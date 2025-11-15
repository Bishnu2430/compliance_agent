# utils/observability.py
from loguru import logger
from prometheus_client import Counter

logger.add("audit.log", rotation="10 MB", retention="7 days", compression="zip")

class Metrics:
    def __init__(self):
        self.docs_processed = Counter("docs_processed_total", "Number of documents processed")
    def inc_processed(self, n):
        self.docs_processed.inc(n)

metrics = Metrics()
