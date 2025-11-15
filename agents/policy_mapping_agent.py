# agents/policy_mapping_agent.py
from tools.policy_db import PolicyDB
from utils.observability import logger

class PolicyMappingAgent:
    def __init__(self, policy_path="configs/policies.json"):
        self.db = PolicyDB(policy_path)
        self.logger = logger

    def map_to_policies(self, items):
        mapped = []
        for it in items:
            text = it.get("text", "")
            candidates = self.db.find_relevant(text)
            mapped.append({"item": it, "candidates": candidates})
            self.logger.debug(f"Mapped {it.get('path')} to {len(candidates)} policies")
        return mapped
