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


class _PathFix:
    """Normalize ASGI scope paths for Vercel's serverless mount point.

    Vercel invokes the `api/index.py` function with the full public URL path.
    For a rewrite like `/(.*)` -> `/api/index/$1`, the app may see
    `/api/index/docs` instead of `/docs`. This wrapper strips the function
    prefix so FastAPI's routers receive the original request paths.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path = scope.get("path", "/")
            raw_path = scope.get("raw_path", b"")
            root_path = scope.get("root_path", "")

            for prefix in ("/api/index.py", "/api/index"):
                if path.startswith(prefix):
                    rest = path[len(prefix):]
                    if not rest.startswith("/"):
                        rest = "/" + rest
                    scope["path"] = rest or "/"

                    raw_prefix = prefix.encode()
                    raw_rest = raw_path[len(raw_prefix):]
                    if not raw_rest.startswith(b"/"):
                        raw_rest = b"/" + raw_rest
                    scope["raw_path"] = raw_rest or b"/"

                    if root_path.startswith(prefix):
                        scope["root_path"] = root_path[len(prefix):] or ""
                    break

        await self.app(scope, receive, send)


app = _PathFix(app)
