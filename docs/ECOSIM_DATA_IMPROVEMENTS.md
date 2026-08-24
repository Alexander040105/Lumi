# EcoSim Data-Accuracy Improvement Roadmap

This document explains the root causes behind two current EcoSim inconsistencies and lists the data needed to fix them in a future pass. It is intended to be a shared checklist for the team before any backend model or data-pipeline changes are made.

---

## 1. Wind Recommendation Contradiction

### What you are seeing
A location with low wind speed is labeled "Wind speeds are low. Consider solar instead.", yet EcoSim still recommends Wind with a high coverage score. This happens because the **estimated monthly kWh for Wind is the highest of the home-scale options**, even when the underlying wind resource is poor.

### Root cause
Two issues combine to produce the contradiction:

1. **The wind-output model overestimates low-wind sites.**  
   `fastapi-backend/app/services/wind_output_calc.py` uses the basic kinetic-energy equation `P = 0.5 × ρ × A × V³ × Cp × η` and then applies a **flat 30% capacity factor** (line 105). It does **not** use:
   - a realistic small-turbine power curve,
   - cut-in / cut-out / rated wind speeds,
   - a Weibull or hourly wind distribution,
   - hub height (it only sees 10 m unless Atlas 100 m data is available),
   - terrain roughness or surface-roughness length.

2. **The recommendation ranking uses raw output as the primary key.**  
   `fastapi-backend/app/services/ecosim.py` lines 1417–1518 compute `suitability_score` for each option, but the final `recommended` source is chosen with:
   ```python
   recommended = max(
       household_options,
       key=lambda item: (item["monthly_output"], item["generation_score"]),
   )
   ```
   So the option with the largest `monthly_output` wins, regardless of whether its climate label is "poor".

### Recommended data to collect before fixing

| Data / parameter | Why it matters | Suggested source |
|---|---|---|
| **Hub-height wind speed** (50–100 m above ground) | Small turbines are usually mounted on towers; 10 m wind speed is too low. | ERA5 reanalysis at hub height, Global Wind Atlas, or AWS/NCAR datasets. |
| **Weibull shape (`k`) and scale (`c`)** or an hourly wind distribution | Real power depends on how often each wind speed occurs, not the average alone. | ERA5 hourly time series or measured meteorological tower data. |
| **Turbine power curves for 1–10 kW small wind turbines** | `P` at a given `V` must respect cut-in, rated, and cut-out speeds; low wind below cut-in should produce zero. | Manufacturer datasheets (e.g., Bergey, SD3, Kingspan) or the SWCC/RETScreen libraries. |
| **Turbine rotor diameter and certified power coefficient (`Cp`)** | Swept area and `Cp` strongly affect output; the current CSV average may not match a real product. | Same manufacturer datasheets; avoid averaging products with very different sizes. |
| **Terrain roughness / surface-roughness length** | Used to extrapolate 10 m wind to hub height. | CORINE land cover, GLO-30 DEM, or local site survey. |
| **Air density at elevation** | Already partially used via `avg_rhoa`; verify it is updated if wind extrapolation is added. | NASA POWER `rhoa` or barometric formula using elevation. |

### Recommended engineering changes (after data is ready)

1. Replace the single `capacity_factor` with a **speed-dependent power curve integration**:
   ```
   E_monthly = Σ_hours P_curve(V_hour) × 1 h
   ```
   where `P_curve` returns `0` below cut-in and above cut-out.
2. Extrapolate 10 m or 100 m wind to the selected hub height using the log wind profile.
3. Make `wind_score` (source quality) drive the recommendation, not only `monthly_output`:
   ```python
   # example: use suitability_score as primary key, output as tie-breaker
   recommended = max(
       household_options,
       key=lambda item: (item["suitability_score"], item["monthly_output"]),
   )
   ```
   This prevents a "poor" wind label from ever being recommended.
4. Add a small sanity check: if `avg_ws10m` (or hub-height wind) is below a calibrated cut-in, force Wind output to near-zero.

---

## 2. Province-Level Geothermal Data Gap

### What you are seeing
When EcoSim is run in **Province** mode, the Geothermal card shows "No significant geothermal activity nearby" or zero values, even though some municipalities inside the province may have data.

### Root cause
`fastapi-backend/app/services/ecosim.py` `get_geothermal_data()` (line 534) queries the pre-computed tables `geothermal_output` and `geothermal_suitability` keyed by `municipality_id`. In province mode, the ID passed in is the `province_id`, and `get_province_data()` (line 402) aggregates climate data from all municipalities in that province. The geothermal lookup therefore finds no pre-computed province row and falls back to an on-the-fly estimate using only the province centroid plus the heat-flow / fault / volcano / aquifer datasets, which are sparse or missing for most centroids.

### Recommended data to collect / generate before fixing

You have two equivalent options. Pick one and document the choice.

#### Option A: Pre-compute province-level rows

| Table / field | Content needed | How to populate |
|---|---|---|
| `provinces` | `province_id`, `name`, `lat`, `lon` (centroid) | Already in Supabase. |
| `geothermal_suitability` | Add `province_id` column or create a new `province_geothermal_suitability` table. | Run `compute_geothermal_suitability(province_lat, province_lon, surface_temp, municipality_id=province_id)` for every province and store the result. |
| `geothermal_output` | Add `province_id` column or create a new `province_geothermal_output` table. | Run `compute_geothermal_output(...)` from the stored suitability values and store the thermal/electric power and annual GWh. |
| Climate input | Province-average surface temperature from `municipality_climate_monthly` or `get_province_data()`. | Re-use existing aggregation (average `t2m` across municipalities). |

#### Option B: Aggregate existing municipality results

| Task | Description |
|---|---|
| Query all municipalities in the province | `client.table("municipalities").select("municipality_id").eq("province_id", province_id).execute()` |
| Fetch their `geothermal_suitability` and `geothermal_output` rows | Use `in_` filters or a pre-joined view. |
| Aggregate | Take the **mean** or **max** `geothermal_score`, `thermal_power_mw`, `electric_power_mw`, and `annual_energy_gwh` for the province. Max is defensible because geothermal potential is usually localized near fault/volcano zones; mean may dilute the signal. |
| Add a flag in the response | `geothermal_aggregation_method: "municipality_mean"` or `"province_centroid"` so the UI can explain the number. |

### Recommended engineering changes (after data is ready)

1. Add `province_id` support to `get_geothermal_data()` or create a parallel `get_province_geothermal_data()` in `ecosim.py`.
2. Call it from `renewable_energy_calculator()` when `mode == "province"`.
3. Ensure the `geothermal_output` dict for provinces uses the same keys as municipalities (`reservoir_temperature_c`, `thermal_power_mw`, `electric_power_mw`, `annual_energy_gwh`, `suitability_score`, `classification`) so `EcosimResults.jsx` needs no special handling.
4. Update the frontend citation text to make it clear whether the value is a province centroid estimate or an aggregate of municipalities.

---

## 3. Validation Plan (for after data acquisition)

- Run a known low-wind municipality through EcoSim. Wind should either be ranked last or have a near-zero kWh estimate.
- Run a known windy coastal municipality. Wind should now track more closely to manufacturer power curves and not exceed the turbine's rated capacity.
- Run Province mode for provinces that contain a known geothermal plant (e.g., Laguna, Albay, Negros Oriental). The Geothermal card should show non-zero values and the correct nearby plant distances.
- Compare a handful of municipalities with hand-calculated values from the new power curve to ensure the monthly kWh is within ±20%.

---

## 4. Files That Will Eventually Be Touched

- `fastapi-backend/app/services/wind_output_calc.py`
- `fastapi-backend/app/services/ecosim.py` (recommendation ranking and province geothermal lookup)
- `fastapi-backend/app/services/geothermal/features.py` (if new aggregation logic is needed)
- Supabase tables: `geothermal_output`, `geothermal_suitability` (add `province_id` or create new province tables)
- `react-frontend/src/components/ecosim/EcosimResults.jsx` (only for citation/explanation text; no formula changes)

---

*This is a recommendation document. No code changes to the wind or geothermal models were made in the current pass; implement the data-acquisition steps above before changing the calculations.*