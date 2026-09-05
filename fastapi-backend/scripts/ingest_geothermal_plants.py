import json
import os
from pathlib import Path

import pandas as pd

def main():
    repo_root = Path(__file__).resolve().parents[2]
    xl = repo_root / "data" / "GeothermalDatasets" / "Geothermal-Power-Tracker-March-2026-Final.xlsx"
    df = pd.read_excel(xl, sheet_name="Data", header=0, skiprows=[1])
    ph = df[df["Country/Area"] == "Philippines"].copy()

    ph["Latitude"] = pd.to_numeric(ph["Latitude"], errors="coerce")
    ph["Longitude"] = pd.to_numeric(ph["Longitude"], errors="coerce")
    ph["Unit Capacity (MW)"] = pd.to_numeric(ph["Unit Capacity (MW)"], errors="coerce")

    clean = ph[ph["Latitude"].notna() & ph["Longitude"].notna()].copy()

    status_map = {
        "operating": "operating",
        "pre-construction": "pre-construction",
        "construction": "construction",
        "announced": "announced",
        "retired": "retired",
        "mothballed / idle": "mothballed",
        " mothballed / idle": "mothballed",
    }
    clean["status_norm"] = (
        clean["Status"]
        .astype(str)
        .str.lower()
        .str.strip()
        .map(status_map)
        .fillna("unknown")
    )

    plants = []
    for _, row in clean.iterrows():
        plants.append(
            {
                "project_name": str(row["Project Name"]) if pd.notna(row["Project Name"]) else None,
                "unit_name": str(row["Unit Name"]) if pd.notna(row["Unit Name"]) else None,
                "capacity_mw": float(row["Unit Capacity (MW)"]) if pd.notna(row["Unit Capacity (MW)"]) else None,
                "technology": str(row["Technology"]) if pd.notna(row["Technology"]) else None,
                "status": row["status_norm"],
                "raw_status": str(row["Status"]) if pd.notna(row["Status"]) else None,
                "latitude": float(row["Latitude"]),
                "longitude": float(row["Longitude"]),
                "province": str(row["State/Province"]) if pd.notna(row["State/Province"]) else None,
                "city": str(row["City"]) if pd.notna(row["City"]) else None,
                "start_year": int(row["Start Year"]) if pd.notna(row["Start Year"]) else None,
                "wiki_url": str(row["Wiki URL"]) if pd.notna(row["Wiki URL"]) else None,
            }
        )

    out_path = repo_root / "fastapi-backend" / "app" / "services" / "local_data" / "ph_geothermal_plants.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plants, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(plants)} plants to {out_path}")
    operating = sum(1 for p in plants if p["status"] == "operating")
    print(f"Operating: {operating}")
    from collections import Counter
    c = Counter(p["province"] for p in plants if p["province"])
    print("By province (top 5):")
    for prov, cnt in c.most_common(5):
        print(f"  {prov}: {cnt}")


if __name__ == "__main__":
    main()
