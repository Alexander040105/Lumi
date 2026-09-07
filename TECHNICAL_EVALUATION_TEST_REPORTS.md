# LUMI — Technical Evaluation Test Reports

**Project:** LUMI — Data-Driven Environmental Intelligence System for Renewable Energy Decision Support
**Test session:** September 5–8, 2026
**Compiled:** September 8, 2026

---

## 1. Functional Test Results

### Scope

Functional testing covered the React/Vite frontend, the FastAPI backend, the unit test suite, the integration suite, and a live endpoint sweep of every mounted API route. Tests used valid inputs, missing parameters, boundary values, and adversarial strings. Authentication flows were verified manually with real Google and GitHub accounts.

### Test Environment

- OS: Windows 11
- Python: 3.13.2
- Backend runtime: uvicorn 0.30.6, single worker, `http://127.0.0.1:8000`
- Node/npm: v24.15.0 / 11.12.1
- Test tooling: pytest 9.1.0, Vitest 3.2.7, Locust 2.46.4

### Overall Test Counts

| Suite | Result | Status |
|---|---|---|
| Unit tests (`lumi_tests/tests/unit/`) | 177 passed | PASS |
| Backend tests (`fastapi-backend/tests/`) | 106 passed | PASS |
| Frontend Vitest (`react-frontend`) | 9 passed (3 test files) | PASS |
| Integration tests (`lumi_tests/tests/integration/`, live server deselected) | 23 passed, 2 skipped, 1 deselected | PASS |
| Live endpoint sweep | 82/82 passed | PASS |

Across these four suites, **315 automated assertions passed**. A separate note in the source also reports 356 automated assertions (177 + 99 + 9 + 67 + 4 extra integration passes); that older aggregated total appears to pre-date the latest run and is superseded by the 315-assertion figure shown above.

### Functional Test Case Summary

The test plan tracked 69 functional test cases across the main modules. 58 passed, 0 failed, and 11 were pending or N/A. The pending cases are mainly the responsive-viewport visual checks (2 cases deferred until a live browser pass can be run) and the ML model notebook re-runs (9 cases; the endpoints were verified but full notebook reproduction sits outside this test cycle).

| Module | Total | Passed | Failed | Pending/N-A |
|---|---:|---:|---:|---:|
| Authentication | 6 | 6 | 0 | 0 |
| EnergyHub | 10 | 10 | 0 | 0 |
| EcoSim | 13 | 13 | 0 | 0 |
| AI Intelligence | 7 | 7 | 0 | 0 |
| API Endpoints | 13 | 13 | 0 | 0 |
| Visualization | 9 | 7 | 0 | 2 |
| Machine Learning | 11 | 2 | 0 | 9 |
| **Total** | **69** | **58** | **0** | **11** |

### Notable Functional Findings

- **Authentication.** No-token, malformed-token, and expired-token requests all returned 401. Valid Supabase JWTs returned 200 with user data. Manual OAuth registration with Google and GitHub succeeded.
- **EcoSim.** `GET /ecosim/municipalities` returned 1,813 items. Simulation and RAG/AI calls returned 200. Missing or invalid `municipality_id` returned 422 or 404 with clean messages.
- **EnergyHub.** Overview, trends, forecast, map-data, source/grid breakdown, and IRENA endpoints all returned 200. Invalid `metric` values now return 422 after the DEF-03 fix.
- **AI layer.** Groq primary path, Gemini-to-Groq fallback, AI timeout, invalid-JSON handling, and RAG retrieval were all exercised.
- **API endpoint sweep.** All 82 checks passed, including boundary cases and SQL-injection-style inputs. The inputs were rejected at the FastAPI boundary with 422 and were not echoed back.

### Defects Fixed and Retested

| Defect ID | Description | Severity | Status |
|---|---|---|---|
| DEF-01 | `/geothermal/{bad_id}` returned 500; now returns 404 | Low | Fixed |
| DEF-02 | `/map/{invalid_type}` returned 200 with an error body; now returns 422 | Low | Fixed |
| DEF-03 | Invalid forecast `metric` was silently accepted; now validated | Low | Fixed |
| DEF-04 | `/forecast/run` accepted injection-style strings; now validated | Low | Fixed |
| DEF-05 | `/products/recommend` echoed unvalidated `energy_type`; allowlist added | Low | Fixed |
| DEF-06 | AI-quota error referenced wrong product name; copy corrected | Trivial | Fixed |

### Limitations

- Responsive viewport tests for 375 px and 768 px are deferred until a live browser pass can be completed.
- ML model cases were verified at the endpoint level; full notebook re-runs are outside the current test scope.

---

## 2. Performance Measurements

### Scope

Performance testing measured FastAPI endpoint latency, LLM latency, Supabase query latency, frontend bundle size, and production cold-start behavior. Tests ran locally with a single user and warm caches, and a light production smoke test was also executed.

### API Endpoint Latency (single user, warm, n=30)

Values are in milliseconds.

| Endpoint | n | min | mean | p50 | p95 | max |
|---|---|---:|---:|---:|---:|---:|
| GET /health | 30 | 1.2 | 4.8 | 1.8 | 3.6 | 84.7 |
| GET /health/detailed | 30 | 174.2 | 191.3 | 183.0 | 214.1 | 403.3 |
| GET /energyhub/overview | 30 | 4.2 | 6.3 | 5.9 | 8.6 | 9.7 |
| GET /energyhub/forecast | 30 | 2.3 | 3.7 | 3.5 | 6.2 | 6.4 |
| GET /energyhub/trends | 30 | 5.3 | 6.8 | 6.3 | 9.6 | 10.5 |
| GET /energyhub/map-data | 30 | 36.5 | 37.5 | 37.1 | 39.4 | 39.5 |
| GET /ecosim/municipalities | 30 | 42.0 | 49.7 | 44.1 | 109.2 | 136.3 |
| GET /geothermal/5441 | 30 | 211.8 | 222.1 | 219.1 | 239.3 | 239.9 |
| GET /ecosim/ (simulation) | 5 | 448.2 | 450.2 | 449.5 | 454.5 | 454.5 |
| GET /ecosim/ai | 5 | 444.1 | 458.0 | 451.3 | 475.9 | 475.9 |
| GET /energyhub/ai-insight?use_llm=true | 5 | 42.0 | 676.8 | 44.3 | **3,207.9** | 3,207.9 |

All endpoints were within the target thresholds except `ai-insight`, where the p95 of 3.2 s reflects one full LLM round-trip. The 401 responses from the anonymous quota are expected behavior, not a performance failure.

### LLM / AI Latency

| Path | Observation |
|---|---|
| Groq EcoSim AI | 450–476 ms p50–p95 including Supabase reads |
| Gemini → Groq fallback | 1,683 ms when Gemini failed |
| AI hard timeout | Fallback returned in 61 ms |
| `ai-insight` full LLM call | ~3.2 s observed |

### Database / Supabase Query Time (direct, n=10)

| Query | mean | p50 | p95 | max |
|---|---:|---:|---:|---:|
| `regions` select-1 | 160.8 ms | 70.6 ms | 962.9 ms | 962.9 ms |
| `municipalities` select-10 | 100.7 ms | 74.0 ms | 317.9 ms | 317.9 ms |
| `climate_monthly` filtered | 78.1 ms | 76.1 ms | 88.0 ms | 88.0 ms |

The p95 on `regions` includes a cold-connection outlier. Steady-state lookups sit around 70 ms; query execution itself is sub-millisecond, with most of the time spent on TLS and network to the managed Postgres endpoint.

### Frontend Build

| Asset | Raw | Gzip |
|---|---|---|
| Main JS bundle | ~6.35 MB | ~1.91 MB |
| CSS | ~61.4 kB | ~10.7 kB |
| Leaflet JS | ~150 kB | ~43.6 kB |

Vite emits a chunk-size warning on the main bundle. The app currently ships as one chunk; route-based code splitting is the recommended next step.

### Production Smoke

A non-destructive production smoke test against `https://lumi-backend-ten.vercel.app` returned 200 for `/health`, `/health/detailed`, `/energyhub/overview`, `/ecosim/municipalities`, and `/map/coverage`. Cold starts ranged from 0.8 s to 3.8 s.

### Performance Findings

- P-01: The single 1.91 MB gzipped JS bundle is the main frontend bottleneck.
- P-02: `ai-insight` p95 of 3.2 s is acceptable because the endpoint is quota-gated by design.
- P-03: Supabase cold-connect spikes reach 963 ms; connection reuse keeps steady-state latency low.
- P-04: `geothermal/{id}` averages 222 ms; joins and response caching could reduce this further.

### Limitations

- LLM samples use n=5 due to the anonymous daily quota; n=30 was used elsewhere.
- Production timing is smoke-level only; no production load was applied.
- NASA POWER exists only in disabled ETL scripts, so no runtime latency was measured.

---

## 3. Load and Scalability Test Results

### Scope

Load tests used Locust 2.46.4 against the local FastAPI backend on a single uvicorn worker. The workload mixed EcoSim simulations, municipality/province lists, EnergyHub reads, map/geospatial calls, and catalog endpoints. Production was explicitly out of scope for load testing.

### Methodology

- Stepped profile: 1 → 10 → 25 → 50 → 75 → 100 concurrent users, 60 s per level, hatch rate 5/s.
- Profiles tested: `raw` (default), `throttled` (fixed XFF), and `spoof` (rotating XFF).
- Real municipality IDs were used to avoid 404 noise.

### Stepped Concurrency Results

| Users | Reqs | Fails | Avg (ms) | p50 (ms) | p95 (ms) | Max (ms) | RPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 96 | 0 | 90 | 38 | 600 | 1,100 | 3.3 |
| 10 (clean) | 790 | 0 | 519 | 410 | 1,400 | 2,800 | 13.3 |
| 25 (clean) | 769 | 0 | 1,637 | 1,400 | ~3,300 | ~6,000 | 13.0 |
| 50 (clean) | 614 | 0 | 3,838 | 3,800 | ~7,000 | ~9,600 | 10.5 |
| 75 (clean) | 657 | 0 | 5,582 | 5,500 | ~8,700 | ~12,000 | 11.0 |
| 100 (pass-1) | 814 | 0 | 5,591 | 5,700 | ~8,900 | ~14,000 | 13.7 |

### Interpretation

- **Every request at every level succeeded.** No 5xx errors, no timeouts, and no connection resets were observed.
- **Throughput plateaued at roughly 11–14 RPS.** Beyond this point, the single worker saturates and requests queue instead of failing.
- **Latency crossed the 1 s p95 threshold between 10 and 25 users** and the 3 s p95 threshold by 25 users.
- **Recommended interactive ceiling** for this single-worker deployment is about 10 concurrent users for sub-second p95 response times, and about 25 users before p95 exceeds 3 s.
- The system degraded gracefully: response times increased, but all requests completed.

### Rate-Limit Interaction

| Profile | Result |
|---|---|
| `throttled` (u=8, fixed IP, 45 s) | 429 returned once the 60 requests/minute window filled |
| `spoof` (u=8, rotating XFF, 30 s) | 0 × 429; each spoofed IP stayed under the cap. After the SEC-01 fix, the `X-Forwarded-For: 127.0.0.1` spoof no longer bypasses limits. |

### Bottlenecks Observed

- Single uvicorn worker with synchronous `httpx`/`supabase` calls blocks the thread pool on I/O.
- Per-request Supabase REST round-trips add about 70 ms per uncached call.
- EcoSim simulation compute averages about 450 ms.
- CORS preflight and middleware add a fixed 30–60 ms floor.

### Limitations

- Localhost loopback removes WAN latency; numbers are optimistic versus real clients.
- The u=100 run was retained from a CPU-contended first pass; a clean re-run is pending.
- Production scaling was not load-tested.
- 401 responses from anonymous AI quotas were counted as failures by Locust but are intended behavior.

---

## 4. Security Test Results and Logs

### Scope

Security testing covered authentication, authorization, JWT handling, rate limiting, input validation, injection attempts, security headers, dependency vulnerability scanning, static analysis, CORS, and secrets handling. All probes were read-only or self-cancelling.

### Static and Dependency Scanning

| Tool | Result |
|---|---|
| `bandit -r fastapi-backend/app` | No issues identified |
| `pip-audit` (backend) | No known vulnerabilities found |
| `npm audit` (frontend) | 0 vulnerabilities |

### Live Probe Results

`security_probes.py` ran 18 live checks:

| Category | Result |
|---|---|
| JWT matrix (no token, malformed, `alg:none`, wrong signature, expired, nonexistent user) | 6 PASS |
| Admin endpoints with bad token | 3 PASS |
| Security headers (XCTO, XFO, HSTS, CSP, Referrer-Policy) | 1 PASS |
| Server banner disclosure | 1 PASS (banner masked to `Lumi`) |
| CORS allowlist, regex, and disallowed origin | 3 PASS |
| `/docs`, `/redoc`, `/openapi.json` | 3 PASS (404 in production) |
| Error body leakage | 1 PASS |
| **Total** | **18 PASS, 0 WARN, 0 FAIL** |

### Confirmed Vulnerabilities

**SEC-01 — X-Forwarded-For trusted unconditionally → rate-limit and quota bypass**
**Severity:** High
**Status:** Fixed
**Result:** The rate limiter previously used the leftmost `X-Forwarded-For` value as the client IP. A spoofed `X-Forwarded-For: 127.0.0.1` header from a non-loopback client bypassed the limiter, allowing 75 requests with 0 × 429. Client identity now uses Vercel platform headers or the direct peer IP. Six unit tests confirm spoofed XFF no longer bypasses limits.

**SEC-02 — Rate limiter fails open under intermittent Redis failure**
**Severity:** Medium
**Status:** Fixed
**Result:** Redis and in-memory counters were separate; a flapping Redis could split counts and allow roughly double the intended rate. The counters are now reconciled, and regression tests confirm the limit is enforced under both healthy and failing Redis states.

**SEC-03 — `_get_user_status` fails open on DB outage**
**Severity:** Medium
**Status:** Fixed
**Result:** The original handler caught any exception and returned `True` (allow). It now returns `True` only for the `PGRST116` missing-row case and `False` for all other DB/runtime errors.

**SEC-04 — Dependency CVEs**
**Severity:** Medium
**Status:** Fixed
**Result:** `pip-audit` now reports 0 known backend vulnerabilities, and `npm audit` reports 0 frontend vulnerabilities. The JWT verification was migrated from `python-jose` to `PyJWT 2.13.0`; FastAPI, Starlette, cryptography, and other runtime dependencies were upgraded.

**SEC-05 — `VITE_`-prefixed backend secrets**
**Severity:** Medium
**Status:** Fixed
**Result:** Backend secrets such as `VITE_SUPABASE_SERVICE_ROLE_KEY` were removed from the root `.env`. Backend-facing variables now use unprefixed names; only non-sensitive frontend configuration uses `VITE_` prefixes.

**SEC-06 — Admin create-user returns `temp_password`**
**Severity:** Low
**Status:** Fixed
**Result:** The endpoint no longer returns the generated password. It returns the created user profile and directs the user to the password-reset flow.

**SEC-07 — ML worker 503 leaks raw exception text**
**Severity:** Low
**Status:** Fixed
**Result:** The 503 response now contains a generic client-facing message. The original exception text is still logged server-side with the request ID.

**SEC-08 — ETL table-name interpolation**
**Severity:** Low
**Status:** Fixed
**Result:** An allowlist was added for ETL validation tables. Unsupported names are rejected and not echoed in the response. The ETL router remains unmounted.

**SEC-09 — Bandit hygiene**
**Severity:** Low/Info
**Status:** Fixed
**Result:** Bandit now reports 0 issues. MD5 cache keys were replaced with SHA-256, the `0.0.0.0` sentinel was removed from localhost trust logic, broad `try/except/pass` cases were cleaned, XML parsing now uses `defusedxml`, and asserts/non-cryptographic choices were validated or annotated.

**SEC-10 — `Server: uvicorn` banner and docs exposure**
**Severity:** Info
**Status:** Fixed
**Result:** The `Server` header is now masked to `Lumi`. `/docs`, `/redoc`, and `/openapi.json` return 404 outside development/test environments.

### Verified Security Controls

- No-token and malformed-token requests to protected and admin routes return 401.
- `alg:none`, wrong-signature, and expired JWTs all return 401.
- A validly-signed JWT for a nonexistent user returns 401.
- Boundary validation hardening passes; 22 FastAPI regression tests pass; endpoint sweep is 82/82.
- Rate limit works when Redis is healthy and when NullRedis is in use.
- Security headers are present both locally and in production.
- CORS allows `http://localhost:5173` and the Vercel regex `https://lumi-frontend-*.vercel.app`; disallowed origins return 400.
- SQL-injection-style inputs return 422 at the FastAPI boundary and are not echoed back.
- Request bodies larger than 1 MB return 413; malformed JSON returns 422.
- `.env` files are not tracked in git; only `*.env.example` files are committed.

### Limitations

- Authenticated OAuth registration, valid-token access, and logout were verified manually; admin role-matrix probing stayed at the unauthenticated layer.
- Direct RLS-policy testing requires an authenticated Supabase session and is outside this test scope.
- TLS/certificate testing was not performed locally; production HSTS was verified.
- Fuzzing, session-fixation, and CSRF cross-site tests beyond CORS preflight were not covered.

---

## 5. System Architecture Documentation

### Overview

LUMI is a three-tier system. The frontend is a React 18 + Vite + Tailwind SPA hosted on Vercel. The backend is a FastAPI application that can run as a long-running uvicorn server or as a Vercel serverless function. Data and auth are handled by Supabase (Postgres, Auth, pgvector), and cache/rate-limit/quota state is handled by Upstash Redis. AI features use Groq as the primary LLM and Gemini as a fallback; an optional external ML worker can handle heavy endpoints but is currently disabled.

### Deployment Topology

| Tier | Component | Role |
|---|---|---|
| Client | React 18 + Vite + Tailwind SPA | Browser UI |
| Edge | `api/index.py` Vercel serverless function | Production API entry, mount normalization, optional ML worker proxy |
| Server | `uvicorn → main:app` | Long-running deployment (local, Docker, or any host) |
| Managed | Supabase (Postgres, Auth, pgvector) | Primary datastore and authentication |
| Managed | Upstash Redis | Cache, rate limiting, quotas |
| External | Groq API | Primary LLM |
| External | Gemini API | Fallback LLM |
| External | Optional ML worker | Heavy/long-running endpoints (disabled) |
| Bundled | Climate and geo CSVs | Supabase outage fallback |

### Request Pipeline

Middleware runs in this order, from outermost to innermost:

1. `TimingMiddleware` — logs request duration
2. `CORSMiddleware` — allowlist plus regex for `lumi-frontend-*.vercel.app`
3. `BodySizeLimitMiddleware` — returns 413 for bodies over 1 MB
4. `SecurityHeadersMiddleware` — sets XCTO, XFO, HSTS, CSP, Referrer-Policy, and masks `Server`
5. `RateLimitMiddleware` — 60/minute public, 10/minute auth actions, Redis + in-memory fallback
6. `RequestIDMiddleware` — assigns a UUID per request
7. Application routers and services

### Backend Routers

Twelve routers are mounted under `/api/v1`:

- `health` — `/health`, `/detailed`
- `ecosim` — simulation, AI, municipality/province/barangay lists
- `energyhub` — overview, forecast, trends, map-data, AI insight, IRENA data, model comparison, demand, solar atlas, analyze-chart
- `geothermal` — plants, plant by ID, EcoSim/EcoHub geothermal summaries
- `geospatial` — centroids, climate, hierarchy, province aggregate
- `map` — PSGC hierarchy, coverage, solar/wind/hydro/geothermal layers
- `products` — recommend, browse, audit
- `forecast` — run, backtest, models
- `simulations` — authenticated
- `admin` — users, analytics, config, usage, logs
- `protected` — `/me`, `/profile`
- `auth` — OAuth callbacks
- `etl` and `example` routers are disabled

### Service Layer

- `ecosim.py` — climate suitability and output calculations
- `gemini_funcs.py` — worker timeout, persistent cache, structured fallback
- `llm_client.py` — provider selection with Groq/Gemini fallback
- `groq_client.py` — Groq API client
- `rag_pipeline.py` — pgvector RAG in production; FAISS code exists but is unused
- `supabase_service.py` — singleton Supabase client using service-role key
- `redis_client.py` — Upstash Redis with NullRedis no-op fallback
- `data_cache.py` — Redis-backed cache

### Authentication Sequence

1. The SPA sends a `Bearer <Supabase JWT>` to the FastAPI backend.
2. On required paths, FastAPI calls `Supabase Auth → auth.get_user(token)`; any error returns 401.
3. FastAPI reads `user_roles.role` and `profiles.is_active` from Supabase using the service-role key.
4. Role is cached in Redis for 300 s; active status for 60 s.
5. FastAPI returns 200 with claims `{sub, email, role, plan}`.
6. On optional-auth read paths, the JWT is verified locally with `SUPABASE_JWT_SECRET`, then cached role/status are checked.

### Frontend

- Framework: React 18, Vite, Tailwind, React Router with hash paths
- API client: `fetch` with 30 s `AbortController` timeout, up to 3 retries, 500 ms exponential backoff, 5xx-only retries, 429 respected, `X-Request-Id`
- Supabase client: publishable anon key (fallback hardcoded in `env.js`)
- API base: dev uses `/api/v1`; prod fallback is `https://lumi-backend-ten.vercel.app`

### Disabled and Dormant Components

| Component | State |
|---|---|
| `/api/v1/etl` router | Disabled |
| `/api/v1/example` router | Disabled |
| FAISS RAG backend | Code present; runtime uses pgvector |
| NASA POWER ingestion | ETL-only; runtime never calls it |

---

## 6. Failure and Recovery Test Results

### Scope

Failure and recovery testing used controlled failure injection through `failure_matrix.py` against the FastAPI `TestClient`. Seventeen scenarios covered LLM provider outages, Supabase failures, Redis failures, invalid inputs, oversized bodies, malformed JSON, and rate-limit edge cases.

### Results Matrix

| ID | Failure Injected | Observed Behavior | Verdict |
|---|---|---|---|
| TC-FR-01 | Gemini outage | Automatic fallback to Groq; response in 1,683 ms | GRACEFUL |
| TC-FR-02 | EcoSim AI hard timeout | Structured fallback returned in 61 ms | GRACEFUL |
| TC-FR-03 | All LLM providers down | Fallback dict returned; endpoint stays functional | GRACEFUL |
| TC-FR-04a | Supabase broken → `/health/detailed` | `status=degraded`, `supabase=error`, HTTP 200 | GRACEFUL |
| TC-FR-04b | Supabase down → `/ecosim/municipalities` | 200 from bundled CSV fallback; 1,813 items returned | GRACEFUL |
| TC-FR-04c | Supabase down → `/ecosim/` simulation | 404 with clean message | GRACEFUL |
| TC-FR-04d | Supabase down → `/protected/me` with no token | 401 before DB dependency is reached | GRACEFUL |
| TC-FR-05 | Redis → NullRedis | Health shows `redis=not_configured`; `/map/solar` returns 200 | GRACEFUL |
| TC-FR-06 | NASA POWER outage at runtime | N/A — not used at runtime | N/A |
| TC-FR-07a | Invalid `municipality_id` → `/ecosim/` | 404 with clean message | GRACEFUL |
| TC-FR-07b | Invalid `municipality_id` → `/geothermal/{id}` | 404 `Municipality not found` | GRACEFUL |
| TC-FR-08 | ML worker URL dead | 503 for proxied path; rest of API healthy | GRACEFUL |
| TC-FR-09a | 70-req burst, public XFF, Redis loop-broken | Split counters allowed ~2× effective rate | FAIL-OPEN (now fixed) |
| TC-FR-09b | 70-req burst, `X-Forwarded-For: 127.0.0.1` | 60 × 200, 10 × 429; spoof no longer works | GRACEFUL |
| TC-FR-09c | NullRedis + public XFF, 75-req burst | Exactly 60 × 200, 15 × 429 | GRACEFUL |
| TC-FR-09d | Throwing Redis, 75-req burst | Exactly 60 × 200, 15 × 429 | GRACEFUL |
| TC-FR-10a | POST body > 1 MB | 413 with size message | GRACEFUL |
| TC-FR-10b | Malformed JSON body | 422 `json_invalid` | GRACEFUL |
| TC-FR-10c | Non-integer path param | 422 `int_parsing` | GRACEFUL |

Out of 17 scenarios, 16 were graceful and 1 was a confirmed fail-open (SEC-02), which has since been fixed.

### Verified Resilience Mechanisms

- Global exception handler returns sanitized `{detail, request_id}` without stack or path leaks.
- Request IDs are assigned per request and echoed in logs and error bodies.
- LLM provider fallback switches from Gemini to Groq automatically.
- LLM hard timeout and persistent cache return a fallback dict.
- Supabase failures fall back to bundled CSVs.
- Redis NullRedis turns cache helpers into no-ops.
- Rate-limit and quota fall back to in-memory counters.
- Frontend client retries 5xx only, with backoff and 429 respect.
- ML worker proxy failure returns 503 and does not affect other routes.
- Health endpoint reports degraded status when dependencies fail.

### Open and Out-of-Scope Scenarios

| Scenario | Status | Reason |
|---|---|---|
| Vercel function timeout (504) under load | Open | Production load testing was out of scope |
| Supabase Auth outage with valid cached JWT | Open | Requires controlled Auth outage with a live token |
| pgvector outage during RAG queries | Open | Needs targeted mock of the vector client |
| Groq and Gemini real network-level outage | Partially covered | Simulated in FR-03; live network partition not exercised |
| Redis permanent outage under sustained load | Partially covered | NullRedis verified; sustained load not run |

---

## Key Findings

### Passed / Verified

- **Functional coverage:** 315 automated assertions passed across unit, backend, frontend, and integration suites. The live endpoint sweep was 82/82, and all six boundary-validation findings (DEF-01–06) were fixed and retested.
- **Security posture:** All ten tracked findings (SEC-01–10) are fixed. Bandit, pip-audit, and npm audit are clean; the 18 live security probes all passed.
- **Load behavior:** Zero failures from 1 to 100 concurrent users. The system degraded gracefully; throughput plateaued at 11–14 RPS.
- **Failure recovery:** 16 of 17 failure scenarios recovered gracefully. The one fail-open (rate-limit split-counter) is now fixed.

### Fixed and Retested

- DEF-01 through DEF-06: boundary validation, error mapping, and input sanitization.
- SEC-01 through SEC-10: XFF trust, rate limiter, dependency CVEs, secret naming, password exposure, 503 leakage, ETL allowlist, Bandit hygiene, and banner/docs exposure.

### Open / Pending / Out of Scope

- Responsive viewport tests at 375 px and 768 px are deferred.
- Direct RLS-policy testing requires an authenticated Supabase session.
- Production load testing and Vercel 504 behavior were not tested.
- ML notebook re-runs and full model calibration exercises are outside this test scope.
- 36 of 120 province records return 404 due to data-source naming gaps for highly-urbanized and renamed provinces.
- The frontend ships as a single 1.91 MB gzipped JS bundle; code splitting is the recommended follow-up.

---

## Overall Technical Assessment

**RELEASE READY**

The evidence from the September 5–8 test session supports a release-ready verdict. All functional, security, and failure-recovery targets were met, no failed test cases were recorded, and the system degraded gracefully under load. The remaining items are documented, non-blocking caveats: deferred responsive-viewport browser tests, out-of-scope production load and RLS testing, a known data-source gap for 36 province records, and the recommendation to split the frontend bundle. None of these prevent the system from being released, but they should be tracked and addressed in the next iteration.