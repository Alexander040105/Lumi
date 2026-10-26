# CHAPTER 3 — INSERT: System Test Plan and Results, and Machine Learning Evaluation

> **Before pasting, three housekeeping notes.**
>
> 1. The tables below are numbered Table 3.1 to Table 3.23 in the order they appear, and a legend line is placed beneath each table that uses coded identifiers or abbreviations, matching the legend convention of the other Chapter 3 tables. The existing Chapter 3 tables that begin in section 3.5 should be renumbered to follow after Table 3.23.
> 2. The results cited come from the testing conducted on the deployed system by the development team together with ten IT expert evaluators, the consolidated technical evaluation, and the machine learning evaluation re-execution.
> 3. Keep the "not applicable" sentences in the machine learning sections. They explain why classifier measures do not apply to a forecasting model, and removing them weakens the defense of the results.

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

The test plan covered three testing surfaces. The manual evaluation instrument contained 101 task-based cases grouped by module, namely public pages and navigation cases (FT-001 to FT-007, covering the home, about, terms, and privacy pages, navigation while logged out, theme and language toggles, and the not-found page), account cases (AC-001 to AC-009, covering sign-up validation, login, Google sign-in, password reset, multi-factor authentication, and logout), EcoSim cases (FT-010 to FT-016, covering the wizard, location pickers, simulation runs, AI analysis, saving, and PDF export), EnergyHub cases (FT-017 to FT-025, covering the overview, trends, forecast chart, choropleth map and level switching, breakdowns, provincial demand, AI insight, and chart explanations), saved-data and account cases (FT-026 to FT-033, covering saved simulations, dashboard, profile editing, password change, and the MFA setup page), admin console cases (AD-001 to AD-010, covering users, analytics, configuration, usage, logs, and the forecast panel), input-validation cases (IV-001 to IV-005, covering letters in bill fields, oversized and negative consumption entries, missing location, and injection strings), persistence and privacy cases (DP-001 to DP-006, covering data survival across sessions and per-user isolation), AI and connected-service cases (AI-001 to AI-006, covering AI narratives, waiting behavior, quota messaging, insight panels, map tiles, and Google sign-in), timed-observation cases (PT-001 to PT-009, covering page loads and key flows), on-screen security cases (SO-001 to SO-014, covering access walls, masking, HTTPS, error messages, and throttling), usability tasks (UAT-1 to UAT-5, the five timed user journeys), and regression checks (REG-01 to REG-06, re-verifying previously fixed defects). The automated technical evaluation added the unit, backend, frontend, and integration test suites of the project, a scripted sweep of every mounted API endpoint, latency and load benchmarks, failure-injection scenarios, and security probes. The machine learning evaluation benchmarked the deployed forecasting model against five alternatives on held-out data, together with cross-validation, residual diagnostics, robustness perturbation, and latency and size measurement.

The coded identifiers and abbreviations used throughout this section are defined in the legend line beneath each table where they appear.

Sections 3.3.1 to 3.3.12 present the scope, methodology, environment, test cases, and results of the system testing. Section 3.3.13 presents the machine learning evaluation results and discussion.

**3.3.1 Testing Scope**

The testing covered every screen, feature, and flow that could be reached through the application interface on the deployed site. This included the public pages consisting of Home, About, Terms, and Privacy; sign-up, login, logout, password reset, and multi-factor authentication; the EcoSim simulation wizard, results, AI analysis, save-simulation, and PDF export; the EnergyHub national dashboard with its overview, trends, forecast, choropleth map, source and grid breakdowns, provincial demand, and AI insight; saved simulations, profile, and security settings; the admin console covering users, analytics, configuration, usage, and logs; input handling including hostile and boundary inputs; on-screen security behavior; data persistence and privacy between users; responsiveness; compatibility across browsers and devices; API behavior under valid, invalid, boundary, and adversarial inputs; performance under single-user and stepped-concurrency load; failure and recovery behavior; and a moderated usability session. The machine learning scope covered the deployed ARIMA(1,1,1) forecaster, an autoregressive integrated moving-average time-series model, for national electricity consumption, peak demand, and renewable generation, together with five comparison models, and the Groq and Gemini generative AI recommendation layer evaluated on its output contract, latency, and resilience.

Some items were excluded from the testing cycle. Load testing on the production deployment was not performed and only a light production smoke check was done instead. Direct row-level security policy testing inside Supabase, meaning the database policies that scope each row to its owning user, was excluded because it requires an authenticated database session. Transport layer security (TLS) and certificate testing were excluded except for verifying that the production HTTP strict-transport-security (HSTS) header was present. Fuzzing, session-fixation, and cross-site request forgery (CSRF) testing beyond cross-origin resource sharing (CORS) preflight behavior were not covered. Reproduction of the forecasting pipeline at the notebook level was excluded and the endpoints were verified instead. NASA POWER fetch latency was not applicable at runtime because climate data is served from Supabase and bundled fallbacks. External validation of the forecast model against the data of a second country was not available. The geothermal suitability classifier present in the codebase was excluded from the machine learning evaluation scope.

**3.3.2 Testing Methodology**

The testing followed the lifecycle of requirements review to test planning, test case development, test execution, defect identification, correction, retesting, and final evaluation. Seven complementary testing types were applied as summarized in Table 3.1.

| Testing Type | Purpose | Instrument |
| ----- | ----- | ----- |
| Functional walkthrough | Follow each scripted scenario and compare expected and actual behavior | Functional test (FT) cases and automated suites |
| Exploratory and negative-input testing | Type bad, unusual, or hostile-looking input into forms and endpoints | Input-validation cases IV-001 to IV-005 and sweep adversarial inputs |
| Permission checks | Exercise the same pages as guest, registered user, and admin | On-screen security cases SO-001 to SO-014 and admin console cases AD-001 to AD-010 |
| Persistence checks | Save data, log out, log back in, and verify ownership isolation | Persistence and privacy cases DP-001 to DP-006 |
| Timed observation and benchmarks | Measure responsiveness directly with thirty repetitions per endpoint | Timed-observation cases PT-001 to PT-009 and latency benchmark |
| Load testing | Stepped virtual users from 1 to 100 at sixty seconds per level | Locust 2.46.4 headless, local target only |
| Failure and security probing | Inject dependency outages, malformed tokens, oversized bodies, and spoofed headers | Seventeen-scenario failure matrix (TC-FR cases) and probes |

*Legend: AD admin console case; IV input-validation case; DP persistence and privacy case; PT timed-observation case; SO on-screen security case; TC-FR failure-recovery scenario.*

*Table 3.1: Testing Types Applied in the LUMI System Test Plan*

Table 3.1 shows the testing types that were applied during the evaluation. Each type targets a different kind of defect, from wrong screen behavior to weak input handling and performance degradation under load. Defect handling was made explicit in the plan. Every defect found during the first execution pass was logged with an identifier, corrected, and executed again in the final pass. The regression block (REG-01 to REG-06) also re-ran previously fixed behaviors by hand to confirm that the corrections remained effective. The methodology for the machine learning evaluation is described in section 3.3.13 and includes the train and test split protocol, expanding-window cross-validation, residual diagnostics, robustness perturbation, and statistical comparison.

**3.3.3 Hardware and Software Test Environment**

| Item | Configuration |
| ----- | ----- |
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

*Table 3.2: Hardware and Software Test Environment*

Table 3.2 summarizes the environment where all automated and instrumented tests were executed. Load testing was pointed at the local backend only so that the production infrastructure and the paid language model providers did not receive any generated traffic. The machine learning artifacts were produced in the same Python environment.

**3.3.4 Functional Test Cases**

Functional verification combined the pre-existing automated suites of the project, a scripted live sweep of every mounted API route, and the 101-case manual instrument. The automated execution results are presented in Table 3.3.

| Suite | Result | Status |
| ----- | ----- | ----- |
| Unit tests (lumi_tests/tests/unit/) | 177 passed | PASS |
| Backend tests (fastapi-backend/tests/) | 106 passed | PASS |
| Frontend Vitest (react-frontend) | 9 passed (3 test files) | PASS |
| Integration tests (live-server cases deselected) | 23 passed, 2 skipped | PASS |
| Live endpoint sweep | 82 of 82 checks passed | PASS |

*Table 3.3: Automated Functional Test Results*

Table 3.3 presents the results of the automated functional tests. All suites passed, and the live endpoint sweep passed all 82 of its checks. The tracked functional test case ledger, which is the monitored list of functional test cases maintained by the evaluation, covered 69 cases across the system modules. On the final pass, after defect correction and retesting, 58 passed, 0 failed, and 11 were pending or not applicable. The pending items were the two responsive-viewport visual checks that were deferred until a live browser pass could be run, and nine machine learning notebook re-run items whose endpoints were verified at the API level instead. Table 3.4 shows the distribution of the cases by module.

| Module | Total | Passed | Failed | Pending or not applicable |
| ----- | ----- | ----- | ----- | ----- |
| Authentication | 6 | 6 | 0 | 0 |
| EnergyHub | 10 | 10 | 0 | 0 |
| EcoSim | 13 | 13 | 0 | 0 |
| AI Intelligence | 7 | 7 | 0 | 0 |
| API Endpoints | 13 | 13 | 0 | 0 |
| Visualization | 9 | 7 | 0 | 2 |
| Machine Learning | 11 | 2 | 0 | 9 |
| **Total** | **69** | **58** | **0** | **11** |

*Table 3.4: Functional Test-Case Summary by Module*

Table 3.4 shows that all modules completed their cases without failures on the final pass. Representative verified behaviors included the completion of Google OAuth (third-party sign-in) registration with JSON Web Token (JWT) issuance, the return of HTTP 401 for requests without a token or with malformed or expired tokens, the serving of 1,813 municipalities by the EcoSim municipality endpoint, and the return of clean 422 or 404 responses for missing or invalid municipality identifiers.

Six defects were found during the first execution pass. All were corrected and retested to closure as listed in Table 3.5.

| Defect ID | Description | Severity | Status |
| ----- | ----- | ----- | ----- |
| DEF-01 | Geothermal lookup of an invalid identifier returned 500 instead of 404 | Low | Fixed and retested |
| DEF-02 | Map with an invalid type returned 200 with an error body instead of a 4xx client-error status | Low | Fixed and retested |
| DEF-03 | Invalid forecast metric was silently accepted and is now validated with 422 | Low | Fixed and retested |
| DEF-04 | The forecast run endpoint accepted injection-style strings silently and now validates them | Low | Fixed and retested |
| DEF-05 | The product recommendation endpoint echoed an unvalidated parameter and an allowlist was added | Low | Fixed and retested |
| DEF-06 | The AI-quota error message referenced the wrong product name and the copy was corrected | Trivial | Fixed and retested |

*Legend: DEF defect identifier; 200 request succeeded; 404 not found; 422 validation failed; 500 server error; 4xx client-side rejection.*

*Table 3.5: Defect Log of Items Found, Corrected, and Retested*

Table 3.5 lists the defects that were found and corrected during testing. All six were of low or trivial severity, and no critical or high-severity functional defect was recorded during the testing window.

**3.3.5 Database Testing**

Database testing covered persistence, privacy isolation, query performance, and the access control posture of the data tier. The persistence and privacy cases of the instrument (DP-001 to DP-006) verified that a saved simulation survives logout and re-login, that profile edits persist across sessions, that the saved simulations and profile of one user are not visible to another account, that the session survives a page refresh, and that logout followed by the browser back button returns the user to the login page instead of the protected content.

Direct query timings were also measured through the same Supabase REST path that the application uses, with ten repetitions per query. The results are presented in Table 3.6.

| Query | Mean | p50 | p95 | Notes |
| ----- | ----- | ----- | ----- | ----- |
| regions select-1 | 160.8 ms | 70.6 ms | 962.9 ms | The p95 value is a cold-connection outlier and steady state is about 70 ms |
| municipalities select-10 | 100.7 ms | 74.0 ms | 317.9 ms | First-call warmup is visible |
| climate_monthly filtered | 78.1 ms | 76.1 ms | 88.0 ms | Indexed lookup with a tight distribution |

*Legend: p50 median; p95 95th percentile; ms milliseconds.*

*Table 3.6: Direct Supabase Query Timings with Ten Repetitions*

Table 3.6 shows the measured database query timings. The dominant cost is the network and TLS transit to the managed PostgreSQL endpoint, which sets a floor of around 70 milliseconds. Query execution itself is below one millisecond for these indexed single-table selects. For access control, the backend uses the Supabase service-role key for server-side reads, which is the correct pattern for a trusted backend, while client access passes through the FastAPI authentication dependencies. The publishable key exposed to the browser is safe by design as long as row-level security remains enabled on user-facing tables. Direct policy testing with an authenticated database session was recorded as an open item outside the scope of this cycle.

**3.3.6 API / External Service Testing**

The live endpoint sweep exercised every mounted API route with valid, invalid, boundary, and adversarial inputs and passed 82 of 82 checks. This included five SQL injection style probe families that were rejected at the FastAPI validation boundary with HTTP 422 and were never echoed in the response bodies. CORS also behaved according to the allowlist. Preflight requests from an allowed origin received the correct header while a disallowed origin was blocked, both in the local environment and in production.

External service behavior was verified through a seventeen-scenario failure injection matrix, of which fifteen scenarios degraded gracefully. Selected scenarios and their outcomes are summarized in Table 3.7.

| Injected Failure | Observed Behavior | Verdict |
| ----- | ----- | ----- |
| Gemini outage on all models | Automatic fallback to live Groq and a response produced in 1,683 ms | Graceful |
| AI worker exceeds the hard timeout | Structured timeout fallback returned in 61 ms | Graceful |
| All LLM providers down | Fallback analysis payload and the endpoint stays functional | Graceful |
| Supabase client broken | Detailed health reports degraded but stays HTTP 200 and municipalities are still served from bundled CSV fallback with 1,813 items | Graceful |
| Redis unavailable | Health check reports not configured and map endpoints still serve 200 through the cache-miss path | Graceful |
| ML worker URL dead | 503 on the proxied path only and the rest of the API stays healthy | Graceful |
| Invalid municipality identifier | Clean 404 messages on EcoSim while the geothermal path initially returned 500 and was mapped to 404 as DEF-01 | Fixed |
| Body above 1 MB or malformed JSON or non-integer parameter | 413 or 422 or 422 respectively | Graceful |
| Rate-limit burst on healthy Redis or the clean NullRedis in-memory fallback | Exactly 60 allowed then 429 so the limiter is enforced | Graceful |

*Legend: DEF defect identifier; 200 request succeeded; 404 not found; 413 body too large; 422 validation failed; 429 rate limited; 500 server error; 503 dependency unavailable; ms milliseconds; MB megabytes; NullRedis in-memory fallback; LLM large language model; Redis rate-limit cache store.*

*Table 3.7: External-Service and Failure-Recovery Behavior for Selected Scenarios*

Table 3.7 summarizes how the system behaved when its dependencies were made to fail. Of the remaining outcomes, one degraded-status case involving the geothermal lookup returning 500 instead of 404 was corrected and retested as defect DEF-01. Two security-relevant rate-limiting behaviors were also recorded, namely split counters under an intermittent Redis connection and an X-Forwarded-For client-address header trust assumption, and these are summarized under the limitations in section 3.3.8. NASA POWER is not a runtime dependency because climate data is served from Supabase with bundled fallbacks, so its outage path was verified as not applicable.

**3.3.7 Performance Testing**

Single-user warm-cache latency was benchmarked with thirty repetitions per endpoint and five for the language model backed paths. The measured results are shown in Table 3.8.

| Endpoint | n | Mean (ms) | p50 | p95 | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
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

*Table 3.8: API Endpoint Latency for a Single User with Warm Cache in Milliseconds*

Table 3.8 shows the measured endpoint latencies. The p95 value of the AI insight endpoint reflects one full language model round-trip of about 3.2 seconds, and the anonymous quota responses of the same endpoint were already consumed during the run, so the p95 column mixes a real model call with quota responses. Standard endpoints averaged around 49 milliseconds while the mean across all measured endpoints was around 104 milliseconds, which is consistent with the figure reported in section 3.9. The heavier user-facing EcoSim and AI flow measured about 612 milliseconds end-to-end in the user evaluation, which is well inside the interactive response budget.

Stepped-concurrency load was also executed against the local backend using Locust with real municipality identifiers and a mixed workload weighted toward the heavier endpoints. The results are presented in Table 3.9.

| Concurrent Users | Requests | Failures | Avg (ms) | p95 | Throughput |
| ----- | ----- | ----- | ----- | ----- | ----- |
| 1 | 96 | 0 | 90 | 600 | 3.3 RPS |
| 10 | 790 | 0 | 519 | about 1,400 | 13.3 RPS |
| 25 | 769 | 0 | 1,637 | about 3,300 | 13.0 RPS |
| 50 | 614 | 0 | 3,838 | about 7,000 | 10.5 RPS |
| 75 | 657 | 0 | 5,582 | about 8,700 | 11.0 RPS |
| 100 | 814 | 0 | 5,591 | about 8,900 | 13.7 RPS |

*Legend: p95 95th percentile; RPS requests per second; ms milliseconds.*

*Table 3.9: Stepped-Concurrency Load Results at Sixty Seconds per Level*

Table 3.9 shows the results of the stepped-concurrency load test. Every request at every level succeeded with zero server errors, timeouts, or connection resets, which means the system degrades gracefully under load because latency inflates while requests queue rather than fail. Throughput plateaus at around 11 to 14 requests per second on a single worker, which places the interactive ceiling at around 10 to 15 concurrent users and the three-second p95 threshold near 25 users. Horizontal scaling is the documented path beyond that point. The rate limiter also returned HTTP 429 correctly under a sustained same-source burst.

Other performance findings were also recorded. The initial production build shipped a single JavaScript chunk of about 1.91 megabytes gzip-compressed, and route-based code-splitting was applied afterwards, which reduced the entry bundle to around 611 kilobytes with lazy-loaded route and vendor chunks. The production smoke checks observed serverless cold-start latencies of around 0.8 to 3.8 seconds. Supabase cold connections produced occasional spikes of around 963 milliseconds that settled to around 70 milliseconds in steady state.

**3.3.8 Security Testing**

Security testing combined static analysis of the backend through Bandit, dependency audits through pip-audit and npm audit, a live probe suite of eighteen executed probes of which sixteen passed with one warning and informational notes, a JSON Web Token (JWT) validation matrix, cross-origin resource sharing (CORS) preflight verification, SQL injection style inputs, error-body inspection, and a secrets-handling review. All probes were read-only or self-cancelling. The verified controls are summarized in Table 3.10.

| Verified Control | Result |
| ----- | ----- |
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

*Table 3.10: Verified Security Controls*

Table 3.10 lists the security controls that were verified during testing. The frontend dependency audit also reported seven advisories, of which one critical and one high were confined to development-only dependencies and five were moderate, including router advisories that ship to runtime and have available non-major fixes. Targeted probing further identified a bounded set of hardening items, mainly an X-Forwarded-For proxy-header trust assumption that affects rate-limit attribution, fail-open behavior in two dependency-check paths during dependency outage, and known backend dependency advisories, and these items are recorded in the findings register of the evaluation with severities and recommended fixes. These items affect enforcement robustness under adverse conditions, while the authentication, authorization, injection, CORS, header, and error-sanitization controls in Table 3.10 were all verified as working under live testing. Testing that remained deferred includes authenticated row-level security policy testing, TLS testing beyond production HSTS verification, and fuzzing and CSRF coverage.

**3.3.9 Compatibility Testing**

Compatibility coverage was defined in the instrument across two matrices, namely four target browsers consisting of Google Chrome, Microsoft Edge, Mozilla Firefox, and Safari, and four device classes consisting of desktop, laptop, tablet, and smartphone. The execution status is reported as follows. LUMI is a React 18 and Vite single-page application delivered as a standards-compliant production build that targets evergreen, meaning continuously updated, browsers, and HTTPS and security headers were verified on the production deployment. Tailwind responsive utility classes are applied throughout the interface, and the production smoke pass confirmed identical API behavior through the deployed edge path, meaning the Vercel hosting layer closest to the user. The two scripted responsive-viewport checks at 375 and 768 pixel widths were deferred pending a live browser pass, and this is the one outstanding functional item in the ledger. The full per-browser version matrix was exercised through the machines of the evaluators rather than a controlled browser-farm run. Even so, real-device and real-browser exposure was substantial because the 100-respondent household evaluation and the ten IT expert evaluators used the deployed system on their own equipment, and no compatibility defect was reported in the defect log. No cross-browser rendering or device-blocking defect was recorded during the testing window, and the formal per-browser matrix remains listed as the compatibility evidence to be completed before production rollout.

**3.3.10 Usability and User Interface Testing**

Usability testing proceeded on two tracks. The scripted user-acceptance tasks (UAT-1 to UAT-5) exercised the five core user journeys with explicit success standards, namely locating the latest national consumption figure in EnergyHub within about 60 seconds, completing an EcoSim simulation for Tagaytay City, Cavite with a 2,500 peso monthly bill within about three minutes, identifying the predicted 2030 consumption from the forecast chart within about 90 seconds, identifying the province with the highest solar potential from the map within about two minutes, and locating and restating the AI generated explanation after a simulation.

User interface behavior was also verified at the component level. The nine-file Vitest suite covers chart, map, KPI-card, and AI-panel rendering, the theme and language toggles were exercised, empty-location and invalid-input states produce clear guidance instead of errors, the not-found route renders a friendly page, and password fields mask input. The participant-scale usability results, which are the primary evidence for usability, are reported in sections 3.8 and 3.9.2 to 3.9.5 and are cross-referenced here. For completeness, the 100-respondent household evaluation obtained an overall usability weighted mean of 4.73 with a standard deviation of 0.38 interpreted as Excellent, and a comparison-with-prior-methods weighted mean of 4.79 with a standard deviation of 0.32 also interpreted as Excellent. The instruments were reliable with Cronbach's alpha of 0.923 and 0.868 respectively, and a one-sample right-tailed t-test produced a t statistic of 55.47 at 99 degrees of freedom with a p-value below 0.001 against the neutral midpoint.

**3.3.11 ISO/IEC 25010 Software Quality Evaluation**

Software quality was evaluated against eight selected ISO/IEC 25010:2023 characteristics, namely functional suitability, performance efficiency, compatibility, reliability, security, maintainability, flexibility, and safety, using a five-point scale interpreted on the evaluation criteria defined in section 3.5. It should be noted that flexibility and safety are drawn from the quality-in-use model of the standard and were included to cover deployment adaptability and risk-mitigation concerns relevant to a decision-support system.

Two complementary evaluations were performed. The independent IT expert evaluation of ten experts scored all eight characteristics and is reported with per-statement detail in section 3.9.6 onwards. The overall weighted mean was 4.46 with a standard deviation of 0.60 and was interpreted as Excellent, led by compatibility at 4.65, maintainability at 4.60, and safety at 4.50, while flexibility was the lowest at 4.20 which was interpreted as Very Good. This result supports the engineering finding that horizontal scalability is the main growth area of the system. The internal technical self-evaluation performed by the development team during the automated testing cycle applied a stricter rubric and produced a weighted score of 3.60 out of 5.0 interpreted as Good, with functional suitability, performance, reliability, and security at 4 and compatibility, usability, maintainability, and portability at 3. This reflects the deductions already evidenced in this chapter, namely the single-worker concurrency ceiling, the deferred responsive-viewport checks, and the dependency and hardening items noted in section 3.3.8. The gap between the internal and external scores is also informative because the independently assessed quality of the system is higher than the conservative technical assessment of the team.

**3.3.12 Testing Results Summary**

| Category | Instrument or Method | Result |
| ----- | ----- | ----- |
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

*Table 3.11: Consolidated Testing Results Summary*

Table 3.11 shows that the overall verdict of the testing cycle is passed and ready for deployment within the stated constraints. No critical or high-severity functional defect remained open after retesting, and the system degraded gracefully under every survivable failure that was injected. The residual items, namely a formal per-browser matrix, direct row-level security policy verification, production-scale load evidence, and the logged security-hardening items, are documented as the boundary of the current evaluation rather than as failures of it.

**3.3.13 Machine Learning Evaluation Results and Discussion**

Three components were evaluated separately so that they are not confused with one another. The first is the deployed ARIMA(1,1,1) time-series forecaster for national electricity consumption, peak demand, and renewable generation, which was benchmarked against five alternatives. The second is the Groq and Gemini generative AI recommendation layer, which was evaluated on output contract, latency, and resilience criteria as a generative component and not as a predictive model. The third is a scope note, which is that the solar, wind, and hydro potential of EcoSim is computed by physics-based estimators and multi-criteria decision analysis and not by a trained model, and that a geothermal-suitability random forest classifier exists in the codebase but was excluded from the scope of this evaluation. Because the forecasting component predicts continuous quantities, the classifier-specific items in the following subsections are marked as not applicable and the correct time-series substitute is reported in their place.

**3.3.13.1 Dataset Description and Distribution**

The modeling dataset is the Philippine Department of Energy national energy statistics that was preprocessed into a single modeling table. The profile of the dataset is summarized in Table 3.12.

| Property | Value |
| ----- | ----- |
| Rows | 23, one record per year |
| Columns | 45 |
| Coverage | 2003 to 2025, annual |
| Duplicate rows | 0 |
| Missing cells | 15, all inside derived lag, growth, and rolling columns where the earliest years have no prior-year source |
| Primary target | total_consumption_gwh, from 52,941 to 126,941 gigawatt-hours (GWh) |
| Secondary targets | total_peak_demand_mw and renewable_generation_gwh |
| Consumption compound annual growth rate (CAGR), 2003 to 2024 | 4.252 percent, with a mean absolute yearly change of 4.49 percent, a maximum of 10.17 percent, and a minimum of negative 4.04 percent |

*Legend: GWh gigawatt-hours; CAGR compound annual growth rate.*

*Table 3.12: Forecasting Dataset Profile*

Table 3.12 shows the profile of the forecasting dataset. The evaluation protocol split the data by time, with training on 2003 to 2020 for 18 samples or 81.8 percent and a held-out test set on 2021 to 2024 for 4 samples or 18.2 percent. The 2025 row was retained in the file but set aside from the historical test metrics. Classes and categories, per-class distribution, and class balance are not applicable to this evaluation because the target is a continuous quantity. The corresponding concern for a continuous target is the sample size itself, which is 18 training points and a four-point test window where each observation carries 25 percent of the reported error. The small sample is the dominant constraint of this evaluation because it rules out data-hungry learners and requires validation methods that are appropriate for time-series data instead of a large random holdout.

**3.3.13.2 Data Preprocessing Results**

| Step | Applied | Rationale or Evidence |
| ----- | ----- | ----- |
| Temporal alignment to annual records | Yes | 23 rows, one per year, no gaps or duplicates |
| Missing-value handling | Structural | The 15 empty cells exist only where lag and rolling windows reach before 2003 and affected rows are excluded where needed |
| Feature engineering | Yes | Lag-1 and lag-2, first difference, year-on-year growth, three and five-year rolling means, capacity margin, renewable share, and years-since-2003 give the comparison models autoregressive memory |
| Differencing for stationarity | Inside ARIMA | The d equals 1 term performs first-order differencing on the trended series |
| Categorical encoding | Not applicable | No categorical predictors exist |
| Feature scaling | Deliberately skipped | The evaluated models are scale-invariant or tree-based and scaling would add a step with no effect |
| Augmentation | Not used | Fabricating national statistics would corrupt the evaluation |

*Legend: ARIMA autoregressive integrated moving average.*

*Table 3.13: Data Preprocessing Steps and Justifications*

Table 3.13 shows that preprocessing was intentionally minimal because the data are already clean national aggregates. The substantive work was the construction of autoregressive features for the comparison models and the internal differencing that ARIMA applies. Scaling was not applied because the evaluated models are scale-invariant or tree-based, and adding the step would not change their behavior.

**3.3.13.3 Machine Learning Model Configuration**

Six models were configured and executed on the same data by the evaluation pipeline as listed in Table 3.14.

| Model | Type | Configuration |
| ----- | ----- | ----- |
| **ARIMA(1,1,1) production model** | Statistical time-series | Order (1,1,1), optimal in the searched AIC and BIC grid as shown in section 3.3.13.10, fitted with statsmodels ARIMA, with native 95 percent prediction intervals |
| Linear Trend Regression | Baseline | Ordinary least squares of consumption on years_since_2003 |
| Naive with Drift | Baseline | Random-walk-with-drift extrapolation |
| Holt Linear Smoothing | Statistical | Exponential smoothing with additive trend |
| SARIMAX(1,1,1) with exogenous input | Statistical with exogenous (external-driver) regressors | ARIMA errors with exogenous regressor columns |
| Random Forest Regression | ML baseline | RandomForestRegressor on engineered lag and rolling features |

*Legend: AIC Akaike information criterion; BIC Bayesian information criterion; SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.14: Evaluated Model Configurations*

Table 3.14 lists the evaluated model configurations. None of the models use iterative training loops and each fits in a single mathematical step, so training epochs and loss values are not applicable. The input features of the statistical models are the history of the target series itself, while the random forest baseline additionally uses the engineered lag and rolling features described in section 3.3.13.2. The production serving path does not retrain per request. The deployed predictor loads precomputed forecast artifacts containing point forecasts with confidence intervals that are registered in the model registry, so training cost is an offline concern and not a request-time latency concern. The hardware and software environment is given in Table 3.2.

**3.3.13.4 Model Training Results**

Training accuracy, training loss, validation accuracy, validation loss, and the number of epochs are not applicable to these models because they are not trained by gradient descent. The correct substitutes, which are fit time and residual diagnostics, are reported instead. The measured fit times are presented in Table 3.15.

| Model | Fit time (s) |
| ----- | ----- |
| Linear Trend Regression | 0.0374 |
| Naive with Drift | 0.00005 |
| Holt Linear Smoothing | 0.0160 |
| ARIMA(1,1,1) | 0.0859 |
| SARIMAX(1,1,1) with exogenous input | 0.0704 |
| Random Forest Regression | 0.1026 |

*Legend: SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.15: Measured Model Fit Times*

Table 3.15 presents the measured fit times of the six models. The fitted parameters of the ARIMA(1,1,1) model were the autoregressive coefficient ar.L1 of about 0.9999, the moving-average coefficient ma.L1 of about negative 0.9972, and the residual variance sigma squared of about 1.032 times ten to the seventh. The Akaike information criterion (AIC) was 325.63 and the Bayesian information criterion (BIC) was 328.13. The Ljung-Box test for leftover autocorrelation in the residuals at lag five returned a statistic of 0.258 with a p-value of 0.9984, which shows no evidence of residual autocorrelation and indicates an adequate in-sample fit. On the question of overfitting, the near-unit autoregressive coefficient paired with a near-cancelling moving-average coefficient is the usual signature of a process that is barely distinguishable from a random walk with drift. This diagnostic foreshadowed the test-set result where the simpler trend and drift baselines matched or slightly exceeded the ARIMA model. The random forest baseline showed the opposite pattern and fitted the training window at 1.45 percent mean absolute percentage error while performing at only 10.94 percent on the held-out data. This gap of about 9.5 points supports the use of parsimonious statistical models at this sample size.

**3.3.13.5 Model Testing Results**

Test accuracy, precision, recall, F1-score, specificity, and the area under the receiver-operating-characteristic curve (ROC-AUC) are not applicable to this evaluation because these metrics evaluate classifiers while the model predicts amounts. The correct regression metrics are the mean absolute error (MAE), root mean squared error (RMSE), mean absolute percentage error (MAPE), and the coefficient of determination (R-squared), together with direction-of-change accuracy as a classification-style substitute. The held-out test results for national consumption from 2021 to 2024 are presented in Table 3.16.

| Model | MAE (GWh) | RMSE (GWh) | MAPE (percent) | R-squared |
| ----- | ----- | ----- | ----- | ----- |
| **Linear Trend Regression** | **5,993.83** | **7,342.10** | **4.965** | **0.1054** |
| Holt Linear Smoothing | 6,557.72 | 7,997.68 | 5.435 | negative 0.0615 |
| Naive with Drift | 6,709.32 | 8,128.45 | 5.566 | negative 0.0965 |
| ARIMA(1,1,1) production model | 6,829.09 | 8,257.12 | 5.667 | negative 0.1315 |
| Random Forest Regression | 13,118.37 | 15,349.45 | 10.937 | negative 2.9099 |
| SARIMAX(1,1,1) with exogenous input | 16,721.10 | 18,787.73 | 14.031 | negative 4.8577 |

*Legend: GWh gigawatt-hours; MAE mean absolute error; RMSE root mean squared error; MAPE mean absolute percentage error; R-squared coefficient of determination; SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.16: Held-Out Test Results for Total Consumption from 2021 to 2024*

Table 3.16 presents the held-out test results for national consumption. The per-year errors of the production model were negative 1.45 percent in 2021, negative 3.69 percent in 2022, negative 6.59 percent in 2023, and negative 10.94 percent in 2024. The secondary targets under the same protocol showed that peak demand was best served by SARIMAX with exogenous regressors at 3.868 percent MAPE with an R-squared of 0.4124 against 5.611 percent for ARIMA with a mean absolute error of about 1,019.66 megawatts, and renewable generation was best served by the linear trend and Holt models at 9.405 percent against 13.665 percent for ARIMA with a mean absolute error of about 3,597.39 gigawatt-hours. Directional accuracy, which is the classification-style substitute, was 8 of 11 fold and test years or 72.7 percent for ARIMA, against 42.9 to 50.0 percent for the linear trend comparators.

The results indicate that ARIMA finished fourth of six on the consumption test at 5.667 percent MAPE, and in absolute terms the top four models all err by around five to six percent of annual national consumption, which is acceptable for a four-year horizon forecast on annual data. Every model under-forecast every test year and the error grew monotonically with the horizon because the test years coincided with the post-2020 acceleration in demand that purely extrapolative models trained on 2003 to 2020 systematically underestimate. The conclusion supported by these results is that point accuracy on 2021 to 2024 is modest. The direction of growth is captured but the magnitude of the acceleration is not, and this is a limitation of the data regime that is shared by every comparator and not a defect of one model.

**3.3.13.6 Confusion Matrix Analysis**

A conventional confusion matrix is not applicable to this evaluation because there are no classes to be confused. The valid substitute is a directional two-by-two matrix on the unique evaluation years from 2015 to 2024 covering the cross-validation folds and the test set, which is presented in Table 3.17.

| Actual Direction and Predicted Direction | Up | Down |
| ----- | ----- | ----- |
| **Up** | 7 | 2 |
| **Down** | 1 | 0 |

*Table 3.17: Directional Matrix of the Forecast Direction of Change*

Table 3.17 presents the directional matrix of the forecast direction of change. The model called the correct direction in 8 of 10 unique years or 80 percent. The informative cells are the two years 2023 and 2024 where the model predicted a decrease while actual demand accelerated upward, and the single year 2020 where the only down year in the dataset, the negative 4.04 percent pandemic-year contraction, was predicted upward. Both error classes share one cause, which is that regime changes with no precedent in the 18 training years cannot be anticipated by an extrapolative model.

**3.3.13.7 Class-Level Performance**

Per-class precision, recall, F1-score, and support are not applicable to this evaluation. The structurally equivalent breakdown is performance per target under one fixed specification, which is shown in Table 3.18.

| Target | ARIMA MAPE | Best model | Best MAPE | Reading |
| ----- | ----- | ----- | ----- | ----- |
| total_consumption_gwh | 5.667 percent | Linear Trend | 4.965 percent | Smooth series and the fixed order is adequate |
| total_peak_demand_mw | 5.611 percent | SARIMAX with exogenous input | 3.868 percent | Exogenous regressors add value here |
| renewable_generation_gwh | 13.665 percent | Linear Trend and Holt | 9.405 percent | Volatile and break-prone so it is the hardest target |

*Legend: MAPE mean absolute percentage error; SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.18: Per-Target Performance as the Regression Equivalent of Per-Class Scores*

Table 3.18 shows the per-target performance of the same ARIMA specification. A single fixed order is a reasonable default for the smooth consumption and demand aggregates but a poor choice for the renewable series, and per-target order selection is a concrete improvement path. The regression analogue of a confidence-quality score is the 95 percent prediction-interval coverage, which was 3 of 4 held-out points or 75 percent, with the acceleration year 2024 falling outside the band. This indicates that the intervals are slightly overconfident under regime acceleration, which is the same condition that degrades the point forecasts.

**3.3.13.8 Cross-Validation Results**

Random k-fold validation is not valid for time-series data because it leaks future information, so expanding-window time-series cross-validation over seven folds was used instead. The results are shown in Table 3.19.

| Model | Folds | Mean APE (percent) | Std dev |
| ----- | ----- | ----- | ----- |
| Holt | 7 | 3.525 | 3.496 |
| Naive with Drift | 7 | 3.584 | 2.535 |
| **ARIMA(1,1,1)** | 7 | **3.607** | **2.512** |
| Linear Trend | 7 | 5.861 | 3.917 |

*Legend: APE absolute percentage error; ARIMA autoregressive integrated moving average.*

*Table 3.19: Expanding-Window Cross-Validation Using Absolute Percentage Error*

Table 3.19 shows the expanding-window cross-validation results. Across the folds the top three methods are statistically indistinguishable because their means are within 0.09 percentage points of each other, while the linear trend model that won the single split is clearly the weakest under resampling. This means the single four-year leaderboard is not stable evidence, and the cross-validated showing of ARIMA, which has a competitive mean and the tightest deviation together with the naive drift baseline, is the fairer justification for retaining it as long as the intervals remain calibrated.

**3.3.13.9 Model Comparison**

| Rank | Model | Test MAPE (percent) | Key differentiator |
| ----- | ----- | ----- | ----- |
| 1 | Linear Trend | 4.965 | Best on this split but weakest in cross-validation |
| 2 | Holt | 5.435 | Best cross-validation mean and consistent |
| 3 | Naive with Drift | 5.566 | Near-zero cost and hard to beat |
| 4 | **ARIMA(1,1,1)** | **5.667** | The only model emitting calibrated intervals with top-tier cross-validation |
| 5 | Random Forest | 10.937 | 18 training rows are far below its data appetite |
| 6 | SARIMAX with exogenous input | 14.031 | Exogenous regressors extrapolated poorly |

*Legend: MAPE mean absolute percentage error; SARIMAX seasonal ARIMA with exogenous inputs; ARIMA autoregressive integrated moving average; exogenous external-driver input.*

*Table 3.20: Consolidated Model Comparison for the Consumption Target*

Table 3.20 shows the consolidated ranking of the six models. Accuracy, precision, recall, F1-score, and ROC-AUC comparisons are not applicable and the comparison uses regression error metrics instead. The production model does not dominate on point accuracy, and no reading of these tables supports such a claim. Its case rests on three properties that the baselines lack, namely a likelihood-based fit with diagnostic testing as reported in section 3.3.13.4, native prediction intervals that are surfaced to users through the confidence fields of the API, and cross-validation performance equal to the best baselines. The failure of SARIMAX on consumption together with its win on peak demand shows that the value of exogenous regressors is target-dependent, and the negative 2.91 R-squared of the random forest confirms that tree ensembles are not appropriate at this sample size.

**3.3.13.10 Hyperparameter Evaluation**

The ARIMA order was selected through an AIC and BIC grid over p, d, and q values from zero to two with d fixed at one, because the trended series requires first-order differencing and annual data has no within-year seasonality to search over. The grid results are shown in Table 3.21.

| Order | AIC | BIC |
| ----- | ----- | ----- |
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

*Table 3.21: ARIMA Order Search Using the AIC and BIC Grid*

Table 3.21 shows that the (1,1,1) order is the information-criterion-optimal choice within the searched grid and is 1.8 AIC points ahead of the next candidate, which makes the selection evidence-based rather than an arbitrary default. The search is appropriate but narrow because d was fixed and per-target orders were not searched, and both are noted as improvement paths.

**3.3.13.11 Feature Importance and Model Explainability**

The ARIMA model is interpretable through its fitted parameters rather than feature importances. The ar.L1 value of about 1.00 means the level next year is about the level this year plus drift, and the ma.L1 value of about negative 1.00 means shocks are absorbed almost fully within one step, which together describe a smooth-trend process with fast shock decay. For the random forest baseline, the feature importances are dominated by the consumption lag and the rolling means, which is the same recent-level information that ARIMA uses and which the forest can only memorize at 18 observations. The SHAP and LIME explainability frameworks were not applied because at 18 observations with fewer than ten features they would add machinery without adding insight. The most influential predictor across all models is in effect the most recent consumption level and its drift.

**3.3.13.12 Error Analysis**

Misclassification patterns, false positives, and false negatives are not applicable to this evaluation. The regression error taxonomy is presented in Table 3.22 instead.

| Error pattern | Frequency | Likely cause |
| ----- | ----- | ----- |
| Under-forecast of magnitude across all models and test years | 24 of 24 model-years | Post-2020 demand acceleration absent from the 2003 to 2020 training window |
| Error growth with horizon | Monotone from negative 1.45 percent to negative 10.94 percent | Multi-step extrapolation compounds the trend miss |
| Direction miss on growth years | 2 of 4 test years | Near-unit-root fit reverts toward mean growth |
| 2020 downturn predicted upward | 1 of 1 down years | A single negative year in 18 cannot teach contraction behavior |
| SARIMAX severe under-shoot of negative 22.8 percent by 2024 | 4 of 4 years | Exogenous regressors extrapolated worse than the target |
| Random Forest flat-lining at about 102 to 103 thousand every year | 3 of 4 years | Trees cannot extrapolate beyond the training range and predict the mean of seen leaves |

*Legend: SARIMAX seasonal ARIMA with exogenous inputs.*

*Table 3.22: Regression Error Taxonomy*

Table 3.22 shows the error taxonomy of the regression models. Every model failed in the same direction, which is under-prediction, and this places the dominant error source in the data regime rather than in the model specification. The plausible remedies are the addition of exogenous demand drivers such as electrification and economic growth, or retraining on shorter recent windows, rather than added model complexity.

**3.3.13.13 Robustness and Generalization**

Perturbation robustness was measured with 30 runs using small input perturbations and produced a MAPE mean of 5.707 percent, a standard deviation of 0.155 percent, and a range of 5.279 to 6.068 percent, which shows that the model is stable under input noise without chaotic sensitivity. On generalization, the held-out window from 2021 to 2024 is one contiguous block inside an acceleration regime, and a different test window would produce different numbers. Temporal generalization is partially supported by the cross-validation stability reported in section 3.3.13.8. External validation is not available because no second national series or held-out region exists in the dataset, and genuine external validity is unestablished and is stated as a limitation rather than claimed.

**3.3.13.14 Statistical Validation**

A Diebold-Mariano style comparison of the ARIMA and linear trend absolute-error losses on the test set returned a statistic of 3.532 with a normal-approximation p-value of about 0.0004 at four test points. This is reported with the caveat that at four test points the test has essentially no power and the nominal p-value must not be read as a real significance result. No other significance test was performed because no defensible test exists at this sample size. The supported statement is that the model differences on this test set are descriptive and not statistically established. Confidence intervals take the form of the 95 percent prediction intervals of the model, whose 75 percent empirical coverage on the test set is reported in section 3.3.13.7. This is a limitation of the data and can only be remedied by more granular monthly or quarterly observations.

**3.3.13.15 Comparison with Previous Studies**

A formal numeric comparison against published Philippine demand-forecasting studies was not executable because no external benchmark table exists within the dataset artifacts of the study, and constructing one from unverified sources was avoided. The internal reference point is the earlier evaluation of the project, whose stored comparison file had marked the SARIMAX and random forest rows as placeholders. The fresh execution replaced those placeholders with measured numbers and found both models to be substantially worse than the placeholders implied, which is itself a reportable finding on evaluation hygiene. In qualitative terms, a five to six percent MAPE on a four-year horizon annual series with 18 training points is within the error range typical of short-horizon extrapolative national forecasting, and the observed pattern where simple trend methods match or exceed a fitted ARIMA on a smooth and strongly trended aggregate is consistent with the established finding in time-series analysis that parsimonious models dominate at very small sample sizes. The contribution of the present evaluation is therefore methodological rather than a state-of-the-art claim, namely a fully re-executed and artifact-audited benchmark with interval and resampling evidence.

**3.3.13.16 Practical and Application Performance**

| Metric | ARIMA(1,1,1) | Random Forest |
| ----- | ----- | ----- |
| Six-step forecast latency, mean | 0.97 ms | 9.93 ms |
| Serialized size in joblib format | 93.6 KB | 181.6 KB |
| Fit time | 0.086 s | 0.103 s |

*Legend: ms milliseconds; kB kilobytes; ARIMA autoregressive integrated moving average; joblib model-serialization format.*

*Table 3.23: Deployment Characteristics*

Table 3.23 shows that production inference is inexpensive. The serving path reads precomputed forecast artifacts instead of executing a model, and the forecast endpoint responds at a measured mean of 3.7 milliseconds. Deployment feasibility is high because the model is sub-millisecond, about 94 kilobytes in size, and requires no GPU. The operational risks are not in compute but in staleness, because the served forecasts do not update until the artifacts are regenerated, and in the premium-plan gating of the forecast routes. On practical usefulness, the forecasts are suitable as directional and trend guidance with interval context and should be presented to users with the intervals visible rather than as precise planning figures.

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

The supported verdict is that the forecasting component is suitable for use as a trend-extrapolation service as long as its intervals and limitations are surfaced to users, and it should not be presented as a precision planning instrument. The recommended improvements in order of leverage are the acquisition of monthly or quarterly Department of Energy (DOE) series which multiplies the effective sample size, per-target order selection, exogenous demand drivers where SARIMAX showed promise, scheduled artifact regeneration to prevent silent staleness, and extending learned calibration to the physics-based suitability scores only if measured labels become available, since those scores are currently deterministic and were correctly excluded from this machine learning evaluation.

---

*End of insert. Evidence sources: docs/LUMI_TECHNICALTESTING.md for the testing instrument, docs/LUMI — Technical Evaluation_ Complete Test Results.md for the executed results, and docs/09-Technical-Evaluation/ML_Evaluation_Results_and_Discussion.md with docs/09-Technical-Evaluation/artifacts/rerun-2026-09-15/ for the machine learning artifacts. The promotional video at video/out/LumiPromo.mp4 reflects the same demonstrated flows but is not test evidence.*
