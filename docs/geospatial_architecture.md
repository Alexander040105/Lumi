# Geospatial Database Architecture

## Overview

LUMI uses a multi-level administrative hierarchy for the Philippines:

```
Regions → Provinces → Municipalities → Barangays
```

The geospatial database architecture separates **boundary polygons** (stored as
GeoJSON files in the frontend) from **centroid metadata** (stored in Supabase).
This allows the backend to serve lightweight coordinate data for map markers
and distance calculations without transferring large polygon files over the API.

## Schema Design

### Core Administrative Tables (Existing)

| Table | PK | FK | Description |
|-------|----|----|-------------|
| `regions` | `region_id` | — | 17 regions of the Philippines |
| `provinces` | `province_id` | `region_id` | 88 provinces |
| `municipalities` | `municipality_id` | `province_id` | 1,618 municipalities |
| `barangays` | `barangay_id` | `municipality_id` | ~42,000 barangays |

### New Tables (Migration 0001)

#### `geospatial_metadata`

Stores centroid coordinates, area, and elevation for any admin unit.

| Column | Type | Description |
|--------|------|-------------|
| `metadata_id` | BIGSERIAL | PK |
| `region_id` | BIGINT | FK → regions (nullable) |
| `province_id` | BIGINT | FK → provinces (nullable) |
| `municipality_id` | BIGINT | FK → municipalities (nullable) |
| `barangay_id` | BIGINT | FK → barangays (nullable) |
| `centroid_lat` | DOUBLE PRECISION | Latitude of geometric centroid |
| `centroid_lon` | DOUBLE PRECISION | Longitude of geometric centroid |
| `area_km2` | DOUBLE PRECISION | Area in square kilometers |
| `elevation_m` | DOUBLE PRECISION | Average elevation in meters |
| `crs` | TEXT | Coordinate reference system (default: EPSG:4326) |
| `source` | TEXT | Data source (e.g., "GeoJSON centroid") |

**CHECK constraint**: Exactly one of `region_id`, `province_id`, `municipality_id`,
`barangay_id` must be non-null.

#### `province_climate_monthly`

Monthly climate data at the province level.

| Column | Type | Description |
|--------|------|-------------|
| `province_id` | BIGINT | FK → provinces |
| `year` | INT | Year (e.g., 2024) |
| `month` | INT | Month (1-12) |
| `t2m` | REAL | Temperature at 2m (°C) |
| `t2m_max` | REAL | Max temperature at 2m (°C) |
| `t2m_min` | REAL | Min temperature at 2m (°C) |
| `rh2m` | REAL | Relative humidity at 2m (%) |
| `prectotcorr` | REAL | Precipitation (mm/day) |
| `ws10m` | REAL | Wind speed at 10m (m/s) |
| `allsky_sfc_sw_dwn` | REAL | All-sky surface shortwave downward irradiance (kWh/m²/day) |
| `cloud_amt` | REAL | Cloud amount (%) |
| `surface_pressure` | REAL | Surface pressure (kPa) |

**PK**: `(province_id, year, month)`

#### `barangay_climate_monthly`

Same structure as `province_climate_monthly` but keyed on `barangay_id`.
Barangay climate data is typically inherited from the parent municipality
when direct barangay-level data is unavailable.

#### Suitability Tables

Four separate tables replace the suitability columns in `municipalities`:

| Table | PK | Key Columns |
|-------|----|-------------|
| `solar_suitability` | `(municipality_id)` | `score`, `classification`, `factors` |
| `wind_suitability` | `(municipality_id)` | `score`, `classification`, `factors` |
| `hydro_suitability` | `(municipality_id)` | `score`, `classification`, `factors` |
| `composite_suitability` | `(municipality_id)` | `score`, `classification`, `factors` |

### Views

- **`province_climate_annual`**: Aggregates monthly climate to annual averages per province.
- **`geographic_hierarchy_with_geo`**: Joins all admin levels with geospatial_metadata for a complete geographic lookup.

### Forecast Cache Extension

The `forecast_cache` table has been extended with:
- `geo_level` (TEXT): 'national', 'province', 'municipality', or 'barangay'
- `geo_id` (BIGINT): The ID for the given geographic level

## Data Sources

| Data | Source | Format |
|------|--------|--------|
| Admin boundaries | PSA / PhilAtlas | GeoJSON (frontend) |
| Centroids | Computed from GeoJSON via shapely | Supabase `geospatial_metadata` |
| Climate (municipality) | NASA POWER | CSV → `municipality_climate_monthly` |
| Climate (province) | Aggregated from municipality | `province_climate_monthly` |
| Climate (barangay) | Inherited from municipality | `barangay_climate_monthly` |
| Suitability scores | Computed by `municipality_suitability_builder.py` | Separate tables |

## Migration

The migration script is at `supabase/migrations/0001_geospatial_architecture.sql`.

It performs:
1. Creates new tables with constraints and indexes
2. Migrates existing suitability data from `municipalities` columns to separate tables
3. Adds `geo_level`/`geo_id` to `forecast_cache`
4. Creates views for annual climate and geographic hierarchy
5. Sets up RLS policies for all new tables

**Note**: Deprecated columns in `municipalities` are NOT dropped in this migration.
They will be removed in a future cleanup migration after all services have been
updated to use the new separate tables.
