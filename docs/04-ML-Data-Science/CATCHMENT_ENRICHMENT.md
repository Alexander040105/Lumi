# Catchment Enrichment for EcoSim Hydro Calculations

## Overview

EcoSim's household micro-hydro model has been enriched with real Philippine
catchment morphology and stream network data from the Boothroyd et al. (2023)
national-scale geodatabase. This replaces fixed assumptions (1.0 km² catchment,
0.001 m³/s flow floor, DEM-derived head) with per-municipality spatial data,
producing differentiated hydro outputs that reflect actual terrain.

## Data Source

**Boothroyd, R.J., Williams, R.D., Hoey, T.B., et al. (2023).**
*National-scale geodatabase of catchment characteristics in the Philippines
for river management applications.*
**PLOS ONE, 18(3), e0281933.**
https://pmc.ncbi.nlm.nih.gov/articles/PMC9994713/

**License:** CC-BY 4.0 (free for commercial and non-commercial use with
attribution)

**Data files** (in `newCatchmentsData/`):
- `Philippines_GIS_catchments_n128/` — 128 catchment polygons with 13
  attributes (area, slope, relief, drainage density, etc.)
- `Philippines_GIS_stream_network_n128/` — 107,613 stream segments with
  gradient, upstream area, stream order, elevation
- `Philippines_topographic_characterstics_n128/` — 91 morphometric
  characteristics per catchment (hypsometric integral, ruggedness number,
  bifurcation ratio, etc.)

## Methodology

### Spatial Join

Each municipality centroid (from `municipality_atlas_averages.csv`) is
spatially joined to:

1. **Containing catchment** (46.3% of municipalities) — the centroid falls
   inside a catchment polygon.
2. **Nearest catchment** (53.7%) — for municipalities outside all catchment
   polygons, the nearest catchment by distance is used as a fallback.
3. **Nearest order 1-2 stream** (100%) — the closest household-relevant
   headwater stream segment (Strahler order 1 or 2, 81,701 segments
   available).

### Derived Fields

| Field | Formula | Replaces |
|-------|---------|----------|
| `effective_catchment_area_km2` | `min(basin_area × 0.001, 1.0)` | Fixed 1.0 km² |
| `stream_head_m` | `stream_gradient × 100m penstock` | DEM-derived municipal head × 0.20 |
| `stream_feasibility_penalty` | `1.0` within 2km, decays to `0.1` at 10km+ | No penalty (gravity_flow_potential only) |
| `enriched_runoff_coefficient` | `base_C × drainage_density_mult × hypsometric_mult` | Slope-only runoff coefficient |

### What Changed in the Hydro Model

**Before (fixed assumptions):**
- Catchment area: always 1.0 km²
- Head: DEM elevation range × 0.20, floored at 2.0m, capped at 25m
- Flow floor: 0.001 m³/s (produced uniform 123.2 kWh ceiling in mountains)
- Runoff coefficient: based only on slope

**After (enrichment):**
- Catchment area: real basin area × 0.001 household fraction (0.26–1.0 km²)
- Head: actual stream gradient × 100m penstock (0–41.77m, no artificial floor)
- Flow floor: removed when enrichment is used (dry areas show 0 kWh)
- Runoff coefficient: refined by drainage density and hypsometric integral
- Feasibility penalty: reduces output for households far from streams

## Coverage

| Metric | Value |
|--------|-------|
| Total municipalities | 1,376 |
| Within catchment | 637 (46.3%) |
| Nearest fallback | 739 (53.7%) |
| With stream data | 1,376 (100%) |
| Stream head range | 0 – 41.77 m (median 1.36 m) |
| Feasibility penalty range | 0.1 – 1.0 (median 0.97) |
| Effective catchment area | 0.26 – 1.0 km² (median 0.91) |

## Files

| File | Purpose |
|------|---------|
| `fastapi-backend/app/services/build_catchment_enrichment.py` | One-time script to generate enrichment CSV |
| `fastapi-backend/app/services/local_data/municipality_catchment_enrichment.csv` | Bundled CSV fallback (1,376 rows) |
| `fastapi-backend/app/services/catchment_data.py` | Loader (Supabase + CSV fallback) |
| `supabase/migrations/0022_catchment_enrichment.sql` | Supabase table DDL + RLS |
| `supabase_tables_scripts/municipality_catchment_enrichment_schema.sql` | Standalone schema |
| `fastapi-backend/tests/test_catchment_enrichment.py` | Tests (20 tests) |

## Configuration

Settings in `fastapi-backend/app/config/settings.py`:

```python
catchment_enrichment_enabled: bool = True
household_hydro_penstock_length_m: float = 100.0
household_hydro_catchment_fraction: float = 0.001
household_hydro_stream_max_distance_m: float = 10000.0
catchment_enrichment_version: str = "v1"
```

## API Impact

The EcoSim API response now includes new fields in the `assumptions` block:

```json
{
  "assumptions": {
    "hydro_data_source": "Boothroyd et al. 2023 catchment geodatabase",
    "hydro_catchment_name": "Cagayan",
    "hydro_stream_feasibility": "high"
  }
}
```

`hydro_stream_feasibility` values: `"high"` (≤2km), `"moderate"` (≤5km),
`"low"` (≤10km), `"none"` (>10km), `"unknown"` (no enrichment data).

When enrichment is unavailable for a municipality, `hydro_data_source` is
`"default terrain data"` and the model falls back to the original
fixed-assumption behavior.

## Regenerating the Enrichment Data

If the source dataset is updated or the modeling constants change:

```bash
python fastapi-backend/app/services/build_catchment_enrichment.py
```

This regenerates `municipality_catchment_enrichment.csv`. Bump
`catchment_enrichment_version` in `settings.py` to invalidate cached
EcoSim responses.

## Panelist Defense

**Q: Why is hydro low when the Philippines has so much water?**

A: The Philippines has 13,097 MW of hydropower potential (DOE), but only
27 MW (0.2%) is household-scale micro-hydro. Our model now uses real
catchment data from a peer-reviewed national geodatabase (Boothroyd et al.
2023, PLOS ONE) showing that:

1. Most Philippine municipalities have very low stream gradients (median
   1.36 m head over a 100m penstock run) — insufficient for useful power.
2. Many households are far from the nearest stream (25% are >5km away),
   making penstock construction economically impractical.
3. The effective catchment area for a single household is tiny (0.26–1.0
   km²), limiting flow even in wet areas.

The low hydro values reflect actual terrain constraints, not model
artifacts. We use real Philippine catchment morphology from a
peer-reviewed source, and the results are consistent with the DOE's own
finding that micro-hydro potential is <0.2% of total hydro potential.

## Citation

```
Boothroyd, R.J., Williams, R.D., Hoey, T.B., MacDonell, C.,
Tolentino, P.L.M., Quick, L., Guardian, E.L., Reyes, J.C.M.,
Sabillo, C.J.S., Perez, J.E.G., & David, C.P.C. (2023).
National-scale geodatabase of catchment characteristics in the
Philippines for river management applications. PLOS ONE, 18(3),
e0281933. https://doi.org/10.1371/journal.pone.0281933
```
