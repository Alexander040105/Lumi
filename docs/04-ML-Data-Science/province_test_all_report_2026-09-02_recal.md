# Renewable Energy Calibration Report

**Date:** 2026-09-02  
**Branch:** `development3`  
**Calibration goal:** Replace the unbounded cubic wind model with a household-scale power curve, raise micro-hydro output in high-feasibility catchments, and produce a balanced province-level recommendation distribution without source bias.

## 1. Model changes

### Wind power curve

The previous wind model allowed output to grow indefinitely with the cube of wind speed. This produced unrealistic household outputs (e.g. 325–440 kWh/month) and a strong wind bias.

The new model uses a household-scale turbine power curve:

- `cut_in_speed_mps = 3.0`
- `rated_speed_mps = 11.0`
- `cut_out_speed_mps = 25.0`
- `rated_power_kw = 1.2`
- `rotor_radius_m = 6.2` (≈12.4 m diameter; low-wind-optimized small-farm/community-scale rotor)
- `capacity_factor = 0.22`
- `cp` from product average (0.239)
- Instantaneous power follows `0.5 * rho * A * v³ * cp * efficiency` below rated speed, then is capped at `rated_power_kw`.

### Province wind aggregation

Province mode continues to compute wind output for each municipality and take the **median** municipality output, avoiding the v³ distortion that comes from averaging wind speeds.

### Hydro calibration

Catchment-enriched hydro was recalibrated with physically realistic household micro-hydro assumptions:

- `household_hydro_head_factor = 0.50`
- `household_hydro_design_flow_factor = 0.80`
- `household_hydro_max_head_m = 30.0`
- `household_hydro_turbine_efficiency = 0.85`
- `household_hydro_generator_efficiency = 0.95`
- `household_hydro_catchment_km2 = 2.0`
- `household_hydro_catchment_fraction = 0.002` (0.2 % of the upstream catchment)

The effective catchment area is now recomputed at runtime from the original Boothroyd et al. catchment area using the configured fraction and cap, so the settings can be tuned without regenerating the enrichment CSV.

### Recommendation logic

Primary recommendation is still based on generated monthly energy (highest kWh wins). Suitability-score-based recommendation remains hidden in the response for possible future reactivation.

## 2. Settings summary

| Setting | Value | Notes |
|---|---|---|
| `household_wind_rotor_radius_m` | 6.2 | Small-turbine low-wind-optimized rotor |
| `household_wind_rated_power_kw` | 1.2 | Household inverter/generator cap |
| `household_wind_capacity_factor` | 0.22 | Small turbine annual-average CF |
| `household_wind_cut_in_mps` | 3.0 | Typical small-turbine cut-in |
| `household_hydro_head_factor` | 0.50 | Fraction of stream/dem head used |
| `household_hydro_design_flow_factor` | 0.80 | Usable flow after environmental reserve |
| `household_hydro_turbine_efficiency` | 0.85 | Micro-hydro turbine efficiency |
| `household_hydro_generator_efficiency` | 0.95 | Generator/inverter efficiency |
| `household_hydro_catchment_fraction` | 0.002 | Household share of total catchment |
| `household_hydro_catchment_km2` | 2.0 | Upper cap on effective catchment area |
| `household_hydro_max_head_m` | 30.0 | Maximum realistic household head |

## 3. Nine target provinces

| Province | Solar (kWh/mo) | Wind (kWh/mo) | Hydro (kWh/mo) | Recommendation |
|---|---:|---:|---:|---|
| Bulacan | 135.4 | 135.0 | 0.5 | Solar |
| Camarines Sur | 135.8 | 190.1 | 25.9 | Wind |
| Leyte | 131.5 | 150.9 | 0.9 | Wind |
| Eastern Samar | 134.6 | 103.8 | 2.8 | Solar |
| Cavite | 142.7 | 190.1 | 4.5 | Wind |
| Laguna | 136.8 | 137.5 | 4.5 | Wind |
| Batangas | 144.7 | 141.6 | 8.4 | Solar |
| Rizal | 139.7 | 112.4 | 11.3 | Solar |
| Quezon | 137.9 | 118.7 | 0.6 | Solar |

- **Wind:** 4 (44 %)
- **Solar:** 5 (56 %)
- **Hydro:** 0

No single renewable source dominates the nine target provinces. Solar and Wind are both well-represented; Hydro remains low in these provinces because the available catchment/head resources are not sufficient to beat solar or wind at the household scale.

## 4. All 120 provinces

- **Total tested:** 84
- **Lookup/data errors:** 36 (same 404/lookup failures as the previous run: highly urbanized cities, renamed provinces, and special geographic areas)
- **Solar:** 46 (54.8 %)
- **Wind:** 35 (41.7 %)
- **Hydropower:** 3 (3.6 %)

### Output ranges

| Source | Min | Max | Mean | Median |
|---|---:|---:|---:|---:|
| Solar (kWh/mo) | 124.9 | 154.5 | 138.0 | 137.0 |
| Wind (kWh/mo) | 0.0 | 190.1 | 132.0 | 133.1 |
| Hydro (kWh/mo) | 0.005 | 194.2 | 18.9 | 4.9 |

### Hydro winners

| Province | Solar (kWh/mo) | Wind (kWh/mo) | Hydro (kWh/mo) |
|---|---:|---:|---:|
| Agusan del Norte | 124.9 | 141.4 | 194.2 |
| Benguet | 142.6 | 150.8 | 165.9 |
| Kalinga | 137.3 | 150.9 | 151.5 |

These three provinces have catchment/head/stream conditions from the Boothroyd et al. enrichment that support realistic household-scale micro-hydro generation, and Hydro now wins without blanket inflation.

## 5. Balance assessment

The province-level recommendation split is:

- Solar ~55 %
- Wind ~42 %
- Hydro ~4 %

This is close to the calibrated municipality-scale target and satisfies the requirement that no single renewable source dominate recommendations. Wind is no longer inflated by unbounded cubic physics, and Hydro wins only where the catchment data support it.

## 6. Verification

- **Backend focused tests:** 57 passed (including 5 new power-curve tests)
- **Frontend build:** `npm run build` passed in `react-frontend/`
- **All 120 provinces:** tested through the live API
- **Errors:** 36 records returned 404 or lookup failures (unchanged; data-source naming issues, not model issues)

## 7. Notable edge cases

1. **Batanes / Catanduanes / Camarines Sur / Antique / Cavite:** Hit the wind rated-power cap (190.1 kWh/mo) because their median municipality wind speeds exceed the rated-speed threshold after hub-height extrapolation.
2. **Leyte:** Wind (150.9 kWh/mo) now beats Solar (131.5 kWh/mo). This is a consequence of the power curve capturing higher wind resource in Leyte’s municipalities without the previous unbounded cubic exaggeration.
3. **Rizal / Quezon / Batangas:** Remain Solar; their wind resource is just below the level needed to overcome the local solar resource.
4. **Hydro in the 9 target provinces:** Remains below Wind/Solar because the catchment areas are small or stream gradients/head are not sufficient.

## 8. Files changed

- `fastapi-backend/app/config/settings.py`
- `fastapi-backend/app/services/wind_output_calc.py`
- `fastapi-backend/app/services/hydro_output_calc.py`
- `fastapi-backend/app/services/ecosim.py`
- `fastapi-backend/tests/test_calibration.py`
