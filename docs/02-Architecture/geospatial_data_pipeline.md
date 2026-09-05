# Geospatial Data Pipeline

## Pipeline Overview

```
GeoJSON Files (frontend)  →  extract_centroids.py  →  CSV  →  insert_geospatial_metadata.py  →  Supabase
NASA POWER API            →  municipality_climate  →  aggregation  →  province_climate_monthly
Suitability Builder       →  solar/wind/hydro/composite_suitability tables
```

## Step 1: Centroid Extraction

### Script: `scripts/extract_centroids.py`

Reads GeoJSON boundary files from `react-frontend/public/` and computes
centroids and areas using **shapely**.

**Input files:**
- `philippine_geojson_file_per_region.json` — 88 province polygons
- `philippine_geojson_file_per_provinces.min.json` — 1,618 municipality polygons

**Process:**
1. Load GeoJSON FeatureCollection
2. For each Feature, parse geometry with `shapely.geometry.shape()`
3. Compute geometric centroid (lat, lon) from the polygon
4. Extract `area_km2` from GeoJSON properties (fallback: equirectangular approximation)
5. Normalize feature name using `norm()` function (strips "City of", "Municipality", parentheticals)
6. Match normalized name against Supabase admin table records
7. Output CSV with `province_id` or `municipality_id`, centroid, area

**Output:**
- `scripts/gap_output/geospatial_province_centroids.csv`
- `scripts/gap_output/geospatial_municipality_centroids.csv`

**Usage:**
```bash
.venv\Scripts\python.exe scripts\extract_centroids.py
```

### Name Normalization

The `norm()` function handles naming discrepancies between GeoJSON and the database:

| GeoJSON Name | DB Name | Normalized |
|-------------|---------|------------|
| "City of Balanga" | "Balanga" | "balanga" |
| "Quezon City (Capital)" | "Quezon City" | "quezon" |
| "Lambayong (Municipality)" | "Lambayong" | "lambayong" |

### Script: `scripts/insert_geospatial_metadata.py`

Reads the centroid CSVs and upserts into `geospatial_metadata` via Supabase REST API.

- Uses `Prefer: resolution=merge-duplicates` header for upsert behavior
- Skips entries that already exist (idempotent)
- Batch size: 500 rows

**Usage:**
```bash
.venv\Scripts\python.exe scripts\insert_geospatial_metadata.py
```

## Step 2: Climate Data

### Municipality Climate (Existing)

Municipality-level climate data is sourced from NASA POWER and stored in:
- CSV: `fastapi-backend/app/services/local_data/municipality_climate_averages.csv`
- DB: `municipality_climate_monthly` table (via migration)

### Province Climate (New)

Province climate is computed by aggregating municipality climate data:

1. **Direct lookup**: Check `province_climate_monthly` table first
2. **Fallback aggregation**: If no province record exists, fetch all municipalities
   in the province, average their monthly climate values

This logic is implemented in `app/services/climate_service.py` →
`get_or_compute_province_climate()`.

### Barangay Climate (New)

Barangay-level climate uses a fallback hierarchy:

1. Check `barangay_climate_monthly` table (if populated)
2. Fall back to parent municipality's `municipality_climate_monthly`
3. Fall back to province `province_climate_monthly` (or aggregated)

Implemented in `app/services/climate_service.py` →
`get_barangay_climate_or_fallback()`.

## Step 3: Suitability Scores

### Existing Flow

`municipality_suitability_builder.py` computes suitability scores and stores
them in the `municipalities` table columns:
- `solar_suitability_score`, `solar_classification`, `solar_factors`
- `wind_suitability_score`, `wind_classification`, `wind_factors`
- `hydro_suitability_score`, `hydro_classification`, `hydro_factors`
- `composite_suitability_score`, `composite_classification`

### New Flow (Post-Migration)

The migration script copies existing suitability data from `municipalities`
into separate tables:
- `solar_suitability`
- `wind_suitability`
- `hydro_suitability`
- `composite_suitability`

**Backward compatibility**: The `municipalities` columns are NOT dropped.
Services can read from either the old columns or the new tables during
the transition period.

## Step 4: Geospatial Metadata Enrichment

After centroids are loaded, the `geospatial_metadata` table can be further
enriched with:

- **Elevation**: From SRTM DEM or NASA POWER elevation parameter
- **CRS info**: Stored in `crs` column (default: EPSG:4326)
- **Area verification**: Cross-check GeoJSON `area_km2` with computed values

## Execution Order

For a fresh deployment:

1. Run SQL migration: `0001_geospatial_architecture.sql`
2. Run centroid extraction: `python scripts/extract_centroids.py`
3. Run centroid insertion: `python scripts/insert_geospatial_metadata.py`
4. Populate province climate (if not done in migration)
5. Build suitability scores: `python scripts/build_suitability.py` (existing)
6. Warm Redis cache: Call `/api/v1/energyhub/map-data?level=municipality` for each metric
