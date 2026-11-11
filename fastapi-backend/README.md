# LUMI FastAPI Backend

REST API powering EcoSim, EnergyHub, and the AI/RAG features of LUMI.

## Structure

```
fastapi-backend/
├── main.py                 # FastAPI app entry point (uvicorn main:app)
├── app/
│   ├── auth/               # JWT / auth helpers
│   ├── config/             # settings.py (pydantic-settings, .env loading)
│   ├── dependencies/       # FastAPI dependencies (auth, quotas)
│   ├── middleware/         # CORS, logging, rate limiting
│   ├── ml/                 # EnergyHub ML predictor (pre-computed ARIMA CSVs)
│   ├── routes/             # API routers: ecosim, energyhub, simulations, admin, ...
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Business logic
│   │   ├── geothermal/     # Geothermal feature extraction (faults, volcanoes, IHFC)
│   │   └── local_data/     # Bundled CSV/JSON fallbacks for serverless
│   └── utils/              # Helpers
├── scripts/                # One-off ingestion & verification scripts (check_*.py,
│                           # ingest_*.py, extract_*.py — run manually, not pytest)
├── tests/                  # pytest suite (77 tests)
├── requirements.txt        # Local dev dependencies
├── requirements-vercel.txt # Vercel serverless bundle (see also ../api/requirements.txt)
└── .env.example            # Backend environment template
```

## Setup

```bash
cd fastapi-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Backend config loads from the REPOSITORY-ROOT .env (settings.py resolves
# ../.env relative to this package). A fastapi-backend/.env file is ignored —
# use it only as a local template reference, not for real values.
uvicorn main:app --reload --port 8000 --no-server-header
```

## Tests

Run from this directory (the suite expects `fastapi-backend/` on `sys.path`):

```bash
cd fastapi-backend
python -m pytest tests -q       # 77 tests
```

## LLM response cache

LLM-generated text is cached durably in the Supabase `chart_ai_insights`
table via `app/services/llm_response_cache.py`. Rows are keyed by
`(chart_type, chart_data_hash)`; up to 3 variants per key are kept and a
random one is served on read (`force_refresh=true` on the API routes
bypasses the read and stores a new variant).

| `chart_type` | Key contents | Expiry |
|---|---|---|
| chart analyses (e.g. `consumption_trend`) | chart payload + `PROMPT_VERSION` | none |
| `map_explanation` | map payload + `PROMPT_VERSION` | none |
| `overview` (ai-insight `use_llm=true`) | stats/forecast/source payload + `PROMPT_VERSION` | none |
| `chat` | normalized message + retrieved-chunk text hashes + version | 7 days |

Cached text is passed through `clean_ai_output`/`strip_source_dump` on
both write and read, so legacy rows with raw `Sources:` dumps render
clean without a migration. Cache failures log a warning and fall back to
a fresh LLM call — they never break the request. Diagnose a deployed
instance with `python scripts/check_ai_cache.py` (write → read-back →
cleanup probe).

## Notes

- `scripts/check_*.py` are interactive verification harnesses (live RAG/LLM
  queries) — run them directly with `python`, they are intentionally **not**
  pytest tests and live outside `tests/` so they do not break collection.
- Runtime dataset paths resolve to `../data/...` (DOE forecasts, GeoJSON,
  geothermal datasets) and `app/services/local_data/` fallbacks.
- Deployment entry point for Vercel is `../api/index.py`; see
  `docs/05-Setup-Guides/VERCEL_DEPLOYMENT_GUIDE.md`.
