"""
AI response cache diagnostics probe.

Verifies that the shared LLM response cache (chart_ai_insights) can read
and write through the service-role Supabase client. Prints PASS/FAIL for
each stage so silent cache failures become visible.

Run from repo root:  python fastapi-backend/scripts/check_ai_cache.py
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

_repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo / "fastapi-backend"))

from dotenv import load_dotenv

load_dotenv(dotenv_path=_repo / ".env")

import os

print("=" * 60)
print("AI CACHE PROBE")
print("=" * 60)
print(f"  SUPABASE_URL              : {'SET' if os.getenv('SUPABASE_URL') else 'MISSING'}")
print(f"  SUPABASE_SERVICE_ROLE_KEY : {'SET' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'MISSING'}")

failures = 0

# 1. Client init
try:
    from app.services.supabase_service import get_supabase_client

    client = get_supabase_client()
    print("  [PASS] Supabase service client initialized")
except Exception as exc:
    print(f"  [FAIL] Supabase client init: {exc}")
    sys.exit(1)

# 2. Table readable
try:
    resp = (
        client.table("chart_ai_insights")
        .select("id", count="exact")
        .limit(1)
        .execute()
    )
    print(f"  [PASS] chart_ai_insights readable ({resp.count or 0} rows)")
except Exception as exc:
    print(f"  [FAIL] chart_ai_insights read: {exc}")
    sys.exit(1)

# 3. Write + read + cleanup via the shared helper
from app.services.llm_response_cache import (
    cache_insight,
    get_cached_insight,
    hash_cache_key,
)

probe_hash = hash_cache_key({"probe": str(uuid.uuid4())})
probe_text = "cache probe payload"

try:
    cache_insight("cache_probe", probe_hash, probe_text)
    print("  [PASS] cache_insight write")
except Exception as exc:
    print(f"  [FAIL] cache_insight write: {exc}")
    failures += 1

try:
    got = get_cached_insight("cache_probe", probe_hash)
    if got == probe_text:
        print("  [PASS] get_cached_insight read-back")
    else:
        print(f"  [FAIL] read-back mismatch: {got!r}")
        failures += 1
except Exception as exc:
    print(f"  [FAIL] get_cached_insight: {exc}")
    failures += 1

# 4. Cleanup probe rows
try:
    client.table("chart_ai_insights").delete().eq(
        "chart_type", "cache_probe"
    ).eq("chart_data_hash", probe_hash).execute()
    print("  [PASS] probe row cleanup")
except Exception as exc:
    print(f"  [WARN] probe cleanup failed (orphan row remains): {exc}")

print("=" * 60)
print("RESULT:", "FAIL" if failures else "PASS")
print("=" * 60)
sys.exit(1 if failures else 0)
