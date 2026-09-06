# LUMI Lessons Learned — EnergyHub Vercel 500s

This document captures the bugs, root causes, and prevention strategies from the
EnergyHub Vercel 500 incident so future LUMI (or any FastAPI-on-Vercel) work
can avoid repeating them.

---

## 1. Pydantic response validation errors when data is missing

**Symptom**

```text
fastapi.exceptions.ResponseValidationError
/api/v1/energyhub/ai-insight 500
/api/v1/energyhub/trends 500
```

**Root cause**

`EnergyHubML` returned `None`, `{}`, or partial dictionaries when `doe_datasets`
was empty or the local CSVs were missing. FastAPI then tried to serialize those
values into the `response_model` (e.g. `AiInsightResponse`, `ForecastResponse`,
`SourceBreakdownResponse`) and failed because required fields were absent.

For example, the original empty-data path for `get_ai_insight()` returned only
`{"insight": "No data available."}`, missing `recommendation` and `data_year`,
both of which `AiInsightResponse` requires:

```python
class AiInsightResponse(BaseModel):
    insight: str
    recommendation: str
    data_year: int
```

**Fix**

In `fastapi-backend/app/ml/predictor.py`, every public method now returns a
complete dict that satisfies its response schema, with sensible defaults for
the missing-data case:

```python
def get_ai_insight(self) -> dict[str, str]:
    if self._historical is None or self._historical.empty:
        return {
            "insight": "No data available.",
            "recommendation": "",
            "data_year": 0,
        }
    ...

def get_latest_statistics(self) -> dict[str, Any]:
    if self._historical is None or self._historical.empty:
        return {
            "year": 0,
            "total_consumption_gwh": 0.0,
            "total_peak_demand_mw": 0.0,
            "total_generation_gwh": 0.0,
            "renewable_generation_gwh": 0.0,
            "renewable_share_pct": 0.0,
            "capacity_margin_mw": None,
            "capacity_margin_pct": None,
        }
    ...

def get_forecast(self, metric: str = "consumption") -> dict[str, Any]:
    if df is None or df.empty:
        return {
            "forecast_years": [],
            "forecast_values": [],
            "ci_lower": [],
            "ci_upper": [],
            "model": "ARIMA(1,1,1)",
            "training_period": "2003-2020",
            "test_period": "2021-2024",
        }
    ...
```

**Prevention**

- Every function behind a FastAPI `response_model` must return an object that
can be parsed by that schema, even when the underlying data is empty.
- Add an explicit empty-data test for each route, not just the happy path.
- Keep a mapping between Pydantic response fields and the default service
  return values; review it whenever a schema changes.

---

## 2. IndexError on empty list access

**Symptom**

```text
IndexError: list index out of range
app/services/energyhub.py in _generate_llm_insight
```

**Root cause**

`_generate_llm_insight` tried to read the last forecast value with
`forecast_values[-1]`, but when the predictor was empty `forecast_values` was
an empty list `[]`.

```python
forecast = self._ml.get_forecast("consumption")
f_2030 = forecast["forecast_values"][-1]   # crashes if []
```

**Fix**

```python
forecast_values = forecast.get("forecast_values") or []
f_2030 = forecast_values[-1] if forecast_values else 0
consumption = latest.get("total_consumption_gwh", 0) or 0
forecast_growth = ((f_2030 / consumption) - 1) * 100 if consumption else 0.0
```

**Prevention**

- Never index directly into a list that can be empty.
- Use a ternary or helper:
  - `value = seq[-1] if seq else default`
  - `value = next(iter(reversed(seq)), default)`
  - `value = seq[-1] if isinstance(seq, list) and seq else 0`

---

## 3. Vercel `functions.<entrypoint>.excludeFiles` > 256 characters

**Symptom**

```text
Invalid request: functions.api/index.py.excludeFiles should NOT be longer than 256 characters.
```

**Root cause**

`vercel.json` duplicated many project-level ignore patterns inside the
`excludeFiles` field, which Vercel limits to 256 characters.

**Fix**

Move large directory exclusions to `.vercelignore` (which has no such limit)
and keep `vercel.json` `excludeFiles` short — only cache/build artifacts and
any fastapi paths not already covered:

```json
{
  "functions": {
    "api/index.py": {
      "excludeFiles": "{__pycache__/**,.pytest_cache/**,fastapi-backend/app/services/local_data/**,fastapi-backend/scripts/**}",
      "includeFiles": "{fastapi-backend/**,api/**,DOE_Data_Extracted/data_v2_preprocessed/**}"
    }
  }
}
```

```text
# .vercelignore — project-level ignores
/DOE_Data_Extracted/**
!/DOE_Data_Extracted/data_v2_preprocessed/
!/DOE_Data_Extracted/data_v2_preprocessed/**
/philippine_geojson/
/fastapi-backend/app/services/local_data/
/fastapi-backend/scripts/
/windsurf_data_extraction/
/lumi_tests/
/GeothermalDatasets/
/regionalData/
/lumi-details/
/docs/
/supabase/
/expo-mobile/
```

**Prevention**

- Use `.vercelignore` for all large project directories.
- Reserve `vercel.json` `excludeFiles` for a small set of files that may still
  leak into the function bundle (e.g. `__pycache__`, dev scripts).
- Validate the length of `excludeFiles` before pushing (`len(json["..."]) < 256`).

---

## 4. Static data not bundled with the Vercel function

**Symptom**

Endpoints returned `year: 0`, empty arrays, and empty dicts on Vercel because
`EnergyHubML` could not find the DOE CSVs.

**Root cause**

`.vercelignore` ignored all of `DOE_Data_Extracted/**`, and `vercel.json` did
not explicitly include the preprocessed CSVs, so the function bundle had no
local data. The Supabase `doe_datasets` table was also empty, so all data
sources failed.

**Fix**

1. Update `vercel.json` to explicitly bundle the small preprocessed CSVs:
   `DOE_Data_Extracted/data_v2_preprocessed/**`.
2. Update `.vercelignore` to unignore that exact path while keeping the raw
   `data_v1/` and `data_v2/` directories out of the bundle.
3. Make the predictor prefer the bundled CSVs on serverless by default.

**Prevention**

- If a serverless function depends on static files, those files must appear in
  both:
  - the upload allowlist (`.vercelignore` or not being ignored by `.gitignore`)
  - the function bundle include list (`vercel.json` `includeFiles`)
- Keep data versioning explicit: `data_v2_preprocessed/` vs legacy `data_v1/`.

---

## 5. Local data fallback toggle mismatch

**Symptom**

Local tests sometimes returned `year=0` while Vercel sometimes returned data,
or vice-versa, depending on whether `USE_LOCAL_DATA_FALLBACK` was set.

**Root cause**

- `predictor.py` originally read `os.getenv("USE_LOCAL_DATA_FALLBACK", "true")`
  directly, while `Settings.use_local_data_fallback` had `default=False`.
- Different environments (IDE shell, `.env`, Vercel dashboard) had different
  values for the same variable.

**Fix**

Centralize the toggle in `Settings` and consume the setting in the predictor:

```python
# fastapi-backend/app/config/settings.py
use_local_data_fallback: bool = Field(
    default=True,
    validation_alias=AliasChoices("USE_LOCAL_DATA_FALLBACK", "use_local_data_fallback"),
)
```

```python
# fastapi-backend/app/ml/predictor.py
def _load_csv(filename: str, subdir: str = "") -> pd.DataFrame | None:
    path = _DATA_DIR / subdir / filename if subdir else _DATA_DIR / filename
    settings = get_settings()

    if settings.use_local_data_fallback and path.exists():
        return pd.read_csv(path)

    df = _load_csv_from_supabase(dataset_name)
    if df is not None:
        return df

    if settings.use_local_data_fallback and path.exists():
        return pd.read_csv(path)
    return None
```

**Prevention**

- Pydantic settings should default to the production behavior you want.
- If the production deployment uses bundled files, default the toggle to `True`.
- If you set it to `False`, the Supabase table must be populated or the
  response will fall back to the empty defaults.
- Do not scatter `os.getenv` checks for the same toggle across the codebase;
  use `get_settings()` consistently.

---

## 6. Supabase `doe_datasets` table was empty

**Symptom**

With local fallback disabled, the predictor loaded nothing because
`doe_datasets` existed but had `0 rows`.

**Root cause**

The migration `supabase/migrations/0008_data_offload.sql` created the table,
but `scripts/migrate_csv_to_supabase.py` had not been run, so the CSVs were
never inserted.

**Fix**

Populate the table:

```bash
python scripts/migrate_csv_to_supabase.py
```

Or bundle the CSVs and enable `use_local_data_fallback`.

**Prevention**

- Data offloading is a two-step process: schema migration + data migration.
- After creating an offloading schema, always run the migration script and
  verify counts in the deployed database.

---

## 7. Inheriting stray environment variables during local testing

**Symptom**

`python -c` smoke tests produced different results inside the IDE terminal
because `USE_LOCAL_DATA_FALLBACK` was `false` in the parent shell even though
`settings.py` defaulted to `True`.

**Root cause**

Environment variables from the IDE or system leaked into the child process and
overrode the Pydantic settings defaults.

**Prevention**

- Use a clean shell when testing environment-sensitive code.
- In PowerShell: `Remove-Item -ErrorAction SilentlyContinue Env:\VAR`.
- In Unix: `env -i VAR=value python -c "..."`.
- Document all environment variables in the deployment guide.

---

## 8. Summary checklist for the next project

### Response model safety

- [ ] Return a schema-compatible default object for every `response_model` path.
- [ ] Test every route with an empty database / missing files.
- [ ] Keep response schema and service return defaults in sync.

### Data loading

- [ ] Decide the source of truth: bundled files, Supabase, or both.
- [ ] Default the loading toggle to the production source of truth.
- [ ] If relying on Supabase, run data migration scripts after schema migrations.

### Vercel deployment

- [ ] Keep `vercel.json` `excludeFiles` under 256 characters.
- [ ] Put large project directory ignores in `.vercelignore`.
- [ ] Explicitly bundle any static files in `vercel.json` `includeFiles`.
- [ ] Unignore bundled paths in `.vercelignore` if they live under an ignored parent.

### Python safety

- [ ] Guard every `list[-1]`, `dict["key"]`, and division by a value that may be `0`.
- [ ] Centralize feature toggles in Pydantic `Settings`, not raw `os.getenv`.

### Testing

- [ ] Run `fastapi.testclient.TestClient` against every route before redeploy.
- [ ] Test with data present and data missing.
- [ ] Test in a clean shell to avoid inherited env leakage.
