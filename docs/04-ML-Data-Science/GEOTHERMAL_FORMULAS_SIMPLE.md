# LUMI Geothermal Formulas: Simplified Panel Reference

**Project:** LUMI  
**Module:** Geothermal Suitability & Output  
**Date:** June 2026

---

## 1. Haversine Distance

**What it is:** Distance between two lat/lon points on Earth. Finds the nearest fault and volcano.

**Formula:**
```
d = 6371 × 2 × atan2(√a, √(1−a))
a = sin²(Δφ/2) + cos(φ₁)cos(φ₂)sin²(Δλ/2)
```

**Why it matters:** Without accurate distance, a municipality 5 km from a fault scores the same as one 200 km away.

**Code:**
```python
# features.py:42-53
def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
```

---

## 2. Fault & Volcano Distance

**What it is:** Minimum distance from a municipality to the nearest mapped fault or volcano.

**Code:**
```python
# features.py:145-171 (fault), 184-210 (volcano)
def calculate_fault_distance(muni_lat, muni_lon, faults):
    min_dist = min(_haversine(muni_lat, muni_lon, f["lat"], f["lon"]) for f in faults)
    return round(min_dist, 2)
```

---

## 3. Inverse Distance Weighting (IDW) — Heat Flow

**What it is:** Interpolates sparse IHFC heat-flow measurements from the nearest known stations.

**Formula:**
```
weight = 1 / (distance²)
if onshore: weight *= 2
heat_flow = Σ(weight × value) / Σ(weight)
```
- **Radius:** 300 km | **Min points:** 3 | **Power:** 2

**Why it matters:** Most municipalities have no direct heat-flow measurement. IDW estimates from the nearest 3+ stations.

**Code:**
```python
# features.py:213-257
def idw_heat_flow(lat, lon, measurements, radius_km=300, power=2, min_points=3):
    weights, values = [], []
    for _, row in measurements.iterrows():
        d = _haversine(lat, lon, float(row["lat"]), float(row["lon"]))
        if 0 < d < radius_km:
            w = 1.0 / (d ** power)
            if "onshore" in str(row.get("environment", "")).lower():
                w *= 2.0
            weights.append(w); values.append(float(row["heat_flow_mw_m2"]))
    if len(weights) < min_points: return None
    return sum(w * v for w, v in zip(weights, values)) / sum(weights)
```

---

## 4. Heat Flow Score

**What it is:** Normalizes raw heat flow (mW/m²) to 0–1.

**Formula:**
```
score = (heat_flow − 40) / (150 − 40)
```
**Range:** 40–150 mW/m². Clamped 0–1.

**Code:**
```python
# features.py:260-271
def calculate_heatflow_score(heat_flow_mw_m2):
    if heat_flow_mw_m2 is None: return None
    return round(_normalize(heat_flow_mw_m2, 40.0, 150.0), 4)
```

---

## 5. Geothermal Gradient

**What it is:** How fast temperature rises with depth. Determines drilling economics.

**Formula:**
```
gradient (°C/km) = (heat_flow / 1000) / 2.5
```

**Why it matters:** Gradient of 30°C/km at 2,000 m = ~87°C reservoir. 15°C/km = ~57°C — possibly too low.

**Code:**
```python
# features.py:305-326
def calculate_geothermal_gradient(heat_flow_mw_m2, thermal_conductivity_wm_k=2.5):
    q_wm2 = heat_flow_mw_m2 / 1000.0
    return round((q_wm2 / thermal_conductivity_wm_k) * 1000.0, 3)
```

---

## 6. Reservoir Temperature

**What it is:** Estimates temperature at reservoir depth (default 2,000 m).

**Formula:**
```
T_reservoir = T_surface + (gradient × depth_in_km)
```

**Code:**
```python
# features.py:329-348
def calculate_reservoir_temperature(surface_temp_c, gradient_c_km, depth_m=2000):
    depth_km = depth_m / 1000.0
    return round(surface_temp_c + (gradient_c_km * depth_km), 2)
```

---

## 7. Aquifer Score

**What it is:** Scores subsurface rock's ability to host geothermal fluids.

**Formula:**
```
score = 0.5 × permeability + 0.3 × porosity + 0.2 × thickness
```

| Property | Range | Weight |
|---|---|---|
| Permeability (log₁₀ m²) | −17 to −11 | 0.50 |
| Porosity | 0 to 0.35 | 0.30 |
| Thickness (m) | 0 to 2,000 | 0.20 |

**Why it matters:** High heat flow with low permeability = no viable system. Philippine fields sit on porous volcanic rock for a reason.

**Code:**
```python
# features.py:274-302
def calculate_aquifer_score(permeability, porosity, thickness):
    perm = _normalize(permeability, -17.0, -11.0)
    poro = _normalize(porosity, 0.0, 0.35)
    thick = _normalize(thickness, 0.0, 2000.0)
    return round(max(0.0, min(1.0, 0.5*perm + 0.3*poro + 0.2*thick)), 4)
```

---

## 8. Flow Rate Estimation

**What it is:** Estimates geothermal fluid mass flow (kg/s) from aquifer properties.

**Formula:**
```
flow = 10 + (aquifer_score × permeability_factor × 400)
```
**Range:** 10–500 kg/s.

**Code:**
```python
# features.py:351-375
def estimate_flow_rate(aquifer_score, permeability_log10_m2):
    perm_factor = max(0.0, _normalize(permeability_log10_m2, -17.0, -11.0))
    return round(10.0 + (aquifer_score * perm_factor * 400.0), 2)
```

---

## 9. AHP-Based MCDA Suitability Score

**What it is:** The core ranking formula. Combines 5 weighted criteria using the Analytic Hierarchy Process.

### AHP Criteria

| Criterion | Weight | Sub-Score Calculation |
|---|---|---|
| **Heat Flow** | 0.30 | Normalized IHFC measurement |
| **Fault Proximity** | 0.15 | `exp(−distance / 20)` |
| **Volcano Proximity** | 0.10 | `exp(−distance / 30)` |
| **Aquifer** | 0.15 | Permeability + porosity + thickness |
| **Temperature** | 0.10 | Normalized surface temp (20–35°C) |

**Decay constants:** Fault = 20 km, Volcano = 30 km.

### Aggregation

```
total_weight = Σ(weight_i × availability_i)
score = Σ(sub_score_i × weight_i × availability_i) / total_weight
```

**Why it matters:** Missing data is neutral, not punitive. A site with no aquifer data but strong heat flow still scores well.

**Code:**
```python
# features.py:457-493
sub_scores = {
    "heat_flow": heat_flow_score or 0.0,
    "fault": math.exp(-(fault_dist or 100) / 20.0) if fault_dist is not None else 0.0,
    "volcano": math.exp(-(volcano_dist or 100) / 30.0) if volcano_dist is not None else 0.0,
    "aquifer": aquifer_score or 0.0,
    "temperature": temp_score or 0.0,
}

avail = {
    k: 1.0 if sub_scores[k] > 0 or (k in ("fault","volcano") and dist is not None) else 0.0
    for k in sub_scores
}

total_weight = sum(ahp_weights[k] * avail[k] for k in ahp_weights)
score = sum(sub_scores[k] * ahp_weights[k] * avail[k] for k in ahp_weights) / total_weight
score = max(0.0, min(1.0, score))
```

---

## 10. Classification

**What it is:** Qualitative label from numeric score.

| Score | Classification |
|---|---|
| ≥ 0.80 | High |
| ≥ 0.60 | Good |
| ≥ 0.40 | Moderate |
| < 0.40 | Low |

**Code:**
```python
# features.py:496-503
if score >= 0.80: classification = "High"
elif score >= 0.60: classification = "Good"
elif score >= 0.40: classification = "Moderate"
else: classification = "Low"
```

---

## 11. Thermal Power

**What it is:** Raw heat energy extracted from the reservoir per second.

**Formula:**
```
Q (MW) = ṁ × 4.186 × ΔT / 1000
```
- **ṁ** = mass flow (kg/s)
- **4.186** = specific heat of water, kJ/(kg·°C)
- **ΔT** = reservoir_temp − 70°C (reinjection temperature)

**Code:**
```python
# features.py:570-576
delta_t = reservoir_temp - REINJECTION_TEMP_C  # 70°C
if delta_t <= 0: delta_t = 1.0
thermal_power_mw = (flow_rate * CP_KJ_KG_C * delta_t) / 1000.0
```

---

## 12. Electric Power

**What it is:** Actual electricity after plant conversion efficiency.

**Formula:**
```
P_electric = P_thermal × efficiency
```

| Plant Type | Efficiency | When Used |
|---|---|---|
| Binary | 12% | Lower temp (<150°C) |
| Flash | 15% | Higher temp (>150°C) |

**Example:** 10 MW thermal × 0.12 = **1.2 MW electric**.

**Code:**
```python
# features.py:578-579
efficiency = 0.15 if plant_type == "flash" else 0.12
electric_power_mw = thermal_power_mw * efficiency
```

---

## 13. Annual Energy

**What it is:** Total GWh per year for EcoSim comparison.

**Formula:**
```
Annual (GWh) = Electric_MW × 8,760 / 1,000
```

**Code:**
```python
# features.py:582
annual_energy_gwh = (electric_power_mw * 8760.0) / 1000.0
```

---

## 14. Proximity Boost

**What it is:** Bonus points if municipality is near an existing operating geothermal plant.

**Formula:**
```
boosted = base_score + 30 × (1 − distance / 25)
```
**Max bonus:** 30 points. **Radius:** 25 km. **Capped at 100.**

**Why it matters:** A municipality 5 km from Tiwi has very high probability of similar geology.

**Code:**
```python
# plants.py:106-134
def calculate_proximity_boost(lat, lon, base_score, radius_km=25, max_bonus=30):
    nearby = get_plants_near(lat, lon, radius_km)
    if not nearby: return base_score, []
    distance = nearby[0]["distance_km"]
    bonus = max_bonus * (1.0 - distance / radius_km)
    return min(base_score + max(0.0, bonus), 100.0), nearby
```

---

## 15. Confidence Score

**What it is:** 0–1 score of data completeness. Warns users when recommendation is based on sparse data.

**Formula:**
```
confidence = 0.5 × heat_flow + 0.3 × aquifer + 0.2 × temp
```
- **Heat flow:** 1.0 if measured, 0.0 if missing
- **Aquifer:** 1.0 if measured, 0.0 if missing
- **Temp:** 1.0 if NASA POWER, 0.5 if fallback (27°C)

**Code:**
```python
# features.py:585-588
avail_heat = 1.0 if gradient_c_km is not None else 0.0
avail_aq = 1.0 if aquifer_score is not None else 0.0
avail_temp = 0.5 if used_fallback_temp else 1.0
confidence = round(min(1.0, 0.5*avail_heat + 0.3*avail_aq + 0.2*avail_temp), 3)
```

---

## 16. EcoSim Integration

**Monthly kWh conversion:**
```python
# ecosim.py:818-819
geo_monthly_kwh = (annual_energy_gwh * 1_000_000) / 12.0
```

**Proximity boost before ranking:**
```python
# ecosim.py:807-815
raw_geo_score = float(geothermal_output.get("suitability_score", 0.0))
boosted_score, nearby = calculate_proximity_boost(muni_lat, muni_lon, raw_geo_score)
geo_score = boosted_score / 100.0
```

**Excluded from household recommendation** (utility-scale only):
```python
# ecosim.py:862-863
household_options = [o for o in options if o.get("scale") != "utility"]
```

---

## Quick Cheat Sheet

| # | Formula | One-liner | Key Constant | File |
|---|---|---|---|---|
| 1 | Haversine | Distance on Earth | R = 6,371 km | `features.py:42` |
| 2 | Fault Distance | Nearest fault | Min over all faults | `features.py:145` |
| 3 | Volcano Distance | Nearest volcano | Min over all volcanoes | `features.py:184` |
| 4 | IDW Heat Flow | Interpolate sparse data | power=2, radius=300km | `features.py:213` |
| 5 | Heat Flow Score | Normalize to 0–1 | 40–150 mW/m² | `features.py:260` |
| 6 | Gradient | °C per km | HF / (1000 × 2.5) | `features.py:305` |
| 7 | Reservoir Temp | Extrapolate to 2 km | T_surface + G × 2 | `features.py:329` |
| 8 | Aquifer Score | Perm + poro + thick | 0.5/0.3/0.2 weights | `features.py:274` |
| 9 | Flow Rate | Estimate from aquifer | 10 + score × perm × 400 | `features.py:351` |
| 10 | Fault Sub-Score | Exponential decay | exp(−dist/20) | `features.py:474` |
| 11 | Volcano Sub-Score | Exponential decay | exp(−dist/30) | `features.py:475` |
| 12 | AHP Score | Weighted 5-criteria | 0.30/0.15/0.10/0.15/0.10 | `features.py:486` |
| 13 | Classification | Qualitative label | High/Good/Moderate/Low | `features.py:496` |
| 14 | Thermal Power | Raw heat extraction | ṁ × 4.186 × ΔT / 1000 | `features.py:576` |
| 15 | Electric Power | After efficiency | × 0.12 (binary) or × 0.15 (flash) | `features.py:579` |
| 16 | Annual Energy | GWh per year | P × 8760 / 1000 | `features.py:582` |
| 17 | Proximity Boost | Near operating plant | +30 × (1 − dist/25) | `plants.py:130` |
| 18 | Confidence | Data completeness | 0.5/0.3/0.2 weighted | `features.py:585` |
| 19 | Monthly kWh | For EcoSim comparison | GWh × 1,000,000 / 12 | `ecosim.py:819` |

---

## Key Constants

| Constant | Value | Meaning |
|---|---|---|
| `CP_KJ_KG_C` | 4.186 | Specific heat of water |
| `BINARY_EFFICIENCY` | 0.12 | Binary plant (12%) |
| `FLASH_EFFICIENCY` | 0.15 | Flash plant (15%) |
| `DEFAULT_RESERVOIR_DEPTH_M` | 2,000 | Default drilling depth |
| `REINJECTION_TEMP_C` | 70 | Cooled fluid return temp |
| `DEFAULT_BOOST_RADIUS_KM` | 25 | Proximity boost radius |

---

## Paragraph Summary

LUMI's geothermal module implements a physics-based, multi-criteria suitability and output engine grounded in established geoscience and engineering literature. The system begins with spatial analysis: it calculates great-circle distances via the haversine formula to find the nearest active fault and volcano to any Philippine municipality, then interpolates sparse IHFC heat-flow measurements using inverse distance weighting (IDW) with a 300 km radius and onshore preference to estimate local heat flow. This heat flow is normalized to a 0–1 score and converted into a geothermal gradient using standard crustal thermal conductivity (2.5 W/m·K), from which reservoir temperature at 2,000 m depth is extrapolated. Simultaneously, the system queries aquifer properties (permeability, porosity, thickness) through point-in-polygon spatial matching and scores them with AHP-derived weights of 0.5, 0.3, and 0.2, then estimates a plausible mass flow rate of 10–500 kg/s. These five inputs—heat flow, fault proximity, volcano proximity, aquifer quality, and surface temperature—are aggregated through an Analytic Hierarchy Process with weights 0.30, 0.15, 0.10, 0.15, and 0.10, using exponential decay functions for fault (20 km) and volcano (30 km) influence and availability flags to handle missing data gracefully. The resulting 0–1 score is classified as High, Good, Moderate, or Low. For output estimation, the module computes thermal power via Q = ṁCpΔT with a 70°C reinjection baseline, converts to electric power using binary (12%) or flash (15%) plant efficiencies, and annualizes to GWh. A proximity boost of up to 30 points is applied for municipalities within 25 km of operating Philippine geothermal plants such as Tiwi or Tongonan, and a confidence score (0.5/0.3/0.2 weighted) reflects data completeness. Finally, the annual GWh is converted to monthly kWh for EcoSim comparison, though geothermal is excluded from household recommendations because it is utility-scale. All formulas are implemented in the open-source codebase with inline citations and validated by thesis RRL studies including Asadi et al. (2023) for GIS-MCDA frameworks, the IEC 61724 standard for performance ratios, and Philippine DOE (2022) emission factors for CO₂ displacement.

---

*Simplified reference for LUMI thesis panel defense.*
