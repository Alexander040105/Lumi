"""
Solar Atlas Preprocessing
=========================
Reads Global Solar Atlas v2 GEOTIFF files and extracts solar
irradiance values at key Philippine locations.

Input files (from newDataset/Philippines_GISdata_*_GlobalSolarAtlas-v2_GEOTIFF/):
- GHI.tif   → Global Horizontal Irradiance (kWh/m²/day)
- DNI.tif   → Direct Normal Irradiance (kWh/m²/day)
- DIF.tif   → Diffuse Horizontal Irradiance (kWh/m²/day)
- PVOUT.tif → PV Power Output (kWh/kW/day)
- TEMP.tif  → Air Temperature (°C)

Output: solar_atlas_ph.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd

INPUT_DIR = (
    Path(__file__).resolve().parent
    / "newDataset"
    / "Philippines_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF"
    / "Philippines_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF"
)
OUTPUT_DIR = Path(__file__).resolve().parent / "data_v2_preprocessed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Key Philippine city/province coordinates for sampling
SAMPLING_POINTS = [
    {"name": "Manila", "lat": 14.5995, "lon": 120.9842},
    {"name": "Cebu", "lat": 10.3157, "lon": 123.8854},
    {"name": "Davao", "lat": 7.1907, "lon": 125.4553},
    {"name": "Baguio", "lat": 16.4023, "lon": 120.5960},
    {"name": "Iloilo", "lat": 10.7202, "lon": 122.5621},
    {"name": "Cagayan de Oro", "lat": 8.4542, "lon": 124.6319},
    {"name": "Legazpi", "lat": 13.1391, "lon": 123.7438},
    {"name": "Puerto Princesa", "lat": 9.9672, "lon": 118.7855},
    {"name": "Tacloban", "lat": 11.2543, "lon": 125.0018},
    {"name": "Zamboanga", "lat": 6.9214, "lon": 122.0790},
    {"name": "Laoag", "lat": 18.1960, "lon": 120.5927},
    {"name": "Batangas", "lat": 13.7565, "lon": 121.0583},
    {"name": "Lipa", "lat": 13.9414, "lon": 121.1648},
    {"name": "Lucena", "lat": 13.9304, "lon": 121.6170},
    {"name": "Olongapo", "lat": 14.8386, "lon": 120.2842},
]


def _read_raster_stats(tif_path: Path) -> dict:
    """Read overall statistics from a GEOTIFF."""
    try:
        import rasterio
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            # Mask nodata values
            nodata = src.nodata
            if nodata is not None:
                data = data[data != nodata]
            data = data[data > 0]  # filter out zero/negative
            return {
                "mean": float(np.mean(data)),
                "min": float(np.min(data)),
                "max": float(np.max(data)),
                "width": src.width,
                "height": src.height,
                "crs": str(src.crs),
            }
    except Exception as exc:
        return {"error": str(exc)}


def _sample_raster(tif_path: Path, lat: float, lon: float) -> float | None:
    """Sample a GEOTIFF at a given lat/lon."""
    try:
        import rasterio
        from rasterio.sample import sample_gen
        with rasterio.open(tif_path) as src:
            vals = list(sample_gen(src, [(lon, lat)]))
            val = vals[0][0]
            if val is not None and val > 0:
                return float(val)
    except Exception:
        pass
    return None


def main():
    print("Reading Solar Atlas GEOTIFFs...")

    # Extract overall statistics
    stats = {}
    for key, fname in [("ghi", "GHI.tif"), ("dni", "DNI.tif"), ("dif", "DIF.tif"), ("pvout", "PVOUT.tif"), ("temp", "TEMP.tif")]:
        path = INPUT_DIR / fname
        if path.exists():
            stats[key] = _read_raster_stats(path)
            print(f"  {fname}: mean={stats[key].get('mean', 'N/A'):.3f}, min={stats[key].get('min', 'N/A'):.3f}, max={stats[key].get('max', 'N/A'):.3f}")
        else:
            print(f"  WARNING: {fname} not found")

    # Sample at key locations
    print("\nSampling at key locations...")
    rows = []
    for pt in SAMPLING_POINTS:
        row = {"location": pt["name"], "lat": pt["lat"], "lon": pt["lon"]}
        for key, fname in [("ghi_kwh_m2_day", "GHI.tif"), ("dni_kwh_m2_day", "DNI.tif"), ("dif_kwh_m2_day", "DIF.tif"), ("pvout_kwh_kW_day", "PVOUT.tif"), ("temp_c", "TEMP.tif")]:
            path = INPUT_DIR / fname
            val = _sample_raster(path, pt["lat"], pt["lon"]) if path.exists() else None
            row[key] = round(val, 3) if val is not None else None
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "solar_atlas_ph.csv", index=False)
    print(f"  → {len(df)} locations written to {OUTPUT_DIR / 'solar_atlas_ph.csv'}")

    # Write a summary JSON with national averages
    summary = {
        "source": "Global Solar Atlas v2",
        "national_mean": {k: round(v.get("mean", 0), 3) for k, v in stats.items() if "mean" in v},
        "note": "Values are long-term annual averages. GHI/DNI/DIF in kWh/m²/day. PVOUT in kWh/kW/day. TEMP in °C.",
    }
    import json
    with open(OUTPUT_DIR / "solar_atlas_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  → Summary written to {OUTPUT_DIR / 'solar_atlas_summary.json'}")


if __name__ == "__main__":
    main()
