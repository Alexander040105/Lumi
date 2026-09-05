# EcoSim Renewable Data Audit & Scaling Guide

## 1. Why this audit exists

EcoSim’s wind output was recommending **wind** in locations where it should not, because the calculation was using **100 m hub-height** wind speeds from the Global Wind Atlas. That is a utility-scale height, not a residential one. At 100 m the wind speed is much higher, and because turbine power scales with `V³`, a small household turbine looked far more productive than a real roof/wall-mounted unit.

The first fix (already implemented) forces wind to use the **10 m** wind speed. This guide documents the current state of all four renewable sources, the data they need, and the next concrete steps to make solar, hydro, and geothermal as research-driven and residential-scaled as wind now is.

## 2. Wind (DONE)

### Current inputs

| Input | Source | Column / file | Status |
|-------|--------|---------------|--------|
| 10 m wind speed | Global Wind Atlas | `municipality_atlas_averages.wind_speed_10m_ms` | Used |
| 10 m wind speed (fallback) | ERA5 | `era5_wind_speed_10m_ms` | Used |
| 10 m wind speed (fallback) | NASA POWER | `municipality_climate_averages.avg_ws10m` | Used |
| 100 m wind speed | Global Wind Atlas | `municipality_atlas_averages.wind_speed_100m_ms` | No longer used for household output |

### What changed

- `fastapi-backend/app/services/ecosim.py` now picks wind speed in this order:
  1. `wind_speed_10m_ms`
  2. `era5_wind_speed_10m_ms`
  3. `avg_ws10m`
- The `assumptions` block now includes `wind_speed_height_m: 10` and `wind_speed_mps`.
- `base_results.climate.avg_ws10m` is now the same value used for output, so `wind_score` and `generation_score` are consistent.

### Remaining data task

If `municipality_atlas_averages.wind_speed_10m_ms` is not already populated in Supabase, load it from the bundled CSV or sample the 10 m TIF:

- Bundled CSV: `fastapi-backend/app/services/local_data/municipality_atlas_averages.csv`
- Raw TIF: `newDataPointsToExtract/GlobalWindAtlas_PHL_wind-speed_10m.tif`

## 3. Solar

### Current inputs

| Input | Source | Column / file | Notes |
|-------|--------|---------------|-------|
| GHI | NASA POWER | `municipality_climate_averages.avg_allsky_sfc_sw_dwn` | Always available |
| PVOUT | Global Solar Atlas | `municipality_atlas_averages.solar_pvout_annual_kwh_kwp` | Best data; used when available |
| DNI / DHI / GTI | Global Solar Atlas | `municipality_atlas_averages.solar_dni_kwh_m2_day`, etc. | Available in the CSV, not used in `ecosim.py` |
| Panel size | Hard-coded | 2 × 400 W = 0.8 kWp | Very small; makes solar look weak next to any wind output |

### Current code paths

- `solar_output_calc.py` has three models:
  - `solar_calc` — basic GHI × performance ratio
  - `solar_calc_pvout` — uses GSA `pvout_annual_kwh_kwp` (already includes losses)
  - `solar_calc_advanced` — uses GHI, DNI, DHI, GTI with Hay-Davies transposition
- `ecosim.py` uses `solar_calc_pvout` when `pvout_annual` exists, otherwise `solar_calc`.

### Accuracy issues

1. The panel count (2 × 400 W) is a tiny array. A typical Philippine home installation is 2–5 kWp. With only 0.8 kWp, solar will under-report even in sunny locations.
2. `solar_calc_advanced` is not used even though DNI/DHI/GTI exist in the atlas data.

### Free data to use / add

| Dataset | Use | Where to get it | Cost |
|---------|-----|-----------------|------|
| Global Solar Atlas | GHI, DNI, DHI, GTI, PVOUT | Already in `newDataPointsToExtract/GlobalSolarAtlasGIS` and the `municipality_atlas_averages.csv` | Free |
| PVGIS (JRC) | PVOUT, GHI, temperature-corrected yield | https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY | Free API |
| NASA POWER | GHI, temperature, cloud | Already used | Free |
| NSRDB | Hourly/daily solar, mainly Americas | https://nsrdb.nrel.gov/ | Free, limited PH coverage |

### Recommended next steps

1. Switch `ecosim.py` to `solar_calc_advanced` when `solar_dni_kwh_m2_day` and `solar_dhi_kwh_m2_day` are present in `municipality_atlas_averages`.
2. Replace the hard-coded 2 × 400 W with a configurable `household_solar_size_kwp` (default e.g. 2.0–3.0 kWp).
3. If the Supabase `municipality_atlas_averages` table is missing DNI/DHI/GTI columns, run a migration and sample the Global Solar Atlas GeoTIFFs in `newDataPointsToExtract/GlobalSolarAtlasGIS`.

## 4. Hydropower

### Current inputs

| Input | Source | Column / file | Notes |
|-------|--------|---------------|-------|
| Monthly rainfall | NASA POWER | `municipality_climate_averages.avg_prectotcorr` | Used to estimate flow |
| Terrain slope, head, runoff | Pre-computed | `municipality_terrain_metrics` / `hydropower_suitability` | Optional; degrades if missing |
| Catchment area | Hard-coded | `0.5 km²` | Very coarse |

### Current formula

```python
Q_design = (C × P × A) / seconds_month × design_factor
```

where `C` is a runoff coefficient from slope, `P` is monthly rainfall, `A` is the catchment area, and the design factor accounts for environmental flow.

### Accuracy issues

1. `catchment_area_km2 = 0.5` is the same for every municipality. Real catchment size varies enormously.
2. `hydraulic_head_m` depends on DEM. If the terrain table is empty, hydro output collapses.
3. The rational method is reasonable for a quick ungauged estimate, but it needs real catchment boundaries and slope from a DEM.

### Free data to use / add

| Dataset | Use | Where to get it | Cost |
|---------|-----|-----------------|------|
| HydroSHEDS | Flow accumulation, catchment boundaries, stream network | https://www.hydrosheds.org/ | Free |
| NASA SRTM / NASA DEM | Elevation, slope, head | https://earthexplorer.usgs.gov/ or https://portal.opentopography.org/ | Free |
| MERIT Hydro | Improved DEM-derived hydrology | http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/ | Free |
| FABDEM | Bare-earth DEM | https://data.bodc.ac.uk/ | Free |
| CHIRPS / NASA POWER | Rainfall | Already used / https://www.chc.ucsb.edu/data/chirps | Free |

### Recommended next steps

1. Add `catchment_area_km2` to `municipality_terrain_metrics` by summing the upstream HydroSHEDS catchment for each municipality centroid.
2. Verify `hydraulic_head_m` is DEM-derived (use a local 12 % drop as currently, but from real elevation, not a default).
3. Keep the `0.5 m³/s` and `25 m` caps; they are appropriate household bounds.

## 5. Geothermal

### Current inputs

| Input | Source | Column / file | Notes |
|-------|--------|---------------|-------|
| Pre-computed output | Supabase | `geothermal_output`, `geothermal_suitability` tables | Best data, when available |
| Surface temperature | NASA POWER | `municipality_climate_averages.avg_t2m` | Fallback only |
| Lat / Lon | Supabase | `municipalities` | Fallback only |

### Current behaviour

- If a pre-computed row exists, it is returned.
- If not, a fallback `compute_geothermal_suitability` uses surface temperature and lat/lon.
- Geothermal is always marked `source_type: utility` and is hidden in EcoSim province mode.

### Accuracy issues

1. The fallback is low-confidence. Surface temperature is not a good proxy for geothermal gradient.
2. No proximity to known geothermal fields is used in the fallback.

### Free data to use / add

| Dataset | Use | Where to get it | Cost |
|---------|-----|-----------------|------|
| IHFC Global Heat Flow Database | Heat-flow measurements, geothermal gradient | https://ihfc-iugg.org/products/global-heat-flow-database | Free |
| IHFC Data Download | CSV/XLSX releases | http://www.ihfc-iugg.org/products/global-heat-flow-database/data | Free |
| New Heat Flow Portal | Searchable catalogue | https://www.heatflow.world/data | Free |
| PHILVOLCS | Known geothermal prospects, volcanoes, hot springs | https://volcano.phivolcs.dost.gov.ph/ | Free (Philippine government) |
| World Geothermal Database / GEOROC | Heat-flow and temperature maps | Partial free access | Mixed |

### Recommended next steps

1. Keep `geothermal_output` / `geothermal_suitability` as the primary source.
2. For the fallback, add a proximity search: if a Global Heat Flow point or PHILVOLCS feature is within e.g. 25 km, use its heat-flow value instead of the surface-temperature estimate.
3. Continue to mark geothermal as `utility` and hide it in province mode.

## 6. Data files already in the repo

```
newDataPointsToExtract/
├── GlobalSolarAtlasGIS/          # GSA GeoTIFFs (solar)
├── SolarGis/                     # SolarGIS GeoTIFFs (solar)
├── GlobalWindAtlas_PHL_wind-speed_10m.tif
├── GlobalWindAtlas_PHL_wind-speed_50m.tif
├── GlobalWindAtlas_PHL_wind-speed_100m.tif
├── PHL_GlobalWindAtlas.geojson
└── ERA5_copernicusData.grib      # ERA5 reanalysis (wind, temperature, etc.)

fastapi-backend/app/services/local_data/
├── municipality_climate_averages.csv
├── municipality_atlas_averages.csv   # already has wind 10/50/100, solar GHI/DNI/DHI/GTI/PVOUT
└── province_atlas_averages.csv
```

## 7. Suggested implementation order

1. ✅ **Wind 10 m** — done.
2. **Solar scaling** — switch to `solar_calc_advanced` and a realistic `household_solar_size_kwp`.
3. **Hydro catchment** — add real `catchment_area_km2` from HydroSHEDS + SRTM.
4. **Geothermal fallback** — improve with heat-flow proximity.

## 8. No commits or pushes

Per your earlier instruction, I will not `git commit` or `git push`. You can commit these changes when you are ready.
