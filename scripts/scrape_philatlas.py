"""Scrape PhilAtlas to build a complete geographic hierarchy
(regions -> provinces -> municipalities -> barangays),
compare with Supabase DB, and output CSVs of missing entries.

Usage:
    py scripts/scrape_philatlas.py

Outputs to scripts/gap_output/:
    - missing_regions.csv
    - missing_provinces.csv
    - missing_municipalities.csv
    - missing_barangays.csv
    - scrape_summary.csv
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "scripts" / "gap_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GEOJSON_REGION_PATH = REPO_ROOT / "react-frontend" / "public" / "philippine_geojson_file_per_region.json"
GEOJSON_MUNI_PATH = REPO_ROOT / "react-frontend" / "public" / "philippine_geojson_file_per_provinces.json"

PHILATLAS_BASE = "https://www.philatlas.com"
INDEX_URL = f"{PHILATLAS_BASE}/barangays.html"

# Static mapping of region PSGC -> region name (GeoJSON has no adm1_en)
REGION_PSGC_TO_NAME: dict[int, str] = {
    100000000: "Region I (Ilocos Region)",
    200000000: "Region II (Cagayan Valley)",
    300000000: "Region III (Central Luzon)",
    400000000: "Region IV-A (CALABARZON)",
    500000000: "Region V (Bicol Region)",
    600000000: "Region VI (Western Visayas)",
    700000000: "Region VII (Central Visayas)",
    800000000: "Region VIII (Eastern Visayas)",
    900000000: "Region IX (Zamboanga Peninsula)",
    1000000000: "Region X (Northern Mindanao)",
    1100000000: "Region XI (Davao Region)",
    1200000000: "Region XII (SOCCSKSARGEN)",
    1300000000: "National Capital Region (NCR)",
    1400000000: "Cordillera Administrative Region (CAR)",
    1600000000: "Region XIII (Caraga)",
    1700000000: "Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)",
    1900000000: "Region IV-B (MIMAROPA)",
}

# Province name normalization for matching
def norm_name(name: str) -> str:
    if not name:
        return ""
    n = name.strip().lower()
    # Strip parenthetical names: "davao de oro (compostela valley)" -> "davao de oro"
    n = re.sub(r'\s*\([^)]*\)\s*', ' ', n).strip()
    for prefix in ("province of ", "city of ", "municipality of "):
        if n.startswith(prefix):
            n = n[len(prefix):]
    # Strip common suffixes
    for suffix in (" city", " municipality"):
        if n.endswith(suffix):
            n = n[: -len(suffix)]
    # Common aliases
    aliases = {
        "compostela valley": "davao de oro",
        "maguindanao": "maguindanao del norte",
        "western samar": "samar",
        "samar (western samar)": "samar",
        "north cotabato": "cotabato",
        "cotabato (north cot.)": "cotabato",
        # NCR province in PhilAtlas maps to NCR 1st District in DB (handled in province matching)
        "region iv-b (mimaropa)": "mimaropa",
        "region iv-a (calabarzon)": "calabarzon",
        "cordillera administrative region": "car",
        "bangsamoro autonomous region in muslim mindanao": "barmm",
        "muñoz": "munoz",
        "science city of muñoz": "munoz",
        "pi v. corpuz": "pio v. corpuz",
        "gen. s.k. pendatun": "general salipada k. pendatun",
        # DB has "DAVAO (DAVAO DEL NORTE)" which strips to "davao"
        "davao": "davao del norte",
        # NCR province in PhilAtlas maps to NCR 1st District in DB
        # DB "NCR - 1st DISTRICT (MANILA)" normalizes to "ncr - 1st district"
        "national capital region": "ncr - 1st district",
    }
    return aliases.get(n, n)


# ---------------------------------------------------------------------------
# GeoJSON loaders
# ---------------------------------------------------------------------------

def load_geojson_province_map() -> dict[str, dict]:
    """Return {normalized_name: {psgc, region_psgc, name}} from per-region GeoJSON."""
    with open(GEOJSON_REGION_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        psgc = props.get("adm2_psgc")
        name = props.get("adm2_en", "")
        region_psgc = props.get("adm1_psgc")
        if psgc and name:
            result[norm_name(name)] = {
                "psgc": int(psgc),
                "region_psgc": int(region_psgc) if region_psgc else None,
                "name": name,
            }
    return result


def load_geojson_municipality_map() -> dict[int, list[dict]]:
    """Return {province_psgc: [{psgc, name, lat, lon}, ...]} from per-provinces GeoJSON."""
    with open(GEOJSON_MUNI_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    result: dict[int, list[dict]] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        muni_psgc = props.get("adm3_psgc")
        muni_name = props.get("adm3_en", "")
        prov_psgc = props.get("adm2_psgc")
        if muni_psgc and muni_name and prov_psgc:
            result.setdefault(int(prov_psgc), []).append({
                "psgc": int(muni_psgc),
                "name": muni_name,
            })
    return result


# ---------------------------------------------------------------------------
# PhilAtlas scraper
# ---------------------------------------------------------------------------

def fetch_page(client: httpx.Client, url: str) -> str:
    resp = client.get(url, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def parse_index_page(html: str) -> list[dict]:
    """Parse the barangays index page to extract province links.

    Returns list of {name, slug, url}.
    PhilAtlas uses single-quoted href attributes.
    """
    # Match: <a href='lists/barangays-SLUG.html' title='...'>NAME</a>
    pattern = re.compile(
        r"<a\s+href=['\"](?:/?)lists/barangays-([a-z0-9-]+)\.html['\"][^>]*>([^<]+)</a>",
        re.IGNORECASE,
    )
    results = []
    seen = set()
    for m in pattern.finditer(html):
        slug = m.group(1)
        name = m.group(2).strip()
        if slug not in seen:
            seen.add(slug)
            results.append({
                "name": name,
                "slug": slug,
                "url": f"{PHILATLAS_BASE}/lists/barangays-{slug}.html",
            })
    return results


def parse_province_page(html: str) -> list[dict]:
    """Parse a province barangays page to extract barangay entries.

    Each entry: {barangay_name, municipality_name, url}

    PhilAtlas uses single-quoted href attributes. Entries look like:
    <a href='luzon/car/abra/bangued/agtangao.html'>Agtangao</a>, Bangued
    """
    # Match: <a href='...'>BARANGAYNAME</a>, MUNINAME (single or double quotes)
    pattern = re.compile(
        r"<a\s+href=['\"]([^'\"]+)['\"][^>]*>([^<]+)</a>\s*,\s*([^\n<]+)",
        re.IGNORECASE,
    )
    results = []
    for m in pattern.finditer(html):
        url = m.group(1)
        barangay_name = m.group(2).strip()
        municipality_name = m.group(3).strip()
        # Skip non-geographic links (e.g., navigation links without path separators)
        if '/' not in url:
            continue
        # Clean up municipality name (remove trailing punctuation/whitespace)
        municipality_name = municipality_name.rstrip(".,;").strip()
        if not barangay_name or not municipality_name:
            continue
        results.append({
            "barangay_name": barangay_name,
            "municipality_name": municipality_name,
            "url": f"{PHILATLAS_BASE}/{url}" if not url.startswith("/") else f"{PHILATLAS_BASE}{url}",
        })
    return results


def scrape_philatlas() -> dict:
    """Scrape PhilAtlas and return structured geographic data.

    Returns:
        {
            "provinces": [{name, slug, url, region_slug, municipalities: [...]}],
            "regions": set of region slugs discovered,
        }
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }

    all_data = {
        "provinces": [],
        "regions_discovered": set(),
    }

    with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True) as client:
        # 1. Fetch index page
        print("Fetching index page...")
        index_html = fetch_page(client, INDEX_URL)
        province_links = parse_index_page(index_html)
        print(f"  Found {len(province_links)} province/special links")

        # 2. Fetch each province page
        for i, prov in enumerate(province_links):
            slug = prov["slug"]
            name = prov["name"]
            print(f"  [{i+1}/{len(province_links)}] {name}...", end="", flush=True)

            try:
                prov_html = fetch_page(client, prov["url"])
            except Exception as exc:
                print(f" FAILED: {exc}")
                continue

            entries = parse_province_page(prov_html)
            print(f" {len(entries)} barangays")

            # Extract region slug from barangay URLs
            # URL pattern: /{island}/{region}/{province}/{muni}/{barangay}.html
            region_slug = None
            for entry in entries:
                url_path = entry["url"]
                if PHILATLAS_BASE in url_path:
                    url_path = url_path[len(PHILATLAS_BASE):]
                parts = url_path.strip("/").split("/")
                if len(parts) >= 4:
                    region_slug = parts[1]
                    break

            if region_slug:
                all_data["regions_discovered"].add(region_slug)

            # Group barangays by municipality
            municipalities: dict[str, list[str]] = {}
            for entry in entries:
                muni_name = entry["municipality_name"]
                if muni_name not in municipalities:
                    municipalities[muni_name] = []
                municipalities[muni_name].append(entry["barangay_name"])

            all_data["provinces"].append({
                "name": name,
                "slug": slug,
                "url": prov["url"],
                "region_slug": region_slug,
                "municipalities": municipalities,
            })

            # Polite delay
            time.sleep(1)

    return all_data


# ---------------------------------------------------------------------------
# Supabase client
# ---------------------------------------------------------------------------

class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.http = httpx.Client(timeout=30.0)

    def get_all(self, table: str, select: str = "*") -> list[dict]:
        all_rows = []
        offset = 0
        batch = 1000
        while True:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {"select": select}
            headers = dict(self.headers)
            headers["Range"] = f"{offset}-{offset + batch - 1}"
            resp = self.http.get(url, params=params, headers=headers)
            resp.raise_for_status()
            rows = resp.json()
            if not rows:
                break
            all_rows.extend(rows)
            if len(rows) < batch:
                break
            offset += batch
        return all_rows


# ---------------------------------------------------------------------------
# Main comparison
# ---------------------------------------------------------------------------

def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)

    # --- Scrape PhilAtlas ---
    print("=" * 60)
    print("Scraping PhilAtlas...")
    print("=" * 60)
    scraped = scrape_philatlas()

    total_munis = sum(len(p["municipalities"]) for p in scraped["provinces"])
    total_barangays = sum(
        len(baries) for p in scraped["provinces"] for baries in p["municipalities"].values()
    )
    print(f"\nScrape complete:")
    print(f"  Provinces/special: {len(scraped['provinces'])}")
    print(f"  Municipalities:   {total_munis}")
    print(f"  Barangays:         {total_barangays}")
    print(f"  Region slugs:      {sorted(scraped['regions_discovered'])}")

    # --- Load GeoJSON mappings ---
    print("\nLoading GeoJSON mappings...")
    geo_provinces = load_geojson_province_map()
    geo_munis = load_geojson_municipality_map()
    print(f"  GeoJSON provinces: {len(geo_provinces)}")
    print(f"  GeoJSON municipalities: {sum(len(v) for v in geo_munis.values())}")

    # --- Build scraped hierarchy with PSGC codes ---
    print("\nBuilding hierarchy with PSGC codes...")

    # Regions: map from province PSGC -> region PSGC
    scraped_regions: dict[int, str] = {}  # region_psgc -> name
    scraped_provinces: list[dict] = []     # {psgc, region_psgc, name}
    scraped_municipalities: list[dict] = []  # {psgc, province_psgc, name}
    scraped_barangays: list[dict] = []    # {barangay_id, municipality_psgc, name}

    unmatched_provinces: list[str] = []
    unmatched_munis: list[dict] = []

    for prov in scraped["provinces"]:
        prov_name = prov["name"]
        prov_key = norm_name(prov_name)

        # Match province to GeoJSON
        geo_match = geo_provinces.get(prov_key)
        if not geo_match:
            # Try without NCR/HUC special names
            if prov_name in ("National Capital Region (NCR)",
                             "Highly urbanized cities outside NCR, and Cotabato City"):
                # These are special groupings, not provinces
                # Assign a synthetic PSGC
                if "ncr" in prov_name.lower():
                    prov_psgc = 1300000000
                    region_psgc = 1300000000
                else:
                    # HUCs - assign to their respective provinces later
                    prov_psgc = None
                    region_psgc = None
            else:
                unmatched_provinces.append(prov_name)
                continue
        else:
            prov_psgc = geo_match["psgc"]
            region_psgc = geo_match["region_psgc"]

        if prov_psgc and region_psgc:
            # Add region
            region_name = REGION_PSGC_TO_NAME.get(region_psgc, f"Region {region_psgc}")
            scraped_regions[region_psgc] = region_name

            # Add province
            scraped_provinces.append({
                "province_id": prov_psgc,
                "region_id": region_psgc,
                "name": prov_name,
            })

        # Process municipalities
        for muni_name, barangay_list in prov["municipalities"].items():
            muni_key = norm_name(muni_name)

            # Match municipality to GeoJSON
            muni_psgc = None
            if prov_psgc and prov_psgc in geo_munis:
                for gm in geo_munis[prov_psgc]:
                    if norm_name(gm["name"]) == muni_key:
                        muni_psgc = gm["psgc"]
                        break

            if not muni_psgc and prov_psgc:
                # Try matching across all provinces (for HUCs)
                for gp_psgc, gm_list in geo_munis.items():
                    for gm in gm_list:
                        if norm_name(gm["name"]) == muni_key:
                            muni_psgc = gm["psgc"]
                            # Use this province's PSGC
                            if not prov_psgc:
                                prov_psgc = gp_psgc
                                region_psgc = geo_provinces.get(
                                    norm_name(prov_name), {}
                                ).get("region_psgc")
                                if not region_psgc:
                                    # Find region from geo_provinces by province psgc
                                    for gp_name, gp_info in geo_provinces.items():
                                        if gp_info["psgc"] == gp_psgc:
                                            region_psgc = gp_info["region_psgc"]
                                            break
                            break
                    if muni_psgc:
                        break

            if not muni_psgc:
                unmatched_munis.append({
                    "name": muni_name,
                    "province": prov_name,
                })
                # Still add with a generated ID
                # Use province_psgc * 1000 + sequential
                if prov_psgc:
                    existing_count = len([
                        m for m in scraped_municipalities
                        if m.get("province_psgc") == prov_psgc
                    ])
                    muni_psgc = prov_psgc * 1000 + existing_count + 1
                else:
                    muni_psgc = 99000000000 + len(scraped_municipalities) + 1

            scraped_municipalities.append({
                "municipality_id": muni_psgc,
                "province_id": prov_psgc or 0,
                "name": muni_name,
            })

            # Add barangays
            for idx, barangay_name in enumerate(barangay_list, 1):
                # Generate barangay ID: municipality_psgc * 100 + sequential
                barangay_id = muni_psgc * 100 + idx
                scraped_barangays.append({
                    "barangay_id": barangay_id,
                    "municipality_id": muni_psgc,
                    "name": barangay_name,
                })

    print(f"  Regions: {len(scraped_regions)}")
    print(f"  Provinces: {len(scraped_provinces)}")
    print(f"  Municipalities: {len(scraped_municipalities)}")
    print(f"  Barangays: {len(scraped_barangays)}")
    if unmatched_provinces:
        print(f"  Unmatched provinces: {len(unmatched_provinces)}")
        for p in unmatched_provinces:
            print(f"    - {p}")
    if unmatched_munis:
        print(f"  Unmatched municipalities: {len(unmatched_munis)}")
        for m in unmatched_munis[:20]:
            print(f"    - {m['name']} ({m['province']})")
        if len(unmatched_munis) > 20:
            print(f"    ... and {len(unmatched_munis) - 20} more")

    # --- Fetch DB state ---
    print("\nFetching DB state from Supabase...")
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

    client = SupabaseRestClient(url, key)

    try:
        db_regions = client.get_all("regions", "region_id,name")
        print(f"  DB regions: {len(db_regions)}")
    except Exception as exc:
        print(f"  WARNING: Could not fetch regions: {exc}")
        db_regions = []

    try:
        db_provinces = client.get_all("provinces", "province_id,name,region_id")
        print(f"  DB provinces: {len(db_provinces)}")
    except Exception as exc:
        print(f"  WARNING: Could not fetch provinces: {exc}")
        db_provinces = []

    try:
        db_munis = client.get_all("municipalities", "municipality_id,name,province_id")
        print(f"  DB municipalities: {len(db_munis)}")
    except Exception as exc:
        print(f"  WARNING: Could not fetch municipalities: {exc}")
        db_munis = []

    try:
        db_barangays = client.get_all("barangays", "barangay_id,name,municipality_id")
        print(f"  DB barangays: {len(db_barangays)}")
    except Exception as exc:
        print(f"  WARNING: Could not fetch barangays: {exc}")
        db_barangays = []

    # --- Compare by normalized name (DB uses sequential IDs, not PSGC) ---
    print("\nComparing scraped vs DB (by normalized name)...")

    # Build DB lookup by normalized name
    db_region_by_name = {norm_name(r["name"]): r for r in db_regions}
    db_province_by_name = {norm_name(p["name"]): p for p in db_provinces}
    db_muni_by_name: dict[str, dict] = {}
    for m in db_munis:
        key_m = norm_name(m["name"])
        if key_m not in db_muni_by_name:
            db_muni_by_name[key_m] = m
    db_barangay_by_key: set[str] = set()
    for b in db_barangays:
        bkey = f"{norm_name(b['name'])}|{b['municipality_id']}"
        db_barangay_by_key.add(bkey)

    # Compute max IDs for new entries
    max_region_id = max((r["region_id"] for r in db_regions), default=0)
    max_province_id = max((p["province_id"] for p in db_provinces), default=0)
    max_muni_id = max((m["municipality_id"] for m in db_munis), default=0)
    max_barangay_id = max((b["barangay_id"] for b in db_barangays), default=0)

    # --- Find missing regions ---
    missing_regions: list[dict] = []
    region_id_map: dict[int, int] = {}  # scraped region_psgc -> DB region_id (existing or new)
    next_region_id = max_region_id + 1

    for psgc, name in scraped_regions.items():
        region_norm = norm_name(name)
        db_match = db_region_by_name.get(region_norm)
        # Special case: scraped "National Capital Region" -> DB "NCR"
        if not db_match and region_norm == "national capital region":
            db_match = db_region_by_name.get("ncr")
        if db_match:
            region_id_map[psgc] = db_match["region_id"]
        else:
            missing_regions.append({"region_id": next_region_id, "name": name})
            region_id_map[psgc] = next_region_id
            next_region_id += 1

    # --- Find missing provinces ---
    missing_provinces: list[dict] = []
    province_id_map: dict[int, int] = {}  # scraped province_psgc -> DB province_id
    next_province_id = max_province_id + 1

    for p in scraped_provinces:
        prov_norm = norm_name(p["name"])
        db_match = db_province_by_name.get(prov_norm)
        # Special case: PhilAtlas "National Capital Region (NCR)" -> DB "NCR - 1st DISTRICT (MANILA)"
        if not db_match and prov_norm == "national capital region":
            db_match = db_province_by_name.get("ncr - 1st district")
        if db_match:
            province_id_map[p["province_id"]] = db_match["province_id"]
        else:
            region_id = region_id_map.get(p["region_id"], p["region_id"])
            missing_provinces.append({
                "province_id": next_province_id,
                "region_id": region_id,
                "name": p["name"],
            })
            province_id_map[p["province_id"]] = next_province_id
            next_province_id += 1

    # --- Find missing municipalities ---
    missing_munis: list[dict] = []
    muni_id_map: dict[int, int] = {}  # scraped muni_psgc -> DB municipality_id
    next_muni_id = max_muni_id + 1

    for m in scraped_municipalities:
        db_match = db_muni_by_name.get(norm_name(m["name"]))
        if db_match:
            muni_id_map[m["municipality_id"]] = db_match["municipality_id"]
        else:
            province_id = province_id_map.get(m["province_id"], m["province_id"])
            missing_munis.append({
                "municipality_id": next_muni_id,
                "province_id": province_id,
                "name": m["name"],
            })
            muni_id_map[m["municipality_id"]] = next_muni_id
            next_muni_id += 1

    # --- Find missing barangays ---
    missing_barangays: list[dict] = []
    next_barangay_id = max_barangay_id + 1

    for b in scraped_barangays:
        muni_id = muni_id_map.get(b["municipality_id"])
        if not muni_id:
            continue
        bkey = f"{norm_name(b['name'])}|{muni_id}"
        if bkey in db_barangay_by_key:
            continue
        missing_barangays.append({
            "barangay_id": next_barangay_id,
            "municipality_id": muni_id,
            "name": b["name"],
        })
        next_barangay_id += 1

    # --- Write CSVs ---
    def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(OUTPUT_DIR / "missing_regions.csv", missing_regions, ["region_id", "name"])
    write_csv(OUTPUT_DIR / "missing_provinces.csv", missing_provinces, ["province_id", "region_id", "name"])
    write_csv(OUTPUT_DIR / "missing_municipalities.csv", missing_munis, ["municipality_id", "province_id", "name"])
    write_csv(OUTPUT_DIR / "missing_barangays.csv", missing_barangays, ["barangay_id", "municipality_id", "name"])

    # Summary
    summary = [
        {"table": "regions", "scraped": len(scraped_regions), "db": len(db_regions), "missing": len(missing_regions)},
        {"table": "provinces", "scraped": len(scraped_provinces), "db": len(db_provinces), "missing": len(missing_provinces)},
        {"table": "municipalities", "scraped": len(scraped_municipalities), "db": len(db_munis), "missing": len(missing_munis)},
        {"table": "barangays", "scraped": len(scraped_barangays), "db": len(db_barangays), "missing": len(missing_barangays)},
    ]
    write_csv(OUTPUT_DIR / "scrape_summary.csv", summary, ["table", "scraped", "db", "missing"])

    print(f"\n{'='*60}")
    print(f"COMPARISON RESULTS")
    print(f"{'='*60}")
    for s in summary:
        print(f"  {s['table']:20s}  scraped={s['scraped']:6d}  db={s['db']:6d}  missing={s['missing']:6d}")
    print(f"\nCSVs written to: {OUTPUT_DIR}")
    print(f"\nTo insert missing entries, run:")
    print(f"  py scripts/insert_from_csvs.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
