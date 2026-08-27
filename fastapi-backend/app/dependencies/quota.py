import logging
import time
from typing import Any

from fastapi import Depends, HTTPException, Request, status

from app.config.settings import get_settings
from app.dependencies.auth import _get_effective_plan, _get_user_role, get_verified_user_optional
from app.services.redis_client import NullRedis, get_redis, is_redis_available
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

# In-memory sliding-window fallback when Redis is unavailable.
# Stores the timestamp of the last request for each anonymous client.
_in_memory_last: dict[str, float] = {}
_in_memory_counts: dict[str, int] = {}


def get_client_id(request: Request) -> str:
    """Extract a stable client identifier from the request."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return "unknown"


async def _reset_redis_key(key: str, window: int) -> bool:
    """Reset a Redis TTL counter key, returning whether it existed."""
    redis = get_redis()
    if isinstance(redis, NullRedis):
        return False
    try:
        pipe = redis.pipeline()
        pipe.get(key)
        pipe.delete(key)
        pipe.setex(key, window, "0")
        results = await pipe.execute()
        return results[0] is not None
    except Exception as exc:
        logger.warning("Redis quota reset failed: %s", exc)
        return False


async def check_and_increment_quota(client_id: str) -> tuple[bool, int]:
    """Public helper for routes that need conditional quota checks."""
    settings = get_settings()
    quota = settings.anonymous_ecosim_quota
    window = settings.anonymous_ecosim_window_seconds

    redis = get_redis()
    if not isinstance(redis, NullRedis):
        try:
            return await _check_and_incr_redis(client_id, window, quota)
        except Exception:
            logger.warning("Redis quota check failed, falling back to in-memory.")

    return _check_and_incr_memory(client_id, window, quota)


async def _check_and_incr_redis(client_id: str, window: int, quota: int) -> tuple[bool, int]:
    """Return (allowed, remaining_after_this_request) using Redis TTL keys."""
    redis = get_redis()
    if isinstance(redis, NullRedis):
        raise RuntimeError("Redis not available")

    key = f"ecosim:anon:{client_id}"
    try:
        raw = await redis.get(key)
        if raw is None:
            await _reset_redis_key(key, window)
            count = 0
        else:
            try:
                count = int(raw)
            except (ValueError, TypeError):
                await _reset_redis_key(key, window)
                count = 0

        if count >= quota:
            return False, 0

        new_count = count + 1
        await redis.setex(key, window, str(new_count))
        return True, max(quota - new_count, 0)
    except Exception as exc:
        logger.warning("Redis quota check failed: %s", exc)
        raise


def _check_and_incr_memory(client_id: str, window: int, quota: int) -> tuple[bool, int]:
    """In-memory fallback for the anonymous quota."""
    now = time.time()
    last = _in_memory_last.get(client_id, 0.0)
    if now - last > window:
        _in_memory_counts[client_id] = 0
    _in_memory_last[client_id] = now

    count = _in_memory_counts.get(client_id, 0)
    if count >= quota:
        return False, 0

    new_count = count + 1
    _in_memory_counts[client_id] = new_count
    return True, max(quota - new_count, 0)


async def check_anonymous_quota(client_id: str) -> tuple[bool, int]:
    """Check whether an anonymous client is within its quota.

    Returns (allowed, remaining_after_this_request). On quota exhaustion,
    allowed is False and remaining is 0.
    """
    return await check_and_increment_quota(client_id)


async def check_authenticated_usage(user: dict, action: str = "simulation") -> dict[str, Any]:
    """Verify a logged-in user is within their monthly usage limits.

    Raises HTTPException 429 if the limit is exceeded. Returns remaining count.
    """
    settings = get_settings()
    if not settings.enforce_usage_limits:
        return {"allowed": True, "remaining": None}

    user_id = user.get("sub")
    role = _get_user_role(user_id)

    if role in ("admin", "dev"):
        return {"allowed": True, "remaining": None}

    plan = _get_effective_plan(user_id, role=role)
    if plan == "premium":
        limit = settings.premium_simulation_limit if action == "simulation" else settings.premium_chat_message_limit
    else:
        limit = settings.free_simulation_limit if action == "simulation" else settings.free_chat_message_limit

    client = get_supabase_client()
    try:
        resp = client.table("user_usage_limits").select("simulations_this_month, chat_messages_this_month").eq("user_id", user_id).execute()
        usage = resp.data[0] if resp.data else {}
    except Exception as exc:
        logger.warning("Failed to fetch usage limits for user_id=%s: %s", user_id, exc)
        usage = {}

    key = "simulations_this_month" if action == "simulation" else "chat_messages_this_month"
    current = int(usage.get(key, 0) or 0)
    if current >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly {action} limit reached",
        )

    return {"allowed": True, "remaining": max(limit - current - 1, 0)}


async def get_optional_user_or_quota(
    request: Request,
    user: dict | None = Depends(get_verified_user_optional),
) -> dict[str, Any]:
    """Allow authenticated requests (with usage limits); apply an anonymous quota otherwise.

    Returns a dict with the verified user (if any) and the number of
    remaining anonymous requests for this client.
    """
    if user:
        usage = await check_authenticated_usage(user, action="simulation")
        return {
            "user": user,
            "remaining_anonymous_requests": None,
            "remaining_usage": usage.get("remaining"),
        }

    client_id = get_client_id(request)
    allowed, remaining = await check_anonymous_quota(client_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to continue using EcoSim.",
        )

    return {
        "user": None,
        "remaining_anonymous_requests": remaining,
    }
