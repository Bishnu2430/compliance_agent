# tools/read_document.py
import os
from PyPDF2 import PdfReader

def list_documents(folder_path):
    file_list = []
    for root, _, files in __import__('os').walk(folder_path):
        for file in files:
            if file.lower().endswith(('.pdf', '.txt', '.md', '.yaml', '.yml', '.json')):
                file_list.append(os.path.join(root, file))
    return file_list

def read_pdf(path):
    reader = PdfReader(path)
    text = []
    for p in reader.pages:
        text.append(p.extract_text() or "")
    return "\n".join(text)

def read_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def read_document(path):
    lower = path.lower()
    if lower.endswith(".pdf"):
        return read_pdf(path)
    else:
        return read_text(path)
