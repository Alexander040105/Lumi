from __future__ import annotations

import argparse
from pathlib import Path

from terrain_pipeline.config import PipelineConfig, default_config
from terrain_pipeline.pipeline import run_pipeline


def build_config(args: argparse.Namespace, repo_root: Path) -> PipelineConfig:
    base = default_config(repo_root)
    return PipelineConfig(
        raster_path=Path(args.raster_path) if args.raster_path else base.raster_path,
        municipalities_csv=Path(args.municipalities_csv) if args.municipalities_csv else base.municipalities_csv,
        provinces_csv=Path(args.provinces_csv) if args.provinces_csv else base.provinces_csv,
        output_dir=Path(args.output_dir) if args.output_dir else base.output_dir,
        polygon_path=Path(args.polygon_path) if args.polygon_path else None,
        buffer_m=args.buffer_m,
        batch_size=args.batch_size,
        use_supabase=not args.no_supabase,
        advanced_hydrology=args.advanced_hydrology,
        write_geojson=args.write_geojson,
        write_parquet=args.write_parquet,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Lumi terrain and hydrology pipeline")
    parser.add_argument("--raster-path", default=None, help="Path to PHL_msk_alt.vrt")
    parser.add_argument("--municipalities-csv", default=None, help="Municipalities CSV path")
    parser.add_argument("--provinces-csv", default=None, help="Provinces CSV path")
    parser.add_argument("--polygon-path", default=None, help="Optional municipality polygons (GeoJSON/Shapefile)")
    parser.add_argument("--output-dir", default=None, help="Output directory for CSVs")
    parser.add_argument("--buffer-m", type=float, default=2000.0, help="Sampling buffer in meters")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for processing")
    parser.add_argument("--no-supabase", action="store_true", help="Disable Supabase coordinate enrichment")
    parser.add_argument("--advanced-hydrology", action="store_true", help="Enable hillshade/flow outputs")
    parser.add_argument("--write-geojson", action="store_true", help="Export GeoJSON output")
    parser.add_argument("--write-parquet", action="store_true", help="Export Parquet output")

    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    config = build_config(args, repo_root)
    run_pipeline(config)


if __name__ == "__main__":
    main()
