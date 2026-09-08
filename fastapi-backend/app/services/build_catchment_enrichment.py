"""One-time script: build municipality catchment enrichment data.

Spatially joins each Philippine municipality centroid to:
  1. Its containing (or nearest) river catchment from the Boothroyd et al.
     (2023) national-scale geodatabase (128 catchments, 91 morphometric
     characteristics).
  2. Its nearest order 1-2 stream segment (household-relevant headwater).

Outputs:
  - fastapi-backend/app/services/local_data/municipality_catchment_enrichment.csv
  - supabase/table_scripts/municipality_catchment_enrichment_schema.sql
  - supabase/migrations/0022_catchment_enrichment.sql

Data source (CC-BY 4.0):
  Boothroyd, R.J., Williams, R.D., Hoey, T.B., et al. (2023).
  National-scale geodatabase of catchment characteristics in the Philippines
  for river management applications. PLOS ONE, 18(3), e0281933.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9994713/

Usage:
  python fastapi-backend/app/services/build_catchment_enrichment.py
"""
from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
CATCHMENT_DIR = REPO_ROOT / "newCatchmentsData"
CATCHMENT_SHP = CATCHMENT_DIR / "Philippines_GIS_catchments_n128" / "Philippines_GIS_catchments_n128.shp"
STREAM_SHP = CATCHMENT_DIR / "Philippines_GIS_stream_network_n128" / "Philippines_GIS_stream_network_n128.shp"
TOPO_CSV = CATCHMENT_DIR / "Philippines_topographic_characterstics_n128" / "Philippines_topographic_characterstics_n128.csv"

LOCAL_DATA_DIR = Path(__file__).resolve().parent / "local_data"
MUNI_ATLAS_CSV = LOCAL_DATA_DIR / "municipality_atlas_averages.csv"
OUTPUT_CSV = LOCAL_DATA_DIR / "municipality_catchment_enrichment.csv"

SUPABASE_SCRIPTS_DIR = REPO_ROOT / "supabase" / "table_scripts"
MIGRATIONS_DIR = REPO_ROOT / "supabase" / "migrations"

# ---------------------------------------------------------------------------
# Modeling constants (must match settings.py defaults)
# ---------------------------------------------------------------------------
HOUSEHOLD_HYDRO_PENSTOCK_LENGTH_M = 100.0
HOUSEHOLD_HYDRO_CATCHMENT_FRACTION = 0.001
HOUSEHOLD_HYDRO_STREAM_MAX_DISTANCE_M = 10_000.0
HOUSEHOLD_HYDRO_STREAM_CLOSE_M = 2_000.0  # full feasibility within 2 km


def _safe_float(val, default=None):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


def load_catchments() -> gpd.GeoDataFrame:
    """Load catchment polygons and join topographic characteristics."""
    logger.info("Loading catchment shapefile ...")
    catchments = gpd.read_file(CATCHMENT_SHP)
    logger.info("  %d catchments, CRS=%s", len(catchments), catchments.crs)

    # Load topographic CSV (91 characteristics) and join by catchment name
    topo = pd.read_csv(TOPO_CSV)
    # Shapefile uses 'New_Name', CSV uses 'Catchment'
    topo = topo.rename(columns={"Catchment": "New_Name"})
    # Fix known name mismatches between shapefile and topo CSV
    topo["New_Name"] = topo["New_Name"].replace({"Labangan2": "Labangan"})
    catchments = catchments.merge(topo, on="New_Name", how="left", suffixes=("", "_topo"))
    logger.info("  Joined topographic CSV: %d columns", catchments.shape[1])
    return catchments


def load_streams() -> gpd.GeoDataFrame:
    """Load stream network and filter to household-relevant (order 1-2)."""
    logger.info("Loading stream network shapefile ...")
    streams = gpd.read_file(STREAM_SHP)
    logger.info("  %d total stream segments", len(streams))
    streams_low = streams[streams["streamord"] <= 2].copy()
    logger.info("  %d order 1-2 segments (household-relevant)", len(streams_low))
    return streams_low


def load_municipalities() -> gpd.GeoDataFrame:
    """Load municipality centroids from the atlas CSV."""
    logger.info("Loading municipality centroids ...")
    df = pd.read_csv(MUNI_ATLAS_CSV)
    df = df.dropna(subset=["centroid_lat", "centroid_lon"]).copy()
    df["municipality_id"] = df["municipality_id"].astype(int)
    df["province_id"] = df["province_id"].astype(int)
    geometry = [Point(xy) for xy in zip(df["centroid_lon"], df["centroid_lat"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    logger.info("  %d municipalities with centroids", len(gdf))
    return gdf


def spatial_join_catchments(
    muni_gdf: gpd.GeoDataFrame, catchments: gpd.GeoDataFrame
) -> pd.DataFrame:
    """Join each municipality to its containing (or nearest) catchment."""
    logger.info("Spatial join: municipalities -> catchments ...")
    muni_proj = muni_gdf.to_crs(catchments.crs)

    # Select only the columns we need from catchments to keep the join lean
    catch_cols = [
        "New_Name",
        "Catch_area",
        "Catch_slp",
        "Catch_rel",
        "Drainage_D",
        "Catch_hyp",
        "Mean_s_slp",
        # Topographic CSV columns (joined above)
        "Basin_drainage_density",
        "Catchment_hypsometric_integral",
        "Basin_ruggedness_number",
        "Basin_melton_ruggedness_number",
        "Stream_mean_slope_50m",
        "geometry",
    ]
    # Some columns may be missing if the topo join used different names
    available_cols = [c for c in catch_cols if c in catchments.columns]
    catchments_subset = catchments[available_cols].copy()

    # First pass: within join
    joined = gpd.sjoin(
        muni_proj[["municipality_id", "province_id", "geometry"]],
        catchments_subset,
        how="left",
        predicate="within",
    )
    joined = joined.drop(columns=["index_right"])

    # A centroid on a catchment boundary can match multiple catchments.
    # Keep only the first match per municipality_id.
    joined = joined.drop_duplicates(subset="municipality_id", keep="first")

    within_mask = joined["New_Name"].notna()
    n_within = int(within_mask.sum())
    logger.info("  Within catchment: %d (%.1f%%)", n_within, 100 * n_within / len(joined))

    # Second pass: nearest catchment for those not within
    uncovered = joined[~within_mask].copy()
    if len(uncovered) > 0:
        nearest = gpd.sjoin_nearest(
            uncovered[["municipality_id", "geometry"]],
            catchments_subset,
            how="left",
            distance_col="catchment_distance_m",
        )
        nearest = nearest.drop(columns=["index_right"])
        # Merge nearest results back
        for col in catchments_subset.columns:
            if col == "geometry":
                continue
            joined.loc[~within_mask, col] = nearest.set_index("municipality_id").reindex(
                uncovered["municipality_id"].values
            )[col].values
        joined.loc[~within_mask, "catchment_distance_m"] = nearest.set_index(
            "municipality_id"
        ).reindex(uncovered["municipality_id"].values)["catchment_distance_m"].values

    # Set match method
    joined["catchment_match_method"] = "within"
    joined.loc[~within_mask, "catchment_match_method"] = "nearest"
    joined.loc[within_mask, "catchment_distance_m"] = 0.0

    logger.info(
        "  Nearest fallback: %d (%.1f%%)",
        int((~within_mask).sum()),
        100 * (~within_mask).sum() / len(joined),
    )
    return pd.DataFrame(joined.drop(columns="geometry"))


def spatial_join_streams(
    muni_gdf: gpd.GeoDataFrame, streams_low: gpd.GeoDataFrame
) -> pd.DataFrame:
    """Find the nearest order 1-2 stream for each municipality."""
    logger.info("Spatial join: municipalities -> nearest stream ...")
    muni_proj = muni_gdf.to_crs(streams_low.crs)

    stream_cols = ["grad_m_m", "area_km2", "streamord", "elevation", "geometry"]
    streams_subset = streams_low[stream_cols].copy()

    nearest = gpd.sjoin_nearest(
        muni_proj[["municipality_id", "geometry"]],
        streams_subset,
        how="left",
        distance_col="distance_to_stream_m",
    )
    nearest = nearest.drop(columns=["index_right"])
    # A centroid equidistant from two streams can match both. Keep nearest.
    nearest = nearest.sort_values("distance_to_stream_m").drop_duplicates(
        subset="municipality_id", keep="first"
    )
    logger.info(
        "  Stream distance stats: min=%.0f m, median=%.0f m, max=%.0f m",
        nearest["distance_to_stream_m"].min(),
        nearest["distance_to_stream_m"].median(),
        nearest["distance_to_stream_m"].max(),
    )
    return pd.DataFrame(nearest.drop(columns="geometry"))


def compute_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Compute household-scale derived fields from the joined data."""
    logger.info("Computing derived fields ...")

    # Effective catchment area: household draws from a tiny fraction of the basin
    # Real catchments range 258-27,684 km². A household micro-hydro intake
    # captures runoff from a small sub-area. We scale the basin area by a
    # configurable fraction (default 0.001 = 0.1%) and cap at 1.0 km²
    # (the previous fixed default) to stay within physically realistic bounds
    # for a single household run-of-river scheme.
    df["effective_catchment_area_km2"] = (
        df["Catch_area"].fillna(0.0) * HOUSEHOLD_HYDRO_CATCHMENT_FRACTION
    ).clip(lower=0.0, upper=1.0)

    # Stream-derived head: gradient (m/m) × penstock length (m)
    # This gives the actual vertical drop available along the nearest stream
    # segment, scaled to a realistic household penstock run.
    df["stream_head_m"] = (
        df["grad_m_m"].fillna(0.0) * HOUSEHOLD_HYDRO_PENSTOCK_LENGTH_M
    )

    # Stream feasibility penalty: decays with distance from the household
    # to the nearest stream. Full feasibility (1.0) within 2 km, linear
    # decay to 0.1 at 10 km, floor of 0.1 beyond.
    dist = df["distance_to_stream_m"].fillna(HOUSEHOLD_HYDRO_STREAM_MAX_DISTANCE_M)
    penalty = pd.Series(1.0, index=df.index)
    far_mask = dist > HOUSEHOLD_HYDRO_STREAM_CLOSE_M
    penalty[far_mask] = 1.0 - (
        (dist[far_mask] - HOUSEHOLD_HYDRO_STREAM_CLOSE_M)
        / (HOUSEHOLD_HYDRO_STREAM_MAX_DISTANCE_M - HOUSEHOLD_HYDRO_STREAM_CLOSE_M)
    ) * 0.9
    too_far = dist >= HOUSEHOLD_HYDRO_STREAM_MAX_DISTANCE_M
    penalty[too_far] = 0.1
    df["stream_feasibility_penalty"] = penalty.clip(lower=0.1, upper=1.0)

    # Enriched runoff coefficient: refine the slope-based coefficient using
    # drainage density and hypsometric integral.
    # - Higher drainage density → more efficient runoff delivery → higher C
    # - Higher hypsometric integral (more area at high elevation) → flashier
    #   runoff → slightly higher C
    # Base values from slope (matching estimate_runoff_coefficient in
    # hydro_output_calc.py):
    #   <3°: 0.30, 3-10°: 0.45, 10-20°: 0.60, >20°: 0.75
    slope = df["Catch_slp"].fillna(10.0)
    base_c = pd.Series(0.45, index=df.index)
    base_c[slope < 3] = 0.30
    base_c[(slope >= 3) & (slope < 10)] = 0.45
    base_c[(slope >= 10) & (slope < 20)] = 0.60
    base_c[slope >= 20] = 0.75

    drainage_density = df["Basin_drainage_density"].fillna(0.85)
    hypsometric = df["Catchment_hypsometric_integral"].fillna(0.5)

    # Drainage density adjustment: 0.65-1.23 km/km² in this dataset
    # Normalize to 0.8-1.2 multiplier
    dd_norm = (drainage_density - 0.65) / (1.23 - 0.65)  # 0..1
    dd_mult = 0.8 + 0.4 * dd_norm.clip(0, 1)  # 0.8..1.2

    # Hypsometric integral adjustment: 0-1, typical 0.4-0.6
    # Higher HI → younger, flashier catchment → slightly higher C
    hi_mult = 0.9 + 0.2 * hypsometric.clip(0, 1)  # 0.9..1.1

    df["enriched_runoff_coefficient"] = (base_c * dd_mult * hi_mult).clip(0.2, 0.85)

    logger.info(
        "  effective_catchment_area: min=%.4f, median=%.4f, max=%.4f km²",
        df["effective_catchment_area_km2"].min(),
        df["effective_catchment_area_km2"].median(),
        df["effective_catchment_area_km2"].max(),
    )
    logger.info(
        "  stream_head: min=%.2f, median=%.2f, max=%.2f m",
        df["stream_head_m"].min(),
        df["stream_head_m"].median(),
        df["stream_head_m"].max(),
    )
    logger.info(
        "  feasibility_penalty: min=%.2f, median=%.2f, max=%.2f",
        df["stream_feasibility_penalty"].min(),
        df["stream_feasibility_penalty"].median(),
        df["stream_feasibility_penalty"].max(),
    )
    logger.info(
        "  enriched_runoff_coefficient: min=%.3f, median=%.3f, max=%.3f",
        df["enriched_runoff_coefficient"].min(),
        df["enriched_runoff_coefficient"].median(),
        df["enriched_runoff_coefficient"].max(),
    )
    return df


def build_output_csv(df: pd.DataFrame) -> None:
    """Write the final enrichment CSV with clean column names."""
    out = pd.DataFrame()
    out["municipality_id"] = df["municipality_id"].astype(int)
    out["province_id"] = df["province_id"].astype(int)
    out["catchment_name"] = df["New_Name"]
    out["catchment_match_method"] = df["catchment_match_method"]
    out["catchment_distance_m"] = df["catchment_distance_m"].round(1)

    # Catchment morphology
    out["catchment_area_km2"] = df["Catch_area"].round(3)
    out["catchment_mean_slope_deg"] = df["Catch_slp"].round(3)
    out["catchment_relief_m"] = df["Catch_rel"].round(1)
    out["catchment_drainage_density_km_km2"] = df["Basin_drainage_density"].round(3)
    out["catchment_hypsometric_integral"] = df["Catchment_hypsometric_integral"].round(4)
    out["catchment_ruggedness_number"] = df["Basin_ruggedness_number"].round(3)
    out["catchment_melton_ruggedness"] = df["Basin_melton_ruggedness_number"].round(3)
    out["catchment_mean_stream_slope_m_m"] = df["Stream_mean_slope_50m"].round(5)

    # Nearest stream
    out["nearest_stream_gradient_m_m"] = df["grad_m_m"].round(5)
    out["nearest_stream_upstream_area_km2"] = df["area_km2"].round(3)
    out["nearest_stream_order"] = df["streamord"].astype("Int64")
    out["nearest_stream_elevation_m"] = df["elevation"].round(1)
    out["distance_to_nearest_stream_m"] = df["distance_to_stream_m"].round(1)

    # Derived
    out["effective_catchment_area_km2"] = df["effective_catchment_area_km2"].round(4)
    out["stream_head_m"] = df["stream_head_m"].round(2)
    out["stream_feasibility_penalty"] = df["stream_feasibility_penalty"].round(3)
    out["enriched_runoff_coefficient"] = df["enriched_runoff_coefficient"].round(4)

    out.to_csv(OUTPUT_CSV, index=False)
    logger.info("Wrote %d rows to %s", len(out), OUTPUT_CSV)


def main() -> None:
    catchments = load_catchments()
    streams_low = load_streams()
    muni_gdf = load_municipalities()

    catchment_df = spatial_join_catchments(muni_gdf, catchments)
    stream_df = spatial_join_streams(muni_gdf, streams_low)

    # Merge catchment + stream joins on municipality_id
    merged = catchment_df.merge(
        stream_df, on="municipality_id", how="left", suffixes=("", "_stream")
    )

    # Compute derived fields
    merged = compute_derived_fields(merged)

    # Write output
    build_output_csv(merged)

    # Summary
    n = len(merged)
    n_within = int((merged["catchment_match_method"] == "within").sum())
    n_nearest = int((merged["catchment_match_method"] == "nearest").sum())
    n_with_stream = int(merged["grad_m_m"].notna().sum())
    logger.info("=" * 60)
    logger.info("ENRICHMENT COMPLETE")
    logger.info("  Total municipalities: %d", n)
    logger.info("  Within catchment: %d (%.1f%%)", n_within, 100 * n_within / n)
    logger.info("  Nearest fallback: %d (%.1f%%)", n_nearest, 100 * n_nearest / n)
    logger.info("  With stream data: %d (%.1f%%)", n_with_stream, 100 * n_with_stream / n)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
