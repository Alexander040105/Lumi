from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter

from app.services.redis_client import is_redis_available

router = APIRouter()

_start_time = time.time()


@router.get("/")
async def health_check() -> dict[str, Any]:
    """Basic liveness probe."""
    return {"status": "ok"}


@router.get("/detailed")
async def detailed_health_check() -> dict[str, Any]:
    """Detailed health check with dependency status."""
    uptime_s = round(time.time() - _start_time, 2)

    checks: dict[str, str] = {}

    # Supabase check
    try:
        from app.services.supabase_service import get_supabase_client
        client = get_supabase_client()
        resp = client.table("regions").select("region_id").limit(1).execute()
        checks["supabase"] = "ok" if resp.data is not None else "degraded"
    except Exception:
        checks["supabase"] = "error"

    # Redis check (optional)
    try:
        checks["redis"] = "ok" if is_redis_available() else "not_configured"
    except Exception:
        checks["redis"] = "not_configured"

    # RAG index check
    try:
        from app.services.rag_pipeline import index_stats
        stats = index_stats()
        checks["rag_index"] = "ok" if stats.get("index_present") else "not_loaded"
    except Exception:
        checks["rag_index"] = "not_loaded"

    all_ok = all(v in ("ok", "not_configured", "not_loaded") for v in checks.values())

    return {
        "status": "ok" if all_ok else "degraded",
        "uptime_seconds": uptime_s,
        "checks": checks,
    }
