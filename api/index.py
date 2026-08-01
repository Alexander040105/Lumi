import os
import sys
from pathlib import Path

# Add the existing fastapi-backend package to the import path.
_BACKEND = Path(__file__).resolve().parents[1] / "fastapi-backend"
sys.path.insert(0, str(_BACKEND))

# Vercel injects env vars; the local .env file is not present.
# Disable RAG by default to avoid heavy startup and missing packages.
os.environ.setdefault("ENABLE_RAG", "false")

# Make the FastAPI application available to Vercel's Python runtime.
from main import app  # noqa: F401
