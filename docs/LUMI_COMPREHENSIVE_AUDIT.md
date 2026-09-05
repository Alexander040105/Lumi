# LUMI Comprehensive Technical Audit

This report provides an end-to-end technical audit of the LUMI project, covering system architecture, database design, data completeness, scientific/engineering accuracy, the EcoSim and EnergyHub modules, forecasting, GIS, the AI/RAG pipeline, data engineering, performance, missing features, and DigitalOcean deployment options. Each finding is grounded in the current codebase and schema, and recommendations are tied to specific files, functions, or tables where possible.

---

## Executive Summary

LUMI is an ambitious renewable-energy intelligence platform for the Philippines. It already contains a solid FastAPI backbone, a React/Vite/Tailwind frontend, a Supabase/PostgreSQL database, and an impressive set of domain-aware services (EcoSim, EnergyHub, RAG). However, the system is currently closer to a feature-rich prototype than a production-grade platform. The audit identifies **critical** gaps in calculation rigor, data completeness, database normalization, RAG accuracy, and production operations. Addressing the highest-impact items will significantly improve accuracy, scalability, and maintainability while making a DigitalOcean deployment cost-effective and stable.

### Top 10 Priority Actions

| # | Action | Impact | Effort | Section |
|---|--------|--------|--------|---------|
| 1 | Replace coarse 0.5° NASA POWER climate with higher-resolution solar/wind data and proper downscaling | Very High | High | 3, 6, 10 |
| 2 | Refactor `municipalities` table: move suitability scores to normalized tables and drop denormalized columns | High | Medium | 2, 5 |
| 3 | Add real hydrology data (streamflow, hydraulic head, watershed boundaries) and remove Rational-Method guesses | High | High | 3, 6 |
| 4 | Build a proper ARIMA/SARIMA/ensemble forecasting pipeline with exogenous variables and uncertainty quantification | High | High | 7 |
| 5 | Containerize FastAPI + frontend, add health checks, structured logging, and CI/CD | High | Medium | 15 |
| 6 | Re-architect the RAG pipeline with hybrid search, citation verification, and prompt guardrails | High | Medium | 9 |
| 7 | Add province/municipality coverage validation and PSGC-code alignment | High | Low-Medium | 4 |
| 8 | Implement proper distribution-utility tariff lookup instead of a single national rate | High | Medium | 5, 6 |
| 9 | Introduce automated ETL scheduling, data lineage, and versioning | High | Medium | 10 |
| 10 | Add observability (OpenTelemetry or similar), rate limiting, and API versioning | High | Low-Medium | 11, 15 |

---

## 1. System Architecture Review

### 1.1 Current Architecture

The backend is built with **FastAPI** (`fastapi==0.115.0`) and organized under `fastapi-backend/app/`. The `main.py` entrypoint loads the global FastAPI app, applies CORS, and mounts all routes via `app/routes/api.py`. The application startup event triggers `rag_pipeline.ensure_index_built()`, which loads/creates a FAISS index for RAG retrieval.

Key architectural patterns observed:

- **Service singletons**: `energyhub.py`, `ecosim.py`, `geothermal/features.py`, `municipality_suitability_builder.py` rely on module-level singletons and global caches (`_energyhub_ml`, `_energyhub_service`, `_index`, `_chunks`, etc.).
- **Mixed sync/async**: Routes are `async`, but much of the service layer calls synchronous Pandas/NumPy/FAISS and Supabase REST operations, often blocking the event loop.
- **Custom Supabase REST client**: `supabase_service.py` includes a hand-rolled `SupabaseRestQuery` that re-implements parts of the official `supabase-py` client, with `httpx.Client(timeout=10.0)` and ad-hoc URL encoding.
- **Settings management**: `config/settings.py` uses `pydantic-settings` with `.env` loading. Defaults are hard-coded to `http://localhost:5173` for CORS.
- **State and data loaded at startup**: `EnergyHubML` loads all CSV files into memory at startup; `rag_pipeline` loads the FAISS index and knowledge base into global variables. This makes cold starts slow and memory-hungry.

### 1.2 Strengths

- **Clean route organization**: `api.py` groups routers logically (ecosim, energyhub, geothermal, geospatial, chat, admin, products, simulations).
- **Granularity-aware services**: `climate_service.py` and `geospatial_service.py` implement fallback hierarchies (barangay → municipality → province), which is a scalable pattern.
- **Caching layer**: Redis is used for climate, centroid, and suitability map caching with sensible TTLs (`_CLIMATE_TTL=86400`, `_DEFAULT_TTL=3600`, `_ECOSIM_TTL=1800`).

### 1.3 Key Architectural Issues

#### 1.3.1 No API versioning discipline

The `api_v1_prefix` is set to `/api/v1`, but the API surface is not versioned internally. Breaking changes in schemas or route behavior will affect all consumers. **Recommendation**: introduce schema-versioning tests, OpenAPI diff checks, and a deprecation policy for endpoints.

#### 1.3.2 Heavy startup and singleton state

`EnergyHubML.__init__` in `app/ml/predictor.py` loads all historical and forecast CSVs into memory at startup. `rag_pipeline.py` loads a ~11 MB FAISS index and a ~5 MB chunks JSON into global module variables. This causes:

- Long container startup times (bad for serverless or auto-scaling on DigitalOcean App Platform).
- High memory footprint (~100–300 MB baseline before request load).
- Difficulty in scaling workers horizontally because each process replicates the state.

**Recommendation**: lazy-load ML artifacts on first request or store them in a shared memory/cache (e.g., Redis for serialized artifacts, or a separate model service). Pre-computed forecast CSVs should be served from object storage or a small SQLite/Postgres cache, not all loaded into a Pandas DataFrame at startup.

#### 1.3.3 Custom REST client duplicates official SDK

`supabase_service.py` re-implements query building and `httpx` calls. It lacks pagination helpers, connection pooling, retry logic, and proper handling of PostgREST advanced operators. The fallback `SupabaseRestClient` is used when the key is not a JWT, which adds an unnecessary branch.

**Recommendation**: standardize on `supabase-py` with `service_role_key` for admin operations and `anon_key` for public routes. Remove the custom client to reduce maintenance surface.

#### 1.3.4 Mixed sync/async operations in async routes

Many routes call `svc.build_overview()`, `svc.get_forecast()`, or `renewable_energy_calculator()`, which internally use `pandas.read_csv`, FAISS, and synchronous Supabase/HTTP calls. In FastAPI, an `async def` route that calls blocking CPU/disk/IO work will block the event loop, reducing concurrency.

**Recommendation**: run blocking work in `asyncio.to_thread` or `ThreadPoolExecutor`, or convert CPU-heavy services to sync routes with `def` (FastAPI runs sync routes in a thread pool by default). Benchmark with `httpx` async client for Supabase if you keep async.

#### 1.3.5 Configuration and secret handling

`.env` loading is in `settings.py`, but there is no validation that required keys are present at startup. `redis_client.py` reads `UPSTASH_REDIS_URL` without fallback; if missing, every Redis call silently fails and the app falls back to expensive DB queries.

**Recommendation**: add a startup health check that validates `supabase_url`, `supabase_service_role_key`, `UPSTASH_REDIS_URL` (or DigitalOcean Redis), and `GEMINI_API_KEY`/`GROQ_API_KEY`. Use Pydantic `SecretStr` for keys and fail fast on missing critical configuration.

#### 1.3.6 CORS and security defaults

`main.py` allows `allow_methods` including `PUT` and `DELETE` globally, and `allow_headers` is broad. There is no rate limiting, CORS is effectively `*` in development, and there is no middleware for request logging or request ID propagation.

**Recommendation**: restrict CORS to known origins in production, add `slowapi` or ASGI rate-limiting middleware, and add request ID tracing.

---

## 2. Database Improvements

### 2.1 Schema Overview

The primary schema is defined in `lumi_schema_v4.sql` (1,464 lines) plus migrations in `supabase/migrations/0001_geospatial_architecture.sql` and `0002_psgc_data_columns.sql`. The design contains a normalized `regions/provinces/municipalities/barangays` hierarchy, plus many domain tables for climate, suitability, energy, chat, and admin.

### 2.2 Critical Issues

#### 2.2.1 Severe denormalization in `municipalities`

`municipalities` currently holds many score columns (`solar_suitability_score`, `solar_classification`, `solar_factors`, `wind_*`, `hydro_*`, `geothermal_*`, `composite_*`, plus repeated `*_factors` JSONB columns). This violates 1NF and 3NF:

- A municipality can have multiple suitability metrics over time.
- Score values and `factors` JSON are repeated per row.
- Adding a new renewable type requires an `ALTER TABLE`.

The migration `0001_geospatial_architecture.sql` correctly creates `solar_suitability`, `wind_suitability`, `hydro_suitability`, `composite_suitability` tables, but the old columns are kept for backward compatibility, and many service functions still read from the denormalized columns (`energyhub.py`, `municipality_suitability_builder.py`, `ecosim.py`).

**Recommendation**:

1. Complete the migration: write a one-time backfill from `municipalities` to the standalone tables.
2. Update all services to read from `*_suitability` tables.
3. Drop the denormalized score columns from `municipalities` after a deprecation window.
4. Add a unique constraint on `geothermal_suitability` table on `municipality_id` (it appears to be missing from schema).

#### 2.2.2 Missing indexes and suboptimal queries

Observed in services:

- `energyhub.py` fetches `provinces`, `hydropower_suitability`, `geothermal_suitability`, `municipalities`, and `municipality_climate_monthly` with `.limit(10000)`. There are no `WHERE` clauses on `province_id` or `municipality_id`, so the query must transfer large result sets to the backend for Python-side aggregation.
- `municipality_suitability_builder.py` fetches all municipalities, all climate, all hydro, and all geothermal data into memory to build scores. This does not scale beyond a few thousand records.
- `climate_service.py` does not use time-series indexes on `(municipality_id, year, month)` in code, although the migration adds them.

**Recommendation**:

- Add composite indexes where missing: `(province_id)`, `(municipality_id, year, month)`, `(barangay_id, year, month)`, and partial indexes for non-null scores.
- Push aggregation into PostgreSQL using `GROUP BY` and `AVG`/`JSONB_AGG` instead of fetching all rows into Python.
- Use Supabase RPC for heavy aggregations and expose materialized views for map tiles.

#### 2.2.3 Row-Level Security (RLS) is too permissive

The schema grants `ALL` to `anon` and `authenticated` on many tables, and policies such as `Allow public read` plus `Allow authenticated write` are broad. Admin tables (`admin_audit_log`, `user_roles`) should not be writable by `authenticated` indiscriminately; they should be restricted to a verified `admin`/`service_role` role.

**Recommendation**: audit all RLS policies, remove `GRANT ALL` from `anon` on write tables, and create a `service_role` bypass function for admin routes.

#### 2.2.4 Data type and constraint gaps

- Many numeric columns store JSON or text values that should be typed (e.g., `factors` JSONB is good, but `solar_score` stored as numeric is okay).
- `geothermal_suitability` and `hydropower_suitability` use `municipality_id` but the standalone migration does not include a `geothermal_suitability` table; instead there is `geothermal_suitability` with `geothermal_score` in the original schema. Need to confirm the migration has a `geothermal_suitability` table for consistency.
- `forecast_cache` has `geo_level` and `geo_id` but no index on them; queries will be slow once sub-national forecasts are added.

**Recommendation**: add `CHECK` constraints for valid score ranges (`0..1` or `0..100`), add composite index on `forecast_cache(geo_level, geo_id, metric, created_at)`, and standardize naming (`score` vs `*_suitability_score`).

#### 2.2.5 Soft-deletion and audit trails

There is no `deleted_at` or `is_active` flag on core entities, and `updated_at` triggers are not consistently applied to all tables. The `admin_audit_log` is a good start but does not cover data changes.

**Recommendation**: add `created_at`/`updated_at` triggers to all business tables and use a versioning extension (`temporal_tables` or `pg_audit`) for high-value tables.

---

## 3. Data Completeness Audit

LUMI’s value depends on the completeness, recency, and spatial resolution of its input data. This section lists missing datasets, why they matter, how they improve calculations, and recommended sources. All recommendations prioritize free, government, or internationally recognized data.

### 3.1 Methodology for Each Gap

For each missing dataset, the audit documents:

- **Why it matters** — what calculation or feature is currently degraded.
- **How it improves calculations** — the specific formula or decision that becomes more accurate.
- **Recommended source** — authoritative API, download, or scraping path.
- **Update frequency**.
- **Confidence level** of the source.
- **Acquisition method** — API, scraper, manual download, GEE.

### 3.2 Climate & Solar Data

#### 3.2.1 High-resolution Global Horizontal Irradiance (GHI), Direct Normal Irradiance (DNI), Diffuse Horizontal Irradiance (DHI)

- **Why it matters**: Current EcoSim uses NASA POWER `allsky_sfc_sw_dwn` at ~0.5° resolution (≈ 50 km) and a single temperature factor. This is too coarse to differentiate municipalities within the same grid cell.
- **How it improves calculations**: With GHI/DNI/DHI, solar output can be modeled with anisotropic diffuse models (Perez, Hay-Davies), tilted irradiance on actual rooftop orientations, and spectral/temperature-corrected performance ratios.
- **Recommended sources**:
  - **Global Solar Atlas** (World Bank / Solargis): free interactive maps, ~250 m–1 km; country downloads available.
  - **NASA POWER**: free API, but 0.5° resolution; use only as fallback.
  - **Solargis** (paid, high accuracy, 250 m): if budget allows.
  - **PVWatts** (NREL): free API for hourly simulation using TMY data at station locations; useful for validation.
  - **PAGASA**: surface radiation measurements for some stations; contact PAGASA for data-sharing MOU.
- **Update frequency**: Annual for atlas layers; daily/hourly for satellite-derived APIs.
- **Confidence**: High (Solargis / Global Solar Atlas), Medium (NASA POWER), Medium-High (PAGASA ground stations).
- **Acquisition**: download GeoTIFF/CSV from Global Solar Atlas; use PVWatts API for representative stations; scrape or request PAGASA data.
- **Automation**: schedule annual download of Global Solar Atlas rasters, clip to Philippines, and sample at municipality centroids; keep a `solar_resource_monthly` table with `municipality_id`, `year`, `month`, `ghi`, `dni`, `dhi`, `gti` (tilted at latitude).

#### 3.2.2 Ambient temperature, module temperature, and albedo

- **Why it matters**: `solar_output_calc.py` uses a fixed temperature coefficient and a generic `dust_loss_from_wind` function. Real module temperature depends on wind speed, ambient temperature, and albedo; `NOCT` (Nominal Operating Cell Temperature) is not used.
- **How it improves calculations**: Replace the current `temp_factor` with a `PVLIB` or ` Sandia ` model: `T_cell = T_amb + (G / 800) * (NOCT - 20) * (1 - η / 0.9)`, then `P = P_stc * (1 + γ * (T_cell - 25))`.
- **Recommended sources**:
  - NASA POWER: `T2M`, `T2M_MAX`, `T2M_MIN`, `WS10M`.
  - PAGASA station data.
  - MODIS/Landsat land surface temperature via Google Earth Engine for spatially distributed estimates.
  - MODIS MCD43 for albedo.
- **Update frequency**: Monthly/daily.
- **Confidence**: High (NASA POWER + PAGASA), Medium (MODIS LST).
- **Automation**: ingest NASA POWER monthly aggregates; pull PAGASA daily station CSVs; use GEE for MODIS albedo raster.

#### 3.2.3 Aerosol optical depth / dust / soiling

- **Why it matters**: `dust_loss_from_wind` uses a heuristic mapping of wind speed to dust loss. Real soiling depends on dust deposition, rainfall cleaning, and local land cover.
- **How it improves calculations**: Introduce a monthly soiling ratio from aerosol optical depth (AOD) and rainfall, validated against published Philippine soiling studies.
- **Recommended sources**:
  - NASA POWER / CAMS: AOD550.
  - CAMS (Copernicus Atmosphere Monitoring Service): daily AOD via API.
  - NASA MODIS Deep Blue AOD via GEE.
  - Local studies (e.g., UP, PAGASA).
- **Update frequency**: Monthly/daily.
- **Confidence**: Medium.
- **Automation**: download CAMS monthly means; derive `soiling_loss_pct` from AOD and monthly precipitation.

### 3.3 Wind Data

#### 3.3.1 High-resolution wind speed and power density at multiple hub heights

- **Why it matters**: `wind_output_calc.py` uses NASA POWER `WS10M` at 10 m and extrapolates to hub height with a fixed power-law coefficient. This is inaccurate for complex terrain and underestimates gusts/wind shear.
- **How it improves calculations**: Use wind speed at 50/80/100 m and the logarithmic wind profile or WAsP/WRF-based maps to compute capacity factor from a turbine power curve.
- **Recommended sources**:
  - **Global Wind Atlas** (DTU / World Bank): free, ~250 m resolution wind resource maps for the Philippines; download as GeoTIFF.
  - **Renewables.ninja** (Imperial College): free API for wind and PV simulations using MERRA-2/ERA5 reanalysis; can model arbitrary lat/lon and turbine models.
  - **ERA5 (Copernicus CDS)**: hourly wind speed, temperature, pressure at 0.25°; free but requires registration.
  - **PAGASA**: anemometer station data.
- **Update frequency**: Annual (atlas); daily/hourly (APIs).
- **Confidence**: High (Global Wind Atlas for long-term mean), High (ERA5/Renewables.ninja for time-series), Medium (PAGASA point measurements).
- **Acquisition**: Global Wind Atlas GeoTIFF download; Copernicus CDS API for ERA5; Renewables.ninja API; PAGASA data request.
- **Automation**: build a monthly `wind_resource_monthly` table with `municipality_id`, `year`, `month`, `ws10m`, `ws50m`, `ws80m`, `ws100m`, `power_density_w_m2`, `air_density_kg_m3`.

#### 3.3.2 Turbine power curves and manufacturer specifications

- **Why it matters**: `wind_output_calc.py` derives a capacity factor from a generic CSV of average rotor and Cp values. It does not use actual turbine power curves or cut-in/cut-out/rated wind speeds.
- **How it improves calculations**: Use IEC 61400-12 power-curve data for specific turbine models; compute `P = power_curve(V) * availability * η_grid`.
- **Recommended sources**:
  - Wind turbine manufacturers (Vestas, Siemens Gamesa, Goldwind, local suppliers).
  - The Wind Power database.
  - IRENA cost and performance data.
- **Update frequency**: As needed.
- **Confidence**: High.
- **Automation**: maintain a `turbine_power_curves` table and allow users to select model; default to a representative 1–10 kW residential turbine for EcoSim.

### 3.4 Hydropower Data

#### 3.4.1 Streamflow / river discharge observations

- **Why it matters**: `hydro_output_calc.py` estimates flow from rainfall, slope, and catchment area using the Rational Method with assumed runoff coefficients and a 40% environmental reserve. This is not hydrologically sound for continuous flow estimation.
- **How it improves calculations**: Use measured or modeled streamflow (m³/s) and design flow with a flow-duration curve (Q30, Q50, Q90) to estimate firm and average energy.
- **Recommended sources**:
  - **NAMRIA** / **DENR**: river network and watershed boundaries.
  - **PAGASA-Hydro**: rainfall-runoff and water level data (limited public streamflow).
  - **Global Runoff Data Centre (GRDC)**: daily discharge for some international stations.
  - **HydroSHEDS / GEE**: river network, flow accumulation, catchment area, and elevation-derived hydraulic head.
  - **OpenStreetMap** waterways and river centerlines.
- **Update frequency**: Daily/monthly for streamflow; static for hydrography.
- **Confidence**: High (GRDC observed), Medium (HydroSHEDS modeled), Low-Medium (Rational Method).
- **Acquisition**: GRDC daily discharge data request; HydroSHEDS from World Wildlife Fund; NAMRIA river network request; GEE for flow accumulation.
- **Automation**: download HydroSHEDS 15-arc-second DEM and flow accumulation; compute catchment polygons and mean flow using regionalization from rainfall; store `streamflow_monthly` table with `municipality_id`/`watershed_id`, `q_mean`, `q_min`, `q_max`.

#### 3.4.2 Hydraulic head and penstock length

- **Why it matters**: The current hydro formula uses `head` derived from `max_elevation - min_elevation` within the municipality, which is not the actual head between intake and powerhouse.
- **How it improves calculations**: Use DEM-derived head along actual river reaches (intake to powerhouse) and add penstock head loss (Hazen-Williams/Darcy-Weisbach).
- **Recommended sources**:
  - **SRTM / NAMRIA DEM**: 30 m or better.
  - **HydroSHEDS**: flow accumulation and river network.
  - **OSM / NAMRIA**: river and stream features.
- **Update frequency**: Static; update if better DEM becomes available.
- **Confidence**: High for DEM-derived gross head; Medium for penstock loss (requires design).
- **Automation**: use GEE/WhiteboxTools to extract river reaches and elevation profiles per municipality; store `hydro_site_candidates` table with `head_m`, `penstock_m`, `head_loss_m`.

#### 3.4.3 Runoff coefficients and watershed delineation

- **Why it matters**: `hydro_output_calc.py` uses a hard-coded lookup table for runoff coefficients based on slope and a 40% environmental flow reserve. Runoff is highly dependent on land cover, soil type, antecedent moisture, and rainfall intensity.
- **How it improves calculations**: Replace with actual hydrological model parameters (CN method or SWAT/HEC-HMS) calibrated to observed flow where available.
- **Recommended sources**:
  - **DENR** land cover maps.
  - **NAMRIA** soil maps.
  - **ESA WorldCover** (Sentinel-2, 10 m, annual).
  - **MODIS / VIIRS** land cover.
  - **USDA-SCS** curve number tables adapted to Philippines.
- **Update frequency**: Annual.
- **Confidence**: High (WorldCover), Medium (CN method), Medium (DENR).
- **Automation**: ingest ESA WorldCover raster, compute land-cover fractions per catchment, and map to CN values; store in `watershed_landcover` table.

### 3.5 Geothermal Data

#### 3.5.1 Heat-flow and temperature-gradient measurements

- **Why it matters**: `geothermal/features.py` interpolates heat flow from the IHFC global database with IDW radius 300 km and only 3–4 local measurements. This is insufficient for meaningful geothermal prospectivity at municipality scale.
- **How it improves calculations**: Add dense heat-flow measurements, temperature-gradient wells, and geothermal well data from PHIVOLCS and DOE to constrain subsurface conditions.
- **Recommended sources**:
  - **IHFC Global Heat Flow Database** (free, sparse in PH).
  - **PHIVOLCS**: volcano and geothermal data, temperature-gradient wells.
  - **DOE-REMB (Renewable Energy Management Bureau)**: geothermal plant data and prospectivity maps.
  - **World Bank / ESMAP** geothermal resource assessments.
- **Update frequency**: Static/occasional.
- **Confidence**: High (well data), Low-Medium (sparse IDW interpolation).
- **Automation**: request DOE/PHIVOLCS geodatabase; update `geothermal_heatflow` table with lat/lon, heat_flow_mw_m2, environment, depth, source.

#### 3.5.2 Active fault and fracture systems

- **Why it matters**: The current implementation uses a simplified list of faults and volcanoes with haversine distance. It does not capture fault orientation, slip rate, or permeability.
- **How it improves calculations**: Use fault density, distance to Quaternary faults, and proximity to calderas/volcanic centers as continuous variables.
- **Recommended sources**:
  - **PHIVOLCS** Fault Finder / active fault maps.
  - **GEM Global Active Faults Database**.
  - **USGS / Smithsonian GVP** volcano database.
  - **OpenStreetMap** for surface traces.
- **Update frequency**: Static.
- **Confidence**: High.
- **Automation**: convert PHIVOLCS shapefiles to GeoJSON, compute minimum distance and fault density per municipality with `shapely`/`geopandas`.

#### 3.5.3 Aquifer / reservoir properties

- **Why it matters**: `calculate_aquifer_score` uses a global `aquifer_properties.csv` and a spatial `aquifers_ph.geojson`. These are likely not calibrated for deep geothermal reservoirs.
- **How it improves calculations**: Replace with geothermal reservoir-specific porosity/permeability ranges from DOE/PHIVOLCS studies.
- **Recommended sources**:
  - **PHIVOLCS** geothermal well logs.
  - **DENR-Mines & Geosciences Bureau (MGB)** hydrogeologic maps.
  - **IGME / local university** studies.
- **Update frequency**: Static/occasional.
- **Confidence**: Medium-High (well logs), Low (global aquifer proxy).

### 3.6 Socio-Economic and Demand Data

#### 3.6.1 Municipal electricity consumption and distribution-utility sales

- **Why it matters**: `energyhub.py` estimates municipal demand from provincial DOE totals and PSA population ratios. This assumes uniform per-capita consumption, which is wrong (cities vs. rural, industrial load).
- **How it improves calculations**: Use actual DU sales by municipality/barangay, or downscale using nighttime lights and economic indicators.
- **Recommended sources**:
  - **ERC/DOE**: distribution utility sales filings (often aggregated to DU franchise area).
  - **Meralco, Visayan Electric, Davao Light, etc.**: annual reports and rate filings; may require data-sharing MOU.
  - **NASA VIIRS DNB nighttime lights**: free, monthly, 500 m; strong proxy for electricity consumption.
  - **PSA**: municipal income class, number of establishments, household energy access.
- **Update frequency**: Annual (DU reports); monthly (VIIRS).
- **Confidence**: High (DU actuals), Medium (VIIRS proxy), Medium (PSA economic proxies).
- **Automation**: download VIIRS monthly composites via GEE/NOAA; calibrate a regression to province-level DOE totals and apply to municipalities; store `municipal_energy_consumption` table with year, source, confidence.

#### 3.6.2 Distribution utility tariffs and rate schedules

- **Why it matters**: EcoSim uses `COST_PER_KW_SOLAR` and other hard-coded cost constants and a national average electricity rate of PHP 14.35/kWh. Actual tariffs vary significantly by DU, customer class, and time of use.
- **How it improves calculations**: Look up the user's DU and rate schedule for accurate savings, payback, and bill offset.
- **Recommended sources**:
  - **ERC** rate schedules.
  - **DU websites** (Meralco, Visayan Electric, etc.).
  - **DOE** electric-power industry statistical bulletins.
- **Update frequency**: Monthly/quarterly.
- **Confidence**: High.
- **Automation**: scrape ERC/DU rate PDFs with `tabula-py`/`camelot`; maintain `du_rate_schedules` table with `du_name`, `customer_class`, `rate_php_per_kwh`, `effective_date`.

### 3.7 Equipment and Cost Data

#### 3.7.1 Local equipment prices and availability

- **Why it matters**: `rag_knowledge_builder.py` aggregates Alibaba/Amazon/Lazada prices and converts currencies with fixed rates (USD 60, CNY 8.96). This is volatile and does not reflect local installation costs, warranties, shipping, or taxes.
- **How it improves calculations**: Use Philippine-specific pricing from local suppliers and apply installation, O&M, and financing costs.
- **Recommended sources**:
  - **Lazada/Shopee Philippines** (scrape with Playwright/Scrapy; respect robots.txt and terms).
  - **Solar suppliers** (e.g., Sinag, Solaric, etc.) websites.
  - **Philippine DOE RE cost benchmark reports**.
- **Update frequency**: Monthly.
- **Confidence**: Medium-High.
- **Automation**: schedule monthly scraping with price normalization and outlier removal; store in `product_prices` and `cost_benchmarks` tables.

### 3.8 National Energy Statistics

- **Why it matters**: `EnergyHubML` in `app/ml/predictor.py` reads `master_preprocessed.csv` and `forecast_consumption_2025_2030.csv`. If these CSVs are stale, all EnergyHub analytics are stale.
- **How it improves calculations**: Automate DOE data extraction and versioning; reconcile with IRENA and NGCP data.
- **Recommended sources**:
  - **DOE Philippine Power Statistics** annual and monthly reports (PDF/Excel).
  - **NGCP** grid operations reports (peak demand, generation mix).
  - **IRENA** country statistics.
  - **PSA** energy accounts.
- **Update frequency**: Monthly/annual.
- **Confidence**: High.
- **Automation**: `tabula-py`/`camelot` to extract DOE PDF tables; store in `national_energy_annual`, `national_energy_monthly`, `grid_operations` tables; version CSVs in object storage.

---

## 4. Province/Municipality Coverage Expansion

### 4.1 Current Coverage

The `municipalities` table holds 1,618 municipalities, and `barangays` holds ~42,000 barangays. This suggests the PSGC (Philippine Standard Geographic Code) hierarchy is largely loaded. However, the following coverage issues remain:

- **GeoJSON boundary mismatch**: The EnergyHub map builder (`energyhub.py` `_build_renewable_potential_map`) uses a hard-coded `_PROVINCE_NAME_MAP` to reconcile GeoJSON `adm2_en` names with database province names. This is brittle and will break with new PSGC updates or boundary changes.
- **Municipal climate data**: `municipality_climate_monthly` appears to be populated for a single year (2010) based on code comments; `energyhub.py` explicitly filters `year = 2010` for raw climate. This makes the renewable potential map stale and not representative of current climate.
- **Barangay climate**: `barangay_climate_monthly` exists in schema and `climate_service.py` but is likely unpopulated; all barangay analysis falls back to municipality data.
- **Geospatial metadata**: `geospatial_metadata` is populated by `scripts/extract_centroids.py` from GeoJSON, but the area calculation uses a rough equirectangular approximation rather than an equal-area projection.
- **PSGC code alignment**: `0002_psgc_data_columns.sql` adds `psgc_code` columns, but there is no verification that `regions`, `provinces`, `municipalities`, `barangays` match the latest PSA PSGC release.

### 4.2 Recommendations

#### 4.2.1 Adopt PSGC codes as the canonical geographic key

- Replace name-based joins with `psgc_code` joins across all tables.
- Add `UNIQUE` constraints on `psgc_code` at each admin level.
- Maintain a `psgc_codes` reference table with `code`, `name`, `level`, `parent_code`, `effective_date`, `deprecated`.
- Add a scheduled reconciliation job (`scripts/verify_sync.py` already exists; expand it) that downloads the latest PSGC CSV from PSA and flags mismatches.

#### 4.2.2 Improve boundary and centroid data

- Use **PSA official boundary shapefiles** (if available via MOU) or **GADM / PhilAtlas / OSM** boundaries.
- Compute centroids and areas using an equal-area projection (EPSG:32651, UTM zone 51N, for the Philippines) rather than equirectangular approximations.
- Validate that GeoJSON polygons are valid (no self-intersections, correct ring orientation) before loading into `geospatial_metadata`.
- Store `geometry` column as `GEOMETRY(Polygon, 4326)` using PostGIS if enabled; if not, store GeoJSON as `jsonb`.

#### 4.2.3 Fill climate data for all barangays and provinces

- Implement a climate downscaling pipeline: query NASA POWER or ERA5 at barangay centroid; if API limits prevent all 42k, sample and interpolate with IDW/kriging.
- For provinces, aggregate municipality data in PostgreSQL (not Python) and materialize the result.
- Remove the hard-coded `year = 2010` in map builders and allow `year` parameter with a sensible default (latest available).

#### 4.2.4 Build a coverage dashboard

- Add an admin endpoint or a `coverage_summary` table that reports: count of municipalities/barangays with climate, suitability, terrain, population, and demand data; date last updated; and data source.
- Expose a `/admin/coverage` API and a frontend coverage map.

---

## 5. EcoSim Improvements

### 5.1 Current EcoSim Flow

`ecosim.py` accepts a municipality/province/barangay, monthly consumption, and monthly bill, then:

1. Derives an `electricity_rate` from `bill / consumption`.
2. Fetches climate and terrain data.
3. Runs solar, wind, hydro, and geothermal calculators.
4. Computes a recommendation with `_calculate_option_summary` using a multiplicative suitability score.

### 5.2 Critical Issues

#### 5.2.1 Single national electricity rate assumption

`ecosim.py` does not use the user's actual DU or location-specific tariff. It computes rate from the bill, but this can be manipulated and does not capture time-of-use, lifeline, or net-metering rates.

**Recommendation**: add a `du_rate_schedule_id` or `province_id` lookup to `du_rate_schedules` table; default to the inferred rate only if no DU match is found; include transmission, distribution, and other charges in savings calculations.

#### 5.2.2 No rooftop or land-availability model

EcoSim estimates system size purely from generation and capacity factors. It does not ask for roof area, shading, orientation, or available land, which can make recommendations physically impossible.

**Recommendation**: add user inputs for roof area, orientation, tilt, shading factor, and available land/stream. Use these to constrain the maximum system size in `solar_output_calc.py` and `hydro_output_calc.py`.

#### 5.2.3 Geothermal recommended for households is misleading

Geothermal is utility-scale and should not appear in the household recommendation. The code currently filters `geothermal` out of `household_options` (good), but the `options` array still includes it, and the explanation may confuse users.

**Recommendation**: clearly label geothermal as "utility-scale, not recommended for household installation" and show it separately only for informational purposes.

#### 5.2.4 Fixed cost constants and payback period

`COST_PER_KW_SOLAR`, `COST_PER_KW_WIND`, `COST_PER_KW_HYDRO`, `COST_PER_KW_GEOTHERMAL` are hard-coded in `ecosim.py`. They do not reflect current market prices, financing, subsidies, or O&M costs. Payback is computed with simple payback without discounting or inflation.

**Recommendation**:

- Replace constants with a `cost_benchmarks` table with `source`, `date`, `technology`, `cost_php_per_kw`, `currency`, `region`, and `confidence`.
- Add financing inputs (loan term, interest rate, down payment) and compute **Net Present Value (NPV)**, **Internal Rate of Return (IRR)**, **Levelized Cost of Energy (LCOE)**, and **discounted payback**.
- Add O&M escalation and inverter replacement at year 10–12.

#### 5.2.5 Desired-savings logic is ambiguous

`desired_savings` parameter is accepted but its effect is unclear in the code reviewed.

**Recommendation**: define desired savings as a target percentage of bill offset; use it to size the system to meet that target, capped by consumption and available area.

#### 5.2.6 No uncertainty or confidence intervals

The recommendation is a single point estimate. Users receive no range for generation, savings, or payback.

**Recommendation**: add Monte Carlo or sensitivity analysis: vary irradiance, equipment cost, tariff escalation, and capacity factor within distributions; report P10/P50/P90 for generation and payback.

---

## 6. Calculation Accuracy Improvements

### 6.1 Solar

Current implementation (`solar_output_calc.py`) uses:

```python
Output = kWp * irradiance_kwh_m2_day * performance_ratio
monthly_output = daily_output * days_in_month
```

with temperature factor, dust loss, and humidity degradation.

#### Issues

- **Irradiance input**: `allsky_sfc_sw_dwn` is treated as plane-of-array (POA) irradiance. It is actually GHI (global horizontal). For fixed-tilt systems, this overestimates output unless the array is horizontal.
- **Temperature factor**: uses a simple 0.4% per °C derating but does not use module-specific `NOCT` or wind-induced cooling.
- **Dust/soiling**: uses a heuristic wind-speed mapping; not validated.
- **Humidity degradation**: uses a humidity factor that is not standard in PV literature.
- **Performance ratio**: combines many losses into a single factor without transparency.

#### Recommendations

1. **Use GHI/DNI/DHI and a transposition model** (Perez, Hay-Davies, or Reindl) to compute POA irradiance for user-specified tilt and azimuth.
2. **Use PVLIB or a validated photovoltaic model** for temperature and DC/AC conversion.
3. **Replace the ad-hoc dust and humidity losses with**: soiling ratio from CAMS AOD + rainfall cleaning; humidity losses included in PID or corrosion warranty, not a generic multiplier.
4. **Split losses explicitly**: inverter efficiency, mismatch, wiring, shading, soiling, temperature, availability, degradation.
5. **Use a temperature-corrected module model**: `P = P_STC * (1 + γ * (T_cell - 25))` with `T_cell = T_amb + (G_POA / 800) * (NOCT - 20) * (1 - η/0.9)`.
6. **Include degradation**: 0.5–0.8% per year for crystalline silicon.
7. **Reference standards**: IEC 61215, IEC 61724 (PV monitoring), PVsyst validation practices.

### 6.2 Wind

Current implementation (`wind_output_calc.py`):

```python
Power = 0.5 * rho * A * V^3 * Cp * eta * capacity_factor
```

uses an average rotor radius, average Cp, and a fixed air density of 1.225 kg/m³.

#### Issues

- **Wind speed extrapolation**: assumes a power-law with fixed coefficient from 10 m to hub height. This is not valid for all roughness classes.
- **No turbine power curve**: uses a theoretical Cp and capacity factor instead of a manufacturer power curve.
- **Air density**: uses sea-level standard; should be corrected for elevation and temperature.
- **No wake, terrain, or roughness effects**: municipalities are not flat homogeneous sites.

#### Recommendations

1. **Obtain wind speed at hub height** from Global Wind Atlas or Renewables.ninja; if only 10 m data, use the log-law with roughness length from land cover, or use the Hellmann power-law with site-specific exponent.
2. **Use actual turbine power curves** from `turbine_power_curves` table.
3. **Compute air density**: `ρ = P / (R_specific * T)` using surface pressure and temperature from NASA POWER/ERA5.
4. **Use a Weibull distribution** for wind speed if hourly data unavailable: `A = ws_mean / Γ(1+1/k)` with typical `k=1.5–2.5` for Philippines.
5. **Apply a capacity factor** derived from the power curve and Weibull PDF, not a hand-picked 25% or 30%.
6. **References**: IEC 61400-12 (power performance), IEC 61400-1 (design), Manwell et al. *Wind Energy Explained*.

### 6.3 Hydropower

Current implementation (`hydro_output_calc.py`) uses the Rational Method to estimate runoff and then flow rate, then power.

#### Issues

- **Rational Method** is for peak storm runoff, not continuous streamflow.
- **40% environmental flow reserve** is a static multiplier with no ecological basis.
- **Head** uses municipality min/max elevation, not actual intake-to-tailrace head.
- **Runoff coefficient** is a hard-coded lookup by slope only; ignores land cover and soil.

#### Recommendations

1. **Replace Rational Method with continuous streamflow** from GRDC or a regional hydrological model (SWAT, HEC-HMS, or FAO-based regionalization).
2. **Use flow-duration curves**: compute firm energy from Q90 and average energy from mean flow.
3. **Compute hydraulic head from DEM river profile** (HydroSHEDS/SRTM) and add penstock head loss.
4. **Use actual turbine efficiency curves** for Pelton, Francis, cross-flow, or Kaplan turbines.
5. **Environmental flow**: implement Q7.10 or Tennant method (10% mean annual flow for minimum) with seasonal variation.
6. **References**: ASME/AWEA micro-hydro guidelines; FAO; Butchers et al. (2021) small-hydro siting; USGS guidelines.

### 6.4 Geothermal

Current implementation (`geothermal/features.py`) uses AHP over heat flow, fault proximity, volcano proximity, aquifer score, and temperature.

#### Issues

- **Sparse heat-flow data**: only a few IHFC measurements; IDW with 300 km radius is not meaningful.
- **Reservoir depth and flow rate are assumed**: default 2000 m depth and inferred flow from permeability.
- **Output formula** `Q = m_dot * Cp * ΔT` is correct for thermal power, but converting to electric power with a fixed 12–15% efficiency ignores resource temperature, brine chemistry, and plant configuration.
- **No surface exploration risk**: proximity to volcanoes/faults is a necessary but not sufficient condition.

#### Recommendations

1. **Classify resources by temperature** (low <150°C, medium 150–200°C, high >200°C) using estimated reservoir temperature from heat flow and gradient.
2. **Use volumetric methods (Monte Carlo)** for resource estimation: stored-heat method or power-density method.
3. **Integrate PHIVOLCS geothermal prospectivity maps** and well data.
4. **Report confidence scores** based on data density and source quality.
5. **Do not report household-scale geothermal recommendations**; keep it as a regional resource indicator.
6. **References**: USGS Geothermal Resource Assessment; Muffler (1979) stored-heat method; Williams et al. (2008) volumetric method; DOE-PHIVOLCS geothermal maps.

### 6.5 Economic and Carbon Calculations

- **CO₂ factor**: uses `0.6835 kg/kWh` DOE national grid emission factor. This is reasonable but should be updated annually and possibly split by grid (Luzon/Visayas/Mindanao) or DU.
- **Payback**: simple payback is fine for a quick screen, but add NPV, IRR, LCOE for robust financial analysis.
- **Tariff escalation**: no escalation assumption; add 2–5% annual escalation.
- **Lifetimes**: not explicitly modeled; use 25 years for solar, 20 for wind, 30+ for hydro, 30 for geothermal.

### 6.6 Weighted Multi-Criteria Scoring

Current formula in `ecosim.py`:

```python
suitability_score = source_score * (0.4 + 0.6 * energy_ratio) * 100
```

is multiplicative, which is better than additive but still opaque to users.

**Recommendation**: document the scoring in the UI; allow user-defined weights (economic, environmental, resource); use a proper MCDA framework (AHP or PROMETHEE) with sensitivity analysis; store weights in `mcda_weights` table and expose an admin UI.

---

## 7. Forecasting Improvements

### 7.1 Current Forecasting Setup

`app/ml/predictor.py` loads pre-computed ARIMA(1,1,1) forecasts from CSV files in `DOE_Data_Extracted/data_v2_preprocessed/`. The model is trained on national total consumption and peak demand from 2003–2020 and evaluated on 2021–2024. Forecasts are served statically; no retraining occurs at runtime.

### 7.2 Strengths

- Pre-computed forecasts avoid runtime ML training costs.
- Model comparison CSV is exposed via `/model-comparison`.
- `forecast_cache` table has been extended with `geo_level`/`geo_id` columns for future sub-national forecasts.

### 7.3 Issues

#### 7.3.1 Single ARIMA model with no exogenous variables

A univariate ARIMA(1,1,1) cannot capture:

- GDP growth, population, and electrification.
- Weather-driven demand variation.
- Policy shocks (e.g., new RE mandates, coal retirements).
- Economic crises, pandemics, or large industrial loads.

**Recommendation**: move to a **SARIMA/ARIMAX** or a hybrid model:

- **Baseline**: `SARIMA(1,1,1)(1,1,1)12` for monthly data.
- **Exogenous variables**: GDP, population, temperature (cooling degree days), industrial production index, fuel prices.
- **ML ensemble**: LightGBM/XGBoost on lagged values, calendar features, and exogenous regressors; combine with SARIMA in a stacking ensemble.
- **Probabilistic forecasting**: report prediction intervals (P10/P50/P90) and use `statsmodels`/`sktime` or `Prophet` for uncertainty.

#### 7.3.2 No forecast reconciliation or sub-national models

EnergyHub only forecasts national consumption/peak. Province/municipality forecasts would improve planning and justify the `geo_level`/`geo_id` schema extension.

**Recommendation**: implement **hierarchical forecast reconciliation**:

- Bottom-up: train models for each region/province; reconcile to national.
- Top-down: disaggregate national forecast using historical shares.
- Middle-out: optimal reconciliation via `scikit-hts` or `hierarchicalforecast`.

#### 7.3.3 Static CSV artifacts are not versioned or retrained automatically

The ARIMA notebooks (`DOE_arima_forecasting.ipynb`) are not part of an automated pipeline. If DOE releases a new annual report, forecasts remain stale.

**Recommendation**:

- Store model artifacts in a versioned object store (DigitalOcean Spaces / S3 / Supabase Storage).
- Add a scheduled job (GitHub Actions / Airflow / Prefect / cron on a DigitalOcean worker) that:
  1. Downloads latest DOE/NGCP data.
  2. Runs preprocessing and model training.
  3. Validates model against hold-out set and model comparison baseline.
  4. Uploads new artifacts and invalidates `forecast_cache`.

#### 7.3.4 No backtesting or model monitoring

`model_comparison_results.csv` is static. There is no continuous tracking of MAE/RMSE/MAPE as new data arrives.

**Recommendation**: implement a backtesting framework using `sktime`/`darts` with expanding-window cross-validation and log metrics to a `forecast_model_runs` table or MLflow/W&B.

### 7.4 Recommended Data for Forecasting

| Feature | Source | Frequency | Confidence |
|---------|--------|-----------|------------|
| Historical demand/generation | DOE, NGCP | Annual/monthly | High |
| GDP by region | PSA | Quarterly/annual | High |
| Population | PSA | Annual | High |
| Cooling/heating degree days | NASA POWER / PAGASA | Monthly | High |
| Fuel/coal/gas prices | DOE, international indices | Monthly | Medium |
| Industrial production | PSA, DTI | Monthly | Medium |

### 7.5 References

- Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (free online).
- Taylor & Letham (2018), *Forecasting at scale* (Prophet).
- Ben Taieb et al. (2017), *Hierarchical Probabilistic Forecasting*.

---

## 8. GIS & Mapping Improvements

### 8.1 Current GIS Stack

- **Frontend**: `leaflet`, `react-leaflet`, `react-plotly.js`/`recharts` for charts.
- **Backend**: GeoJSON boundary files in `react-frontend/public/`, Supabase for point data, `geospatial_metadata` table for centroids/area.
- **Scripts**: `scripts/extract_centroids.py` computes centroids and area from GeoJSON.
- **Map data**: `EnergyHubService._build_renewable_potential_map` aggregates municipality scores by province and matches against GeoJSON province names using `_PROVINCE_NAME_MAP`.

### 8.2 Issues

#### 8.2.1 GeoJSON files in the frontend repository

Storing large GeoJSON (e.g., 1,618 municipality polygons, 42,000 barangays) in `react-frontend/public` bloats the frontend bundle and makes dynamic updates difficult. Some maps may load 5–20 MB of vector data into the browser.

**Recommendation**:

- Serve vector tiles (MVT) from a tile server or static tileset (e.g., `tippecanoe` + DigitalOcean Spaces CDN, or Mapbox/MapTiler if budget allows).
- For a budget setup, pre-generate **TopoJSON** or **simplified GeoJSON** and split by province; lazy-load the current province only.
- Add a `map_layers` table with `level`, `geojson_url`, `tile_url`, `last_updated`, `checksum`.

#### 8.2.2 Map endpoint performance

`_build_renewable_potential_map` and `_build_barangay_potential_map` fetch thousands of rows and build the response in Python. The barangay map has ~42,000 items and is cached only for 1 hour; a cold request can take several seconds and hundreds of MB.

**Recommendation**:

- Use **materialized views** in PostgreSQL for province/municipality map data; refresh them after data updates.
- For barangays, serve vector tiles with property attributes embedded, not 42,000 JSON items.
- Add query parameters (`bbox`, `zoom`, `province_id`) so the frontend only fetches visible features.

#### 8.2.3 Projection and area issues

`scripts/extract_centroids.py` uses a rough equirectangular approximation for area. This is inaccurate for municipalities near the equator (the Philippines spans ~5–20°N, so area error is moderate but not negligible).

**Recommendation**: use an equal-area projection (EPSG:32651 for Luzon, 32652 for Visayas/Mindanao) with `pyproj`/`geopandas`.

#### 8.2.4 Hard-coded province name mapping

`_PROVINCE_NAME_MAP` in `energyhub.py` is a brittle, manual mapping between DOE/Supabase names and GeoJSON `adm2_en` names.

**Recommendation**: use **PSGC codes** as the canonical join key and attach `psgc_code` to each GeoJSON feature. This eliminates name-based matching.

#### 8.2.5 Choropleth metric limitations

The map currently supports `renewable_potential`, `solar_potential`, `wind_potential`, `hydro_potential`, `geothermal_potential` at province/municipality/barangay. It does not support:

- Time-series maps (year slider).
- Scenario overlays (e.g., grid capacity, transmission lines).
- Uncertainty/confidence maps.

**Recommendation**: add a generic `/map-data?metric=X&level=Y&year=Z` endpoint; return standardized `feature_id`, `value`, `confidence`, `source` fields; add a year slider in the frontend.

### 8.3 Recommended GIS Data Sources

| Dataset | Source | Use | Update |
|---------|--------|-----|--------|
| Administrative boundaries | PSA, GADM, PhilAtlas | Choropleth base layer | Annual |
| SRTM/NAMRIA DEM | USGS, NAMRIA | Elevation, slope, hydropower head | Static |
| HydroSHEDS | WWF | River network, watershed, flow accumulation | Static |
| Grid/transmission lines | NGCP, OpenStreetMap | Grid integration and curtailment risk | Occasional |
| Protected areas | DENR, UNEP-WCMC | Exclusion zones for siting | Annual |
| Nighttime lights | NASA VIIRS DNB | Demand proxy | Monthly |

### 8.4 References

- Longley et al., *Geographic Information Systems and Science*.
- OSGeo / PostGIS documentation for spatial indexing and MVT.
- Mapbox / Tippecanoe for vector tile generation.

---

## 9. AI/RAG Improvements

### 9.1 Current RAG Pipeline

`rag_pipeline.py`:

- Loads a knowledge JSON (`rag_knowledge_base.json`) and builds a FAISS `IndexFlatIP` using `sentence-transformers` (default `all-MiniLM-L6-v2`).
- `retrieve_context` embeds the query, searches the index, and returns `top_k` chunks with cosine-similarity scores.
- `retrieve_with_filter` post-filters by `renewable_type` and `category`.
- `rag_knowledge_builder.py` aggregates scraped e-commerce products into knowledge chunks by equipment cost, installation cost, maintenance, components, capacity, etc.

`chat.py`:

- Calls `_retrieve_context` to get chunks.
- Builds a prompt with retrieved context and optional user context.
- Sends to Groq `llama-3.3-70b-versatile` with a system prompt that includes topic guardrails and source citation instructions.
- Returns the response with `retrieved_chunks`.

### 9.2 Strengths

- Semantic chunking with sentence-aware boundaries and rich metadata (`renewable_type`, `category`, `sources`).
- Knowledge is pre-aggregated rather than indexing raw product rows.
- System prompt explicitly restricts off-topic queries and requires citations.

### 9.3 Issues

#### 9.3.1 Embedding model is generic and not domain-tuned

`all-MiniLM-L6-v2` is a general-purpose model. It may miss technical terms like "micro-hydro", "Pelton turbine", "net metering", "FIT", and "interconnection".

**Recommendation**:

- Evaluate **domain-specific embedders** (e.g., `BAAI/bge-base-en`, `sentence-transformers/multi-qa-MiniLM-L6-dot-v1`, or fine-tune on energy/Philippines Q&A triplets).
- Fine-tune a small embedder using LUMI chat logs and synthetic Q&A pairs.
- Add a reranker (cross-encoder such as `cross-encoder/ms-marco-MiniLM-L-6-v2`) to improve top-k precision.

#### 9.3.2 FAISS index is in-process and memory-bound

The FAISS index (~11 MB) and chunks JSON (~5 MB) are loaded into a global variable on every worker. It cannot be shared across horizontal replicas and is not updated without redeploy.

**Recommendation**:

- For budget: keep FAISS but load lazily and mount the index from a shared volume (DigitalOcean Block Storage or Spaces) during startup.
- For scale: switch to a managed vector database such as **pgvector** in PostgreSQL (Supabase supports pgvector), **Pinecone**, **Weaviate**, or **Qdrant**.
- With pgvector, store chunks in a `rag_chunks` table with `embedding vector(384)` and use `pgvector` HNSW/IVFFlat indexes.

#### 9.3.3 No retrieval evaluation or metrics

There is no test set to measure precision, recall, or answer relevance.

**Recommendation**:

- Create an evaluation set of 50–100 representative questions with expected source documents.
- Implement retrieval metrics: `Recall@k`, `MRR`, `NDCG`.
- Add user feedback (thumbs up/down) on chat responses and log it.

#### 9.3.4 Chunking may lose tabular/numerical structure

Aggregated price ranges are stored as prose ("Prices range from PHP X to PHP Y"). Tables and numbers can be hard for the LLM to reason over.

**Recommendation**:

- Add structured metadata to chunks: `min_price`, `max_price`, `median_price`, `currency`, `region`, `date`, `product_type`.
- Generate **small structured tool responses** (e.g., JSON) for price queries, in addition to prose answers.
- Use **retrieval-augmented generation with tool use**: the LLM can call a "price_lookup" function.

#### 9.3.5 Citation quality and hallucination risk

The system prompt asks for `[Source N: Title]` citations, but the LLM may hallucinate sources or misattribute facts. The chat route returns `retrieved_chunks`, but the final answer is not verified against them.

**Recommendation**:

- Implement **constrained generation** or post-processing: extract all claims and verify each against retrieved chunks; flag claims not supported by context.
- Use a smaller model to generate citations first, then the LLM to synthesize.
- Add a "confidence" score and "not found" fallback for queries outside the knowledge base.

#### 9.3.6 No chat history or session persistence

`chat.py` accepts `session_id` but does not persist messages; the `/chat/sessions` endpoints return empty.

**Recommendation**: store messages in the existing `chat_sessions`/`chat_messages` tables; use conversation context (sliding window or summarized) for follow-up questions.

#### 9.3.7 Prompt injection and safety

The system prompt tries to reject off-topic queries, but there is no input sanitization, prompt injection testing, or output moderation.

**Recommendation**: add input/output moderation via OpenAI moderation API, Azure Content Safety, or a local guardrails model; run prompt injection test suites.

### 9.4 RAG Knowledge Gaps

- **Policy/regulatory documents**: RE Act, net metering rules, ERC resolutions, DOE circulars.
- **Local installer and supplier directory**: not currently in the knowledge base.
- **Case studies and actual performance data**: rooftop PV performance in the Philippines.
- **Geothermal/Hydro/Wind specific FAQs**: e.g., environmental permits, EIAs, land rights.

### 9.5 References

- Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*.
- Gao et al. (2023), *RAG-Fusion / Search-Respond-Verify*.
- LangChain / LlamaIndex documentation for agentic RAG and vector store integration.

---

## 10. Data Engineering Improvements

### 10.1 Current Data Pipeline

Data flows through several ad-hoc scripts and notebooks:

- `scripts/extract_centroids.py` → `geospatial_metadata`
- `municipality_suitability_builder.py` → `municipalities` / `*_suitability`
- `rag_knowledge_builder.py` → `rag_knowledge_base.json`
- `DOE_Data_Extracted/` notebooks → CSV artifacts
- `scraped_data/` scripts → `cleaned_products_master.csv`

### 10.2 Issues

#### 10.2.1 No orchestration or scheduling

ETL steps are manual or triggered on deploy. There is no job scheduler, dependency graph, retry logic, or observability.

**Recommendation**: adopt an orchestrator appropriate for your budget:

- **Budget**: GitHub Actions scheduled workflows (free for public repos, limited minutes for private) calling Python scripts.
- **Small scale**: **Prefect** (open-source, easy to deploy on a small DigitalOcean droplet) or **Dagster**.
- **Medium scale**: **Apache Airflow** (more mature, heavier).
- Define DAGs for: climate ingestion → suitability build → forecast retrain → RAG index rebuild.

#### 10.2.2 No data versioning or lineage

CSV files in `DOE_Data_Extracted/` and `local_data/` are not versioned. It is impossible to reproduce an old forecast or map tile.

**Recommendation**:

- Use **DVC** (Data Version Control) for large files, or store them in versioned object storage (DigitalOcean Spaces with lifecycle policies).
- Add `data_version` and `source_url` columns to all derived tables.
- Maintain a `data_lineage` table: `source`, `destination`, `transform`, `run_id`, `started_at`, `finished_at`, `rows`, `checksum`.

#### 10.2.3 Quality checks are missing

There are no automated schema, range, or referential-integrity checks after ingestion. Bad data can silently corrupt maps and recommendations.

**Recommendation**: implement a `pandera`/`great_expectations` validation step for each pipeline stage:

- Range checks: `allsky_sfc_sw_dwn > 0`, `ws10m >= 0`.
- Referential checks: every `municipality_id` in climate tables exists in `municipalities`.
- Uniqueness: `psgc_code` unique per admin level.
- Coverage: count of municipalities with climate data per province.

#### 10.2.4 Scrapers are fragile

E-commerce scrapers depend on page structure and may violate terms of service.

**Recommendation**:

- Use official APIs or data feeds where available (Lazada/Shopee APIs for sellers, supplier price lists).
- For scraping, use **Playwright** with rotating user-agents and respect `robots.txt`.
- Store raw HTML/JSON snapshots for reproducibility and compliance.
- Add a `price_data_sources` table with `source`, `url`, `date_collected`, `license`.

#### 10.2.5 No data catalog or documentation

New contributors cannot easily understand which dataset feeds which table.

**Recommendation**:

- Create a `data_catalog.md` and/or a `datasets` table in the database with: name, description, source URL, update frequency, schema, last_update, license.
- Add inline comments and READMEs in `scripts/` and `DOE_Data_Extracted/`.

### 10.3 Recommended Pipeline Architecture (Budget)

```
Sources (NASA POWER, DOE PDFs, PSA CSVs, OSM, GEE)
    │
    ▼
Landing (raw files in DigitalOcean Spaces / S3)
    │
    ▼
Bronze (raw tables in PostgreSQL, e.g., raw_nasa_power, raw_doe_stats)
    │
    ▼
Silver (cleaned, deduplicated, validated: municipality_climate_monthly, national_energy_annual)
    │
    ▼
Gold (aggregated, modeled: suitability scores, forecasts, knowledge chunks)
    │
    ▼
API + Cache + Frontend
```

This medallion-style architecture makes debugging and auditing easier.

### 10.4 References

- Kleppmann, *Designing Data-Intensive Applications*.
- DVC and Great Expectations documentation.
- Prefect / Dagster / Airflow documentation.

---

## 11. Performance Optimization

### 11.1 Observed Bottlenecks

From code review, the following performance issues are evident:

1. **Large in-memory data fetches**: `energyhub.py` and `municipality_suitability_builder.py` use `.limit(10000)` and fetch all municipalities/provinces/climate/suitability rows into Python. As data grows, these queries will OOM or time out.
2. **Barangay map endpoint**: ~42,000 items serialized to JSON on every cold cache miss; Redis caches for only 1 hour.
3. **Heavy startup**: FAISS index + knowledge base + EnergyHubML CSVs load on app startup, causing slow cold starts and high memory usage.
4. **Frequent Supabase round-trips**: `get_or_compute_province_climate` loops over each municipality and calls `get_climate_data` individually, leading to N+1 API calls.
5. **No CDN / static compression**: GeoJSON/JSON assets in `react-frontend/public` are served from the app origin.
6. **CPU-bound work in async routes**: Pandas/FAISS/NumPy operations block the FastAPI event loop.
7. **No connection pooling**: `httpx.Client(timeout=10.0)` is used in `SupabaseRestClient` but not in all service code; many functions create new clients.

### 11.2 Optimization Recommendations

| Priority | Action | Expected Impact |
|----------|--------|-----------------|
| High | Replace `.limit(10000)` with paginated SQL queries and push aggregation to PostgreSQL (materialized views for maps). | Reduces memory and query time by orders of magnitude. |
| High | Use vector tiles or chunked GeoJSON for barangay maps; never return 42,000 items at once. | Eliminates multi-second cold requests and large Redis payloads. |
| High | Lazy-load FAISS index/ML CSVs on first request or move to a separate model worker. | Faster cold starts; lower baseline memory. |
| Medium | Add `asyncio.to_thread` for Pandas/FAISS or convert CPU-heavy endpoints to sync `def`. | Prevents event-loop blocking. |
| Medium | Add HTTP caching headers and a CDN (DigitalOcean Spaces CDN, Cloudflare free tier) for static assets. | Reduces bandwidth and improves frontend load times. |
| Medium | Use `asyncpg`/`supabase-py` async connection pool and `httpx.AsyncClient` for Supabase. | Reduces connection overhead. |
| Low | Minify and split frontend bundle (Vite code-splitting). | Faster initial page load. |
| Low | Add request/response Gzip/Brotli compression. | Smaller payloads. |

### 11.3 Load & Stress Testing

**Recommendation**: add a `lumi_tests/` suite with `pytest`, `pytest-benchmark`, and `locust`/`k6` to:

- Profile map endpoints under concurrent users.
- Measure cold-start time and memory for the Docker container.
- Validate cache hit/miss behavior.

### 11.4 Caching Strategy Refinement

- Increase barangay map TTL to at least 24 hours and add a background job to refresh it.
- Cache `energyhub/overview` and `ai-insight` with short TTLs (5–15 minutes) because they are expensive.
- Use cache tags so a data update invalidates only affected keys.

---

## 12. Missing Features

This section lists high-value features not currently implemented but needed for a production-grade, scientifically credible platform.

### 12.1 User-Facing Features

1. **User registration and saved simulations**: `profiles` and `user_roles` tables exist, but EcoSim does not persist user scenarios or allow comparisons.
2. **Bill upload / smart-meter integration**: allow users to upload a Meralco/DU bill image (OCR) or enter net-metering data.
3. **Sensitivity / what-if analysis**: sliders for tariff escalation, equipment cost, financing terms, inflation.
4. **LCOE and NPV dashboard**: financial metrics beyond simple payback.
5. **Historical comparison**: compare a municipality's renewable potential over multiple years.
6. **Climate risk overlay**: typhoon/flood/drought hazard maps from NOAH/PAGASA for siting resilience.
7. **Grid-connection and interconnection checker**: estimate distance to nearest transmission line/substation and rough interconnection cost.
8. **Installer / supplier marketplace directory**: curated list of local installers with ratings and service areas.
9. **Multi-language support**: Tagalog/Visayan/Cebuano localizations for accessibility.
10. **Mobile responsiveness and PWA**: ensure maps and charts work on mobile devices; add offline map caching.

### 12.2 Admin / Operational Features

1. **Data coverage dashboard** (see Section 4.2.4).
2. **Admin UI to update MCDA weights** and recompute suitability scores.
3. **ETL run log and data lineage viewer**.
4. **Model registry and experiment tracking** (`ml_model_registry` table exists but appears unused; integrate MLflow/W&B).
5. **A/B testing for LLM prompts** and RAG configurations.
6. **Audit log for all data and admin changes**.

### 12.3 Scientific / Engineering Features

1. **PV yield simulation engine**: hourly PV simulation using PVLIB or Renewables.ninja.
2. **Wind resource assessment tool**: Weibull fitting, power-curve selection, wake loss estimation.
3. **Hydrological modeling module**: flow-duration curves and design flood estimates.
4. **Geothermal volumetric resource estimator**: Monte Carlo stored-heat method.
5. **Grid integration / curtailment screening**: distance to substation and existing generation capacity.
6. **Lifecycle carbon accounting**: embodied emissions of equipment, not just grid displacement.

### 12.4 Priority Ranking

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| User accounts + saved simulations | High | Medium | P1 |
| Sensitivity / what-if | High | Medium | P1 |
| LCOE/NPV dashboard | High | Medium | P1 |
| Data coverage dashboard | High | Low | P1 |
| PVLIB hourly yield | High | High | P2 |
| Hydrology flow-duration module | High | High | P2 |
| Installer/supplier directory | Medium | Medium | P2 |
| Multi-language | Medium | Medium | P3 |
| Grid-connection checker | High | Medium | P2 |
| Climate risk overlay | Medium | High | P3 |

---

## 13. Scientific & Engineering Validation

### 13.1 Need for Validation

LUMI makes recommendations that affect household investment and policy. It is essential that calculations are validated against authoritative sources and standards.

### 13.2 Recommended Validation Steps

1. **Cross-validate solar output**:
   - Pick 5 representative Philippine cities (Manila, Cebu, Davao, Iloilo, Baguio).
   - Compute annual PV yield with LUMI and compare to NREL PVWatts, Global Solar Atlas, and Renewables.ninja.
   - Target: annual energy within ±10% of PVWatts for the same location/system.

2. **Cross-validate wind output**:
   - Pick locations with known PAGASA anemometer data or operating wind farms (Bangui, Pililla).
   - Compare capacity factor from LUMI to Global Wind Atlas and measured plant data.

3. **Cross-validate hydropower**:
   - Compare estimated flow to GRDC/NAMRIA gauge data where available.
   - Validate head estimates with SRTM-derived river profiles.

4. **Cross-validate geothermal**:
   - Compare suitability scores to DOE-PHIVOLCS geothermal prospectivity maps and operating plant locations.
   - Do not present household-scale geothermal output as actionable.

5. **Economic validation**:
   - Compare LUMI payback/LCOE to published Philippine case studies (e.g., Taduran & Piao 2025 for Tarlac PV).
   - Validate tariffs against Meralco and Visayan Electric rate filings.

6. **MCDA validation**:
   - Use AHP consistency ratio (CR < 0.1) when soliciting expert weights.
   - Sensitivity test weights and compare ranking to published GIS-MCDA studies for Philippine RE siting.

### 13.3 Standards and Methodologies to Adopt

| Domain | Standard / Methodology |
|--------|------------------------|
| Solar PV | IEC 61215, IEC 61724, PVsyst validation, ASHRAE/NSRDB TMY data |
| Wind | IEC 61400-12 (power performance), IEC 61400-1 (design), WAsP/WRF for resource |
| Hydro | FAO small-hydro, ASME/AWEA micro-hydro, USGS streamflow methods |
| Geothermal | USGS circular 790/790-revised, Muffler (1979), Williams et al. (2008) |
| MCDA | Saaty AHP consistency ratio, PROMETHEE/GAIA sensitivity, Asadi et al. (2023) GIS-AHP |
| Emissions | IPCC 2006 Guidelines, DOE National Grid Emission Factor |
| Financial | IEC 61194 / NREL LCOE methodology, discounted cash flow (NPV/IRR) |

### 13.4 Uncertainty Quantification

Every recommendation should report confidence:

- **Data confidence**: based on source density, recency, and resolution.
- **Model confidence**: based on validation RMSE/MAPE.
- **Scenario confidence**: P10/P50/P90 for generation, savings, and payback.

**Recommendation**: add a `confidence` object to every EcoSim and EnergyHub response with `data`, `model`, and `overall` scores and plain-language caveats.

---

## 14. Implementation Roadmap

The roadmap is organized into phases. Each phase has a primary goal and a list of concrete deliverables. Priorities reflect impact, effort, and dependency order.

### Phase 1: Foundation (Weeks 1–4) — Accuracy & Stability

**Goal**: fix the most glaring data and calculation inaccuracies, and make the system stable enough for real users.

| # | Task | Owner | Effort | Files/Tools |
|---|------|-------|--------|-------------|
| 1.1 | Refactor `municipalities` table and use standalone suitability tables; update all service reads. | Backend + DB | Medium | `municipality_suitability_builder.py`, `energyhub.py`, `ecosim.py`, `0001_geospatial_architecture.sql` |
| 1.2 | Add PostgreSQL materialized views for province/municipality map data. | Backend + DB | Low | SQL migrations |
| 1.3 | Paginate and push aggregation to DB; remove `.limit(10000)` patterns. | Backend | Medium | `energyhub.py`, `municipality_suitability_builder.py` |
| 1.4 | Replace hard-coded cost constants with `cost_benchmarks` table and DU tariff lookup. | Backend + DB | Medium | `ecosim.py`, `solar_output_calc.py`, etc. |
| 1.5 | Fix solar irradiance model: use GHI/DNI/DHI + transposition; adopt temperature-corrected module model. | Backend | High | `solar_output_calc.py` |
| 1.6 | Add confidence fields to EcoSim and EnergyHub responses. | Backend/Frontend | Low | API schemas |
| 1.7 | Containerize FastAPI and frontend with Docker; add `docker-compose.yml`. | DevOps | Medium | New files |
| 1.8 | Add startup health checks and fail-fast config validation. | Backend | Low | `main.py`, `config/settings.py` |

### Phase 2: Data Expansion (Weeks 5–10) — Coverage & Resolution

**Goal**: fill critical data gaps and improve geographic/scientific coverage.

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 2.1 | Integrate Global Solar Atlas / PVWatts and Global Wind Atlas / Renewables.ninja data. | Data Eng | High |
| 2.2 | Add municipal population and nighttime-lights demand disaggregation. | Data Eng | Medium |
| 2.3 | Build hydrology pipeline: HydroSHEDS + streamflow regionalization. | Data Eng + Backend | High |
| 2.4 | Update geothermal dataset: PHIVOLCS faults/volcanoes + DOE well data. | Data Eng | Medium |
| 2.5 | Add PSGC-code alignment and coverage dashboard. | Backend + DB | Medium |
| 2.6 | Implement automated DOE/PSA data ingestion and versioning. | Data Eng | Medium |

### Phase 3: Intelligence (Weeks 11–16) — Forecasting & RAG

**Goal**: improve predictive and AI capabilities.

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 3.1 | Build SARIMA/ARIMAX/ensemble national forecast with exogenous variables. | ML Eng | High |
| 3.2 | Add probabilistic prediction intervals and backtesting. | ML Eng | Medium |
| 3.3 | Implement sub-national forecast reconciliation. | ML Eng | High |
| 3.4 | Move RAG to pgvector or managed vector DB; add reranking. | ML Eng + Backend | Medium |
| 3.5 | Add retrieval evaluation and user feedback loop. | ML Eng | Low-Medium |
| 3.6 | Implement chat history and session persistence. | Backend | Medium |
| 3.7 | Add citation verification / constrained generation. | ML Eng | Medium |

### Phase 4: Production Readiness (Weeks 17–22) — Scale & Operations

**Goal**: make the platform reliable, observable, and scalable on DigitalOcean.

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 4.1 | Set up DigitalOcean infrastructure (see Section 15). | DevOps | Medium |
| 4.2 | Implement CI/CD with GitHub Actions → DO Container Registry → App Platform / Droplet. | DevOps | Low-Medium |
| 4.3 | Add monitoring, logging, and alerting (Prometheus/Grafana/Loki or DO Monitoring). | DevOps | Medium |
| 4.4 | Add rate limiting, CORS hardening, and security headers. | Backend | Low |
| 4.5 | Add automated data-quality checks with Pandera/Great Expectations. | Data Eng | Medium |
| 4.6 | Implement ETL orchestration (Prefect/Airflow/GitHub Actions). | Data Eng | Medium |
| 4.7 | Load/stress testing with Locust/k6 and optimization. | QA/Backend | Medium |
| 4.8 | Documentation: data catalog, API docs, deployment runbook. | Docs | Low |

### Phase 5: Advanced Features (Weeks 23+) — Differentiation

- Hourly PV/wind simulation with PVLIB/Renewables.ninja.
- Hydrology flow-duration module.
- Grid-connection and interconnection cost estimates.
- LCOE/NPV/IRR full financial dashboard.
- Climate risk overlays and resilience scoring.
- Multi-language UI.

### 14.1 Roadmap Summary Table

| Phase | Duration | Primary Outcome | Budget Impact |
|-------|----------|-----------------|---------------|
| 1 | 1–4 weeks | Stable, more accurate core platform | Low |
| 2 | 5–10 weeks | Rich, authoritative datasets | Medium (data/apis) |
| 3 | 11–16 weeks | Reliable forecasts and AI answers | Medium |
| 4 | 17–22 weeks | Production-ready, scalable DO deployment | Medium-High |
| 5 | 23+ weeks | Differentiated advanced features | Medium |

---

## 15. DigitalOcean Deployment & Budget-Friendly Sizing

### 15.1 Deployment Goals

- Host the FastAPI backend and optionally the React frontend on DigitalOcean.
- Keep the database/cache either on DigitalOcean (managed) or continue using existing Supabase/Upstash if budget is tight.
- Provide a clear, budget-friendly configuration that can scale as usage grows.
- Optimize cold-start, memory, and compute usage for the LUMI workload.

### 15.2 Application Workload Profile

LUMI is **data-heavy and startup-heavy** rather than request-heavy:

- FastAPI backend loads a FAISS index (~11 MB), knowledge JSON (~5 MB), and several Pandas CSVs into memory.
- EcoSim/EnergyHub queries Supabase/Postgres and performs vector search or Pandas aggregation.
- Map endpoints can serialize 1,600–42,000 items if not optimized (must be fixed before production).
- RAG uses `sentence-transformers`/`FAISS` (CPU-bound); embedding calls may take 100–500 ms.
- Forecasting is static CSV serving, so CPU cost is low.

Because of this, the minimum viable droplet should have **at least 1 GB RAM**, and 2 GB is strongly recommended for a stable production deployment.

### 15.3 Recommended Deployment Options

#### Option A: Minimum Budget (Hybrid — compute on DO, DB/cache on existing Supabase/Upstash)

Use this if you already have Supabase and Upstash working and want the cheapest path to DO-hosted compute.

| Component | DO Service | Spec | Estimated Monthly Cost |
|-----------|-----------|------|-------------------------|
| Frontend (static) | App Platform static site or Vercel/Netlify | — | $0–$5 (DO) or free (Vercel) |
| Backend API | Basic Droplet (regular or premium Intel/AMD) | 1 vCPU / 2 GB RAM / 25 GB SSD | $12–$18/mo |
| Worker/ETL (optional) | Same droplet as backend, separate process | Shared resources | $0 extra |
| Database | Existing Supabase free/pro tier | — | $0–$25/mo |
| Cache | Existing Upstash Redis free tier | — | $0 |
| Object storage | Spaces (for artifacts, exports) | 250 GB + egress | $5/mo + egress |
| CDN | Spaces CDN or Cloudflare free | — | $0–$5/mo |
| Domain + Load balancer | Optional | — | $0–$12/mo |
| **Total** | | | **~$20–$45/mo** |

**Notes for Option A**:

- Run the FastAPI app in a Docker container on the Droplet with `gunicorn` + `uvicorn.workers.UvicornWorker`.
- Use `nginx` as a reverse proxy and static file server; enable Gzip/Brotli and caching headers.
- Mount a persistent volume or use `git clone`/`docker build` for artifacts; keep data artifacts in Spaces.
- For ETL, use `systemd` timer or `cron` inside the same droplet to run Python scripts nightly/weekly.

#### Option B: Full DigitalOcean Stack (Managed DB + Redis)

Use this if you want everything on DO and better reliability/scaling.

| Component | DO Service | Spec | Estimated Monthly Cost |
|-----------|-----------|------|-------------------------|
| Frontend | App Platform static site or Droplet+Nginx | — | $0–$5 |
| Backend API | Droplet (Premium AMD/Intel) | 1 vCPU / 2 GB RAM / 50 GB SSD | $18/mo |
| Database | Managed PostgreSQL | 1 vCPU / 1 GB RAM / 10 GB | $15/mo |
| Cache | Managed Redis | 1 vCPU / 1 GB RAM / 10 GB | $15/mo |
| Object storage | Spaces | 250 GB | $5/mo |
| Worker/ETL | Separate Basic Droplet | 1 vCPU / 1 GB RAM | $6–$12/mo |
| Load balancer | DO Load Balancer (when scaling to 2+ backend droplets) | — | $12/mo |
| Monitoring | DO Monitoring (included) | — | $0 |
| Container Registry | DO Container Registry (basic) | — | $0–$5/mo |
| **Total** | | | **~$65–$100/mo** |

**Notes for Option B**:

- This is the minimum "serious" production stack on DO.
- Managed PostgreSQL and Redis remove operational burden and improve reliability.
- The backend droplet can later be horizontally scaled behind a load balancer.
- Use DO Container Registry to push Docker images from CI/CD.

#### Option C: App Platform Only (Serverless-ish)

Use this if you prefer not to manage droplets and accept higher per-resource cost for simplicity.

| Component | DO Service | Spec | Estimated Monthly Cost |
|-----------|-----------|------|-------------------------|
| Frontend | App Platform static site | — | $0–$5 |
| Backend | App Platform service | Basic / Pro instance with 1 GB RAM | $12–$25/mo per container |
| Database | Managed PostgreSQL | 1 GB | $15/mo |
| Cache | Managed Redis | 1 GB | $15/mo |
| Worker | App Platform worker (Pro) | 1 GB | $12–$25/mo |
| **Total** | | | **~$55–$90/mo** |

**Caveat**: App Platform cold starts can be slow if the FAISS/ML artifacts are loaded at startup. Use lazy loading or store artifacts in a shared volume / Spaces and load on first request. App Platform Pro is recommended because Basic instances have limited memory and CPU.

### 15.4 Budget-Friendly Optimizations

1. **Use Supabase free/Upstash free until you outgrow them**. Supabase free tier gives a managed Postgres with generous limits; Upstash Redis free tier is enough for caching. This saves $30/mo in Option A.
2. **Host the frontend as a static site** on Vercel/Netlify or DO App Platform static site. This is free or nearly free and offloads the backend.
3. **Combine backend + worker on one droplet** initially. Run FastAPI and scheduled cron jobs on the same 2 GB droplet; separate only when worker load grows.
4. **Move map tiles and GeoJSON to Spaces + CDN**. Large static files should not be served from the app server.
5. **Use Cloudflare free tier** in front of the DO droplet for caching, DDoS protection, and DNS. This reduces bandwidth cost and improves global latency.
6. **Lazy-load ML/RAG artifacts**. Do not load the FAISS index and CSVs on startup. Load on first request or pre-warm via a background thread.
7. **Use the smallest droplet that fits memory**. With current startup behavior, 1 GB may be too tight; 2 GB is the sweet spot. Avoid Premium Droplets unless you need the CPU.
8. **Schedule ETL with GitHub Actions** (free for public repos, 2,000 minutes for free private) or on the same droplet via `cron`, not a separate orchestrator initially.

### 15.5 Suggested Starter Configuration (~$25–$35/mo)

For a thesis/demo/production-pilot with low-to-moderate traffic:

| Component | Choice | Cost |
|-----------|--------|------|
| Frontend | Vercel free / DO App Platform static | $0 |
| Backend | DO Basic Droplet 1 vCPU / 2 GB RAM | $12–$18/mo |
| Database | Supabase free / existing managed Postgres | $0 |
| Cache | Upstash Redis free / existing | $0 |
| Storage/Artifacts | DO Spaces 250 GB | $5/mo |
| Domain + Cloudflare | Free plan + cheap domain | ~$10–$15/yr |
| Backup snapshot | Weekly Droplet backups | ~$2/mo |
| **Total** | | **~$20–$35/mo** |

This is the most cost-effective configuration that can handle the LUMI backend with FAISS + Pandas + FastAPI. Once traffic or data volume grows, migrate to managed DB/Redis and a larger droplet or load-balanced pair.

### 15.6 Infrastructure-as-Code & CI/CD

**Recommendation**: manage DO resources as code from day one:

- Use `docker-compose.yml` for local and single-droplet deployment.
- Use **GitHub Actions** to build and push Docker images to **DigitalOcean Container Registry**.
- Use **doctl** or **Terraform** (`digitalocean/digitalocean` provider) to provision droplets, databases, and Spaces.
- Keep secrets (DB URL, API keys, Redis URL) in **GitHub Secrets** or DigitalOcean App Platform environment variables, not in the image.
- Add a `deploy.yml` workflow that SSHs into the droplet (or uses `doctl apps update`) to pull the latest image and restart containers.

### 15.7 Security & Operations on DO

- **Firewall**: Use DO Cloud Firewall to allow only ports 80/443/22; restrict SSH to your IP.
- **HTTPS**: Use **Let's Encrypt + Certbot** with Nginx, or DO App Platform handles HTTPS automatically.
- **Updates**: Enable automatic security updates on Ubuntu; schedule weekly `apt` updates.
- **Backups**: Enable Droplet backups ($2/mo for 2 GB droplet) or scheduled `pg_dump` to Spaces.
- **Logs**: Forward logs to `/var/log` or a managed service (Papertrail free tier, Datadog free).
- **Monitoring**: Use DO Monitoring for CPU/memory/disk; add Sentry for application error tracking (free tier).

### 15.8 Scaling Path

| Traffic Level | Configuration | Estimated Monthly Cost |
|---------------|---------------|----------------------|
| 0–100 users/day | 1 droplet (2 GB) + free Supabase/Upstash + Spaces | $25–$35 |
| 100–1,000 users/day | 2 GB droplet + managed DB + managed Redis + Spaces CDN | $70–$100 |
| 1,000–10,000 users/day | 2× 2 GB droplets behind load balancer + managed DB (2–4 GB) + Redis (2 GB) | $150–$250 |
| 10,000+ users/day | Kubernetes (DOKS) or multiple App Platform Pro containers + larger managed DB + read replicas | $300+ |

### 15.9 Migration Checklist to DigitalOcean

- [ ] Build a `Dockerfile` for FastAPI and a separate multi-stage `Dockerfile` for the static React build.
- [ ] Create `docker-compose.yml` for local development parity.
- [ ] Push image to DO Container Registry.
- [ ] Provision droplet (2 GB) and install Docker + Docker Compose.
- [ ] Configure `.env` with Supabase/Upstash or DO managed DB/Redis credentials.
- [ ] Set up Nginx reverse proxy with HTTPS (Let's Encrypt).
- [ ] Move GeoJSON/CSV artifacts to Spaces and update paths.
- [ ] Configure `systemd` or `cron` for ETL worker.
- [ ] Add health check endpoint (`/health`) and monitoring.
- [ ] Run smoke tests against the deployed API.
- [ ] Set up CI/CD pipeline for automatic deploys.

### 15.10 Summary: Which Plan Should You Avail?

For a **budget-friendly, production-ready** DigitalOcean deployment for LUMI:

- **Start with Option A** using a **$12–$18 DO Basic Droplet (2 GB RAM)**, keep **Supabase free/Upstash free**, use **Spaces** for artifacts, and host the frontend on **Vercel free** or DO App Platform static. This lands at **~$20–$35/month**.
- If you want fully managed database/cache and less operational risk, move to **Option B** at **~$65–$100/month**.
- Use **Option C (App Platform)** only if you value zero server management over cost and are willing to optimize startup/lazy loading.

### 15.11 References

- DigitalOcean documentation: Droplets, App Platform, Managed Databases, Spaces, Container Registry.
- Docker and Docker Compose documentation.
- Nginx reverse proxy + Let's Encrypt guides (Certbot).
- Terraform DigitalOcean provider documentation.

---

*End of Audit Report*


