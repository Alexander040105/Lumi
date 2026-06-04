from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import rasterio
from pyproj import CRS, Geod, Transformer
from rasterio.windows import from_bounds


@dataclass(frozen=True)
class RasterContext:
    dataset: rasterio.io.DatasetReader
    crs: CRS
    nodata: Optional[float]
    transform: rasterio.Affine
    bounds: rasterio.coords.BoundingBox
    pixel_size_x: float
    pixel_size_y: float


def open_raster(path: str) -> RasterContext:
    dataset = rasterio.open(path)
    crs = CRS.from_wkt(dataset.crs.to_wkt())
    transform = dataset.transform
    pixel_size_x = abs(transform.a)
    pixel_size_y = abs(transform.e)
    return RasterContext(
        dataset=dataset,
        crs=crs,
        nodata=dataset.nodata,
        transform=transform,
        bounds=dataset.bounds,
        pixel_size_x=pixel_size_x,
        pixel_size_y=pixel_size_y,
    )


def inspect_raster(ctx: RasterContext, logger: logging.Logger) -> None:
    logger.info("Raster CRS: %s", ctx.crs.to_string())
    logger.info("Raster bounds: %s", ctx.bounds)
    logger.info("Raster resolution: %.6f x %.6f", ctx.pixel_size_x, ctx.pixel_size_y)
    logger.info("Raster nodata: %s", ctx.nodata)


def _meters_per_degree(lat: float, lon: float) -> Tuple[float, float]:
    geod = Geod(ellps="WGS84")
    _, _, dist_x = geod.inv(lon, lat, lon + 1.0, lat)
    _, _, dist_y = geod.inv(lon, lat, lon, lat + 1.0)
    return abs(dist_x), abs(dist_y)


def point_to_raster_coords(
    lon: float,
    lat: float,
    raster_crs: CRS,
) -> Tuple[float, float]:
    if raster_crs.is_geographic:
        return lon, lat
    transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
    return transformer.transform(lon, lat)


def buffer_bounds(
    lon: float,
    lat: float,
    buffer_m: float,
    raster_crs: CRS,
    raster_xy: Tuple[float, float],
) -> Tuple[float, float, float, float]:
    x, y = raster_xy
    if raster_crs.is_projected:
        return (x - buffer_m, y - buffer_m, x + buffer_m, y + buffer_m)
    meters_x, meters_y = _meters_per_degree(lat, lon)
    buffer_deg_x = buffer_m / meters_x if meters_x else 0.0
    buffer_deg_y = buffer_m / meters_y if meters_y else 0.0
    return (x - buffer_deg_x, y - buffer_deg_y, x + buffer_deg_x, y + buffer_deg_y)


def read_window(
    ctx: RasterContext,
    bounds: Tuple[float, float, float, float],
) -> np.ma.MaskedArray:
    window = from_bounds(*bounds, transform=ctx.transform)
    data = ctx.dataset.read(1, window=window, masked=True)
    return data


def sample_point(ctx: RasterContext, lon: float, lat: float) -> Optional[float]:
    if ctx.crs.is_geographic:
        coords = [(lon, lat)]
    else:
        transformer = Transformer.from_crs("EPSG:4326", ctx.crs, always_xy=True)
        coords = [transformer.transform(lon, lat)]
    values = list(ctx.dataset.sample(coords))
    if not values:
        return None
    value = values[0][0]
    if ctx.nodata is not None and value == ctx.nodata:
        return None
    return float(value)


def pixel_size_meters(ctx: RasterContext, lat: float, lon: float) -> Tuple[float, float]:
    if ctx.crs.is_projected:
        return ctx.pixel_size_x, ctx.pixel_size_y
    meters_x, meters_y = _meters_per_degree(lat, lon)
    return ctx.pixel_size_x * meters_x, ctx.pixel_size_y * meters_y


def mean_slope_degrees(data: np.ma.MaskedArray, pixel_size: Tuple[float, float]) -> float:
    if data.count() == 0:
        return float("nan")
    filled = data.filled(data.mean())
    dy, dx = np.gradient(filled, pixel_size[1], pixel_size[0])
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)
    if isinstance(data, np.ma.MaskedArray):
        slope_deg = np.ma.array(slope_deg, mask=data.mask)
    return float(np.ma.mean(slope_deg))


def terrain_ruggedness_index(data: np.ma.MaskedArray) -> float:
    if data.count() == 0:
        return float("nan")
    filled = data.filled(data.mean())
    center = filled[filled.shape[0] // 2, filled.shape[1] // 2]
    tri = np.mean(np.abs(filled - center))
    return float(tri)
