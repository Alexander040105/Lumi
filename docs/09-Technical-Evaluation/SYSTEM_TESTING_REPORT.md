# COMPREHENSIVE SOFTWARE TECHNICAL TESTING REPORT

**Title:** LUMI — Data-Driven Environmental Intelligence System
**Group Name:** LUMI Development Team
**Technical Evaluators (IT Experts):** Automated evidence collection executed in-repository by Devin; human expert review/sign-off pending (see §23)

---

## 1. Document Information

| Item | Details |
|---|---|
| **Project/System Name** | LUMI |
| **Project Title** | LUMI — Data-Driven Environmental Intelligence System (renewable-energy simulation, national energy analytics, and AI-assisted recommendations for Philippine municipalities) |
| **Version** | 0.1.0 (`package.json`, root and `react-frontend`) |
| **Testing Date** | 2026-09-15 (fresh re-execution); historical baseline September 5–8, 2026, clearly labeled where cited |
| **Testing Environment** | Windows 11 Pro for Workstations (build 26200) · Intel Core i5-8400 @ 2.80 GHz · ~8 GB RAM · 480 GB SSD · Python 3.13.2 venv · Node.js v24.15.0 · live Supabase project + live Groq/Gemini keys via `.env` (keys not exposed) |
| **Tested By** | Devin (automated/agentic test execution) |
| **Developer/Development Team** | LUMI Development Team |
| **Test Report Version** | 1.0 — replaces/supplements `TECHNICAL_EVALUATION_ALL_RESULTS.md` |
| **Status** | ☒ Final (with explicitly marked not-executable items; human sign-off pending) |

---

## 2. Executive Summary

### 2.1 Purpose of Testing
Per the worksheet: this report presents the procedures, test cases, results, identified defects, corrective actions, and overall assessment of the LUMI software system, conducted to determine whether it meets functional, technical, performance, security, usability, compatibility, and reliability requirements.

### 2.2 Testing Objectives
All nine objectives were addressed; **Objective 8 (defects corrected and retested)** was verified live for the six previously-logged defects, and **Objective 9 (deployment readiness)** is answered in §21 with an honest "not yet" due to unresolved dependency vulnerabilities.

### 2.3 Headline Results (all freshly executed 2026-09-15)

| Activity | Result |
|---|---|
| Backend pytest (`fastapi-backend/tests`) | **104 passed / 2 failed** (both are test-infrastructure failures — missing async plugin, not product defects) |
| Unit suite (`tests/tests/unit`) | **177 passed / 0 failed** |
| Integration suite (`tests/tests/integration`) | **66 passed / 1 failed** (health endpoint 555 ms > 500 ms threshold while suites ran concurrently; standalone re-time: mean 10.9 ms — a load-contention artifact, not a defect) / 32 skipped |
| Frontend Vitest | **13 passed / 0 failed** (4 files) |
| Endpoint sweep | **79 PASS / 3 FAIL** of 82 checks — the 3 failures are `/forecast/*` now returning 401: a deliberate auth-hardening change that made the sweep's "public 200" expectations stale (§8, §17 BUG-06) |
| Security probes | **16/16 PASS**; rate-limit XFF-spoof fix verified live (70/70 → 429) |
| Read-only Supabase checks | 14/14 expected results; RLS correctly denies anon access to user tables |
| Locust 25-user load | 1,155 requests, **0 failures**, mean 2,202 ms — but ~2 s avg latency confirms prior finding that ~10 concurrent interactive users is the practical single-worker ceiling |
| Dependency audits | **REGRESSION vs Sept claims:** pip-audit found **66 known vulnerabilities in 6 backend packages**; npm audit found **4 frontend vulnerabilities (2 critical)** — Sept documentation claimed both were clean |
| Bandit SAST | **0 issues** across 16,960 scanned lines |
| Production build | Vite build succeeds; **6.42 MB main JS chunk (1.93 MB gzip)** — bundle-bloat warning |

---

## 3. System Overview

### 3.1 System Description

**System Name:** LUMI

**Description:** A full-stack web system providing (a) **EcoSim** — a household renewable-energy simulator producing per-municipality solar/wind/hydro/geothermal viability and cost estimates; (b) **EnergyHub** — a national energy dashboard with DOE statistics, ARIMA-based consumption/peak/renewable forecasts, and IRENA analytics; (c) **geospatial map services** over PSGC hierarchy, climate, and renewable-suitability layers; (d) a **generative-AI recommendation layer** (Groq primary, Gemini fallback) producing per-simulation narrative analysis; and (e) **authenticated user features** — saved simulations, profile, MFA, chat, and an admin console (user management, analytics, config, audit logs). Stack: FastAPI + Uvicorn backend, Supabase (PostgreSQL + Auth + RLS), Upstash Redis cache/rate-limit, React 18 + Vite + Tailwind/shadcn + Leaflet frontend.

### 3.2 Intended Users

| User Type | Description | Access Level |
|---|---|---|
| Administrator | Manages users (create/ban/role/reset/delete), views analytics, edits config, audits chat sessions | Full — `/admin/*` routes, admin role check |
| Registered user (analogous to template's "Faculty/Staff" / "Student/User") | Runs EcoSim simulations, saves/loads simulations, uses AI insights, forecasts, chat, profile/MFA | Authenticated — `/protected/*`, `/forecast/*`, `/simulations`, `/ecosim` POST, `/chat` |
| Guest / anonymous | Public dashboards: EnergyHub analytics, map layers, geothermal/plant data, product browse/recommend | Public GET endpoints |

### 3.3 Major System Modules (as they actually exist in `fastapi-backend/app/routes/`)

| No. | Module/Feature | Description |
|---|---|---|
| 1 | User Authentication & Account (`protected.py`, Supabase Auth) | JWT-verified profile/me endpoints, avatar sync, session, account deletion; MFA via Supabase |
| 2 | EcoSim (`ecosim.py`) | Household simulation GET (dashboard) + POST (persist), municipalities/provinces/barangays pickers, `/ecosim/ai` narrative analysis |
| 3 | EnergyHub (`energyhub.py`) | Overview, forecast, trends, map-data, source/grid breakdowns, model comparison, provincial/municipal demand, IRENA, Meralco rate, solar atlas, AI insight, chart analysis, map explanation |
| 4 | Forecasting (`forecast.py`) | `/forecast/run`, `/backtest`, `/models` — **now auth-gated** (`_require_forecast_access`) |
| 5 | Geospatial & Map (`geospatial.py`, `map.py`) | Centroids, climate (incl. hierarchy fallback, province aggregate), PSGC hierarchy, coverage, per-renewable-type map layers |
| 6 | Geothermal (`geothermal.py`) | Plant catalog, per-municipality suitability analysis, EcoSim geothermal params |
| 7 | Products (`products.py`) | `/recommend`, `/browse`, `/audit` — component recommendations |
| 8 | Simulations persistence (`simulations.py`) | CRUD over `saved_simulations` (POST/GET/GET-id/PATCH/DELETE) |
| 9 | Chat (`chat.py`) | Chat sessions + history (authenticated) |
| 10 | Admin (`admin.py`) | 17 endpoints: user CRUD/ban/role/reset, analytics, config, chat-session flagging, usage, logs |
| 11 | ETL (`etl.py`) | `/etl/run/climate` (POST), `/etl/lineage`, `/etl/validate` — admin-triggered pipeline |
| 12 | Health (`health.py`) | `/health`, `/health/detailed` with Supabase/Redis/RAG-index checks |
| 13 | AI/LLM services (`services/llm_client.py`, `groq_client.py`, `gemini_funcs.py`) | Provider abstraction, Groq primary + fallback list, Gemini fallback, sanitization, timeout |

---

## 4. Testing Scope

### 4.1 In-Scope (executed)
Authentication enforcement (401 matrix), all REST API endpoints (82-check sweep), input validation (422/literal-allowlist behavior), injection probes, rate limiting incl. XFF-spoof regression, security headers/CORS/docs-exposure, read-only database integrity + RLS verification, performance benchmarks (23 endpoints × 30 reps), 25-user load test, dependency/SAST audits, LLM-layer behavioral eval, production frontend build, automated unit/integration/UI test suites, defect regression.

### 4.2 Out-of-Scope / Not executable in this environment
- Multi-browser (Chrome/Edge/Firefox/Safari) and multi-device (tablet/smartphone) compatibility — no browser automation tool was configured in this environment → **marked "not executable" in §14; recommend manual verification**.
- Human usability/UAT sessions with real users → heuristic/code-level review only (§15).
- Screenshot evidence (Appendix B) → replaced by machine-readable JSON/CSV/log artifacts.
- Database **write** operations — stakeholder constraint: read-only only. INSERT/UPDATE/DELETE paths were verified via code + test-suite mocks, not live writes (§10).
- Destructive/admin operations against live data (user creation, banning, config writes) — read-only constraint.

---

## 5. Testing Methodology

Followed **Requirements → Test Planning → Test Case Development → Test Execution → Defect Identification → Correction → Retesting → Final Evaluation**, re-executing rather than trusting the September baseline.

| Testing Type | Performed? | Evidence |
|---|---|---|
| Unit Testing | ☒ Yes | 177 unit tests passed |
| Integration Testing | ☒ Yes | 66 passed / 1 failed / 32 skipped |
| System Testing | ☒ Yes | 82-endpoint live sweep |
| Functional Testing | ☒ Yes | Sweep + defect retests (§8) |
| Usability Testing | ◐ Partial | Code-level heuristic review only; no human testers (§15) |
| Performance Testing | ☒ Yes | 23-endpoint benchmark + Locust u25 |
| Security Testing | ☒ Yes | 16 probes + SAST + dependency audits + live rate-limit retest |
| Compatibility Testing | ☐ Not executable | No multi-browser/device rig (§14) |
| Database Testing | ◐ Read-only | Counts + RLS + integrity inspection; no writes by constraint |
| API Testing | ☒ Yes | 82-check sweep incl. error paths |
| Regression Testing | ☒ Yes | DEF-01–06 retests + full suite re-runs |
| User Acceptance Testing | ☐ Not executable | Requires human users (§15) |

---

## 6. Test Environment

### 6.1 Hardware
| Component | Specification |
|---|---|
| Processor | Intel Core i5-8400 @ 2.80 GHz (6 cores) |
| RAM | ~8 GB |
| Storage | 480 GB SSD |
| Display Resolution | Not measured (API-level testing; no browser rig) |
| Network | Live internet (Supabase/Groq/Gemini reachable) |

### 6.2 Software
| Software | Version |
|---|---|
| Operating System | Windows 11 Pro for Workstations, build 26200 |
| Web Browser | Not exercised — no browser automation configured (see §14) |
| Programming Language | Python 3.13.2 / Node.js 24.15.0 |
| Framework | FastAPI 0.115.0 + Uvicorn · React 18 + Vite 6.4.3 |
| Database | Supabase (PostgreSQL, PostgREST, RLS) — live project, accessed read-only |
| Cache/Rate-limit | Upstash Redis (+ in-memory fallback) |
| API/LLM Service | Groq (`groq/compound-mini`, groq 0.18.0) · Google Gemini (fallback) |
| Key deps | statsmodels 0.14.6, scikit-learn 1.9.0, pandas 3.0.5, supabase 2.10.0, pytest 9.1.1, httpx 0.27.2, locust 2.46.5, bandit 1.9.4, pip-audit 2.10.1 |

---

## 7. Test Data

| Data Category | Description | Records |
|---|---|---|
| DOE energy dataset | `master_preprocessed.csv`, annual national statistics | 23 rows × 45 cols (2003–2025) |
| Geographic reference | Live Supabase read-only counts | regions **18**, provinces **120**, municipalities **1,813**, barangays **53,460** |
| Climate | `municipality_climate_monthly` | **334,584** rows |
| Suitability | hydropower / geothermal suitability tables | **1,600** / **1,813** rows |
| Forecast artifacts | `forecast_consumption_2025_2030.csv`, `model_comparison_results.csv` | 6-yr forecasts, 6-model comparison |
| User accounts | Real auth not exercised beyond 401-negative probes (read-only constraint; no test user was created) | n/a |
| Sample transactions | EcoSim simulation requests via sweep/benchmark (valid param sets) | 5–30 reps per endpoint |

---

## 8. Functional Test Cases & Results

The 82-check live endpoint sweep (`rerun-2026-09-15/functional/endpoint_sweep.csv`) exercised every public route plus negative/auth paths. Status mix was **45×200, 17×401, 16×422, 3×404, 1×201** — every non-200 was an *expected* auth/validation/not-found response.

| Test ID | Module | Test | Expected | Actual | Status |
|---|---|---|---|---|---|
| TC-API-001 | Health | `GET /health` | 200 `{status:ok}` | 200, 4.1 ms | **Pass** |
| TC-API-001b | Health | `GET /health/detailed` | 200 + dep checks | 200: supabase=ok, redis=ok, rag_index=ok | **Pass** |
| TC-ES-001/001b | EcoSim | municipalities/provinces lists | 200, items>0 | 200 (64.7/44.8 ms), populated | **Pass** |
| TC-ES-sim | EcoSim | `GET /ecosim/` simulation | 200 computed result | 200, mean 547 ms | **Pass** |
| TC-ES-AI | EcoSim | `GET /ecosim/ai` | 200 AI narrative | 200, mean 612 ms | **Pass** |
| TC-EH-* | EnergyHub | overview/forecast/trends/map-data/breakdowns/demand/irena/meralco/solar-atlas | 200 | all 200, ≤50 ms except map-data 41 ms | **Pass** |
| TC-EH-AI | EnergyHub | `/energyhub/ai-insight` | 200 or quota-gated 401 | mixed 200/401 — quota enforcement working | **Pass** |
| TC-GEO-* | Geothermal | plants + per-municipality | 200 | 200 (plants 4.6 ms; analysis 294.9 ms) | **Pass** |
| TC-MAP-* | Map | coverage/solar/psgc | 200 | 200, ≤60 ms | **Pass** |
| TC-GSP-* | Geospatial | centroids/climate | 200 | 200, ≤47 ms | **Pass** |
| TC-PR-* | Products | recommend/browse/audit | 200 | 200, ≤9 ms | **Pass** |
| TC-AUTH-* | Auth | `/protected/me`, `/admin/*` w/o token | 401 | 401 "Missing token" on all | **Pass** |
| TC-FC-001–003 | Forecast | `/forecast/run`, `/backtest`, `/models` | sweep expected public 200 | **401 "Missing token"** — routes now require `get_verified_user` (`forecast.py:31`) | **Fail-in-sweep / Pass-as-hardening** — deliberate behavior change; sweep expectation stale (BUG-06) |
| TC-INJ-* | Input security | injection strings in `metric`, `energy_type`, `renewable_type` | 4xx reject | 422 literal-validation errors; nothing echoed into success bodies | **Pass** |
| TC-SIM-* | Simulations | CRUD w/o auth | 401 | 401 | **Pass** |

**Functional result: 79/82 sweep checks PASS; the 3 "failures" are a verified security improvement** (forecast endpoints moved from public to authenticated). No functional regression found.

---

## 9. Input Validation Testing

| Test ID | Input | Condition | Expected | Actual | Status |
|---|---|---|---|---|---|
| IV-001 | `/forecast/run?metric=` | injection `' OR '1'='1` | 4xx | 401 (auth gate precedes validation) | **Pass** |
| IV-002 | `/energyhub/forecast?metric=` | `invalid_metric` / `consumption;DROP TABLE municipalities--` | 4xx | 422 literal_error, allowlist enforced | **Pass** |
| IV-003 | `/map/{renewable_type}` | invalid type | 4xx | 422 literal_error (`solar|wind|hydro|…`) | **Pass** |
| IV-004 | `/products/recommend?energy_type=` | `' OR '1'='1` | 4xx, no reflection | 422 allowlist reject | **Pass** (DEF-05 fix verified) |
| IV-005 | `/ecosim` GET | missing required params | 422 | 422 (suite test `test_get_ecosim_missing_params` passed) | **Pass** |
| IV-006 | `/ecosim` POST | invalid body | 422 | 422 (suite test `test_post_ecosim_invalid_body` passed) | **Pass** |
| IV-007 | `/geothermal/{id}` | nonexistent id 999999 | 4xx, no internals | 404 `{"detail":"Municipality not found"}` — no stack/DB leak | **Pass** (DEF-01 fix verified) |

Validation is enforced by FastAPI/Pydantic literal-allowlists at the boundary — consistent with the project's api-design rules.

---

## 10. Database Testing (read-only by stakeholder constraint — no live writes performed)

### 10.1 Operations
| Test ID | Operation | Expected | Actual | Status |
|---|---|---|---|---|
| DB-001 | INSERT | — | **Not executed — read-only constraint.** Covered indirectly by unit/integration suites' mocked writes (all passed) | N/A |
| DB-002 | SELECT | correct rows | PostgREST `count=exact` HEAD/GET returned live counts (§7) | **Pass** |
| DB-003 | UPDATE | — | Not executed — read-only constraint | N/A |
| DB-004 | DELETE | — | Not executed — read-only constraint | N/A |
| DB-005 | RLS / access control | anon key must not read user tables | `profiles`, `saved_simulations`, `admin_audit_log`, `ml_model_registry` → **401 "permission denied"**; `user_ecosim_logs` → 200 with **0 rows** (RLS filters to own rows; anon has none) | **Pass** |

### 10.2 Data Integrity
| Check | Result |
|---|---|
| Primary/foreign key integrity | ☒ Pass by inspection — PSGC hierarchy consistent (18 regions → 120 provinces → 1,813 municipalities → 53,460 barangays) and `/map/psgc/hierarchy` serves coherent nested data |
| Referential completeness | ☒ geothermal_suitability has exactly 1,813 rows = one per municipality; hydropower 1,600 |
| Required fields / dtype consistency | ☒ modeling CSV: 0 duplicates, missing values only in structurally-unavoidable derived-lag cells |
| Duplicate prevention | ☒ dataset contains no duplicate year rows |
| Transaction consistency / backup | ☐ Not executable under read-only constraint — recommend admin-side verification |

---

## 11. API / External Service Testing

| Test ID | Service | Request | Expected | Actual | Status |
|---|---|---|---|---|---|
| API-001 | Groq | 6 live renewable-analysis calls | structured markdown | 6/6 non-empty, sanitized, all required headers, prescriptive content extracted | **Pass** |
| API-002 | Groq→fallback | inject Gemini failure | Groq answers | response in 1,919.7 ms | **Pass** |
| API-003 | Groq timeout | 0.5 s budget | graceful empty return | elapsed 504.1 ms → `""` → caller fallback path | **Pass** |
| API-004 | Groq configured fallback model | call `qwen/qwen3.6-27b` | 200 | **HTTP 404 model-not-found** — configured model unavailable to this account | **Fail** (BUG-08) |
| API-005 | Supabase | REST reads (anon key) | public tables readable, private denied | both verified (§10) | **Pass** |
| API-006 | Redis/Upstash | `/health/detailed` | dep check `ok` | `redis: ok` | **Pass** |

**API evaluation checklist:** ☒ successful requests · ☒ invalid requests handled (422 allowlists) · ☒ authentication verified (401 matrix) · ☒ timeout handling (LLM 504 ms abort) · ☒ error handling (no internals leaked) · ☒ response validation · ☒ rate-limit handling (60/min + 429s; spoof regression fixed) · ☒ service-failure handling (Gemini→Groq, timeout→fallback, Supabase-down→`degraded` per historical failure matrix, re-confirmed by code inspection).

---

## 12. Performance Testing

### 12.1 Endpoint benchmark — `rerun-2026-09-15/perf/summary.json` (30 reps each, sequential)

| Endpoint | Mean | p95 | Result |
|---|---:|---:|---|
| `/health` | 3.6 ms | 4.0 ms | Pass |
| `/health/detailed` | 260.7 ms | 250.7 ms | Pass (live dependency checks) |
| `/energyhub/overview` | 5.5 ms | 7.0 ms | Pass |
| `/energyhub/forecast` | 3.4 ms | 4.8 ms | Pass (precomputed CSV) |
| `/energyhub/trends` | 7.2 ms | 9.2 ms | Pass |
| `/energyhub/map-data` | 41.1 ms | 42.6 ms | Pass |
| `/energyhub` breakdowns / model-comparison / provincial-demand | 3.2–5.2 ms | ≤6.5 ms | Pass |
| `/ecosim/municipalities` | 50.1 ms | 52.4 ms | Pass |
| `/ecosim/provinces` | 40.5 ms | 43.1 ms | Pass |
| `/geothermal/plants` | 4.6 ms | 5.9 ms | Pass |
| `/geothermal/{municipality}` | 294.9 ms | 324.5 ms | Pass (heavier compute) |
| `/geospatial/climate` | 47.1 ms | 48.2 ms | Pass |
| `/map/coverage` `/map/solar` | 39.0 / 60.1 ms | ≤61.5 ms | Pass |
| `/products/recommend` | 8.2 ms | 9.3 ms | Pass |
| `/forecast/models` | 3.1 ms | 4.0 ms | Flagged — 401 unauthenticated; latency fine, auth-by-design |
| `/ecosim/` simulation | 547.0 ms | 553.3 ms | Pass (n=5, compute-heavy) |
| `/ecosim/ai` | 611.8 ms | 628.3 ms | Pass (n=5) |
| `/energyhub/ai-insight` | 638.9 ms | 3,038.0 ms | Flagged — mixed 200/401 from quota/auth gating, not a latency defect |
| `/energyhub/map-explanation` | 137.6 ms | 144.9 ms | Pass |

### 12.2 Load test — fresh Locust, 25 concurrent users (`rerun-2026-09-15/load/u25_stats.csv`)

| Metric | Value |
|---|---|
| Total requests | **1,155** |
| Request failures | **0** |
| Throughput | ~9.99 req/s |
| Aggregate mean / median / p95 / max | 2,202 / 2,000 / 4,400 / 6,278 ms |
| EcoSim simulation under load | 121 reqs · 0 fail · mean 3,615 ms · p95 5,400 ms |
| EnergyHub overview under load | 159 reqs · 0 fail · mean 1,877 ms |
| Map data under load | 152 reqs · 0 fail · mean 1,831 ms |

**Tooling note:** Locust's `StatsCSVFileWriter` raised `ValueError: I/O operation on closed file` in a post-run greenlet — a Locust artifact, not an application failure; all request statistics were still captured (BUG-05).

**Interpretation:** zero failures but **~2 s average latency at only 25 users** confirms the September finding that a single uvicorn worker saturates near ~10 interactive users; horizontal scale-out is required beyond that. The sequential benchmark (single-user ~3–60 ms on reads) shows the app itself is fast — the degradation is concurrency-bound, consistent with synchronous route handlers + per-process state.

### 12.3 Performance metrics block
- Avg response (single user, read APIs): **3–60 ms** · (compute endpoints) **~140–640 ms**
- Min / max observed: **2.4 ms** (`/health`) / **6,278 ms** (EcoSim under u25 load)
- Concurrent users tested: **25** (0 request failures) — **recommended single-worker ceiling ≈ 10**
- Error rate under load: **0%**
- Availability during test window: 100% of probed requests answered
- Frontend build: success in 2 m 59 s; **main chunk 6.42 MB (1.93 MB gzip)** + pdfmake chunk 1.01 MB → >500 kB warnings; code-splitting recommended (BUG-07)

---

## 13. Security Testing

| Test ID | Area | Procedure | Expected | Actual | Status |
|---|---|---|---|---|---|
| SEC-AUTH-01–04 | AuthN | no/malformed/`alg:none`/wrong-signature JWT on `/protected/me` | 401 | 401 ×4 | **Pass** |
| SEC-AUTH-ADM | AuthZ | bad token on `/admin/users`, `/admin/analytics`, `/admin/config` | 401/403 | 401 ×3 | **Pass** |
| SEC-HDR-01/02 | Headers | inspect response headers | security headers, masked banner | 5/5 headers present; `server: Lumi` | **Pass** |
| SEC-CORS-* | CORS | preflight allowed origin / Vercel-regex / disallowed origin | 200 / 200 / reject | 200 · 200 · **400, no ACAO** | **Pass** |
| SEC-DOCS | Info exposure | `/docs`, `/redoc`, `/openapi.json` | not exposed in prod mode | **404 ×3** | **Pass** |
| SEC-ERR-01 | Error leakage | trigger 404 | no internals | clean `{"detail":…}` | **Pass** |
| SEC-RL-* | Rate limiting | 70 req ×3: normal / spoofed-loopback-XFF / public-XFF | cap enforced; spoof must not bypass | 60×200+10×429 · **70×429 · 70×429** — Sept SEC-01 bypass confirmed fixed | **Pass** |
| SEC-INJ | Injection | `' OR '1'='1`, `;DROP TABLE…` in query/path params | rejected inert | 422 allowlist rejects, no echo, no DB effect | **Pass** |
| SEC-SAST | Static analysis | Bandit on `app/` | — | **0 issues / 16,960 LOC** (3 skips configured) | **Pass** |
| SEC-DEP-BE | Dependency audit | pip-audit on backend venv | — | **66 known vulns in 6 pkgs** — pillow 11.3.0 (~35 rows, fix→12.x), starlette 0.38.6 (~14, incl. multipart-DoS family), transformers (~8), python-jose 3.3.0 (5, JWT alg-confusion), python-dotenv 1.0.1 (2), ecdsa 0.19.2 (2, Minerva, no fix) | **Fail** (BUG-02) |
| SEC-DEP-FE | Dependency audit | npm audit on frontend | — | **4 vulns: 2 moderate (vitest, @vitest/mocker — dev-only), 2 critical (maplibre-gl via plotly.js, plotly.js; fix = plotly.js 4.1.1 major)** | **Fail** (BUG-03) |

**Security summary:** application-layer defenses are strong (16/16 probes; previously-fixed SEC-01–10 items remain fixed — verified live for SEC-01, SEC-10 and by code for the rest). The exposed risk has moved to the **dependency layer**: 66 backend + 4 frontend advisories, directly contradicting the September "clean audit" claims.

---

## 14. Compatibility Testing

| Browser | Result |
|---|---|
| Chrome / Edge / Firefox / Safari | **Not executable in this environment — no browser automation configured; recommend manual verification.** Frontend targets ES-modern browsers via Vite 6; Vitest suite (13 tests incl. i18n, charts, theme-contrast) passed under jsdom. |

| Device | Result |
|---|---|
| Desktop Windows | **Pass (build + API-level)** — production build compiles, backend serves correctly on this machine |
| Laptop/Tablet/Smartphone | **Not executable — recommend manual verification.** Tailwind responsive classes exist throughout but no physical devices were tested |

---

## 15. Usability and UI Testing (heuristic/code-level — no human testers available)

| Test ID | Criterion | Evidence found | Status |
|---|---|---|---|
| UI-001 | Navigation | React Router with dedicated pages (Home, Dashboard, EcoSim, EnergyHub, Saved Simulations, Chat, Profile, Security Settings, Admin) | Pass (structure) |
| UI-002 | Readability | `theme-contrast.test.js` (3 tests) enforces contrast programmatically — passed | Pass |
| UI-003 | Consistency | shadcn/Tailwind component system used uniformly | Pass |
| UI-004 | Feedback | **39 `toast.error` + 16 `toast.success` call sites** across pages; EcoSim AI has retry/status-polling UX | Pass |
| UI-005 | Error messages | `Please log in to continue using EnergyHub` copy verified in `energyhub.py:134` (DEF-06 fix confirmed); backend returns clean `{"detail":…}` | Pass |
| UI-006 | Responsiveness/a11y | `aria-*`/`label`/`alt` attributes present in 11+ page files; i18n provider tested | Partial — code-level only |
| UI-UAT | Real-user acceptance | **Not executable in this environment — requires human participants; recommend moderated UAT per `tests/docs/usability_testing.md`** | Not tested |

---

## 16. ISO/IEC 25010 Evaluation (evidence-based; 2023 revision terminology)

| Characteristic | Evidence | Result |
|---|---|---|
| Functional Suitability | 79/82 sweep + 360/363 automated tests pass; all modules respond correctly | **Good** |
| Performance Efficiency | Reads 3–60 ms; but ~2.2 s avg @25 users, 6.4 MB bundle | **Adequate — constrained concurrency** |
| Compatibility | No multi-browser/device testing possible | **Not assessed** |
| Interaction Capability | Toasts, i18n, contrast tests, structured pages | **Good (code-level)** |
| Reliability | 0 load-test failures; graceful LLM fallback/timeout; `degraded` health reporting; in-memory counters per-process (documented limitation) | **Good** |
| Security | 16/16 probes, RLS verified, allowlist validation, masked banner — but 70 unpatched dependency advisories | **Good app-layer / Poor dep-layer** |
| Maintainability | Modular routes/services split, 363 automated tests executed (+32 env-skipped), SAST clean; test-infra gap (BUG-01) | **Good** |
| Flexibility | Per-process rate limits multiply under horizontal scaling (documented); static forecast artifacts need pipeline re-runs | **Adequate** |
| Safety | AI outputs sanitized; quota gating; no unsafe side-effects observed in testing | **Adequate** |

---

## 17. Defect / Bug Report

**Historical defects — retest status (fresh):**

| Defect | Description | Original sev. | Fresh retest | Status |
|---|---|---|---|---|
| DEF-01 | `/geothermal/999999` leaked 500 internals | Medium | 404 `{"detail":"Municipality not found"}` — clean | **Verified fixed** |
| DEF-02 | `/map` invalid renewable type | Low | 422 literal_error | **Verified fixed** |
| DEF-03 | `/forecast` bogus metric | Low | 422 literal_error (public `/energyhub/forecast`); 401 on auth-gated `/forecast/*` | **Verified fixed** |
| DEF-04 | `/forecast/run` accepted injection silently | Low | 401 auth gate → then 422 validation; injection cannot reach handler | **Verified fixed** |
| DEF-05 | `/products/recommend` unvalidated `energy_type` | Low | 422 allowlist reject, no echo | **Verified fixed** |
| DEF-06 | AI-quota message named wrong product | Trivial | `energyhub.py:134` reads "continue using EnergyHub" | **Verified fixed (code + behavior)** |
| SEC-01 | XFF spoof → rate-limit bypass | High | Live retest: spoofed XFF 70/70 → 429 | **Verified fixed** |
| SEC-02–10 | split counters, fail-open status, CVEs, `VITE_` secrets, temp_password leak, 503 leak, ETL interpolation, Bandit lows, banner/docs | Med–Info | Rate-limit merged-counter tests pass; docs 404; banner `Lumi`; **BUT SEC-04's "0 CVEs" claim no longer holds** — see BUG-02/03 | Mostly verified; dep-CVE claim regressed |

**New defects found by this evaluation:**

| Bug ID | Module | Description | Severity | Priority | Status |
|---|---|---|---|---|---|
| BUG-01 | Test infra | `TestETLTableAllowlist` 2 tests fail — `pytest-asyncio` (or any async plugin) absent from backend venv; `async def` tests can't execute | Medium | Med | **Open** — install pytest-asyncio or convert tests |
| BUG-02 | Backend deps | pip-audit: **66 known vulnerabilities** across pillow, starlette, transformers, python-jose, python-dotenv, ecdsa | **High** | **High** | **Open** — upgrade pillow≥12.2, starlette≥0.40, python-jose≥3.4.0, python-dotenv≥1.2.2; ecdsa has no fix (monitor/scope) |
| BUG-03 | Frontend deps | npm audit: 4 vulns — **critical** maplibre-gl (bundled by plotly.js) & plotly.js; moderate vitest/@vitest/mocker | **High** | **High** | **Open** — major bump plotly.js→4.1.1, vitest→5.x |
| BUG-04 | Test stability | `test_health_endpoint_response_time` flaky under concurrent suite load (555 ms > 500 ms; standalone 10.9 ms) | Low | Low | **Open** — isolate perf test or raise threshold |
| BUG-05 | Tooling | Locust `StatsCSVFileWriter` closed-file error post-run (stats still captured) | Low | Low | **Open** — Locust 2.46.5/Windows artifact |
| BUG-06 | Docs/sweep | Stale expectations & metrics: sweep assumes `/forecast/*` public (now authed); Sept CSV carried "placeholder" SARIMAX/RF rows; Sept "0 vulnerabilities" audits contradicted by fresh runs | Medium | Med | **Open** — update sweep expectations + comparison CSV + audit notes |
| BUG-07 | Frontend perf | Main bundle 6.42 MB (1.93 MB gzip) + 1 MB pdfmake chunk | Medium | Med | **Open** — route-level code-splitting, lazy-load pdfmake/plotly |
| BUG-08 | LLM config | Configured Groq fallback model `qwen/qwen3.6-27b` → HTTP 404 for this account | Medium | Med | **Open** — prune/replace fallback list |
| BUG-09 | LLM contract | `groq_client.py` comments claim forced-JSON output; observed output is markdown prose (0/4 JSON validity when JSON probed) — doc/behavior mismatch; harmless for current prompts, hazardous if a consumer assumes JSON | Low | Low | **Open** — fix comments or enforce `response_format` |

---

## 18. Corrective Action and Retesting

| Defect | Corrective action (from Sept cycle) | Retest (2026-09-15) | Final status |
|---|---|---|---|
| DEF-01–06 | Validation allowlists, error sanitization, copy fix, auth gate | All six verified — §17 | **Closed** |
| SEC-01 | Trust Vercel platform headers / direct peer only | Spoof retest 70/70 → 429 | **Closed** |
| SEC-04 | Dependency upgrades claimed complete | **Fresh audits contradict: 66 backend + 4 frontend advisories** | **Reopened → BUG-02/03** |

No new fixes were applied during this read-only evaluation; all BUG-01–09 items are handed to the team.

---

## 19. Regression Testing

| Test ID | Previously passing function | Retest | Status |
|---|---|---|---|
| REG-01 | Auth rejection (unauthenticated matrix) | 401s across `/protected/*`, `/admin/*`, `/forecast/*`, `/simulations` | Pass |
| REG-02 | Public GET modules (EcoSim/EnergyHub/Map/Geothermal/Geospatial/Products) | 82-check sweep, all public routes 200 | Pass |
| REG-03 | Forecast endpoints | Behavior **changed**: public → authenticated (hardening, not regression) | Pass w/ note |
| REG-04 | Rate limiting | Stricter — merged counters + anti-spoof | Pass |
| REG-05 | Full automated suites | 360/363 pass; 2 infra-fail + 1 flaky-perf + 32 env-skips | Pass w/ exceptions |
| REG-06 | Prior security fixes (SEC-01–10 minus CVE claim) | Verified as in §17 | Pass |
| REG-07 | Frontend unit tests | 13/13 Vitest | Pass |

---

## 20. Testing Results Summary

Counts include only activities actually executed on 2026-09-15 (skipped tests excluded from denominators; the 3 sweep "fails" counted as fails for honesty even though root cause is stale expectation):

| Category | Total | Passed | Failed | Pass rate |
|---|---:|---:|---:|---|
| Functional (endpoint sweep + defect retests) | 88 | 85 | 3* | 96.6% |
| Database (read-only checks) | 14 | 14 | 0 | 100% |
| API/external (LLM eval + service probes) | 6 | 5 | 1 | 83.3% |
| Automated suites (pytest×3 + vitest; skips excluded) | 363 | 360 | 3† | 99.2% |
| Performance (24 benchmark entries + load test) | 25 | 22 | 3‡ | 88.0% |
| Security (probes + rate-limit scenarios + audits) | 21 | 19 | 2§ | 90.5% |
| Compatibility | — | — | — | Not executable |
| Usability (heuristic items) | 6 | 5 | 1 partial | 83.3% |
| Regression (items in §19) | 7 | 7 | 0 | 100% |
| **TOTAL (executed items)** | **530** | **517** | **13** | **97.5%** |

\* 3 sweep fails = auth-hardening expectation drift (verified correct-by-design). † 2 missing-async-plugin (BUG-01) + 1 flaky perf threshold under concurrent load (BUG-04). ‡ `forecast/models` 401-by-design, `ai-insight` mixed 200/401 quota gating, `db:setup` benchmark-script artifact ("No module named 'app'"). § 2 audit failures = BUG-02/03.

---

## 21. Overall Technical Assessment

### Overall Testing Result: ☒ **Passed with Minor Issues → trending For Further Improvement** (dependency findings prevent a clean bill)

**Technical assessment.** LUMI's application layer is in genuinely good shape: every functional module responds correctly, auth/authz boundaries hold under direct probing, the September defect and security-fix set survived regression wholesale (including the previously-bypassable rate limiter), input validation is allowlist-strict, the failure modes are graceful, and the single-worker performance envelope is honestly characterized (fast reads, ~10-user practical ceiling, zero request failures at 25 users). The ML component is modest but honestly measured — see the companion ML report.

**The identified defects/issues:** 9 new open items — most consequentially **70 dependency advisories (66 backend + 4 frontend, incl. 2 critical frontend)** that contradict the earlier clean-audit documentation, a test-infrastructure gap (missing async plugin), stale sweep/doc expectations, a heavy 6.4 MB bundle, and one unreachable configured Groq fallback model. None are application-logic defects; all are remediable dependency/tooling/documentation items.

**The system is therefore assessed as: ☒ Acceptable with Minor Revisions** — *not yet deployment-ready*: BUG-02 and BUG-03 (unpatched dependency vulnerabilities) should be resolved before any public production launch, and compatibility/UAT remain unverified pending manual testing.

---

## 22. Recommendations

1. **Remediate dependency CVEs first** (BUG-02/03): pillow→≥12.2, starlette→≥0.40, python-jose→≥3.4.0, python-dotenv→≥1.2.2, plotly.js→4.1.1, vitest→5.x; pin and re-audit in CI so "clean audit" claims can't silently regress.
2. **Fix test infrastructure** (BUG-01/04): add pytest-asyncio; isolate the 500 ms health-threshold test from concurrent load.
3. **Update stale artifacts** (BUG-06): sweep expectations for `/forecast/*` (now authenticated), regenerate `model_comparison_results.csv` (remove placeholder rows — real numbers now exist), correct prior "0 vulnerabilities" statements.
4. **Scale plan** (documented ceiling ~10 interactive users/worker): multi-worker uvicorn or instance scaling before launch; note per-process rate-limit counters multiply effective limits.
5. **Bundle diet** (BUG-07): route-level code-splitting; lazy-load pdfmake/plotly.
6. **LLM hardening** (BUG-08/09): prune the 404 fallback model; align `groq_client.py` comments/`response_format` with actual markdown contract; surface the ~5 s median / 18 s tail latency via the existing retry/polling UX.
7. **Complete the untested quadrants manually:** multi-browser/device matrix, real-user UAT, DB write-path verification under a disposable test project.
8. **Keep the ML honest:** surface forecast intervals + the small-sample caveat in the UI; move to monthly data if available (biggest accuracy lever); per-target ARIMA orders.

---

## 23. Testing Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Test Engineer/Tester | Devin (automated execution) | *electronic — this report + artifacts* | 2026-09-15 |
| Developer | LUMI Development Team | *pending human sign-off* | — |
| Project Leader | — | *pending* | — |
| Technical Adviser | — | *pending* | — |
| Project Adviser | — | *pending* | — |

---

## 24. Appendices — Evidence Index

All under `docs/09-Technical-Evaluation/artifacts/`:

| Artifact | Contents |
|---|---|
| `rerun-2026-09-15/functional/` | `pytest-backend.txt` (104/2), `pytest-lumi-unit.txt` (177), `pytest-lumi-integration.txt` (66/1/32), `vitest-frontend.txt` (13), `endpoint_sweep.csv/.jsonl` (82 checks), `defect_retests.json`, `backend_boot.log`, `sweep_log.txt` |
| `rerun-2026-09-15/security/` | `probes.json` (16/16), `ratelimit_live.json` (XFF regression), `bandit-app.txt` (0 issues/16,960 LOC), `pip-audit-env.txt` (66 vulns), `npm-audit-frontend.json` (4 vulns) |
| `rerun-2026-09-15/perf/` | `summary.json` + `latency.csv` (23 endpoints × 30), `benchmark_log.txt`, `vite-build.txt` |
| `rerun-2026-09-15/load/` | `u25_stats.csv`, `u25_stats_history.csv`, `u25.html`, `u25_failures.csv` (0), `u25_exceptions.csv`, `locust_log.txt` (incl. stats-writer error) |
| `rerun-2026-09-15/db/` | `supabase_readonly_checks.json` (counts + RLS) |
| `rerun-2026-09-15/llm/` | `llm_eval.json`, prompt/response snippets, run log |
| `rerun-2026-09-15/ml/` | full fresh forecasting-eval artifacts (see ML report Appendix A) |
| `rerun-2026-09-15/scripts/` | `endpoint_sweep.py`, `security_probes.py`, `benchmark.py` |
| `artifacts/scripts/` | `evaluate_forecasting_models.py`, `llm_groq_eval.py` (authored for this evaluation) |
| Historical (Sept 5–8) | `TECHNICAL_EVALUATION_ALL_RESULTS.md`, `functional-test-results.md`, `security-test-results.md`, `performance-measurements.md`, `artifacts/{functional,failure,load,security,perf}/` — cited as baseline only; fresh numbers above supersede where they conflict |

**Appendix B note:** no screenshot evidence — no browser tool in this environment; artifacts are machine-readable JSON/CSV/logs instead.
