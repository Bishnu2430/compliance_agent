# utils/helpers.py
import os
import subprocess

def extract_text_from_file(path):
    lower = path.lower()
    if lower.endswith(".pdf"):
        # simple pdf text extraction via PyPDF2
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        return "\n".join([p.extract_text() or "" for p in reader.pages])
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path
