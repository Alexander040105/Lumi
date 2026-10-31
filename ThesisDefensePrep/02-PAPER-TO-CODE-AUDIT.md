# 02 — Paper ↔ Code Audit

> **Purpose:** answer any "show me the code for X in the paper" question in seconds, and let the
> developer track every code file in the repo — what it does and why it exists.
>
> **Method:** every technical claim in the thesis manuscript and the 27-slide deck was mapped to
> verified repo paths (each path checked to exist). File purposes come from module docstrings,
> code reads, `docs/` documentation, and `git log` history; anything not recorded is tagged
> `*(inferred)*`. Sources are cited as thesis section (§), deck slide (S#), or artifact path.
> Repo state: `main @ 438789c`, audited 2026-10-31.
>
> **Structure:** Part A = claim→code traceability matrix · Part B = exhaustive file inventory ·
> Part C = bidirectional gap lists · Part D = deep logic breakdowns of the ~25 core files.
>
> **Code logic:** Part D covers the core files in depth. Every *other* cited file gets a
> uniform logic breakdown in the companion volumes — [`06a`](./06a-CODE-BREAKDOWNS-BACKEND.md)
> (backend app), [`06b`](./06b-CODE-BREAKDOWNS-ETL-SCRIPTS.md) (ETL/ops scripts),
> [`06c`](./06c-CODE-BREAKDOWNS-FRONTEND.md) (React frontend),
> [`06d`](./06d-CODE-BREAKDOWNS-TESTS.md) (test files).

---

## PART A — Traceability matrix

### A.0 Specific objectives → modules → code

| Ref | Objective claim | Implementing code | What it does | Evidence |
|---|---|---|---|---|
| SO1 (S5) | Interactive map-based interface, site suitability per province/municipality | `react-frontend/src/pages/EnergyHub.jsx`, `Dashboard.jsx`; `components/energyhub/EnergyMap.jsx`, `ProvincialDemand.jsx`, `EnergyOverview.jsx`; backend `routes/energyhub.py`, `routes/map.py`, `routes/geospatial.py`; services `energyhub.py`, `map_service.py`, `geospatial_service.py`, `atlas_data.py` | Map UI + choropleth/overview/provincial-demand endpoints | IT experts rated Energy Dashboard & Map 4.50/5 (S5) |
| SO2 (S5) | Weighted multi-criteria recommendation engine | `services/mcda.py`, `mcda_weights_service.py`, `municipality_suitability_builder.py`, `confidence.py`; exposed via `services/ecosim.py` → `routes/ecosim.py` | AHP weights + weighted-sum scoring + PROMETHEE II ranking + confidence scoring | 82.22% agreement w/ engineers (S9) |
| SO3 (S5) | Predictive analytics on PH energy demand | `ml/predictor.py`, `services/forecasting.py`, `ml_worker_proxy.py`; `routes/forecast.py`, `routes/energyhub.py` (`/forecast`, `/model-comparison`, `/trends`) | SARIMA/ARIMA(1,1,1) fit+forecast, walk-forward backtest, model registry | MAE 6,829.09 GWh / MAPE 5.67% (S18) |
| SO4 (S5) | What-if simulation: solar/wind/hydro (geothermal reference) | `routes/ecosim.py` + `services/ecosim.py`; `solar_output_calc.py`, `wind_output_calc.py`, `hydro_output_calc.py`, `financials.py`, `products.py`, `hydro_plants.py`, `wind_plants.py`, `services/geothermal/*`; frontend `pages/Ecosim.jsx`, `components/ecosim/*` | Household what-if sim: consumption, savings, payback, recommendations | 4.40/5 EcoSim rating (S5) |
| SO5 (S5) | User-friendly interface aiding interpretation | `react-frontend/src/**` (pages, `components/shared/{Markdown,InsightCard,InterpretationBadge,CitationSources,NextStepList,HelpTooltip}`), `i18n/{en,fil}.json`, AI explanation endpoints | Dashboards, charts, AI explanations in plain language | 4.70/5 household clarity rating (S5) |
| SO6 (S6) | Evaluate usability/usefulness/acceptability | Household questionnaire (thesis §2.10.5); results in paper ch.3/4 | Survey instrument + analysis | 4.73 usability / 4.79 advantage (S9) |
| SO7 (S6) | Validate criteria & rule logic w/ barangay + engineers; software quality via IT experts | Engineering + IT instruments (§2.10.6–7); scoring code under validation: `mcda*.py`, `*_output_calc.py` | Criteria/weights validated by domain experts | 82.22% agreement; 4.47/5 ISO 25010 (S9) |
| SO8 (S6) | Performance testing: agreement rate, response time, ML MAE/RMSE | `tests/` + `fastapi-backend/tests/` + sweep/locust/security scripts; artifacts in `docs/09-Technical-Evaluation/` | Full test pyramid + live sweeps | 82.22%, ~104 ms, 6,829.09/8,257.12 (S18–19) |

### A.1 Algorithm-structure claims (thesis §2.7.2.2.8) → implementing code

| Paper algorithm (§2.7.2.2.8) | File | What the code does | Decision rationale |
|---|---|---|---|
| Solar temperature factor (25 °C STC deviation) | `fastapi-backend/app/services/solar_output_calc.py` | `calculate_temperature_factor` — **NOCT-based** correction (not a naive linear factor) | Docstring: "NOCT-based temperature correction (replaces simple linear factor)" — more physically accurate for household-scale estimates |
| Solar performance ratio aggregation (temp, dust, inverter, mismatch, wiring, degradation) | `solar_output_calc.py` | `calculate_performance_ratio`, `calculate_dust_loss_from_wind`, `calculate_degradation_from_humidity`, `solar_calc(_pvout/_advanced)` | Composable loss model; GHI-only fallback when DNI/DHI missing; air-density correction from surface pressure |
| Wind power output (P ∝ v³, swept area, density) | `wind_output_calc.py`, `python_scripts/wind_power_coefficient.py` | `calculate_wind_output`, `load_wind_averages`, `extrapolate_wind_speed`; Cp bounded by **Betz limit 16/27** (`python_scripts/wind_power_coefficient.py`) | Household power-curve calibrated (git `77bb8725`); unrealistic inputs raise errors (tests assert bounds) |
| Runoff coefficient (slope-based small catchment) | `hydro_output_calc.py` | C by slope band: <3°→0.30, 3–10°→0.45, 10–20°→0.60, >20°→0.75 (Javadinejad et al. 2022 in docstring) | Slope-from-terrain data decides runoff — physically grounded without field surveys |
| Micro-hydro design flow (rational method) | `hydro_output_calc.py` | `estimated_flow_rate` — catchment area × runoff coeff × rainfall intensity | Adapts civil-engineering rational method to municipality-scale data we actually have |
| Micro-hydro electrical output (run-of-river) | `hydro_output_calc.py` | `calculate_hydropower` — ρ·g·Q·H·η with head/flow clamps | Di Dio et al. cited in paper; clamps prevent nonphysical outputs (unit-tested) |
| Economic viability + recommendation scoring | `financials.py`, `mcda.py`, `mcda_weights_service.py` | NPV, IRR, LCOE, discounted + simple payback (PHP/kWh); weighted-sum + PROMETHEE II + AHP consistency check | Standard investment metrics households understand; weights come from `mcda_weights_service` (DB w/ hardcoded fallback so scoring never breaks) |
| ARIMA(1,1,1) forecasting | `ml/predictor.py`, `services/forecasting.py` | SARIMA/ARIMA fit, forecast w/ CI, walk-forward backtest, NaN/Inf sanitization for JSON | §3.3.13 + `ml/aic_grid.csv` artifact documents order selection; registry table `forecast_model_runs` (migration 0005) |
| Composite renewable potential score (choropleth) | `map_service.py`, `municipality_suitability_builder.py`, `atlas_data.py` | Aggregates municipal climate/terrain → single score per admin unit via materialized views `mv_province_map_data`, `mv_municipality_map_data` | Precomputed scores keep map reads fast (docstring: materialized-view integration) |

### A.2 Weighted MCDM recommendation engine (SO2, S10, S18)

| File | What it does | Decision rationale |
|---|---|---|
| `services/mcda.py` | AHP consistency check for weight matrices; weighted-sum aggregation; PROMETHEE II outranking | Docstring: "AHP weight validation and PROMETHEE ranking" — gives both a weighted score AND an outranking cross-check *(inferred: dual methods defend against a single-method critique)* |
| `services/mcda_weights_service.py` | Loads AHP-derived criterion weights from Supabase; falls back to hardcoded defaults if table missing/empty | Docstring: "the scoring pipeline never breaks" — resilience over strictness |
| `services/municipality_suitability_builder.py` | Computes per-municipality suitability scores for solar/wind/hydro/geothermal and composite | Core scoring assembly for the 82.22% agreement figure |
| `services/confidence.py` | Per-source confidence score (0–100) propagating data coverage + model uncertainty | Docstring: honest confidence surfacing — panel can ask "how sure are you?" and the system answers quantitatively |
| `services/atlas_data.py` | Global Solar/Wind Atlas values per municipality/province; Supabase→bundled-CSV fallback | Ground-truth atlas values anchor scores; CSV fallback keeps EcoSim alive without the table |

### A.3 Predictive analytics — ARIMA(1,1,1) (SO3, S10, S18)

| File | What it does | Decision rationale |
|---|---|---|
| `app/ml/predictor.py` | Model wrapper; `_sanitize_nan` for JSON-safe output | NaN/Inf → None so forecast JSON never 500s on edge data |
| `services/forecasting.py` | SARIMA(p,d,q)(P,D,Q,s) + ARIMAX fitting, walk-forward backtesting, model registry integration | Docstring; chosen model is ARIMA(1,1,1) per `ml/model_metrics_consumption.csv` (AIC grid in `ml/aic_grid.csv` documents order search) |
| `services/ml_worker_proxy.py` | Optional proxy: forwards heavy/RAG/long-running paths to a companion full-Docker worker when `ML_WORKER_URL` set | Docstring: Vercel's light serverless can't run heavy ML — split-worker design; SEC-07 notes the 503 leak finding |
| `routes/forecast.py` | `/forecast/run`, `/forecast/backtest`, `/forecast/models` | Validation of `metric` enum added post-audit (test_security_fixes covers 422s) |
| `python_scripts/prepare_national_energy_csv.py` (+ `.ipynb`) | Combines 6 DOE CSVs → clean `national_energy_annual` schema (stdlib only) | Docstring: "no pandas dependency" — reproducible on any machine |
| `tests/pilot_run/evaluate_models.py` | ARIMA vs Linear/Holt/RF validation script | Pilot evidence behind the model choice |

### A.4 AI Assistant & RAG layer (SO5, S10, S18)

| File | What it does | Decision rationale |
|---|---|---|
| `services/rag_pipeline.py` | **Dispatcher**: `RAG_BACKEND=pgvector` (Supabase vector, Vercel-compatible) or `faiss` (local sentence-transformers) | Docstring: two backends because FAISS can't run on Vercel serverless — deployment-shaped design |
| `services/rag_faiss.py` | Semantic chunking, rich metadata (renewable_type/category/product_type), cosine FAISS | "replaces ad-hoc text slicing" — quality upgrade |
| `services/rag_pgvector_store.py` | `rag_chunks` table + `match_rag_chunks` RPC (migration 0007) | Serverless-safe retrieval path |
| `services/rag_embeddings_client.py` | Embedding encode (384-d), Redis-cached, batch, OpenAI provider option | Cache embeddings — repeat queries are free |
| `services/rag_hybrid.py` | Semantic + BM25 keyword → reciprocal-rank fusion → optional cross-encoder rerank | Hybrid beats pure-vector on energy jargon queries *(docstring)* |
| `services/rag_knowledge_builder.py` | Aggregates scraped product listings + national stats + climate/terrain into knowledge chunks | Structured docs > raw rows for LLM grounding |
| `services/llm_client.py` | Unified client: `LLM_PROVIDER` (`gemini` default per docstring, **`groq` runtime default at line 28**), retry, timeout cap, Gemini→Groq emergency fallback | Free-tier constraints drive design; NOTE: paper §2.7.2.2.9 says "primary AI is Gemini 2.5 Flash" while runtime default is Groq — order flipped in practice (see 05 watchlist) |
| `services/groq_client.py` | Groq free-tier client (20 rpm / 200k tpm / 500k tpd limits documented) | Cost ceiling = free tier |
| `services/gemini_funcs.py` | Gemini analysis (`analyze_renewable_results`), lazy google-genai import so Vercel can omit it, hard-timeout + content-keyed cache (lines ~601–647) | Lazy import keeps serverless bundle small; timeout→fallback dict prevents hangs (TC-FR-02 verified 61 ms) |
| `services/rag_gemini_funcs.py` | RAG prompt construction w/ strong grounding rules, `analyze_with_rag` | Grounding prompts keep LLM honest |
| `services/llm_sanitizer.py` | Strips JSON wrappers, markdown fences, HTML, chain-of-thought, normalizes whitespace | LLM output is untrusted — never render raw (test file exists) |
| `routes/chat.py` | RAG chat endpoints (`POST /chat`, sessions) — **router commented out in `api.py`; dormant** (GAP-01) | Chat surface was descoped; AI lives in EcoSim/EnergyHub explanations |
| `python_scripts/prepare_rag_products.py`, `fastapi-backend/scripts/seed_rag_pgvector.py` | RAG corpus prep + pgvector seeding | Offline corpus build so runtime only retrieves |

### A.5 EcoSim what-if module (SO4, S13–15, S17)

| File | What it does | Decision rationale |
|---|---|---|
| `routes/ecosim.py` | `GET /ecosim/` dashboard, `/ai`, `/municipalities`, `/provinces`, `/barangays`, `POST /`; quota dep `get_ecosim_optional_user_or_quota`; `data_source` param (auto/atlas/era5); logs each run to `user_ecosim_logs` | Printed verbatim in thesis System Codes appendix — verify printed vs current (see A.13) |
| `services/ecosim.py` | Orchestrates: climate/atlas/era5/catchment inputs → solar/wind/hydro calcs → geothermal compute → plant proximity boosts → financials → explanations; two cache layers (`data_cache`, `redis_client` `_ECOSIM_TTL`) | The module's "brain"; imports show the full dependency fan-in |
| `services/financials.py` | NPV, IRR, LCOE, discounted + simple payback | Paper's "savings and payback" (S13) — investment metrics a household can read |
| `services/hydro_plants.py`, `wind_plants.py` | Wikipedia PH plant lists → proximity boost + generation-scale + hydro floor | Sep-3 recalibration (git `85fa46d7`): real plant proximity grounds scores in reality |
| `services/products.py` | Product/provider recommendations from `cleaned_products_master.csv` — a **generated artifact** (gitignored; produced by `clean_scraped_products.py`, not committed) | S14 "directory of renewable-energy providers" |
| `services/mcda_weights_service.py` + `confidence.py` | (see A.2) | — |
| `fastapi-backend/scripts/calibrate_*.py`, `diagnose_ecosim.py`, `regenerate_*.py`, `check_*.py` | Calibration/diagnostic/backfill tooling | How scores were tuned & verified pre-defense — the engineering-validation workflow |
| Frontend `pages/Ecosim.jsx` + `components/ecosim/{EcosimWizard,EcosimResults,EcosimBOM,ExplanationModal,ProviderRecommendations}.jsx` + `utils/ecosimAnalysis.js`, `ecosimPdf.js`, `matchProviders.js` | 5-step wizard → results cards + AI modals + PDF export + provider matching | UI reworked per expert feedback (megaplan-it-feedback: hidden province mode, bill guide, 5th step, modals) |

### A.6 EnergyHub module (SO1/SO3, S11–12)

| File | What it does |
|---|---|
| `routes/energyhub.py` | `/overview`, `/trends`, `/forecast`, `/map-data`, `/source-breakdown`, `/grid-breakdown`, `/model-comparison`, `/provincial-demand`, `/ai-insight`, `/map-explanation`, `/analyze-chart` (printed in appendix) |
| `services/energyhub.py` | National/provincial stats assembly + suitability cache |
| `services/map_service.py` | Suitability scores + centroids per renewable at any admin level; materialized views; PSGC joins |
| `services/geospatial_service.py` | `geospatial_metadata` centroid/area/elevation reads, Redis-cached |
| `services/climate_service.py` | Multi-resolution climate: barangay→municipality→province fallback hierarchy |
| `routes/map.py` | `/map/{type}` suitability map data, `/map/psgc/hierarchy`, `/map/coverage` |
| `routes/geospatial.py` | `/centroids` bulk+single, `/climate`, `/climate/hierarchy` fallback |
| Frontend `pages/EnergyHub.jsx`, `Dashboard.jsx` + `components/energyhub/{EnergyMap,EnergyOverview,EnergyTrends,EnergySources,ProvincialDemand,PlotlyChart,AiInsightPanel,ChartExplanation,MapExplanationCard}.jsx` | Dashboard + map UI; `Dashboard.jsx` hosts the searchable municipality picker + saved locations |

### A.7 Geothermal (reference-only per deck caveats)

| File | What it does | Decision note |
|---|---|---|
| `services/geothermal/features.py` | Physics-based suitability + output (IHFC heat flow, fault/volcano distances, NASA temp; flags estimated inputs) | Docstring: measured vs estimated inputs explicitly flagged — honesty about data quality |
| `services/geothermal/plants.py` | GEM geothermal-plant tracker → proximity boost | Real plant proximity |
| `services/geothermal/ml_classifier.py` | Optional RandomForest classifier + feature importance | Docstring: "Physics-based calculations remain primary; this is enhancement only" |
| `services/geothermal/{batch_compute,extract_kmz}.py` | Precompute + KMZ→JSON extraction to `local_data/` | One-time offline jobs so runtime needs no heavy GIS deps |
| `routes/geothermal.py` | `/geothermal/plants`, `/geothermal/{municipality_id}` | PGRST116→500 finding fixed post-audit (DEF-01) |

### A.8 Authentication & accounts (S16)

| File | What it does | Decision rationale |
|---|---|---|
| `react-frontend/src/context/AuthContext.jsx` | Supabase auth wrapper: signup (incl. anti-enumeration handling), login, Google OAuth, MFA, profile fetch | `PRODUCTION_AUTH_EMAIL.md` + recent commits document Gmail-SMTP + `/auth/callback` flow fixes |
| `react-frontend/src/pages/{Login,MFASetup,SecuritySettings,AuthCallback,ResetPassword,ProfilePage}.jsx` | Auth UX: sign-in/up, TOTP enrollment (QR + manual secret + app guidance), security prefs incl. EcoSim autosave toggle, OAuth/email landing | TOTP-only 2FA — Supabase Auth as configured supports TOTP; SMS/WhatsApp would need paid Twilio (megaplan-it-feedback A2) |
| `app/auth/jwt.py`, `app/dependencies/auth.py`, `app/dependencies/quota.py` | JWT verify + role/status deps (fail-closed), anonymous EcoSim quota (Redis TTL counter) | SEC-03 fix: user-status now fails closed; quota gives guests a taste without accounts |
| `app/services/supabase_service.py` | Supabase client (service-role), JWT pattern check | Service-role = backend-only; frontend never touches tables directly |
| `routes/protected.py` | `/protected/me`, `/protected/profile` (GET/PUT incl. `ecosim_autosave`) | `extra="forbid"` schema — new fields must be declared explicitly |
| Supabase GoTrue + migrations `0009`, `0012`–`0018`, `0023`–`0025` | Auth provider + RLS policies + profile/preferences | Managed auth over custom — thesis-level scope control |

### A.9 Saved simulations & locations (S17)

| File | What it does |
|---|---|
| `routes/simulations.py` | CRUD for `saved_simulations` (label sanitization strips `<>`; 404/422 mappings tested) |
| `react-frontend/src/services/savedLocations.js`, `pages/SavedSimulations.jsx`, Dashboard save/open/remove flows | Save, revisit, delete previous analyses; deep-link `?municipality=` + `?simulation_id=` |
| `supabase/migrations/0021_add_saved_simulation_mode.sql`, `0023_profiles_ecosim_autosave.sql` | Province-mode saves + default-ON autosave preference |
| `pages/Ecosim.jsx` autosave path | Auto-POST on run when `profile.ecosim_autosave` (IT-expert feedback item) |

### A.10 Named data sources → ingestion/ETL code

| Source named in paper/deck | Ingestion / prep code | Lands in |
|---|---|---|
| DOE data (national energy stats) | `python_scripts/prepare_national_energy_csv.py` (+ipynb), `scripts/migrate_csv_to_supabase.py` | `national_energy_annual` + forecast tables |
| NASA POWER climate | `python_scripts/ingest_nasa_power_monthly.py`, `scripts/run_nasa_for_gaps.py`, `ingest_municipality_climate_averages.py` | `municipality_climate_monthly/averages` |
| Climate data (analysis) | `python_scripts/municipality_climate_analysis.py` | analysis CSVs |
| Terrain / elevation | `python_scripts/elevation_etl.py`, `run_terrain_pipeline.py`, `terrain_pipeline/` | `geospatial_metadata`, hydro slope inputs |
| GIS boundaries / centroids | `scripts/extract_centroids.py`, `insert_geospatial_metadata.py`, `simplify-geojson.js`, `fill_missing_coords_from_geojson.py`, `geocode_missing_coords.py`, `get_geocode.py` | `geospatial_metadata` |
| Global Solar/Wind Atlas rasters | `scripts/extract_atlas_values.py`, `ingest_atlas_averages.py`, `build_province_atlas_averages.py`, `ingest_province_atlas_averages.py`, `update_municipality_suitability_from_atlas.py` | `municipality_atlas_averages`, `province_atlas_averages` |
| ERA5 wind | `scripts/extract_era5_wind.py`, `ingest_era5_averages.py`, `inspect_era5.py` | `*_era5_averages` |
| PSGC / PSA hierarchy | `scripts/sync_psgc_data.py` (authenticated PSA API), `scrape_philatlas.py`, `insert_missing_municipalities.py`, `insert_from_csvs.py`, `identify_gaps.py`, `debug_regions.py` | regions/provinces/municipalities/barangays |
| Boothroyd 2023 catchment geodatabase (hydro) | `services/build_catchment_enrichment.py`, `catchment_data.py`, `load_catchment_to_supabase.py`, `scripts/precompute_aquifer_scores.py`, migration `0022` | `municipality_catchment_enrichment` |
| IHFC heat flow + GEM geothermal tracker | `fastapi-backend/scripts/ingest_ihfc.py`, `ingest_geothermal_plants.py`, `prepare_aquifer_spatial.py`, `services/geothermal/*` | geothermal inputs + `local_data/` |
| Wikipedia wind/hydro plant lists | `fastapi-backend/scripts/ingest_wind_hydro_plants.py` → `services/{wind,hydro}_plants.py` | plant proximity boosts |
| Product/provider catalog | `python_scripts/clean_scraped_products.py`, `extract_product_kw.py`, `append_istabreeze_products.py`, `join_wind_data(_betz).py`, `prepare_rag_products.py` + `react-frontend/src/data/providers.json` (2026 DOE registry, 32 providers) | `cleaned_products_master.csv`, provider directory, RAG corpus |
| ECOSTRESS LST | `fastapi-backend/scripts/extract_ecostress_lst.py` | geothermal/thermal features |
| Volcano/fault KMZ overlays | `fastapi-backend/scripts/extract_kmz_to_geojson.py` | map raster overlays |
| External APIs at runtime | `services/atlas_data.py` (local), `geospatial_service.py`, `climate_service.py` — **NASA POWER NOT called at runtime** (perf doc §9: runtime data served from Supabase/bundled CSVs; NASA only in ETL) | — |
| ETL orchestration | `services/etl_orchestrator.py`, `routes/etl.py` (**disabled in api.py**), `data_cache.py`, `redis_client.py` | lineage `data_lineage` table |

### A.11 Frontend surfaces → features

| Surface | Files | Feature (deck ref) |
|---|---|---|
| Home/About/Privacy/Terms/NotFound | `pages/{Home,About,Privacy,Terms,NotFound}.jsx` | Static/landing (S1) |
| Dashboard | `pages/Dashboard.jsx` + `components/shared/SearchableSelect.jsx` | Municipality picker, composite score card, saved locations (S11/S16+) |
| EnergyHub | `pages/EnergyHub.jsx` + `components/energyhub/*` | National stats, trends, forecast, maps, AI insights (S11–12) |
| EcoSim | `pages/Ecosim.jsx` + `components/ecosim/*` | Wizard → results → AI → providers → PDF (S13–15) |
| SavedSimulations | `pages/SavedSimulations.jsx` | Saved runs CRUD (S17) |
| Auth | `pages/{Login,MFASetup,SecuritySettings,AuthCallback,ResetPassword,ProfilePage}.jsx` + `context/AuthContext.jsx` + `hooks/useAuth.js` | Email/password, Google, TOTP 2FA (S16) |
| AI chat (dormant) | `pages/ChatPage.jsx` (unrouted) | GAP-01 |
| Admin | `pages/admin/Admin{Dashboard,Users,Analytics,Config,Logs,Moderation,Usage}.jsx` + `components/admin/*` + `components/shared/AdminRoute.jsx` | Internal ops portal — NOT in the paper (Part C) |
| Shell/i18n | `layouts/MainLayout.jsx`, `components/layout/{Navbar,Footer}.jsx`, `context/ThemeContext.jsx`, `hooks/useTheme.js`, `i18n/*`, `components/shared/LanguageToggle.jsx` | App chrome, en/fil, theme |
| Primitives | `components/ui/*` (shadcn-style), `components/shared/*`, `ErrorBoundary.jsx`, `ErrorState.jsx` | Design system |
| Services | `services/{apiClient,energyhub,savedLocations,supabaseClient}.js` | API layer: 30 s timeout, 3 retries, exp. backoff, no-retry-on-429 (failure doc) |

### A.12 Evaluation instruments & results → where they live

| Paper element | Location |
|---|---|
| Household questionnaire (12 usability + 7 comparison items) | thesis §2.10.5 + appendix "Sample Questionnaire" (@3094) |
| IT expert ISO/IEC 25010 instrument | §2.10.6 + `tests/docs/iso25010_evaluation.md` + `docs/thesis/Chapter_3_Table_19_*` |
| Engineering validation form | §2.10.7 + appendix transcripts (@3121–3488) |
| System test plan (Table 2.15) | §2.7.3.1 + `tests/docs/testing_strategy.md`, `test_results_template.md` |
| Statistical treatment (α, t-test) | §2.11 + appendix "Statistical analyses output" (@3489) |
| Test results & artifacts | §3.3 + `docs/09-Technical-Evaluation/**` (see 04-TESTING-AUDIT) |

### A.13 Printed System Codes ↔ current code (drift check)

| Appendix listing (@3523–7752) | Current file | Drift status |
|---|---|---|
| `ecosim.py (FastAPI endpoints)` | `fastapi-backend/app/routes/ecosim.py` | Printed version shows `data_source` param + `get_ecosim_optional_user_or_quota` — recent features; verify printed ≈ current at defense (line-level diff recommended if panel asks) |
| `energyhub.py (FastAPI Endpoints)` | `fastapi-backend/app/routes/energyhub.py` | verify |
| `ecosim.py (Function Logic)` | `fastapi-backend/app/services/ecosim.py` | verify — file has grown (imports list 30+ services) |
| `energyhub.py (Function Logic)` | `fastapi-backend/app/services/energyhub.py` | verify |

*The other ~80 backend files exist in the repo but are NOT printed in the appendix — Part C.*

---

## PART B — Exhaustive file inventory

Scope: every code file in `fastapi-backend/`, `react-frontend/src/`, `python_scripts/`, `scripts/`,
`tests/`, `api/`, `supabase/migrations/`, plus root config. Excluded: `node_modules/`, `.venv/`,
`__pycache__/`, `dist/`, `.git/`, raw `data/` datasets (summarized by category in A.10), binary
assets, `expo-mobile/` (stub, future work), `video/` (production assets).

### B.1 `fastapi-backend/` application code

**Entry & config**

| File | Purpose | Notes / rationale |
|---|---|---|
| `main.py` | FastAPI app: sanitized global 500 handler, middleware stack (RequestID→RateLimit→SecurityHeaders→BodyLimit→CORS→Timing), router mount at `api_v1_prefix`, startup warm-up (Supabase/Redis clients, RAG index), docs gated on `settings.debug` | Comment block documents middleware-order reasoning (CORS outermost for headers on 429/413/5xx; Timing last-added=outermost for full-measurement) |
| `main.py` `@app.on_event` | startup hook | DeprecationWarning noted — lifespan handler is the modern replacement (low-risk cleanup) |
| `requirements.txt` / `requirements-vercel.txt` | Full vs slim dependency set | Vercel omits heavy ML/geo deps (lazy imports guard the seams, e.g. `gemini_funcs`) |
| `app/config/settings.py` | Pydantic settings (`load_dotenv(override=True)`), env contract | `override=True` noted in failure doc as why env-injection was unreliable |
| `app/auth/jwt.py` | JWT helpers | Local verify path optional (`get_verified_user_optional`) — security doc flags the caveat |
| `app/utils/network.py` | Client-IP helpers: trust only real socket peer/known platform headers; `x-vercel-forwarded-for` on Vercel | Written for SEC-01 fix — spoofed XFF can't bypass quota/rate-limit |
| `app/utils/postgrest.py` | PGRST116 → clean 404 mapping | Written for DEF-01/geothermal finding |
| `app/models/` | (package marker) | Pydantic models live under `schemas/` instead |
| `app/schemas/common.py` | Shared Literal/Enum boundary types (e.g. `EcoSimDataSource`) | Docstring: reject bad enum values at the boundary w/ standard 422 — validation-at-boundaries principle |
| `app/schemas/{ecosim,energyhub,geothermal,products,example}.py` | Request/response models per module | `PostHouse`, `EcosimQueryParams`, list/dashboard/AI responses |
| `app/middleware/request_id.py` | X-Request-ID + structured JSON logs | Every response/error carries a correlatable request_id |
| `app/middleware/rate_limit.py` | Sliding-window limiter: Redis (shared) w/ in-memory fallback | SEC-02: counters now merged post-fix (`TestRateLimitMergedCounters`) |
| `app/middleware/security.py` | Security headers + body size limit (1 MB → 413) | SEC-HDR/FR-10 verified |
| `app/middleware/timing.py` | Per-request duration logs | Observability first-pass (docstring) |
| `app/dependencies/auth.py` | `get_current_user`, `require_admin`, role/status checks | Fail-closed posture (SEC-03 fix) |
| `app/dependencies/quota.py` | Anonymous EcoSim quota (Redis TTL counter) | Guest access without account, per-IP |

**Routes** (all mounted under `/api/v1` via `routes/api.py`; `api.py` itself aggregates routers — chat/etl commented out)

| File | Endpoints / purpose |
|---|---|
| `routes/api.py` | Router registry + `/api/v1` mount; chat & etl routers **dormant** |
| `routes/health.py` | `/health` liveness, `/health/detailed` (supabase/redis/rag_index checks, degraded state) |
| `routes/energyhub.py` | EnergyHub API (see A.6) |
| `routes/ecosim.py` | EcoSim API (see A.5) |
| `routes/forecast.py` | `/forecast/run|backtest|models` |
| `routes/map.py` | suitability map data, PSGC hierarchy, coverage |
| `routes/geospatial.py` | centroids + climate (hierarchy fallback) |
| `routes/geothermal.py` | plants list + per-municipality geothermal |
| `routes/products.py` | product/provider recommendations |
| `routes/protected.py` | authenticated profile (`me`, `profile` GET/PUT) |
| `routes/simulations.py` | saved-simulations CRUD |
| `routes/admin.py` | admin portal: users list/create, usage+audit CSV export, moderation |
| `routes/chat.py` | RAG chat (dormant — router not mounted) |
| `routes/etl.py` | ETL run/lineage/validate (dormant — not mounted; SEC-08 flagged string interpolation) |
| `routes/example.py` | scaffold/example route — boilerplate |

**Services** (rationale in A-sections where applicable)

| File | Purpose |
|---|---|
| `atlas_data.py` | Solar/Wind Atlas values, Supabase→CSV fallback |
| `build_catchment_enrichment.py` | One-time builder: join municipality centroids to Boothroyd catchments + nearest order-1/2 streams |
| `catchment_data.py` | Runtime loader for catchment enrichment (Supabase→CSV fallback) |
| `climate_service.py` | Multi-resolution climate w/ barangay→municipality→province fallback |
| `confidence.py` | Data-quality→confidence propagation per energy type |
| `data_cache.py` | Redis wrapper w/ gzip+base64 (fits Upstash free-tier size limits) |
| `ecosim.py` | EcoSim orchestration (see A.5) |
| `energyhub.py` | EnergyHub data assembly + cache |
| `etl_orchestrator.py` | Pipeline runner: step tracking, retry, lineage logging, validation (schema/range/null/uniqueness), scraper hardening |
| `example_service.py` | scaffold example |
| `financials.py` | NPV/IRR/LCOE/payback (PHP, kWh) |
| `forecasting.py` | SARIMA/ARIMAX fit/forecast, walk-forward backtest, model registry |
| `gemini_funcs.py` | Gemini analysis, lazy import, timeout+cache |
| `geospatial_service.py` | `geospatial_metadata` reads, Redis-cached |
| `geothermal/__init__.py` | package marker |
| `geothermal/features.py` | geothermal physics (measured vs estimated flagged) |
| `geothermal/plants.py` | GEM plant list + proximity boost |
| `geothermal/ml_classifier.py` | optional RF classifier (physics stays primary) |
| `geothermal/batch_compute.py` | one-time suitability/output precompute |
| `geothermal/extract_kmz.py` | KMZ→lightweight JSON in `local_data/` |
| `groq_client.py` | Groq free-tier LLM client |
| `hydro_output_calc.py` | runoff coeff, design flow, hydro output (slope/literature-based) |
| `hydro_plants.py` | Wikipedia hydro plants + proximity boost/floor/scale |
| `llm_client.py` | unified provider client w/ Gemini→Groq fallback |
| `llm_sanitizer.py` | strip JSON/fences/HTML/CoT from LLM output |
| `load_catchment_to_supabase.py` | upload enrichment CSV → `municipality_catchment_enrichment` |
| `local_data/` | bundled CSV/JSON fallbacks (keeps app alive without DB) |
| `map_service.py` | map data + materialized views + PSGC joins |
| `mcda.py` | AHP consistency, weighted sum, PROMETHEE II |
| `mcda_weights_service.py` | weights loader w/ fallback defaults |
| `ml_worker_proxy.py` | optional heavy-work proxy for Vercel |
| `municipality_suitability_builder.py` | per-municipality suitability scores |
| `products.py` | product recommendation service (known data-quality notes) |
| `rag_embeddings_client.py` | embedding encode + cache |
| `rag_faiss.py` | semantic chunking + FAISS retrieval |
| `rag_gemini_funcs.py` | RAG prompt construction + `analyze_with_rag` |
| `rag_hybrid.py` | semantic+BM25 fusion + rerank |
| `rag_knowledge_builder.py` | structured knowledge docs from all sources |
| `rag_pgvector_store.py` | `rag_chunks`/`match_rag_chunks` store |
| `rag_pipeline.py` | backend dispatcher pgvector|faiss |
| `redis_client.py` | Redis client + `NullRedis` no-op fallback + ecosim cache helpers |
| `solar_output_calc.py` | NOCT temp factor, soiling/degradation, PR, output |
| `supabase_service.py` | Supabase client singleton + JWT pattern |
| `wind_output_calc.py` | wind averages, output calc, speed extrapolation |
| `wind_plants.py` | Wikipedia wind plants + proximity boost/scale |

**Tests** (`fastapi-backend/tests/` — covered exhaustively in `04-TESTING-AUDIT.md` §4.2)

**Ops scripts** (`fastapi-backend/scripts/`)

| File | Purpose |
|---|---|
| `audit_dataless_municipalities.py` | Report/optionally delete municipalities with no climate data (API already hides them) |
| `calibrate_all.py` | EcoSim API across ALL provinces+municipalities → CSV+report |
| `calibrate_municipalities.py` | municipality-mode scoring bias report (30+ municipalities) |
| `calibrate_renewables.py` | province-mode scoring bias report (25+ provinces) |
| `check_explanation_mismatches.py` | diff cached explanations vs latest calibration ground truth |
| `check_full_pipeline.py` | RAG+Groq+Gemini-fallback end-to-end smoke |
| `check_gemini_mock.py` | Gemini mock verification |
| `check_prompt_inspection.py` | inspect constructed prompts |
| `check_rag_normalize.py` | RAG normalization checks |
| `check_rag_pipeline.py` | RAG pipeline test script |
| `check_retrieval_only.py` | retrieval-only RAG check |
| `diagnose_ecosim.py` | call `build_ecosim_dashboard_response` per province, print first failure |
| `extract_ecostress_lst.py` | ECOSTRESS L2G LSTE surface-temp extraction |
| `extract_kmz_to_geojson.py` | volcano/fault KMZ overlays → frontend-ready JSON manifest |
| `ingest_geothermal_plants.py` | GEM geothermal plants ingestion |
| `ingest_ihfc.py` | IHFC heat-flow DB → PH-relevant CSV for IDW interpolation |
| `ingest_wind_hydro_plants.py` | scrape Wikipedia wind/hydro plant lists |
| `prepare_aquifer_spatial.py` | aquifer shapefile → WGS84 GeoJSON for point-in-polygon |
| `regenerate_explanations.py` | backfill stale `municipality_renewable_explanations` |
| `regenerate_province_fallbacks.py` | province atlas/ERA5 fallbacks from municipal means |
| `seed_rag_pgvector.py` | seed `rag_chunks` for pgvector backend |

### B.2 `react-frontend/src/` (every file)

| File | Purpose |
|---|---|
| `main.jsx`, `App.jsx` | app bootstrap + root component |
| `routes/AppRoutes.jsx` | route table (incl. admin; ChatPage not routed) |
| `layouts/MainLayout.jsx` | page shell |
| `styles/globals.css` | Tailwind 4 + theme tokens |
| `lib/utils.js` | `cn()` tailwind-merge helper |
| `context/AuthContext.jsx` | auth state/actions (see A.8) |
| `context/ThemeContext.jsx` | theme provider |
| `hooks/useAuth.js`, `useTheme.js` | context hooks |
| `services/apiClient.js` | fetch wrapper: 30 s timeout, 3 retries, exp. backoff, no-retry-429 |
| `services/supabaseClient.js` | Supabase JS client (anon key — publishable by design) |
| `services/energyhub.js` | EnergyHub endpoint helpers |
| `services/savedLocations.js` | saved-locations CRUD |
| `utils/env.js` | env access (hardcoded anon key per security doc — publishable-by-design) |
| `utils/ecosimAnalysis.js` | client-side EcoSim result shaping |
| `utils/ecosimPdf.js` | pdfmake results export (Sep-15 feature) |
| `utils/pdfFonts.js` | PDF font embedding |
| `utils/matchProviders.js` | provider matching vs `data/providers.json` |
| `utils/municipalities.js` | municipality helpers |
| `utils/glossary.js`, `regionMap.js`, `cssVarToHsl.js` | glossary terms, region mapping, CSS var→HSL for PDFs |
| `data/providers.json` | 2026 DOE registry — 32 verified providers (git `896843d9`) |
| `data/references.json` | source/reference list shown in UI (citations) |
| `i18n/index.jsx`, `en.json`, `fil.json` | i18n provider + locales (`{{var}}` interpolation; parity tested) |
| `test/setup.js` | vitest setup (jsdom/testing-library) |
| `pages/Home.jsx`, `About.jsx`, `Privacy.jsx`, `Terms.jsx`, `NotFound.jsx` | static/landing pages |
| `pages/Dashboard.jsx` | municipality dashboard + saved locations |
| `pages/EnergyHub.jsx` | EnergyHub dashboard |
| `pages/Ecosim.jsx` | EcoSim wizard host + results + autosave |
| `pages/SavedSimulations.jsx` | saved runs list |
| `pages/ChatPage.jsx` | chat UI — dormant/unrouted |
| `pages/Login.jsx`, `AuthCallback.jsx`, `ResetPassword.jsx` | auth entry + OAuth/email landing + reset |
| `pages/MFASetup.jsx`, `SecuritySettings.jsx`, `ProfilePage.jsx` | TOTP enroll, security prefs (autosave toggle), profile |
| `pages/admin/Admin{Dashboard,Users,Analytics,Config,Logs,Moderation,Usage}.jsx` | admin portal screens |
| `components/ErrorBoundary.jsx`, `ErrorState.jsx` | error UX |
| `components/admin/{CreateUserModal,UserDetailDrawer}.jsx` | admin widgets |
| `components/ecosim/{EcosimWizard,EcosimResults,EcosimBOM,ExplanationModal,ProviderRecommendations}.jsx` | EcoSim UI (wizard 5-step, results, bill-of-materials, explanation modals, providers) |
| `components/energyhub/{EnergyMap,EnergyOverview,EnergyTrends,EnergySources,ProvincialDemand,PlotlyChart,AiInsightPanel,ChartExplanation,MapExplanationCard}.jsx` | EnergyHub UI (Leaflet map, charts, AI cards) |
| `components/layout/{Navbar,Footer}.jsx` | chrome |
| `components/shared/{AdminRoute,ProtectedRoute}.jsx` | route guards |
| `components/shared/{CitationSources,ExpandableBlock,HelpTooltip,InfoTooltip,InsightCard,InterpretationBadge,LanguageToggle,Loading,LoadingSkeleton,Markdown,NextStepList,SearchableSelect,ThemeToggle}.jsx` | shared UI incl. explanation/citation components (SO5) |
| `components/ui/{badge,button,card,dialog,dropdown-menu,form,input,progress,sheet,skeleton,sonner,table,tabs,tooltip}.jsx` | shadcn-style primitives |
| `__tests__/{i18n-keys.test.js,I18nProvider.test.jsx,theme-contrast.test.js}`, `components/__tests__/*.test.jsx`, `utils/*.test.js` | vitest suites (see 04 §4.4) |

### B.3 `python_scripts/` (data-prep pipeline)

| File | Purpose |
|---|---|
| `ingest_nasa_power_monthly.py` | NASA POWER monthly climate → `municipality_climate_monthly` (env-tunable: `START_YEAR=2018`, `ONLY_MISSING`, `BATCH_SIZE=500`, rate-limit/retry knobs) |
| `elevation_etl.py` | Open-Meteo Elevation API → elevation enrichment |
| `run_terrain_pipeline.py` + `terrain_pipeline/` | terrain raster → slope/morphometry per municipality (drives hydro runoff) |
| `geocode_missing_coords.py`, `get_geocode.py` | Nominatim geocoding for missing lat/lon (≥1 s rate limit honored) |
| `fill_missing_coords_from_geojson.py` | GeoJSON centroids → fill DB coords (fuzzy name match) |
| `municipality_climate_analysis.py` | climate averages analysis → CSV |
| `prepare_national_energy_csv.py` (+ `.ipynb`) | DOE 6-CSV merge → `national_energy_annual` (stdlib-only) |
| `wind_power_coefficient.py` | Cp computation vs Betz 16/27 |
| `join_wind_data.py`, `join_wind_data_betz.py` | scraped wind-product joins + stats (Betz variants) |
| `clean_scraped_products.py` | normalize scraped listings (header synonyms etc.) |
| `extract_product_kw.py` | parse kW from product names → `kw` column |
| `append_istabreeze_products.py` | append Istabreeze catalog rows |
| `prepare_rag_products.py` | product data → RAG corpus |
| `municipality_climate_averages.csv` | bundled fallback CSV (not code — data) |
| `prepare_national_energy_data.ipynb` | notebook version of DOE prep |

### B.4 `scripts/` (top-level ops)

| File | Purpose |
|---|---|
| `extract_centroids.py` | GeoJSON → centroid+area CSVs (shapely, normalized-name matching) |
| `extract_atlas_values.py` | sample Solar/Wind Atlas rasters at centroids |
| `extract_era5_wind.py`, `inspect_era5.py` | ERA5 10 m wind extraction + GRIB inspect |
| `ingest_atlas_averages.py`, `ingest_province_atlas_averages.py`, `ingest_era5_averages.py`, `ingest_municipality_climate_averages.py` | upsert averages → Supabase |
| `build_province_atlas_averages.py` | province atlas values (aggregation + centroid sampling) |
| `update_municipality_suitability_from_atlas.py` | one-off map-score migration from atlas CSV |
| `scrape_philatlas.py` | PhilAtlas hierarchy scrape vs DB → gap CSVs |
| `sync_psgc_data.py` | authenticated PSA PSGC API → Supabase sync |
| `insert_missing_municipalities.py`, `insert_from_csvs.py` | insert gaps in FK order |
| `insert_geospatial_metadata.py` | centroid CSVs → `geospatial_metadata` |
| `identify_gaps.py` | missing-from-DB / null-scores / has-data CSVs |
| `migrate_csv_to_supabase.py` | bulk CSV/GeoJSON → Supabase migration |
| `run_nasa_for_gaps.py` | NASA POWER fetch for gap municipalities |
| `precompute_aquifer_scores.py` | aquifer scores → `geothermal_suitability` |
| `generate_erd.py` | matplotlib ERD PNG of schema |
| `verify_fixes.py` | v2.1 bug-fix verification (compile/import checks) |
| `check_cache.py`, `debug_regions.py`, `temp_db_check.py` | diagnostics |
| `test_api.py` | PSA API pagination probe |
| `simplify-geojson.js` | GeoJSON simplification (map payload size) |
| `psgc_cache/` | cached PSGC responses (not code) |

### B.5 `tests/` (root suite)

| File | Purpose |
|---|---|
| `pytest.ini`, `conftest.py` | pythonpath + markers (`mock`/`live`/`local`/`benchmark`) |
| `run_tests_and_save.py` | suite runner that persists reports |
| `tests/unit/*.py` (7 + conftest) | unit suite — 177 cases (04 §4.1) |
| `tests/integration/*.py` (4) | integration suite (04 §4.3) |
| `pilot_run/evaluate_models.py` | ARIMA/Linear/Holt/RF model validation → CSV+plots |
| `reports/test_results_report.md` | historical run report |
| `test_results/` | saved run outputs |
| `docs/*.md` | testing strategy, usability (SUS), ISO 25010 rubric, algorithms, metrics explainers, LLM eval methodology, ML eval framework, methodology report |
| `sql/` | test/support SQL |

### B.6 Deploy & root files

| File | Purpose |
|---|---|
| `api/index.py` | Vercel serverless entry (ASGI wrapper to `main:app`) |
| `api/requirements.txt` | serverless dep set |
| `vercel.json` | Vercel build/route config (backend `lumi-backend-ten.vercel.app`) |
| `docker-compose.yml`, `docker-compose.prod.yml` | containerized backend option |
| `deploy/` | deployment assets |
| `package.json` (root) | `npm run dev` → Vite + uvicorn concurrently |
| `pyproject.toml`, `requirements.txt`, `requirements-no-torch.txt` | Python deps (no-torch variant for slim installs) |
| `.env.example` | env contract (names only) |
| `README.md`, `DESIGN.md`, `PRODUCT.md` | project docs |
| `expo-mobile/` (2 files) | mobile stub — future work |

### B.7 `supabase/migrations/` (0001–0025, chronological)

| # | One-line purpose |
|---|---|
| 0001 | geospatial architecture (admin units, `geospatial_metadata`) |
| 0002 | PSGC data columns |
| 0003 | schema hardening (constraints/indexes) |
| 0004 | phase-1 improvements; keep legacy `suitability_*` columns for coexistence |
| 0005 | `forecast_model_runs` table (model registry) |
| 0006 | remaining forecasting-module tables |
| 0007 | pgvector extension + `rag_chunks`/`match_rag_chunks` |
| 0008 | data offload — local CSV/GeoJSON into Supabase |
| 0009 | **RLS hardening** (user-owned table policies) |
| 0010 | EcoSim climate (Supabase as source of truth) + AI cache |
| 0011 | optimized admin usage-summary RPC (Vercel-free-tier-friendly single call) |
| 0012 | `municipality_id` FKs on saved_* so frontend joins work |
| 0013 | `is_admin()` treats devs as admins |
| 0014 | admin users-list function |
| 0015 | `user_ecosim_logs` — per-request usage tracking (powers analytics) |
| 0016 | usage-report functions + role casting fix |
| 0017 | admin audit-log grants/indexes |
| 0018 | backfill `user_ecosim_logs` from `saved_simulations` |
| 0019 | cache per-municipality EcoSim explanations (no AI call just to render cards) |
| 0020 | clear old AI cache after prompt/token-limit changes |
| 0021 | `saved_simulations.province_id` + `mode` (province saves w/o municipality FK) |
| 0022 | `municipality_catchment_enrichment` (Boothroyd 2023 hydro data) |
| 0023 | `profiles.ecosim_autosave` default true |
| 0024 | pre-launch audit fixes (column-scope UPDATE privileges etc.) |
| 0025 | Supabase security-lint fixes |

*(PostgREST views/materialized views referenced by code — `regional_lookup`, `mv_province_map_data`, `mv_municipality_map_data` — live in `supabase/schema_structure/lumi_schema_latest.sql`.)*

---

## PART C — Bidirectional gap lists

### C.1 Code in the repo the paper never mentions (exists, but be ready if asked)

| Area | Files | Why it exists *(inferred unless cited)* |
|---|---|---|
| **Admin portal** | `routes/admin.py`, `pages/admin/*`, `components/admin/*`, migrations 0011–0018 | Internal ops: user management, usage analytics, audit logs, CSV export — built for the dev/admin side, not a defended feature |
| **ETL framework** | `routes/etl.py` (dormant), `services/etl_orchestrator.py` | Data-lineage/validation framework for pipelines — disabled at runtime (SEC-08 note) |
| **Ops/diagnostic scripts** | `fastapi-backend/scripts/check_*`, `diagnose_ecosim.py`, `regenerate_*.py`, `audit_dataless_municipalities.py`; `scripts/check_cache.py`, `debug_regions.py`, `temp_db_check.py`, `verify_fixes.py` | The calibration/QA toolchain behind score tuning and expert-validation rounds |
| **Dormant chatbot** | `routes/chat.py`, `pages/ChatPage.jsx` | Descoped AI surface (GAP-01) |
| **Example scaffolds** | `routes/example.py`, `services/example_service.py`, `schemas/example.py` | Template remnants |
| **Resilience internals** | `middleware/timing.py`, `ml_worker_proxy.py`, `utils/postgrest.py`, `utils/network.py` | Post-audit hardening layer (Sep-7→18) |
| **`.benchmarks/`** | performance snapshots | internal benchmarking |
| **`expo-mobile/`** | stub | future mobile app |

### C.2 Paper/deck claims with no directly locatable code (or weak mapping)

| Claim | Status |
|---|---|
| "AI Assistant" as a discrete user-facing module (S10 implies chat-like assistant) | **Partial** — code exists (`routes/chat.py`, `ChatPage.jsx`, RAG stack) but the chat surface is unmounted; live assistant = explanation endpoints. Frame carefully. |
| GitHub OAuth sign-in (functional-test doc lists TC-AUTH-002 GitHub) | `AuthContext`/Supabase supports providers, but **GitHub flow not evidenced in code** like Google's — `UNVERIFIED:` only Google OAuth is wired in `AuthContext.jsx`/`AuthCallback.jsx`. Say "Google + email + 2FA" per deck S16. |
| "Barangay-level" assessments | Barangay endpoints exist (`/ecosim/barangays`, `list_barangays`; climate fallback hierarchy reaches barangay) but **suitability scoring is municipality-level** — be precise: coverage is province/municipality per S7. |
| Wording "ML model" for the MCDM engine | The recommendation engine is **rule/weight-based MCDM**, not learned ML — if asked, distinguish ARIMA (learned) vs MCDM (expert weights) vs optional geothermal RF classifier. |
| Hardware sizing / BOM depth | `EcosimBOM.jsx` exists client-side; paper promises "estimated generation/savings" — hardware sizing is light (panel-friendly phrasing: preliminary sizing guidance). |
| Printed appendix code ↔ current | See A.13 — spot-verify the four listings match current files before defense (they show current param signatures, so likely regenerated near submission). |

---

*Every path above was verified to exist at audit time (2026-10-31). File purposes cite docstrings
or docs; `*(inferred)*` marks judgment calls. Report any path that 404s as a fix, not a mystery.*

---

## PART D — Core file logic breakdowns (~25 files)

> Function-by-function walkthrough of the files that carry thesis-defensible logic — the ones a
> panel would actually ask "how does this work?" about. Every remaining cited file gets the same
> treatment in `06a` (backend), `06b` (scripts/ETL), `06c` (frontend), `06d` (tests).
>
> **Formula ↔ paper map:** thesis §2.7.2.2.8's nine algorithm items resolve to —
> solar temp factor → `calculate_noct_cell_temp`/`calculate_temperature_factor_noct`;
> solar PR aggregation → `calculate_performance_ratio`;
> wind output → `calculate_wind_output`;
> runoff coefficient → `estimate_runoff_coefficient`;
> micro-hydro design flow → `estimated_flow_rate`;
> micro-hydro electrical output → `calculate_hydropower`;
> economic viability/recommendation scoring → `financials.*` + `_calculate_option_summary`;
> ARIMA → `forecasting.*` + `ml/predictor.EnergyHubML`;
> composite score → `mcda.aggregate_score` + `municipality_suitability_builder._compute_composite`.

### D.1 `fastapi-backend/main.py` — app assembly & request pipeline

- **Role:** ASGI entrypoint; builds the FastAPI app, middleware stack, router mount, startup warm-up.
- **Logic flow:** settings → logging setup → app init (docs gated on `debug`) → register global exception handler → add middleware (order matters, see below) → mount `api_router` at `api_v1_prefix` → startup hook.
- **Functions/blocks:**
  - `unhandled_exception_handler(request, exc)` — last-resort 500: logs exception with request_id/method/path/client_ip, returns sanitized `{detail, request_id}` + `X-Request-ID` header. Never leaks internals (L30-56).
  - Middleware adds (L62-91) — RequestID → RateLimit(60/min) → SecurityHeaders → BodySizeLimit → CORS → Timing. Comment block (L58-61): last-added = outermost; CORS must wrap 429/413/5xx responses; Timing is outermost to measure all layers including CORS.
  - CORS (L67-88) — `_VERCEL_PREVIEW_ORIGIN` regex scoped to `lumi-frontend-*-xi.vercel.app`; `_LOCALHOST_ORIGIN` added **only** when `ENVIRONMENT != production`.
  - `startup_event()` (L96-134) — logs config state (provider, key presence, quota — values never printed); pre-inits Supabase+Redis clients in threadpool; skips RAG build if `enable_rag` off or `RAG_BACKEND=pgvector`; else `ensure_index_built` in thread — failures warn, never crash.
  - `root()` — `GET /` → `{"status": "ok", "service": ...}`.
- **Tie:** the request lifecycle the security probes exercise; middleware order is a defended design decision.

### D.2 `fastapi-backend/app/routes/api.py` — router registry

- **Role:** single `api_router` that aggregates all feature routers; mounted at `/api/v1`.
- **Logic:** imports each router → `include_router` with prefix+tags. **Commented out:** `chat_router` ("heavy RAG chat not needed at launch") and `etl_router` ("long-running, not used by webapp") — the dormant-surface evidence. `example_router` also commented.
- **Mounts:** health, protected, ecosim, energyhub, geothermal, geospatial, simulations, admin, products, forecast, map.
- **Tie:** proof that `/api/v1/chat` and `/api/v1/etl` exist as code but are not routed — say "implemented but not currently mounted."

### D.3 `fastapi-backend/app/routes/ecosim.py` — EcoSim HTTP boundary (167 ln)

- **Role:** thin HTTP layer over `services/ecosim.py`; this is the file printed in the thesis appendix.
- **Functions:**
  - `_log_ecosim_request(user, municipality_id)` (L32) — fire-and-forget insert into `user_ecosim_logs` for authenticated runs; powers admin analytics (migration 0015).
  - `GET /` `get_ecosim_results` (L47) — query params (municipality_id, consumption, bill, rate, savings, mode, data_source) → `build_ecosim_dashboard_response`; dep `get_ecosim_optional_user_or_quota` gates anonymous use.
  - `GET /ai` `get_ecosim_ai` (L74) — same inputs → AI analysis path (cache-first).
  - `GET /municipalities|/provinces|/barangays` (L127-143) — picker lists from `list_*` service fns.
  - `POST /` `post_item` (L144) — 201; validated `PostHouse` schema → `renewable_energy_calculator`.
- **Tie:** quota-gated anonymous access + per-request logging + strict response models — the SO4 surface.

### D.4 `fastapi-backend/app/routes/energyhub.py` — EnergyHub HTTP boundary (253 ln)

- **Role:** thin layer over `EnergyHubService`/`energyhub` helpers; ~20 GET/POST endpoints.
- **Endpoint map:** `/overview`, `/forecast` (metric enum), `/trends`, `/map-data` (level+type), `/source-breakdown`, `/grid-breakdown`, `/model-comparison`, `/ai-insight` (cached LLM or static), `POST /analyze-chart` (chart JSON → insight, content-hash cache), `/map-explanation`, `/provincial-demand`, `/municipal-demand/{province_id}`, `/irena/*` (overview, capacity, generation, renewable-share), `/meralco-rate`, `/solar-atlas`.
- **Logic pattern:** each handler = parse params → call service → return typed response. `metric` params are Pydantic Literal enums → invalid values 422 at the boundary.
- **Tie:** SO1/SO3 surfaces; every number the dashboard shows flows through these.

### D.5 `fastapi-backend/app/services/ecosim.py` — EcoSim orchestrator (2,265 ln)

- **Role:** the module brain — fans in ~30 imports: climate/atlas/ERA5/catchment loaders, all three calc engines, plant-proximity boosters, geothermal, financials, caches.
- **Logic flow (dashboard path):** input validation → municipality/province fetch → consumption calc → per-source calcs w/ plant boosts → suitability scores → option summaries (payback/CO₂/sizing/score) → best-option pick → static explanations + optional AI → assemble response.
- **Key functions:**
  - `_load_climate_csv` (L69), `_get_climate_for_municipality(_ids)` (L80/119) — bundled-CSV fallback reads used when Supabase path misses.
  - `get_municipality_terrain_data` (L174), `get_municipality_data` (L200) — assemble per-municipality climate+terrain+atlas row; source=`auto|atlas|era5`.
  - `_get_climate_municipality_ids` (L293) — the coverage set powering "filter municipalities by data coverage."
  - `list_municipalities/provinces/barangays` (L331/395/438) — picker lists.
  - `_compute_municipality_wind_output_kwh` (L484) — per-month wind energy across climate rows.
  - `get_province_data` (L550) — province aggregation: mean of member municipalities' data.
  - `get_geothermal_data` (L754) — suitability+output w/ measured-vs-estimated flags.
  - `get_municipality_name_by_id`, `get_province_name_by_id` (L850/879) — lookups.
  - `consumption_calculator` (L908) — `monthly_kwh = bill / rate`; `daily = monthly / days`; `target = monthly × (1 − desired_savings)`.
  - `renewable_energy_calculator` (L933-1457) — the core. Steps: fetch data by mode → build **params_hash** (all inputs + ~30 settings incl. every household-scale constant + `scoring_version: "v5"`) → Redis full-result cache check (L963-1018) → consumption results → pick irradiance (`solar_ghi_kwh_m2_day` atlas preferred, else `avg_allsky_sfc_sw_dwn` NASA) → per-source outputs (solar `solar_calc_pvout`, wind w/ `extrapolate_wind_speed` to hub height, hydro w/ catchment enrichment + plant floors, geothermal compute) → option summaries → best pick → return dict (+cache store).
  - `_build_static_renewable_explanations` (L1458) — template text per source from result numbers (works with zero LLM).
  - `_get_or_build_explanations` (L1608) — Supabase `municipality_renewable_explanations` cache; **staleness = any source text differs from freshly generated** → regenerate+upsert. This is why cards render without an AI call (migration 0019).
  - `_calculate_option_summary` (L1657-1814) — the economic-scoring heart, docstring carries APA citations: **SPP** = cost / (monthly_savings×12) [Ngwakwe 2025]; **CO₂** = usable_kwh × 0.6835 kg/kWh [DOE 2019–2021 OMEF]; **system-kw proxy** = monthly_gen/30/4.0 peak-sun-hrs [Taduran & Piao 2025, NREL]; **weighted score** = `source_score × (0.4 + 0.6 × energy_ratio) × 100` — multiplicative so resource quality dominates and a weak source can't win on volume [Asadi 2023]. Source-specific cost bases (geothermal = utility MW-scale).
  - `build_ecosim_dashboard_response` (L1815-2265) — route-facing wrapper: validates consumption/bill >0 (422), derives rate if absent, **mismatch guard**: if entered kWh vs bill/rate differ >20%, prefer bill-derived kWh + set `input_warning` (L1836-1843); resolves name/lat/lon/province (404 if unknown); calls `renewable_energy_calculator`; attaches explanations, warnings, confidence.
- **Deps:** all `*_output_calc`, `financials`, `atlas_data`, `catchment_data`, `climate_service`, `geothermal/*`, `*_plants`, `mcda*`/`confidence` indirectly, `redis_client`, `data_cache`, `supabase_service`, `settings`.
- **Tie:** SO4; printed in appendix; the params_hash + `scoring_version` is the honest answer to "how do you invalidate cached results?" — bump a constant, cache keys change.

### D.6 `fastapi-backend/app/services/energyhub.py` — EnergyHub orchestrator (1,809 ln)

- **Role:** assembles everything EnergyHub shows: national stats (via `EnergyHubML`), suitability maps per admin level, AI insights/chart analysis, provincial+municipal demand, IRENA/MERALCO/atlas datasets.
- **Key members:**
  - `_classify_score(value)` (L60) — score→label bands for map legend.
  - `_load_volcanoes` (L74), `_get_geojson_province_names` (L156) — local geodata fallbacks.
  - `EnergyHubService.__init__` (L203) — lazy-loads datasets + caches.
  - `build_overview` (L208) — national snapshot payload for `/overview`.
  - `get_forecast` (L236) — delegates to ML predictor (precomputed ARIMA outputs).
  - `build_trends` (L241) — historical series payload.
  - `build_map_data` → `_build_map_data` (L260-274) → per-level builders: `_build_renewable_potential_map` (province), `_build_municipality_potential_map`, `_build_barangay_potential_map`, `_build_geothermal_potential_map`, `_build_province_metric_map` — each reads suitability columns + centroids and emits GeoJSON-ready items.
  - `_apply_geothermal_boost` (L806), `_aggregate_factors` (L775) — boost/aggregate helpers.
  - `get_ai_insight` (L967) — static insight by default; LLM only when `use_llm`.
  - `get_map_explanation` (L982) + `_static_map_explanation` (L1036) + `_summarize_map_data` (L1051) + `_map_data_sources` (L1148) — summarize top/bottom items, then static or LLM-rendered explanation with source citations.
  - `_lookup_item_lat_lon`, `_nearest_geo_feature` (L1186/1199) — nearest volcano/plant for context.
  - `analyze_chart` (L1226) — chart JSON → `_hash_chart_data` (content hash) → `_get_cached_insight`/`_cache_insight` (Supabase AI-cache) → `_generate_llm_insight`/`_build_chart_prompt` (typed prompts per chart) → `_clean_llm_text`.
  - `get_provincial_consumption` (L1576), `estimate_municipal_demand` (L1585) — provincial demand allocation down to municipalities (population-weighted).
  - IRENA/MERALCO/atlas delegates (L1773-1788) + `build_irena_overview`.
  - `get_energyhub_service()` (L1805) — module singleton.
- **Tie:** SO1/SO3; shows the static-first/LLM-optional pattern everywhere (AI is an enhancement layer, not a dependency).

### D.7 `fastapi-backend/app/services/solar_output_calc.py` — solar engine (348 ln)

- **Role:** §2.7.2.2.8 "solar temperature factor" + "solar performance ratio aggregation" — household PV output physics.
- **Functions:**
  - `calculate_noct_cell_temp` (L15) — `T_cell = T_amb + (NOCT−20)×(G/800)/(1+wind_factor)`, IEC 61853 / King et al. 2004; NOCT default 45 °C.
  - `calculate_temperature_factor_noct` (L45) — derate `1 + temp_coeff×(T_cell−25)`, coeff −0.004/°C, floored at 0.
  - `calculate_temperature_factor` (L70) — legacy linear variant kept for compat.
  - `calculate_soiling_loss` (L79) — env-driven soiling ratio: dry+windy accumulation (`PRECTOTCORR<10` grows dust w/ wind & days-since-cleaning), rain cleaning (`>50mm`), high-humidity penalty (`RH>80`); clamped 0.80–1.0.
  - `calculate_dust_loss_from_wind`, `calculate_degradation_from_humidity` — legacy simple variants.
  - `calculate_air_density_correction` (L129) — `ρ_ratio = (P/101325)×(288.15/T_K)` → ±2% clamped.
  - `calculate_performance_ratio` (L149) — product of system_efficiency(0.80) × temp × (soiling or dust) × inverter(0.96) × mismatch(0.98) × wiring(0.98) × degradation(0.99) [× air density] — the paper's PR aggregation list.
  - `solar_calc` (L175) — legacy flat formula `kWp×GHI×PR`; score = min(GHI/6,1)×100.
  - `solar_calc_advanced` (L195) — full path: kWp → **POA transposition** — Hay-Davies-style when DNI+DHI present (`dhi×(1+cosβ)/2 + dni×aoi + ghi×albedo-term`, floor 0.9×GHI) else latitude tilt-gain on GHI → NOCT temp factor → soiling → air density → PR → daily/monthly kWh + full `loss_breakdown` + `transposition_source` tag (honesty about which model ran).
  - `solar_calc_pvout` (L312) — preferred path when Global Solar Atlas PVOUT exists: `kWp × PVOUT/365`, **no double PR** (PVOUT already embeds losses — docstring states this explicitly); score vs 1,800 kWh/kWp excellent-baseline.
- **Tie:** SO4 solar math; PVOUT-vs-NOCT duality = "we use atlas yields when available, physics fallback otherwise."

### D.8 `fastapi-backend/app/services/wind_output_calc.py` — wind engine (254 ln)

- **Role:** §2.7.2.2.8 "wind power output" — household-scale power curve.
- **Functions:**
  - `_compute_wind_averages` (L24) / `load_wind_averages` (L56) — compute+cache household product averages (rotor radius, Cp) from scraped product CSV.
  - `extrapolate_wind_speed` (L107) — power law `V(h)=V_ref×(h/h_ref)^α`, **α=0.143 (1/7 law)** per NREL PH atlas which used 30 m reference — converts 10 m NASA wind to hub height.
  - `calculate_wind_output` (L127) — steps: fill power-curve params from `settings` (household_wind_*), fill rotor/cp from product averages → **validate**: rotor>0, air density ∈[0.9,1.3], **Cp ≤ 0.593 Betz limit** (raises w/ citation), CF∈[0,1] → swept area πr² → raw cubic `P=½ρAV³Cp·η` → 3-region curve: <cut-in or ≥cut-out → 0; ≥rated → rated cap; else min(raw, rated) → energy = kW × 24h × CF × days.
  - Defaults read from `get_settings()` inside the function — calibration constants live in env config, not code.
- **Tie:** the Betz guard is a great "we engineered for honesty" story — the model refuses nonphysical inputs.

### D.9 `fastapi-backend/app/services/hydro_output_calc.py` — hydro engine (240 ln)

- **Role:** §2.7.2.2.8 runoff coefficient + design flow + electrical output (run-of-river micro-hydro).
- **Functions:**
  - `normalize` (L6) — 0-1 clamp helper (returns 0 on degenerate range).
  - `estimate_runoff_coefficient` (L14) — slope bands (Javadinejad 2022): <3°→0.30, <10°→0.45, <20°→0.60, else 0.75; None→0.45.
  - `estimated_flow_rate` (L35) — rational-method-inspired `Q_design = (C × P_monthly × A) / seconds_month × design_factor × gravity_flow`: catchment km²→m², mm→m; `runoff_coefficient_override` (from Boothroyd enrichment) **bypasses** slope path to avoid double-counting terrain; else slope C moderated by runoff_potential & watershed_gradient. Design factor default 0.40 = environmental-flow reserve; gravity floor 0.1; output clamped [0.001, 0.5] m³/s — **`apply_flow_floor=False` lets genuinely dry sites return 0** instead of a fake floor (enrichment path).
  - `estimate_discharge` (L120) — plain `Q=(P×A×C)/seconds_month` variant using current month's real day count.
  - `calculate_hydropower` (L146) — `P_elec = η_turb × η_gen × ρ g Q H`: flow clamped ≤0.5 m³/s; head handling — `head_already_realistic` (stream-gradient×penstock) just clamps 0-25 m, else DEM head × `head_factor` (0.20) with 2-25 m band; hydraulic kW = ρgQH/1000; η = 0.75×0.90; optional `feasibility_penalty` (stream-distance, 0-1) scales energy; `hydro_score = normalize(monthly,0,100)×100` — 100 kWh/month = excellent-site baseline (docstring explains the conservative PH choice vs Feyissa's 500-2000).
- **Tie:** the "why was hydro weakest (60% agreement)?" answer lives here — estimates depend on catchment proxies; enrichment (Boothroyd 2023) was added to close the gap.

### D.10 `fastapi-backend/app/services/financials.py` — investment metrics (273 ln)

- **Role:** §2.7.2.2.8 "economic viability" — NPV/IRR/LCOE/payback in PHP/kWh.
- **Members:**
  - `FinancialInputs` / `FinancialResults` (L16/31) — dataclasses bounding the calc contract.
  - `calculate_npv` (L45) — `Σ CF_t/(1+r)^t`.
  - `calculate_irr` (L64) — **Newton-Raphson**: iterate `rate -= NPV/dNPV`, tol 1e-6, bail if dNPV≈0 or rate≤−1 → None.
  - `calculate_lcoe` (L100) — `PV(costs)/PV(energy)`; energy degrades `(1−d)^(t−1)` yearly; O&M discounted flat; `inf` on zero energy.
  - `calculate_payback` (L137) — simple = cost/annual_savings; discounted walks years w/ degrading savings, **interpolates the crossing year fraction** (`prev_cumulative/discounted_savings`); None when savings ≤0.
  - `analyze_financials` (L179) — orchestrates all four + aggregates; `to_dict` (L260) — JSON shape.
- **Tie:** "savings and payback" on S13 — metrics a household (and a panel) understands.

### D.11 `fastapi-backend/app/services/mcda.py` — MCDM engine (213 ln)

- **Role:** SO2 + §2.7.2.2.8 "recommendation scoring" — AHP validation, weighted sum, PROMETHEE II.
- **Functions:**
  - `ahp_consistency_ratio` (L16) — eigenvector-approx priority vector → `λ_max` → `CI=(λ−n)/(n−1)` → Saaty RI table (n=1-10) → `CR=CI/RI`, `is_consistent = CR<0.10`. This is how expert weight matrices get *validated*, not just used.
  - `aggregate_score` (L63) — weighted sum: weights from `get_weights(energy_type)` (DB w/ fallback) or equal-split if empty → normalize to Σ1 → per-criterion contributions → clamp 0-100 → classification bands (≥81 Very High … <21 Very Low). Returns `weights_used` + `contributions` — **fully auditable output** (each criterion's contribution is exposed).
  - `promethee_ii` (L126) — outranking: per-criterion type-5 linear preference w/ threshold q (default 10% of range) → pairwise π matrix → positive/negative flows → net flow → rank. Cross-check for weighted-sum rankings.
- **Tie:** the "is your engine a black box?" answer — every score decomposes into weights×contributions.

### D.12 `fastapi-backend/app/services/mcda_weights_service.py` — weights loader (113 ln)

- **Role:** supplies criterion weights to `mcda.aggregate_score`.
- **Functions:**
  - `load_mcda_weights(client)` (L49) — query `mcda_weights` table → reshape per energy_type → module-level cache; **hardcoded default fallback** when table missing/empty (docstring: "scoring pipeline never breaks").
  - `get_weights(energy_type, client)` (L95) — cached accessor per type.
  - `invalidate_weights_cache()` (L109) — bump after admin weight edits.
- **Tie:** weights are *data*, not code — engineers can revise them without a deploy; fallback keeps scoring alive.

### D.13 `fastapi-backend/app/services/confidence.py` — confidence scoring (177 ln)

- **Role:** the honesty layer — propagates data quality into a 0-100 confidence per recommendation.
- **Members:**
  - `ConfidenceFactors` (L20) — dataclass: has_climate, variables_count, data_year, terrain, population, tariff, user_inputs, energy_type.
  - `_score_data_coverage` (L32) — climate 0.3 + variables frac×0.3 + terrain 0.15 + population 0.1 + tariff 0.1 + inputs 0.05.
  - `_score_data_recency` (L56) — unknown→0.3; ≤2y→1.0, ≤5y→0.8, ≤10y→0.6, older→0.4 (anchor year 2025).
  - `_score_model_maturity` (L72) — solar 0.85 / wind 0.70 / hydro 0.65 / geothermal 0.40 — the code literally encodes "geothermal is reference-grade."
  - `_score_spatial_resolution` (L83) — flat 0.55 (NASA POWER ~50 km grid; comment admits coarseness).
  - `calculate_confidence` (L90) — weighted blend `.35 coverage + .15 recency + .30 maturity + .20 resolution` → label bands (≥75 High, ≥55 Moderate, ≥35 Low) → factor breakdown + recommendations list.
  - `_generate_recommendations` (L144) — actionable fixes ("fetch NASA POWER", "add DEM terrain", "consult PHIVOLCS/DOE" for geothermal).
- **Tie:** "how sure is the system?" — answered quantitatively, and geothermal's 0.40 explains why it stays reference-only.

### D.14 `fastapi-backend/app/services/municipality_suitability_builder.py` — score factory (484 ln)

- **Role:** computes/persists per-municipality suitability (solar/wind/hydro/geothermal + composite) — the dataset behind map choropleths and the 82.22% validation.
- **Key members:**
  - `_CLASSIFICATION_THRESHOLDS` (L32) + `get_classification` — score→band.
  - `_estimate_solar_from_lat`, `_estimate_wind_from_lat` (L54/64) — latitude-based fallback estimates when measurements missing.
  - `_compute_solar_score` (L69), `_compute_wind_score` (L79), `_compute_hydro_score` (L87), `_compute_geothermal_score` (L97) — per-source score assembly returning (score, evidence-dict).
  - `_compute_composite` (L113) — composite = aggregation across available sources (the map "potential" number).
  - `_fetch_all_municipalities/_fetch_climate_data/_fetch_hydro_data/_fetch_geothermal_data` (L126-226) — batched Supabase reads.
  - `build_suitability_for_municipality` (L227) — one municipality end-to-end.
  - `persist_batch` (L297), `invalidate_suitability_cache`, `warm_suitability_cache` (L306/318) — upsert + cache warming.
  - `build_all_municipality_suitability` (L387) — full rebuild loop (batch_size=200); `refresh_municipality_suitability` (L428) — targeted re-score; `main` (L466) — CLI entry.
- **Tie:** the scoring pipeline experts validated; batch+warming = map stays fast.

### D.15 `fastapi-backend/app/services/forecasting.py` — SARIMA pipeline (602 ln)

- **Role:** §2.7.2.2.8 "ARIMA forecasting" — fit, forecast w/ CI, backtest, registry logging, cache.
- **Members:**
  - `FORECAST_CACHE_TTL_SECONDS=86400` (L31), `_forecast_cache_key` (L34) — 24 h cache for stable historical forecasts.
  - `SARIMAConfig`/`BacktestResult`/`ForecastResult` (L45/53/65) — dataclasses: order, seasonal_order, trend; actuals/preds/metrics/residuals.
  - `_safe_float` (L77) — NaN/Inf→None for JSON safety.
  - `fit_sarima` (L88) — statsmodels SARIMAX(order, seasonal_order, trend; enforce_stationarity/invertibility=False).
  - `fit_arimax` (L117) — same w/ exogenous regressors.
  - `forecast_sarima` (L144) — `get_forecast(steps)` → mean + `conf_int(alpha)` → sanitized lists.
  - `backtest_walk_forward` (L176) — train [0:cut], predict 1 step, append actual, refit, repeat → metrics + residuals + train/test period labels; per-step failure → naive fallback + warn.
  - `calculate_metrics` (L250) — MAE, RMSE, **MAPE w/ zero-guard**, sMAPE.
  - `run_forecast_pipeline` (L275) — end-to-end: select target col → fit → forecast → metrics vs holdout.
  - `reconcile_forecast_cache` (L348) — cache integrity refresh.
  - `_classify_model_type`/`log_model_run` (L431/445) — writes `forecast_model_runs` (migration 0005) — **every forecast is versioned**.
  - `select_best_sarima_config` (L510) — AIC-style config selection; `run_forecast_pipeline_cached` (L548) — cache-first wrapper.
- **Tie:** SO3; the honest answer to "how did you pick (1,1,1)?" — config search + walk-forward backtest metrics (5.67% MAPE), not a guess.

### D.16 `fastapi-backend/app/ml/predictor.py` — precomputed-forecast provider (508 ln)

- **Role:** serves DOE historicals + **pre-computed** ARIMA forecast tables — class docstring: "No model retraining occurs at runtime."
- **Members:**
  - `_sanitize_nan` (L18) — JSON-safe numbers.
  - `_load_csv_from_supabase` (L40) / `_load_csv` (L68) — Supabase-first, local `data/DOE_Data_Extracted` fallback; `_prefer_v2` picks `data_v2_preprocessed/` over legacy `data_v1/`.
  - `EnergyHubML.__init__`/`_load_all` (L96/115) — eager-loads ~15 frames: master_preprocessed, forecast_consumption/peak/renewable_2025_2030, model_comparison×4, provincial_consumption_2003_2025, regional_sales_2025, IRENA capacity/generation/renewable-share, meralco_rates_2011_2020, solar_atlas_ph.
  - Public getters: `get_latest_statistics`, `get_historical_trends`, `get_forecast(metric)`, `get_model_comparison(metric)`, `get_source_breakdown(year)`, `get_grid_breakdown(year)`, `get_ai_insight`, `get_provincial_consumption`, `get_regional_sales`, `get_irena_*`, `get_meralco_rate`, `get_solar_atlas` — each slices the preloaded frame, returns dicts/lists.
  - `get_energyhub_ml()` — singleton accessor.
- **Tie:** clarifies the ML story — runtime serves *validated, versioned* forecast artifacts (from `python_scripts`/`tests/pilot_run` + `forecasting.py` pipelines); forecasting module can refit, but the served numbers are the frozen, evaluated ones. This is why the API stays ~104 ms.

### D.17 `fastapi-backend/app/services/llm_client.py` — provider switchboard (122 ln)

- **Role:** single entry `generate_response` used by all callers; provider via `LLM_PROVIDER` (**runtime default `groq`**, L28).
- **Logic:**
  - `generate_response` (L31) — inner `_attempt()`: provider `groq` → `generate_groq_response`; else `generate_gemini_response`, and **on total Gemini failure, emergency Groq fallback if `GROQ_API_KEY` present** (L77-90). Optional `timeout` wraps the whole attempt in a `ThreadPoolExecutor`; on `FutureTimeoutError` returns `""` so callers degrade gracefully (L92-103). Output passed through `clean_ai_output` unless `clean=False`.
  - `parse_json_response` (L108) — `json.loads`, else regex-extracts `{...}` block, else `{}`.
- **Tie:** W2 watchlist — paper says Gemini primary; runtime default is Groq, but the *architecture* is provider-agnostic with fallback both ways of deployment history.

### D.18 `fastapi-backend/app/services/gemini_funcs.py` — Gemini + EcoSim AI path (696 ln)

- **Role:** Gemini client layer + `analyze_renewable_results` — the EcoSim AI pipeline.
- **Key members:**
  - `_import_genai`/`_import_genai_errors` (L15/26) — **lazy import** so Vercel can ship without `google-genai`.
  - Env-tuned constants (L38-65): model `gemini-2.5-flash`, temp 0.3, `FALLBACK_GEMINI_MODELS` cascade, `_AI_CACHE_TTL=7d`, `_AI_CACHE_VERSION=v3`, `_AI_CALL_TIMEOUT=4s` (outer), `_AI_LLM_TIMEOUT=60s` (worker), retries=1.
  - `_municipality_id_from_payload`, `_backend_recommendation_from_payload` — payload helpers.
  - `_compute_ai_cache_key`/`_get_cached_ai_analysis`/`_set_cached_ai_analysis` (L111/127/174) — content-keyed Supabase AI cache.
  - `_strip_geothermal_for_province` (L203) — removes geothermal text in province mode (reference-only discipline in code).
  - `_build_renewable_analysis_result` (L214) — prompt → LLM → parse → normalize.
  - `_get_gemini_client`/`_generate_once`/`generate_gemini_response` (L256/270/334) — client lazy-init; per-model attempt; cascade over FALLBACK models w/ `SIMPLE_VOCABULARY_INSTRUCTION` system prompt (plain-English-for-homeowners persona, L318).
  - `_extract_json_block`, `parse_gemini_json_response`, `_extract_summary`, `_normalize_analysis_output` — output hardening.
  - `_build_renewable_analysis_prompt` (L514) — structured prompt w/ grounding rules.
  - `analyze_renewable_results` (L606) — **the served path**: cache-key → return cached (skip stale timeout/pending placeholders) → `in_flight` lock prevents duplicate workers → ThreadPoolExecutor worker runs `_build_renewable_analysis_result` → **4 s outer timeout → returns `pending`** while worker continues → success cached 7 d; failure cached 5 min as `failed`. This is why the UI polls and why ~1.9 s fallback ≠ ~7.1 s live.
  - `analyze_renewable_results_async` (L694) — async wrapper.
- **Tie:** the pending/cache/in-flight design is the direct answer to "why does the AI take ~7 s and how do you keep the UI snappy?"

### D.19 `fastapi-backend/app/services/groq_client.py` — Groq client (131 ln)

- **Role:** Groq free-tier client — runtime-default provider.
- **Members:**
  - `_get_groq_client` (L41) — lazy singleton; raises clearly on missing key/package.
  - `generate_groq_response` (L56) — `models_to_try = requested + FALLBACK_GROQ_MODELS` (`qwen/qwen3.8-27b` default per Sept-2026 re-verification, commit `0dca0be`); per model × retries w/ **exponential backoff `sleep(2**attempt)`**; skip empties w/ warning; raise last error if all fail. System prompt (L92-105) is the plain-language homeowner persona: jargon→simple words, numbers→comparisons, always tie to wallet.
- **Tie:** persona prompt is *why* explanations read at household level — cite L92-105 if asked "how do you make AI output accessible?"

### D.20 `fastapi-backend/app/services/rag_pipeline.py` — retrieval dispatcher (131 ln)

- **Role:** uniform retrieval API over two backends: `pgvector` (Supabase, serverless) or `faiss` (local).
- **Functions:**
  - `_rag_faiss` (L17) — lazy module import (keeps FAISS deps out of Vercel).
  - `DEFAULT_EMBEDDING_MODEL = all-MiniLM-L6-v2` (L25).
  - `_rag_backend` (L34) — `RAG_BACKEND` env, default pgvector.
  - `build_faiss_index`/`load_faiss_index`/`ensure_index_built` (L38/46/59) — local index lifecycle (built in startup threadpool).
  - `retrieve_context` (L68) — query → backend-specific retrieval → ranked chunks.
  - `retrieve_with_filter` (L92) — metadata-filtered retrieval (renewable_type, category, product_type).
  - `index_stats`/`sample_chunks` (L122/128) — diagnostics.
- **Tie:** D7 — deployment-shaped design, same interface either backend.

### D.21 `fastapi-backend/app/services/rag_hybrid.py` — hybrid retrieval + chat safety (498 ln)

- **Role:** semantic+keyword fusion, rerank, citation verification, input/output guards, chat persistence.
- **Functions:**
  - `_tokenize`/`_bm25_scores` (L28/33) — keyword leg.
  - `_reciprocal_rank_fusion` (L90) — `RRF(d) = Σ 1/(k + rank_i(d))` merging semantic+BM25 lists.
  - `hybrid_search` (L139) — run both retrievers → RRF → dedup → top-k.
  - `rerank_results` (L209) — optional cross-encoder rerank.
  - `verify_citations` (L269) — checks cited chunks actually back the answer — the anti-hallucination leg.
  - `validate_input` (L361) — reject over-length queries + off-topic keywords (`_OFF_TOPIC_KEYWORDS`, L352); `_MAX_CHAT_HISTORY=20`.
  - `sanitize_output` (L384) — post-processes model text.
  - `save_chat_message`/`get_chat_history`/`create_chat_session` (L403/447/475) — Supabase persistence for the **dormant** chat surface.
- **Tie:** quality+guardrails: retrieval fuses two strategies *and* verifies citations — answer for "how do you ground the LLM?"

### D.22 `fastapi-backend/app/services/llm_sanitizer.py` — output firewall (236 ln)

- **Role:** strips everything an LLM shouldn't emit before text reaches UI or downstream parsers.
- **Functions:** `strip_thinking_blocks` (<think>/reasoning), `decode_html_entities`, `strip_html_tags`, `strip_markdown_fences`, `strip_json_wrappers`, `strip_key_value_formatting`, `normalize_whitespace`, `_extract_text` (nested dict/list → str), `sanitize_llm_output` (full pipeline), `extract_prescriptive_recommendation` (label→text mapping for recommendation cards), `_truncate_to_complete_sentence`, `clean_ai_output` (composed entry used by `llm_client`).
- **Tie:** "LLM output is untrusted input" — the sanitization boundary behind the 4.70/5 clarity rating's safety.

### D.23 `fastapi-backend/app/dependencies/auth.py` — authN/Z deps (307 ln)

- **Role:** FastAPI dependency layer for identity, verification, roles, plans.
- **Functions:**
  - `get_bearer_token`/`get_optional_bearer_token` (L16/26) — header extraction.
  - `_extract_user_data`, `_build_user_claims`, `_build_user_claims_from_jwt` (L37/47/65) — normalize Supabase/JWT payloads.
  - `_get_local_user` (L75) — local `verify_jwt` fast path for read-only paths.
  - `get_current_user` (L91) — `auth.get_user(token)` → claims (401 on any failure).
  - `get_verified_user` (L103) — the strict path: **token-claims cache** (sha256 key, 60 s TTL — comment explains why: Supabase ES256 can't use the HS256 local fast path, so cache verified claims instead) → else `auth.get_user` → **email-confirmed required (403)** → claims cached (JSON-safe fields only) → `_get_user_status` active check (403 "Account suspended") → `is_active=True`.
  - `get_verified_user_optional` (L151) — same rules, returns `None` instead of raising — powers optional-auth endpoints (quota deps).
  - `_get_user_role` (L193) — service_role read of `user_roles`, Redis-cached 300 s; **on DB failure returns `"user"`** — fail-safe *downgrade* (comment: safe, but admins get denied during outages).
  - `_get_user_status` (L223) — `profiles.is_active`, Redis-cached; post-SEC-03 **fail-closed**.
  - `get_current_user_with_role`, `_get_effective_plan`, `get_current_user_with_role_and_plan`, `require_admin` (L257-307) — role/plan enrichment; admin/`dev` gate.
- **Tie:** S16's backend half + SEC-03 fix evidence (status check now fails closed; role failure degrades privilege).

### D.24 `fastapi-backend/app/dependencies/quota.py` — anonymous quota + usage limits (207 ln)

- **Role:** lets guests try EcoSim/EnergyHub without an account, then requires login; enforces per-plan monthly limits for users.
- **Functions:**
  - `_reset_redis_key` (L21) — atomic get→delete→setex window reset.
  - `check_and_increment_quota` (L38) — settings-driven (`anonymous_ecosim_quota`, window); Redis path, falls back to memory on failure.
  - `_check_and_incr_redis` (L54) — `ecosim:anon:{id}` TTL counter: get → (reset if missing/unparseable) → deny at quota → setex incremented.
  - `_check_and_incr_memory` (L84) — per-process dicts; window-since-last resets count.
  - `check_anonymous_quota` (L101) — public alias.
  - `check_authenticated_usage` (L110) — if `enforce_usage_limits`: admins/devs bypass; plan→limit map (`free/premium_simulation_limit`, `chat_message_limit`); read `user_usage_limits`; 429 at cap.
  - `get_optional_user_or_quota` (L150) — the EcoSim/EnergyHub gate: verified user → usage check → dict; **localhost exemption via `_direct_peer_ip` only** (never spoofed headers, L171-172); else anonymous quota → 401 "Please log in to continue using {feature_name}".
  - `get_ecosim_optional_user_or_quota`/`get_energyhub_optional_user_or_quota` (L194/202) — flavored wrappers.
- **Tie:** D13 — accessibility-without-accounts decision + SEC-01-era IP trust rules.

### D.25 `fastapi-backend/app/middleware/rate_limit.py` — sliding-window limiter (119 ln)

- **Role:** per-IP sliding-window rate limit shared across workers via Redis.
- **Logic:**
  - `_is_allowed_memory` (L39) — timestamp-list sliding window per IP.
  - `_is_allowed_redis` (L50) — Redis sorted-set window: `zremrangebyscore` (evict old) → `zcard` (count) → `zadd` (record) → `expire`; **always also updates the memory counter** so flapping Redis can't split counts (SEC-02 fix, comment L51-55); Redis error → memory path.
  - `dispatch` (L85) — skip OPTIONS + `/health`; **localhost exemption checks `_direct_peer_ip`** — the direct socket peer, immune to spoofed XFF; tighter 10/min limit for non-GET admin/protected (auth-sensitive actions); over-limit → 429 JSON w/ `Retry-After`.
- **Tie:** the rate-limit correctness story (merged counters, real-peer identity) — direct SEC-02/SEC-01 evidence.

---

*Part D covers the ~25 core files. All remaining cited files → `06a` (backend), `06b` (ETL/scripts), `06c` (frontend), `06d` (tests).*
