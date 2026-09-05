"""LUMI failure & recovery matrix — controlled failure-injection evidence.

Simulates dependency failures and malformed inputs against the real FastAPI
app via TestClient + targeted patching of client singletons. No external
credentials or .env values are modified; the only real network call is one
Groq fallback request in TC-FR-01.

Usage:
    python docs/09-Technical-Evaluation/artifacts/scripts/failure_matrix.py

Writes artifacts/failure/failure_matrix.json and prints a summary.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "fastapi-backend"))

import httpx  # noqa: E402

LOCALHOST_HDR = {"X-Forwarded-For": "127.0.0.1"}   # loopback skip (no throttle noise)
PUBLIC_HDR = {"X-Forwarded-For": "203.0.113.77"}   # TEST-NET-3 → limiter engages

RESULTS: list[dict] = []


def record(tid: str, scenario: str, observed: str, verdict: str, detail: str = ""):
    RESULTS.append({
        "id": tid, "scenario": scenario, "observed": observed,
        "verdict": verdict, "detail": detail[:600],
    })
    print(f"{tid:>10} | {verdict:<8} | {observed}")


def main() -> None:
    from fastapi.testclient import TestClient
    from main import app
    from app.services import supabase_service, redis_client
    from app.services import gemini_funcs, llm_client

    client = TestClient(app, raise_server_exceptions=False)

    # ------------------------------------------------------------------
    # TC-FR-01  Gemini failure -> Groq emergency fallback (live Groq call)
    # ------------------------------------------------------------------
    try:
        with patch.object(llm_client, "LLM_PROVIDER", "gemini"), \
             patch("app.services.gemini_funcs.generate_gemini_response",
                   side_effect=RuntimeError("simulated Gemini outage")):
            t0 = time.perf_counter()
            resp = llm_client.generate_response(
                "Reply with the single word: alive", max_retries=1)
            ms = (time.perf_counter() - t0) * 1000
        if resp:
            record("TC-FR-01", "Gemini outage -> Groq fallback",
                   f"Fallback produced text in {ms:.0f}ms", "GRACEFUL",
                   f"resp={resp[:80]!r}")
        else:
            record("TC-FR-01", "Gemini outage -> Groq fallback",
                   "Fallback returned empty", "DEGRADED")
    except Exception as exc:
        record("TC-FR-01", "Gemini outage -> Groq fallback",
               f"Exception propagated: {type(exc).__name__}", "FAIL",
               str(exc))

    # ------------------------------------------------------------------
    # TC-FR-02  EcoSim AI call exceeds hard timeout -> fallback dict
    # ------------------------------------------------------------------
    try:
        with patch.object(gemini_funcs, "_AI_CALL_TIMEOUT", 0.05), \
             patch.object(gemini_funcs, "_get_cached_ai_analysis",
                          lambda *a, **k: None), \
             patch.object(gemini_funcs, "_set_cached_ai_analysis",
                          lambda *a, **k: None), \
             patch.object(gemini_funcs, "_build_renewable_analysis_result",
                          lambda p: (time.sleep(2.0), {})[1]):
            t0 = time.perf_counter()
            out = gemini_funcs.analyze_renewable_results(
                {"municipality_id": 5441, "test_probe": time.time()})
            ms = (time.perf_counter() - t0) * 1000
        ok = out.get("error") == "AI analysis timed out" and ms < 1500
        record("TC-FR-02", "EcoSim AI timeout -> fallback dict",
               f"Returned '{out.get('error', 'no-error-field')}' in {ms:.0f}ms",
               "GRACEFUL" if ok else "FAIL", json.dumps(out)[:200])
    except Exception as exc:
        record("TC-FR-02", "EcoSim AI timeout -> fallback dict",
               f"Exception: {type(exc).__name__}", "FAIL", str(exc))

    # ------------------------------------------------------------------
    # TC-FR-03  All LLM providers down -> EcoSim AI still returns fallback
    # ------------------------------------------------------------------
    try:
        with patch.object(gemini_funcs, "_get_cached_ai_analysis",
                          lambda *a, **k: None), \
             patch.object(gemini_funcs, "_build_renewable_analysis_result",
                          side_effect=RuntimeError("all LLMs down")):
            out = gemini_funcs.analyze_renewable_results(
                {"municipality_id": 5441, "test_probe": time.time()})
        ok = out.get("error") == "AI analysis timed out" or "summary" in out
        record("TC-FR-03", "LLM total outage -> EcoSim AI path",
               f"Returned fallback dict, error={out.get('error')!r}",
               "GRACEFUL" if ok else "FAIL")
    except Exception as exc:
        record("TC-FR-03", "LLM total outage -> EcoSim AI path",
               f"Exception: {type(exc).__name__}", "FAIL", str(exc))

    # ------------------------------------------------------------------
    # TC-FR-04  Supabase outage -> health degrades, EcoSim CSV fallback
    # ------------------------------------------------------------------
    class BrokenClient:
        def table(self, *a, **k):
            raise httpx.ConnectError("simulated Supabase outage")
        def rpc(self, *a, **k):
            raise httpx.ConnectError("simulated Supabase outage")

    try:
        supabase_service._supabase_client = BrokenClient()
        supabase_service._supabase_public_client = BrokenClient()

        r = client.get("/api/v1/health/detailed", headers=LOCALHOST_HDR)
        det = r.json()
        record("TC-FR-04a", "Supabase down -> /health/detailed",
               f"status={det.get('status')} supabase={det.get('checks',{}).get('supabase')}",
               "GRACEFUL" if det.get("checks", {}).get("supabase") == "error" else "FAIL",
               json.dumps(det)[:300])

        r = client.get("/api/v1/ecosim/municipalities", headers=LOCALHOST_HDR)
        record("TC-FR-04b", "Supabase down -> /ecosim/municipalities",
               f"HTTP {r.status_code} body={r.text[:120]}",
               "GRACEFUL" if r.status_code in (200, 503) else "CRASH")

        r = client.get("/api/v1/ecosim/", headers=LOCALHOST_HDR, params={
            "municipality_id": 5441, "monthly_consumption": 350,
            "monthly_bill": 5000})
        record("TC-FR-04c", "Supabase down -> /ecosim/ simulation",
               f"HTTP {r.status_code} body={r.text[:160]}",
               "GRACEFUL" if r.status_code in (200, 404, 503) else "CRASH")

        r = client.get("/api/v1/protected/me", headers=LOCALHOST_HDR)
        record("TC-FR-04d", "Supabase down -> /protected/me (no token)",
               f"HTTP {r.status_code} body={r.text[:120]}",
               "GRACEFUL" if r.status_code in (401, 503) else "CRASH")
    except Exception as exc:
        record("TC-FR-04", "Supabase outage", f"Harness error: {exc}", "FAIL")
    finally:
        supabase_service._supabase_client = None
        supabase_service._supabase_public_client = None

    # ------------------------------------------------------------------
    # TC-FR-05  Redis outage -> NullRedis, requests still succeed
    # ------------------------------------------------------------------
    try:
        redis_client._redis_sync = redis_client.NullRedisSync()
        redis_client._redis_async = redis_client.NullRedis()

        r = client.get("/api/v1/health/detailed", headers=LOCALHOST_HDR)
        redis_status = r.json().get("checks", {}).get("redis")
        r2 = client.get("/api/v1/map/solar", headers=LOCALHOST_HDR)
        record("TC-FR-05", "Redis down -> health + /map/solar",
               f"redis={redis_status}, /map/solar={r2.status_code}",
               "GRACEFUL" if r2.status_code == 200 else "FAIL")
    except Exception as exc:
        record("TC-FR-05", "Redis outage", f"Harness error: {exc}", "FAIL")
    finally:
        redis_client._redis_sync = None
        redis_client._redis_async = None

    # ------------------------------------------------------------------
    # TC-FR-06  NASA POWER down — N/A at runtime (code-verified, ETL only)
    # ------------------------------------------------------------------
    record("TC-FR-06", "NASA POWER outage at runtime",
           "N/A — runtime climate is served from Supabase + bundled CSVs; "
           "NASA POWER exists only in disabled ETL scripts", "N/A")

    # ------------------------------------------------------------------
    # TC-FR-07  Malformed inputs (cross-checked with endpoint sweep)
    # ------------------------------------------------------------------
    r = client.get("/api/v1/ecosim/", headers=LOCALHOST_HDR, params={
        "municipality_id": 999999, "monthly_consumption": 350,
        "monthly_bill": 5000})
    record("TC-FR-07a", "Invalid municipality_id -> /ecosim/",
           f"HTTP {r.status_code} {r.text[:100]}",
           "GRACEFUL" if r.status_code == 404 else "FAIL")
    r = client.get("/api/v1/geothermal/999999", headers=LOCALHOST_HDR)
    record("TC-FR-07b", "Invalid municipality_id -> /geothermal/{id}",
           f"HTTP {r.status_code} {r.text[:140]}",
           "GRACEFUL" if r.status_code == 404 else "DEGRADED")

    # ------------------------------------------------------------------
    # TC-FR-08  ML worker down -> 503 for proxied paths (api.index wrapper)
    # ------------------------------------------------------------------
    try:
        os.environ["ML_WORKER_URL"] = "http://127.0.0.1:59999"
        import importlib
        import api.index as api_index  # noqa
        importlib.reload(api_index)
        wrapped = TestClient(api_index.app, raise_server_exceptions=False)
        r = wrapped.post("/api/v1/chat", headers=LOCALHOST_HDR,
                         json={"message": "hello"})
        record("TC-FR-08", "ML worker down -> /api/v1/chat proxy",
               f"HTTP {r.status_code} body={r.text[:160]}",
               "GRACEFUL" if r.status_code == 503 else "FAIL")
    except Exception as exc:
        record("TC-FR-08", "ML worker down -> proxy",
               f"Harness error: {type(exc).__name__}: {exc}", "FAIL")
    finally:
        os.environ.pop("ML_WORKER_URL", None)

    # ------------------------------------------------------------------
    # TC-FR-09  Rate limiting + XFF bypass demonstration
    #   TestClient's client host is 'testclient' (non-loopback), so without
    #   XFF the limiter applies; XFF=127.0.0.1 spoofs loopback and bypasses.
    # ------------------------------------------------------------------
    codes_public = []
    for _ in range(70):
        codes_public.append(
            client.get("/api/v1/ecosim/provinces", headers=PUBLIC_HDR).status_code)
    n429 = codes_public.count(429)
    record("TC-FR-09a", "Burst 70 req, public XFF -> 429 throttling",
           f"429s={n429}/70 (limit=60/min)",
           "GRACEFUL" if n429 > 0 else "FAIL",
           f"codes={ {c: codes_public.count(c) for c in set(codes_public)} }")

    codes_spoof = []
    for _ in range(70):
        codes_spoof.append(
            client.get("/api/v1/ecosim/provinces",
                       headers={"X-Forwarded-For": "127.0.0.1"}).status_code)
    n429_s = codes_spoof.count(429)
    record("TC-FR-09b", "Burst 70 req, spoofed loopback XFF -> bypass",
           f"429s={n429_s}/70 — limiter bypassed" if n429_s == 0 else f"429s={n429_s}/70",
           "BYPASS-CONFIRMED" if n429_s == 0 else "GRACEFUL")

    # ------------------------------------------------------------------
    # TC-FR-10  Body limits, malformed JSON, structured 500
    # ------------------------------------------------------------------
    big = b"x" * (1_100_000)
    r = client.post("/api/v1/ecosim/", headers=LOCALHOST_HDR, content=big)
    record("TC-FR-10a", "Body >1MB -> limiter",
           f"HTTP {r.status_code} {r.text[:120]}",
           "GRACEFUL" if r.status_code == 413 else "FAIL")

    r = client.post("/api/v1/ecosim/", headers={**LOCALHOST_HDR,
                    "Content-Type": "application/json"}, content=b"{not json")
    record("TC-FR-10b", "Malformed JSON body",
           f"HTTP {r.status_code} {r.text[:120]}",
           "GRACEFUL" if r.status_code in (400, 422) else "FAIL")

    r = client.get("/api/v1/geospatial/centroids/bad-level/abc",
                   headers=LOCALHOST_HDR)
    record("TC-FR-10c", "Bad path params -> structured error",
           f"HTTP {r.status_code} {r.text[:140]}",
           "GRACEFUL" if r.status_code in (400, 404, 422) else "DEGRADED")

    out_path = (Path(__file__).resolve().parents[1] / "failure"
                / "failure_matrix.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(RESULTS, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\n{len(RESULTS)} scenarios recorded -> {out_path}")


if __name__ == "__main__":
    main()
