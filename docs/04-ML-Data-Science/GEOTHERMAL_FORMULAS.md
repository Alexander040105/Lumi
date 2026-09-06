# LUMI Geothermal Formulas: Complete Technical Reference

**Project:** LUMI (Lightweight Utility for Municipal Intelligence)  
**Module:** Geothermal Suitability & Output Engine  
**Date:** June 2026

---

## Table of Contents

1. [Distance & Spatial Formulas](#1-distance--spatial-formulas)
2. [Heat Flow Interpolation](#2-heat-flow-interpolation)
3. [Geothermal Gradient & Reservoir Temperature](#3-geothermal-gradient--reservoir-temperature)
4. [Aquifer Scoring](#4-aquifer-scoring)
5. [AHP-Based MCDA Suitability Score](#5-ahp-based-mcda-suitability-score)
6. [Geothermal Energy Output](#6-geothermal-energy-output)
7. [Proximity Boost](#7-proximity-boost)
8. [Confidence Scoring](#8-confidence-scoring)
9. [Integration in EcoSim Dashboard](#9-integration-in-ecosim-dashboard)
10. [Summary Cheat Sheet](#10-summary-cheat-sheet)

---

## 1. Distance & Spatial Formulas

### 1.1 Haversine Distance

**What it is:**
Calculates the great-circle distance between two lat/lon points on Earth. Used to find the nearest fault and volcano to any municipality.

**Formula:**
```
a = sin²(Δφ/2) + cos(φ₁) × cos(φ₂) × sin²(Δλ/2)
c = 2 × atan2(√a, √(1−a))
distance = R × c
```
Where:
- **R** = 6,371 km (Earth radius)
- **φ** = latitude in radians
- **λ** = longitude in radians

**Why this is used:**
Geothermal potential is strongly correlated with proximity to faults and volcanoes. The haversine formula is the standard spherical-Earth distance calculation used in all GIS applications.

**Why it matters:**
Without accurate distance calculation, a municipality 5 km from an active fault could be scored the same as one 200 km away. The exponential decay functions (later) depend on precise distances.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:42-53
def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
```

---

### 1.2 Fault Distance

**What it is:**
Finds the distance from a municipality to the nearest mapped active fault.

**Formula:**
```
fault_distance = min(haversine(muni_lat, muni_lon, fault_lat, fault_lon)) for all faults
```

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:145-171
def calculate_fault_distance(muni_lat: float, muni_lon: float, faults: list[dict] | None = None) -> float | None:
    if faults is None:
        if not _FAULTS_JSON.exists():
            return None
        with open(_FAULTS_JSON, "r", encoding="utf-8") as f:
            faults = json.load(f)
    if not faults:
        return None

    min_dist = float("inf")
    for fault in faults:
        dist = _haversine(muni_lat, muni_lon, fault["lat"], fault["lon"])
        if dist < min_dist:
            min_dist = dist
    return round(min_dist, 2)
```

---

### 1.3 Volcano Distance

**What it is:**
Finds the distance from a municipality to the nearest volcano.

**Formula:**
```
volcano_distance = min(haversine(muni_lat, muni_lon, vol_lat, vol_lon)) for all volcanoes
```

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:184-210
def calculate_volcano_distance(muni_lat: float, muni_lon: float, volcanoes: list[dict] | None = None) -> float | None:
    if volcanoes is None:
        if not _VOLCANOES_JSON.exists():
            return None
        with open(_VOLCANOES_JSON, "r", encoding="utf-8") as f:
            volcanoes = json.load(f)
    if not volcanoes:
        return None

    min_dist = float("inf")
    for vol in volcanoes:
        dist = _haversine(muni_lat, muni_lon, vol["lat"], vol["lon"])
        if dist < min_dist:
            min_dist = dist
    return round(min_dist, 2)
```

---

### 1.4 Fault Density

**What it is:**
The length of faults per square kilometer within a municipality. Higher density = more fractures = better fluid pathways for geothermal heat.

**Formula:**
```
fault_density = fault_length_km / municipality_area_km2
```

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:174-181
def calculate_fault_density(fault_lengths_km: float, municipality_area_km2: float) -> float | None:
    if not municipality_area_km2 or municipality_area_km2 <= 0:
        return None
    return round(fault_lengths_km / municipality_area_km2, 6)
```

---

## 2. Heat Flow Interpolation

### 2.1 Inverse Distance Weighting (IDW)

**What it is:**
Interpolates heat-flow measurements from the nearest known measurement points. Heat-flow data is sparse, so we estimate a municipality's value from surrounding IHFC (International Heat Flow Commission) measurement stations.

**Formula:**
```
weight_i = 1 / (distance_i ^ power)
if onshore: weight_i *= 2.0

heat_flow = Σ(weight_i × value_i) / Σ(weight_i)
```
- **power** = 2.0 (standard for heat-flow interpolation)
- **radius** = 300 km (covers Philippines from nearby land measurements)
- **min_points** = 3 (need at least 3 neighbors for reliable estimate)
- **Onshore preference** = 2× weight (onshore data is more relevant than offshore)

**Why this is used:**
The Philippines has scattered heat-flow measurements. IDW is the standard geostatistical method for interpolating sparse point data.

**Why it matters:**
Without interpolation, most municipalities would have no heat-flow data at all and could not be scored. IDW lets us estimate values from the nearest 3+ measurements within 300 km.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:213-257
def idw_heat_flow(
    lat: float, lon: float, measurements: pd.DataFrame,
    radius_km: float = 300.0, power: float = 2.0, min_points: int = 3,
    prefer_onshore: bool = True,
) -> float | None:
    if measurements is None or measurements.empty:
        return None

    weights = []
    values = []

    for _, row in measurements.iterrows():
        d = _haversine(lat, lon, float(row["lat"]), float(row["lon"]))
        if 0 < d < radius_km:
            w = 1.0 / (d ** power)
            if prefer_onshore and "onshore" in str(row.get("environment", "")).lower():
                w *= 2.0
            weights.append(w)
            values.append(float(row["heat_flow_mw_m2"]))

    if len(weights) < min_points:
        return None

    return sum(w * v for w, v in zip(weights, values)) / sum(weights)
```

---

### 2.2 Heat Flow Score (Normalization)

**What it is:**
Normalizes raw heat-flow value (mW/m²) to a 0–1 score.

**Formula:**
```
score = (heat_flow − 40) / (150 − 40)
```
- **Range:** 40–150 mW/m² (Philippine context)
- **Clamped:** 0 to 1

**Why this is used:**
Raw heat-flow values vary widely (30–200+ mW/m²). Normalization makes them comparable across all municipalities.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:260-271
def calculate_heatflow_score(heat_flow_mw_m2: float | None) -> float | None:
    if heat_flow_mw_m2 is None:
        return None
    return round(_normalize(heat_flow_mw_m2, 40.0, 150.0), 4)
```

---

## 3. Geothermal Gradient & Reservoir Temperature

### 3.1 Geothermal Gradient

**What it is:**
How fast temperature rises with depth. Calculated from heat flow and thermal conductivity of crustal rock.

**Formula:**
```
G = (heat_flow / 1000) / thermal_conductivity
```
Where:
- **heat_flow** in mW/m² → converted to W/m² by dividing by 1000
- **thermal_conductivity** = 2.5 W/(m·K) (typical crustal rock)
- **Result** in °C/km

**Why this is used:**
The gradient tells us how deep we need to drill to reach useful temperatures. A high gradient means a viable reservoir at shallower depths.

**Why it matters:**
A gradient of 30°C/km at 2,000 m depth gives ~87°C. A gradient of 15°C/km gives only ~57°C — possibly too low for efficient power generation.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:305-326
def calculate_geothermal_gradient(
    heat_flow_mw_m2: float | None, thermal_conductivity_wm_k: float = 2.5
) -> float | None:
    if heat_flow_mw_m2 is None or thermal_conductivity_wm_k <= 0:
        return None
    q_wm2 = heat_flow_mw_m2 / 1000.0
    gradient_c_m = q_wm2 / thermal_conductivity_wm_k
    gradient_c_km = gradient_c_m * 1000.0
    return round(gradient_c_km, 3)
```

---

### 3.2 Reservoir Temperature

**What it is:**
Estimates the temperature at the geothermal reservoir depth (default 2,000 m) using surface temperature and geothermal gradient.

**Formula:**
```
T_reservoir = T_surface + (gradient × depth)
```
Where:
- **T_surface** from NASA POWER climate data
- **gradient** in °C/km
- **depth** in km (default 2,000 m = 2 km)

**Why this is used:**
We cannot directly measure deep reservoir temperatures for every municipality. This extrapolates from surface data using standard geothermal physics.

**Why it matters:**
Reservoir temperature determines the plant type (binary vs flash) and overall efficiency. Below ~100°C, binary cycles are required. Above ~180°C, flash cycles become viable.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:329-348
def calculate_reservoir_temperature(
    surface_temp_c: float | None,
    gradient_c_km: float | None,
    depth_m: float = DEFAULT_RESERVOIR_DEPTH_M,
) -> float | None:
    if surface_temp_c is None or gradient_c_km is None:
        return None
    depth_km = depth_m / 1000.0
    temp = surface_temp_c + (gradient_c_km * depth_km)
    return round(temp, 2)
```

---

## 4. Aquifer Scoring

### 4.1 Aquifer Score (Composite)

**What it is:**
Scores the subsurface rock's ability to host and transmit geothermal fluids. Based on three properties: permeability, porosity, and thickness.

**Formula:**
```
score = 0.5 × permeability_score + 0.3 × porosity_score + 0.2 × thickness_score
```

Where each sub-score is normalized:
- **Permeability:** log₁₀(m²), range −17 to −11
- **Porosity:** 0 to 0.35 (fraction)
- **Thickness:** 0 to 2,000 meters

**Why this is used:**
Even with high heat flow, a tight rock with no pore space cannot circulate fluids. The aquifer score captures whether the geology can support a geothermal system.

**Why it matters:**
The Philippine geothermal fields (Tiwi, Tongonan, Palinpinon) all sit on permeable volcanic rock. Areas with similar heat flow but low permeability (e.g., granite) are not viable.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:274-302
def calculate_aquifer_score(
    permeability: float | None, porosity: float | None, thickness: float | None
) -> float | None:
    if permeability is None or porosity is None or thickness is None:
        return None

    perm_score = _normalize(permeability, -17.0, -11.0)
    poro_score = _normalize(porosity, 0.0, 0.35)
    thick_score = _normalize(thickness, 0.0, 2000.0)

    score = (0.5 * perm_score) + (0.3 * poro_score) + (0.2 * thick_score)
    return round(max(0.0, min(1.0, score)), 4)
```

---

### 4.2 Flow Rate Estimation

**What it is:**
Estimates the mass flow rate of geothermal fluid (kg/s) from aquifer properties. When direct flow data is unavailable, we infer it from permeability and aquifer quality.

**Formula:**
```
flow = 10 + (aquifer_score × permeability_factor × 400)
```
- **Base:** 10 kg/s (minimum for small geothermal field)
- **Range:** 10–500 kg/s (literature range for small-to-medium fields)

**Why this is used:**
Flow meters do not exist for every municipality. This first-order estimate lets us calculate thermal power even without direct measurements.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:351-375
def estimate_flow_rate(
    aquifer_score: float | None, permeability_log10_m2: float | None
) -> float | None:
    if aquifer_score is None or permeability_log10_m2 is None:
        return None

    perm_factor = max(0.0, _normalize(permeability_log10_m2, -17.0, -11.0))
    flow = 10.0 + (aquifer_score * perm_factor * 400.0)
    return round(flow, 2)
```

---

## 5. AHP-Based MCDA Suitability Score

### 5.1 Sub-Score Calculation

**What it is:**
The core ranking formula for geothermal. Uses the Analytic Hierarchy Process (AHP) with 5 weighted criteria. Each criterion gets a sub-score (0–1) and a weight.

| Criterion | Weight | How Sub-Score is Calculated |
|---|---|---|
| **Heat Flow** | 0.30 | Normalized IHFC measurement |
| **Fault Proximity** | 0.15 | `exp(−distance / 20)` — closer faults = higher score |
| **Volcano Proximity** | 0.10 | `exp(−distance / 30)` — closer volcanoes = higher score |
| **Aquifer** | 0.15 | Composite of permeability, porosity, thickness |
| **Temperature** | 0.10 | Normalized surface temperature (20–35°C) |

**Exponential Decay Functions:**
- **Fault decay constant:** 20 km (fault influence drops off rapidly)
- **Volcano decay constant:** 30 km (volcanic influence extends farther)

**Why this is used:**
AHP is the standard multi-criteria method in geothermal site-selection literature. The exponential decay captures the real-world physics: faults channel heat upward, but their influence weakens with distance.

**Why it matters:**
A municipality 10 km from a volcano in low-permeability granite scores lower than one 30 km from a volcano but sitting on porous volcanic rock. The weighted combination captures this trade-off.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:457-488
# Sub-scores (all 0-1)
sub_scores = {
    "heat_flow": heat_flow_score or 0.0,
    "fault": math.exp(-(fault_dist or 100) / 20.0) if fault_dist is not None else 0.0,
    "volcano": math.exp(-(volcano_dist or 100) / 30.0) if volcano_dist is not None else 0.0,
    "aquifer": aquifer_score or 0.0,
    "temperature": temp_score or 0.0,
}

# Availability flags (1.0 if data exists, 0.0 otherwise)
avail = {
    k: 1.0 if sub_scores[k] > 0 or (k == "fault" and fault_dist is not None) or (k == "volcano" and volcano_dist is not None) else 0.0
    for k in sub_scores
}
```

---

### 5.2 Weighted Aggregation

**What it is:**
Combines the 5 sub-scores using AHP weights. Missing data is handled gracefully — unavailable criteria do not penalize the score.

**Formula:**
```
total_weight = Σ(weight_i × availability_i)
score = Σ(sub_score_i × weight_i × availability_i) / total_weight
```

**Why this is used:**
If a municipality has no aquifer data but strong heat flow and fault proximity, it should still score well. The availability flag ensures missing data is neutral, not punitive.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:486-493
total_weight = sum(ahp_weights[k] * avail[k] for k in ahp_weights)
if total_weight > 0:
    geothermal_score = sum(sub_scores[k] * ahp_weights[k] * avail[k] for k in ahp_weights) / total_weight
else:
    geothermal_score = 0.0

# Clamp and round
geothermal_score = max(0.0, min(1.0, geothermal_score))
```

---

### 5.3 Classification

**What it is:**
Converts the numeric score into a qualitative classification for user-facing display.

| Score Range | Classification |
|---|---|
| ≥ 0.80 | High |
| ≥ 0.60 | Good |
| ≥ 0.40 | Moderate |
| < 0.40 | Low |

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:496-503
if geothermal_score >= 0.80:
    classification = "High"
elif geothermal_score >= 0.60:
    classification = "Good"
elif geothermal_score >= 0.40:
    classification = "Moderate"
else:
    classification = "Low"
```

---

## 6. Geothermal Energy Output

### 6.1 Thermal Power

**What it is:**
The total heat energy extracted from the reservoir per second. This is the raw thermal energy before conversion to electricity.

**Formula:**
```
Q = ṁ × Cp × ΔT
```
Where:
- **ṁ** = mass flow rate (kg/s)
- **Cp** = 4.186 kJ/(kg·°C) (specific heat of water)
- **ΔT** = reservoir_temp − reinjection_temp (°C)
- **Reinjection temp** = 70°C (cooled fluid returned to reservoir)
- **Result** converted from kW to MW by dividing by 1,000

**Why this is used:**
This is the fundamental thermodynamic equation for geothermal heat extraction. Every geothermal engineering textbook uses this form.

**Why it matters:**
A reservoir at 150°C with 50 kg/s flow produces ~16.7 MW thermal. The same flow at 100°C produces only ~6.3 MW thermal — a 2.6× difference that determines project viability.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:570-576
delta_t = reservoir_temp - REINJECTION_TEMP_C  # 70°C
if delta_t <= 0:
    delta_t = 1.0  # prevent zero/negative thermal power

# Q = m_dot * Cp * delta_T  (Cp in kJ/kgC, convert to MW)
thermal_power_mw = (flow_rate * CP_KJ_KG_C * delta_t) / 1000.0
```

---

### 6.2 Electric Power

**What it is:**
The actual electricity generated from thermal power, accounting for plant efficiency.

**Formula:**
```
P_electric = P_thermal × efficiency
```

| Plant Type | Efficiency | When Used |
|---|---|---|
| **Binary** | 12% (0.12) | Lower temperature reservoirs (<150°C) |
| **Flash** | 15% (0.15) | Higher temperature reservoirs (>150°C) |

**Why this is used:**
No geothermal plant converts 100% of thermal energy to electricity. Binary plants (Organic Rankine Cycle) achieve 10–13%. Flash plants achieve 12–15% but require hotter reservoirs.

**Why it matters:**
At 150°C reservoir with 10 MW thermal:
- Binary: 10 × 0.12 = **1.2 MW electric**
- Flash: 10 × 0.15 = **1.5 MW electric**

The 0.3 MW difference determines whether the project is economically viable.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:578-579
efficiency = FLASH_EFFICIENCY if plant_type == "flash" else BINARY_EFFICIENCY
electric_power_mw = thermal_power_mw * efficiency
```

---

### 6.3 Annual Energy

**What it is:**
Total electricity produced per year, used for comparison with household-scale sources in EcoSim.

**Formula:**
```
Annual Energy (GWh) = (Electric Power MW × 8,760 hours) / 1,000
```

**Why this is used:**
Converts power (instantaneous) into energy (annual total). EcoSim divides this by 12 to get monthly kWh for household comparison.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:582
annual_energy_gwh = (electric_power_mw * 8760.0) / 1000.0
```

---

## 7. Proximity Boost

### 7.1 Operating Plant Distance

**What it is:**
Boosts the geothermal suitability score if a municipality is near an existing operating geothermal plant. Existing plants are strong evidence of viable subsurface conditions.

**Formula:**
```
boosted_score = base_score + max_bonus × (1 − distance / radius)
```
- **radius** = 25 km (zone of influence)
- **max_bonus** = 30 points
- **Capped at 100**

**Why this is used:**
The Philippines has proven geothermal fields (Tiwi, Tongonan, Palinpinon). If a municipality is 5 km from Tiwi, it has very high probability of similar subsurface geology.

**Why it matters:**
Without the boost, Leyte municipalities near Tongonan could score "Moderate" on sparse data alone. The boost corrects this by leveraging proven geology.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/plants.py:106-134
def calculate_proximity_boost(
    lat: float, lon: float, base_score: float,
    radius_km: float = DEFAULT_BOOST_RADIUS_KM, max_bonus: float = 30.0,
) -> tuple[float, list[dict[str, Any]]]:
    nearby = get_plants_near(lat, lon, radius_km, only_operating=True)
    if not nearby:
        return base_score, []

    closest = nearby[0]
    distance = closest["distance_km"]

    # Linear taper: bonus = max_bonus * (1 - distance / radius_km)
    bonus = max_bonus * (1.0 - distance / radius_km)
    bonus = max(0.0, bonus)

    boosted = min(base_score + bonus, 100.0)
    return round(boosted, 2), nearby
```

---

## 8. Confidence Scoring

### 8.1 Data Confidence

**What it is:**
A 0–1 score indicating how complete the input data is. Higher confidence = more reliable recommendation.

**Formula:**
```
confidence = 0.5 × heat_flow_avail + 0.3 × aquifer_avail + 0.2 × temp_avail
```

| Data Source | Weight | Condition |
|---|---|---|
| Heat flow / gradient | 0.50 | 1.0 if measured, 0.0 if missing |
| Aquifer | 0.30 | 1.0 if measured, 0.0 if missing |
| Temperature | 0.20 | 1.0 if NASA POWER measured, 0.5 if fallback (27°C) |

**Why this is used:**
Not all municipalities have equal data quality. The confidence score warns users when the recommendation is based on sparse or inferred data.

**Why it matters:**
A "High" classification with 0.95 confidence is very different from a "High" classification with 0.35 confidence. The user needs to know the difference.

**Exact code:**
```python
# fastapi-backend/app/services/geothermal/features.py:585-588
avail_heat = 1.0 if gradient_c_km is not None else 0.0
avail_aq = 1.0 if aquifer_score is not None else 0.0
avail_temp = 0.5 if used_fallback_temp else 1.0
confidence = (0.5 * avail_heat) + (0.3 * avail_aq) + (0.2 * avail_temp)
confidence = round(min(1.0, confidence), 3)
```

---

## 9. Integration in EcoSim Dashboard

### 9.1 Monthly kWh Conversion

**What it is:**
Geothermal is utility-scale, so annual GWh is converted to monthly kWh for comparison with household solar/wind/hydro.

**Formula:**
```
monthly_kWh = (annual_GWh × 1,000,000) / 12
```

**Why this is used:**
EcoSim compares all four sources on the same scale. A 10 MW geothermal plant produces ~8,760,000 kWh/year = 730,000 kWh/month — far exceeding a typical household's 500 kWh/month.

**Exact code:**
```python
# fastapi-backend/app/services/ecosim.py:818-819
geo_annual_gwh = geothermal_output.get("annual_energy_gwh") or 0.0
geo_monthly_kwh = (geo_annual_gwh * 1_000_000) / 12.0
```

---

### 9.2 Proximity Boost Application

**What it is:**
Before MCDA ranking, the raw geothermal score gets boosted if near an operating plant.

**Exact code:**
```python
# fastapi-backend/app/services/ecosim.py:807-815
raw_geo_score = float(geothermal_output.get("suitability_score", 0.0))
if muni_lat is not None and muni_lon is not None:
    boosted_score, nearby_geo_plants = calculate_proximity_boost(
        float(muni_lat), float(muni_lon), raw_geo_score
    )
    geo_score = boosted_score / 100.0
else:
    geo_score = raw_geo_score / 100.0
```

---

### 9.3 Utility-Scale Exclusion

**What it is:**
Geothermal is excluded from the household recommendation because it requires utility-scale drilling (typically PHP 100M+ investment, not a household decision).

**Exact code:**
```python
# fastapi-backend/app/services/ecosim.py:862-863
household_options = [o for o in options if o.get("scale") != "utility"]
```

---

## 10. Summary Cheat Sheet

| # | Formula | What It Does | Key Constant | File |
|---|---|---|---|---|
| 1 | **Haversine** | Distance between lat/lon points | R = 6,371 km | `features.py:42` |
| 2 | **Fault Distance** | Nearest active fault | Min over all faults | `features.py:145` |
| 3 | **Volcano Distance** | Nearest volcano | Min over all volcanoes | `features.py:184` |
| 4 | **Fault Density** | Fault length per km² | `length / area` | `features.py:174` |
| 5 | **IDW Heat Flow** | Interpolate sparse measurements | power=2, radius=300km | `features.py:213` |
| 6 | **Heat Flow Score** | Normalize 40–150 mW/m² | `(HF−40)/(150−40)` | `features.py:260` |
| 7 | **Geothermal Gradient** | °C per km depth | `G = HF / (1000 × 2.5)` | `features.py:305` |
| 8 | **Reservoir Temp** | Extrapolate to 2,000 m | `T_surface + G × 2` | `features.py:329` |
| 9 | **Aquifer Score** | Permeability + porosity + thickness | 0.5/0.3/0.2 weights | `features.py:274` |
| 10 | **Flow Rate** | Estimate from aquifer properties | `10 + score × perm × 400` | `features.py:351` |
| 11 | **Fault Sub-Score** | Exponential decay | `exp(−dist/20)` | `features.py:474` |
| 12 | **Volcano Sub-Score** | Exponential decay | `exp(−dist/30)` | `features.py:475` |
| 13 | **AHP Score** | Weighted average of 5 criteria | Weights: 0.30/0.15/0.10/0.15/0.10 | `features.py:486` |
| 14 | **Classification** | Qualitative label | High/Good/Moderate/Low | `features.py:496` |
| 15 | **Thermal Power** | Raw heat extraction | `Q = ṁ × 4.186 × ΔT / 1000` | `features.py:576` |
| 16 | **Electric Power** | After plant efficiency | `P = Q × 0.12` or `× 0.15` | `features.py:579` |
| 17 | **Annual Energy** | GWh per year | `P × 8760 / 1000` | `features.py:582` |
| 18 | **Proximity Boost** | Bonus near operating plants | `+30 × (1 − dist/25)` | `plants.py:130` |
| 19 | **Confidence** | Data completeness | 0.5/0.3/0.2 weighted | `features.py:585` |
| 20 | **Monthly kWh** | For EcoSim comparison | `GWh × 1,000,000 / 12` | `ecosim.py:819` |

---

## Key Constants

| Constant | Value | Meaning |
|---|---|---|
| `CP_KJ_KG_C` | 4.186 | Specific heat of water, kJ/(kg·°C) |
| `BINARY_EFFICIENCY` | 0.12 | Binary plant efficiency (12%) |
| `FLASH_EFFICIENCY` | 0.15 | Flash plant efficiency (15%) |
| `DEFAULT_RESERVOIR_DEPTH_M` | 2,000 | Assumed drilling depth (meters) |
| `REINJECTION_TEMP_C` | 70 | Cooled fluid return temperature (°C) |
| `DEFAULT_BOOST_RADIUS_KM` | 25 | Proximity boost radius (km) |
| `PH_MIN_LAT / PH_MAX_LAT` | 4.0 / 21.5 | Philippine bounding box |
| `PH_MIN_LON / PH_MAX_LON` | 116.0 / 127.0 | Philippine bounding box |

---

*Generated from source code analysis of `fastapi-backend/app/services/geothermal/` — current as of latest repository commit.*
