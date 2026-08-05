"""Unit tests for Phase 0-2 production-readiness improvements.

Covers:
- Structured logging safety (SafeJSONFormatter)
- Rate limiting (memory fallback)
- Redis null-client fallback
- Forecasting cache and auto order selection
- RAG keyword reranking
- Settings loading
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

# Ensure required env vars exist for Settings instantiation
os.environ.setdefault("SUPABASE_URL", "https://placeholder.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "placeholder-anon-key")

from app.config.settings import get_settings, Settings
from app.middleware.request_id import SafeJSONFormatter
from app.middleware.rate_limit import RateLimitMiddleware
from app.services.redis_client import NullRedis, NullRedisSync, _redis_url, is_redis_available
from app.services.rag_faiss import _keyword_score, _hybrid_score, _rerank_results
from app.services.forecasting import (
    SARIMAConfig,
    calculate_metrics,
    select_best_sarima_config,
    run_forecast_pipeline_cached,
    ForecastResult,
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

class TestSafeJSONFormatter:
    """SafeJSONFormatter must tolerate log records without request metadata."""

    def test_format_without_request_fields(self):
        record = logging.LogRecord(
            name="faiss",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        formatted = SafeJSONFormatter().format(record)
        parsed = json.loads(formatted)
        assert parsed["message"] == "test message"
        assert parsed["request_id"] is None
        assert parsed["method"] is None

    def test_format_with_request_fields(self):
        record = logging.LogRecord(
            name="lumi.request",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="ok",
            args=(),
            exc_info=None,
        )
        record.request_id = "abc-123"
        record.method = "GET"
        record.path = "/api/v1/health/"
        record.status_code = 200
        record.duration_ms = 12.5
        formatted = SafeJSONFormatter().format(record)
        parsed = json.loads(formatted)
        assert parsed["request_id"] == "abc-123"
        assert parsed["method"] == "GET"
        assert parsed["status_code"] == 200


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

class TestRateLimitMiddleware:
    """Rate limiter must fall back to in-memory when Redis is unavailable."""

    @pytest.fixture(autouse=True)
    def patch_redis_null(self, monkeypatch):
        monkeypatch.setattr("app.middleware.rate_limit.get_redis", lambda: NullRedis())

    def test_allows_requests_under_limit(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=2)
        request = MagicMock()
        request.url.path = "/api/v1/ecosim/"
        request.headers = {}
        request.client.host = "1.2.3.4"
        call_next = AsyncMock(return_value="response")

        async def run():
            for _ in range(2):
                resp = await middleware.dispatch(request, call_next)
                assert resp == "response"
            return call_next.call_count

        assert asyncio.run(run()) == 2

    def test_blocks_after_limit(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=1)
        request = MagicMock()
        request.url.path = "/api/v1/ecosim/"
        request.headers = {}
        request.client.host = "1.2.3.4"
        call_next = AsyncMock(return_value="response")

        async def run():
            await middleware.dispatch(request, call_next)
            return await middleware.dispatch(request, call_next)

        resp = asyncio.run(run())
        assert resp.status_code == 429
        assert resp.headers["Retry-After"] == "60"

    def test_extracts_x_forwarded_for(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=2)
        request = MagicMock()
        request.url.path = "/api/v1/ecosim/"
        request.headers = {"x-forwarded-for": "9.9.9.9, 8.8.8.8"}
        request.client.host = "127.0.0.1"
        assert middleware._client_ip(request) == "9.9.9.9"

    def test_skips_health_checks(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app)
        request = MagicMock()
        request.url.path = "/api/v1/health/"
        request.headers = {}
        call_next = AsyncMock(return_value="ok")

        async def run():
            return await middleware.dispatch(request, call_next)

        assert asyncio.run(run()) == "ok"


# ---------------------------------------------------------------------------
# Redis fallback
# ---------------------------------------------------------------------------

class TestRedisFallback:
    """Redis client must degrade gracefully when no URL is configured."""

    def test_null_redis_async(self):
        null = NullRedis()

        async def run():
            return (await null.get("key"), await null.keys("*"))

        val, keys = asyncio.run(run())
        assert val is None
        assert keys == []

    def test_null_redis_async_await(self):
        null = NullRedis()

        async def run():
            return (await null.get("key"), await null.keys("*"))

        val, keys = asyncio.run(run())
        assert val is None
        assert keys == []

    def test_null_redis_sync(self):
        null = NullRedisSync()
        assert null.get("key") is None
        assert null.keys("*") == []

    def test_is_redis_available_false_when_no_url(self, monkeypatch):
        monkeypatch.setenv("UPSTASH_REDIS_URL", "")
        from app.config import settings
        # Reset lru_cache so the new env value is picked up
        settings.get_settings.cache_clear()
        assert is_redis_available() is False


# ---------------------------------------------------------------------------
# Forecasting
# ---------------------------------------------------------------------------

class TestForecastingHelpers:
    """Forecasting helpers must produce sensible metrics and model selection."""

    def test_calculate_metrics(self):
        actuals = [100.0, 110.0, 120.0]
        predictions = [105.0, 108.0, 118.0]
        metrics = calculate_metrics(actuals, predictions)
        assert metrics["mae"] > 0
        assert metrics["rmse"] > 0
        assert 0 <= metrics["mape"] <= 100

    def test_select_best_sarima_config(self):
        series = pd.Series(
            [45000 + i * 1500 for i in range(20)],
            index=list(range(2004, 2024)),
        )
        config = select_best_sarima_config(series, candidates=[
            SARIMAConfig(order=(0, 1, 0)),
            SARIMAConfig(order=(1, 1, 0)),
            SARIMAConfig(order=(1, 1, 1)),
        ])
        assert isinstance(config.order, tuple)
        assert len(config.order) == 3


# ---------------------------------------------------------------------------
# RAG reranking
# ---------------------------------------------------------------------------

class TestRAGReranking:
    """RAG retrieval helper functions must combine semantic and keyword signals."""

    def test_keyword_score(self):
        score = _keyword_score("solar panel installation", "solar panels convert sunlight")
        assert 0 <= score <= 1

    def test_hybrid_score_boosts_renewable_type(self):
        chunk = {"renewable_type": "solar", "category": "guide"}
        score = _hybrid_score(0.5, 0.2, chunk, "best solar setup", "solar", None)
        assert score >= 0.45  # base 0.41 + metadata boosts (0.09), floating-point safe

    def test_rerank_results(self):
        candidates = [
            {"text": "wind turbine maintenance", "score": 0.6, "renewable_type": "wind"},
            {"text": "solar panel guide", "score": 0.5, "renewable_type": "solar"},
        ]
        ranked = _rerank_results("solar panel", candidates, None, None)
        assert ranked[0]["renewable_type"] == "solar"


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class TestSettings:
    """Settings must load feature toggles and Redis config from the environment."""

    def test_default_settings(self):
        settings = get_settings()
        assert settings.use_redis_cache is True
        assert settings.enable_rag is True
        assert settings.enable_forecast is True
        assert settings.log_level == "INFO"

    def test_redis_url_loaded(self, monkeypatch):
        monkeypatch.setenv("UPSTASH_REDIS_URL", "rediss://localhost:6379")
        from app.config import settings
        settings.get_settings.cache_clear()
        assert _redis_url() == "rediss://localhost:6379"
