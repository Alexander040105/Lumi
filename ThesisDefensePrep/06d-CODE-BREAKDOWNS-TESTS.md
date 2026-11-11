# 06d — Code Breakdowns: Test Files & Misc

> Logic walkthrough for every cited test file and misc Python/JS file. For test files the
> "logic" is *what each class asserts and why it matters to the defense* — cross-referenced to
> `04-TESTING-AUDIT.md` §4 for counts/status.
>
> **TOC:** [Unit suite](#unit-suite-testsunit) · [Integration suite](#integration-suite-testsintegration) ·
> [Backend suite](#backend-suite-fastapi-backendtests) · [Frontend vitest](#frontend-vitest) ·
> [Misc scripts](#misc-scripts)

---

## Unit suite — `tests/tests/unit/`

### `conftest.py` (304 ln) — unit fixtures/mocks
- Centralizes **fake env vars** (Supabase URL/key placeholders — commit `a4b111c` fixed Settings validation errors), mock Supabase/Redis clients, sample DataFrames, and fixture factories shared by all unit tests. Marker system (`mock`/`live`/`local`/`benchmark`) defined in `pytest.ini`.

### `test_ai_service.py` (228 ln, 18 tests) — AI pipeline unit tests
- `TestPromptConstruction` — prompt builders include payload values + grounding rules.
- `TestJsonNormalization` — `_normalize_analysis_output`/`parse_*_json_response` handle malformed LLM JSON (regex extraction, empty→`{}`).
- `TestRagRetrievalMock` — retrieval returns expected chunk shape/metadata (mocked index).
- `TestErrorHandling` — provider failures → graceful dict/empty, never raise to user.
- `TestGeminiModuleImports` — module loads without `google-genai` installed (lazy-import guarantee → Vercel bundle can omit it).

### `test_geothermal_calculations.py` (519 ln, 56 tests) — geothermal physics tests
- `TestHaversine` (distance math), `TestNormalize`, `TestFaultDistance`, `TestFaultDensity`, `TestVolcanoDistance`, `TestHeatflowScore`, `TestGeothermalGradient`, `TestReservoirTemperature` + suitability/output compute classes — every geothermal formula validated incl. None/edge handling and measured-vs-estimated flags.

### `test_ml_preprocessing.py` (253 ln, 22 tests) — ML data-prep tests
- `TestPreprocessEnergyData`, `TestCreateTimeFeatures`, `TestSplitTrainTest`, `TestLinearTrendForecast`, `TestCalculateMape`, `TestScikitLearnMetrics` — preprocessing pipeline + baseline-model math used in `pilot_run` comparisons.

### `test_new_improvements.py` (280 ln, 18 tests) — post-audit hardening tests
- `TestSafeJSONFormatter` (log records → JSON), `TestRateLimitMiddleware` (sliding-window incl. merged-counter behavior), `TestRedisFallback` (NullRedis paths), `TestForecastingHelpers` (`_safe_float` NaN→None), `TestRAGReranking`, `TestSettings` (env parsing/defaults).

### `test_rag_embeddings_client.py` (92 ln, 5 tests) — embeddings
- `test_encode_single_returns_384d` (dimension contract), `test_encode_uses_redis_cache` (cache hit skips provider), `test_encode_batch`, `test_encode_openai` (provider variant), `test_unsupported_provider` (clear error).

### `test_rag_pgvector_store.py` (92 ln, 5 tests) — pgvector store
- `test_retrieve_context_shape` (result dict contract), `test_retrieve_with_filter_passes_params` (filters reach `match_rag_chunks` RPC), `test_index_stats_count`, `test_ensure_index_built_empty`/`_ready` (no-op semantics for pgvector backend).

### `test_renewable_calculations.py` (440 ln, 53 tests) — **the calc-engine test file**
- `TestSolarTemperatureFactor` (temp derating bounds), `TestSolarDustLoss`, `TestSolarHumidityDegradation`, `TestSolarPerformanceRatio` (PR multiplicative aggregation), `TestSolarCalc`, `TestWindLoadAverages`, `TestWindCalculateOutput` (power-curve regions, **Betz-limit rejection**), `TestHydroNormalize` (+ hydro flow/output classes) — the direct evidence that §2.7.2.2.8 formulas behave correctly and refuse nonphysical inputs.

## Integration suite — `tests/tests/integration/`

### `conftest.py` (4 ln) — integration fixtures.

### `test_api.py` (418 ln, 26 tests) — live API contract tests
- `TestHealthEndpoint`, `TestEnergyHubEndpoints`, `TestEcoSimEndpoints`, `TestAuthEndpoints`, `TestForecastEndpoints`, `TestEcoSimPost`, `TestResponseSchema` — endpoint status/shape against a running backend (`live`/`local` markers → many were env-skipped; `04` §4.3).

### `test_database.py` (412 ln, 30 tests) — DB schema/CRUD tests
- `TestSchemaExists` (tables/columns present), `TestRegions/Provinces/MunicipalitiesCRUD`, `TestClimateDataCRUD`, `TestHydropowerSuitabilityCRUD`, `TestForeignKeyIntegrity`, `TestRegionalLookupView` — needs a test DB (`TEST_DATABASE_URL`) → env-gated.

### `test_pipeline.py` (362 ln, 30 tests) — data-pipeline integration
- `TestDataLoading` → `TestPreprocessing` → `TestFeatureEngineering` → `TestModelTraining` → `TestForecastGeneration` → `TestApiFormatting` → `TestCompletePipeline` (end-to-end) → `TestFailureHandling` — the ingest→forecast→API chain.

### `performance_test.py` (361 ln, 13 tests) — perf assertions
- `TestDatasetLoadingPerformance`, `TestPredictionPerformance`, `TestApiResponsePerformance`, `TestMapAggregationPerformance`, `TestRagRetrievalPerformance`, `TestMemoryPerformance` — `benchmark`-marked thresholds.

## Backend suite — `fastapi-backend/tests/`

### `conftest.py` — app client fixtures (TestClient, mock services, env placeholders).

### `test_admin_export.py` (175 ln, 4 tests) — admin CSV export
- `_FakeResponse/_FakeQuery/_FakeRpc/FakeSupabaseClient` — fake Supabase plumbing; `test_usage_export_returns_csv`, `test_logs_export_returns_csv` (CSV shape+content), `test_*_requires_auth` (401 unauthenticated).

### `test_calibration.py` (351 ln, 19 tests) — scoring-bias calibration tests
- `test_wind_score_is_output_based_not_step_function` (score tracks output continuously, no plateaus), `test_wind_score_zero/capped/300kwh`, `test_hydro_score_baseline_100_kwh` (100 kWh→score 100 anchor), `test_scores_comparable_across_sources` — **encodes the recalibration invariants** so future edits can't silently re-bias scoring.

### `test_catchment_enrichment.py` (327 ln, 21+ tests) — enrichment data quality
- `test_enrichment_csv_has_all_municipalities`, `no_duplicate_ids`, `no_nulls_in_key_columns`, `match_methods_are_valid`, `within_count_matches_expected`, `stream_head_non_negative/within_physical_bounds`, `feasibility_penalty_in_range`, `effective_catchment_area_in_range`, `runoff_coefficient_in_range`, `test_catchment_loader_returns_data/none` — validates the Boothroyd dataset feeding hydro.

### `test_ecosim_explanations.py` (79 ln, 3 tests) — explanation logic
- `test_build_static_renewable_explanations_embeds_output_numbers` (real numbers appear in text), `zero_output_omits_number` (no "0 kWh" claims), `returns_generated_without_municipality_id` (no-ID path skips cache).

### `test_ecosim_quezon.py` (145 ln, 6 tests) — named-region regression
- `_FailingQuery/_FailingClient` (simulate Supabase outage); `test_quezon_province/municipality_no_500` (fallbacks prevent 500s), `test_build_ecosim_dashboard_quezon_province`, `test_get_province/municipality_data_quezon`, `test_missing_csv_fallbacks_return_none_or_empty` — a real past bug (Quezon data gaps) pinned as a test.

### `test_llm_sanitizer.py` (80 ln) — sanitizer unit tests (fence/HTML/JSON-strip assertions).

### `test_regression.py` (145 ln, ~5 tests) — aggregation regressions
- `test_format_score_scales_normalized`, `test_aggregate_municipality_climate_monthly_means`, `empty_input`, `test_get_or_compute_province_climate_batches_and_aggregates`, `test_aggregate_to_province_averages_municipality_scores` — province aggregation math pinned.

### `test_routes.py` (279 ln, ~11 tests) — quota/route behavior
- `MockEnergyHubService`; `test_ecosim_get_anonymous_first_request` / `_second_request_blocked` (quota kicks in), `test_ecosim_get_authenticated_no_quota` (users bypass), `test_ecosim_ai_fills_empty_renewable_analysis`/`preserves_llm_*` (AI fill-in logic), `test_ecosim_post_*` quota, `test_energyhub_ai_insight_static_no_quota`/`_llm_anonymous_quota`/`analyze_chart_anonymous_quota`, `test_energyhub_authenticated_bypass_quota` — the anonymous-quota contract.

### `test_security_fixes.py` (536 ln) — post-audit security tests
- `TestGeothermalNotFound` (PGRST116→404), `TestMapValidation` (type/level 422s), `TestEnergyHubForecastValidation` (metric enum 422), `TestForecastRunValidation`, + merged rate-limit counters, fail-closed user status, XFF-trust rules, ETL table allowlist (**the 2 async tests that env-fail without pytest-asyncio** — `04` §3.1).

### `test_simulations_audit.py` (143 ln, ~7 tests) — saved-sim hardening
- `TestSimulationNotFound` (get/patch/delete → 404 not 500), `TestSimulationInputValidation` (negative IDs rejected, **HTML in label stripped**, bracket-only label rejected), `TestMissingProfileFailsClosed` (SEC-03).

### `test_wind_hydro_plants.py` (115 ln, ~8 tests) — plant-proximity tests
- `TestWindPlants` (loader, `near_ilocos`, boost raises score, no-plants no-boost, generation scale + cap); `TestHydroPlants` (loader, `near_bulacan`, boost + cap-at-100).

## Frontend vitest

- `test/setup.js` — jsdom + testing-library bootstrap.
- `__tests__/i18n-keys.test.js` — **en/fil dictionary key parity** (no missing translations).
- `__tests__/I18nProvider.test.jsx` — provider renders, `t()` resolves + interpolates.
- `__tests__/theme-contrast.test.js` — theme token contrast/accessibility assertions.
- `components/__tests__/DashboardChart.test.jsx` (52 ln) — framework-smoke test: renders a `MockChart` placeholder w/ data-point fixtures; verifies vitest+jsdom wiring, not real chart code.
- `components/__tests__/EcosimWizard.test.jsx` (121 ln) — real component test: `setup()` injects all wizard props as `vi.fn()` spies (municipality mode defaults) wrapped in `I18nProvider`; `fireEvent` drives step interactions/assertions.
- `components/__tests__/SearchableSelect.test.jsx` (59 ln) — renders `SearchableSelect` w/ 2-item fixture + `vi.fn()` callbacks; asserts filter/render/click-select behavior.
- `utils/ecosimAnalysis.test.js` (33 ln), `ecosimPdf.test.js` (327 ln — `flatText` helper inspects pdfmake doc tree), `matchProviders.test.js` (164 ln — `P()` fixture factory + ranking assertions), `municipalities.test.js` (95 ln — filter/nearest + `ids()` helper).

## Misc scripts

- `api/index.py` — see `06a` §serverless-entry.
- `tests/run_tests_and_save.py` — runs suites and persists reports to `tests/test_results/`.
- `tests/pilot_run/evaluate_models.py` — trains+compares ARIMA vs Linear/Holt/RF on the same data → `model_metrics_*.csv` + plots; the evidence that ARIMA(1,1,1) was *selected*, not assumed.
- `scripts/test_api.py` (16 ln) — PSA API pagination probe (opposite of a test file — dev utility).
- `scripts/verify_fixes.py` (427 ln) — post-fix compile/import verification harness.
- `python_scripts/prepare_national_energy_data.ipynb` — notebook twin of `prepare_national_energy_csv.py`.

### Eval/benchmark artifact scripts — `docs/09-Technical-Evaluation/artifacts/`

These are the **evidence-generating harnesses** behind the deck's measured numbers (not pytest suites):

- `scripts/endpoint_sweep.py` (311 ln) — hits every mounted endpoint on `:8000` w/ valid + negative cases; records status/latency/verdict → CSV+JSONL. Auth endpoints probed w/o token + malformed token (expect 401); happy-paths marked `[OPEN]` needing a session → **the 82/82 sweep** (`04` §3).
- `scripts/security_probes.py` (161 ln) — live probes: JWT matrix (none/malformed/`alg:none`/wrong-sig/expired), security headers, CORS preflight, docs exposure, error-body leakage → `probes.json` → **the 18 SEC-* probes** (`04` §5).
- `scripts/failure_matrix.py` (272 ln) — TestClient + patched singletons simulate dependency failures/malformed inputs w/o touching `.env`; one real Groq fallback call in TC-FR-01 → `failure_matrix.json` (degradation-proof evidence).
- `load/locustfile.py` (94 ln) — Locust profiles: **A** raw capacity (loopback exempt → true ceiling); **B** `XFF:203.0.113.7` → verifies 60/min limiter engages (429+Retry-After); **C** `XFF:127.0.0.1` → *documents the spoofed-loopback bypass* (SEC-01 caveat, D14/fixed in `rate_limit.py`) → **the 100-user/no-failure result** (`04` §3.4).
- `rerun-2026-09-15/scripts/` — post-fix re-runs of `endpoint_sweep.py`/`security_probes.py` producing the corrected numbers the deck quotes.

---
*Test intents summarized from class names + assertion reads; per-file counts live in `04-TESTING-AUDIT.md` §4 — that file is the reconciliation source of truth.*
