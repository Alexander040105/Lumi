import json
import logging
import os
from typing import Any

import redis as redis_sync
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 3600  # 1 hour
_CLIMATE_TTL = 86400  # 24 hours
_CENTROID_TTL = 86400  # 24 hours
_ECOSIM_TTL = 1800  # 30 minutes

_redis_async: Redis | None = None
_redis_sync: redis_sync.Redis | None = None


def get_redis() -> Redis:
    global _redis_async
    if _redis_async is None:
        redis_url = os.getenv("UPSTASH_REDIS_URL")
        _redis_async = Redis.from_url(redis_url, decode_responses=True)
    return _redis_async


def get_redis_sync() -> redis_sync.Redis:
    global _redis_sync
    if _redis_sync is None:
        redis_url = os.getenv("UPSTASH_REDIS_URL")
        _redis_sync = redis_sync.Redis.from_url(redis_url, decode_responses=True)
    return _redis_sync


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


# ---------------------------------------------------------------------------
# Climate cache helpers — sync variants
# ---------------------------------------------------------------------------

def _climate_cache_key(level: str, geo_id: int | str, year: int | str) -> str:
    return f"lumi:climate:{level}:{geo_id}:{year}"


def get_climate_cache_sync(level: str, geo_id: int | str, year: int | str) -> list[dict[str, Any]] | None:
    """Fetch cached climate data for a geo unit and year (sync)."""
    try:
        redis = get_redis_sync()
        raw = redis.get(_climate_cache_key(level, geo_id, year))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis sync climate cache read failed: %s", exc)
    return None


def set_climate_cache_sync(
    level: str,
    geo_id: int | str,
    year: int | str,
    data: list[dict[str, Any]],
    ttl: int = _CLIMATE_TTL,
) -> None:
    """Store climate data in Redis with TTL (sync)."""
    try:
        redis = get_redis_sync()
        redis.setex(
            _climate_cache_key(level, geo_id, year),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis sync climate cache write failed: %s", exc)


def invalidate_climate_cache_sync(level: str | None = None, geo_id: int | str | None = None) -> None:
    """Delete climate cache keys. If level/geo_id given, scoped; otherwise all."""
    try:
        redis = get_redis_sync()
        if level and geo_id is not None:
            keys = redis.keys(f"lumi:climate:{level}:{geo_id}:*")
        else:
            keys = redis.keys("lumi:climate:*")
        if keys:
            redis.delete(*keys)
            logger.info("Invalidated %s climate cache keys", len(keys))
    except Exception as exc:
        logger.warning("Redis sync climate cache invalidation failed: %s", exc)


# ---------------------------------------------------------------------------
# Centroid cache helpers — sync variants
# ---------------------------------------------------------------------------

def _centroid_cache_key(level: str) -> str:
    return f"lumi:centroids:{level}"


def get_centroid_cache_sync(level: str) -> list[dict[str, Any]] | None:
    """Fetch cached centroid data for a geographic level (sync)."""
    try:
        redis = get_redis_sync()
        raw = redis.get(_centroid_cache_key(level))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis sync centroid cache read failed: %s", exc)
    return None


def set_centroid_cache_sync(
    level: str,
    data: list[dict[str, Any]],
    ttl: int = _CENTROID_TTL,
) -> None:
    """Store centroid data in Redis with TTL (sync)."""
    try:
        redis = get_redis_sync()
        redis.setex(
            _centroid_cache_key(level),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis sync centroid cache write failed: %s", exc)


# ---------------------------------------------------------------------------
# EcoSim cache helpers — sync variants
# ---------------------------------------------------------------------------

def _ecosim_cache_key(level: str, geo_id: int | str, params_hash: str) -> str:
    return f"lumi:ecosim:{level}:{geo_id}:{params_hash}"


def get_ecosim_cache_sync(level: str, geo_id: int | str, params_hash: str) -> dict[str, Any] | None:
    """Fetch cached EcoSim simulation result (sync)."""
    try:
        redis = get_redis_sync()
        raw = redis.get(_ecosim_cache_key(level, geo_id, params_hash))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis sync ecosim cache read failed: %s", exc)
    return None


def set_ecosim_cache_sync(
    level: str,
    geo_id: int | str,
    params_hash: str,
    data: dict[str, Any],
    ttl: int = _ECOSIM_TTL,
) -> None:
    """Store EcoSim simulation result in Redis with TTL (sync)."""
    try:
        redis = get_redis_sync()
        redis.setex(
            _ecosim_cache_key(level, geo_id, params_hash),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis sync ecosim cache write failed: %s", exc)


# ---------------------------------------------------------------------------
# Async variants for climate, centroid, ecosim
# ---------------------------------------------------------------------------

async def get_climate_cache(level: str, geo_id: int | str, year: int | str) -> list[dict[str, Any]] | None:
    try:
        redis = get_redis()
        raw = await redis.get(_climate_cache_key(level, geo_id, year))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis climate cache read failed: %s", exc)
    return None


async def set_climate_cache(
    level: str, geo_id: int | str, year: int | str, data: list[dict[str, Any]], ttl: int = _CLIMATE_TTL,
) -> None:
    try:
        redis = get_redis()
        await redis.setex(_climate_cache_key(level, geo_id, year), ttl, json.dumps(data, default=str))
    except Exception as exc:
        logger.debug("Redis climate cache write failed: %s", exc)


async def get_centroid_cache(level: str) -> list[dict[str, Any]] | None:
    try:
        redis = get_redis()
        raw = await redis.get(_centroid_cache_key(level))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis centroid cache read failed: %s", exc)
    return None


async def set_centroid_cache(level: str, data: list[dict[str, Any]], ttl: int = _CENTROID_TTL) -> None:
    try:
        redis = get_redis()
        await redis.setex(_centroid_cache_key(level), ttl, json.dumps(data, default=str))
    except Exception as exc:
        logger.debug("Redis centroid cache write failed: %s", exc)


async def invalidate_all_geospatial_cache() -> None:
    """Delete all geospatial-related cache keys (async)."""
    try:
        redis = get_redis()
        patterns = ["lumi:suitability:*", "lumi:climate:*", "lumi:centroids:*", "lumi:ecosim:*"]
        total = 0
        for pattern in patterns:
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
                total += len(keys)
        if total:
            logger.info("Invalidated %s total geospatial cache keys", total)
    except Exception as exc:
        logger.warning("Redis geospatial cache invalidation failed: %s", exc)
