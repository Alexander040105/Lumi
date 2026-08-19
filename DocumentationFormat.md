# **9. TESTING AND VALIDATION**

| **Test ID** | **Feature / Requirement Tested** | **Testing Method** | **Expected Result** | **Actual Result** | **Status** |
| --- | --- | --- | --- | --- | --- |
| T-01 | EcoSim anonymous dashboard request (`/api/v1/ecosim/` with `municipality_id`) | Functional / Unit — `fastapi-backend/tests/test_routes.py` | Returns HTTP 200 with `input_warning`, `generation_score`, and renewable energy outputs | 200 response; mocked dashboard fields returned as asserted (`input_warning=True`, `generation_score=60.0`, `remaining_anonymous_requests=0`) | Passed |
| T-02 | EcoSim `data_source` selector (`nasa` / `atlas` / `era5` / `auto`) | Functional / Manual — runtime verification via `build_ecosim_dashboard_response` | `auto` uses Global Solar Atlas / Global Wind Atlas; `era5` uses ERA5 10 m wind; labels are accurate | `auto` for 5145 → `Global Solar Atlas / Global Wind Atlas` (100 m wind); `era5` for 5145 → `ERA5 (wind, 10m) + NASA POWER` (10 m wind) | Passed |
| T-03 | EnergyHub empty-data response model safety | Functional / Code-quality — targeted checks in `CHANGELOG_v2.1_FIXES.md` | Predictor returns schema-compatible defaults when `doe_datasets` is empty; no 500s on `/ai-insight` or `/trends` | 29 targeted checks passed (`predictor.py` defaults present, `rag_pipeline.py` `None` guard, `supabase_service.py` cleanup, etc.) | Passed |
| T-04 | EcoSim AI analysis within Vercel 10-second limit | Performance — live deployment / cache timing, `CHANGELOG_v3.2.md` verification | First AI call <10 s; subsequent cache hits faster | ~7.8 s first call, ~3 s cache hits with Groq + Redis L1 + Supabase L2 | Passed |
| T-05 | CORS preflight and cross-origin frontend requests | Security / Integration — `main.py` + CORS commits | OPTIONS requests handled by CORS middleware and `Access-Control-Allow-Origin` covers deployed Vercel frontends | CORS middleware added outermost; `allow_origin_regex` configured for Vercel previews; `allow_methods`/`allow_headers` restricted | Passed |
| T-06 | Design-review PDF copy/UI revisions (Home, About, EcoSim, EnergyHub) | Usability — requirements from `LUMI-System-Revisions.pdf` implemented | Copy, labels, and layout changes reflected in frontend pages | `Home.jsx`, `About.jsx`, `Ecosim.jsx`, `EcosimWizard.jsx` etc. updated per `revisionFiles/LUMI-Revisions-Instructions.md` | Passed |

---

# **10. PROBLEMS / CHALLENGES ENCOUNTERED**

| **Problem / Challenge** | **Affected Requirement** | **Impact** | **Solution / Action Taken** | **Status** |
| --- | --- | --- | --- | --- |
| EnergyHub 500 on `/ai-insight` and `/trends` due to Pydantic `ResponseValidationError` when `doe_datasets` empty | EnergyHub FR: deliver AI-assisted data-driven insights | High (endpoint crash) | `app/ml/predictor.py` now returns complete, schema-compatible defaults for empty data; DOE CSVs bundled in Vercel package (`vercel.json` `includeFiles`) | Resolved |
| Vercel `excludeFiles` glob exceeded 256-character limit | NFR: deployable on Vercel serverless | High (deployment rejected) | Moved large directory ignores to `.vercelignore`; kept `vercel.json` `excludeFiles` under 256 chars | Resolved |
| CORS preflight / cross-origin failures on Vercel deployments | NFR: frontend can call backend API | Medium (OPTIONS blocked on some origins) | Added `cors_origin_regex` with deployed Vercel and preview patterns; moved `CORSMiddleware` outermost in `main.py` | Resolved |
| EcoSim timeout under Vercel 10-second limit on AI analysis | EcoSim FR: AI-powered analysis | High (504s / perceived CORS) | Added `municipality_climate_averages` table; per-municipality queries; switched default LLM to Groq; added Redis L1 and Supabase L2 AI cache; 5-second AI timeout | Resolved |
| Province EcoSim aggregation mismatch between area-weighted municipal average and province centroid | EcoSim FR: multi-granularity (province-level) | Medium (single centroid not representative for large provinces) | Created `province_atlas_averages` with both area-weighted municipal and centroid-sample values, `reconciliation_note` for >5% deviations | Resolved |
| Groq API `BadRequestError` and JSON-format errors in AI chat | EcoSim/Chat FR: LLM inference | Medium (AI responses failed) | Updated Groq model IDs (`groq/compound-mini`, `groq/compound`, `qwen/qwen3.6-27b`); removed forced `response_format={"type":"json_object"}` | Resolved |

---

# **11. BUG / ISSUE TRACKING**

| **Bug ID** | **Description** | **Severity** | **Date Identified** | **Action Taken** | **Status** |
| --- | --- | --- | --- | --- | --- |
| BUG-01 | `ResponseValidationError` on `/api/v1/energyhub/ai-insight` and `/trends` when DOE data empty | High | 2026-08-07 | `predictor.py` returns schema-safe defaults for `AiInsightResponse`, `ForecastResponse`, `SourceBreakdownResponse`; bundled DOE preprocessed CSVs in Vercel function | Resolved |
| BUG-02 | Vercel deployment rejected: `excludeFiles` string >256 characters | High | 2026-08-07 | Shortened `vercel.json` `excludeFiles`; created/updated `.vercelignore` for directory-level ignores | Resolved |
| BUG-03 | CORS preflight blocked for deployed Vercel frontend origins | Medium | 2026-08-06 | Added `cors_origin_regex` defaults for Vercel deploys and previews; moved CORS middleware to outermost in middleware stack | Resolved |
| BUG-04 | EcoSim AI analysis timed out >10s on Vercel | High | 2026-08-18 | Migrated to Groq, added Redis L1 + Supabase L2 `ecosim_ai_cache`, capped AI call at 5s with background worker, shortened cache TTL on fallback | Resolved |
| BUG-05 | Groq model-name `BadRequestError` and JSON schema errors in chat/AI routes | Medium | 2026-08-18 | Corrected Groq model IDs; removed `response_format={"type":"json_object"}` for markdown prompts | Resolved |
| BUG-06 | Province-level atlas values diverged from single-centroid sample for large/hilly provinces | Medium | 2026-08-19 | Added `province_atlas_averages` table with area-weighted municipal averages, direct centroid samples, and reconciliation notes | Resolved |

---

## Evidence Log

| Row / Item | Source Commit / File | Evidence Location |
| --- | --- | --- |
| T-01 (EcoSim route tests) | `c83067d` 2026-08-19 | `fastapi-backend/tests/test_routes.py` |
| T-02 (data_source runtime) | `a808a60` 2026-08-20, `e32be88` 2026-08-20 | `fastapi-backend/app/services/ecosim.py`, runtime tests in this session |
| T-03 (EnergyHub empty-data checks) | `be0439b` 2026-08-07 | `docs/LESSONS_LEARNED.md` sections 1–2, `docs/CHANGELOG_v2.1_FIXES.md` verification list |
| T-04 (AI performance) | `614b5a1` 2026-08-18 | `CHANGELOG_v3.2.md` sections 2.1/3.1, `docs/LESSONS_LEARNED.md` section 5 |
| T-05 (CORS) | `2665956` 2026-08-19, `22bbed6` 2026-08-06, `79bfe27` 2026-08-06 | `fastapi-backend/main.py` lines 29–36; `app/config/settings.py` |
| T-06 (design review) | `4fc1fc6` 2026-08-18 | `revisionFiles/LUMI-Revisions-Instructions.md`; `CHANGELOG_v3.2.md` frontend changes |
| P-01 / BUG-01 (EnergyHub 500) | `be0439b` 2026-08-07 | `docs/LESSONS_LEARNED.md`; `CHANGELOG_v2.1_FIXES.md` |
| P-02 / BUG-02 (Vercel excludeFiles) | `cfbd082` 2026-08-07 | `vercel.json`; `docs/LESSONS_LEARNED.md` section 3 |
| P-03 / BUG-03 (CORS) | `22bbed6`, `79bfe27`, `2665956` 2026-08-06 / 19 | `main.py`; `CHANGELOG_v3.2.md` |
| P-04 / BUG-04 (AI timeout) | `614b5a1` 2026-08-18 | `CHANGELOG_v3.2.md`; `CHANGELOG_v2.1_FIXES.md` section 5 |
| P-05 / BUG-06 (province aggregation) | `cf80c25` 2026-08-19 | `supabase_tables_scripts/province_atlas_schema.sql`; `docs/PROVINCE_ATLAS_VALIDATION.md` |
| P-06 (Groq errors) | `614b5a1` 2026-08-18 | `CHANGELOG_v3.2.md` sections 2.1/3.2; `fastapi-backend/app/services/groq_client.py` |
| NASA POWER future-date validation | — | Searched `scripts/run_nasa_for_gaps.py`, `python_scripts/ingest_nasa_power_monthly.py`, and `etl_orchestrator.py`; no explicit future/out-of-range date guard found; not listed in tables because evidence is absent. |
