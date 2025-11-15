# agents/repo_scanner_agent.py
import tempfile
import os
from git import Repo
from utils.helpers import extract_text_from_file
from utils.observability import logger

class RepoScannerAgent:
    def __init__(self):
        self.logger = logger

    def scan_repo(self, repo_url):
        tmp = tempfile.mkdtemp(prefix="repo_scan_")
        self.logger.info(f"Cloning {repo_url} into {tmp}")
        Repo.clone_from(repo_url, tmp)
        repo_files = []
        for root, _, files in os.walk(tmp):
            for file in files:
                if file.endswith((".yaml", ".yml", ".tf", ".json", ".py", ".md", ".sh")):
                    path = os.path.join(root, file)
                    try:
                        text = extract_text_from_file(path)
                        repo_files.append({"path": path, "text": text})
                    except Exception as e:
                        self.logger.error(f"Failed to extract {path}: {e}")
        return repo_files
