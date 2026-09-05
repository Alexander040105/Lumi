# Vercel FastAPI Backend 404 Fix

A short reference on how to deploy a single FastAPI app on Vercel so that `https://<deployment>/docs`, `/api/v1/...`, and `/` all work.

## The Problem

Vercel builds the `api/index.py` Python serverless function, but by default it only answers requests that match its file path (`/api/index`). Calling `/docs` or `/api/v1/health` from the root domain results in a `404: NOT_FOUND` from Vercel's edge, and no function logs appear because the function is never invoked.

## The Fix

### 1. Route every request to the FastAPI function

In the root `vercel.json`:

```json
{
  "version": 2,
  "framework": null,
  "buildCommand": null,
  "installCommand": "pip install -r api/requirements.txt",
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/index" }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 10,
      "memory": 1024,
      "excludeFiles": "{.venv/**,node_modules/**,__pycache__/**,.pytest_cache/**,fastapi-backend/app/services/local_data/**,fastapi-backend/scripts/**}",
      "includeFiles": "{fastapi-backend/**,api/**}"
    }
  }
}
```

Important: the rewrite destination is `/api/index` **without `$1`**. Vercel serverless functions are matched by exact file path, so `destination: "/api/index/$1"` points to a non-existent function and still 404s at the edge.

### 2. Make sure Vercel finds the Python entrypoint

Create a `pyproject.toml` at the repository root:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "lumi-backend"
version = "0.1.0"
dependencies = [
    # list the runtime dependencies the Vercel function needs
    "fastapi",
    "pydantic-settings",
    "python-dotenv",
    "supabase",
    "python-jose[cryptography]",
    "httpx",
    "redis",
    "google-genai",
    "groq",
    "pandas",
    "numpy",
]

[tool.vercel]
entrypoint = "api.index:app"
```

`api/index.py` should expose the FastAPI app as `app` and add the backend package to `sys.path`:

```python
import os
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "fastapi-backend"
sys.path.insert(0, str(_BACKEND))

from main import app  # noqa: F401
```

### 3. Normalize the ASGI path

Vercel may pass the original request path (`/docs`) or the destination path (`/api/index`). A small ASGI wrapper strips `/api/index` and `/api/index.py` so FastAPI routes against the public URL:

```python
class _PathFix:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path = scope.get("path", "/")
            raw_path = scope.get("raw_path", b"/")

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
                    break

            scope["root_path"] = ""

        await self.app(scope, receive, send)


app = _PathFix(app)
```

### 4. Verify after deploy

```bash
curl https://<deployment>/
curl https://<deployment>/docs
curl https://<deployment>/api/v1/health
```

If any 404, check the Vercel **Functions** logs for the request. If the log is missing, the rewrite did not match. If the log shows a 404, the ASGI path is not being normalized correctly.

## Common Mistakes

- `vercel.json` `excludeFiles` string > 256 characters. Keep the glob short.
- `destination: "/api/index/$1"` in a rewrite. Do not use `$1` for serverless function routing.
- `pyproject.toml` missing the `[tool.vercel] entrypoint` or not at the repo root.
- `app` variable in `api/index.py` is not top-level or is not a valid ASGI callable.
