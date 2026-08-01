"""Sync PSGC data from the authenticated PSA API to Supabase.

Fetches regions, provinces, municipalities, and barangays from
https://classification.psa.gov.ph/psgc/Q2_2024/{level}?token={PSGC_API_CODE}

Then:
  1. Matches API records to existing DB rows by normalized name within parent context
  2. Updates existing rows with psgc_code + all new PSGC attribute columns
  3. Inserts missing barangays and municipalities
  4. Populates municipal_population table
  5. Populates population_data table for historical tracking

Usage:
    py scripts/sync_psgc_data.py
    py scripts/sync_psgc_data.py --skip-fetch   # use cached JSON
    py scripts/sync_psgc_data.py --level barangays  # sync only one level
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = REPO_ROOT / "scripts" / "psgc_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PSGC_BASE = "https://classification.psa.gov.ph/psgc"
PSGC_VERSION = "Q2_2024"
PAGE_SIZE = 100
API_DELAY = 0.1  # seconds between API requests

LEVELS = ["regions", "provinces", "municipalities", "barangays"]

# ---------------------------------------------------------------------------
# Name normalization
# ---------------------------------------------------------------------------

_CITY_PREFIX = re.compile(r"^city of\s+", re.IGNORECASE)
_PARENTHETICAL = re.compile(r"\s*\([^)]*\)\s*", re.IGNORECASE)
_MULTI_SPACE = re.compile(r"\s+")
_SPECIAL_CHARS = re.compile(r"[^a-z0-9\s]")
_MUNI_SUFFIXES = re.compile(
    r"\s+(municipality|municipio|town|capital|poblacion)$", re.IGNORECASE
)


def normalize_name(name: str) -> str:
    """Normalize a geographic name for matching."""
    if not name:
        return ""
    s = name.strip().lower()
    s = _CITY_PREFIX.sub("", s)
    s = _PARENTHETICAL.sub(" ", s)
    s = _MUNI_SUFFIXES.sub("", s)
    s = _SPECIAL_CHARS.sub("", s)
    s = _MULTI_SPACE.sub(" ", s).strip()
    return s


_PAREN_EXTRACT = re.compile(r"\(([^)]+)\)")


def extract_parenthetical(name: str) -> str:
    """Extract the text inside the first pair of parentheses, normalized."""
    if not name:
        return ""
    m = _PAREN_EXTRACT.search(name)
    if m:
        return normalize_name(m.group(1))
    return ""


def normalize_with_old_name(name: str, old_name: str = "") -> list[str]:
    """Return all possible normalized forms of a name for matching.

    Includes the primary normalized name, the parenthetical content,
    and the old_name field if provided.
    """
    results = [normalize_name(name)]
    paren = extract_parenthetical(name)
    if paren and paren not in results:
        results.append(paren)
    if old_name:
        old_norm = normalize_name(old_name)
        if old_norm and old_norm not in results:
            results.append(old_norm)
        old_paren = extract_parenthetical(old_name)
        if old_paren and old_paren not in results:
            results.append(old_paren)
    return results


# Known name overrides: normalized DB name -> normalized API name
# Used when DB names are structurally different from API names
NAME_OVERRIDES: dict[str, str] = {
    # NCR district mapping (DB province name -> API HUC name)
    "ncr 1st district manila": "manila",
    "ncr 2nd district": "caloocan",
    "ncr 3rd district": "pasig",
    "ncr 4th district": "quezon city",
    "taguigpateros": "taguig",
    # Compostela Valley was renamed to Davao de Oro
    "compostela valley": "davao de oro",
    # Maguindanao was split into Maguindanao del Norte and del Sur
    "maguindanao": "maguindanao del norte",
}


# ---------------------------------------------------------------------------
# PSA API Client
# ---------------------------------------------------------------------------


class PsaApiClient:
    def __init__(self, token: str):
        self.token = token
        self.base = f"{PSGC_BASE}/{PSGC_VERSION}"
        self.http = httpx.Client(timeout=60.0)

    def fetch_all(self, level: str) -> list[dict[str, Any]]:
        """Fetch all records for a given level, handling pagination."""
        cache_path = CACHE_DIR / f"{level}.json"
        if cache_path.exists():
            logger.info("Loading cached %s from %s", level, cache_path)
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        records: list[dict[str, Any]] = []
        url = f"{self.base}/{level}?token={self.token}&perPage={PAGE_SIZE}&page=1"

        page = 1
        while url:
            logger.info("Fetching %s page %s...", level, page)
            try:
                resp = self.http.get(url)
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                logger.error("API error on %s page %s: %s", level, page, exc)
                break

            # API returns {"count": N, "next": url, "previous": null, "results": {"psgc_data": [...]}}
            results_obj = data.get("results", {})
            if isinstance(results_obj, dict):
                page_records = results_obj.get("psgc_data", [])
            else:
                page_records = results_obj if isinstance(results_obj, list) else []
            records.extend(page_records)

            # Check for next page
            next_url = data.get("next")
            if next_url:
                # Append token if not already in URL
                if "token=" not in next_url:
                    separator = "&" if "?" in next_url else "?"
                    next_url = f"{next_url}{separator}token={self.token}"
                url = next_url
                page += 1
                time.sleep(API_DELAY)
            else:
                url = None

        logger.info("Fetched %s total %s records", level, len(records))

        # Cache to disk
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return records


# ---------------------------------------------------------------------------
# Supabase REST Client
# ---------------------------------------------------------------------------


class SupabaseClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        self.http = httpx.Client(timeout=120.0)

    def fetch_all_rows(self, table: str, select: str = "*") -> list[dict[str, Any]]:
        """Fetch all rows from a table with pagination."""
        all_rows: list[dict[str, Any]] = []
        start = 0
        batch = 1000
        while True:
            url = f"{self.base_url}/rest/v1/{table}?select={select}"
            url += f"&limit={batch}&offset={start}"
            try:
                resp = self.http.get(url, headers=self.headers)
                resp.raise_for_status()
                rows = resp.json()
            except Exception as exc:
                logger.error("Error fetching from %s (offset %s): %s", table, start, exc)
                break
            all_rows.extend(rows)
            if len(rows) < batch:
                break
            start += batch
        return all_rows

    def update_row(self, table: str, pk_col: str, pk_val: int, data: dict[str, Any]) -> bool:
        """Update a single row by primary key."""
        url = f"{self.base_url}/rest/v1/{table}?{pk_col}=eq.{pk_val}"
        headers = {**self.headers, "Prefer": "return=minimal"}
        try:
            resp = self.http.patch(url, json=data, headers=headers)
            resp.raise_for_status()
            return True
        except Exception as exc:
            logger.warning("Update failed %s/%s=%s: %s", table, pk_col, pk_val, exc)
            return False

    def insert_batch(self, table: str, rows: list[dict[str, Any]]) -> tuple[int, str]:
        """Insert a batch of rows. Returns (count, error_msg)."""
        if not rows:
            return 0, ""
        url = f"{self.base_url}/rest/v1/{table}"
        try:
            resp = self.http.post(url, json=rows, headers=self.headers)
            resp.raise_for_status()
            return len(rows), ""
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            return 0, f"HTTP {exc.response.status_code}: {body}"
        except Exception as exc:
            return 0, str(exc)

    def upsert_batch(self, table: str, rows: list[dict[str, Any]], on_conflict: str = "") -> tuple[int, str]:
        """Upsert a batch of rows using merge-duplicates."""
        if not rows:
            return 0, ""
        url = f"{self.base_url}/rest/v1/{table}"
        prefer = "resolution=merge-duplicates"
        if on_conflict:
            prefer += f",on_conflict=({on_conflict})"
        headers = {**self.headers, "Prefer": prefer}
        try:
            resp = self.http.post(url, json=rows, headers=headers)
            resp.raise_for_status()
            return len(rows), ""
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            return 0, f"HTTP {exc.response.status_code}: {body}"
        except Exception as exc:
            return 0, str(exc)

    def get_max_id(self, table: str, id_col: str) -> int:
        """Get the maximum ID from a table."""
        url = f"{self.base_url}/rest/v1/{table}?select={id_col}&order={id_col}.desc&limit=1"
        try:
            resp = self.http.get(url, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            if data:
                return data[0].get(id_col, 0)
        except Exception:
            pass
        return 0


# ---------------------------------------------------------------------------
# Population extraction
# ---------------------------------------------------------------------------


def _parse_population_value(value) -> int | None:
    """Parse a population value that may be a string with commas/spaces."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    # String like " 5,026,128 " or "5,342,453"
    cleaned = str(value).strip().replace(",", "").replace(" ", "")
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except (TypeError, ValueError):
        return None


def extract_population(record: dict[str, Any]) -> dict[str, int | None]:
    """Extract population data from a PSA API record."""
    pop_data = record.get("population_data", [])
    result = {"population_2015": None, "population_2020": None, "population_2024": None}
    if not pop_data:
        return result
    for entry in pop_data:
        year = entry.get("year")
        pop = entry.get("population")
        if year and pop is not None:
            year_str = str(year)
            parsed = _parse_population_value(pop)
            if parsed is None:
                continue
            if "2015" in year_str:
                result["population_2015"] = parsed
            elif "2020" in year_str:
                result["population_2020"] = parsed
            elif "2024" in year_str:
                result["population_2024"] = parsed
    return result


# ---------------------------------------------------------------------------
# Sync logic per level
# ---------------------------------------------------------------------------


def sync_regions(
    api_records: list[dict[str, Any]],
    sb: SupabaseClient,
    report: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync regions from PSA API to Supabase."""
    logger.info("=== Syncing REGIONS ===")
    db_rows = sb.fetch_all_rows("regions", "region_id,name,psgc_code,lat,lon")

    if not db_rows:
        logger.warning("No existing regions fetched from DB — skipping sync to avoid duplicates (possible network issue)")
        return {"matched": 0, "updated": 0, "inserted": 0, "unmatched": 0}

    # Build lookup by normalized name
    db_by_name: dict[str, dict[str, Any]] = {}
    for row in db_rows:
        norm = normalize_name(row.get("name", ""))
        if norm:
            db_by_name[norm] = row

    # Alternate name mapping for abbreviated DB region names
    alt_names: dict[str, str] = {
        "ncr": "national capital region",
        "car": "cordillera administrative region",
        "barmm": "bangsamoro autonomous region in muslim mindanao",
        "region ivb": "mimaropa region",
    }

    matched = 0
    updated = 0
    inserted = 0
    unmatched = 0
    max_id = sb.get_max_id("regions", "region_id")
    new_regions: list[dict[str, Any]] = []

    for rec in api_records:
        api_name = rec.get("area_name", "").strip()
        api_norm = normalize_name(api_name)
        psgc_code = rec.get("psgc_code", "")
        pop = extract_population(rec)
        island_group = rec.get("island_region", "")
        geo_level = rec.get("geographic_level", "")

        db_row = db_by_name.get(api_norm)

        # Try alternate name mapping (e.g., API "National Capital Region (NCR)" -> DB "NCR")
        if not db_row:
            for db_norm, db_row_val in db_by_name.items():
                alt_target = alt_names.get(db_norm)
                if alt_target and alt_target == api_norm:
                    db_row = db_row_val
                    break

        if db_row:
            matched += 1
            region_id = db_row["region_id"]
            update_data = {
                "psgc_code": psgc_code,
                "island_group": island_group,
                "geographic_level": geo_level,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            }
            if sb.update_row("regions", "region_id", region_id, update_data):
                updated += 1
        else:
            # Insert new region (e.g., NIR - Negros Island Region)
            max_id += 1
            new_regions.append({
                "region_id": max_id,
                "name": api_name,
                "psgc_code": psgc_code,
                "island_group": island_group,
                "geographic_level": geo_level,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            })
            inserted += 1
            db_by_name[api_norm] = {"region_id": max_id}
            logger.info("Inserting new region: %s (psgc: %s)", api_name, psgc_code)

    # Batch insert new regions
    if new_regions:
        count, err = sb.insert_batch("regions", new_regions)
        if err:
            logger.error("Region insert error: %s", err)
        else:
            logger.info("Inserted %s new regions", count)

    logger.info("Regions: matched=%s updated=%s unmatched=%s", matched, updated, unmatched)
    return {"matched": matched, "updated": updated, "inserted": inserted, "unmatched": unmatched}


def sync_provinces(
    api_records: list[dict[str, Any]],
    sb: SupabaseClient,
    report: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync provinces from PSA API to Supabase."""
    logger.info("=== Syncing PROVINCES ===")
    db_rows = sb.fetch_all_rows("provinces", "province_id,region_id,name,psgc_code,lat,lon")
    db_regions = sb.fetch_all_rows("regions", "region_id,name,psgc_code")

    if not db_rows:
        logger.warning("No existing provinces fetched from DB — skipping sync (possible network issue)")
        return {"matched": 0, "updated": 0, "inserted": 0, "unmatched": 0}

    # Build region lookup by psgc_code and by normalized name
    region_by_psgc: dict[str, int] = {}
    region_by_name: dict[str, int] = {}
    for r in db_regions:
        if r.get("psgc_code"):
            region_by_psgc[r["psgc_code"]] = r["region_id"]
        region_by_name[normalize_name(r.get("name", ""))] = r["region_id"]

    # Build province lookup by normalized name within region
    db_by_name: dict[tuple[str, int], dict[str, Any]] = {}
    db_by_psgc: dict[str, dict[str, Any]] = {}
    db_by_norm_only: dict[str, dict[str, Any]] = {}
    for row in db_rows:
        norm = normalize_name(row.get("name", ""))
        region_id = row.get("region_id", 0)
        if norm:
            db_by_name[(norm, region_id)] = row
            db_by_norm_only[norm] = row
        # Also index by parenthetical content (old name)
        paren = extract_parenthetical(row.get("name", ""))
        if paren and paren not in db_by_norm_only:
            db_by_norm_only[paren] = row
        if row.get("psgc_code"):
            db_by_psgc[row["psgc_code"]] = row

    # Build reverse NAME_OVERRIDES: API normalized name -> DB normalized name
    api_to_db_override: dict[str, str] = {}
    for db_norm, api_norm in NAME_OVERRIDES.items():
        api_to_db_override[api_norm] = db_norm

    matched = 0
    updated = 0
    inserted = 0
    unmatched = 0
    max_id = sb.get_max_id("provinces", "province_id")

    new_provinces: list[dict[str, Any]] = []

    for rec in api_records:
        api_name = rec.get("area_name", "").strip()
        api_norm = normalize_name(api_name)
        psgc_code = rec.get("psgc_code", "")
        pop = extract_population(rec)
        island_group = rec.get("island_region", "")
        income_class = rec.get("income_classification", "")
        geo_level = rec.get("geographic_level", "")
        old_name = rec.get("old_name", "")

        # Find parent region
        reg_code = rec.get("reg")
        parent_region_id = None
        if reg_code:
            # Try to find region by reg code in psgc_code
            for r_psgc, r_id in region_by_psgc.items():
                if r_psgc.startswith(str(reg_code).zfill(2)):
                    parent_region_id = r_id
                    break

        # Try match by psgc_code first
        db_row = db_by_psgc.get(psgc_code) if psgc_code else None

        # Try match by name within region
        if not db_row and parent_region_id is not None:
            db_row = db_by_name.get((api_norm, parent_region_id))

        # Try match by name only (any region)
        if not db_row:
            db_row = db_by_norm_only.get(api_norm)

        # Try NAME_OVERRIDES (API name -> DB name)
        if not db_row:
            db_norm_override = api_to_db_override.get(api_norm)
            if db_norm_override:
                db_row = db_by_norm_only.get(db_norm_override)

        # Try matching API old_name to DB names
        if not db_row and old_name:
            for alt in normalize_with_old_name(api_name, old_name):
                if alt == api_norm:
                    continue
                db_row = db_by_norm_only.get(alt)
                if db_row:
                    break

        # Try matching API name to DB parenthetical/old names
        if not db_row:
            for db_norm, db_row_val in db_by_norm_only.items():
                db_paren = extract_parenthetical(db_norm)
                if db_paren and db_paren == api_norm:
                    db_row = db_row_val
                    break

        if db_row:
            matched += 1
            province_id = db_row["province_id"]
            update_data = {
                "psgc_code": psgc_code,
                "island_group": island_group,
                "income_classification": income_class,
                "geographic_level": geo_level,
                "old_name": old_name if old_name else None,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            }
            if sb.update_row("provinces", "province_id", province_id, update_data):
                updated += 1
        else:
            # Insert new province
            if parent_region_id is not None:
                max_id += 1
                new_provinces.append({
                    "province_id": max_id,
                    "region_id": parent_region_id,
                    "name": api_name,
                    "psgc_code": psgc_code,
                    "island_group": island_group,
                    "income_classification": income_class,
                    "geographic_level": geo_level,
                    "old_name": old_name if old_name else None,
                    "population_2015": pop["population_2015"],
                    "population_2020": pop["population_2020"],
                    "population_2024": pop["population_2024"],
                })
                inserted += 1
                db_by_psgc[psgc_code] = {"province_id": max_id, "region_id": parent_region_id}
            else:
                unmatched += 1
                report.append({
                    "level": "province",
                    "api_name": api_name,
                    "psgc_code": psgc_code,
                    "status": "unmatched_no_parent",
                })
                logger.warning("Unmatched province (no parent): %s (psgc: %s)", api_name, psgc_code)

    # Batch insert new provinces
    if new_provinces:
        count, err = sb.insert_batch("provinces", new_provinces)
        if err:
            logger.error("Province insert error: %s", err)
        else:
            logger.info("Inserted %s new provinces", count)

    logger.info("Provinces: matched=%s updated=%s inserted=%s unmatched=%s", matched, updated, inserted, unmatched)
    return {"matched": matched, "updated": updated, "inserted": inserted, "unmatched": unmatched}


def sync_municipalities(
    api_records: list[dict[str, Any]],
    sb: SupabaseClient,
    report: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync municipalities from PSA API to Supabase."""
    logger.info("=== Syncing MUNICIPALITIES ===")
    db_rows = sb.fetch_all_rows(
        "municipalities",
        "municipality_id,province_id,name,psgc_code,lat,lon",
    )
    db_provinces = sb.fetch_all_rows("provinces", "province_id,region_id,name,psgc_code")

    if not db_rows:
        logger.warning("No existing municipalities fetched from DB — skipping sync (possible network issue)")
        return {"matched": 0, "updated": 0, "inserted": 0, "unmatched": 0}

    # Build province lookup by psgc_code
    prov_by_psgc: dict[str, dict[str, Any]] = {}
    for p in db_provinces:
        if p.get("psgc_code"):
            prov_by_psgc[p["psgc_code"]] = p

    # Build municipality lookup
    db_by_name: dict[tuple[str, int], dict[str, Any]] = {}
    db_by_psgc: dict[str, dict[str, Any]] = {}
    db_by_norm_only: dict[str, dict[str, Any]] = {}
    for row in db_rows:
        norm = normalize_name(row.get("name", ""))
        province_id = row.get("province_id", 0)
        if norm:
            db_by_name[(norm, province_id)] = row
            if norm not in db_by_norm_only:
                db_by_norm_only[norm] = row
        # Also index by parenthetical content (old name in parentheses)
        paren = extract_parenthetical(row.get("name", ""))
        if paren and paren not in db_by_norm_only:
            db_by_norm_only[paren] = row
        if row.get("psgc_code"):
            db_by_psgc[row["psgc_code"]] = row

    matched = 0
    updated = 0
    inserted = 0
    unmatched = 0
    max_id = sb.get_max_id("municipalities", "municipality_id")

    new_munis: list[dict[str, Any]] = []
    pop_rows: list[dict[str, Any]] = []

    for rec in api_records:
        api_name = rec.get("area_name", "").strip()
        api_norm = normalize_name(api_name)
        psgc_code = rec.get("psgc_code", "")
        pop = extract_population(rec)
        island_group = rec.get("island_region", "")
        income_class = rec.get("income_classification", "")
        city_class = rec.get("city_class", "")
        geo_level = rec.get("geographic_level", "")
        old_name = rec.get("old_name", "")
        is_city = bool(city_class and city_class.strip())

        # Find parent province via PSGC code prefix
        # Province psgc_code is the first 7 digits of municipality psgc_code (without last 3)
        parent_province_id = None
        if psgc_code and len(psgc_code) >= 7:
            prov_psgc = psgc_code[:7] + "000"
            prov_row = prov_by_psgc.get(prov_psgc)
            if prov_row:
                parent_province_id = prov_row["province_id"]
            else:
                # Try progressively shorter prefixes
                for length in [7, 6, 5]:
                    prefix = psgc_code[:length]
                    for p_psgc, p_row in prov_by_psgc.items():
                        if p_psgc.startswith(prefix):
                            parent_province_id = p_row["province_id"]
                            break
                    if parent_province_id:
                        break

        # Try match by psgc_code first
        db_row = db_by_psgc.get(psgc_code) if psgc_code else None

        # Try match by name within province
        if not db_row and parent_province_id is not None:
            db_row = db_by_name.get((api_norm, parent_province_id))

        # Try match by name only (any province)
        if not db_row:
            db_row = db_by_norm_only.get(api_norm)

        # Try matching API old_name to DB names
        if not db_row and old_name:
            for alt in normalize_with_old_name(api_name, old_name):
                if alt == api_norm:
                    continue
                db_row = db_by_norm_only.get(alt)
                if db_row:
                    break

        # Try matching API name to DB parenthetical/old names
        if not db_row:
            api_paren = extract_parenthetical(api_name)
            if api_paren:
                db_row = db_by_norm_only.get(api_paren)
        if not db_row:
            for db_norm_key, db_row_val in db_by_norm_only.items():
                db_paren = extract_parenthetical(db_norm_key)
                if db_paren and db_paren == api_norm:
                    db_row = db_row_val
                    break

        if db_row:
            matched += 1
            muni_id = db_row["municipality_id"]
            update_data = {
                "psgc_code": psgc_code,
                "island_group": island_group,
                "income_classification": income_class if income_class else None,
                "city_class": city_class if city_class else None,
                "is_city": is_city,
                "geographic_level": geo_level,
                "old_name": old_name if old_name else None,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            }
            if sb.update_row("municipalities", "municipality_id", muni_id, update_data):
                updated += 1

            # Populate municipal_population
            if any(v is not None for v in pop.values()):
                pop_rows.append({
                    "municipality_id": muni_id,
                    "province_id": db_row.get("province_id", parent_province_id or 0),
                    "population_2015": pop["population_2015"],
                    "population_2020": pop["population_2020"],
                    "population_2024": pop["population_2024"],
                })
        else:
            if parent_province_id is not None:
                max_id += 1
                new_munis.append({
                    "municipality_id": max_id,
                    "province_id": parent_province_id,
                    "name": api_name,
                    "psgc_code": psgc_code,
                    "island_group": island_group,
                    "income_classification": income_class if income_class else None,
                    "city_class": city_class if city_class else None,
                    "is_city": is_city,
                    "geographic_level": geo_level,
                    "old_name": old_name if old_name else None,
                    "population_2015": pop["population_2015"],
                    "population_2020": pop["population_2020"],
                    "population_2024": pop["population_2024"],
                })
                inserted += 1
                db_by_psgc[psgc_code] = {"municipality_id": max_id, "province_id": parent_province_id}

                if any(v is not None for v in pop.values()):
                    pop_rows.append({
                        "municipality_id": max_id,
                        "province_id": parent_province_id,
                        "population_2015": pop["population_2015"],
                        "population_2020": pop["population_2020"],
                        "population_2024": pop["population_2024"],
                    })
            else:
                unmatched += 1
                report.append({
                    "level": "municipality",
                    "api_name": api_name,
                    "psgc_code": psgc_code,
                    "status": "unmatched_no_parent",
                })
                logger.warning("Unmatched municipality (no parent): %s (psgc: %s)", api_name, psgc_code)

    # Batch insert new municipalities
    if new_munis:
        count, err = sb.insert_batch("municipalities", new_munis)
        if err:
            logger.error("Municipality insert error: %s", err)
        else:
            logger.info("Inserted %s new municipalities", count)

    # Upsert municipal_population
    if pop_rows:
        # Do in batches of 500
        for i in range(0, len(pop_rows), 500):
            batch = pop_rows[i : i + 500]
            count, err = sb.upsert_batch("municipal_population", batch, on_conflict="municipality_id")
            if err:
                logger.warning("municipal_population upsert error (batch %s): %s", i // 500, err)
            else:
                logger.info("Upserted %s municipal_population rows (batch %s)", count, i // 500)

    logger.info("Municipalities: matched=%s updated=%s inserted=%s unmatched=%s", matched, updated, inserted, unmatched)
    return {"matched": matched, "updated": updated, "inserted": inserted, "unmatched": unmatched}


def sync_barangays(
    api_records: list[dict[str, Any]],
    sb: SupabaseClient,
    report: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync barangays from PSA API to Supabase."""
    logger.info("=== Syncing BARANGAYS ===")
    db_rows = sb.fetch_all_rows("barangays", "barangay_id,municipality_id,name,psgc_code,lat,lon")
    db_munis = sb.fetch_all_rows("municipalities", "municipality_id,province_id,name,psgc_code")

    if not db_rows:
        logger.warning("No existing barangays fetched from DB — skipping sync (possible network issue)")
        return {"matched": 0, "updated": 0, "inserted": 0, "unmatched": 0}

    # Build municipality lookup by psgc_code and by name
    muni_by_psgc: dict[str, dict[str, Any]] = {}
    muni_by_name: dict[str, dict[str, Any]] = {}
    for m in db_munis:
        if m.get("psgc_code"):
            muni_by_psgc[m["psgc_code"]] = m
        norm = normalize_name(m.get("name", ""))
        if norm and norm not in muni_by_name:
            muni_by_name[norm] = m
        paren = extract_parenthetical(m.get("name", ""))
        if paren and paren not in muni_by_name:
            muni_by_name[paren] = m

    # Build barangay lookup by (normalized name, municipality_id)
    db_by_name: dict[tuple[str, int], dict[str, Any]] = {}
    db_by_psgc: dict[str, dict[str, Any]] = {}
    for row in db_rows:
        norm = normalize_name(row.get("name", ""))
        muni_id = row.get("municipality_id", 0)
        if norm:
            db_by_name[(norm, muni_id)] = row
        if row.get("psgc_code"):
            db_by_psgc[row["psgc_code"]] = row

    # Build API municipality lookup by PSGC code for parent matching fallback
    api_muni_by_psgc: dict[str, str] = {}  # psgc_code -> normalized name
    api_muni_cache = CACHE_DIR / "municipalities.json"
    if api_muni_cache.exists():
        with open(api_muni_cache, "r", encoding="utf-8") as f:
            api_munis = json.load(f)
            for am in api_munis:
                ac = am.get("psgc_code", "")
                if ac:
                    api_muni_by_psgc[ac] = normalize_name(am.get("area_name", ""))

    matched = 0
    updated = 0
    inserted = 0
    unmatched = 0
    max_id = sb.get_max_id("barangays", "barangay_id")

    new_barangays: list[dict[str, Any]] = []
    INSERT_BATCH_SIZE = 200
    total_inserted = 0

    for rec in api_records:
        api_name = rec.get("area_name", "").strip()
        api_norm = normalize_name(api_name)
        psgc_code = rec.get("psgc_code", "")
        pop = extract_population(rec)
        island_group = rec.get("island_region", "")
        urban_rural = rec.get("urban_rural", "")
        geo_level = rec.get("geographic_level", "")
        old_name = rec.get("old_name", "")
        status = rec.get("status", "")

        # Find parent municipality via PSGC code prefix
        # Municipality psgc_code is the first 7 digits + "000" of barangay psgc_code
        parent_muni_id = None
        if psgc_code and len(psgc_code) >= 7:
            muni_psgc = psgc_code[:7] + "000"
            muni_row = muni_by_psgc.get(muni_psgc)
            if muni_row:
                parent_muni_id = muni_row["municipality_id"]
            else:
                # Try matching by shorter prefix
                for length in [7, 6, 5]:
                    prefix = psgc_code[:length]
                    for m_psgc, m_row in muni_by_psgc.items():
                        if m_psgc.startswith(prefix):
                            parent_muni_id = m_row["municipality_id"]
                            break
                    if parent_muni_id:
                        break

        # Fallback: use API municipality cache to find parent by name
        if not parent_muni_id and psgc_code and len(psgc_code) >= 7:
            muni_psgc = psgc_code[:7] + "000"
            api_muni_norm = api_muni_by_psgc.get(muni_psgc)
            if api_muni_norm:
                # Try exact name match
                m_row = muni_by_name.get(api_muni_norm)
                if m_row:
                    parent_muni_id = m_row["municipality_id"]
                else:
                    # Try parenthetical match
                    for mn, mr in muni_by_name.items():
                        if extract_parenthetical(mn) == api_muni_norm:
                            parent_muni_id = mr["municipality_id"]
                            break

        # Try match by psgc_code first
        db_row = db_by_psgc.get(psgc_code) if psgc_code else None

        # Try match by name within municipality
        if not db_row and parent_muni_id is not None:
            db_row = db_by_name.get((api_norm, parent_muni_id))

        if db_row:
            matched += 1
            barangay_id = db_row["barangay_id"]
            update_data = {
                "psgc_code": psgc_code,
                "island_group": island_group,
                "urban_rural": urban_rural if urban_rural else None,
                "geographic_level": geo_level,
                "old_name": old_name if old_name else None,
                "status": status if status else None,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            }
            if sb.update_row("barangays", "barangay_id", barangay_id, update_data):
                updated += 1
        else:
            if parent_muni_id is not None:
                max_id += 1
                new_barangays.append({
                    "barangay_id": max_id,
                    "municipality_id": parent_muni_id,
                    "name": api_name,
                    "psgc_code": psgc_code,
                    "island_group": island_group,
                    "urban_rural": urban_rural if urban_rural else None,
                    "geographic_level": geo_level,
                    "old_name": old_name if old_name else None,
                    "status": status if status else None,
                    "population_2015": pop["population_2015"],
                    "population_2020": pop["population_2020"],
                    "population_2024": pop["population_2024"],
                })
                inserted += 1

                # Batch insert
                if len(new_barangays) >= INSERT_BATCH_SIZE:
                    count, err = sb.insert_batch("barangays", new_barangays)
                    if err:
                        logger.error("Barangay insert error: %s", err)
                    else:
                        total_inserted += count
                        logger.info("Inserted %s barangays (total new: %s)", count, total_inserted)
                    new_barangays = []
            else:
                unmatched += 1
                if unmatched <= 100:  # Log only first 100 to avoid spam
                    report.append({
                        "level": "barangay",
                        "api_name": api_name,
                        "psgc_code": psgc_code,
                        "status": "unmatched_no_parent",
                    })
                if unmatched == 1:
                    logger.warning("First unmatched barangay (no parent): %s (psgc: %s)", api_name, psgc_code)

    # Insert remaining batch
    if new_barangays:
        count, err = sb.insert_batch("barangays", new_barangays)
        if err:
            logger.error("Barangay insert error (final batch): %s", err)
        else:
            total_inserted += count

    logger.info("Barangays: matched=%s updated=%s inserted=%s(total=%s) unmatched=%s",
                matched, updated, inserted, total_inserted, unmatched)
    return {"matched": matched, "updated": updated, "inserted": total_inserted, "unmatched": unmatched}


def sync_population_data(
    api_data: dict[str, list[dict[str, Any]]],
    sb: SupabaseClient,
) -> int:
    """Populate population_data table with all historical population records."""
    logger.info("=== Populating population_data table ===")
    rows: list[dict[str, Any]] = []

    level_map = {
        "regions": "region",
        "provinces": "province",
        "municipalities": "municipality",
        "barangays": "barangay",
    }

    for level_key, level_name in level_map.items():
        records = api_data.get(level_key, [])
        for rec in records:
            psgc_code = rec.get("psgc_code", "")
            if not psgc_code:
                continue
            pop_data = rec.get("population_data", [])
            for entry in pop_data:
                year = entry.get("year")
                pop = entry.get("population")
                if year and pop is not None:
                    parsed = _parse_population_value(pop)
                    if parsed is None:
                        continue
                    rows.append({
                        "psgc_code": psgc_code,
                        "geographic_level": level_name,
                        "year": int(year),
                        "population": parsed,
                    })

    # Delete existing population_data, then insert fresh (on_conflict doesn't work
    # with the unique constraint on this PostgREST version)
    delete_url = f"{sb.base_url}/rest/v1/population_data?psgc_code=neq.0000000000"
    try:
        resp = sb.http.delete(delete_url, headers=sb.headers)
        resp.raise_for_status()
        logger.info("Cleared existing population_data rows")
    except Exception as exc:
        logger.warning("Could not clear population_data: %s", exc)

    # Insert in batches of 500
    total = 0
    for i in range(0, len(rows), 500):
        batch = rows[i : i + 500]
        count, err = sb.insert_batch("population_data", batch)
        if err:
            logger.warning("population_data insert error (batch %s): %s", i // 500, err)
        else:
            total += count

    logger.info("Population_data: inserted %s records", total)
    return total


def sync_municipal_population(
    api_data: dict[str, list[dict[str, Any]]],
    sb: SupabaseClient,
) -> int:
    """Populate municipal_population table from municipality API data."""
    logger.info("=== Populating municipal_population table ===")

    # Fetch existing municipalities to get municipality_id and province_id by psgc_code
    db_munis = sb.fetch_all_rows("municipalities", "municipality_id,province_id,psgc_code")
    muni_by_psgc: dict[str, dict[str, Any]] = {}
    for m in db_munis:
        code = m.get("psgc_code")
        if code:
            muni_by_psgc[code] = m

    rows: list[dict[str, Any]] = []
    muni_records = api_data.get("municipalities", [])
    for rec in muni_records:
        psgc_code = rec.get("psgc_code", "")
        if not psgc_code:
            continue
        db_muni = muni_by_psgc.get(psgc_code)
        if not db_muni:
            continue
        pop = extract_population(rec)
        rows.append({
            "municipality_id": db_muni["municipality_id"],
            "province_id": db_muni["province_id"],
            "population_2015": pop["population_2015"],
            "population_2020": pop["population_2020"],
            "population_2024": pop["population_2024"],
        })

    # Upsert in batches of 500
    total = 0
    for i in range(0, len(rows), 500):
        batch = rows[i : i + 500]
        count, err = sb.upsert_batch("municipal_population", batch, on_conflict="municipality_id")
        if err:
            logger.warning("municipal_population upsert error (batch %s): %s", i // 500, err)
        else:
            total += count

    logger.info("Municipal_population: upserted %s records", total)
    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync PSGC data from PSA API to Supabase")
    parser.add_argument("--skip-fetch", action="store_true", help="Use cached JSON instead of fetching from API")
    parser.add_argument("--level", choices=LEVELS, help="Sync only one level")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")

    psgc_token = os.getenv("PSGC_API_CODE")
    sb_url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    sb_key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )

    if not sb_url or not sb_key:
        logger.error("Missing SUPABASE_URL or SUPABASE key in .env")
        return 1

    if not args.skip_fetch and not psgc_token:
        logger.error("Missing PSGC_API_CODE in .env")
        return 1

    # Initialize clients
    sb = SupabaseClient(sb_url, sb_key)

    # Fetch or load cached data
    api_data: dict[str, list[dict[str, Any]]] = {}
    levels_to_sync = [args.level] if args.level else LEVELS

    if not args.skip_fetch:
        api_client = PsaApiClient(psgc_token)
        for level in levels_to_sync:
            api_data[level] = api_client.fetch_all(level)
    else:
        for level in levels_to_sync:
            cache_path = CACHE_DIR / f"{level}.json"
            if cache_path.exists():
                with open(cache_path, "r", encoding="utf-8") as f:
                    api_data[level] = json.load(f)
                logger.info("Loaded cached %s: %s records", level, len(api_data[level]))
            else:
                logger.error("No cached data for %s. Run without --skip-fetch first.", level)
                return 1

    # Sync each level
    report: list[dict[str, Any]] = []
    summary: dict[str, dict[str, int]] = {}

    if "regions" in levels_to_sync:
        summary["regions"] = sync_regions(api_data.get("regions", []), sb, report)
    if "provinces" in levels_to_sync:
        summary["provinces"] = sync_provinces(api_data.get("provinces", []), sb, report)
    if "municipalities" in levels_to_sync:
        summary["municipalities"] = sync_municipalities(api_data.get("municipalities", []), sb, report)
    if "barangays" in levels_to_sync:
        summary["barangays"] = sync_barangays(api_data.get("barangays", []), sb, report)

    # Populate population tables (only when syncing all levels)
    if not args.level:
        sync_population_data(api_data, sb)
        sync_municipal_population(api_data, sb)

    # Write report
    report_path = CACHE_DIR / "sync_report.csv"
    if report:
        with open(report_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["level", "api_name", "psgc_code", "status"])
            writer.writeheader()
            writer.writerows(report)
        logger.info("Unmatched report written to %s (%s entries)", report_path, len(report))
    else:
        logger.info("No unmatched entries — all records matched!")

    # Print summary
    logger.info("=" * 60)
    logger.info("SYNC SUMMARY")
    logger.info("=" * 60)
    for level, stats in summary.items():
        logger.info(
            "  %s: matched=%s updated=%s inserted=%s unmatched=%s",
            level.ljust(15),
            stats["matched"],
            stats["updated"],
            stats["inserted"],
            stats["unmatched"],
        )
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
