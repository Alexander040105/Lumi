# EcoSim Module — Architecture & Implementation Guide

## Overview

The **EcoSim** module is the household-level renewable energy simulation and recommendation engine of the LUMI Environmental Intelligence System. It evaluates solar, wind, and hydropower feasibility for any Philippine municipality based on NASA POWER climate data and local terrain metrics.

Features:

- Municipality-level climate lookup (NASA POWER)
- Solar output estimation using irradiance, temperature, humidity, and dust loss
- Wind output estimation using physics-based power coefficient and capacity factor
- Micro-hydropower estimation using rainfall, runoff, slope, and DEM-derived hydraulic head
- Economic comparison: installation cost, payback period, monthly savings, carbon reduction
- AI-powered analysis via Gemini (optional RAG)
- Scenario comparison: current bill vs renewable offset

**Target users:** Homeowners, students, community planners, barangay officials.
**Disclaimer:** Estimates are educational. Actual performance depends on site conditions, equipment quality, and grid availability.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     Ecosim.jsx (page)                      ││
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐   ││
│  │   │ SimInput │ │ KPI Cards│ │ Climate  │ │ AI Analysis│   ││
│  │   │  Form    │ │          │ │  Panel   │ │   Panel    │   ││
│  │   └──────────┘ └──────────┘ └──────────┘ └────────────┘   ││
│  │   ┌──────────────────────────────────────────────────────┐││
│  │   │          Renewable Comparison Bars                    │││
│  │   │   Solar ▓▓▓▓▓▓░░░  Wind ▓▓▓░░░░░  Hydro ▓▓▓▓░░░░      │││
│  │   └──────────────────────────────────────────────────────┘││
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐                  ││
│  │   │  Solar   │ │   Wind   │ │  Hydro   │                  ││
│  │   │  Card    │ │  Card    │ │  Card    │                  ││
│  │   └──────────┘ └──────────┘ └──────────┘                  ││
│  │   ┌──────────────────────────────────────────────────────┐││
│  │   │         Scenario Comparison Table                     │││
│  │   │   Current vs With Recommended Source                  │││
│  │   └──────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
│                    services/apiClient.js                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP (fetch)
┌──────────────────────────────▼──────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │   /api/v1/ecosim                                            ││
│  │   ├── GET /                  → Dashboard response           ││
│  │   ├── GET /municipalities   → Municipality list            ││
│  │   └── POST /                 → Save house configuration    ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ ecosim.py    │  │ ecosim.py    │  │ solar_output │          │
│  │   Router     │  │   Service    │  │   _calc.py   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │wind_output_  │  │hydro_output_ │  │   Gemini AI          │   │
│  │   calc.py    │  │   calc.py    │  │   (optional RAG)     │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │ SQL / REST
┌──────────────────────────────▼──────────────────────────────────┐
│                     SUPABASE POSTGRESQL                         │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │ municipalities│  │ municipality_     │  │hydropower_      │ │
│  │               │  │ climate_monthly  │  │ suitability     │ │
│  └──────────────┘  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Implementation

### 2.1 Physics Calculators (`app/services/`)

The EcoSim backend does **not use ML**. Instead, it uses deterministic physics-based formulas derived from peer-reviewed literature.

| File | Purpose |
|------|---------|
| `solar_output_calc.py` | Temperature factor, dust loss, humidity degradation, performance ratio, and solar irradiance-to-output conversion. Default: 2 × 550 W panels. |
| `wind_output_calc.py` | Loads a product database (`wind_products_joined_betz.csv`) to compute average rotor radius and power coefficient. Uses Betz-capped power equation with capacity factor. |
| `hydro_output_calc.py` | Rational-method runoff estimation + micro-hydropower output (`ρ × g × Q × H × η`). Uses terrain metrics (slope, runoff potential, gravity flow, hydraulic head). |

**Why physics-based instead of ML?**
- Municipal-level renewable potential is a deterministic function of climate and terrain variables.
- Physics models are interpretable and require no training data.
- The thesis scope (Section 1.4.2) avoids heavy ML inference for user-facing simulations.

### 2.2 Service Layer (`app/services/ecosim.py`)

`renewable_energy_calculator()` is the core orchestrator:

1. Fetches municipality climate averages from a local CSV (`municipality_climate_averages.csv`)
2. Fetches terrain metrics from Supabase (`hydropower_suitability`)
3. Runs consumption calculator: `monthly_kWh = bill / rate`
4. Computes solar output using irradiance, temperature, dust, and humidity factors
5. Computes hydro output using rainfall, slope, and DEM-derived head
6. Computes wind output using wind speed and air density
7. Optionally calls Gemini AI (standard or RAG) for natural language analysis

`build_ecosim_dashboard_response()` wraps the calculator with economic scoring:
- Weighted suitability score: `0.6 × energy_ratio + 0.4 × source_score`
- Payback period: `installation_cost / (monthly_savings × 12)`
- Carbon reduction: `usable_kWh × 0.6835 kg CO₂/kWh` (DOE grid EF)
- Installation costs: PHP 60k/kW solar, PHP 80k/kW wind, PHP 100k/kW hydro

### 2.3 Router (`app/routes/ecosim.py`)

| Endpoint | Response Model | Description |
|----------|---------------|-------------|
| `GET /api/v1/ecosim/` | `EcosimDashboardResponse` | Full simulation dashboard |
| `GET /api/v1/ecosim/municipalities` | `MunicipalityListResponse` | All 1,600+ Philippine municipalities |
| `POST /api/v1/ecosim/` | `EcosimResponse` | Save house configuration with AI analysis |

Query params for GET:
- `municipality_id` (int)
- `monthly_consumption` (kWh)
- `monthly_bill` (PHP)
- `include_ai` (bool) — enables Gemini analysis
- `use_rag` (bool) + `rag_query` (str) — enables RAG-backed AI

### 2.4 Schemas (`app/schemas/ecosim.py`)

All Pydantic v2 models with strict typing and validation constraints:

| Model | Fields |
|-------|--------|
| `EcosimDashboardResponse` | `recommended_source`, `suitability_score`, `estimated_generation_kwh`, `monthly_savings`, `installation_cost`, `payback_years`, `carbon_reduction`, `options`, `comparison`, `climate`, `renewable_energy_results`, `ai_analysis` |
| `RenewableEnergyResults` | `solar_output`, `hydro_output`, `wind_output`, `consumption_results`, `climate`, `assumptions` |
| `EcosimOption` | `source`, `suitability_score`, `estimated_generation_kwh`, `monthly_savings`, `installation_cost`, `payback_years`, `carbon_reduction`, `explanation` |

---

## 3. Frontend Implementation

### 3.1 Component Structure

```
src/
├── pages/
│   └── Ecosim.jsx                 # Main simulation page
└── services/
    └── apiClient.js               # getEcosim(), getMunicipalities()
```

### 3.2 Simulation Input Form

Four fields in a responsive grid:
1. **Monthly consumption (kWh)** — default 350
2. **Monthly bill (PHP)** — default 5,000
3. **Municipality** — searchable dropdown with 1,600+ municipalities (filtered client-side)
4. **Include AI analysis** — checkbox to enable Gemini

### 3.3 Results Dashboard

**Top recommendation card:**
- Recommended source (Solar / Wind / Hydropower)
- Suitability score (0–1)
- Estimated generation (kWh/month)
- Explanation text

**KPI cards (5 metrics):**
1. Estimated monthly generation (kWh)
2. Estimated savings (PHP)
3. Installation cost (PHP)
4. Payback period (years)
5. Carbon reduction (kg CO₂/month)

**Climate data panel (8 metrics):**
- Temperature, humidity, rainfall, solar irradiance
- Wind speed, cloud coverage, surface pressure, elevation

**Detailed renewable outputs (3 cards):**
- Solar: system size, daily/monthly output, solar score
- Wind: swept area, rated power, capacity factor, daily/monthly output
- Hydro: system size, daily/monthly output, hydro score

**AI Analysis panel (when enabled):**
- Summary, per-source analysis, recommendation, environmental impact

**Comparison section:**
- Horizontal bar chart: generation by source
- Scenario comparison table: current vs with recommended source

---

## 4. Data Flow

### 4.1 Simulation Flow

```
User input (consumption, bill, municipality)
        ↓
GET /api/v1/ecosim/?municipality_id=...&monthly_consumption=...&monthly_bill=...
        ↓
app/services/ecosim.py
  ├─ get_municipality_data() → local CSV climate averages
  ├─ get_municipality_terrain_data() → Supabase hydropower_suitability
  ├─ consumption_calculator()
  ├─ solar_output_calc.py
  ├─ hydro_output_calc.py
  ├─ wind_output_calc.py
  └─ _calculate_option_summary() × 3 (solar, wind, hydro)
        ↓
EcosimDashboardResponse
        ↓
React → Ecosim.jsx renders recommendation + KPIs + comparisons
```

### 4.2 AI Analysis Flow (Optional)

```
include_ai=true
        ↓
renewable_energy_calculator()
  ├─ Standard: analyze_renewable_results() → Gemini
  └─ RAG: analyze_with_rag() → Gemini + Supabase context
        ↓
ai_analysis: { summary, renewable_analysis, recommendation, cost_estimation, environmental_impact }
```

---

## 5. Database & Data Sources

### 5.1 Supabase Tables Used

| Table | Columns Used | Purpose |
|-------|-------------|---------|
| `municipalities` | `municipality_id`, `name` | Municipality lookup and listing |
| `hydropower_suitability` | `hydraulic_head_m`, `runoff_potential`, `watershed_gradient`, `mean_slope_deg`, `gravity_flow_potential`, `hydro_suitability_score` | Terrain metrics for micro-hydro |

### 5.2 Local CSV Assets

| File | Location | Purpose |
|------|----------|---------|
| `municipality_climate_averages.csv` | `app/services/local_data/` | Pre-aggregated NASA POWER climate data (solar irradiance, wind speed, temperature, humidity, rainfall, etc.) |
| `wind_products_joined_betz.csv` | `app/services/local_data/` | Wind turbine product database for computing average rotor radius and power coefficient |

### 5.3 Data Preprocessing

The `municipality_climate_averages.csv` was generated by aggregating `municipality_climate_monthly` (NASA POWER) across all available years per municipality. This avoids querying Supabase for every simulation request.

---

## 6. Installation & Setup

### 6.1 Backend

```bash
# .venv is at the project root
cd "d:\63947\Documents\GitHub\Lumi"
.\.venv\Scripts\python.exe -m pip install -r fastapi-backend/requirements.txt
```

Required packages already in `requirements.txt`:
- `pandas>=2.0.0`
- `numpy>=1.24.0`

### 6.2 Frontend

```bash
cd react-frontend
npm install
```

No additional frontend dependencies are required beyond the existing UI library (`shadcn/ui`).

### 6.3 Local Data Assets

Ensure these files exist in `fastapi-backend/app/services/local_data/`:
- `municipality_climate_averages.csv`
- `wind_products_joined_betz.csv`

---

## 7. Testing Instructions

### 7.1 Backend Tests

```bash
cd "d:\63947\Documents\GitHub\Lumi"
.\.venv\Scripts\python.exe -m uvicorn fastapi-backend.main:app --reload
```

Then test with curl:

```bash
# Municipality list
curl http://localhost:8000/api/v1/ecosim/municipalities

# Simulation for Quezon City (municipality_id varies; check list first)
curl "http://localhost:8000/api/v1/ecosim/?municipality_id=123&monthly_consumption=350&monthly_bill=5000"

# With AI analysis
curl "http://localhost:8000/api/v1/ecosim/?municipality_id=123&monthly_consumption=350&monthly_bill=5000&include_ai=true"

# With RAG
curl "http://localhost:8000/api/v1/ecosim/?municipality_id=123&monthly_consumption=350&monthly_bill=5000&include_ai=true&use_rag=true&rag_query=suitable+for+solar"
```

### 7.2 Frontend Tests

```bash
cd react-frontend
npm run dev
```

Navigate to `http://localhost:5173/ecosim`.

Verify:
1. Municipality dropdown loads and filters correctly.
2. Submitting the form shows loading state then results.
3. **Recommendation card** displays the top-scoring renewable source.
4. **KPI cards** show generation, savings, cost, payback, and carbon reduction.
5. **Climate panel** shows temperature, rainfall, irradiance, wind speed, etc.
6. **Solar / Wind / Hydro cards** show detailed technical outputs.
7. **Comparison bars** visualize generation across all three sources.
8. **Scenario table** compares current vs renewable-offset usage.
9. With "Include AI analysis" checked, the **AI Analysis** panel appears after the simulation.

---

## 8. Production Considerations

### 8.1 Performance

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `GET /ecosim/` | O(1) | CSV lookup + deterministic calculations, < 100ms |
| `GET /ecosim/municipalities` | O(n log n) | n ≈ 1,600; sorted alphabetically |
| AI analysis | ~1–3s | Gemini API call; optional and non-blocking |

### 8.2 Known Limitations

1. **Fixed panel assumptions:** Solar uses a hardcoded 2 × 550 W configuration. Users cannot yet customize panel count or wattage.
2. **Single-turbine wind model:** Wind output assumes one representative small turbine based on product averages.
3. **Micro-hydro catchment:** Assumes a 0.5 km² catchment area and 40 % environmental flow reserve.
4. **No grid-interconnection cost:** Installation costs are equipment-only; grid-tie, permits, and labor are not included.
5. **Climate data is averaged:** Uses long-term averages, not real-time or seasonal data.
6. **Municipality-level only:** Does not account for hyperlocal microclimates (e.g., rooftop orientation, shading).

---

## 9. Files Created / Modified

### New Backend Files
| File | Description |
|------|-------------|
| `fastapi-backend/app/services/ecosim.py` | Core simulation orchestrator + dashboard builder |
| `fastapi-backend/app/services/solar_output_calc.py` | Solar irradiance → energy output with loss factors |
| `fastapi-backend/app/services/wind_output_calc.py` | Wind turbine physics + Betz limit + capacity factor |
| `fastapi-backend/app/services/hydro_output_calc.py` | Runoff estimation + micro-hydropower output |
| `fastapi-backend/app/schemas/ecosim.py` | Pydantic request/response models |
| `fastapi-backend/app/routes/ecosim.py` | FastAPI router with 3 endpoints |

### Modified Backend Files
| File | Change |
|------|--------|
| `fastapi-backend/app/routes/api.py` | Added `ecosim_router` |

### New Frontend Files
| File | Description |
|------|-------------|
| `react-frontend/src/pages/Ecosim.jsx` | Main simulation page with input form, KPIs, comparison charts, and AI panel |

### Modified Frontend Files
| File | Change |
|------|--------|
| `react-frontend/src/routes/AppRoutes.jsx` | Added `/ecosim` route |
| `react-frontend/src/components/layout/Navbar.jsx` | Added Ecosim nav link |
| `react-frontend/src/services/apiClient.js` | Added `getEcosim()` and `getMunicipalities()` |

### Data Assets
| File | Location | Purpose |
|------|----------|---------|
| `municipality_climate_averages.csv` | `fastapi-backend/app/services/local_data/` | Pre-aggregated NASA POWER climate data |
| `wind_products_joined_betz.csv` | `fastapi-backend/app/services/local_data/` | Wind turbine product averages |

---

## 10. Future Enhancements

- **Customizable solar config:** Allow users to input panel wattage, quantity, roof area, and azimuth/tilt.
- **Seasonal simulation:** Use monthly climate data instead of annual averages to show wet vs dry season performance.
- **Battery storage modeling:** Add PV + battery sizing for off-grid scenarios.
- **LCOE calculation:** Extend payback period to full Levelized Cost of Energy with maintenance, degradation, and financing.
- **Map integration:** Show results on a mini-map with the municipality highlighted (reuse EnergyHub GeoJSON).
- **Household profile save:** Persist multiple house configurations per user account.

---

*Last updated: June 2026*
