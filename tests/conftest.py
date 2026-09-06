import os

# The module-level FastAPI app requires configuration during test collection.
os.environ.setdefault("RUNBOOK_RELAY_API_KEY", "pytest-collection-key")
