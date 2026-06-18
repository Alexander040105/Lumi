"""Insert missing municipalities from GeoJSON into Supabase municipalities table."""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "scripts" / "gap_output" / "missing_from_db.csv"
PROVINCE_GEOJSON_PATH = REPO_ROOT / "react-frontend" / "public" / "philippine_geojson_file_per_region.json"


def load_province_name_by_psgc() -> dict[int, str]:
    import json
    with open(PROVINCE_GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        psgc = props.get("adm2_psgc")
        name = props.get("adm2_en")
        if psgc and name:
            mapping[int(psgc)] = name
    return mapping


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
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

    def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select_cols = columns
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

    def insert(self, rows: list[dict]) -> "SupabaseRestQuery":
        self._rows = rows
        return self

    def execute(self):
        if hasattr(self, "_rows"):
            # INSERT path
            url = f"{self._client.base_url}/rest/v1/{self._table}"
            response = self._client.http.post(url, json=self._rows, headers=self._client.headers)
            response.raise_for_status()
            return type("Response", (), {"data": response.json() if response.text else []})()

        # SELECT path
        params: dict[str, str] = {"select": self._select_cols}
        for column, op, value in self._filters:
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
        print("ERROR: Missing Supabase credentials", file=sys.stderr)
        return 1

    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found. Run identify_gaps.py first.", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)

    # Load province mapping
    province_psgc_to_name = load_province_name_by_psgc()
    print(f"Loaded {len(province_psgc_to_name)} provinces from GeoJSON")

    # Fetch DB provinces to map name -> province_id
    resp = client.table("provinces").select("province_id,name").execute()
    db_provinces = resp.data or []
    province_name_to_id = {}
    for p in db_provinces:
        name = p.get("name", "").strip().upper()
        province_name_to_id[name] = p["province_id"]
    print(f"Loaded {len(db_provinces)} provinces from DB")

    rows = []
    skipped = 0
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = row.get("geo_psgc")
            psgc = row.get("geo_province_psgc")
            if not mid:
                continue

            # Look up province name from PSGC, then map to DB province_id
            province_name = province_psgc_to_name.get(int(psgc)) if psgc else None
            province_id = province_name_to_id.get(province_name.upper()) if province_name else None

            if not province_id:
                print(f"  Warning: Cannot map province PSGC {psgc} for {row['geo_name']} — skipping")
                skipped += 1
                continue

            rows.append({
                "municipality_id": int(mid),
                "province_id": province_id,
                "name": row["geo_name"],
                "lat": float(row["lat"]) if row["lat"] else None,
                "lon": float(row["lon"]) if row["lon"] else None,
            })

    if not rows:
        print("No missing municipalities to insert.")
        return 0

    print(f"Inserting {len(rows)} missing municipalities...")
    batch_size = 100
    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        try:
            resp = client.table("municipalities").insert(batch).execute()
            inserted += len(batch)
            print(f"  Inserted batch {i//batch_size + 1}: {len(batch)} rows")
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            print(f"  Batch {i//batch_size + 1} failed (status={exc.response.status_code}): {body}")
        except Exception as exc:
            print(f"  Batch {i//batch_size + 1} failed: {exc}")

    print(f"Done. Total inserted: {inserted}, Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
