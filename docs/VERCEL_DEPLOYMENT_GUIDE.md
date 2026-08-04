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

RAG now runs directly on Vercel via Supabase `pgvector` and the free HuggingFace Inference API (`sentence-transformers/all-MiniLM-L6-v2`). You must enable the `vector` extension in Supabase and run `fastapi-backend/scripts/seed_rag_pgvector.py` once before RAG is available.

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
| `ENABLE_RAG` | `true` | Required on Vercel to enable RAG |
| `RAG_BACKEND` | `pgvector` | Use `pgvector` on Vercel; `faiss` is for local Docker |
| `EMBEDDING_PROVIDER` | `huggingface-inference` | Free by default; `openai` is optional and paid |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Must match the dimension of the stored vectors |
| `HF_TOKEN` | `<token>` | Optional; raises HuggingFace rate limits |
| `OPENAI_API_KEY` | `<key>` | Optional; only used when `EMBEDDING_PROVIDER=openai` |
| `ML_WORKER_URL` | `https://<worker-domain>` | Optional; see below |
| `ML_WORKER_PROXY_PREFIXES` | `/api/v1/chat,/api/v1/etl` | Comma-separated prefixes to proxy |

## Deploy steps

### Vercel dashboard (recommended for first deploy)

1. **Push the correct branch to GitHub.**
   The serverless RAG changes are on branch `lumi-fastapi-react-v2.3`.
   Either import that branch directly in Vercel, or merge it into `main` first:

   ```bash
   git checkout main
   git merge lumi-fastapi-react-v2.3
   git push origin main
   ```

2. **Create a new project and import the GitHub repository.**
   In the Vercel dashboard:
   - Click **Add New... → Project**.
   - Choose **Alexander040105/Lumi**.
   - Select the branch that contains the latest RAG code (`lumi-fastapi-react-v2.3` or `main` after merging).

3. **Configure the build settings.**
   Vercel will pre-fill the values from `vercel.json`. Verify them against this screenshot:

   - **Project Name:** `lumi` (or any name)
   - **Framework Preset / Application Preset:** `FastAPI` is fine — `vercel.json` overrides it with `"framework": null` so the build is driven by the explicit commands. If you see an `Other` or `Vite` option you can select that, but `FastAPI` will not break the deploy.
   - **Root Directory:** `./`
   - **Build Command:** `cd react-frontend && npm run build`
   - **Output Directory:** `react-frontend/dist`
   - **Install Command:** `cd react-frontend && npm ci && cd .. && pip install --break-system-packages -r fastapi-backend/requirements-vercel.txt`

4. **Add the environment variables.**
   Go to **Project → Settings → Environment Variables** and add every variable from the "Environment variables" section above.

5. **Deploy.**
   Click **Deploy**. The first build will:
   - Install the frontend (`react-frontend`) dependencies and build the Vite SPA.
   - Install the backend dependencies from `fastapi-backend/requirements-vercel.txt`.
   - Package `api/index.py` as a Python serverless function.

6. **Verify.**
   After the deploy completes, open the production URL and test:

   - `https://<your-domain>/api/v1/health/detailed` → should show `rag_index: ok`.
   - `https://<your-domain>/api/v1/health/` → should return `{"status":"ok"}`.
   - Open the frontend and test login + a chat query.

### GitHub Actions

A workflow is provided at `.github/workflows/vercel-deploy.yml`. To use it, add these repository secrets in **Settings → Secrets and variables → Actions**:

- `VERCEL_TOKEN` — from your Vercel account settings
- `VERCEL_ORG_ID` — from `vercel whoami` or your Vercel dashboard URL
- `VERCEL_PROJECT_ID` — from the Vercel project settings

Once configured, pushing to `main` will automatically build and deploy to Vercel.

## Optional companion ML worker

If you want full RAG, long ETL jobs, or to run training/backtesting, deploy the existing Docker backend to a separate host (Render, Fly, Railway, DigitalOcean Apps, etc.) and set `ML_WORKER_URL` to its URL.

The Vercel Function will forward requests on the prefixes defined by `ML_WORKER_PROXY_PREFIXES` (default: `/api/v1/chat`, `/api/v1/etl`) to the worker, preserving headers and auth.

When `ML_WORKER_URL` is not set, those routes run inside the Vercel Function with graceful degradation:

- `chat` works without RAG context.
- `etl/run/climate` may time out on the 60 s Vercel limit if the dataset is large.

## Post-deploy validation

1. Open the deployed Vercel URL.
2. Visit `/api/v1/health/` -> should return `{"status":"ok"}`.
3. Visit `/api/v1/health/detailed` -> should return `ok/degraded` status for Supabase and Redis. `rag_index` is `ok` after seeding and `not_loaded` before.
4. Open the frontend and verify login, dashboard, and EcoSim work.
5. Test a light forecast request: `/api/v1/forecast/models`.

## Bundle-size notes

- `fastapi-backend/requirements-vercel.txt` keeps the installed size under ~350 MB.
- Large data files (`.tif`, `.pdf`, `.png`, `.ipynb`, `.xml`, `.xlsx`, `scraped_data/runtime/`, `scraped_data/drivers/`) are excluded in `vercel.json` `excludeFiles`.
- Required CSVs and GeoJSON files are included via `includeFiles`.
- The products dataset was copied to `fastapi-backend/app/services/local_data/products.csv` so it is bundled with the function.

## Troubleshooting

- **RAG returns `not_loaded` or empty context**: make sure the Supabase `vector` extension is enabled and `fastapi-backend/scripts/seed_rag_pgvector.py` has been run.
- **ImportError for `sentence_transformers` or `faiss`**: expected on Vercel; the pgvector path does not use these packages.
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
