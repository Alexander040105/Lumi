import os
import time
import logging
import calendar
from dataclasses import dataclass
from datetime import date
from typing import Iterable
from pathlib import Path

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv
from supabase import Client, create_client

NASA_BASE_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
MIN_INGEST_YEAR = 2018
MAX_INGEST_YEAR = 2025
PARAMETERS = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "RHOA",
    "PRECTOTCORR",
    "WS10M",
    "ALLSKY_SFC_SW_DWN",
    "CLOUD_AMT",
    "PS",
]
MISSING_VALUES = {-999, -999.0, -9999, -9999.0}


def parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


@dataclass
class Config:
    supabase_url: str | None
    supabase_key: str | None
    start_year: int
    end_year: int
    rate_limit_seconds: float
    request_timeout: int
    only_missing: bool
    update_existing: bool
    batch_size: int
    max_retries: int
    backoff_factor: float
    nasa_date_formats: list[str]


def load_config() -> Config:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=repo_root / ".env", override=False)
    supabase_key = None
    for key_name in (
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_ANON_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
    ):
        value = os.getenv(key_name)
        if value:
            supabase_key = value
            break
    date_formats = "YYYY"
    return Config(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=supabase_key,
        start_year=MIN_INGEST_YEAR,
        end_year=MAX_INGEST_YEAR,
        rate_limit_seconds=float(os.getenv("NASA_RATE_LIMIT_SECONDS", "0.6")),
        request_timeout=int(os.getenv("NASA_REQUEST_TIMEOUT", "30")),
        only_missing=parse_bool(os.getenv("ONLY_MISSING"), True),
        update_existing=parse_bool(os.getenv("UPDATE_EXISTING"), True),
        batch_size=int(os.getenv("BATCH_SIZE", "500")),
        max_retries=int(os.getenv("NASA_MAX_RETRIES", "5")),
        backoff_factor=float(os.getenv("NASA_BACKOFF_FACTOR", "1.5")),
        nasa_date_formats=[fmt.strip().upper() for fmt in date_formats.split(",") if fmt.strip()],
    )


def build_supabase_client(config: Config) -> Client:
    if not config.supabase_url or not config.supabase_key:
        raise SystemExit("Missing SUPABASE_URL or SUPABASE_*_KEY in .env.")
    return create_client(config.supabase_url, config.supabase_key)


def configure_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def build_session(config: Config) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=config.max_retries,
        backoff_factor=config.backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def last_complete_year_month() -> tuple[int, int]:
    today = date.today()
    last_month = today.month - 1
    last_year = today.year
    if last_month < 1:
        last_month = 12
        last_year -= 1
    return last_year, last_month


def month_range(start_year: int, end_year: int) -> list[tuple[int, int]]:
    last_year, last_month = last_complete_year_month()
    months = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year > last_year or (year == last_year and month > last_month):
                break
            months.append((year, month))
    return months


def fetch_municipalities(supabase: Client, page_size: int = 1000) -> list[dict]:
    all_rows: list[dict] = []
    offset = 0
    while True:
        response = (
            supabase.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .not_.is_("lat", "null")
            .not_.is_("lon", "null")
            .order("municipality_id")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            break
        all_rows.extend(
            {
                "municipality_id": row["municipality_id"],
                "name": row["name"],
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
            }
            for row in rows
        )
        if len(rows) < page_size:
            break
        offset += page_size
    return all_rows


def fetch_existing_months(
    supabase: Client,
    municipality_id: int,
    page_size: int = 1000,
) -> set[tuple[int, int]]:
    existing: set[tuple[int, int]] = set()
    offset = 0
    while True:
        response = (
            supabase.table("municipality_climate_monthly")
            .select("year,month")
            .eq("municipality_id", municipality_id)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            break
        existing.update((row["year"], row["month"]) for row in rows)
        if len(rows) < page_size:
            break
        offset += page_size
    return existing


def find_missing_months(
    existing: set[tuple[int, int]],
    start_year: int,
    end_year: int,
) -> list[tuple[int, int]]:
    expected = month_range(start_year, end_year)
    return [(year, month) for (year, month) in expected if (year, month) not in existing]


def build_nasa_start_end(
    start_year: int,
    start_month: int,
    end_year: int,
    date_format: str,
) -> tuple[str, str]:
    if start_month < 1 or start_month > 12:
        raise ValueError(f"Invalid start_month: {start_month}")
    last_year, last_month = last_complete_year_month()
    if date_format == "YYYY":
        end_year = min(end_year, last_year)
        return (f"{start_year}", f"{end_year}")

    if end_year >= last_year:
        end_year = last_year
        end_month = last_month
    else:
        end_month = 12

    if date_format == "YYYYMM":
        return (
            f"{start_year}{start_month:02d}",
            f"{end_year}{end_month:02d}",
        )

    if date_format == "YYYYMMDD":
        start_day = 1
        end_day = calendar.monthrange(end_year, end_month)[1]
        return (
            f"{start_year}{start_month:02d}{start_day:02d}",
            f"{end_year}{end_month:02d}{end_day:02d}",
        )

    raise ValueError(f"Unsupported NASA_DATE_FORMATS entry: {date_format}")


def nasa_request(
    session: requests.Session,
    lat: float,
    lon: float,
    start_year: int,
    start_month: int,
    end_year: int,
    timeout: int,
    date_formats: list[str],
) -> dict:
    last_error: RuntimeError | None = None
    for date_format in date_formats:
        start_value, end_value = build_nasa_start_end(
            start_year,
            start_month,
            end_year,
            date_format,
        )
        params = {
            "parameters": ",".join(PARAMETERS),
            "community": "RE",
            "format": "JSON",
            "latitude": f"{lat:.6f}",
            "longitude": f"{lon:.6f}",
            "start": start_value,
            "end": end_value,
        }
        logging.debug(
            "NASA request format=%s start=%s end=%s lat=%s lon=%s",
            date_format,
            start_value,
            end_value,
            lat,
            lon,
        )
        resp = session.get(NASA_BASE_URL, params=params, timeout=timeout)
        if resp.ok:
            return resp.json()
        if resp.status_code == 422 and "date formatting" in resp.text:
            last_error = RuntimeError(
                f"NASA POWER error {resp.status_code}: {resp.text[:300]}"
            )
            continue
        raise RuntimeError(f"NASA POWER error {resp.status_code}: {resp.text[:300]}")

    if last_error:
        raise last_error
    raise RuntimeError("NASA POWER error: failed to build a valid date format")


def parse_nasa_payload(payload: dict) -> dict[str, dict[str, float | None]]:
    try:
        return payload["properties"]["parameter"]
    except KeyError as exc:
        raise RuntimeError("Unexpected NASA POWER response format") from exc


def coerce_value(value) -> float | None:
    if value in MISSING_VALUES or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_rows(
    municipality_id: int,
    parameter_map: dict[str, dict[str, float | None]],
    start_year: int,
    end_year: int,
) -> list[dict]:
    rows = []
    for year, month in month_range(start_year, end_year):
        key = f"{year}{month:02d}"
        row = {
            "municipality_id": municipality_id,
            "year": year,
            "month": month,
            "t2m": coerce_value(parameter_map.get("T2M", {}).get(key)),
            "t2m_max": coerce_value(parameter_map.get("T2M_MAX", {}).get(key)),
            "t2m_min": coerce_value(parameter_map.get("T2M_MIN", {}).get(key)),
            "rh2m": coerce_value(parameter_map.get("RH2M", {}).get(key)),
            "rhoa": coerce_value(parameter_map.get("RHOA", {}).get(key)),
            "prectotcorr": coerce_value(parameter_map.get("PRECTOTCORR", {}).get(key)),
            "ws10m": coerce_value(parameter_map.get("WS10M", {}).get(key)),
            "allsky_sfc_sw_dwn": coerce_value(parameter_map.get("ALLSKY_SFC_SW_DWN", {}).get(key)),
            "cloud_amt": coerce_value(parameter_map.get("CLOUD_AMT", {}).get(key)),
            "surface_pressure": coerce_value(parameter_map.get("PS", {}).get(key)),
        }
        rows.append(row)
    return rows


def build_rhoa_rows(rows: Iterable[dict]) -> list[dict]:
    return [
        {
            "municipality_id": row["municipality_id"],
            "year": row["year"],
            "month": row["month"],
            "rhoa": row.get("rhoa"),
        }
        for row in rows
    ]


def upsert_rows(supabase: Client, rows: Iterable[dict]) -> int:
    if not rows:
        return 0
    response = (
        supabase.table("municipality_climate_monthly")
        .upsert(list(rows), on_conflict="municipality_id,year,month")
        .execute()
    )
    if response.data is None:
        raise RuntimeError("Supabase upsert returned no data.")
    return len(response.data)


def sanitize_lat_lon(lat: float, lon: float) -> bool:
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def main() -> None:
    configure_logging()
    config = load_config()
    supabase = build_supabase_client(config)

    session = build_session(config)
    total_rows = 0

    municipalities = fetch_municipalities(supabase)
    logging.info("Municipalities to process: %s", len(municipalities))

    for index, municipality in enumerate(municipalities, start=1):
        municipality_id = municipality["municipality_id"]
        name = municipality["name"]
        lat = municipality["lat"]
        lon = municipality["lon"]

        if not sanitize_lat_lon(lat, lon):
            logging.warning(
                "Skipping municipality %s due to invalid lat/lon: %s, %s",
                municipality_id,
                lat,
                lon,
            )
            continue

        existing = fetch_existing_months(supabase, municipality_id)

        if config.only_missing:
            missing_months = find_missing_months(
                existing,
                config.start_year,
                config.end_year,
            )
            if not missing_months and not config.update_existing:
                logging.info(
                    "[%s/%s] %s already complete. Skipping.",
                    index,
                    len(municipalities),
                    name,
                )
                continue
            if config.update_existing:
                start_year = config.start_year
                start_month = 1
            else:
                start_year, start_month = min(missing_months)
        else:
            start_year = config.start_year
            start_month = 1

        try:
            payload = nasa_request(
                session,
                lat,
                lon,
                start_year,
                start_month,
                config.end_year,
                config.request_timeout,
                config.nasa_date_formats,
            )
        except Exception as exc:
            logging.error(
                "NASA request failed for municipality %s (%s): %s",
                municipality_id,
                name,
                exc,
            )
            continue

        parameter_map = parse_nasa_payload(payload)
        rows = build_rows(municipality_id, parameter_map, start_year, config.end_year)

        existing_set = set(existing)
        missing_rows = [
            row
            for row in rows
            if (row["year"], row["month"]) not in existing_set
        ]
        existing_rows = [
            row
            for row in rows
            if (row["year"], row["month"]) in existing_set
        ]
        rhoa_rows = build_rhoa_rows(existing_rows) if config.update_existing else []

        inserted = 0
        try:
            for i in range(0, len(missing_rows), config.batch_size):
                batch = missing_rows[i : i + config.batch_size]
                inserted += upsert_rows(supabase, batch)
            for i in range(0, len(rhoa_rows), config.batch_size):
                batch = rhoa_rows[i : i + config.batch_size]
                inserted += upsert_rows(supabase, batch)
        except Exception as exc:
            logging.error(
                "Insert failed for municipality %s (%s): %s",
                municipality_id,
                name,
                exc,
            )
            continue

        total_rows += inserted
        logging.info(
            "[%s/%s] %s processed, rows upserted: %s",
            index,
            len(municipalities),
            name,
            inserted,
        )
        time.sleep(config.rate_limit_seconds)

    logging.info("Done. Total rows upserted: %s", total_rows)


if __name__ == "__main__":
    main()