# EnergyHub Module — Architecture & Implementation Guide

## Overview

The **EnergyHub** module is the predictive analytics and energy visualization component of the LUMI Environmental Intelligence System. It provides:

- Historical Philippine national energy statistics (2003–2024)
- ARIMA-based demand forecasts (2025–2030)
- Interactive choropleth map for renewable potential
- Energy source comparison and grid-level breakdowns
- AI-assisted data-driven insights

**Target users:** Students, researchers, communities, and government-related stakeholders.
**Disclaimer:** Educational insights only — not a professional energy planning replacement.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND                           │
│  ┌─────────────┐  ┌──────────┐  ┌─────────┐  ┌──────────────┐  │
│  │ EnergyHub   │  │ Energy   │  │ Energy  │  │ AiInsight  │  │
│  │ Overview    │  │ Trends   │  │ Sources │  │ Panel      │  │
│  └─────────────┘  └──────────┘  └─────────┘  └──────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    EnergyMap (Choropleth)                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                         services/energyhub.js                    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP (fetch)
┌──────────────────────────────▼──────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │   /api/v1/energyhub                                         ││
│  │   ├── GET /overview          → Latest stats + forecast      ││
│  │   ├── GET /forecast          → 2025-2030 ML forecast        ││
│  │   ├── GET /trends            → Historical time series       ││
│  │   ├── GET /map-data          → Choropleth data points       ││
│  │   ├── GET /source-breakdown  → Generation by plant type     ││
│  │   ├── GET /grid-breakdown    → Generation by grid           ││
│  │   ├── GET /model-comparison  → Test-set MAE/RMSE/MAPE      ││
│  │   └── GET /ai-insight        → Narrative + recommendation   ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ energyhub.py │  │ energyhub.py │  │ predictor.py (ML)    │   │
│  │   Router     │  │   Service    │  │   Offline ARIMA       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │ SQL / REST
┌──────────────────────────────▼──────────────────────────────────┐
│                     SUPABASE POSTGRESQL                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐ │
│  │ regions  │  │ provinces│  │municipalities│ │ municipality_ │ │
│  │          │  │          │  │              │ │ climate_monthly│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │        hydropower_suitability (terrain + DEM)              ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Implementation

### 2.1 ML Module (`app/ml/`)

**Design decision:** The ARIMA model was trained **offline** in `DOE_arima_forecasting.ipynb`. The production system does **not retrain on every request**; instead, it loads pre-computed CSV artifacts.

| File | Purpose |
|------|---------|
| `app/ml/predictor.py` | Singleton `EnergyHubML` class that loads `master_preprocessed.csv`, `forecast_consumption_2025_2030.csv`, `forecast_peak_demand_2025_2030.csv`, and `model_comparison_results.csv` on startup. |

**Why no runtime training?**
- ARIMA on 22 observations trains in milliseconds, but `statsmodels` is not in the lightweight backend requirements.
- The thesis scope explicitly avoids heavy ML inference (Section 1.4.2).
- Pre-computed artifacts guarantee deterministic, reproducible outputs.

### 2.2 Service Layer (`app/services/energyhub.py`)

`EnergyHubService` bridges the ML predictor, Supabase geographic/climate data, and the REST API.

**Key method: `build_map_data()`**
- For national metrics (`energy_consumption`, `peak_demand`, `generation`, `forecasted_demand`): returns a single national point because the DOE dataset has **no sub-national consumption statistics**.
- For `renewable_potential`: queries Supabase (`regional_lookup`, `hydropower_suitability`, `municipality_climate_monthly`) and computes a composite score per province:
  - Solar potential (40%): derived from `allsky_sfc_sw_dwn`
  - Wind potential (30%): derived from `ws10m`
  - Hydropower potential (30%): derived from `hydro_suitability_score`

### 2.3 Router (`app/routes/energyhub.py`)

| Endpoint | Response Model | Description |
|----------|---------------|-------------|
| `GET /api/v1/energyhub/overview` | `OverviewResponse` | Latest DOE statistics + forecast summary + model comparison |
| `GET /api/v1/energyhub/forecast?metric=consumption` | `ForecastResponse` | 2025–2030 point forecast with 95% CI |
| `GET /api/v1/energyhub/trends` | `TrendsResponse` | Full historical series + forecast overlay + source/grid breakdown |
| `GET /api/v1/energyhub/map-data?metric=renewable_potential` | `MapDataResponse` | Geo-ready data points for choropleth |
| `GET /api/v1/energyhub/source-breakdown?year=2024` | `SourceBreakdownResponse` | Generation by plant type |
| `GET /api/v1/energyhub/grid-breakdown?year=2024` | `GridBreakdownResponse` | Generation by island grid |
| `GET /api/v1/energyhub/model-comparison` | `ModelComparisonResponse` | All 6 models’ test-set metrics |
| `GET /api/v1/energyhub/ai-insight` | `AiInsightResponse` | Data-backed narrative + recommendation |

### 2.4 Schemas (`app/schemas/energyhub.py`)

All Pydantic v2 models with strict typing. Used for both request validation and OpenAPI documentation.

---

## 3. Frontend Implementation

### 3.1 Component Structure

```
src/
├── pages/
│   └── EnergyHub.jsx              # Main dashboard page
├── components/energyhub/
│   ├── EnergyOverview.jsx         # 4 KPI cards (consumption, peak, RE share, growth)
│   ├── EnergyMap.jsx              # Choropleth map (leaflet + fallback grid)
│   ├── EnergyTrends.jsx           # SVG line/bar charts (historical vs forecast)
│   ├── EnergySources.jsx          # Donut chart + legend by plant type
│   └── AiInsightPanel.jsx         # Insight box + recommendation box
└── services/
    └── energyhub.js               # API client functions
```

### 3.2 Choropleth Map (`EnergyMap.jsx`)

**Two rendering modes:**

1. **Leaflet mode** (primary): uses `react-leaflet` + CARTO light basemap. Loads `philippine_geojson_file_per_region.json` from `/public` and colors each region based on the selected metric. Includes hover tooltips.
2. **Fallback mode**: if leaflet is not installed, renders a responsive color-coded grid of provinces/regions.

**Metric selector:**
- `renewable_potential` — province-level composite score
- `energy_consumption` — national total (single point)
- `peak_demand` — national total
- `generation` — national total
- `forecasted_demand` — 2030 ARIMA projection

### 3.3 Charts (`EnergyTrends.jsx`)

Uses lightweight inline SVG charts (no extra charting library) to avoid bundle bloat:
- **Line chart**: historical consumption + forecast overlay
- **Bar chart**: renewable generation by year
- **Line chart**: peak demand trend

---

## 4. Data Flow

### 4.1 Forecast Flow (Read-Only Artifacts)

```
DOE_Data_Extracted/forecast_consumption_2025_2030.csv
        ↓  (loaded at startup)
app/ml/predictor.py  →  EnergyHubML singleton
        ↓
app/services/energyhub.py  →  build_overview()
        ↓
app/routes/energyhub.py  →  GET /overview
        ↓
React  →  EnergyOverview cards
```

### 4.2 Map Flow (Supabase Query)

```
Supabase
  ├─ regional_lookup (region/province coordinates)
  ├─ hydropower_suitability (suitability scores)
  └─ municipality_climate_monthly (solar, wind)
        ↓
app/services/energyhub.py  →  _build_renewable_potential_map()
        ↓
app/routes/energyhub.py  →  GET /map-data?metric=renewable_potential
        ↓
React  →  EnergyMap (Leaflet or fallback grid)
```

---

## 5. Database Changes

**No new tables were created.**

The EnergyHub module consumes existing Supabase tables:

| Table | Usage |
|-------|-------|
| `regions` | Region names and centroid coordinates for map labels |
| `provinces` | Province names and coordinates for map fallback grid |
| `municipality_climate_monthly` | Solar irradiance (`allsky_sfc_sw_dwn`) and wind speed (`ws10m`) for renewable scoring |
| `hydropower_suitability` | `hydro_suitability_score` and `estimated_hydropower_potential_kw` |
| `regional_lookup` (view) | Joined region→province→municipality→barangay for coordinate lookups |

**Note:** The DOE energy data is stored as **static CSV files** in `DOE_Data_Extracted/` and loaded by the backend predictor. No database migration is required.

---

## 6. Installation & Setup

### 6.1 Backend

```bash
# .venv is at the project root, not inside fastapi-backend/
cd "d:\63947\Documents\GitHub\Lumi"
.\.venv\Scripts\python.exe -m pip install -r fastapi-backend/requirements.txt
```

The backend already includes the new dependencies (`pandas>=2.0.0`, `numpy>=1.24.0`) in `fastapi-backend/requirements.txt`.

### 6.2 Frontend

```bash
cd react-frontend
npm install
```

New dependencies added to `package.json`:
- `leaflet@^1.9.4`
- `react-leaflet@^4.2.1`

Leaflet CSS is loaded from CDN in `index.html`.

### 6.3 GeoJSON Asset

The region-level GeoJSON file has been copied to:
```
react-frontend/public/philippine_geojson_file_per_region.json
```

This ensures Vite serves it at runtime at `/philippine_geojson_file_per_region.json`.

---

## 7. Testing Instructions

### 7.1 Backend Tests

```bash
cd "d:\63947\Documents\GitHub\Lumi"
.\.venv\Scripts\python.exe -m uvicorn fastapi-backend.main:app --reload
```

Then visit in browser or use curl:

```bash
# Overview
curl http://localhost:8000/api/v1/energyhub/overview

# Forecast
curl "http://localhost:8000/api/v1/energyhub/forecast?metric=consumption"

# Trends
curl http://localhost:8000/api/v1/energyhub/trends

# Map data (renewable potential)
curl "http://localhost:8000/api/v1/energyhub/map-data?metric=renewable_potential"

# AI Insight
curl http://localhost:8000/api/v1/energyhub/ai-insight
```

### 7.2 Frontend Tests

```bash
cd react-frontend
npm run dev
```

Navigate to `http://localhost:5173/energyhub`.

Verify:
1. **Overview cards** load with 2024 statistics.
2. **Map** shows a colored grid (or leaflet map if packages installed).
3. **Trends** show historical line + forecast continuation.
4. **Sources** show a donut chart for 2024 plant-type generation.
5. **AI Insight** displays a data-backed narrative.

---

## 8. Production Considerations

### 8.1 Render Deployment

- The FastAPI backend is stateless; the `EnergyHubML` singleton loads CSVs once at startup.
- No heavy ML inference occurs at request time — all endpoints are O(1) reads.
- Supabase connection uses the existing `get_supabase_client()` utility with JWT and REST fallback.

### 8.2 Performance

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `GET /overview` | O(1) | Reads cached DataFrame rows |
| `GET /forecast` | O(1) | Reads cached forecast CSV |
| `GET /map-data` | O(n) | n = number of provinces (~80). Single Supabase query. |
| `GET /trends` | O(1) | All data in memory |

### 8.3 Known Limitations

1. **No sub-national energy consumption data:** The DOE publishes national-level statistics only. Regional/provincial consumption cannot be displayed on the map without disaggregation assumptions.
2. **Annual resolution only:** Monthly or daily granularity is not available in the DOE dataset.
3. **Single national ARIMA model:** The model does not produce per-region forecasts.
4. **Renewable potential is a proxy:** The map score is a composite of climate and terrain indicators, not measured renewable generation capacity.

---

## 9. Files Created / Modified

### New Backend Files
| File | Description |
|------|-------------|
| `fastapi-backend/app/ml/__init__.py` | Package marker |
| `fastapi-backend/app/ml/predictor.py` | ML artifact loader and prediction service |
| `fastapi-backend/app/schemas/energyhub.py` | Pydantic request/response models |
| `fastapi-backend/app/services/energyhub.py` | Business logic + Supabase bridge |
| `fastapi-backend/app/routes/energyhub.py` | FastAPI router with 8 endpoints |

### Modified Backend Files
| File | Change |
|------|--------|
| `fastapi-backend/app/routes/api.py` | Added `energyhub_router` |
| `fastapi-backend/requirements.txt` | Added `pandas>=2.0.0`, `numpy>=1.24.0` |

### New Frontend Files
| File | Description |
|------|-------------|
| `react-frontend/src/pages/EnergyHub.jsx` | Main dashboard page |
| `react-frontend/src/components/energyhub/EnergyOverview.jsx` | KPI cards |
| `react-frontend/src/components/energyhub/EnergyMap.jsx` | Choropleth map |
| `react-frontend/src/components/energyhub/EnergyTrends.jsx` | SVG trend charts |
| `react-frontend/src/components/energyhub/EnergySources.jsx` | Donut source chart |
| `react-frontend/src/components/energyhub/AiInsightPanel.jsx` | Insight panel |
| `react-frontend/src/services/energyhub.js` | API client |

### Modified Frontend Files
| File | Change |
|------|--------|
| `react-frontend/src/routes/AppRoutes.jsx` | Added `/energyhub` route |
| `react-frontend/src/components/layout/Navbar.jsx` | Added EnergyHub nav link |
| `react-frontend/src/services/apiClient.js` | Exported `request` helper |
| `react-frontend/package.json` | Added `leaflet`, `react-leaflet` |
| `react-frontend/index.html` | Added Leaflet CSS CDN + updated title |

### Asset Files
| File | Action |
|------|--------|
| `react-frontend/public/philippine_geojson_file_per_region.json` | Copied from `philippine_geojson/` |

---

## 10. Future Enhancements

- **Per-region forecasting:** If DOE or NGCP releases regional consumption time series, retrain ARIMA per grid (Luzon, Visayas, Mindanao).
- **Live DOE ingestion:** Automate PDF extraction pipeline to refresh data annually.
- **LLM insight generation:** Replace static AI insight with Gemini/Groq call for dynamic, RAG-backed analysis.
- **Municipal energy disaggregation:** Use population and economic activity proxies to downscale national forecasts.
