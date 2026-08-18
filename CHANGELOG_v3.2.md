# LUMI v3.2 Release Notes

> Branch: `development_working_branch`  
> Baseline: `main`  
> Release: 3.2.0

This release integrates the `lumi-fastapi-react-v4` workstream, makes the EcoSim AI stack faster and provider-agnostic, adds a new Supabase-backed climate/AI cache, refreshes the frontend UX, and gates production deployments behind manual approval.

---

## 1. Added

### 1.1 EcoSim AI & climate caching

- **Supabase migration** `supabase/migrations/0010_ecosim_climate_and_ai_cache.sql`
  - New `municipality_climate_averages` table.
  - New `ecosim_ai_cache` table for durable AI analysis results.
- **Ingestion script** `scripts/ingest_municipality_climate_averages.py`
  - Populates `municipality_climate_averages` from the bundled climate CSV.
- **AI cache layer** in `fastapi-backend/app/services/gemini_funcs.py`
  - L1 Redis cache and L2 Supabase cache for EcoSim AI analyses.
  - Cache keys and `model_version` now reflect the actual LLM provider/model being called.

### 1.2 EcoSim API capabilities

- Optional `electricity_rate` query parameter on the EcoSim dashboard endpoint, allowing the caller to override the rate derived from `monthly_bill / monthly_consumption` (`fastapi-backend/app/services/ecosim.py`, `app/routes/ecosim.py`, `app/schemas/ecosim.py`).

### 1.3 Frontend UX components

- `react-frontend/src/components/shared/BillHelpModal.jsx` — bill-reading help modal.
- `react-frontend/src/components/shared/CitationSources.jsx` — reusable citation / source display, now supporting direct source text.
- `react-frontend/src/components/shared/ExpandableBlock.jsx` — collapsible content block.
- `react-frontend/src/components/shared/InfoTooltip.jsx` and `react-frontend/src/components/ui/tooltip.jsx` — accessible tooltip primitives.
- `react-frontend/src/data/references.json` — shared reference data used by citation components.
- `react-frontend/public/MeralcoBillWithBoxes.png` — new annotated bill example image.

### 1.4 Energy Hub visualizations

- Updates to `EnergyMap.jsx`, `EnergyOverview.jsx`, `EnergyTrends.jsx`, and `ProvincialDemand.jsx` for improved energy-hub dashboards.

### 1.5 Documentation

- `docs/DEVELOPMENT_WORKFLOW.md` — branch strategy, CI/CD workflow explanation, and manual GitHub/Vercel settings.
- `docs/LESSONS_LEARNED.md` — post-mortem and fixes for EnergyHub Vercel 500 errors.
- `docs/function-reference/BACKEND.md`, `FRONTEND.md`, `GEOLOCATION.md`, `MISC.md`, `README.md`, `UPDATE_PROMPT.md` — auto-generated function reference docs.
- `DOCS_INDEX.md` reorganized, alphabetized, and linked to the new function-reference section.

### 1.6 Deployment safety

- `.github/workflows/vercel-preview.yml` — automatic Vercel preview deploys for `development` / `develop`.
- `.vercelignore` to keep the Vercel function bundle under size limits.

---

## 2. Changed

### 2.1 EcoSim AI provider

- `fastapi-backend/app/services/llm_client.py` and `app/services/gemini_funcs.py`
  - `LLM_PROVIDER` now defaults to `groq`.
  - `DEFAULT_GROQ_MODEL` now defaults to `groq/compound-mini`.
  - AI cache keys and stored `model_version` now encode the real provider and model.
- `fastapi-backend/app/services/groq_client.py`
  - Updated default and fallback models to valid Groq IDs: `groq/compound-mini`, `groq/compound`, `qwen/qwen3.6-27b`.
  - Removed forced `response_format={"type": "json_object"}` so the markdown prompt works without validation errors.
- `fastapi-backend/app/services/ecosim.py`
  - EcoSim AI error/summary messages are now provider-agnostic ("AI analysis" instead of "Gemini analysis").

### 2.2 Climate data loading

- `fastapi-backend/app/services/ecosim.py`
  - Replaced global climate DataFrame load with per-municipality and batched municipality-ID queries against `municipality_climate_averages`.
  - Climate queries now target only the rows needed instead of fetching the entire table.
  - Added elevation fallback in terrain data lookup.

### 2.3 Startup performance

- `fastapi-backend/main.py`
  - Pre-initializes Supabase and Redis sync clients on startup to avoid SSL/TLS handshake latency on the first request.

### 2.4 Frontend content and styling

- `react-frontend/src/pages/Home.jsx` — simplified hero copy and feature descriptions to focus on user-facing benefits.
- `react-frontend/src/pages/About.jsx` — refreshed about page content and layout.
- `react-frontend/src/pages/Ecosim.jsx`, `EcosimWizard.jsx`, `EcosimResults.jsx`, `EcosimInputForm.jsx` — EcoSim flow and results UX updates.
- `react-frontend/src/pages/EnergyHub.jsx`, `Navbar.jsx`, `globals.css` — navigation and global style updates.
- `react-frontend/src/i18n/en.json` and `fil.json` — new and updated localization strings for the new UI copy.

### 2.5 Dependencies and tooling

- `react-frontend/package.json` and `package-lock.json` updated:
  - Tailwind CSS v4 (`@tailwindcss/postcss`, `@tailwindcss/vite`, `tailwindcss` `^4.0.0`).
  - Vite, Vitest, Radix UI, and related build/test tooling refreshed.

---

## 3. Fixed

### 3.1 EcoSim performance

- EcoSim AI analysis now completes under the 10-second Vercel serverless limit (~7.8s first call, ~3s cache hits) by combining Groq, Redis L1 cache, and Supabase L2 cache.

### 3.2 Groq API errors

- Fixed `BadRequestError` from invalid Groq model names.
- Fixed JSON validation error by removing `response_format={"type": "json_object"}` for the markdown prompt.

### 3.3 Health endpoint redirect

- `fastapi-backend/app/routes/health.py` now registers both `/api/v1/health` and `/api/v1/health/` so live tests no longer hit a 307 Temporary Redirect.

### 3.4 Vercel function bundling

- `vercel.json` `excludeFiles` shortened to stay under the 256-character limit, preventing deployment-time bundle errors.

---

## 4. Infrastructure & CI/CD

### 4.1 Branch and deployment guard

- Renamed the active integration branch to `development`.
- `.github/workflows/vercel-deploy.yml` is now `workflow_dispatch` only, gated by `environment: production` and `main` branch.
- `.github/workflows/deploy.yml` (DigitalOcean) is also `workflow_dispatch` only with the same `environment: production` / `main` guard.
- `.github/workflows/ci.yml` triggers on `main` and `development`.

### 4.2 Vercel preview

- `.github/workflows/vercel-preview.yml` deploys a Vercel preview for every push to `development` or `develop`.

---

## 5. Removed / Cleaned

- Deleted stale raw scraped-data artifacts under `scraped_data/output/raw_data/`.
- Removed `react-frontend/node_modules/nanoid/.claude/settings.local.json` and other incidental `node_modules` noise.

---

## 6. Verification

- `python -m py_compile` passes on all changed Python files.
- `lumi_tests/tests/unit/` — **176 passed**.
- `lumi_tests/tests/integration/test_api.py -m mock` — **24 passed, 1 skipped**.
- `lumi_tests/tests/integration/test_pipeline.py` — **30 passed**.
- Live, database, and performance tests are conditional on environment variables and a running server (see `lumi_tests/README.md`).

---

## 7. Notes

- Production deploys now require a manual run of the `Vercel Production Deploy` and/or `Deploy` GitHub Actions from the `main` branch, plus an approved `production` environment reviewer.
- See `docs/DEVELOPMENT_WORKFLOW.md` for the full branching and release process.
