# LUMI: Methodology and Technical Resources

## Chapter 3 — Methodology

**System:** LUMI Environmental Intelligence System  
**Scope:** Documentation of technologies, data sources, development methodology, and system architecture for the LUMI undergraduate research project.

---

## 3.1 Research Design

LUMI (Localized Utility Management Intelligence) is a web application that assists Philippine households, communities, and researchers in understanding energy consumption patterns and renewable energy feasibility. The system was developed under a **developmental research design** combining quantitative analysis, predictive modeling, physics-based simulation, and AI-generated insights.

---

## 3.2 System Development Approach

Development followed an **iterative methodology** blending Agile principles with traditional systems analysis:

```
Planning -> Data Collection -> System Design -> Development -> Testing -> Deployment
```

| Stage | Key Activities |
|-------|----------------|
| **Planning** | Stakeholder requirements gathering; scope definition (household simulation + national analytics); technology stack selection |
| **Data Collection** | DOE energy statistics acquisition; NASA POWER climate data extraction; DEM terrain processing |
| **System Design** | Modular architecture; PostgreSQL schema for Philippine administrative hierarchy; RESTful API specification |
| **Development** | Parallel tracks: React frontend, FastAPI backend, Python data pipeline; incremental module delivery |
| **Testing** | API manual testing; Vite production builds; notebook validation; end-to-end integration |
| **Deployment** | Local Uvicorn/Vite servers; Supabase managed PostgreSQL; reproducible CSV artifacts |

---

## 3.3 System Architecture

LUMI employs a **three-tier client-server architecture**:

```
Presentation Tier (React SPA)
         |
         | HTTP / REST / JSON
         v
Application Tier (FastAPI Python)
         |
         | SQL / REST
         v
Data Tier (Supabase PostgreSQL + Filesystem)
```

### Data Flow
1. User interacts with React frontend (forms, maps, dashboards).
2. Frontend sends HTTP requests to FastAPI via a centralized API client.
3. Backend queries Supabase or loads pre-computed CSV artifacts.
4. Backend executes physics-based calculations (EcoSim) or statistical inference (EnergyHub).
5. Backend optionally calls Google Gemini LLM for narrative insights.
6. JSON response renders as charts, tables, and AI-generated text panels.

### Modules
| Module | Purpose |
|--------|---------|
| **EcoSim** | Household renewable energy simulation (solar, wind, hydro) |
| **EnergyHub** | National energy statistics, trends, and ARIMA forecasting |
| **AI Insights** | LLM-generated narrative explanations |
| **Model Registry** | Forecasting model versioning and activation |
| **RAG System** | Retrieval-augmented generation for EcoSim recommendations |

---

## 3.4 Technologies Used

### 3.4.1 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3.1 | UI library for component-based interfaces |
| Vite | 5.4.2 | Build tool and development server |
| React Router DOM | 6.26.0 | Client-side routing |
| TailwindCSS | 4.0.0 | Utility-first CSS framework |
| Radix UI | 1.1.2 | Accessible UI primitives (Dialog, Dropdown, Tooltip) |
| Lucide React | 0.445.0 | Icon library |
| Leaflet / React-Leaflet | 1.9.4 / 4.2.1 | Interactive maps |
| React Hook Form | 7.53.0 | Form state management |
| Zod | 3.23.8 | Schema validation |
| Sonner | 1.5.0 | Toast notifications |
| Supabase JS Client | 2.45.0 | Direct database queries |

### 3.4.2 Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.115.0 | REST API framework |
| Uvicorn | 0.30.6 | ASGI server |
| Python | 3.13.2 | Primary language |
| Pydantic / Pydantic-Settings | 2.x / 2.4.0 | Data validation and configuration |
| python-dotenv | 1.0.1 | Environment variable management |

### 3.4.3 Database

| Technology | Purpose |
|------------|---------|
| Supabase (PostgreSQL) | Managed relational database with RLS |
| psycopg2-binary | PostgreSQL Python adapter |
| supabase-py | 2.10.0 | Python REST client |

### 3.4.4 Machine Learning & Data Science

| Library | Purpose |
|---------|---------|
| pandas | Data manipulation |
| numpy | Numerical computing |
| matplotlib | Visualization |
| scikit-learn | Regression, Random Forest, metrics (MAE, RMSE, MAPE) |
| statsmodels | ARIMA, SARIMAX, Holt smoothing, ADF test |

### 3.4.5 AI & NLP

| Technology | Version | Purpose |
|------------|---------|---------|
| Google GenAI | 0.6.0 | Gemini LLM client |
| Groq | 0.18.0 | Fallback LLM API |
| FAISS (CPU) | 1.9.0.post1 | Vector similarity search |
| Sentence-Transformers | 3.0.1 | Text embeddings |
| LangChain | — | LLM orchestration |

### 3.4.6 GIS & Terrain

| Library | Purpose |
|---------|---------|
| rasterio | DEM raster I/O |
| geopandas / shapely | Geospatial DataFrame and geometry |
| rasterstats | Zonal statistics |
| richdem | DEM analysis (slope, ruggedness) |

### 3.4.7 PDF Processing

| Library | Purpose |
|---------|---------|
| pymupdf / pdfplumber | Text and table extraction |
| camelot-py | PDF table extraction |
| pytesseract / paddleocr | OCR |

### 3.4.8 Development Tools

| Tool | Purpose |
|------|---------|
| Git / GitHub | Version control |
| Visual Studio Code | IDE |
| Jupyter Notebook | Data exploration and prototyping |
| Postman / HTTPie | API testing |

---

## 3.5 Data Sources

### 3.5.1 DOE Philippine Energy Statistics

| Attribute | Value |
|-----------|-------|
| **Source** | Department of Energy (DOE) — Power Statistics Division |
| **Period** | 2003–2024 (22 annual observations) |
| **Features** | Consumption (GWh), generation (GWh), peak demand (MW), dependable capacity (MW), renewable generation (GWh), plant-type breakdown |
| **Format** | PDF → manual extraction → CSV → `master_preprocessed.csv` |
| **Usage** | EnergyHub trends, source breakdown, ARIMA input |
| **Limitations** | National-level only; no municipal consumption; annual only |

### 3.5.2 NASA POWER Climate Data

| Attribute | Value |
|-----------|-------|
| **Source** | NASA Prediction of Worldwide Energy Resources (POWER) API |
| **Endpoint** | `power.larc.nasa.gov/api/temporal/daily/point` |
| **Period** | 2018–present (monthly averages) |
| **Variables** | Temperature, humidity, precipitation, wind speed, solar irradiance, cloud amount, surface pressure, elevation, air density |
| **Coverage** | All 1,634+ Philippine municipalities |
| **Usage** | EcoSim solar/wind/hydro calculations |
| **Storage** | `municipality_climate_monthly` table |

### 3.5.3 Terrain & Hydropower

| Attribute | Value |
|-----------|-------|
| **Source** | DEM raster data (SRTM/ASTER — requires verification) |
| **Processing** | Elevation, slope, ruggedness, hydraulic head, runoff potential |
| **Storage** | `hydropower_suitability` table |
| **Usage** | EcoSim micro-hydropower feasibility |

### 3.5.4 Administrative Boundaries

| Level | Count | Table |
|-------|-------|-------|
| Regions | 17 | `regions` |
| Provinces | 82 | `provinces` |
| Municipalities | 1,634+ | `municipalities` |
| Barangays | 42,000+ | `barangays` |
| **Source** | Philippine Statistics Authority (PSA) shapefiles |

---

## 3.6 Machine Learning Implementation

### 3.6.1 Objective

Forecast national **total electricity consumption (GWh)** and **peak demand (MW)** for 2025–2030.

### 3.6.2 Rationale for Statistical Models

With only **22 annual observations**, advanced ML (LSTM, XGBoost, LightGBM) would severely overfit. Classical models are parsimonious, interpretable, and computationally efficient.

### 3.6.3 Models Evaluated

| Model | Family | Purpose |
|-------|--------|---------|
| Naive with Drift | Baseline | Accuracy floor |
| Linear Trend Regression | Regression | Coefficient = annual growth rate |
| ARIMA(1,1,1) | Box-Jenkins | Core thesis model |
| Holt Linear Smoothing | Smoothing | Trend-aware baseline |
| SARIMAX(1,1,1) | Box-Jenkins + Exogenous | External predictors: renewable share, capacity margin |
| Random Forest | ML | Controlled experiment to demonstrate overfitting |

### 3.6.4 ARIMA Parameters

- **d = 1**: ADF test confirmed non-stationarity.
- **p = 1**: PACF significant at lag 1.
- **q = 1**: ACF significant at lag 1.

### 3.6.5 Evaluation Protocol

- **Train**: 2003–2020 (18 years)
- **Test**: 2021–2024 (4 years, held-out)
- **Metrics**: MAE, RMSE, MAPE

### 3.6.6 Test Results

| Model | MAE (GWh) | MAPE (%) |
|-------|-----------|----------|
| Linear Trend Regression | 5,993.83 | **4.97** |
| Holt Linear Smoothing | 6,557.72 | 5.44 |
| Naive with Drift | 6,709.32 | 5.57 |
| ARIMA(1,1,1) | 6,829.09 | 5.67 |
| SARIMAX(1,1,1) + Exog | 9,913.65 | 8.28 |
| Random Forest Regression | 15,957.41 | 13.41 |

**Key Finding:** Linear Trend Regression performed best. Random Forest confirmed overfitting: training MAPE 1.45% vs. test MAPE 13.41% (11.95% gap), validating the statistical approach.

### 3.6.7 Deployment

The best model is retrained on the full dataset (2003–2024). Pre-computed CSVs (`forecast_consumption_2025_2030.csv`, `forecast_peak_demand_2025_2030.csv`) are loaded at runtime. No runtime retraining occurs.

### 3.6.8 Model Registry

The `ml_model_registry` table tracks:
- `model_name`, `model_version`, `model_type`
- `target_variable`, `train_date`
- `metrics` (JSONB: MAE, RMSE, MAPE)
- `model_path`, `is_active`

Workflow: train → insert → activate best → backend queries `is_active = true`.

---

## 3.7 AI Implementation

### 3.7.1 LLM Configuration

| Attribute | Value |
|-----------|-------|
| **Primary Model** | Gemini 2.5 Flash (Google GenAI SDK) |
| **Fallback** | Groq API |
| **Temperature** | 0.3–0.5 |
| **Max Tokens** | 2,000–2,500 |

### 3.7.2 Prompt Engineering

- **Chart-specific prompts**: Each chart type has a dedicated template with analytical questions.
- **Overview prompt**: 5-paragraph analysis (current situation, renewable share, forecast implications, decarbonization barriers, policy recommendations).
- **Constraints**: "500–700 words; plain language; include specific data points."

### 3.7.3 Insight Caching

AI responses are cached in `chart_ai_insights`:
- Up to **3 variants** stored per chart+hash.
- **Rotation**: Randomly selects among variants on cache hit.
- **`force_refresh`**: Query parameter to bypass cache.
- **Eviction**: Oldest entries removed when limit exceeded.

### 3.7.4 RAG System (EcoSim)

| Component | Technology |
|-----------|------------|
| Document ingestion | `pymupdf`, `pdfplumber` |
| Text splitting | LangChain |
| Embeddings | Sentence-Transformers |
| Vector store | FAISS (CPU) |
| Generation | Gemini 2.5 Flash |

**Workflow**: Simulate → construct query → FAISS retrieves relevant chunks → inject into Gemini prompt → generate personalized recommendation.

---

## 3.8 System Modules

### 3.8.1 EcoSim

**Purpose:** Household renewable energy feasibility simulation.

**Inputs:** Municipality, house size, roof area, monthly bill, coordinates.

**Calculations:**
- **Solar**: Temperature derating, dust loss, humidity degradation, performance ratio. Default: 2 × 550 W panels.
- **Wind**: Betz-limit power equation with capacity factor using `wind_products_joined_betz.csv`.
- **Hydro**: Rational-method runoff + micro-hydro equation (`P = ρ·g·Q·H·η`) using `hydropower_suitability` terrain metrics.

**Outputs:** Potential (kWh/month, kWh/year), recommended source, budget, payback period, savings, carbon reduction, scenario comparison.

### 3.8.2 EnergyHub

**Purpose:** National energy analytics and forecasting.

**Features:**
- Historical trends (2003–2024)
- ARIMA forecasts (2025–2030)
- Source breakdown by plant type
- Grid-level generation breakdown
- Choropleth map for renewable potential
- Model comparison (MAE/RMSE/MAPE)
- AI-generated insights per chart

---

## 3.9 Database Schema

### Core Tables

| Table | PK | Purpose |
|-------|-----|---------|
| `regions` | `region_id` | 17 regions |
| `provinces` | `province_id` | 82 provinces |
| `municipalities` | `municipality_id` | 1,634+ municipalities |
| `barangays` | `barangay_id` | 42,000+ barangays |
| `municipality_climate_monthly` | `(municipality_id, year, month)` | NASA POWER climate data |
| `hydropower_suitability` | `municipality_id` | Terrain metrics |
| `ml_model_registry` | `model_id` (UUID) | Model versioning |
| `chart_ai_insights` | `id` (UUID) | Cached AI insights |

### Views

| View | Purpose |
|------|---------|
| `regional_lookup` | Denormalized region → province → municipality → barangay join with coordinates |

---

## 3.10 API Design

### EcoSim Router (`/api/v1/ecosim`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard (climate, renewables, economics, AI) |
| `/municipalities` | GET | Municipality dropdown list |
| `/` | POST | Save/simulate configuration |

### EnergyHub Router (`/api/v1/energyhub`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/overview` | GET | Latest stats + forecast |
| `/forecast` | GET | 2025–2030 ML forecast |
| `/trends` | GET | Historical time series |
| `/map-data` | GET | Choropleth data |
| `/source-breakdown` | GET | Generation by plant type |
| `/grid-breakdown` | GET | Generation by grid |
| `/model-comparison` | GET | Test-set accuracy metrics |
| `/ai-insight` | GET | Narrative insight |
| `/analyze-chart` | POST | AI interpretation of specific chart |

---

## 3.11 Development Environment

| Component | Specification |
|-----------|---------------|
| **OS** | Windows 10/11 |
| **Python** | 3.13.2 (root `.venv` at project root) |
| **Node.js** | 18+ (for Vite/React) |
| **IDE** | Visual Studio Code |
| **Database** | Supabase Cloud PostgreSQL |
| **Dev Servers** | Uvicorn (backend, port 8000); Vite (frontend, port 5173) |
| **API Base URL** | `http://127.0.0.1:8000/api/v1` |
| **Frontend Dev URL** | `http://127.0.0.1:5173` |

---

## 3.12 Security & Configuration

- **CORS**: Allows `localhost:5173` and production domain.
- **Secrets**: API keys stored in `.env`; excluded from version control.
- **RLS**: Supabase Row Level Security policies enforce data access control.
- **Validation**: Pydantic schemas enforce type-safe API contracts.

---

*End of Methodology Documentation*
