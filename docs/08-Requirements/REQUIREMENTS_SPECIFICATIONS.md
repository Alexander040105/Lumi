# LUMI — Requirements Specifications

> Document generated from repository analysis. Covers tools, functional requirements, software/AI/algorithms, hardware, and testing artifacts.

---

## 1. Tools, Technologies, or Platforms Used

### 1.1 Development & Runtime Platforms
- **Node.js 18+** — JavaScript runtime for frontend tooling
- **Python 3.11+** — Backend runtime and ML/data pipelines
- **Windows / cross-platform** — Primary development OS

### 1.2 Version Control & Collaboration
- **Git** — Source control
- **GitHub** — Remote repository hosting

### 1.3 Cloud Services & External APIs
| Platform / API | Purpose |
|---------------|---------|
| **Supabase** | Managed PostgreSQL, Auth (email/password + OAuth), Row-Level Security (RLS) |
| **Render** | Primary target for FastAPI backend deployment |
| **Vercel** | Recommended for React frontend static hosting |
| **NASA POWER API** | Municipal climate data ingestion (irradiance, wind, temperature, rainfall) |
| **Google Gemini API** | LLM summaries, AI analysis, RAG-based recommendations |
| **Groq API** | Fast LLM inference fallback |
| **Open-Meteo** | Supplementary climate data (optional) |

### 1.4 Data Extraction & GIS Sources
| Source | Usage |
|--------|-------|
| **DOE Philippines** | National energy statistics (PDF manual extraction) |
| **PSA** | Household energy consumption baselines |
| **Global Solar Atlas** | Solar potential reference |
| **Global Wind Atlas** | Wind feasibility screening |
| **USGS SRTM / HydroSHEDS** | Elevation, terrain, river network data for hydropower |
| **OpenStreetMap** | Geographic context |
| **Philippine Geoportal** | Local geographic layers |

---

## 2. Functional Requirements

### 2.1 Core Modules

#### EnergyHub
- Display historical Philippine national energy statistics (2003–2024)
- Provide ARIMA-based demand forecasts (2025–2030)
- Render an interactive choropleth map for renewable potential (province-level)
- Show energy source comparisons and grid-level breakdowns
- Deliver AI-assisted data-driven insights

#### EcoSim (Household Renewable Simulation)
- Municipality-level climate lookup (1,600+ Philippine municipalities)
- Solar output estimation using irradiance, temperature, humidity, and dust loss
- Wind output estimation using physics-based power coefficient and capacity factor (Betz limit)
- Micro-hydropower estimation using rainfall, runoff, slope, and DEM-derived hydraulic head
- Economic comparison: installation cost, payback period, monthly savings, carbon reduction
- Scenario comparison: current bill vs renewable offset
- Optional AI-powered analysis via Gemini (standard or RAG-backed)

#### Forecasting Module
- Predict future energy demand and consumption trends
- Support proactive planning with shortage predictions
- Present forecasts with confidence intervals

### 2.2 Authentication & Authorization
- Email/password sign-up and sign-in
- Google OAuth integration
- JWT token validation on protected FastAPI routes
- Row-Level Security (RLS) on Supabase tables
- Session caching with Redis

### 2.3 User Roles & Targets
- **Homeowners / students** — EcoSim household simulations
- **Community planners / barangay officials** — Local renewable feasibility
- **Researchers / government stakeholders** — National energy trends and forecasts

---

## 3. Software / Framework / Tools, AI, Algorithms Requirements

### 3.1 Frontend Stack

| Technology | Version | Role |
|-----------|---------|------|
| **React** | ^18.3.1 | UI framework |
| **Vite** | ^5.4.2 | Build tool and dev server |
| **React Router DOM** | ^6.26.0 | Client-side routing |
| **Tailwind CSS** | ^4.0.0 | Utility-first styling |
| **shadcn/ui** | — | Copied-in UI component primitives |
| **Radix UI** | ^1.1.x | Headless accessible UI primitives (Dialog, Dropdown, Tooltip, Slot) |
| **Leaflet** | ^1.9.4 | Interactive maps |
| **React-Leaflet** | ^4.2.1 | React bindings for Leaflet |
| **Lucide React** | ^0.445.0 | Icon library |
| **Zod** | ^3.23.8 | Schema validation |
| **React Hook Form** | ^7.53.0 | Form state management |
| **@hookform/resolvers** | ^3.9.1 | Zod resolver for RHF |
| **Sonner** | ^1.5.0 | Toast notifications |
| **Tailwind Merge / clsx / class-variance-authority** | — | Class name utilities |

### 3.2 Backend Stack

| Technology | Version | Role |
|-----------|---------|------|
| **FastAPI** | 0.115.0 | Web framework |
| **Uvicorn** | 0.30.6 | ASGI server |
| **Pydantic** | — | Data validation and settings management |
| **Pydantic Settings** | 2.4.0 | Environment-based configuration |
| **python-dotenv** | 1.0.1 | `.env` file loading |
| **Supabase Python Client** | 2.10.0 | Database and Auth SDK |
| **python-jose** | 3.3.0 | JWT encoding/decoding |
| **Redis** | 5.0.8 | Session/cache store |
| **HTTPX** | 0.27.2 | Async HTTP client |

### 3.3 Machine Learning & Data Science Libraries

| Library | Role |
|---------|------|
| **pandas** | Data manipulation and time-series preprocessing |
| **numpy** | Numerical computing |
| **statsmodels** | ARIMA / SARIMA / SARIMAX forecasting |
| **scikit-learn** | Random Forest, regression baselines, metrics |
| **torch** | Deep learning runtime (available but not primary) |
| **matplotlib** | Static plotting and EDA visualization |

### 3.4 AI / LLM / RAG Stack

| Technology | Role |
|-----------|------|
| **Google GenAI** | Gemini API client for LLM calls |
| **google-generativeai** | Supplementary Google AI SDK |
| **Groq** | Fast LLM inference client |
| **sentence-transformers** | Text embedding model for RAG retrieval |
| **FAISS-CPU** | Vector similarity search index |
| **transformers** | Hugging Face model hub access |
| **LangChain** | LLM chaining and text splitting utilities |
| **NLTK** | Text preprocessing for RAG pipeline |
| **deep-translator** | Translation utilities |

### 3.5 GIS / Raster / Terrain Processing

| Library | Role |
|---------|------|
| **rasterio** | GeoTIFF/DEM raster I/O |
| **geopandas** | Geospatial vector data manipulation |
| **shapely** | Geometric operations |
| **rasterstats** | Zonal statistics on rasters |
| **pyproj** | Coordinate reference system transformations |
| **richdem** | DEM terrain analysis |
| **whitebox** | Advanced geospatial processing |
| **folium** | Interactive map generation (Python) |

### 3.6 Web Scraping & PDF / Document Processing

| Library | Role |
|---------|------|
| **Selenium** | Browser automation for e-commerce scrapers |
| **Playwright** | Modern browser automation |
| **BeautifulSoup4 + lxml** | HTML parsing |
| **requests + urllib3** | HTTP requests |
| **PyMuPDF** | PDF text extraction |
| **pdfplumber** | Table extraction from PDFs |
| **camelot-py** | Lattice/stream table extraction |
| **tabula-py** | PDF table parsing |
| **pytesseract + paddleocr + Pillow** | OCR and image processing |

### 3.7 Additional Python Tools

| Library | Role |
|---------|------|
| **Flask** (with CORS, RESTful, SQLAlchemy, Migrate, Login, WTForms, Mail, Session, Bcrypt) | Alternative monolithic backend (available in stack) |
| **gunicorn + werkzeug** | WSGI server and utilities |
| **psycopg2-binary** | PostgreSQL adapter |
| **aiosqlite** | Async SQLite support |
| **cryptography + email-validator** | Security and validation |
| **pandera** | DataFrame validation |
| **tqdm + python-dateutil** | Progress bars and date parsing |
| **ipykernel + notebook** | Jupyter notebooks for EDA and ARIMA experiments |

### 3.8 Root-Level Orchestration

| Tool | Role |
|------|------|
| **concurrently** | Run frontend (`vite`) and backend (`uvicorn`) simultaneously |
| **Tailwind CSS v4** | PostCSS + Vite integration |
| **autoprefixer + postcss** | CSS processing |

---

## 4. Hardware Requirements

### 4.1 Development Environment
- **OS**: Windows 10/11 (current dev environment), Linux/macOS compatible
- **CPU**: Multi-core x86_64 processor
- **RAM**: Minimum 8 GB recommended; 16 GB preferred for GIS/ML workloads
- **Storage**: ~2 GB for repository, virtual environments, and node_modules
- **GPU**: Not required; all inference is CPU-based

### 4.2 Deployment / Hosting Constraints (Render Free Tier)
| Resource | Limit | Implication |
|----------|-------|-------------|
| **RAM** | 512 MB | Lightweight models only; no heavy DL frameworks at runtime |
| **CPU** | Shared (ephemeral) | Cold-start 15–30 s after idle |
| **Disk** | 0.5 GB (ephemeral) | Static CSV artifacts preferred over large model binaries |
| **Max request time** | 100 s | AI calls must be non-blocking or cached |

### 4.3 Production Recommendations
- **Render Starter tier** (1 GB RAM) or higher for sustained traffic
- **Persistent paid instance** or cron-based keep-alive to mitigate cold starts
- **Supabase free tier** sufficient for thesis/demo scale
- **Redis (Upstash free tier)** for caching LLM outputs and forecast results

---

## 5. Testing Scripts / Code

### 5.1 Backend Test Scripts (FastAPI `app/services/`)

| Script | Purpose |
|--------|---------|
| `test_full_pipeline.py` | End-to-end validation of Groq client, unified LLM client, RAG retrieval, and RAG + Gemini end-to-end analysis |
| `test_rag_pipeline.py` | Knowledge base building, FAISS index construction, retrieval accuracy tests, and end-to-end Gemini RAG tests |
| `test_retrieval_only.py` | Isolated FAISS/vector retrieval testing |
| `test_rag_normalize.py` | RAG response normalization and post-processing tests |
| `test_prompt_inspection.py` | LLM prompt template inspection and validation |
| `test_gemini_mock.py` | Mocked Gemini API interaction tests |

### 5.2 Manual Backend Testing (cURL / Browser)
- `GET /api/v1/ecosim/municipalities` — Municipality list (1,600+ entries)
- `GET /api/v1/ecosim/?municipality_id={id}&monthly_consumption=350&monthly_bill=5000` — Simulation dashboard
- `GET /api/v1/ecosim/...&include_ai=true` — With Gemini analysis
- `GET /api/v1/ecosim/...&include_ai=true&use_rag=true&rag_query=...` — With RAG-backed AI
- `GET /api/v1/energyhub/overview` — Latest stats + forecast summary
- `GET /api/v1/energyhub/forecast?metric=consumption` — 2025–2030 ARIMA forecast
- `GET /api/v1/energyhub/map-data?metric=renewable_potential` — Choropleth data
- `GET /api/v1/energyhub/ai-insight` — Data-backed narrative

### 5.3 Frontend Manual Testing
- `npm run dev` → `http://localhost:5173`
- Verify: Login/logout, Dashboard protected data load, EcoSim form → results, EnergyHub map + charts, AI Analysis panel

### 5.4 ML / Data Pipeline Notebooks (`DOE_Data_Extracted/`)
- `DOE_datacleaning.ipynb` — DOE PDF data extraction and cleaning
- `DOE_arima_forecasting.ipynb` — Offline ARIMA model training and forecast generation
- `DOE_model_registry.ipynb` — Model artifact tracking and comparison

### 5.5 E-Commerce Scrapers (`scraped_data/`)
- `alibaba_scraper.py`
- `amazon_scraper.py`
- `lazada_scraper.py`
- `shopee_scraper.py`

### 5.6 Data Extraction & RAG Conversion (`windsurf_data_extraction/`)
- `extract_compendium.py`
- `pdf_extractor.py`
- `rag_converter.py`
- `cleaner.py`
- `run_extraction.py`

### 5.7 No Formal Unit Test Framework Detected
- No `pytest.ini`, `pytest`, or organized `tests/` directory found in the repository
- Testing is currently script-based and manual

---

*Document compiled from repository artifacts: `package.json`, `requirements.txt`, architecture guides (`ECOSIM_ARCHITECTURE.md`, `ENERGYHUB_ARCHITECTURE.md`), ML analysis (`LUMI_ML_MODEL_ANALYSIS.md`, `LUMI_METHODOLOGY_ML.md`), tech recommendations (`LUMI_TECH_RECOMMENDATIONS.md`), development guides, and source code inspection.*
