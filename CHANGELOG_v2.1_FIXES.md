# LUMI v2.1 Bug Fixes & Security Improvements

> Session: 2026-07-08
> Branch: `lumi-fastapi-react-v2.1-defenseRevisions`
> Scope: Backend (FastAPI), Frontend (React), Data Preprocessing, SQL Schema

---

## 1. Critical Backend Fixes

### 1.1 ML Predictor (`app/ml/predictor.py`)

**Regex Injection Fix**
- **Line 350:** Added `regex=False` to `str.contains()` in `get_solar_atlas()`.
- **Problem:** `location.lower()` could contain regex metacharacters (e.g., `(`, `)`, `[`), causing a `re.error` crash.
- **Fix:**
  ```python
  df = df[df["location"].str.lower().str.contains(location.lower(), regex=False)]
  ```

**Unsorted DataFrame Assumption**
- **Line 372-374:** Added `sort_values("year")` before `iloc[-1]` in `get_meralco_rate()`.
- **Problem:** `df.iloc[-1]` assumed the DataFrame was sorted by year; unsorted data could return an incorrect (non-latest) row.
- **Fix:**
  ```python
  df = df.sort_values("year", ascending=True)
  row = df.iloc[-1]
  ```

### 1.2 Supabase Service (`app/services/supabase_service.py`)

**Resource Leak (httpx.Client)**
- **Line 83-87:** Added `__del__` destructor to close the `httpx.Client`.
- **Problem:** Client was created per `SupabaseRestClient` instance but never explicitly closed, causing socket/connection pool exhaustion.
- **Fix:**
  ```python
  def __del__(self):
      try:
          self.http.close()
      except Exception:
          pass
  ```

**URL Encoding in REST Filters**
- **Line 29-40:** Added `urllib.parse.quote` inside `.eq()`.
- **Problem:** Special characters (spaces, `&`, `=`) in filter values broke the Supabase REST query string.
- **Fix:**
  ```python
  def eq(self, column: str, value: str) -> "SupabaseRestQuery":
      self._filters.append((column, urllib.parse.quote(str(value), safe="")))
      return self
  ```

### 1.3 Product Service (`app/services/products.py`)

**Thread-Safe Lazy Loading**
- **Line 13-44:** Wrapped `_products_df` initialization with `threading.Lock()`.
- **Problem:** Concurrent requests could trigger multiple CSV loads or race conditions.
- **Fix:**
  ```python
  _products_lock = threading.Lock()
  def _load_products() -> pd.DataFrame:
      global _products_df
      with _products_lock:
          if _products_df is None:
              # load CSV...
  ```

**Currency-Agnostic Sorting**
- **Line 88-114:** Normalized prices to PHP before sorting.
- **Problem:** `sort_values("price_value")` mixed currencies (PHP, USD, EUR), producing nonsensical rankings.
- **Fix:** Added a temporary `price_in_php` column, sorted on it, then dropped it.

**Overly Aggressive Category Fixing**
- **Line 44-69:** Restricted `_fix_category` to exact filename suffixes.
- **Problem:** Substring matching caused false positives (e.g., any file with "solar" anywhere in the path forced category = solar).
- **Fix:** Check `source_file` basename for exact suffixes (`_solar.csv`, `_wind.csv`, etc.).

### 1.4 RAG Pipeline (`app/services/rag_pipeline.py`)

**None Guard on `_chunks`**
- **Line 365-387:** Added guard conditions in `sample_chunks()` and `index_stats()`.
- **Problem:** Calling these helpers before the index was built caused `TypeError: 'NoneType' object is not subscriptable`.
- **Fix:**
  ```python
  def sample_chunks(n: int = 3) -> list[dict[str, Any]]:
      if _chunks is None:
          return []
      return _chunks[:n]
  ```
  ```python
  def index_stats() -> dict[str, Any]:
      return {
          "chunks_loaded": len(_chunks) if _chunks is not None else 0,
          ...
      }
  ```

### 1.5 Wind Output Calculator (`app/services/wind_output_calc.py`)

**Removed Production Print Statement**
- **Line 53:** Removed `print()` at module level.
- **Problem:** Unconditional `print()` executed on every module import polluted stdout/logs.
- **Fix:** Deleted the `print()` line.

### 1.6 Settings (`app/config/settings.py`)

**Replaced Print with Logging**
- **Line 1-24, 40-52:** Replaced `print()` with `logger.info()` for `.env` loading feedback.
- **Problem:** `print()` bypasses the logging framework and makes log aggregation inconsistent.
- **Fix:**
  ```python
  logger.info("Settings loaded successfully from %s", env_file)
  ```

### 1.7 Chat Route (`app/routes/chat.py`)

**Groq Client Singleton**
- **Line 56-78:** Reused `_get_groq_client()` singleton instead of instantiating a new `Groq(...)` on every request.
- **Problem:** Creating a new client per message wasted connections and slowed responses.
- **Fix:**
  ```python
  from app.services.groq_client import _get_groq_client
  client = _get_groq_client()
  ```

### 1.8 Main App (`main.py`)

**Restricted CORS**
- **Line 11-17:** Narrowed `allow_methods` and `allow_headers` from `"*"` to explicit lists.
- **Problem:** Wildcard CORS is a security risk in production.
- **Fix:**
  ```python
  allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
  ```

---

## 2. High-Priority Logic Fixes

### 2.1 EcoSim Service (`app/services/ecosim.py`)

**Municipality-Level Meralco Franchise Check**
- **Line 258-278:** Replaced coarse province-level check with a municipality whitelist + province fallback.
- **Problem:** Previous implementation matched any municipality in a province, which is too broad for franchise boundaries.
- **Fix:**
  ```python
  meralco_franchise_municipalities = {"caloocan", "malabon", ...}
  meralco_franchise_provinces = {"metro manila", "cavite", ...}
  if muni_name in meralco_franchise_municipalities or any(p in prov_name for p in meralco_franchise_provinces):
      # fetch Meralco rate
  ```

**NameError Risk in Meralco Lookup**
- **Line 1054-1115:** Re-initialized `client = get_supabase_client()` inside the `try` block.
- **Problem:** If `client` was undefined from a prior scope failure, the `except` block would raise a secondary `NameError`.
- **Fix:** Moved client creation inside the guarded block.

**Removed Magic-Number Slice**
- Deleted `municipality_ids[:500]` hard cap in the `.in_()` query.
- **Problem:** Arbitrary 500-row truncation silently dropped valid municipalities from large provinces.
- **Fix:** Pass the full `municipality_ids` list to the query.

### 2.2 Data Preprocessing (`DOE_Data_Extracted/data_v2_preprocessing.py`)

**Removed Duplicate Year Column Hack**
- **Line 342-359:** Removed `parts.insert(34, "year")` and the associated CSV header rewrite.
- **Problem:** Hardcoded column insertion created a duplicate `year` column, corrupting downstream CSV consumers.
- **Fix:** Relied on the actual schema rather than injecting a second `year`.

**Relabeled Synthetic Model Metrics**
- **Line 395-416:** Added a `note` field to placeholder SARIMAX and Random Forest results.
- **Problem:** Synthetic metrics were indistinguishable from real model outputs, misleading consumers.
- **Fix:**
  ```python
  for p in placeholder_models:
      p["note"] = "placeholder — model not executed"
  ```

### 2.3 EnergyHub Province Mapping (`app/services/energyhub.py`)

**Typo & Missing Mappings**
- **Line 997-1033:**
  - Fixed leading space in `" compostela valley"` → `"compostela valley"`.
  - Corrected Siargao region code: `VII` → `XIII`.
  - Added missing `"davao de oro": "XI"` mapping.
- **Problem:** These caused wrong region codes in charts and API responses.

### 2.4 EnergyHub Schema (`app/schemas/energyhub.py`)

**Added Missing `note` Field**
- **Line 130-134:** Added `note: str = ""` to `MunicipalDemandResponse`.
- **Problem:** The schema dropped the `note` field present in the service layer, causing data loss in JSON serialization.
- **Fix:**
  ```python
  class MunicipalDemandResponse(BaseModel):
      items: list[MunicipalDemandEstimate]
      province: str | None = None
      note: str = ""
  ```

---

## 3. Security & Quality Improvements

### 3.1 Removed Redundant `load_dotenv()` Calls

| File | Reason |
|---|---|
| `app/services/gemini_funcs.py` | `settings.py` already loads `.env` once at startup; redundant calls clutter imports and can override environment state. |
| `app/services/groq_client.py` | Same as above. |
| `app/services/llm_client.py` | Same as above. |

### 3.2 Auth Dependency (`app/dependencies/auth.py`)

**Documented Safe Fallback**
- **Line 101-105:** Added explicit comment on `_get_user_role()` fallback behavior.
- **Problem:** Silent fallback to `"user"` on DB failure could mask outages.
- **Fix:** Log at `ERROR` level and document that the behavior fails safely (no privilege escalation), though legitimate admins will be denied during outages.
  ```python
  except Exception as exc:
      # NOTE: Returning "user" on DB failure fails safely (no privilege escalation),
      # but legitimate admins will be denied access during outages.
      logger.error("_get_user_role DB failure for user_id=%s: %s", user_id, exc)
      return "user"
  ```

### 3.3 Admin Routes (`app/routes/admin.py`)

**Logged Swallowed Exceptions**
- Replaced all `except Exception: pass` blocks with `logger.warning(...)` calls.
- **Locations:**
  - `_log_admin_action()` — audit log insert failures
  - `list_users()` — user enrichment loop failures
  - `create_user()` — profile/role upsert failures
  - `get_user()` — auth metadata fetch failures
  - `update_config()` — config upsert failures
- **Problem:** Silent swallowing made production debugging impossible.

### 3.4 Simulation Routes (`app/routes/simulations.py`)

**Added Logging & Fixed Silent Exception**
- **Line 1-11:** Added `import logging` and `logger = logging.getLogger(__name__)`.
- **Line 33-34:** Replaced `except Exception: pass` with `logger.warning(...)` in `_get_free_sim_limit()`.
- **Problem:** Same silent-failure anti-pattern as admin routes.

### 3.5 Redis Client (`app/services/redis_client.py`)

**Cached Connection Pools**
- **Line 13-30:** Added module-level `_redis_async` and `_redis_sync` globals with lazy initialization.
- **Problem:** `get_redis()` and `get_redis_sync()` created a brand-new connection pool on every call, causing connection exhaustion under load.
- **Fix:**
  ```python
  _redis_async: Redis | None = None
  _redis_sync: redis_sync.Redis | None = None

  def get_redis() -> Redis:
      global _redis_async
      if _redis_async is None:
          redis_url = os.getenv("UPSTASH_REDIS_URL")
          _redis_async = Redis.from_url(redis_url, decode_responses=True)
      return _redis_async
  ```

### 3.6 SQL Schema (`supabase_tables_scripts/municipal_population.sql`)

**Unique Constraint**
- **Line 25-28:** Added `uq_municipal_population_unique`.
- **Problem:** Duplicate census rows for the same municipality and year could be inserted, skewing population-weighted demand calculations.
- **Fix:**
  ```sql
  alter table public.municipal_population
    add constraint if not exists uq_municipal_population_unique
    unique (province_id, municipality_id, year);
  ```

---

## 4. Frontend Fixes

### 4.1 EnergyHub Page (`react-frontend/src/pages/EnergyHub.jsx`)

**IRENA Capacity Filter Typo**
- **Line 253-276:** Fixed grid connection string from `"OnGrid"` to `"On-grid"`.
- **Problem:** The IRENA data uses hyphenated `"On-grid"`; the typo caused the capacity display to show `"—"` (missing data) even when data existed.

**Falsy-Value Bug in Renewable Share**
- **Line 277:** Changed `||` to `??` for `renewable_share_pct`.
- **Problem:** `0 || "—"` evaluates to `"—"`, hiding legitimate zero-percent values.
- **Fix:**
  ```jsx
  {irena.renewable_share?.pop()?.renewable_share_pct ?? "—"}%
  ```

### 4.2 ProvincialDemand Component (`react-frontend/src/components/energyhub/ProvincialDemand.jsx`)

**Double Unit Division**
- **Line 108:** Removed extra `/ 1000` in `<YAxis tickFormatter>`.
- **Problem:** Data was already converted from MWh → GWh (`value_mwh / 1000`), and the tick formatter divided again, producing TWh-scale labels incorrectly.
- **Fix:**
  ```jsx
  <YAxis tickFormatter={(v) => `${v.toFixed(0)}`} />
  ```

**Unsorted Regions**
- **Line 81:** Added `.sort((a, b) => a.localeCompare(b))` to the regions array.
- **Problem:** `Set` iteration order is unstable, causing chart bars to jump between renders.
- **Fix:**
  ```js
  const regions = [...new Set(items.map((i) => i.region))].sort((a, b) => a.localeCompare(b));
  ```

### 4.3 EcoSim Page (`react-frontend/src/pages/Ecosim.jsx`)

**Unstable React Keys**
- **Line 930:** Replaced `key={idx}` with `key={item.url || item.product_name}`.
- **Problem:** Array index keys cause unnecessary re-renders and DOM reconciliation bugs when the list order changes.
- **Fix:**
  ```jsx
  {productRecs.items.map((item) => (
    <a key={item.url || item.product_name} href={item.url} ...>
  ```

---

## 5. Files Modified

| # | File | Lines Changed | Category |
|---|---|---|---|
| 1 | `app/ml/predictor.py` | 350-355, 372-374 | Critical |
| 2 | `app/services/supabase_service.py` | 3-13, 29-40, 73-98 | Critical |
| 3 | `app/services/products.py` | 13-44, 44-69, 88-114 | Critical |
| 4 | `app/services/rag_pipeline.py` | 365-387 | Critical |
| 5 | `app/services/wind_output_calc.py` | 53 | Critical |
| 6 | `app/config/settings.py` | 1-24, 40-52 | Critical |
| 7 | `app/routes/chat.py` | 56-78 | Critical |
| 8 | `main.py` | 11-17 | Critical |
| 9 | `app/services/ecosim.py` | 258-278, 953-964, 1054-1115 | High |
| 10 | `DOE_Data_Extracted/data_v2_preprocessing.py` | 342-359, 395-416 | High |
| 11 | `app/services/energyhub.py` | 997-1033 | High |
| 12 | `app/schemas/energyhub.py` | 130-134 | High |
| 13 | `app/services/gemini_funcs.py` | 1-20 | Security |
| 14 | `app/services/groq_client.py` | 13-24 | Security |
| 15 | `app/services/llm_client.py` | 16-27 | Security |
| 16 | `app/dependencies/auth.py` | 101-105 | Security |
| 17 | `app/routes/admin.py` | 24-35, 96-107, 173-190, 228-234, 477-488 | Security |
| 18 | `app/routes/simulations.py` | 1-11, 33-34 | Security |
| 19 | `app/services/redis_client.py` | 11-30 | Security |
| 20 | `supabase_tables_scripts/municipal_population.sql` | 25-28 | Data Integrity |
| 21 | `react-frontend/src/pages/EnergyHub.jsx` | 253-276, 277 | Frontend |
| 22 | `react-frontend/src/components/energyhub/ProvincialDemand.jsx` | 80-114 | Frontend |
| 23 | `react-frontend/src/pages/Ecosim.jsx` | 925-944 | Frontend |

---

## 6. Verification Results

All 29 targeted code-quality checks passed:
- `predictor.py`: `regex=False` present, year sort before `iloc[-1]`
- `main.py`: CORS methods/headers restricted
- `settings.py`: no `print()` statements
- `wind_output_calc.py`: no `print()` statements
- `gemini_funcs.py`, `groq_client.py`, `llm_client.py`: no `load_dotenv()`
- `products.py`: `threading.Lock()` present
- `rag_pipeline.py`: `_chunks is None` guard present
- `supabase_service.py`: `__del__` and `urllib.parse.quote` present
- `redis_client.py`: connection pool cache globals present
- `MunicipalDemandResponse`: `note` field present
- `energyhub.py`: Siargao → XIII, compostela valley no leading space, davao de oro → XI
- `ecosim.py`: municipality whitelist present, `[:500]` removed
- `data_v2_preprocessing.py`: duplicate year hack removed, placeholder labels present
- `EnergyHub.jsx`: `"On-grid"` used, `??` operator present
- `ProvincialDemand.jsx`: extra `/1000` removed, `.sort()` present
- `Ecosim.jsx`: stable `key={item.url || item.product_name}` present
- `auth.py`: safe-fallback comment present
- `admin.py`: all `logger.warning(...)` calls present
- `simulations.py`: `logger.warning(...)` present
- `municipal_population.sql`: unique constraint present

---

*End of changelog.*
