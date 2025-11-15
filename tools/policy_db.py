# tools/policy_db.py
import json
import re

class PolicyDB:
    def __init__(self, path="configs/policies.json"):
        with open(path, "r", encoding="utf-8") as f:
            self.db = json.load(f)

    def find_relevant(self, text, max_results=5):
        results = []
        for p in self.db.get("policies", []):
            for kw in p.get("keywords", []):
                # simple word boundary search
                if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE):
                    results.append(p)
                    break
            if len(results) >= max_results:
                break
        return results
