# agents/violation_agent.py
import os
import json
import time
from tqdm import tqdm
from utils.observability import logger
import google.generativeai as genai

class ViolationAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.logger = logger

    def _build_prompt(self, mapped):
        text = mapped["item"].get("text", "")
        policies = mapped.get("candidates", [])
        policies_str = json.dumps(policies, indent=2)

        prompt = (
            "You are a compliance auditor. Given the DOCUMENT and candidate policy entries, "
            "identify violations. For each violation return JSON objects with fields: "
            "policy_id, violation, severity (LOW/MEDIUM/HIGH), snippet (evidence), "
            "confidence (0-1), path.\n\n"
            f"DOCUMENT:\n{text[:6000]}\n\n"
            f"CANDIDATE_POLICIES:\n{policies_str}\n\n"
            "RETURN A JSON ARRAY."
        )
        return prompt

    def _parse_response(self, text):
        try:
            return json.loads(text)
        except:
            # Attempt to extract JSON
            import re
            match = re.search(r"(\[.*\])", text, re.S)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
        return []

    def detect(self, mapped_items):
        results = []

        for m in tqdm(mapped_items, desc="Detecting violations"):
            prompt = self._build_prompt(m)
            try:
                response = self.model.generate_content(prompt)
                output_text = response.text
                parsed = self._parse_response(output_text)

                for v in parsed:
                    v["path"] = m["item"].get("path")
                    results.append(v)

            except Exception as e:
                self.logger.error(f"Gemini failed on {m['item'].get('path')}: {e}")

            time.sleep(0.3)

        return results
