# Vercel Deployment Guide for Lumi

This guide deploys the entire Lumi stack (React frontend + FastAPI backend) to a single Vercel project.

## What runs where

- **Frontend**: `react-frontend` builds as a static Vite site served by Vercel.
- **Backend**: `api/index.py` runs as a single Vercel Python Function with the FastAPI app from `fastapi-backend/main.py`.
- **Heavy ML/RAG/ETL workloads** are optionally forwarded to a companion ML worker via the `ML_WORKER_URL` environment variable.

## What is included / excluded

The Vercel Function intentionally omits the largest packages that exceed Vercel's 500 MB function bundle size when installed:

- `sentence-transformers` (pulls `torch` / `transformers` ~500 MB)
- `faiss-cpu`
- `scikit-learn` (only used by offline `ml_classifier.py`, not by API routes)

The following remain in Vercel:

- `fastapi`, `pydantic-settings`, `supabase`, `httpx`, `redis`, `google-genai`, `groq`
- `pandas`, `numpy`, `statsmodels` (for forecasting)

RAG functionality runs with degraded context when `ML_WORKER_URL` is unset, because `sentence-transformers` and `faiss-cpu` are not present. Chat still responds using Groq/Gemini.

## Environment variables

Add all of the following in **Project → Settings → Environment Variables** in the Vercel dashboard.

### Frontend (`react-frontend`)

| Variable | Value | Notes |
|----------|-------|-------|
| `VITE_SUPABASE_URL` | `https://<project>.supabase.co` | Same as the backend `SUPABASE_URL` |
| `VITE_SUPABASE_ANON_KEY` | `<anon-key>` | Supabase anon/public key |
| `VITE_API_BASE_URL` | `/api/v1` | Same-origin API; use `https://<api-domain>/api/v1` if the API is a separate Vercel project |

### Backend (Vercel Function)

| Variable | Value | Notes |
|----------|-------|-------|
| `APP_NAME` | `Lumi API` | Optional |
| `API_V1_PREFIX` | `/api/v1` | Keep this so the FastAPI app matches the `/api/v1` rewrite |
| `CORS_ORIGINS` | `["https://<your-vercel-domain>"]` | Add preview domains if you want them to work |
| `SUPABASE_URL` | `https://<project>.supabase.co` | Required |
| `SUPABASE_ANON_KEY` | `<anon-key>` | Required |
| `SUPABASE_SERVICE_ROLE_KEY` | `<service-role-key>` | Required for admin endpoints |
| `SUPABASE_JWT_SECRET` | `<jwt-secret>` | Required for auth validation |
| `UPSTASH_REDIS_URL` | `rediss://default:...@...upstash.io:6379` | Optional; app falls back to in-memory cache |
| `GROQ_API_KEY` | `<key>` | Required for chat/AI insights |
| `GEMINI_API_KEY` | `<key>` | Optional alternative LLM |
| `ENABLE_RAG` | `false` | Required on Vercel to skip FAISS startup |
| `ML_WORKER_URL` | `https://<worker-domain>` | Optional; see below |
| `ML_WORKER_PROXY_PREFIXES` | `/api/v1/chat,/api/v1/etl` | Comma-separated prefixes to proxy |

## Deploy steps

1. Push the repository to GitHub.
2. In Vercel, create a new project and import the GitHub repository.
3. Vercel will use the root `vercel.json`:
   - `buildCommand` builds the React frontend from `react-frontend/`
   - `installCommand` installs the Vercel Python dependencies from `fastapi-backend/requirements-vercel.txt`
   - `outputDirectory` is `react-frontend/dist`
   - `/api/v1/*` is rewritten to the Python Function (`api/index.py`)
   - all other paths serve the static SPA
4. Add the environment variables above.
5. Deploy.

## Optional companion ML worker

If you want full RAG, long ETL jobs, or to run training/backtesting, deploy the existing Docker backend to a separate host (Render, Fly, Railway, DigitalOcean Apps, etc.) and set `ML_WORKER_URL` to its URL.

The Vercel Function will forward requests on the prefixes defined by `ML_WORKER_PROXY_PREFIXES` (default: `/api/v1/chat`, `/api/v1/etl`) to the worker, preserving headers and auth.

When `ML_WORKER_URL` is not set, those routes run inside the Vercel Function with graceful degradation:

- `chat` works without RAG context.
- `etl/run/climate` may time out on the 60 s Vercel limit if the dataset is large.

## Post-deploy validation

1. Open the deployed Vercel URL.
2. Visit `/api/v1/health/` -> should return `{"status":"ok"}`.
3. Visit `/api/v1/health/detailed` -> should return `ok/degraded` status for Supabase, Redis, and `not_loaded` for the RAG index.
4. Open the frontend and verify login, dashboard, and EcoSim work.
5. Test a light forecast request: `/api/v1/forecast/models`.

## Bundle-size notes

- `fastapi-backend/requirements-vercel.txt` keeps the installed size under ~350 MB.
- Large data files (`.tif`, `.pdf`, `.png`, `.ipynb`, `.xml`, `.xlsx`, `scraped_data/runtime/`, `scraped_data/drivers/`) are excluded in `vercel.json` `excludeFiles`.
- Required CSVs and GeoJSON files are included via `includeFiles`.
- The products dataset was copied to `fastapi-backend/app/services/local_data/products.csv` so it is bundled with the function.

## Troubleshooting

- **ImportError for `sentence_transformers` or `faiss`**: expected; RAG falls back. Enable `ML_WORKER_URL` for full RAG.
- **`ModuleNotFoundError: No module named 'main'`**: `api/index.py` uses `Path(__file__).resolve().parents[1]`. Verify `fastapi-backend/main.py` exists.
- **CORS errors in the browser**: set `CORS_ORIGINS` to your deployed Vercel domain and any preview domains.
- **Function timeout on forecast/ETL**: increase `maxDuration` in `vercel.json` (up to 60 s on Pro) or route the endpoint to an ML worker.
- **Missing static data**: check `vercel.json` `includeFiles` for the relevant CSV/GeoJSON files.

## Local development (unchanged)

The existing local setup continues to work:

```bash
cd fastapi-backend && uvicorn main:app --host 0.0.0.0 --port 8000
cd react-frontend && npm run dev
```

`vercel.json`, `api/index.py`, and `fastapi-backend/requirements-vercel.txt` are only used by Vercel.
