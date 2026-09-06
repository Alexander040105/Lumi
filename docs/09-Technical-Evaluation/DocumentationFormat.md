# **9. TESTING AND VALIDATION**

| **Test ID** | **Feature / Requirement Tested** | **Testing Method** | **Expected Result** | **Actual Result** | **Status** |
| --- | --- | --- | --- | --- | --- |
| T-01 | Renewable energy calculation correctness (solar, wind, hydro) | Unit testing of solar temperature factor, wind Betz-limit enforcement, and hydro flow-rate bounds | Solar temperature factor equals 1.0 at 25°C; power coefficient exceeding Betz limit raises a validation error; hydropower flow is constrained to realistic bounds | 48 unit tests passed for renewable-energy calculations | Passed |
| T-02 | Machine-learning preprocessing and metric computation | Unit testing of missing-value imputation, feature scaling, and forecast error metrics | Missing values handled via forward/backward fill; MAE, RMSE, MAPE, and R² computed deterministically | 20 unit tests passed for ML preprocessing and metric computation | Passed |
| T-03 | AI prompt construction, JSON normalization, and RAG retrieval | Unit testing with mocked LLM and retrieval responses | Prompts contain grounded simulation data; JSON outputs contain the required recommendation fields; RAG returns scored chunks | 18 unit tests passed for AI service logic | Passed |
| T-04 | EcoSim dashboard API with valid and invalid inputs | Integration testing of the EcoSim GET and POST endpoints | HTTP 200 for valid municipality selection; HTTP 422 for missing or invalid parameters; response schema matches the dashboard model | Endpoint tests passed for 200 and 422 cases | Passed |
| T-05 | Database referential integrity and constraint compliance | Integration testing of barangay→municipality→province→region foreign keys and CHECK constraints | All child records reference valid parents; invalid month and year values are rejected | Database integration tests passed | Passed |
| T-06 | DOE-to-ML-to-API forecast pipeline | End-to-end pipeline test of DOE v2 ingestion, ARIMA training, and API exposure | Preprocessed DOE data produces forecast CSVs; FastAPI serves historical and forecast series | 30 pipeline integration tests passed | Passed |
| T-07 | EcoSim AI and EnergyHub response time under Vercel constraints | Performance timing of the AI analysis and key dashboard endpoints | AI analysis completes below the 10-second serverless threshold; cached responses are materially faster | First AI call measured at ~7.8 seconds; subsequent cache hits at ~3 seconds | Passed |
| T-08 | Multi-granularity EcoSim analysis (municipality, province, barangay) | Functional verification of province aggregation and barangay multiplicative scoring | Province mode returns aggregated climate, terrain, and economic values; barangay mode applies multiplicative suitability adjustments | Province and barangay dashboards return the expected structure and values | Passed |
| T-09 | Design-review PDF copy and UX implementation | Usability review against the requirements captured in the panelist revision document | Home, About, EcoSim, and EnergyHub pages adopt the requested copy, labels, layout, and citation behavior | Frontend pages updated per the design-review specification | Passed |
| T-10 | Global Solar Atlas and Global Wind Atlas extraction and ingestion | Data-accuracy validation of raster-sampled municipal and provincial values | All 1,376 municipality centroids and 81 province polygons sampled; area-weighted and centroid methods reconciled | 1,376 municipal rows and 81 provincial rows ingested with reconciliation notes | Passed |
| T-11 | ERA5 reanalysis wind integration and source precedence | Data-accuracy and source-switching verification of 10 m wind values | 1,376 municipality and 81 province ERA5 rows created; `auto` prefers Atlas 100 m wind, `era5` uses Copernicus 10 m wind | Ingestion completed; runtime checks confirmed correct source labels | Passed |
| T-12 | Authentication, CORS, and rate limiting | Security testing of protected endpoints and cross-origin frontend access | Unauthenticated requests to protected routes return 401; OPTIONS preflight accepted; origin patterns cover Vercel deployments | Auth dependency and CORS middleware active across protected routes | Passed |

---

# **10. PROBLEMS / CHALLENGES ENCOUNTERED**

| **Problem / Challenge** | **Affected Requirement** | **Impact** | **Solution / Action Taken** | **Status** |
| --- | --- | --- | --- | --- |
| NASA POWER 0.5° grid made adjacent municipalities appear climatically identical | EcoSim accuracy and defensibility | High | Global Solar Atlas and Global Wind Atlas rasters were integrated at true municipal and provincial centroids; NASA POWER was retained as an explicit fallback | Resolved |
| Municipal and provincial centroids in the base `municipalities` and `provinces` tables were not geometrically authoritative | Geospatial accuracy of climate and terrain lookups | High | Authoritative centroids and area values were generated from PSA/PSGC boundary GeoJSON, stored in `geospatial_metadata`, and used for all subsequent sampling | Resolved |
| DOE v2 preprocessing produced a duplicate `year` column that corrupted downstream consumers | EnergyHub data integrity | High | The hardcoded column-injection hack was removed and the parser was aligned with the actual CSV schema | Resolved |
| EnergyHub insight and trend endpoints returned 500-series errors when DOE data was missing or empty | EnergyHub availability and Pydantic response safety | High | The predictor was hardened to return complete, schema-compatible default responses for missing data, and the preprocessed DOE CSVs were bundled with the Vercel function | Resolved |
| Vercel function routes returned 404 for `/docs`, `/api/v1/health`, and other public paths | Deployment availability | High | Catch-all rewrites, an ASGI path-normalization middleware, and dual health-endpoint registration were introduced | Resolved |
| Vercel function bundle exceeded the `excludeFiles` 256-character limit and included unnecessary heavy directories | Deployment size and build success | High | Large directory exclusions were moved to `.vercelignore`; `vercel.json` `excludeFiles` was shortened to a small glob of build and cache artifacts | Resolved |
| Cross-origin requests from the deployed Vercel frontend were rejected at the preflight stage | Frontend-backend connectivity | Medium | The CORS middleware was placed at the outermost position, and an origin regex was configured to recognize Vercel production and preview domains | Resolved |
| EcoSim AI analysis exceeded the 10-second Vercel serverless execution limit | EcoSim AI responsiveness | High | The default LLM was switched to Groq, a Redis L1 and Supabase L2 AI cache was added, and the AI call was capped at 5 seconds with a background worker for non-blocking results | Resolved |
| Province-level EcoSim values diverged when a single centroid was used instead of an area-weighted municipal average | Province-level accuracy | Medium | The `province_atlas_averages` table was created with both area-weighted municipal and direct centroid methods, and reconciliation notes are recorded when the two differ by more than 5% | Resolved |
| Product recommendation data mixed currencies and misclassified hydro equipment as wind | EcoSim product cards and cost realism | Medium | Prices were normalized to Philippine pesos before ranking, and categories were assigned from exact source-file suffixes rather than loose substrings | Resolved |
| ERA5 GRIB ingestion required specialized tooling and was blocked by absent Supabase tables | ERA5 integration | Medium | The `cfgrib` and `eccodes` stack was installed, 10 m wind was extracted at centroids, municipality and province ERA5 schemas were created, and local CSV fallbacks were bundled | Resolved |
| Duplicate province identifiers for Isabela caused an `ON CONFLICT` failure during province Atlas upsert | Province Atlas integrity | High | The province-building script was changed to keep the largest-area match for duplicate province IDs, producing 81 unique provincial rows | Resolved |

---

# **11. BUG / ISSUE TRACKING**

| **Bug ID** | **Description** | **Severity** | **Date Identified** | **Action Taken** | **Status** |
| --- | --- | --- | --- | --- | --- |
| BUG-01 | Duplicate `year` column in the DOE v2 preprocessing pipeline | High | 2026-07-12 | Removed the hardcoded column injection and aligned the parser to the true schema | Resolved |
| BUG-02 | `ResponseValidationError` on `/api/v1/energyhub/ai-insight` and `/trends` when DOE data was empty | High | 2026-08-07 | Introduced schema-safe default responses for `AiInsightResponse`, `ForecastResponse`, and `SourceBreakdownResponse`; bundled DOE CSVs in the Vercel package | Resolved |
| BUG-03 | Vercel 404 on `/docs` and `/api/v1/health` because serverless functions match by exact file path | High | 2026-08-06 | Added catch-all rewrites and an ASGI path-normalization middleware to map public URLs to the FastAPI app | Resolved |
| BUG-04 | Vercel deployment rejected because the `excludeFiles` glob string exceeded 256 characters | High | 2026-08-07 | Moved large directory ignores to `.vercelignore` and kept `vercel.json` `excludeFiles` under the limit | Resolved |
| BUG-05 | CORS preflight blocked for deployed Vercel frontend and preview origins | Medium | 2026-08-06 | Configured a `cors_origin_regex` covering Vercel domains and moved `CORSMiddleware` to the outermost middleware layer | Resolved |
| BUG-06 | EcoSim AI analysis exceeded the 10-second Vercel serverless limit | High | 2026-08-18 | Migrated the default LLM to Groq, added a Redis L1 and Supabase L2 `ecosim_ai_cache`, and capped the AI call at 5 seconds with a background worker | Resolved |
| BUG-07 | Province atlas values from a single centroid diverged from the area-weighted municipal average | Medium | 2026-08-19 | Created `province_atlas_averages` with both area-weighted municipal and centroid-sample columns, recording reconciliation notes for >5% differences | Resolved |
| BUG-08 | Product recommendation data mixed currencies and misclassified equipment by loose substrings | Medium | 2026-08-05 | Normalized all prices to Philippine pesos and enforced exact source-file suffix matching for category assignment | Resolved |
| BUG-09 | Duplicate `province_id=258` for Isabela caused an upsert conflict during province Atlas ingestion | High | 2026-08-19 | Retained the largest-area match for duplicate province IDs and regenerated the 81 unique province rows | Resolved |
| BUG-10 | ERA5 `data_source` labels were polluted when switching between `auto`, `atlas`, and `era5` modes | Medium | 2026-08-20 | Isolated source-specific climate rows and corrected the source-labeling logic so `auto` does not overwrite Atlas with ERA5 | Resolved |
| BUG-11 | Supabase REST filters broke on special characters in query values | Medium | 2026-07-25 | Applied `urllib.parse.quote` to filter values before sending the REST request | Resolved |
| BUG-12 | EcoSim dashboard routes returned unstable or incomplete responses | Medium | 2026-05-25 | Restructured the EcoSim route handling and response assembly to return consistent dashboard payloads | Resolved |

---

## Evidence Log

| Row / Item | Source Commit / File | Evidence Location |
| --- | --- | --- |
| T-01, T-02, T-03 (unit tests) | `8b4ba13` (pytest setup); `CHANGELOG_v3.2.md` (176 unit, 24 mock, 30 pipeline tests) | `tests/docs/testing_methodology_report.md`; `tests/README.md`; `tests/tests/unit/` |
| T-04, T-05, T-06 (integration tests) | `c8513db` (pytest pythonpath); `CHANGELOG_v3.2.md` | `fastapi-backend/tests/test_routes.py`; `tests/tests/integration/test_api.py`; `tests/tests/integration/test_database.py`; `tests/tests/integration/test_pipeline.py` |
| T-07 (performance) | `614b5a1` 2026-08-18 | `CHANGELOG_v3.2.md` sections 2.1/3.1; `docs/01-Project-Overview/LESSONS_LEARNED.md` sections 4–5; `tests/tests/integration/performance_test.py` |
| T-08 (multi-granularity) | `c7689f1` 2026-07-12; `42151d7` 2026-06-30 | `docs/thesis/LUMI_THESIS_REVISIONS_MASTER.md` Phase 2 and Phase 7; `fastapi-backend/app/services/ecosim.py` |
| T-09 (usability / design review) | `4fc1fc6` 2026-08-18 | `docs/thesis/revisionFiles/LUMI-Revisions-Instructions.md` (sourced from `docs/thesis/revisionFiles/LUMI-System-Revisions.pdf`); `CHANGELOG_v3.2.md` |
| T-10 (Atlas integration) | `118aff9` 2026-08-19; `e420163` 2026-08-19; `cf80c25` 2026-08-19 | `docs/07-Data-Extraction-Reports/ATLAS_DATA_INTEGRATION.md`; `docs/07-Data-Extraction-Reports/PROVINCE_ATLAS_VALIDATION.md`; `supabase/table_scripts/province_atlas_schema.sql` |
| T-11 (ERA5 integration) | `a808a60` 2026-08-20; `e32be88` 2026-08-20 | `docs/07-Data-Extraction-Reports/ERA5_INTEGRATION.md`; `docs/07-Data-Extraction-Reports/ERA5_VALIDATION.md`; `fastapi-backend/app/services/ecosim.py` |
| T-12 (security) | `4500f0a` 2026-08-05; `2665956` 2026-08-19; `22bbed6` 2026-08-06 | `fastapi-backend/main.py`; `fastapi-backend/app/dependencies/auth.py`; `CHANGELOG_v3.2.md` |
| P-01, P-02, P-09, P-10, P-12 (Atlas/accuracy) | `118aff9` 2026-08-19; `e420163` 2026-08-19; `cf80c25` 2026-08-19; `a808a60` 2026-08-20; `e32be88` 2026-08-20 | `docs/09-Technical-Evaluation/DATA_ACCURACY_AND_THESIS_DEFENSE_GUIDE.md`; `docs/07-Data-Extraction-Reports/ATLAS_DATA_INTEGRATION.md`; `docs/07-Data-Extraction-Reports/ERA5_VALIDATION.md` |
| P-03, P-04, P-07 (EnergyHub/DOE) | `be0439b` 2026-08-07; `c7689f1` 2026-07-12 | `docs/01-Project-Overview/LESSONS_LEARNED.md`; `CHANGELOG_v2.1_FIXES.md`; `CHANGELOG_v3.2.md` |
| P-05, P-06, P-08 (Vercel/deployment) | `9cfff26` 2026-08-02; `742099a` 2026-08-06; `cfbd082` 2026-08-07; `907f268` 2026-08-06; `9d2c07d` 2026-08-05 | `docs/05-Setup-Guides/VERCEL_BACKEND_404_FIX.md`; `docs/01-Project-Overview/LESSONS_LEARNED.md`; `vercel.json`; `.vercelignore` |
| P-11 (ERA5 tooling) | `a808a60` 2026-08-20; `e32be88` 2026-08-20 | `docs/07-Data-Extraction-Reports/ERA5_INTEGRATION.md`; `scripts/inspect_era5.py`; `scripts/extract_era5_wind.py`; `scripts/ingest_era5_averages.py` |
| BUG-01 | `c7689f1` 2026-07-12 | `data/DOE_Data_Extracted/data_v2_preprocessing.py`; `CHANGELOG_v2.1_FIXES.md` |
| BUG-02 | `be0439b` 2026-08-07 | `docs/01-Project-Overview/LESSONS_LEARNED.md`; `fastapi-backend/app/ml/predictor.py` |
| BUG-03 | `742099a` 2026-08-06 | `docs/05-Setup-Guides/VERCEL_BACKEND_404_FIX.md`; `fastapi-backend/main.py`; `fastapi-backend/app/routes/health.py` |
| BUG-04 | `cfbd082` 2026-08-07 | `docs/01-Project-Overview/LESSONS_LEARNED.md` section 3; `vercel.json` |
| BUG-05 | `22bbed6` 2026-08-06; `79bfe27` 2026-08-06; `2665956` 2026-08-19 | `fastapi-backend/main.py`; `fastapi-backend/app/config/settings.py` |
| BUG-06 | `614b5a1` 2026-08-18 | `CHANGELOG_v3.2.md` sections 2.1/3.1; `fastapi-backend/app/services/gemini_funcs.py` |
| BUG-07, BUG-09 | `cf80c25` 2026-08-19 | `docs/07-Data-Extraction-Reports/PROVINCE_ATLAS_VALIDATION.md`; `supabase/table_scripts/province_atlas_schema.sql` |
| BUG-08 | `9d2c07d` 2026-08-05 | `CHANGELOG_v2.1_FIXES.md` section 1.3; `fastapi-backend/app/services/products.py` |
| BUG-10 | `e32be88` 2026-08-20 | `fastapi-backend/app/services/ecosim.py`; `fastapi-backend/app/services/atlas_data.py` |
| BUG-11 | `42cf377` 2026-07-25 | `CHANGELOG_v2.1_FIXES.md` section 1.2; `fastapi-backend/app/services/supabase_service.py` |
| BUG-12 | `ada43c7` 2026-05-25; `6a683a1` 2026-05-25 | `fastapi-backend/app/routes/ecosim.py`; `fastapi-backend/app/services/ecosim.py` |
