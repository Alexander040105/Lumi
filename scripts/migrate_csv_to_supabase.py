#!/usr/bin/env python3
"""
Migrate local CSV/GeoJSON datasets into Supabase.

Run from the repo root:
    python scripts/migrate_csv_to_supabase.py

Required environment variables (from the repo root .env):
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
"""

from __future__ import annotations

import json
import logging
import math
import os
import re

import numpy as np
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Repo root is two levels up from this script
ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")


_JWT_PATTERN = re.compile(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$")


def _is_jwt_key(key: str) -> bool:
    return bool(key) and _JWT_PATTERN.match(key) is not None


def _resolve_service_role_key() -> str:
    """Return a JWT-formatted key the supabase-py client can use.

    The environment may store either a real JWT (eyJ...) or a custom
    non-JWT identifier (sb_secret_...).  The official Supabase client
    requires a JWT, so fall back to the explicit JWT service role key.
    """
    for env_name in (
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
    ):
        value = os.environ.get(env_name)
        if value and _is_jwt_key(value):
            return value
    raise RuntimeError(
        "No JWT-formatted Supabase key found. "
        "Set SUPABASE_SERVICE_ROLE_KEY to a valid eyJ... JWT, or set "
        "SUPABASE_JWT_SERVICE_ROLE_KEY to the service_role JWT."
    )


def _get_client() -> Client:
    return create_client(SUPABASE_URL, _resolve_service_role_key())


# Copy of the mapping from energyhub.py so the migration script does not
# need to import the FastAPI application graph.
_PROVINCE_NAME_MAP = {
    "compostela valley": "davao de oro",
    "cotabato (north cot.)": "cotabato",
    "davao (davao del norte)": "davao del norte",
    "davao (davao occidental)": "davao occidental",
    "davao del sur": "davao del sur",
    "maguindanao": "maguindanao del norte",
    "ncr - 1st district (manila)": "ncr, city of manila, first district (not a province)",
    "ncr - 2nd district": "ncr, second district (not a province)",
    "ncr - 3rd district": "ncr, third district (not a province)",
    "ncr - 4th district": "ncr, fourth district (not a province)",
    "samar (western samar)": "samar",
    "taguig-pateros": "",  # not a province, skip
    "south cotabato": "south cotabato",
    "sultan kudarat": "sultan kudarat",
    "sulu": "sulu",
    "surigao del norte": "surigao del norte",
    "surigao del sur": "surigao del sur",
    "tawi-tawi": "tawi-tawi",
    "zambales": "zambales",
    "zamboanga del norte": "zamboanga del norte",
    "zamboanga del sur": "zamboanga del sur",
    "zamboanga sibugay": "zamboanga sibugay",
}


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _sanitize_value(value: Any) -> Any:
    """Replace NaN / inf floats with None and convert numpy scalars to Python types."""
    if value is None:
        return None
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        if pd.isna(value) or (isinstance(value, np.floating) and (np.isnan(value) or np.isinf(value))):
            return None
        return value.item()
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, (int, str, bool, list, dict)):
        return value
    # pandas / other scalar fallback
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _records_from_df(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Return a list of dicts with native Python types and None instead of NaN/inf."""
    df = df.copy()
    df = df.replace([math.inf, -math.inf], math.nan)
    # Ensure ID-ish columns stay ints when possible
    for col in df.columns:
        if col in ("municipality_id", "id") or col.endswith("_id"):
            if df[col].dtype.kind == "f":
                df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) else None)

    records = df.to_dict(orient="records")
    return [{col: _sanitize_value(value) for col, value in row.items()} for row in records]


def _fix_category(row: dict[str, Any]) -> str:
    """Replicate products.py category correction logic."""
    cat = str(row.get("energy_category", "")).lower().strip()
    src = str(row.get("source_file", "")).lower()
    base = src.split("/")[-1].split("\\")[-1]
    if base.endswith("_hydro.csv") and cat == "wind":
        return "hydro"
    if base.endswith("_solar.csv") and cat != "solar":
        return "solar"
    if base.endswith("_wind.csv") and cat != "wind":
        return "wind"
    if base.endswith("_geothermal.csv") and cat != "geothermal":
        return "geothermal"
    return cat


# ---------------------------------------------------------------------------
# DOE datasets stored as JSONB rows in doe_datasets
# ---------------------------------------------------------------------------

DOE_CSVS = [
    "DOE_Data_Extracted/data_v2_preprocessed/master_preprocessed.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/forecast_consumption_2025_2030.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/forecast_peak_demand_2025_2030.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/model_comparison_results.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/irena_ph_capacity_by_tech.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/irena_ph_generation_by_tech.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/irena_renewable_share.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/meralco_rates_2011_2020.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/solar_atlas_ph.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/regional_sales_2025.csv",
    "DOE_Data_Extracted/data_v2_preprocessed/provincial_consumption_2003_2025.csv",
    "DOE_Data_Extracted/data_v1/Tabula_DOE_Data.csv",
    # v1 fallbacks for files that also exist in v2 (predictor.py _prefer_v2 logic)
    "DOE_Data_Extracted/data_v1/master_preprocessed.csv",
    "DOE_Data_Extracted/data_v1/forecast_consumption_2025_2030.csv",
    "DOE_Data_Extracted/data_v1/forecast_peak_demand_2025_2030.csv",
    "DOE_Data_Extracted/data_v1/model_comparison_results.csv",
    "DOE_Data_Extracted/data_v1/irena_ph_capacity_by_tech.csv",
    "DOE_Data_Extracted/data_v1/irena_ph_generation_by_tech.csv",
    "DOE_Data_Extracted/data_v1/irena_renewable_share.csv",
    "DOE_Data_Extracted/data_v1/meralco_rates_2011_2020.csv",
    "DOE_Data_Extracted/data_v1/solar_atlas_ph.csv",
    "DOE_Data_Extracted/data_v1/regional_sales_2025.csv",
    "DOE_Data_Extracted/data_v1/provincial_consumption_2003_2025.csv",
]


def migrate_doe_datasets(client: Client) -> None:
    logger.info("Migrating DOE datasets into doe_datasets")
    for rel_path in DOE_CSVS:
        csv_path = ROOT / rel_path
        if not csv_path.exists():
            logger.warning("Skipping missing CSV: %s", rel_path)
            continue
        dataset_name = rel_path
        df = pd.read_csv(csv_path)
        records = _records_from_df(df)
        payload = {
            "dataset_name": dataset_name,
            "row_count": len(records),
            "data": records,
            "updated_at": "now()",
        }
        client.table("doe_datasets").upsert(payload, on_conflict="dataset_name").execute()
        logger.info("  -> %s: %s rows", dataset_name, len(records))


# ---------------------------------------------------------------------------
# Municipality climate averages
# ---------------------------------------------------------------------------


def _valid_municipality_ids(client: Client) -> set[int]:
    resp = client.table("municipalities").select("municipality_id").execute()
    return {int(r["municipality_id"]) for r in (resp.data or []) if r.get("municipality_id") is not None}


def migrate_climate(client: Client) -> None:
    csv_path = ROOT / "fastapi-backend/app/services/local_data/municipality_climate_averages.csv"
    df = pd.read_csv(csv_path)
    records = _records_from_df(df)
    valid_ids = _valid_municipality_ids(client)
    filtered = [r for r in records if r.get("municipality_id") in valid_ids]
    skipped = len(records) - len(filtered)
    if skipped:
        logger.warning("  -> skipped %s climate rows without matching municipalities", skipped)

    for i in range(0, len(filtered), 500):
        batch = filtered[i : i + 500]
        client.table("municipality_climate_averages").upsert(
            batch, on_conflict="municipality_id"
        ).execute()
    logger.info("Migrated municipality_climate_averages: %s rows", len(filtered))


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------


def migrate_products(client: Client) -> None:
    csv_path = ROOT / "fastapi-backend/app/services/local_data/products.csv"
    df = pd.read_csv(csv_path)
    df["energy_category"] = df.apply(
        lambda row: _fix_category(row.to_dict()), axis=1
    )
    records = _records_from_df(df)
    # Source-of-truth refresh: delete existing rows then re-insert
    try:
        client.table("products").delete().neq("id", 0).execute()
    except Exception as exc:
        logger.warning("Could not clear products table (may be empty): %s", exc)

    for i in range(0, len(records), 500):
        client.table("products").insert(records[i : i + 500]).execute()
    logger.info("Migrated products: %s rows", len(records))


# ---------------------------------------------------------------------------
# Wind products
# ---------------------------------------------------------------------------

WIND_CSVS = [
    ("fastapi-backend/app/services/local_data/wind_products_joined.csv", "joined"),
    ("fastapi-backend/app/services/local_data/wind_products_joined_betz.csv", "betz"),
]


def _compute_wind_summary(df: pd.DataFrame) -> dict[str, Any]:
    df = df.copy()
    df["rotor_radius_m"] = pd.to_numeric(df["rotor_radius_m"], errors="coerce")
    df["power_coefficient"] = pd.to_numeric(df["power_coefficient"], errors="coerce")

    rotor_series = df["rotor_radius_m"].dropna()
    cp_series = df["power_coefficient"].dropna()

    avg_rotor = float(rotor_series.mean()) if not rotor_series.empty else 0.0
    avg_cp = float(cp_series.mean()) if not cp_series.empty else 0.0

    return {
        "avg_rotor_radius_m": avg_rotor,
        "avg_power_coefficient": avg_cp * 100,  # matches wind_output_calc.py output
        "rotor_count": int(len(rotor_series)),
        "cp_count": int(len(cp_series)),
        "summary_rotor": (
            f"Average rotor radius (m): {avg_rotor:.3f} from {len(rotor_series)} rows "
            f"where a blade diameter was parsed from text (m/cm/mm/in/ft), then divided by 2."
        ),
        "summary_cp": (
            f"Average power coefficient: {avg_cp:.3f} from {len(cp_series)} rows with both parsed power "
            f"(W/kW/MW) and diameter; uses Cp = P / (0.5 * 1.225 * A * V^3) with V=12.0 m/s unless a m/s value is present."
        ),
    }


def migrate_wind(client: Client) -> None:
    for rel_path, variant in WIND_CSVS:
        csv_path = ROOT / rel_path
        if not csv_path.exists():
            logger.warning("Wind CSV not found: %s", rel_path)
            continue
        df = pd.read_csv(csv_path)
        records = _records_from_df(df)

        # Source-of-truth refresh per variant
        try:
            client.table("wind_products").delete().eq("source_file", f"{variant}").execute()
        except Exception as exc:
            logger.warning("Could not clear wind_products for %s: %s", variant, exc)

        # source_file is a loose tag; keep the original column but also tag variant for deletion
        for rec in records:
            rec["source_file"] = variant

        for i in range(0, len(records), 500):
            client.table("wind_products").insert(records[i : i + 500]).execute()

        summary = _compute_wind_summary(df)
        summary["variant"] = variant
        summary["updated_at"] = "now()"
        client.table("wind_products_summary").upsert(
            summary, on_conflict="variant"
        ).execute()
        logger.info("Migrated wind products variant '%s': %s rows", variant, len(records))


# ---------------------------------------------------------------------------
# Geothermal CSV / JSON
# ---------------------------------------------------------------------------


def migrate_geothermal(client: Client) -> None:
    # Heat flow
    heat_path = ROOT / "fastapi-backend/app/services/local_data/geothermal_heatflow.csv"
    if heat_path.exists():
        df = pd.read_csv(heat_path)
        records = _records_from_df(df)
        try:
            client.table("geothermal_heatflow").delete().neq("id", 0).execute()
        except Exception as exc:
            logger.warning("Could not clear geothermal_heatflow: %s", exc)
        for i in range(0, len(records), 500):
            client.table("geothermal_heatflow").insert(records[i : i + 500]).execute()
        logger.info("Migrated geothermal_heatflow: %s rows", len(records))

    # Faults
    faults_path = ROOT / "fastapi-backend/app/services/local_data/geothermal_faults.json"
    if faults_path.exists():
        with open(faults_path, "r", encoding="utf-8") as f:
            faults = json.load(f)
        try:
            client.table("geothermal_faults").delete().neq("id", 0).execute()
        except Exception as exc:
            logger.warning("Could not clear geothermal_faults: %s", exc)
        records = [
            {
                "name": f.get("name"),
                "lat": _sanitize_value(f.get("lat")),
                "lon": _sanitize_value(f.get("lon")),
                "length_km": _sanitize_value(f.get("length_km")),
            }
            for f in faults
        ]
        client.table("geothermal_faults").insert(records).execute()
        logger.info("Migrated geothermal_faults: %s rows", len(records))

    # Volcanoes
    volcano_path = ROOT / "fastapi-backend/app/services/local_data/geothermal_volcanoes.json"
    if volcano_path.exists():
        with open(volcano_path, "r", encoding="utf-8") as f:
            volcanoes = json.load(f)
        try:
            client.table("geothermal_volcanoes").delete().neq("id", 0).execute()
        except Exception as exc:
            logger.warning("Could not clear geothermal_volcanoes: %s", exc)
        records = [
            {
                "name": v.get("name"),
                "lat": _sanitize_value(v.get("lat")),
                "lon": _sanitize_value(v.get("lon")),
            }
            for v in volcanoes
        ]
        client.table("geothermal_volcanoes").insert(records).execute()
        logger.info("Migrated geothermal_volcanoes: %s rows", len(records))


# ---------------------------------------------------------------------------
# GeoJSON files -> Supabase Storage + province name mapping
# ---------------------------------------------------------------------------

GEOJSON_FILES = [
    ("philippine_geojson/philippine_geojson_file_per_region.json", "philippine_geojson_file_per_region.json"),
    ("philippine_geojson/philippine_geojson_file_per_provinces.json", "philippine_geojson_file_per_provinces.json"),
    ("fastapi-backend/app/services/local_data/aquifers_ph.geojson", "aquifers_ph.geojson"),
]


def _extract_geojson_names(geojson_path: Path) -> dict[str, str]:
    """Return {lower(adm2_en): adm2_en} from a GeoJSON feature collection."""
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    names: dict[str, str] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        name = props.get("adm2_en") or props.get("ADM2_EN")
        if name:
            key = name.strip().lower()
            names[key] = name.strip()
    return names


def _upload_storage_object(client: Client, bucket: str, storage_path: str, local_path: Path) -> None:
    content = local_path.read_bytes()
    file_options = {"content-type": "application/json"} if local_path.suffix == ".json" else {"content-type": "application/geo+json"}
    try:
        # Remove existing object first so the upload is idempotent
        try:
            client.storage.from_(bucket).remove([storage_path])
        except Exception:
            pass
        client.storage.from_(bucket).upload(storage_path, content, file_options=file_options)
        logger.info("  -> uploaded %s to %s/%s", local_path, bucket, storage_path)
    except Exception as exc:
        logger.error("Failed to upload %s to storage: %s", local_path, exc)


def migrate_geojson(client: Client) -> None:
    bucket = "geojsons"
    try:
        client.storage.create_bucket(bucket, {"public": True})
    except Exception:
        logger.info("Storage bucket '%s' already exists or creation disabled", bucket)

    all_names: dict[str, str] = {}
    for rel_path, storage_name in GEOJSON_FILES:
        local_path = ROOT / rel_path
        if not local_path.exists():
            logger.warning("GeoJSON not found: %s", rel_path)
            continue
        _upload_storage_object(client, bucket, storage_name, local_path)
        if "province" in storage_name or "region" in storage_name:
            all_names.update(_extract_geojson_names(local_path))

    # Update provinces.geojson_name
    resp = client.table("provinces").select("province_id,name").execute()
    provinces = resp.data or []

    name_to_id: dict[str, int] = {}
    for p in provinces:
        name = str(p.get("name", "")).strip().lower()
        if name:
            name_to_id[name] = int(p["province_id"])

    updates = []
    for db_name_lower, province_id in name_to_id.items():
        matched = None
        if db_name_lower in all_names:
            matched = all_names[db_name_lower]
        else:
            mapped = _PROVINCE_NAME_MAP.get(db_name_lower)
            if mapped and mapped.strip():
                mapped_lower = mapped.strip().lower()
                if mapped_lower in all_names:
                    matched = all_names[mapped_lower]
        if matched:
            updates.append({"province_id": province_id, "geojson_name": matched})

    if updates:
        # Update geojson_name on the existing provinces table row by row.
        # Using .update avoids trying to insert rows and triggering NOT NULL
        # constraints on columns like region_id that we do not have here.
        for upd in updates:
            client.table("provinces").update(
                {"geojson_name": upd["geojson_name"]}
            ).eq("province_id", upd["province_id"]).execute()
        logger.info("Updated geojson_name for %s provinces", len(updates))
    else:
        logger.warning("No province names matched GeoJSON adm2_en values")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    client = _get_client()
    logger.info("Starting CSV/GeoJSON migration to Supabase")
    migrate_doe_datasets(client)
    migrate_climate(client)
    migrate_products(client)
    migrate_wind(client)
    migrate_geothermal(client)
    migrate_geojson(client)
    logger.info("Migration complete")


if __name__ == "__main__":
    main()
