# Province Atlas Validation

## Method

Province-level atlas values were computed using two independent methods:

1. **Area-weighted municipal average** — every municipality in a province is weighted by its `area_km2` from the verified centroid CSV, then averaged. This preserves the spatial coverage and size differences of municipalities.
2. **Direct province centroid sample** — the Global Solar Atlas and Global Wind Atlas rasters are sampled at the province polygon centroid from `geospatial_province_centroids.csv`.

The final `solar_*` and `wind_*` values in `province_atlas_averages` default to the **area-weighted municipal average** because it better represents the whole province than a single centroid sample. When a variable differs between the two methods by more than 5%, a `reconciliation_note` is recorded.

## Coverage

- 82 provinces computed
- 1,376 municipalities used for area-weighted aggregation
- Solar rasters: GSA `LTAy_AvgDailyTotals` (GHI, DNI, DIF, GTI, PVOUT daily, TEMP, OPTA) and `LTAy_YearlyMonthlyTotals` (PVOUT annual)
- Wind rasters: GWA `wind-speed_10m`, `wind-speed_50m`, `wind-speed_100m`

## Sample results

| Province | PVOUT annual (kWh/kWp/y) | Wind 100 m (m/s) | Municipalities | Notes |
| --- | --- | --- | --- | --- |
| Ilocos Norte | 1511.09 | 5.30 | 22 | DNI, GTI, temperature, tilt, and all wind heights differ >5% |
| Ilocos Sur | 1476.39 | 3.61 | 27 | DNI, GTI, daily PVOUT, tilt, and all wind heights differ >5% |
| La Union | 1441.13 | 2.66 | 14 | Temperature, tilt, and wind speeds differ >5% |
| Pangasinan | 1566.93 | 4.97 | 35 | 10m/50m/100m wind speeds differ >5% |
| Batanes | 1366.45 | 6.67 | 6 | All wind layers differ >5% (small island, centroid is coastal) |
| Cagayan | 1437.14 | 5.09 | 26 | DNI and wind speeds differ >5% |
| Isabela | 1379.09 | 3.84 | 29 | DNI, DIF, GTI, tilt, and all wind layers differ >5% |
| Nueva Vizcaya | 1339.94 | 4.02 | 13 | DNI, temperature, and all wind layers differ >5% |
| Nueva Ecija | 1527.76 | 5.59 | 26 | No >5% differences between methods |
| Pampanga | 1514.70 | 4.54 | 18 | 10m wind speed differs >5% |

## Expected differences

- **Wind** shows the largest centroid-vs-municipal divergence because wind is more spatially variable and a single centroid can land on a ridge, valley, or coastline.
- **Solar** is more spatially stable; differences are usually small except for large provinces with varied elevation or cloud patterns.
- **Batanes** is an extreme example: the centroid is on a small island, while the municipal average includes multiple islands, giving a better province-wide picture.

## Reproducibility

Run the full pipeline:

```powershell
.venv\Scripts\python.exe scripts\ingest_atlas_averages.py
.venv\Scripts\python.exe scripts\build_province_atlas_averages.py
# After creating the table:
# .venv\Scripts\python.exe scripts\ingest_province_atlas_averages.py
```

Output CSVs:
- `scripts/gap_output/province_atlas_averages.csv`
- `fastapi-backend/app/services/local_data/province_atlas_averages.csv`

## Limitations

- Province boundaries are treated as static polygons; small boundary changes are not re-derived.
- Centroid sampling is a single point; it does not capture sub-provincial variation.
- No rooftop geometry, shading, or land-use exclusions are applied.
- Wind values are annual mean speed only; no turbine power curve, wake losses, or site measurements are included.
