# LUMI Test Suite Results Report

**Date:** June 20, 2026
**Command:** `pytest lumi_tests/tests/ -v`
**Environment:** Python 3.13, Windows

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tests Collected | 248 |
| Passed | 212 |
| Failed | 6 |
| Errors | 30 |
| Warnings | 4 |
| Duration | ~26 seconds |

**Pass Rate (excluding env-dependent errors):** 212 / 218 = **97.2%**

---

## Test Breakdown by Module

### 1. Unit Tests

#### `test_renewable_calculations.py` (17 tests)
- **Status:** 15 passed, 2 failed
- **Coverage:** Solar temperature factor, dust loss, performance ratio, `solar_calc`, wind output (Betz limit, cubic scaling), hydro runoff, flow rate, hydropower, `_calculate_option_summary`

#### `test_geothermal_calculations.py` (56 tests) — NEW
- **Status:** 56 passed, 0 failed
- **Coverage:**
  - Haversine distance formula (same point, known distance, symmetry, positivity)
  - `_normalize` helper (midpoint, bounds, clamping, None handling, divide-by-zero)
  - Fault distance (nearest fault, empty dataset)
  - Fault density (typical, zero/negative area, None area)
  - Volcano distance (nearest volcano, empty dataset)
  - Heat flow score (normalization 40–120 mW/m² range, clamping)
  - Geothermal gradient (`G = q/k`, zero/negative conductivity rejection)
  - Reservoir temperature (`T_res = T_surf + G × depth`, default depth)
  - Aquifer score (weighted composite: permeability 0.5, porosity 0.3, thickness 0.2)
  - Flow rate estimation (10–500 kg/s range, base case ~10 kg/s)
  - `compute_geothermal_suitability` (full integration with mocked datasets, classification: High/Good/Moderate/Low, missing surface temp, fault density)
  - `compute_geothermal_output` (binary vs flash plant efficiency, missing data handling, fallback temperature 27°C, zero delta-T flooring, annual energy GWh calculation, confidence scoring)

#### `test_ml_preprocessing.py`
- **Status:** All passed
- **Coverage:** Missing-value imputation, year conversion, time-feature creation, train-test split, linear trend forecast, MAPE calculation

#### `test_ai_service.py`
- **Status:** All passed
- **Coverage:** Prompt construction, JSON parsing, schema validation, cosine similarity, chunk filtering, error handling

### 2. Integration Tests

#### `test_api.py`
- **Status:** 16 passed, 3 failed
- **Passed:** EcoSim GET, overview, trends, map data, source/grid breakdown, JWT auth (valid, expired, malformed), protected endpoint 401, OAuth callback, invalid forecast metric
- **Failed:**
  - `test_health_check_live` — Health endpoint returns 307 (Temporary Redirect) instead of 200
  - `test_forecast_metric_param` — `KeyError: 'year'` in predictor (missing DataFrame column)
  - `test_post_ecosim_invalid_municipality` — Supabase API error PGRST116 (0 rows returned, cannot coerce to single JSON object)

#### `test_database.py`
- **Status:** 0 passed, 30 errors
- **Root Cause:** `TEST_DATABASE_URL` or `DATABASE_URL` environment variable not set. All 30 tests fail at the `db_conn` fixture setup stage before any test logic executes.
- **Tests affected:** Schema existence, CRUD operations (regions, provinces, municipalities, climate, hydropower), foreign key integrity, regional lookup view, null constraints, data types

#### `performance_test.py`
- **Status:** 13 passed, 1 failed
- **Passed:** DOE CSV loading, large CSV loading, linear regression inference, preprocessing pipeline, EnergyHub overview response, EcoSim response, province aggregation, renewable potential computation, FAISS search, chunk filtering, DataFrame memory, FAISS index memory
- **Failed:** `test_health_endpoint_response_time` — Health endpoint returns 307 instead of 200

#### `test_pipeline.py`
- **Status:** All passed
- **Coverage:** End-to-end data pipeline validation

### 3. Frontend Tests

#### `DashboardChart.test.jsx`
- **Status:** Not executed (requires Vitest/Jest; run separately via `npm test` in `react-frontend/`)
- **Coverage:** Chart rendering (FE-001), AI chat input validation (FE-004)

---

## Failure Details

### Failures Requiring Code Fixes

| Test | File | Error | Root Cause |
|------|------|-------|------------|
| `test_solar_scenario` | `test_renewable_calculations.py` | `assert 30.4 <= 1.0` | `_calculate_option_summary` returns `suitability_score` > 1.0; test expects 0–1 normalized score |
| `test_wind_scale` | `test_renewable_calculations.py` | `assert 24.3 <= 1.0` | Same as above — wind scenario also yields score > 1.0 |
| `test_forecast_metric_param` | `test_api.py` | `KeyError: 'year'` | ML predictor DataFrame missing `"year"` column; likely a data loading or preprocessing issue |
| `test_post_ecosim_invalid_municipality` | `test_api.py` | `APIError: PGRST116` | Supabase query returns 0 rows for invalid municipality; `execute()` raises when expecting single object |

### Failures Requiring Environment Configuration

| Test | File | Error | Fix |
|------|------|-------|-----|
| `test_health_check_live` | `test_api.py` | 307 Temporary Redirect | Health endpoint may redirect; test client needs `follow_redirects=True` or endpoint path needs trailing slash fix |
| `test_health_endpoint_response_time` | `performance_test.py` | 307 Temporary Redirect | Same root cause as above |
| All `test_database.py` tests | `test_database.py` | `RuntimeError: TEST_DATABASE_URL or DATABASE_URL required` | Export database connection string: `set TEST_DATABASE_URL=postgresql://...` |

---

## Recommendations

1. **Fix `_calculate_option_summary` scoring:** Either normalize `suitability_score` to 0–1, or update test assertions to match the actual formula output.
2. **Fix health endpoint tests:** Update test client requests to `follow_redirects=True`, or configure the FastAPI health endpoint to not redirect.
3. **Fix forecast endpoint:** Ensure the DOE dataset preprocessing pipeline creates the `"year"` column before the ML predictor accesses it.
4. **Fix EcoSim POST for invalid municipality:** Add error handling in `ecosim.py` to catch Supabase empty-result errors and return a 404 with a clear message.
5. **Enable database tests:** Set the `TEST_DATABASE_URL` or `DATABASE_URL` environment variable pointing to the LUMI PostgreSQL/Supabase instance.
6. **Run frontend tests:** Execute `cd react-frontend && npm test` to generate Vitest coverage for FE-001 and FE-004.

---

## Test File Inventory

| File | Tests | Passed | Failed | Errors |
|------|-------|--------|--------|--------|
| `tests/unit/test_renewable_calculations.py` | 17 | 15 | 2 | 0 |
| `tests/unit/test_geothermal_calculations.py` | 56 | 56 | 0 | 0 |
| `tests/unit/test_ml_preprocessing.py` | — | All | 0 | 0 |
| `tests/unit/test_ai_service.py` | — | All | 0 | 0 |
| `tests/integration/test_api.py` | 19 | 16 | 3 | 0 |
| `tests/integration/performance_test.py` | 14 | 13 | 1 | 0 |
| `tests/integration/test_database.py` | 30 | 0 | 0 | 30 |
| `tests/integration/test_pipeline.py` | — | All | 0 | 0 |

---

*Report generated automatically by pytest test runner.*
