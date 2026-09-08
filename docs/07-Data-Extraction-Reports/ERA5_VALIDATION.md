# ERA5 Validation

## Data

- ERA5 10 m wind: 2015-01-01 to 2026-08-14, hourly, 0.25° grid, 8,488 time steps.
- GWA 10 m and 100 m wind: single-layer GeoTIFFs from Global Wind Atlas.
- Comparison at 1,376 municipality centroids.

## Key findings

| Metric | ERA5 10 m | GWA 10 m | GWA 100 m |
|---|---|---|---|
| Mean wind speed (m/s) | 1.02 | 1.27 | 4.24 |
| Min wind speed (m/s) | 0.00 | 0.00 | 0.00 |
| Max wind speed (m/s) | 5.05 | 6.36 | 10.52 |
| ERA5 vs GWA 10 m MAE (m/s) | 1.04 | — | — |
| ERA5 vs GWA 10 m correlation | 0.08 | — | — |
| ERA5 vs GWA 100 m correlation | 0.59 | — | — |

## Interpretation

- ERA5 10 m speeds are generally low and smooth, as expected for a global reanalysis.
- GWA 10 m values are highly variable and include many near-zero cells (e.g., 0.15 m/s). This can produce unrealistic wind power at 10 m.
- ERA5 10 m correlates more strongly with GWA 100 m than with GWA 10 m, which suggests the GWA 10 m product is noisier or represents a different statistical mean.
- For utility-scale wind, GWA 100 m remains the preferred source. ERA5 10 m is best used as a high-resolution 10 m reference or for validation.

## Sample municipalities

| municipality_id | ERA5 10 m (m/s) | GWA 10 m (m/s) | GWA 100 m (m/s) |
|---|---|---|---|
| 5145 | 1.06 | 1.45 | 4.05 |
| 5146 | 1.42 | 0.43 | 6.30 |
| 5147 | 1.21 | 0.24 | 5.24 |
| 5151 | 1.64 | 0.15 | 5.02 |
| 5153 | 0.96 | 2.10 | 4.07 |

## Recommendation

- Keep `data_source=atlas` as the default; it uses GWA 100 m, the most relevant hub height.
- Use `data_source=era5` when a consistent, observation-corrected 10 m reference is needed for a specific turbine or for cross-checking the GWA 100 m values.
- ERA5 should not be treated as a bankable wind-yield source by itself; it lacks hub-height extrapolation, local roughness, and turbine power-curve modelling.
