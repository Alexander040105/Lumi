# LUMI — Data-Driven Environmental Intelligence System

> A web-based platform for renewable energy simulation, national energy analytics, and AI-powered recommendations tailored for Philippine municipalities.

---

## Overview

**LUMI** is an integrated environmental intelligence system built to support the Philippines' transition toward sustainable energy. It combines a household-level renewable energy simulator (**EcoSim**), a national energy analytics dashboard (**EnergyHub**), and an AI-powered recommendation engine to help homeowners, community planners, and researchers make data-driven energy decisions.

The platform ingests municipal climate data from **NASA POWER**, national energy statistics from the **Philippine Department of Energy (DOE)**, and terrain data from **USGS SRTM / HydroSHEDS** to deliver accurate, location-specific renewable energy assessments.

---

## Key Features

### EcoSim — Household Renewable Energy Simulator

- **Municipality-level climate lookup** across 1,600+ Philippine municipalities
- **Solar output estimation** using irradiance, temperature, humidity, and dust-loss adjustments
- **Wind output estimation** via physics-based power-coefficient and capacity-factor calculations
- **Micro-hydropower estimation** using rainfall, DEM-derived hydraulic head, and terrain slope
- **Economic analysis**: installation cost, payback period, monthly savings, and CO₂ reduction
- **AI-powered recommendations** via Google Gemini, optionally enhanced with Retrieval-Augmented Generation (RAG)

### EnergyHub — National Energy Analytics & Forecasting

- **Interactive historical dashboard**: Philippine national energy statistics (2003–2024)
- **ARIMA-based demand forecasts**: 2025–2030 projections with confidence intervals
- **Interactive choropleth maps**: Province-level renewable potential using Leaflet
- **Generation mix breakdowns**: Coal, natural gas, renewables, hydro, solar, wind, geothermal, biomass
- **Grid-level analysis**: Luzon, Visayas, and Mindanao generation and peak demand
- **AI-assisted data-driven insights** for policy and planning contexts

### Authentication & Security

- Email/password and Google OAuth authentication via **Supabase Auth**
- JWT-protected FastAPI routes with role-based access
- Row-Level Security (RLS) on PostgreSQL tables
- Redis-backed session caching

---

## Tech Stack

### Frontend

- **React 18** with Vite
- **Tailwind CSS** + **shadcn/ui** component primitives
- **Leaflet** + **React-Leaflet** for interactive mapping
- **React Router** for client-side navigation
- **Zod** + **React Hook Form** for validation

### Backend

- **FastAPI** (Python) — RESTful API with Pydantic validation
- **Uvicorn** — ASGI server
- **Supabase** — Managed PostgreSQL + Auth
- **Redis** — Session caching and token storage
- **python-jose** — JWT encoding/decoding

### Machine Learning & AI

- **ARIMA(1,1,1)** — Core national energy demand forecasting model
- **statsmodels** — Statistical modeling and time-series diagnostics
- **scikit-learn** — Controlled Random Forest experiment and metrics
- **Google Gemini API** — AI analysis and natural-language recommendations
- **sentence-transformers + FAISS** — RAG vector search for equipment pricing context
- **LangChain + NLTK** — Document chunking and preprocessing for RAG

### Data & GIS

- **NASA POWER API** — Municipal climate data (solar irradiance, wind, rainfall, temperature)
- **USGS SRTM / HydroSHEDS** — DEM and terrain data for hydropower
- **rasterio, geopandas, richdem, whitebox** — Raster and terrain processing
- **Tabula** — DOE PDF table extraction

---

## Quick Start

### Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- A **Supabase** account (free tier sufficient)
- (Optional) **Upstash Redis** for caching

### 1. Clone & Environment Setup

```bash
git clone https://github.com/Alexander040105/Lumi.git
cd Lumi
```

Create a `.env` file in `fastapi-backend/` based on `.env.example`:

```bash
cp fastapi-backend/.env.example fastapi-backend/.env
```

Fill in your Supabase credentials and API keys (Gemini, Groq, NASA POWER settings).

### 2. Backend Setup

```bash
cd fastapi-backend
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd react-frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.

### 4. Run Everything at Once (Root)

```bash
cd Lumi
npm install
npm run dev
```

This uses `concurrently` to spin up both the React dev server and the FastAPI backend simultaneously.

---

## Project Structure

```
Lumi/
├── docs/                           # Project documentation (organized by category)
│   ├── 01-Project-Overview/       # README, setup, development guide
│   ├── 02-Architecture/            # API, frontend, and system architecture
│   ├── 03-Modules/                 # EcoSim & EnergyHub module docs
│   ├── 04-ML-Data-Science/         # ML models, methodology, data sources
│   ├── 05-Setup-Guides/            # Auth, shadcn, Supabase, Tailwind
│   ├── 06-Technical-Resources/     # Methodology & tech recommendations
│   ├── 07-Data-Extraction-Reports/ # Formula references & data quality
│   └── 08-Requirements/            # Tech stack & requirements specs
│
├── react-frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── components/ui/          # shadcn/ui components
│   │   ├── context/                # AuthContext, etc.
│   │   ├── pages/                  # Dashboard, EcoSim, EnergyHub
│   │   ├── routes/                 # React Router configuration
│   │   ├── services/               # API client, Supabase client
│   │   └── styles/                 # Tailwind + custom CSS
│   └── package.json
│
├── fastapi-backend/                # FastAPI Python backend
│   ├── app/
│   │   ├── dependencies/           # Auth dependencies
│   │   ├── ml/                     # ML prediction service (ARIMA artifacts)
│   │   ├── routes/                 # API routers
│   │   ├── schemas/                # Pydantic models
│   │   ├── services/               # Business logic (EcoSim, RAG, etc.)
│   │   └── auth/                   # JWT handling
│   └── requirements.txt
│
├── DOE_Data_Extracted/             # DOE data, ARIMA notebooks, and CSV artifacts
│   ├── DOE_arima_forecasting.ipynb
│   ├── DOE_datacleaning.ipynb
│   ├── DOE_model_registry.ipynb
│   ├── master_preprocessed.csv
│   ├── forecast_consumption_2025_2030.csv
│   └── model_comparison_results.csv
│
├── python_scripts/                 # Terrain & climate ETL scripts
├── scraped_data/                   # E-commerce scrapers (Alibaba, Amazon, Lazada, Shopee)
├── windsurf_data_extraction/       # PDF extraction, cleaning, and RAG conversion
└── requirements.txt                # Consolidated Python dependencies
```

---

## Machine Learning Pipeline

The EnergyHub forecasting module uses a **pre-trained ARIMA(1,1,1)** model, trained offline on DOE data (2003–2020) and evaluated on 2021–2024.

| Model | MAE | RMSE | MAPE |
| --- | --- | --- | --- |
| Linear Trend Regression | 5,994 | 7,342 | 4.97 % |
| Holt Linear Smoothing | 6,558 | 7,998 | 5.44 % |
| Naive with Drift | 6,709 | 8,128 | 5.57 % |
| **ARIMA(1,1,1)** | **6,829** | **8,257** | **5.67 %** |
| SARIMAX + Exogenous | 9,914 | 11,459 | 8.28 % |
| Random Forest | 15,957 | 17,806 | 13.41 % |

ARIMA was selected for its balance of accuracy, interpretability, and minimal deployment footprint. All forecasting is served from pre-computed CSV artifacts — no runtime model training occurs.

See `docs/04-ML-Data-Science/` for full methodology, data sources, and model analysis.

---

## Data Sources

| Source | Data | Usage |
| --- | --- | --- |
| **DOE Philippines** | National power statistics (2003–2024) | Historical trends, ARIMA training, generation mix |
| **NASA POWER API** | Municipal climate (irradiance, wind, rainfall, temp) | EcoSim solar, wind, and hydro calculations |
| **Global Solar Atlas 2.0 (Solargis / World Bank)** | GHI, DNI, DIF, GTI, PVOUT, TEMP | High-resolution municipal solar output and irradiance |
| **Global Wind Atlas (DTU / World Bank)** | Wind speed at 10/50/100 m | Hub-height municipal wind resource estimates |
| **USGS SRTM / HydroSHEDS** | DEM, elevation, river networks | Hydropower hydraulic head and terrain analysis |
| **E-commerce scrapers** | Equipment pricing (solar, wind, hydro) | RAG knowledge base for AI cost estimates |

Solar and wind atlas data are licensed under CC BY 4.0.
- Solar: © 2019 Solargis, published by the World Bank in the Global Solar Atlas 2.0.
- Wind: © DTU / World Bank, Global Wind Atlas.

---

## API Endpoints (Key)

### EcoSim

- `GET /api/v1/ecosim/municipalities` — List all municipalities
- `GET /api/v1/ecosim/?municipality_id={id}&monthly_consumption=...&monthly_bill=...` — Run simulation
- `GET /api/v1/ecosim/...&include_ai=true` — Simulation + Gemini analysis
- `GET /api/v1/ecosim/...&include_ai=true&use_rag=true` — Simulation + RAG-backed analysis

### EnergyHub

- `GET /api/v1/energyhub/overview` — Latest statistics + forecast summary
- `GET /api/v1/energyhub/forecast?metric=consumption` — 2025–2030 forecast
- `GET /api/v1/energyhub/trends` — Historical time-series data
- `GET /api/v1/energyhub/map-data` — Choropleth map data
- `GET /api/v1/energyhub/model-comparison` — Test-set performance across all models

---

## Documentation

All project documentation has been organized into categorized folders under `docs/`:

| Category | Location |
| --- | --- |
| Project Overview & Setup | `docs/01-Project-Overview/` |
| System Architecture | `docs/02-Architecture/` |
| Module Specifications | `docs/03-Modules/` |
| ML & Data Science | `docs/04-ML-Data-Science/` |
| Setup Guides | `docs/05-Setup-Guides/` |
| Technical Resources | `docs/06-Technical-Resources/` |
| Data Extraction Reports | `docs/07-Data-Extraction-Reports/` |
| Requirements Specs | `docs/08-Requirements/` |

---

## Deployment

### Vercel (full-stack, recommended)

The repository is now configured for a single-project Vercel deployment:

- `vercel.json` builds the Vite frontend and runs `fastapi-backend/main.py` from `api/index.py` as a Vercel Python Function.
- Heavy ML/RAG packages (`sentence-transformers`, `faiss-cpu`) are excluded from the Vercel Function bundle.
- Optional companion ML worker for full RAG/ETL can be set via `ML_WORKER_URL`.

See `docs/VERCEL_DEPLOYMENT_GUIDE.md` for environment variables and step-by-step deploy instructions.

### Docker Compose (self-hosted)

For a containerized self-hosted deployment, this project is designed to run using Docker Compose. See `DEPLOYMENT_GUIDE.md` for a detailed setup.

### Database & Cache

- **Supabase** — PostgreSQL + Auth (free tier)
- **Upstash Redis** — Session caching (free tier)

---

## Contributing

This is a thesis project for the **Bachelor of Science in Computer Science Major in Data Science** at the **University of Perpetual Help System DALTA - Molino Campus**. Contributions, feedback, and academic collaboration are welcome.

---

## License

This project is licensed for academic and research purposes. See the repository for full terms.

---

*Built with React, FastAPI, Supabase, and a lot of Philippine climate data.*