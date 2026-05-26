"""ETL: Enrich municipality_climate_monthly with elevation data.

Uses Open-Meteo Elevation API and Supabase API.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import asyncio

import httpx
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover - tqdm is optional
    tqdm = None


API_URL = "https://api.open-meteo.com/v1/elevation"
CACHE_DIRNAME = "elevation_cache"
FAILED_CSV_NAME = "failed_municipalities.csv"
JWT_PATTERN = re.compile(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$")


@dataclass(frozen=True)
class AppConfig:
    batch_size: int
    max_retries: int
    backoff_factor: float
    request_timeout: int
    rate_limit_per_second: float
    concurrency: int
    dry_run: bool
    cache_ttl_days: int
    resume_from_cache: bool
    use_async_requests: bool
    supabase_url: Optional[str]
    supabase_key: Optional[str]
    supabase_key_source: str


@dataclass(frozen=True)
class Municipality:
    municipality_id: int
    name: str
    lat: float
    lon: float


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)
        return json.dumps(payload)


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("elevation_etl")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def load_config() -> AppConfig:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=repo_root / ".env", override=False)

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = None
    supabase_key_source = ""
    key_candidates = (
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_ANON_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
    )
    for key_name in key_candidates:
        value = os.getenv(key_name)
        if value:
            supabase_key = value
            supabase_key_source = key_name
            break

    if not supabase_url or not supabase_key:
        missing = []
        if not supabase_url:
            missing.append("SUPABASE_URL")
        if not supabase_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY/SUPABASE_ANON_KEY/SUPABASE_KEY")
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")

    app_cfg = AppConfig(
        batch_size=int(os.getenv("BATCH_SIZE", "200")),
        max_retries=int(os.getenv("HTTP_MAX_RETRIES", "5")),
        backoff_factor=float(os.getenv("HTTP_BACKOFF_FACTOR", "0.5")),
        request_timeout=int(os.getenv("HTTP_TIMEOUT_SECONDS", "20")),
        rate_limit_per_second=float(os.getenv("RATE_LIMIT_PER_SECOND", "4")),
        concurrency=int(os.getenv("CONCURRENCY", "4")),
        dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        cache_ttl_days=int(os.getenv("CACHE_TTL_DAYS", "365")),
        resume_from_cache=os.getenv("RESUME_FROM_CACHE", "true").lower() == "true",
        use_async_requests=os.getenv("USE_ASYNC", "false").lower() == "true",
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        supabase_key_source=supabase_key_source,
    )

    return app_cfg


def create_http_session(cfg: AppConfig) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=cfg.max_retries,
        backoff_factor=cfg.backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class SupabaseResponse:
    def __init__(self, data: Any):
        self.data = data


class SupabaseRestQuery:
    def __init__(self, client: "SupabaseRestClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[tuple[str, str]] = []
        self._single = False

    def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select = columns
        return self

    def eq(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, value))
        return self

    def single(self) -> "SupabaseRestQuery":
        self._single = True
        return self

    def update(self, payload: dict[str, Any]) -> "SupabaseRestQuery":
        self._update_payload = payload
        return self

    def execute(self) -> SupabaseResponse:
        params: dict[str, str] = {"select": self._select}
        for column, value in self._filters:
            params[column] = f"eq.{value}"
        if self._single:
            params["limit"] = "1"

        url = f"{self._client.base_url}/rest/v1/{self._table}"
        if hasattr(self, "_update_payload"):
            response = self._client.http.patch(url, params=params, json=self._update_payload, headers=self._client.headers)
        else:
            response = self._client.http.get(url, params=params, headers=self._client.headers)
        response.raise_for_status()
        data = response.json()
        if self._single:
            data = data[0] if data else None
        return SupabaseResponse(data)


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Prefer": "return=representation",
        }
        self.http = httpx.Client(timeout=10.0)

    def table(self, table_name: str) -> SupabaseRestQuery:
        return SupabaseRestQuery(self, table_name)


def _is_jwt_key(key: str | None) -> bool:
    return bool(key) and JWT_PATTERN.match(key) is not None


def build_supabase_client(cfg: AppConfig) -> "Client | SupabaseRestClient":
    if not cfg.supabase_url or not cfg.supabase_key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY/SUPABASE_KEY.")
    try:
        from supabase import create_client
    except Exception as exc:
        raise RuntimeError("supabase-py is required for Supabase API mode") from exc

    if _is_jwt_key(cfg.supabase_key):
        try:
            return create_client(cfg.supabase_url, cfg.supabase_key)
        except Exception as exc:
            logging.getLogger("elevation_etl").warning(
                "Supabase JWT client failed; falling back to REST client",
                extra={"extra": {"error": str(exc)}},
            )
            return SupabaseRestClient(cfg.supabase_url, cfg.supabase_key)

    logging.getLogger("elevation_etl").warning(
        "Supabase key is not JWT; using REST client fallback for table queries only.",
    )
    return SupabaseRestClient(cfg.supabase_url, cfg.supabase_key)


def fetch_municipalities_supabase(client: "Client | SupabaseRestClient", page_size: int = 1000) -> List[Municipality]:
    all_rows: List[Municipality] = []
    offset = 0
    while True:
        response = (
            client.table("municipalities")
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
            Municipality(
                municipality_id=row["municipality_id"],
                name=row["name"],
                lat=float(row["lat"]),
                lon=float(row["lon"]),
            )
            for row in rows
        )
        if len(rows) < page_size:
            break
        offset += page_size
    return all_rows


def ensure_cache_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def cache_path(cache_dir: Path, municipality_id: int) -> Path:
    return cache_dir / f"{municipality_id}.json"


def cache_is_fresh(path: Path, ttl_days: int) -> bool:
    if not path.exists():
        return False
    age_seconds = time.time() - path.stat().st_mtime
    return age_seconds <= ttl_days * 86400


def read_cache(path: Path) -> Optional[float]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return float(data["elevation"])
    except Exception:
        return None


def write_cache(path: Path, elevation: float) -> None:
    path.write_text(json.dumps({"elevation": elevation}), encoding="utf-8")


def rate_limit(last_call: float, rate_limit_per_second: float) -> float:
    if rate_limit_per_second <= 0:
        return time.time()
    min_interval = 1.0 / rate_limit_per_second
    now = time.time()
    elapsed = now - last_call
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    return time.time()


def fetch_elevation(
    session: requests.Session,
    municipality: Municipality,
    cfg: AppConfig,
    logger: logging.Logger,
    cache_dir: Path,
) -> Tuple[Optional[float], Optional[str], bool]:
    cache_file = cache_path(cache_dir, municipality.municipality_id)
    if cfg.resume_from_cache and cache_is_fresh(cache_file, cfg.cache_ttl_days):
        cached = read_cache(cache_file)
        if cached is not None:
            return cached, None, True

    params = {"latitude": municipality.lat, "longitude": municipality.lon}
    try:
        resp = session.get(API_URL, params=params, timeout=cfg.request_timeout)
        if resp.status_code != 200:
            return None, f"http_{resp.status_code}", False
        payload = resp.json()
        elevation = payload.get("elevation", [None])[0]
        if elevation is None:
            return None, "missing_elevation", False
        elevation_value = float(elevation)
        write_cache(cache_file, elevation_value)
        return elevation_value, None, False
    except requests.RequestException as exc:
        logger.error(
            "Elevation API request failed",
            extra={"extra": {"municipality_id": municipality.municipality_id, "error": str(exc)}},
        )
        return None, "request_exception", False


class AsyncRateLimiter:
    def __init__(self, rate_limit_per_second: float) -> None:
        self._rate = rate_limit_per_second
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        if self._rate <= 0:
            return
        async with self._lock:
            min_interval = 1.0 / self._rate
            now = time.time()
            elapsed = now - self._last_call
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_call = time.time()


async def fetch_elevation_async(
    client: "httpx.AsyncClient",
    municipality: Municipality,
    cfg: AppConfig,
    logger: logging.Logger,
    cache_dir: Path,
    rate_limiter: AsyncRateLimiter,
) -> Tuple[Optional[float], Optional[str], bool]:
    cache_file = cache_path(cache_dir, municipality.municipality_id)
    if cfg.resume_from_cache and cache_is_fresh(cache_file, cfg.cache_ttl_days):
        cached = read_cache(cache_file)
        if cached is not None:
            return cached, None, True

    params = {"latitude": municipality.lat, "longitude": municipality.lon}
    for attempt in range(cfg.max_retries + 1):
        await rate_limiter.wait()
        try:
            resp = await client.get(API_URL, params=params, timeout=cfg.request_timeout)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < cfg.max_retries:
                await asyncio.sleep(cfg.backoff_factor * (2 ** attempt))
                continue
            if resp.status_code != 200:
                return None, f"http_{resp.status_code}", False
            payload = resp.json()
            elevation = payload.get("elevation", [None])[0]
            if elevation is None:
                return None, "missing_elevation", False
            elevation_value = float(elevation)
            write_cache(cache_file, elevation_value)
            return elevation_value, None, False
        except Exception as exc:
            if attempt < cfg.max_retries:
                await asyncio.sleep(cfg.backoff_factor * (2 ** attempt))
                continue
            logger.error(
                "Elevation API request failed",
                extra={"extra": {"municipality_id": municipality.municipality_id, "error": str(exc)}},
            )
            return None, "request_exception", False

    return None, "request_exception", False


def update_elevation_batch_supabase(
    client: "Client | SupabaseRestClient",
    updates: List[Tuple[float, int]],
    dry_run: bool,
    logger: logging.Logger,
) -> int:
    if not updates:
        return 0
    if dry_run:
        return len(updates)

    updated = 0
    for elevation, municipality_id in updates:
        response = (
            client.table("municipality_climate_monthly")
            .update({"elevation": elevation})
            .eq("municipality_id", municipality_id)
            .execute()
        )
        if response.data is None:
            logger.error(
                "Supabase update returned no data",
                extra={"extra": {"municipality_id": municipality_id}},
            )
            continue
        updated += 1
    return updated


def save_failed_csv(path: Path, failed: List[Tuple[Municipality, str]]) -> None:
    if not failed:
        return
    header = "municipality_id,name,lat,lon,reason\n"
    rows = [
        f"{m.municipality_id},{m.name},{m.lat},{m.lon},{reason}\n"
        for m, reason in failed
    ]
    path.write_text(header + "".join(rows), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enrich climate monthly data with elevation.")
    parser.add_argument("--batch-size", type=int, default=None, help="Update batch size.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write updates.")
    parser.add_argument("--resume-from-cache", action="store_true", help="Use cached API data.")
    parser.add_argument("--no-cache", action="store_true", help="Disable cache usage.")
    parser.add_argument("--rate", type=float, default=None, help="Requests per second.")
    parser.add_argument("--limit", type=int, default=None, help="Limit municipalities for testing.")
    parser.add_argument("--cache-ttl-days", type=int, default=None, help="Cache TTL in days.")
    parser.add_argument("--async-requests", action="store_true", help="Use async HTTP requests.")
    return parser


def process_sync_supabase(
    client: "Client",
    municipalities: List[Municipality],
    cfg: AppConfig,
    logger: logging.Logger,
    cache_dir: Path,
) -> Tuple[int, int, int, List[Tuple[Municipality, str]]]:
    total_updated = 0
    total_failed = 0
    total_cached = 0
    failed_list: List[Tuple[Municipality, str]] = []

    iterator: Iterable[Municipality]
    if tqdm:
        iterator = tqdm(municipalities, desc="Municipalities")
    else:
        iterator = municipalities

    session = create_http_session(cfg)
    last_call = 0.0
    pending_updates: List[Tuple[float, int]] = []

    for municipality in iterator:
        last_call = rate_limit(last_call, cfg.rate_limit_per_second)
        elevation, error, cached_hit = fetch_elevation(session, municipality, cfg, logger, cache_dir)
        if cached_hit:
            total_cached += 1
        if elevation is None:
            total_failed += 1
            failed_list.append((municipality, error or "unknown"))
            continue

        pending_updates.append((elevation, municipality.municipality_id))
        if len(pending_updates) >= cfg.batch_size:
            updated = update_elevation_batch_supabase(client, pending_updates, cfg.dry_run, logger)
            total_updated += updated
            pending_updates.clear()

    if pending_updates:
        updated = update_elevation_batch_supabase(client, pending_updates, cfg.dry_run, logger)
        total_updated += updated

    return total_updated, total_failed, total_cached, failed_list


def main() -> int:
    logger = setup_logging()
    app_cfg = load_config()

    parser = build_arg_parser()
    args = parser.parse_args()

    app_cfg = AppConfig(
        batch_size=args.batch_size or app_cfg.batch_size,
        max_retries=app_cfg.max_retries,
        backoff_factor=app_cfg.backoff_factor,
        request_timeout=app_cfg.request_timeout,
        rate_limit_per_second=args.rate or app_cfg.rate_limit_per_second,
        concurrency=app_cfg.concurrency,
        dry_run=args.dry_run or app_cfg.dry_run,
        cache_ttl_days=args.cache_ttl_days or app_cfg.cache_ttl_days,
        resume_from_cache=(not args.no_cache) and (args.resume_from_cache or app_cfg.resume_from_cache),
        use_async_requests=args.async_requests or app_cfg.use_async_requests,
        supabase_url=app_cfg.supabase_url,
        supabase_key=app_cfg.supabase_key,
        supabase_key_source=app_cfg.supabase_key_source,
    )

    cache_dir = Path(CACHE_DIRNAME)
    ensure_cache_dir(cache_dir)
    failed_csv = cache_dir / FAILED_CSV_NAME

    total_updated = 0
    total_failed = 0
    total_cached = 0
    total_processed = 0
    failed_list: List[Tuple[Municipality, str]] = []

    logger.info(
        "Using Supabase API credentials",
        extra={"extra": {"key_source": app_cfg.supabase_key_source}},
    )
    client = build_supabase_client(app_cfg)
    municipalities = fetch_municipalities_supabase(client)
    if args.limit:
        municipalities = municipalities[: args.limit]
    total_processed = len(municipalities)
    total_updated, total_failed, total_cached, failed_list = process_sync_supabase(
        client, municipalities, app_cfg, logger, cache_dir
    )

    save_failed_csv(failed_csv, failed_list)

    logger.info(
        "ETL completed",
        extra={
            "extra": {
                "processed": total_processed,
                "updated": total_updated,
                "cached": total_cached,
                "failed": total_failed,
                "dry_run": app_cfg.dry_run,
            }
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
