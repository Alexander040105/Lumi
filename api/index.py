import os
import sys
from pathlib import Path

# Add the existing fastapi-backend package to the import path.
_BACKEND = Path(__file__).resolve().parents[1] / "fastapi-backend"
sys.path.insert(0, str(_BACKEND))

# Vercel injects env vars; the local .env file is not present.
# Use the serverless pgvector RAG backend by default.
os.environ.setdefault("RAG_BACKEND", "pgvector")
os.environ.setdefault("ENABLE_RAG", "true")
os.environ.setdefault("EMBEDDING_PROVIDER", "huggingface-inference")
os.environ.setdefault("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Import the FastAPI application from the backend package.
from main import app  # noqa: F401

# Optionally route heavy / RAG / long-running requests to a companion ML worker.
ml_worker_url = os.environ.get("ML_WORKER_URL")
if ml_worker_url:
    from app.services.ml_worker_proxy import MLWorkerProxyMiddleware

    app.add_middleware(MLWorkerProxyMiddleware, worker_url=ml_worker_url)
