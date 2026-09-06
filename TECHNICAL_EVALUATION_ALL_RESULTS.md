# LUMI — Technical Evaluation: Complete Test Results

**Project:** LUMI — Data-Driven Environmental Intelligence System for Renewable Energy Decision Support (EcoSim · Energy Hub · AI features · FastAPI · React/Vite · Supabase · Groq/Gemini · Vercel)
**Compiled:** September 6, 2026
**Primary test session:** September 5, 2026 (retrospective audit + live endpoint/failure/security probing)
**Supersedes:** June 14–20, 2026 test run (included as historical record in Appendix G)
**Purpose:** Consolidated evidence package for thesis-panel / technical evaluation — all test results, measurements, logs, and architecture documentation in a single document.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Test Environment](#test-environment)
3. [Section 1 — Functional Test Results](#section-1--functional-test-results)
4. [Section 2 — Performance Measurements](#section-2--performance-measurements)
5. [Section 3 — Load and Scalability Test Results](#section-3--load-and-scalability-test-results)
6. [Section 4 — Security Test Results and Logs](#section-4--security-test-results-and-logs)
7. [Section 5 — System Architecture Documentation](#section-5--system-architecture-documentation)
8. [Section 6 — Failure and Recovery Test Results](#section-6--failure-and-recovery-test-results)
9. [Section 7 — ML Model and Calibration Results](#section-7--ml-model-and-calibration-results)
10. [Section 8 — Known Gaps and Limitations](#section-8--known-gaps-and-limitations)
11. [Appendices A–H — Raw Logs and Evidence Artifacts](#appendices--raw-logs-and-evidence-artifacts)

---

## Executive Summary

| Area | Headline Result |
|---|---|
| **Functional** | 333 automated assertions pass (176 unit + 77 backend + 9 frontend + 67 integration + 4 extra integration). Live endpoint sweep: **70/75 checks passed**, 5 low-severity validation findings. 30 DB-layer tests blocked on `TEST_DATABASE_URL` (deliberately not run against production). |
| **Performance** | All core endpoints p95 < 500 ms single-user; simulation ~450 ms; LLM path ~460 ms–3.2 s; Supabase ~70–160 ms/query; frontend bundle 1.91 MB gzipped (no code splitting). |
| **Load** | **Zero failures at all levels** (1→100 users); graceful degradation; interactive ceiling ~10–25 users on a single worker; ~11–14 RPS throughput plateau. |
| **Security** | XFF-spoof rate-limit/quota bypass **confirmed from a real LAN socket** (High); split-counter fail-open under Redis flapping (Medium); 87 backend + 7 frontend dependency advisories; all auth/JWT probes rejected correctly; 5/5 security headers present locally and in production. |
| **Failure/Recovery** | **15/17 scenarios graceful** — CSV fallback, NullRedis, LLM fallback + timeout, 503 proxy isolation, 413/422 input gates all verified live. |
| **ML models** | 6 forecasting models benchmarked on DOE 2003–2024 data: Linear Trend MAPE 4.97 % (best), ARIMA(1,1,1) MAPE 5.67 % (deployed). EcoSim calibrated across 84/120 provinces — Solar ~55 %, Wind ~42 %, Hydro ~4 % recommendation split. |
| **ISO 25010 self-evaluation** | Weighted score **3.60 / 5.0** ("Good") — see Appendix H. |

### Known gaps (honest accounting)

- Dedicated chatbot (`/api/v1/chat` + `ChatPage.jsx`) is **code-present but not mounted** — live AI coverage is via EcoSim AI + EnergyHub endpoints.
- `TEST_DATABASE_URL` not configured → 30 DB-layer tests pending (kept off production by design).
- OAuth/valid-token flows not exercised (no test credentials).
- Production load testing deliberately excluded — smoke-level only.
- NASA POWER is not part of runtime behavior — marked N/A, not measured.

---

## Test Environment

| Item | Value |
|---|---|
| OS | Windows 11 |
| Python | 3.13.2 (global env) |
| Backend runtime | uvicorn 0.30.6, single worker, `http://127.0.0.1:8000` |
| Node / npm | v24.15.0 / 11.12.1 |
| Test tooling | pytest 9.1.0 · Vitest 2.1.9 · Locust 2.46.4 · pip-audit 2.10.1 · Bandit 1.9.4 |
| Data tier | Live Supabase (eu-west) + Upstash Redis; bundled CSV fallbacks |
| LLM providers | Groq (primary, `LLM_PROVIDER` default), Gemini (fallback-capable) |
| Production target | `https://lumi-backend-ten.vercel.app` (serverless; smoke-tested only) |
| Frontend under test | `react-frontend` (React 18 + Vite + Tailwind) |

**Result legend used throughout:** ✅ Executed & passed · ❌ Executed & failed (defect logged) · ⚠️ Executed with caveat · ⏳ Blocked/pending — reason given · — N/A

---

## Section 1 — Functional Test Results

**Method:** Existing automated suites + live endpoint sweep (`endpoint_sweep.py`) that exercised every mounted API route with valid, invalid, boundary, and adversarial inputs. Test-case structure follows `lumi_tests/docs/test_results_template.md`.

### 1.1 Pre-existing suite results (all executed September 5, 2026)

| Suite | Result | Evidence |
|---|---|---|
| `lumi_tests/` unit suite | **176 passed** | `artifacts/functional/pytest-lumi-unit.txt` |
| `fastapi-backend/tests/` | **77 passed** | `artifacts/functional/pytest-backend.txt` |
| `react-frontend` Vitest | **9 passed** (3 files) | `artifacts/functional/vitest-frontend.txt` |
| `fastapi-backend/tests/integration/` | **67 passed, 2 skipped, 30 errors** | `artifacts/functional/pytest-lumi-integration.txt` |
| Live endpoint sweep | **70/75 passed** | `artifacts/functional/endpoint_sweep.jsonl` / `.csv` |

The 30 integration errors are all `TEST_DATABASE_URL`/`DATABASE_URL`-dependent DB tests — they were **not** run against production Supabase (destructive-write risk) and are marked ⏳ below.

### 1.2 Authentication Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-AUTH-001 | Register via Google OAuth | JWT token returned; user record created | Not executed — OAuth browser flow not scriptable without credentials | ⏳ | `auth.py` implements callback handler; needs interactive session |
| TC-AUTH-002 | Register via GitHub OAuth | JWT token returned; user record created | Not executed — same constraint | ⏳ | Code path exists (`app/routes/auth.py`) |
| TC-AUTH-003 | Access protected endpoint without token | HTTP 401 | `GET /protected/me` → **401** `{"detail":"Missing token"}` | ✅ | Live probe SEC-AUTH-01 |
| TC-AUTH-004 | Access protected endpoint with valid token | HTTP 200 + user data | Not executed — no test credentials available | ⏳ | Dependency `get_current_user` verifies via `client.auth.get_user` |
| TC-AUTH-005 | Access with expired token | HTTP 401 | Expired JWT minted with real secret → **401** | ✅ | Live probe SEC-AUTH-05 |
| TC-AUTH-006 | Logout / token revocation | Session invalidated | Not executed — requires authenticated session | ⏳ | Supabase manages token lifecycle |

### 1.3 EnergyHub Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-EH-001 | Load EnergyHub overview | Consumption/demand/generation stats | `GET /energyhub/overview` → 200, full stats object | ✅ | Sweep + benchmark (6.3 ms mean) |
| TC-EH-002 | Historical trends | Line chart data 2003–2024 | `GET /energyhub/trends` → 200, series present | ✅ | Data served from pre-computed store |
| TC-EH-003 | Forecast 2025–2030 | Forecast line + CI bands | `GET /energyhub/forecast` → 200, forecast array + intervals | ✅ | |
| TC-EH-004 | Forecast metric=consumption | Consumption forecast | 200, consumption series | ✅ | |
| TC-EH-005 | Forecast metric=peak_demand | Peak-demand forecast | 200, peak_demand series | ✅ | |
| TC-EH-006 | Choropleth map data | Province-level map points | `GET /energyhub/map-data` → 200 | ✅ | |
| TC-EH-007 | Source breakdown | Coal/gas/renewable/oil % | `GET /energyhub/source-breakdown` → 200 | ✅ | |
| TC-EH-008 | Grid breakdown | Luzon/Visayas/Mindanao split | `GET /energyhub/grid-breakdown` → 200 | ✅ | |
| TC-EH-009 | AI-generated insight | Narrative text | `GET /energyhub/ai-insight` → **mixed 200/401** — anonymous AI quota (1/day) consumed | ⚠️ | Expected behavior: quota returns 401 `"EcoSim quota reached…"` — see DEF-05 message bug |
| TC-EH-010 | Invalid forecast metric | HTTP 422 | `metric=bogus` → **200** silently returns default series | ❌ | **DEF-03** — invalid enum not rejected |

### 1.4 EcoSim Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-ES-001 | Municipality list | 1,600+ municipalities | `GET /ecosim/municipalities` → 200, **1,813 items** | ✅ | Exceeds expectation |
| TC-ES-002 | Run simulation | Dashboard w/ solar/wind/hydro | `GET /ecosim/?municipality_id=5441&…` → 200, full result incl. geothermal | ✅ | 450 ms mean |
| TC-ES-003 | Missing municipality_id | HTTP 422 | `GET /ecosim/` (no params) → **422** | ✅ | |
| TC-ES-004 | Invalid municipality_id | HTTP 404 or empty | `municipality_id=999999` → **404** `"municipality was not found"` | ✅ | Clean message, no leak |
| TC-ES-005 | Solar output calculation | Positive kWh, score 0–100 | Unit tests cover `solar_output_calc.py` (176-test suite) | ✅ | `test_solar_output_calc.py` |
| TC-ES-006 | Wind output calculation | Positive values, Betz limit | Unit-tested | ✅ | `test_wind_output_calc.py` |
| TC-ES-007 | Hydro output calculation | Positive, flow in bounds | Unit-tested | ✅ | `test_hydro_output_calc.py` |
| TC-ES-008 | Economic scoring / payback | Positive years + PHP cost | Unit-tested (`test_economic_calc.py`) + live sim returns payback fields | ✅ | |
| TC-ES-009 | Carbon reduction estimate | Positive tCO₂/yr | Returned in live simulation response | ✅ | |
| TC-ES-010 | `include_ai=true` | AI analysis panel | `GET /ecosim/ai?…` → 200 with analysis fields | ✅ | Groq-backed, 458 ms mean |
| TC-ES-011 | `use_rag=true` | Retrieved chunks incorporated | `GET /ecosim/ai?use_rag=true` → 200 | ✅ | RAG=pgvector path; dedicated chat router still disabled |
| TC-ES-012 | POST full body | HTTP 201 | `POST /ecosim/` with full `PostHouse` body → **201** | ✅ | Corrected schema: house_name, municipality, electricity_rate, bill, desired_savings |
| TC-ES-013 | POST invalid body | HTTP 422 | Partial body and `desired_savings` out-of-range → **422** | ✅ | |

### 1.5 AI Intelligence Layer

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-AI-001 | Prompt construction | Simulation data + grounding rules | Unit-tested | ✅ | `test_rag_*.py` |
| TC-AI-002 | Gemini JSON output parsing | Valid JSON w/ required fields | Unit-tested | ✅ | |
| TC-AI-003 | Gemini→Groq fallback | Groq responds on Gemini failure | Injected Gemini outage → real Groq reply in **1.68 s** | ✅ | failure_matrix TC-FR-01 |
| TC-AI-004 | RAG retrieval (valid query) | Chunks w/ score ≥ 0.25 | Unit-tested; pgvector backend live | ✅ | `RAG_BACKEND=pgvector` at startup |
| TC-AI-005 | RAG retrieval (no matches) | Empty list / low-score warning | Unit-tested | ✅ | |
| TC-AI-006 | Invalid JSON from LLM | Graceful fallback | Worker-exception path returns fallback dict | ✅ | failure_matrix TC-FR-03 |
| TC-AI-007 | Empty/failed API response | Detect + retry or fall back | Timeout → structured fallback `"AI analysis timed out"` in 61 ms | ✅ | failure_matrix TC-FR-02 |
| TC-AI-008 | Dedicated chatbot (`/api/v1/chat`, `ChatPage.jsx`) | Chat Q&A endpoint live | **Not mounted** — router commented out (`api.py:10,27`), page not routed (`AppRoutes.jsx`) | ⚠️ | **GAP**: "Chatbot/AI" rubric coverage is via EcoSim AI + EnergyHub insight + explain-chart/map endpoints only |

### 1.6 Database Layer

All 10 cases require `TEST_DATABASE_URL` against a **non-production** database. They were not run against live Supabase to avoid destructive writes.

| Test Case ID | Description | Status | Remarks |
|---|---|---|---|
| TC-DB-001 – TC-DB-010 | Insert/constraints/FK/index tests | ⏳ | 30 integration errors are exactly these `DATABASE_URL` tests. Indirect read coverage exists: live endpoints exercised regions/municipalities/climate reads via Supabase REST (see §1.7). |

### 1.7 API Endpoints

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-API-001 | Health check | 200 `{"status":"ok"}` | 200 ✓ (local + prod) | ✅ | |
| TC-API-002–005 | EnergyHub endpoints | 200 + valid JSON | All 200 | ✅ | Sweep + latency table |
| TC-API-006 | EcoSim GET valid | 200 dashboard | 200 | ✅ | |
| TC-API-007 | EcoSim GET missing params | 422 | 422 | ✅ | |
| TC-API-008 | EcoSim municipalities | 200, items>0 | 200, 1,813 items | ✅ | |
| TC-API-009 | EcoSim POST valid | 201 | 201 | ✅ | |
| TC-API-010 | EcoSim POST invalid | 422 | 422 | ✅ | |
| TC-API-011 | Response times < 2 s | All < 2 s | 22/23 under 2 s single-user; `ai-insight` hit 3.2 s p95 (LLM) | ⚠️ | See Section 2 |
| TC-API-012 | CORS headers | ACAO on allowed origin | Preflight → `ACAO: http://localhost:5173`; disallowed origin → 400 | ✅ | |
| TC-API-013 | Full sweep | All 75 checks pass | **70/75** — 5 validation findings below | ⚠️ | `artifacts/functional/endpoint_sweep.jsonl` |

**Sweep findings (executed, genuine defects):**

| ID | Endpoint / input | Expected | Actual | Severity |
|---|---|---|---|---|
| DEF-01 | `GET /geothermal/999999` | 404 | **500** (PGRST116 surfaces via global handler) | Low — clean body, wrong status semantics |
| DEF-02 | `GET /map/nuclear` (invalid type) | 4xx | **200** with error object in body | Low — contract ambiguity |
| DEF-03 | `GET /energyhub/forecast?metric=bogus` | 422 | **200** default series (silent fallback) | Low — masks bad input |
| DEF-04 | `GET /forecast/run?…` injection-style input | 4xx | 200, input ignored | Low |
| DEF-05 | `GET /products/recommend?energy_type=' OR '1'='1` | 4xx | **200**, echoes malicious string, empty results | Low — parameterized queries hold (no SQL exec), but input is echoed unvalidated |
| DEF-06 | EnergyHub AI quota error message | Feature-correct copy | Says *"Please log in to continue using **EcoSim**"* on EnergyHub | Trivial — wrong product name |

SQL-injection-style inputs (5 probe families: `' OR '1'='1`, `; DROP TABLE`, `UNION SELECT`, comment sequences, tautology strings) returned 200/404/422 with **no evidence of server-side SQL execution** — Supabase REST/PostgREST parameterization holds end-to-end. Raw evidence: `endpoint_sweep.jsonl` entries marked `inj`.

### 1.8 Visualization Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-VIZ-001–007 | Charts, map, KPI cards, AI panel render | Components render | 9/9 Vitest component tests pass | ✅ | `react-frontend` suite; production build verified (Section 2.5) |
| TC-VIZ-008–009 | Responsive 375 px/768 px | No horizontal scroll | Not executed — requires live browser viewport | ⏳ | Tailwind classes present; needs DevTools/browser pass |

### 1.9 Machine Learning Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-ML-001–008 | ARIMA/RF pipeline cases | Notebook + evaluation metrics | `GET /energyhub/model-comparison` → 200 with MAE/RMSE/MAPE per model | ⚠️ | Endpoint-level verification only; notebook re-run not in scope |
| TC-ML-009 | `/forecast/backtest` | Backtest metrics | 200 | ✅ | Sweep |
| TC-ML-010 | `/forecast/models` | Model list | 200, 82 ms mean | ✅ | |

### 1.10 Summary Statistics

| Module | Total | Passed | Failed | Pending/N-A | Notes |
|---|---|---|---|---|---|
| Authentication | 6 | 2 | 0 | 4 | OAuth + valid-token paths need credentials |
| EnergyHub | 10 | 9 | 1 | 0 | DEF-03 (metric validation) |
| EcoSim | 13 | 13 | 0 | 0 | incl. AI + POST flows |
| AI Intelligence | 8 | 7 | 0 | 1 | dedicated chatbot dormant (gap) |
| Database | 10 | 0 | 0 | 10 | `TEST_DATABASE_URL` not configured |
| API Endpoints | 13 | 11 | 2 | 0 | sweep 70/75; DEF-01/02/04/05/06 minor |
| Visualization | 9 | 7 | 0 | 2 | responsive cases need browser |
| Machine Learning | 11 | 2 | 0 | 9 | endpoint-verified; notebook cases pending |
| **Grand Total** | **80** | **51** | **3** | **26** | |

> Prior historical report (212 pass / 6 fail / 30 env-errors) is superseded by this session's improved counts: **333 total automated assertions passed** (176 + 77 + 9 + 67 + 4 extra integration passes).

### 1.11 Defect Log

| Defect ID | Test Case | Severity | Description | Status |
|---|---|---|---|---|
| DEF-01 | TC-API-013 | Low | `/geothermal/{bad_id}` → 500 instead of 404 (PGRST116 leaks to handler, sanitized body) | Open |
| DEF-02 | TC-API-013 | Low | `/map/{invalid_type}` → 200 + error body instead of 4xx | Open |
| DEF-03 | TC-EH-010 | Low | Invalid forecast `metric` silently accepted (200 default) | Open |
| DEF-04 | TC-API-013 | Low | `/forecast/run` accepts injection-style strings silently | Open |
| DEF-05 | TC-API-013 | Low | `/products/recommend` echoes unvalidated `energy_type`; parameterized queries prevent injection but no allowlist | Open |
| DEF-06 | TC-EH-009 | Trivial | AI-quota error references wrong product ("EcoSim" on EnergyHub) | Open |
| GAP-01 | TC-AI-008 | Medium | Dedicated chatbot router (`/api/v1/chat`) + `ChatPage.jsx` are code-present but not mounted/routed — live AI coverage is via EcoSim/EnergyHub endpoints | Documented |

---
## Section 2 — Performance Measurements

**Scope:** FastAPI endpoint latency, LLM latency, Supabase query time, frontend bundle weight, production cold-start smoke.
**Method:** `benchmark.py` — warm-cache, n=30 per endpoint (n=5 for LLM-backed), min/mean/p50/p95/max; direct Supabase RPC timing; `vite build` size analysis; light production smoke.

**Caveat:** Local timings include loopback overhead; absolute ms are indicative, not contractual. Cross-run CPU contention during the first pass is flagged where relevant (see Section 3).

### 2.1 API Endpoint Latency (single user, warm)

| Endpoint | n | min | mean | p50 | p95 | max | Status |
|---|---|---|---|---|---|---|---|
| `GET /health` | 30 | 1.2 | 4.8 | 1.8 | 3.6 | 84.7 | ✅ <500 ms |
| `GET /health/detailed` | 30 | 174.2 | 191.3 | 183.0 | 214.1 | 403.3 | ✅ <5 s |
| `GET /energyhub/overview` | 30 | 4.2 | 6.3 | 5.9 | 8.6 | 9.7 | ✅ <2 s |
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
| `GET /ecosim/` (simulation) | 5 | 448.2 | 450.2 | 449.5 | 454.5 | 454.5 | ✅ <3 s |
| `GET /ecosim/ai` | 5 | 444.1 | 458.0 | 451.3 | 475.9 | 475.9 | ✅ <5 s |
| `GET /energyhub/ai-insight?use_llm=true` | 5 | 42.0 | 676.8 | 44.3 | **3207.9** | 3207.9 | ⚠️ mixed 200/401 |
| `GET /energyhub/map-explanation` | 5 | 110.7 | 113.4 | 111.4 | 120.7 | 120.7 | ✅ |

All values in milliseconds. Raw: `artifacts/perf/latency.csv` (reproduced in Appendix C). The `ai-insight` p95 is inflated by one full LLM call (~3.2 s); the 401s are anonymous-quota rejections, not slowdowns.

### 2.2 LLM / AI Latency

| Path | Observation | Evidence |
|---|---|---|
| Groq (primary) | EcoSim AI response ≈ **450–476 ms** p50–p95 including Supabase reads | `latency.csv` `ecosim_ai` |
| Gemini→Groq fallback | Injected Gemini failure → Groq answered in **1,683 ms** | `failure_matrix.json` TC-FR-01 |
| AI timeout path | Hard timeout returns structured fallback in **61 ms** (`"AI analysis timed out"`) | TC-FR-02 |
| `ai-insight` cold LLM | ~3.2 s observed for the one full LLM round-trip | `latency.csv` |

The dedicated chatbot endpoint (`/api/v1/chat`) is not mounted — chatbot-latency coverage is provided by the live AI endpoints above (GAP-01).

### 2.3 Database / Supabase Query Time (direct, n=10)

| Query | mean | p50 | p95 | max | Notes |
|---|---|---|---|---|---|
| `regions` select-1 | 160.8 ms | 70.6 | 962.9 | 962.9 | p95 = cold-connection outlier; steady-state ~70 ms |
| `municipalities` select-10 | 100.7 ms | 74.0 | 317.9 | 317.9 | First-call warmup visible |
| `climate_monthly` filtered | 78.1 ms | 76.1 | 88.0 | 88.0 | Indexed lookup, tight distribution |

Raw: `artifacts/perf/db_timings.csv`. Dominant cost is TLS+network to the managed Postgres endpoint (~70 ms floor); query execution itself is sub-ms for these single-table selects.

### 2.4 Frontend Build / Load Characteristics

| Asset | Raw | Gzip | Note |
|---|---|---|---|
| `index-*.js` (main bundle) | ~6.35 MB | ~1.91 MB | Vite warns `>500 kB` — no route-level code splitting |
| `index-*.css` | ~61.4 kB | ~10.7 kB | Tailwind purged correctly |
| `index-*.js` (small chunk) | 11.46 kB | 3.68 kB | |
| `leaflet-src-*.js` | 149.99 kB | 43.55 kB | |
| `index.html` | 0.69 kB | 0.43 kB | |
| `vite build` | 1 m 17 s (2561 modules) | — | `artifacts/perf/vite-build.txt` |

First-load risk: the 1.9 MB-gz single chunk is the dominant frontend bottleneck; route-based `React.lazy` splitting is the recommended follow-up.

### 2.5 Production Smoke (light, non-destructive)

| Check | Result |
|---|---|
| `GET /api/v1/health` (prod) | 200 — cold start observed ~0.8–3.8 s across endpoints |
| `GET /docs`, `/openapi.json` (prod) | 200 — exposed (INFO finding, see Section 4) |
| Security headers (prod) | `server: Vercel`, `x-content-type-options`, `x-frame-options: DENY`, HSTS, CSP all present |
| CORS disallowed origin (prod) | Preflight → **400** blocked |

Raw production timings (`artifacts/perf/prod_smoke.txt`):

| Endpoint | Status | Latency |
|---|---|---|
| `GET /health` | 200 | 3835.4 ms |
| `GET /health/detailed` | 200 | 3095.7 ms |
| `GET /energyhub/overview` | 200 | 2280 ms |
| `GET /ecosim/municipalities` | 200 | 1133.8 ms |
| `GET /map/coverage` | 200 | 852.9 ms |

### 2.6 Existing Performance Test Suite

`fastapi-backend/tests/integration/test_performance.py` — **13/13 executed & passed**, covering response-time assertions and pagination behavior under the live app.

### 2.7 Findings

| # | Finding | Severity |
|---|---|---|
| P-01 | Single-chunk frontend bundle 1.91 MB gz — no code splitting | Medium |
| P-02 | `ai-insight` unbounded LLM latency (3.2 s p95 at n=5) | Low — quota-gated by design |
| P-03 | Supabase cold-connect spikes (p95 963 ms on `regions`) | Low — connection reuse mitigates |
| P-04 | `geothermal/{id}` lookup 222 ms mean — joins + no response cache noted | Info |

### 2.8 Limitations

- LLM samples are n=5 (quota-respecting); n=30 elsewhere.
- Production timing is smoke-level only — no load applied to Vercel (per scope).
- NASA POWER fetch latency: **N/A at runtime** — runtime climate data is served from Supabase/bundled CSVs; NASA POWER exists only in disabled ETL scripts (`api.py:16`). No timing is claimed.
- `TEST_DATABASE_URL` unavailable → direct SQL benchmark uses Supabase REST path (representative of the app's actual data path).
- `db:setup` row in `latency.csv` failed with `No module named 'app'` — a harness artifact, not a product defect.

---

## Section 3 — Load and Scalability Test Results

**Tool:** Locust 2.46.4 (headless), `artifacts/load/locustfile.py`
**Target:** Local FastAPI backend `http://127.0.0.1:8000` (single uvicorn worker)
**Constraint honored:** No load applied to production Vercel/Gemini/Groq — all load local.

### 3.1 Methodology

`locustfile.py` models a realistic mixed workload over public endpoints, weighted toward the heavier ones:

| Task | Endpoint | Weight |
|---|---|---|
| EcoSim simulation | `GET /ecosim/?municipality_id=<real>&…` | 3 |
| Municipality/province lists | `GET /ecosim/{municipalities,provinces}` | 2 |
| EnergyHub reads | `overview`, `trends`, `map-data` | 2 |
| Map/geospatial | `map/coverage`, `map/solar`, `geospatial/centroids` | 2 |
| Catalog | `geothermal/plants`, `products/browse` | 1 |

Municipality IDs are real (5441, 5415, 5145, 5050, 5892, 4919, 5354, 5131) — an earlier pass that mixed a province ID produced 404 noise and was discarded.

**Stepped profile:** 1 → 10 → 25 → 50 → 75 → 100 users, 60 s per level, hatch rate 5/s.
**Profiles:** `raw` (default), `throttled` (fixed XFF → same IP bucket), `spoof` (rotating random XFFs).

> ⚠️ First-pass u=25–u=100 ran while dependency scanners (bandit/pip-audit/npm-audit) and failure-matrix bursts competed for CPU. Levels 10/25/50/75 were re-run in a clean window (`clean_u*.csv`); u=100 uses the first-pass value (directionally consistent).

### 3.2 Results — stepped concurrency

| Users | Reqs | Fails | Avg (ms) | p50 | p95 | Max | RPS |
|---|---|---|---|---|---|---|---|
| 1 | 96 | 0 | 90 | 38 | 600 | 1,100 | 3.3 |
| 10 (clean) | 790 | 0 | 519 | 410 | 1,400 | 2,800 | 13.3 |
| 25 (clean) | 769 | 0 | 1,637 | 1,400 | ~3,300 | ~6,000 | 13.0 |
| 50 (clean) | 614 | 0 | 3,838 | 3,800 | ~7,000 | ~9,600 | 10.5 |
| 75 (clean) | 657 | 0 | 5,582 | 5,500 | ~8,700 | ~12,000 | 11.0 |
| 100 (pass-1) | 814 | 0 | 5,591 | 5,700 | ~8,900 | ~14,000 | 13.7 |

Raw per-level aggregates from `artifacts/load/runs/` are reproduced in Appendix D. HTML reports: `u{N}.html` per level.

### 3.3 Interpretation

- **Zero hard failures at every level** — no 5xx, no timeouts, no connection resets. The system degrades **gracefully** (latency inflates; every request completes).
- **Throughput plateaus at ~11–14 RPS** regardless of user count → the worker is saturated; requests queue rather than fail.
- **Latency knee between 10 and 25 users:** p95 crosses ~2 s near u=10–25 and ~3 s by u=25 — attributable to sync (non-`async def`) handlers blocking the FastAPI thread pool on sequential Supabase REST round-trips (~70–300 ms each) plus the heavier EcoSim compute.
- **Single-worker ceiling:** ~10–15 concurrent users for interactive (sub-second p95) experience; ~25 users before p95 breaches 3 s.

### 3.4 Rate-limit interaction under load

| Profile | Result |
|---|---|
| `throttled` (u=8, 45 s, fixed IP) | **429s on all probed endpoints** once the 60/min window filled — limiter works under load. Raw CSV: 1,161 requests, ~1,108 rejected (429s counted as failures by Locust — intended behavior) |
| `spoof` (u=8, 30 s, rotating XFF) | ~370–378 reqs, **0 × 429** — each spoofed IP stays under the cap; see Section 4, SEC-01 |

### 3.5 Bottleneck analysis (observed + code-correlated)

| # | Bottleneck | Evidence |
|---|---|---|
| B-01 | Single uvicorn worker + sync handlers block the thread pool on Supabase I/O | Latency curve saturates at 11–14 RPS; `app/services/*` uses sync `httpx`/`supabase` calls |
| B-02 | Per-request Supabase REST round-trips (uncached paths) | DB timings §2.3: ~70 ms floor per call |
| B-03 | EcoSim simulation compute ~450 ms serial | `latency.csv` `ecosim_simulation` |
| B-04 | CORS preflight + per-request middleware add fixed ~30–60 ms | p50 floor under no contention |
| B-05 | **No CORS/504/Gemini-timeout cascade observed** — quota gates (1/day anon) cap LLM spend before timeouts matter | ai-insight 401s, not timeouts |

No 504s occurred locally; Vercel serverless has its own function-duration limit (would surface as 504 under sustained load — untested by design).

### 3.6 Breaking point

| Threshold | Level reached |
|---|---|
| p95 < 1 s | ~10 users |
| p95 < 3 s | ~25 users |
| Hard failures (>1 % error) | **Not reached** at u=100 — graceful degradation |

**Recommended ceiling (this hardware/deployment):** ~10 concurrent interactive users per single worker; horizontal scale-out (multiple uvicorn workers / Vercel concurrency) required beyond that. In-memory rate-limit + quota counters are **per-process**, so effective limits multiply per worker/instance — see Section 4, SEC-01.

### 3.7 Reproduction

```
python -m locust -f docs/09-Technical-Evaluation/artifacts/load/locustfile.py \
  --headless -u 25 -r 5 -t 60s \
  --csv docs/09-Technical-Evaluation/artifacts/load/runs/u25 \
  --host http://127.0.0.1:8000 --only-summary

# Rate-limit profiles
LUMI_LOAD_PROFILE=throttled python -m locust ... -u 8 -t 45s
LUMI_LOAD_PROFILE=spoof     python -m locust ... -u 8 -t 30s
```

### 3.8 Limitations

- Localhost loopback removes WAN latency — absolute numbers are optimistic vs. real clients.
- u=100 retained from the contaminated first pass; a clean re-run is queued but direction is clear (plateau + graceful degradation).
- Production (Vercel serverless) scaling behavior not load-tested — cold-start smoke only (0.8–3.8 s).
- Anonymous-quota 401s appear in traces where AI endpoints were exercised — counted as failures by Locust but are **intended** behavior.

---

## Section 4 — Security Test Results and Logs

**Scope:** AuthN/AuthZ, injection, CORS, headers, secrets handling, dependency CVEs, rate-limit/quota enforcement.
**Tools:** Bandit 1.9.4, pip-audit 2.10.1, npm audit, `security_probes.py`, targeted live probes.
**Constraint honored:** No destructive DB writes; no credential brute-forcing; probes read-only or self-cancelling.

### 4.1 Methodology

1. **Static analysis:** `bandit -r fastapi-backend/app` + `pip-audit` (env) + `npm audit` (frontend).
2. **Live probes** (`security_probes.py`): JWT matrix, security headers, CORS preflight, docs exposure, error-body leakage.
3. **Targeted live tests:** XFF rate-limit bypass (LAN socket), rate-limit split-counter behavior, SQL-injection-style inputs via the endpoint sweep.
4. **Code audit:** auth deps, rate-limit/quota middleware, env handling, admin endpoints, ETL string interpolation.
5. **Secrets review:** `git ls-files` for tracked env/key files; `.env` names scanned for `VITE_`-prefixed secrets.

Raw artifacts: `artifacts/security/` (`bandit-app.txt`, `pip-audit-env.txt`, `npm-audit-frontend.json`, `probes.json`, `prod_smoke.txt`) — see Appendix E.

### 4.2 Confirmed Vulnerabilities

#### SEC-01 — `X-Forwarded-For` trusted unconditionally → rate-limit & quota bypass — **HIGH**

`app/middleware/rate_limit.py:43-52` and `app/dependencies/quota.py` take the *leftmost* `X-Forwarded-For` as the client IP with no trusted-proxy validation. `_is_localhost()` then exempts loopback values.

**Live proof** (LAN socket 192.168.254.160 → `0.0.0.0:8001`, non-loopback client):

| Burst | Result |
|---|---|
| No XFF, 75 req | `60 × 200` then `15 × 429` — limiter enforced |
| `X-Forwarded-For: 127.0.0.1`, 75 req | `75 × 200`, **0 × 429** — bypassed |

Same code path exempts the **anonymous EcoSim AI quota** (1/day) and the stricter auth-endpoint limit (10/min). On Vercel, `x-vercel-forwarded-for`/platform headers should be preferred; trusting raw XFF is only safe behind a proxy that overwrites it.

#### SEC-02 — Rate limiter fails open under intermittent Redis failure (split counters) — **MEDIUM**

`_is_allowed_redis` counts in the Redis ZSET; on exception it falls back to a **separate** in-memory dict (`_is_allowed_memory`). Under a flapping Redis, each request lands in exactly one counter — the two are never merged. Observed live: 70-request burst during "Event loop is closed" churn → **0 × 429** because counts split ~35/35, neither reaching 60. Worst case ≈ 2× effective limit; in multi-worker/serverless deployments the in-memory counter is per-process anyway (limits multiply per instance — architectural caveat, not a bug).

#### SEC-03 — `_get_user_status` fails open on DB outage — **MEDIUM**

`app/dependencies/auth.py:223-228`: if the `profiles.is_active` lookup throws, the dependency returns `True` (allow). A suspended user retains access during a Supabase outage. `_get_user_role` (line 200) correctly fails *closed* to `"user"` — posture is inconsistent; status check should match.

#### SEC-04 — Dependency CVEs in the backend env — **MEDIUM**

`pip-audit`: **87 known vulnerabilities across 15 packages** (`artifacts/security/pip-audit-env.txt`). Runtime-relevant:

| Package | Version | Advisory | Fix | Reachability |
|---|---|---|---|---|
| `python-jose` | 3.3.0 | PYSEC-2024-232/233 (alg-confusion / DoS in JWT verify), PYSEC-2025-185 | 3.4.0 | **Direct** — JWT verify path |
| `starlette` | 0.38.6 | 8 advisories (incl. PYSEC-2026-1941/1943, multipart DoS family) | ≥0.40.0 / 1.x | **Direct** — every request |
| `cryptography` | 49.0.0 | PYSEC-2026-3552 | 50.0.0 | Transitive (TLS/JWT) |
| `ecdsa` | 0.19.2 | PYSEC-2026-1325 (Minerva timing) | none yet | JWT alg support |
| `python-dotenv` | 1.0.1 | PYSEC-2026-2270 | 1.2.2 | Startup only |
| `pillow`, `transformers`, `torch`, `tornado`, `mistune`, `pip`, `setuptools`, `h2`, `pyasn1`, `ujson` | various | 60+ advisories | — | Mostly non-runtime or dev/ML |

Full package-by-advisory listing in Appendix E.2.

#### SEC-05 — `VITE_`-prefixed secret names in root `.env` — **MEDIUM (latent)**

Root `.env` contains `VITE_SUPABASE_SERVICE_ROLE_KEY` and `VITE_SUPABASE_JWT_SECRET`. No frontend source references them today, but **any `VITE_*` var is inlined into the client bundle** if ever imported — service-role key exposure would defeat RLS entirely. Rename to unprefixed names (backend-only) or move to `fastapi-backend/.env`.

#### SEC-06 — `admin create-user` returns `temp_password` in the response body — **LOW**

`app/routes/admin.py:202-209` includes the generated password in JSON. Admin-only + HTTPS mitigates, but credentials should be delivered via a one-time link or server-side email, not an API response that intermediaries/logs may capture.

#### SEC-07 — ML-worker 503 leaks raw exception text — **LOW**

`app/services/ml_worker_proxy.py:79-80`: `{"detail": "ML worker unavailable: {exc}"}` — exception strings can embed internal hostnames/URLs. Verified live: `POST /api/v1/chat` → 503 `"All connection attempts failed"`. Return a generic message + request_id.

#### SEC-08 — `etl.py` table-name interpolation — **LOW**

Table identifiers interpolated into SQL strings (code-verified; ETL router disabled — `api.py:16`). Not reachable at runtime; fix before re-enabling ETL.

#### SEC-09 — Bandit: MD5 for cache keys, `0.0.0.0` strings, `try/except/pass` — **LOW/INFO**

`bandit-app.txt`: **4 High / 3 Medium / 13 Low** across 17,006 lines scanned. Triaged: the MD5 hits (`ecosim.py` ~958/963, `energyhub.py` ~1277) hash non-secret cache keys — **not password storage**, acceptable but migrate to `sha256` for hygiene. `0.0.0.0` strings are in `_is_localhost` helpers (not socket binds). `try/except/pass` in `settings.py` masks config errors. Most `assert` hits are test helpers.

#### SEC-10 — `server: uvicorn` banner + docs exposure — **INFO**

`server` header discloses the ASGI server; `/docs`, `/openapi.json`, `/redoc` return 200 in **production** (verified). Acceptable for a public API but worth an intentional decision.

### 4.3 Verified Controls (executed, passing)

| Control | Evidence |
|---|---|
| No token → 401 on all protected/admin routes | probes SEC-AUTH-01, ADM×3 |
| Malformed / `alg:none` / wrong-signature JWT → 401 | SEC-AUTH-02/03/04 |
| Expired JWT (real secret) → 401 | SEC-AUTH-05 |
| Validly-signed JWT for nonexistent user → 401 (server-side `auth.get_user` check) | SEC-AUTH-06 |
| Security headers 5/5 (XCTO, XFO, HSTS, CSP, Referrer-Policy) local + prod | SEC-HDR-01, `prod_smoke.txt` |
| CORS allowlist + `lumi-frontend-*.vercel.app` regex; disallowed origin → 400 | SEC-CORS-* local + prod |
| SQL-injection-style inputs → 200/404/422, no SQL execution | sweep `inj` rows |
| 500 body sanitized (`{"detail":"Server error…","request_id"}` — no stack/path leak) | SEC-ERR-01 |
| Body >1 MB → 413; malformed JSON → 422 | failure_matrix TC-FR-10 |
| Rate limit works when Redis healthy (60/min → 429) & on NullRedis in-memory fallback (exactly 60→429) | §4.2 live tests |
| `.env` not tracked in git; only `*.env.example` committed | `git ls-files` |
| Local-JWT optional path (`get_verified_user_optional`) trusts signature without re-checking user existence — only usable if `SUPABASE_JWT_SECRET` already leaked | code read, `auth.py:132-167` |

**Live probe results (`artifacts/security/probes.json`):** 18 probes executed — 16 PASS, 1 WARN (server banner), 3 INFO (docs exposure). Detail in Appendix E.4.

### 4.4 Frontend dependency audit

`npm audit`: **7 vulnerabilities** — 1 critical (`vitest` via `@vitest/mocker`, dev-only), 1 high (`vite` path-traversal, dev-only), 5 moderate incl. **`react-router`/`react-router-dom` open-redirect & XSS advisories (CVE-2025-68470 family — runtime-shipped)** and `esbuild` dev-server request forgery. Recommendation: bump `react-router-dom` (fix available, non-major); vitest/vite require major upgrades. Detail in Appendix E.3.

### 4.5 Supabase / RLS posture

- Backend uses **service-role key** (bypasses RLS) for all server-side reads — correct pattern for a trusted backend; means RLS is *not* the access-control layer for API consumers (the FastAPI auth deps are).
- Anon/publishable key is hardcoded in `react-frontend/src/utils/env.js` — acceptable *by design* for the publishable key, provided RLS is enabled on user-facing tables (frontend never talks to tables directly in current code — all data flows through the backend).
- RLS policies themselves were not probed (requires authenticated Supabase session) — **[OPEN]**.

### 4.6 Findings Register

| ID | Severity | Status |
|---|---|---|
| SEC-01 XFF bypass | **High** | Confirmed live — fix: trust `x-vercel-forwarded-for` / real socket IP behind platform |
| SEC-02 split-counter fail-open | Medium | Confirmed — merge counters or prefer-Redis-then-stampede |
| SEC-03 status check fail-open | Medium | Confirmed — fail closed like `_get_user_role` |
| SEC-04 dependency CVEs | Medium | pip/npm audit artifacts; priority: `python-jose`, `starlette`, `react-router-dom` |
| SEC-05 `VITE_` secret names | Medium (latent) | Rename/move |
| SEC-06 temp_password in response | Low | Design change |
| SEC-07 503 leaks exception text | Low | Generic message |
| SEC-08 etl.py SQL identifiers | Low (unreachable) | Parameterize before re-enable |
| SEC-09 bandit triage | Low/Info | MD5→sha256 hygiene |
| SEC-10 banner + docs exposure | Info | Decision needed |

### 4.7 Limitations

- No authenticated-session testing (no test credentials) — admin/user role paths probed only unauthenticated.
- RLS policies not exercised directly.
- No TLS/cert testing (localhost) — prod HSTS verified.
- Pen-test depth is bounded: no fuzzing, no session-fixation or CSRF cross-site tests beyond CORS preflight.

---

## Section 5 — System Architecture Documentation

**Basis:** Codebase audit + live runtime inspection (OpenAPI: 70 mounted endpoints across 12 routers).

> Note: this section is written in prose and tables so it can be pasted directly into a word processor. The original Mermaid source diagrams are preserved in `docs/09-Technical-Evaluation/system-architecture.md`.

### 5.1 Overview

LUMI is a three-tier system: a **React/Vite SPA** (Vercel), a **FastAPI backend** deployable as a long-running server *or* a Vercel serverless function, and managed services — **Supabase** (Postgres + Auth + pgvector RAG) and **Upstash Redis** (cache, rate limiting, quotas). AI features are served by **Groq** (primary) and **Gemini** (fallback-capable), with an optional external **ML worker** for heavy endpoints.

### 5.2 Deployment Topology (text form)

| Tier | Component | Role |
|---|---|---|
| Client | React 18 + Vite + Tailwind SPA (Vercel static hosting) | Browser UI |
| Edge | `api/index.py` Vercel serverless function — `_PathFix` mount-normalizer + optional `MLWorkerProxy` | Production API entry |
| Server | `uvicorn → main:app` (single worker observed) | Long-running deployment (local / Docker / any host) |
| Managed | Supabase (Postgres · Auth · pgvector, eu-west) | Primary datastore + auth |
| Managed | Upstash Redis | Cache · rate-limit · quota |
| External | Groq API | Primary LLM |
| External | Gemini API | Fallback LLM |
| External | Optional ML worker (Render/Fly/DO) | `/api/v1/chat`, `/api/v1/etl` (disabled) |
| Bundled | Climate / geo CSVs in-repo | Supabase outage fallback |

**Request flow:** SPA → `HTTPS /api/v1/*` (apiClient: 30 s timeout, 3× retry) → Vercel serverless function → Supabase, Upstash, Groq, Gemini (+ ML worker if `ML_WORKER_URL` set). In dev, the SPA talks to uvicorn directly via dev proxy. Both the serverless function and uvicorn read bundled CSV fallbacks.

**Dual-mode backend:** `api/index.py` (serverless wrapper) sets `RAG_BACKEND=pgvector`, `LLM_PROVIDER=groq`, `EMBEDDING_PROVIDER=huggingface-inference` as env defaults, wraps `main.app` in `_PathFix` (strips `/api/index[.py]` mount prefix, clears `root_path`), and conditionally adds `MLWorkerProxyMiddleware` when `ML_WORKER_URL` is set. The same `main:app` runs under uvicorn elsewhere.

### 5.3 Request Pipeline — middleware order (outermost → innermost, `main.py:56-70`)

| Order | Middleware | Behavior |
|---|---|---|
| 1 | `TimingMiddleware` | Duration logging |
| 2 | `CORSMiddleware` | Allowlist + `lumi-frontend-*.vercel.app` regex |
| 3 | `BodySizeLimitMiddleware` | >1 MB → 413 |
| 4 | `SecurityHeadersMiddleware` | XCTO / XFO / HSTS / CSP / Referrer-Policy |
| 5 | `RateLimitMiddleware` | 60/min · 10/min auth-actions · Redis + memory |
| 6 | `RequestIDMiddleware` | UUID per request |
| 7 | Routers (12) → services → Supabase/Redis/LLM | Application layer |

### 5.4 Component & Data Flow (text form)

**Routers mounted under `/api/v1`:**

| Router | Endpoints |
|---|---|
| `health` | `/health`, `/detailed` |
| `ecosim` | `GET/POST /`, `/ai`, `/municipalities`, `/provinces`, `/barangays` |
| `energyhub` | `overview`, `forecast`, `trends`, `map-data`, `ai-insight`, `explain-*`, `irena/*`, `model-comparison`, `provincial-demand`, `meralco-rate`, `solar-atlas`, `analyze-chart` |
| `geothermal` | `/plants`, `/{id}`, `/ecosim/geothermal`, `/ecohub/geothermal-summary` |
| `geospatial` | `/centroids`, `/climate`, `/climate/hierarchy`, `/climate/province-aggregate` |
| `map` | `/psgc/hierarchy`, `/coverage`, `/{solar,wind,hydro,geothermal}` |
| `products` | `/recommend`, `/browse`, `/audit` |
| `forecast` | `/run`, `/backtest`, `/models` |
| `simulations` | (auth) |
| `admin` | (auth) `/users`, `/analytics`, `/config`, `/usage`, `/logs` |
| `protected` | (auth) `/me`, `/profile` |
| `auth` | OAuth callbacks |
| `chat` / `etl` / `example` | **DISABLED** (`api.py:10,16,27,33`) |

**Service layer wiring:**

| Service module | Used by | Depends on |
|---|---|---|
| `ecosim.py` (climatic suitability + output calcs) | ecosim router | `supabase_service`, `data_cache`, CSV fallback |
| `gemini_funcs.py` (worker timeout + persistent cache + structured fallback) | ecosim, energyhub | `llm_client` |
| `llm_client.py` (provider select) | `gemini_funcs` | Groq or Gemini (falls back to Groq on Gemini failure) |
| `groq_client.py` | `llm_client` | Groq API |
| `rag_pipeline.py` | AI features | pgvector (prod) via `supabase_service`; FAISS present but index not built |
| `supabase_service.py` (singleton client, service-role, REST fallback for non-JWT keys) | most services | Supabase Postgres |
| `redis_client.py` (NullRedis no-op fallback) | cache/rate-limit/quota | Upstash Redis + in-memory fallback |
| `data_cache.py` | ecosim, energyhub | Redis |

### 5.5 Authentication Sequence (text form)

1. User (SPA) sends `Bearer <supabase JWT>` to FastAPI.
2. On **required** paths, FastAPI calls `Supabase Auth → auth.get_user(token)`; error → 401.
3. FastAPI then reads `user_roles.role` and `profiles.is_active` from Supabase DB using the service-role key.
4. Role is cached in Redis for 300 s; active-status for 60 s (`lumi:auth:*` keys).
5. FastAPI returns 200 + claims `{sub, email, role, plan}`.
6. On **optional-auth read paths**, the JWT is verified **locally** with `SUPABASE_JWT_SECRET` (no Supabase round-trip), then cached role/status are checked.

Observed behavior: `get_current_user`/`get_verified_user` verify via `auth.get_user` (server-side). `get_verified_user_optional` uses local JWT verify (`_get_local_user`) → cached role/status — used on read-only paths.

### 5.6 Frontend

| Aspect | Implementation |
|---|---|
| Framework | React 18 + Vite + Tailwind; React Router (hash paths) |
| API client | `apiClient.js` — `fetch` + 30 s `AbortController` timeout, ≤3 retries, 500 ms exponential backoff, retries 5xx only (429 respected), `X-Request-Id` |
| Supabase | `supabaseClient` — publishable anon key (fallback hardcoded in `env.js`) |
| API base | dev: `/api/v1` (proxy); prod fallback: `https://lumi-backend-ten.vercel.app` |
| **Gap** | `ChatPage.jsx` exists but is **not in `AppRoutes.jsx`**; `apiClient` chat methods target the disabled `/api/v1/chat` router |

### 5.7 Disabled / Dormant Surface

| Component | State |
|---|---|
| `/api/v1/chat` router | Commented out — `api.py:10,27` (heavy RAG chat deferred) |
| `/api/v1/etl` router | Commented out — `api.py:16,33` (long-running) |
| `/api/v1/example` items router | Commented out |
| `ChatPage.jsx` frontend route | Not registered in `AppRoutes.jsx` |
| FAISS RAG backend | Code present; startup uses `pgvector` — FAISS index not built |
| NASA POWER ingestion | ETL-script only; **not called at runtime** |

### 5.8 Failure Boundaries (verified — see Section 6)

| Dependency fails → | Behavior |
|---|---|
| Supabase | `/health/detailed` → `degraded`; EcoSim falls back to CSV then clean 404 |
| Redis | NullRedis no-op cache; in-memory rate-limit/quota fallback |
| Groq + Gemini | EcoSim AI → structured fallback dict; endpoint still 200 |
| Gemini only | Automatic Groq fallback (verified live, 1.68 s) |
| ML worker | 503 for proxied paths only; rest of API unaffected |
| Oversized body / bad JSON | 413 / 422 before routing |

---

## Section 6 — Failure and Recovery Test Results

**Method:** `failure_matrix.py` — controlled failure injection via TestClient + singleton/mocking (no `.env` tampering; `settings.py:15` uses `load_dotenv(override=True)` so env-based injection is unreliable — in-process patching was used instead).
**Raw artifact:** `artifacts/failure/failure_matrix.json` (17 scenarios) — reproduced in Appendix F.

**Verdict legend:** GRACEFUL (degraded but correct response) · DEGRADED (works but wrong semantics) · FAIL · N/A · BYPASS-CONFIRMED (security-relevant behavior)

### 6.1 Results Matrix

| ID | Failure injected | Observed behavior | Verdict |
|---|---|---|---|
| TC-FR-01 | Gemini outage (all models raise) | Automatic fallback to **live Groq** — response produced in 1,683 ms; log: `"All Gemini models failed; falling back to Groq emergency path"` | GRACEFUL |
| TC-FR-02 | EcoSim AI worker exceeds hard timeout (`_AI_CALL_TIMEOUT` → 50 ms) | Returns structured fallback dict `error:"AI analysis timed out"` in **61 ms** — no hang | GRACEFUL |
| TC-FR-03 | All LLM providers down (worker raises) | `analyze_renewable_results` returns fallback dict — endpoint remains functional | GRACEFUL |
| TC-FR-04a | Supabase client broken → `/health/detailed` | `status=degraded`, `supabase=error`, still HTTP 200 | GRACEFUL |
| TC-FR-04b | Supabase down → `/ecosim/municipalities` | **200** — served from bundled CSV fallback (1,813 items still returned) | GRACEFUL |
| TC-FR-04c | Supabase down → `/ecosim/` simulation | **404** `"The selected municipality was not found"` — clean, no crash | GRACEFUL |
| TC-FR-04d | Supabase down → `/protected/me` (no token) | **401** `"Missing token"` — auth fails before DB dependency | GRACEFUL |
| TC-FR-05 | Redis client → NullRedis | `/health/detailed`: `redis=not_configured`; `/map/solar` → **200** (cache-miss path) | GRACEFUL |
| TC-FR-06 | NASA POWER outage at runtime | **N/A** — runtime climate is served from Supabase + bundled CSVs; NASA POWER exists only in disabled ETL scripts (`api.py:16`) | N/A |
| TC-FR-07a | `municipality_id=999999` → `/ecosim/` | **404** clean message | GRACEFUL |
| TC-FR-07b | `municipality_id=999999` → `/geothermal/{id}` | **500** — global handler returns sanitized body `{detail, request_id}` but PGRST116 should map to 404 | DEGRADED |
| TC-FR-08 | ML worker URL dead (`127.0.0.1:59999`) → `POST /api/v1/chat` | **503** `{"detail":"ML worker unavailable: All connection attempts failed"}`; non-proxied paths unaffected (health 200) | GRACEFUL (⚠ leaks raw exception text — SEC-07) |
| TC-FR-09a | 70-req burst, public XFF, Redis loop-broken | 0×429 — **split counters**: ~35 reqs went to Redis path, ~35 to in-memory fallback; neither reached the 60 cap | FAIL-OPEN (see SEC-02) |
| TC-FR-09b | 70-req burst, `X-Forwarded-For: 127.0.0.1` | 0×429 — limiter bypassed (proven from LAN socket: 75×200 vs 60+15×429 without XFF) | BYPASS-CONFIRMED (SEC-01) |
| TC-FR-09c | NullRedis + public XFF, 75-req burst | Exactly `60×200, 15×429` — in-memory fallback **correct** when Redis returns NullRedis cleanly | GRACEFUL |
| TC-FR-09d | Throwing Redis (`pipeline()` raises) | Exactly `60×200, 15×429` — exception→memory path **correct** for a hard failure | GRACEFUL |
| TC-FR-10a | POST body >1 MB | **413** `"Request body too large. Maximum size is 1 MB."` | GRACEFUL |
| TC-FR-10b | Malformed JSON body | **422** `json_invalid` | GRACEFUL |
| TC-FR-10c | Non-integer path param | **422** `int_parsing` | GRACEFUL |

### 6.2 Verified Resilience Mechanisms (code-level)

| Mechanism | Location | Behavior |
|---|---|---|
| Global exception handler | `main.py` + `app/middleware/` | Sanitized `{detail, request_id}` — no stack/path leak (verified TC-FR-07b body) |
| Request IDs | `RequestIDMiddleware` | UUID per request, echoed in logs + error bodies |
| LLM provider fallback | `llm_client.py` | Gemini → Groq when `GROQ_API_KEY` set |
| LLM hard timeout + persistent cache | `gemini_funcs.py:601-647` | Worker-thread timeout → fallback dict; results cached by content key |
| Supabase→CSV fallback | `ecosim.py:79-115` | Climate/municipality data falls back to bundled CSVs; 404 only if both empty |
| Redis NullRedis | `redis_client.py` | All cache helpers try/except → no-op |
| Rate-limit memory fallback | `rate_limit.py:54-63` | Works for clean NullRedis & hard exceptions; **not** merged with Redis counter (SEC-02) |
| Quota in-memory fallback | `dependencies/quota.py` | Anonymous quota works without Redis (per-process) |
| Frontend retry/timeout | `apiClient.js:5-7,58-95` | 30 s timeout, 3 retries, 500 ms exp backoff, no retry on 429 |
| ML-worker proxy isolation | `ml_worker_proxy.py:68-83` | 55 s timeout → 503; other routes unaffected |
| Health degradation | `health.py` | `degraded` status + per-check detail |

### 6.3 Crash / Fail-Open Findings

| Finding | Severity | Detail |
|---|---|---|
| Rate-limit split-counter fail-open | Medium | Intermittent Redis → ~2× effective limit (FR-09a). Multi-instance deployments multiply the in-memory limit per process |
| `_get_user_status` fails open | Medium | Suspended users pass during a `profiles` outage (`auth.py:223-228`); `_get_user_role` fails closed — inconsistent |
| `/geothermal/{bad_id}` → 500 | Low | Sanitized body, wrong status semantics (DEF-01) |

### 6.4 Proposed / Not-Executed Scenarios

| Scenario | Status | Reason |
|---|---|---|
| Production Vercel function timeout (504) under cold-start | [OPEN] | Not load-tested against prod per scope constraint |
| Supabase **Auth** outage with a valid cached JWT | [OPEN] | Requires a real user token; `get_verified_user` would 401 (no local fallback on required paths — arguably correct) |
| pgvector outage during RAG queries | [OPEN] | Would need targeted mock of the vector client; expected behavior mirrors Supabase outage |
| Groq **and** Gemini real-API outage (network-level) | Partially covered | FR-03 simulated both raising; live network partition untested |
| Redis **permanent** outage under sustained load | Covered in part | NullRedis path verified; split-counter edge case found instead |

### 6.5 Recommendations

1. **Merge rate-limit counters** (or prefer Redis and count failures toward the window) — closes the SEC-02 fail-open gap.
2. **Fail closed in `_get_user_status`** to match `_get_user_role`.
3. **Map PGRST116 → 404** in `geothermal` (and audit for other `.single()` callers).
4. **Generic 503 body** in `ml_worker_proxy` — move exception text to logs keyed by `request_id`.
5. **Structured "degraded" responses**: endpoints that lose Supabase currently return 404 — a 503 with `Retry-After` would distinguish "not found" from "dependency down".
6. **Surface fallback state to the client**: EcoSim AI fallback returns 200 with `error` inside the payload — a `X-Degraded: true` header would let the UI show honest state.

---

## Section 7 — ML Model and Calibration Results

This section consolidates the machine-learning / model-validation evidence: the EnergyHub forecasting pilot run, the theoretical model feasibility study, the LLM evaluation framework, and the EcoSim calibration campaigns.

### 7.1 Forecasting Model Benchmarks (empirical — DOE 2003–2024)

**Dataset & protocol:** Philippine DOE Statistical Bulletin 2003–2024. Target: total national electricity consumption (`consumption_gwh`). Train: 2003–2020 (n=18). Test: 2021–2024 (n=4, held out). Source: `docs/ML_MODEL_EVALUATION_SUMMARY.md`; metrics in `DOE_Data_Extracted/model_comparison_results.csv`, registered in Supabase `ml_model_registry` and served live by `GET /energyhub/model-comparison`.

> Forecasting outputs a continuous number — classification metrics (accuracy, recall, F1) are a category error here. Metrics used: MAE, RMSE, MAPE, R², AIC/BIC, Directional Accuracy, PICP.

**Performance leaderboard:**

| Rank | Model | MAE (GWh) | RMSE (GWh) | MAPE (%) |
|---|---|---:|---:|---:|
| 1 | **Linear Trend Regression** | 5,993.83 | 7,342.10 | **4.97** |
| 2 | Holt Linear Smoothing | 6,557.72 | 7,997.68 | 5.44 |
| 3 | Naive with Drift | 6,709.32 | 8,128.45 | 5.57 |
| 4 | ARIMA(1,1,1) | 6,829.09 | 8,257.12 | 5.67 |
| 5 | SARIMAX(1,1,1) + Exogenous | 9,913.65 | 11,459.11 | 8.28 |
| 6 | Random Forest Regression | 15,957.41 | 17,806.29 | 13.41 |

**Model-by-model findings:**

| Model | Result | Why it performed that way |
|---|---|---|
| Linear Trend Regression | Best MAE/MAPE | PH consumption 2003–2020 is almost perfectly linear (+~3,190 GWh/yr); simplest model avoids overfitting on n=18. |
| Holt Linear Smoothing | MAPE 5.44 % | Trend is stable enough that extra adaptivity adds no meaningful gain. |
| Naive with Drift | MAPE 5.57 % | Accuracy floor — any real model must beat "keep going in the same direction". |
| ARIMA(1,1,1) | MAPE 5.67 % — **deployed** | Provides 95 % prediction intervals, statistically defensible, robust to future trend change. Chosen over Linear Trend despite +0.7 pp MAPE. |
| SARIMAX + Exogenous | MAPE 8.28 % | Extra regressors on n=18 → curse of dimensionality; overfit. |
| Random Forest | MAPE 13.41 % | Controlled experiment — training MAPE 1.45 % vs test 13.41 % (−11.95 pp gap): textbook overfitting on 18 points. Empirically justifies parsimonious statistical models over advanced ML. |

**Theoretically evaluated (feasibility study, not trained):**

| Model | Suitability | Expected MAPE | Rationale |
|---|---|---|---|
| LSTM | LOW | — | Needs hundreds–thousands of time steps; only 84 monthly steps/municipality; ~300–400 MB framework. |
| Prophet | MEDIUM | 7–12 % | Good for seasonality/missing data; Stan backend ~100 MB; one model per municipality = maintenance overhead. |
| XGBoost / LightGBM | **HIGH (Phase 2 rec.)** | 5–10 % | SOTA on tabular; single global model across municipalities; <20 MB serialized, <100 MB RAM, sub-ms inference. |
| Temporal Fusion Transformer | OVERKILL | — | Needs 100K+ samples + PyTorch; impractical on free-tier hosting. |
| Naive / ETS | BASELINE | — | Floor reference; deployed model must beat it. |

### 7.2 LLM / Generative AI Evaluation

The AI layer integrates **Google Gemini 2.5 Flash** (primary) and **Groq-hosted Llama 3** (fallback). Generative models produce free-form language and structured JSON, so traditional classification metrics are inapplicable.

**Evaluation dimensions & targets** (from `llm_evaluation_methodology.md`):

| Dimension | Type | Target | Measurement |
|---|---|---|---|
| Response Latency | Intrinsic | <2,000 ms (Gemini); <500 ms (Groq) | `time.perf_counter()` |
| Token Usage | Intrinsic | <6,000 tokens/query | API `usage_metadata` |
| Cost Efficiency | Intrinsic | <$0.005/query (Gemini) | Token count × provider rate |
| JSON Validity Rate | Intrinsic | ≥95 % | `json.loads()` success rate |
| Schema Compliance | Intrinsic | ≥90 % | Required field presence |
| Hallucination Rate | Extrinsic | <10 % | Manual annotation (n=50) |
| Faithfulness | Extrinsic | ≥4.0/5 | Likert rubric (grounding to RAG context) |
| Relevance | Extrinsic | ≥4.0/5 | Likert rubric |
| Grounding Citation Rate | Extrinsic | ≥70 % | Regex match for source citations |
| BLEU / ROUGE | Reference | 0.3–0.5 | N-gram overlap vs reference |
| Human Correctness | Human | ≥4.0/5 | Expert panel (n=4 raters) |
| Inter-Rater Kappa | Human | κ ≥ 0.60 | Cohen's Kappa |

**Measured live behavior (Sept 5 session):** Groq primary path ≈ 450–476 ms p50–p95 (Section 2.2); Gemini→Groq fallback verified live at 1,683 ms (TC-FR-01); timeout fallback at 61 ms (TC-FR-02); JSON parsing/normalization unit-tested (`test_ai_service.py`).

**Gemini vs Groq comparative summary:**

| Dimension | Gemini 2.5 Flash | Groq (Llama 3) |
|---|---|---|
| Latency | Moderate (occasional 503 overload) | Fast (Groq inference engine) |
| Cost | Lower ($0.15/M input tokens) | Higher ($0.59/M input tokens) |
| RAG Grounding | Strong | Moderate |
| JSON Compliance | High | Moderate |
| Fallback Reliability | Primary; sometimes overloaded | Fallback; highly available |
| Context Window | 1M tokens | 128K tokens |
| Philippine Knowledge | Moderate | Lower |

**RAG retrieval smoke evidence** (`retrieval_test_output.txt`, `gemini_mock_test.txt`): top-k retrieval returns correctly-typed knowledge chunks (scores 0.49–0.78) across cost/component/capacity categories; prompts assembled with strict grounding rules (~4.4–4.6 K chars). Samples in Appendix G.

### 7.3 EcoSim Physics-Based Models (deterministic)

EcoSim's solar/wind/hydro/geothermal calculators are physics-based, not trained ML. Rationale: no ground-truth sensor data, interpretability for LGU planners, zero training cost, immediate deployability.

| Energy Source | Model Type | Key Inputs |
|---|---|---|
| Solar | Physics-based regression | Irradiance, temperature, panel efficiency, degradation, dust loss |
| Wind | Physics-based regression | Wind speed, rotor radius, power coefficient, air density, capacity factor |
| Hydro | Physics-based regression | Elevation, slope, hydraulic head, runoff coefficient, flow rate |
| Geothermal | Suitability scoring + thermal power formula | Heat flow, fault distance, volcano distance, aquifer properties, thermal conductivity |

### 7.4 Calibration Campaign Results (province & municipality level)

**Calibration goal (v5, branch `development3`, 2026-09-02):** replace the unbounded cubic wind model with a household-scale power curve, raise micro-hydro output in high-feasibility catchments, and produce a balanced recommendation distribution without source bias.

Key model settings (v5): household turbine `rated_power_kw=1.2`, `cut_in=3.0 m/s`, `rated=11.0 m/s`, `cut_out=25.0 m/s`, `rotor_radius=6.2 m`, `capacity_factor=0.22`, `cp=0.239`; micro-hydro `head_factor=0.50`, `design_flow_factor=0.80`, `max_head=30 m`, `turbine_eff=0.85`, `gen_eff=0.95`, `catchment_fraction=0.002`, `catchment_cap=2.0 km²`; hydro plant output floor `15.0 kWh per √MW`, capped at 150 kWh, absolute cap 250 kWh.

**Comprehensive calibration — all provinces & municipalities** (`calibration_all_report.md`):

| Level | Tested | Solar rec. | Wind rec. | Hydro rec. | Bias check |
|---|---|---|---|---|---|
| Province | 78 | 46 (59.0 %) | 32 (41.0 %) | 0 | OK — no source >80 % |
| Municipality | 1,287 | 748 (58.1 %) | 539 (41.9 %) | 0 | OK — max 58.1 % |

- Score–output correlation: solar r=1.000/0.992, wind r=0.941/0.703, hydro r=1.000 (province/municipality).
- Hydro enrichment used for 100 % of rows; hydro >5 kWh in 14/78 provinces (17.9 %) and 170/1,287 municipalities (13.2 %).
- Gen-vs-suitability recommendation agreement: 84.6 % (province), 85.6 % (municipality).

**Province-mode full run, 2026-09-01** (`province_test_all_report_2026-09-01.md`): 120 provinces in table → **84 successful, 36 failed (404)** — failures are highly-urbanized cities (City of Manila, Quezon City, etc.), renamed provinces (Davao de Oro, Davao del Norte, Cotabato), and special geographic areas lacking climate/average rows. Output ranges: Solar 124.9–154.5 kWh/mo (mean 138.0); Wind 13.2–439.5 (mean 140.4 — still unbounded pre-v5); Hydro 0.0–40.4 (mean 3.6).

**Post-recalibration run, 2026-09-02** (`province_test_all_report_2026-09-02_recal.md`): same 84/36 split; recommendations now **Solar 46 (54.8 %), Wind 35 (41.7 %), Hydropower 3 (3.6 %)**. Hydro wins appear only where Boothroyd catchment enrichment supports realistic household micro-hydro (Agusan del Norte 194.2, Benguet 165.9, Kalinga 151.5 kWh/mo). Wind cap edge cases: Batanes, Catanduanes, Camarines Sur, Antique, Cavite hit the 190.1 kWh/mo rated-power cap. Backend focused tests: 57 passed incl. 5 new power-curve tests; frontend build passed.

**Nine target provinces (v5):** Bulacan → Hydropower (150.0), Camarines Sur → Wind (190.1), Leyte → Wind (150.9), Eastern Samar → Solar (134.6), Cavite → Wind (190.1), Laguna → Wind (137.5), Batangas → Solar (144.7), Rizal → Solar (139.7), Quezon → Solar (137.9). Split: 5 Solar / 4 Wind / 0 Hydro — no single source dominates.

**Wikipedia plant recalibration (v5, 2026-09-03)** (`PLANT_RECAL_REPORT_2026-09-02.md`): wind plants cataloged 10 (6 operating, 408 MW, 5 provinces); hydro plants 17 (all operating, 1,235.92 MW, 13 provinces). Hydro floor flips provinces with large operating plants (Bulacan/Angat 218 MW, Isabela/Magat 360 MW, Lanao del Sur/Agus 1 80 MW) where base household catchment output was low. Hydro remains the minority recommendation (~10 % of successful provinces). Caveat: Wikipedia list is explicitly incomplete — supplementary evidence only.

**Earlier calibration rounds:** `calibration_report.md` (27 provinces — Wind-biased 66.7 %, pre-v5 baseline), `calibration_municipality_report.md` (17 municipalities with per-row scores, catchments, feasibility).

**Explanation consistency:** `explanation_mismatch_report.md` — **0 mismatches** between computed outputs and generated explanations. `regenerate_explanations_report.md` — 20/20 municipality explanations regenerated, 0 errors, 16.8 s.

---

## Section 8 — Known Gaps and Limitations (aggregated)

| # | Gap / Limitation | Where evidenced |
|---|---|---|
| 1 | Dedicated chatbot (`/api/v1/chat` + `ChatPage.jsx`) code-present but not mounted — live AI coverage via EcoSim AI + EnergyHub only | §1.5 GAP-01, §5.7 |
| 2 | `TEST_DATABASE_URL` not configured → 30 DB-layer tests pending (kept off production by design) | §1.6 |
| 3 | OAuth / valid-token / authenticated-session flows not exercised (no test credentials) | §1.2, §4.7 |
| 4 | RLS policies not probed directly (requires authenticated Supabase session) | §4.5 |
| 5 | Production load testing deliberately excluded — smoke-level only (cold start 0.8–3.8 s observed) | §2.5, §3.8 |
| 6 | NASA POWER not part of runtime behavior — N/A, not measured | §2.8, TC-FR-06 |
| 7 | LLM latency samples n=5 (quota-respecting); n=30 elsewhere | §2.8 |
| 8 | Responsive-viewport tests (375 px/768 px) not executed — need live browser pass | §1.8 |
| 9 | 36/120 province records fail lookup (404) — data-source naming gaps for highly-urbanized cities & renamed provinces | §7.4 |
| 10 | Single-chunk frontend bundle 1.91 MB gz — no code splitting (recommended follow-up) | §2.4, P-01 |
| 11 | u=100 load level retained from CPU-contaminated first pass — direction consistent but not clean | §3.8 |
| 12 | SEC-01 XFF bypass + SEC-02/03 fail-open findings are open fixes | §4.6 |
| 13 | Notebook-level ML re-runs not in scope — endpoint-level verification only | §1.9 |
| 14 | June historical run had 6 failures (scoring normalization, 307 health redirect, forecast `year` KeyError, PGRST116) — all resolved or re-characterized in the Sept 5 pass | Appendix G |

---

## Appendices — Raw Logs and Evidence Artifacts

All paths are relative to the repository root. Small artifacts are reproduced in full or near-full; large artifacts are excerpted with the file path given for the complete record.

### Appendix A — Automated Test Suite Logs (September 5, 2026)

**A.1 `lumi_tests/` unit suite** — `docs/09-Technical-Evaluation/artifacts/functional/pytest-lumi-unit.txt`

```
====================== 176 passed, 9 warnings in 34.39s =======================
```

**A.2 `fastapi-backend/tests/`** — `artifacts/functional/pytest-backend.txt`

```
======================= 77 passed, 3 warnings in 6.47s ========================
```

**A.3 `fastapi-backend/tests/integration/`** — `artifacts/functional/pytest-lumi-integration.txt`

```
============ 67 passed, 2 skipped, 3 warnings, 30 errors in 12.52s ============
```

All 30 errors are `RuntimeError: TEST_DATABASE_URL or DATABASE_URL environment variable required` at the `db_conn` fixture — the complete list of the 30 erroring tests (schema existence, CRUD for regions/provinces/municipalities/climate/hydropower, FK integrity, regional lookup view, null constraints, data types) is in the artifact file.

**A.4 `react-frontend` Vitest** — `artifacts/functional/vitest-frontend.txt`

```
 ✓ src/__tests__/theme-contrast.test.js (3 tests) 8ms
 ✓ src/components/__tests__/DashboardChart.test.jsx (2 tests) 50ms
 ✓ src/__tests__/I18nProvider.test.jsx (4 tests) 136ms

 Test Files  3 passed (3)
      Tests  9 passed (9)
   Duration  21.82s
```

### Appendix B — Endpoint Sweep Results (75 checks, 70 PASS / 5 FAIL)

Full machine-readable records: `artifacts/functional/endpoint_sweep.csv` (19 KB) and `endpoint_sweep.jsonl` (28 KB). Complete check list:

| # | ID | Method | Path | Expected | Got | Verdict |
|---|---|---|---|---|---|---|
| 1 | TC-API-001 | GET | `/health` | 200 ok | 200 (20.8 ms) | PASS |
| 2 | TC-API-001b | GET | `/health/detailed` | 200 dep checks | 200 (288.8 ms) | PASS |
| 3 | TC-ES-001 | GET | `/ecosim/municipalities` | 200, items>0 | 200 (45.2 ms) | PASS |
| 4 | TC-ES-001b | GET | `/ecosim/provinces` | 200, items>0 | 200 (36.2 ms) | PASS |
| 5 | TC-ES-001c | GET | `/ecosim/barangays` | 200 list | 200 (44.3 ms) | PASS |
| 6 | TC-ES-002 | GET | `/ecosim/` | 200 dashboard | 200 (770.1 ms) | PASS |
| 7 | TC-ES-003 | GET | `/ecosim/` | 422 missing params | 422 (5.5 ms) | PASS |
| 8 | TC-ES-004 | GET | `/ecosim/` | 404 invalid municipality | 404 (112.2 ms) | PASS |
| 9 | TC-ES-004b | GET | `/ecosim/` | 422 negative id | 422 (5.1 ms) | PASS |
| 10 | TC-ES-010 | GET | `/ecosim/ai` | 200 AI/fallback | 200 (902.7 ms) | PASS |
| 11 | TC-ES-011 | GET | `/ecosim/` (RAG) | 200 | 200 (849.2 ms) | PASS |
| 12 | TC-ES-012 | POST | `/ecosim/` | 200/201 | 201 (380.0 ms) | PASS |
| 13 | TC-ES-012b | POST | `/ecosim/` | 422 out-of-range | 422 (3.5 ms) | PASS |
| 14 | TC-ES-013 | POST | `/ecosim/` | 422 invalid body | 422 (4.5 ms) | PASS |
| 15 | TC-EH-001 | GET | `/energyhub/overview` | 200 | 200 (5.2 ms) | PASS |
| 16 | TC-EH-002 | GET | `/energyhub/trends` | 200 | 200 (8.7 ms) | PASS |
| 17 | TC-EH-004 | GET | `/energyhub/forecast` | 200 consumption | 200 (3.0 ms) | PASS |
| 18 | TC-EH-005 | GET | `/energyhub/forecast` | 200 peak_demand | 200 (5.2 ms) | PASS |
| 19 | TC-EH-006 | GET | `/energyhub/map-data` | 200 | 200 (40.6 ms) | PASS |
| 20 | TC-EH-007 | GET | `/energyhub/source-breakdown` | 200 | 200 (2.4 ms) | PASS |
| 21 | TC-EH-008 | GET | `/energyhub/grid-breakdown` | 200 | 200 (2.0 ms) | PASS |
| 22 | TC-EH-009 | GET | `/energyhub/ai-insight` | 200 | 200 (5.3 ms) | PASS |
| 23 | TC-EH-010 | GET | `/energyhub/forecast?metric=bogus` | 4xx | **200** (2.3 ms) | **FAIL** (DEF-03) |
| 24 | TC-EH-011 | GET | `/energyhub/model-comparison` | 200 | 200 (3.2 ms) | PASS |
| 25 | TC-EH-012 | GET | `/energyhub/provincial-demand` | 200 | 200 (3.8 ms) | PASS |
| 26 | TC-EH-013 | GET | `/energyhub/municipal-demand/327` | 200 | 200 (158.2 ms) | PASS |
| 27 | TC-EH-014 | GET | `/energyhub/irena/overview` | 200 | 200 (7.2 ms) | PASS |
| 28 | TC-EH-015 | GET | `/energyhub/irena/capacity` | 200 | 200 (5.4 ms) | PASS |
| 29 | TC-EH-016 | GET | `/energyhub/irena/generation` | 200 | 200 (6.0 ms) | PASS |
| 30 | TC-EH-017 | GET | `/energyhub/irena/renewable-share` | 200 | 200 (2.9 ms) | PASS |
| 31 | TC-EH-018 | GET | `/energyhub/meralco-rate` | 200 | 200 (2.3 ms) | PASS |
| 32 | TC-EH-019 | GET | `/energyhub/solar-atlas` | 200/4xx | 200 (3.6 ms) | PASS |
| 33 | TC-EH-020 | GET | `/energyhub/map-explanation` | 200 | 200 (115.5 ms) | PASS |
| 34 | TC-EH-021 | POST | `/energyhub/analyze-chart` | 200/503 | 200 (78.9 ms) | PASS |
| 35 | TC-GEO-001 | GET | `/geothermal/plants` | 200 | 200 (2.2 ms) | PASS |
| 36 | TC-GEO-002 | GET | `/geothermal/5441` | 200 | 200 (258.9 ms) | PASS |
| 37 | TC-GEO-003 | GET | `/geothermal/ecosim/geothermal` | 200 | 200 (155.5 ms) | PASS |
| 38 | TC-GEO-004 | GET | `/geothermal/ecohub/geothermal-summary` | 200 | 200 (336.3 ms) | PASS |
| 39 | TC-GEO-005 | GET | `/geothermal/999999` | 404 | **500** (97.1 ms) | **FAIL** (DEF-01) |
| 40 | TC-GS-001 | GET | `/geospatial/centroids` | 200 | 200 (39.9 ms) | PASS |
| 41 | TC-GS-002 | GET | `/geospatial/centroids/municipality/5441` | 200 | 200 (37.0 ms) | PASS |
| 42 | TC-GS-003 | GET | `/geospatial/climate` | 200 | 200 (41.7 ms) | PASS |
| 43 | TC-GS-004 | GET | `/geospatial/climate/hierarchy` | 200 | 200 (44.7 ms) | PASS |
| 44 | TC-GS-005 | GET | `/geospatial/climate/province-aggregate` | 200 | 200 (39.2 ms) | PASS |
| 45 | TC-GS-006 | GET | `/geospatial/climate` (no geo_id) | 422 | 422 (1.8 ms) | PASS |
| 46 | TC-MAP-001 | GET | `/map/psgc/hierarchy` | 200 | 200 (36.4 ms) | PASS |
| 47 | TC-MAP-002 | GET | `/map/coverage` | 200 | 200 (35.9 ms) | PASS |
| 48 | TC-MAP-003-solar | GET | `/map/solar` | 200 | 200 (82.7 ms) | PASS |
| 49 | TC-MAP-003-wind | GET | `/map/wind` | 200 | 200 (97.3 ms) | PASS |
| 50 | TC-MAP-003-hydro | GET | `/map/hydro` | 200 | 200 (43.5 ms) | PASS |
| 51 | TC-MAP-003-geothermal | GET | `/map/geothermal` | 200 | 200 (45.6 ms) | PASS |
| 52 | TC-MAP-004 | GET | `/map/nuclear` | 4xx invalid type | **200** (2.8 ms) | **FAIL** (DEF-02) |
| 53 | TC-PROD-001 | GET | `/products/recommend` | 200 | 200 (6.6 ms) | PASS |
| 54 | TC-PROD-002 | GET | `/products/browse` | 200 | 200 (3.4 ms) | PASS |
| 55 | TC-PROD-003 | GET | `/products/audit` | 200 | 200 (5.2 ms) | PASS |
| 56 | TC-PROD-004 | GET | `/products/recommend` (no type) | 422 | 422 (2.1 ms) | PASS |
| 57 | TC-FC-001 | GET | `/forecast/run` | 200 | 200 (276.3 ms) | PASS |
| 58 | TC-FC-002 | GET | `/forecast/backtest` | 200 | 200 (234.8 ms) | PASS |
| 59 | TC-FC-003 | GET | `/forecast/models` | 200 | 200 (80.6 ms) | PASS |
| 60 | TC-AUTH-003 | GET | `/protected/me` | 401 no token | 401 (2.2 ms) | PASS |
| 61 | TC-AUTH-003b | GET | `/protected/me` | 401 bad token | 401 (464.2 ms) | PASS |
| 62 | TC-AUTH-004 | GET | `/protected/profile` | 401 no token | 401 (4.9 ms) | PASS |
| 63 | TC-AUTH-007 | GET | `/simulations` | 401 no token | 401 (3.2 ms) | PASS |
| 64 | TC-AUTH-007b | POST | `/simulations` | 401 no token | 401 (6.0 ms) | PASS |
| 65 | TC-AUTH-008 | GET | `/simulations/{uuid}` | 401 no token | 401 (2.2 ms) | PASS |
| 66 | TC-ADM-001 | GET | `/admin/users` | 401/403 | 401 (2.5 ms) | PASS |
| 67 | TC-ADM-001b | GET | `/admin/users` (bad token) | 401/403 | 401 (137.1 ms) | PASS |
| 68 | TC-ADM-002 | GET | `/admin/analytics` | 401/403 | 401 (2.2 ms) | PASS |
| 69 | TC-ADM-003 | GET | `/admin/config` | 401/403 | 401 (2.8 ms) | PASS |
| 70 | TC-ADM-004 | GET | `/admin/usage` | 401/403 | 401 (4.7 ms) | PASS |
| 71 | TC-ADM-005 | GET | `/admin/logs` | 401/403 | 401 (1.8 ms) | PASS |
| 72 | TC-SEC-INJ-01 | GET | `/ecosim/` (injection params) | 4xx | 422 (2.7 ms) | PASS |
| 73 | TC-SEC-INJ-02 | GET | `/energyhub/forecast` (injection) | 4xx | **200** (2.9 ms) | **FAIL** (DEF-04) |
| 74 | TC-SEC-INJ-03 | GET | `/geospatial/centroids/../../etc/passwd/1` | 4xx traversal | 404 (1.8 ms) | PASS |
| 75 | TC-SEC-INJ-04 | GET | `/products/recommend` (`' OR '1'='1`) | 4xx | **200** (5.9 ms) | **FAIL** (DEF-05) |

### Appendix C — Performance Raw Data

**C.1 Endpoint latency** — `artifacts/perf/latency.csv` is fully tabulated in §2.1 (columns: endpoint, method, path, params, n, min_ms, mean_ms, p50_ms, p95_ms, max_ms, statuses, all_2xx, threshold_ms, within_threshold, errors). One harness row (`db:setup`) failed with `No module named 'app'` — script artifact, not a product defect.

**C.2 Supabase direct timings** — `artifacts/perf/db_timings.csv` (full):

| Query | n | min | mean | p50 | p95 | max | Status |
|---|---|---|---|---|---|---|---|
| `regions` select-1 | 10 | 68.5 | 160.8 | 70.6 | 962.9 | 962.9 | ok |
| `municipalities` select-10 | 10 | 69.5 | 100.7 | 74.0 | 317.9 | 317.9 | ok |
| `climate_monthly` filtered | 10 | 69.9 | 78.1 | 76.1 | 88.0 | 88.0 | ok |

**C.3 Frontend build** — `artifacts/perf/vite-build.txt`:

```
vite v5.4.21 building for production...
✓ 2561 modules transformed.
dist/index.html                     0.69 kB │ gzip:   0.43 kB
dist/assets/index-BNs3tU1I.css     61.40 kB │ gzip:  10.68 kB
dist/assets/index-Bbw5gU5o.js      11.46 kB │ gzip:   3.68 kB
dist/assets/leaflet-src-oBiBh4GO.js 149.99 kB │ gzip:  43.55 kB
dist/assets/index-Cdjg2hsO.js   6,354.84 kB │ gzip: 1,907.84 kB
✓ built in 1m 17s
(!) Some chunks are larger than 500 kB after minification.
```

**C.4 Production smoke** — `artifacts/perf/prod_smoke.txt` (full): see §2.5 table. Prod base URL: `https://lumi-backend-ten.vercel.app/api/v1`.

### Appendix D — Load-Test Raw Aggregates (`artifacts/load/runs/*_stats.csv`, "Aggregated" rows)

| Run | Reqs | Fails | Median ms | Avg ms | Min ms | Max ms | RPS | p95 |
|---|---|---|---|---|---|---|---|---|
| u1 | 96 | 0 | 37 | 90.4 | 2.1 | 1,052 | 3.29 | 600 |
| u10 (pass-1) | 756 | 0 | 370 | 533.3 | 5.2 | 3,511 | 12.96 | 1,700 |
| clean_u10 | 790 | 0 | 410 | 519.2 | 2.2 | 2,842 | 13.32 | 1,400 |
| u25 (pass-1) | 765 | 0 | 1,600 | 1,632.1 | 3.6 | 4,196 | 12.87 | 3,200 |
| clean_u25 | 769 | 0 | 1,400 | 1,637.0 | 78.9 | 5,963 | 13.00 | 3,300 |
| u50 (pass-1) | 660 | 0 | 3,700 | 3,649.8 | 59.3 | 9,079 | 11.32 | 6,800 |
| clean_u50 | 610 | 0 | 3,800 | 3,818.9 | 8.7 | 9,632 | 10.45 | 6,900 |
| u75 (pass-1) | 700 | 0 | 5,100 | 5,176.5 | 1,518.2 | 11,018 | 11.81 | 7,700 |
| clean_u75 | 651 | 0 | 5,500 | 5,600.6 | 2,076.5 | 12,210 | 11.03 | 8,700 |
| u100 (pass-1) | 814 | 0 | 5,700 | 5,590.8 | 462.2 | 13,627 | 13.70 | 8,900 |
| throttled_u8 | 1,161 | 1,108* | 36 | 69.0 | 34.3 | 4,898 | 26.26 | 48 |
| spoof_u8 | 367 | 0 | 120 | 387.8 | 2.2 | 2,122 | 12.70 | 1,400 |

\* throttled "failures" are 429 rate-limit rejections — intended behavior once the 60/min window filled (≈95 % of requests rejected).

Per-endpoint detail, per-second history (`*_stats_history.csv`, ~11 KB each), exceptions/failures CSVs, and HTML reports (`u{N}.html`, ~960 KB each) are in `artifacts/load/runs/`. Workload definition: `artifacts/load/locustfile.py`.

### Appendix E — Security Scan Raw Outputs

**E.1 Bandit** — `artifacts/security/bandit-app.txt`: `bandit -r fastapi-backend/app`, run 2026-09-05, 17,006 LOC scanned → **4 High / 3 Medium / 13 Low** (confidence: 18 High, 2 Medium). Notable entries:

| Rule | Severity | Location | Triage |
|---|---|---|---|
| B324 MD5 hash | High | `ecosim.py:958`, `ecosim.py:963`, `energyhub.py:1277` (+1) | Non-secret cache keys — not credential hashing; migrate to sha256 for hygiene |
| B104 `0.0.0.0` string | Medium | `quota.py:22`, `rate_limit.py:24` | Loopback-whitelist literals, not socket binds |
| B110 try/except/pass | Low | `settings.py:220` | Masks config parse errors |
| B112 try/except/continue | Low | `energyhub.py:786` | JSON parse loop skip |
| B101 assert used | Low | `app/services/test_rag_normalize.py` and similar | Test helpers, not production logic |

**E.2 pip-audit** — `artifacts/security/pip-audit-env.txt` (full summary): **87 known vulnerabilities in 15 packages**.

| Package | Version | # Advisories | Fix version(s) |
|---|---|---|---|
| cryptography | 49.0.0 | 1 | 50.0.0 |
| ecdsa | 0.19.2 | 1 | none |
| h2 | 4.3.0 | 1 | 4.4.1 |
| mistune | 3.2.1 | 11 | 3.3.0 |
| pillow | 11.3.0 | 22 | 12.1.1–12.3.0 |
| pip | 24.3.1 | 7 | 25.3–26.2 |
| pyasn1 | 0.6.3 | 4 | 0.6.4 |
| python-dotenv | 1.0.1 | 1 | 1.2.2 |
| python-jose | 3.3.0 | 5 | 3.4.0 (PYSEC-2025-185 unfixed) |
| setuptools | 81.0.0 | 2 | 83.0.0 |
| starlette | 0.38.6 | 9 | 0.40.0–1.3.1 |
| torch | 2.12.0 | 1 | 2.13.0 |
| tornado | 6.5.7 | 3 | 6.5.8 |
| transformers | 4.57.6 | 6 | 5.0.0–5.10.0 (2 unfixed) |
| ujson | 5.12.1 | 2 | 5.13.0 |

**E.3 npm audit (frontend)** — `artifacts/security/npm-audit-frontend.json`: 7 vulnerabilities — 1 critical (`vitest` via `@vitest/mocker`, dev-only), 1 high (`vite` path-traversal, dev-only), 5 moderate (`react-router`/`react-router-dom` open-redirect & SSR-hydration constructor injection, CVE-2025-68470 family — **runtime-shipped**; `esbuild` dev-server request forgery GHSA-67mh-4wv8-2f99). Fix: `react-router-dom` non-major bump available; vite/vitest need major upgrades.

**E.4 Live probe results** — `artifacts/security/probes.json` (18 probes):

| ID | Check | Observed | Verdict |
|---|---|---|---|
| SEC-AUTH-01 | No token → `/protected/me` | HTTP 401 `Missing token` | PASS |
| SEC-AUTH-02 | Malformed token | HTTP 401 `Invalid token` | PASS |
| SEC-AUTH-03 | `alg:none` JWT | HTTP 401 | PASS |
| SEC-AUTH-04 | Wrong-signature JWT | HTTP 401 | PASS |
| SEC-AUTH-05 | Expired JWT (real secret) | HTTP 401 | PASS |
| SEC-AUTH-06 | Locally-minted JWT, nonexistent user | HTTP 401 | PASS |
| SEC-AUTH-ADM ×3 | Bad token → `/admin/users`, `/admin/analytics`, `/admin/config` | HTTP 401 each | PASS |
| SEC-HDR-01 | Security headers | 5/5 present (XCTO nosniff, XFO DENY, HSTS 31536000+includeSubDomains, CSP, Referrer-Policy) | PASS |
| SEC-HDR-02 | Server banner | `server='uvicorn'` | WARN |
| SEC-CORS-allowed | Preflight `localhost:5173` | 200 + ACAO echo | PASS |
| SEC-CORS-regex | Preflight `lumi-frontend-abc.vercel.app` | 200 + ACAO echo | PASS |
| SEC-CORS-disallowed | Preflight `evil.example.com` | **400**, no ACAO | PASS |
| SEC-DOCS ×3 | `/docs`, `/openapi.json`, `/redoc` | 200 each | INFO |
| SEC-ERR-01 | 500 body leak check (`/geothermal/999999`) | Sanitized `{detail, request_id}` — no leak | PASS |

**E.5 Production security smoke** — `artifacts/security/prod_smoke.txt`: `/api/v1/health`, `/docs`, `/openapi.json` all 200 with `server=Vercel` + full security-header set; `OPTIONS` from disallowed origin → 400.

### Appendix F — Failure-Injection Raw Evidence

`artifacts/failure/failure_matrix.json` — 17 scenarios, all rendered in the §6.1 matrix. Representative raw records:

```
TC-FR-01  Gemini outage → Groq fallback          observed: "Fallback produced text in 1683ms"   verdict: GRACEFUL
TC-FR-02  EcoSim AI timeout → fallback dict      observed: "Returned 'AI analysis timed out' in 61ms"  verdict: GRACEFUL
TC-FR-04a Supabase down → /health/detailed       observed: {"status":"degraded","checks":{"supabase":"error","redis":"ok","rag_index":"not_loaded"}}
TC-FR-07b bad id → /geothermal/{id}              observed: HTTP 500 {"detail":"Server error. Please try again or contact support.","request_id":"321ecf90-…"}  verdict: DEGRADED
TC-FR-09a 70-req burst, Redis loop-broken        observed: "429s=0/70 (limit=60/min)"  codes={200:70}  verdict: FAIL
TC-FR-09b 70-req burst, XFF=127.0.0.1            observed: "429s=0/70 - limiter bypassed"  verdict: BYPASS-CONFIRMED
TC-FR-10a POST body >1MB                          observed: HTTP 413 "Request body too large. Maximum size is 1 MB."  verdict: GRACEFUL
```

Note: the JSON records TC-FR-08 as `FAIL` with "Cannot add middleware after an application has started" (harness limitation) — the equivalent scenario was verified live via a dead `ML_WORKER_URL` producing the isolated 503 reported in §6.1.

### Appendix G — Historical June 2026 Run + Retrieval/LLM Smoke Logs

**G.1 `lumi_tests` full-suite run (June 14–20, 2026 — superseded by §1.1 counts)** — `lumi_tests/test_results/lumi_test_results.txt` + `lumi_tests/reports/test_results_report.md`:

| Metric | Count |
|---|---|
| Total collected | 248 |
| Passed | 212 |
| Failed | 6 |
| Errors | 30 (all `TEST_DATABASE_URL`-dependent) |
| Warnings | 4 |
| Duration | ~26 s |
| Pass rate (excl. env errors) | 212/218 = **97.2 %** |

The 6 June failures and their resolution status:

| June failure | Root cause | Sept 5 status |
|---|---|---|
| `test_solar_scenario`, `test_wind_scale` (`_calculate_option_summary` score >1.0) | Score normalization expectation | Resolved — 176/176 unit pass |
| `test_health_check_live`, `test_health_endpoint_response_time` | 307 redirect vs 200 | Resolved — `/health` → 200 verified in sweep + benchmark |
| `test_forecast_metric_param` (`KeyError: 'year'`) | Predictor DataFrame column | Resolved — forecast endpoints 200 in sweep |
| `test_post_ecosim_invalid_municipality` (PGRST116) | Empty `.single()` result | Resolved for `/ecosim/` (clean 404); same pattern still open for `/geothermal/{id}` → DEF-01 |

Additional June-era unit log `lumi_tests/test_results/unit_test_results.txt`: `87 passed, 2 skipped in 1.75s` (earlier, narrower suite — since expanded to 176).

**G.2 RAG retrieval smoke** — `retrieval_test_output.txt` (excerpt): queries like "Which renewable source is cheaper?" return top-k knowledge chunks with cosine scores 0.49–0.78 from correct categories (`all/comparison`, `solar/equipment_cost`, `hydro/components`, `wind/components`, …).

**G.3 Prompt-assembly mock** — `gemini_mock_test.txt` (excerpt): two scenarios ("Solar budget", "Hydro equipment") each retrieve 5 chunks (top scores 0.67–0.76) and assemble a ~4.4–4.6 K-char prompt enforcing the strict grounding rules (cost figures must come from retrieved knowledge; JSON output schema enforced).

**G.4 Integration log** — `test_output.txt` (root): contains the June integration pass/fail detail matching G.1 (6 failed, 212 passed, 30 errors in 25.99 s).

### Appendix H — Related Methodology & Evaluation Documents (index)

These are evaluation frameworks/protocols (criteria and process, not raw results) kept in `lumi_tests/docs/`:

| File | Contents |
|---|---|
| `iso25010_evaluation.md` | ISO/IEC 25010 quality evaluation — weighted score **3.60/5.0 "Good"** (Functional Suitability 4, Performance 4, Reliability 4, Security 4; Compatibility 3, Usability 3, Maintainability 3, Portability 3) |
| `testing_methodology_report.md` | Test methodology (24.9 KB) |
| `testing_strategy.md` | Testing strategy (11.1 KB) |
| `test_results_template.md` | Test-case template used by §1 tables (12.5 KB) |
| `ml_evaluation_framework.md` | Metric selection, statistical tests, Random Forest controlled experiment (19.7 KB) |
| `llm_evaluation_methodology.md` | Gemini/Groq evaluation dimensions (17.1 KB) |
| `lumi_metrics_and_models_for_everyone.md` | Plain-language metrics explainer (19.2 KB) |
| `algorithms.md` | Algorithm notes (6.2 KB) |
| `usability_testing.md` | Usability evaluation protocol — task-based, 4 user profiles ×10 participants (11.5 KB; **plan only — sessions not yet executed**) |
| `supabase_schema_additions.sql` | Schema additions for test support (8.4 KB) |

Other related result docs in `docs/04-ML-Data-Science/`: `LUMI_ML_MODEL_ANALYSIS.md` (feasibility study), `LUMI_METHODOLOGY_ML.md`, `ML_LIBRARIES_ALGORITHMS_DATA.md`, `CATCHMENT_ENRICHMENT.md`, `DOE_datacleaning_EXPLAINED.md`, `LUMI_FORECASTING_DATA_SOURCES.md`; raw CSV/JSON alongside each report (`calibration_all_results.csv`, `province_test_all_results_*.json`, `PLANT_RECAL_ALL_120_*.json`).

Reproduction scripts: `docs/09-Technical-Evaluation/artifacts/scripts/` — `endpoint_sweep.py`, `benchmark.py`, `failure_matrix.py`, `security_probes.py`; `lumi_tests/run_tests_and_save.py`; `lumi_tests/pilot_run/evaluate_models.py`.

---

*End of consolidated technical evaluation results. Source documents remain authoritative; this file is a copy-paste convenience compilation generated 2026-09-06.*
