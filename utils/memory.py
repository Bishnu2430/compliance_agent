# utils/memory.py
import json
from datetime import datetime
from utils.helpers import ensure_dir
import os

class MemoryBank:
    def __init__(self, path="memory/memory.json"):
        self.path = path
        ensure_dir(os.path.dirname(self.path))

    def save_audit(self, report):
        entry = {"timestamp": datetime.utcnow().isoformat() + "Z", "report": report}
        try:
            if os.path.exists(self.path):
                with open(self.path, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    data.append(entry)
                    f.seek(0)
                    json.dump(data, f, indent=2)
            else:
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump([entry], f, indent=2)
        except Exception:
            # fallback: overwrite
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([entry], f, indent=2)
