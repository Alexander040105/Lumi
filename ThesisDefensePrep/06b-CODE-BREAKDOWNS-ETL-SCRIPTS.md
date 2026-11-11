# 06b — Code Breakdowns: ETL & Ops Scripts

> Function-level walkthroughs of every cited script — the offline machinery that builds,
> calibrates, and verifies the data the runtime serves. Grouped by directory:
> [fastapi-backend/scripts](#fastapi-backendscripts) · [python_scripts](#python_scripts) ·
> [scripts](#scripts-top-level). These are run manually/CLI; nothing here runs at request time —
> that's why the API stays ~104 ms.

---

## fastapi-backend/scripts/

### `audit_dataless_municipalities.py` (166 ln) — coverage auditor
- `_paged_column` (paginated column fetch), `_climate_ids` (set of municipalities with climate rows), `_reference_counts` (FK usage per table), `main` — reports municipalities lacking climate data, optionally deletes the ones nothing references. The API-side twin: pickers hide dataless municipalities (git `2a17ce9`).

### `calibrate_all.py` (322 ln) — full-coverage calibration
- `fetch_all_provinces`/`fetch_all_municipalities`; `call_ecosim(geo_id, mode)` — HTTP call to a running backend; `extract_result` (scores/outputs per source); `run_batch`; `write_csv`; `fmt_stats`, `correlation` (Pearson r — used to check score-vs-solar-irradiance correlation); `write_report` (distribution stats + flags); `main`. Runs EcoSim across **every** province + municipality → CSV + report — the ground truth for score sanity.

### `calibrate_municipalities.py` (267 ln) — municipality-mode bias check
- `call_ecosim(muni_id)` + `main` — hits the API across 30+ municipalities, summarizes per-source score distributions to spot systematic bias (e.g., solar always winning).

### `calibrate_renewables.py` (232 ln) — province-mode bias check
- `call_ecosim(province_id)` + `main` — same idea at province level (25+ provinces).

### `check_explanation_mismatches.py` (251 ln) — explanation staleness detector
- `load_calibration` (latest calibration CSV → ground truth), `fetch_explanations` (Supabase `municipality_renewable_explanations`), `parse_text_number` (regex-extract numbers embedded in explanation text), `check_mismatches` (diff cached text vs truth), `write_outputs` (CSV+report), `main` → exit code. Feeds `regenerate_explanations.py`.

### `check_rag_pipeline.py` (146 ln) — RAG smoke test
- `_build_index`, `_test_retrieval`, `_test_end_to_end`, `main` — index build → sample retrievals → full prompt+LLM path check.

### `check_full_pipeline.py` (123 ln) — RAG+Groq+Gemini-fallback end-to-end script (asserts provider chain works).

### `check_gemini_mock.py` (44 ln), `check_prompt_inspection.py` (36 ln), `check_rag_normalize.py` (33 ln), `check_retrieval_only.py` (31 ln) — small verification scripts: mock-mode Gemini path, prompt-construction inspection, output normalization, retrieval-only run.

### `diagnose_ecosim.py` (76 ln) — failure localizer
- `_province_ids` → `_call(province_id)` → `main`: iterates provinces calling `build_ecosim_dashboard_response`, prints the first failing province + exception — fastest way to find which geo breaks the pipeline.

### `extract_ecostress_lst.py` (307 ln) — ECOSTRESS surface temperature
- `read_lst_array` (HDF5 → array+meta), `extract_spatial_extent`, `build_affine_transform` (pixel→lat/lon), `extract_temperature_at` (sample LST at a point), `main` — geothermal/thermal input prep.

### `extract_kmz_to_geojson.py` (150 ln) — raster overlay prep
- `extract_overlay_manifest(kmz_path, kind)` — volcano/fault KMZ → frontend-ready JSON manifest; `main` — batch writes map overlay files.

### `ingest_geothermal_plants.py` (72 ln) — GEM tracker ingest
- `main` — Global Energy Monitor geothermal plant data → local dataset used by `geothermal/plants.py`.

### `ingest_ihfc.py` (156 ln) — heat-flow ingest
- `parse_ihfc` (IHFC DB → DataFrame), `filter_bounds` (PH bounding box), `main` → PH-relevant heat-flow CSV for `idw_heat_flow` interpolation.

### `ingest_wind_hydro_plants.py` (304 ln) — Wikipedia plant scraper
- `_dms_to_decimal`, `_extract_coordinates` (DMS text → lat/lon), `_status_from_notes`, `_parse_community`, `_year`, `_capacity`, `_extract_wiki_url`, `_clean_table`, `_find_tables` (locate the right tables), `main` — scrapes PH wind/hydro plant lists into the datasets `wind_plants.py`/`hydro_plants.py` serve.

### `prepare_aquifer_spatial.py` (94 ln) — aquifer shapefile prep
- `main` — aquifer shapefile → WGS84 GeoJSON ready for point-in-polygon queries (`features.query_aquifer_by_*`).

### `regenerate_explanations.py` (190 ln) — explanation backfill
- `get_all_municipalities`, `get_mismatched_ids` (from mismatch checker), `get_specific_ids`, `regenerate` (recompute + upsert one row), `write_report`, `main` — repairs stale `municipality_renewable_explanations` after scoring/settings changes.

### `regenerate_province_fallbacks.py` (199 ln) — province fallback builder
- `_load_or_empty`, `_get_supabase_province_names`, `_regenerate_atlas`, `_regenerate_era5`, `main` — computes province atlas/ERA5 CSVs as **means of member municipalities** so province mode has data even without direct measurements.

### `seed_rag_pgvector.py` (119 ln) — pgvector seeder
- `_chunk_documents`, `_vector_literal`, `_truncate`, `_build_records`, `_seed` (batch upsert), `_encode_local`/`_encode_external` (ST vs API embeddings), `main` — populates `rag_chunks` for the pgvector backend.

## python_scripts/

### `ingest_nasa_power_monthly.py` (478 ln) — NASA POWER pipeline
- `Config`/`load_config` (env-tunable: `START_YEAR`, `ONLY_MISSING`, `BATCH_SIZE`, rate-limit/backoff knobs); `build_supabase_client`, `build_session` (retrying HTTP); `last_complete_year_month`, `month_range`; `fetch_municipalities`, `fetch_existing_months` (gap detection — only fetch what's missing); parse_bool. Monthly climate → `municipality_climate_monthly`.

### `elevation_etl.py` (568 ln) — elevation enrichment
- `AppConfig`/`load_config`, `Municipality`, `JsonFormatter`/`setup_logging`, `create_http_session` (Open-Meteo Elevation API), embedded `SupabaseRestClient`/`SupabaseRestQuery` (SDK-free REST), `_is_jwt_key` — fetches elevation per municipality → terrain/geospatial fields.

### `run_terrain_pipeline.py` (48 ln) + `terrain_pipeline/` package — terrain raster → slope/morphometry per municipality (drives hydro runoff coefficient + gravity-flow inputs).

### `geocode_missing_coords.py` (218 ln) + `get_geocode.py` (181 ln) — Nominatim geocoders
- `load_env_file`, `_rest_get`/`_rest_patch`, `fetch_missing_ids`, `geocode(query, cache)` (≥1 s rate-limit honored — `RATE_LIMIT_SECONDS=1.1`, UA string with contact email), `update_coords`, `main` — fills missing lat/lon with cache so re-runs are cheap.

### `fill_missing_coords_from_geojson.py` (188 ln) — centroid fill
- `_rest_get`/`_rest_patch`, `normalize_name`, `compute_centroids` (from PH GeoJSON polygons), `main` — fuzzy name match → patch DB coords.

### `municipality_climate_analysis.py` (363 ln) — climate EDA
- `load_env`, `is_jwt_key`, `SupabaseRest*` (SDK-free REST again), `fetch_all_rows`, `validate_dataframe`, `summarize_missing_values`, `descriptive_statistics`, `plot_histogram` — analysis outputs to CSV/plots.

### `prepare_national_energy_csv.py` (274 ln) + `.ipynb` — DOE table builder
- `read_wide_csv` (wide year-format DOE sheets → dict), `safe_get`, `build_energy_table` (6 source CSVs → unified `national_energy_annual` records), `validate_data`, `write_csv`, `print_preview`, `main`. **Stdlib-only** (no pandas) so it runs anywhere.

### `clean_scraped_products.py` (453 ln) — listing normalizer
- `normalize_header`, `standardize_columns` (HEADER_SYNONYMS map), `sniff_delimiter`, `read_csv_with_fallback` (encoding+delimiter guessing), `validate_file`, `normalize_text`, `normalize_name`, `detect_currency`, `parse_price_value` — turns messy scraped listings → `cleaned_products_master.csv` (generated artifact).

### `extract_product_kw.py` (78 ln) — kW parser
- `extract_kw_values` (regex pull from product names), `mean_or_none`, `compute_kw` (row → kw), `build_arg_parser`, `main`.

### `append_istabreeze_products.py` (94 ln) — catalog append
- `normalize_name`, `build_rows`, `main` — appends Istabreeze catalog rows to the master CSV.

### `join_wind_data.py` (276 ln) / `join_wind_data_betz.py` (303 ln) — wind-product joins
- `detect_source`, `normalize_text`, `parse_power_w`, `parse_diameter_m`, `parse_wind_speed_mps`, `compute_power_coefficient` (Betz-bounded in `_betz` variant), `read_csv_rows`, `read_json_rows`, `extract_row_fields`, `find_wind_files` → `wind_products_joined(_betz).csv` + stats — product averages consumed by `wind_output_calc.load_wind_averages`.

### `prepare_rag_products.py` (407 ln) — product→corpus
- `normalize_*`, `coerce_price`, `enrich_category`, `infer_product_type`, `tokenize`, `token_set_similarity` (dedup matching), `build_document` — products → RAG-ready documents.

### `wind_power_coefficient.py` (62 ln) — Cp calculator
- `compute_power_coefficient` (Cp = P / (½ρAv³), **BETZ_LIMIT = 16/27**), `validate_power_coefficient` — flags nonphysical products.

### `municipality_climate_averages.csv` — bundled fallback data (not code).

## scripts/ (top-level)

### `extract_centroids.py` (341 ln) — polygon→centroid+area
- `norm` (name normalization), `compute_centroid_and_area` (shapely), `cos` (equirectangular area adjust), `process_geojson`, `SupabaseRestClient`, `build_province_lookup`/`build_municipality_lookup` (normalized-name maps), `write_csv`, `main` → `*_centroids.csv` driving `geospatial_metadata` inserts.

### `extract_atlas_values.py` (196 ln) — atlas raster sampling
- `load_centroids`, `sample_points` (rasterio pixel sample at each centroid), `clamp_or_none` (physical bounds), `main` → `municipality_atlas_averages` CSV (GHI/PVOUT, wind speeds).

### `extract_era5_wind.py` (151 ln) / `inspect_era5.py` (82 ln) — ERA5 10 m wind
- `sample_gridded` (xarray dataset → per-point wind series), `main` → ERA5 averages CSVs; `inspect_era5` prints GRIB/NetCDF structure.

### `build_province_atlas_averages.py` (208 ln) — province atlas values
- `sample_points`, `clamp`, `weighted_mean` (area-weighted aggregation), `main` → `province_atlas_averages`.

### `ingest_atlas_averages.py` (118 ln), `ingest_province_atlas_averages.py` (81 ln), `ingest_era5_averages.py` (83 ln), `ingest_municipality_climate_averages.py` (105 ln) — upsert family
- `_clean_row` (sanitize/NaN→None), `_fetch_valid_municipality_ids` (FK guard — only rows for real municipalities), `main` → Supabase upserts.

### `update_municipality_suitability_from_atlas.py` (135 ln) — map-score migration
- `_solar_score` (PVOUT→score), `_wind_score` (100 m wind→score), `load_centroids`, `build_upsert_rows`, `main` — one-off backfill of `municipalities.suitability_*` from atlas CSVs.

### `scrape_philatlas.py` (659 ln) — PhilAtlas gap finder
- `norm_name`, `load_geojson_province_map`, `load_geojson_municipality_map`, `fetch_page`, `parse_index_page`, `parse_province_page`, `scrape_philatlas` (walk region/province/municipality pages), `SupabaseRestClient`, `main` → gap CSVs (places PhilAtlas knows that we lack, and vice-versa).

### `sync_psgc_data.py` (1,184 ln) — PSA PSGC sync (largest script)
- `normalize_name`, `extract_parenthetical` (handles renamed units e.g. "(Old Name)"), `normalize_with_old_name`; `PsaApiClient` (authenticated PSA API w/ pagination); `SupabaseClient`; `_parse_population_value`, `extract_population`; `sync_regions`, `sync_provinces`, `sync_municipalities` (+ barangays) — upsert in FK order. The authoritative admin-hierarchy feeder.

### `insert_missing_municipalities.py` (181 ln), `insert_from_csvs.py` (173 ln) — gap fillers
- `load_province_name_by_psgc`, `SupabaseRest*`, `read_csv`, `main` — insert gap rows respecting province FK.

### `insert_geospatial_metadata.py` (195 ln) — metadata loader
- `SupabaseRestClient`, `read_csv`, `main` — centroid CSVs → `geospatial_metadata`.

### `identify_gaps.py` (276 ln) — coverage diff
- `SupabaseRestClient/Query`, `compute_centroid`, `load_geojson_municipalities`, `fetch_all_municipalities_from_db`, `main` → missing-from-DB / null-scores / has-data CSVs.

### `migrate_csv_to_supabase.py` (511 ln) — bulk dataset migration
- `_is_jwt_key`, `_resolve_service_role_key`, `_get_client`, `_normalize_text`, `_sanitize_value`, `_records_from_df`, `_fix_category`, `migrate_doe_datasets`, `_valid_municipality_ids`, `migrate_climate` (+ more) — the migration-0008 companion: local CSV/GeoJSON → Supabase.

### `run_nasa_for_gaps.py` (334 ln) — NASA POWER gap filler
- `SupabaseRest*`, `load_gap_municipality_ids`, `fetch_db_gap_municipalities`, `fetch_gap_municipalities`, `fetch_nasa_data` (lat/lon point query), `coerce_value`, `build_climate_rows`, `main` — targeted fetch for the gaps `identify_gaps.py` found.

### `precompute_aquifer_scores.py` (418 ln) — geothermal aquifer precompute
- `_get_client`, `_load_aquifer_gdf`, `_sanitize`, `_penalised_score` (distance penalty), `_compute_aquifer_score`, `_aquifer_stats`, `_reset_geothermal_suitability`, `main` → `geothermal_suitability` rows.

### `generate_erd.py` (360 ln) — schema ERD
- `draw_table`, `draw_relationship`, `main` — matplotlib ERD PNG of the live schema.

### `verify_fixes.py` (427 ln) — post-fix verifier; `check_cache.py` (4 ln), `debug_regions.py` (37 ln), `temp_db_check.py` (43 ln), `test_api.py` (16 ln), `verify_sync.py` (30 ln) — small diagnostic scripts (cache probe, region-name debug, DB sanity, PSA-API pagination probe, sync spot-check).

### `simplify-geojson.js` — GeoJSON simplifier (map payload size decision — see `03` §10).

### `psgc_cache/` — cached PSGC API responses (data, not code).

---
*Every entry reflects real signatures extracted from the files; purpose statements cite docstrings/comments where present. Scripts marked "SDK-free REST" duplicate the tiny `SupabaseRestClient` pattern so they run where the full SDK isn't installed.*
