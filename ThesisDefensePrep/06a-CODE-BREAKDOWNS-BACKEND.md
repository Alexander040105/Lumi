# 06a — Code Breakdowns: Backend (remaining files)

> Function-by-function logic walkthrough for every `fastapi-backend/` file **not** already
> covered in `02` Part D (core files). Same template everywhere: role → logic flow →
> functions/classes → tie. Line refs spot-verified at `main @ 438789c`.
>
> **TOC:** [Routes](#routes) · [Services](#services) · [Geothermal package](#geothermal-package) ·
> [Schemas](#schemas) · [Middleware](#middleware) · [Auth/config/utils](#authconfigutils) ·
> [Serverless entry](#serverless-entry)

---

## Routes

### `app/routes/admin.py` (786 ln) — internal ops portal API
- **Role:** admin-only surface: user management, usage/audit exports, moderation. Requires `require_admin`.
- **Logic:** all handlers = `require_admin` dep → service-role Supabase ops → `_log_admin_action` audit insert.
- **Functions:**
  - `_log_admin_action(admin_id, action, target_user_id, details)` (L36) — writes `admin_audit_log`.
  - `_rows_to_csv`/`_csv_response` (L53/62) — export serializers (usage + audit CSV endpoints, commit `eb97b68`).
  - `_has_auth_admin_api`/`_auth_user_to_dict` (L70/75) — GoTrue admin-API interop + user dict shaping.
  - `GET /users` `list_users` (L104) — paginated user list via `get_admin_users_list` RPC (migration 0014; single-call, serverless-friendly).
  - `POST /users` `create_user` (L157) — admin-created accounts.
  - `GET /users/{id}` `get_user_detail` (L238); `POST /users/{id}/ban` (L277); `PUT .../role` (L302); `PUT .../profile` (L364); `POST .../force-password-reset` (L392); `GET .../simulations` (L442); `GET .../reports` (L463); `DELETE /users/{id}` `soft_delete_user` (L480) — moderation lifecycle, all audit-logged.
- **Tie:** not a defended feature (Part C gap in `02`) — exists for operating the deployment.

### `app/routes/chat.py` (232 ln) — dormant RAG chat API
- **Role:** full chat surface that exists but is **unmounted** (`api.py` comment: "heavy RAG chat not needed at launch").
- **Functions:**
  - `_build_chat_prompt(query, chunks, user_context)` (L24) — retrieved chunks + persona → grounded prompt.
  - `_retrieve_context(query, top_k)` (L57) — calls `rag_pipeline.retrieve_context`.
  - `_generate_response(prompt)` (L74) — `llm_client.generate_response`.
  - `POST /` `chat_message` (L106) — validate → retrieve → generate → persist session; `GET /sessions` (L184), `GET /sessions/{id}` (L204) — history.
- **Tie:** W8 — "implemented, not routed." Demo it in code if asked, never claim it's live.

### `app/routes/etl.py` (129 ln) — dormant ETL triggers
- **Role:** HTTP triggers for ETL pipelines — also unmounted ("long-running, not used by webapp").
- **Endpoints:** `POST /run/climate` (L44) → `build_climate_etl_pipeline().run()`; `GET /lineage` (L74) → `get_lineage_history`; `GET /validate` (L88) → `validate_dataframe` on a table (SEC-08: table-name allowlist applies).
- **Tie:** ETL exists as governed framework; it runs via scripts, not HTTP, in production.

### `app/routes/example.py` (18 ln) — scaffold
- **Role:** leftover CRUD example route; unmounted. No logic of consequence.

### `app/routes/forecast.py` (156 ln) — forecasting API
- **Endpoints:** `GET /run` (L47) → `run_forecast_pipeline_cached`; `GET /backtest` (L92) → `backtest_walk_forward`; `GET /models` (L137) → `forecast_model_runs` history.
- **Access:** `_require_forecast_access` (L31) — verified users only; `metric` is a Literal enum (invalid → 422; added post-audit).
- **Tie:** SO3's HTTP surface; runs are logged to the registry so forecasts stay versioned.

### `app/routes/geospatial.py` (228 ln) — centroids & climate API
- **Endpoints:** `GET /centroids` (bulk, L92), `GET /centroids/{level}/{geo_id}` (L107), `GET /climate` (L157), `GET /climate/hierarchy` (L183 — **barangay→municipality→province fallback chain**), `GET /climate/province-aggregate` (L211).
- **Tie:** the multi-resolution story — a barangay without data inherits its municipality's climate.

### `app/routes/geothermal.py` (266 ln) — geothermal API
- **Endpoints:** `GET /plants` (L20) → GEM plant list; `GET /{municipality_id}` (L27) → suitability+output analysis (PGRST116→404 via `postgrest` util — DEF-01 fix); `GET /ecosim/geothermal` (L139) → sim params; `GET /ecohub/geothermal-summary` (L187) → dashboard rows.
- **Tie:** geothermal is served as *reference* data — consistent with deck scope.

### `app/routes/health.py` (58 ln) — liveness/readiness
- **Endpoints:** `GET /health` (+ `/`) (L15-17) → `{status:"ok"}`; `GET /detailed` (L22) → per-dependency checks (supabase/redis/rag_index) → `ok`/`degraded`.
- **Tie:** demo-day readiness check — hit `/detailed` before presenting.

### `app/routes/map.py` (92 ln) — suitability map API
- **Functions:** `_normalize_level` (L24) → enum coercion; `GET /psgc/hierarchy` (L35); `GET /coverage` (L57) → data-coverage summary; `GET /{renewable_type}` `get_suitability_map` (L71) → `map_service.get_map_data`.
- **Tie:** SO1's map data feed.

### `app/routes/products.py` (62 ln) — product catalog API
- **Endpoints:** `GET /recommend` (L19) → `get_product_recommendations` (energy type + budget); `GET /browse` (L33); `GET /audit` (L55) → data-quality report.
- **Tie:** S14 provider directory backend.

### `app/routes/protected.py` (158 ln) — account API
- **Endpoints:** `GET /me` (L46, role+plan enriched); `GET /profile` (L51); `PUT /profile` (L75 — `ProfileUpdatePayload` incl. `ecosim_autosave`, `extra="forbid"`); `POST /sync-avatar` (L93); `POST /session` (L129 — Redis session store, TTL); `DELETE /me` `delete_account` (L145).
- **Tie:** account surface behind `get_verified_user`; profile update path that carries the autosave preference.

### `app/routes/simulations.py` (251 ln) — saved-simulation CRUD
- **Functions:** `_sanitize_label` (L17 — strips `<>`); `POST ""` create (L48, 201); `GET ""` list (L81); `GET /{id}` (L109); `PATCH /{id}` (L154 — label+payload update); `DELETE /{id}` (L208, 204).
- **Tie:** S17 backend; RLS isolates rows to the owner.

## Services

### `app/services/atlas_data.py` (252 ln) — Global Solar/Wind Atlas values
- **Logic:** Supabase `municipality_atlas_averages`/`province_atlas_averages` → bundled CSV fallback.
- **Functions:** `_load_csv`/`_df_row_to_dict` (local fallback); `get_atlas_for_municipality` (L36), `get_atlas_for_municipality_ids` (batch, L63); `_load_province_csv` (L89), `get_province_atlas`/`get_atlas_for_province` (L97/124); `_mean_rows` (L160 — province = mean of member municipalities); `_load_muni_era5_csv`/`_load_province_era5_csv`, `get_era5_for_municipality/province` (L189-252) — ERA5 wind variants.
- **Tie:** atlas-vs-NASA source choice (`data_source=auto|atlas|era5` in EcoSim).

### `app/services/build_catchment_enrichment.py` (379 ln) — Boothroyd enrichment builder
- **Role:** offline job: join municipality centroids → Boothroyd 2023 catchments + nearest streams → enrichment CSV.
- **Functions:** `load_catchments`/`load_streams`/`load_municipalities` (GeoDataFrame reads); `spatial_join_catchments` (L109 — point-in-polygon); `spatial_join_streams` (L188 — nearest order-1/2 stream + distance); `compute_derived_fields` (L218 — drainage density, hypsometric integral, runoff coefficient override); `build_output_csv` (L309); `main` (L345).
- **Tie:** migration 0022's data producer — the dataset that fixed weak hydro scoring.

### `app/services/catchment_data.py` (121 ln) — enrichment runtime loader
- **Functions:** `_load_csv`/`_df_row_to_dict`; `get_catchment_for_municipality` (L48 — Supabase→CSV fallback); `get_catchment_for_municipality_ids` (L81 — batch).
- **Tie:** feeds `runoff_coefficient_override` + `feasibility_penalty` + stream-distance head into `hydro_output_calc`.

### `app/services/climate_service.py` (313 ln) — multi-resolution climate
- **Functions:** `determine_resolution` (L31 — pick finest level w/ data); `get_climate_data` (L68); `get_climate_with_fallback` (L119 — barangay→municipality→province); `_aggregate_municipality_climate` (L167); `get_or_compute_province_climate` (L211 — mean of members, cached); `get_barangay_climate_or_fallback` (L286).
- **Tie:** coverage-vs-granularity tradeoff — the API never 404s on a sparse barangay, it falls back up the hierarchy.

### `app/services/data_cache.py` (136 ln) — Redis cache wrapper
- **Logic:** `_serialize` (L24 — JSON → **gzip → base64**, keeps payloads under Upstash free-tier size limits); `_deserialize` reverses.
- **Functions:** async `cache_get/set/delete/delete_pattern` (L56-85); sync twins `cache_get_sync/set_sync/delete_sync/delete_pattern_sync` (L100-129) for non-async service code.
- **Tie:** the gzip+base64 line is the concrete answer to "how do you fit results in free-tier Redis?"

### `app/services/etl_orchestrator.py` (505 ln) — governed ETL framework
- **Members:** `log_lineage`/`get_lineage_history` (L25/74 — `data_lineage` audit table); `ValidationResult` + `validate_dataframe` (L101/110 — schema/range/null/uniqueness checks); `get_random_user_agent`, `fetch_with_retry` (L227/233 — polite, retrying HTTP); `ETLStep`/`ETLStepResult`/`ETLOrchestrator` (L300-336 — step registry, sequential run w/ per-step timing+lineage); `build_climate_etl_pipeline` (L445 — gaps→fetch NASA→validate→upsert steps).
- **Tie:** data isn't hand-loaded — every ingestion is logged and validated. Runs via scripts/CLI; HTTP route dormant.

### `app/services/example_service.py` (15 ln) — scaffold stub.

### `app/services/geospatial_service.py` (184 ln) — `geospatial_metadata` reads
- **Functions:** `get_geospatial_metadata` (L34); `get_centroid` (L74); `get_all_centroids` (L87 — Redis-cached per level); `get_centroid_fallback` (L147 — compute from GeoJSON when row missing); `get_centroid_with_fallback` (L179 — DB → GeoJSON → None).
- **Tie:** every map pin/lookup funnels through here.

### `app/services/hydro_plants.py` (241 ln) + `wind_plants.py` (202 ln) — real-plant proximity
- **Same shape:** `_haversine` (km distance); `_load_plants` (bundled Wikipedia-derived list); `get_all_*`/`get_operating_*`/`get_*_near(lat,lon,radius_km)`/`get_*_in_province`; `calculate_*_proximity_boost` (nearby real plants → score bonus); `calculate_*_generation_scale` (plant size → output scaling). Hydro adds `calculate_hydro_plant_floor` (L208 — province-floor logic so known-hydro provinces aren't zeroed).
- **Tie:** Sept-3 recalibration (git `85fa46d7`) — scores grounded in where real plants actually operate; defensible response to "your scores are just climate math."

### `app/services/load_catchment_to_supabase.py` (95 ln) — enrichment uploader
- `main` — read enrichment CSV → chunked upsert → `municipality_catchment_enrichment`.

### `app/services/map_service.py` (594 ln) — map data engine
- **Functions:** `validate_wgs84` (L63); `_format_score` (L97); `_aggregate_to_province` (L106); `_fetch_municipality_scores` (L154); `get_map_data` (L245 — level+type dispatcher); `_fetch_from_materialized_view` (L285 — `mv_province_map_data`/`mv_municipality_map_data` fast path); `_fetch_from_table_join` (L336 — fallback path); `get_psgc_hierarchy` (L428); `get_coverage_summary` (L537).
- **Tie:** materialized views = the map stays interactive; table-join fallback = it stays correct if the view lags.

### `app/services/ml_worker_proxy.py` (100 ln) — heavy-work offloader
- **Members:** `_proxy_prefixes` (paths to forward); `MLWorkerProxyMiddleware.dispatch` — if `ML_WORKER_URL` set and path matches → forward request to the Docker worker, else `call_next`. SEC-07 documented the 503 leak behavior.
- **Tie:** how heavy RAG/ML could run while the serverless backend stays light — optional, not required.

### `app/services/products.py` (231 ln) — product recommendations
- **Functions:** `_load_products` (L34 — `cleaned_products_master.csv`, generated artifact); `_fix_category` (L72 — heuristic category repair for bad rows); `_row_to_dict`/`_clean` (NaN-safe rows); `get_product_recommendations` (L114 — filter by type + `in_php` budget guard, top-N); `browse_products` (L165 — paginated); `get_product_data_audit` (L203 — quality report feeding the honest "data has issues" caveat).
- **Tie:** S14; the audit endpoint exists *because* product data quality is knowingly imperfect.

### `app/services/rag_embeddings_client.py` (227 ln) — embedding encoder
- **Functions:** `_cache_key`/`_get_cached_embedding`/`_save_cached_embedding` (Redis-cached vectors); `_format_embeddings` (normalize provider output); `_embed_with_huggingface`/`_embed_with_openai`/`_embed_with_sentence_transformers` (three providers — HF inference API, OpenAI, local ST); `_embed_batch` (chunked); `encode` (public, L180); `encode_query` (L222).
- **Tie:** embeddings cached → repeat RAG queries skip the embedding call entirely.

### `app/services/rag_faiss.py` (525 ln) — local FAISS backend
- **Functions:** `_index_is_stale` (L42); `_get_embedder` (L62 — lazy ST model); `_sentences`/`_semantic_chunks`/`_clean_text`/`_chunk_documents` (L81-149 — semantic chunking w/ rich metadata: renewable_type, category, product_type); `build_faiss_index`/`load_faiss_index`/`ensure_index_built` (L174-265); `_rag_cache_key`/`_query_tokens`/`_keyword_score`/`_hybrid_score`/`_rerank_results` (L301-360 — local hybrid scoring); `retrieve_context`/`retrieve_with_filter` (L383/456); `index_stats`/`sample_chunks` (L512/521).
- **Tie:** the local-dev retrieval twin of pgvector — same interface.

### `app/services/rag_gemini_funcs.py` (226 ln) — RAG prompt + analysis
- **Functions:** `_build_rag_prompt` (L17 — strong grounding rules: answer only from chunks, cite sources); `_normalize_rag_output` (L74); `_smart_retrieve` (L130 — query-aware retrieval strategy); `analyze_with_rag` (L178 — retrieve → prompt → LLM → normalized answer).
- **Tie:** how EcoSim/Hub AI stays grounded in project data instead of general knowledge.

### `app/services/rag_knowledge_builder.py` (1,211 ln) — corpus factory
- **Role:** turns all datasets into structured knowledge chunks for RAG.
- **Functions (grouped):** `_enrich_sources`, `_normalize`, `classify_renewable`, `classify_product_type`, `to_php`, `_currency_note` (taxonomy + currency normalization); `load_and_fix_csv`, `_price_range_text`; **knowledge builders:** equipment/installation/maintenance costs, components, capacity, comparisons, pricing assumptions, raw product chunks, `build_national_energy_knowledge` (DOE stats), `_load_municipality_names` + municipality climate, terrain, geothermal, hydropower suitability builders; `_extract_pdf_text`/`_chunk_text`/`build_thesis_paper_knowledge` (ingests reference papers incl. the thesis itself).
- **Tie:** the breadth of the corpus is the answer to "what does the AI know?" — products, national stats, per-municipality climate/terrain/geo/hydro, and papers.

### `app/services/rag_pgvector_store.py` (144 ln) — Supabase vector store
- **Functions:** `_vector_literal`; `_row_to_result`; `_count_rows`; `ensure_index_built` (no-op true for pgvector); `index_stats`; `_retrieve` (calls `match_rag_chunks` RPC w/ embedding + threshold); `retrieve_context`/`retrieve_with_filter`; `sample_chunks`.
- **Tie:** migration 0007's runtime twin — cosine match via Postgres function.

### `app/services/redis_client.py` (390 ln) — Redis access layer
- **Members:** `NullRedis`/`NullRedisSync` (no-op stand-ins — app never crashes without Redis); `_redis_url`; `get_redis`/`get_redis_sync` (lazy clients); `is_redis_available`; **domain caches:** `_cache_key` + `get/set/invalidate_suitability_cache` (async + `_sync` twins); `_climate_cache_key` + climate cache fns; `_ECOSIM_TTL` + `get/set_ecosim_cache_sync` (params-hash keyed full-result cache used by `renewable_energy_calculator`).
- **Tie:** the three cache tiers in `03` §7; `NullRedis` is the graceful-degradation backbone.

### `app/services/supabase_service.py` (145 ln) — Supabase client
- **Members:** `_is_jwt_key` (detect key format); `_reset_supabase_client`; `SupabaseResponse`/`SupabaseRestQuery`/`SupabaseRestClient` (L33-107 — **minimal PostgREST client**: select/eq/limit/offset/single/execute — lets scripts talk to Supabase without the full SDK); `get_supabase_client` (service-role singleton); `get_supabase_public_client` (anon-key client for `auth.get_user`).
- **Tie:** service-role stays server-side; the hand-rolled REST client exists so thin environments (CI/scripts) don't need the SDK.

### `app/services/wind_plants.py` — see `hydro_plants.py` entry (same shape, wind list).

## Geothermal package

### `geothermal/__init__.py` (27 ln) — package docstring + shared constants.

### `geothermal/features.py` (707 ln) — geothermal physics
- **Functions:** `_haversine`, `_normalize`; `_load_local_geothermal_datasets`/`load_geothermal_datasets` (IHFC, aquifer, faults, volcanoes — local JSON/CSV); `query_aquifer_by_location`/`query_aquifer_by_municipality` (point-in-polygon aquifer class); `calculate_fault_distance`/`calculate_fault_density`/`calculate_volcano_distance`; **`idw_heat_flow`** (L305 — inverse-distance-weighted interpolation of IHFC points); `calculate_heatflow_score`; `calculate_aquifer_score`; `calculate_geothermal_gradient`; `calculate_reservoir_temperature`; `estimate_flow_rate`; `compute_geothermal_suitability` (L473 — weighted blend of heat-flow, fault proximity/density, volcano distance, aquifer; **flags measured vs estimated inputs**); `compute_geothermal_output` (L623).
- **Tie:** physically grounded but data-sparse — exactly why it's reference-only (confidence maturity 0.40).

### `geothermal/plants.py` (144 ln) — GEM plant proximity
- `_haversine`; `_load_plants`; `get_all_ph_geothermal_plants`; `get_operating_plants`; `get_plants_near`; `calculate_proximity_boost` — same real-world grounding trick as wind/hydro plants.

### `geothermal/ml_classifier.py` (132 ln) — optional RF classifier
- `fetch_training_data` (features+labels); `train_model` (RandomForest + feature importance); `main`. Docstring: **enhancement only — physics stays primary.** If asked "any learned model besides ARIMA?" → this + pilot baselines.

### `geothermal/batch_compute.py` (173 ln) — precompute job
- `fetch_municipalities`; `fetch_all_climate`; `batch_upsert` (chunked 100); `main` — computes suitability+output for all municipalities → `geothermal_suitability` table so runtime does no GIS math.

### `geothermal/extract_kmz.py` (261 ln) — KMZ→JSON extraction
- `_parse_kmz_coords`; `_haversine`; `extract_faults`/`extract_volcanoes`/`extract_heatflow`; `_write_philippine_*`; `main` — one-time conversion to `local_data/` so runtime needs no geopandas/KMZ parsing.

## Schemas

All `app/schemas/*.py` are Pydantic `BaseModel` contracts — validation happens at the HTTP boundary (D1 principle).

- `common.py` (42 ln) — shared Literal/Enum types (`EcoSimDataSource` etc.); docstring: reject bad enum values at the boundary → standard 422.
- `ecosim.py` (209 ln) — `PostHouse` (POST body), `EcosimQueryParams`, response models per endpoint: `EcosimResponse`, `EcosimDashboardResponse` (nested `ConsumptionResults`, `SolarOutput`, `WindOutput`, `HydroOutput`, `GeothermalOutput`, `RenewableEnergyResults`, `EcosimOption`, `EcosimComparison`), `EcosimAIResponse`, `Municipality/Province/Barangay List` + `Option` models, `HouseList`.
- `energyhub.py` (195 ln) — `AnalyzeChartRequest/Response`, `MapExplanationResponse`, `LatestStatistics/HistoricalTrends/Forecast/ModelComparison/SourceBreakdown/GridBreakdown/AiInsight/Overview/MapData/Trends/ProvincialDemand/MunicipalDemand` responses + item models, `Irena*` models, `MeralcoRate`, `SolarAtlas*`.
- `geothermal.py` (49 ln) — `GeothermalSuitability/Output/Analysis` responses, `GeothermalSimulationParams`, `GeothermalDashboardSummary`.
- `products.py` (45 ln) — `ProductItem`, `ProductRecommendationRequest/Response`, `ProductBrowseResponse`, `ProductAuditResponse`.
- `example.py` (16 ln) — scaffold models.

## Middleware

### `middleware/request_id.py` (150 ln) — request identity + logging
- `RequestIDMiddleware.dispatch` (L26) — assign/echo `X-Request-ID`, stash on `request.state`.
- `DefaultRequestFilter` (L52) — injects request_id into log records.
- `SafeJSONFormatter` (L76) — structured JSON logs.
- `setup_logging` (L111) — root logger config.

### `middleware/security.py` (72 ln) — headers + body cap
- `SecurityHeadersMiddleware.dispatch` — sets CSP/HSTS/X-Content-Type-Options/Referrer-Policy etc. on every response (SEC-HDR evidence).
- `BodySizeLimitMiddleware.dispatch` — rejects >1 MB bodies with 413 (FR-10 verified).

### `middleware/timing.py` (48 ln) — duration logging
- `TimingMiddleware.dispatch` — wall-clock around `call_next`, logs per-request duration; outermost middleware so it measures everything (observability first-pass).

## Auth/config/utils

### `app/auth/jwt.py` (17 ln) — local JWT verify
- `verify_jwt(token)` — HS256 local decode for the read-only fast path in `get_verified_user_optional`; returns claims or None. (Supabase ES256 tokens take the remote path — see D23 comment.)

### `app/config/settings.py` (244 ln) — env contract
- `Settings(BaseSettings)` — every env var declared w/ defaults: app/api prefix, Supabase, Redis, CORS (`parse_cors_origins`/`parse_cors_origin_regex` validators), LLM providers, quota/limits, **household-scale constants** (`household_solar_size_kwp`, `household_wind_*`, `household_hydro_*`, plant-boost knobs, `catchment_enrichment_*`) — the same constants hashed into EcoSim cache keys.
- `get_settings()` — cached accessor; `load_dotenv(override=True)` so `.env` wins over shell.
- **Tie:** calibration lives in config, not code — tuning scoring constants never requires a code change (and cache-invalidates cleanly).

### `app/utils/network.py` (53 ln) — client-IP trust
- `_direct_peer_ip` — socket peer; `_is_localhost`; `_is_trusted_proxy_platform` (Vercel env check); `get_client_id` — **real peer or `x-vercel-forwarded-for` on Vercel only**; never trusts arbitrary `X-Forwarded-For`. SEC-01 fix.

### `app/utils/postgrest.py` (46 ln) — PGRST116 mapping
- `is_pgrst116_not_found` — detect PostgREST "0 rows" error; `raise_for_pgrst116_or_404` — map to clean 404; `data_or_none_for_pgrst116` — None instead of 500. DEF-01 fix.

## Serverless entry

### `api/index.py` (67 ln) — Vercel ASGI wrapper
- `_PathFix` middleware — normalizes the `/api` path prefix Vercel strips/adds so `main:app` sees consistent routes; exposes the FastAPI app as the serverless handler.
- **Tie:** how the same FastAPI app runs both as `uvicorn main:app` locally and a Vercel function.
