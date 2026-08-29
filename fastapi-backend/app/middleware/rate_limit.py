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


def _is_localhost(client_ip: str) -> bool:
    """Return True for loopback addresses used in local dev only."""
    return client_ip in ("127.0.0.1", "::1", "localhost", "0.0.0.0")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter per client IP, Redis-backed when available."""

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 60,
        window_seconds: int = 60,
        auth_requests_per_minute: int = 10,
    ) -> None:
        super().__init__(app)
        self.rate_limit = requests_per_minute
        self.auth_rate_limit = auth_requests_per_minute
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

    async def _is_allowed_memory(self, client_ip: str, limit: int | None = None) -> bool:
        """In-memory sliding window fallback."""
        limit = self.rate_limit if limit is None else limit
        now = time.time()
        cutoff = now - self._window
        self._hits[client_ip] = [t for t in self._hits[client_ip] if t > cutoff]
        if len(self._hits[client_ip]) >= limit:
            return False
        self._hits[client_ip].append(now)
        return True

    async def _is_allowed_redis(self, client_ip: str, limit: int | None = None) -> bool:
        """Redis sorted-set sliding window."""
        limit = self.rate_limit if limit is None else limit
        redis = get_redis()
        if isinstance(redis, NullRedis):
            return await self._is_allowed_memory(client_ip, limit=limit)

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
            return count < limit
        except Exception as exc:
            logger.warning("Redis rate limit check failed for %s: %s", client_ip, exc)
            return await self._is_allowed_memory(client_ip, limit=limit)

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        # Skip rate limiting for health checks and CORS preflight requests
        if request.method == "OPTIONS" or request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        client_ip = self._client_ip(request)

        # Skip rate limiting for local development requests
        if _is_localhost(client_ip):
            return await call_next(request)

        # Admin and protected write endpoints are higher-sensitivity auth actions
        # and get a much tighter per-minute budget.
        is_auth_action = (
            request.method != "GET"
            and (
                request.url.path.startswith("/api/v1/admin/")
                or request.url.path.startswith("/api/v1/protected/")
            )
        )
        limit = self.auth_rate_limit if is_auth_action else self.rate_limit
        allowed = await self._is_allowed_redis(client_ip, limit=limit)

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
