"""Optional ML-worker proxy for Vercel.

When ML_WORKER_URL is set, requests to heavy / RAG / long-running paths can be
forwarded to a companion worker that still runs the full Docker backend
(e.g. on Render, Fly, or DigitalOcean). When it is unset, the middleware is a
pass-through and the lightweight Vercel endpoints run as usual.
"""
import json
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Path prefixes that are offloaded to the ML worker by default.
DEFAULT_PROXY_PREFIXES = ["/api/v1/chat", "/api/v1/etl"]


def _proxy_prefixes() -> list[str]:
    extra = os.environ.get("ML_WORKER_PROXY_PREFIXES")
    if extra:
        return [p.strip() for p in extra.split(",") if p.strip()]
    return DEFAULT_PROXY_PREFIXES


class MLWorkerProxyMiddleware(BaseHTTPMiddleware):
    """Forward selected API requests to an external ML worker."""

    def __init__(self, app, worker_url: str | None = None) -> None:
        super().__init__(app)
        self.worker_url = (worker_url or os.environ.get("ML_WORKER_URL", "")).rstrip("/")
        self.proxy_prefixes = _proxy_prefixes()

    def _should_proxy(self, path: str) -> bool:
        if not self.worker_url:
            return False
        path = path.rstrip("/")
        for prefix in self.proxy_prefixes:
            if path == prefix or path.startswith(prefix + "/"):
                return True
        return False

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> Any:
        if not self._should_proxy(request.url.path):
            return await call_next(request)

        # Keep CORS preflights local.
        if request.method == "OPTIONS":
            return await call_next(request)

        target = f"{self.worker_url}{request.url.path}"
        if request.url.query:
            target += f"?{request.url.query}"

        body = await request.body()
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in {"host", "content-length", "accept-encoding"}
        }

        try:
            async with httpx.AsyncClient(timeout=55.0) as client:
                worker_resp = await client.request(
                    method=request.method,
                    url=target,
                    headers=headers,
                    content=body,
                    follow_redirects=True,
                )
        except Exception as exc:
            logger.exception("ML worker proxy failed for %s: %s", target, exc)
            return Response(
                content=json.dumps({"detail": f"ML worker unavailable: {exc}"}),
                status_code=503,
                media_type="application/json",
            )

        return Response(
            content=worker_resp.content,
            status_code=worker_resp.status_code,
            headers={
                "content-type": worker_resp.headers.get(
                    "content-type", "application/json"
                )
            },
        )
