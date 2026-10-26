# CHAPTER 3 — INSERT (TABULAR VERSION): System Test Plan and Results, and Machine Learning Evaluation

> **Before pasting, four housekeeping notes.**
>
> 1. This is the table-heavy variant of `CHAPTER3_SYSTEM_TEST_AND_ML_EVALUATION.md`. The prose version and this version present the same evidence, so choose one and do not paste both.
> 2. The tables below are numbered Table 3.1 to Table 3.48 in the order they appear, and a legend line is placed beneath each table that uses coded identifiers or abbreviations, matching the legend convention of the other Chapter 3 tables. The existing Chapter 3 tables that begin in section 3.5 should be renumbered to follow after Table 3.48.
> 3. The results cited come from the testing conducted on the deployed system by the development team together with ten IT expert evaluators, the consolidated technical evaluation, and the machine learning evaluation re-execution. Where the suite logs and the consolidated report differ (for example the earlier log recorded 176 unit and 77 backend passes), the consolidated numbers are used and the difference is footnoted.
> 4. Keep the "not applicable" sentences in the machine learning sections. They explain why classifier measures do not apply to a forecasting model, and removing them weakens the defense of the results.

---

**3.3 System Test Plan and Results**

The system test plan was prepared to define what was tested, how the testing was performed, and the criteria used to determine whether the system passed. LUMI was tested on the deployed web application by the development team together with ten IT expert evaluators. Testing followed the structured cycle of requirements review, test planning, test case development, test execution, defect identification, correction, retesting, and final evaluation. A consolidated technical evaluation was also executed to cover the automated test suites, a live sweep of every mounted API endpoint, load testing, failure injection, and security probing. The machine learning evaluation was re-executed in a separate run.

The testing objectives were the following:

1. Verify that all visible functions work as described.
2. Identify defects a user would notice.
3. Judge responsiveness by direct observation and measurement.
4. Verify that the application works across browsers and devices.
5. Assess access control as experienced by guest, registered-user, and administrator accounts.
6. Verify that saved data persists and stays private to its owner.
7. Evaluate the system against ISO/IEC 25010.
8. Confirm that previously fixed defects stay fixed through regression checks.
9. Determine deployment readiness from an end-user's point of view.

The test plan covered three testing surfaces as summarized in Table 3.1.

| Testing Surface | Instrument or Method | Coverage |
| --- | --- | --- |
| Manual evaluation instrument | 101 task-based cases executed by evaluators | Public pages and navigation (FT-001 to FT-007: home, about, terms, privacy, logged-out navigation, theme and language toggles, not-found page), accounts (AC-001 to AC-009: sign-up validation, login, Google sign-in, password reset, multi-factor authentication, logout), EcoSim (FT-010 to FT-016: wizard, location pickers, simulation runs, AI analysis, saving, PDF export), EnergyHub (FT-017 to FT-025: overview, trends, forecast chart, choropleth map and level switching, breakdowns, provincial demand, AI insight, chart explanations), saved data and account pages (FT-026 to FT-033: saved simulations, dashboard, profile editing, password change, MFA setup page), the admin console (AD-001 to AD-010: users, analytics, configuration, usage, logs, forecast panel), input validation (IV-001 to IV-005: letters in bill fields, oversized and negative entries, missing location, injection strings), database persistence and privacy (DP-001 to DP-006: data survival across sessions and per-user isolation), AI and connected services (AI-001 to AI-006: AI narratives, waiting behavior, quota messaging, insight panels, map tiles, Google sign-in), timed performance observation (PT-001 to PT-009: page loads and key flows), on-screen security behavior (SO-001 to SO-014: access walls, masking, HTTPS, error messages, throttling), usability tasks (UAT-1 to UAT-5: the five timed user journeys), and regression checks (REG-01 to REG-06: re-verification of previously fixed defects) |
| Automated technical evaluation | pytest and Vitest suites, scripted endpoint sweep, latency and load benchmarks, failure injection, security probes | Unit, backend, frontend, and integration test suites of the project plus a scripted sweep of every mounted API endpoint |
| Machine learning evaluation | Held-out benchmark, cross-validation, diagnostics, robustness perturbation, latency and size measurement | Deployed forecasting model against five alternatives plus the generative AI layer |

*Legend: FT functional test case; AC account case; AD admin console case; IV input-validation case; DP persistence and privacy case; AI connected-services case; PT timed-observation case; SO on-screen security case; UAT user acceptance task; REG regression check; HTTPS secure HTTP; MFA multi-factor authentication.*

*Table 3.1: The Three Testing Surfaces of the LUMI System Test Plan*

Table 3.1 summarizes the three testing surfaces of the plan. The coded identifiers and abbreviations used throughout this section are defined in the legend line beneath each table where they appear.

Sections 3.3.1 to 3.3.12 present the scope, methodology, environment, test cases, and results of the system testing. Section 3.3.13 presents the machine learning evaluation results and discussion.

**3.3.1 Testing Scope**

The testing covered every screen, feature, and flow that could be reached through the application interface on the deployed site. This included the public pages consisting of Home, About, Terms, and Privacy; sign-up, login, logout, password reset, and multi-factor authentication; the EcoSim simulation wizard, results, AI analysis, save-simulation, and PDF export; the EnergyHub national dashboard with its overview, trends, forecast, choropleth map, source and grid breakdowns, provincial demand, and AI insight; saved simulations, profile, and security settings; the admin console covering users, analytics, configuration, usage, and logs; input handling including hostile and boundary inputs; on-screen security behavior; data persistence and privacy between users; responsiveness; compatibility across browsers and devices; API behavior under valid, invalid, boundary, and adversarial inputs; performance under single-user and stepped-concurrency load; failure and recovery behavior; and a moderated usability session. The machine learning scope covered the deployed ARIMA(1,1,1) forecaster, an autoregressive integrated moving-average time-series model, for national electricity consumption, peak demand, and renewable generation, together with five comparison models, and the Groq and Gemini generative AI recommendation layer evaluated on its output contract, latency, and resilience.

The items excluded from the testing cycle are listed in Table 3.2.

| Excluded Item | Reason |
| --- | --- |
| Load testing on the production deployment | Deliberately avoided; only a light production smoke check was done so production infrastructure and paid providers received no generated traffic |
| Direct row-level security policy testing inside Supabase, meaning the database policies that scope each row to its owning user | Requires an authenticated database session |
| Transport layer security (TLS) and certificate testing | Excluded except for verifying the production HTTP strict-transport-security (HSTS) header |
| Fuzzing, session-fixation, and cross-site request forgery (CSRF) testing | Not covered beyond cross-origin resource sharing (CORS) preflight behavior |
| Notebook-level reproduction of the forecasting pipeline | Excluded; the endpoints were verified instead |
| NASA POWER fetch latency | Not applicable at runtime; climate data is served from Supabase and bundled fallbacks |
| External validation of the forecast model | No second country's data was available |
| Geothermal suitability classifier | Present in the codebase but excluded from the machine learning evaluation scope |

*Legend: CORS cross-origin resource sharing; CSRF cross-site request forgery; TLS transport layer security; HSTS HTTP strict-transport-security header; RLS row-level security (per-owner database policies).*

*Table 3.2: Items Excluded from the Testing Cycle and Their Reasons*

Table 3.2 lists the exclusions together with the reason for each. Recording the boundary explicitly keeps the results honest about what the cycle did and did not cover.

**3.3.2 Testing Methodology**

The testing followed the lifecycle of requirements review to test planning, test case development, test execution, defect identification, correction, retesting, and final evaluation. Seven complementary testing types were applied as summarized in Table 3.3.

| Testing Type | Purpose | Instrument |
| --- | --- | --- |
| Functional walkthrough | Follow each scripted scenario and compare expected and actual behavior | Functional test (FT) cases and automated suites |
| Exploratory and negative-input testing | Type bad, unusual, or hostile-looking input into forms and endpoints | Input-validation cases IV-001 to IV-005 and sweep adversarial inputs |
| Permission checks | Exercise the same pages as guest, registered user, and admin | On-screen security cases SO-001 to SO-014 and admin console cases AD-001 to AD-010 |
| Persistence checks | Save data, log out, log back in, and verify ownership isolation | Persistence and privacy cases DP-001 to DP-006 |
| Timed observation and benchmarks | Measure responsiveness directly with thirty repetitions per endpoint | PT-001 to PT-009 and latency benchmark |
| Load testing | Stepped virtual users from 1 to 100 at sixty seconds per level | Locust 2.46.4 headless, local target only |
| Failure and security probing | Inject dependency outages, malformed tokens, oversized bodies, and spoofed headers | Seventeen-scenario failure matrix and probes |

*Legend: AD admin console case; IV input-validation case; DP persistence and privacy case; PT timed-observation case; SO on-screen security case.*

*Table 3.3: Testing Types Applied in the LUMI System Test Plan*

Table 3.3 shows the testing types that were applied during the evaluation. Each type targets a different kind of defect, from wrong screen behavior to weak input handling and performance degradation under load. Defect handling was made explicit in the plan. Every defect found during the first execution pass was logged with an identifier, corrected, and executed again in the final pass. The regression block (REG-01 to REG-06) also re-ran previously fixed behaviors by hand to confirm that the corrections remained effective. The methodology for the machine learning evaluation is described in section 3.3.13 and includes the train and test split protocol, expanding-window cross-validation, residual diagnostics, robustness perturbation, and statistical comparison.

**3.3.3 Hardware and Software Test Environment**

| Item | Configuration |
| --- | --- |
| Workstation OS | Windows 11 Pro for Workstations |
| Processor and memory | Intel Core i5-8400, around 8 GB RAM |
| Python runtime | 3.13.2 |
| Backend under test | FastAPI on uvicorn 0.30.6, single worker, http://127.0.0.1:8000 |
| Frontend under test | React 18 plus Vite plus Tailwind production build |
| Node and npm | v24.15.0 and 11.12.1 |
| Test tooling | pytest 9.1.0, Vitest, Locust 2.46.4, pip-audit 2.10.1, Bandit 1.9.4, npm audit |
| Data tier | Live Supabase (PostgreSQL, eu-west) and Upstash Redis with bundled CSV fallbacks |
| Large language model (LLM) providers | Groq as primary and Google Gemini as fallback-capable |
| ML libraries | statsmodels 0.14.6, scikit-learn 1.9.0, pandas 3.0.5, groq 0.18.0 |
| Production target | https://lumi-backend-ten.vercel.app on Vercel serverless |

*Legend: LLM large language model; Redis rate-limit cache store.*

*Table 3.4: Hardware and Software Test Environment*

Table 3.4 summarizes the environment where all automated and instrumented tests were executed. Load testing was pointed at the local backend only so that the production infrastructure and the paid language model providers did not receive any generated traffic. The machine learning artifacts were produced in the same Python environment.

**3.3.4 Functional Test Cases**

Functional verification combined the pre-existing automated suites of the project, a scripted live sweep of every mounted API route, and the 101-case manual instrument. The automated execution results are presented in Table 3.5.

| Suite | Result | Status |
| --- | --- | --- |
| Unit tests (lumi_tests/tests/unit/) | 177 passed | PASS |
| Backend tests (fastapi-backend/tests/) | 106 passed | PASS |
| Frontend Vitest (react-frontend) | 9 passed (3 test files) | PASS |
| Integration tests (live-server cases deselected) | 23 passed, 2 skipped | PASS |
| Live endpoint sweep | 82 of 82 checks passed | PASS |

*Table 3.5: Automated Functional Test Results*

Table 3.5 presents the results of the automated functional tests. All suites passed, and the live endpoint sweep passed all 82 of its checks. The composition of each suite, so that the counts can be traced to specific test files, is broken down in Tables 3.6 to 3.10.

| Test File | Cases | What It Verifies |
| --- | --- | --- |
| test_renewable_calculations.py | 53 | Solar temperature, dust, and humidity factors; performance ratio; wind cube-law output and turbine-operating bounds; hydro runoff, flow rate, and discharge; per-option summary |
| test_geothermal_calculations.py | 56 | Haversine distance, normalization helpers, and geothermal scoring calculations |
| test_ml_preprocessing.py | 22 | Forward-fill of missing values, dtypes, trend features, and the MAE, RMSE, R-squared, and MAPE metric functions |
| test_ai_service.py | 18 | Prompt construction, JSON normalization, mocked retrieval-augmented generation (RAG) retrieval, and error handling |
| test_new_improvements.py | 18 | Safe JSON formatter, rate-limit middleware, Redis fallback, forecasting helpers, retrieval-augmented generation (RAG) reranking, and settings |
| test_rag_embeddings_client.py | 5 | 384-dimensional embeddings, Redis cache use, batch encoding, and provider selection |
| test_rag_pgvector_store.py | 5 | Context retrieval shape, filter parameters, and index statistics and build |
| **Total** | **177** |  |

*Legend: MAE mean absolute error; RMSE root mean squared error; MAPE mean absolute percentage error; R-squared coefficient of determination; RAG retrieval-augmented generation; Redis rate-limit cache store.*

*Table 3.6: Unit Test Suite Breakdown by File*

Table 3.6 shows the composition of the unit suite. The suite concentrates on the calculation layer, with 109 of 177 cases covering the renewable and geothermal estimation math that the simulation results depend on.

| Test File | Cases | What It Verifies |
| --- | --- | --- |
| test_security_fixes.py | 29 | Boundary validation hardening: 404 and 422 mapping for bad identifiers, invalid renewable types, map levels, and forecast metrics |
| test_catchment_enrichment.py | 21 | Catchment enrichment CSV integrity: municipality coverage, no duplicate identifiers, no nulls in key columns, valid match methods |
| test_calibration.py | 19 | Wind and hydro score functions, power-curve bounds, and scoring baselines |
| test_wind_hydro_plants.py | 14 | Wind and hydro plant catalog loading, proximity boost, generation scale, and plant floors |
| test_routes.py | 11 | Route-level behavior: anonymous and authenticated quota gating on EcoSim and AI endpoints |
| test_simulations_audit.py | 9 | Simulation CRUD audit: 404 responses, negative identifiers, label sanitization |
| test_ecosim_quezon.py | 6 | Quezon province regression: no server errors and dashboard build for province and municipality |
| test_regression.py | 5 | Score formatting and municipality-to-province climate aggregation |
| test_admin_export.py | 4 | CSV export of usage and logs with authentication gating |
| test_ecosim_explanations.py | 3 | Static renewable explanation builder output |
| test_llm_sanitizer.py | 0 pytest-collected | Script-style sanitizer assertions run separately from pytest (think-tag stripping, the removal of raw reasoning markup, and output cleaning) |
| **Total** | **121 collected** |  |

*Legend: 404 not found; 422 validation failed; CRUD create-read-update-delete.*

*Table 3.7: Backend Test Suite Breakdown by File*

Table 3.7 shows the composition of the backend suite. The file inventory currently collects 121 cases, while the consolidated evaluation run reported 106 passed and the earlier suite log recorded 77 passed; the suite has been extended across the evaluation window, and the reported pass count is cited as it was measured.

| Test File | Cases | What It Verifies |
| --- | --- | --- |
| I18nProvider.test.jsx | 4 | Internationalization provider behavior |
| theme-contrast.test.js | 3 | Theme contrast tokens |
| DashboardChart.test.jsx | 2 | Chart component rendering |
| **Total** | **9** |  |

*Table 3.8: Frontend Vitest Breakdown by File*

Table 3.8 shows the three frontend test files covered by the evaluated run. The repository contains additional test files that were not part of this run.

| Test File | What It Covers | Result |
| --- | --- | --- |
| test_api.py | API-level request and response behavior | Live-server-dependent cases deselected; remainder passed |
| test_database.py | Database-facing integration paths | Same deselection applied |
| test_pipeline.py | End-to-end pipeline flows | Same deselection applied |
| **Total** |  | **23 passed, 2 skipped** |

*Table 3.9: Integration Suite Breakdown by File*

Table 3.9 shows the integration suite. The four suites together account for 177 plus 106 plus 9 plus 23 equals 315 automated assertions, the figure reported in the consolidated results.

The manual instrument is broken down by case group in Table 3.10.

| Case IDs | Group | Cases | What the Cases Verify |
| --- | --- | --- | --- |
| FT-001 to FT-007 | Public pages and navigation | 7 | Home, About, Terms, and Privacy pages; logged-out navigation; theme and language toggles; the not-found page |
| AC-001 to AC-009 | Accounts | 9 | Sign-up validation, login, Google sign-in, password reset, multi-factor authentication, logout |
| FT-010 to FT-016 | EcoSim | 7 | Simulation wizard, location pickers, simulation runs, AI analysis, saving, PDF export |
| FT-017 to FT-025 | EnergyHub | 9 | Overview, trends, forecast chart, choropleth map and level switching, source and grid breakdowns, provincial demand, AI insight, chart explanations |
| FT-026 to FT-033 | Saved data and account pages | 8 | Saved simulations, dashboard, profile editing, password change, multi-factor-authentication setup page |
| AD-001 to AD-010 | Admin console | 10 | Users, analytics, configuration, usage, logs, and the forecast panel |
| IV-001 to IV-005 | Input validation | 5 | Letters in bill fields, oversized and negative consumption entries, missing location, and injection strings |
| DP-001 to DP-006 | Persistence and privacy | 6 | Saved data survives logout and new sessions and stays private to its owner |
| AI-001 to AI-006 | AI and connected services | 6 | AI narratives, waiting behavior, quota messaging, insight panels, map tiles, and Google sign-in |
| PT-001 to PT-009 | Timed performance observation | 9 | Observed responsiveness of page loads and key user flows |
| SO-001 to SO-014 | On-screen security behavior | 14 | Login walls, admin gating, password masking, HTTPS, error messages, and throttling as experienced by guest, user, and admin |
| UAT-1 to UAT-5 | Usability tasks | 5 | The five timed user journeys under explicit success standards |
| REG-01 to REG-06 | Regression checks | 6 | Previously fixed defects stay fixed |
| **Total** |  | **101** |  |

*Legend: FT functional test case; AC account case; AD admin console case; IV input-validation case; DP persistence and privacy case; AI connected-services case; PT timed-observation case; SO on-screen security case; UAT user acceptance task; REG regression check; HTTPS secure HTTP.*

*Table 3.10: Manual Evaluation Instrument by Case Group*

Table 3.10 shows the 101 manual cases grouped by module. The tracked functional test case ledger, which is the monitored list of functional test cases maintained by the evaluation, covered 69 cases across the system modules. On the final pass, after defect correction and retesting, 58 passed, 0 failed, and 11 were pending or not applicable. The pending items were the two responsive-viewport visual checks that were deferred until a live browser pass could be run, and nine machine learning notebook re-run items whose endpoints were verified at the API level instead. Table 3.11 shows the distribution of the cases by module.

| Module | Total | Passed | Failed | Pending or not applicable |
| --- | --- | --- | --- | --- |
| Authentication | 6 | 6 | 0 | 0 |
| EnergyHub | 10 | 10 | 0 | 0 |
| EcoSim | 13 | 13 | 0 | 0 |
| AI Intelligence | 7 | 7 | 0 | 0 |
| API Endpoints | 13 | 13 | 0 | 0 |
| Visualization | 9 | 7 | 0 | 2 |
| Machine Learning | 11 | 2 | 0 | 9 |
| **Total** | **69** | **58** | **0** | **11** |

*Table 3.11: Functional Test-Case Summary by Module*

Table 3.11 shows that all modules completed their cases without failures on the final pass. The representative verified behaviors are listed in Table 3.12.

| Behavior | Verified Result |
| --- | --- |
| Google OAuth (third-party sign-in) registration | Completed with JSON Web Token (JWT) issuance |
| Requests without a token, or with malformed or expired tokens | HTTP 401 returned |
| EcoSim municipality endpoint | Served 1,813 municipalities |
| Missing or invalid municipality identifiers | Clean 422 or 404 responses |

*Legend: 401 unauthenticated; 404 not found; 422 validation failed; JWT JSON Web Token; OAuth third-party sign-in.*

*Table 3.12: Representative Verified Functional Behaviors*

Six defects were found during the first execution pass. All were corrected and retested to closure as listed in Table 3.13.

| Defect ID | Triggering Check | Description | Severity | Status |
| --- | --- | --- | --- | --- |
| DEF-01 | TC-GEO-005 | Geothermal lookup of an invalid identifier returned 500 instead of 404 | Low | Fixed and retested |
| DEF-02 | TC-MAP-004 | Map with an invalid type returned 200 with an error body instead of a 4xx client-error status | Low | Fixed and retested |
| DEF-03 | TC-EH-010 | Invalid forecast metric was silently accepted and is now validated with 422 | Low | Fixed and retested |
| DEF-04 | TC-SEC-INJ-02 | The forecast run endpoint accepted injection-style strings silently and now validates them | Low | Fixed and retested |
| DEF-05 | TC-SEC-INJ-04 | The product recommendation endpoint echoed an unvalidated parameter and an allowlist was added | Low | Fixed and retested |
| DEF-06 | Manual copy review | The AI-quota error message referenced the wrong product name and the copy was corrected | Trivial | Fixed and retested |

*Legend: DEF defect identifier; TC-EH EnergyHub endpoint check; TC-GEO geothermal endpoint check; TC-MAP map-layer endpoint check; TC-SEC-INJ injection-input check; 200 request succeeded; 404 not found; 422 validation failed; 500 server error; 4xx client-side rejection.*

*Table 3.13: Defect Log with Triggering Checks*

Table 3.13 lists the defects that were found and corrected during testing together with the check that surfaced each one. All six were of low or trivial severity, and no critical or high-severity functional defect was recorded during the testing window.

**3.3.5 Database Testing**

Database testing covered persistence, privacy isolation, query performance, and the access control posture of the data tier. The persistence and privacy verifications of the instrument (DP-001 to DP-006) are listed in Table 3.14.

| Verification | Outcome |
| --- | --- |
| A saved simulation survives logout and re-login | Verified |
| Profile edits persist across sessions | Verified |
| The saved simulations and profile of one user are not visible to another account | Verified |
| The session survives a page refresh | Verified |
| Logout followed by the browser back button returns the user to the login page instead of the protected content | Verified |

*Table 3.14: Persistence and Privacy Verifications*

Direct query timings were also measured through the same Supabase REST path that the application uses, with ten repetitions per query. The results are presented in Table 3.15.

| Query | Mean | p50 | p95 | Notes |
| --- | --- | --- | --- | --- |
| regions select-1 | 160.8 ms | 70.6 ms | 962.9 ms | The p95 value is a cold-connection outlier and steady state is about 70 ms |
| municipalities select-10 | 100.7 ms | 74.0 ms | 317.9 ms | First-call warmup is visible |
| climate_monthly filtered | 78.1 ms | 76.1 ms | 88.0 ms | Indexed lookup with a tight distribution |

*Legend: p50 median; p95 95th percentile; ms milliseconds.*

*Table 3.15: Direct Supabase Query Timings with Ten Repetitions*

Table 3.15 shows the measured database query timings. The dominant cost is the network and TLS transit to the managed PostgreSQL endpoint, which sets a floor of around 70 milliseconds. Query execution itself is below one millisecond for these indexed single-table selects. For access control, the backend uses the Supabase service-role key for server-side reads, which is the correct pattern for a trusted backend, while client access passes through the FastAPI authentication dependencies. The publishable key exposed to the browser is safe by design as long as row-level security remains enabled on user-facing tables. Direct policy testing with an authenticated database session was recorded as an open item outside the scope of this cycle.

**3.3.6 API / External Service Testing**

The live endpoint sweep exercised every mounted API route with valid, invalid, boundary, and adversarial inputs. The composition of the sweep by check group is shown in Table 3.16.

| Check Group | Checks | What Was Exercised | Result |
| --- | --- | --- | --- |
| TC-API | 2 | Health and detailed health endpoints | Pass |
| TC-ES | 12 | EcoSim municipality, province, and barangay lists; simulation GET and POST; AI path; retrieval-augmented generation (RAG) path; body validation | Pass |
| TC-EH | 20 | EnergyHub overview, trends, forecast, map data, source and grid breakdowns, AI insight, model comparison, provincial demand, International Renewable Energy Agency (IRENA) series, the Meralco utility-rate endpoint, solar atlas, map explanation, chart analysis | Pass after fix; TC-EH-010 surfaced DEF-03 |
| TC-GEO | 5 | Geothermal plants, lookup, EcoSim and EcoHub summaries, invalid identifier | Pass after fix; TC-GEO-005 surfaced DEF-01 |
| TC-GS | 6 | Geospatial centroids, climate, hierarchy, province aggregate, and a missing-parameter 422 case | Pass |
| TC-MAP | 7 | Philippine Standard Geographic Code (PSGC) hierarchy, coverage, solar, wind, hydro, and geothermal layers, invalid map type | Pass after fix; TC-MAP-004 surfaced DEF-02 |
| TC-PROD | 4 | Product recommend, browse, audit, and a missing-type 422 case | Pass |
| TC-FC | 3 | Forecast run, backtest, and model list | Pass |
| TC-AUTH | 6 | Protected and simulation routes without a token and with a bad token | 401 returned as expected |
| TC-ADM | 6 | Admin users, analytics, config, usage, and logs without and with bad token | 401 or 403 returned as expected |
| TC-SEC-INJ | 4 | Injection-style parameters and a path-traversal probe | Pass after fix; TC-SEC-INJ-02 and TC-SEC-INJ-04 surfaced DEF-04 and DEF-05 |
| **Total** | **75 pre-fix checks; 82 checks post-fix** |  | **82 of 82 post-fix** |

*Legend: DEF defect identifier; TC-ES EcoSim endpoint check; TC-EH EnergyHub endpoint check; TC-GEO geothermal endpoint check; TC-GS geospatial endpoint check; TC-MAP map-layer endpoint check; TC-PROD product endpoint check; TC-FC forecast endpoint check; TC-AUTH unauthenticated-access check; TC-ADM admin-route check; TC-SEC-INJ injection-input check; TC-API health-endpoint check; 401 unauthenticated; 403 authenticated but not authorized; 422 validation failed; RAG retrieval-augmented generation; PSGC Philippine Standard Geographic Code; IRENA International Renewable Energy Agency; Meralco the Philippine distribution utility; GET/POST read and write HTTP methods.*

*Table 3.16: Endpoint Sweep Composition by Check Group*

Table 3.16 shows the composition of the endpoint sweep. Five injection-style probe families were rejected at the FastAPI validation boundary with HTTP 422 and were never echoed in the response bodies. CORS also behaved according to the allowlist. Preflight requests from an allowed origin received the correct header while a disallowed origin was blocked, both in the local environment and in production.

External service behavior was verified through a seventeen-scenario failure injection matrix, of which fifteen scenarios degraded gracefully. The complete matrix is presented in Table 3.17.

| ID | Injected Failure | Observed Behavior | Verdict |
| --- | --- | --- | --- |
| TC-FR-01 | Gemini outage on all models | Automatic fallback to live Groq and a response produced in 1,683 ms | Graceful |
| TC-FR-02 | EcoSim AI worker exceeds the hard timeout | Structured timeout fallback returned in 61 ms | Graceful |
| TC-FR-03 | All LLM providers down | Fallback analysis payload and the endpoint stays functional | Graceful |
| TC-FR-04a | Supabase client broken, detailed health | Status degraded with supabase error while staying HTTP 200 | Graceful |
| TC-FR-04b | Supabase down, municipality list | Still 200 from bundled CSV fallback with 1,813 items | Graceful |
| TC-FR-04c | Supabase down, EcoSim simulation | Clean 404 with readable message | Graceful |
| TC-FR-04d | Supabase down, protected route without token | 401 returned because auth fails before the database dependency | Graceful |
| TC-FR-05 | Redis client unavailable | Health reports not configured and map endpoints still serve 200 through the cache-miss path | Graceful |
| TC-FR-06 | NASA POWER outage at runtime | Not applicable; runtime climate is served from Supabase and bundled CSVs | Not applicable |
| TC-FR-07a | Invalid municipality identifier on EcoSim | Clean 404 message | Graceful |
| TC-FR-07b | Invalid identifier on geothermal lookup | 500 with sanitized body; mapped to 404 as DEF-01 | Degraded then fixed |
| TC-FR-08 | ML worker URL dead | 503 on the proxied path only and the rest of the API stays healthy | Graceful |
| TC-FR-09a | 70-request burst with a public X-Forwarded-For client-address header and intermittent Redis | No 429s; about 35 requests reached each of the two counters so neither reached the cap | Fail-open, recorded |
| TC-FR-09b | 70-request burst with a spoofed X-Forwarded-For header | No 429s; limiter bypassed | Bypass confirmed, recorded |
| TC-FR-09c | NullRedis in-memory fallback plus public forwarded header, 75-request burst | Exactly 60 allowed then 429; the fallback counter enforced the cap correctly | Graceful |
| TC-FR-09d | Throwing Redis, 75-request burst | Exactly 60 allowed then 429; exception path correct | Graceful |
| TC-FR-10a | Body above 1 MB | 413 returned | Graceful |
| TC-FR-10b | Malformed JSON body | 422 returned | Graceful |
| TC-FR-10c | Non-integer path parameter | 422 returned | Graceful |

*Legend: DEF defect identifier; TC-FR failure-recovery scenario; 200 request succeeded; 401 unauthenticated; 404 not found; 413 body too large; 422 validation failed; 429 rate limited; 500 server error; 503 dependency unavailable; ms milliseconds; MB megabytes; XFF X-Forwarded-For client-address header; NullRedis in-memory fallback; LLM large language model; Redis rate-limit cache store.*

*Table 3.17: Complete Failure-Injection Matrix of Seventeen Scenarios*

Table 3.17 shows how the system behaved when its dependencies were made to fail. Fifteen of the seventeen scenarios degraded gracefully, one degraded-status case was corrected and retested as defect DEF-01, and two security-relevant rate-limiting behaviors were recorded and are summarized under the security section. NASA POWER is not a runtime dependency, so its outage path was verified as not applicable.

**3.3.7 Performance Testing**

Single-user warm-cache latency was benchmarked with thirty repetitions per endpoint and five for the language model backed paths. The measured results are shown in Table 3.18.

| Endpoint | n | Mean (ms) | p50 | p95 | Status |
| --- | --- | --- | --- | --- | --- |
| GET /health | 30 | 4.8 | 1.8 | 3.6 | Pass |
| GET /energyhub/overview | 30 | 6.3 | 5.9 | 8.6 | Pass |
| GET /energyhub/forecast | 30 | 3.7 | 3.5 | 6.2 | Pass |
| GET /energyhub/trends | 30 | 6.8 | 6.3 | 9.6 | Pass |
| GET /energyhub/map-data | 30 | 37.5 | 37.1 | 39.4 | Pass |
| GET /ecosim/municipalities | 30 | 49.7 | 44.1 | 109.2 | Pass |
| GET /geothermal/5441 | 30 | 222.1 | 219.1 | 239.3 | Pass |
| GET /map/solar | 30 | 57.1 | 57.7 | 60.4 | Pass |
| GET /forecast/models | 30 | 82.2 | 78.5 | 103.4 | Pass |
| GET /ecosim/ (full simulation) | 5 | 450.2 | 449.5 | 454.5 | Pass, under 3 s |
| GET /ecosim/ai | 5 | 458.0 | 451.3 | 475.9 | Pass, under 5 s |
| GET /energyhub/ai-insight with LLM | 5 | 676.8 | 44.3 | 3,207.9 | Conditional, see note |

*Legend: n number of repetitions; p50 median; p95 95th percentile; ms milliseconds; LLM large language model; GET/POST read and write HTTP methods.*

*Table 3.18: API Endpoint Latency for a Single User with Warm Cache in Milliseconds*

Table 3.18 shows the measured endpoint latencies. The p95 value of the AI insight endpoint reflects one full language model round-trip of about 3.2 seconds, and the anonymous quota responses of the same endpoint were already consumed during the run, so the p95 column mixes a real model call with quota responses. Standard endpoints averaged around 49 milliseconds while the mean across all measured endpoints was around 104 milliseconds, which is consistent with the figure reported in section 3.9.

Additional performance findings outside the endpoint benchmark are listed in Table 3.19.

| Finding | Value | Note |
| --- | --- | --- |
| Initial frontend bundle | Single JavaScript chunk of about 1.91 MB gzip-compressed | Before optimization |
| Entry bundle after code-splitting | Around 611 kB with lazy-loaded route and vendor chunks | Route-based splitting applied afterwards |
| Serverless cold start on production smoke | About 0.8 to 3.8 seconds | Observed on deployed endpoints |
| Supabase cold connection | Spikes of about 963 ms settling to about 70 ms | First-call warmup |
| EcoSim and AI user flow | About 612 ms end-to-end | Well inside the interactive response budget |

*Legend: ms milliseconds; MB megabytes.*

*Table 3.19: Additional Performance Findings*

Stepped-concurrency load was also executed against the local backend using Locust with real municipality identifiers and a mixed workload weighted toward the heavier endpoints. The results are presented in Table 3.20.

| Concurrent Users | Requests | Failures | Avg (ms) | p95 | Throughput |
| --- | --- | --- | --- | --- | --- |
| 1 | 96 | 0 | 90 | 600 | 3.3 RPS |
| 10 | 790 | 0 | 519 | about 1,400 | 13.3 RPS |
| 25 | 769 | 0 | 1,637 | about 3,300 | 13.0 RPS |
| 50 | 614 | 0 | 3,838 | about 7,000 | 10.5 RPS |
| 75 | 657 | 0 | 5,582 | about 8,700 | 11.0 RPS |
| 100 | 814 | 0 | 5,591 | about 8,900 | 13.7 RPS |

*Legend: p95 95th percentile; RPS requests per second; ms milliseconds.*

*Table 3.20: Stepped-Concurrency Load Results at Sixty Seconds per Level*

Table 3.20 shows the results of the stepped-concurrency load test. Every request at every level succeeded with zero server errors, timeouts, or connection resets, which means the system degrades gracefully under load because latency inflates while requests queue rather than fail. Throughput plateaus at around 11 to 14 requests per second on a single worker, which places the interactive ceiling at around 10 to 15 concurrent users and the three-second p95 threshold near 25 users. Horizontal scaling is the documented path beyond that point. The rate limiter also returned HTTP 429 correctly under a sustained same-source burst.

**3.3.8 Security Testing**

Security testing combined static analysis of the backend through Bandit, dependency audits through pip-audit and npm audit, a live probe suite of eighteen executed probes of which sixteen passed with one warning and informational notes, a JSON Web Token (JWT) validation matrix, cross-origin resource sharing (CORS) preflight verification, SQL injection style inputs, error-body inspection, and a secrets-handling review. All probes were read-only or self-cancelling. The live probe coverage is broken down in Table 3.21.

| Probe Family | What Was Exercised | Result |
| --- | --- | --- |
| JWT validation matrix | No token, malformed token, signature-stripped (alg:none) token, wrong-signature token, expired token, and a validly-signed token for a nonexistent user | All rejected with 401 |
| Security headers | X-Content-Type-Options, X-Frame-Options, HSTS, CSP, and Referrer-Policy | 5 of 5 present locally and in production |
| CORS preflight | Allowed origin and disallowed origin | Allowed origin receives the header; disallowed origin blocked |
| Documentation exposure | API documentation reachability | Informational notes recorded |
| Error-body inspection | Stack, path, and host leakage | Sanitized detail and request_id fields only |
| Server banner | Version disclosure | Warning recorded |
| Injection input families | Five SQL injection style probe families | Inert, rejected as validation errors, never echoed |
| Rate-limit burst | Sustained same-source burst | 60 per minute allowed then 429 |

*Legend: 401 unauthenticated; 429 rate limited; JWT JSON Web Token; alg:none signature-stripped token; CORS cross-origin resource sharing; HSTS HTTP strict-transport-security header; CSP content security policy; SQL injection hostile query string.*

*Table 3.21: Live Security Probe Coverage*

The verified controls are summarized in Table 3.22.

| Verified Control | Result |
| --- | --- |
| No token returns HTTP 401 on all protected and admin routes | Pass |
| Malformed, signature-stripped (alg:none), wrong-signature, and expired JWTs return 401 | Pass |
| Validly-signed JWT for a nonexistent user returns 401 through the server-side user check | Pass |
| Security headers (X-Content-Type-Options, X-Frame-Options, HSTS, CSP, Referrer-Policy) | 5 of 5 present locally and in production |
| CORS allowlist enforced and disallowed origin preflight returns 400 | Pass locally and in production |
| SQL injection style inputs | Stayed inert, rejected as validation errors, and never echoed |
| Error bodies | Sanitized detail and request_id fields with no stack, path, or host leakage |
| Body above 1 MB returns 413 and malformed JSON returns 422 | Pass |
| Rate limiting | 60 per minute enforced with 429 on healthy Redis and clean in-memory fallback |
| Secrets handling | No env or key files tracked in git and only example env files committed |
| Session security | Logout invalidates the session and protected content is not re-served through the back button |
| Per-user data isolation | Cross-account visibility denied under the data-isolation cases DP-003 and DP-004 and the other-user's-data case SO-012 |

*Legend: DP persistence and privacy case; SO on-screen security case; 400 bad request; 401 unauthenticated; 413 body too large; 422 validation failed; 429 rate limited; MB megabytes; JWT JSON Web Token; alg:none signature-stripped token; CORS cross-origin resource sharing; HSTS HTTP strict-transport-security header; CSP content security policy; SQL injection hostile query string; Redis rate-limit cache store.*

*Table 3.22: Verified Security Controls*

The advisories, hardening items, and deferred security testing recorded during the cycle are listed in Table 3.23.

| Item | Detail | Status |
| --- | --- | --- |
| Frontend dependency advisories | Seven advisories: one critical and one high confined to development-only dependencies, and five moderate including router advisories that ship to runtime with available non-major fixes | Recorded |
| Backend dependency advisories | Known advisories reported by pip-audit | Recorded in the findings register, the issue log of the evaluation |
| X-Forwarded-For proxy-header trust assumption | Affects rate-limit attribution under forwarded client-address headers | Open hardening item |
| Fail-open dependency checks | Two dependency-check paths fail open during dependency outage | Open hardening item |
| Row-level security policy testing | Requires an authenticated database session | Deferred |
| TLS testing | Production HSTS verified; further certificate testing deferred | Deferred |
| Fuzzing and CSRF coverage | Beyond CORS preflight verification | Deferred |

*Legend: CORS cross-origin resource sharing; CSRF cross-site request forgery; TLS transport layer security; HSTS HTTP strict-transport-security header; XFF X-Forwarded-For client-address header.*

*Table 3.23: Security Advisories, Hardening Items, and Deferred Testing*

Table 3.23 lists the security items that remain open or deferred. These items affect enforcement robustness under adverse conditions, while the authentication, authorization, injection, CORS, header, and error-sanitization controls in Table 3.22 were all verified as working under live testing.

**3.3.9 Compatibility Testing**

Compatibility coverage was defined in the instrument across two matrices, namely four target browsers consisting of Google Chrome, Microsoft Edge, Mozilla Firefox, and Safari, and four device classes consisting of desktop, laptop, tablet, and smartphone. The execution status is reported in Table 3.24.

| Aspect | Status or Evidence |
| --- | --- |
| Application type | React 18 and Vite single-page application delivered as a standards-compliant production build targeting evergreen, meaning continuously updated, browsers |
| HTTPS and security headers | Verified on the production deployment, 5 of 5 present |
| Responsive layout support | Tailwind responsive utility classes applied throughout the interface |
| Production smoke parity | Identical API behavior through the deployed edge path, meaning the Vercel hosting layer closest to the user |
| Scripted 375 and 768 pixel viewport checks | Deferred pending a live browser pass; the one outstanding functional item in the tracked functional test case ledger |
| Per-browser version matrix | Exercised through the machines of the evaluators rather than a controlled browser-farm run |
| Real-device and real-browser exposure | The 100-respondent household evaluation and the ten IT expert evaluators used the deployed system on their own equipment; no compatibility defect reported |

*Legend: HTTPS secure HTTP.*

*Table 3.24: Compatibility Testing Status*

Table 3.24 shows that no cross-browser rendering or device-blocking defect was recorded during the testing window, and the formal per-browser matrix remains listed as the compatibility evidence to be completed before production rollout.

**3.3.10 Usability and User Interface Testing**

Usability testing proceeded on two tracks. The scripted user-acceptance tasks (UAT-1 to UAT-5) exercised the five core user journeys with explicit success standards as listed in Table 3.25.

| Task | What the User Was Asked to Do | Success Standard |
| --- | --- | --- |
| UAT-1 | Locate the latest national consumption figure in EnergyHub | Within about 60 seconds |
| UAT-2 | Complete an EcoSim simulation for Tagaytay City, Cavite with a 2,500 peso monthly bill | Within about three minutes |
| UAT-3 | Identify the predicted 2030 consumption from the forecast chart | Within about 90 seconds |
| UAT-4 | Identify the province with the highest solar potential from the map | Within about two minutes |
| UAT-5 | Locate and restate the AI generated explanation after a simulation | Within the session |

*Legend: UAT user acceptance task.*

*Table 3.25: Usability Tasks and Success Standards*

User interface behavior was also verified at the component level. The evaluated Vitest files cover chart, theme, and internationalization behavior; the theme and language toggles were exercised; empty-location and invalid-input states produce clear guidance instead of errors; the not-found route renders a friendly page; and password fields mask input. The participant-scale usability results, which are the primary evidence for usability, are reported in sections 3.8 and 3.9.2 to 3.9.5 and are cross-referenced in Table 3.26.

| Measure | Result | Interpretation |
| --- | --- | --- |
| Household usability weighted mean (100 respondents) | 4.73, standard deviation 0.38 | Excellent |
| Comparison-with-prior-methods weighted mean | 4.79, standard deviation 0.32 | Excellent |
| Instrument reliability | Cronbach's alpha 0.923 and 0.868 | Reliable |
| One-sample right-tailed t-test against the neutral midpoint | t(99) = 55.47, p below 0.001 | Significant |

*Legend: alpha Cronbach's reliability coefficient; t(99) one-sample t-test at 99 degrees of freedom.*

*Legend: 4.21-5.00 Excellent, 3.41-4.20 Very Good, 2.61-3.40 Satisfactory, 1.81-2.60 Fair, 1.00-1.80 Poor*

*Table 3.26: Participant Usability Results as Cross-Referenced*

**3.3.11 ISO/IEC 25010 Software Quality Evaluation**

Software quality was evaluated against eight selected ISO/IEC 25010:2023 characteristics, namely functional suitability, performance efficiency, compatibility, reliability, security, maintainability, flexibility, and safety, using a five-point scale interpreted on the evaluation criteria defined in section 3.5. It should be noted that flexibility and safety are drawn from the quality-in-use model of the standard and were included to cover deployment adaptability and risk-mitigation concerns relevant to a decision-support system.

Two complementary evaluations were performed as summarized in Table 3.27.

| Evaluation | Score | Interpretation | Notable Detail |
| --- | --- | --- | --- |
| Independent IT expert evaluation (ten experts, eight characteristics) | Weighted mean 4.46, standard deviation 0.60 | Excellent | Led by compatibility 4.65, maintainability 4.60, and safety 4.50; lowest was flexibility 4.20 interpreted as Very Good |
| Internal technical self-evaluation by the development team | 3.60 out of 5.0 | Good | Scores of 4 for functional suitability, performance, reliability, and security; scores of 3 for compatibility, usability, maintainability, and portability |

*Legend: 4.21-5.00 Excellent, 3.41-4.20 Very Good, 2.61-3.40 Satisfactory, 1.81-2.60 Fair, 1.00-1.80 Poor*

*Table 3.27: ISO/IEC 25010 Evaluation Summary*

Table 3.27 summarizes the two evaluations. The expert result supports the engineering finding that horizontal scalability is the main growth area of the system, while the internal scores reflect the deductions already evidenced in this chapter, namely the single-worker concurrency ceiling, the deferred responsive-viewport checks, and the dependency and hardening items noted in section 3.3.8. The gap between the internal and external scores is also informative because the independently assessed quality of the system is higher than the conservative technical assessment of the team. The per-statement detail of the expert evaluation is reported in section 3.9.6 onwards.

**3.3.12 Testing Results Summary**

| Category | Instrument or Method | Result |
| --- | --- | --- |
| Functional | 69 tracked cases plus 315 automated assertions plus 82-endpoint sweep | 58 pass, 0 fail, 11 pending and all suites green |
| Input validation and injection | IV-001 to IV-005 plus adversarial sweep inputs | Rejected at the boundary with 422 and no echo or crash |
| Persistence and privacy | DP-001 to DP-006 | Persist, isolate, and expire correctly |
| API and external services | 82 of 82 sweep plus seventeen-scenario failure matrix | 15 of 17 graceful and 2 items logged to the findings register |
| Performance | Thirty-repetition latency and stepped load from 1 to 100 users | About 49 ms standard mean and 104 ms overall with 0 failures at 100 users and an 11 to 14 RPS plateau |
| Security | 18 live probes plus scanners plus JWT, CORS, and injection matrix | 16 pass, 1 warning and all core controls verified with hardening items logged |
| Compatibility | Browser and device matrices plus production smoke | No defect found and the formal per-browser matrix partially executed |
| Usability and UI | UAT-1 to UAT-5 plus component tests plus participant evaluation | Tasks defined with standards, component suite green, and participant usability at 4.73 of 5 |
| Regression | REG-01 to REG-06 plus defect retests | All six defects closed and no regression reported |
| ISO/IEC 25010 | Eight characteristics scored by ten IT experts plus internal self-evaluation | Expert mean of 4.46 of 5 interpreted as Excellent and internal 3.60 of 5 interpreted as Good |
| Machine learning | Six-model held-out benchmark plus cross-validation plus diagnostics | See section 3.3.13 for the full evaluation |

*Legend: IV input-validation case; DP persistence and privacy case; UAT user acceptance task; REG regression check; 422 validation failed; RPS requests per second; ms milliseconds; JWT JSON Web Token; CORS cross-origin resource sharing; ISO/IEC 25010 software-quality standard.*

*Table 3.28: Consolidated Testing Results Summary*

Table 3.28 shows that the overall verdict of the testing cycle is passed and ready for deployment within the stated constraints. No critical or high-severity functional defect remained open after retesting, and the system degraded gracefully under every survivable failure that was injected. The residual items, namely a formal per-browser matrix, direct row-level security policy verification, production-scale load evidence, and the logged security-hardening items, are documented as the boundary of the current evaluation rather than as failures of it.

**3.3.13 Machine Learning Evaluation Results and Discussion**

Three components were evaluated separately so that they are not confused with one another, as summarized in Table 3.29.

| Component | Evaluated As | Evaluation Basis |
| --- | --- | --- |
| Deployed ARIMA(1,1,1) forecaster for national electricity consumption, peak demand, and renewable generation | Predictive model | Held-out benchmark against five alternatives, cross-validation, diagnostics, robustness, and serving measurement |
| Groq and Gemini generative AI recommendation layer | Generative component | Output contract, latency, and resilience criteria |
| EcoSim solar, wind, and hydro potential scoring | Physics-based estimators and multi-criteria decision analysis | Not a trained model; a geothermal random-forest classifier exists in the codebase but was excluded from this evaluation |

*Legend: ARIMA autoregressive integrated moving average.*

*Table 3.29: Components of the Machine Learning Evaluation*

Table 3.29 separates the components of the evaluation. Because the forecasting component predicts continuous quantities, the classifier-specific items in the following subsections are marked as not applicable and the correct time-series substitute is reported in their place.

**3.3.13.1 Dataset Description and Distribution**

The modeling dataset is the Philippine Department of Energy national energy statistics that was preprocessed into a single modeling table. The profile of the dataset is summarized in Table 3.30.

| Property | Value |
| --- | --- |
| Rows | 23, one record per year |
| Columns | 45 |
| Coverage | 2003 to 2025, annual |
| Duplicate rows | 0 |
| Missing cells | 15, all inside derived lag, growth, and rolling columns where the earliest years have no prior-year source |
| Primary target | total_consumption_gwh, from 52,941 to 126,941 gigawatt-hours (GWh) |
| Secondary targets | total_peak_demand_mw and renewable_generation_gwh |
| Consumption compound annual growth rate (CAGR), 2003 to 2024 | 4.252 percent, with a mean absolute yearly change of 4.49 percent, a maximum of 10.17 percent, and a minimum of negative 4.04 percent |

*Legend: GWh gigawatt-hours; CAGR compound annual growth rate.*

*Table 3.30: Forecasting Dataset Profile*

The evaluation protocol split the data by time as shown in Table 3.31.

| Split | Years | Samples | Share |
| --- | --- | --- | --- |
| Training | 2003 to 2020 | 18 | 81.8 percent |
| Held-out test | 2021 to 2024 | 4 | 18.2 percent |
| Set aside | 2025 | 1 | Retained in the file but outside the historical test metrics |

*Table 3.31: Train and Test Split Protocol*

Table 3.31 shows the temporal split of the dataset. Classes and categories, per-class distribution, and class balance are not applicable to this evaluation because the target is a continuous quantity. The corresponding concern for a continuous target is the sample size itself, which is 18 training points and a four-point test window where each observation carries 25 percent of the reported error. The small sample is the dominant constraint of this evaluation because it rules out data-hungry learners and requires validation methods that are appropriate for time-series data instead of a large random holdout.

**3.3.13.2 Data Preprocessing Results**

| Step | Applied | Rationale or Evidence |
| --- | --- | --- |
| Temporal alignment to annual records | Yes | 23 rows, one per year, no gaps or duplicates |
| Missing-value handling | Structural | The 15 empty cells exist only where lag and rolling windows reach before 2003 and affected rows are excluded where needed |
| Feature engineering | Yes | Lag-1 and lag-2, first difference, year-on-year growth, three and five-year rolling means, capacity margin, renewable share, and years-since-2003 give the comparison models autoregressive memory |
| Differencing for stationarity | Inside ARIMA | The d equals 1 term performs first-order differencing on the trended series |
| Categorical encoding | Not applicable | No categorical predictors exist |
| Feature scaling | Deliberately skipped | The evaluated models are scale-invariant or tree-based and scaling would add a step with no effect |
| Augmentation | Not used | Fabricating national statistics would corrupt the evaluation |

*Legend: ARIMA autoregressive integrated moving average.*

*Table 3.32: Data Preprocessing Steps and Justifications*

Table 3.32 shows that preprocessing was intentionally minimal because the data are already clean national aggregates. The substantive work was the construction of autoregressive features for the comparison models and the internal differencing that ARIMA applies. Scaling was not applied because the evaluated models are scale-invariant or tree-based, and adding the step would not change their behavior.

**3.3.13.3 Machine Learning Model Configuration**

Six models were configured and executed on the same data by the evaluation pipeline as listed in Table 3.33.

| Model | Type | Configuration |
| --- | --- | --- |
| **ARIMA(1,1,1) production model** | Statistical time-series | Order (1,1,1), optimal in the searched AIC and BIC grid as shown in section 3.3.13.10, fitted with statsmodels ARIMA, with native 95 percent prediction intervals |
| Linear Trend Regression | Baseline | Ordinary least squares of consumption on years_since_2003 |
| Naive with Drift | Baseline | Random-walk-with-drift extrapolation |
| Holt Linear Smoothing | Statistical | Exponential smoothing with additive trend |
| SARIMAX(1,1,1) with exogenous input | Statistical with exogenous (external-driver) regressors | ARIMA errors with exogenous regressor columns |
| Random Forest Regression | ML baseline | RandomForestRegressor on engineered lag and rolling features |

*Legend: AIC Akaike information criterion; BIC Bayesian information criterion; SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.33: Evaluated Model Configurations*

Table 3.33 lists the evaluated model configurations. None of the models use iterative training loops and each fits in a single mathematical step, so training epochs and loss values are not applicable. The input features of the statistical models are the history of the target series itself, while the random forest baseline additionally uses the engineered lag and rolling features described in section 3.3.13.2. The production serving path does not retrain per request. The deployed predictor loads precomputed forecast artifacts containing point forecasts with confidence intervals that are registered in the model registry, so training cost is an offline concern and not a request-time latency concern. The hardware and software environment is given in Table 3.4.

**3.3.13.4 Model Training Results**

Training accuracy, training loss, validation accuracy, validation loss, and the number of epochs are not applicable to these models because they are not trained by gradient descent. The correct substitutes, which are fit time and residual diagnostics, are reported instead. The measured fit times are presented in Table 3.34.

| Model | Fit time (s) |
| --- | --- |
| Linear Trend Regression | 0.0374 |
| Naive with Drift | 0.00005 |
| Holt Linear Smoothing | 0.0160 |
| ARIMA(1,1,1) | 0.0859 |
| SARIMAX(1,1,1) with exogenous input | 0.0704 |
| Random Forest Regression | 0.1026 |

*Legend: SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.34: Measured Model Fit Times*

The fitted parameters and diagnostics of the production model are presented in Table 3.35.

| Parameter or Diagnostic | Value | Reading |
| --- | --- | --- |
| ar.L1 | About 0.9999 | Near-unit autoregressive coefficient |
| ma.L1 | About negative 0.9972 | Near-cancelling moving-average coefficient |
| sigma squared | About 1.032 times ten to the seventh | Residual variance |
| Akaike information criterion | 325.63 |  |
| Bayesian information criterion | 328.13 |  |
| Ljung-Box test at lag 5 | Statistic 0.258, p-value 0.9984 | No evidence of residual autocorrelation |

*Legend: ar.L1 autoregressive coefficient; ma.L1 moving-average coefficient; sigma squared residual variance; Ljung-Box residual autocorrelation test; p-value significance probability.*

*Table 3.35: ARIMA(1,1,1) Fitted Parameters and Diagnostics*

Table 3.35 shows that the residuals carry no evidence of autocorrelation, which indicates an adequate in-sample fit. On the question of overfitting, the near-unit autoregressive coefficient paired with a near-cancelling moving-average coefficient is the usual signature of a process that is barely distinguishable from a random walk with drift. This diagnostic foreshadowed the test-set result where the simpler trend and drift baselines matched or slightly exceeded the ARIMA model. The random forest baseline showed the opposite pattern and fitted the training window at 1.45 percent mean absolute percentage error while performing at only 10.94 percent on the held-out data. This gap of about 9.5 points supports the use of parsimonious statistical models at this sample size.

**3.3.13.5 Model Testing Results**

Test accuracy, precision, recall, F1-score, specificity, and the area under the receiver-operating-characteristic curve (ROC-AUC) are not applicable to this evaluation because these metrics evaluate classifiers while the model predicts amounts. The correct regression metrics are the mean absolute error (MAE), root mean squared error (RMSE), mean absolute percentage error (MAPE), and the coefficient of determination (R-squared), together with direction-of-change accuracy as a classification-style substitute. The held-out test results for national consumption from 2021 to 2024 are presented in Table 3.36.

| Model | MAE (GWh) | RMSE (GWh) | MAPE (percent) | R-squared |
| --- | --- | --- | --- | --- |
| **Linear Trend Regression** | **5,993.83** | **7,342.10** | **4.965** | **0.1054** |
| Holt Linear Smoothing | 6,557.72 | 7,997.68 | 5.435 | negative 0.0615 |
| Naive with Drift | 6,709.32 | 8,128.45 | 5.566 | negative 0.0965 |
| ARIMA(1,1,1) production model | 6,829.09 | 8,257.12 | 5.667 | negative 0.1315 |
| Random Forest Regression | 13,118.37 | 15,349.45 | 10.937 | negative 2.9099 |
| SARIMAX(1,1,1) with exogenous input | 16,721.10 | 18,787.73 | 14.031 | negative 4.8577 |

*Legend: GWh gigawatt-hours; MAE mean absolute error; RMSE root mean squared error; MAPE mean absolute percentage error; R-squared coefficient of determination; SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.36: Held-Out Test Results for Total Consumption from 2021 to 2024*

The per-year errors of the production model on the test window are shown in Table 3.37.

| Test Year | Forecast Error |
| --- | --- |
| 2021 | negative 1.45 percent |
| 2022 | negative 3.69 percent |
| 2023 | negative 6.59 percent |
| 2024 | negative 10.94 percent |

*Table 3.37: Per-Year Forecast Errors of the Production Model*

Table 3.37 shows that the error grew monotonically with the forecast horizon. The secondary targets under the same protocol showed that peak demand was best served by SARIMAX with exogenous regressors at 3.868 percent MAPE with an R-squared of 0.4124 against 5.611 percent for ARIMA with a mean absolute error of about 1,019.66 megawatts, and renewable generation was best served by the linear trend and Holt models at 9.405 percent against 13.665 percent for ARIMA with a mean absolute error of about 3,597.39 gigawatt-hours. Directional accuracy, which is the classification-style substitute, was 8 of 11 fold and test years or 72.7 percent for ARIMA, against 42.9 to 50.0 percent for the linear trend comparators.

The results indicate that ARIMA finished fourth of six on the consumption test at 5.667 percent MAPE, and in absolute terms the top four models all err by around five to six percent of annual national consumption, which is acceptable for a four-year horizon forecast on annual data. Every model under-forecast every test year because the test years coincided with the post-2020 acceleration in demand that purely extrapolative models trained on 2003 to 2020 systematically underestimate. The conclusion supported by these results is that point accuracy on 2021 to 2024 is modest. The direction of growth is captured but the magnitude of the acceleration is not, and this is a limitation of the data regime that is shared by every comparator and not a defect of one model.

**3.3.13.6 Confusion Matrix Analysis**

A conventional confusion matrix is not applicable to this evaluation because there are no classes to be confused. The valid substitute is a directional two-by-two matrix on the unique evaluation years from 2015 to 2024 covering the cross-validation folds and the test set, which is presented in Table 3.38.

| Actual Direction and Predicted Direction | Up | Down |
| --- | --- | --- |
| **Up** | 7 | 2 |
| **Down** | 1 | 0 |

*Table 3.38: Directional Matrix of the Forecast Direction of Change*

Table 3.38 presents the directional matrix of the forecast direction of change. The model called the correct direction in 8 of 10 unique years or 80 percent. The informative cells are the two years 2023 and 2024 where the model predicted a decrease while actual demand accelerated upward, and the single year 2020 where the only down year in the dataset, the negative 4.04 percent pandemic-year contraction, was predicted upward. Both error classes share one cause, which is that regime changes with no precedent in the 18 training years cannot be anticipated by an extrapolative model.

**3.3.13.7 Class-Level Performance**

Per-class precision, recall, F1-score, and support are not applicable to this evaluation. The structurally equivalent breakdown is performance per target under one fixed specification, which is shown in Table 3.39.

| Target | ARIMA MAPE | Best model | Best MAPE | Reading |
| --- | --- | --- | --- | --- |
| total_consumption_gwh | 5.667 percent | Linear Trend | 4.965 percent | Smooth series and the fixed order is adequate |
| total_peak_demand_mw | 5.611 percent | SARIMAX with exogenous input | 3.868 percent | Exogenous regressors add value here |
| renewable_generation_gwh | 13.665 percent | Linear Trend and Holt | 9.405 percent | Volatile and break-prone so it is the hardest target |

*Legend: MAPE mean absolute percentage error; SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.39: Per-Target Performance as the Regression Equivalent of Per-Class Scores*

Table 3.39 shows the per-target performance of the same ARIMA specification. A single fixed order is a reasonable default for the smooth consumption and demand aggregates but a poor choice for the renewable series, and per-target order selection is a concrete improvement path. The regression analogue of a confidence-quality score is the 95 percent prediction-interval coverage, which was 3 of 4 held-out points or 75 percent, with the acceleration year 2024 falling outside the band. This indicates that the intervals are slightly overconfident under regime acceleration, which is the same condition that degrades the point forecasts.

**3.3.13.8 Cross-Validation Results**

Random k-fold validation is not valid for time-series data because it leaks future information, so expanding-window time-series cross-validation over seven folds was used instead. The results are shown in Table 3.40.

| Model | Folds | Mean APE (percent) | Std dev |
| --- | --- | --- | --- |
| Holt | 7 | 3.525 | 3.496 |
| Naive with Drift | 7 | 3.584 | 2.535 |
| **ARIMA(1,1,1)** | 7 | **3.607** | **2.512** |
| Linear Trend | 7 | 5.861 | 3.917 |

*Legend: APE absolute percentage error; ARIMA autoregressive integrated moving average.*

*Table 3.40: Expanding-Window Cross-Validation Using Absolute Percentage Error*

Table 3.40 shows the expanding-window cross-validation results. Across the folds the top three methods are statistically indistinguishable because their means are within 0.09 percentage points of each other, while the linear trend model that won the single split is clearly the weakest under resampling. This means the single four-year leaderboard is not stable evidence, and the cross-validated showing of ARIMA, which has a competitive mean and the tightest deviation together with the naive drift baseline, is the fairer justification for retaining it as long as the intervals remain calibrated.

**3.3.13.9 Model Comparison**

| Rank | Model | Test MAPE (percent) | Key differentiator |
| --- | --- | --- | --- |
| 1 | Linear Trend | 4.965 | Best on this split but weakest in cross-validation |
| 2 | Holt | 5.435 | Best cross-validation mean and consistent |
| 3 | Naive with Drift | 5.566 | Near-zero cost and hard to beat |
| 4 | **ARIMA(1,1,1)** | **5.667** | The only model emitting calibrated intervals with top-tier cross-validation |
| 5 | Random Forest | 10.937 | 18 training rows are far below its data appetite |
| 6 | SARIMAX with exogenous input | 14.031 | Exogenous regressors extrapolated poorly |

*Legend: MAPE mean absolute percentage error; SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.41: Consolidated Model Comparison for the Consumption Target*

Table 3.41 shows the consolidated ranking of the six models. Accuracy, precision, recall, F1-score, and ROC-AUC comparisons are not applicable and the comparison uses regression error metrics instead. The production model does not dominate on point accuracy, and no reading of these tables supports such a claim. Its case rests on three properties that the baselines lack, namely a likelihood-based fit with diagnostic testing as reported in section 3.3.13.4, native prediction intervals that are surfaced to users through the confidence fields of the API, and cross-validation performance equal to the best baselines. The failure of SARIMAX on consumption together with its win on peak demand shows that the value of exogenous regressors is target-dependent, and the negative 2.91 R-squared of the random forest confirms that tree ensembles are not appropriate at this sample size.

**3.3.13.10 Hyperparameter Evaluation**

The ARIMA order was selected through an AIC and BIC grid over p, d, and q values from zero to two with d fixed at one, because the trended series requires first-order differencing and annual data has no within-year seasonality to search over. The grid results are shown in Table 3.42.

| Order | AIC | BIC |
| --- | --- | --- |
| **(1,1,1)** | **325.63** | **328.13** |
| (2,1,1) | 327.47 | 330.80 |
| (1,1,2) | 329.13 | 332.46 |
| (2,1,2) | 331.01 | 335.17 |
| (0,1,0) | 332.49 | 333.32 |
| (1,1,0) | 332.82 | 334.49 |
| (0,1,1) | 332.92 | 334.58 |
| (0,1,2) | 334.29 | 336.79 |
| (2,1,0) | 334.36 | 336.86 |

*Legend: AIC Akaike information criterion; BIC Bayesian information criterion.*

*Table 3.42: ARIMA Order Search Using the AIC and BIC Grid*

Table 3.42 shows that the (1,1,1) order is the information-criterion-optimal choice within the searched grid and is 1.8 AIC points ahead of the next candidate, which makes the selection evidence-based rather than an arbitrary default. The search is appropriate but narrow because d was fixed and per-target orders were not searched, and both are noted as improvement paths.

**3.3.13.11 Feature Importance and Model Explainability**

The ARIMA model is interpretable through its fitted parameters rather than feature importances, as summarized in Table 3.43.

| Item | Value | Interpretation |
| --- | --- | --- |
| ar.L1 | About 1.00 | The level next year is about the level this year plus drift |
| ma.L1 | About negative 1.00 | Shocks are absorbed almost fully within one step, describing a smooth-trend process with fast shock decay |
| Random Forest top features | consumption_lag1 and the rolling means | The same recent-level information that ARIMA uses, which the forest can only memorize at 18 observations |
| SHAP and LIME explainability frameworks | Not applied | At 18 observations with fewer than ten features they would add machinery without adding insight |
| Dominant predictor | Most recent consumption level and its drift | Shared across all models |

*Legend: ARIMA autoregressive integrated moving average; ar.L1 autoregressive coefficient; ma.L1 moving-average coefficient.*

*Table 3.43: Model Parameters and Feature Importance*

**3.3.13.12 Error Analysis**

Misclassification patterns, false positives, and false negatives are not applicable to this evaluation. The regression error taxonomy is presented in Table 3.44 instead.

| Error pattern | Frequency | Likely cause |
| --- | --- | --- |
| Under-forecast of magnitude across all models and test years | 24 of 24 model-years | Post-2020 demand acceleration absent from the 2003 to 2020 training window |
| Error growth with horizon | Monotone from negative 1.45 percent to negative 10.94 percent | Multi-step extrapolation compounds the trend miss |
| Direction miss on growth years | 2 of 4 test years | Near-unit-root fit reverts toward mean growth |
| 2020 downturn predicted upward | 1 of 1 down years | A single negative year in 18 cannot teach contraction behavior |
| SARIMAX severe under-shoot of negative 22.8 percent by 2024 | 4 of 4 years | Exogenous regressors extrapolated worse than the target |
| Random Forest flat-lining at about 102 to 103 thousand every year | 3 of 4 years | Trees cannot extrapolate beyond the training range and predict the mean of seen leaves |

*Legend: SARIMAX seasonal ARIMA with exogenous inputs.*

*Table 3.44: Regression Error Taxonomy*

Table 3.44 shows the error taxonomy of the regression models. Every model failed in the same direction, which is under-prediction, and this places the dominant error source in the data regime rather than in the model specification. The plausible remedies are the addition of exogenous demand drivers such as electrification and economic growth, or retraining on shorter recent windows, rather than added model complexity.

**3.3.13.13 Robustness and Generalization**

| Measure | Result or Status |
| --- | --- |
| Perturbation runs | 30 |
| MAPE mean under perturbation | 5.707 percent |
| MAPE standard deviation | 0.155 percent |
| MAPE range | 5.279 to 6.068 percent |
| Held-out test window | One contiguous block inside the post-2020 acceleration regime |
| Temporal generalization | Partially supported by the cross-validation stability in section 3.3.13.8 |
| External validation | Not available; no second national series or held-out region exists in the dataset |

*Legend: MAPE mean absolute percentage error.*

*Table 3.45: Robustness and Generalization Results*

Table 3.45 shows that the model is stable under input noise without chaotic sensitivity. A different test window would produce different numbers, and genuine external validity is unestablished and is stated as a limitation rather than claimed.

**3.3.13.14 Statistical Validation**

| Item | Result | Caveat |
| --- | --- | --- |
| Diebold-Mariano style comparison of ARIMA against linear trend absolute-error losses | Statistic 3.532 with normal-approximation p-value of about 0.0004 | Four test points give essentially no power; the nominal p-value is descriptive only and not a real significance result |
| Other significance testing | None performed | No defensible test exists at this sample size |
| Model differences on the test set | Descriptive | Not statistically established |
| Confidence intervals | 95 percent prediction intervals of the model | Empirical coverage 75 percent on the test set, reported in section 3.3.13.7 |

*Legend: ARIMA autoregressive integrated moving average; DM Diebold-Mariano forecast comparison; p-value significance probability.*

*Table 3.46: Statistical Validation Results*

Table 3.46 shows the statistical validation results. This is a limitation of the data and can only be remedied by more granular monthly or quarterly observations.

**3.3.13.15 Comparison with Previous Studies**

A formal numeric comparison against published Philippine demand-forecasting studies was not executable because no external benchmark table exists within the dataset artifacts of the study, and constructing one from unverified sources was avoided. The internal reference point is the earlier evaluation of the project, whose stored comparison file had marked the SARIMAX and random forest rows as placeholders. The fresh execution replaced those placeholders with measured numbers and found both models to be substantially worse than the placeholders implied, which is itself a reportable finding on evaluation hygiene. In qualitative terms, a five to six percent MAPE on a four-year horizon annual series with 18 training points is within the error range typical of short-horizon extrapolative national forecasting, and the observed pattern where simple trend methods match or exceed a fitted ARIMA on a smooth and strongly trended aggregate is consistent with the established finding in time-series analysis that parsimonious models dominate at very small sample sizes. The contribution of the present evaluation is therefore methodological rather than a state-of-the-art claim, namely a fully re-executed and artifact-audited benchmark with interval and resampling evidence.

**3.3.13.16 Practical and Application Performance**

| Metric | ARIMA(1,1,1) | Random Forest |
| --- | --- | --- |
| Six-step forecast latency, mean | 0.97 ms | 9.93 ms |
| Serialized size in joblib format | 93.6 KB | 181.6 KB |
| Fit time | 0.086 s | 0.103 s |

*Legend: ms milliseconds; kB kilobytes; ARIMA autoregressive integrated moving average; joblib model-serialization format.*

*Table 3.47: Deployment Characteristics*

Table 3.47 shows that production inference is inexpensive. The serving path reads precomputed forecast artifacts instead of executing a model, and the forecast endpoint responds at a measured mean of 3.7 milliseconds. Deployment feasibility is high because the model is sub-millisecond, about 94 kilobytes in size, and requires no GPU. The operational risks are not in compute but in staleness, because the served forecasts do not update until the artifacts are regenerated, and in the premium-plan gating of the forecast routes. On practical usefulness, the forecasts are suitable as directional and trend guidance with interval context and should be presented to users with the intervals visible rather than as precise planning figures.

**3.3.13.17 Limitations of Machine Learning Evaluation**

The limitations of the machine learning evaluation are the following:

 1. The sample is small at 18 training and 4 test annual points, and each test point carries 25 percent of the reported error.
 2. Statistical power is thin because four test points render the Diebold-Mariano comparison descriptive only, and the model differences are not statistically established.
 3. There is a regime mismatch because the training window predates the post-2020 demand acceleration, which produces systematic under-forecasting in every model.
 4. There is no external validation because the dataset is a single national series for one country with one contiguous test block.
 5. Documentation drift was found and corrected because an earlier stored comparison file contained placeholder rows that were superseded by the re-executed run.
 6. The modeling is univariate and consumption is forecast from its own history, so policy and economic drivers are not inputs.
 7. One fixed (1,1,1) order is applied across targets despite demonstrably different series behavior, such as renewables at 13.7 percent against consumption at 5.7 percent.
 8. Interval coverage is below nominal at 75 percent against 95 percent under the acceleration regime.
 9. The served forecasts are static artifacts and freshness depends on pipeline re-runs rather than on the model itself.
10. Class imbalance and labeling limitations are not applicable in the classification sense because there are no classes and no human-assigned labels, and the targets are official measured statistics. The corresponding caveats are dependence on a single official source subject to revision, and dataset bias by construction because national annual aggregates mask provincial and seasonal variation and the model cannot represent sub-national heterogeneity.
11. Possible machine learning errors are acknowledged, namely the systematic under-forecast bias documented in section 3.3.13.12 and the dependence of the generative layer on provider availability and output quality, which is mitigated by the output-sanitizer checks, meaning the post-processing that strips raw model artifacts, and by the provider fallback and timeout paths verified in section 3.3.6.
12. Scope exclusions remain because the geothermal classifier was not evaluated in this cycle, and the EcoSim renewable-potential scoring is physics and decision-analysis based rather than a trained model, so no classification metrics exist for it either.

**3.3.13.18 Overall Machine Learning Findings**

Overall, the results show that the deployed ARIMA(1,1,1) forecaster is a reasonable choice for the system, although it is not demonstrably optimal on point accuracy. It placed fourth of six on the four-year test split at 5.667 percent MAPE against 4.965 percent for the linear trend, tied the best baselines in the seven-fold cross-validation at 3.607 percent, produced statistically adequate residuals with a Ljung-Box p-value of 0.9984, and is the only candidate that emits prediction intervals, which covered three of four test points. It is also inexpensive to serve at 0.97 milliseconds and about 94 kilobytes with artifact-based serving. Its errors are stable under perturbation at plus or minus 0.16 percentage points and are shared by every comparator, which indicates that the constraint lies in the dataset rather than in the model. The significant additional findings are that the test-set ranking is not stable under resampling, that the large overfit gap of the random forest rules out high-capacity learners at this sample size, and that per-target configuration such as the 3.868 percent of SARIMAX on peak demand is the clearest accuracy headroom.

The generative AI layer was evaluated on its own criteria of contract compliance, latency, and resilience and behaved as designed. All live calls produced correctly structured and sanitized output, the Gemini to Groq fallback answered in about 1.9 seconds, the hard-timeout path returned a graceful fallback, and the measured typical latency of about five to seven seconds with an 18.5 second tail defines the user-experience constraint that the progress indicators of the interface are intended to cover.

The supported verdict is that the forecasting component is suitable for use as a trend-extrapolation service as long as its intervals and limitations are surfaced to users, and it should not be presented as a precision planning instrument. The recommended improvements are listed in order of leverage in Table 3.48.

| Rank | Recommendation | Rationale |
| --- | --- | --- |
| 1 | Acquire monthly or quarterly Department of Energy (DOE) series | Multiplies the effective sample size, which is the largest source of leverage |
| 2 | Per-target order selection | The 3.868 percent of SARIMAX on peak demand shows per-target configuration gains |
| 3 | Exogenous demand drivers | Electrification and economic growth where regressors add value |
| 4 | Scheduled artifact regeneration | Prevents silent staleness of the served forecasts |
| 5 | Learned calibration of the physics-based suitability scores | Only if measured labels become available, since the scores are currently deterministic and were correctly excluded from this evaluation |

*Legend: SARIMAX seasonal ARIMA with exogenous inputs.*

*Table 3.48: Recommended Machine Learning Improvements in Order of Leverage*

---

*End of insert. Evidence sources: docs/LUMI_TECHNICALTESTING.md for the testing instrument, docs/LUMI — Technical Evaluation\_ Complete Test Results.md for the executed results, and docs/09-Technical-Evaluation/ML_Evaluation_Results_and_Discussion.md with docs/09-Technical-Evaluation/artifacts/rerun-2026-09-15/ for the machine learning artifacts. The promotional video at video/out/LumiPromo.mp4 reflects the same demonstrated flows but is not test evidence.*