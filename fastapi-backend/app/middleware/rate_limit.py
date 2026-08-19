"""Distributed sliding-window rate limiting middleware for LUMI.

Prefers Redis (Upstash) so the limit is shared across workers and containers.
Falls back to an in-memory sliding window when Redis is unavailable.
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.services.redis_client import NullRedis, get_redis

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter per client IP, Redis-backed when available."""

    def __init__(self, app: Any, requests_per_minute: int = 60, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.rate_limit = requests_per_minute
        self._window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_ip(self, request: Request) -> str:
        """Extract the real client IP, respecting reverse proxy headers."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # X-Forwarded-For can be a comma-separated list; the left-most is the original client.
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "unknown"

    async def _is_allowed_memory(self, client_ip: str) -> bool:
        """In-memory sliding window fallback."""
        now = time.time()
        cutoff = now - self._window
        self._hits[client_ip] = [t for t in self._hits[client_ip] if t > cutoff]
        if len(self._hits[client_ip]) >= self.rate_limit:
            return False
        self._hits[client_ip].append(now)
        return True

    async def _is_allowed_redis(self, client_ip: str) -> bool:
        """Redis sorted-set sliding window."""
        redis = get_redis()
        if isinstance(redis, NullRedis):
            return await self._is_allowed_memory(client_ip)

        now = time.time()
        key = f"lumi:rate_limit:{client_ip}"
        try:
            pipe = redis.pipeline()
            # Remove timestamps outside the current window
            pipe.zremrangebyscore(key, 0, now - self._window)
            # Count remaining entries in the window
            pipe.zcard(key)
            # Add the current timestamp and set key expiry
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self._window + 1)
            _, count, _, _ = await pipe.execute()
            return count < self.rate_limit
        except Exception as exc:
            logger.warning("Redis rate limit check failed for %s: %s", client_ip, exc)
            return await self._is_allowed_memory(client_ip)

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        # Skip rate limiting for health checks and CORS preflight requests
        if request.method == "OPTIONS" or request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        client_ip = self._client_ip(request)
        allowed = await self._is_allowed_redis(client_ip)

        if not allowed:
            retry_after = self._window
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Try again in a minute.",
                    "retry_after_seconds": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
