# LUMI Complete System Documentation

**Project:** LUMI (Data-Driven Environmental Intelligence System for Renewable Energy Decision Support)  
**Document Version:** 1.0  
**Date:** June 2026  
**Purpose:** Comprehensive technical documentation of the entire LUMI web application implementation, suitable for new developers, thesis panels, and defense presentations.

---

## Part 1: Project Overview & Repository Structure

### 1.1 What is LUMI?

LUMI is a full-stack web application that provides decision support for renewable energy planning in the Philippines. It combines:

- **Geospatial analysis** of solar, wind, hydro, and geothermal potential at the municipality level
- **Time-series forecasting** of national energy consumption and peak demand using ARIMA models
- **AI-powered insights** via Retrieval-Augmented Generation (RAG) with Google Gemini and Groq LLMs
- **E-commerce pricing intelligence** from scraped product data for cost estimation
- **Interactive dashboards** with choropleth maps, trend charts, and suitability scores

The system serves three user tiers:
- **Free users** — Basic simulations, limited to 3 saved scenarios
- **Premium users** — Unlimited simulations, advanced AI insights, priority RAG
- **Admins** — User management, audit logging, system configuration

### 1.2 Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Frontend | React | 18 | SPA with routing, state management, charts |
| UI Library | Tailwind CSS + shadcn/ui | - | Component styling |
| Maps | Leaflet + React-Leaflet | - | Choropleth and marker maps |
| Charts | Recharts | - | Time-series and pie charts |
| Backend | FastAPI | 0.115+ | REST API, async request handling |
| Auth | Supabase Auth | - | JWT, OAuth, role-based access |
| Database | Supabase PostgreSQL | 15+ | Primary data store with RLS |
| Cache | Redis / Upstash Redis | - | Suitability map caching |
| ML | Pandas + Statsmodels | - | ARIMA forecasting (offline trained) |
| AI/LLM | Google Gemini + Groq | - | Text generation, RAG responses |
| Embeddings | Sentence Transformers | - | `all-MiniLM-L6-v2` for RAG |
| Vector DB | FAISS | - | In-memory similarity search |
| Deployment | Docker + Uvicorn | - | Containerized backend |

### 1.3 Repository Structure

```
Lumi/
├── docs/                                    # Project documentation
│   ├── 01-Project-Overview/
│   ├── 02-Architecture/
│   ├── 03-Modules/
│   ├── 04-ML-Data-Science/
│   ├── 05-Setup-Guides/
│   ├── 06-Technical-Resources/
│   ├── 07-Data-Extraction-Reports/
│   ├── 08-Requirements/
│   ├── SYSTEM_FUNCTION_INVENTORY.md
│   ├── THESIS_RESEARCH_INTEGRATION.md
│   └── ML_MODEL_EVALUATION_SUMMARY.md
├── fastapi-backend/                         # FastAPI backend application
│   ├── app/
│   │   ├── auth/                            # OAuth provider handlers
│   │   ├── config/                          # Settings and environment
│   │   ├── dependencies/                    # Auth dependencies
│   │   ├── middleware/                      # CORS, logging, rate limit
│   │   ├── ml/                              # ML predictor service
│   │   ├── models/                          # SQLAlchemy models (if any)
│   │   ├── routes/                          # API endpoint modules
│   │   ├── schemas/                         # Pydantic request/response models
│   │   ├── services/                        # Business logic
│   │   │   ├── geothermal/                  # Geothermal calculations
│   │   │   └── local_data/                  # Cached datasets
│   │   └── utils/                           # Helper utilities
│   ├── scripts/                             # One-off scripts
│   ├── main.py                              # FastAPI entry point
│   └── requirements.txt                     # Python dependencies
├── react-frontend/                          # React frontend application
│   ├── public/                              # Static assets, GeoJSON
│   └── src/
│       ├── components/                      # Reusable UI components
│       ├── context/                         # React context providers
│       ├── hooks/                           # Custom React hooks
│       ├── layouts/                         # Page layouts
│       ├── pages/                           # Route-level pages
│       │   └── admin/                       # Admin dashboard pages
│       ├── routes/                          # Route definitions
│       ├── services/                        # API client modules
│       ├── styles/                          # Global CSS
│       ├── utils/                           # Frontend utilities
│       ├── App.jsx                          # Root component
│       └── main.jsx                         # Entry point
├── supabase/table_scripts/                 # SQL schema definitions
├── python_scripts/                          # ETL and utility scripts
│   └── terrain_pipeline/                    # Terrain analysis pipeline
├── data/                                    # All data directories (grouped)
│   ├── DOE_Data_Extracted/                  # DOE data and ML notebooks
│   ├── GeothermalDatasets/                  # Geospatial datasets
│   ├── ThesisResearchStudies/               # Reference papers
│   ├── philippine_geojson/                  # GeoJSON map files
│   ├── regionalData/                        # Regional energy data
│   ├── scraped_data/                        # E-commerce scraped data
│   ├── windsurf_data_extraction/            # PDF extraction pipeline
│   ├── newDataPointsToExtract/              # Atlas/ERA5 raw rasters
│   ├── phl_msk_alt/                         # SRTM elevation raster
│   └── debug_outputs/                       # Debug/response dumps
├── supabase/schema_structure/lumi_schema_v4.sql  # Complete database schema
└── README.md
```

### 1.4 Folder Descriptions

| Folder | Purpose | Contains | Used For |
|---|---|---|---|
| `docs/` | Project documentation | Architecture guides, ML evaluations, thesis integration docs | Developer onboarding, thesis reference |
| `fastapi-backend/` | REST API server | Python FastAPI application with services, routes, schemas | Business logic, data processing, AI integration |
| `react-frontend/` | User interface | React components, pages, hooks, services | User interaction, visualization, dashboard |
| `supabase/table_scripts/` | Database schemas | SQL scripts for Supabase table creation | Database structure definition |
| `python_scripts/` | ETL utilities | Data extraction, cleaning, terrain analysis scripts | Data pipeline automation |
| `data/DOE_Data_Extracted/` | ML artifacts | Jupyter notebooks, CSV forecasts, model comparison results | Time-series forecasting, model evaluation |
| `data/GeothermalDatasets/` | Geospatial data | Shapefiles, heat flow database, aquifer properties | Geothermal suitability calculations |
| `data/ThesisResearchStudies/` | Academic references | PDF papers supporting algorithms and methods | Research backing for thesis |
| `data/philippine_geojson/` | Map boundaries | Province and municipality GeoJSON files | Choropleth map rendering |
| `data/regionalData/` | Regional statistics | DOE PDFs, fault line shapefiles, barangay data | National energy analysis |
| `data/scraped_data/` | Market data | E-commerce product listings (Alibaba, Amazon, Lazada) | RAG knowledge base for pricing |
| `data/windsurf_data_extraction/` | Document extraction | PDF-to-text/CSV conversion scripts, RAG chunks | DOE document processing |

---

## Part 2: Backend Architecture

### 2.1 FastAPI Application Entry Point

#### `main.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\main.py`
- **Purpose:** FastAPI application entry point
- **Responsibilities:**
  - Initializes FastAPI app with CORS middleware based on `cors_origins` from settings
  - Mounts all API routers under `/api/v1` prefix via `api_router`
  - Runs RAG index build on startup event (`ensure_index_built()`)
  - Root endpoint returns `{"status": "ok"}` for health checks
- **Dependencies:** `fastapi`, `uvicorn`, `app.config.settings`, `app.routes.api_router`
- **Key Code:**
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from app.config.settings import settings
  from app.routes.api import api_router

  app = FastAPI(title=settings.app_name)

  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.cors_origins,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

  app.include_router(api_router, prefix="/api/v1")

  @app.on_event("startup")
  async def startup_event():
      from app.services.rag_pipeline import ensure_index_built
      ensure_index_built()
  ```

### 2.2 Configuration and Settings

#### `app/config/settings.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\config\settings.py`
- **Purpose:** Pydantic-settings configuration loader
- **Responsibilities:**
  - Loads `.env` file from repo root (parent of `fastapi-backend/`)
  - Parses `cors_origins` as JSON array from environment string
  - Validates Supabase URL, anon key, service role key, and JWT secret
  - Exposes settings as singleton: `settings = Settings()`
- **Key Fields:**
  - `app_name`: str = "LUMI API"
  - `api_v1_prefix`: str = "/api/v1"
  - `cors_origins`: list[str]
  - `supabase_url`: str
  - `supabase_anon_key`: str
  - `supabase_service_role_key`: str
  - `supabase_jwt_secret`: str
- **Used By:** All services requiring environment configuration

### 2.3 Authentication Dependencies

#### `app/dependencies/auth.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\dependencies\auth.py`
- **Purpose:** JWT authentication and role-based access control
- **Functions:**

**`get_current_user(request)`**
- Extracts Bearer token from `Authorization` header
- Verifies JWT via Supabase Auth `get_user()`
- Returns user dict with `id`, `email`, `aud`, `role`

**`get_verified_user(request)`**
- Calls `get_current_user()` and ensures `email_confirmed_at` is set
- Raises 403 if email not verified

**`get_current_user_with_role_and_plan(request)`**
- Authenticates user, then fetches:
  - Role from `user_roles` table (default: 'user')
  - Plan from `profiles` table (default: 'free')
- Returns `UserAuthContext` with `user`, `role`, `plan`

**`require_admin(request)`**
- Calls `get_verified_user()` then checks role is 'admin' or 'dev'
- Raises 403 for non-admin users
- Used by all `/admin/*` routes

### 2.4 API Router Aggregation

#### `app/routes/api.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\routes\api.py`
- **Purpose:** Central API router aggregator
- **Responsibilities:**
  - Includes all sub-routers with their prefixes:

| Router | Prefix | Tag | Description |
|---|---|---|---|
| `health` | `/health` | Health | Status check |
| `protected` | `/protected` | User | Authenticated profile endpoints |
| `ecosim` | `/ecosim` | EcoSim | Renewable energy simulation |
| `energyhub` | `/energyhub` | EnergyHub | National energy dashboard |
| `geothermal` | `/geothermal` | Geothermal | Geothermal analysis data |
| `chat` | `/chat` | Chat | AI chat assistant |
| `simulations` | `/simulations` | Simulations | Saved simulations CRUD |
| `admin` | `/admin` | Admin | Admin portal endpoints |

---

## Part 3: EcoSim Module

### 3.1 EcoSim Routes

#### `app/routes/ecosim.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\routes\ecosim.py`
- **Purpose:** EcoSim REST API endpoints
- **Endpoints:**

**`GET /ecosim/`**
- Parameters (query): `municipality_id`, `monthly_consumption`, `monthly_bill`, `desired_savings` (optional), `include_ai` (bool), `use_rag` (bool), `rag_query` (str)
- Returns `EcosimDashboardResponse` with consumption, renewable results, and optional AI analysis
- Logic: Calls `build_ecosim_dashboard_response()` from `app.services.ecosim`

**`GET /ecosim/municipalities`**
- Returns list of all municipalities with basic info
- Used for dropdown selection in frontend

**`POST /ecosim/`**
- Body: `EcosimQueryParams` with municipality, consumption, bill, savings target
- Returns full `RenewableEnergyResults` with detailed calculations

### 3.2 EcoSim Core Service

#### `app/services/ecosim.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\ecosim.py`
- **Purpose:** Core renewable energy simulation logic
- **Responsibilities:**
  - Municipality data retrieval from Supabase and local CSV
  - Solar, wind, hydro, geothermal output calculations
  - Consumption and cost analysis
  - AI analysis integration (Gemini / RAG)
  - Static fallback explanations when AI fails
- **Dependencies:**
  - `pandas` — climate CSV loading
  - `app.services.solar_output_calc` — solar formulas
  - `app.services.wind_output_calc` — wind formulas
  - `app.services.hydro_output_calc` — hydro formulas
  - `app.services.geothermal.features` — geothermal formulas
  - `app.services.gemini_funcs` — AI analysis
  - `app.services.rag_gemini_funcs` — RAG-enhanced AI
  - `app.services.supabase_service` — database client
- **Used By:** `app.routes.ecosim`, `app.services.energyhub`

**Key Constants:**
| Constant | Value | Description |
|---|---|---|
| Solar installation cost | 60,000 PHP/kW | Including panels, inverter, mounting |
| Wind installation cost | 80,000 PHP/kW | Including turbine, tower, inverter |
| Hydro installation cost | 100,000 PHP/kW | Including turbine, penstock, civil works |
| Geothermal installation cost | 100,000 PHP/kW | Exploration + drilling estimate |
| CO2 emission factor | 0.6835 kg CO2/kWh | Philippines grid average (DOE 2019–2021) |

**`renewable_energy_calculator(house, municipality, current_electricity_bill, electricity_rate, desired_savings, include_ai=False, use_rag=False, rag_query=None, nearby_geo_plants=None)`**
- **Parameters:**
  - `house` (str): House name label
  - `municipality` (str): Municipality name
  - `current_electricity_bill` (float): Monthly bill in PHP
  - `electricity_rate` (float): PHP per kWh
  - `desired_savings` (float): Target savings fraction (0.0–1.0)
  - `include_ai` (bool): Whether to call LLM analysis
  - `use_rag` (bool): Whether to use RAG-enhanced analysis
  - `rag_query` (str | None): Custom query for RAG retrieval
  - `nearby_geo_plants` (list | None): Nearby geothermal plants for context
- **Return Value:** Dict with keys:
  - `municipality_data`: Climate and terrain info
  - `consumption_results`: Usage, cost, savings metrics
  - `renewable_energy_results`: Solar, wind, hydro, geothermal outputs
  - `ai_analysis`: Optional LLM-generated summary
- **Logic:**
  1. Fetches municipality climate data from `municipality_climate_averages.csv`
  2. Fetches terrain data from `hydropower_suitability` table
  3. Calculates consumption metrics via `consumption_calculator()`
  4. **Solar:** Computes temperature factor, performance ratio (with dust/humidity adjustments), monthly output via `solar_calc()`
  5. **Hydro:** Estimates flow rate from rainfall + terrain, calculates power via `calculate_hydropower()`
  6. **Wind:** Calculates output via `calculate_wind_output()`
  7. **Geothermal:** Gets suitability and output from `compute_geothermal_suitability()`
  8. If `include_ai`, builds prompt and calls `generate_gemini_response()` or RAG variant
  9. If AI fails, returns static fallback explanation with the calculated results

### 3.3 Solar Output Calculation

#### `app/services/solar_output_calc.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\solar_output_calc.py`
- **Purpose:** Solar energy output and performance ratio calculations
- **Functions:**

**`calculate_temperature_factor(avg_temp, temp_coeff=-0.004)`**
- Adjusts PV efficiency for temperature deviation from STC (25°C)
- Formula: `temperature_factor = 1 + (temp_coeff * (avg_temp - 25))`
- Default coefficient: -0.004/°C (typical for crystalline silicon)

**`calculate_dust_loss(avg_wind_speed, threshold=3.5)`**
- Estimates dust accumulation loss based on wind speed
- Lower wind = more dust accumulation
- Returns loss factor between 0.90 and 0.97

**`calculate_degradation_loss(avg_humidity)`**
- Estimates annual degradation from humidity (corrosion risk)
- Higher humidity = faster degradation
- Returns degradation multiplier (0.85–0.95)

**`calculate_performance_ratio(system_efficiency=0.18, temperature_factor, dust_loss, inverter_efficiency=0.95, mismatch_loss=0.98, wiring_loss=0.98, degradation_loss)`**
- Aggregates all loss factors into single PR value
- Typical range: 0.65–0.80

**`calculate_daily_solar_output(system_kwp, solar_irradiance, performance_ratio)`**
- Daily energy output (kWh/day)
- Formula: `daily_solar_output = system_kwp * solar_irradiance * performance_ratio`

**`calculate_annual_solar_output(daily_solar_output, days_in_month=30)`**
- Annual energy output (kWh/year)
- Uses 30 days per month for simplicity

**`calculate_system_sizing(monthly_consumption_kwh, solar_percentage, system_efficiency, performance_ratio, solar_irradiance, days_in_month=30)`**
- Determines required system size (kWp) to meet savings target
- Formula: `system_kwp = (monthly_consumption * solar_percentage) / (days_in_month * solar_irradiance * performance_ratio * system_efficiency)`

### 3.4 Wind Output Calculation

#### `app/services/wind_output_calc.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\wind_output_calc.py`
- **Purpose:** Wind turbine power and energy calculations
- **Functions:**

**`load_product_data()`**
- Loads `cleaned_products_master.csv` to get average rotor radius and power coefficient from scraped wind turbine data
- Returns dict with `avg_rotor_radius`, `avg_power_coefficient`, `count`

**`calculate_swept_area(rotor_radius)`**
- Formula: `A = π * r²` (m²)

**`calculate_rated_power(air_density, swept_area, wind_speed, power_coefficient, efficiency=0.90)`**
- Formula: `P = 0.5 * ρ * A * V³ * Cp * η`
- Validates `Cp <= 0.593` (Betz limit enforcement)

**`calculate_annual_energy(rated_power, capacity_factor=0.30, hours_per_year=8760)`**
- Formula: `E = P_rated * CF * 8760` (kWh/year)
- Default capacity factor 30% for small turbines

### 3.5 Hydropower Output Calculation

#### `app/services/hydro_output_calc.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\hydro_output_calc.py`
- **Purpose:** Micro-hydropower flow estimation and output calculation
- **Functions:**

**`estimate_runoff_coefficient(mean_slope_deg)`**
- Returns runoff coefficient based on terrain slope:
  - < 3° → 0.30 (flat, high infiltration)
  - 3–10° → 0.45 (moderate slope)
  - 10–20° → 0.60 (steep, rapid runoff)
  - > 20° → 0.75 (very steep, high runoff)

**`estimate_design_flow(avg_flow, gravity_flow_potential)`**
- Sustainable design flow = 40% of average flow × gravity flow potential
- Formula: `design_flow = avg_flow * 0.40 * gravity_flow_potential`

**`calculate_hydropower(design_flow, head_m, efficiency=0.75)`**
- Formula: `P = η * ρ * g * Q * H / 1000` (kW)
  - η = turbine + generator combined efficiency (default 75%)
  - ρ = 1000 kg/m³ (water density)
  - g = 9.81 m/s²
  - Q = flow rate (m³/s)
  - H = head (m)
- **Realistic head scaling:** `realistic_head = min(max(head * 0.12, 2.0), 25.0)`
  - Micro-hydro sites typically use 12% of max elevation difference
  - Constrained between 2m (minimum viable) and 25m (upper micro-hydro limit)

---

## Part 4: Geothermal Module

### 4.1 Geothermal Feature Engineering

#### `app/services/geothermal/features.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\geothermal\features.py`
- **Purpose:** Physics-based geothermal suitability and output computation
- **Responsibilities:**
  - Load IHFC heat flow, fault, volcano, and aquifer datasets
  - Calculate haversine distances to nearest faults and volcanoes
  - Inverse Distance Weighting (IDW) for heat flow interpolation
  - Aquifer suitability scoring (permeability, porosity, thickness)
  - Geothermal gradient and reservoir temperature estimation
  - AHP-based MCDA weighted suitability scoring
  - Thermal and electric power output estimation
- **Dependencies:** `pandas`, `math`, `json`, `pathlib`
- **Used By:** `app.routes.geothermal`, `app.services.ecosim`

**Key Functions:**

**`load_heat_flow_data()`**
- Loads `IHFC_2024_GHFDB_v.2026.03.txt` (Global Heat Flow Database)
- Filters for Philippine bounding box: lat 4.0–21.5, lon 116.0–127.0
- Returns DataFrame with `lat`, `lon`, `heat_flow_mw_m2`

**`load_fault_data()`**
- Loads `geothermal_faults.json` from `public/` directory
- Extracts fault coordinates for distance calculations

**`load_volcano_data()`**
- Loads volcano dataset (Smithsonian Global Volcanism Program)
- Filters for Philippine volcanoes

**`load_aquifer_data()`**
- Loads merged aquifer shapefile data (JGCRI / Zenodo)
- Extracts permeability, porosity, and thickness values

**`haversine_distance(lat1, lon1, lat2, lon2)`**
- Calculates great-circle distance between two coordinates
- Formula: `a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)`
- `c = 2 * atan2(sqrt(a), sqrt(1-a))`
- `distance = R * c` where R = 6371 km

**`idw_interpolation(target_lat, target_lon, data_points, power=2, radius_km=300)`**
- Inverse Distance Weighting with configurable power and search radius
- Formula: `value = Σ(wi * vi) / Σ(wi)` where `wi = 1 / di^p`
- Only uses points within `radius_km`
- Returns interpolated heat flow in mW/m²

**`compute_geothermal_suitability(municipality_id, lat, lon, surface_temp, client=None)`**
- **Parameters:**
  - `municipality_id`: int — Primary key
  - `lat`, `lon`: float — Coordinates
  - `surface_temp`: float — Average surface temperature (°C)
  - `client`: Supabase client (optional)
- **Logic:**
  1. Interpolate heat flow using IDW from nearest IHFC stations
  2. Calculate distance to nearest fault (km)
  3. Calculate distance to nearest volcano (km)
  4. Score aquifer properties (permeability, porosity, thickness normalized 0–1)
  5. Compute geothermal gradient: `G = (q / 1000) / k * 1000` °C/km
     - q = heat flow (mW/m²), k = thermal conductivity (default 2.5 W/m·K)
  6. Estimate reservoir temperature: `T_res = T_surface + G * depth`
     - Default depth = 2000m
  7. Apply MCDA weights (AHP-derived):
     - heat_flow: 0.30, fault: 0.15, volcano: 0.10, aquifer: 0.15, temperature: 0.10
  8. Compute composite score (0–1) and classification
- **Returns:** Dict with all scores, distances, temperatures, and classification

**Classification Thresholds:**
| Score Range | Classification |
|---|---|
| 0.81 – 1.00 | Very High |
| 0.61 – 0.80 | High |
| 0.41 – 0.60 | Moderate |
| 0.21 – 0.40 | Low |
| 0.00 – 0.20 | Very Low |

**`estimate_geothermal_output(suitability_result)`**
- Estimates thermal and electric power from reservoir properties
- **Formulas:**
  - Flow rate inference: from aquifer permeability (if no direct measurement)
  - Thermal power: `Q = m_dot * Cp * ΔT / 1000` (MW)
    - m_dot = mass flow rate (kg/s)
    - Cp = 4180 J/kg·K (specific heat of water)
    - ΔT = reservoir_temp - surface_temp
  - Electric power: `P = Q * η` where η = 0.12 (binary) or 0.15 (flash)
  - Annual energy: `E = P * 8760` (GWh/year)
- **Confidence score:** Based on data availability (0–1)

### 4.2 Geothermal Plant Proximity

#### `app/services/geothermal/plants.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\geothermal\plants.py`
- **Purpose:** Philippines geothermal plant data and proximity boost
- **Functions:**

**`load_geothermal_plants()`**
- Loads `Geothermal-Power-Tracker-March-2026-Final.xlsx` or JSON
- Filters for operating plants only (status = "Operating")
- Returns list of dicts with `name`, `lat`, `lon`, `capacity_mw`, `status`

**`find_nearby_plants(lat, lon, radius_km=50)`**
- Uses haversine distance to find all operating plants within radius
- Returns list sorted by distance

**`calculate_proximity_boost(lat, lon, base_score, radius_km=50, max_bonus=20)`**
- Calculates distance-dependent bonus for geothermal suitability
- Formula: `bonus = max_bonus * (1 - distance / radius_km)`
- Applied linearly: closer plant = higher bonus
- Capped at +20 points (raw score, not percentage)
- Used by EnergyHub to adjust municipality scores before province averaging
- **Returns:** Adjusted score (capped at 100)

### 4.3 Geothermal Routes

#### `app/routes/geothermal.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\routes\geothermal.py`
- **Purpose:** Geothermal REST API endpoints
- **Endpoints:**

**`GET /geothermal/{municipality_id}`**
- Returns `GeothermalAnalysisResponse` with suitability and output for a municipality

**`GET /geothermal/plants`**
- Returns list of all operating geothermal plants with coordinates and capacity

**`GET /geothermal/ecohub/geothermal-summary`**
- Returns province-level summary: average score, total potential MW, classification counts
- Used by EnergyHub choropleth map

---

## Part 5: EnergyHub Module

### 5.1 EnergyHub Routes

#### `app/routes/energyhub.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\routes\energyhub.py`
- **Purpose:** EnergyHub REST API endpoints
- **Endpoints:**

| Method | Path | Description |
|---|---|---|
| GET | `/energyhub/overview` | Latest statistics + forecast summary + model comparison |
| GET | `/energyhub/forecast` | ARIMA forecast 2025–2030 for a metric |
| GET | `/energyhub/trends` | Historical trends with forecast overlay |
| GET | `/energyhub/map-data` | Choropleth data for maps |
| GET | `/energyhub/source-breakdown` | Generation by plant type |
| GET | `/energyhub/grid-breakdown` | Generation by grid (Luzon/Visayas/Mindanao) |
| GET | `/energyhub/model-comparison` | ML model evaluation metrics |
| GET | `/energyhub/ai-insight` | LLM-generated insights |
| POST | `/energyhub/analyze-chart` | Chart-specific AI analysis |

**`GET /energyhub/overview`**
- Returns `OverviewResponse` with:
  - Latest year statistics (consumption, peak demand, generation)
  - Forecast summary (2025–2030 growth rates)
  - Model comparison metrics

**`GET /energyhub/map-data`**
- Parameters: `metric` (default: "renewable_potential"), `level` (default: "province")
- Returns `MapDataResponse` with province-level aggregated scores
- Uses Redis cache with key `lumi:suitability:{metric}:{level}`
- Cache TTL: 24 hours

### 5.2 EnergyHub Service

#### `app/services/energyhub.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\energyhub.py`
- **Purpose:** EnergyHub business logic layer
- **Responsibilities:**
  - Bridges ML predictor, Supabase geographic data, and REST API
  - Builds overview with latest stats, forecast growth, and model comparison
  - Aggregates municipality-level scores to province-level for choropleth maps
  - Applies geothermal proximity boost per municipality before province averaging
- **Dependencies:** `app.ml.predictor`, `app.services.supabase_service`, `app.services.redis_client`, `app.services.geothermal.plants`
- **Used By:** `app.routes.energyhub`

**Key Functions:**

**`get_overview()`**
- Fetches latest year data from `national_energy_annual` table
- Fetches forecast summary from `EnergyHubML.get_forecast()`
- Fetches model comparison from `EnergyHubML.get_model_comparison()`
- Returns combined overview dict

**`get_map_data(metric, level)`**
- Checks Redis cache first
- If cache miss, queries `municipalities` table
- For province level: averages municipality scores by province
- Applies geothermal proximity boost before aggregation if metric is geothermal-related
- Stores result in Redis with 24h TTL

### 5.3 ML Predictor

#### `app/ml/predictor.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\ml\predictor.py`
- **Purpose:** ML prediction service for EnergyHub
- **Responsibilities:**
  - Loads pre-computed ARIMA forecast CSVs on startup
  - Serves historical trends, forecasts with confidence intervals, and model comparison
  - **No runtime retraining** — all models trained offline in Jupyter notebooks
- **Dependencies:** `pandas`, `numpy`
- **Used By:** `app.services.energyhub`

**Data Files Loaded:**
| File | Description |
|---|---|
| `data/DOE_Data_Extracted/master_preprocessed.csv` | Historical data 2003–2024 |
| `data/DOE_Data_Extracted/forecast_consumption_2025_2030.csv` | ARIMA forecast for consumption |
| `data/DOE_Data_Extracted/forecast_peak_demand_2025_2030.csv` | ARIMA forecast for peak demand |
| `data/DOE_Data_Extracted/model_comparison_results.csv` | Model evaluation metrics |

**`EnergyHubML` Class Methods:**

**`get_latest_statistics()`**
- Returns latest year values for consumption, peak demand, generation, and capacity

**`get_historical_trends()`**
- Returns time series 2003–2024 for all metrics

**`get_forecast(metric, years=6)`**
- Returns ARIMA point forecasts and confidence intervals for 2025–2030
- Metrics: `consumption`, `peak_demand`, `generation`

**`get_model_comparison()`**
- Returns comparison of SARIMA, LightGBM, XGBoost, and Prophet models
- Metrics: MAE, RMSE, MAPE, R²

---

## Part 6: AI / LLM System

### 6.1 RAG Pipeline

#### `app/services/rag_pipeline.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\rag_pipeline.py`
- **Purpose:** Semantic chunking, embedding, and FAISS retrieval for RAG
- **Responsibilities:**
  - Sentence-aware chunking (max 150 words, 1-sentence overlap)
  - Document ingestion from knowledge base JSON
  - FAISS index building and persistence (`rag_faiss.index`)
  - Cosine similarity search with score threshold (0.25)
  - Metadata filtering by `renewable_type` and `category`
- **Dependencies:** `numpy`, `sentence_transformers`, `faiss`
- **Used By:** `app.routes.chat`, `app.services.rag_gemini_funcs`
- **Key Logic:**
  - Embedding model: `all-MiniLM-L6-v2`
  - Index type: `IndexFlatIP` on normalized vectors (cosine similarity)
  - Stale detection: rebuilds index if knowledge JSON is newer

**`ensure_index_built()`**
- Called on FastAPI startup
- Checks if FAISS index exists and is up-to-date
- Rebuilds from `rag_knowledge_base.json` if stale or missing

**`retrieve_context(query, top_k=5, score_threshold=0.25, filters=None)`**
- Encodes query to embedding vector
- Searches FAISS index for nearest neighbors
- Filters by metadata (renewable_type, category)
- Returns chunks with source attribution

### 6.2 RAG Knowledge Builder

#### `app/services/rag_knowledge_builder.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\rag_knowledge_builder.py`
- **Purpose:** Build structured knowledge documents from multiple data sources
- **Responsibilities:**
  - Aggregate scraped e-commerce product data into price ranges
  - Ingest DOE national energy statistics as narrative chunks
  - Ingest NASA POWER municipality climate data as narrative chunks
  - Ingest terrain metrics and suitability scores as narrative chunks
  - Output structured JSON with metadata (renewable_type, category, sources)
- **Dependencies:** `pandas`, `app.services.supabase_service`
- **Used By:** `app.services.rag_pipeline` (via `ensure_index_built`)
- **Source Map:** Alibaba, Amazon, Lazada, iSTA Breeze, DOE, NASA POWER, LUMI System

**Knowledge Categories:**
| Category | Description |
|---|---|
| `equipment_cost` | Price ranges for individual components |
| `installation_cost` | System-level installation estimates |
| `maintenance_cost` | Expected maintenance / replacement schedules |
| `components` | Required parts for each renewable type |
| `capacity_info` | Typical system sizes and outputs |
| `pricing_assumptions` | How prices were derived, currency notes |
| `national_energy_statistics` | DOE national energy annual data |
| `municipality_climate` | NASA POWER climate averages per municipality |
| `terrain_metrics` | Terrain and hydropower suitability per municipality |

### 6.3 RAG Gemini Functions

#### `app/services/rag_gemini_funcs.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\rag_gemini_funcs.py`
- **Purpose:** RAG-enhanced AI analysis for EcoSim
- **Responsibilities:**
  - Build RAG prompts with strict grounding rules
  - Perform smart retrieval with renewable type hints
  - Call unified LLM client and sanitize output
  - Normalize RAG output to backward-compatible shape
- **Dependencies:** `app.services.rag_pipeline`, `app.services.llm_client`, `app.services.llm_sanitizer`
- **Used By:** `app.services.ecosim`

**`analyze_with_rag(ecosim_data, user_query, use_rag=True, rag_query=None)`**
- **Parameters:**
  - `ecosim_data`: dict — Full simulation results
  - `user_query`: str — User question or analysis request
  - `use_rag`: bool — Whether to retrieve RAG context
  - `rag_query`: str | None — Override query for retrieval
- **Logic:**
  1. If `use_rag`, calls `retrieve_context()` with renewable type hints
  2. Builds prompt with grounding instruction: "Only use the provided context"
  3. Calls `generate_response()` from unified LLM client
  4. Sanitizes output via `sanitize_llm_output()`
  5. Normalizes to expected structure via `_normalize_rag_output()`

### 6.4 Gemini Client

#### `app/services/gemini_funcs.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\gemini_funcs.py`
- **Purpose:** Google Gemini LLM client with retry and fallback
- **Responsibilities:**
  - Generate responses with retry logic (exponential backoff)
  - Model fallback chain: gemini-2.5-flash → gemini-2.0-flash
  - Handle 503/529 server errors and 429 rate limits
  - Parse JSON responses, extract summary blocks
  - Build structured renewable analysis prompts
- **Dependencies:** `google.genai`, `dotenv`
- **Used By:** `app.services.llm_client` (indirectly), `app.services.rag_gemini_funcs`

**`generate_gemini_response(prompt, model_name="gemini-2.5-flash", max_retries=3)`**
- **Parameters:**
  - `prompt`: str — Full text prompt
  - `model_name`: str — Primary model to use
  - `max_retries`: int — Retry attempts for transient errors
- **Logic:**
  1. Loads API key from `GEMINI_API_KEY` env var
  2. Sends request to Google GenAI API
  3. On 503/529/429: exponential backoff retry (1s, 2s, 4s)
  4. On persistent failure: falls back to `gemini-2.0-flash`
  5. If all models fail, raises exception for upstream handling

**`parse_gemini_json_response(response_text)`**
- Attempts to extract JSON from Gemini's text output
- Handles markdown fences, partial JSON, and nested structures
- Returns parsed dict or None if unparseable

### 6.5 Groq Client

#### `app/services/groq_client.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\groq_client.py`
- **Purpose:** Groq LLM client (free-tier alternative)
- **Responsibilities:**
  - Generate responses via Groq API (`llama-3.3-70b-versatile`)
  - Retry with fallback models: llama-3.1-70b, mixtral-8x7b, llama-3.1-8b
  - Forces JSON output via `response_format`
- **Dependencies:** `groq`
- **Used By:** `app.services.llm_client`, `app.routes.chat`

**`generate_groq_response(prompt, model="llama-3.3-70b-versatile", max_retries=3)`**
- **Parameters:**
  - `prompt`: str — Full text prompt
  - `model`: str — Primary model
  - `max_retries`: int — Retry attempts
- **Logic:**
  1. Loads API key from `GROQ_API_KEY` env var
  2. Sends request with `response_format={"type": "json_object"}` for structured output
  3. Temperature: 0.3, max tokens: 4096
  4. On failure: falls back through model chain

**Default Models:**
| Priority | Model | Description |
|---|---|---|
| 1 | `llama-3.3-70b-versatile` | Primary model, 70B parameters |
| 2 | `llama-3.1-70b-versatile` | Fallback 70B |
| 3 | `mixtral-8x7b-32768` | MoE fallback |
| 4 | `llama-3.1-8b-instant` | Lightweight fallback |

### 6.6 Unified LLM Client

#### `app/services/llm_client.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\llm_client.py`
- **Purpose:** Unified LLM provider switcher
- **Responsibilities:**
  - Routes to Gemini or Groq based on `LLM_PROVIDER` env var
  - Emergency fallback to Groq if all Gemini models fail
- **Dependencies:** `app.services.gemini_funcs`, `app.services.groq_client`
- **Used By:** `app.services.rag_gemini_funcs`, `app.routes.chat`

**`generate_response(prompt, **kwargs)`**
- **Parameters:**
  - `prompt`: str — Text prompt
  - `**kwargs`: Additional args passed to underlying client
- **Logic:**
  1. Reads `LLM_PROVIDER` env var (default: "gemini")
  2. If "gemini": calls `generate_gemini_response()`
  3. If Gemini fails entirely: emergency fallback to Groq with warning log
  4. If "groq": calls `generate_groq_response()`

**`parse_json_response(response_text)`**
- Handles JSON parsing from either Gemini or Groq output
- Tries `json.loads()` first, then regex extraction, then markdown stripping
- Returns dict or None

### 6.7 LLM Sanitizer

#### `app/services/llm_sanitizer.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\llm_sanitizer.py`
- **Purpose:** Clean and normalize LLM output text
- **Responsibilities:**
  - Strip markdown code fences (` ```json ... ``` `)
  - Extract narrative text from JSON wrappers
  - Remove key-value formatting artifacts
  - Normalize whitespace and escaped characters
  - Extract 4-part prescriptive structure: Observation, Interpretation, Recommendation, Reason
- **Dependencies:** `json`, `re`
- **Used By:** `app.services.gemini_funcs`, `app.services.rag_gemini_funcs`

**`sanitize_llm_output(raw_text)`**
- Pipeline: strip fences → extract JSON → strip KV artifacts → normalize whitespace
- Returns clean text string

**`extract_prescriptive_recommendation(text)`**
- Extracts structured 4-part format:
  - **Observation:** What the data shows
  - **Interpretation:** What it means
  - **Recommendation:** What to do
  - **Reason:** Why this recommendation
- Returns dict with these keys, or None if pattern not found

### 6.8 Chat Routes

#### `app/routes/chat.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\routes\chat.py`
- **Purpose:** RAG-powered chat backend
- **Endpoints:**

**`POST /chat/`**
- Body: `{ "message": str, "session_id": str | None, "use_rag": bool }`
- **Logic:**
  - Uses `llama-3.3-70b-versatile` via Groq directly
  - 7-step system prompt with:
    1. Greeting detection and friendly response
    2. Off-topic filtering (politics, illegal content)
    3. Citation rules (`[Source N: Title]` format)
    4. Structured response format
    5. Conciseness requirement (3-5 sentences)
    6. Confidence calibration (hedge uncertain claims)
    7. Follow-up suggestion
  - Retrieves RAG context if `use_rag=true`
  - Persists messages to Supabase `chat_messages` table when session exists

**`GET /chat/sessions`**
- MVP public: returns empty list (sessions managed client-side)

**`GET /chat/sessions/{id}`**
- MVP public: returns empty messages list

---

## Part 7: Authentication & User Management

### 7.1 Protected Routes

#### `app/routes/protected.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\routes\protected.py`
- **Purpose:** Authenticated user endpoints
- **Endpoints:**

| Method | Path | Description |
|---|---|---|
| GET | `/protected/me` | Current user basic info from JWT |
| GET | `/protected/profile` | Extended profile from `profiles` table |
| PUT | `/protected/profile` | Update profile fields (name, avatar, etc.) |
| POST | `/protected/sync-avatar` | Sync OAuth avatar URL from auth metadata |
| POST | `/protected/session` | Store session data in Redis |

**`GET /protected/me`**
- Returns: `{ id, email, role, plan, email_confirmed }`
- Uses `get_verified_user()` dependency

**`GET /protected/profile`**
- Fetches from `profiles` table by user ID
- Returns: `{ user_id, display_name, avatar_url, bio, plan, created_at, updated_at }`

**`PUT /protected/profile`**
- Body: `{ display_name, bio, avatar_url }` (partial updates allowed)
- Updates `profiles` table and returns updated record

### 7.2 Simulations Routes

#### `app/routes/simulations.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\routes\simulations.py`
- **Purpose:** Saved simulation CRUD
- **Endpoints:**

| Method | Path | Description |
|---|---|---|
| POST | `/simulations` | Create new saved simulation |
| GET | `/simulations` | List all simulations for current user |
| GET | `/simulations/{id}` | Get single simulation by ID |
| PATCH | `/simulations/{id}` | Update simulation label |
| DELETE | `/simulations/{id}` | Delete simulation |

**`POST /simulations`**
- Body: `{ municipality_id, monthly_consumption, monthly_bill, desired_savings, results_json, label }`
- **Free tier limit check:**
  - Queries `system_config` table for `free_sim_limit` (default: 3)
  - Counts existing simulations for user
  - If count >= limit, returns 403 with `{"detail": "Free tier limit reached"}`
- On success, inserts into `saved_simulations` table

**`GET /simulations`**
- Returns list of user's simulations, ordered by `created_at DESC`
- Uses `get_current_user_with_role_and_plan()` for auth

**`GET /simulations/{id}`**
- Returns single simulation with full `results_json`
- Verifies ownership: 403 if simulation belongs to another user

**`PATCH /simulations/{id}`**
- Body: `{ label: str }`
- Updates label only
- Ownership check enforced

**`DELETE /simulations/{id}`**
- Soft delete (sets `is_active = false`) or hard delete depending on config
- Ownership check enforced

### 7.3 Admin Routes

#### `app/routes/admin.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\routes\admin.py`
- **Purpose:** Admin portal backend
- **Dependencies:** `require_admin` dependency on all routes
- **Endpoints:**

| Method | Path | Description |
|---|---|---|
| GET | `/admin/users` | List all users with roles and profiles |
| POST | `/admin/users` | Create user (admin action) |
| GET | `/admin/users/{id}` | User detail with simulations count |
| POST | `/admin/users/{id}/ban` | Soft delete (set `is_active=false`) |
| POST | `/admin/users/{id}/role` | Change user role |
| POST | `/admin/users/{id}/plan` | Change subscription plan |
| GET | `/admin/users/{id}/simulations` | View user's simulations |
| GET | `/admin/analytics` | System analytics (user counts, sim counts) |
| GET | `/admin/config` | System configuration |
| POST | `/admin/config` | Update configuration |
| GET | `/admin/audit-log` | Admin audit trail |

**`POST /admin/users/{id}/ban`**
- Sets `is_active = false` in `profiles` table
- Logs action to `admin_audit_log` table

**`POST /admin/users/{id}/role`**
- Body: `{ role: "user" | "admin" | "dev" }`
- Updates `user_roles` table
- Uses `app_role` enum type

**`POST /admin/users/{id}/plan`**
- Body: `{ plan: "free" | "premium" }`
- Updates `profiles.plan` field

**`GET /admin/audit-log`**
- Returns recent admin actions from `admin_audit_log`
- Fields: `id`, `admin_id`, `action`, `target_user_id`, `details`, `created_at`

---

## Part 8: Database & Infrastructure

### 8.1 Supabase Service

#### `app/services/supabase_service.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\supabase_service.py`
- **Purpose:** Supabase client factory with fallback
- **Responsibilities:**
  - Detect JWT vs anon key and create appropriate client
  - Custom `SupabaseRestClient` fallback for non-JWT keys
  - Service role key for admin operations (bypasses RLS)
- **Dependencies:** `supabase`, `httpx`
- **Used By:** Nearly all backend services

**`get_supabase_client()`**
- Creates client with `supabase_url` and `supabase_service_role_key`
- Service role key bypasses Row Level Security (RLS)
- Used for: admin operations, batch inserts, background jobs

**`get_supabase_public_client()`**
- Creates client with `supabase_url` and `supabase_anon_key`
- Respects RLS policies
- Used for: user-facing queries where RLS is desired

**`SupabaseRestClient`**
- Fallback implementation when Supabase key is not a JWT
- Uses direct REST API calls via `httpx`
- Handles GET, POST, PATCH, DELETE verbs

### 8.2 Redis Client

#### `app/services/redis_client.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\redis_client.py`
- **Purpose:** Redis caching for suitability map data
- **Responsibilities:**
  - Async and sync variants for cache get/set
  - Suitability cache invalidation
  - Key pattern: `lumi:suitability:{renewable_type}:{level}`
- **Dependencies:** `redis`
- **Used By:** `app.services.energyhub`, `app.services.municipality_suitability_builder`

**`get_redis()`**
- Returns async Redis client from `UPSTASH_REDIS_URL` or `REDIS_URL` env var

**`get_redis_sync()`**
- Returns sync Redis client for non-async contexts

**`get_suitability_cache(renewable_type, level)`**
- Key: `lumi:suitability:{renewable_type}:{level}`
- Returns cached JSON string or None

**`set_suitability_cache(renewable_type, level, data, ttl=86400)`**
- Stores JSON string with TTL (default 24 hours = 86400s)

**`invalidate_suitability_cache(renewable_type=None, level=None)`**
- If parameters provided: deletes specific key
- If no parameters: deletes all keys matching `lumi:suitability:*`

### 8.3 Municipality Suitability Builder

#### `app/services/municipality_suitability_builder.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\municipality_suitability_builder.py`
- **Purpose:** Batch computation and persistence of municipality suitability scores
- **Responsibilities:**
  - Compute solar, wind, hydro, geothermal, and composite scores per municipality
  - Fetch climate data from Supabase `municipality_climate_monthly`
  - Persist scores to `municipalities` table
  - Invalidate Redis cache after updates
  - Classification: Very High (81+), High (61+), Moderate (41+), Low (21+), Very Low (0+)
- **Dependencies:** `app.services.supabase_service`, `app.services.redis_client`

**Key Functions:**

**`estimate_solar_score(municipality_id, client)`**
- Fetches `allsky_sfc_sw_dwn` (solar irradiance) and `t2m` (temperature)
- Normalizes irradiance to 0–100 score
- Applies temperature penalty for high temperatures (>30°C)

**`estimate_wind_score(municipality_id, client)`**
- Fetches `ws10m` (wind speed at 10m)
- Adjusts to 50m hub height using power law: `V50 = V10 * (50/10)^0.14`
- Normalizes to 0–100 score

**`estimate_hydro_score(municipality_id, client)`**
- Fetches `prectotcorr` (precipitation) and elevation data
- Combines rainfall and terrain ruggedness into 0–100 score

**`compute_composite_score(solar, wind, hydro, geothermal)`**
- Average of available scores (ignores None values)
- Returns score 0–100 and classification string

### 8.4 MCDA Weights Service

#### `app/services/mcda_weights_service.py`
- **Location:** `d:\63947\Documents\GitHub\Lumi\fastapi-backend\app\services\mcda_weights_service.py`
- **Purpose:** AHP-derived MCDA criterion weights loader
- **Responsibilities:**
  - Load active weights from `mcda_weights` table
  - Fallback to hard-coded defaults if DB unavailable
  - Cache weights in memory
- **Default Weights:**

| Energy Type | Criterion | Weight |
|---|---|---|
| Geothermal | heat_flow | 0.30 |
| Geothermal | fault | 0.15 |
| Geothermal | volcano | 0.10 |
| Geothermal | aquifer | 0.15 |
| Geothermal | temperature | 0.10 |
| Solar | irradiance | 0.40 |
| Solar | temperature | 0.20 |
| Solar | cloud_cover | 0.20 |
| Solar | terrain_slope | 0.10 |
| Solar | land_use | 0.10 |
| Wind | wind_speed | 0.40 |
| Wind | terrain_roughness | 0.20 |
| Wind | elevation | 0.20 |
| Wind | land_use | 0.10 |
| Wind | air_density | 0.10 |
| Hydro | rainfall | 0.30 |
| Hydro | watershed_slope | 0.25 |
| Hydro | catchment_area | 0.25 |
| Hydro | hydraulic_head | 0.20 |

**`load_mcda_weights(client=None)`**
- Fetches from `mcda_weights` table where `is_active = true`
- Returns dict: `{ energy_type: { criterion: weight } }`
- Caches result in `_weights_cache` global

**`get_weights(energy_type, client=None)`**
- Returns weights for specific energy type
- Falls back to defaults if not found

**`invalidate_weights_cache()`**
- Clears `_weights_cache` global
- Call after admin updates to weights

### 8.5 Database Schema Overview

#### `lumi_schema_v4.sql`
- **Location:** `supabase/schema_structure/lumi_schema_v4.sql` (repo root)
- **Purpose:** Complete Supabase PostgreSQL schema
- **Key Tables:**

| Table | Purpose | Key Columns |
|---|---|---|
| `municipalities` | Geographic units with suitability scores | `municipality_id`, `name`, `province_id`, `lat`, `lon`, `solar_suitability_score`, `wind_suitability_score`, `hydro_suitability_score`, `geothermal_suitability_score`, `composite_suitability_score` |
| `municipality_climate_monthly` | Monthly climate data per municipality | `municipality_id`, `year`, `month`, `t2m`, `ws10m`, `allsky_sfc_sw_dwn`, `prectotcorr` |
| `national_energy_annual` | DOE national statistics | `year`, `total_consumption_gwh`, `peak_demand_mw`, `total_generation_gwh` |
| `geothermal_suitability` | Pre-computed geothermal metrics | `municipality_id`, `heat_flow_score`, `fault_distance_km`, `volcano_distance_km`, `geothermal_score`, `classification` |
| `geothermal_output` | Pre-computed geothermal energy estimates | `municipality_id`, `reservoir_temperature_c`, `thermal_power_mw`, `electric_power_mw`, `annual_energy_gwh` |
| `hydropower_suitability` | Pre-computed hydropower metrics | `municipality_id`, `elevation_m`, `hydraulic_head_m`, `hydro_suitability_score` |
| `saved_simulations` | User saved scenarios | `id`, `user_id`, `municipality_id`, `monthly_consumption`, `monthly_bill`, `desired_savings`, `results_json`, `label`, `is_active` |
| `profiles` | User profiles | `user_id`, `display_name`, `avatar_url`, `plan`, `is_active` |
| `user_roles` | Role assignments | `user_id`, `role` (enum: user, admin, dev) |
| `chat_sessions` | Chat session metadata | `id`, `user_id`, `title`, `created_at` |
| `chat_messages` | Individual chat messages | `id`, `session_id`, `role` (user/assistant), `content`, `sources_json`, `created_at` |
| `admin_audit_log` | Admin actions | `id`, `admin_id`, `action`, `target_user_id`, `details`, `created_at` |
| `system_config` | Application configuration | `key`, `value`, `updated_at` |
| `forecast_cache` | Cached ML forecasts | `model_id`, `target_variable`, `forecast_json`, `created_at` |
| `ml_model_registry` | Trained model metadata | `model_id`, `model_name`, `model_version`, `model_type`, `metrics`, `is_active` |
| `mcda_weights` | AHP criterion weights | `energy_type`, `criterion`, `weight`, `is_active` |

**Custom Types:**
- `app_role`: ENUM of 'user', 'admin', 'dev'

**Functions:**
- `get_suitability_classification(score numeric)` → text: Returns classification label from numeric score
- `handle_new_user()` → trigger: Auto-creates profile and role on new user signup
- `set_updated_at()` → trigger: Auto-updates `updated_at` timestamp on row modification

---

## Part 9: Frontend Architecture

### 9.1 React Application Structure

#### `src/App.jsx`
- **Location:** `d:\63947\Documents\GitHub\Lumi\react-frontend\src\App.jsx`
- **Purpose:** Root React component
- **Responsibilities:**
  - Renders `AppRoutes` (react-router)
  - Mounts global `Toaster` for notifications
- **Code:**
  ```jsx
  import AppRoutes from "./routes/AppRoutes";
  import { Toaster } from "./components/ui/sonner";

  export default function App() {
    return (
      <>
        <AppRoutes />
        <Toaster />
      </>
    );
  }
  ```

#### `src/routes/AppRoutes.jsx`
- **Location:** `d:\63947\Documents\GitHub\Lumi\react-frontend\src\routes\AppRoutes.jsx`
- **Purpose:** Application routing configuration
- **Responsibilities:**
  - Defines all routes with `MainLayout` wrapper
  - Protected routes: Dashboard, EcoSim, EnergyHub, Chat, Saved Simulations
  - Admin routes: Dashboard, Users, Analytics, Config, Moderation
  - Public routes: Home, About, Login, Reset Password
- **Routes Table:**

| Path | Component | Auth Required | Admin Required |
|---|---|---|---|
| `/` | Home | No | No |
| `/login` | Login | No | No |
| `/reset-password` | ResetPassword | No | No |
| `/about` | About | No | No |
| `/dashboard` | Dashboard | Yes | No |
| `/ecosim` | Ecosim | Yes | No |
| `/energyhub` | EnergyHub | Yes | No |
| `/chat` | ChatPage | Yes | No |
| `/saved-simulations` | SavedSimulations | Yes | No |
| `/admin` | AdminDashboard | Yes | Yes |
| `/admin/users` | AdminUsers | Yes | Yes |
| `/admin/analytics` | AdminAnalytics | Yes | Yes |
| `/admin/config` | AdminConfig | Yes | Yes |
| `/admin/moderate` | AdminModeration | Yes | Yes |
| `*` | NotFound | No | No |

### 9.2 API Client

#### `src/services/apiClient.js`
- **Location:** `d:\63947\Documents\GitHub\Lumi\react-frontend\src\services\apiClient.js`
- **Purpose:** Generic HTTP client for backend API
- **Responsibilities:**
  - Base URL resolution via `getApiBaseUrl()`
  - Bearer token injection for authenticated requests
  - JSON error parsing with detailed messages
- **Key Function:**

**`request(path, { token, ...options })`**
- Constructs full URL from `BASE_URL + path`
- Injects `Authorization: Bearer {token}` if provided
- Sets `Content-Type: application/json` for POST/PUT bodies
- On non-2xx response:
  1. Parses error body as JSON
  2. Extracts `detail.msg`, `detail` string, or `message`
  3. Throws `Error` with extracted message
- Returns parsed JSON on success

**Helper Functions:**
| Function | Path | Auth |
|---|---|---|
| `getHealth()` | `/health/` | No |
| `getProtectedMe(token)` | `/protected/me` | Yes |
| `getEcosim(params)` | `/ecosim/?...` | No (public params) |
| `getMunicipalities()` | `/ecosim/municipalities` | No |
| `getGeothermal(municipalityId)` | `/geothermal/{id}` | No |

### 9.3 EnergyHub Service

#### `src/services/energyhub.js`
- **Location:** `d:\63947\Documents\GitHub\Lumi\react-frontend\src\services\energyhub.js`
- **Purpose:** EnergyHub API service layer
- **Functions:**

| Function | Endpoint | Parameters |
|---|---|---|
| `getEnergyHubOverview()` | `/energyhub/overview` | None |
| `getEnergyHubForecast(metric)` | `/energyhub/forecast` | `metric` (default: "consumption") |
| `getEnergyHubTrends()` | `/energyhub/trends` | None |
| `getEnergyHubMapData(metric, level)` | `/energyhub/map-data` | `metric`, `level` (default: "province") |
| `getEnergyHubSourceBreakdown(year)` | `/energyhub/source-breakdown` | `year` (optional) |
| `getEnergyHubGridBreakdown(year)` | `/energyhub/grid-breakdown` | `year` (optional) |
| `getEnergyHubModelComparison()` | `/energyhub/model-comparison` | None |
| `getEnergyHubAiInsight(useLlm)` | `/energyhub/ai-insight` | `useLlm` (default: false) |
| `getGeothermalSummary()` | `/geothermal/ecohub/geothermal-summary` | None |
| `getGeothermalPlants()` | `/geothermal/plants` | None |
| `analyzeChart(chartType, chartData, forceRefresh)` | `/energyhub/analyze-chart` | POST body |

### 9.4 EcoSim Page

#### `src/pages/Ecosim.jsx`
- **Location:** `d:\63947\Documents\GitHub\Lumi\react-frontend\src\pages\Ecosim.jsx`
- **Purpose:** EcoSim simulation page
- **Responsibilities:**
  - Municipality selection with search/filter
  - Household input form (bill, rate, savings target)
  - Simulation result display (cards, charts, comparisons)
  - AI analysis display with toggle
  - Save simulation dialog (persist to Supabase)
  - Load saved simulation from query param `?simulation_id=`
- **State Management:**
  - `municipalityId`, `municipalityName`
  - `monthlyConsumption`, `monthlyBill`, `desiredSavings`
  - `results` (simulation output)
  - `aiAnalysis` (LLM response)
  - `loading`, `saving`
- **Key Effects:**
  - On mount: fetch municipalities list for dropdown
  - On `simulation_id` query param: load saved simulation and pre-populate inputs

### 9.5 EnergyHub Page

#### `src/pages/EnergyHub.jsx`
- **Location:** `d:\63947\Documents\GitHub\Lumi\react-frontend\src\pages\EnergyHub.jsx`
- **Purpose:** National energy dashboard
- **Responsibilities:**
  - Overview cards with latest statistics
  - Historical trends chart with forecast overlay
  - Choropleth map with metric/level switching
  - Source and grid breakdown pie charts
  - AI insight panel with LLM toggle
  - Chart-specific AI analysis
  - Geothermal plant markers on map
- **State Management:**
  - `overviewData`, `trendsData`, `forecastData`
  - `mapData`, `mapMetric`, `mapLevel`
  - `sourceBreakdown`, `gridBreakdown`
  - `aiInsight`, `aiLoading`
  - `chartAnalysis` (for selected chart)
- **Caching:**
  - Map data cached by `metric:level` key in component state
  - Reduces redundant API calls when switching between metrics

### 9.6 Chat Page

#### `src/pages/ChatPage.jsx`
- **Location:** `d:\63947\Documents\GitHub\Lumi\react-frontend\src\pages\ChatPage.jsx`
- **Purpose:** AI chat assistant interface
- **Responsibilities:**
  - Message list with user/assistant bubbles
  - Input field with send button
  - Citation formatting (`[Source N: Title]` highlighted)
  - Session creation and persistence to Supabase
  - Load chat history from `chat_messages` table
  - New chat button (clears current session)
- **State Management:**
  - `messages`: array of `{ role, content, sources }`
  - `inputText`
  - `sessionId`
  - `loading`
- **Key Effects:**
  - On mount: fetch or create chat session
  - On session change: load messages for that session

### 9.7 Frontend Services Summary

| Service File | Purpose | Key Exports |
|---|---|---|
| `apiClient.js` | Generic HTTP client | `request()`, `getHealth()`, `getEcosim()`, `getMunicipalities()` |
| `energyhub.js` | EnergyHub endpoints | All `getEnergyHub*()` and `analyzeChart()` |
| `ecosim.js` | EcoSim endpoints | `runSimulation()`, `saveSimulation()`, `getSavedSimulations()` |
| `chat.js` | Chat endpoints | `sendMessage()`, `getSessions()`, `getSessionMessages()` |
| `auth.js` | Auth helpers | `getCurrentUser()`, `signIn()`, `signOut()`, `onAuthStateChange()` |
| `supabase.js` | Supabase client | `supabase` singleton instance |

---

## Part 10: API Endpoint Reference

### 10.1 Health Check

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/health/` | No | Returns `{ "status": "ok" }` |

### 10.2 EcoSim Endpoints

| Method | Path | Auth | Parameters | Response |
|---|---|---|---|---|
| GET | `/api/v1/ecosim/` | No | `municipality_id` (int), `monthly_consumption` (float), `monthly_bill` (float), `desired_savings` (float, optional), `include_ai` (bool), `use_rag` (bool), `rag_query` (str) | `EcosimDashboardResponse` |
| GET | `/api/v1/ecosim/municipalities` | No | None | `MunicipalityListResponse` |
| POST | `/api/v1/ecosim/` | No | Body: `EcosimQueryParams` | `RenewableEnergyResults` |

**`EcosimDashboardResponse` Schema:**
```json
{
  "municipality": {
    "municipality_id": 1,
    "name": "Example",
    "province": "Batangas",
    "lat": 13.75,
    "lon": 121.05,
    "climate": { "avg_temp": 27.5, "avg_wind_speed": 3.2, "avg_solar_irradiance": 5.1, "avg_rainfall": 200 }
  },
  "consumption": {
    "monthly_kwh": 300,
    "monthly_cost_php": 4500,
    "annual_kwh": 3600,
    "annual_cost_php": 54000,
    "target_savings_percent": 50
  },
  "renewable_results": {
    "solar": { "system_kwp": 5.2, "annual_output_kwh": 7200, "installation_cost_php": 312000, "payback_years": 5.8 },
    "wind": { "rated_power_kw": 2.5, "annual_output_kwh": 6570, "installation_cost_php": 200000, "payback_years": 3.7 },
    "hydro": { "design_flow_lps": 15, "head_m": 8, "power_kw": 0.88, "annual_output_kwh": 7710, "installation_cost_php": 88000, "payback_years": 1.6 },
    "geothermal": { "suitability_score": 72, "classification": "High", "estimated_output_kwh": 0, "notes": "Requires geological survey" }
  },
  "ai_analysis": "string (optional)"
}
```

### 10.3 EnergyHub Endpoints

| Method | Path | Auth | Parameters | Response |
|---|---|---|---|---|
| GET | `/api/v1/energyhub/overview` | No | None | `OverviewResponse` |
| GET | `/api/v1/energyhub/forecast` | No | `metric` (str, default: "consumption") | `ForecastResponse` |
| GET | `/api/v1/energyhub/trends` | No | None | `TrendsResponse` |
| GET | `/api/v1/energyhub/map-data` | No | `metric` (str), `level` (str, default: "province") | `MapDataResponse` |
| GET | `/api/v1/energyhub/source-breakdown` | No | `year` (int, optional) | `SourceBreakdownResponse` |
| GET | `/api/v1/energyhub/grid-breakdown` | No | `year` (int, optional) | `GridBreakdownResponse` |
| GET | `/api/v1/energyhub/model-comparison` | No | None | `ModelComparisonResponse` |
| GET | `/api/v1/energyhub/ai-insight` | No | `use_llm` (bool, default: false) | `AiInsightResponse` |
| POST | `/api/v1/energyhub/analyze-chart` | No | Body: `{ chart_type, chart_data }` | `AnalyzeChartResponse` |

### 10.4 Geothermal Endpoints

| Method | Path | Auth | Parameters | Response |
|---|---|---|---|---|
| GET | `/api/v1/geothermal/{municipality_id}` | No | `municipality_id` (path) | `GeothermalAnalysisResponse` |
| GET | `/api/v1/geothermal/plants` | No | None | List of `GeothermalPlant` |
| GET | `/api/v1/geothermal/ecohub/geothermal-summary` | No | None | `GeothermalDashboardSummary` |

### 10.5 Chat Endpoints

| Method | Path | Auth | Parameters | Response |
|---|---|---|---|---|
| POST | `/api/v1/chat/` | No | Body: `{ message, session_id, use_rag }` | `{ reply, sources }` |
| GET | `/api/v1/chat/sessions` | No | None | `[]` (MVP) |
| GET | `/api/v1/chat/sessions/{id}` | No | `id` (path) | `{ messages: [] }` (MVP) |

### 10.6 Simulations Endpoints (Auth Required)

| Method | Path | Auth | Parameters | Response |
|---|---|---|---|---|
| POST | `/api/v1/simulations` | Yes | Body: `CreateSimulationRequest` | `Simulation` |
| GET | `/api/v1/simulations` | Yes | None | List of `Simulation` |
| GET | `/api/v1/simulations/{id}` | Yes | `id` (path) | `Simulation` |
| PATCH | `/api/v1/simulations/{id}` | Yes | Body: `{ label }` | `Simulation` |
| DELETE | `/api/v1/simulations/{id}` | Yes | `id` (path) | `204 No Content` |

### 10.7 Protected Endpoints (Auth Required)

| Method | Path | Auth | Parameters | Response |
|---|---|---|---|---|
| GET | `/api/v1/protected/me` | Yes | None | `User` |
| GET | `/api/v1/protected/profile` | Yes | None | `Profile` |
| PUT | `/api/v1/protected/profile` | Yes | Body: `UpdateProfileRequest` | `Profile` |
| POST | `/api/v1/protected/sync-avatar` | Yes | None | `Profile` |
| POST | `/api/v1/protected/session` | Yes | Body: `SessionData` | `200 OK` |

### 10.8 Admin Endpoints (Admin Required)

| Method | Path | Auth | Parameters | Response |
|---|---|---|---|---|
| GET | `/api/v1/admin/users` | Admin | None | List of `UserWithProfile` |
| POST | `/api/v1/admin/users` | Admin | Body: `CreateUserRequest` | `User` |
| GET | `/api/v1/admin/users/{id}` | Admin | `id` (path) | `UserWithProfile` |
| POST | `/api/v1/admin/users/{id}/ban` | Admin | `id` (path) | `200 OK` |
| POST | `/api/v1/admin/users/{id}/role` | Admin | Body: `{ role }` | `200 OK` |
| POST | `/api/v1/admin/users/{id}/plan` | Admin | Body: `{ plan }` | `200 OK` |
| GET | `/api/v1/admin/users/{id}/simulations` | Admin | `id` (path) | List of `Simulation` |
| GET | `/api/v1/admin/analytics` | Admin | None | `AnalyticsResponse` |
| GET | `/api/v1/admin/config` | Admin | None | `SystemConfig` |
| POST | `/api/v1/admin/config` | Admin | Body: `{ key, value }` | `SystemConfig` |
| GET | `/api/v1/admin/audit-log` | Admin | None | List of `AuditLogEntry` |

---

## Part 11: Algorithms & Formulas

### 11.1 Solar Energy Calculations

#### Temperature Factor
```
temperature_factor = 1 + temp_coeff * (avg_temp - 25)
```
- `temp_coeff` = -0.004 /°C (crystalline silicon)
- Reference temperature (STC) = 25°C
- For every 1°C above 25°C, efficiency drops 0.4%

#### Performance Ratio
```
performance_ratio = system_efficiency * temperature_factor * dust_loss * inverter_efficiency * mismatch_loss * wiring_loss * degradation_loss
```
- Typical range: 0.65 – 0.80
- Default values:
  - `system_efficiency` = 0.18 (18%)
  - `inverter_efficiency` = 0.95 (95%)
  - `mismatch_loss` = 0.98 (2% loss)
  - `wiring_loss` = 0.98 (2% loss)

#### Daily Solar Output
```
daily_output_kwh = system_kwp * solar_irradiance_kwh_m2_day * performance_ratio
```

#### Annual Solar Output
```
annual_output_kwh = daily_output_kwh * 30 * 12
```
(Uses 30 days/month simplification)

#### System Sizing
```
system_kwp = (monthly_consumption_kwh * solar_percentage) / (30 * solar_irradiance * performance_ratio * system_efficiency)
```

#### Payback Period
```
payback_years = installation_cost_php / (annual_savings_php)
annual_savings_php = (annual_output_kwh * electricity_rate_php_kwh) - maintenance_cost_php
```

### 11.2 Wind Energy Calculations

#### Swept Area
```
swept_area_m2 = π * rotor_radius_m²
```

#### Rated Power (Betz Limit Applied)
```
rated_power_kw = 0.5 * air_density_kg_m3 * swept_area_m2 * wind_speed_ms³ * power_coefficient * efficiency
```
- `air_density` = 1.225 kg/m³ (sea level standard)
- `power_coefficient` (Cp) ≤ 0.593 (Betz limit enforced)
- `efficiency` = 0.90 (generator + drivetrain)

#### Annual Energy Output
```
annual_energy_kwh = rated_power_kw * capacity_factor * 8760_hours
```
- Default `capacity_factor` = 0.30 (30% for small turbines)

### 11.3 Hydropower Calculations

#### Runoff Coefficient
| Slope | Coefficient |
|---|---|
| < 3° | 0.30 |
| 3 – 10° | 0.45 |
| 10 – 20° | 0.60 |
| > 20° | 0.75 |

#### Design Flow
```
design_flow_m3s = avg_flow_m3s * 0.40 * gravity_flow_potential
```
- 40% of average flow (sustainability factor)
- Multiplied by terrain-based gravity flow potential

#### Hydropower Output
```
power_kw = efficiency * water_density_kg_m3 * gravity_ms2 * design_flow_m3s * head_m / 1000
```
- `efficiency` = 0.75 (turbine + generator)
- `water_density` = 1000 kg/m³
- `gravity` = 9.81 m/s²

#### Realistic Head
```
realistic_head_m = min(max(raw_head_m * 0.12, 2.0), 25.0)
```
- Micro-hydro uses ~12% of max elevation difference
- Constrained: 2m minimum, 25m maximum

### 11.4 Geothermal Calculations

#### Geothermal Gradient
```
gradient_c_km = (heat_flow_mw_m2 / 1000) / thermal_conductivity_w_m_k * 1000
```
- `thermal_conductivity` = 2.5 W/m·K (default for crustal rocks)

#### Reservoir Temperature
```
reservoir_temp_c = surface_temp_c + (gradient_c_km * depth_km)
```
- Default `depth` = 2000m (2km)

#### Thermal Power
```
thermal_power_mw = (mass_flow_rate_kg_s * specific_heat_j_kg_k * delta_temp_k) / 1000
```
- `specific_heat` (Cp) = 4180 J/kg·K (water)
- `delta_temp` = reservoir_temp - surface_temp

#### Electric Power
```
electric_power_mw = thermal_power_mw * plant_efficiency
```
- Binary plant: η = 0.12 (12%)
- Flash plant: η = 0.15 (15%)

#### Annual Energy
```
annual_energy_gwh = electric_power_mw * 8760_hours_year
```

#### Suitability Score (MCDA)
```
score = heat_flow_score * 0.30 + fault_score * 0.15 + volcano_score * 0.10 + aquifer_score * 0.15 + temperature_score * 0.10
```
- All sub-scores normalized to 0–1

### 11.5 ARIMA Forecasting (EnergyHub)

#### Why ARIMA?
- With only **22 years** of annual data, deep learning models (LSTM, XGBoost) would overfit
- ARIMA is a classical statistical model requiring minimal data
- Produces interpretable results with confidence intervals

#### Model Selection Process
1. **Stationarity Check:** ADF test on time series
2. **Differencing:** Apply d-th order differencing if non-stationary
3. **ACF/PACF:** Determine AR(p) and MA(q) orders
4. **Grid Search:** Auto-ARIMA over p, d, q ∈ [0, 3]
5. **Validation:** Walk-forward validation on last 3 years

#### Evaluation Metrics
| Metric | Formula | Target |
|---|---|---|
| MAE | mean(\|actual - predicted\|) | Lower is better |
| RMSE | sqrt(mean((actual - predicted)²)) | Lower is better |
| MAPE | mean(\|actual - predicted\| / actual) * 100% | < 10% preferred |
| R² | 1 - (SS_res / SS_tot) | > 0.85 preferred |

#### Forecast Files
- `forecast_consumption_2025_2030.csv`: Point forecasts + 80% and 95% confidence intervals
- `forecast_peak_demand_2025_2030.csv`: Same for peak demand
- `model_comparison_results.csv`: SARIMA vs LightGBM vs XGBoost vs Prophet

### 11.6 RAG Retrieval Algorithm

#### Sentence-Aware Chunking
```
chunk_size = 150 words (max)
overlap = 1 sentence
```
- Preserves semantic coherence
- Avoids cutting mid-sentence

#### Embedding
```
model = "sentence-transformers/all-MiniLM-L6-v2"
dimension = 384
```

#### Similarity Search
```
cosine_similarity = dot(query_vector, doc_vector) / (norm(query) * norm(doc))
```
- FAISS `IndexFlatIP` on normalized vectors
- `score_threshold = 0.25` (minimum relevance)
- `top_k = 5` (max chunks returned)

#### Metadata Filtering
```python
filters = {
    "renewable_type": "solar",  # or "wind", "hydro", "geothermal"
    "category": "equipment_cost"
}
```

---

## Part 12: Data Sources & Research Mapping

### 12.1 Primary Data Sources

| Dataset | Source | Type | Coverage | Used In |
|---|---|---|---|---|
| **NASA POWER** | NASA Langley Research Center | API / CSV | Municipality-level climate (2003–2024) | Solar, wind, hydro scoring; municipality climate table |
| **IHFC Global Heat Flow DB** | GFZ Potsdam / Fuchs et al. 2024 | TXT | Global heat flow measurements | Geothermal suitability, reservoir temp estimation |
| **PHIVOLCS Fault Data** | Philippine Institute of Volcanology and Seismology | Shapefile / GeoJSON | Philippine active faults | Fault distance, density calculations |
| **Smithsonian Volcano DB** | Smithsonian Global Volcanism Program | CSV / JSON | Global volcano catalog | Volcano proximity scoring |
| **JGCRI Aquifer Data** | JGCRI / Zenodo | Shapefile (GDB) | Global aquifer properties | Aquifer permeability, porosity, thickness |
| **DOE Power Statistics** | Department of Energy Philippines | PDF / CSV | National energy (2003–2024) | EnergyHub trends, forecasts, source breakdown |
| **Global Energy Monitor** | Global Energy Monitor | XLSX | Global power plant tracker | Geothermal plant locations, capacity, status |
| **E-commerce Scrapers** | Alibaba, Amazon, Lazada, iSTA Breeze | JSON / CSV | Renewable product listings | RAG knowledge base for pricing |
| **Philippine GeoJSON** | GADM / PhilGIS | GeoJSON | Province and municipality boundaries | Choropleth map rendering |

### 12.2 NASA POWER Variables

| Variable | Unit | Description | Used For |
|---|---|---|---|
| `T2M` | °C | Temperature at 2m | Solar temp factor, geothermal surface temp |
| `T2M_MAX` | °C | Max temperature | Solar peak temp stress |
| `T2M_MIN` | °C | Min temperature | Solar cold-start efficiency |
| `RH2M` | % | Relative humidity at 2m | Solar degradation, dust loss proxy |
| `PRECTOTCORR` | mm/day | Precipitation corrected | Hydropower flow estimation |
| `WS10M` | m/s | Wind speed at 10m | Wind power calculation (extrapolated to 50m) |
| `ALLSKY_SFC_SW_DWN` | kWh/m²/day | Solar irradiance | Solar output calculation |
| `CLOUD_AMT` | % | Cloud amount | Solar irradiance adjustment |
| `SURFACE_PRESSURE` | kPa | Surface pressure | Air density for wind power |
| `ELEVATION` | m | Elevation | Hydropower head, terrain classification |
| `RHOA` | kg/m³ | Surface air density | Wind power calculation |

### 12.3 Thesis Research Papers

| Paper | Year | Citation | Relevance |
|---|---|---|---|
| Fuchs et al. — Global Heat Flow Database 2024 | 2024 | 10.5880/fidgeo.2024.014 | Geothermal heat flow data provenance |
| Kim et al. — PV Module Degradation Review | 2021 | 10.3390/en14144278 | Solar degradation formulas |
| Zdyb & Sobczynski — PV Performance Assessment | 2021 | 10.3390/en17092197 | Solar performance ratio methodology |
| Chatzipanagi et al. — Updated PV Yield Model | 2025 | 10.1002/pip.3926 | PVGIS solar yield methodology |
| Castro et al. — Micro Hydro in Bataan | 2021 | IRE Journals Vol 6 Issue 12 | Hydropower feasibility case study |
| Rumbayan & Rumbayan — Micro Hydro in Indonesia | 2021 | 10.3390/ | Hydropower design flow methodology |
| Di Dio et al. — Pico Hydro Generators | 2021 | 10.3390/ | Wind turbine efficiency parallels |
| Bianchini et al. — Small Wind Challenges | 2022 | 10.5194/wes-7-2003-2022 | Wind turbine design constraints |
| Molteno — Nature's Wind Turbines | 2022 | 10.3390/biomimetics7040161 | Betz limit aerodynamic efficiency |
| Ngwakwe — Payback Period Review | 2025 | 10.33146/2307-9878-2025-2(108)-59-66 | Financial payback methodology |

### 12.4 Data Provenance by Module

#### EcoSim
- **Climate data:** NASA POWER municipality averages → `municipality_climate_averages.csv`
- **Terrain data:** DEM-derived slope/elevation → `hydropower_suitability` table
- **Pricing data:** Scraped e-commerce → `cleaned_products_master.csv` → RAG knowledge base
- **Plant data:** Global Energy Monitor → `geothermal_plants.json`

#### EnergyHub
- **Historical trends:** DOE Power Statistics → `master_preprocessed.csv`
- **Forecasts:** Statsmodels ARIMA → `forecast_*_2025_2030.csv`
- **Map data:** Municipality scores → `municipalities` table → Redis cache
- **AI insights:** RAG + Groq LLM → `chart_ai_insights` table (cached)

#### Geothermal
- **Heat flow:** IHFC 2024 → `IHFC_2024_GHFDB_v.2026.03.txt`
- **Faults:** PHIVOLCS → `geothermal_faults.json`
- **Volcanoes:** Smithsonian → volcano dataset
- **Aquifers:** JGCRI / Zenodo → `All_merged.shp` (shapefile)
- **Plants:** Global Energy Monitor → `Geothermal-Power-Tracker.xlsx`

### 12.5 Data Processing Pipeline

```
Raw Sources
    |
    v
[PDF Extraction]  →  Tabula / pdfplumber  →  CSV files (data/windsurf_data_extraction/)
    |
    v
[Data Cleaning]   →  pandas / custom scripts  →  Cleaned CSVs
    |
    v
[Feature Engineering] →  python_scripts/terrain_pipeline/  →  Suitability scores
    |
    v
[ML Training]     →  Jupyter notebooks (data/DOE_Data_Extracted/*.ipynb)  →  Forecast CSVs
    |
    v
[Knowledge Building] →  rag_knowledge_builder.py  →  rag_knowledge_base.json
    |
    v
[Index Building]  →  rag_pipeline.py  →  rag_faiss.index
    |
    v
[Application]     →  FastAPI + React  →  LUMI Web App
```

---

## Part 13: User Flow & System Logic

### 13.1 New User Registration Flow

```
User visits /login
    |
    v
[Supabase Auth] OAuth (Google/GitHub) or Email+Password
    |
    v
[Trigger: handle_new_user()]
    - Creates row in `profiles` table (default plan: "free")
    - Creates row in `user_roles` table (default role: "user")
    |
    v
Redirect to /dashboard
    - Fetch profile from /protected/profile
    - Display welcome message, plan badge (Free)
```

### 13.2 EcoSim Simulation Flow

```
User navigates to /ecosim
    |
    v
Load municipalities dropdown (GET /ecosim/municipalities)
    |
    v
User selects municipality, enters bill/consumption, sets savings target
    |
    v
[Submit] GET /ecosim/?municipality_id=...&monthly_consumption=...&monthly_bill=...&desired_savings=...
    |
    v
Backend:
    1. Fetch climate data from CSV
    2. Fetch terrain data from Supabase
    3. Calculate solar, wind, hydro, geothermal outputs
    4. (If include_ai) Build prompt, call LLM (Gemini → fallback Groq)
    5. (If use_rag) Retrieve context from FAISS, inject into prompt
    6. Return JSON with results + optional AI analysis
    |
    v
Frontend displays:
    - Municipality info card
    - Consumption summary
    - 4 renewable option cards (Solar, Wind, Hydro, Geothermal)
    - Comparison table
    - AI insight panel (if requested)
    |
    v
[Save Simulation] POST /simulations (auth required)
    - Free tier: max 3 simulations
    - Premium: unlimited
    - Stores results_json in `saved_simulations` table
```

### 13.3 EnergyHub Dashboard Flow

```
User navigates to /energyhub
    |
    v
Parallel API calls:
    - GET /energyhub/overview
    - GET /energyhub/trends
    - GET /energyhub/map-data?metric=renewable_potential&level=province
    - GET /energyhub/source-breakdown
    |
    v
Frontend renders:
    - Overview cards (latest stats, forecast growth)
    - Historical trends chart (2003–2024) + forecast overlay (2025–2030)
    - Choropleth map (province-level renewable potential)
    - Source breakdown pie chart
    |
    v
User switches map metric to "geothermal"
    |
    v
Check cache: key = "lumi:suitability:geothermal:province"
    - Cache hit: return cached data
    - Cache miss: query municipalities table, apply proximity boost, aggregate by province, store in Redis
    |
    v
Map re-renders with geothermal scores
    |
    v
[Get AI Insight] GET /energyhub/ai-insight?use_llm=true
    - If use_llm=true: calls Groq LLM with chart summary context
    - Returns structured insight text
```

### 13.4 Chat Assistant Flow

```
User navigates to /chat
    |
    v
Create or resume chat session (Supabase `chat_sessions`)
    |
    v
Load previous messages from `chat_messages` table
    |
    v
User types message: "What solar system size do I need for 300 kWh/month in Batangas?"
    |
    v
Frontend POST /chat/ with { message, session_id, use_rag: true }
    |
    v
Backend:
    1. (If use_rag) retrieve_context(query, top_k=5)
       - Encode query with all-MiniLM-L6-v2
       - Search FAISS index
       - Filter by relevant renewable_type
    2. Build system prompt + user message + retrieved context
    3. Call Groq API (llama-3.3-70b-versatile)
    4. Parse response, extract sources
    5. Persist to chat_messages (user message + assistant reply)
    |
    v
Frontend displays:
    - Assistant reply with formatted text
    - Citations highlighted: [Source 1: Alibaba Marketplace]
    - Sources listed below message
```

### 13.5 Admin Portal Flow

```
Admin navigates to /admin
    |
    v
[Auth check] require_admin dependency
    - Verifies JWT
    - Checks user_roles.role IN ('admin', 'dev')
    - 403 if not admin
    |
    v
Admin Dashboard loads:
    - GET /admin/analytics → user counts, simulation counts, recent signups
    - GET /admin/users → paginated user list with roles and plans
    |
    v
Admin actions:
    - Ban user: POST /admin/users/{id}/ban
      → Sets profiles.is_active = false
      → Logs to admin_audit_log
    - Change role: POST /admin/users/{id}/role
      → Updates user_roles.role
      → Logs to admin_audit_log
    - Change plan: POST /admin/users/{id}/plan
      → Updates profiles.plan
      → Logs to admin_audit_log
    - View config: GET /admin/config
      → Returns system_config key-value pairs
    - Update config: POST /admin/config
      → Updates system_config (e.g., free_sim_limit)
```

### 13.6 Data Refresh Flow (Background)

```
[Monthly / On-demand]
    |
    v
Run python_scripts/ scripts:
    - NASA POWER data fetch (new month)
    - Terrain pipeline recalculation
    - Municipality suitability recomputation
    |
    v
Update Supabase tables:
    - municipality_climate_monthly (INSERT new rows)
    - municipalities (UPDATE scores)
    - hydropower_suitability (UPDATE terrain metrics)
    |
    v
Invalidate Redis cache:
    - invalidate_suitability_cache() → deletes all lumi:suitability:* keys
    |
    v
Rebuild RAG index (if knowledge base updated):
    - rag_knowledge_builder.py → regenerate rag_knowledge_base.json
    - rag_pipeline.ensure_index_built() → rebuild FAISS index
```

---

## Appendix: Environment Variables

| Variable | Required | Description | Used By |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | Google GenAI API key | `gemini_funcs.py` |
| `GROQ_API_KEY` | Yes | Groq API key | `groq_client.py`, `chat.py` |
| `LLM_PROVIDER` | No | "gemini" or "groq" (default: gemini) | `llm_client.py` |
| `SUPABASE_URL` | Yes | Supabase project URL | `supabase_service.py` |
| `SUPABASE_ANON_KEY` | Yes | Supabase anon/public key | `supabase_service.py` |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service role key | `supabase_service.py` |
| `SUPABASE_JWT_SECRET` | Yes | JWT signing secret | `auth.py` |
| `UPSTASH_REDIS_URL` | Yes | Redis connection URL | `redis_client.py` |
| `CORS_ORIGINS` | Yes | JSON array of allowed origins | `settings.py` |
| `APP_NAME` | No | API title (default: "LUMI API") | `settings.py` |

---

## Document Index

| Part | Title | Description |
|---|---|---|
| 1 | Project Overview & Repository Structure | What LUMI is, tech stack, folder layout |
| 2 | Backend Architecture | FastAPI entry, settings, auth, router aggregation |
| 3 | EcoSim Module | Routes, core service, solar/wind/hydro calculations |
| 4 | Geothermal Module | Feature engineering, plant proximity, routes |
| 5 | EnergyHub Module | Routes, service layer, ML predictor |
| 6 | AI / LLM System | RAG pipeline, Gemini, Groq, unified client, sanitizer |
| 7 | Authentication & User Management | Protected routes, simulations, admin portal |
| 8 | Database & Infrastructure | Supabase service, Redis, suitability builder, MCDA weights, schema |
| 9 | Frontend Architecture | React structure, API client, key pages |
| 10 | API Endpoint Reference | All routes with methods, auth, parameters, responses |
| 11 | Algorithms & Formulas | Solar, wind, hydro, geothermal, ARIMA, RAG math |
| 12 | Data Sources & Research Mapping | Datasets, NASA variables, papers, provenance, pipeline |
| 13 | User Flow & System Logic | End-to-end user journeys, admin actions, data refresh |

---

*End of LUMI Complete System Documentation*










