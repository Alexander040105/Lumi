# Geospatial / Location Reference
## `python_scripts/get_geocode.py`

**File:** `python_scripts/get_geocode.py`

**Summary:** Source file `python_scripts/get_geocode.py`.

### `load_env_file`

- **File:** `python_scripts/get_geocode.py`
- **Lines:** `12-21`
- **Signature:** `def load_env_file(path):`
- **Purpose:** Loads env file.

**Code:**
```python
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
```

**Explanation:** It accepts `path`. See the code below for the full implementation. Key calls include `isfile()`, `open()`, `strip()`, `split()`, `setdefault()`.

### `geocode`

- **File:** `python_scripts/get_geocode.py`
- **Lines:** `52-90`
- **Signature:** `def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:`
- **Purpose:** Handles geocode.

**Code:**
```python
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
```

**Explanation:** It accepts `query`, `cache` and returns `tuple[float | None, float | None]`. See the code below for the full implementation. Key calls include `range()`, `get()`, `json()`, `int()`, `sleep()`.

### `update_coords`

- **File:** `python_scripts/get_geocode.py`
- **Lines:** `93-96`
- **Signature:** `def update_coords(table: str, id_field: str, id_value: int, lat, lon):`
- **Purpose:** Updates coords.

**Code:**
```python
def update_coords(table: str, id_field: str, id_value: int, lat, lon):
    if lat is None or lon is None:
        return
    supabase.table(table).update({"lat": lat, "lon": lon}).eq(id_field, id_value).execute()
```

**Explanation:** It accepts `table`, `id_field`, `id_value`, `lat`, `lon`. See the code below for the full implementation. Key calls include `execute()`, `eq()`, `update()`, `table()`.

### `fetch_missing_ids`

- **File:** `python_scripts/get_geocode.py`
- **Lines:** `99-118`
- **Signature:** `def fetch_missing_ids(table: str, id_field: str, page_size: int = 1000) -> set[int]:`
- **Purpose:** Fetches missing ids.

**Code:**
```python
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
```

**Explanation:** It accepts `table`, `id_field`, `page_size` and returns `set[int]`. See the code below for the full implementation. Key calls include `set()`, `execute()`, `add()`, `len()`, `range()`.


## `python_scripts/geocode_missing_coords.py`

**File:** `python_scripts/geocode_missing_coords.py`

**Summary:** Geocode missing lat/lon for municipalities using Nominatim + direct Supabase REST API.

### `load_env_file`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `27-36`
- **Signature:** `def load_env_file(path: Path) -> None:`
- **Purpose:** Loads env file.

**Code:**
```python
def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
```

**Explanation:** It accepts `path` and returns `None`. See the code below for the full implementation. Key calls include `is_file()`, `open()`, `strip()`, `split()`, `setdefault()`.

### `_rest_get`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `72-76`
- **Signature:** `def _rest_get(table: str, params: dict) -> list[dict]:`
- **Purpose:** Handles  rest get.

**Code:**
```python
def _rest_get(table: str, params: dict) -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = httpx.get(url, params=params, headers=HEADERS, timeout=30.0)
    resp.raise_for_status()
    return resp.json() or []
```

**Explanation:** It accepts `table`, `params` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`.

### `_rest_patch`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `79-83`
- **Signature:** `def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:`
- **Purpose:** Handles  rest patch.

**Code:**
```python
def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}?{pk_col}=eq.{pk_val}"
    resp = httpx.patch(url, json=data, headers={**HEADERS, "Prefer": "return=minimal"}, timeout=30.0)
    if resp.status_code not in (200, 204):
        logger.warning("PATCH failed for %s.%s=%s: %s %s", table, pk_col, pk_val, resp.status_code, resp.text[:200])
```

**Explanation:** It accepts `table`, `pk_col`, `pk_val`, `data` and returns `None`. See the code below for the full implementation. Key calls include `patch()`, `warning()`.

### `fetch_missing_ids`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `86-104`
- **Signature:** `def fetch_missing_ids(table: str, id_field: str) -> list[int]:`
- **Purpose:** Fetches missing ids.

**Code:**
```python
def fetch_missing_ids(table: str, id_field: str) -> list[int]:
    missing: list[int] = []
    offset = 0
    while True:
        params = {
            "select": id_field,
            "or": "(lat.is.null,lon.is.null)",
            "offset": str(offset),
            "limit": str(PAGE_SIZE),
        }
        rows = _rest_get(table, params)
        if not rows:
            break
        for row in rows:
            missing.append(int(row[id_field]))
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return missing
```

**Explanation:** It accepts `table`, `id_field` and returns `list[int]`. See the code below for the full implementation. Key calls include `_rest_get()`, `str()`, `append()`, `len()`, `int()`.

### `geocode`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `107-149`
- **Signature:** `def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:`
- **Purpose:** Handles geocode.

**Code:**
```python
def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:
    if query in cache:
        return cache[query]

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    if NOMINATIM_EMAIL:
        params["email"] = NOMINATIM_EMAIL
        headers["From"] = NOMINATIM_EMAIL

    for attempt in range(1, 4):
        try:
            resp = httpx.get(url, params=params, headers=headers, timeout=20.0)
        except Exception as exc:
            logger.warning("HTTP error for %r (attempt %d): %s", query, attempt, exc)
            time.sleep(5)
            continue

        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 60))
            logger.warning("Rate limited for %r. Waiting %ds...", query, wait)
            time.sleep(wait)
            continue

        if not resp.is_success:
            logger.warning("HTTP %s for %r: %s", resp.status_code, query, resp.text[:200])
            cache[query] = (None, None)
            return None, None

        data = resp.json()
        if not data:
            logger.warning("No results for: %r", query)
            cache[query] = (None, None)
            return None, None

        lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        cache[query] = (lat, lon)
        return lat, lon

    logger.error("Exhausted retries for: %r", query)
    cache[query] = (None, None)
    return None, None
```

**Explanation:** It accepts `query`, `cache` and returns `tuple[float | None, float | None]`. See the code below for the full implementation. Key calls include `range()`, `json()`, `get()`, `int()`, `warning()`.

### `update_coords`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `152-155`
- **Signature:** `def update_coords(table: str, id_field: str, id_value: int, lat, lon) -> None:`
- **Purpose:** Updates coords.

**Code:**
```python
def update_coords(table: str, id_field: str, id_value: int, lat, lon) -> None:
    if lat is None or lon is None:
        return
    _rest_patch(table, id_field, id_value, {"lat": lat, "lon": lon})
```

**Explanation:** It accepts `table`, `id_field`, `id_value`, `lat`, `lon` and returns `None`. See the code below for the full implementation. Key calls include `_rest_patch()`.

### `main`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `158-214`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    # Load CSVs
    csv_dir = Path("regionalData")
    regions = pd.read_csv(csv_dir / "regions.csv")
    provinces = pd.read_csv(csv_dir / "provinces.csv").rename(columns={"Name": "name"})
    municipalities = pd.read_csv(csv_dir / "municipalities.csv")

    region_by_id = regions.set_index("region_id")
    prov_by_id = provinces.set_index("province_id")
    mun_by_id = municipalities.set_index("municipality_id")

    cache: dict[str, tuple] = {}

    # --- Regions ---
    missing_region_ids = fetch_missing_ids("regions", "region_id")
    logger.info("Regions missing coords: %d", len(missing_region_ids))
    for _, row in regions.iterrows():
        if int(row["region_id"]) not in missing_region_ids:
            continue
        query = f"{row['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("regions", "region_id", int(row["region_id"]), lat, lon)
        time.sleep(RATE_LIMIT_SECONDS)

    # --- Provinces ---
    missing_province_ids = fetch_missing_ids("provinces", "province_id")
    logger.info("Provinces missing coords: %d", len(missing_province_ids))
    for _, row in provinces.iterrows():
        if int(row["province_id"]) not in missing_province_ids:
            continue
        region = region_by_id.loc[row["region_id"]]
        query = f"{row['name']}, {region['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("provinces", "province_id", int(row["province_id"]), lat, lon)
        time.sleep(RATE_LIMIT_SECONDS)

    # --- Municipalities ---
    missing_muni_ids = fetch_missing_ids("municipalities", "municipality_id")
    logger.info("Municipalities missing coords: %d", len(missing_muni_ids))
    total = len(missing_muni_ids)
    for idx, row in municipalities.iterrows():
        mid = int(row["municipality_id"])
        if mid not in missing_muni_ids:
            continue
        prov = prov_by_id.loc[row["province_id"]]
        query = f"{row['name']}, {prov['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("municipalities", "municipality_id", mid, lat, lon)
        if (idx + 1) % 50 == 0 or idx == total - 1:
            logger.info("Geocoded %d/%d municipalities", idx + 1, total)
        time.sleep(RATE_LIMIT_SECONDS)

    logger.info("Done updating coordinates.")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `Path()`, `read_csv()`, `rename()`, `set_index()`, `fetch_missing_ids()`.


## `python_scripts/fill_missing_coords_from_geojson.py`

**File:** `python_scripts/fill_missing_coords_from_geojson.py`

**Summary:** Fill missing municipality lat/lon from Philippine GeoJSON centroids.

### `_rest_get`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `59-63`
- **Signature:** `def _rest_get(table: str, params: dict) -> list[dict]:`
- **Purpose:** Handles  rest get.

**Code:**
```python
def _rest_get(table: str, params: dict) -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = httpx.get(url, params=params, headers=HEADERS, timeout=30.0)
    resp.raise_for_status()
    return resp.json() or []
```

**Explanation:** It accepts `table`, `params` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`.

### `_rest_patch`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `66-70`
- **Signature:** `def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:`
- **Purpose:** Handles  rest patch.

**Code:**
```python
def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}?{pk_col}=eq.{pk_val}"
    resp = httpx.patch(url, json=data, headers={**HEADERS, "Prefer": "return=minimal"}, timeout=30.0)
    if resp.status_code not in (200, 204):
        logger.warning("PATCH failed for %s.%s=%s: %s %s", table, pk_col, pk_val, resp.status_code, resp.text[:200])
```

**Explanation:** It accepts `table`, `pk_col`, `pk_val`, `data` and returns `None`. See the code below for the full implementation. Key calls include `patch()`, `warning()`.

### `normalize_name`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `73-84`
- **Signature:** `def normalize_name(name: str) -> str:`
- **Purpose:** Normalize municipality name for matching.

**Code:**
```python
def normalize_name(name: str) -> str:
    """Normalize municipality name for matching."""
    return (
        name.upper()
        .replace(" CITY", "")
        .replace(" (POB.)", "")
        .replace(" (CAPITAL)", "")
        .replace(" (", " ")
        .replace(")", " ")
        .replace(".", "")
        .strip()
    )
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `replace()`, `upper()`.

### `compute_centroids`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `87-109`
- **Signature:** `def compute_centroids(geojson_path: Path) -> dict[str, tuple[float, float]]:`
- **Purpose:** Compute centroid lat/lon for each municipality in GeoJSON.

**Code:**
```python
def compute_centroids(geojson_path: Path) -> dict[str, tuple[float, float]]:
    """Compute centroid lat/lon for each municipality in GeoJSON."""
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    centroids: dict[str, tuple[float, float]] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        name = props.get("adm3_en", "").strip()
        if not name:
            continue
        geom = feat.get("geometry")
        if not geom:
            continue
        try:
            poly = shape(geom)
            centroid = poly.centroid
            centroids[normalize_name(name)] = (round(centroid.y, 6), round(centroid.x, 6))
        except Exception:
            continue

    logger.info("Computed %d centroids from GeoJSON", len(centroids))
    return centroids
```

**Explanation:** It accepts `geojson_path` and returns `dict[str, tuple[float, float]]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `strip()`, `shape()`.

### `main`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `112-184`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Missing SUPABASE_URL or SUPABASE_KEY")
        return 1

    if not GEOJSON_PATH.exists():
        logger.error("GeoJSON not found: %s", GEOJSON_PATH)
        return 1

    # 1. Load GeoJSON centroids
    logger.info("Loading GeoJSON centroids...")
    centroids = compute_centroids(GEOJSON_PATH)

    # 2. Load municipalities CSV for name mapping
    logger.info("Loading municipalities CSV...")
    municipalities = pd.read_csv(CSV_MUNI_PATH)
    provinces = pd.read_csv(CSV_PROV_PATH).rename(columns={"Name": "name"})
    prov_map = dict(zip(provinces["province_id"], provinces["name"]))

    # 3. Fetch missing municipality IDs from Supabase
    logger.info("Fetching municipalities missing lat/lon...")
    missing_ids: list[int] = []
    offset = 0
    while True:
        params = {
            "select": "municipality_id,name",
            "or": "(lat.is.null,lon.is.null)",
            "offset": str(offset),
            "limit": "1000",
        }
        rows = _rest_get("municipalities", params)
        if not rows:
            break
        for row in rows:
            missing_ids.append(int(row["municipality_id"]))
        if len(rows) < 1000:
            break
        offset += 1000

    logger.info("Found %d municipalities missing coordinates", len(missing_ids))

    # 4. Build name -> (lat, lon) map from GeoJSON centroids
    updated = 0
    failed = 0
    for _, row in municipalities.iterrows():
        mid = int(row["municipality_id"])
        if mid not in missing_ids:
            continue

        name = str(row["name"])
        norm = normalize_name(name)

        # Try exact normalized match first
        coords = centroids.get(norm)

        # If no match, try without parenthetical suffix
        if not coords and "(" in norm:
            alt = norm.split("(")[0].strip()
            coords = centroids.get(alt)

        if not coords:
            logger.warning("No GeoJSON match for: %s (normalized: %s)", name, norm)
            failed += 1
            continue

        lat, lon = coords
        _rest_patch("municipalities", "municipality_id", mid, {"lat": lat, "lon": lon})
        updated += 1
        if updated % 100 == 0:
            logger.info("Updated %d/%d municipalities", updated, len(missing_ids))

    logger.info("Done. Updated: %d, Failed: %d, Total missing: %d", updated, failed, len(missing_ids))
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `error()`, `exists()`, `info()`, `compute_centroids()`, `read_csv()`.


## `python_scripts/municipality_climate_analysis.py`

**File:** `python_scripts/municipality_climate_analysis.py`

**Summary:** Source file `python_scripts/municipality_climate_analysis.py`.

### `load_env`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `49-73`
- **Signature:** `def load_env() -> Dict[str, str]:`
- **Purpose:** Load required environment variables.

**Code:**
```python
def load_env() -> Dict[str, str]:
    """Load required environment variables."""
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=repo_root / ".env", override=False)
    print(f"Loaded environment variables from: {repo_root / '.env'}")
    supabase_url = os.getenv("SUPABASE_URL")
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

    if not supabase_url or not supabase_key:
        raise EnvironmentError(
            "Missing SUPABASE_URL or SUPABASE_KEY. Add them to your .env file."
        )

    return {"SUPABASE_URL": supabase_url, "SUPABASE_KEY": supabase_key}
```

**Explanation:** It accepts zero arguments and returns `Dict[str, str]`. See the code below for the full implementation. Key calls include `resolve()`, `Path()`, `load_dotenv()`, `getenv()`, `EnvironmentError()`.

### `is_jwt_key`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `76-77`
- **Signature:** `def is_jwt_key(key: str | None) -> bool:`
- **Purpose:** Handles is jwt key.

**Code:**
```python
def is_jwt_key(key: str | None) -> bool:
    return bool(key) and JWT_PATTERN.match(key) is not None
```

**Explanation:** It accepts `key` and returns `bool`. See the code below for the full implementation. Key calls include `bool()`, `match()`.

### `SupabaseRestQuery.__init__`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `81-85`
- **Signature:** `def __init__(self, client: "SupabaseRestClient", table: str):`
- **Purpose:** Method of `SupabaseRestQuery` that handles   init  .

**Code:**
```python
def __init__(self, client: "SupabaseRestClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[tuple[str, str]] = []
```

**Explanation:** It accepts `client`, `table`. See the code below for the full implementation.

### `SupabaseRestQuery.select`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `87-89`
- **Signature:** `def select(self, columns: str = "*") -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles select.

**Code:**
```python
def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select = columns
        return self
```

**Explanation:** It accepts `columns` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.range`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `91-93`
- **Signature:** `def range(self, start: int, end: int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles range.

**Code:**
```python
def range(self, start: int, end: int) -> "SupabaseRestQuery":
        self._range = (start, end)
        return self
```

**Explanation:** It accepts `start`, `end` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.execute`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `95-104`
- **Signature:** `def execute(self):`
- **Purpose:** Method of `SupabaseRestQuery` that handles execute.

**Code:**
```python
def execute(self):
        params: dict[str, str] = {"select": self._select}
        headers = dict(self._client.headers)
        if hasattr(self, "_range"):
            start, end = self._range
            headers["Range"] = f"{start}-{end}"
        url = f"{self._client.base_url}/rest/v1/{self._table}"
        response = self._client.http.get(url, params=params, headers=headers)
        response.raise_for_status()
        return type("Resp", (), {"data": response.json()})
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `dict()`, `hasattr()`, `get()`, `raise_for_status()`, `type()`.

### `SupabaseRestClient.__init__`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `108-114`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=10.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.table`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `116-117`
- **Signature:** `def table(self, table_name: str) -> SupabaseRestQuery:`
- **Purpose:** Method of `SupabaseRestClient` that handles table.

**Code:**
```python
def table(self, table_name: str) -> SupabaseRestQuery:
        return SupabaseRestQuery(self, table_name)
```

**Explanation:** It accepts `table_name` and returns `SupabaseRestQuery`. See the code below for the full implementation. Key calls include `SupabaseRestQuery()`.

### `get_supabase_client`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `123-131`
- **Signature:** `def get_supabase_client() -> Client:`
- **Purpose:** Initialize and return a Supabase client.

**Code:**
```python
def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    env = load_env()
    if is_jwt_key(env["SUPABASE_KEY"]):
        try:
            return create_client(env["SUPABASE_URL"], env["SUPABASE_KEY"])
        except Exception:
            return SupabaseRestClient(env["SUPABASE_URL"], env["SUPABASE_KEY"])
    return SupabaseRestClient(env["SUPABASE_URL"], env["SUPABASE_KEY"])
```

**Explanation:** It accepts zero arguments and returns `Client`. See the code below for the full implementation. Key calls include `load_env()`, `is_jwt_key()`, `create_client()`, `SupabaseRestClient()`.

### `fetch_all_rows`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `137-170`
- **Signature:** `def fetch_all_rows(supabase: Client, table_name: str) -> List[Dict[str, Any]]:`
- **Purpose:** Fetch all rows from a Supabase table using pagination.

**Code:**
```python
def fetch_all_rows(supabase: Client, table_name: str) -> List[Dict[str, Any]]:
    """Fetch all rows from a Supabase table using pagination."""
    all_rows: List[Dict[str, Any]] = []
    start = 0

    while True:
        end = start + PAGE_SIZE - 1
        try:
            response = (
                supabase
                .table(table_name)
                .select("*")
                .range(start, end)
                .execute()
            )
        except Exception as exc:
            raise RuntimeError(f"Supabase API request failed: {exc}") from exc

        data = response.data if response and response.data else []

        if not data:
            break

        all_rows.extend(data)
        start += PAGE_SIZE

        # Safety guard against unexpected pagination issues
        if start > 10_000_000:
            raise RuntimeError("Pagination exceeded safe limit. Check table size or API response.")

    if not all_rows:
        raise ValueError("No data returned from Supabase. Check table name and credentials.")

    return all_rows
```

**Explanation:** It accepts `supabase`, `table_name` and returns `List[Dict[str, Any]]`. See the code below for the full implementation. Key calls include `extend()`, `execute()`, `RuntimeError()`, `range()`, `select()`.

### `validate_dataframe`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `176-183`
- **Signature:** `def validate_dataframe(df: pd.DataFrame) -> None:`
- **Purpose:** Basic validation checks for expected columns and non-empty data.

**Code:**
```python
def validate_dataframe(df: pd.DataFrame) -> None:
    """Basic validation checks for expected columns and non-empty data."""
    if df.empty:
        raise ValueError("DataFrame is empty. No data to analyze.")

    missing_cols = [col for col in NASA_POWER_COLUMNS + ["municipality_id"] if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected columns: {missing_cols}")
```

**Explanation:** It accepts `df` and returns `None`. See the code below for the full implementation. Key calls include `ValueError()`.

### `summarize_missing_values`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `189-196`
- **Signature:** `def summarize_missing_values(df: pd.DataFrame) -> pd.DataFrame:`
- **Purpose:** Return a summary of missing values by column.

**Code:**
```python
def summarize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary of missing values by column."""
    missing_counts = df.isna().sum().sort_values(ascending=False)
    missing_percent = (missing_counts / len(df) * 100).round(2)
    return pd.DataFrame({
        "missing_count": missing_counts,
        "missing_percent": missing_percent
    })
```

**Explanation:** It accepts `df` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `sort_values()`, `sum()`, `isna()`, `round()`, `len()`.

### `descriptive_statistics`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `199-201`
- **Signature:** `def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:`
- **Purpose:** Return descriptive statistics for numeric NASA POWER columns.

**Code:**
```python
def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric NASA POWER columns."""
    return df[NASA_POWER_COLUMNS].describe().T
```

**Explanation:** It accepts `df` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `describe()`.

### `plot_histogram`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `207-215`
- **Signature:** `def plot_histogram(df: pd.DataFrame, column: str) -> None:`
- **Purpose:** Plot a histogram for a single column.

**Code:**
```python
def plot_histogram(df: pd.DataFrame, column: str) -> None:
    """Plot a histogram for a single column."""
    plt.figure(figsize=(8, 4))
    plt.hist(df[column].dropna(), bins=30, color="#2E86AB", alpha=0.85)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()
```

**Explanation:** It accepts `df`, `column` and returns `None`. See the code below for the full implementation. Key calls include `figure()`, `hist()`, `dropna()`, `title()`, `xlabel()`.

### `plot_boxplot`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `218-225`
- **Signature:** `def plot_boxplot(df: pd.DataFrame, column: str) -> None:`
- **Purpose:** Plot a boxplot for a single column.

**Code:**
```python
def plot_boxplot(df: pd.DataFrame, column: str) -> None:
    """Plot a boxplot for a single column."""
    plt.figure(figsize=(6, 4))
    plt.boxplot(df[column].dropna(), vert=True)
    plt.title(f"Boxplot of {column}")
    plt.ylabel(column)
    plt.tight_layout()
    plt.show()
```

**Explanation:** It accepts `df`, `column` and returns `None`. See the code below for the full implementation. Key calls include `figure()`, `boxplot()`, `dropna()`, `title()`, `ylabel()`.

### `plot_correlation_heatmap`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `228-238`
- **Signature:** `def plot_correlation_heatmap(df: pd.DataFrame) -> None:`
- **Purpose:** Plot a correlation heatmap using matplotlib.

**Code:**
```python
def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    """Plot a correlation heatmap using matplotlib."""
    corr = df[NASA_POWER_COLUMNS].corr()
    plt.figure(figsize=(10, 8))
    plt.imshow(corr, cmap="coolwarm", interpolation="nearest")
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Heatmap: NASA POWER Parameters")
    plt.tight_layout()
    plt.show()
```

**Explanation:** It accepts `df` and returns `None`. See the code below for the full implementation. Key calls include `corr()`, `figure()`, `imshow()`, `colorbar()`, `xticks()`.

### `plot_municipality_distribution`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `241-253`
- **Signature:** `def plot_municipality_distribution(df: pd.DataFrame, column: str, sample_size: int = 10) -> None:`
- **Purpose:** Plot a distribution of values for a subset of municipalities.

**Code:**
```python
def plot_municipality_distribution(df: pd.DataFrame, column: str, sample_size: int = 10) -> None:
    """Plot a distribution of values for a subset of municipalities."""
    sample_ids = df["municipality_id"].dropna().unique()[:sample_size]
    plt.figure(figsize=(10, 5))
    for municipality_id in sample_ids:
        subset = df[df["municipality_id"] == municipality_id][column].dropna()
        plt.plot(subset.values, label=f"{municipality_id}")
    plt.title(f"{column} Distribution (Sample Municipalities)")
    plt.xlabel("Record Index")
    plt.ylabel(column)
    plt.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    plt.show()
```

**Explanation:** It accepts `df`, `column`, `sample_size` and returns `None`. See the code below for the full implementation. Key calls include `unique()`, `dropna()`, `figure()`, `plot()`, `title()`.

### `compute_all_time_averages`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `259-292`
- **Signature:** `def compute_all_time_averages(df: pd.DataFrame) -> pd.DataFrame:`
- **Purpose:** Compute all-time averages per municipality for NASA POWER parameters.

**Code:**
```python
def compute_all_time_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all-time averages per municipality for NASA POWER parameters."""
    if ELEVATION_COLUMN not in df.columns:
        df[ELEVATION_COLUMN] = pd.NA

    avg_df = (
        df.groupby("municipality_id")[NASA_POWER_COLUMNS]
        .mean(numeric_only=True)
        .reset_index()
    )

    elevation_df = (
        df[["municipality_id", ELEVATION_COLUMN]]
        .dropna(subset=[ELEVATION_COLUMN])
        .drop_duplicates(subset=["municipality_id"])
        .rename(columns={ELEVATION_COLUMN: "elevation"})
    )

    merged = avg_df.merge(elevation_df, on="municipality_id", how="left")
    if "elevation" not in merged.columns:
        merged["elevation"] = pd.NA

    return merged.rename(columns={
        "t2m": "avg_t2m",
        "t2m_max": "avg_t2m_max",
        "t2m_min": "avg_t2m_min",
        "rh2m": "avg_rh2m",
        "rhoa": "avg_rhoa",
        "prectotcorr": "avg_prectotcorr",
        "ws10m": "avg_ws10m",
        "allsky_sfc_sw_dwn": "avg_allsky_sfc_sw_dwn",
        "cloud_amt": "avg_cloud_amt",
        "surface_pressure": "avg_surface_pressure",
    })
```

**Explanation:** It accepts `df` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `reset_index()`, `mean()`, `groupby()`, `rename()`, `drop_duplicates()`.

### `main`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `323-359`
- **Signature:** `def main() -> None:`
- **Purpose:** Main execution flow.

**Code:**
```python
def main() -> None:
    """Main execution flow."""
    try:
        supabase = get_supabase_client()
        rows = fetch_all_rows(supabase, TABLE_NAME)
    except Exception as exc:
        print(f"Error loading data: {exc}")
        sys.exit(1)

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Data validation
    try:
        validate_dataframe(df)
    except Exception as exc:
        print(f"Validation error: {exc}")
        sys.exit(1)

    # Basic EDA
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nMissing Values:\n", summarize_missing_values(df).head(15))
    print("\nDescriptive Statistics:\n", descriptive_statistics(df).head(15))

    # Visualization examples
    plot_histogram(df, "t2m")
    plot_boxplot(df, "t2m")
    plot_correlation_heatmap(df)
    plot_municipality_distribution(df, "t2m")

    # Compute all-time averages
    avg_df = compute_all_time_averages(df)

    # Save output
    avg_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved averages to {OUTPUT_CSV}")
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `fetch_all_rows()`, `exit()`, `DataFrame()`, `validate_dataframe()`.


## `python_scripts/elevation_etl.py`

**File:** `python_scripts/elevation_etl.py`

**Summary:** ETL: Enrich municipality_climate_monthly with elevation data.

### `JsonFormatter.format`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `65-76`
- **Signature:** `def format(self, record: logging.LogRecord) -> str:`
- **Purpose:** Method of `JsonFormatter` that handles format.

**Code:**
```python
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
```

**Explanation:** It accepts `record` and returns `str`. See the code below for the full implementation. Key calls include `formatTime()`, `getMessage()`, `formatException()`, `hasattr()`, `isinstance()`.

### `setup_logging`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `79-86`
- **Signature:** `def setup_logging() -> logging.Logger:`
- **Purpose:** Sets up logging.

**Code:**
```python
def setup_logging() -> logging.Logger:
    logger = logging.getLogger("elevation_etl")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.propagate = False
    return logger
```

**Explanation:** It accepts zero arguments and returns `logging.Logger`. See the code below for the full implementation. Key calls include `getLogger()`, `setLevel()`, `StreamHandler()`, `setFormatter()`, `JsonFormatter()`.

### `load_config`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `89-134`
- **Signature:** `def load_config() -> AppConfig:`
- **Purpose:** Loads config.

**Code:**
```python
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
```

**Explanation:** It accepts zero arguments and returns `AppConfig`. See the code below for the full implementation. Key calls include `resolve()`, `Path()`, `load_dotenv()`, `getenv()`, `ValueError()`.

### `create_http_session`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `137-149`
- **Signature:** `def create_http_session(cfg: AppConfig) -> requests.Session:`
- **Purpose:** Creates http session.

**Code:**
```python
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
```

**Explanation:** It accepts `cfg` and returns `requests.Session`. See the code below for the full implementation. Key calls include `Session()`, `Retry()`, `HTTPAdapter()`, `mount()`.

### `SupabaseResponse.__init__`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `153-154`
- **Signature:** `def __init__(self, data: Any):`
- **Purpose:** Method of `SupabaseResponse` that handles   init  .

**Code:**
```python
def __init__(self, data: Any):
        self.data = data
```

**Explanation:** It accepts `data`. See the code below for the full implementation.

### `SupabaseRestQuery.__init__`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `158-163`
- **Signature:** `def __init__(self, client: "SupabaseRestClient", table: str):`
- **Purpose:** Method of `SupabaseRestQuery` that handles   init  .

**Code:**
```python
def __init__(self, client: "SupabaseRestClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[tuple[str, str]] = []
        self._single = False
```

**Explanation:** It accepts `client`, `table`. See the code below for the full implementation.

### `SupabaseRestQuery.select`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `165-167`
- **Signature:** `def select(self, columns: str = "*") -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles select.

**Code:**
```python
def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select = columns
        return self
```

**Explanation:** It accepts `columns` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.eq`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `169-171`
- **Signature:** `def eq(self, column: str, value: str) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles eq.

**Code:**
```python
def eq(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, value))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`.

### `SupabaseRestQuery.single`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `173-175`
- **Signature:** `def single(self) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles single.

**Code:**
```python
def single(self) -> "SupabaseRestQuery":
        self._single = True
        return self
```

**Explanation:** It accepts zero arguments and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.update`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `177-179`
- **Signature:** `def update(self, payload: dict[str, Any]) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles update.

**Code:**
```python
def update(self, payload: dict[str, Any]) -> "SupabaseRestQuery":
        self._update_payload = payload
        return self
```

**Explanation:** It accepts `payload` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.execute`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `181-197`
- **Signature:** `def execute(self) -> SupabaseResponse:`
- **Purpose:** Method of `SupabaseRestQuery` that handles execute.

**Code:**
```python
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
```

**Explanation:** It accepts zero arguments and returns `SupabaseResponse`. See the code below for the full implementation. Key calls include `hasattr()`, `patch()`, `get()`, `raise_for_status()`, `json()`.

### `SupabaseRestClient.__init__`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `201-208`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Prefer": "return=representation",
        }
        self.http = httpx.Client(timeout=10.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.table`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `210-211`
- **Signature:** `def table(self, table_name: str) -> SupabaseRestQuery:`
- **Purpose:** Method of `SupabaseRestClient` that handles table.

**Code:**
```python
def table(self, table_name: str) -> SupabaseRestQuery:
        return SupabaseRestQuery(self, table_name)
```

**Explanation:** It accepts `table_name` and returns `SupabaseRestQuery`. See the code below for the full implementation. Key calls include `SupabaseRestQuery()`.

### `_is_jwt_key`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `214-215`
- **Signature:** `def _is_jwt_key(key: str | None) -> bool:`
- **Purpose:** Handles  is jwt key.

**Code:**
```python
def _is_jwt_key(key: str | None) -> bool:
    return bool(key) and JWT_PATTERN.match(key) is not None
```

**Explanation:** It accepts `key` and returns `bool`. See the code below for the full implementation. Key calls include `bool()`, `match()`.

### `build_supabase_client`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `218-239`
- **Signature:** `def build_supabase_client(cfg: AppConfig) -> "Client | SupabaseRestClient":`
- **Purpose:** Builds supabase client.

**Code:**
```python
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
```

**Explanation:** It accepts `cfg` and returns `'Client | SupabaseRestClient'`. See the code below for the full implementation. Key calls include `RuntimeError()`, `_is_jwt_key()`, `create_client()`, `warning()`, `SupabaseRestClient()`.

### `fetch_municipalities_supabase`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `242-270`
- **Signature:** `def fetch_municipalities_supabase(client: "Client | SupabaseRestClient", page_size: int = 1000) -> List[Municipality]:`
- **Purpose:** Fetches municipalities supabase.

**Code:**
```python
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
```

**Explanation:** It accepts `client`, `page_size` and returns `List[Municipality]`. See the code below for the full implementation. Key calls include `execute()`, `extend()`, `len()`, `range()`, `Municipality()`.

### `ensure_cache_dir`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `273-274`
- **Signature:** `def ensure_cache_dir(path: Path) -> None:`
- **Purpose:** Handles ensure cache dir.

**Code:**
```python
def ensure_cache_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
```

**Explanation:** It accepts `path` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`.

### `cache_path`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `277-278`
- **Signature:** `def cache_path(cache_dir: Path, municipality_id: int) -> Path:`
- **Purpose:** Handles cache path.

**Code:**
```python
def cache_path(cache_dir: Path, municipality_id: int) -> Path:
    return cache_dir / f"{municipality_id}.json"
```

**Explanation:** It accepts `cache_dir`, `municipality_id` and returns `Path`. See the code below for the full implementation.

### `cache_is_fresh`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `281-285`
- **Signature:** `def cache_is_fresh(path: Path, ttl_days: int) -> bool:`
- **Purpose:** Handles cache is fresh.

**Code:**
```python
def cache_is_fresh(path: Path, ttl_days: int) -> bool:
    if not path.exists():
        return False
    age_seconds = time.time() - path.stat().st_mtime
    return age_seconds <= ttl_days * 86400
```

**Explanation:** It accepts `path`, `ttl_days` and returns `bool`. See the code below for the full implementation. Key calls include `exists()`, `time()`, `stat()`.

### `read_cache`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `288-293`
- **Signature:** `def read_cache(path: Path) -> Optional[float]:`
- **Purpose:** Reads cache.

**Code:**
```python
def read_cache(path: Path) -> Optional[float]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return float(data["elevation"])
    except Exception:
        return None
```

**Explanation:** It accepts `path` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `loads()`, `float()`, `read_text()`.

### `write_cache`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `296-297`
- **Signature:** `def write_cache(path: Path, elevation: float) -> None:`
- **Purpose:** Handles write cache.

**Code:**
```python
def write_cache(path: Path, elevation: float) -> None:
    path.write_text(json.dumps({"elevation": elevation}), encoding="utf-8")
```

**Explanation:** It accepts `path`, `elevation` and returns `None`. See the code below for the full implementation. Key calls include `write_text()`, `dumps()`.

### `rate_limit`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `300-308`
- **Signature:** `def rate_limit(last_call: float, rate_limit_per_second: float) -> float:`
- **Purpose:** Handles rate limit.

**Code:**
```python
def rate_limit(last_call: float, rate_limit_per_second: float) -> float:
    if rate_limit_per_second <= 0:
        return time.time()
    min_interval = 1.0 / rate_limit_per_second
    now = time.time()
    elapsed = now - last_call
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    return time.time()
```

**Explanation:** It accepts `last_call`, `rate_limit_per_second` and returns `float`. See the code below for the full implementation. Key calls include `time()`, `sleep()`.

### `fetch_elevation`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `311-341`
- **Signature:** `def fetch_elevation(`
- **Purpose:** Fetches elevation.

**Code:**
```python
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
```

**Explanation:** It accepts `session`, `municipality`, `cfg`, `logger`, `cache_dir` and returns `Tuple[Optional[float], Optional[str], bool]`. See the code below for the full implementation. Key calls include `cache_path()`, `cache_is_fresh()`, `read_cache()`, `get()`, `json()`.

### `AsyncRateLimiter.__init__`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `345-348`
- **Signature:** `def __init__(self, rate_limit_per_second: float) -> None:`
- **Purpose:** Method of `AsyncRateLimiter` that handles   init  .

**Code:**
```python
def __init__(self, rate_limit_per_second: float) -> None:
        self._rate = rate_limit_per_second
        self._lock = asyncio.Lock()
        self._last_call = 0.0
```

**Explanation:** It accepts `rate_limit_per_second` and returns `None`. See the code below for the full implementation. Key calls include `Lock()`.

### `AsyncRateLimiter.wait`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `350-359`
- **Signature:** `async def wait(self) -> None:`
- **Purpose:** Method of `AsyncRateLimiter` that handles wait.

**Code:**
```python
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
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `time()`, `sleep()`.

### `fetch_elevation_async`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `362-403`
- **Signature:** `async def fetch_elevation_async(`
- **Purpose:** Fetches elevation async.

**Code:**
```python
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
```

**Explanation:** It accepts `client`, `municipality`, `cfg`, `logger`, `cache_dir`, `rate_limiter` and returns `Tuple[Optional[float], Optional[str], bool]`. See the code below for the full implementation. Key calls include `cache_path()`, `cache_is_fresh()`, `read_cache()`, `range()`, `wait()`.

### `update_elevation_batch_supabase`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `406-432`
- **Signature:** `def update_elevation_batch_supabase(`
- **Purpose:** Updates elevation batch supabase.

**Code:**
```python
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
```

**Explanation:** It accepts `client`, `updates`, `dry_run`, `logger` and returns `int`. See the code below for the full implementation. Key calls include `len()`, `execute()`, `error()`, `eq()`, `update()`.

### `save_failed_csv`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `435-443`
- **Signature:** `def save_failed_csv(path: Path, failed: List[Tuple[Municipality, str]]) -> None:`
- **Purpose:** Saves failed csv.

**Code:**
```python
def save_failed_csv(path: Path, failed: List[Tuple[Municipality, str]]) -> None:
    if not failed:
        return
    header = "municipality_id,name,lat,lon,reason\n"
    rows = [
        f"{m.municipality_id},{m.name},{m.lat},{m.lon},{reason}\n"
        for m, reason in failed
    ]
    path.write_text(header + "".join(rows), encoding="utf-8")
```

**Explanation:** It accepts `path`, `failed` and returns `None`. See the code below for the full implementation. Key calls include `write_text()`, `join()`.

### `build_arg_parser`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `446-456`
- **Signature:** `def build_arg_parser() -> argparse.ArgumentParser:`
- **Purpose:** Builds arg parser.

**Code:**
```python
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
```

**Explanation:** It accepts zero arguments and returns `argparse.ArgumentParser`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`.

### `process_sync_supabase`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `459-501`
- **Signature:** `def process_sync_supabase(`
- **Purpose:** Processes sync supabase.

**Code:**
```python
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
```

**Explanation:** It accepts `client`, `municipalities`, `cfg`, `logger`, `cache_dir` and returns `Tuple[int, int, int, List[Tuple[Municipality, str]]]`. See the code below for the full implementation. Key calls include `tqdm()`, `create_http_session()`, `rate_limit()`, `fetch_elevation()`, `append()`.

### `main`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `504-564`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
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
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `setup_logging()`, `load_config()`, `build_arg_parser()`, `parse_args()`, `AppConfig()`.


## `scripts/extract_centroids.py`

**File:** `scripts/extract_centroids.py`

**Summary:** Extract centroid coordinates and area from GeoJSON boundary files.

### `norm`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `51-59`
- **Signature:** `def norm(name: str) -> str:`
- **Purpose:** Normalize a geographic name for matching.

**Code:**
```python
def norm(name: str) -> str:
    """Normalize a geographic name for matching."""
    s = name.strip().lower()
    s = _PARENTHETICAL.sub(" ", s)
    s = _CITY_SUFFIXES.sub("", s)
    s = _MUNI_SUFFIXES.sub("", s)
    s = s.replace("city of ", "").strip()
    s = _MULTI_SPACE.sub(" ", s)
    return s
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `strip()`, `sub()`, `replace()`.

### `compute_centroid_and_area`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `67-94`
- **Signature:** `def compute_centroid_and_area(feature: dict) -> tuple[float, float, float]:`
- **Purpose:** Compute centroid (lat, lon) and area_km2 from a GeoJSON feature.

**Code:**
```python
def compute_centroid_and_area(feature: dict) -> tuple[float, float, float]:
    """Compute centroid (lat, lon) and area_km2 from a GeoJSON feature.

    Uses shapely to compute the geometric centroid. Area is computed
    using a simple equirectangular approximation centered on the polygon.
    """
    geom = shape(feature["geometry"])

    # Centroid — shapely gives (lon, lat) in EPSG:4326
    centroid = geom.centroid
    lon = centroid.x
    lat = centroid.y

    # Area approximation: equirectangular projection
    # R_earth = 6371 km
    # area = (lon_range * cos(lat_avg) * lat_range) * (pi/180)^2 * R^2
    # But shapely doesn't do geodesic. Use the property from GeoJSON if available.
    props = feature.get("properties", {})
    area_km2 = props.get("area_km2")
    if area_km2 is None:
        # Fallback: rough equirectangular approximation
        minx, miny, maxx, maxy = geom.bounds
        lat_rad = lat * 3.141592653589793 / 180.0
        lon_range_km = (maxx - minx) * 111.32 * cos(lat_rad)
        lat_range_km = (maxy - miny) * 110.574
        area_km2 = lon_range_km * lat_range_km

    return round(lat, 6), round(lon, 6), round(float(area_km2), 2)
```

**Explanation:** It accepts `feature` and returns `tuple[float, float, float]`. See the code below for the full implementation. Key calls include `shape()`, `get()`, `cos()`, `round()`, `float()`.

### `cos`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `97-100`
- **Signature:** `def cos(x: float) -> float:`
- **Purpose:** Handles cos.

**Code:**
```python
def cos(x: float) -> float:
    import math

    return math.cos(x)
```

**Explanation:** It accepts `x` and returns `float`. See the code below for the full implementation. Key calls include `cos()`.

### `process_geojson`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `103-138`
- **Signature:** `def process_geojson(`
- **Purpose:** Process a GeoJSON file and return list of centroid records.

**Code:**
```python
def process_geojson(
    filepath: Path, name_property: str
) -> list[dict]:
    """Process a GeoJSON file and return list of centroid records.

    Each record: {name, centroid_lat, centroid_lon, area_km2, psgc}
    """
    print(f"Loading {filepath.name}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    print(f"  {len(features)} features found")

    records = []
    for feat in features:
        props = feat.get("properties", {})
        name = props.get(name_property, "")
        if not name:
            continue

        lat, lon, area = compute_centroid_and_area(feat)
        psgc = props.get(f"{name_property.split('_')[0]}_psgc")

        records.append(
            {
                "name": name,
                "normalized_name": norm(name),
                "centroid_lat": lat,
                "centroid_lon": lon,
                "area_km2": area,
                "psgc": psgc,
            }
        )

    return records
```

**Explanation:** It accepts `filepath`, `name_property` and returns `list[dict]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `len()`, `compute_centroid_and_area()`.

### `SupabaseRestClient.__init__`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `147-153`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=60.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.fetch_all`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `155-171`
- **Signature:** `def fetch_all(self, table: str, select: str, batch: int = 1000) -> list[dict]:`
- **Purpose:** Fetch all rows from a table with pagination.

**Code:**
```python
def fetch_all(self, table: str, select: str, batch: int = 1000) -> list[dict]:
        """Fetch all rows from a table with pagination."""
        rows = []
        offset = 0
        while True:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {"select": select, "limit": str(batch), "offset": str(offset)}
            resp = self.http.get(url, params=params, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            rows.extend(data)
            if len(data) < batch:
                break
            offset += batch
        return rows
```

**Explanation:** It accepts `table`, `select`, `batch` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`, `extend()`, `str()`.

### `build_province_lookup`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `174-185`
- **Signature:** `def build_province_lookup(client: SupabaseRestClient) -> dict[str, dict]:`
- **Purpose:** Build normalized name → province record mapping.

**Code:**
```python
def build_province_lookup(client: SupabaseRestClient) -> dict[str, dict]:
    """Build normalized name → province record mapping."""
    print("Fetching provinces from Supabase...")
    rows = client.fetch_all("provinces", "province_id,name,region_id,lat,lon")
    print(f"  {len(rows)} provinces found")
    lookup = {}
    for r in rows:
        key = norm(r["name"])
        lookup[key] = r
        # Also add the raw name lowercased as an alias
        lookup[r["name"].lower().strip()] = r
    return lookup
```

**Explanation:** It accepts `client` and returns `dict[str, dict]`. See the code below for the full implementation. Key calls include `fetch_all()`, `len()`, `norm()`, `strip()`, `lower()`.

### `build_municipality_lookup`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `188-205`
- **Signature:** `def build_municipality_lookup(client: SupabaseRestClient) -> dict[str, dict]:`
- **Purpose:** Build normalized name → municipality record mapping.

**Code:**
```python
def build_municipality_lookup(client: SupabaseRestClient) -> dict[str, dict]:
    """Build normalized name → municipality record mapping."""
    print("Fetching municipalities from Supabase...")
    rows = client.fetch_all(
        "municipalities", "municipality_id,name,province_id,lat,lon"
    )
    print(f"  {len(rows)} municipalities found")
    lookup = {}
    for r in rows:
        key = norm(r["name"])
        # If duplicate normalized names exist, keep the first
        if key not in lookup:
            lookup[key] = r
        # Also add raw name
        raw_key = r["name"].lower().strip()
        if raw_key not in lookup:
            lookup[raw_key] = r
    return lookup
```

**Explanation:** It accepts `client` and returns `dict[str, dict]`. See the code below for the full implementation. Key calls include `fetch_all()`, `len()`, `norm()`, `strip()`, `lower()`.

### `write_csv`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `213-219`
- **Signature:** `def write_csv(filepath: Path, rows: list[dict], fieldnames: list[str]) -> None:`
- **Purpose:** Handles write csv.

**Code:**
```python
def write_csv(filepath: Path, rows: list[dict], fieldnames: list[str]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written {len(rows)} rows to {filepath.name}")
```

**Explanation:** It accepts `filepath`, `rows`, `fieldnames` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`, `open()`, `DictWriter()`, `writeheader()`, `writerows()`.

### `main`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `227-335`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
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

    client = SupabaseRestClient(url, key)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Province centroids ---
    print("\n=== Processing province GeoJSON ===")
    province_records = process_geojson(PROVINCE_GEOJSON, "adm2_en")
    province_lookup = build_province_lookup(client)

    province_matches = []
    province_unmatched = []
    for rec in province_records:
        match = province_lookup.get(rec["normalized_name"]) or province_lookup.get(
            rec["name"].lower().strip()
        )
        if match:
            province_matches.append(
                {
                    "province_id": match["province_id"],
                    "name": match["name"],
                    "centroid_lat": rec["centroid_lat"],
                    "centroid_lon": rec["centroid_lon"],
                    "area_km2": rec["area_km2"],
                    "source": "GeoJSON centroid",
                }
            )
        else:
            province_unmatched.append(rec)

    print(f"  Matched: {len(province_matches)}, Unmatched: {len(province_unmatched)}")
    if province_unmatched:
        print("  Unmatched provinces:")
        for u in province_unmatched[:10]:
            print(f"    {u['name']} (norm: {u['normalized_name']})")

    write_csv(
        OUTPUT_DIR / "geospatial_province_centroids.csv",
        province_matches,
        ["province_id", "name", "centroid_lat", "centroid_lon", "area_km2", "source"],
    )

    # --- Municipality centroids ---
    print("\n=== Processing municipality GeoJSON ===")
    muni_records = process_geojson(MUNICIPALITY_GEOJSON, "adm3_en")
    muni_lookup = build_municipality_lookup(client)

    muni_matches = []
    muni_unmatched = []
    for rec in muni_records:
        match = muni_lookup.get(rec["normalized_name"]) or muni_lookup.get(
            rec["name"].lower().strip()
        )
        if match:
            muni_matches.append(
                {
                    "municipality_id": match["municipality_id"],
                    "name": match["name"],
                    "province_id": match.get("province_id", ""),
                    "centroid_lat": rec["centroid_lat"],
                    "centroid_lon": rec["centroid_lon"],
                    "area_km2": rec["area_km2"],
                    "source": "GeoJSON centroid",
                }
            )
        else:
            muni_unmatched.append(rec)

    print(f"  Matched: {len(muni_matches)}, Unmatched: {len(muni_unmatched)}")
    if muni_unmatched:
        print(f"  (showing first 10 of {len(muni_unmatched)} unmatched)")
        for u in muni_unmatched[:10]:
            print(f"    {u['name']} (norm: {u['normalized_name']})")

    write_csv(
        OUTPUT_DIR / "geospatial_municipality_centroids.csv",
        muni_matches,
        [
            "municipality_id",
            "name",
            "province_id",
            "centroid_lat",
            "centroid_lon",
            "area_km2",
            "source",
        ],
    )

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Province centroids:  {len(province_matches)} matched")
    print(f"  Municipality centroids: {len(muni_matches)} matched")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}")
    print("\nNext step: Run insert_geospatial_metadata.py to insert into Supabase.")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `load_dotenv()`, `getenv()`, `SupabaseRestClient()`, `mkdir()`, `process_geojson()`.


## `scripts/simplify-geojson.js`

**File:** `scripts/simplify-geojson.js`

**Summary:** Reference or configuration file.


## `scripts/insert_geospatial_metadata.py`

**File:** `scripts/insert_geospatial_metadata.py`

**Summary:** Insert geospatial metadata from CSVs into Supabase.

### `SupabaseRestClient.__init__`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `24-32`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        self.http = httpx.Client(timeout=60.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.upsert_batch`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `34-46`
- **Signature:** `def upsert_batch(self, table: str, rows: list[dict]) -> tuple[int, str]:`
- **Purpose:** Method of `SupabaseRestClient` that upserts batch.

**Code:**
```python
def upsert_batch(self, table: str, rows: list[dict]) -> tuple[int, str]:
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
```

**Explanation:** It accepts `table`, `rows` and returns `tuple[int, str]`. See the code below for the full implementation. Key calls include `post()`, `raise_for_status()`, `len()`, `str()`.

### `SupabaseRestClient.fetch_existing_keys`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `48-71`
- **Signature:** `def fetch_existing_keys(self, table: str, select: str) -> set[str]:`
- **Purpose:** Fetch existing geo keys to skip duplicates.

**Code:**
```python
def fetch_existing_keys(self, table: str, select: str) -> set[str]:
        """Fetch existing geo keys to skip duplicates."""
        rows = []
        offset = 0
        batch = 1000
        while True:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {"select": select, "limit": str(batch), "offset": str(offset)}
            resp = self.http.get(url, params=params, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            rows.extend(data)
            if len(data) < batch:
                break
            offset += batch
        keys = set()
        for r in rows:
            for col in ["region_id", "province_id", "municipality_id", "barangay_id"]:
                val = r.get(col)
                if val is not None:
                    keys.add(f"{col}:{val}")
        return keys
```

**Explanation:** It accepts `table`, `select` and returns `set[str]`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`, `extend()`, `str()`.

### `read_csv`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `74-79`
- **Signature:** `def read_csv(path: Path) -> list[dict]:`
- **Purpose:** Reads csv.

**Code:**
```python
def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
```

**Explanation:** It accepts `path` and returns `list[dict]`. See the code below for the full implementation. Key calls include `exists()`, `open()`, `DictReader()`, `list()`.

### `main`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `82-191`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
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

    client = SupabaseRestClient(url, key)
    batch_size = 500
    total_inserted = 0

    # Check existing entries to avoid duplicates
    print("Fetching existing geospatial_metadata keys...")
    try:
        existing_keys = client.fetch_existing_keys(
            "geospatial_metadata",
            "region_id,province_id,municipality_id,barangay_id",
        )
        print(f"  {len(existing_keys)} existing entries")
    except Exception as exc:
        print(f"  Warning: could not fetch existing keys ({exc}), will attempt all")
        existing_keys = set()

    # --- Province centroids ---
    print("\n--- Province centroids ---")
    provinces = read_csv(GAP_DIR / "geospatial_province_centroids.csv")
    print(f"  {len(provinces)} rows in CSV")

    rows = []
    skipped = 0
    for p in provinces:
        pid = int(p["province_id"])
        geo_key = f"province_id:{pid}"
        if geo_key in existing_keys:
            skipped += 1
            continue
        rows.append(
            {
                "province_id": pid,
                "centroid_lat": float(p["centroid_lat"]),
                "centroid_lon": float(p["centroid_lon"]),
                "area_km2": float(p["area_km2"]) if p.get("area_km2") else None,
                "source": p.get("source", "GeoJSON centroid"),
            }
        )

    print(f"  Skipped (already exist): {skipped}")
    print(f"  To insert: {len(rows)}")

    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        count, err = client.upsert_batch("geospatial_metadata", batch)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Province centroids inserted: {inserted}")

    # --- Municipality centroids ---
    print("\n--- Municipality centroids ---")
    munis = read_csv(GAP_DIR / "geospatial_municipality_centroids.csv")
    print(f"  {len(munis)} rows in CSV")

    rows = []
    skipped = 0
    for m in munis:
        mid = int(m["municipality_id"])
        geo_key = f"municipality_id:{mid}"
        if geo_key in existing_keys:
            skipped += 1
            continue
        rows.append(
            {
                "municipality_id": mid,
                "centroid_lat": float(m["centroid_lat"]),
                "centroid_lon": float(m["centroid_lon"]),
                "area_km2": float(m["area_km2"]) if m.get("area_km2") else None,
                "source": m.get("source", "GeoJSON centroid"),
            }
        )

    print(f"  Skipped (already exist): {skipped}")
    print(f"  To insert: {len(rows)}")

    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        count, err = client.upsert_batch("geospatial_metadata", batch)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Municipality centroids inserted: {inserted}")

    print(f"\n{'='*60}")
    print(f"TOTAL INSERTED: {total_inserted}")
    print(f"{'='*60}")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `load_dotenv()`, `getenv()`, `SupabaseRestClient()`, `fetch_existing_keys()`, `set()`.


## `philippine_geojson/LUMI-LOGO-removebg-preview.png`

**File:** `philippine_geojson/LUMI-LOGO-removebg-preview.png`

**Summary:** Reference or configuration file.


## `philippine_geojson/philippine_geojson_file_per_provinces.json`

**File:** `philippine_geojson/philippine_geojson_file_per_provinces.json`

**Summary:** JSON configuration or data file.

**First lines:**
```json
{"type":"FeatureCollection", "features": [
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.54912983600002,14.740754617000052],[120.519016039,14.756447996000075],[120.48768967500007,14.754822206000034],[120.45148344700009,14.743288503000036],[120.40032200400003,14.711798445000055],[120.40956802700009,14.700078456000025],[120.50527629400005,14.692398725000029],[120.55219625900008,14.705209836000051],[120.54912983600002,14.740754617000052]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300801000,"adm3_en":"Abucay","geo_level":"Mun","len_crs":46095,"area_crs":76966805,"len_km":46,"area_km2":76},"id":300801000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.40956802700009,14.700078456000025],[120.40032200400003,14.711798445000055],[120.34635076100007,14.631868223000028],[120.36803668300001,14.625765517000048],[120.39280916200006,14.587940439000025],[120.38291627700005,14.568593554000076],[120.38998949300002,14.537892413000067],[120.37474302800003,14.524687197000045],[120.39182957300011,14.46515801300006],[120.47632616600004,14.539141382000023],[120.465056408,14.56906848600005],[120.46406136400005,14.60364183900003],[120.45994848500004,14.633972138000043],[120.44585296500009,14.639999311000055],[120.40956802700009,14.700078456000025]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300802000,"adm3_en":"Bagac","geo_level":"Mun","len_crs":84386,"area_crs":189246123,"len_km":84,"area_km2":189},"id":300802000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.55912062900006,14.68897795900006],[120.55219625900008,14.705209836000051],[120.50527629400005,14.692398725000029],[120.40956802700009,14.700078456000025],[120.44585296500009,14.639999311000055],[120.45994848500004,14.633972138000043],[120.46406136400005,14.60364183900003],[120.46904436400008,14.601599101000032],[120.4792965150001,14.636175931000025],[120.521420884,14.635518414000042],[120.5477613380001,14.663026117000072],[120.55912062900006,14.68897795900006]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300803000,"adm3_en":"City of Balanga","geo_level":"City","len_crs":60735,"area_crs":89675904,"len_km":60,"area_km2":89},"id":300803000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.47934569400003,14.890787504000063],[120.4838347650001,14.913516805000029],[120.4673985500001,14.922759493000063],[120.42280570000003,14.914471035000073],[120.40665743800001,14.88570509300007],[120.34119403900002,14.857304444000023],[120.3390555960001,14.841486584000045],[120.37833608500013,14.850868001000041],[120.40634211600002,14.843403677000028],[120.44109522500004,14.859036774000062],[120.47768865100011,14.86055423500005],[120.47934569400003,14.890787504000063]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300804000,"adm3_en":"Dinalupihan","geo_level":"Mun","len_crs":60060,"area_crs":75592615,"len_km":60,"area_km2":75},"id":300804000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.52996468200003,14.832459915000069],[120.4920569200001,14.888984074000064],[120.47934569400003,14.890787504000063],[120.47768865100011,14.86055423500005],[120.44109522500004,14.859036774000062],[120.40634211600002,14.843403677000028],[120.37833608500013,14.850868001000041],[120.3390555960001,14.841486584000045],[120.34021008900005,14.817820355000038],[120.36109152900009,14.792929272000038],[120.36058266300006,14.777602718000026],[120.381437516,14.74487362600007],[120.39561471300011,14.744547584000028],[120.430288528,14.762044054000059],[120.45404258500002,14.806266291000043],[120.50365496800009,14.812110385000043],[120.52996468200003,14.832459915000069]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300805000,"adm3_en":"Hermosa","geo_level":"Mun","len_crs":85880,"area_crs":149116470,"len_km":85,"area_km2":149},"id":300805000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.61092647700002,14.511408636000054],[120.59267934900004,14.581285602000035],[120.56584382000005,14.575284762000022],[120.55182263200004,14.558990180000023],[120.51725748300011,14.541802632000044],[120.47632616600004,14.539141382000023],[120.56130444700011,14.504748130000053],[120.61092647700002,14.511408636000054]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300806000,"adm3_en":"Limay","geo_level":"Mun","len_crs":46114,"area_crs":60754280,"len_km":46,"area_km2":60},"id":300806000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.61092647700002,14.511408636000054],[120.56130444700011,14.504748130000053],[120.47632616600004,14.539141382000023],[120.39182957300011,14.46515801300006],[120.44478092700002,14.446346042000073],[120.46535926700007,14.421280646000067],[120.48639886800004,14.43344834000004],[120.55401782400008,14.422366258000064],[120.5763699160001,14.431959074000074],[120.60237232300005,14.461890157000026],[120.61092647700002,14.511408636000054]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300807000,"adm3_en":"Mariveles","geo_level":"Mun","len_crs":112145,"area_crs":194510486,"len_km":112,"area_km2":194},"id":300807000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.39561471300011,14.744547584000028],[120.381437516,14.74487362600007],[120.36058266300006,14.777602718000026],[120.2502833420001,14.726266689000056],[120.24818179700004,14.692287460000045],[120.29232886400007,14.655530363000024],[120.31487632400001,14.626121303000048],[120.34635076100007,14.631868223000028],[120.40032200400003,14.711798445000055],[120.42257137600006,14.743429041000073],[120.39561471300011,14.744547584000028]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300808000,"adm3_en":"Morong","geo_level":"Mun","len_crs":68139,"area_crs":173815670,"len_km":68,"area_km2":173},"id":300808000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.547230279,14.786174901000035],[120.54954030000012,14.822315404000049],[120.52996468200003,14.832459915000069],[120.50365496800009,14.812110385000043],[120.45404258500002,14.806266291000043],[120.430288528,14.762044054000059],[120.39561471300011,14.744547584000028],[120.42257137600006,14.743429041000073],[120.44484715700004,14.753264496000044],[120.484387534,14.784157906000077],[120.547230279,14.786174901000035]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300809000,"adm3_en":"Orani","geo_level":"Mun","len_crs":66771,"area_crs":53713890,"len_km":66,"area_km2":53},"id":300809000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.59267934900004,14.581285602000035],[120.57774852000011,14.658174625000074],[120.5625277580001,14.643406786000071],[120.52282089000005,14.625400577000049],[120.5254815830001,14.606581758000061],[120.50994564100006,14.583172625000032],[120.46904436400008,14.601599101000032],[120.46406136400005,14.60364183900003],[120.465056408,14.56906848600005],[120.47632616600004,14.539141382000023],[120.51725748300011,14.541802632000044],[120.55182263200004,14.558990180000023],[120.56584382000005,14.575284762000022],[120.59267934900004,14.581285602000035]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300810000,"adm3_en":"Orion","geo_level":"Mun","len_crs":61499,"area_crs":89724860,"len_km":61,"area_km2":89},"id":300810000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.57774852000011,14.658174625000074],[120.55912062900006,14.68897795900006],[120.5477613380001,14.663026117000072],[120.521420884,14.635518414000042],[120.4792965150001,14.636175931000025],[120.46904436400008,14.601599101000032],[120.50994564100006,14.583172625000032],[120.5254815830001,14.606581758000061],[120.52282089000005,14.625400577000049],[120.5625277580001,14.643406786000071],[120.57774852000011,14.658174625000074]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300811000,"adm3_en":"Pilar","geo_level":"Mun","len_crs":47893,"area_crs":45597285,"len_km":47,"area_km2":45},"id":300811000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.547230279,14.786174901000035],[120.484387534,14.784157906000077],[120.44484715700004,14.753264496000044],[120.42257137600006,14.743429041000073],[120.40032200400003,14.711798445000055],[120.45148344700009,14.743288503000036],[120.48768967500007,14.754822206000034],[120.519016039,14.756447996000075],[120.54912983600002,14.740754617000052],[120.547230279,14.786174901000035]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm3_psgc":300812000,"adm3_en":"Samal","geo_level":"Mun","len_crs":52240,"area_crs":47561071,"len_km":52,"area_km2":47},"id":300812000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.0600175070001,14.948693150000054],[121.02629634100003,14.962277589000054],[121.01817435700002,14.956274170000032],[121.05187106100006,14.917126073000073],[121.0600175070001,14.948693150000054]]],[[[121.03353271100002,14.911199626000043],[121.03451613600008,14.929714999000048],[121.00247087900006,14.957780959000047],[120.98901668900011,14.945091191000076],[120.95939887400003,14.949525091000055],[120.96296742000004,14.914453782000066],[121.00007929900003,14.894102731000032],[121.02078335400006,14.891560991000063],[121.03353271100002,14.911199626000043]]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301401000,"adm3_en":"Angat","geo_level":"Mun","len_crs":61524,"area_crs":49424835,"len_km":61,"area_km2":49},"id":301401000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.92719888300007,14.83016499700005],[120.90707347900002,14.871764743000032],[120.89918273500007,14.866661650000024],[120.89142116700009,14.814842762000067],[120.90566397600003,14.784231372000022],[120.92719888300007,14.83016499700005]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301402000,"adm3_en":"Balagtas","geo_level":"Mun","len_crs":31861,"area_crs":21490346,"len_km":31,"area_km2":21},"id":301402000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.9225200190001,14.963751060000053],[120.89308200600011,15.015760345000047],[120.84911058500006,14.957067304000073],[120.85580789700008,14.92281652200006],[120.89328195100006,14.911978075000034],[120.89040638100006,14.920987530000048],[120.9225200190001,14.963751060000053]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301403000,"adm3_en":"City of Baliwag","geo_level":"City","len_crs":44173,"area_crs":45781993,"len_km":44,"area_km2":45},"id":301403000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.95096273900005,14.844527219000042],[120.92719888300007,14.83016499700005],[120.90566397600003,14.784231372000022],[120.91512261800005,14.766244732000075],[120.92218369700005,14.763330215000055],[120.96119559300007,14.785311779000041],[120.95096273900005,14.844527219000042]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301404000,"adm3_en":"Bocaue","geo_level":"Mun","len_crs":32852,"area_crs":26363708,"len_km":32,"area_km2":26},"id":301404000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.89142116700009,14.814842762000067],[120.86617458700005,14.820866962000023],[120.82632309200004,14.770624134000064],[120.83682552300002,14.745885322000046],[120.8876598390001,14.709949052000068],[120.90287439300005,14.723927337000077],[120.90044368500004,14.747587724000024],[120.91512261800005,14.766244732000075],[120.90566397600003,14.784231372000022],[120.89142116700009,14.814842762000067]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301405000,"adm3_en":"Bulacan","geo_level":"Mun","len_crs":51308,"area_crs":72373254,"len_km":51,"area_km2":72},"id":301405000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.95512918900009,14.95672827300007],[120.9225200190001,14.963751060000053],[120.89040638100006,14.920987530000048],[120.90560132500002,14.892586728000031],[120.96296742000004,14.914453782000066],[120.95939887400003,14.949525091000055],[120.95512918900009,14.95672827300007]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301406000,"adm3_en":"Bustos","geo_level":"Mun","len_crs":34195,"area_crs":39882083,"len_km":34,"area_km2":39},"id":301406000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.80278833800004,14.901639916000025],[120.79374105600006,14.937171343000044],[120.74316107100003,14.93094760900004],[120.7350646540001,14.872973665000071],[120.77455784000006,14.868719627000074],[120.78154180000001,14.868383700000038],[120.80497795900011,14.891166791000048],[120.80278833800004,14.901639916000025]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301407000,"adm3_en":"Calumpit","geo_level":"Mun","len_crs":35613,"area_crs":46830108,"len_km":35,"area_km2":46},"id":301407000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.89918273500007,14.866661650000024],[120.85452280900007,14.865266780000066],[120.86617458700005,14.820866962000023],[120.89142116700009,14.814842762000067],[120.89918273500007,14.866661650000024]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301408000,"adm3_en":"Guiguinto","geo_level":"Mun","len_crs":27394,"area_crs":22328398,"len_km":27,"area_km2":22},"id":301408000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.77455784000006,14.868719627000074],[120.7350646540001,14.872973665000071],[120.69810754700006,14.830804838000063],[120.68703221300007,14.773480495000056],[120.76721255000008,14.768831383000075],[120.76261442900011,14.836524166000055],[120.77455784000006,14.868719627000074]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301409000,"adm3_en":"Hagonoy","geo_level":"Mun","len_crs":59736,"area_crs":83450373,"len_km":59,"area_km2":83},"id":301409000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.80497795900011,14.891166791000048],[120.78154180000001,14.868383700000038],[120.80103311300003,14.840341529000057],[120.80370175500002,14.757803225000034],[120.82632309200004,14.770624134000064],[120.86617458700005,14.820866962000023],[120.85452280900007,14.865266780000066],[120.80497795900011,14.891166791000048]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301410000,"adm3_en":"City of Malolos","geo_level":"City","len_crs":67577,"area_crs":70877342,"len_km":67,"area_km2":70},"id":301410000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.01336976000005,14.80172258500005],[120.96119559300007,14.785311779000041],[120.92218369700005,14.763330215000055],[120.94164780900007,14.738630583000033],[121.0026142690001,14.783637500000047],[121.023732171,14.772783646000047],[121.028329718,14.781832778000021],[121.01336976000005,14.80172258500005]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301411000,"adm3_en":"Marilao","geo_level":"Mun","len_crs":44282,"area_crs":28353727,"len_km":44,"area_km2":28},"id":301411000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.023732171,14.772783646000047],[121.0026142690001,14.783637500000047],[120.94164780900007,14.738630583000033],[120.92218369700005,14.763330215000055],[120.91512261800005,14.766244732000075],[120.90044368500004,14.747587724000024],[120.92701620000004,14.736080406000042],[120.97852281100006,14.73480671900006],[121.023732171,14.772783646000047]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301412000,"adm3_en":"City of Meycauayan","geo_level":"City","len_crs":52104,"area_crs":31794854,"len_km":52,"area_km2":31},"id":301412000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.34032747600008,14.910309698000045],[121.18117081400011,14.907626440000056],[121.11677614000007,14.938568709000037],[121.09288736700012,14.922217289000063],[121.0600175070001,14.948693150000054],[121.05187106100006,14.917126073000073],[121.03353271100002,14.911199626000043],[121.02078335400006,14.891560991000063],[121.03016048100004,14.849776138000038],[121.06989460500006,14.86521855500007],[121.16528463600002,14.823417534000043],[121.20804184000006,14.81794121400003],[121.33035662500004,14.834802543000022],[121.34032747600008,14.910309698000045]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301413000,"adm3_en":"Norzagaray","geo_level":"Mun","len_crs":129322,"area_crs":297426794,"len_km":129,"area_km2":297},"id":301413000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.92701620000004,14.736080406000042],[120.90044368500004,14.747587724000024],[120.90287439300005,14.723927337000077],[120.92701620000004,14.736080406000042]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301414000,"adm3_en":"Obando","geo_level":"Mun","len_crs":27634,"area_crs":16214719,"len_km":27,"area_km2":16},"id":301414000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.00007929900003,14.894102731000032],[120.96296742000004,14.914453782000066],[120.90560132500002,14.892586728000031],[120.90707347900002,14.871764743000032],[120.92719888300007,14.83016499700005],[120.95096273900005,14.844527219000042],[121.00007929900003,14.894102731000032]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301415000,"adm3_en":"Pandi","geo_level":"Mun","len_crs":44562,"area_crs":50438115,"len_km":44,"area_km2":50},"id":301415000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.78154180000001,14.868383700000038],[120.77455784000006,14.868719627000074],[120.76261442900011,14.836524166000055],[120.76721255000008,14.768831383000075],[120.80370175500002,14.757803225000034],[120.80103311300003,14.840341529000057],[120.78154180000001,14.868383700000038]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301416000,"adm3_en":"Paombong","geo_level":"Mun","len_crs":44506,"area_crs":45312548,"len_km":44,"area_km2":45},"id":301416000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.90560132500002,14.892586728000031],[120.89040638100006,14.920987530000048],[120.89328195100006,14.911978075000034],[120.87696524700004,14.893578163000027],[120.80278833800004,14.901639916000025],[120.80497795900011,14.891166791000048],[120.85452280900007,14.865266780000066],[120.89918273500007,14.866661650000024],[120.90707347900002,14.871764743000032],[120.90560132500002,14.892586728000031]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm3_psgc":301417000,"adm3_en":"Plaridel","geo_level":"Mun","len_crs":39787,"area_crs":35760318,"len_km":39,"area_km2":35},"id":301417000},
```


## `philippine_geojson/philippine_geojson_file_per_region.json`

**File:** `philippine_geojson/philippine_geojson_file_per_region.json`

**Summary:** JSON configuration or data file.

**First lines:**
```json
{"type":"FeatureCollection", "features": [
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.57182232500008,17.786033365000037],[120.6022255060001,17.809284779000055],[120.69086868800002,17.83457964200005],[120.713090887,17.85995599300003],[120.72824914700004,17.892507978000026],[120.78375228200004,17.911236471000052],[120.82604262300005,17.95475861500006],[120.85020468100005,17.962860961000043],[120.89458557200008,17.951472294000038],[120.9203956020001,17.95626482200003],[120.9469459710001,17.99709437600006],[120.9277503080001,18.020743286000023],[120.93546188900007,18.06899515000003],[120.92814130400008,18.088193385000068],[120.97006946800002,18.18186392000007],[120.92676405500005,18.241938255000036],[120.91666636100001,18.28456025600007],[120.94836326600011,18.38169343000004],[120.94704360700008,18.42062579300005],[120.96914518200002,18.510116371000038],[120.97645367700012,18.568958937000048],[120.92800873600004,18.559397641000032],[120.89732007100008,18.572443782000047],[120.86849404900009,18.61074516800005],[120.85288653600003,18.647526628000037],[120.78498690700006,18.624524222000048],[120.77766979400008,18.600878073000043],[120.7871003460001,18.568201960000067],[120.76150944400003,18.53956400500004],[120.72517807700002,18.52894981400004],[120.6694201160001,18.531711337000047],[120.62456250900004,18.54570767900003],[120.5636528010001,18.49142517700005],[120.59390701900008,18.414015010000067],[120.59999656500008,18.37675214800003],[120.59729645400012,18.333825110000078],[120.54865267100001,18.233600720000027],[120.52351140500002,18.204803687000037],[120.51223627900004,18.135350546000033],[120.47091102600007,18.08597968200007],[120.47856773900001,18.07902007900003],[120.48026778000006,18.016806657000075],[120.49763223400008,18.003474580000045],[120.47603697300008,17.978723403000057],[120.46188261800012,17.939657187000027],[120.42928257500012,17.915602186000054],[120.44338379200008,17.90272064800007],[120.48002829200006,17.898077388000043],[120.5281210910001,17.878524456000036],[120.54059008000002,17.824333185000057],[120.57182232500008,17.786033365000037]]]},"properties":{"adm1_psgc":100000000,"adm2_psgc":102800000,"adm2_en":"Ilocos Norte","geo_level":"Prov","len_crs":309785,"area_crs":3276945154,"len_km":309,"area_km2":3276},"id":102800000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.57182232500008,17.786033365000037],[120.54059008000002,17.824333185000057],[120.5281210910001,17.878524456000036],[120.48002829200006,17.898077388000043],[120.44338379200008,17.90272064800007],[120.44005329900004,17.867140905000042],[120.45311075100005,17.819130408000035],[120.40263634400003,17.794080668000053],[120.42606927300005,17.774510965000047],[120.43523230500013,17.731811538000045],[120.415776563,17.70888861900005],[120.38320818900002,17.692943489000072],[120.35281905200009,17.635678444000064],[120.34437655300009,17.577796981000063],[120.35184339200009,17.548208770000027],[120.39159110500009,17.516358779000033],[120.41357341600009,17.516623544000026],[120.43594567000004,17.47842835400007],[120.4612753570001,17.40782160400005],[120.45456856300007,17.36126159800005],[120.42839832000006,17.31631017800004],[120.417079553,17.253710443000045],[120.41427879900006,17.204509846000064],[120.42630269900006,17.16897719900004],[120.43625797100003,17.083883638000028],[120.44818463300011,17.04352363600003],[120.444812522,16.974010931000063],[120.41079750900008,16.920904919000066],[120.43577346200004,16.900497252000033],[120.46426010700009,16.914504663000056],[120.48999382900001,16.90546628500005],[120.51072422900006,16.918236059000037],[120.50695831400003,16.846549994000043],[120.53520039300008,16.816054985000047],[120.53514004700003,16.787169211000048],[120.54890816500007,16.767490429000077],[120.54544368800009,16.728928588000027],[120.53478210300011,16.720904921000056],[120.5650648840001,16.669766382000034],[120.57452221100006,16.67126486700004],[120.59903624900006,16.738317935000055],[120.58961744100009,16.747182695000053],[120.58601613200004,16.836661373000027],[120.61018355700003,16.840016965000075],[120.62453594000011,16.877777002000073],[120.669563,16.911981],[120.73856888600005,16.915983209000046],[120.74751261300004,16.926550587000058],[120.78527385300004,16.92133500700004],[120.7800911270001,17.016488273000046],[120.76761284700002,17.066790583000053],[120.77482395200002,17.10802099300002],[120.81235520500002,17.155871674000025],[120.75133329500011,17.15525632500004],[120.73368256900007,17.167989204000037],[120.68144676200005,17.18662150900008],[120.67840099500005,17.25683886900003],[120.63616998800002,17.275628543000032],[120.61194929200009,17.302219217000076],[120.56675985500011,17.30715998400006],[120.5378136380001,17.356986044000053],[120.57786001500004,17.430012811000037],[120.58165948100009,17.471827468000072],[120.56549074100006,17.50175551600006],[120.54333671200003,17.492196233000076],[120.51159320200009,17.49823266400005],[120.47441593400005,17.484247811000042],[120.46816717700004,17.51472706000004],[120.48964597200006,17.55323366400006],[120.48809572800008,17.58461679900006],[120.49781832400004,17.625130266000042],[120.51638505600012,17.649240339000077],[120.54274383600011,17.735323652000037],[120.57182232500008,17.786033365000037]]]},"properties":{"adm1_psgc":100000000,"adm2_psgc":102900000,"adm2_en":"Ilocos Sur","geo_level":"Prov","len_crs":452374,"area_crs":2467458323,"len_km":452,"area_km2":2467},"id":102900000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.5650648840001,16.669766382000034],[120.53478210300011,16.720904921000056],[120.54544368800009,16.728928588000027],[120.54890816500007,16.767490429000077],[120.53514004700003,16.787169211000048],[120.53520039300008,16.816054985000047],[120.50695831400003,16.846549994000043],[120.51072422900006,16.918236059000037],[120.48999382900001,16.90546628500005],[120.46426010700009,16.914504663000056],[120.43577346200004,16.900497252000033],[120.41079750900008,16.920904919000066],[120.39798862300006,16.879663127000075],[120.33528829000012,16.83673898400002],[120.32519550100007,16.799130766000072],[120.34119219000003,16.735108901000046],[120.33250059400007,16.671132731000053],[120.31053996600006,16.64868405400005],[120.316417795,16.629300101000073],[120.29732813300008,16.604885739000053],[120.30120534600007,16.581581564000036],[120.32080571000006,16.568388156000022],[120.3042632260001,16.505451922000077],[120.32744159500011,16.478839367000035],[120.33471454400002,16.43134799100005],[120.32121695400006,16.38247930000006],[120.34361002100003,16.345948905000053],[120.33972041600009,16.307229315000036],[120.34790061800003,16.28190458400007],[120.40133064300005,16.249058478000048],[120.41726211800005,16.20473609300006],[120.5066795030001,16.206713226000034],[120.51182322200009,16.23220132700004],[120.51669938400006,16.249475371000077],[120.50082950600007,16.293355268000028],[120.494724172,16.347753779000076],[120.4690371590001,16.37975687500005],[120.44461437400001,16.38612987700003],[120.46996988700005,16.424879316000037],[120.47311491200001,16.47272088900007],[120.4673463900001,16.502706239000076],[120.48809029900006,16.540866315000073],[120.5126313620001,16.550257849000044],[120.51785667800004,16.594691728000043],[120.5650648840001,16.669766382000034]]]},"properties":{"adm1_psgc":100000000,"adm2_psgc":103300000,"adm2_en":"La Union","geo_level":"Prov","len_crs":262415,"area_crs":1414080983,"len_km":262,"area_km2":1414},"id":103300000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[119.91216765100012,16.39342735000002],[119.96124428600001,16.36946695300003],[119.96127291700009,16.39872865900003],[119.93368374500005,16.42496817500006],[119.91397544300004,16.422775155000068],[119.91216765100012,16.39342735000002]]],[[[120.41726211800005,16.20473609300006],[120.42313200600006,16.162379255000072],[120.35948532600003,16.093014466000053],[120.32808684000007,16.069481077000034],[120.28393004600002,16.050265633000038],[120.21752771900003,16.03684232300003],[120.18823561700002,16.04851483400006],[120.14400125200005,16.038412460000075],[120.09616972100002,16.069181764000067],[120.08852784300008,16.108407232000047],[120.10186390100013,16.13053090600005],[120.09609883400003,16.156413629000046],[120.02906665700004,16.19001124800008],[120.01650739200011,16.17019259100005],[119.977052812,16.228443819000063],[119.93556626400006,16.23986463000006],[119.9140756040001,16.26221283700005],[119.91421518900006,16.300979208000054],[119.93020722400003,16.361710845000065],[119.90141155100004,16.392167997000058],[119.87997107600005,16.390971771000064],[119.85646095800007,16.368207323000036],[119.81668234300004,16.360016235000046],[119.78877653400002,16.332683557000053],[119.77371314200002,16.280572957000057],[119.78354874100012,16.238800767000043],[119.7644079270001,16.210253697000038],[119.75490576600009,16.171478125000014],[119.76913519400011,16.165706982000074],[119.77799512500009,16.12433034400004],[119.76360343300009,16.112800072000027],[119.75676450000002,16.05474917400005],[119.77356094800005,16.02139463000003],[119.74972090100005,15.965595011000058],[119.76501464700004,15.926094047000051],[119.80454822,15.922644882000045],[119.81211371200006,15.955791413000036],[119.85466878400007,15.962626218000025],[119.90487234400007,15.86574382600003],[119.91279496000006,15.835461123000073],[119.90178234300005,15.807124243000034],[119.97349795700005,15.804924678000074],[119.99890120200008,15.819663963000044],[120.01961753400008,15.872207125000045],[120.03641615200002,15.874149902000056],[120.06062831300004,15.843698523000057],[120.1126600240001,15.82891142400007],[120.14429317400004,15.82619759400006],[120.15845308700013,15.771714149000047],[120.17777614100008,15.735479338000058],[120.21245195000006,15.687199554000074],[120.2528567830001,15.617769571000052],[120.26539332200002,15.639273167000056],[120.31116236500009,15.644613677000052],[120.3278619250001,15.680753150000044],[120.35839257500004,15.711756747000043],[120.36227633300007,15.735466716000072],[120.39426220300005,15.755677791000036],[120.42768256700003,15.753784435000057],[120.46759425200003,15.722242866000038],[120.52367794700002,15.75647107700007],[120.55103785800009,15.763746918000043],[120.58036818900007,15.82990640500003],[120.6036309120001,15.860894016000035],[120.6150636640001,15.815561238000045],[120.69093991600005,15.831160646000058],[120.73089299500008,15.851010298000066],[120.79019697800004,15.827182218000072],[120.81905751900001,15.793215701000065],[120.839224725,15.83120741500005],[120.85593758500012,15.836526259000037],[120.872612623,15.868065273000072],[120.87386427500007,15.896079757000056],[120.90151585000001,15.912567670000042],[120.92052940700013,15.966318216000047],[120.8961103580001,16.042520563000043],[120.84150888600004,16.168612326000076],[120.76891381100006,16.198050425000076],[120.628418151,16.18062420900003],[120.55802100200003,16.218416174000026],[120.51182322200009,16.23220132700004],[120.5066795030001,16.206713226000034],[120.41726211800005,16.20473609300006]]],[[[119.98968519800007,16.35010211800005],[119.95141277900005,16.33275043900005],[119.93343578000008,16.295498688000066],[119.99855842700003,16.223865776000025],[120.01938622500008,16.25083022800004],[119.99926111,16.281138708000064],[120.0198274080001,16.31102504500006],[119.99816665500009,16.323103896000077],[119.98968519800007,16.35010211800005]]]]},"properties":{"adm1_psgc":100000000,"adm2_psgc":105500000,"adm2_en":"Pangasinan","geo_level":"Prov","len_crs":789136,"area_crs":5161200257,"len_km":789,"area_km2":5161},"id":105500000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.80285287400011,20.688200545000026],[121.83902334500009,20.70846291900005],[121.85371311900008,20.723667880000054],[121.85665217100008,20.75136337400005],[121.876226082,20.759859551000027],[121.86785084400003,20.781479426000036],[121.88034716900007,20.794038180000026],[121.88019767400012,20.81996234900004],[121.85979046400007,20.836012216000025],[121.83686854900009,20.825403919000053],[121.82822395500011,20.789113772000064],[121.81520760500008,20.76027192200007],[121.80095918600011,20.754521984000068],[121.78276832400002,20.721662759000022],[121.80285287400011,20.688200545000026]]],[[[121.91524715200002,20.355675892000026],[121.95030493400009,20.348728030000075],[121.98071256100002,20.38329184900004],[121.9624234910001,20.41261390800003],[121.98629980400007,20.43804806300005],[122.01393450600007,20.448070017000077],[122.03567570900007,20.46795041900003],[122.02785446300004,20.481029539000073],[122.0029536280001,20.48946827800006],[121.97558691100004,20.471562048000067],[121.95695717300009,20.46866799100007],[121.96756219300005,20.44671681300002],[121.94565098900011,20.41561325300006],[121.92732569300004,20.40928706400006],[121.91524715200002,20.355675892000026]]],[[[121.85854826500008,20.26028199000007],[121.8723958920001,20.28412039600005],[121.88350032300004,20.285062047000046],[121.8889120790001,20.31325944400004],[121.87061830200003,20.340815648000046],[121.84485138900006,20.355371437000034],[121.83795049800004,20.324640487000064],[121.8406808090001,20.287724014000048],[121.85854826500008,20.26028199000007]]],[[[121.80715731700002,20.29992142900004],[121.8195575970001,20.326299685000038],[121.80001695500006,20.33409282200006],[121.79855419000012,20.308395397000027],[121.80715731700002,20.29992142900004]]]]},"properties":{"adm1_psgc":200000000,"adm2_psgc":200900000,"adm2_en":"Batanes","geo_level":"Prov","len_crs":230060,"area_crs":201280837,"len_km":230,"area_km2":201},"id":200900000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.95962747100009,19.47584474100006],[121.99049111600004,19.50374459600005],[121.99094934600011,19.556471327000054],[121.96944268900005,19.57392396600005],[121.94367013100008,19.55532832800003],[121.89602770200008,19.549136694000023],[121.89968606800007,19.51788525400008],[121.95962747100009,19.47584474100006]]],[[[121.51161315600007,19.244224647000063],[121.5103670090001,19.257692546000044],[121.53967262900005,19.268404838000034],[121.53945250100003,19.28776479900006],[121.522910367,19.318213812000074],[121.52933978500006,19.348736603000077],[121.5150989450001,19.38848362100003],[121.50021131200005,19.370893983000027],[121.48158188600006,19.371944167000034],[121.40689028000008,19.393340091000027],[121.39233084700004,19.388337721000028],[121.38829911200003,19.36970234400007],[121.36074723500008,19.351019670000024],[121.39081637600009,19.32857758600006],[121.39004284300006,19.300925148000033],[121.40934532900008,19.283002211000053],[121.46808673800003,19.266573349000055],[121.51161315600007,19.244224647000063]]],[[[121.238831623,19.01277019300005],[121.25384397300002,19.02859803300004],[121.24765641300007,19.103454675000027],[121.23644782000008,19.12630365200005],[121.23153837600013,19.15601165000004],[121.21054603800009,19.14248746000004],[121.19568852400003,19.09639591600006],[121.1991405240001,19.059833291000082],[121.21512476900011,19.03866495100004],[121.23525748600002,19.03066392500006],[121.238831623,19.01277019300005]]],[[[121.85594979400003,18.812052408000053],[121.87760347300002,18.827192575000026],[121.89103888600005,18.86850559600003],[121.92859190500006,18.88587094300004],[121.95563991500002,18.907532332000073],[121.96056807400008,18.935473530000024],[121.97919964900008,18.935285200000067],[121.99294018800003,18.958930634000073],[121.96462497200001,18.973609008000032],[121.94489424800007,19.00180591300006],[121.89702695500011,19.00125293600007],[121.86815825600002,18.97468199900004],[121.87060851000003,18.946850638000058],[121.85108862800007,18.927983965000063],[121.87138301200002,18.893874993000054],[121.86272099900009,18.880893620000048],[121.8346055610001,18.87161035400004],[121.82624672500003,18.860767505000062],[121.83839260600007,18.82039829900003],[121.85594979400003,18.812052408000053]]],[[[121.31633801200006,18.839724181000065],[121.37379818800002,18.850166024000035],[121.45296128000007,18.855661315000077],[121.47928180800011,18.872838815000016],[121.41511844700005,18.905782884000068],[121.37770847600007,18.898717593000068],[121.36120551600006,18.888151987000068],[121.34473650600013,18.89134155500005],[121.31224013400004,18.877496288000028],[121.28516976200001,18.884799910000023],[121.27516214500008,18.85785132800004],[121.28954569600012,18.844289756000027],[121.31633801200006,18.839724181000065]]],[[[122.17296890000013,17.58454244400002],[122.1633278490001,17.61140685200007],[122.16314383600002,17.676210140000023],[122.1685222410001,17.69865232500007],[122.14434510100011,17.73768922900007],[122.14839150600005,17.75418382500004],[122.13788191900005,17.779920099000037],[122.13990921300002,17.802975500000056],[122.15538423600003,17.813995345000016],[122.15268325200009,17.839762533000055],[122.16836572800001,17.850726985000048],[122.16563083300002,17.88351555800005],[122.1895840420001,17.911332769000065],[122.18115558900003,17.92167638600006],[122.17739595700003,17.969262805000028],[122.18835812100008,18.01631366800007],[122.17438470100002,18.032602939000068],[122.17723768600003,18.054309273000055],[122.16477260100011,18.071423221000032],[122.18174746000011,18.11664994700004],[122.19065588600007,18.11623225300008],[122.21581376700011,18.15176181200008],[122.26353889600011,18.170332990000073],[122.26609010800007,18.18598311400007],[122.28729110900008,18.199992964000046],[122.30732023300004,18.240391818000028],[122.32031544700008,18.247146152000024],[122.33747537500005,18.308790129000048],[122.32042427600004,18.37897686800005],[122.29334246400003,18.411663025000045],[122.276972827,18.416314178000047],[122.2485903500001,18.450705274000025],[122.24047656200003,18.477016673000037],[122.23910830200009,18.511822059000046],[122.22375948100013,18.522506965000044],[122.18955019300006,18.51154951100005],[122.14665067700001,18.507007084000062],[122.14808044500013,18.48227639700008],[122.12468801800003,18.423745764000042],[122.131934612,18.388181351000068],[122.1178778970001,18.37452400700004],[122.06315085700011,18.342769002000068],[122.05292684000004,18.321735307000043],[122.02781465200007,18.30783786200004],[122.01116399400007,18.287890254000047],[121.93385582600003,18.266702418000023],[121.90842681300002,18.269700620000037],[121.85226362400012,18.284368354000037],[121.64395728800002,18.358924992000027],[121.62151758600008,18.35134620900004],[121.60640043900004,18.371869421000042],[121.53602248400011,18.404502226000034],[121.48466872900009,18.435622809000048],[121.45158316900007,18.460188465000044],[121.31367422700009,18.521188671000058],[121.28902353300009,18.536927648000066],[121.19677468800012,18.60882792400002],[121.1609823140001,18.62232623400007],[121.12366305400008,18.628709585000024],[121.09748466400005,18.626217995000044],[121.09069812800011,18.61456853700002],[121.06568194700003,18.607342463000066],[121.03744608100011,18.61542819800007],[120.97272398500002,18.581773456000064],[120.97645367700012,18.568958937000048],[120.96914518200002,18.510116371000038],[120.95867309800006,18.46320241200004],[121.002873797,18.466105643000045],[121.0234730630001,18.498688611000034],[121.03880811000012,18.50503012800004],[121.04277930400009,18.52818576600003],[121.06136538900012,18.539197991000037],[121.09350099600012,18.541745912000067],[121.08906431300011,18.495391214000048],[121.11848091500008,18.54311065400004],[121.15600338400009,18.543774998000064],[121.1678637000001,18.521977657000036],[121.2220811540001,18.500580942000056],[121.22654139600003,18.43647132900003],[121.24884436800005,18.42887990300005],[121.28555701000005,18.388537952000032],[121.3186229800001,18.38715477900007],[121.4023827430001,18.340896047000054],[121.41583439900012,18.32357207300004],[121.4612568030001,18.31461976800006],[121.48022320600012,18.30637117400005],[121.46462696400012,18.284910661000026],[121.48948360700003,18.23884498300003],[121.48189198400009,18.14438367100007],[121.468931816,18.12564935000006],[121.46035909600005,18.049410337000037],[121.427838,18.035335404000023],[121.36446941600003,18.061619119000056],[121.34689143800007,18.03861084700003],[121.3317759140001,17.99122467000007],[121.31511820900005,17.97078315600004],[121.35745211900009,17.922368543000058],[121.34696177600006,17.879415140000045],[121.32413865500008,17.84713067200004],[121.32155435200002,17.80423081600002],[121.35867264400008,17.80464696600006],[121.38829731500005,17.793630291000053],[121.41411788300002,17.76319366200005],[121.42825329100003,17.72960822100004],[121.43675604700002,17.671347725000036],[121.449612956,17.661005241000055],[121.4663220020001,17.67232157400002],[121.48512366300008,17.647321689000027],[121.49661415900005,17.591042718000036],[121.546723013,17.580621351000048],[121.59972009100011,17.548195070000077],[121.61420260300008,17.560316989000057],[121.6259729310001,17.528587955000035],[121.64723067800004,17.50048373000004],[121.70381581100003,17.50181446600004],[121.75512754700004,17.509929960000015],[121.78851574600003,17.52549255400003],[121.82031676800013,17.53140441100004],[121.89488360000009,17.530313728000067],[122.04625641700011,17.570316798000018],[122.17296890000013,17.58454244400002]]],[[[122.13331402600011,18.58171632400007],[122.11635635300003,18.56726133500007],[122.111250734,18.548616460000062],[122.12439398700009,18.540791775000063],[122.11802079000006,18.520305017000055],[122.15011540800003,18.51740799300006],[122.14623244900007,18.53209681000004],[122.15771211900007,18.55483806500007],[122.15386680000006,18.576478639000076],[122.13331402600011,18.58171632400007]]]]},"properties":{"adm1_psgc":200000000,"adm2_psgc":201500000,"adm2_en":"Cagayan","geo_level":"Prov","len_crs":1135169,"area_crs":8794377504,"len_km":1135,"area_km2":8794},"id":201500000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[122.17296890000013,17.58454244400002],[122.04625641700011,17.570316798000018],[121.89488360000009,17.530313728000067],[121.82031676800013,17.53140441100004],[121.78851574600003,17.52549255400003],[121.75512754700004,17.509929960000015],[121.70381581100003,17.50181446600004],[121.64723067800004,17.50048373000004],[121.63792704800005,17.453543829000072],[121.62793480900008,17.431389672000012],[121.60608069200009,17.421432186000064],[121.59347822600012,17.39691670600007],[121.58219454800007,17.35355906800003],[121.55993127700003,17.350483108000045],[121.5387001150001,17.317268562000038],[121.53017478800008,17.274919214000022],[121.54497556000001,17.26489446200003],[121.54278393400011,17.247162222000043],[121.54913468000008,17.19652380800005],[121.56139800500011,17.183361080000054],[121.56715873800012,17.13502168600007],[121.56604146900008,17.08572494500004],[121.57149082100013,17.040943460000054],[121.56071687200006,17.00945781000007],[121.56822243500005,16.909511535000032],[121.54887157900009,16.87368920000006],[121.52132234000011,16.838934767000065],[121.47913536400007,16.83597295800007],[121.41951945100004,16.817469334000066],[121.38601317000008,16.796678027000038],[121.35409018100007,16.783638653000025],[121.33865075400001,16.75348573900003],[121.370574905,16.75200994000005],[121.3902645050001,16.694436527000054],[121.3971688790001,16.649877948000036],[121.40618698600008,16.639204305000074],[121.44575299200004,16.634300799000066],[121.46601437900006,16.641396523000026],[121.55481491400006,16.628912362000047],[121.57858267100005,16.598471049000068],[121.58379264000007,16.575755187000027],[121.59952867000004,16.57575489800007],[121.62547554000002,16.54907837400003],[121.65903144000005,16.493009112000035],[121.6838058630001,16.47574939900005],[121.69022134400007,16.45900179400007],[121.74500357300008,16.393169809000025],[121.79286491500012,16.408780795000038],[121.80059177500004,16.417749977000028],[121.88729434000004,16.449180033000065],[121.96387054100002,16.484835325000066],[122.0177337130001,16.51702452700005],[122.05880819100003,16.50925477800007],[122.21427288000007,16.47984429100006],[122.23059986800001,16.48400908800005],[122.25081580300002,16.516272372000056],[122.276357619,16.52470019200007],[122.29826674100002,16.55179161800004],[122.32427408,16.61079278400006],[122.35061364100011,16.655135019000056],[122.35782234800001,16.677408492000037],[122.40411025100002,16.748780186000033],[122.41872644800003,16.787039113000045],[122.43348266200009,16.797123175000028],[122.43148398400001,16.831394414000044],[122.45921524000005,16.87385955900004],[122.46099050500004,16.917758164000077],[122.47582282200007,16.95136893600005],[122.46492127200008,16.96632771300005],[122.4877791450001,17.02036920300003],[122.51007473200004,17.03759480300005],[122.51993955000012,17.09063590800002],[122.51501961200006,17.136765427000057],[122.48016162300007,17.116009943000044],[122.45810080900002,17.11450352800006],[122.41855300600002,17.138062347000073],[122.41087640400008,17.170569783000076],[122.42011281500004,17.191682057000037],[122.42235368700005,17.254440021000054],[122.44369316000005,17.26380267100007],[122.43948498500004,17.287668364000066],[122.42170372600003,17.30357915200005],[122.40707924700007,17.33359686500006],[122.39356083700011,17.322508150000033],[122.37331036700003,17.352376717000027],[122.35427872700006,17.33531371500004],[122.32235627500008,17.34242186200004],[122.31180370200002,17.33243779500003],[122.28750753300007,17.338946431000068],[122.2858022470001,17.360982876000037],[122.2653315120001,17.353988048000076],[122.24575531400002,17.366183745000054],[122.2447460610001,17.409375874000034],[122.21478842500005,17.455597506000064],[122.19482784800006,17.501074138000035],[122.18474922400004,17.54193998800002],[122.19068245400001,17.547957689000043],[122.17296890000013,17.58454244400002]]]},"properties":{"adm1_psgc":200000000,"adm2_psgc":203100000,"adm2_en":"Isabela","geo_level":"Prov","len_crs":606202,"area_crs":10489909469,"len_km":606,"area_km2":10489},"id":203100000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.44575299200004,16.634300799000066],[121.40618698600008,16.639204305000074],[121.3971688790001,16.649877948000036],[121.3902645050001,16.694436527000054],[121.370574905,16.75200994000005],[121.33865075400001,16.75348573900003],[121.31434472400008,16.717911633000025],[121.31541259900008,16.701307632000066],[121.28823650000005,16.68623673400003],[121.25928948300007,16.65178447000005],[121.23604050400002,16.654163596000043],[121.19690026700006,16.639026568000077],[121.16058286600004,16.63868909200005],[121.1354977630001,16.644747052000074],[121.10563417500009,16.63056137700005],[121.07213162600011,16.627830254000056],[121.03570305200004,16.61000610700006],[120.98371653300002,16.56947082300007],[120.94753998600004,16.57919712100005],[120.92950614800007,16.600053544000048],[120.90440899500003,16.595359904000077],[120.89210972500007,16.558460226000022],[120.88320633500008,16.505391507000066],[120.889427,16.436073],[120.87814482400007,16.421579058000077],[120.87115844600008,16.384243957000024],[120.84552298100004,16.319500078000026],[120.82832254100003,16.31969874500004],[120.80005260900009,16.30484574400003],[120.76896590800004,16.19803365700005],[120.84150888600004,16.168612326000076],[120.8578886040001,16.130260565000068],[120.87044651800012,16.118870179000055],[120.94003228000008,16.133600949000023],[120.98789352400001,16.125824962000024],[120.9987737030001,16.136511258000038],[121.04773934000002,16.137989391000076],[121.0878713080001,16.11399938200003],[121.11953343000006,16.113344204000043],[121.17424918400003,16.090108902000054],[121.18504504700002,16.07174795900005],[121.19210574800002,15.997633897000071],[121.18785990100002,15.948386911000059],[121.19399818500007,15.922087606000046],[121.22285791500008,15.872750951000056],[121.28033899700006,15.767132018000035],[121.30590318500003,15.78212419000005],[121.31771017400001,15.804652432000069],[121.37376803400002,15.831617787000027],[121.47114962000002,15.886741050000069],[121.46354426900007,15.926616156000026],[121.44036342000004,15.936710192000074],[121.3407596090001,16.021969981000037],[121.36543708700003,16.066626002000078],[121.32284322700004,16.093650980000064],[121.30264075500008,16.116559135000042],[121.28703627500012,16.148544101000024],[121.32651811800008,16.15783594700002],[121.29989098200008,16.209559719000023],[121.34825628400006,16.19670942400006],[121.38376232500002,16.201110999000036],[121.41985524200005,16.231628588000035],[121.432033595,16.254100451000053],[121.4670669950001,16.270934803000046],[121.520757752,16.339014960000043],[121.48150201400004,16.357183331000044],[121.43716017000008,16.383300146000067],[121.44860449300008,16.428118329000032],[121.40003235000007,16.434969730000034],[121.376865703,16.451005424000073],[121.3577187190001,16.498419118000076],[121.38468610900009,16.506486988000066],[121.39264336400004,16.54154879800006],[121.39985675100002,16.607053096000072],[121.44575299200004,16.634300799000066]]]},"properties":{"adm1_psgc":200000000,"adm2_psgc":205000000,"adm2_en":"Nueva Vizcaya","geo_level":"Prov","len_crs":403864,"area_crs":4126548282,"len_km":403,"area_km2":4126},"id":205000000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[122.05880819100003,16.50925477800007],[122.0177337130001,16.51702452700005],[121.96387054100002,16.484835325000066],[121.88729434000004,16.449180033000065],[121.80059177500004,16.417749977000028],[121.79286491500012,16.408780795000038],[121.74500357300008,16.393169809000025],[121.69022134400007,16.45900179400007],[121.6838058630001,16.47574939900005],[121.65903144000005,16.493009112000035],[121.62547554000002,16.54907837400003],[121.59952867000004,16.57575489800007],[121.58379264000007,16.575755187000027],[121.57858267100005,16.598471049000068],[121.55481491400006,16.628912362000047],[121.46601437900006,16.641396523000026],[121.44575299200004,16.634300799000066],[121.39985675100002,16.607053096000072],[121.39264336400004,16.54154879800006],[121.38468610900009,16.506486988000066],[121.3577187190001,16.498419118000076],[121.376865703,16.451005424000073],[121.40003235000007,16.434969730000034],[121.44860449300008,16.428118329000032],[121.43716017000008,16.383300146000067],[121.48150201400004,16.357183331000044],[121.520757752,16.339014960000043],[121.4670669950001,16.270934803000046],[121.432033595,16.254100451000053],[121.41985524200005,16.231628588000035],[121.38376232500002,16.201110999000036],[121.34825628400006,16.19670942400006],[121.29989098200008,16.209559719000023],[121.32651811800008,16.15783594700002],[121.28703627500012,16.148544101000024],[121.30264075500008,16.116559135000042],[121.32284322700004,16.093650980000064],[121.36543708700003,16.066626002000078],[121.3407596090001,16.021969981000037],[121.44036342000004,15.936710192000074],[121.46354426900007,15.926616156000026],[121.4745488740001,15.92984777800007],[121.52882642900009,15.969868599000048],[121.57062539300013,16.01126710500006],[121.62897873000009,16.063865467000024],[121.72325119700008,16.144655707000027],[121.764923618,16.173819910000077],[121.78125155300006,16.19321946900004],[121.84589590900009,16.249155589000054],[121.89353425500009,16.301854026000058],[121.96723491500006,16.40023248400007],[122.02489034600002,16.46535309900003],[122.05880819100003,16.50925477800007]]]},"properties":{"adm1_psgc":200000000,"adm2_psgc":205700000,"adm2_en":"Quirino","geo_level":"Prov","len_crs":323147,"area_crs":2767354533,"len_km":323,"area_km2":2767},"id":205700000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.55426459000012,14.820737035000036],[120.52996468200003,14.832459915000069],[120.50599482200005,14.861656435000043],[120.47641131900004,14.91962046200007],[120.46126986800006,14.921266418000073],[120.42280570000003,14.914471035000073],[120.40665743800001,14.88570509300007],[120.34119403900002,14.857304444000023],[120.34021008900005,14.817820355000038],[120.36109152900009,14.792929272000038],[120.3593488030001,14.776626151000073],[120.2782164140001,14.73891010900007],[120.2502833420001,14.726266689000056],[120.24818179700004,14.692287460000045],[120.29232886400007,14.655530363000024],[120.31487632400001,14.626121303000048],[120.32877685200003,14.636236736000054],[120.34858773600003,14.619553496000036],[120.36803668300001,14.625765517000048],[120.39280916200006,14.587940439000025],[120.38291627700005,14.568593554000076],[120.38998949300002,14.537892413000067],[120.37474302800003,14.524687197000045],[120.38853580900002,14.460073983000026],[120.44478092700002,14.446346042000073],[120.46535926700007,14.421280646000067],[120.48639886800004,14.43344834000004],[120.55401782400008,14.422366258000064],[120.5763699160001,14.431959074000074],[120.608716791,14.478447205000064],[120.60842371700005,14.533553079000054],[120.58742078800003,14.589587866000043],[120.5840988020001,14.643158220000025],[120.54658337400008,14.726362146000042],[120.55617815100005,14.79959864900007],[120.55426459000012,14.820737035000036]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":300800000,"adm2_en":"Bataan","geo_level":"Prov","len_crs":290679,"area_crs":1246275464,"len_km":290,"area_km2":1246},"id":300800000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.31215264300012,15.198769701000064],[121.25093778800012,15.201790574000022],[121.20653523100007,15.220440853000069],[121.18592226200008,15.265765786000035],[121.14503048900009,15.272196883000047],[121.1163055830001,15.265820260000053],[121.07470719000004,15.268369465000033],[121.00487735400009,15.245915766000055],[120.98568132400011,15.227066111000056],[120.92865891600002,15.216318620000036],[120.92127848400001,15.155285676000062],[120.94784750500001,15.136836239000042],[120.93328239500012,15.089088583000038],[120.90273443800004,15.08579794200006],[120.89808489900008,15.072300916000074],[120.91405588500004,15.051393264000069],[120.90889529800005,15.022694277000024],[120.8781569030001,15.007854643000027],[120.87914163500011,14.982093235000042],[120.85629099500012,14.976220701000043],[120.83266964000008,14.95703023000004],[120.77246186800005,14.924464991000036],[120.74316107100003,14.93094760900004],[120.7257576410001,14.910641975000031],[120.7216121670001,14.873341453000021],[120.69810754700006,14.830804838000063],[120.69958991900013,14.814917805000047],[120.6872372130001,14.770876218000069],[120.75003958600007,14.75881515900005],[120.7691687680001,14.764475984000063],[120.80138175000002,14.754859573000033],[120.820108536,14.760218699000065],[120.8551997830001,14.729142895000047],[120.90340439300009,14.704011029000068],[120.91841488700004,14.712960826000025],[120.94315945500011,14.68961009700007],[120.95312750500011,14.694240067000067],[120.92596146500011,14.734299748000069],[120.97852281100006,14.73480671900006],[120.9901370550001,14.75706363100005],[121.02402399100004,14.763034879000028],[121.02796889500009,14.781271736000066],[121.10445726500006,14.77068312600005],[121.16528463600002,14.823417534000043],[121.20804184000006,14.81794121400003],[121.21925184400004,14.833223191000052],[121.25299686000005,14.829226647000041],[121.33035662500004,14.834802543000022],[121.3401122450001,14.886441354000056],[121.33820501800007,14.947222596000074],[121.34785653300003,14.996370968000065],[121.31965715800004,15.11639764200004],[121.31879139300008,15.164067442000029],[121.31215264300012,15.198769701000064]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":301400000,"adm2_en":"Bulacan","geo_level":"Prov","len_crs":357485,"area_crs":2710754756,"len_km":357,"area_km2":2710},"id":301400000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.28476349300001,15.754418537000051],[121.28033899700006,15.767132018000035],[121.19399818500007,15.922087606000046],[121.18785990100002,15.948386911000059],[121.19210574800002,15.997633897000071],[121.18504504700002,16.07174795900005],[121.17424918400003,16.090108902000054],[121.11953343000006,16.113344204000043],[121.0878713080001,16.11399938200003],[121.04773934000002,16.137989391000076],[120.9987737030001,16.136511258000038],[120.98789352400001,16.125824962000024],[120.94003228000008,16.133600949000023],[120.87044651800012,16.118870179000055],[120.87446505100003,16.093515548000028],[120.8961103580001,16.042520563000043],[120.92052940700013,15.966318216000047],[120.90151585000001,15.912567670000042],[120.87386427500007,15.896079757000056],[120.872612623,15.868065273000072],[120.85593758500012,15.836526259000037],[120.839224725,15.83120741500005],[120.81905751900001,15.793215701000065],[120.79019697800004,15.827182218000072],[120.73089299500008,15.851010298000066],[120.69093991600005,15.831160646000058],[120.67347150400006,15.831639223000025],[120.6150636640001,15.815561238000045],[120.62845097100002,15.731305624000074],[120.65766849400005,15.662499082000068],[120.69694031000004,15.618043090000068],[120.74181079700008,15.618811382000047],[120.74803815300005,15.593195428000058],[120.7325260680001,15.583154759000026],[120.72099495400006,15.550356954000053],[120.74540941400006,15.505163393000034],[120.74376207000013,15.450884910000067],[120.76160618700011,15.435547245000068],[120.76236231700011,15.417785005000042],[120.74187423800004,15.381475093000065],[120.7384524040001,15.333535906000066],[120.75572014200009,15.319438281000034],[120.73421095200001,15.277158338000046],[120.73540473100003,15.257245636000048],[120.76835413100002,15.25120829800005],[120.7901530040001,15.212853917000075],[120.8381835470001,15.201553705000034],[120.86542324400013,15.176232549000078],[120.890312246,15.18523474500006],[120.90346552800008,15.213618034000032],[120.92865891600002,15.216318620000036],[120.98568132400011,15.227066111000056],[121.00487735400009,15.245915766000055],[121.07470719000004,15.268369465000033],[121.1163055830001,15.265820260000053],[121.14503048900009,15.272196883000047],[121.18592226200008,15.265765786000035],[121.20653523100007,15.220440853000069],[121.25093778800012,15.201790574000022],[121.31215264300012,15.198769701000064],[121.33389083800013,15.295655260000045],[121.35379088200011,15.345691532000043],[121.33999648100006,15.382839272000068],[121.35835769500011,15.406953526000052],[121.378521524,15.485011371000047],[121.28476349300001,15.754418537000051]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":304900000,"adm2_en":"Nueva Ecija","geo_level":"Prov","len_crs":417819,"area_crs":5506443156,"len_km":417,"area_km2":5506},"id":304900000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.73421095200001,15.277158338000046],[120.70041309500004,15.263124283000025],[120.66793663200009,15.277760137000032],[120.63261738900007,15.259523647000037],[120.59331824000002,15.265997952000077],[120.547660768,15.254440064000052],[120.52199098000006,15.226423853000028],[120.49421364300007,15.225257195000042],[120.440227616,15.20099907200006],[120.41835810100008,15.181353086000055],[120.36759662500005,15.167097115000045],[120.35605737500009,15.13502351100004],[120.36503970000001,15.108136663000039],[120.406873,15.074102701000069],[120.42228522400002,15.041691793000034],[120.42091735000007,14.990123146000032],[120.44769220000002,14.960627217000026],[120.46126986800006,14.921266418000073],[120.47641131900004,14.91962046200007],[120.50599482200005,14.861656435000043],[120.52996468200003,14.832459915000069],[120.55426459000012,14.820737035000036],[120.58601226000008,14.82406656300003],[120.6025850740001,14.815458633000047],[120.6523424180001,14.767872625000056],[120.6872372130001,14.770876218000069],[120.69958991900013,14.814917805000047],[120.69810754700006,14.830804838000063],[120.7216121670001,14.873341453000021],[120.7257576410001,14.910641975000031],[120.74316107100003,14.93094760900004],[120.77246186800005,14.924464991000036],[120.83266964000008,14.95703023000004],[120.85629099500012,14.976220701000043],[120.87914163500011,14.982093235000042],[120.8781569030001,15.007854643000027],[120.90889529800005,15.022694277000024],[120.91405588500004,15.051393264000069],[120.89808489900008,15.072300916000074],[120.90273443800004,15.08579794200006],[120.93328239500012,15.089088583000038],[120.94784750500001,15.136836239000042],[120.92127848400001,15.155285676000062],[120.92865891600002,15.216318620000036],[120.90346552800008,15.213618034000032],[120.890312246,15.18523474500006],[120.86542324400013,15.176232549000078],[120.8381835470001,15.201553705000034],[120.7901530040001,15.212853917000075],[120.76835413100002,15.25120829800005],[120.73540473100003,15.257245636000048],[120.73421095200001,15.277158338000046]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":305400000,"adm2_en":"Pampanga","geo_level":"Prov","len_crs":291563,"area_crs":2115903632,"len_km":291,"area_km2":2115},"id":305400000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.6150636640001,15.815561238000045],[120.6036309120001,15.860894016000035],[120.5900943040001,15.862431135000065],[120.58036818900007,15.82990640500003],[120.55103785800009,15.763746918000043],[120.52367794700002,15.75647107700007],[120.46759425200003,15.722242866000038],[120.42768256700003,15.753784435000057],[120.39426220300005,15.755677791000036],[120.36227633300007,15.735466716000072],[120.35839257500004,15.711756747000043],[120.3278619250001,15.680753150000044],[120.31116236500009,15.644613677000052],[120.26539332200002,15.639273167000056],[120.2528567830001,15.617769571000052],[120.26404654900011,15.597693989000046],[120.223042,15.57605272200004],[120.18910368800005,15.516064781000066],[120.1724779860001,15.438335885000068],[120.16519461000007,15.36177375200003],[120.28224524300005,15.289590427000064],[120.33616555000003,15.235095099000032],[120.36759662500005,15.167097115000045],[120.41835810100008,15.181353086000055],[120.440227616,15.20099907200006],[120.49421364300007,15.225257195000042],[120.52199098000006,15.226423853000028],[120.547660768,15.254440064000052],[120.59331824000002,15.265997952000077],[120.63261738900007,15.259523647000037],[120.66793663200009,15.277760137000032],[120.70041309500004,15.263124283000025],[120.73421095200001,15.277158338000046],[120.75572014200009,15.319438281000034],[120.7384524040001,15.333535906000066],[120.74187423800004,15.381475093000065],[120.76236231700011,15.417785005000042],[120.76160618700011,15.435547245000068],[120.74376207000013,15.450884910000067],[120.74540941400006,15.505163393000034],[120.72099495400006,15.550356954000053],[120.7325260680001,15.583154759000026],[120.74803815300005,15.593195428000058],[120.74181079700008,15.618811382000047],[120.69694031000004,15.618043090000068],[120.65766849400005,15.662499082000068],[120.62845097100002,15.731305624000074],[120.6150636640001,15.815561238000045]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":306900000,"adm2_en":"Tarlac","geo_level":"Prov","len_crs":275154,"area_crs":2974676788,"len_km":275,"area_km2":2974},"id":306900000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[120.2528567830001,15.617769571000052],[120.21245195000006,15.687199554000074],[120.17777614100008,15.735479338000058],[120.15845308700013,15.771714149000047],[120.14429317400004,15.82619759400006],[120.1126600240001,15.82891142400007],[120.06062831300004,15.843698523000057],[120.03641615200002,15.874149902000056],[120.01961753400008,15.872207125000045],[119.99890120200008,15.819663963000044],[119.97349795700005,15.804924678000074],[119.90178234300005,15.807124243000034],[119.90023609300009,15.771063926000068],[119.90936622000004,15.754257368000028],[119.86918836400002,15.735833707000038],[119.89522472600005,15.711295255000039],[119.93221053600008,15.694479948000039],[119.93188576500006,15.666316756000068],[119.91571935500006,15.62584643900004],[119.90474981900003,15.620130864000034],[119.91792623500011,15.583544121000044],[119.93997353000009,15.558144939000043],[119.96154224600004,15.50421723100004],[119.94786384000008,15.482155624000027],[119.89982846100008,15.47766777800007],[119.91441569800007,15.443786707000067],[119.89009185200007,15.431010754000056],[119.90220778300012,15.40713038100006],[119.93558463000011,15.381309680000067],[119.96745294700007,15.343288895000057],[119.96395986600011,15.327698124000051],[120.0162021110001,15.264447562000045],[120.01053930100012,15.238335951000067],[120.02972292200002,15.189289101000044],[120.0595993190001,15.061823844000061],[120.05366806400002,15.035730695000037],[120.06390168400003,15.017936689000067],[120.06425760700006,14.98649978500003],[120.0561792200001,14.93731039500005],[120.06238576000011,14.918239844000027],[120.0543201800001,14.893539052000055],[120.06543045500005,14.86672488700003],[120.08404439700007,14.85287765600003],[120.10257851200005,14.807437442000033],[120.08350310900005,14.786746616000075],[120.13083897500007,14.775664694000062],[120.14846895800007,14.756340142000056],[120.18954915300003,14.750836982000065],[120.2033190410001,14.79767999600005],[120.21523077100007,14.809095295000073],[120.20762727500005,14.874339490000068],[120.2252995660001,14.877900965000036],[120.24475623600006,14.849407532000043],[120.26716135100003,14.846981645000028],[120.267623209,14.823748920000071],[120.2840905380001,14.800739975000052],[120.25780643200007,14.76451903800006],[120.25668235400008,14.746341670000051],[120.2782164140001,14.73891010900007],[120.3593488030001,14.776626151000073],[120.36109152900009,14.792929272000038],[120.34021008900005,14.817820355000038],[120.34119403900002,14.857304444000023],[120.40665743800001,14.88570509300007],[120.42280570000003,14.914471035000073],[120.46126986800006,14.921266418000073],[120.44769220000002,14.960627217000026],[120.42091735000007,14.990123146000032],[120.42228522400002,15.041691793000034],[120.406873,15.074102701000069],[120.36503970000001,15.108136663000039],[120.35605737500009,15.13502351100004],[120.36759662500005,15.167097115000045],[120.33616555000003,15.235095099000032],[120.28224524300005,15.289590427000064],[120.16519461000007,15.36177375200003],[120.1724779860001,15.438335885000068],[120.18910368800005,15.516064781000066],[120.223042,15.57605272200004],[120.26404654900011,15.597693989000046],[120.2528567830001,15.617769571000052]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":307100000,"adm2_en":"Zambales","geo_level":"Prov","len_crs":582660,"area_crs":3733936862,"len_km":582,"area_km2":3733},"id":307100000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.34785653300003,14.996370968000065],[121.35710532600002,15.011749193000067],[121.35137018900002,15.035906006000063],[121.37400455200009,15.095887405000038],[121.39460381500011,15.105961485000027],[121.40809682500004,15.182936998000056],[121.40232335200005,15.203701252000029],[121.41691950100004,15.21964939600002],[121.38064047200011,15.290072694000058],[121.37299956800008,15.32171117700005],[121.3850317450001,15.365060471000046],[121.40312952600004,15.384515089000043],[121.42548904700006,15.37100412300003],[121.45612017100005,15.411954795000042],[121.4730592630001,15.41668181400007],[121.48844016400005,15.462515176000066],[121.48449988900008,15.483463863000056],[121.49270334000005,15.520978898000068],[121.512142304,15.542092457000022],[121.53059794500007,15.545712518000071],[121.54251661,15.575917044000049],[121.59621008300007,15.642419078000046],[121.61703790600006,15.657411187000035],[121.61113166000007,15.707719990000044],[121.63716655000007,15.708217685000026],[121.63674170900005,15.748979476000041],[121.59829702500008,15.762418049000077],[121.58451588900006,15.753835847000058],[121.5645178310001,15.768322867000045],[121.55159618200004,15.81066733300003],[121.5478308590001,15.861242571000052],[121.554405502,15.897447717000034],[121.58006320000004,15.927955131000038],[121.60049794400005,15.934980471000076],[121.6261494460001,15.965536451000046],[121.65298387100007,15.972899435000041],[121.66501017000006,16.005500489000042],[121.71734526900002,16.040927647000046],[121.75789200800011,16.076082430000042],[121.7793574860001,16.062419646000023],[121.813044998,16.086483175000065],[121.83637628800011,16.09032705100003],[121.86155739700007,16.11604703300003],[121.9073406660001,16.12888269200005],[121.93698157800009,16.125986667000063],[121.96712696700003,16.136384588000052],[121.98275792800007,16.15677384300005],[122.020868,16.18019077400004],[122.03742231100011,16.17453355400005],[122.06772900800003,16.190797576000026],[122.06349797500003,16.223708996000024],[122.08482099300011,16.258823981000035],[122.10446615600006,16.26318962500005],[122.13939712800004,16.256261909000045],[122.11775431900003,16.214213216000076],[122.09509441500008,16.204547415000032],[122.09417613500011,16.17158541300006],[122.06174642300006,16.12965362200003],[122.03370429500002,16.111832442000036],[121.99423399800004,16.043701713000075],[122.03242999600002,16.050370203000057],[122.0700829430001,16.092578685000035],[122.07202991400004,16.122365236000057],[122.10691271300004,16.149554731000023],[122.1432184350001,16.19286253900003],[122.20333965200008,16.237566206000047],[122.20827416400003,16.27145518800006],[122.17997632000005,16.303677168000032],[122.190997153,16.333776695000044],[122.22509413500006,16.35704965000002],[122.22836002000007,16.39534024900007],[122.20026639000004,16.41520622400003],[122.19935632300006,16.433834282000085],[122.23038198000008,16.463996627000025],[122.21427288000007,16.47984429100006],[122.05880819100003,16.50925477800007],[122.02489034600002,16.46535309900003],[121.96723491500006,16.40023248400007],[121.89353425500009,16.301854026000058],[121.84589590900009,16.249155589000054],[121.78125155300006,16.19321946900004],[121.764923618,16.173819910000077],[121.72325119700008,16.144655707000027],[121.62897873000009,16.063865467000024],[121.52882642900009,15.969868599000048],[121.4745488740001,15.92984777800007],[121.47114962000002,15.886741050000069],[121.37376803400002,15.831617787000027],[121.31771017400001,15.804652432000069],[121.28476349300001,15.754418537000051],[121.378521524,15.485011371000047],[121.35835769500011,15.406953526000052],[121.33999648100006,15.382839272000068],[121.35379088200011,15.345691532000043],[121.33389083800013,15.295655260000045],[121.31215264300012,15.198769701000064],[121.31879139300008,15.164067442000029],[121.31965715800004,15.11639764200004],[121.34785653300003,14.996370968000065]]]},"properties":{"adm1_psgc":300000000,"adm2_psgc":307700000,"adm2_en":"Aurora","geo_level":"Prov","len_crs":736253,"area_crs":3029553529,"len_km":736,"area_km2":3029},"id":307700000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.08896686700008,13.569401490000072],[121.08531609700003,13.57366520200003],[121.05279495800005,13.555765870000071],[121.07441782,13.52998965200004],[121.09715144800009,13.536852737000059],[121.08896686700008,13.569401490000072]]],[[[120.83115867100003,13.68768679400006],[120.84260246900008,13.652000642000077],[120.866908093,13.645563303000072],[120.87259897000003,13.63465789600002],[120.90341105200002,13.624439212000024],[120.94251647100008,13.632079410000072],[120.93402842000012,13.655373922000022],[120.90771382900006,13.659066702000077],[120.88492621700003,13.654887412000047],[120.84114106800008,13.672337123000036],[120.83115867100003,13.68768679400006]]],[[[120.618347222,14.220246020000047],[120.610491066,14.227454464000063],[120.58854213500001,14.21399773400003],[120.59233886900007,14.20278900900007],[120.58667654000011,14.17554861600007],[120.59441020400006,14.154152346000048],[120.58044213600012,14.131404079000049],[120.59180190400002,14.122496121000038],[120.61597123900003,14.118051798000065],[120.62389206200011,14.107314115000067],[120.61703780300003,14.089199754000049],[120.62497698400011,14.063746114000024],[120.61800068000002,14.00694984200004],[120.63205137200009,13.984308782000028],[120.61612142700005,13.960633223000059],[120.62512483900004,13.895109801000045],[120.61879275400008,13.889984386000036],[120.61762334400008,13.86653645700005],[120.62347730300009,13.84557276500004],[120.62210515900006,13.811289915000033],[120.6309584270001,13.807126398000035],[120.65243798300004,13.772678713000063],[120.66612869400002,13.771131907000038],[120.67614737300003,13.78920608800007],[120.65527408800006,13.831185435000068],[120.6633547140001,13.859240321000073],[120.68675044300005,13.854447920000041],[120.71570147900003,13.840779309000027],[120.72240332600006,13.858536730000028],[120.69779847500001,13.89074235500004],[120.6990727540001,13.90782664300002],[120.70773336200011,13.921860339000036],[120.72870784100007,13.927006150000066],[120.74099969100006,13.936309202000075],[120.77762407800004,13.926258922000045],[120.78973798800007,13.928075128000046],[120.84527486300011,13.909197840000047],[120.8786935820001,13.901967501000058],[120.90612944600002,13.884446042000036],[120.913528927,13.87301818000003],[120.91677597100012,13.847939838000054],[120.91429866300007,13.827985269000067],[120.9024432870001,13.820358266000028],[120.92845353400004,13.779915285000072],[120.92692030800005,13.759046026000021],[120.90820516300006,13.754794665000075],[120.87245740100002,13.715929692000028],[120.89578357900007,13.687742025000032],[120.91719802600004,13.69969559800006],[120.93132291500001,13.72898204000006],[120.94473866900013,13.739210463000061],[120.96335771300005,13.771982123000043],[120.97722865600008,13.781921372000054],[121.01211689600007,13.77876764100006],[121.03828505600006,13.762713785000072],[121.06018979500003,13.725967155000033],[121.06051419300003,13.707631827000053],[121.04920710400006,13.683770772000058],[121.0535826480001,13.670413241000064],[121.04872595200004,13.653981593000028],[121.03563406300009,13.635627308000037],[121.07107900500013,13.629988397000032],[121.07772076400012,13.61886630400005],[121.11450737700011,13.63110322500006],[121.17974804100004,13.645006775000068],[121.20761426400009,13.626623613000051],[121.2332565160001,13.627795713000069],[121.25809414400011,13.59941892100005],[121.2854872380001,13.596989127000029],[121.29475417100004,13.601113575000054],[121.32558172800007,13.633740160000059],[121.36372918200004,13.658786066000062],[121.39153220100002,13.671445562000027],[121.40934611700006,13.667194375000063],[121.41762738600004,13.655700285000021],[121.46760841900004,13.682257206000028],[121.45373840900004,13.701390606000075],[121.4500890060001,13.72016628500006],[121.44003323100003,13.732804085000053],[121.43235808600002,13.760722162000036],[121.43837150500008,13.79190248900005],[121.45661691000011,13.810264001000064],[121.45665641300002,13.818242209000058],[121.41748513700009,13.84387438000004],[121.40740856500008,13.83923178700007],[121.37892195100007,13.850860930000065],[121.36747200600007,13.869398101000057],[121.34806799100011,13.862572201000033],[121.332145878,13.869742202000053],[121.30795183300008,13.867019690000062],[121.27160968300007,13.878059858000029],[121.26436672500006,13.890060691000029],[121.23998049000011,13.905983693000051],[121.23724036700003,13.934252107000079],[121.24647366500005,13.963490883000073],[121.24809656500008,13.984388119000071],[121.22896824600004,14.002903136000045],[121.21619239800008,14.026614681000067],[121.20556391600009,14.109612395000054],[121.19440848600004,14.131070861000065],[121.09505203000003,14.156300173000032],[121.03586636200009,14.151780380000046],[121.02632882300009,14.13458585600006],[121.00588658800005,14.121661488000026],[120.9803753240001,14.12008944300004],[120.96797163000008,14.098633049000055],[120.93759739600013,14.08594336700003],[120.90250537600002,14.076790614000062],[120.89272050800002,14.087613034000073],[120.8624147820001,14.07542182900005],[120.84485636600004,14.07683931200006],[120.83929156600004,14.088780735000057],[120.82014925800003,14.100724957000066],[120.79687725900011,14.103118018000034],[120.76768094300007,14.11773682100005],[120.76888523800005,14.133428447000027],[120.7294194100001,14.14038455700006],[120.71593295800005,14.126534449000077],[120.69878430600009,14.138474807000025],[120.69194031400002,14.16085890600004],[120.70565717500004,14.174333526000055],[120.66230859400002,14.18609027100007],[120.65039621500011,14.204818189000035],[120.618347222,14.220246020000047]]]]},"properties":{"adm1_psgc":400000000,"adm2_psgc":401000000,"adm2_en":"Batangas","geo_level":"Prov","len_crs":654610,"area_crs":3197610494,"len_km":654,"area_km2":3197},"id":401000000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.01623891600002,14.351821071000073],[121.00759085400011,14.355170370000051],[121.01161116900006,14.380260945000037],[120.99448670900004,14.407610540000064],[120.98377063700002,14.433689059000075],[120.97409510600004,14.439106137000072],[120.9660033990001,14.465722366000023],[120.95171060400003,14.467584679000028],[120.9181292620001,14.456246315000048],[120.89018940800007,14.45378368000007],[120.8861442330001,14.461363476000031],[120.90353669900004,14.486818243000073],[120.89358522400005,14.491676189000032],[120.87992130500004,14.461694379000049],[120.87049060100001,14.430223676000022],[120.8486171400001,14.419447104000028],[120.83941807400004,14.399228124000048],[120.81640639600005,14.37750800700008],[120.78347779500008,14.352602780000039],[120.76863065900011,14.331655502000046],[120.74627880400008,14.31779869700006],[120.73221623000006,14.31626009800004],[120.71583678400009,14.293486407000044],[120.70387674000004,14.28482996800005],[120.65639277200012,14.278288906000054],[120.62437443400006,14.266113834000068],[120.62119393300009,14.252668307000022],[120.62571672600006,14.225876094000055],[120.618347222,14.220246020000047],[120.65039621500011,14.204818189000035],[120.66230859400002,14.18609027100007],[120.70565717500004,14.174333526000055],[120.69194031400002,14.16085890600004],[120.69878430600009,14.138474807000025],[120.71593295800005,14.126534449000077],[120.7294194100001,14.14038455700006],[120.76888523800005,14.133428447000027],[120.76768094300007,14.11773682100005],[120.79687725900011,14.103118018000034],[120.82014925800003,14.100724957000066],[120.83929156600004,14.088780735000057],[120.84485636600004,14.07683931200006],[120.8624147820001,14.07542182900005],[120.89272050800002,14.087613034000073],[120.90250537600002,14.076790614000062],[120.93759739600013,14.08594336700003],[120.96797163000008,14.098633049000055],[120.9803753240001,14.12008944300004],[121.00588658800005,14.121661488000026],[121.02632882300009,14.13458585600006],[121.03586636200009,14.151780380000046],[121.01369984200005,14.163004601000068],[121.031764898,14.202937527000076],[121.05282869100007,14.21626380400005],[121.05084043600004,14.23360244400004],[121.03913747200012,14.271101015000058],[121.05865658400012,14.299756230000073],[121.06102153600013,14.32266921300004],[121.03202391200013,14.334445145000071],[121.00727737200009,14.320966914000053],[121.00898090600002,14.341994256000078],[121.01623891600002,14.351821071000073]]],[[[120.57977691400004,14.37249506200004],[120.585803499,14.387572941000029],[120.57312609200007,14.392697017000048],[120.56380811400004,14.380258078000056],[120.57977691400004,14.37249506200004]]]]},"properties":{"adm1_psgc":400000000,"adm2_psgc":402100000,"adm2_en":"Cavite","geo_level":"Prov","len_crs":295248,"area_crs":1245817119,"len_km":295,"area_km2":1245},"id":402100000},
{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[121.24647366500005,13.963490883000073],[121.26873271100011,13.966524442000033],[121.27842933000011,13.97412713700004],[121.29666784200003,13.971803668000062],[121.3293513110001,13.985808889000053],[121.35080923700002,14.012048831000072],[121.40637835300002,14.035973959000046],[121.42443541600005,14.047909082000045],[121.43090350800004,14.063428043000046],[121.47859448800013,14.064792674000042],[121.49208853200003,14.073258048000069],[121.51159650500004,14.10140330900003],[121.52919053500011,14.163656280000055],[121.5441269260001,14.17447531700003],[121.5552102570001,14.162746059000026],[121.59066469700008,14.160782653000068],[121.60319213900006,14.190359066000042],[121.5899512520001,14.199159350000059],[121.61794271500004,14.234942428000066],[121.61789854600009,14.24910196700006],[121.63412066400008,14.26771032100004],[121.63451880200012,14.289790898000033],[121.60825957700003,14.29685296200006],[121.57002646300009,14.398442990000037],[121.52409879000004,14.469167303000063],[121.55047443400008,14.492387305000026],[121.53463026500003,14.509421780000023],[121.52956397300012,14.532863972000026],[121.4811586080001,14.535665168000035],[121.48067421200004,14.556779521000069],[121.45105053500004,14.59521547800006],[121.44111363900002,14.58729141100003],[121.44938626000011,14.56961988200004],[121.43933971400008,14.557175536000045],[121.44798978300004,14.544977906000042],[121.42044759500004,14.541761899000049],[121.40428190100012,14.545414044000037],[121.38110691500005,14.531527832000053],[121.3617534770001,14.477181419000031],[121.37614436800006,14.464246069000069],[121.36243190200001,14.454193887000029],[121.36919831600005,14.375142206000076],[121.365349949,14.355935850000035],[121.380494558,14.33794374300004],[121.39161260300011,14.345135542000039],[121.40982056300004,14.37843289800003],[121.44831398600002,14.397321084000058],[121.47342802900003,14.371872782000025],[121.47915953100005,14.350028565000057],[121.47017123200011,14.326954468000054],[121.43867903700006,14.337059047000025],[121.44106436400011,14.321030052000026],[121.43509993400005,14.30025627300006],[121.41666175900002,14.290282158000025],[121.39956898300012,14.28839630300007],[121.35011422900004,14.25951541300003],[121.34221837900009,14.242011478000048],[121.31275119200006,14.223053012000037],[121.30403818800004,14.203344473000072],[121.26457854800003,14.190008268000042],[121.23753567000007,14.198150648000023],[121.22750391400005,14.183867134000023],[121.21240129700004,14.178625803000045],[121.18300259000013,14.186391696000042],[121.18722334200004,14.222274966000038],[121.17345136300004,14.237735961000054],[121.16753888000005,14.261130261000059],[121.12663088000009,14.303282566000064],[121.1147152850001,14.329603632000047],[121.09267377000003,14.343295549000059],[121.09093242800009,14.356038872000052],[121.05150154700004,14.369658617000026],[121.0298758130001,14.365980729000055],[121.01623891600002,14.351821071000073],[121.00898090600002,14.341994256000078],[121.00727737200009,14.320966914000053],[121.03202391200013,14.334445145000071],[121.06102153600013,14.32266921300004],[121.05865658400012,14.299756230000073],[121.03913747200012,14.271101015000058],[121.05084043600004,14.23360244400004],[121.05282869100007,14.21626380400005],[121.031764898,14.202937527000076],[121.01369984200005,14.163004601000068],[121.03586636200009,14.151780380000046],[121.09505203000003,14.156300173000032],[121.19440848600004,14.131070861000065],[121.20556391600009,14.109612395000054],[121.21619239800008,14.026614681000067],[121.22896824600004,14.002903136000045],[121.24809656500008,13.984388119000071],[121.24647366500005,13.963490883000073]]]},"properties":{"adm1_psgc":400000000,"adm2_psgc":403400000,"adm2_en":"Laguna","geo_level":"Prov","len_crs":418123,"area_crs":1802223691,"len_km":418,"area_km2":1802},"id":403400000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.45665641300002,13.818242209000058],[121.47448112500001,13.83938307100004],[121.49649541400004,13.853481067000075],[121.55392163300007,13.87193623300004],[121.58906447100003,13.891895614000077],[121.61215150800003,13.894430111000073],[121.62595450200003,13.907978107000073],[121.64210939300006,13.907356496000032],[121.68038313300009,13.923599032000027],[121.695340901,13.918428206000044],[121.70212556000003,13.963223513000061],[121.71564828000011,13.970735347000073],[121.76129736900009,13.961736553000035],[121.77266409800008,13.94528856200003],[121.80246828100006,13.947775989000034],[121.81659586900003,13.941522666000028],[121.8180838180001,13.92798979200006],[121.80963326300002,13.91354081900005],[121.83045305000006,13.900417123000066],[121.84551963100012,13.901451176000021],[121.8572096480001,13.887257591000035],[121.8711045970001,13.896312285000022],[121.88344372200004,13.890486180000037],[121.89046050900004,13.862574024000025],[121.92836450100002,13.850634332000029],[121.9450043710001,13.85225305000006],[121.96102276800003,13.840662588000042],[121.97394871600012,13.83992019800007],[121.98111445600011,13.80631926500007],[122.00710615900005,13.809134518000063],[122.04165051700011,13.789082647000043],[122.05601823000008,13.775167195000051],[122.07391599300001,13.78630302700003],[122.09022455000002,13.780501347000037],[122.13205865500002,13.745047551000027],[122.13773675000004,13.72090889600002],[122.16117801200004,13.700554555000048],[122.17430450300002,13.669460971000033],[122.19533914100009,13.64795731600003],[122.19995003300005,13.616222911000024],[122.20757719100004,13.602519683000024],[122.22760816000006,13.599936552000033],[122.2665288410001,13.606635018000077],[122.294625429,13.59277005700005],[122.32175913100004,13.590393050000046],[122.33794418300009,13.57410410400007],[122.32925061700006,13.563895321000073],[122.35233919200004,13.547473634000026],[122.36971386900007,13.546263163000049],[122.40071531400008,13.523970588000052],[122.41318926500003,13.484109706000027],[122.47257576800006,13.420234345000036],[122.490124809,13.405739956000046],[122.48932020600012,13.39615920800003],[122.51616277000005,13.350051128000075],[122.52253191800003,13.329623189000076],[122.52241547200003,13.309181935000028],[122.51157066600003,13.290989930000025],[122.52332678500011,13.280357236000045],[122.5109500320001,13.27146639800003],[122.51468655700013,13.257053776000074],[122.50319771900001,13.246563469000021],[122.53933971600007,13.21889877100005],[122.54906437900001,13.19852492000007],[122.56464192300007,13.178826008000039],[122.598782678,13.162089163000074],[122.62208313100007,13.171447936000048],[122.64297067400004,13.196679473000076],[122.65779889300006,13.208398923000061],[122.70200340000008,13.223594096000056],[122.69101056400008,13.267999849000033],[122.67708590100005,13.275539311000045],[122.67870407200007,13.337128547000077],[122.67470238200008,13.34533945000004],[122.67677651800012,13.37868201300006],[122.66306359500003,13.41927506600007],[122.64340008900002,13.456395197000061],[122.6308393390001,13.468126399000024],[122.61886709000008,13.489154326000058],[122.60255800800009,13.502847802000076],[122.60081670000011,13.521834833000069],[122.57942176900009,13.530269143000057],[122.56464320700002,13.551563702000067],[122.58499810500005,13.558236816000031],[122.60335197300002,13.534762765000036],[122.60723489700001,13.522154787000035],[122.6231394780001,13.512962862000052],[122.63422480100007,13.528953963000047],[122.61267053900008,13.540793495000061],[122.60364409900002,13.552623614000025],[122.56996793000008,13.57736270300006],[122.54396549800005,13.58540886600002],[122.54987068600008,13.595143295000067],[122.52707417300009,13.613742401000023],[122.51871177500004,13.62815531500007],[122.4968001850001,13.648013676000062],[122.50221816900013,13.668412908000048],[122.48059177300001,13.699394439000061],[122.48081352300005,13.715990905000071],[122.49347367000009,13.73405533300007],[122.5183272910001,13.73432417500004],[122.52128139600006,13.744645658000024],[122.50888940000004,13.769678094000028],[122.51282505700011,13.784473256000068],[122.50633524200009,13.823395688000062],[122.4994093570001,13.844463133000037],[122.48560219,13.848332600000049],[122.45138254200003,13.905343278000034],[122.42365999400012,13.93005154700006],[122.43633539600013,13.944239149000051],[122.44896102300005,13.926515023000038],[122.4692214170001,13.934145212000033],[122.48501380500011,13.92719622100003],[122.5060017600001,13.927294166000026],[122.53344986000002,13.943367887000024],[122.53642447800009,13.963503432000037],[122.55241423100006,13.947554817000027],[122.58387379100009,13.961811396000028],[122.6201502670001,13.967995488000044],[122.66522009700009,13.983192314000064],[122.79251799700013,14.013752262000024],[122.71850226100004,14.042740808000076],[122.64161751700009,14.070068482000066],[122.538911374,14.116739880000067],[122.45199363600011,14.150213563000023],[122.44662851400004,14.135111727000034],[122.40846578100002,14.090570177000075],[122.39616586800004,14.084713977000035],[122.38376856000002,14.066641330000037],[122.36204661600006,14.062866015000052],[122.32626999400009,14.06270484200007],[122.29877357100008,14.072661698000047],[122.30803572300009,14.100043253000024],[122.31148847400006,14.131091327000037],[122.29681243100003,14.133851008000022],[122.28989877200002,14.121435567000047],[122.26736044000006,14.124973338000075],[122.26603416300009,14.149257278000052],[122.2732287660001,14.162783313000034],[122.2599896820001,14.173952432000021],[122.27138694700012,14.20723655100005],[122.271841202,14.24582354500006],[122.24807506200011,14.236203036000063],[122.24567170100012,14.217679826000053],[122.25109638300012,14.202730970000063],[122.2301954200001,14.190356433000032],[122.2083291360001,14.183806355000058],[122.18417059500007,14.164707776000055],[122.1894496750001,14.139014142000063],[122.16460668500008,14.140705519000049],[122.19174247600006,14.094318461000055],[122.20868383000003,14.081919820000053],[122.22778587900008,14.077123481000056],[122.27286371900003,14.03923153900007],[122.28836274500009,14.038619913000046],[122.28541947300006,14.022700017000034],[122.30817487000003,14.01144186300007],[122.30787704000011,14.00097696200004],[122.29347082500009,13.991616277000048],[122.306609448,13.972539852000066],[122.2988423060001,13.959299013000075],[122.2829573040001,13.957833627000069],[122.26466833200006,13.970000924000034],[122.23661523600003,13.972427346000073],[122.20504918000006,13.98423747400005],[122.19573073100003,13.996285628000065],[122.18119780100005,13.98764199200002],[122.19359634000013,13.96799826800003],[122.22021023100002,13.947387869000062],[122.23812119100012,13.946429891000037],[122.24800402200002,13.933704464000074],[122.24377755700003,13.911964510000075],[122.23162079100008,13.89515192400006],[122.18356065800003,13.916510965000043],[122.16916555300008,13.91334903200004],[122.15581266500011,13.92007461500003],[122.13728964700012,13.912853584000061],[122.11191195200003,13.926459569000027],[122.03555630100004,13.947682896000059],[122.00696268000002,13.96171291000007],[121.99243912500005,13.976199284000074],[121.94551378900009,13.988508342000044],[121.907282871,14.01107543100005],[121.88330458200005,14.041591311000046],[121.8466806030001,14.072705909000033],[121.82433548400002,14.08185481400005],[121.80582774100003,14.099078149000038],[121.77888026300002,14.11742792500007],[121.74884068100005,14.145731341000042],[121.73211506000007,14.172736651000037],[121.73368478600001,14.190967012000044],[121.75308791400005,14.207676924000051],[121.75968020700009,14.233937024000056],[121.75812446200007,14.247578691000056],[121.73333296500005,14.265962219000075],[121.73415384000009,14.290611389000047],[121.72766815900003,14.326294499000028],[121.68206498000008,14.379099813000037],[121.66331853600003,14.392045971000071],[121.65732617700009,14.410903702000041],[121.6489076260001,14.460015097000047],[121.6419501800001,14.471894262000038],[121.62370647700004,14.522929201000071],[121.62814511400008,14.534903568000065],[121.61866553000006,14.589663571000074],[121.60862523000003,14.599226437000024],[121.60907693200011,14.641233602000058],[121.60376832500002,14.652083388000051],[121.61118222100004,14.675472869000032],[121.63394362900009,14.668003647000035],[121.6772427290001,14.695435136000071],[121.70013697800005,14.701876612000035],[121.72265856600008,14.690831028000044],[121.73378365000006,14.69694225400008],[121.70985591200008,14.726129045000052],[121.6774056370001,14.752004167000049],[121.6585604920001,14.775783390000072],[121.63338964700007,14.78634946300002],[121.60210874300002,14.827585130000045],[121.61164176700004,14.855757702000062],[121.58998576400006,14.875669953000056],[121.5816605760001,14.89036940000005],[121.57265884500009,14.928360748000049],[121.57295149800007,14.947854049000053],[121.56678846200009,14.966509539000075],[121.54846262900003,14.990863452000049],[121.5466605040001,15.004197357000063],[121.52707271000008,15.034892623000072],[121.517435716,15.03882709800007],[121.49972819400011,15.072824396000046],[121.49449537100008,15.104047127000054],[121.49609323800006,15.120051344000045],[121.48093849800013,15.180228622000074],[121.46253959500007,15.20075498400007],[121.44803852100006,15.196346930000061],[121.43511708100003,15.210379016000049],[121.41712050200012,15.216888696000073],[121.40222658300003,15.195523378000072],[121.40809682500004,15.182936998000056],[121.39618145400006,15.162714643000077],[121.40341882900009,15.151331872000068],[121.39460381500011,15.105961485000027],[121.37400455200009,15.095887405000038],[121.37647404400003,15.08051352900003],[121.36131628900013,15.073161476000049],[121.35137018900002,15.035906006000063],[121.35710532600002,15.011749193000067],[121.34785653300003,14.996370968000065],[121.33820501800007,14.947222596000074],[121.3401122450001,14.886441354000056],[121.33555014700005,14.848280439000062],[121.33035662500004,14.834802543000022],[121.33550040000011,14.800851961000038],[121.3289782690001,14.78820056400002],[121.34179742100001,14.74712040000003],[121.33743612900004,14.727966391000052],[121.35387583300009,14.722557836000023],[121.36271785000007,14.708406480000066],[121.38062866200006,14.695232352000065],[121.4048067990001,14.690213882000025],[121.4108207590001,14.667812216000073],[121.40420229200004,14.660925983000029],[121.40486651800006,14.639266049000074],[121.41579713500005,14.627965106000032],[121.44173702300009,14.622482465000077],[121.43953569400003,14.60398770800003],[121.45105053500004,14.59521547800006],[121.48067421200004,14.556779521000069],[121.4811586080001,14.535665168000035],[121.52956397300012,14.532863972000026],[121.53463026500003,14.509421780000023],[121.55047443400008,14.492387305000026],[121.52409879000004,14.469167303000063],[121.57002646300009,14.398442990000037],[121.60825957700003,14.29685296200006],[121.63451880200012,14.289790898000033],[121.63412066400008,14.26771032100004],[121.61789854600009,14.24910196700006],[121.61794271500004,14.234942428000066],[121.5899512520001,14.199159350000059],[121.60319213900006,14.190359066000042],[121.59066469700008,14.160782653000068],[121.5552102570001,14.162746059000026],[121.5441269260001,14.17447531700003],[121.52919053500011,14.163656280000055],[121.51159650500004,14.10140330900003],[121.49208853200003,14.073258048000069],[121.47859448800013,14.064792674000042],[121.43090350800004,14.063428043000046],[121.42443541600005,14.047909082000045],[121.40637835300002,14.035973959000046],[121.35080923700002,14.012048831000072],[121.3293513110001,13.985808889000053],[121.29666784200003,13.971803668000062],[121.27842933000011,13.97412713700004],[121.26873271100011,13.966524442000033],[121.24647366500005,13.963490883000073],[121.23724036700003,13.934252107000079],[121.23998049000011,13.905983693000051],[121.26436672500006,13.890060691000029],[121.27160968300007,13.878059858000029],[121.30795183300008,13.867019690000062],[121.332145878,13.869742202000053],[121.34806799100011,13.862572201000033],[121.36747200600007,13.869398101000057],[121.37892195100007,13.850860930000065],[121.40740856500008,13.83923178700007],[121.41748513700009,13.84387438000004],[121.45665641300002,13.818242209000058]]],[[[121.93493514700005,15.058643889000052],[121.89112799500002,15.030265070000038],[121.87784892500007,15.034731209000025],[121.86379856300005,15.025732036000019],[121.85625065200009,15.039718821000063],[121.83716326500009,15.039383293000075],[121.8134272420001,14.981719722000038],[121.81795829400006,14.974184152000081],[121.8014275170001,14.93597659300008],[121.81999082100003,14.936966738000026],[121.85216895900011,14.921810150000052],[121.84911075200012,14.912626057000066],[121.8726937130001,14.876895735000058],[121.87851026700002,14.835420355000053],[121.88869981100004,14.817900287000041],[121.91207894300011,14.796126048000074],[121.91431616800001,14.77793671300003],[121.9268604550001,14.756292173000071],[121.93655507900009,14.72910940100007],[121.93521177900004,14.70686980200003],[121.90324063300011,14.706294076000063],[121.90290726400008,14.679319525000034],[121.91659065200007,14.638357765000027],[121.9392382850001,14.626554099000032],[121.94980680100002,14.628587202000066],[122.01056856800004,14.674729756000033],[122.03641732000006,14.717337928000063],[122.0248344270001,14.772614071000078],[122.02342901400006,14.808491812000055],[122.00788478200002,14.82683103600004],[121.98840884400012,14.836694712000051],[121.96773025300003,14.867880761000036],[121.96573109000009,14.900207688000023],[121.98196989300003,14.903137246000032],[121.99235064100003,14.913872915000068],[122.02023830200005,14.919766184000022],[122.01141202300005,14.951311142000064],[121.99126919100001,14.957719172000054],[122.00739686600004,14.986142413000037],[122.03121225600013,14.991962071000044],[122.04947621400004,14.96244911300004],[122.05525446400009,14.975048660000022],[122.04786400800003,15.00378612000003],[122.03525485600007,15.012771225000048],[122.02016622400004,15.00617143200003],[122.02104997300012,15.027864829000066],[121.9975558320001,15.04428848300006],[121.97764326100003,15.037985616000073],[121.97428569300006,15.050484697000059],[121.95529340700013,15.057591237000052],[121.93493514700005,15.058643889000052]]],[[[122.03795522300004,14.875929851000022],[122.01384395600009,14.874321898000064],[122.02643373800004,14.845248315000045],[122.04629403900003,14.841632891000073],[122.06322906600008,14.86330408600003],[122.03795522300004,14.875929851000022]]],[[[122.2099045220001,14.842597328000068],[122.20174144500005,14.837924971000065],[122.16797325100005,14.83968378500003],[122.1331594400001,14.828476545000056],[122.12305275100005,14.841031216000031],[122.09626915800006,14.832393061000058],[122.10594970600003,14.806769321000047],[122.12539051800002,14.796562297000035],[122.13613356700012,14.79850333100006],[122.19125779800004,14.763788591000036],[122.22928445800005,14.750925411000027],[122.25818536100009,14.727114745000051],[122.25947774700013,14.75920952300004],[122.25224887,14.771585955000036],[122.26101084600009,14.78359857600003],[122.24187347300007,14.794246893000036],[122.23481612300007,14.786541191000023],[122.19725139400009,14.805897494000021],[122.1965453790001,14.813837302000026],[122.21218319200013,14.832923038000049],[122.2099045220001,14.842597328000068]]],[[[122.40355435000005,14.733756076000068],[122.38171471900012,14.729608458000026],[122.35882520300002,14.712029398000025],[122.3330491370001,14.71096541400004],[122.30986313000005,14.689345515000069],[122.32153507500004,14.674668697000078],[122.35017878000008,14.681508049000056],[122.37528000700003,14.679606041000051],[122.42118011800005,14.687132906000043],[122.43611228700001,14.695217537000076],[122.42955647800011,14.713420409000035],[122.40355435000005,14.733756076000068]]],[[[121.82630932500001,14.306325829000057],[121.80551447700007,14.295245410000064],[121.80723218600009,14.27111568300006],[121.83179600100004,14.25976224100003],[121.83849565300012,14.279009296000027],[121.84859243000005,14.28682904200002],[121.82630932500001,14.306325829000057]]],[[[121.92948540300007,14.235902975000043],[121.91354023300006,14.196019116000057],[121.92962557100009,14.187418743000023],[121.94503155500001,14.158566670000027],[121.98609023100005,14.11121679900003],[122.00141447300007,14.108401487000037],[122.03809213400008,14.089898591000061],[122.05636937500003,14.066677030000053],[122.09008065800005,14.051938684000048],[122.11346146300002,14.026897012000063],[122.13289577600005,14.01999114200004],[122.16675787600003,14.000324443000066],[122.18513729200005,14.004285103000027],[122.18538578400012,14.025397548000056],[122.17049225500013,14.04631869700006],[122.15052478300004,14.064486819000024],[122.1393889200001,14.067521443000032],[122.12775754700012,14.087310753000054],[122.07746252600009,14.114216487000018],[122.05828893000013,14.131725135000064],[122.0215609700001,14.152981260000045],[121.92948540300007,14.235902975000043]]],[[[121.78178434100005,13.879221151000024],[121.80128927500006,13.894763166000075],[121.78592428200011,13.910739701000066],[121.78865056000006,13.935551964000071],[121.75615508800001,13.942874669000044],[121.75467382500004,13.928714752000076],[121.73945740300007,13.899090826000075],[121.75382303500011,13.883622510000064],[121.78370312200002,13.909541626000077],[121.79051253800003,13.901402221000069],[121.78178434100005,13.879221151000024]]]]},"properties":{"adm1_psgc":400000000,"adm2_psgc":405600000,"adm2_en":"Quezon","geo_level":"Prov","len_crs":2165220,"area_crs":8398566534,"len_km":2165,"area_km2":8398},"id":405600000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.45105053500004,14.59521547800006],[121.43953569400003,14.60398770800003],[121.44173702300009,14.622482465000077],[121.41579713500005,14.627965106000032],[121.40486651800006,14.639266049000074],[121.40420229200004,14.660925983000029],[121.4108207590001,14.667812216000073],[121.4048067990001,14.690213882000025],[121.38062866200006,14.695232352000065],[121.36271785000007,14.708406480000066],[121.35387583300009,14.722557836000023],[121.33743612900004,14.727966391000052],[121.34179742100001,14.74712040000003],[121.3289782690001,14.78820056400002],[121.33550040000011,14.800851961000038],[121.33035662500004,14.834802543000022],[121.25299686000005,14.829226647000041],[121.21925184400004,14.833223191000052],[121.20804184000006,14.81794121400003],[121.1879882930001,14.823554116000025],[121.16528463600002,14.823417534000043],[121.15052962900006,14.801784266000027],[121.1368658130001,14.801465402000076],[121.11488089400007,14.778960670000059],[121.1321174950001,14.776390408000054],[121.11822157000006,14.749419337000065],[121.11802297800013,14.729928850000022],[121.12461778900001,14.70874460200002],[121.11146916300005,14.69566768200002],[121.11188912900003,14.671163089000059],[121.1261471470001,14.66997417700003],[121.13486852100006,14.65885238300007],[121.12855805700009,14.643593338000073],[121.10549838300007,14.632654354000065],[121.1019327580001,14.615649672000071],[121.11044978200005,14.592235448000055],[121.0968965510001,14.569254547000074],[121.10700168300002,14.545701014000032],[121.10159991300009,14.52170471800002],[121.12549315400008,14.535482970000032],[121.13776139700009,14.536233714000048],[121.15136547300006,14.517932543000033],[121.16483093600006,14.509482851000028],[121.18476833500006,14.483051347000067],[121.19989704400007,14.442357430000074],[121.21273222400009,14.432176134000033],[121.22269985000004,14.447992351000039],[121.2203872230001,14.473891436000033],[121.23394820300008,14.48488673000003],[121.24175233200003,14.502442474000082],[121.27457867700002,14.503246765000029],[121.28308143000004,14.482170546000077],[121.30132633200003,14.484151828000051],[121.30895096400002,14.467338821000055],[121.32510470500006,14.46085707900005],[121.32519509500003,14.447476062000021],[121.33623956200006,14.42965614800005],[121.33869553900001,14.411620088000062],[121.33319216100007,14.385630970000022],[121.31986819000008,14.358159276000038],[121.32015815500006,14.341119138000066],[121.30495614900008,14.326485487000072],[121.30372590800005,14.295929162000048],[121.31475987200008,14.287077226000063],[121.33459460300003,14.312053516000047],[121.35284235100006,14.328435214000026],[121.380494558,14.33794374300004],[121.365349949,14.355935850000035],[121.36919831600005,14.375142206000076],[121.36243190200001,14.454193887000029],[121.37614436800006,14.464246069000069],[121.3617534770001,14.477181419000031],[121.38110691500005,14.531527832000053],[121.40428190100012,14.545414044000037],[121.42044759500004,14.541761899000049],[121.44798978300004,14.544977906000042],[121.43933971400008,14.557175536000045],[121.44938626000011,14.56961988200004],[121.44111363900002,14.58729141100003],[121.45105053500004,14.59521547800006]]],[[[121.2310912150001,14.401883034000038],[121.22027881400004,14.383827091000054],[121.22005028100011,14.357883577000049],[121.21514231600008,14.34686467900008],[121.22605139900007,14.323951671000033],[121.22628229100009,14.310949369000069],[121.24537887300006,14.310899527000059],[121.24211410200009,14.329852956000028],[121.25867039900005,14.344750345000023],[121.2405610620001,14.349521148000061],[121.2310912150001,14.401883034000038]]]]},"properties":{"adm1_psgc":400000000,"adm2_psgc":405800000,"adm2_en":"Rizal","geo_level":"Prov","len_crs":326217,"area_crs":1200455008,"len_km":326,"area_km2":1200},"id":405800000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[123.60125067900003,13.522687456000027],[123.54560845100002,13.516697864000035],[123.54328423700008,13.501666299000018],[123.54544748100011,13.485836639000068],[123.55664269700004,13.469524604000071],[123.57268960300009,13.458021292000069],[123.5812924910001,13.448367139000023],[123.58806336800002,13.422057589000076],[123.58243122100009,13.395386389000063],[123.57621389300004,13.378277725000034],[123.56798881000009,13.371857841000063],[123.57150571400007,13.365336622000026],[123.55934980300003,13.360391644000057],[123.55561125500003,13.354617189000066],[123.52370334700002,13.352766140000028],[123.51239273900002,13.346792858000072],[123.49379612100006,13.344597269000076],[123.49383574500008,13.361898781000036],[123.46802729700006,13.363971094000023],[123.4585464270001,13.367820793000021],[123.43280213500009,13.363097290000042],[123.41758121300005,13.352300169000044],[123.40645509100011,13.347575831000029],[123.39879749300009,13.33465374700006],[123.39259550500005,13.341061079000042],[123.38393397400013,13.336091727000051],[123.37317003100007,13.33751864900006],[123.38092833200005,13.33090983100004],[123.38384769300002,13.321214429000062],[123.37775489500005,13.305574159000058],[123.36044881300006,13.299699216000016],[123.3526878670001,13.306672606000062],[123.33555191200004,13.294827203000068],[123.31225141000004,13.287249039000073],[123.28522357100007,13.269512651000069],[123.28127328200003,13.258541065000031],[123.29278121400013,13.253141184000068],[123.31465514000003,13.221597847000053],[123.31910671500007,13.209473701000036],[123.32734117800011,13.198223321000057],[123.3242564000001,13.190830445000069],[123.3096000170001,13.191584660000048],[123.30488054100012,13.177834879000045],[123.31089495300012,13.16862218800003],[123.3012572680001,13.155904717000055],[123.28868467900008,13.146838289000073],[123.29193012500004,13.134971285000063],[123.29182998000012,13.118410209000045],[123.28871334900009,13.107095036000034],[123.29628711800002,13.087484024000046],[123.29398133200004,13.07252150000005],[123.28920846200003,13.064442088000021],[123.30135416000007,13.049536619000037],[123.30149615900008,13.039262514000027],[123.30752578900002,13.024373040000054],[123.31953698200006,13.006877386000046],[123.3385821720001,13.011880753000069],[123.3698917900001,13.027586874000063],[123.3704314680001,13.035607095000046],[123.38335280900004,13.04082455800005],[123.39075768600003,13.036232432000077],[123.40788715700012,13.04591226400004],[123.41946437300011,13.039157861000033],[123.42583445000004,13.03991796400004],[123.43637977000004,13.029829243000052],[123.44761729100004,13.027219128000068],[123.45832104000011,13.014859250000027],[123.46184795600004,13.00489742700006],[123.48226570000008,12.988444596000024],[123.49216108500002,13.00091114700007],[123.51782511400006,13.012754216000074],[123.53782893100005,13.01813417300002],[123.54809213500006,13.024415272000056],[123.56306575500003,13.02307481200006],[123.57486209300009,13.030070694000072],[123.58691683200004,13.022239605000037],[123.62025036800004,13.022980362000055],[123.62968937800008,13.010442943000044],[123.65000598900008,13.01932447300004],[123.68452626700004,13.02852085000006],[123.71473746600009,13.039926492000063],[123.72308167900009,13.034239268000023],[123.72238104200005,13.027039090000073],[123.73445022100007,13.026391081000043],[123.7364397980001,13.01621579400006],[123.74598040500007,12.996885520000037],[123.76215491200004,12.997107576000072],[123.76765605700007,12.986184890000061],[123.78231135300005,12.994530540000028],[123.7872156410001,13.004620741000048],[123.79577553900005,13.00827792900003],[123.80564823300006,13.019028077000028],[123.82253470700006,13.02440377700003],[123.85924674000012,13.040744483000024],[123.87528872300005,13.042301291000058],[123.89598666200006,13.03764349000005],[123.90670266300005,13.040932211000039],[123.9155897280001,13.054929226000066],[123.92101326300008,13.083766269000023],[123.92917038300006,13.102068074000046],[123.92676515300003,13.120887665000055],[123.9112910460001,13.122745912000026],[123.90849467500004,13.138472829000019],[123.87943236900004,13.143195179000033],[123.86547750200009,13.137671910000051],[123.8615406130001,13.132382013000038],[123.86022079200006,13.113080184000069],[123.85420815400005,13.107569650000071],[123.83861827800001,13.108886273000051],[123.83910970000011,13.089348911000057],[123.83002741800011,13.075609881000045],[123.81360943700008,13.064386235000027],[123.81286711700011,13.054511989000046],[123.79430548000006,13.046002164000072],[123.77415767400011,13.051709798000047],[123.75676978000003,13.063679161000037],[123.76507158600009,13.074638358000069],[123.7503574640001,13.08454801700003],[123.7526960450001,13.090351708000073],[123.7756962860001,13.09813189400006],[123.78507549500011,13.110741827000027],[123.78590890900013,13.118038575000071],[123.77003674600007,13.128581102000053],[123.75653273600007,13.14470742000003],[123.75691776100008,13.159143655000033],[123.75400483200006,13.173593197000056],[123.76190656200004,13.203602914000044],[123.77472171200009,13.227651745000056],[123.78718215000004,13.237998711000047],[123.8019283220001,13.23793046100008],[123.81794087700007,13.230503289000069],[123.85769196800004,13.224262921000047],[123.86830844800012,13.235793731000054],[123.85013185100001,13.247791731000063],[123.84481527500009,13.265052179000065],[123.82880871600004,13.266778777000066],[123.82622064500005,13.252059555000077],[123.8161600520001,13.261035390000076],[123.82142379000005,13.266515310000043],[123.8136288160001,13.283708149000061],[123.8155418030001,13.288000042000021],[123.80278131500006,13.297034033000044],[123.7930146310001,13.29697465300006],[123.78274044900003,13.301935014000035],[123.78001324300008,13.311616324000056],[123.75639036800011,13.323684983000017],[123.74694698500002,13.323091477000048],[123.7415387000001,13.33292896600005],[123.74053272100002,13.349800832000026],[123.73535862000006,13.368178156000054],[123.72725499600006,13.371132964000028],[123.72590146000005,13.39112465100004],[123.7140309560001,13.409821892000025],[123.71345990300006,13.417797527000063],[123.70324286700009,13.431673411000075],[123.69852355600007,13.447561618000066],[123.68552568700012,13.459491162000063],[123.68243194600008,13.469922297000037],[123.67412188900005,13.479258905000052],[123.66474253700005,13.47865629900002],[123.63940493200005,13.484268299000062],[123.62412979400007,13.491885283000043],[123.60490248100005,13.51506624600006],[123.60125067900003,13.522687456000027]]],[[[123.76545898200004,13.407387588000061],[123.77403737300006,13.389320779000057],[123.79029151700001,13.378579207000026],[123.7983094240001,13.366354247000059],[123.81093411600011,13.356016579000027],[123.83557730200005,13.344191875000039],[123.84168565300001,13.363234952000026],[123.82980221800007,13.36871433600004],[123.81760026800009,13.387786940000069],[123.80025171000011,13.395556055000043],[123.793346143,13.39244130000003],[123.78264617200011,13.402044838000052],[123.77447899100004,13.399582367000049],[123.76545898200004,13.407387588000061]]],[[[123.8507392460001,13.354140749000067],[123.84367772100006,13.351438892000033],[123.84009124600004,13.337295589000064],[123.86115489800011,13.317835872000044],[123.85149474700007,13.308725597000032],[123.84921496000005,13.293349068000055],[123.84998965300008,13.267937806000075],[123.85607143000004,13.255311712000035],[123.86838695500013,13.246402221000038],[123.87420404300006,13.230091798000043],[123.8923504060001,13.230673817000023],[123.90091586300004,13.23995351000008],[123.90493093200008,13.250117771000076],[123.89413230000002,13.25897957400002],[123.88652057800005,13.271612499000069],[123.8884032830001,13.28021835700002],[123.90479968700004,13.304104434000063],[123.91806194800007,13.304846614000038],[123.92901212800007,13.321099050000045],[123.9215326860001,13.33038318900003],[123.905724737,13.330950301000032],[123.90635535900003,13.339577071000065],[123.88874107400012,13.34054588300006],[123.88419411200005,13.34758806600007],[123.87421260200007,13.347925036000047],[123.8507392460001,13.354140749000067]]],[[[123.93769424600009,13.32452823800003],[123.92727945100012,13.306531816000074],[123.94861347900007,13.306242279000058],[123.93769424600009,13.32452823800003]]],[[[123.97712102700007,13.291520552000067],[123.9746344470001,13.283317575000071],[123.9659869200001,13.280285960000066],[123.95098546800013,13.29061577600004],[123.92982109600005,13.286057735000043],[123.91516663100003,13.286194613000077],[123.91313382300008,13.274335149000024],[123.918304809,13.260311084000023],[123.95751028100005,13.23168670500007],[123.97245797800008,13.232155538000029],[123.98389321000002,13.236663143000044],[124.00136363000001,13.222010157000057],[124.02236600800008,13.216965371000072],[124.03881015900005,13.218640185000027],[124.05216398100004,13.22769569400003],[124.06384609300007,13.239853340000021],[124.06493934200012,13.25094863300006],[124.07617549800011,13.25298086000004],[124.0861054510001,13.260491645000055],[124.08371138000007,13.267401418000073],[124.07451334200006,13.271555696000064],[124.0651883930001,13.269938498000041],[124.05386907800005,13.278367106000076],[124.04056050500004,13.27895073000008],[124.03673777900008,13.260322448000066],[124.01676857100006,13.284410512000019],[124.00171443300009,13.286704579000059],[123.99173658500003,13.26106065300007],[123.98297530100001,13.261381213000053],[123.9832006900001,13.274961564000021],[123.97591375600008,13.281254258000049],[123.97712102700007,13.291520552000067]]],[[[124.12990765300005,13.236041439000076],[124.12523771000009,13.227446823000037],[124.08303347800006,13.21220501700003],[124.07711992200008,13.203195288000073],[124.09900134700003,13.189683735000074],[124.12594292400001,13.184993563000033],[124.14614155900006,13.187129072000062],[124.15705103100004,13.180565597000056],[124.16469464000012,13.18140939600005],[124.18049767200013,13.173106918000032],[124.19826132900005,13.173966368000038],[124.20962945500001,13.169525778000036],[124.2194946190001,13.179584489000032],[124.21396605600012,13.18987201300007],[124.21448630900011,13.19901217600005],[124.20809752000002,13.207543222000027],[124.19420327100012,13.216271395000033],[124.18589094800006,13.216956469000024],[124.15458882400003,13.231168857000055],[124.1448164310001,13.22880707400003],[124.12990765300005,13.236041439000076]]]]},"properties":{"adm1_psgc":500000000,"adm2_psgc":500500000,"adm2_en":"Albay","geo_level":"Prov","len_crs":711965,"area_crs":2467882577,"len_km":711,"area_km2":2467},"id":500500000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[122.95023318900007,14.494021075000035],[122.9411060990001,14.488586185000031],[122.93783636900002,14.47409759100003],[122.9314054250001,14.468080301000043],[122.90999072300008,14.462113090000054],[122.89930551300004,14.452170613000021],[122.91069996100009,14.445029748000024],[122.92265959900008,14.454771389000026],[122.9356541200001,14.446503692000022],[122.94464038600007,14.45011723400006],[122.93970171,14.46475355200005],[122.95179253900005,14.466416124000036],[122.94877936700004,14.47876889400004],[122.95873828200003,14.490192171000047],[122.95023318900007,14.494021075000035]]],[[[122.94051555600002,14.439536489000034],[122.93710857200007,14.428359607000063],[122.94395506000002,14.417953449000038],[122.95498167800008,14.40858371500008],[122.97084500500013,14.404431804000074],[122.97639300400012,14.411711111000045],[122.95499791700001,14.419351941000057],[122.94285824500002,14.429807419000042],[122.94051555600002,14.439536489000034]]],[[[123.06069556700004,13.837581502000035],[123.05854909200004,13.852731211000046],[123.0697007440001,13.87637149300002],[123.08706976600003,13.88158723400005],[123.09432805900006,13.887687827000036],[123.08961222900005,13.90265760300002],[123.09270104900008,13.91538239000005],[123.0879285300001,13.922626498000055],[123.08201959000006,13.959125904000075],[123.08752683800004,13.970407353000041],[123.07901614900004,13.986595491000061],[123.05648891100007,13.993950577000021],[123.04625173900001,14.01202114600005],[123.03169030900007,14.031097186000066],[123.02931115000003,14.040984282000068],[123.02983874600012,14.06022058800005],[123.03284526200004,14.067434628000058],[123.04823409000005,14.06841824700007],[123.04075821200003,14.101350163000063],[123.03193400200009,14.099974316000042],[123.02339867800005,14.111869162000062],[123.01181875000007,14.096905680000074],[123.01060276800001,14.111396160000023],[123.00212930400004,14.114826682000057],[122.98843210600012,14.129168167000048],[122.97858796900005,14.148256182000067],[122.96551145600006,14.152154890000078],[122.95315931100004,14.162961007000034],[122.93744859000005,14.190606294000077],[122.91377083600003,14.198238537000064],[122.91179302100011,14.211425441000074],[122.91546806400004,14.221458030000061],[122.9030396160001,14.224149262000026],[122.88722470500011,14.236454697000056],[122.86341388300002,14.271056222000025],[122.85419268300008,14.27003165000002],[122.84835619400008,14.28212379300004],[122.82692340000006,14.286220897000023],[122.82079885100006,14.27598218500003],[122.80316656800007,14.277364986000064],[122.79869278500007,14.28840694200005],[122.79147267400003,14.282062880000067],[122.78524974700008,14.291551961000035],[122.79493724800011,14.305316998000023],[122.78193304000001,14.30755157100003],[122.77462077000007,14.31996886400003],[122.764164606,14.320258731000022],[122.75095041700001,14.328071634000024],[122.73666771,14.311547424000025],[122.72542166400001,14.31139645100006],[122.71344948900003,14.32147367300007],[122.71583305900003,14.332628937000035],[122.71264919000009,14.34021232900005],[122.69314728000006,14.338422663000076],[122.68832319700006,14.343925172000068],[122.66803338800003,14.33690926800006],[122.67662371100006,14.311144521000074],[122.69385732500008,14.285379810000052],[122.68202071600001,14.283689823000032],[122.6639121270001,14.300403708000033],[122.64721337200002,14.30244236200002],[122.63870229100007,14.291568253000035],[122.6147198760001,14.290681475000044],[122.59705632600003,14.302618955000069],[122.59759344100007,14.318786681000063],[122.5694721010001,14.325547820000052],[122.538077422,14.340147731000064],[122.52949465400003,14.335669702000072],[122.52222619400005,14.344271098000037],[122.50931740800002,14.344450388000038],[122.51550258800012,14.330017819000034],[122.52619092900011,14.322273873000027],[122.51271480300012,14.318313298000076],[122.50324496500002,14.331020443000057],[122.4943378280001,14.336679752000066],[122.4864149120001,14.328632154000047],[122.46904584000005,14.33965673400007],[122.46551290400011,14.328110982000059],[122.45834626000011,14.329449160000022],[122.45327977500007,14.31861601200006],[122.43511515800002,14.31638781600003],[122.4306987770001,14.301042566000035],[122.41895649700008,14.310201145000066],[122.41457819800007,14.303192186000047],[122.41289908600004,14.28714265700006],[122.39373393600012,14.279170495000074],[122.38439486300003,14.286956624000025],[122.37251421000008,14.258798826000032],[122.3605487540001,14.245757278000042],[122.36870362500007,14.230777614000033],[122.37997275300008,14.219927467000046],[122.37998623300007,14.21366003500003],[122.35891979500002,14.214793650000049],[122.35594786500009,14.222552048000066],[122.34609708000005,14.21790071400005],[122.34830726400003,14.207497480000029],[122.35680971200009,14.20398294300003],[122.35623329500005,14.18874353800004],[122.34425465700008,14.19028972500007],[122.34913292100009,14.201012570000046],[122.34137673300006,14.203263801000046],[122.33236814800011,14.196939761000069],[122.33772044700002,14.18441675200006],[122.33525293400008,14.167794992000035],[122.33696313300004,14.155423720000044],[122.35223498300002,14.136298861000054],[122.346422478,14.113234128000043],[122.34055515300008,14.116789103000027],[122.3311714890001,14.106660615000068],[122.31109409400004,14.104277247000027],[122.30187157000013,14.087203955000062],[122.29877357100008,14.072661698000047],[122.32626999400009,14.06270484200007],[122.34078479700008,14.064244632000054],[122.36204661600006,14.062866015000052],[122.38376856000002,14.066641330000037],[122.39616586800004,14.084713977000035],[122.40846578100002,14.090570177000075],[122.42299240600006,14.10809583200006],[122.43217796400008,14.113516736000063],[122.43353581000008,14.121447172000046],[122.44662851400004,14.135111727000034],[122.45199363600011,14.150213563000023],[122.538911374,14.116739880000067],[122.61303162500008,14.082416848000035],[122.64161751700009,14.070068482000066],[122.70631229800006,14.046433639000043],[122.71850226100004,14.042740808000076],[122.771600067,14.021161902000074],[122.79251799700013,14.013752262000024],[122.84465426400006,13.98558823600007],[122.85295762900012,13.976679415000035],[122.89186546600003,13.96438053000003],[122.90382023100005,13.948699912000052],[122.90082775600001,13.940135232000044],[122.92109169100002,13.938515966000065],[122.92858871300005,13.922099048000064],[122.94104603600012,13.922882583000046],[122.95698706100006,13.918252184000039],[122.9935150020001,13.891340081000067],[123.06069556700004,13.837581502000035]]],[[[123.05162313400001,14.129265904000022],[123.0673145830001,14.103751846000023],[123.06791584700011,14.12931419000006],[123.05162313400001,14.129265904000022]]],[[[123.10509961900004,14.046707566000068],[123.0941300500001,14.041936577000058],[123.10370197800012,14.03314669400004],[123.11359965200005,14.034704312000029],[123.10509961900004,14.046707566000068]]]]},"properties":{"adm1_psgc":500000000,"adm2_psgc":501600000,"adm2_en":"Camarines Norte","geo_level":"Prov","len_crs":670564,"area_crs":2119744287,"len_km":670,"area_km2":2119},"id":501600000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[123.57775347900008,13.969881650000046],[123.56381699300006,13.96359436400007],[123.5639501170001,13.952650506000053],[123.56884707200004,13.944054347000074],[123.57816327600005,13.953091984000025],[123.57775347900008,13.969881650000046]]],[[[123.81795992900005,13.978474025000024],[123.819038255,13.95261780000004],[123.8103119740001,13.94407877800006],[123.81669195500002,13.939566267000032],[123.81192843600003,13.929876818000023],[123.81409841800007,13.909761982000076],[123.8244161890001,13.910137045000058],[123.8246828350001,13.897481867000065],[123.83139722300007,13.889471456000026],[123.84035405500003,13.898723352000047],[123.83257341100011,13.937020803000053],[123.8379271430001,13.945400489000068],[123.83379934700008,13.952484860000029],[123.83126682900003,13.976046637000023],[123.81795992900005,13.978474025000024]]],[[[123.64427264900009,13.978375624000021],[123.65276807000009,13.965273413000038],[123.62431736700013,13.958540497000055],[123.61826850400007,13.949765132000039],[123.60987063100004,13.946484841000029],[123.59637225400002,13.933791730000054],[123.60467074300006,13.924424032000045],[123.62511979300007,13.906999281000028],[123.62993176300006,13.914135901000067],[123.64598059200013,13.917768732000066],[123.65751028700004,13.934591940000075],[123.67225568100001,13.937055670000062],[123.67788996600007,13.950839866000022],[123.6705776120001,13.965310405000027],[123.66067009900007,13.960904785000022],[123.65429461900011,13.97281502800007],[123.64427264900009,13.978375624000021]]],[[[123.55795851300003,13.993874875000072],[123.56798237100008,13.975536957000031],[123.57510760700008,13.982425021000042],[123.55795851300003,13.993874875000072]]],[[[123.60125067900003,13.522687456000027],[123.59826957900007,13.53707789400005],[123.5818112950001,13.546509452000064],[123.56855306700004,13.562129624000018],[123.55545618100007,13.558053430000031],[123.5383656,13.558276147000072],[123.53131607000013,13.566473659000053],[123.53004713500003,13.576289767000047],[123.54813717400009,13.595668501000034],[123.535701173,13.61262255600008],[123.53850233800007,13.638013302000042],[123.55364015000009,13.676811336000073],[123.55638421700009,13.687234364000064],[123.56581197700007,13.705180841000072],[123.58167432700007,13.726634114000033],[123.58691885900008,13.729737583000029],[123.61956546700003,13.723897221000072],[123.64463267000009,13.714979232000076],[123.65771455600007,13.707352935000074],[123.67319177400009,13.721081325000055],[123.6945142850001,13.71970830200007],[123.702363384,13.712709668000057],[123.71800622700005,13.708689456000057],[123.72688095500008,13.711226886000077],[123.7405381010001,13.705742708000056],[123.7467367920001,13.708660623000071],[123.77618508200011,13.698446303000026],[123.7799938500001,13.69418922400007],[123.80189008800005,13.688111903000047],[123.82573395500005,13.692428557000028],[123.85741845600012,13.718169260000026],[123.86025164600005,13.730724251000026],[123.87397042000009,13.73776063100007],[123.89562535800009,13.726380380000023],[123.90875692900012,13.730286707000062],[123.91951075200006,13.727282095000021],[123.93569274600009,13.735301922000076],[123.9473992830001,13.725177187000044],[123.96944360700002,13.725660673000046],[123.97486630500008,13.738616299000059],[123.96211725800003,13.752538973000071],[123.95099946700009,13.75516656800005],[123.95002136500011,13.768865022000057],[123.94247269300003,13.776513489000022],[123.94701177400007,13.786421776000054],[123.94084194600008,13.79512832000006],[123.9176739610001,13.791440430000023],[123.90124674100002,13.79540252500004],[123.88446022900007,13.803674569000064],[123.87744328200006,13.816291364000048],[123.86819890200002,13.825253592000026],[123.85202696200008,13.815730501000074],[123.84342825100009,13.815781523000055],[123.8134452180001,13.82901173300007],[123.80183178300001,13.840951049000068],[123.78417365100005,13.84644504300007],[123.7799395400001,13.858568097000047],[123.77098891700007,13.85835141900003],[123.75497428300001,13.868205066000028],[123.74948491600003,13.883463893000055],[123.73354572400001,13.899002239000025],[123.73239765100006,13.91454939800008],[123.721905933,13.93483367300007],[123.71303065500001,13.932147498000061],[123.71683348800002,13.920346048000058],[123.70255712500013,13.912671634000047],[123.70655017600008,13.899929518000022],[123.6992413260001,13.884129269000026],[123.68284123300009,13.879115421000048],[123.66798494100011,13.883133890000067],[123.662142795,13.890608228000074],[123.648300692,13.890970170000061],[123.64597364600002,13.883111060000033],[123.63083110500008,13.888875563000054],[123.60290754600008,13.894315245000028],[123.58617589700009,13.908790636000049],[123.55599377400004,13.921479068000052],[123.548606403,13.929629789000046],[123.54053413200006,13.91754044000004],[123.51721068500002,13.91881076100003],[123.5167872090001,13.930260511000025],[123.49379390500008,13.920938182000041],[123.48758644700001,13.925238213000055],[123.49666451800012,13.933960309000039],[123.48612350400002,13.941314587000022],[123.47922233400006,13.952505478000035],[123.47321627800012,13.952626210000062],[123.4541461230001,13.96396913800004],[123.44514998500006,13.949182237000057],[123.44853055300005,13.920205390000033],[123.43150722100006,13.925719080000022],[123.41775173200006,13.933926278000056],[123.41265165000004,13.985484341000074],[123.40265080400003,13.994008541000026],[123.40152112400006,14.00831168600007],[123.3912375020001,14.013003990000072],[123.39269546300012,14.027581400000027],[123.387864754,14.034825162000061],[123.37601889100007,14.021277974000041],[123.363525191,14.017799514000046],[123.3640286970001,14.010034564000021],[123.35225593300004,14.005940200000053],[123.34882830900006,14.010682921000065],[123.3466998250001,14.029024838000053],[123.35371059600004,14.037782408000052],[123.36861799200005,14.038377953000063],[123.35539984200011,14.053760537000075],[123.35937508000006,14.074123605000068],[123.34719595500007,14.092593657000066],[123.33171048500004,14.092732726000063],[123.34437536200005,14.080018800000062],[123.33655678800007,14.068705516000021],[123.3250851800001,14.066081313000037],[123.31548388400005,14.071937087000038],[123.30865925400006,14.045318631000043],[123.30019537200009,14.049369751000029],[123.29845141000011,14.056926528000076],[123.2735020460001,14.073537784000052],[123.25484066800004,14.072065475000045],[123.27340374500011,14.056168033000063],[123.27914078500011,14.039693759000045],[123.27136344300003,14.03201513300007],[123.25627459000009,14.025630246000047],[123.24260512700005,14.031633931000044],[123.2400922720001,14.025443293000025],[123.25862185100003,14.019383165000022],[123.2642215950001,14.010480119000022],[123.26040242700003,14.003512615000034],[123.24632720000012,13.999786749000066],[123.22849265800006,14.002152021000033],[123.22806381700002,13.98798017800004],[123.23425527900008,13.975180675000045],[123.23199661500007,13.968191365000049],[123.25210091700002,13.964624524000044],[123.26015187300005,13.958511990000034],[123.26334455800009,13.948912325000034],[123.27756983600011,13.946195457000044],[123.28463105800007,13.932864109000036],[123.2962837680001,13.929553759000042],[123.30927783200003,13.930770393000044],[123.3245900170001,13.962962376000064],[123.3369119030001,13.97467940400003],[123.34085518600011,13.971744131000039],[123.33959874300001,13.95556517400007],[123.3284923440001,13.936802208000072],[123.32228292700007,13.935812343000066],[123.31727455700003,13.922435767000023],[123.3113195630001,13.921802582000053],[123.28605346600013,13.891644698000052],[123.29215339300002,13.88359278300004],[123.29550171900007,13.871202432000075],[123.30776331900006,13.85926207400007],[123.323293078,13.819436554000047],[123.32129474600004,13.801757607000066],[123.3149034150001,13.788076406000073],[123.30532974400013,13.779722119000038],[123.28805809400002,13.770867767000025],[123.27634157500006,13.750642450000043],[123.26879846200006,13.745348787000069],[123.2442910630001,13.736798253000073],[123.22932266500005,13.729124393000063],[123.2053409990001,13.72735375600007],[123.1623355270001,13.730609504000025],[123.11508652200007,13.728059541000048],[123.1164341440001,13.737608255000051],[123.09387588800008,13.745668638000042],[123.04756701700002,13.773978055000043],[123.04984451300004,13.821097523000043],[123.06069556700004,13.837581502000035],[122.9935150020001,13.891340081000067],[122.95698706100006,13.918252184000039],[122.94104603600012,13.922882583000046],[122.92858871300005,13.922099048000064],[122.92109169100002,13.938515966000065],[122.90082775600001,13.940135232000044],[122.90382023100005,13.948699912000052],[122.89186546600003,13.96438053000003],[122.85295762900012,13.976679415000035],[122.84465426400006,13.98558823600007],[122.79251799700013,14.013752262000024],[122.66522009700009,13.983192314000064],[122.62832535300004,13.972545667000075],[122.6201502670001,13.967995488000044],[122.58387379100009,13.961811396000028],[122.55241423100006,13.947554817000027],[122.56714718900004,13.937134659000035],[122.5648371750001,13.926952761000054],[122.55734135200011,13.925190435000047],[122.57103774200003,13.902811205000036],[122.59703058900004,13.895255462000023],[122.60470290100012,13.899374442000063],[122.61388522900006,13.895689229000023],[122.63511355100003,13.87673209800005],[122.64307396300002,13.863582722000046],[122.64954331400008,13.861778515000028],[122.65127577600003,13.850805381000042],[122.64303124100002,13.843485027000042],[122.65319974500005,13.82687168500007],[122.66885399900004,13.810537683000062],[122.67573413000004,13.810119790000046],[122.67894220900007,13.826469204000034],[122.6873048540001,13.826507319000026],[122.70398778700007,13.81613738100003],[122.71043766900006,13.820467851000046],[122.73228952400007,13.812026611000022],[122.74886469900002,13.796005327000046],[122.75885358800008,13.79110713800003],[122.75380245600002,13.783092560000053],[122.76358983300008,13.778696082000069],[122.7795410120001,13.764207882000049],[122.79563379000002,13.757071967000059],[122.80496814000003,13.749849160000053],[122.81730029200004,13.747012829000028],[122.83089522600005,13.736124777000047],[122.84954888100005,13.710606004000052],[122.86202012100011,13.68971127200007],[122.85239305100004,13.678763138000022],[122.84281828100006,13.682174589000057],[122.83402047600009,13.670616633000064],[122.82440749800001,13.64170255500005],[122.83251415900008,13.639714566000066],[122.83436953600007,13.629796746000068],[122.86012482900003,13.606871930000066],[122.86968381800013,13.601763830000039],[122.8707385690001,13.594725648000065],[122.8851651970001,13.58716103000006],[122.88821281900005,13.57615427500002],[122.90854491400013,13.570221324000043],[122.92124067100008,13.556229787000062],[122.94033234100004,13.552899487000047],[122.9611224680001,13.541133435000061],[122.97320068800002,13.523281412000072],[122.99059503600006,13.520354040000027],[123.00096567200002,13.522938082000053],[123.03878104400007,13.501556891000064],[123.0443830270001,13.50894517900002],[123.06784112000003,13.498199472000067],[123.07877926400012,13.48774246900007],[123.11582551100004,13.475420252000049],[123.13587983800004,13.464503751000054],[123.14314784000008,13.454232880000063],[123.1564791080001,13.456053425000052],[123.18844368300007,13.434588865000025],[123.20074582400004,13.418608176000074],[123.1992286420001,13.407779237000055],[123.20666102000007,13.392712311000025],[123.20083983400002,13.388385794000044],[123.20850249800003,13.370942306000073],[123.205707833,13.357319532000075],[123.21982098900004,13.334292116000029],[123.22533950000003,13.331745277000035],[123.234355896,13.313369110000055],[123.2385032300001,13.290611229000035],[123.24632322900004,13.286959527000022],[123.26372438600004,13.267450680000026],[123.28127328200003,13.258541065000031],[123.28522357100007,13.269512651000069],[123.31225141000004,13.287249039000073],[123.33555191200004,13.294827203000068],[123.3526878670001,13.306672606000062],[123.34625460200006,13.316078251000022],[123.33571568,13.318695996000029],[123.32718364700008,13.327270271000032],[123.33292006700005,13.347676081000031],[123.34140162100005,13.357780860000046],[123.35230857900001,13.358739036000031],[123.37347123000008,13.348629537000024],[123.37317003100007,13.33751864900006],[123.38393397400013,13.336091727000051],[123.39259550500005,13.341061079000042],[123.39879749300009,13.33465374700006],[123.40645509100011,13.347575831000029],[123.41758121300005,13.352300169000044],[123.43280213500009,13.363097290000042],[123.4585464270001,13.367820793000021],[123.46802729700006,13.363971094000023],[123.49383574500008,13.361898781000036],[123.49379612100006,13.344597269000076],[123.51239273900002,13.346792858000072],[123.52370334700002,13.352766140000028],[123.55561125500003,13.354617189000066],[123.55934980300003,13.360391644000057],[123.57150571400007,13.365336622000026],[123.56798881000009,13.371857841000063],[123.57621389300004,13.378277725000034],[123.58243122100009,13.395386389000063],[123.58806336800002,13.422057589000076],[123.5812924910001,13.448367139000023],[123.57268960300009,13.458021292000069],[123.55664269700004,13.469524604000071],[123.54544748100011,13.485836639000068],[123.54328423700008,13.501666299000018],[123.54560845100002,13.516697864000035],[123.60125067900003,13.522687456000027]]],[[[123.29880567000009,14.12880004900006],[123.29041319500006,14.122327985000025],[123.30642062800007,14.111382064000054],[123.31398629000013,14.098533596000037],[123.32586966800011,14.098748714000067],[123.32149866300007,14.115932045000022],[123.314100918,14.123958863000043],[123.29880567000009,14.12880004900006]]]]},"properties":{"adm1_psgc":500000000,"adm2_psgc":501700000,"adm2_en":"Camarines Sur","geo_level":"Prov","len_crs":1370001,"area_crs":5280741968,"len_km":1370,"area_km2":5280},"id":501700000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[124.20623305500011,14.100054783000074],[124.19255616600003,14.088147639000056],[124.18818728000007,14.075981977000025],[124.18965606100006,14.067947529000035],[124.17725178800004,14.060315551000032],[124.17037226800005,14.050681378000034],[124.15762043100005,14.049873715000043],[124.14087777900009,14.063700932000073],[124.1291612440001,14.059511283000063],[124.12709720500004,14.048880841000031],[124.12972229200012,14.029409969000028],[124.13971512400009,14.01327862200003],[124.1275881470001,14.00288639300004],[124.13072060100002,13.995912050000072],[124.1291788410001,13.97085429400005],[124.13482851700007,13.963179944000045],[124.14242202300011,13.943047077000076],[124.14751817000001,13.936184676000039],[124.14717092900001,13.911068650000061],[124.14439393200009,13.89988535200007],[124.13106053500006,13.883604488000058],[124.13677278700004,13.870854916000042],[124.13757621100001,13.854722379000062],[124.13338025900009,13.836725525000077],[124.13287696900012,13.82049255000004],[124.13610895600004,13.797710867000031],[124.12734955900011,13.77845727800007],[124.12827172400011,13.768696247000035],[124.12175546400012,13.752154167000072],[124.10450403000004,13.739338787000065],[124.10530052500008,13.725276284000074],[124.09971635000011,13.712262449000034],[124.0905913260001,13.70033067600002],[124.06396273900009,13.693329240000025],[124.05765363900002,13.684057274000054],[124.04698826000003,13.677533347000061],[124.04536680800004,13.671422044000053],[124.02443688000005,13.664490482000074],[124.04095315300005,13.635123451000027],[124.0566759280001,13.619814695000057],[124.05732953100006,13.596064353000033],[124.06893563900007,13.604173915000047],[124.09594956300009,13.598276601000064],[124.10582369100007,13.59353484400003],[124.1240590540001,13.578168798000034],[124.13731985400013,13.574512147000064],[124.14380605100007,13.567936287000068],[124.14762075700001,13.55584983500006],[124.16471201400009,13.53896340000006],[124.18506637300005,13.522798058000033],[124.21011749100013,13.518389021000074],[124.21465130400009,13.52353775100005],[124.20590536300007,13.54295626900006],[124.21308117,13.562063805000035],[124.23462664400006,13.58241015800007],[124.24737351800002,13.590502482000032],[124.27404866200004,13.595806451000042],[124.2971457640001,13.593258200000033],[124.31187109400001,13.588708334000048],[124.313137761,13.575020781000035],[124.32638436500008,13.557551820000068],[124.34310525,13.572501517000033],[124.34405555500008,13.592756129000065],[124.35033036700008,13.605391854000063],[124.34429414300006,13.623047924000046],[124.34884962600006,13.627643166000041],[124.341941893,13.640050556000062],[124.3471584040001,13.64869306400004],[124.35624401000008,13.650098842000034],[124.3622512390001,13.657881859000042],[124.37776437100001,13.659547165000047],[124.37851197200007,13.646600778000051],[124.38986687800003,13.655477328000075],[124.4092056400001,13.660349758000052],[124.41083103900006,13.68450559100006],[124.38908751300006,13.691667916000027],[124.39675525900009,13.70393221300003],[124.38506534800001,13.711425806000019],[124.39098167300006,13.71915040500005],[124.38812112600012,13.729259789000027],[124.40055694400009,13.739349988000068],[124.3958813500001,13.75099432200005],[124.40728033500012,13.750708709000035],[124.40135115400007,13.769317762000071],[124.39329785600012,13.775752871000066],[124.40883129400005,13.784466219000022],[124.41444609200006,13.781283977000042],[124.41371334300004,13.811656851000066],[124.40768461500012,13.823502847000043],[124.41478461900009,13.834536498000036],[124.39988276600002,13.839164935000042],[124.40958336300001,13.848221361000071],[124.42122453600008,13.846954354000044],[124.41586343000004,13.858329317000027],[124.40053018000003,13.857726107000074],[124.41257577500006,13.869317030000047],[124.4014059650001,13.874554457000045],[124.39565916500011,13.883948691000057],[124.3865231210001,13.877331076000074],[124.38460542600002,13.892885675000057],[124.36406216700004,13.89680463900004],[124.35422380400009,13.909274554000032],[124.35553119100008,13.923889580000036],[124.35178777200008,13.937153583000052],[124.33496381600004,13.936987011000042],[124.32073555000012,13.910057338000058],[124.30927491600006,13.918434579000063],[124.30979976000003,13.931660511000075],[124.30037739600004,13.94332745200006],[124.28727080600004,13.94183918500005],[124.28216734400006,13.958934525000076],[124.27946535800002,13.998246454000027],[124.27068472400003,14.015108987000076],[124.25944608800012,14.01869841100006],[124.2646499110001,14.028612724000025],[124.25156903100003,14.039069706000078],[124.24919765400011,14.04921027000006],[124.2226103270001,14.074101137000069],[124.21522766500006,14.078726213000039],[124.21178433500005,14.09412817400005],[124.20623305500011,14.100054783000074]]],[[[124.04739697500008,14.013784642000074],[124.04379297100002,14.029429330000028],[124.03473919600003,14.02674539700007],[124.0373936100001,14.018571988000073],[124.04739697500008,14.013784642000074]]],[[[124.32627071400009,13.987023343000034],[124.32353253700012,13.975151894000021],[124.31121059400004,13.979017297000041],[124.31343026900005,13.968361761000038],[124.30945620500007,13.960471262000052],[124.32146883400004,13.953390123000077],[124.32678536600008,13.94131120900005],[124.34249568000007,13.942154280000064],[124.35463149100008,13.951619231000054],[124.34557419000008,13.958071780000068],[124.34627687800004,13.964825527000073],[124.33414040500008,13.970891754000032],[124.32627071400009,13.987023343000034]]]]},"properties":{"adm1_psgc":500000000,"adm2_psgc":502000000,"adm2_en":"Catanduanes","geo_level":"Prov","len_crs":479965,"area_crs":1460034357,"len_km":479,"area_km2":1460},"id":502000000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[122.88724233000005,13.140168842000035],[122.89541264300011,13.146860223000035],[122.87020807700003,13.153634098000055],[122.8710664780001,13.145131240000069],[122.88724233000005,13.140168842000035]]],[[[123.38470637300007,12.693603422000024],[123.37541049900005,12.717705351000063],[123.36408224700007,12.72661355200006],[123.34536505400003,12.746659622000035],[123.33811168800003,12.748262347000034],[123.32756066900005,12.771797507000029],[123.31893340400005,12.781200027000068],[123.30858795000006,12.781257613000038],[123.3053286060001,12.793216669000062],[123.286954551,12.819855407000036],[123.28556772500008,12.835141752000023],[123.27984338600004,12.844273437000023],[123.28302033700004,12.855023499000025],[123.27613173300006,12.867321799000022],[123.28062610600013,12.874941484000033],[123.27747667300004,12.888033419000065],[123.2685787590001,12.895622970000034],[123.23106947300005,12.910972345000063],[123.22529982100002,12.905995773000031],[123.21145928700004,12.909417980000061],[123.19994791200007,12.908075910000035],[123.17965743100001,12.91722377100007],[123.167440757,12.938771369000051],[123.16212008600007,12.941120559000069],[123.15783960400006,12.962234738000062],[123.14314589700007,12.970764771000061],[123.14590495900006,12.980772013000031],[123.13544925800011,13.005504754000073],[123.12454270300009,13.021964314000058],[123.11415259300007,13.032648238000036],[123.10709721700006,13.028452009000032],[123.09690703800003,13.047956072000035],[123.09602849600005,13.061543330000063],[123.09123940200004,13.063781642000038],[123.08157390400004,13.080679215000032],[123.0649185970001,13.099862079000046],[123.0550168530001,13.118644455000037],[123.04809213400007,13.121594924000021],[123.04481751900006,13.135474984000039],[123.03105174300003,13.13963452100006],[123.01589067600001,13.135860482000055],[123.00466859900007,13.147718922000024],[122.99022052200007,13.156166976000064],[122.98462061000009,13.143650717000067],[122.97527216800007,13.13229121800003],[122.96212428700007,13.124383794000035],[122.94562797800005,13.122734372000023],[122.92851598900006,13.112618472000065],[122.9295607050001,13.10846721900003],[122.94541796300005,13.094740252000063],[122.9573844580001,13.090179440000043],[122.95079594000003,13.07818560100003],[122.94321181500005,13.05450316000002],[122.95143708700004,13.031613193000055],[122.96138029200006,13.033921937000061],[122.96338682700004,13.026249918000074],[122.978197786,13.010110225000062],[122.9858733440001,13.006291934000044],[123.00974234300008,13.008734116000026],[123.02744423,12.998240803000046],[123.06392131000008,12.998414290000026],[123.068606584,12.992061537000039],[123.06563511600007,12.977884245000043],[123.07806044000006,12.957175832000077],[123.09647210100002,12.943510826000024],[123.1043906960001,12.945372657000062],[123.10954303300004,12.935718670000025],[123.10828387800007,12.927697160000033],[123.11720092100006,12.922036126000023],[123.12119922400007,12.912878259000024],[123.14779562100013,12.904899631000037],[123.14031428500006,12.899045917000024],[123.14959190400009,12.888671887000045],[123.16105312000003,12.889835910000045],[123.17411584100012,12.88120722600007],[123.18475935600009,12.861526672000025],[123.1981925660001,12.844430862000024],[123.21183728900006,12.847812968000026],[123.21888656700001,12.836217513000063],[123.24219443900007,12.83886117600002],[123.26352995600008,12.83076166300003],[123.26794242000005,12.81429198300003],[123.27771650200009,12.812501802000043],[123.29084388000001,12.800633883000048],[123.29214834900006,12.790193560000032],[123.30272515700007,12.782768516000033],[123.30989631600005,12.77015804600006],[123.31217549900009,12.751887519000036],[123.32246511300004,12.742285312000034],[123.33577064300005,12.72086180600007],[123.34673678200011,12.713387222000051],[123.35764522100008,12.697592148000068],[123.37054779300003,12.693764529000077],[123.38470637300007,12.693603422000024]]],[[[122.95899099100006,13.12914199200003],[122.96390446400005,13.135817862000067],[122.9723388000001,13.135320679000072],[122.97855497100011,13.142999261000055],[122.97607083300011,13.157361045000071],[122.9470940010001,13.139884093000035],[122.95899099100006,13.12914199200003]]],[[[123.60168914800009,12.67526867400005],[123.61166169100011,12.645019359000061],[123.59517089200006,12.640706150000026],[123.58245492800006,12.641714084000055],[123.58493095500012,12.627800735000049],[123.59529205400007,12.605218554000029],[123.61135061100003,12.60705407000006],[123.60996618400009,12.600587989000074],[123.6141296180001,12.583385283000037],[123.62199152800007,12.573316783000053],[123.62511270900006,12.559387839000065],[123.63478447200009,12.542179080000038],[123.6494979680001,12.532593692000033],[123.65266875600003,12.52206644200004],[123.66347238300011,12.51154333900007],[123.66518270200004,12.498698791000036],[123.67063382700007,12.491137888000024],[123.6870197390001,12.48004929600006],[123.68379114900004,12.46468543100002],[123.699960732,12.44858396600006],[123.70856949000004,12.435457292000024],[123.723617579,12.42163121700003],[123.72478266300006,12.406942553000022],[123.73839424900008,12.397683587000072],[123.76682161000006,12.367186939000021],[123.7881930730001,12.339109320000036],[123.79588830400007,12.350168796000045],[123.80019856500007,12.371638726000068],[123.78456560400002,12.379970140000072],[123.79320184300003,12.389253420000045],[123.79131836200008,12.409881351000022],[123.78275494900005,12.420684017000038],[123.76956533500004,12.46541102300006],[123.77237601000002,12.476287225000023],[123.76497087300004,12.481637478000039],[123.77002182500007,12.492428342000037],[123.75518514700002,12.517938958000057],[123.74851710400004,12.537869067000033],[123.74046504500006,12.554273675000047],[123.736259355,12.570395805000034],[123.72436896400008,12.569288930000027],[123.73563206700011,12.583876451000036],[123.72532623600011,12.614558064000049],[123.70863610100002,12.616975014000047],[123.70889864800006,12.624727553000069],[123.69204679800009,12.638379908000047],[123.68037814400009,12.643381230000044],[123.66165949700007,12.64481613200007],[123.64401529100009,12.663063909000073],[123.62491526900011,12.693712492000031],[123.61211630000004,12.688173737000056],[123.60168914800009,12.67526867400005]]],[[[124.0634376060001,11.720654878000063],[124.07356077700001,11.73010143400006],[124.07327468500011,11.747279479000042],[124.05932900800008,11.775614324000058],[124.05580730700002,11.787634757000033],[124.0558850320001,11.804851029000075],[124.06745358400009,11.82835569800005],[124.06548263700006,11.835399188000052],[124.0700903300001,11.852563588000065],[124.05586561900009,11.87308611700007],[124.0536318820001,11.88069592100004],[124.03718184600005,11.90619544300006],[124.029568659,11.923507222000069],[124.0279874050001,11.940666770000064],[124.01004886800003,11.959808234000036],[124.01054590500009,11.968999223000024],[123.99937745000013,11.977588413000033],[123.99454605200005,11.994327824000038],[124.00090660100012,11.999474697000036],[123.99837815600007,12.01200836400005],[124.00910393800007,12.012010700000074],[124.01484937200007,12.005388508000063],[124.01773007300007,11.985183773000076],[124.0292642280001,11.975884512000047],[124.05118051800002,11.94932809100004],[124.05172377600002,11.968941248000021],[124.04535362900005,11.974850859000071],[124.02729179800006,12.00400424000003],[124.00627613300004,12.02399040900002],[123.99027157500007,12.051445467000065],[123.96932562300003,12.093504038000049],[123.94985348500006,12.110325450000062],[123.94636581700003,12.12229048000006],[123.93363011800011,12.140999360000023],[123.9208953650001,12.150191915000049],[123.9093320510001,12.167584265000073],[123.91209506400003,12.179788663000068],[123.89822655500006,12.193380635000038],[123.89594097000007,12.207088485000043],[123.88152324400006,12.219732537000025],[123.8721463620001,12.221591475000027],[123.86539040000004,12.21355592000003],[123.86869932800005,12.199879599000038],[123.8532308980001,12.195024155000054],[123.838948887,12.217435254000064],[123.82317466700012,12.235991155000024],[123.8086345260001,12.243858590000059],[123.79909027300006,12.243862799000052],[123.7871659660001,12.236390905000064],[123.78104690400005,12.226152313000057],[123.79133650500013,12.203001804000051],[123.78315694200012,12.195272345000037],[123.75751730700006,12.234548172000077],[123.75552903000005,12.246077221000062],[123.74442096200005,12.252371287000072],[123.73918176500003,12.267017452000067],[123.73009701900004,12.274533656000072],[123.709752449,12.307329472000049],[123.69675007700005,12.330615729000042],[123.67205287800004,12.347813817000034],[123.65596277700003,12.340031054000066],[123.64045447500007,12.349951232000022],[123.63264560200001,12.360788640000067],[123.6374983710001,12.373304525000037],[123.6249612060001,12.379024548000073],[123.5989047060001,12.355323230000067],[123.58881688500003,12.35219302100006],[123.5855691470001,12.36965258500004],[123.59444671100005,12.386253243000057],[123.59273867600007,12.396279745000074],[123.5806984410001,12.406962412000041],[123.57125034800004,12.410351674000026],[123.56202983900005,12.452699861000042],[123.5546635600001,12.462505519000045],[123.54452019500002,12.457373072000054],[123.52317077000009,12.455556054000056],[123.5023124500001,12.475625722000077],[123.49634551500002,12.476065325000034],[123.47426219700003,12.48907081700003],[123.46577798500005,12.501694230000057],[123.44361442800003,12.51693667300003],[123.40335995300006,12.522411757000043],[123.39774805300011,12.513164267000034],[123.37509545500005,12.508191571000054],[123.374750456,12.47379334300007],[123.34752315700008,12.456067999000028],[123.3455301790001,12.441537332000053],[123.32502578600008,12.442132464000053],[123.33165936200011,12.449884737000048],[123.32266270900004,12.46083746000005],[123.32529063700008,12.470050879000041],[123.34545686100013,12.476880742000048],[123.34758240200007,12.483253899000033],[123.35908915000005,12.480401283000049],[123.3596014090001,12.494221784000045],[123.35413555900004,12.504536561000064],[123.35298910000007,12.517932735000045],[123.34418349100008,12.519444090000034],[123.33955769200008,12.53644437200006],[123.34526905300004,12.541773211000075],[123.36111564300006,12.540263745000061],[123.36476060200005,12.545554228000071],[123.34599826600004,12.551286360000065],[123.31976360300008,12.57136421800004],[123.30454464900004,12.578543344000026],[123.28474855900002,12.573387832000039],[123.26557422200007,12.589935192000043],[123.245214583,12.60016521500006],[123.23405885300009,12.58941899900003],[123.24971879300006,12.561486151000054],[123.24140247100001,12.561164634000022],[123.24988533900013,12.521087799000043],[123.24728939700003,12.514370605000071],[123.25082369600011,12.502664931000027],[123.25221668800009,12.471496225000065],[123.25103285000012,12.456963547000043],[123.25540175300011,12.45288593600003],[123.27020895300005,12.45759988000003],[123.27903451300004,12.42760368000006],[123.28763295800003,12.421307737000062],[123.28514910700007,12.41050957200002],[123.27914628500004,12.40483371700003],[123.27173424900003,12.381541303000061],[123.25929600200004,12.376954759000059],[123.26512439800001,12.366088268000055],[123.266885967,12.333857051000049],[123.25759523800002,12.321521469000059],[123.24629867900002,12.301440895000042],[123.24329807900004,12.289471159000072],[123.23534985700007,12.280727389000049],[123.22771504700006,12.279396516000077],[123.22276714400004,12.266754035000078],[123.22580530900007,12.247114767000026],[123.21699576900005,12.238999227000022],[123.2180223910001,12.231889557000045],[123.22777762900012,12.21701338300005],[123.24011570400012,12.22177250800007],[123.2504012280001,12.236079446000073],[123.26169746200003,12.246068080000043],[123.27499185500005,12.23770196400005],[123.28546782300008,12.219182518000023],[123.2951231520001,12.225072889000048],[123.30104470900005,12.215883112000027],[123.28837929400004,12.198837501000067],[123.28259276000007,12.212837313000021],[123.26959447800006,12.198173413000061],[123.26776903500001,12.185458032000042],[123.27652196200006,12.182032955000066],[123.28220392900005,12.170487019000062],[123.2733086830001,12.160288930000036],[123.25188430800007,12.149535141000056],[123.24142555000005,12.135507668000061],[123.24943116100006,12.129390113000056],[123.2467883400001,12.121699401000058],[123.23099865800009,12.120005216000036],[123.22601524000004,12.131935769000052],[123.2195422330001,12.132561428000031],[123.21227336700008,12.11575808200007],[123.2102547920001,12.094165194000023],[123.20541707900009,12.084762237000065],[123.20624749700005,12.06176268300004],[123.20101158500006,12.050291101000028],[123.19193492700002,12.042170105000027],[123.19585889000007,12.026605274000076],[123.19207661600002,12.011461610000024],[123.18227084500006,12.003374440000073],[123.15630250400011,11.961742104000049],[123.15753670400011,11.954135274000066],[123.14377318400011,11.93610079800004],[123.14253482300012,11.93036259400003],[123.15102050300005,11.921750471000054],[123.15977543700002,11.905933180000035],[123.16642247500012,11.904045479000047],[123.17929247400002,11.912399487000071],[123.18517828800007,11.925468232000071],[123.21055198200008,11.950305557000037],[123.23074134800004,11.95802172500004],[123.24192439400008,11.96785712500002],[123.25320802600005,11.985174767000045],[123.25300268100013,11.99011243700005],[123.26700605400002,12.008331653000026],[123.27775403500003,12.016399588000068],[123.2896389030001,12.017345651000028],[123.30204923100007,12.028500114000051],[123.31417435900005,12.054961752000054],[123.32428088400003,12.070331540000039],[123.335499776,12.094012758000078],[123.35676335300003,12.099134853000066],[123.37141425400011,12.111872728000035],[123.37477605700009,12.121829190000028],[123.39753105400005,12.152558685000031],[123.40027652700007,12.160139786000057],[123.41874603100007,12.180384770000046],[123.42724048700005,12.19969145500005],[123.45156105900003,12.21015296100006],[123.48544382800003,12.210787135000027],[123.4883252740001,12.216568280000047],[123.5109987610001,12.216769222000037],[123.53229312300004,12.21283009800004],[123.56464539300009,12.181642447000057],[123.56689092900001,12.16746712500003],[123.59081895300005,12.144613453000032],[123.5943014290001,12.131166677000067],[123.61311236400002,12.093293615000052],[123.60015413900011,12.079608387000063],[123.6035041130001,12.074084062000052],[123.62765562100003,12.070394646000068],[123.64127920000011,12.070616406000054],[123.641890116,12.062940054000022],[123.65508563300013,12.042834139000036],[123.68492321200007,12.025534357000026],[123.7033679760001,12.016986373000064],[123.71437574200002,12.005898494000062],[123.73024582900007,11.985598809000068],[123.72790026200005,11.974290036000072],[123.71531751300006,11.962930950000041],[123.71390673200007,11.954249259000052],[123.72847079400003,11.945029728000065],[123.72180201300012,11.931963258000053],[123.73061386600013,11.930548101000054],[123.74669744500011,11.922167869000077],[123.76823506400001,11.927181095000037],[123.77905060800005,11.921128085000019],[123.79155585300009,11.922524850000057],[123.83870914200008,11.909778483000027],[123.86226174100013,11.898029414000064],[123.88191981400009,11.884106036000048],[123.89712599200006,11.866389936000074],[123.91874343600013,11.86679444900005],[123.9401848870001,11.85101051600003],[123.94886241300004,11.840940144000058],[123.97794824100005,11.823292618000037],[123.98265335100007,11.813819106000038],[123.99201821600003,11.807161912000025],[124.00989589300002,11.788278846000027],[124.02489054700003,11.760718764000043],[124.02722843900006,11.752615975000026],[124.040619009,11.736403387000053],[124.0538726750001,11.724139117000048],[124.0634376060001,11.720654878000063]]],[[[123.24577048700007,12.384277778000069],[123.23361313200007,12.371049595000047],[123.24173636600005,12.366049261000057],[123.25222600400004,12.380389456000044],[123.24577048700007,12.384277778000069]]],[[[123.84433538300006,12.254019270000072],[123.84339446100012,12.250585483000066],[123.8628834750001,12.229437525000037],[123.8661070070001,12.240287638000042],[123.86045606000005,12.246072647000062],[123.84433538300006,12.254019270000072]]],[[[123.26191568500009,12.191971138000044],[123.25209991800011,12.179403697000053],[123.23794349900005,12.174856889000065],[123.23837548600011,12.169386794000049],[123.25470975400005,12.171443593000044],[123.26191568500009,12.191971138000044]]],[[[123.672308819,11.871996177000028],[123.67566740200006,11.887066993000078],[123.67396920300008,11.90191330700003],[123.66184460600005,11.90459135100002],[123.65838207100012,11.89504729400005],[123.66065607800009,11.880064959000036],[123.672308819,11.871996177000028]]],[[[124.08833838700004,11.867877313000065],[124.09652110700007,11.872166688000046],[124.08824128700009,11.882196575000023],[124.0808957180001,11.875277926000026],[124.08833838700004,11.867877313000065]]],[[[123.12901205800004,11.838778287000027],[123.14191494300007,11.853683909000042],[123.13662729200009,11.860854220000022],[123.12242310600004,11.857970335000061],[123.11786774000008,11.852341683000077],[123.118596367,11.837503573000049],[123.12901205800004,11.838778287000027]]]]},"properties":{"adm1_psgc":500000000,"adm2_psgc":504100000,"adm2_en":"Masbate","geo_level":"Prov","len_crs":1382930,"area_crs":3986492499,"len_km":1382,"area_km2":3986},"id":504100000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[123.48226570000008,12.988444596000024],[123.493268015,12.982890014000075],[123.49864280300007,12.972962504000062],[123.5326825290001,12.93740772700005],[123.5354095790001,12.94791368300002],[123.54399909600012,12.950059346000046],[123.55597734900005,12.946071962000076],[123.5641796760001,12.93882951900002],[123.59360334500003,12.902323789000032],[123.62080686200011,12.897836895000067],[123.63529437100011,12.887476989000046],[123.65275190400008,12.870512329000062],[123.65893497000002,12.889977803000024],[123.65196709400006,12.898522215000067],[123.66213564300006,12.917684413000071],[123.67900517300006,12.921907341000063],[123.69057378800005,12.919089575000045],[123.67789513000002,12.901711466000048],[123.68229453600009,12.876126518000033],[123.69493367000008,12.866718129000047],[123.69887690300003,12.875910347000058],[123.68837043000009,12.886821249000034],[123.69847170700008,12.889805605000051],[123.71695356200007,12.884538500000073],[123.72875816600003,12.870047633000068],[123.72378867400005,12.860138614000046],[123.73396664600011,12.845356693000042],[123.7442979230001,12.845886503000031],[123.76331582500008,12.867160750000041],[123.76240178500007,12.875350942000068],[123.77197336200005,12.880885787000068],[123.7807641490001,12.868858919000047],[123.80622406400005,12.86608856200007],[123.81635878800012,12.881678599000058],[123.82792810500007,12.878459920000065],[123.84200255200005,12.901616482000064],[123.85481788800007,12.897815445000049],[123.85938180200004,12.92182061200003],[123.8685914260001,12.925891325000066],[123.8711737000001,12.934846706000027],[123.87995651700008,12.936171512000044],[123.87742709000008,12.947531708000042],[123.88122531500007,12.957560885000078],[123.88430714700009,12.978461407000054],[123.8963293390001,12.973607014000036],[123.92370202400002,12.978449296000065],[123.92885884200007,12.965741550000075],[123.94306619900009,12.956916420000022],[123.96967589100007,12.95647901700005],[123.98588269000004,12.96358454500006],[124.0195786600001,12.973360303000048],[124.02972809700009,12.967084999000065],[124.0388210100001,12.945046012000034],[124.04186967300006,12.930591922000076],[124.03278417400008,12.90981447900003],[124.02680362,12.89007923100007],[124.0185593540001,12.87797211800006],[124.00395418100003,12.87552102400002],[123.99246562200005,12.868455077000021],[123.98303600500003,12.879476995000061],[123.97333772700006,12.876525216000061],[123.94747819300005,12.874881554000067],[123.94163075500013,12.865335681000033],[123.94462318500008,12.849476834000027],[123.93675364800004,12.844822186000044],[123.9096675500001,12.851363311000055],[123.87692118100007,12.870924913000065],[123.85786120900002,12.873825786000053],[123.86352448600007,12.861491552000077],[123.85563894900007,12.848235342000065],[123.84859464700003,12.84820280700006],[123.84310625400009,12.838377349000043],[123.83689390200006,12.838088111000047],[123.83558168200013,12.825071714000048],[123.84588404300007,12.79560230000004],[123.84649551300005,12.747056337000059],[123.84980453700007,12.720648854000048],[123.8603369540001,12.687899834000063],[123.87125892200005,12.673751633000055],[123.87509012600005,12.65531693500003],[123.8914198880001,12.644521178000044],[123.90443930300012,12.64249974200004],[123.91279764,12.637402045000043],[123.91643574700004,12.619359121000057],[123.92426773800004,12.616748341000063],[123.93050974300002,12.628790070000036],[123.93743958000005,12.62532819800003],[123.9366967530001,12.61441998300006],[123.94469304400003,12.60257141900007],[123.94806318600001,12.58983082800006],[123.95632807400011,12.582935908000023],[123.95764167100003,12.574745070000063],[123.96972746000004,12.566543728000054],[123.97473392900008,12.556372977000025],[123.98197227800006,12.554839599000045],[123.98787217900006,12.546211454000055],[123.9952667460001,12.547416774000052],[124.00401763600007,12.540324514000076],[124.0441062210001,12.532966178000036],[124.0509434060001,12.539801157000056],[124.0699554040001,12.538262739000059],[124.0976451450001,12.556532570000059],[124.09597388900012,12.572572260000072],[124.08493469200006,12.580558769000048],[124.090328784,12.58801126900005],[124.10949149200006,12.596506126000062],[124.10297700800004,12.61395152700004],[124.09403249200011,12.621117555000067],[124.0941325540001,12.635989324000036],[124.11485640700005,12.651752332000056],[124.13389260000007,12.662086969000029],[124.13559203500006,12.670315444000037],[124.1295060120001,12.685916888000063],[124.13234856500003,12.69447184100005],[124.14215540600003,12.699786189000063],[124.13170167300008,12.734251369000049],[124.13735347900001,12.74287840900007],[124.14038171900005,12.756353287000024],[124.13742995900009,12.764558753000072],[124.14853845200004,12.772715160000075],[124.14770160600004,12.788666458000021],[124.15556476200004,12.808520696000073],[124.1551865350001,12.829460996000025],[124.14706130900004,12.844696220000062],[124.15156398700005,12.861752188000025],[124.13976054200009,12.87335507600005],[124.14137930700008,12.883197565000046],[124.1486411410001,12.891762170000046],[124.14365271300005,12.899077709000034],[124.13016341000004,12.891187729000025],[124.1215091680001,12.897657658000067],[124.11737146000006,12.908745986000042],[124.12781790300004,12.913475247000065],[124.12681722000004,12.928295955000065],[124.14219730100001,12.933617162000075],[124.148001023,12.965526690000049],[124.14116993300001,12.971229590000066],[124.14142512400008,12.979348510000024],[124.151504122,12.998062197000023],[124.16544264200003,13.006575499000062],[124.17160740700001,13.004305912000063],[124.18829003000008,13.009283795000044],[124.19828708700003,13.02197710800004],[124.19094150200009,13.031619290000037],[124.19610016500009,13.040766474000064],[124.19291605900004,13.060903855000047],[124.18791070500004,13.066762737000033],[124.17013276800004,13.06789224800002],[124.1351507810001,13.075707771000056],[124.11352144800003,13.065841269000032],[124.10691161200008,13.058676002000027],[124.10717200300009,13.045612759000047],[124.09697717400003,13.015240425000057],[124.08880485200007,13.003141693000034],[124.08264340100004,13.002029895000023],[124.07140861100004,13.01042192400007],[124.07085737700005,13.02059812700003],[124.06386762300006,13.033957506000036],[124.0454041270001,13.040861592000056],[124.03649328200004,13.041157854000064],[124.02221828100006,13.052212728000027],[124.0071188070001,13.076620243000034],[123.99197552600003,13.09228584600004],[123.97878366800012,13.093151440000039],[123.97384034900007,13.102009088000045],[123.9623214080001,13.10121003100005],[123.94799620100002,13.106125940000025],[123.939456618,13.118298482000053],[123.92676515300003,13.120887665000055],[123.92917038300006,13.102068074000046],[123.92101326300008,13.083766269000023],[123.9155897280001,13.054929226000066],[123.90670266300005,13.040932211000039],[123.89598666200006,13.03764349000005],[123.87528872300005,13.042301291000058],[123.85924674000012,13.040744483000024],[123.82253470700006,13.02440377700003],[123.80564823300006,13.019028077000028],[123.79577553900005,13.00827792900003],[123.7872156410001,13.004620741000048],[123.78231135300005,12.994530540000028],[123.76765605700007,12.986184890000061],[123.76215491200004,12.997107576000072],[123.74598040500007,12.996885520000037],[123.7364397980001,13.01621579400006],[123.73445022100007,13.026391081000043],[123.72238104200005,13.027039090000073],[123.72308167900009,13.034239268000023],[123.71473746600009,13.039926492000063],[123.68452626700004,13.02852085000006],[123.65000598900008,13.01932447300004],[123.62968937800008,13.010442943000044],[123.62025036800004,13.022980362000055],[123.58691683200004,13.022239605000037],[123.57486209300009,13.030070694000072],[123.56306575500003,13.02307481200006],[123.54809213500006,13.024415272000056],[123.53782893100005,13.01813417300002],[123.51782511400006,13.012754216000074],[123.49216108500002,13.00091114700007],[123.48226570000008,12.988444596000024]]],[[[123.88479865500007,12.874554861000037],[123.90210949200002,12.867940175000056],[123.90097198100011,12.879778396000061],[123.88119377400005,12.883823166000068],[123.88479865500007,12.874554861000037]]],[[[123.82063061500003,12.817851399000059],[123.8273540890001,12.82096592800002],[123.82686770100008,12.831400706000066],[123.81676391700013,12.831310105000057],[123.8088550100001,12.838485229000069],[123.79736757400008,12.839098278000051],[123.79430409000008,12.832090901000072],[123.82063061500003,12.817851399000059]]],[[[124.0925378730001,12.52381388400005],[124.10453201700011,12.529762819000041],[124.1024193290001,12.540265246000045],[124.09627588700006,12.54347148900007],[124.08896375400002,12.528257736000057],[124.0925378730001,12.52381388400005]]]]},"properties":{"adm1_psgc":500000000,"adm2_psgc":506200000,"adm2_en":"Sorsogon","geo_level":"Prov","len_crs":707760,"area_crs":1985336553,"len_km":707,"area_km2":1985},"id":506200000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.92162284600012,11.999319628000022],[121.90508849700005,11.988213816000043],[121.910296893,11.976976423000053],[121.92416211900002,11.961779904000023],[121.93356751000012,11.94007769500007],[121.94351172400003,11.940699905000033],[121.94698429200004,11.954844540000067],[121.93439107800009,11.957072397000045],[121.92720573300006,11.970059879000075],[121.92162284600012,11.999319628000022]]],[[[122.57735727300008,11.553467966000028],[122.57431884700009,11.563781681000025],[122.50787030400011,11.592123358000038],[122.4950665660001,11.594832677000056],[122.49623150200013,11.57795175100006],[122.48579240900006,11.559741923000043],[122.47492937000004,11.553764942000042],[122.45774135600003,11.550535951000029],[122.44663690100005,11.562591335000034],[122.4434120530001,11.575997051000058],[122.46047139000007,11.580008909000073],[122.48305983900002,11.562633574000074],[122.48473157500008,11.575115965000062],[122.47085333400003,11.584563536000074],[122.46562593700003,11.593524376000062],[122.44586291000007,11.608806424000022],[122.43373764700004,11.59767436100003],[122.43055891100005,11.611110025000073],[122.4220099920001,11.611882766000065],[122.39745368900002,11.635466659000027],[122.39861638600007,11.645491374000072],[122.40859741700002,11.646555625000076],[122.40869410500011,11.657871441000053],[122.43039513300006,11.651052535000076],[122.43347159000007,11.639783437000062],[122.46078944900013,11.613807832000077],[122.47652135200008,11.606616810000048],[122.48664180400009,11.594936050000056],[122.49225852100005,11.609933782000043],[122.45268663100002,11.634719858000036],[122.42577978800013,11.659076303000063],[122.39741526900002,11.695415923000043],[122.39062272600006,11.709199415000057],[122.39358715500009,11.717685703000027],[122.38536589500006,11.734491677000051],[122.37445671600007,11.738385246000064],[122.34476466000001,11.738372656000026],[122.33130037,11.735422485000072],[122.30221919300006,11.747664161000046],[122.27499079100005,11.768384858000047],[122.25842803700004,11.785607028000072],[122.23526191500002,11.788414241000055],[122.22487558000012,11.79607389000006],[122.22208112500003,11.813653740000063],[122.19964430100003,11.807878037000025],[122.18531555900007,11.81277714600003],[122.16460698600007,11.825291022000043],[122.13882496200006,11.825063338000064],[122.09948816500003,11.830272682000043],[122.0820770050001,11.836972984000056],[122.05697774600004,11.851601892000076],[122.03607051100005,11.866912076000062],[122.02510853000001,11.879563205000064],[122.0184560460001,11.893225010000036],[122.00033174300007,11.907702384000062],[121.97380907500006,11.920085119000019],[121.95993367500013,11.936479263000022],[121.95115797000007,11.939131072000064],[121.94799894900005,11.918429136000043],[121.91678278300004,11.902410129000033],[121.88707202000012,11.899884822000045],[121.88197357400009,11.884735659000057],[121.8834896620001,11.854602827000067],[121.88841652500004,11.848225484000068],[121.88225247300011,11.833468579000055],[121.8788387830001,11.810293],[121.86092850100012,11.77964142700006],[121.84359594500006,11.764169970000067],[121.8777692450001,11.771529970000076],[121.89276889900009,11.799825263000061],[121.90380822800012,11.799311806000047],[121.93343850300005,11.821365564000075],[121.96754248800006,11.823849226000048],[121.99037648900003,11.827633858000071],[122.00332330500011,11.825534597000058],[122.02240899100002,11.817209906000073],[122.06392905100007,11.794101714000021],[122.07541857100011,11.784862795000038],[122.0923394880001,11.776767171000072],[122.10901278300003,11.779049931000033],[122.1281677500001,11.763640585000076],[122.15647591200002,11.756762532000039],[122.1554060860001,11.74678345900003],[122.16945530700004,11.732364552000035],[122.17457459100001,11.696275940000024],[122.1706523490001,11.685672361000057],[122.14606124000011,11.656123132000063],[122.14205087300002,11.641073437000045],[122.14231530000008,11.618848266000043],[122.1491168750001,11.595908877000054],[122.13995703900004,11.566394845000046],[122.141238971,11.553002749000028],[122.15490996200003,11.531966966000025],[122.135959737,11.505061038000063],[122.1341435800001,11.473020229000038],[122.13804953300009,11.46445179400007],[122.16159341800005,11.44535398200003],[122.1661023710001,11.43668455100004],[122.16696420200005,11.402434884000057],[122.18810468400011,11.392383335000032],[122.19372804200007,11.374901635000072],[122.1919104650001,11.363839978000046],[122.18272222200005,11.345952808000048],[122.18456384000002,11.332032606000041],[122.19990772800008,11.311955905000046],[122.21426972200005,11.311229724000041],[122.2468685550001,11.317676399000048],[122.27312304000009,11.329970397000066],[122.29807632200004,11.348349114000028],[122.32608554300009,11.374853227000074],[122.34515057400006,11.408734009000057],[122.35076840300007,11.44225880600004],[122.37082335300012,11.42764624600005],[122.40012524700012,11.455984206000037],[122.399397539,11.474120096000036],[122.40507282600005,11.47768442800003],[122.43921808000003,11.475965538000024],[122.45351579300007,11.479252978000032],[122.47260793400005,11.476178983000066],[122.48457481000004,11.48872118600002],[122.50488909,11.484729438000045],[122.53002524900012,11.493157942000039],[122.52670540000008,11.512783739000042],[122.5326996450001,11.518185372000062],[122.535941728,11.535662641000046],[122.55077428000004,11.535207513000044],[122.56479972600006,11.546975991000068],[122.57376008400001,11.541323981000062],[122.57735727300008,11.553467966000028]]],[[[122.45845579500009,11.608081214000036],[122.43072736500007,11.638086020000062],[122.4255840080001,11.635033968000073],[122.43953144800003,11.619233050000048],[122.45845579500009,11.608081214000036]]]]},"properties":{"adm1_psgc":600000000,"adm2_psgc":600400000,"adm2_en":"Aklan","geo_level":"Prov","len_crs":507785,"area_crs":1683814691,"len_km":507,"area_km2":1683},"id":600400000},
{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[121.42638759100011,12.03124697100003],[121.42399204800006,12.037426775000029],[121.41005274000007,12.040940969000076],[121.40323033100002,12.056242509000072],[121.39795998000012,12.078112363000058],[121.40596645100004,12.105450589000045],[121.39327987200011,12.109151681000071],[121.38987036700009,12.122771822000061],[121.37027699300006,12.123531944000032],[121.35543284900008,12.115648940000028],[121.34544240100001,12.09519613800006],[121.34538048600007,12.086145033000033],[121.36191479200012,12.083407105000047],[121.36196881600006,12.074020756000039],[121.37928048000003,12.07247068700008],[121.38073897200003,12.063810733000027],[121.36268699800006,12.051347119000072],[121.3632794990001,12.03406825200005],[121.3728684010001,12.019505999000046],[121.37411922500009,12.007284026000034],[121.38185696000004,11.991193327000076],[121.38882099200009,11.98570397700007],[121.41854613300006,12.010417387000073],[121.42638759100011,12.03124697100003]]],[[[121.5752892710001,11.939182397000026],[121.55461210000011,11.959626902000023],[121.54047500700007,11.953899259000023],[121.538776331,11.94333458400007],[121.54681220000009,11.937111985000055],[121.53994738200002,11.909741335000033],[121.54049977200009,11.901814157000045],[121.54997085500007,11.892424072000038],[121.57028122500003,11.895482608000064],[121.5829525590001,11.905549648000033],[121.58189107700002,11.916914849000023],[121.57305218600004,11.92661053200004],[121.5752892710001,11.939182397000026]]],[[[121.45307829700005,11.869070062000048],[121.42605372700007,11.866644],[121.41332384600003,11.84088437500003],[121.43435607800008,11.84056739500005],[121.4780317210001,11.825476597000035],[121.49540629500007,11.82901057300006],[121.5169010210001,11.82687255500002],[121.53073911500007,11.846506273000045],[121.5086202320001,11.862040948000072],[121.47392105400003,11.863934297000071],[121.45307829700005,11.869070062000048]]],[[[122.19990772800008,11.311955905000046],[122.18456384000002,11.332032606000041],[122.18272222200005,11.345952808000048],[122.1919104650001,11.363839978000046],[122.19372804200007,11.374901635000072],[122.18810468400011,11.392383335000032],[122.16696420200005,11.402434884000057],[122.1661023710001,11.43668455100004],[122.16159341800005,11.44535398200003],[122.13804953300009,11.46445179400007],[122.1341435800001,11.473020229000038],[122.135959737,11.505061038000063],[122.15490996200003,11.531966966000025],[122.141238971,11.553002749000028],[122.13995703900004,11.566394845000046],[122.1491168750001,11.595908877000054],[122.14231530000008,11.618848266000043],[122.14205087300002,11.641073437000045],[122.14606124000011,11.656123132000063],[122.1706523490001,11.685672361000057],[122.17457459100001,11.696275940000024],[122.16945530700004,11.732364552000035],[122.1554060860001,11.74678345900003],[122.15647591200002,11.756762532000039],[122.1281677500001,11.763640585000076],[122.10901278300003,11.779049931000033],[122.0923394880001,11.776767171000072],[122.07541857100011,11.784862795000038],[122.06392905100007,11.794101714000021],[122.02240899100002,11.817209906000073],[122.00332330500011,11.825534597000058],[121.99037648900003,11.827633858000071],[121.96754248800006,11.823849226000048],[121.93343850300005,11.821365564000075],[121.90380822800012,11.799311806000047],[121.89276889900009,11.799825263000061],[121.8777692450001,11.771529970000076],[121.84359594500006,11.764169970000067],[121.86262965800006,11.756320428000036],[121.89712543900009,11.757277147000025],[121.91819855300004,11.767649724000021],[121.94257220400006,11.761091173000066],[121.9479451640001,11.757006834000034],[121.98709272500004,11.752189331000068],[122.0126258030001,11.736152684000045],[122.02033511000002,11.741952294000043],[122.044999446,11.732177607000041],[122.06874017900009,11.73872911500007],[122.08480729700011,11.725987789000044],[122.10065714200005,11.700553808000048],[122.10122186300009,11.686518564000039],[122.09577114900004,11.669524421000064],[122.10152019400003,11.652800988000024],[122.0966686820001,11.629919765000064],[122.09292413800007,11.590018858000063],[122.08681280600001,11.578221058000052],[122.08665763200008,11.561745979000023],[122.07827889700003,11.53662182700003],[122.08580505300007,11.505236615000056],[122.07358871800012,11.477525995000065],[122.05821013000002,11.46857943500004],[122.0589931290001,11.43925554800006],[122.05009160800012,11.410117701000049],[122.06258706300004,11.374663725000064],[122.05820774300001,11.345064530000059],[122.05387370900007,11.335744317000037],[122.03579501700004,11.320292493000062],[122.02710348000006,11.298443717000055],[122.0305323130001,11.290619804000073],[122.05203945100004,11.261286728000073],[122.0480822600001,11.246478030000048],[122.05307044900007,11.227105542000062],[122.03396906600005,11.199127747000034],[122.03319639100005,11.190858166000055],[122.03961760100003,11.15027888900005],[122.03773811600003,11.115873330000056],[122.04557204400008,11.094415365000028],[122.04137531900005,11.071905574000025],[122.046324668,11.062138360000061],[122.05398686700005,11.03346733700005],[122.03963948900002,11.017694980000044],[122.03784987300003,10.997978692000062],[122.01452345900009,10.966859749000037],[121.99889837600004,10.952548044000023],[121.98406786200009,10.931452068000054],[121.97564074800006,10.896479147000033],[121.96366302600006,10.864099793000038],[121.95633035800007,10.850805555000022],[121.94335582300006,10.79751016700004],[121.923126367,10.76335135800002],[121.93647738000004,10.737225214000034],[121.9465109030001,10.737631638000037],[121.967641146,10.711739677000025],[121.97808132300007,10.675039620000065],[121.974769852,10.632055277000063],[121.96766481100006,10.60463510500006],[121.9644338820001,10.572512759000062],[121.95812845000012,10.551179183000043],[121.94743134600004,10.530745481000054],[121.91868134200001,10.500813728000026],[121.9218428700001,10.481320514000057],[121.9127139530001,10.44640674200002],[121.9192196360001,10.434917631000078],[121.94267594100006,10.421221346000037],[121.95997604500006,10.413809783000035],[121.98030161600002,10.422776239000028],[121.99854772600008,10.439987748000021],[122.01073719400006,10.443017514000076],[122.03028776500003,10.466848482000046],[122.01303394100013,10.476499513000023],[122.01216107800009,10.486723335000022],[122.01819370900012,10.524373494000029],[122.01584591000005,10.544761710000044],[122.02265034200002,10.559906409000064],[122.01906709400009,10.565216420000068],[122.03481262200012,10.623438966000034],[122.04721864800001,10.63156335000002],[122.05098571500004,10.647015267000029],[122.06031076300007,10.659141388000021],[122.06518785800006,10.680676879000034],[122.08405293200008,10.700210447000073],[122.09472650600004,10.699596017000035],[122.11537238300004,10.715170645000057],[122.15394495400005,10.751227345000075],[122.17497210800003,10.755996189000026],[122.19932536600005,10.816251925000074],[122.20100347600008,10.834685975000072],[122.22436151400008,10.852999279000073],[122.24428145000003,10.84951326300006],[122.25827484200009,10.860611470000038],[122.2648694290001,10.876856672000027],[122.260612679,10.895246205000033],[122.28086203700003,10.892336224000074],[122.2857364240001,10.903057545000024],[122.2829747310001,10.911117010000055],[122.29696678700007,10.925630946000066],[122.30786046400009,10.923071334000042],[122.32363979700007,10.933363292000022],[122.32419683600004,10.94167671800005],[122.31246292500009,10.958055645000059],[122.32373918400002,11.015286657000047],[122.31961925200005,11.028805747000034],[122.3084573520001,11.04731852700007],[122.23994482700006,11.133468934000064],[122.21252489900007,11.166055007000068],[122.20102923400007,11.210432844000024],[122.204942371,11.239576831000022],[122.20559152500005,11.271410649000076],[122.21064438200004,11.278133869000044],[122.20517160900012,11.288325495000036],[122.19990772800008,11.311955905000046]]],[[[121.90645864300005,11.464299284000047],[121.91713277100007,11.46347103700003],[121.92912615100012,11.473421515000041],[121.92684580100001,11.478879490000052],[121.89990339500002,11.473274127000021],[121.90645864300005,11.464299284000047]]]]},"properties":{"adm1_psgc":600000000,"adm2_psgc":600600000,"adm2_en":"Antique","geo_level":"Prov","len_crs":664764,"area_crs":2735034505,"len_km":664,"area_km2":2735},"id":600600000},
```


## `phl_msk_alt/PHL_msk_alt.grd`

**File:** `phl_msk_alt/PHL_msk_alt.grd`

**Summary:** Reference or configuration file.


## `phl_msk_alt/PHL_msk_alt.gri`

**File:** `phl_msk_alt/PHL_msk_alt.gri`

**Summary:** Reference or configuration file.


## `phl_msk_alt/PHL_msk_alt.vrt`

**File:** `phl_msk_alt/PHL_msk_alt.vrt`

**Summary:** Reference or configuration file.


## `municipality_climate_averages.csv`

**File:** `municipality_climate_averages.csv`

**Summary:** CSV data file used for lookups, reference values, or model inputs.

**Preview (first 10 rows):**
```csv
municipality_id,avg_t2m,avg_t2m_max,avg_t2m_min,avg_rh2m,avg_rhoa,avg_prectotcorr,avg_ws10m,avg_allsky_sfc_sw_dwn,avg_cloud_amt,avg_surface_pressure,elevation
4919,27.191770833333333,31.353020833333332,24.128020833333334,80.2384375,1.1485416666666666,8.010833333333332,5.891354166666667,5.248924210526316,62.880105263157894,99.75052083333333,235
4920,27.191770833333333,31.353020833333332,24.128020833333334,80.2384375,1.1485416666666666,8.010833333333332,5.891354166666667,5.248924210526316,62.880105263157894,99.75052083333333,18
4921,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.3685989473684215,59.30210526315789,98.05052083333334,13
4922,27.191770833333333,31.353020833333332,24.128020833333334,80.2384375,1.1485416666666666,8.010833333333332,5.891354166666667,5.248924210526316,62.880105263157894,99.75052083333333,10
4923,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.3685989473684215,59.30210526315789,98.05052083333334,79
4924,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,25
4925,27.191770833333333,31.353020833333332,24.128020833333334,80.2384375,1.1485416666666666,8.010833333333332,5.891354166666667,5.248924210526316,62.880105263157894,99.75052083333333,65
4926,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,132
4927,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,8
4928,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,29
4929,27.191770833333333,31.353020833333332,24.128020833333334,80.2384375,1.1485416666666666,8.010833333333332,5.891354166666667,5.248924210526316,62.880105263157894,99.75052083333333,84
4930,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,13
4931,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,59
4932,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.3685989473684215,59.30210526315789,98.05052083333334,126
4933,27.191770833333333,31.353020833333332,24.128020833333334,80.2384375,1.1485416666666666,8.010833333333332,5.891354166666667,5.248924210526316,62.880105263157894,99.75052083333333,8
4934,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,10
4935,27.191770833333333,31.353020833333332,24.128020833333334,80.2384375,1.1485416666666666,8.010833333333332,5.891354166666667,5.248924210526316,62.880105263157894,99.75052083333333,12
4936,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,39
4937,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.3685989473684215,59.30210526315789,98.05052083333334,44
4938,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,14
4939,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,19
4940,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,53
4941,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.248924210526316,62.880105263157894,98.05052083333334,30
4942,24.6765625,30.239895833333335,19.856875,80.31197916666666,1.0926041666666668,8.937708333333333,2.5132291666666666,5.185797894736842,64.92347368421052,94.21375,61
4943,24.6765625,30.239895833333335,19.856875,80.31197916666666,1.0926041666666668,8.937708333333333,2.5132291666666666,5.3685989473684215,59.30210526315789,94.21375,24
4944,26.008333333333336,32.38458333333333,21.10375,78.37656249999999,1.1151041666666668,8.149062500000001,3.177395833333333,5.3685989473684215,59.30210526315789,96.61979166666667,12
4945,26.008333333333336,32.38458333333333,21.10375,78.37656249999999,1.1151041666666668,8.149062500000001,3.177395833333333,5.3685989473684215,59.30210526315789,96.61979166666667,22
4946,26.601041666666664,32.48,22.270520833333332,78.38645833333334,1.1295833333333334,7.239895833333333,4.5615625,5.3685989473684215,59.30210526315789,98.05052083333334,16
4947,24.6765625,30.239895833333335,19.856875,80.31197916666666,1.0926041666666668,8.937708333333333,2.5132291666666666,5.3685989473684215,59.30210526315789,94.21375,7
```

