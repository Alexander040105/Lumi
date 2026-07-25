"""Simple in-memory rate limiting middleware for LUMI.

Uses a sliding window counter per client IP.
For production with multiple workers, use Redis-backed rate limiting instead.
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter per client IP."""

    def __init__(self, app: Any, requests_per_minute: int = 60) -> None:
        super().__init__(app)
        self.rate_limit = requests_per_minute
        self._window = 60  # seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Prune old entries
        self._hits[client_ip] = [
            t for t in self._hits[client_ip] if now - t < self._window
        ]

        if len(self._hits[client_ip]) >= self.rate_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Try again in a minute.",
                    "retry_after_seconds": self._window,
                },
                headers={"Retry-After": str(self._window)},
            )

        self._hits[client_ip].append(now)
        return await call_next(request)
