# LUMI MCDA Breakdown: Multi-Criteria Decision Analysis (Simplified)

**Project:** LUMI (Lightweight Utility for Municipal Intelligence)  
**Version:** 1.0-Simple  
**Date:** June 2026

---

## 1. What is MCDA in LUMI?

LUMI uses **Weighted Linear Combination (WLC)** — a type of MCDA — to rank 4 renewable energy sources (solar, wind, hydro, geothermal) for any Philippine municipality.

The system scores each source by combining:
1. **How much energy it can produce** (physics-based)
2. **How well the location fits** (suitability score)
3. **Economic return** (payback period, cost, savings)
4. **Environmental impact** (CO₂ reduction)

---

## 2. Core MCDA Formula

```
suitability_score = 0.6 × energy_ratio + 0.4 × source_score
```

| Component | Meaning |
|---|---|
| `energy_ratio` | Generation ÷ Consumption (capped at 1.0) |
| `source_score` | Location suitability (0–1) |

This is the **Weighted Linear Combination (WLC)** method cited from **Asadi et al. (2023)**.

*Source:* `ecosim.py:658-661`

---

## 3. The 4 Energy Formulas

### 3.1 Solar
**File:** `solar_output_calc.py`

```
Output = kWp × Irradiance × Performance_Ratio
```

| Factor | Value | Why |
|---|---|---|
| System Efficiency | 80% | Panel + inverter losses |
| Temp Factor | ~0.4% loss per °C > 25°C | Silicon physics |
| Dust Loss | Wind-speed adjusted | Philippine dust |
| Inverter | 96% | AC conversion |

**Suitability Score:**
```python
solar_score = min((irradiance / 6.0) * 100, 100)
```

---

### 3.2 Wind
**File:** `wind_output_calc.py`

```
Power = 0.5 × ρ × A × V³ × Cp × η × Capacity_Factor
```

| Variable | Meaning | Typical Value |
|---|---|---|
| ρ | Air density | 1.225 kg/m³ |
| A | Swept area (πr²) | From rotor radius |
| V | Wind speed | m/s (cubed!) |
| Cp | Power coefficient | ≤ 0.593 (Betz limit) |
| η | Efficiency | 90% |
| CF | Capacity factor | 30% |

**Suitability Score:**
```python
wind_score = min(capacity_factor * 1.5, 1.0)
```

*Cites:* Fahim et al. (2024) for wind power equation

---

### 3.3 Hydropower
**File:** `hydro_output_calc.py`

```
Power (kW) = η_turbine × η_generator × ρ × g × Q × H / 1000
```

| Variable | Meaning |
|---|---|
| Q | Flow rate (m³/s) — from rainfall + slope + catchment |
| H | Head (m) — elevation drop |
| η | Turbine (75%) × Generator (90%) = 67.5% |

**Flow Estimation (Rational Method):**
```
Q = (C × P × A) / seconds_month × 0.40
```
- C = Runoff coefficient (0.30–0.75 based on slope)
- 0.40 = 40% environmental flow reserve

**Suitability Score:**
```python
hydro_score = normalize(monthly_kwh, 0, 1000) * 100
```

*Cites:* Fahim et al. (2024); Butchers et al. (2021); Wang et al. (2025)

---

### 3.4 Geothermal (Full AHP)
**File:** `geothermal/features.py`

Unlike the others, geothermal uses **5 weighted AHP criteria:**

| Criterion | Weight | Input |
|---|---|---|
| Heat Flow | 0.30 | Surface heat flow |
| Fault Proximity | 0.15 | `exp(-distance / 20)` |
| Volcano Proximity | 0.10 | `exp(-distance / 30)` |
| Aquifer | 0.15 | Permeability score |
| Temperature | 0.10 | Surface temp (20–35°C) |

```python
total_weight = sum(weight × availability)
score = sum(sub_score × weight × availability) / total_weight
```

- Missing data handled gracefully (availability = 0)
- Proximity boost for municipalities near existing plants

---

## 4. MCDA Ranking Engine

**File:** `ecosim.py` — `_calculate_option_summary()`

For each source, the system calculates:

| Metric | Formula | Thesis Support |
|---|---|---|
| **Suitability** | `0.6 × energy_ratio + 0.4 × source_score` | Asadi et al. (2023); Beriro et al. (2022) |
| **Payback** | `cost / (savings × 12)` | Ngwakwe (2025) |
| **CO₂ Saved** | `kWh × 0.6835` | DOE Philippines (2022) |
| **System Size** | Source-specific kW | Taduran & Piao (2025) |

**Capacity Factors by Source:**

| Source | CF | Scale |
|---|---|---|
| Solar | 4.5 peak sun hrs/day | Residential |
| Wind | 25% | Residential |
| Hydro | 50% | Residential |
| Geothermal | 100% (utility) | Utility (excluded from household rec) |

**Final Pick:**
```python
household_options = [o for o in options if o["scale"] != "utility"]
recommended = max(household_options, key=lambda x: (x["suitability_score"], x["generation"]))
```

---

## 5. Thesis RRL Studies Supporting MCDA

### 5.1 Weighted Sum Model (WSM) — Core Method
> "...utilized an MCDA method specifically, the weighted sum model (WSM) to assess, score and rank the strengths and weaknesses of renewable energy options..." *(Thesis p. 27)*

**Connection:** LUMI uses the same WSM approach for transparent, fast scoring.

---

### 5.2 GIS-MCDA for Site Suitability
> "...a Geographic Information Systems (GIS) and Multi-Criteria Decision Analysis (MCDA) framework used in energy-planning literature to evaluate site suitability for solar, wind, hydro, and geothermal development (Asadi et al., 2023)." *(Thesis p. 33)*

**Connection:** LUMI screens municipalities using NASA POWER data across the same four dimensions (meteorological, topographical, infrastructural, environmental).

---

### 5.3 AHP for Multi-Criteria Scoring
> "Hybrid Fuzzy AHP + TOPSIS as the MCDM approach... preferred by field experts." *(Thesis p. 71)*

**Connection:** LUMI's geothermal module uses a simplified AHP with 5 weighted criteria — the same structure, without fuzzy logic for transparency.

---

### 5.4 Intelligent Decision Support Systems
> "Decision support systems that integrated machine learning and AI... enhanced the capabilities... with accuracy and reliability of energy performance predictions." *(Thesis p. 28)*

**Connection:** LUMI is an IDSS combining rule-based physics, ML forecasting, and AI explanations.

---

### 5.5 Explainable AI (XAI)
> "...explainable artificial intelligence (XAI)... ensures that it is tailored to the needs of the user..." *(Thesis p. 27)*

**Connection:** LUMI generates plain-language explanations for every recommendation (e.g. "Solar panels convert photons... This location receives X kWh/m²/day...").

---

## 6. Dynamic Weights

**File:** `mcda_weights_service.py`

| Energy Type | Key Weights |
|---|---|
| **Solar** | Irradiance 0.40, Temperature 0.20, Cloud 0.20, Slope 0.10, Land 0.10 |
| **Wind** | Wind Speed 0.40, Roughness 0.20, Elevation 0.20, Land 0.10, Density 0.10 |
| **Hydro** | Rainfall 0.30, Slope 0.25, Catchment 0.25, Head 0.20 |
| **Geothermal** | Heat Flow 0.30, Fault 0.15, Volcano 0.10, Aquifer 0.15, Temperature 0.10 |

- Stored in Supabase (`mcda_weights` table)
- Cached in memory; invalidated on admin update
- Falls back to defaults if DB is unavailable

---

## 7. MCDA Pipeline at a Glance

```
User Input (Municipality + Bill)
        │
        ▼
   NASA POWER API
        │
        ▼
┌──────────────────┐
│ 1. Solar:  kWp × Irradiance × PR        │
│ 2. Wind:   0.5ρAV³Cpη × CF              │
│ 3. Hydro:  ρgQH × η_turbine × η_gen    │
│ 4. Geo:    AHP(heat, fault, aquifer...)  │
└──────────────────┘
        │
        ▼
   Suitability Scores (0–1)
        │
        ▼
   MCDA: score = 0.6 × ratio + 0.4 × score
        │
        ▼
   Economics: Payback, Cost, CO₂
        │
        ▼
   Rank → Recommend Highest
        │
        ▼
   XAI Explanation Generated
```

---

## 8. Key References

| Study | What It Supports | Where in Thesis |
|---|---|---|
| **Asadi et al. (2023)** | GIS-AHP + WLC for renewable site selection | p. 33; cited in code |
| **Beriro et al. (2022)** | WSM for scoring/ranking renewables | p. 27 |
| **Butschek et al. (2023)** | GIS-MCDA criteria framework | p. 33 |
| **Ngwakwe (2025)** | Payback period as screening metric | p. —; cited in code |
| **DOE Philippines (2022)** | CO₂ emission factor (0.6835 kg/kWh) | p. —; cited in code |
| **Taduran & Piao (2025)** | Solar yield in Tarlac (3.01 kWh/kWp/day) | p. —; cited in code |
| **Fahim et al. (2024)** | Wind power physics (P = 0.5ρAV³Cpη) | p. —; cited in code |

---

*Document generated: June 2026*
