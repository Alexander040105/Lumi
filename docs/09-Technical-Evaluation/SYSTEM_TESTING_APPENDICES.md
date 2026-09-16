# **Title :** LUMI System Testing — Appendices A–E

Group Name : \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Technical Evaluators ( IT Experts ) \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Project:** LUMI — Data-Driven Environmental Intelligence System
**Companion to:** `SYSTEM_TESTING_REPORT.md` (§24 evidence index) · evaluation date 2026-09-15 (fresh re-execution), historical baseline September 5–8, 2026
**Artifact root:** `docs/09-Technical-Evaluation/artifacts/` — every table below cites the file that produced it. `rerun-2026-09-15/` = the fresh run.

---

## Appendix A – Test Case Documentation

*Complete record of every test case executed in the fresh 2026-09-15 cycle, plus the manual test kit.*

### A.1 Automated test suites (per-file)

**Backend suite** — `pytest fastapi-backend/tests -v` → `rerun-2026-09-15/functional/pytest-backend.txt` — **106 collected · 104 passed · 2 failed**

| Test file | Cases | Result |
|---|---:|---|
| `test_calibration.py` | 19 | all pass |
| `test_catchment_enrichment.py` | 21 | all pass |
| `test_ecosim_explanations.py` | 3 | all pass |
| `test_ecosim_quezon.py` | 6 | all pass |
| `test_regression.py` | 5 | all pass |
| `test_routes.py` | 9 | all pass |
| `test_security_fixes.py` | 29 | 27 pass · **2 fail** — `TestETLTableAllowlist::test_validate_table_rejects_injection_names`, `::test_validate_table_accepts_allowed_table` (missing async plugin → BUG-01) |
| `test_wind_hydro_plants.py` | 14 | all pass |

**LUMI unit suite** — `pytest tests/tests/unit -v` → `pytest-lumi-unit.txt` — **177 collected · 177 passed**

| Test file | Cases | Coverage area |
|---|---:|---|
| `test_ai_service.py` | 18 | prompt construction, JSON normalization, RAG retrieval, error handling, Gemini imports |
| `test_geothermal_calculations.py` | 56 | haversine distance, suitability scoring, geothermal plant lookups |
| `test_ml_preprocessing.py` | 22 | feature engineering, lag/rolling construction |
| `test_new_improvements.py` | 18 | forecasting helpers incl. SARIMA config selection |
| `test_rag_embeddings_client.py` | 5 | embeddings client |
| `test_rag_pgvector_store.py` | 5 | pgvector store |
| `test_renewable_calculations.py` | 53 | solar/wind/hydro calculation correctness |

**LUMI integration suite** — `pytest tests/tests/integration -v` → `pytest-lumi-integration.txt` — **99 collected · 66 passed · 1 failed · 32 skipped**

| Test file | Cases | Notes |
|---|---:|---|
| `test_api.py` | 26 | endpoint contracts; environment-dependent cases skipped where services absent |
| `test_database.py` | 30 | DB integration; skips where live writes/credentials not provisioned |
| `test_pipeline.py` | 30 | ETL pipeline paths |
| `performance_test.py` | 13 | **1 fail:** `test_health_endpoint_response_time` — 555.4 ms vs 500 ms threshold under concurrent suite load (standalone mean 10.9 ms → BUG-04) |

**Frontend suite** — `vitest run` in `react-frontend/` → `vitest-frontend.txt` — **4 files · 13 tests · all pass**

| Test file | Cases | Duration |
|---|---:|---|
| `src/__tests__/I18nProvider.test.jsx` | 4 | 83 ms |
| `src/__tests__/theme-contrast.test.js` | 3 | 6 ms |
| `src/components/__tests__/DashboardChart.test.jsx` | 2 | 55 ms |
| `src/utils/ecosimPdf.test.js` | 4 | 141 ms |

> Every individual test name and verdict is in the referenced `.txt` logs (run with `-v`).

### A.2 API endpoint sweep — 82 cases (`endpoint_sweep.csv/.jsonl`, `sweep_log.txt`)

| Case group | Checks | Verdict |
|---|---:|---|
| TC-API — health & meta | 2 | pass |
| TC-ES — EcoSim | 13 | pass |
| TC-EH — EnergyHub | 21 | pass |
| TC-GEO — geothermal | 5 | pass |
| TC-GS — geospatial | 7 | pass |
| TC-MAP — map services | 8 | pass |
| TC-PROD — products | 5 | pass |
| TC-FC — forecast | 5 | **2 pass / 3 fail** — `GET /forecast/run`, `/forecast/backtest`, `/forecast/models` returned 401: sweep expected public access, routes now require authentication (verified correct — authenticated sweep returns 200; stale expectation, BUG-06) |
| TC-AUTH — auth boundaries | 6 | pass |
| TC-ADM — admin endpoints | 6 | pass |
| TC-SEC-INJ — injection probes | 4 | pass |

**Total: 82 checks · 79 pass · 3 fail (all stale-expectation 401s, not application defects).**

### A.3 Security probe cases — 16/16 pass (`security/probes.json`, `probes_log.txt`)

| ID | Check | Observed |
|---|---|---|
| SEC-AUTH-01 | No token → `/protected/me` | HTTP 401 `Missing token` |
| SEC-AUTH-02 | Malformed token | HTTP 401 `Invalid token` |
| SEC-AUTH-03 | `alg=none` JWT | HTTP 401 `Invalid token` |
| SEC-AUTH-04 | Wrong-signature JWT | HTTP 401 `Invalid token` |
| SEC-AUTH-ADM ×3 | Bad token → `/admin/users`, `/admin/analytics`, `/admin/config` | HTTP 401 each |
| SEC-HDR-01 | Security headers present | 5/5 present, 0 missing |
| SEC-HDR-02 | Server banner disclosure | `server='Lumi'` (masked) |
| SEC-CORS-allowed | Preflight `http://localhost:5173` | 200, correct `ACAO` |
| SEC-CORS-regex-allowed | Preflight `https://lumi-frontend-abc.vercel.app` | 200, regex match works |
| SEC-CORS-disallowed | Preflight `https://evil.example.com` | 400, no `ACAO` |
| SEC-DOCS ×3 | `/docs`, `/openapi.json`, `/redoc` | HTTP 404 each |
| SEC-ERR-01 | Error-body leak check (`/geothermal/999999`) | 404 `{"detail":"Municipality not found"}` — no internals |

Plus the live rate-limit regression retest (`security/ratelimit_live.json`): 70/70 spoofed `X-Forwarded-For` requests correctly throttled to 429 — SEC-01 stays fixed.

### A.4 Defect retest cases (`functional/defect_retests.json`)

| Case | Steps | Observed | Verdict |
|---|---|---|---|
| DEF-01 retest | `GET /geothermal/999999` | 404 `{"detail":"Municipality not found"}` — clean error, no internals | Verified fixed |
| DEF-02 retest | `GET /map` with invalid renewable type | 422 `literal_error` | Verified fixed |
| DEF-03 retest | `GET /forecast` with bogus metric | 422 `literal_error` on public route; 401 on auth-gated `/forecast/*` | Verified fixed |
| DEF-04 retest | `GET /forecast/run` with injection payload | 401 auth gate → then 422; injection cannot reach handler | Verified fixed |
| DEF-05 retest | `GET /products/recommend` with `' OR '1'='1` in `energy_type` | 422 allowlist rejection, input not echoed | Verified fixed |
| DEF-06 retest | AI-quota message text inspection (`energyhub.py:134`) | Message reads "continue using EnergyHub" | Verified fixed |
| Health retime | `/health` timed standalone | min 6.4 / mean 10.9 / max 16.6 ms | Pass |

### A.5 Database read-only checks — 14 cases (`db/supabase_readonly_checks.json`)

| Check | Observed | Meaning |
|---|---|---|
| `regions` count | 200 — `0-17/18` | 18 regions readable |
| `provinces` count | 200 — `0-119/120` | 120 provinces readable |
| `municipalities` count | 206 — `0-999/1813` | 1,813 rows (paginated) |
| `barangays` count | 206 — `0-999/53460` | 53,460 rows |
| `municipality_climate_monthly` count | 206 — `0-999/334584` | 334,584 rows |
| `hydropower_suitability` count | 206 — `0-999/1600` | 1,600 rows |
| `geothermal_suitability` count | 206 — `0-999/1813` | 1,813 rows |
| `ml_model_registry` count | 401 | anonymous read denied |
| RLS `profiles` | 401 `42501` — "permission denied" | RLS enforced |
| RLS `saved_simulations` | 401 `42501` | RLS enforced |
| RLS `admin_audit_log` | 401 `42501` | RLS enforced |
| RLS `user_ecosim_logs` | 200, 0 rows | public table exists, empty to anon |
| `simulations` (guessed name) | 404 `PGRST205` | table does not exist under that name |
| `api_usage_logs` (guessed name) | 404 `PGRST205` | table does not exist under that name |

All checks read-only — no writes were attempted or performed.

### A.6 Generative-AI checks (`llm/llm_eval.json`)

| Case | Result |
|---|---|
| Live analysis calls (n=6) | 100% non-empty, 100% sanitizer-survival, 100% required-heading compliance, 100% prescriptive extraction |
| JSON-mode probe (n=4) | 0% valid JSON — expected: prompt requests markdown (doc/comment mismatch → BUG-09) |
| Gemini→Groq fallback | injected Gemini failure → Groq response in 1,919.7 ms |
| Hard timeout | 0.5 s budget → empty return at 504.1 ms, caller fallback verified |
| Token usage sample | 571 prompt + 450 completion = 1,021 tokens |

### A.7 Manual test-case index

The complete manual test kit lives in `SYSTEM_TESTING_FORM_LUMI_v2.md` (executable step tables). Index of all manual case IDs:

| Block | IDs | Cases |
|---|---|---|
| Public pages & navigation | FT-001 … FT-007 | 7 |
| Accounts (sign-up/login/logout/MFA/reset) | AC-001 … AC-009 | 9 |
| EcoSim flow | FT-010 … FT-016 | 7 |
| EnergyHub dashboard & map | FT-017 … FT-025 | 9 |
| Saved data & account pages | FT-026 … FT-033 | 8 |
| Admin console | AD-001 … AD-010 | 10 |
| Input validation | IV-001 … IV-012 | 12 |
| Persistence & privacy | DP-001 … DP-006 | 6 |
| AI & connected services | AI-001 … AI-006 | 6 |
| Performance observation | PT-001 … PT-009 | 9 |
| Observable security | SO-001 … SO-014 | 14 |
| Compatibility matrix | 8 rows (§14) | 8 |
| Usability tasks | UAT-1 … UAT-5 | 5 |
| SUS questionnaire | 10 statements (§15.2) | 10 |
| Usability observations | 6 criteria (§15.4) | 6 |
| Regression retests | REG-01 … REG-06 | 6 |
| **Manual total** | | **132** |

---

## Appendix B – Screenshots of Testing

**Generated captures live in `artifacts/screenshots/` as `B-01…B-24.png`** — produced 2026-09-16 by `artifacts/scripts/make_screenshots.py`, which renders the verbatim recorded run outputs (and the live `curl -i` captures in `artifacts/live_captures/`) as terminal-style images; `B-14` is a real headless-Edge capture of the Locust HTML report and `B-19` is the forecast chart itself. The table below remains as the reproduction recipe for each slot.

**Setup once:** `cd fastapi-backend` then `.\.venv\Scripts\activate`; start the API with `uvicorn main:app --port 8000` (leave it running; a second terminal runs the commands).

| Slot | Required evidence type | Run / open | What to screenshot |
|---|---|---|---|
| B-01 | Successful execution | `cd tests` → `pytest tests/unit -v` | Tail of output showing `177 passed` |
| B-02 | Successful execution | `cd fastapi-backend` → `python -m pytest tests -v` | Summary `104 passed, 2 failed` + suite list |
| B-03 | Successful execution | `cd tests` → `pytest tests/integration -v` | `66 passed, 1 failed, 32 skipped` summary |
| B-04 | Successful execution | `cd react-frontend` → `npx vitest run` | `Test Files 4 passed · Tests 13 passed` |
| B-05 | Successful execution | `python docs/09-Technical-Evaluation/artifacts/scripts/endpoint_sweep.py` (backend on :8000) | Sweep summary line `79/82 pass` (or equivalent tally) |
| B-06 | Successful execution | `python docs/09-Technical-Evaluation/artifacts/scripts/security_probes.py` | `16/16 PASS` block |
| B-07 | Failed test case | same run as B-02 — scroll to `TestETLTableAllowlist` | The two FAILED lines + `async def functions are not natively supported` message |
| B-08 | Failed test case | `cd tests` → `pytest tests/integration/performance_test.py -v` | `test_health_endpoint_response_time` failure (555.4 ms > 500 ms) — may pass standalone; if it passes, screenshot `pytest-lumi-integration.txt` line instead |
| B-09 | Failed test case / error message | `curl -i http://127.0.0.1:8000/forecast/run` (no token) | `HTTP/1.1 401` + `{"detail":"Missing token"}` — the stale-expectation fails |
| B-10 | Error message (clean) | `curl -i http://127.0.0.1:8000/geothermal/999999` | `404 {"detail":"Municipality not found"}` — sanitized error (DEF-01 fix) |
| B-11 | Error message (validation) | `curl -i "http://127.0.0.1:8000/products/recommend?energy_type=' OR '1'='1"` | `422 literal_error` — injection refused |
| B-12 | Error message (throttling) | `python docs/09-Technical-Evaluation/artifacts/scripts/security_probes.py` (rate-limit section) or rapid-repeat `curl /health` ×70 | `429 Too Many Requests` responses |
| B-13 | Successful execution (load) | `cd docs/09-Technical-Evaluation/artifacts/load` → `locust -f locustfile.py --headless -u 25 -r 5 -t 120s --host http://127.0.0.1:8000` | Terminal stats table (1,155 reqs, 0 failures) |
| B-14 | Successful execution (load, visual) | open `docs/09-Technical-Evaluation/artifacts/rerun-2026-09-15/load/u25.html` in a browser | Locust charts page (requests/failures/response-time graphs) |
| B-15 | Failed case (tooling) | `docs/…/rerun-2026-09-15/load/locust_log.txt` (open in editor) | `CRITICAL … StatsCSVFileWriter … I/O operation on closed file` trace — BUG-05 |
| B-16 | Error message (audit) | `cd fastapi-backend` → `.\.venv\Scripts\pip-audit` | Vulnerability table (66 findings) — BUG-02 |
| B-17 | Error message (audit) | `cd react-frontend` → `npm audit` | Advisory list incl. critical plotly.js/maplibre-gl — BUG-03 |
| B-18 | Successful execution (ML) | `python docs/09-Technical-Evaluation/artifacts/scripts/evaluate_forecasting_models.py` | Console summary of model metrics + CV table |
| B-19 | Successful execution (ML, visual) | open `docs/09-Technical-Evaluation/artifacts/rerun-2026-09-15/ml/forecast_plot.png` | The forecast-vs-actual chart itself |
| B-20 | Successful execution (LLM) | `python docs/09-Technical-Evaluation/artifacts/scripts/llm_groq_eval.py` (needs `.env` loaded) | `llm_eval` JSON summary (latency block, 100% contract rows) |
| B-21 | Corrective action evidence | `git log --oneline` filtered to fix commits for DEF-01–06 / SEC-01–10 | The commit list proving corrective actions landed |
| B-22 | Retesting results | `python` retest of defect endpoints — or open `rerun-2026-09-15/functional/defect_retests.json` in an editor | The JSON showing all five defect retests with clean statuses |
| B-23 | Successful execution (build) | `cd react-frontend` → `npm run build` | `✓ built` line **plus** the >500 kB chunk-size warning (BUG-07 evidence) |
| B-24 | Successful execution (benchmark) | `python docs/09-Technical-Evaluation/artifacts/scripts/benchmark.py` | Latency table (`/health` ~3.6 ms mean, `/energyhub/overview` ~5.5 ms) |

**Screenshot-to-worksheet mapping:** Successful test execution → B-01…06, B-13/14, B-18…20, B-23/24 · Failed test cases → B-07…09, B-15 · Error messages → B-09…12, B-15…17 · Corrective actions → B-21 · Retesting results → B-10/11/22 (defect retests), B-12 (SEC-01 rate-limit regression), B-03 (suite regression).

---

## Appendix C – System Logs

### C.1 Application logs

**Backend boot + request log** — `rerun-2026-09-15/functional/backend_boot.log` (structured JSON lines). Excerpt (startup, 2026-09-16 00:23:52):

```json
{"logger":"uvicorn.error","message":"Started server process [2640]"}
{"logger":"main","message":"CORS allow_origins: ['http://localhost:5173','https://lumi-frontend-xi.vercel.app']"}
{"logger":"main","message":"GROQ_API_KEY configured: True"}
{"logger":"main","message":"GEMINI_API_KEY configured: True"}
{"logger":"main","message":"Anonymous EcoSim quota: 1 requests per 86400 seconds"}
{"logger":"main","message":"Supabase and Redis sync clients pre-initialized on startup."}
{"logger":"main","message":"RAG_BACKEND=pgvector; FAISS index is not built at startup."}
{"logger":"uvicorn.error","message":"Application startup complete."}
{"logger":"lumi.request","message":"request","method":"GET","path":"/","status_code":200,"duration_ms":0.51}
```

Second instance log: `rerun-2026-09-15/security/backend_8001.log` (port-8001 instance used for the rate-limit retest).

### C.2 API logs

- `rerun-2026-09-15/functional/endpoint_sweep.jsonl` — one JSON record per probed endpoint (id, method, path, expected, status, latency_ms, verdict, response snippet). 82 records.
- `rerun-2026-09-15/functional/sweep_log.txt` — sweep console transcript.

### C.3 Error logs

**Pytest failures** — `pytest-backend.txt`:

```text
tests\test_security_fixes.py::TestETLTableAllowlist::test_validate_table_rejects_injection_names FAILED [85%]
tests\test_security_fixes.py::TestETLTableAllowlist::test_validate_table_accepts_allowed_table FAILED [86%]
→ async def functions are not natively supported. Install a plugin: anyio / pytest-asyncio / …
```

`pytest-lumi-integration.txt`: `test_health_endpoint_response_time` — measured 555.4 ms against a 500 ms ceiling under concurrent suite load.

**Locust stats-writer error** — `rerun-2026-09-15/load/locust_log.txt` (post-run, non-fatal; stats were already captured):

```text
[00:31:21] AKIII/CRITICAL/locust.main: Unhandled exception in greenlet: StatsCSVFileWriter.stats_writer
ValueError: I/O operation on closed file.
```

**Load failures:** `u25_failures.csv` and `u25_exceptions.csv` — both empty (0 request failures at 25 users).

### C.4 Database logs

`rerun-2026-09-15/db/supabase_readonly_checks.json` — 14 REST access records (public counts return `content-range` totals; protected tables return `401`/`42501` permission-denied; two guessed table names return `404`/`PGRST205`). Note: engine-level PostgreSQL logs are not exposed to the anonymous API key — this file is the access-log evidence within read-only scope.

### C.5 Performance logs

- `rerun-2026-09-15/perf/summary.json` + `latency.csv` — 23 endpoints × 30 samples (e.g., `/health` mean 3.6 ms; `/energyhub/overview` mean 5.5 ms; `/health/detailed` mean 260.7 ms).
- `rerun-2026-09-15/perf/benchmark_log.txt` — benchmark console transcript.
- `rerun-2026-09-15/perf/vite-build.txt` — Vite build output incl. 6.42 MB chunk warning.
- `rerun-2026-09-15/load/locust_log.txt` — ramp to 25 users, 120 s run, shutdown.

### C.6 Script run logs

`rerun-2026-09-15/ml/run_log.txt` (full ML evaluation trace) · `rerun-2026-09-15/llm/run_log.txt` (live Groq calls).

---

## Appendix D – Test Environment

### D.1 Hardware

| Item | Specification |
|---|---|
| CPU | Intel Core i5-8400 @ 2.80 GHz (6 cores) |
| RAM | ~8 GB |
| Storage | 480 GB SSD |
| OS | Windows 11 Pro for Workstations, build 26200 |
| Hostname (logs) | AKIII |

### D.2 Software & toolchain (`artifacts/tool-versions.txt` + measured)

| Component | Version |
|---|---|
| Python | 3.13.2 (`fastapi-backend/.venv`) |
| Node.js / npm | v24.15.0 / 11.12.1 |
| pytest | 9.1.1 (unit/integration venv), plugins: anyio 4.14.2, benchmark 5.3.0, mock 3.15.1 |
| Locust | 2.46.5 |
| pip-audit / Bandit | 2.10.1 / 1.9.4 |
| Uvicorn | 0.30.6 (single worker) |
| FastAPI | per `fastapi-backend` requirements |
| statsmodels / scikit-learn / pandas | 0.14.6 / 1.9.0 / 3.0.5 |
| groq (Python SDK) | 0.18.0 |
| Vitest | per `react-frontend` (Vite + React 18) |

### D.3 Services & configuration

| Service | Detail |
|---|---|
| Backend | FastAPI + Uvicorn, `127.0.0.1:8000` (and :8001 for the rate-limit retest) |
| Database | Supabase PostgreSQL (cloud) — anonymous-key, read-only access for checks |
| Cache | Upstash Redis (pre-initialized at startup per boot log) |
| LLM providers | Groq `groq/compound-mini` (default), Gemini fallback; `GROQ_API_KEY`/`GEMINI_API_KEY` configured = True |
| Frontend build | Vite (`react-frontend`), production bundle 6.42 MB main chunk |
| RAG backend | pgvector; FAISS index not built at startup |

---

## Appendix E – Defect Documentation

### E.1 Corrective-action records — closed defects (Sept 5–8 cycle → fresh retest 2026-09-15)

| ID | Description | Severity | Corrective action | Retest evidence | Status |
|---|---|---|---|---|---|
| DEF-01 | `/geothermal/999999` leaked 500 internals | Medium | Sanitized error responses | 404 `{"detail":"Municipality not found"}` (`defect_retests.json`) | **Closed — verified** |
| DEF-02 | `/map` accepted invalid renewable type | Low | Literal-type validation | 422 `literal_error` | **Closed — verified** |
| DEF-03 | `/forecast` accepted bogus metric | Low | Literal-type validation + auth gate | 422 public / 401 gated | **Closed — verified** |
| DEF-04 | `/forecast/run` accepted injection silently | Low | Auth gate + validation | 401 → injection unreachable | **Closed — verified** |
| DEF-05 | `/products/recommend` unvalidated `energy_type` | Low | Allowlist validation | 422, input not echoed | **Closed — verified** |
| DEF-06 | AI-quota message named wrong product | Trivial | Copy fix `energyhub.py:134` | Message reads "continue using EnergyHub" | **Closed — verified** |
| SEC-01 | XFF spoofing → rate-limit bypass | High | Trust platform headers/direct peer only | `ratelimit_live.json`: 70/70 spoofed → 429 | **Closed — verified** |
| SEC-02–03, 05–10 | split counters, fail-open status, `VITE_` secrets, temp_password leak, 503 leak, ETL interpolation, Bandit lows, banner/docs exposure | Med–Info | respective fixes | merged-counter tests pass; docs 404; banner `Lumi`; Bandit 0 issues/16,960 LOC | **Closed — verified** |

### E.2 Reopened item

| ID | History | Finding | Disposition |
|---|---|---|---|
| SEC-04 | Sept report claimed clean dependency audits ("0 vulnerabilities") | Fresh 2026-09-15 audits: **66 backend + 4 frontend advisories** — the claim no longer holds | **Reopened → tracked as BUG-02 / BUG-03** |

### E.3 Open bug reports — found by this evaluation

| ID | Module | Severity | Priority | Description | Evidence | Corrective action | Status |
|---|---|---|---|---|---|---|---|
| BUG-01 | Test infra | Medium | Med | `TestETLTableAllowlist` 2 tests fail — no async plugin (`pytest-asyncio`) in backend venv; `async def` tests cannot execute | `pytest-backend.txt` trace | install pytest-asyncio or convert tests to sync | Open |
| BUG-02 | Backend deps | **High** | **High** | pip-audit: **66 vulnerabilities** across pillow, starlette, transformers, python-jose, python-dotenv, ecdsa | `security/pip-audit-env.txt` | upgrade pillow≥12.2, starlette≥0.40, python-jose≥3.4.0, python-dotenv≥1.2.2; ecdsa no fix — monitor/scope | Open |
| BUG-03 | Frontend deps | **High** | **High** | npm audit: 4 vulns — **critical** maplibre-gl (via plotly.js) & plotly.js; moderate vitest/@vitest/mocker | `security/npm-audit-frontend.json` | major bump plotly.js→4.1.1, vitest→5.x | Open |
| BUG-04 | Test stability | Low | Low | `test_health_endpoint_response_time` flaky under concurrent suite load (555 ms > 500 ms; standalone 10.9 ms) | `pytest-lumi-integration.txt`, `defect_retests.json` | isolate perf test or raise threshold | Open |
| BUG-05 | Tooling | Low | Low | Locust `StatsCSVFileWriter` closed-file error post-run (stats still captured) | `load/locust_log.txt` | Locust 2.46.5/Windows artifact — cosmetic | Open |
| BUG-06 | Docs/sweep | Medium | Med | Stale expectations & metrics: sweep assumes `/forecast/*` public (now authed); Sept CSV carried "placeholder" SARIMAX/RF rows; Sept "0 vulns" audits contradicted | `endpoint_sweep.csv`, `model_comparison_results.csv`, audit files | update sweep expectations + comparison CSV + audit notes | Open |
| BUG-07 | Frontend perf | Medium | Med | Main bundle 6.42 MB (1.93 MB gzip) + 1 MB pdfmake chunk | `perf/vite-build.txt` | route-level code-splitting; lazy-load pdfmake/plotly | Open |
| BUG-08 | LLM config | Medium | Med | Configured Groq fallback `qwen/qwen3.6-27b` → HTTP 404 for this account | `llm/llm_eval.json` | prune/replace fallback model list | Open |
| BUG-09 | LLM contract | Low | Low | `groq_client.py` comments claim forced-JSON output; observed output is markdown prose (0/4 JSON validity when probed) — hazardous if a consumer assumes JSON | `llm/llm_eval.json → json_mode` | fix comments or enforce `response_format` | Open |

### E.4 Defect summary

| Group | Count | State |
|---|---:|---|
| Historical defects DEF-01…06 | 6 | all closed — retest-verified |
| Security fixes SEC-01…10 | 10 | 9 verified · SEC-04 reopened (→ BUG-02/03) |
| New defects BUG-01…09 | 9 | all open — handed to the team |
