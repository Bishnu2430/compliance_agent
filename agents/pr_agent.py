# agents/pr_agent.py
from tools.github_tool import GitHubTool
from utils.observability import logger

class PRAgent:
    def __init__(self):
        self.gh = GitHubTool()
        self.logger = logger

    def create_prs(self, remediations, owner, repo):
        prs = []
        for r in remediations:
            v = r.get("violation", {})
            suggestion = r.get("suggestion", {})
            # We expect suggestion to contain proposed_change with file path & content
            proposed = suggestion.get("proposed_change") or suggestion.get("proposed_change_raw") or None
            if not proposed:
                # Maybe the model provided raw patch in suggestion['raw']
                if isinstance(suggestion, dict) and "raw" in suggestion:
                    # skip for safety
                    continue
                else:
                    continue
            # proposed should be dict: {"path": "path/in/repo", "content": "new file content"}
            path = proposed.get("path")
            content = proposed.get("content")
            if not path or content is None:
                self.logger.warning("Suggestion missing path/content; skipping PR creation")
                continue
            branch = self.gh.create_branch_with_change(owner, repo, path, content)
            title = f"Auto-fix: {v.get('policy_id', 'compliance')}"
            body = suggestion.get("notes", "") or str(suggestion)
            pr_obj = self.gh.create_pull(owner, repo, branch, "main", title, body) if False else self.gh.create_pull(owner, repo, branch, "main", title, body)
            # Note: create_pull signature: owner, repo, head_branch, base_branch, title, body
            prs.append(pr_obj)
            self.logger.info(f"Created PR for {path}: {pr_obj.get('html_url')}")
        return prs
