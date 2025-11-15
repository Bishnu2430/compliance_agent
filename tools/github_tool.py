# tools/github_tool.py
import os
import requests
import base64
import json
from utils.observability import logger

GITHUB_API = "https://api.github.com"

class GitHubTool:
    def __init__(self, token=None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN not set")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }
        self.logger = logger

    def _req(self, method, path, **kwargs):
        url = f"{GITHUB_API}{path}"
        r = requests.request(method, url, headers=self.headers, **kwargs)
        if not r.ok:
            self.logger.error(f"GitHub API error {r.status_code}: {r.text}")
            r.raise_for_status()
        return r.json()

    def get_default_branch(self, owner, repo):
        data = self._req("GET", f"/repos/{owner}/{repo}")
        return data.get("default_branch", "main")

    def get_ref(self, owner, repo, ref):
        return self._req("GET", f"/repos/{owner}/{repo}/git/ref/heads/{ref}")

    def create_ref(self, owner, repo, branch_name, sha):
        data = {"ref": f"refs/heads/{branch_name}", "sha": sha}
        return self._req("POST", f"/repos/{owner}/{repo}/git/refs", json=data)

    def get_commit(self, owner, repo, sha):
        return self._req("GET", f"/repos/{owner}/{repo}/git/commits/{sha}")

    def get_tree(self, owner, repo, sha):
        return self._req("GET", f"/repos/{owner}/{repo}/git/trees/{sha}")

    def create_blob(self, owner, repo, content):
        # content must be base64-encoded or raw string with encoding param
        data = {"content": content, "encoding": "utf-8"}
        return self._req("POST", f"/repos/{owner}/{repo}/git/blobs", json=data)

    def create_tree(self, owner, repo, tree, base_tree):
        data = {"tree": tree, "base_tree": base_tree}
        return self._req("POST", f"/repos/{owner}/{repo}/git/trees", json=data)

    def create_commit(self, owner, repo, message, tree_sha, parents):
        data = {"message": message, "tree": tree_sha, "parents": parents}
        return self._req("POST", f"/repos/{owner}/{repo}/git/commits", json=data)

    def update_ref(self, owner, repo, branch, sha):
        data = {"sha": sha, "force": False}
        return self._req("PATCH", f"/repos/{owner}/{repo}/git/refs/heads/{branch}", json=data)

    def create_pull(self, owner, repo, head_branch, base_branch, title, body):
        data = {"title": title, "head": head_branch, "base": base_branch, "body": body}
        return self._req("POST", f"/repos/{owner}/{repo}/pulls", json=data)

    # high-level function to create a commit that updates a single file path with new content on a new branch
    def create_branch_with_change(self, owner, repo, file_path, new_content, branch_prefix="auto-fix"):
        self.logger.info(f"Preparing branch & commit to change {file_path} in {owner}/{repo}")
        default_branch = self.get_default_branch(owner, repo)
        default_ref = self.get_ref(owner, repo, default_branch)
        base_sha = default_ref["object"]["sha"]
        # Get base commit and tree
        commit = self.get_commit(owner, repo, base_sha)
        base_tree_sha = commit["tree"]["sha"]
        # Create blob for new content
        blob = self.create_blob(owner, repo, new_content)
        blob_sha = blob["sha"]
        # Create a new tree with updated file
        tree = [{"path": file_path, "mode": "100644", "type": "blob", "sha": blob_sha}]
        new_tree = self.create_tree(owner, repo, tree, base_tree_sha)
        new_tree_sha = new_tree["sha"]
        # Create commit
        commit_message = f"Auto-fix compliance: {file_path}"
        new_commit = self.create_commit(owner, repo, commit_message, new_tree_sha, [base_sha])
        new_commit_sha = new_commit["sha"]
        # Create new branch name
        safe_path = file_path.replace("/", "_").replace(".", "_")
        branch_name = f"{branch_prefix}/{safe_path}"
        # create branch ref
        self.create_ref(owner, repo, branch_name, new_commit_sha)
        self.logger.info(f"Created branch {branch_name} with commit {new_commit_sha}")
        return branch_name
