# ERA5 Integration

## What changed

LUMI now ingests the Copernicus ERA5 10 m wind reanalysis for the Philippines. The dataset (`data/newDataPointsToExtract/ERA5_copernicusData.grib`) provides hourly `u10` and `v10` wind components on a 0.25° grid from 2015-01-01 to 2026-08-14, which we converted to scalar 10 m wind speed and sampled at every municipality and province centroid.

## ERA5 variables in the file

- `u10` — 10 metre U wind component (`m s-1`)
- `v10` — 10 metre V wind component (`m s-1`)
- `u10n` — 10 metre U-component of neutral wind
- `v10n` — 10 metre V-component of neutral wind

The first implementation uses `u10` and `v10` to compute:

```
wind_speed_10m = sqrt(u10^2 + v10^2)
```

Solar and hydro variables are not present in this file, so they continue to come from GSA/GWA or NASA POWER.

## Extraction pipeline

1. Install `xarray`, `cfgrib`, `scipy`:
   ```powershell
   .venv\Scripts\pip.exe install xarray cfgrib scipy
   ```
2. Run the extraction:
   ```powershell
   .venv\Scripts\python.exe scripts/extract_era5_wind.py
   ```
   This writes:
   - `scripts/gap_output/municipality_era5_averages.csv`
   - `scripts/gap_output/province_era5_averages.csv`
   - `fastapi-backend/app/services/local_data/municipality_era5_averages.csv`
   - `fastapi-backend/app/services/local_data/province_era5_averages.csv`
3. Create the Supabase tables:
   - `supabase/table_scripts/municipality_era5_schema.sql`
   - `supabase/table_scripts/province_era5_schema.sql`
4. Ingest:
   ```powershell
   .venv\Scripts\python.exe scripts/ingest_era5_averages.py
   ```

## Source selector

The EcoSim `data_source` parameter now accepts `nasa`, `atlas`, `era5`, and `auto`.

- `nasa` — NASA POWER only.
- `atlas` — Global Solar Atlas / Global Wind Atlas (100 m wind, GSA PVOUT).
- `era5` — ERA5 10 m wind + GSA solar (when available).
- `auto` — Prefers GSA/GWA; falls back to ERA5 for wind if GWA is missing.

## Attribution

- Wind data: ERA5 hourly reanalysis, Copernicus Climate Change Service / ECMWF.
