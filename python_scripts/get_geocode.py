import os
import time
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from supabase import Client, create_client

USER_AGENT = "lumi-geocoder/1.0 (alexanderjonsolis0401@gmail.com)"
RATE_LIMIT_SECONDS = 1.1  # Nominatim requires >= 1s between requests

def load_env_file(path):
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

load_env_file(".env")

NOMINATIM_EMAIL = os.environ.get("NOMINATIM_EMAIL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_JWT_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_JWT_ANON_KEY")
    or os.environ.get("SUPABASE_ANON_KEY")
    or os.environ.get("SUPABASE_KEY")
)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("Missing SUPABASE_URL or SUPABASE_KEY.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Session with automatic retry on 429/5xx
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=2,          # waits 2, 4, 8, 16, 32s between retries
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,     # we'll handle status manually
)
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))


def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:
    if query in cache:
        return cache[query]

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    if NOMINATIM_EMAIL:
        params["email"] = NOMINATIM_EMAIL
        headers["From"] = NOMINATIM_EMAIL

    for attempt in range(1, 4):  # up to 3 manual retries for 429
        resp = session.get(url, params=params, headers=headers, timeout=20)

        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 60))
            print(f"  [429] Rate limited. Waiting {wait}s before retry {attempt}/3...")
            time.sleep(wait)
            continue

        if not resp.ok:
            print(f"  [ERROR] HTTP {resp.status_code} for query: {query!r}")
            print(f"          Response: {resp.text[:200]}")
            cache[query] = (None, None)
            return None, None

        data = resp.json()
        if not data:
            print(f"  [WARN] No results for: {query!r}")
            cache[query] = (None, None)
            return None, None

        lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        cache[query] = (lat, lon)
        return lat, lon

    print(f"  [FAIL] Exhausted retries for: {query!r}")
    cache[query] = (None, None)
    return None, None


def update_coords(table: str, id_field: str, id_value: int, lat, lon):
    if lat is None or lon is None:
        return
    supabase.table(table).update({"lat": lat, "lon": lon}).eq(id_field, id_value).execute()


def fetch_missing_ids(table: str, id_field: str, page_size: int = 1000) -> set[int]:
    missing = set()
    offset = 0
    while True:
        response = (
            supabase.table(table)
            .select(id_field)
            .or_("lat.is.null,lon.is.null")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            break
        for row in rows:
            missing.add(int(row[id_field]))
        if len(rows) < page_size:
            break
        offset += page_size
    return missing


# Load CSVs
regions       = pd.read_csv("data/regionalData/regions.csv")
provinces     = pd.read_csv("data/regionalData/provinces.csv").rename(columns={"Name": "name"})
municipalities = pd.read_csv("data/regionalData/municipalities.csv")
barangays     = pd.read_csv("data/regionalData/barangays.csv")

region_by_id = regions.set_index("region_id")
prov_by_id   = provinces.set_index("province_id")
mun_by_id    = municipalities.set_index("municipality_id")

cache = {}

missing_region_ids = fetch_missing_ids("regions", "region_id")
missing_province_ids = fetch_missing_ids("provinces", "province_id")
missing_municipality_ids = fetch_missing_ids("municipalities", "municipality_id")
missing_barangay_ids = fetch_missing_ids("barangays", "barangay_id")

print("=== Geocoding Regions ===")
for _, row in regions.iterrows():
    if int(row["region_id"]) not in missing_region_ids:
        continue
    query = f"{row['name']}, Philippines"
    print(f"  {query}")
    lat, lon = geocode(query, cache)
    update_coords("regions", "region_id", int(row["region_id"]), lat, lon)
    time.sleep(RATE_LIMIT_SECONDS)

print("=== Geocoding Provinces ===")
for _, row in provinces.iterrows():
    if int(row["province_id"]) not in missing_province_ids:
        continue
    region = region_by_id.loc[row["region_id"]]
    query = f"{row['name']}, {region['name']}, Philippines"
    print(f"  {query}")
    lat, lon = geocode(query, cache)
    update_coords("provinces", "province_id", int(row["province_id"]), lat, lon)
    time.sleep(RATE_LIMIT_SECONDS)

print("=== Geocoding Municipalities ===")
for _, row in municipalities.iterrows():
    if int(row["municipality_id"]) not in missing_municipality_ids:
        continue
    prov = prov_by_id.loc[row["province_id"]]
    query = f"{row['name']}, {prov['name']}, Philippines"
    print(f"  {query}")
    lat, lon = geocode(query, cache)
    update_coords("municipalities", "municipality_id", int(row["municipality_id"]), lat, lon)
    time.sleep(RATE_LIMIT_SECONDS)

print("=== Geocoding Barangays ===")
for _, row in barangays.iterrows():
    if int(row["barangay_id"]) not in missing_barangay_ids:
        continue
    mun  = mun_by_id.loc[row["municipality_id"]]
    prov = prov_by_id.loc[mun["province_id"]]
    query = f"{row['name']}, {mun['name']}, {prov['name']}, Philippines"
    print(f"  {query}")
    lat, lon = geocode(query, cache)
    update_coords("barangays", "barangay_id", int(row["barangay_id"]), lat, lon)
    time.sleep(RATE_LIMIT_SECONDS)

print("Done updating coordinates.")