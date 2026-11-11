"""Shared Supabase-backed cache for LLM-generated text responses.

Stores responses in the ``chart_ai_insights`` table keyed by
``(chart_type, chart_data_hash)``. Up to ``MAX_VARIANTS`` variants are kept
per key and a random one is served on read — this is what powers the
"Get a different explanation" rotation.

Everything fails soft: a missing table, RLS block, or absent
SUPABASE_SERVICE_ROLE_KEY logs a warning and returns a cache miss, never
an exception — generation continues normally.

Callers that need expiry pass ``max_age_seconds`` (e.g. chat, whose
answers depend on a changing RAG corpus). Insights need no TTL: their
hash already covers the input data and prompt version.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

TABLE = "chart_ai_insights"
MAX_VARIANTS = 3


def hash_cache_key(payload: Any) -> str:
    """Stable sha256 for a JSON-serialisable payload."""
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def get_cached_insight(
    chart_type: str,
    chart_hash: str,
    max_age_seconds: int | None = None,
) -> str | None:
    """Return a random cached variant for the key, or None on miss/stale."""
    try:
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = (
            client.table(TABLE)
            .select("insight,created_at")
            .eq("chart_type", chart_type)
            .eq("chart_data_hash", chart_hash)
            .execute()
        )
        rows = resp.data or []
    except Exception as exc:
        logger.warning("AI cache read failed for %s: %s", chart_type, exc)
        return None

    if max_age_seconds is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        rows = [r for r in rows if _is_fresh(r.get("created_at"), cutoff)]

    if not rows:
        return None

    # Serve text through the same cleanup used at write time so legacy
    # cached rows (e.g. ones containing a raw "Sources:" dump) render clean.
    from app.services.llm_sanitizer import strip_source_dump

    return strip_source_dump(random.choice(rows).get("insight") or "")


def _is_fresh(created_at: Any, cutoff: datetime) -> bool:
    try:
        ts = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts >= cutoff
    except Exception:
        return True


def cache_insight(
    chart_type: str,
    chart_hash: str,
    insight: str,
    max_variants: int = MAX_VARIANTS,
) -> None:
    """Store a variant for the key, evicting the oldest beyond ``max_variants``."""
    if not insight:
        return
    try:
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        count_resp = (
            client.table(TABLE)
            .select("id", count="exact")
            .eq("chart_type", chart_type)
            .eq("chart_data_hash", chart_hash)
            .execute()
        )
        existing = count_resp.count or 0
        if existing >= max_variants:
            oldest = (
                client.table(TABLE)
                .select("id")
                .eq("chart_type", chart_type)
                .eq("chart_data_hash", chart_hash)
                .order("created_at")
                .limit(1)
                .execute()
            )
            if oldest.data:
                client.table(TABLE).delete().eq("id", oldest.data[0]["id"]).execute()
        client.table(TABLE).insert({
            "chart_type": chart_type,
            "chart_data_hash": chart_hash,
            "insight": insight,
        }).execute()
    except Exception as exc:
        logger.warning("AI cache write failed for %s: %s", chart_type, exc)
