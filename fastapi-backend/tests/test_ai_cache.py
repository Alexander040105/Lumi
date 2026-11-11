"""Fixture-based assertions for the shared LLM response cache.

Uses an in-memory fake of the chainable Supabase query API so tests run
without network or credentials. The real supabase_service module is stubbed
in sys.modules because it requires pydantic_settings at import time.

Run with: python -m pytest fastapi-backend/tests/test_ai_cache.py -q
or: python fastapi-backend/tests/test_ai_cache.py
"""
from __future__ import annotations

import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub supabase_service before llm_response_cache lazily imports it.
_stub = types.ModuleType("app.services.supabase_service")
_stub.get_supabase_client = lambda: None  # replaced per-test
sys.modules["app.services.supabase_service"] = _stub

from app.services.llm_response_cache import (  # noqa: E402
    MAX_VARIANTS,
    cache_insight,
    get_cached_insight,
    hash_cache_key,
)


class _Result:
    def __init__(self, data, count=None):
        self.data = data
        self.count = count


class _Query:
    """Minimal chainable query over a list of row dicts."""

    def __init__(self, rows, op="select"):
        self._rows = rows
        self._op = op
        self._filters = []
        self._limit = None
        self._order_col = None
        self._count = None
        self._payload = None

    def select(self, _cols, count=None):
        self._count = count
        return self

    def insert(self, payload):
        self._op = "insert"
        self._payload = payload
        return self

    def delete(self):
        self._op = "delete"
        return self

    def eq(self, col, val):
        self._filters.append((col, val))
        return self

    def order(self, col):
        self._order_col = col
        return self

    def limit(self, n):
        self._limit = n
        return self

    def _match(self, row):
        return all(row.get(c) == v for c, v in self._filters)

    def execute(self):
        if self._op == "insert":
            row = dict(self._payload)
            row.setdefault("id", len(self._rows) + 1)
            row.setdefault(
                "created_at", datetime.now(timezone.utc).isoformat()
            )
            self._rows.append(row)
            return _Result([row])
        matched = [r for r in self._rows if self._match(r)]
        if self._op == "delete":
            for r in matched:
                self._rows.remove(r)
            return _Result(matched)
        if self._order_col:
            matched.sort(key=lambda r: str(r.get(self._order_col, "")))
        if self._limit:
            matched = matched[: self._limit]
        return _Result(matched, count=len(matched))


class _FakeClient:
    def __init__(self):
        self.rows = []

    def table(self, _name):
        return _Query(self.rows)


def _patch_client():
    fake = _FakeClient()
    _stub.get_supabase_client = lambda: fake
    return fake


def test_hash_cache_key_stable():
    a = hash_cache_key({"x": 1, "y": [2, 3]})
    b = hash_cache_key({"y": [2, 3], "x": 1})
    assert a == b
    assert len(a) == 64


def test_cache_write_then_read():
    _patch_client()
    h = hash_cache_key("d1")
    cache_insight("chart", h, "hello")
    assert get_cached_insight("chart", h) == "hello"


def test_cache_miss_returns_none():
    _patch_client()
    assert get_cached_insight("chart", "nope") is None


def test_variant_rotation_cap():
    fake = _patch_client()
    h = hash_cache_key("d2")
    for i in range(MAX_VARIANTS + 2):
        cache_insight("chart", h, f"v{i}")
    remaining = [
        r["insight"]
        for r in fake.rows
        if r["chart_type"] == "chart" and r["chart_data_hash"] == h
    ]
    assert len(remaining) == MAX_VARIANTS
    # oldest evicted — newest kept
    assert remaining[-1] == f"v{MAX_VARIANTS + 1}"
    assert "v0" not in remaining


def test_max_age_expiry():
    fake = _patch_client()
    h = hash_cache_key("d3")
    old = datetime.now(timezone.utc) - timedelta(days=30)
    fake.rows.append({
        "id": 1,
        "chart_type": "chat",
        "chart_data_hash": h,
        "insight": "stale",
        "created_at": old.isoformat(),
    })
    assert get_cached_insight("chat", h, max_age_seconds=7 * 86400) is None
    assert get_cached_insight("chat", h) == "stale"  # no TTL → still served


def test_read_back_strips_source_dump():
    fake = _patch_client()
    h = hash_cache_key("d4")
    fake.rows.append({
        "id": 2,
        "chart_type": "map",
        "chart_data_hash": h,
        "insight": "Solar is viable.\n\nSources: plants_table, solar_irradiance",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    got = get_cached_insight("map", h)
    assert "Sources:" not in got
    assert "Solar is viable." in got


def test_read_failure_soft_misses():
    def _boom():
        raise RuntimeError("no supabase")

    _stub.get_supabase_client = _boom
    assert get_cached_insight("chart", "x") is None
    cache_insight("chart", "x", "y")  # must not raise


def _run():
    test_hash_cache_key_stable()
    test_cache_write_then_read()
    test_cache_miss_returns_none()
    test_variant_rotation_cap()
    test_max_age_expiry()
    test_read_back_strips_source_dump()
    test_read_failure_soft_misses()
    print("all test_ai_cache assertions passed")


if __name__ == "__main__":
    _run()
