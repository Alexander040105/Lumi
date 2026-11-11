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
from app.utils.network import _direct_peer_ip, _is_localhost, get_client_id

logger = logging.getLogger(__name__)


# Genuinely sensitive writes that keep the tight per-minute budget.
# Everything else under /protected/ (PUT /profile, POST /sync-avatar) is a
# routine user action and uses the normal limit.
_SENSITIVE_WRITE_PATHS = {
    ("DELETE", "/api/v1/protected/me"),
    ("POST", "/api/v1/protected/session"),
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter per client IP, Redis-backed when available.

    Three tiers: sensitive writes (admin mutations + account-level actions)
    get ``auth_requests_per_minute``; all other traffic including routine
    protected/profile writes gets ``requests_per_minute``; health checks and
    OPTIONS are exempt.
    """

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 60,
        window_seconds: int = 60,
        auth_requests_per_minute: int = 15,
    ) -> None:
        super().__init__(app)
        self.rate_limit = requests_per_minute
        self.auth_rate_limit = auth_requests_per_minute
        self._window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

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
        """Redis sorted-set sliding window with merged in-memory counter.

        The in-memory counter is always updated for allowed requests so the limit
        is enforced even when Redis is flapping between healthy and failing.
        """
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
            if count >= limit:
                return False
            # Merge with the local counter so flapping Redis cannot split counts.
            return await self._is_allowed_memory(client_ip, limit=limit)
        except Exception as exc:
            logger.warning("Redis rate limit check failed for %s: %s", client_ip, exc)
            return await self._is_allowed_memory(client_ip, limit=limit)

    def _client_ip(self, request: Request) -> str:
        """Return the client IP used for rate-limit buckets."""
        return get_client_id(request)

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        # Skip rate limiting for health checks and CORS preflight requests
        if request.method == "OPTIONS" or request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        # Localhost exemption must use the direct peer, never a spoofed header.
        if _is_localhost(_direct_peer_ip(request)):
            return await call_next(request)

        client_ip = self._client_ip(request)

        # Tight budget only for sensitive writes: all admin mutations plus
        # the account-level protected actions listed in _SENSITIVE_WRITE_PATHS.
        is_sensitive = request.method != "GET" and (
            request.url.path.startswith("/api/v1/admin/")
            or (request.method, request.url.path) in _SENSITIVE_WRITE_PATHS
        )
        limit = self.auth_rate_limit if is_sensitive else self.rate_limit
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
