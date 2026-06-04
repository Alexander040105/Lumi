from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx
import pandas as pd
import geopandas as gpd
from dotenv import load_dotenv


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    key: str


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=20.0)

    def fetch_table(self, table: str, columns: str, page_size: int = 1000) -> list[dict]:
        rows: list[dict] = []
        offset = 0
        while True:
            headers = dict(self.headers)
            headers["Range"] = f"{offset}-{offset + page_size - 1}"
            url = f"{self.base_url}/rest/v1/{table}"
            response = self.http.get(url, params={"select": columns}, headers=headers)
            response.raise_for_status()
            payload = response.json()
            if not payload:
                break
            rows.extend(payload)
            if len(payload) < page_size:
                break
            offset += page_size
        return rows


def load_env(repo_root: Path) -> None:
    load_dotenv(dotenv_path=repo_root / ".env", override=False)


def resolve_supabase_config(repo_root: Path) -> Optional[SupabaseConfig]:
    load_env(repo_root)
    url = os.getenv("SUPABASE_URL")
    key_candidates = (
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_ANON_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
    )
    key = None
    for key_name in key_candidates:
        value = os.getenv(key_name)
        if value:
            key = value
            break
    if url and key:
        return SupabaseConfig(url=url, key=key)
    return None


def load_municipalities(
    municipalities_csv: Path,
    provinces_csv: Path,
    supabase: Optional[SupabaseConfig],
    logger: logging.Logger,
) -> pd.DataFrame:
    municipalities = pd.read_csv(municipalities_csv)
    provinces = pd.read_csv(provinces_csv)
    provinces = provinces.rename(columns={"name": "province"})
    merged = municipalities.merge(provinces[["province_id", "province"]], on="province_id", how="left")

    if "lat" in merged.columns and "lon" in merged.columns:
        merged = merged.rename(columns={"lat": "latitude", "lon": "longitude"})
    else:
        merged["latitude"] = pd.NA
        merged["longitude"] = pd.NA

    if supabase:
        logger.info("Loading municipality coordinates from Supabase")
        client = SupabaseRestClient(supabase.url, supabase.key)
        payload = client.fetch_table("municipalities", "municipality_id,lat,lon")
        coords = pd.DataFrame(payload)
        coords = coords.rename(columns={"lat": "latitude", "lon": "longitude"})
        merged = merged.merge(coords, on="municipality_id", how="left", suffixes=("", "_sb"))
        merged["latitude"] = merged["latitude"].fillna(merged.pop("latitude_sb"))
        merged["longitude"] = merged["longitude"].fillna(merged.pop("longitude_sb"))

    missing = merged["latitude"].isna() | merged["longitude"].isna()
    if missing.any():
        count = int(missing.sum())
        logger.warning("Missing coordinates for %s municipalities", count)

    merged = merged.rename(columns={"name": "municipality_name"})
    merged = merged[
        [
            "municipality_id",
            "municipality_name",
            "province",
            "latitude",
            "longitude",
            "province_id",
        ]
    ]
    return merged


def load_polygons(path: Path, logger: logging.Logger) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        logger.warning("Polygon CRS missing; assuming EPSG:4326")
        gdf = gdf.set_crs("EPSG:4326")
    return gdf


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
