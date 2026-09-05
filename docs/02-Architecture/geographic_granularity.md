# Geographic Granularity Logic

## Resolution Hierarchy

LUMI supports four geographic resolution levels:

```
National → Province → Municipality → Barangay
```

Each level has different data availability and use cases.

## Data Availability Matrix

| Data Type | National | Province | Municipality | Barangay |
|-----------|----------|----------|--------------|----------|
| Energy statistics (DOE) | ✅ | ✅ (Annex 8) | ❌ | ❌ |
| ML forecasts (ARIMA) | ✅ | ❌ | ❌ | ❌ |
| Climate (NASA POWER) | ❌ | ✅ (aggregated) | ✅ | ✅ (inherited) |
| Solar suitability | ❌ | ✅ (aggregated) | ✅ | ✅ (inherited) |
| Wind suitability | ❌ | ✅ (aggregated) | ✅ | ✅ (inherited) |
| Hydro suitability | ❌ | ✅ (aggregated) | ✅ | ✅ (inherited) |
| Geothermal suitability | ❌ | ✅ (aggregated) | ✅ | ✅ (inherited) |
| Centroids | ❌ | ✅ | ✅ | ✅ (from admin table) |
| Population | ❌ | ✅ | ✅ | ❌ |
| Boundaries (GeoJSON) | ✅ (regions) | ✅ | ✅ | ❌ |

## Fallback Strategy

When data at a requested level is unavailable, the system falls back to
the next coarser level automatically.

### Climate Fallback

Implemented in `app/services/climate_service.py`:

```python
get_climate_with_fallback(
    barangay_id=123,
    municipality_id=456,
    province_id=78,
    year=2024
)
```

**Resolution chain:**
1. Try `barangay_climate_monthly` for `barangay_id=123`
2. If empty, try `municipality_climate_monthly` for `municipality_id=456`
3. If empty, try `province_climate_monthly` for `province_id=78`
4. If empty, aggregate from all municipalities in the province

**Returns**: `(actual_level, actual_geo_id, records)`

### Suitability Fallback

Barangays inherit suitability scores from their parent municipality.

- No separate barangay suitability computation is performed
- The barangay map endpoint joins `barangays` → `municipalities` to get scores
- This is appropriate because suitability factors (irradiance, wind speed, terrain)
  do not vary significantly within a single municipality

### Centroid Fallback

Implemented in `app/services/geospatial_service.py`:

```python
get_centroid_with_fallback("municipality", 456)
```

1. Try `geospatial_metadata` table for computed centroid
2. If not found, fall back to `lat`/`lon` columns in the admin table
3. If neither available, return `None`

## API Level Selection

### EnergyHub Map Data

```
GET /api/v1/energyhub/map-data?metric=solar_potential&level=barangay
```

| Level | Data Source | Performance |
|-------|------------|-------------|
| `province` | Aggregated from municipality climate/suitability | Fast (~88 items) |
| `municipality` | Pre-computed suitability scores from DB | Medium (~1,618 items) |
| `barangay` | Inherits parent municipality scores | Slow (~42,000 items) |

**Note**: Barangay-level map data is cached in Redis with key pattern
`lumi:suitability:{metric}:barangay` and 1-hour TTL.

### EcoSim Simulation

```
POST /api/v1/ecosim/  (mode: "municipality" | "province" | "barangay")
```

- **municipality mode**: Uses municipality climate data directly
- **province mode**: Aggregates all municipality data in the province
- **barangay mode**: Falls back to parent municipality climate data

### Geospatial Centroids

```
GET /api/v1/geospatial/centroids?level=province
GET /api/v1/geospatial/centroids/municipality/456
```

### Climate Data

```
GET /api/v1/geospatial/climate?level=municipality&geo_id=456&year=2024
GET /api/v1/geospatial/climate/hierarchy?barangay_id=123&municipality_id=456&province_id=78
```

## Redis Cache Key Patterns

| Data | Key Pattern | TTL |
|------|------------|-----|
| Suitability (municipality) | `lumi:suitability:{metric}:municipality` | 1 hour |
| Suitability (barangay) | `lumi:suitability:{metric}:barangay` | 1 hour |
| Climate | `lumi:climate:{level}:{geo_id}:{year}` | 24 hours |
| Centroids | `lumi:centroids:{level}` | 24 hours |
| EcoSim results | `lumi:ecosim:{level}:{geo_id}:{params_hash}` | 30 minutes |

### Cache Invalidation

- `invalidate_suitability_cache_sync()`: Clears all `lumi:suitability:*` keys
- `invalidate_climate_cache_sync(level, geo_id)`: Clears climate keys (scoped or all)
- `invalidate_all_geospatial_cache()`: Clears all geospatial-related keys

## ML Forecast Granularity

Current ML forecasts (ARIMA) operate at the **national level only**.

The `forecast_cache` table has been extended with `geo_level` and `geo_id`
columns to support future sub-national forecasting:

- `geo_level = 'national'`, `geo_id = NULL`: Current behavior (default)
- `geo_level = 'province'`, `geo_id = 78`: Future province-level forecast
- `geo_level = 'municipality'`, `geo_id = 456`: Future municipality-level forecast

**No changes to ML model code are needed** — the schema extension is
forward-compatible. When sub-national models are trained, the forecast
service can store and retrieve forecasts at any geographic level.
