# TECHNICAL TESTING REPORT — Plain-Language Edition (v2)

**Title:** LUMI — Data-Driven Environmental Intelligence System
**Group Name:** LUMI Development Team
**Technical Evaluators (IT Experts):** automated evidence collection executed in-repository; human expert sign-off pending (§23)

**Purpose of this version:** a plain-language companion to `SYSTEM_TESTING_REPORT.md` (v1). Every number, status, and verdict is identical to v1 and to the saved artifacts — only the wording changed. Write-ups use "we" throughout: "we tested", "we found", "we recommend".

---

## 1. Report card cover

| Item | Details |
|---|---|
| System name | LUMI |
| Full title | LUMI — Data-Driven Environmental Intelligence System (renewable-energy simulation, national energy analytics, and AI-assisted recommendations for Philippine municipalities) |
| Version | 0.1.0 |
| Testing date | 2026-09-15 (fresh re-run); earlier baseline September 5–8, 2026, labeled where used |
| Test machine | Windows 11 Pro for Workstations · i5-8400 @ 2.80 GHz · ~8 GB RAM · 480 GB SSD · Python 3.13.2 · Node 24.15.0 · live Supabase + live Groq/Gemini keys (kept private) |
| Tested by | Devin (automated test execution) |
| Team | LUMI Development Team |
| Report version | 1.0 |
| Status | **Final** — with clearly marked items reserved for manual verification |

---

## 2. Summary for the panel

We re-ran every test live rather than trusting the earlier September run. Headline results:

| What we ran | Result |
|---|---|
| Backend test suite | **104 of 106 passed** — the 2 misses come from a missing test plugin (`pytest-asyncio`), a tooling gap rather than a product bug |
| Unit tests | **177 of 177 passed** |
| Integration tests | **66 passed, 1 missed, 32 skipped** — the miss is a 500 ms speed limit hit at 555 ms while other suites ran at the same time; re-timed alone it took 10.9 ms, so the product is fine and the test needs a quieter lane |
| Frontend tests | **13 of 13 passed** |
| Live API sweep (82 checks across every route) | **79 passed, 3 flagged** — the 3 flags are the `/forecast/*` pages now requiring login, which is a deliberate security upgrade; the sweep's old "public" expectations were outdated |
| Security probes | **16 of 16 passed**; the old rate-limit bypass stayed fixed (spoofed headers get 70/70 rejections) |
| Database checks (read-only) | 14 of 14 behaved as required; private tables correctly refuse anonymous reads |
| Load test (25 users at once) | **1,155 requests, 0 failures**, average ~2.2 s — works, and confirms ~10 active users per server worker as the practical ceiling |
| Dependency audits | **We found a regression vs the September claims:** pip-audit lists **66 known issues in 6 backend packages**; npm lists **4 frontend issues (2 critical)** — earlier docs said both were clean |
| Static security scan (Bandit) | **0 issues** across 16,960 lines |
| Production build | Builds fine; main browser bundle is **6.42 MB** — heavy, logged as an improvement item |

> **In plain terms:** the application's own defenses and features are in strong shape — nearly everything passed. The real concerns sit in third-party packages we depend on, plus a few tooling/documentation items. Details and proof are in the sections below.

---

## 3. What LUMI is and who uses it

LUMI is a web system with four working parts:

- **EcoSim** — a household renewable-energy simulator that estimates solar/wind/hydro/geothermal viability and cost per municipality.
- **EnergyHub** — a national energy dashboard with DOE statistics, ARIMA-based forecasts, and international (IRENA) comparisons.
- **Maps and geospatial services** — PSGC hierarchy, climate layers, and renewable-suitability maps.
- **AI helper** — Groq writes the analysis text (Gemini as backup), plus authenticated extras: saved simulations, profiles, MFA, chat, and an admin console.

| User type | What they can do |
|---|---|
| Administrator | Manage users (create, ban, role, reset, delete), view analytics, edit config, audit chats |
| Registered user | Run and save simulations, AI insights, forecasts, chat, profile/MFA |
| Guest | Public dashboards, map layers, plant data, product browse/recommend |

**The modules we tested** (all real routes in `fastapi-backend/app/routes/`): authentication/accounts, EcoSim, EnergyHub, Forecasting, Geospatial/Map, Geothermal, Products, Saved Simulations, Chat, Admin, ETL, Health, and the AI service layer.

---

## 4. What we covered — and what stays on the manual checklist

**Covered live:** login enforcement, all 82 API checks, bad-input handling, injection attempts, rate limiting (including the old bypass), security headers/CORS, read-only database checks, 23-endpoint speed runs, a 25-user load test, dependency and static security audits, the AI helper's live behavior, the production frontend build, and regression checks of every previously-fixed bug.

**Reserved for manual verification — this environment lacks what's needed:**

- Real-browser matrix (Chrome/Edge/Firefox/Safari) and physical devices (tablet/phone) — requires a browser rig beyond this environment's tooling.
- Human usability/UAT sessions — needs real users.
- Screenshots — replaced with machine-readable JSON/CSV/log evidence instead.
- Database **writes** — kept read-only by the stakeholder's rule; write paths are covered through the mocked test suites.

---

## 5. How we tested

Process: **requirements → plan → build cases → execute → log defects → fix → retest → final evaluation** — and we re-executed rather than trusting the earlier baseline.

| Test type | Ran? | Where the proof is |
|---|---|---|
| Unit | Yes | 177 tests passed |
| Integration | Yes | 66 passed / 1 missed / 32 skipped |
| System (end-to-end API) | Yes | 82-check live sweep |
| Functional | Yes | sweep + defect retests (§8) |
| Usability | Partly | code-level review only; humans still needed (§15) |
| Performance | Yes | 23-endpoint benchmark + 25-user load test |
| Security | Yes | 16 probes + audits + live rate-limit retest |
| Compatibility | Reserved | needs a browser/device rig (§14) |
| Database | Read-only pass | counts + access-control verification (§10) |
| API | Yes | 82-check sweep including error paths |
| Regression | Yes | all 6 old defects + security fixes retested |
| User acceptance | Reserved | needs human participants (§15) |

---

## 6. The test machine and tools

| Component | Specification |
|---|---|
| CPU / RAM / Storage | i5-8400 @ 2.80 GHz · ~8 GB · 480 GB SSD |
| OS | Windows 11 Pro for Workstations, build 26200 |
| Backend stack | Python 3.13.2 · FastAPI 0.115.0 + Uvicorn · Supabase (PostgreSQL + auth + row-level security) · Upstash Redis |
| Frontend stack | Node 24.15.0 · React 18 · Vite 6.4.3 · Tailwind/shadcn · Leaflet |
| AI services | Groq (`groq/compound-mini`) primary, Gemini fallback |
| Test tooling | pytest 9.1.1 · Vitest · Locust 2.46.5 · Bandit 1.9.4 · pip-audit 2.10.1 · httpx 0.27.2 |
| Browser | Reserved for manual pass — API-level testing only in this environment |

---

## 7. The data we tested against

| Data | What it is | Size |
|---|---|---|
| DOE energy dataset | `master_preprocessed.csv`, annual national stats | 23 rows × 45 cols (2003–2025) |
| Geography (live, read-only) | regions → provinces → municipalities → barangays | **18 → 120 → 1,813 → 53,460** |
| Climate | `municipality_climate_monthly` | **334,584 rows** |
| Suitability | hydropower / geothermal tables | 1,600 / 1,813 rows |
| Forecast artifacts | precomputed prediction + model-comparison CSVs | 6-year forecasts, 6 models |
| Test traffic | valid request sets per endpoint | 5–30 repetitions each |
| Test users | we used unauthenticated probes only — creating accounts was left out under the read-only rule | — |

---

## 8. Feature checks — what works

The 82-check sweep (`functional/endpoint_sweep.csv`) touched every public route plus negative and login-gated paths. The response mix — **45 healthy responses, 17 correct "login required" rejections, 16 correct "bad input" rejections, 3 correct "not found," 1 successful create** — is exactly the shape a healthy API should show.

| Check | Module | What we did | What happened | Result |
|---|---|---|---|---|
| Health | Health | `/health`, `/health/detailed` | OK in 4 ms; detailed reports supabase/redis/rag_index all ok | **Pass** |
| Pickers | EcoSim | municipalities/provinces lists | Populated (1,813 municipalities served) | **Pass** |
| Simulation | EcoSim | `GET /ecosim/` compute + `POST` create | Computed results ~547 ms; create → 201 | **Pass** |
| AI analysis | EcoSim | `/ecosim/ai` | Narrative analysis ~612 ms | **Pass** |
| Dashboards | EnergyHub | overview, forecast, trends, map-data, breakdowns, demand, IRENA, Meralco, solar atlas | All healthy, ≤50 ms each | **Pass** |
| AI insight | EnergyHub | `/energyhub/ai-insight` | Mix of answers and quota-gated 401s — the quota system working as designed | **Pass** |
| Plants | Geothermal | catalog + per-municipality analysis | 200s; analysis ~295 ms (heavier compute) | **Pass** |
| Map layers | Map/Geospatial | coverage, solar, PSGC, climate, centroids | All healthy, ≤60 ms | **Pass** |
| Products | Products | recommend / browse / audit | Healthy, ≤9 ms | **Pass** |
| Login walls | Auth/Admin/Simulations/Chat | hit protected routes missing a token | Uniform 401 "Missing token" | **Pass** |
| Forecast routes | Forecast | `/forecast/run`, `/backtest`, `/models` | **401 "Missing token"** — these routes gained a login requirement since September (`forecast.py` `_require_forecast_access`); the sweep expected the old public behavior | **Flagged — deliberate hardening; sweep expectations updated in BUG-06** |
| Injections | Input security | `' OR '1'='1`, `;DROP TABLE…` in parameters | 422 rejections; nothing reflected, nothing reached the database | **Pass** |

> **In plain terms:** every feature works. The only sweep flags were three forecast URLs that now ask for login — the system got *more* secure since the last check, and the sweep script's expectations were the stale part.

---

## 9. Bad-input checks

| Input | Attack/edge case | Expected | Got | Result |
|---|---|---|---|---|
| `metric` (forecast) | `' OR '1'='1`, `invalid_metric`, `consumption;DROP TABLE…` | reject | 422 allowlist error (public route) / 401 first on the login-gated route | **Pass** |
| `renewable_type` (map) | invalid value | reject | 422 literal error | **Pass** |
| `energy_type` (products) | `' OR '1'='1` | reject, input stays out of the response | 422 allowlist reject — old DEF-05 stays fixed | **Pass** |
| `/geothermal/{id}` | id 999999 | clean 404 | `{"detail":"Municipality not found"}` — internals stayed hidden | **Pass** |
| EcoSim params | missing / malformed body | reject | 422 (suite tests confirm) | **Pass** |

> **In plain terms:** the API validates every input against a strict allowlist at the front door. Injection strings get rejected with a polite 422 and stay clear of the database.

---

## 10. Database checks (read-only by rule)

The stakeholder rule was **read-only**, so we verified structure and access control live, and covered write behavior through the test suites' mocks.

| Check | Expected | Got | Result |
|---|---|---|---|
| Read public tables | counts return | regions 18, provinces 120, municipalities 1,813, barangays 53,460, climate 334,584, suitability 1,600/1,813 | **Pass** |
| Anonymous access to private tables | denied | `profiles`, `saved_simulations`, `admin_audit_log`, `ml_model_registry` → "permission denied"; `user_ecosim_logs` → empty set (row-level security filters to own rows) | **Pass** |
| Referential shape | consistent hierarchy | 18→120→1,813→53,460 chain is coherent; geothermal table has exactly one row per municipality | **Pass** |
| Duplicates | none in modeling data | zero duplicate year rows | **Pass** |
| Writes (INSERT/UPDATE/DELETE) | — | **Reserved** — read-only rule; mocked write paths all pass in the suites | Covered indirectly |
| Transactions / backups | — | **Reserved for admin-side verification** under the read-only rule | Reserved |

> **In plain terms:** the database is organized, complete for what we checked, and correctly refuses anonymous readers on private tables.

---

## 11. External services

| Service | Test | Expected | Got | Result |
|---|---|---|---|---|
| Groq | 6 live analysis calls | usable structured text | 6/6 well-formed, sanitized, correctly sectioned | **Pass** |
| Groq | break Gemini first | Groq covers | answered in 1.92 s | **Pass** |
| Groq | 0.5 s timeout | give up gracefully | stopped at 504 ms → caller's fallback message shown | **Pass** |
| Groq | configured fallback model `qwen/qwen3.6-27b` | available | **HTTP 404 — the model is unavailable to this account** | **Fail — BUG-08** |
| Supabase | REST reads, anonymous key | public allowed, private denied | both verified | **Pass** |
| Redis | health detail | `ok` | `ok` | **Pass** |

Checklist coverage: successful calls, invalid calls handled, auth verified, timeouts handled, clean errors, rate limits enforced, provider-failure fallback verified.

---

## 12. Speed and load

### 12.1 Single-user speed (30 repetitions per endpoint)

| Group | Endpoints | Typical | Slowest edge (p95) |
|---|---|---|---|
| Instant reads | health, overview, forecast, trends, breakdowns, plants, products, forecast models | **3–8 ms** | ≤9 ms |
| Data reads | map-data, municipalities, provinces, climate, coverage, solar | **39–60 ms** | ≤62 ms |
| Heavy computes | map-explanation, geothermal analysis, health/detailed | **138–295 ms** | ≤325 ms |
| Simulations & AI | EcoSim sim, EcoSim AI, AI insight | **547–639 ms** | ≤3,038 ms (AI quota path) |

Two flagged rows are honest-by-design rather than slow: `/forecast/models` answers "login required" in 3.1 ms, and `/energyhub/ai-insight` mixes answers with quota rejections.

### 12.2 Load — 25 users at once (fresh Locust run)

| Metric | Value |
|---|---|
| Total requests / failures | **1,155 / 0** |
| Throughput | ~10 requests/second |
| Average / middle / 95th pct / worst | **2,202 / 2,000 / 4,400 / 6,278 ms** |
| EcoSim simulation under load | 121 reqs · 0 fails · avg 3,615 ms |
| EnergyHub overview under load | 159 reqs · 0 fails · avg 1,877 ms |

Tooling footnote: Locust's own stats-writer threw a closed-file error after the run finished — a quirk of the tool on Windows; every request statistic was captured regardless (logged as BUG-05).

### 12.3 Frontend bundle

Production build succeeded in ~3 minutes, but the main browser bundle is **6.42 MB (1.93 MB compressed)** plus a 1 MB PDF-library chunk — Vite itself warned about >500 kB chunks (logged as BUG-07).

> **In plain terms:** one user gets lightning-fast answers (reads in single-digit milliseconds). Under 25 simultaneous users every request still succeeds, but averages ~2.2 seconds — consistent with the earlier finding that one server worker comfortably serves about **10 active users**, so scaling means adding workers, and the frontend bundle deserves a diet.

---

## 13. Security checks

| Area | What we tried | Result |
|---|---|---|
| Login enforcement | missing token / garbage token / `alg:none` trick / forged signature on protected routes | 401 rejection on all four — **Pass** |
| Admin enforcement | bad token on three admin routes | 401 ×3 — **Pass** |
| Security headers | inspected responses | all 5 present; server banner masked to `Lumi` — **Pass** |
| CORS | allowed origin / Vercel-style origin / hostile origin | 200 · 200 · **400 rejected** — **Pass** |
| Info exposure | `/docs`, `/redoc`, `/openapi.json` | 404 in production mode — **Pass** |
| Error leakage | forced a 404 | clean message, zero internals — **Pass** |
| Rate limiting | 70 requests ×3: normal, spoofed-loopback header, spoofed-public header | 60 allowed then 429s; **both spoof runs rejected 70/70** — September's bypass stays fixed — **Pass** |
| Injection | SQL-style strings in parameters | 422 allowlist rejections, nothing reached the DB — **Pass** |
| Static scan | Bandit over the whole backend | **0 issues / 16,960 lines** — **Pass** |
| Dependency audit (backend) | pip-audit | **66 known advisories across 6 packages** (pillow, starlette, transformers, python-jose, python-dotenv, ecdsa) — **Fail — BUG-02** |
| Dependency audit (frontend) | npm audit | **4 advisories: 2 critical (maplibre-gl via plotly.js, plotly.js), 2 moderate (vitest tooling)** — **Fail — BUG-03** |

> **In plain terms:** the application layer is strong — every attack we threw was refused, and the September security fixes held up. The exposed layer is **third-party dependencies**: 70 advisories total, which directly contradicts the earlier "clean audit" documentation. Upgrading packages is the fix, and it's our top recommendation.

---

## 14. Browser and device checks

| Target | Status |
|---|---|
| Chrome / Edge / Firefox / Safari | **Reserved for manual verification** — a browser rig sits outside this environment's tooling. What we *can* say from code: the frontend builds for modern browsers (Vite 6), and its 13 automated tests (including i18n and color-contrast checks) pass under jsdom. |
| Desktop (Windows) | **Pass at build + API level** — production build compiles and the backend serves correctly on this machine. |
| Laptop / tablet / smartphone | **Reserved for manual verification** — responsive layout classes exist throughout the code, but physical devices need a human pass. |

---

## 15. Ease-of-use review (code-level — humans still needed for the real thing)

| Criterion | What the code shows | Result |
|---|---|---|
| Navigation | Dedicated pages for Home, Dashboard, EcoSim, EnergyHub, Saved Simulations, Chat, Profile, Security Settings, Admin | **Pass** |
| Readability | An automated color-contrast test suite exists and passes (3 tests) | **Pass** |
| Consistency | A single component system (shadcn/Tailwind) used across pages | **Pass** |
| Feedback | **39 error-toast + 16 success-toast call sites**; the AI panel retries and polls progress during slow answers | **Pass** |
| Error messages | Verified friendly copy ("Please log in to continue using EnergyHub") and clean API errors | **Pass** |
| Accessibility / screens | `aria-*` attributes and labels present across 11+ page files; i18n tested | **Partial — code-level only** |
| Real-user acceptance | **Reserved for manual verification** — a moderated UAT session with actual users remains the plan per `tests/docs/usability_testing.md` | Reserved |

---

## 16. ISO/IEC 25010 quality summary

| Quality area | Evidence | Grade |
|---|---|---|
| Functional suitability | 79/82 sweep + 360/363 automated checks pass | **Good** |
| Performance efficiency | instant single-user reads; ~2.2 s average under 25 users; 6.4 MB bundle | **Adequate — concurrency-limited** |
| Compatibility | browser/device matrix awaits a manual pass | **Unassessed** |
| Interaction capability | toasts, i18n, contrast tests, structured pages | **Good (code-level)** |
| Reliability | zero load-test failures; graceful AI fallback/timeout; degraded-mode health reporting | **Good** |
| Security | 16/16 probes, row-level security verified, strict allowlists — alongside 70 unpatched dependency advisories | **Strong app layer / weak dependency layer** |
| Maintainability | modular routes, 363 automated checks, clean static scan, one test-plugin gap | **Good** |
| Flexibility | per-process rate-limit counters multiply under scale-out (documented); served forecasts refresh on pipeline re-runs | **Adequate** |
| Safety | AI outputs sanitized, quotas enforced, zero unsafe side-effects observed | **Adequate** |

---

## 17. Bugs we found

### Old bugs — retested fresh

| Bug | What it was | Retest result | Status |
|---|---|---|---|
| DEF-01 | geothermal bad-id leaked a 500 | clean 404 "Municipality not found" | **Verified fixed** |
| DEF-02 | map accepted bad renewable type | 422 | **Verified fixed** |
| DEF-03 | forecast accepted bogus metric | 422 (public) / 401 (gated route) | **Verified fixed** |
| DEF-04 | forecast swallowed injection strings | blocked at the login wall, then 422 | **Verified fixed** |
| DEF-05 | products echoed unvalidated input | 422 allowlist, input stays out of the response | **Verified fixed** |
| DEF-06 | quota message named the wrong product | now reads "continue using EnergyHub" | **Verified fixed** |
| SEC-01 | spoofed headers bypassed rate limits | 70/70 rejected live | **Verified fixed** |
| SEC-02–10 | assorted security fixes (split counters, fail-open status, secrets, leaks, banner) | verified by probes/tests — **except** SEC-04's "zero CVEs" claim, which regressed into BUG-02/03 | Mostly verified |

### New bugs logged by this evaluation

| ID | Where | What we found | Severity | Status |
|---|---|---|---|---|
| BUG-01 | Test setup | 2 backend tests fail to execute — the venv lacks an async test plugin (`pytest-asyncio`) | Medium | **Open** — install the plugin |
| BUG-02 | Backend packages | pip-audit: **66 advisories** in pillow, starlette, transformers, python-jose, python-dotenv, ecdsa | **High** | **Open** — upgrade package versions |
| BUG-03 | Frontend packages | npm audit: 4 advisories, **2 critical** (plotly.js / bundled maplibre-gl) | **High** | **Open** — major version bumps needed |
| BUG-04 | Test stability | the 500 ms health-check test trips under parallel load (555 ms; 10.9 ms when quiet) | Low | **Open** — isolate or relax the threshold |
| BUG-05 | Tooling | Locust stats-writer closed-file error after the run (stats still saved) | Low | **Open** — tool quirk |
| BUG-06 | Docs/sweep | stale expectations: sweep assumes public `/forecast/*`; September CSV had "placeholder" model rows; September "0 vulnerabilities" claims contradict fresh audits | Medium | **Open** — refresh the artifacts |
| BUG-07 | Frontend | 6.42 MB main bundle + 1 MB PDF chunk | Medium | **Open** — code-split routes, lazy-load heavy libs |
| BUG-08 | AI config | configured Groq fallback model returns 404 for this account | Medium | **Open** — prune the fallback list |
| BUG-09 | AI contract | code comments claim forced-JSON output while real output is markdown prose — harmless today, hazardous for future consumers | Low | **Open** — fix the comment or the contract |

---

## 18. What got fixed and re-checked

Every defect fixed in the September cycle was retested fresh: **all six DEF items and the high-severity SEC-01 stay fixed and verified.** One earlier claim reopened: the "clean dependency audit" (SEC-04) regressed — fresh audits found 70 advisories, now tracked as BUG-02/03. This read-only evaluation changed zero lines of code; BUG-01 through BUG-09 are handed to the team.

## 19. Re-testing the old fixes

| Item | Retest | Status |
|---|---|---|
| Login walls | uniform 401s across protected/admin/forecast/simulation routes | Pass |
| Public features | all public routes healthy in the sweep | Pass |
| Forecast routes | behavior *changed deliberately*: public → login-required | Pass (hardening) |
| Rate limiting | stricter than before — merged counters, anti-spoof | Pass |
| Automated suites | 360/363 pass; misses are the plugin gap + one load-sensitive timing test | Pass w/ noted exceptions |
| Old security fixes | verified as above | Pass |
| Frontend tests | 13/13 | Pass |

---

## 20. Scoreboard

Executed items only (skipped tests excluded; the 3 sweep flags counted as flags for honesty):

| Category | Ran | Passed | Flagged/Failed | Pass rate |
|---|---:|---:|---:|---|
| Feature checks (sweep + defect retests) | 88 | 85 | 3* | 96.6% |
| Database (read-only) | 14 | 14 | 0 | 100% |
| External services | 6 | 5 | 1 | 83.3% |
| Automated suites | 363 | 360 | 3† | 99.2% |
| Performance | 25 | 22 | 3‡ | 88.0% |
| Security | 21 | 19 | 2§ | 90.5% |
| Compatibility | — | — | — | reserved for manual pass |
| Usability | 6 | 5 | 1 partial | 83.3% |
| Regression | 7 | 7 | 0 | 100% |
| **TOTAL** | **530** | **517** | **13** | **97.5%** |

\* the three sweep flags are the deliberate login-hardening on `/forecast/*`. † two missing-plugin test items (BUG-01) + one load-sensitive timing test (BUG-04). ‡ login-gated forecast route, quota-gated AI route, and one benchmark-script artifact. § the two dependency audits (BUG-02/03).

---

## 21. Overall verdict

**Result: Passed with minor issues — trending toward "further improvement" until the dependency findings are patched.**

> **In plain terms:** LUMI's own code is in genuinely good shape — every feature answers correctly, the login walls hold under direct attack, every previously-fixed bug stayed fixed, bad inputs get refused politely, failures degrade gracefully, and performance is honestly characterized (fast reads, ~10 active users per worker, zero failures at 25). What stands between this and a clean deployment sign-off is **outside our own code**: 70 dependency advisories (BUG-02/03), plus a handful of tooling and documentation items. The browser/device matrix and human UAT remain scheduled for the manual pass.

**Assessment: ☒ Acceptable with minor revisions** — deployment sign-off should follow the BUG-02/03 package upgrades and the manual compatibility/UAT pass.

---

## 22. What we recommend next

1. **Patch dependencies first** — pillow ≥12.2, starlette ≥0.40, python-jose ≥3.4.0, python-dotenv ≥1.2.2 backend-side; plotly.js →4.1.1 and vitest →5.x frontend-side; then wire audits into CI so "clean" claims stay true.
2. **Fix test tooling** — add `pytest-asyncio`; give the timing-sensitive health check a quiet lane or a realistic threshold.
3. **Refresh stale artifacts** — update sweep expectations for login-gated forecasts; regenerate the model-comparison CSV with the real numbers this run produced; correct the earlier "0 vulnerabilities" notes.
4. **Plan for scale** — the documented ceiling is ~10 active users per worker; add workers/instances before launch, and remember per-process rate-limit counters multiply accordingly.
5. **Trim the bundle** — split routes and lazy-load the PDF and charting libraries.
6. **Harden the AI layer** — remove the 404 fallback model; align the code comment with the real markdown contract; keep the retry/polling UX for the ~5 s typical response.
7. **Run the manual pass** — real browsers, real devices, real users for UAT, and a disposable test project to exercise database writes.
8. **Keep the ML honest** — always show the forecast's "between X and Y" range in the UI; pursue monthly data and per-target model settings.

---

## 23. Sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Test engineer | Devin (automated execution) | electronic — this report + artifacts | 2026-09-15 |
| Developer | LUMI Development Team | pending | — |
| Project leader | — | pending | — |
| Technical adviser | — | pending | — |
| Project adviser | — | pending | — |

---

## 24. Where the proof lives

Everything under `docs/09-Technical-Evaluation/artifacts/`:

| Folder | What's inside |
|---|---|
| `rerun-2026-09-15/functional/` | all four test-suite logs, the 82-check sweep, defect retests, backend boot log |
| `rerun-2026-09-15/security/` | 16-probe results, rate-limit retest, Bandit output, both dependency audits |
| `rerun-2026-09-15/perf/` | 23-endpoint benchmark + the frontend build log |
| `rerun-2026-09-15/load/` | Locust 25-user stats, history, HTML report, and log (with the tool's own error noted) |
| `rerun-2026-09-15/db/` | read-only Supabase counts + access-control checks |
| `rerun-2026-09-15/llm/` | live Groq evaluation |
| `rerun-2026-09-15/ml/` | full fresh forecasting-evaluation artifacts |
| `artifacts/scripts/` | the test scripts written for this evaluation |
| Earlier evidence (labeled historical) | `TECHNICAL_EVALUATION_ALL_RESULTS.md` and the September `artifacts/` folders — used as baseline; fresh numbers above win wherever they disagree |

**Screenshot appendix:** machine-readable JSON/CSV/logs stand in for screenshots — a browser pass remains on the manual checklist.
