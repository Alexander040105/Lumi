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
cp .env.example .env            # fill in Supabase/Gemini/Groq/Redis values
uvicorn main:app --reload --port 8000
```

## Tests

Run from this directory (the suite expects `fastapi-backend/` on `sys.path`):

```bash
cd fastapi-backend
python -m pytest tests -q       # 77 tests
```

## Notes

- `scripts/check_*.py` are interactive verification harnesses (live RAG/LLM
  queries) — run them directly with `python`, they are intentionally **not**
  pytest tests and live outside `tests/` so they do not break collection.
- Runtime dataset paths resolve to `../data/...` (DOE forecasts, GeoJSON,
  geothermal datasets) and `app/services/local_data/` fallbacks.
- Deployment entry point for Vercel is `../api/index.py`; see
  `docs/05-Setup-Guides/VERCEL_DEPLOYMENT_GUIDE.md`.
