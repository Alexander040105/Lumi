# **TECHNICAL TESTING REPORT — LUMI Evaluation Form**

**Title:** LUMI — Data-Driven Environmental Intelligence System
**Group Name:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
**Technical Evaluators (IT Experts):** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
**Form Version:** 1.0 (adapted to the LUMI repository, 2026-09-16)

> **How to use this form.** This is the generic System Testing worksheet rewritten for LUMI: every module, test case, endpoint, and threshold below is real and traced to this repository. Pre-filled cells contain verified facts — leave them unless the code changed. Blank cells (`____` / Pass-Fail) are yours to complete by running the instruments in Appendix A. Items marked **Reserved** need resources outside a code-only environment (browser rig, physical devices, human users, or write access) — keep them on the manual checklist rather than guessing a result.

---

## **1. Document Information**

| Item | Details |
|---|---|
| **Project/System Name** | LUMI |
| **Project Title** | LUMI — Data-Driven Environmental Intelligence System |
| **Version** | 0.1.0 (`package.json`) |
| **Testing Date** | \_\_\_\_\_\_ |
| **Testing Environment** | Windows 11 Pro for Workstations (b26200) · i5-8400 @ 2.80 GHz · ~8 GB RAM · 480 GB SSD · Python 3.13.2 · Node 24.15.0 · live Supabase + Groq/Gemini keys via `.env` |
| **Tested By** | \_\_\_\_\_\_ |
| **Developer/Team** | LUMI Development Team |
| **Test Report Version** | \_\_\_\_\_\_ |
| **Status** | ☐ Draft ☐ Final |

---

## **2. Executive Summary**

### **2.1 Purpose of Testing** *(pre-filled)*

This report presents the procedures, test cases, results, identified defects, corrective actions, and overall assessment of LUMI — covering functional, technical, performance, security, usability, compatibility, and reliability requirements.

### **2.2 Testing Objectives** *(pre-filled)*

1. Verify all major functions operate to spec. 2. Identify defects. 3. Evaluate performance under defined load. 4. Verify compatibility (manual pass). 5. Assess security/access control. 6. Verify database operations and integrity (read-only). 7. Evaluate against ISO/IEC 25010. 8. Confirm fixed defects stay fixed. 9. Determine deployment readiness.

### **2.3 Result Summary** *(fill after execution)*

| Activity | Result |
|---|---|
| Backend pytest (`fastapi-backend/tests`) | ____ |
| Unit suite (`tests/tests/unit`) | ____ |
| Integration suite (`tests/tests/integration`) | ____ |
| Frontend Vitest | ____ |
| Endpoint sweep (82 checks) | ____ |
| Security probes | ____ |
| Read-only database checks | ____ |
| Load test | ____ |
| Dependency audits | ____ |
| SAST (Bandit) | ____ |
| Production build | ____ |

---

## **3. System Overview**

### **3.1 System Description** *(pre-filled)*

**System Name:** LUMI

**Description:** Full-stack web system: **EcoSim** (household renewable-energy simulation per municipality), **EnergyHub** (national DOE/IRENA analytics + ARIMA forecasts), geospatial map services (PSGC hierarchy, climate, suitability layers), a generative-AI recommendation layer (Groq primary, Gemini fallback), and authenticated features (saved simulations, profile, MFA, chat, admin console). Stack: FastAPI + Uvicorn, Supabase (PostgreSQL + Auth + RLS), Upstash Redis, React 18 + Vite + Tailwind/shadcn + Leaflet.

### **3.2 Intended Users** *(pre-filled)*

| User Type | Description | Access Level |
|---|---|---|
| Administrator | User CRUD/ban/role/reset, analytics, config, chat audit | Full — `/admin/*` |
| Registered user | Simulations, AI insights, forecasts, chat, profile/MFA | Authenticated — `/protected/*`, `/forecast/*`, `/simulations`, `/ecosim` POST, `/chat` |
| Guest | Public dashboards, maps, plant data, product browse | Public GET endpoints |

### **3.3 Major System Modules** *(pre-filled — the real route inventory)*

| No. | Module | Description |
|---|---|---|
| 1 | Auth & Account (`protected.py`) | `/me`, `/profile`, avatar sync, session, account deletion |
| 2 | EcoSim (`ecosim.py`) | Simulation GET/POST, `/ai`, municipalities/provinces/barangays |
| 3 | EnergyHub (`energyhub.py`) | overview, forecast, trends, map-data, source/grid breakdowns, model-comparison, demand, IRENA, meralco-rate, solar-atlas, ai-insight, analyze-chart, map-explanation |
| 4 | Forecast (`forecast.py`) | `/run`, `/backtest`, `/models` — login-gated (`_require_forecast_access`) |
| 5 | Geospatial & Map (`geospatial.py`, `map.py`) | centroids, climate (+hierarchy fallback, province-aggregate), PSGC hierarchy, coverage, `/{renewable_type}` |
| 6 | Geothermal (`geothermal.py`) | plants catalog, `/{municipality_id}` analysis, EcoSim params |
| 7 | Products (`products.py`) | `/recommend`, `/browse`, `/audit` |
| 8 | Simulations (`simulations.py`) | saved-simulation CRUD |
| 9 | Chat (`chat.py`) | sessions + history (authenticated) |
| 10 | Admin (`admin.py`) | 17 endpoints: users, analytics, config, chat flags, usage, logs |
| 11 | ETL (`etl.py`) | `/run/climate`, `/lineage`, `/validate` |
| 12 | Health (`health.py`) | `/health`, `/health/detailed` (supabase/redis/rag checks) |
| 13 | AI services (`services/llm_client.py`, `groq_client.py`, `gemini_funcs.py`) | provider abstraction, fallbacks, sanitization, timeout |

---

## **4. Testing Scope**

### **4.1 In-Scope** *(pre-filled)*

Auth enforcement · all REST endpoints · input validation · injection handling · rate limiting · security headers/CORS · read-only DB integrity + RLS · performance benchmarks · load test · dependency/SAST audits · LLM behavior · production build · automated suites · defect regression.

### **4.2 Reserved for Manual Verification** *(pre-filled — needs resources outside this environment)*

- Real-browser matrix + physical devices — requires a browser/device rig.
- Human usability/UAT — requires participants.
- Screenshots — machine-readable artifacts stand in.
- Database **writes** — read-only constraint; use a disposable test project for the write pass.
- Admin/destructive operations on live data.

---

## **5. Testing Methodology**

Process: **Requirements → Test Planning → Test Case Development → Execution → Defect Identification → Correction → Retesting → Final Evaluation**

| Testing Type | Purpose | Performed? |
|---|---|---|
| Unit Testing | Components in isolation | ☐ yes — `tests/tests/unit` |
| Integration Testing | Module interactions | ☐ yes — `tests/tests/integration` |
| System Testing | Whole system end-to-end | ☐ yes — endpoint sweep |
| Functional Testing | Required functions | ☐ yes — §8 |
| Usability Testing | Ease of use | ☐ partial — code-level; UAT reserved |
| Performance Testing | Response/processing | ☐ yes — §12 |
| Security Testing | Vulnerabilities | ☐ yes — §13 |
| Compatibility Testing | Environments | ☐ reserved — needs rig |
| Database Testing | Data ops/integrity | ☐ read-only pass |
| API Testing | Requests/responses | ☐ yes — §8/§11 |
| Regression Testing | Fixes hold | ☐ yes — §19 |
| User Acceptance | User requirements | ☐ reserved — needs users |

---

## **6. Test Environment** *(pre-filled)*

### **6.1 Hardware**

| Component | Specification |
|---|---|
| Processor | Intel Core i5-8400 @ 2.80 GHz (6 cores) |
| RAM | ~8 GB |
| Storage | 480 GB SSD |
| Display | ____ (record your rig) |
| Network | live internet (Supabase/Groq/Gemini reachable) |

### **6.2 Software**

| Software | Version |
|---|---|
| OS | Windows 11 Pro for Workstations, build 26200 |
| Language/runtime | Python 3.13.2 · Node.js 24.15.0 |
| Backend framework | FastAPI 0.115.0 + Uvicorn |
| Frontend framework | React 18 + Vite 6.4.3 |
| Database | Supabase (PostgreSQL + PostgREST + RLS) — read-only access |
| Cache | Upstash Redis (+ in-memory fallback) |
| AI services | Groq `groq/compound-mini` (groq 0.18.0) · Gemini fallback |
| Test tooling | pytest 9.1.1 · Vitest · Locust 2.46.5 · Bandit 1.9.4 · pip-audit 2.10.1 · httpx 0.27.2 |
| Browser | ____ (record on manual pass) |

---

## **7. Test Data** *(pre-filled — verify on your run)*

| Data Category | Description | Records |
|---|---|---|
| DOE dataset | `master_preprocessed.csv`, annual national stats | 23 rows × 45 cols |
| Geography (live, read-only) | PSGC chain | regions 18 · provinces 120 · municipalities 1,813 · barangays 53,460 |
| Climate | `municipality_climate_monthly` | 334,584 |
| Suitability | hydropower / geothermal | 1,600 / 1,813 |
| Forecast artifacts | precomputed forecast + comparison CSVs | 6-year horizon |
| Test users | ____ (create on a disposable project if a write pass is authorized) | ____ |

---

## **8. Functional Test Cases**

*(Instrument: `artifacts/rerun-*/scripts/endpoint_sweep.py` produces the full 82-check matrix — IDs below match it. Fill Actual Result + Status.)*

| Test ID | Module | Test Description | Expected | Actual | Status |
|---|---|---|---|---|---|
| TC-API-001 | Health | `GET /health` | 200 `{status:ok}` | ____ | ☐P ☐F |
| TC-API-001b | Health | `GET /health/detailed` | 200 + dep checks | ____ | ☐P ☐F |
| TC-ES-001 | EcoSim | `GET /ecosim/municipalities` | 200, items > 0 | ____ | ☐P ☐F |
| TC-ES-001b | EcoSim | `GET /ecosim/provinces` | 200, items > 0 | ____ | ☐P ☐F |
| TC-ES-002 | EcoSim | `GET /ecosim/` (valid params) | 200 computed result | ____ | ☐P ☐F |
| TC-ES-003 | EcoSim | `POST /ecosim/` (valid body) | 201 created | ____ | ☐P ☐F |
| TC-ES-004 | EcoSim | `GET /ecosim/ai` | 200 AI narrative | ____ | ☐P ☐F |
| TC-EH-001 | EnergyHub | `GET /energyhub/overview` | 200 | ____ | ☐P ☐F |
| TC-EH-004/005 | EnergyHub | `GET /energyhub/forecast` (consumption / peak_demand) | 200 + `ci_lower`/`ci_upper` | ____ | ☐P ☐F |
| TC-EH-006–009 | EnergyHub | trends, map-data, source-breakdown, grid-breakdown | 200 | ____ | ☐P ☐F |
| TC-EH-010 | EnergyHub | `GET /energyhub/forecast?metric=invalid` | 422 | ____ | ☐P ☐F |
| TC-EH-011+ | EnergyHub | model-comparison, provincial-demand, irena/*, meralco-rate, solar-atlas, map-explanation | 200 | ____ | ☐P ☐F |
| TC-EH-AI | EnergyHub | `GET /energyhub/ai-insight` | 200 or quota 401 | ____ | ☐P ☐F |
| TC-FC-001–003 | Forecast | `/forecast/run`, `/backtest`, `/models` | **401 unauthenticated** (login-gated); with valid token: 200 | ____ | ☐P ☐F |
| TC-GEO-001/002 | Geothermal | `/geothermal/plants`, `/geothermal/{id}` | 200 | ____ | ☐P ☐F |
| TC-GSP-* | Geospatial | centroids, `/climate`, hierarchy, province-aggregate | 200 | ____ | ☐P ☐F |
| TC-MAP-* | Map | `/map/psgc/hierarchy`, `/coverage`, `/map/solar` | 200 | ____ | ☐P ☐F |
| TC-PR-* | Products | `/recommend`, `/browse`, `/audit` | 200 | ____ | ☐P ☐F |
| TC-AUTH-* | Auth | `/protected/me`, `/admin/users`, `/simulations`, `/chat/sessions` — no token | 401 `Missing token` | ____ | ☐P ☐F |
| TC-INJ-* | Input security | injection strings in `metric`, `energy_type`, `renewable_type` | 4xx reject | ____ | ☐P ☐F |
| TC-ETL-* | ETL | `/etl/lineage`, `/etl/validate` | 200 or auth-gated | ____ | ☐P ☐F |

**Functional summary:** total ____ · passed ____ · failed ____ · flags explained: \_\_\_\_\_\_

---

## **9. Input Validation Testing**

| Test ID | Input Field | Test Condition | Expected | Actual | Status |
|---|---|---|---|---|---|
| IV-001 | `/energyhub/forecast?metric` | `' OR '1'='1` / `;DROP TABLE…` | 422 allowlist reject | ____ | ☐P ☐F |
| IV-002 | `/forecast/run?metric` (gated) | injection string | 401 auth wall first, then 422 | ____ | ☐P ☐F |
| IV-003 | `/map/{renewable_type}` | invalid value | 422 literal error | ____ | ☐P ☐F |
| IV-004 | `/products/recommend?energy_type` | `' OR '1'='1` | 422; input stays out of response | ____ | ☐P ☐F |
| IV-005 | `/ecosim` GET | missing required params | 422 | ____ | ☐P ☐F |
| IV-006 | `/ecosim` POST | malformed body | 422 | ____ | ☐P ☐F |
| IV-007 | `/geothermal/{id}` | nonexistent id | clean 404, internals hidden | ____ | ☐P ☐F |
| IV-008 | auth payload | empty/invalid fields | rejection message | ____ | ☐P ☐F |

---

## **10. Database Testing** *(read-only constraint — write rows reserved)*

### **10.1 Operations**

| Test ID | Operation | Expected | Actual | Status |
|---|---|---|---|---|
| DB-001 | SELECT — public tables | counts via PostgREST `count=exact` | ____ | ☐P ☐F |
| DB-002 | RLS — anon reads private tables | permission denied on `profiles`, `saved_simulations`, `admin_audit_log`, `ml_model_registry`; empty set on `user_ecosim_logs` | ____ | ☐P ☐F |
| DB-003 | INSERT | Reserved — read-only constraint (use disposable project) | ____ | — |
| DB-004 | UPDATE | Reserved — read-only constraint | ____ | — |
| DB-005 | DELETE | Reserved — read-only constraint | ____ | — |
| DB-006 | Duplicate prevention | zero duplicate year rows in modeling CSV | ____ | ☐P ☐F |

### **10.2 Integrity Checklist**

- ☐ PSGC hierarchy coherent (18 → 120 → 1,813 → 53,460)
- ☐ Suitability tables complete (geothermal = 1/municipality)
- ☐ Required fields populated in base columns
- ☐ Type consistency across derived features
- ☐ Transaction/backup verification — **Reserved** (admin-side)

---

## **11. API / External Service Testing**

| Test ID | Service | Request | Expected | Actual | Status |
|---|---|---|---|---|---|
| API-001 | Groq | live analysis call | structured markdown, all required sections | ____ | ☐P ☐F |
| API-002 | Groq | 6-call batch | non-empty, sanitized, header-compliant | ____ | ☐P ☐F |
| API-003 | Groq | 0.5 s timeout | graceful empty return → caller fallback | ____ | ☐P ☐F |
| API-004 | Fallback | inject Gemini failure | Groq answers | ____ | ☐P ☐F |
| API-005 | Groq | each configured fallback model | reachable | ____ | ☐P ☐F |
| API-006 | Supabase | anon-key reads | public yes / private denied | ____ | ☐P ☐F |
| API-007 | Redis | `/health/detailed` | `redis: ok` | ____ | ☐P ☐F |

**API checklist:** ☐ successful requests ☐ invalid handled ☐ auth verified ☐ timeouts ☐ clean errors ☐ response validation ☐ rate-limit handling ☐ service-failure fallback

---

## **12. Performance Testing**

*(Instrument: `benchmark.py` → `perf/summary.json`; thresholds pre-filled from observed baselines — adjust to your SLA.)*

| Test ID | Metric | Condition | Expected | Actual | Status |
|---|---|---|---|---|---|
| PT-001 | Read APIs (health, overview, forecast, breakdowns, plants, products) | 30 reps, single user | mean ≤ ____ ms | ____ | ☐P ☐F |
| PT-002 | Data reads (map-data, municipalities, climate, coverage, solar) | 30 reps | mean ≤ ____ ms | ____ | ☐P ☐F |
| PT-003 | Heavy computes (geothermal analysis, map-explanation, health/detailed) | 30 reps | mean ≤ ____ ms | ____ | ☐P ☐F |
| PT-004 | Simulations + AI (`/ecosim/`, `/ecosim/ai`, `ai-insight`) | 5 reps | mean ≤ ____ ms | ____ | ☐P ☐F |
| PT-005 | Concurrent users | ____ users, Locust | ____% request success | ____ | ☐P ☐F |
| PT-006 | Frontend bundle | `vite build` | builds; chunk sizes recorded | ____ | ☐P ☐F |

**Metrics block:** avg ____ · min ____ · max ____ · concurrent users ____ · error rate ____ · availability ____

---

## **13. Security Testing**

*(Instrument: `security_probes.py` → `security/probes.json` + live rate-limit run + audit commands)*

| Test ID | Area | Procedure | Expected | Actual | Status |
|---|---|---|---|---|---|
| SEC-AUTH-01–04 | Authentication | missing / malformed / `alg:none` / wrong-signature JWT on `/protected/me` | 401 ×4 | ____ | ☐P ☐F |
| SEC-AUTH-ADM | Authorization | bad token on `/admin/users`, `/analytics`, `/config` | 401/403 | ____ | ☐P ☐F |
| SEC-HDR-01 | Headers | inspect response | all security headers present | ____ | ☐P ☐F |
| SEC-HDR-02 | Banner | server header | masked (`Lumi`) | ____ | ☐P ☐F |
| SEC-CORS-* | CORS | allowed / Vercel-regex / disallowed origin | 200 / 200 / reject | ____ | ☐P ☐F |
| SEC-DOCS | Exposure | `/docs`, `/redoc`, `/openapi.json` | 404 in production mode | ____ | ☐P ☐F |
| SEC-ERR | Error leakage | force 404/422 | clean body, internals hidden | ____ | ☐P ☐F |
| SEC-RL-* | Rate limiting | 70 req ×3: normal / spoofed-loopback-XFF / public-XFF | cap enforced; spoofs rejected | ____ | ☐P ☐F |
| SEC-INJ | Injection | SQL-style strings in params | 422 allowlist reject | ____ | ☐P ☐F |
| SEC-SAST | Static scan | `bandit -r fastapi-backend/app` | findings recorded | ____ | ☐P ☐F |
| SEC-DEP-BE | Backend deps | `pip-audit` | advisories listed + severity | ____ | ☐P ☐F |
| SEC-DEP-FE | Frontend deps | `npm audit` | advisories listed + severity | ____ | ☐P ☐F |

---

## **14. Compatibility Testing**

| Target | Result | Remarks |
|---|---|---|
| Chrome / Edge / Firefox / Safari | **Reserved** — needs a browser rig | record versions on manual pass |
| Desktop (Windows) | ____ | build + API-level evidence allowed here |
| Laptop / tablet / smartphone | **Reserved** — needs devices | responsive classes exist in code |
| Code-level evidence | ____ | `vite build` success, Vitest count (incl. contrast/i18n tests) |

---

## **15. Usability and UI Testing**

| Test ID | Criterion | How to check | Actual | Status |
|---|---|---|---|---|
| UI-001 | Navigation | page inventory + router | ____ | ☐P ☐F |
| UI-002 | Readability | `theme-contrast` tests | ____ | ☐P ☐F |
| UI-003 | Consistency | component system usage | ____ | ☐P ☐F |
| UI-004 | Feedback | toast coverage (error/success), retry/polling UX | ____ | ☐P ☐F |
| UI-005 | Error messages | friendly copy + clean API errors | ____ | ☐P ☐F |
| UI-006 | Responsiveness/a11y | `aria-*`/labels, i18n tests | ____ | ☐P ☐F |
| UI-UAT | Real-user acceptance | **Reserved** — moderated session per `tests/docs/usability_testing.md` | ____ | — |

---

## **16. ISO/IEC 25010 Evaluation**

| Characteristic | What to examine in LUMI | Result |
|---|---|---|
| Functional Suitability | sweep pass rate + suite results | ____ |
| Performance Efficiency | §12 latency + load ceiling + bundle size | ____ |
| Compatibility | §14 evidence (manual pass pending) | ____ |
| Interaction Capability | §15 code-level usability | ____ |
| Reliability | load-test failure rate, degraded-mode behavior, LLM fallback | ____ |
| Security | §13 probes + audits | ____ |
| Maintainability | module structure, test coverage, SAST | ____ |
| Flexibility | per-process limits under scale-out, artifact freshness | ____ |
| Safety | sanitization, quotas, side-effect control | ____ |

---

## **17. Defect / Bug Report**

| Defect ID | Module | Description | Severity | Priority | Status |
|---|---|---|---|---|---|
| BUG-___ | ____ | ____ | Critical/High/Med/Low | ____ | ____ |
| BUG-___ | ____ | ____ | ____ | ____ | ____ |
| BUG-___ | ____ | ____ | ____ | ____ | ____ |

**Severity guide:** Critical = system down or major data/security failure · High = major function broken · Medium = works with limitations · Low = minor.

## **18. Corrective Action and Retesting**

| Defect ID | Corrective Action | Date Fixed | Retest Result | Final Status |
|---|---|---|---|---|
| ____ | ____ | ____ | ____ | ____ |
| ____ | ____ | ____ | ____ | ____ |

## **19. Regression Testing**

*(Pre-filled retest list — prior fixed items worth re-checking every cycle:)*

| Test ID | Previously fixed item | How to retest | Result | Status |
|---|---|---|---|---|
| REG-01 | DEF-01 geothermal bad-id → clean 404 | `GET /geothermal/999999` | ____ | ☐P ☐F |
| REG-02 | DEF-02 invalid map type → 422 | `GET /map/bogus` | ____ | ☐P ☐F |
| REG-03 | DEF-03 bogus forecast metric → 422 | `GET /energyhub/forecast?metric=bogus` | ____ | ☐P ☐F |
| REG-04 | DEF-04 injection on `/forecast/run` → auth wall + 422 | inject `metric` param | ____ | ☐P ☐F |
| REG-05 | DEF-05 products `energy_type` echo → 422 | `?energy_type=' OR '1'='1` | ____ | ☐P ☐F |
| REG-06 | DEF-06 quota message product name | inspect `energyhub.py` detail string | ____ | ☐P ☐F |
| REG-07 | SEC-01 XFF spoof bypass | 70 req with spoofed XFF → expect 429s | ____ | ☐P ☐F |
| REG-08 | Suite regression | re-run pytest ×3 + vitest | ____ | ☐P ☐F |

## **20. Testing Results Summary**

| Category | Total | Passed | Failed | Pass Rate |
|---|---:|---:|---:|---:|
| Functional | ____ | ____ | ____ | ____% |
| Database | ____ | ____ | ____ | ____% |
| API/External | ____ | ____ | ____ | ____% |
| Automated suites | ____ | ____ | ____ | ____% |
| Performance | ____ | ____ | ____ | ____% |
| Security | ____ | ____ | ____ | ____% |
| Compatibility | ____ | ____ | ____ | ____ |
| Usability | ____ | ____ | ____ | ____% |
| Regression | ____ | ____ | ____ | ____% |
| **TOTAL** | ____ | ____ | ____ | ____% |

**Pass Rate = (Passed ÷ Total Executed) × 100** — exclude reserved/skipped items from the denominator.

---

## **21. Overall Technical Assessment**

### **Overall Testing Result**

☐ Passed – Ready for Deployment ☐ Passed with Minor Issues ☐ For Further Improvement ☐ Failed – Major Corrections Required

**Assessment narrative:**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**The system is assessed as:** ☐ Technically Acceptable ☐ Acceptable with Minor Revisions ☐ Requires Further Testing ☐ Not Acceptable

---

## **22. Recommendations**

1. \_\_\_\_\_\_ 2. \_\_\_\_\_\_ 3. \_\_\_\_\_\_ 4. \_\_\_\_\_\_ 5. \_\_\_\_\_\_

---

## **23. Testing Approval**

| Role | Name | Signature | Date |
|---|---|---|---|
| Test Engineer/Tester | ____ | ____ | ____ |
| Developer | ____ | ____ | ____ |
| Project Leader | ____ | ____ | ____ |
| Technical Adviser | ____ | ____ | ____ |
| Project Adviser | ____ | ____ | ____ |

---

## **24. Appendices**

### **Appendix A — Instruments**

| Instrument | Purpose | Output |
|---|---|---|
| `pytest fastapi-backend/tests` | backend suite | pass/fail log |
| `pytest tests/tests/unit`, `tests/tests/integration` | unit + integration suites | pass/fail logs |
| `npm test` / `vitest` (react-frontend) | frontend tests | pass/fail log |
| `artifacts/rerun-*/scripts/endpoint_sweep.py` | 82-check endpoint matrix | `functional/endpoint_sweep.csv` |
| `artifacts/rerun-*/scripts/security_probes.py` | §13 probes | `security/probes.json` |
| `artifacts/rerun-*/scripts/benchmark.py` | §12 endpoint timing | `perf/summary.json` |
| `locust -f tests/pilot_run/locustfile.py --headless -u 25` | load test | `load/u25_*.csv/html` |
| `artifacts/scripts/evaluate_forecasting_models.py` | ML metrics (companion form) | `ml/*` |
| `artifacts/scripts/llm_groq_eval.py` | Groq evaluation | `llm/llm_eval.json` |
| `bandit -r fastapi-backend/app` · `pip-audit` · `npm audit` | SAST + dependency audits | security logs |
| Read-only Supabase checks (PostgREST `count=exact`, anon RLS probes) | §10 | `db/*.json` |

### **Appendix B — Evidence folders**

`docs/09-Technical-Evaluation/artifacts/rerun-<date>/{functional,security,perf,load,db,llm,ml,scripts}/` — keep one dated folder per evaluation cycle so results stay comparable.

### **Appendix C — Notes for the evaluator**

- `/forecast/*` requires login since the Sept cycle — unauthenticated checks should expect **401**, and the authenticated path needs a real token.
- The previous evaluation's historical artifacts (Sept 5–8) live alongside reruns — label yours with today's date.
- The backend used for probing last cycle ran on port 8001 (`uvicorn main:app --port 8001` from `fastapi-backend/`).
- Read-only rule: all Supabase checks use GET/HEAD with the anon key — never write to the live project.
