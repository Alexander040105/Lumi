"""Thin Redis cache layer with optional gzip + base64 compression.

This module wraps the existing redis_client.py with a small serialization
layer that keeps payloads under Upstash's 10 MB / 256 MB free-tier limits.
"""

from __future__ import annotations

import base64
import gzip
import json
import logging
from typing import Any

from app.services.redis_client import get_redis, get_redis_sync

logger = logging.getLogger(__name__)

DEFAULT_TTL = 3600
_COMPRESS_THRESHOLD = 1024  # bytes; compress JSON payloads larger than this
_GZIP_PREFIX = "gzip:"


def _serialize(value: Any) -> str:
    """Serialize a value for Redis; compress large payloads."""
    payload = json.dumps(value, default=str).encode("utf-8")
    if len(payload) > _COMPRESS_THRESHOLD:
        compressed = gzip.compress(payload, compresslevel=6)
        encoded = base64.b64encode(compressed).decode("ascii")
        return f"{_GZIP_PREFIX}{encoded}"
    return payload.decode("utf-8")


def _deserialize(raw: Any) -> Any | None:
    """Deserialize a Redis value; decompress if it was compressed."""
    if raw is None:
        return None
    if not isinstance(raw, str):
        raw = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
    try:
        if raw.startswith(_GZIP_PREFIX):
            compressed = base64.b64decode(raw[len(_GZIP_PREFIX):].encode("ascii"))
            payload = gzip.decompress(compressed)
            return json.loads(payload)
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Cache decode failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Async API
# ---------------------------------------------------------------------------


async def cache_get(key: str) -> Any | None:
    """Fetch a cached value by key, returning None on miss/error."""
    try:
        redis = get_redis()
        raw = await redis.get(key)
        return _deserialize(raw)
    except Exception as exc:
        logger.debug("Redis async cache read failed for %s: %s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Store a JSON-serializable value with TTL."""
    try:
        redis = get_redis()
        payload = _serialize(value)
        await redis.setex(key, ttl, payload)
    except Exception as exc:
        logger.debug("Redis async cache write failed for %s: %s", key, exc)


async def cache_delete(key: str) -> None:
    try:
        redis = get_redis()
        await redis.delete(key)
    except Exception as exc:
        logger.debug("Redis async cache delete failed for %s: %s", key, exc)


async def cache_delete_pattern(pattern: str) -> None:
    try:
        redis = get_redis()
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
    except Exception as exc:
        logger.debug("Redis async cache delete pattern failed for %s: %s", pattern, exc)


# ---------------------------------------------------------------------------
# Sync API
# ---------------------------------------------------------------------------


def cache_get_sync(key: str) -> Any | None:
    """Fetch a cached value synchronously."""
    try:
        redis = get_redis_sync()
        raw = redis.get(key)
        return _deserialize(raw)
    except Exception as exc:
        logger.debug("Redis sync cache read failed for %s: %s", key, exc)
        return None


def cache_set_sync(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Store a JSON-serializable value with TTL synchronously."""
    try:
        redis = get_redis_sync()
        payload = _serialize(value)
        redis.setex(key, ttl, payload)
    except Exception as exc:
        logger.debug("Redis sync cache write failed for %s: %s", key, exc)


def cache_delete_sync(key: str) -> None:
    try:
        redis = get_redis_sync()
        redis.delete(key)
    except Exception as exc:
        logger.debug("Redis sync cache delete failed for %s: %s", key, exc)


def cache_delete_pattern_sync(pattern: str) -> None:
    try:
        redis = get_redis_sync()
        keys = redis.keys(pattern)
        if keys:
            redis.delete(*keys)
    except Exception as exc:
        logger.debug("Redis sync cache delete pattern failed for %s: %s", pattern, exc)
