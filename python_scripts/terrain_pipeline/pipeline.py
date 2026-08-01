from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from rasterstats import zonal_stats

from .config import PipelineConfig
from .export import write_csv, write_geojson, write_parquet
from .hydrology import generate_flow_products, generate_hillshade
from .io import load_polygons, resolve_supabase_config, load_municipalities, save_json
from .metrics import (
    NormalizationCaps,
    SuitabilityWeights,
    elevation_classification,
    gravity_flow_potential,
    hydro_suitability_score,
    runoff_potential,
    slope_classification,
    terrain_exposure_index,
    terrain_flatness,
)
from .raster_utils import (
    buffer_bounds,
    inspect_raster,
    mean_slope_degrees,
    open_raster,
    pixel_size_meters,
    point_to_raster_coords,
    read_window,
    sample_point,
    terrain_ruggedness_index,
)


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("terrain_pipeline")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def chunked(iterable: Iterable, size: int) -> Iterable[list]:
    batch: list = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def compute_metrics_for_row(row: dict, cfg: PipelineConfig, ctx) -> dict:
    lon = row.get("longitude")
    lat = row.get("latitude")
    if lon is None or lat is None or np.isnan(lon) or np.isnan(lat):
        row.update(
            {
                "elevation_m": np.nan,
                "mean_elevation_m": np.nan,
                "min_elevation_m": np.nan,
                "max_elevation_m": np.nan,
                "elevation_range_m": np.nan,
                "mean_slope_deg": np.nan,
                "hydraulic_head_m": np.nan,
                "terrain_ruggedness": np.nan,
                "watershed_gradient": np.nan,
                "hydro_suitability_score": np.nan,
                "estimated_hydropower_potential_kw": np.nan,
                "runoff_potential": np.nan,
                "gravity_flow_potential": np.nan,
                "terrain_flatness": np.nan,
                "slope_classification": "unknown",
                "elevation_classification": "unknown",
                "ridge_elevation": np.nan,
                "terrain_exposure_index": np.nan,
            }
        )
        return row

    elevation = sample_point(ctx, lon, lat)
    if elevation is None:
        elevation = np.nan
    raster_xy = point_to_raster_coords(lon, lat, ctx.crs)
    bounds = buffer_bounds(lon, lat, cfg.buffer_m, ctx.crs, raster_xy)
    window = read_window(ctx, bounds)

    zonal_mean = row.get("zonal_mean_elev")
    zonal_min = row.get("zonal_min_elev")
    zonal_max = row.get("zonal_max_elev")
    zonal_std = row.get("zonal_std_elev")

    if zonal_mean is not None and not np.isnan(zonal_mean):
        mean_elev = float(zonal_mean)
        min_elev = float(zonal_min) if zonal_min is not None else np.nan
        max_elev = float(zonal_max) if zonal_max is not None else np.nan
        std_elev = float(zonal_std) if zonal_std is not None else np.nan
    elif window.count() == 0:
        mean_elev = min_elev = max_elev = std_elev = np.nan
    else:
        mean_elev = float(window.mean())
        min_elev = float(window.min())
        max_elev = float(window.max())
        std_elev = float(window.std())

    elevation_range = max_elev - min_elev if not np.isnan(max_elev) else np.nan
    hydraulic_head = elevation_range

    pixel_sizes = pixel_size_meters(ctx, lat, lon)
    mean_slope = mean_slope_degrees(window, pixel_sizes)
    ruggedness = std_elev if not np.isnan(std_elev) else terrain_ruggedness_index(window)
    watershed_gradient = hydraulic_head / (cfg.buffer_m * 2.0) if cfg.buffer_m else np.nan

    caps = NormalizationCaps(
        head_m=cfg.normalize_max_head_m,
        slope_deg=cfg.normalize_max_slope_deg,
        ruggedness_m=cfg.normalize_max_ruggedness_m,
    )
    weights = SuitabilityWeights(
        head=cfg.suitability_weight_head,
        slope=cfg.suitability_weight_slope,
        ruggedness=cfg.suitability_weight_ruggedness,
    )

    runoff = runoff_potential(mean_slope, mean_elev, caps)
    gravity = gravity_flow_potential(hydraulic_head, mean_slope, caps)
    suitability = hydro_suitability_score(hydraulic_head, mean_slope, ruggedness, weights, caps)
    hydropower_kw = hydraulic_head * runoff * cfg.hydropower_scale_kw if not np.isnan(hydraulic_head) else np.nan

    slope_class = slope_classification(
        mean_slope,
        cfg.slope_flat_threshold_deg,
        cfg.slope_gentle_threshold_deg,
        cfg.slope_moderate_threshold_deg,
        cfg.slope_steep_threshold_deg,
    )
    elev_class = elevation_classification(
        mean_elev,
        cfg.elevation_low_m,
        cfg.elevation_mid_m,
        cfg.elevation_high_m,
    )

    row.update(
        {
            "elevation_m": elevation,
            "mean_elevation_m": mean_elev,
            "min_elevation_m": min_elev,
            "max_elevation_m": max_elev,
            "elevation_range_m": elevation_range,
            "mean_slope_deg": mean_slope,
            "hydraulic_head_m": hydraulic_head,
            "terrain_ruggedness": ruggedness,
            "watershed_gradient": watershed_gradient,
            "hydro_suitability_score": suitability,
            "estimated_hydropower_potential_kw": hydropower_kw,
            "runoff_potential": runoff,
            "gravity_flow_potential": gravity,
            "terrain_flatness": terrain_flatness(mean_slope, cfg.normalize_max_slope_deg),
            "slope_classification": slope_class,
            "elevation_classification": elev_class,
            "ridge_elevation": max_elev,
            "terrain_exposure_index": terrain_exposure_index(max_elev, mean_elev, ruggedness),
        }
    )
    return row


def run_pipeline(cfg: PipelineConfig) -> dict:
    logger = setup_logger()
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    raster_ctx = open_raster(str(cfg.raster_path))
    inspect_raster(raster_ctx, logger)

    supabase_cfg = None
    if cfg.use_supabase:
        supabase_cfg = resolve_supabase_config(cfg.raster_path.parents[1])
        if not supabase_cfg:
            logger.warning("Supabase credentials not found; using CSV coordinates only")

    muni_df = load_municipalities(cfg.municipalities_csv, cfg.provinces_csv, supabase_cfg, logger)
    muni_df = muni_df.dropna(subset=["latitude", "longitude"], how="any")

    geo = gpd.GeoDataFrame(
        muni_df,
        geometry=[Point(xy) for xy in zip(muni_df["longitude"], muni_df["latitude"])],
        crs="EPSG:4326",
    )

    if cfg.polygon_path:
        polygons = load_polygons(cfg.polygon_path, logger)
        if "municipality_id" not in polygons.columns:
            raise ValueError("Polygon data must include municipality_id")
        stats = zonal_stats(
            polygons,
            str(cfg.raster_path),
            stats=["mean", "min", "max", "std"],
            nodata=raster_ctx.nodata,
        )
        stats_df = polygons[["municipality_id"]].copy()
        stats_df["zonal_mean_elev"] = [item.get("mean") for item in stats]
        stats_df["zonal_min_elev"] = [item.get("min") for item in stats]
        stats_df["zonal_max_elev"] = [item.get("max") for item in stats]
        stats_df["zonal_std_elev"] = [item.get("std") for item in stats]
        geo = geo.merge(stats_df, on="municipality_id", how="left")

    results: list[dict] = []
    for batch in chunked(geo.to_dict(orient="records"), cfg.batch_size):
        for row in batch:
            results.append(compute_metrics_for_row(row, cfg, raster_ctx))

    metadata = {
        "raster_path": str(cfg.raster_path),
        "buffer_m": cfg.buffer_m,
        "count": len(results),
    }
    save_json(cfg.output_dir / "run_metadata.json", metadata)

    csv_rows = [
        {
            k: v
            for k, v in row.items()
            if k != "geometry" and not k.startswith("zonal_")
        }
        for row in results
    ]
    write_csv(cfg.output_dir / "municipality_terrain_metrics.csv", csv_rows)
    write_csv(cfg.output_dir / "hydropower_suitability.csv", csv_rows)
    write_csv(cfg.output_dir / "renewable_energy_geodata.csv", csv_rows)

    if cfg.write_geojson or cfg.write_parquet:
        output_gdf = gpd.GeoDataFrame(results, geometry="geometry", crs="EPSG:4326")
        if cfg.write_geojson:
            write_geojson(cfg.output_dir / "renewable_energy_geodata.geojson", output_gdf)
        if cfg.write_parquet:
            write_parquet(cfg.output_dir / "renewable_energy_geodata.parquet", output_gdf)

    if cfg.advanced_hydrology:
        hillshade_path = cfg.output_dir / "hillshade.tif"
        generate_hillshade(cfg.raster_path, hillshade_path, logger)
        generate_flow_products(cfg.raster_path, cfg.output_dir, logger)

    raster_ctx.dataset.close()
    logger.info("Pipeline complete. Outputs in %s", cfg.output_dir)
    return metadata
