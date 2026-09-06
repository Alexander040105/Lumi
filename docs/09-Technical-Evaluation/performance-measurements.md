# Performance Measurements — LUMI

**Date:** September 5, 2026
**Scope:** FastAPI endpoint latency, LLM latency, Supabase query time, frontend bundle weight, production cold-start smoke
**Method:** `artifacts/scripts/benchmark.py` — warm-cache, n=30 per endpoint (n=5 for LLM-backed), min/mean/p50/p95/max; direct Supabase RPC timing; `vite build` size analysis; light production smoke.

---

## 1. Environment

| Item | Value |
|---|---|
| Local backend | uvicorn single worker, Python 3.13.2, Windows 11 |
| Data tier | Supabase (eu-west, live) + Upstash Redis |
| Production | `https://lumi-backend-ten.vercel.app` (serverless) |
| Caveat | Local timings include loopback overhead; absolute ms are indicative, not contractual. Cross-run CPU contention during the first pass is flagged where relevant (see load doc). |

## 2. API Endpoint Latency (single user, warm)

| Endpoint | n | min | mean | p50 | p95 | max | Status |
|---|---|---|---|---|---|---|---|
| `GET /health` | 30 | 1.2 | 4.8 | 1.8 | 3.6 | 84.7 | ✅ <500ms |
| `GET /health/detailed` | 30 | 174.2 | 191.3 | 183.0 | 214.1 | 403.3 | ✅ <5s |
| `GET /energyhub/overview` | 30 | 4.2 | 6.3 | 5.9 | 8.6 | 9.7 | ✅ <2s |
| `GET /energyhub/forecast` | 30 | 2.3 | 3.7 | 3.5 | 6.2 | 6.4 | ✅ |
| `GET /energyhub/trends` | 30 | 5.3 | 6.8 | 6.3 | 9.6 | 10.5 | ✅ |
| `GET /energyhub/map-data` | 30 | 36.5 | 37.5 | 37.1 | 39.4 | 39.5 | ✅ |
| `GET /energyhub/source-breakdown` | 30 | 1.9 | 2.7 | 2.5 | 3.7 | 7.5 | ✅ |
| `GET /energyhub/grid-breakdown` | 30 | 2.1 | 3.1 | 2.7 | 5.7 | 5.7 | ✅ |
| `GET /energyhub/model-comparison` | 30 | 3.4 | 4.5 | 4.2 | 5.9 | 6.2 | ✅ |
| `GET /energyhub/provincial-demand` | 30 | 3.5 | 4.9 | 4.7 | 7.3 | 7.3 | ✅ |
| `GET /ecosim/municipalities` | 30 | 42.0 | 49.7 | 44.1 | 109.2 | 136.3 | ✅ |
| `GET /ecosim/provinces` | 30 | 35.7 | 37.3 | 36.6 | 40.0 | 42.1 | ✅ |
| `GET /geothermal/plants` | 30 | 2.2 | 3.5 | 3.3 | 5.6 | 6.2 | ✅ |
| `GET /geothermal/5441` | 30 | 211.8 | 222.1 | 219.1 | 239.3 | 239.9 | ✅ |
| `GET /geospatial/climate` | 30 | 42.1 | 45.1 | 44.9 | 48.0 | 48.6 | ✅ |
| `GET /map/coverage` | 30 | 36.7 | 38.4 | 38.0 | 40.9 | 41.3 | ✅ |
| `GET /map/solar` | 30 | 50.6 | 57.1 | 57.7 | 60.4 | 60.9 | ✅ |
| `GET /products/recommend?energy_type=solar` | 30 | 7.5 | 13.1 | 13.8 | 19.1 | 19.5 | ✅ |
| `GET /forecast/models` | 30 | 72.3 | 82.2 | 78.5 | 103.4 | 154.3 | ✅ |
| `GET /ecosim/` (simulation) | 5 | 448.2 | 450.2 | 449.5 | 454.5 | 454.5 | ✅ <3s |
| `GET /ecosim/ai` | 5 | 444.1 | 458.0 | 451.3 | 475.9 | 475.9 | ✅ <5s |
| `GET /energyhub/ai-insight?use_llm=true` | 5 | 42.0 | 676.8 | 44.3 | **3207.9** | 3207.9 | ⚠️ mixed 200/401 |
| `GET /energyhub/map-explanation` | 5 | 110.7 | 113.4 | 111.4 | 120.7 | 120.7 | ✅ |

Raw: `artifacts/perf/latency.csv`. The `ai-insight` p95 is inflated by one full LLM call (~3.2s); the 401s are anonymous-quota rejections, not slowdowns.

## 3. LLM / AI Latency

| Path | Observation | Evidence |
|---|---|---|
| Groq (primary) | EcoSim AI response ≈ **450–476ms** p50–p95 including Supabase reads | `latency.csv` `ecosim_ai` |
| Gemini→Groq fallback | Injected Gemini failure → Groq answered in **1,683ms** | `failure_matrix.json` TC-FR-01 |
| AI timeout path | Hard timeout returns structured fallback in **61ms** (`"AI analysis timed out"`) | TC-FR-02 |
| `ai-insight` cold LLM | ~3.2s observed for the one full LLM round-trip | `latency.csv` |

The dedicated chatbot endpoint (`/api/v1/chat`) is not mounted — chatbot-latency rubric coverage is provided by the live AI endpoints above (see functional doc GAP-01).

## 4. Database / Supabase Query Time (direct, n=10)

| Query | mean | p50 | p95 | max | Notes |
|---|---|---|---|---|---|
| `regions` select-1 | 160.8ms | 70.6 | 962.9 | 962.9 | p95 = cold-connection outlier; steady-state ~70ms |
| `municipalities` select-10 | 100.7ms | 74.0 | 317.9 | 317.9 | First-call warmup visible |
| `climate_monthly` filtered | 78.1ms | 76.1 | 88.0 | 88.0 | Indexed lookup, tight distribution |

Raw: `artifacts/perf/db_timings.csv`. Dominant cost is TLS+network to the managed Postgres endpoint (~70ms floor); query execution itself is sub-ms for these single-table selects.

## 5. Frontend Build / Load Characteristics

| Asset | Raw | Gzip | Note |
|---|---|---|---|
| `index-*.js` (main bundle) | ~6.35 MB | ~1.91 MB | Vite warns `>500 kB` — no route-level code splitting |
| `index-*.css` | ~61.4 kB | ~10.7 kB | Tailwind purged correctly |
| `vite build` | 9.6s | — | `artifacts/perf/vite-build.txt` |

First-load risk: the 1.9MB-gz single chunk is the dominant frontend bottleneck; route-based `React.lazy` splitting is the recommended follow-up (out of audit scope).

## 6. Production Smoke (light, non-destructive)

| Check | Result |
|---|---|
| `GET /api/v1/health` (prod) | 200 — cold start observed ~0.8–3.8s across endpoints |
| `GET /docs`, `/openapi.json` (prod) | 200 — exposed (INFO finding, see security doc) |
| Security headers (prod) | `server: Vercel`, `x-content-type-options`, `x-frame-options: DENY`, HSTS, CSP all present |
| CORS disallowed origin (prod) | Preflight → **400** blocked |

Raw: `artifacts/security/prod_smoke.txt`.

## 7. Existing Performance Test Suite

`fastapi-backend/tests/integration/test_performance.py` — **13/13 executed & passed**, covering response-time assertions and pagination behavior under the live app. Raw: `artifacts/functional/pytest-lumi-integration.txt`.

## 8. Findings

| # | Finding | Severity |
|---|---|---|
| P-01 | Single-chunk frontend bundle 1.91MB gz — no code splitting | Medium |
| P-02 | `ai-insight` unbounded LLM latency (3.2s p95 at n=5) | Low — quota-gated by design |
| P-03 | Supabase cold-connect spikes (p95 963ms on `regions`) | Low — connection reuse mitigates |
| P-04 | `geothermal/{id}` lookup 222ms mean — joins + no response cache noted | Info |

## 9. Limitations

- LLM samples are n=5 (quota-respecting); n=30 elsewhere.
- Production timing is smoke-level only — no load applied to Vercel (per scope).
- NASA POWER fetch latency: **N/A at runtime** — runtime climate data is served from Supabase/bundled CSVs; NASA POWER exists only in disabled ETL scripts (`api.py:16`). No timing is claimed.
- `TEST_DATABASE_URL` unavailable → direct SQL benchmark uses Supabase REST path (representative of the app's actual data path).

*End of Performance Measurements*
