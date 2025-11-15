# agents/remediation_agent.py
import os
import json
import time
import google.generativeai as genai
from utils.observability import logger

class RemediationAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.logger = logger

    def _build_prompt(self, violation):
        vjson = json.dumps(violation, indent=2)
        prompt = (
            "You are a senior security engineer. For the following violation JSON, "
            "produce a JSON object with fields: proposed_change (include file path "
            "and new content), remediation_steps (list), difficulty, estimated_time_mins, notes.\n\n"
            f"{vjson}\n\n"
            "RETURN JSON."
        )
        return prompt

    def generate(self, violations):
        remediations = []

        for v in violations:
            try:
                prompt = self._build_prompt(v)
                response = self.model.generate_content(prompt)
                output_text = response.text

                try:
                    parsed = json.loads(output_text)
                except:
                    parsed = {"raw": output_text}

                remediations.append({
                    "violation": v,
                    "suggestion": parsed
                })
            except Exception as e:
                self.logger.error(f"Remediation generation failed: {e}")

            time.sleep(0.3)

        return remediations
