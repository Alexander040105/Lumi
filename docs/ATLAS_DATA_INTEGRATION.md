# Atlas Data Integration

LUMI now uses high-resolution **Global Solar Atlas (Solargis / World Bank)** and **Global Wind Atlas (DTU / World Bank)** rasters for municipal and provincial solar and wind screening.

## What changed

- New backend service `app/services/atlas_data.py` loads atlas values from Supabase (`municipality_atlas_averages`) or falls back to `app/services/local_data/municipality_atlas_averages.csv`.
- `app/services/ecosim.py` accepts a `data_source` parameter (`nasa`, `atlas`, `auto`) and uses GSA `PVOUT` directly for solar output and 100 m GWA wind speed for wind output when atlas data is available.
- `app/services/solar_output_calc.py` now exports `solar_calc_pvout`, which uses the atlas-specific-yield value without double-counting losses.
- Map suitability scores for `solar_suitability_score` and `wind_suitability_score` have been updated from the atlas CSV via `scripts/update_municipality_suitability_from_atlas.py`.

## Data files

| File | Purpose |
|---|---|
| `newDataPointsToExtract/GlobalSolarAtlasGIS/.../LTAy_AvgDailyTotals/GHI.tif` | Daily GHI (kWh/m²/day) |
| `newDataPointsToExtract/GlobalSolarAtlasGIS/.../LTAy_AvgDailyTotals/PVOUT.tif` | Daily PV specific yield (kWh/kWp/day) |
| `newDataPointsToExtract/GlobalSolarAtlasGIS/.../LTAy_YearlyMonthlyTotals/PVOUT.tif` | Annual PV specific yield (kWh/kWp/year) |
| `newDataPointsToExtract/GlobalSolarAtlasGIS/.../LTAy_AvgDailyTotals/DNI.tif` | Direct normal irradiance |
| `newDataPointsToExtract/GlobalSolarAtlasGIS/.../LTAy_AvgDailyTotals/DIF.tif` | Diffuse horizontal irradiance |
| `newDataPointsToExtract/GlobalSolarAtlasGIS/.../LTAy_AvgDailyTotals/GTI.tif` | Global tilted irradiance (optimum tilt) |
| `newDataPointsToExtract/GlobalSolarAtlasGIS/.../LTAy_AvgDailyTotals/TEMP.tif` | Long-term average temperature (°C) |
| `newDataPointsToExtract/GlobalSolarAtlasGIS/.../LTAy_AvgDailyTotals/OPTA.tif` | Optimum tilt angle (°) |
| `newDataPointsToExtract/GlobalWindAtlas_PHL_wind-speed_10m.tif` | 10 m wind speed (m/s) |
| `newDataPointsToExtract/GlobalWindAtlas_PHL_wind-speed_50m.tif` | 50 m wind speed (m/s) |
| `newDataPointsToExtract/GlobalWindAtlas_PHL_wind-speed_100m.tif` | 100 m wind speed (m/s) |

## Extraction pipeline

1. Run `python scripts/extract_centroids.py` and `python scripts/insert_geospatial_metadata.py` to refresh true polygon centroids.
2. Run `python scripts/extract_atlas_values.py` to sample the rasters and produce `scripts/gap_output/municipality_atlas_averages.csv`.
3. (Optional) Run `python scripts/ingest_atlas_averages.py` after creating the `municipality_atlas_averages` table via `supabase_tables_scripts/municipality_atlas_schema.sql`.
4. Run `python scripts/update_municipality_suitability_from_atlas.py` to update the live map scores in the `municipalities` table.
5. For provinces, create the `province_atlas_averages` table with `supabase_tables_scripts/province_atlas_schema.sql`, then run `python scripts/build_province_atlas_averages.py` and `python scripts/ingest_province_atlas_averages.py`.
6. The local CSV fallbacks at `fastapi-backend/app/services/local_data/` keep EcoSim working before the tables are created.

## Solar calculation

Atlas PVOUT already includes temperature, soiling, wiring, inverter, and other losses, so the new mode does **not** re-apply the old performance-ratio chain:

```
daily_kWh = system_kWp * (PVOUT_annual / 365)
annual_kWh = system_kWp * PVOUT_annual
```

To use the old physics-based GHI model, call EcoSim with `?data_source=nasa`.

## Wind calculation

Atlas 100 m wind speed is used in the existing `P = 0.5 * ρ * A * V³ * Cp * η` calculation. If no 100 m value is available, the system falls back to NASA POWER `ws10m`.

## Attribution

- Solar data © 2019 Solargis, published by the World Bank in the Global Solar Atlas 2.0, CC BY 4.0.
- Wind data © DTU / World Bank, Global Wind Atlas, CC BY 4.0.

## Province atlas

Province values are computed in two ways and reconciled:
1. **Area-weighted municipal average** — municipalities are weighted by `area_km2` from the verified centroid CSV.
2. **Direct centroid sample** — the GSA/GWA rasters are sampled at the province polygon centroid.

The final values default to the area-weighted municipal average because it represents the whole province better than a single point. The `reconciliation_note` column records any variable where the two methods differ by more than 5%. See `docs/PROVINCE_ATLAS_VALIDATION.md` for the full validation report.

## Validation notes

Atlas values are **modeled, screening-level estimates**, not bankable measurements. Local shading, rooftop geometry, grid connection, and turbine-specific power curves are still not captured.
