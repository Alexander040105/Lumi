"""
Identify municipalities from the GeoJSON map that are missing from Supabase
or have NULL suitability scores. Outputs three CSVs:
- missing_from_db.csv     : GeoJSON municipalities not in DB at all
- null_scores.csv         : In DB but all 5 scores are NULL
- has_data.csv            : In DB with at least one score
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=30.0)

    def table(self, table_name: str):
        return SupabaseRestQuery(self, table_name)


class SupabaseRestQuery:
    def __init__(self, client: SupabaseRestClient, table: str):
        self._client = client
        self._table = table
        self._select_cols = "*"
        self._filters: list[tuple[str, str, str]] = []
        self._order: str | None = None
        self._range: tuple[int, int] | None = None
        self._not_null: list[str] = []

    def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select_cols = columns
        return self

    def not_(self) -> "SupabaseRestQuery":
        self._not = True
        return self

    def is_(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, "is", str(value)))
        return self

    def eq(self, column: str, value: str | int) -> "SupabaseRestQuery":
        self._filters.append((column, "eq", str(value)))
        return self

    def order(self, column: str, desc: bool = False) -> "SupabaseRestQuery":
        self._order = f"{column}.{'desc' if desc else 'asc'}"
        return self

    def range(self, start: int, end: int) -> "SupabaseRestQuery":
        self._range = (start, end)
        return self

    def execute(self):
        params: dict[str, str] = {"select": self._select_cols}
        for column, op, value in self._filters:
            if op == "is":
                params[column] = f"is.{value}"
            else:
                params[column] = f"{op}.{value}"
        if self._order:
            params["order"] = self._order
        url = f"{self._client.base_url}/rest/v1/{self._table}"
        headers = dict(self._client.headers)
        if self._range:
            headers["Range"] = f"{self._range[0]}-{self._range[1]}"
        response = self._client.http.get(url, params=params, headers=headers)
        response.raise_for_status()
        return type("Response", (), {"data": response.json()})()

REPO_ROOT = Path(__file__).resolve().parents[1]
GEOJSON_PATH = REPO_ROOT / "react-frontend" / "public" / "philippine_geojson_file_per_provinces.json"
OUTPUT_DIR = REPO_ROOT / "scripts" / "gap_output"


def compute_centroid(geometry: dict) -> tuple[float, float]:
    coords = geometry.get("coordinates", [])
    lats, lons = [], []

    def visit(c):
        if isinstance(c[0], list):
            for sub in c:
                visit(sub)
        else:
            lons.append(c[0])
            lats.append(c[1])

    visit(coords)
    if not lats:
        return 0.0, 0.0
    return sum(lats) / len(lats), sum(lons) / len(lons)


def load_geojson_municipalities() -> list[dict]:
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry")
        lat, lon = compute_centroid(geom) if geom else (0.0, 0.0)
        results.append({
            "geo_name": props.get("adm3_en", ""),
            "geo_province_psgc": props.get("adm2_psgc"),
            "geo_municipality_psgc": props.get("adm3_psgc"),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
        })
    return results


def fetch_all_municipalities_from_db(client) -> list[dict]:
    all_rows = []
    offset = 0
    batch = 1000
    while True:
        resp = (
            client.table("municipalities")
            .select(
                "municipality_id, province_id, name, lat, lon, "
                "solar_suitability_score, wind_suitability_score, "
                "hydro_suitability_score, geothermal_suitability_score, "
                "composite_suitability_score"
            )
            .range(offset, offset + batch - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch
    return all_rows


def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)
    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    geo_munis = load_geojson_municipalities()
    print(f"GeoJSON municipalities: {len(geo_munis)}")

    db_munis = fetch_all_municipalities_from_db(client)
    print(f"DB municipalities:      {len(db_munis)}")

    # Build lookup by municipality_id (PSGC)
    db_by_id = {row["municipality_id"]: row for row in db_munis}

    # Also build by normalized name for fuzzy matching
    def norm(name: str) -> str:
        import re as _re
        n = name.lower().strip()
        # Strip parenthetical aliases: "paranas (wright)" -> "paranas"
        n = _re.sub(r'\s*\([^)]*\)\s*', ' ', n).strip()
        for prefix in ("city of ", "municipality of ", "province of "):
            if n.startswith(prefix):
                n = n[len(prefix):]
        for suffix in (" city", " municipality"):
            if n.endswith(suffix):
                n = n[: -len(suffix)]
        # Common aliases
        aliases = {
            "gen. s.k. pendatun": "general salipada k. pendatun",
            "pi v. corpuz": "pio v. corpuz",
            "muñoz": "munoz",
            "science city of muñoz": "munoz",
        }
        return aliases.get(n, n)

    db_by_name = {norm(row["name"]): row for row in db_munis if row.get("name")}

    missing_from_db = []
    null_scores = []
    has_data = []

    for gm in geo_munis:
        psgc = gm["geo_municipality_psgc"]
        db_row = db_by_id.get(psgc)

        if not db_row:
            # Try fuzzy name match
            db_row = db_by_name.get(norm(gm["geo_name"]))

        if not db_row:
            missing_from_db.append({
                "geo_name": gm["geo_name"],
                "geo_psgc": psgc,
                "geo_province_psgc": gm["geo_province_psgc"],
                "lat": gm["lat"],
                "lon": gm["lon"],
            })
            continue

        scores = [
            db_row.get("solar_suitability_score"),
            db_row.get("wind_suitability_score"),
            db_row.get("hydro_suitability_score"),
            db_row.get("geothermal_suitability_score"),
            db_row.get("composite_suitability_score"),
        ]
        has_any_score = any(s is not None for s in scores)

        if has_any_score:
            has_data.append({
                "municipality_id": db_row["municipality_id"],
                "name": db_row.get("name"),
                "lat": db_row.get("lat"),
                "lon": db_row.get("lon"),
                "solar_score": db_row.get("solar_suitability_score"),
                "wind_score": db_row.get("wind_suitability_score"),
                "hydro_score": db_row.get("hydro_suitability_score"),
                "geo_score": db_row.get("geothermal_suitability_score"),
                "composite_score": db_row.get("composite_suitability_score"),
            })
        else:
            null_scores.append({
                "municipality_id": db_row["municipality_id"],
                "name": db_row.get("name"),
                "lat": db_row.get("lat"),
                "lon": db_row.get("lon"),
            })

    # Write CSVs
    def write_csv(path, rows, fieldnames):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(OUTPUT_DIR / "missing_from_db.csv", missing_from_db,
              ["geo_name", "geo_psgc", "geo_province_psgc", "lat", "lon"])
    write_csv(OUTPUT_DIR / "null_scores.csv", null_scores,
              ["municipality_id", "name", "lat", "lon"])
    write_csv(OUTPUT_DIR / "has_data.csv", has_data,
              ["municipality_id", "name", "lat", "lon",
               "solar_score", "wind_score", "hydro_score", "geo_score", "composite_score"])

    print(f"\n{'='*60}")
    print(f"Missing from DB:        {len(missing_from_db)}")
    print(f"In DB but NULL scores:  {len(null_scores)}")
    print(f"In DB with data:        {len(has_data)}")
    print(f"{'='*60}")
    print(f"Output written to: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
