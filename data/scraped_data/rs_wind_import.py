"""Import RS Components Philippines wind turbine listings into the shared catalog format.

Reads data/scraped_data/input/RS-PH-wind-turbines.csv, writes
data/scraped_data/output/rs_wind_catalog.{csv,json}. Stdlib only, deterministic.
"""

import argparse
import csv
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent          # data/scraped_data
REPO_ROOT = SCRIPT_DIR.parent.parent                  # repo root
OUT_CSV = SCRIPT_DIR / "output" / "rs_wind_catalog.csv"
OUT_JSON = SCRIPT_DIR / "output" / "rs_wind_catalog.json"

COLUMNS = [
    "name", "price", "currency", "url", "source_category", "brand",
    "model_number", "short_description", "description", "specs_json",
    "image_url", "ratings", "reviews", "price_type",
]

MPH_TO_MPS = 0.44704


def parse_diameter_m(text):
    """'1.17m' -> 1.17; handles m/cm/mm."""
    m = re.match(r"([\d.]+)\s*(mm|cm|m)\b", text.strip(), re.I)
    if not m:
        return None
    value, unit = float(m.group(1)), m.group(2).lower()
    return value / 1000 if unit == "mm" else value / 100 if unit == "cm" else value


def parse_wind_mps(text):
    """'110mph' -> 49.17 m/s."""
    m = re.match(r"([\d.]+)\s*mph", text.strip(), re.I)
    return round(float(m.group(1)) * MPH_TO_MPS, 2) if m else None


def parse_price(text):
    """'PHP141,053.65' -> '141053.65'."""
    return re.sub(r"[^0-9.]", "", text)


def build_row(rec):
    details = rec["Product Details"].strip()
    diameter_m = parse_diameter_m(rec["Blade Diameter"])
    specs = {
        "rs_stock_no": rec["RS Stock No."].strip(),
        "mfr_part_no": rec["Mfr. Part No."].strip(),
        "product_type": rec["Product Type"].strip(),
        "voltage": rec["Voltage"].strip(),
        "blade_diameter": rec["Blade Diameter"].strip(),
        "blade_diameter_m": diameter_m,
        "rotor_radius_m": round(diameter_m / 2, 3) if diameter_m else None,
        "max_wind_speed": rec["Maximum Wind Speed"].strip(),
        "max_wind_speed_mps": parse_wind_mps(rec["Maximum Wind Speed"]),
        "weight": rec["Weight"].strip(),
        "standards": rec["Standards/Approvals"].strip(),
        "pack_size": rec["Pack Size"].strip(),
    }
    short = details[:120]
    return {
        "name": details,
        "price": parse_price(rec["Price"]),
        "currency": "PHP",
        "url": rec["URL"].strip(),
        "source_category": "Wind Turbines",
        "brand": rec["Brand"].strip(),
        "model_number": rec["Model Number"].strip(),
        "short_description": short,
        "description": short + " — RS Components Philippines",
        "specs_json": json.dumps(specs),
        "image_url": "",
        "ratings": "",
        "reviews": "",
        "price_type": "fixed",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/scraped_data/input/RS-PH-wind-turbines.csv")
    args = ap.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = REPO_ROOT / input_path

    with open(input_path, newline="", encoding="utf-8-sig") as f:  # input has a BOM
        rows = [build_row(rec) for rec in csv.DictReader(f)]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    # Self-check
    assert len(rows) == 2, f"expected 2 rows, got {len(rows)}"
    assert all(r["price"] for r in rows), "a row is missing a price"
    for r in rows:
        specs = json.loads(r["specs_json"])
        assert specs["rotor_radius_m"] == 0.585, specs["rotor_radius_m"]
        print(json.dumps(specs, indent=2))

    print(f"Wrote {len(rows)} rows -> {OUT_CSV} and {OUT_JSON}")


if __name__ == "__main__":
    main()
