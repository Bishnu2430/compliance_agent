# agents/orchestrator.py
from agents.ingestion_agent import IngestionAgent
from agents.repo_scanner_agent import RepoScannerAgent
from agents.policy_mapping_agent import PolicyMappingAgent
from agents.violation_agent import ViolationAgent
from agents.remediation_agent import RemediationAgent
from agents.pr_agent import PRAgent
from utils.memory import MemoryBank
from utils.observability import logger, metrics

class Orchestrator:
    def __init__(self):
        self.ingest = IngestionAgent()
        self.repo = RepoScannerAgent()
        self.mapper = PolicyMappingAgent()
        self.detector = ViolationAgent()
        self.remed = RemediationAgent()
        self.pr_agent = PRAgent()
        self.memory = MemoryBank()
        self.logger = logger
        self.metrics = metrics

    def run_audit(self, documents_path=None, repo_url=None, create_pr=False, gh_owner=None, gh_repo=None):
        self.logger.info("Starting compliance audit pipeline")
        docs = []
        if documents_path:
            docs = self.ingest.read_folder(documents_path)
            self.logger.info(f"Read {len(docs)} docs from {documents_path}")
        repo_files = []
        if repo_url:
            repo_files = self.repo.scan_repo(repo_url)
            self.logger.info(f"Scanned {len(repo_files)} repo files from {repo_url}")

        all_items = docs + repo_files
        self.logger.info(f"Total items to map: {len(all_items)}")
        mapping = self.mapper.map_to_policies(all_items)
        self.logger.info("Completed policy mapping")
        violations = self.detector.detect(mapping)
        self.logger.info(f"Detected {len(violations)} potential violations")
        remediations = self.remed.generate(violations)
        self.logger.info("Generated remediation suggestions")

        report = {"violations": violations, "remediations": remediations}
        self.memory.save_audit(report)

        if create_pr and repo_url and gh_owner and gh_repo:
            prs = self.pr_agent.create_prs(remediations, gh_owner, gh_repo)
            self.logger.info(f"Created {len(prs)} PRs")
            report["prs"] = prs

        self.metrics.inc_processed(len(all_items))
        self.logger.info("Audit complete")
        return report
