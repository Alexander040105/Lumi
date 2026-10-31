# 03 — System Design Audit

> **Purpose:** the "how and why" deep-dive. If the panel asks *"why did you build it this way?"*
> this file is the answer book. Every decision cites code comments, docs, or git history;
> unrecorded reasoning is marked `*(inferred)*`. Audited at `main @ 438789c` (2026-10-30).
>
> **Code logic:** per-file function-level walkthroughs live in `02` Part D +
> [`06a`](./06a-CODE-BREAKDOWNS-BACKEND.md)/[`06b`](./06b-CODE-BREAKDOWNS-ETL-SCRIPTS.md)/
> [`06c`](./06c-CODE-BREAKDOWNS-FRONTEND.md)/[`06d`](./06d-CODE-BREAKDOWNS-TESTS.md).

---

## 1. System at a glance

```
┌─────────────────────────────────────────────────────────────────┐
│  CLIENT (Vercel: lumi-frontend-xi.vercel.app)                     │
│  React 19 + Vite · Tailwind 4 · shadcn-style ui/* · Leaflet maps  │
│  Plotly charts · i18n en/fil · pdfmake export · Supabase JS (anon)│
└──────┬──────────────────────────────────────────────────────────┘
       │ HTTPS /api/v1/* (30s timeout, 3 retries, no-retry-429)
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  API (Vercel serverless: lumi-backend-ten.vercel.app)             │
│  FastAPI · api/index.py → main.py                                 │
│  Middleware (outer→inner): Timing → CORS → BodyLimit →            │
│    SecurityHeaders → RateLimit → RequestID → router               │
│  routes/* (thin) → services/* (fat) → Supabase / Redis / LLM      │
└──────┬──────────────┬──────────────┬──────────────┬──────────────┘
       ▼              ▼              ▼              ▼
   Supabase      Upstash Redis    LLM providers   Bundled CSV/
   Postgres+Auth (+pgvector,     (cache, quota,   Groq→(Gemini)   JSON fallbacks
   GoTrue, RLS)   rate limiter)   RAG retrieval   (local_data/)
```

**Three features over one data spine:** EnergyHub (national/provincial stats + maps + forecasts),
EcoSim (household what-if simulation), AI explanations (RAG + LLM) — all reading the same
municipality-level dataset assembled by offline ETL.

## 2. Request lifecycle (one request, end to end)

1. `TimingMiddleware` starts the clock (outermost — added last, `main.py:90-91`).
2. `CORSMiddleware` — explicit `CORS_ORIGINS` + regex for Vercel previews
   (`lumi-frontend-*-xi.vercel.app`); localhost ports allowed **only** when
   `ENVIRONMENT != production` (`main.py:67-88`). *Why: preview deploys must work but production
   can't trust arbitrary localhost.*
3. `BodySizeLimitMiddleware` — 1 MB cap → 413.
4. `SecurityHeadersMiddleware` — CSP/HSTS/etc.
5. `RateLimitMiddleware` — 60 req/min sliding window; **Redis shared counter when available,
   per-process memory fallback** (see Limitations §9).
6. `RequestIDMiddleware` — `X-Request-ID` on every response + structured JSON logging.
7. Router → dependency layer (`auth`, `quota`) → service layer → data/LLM.
8. Global `except Exception` handler returns sanitized 500 `{detail, request_id}` — never leaks
   internals (`main.py:30-56`).

## 3. Deployment topology

| Piece | Runs where | Config |
|---|---|---|
| Frontend | Vercel static/SPA | `react-frontend/` (Vite build) |
| Backend | Vercel serverless function | `api/index.py` ASGI wrapper → `main:app`; `api/requirements.txt` = slim dep set |
| Database+Auth | Supabase | Postgres + GoTrue + RLS + pgvector |
| Cache/quota | Upstash Redis | `redis_client.py` with `NullRedis` no-op fallback |
| Optional heavy worker | Docker (`docker-compose*.yml`) | `ml_worker_proxy.py` forwards heavy/RAG paths when `ML_WORKER_URL` set |
| Local dev | `npm run dev` | Vite + uvicorn concurrently (root `package.json`) |

**Why two Vercel deps sets:** `requirements-vercel.txt` omits heavy ML/geo libs; code guards the
seams with lazy imports (e.g., `gemini_funcs.py` lazy-imports `google.genai`; `rag_pipeline` only
builds FAISS when `RAG_BACKEND=faiss`, `main.py:126-134`).

## 4. Decision log — why each major choice

| # | Decision | Evidence of "why" |
|---|---|---|
| D1 | **FastAPI** backend | Pydantic boundary validation + auto OpenAPI; docstring in `schemas/common.py`: "reject bad enum values at the boundary with standard 422." *(inferred: team Python fluency + DS/ML ecosystem)* |
| D2 | **React + Vite** frontend | Ecosystem + fast dev loop; `npm run dev` runs both tiers; commit `3849489` documents forcing IPv4 for dev parity. |
| D3 | **Supabase** (Postgres+Auth+RLS) | Managed auth + hosted Postgres + RLS in one free tier; migrations 0001-0025 show schema-first development. Replaces custom auth/JWT store + self-hosted DB. |
| D4 | **Upstash Redis** for cache/quota/rate-limit | Serverless-compatible REST Redis; `data_cache.py` gzips+base64s payloads — docstring cites Upstash free-tier size limits. `NullRedis` keeps app functional when Redis absent. |
| D5 | **Weighted MCDM (AHP weights + weighted sum + PROMETHEE II)** | `mcda.py` docstring: "AHP weight validation and PROMETHEE ranking." Expert-validated weights (82.22% agreement, S9) — defensible because experts can inspect/justify each weight, unlike a black-box model. *(inferred for the "defensible" rationale)* |
| D6 | **ARIMA(1,1,1)** for demand forecasting | `ml/aic_grid.csv` + `ml/model_metrics_consumption.csv` document the AIC order search; pilot script `tests/pilot_run/evaluate_models.py` compared ARIMA vs Linear/Holt/RF. Chosen order reported as MAPE 5.67% (S18). |
| D7 | **Dual RAG backends** (`RAG_BACKEND=pgvector` on Vercel, `faiss` locally) | `rag_pipeline.py` docstring: FAISS can't run on Vercel serverless — pgvector in Supabase is the serverless-safe path; FAISS stays for local dev quality. Deployment-shaped design. |
| D8 | **Hybrid retrieval** (semantic + BM25 → RRF → optional cross-encoder rerank) | `rag_hybrid.py` docstring — pure-vector retrieval misses energy jargon; keyword leg catches exact terms. |
| D9 | **Groq runtime-default LLM with Gemini fallback path** | `llm_client.py:28` defaults `LLM_PROVIDER=groq` (docstring still says gemini default — see watchlist); Groq free-tier limits documented in `groq_client.py`; commit `0dca0be` re-verified the live model stack (qwen3.8-27b + gpt-oss fallbacks, Sept 2026). Note: **paper §2.7.2.2.9 says Gemini 2.5 Flash is primary** — provider order flipped in practice. |
| D10 | **LLM output sanitization** | `llm_sanitizer.py` strips JSON wrappers/fences/HTML/chain-of-thought before rendering — LLM output treated as untrusted. |
| D11 | **Bundled CSV/JSON fallbacks** (`services/local_data/`, atlas/catchment fallbacks) | Multiple services follow Supabase→CSV fallback (`atlas_data.py`, `catchment_data.py`, `wind_output_calc.py` DATA_PATH). Keeps app alive for demos/tests without DB. *(inferred: also a defense-day safety net.)* |
| D12 | **Offline ETL, no runtime external-API calls** | NASA POWER/atlas/ERA5/terrain fetched by `python_scripts/`+`scripts/` and stored; perf doc §9 documents runtime reads from Supabase/bundled data only. Keeps local API at ~104 ms instead of being hostage to third-party latency. |
| D13 | **Anonymous EcoSim quota** instead of forced login | `dependencies/quota.py` — guests get N runs/IP (Redis TTL counter) then prompted to sign up. Preserves household accessibility (evaluation had non-account testers). |
| D14 | **TOTP-only 2FA** | Supabase GoTrue supports TOTP natively; SMS/WhatsApp would need paid Twilio (`megaplan-it-feedback` A2). |
| D15 | **Client-side PDF export via pdfmake** | Commit `1226dc9` adds pdfmake export; `dfb78f7` switched from self-hosted Roboto TTFs to pdfmake's bundled font container — fewer assets to ship/serve. |
| D16 | **Middleware order** (documented inline) | `main.py:58-91` comments: CORS outermost so 429/413/5xx carry headers; Timing last-added to measure everything including CORS. |
| D17 | **Docs gated on `settings.debug`** | `main.py:24-26` — `/docs`, `/redoc`, `/openapi.json` only in debug. (Security probe still flagged exposed docs in one environment — see 04.) |
| D18 | **Materialized views for map scores** | `map_service.py` reads `mv_province_map_data`/`mv_municipality_map_data` — precomputed aggregates keep the map interactive at province level. |
| D19 | **i18n en/fil** | Filipino audience (thesis households); `i18n/` parity enforced by `i18n-keys.test.js`. |
| D20 | **shadcn-style local primitives** (`components/ui/*`) | Vendored primitives — no UI-lib lock-in, Tailwind 4 tokens in `globals.css`. |
| D21 | **Error semantics**: sanitized 500 + request_id; PGRST116→404 via `utils/postgrest.py` | Post-audit fixes (commits `85fe223`, `30df253`, `d6cc646`) — never leak internals or postgrest noise to the client. |
| D22 | **Client IP = socket peer / platform header only** | `utils/network.py` — written for SEC-01 (XFF spoofing → quota/rate bypass). |
| D23 | **Explainability surfaces** (confidence score, `InterpretationBadge`, `CitationSources`, explanation modals) | `confidence.py` propagates data-coverage uncertainty; commit `e3f1fa0` added explanation modals after expert feedback. UI shows *why*, not just *what*. |
| D24 | **Data-coverage gating of pickers** | Commit `2e522bb`/`2a17ce9`: municipalities filtered by climate coverage + geolocation picker — users can't select sites with no data (which the API would reject anyway). |
| D25 | **`ecosim_autosave` default-on** | Migration 0023 + commit `941b6b0` — IT-expert feedback: don't make users remember to save. |

## 5. Module boundaries

- **`routes/` are thin**: parse/validate (Pydantic) → call service → shape response → map errors.
  Business logic lives in `services/` (e.g., `routes/ecosim.py` delegates to
  `services/ecosim.py`'s `build_ecosim_dashboard_response` — that one function fans in ~30 imports:
  calcs, plants, atlas, catchment, financials, caches).
- **`schemas/` is the contract layer**: request/response models + `Literal` enums at the boundary.
- **`services/` owns I/O**: Supabase (`supabase_service.py`), Redis (`redis_client.py`,
  `data_cache.py`), LLMs (`llm_client.py`/`groq_client.py`/`gemini_funcs.py`), retrieval
  (`rag_*`), geodata (`atlas_data`, `catchment_data`, `geospatial_service`, `map_service`).
- **`ml/` + `ml_worker_proxy.py`**: forecasting core + optional delegation to a heavy worker.
- **`middleware/` + `dependencies/`**: cross-cutting concerns (identity, limits, headers, IDs, timing).
- **Dormant code**: `routes/chat.py`, `routes/etl.py`, `pages/ChatPage.jsx` — present but unmounted.
  Say "implemented but not currently routed" if asked — do not claim they're live.

## 6. Security model (post-audit state)

| Layer | Mechanism | Evidence |
|---|---|---|
| AuthN | Supabase GoTrue — email/password + Google OAuth + TOTP 2FA | `AuthContext.jsx`, `jwt.py` |
| AuthZ | `require_admin`/`get_current_user` deps; role+status **fail-closed** after SEC-03 fix | `dependencies/auth.py`, commit `85fe223` |
| Rate limiting | 60 rpm sliding window, Redis-backed; merged counters post-SEC-02 | `middleware/rate_limit.py` |
| Guest quota | per-IP Redis TTL counter for anonymous EcoSim | `dependencies/quota.py` |
| RLS | DB policies on user tables; hardened across migrations 0009, 0024, 0025 + commit `e7b2a2a` | migrations, security lint fixes |
| Input | Pydantic + `extra="forbid"` + Literal enums; forecast `metric` enum validation; ETL table allowlist | `schemas/*`, `etl_orchestrator` tests |
| Output | `llm_sanitizer` on LLM text; label sanitization strips `<>` in simulations | `llm_sanitizer.py`, `routes/simulations.py` |
| Secrets | env-only; anon key publishable-by-design; service-role stays server-side | `.env.example`, `env.js` |
| Known residual findings | see `04-TESTING-AUDIT.md` §6 — XFF edge cases, dependency vulns, exposed docs in one env, RLS not directly probed | security artifacts |

## 7. Caching & resilience

- **Three cache tiers:** Redis app cache (`data_cache.py`, gzip) → `ecosim_cache` helpers
  (`redis_client.py` `_ECOSIM_TTL`) → bundled `local_data/` static fallbacks.
- **Graceful degradation ladder** everywhere: Supabase → CSV fallback; pgvector → FAISS local;
  Gemini→Groq emergency swap; Groq models cascade (commit `0dca0be`); explanation endpoints have
  cached fallbacks (migration 0019 exists *because* cards must render without an AI call).
- **Client-side resilience:** `apiClient.js` 30 s timeout, 3 retries w/ exponential backoff,
  no-retry-429; `53649f4` added EcoSim AI retry/status/visibility-polling UX.
- **Failure-recovery evidence:** TC-FR-02 (Gemini timeout → fallback dict in 61 ms),
  body-limit 413, unhandled-exception sanitizer — all in 04's artifact table.

## 8. Database evolution narrative (0001→0025)

The migrations tell the build story in order:

1. **Foundations (0001-0004):** geospatial schema (regions→provinces→municipalities→barangays +
   `geospatial_metadata`), PSGC columns, hardening; 0004 deliberately **keeps legacy `suitability_*`
   columns** so old clients didn't break — coexistence over rewrite.
2. **Forecasting (0005-0006):** model-run registry + forecast tables — predictions are *versioned*,
   not overwritten. Defensible: "which model produced this number?" is answerable.
3. **RAG & offload (0007-0008):** pgvector + `rag_chunks`; local datasets moved into Supabase.
4. **RLS hardening (0009):** user-data isolation.
5. **EcoSim as product (0010-0011):** climate as Supabase source-of-truth + AI cache; admin usage
   RPC optimized for serverless (one call, not N+1).
6. **Account features (0012-0018):** saved_* FKs, admin functions, per-request `user_ecosim_logs`
   (→ powers admin analytics), audit log, backfill.
7. **AI-cache discipline (0019-0020):** cache per-municipality explanations; invalidate on prompt
   changes (0020 clears cache so new prompts take effect — versioning applied to AI output).
8. **Validation data (0021-0022):** province-mode saves; Boothroyd 2023 catchment enrichment —
   the dataset behind defensible hydro scoring.
9. **Pre-launch (0023-0025):** autosave pref, column-scope privilege fixes, Supabase lint fixes.

**Panel answer for "how did the schema evolve?":** "Foundations → forecasting registry → RAG →
RLS → product features → validation datasets → launch-hardening. Every change is a numbered,
idempotent migration; nothing was applied by hand in the dashboard."

## 9. Known architectural limitations (say these first — beats being caught)

| Limitation | Reality | Honest framing |
|---|---|---|
| **Synchronous backend calls** | Most services are sync (`get_*_sync`); FastAPI runs them in threadpool | Fine at current load; heavy paths delegated to optional worker via `ml_worker_proxy` |
| **Single-worker load behavior** | Serverless = per-instance memory; in-memory rate-limit fallback is per-process | Redis path is correct/shared; memory fallback is best-effort (SEC-02 residual) |
| **Per-process fallback counters** | If Redis is down, quota/rate counters don't share state | Documented residual; fail-open vs fail-closed was a deliberate availability call *(inferred)* |
| **Dormant routes** | `/api/v1/chat` + `/api/v1/etl` code present, not mounted | Descoped, not deleted — present as "implemented but not routed" |
| **`@app.on_event` deprecation** | `main.py` startup hook uses deprecated API | Cosmetic; lifespan migration is a known cleanup item |
| **Free-tier ceilings** | Groq 20rpm/500k tpd; Upstash size limits (hence gzip); Vercel serverless timeouts | Cost-driven constraints shaped the architecture — own it: "designed for zero operating cost" |
| **No runtime external calls** = data staleness risk | ETL refresh is manual | Data is as fresh as the last ingestion run; refresh cadence is an ops task |
| **GitHub OAuth listed in old test doc** | Only Google OAuth is evidenced in `AuthContext.jsx`/`AuthCallback.jsx` | `UNVERIFIED:` GitHub provider — don't claim it |

## 10. Frontend architecture notes

- **Routing:** `AppRoutes.jsx` — public pages, `ProtectedRoute`-wrapped app pages,
  `AdminRoute`-wrapped admin. `ChatPage.jsx` exists unrouted.
- **State:** React context only (`AuthContext`, `ThemeContext`) — no Redux; app is read-heavy.
- **Data layer:** `services/apiClient.js` (timeout/retry policy) + feature services
  (`energyhub.js`, `savedLocations.js`); Supabase JS only for auth, never for app data — app data
  flows through the FastAPI boundary. *(inferred: keeps RLS/service-role separation clean.)*
- **i18n:** provider + `en.json`/`fil.json`; `{{var}}` interpolation; parity test exists.
- **Maps/charts:** Leaflet (`EnergyMap`) + Plotly (`PlotlyChart`); province/municipality polygons
  from simplified GeoJSON (`scripts/simplify-geojson.js` — payload size decision).
- **PDF:** pdfmake client-side, bundled fonts, `cssVarToHsl` theme matching.

## 11. Operational notes (no secrets — names only)

- **Env contract:** `.env.example` + `config/settings.py` (`load_dotenv(override=True)` — env file
  wins over shell vars; this confused test injection once, noted in failure doc).
- **Health:** `/api/v1/health` liveness; `/health/detailed` reports supabase/redis/rag_index and
  can return degraded — use it for demo-day readiness.
- **Startup warm-up:** Supabase+Redis clients pre-initialized; RAG index built in threadpool
  (non-blocking, warning on failure) — first request isn't the slow request.
- **Deploys:** frontend on Vercel (preview origins regex-scoped), backend on Vercel serverless,
  optional Docker worker for heavy paths.
- **User manual (appendix) records deployed URL:** `lumi-frontend-xi.vercel.app`.

---
*Design rationale cited from code comments/docstrings, `docs/`, or `git log` (commit hashes shown).
Everything else is tagged `*(inferred)*` — own those tags on the stand.*
