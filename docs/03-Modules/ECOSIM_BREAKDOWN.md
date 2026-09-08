# LUMI Ecosim Recommendation System — Technical Breakdown

> **Purpose**: Provide Filipino households with a data-driven renewable-energy recommendation based on municipal climate data, terrain features, and user consumption patterns.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ECOSIM PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Inputs                                                                     │
│    ├── municipality_id  (Supabase municipalities table)                     │
│    ├── monthly_consumption_kwh                                              │
│    ├── monthly_bill_php                                                   │
│    └── desired_savings (default 0.50)                                     │
│                                                                             │
│  Data Sources                                                               │
│    ├── NASA POWER climate averages (local CSV)                              │
│    ├── Supabase: municipalities, hydropower_suitability                   │
│    │            geothermal_output, geothermal_suitability                   │
│    ├── Local GIS: faults, volcanoes, heat flow, aquifers                  │
│    └── Global Energy Monitor: PH geothermal plants                        │
│                                                                             │
│  Core Engine  ──►  4 Renewable Calculators  ──►  Scoring & Economics        │
│     │                                              │                        │
│     └─►  Optional AI Layer (Gemini / Groq / RAG)  ─┘                        │
│                                                                             │
│  Output: EcosimDashboardResponse                                            │
│    ├── Recommended source (solar / wind / hydro)                          │
│    ├── Suitability score, payback, carbon reduction                         │
│    ├── Side-by-side comparison of all 4 options                             │
│    ├── Climate snapshot                                                     │
│    └── AI-generated narrative (optional)                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Entry Points

| Function | File | Role |
|----------|------|------|
| `build_ecosim_dashboard_response()` | `ecosim.py:748` | Main orchestrator; returns the dashboard JSON. |
| `renewable_energy_calculator()` | `ecosim.py:297` | Lower-level calculator; produces raw generation + climate data. |

---

## 3. Data Layer

### 3.1 Climate Baseline (NASA POWER)
Stored in `fastapi-backend/app/services/local_data/municipality_climate_averages.csv`.

| Variable | NASA POWER Column | Used By |
|----------|------------------|---------|
| Solar irradiance | `avg_allsky_sfc_sw_dwn` | Solar calc |
| Wind speed | `avg_ws10m` | Wind calc |
| Rainfall | `avg_prectotcorr` | Hydro calc |
| Temperature | `avg_t2m` | Solar efficiency, geothermal surface proxy |
| Humidity | `avg_rh2m` | Solar degradation, climate scoring |
| Cloud cover | `avg_cloud_amt` | Solar penalties |
| Surface pressure | `avg_surface_pressure` | Wind (optional) |
| Air density | `avg_rhoa` | Wind power |
| Elevation | `avg_elevation` | Hydro head |

### 3.2 Supabase Tables
- `municipalities` — id, name, lat, lon
- `hydropower_suitability` — hydraulic_head_m, runoff_potential, gravity_flow_potential, watershed_gradient, mean_slope_deg, terrain_ruggedness, hydro_suitability_score
- `geothermal_output` — pre-computed reservoir temp, thermal/electric power, annual GWh
- `geothermal_suitability` — geothermal_score, classification

### 3.3 Local GIS Datasets (Geothermal)
- `geothermal_faults.json` — fault lat/lon/length
- `geothermal_volcanoes.json` — volcano locations
- `geothermal_heatflow.csv` — IHFC heat-flow point measurements
- `aquifers_ph.geojson` — spatial aquifer polygons (preferred) or legacy CSV fallback
- `ph_geothermal_plants.json` — Global Energy Monitor Philippines tracker

---

## 4. Consumption Baseline

```python
monthly_consumption_kwh = monthly_bill / electricity_rate
daily_consumption_kwh   = monthly_consumption_kwh / days_in_month
target_consumption_kwh  = monthly_consumption_kwh * (1 - desired_savings)
```

- `electricity_rate` is derived from `monthly_bill / monthly_consumption` in the dashboard builder.
- Default `desired_savings = 0.50` (50%).

---

## 5. Renewable Energy Calculators

### 5.1 Solar
**File**: `solar_output_calc.py`

**Default hardware** (hard-coded residential baseline):
```python
panel_wattage      = 400 W
number_of_panels   = 2
system_efficiency  = 0.80
temp_coeff         = -0.004 / °C
inverter_eff       = 0.96
mismatch_loss      = 0.98
wiring_loss        = 0.98
base_dust_loss     = 0.97
base_degradation   = 0.99
```

**Physics chain**:
1. **Temperature factor**  
   `factor = 1 + temp_coeff × (avg_temp − 25)`  
   Silicon loses ~0.4 %/°C above 25 °C.

2. **Dust loss** (wind-adjusted)  
   `dust = base_dust_loss / (1 + 0.02 × (wind_speed − 3))`  
   Higher wind = more dust accumulation.

3. **Degradation from humidity**  
   If RH > 70 %, extra 0.5 % degradation penalty.

4. **Performance Ratio (PR)**  
   `PR = system_efficiency × temp_factor × dust × inverter × mismatch × wiring × degradation`

5. **Energy output**  
   `daily_kWh   = system_kWp × irradiance × PR`  
   `monthly_kWh = daily_kWh × days_in_month`  
   `solar_score = min((irradiance / 6.0) × 100, 100)`

---

### 5.2 Wind
**File**: `wind_output_calc.py`

**Hardware averaged from product database** (`wind_products_joined_betz.csv`):
- Average rotor radius — computed from parsed blade diameters
- Average power coefficient `Cp` — computed from rated power & diameter at 12 m/s

**Physics**:
```
P = 0.5 × ρ × A × V³ × Cp × η
```
- `ρ` = air density (kg/m³) — validated 0.9–1.3 range
- `A` = π × r²
- `Cp` capped at **Betz limit 0.593**
- `η` = mechanical/electrical efficiency (default 0.90)

**Realism adjustment**:
- **Capacity factor** = 0.30 (30 %) — accounts for variable winds, cut-in/cut-out speeds, maintenance.  
  Source: Baker et al., 2023.
- `effective_hours_per_day = 24 × 0.30 = 7.2 h`
- `monthly_kWh = rated_power_kW × 7.2 × days_in_month`

---

### 5.3 Hydropower
**File**: `hydro_output_calc.py`

**Two-stage model**:

#### A) Flow-rate estimation (`estimated_flow_rate`)
Rational-method inspired for ungauged small catchments:
```
Q_design = (C × P × A) / seconds_month × design_factor
```
- `C` = runoff coefficient from slope (0.30–0.75) — Javadinejad et al., 2022
- `P` = monthly precipitation (m)
- `A` = catchment area (default 0.5 km²)
- `design_factor` = 0.40 × gravity_flow_potential (40 % environmental reserve)
- Bounds clamped to `0.001 – 0.5 m³/s` (Butchers et al., 2021)

#### B) Power conversion (`calculate_hydropower`)
```
P_elec = η_turbine × η_generator × ρ × g × Q × H
```
- `η_turbine` = 0.75, `η_generator` = 0.90
- `H` (head) = municipal hydraulic_head × 0.12, clamped 2–25 m  
  (Only ~12 % of municipal elevation drop is household-accessible.)
- `hydro_score = normalize(monthly_energy, 0, 1000) × 100`

---

### 5.4 Geothermal
**Files**: `geothermal/features.py`, `geothermal/plants.py`

This is the most complex module. It treats geothermal as **utility-scale** rather than residential.

#### Suitability scoring (`compute_geothermal_suitability`)
Five sub-scores (AHP-weighted MCDA):

| Factor | Weight (default) | Data source |
|--------|------------------|-------------|
| Heat flow | 0.30 | IHFC point data → IDW interpolation (300 km radius, p=2) |
| Fault proximity | 0.15 | Nearest fault distance → `exp(−dist/20)` |
| Volcano proximity | 0.10 | Nearest volcano distance → `exp(−dist/30)` |
| Aquifer | 0.15 | Spatial point-in-polygon or legacy CSV median |
| Temperature | 0.10 | NASA POWER surface temp normalized 20–35 °C |

Weights are dynamically loaded from `mcda_weights_service`; fall back to defaults if DB is unreachable.

**Availability-aware weighting**: if a dataset is missing, its weight is redistributed among available factors.

**Classification thresholds**:
- High: ≥ 0.80
- Good: ≥ 0.60
- Moderate: ≥ 0.40
- Low: < 0.40

#### Output estimation (`compute_geothermal_output`)
```
reservoir_temp = surface_temp + (gradient × depth_km)
thermal_power  = flow_rate × Cp × ΔT / 1000      [MW]
electric_power = thermal_power × efficiency        [MW]
annual_energy  = electric_power × 8760 / 1000      [GWh]
```
- Default depth = 2 000 m
- Reinjection temp = 70 °C
- Binary efficiency = 12 %, Flash = 15 %

#### Proximity boost (`plants.py`)
Municipalities within 25 km of an operating geothermal plant get a linearly tapered bonus:
```
bonus = 30 × (1 − distance / 25)
```
This reflects the real-world presence of proven geothermal resources.

---

## 6. Economic & Environmental Scoring

### 6.1 Cost Constants (PHP per kW installed)

| Source | Cost/kW | Basis |
|--------|---------|-------|
| Solar | ₱60 000 | Philippines residential market estimate |
| Wind | ₱80 000 | Small-turbine installed cost estimate |
| Hydro | ₱100 000 | Micro-hydro civil-works + turbine |
| Geothermal | ₱100 000 | BOI Green Lane project average (Daklan, Mt. Labo, Mt. Malinao) |

### 6.2 Per-Option Summary (`_calculate_option_summary`)

For each renewable type the engine computes:

| Metric | Formula | Notes |
|--------|---------|-------|
| System size (kW) | Source-specific sizing (see below) | Proxy for cost calculation |
| Installation cost | `system_kw × cost_per_kw` | Geothermal uses utility-scale logic |
| Monthly savings | `min(generation, consumption) × electricity_rate` | Capped at 100 % offset |
| Payback (years) | `installation_cost / (monthly_savings × 12)` | `None` for utility-scale geothermal |
| Carbon reduction | `usable_kWh × 0.6835 kg CO₂/kWh` | Philippines DOE 2019–2021 OMEF |
| Suitability score | `0.6 × energy_ratio + 0.4 × source_score` | Weighted linear combination (Asadi et al., 2023) |

**System-sizing proxies**:
- Solar: `generation_kWh / (30 × 4.5)` — 4.5 peak-sun hrs/day (conservative PH estimate)
- Wind: `generation_kWh / (30 × 24 × 0.25)` — 25 % capacity factor
- Hydro: `generation_kWh / (30 × 24 × 0.50)` — 50 % capacity factor
- Geothermal: `generation_kWh / (30 × 24)` — utility base-load

### 6.3 Recommendation Logic

1. **Exclude utility-scale** (`scale == "utility"`) from household recommendation.
2. Pick the household option with the **highest suitability score**, tie-broken by estimated generation.
3. Compute net consumption and net bill after installing the recommended system.

---

## 7. AI Analysis Layer (Optional)

### 7.1 Standard AI (`gemini_funcs.py`)
- **Primary**: Google Gemini (`gemini-2.5-flash`)
- **Fallback**: `gemini-2.0-flash` (auto-retries with exponential backoff on 503/429)
- **Prompt structure**:
  - `## Observation` — climate summary
  - `## Interpretation` — 2-3 sentences per renewable type
  - `## Recommendation` — best option + actionable bullets (system size, cost range, first step)
  - `## Reason` — compare top 2-3 options using actual numbers
- **Unified LLM client** (`llm_client.py`) routes to Groq if Gemini is exhausted.

### 7.2 RAG AI (`rag_gemini_funcs.py`)
When `use_rag=True` + `rag_query` is provided, the system:
1. Retrieves relevant documents from the RAG knowledge base.
2. Injects them into the prompt as extra context.
3. Generates a more citation-rich answer.

### 7.3 Static Fallback Explanations
If the LLM fails or is disabled, `_build_static_renewable_explanations()` produces deterministic, physics-based text for every renewable type:
- **Solar**: irradiance → photons → electrons; cloud scatter; temp penalty
- **Wind**: V³ physics; capacity factor rationale
- **Hydro**: rainfall → flow; elevation → head → potential energy
- **Geothermal**: four subsurface drivers (heat flow, faults, aquifer permeability, gradient)

These are merged into any partial AI response so no card is ever empty.

---

## 8. Response Schema

### `EcosimDashboardResponse`
```json
{
  "municipality": "TAGUIG",
  "municipality_id": 1234,
  "monthly_consumption_kwh": 350.0,
  "monthly_bill": 5022.50,
  "recommended_source": "Solar",
  "suitability_score": 0.823,
  "estimated_generation_kwh": 310.5,
  "monthly_savings": 4452.67,
  "installation_cost": 165000.0,
  "payback_years": 3.1,
  "carbon_reduction": 212.1,
  "explanation": "Solar scores highest...",
  "options": [ /* Solar, Wind, Hydropower, Geothermal */ ],
  "comparison": {
    "current_monthly_consumption_kwh": 350.0,
    "current_monthly_bill": 5022.50,
    "renewable_monthly_consumption_kwh": 39.5,
    "renewable_monthly_bill": 566.83
  },
  "climate": { /* NASA POWER snapshot */ },
  "renewable_energy_results": { /* full generation objects */ },
  "ai_analysis": { /* LLM narrative + prescriptive recommendation */ },
  "nearby_geothermal_plants": [ /* if any within 25 km */ ]
}
```

---

## 9. Key Assumptions & Limitations

1. **Solar** uses a fixed 2-panel 400 W config. Not yet customizable per user.
2. **Wind** uses averaged product specs; no site-specific turbine selection.
3. **Hydro** assumes a 0.5 km² catchment and 12 % of municipal head — household-scale proxies.
4. **Geothermal** is utility-scale; households cannot install their own geothermal plant. It is included for completeness and regional energy-awareness.
5. Climate data is **monthly averaged**; no seasonal breakdown.
6. All economic figures are **first-order estimates**; actual quotes vary by installer.

---

## 10. File Map

```
fastapi-backend/app/
├── schemas/ecosim.py               # Pydantic request/response models
├── services/
│   ├── ecosim.py                   # Main orchestrator & dashboard builder
│   ├── solar_output_calc.py        # Solar physics & PR chain
│   ├── wind_output_calc.py         # Wind power & capacity factor
│   ├── hydro_output_calc.py        # Runoff & micro-hydro power
│   ├── geothermal/
│   │   ├── features.py             # Suitability, heat flow IDW, output
│   │   └── plants.py               # Proximity boost to operating plants
│   ├── gemini_funcs.py             # Gemini prompt builder & fallback chain
│   ├── rag_gemini_funcs.py         # RAG-enabled AI analysis
│   ├── llm_client.py               # Unified LLM router (Gemini → Groq)
│   ├── llm_sanitizer.py            # Output cleaning & extraction
│   ├── mcda_weights_service.py     # Dynamic AHP weight loader
│   └── local_data/
│       ├── municipality_climate_averages.csv
│       ├── wind_products_joined_betz.csv
│       ├── geothermal_faults.json
│       ├── geothermal_volcanoes.json
│       ├── geothermal_heatflow.csv
│       ├── aquifers_ph.geojson
│       └── ph_geothermal_plants.json
```

---

## 11. Academic & Official References

| Citation | Used In |
|----------|---------|
| Asadi et al. (2023) — GIS-AHP site selection | Weighted suitability scoring |
| Baker et al. (2023) — small wind capacity factor | Wind capacity factor = 0.30 |
| Butchers et al. (2021) — micro-hydro flow bounds | Hydro flow clamp 0.001–0.5 m³/s |
| DOE Philippines (2022) — National Grid Emission Factor | CO₂ factor 0.6835 kg/kWh |
| Fahim et al. (2024) — physics-based Cp model | Wind power equation |
| Feyissa et al. (2024); Wang et al. (2025) — micro-hydro | Hydro power & design flow |
| Huda et al. (2024) — Indonesian residential PV | Payback methodology |
| Javadinejad et al. (2022) — runoff coefficient from slope | Hydro runoff estimation |
| Ngwakwe (2025) — payback period review | Simple Payback Period (SPP) |
| Taduran & Piao (2025) — Tarlac PV performance | 4.0 kWh/m²/day conservative irradiance |

---

*Document generated from source: `fastapi-backend/app/services/ecosim.py` and supporting modules.*
