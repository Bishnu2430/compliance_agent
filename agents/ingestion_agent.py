# agents/ingestion_agent.py
from tools.read_document import read_document, list_documents
from utils.observability import logger

class IngestionAgent:
    def __init__(self):
        self.logger = logger

    def read_folder(self, folder_path):
        files = list_documents(folder_path)
        docs = []
        for f in files:
            try:
                text = read_document(f)
                docs.append({"path": f, "text": text})
            except Exception as e:
                self.logger.error(f"Failed to read {f}: {e}")
        return docs
