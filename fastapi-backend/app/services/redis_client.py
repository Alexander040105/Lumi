import json
import logging
import os
from typing import Any

import redis as redis_sync
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 3600  # 1 hour


def get_redis() -> Redis:
    redis_url = os.getenv("UPSTASH_REDIS_URL")
    return Redis.from_url(redis_url, decode_responses=True)


def get_redis_sync() -> redis_sync.Redis:
    redis_url = os.getenv("UPSTASH_REDIS_URL")
    return redis_sync.Redis.from_url(redis_url, decode_responses=True)


# ---------------------------------------------------------------------------
# Suitability cache helpers — async variants (for async routes)
# ---------------------------------------------------------------------------

def _cache_key(renewable_type: str, level: str) -> str:
    return f"lumi:suitability:{renewable_type}:{level}"


async def get_suitability_cache(renewable_type: str, level: str) -> list[dict[str, Any]] | None:
    """Fetch cached municipality/province suitability data (async)."""
    try:
        redis = get_redis()
        raw = await redis.get(_cache_key(renewable_type, level))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis suitability cache read failed: %s", exc)
    return None


async def set_suitability_cache(
    renewable_type: str,
    level: str,
    data: list[dict[str, Any]],
    ttl: int = _DEFAULT_TTL,
) -> None:
    """Store suitability map data in Redis with TTL (async)."""
    try:
        redis = get_redis()
        await redis.setex(
            _cache_key(renewable_type, level),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis suitability cache write failed: %s", exc)


async def invalidate_suitability_cache() -> None:
    """Delete all suitability-related cache keys (async)."""
    try:
        redis = get_redis()
        keys = await redis.keys("lumi:suitability:*")
        if keys:
            await redis.delete(*keys)
            logger.info("Invalidated %s suitability cache keys", len(keys))
    except Exception as exc:
        logger.warning("Redis suitability cache invalidation failed: %s", exc)


# ---------------------------------------------------------------------------
# Suitability cache helpers — sync variants (for sync services / scripts)
# ---------------------------------------------------------------------------

def get_suitability_cache_sync(renewable_type: str, level: str) -> list[dict[str, Any]] | None:
    """Fetch cached municipality/province suitability data (sync)."""
    try:
        redis = get_redis_sync()
        raw = redis.get(_cache_key(renewable_type, level))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis sync suitability cache read failed: %s", exc)
    return None


def set_suitability_cache_sync(
    renewable_type: str,
    level: str,
    data: list[dict[str, Any]],
    ttl: int = _DEFAULT_TTL,
) -> None:
    """Store suitability map data in Redis with TTL (sync)."""
    try:
        redis = get_redis_sync()
        redis.setex(
            _cache_key(renewable_type, level),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis sync suitability cache write failed: %s", exc)


def invalidate_suitability_cache_sync() -> None:
    """Delete all suitability-related cache keys (sync)."""
    try:
        redis = get_redis_sync()
        keys = redis.keys("lumi:suitability:*")
        if keys:
            redis.delete(*keys)
            logger.info("Invalidated %s sync suitability cache keys", len(keys))
    except Exception as exc:
        logger.warning("Redis sync suitability cache invalidation failed: %s", exc)
