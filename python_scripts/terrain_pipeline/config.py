from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class PipelineConfig:
    raster_path: Path
    municipalities_csv: Path
    provinces_csv: Path
    output_dir: Path
    polygon_path: Optional[Path] = None
    buffer_m: float = 2000.0
    batch_size: int = 500
    use_supabase: bool = True
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    slope_sample_strategy: str = "gradient"
    advanced_hydrology: bool = False
    write_geojson: bool = False
    write_parquet: bool = False
    hydropower_scale_kw: float = 5.0
    slope_flat_threshold_deg: float = 3.0
    slope_gentle_threshold_deg: float = 8.0
    slope_moderate_threshold_deg: float = 15.0
    slope_steep_threshold_deg: float = 30.0
    elevation_low_m: float = 200.0
    elevation_mid_m: float = 1000.0
    elevation_high_m: float = 2000.0
    suitability_weight_head: float = 0.45
    suitability_weight_slope: float = 0.35
    suitability_weight_ruggedness: float = 0.20
    normalize_max_head_m: float = 300.0
    normalize_max_slope_deg: float = 40.0
    normalize_max_ruggedness_m: float = 150.0


def default_config(repo_root: Path) -> PipelineConfig:
    return PipelineConfig(
        raster_path=repo_root / "data" / "phl_msk_alt" / "PHL_msk_alt.vrt",
        municipalities_csv=repo_root / "data" / "regionalData" / "municipalities.csv",
        provinces_csv=repo_root / "data" / "regionalData" / "provinces.csv",
        output_dir=repo_root / "data" / "regionalData" / "output" / "terrain_metrics",
    )
