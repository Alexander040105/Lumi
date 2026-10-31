# Megaplan: Thesis Defense Preparation Pack (SWE-2 Max Prompt)

You are producing a **defense-preparation documentation pack** for **LUMI** — a Philippine
renewable-energy decision-support web app built as an undergraduate thesis ("LUMI: Data-Driven
Environmental Intelligence System for Renewable Energy Decision Support", University of Perpetual
Help System DALTA – Molino, November 2026).

Create a new folder **`ThesisDefensePrep/`** at the repo root containing the **six markdown
deliverables** specified in §5. The purpose: the system developer must be able to (a) present the
27-slide final defense deck, (b) trace every claim in the thesis paper to the code that implements
it, (c) explain in depth why the system was built the way it was, and (d) justify every reported
test result — without being able to be caught off guard.

Everything you need is referenced in this document — **verify every path and number before citing
it** (paths and counts may have drifted since this prompt was written).

---

## 1. Ground rules

1. **Documentation only.** Create/edit files ONLY inside `ThesisDefensePrep/`. No code changes, no
   edits to existing files, no commits, no `.env` reads into output, no secrets anywhere.
2. **Verify before you cite.** Every file path, line reference, test count, and figure in your
   output must be checked against the repo (grep/read) or the source documents (§2) first. If you
   cannot verify something, write `UNVERIFIED:` plus what you tried — never guess.
3. **Numbers are verbatim.** Copy every reported figure exactly from the embedded ground truth in
   §4. Never round, paraphrase, or "improve" a number. If two sources disagree, report both and
   flag the discrepancy instead of picking one silently.
4. **Rationale labeling.** Where the reason for a design decision is not recorded in code,
   comments, docs, or git history, write your best inference tagged `*(inferred)*`. Where it is
   recorded, cite it (`path:line`, `docs/...`, `git log`).
5. **Citations everywhere.** Claims cite their source: slide number (S#), thesis section (§), repo
   path (`fastapi-backend/app/services/mcda.py#L40`), or docs path (`docs/...`). This
   traceability is the whole point of the pack.
6. **English throughout.** Match the deck's terminology and glossary exactly (e.g., "Weighted
   MCDM", "EnergyHub", "EcoSim", "Composite Renewable Score").

---

## 2. Source files (outside the repo — absolute paths, readable on this machine)

| File | Size | Role | Read strategy |
|---|---|---|---|
| `C:\Users\Admin\Documents\DefenseGuide_LUMI\LUMI-Final-Defense-Agent-Guide.md` | ~23 KB | **Primary ground truth for the deck**: quick facts, key numbers, slide-by-slide (27 slides), tech-stack notes, caveats, Q&A | Read fully. Treat its §1 (Quick Facts) and §3 (Key Numbers) as source of truth. |
| `C:\Users\Admin\Documents\DefenseGuide_LUMI\Complete-LUMI_Thesis.docx.md` | **~46 MB**, ~8,400 lines, ~213 embedded base64 images | Full thesis text: Ch1 Problem/RRL, Ch2 Methodology (SDLC, DFDs, data dictionary, algorithm structure), Ch3 Results (test plan/results §3.3, ML evaluation §3.3.13), Ch4 Conclusions, appendices incl. System Codes (~pp.399–558) | **Never read whole file.** It is a docx conversion — headings are plain/bold text, NOT `#` markdown. Find section offsets with `grep -n "CHAPTER"`, `grep -n "^3\.3\."`, `grep -n "APPENDICES"`, `grep -n "System Codes"`, then read ≤500-line windows. Skip lines >2,000 chars (base64 image blobs). |
| `C:\Users\Admin\Documents\DefenseGuide_LUMI\FINAL-DEFENSE-PPT.pdf` | ~104 MB, 27 slides | The actual defense deck (Canva export) | `pdftotext` is on PATH. Extract to a temp file or stdout range to confirm slide order/visuals. The Agent Guide is already a faithful text extraction — use the PDF mainly for image-only slides and layout. |

Thesis navigation anchors (grep targets): `CHAPTER 1: THE PROBLEM`, `CHAPTER 2: METHODOLOGY`,
`CHAPTER 3: RESULTS AND DISCUSSION`, `CHAPTER 4: SUMMARY`, `TABLE OF CONTENTS`, `LIST OF TABLE`,
`LIST OF FIGURES`, `REFERENCES`, `APPENDICES`, plus numbered-section patterns like `2\.7\.2\.2\.8`,
`3\.3\.4`, `3\.3\.13`, `Statistical Analyses Output`, `System Codes`.

---

## 3. Repository orientation

Full-stack monorepo at `D:\63947\Documents\GitHub\Lumi`. Layout (verify before citing):

```
fastapi-backend/          FastAPI backend
  main.py                 uvicorn entry (main:app)
  requirements.txt        + requirements-vercel.txt (Vercel serverless)
  app/
    routes/               admin, api, chat, ecosim, energyhub, etl, example, forecast,
                          geospatial, geothermal, health, map, products, protected, simulations
    services/             mcda.py, mcda_weights_service.py, municipality_suitability_builder.py,
                          confidence.py, forecasting.py, ml_worker_proxy.py,
                          rag_pipeline.py, rag_hybrid.py, rag_faiss.py, rag_pgvector_store.py,
                          rag_embeddings_client.py, rag_knowledge_builder.py, rag_gemini_funcs.py,
                          llm_client.py, groq_client.py, gemini_funcs.py, llm_sanitizer.py,
                          ecosim.py, financials.py, solar_output_calc.py, hydro_output_calc.py,
                          hydro_plants.py, products.py, energyhub.py, atlas_data.py,
                          climate_service.py, map_service.py, geospatial_service.py,
                          data_cache.py, redis_client.py, supabase_service.py,
                          build_catchment_enrichment.py, catchment_data.py,
                          load_catchment_to_supabase.py, etl_orchestrator.py,
                          geothermal/, local_data/
    ml/predictor.py       ARIMA model wrapper
    auth/jwt.py           JWT helpers
    models/ schemas/ middleware/ dependencies/ utils/ config/
  tests/                  11 test files + conftest.py (see §4 for counts)
react-frontend/           React 18 + Vite + Tailwind 4, vitest
  src/
    pages/                Dashboard, EnergyHub, Ecosim, SavedSimulations, ChatPage, Login,
                          MFASetup, SecuritySettings, ProfilePage, ResetPassword, Home, About,
                          Privacy, Terms, NotFound, admin/
    components/           ecosim/ energyhub/ admin/ shared/ layout/ ui/ (shadcn-style primitives)
    context/AuthContext.jsx  Supabase auth wrapper (signup/login/OAuth/MFA/profile)
    services/             apiClient.js, energyhub.js, savedLocations.js, supabaseClient.js
    i18n/                 en.json + fil.json (every user-facing string, both locales, {{var}})
    routes/AppRoutes.jsx  hooks/ utils/ (ecosimAnalysis, ecosimPdf, matchProviders,
                          municipalities + *.test.* siblings) data/ layouts/ lib/
    __tests__/ components/__tests__/   vitest suites
tests/                    ROOT test dir — NOTE: the deck/paper cites `lumi_tests/`; that folder
  tests/unit/             was renamed `tests/` in the repo reorganization. Same suite.
    (7 files: test_ai_service, test_geothermal_calculations, test_ml_preprocessing,
     test_new_improvements, test_rag_embeddings_client, test_rag_pgvector_store,
     test_renewable_calculations)
  tests/integration/      test_api.py, test_database.py, test_pipeline.py, performance_test.py
  pilot_run/ reports/ test_results/ sql/ docs/ run_tests_and_save.py pytest.ini conftest.py
python_scripts/           ETL & data-prep: ingest_nasa_power_monthly.py, elevation_etl.py,
                          terrain_pipeline/, run_terrain_pipeline.py, join_wind_data(_betz).py,
                          geocode_missing_coords.py, fill_missing_coords_from_geojson.py,
                          prepare_national_energy_csv.py (+ .ipynb), prepare_rag_products.py,
                          municipality_climate_analysis.py, wind_power_coefficient.py,
                          append_istabreeze_products.py, clean_scraped_products.py,
                          extract_product_kw.py, get_geocode.py
scripts/                  ~30 ops/ingestion scripts: *_atlas_averages, extract_era5_wind,
                          ingest_era5_averages, ingest_municipality_climate_averages,
                          precompute_aquifer_scores, scrape_philatlas, sync_psgc_data,
                          migrate_csv_to_supabase, insert_geospatial_metadata,
                          insert_missing_municipalities, identify_gaps, check_cache, verify_fixes,
                          generate_erd, simplify-geojson.js, test_api.py, psgc_cache/
supabase/                 migrations/ (latest 0025_security_lint_fixes.sql; incl.
                          0022_catchment_enrichment.sql, 0023_profiles_ecosim_autosave.sql),
                          schema_structure/
api/index.py              Vercel serverless entry + vercel.json + docker-compose(.prod).yml, deploy/
expo-mobile/              2 files only — early stub, NOT part of the defended system
docs/                     ~317 md files — MINE THESE FIRST, they already contain audit material:
  09-Technical-Evaluation/  SYSTEM_TESTING_REPORT(+_v2), SYSTEM_TESTING_APPENDICES,
                          SYSTEM_TESTING_FORM_LUMI(+v2), TECHNICAL_EVALUATION_ALL_RESULTS,
                          TECHNICAL_EVALUATION_TEST_REPORTS, ML_Evaluation_Results_and_Discussion
                          (+_FORM_LUMI, +_v2), DATA_ACCURACY_AND_THESIS_DEFENSE_GUIDE,
                          LUMI_COMPREHENSIVE_AUDIT, LUMI_PRODUCTION_READINESS_REPORT,
                          LUMI_Project_Checklist_Compliance, functional-test-results.md,
                          load-scalability-results.md, performance-measurements.md,
                          security-test-results.md, failure-recovery-results.md,
                          system-architecture.md, artifacts/{functional,load,perf,security,
                          failure,live_captures,screenshots,scripts,rerun-2026-09-15,
                          tool-versions.txt}
  thesis/                 Chapter_3_* drafts, ISO25010 tables, LUMI_THESIS_REVISIONS_MASTER,
                          CONSULTATION_RECORD_2_*, THESIS_RESEARCH_INTEGRATION, revisionFiles/,
                          lumi-details/
  01–08                   Project-Overview, Architecture, Modules, ML-Data-Science,
                          Setup-Guides, Technical-Resources, Data-Extraction-Reports, Requirements
  megaplan-it-feedback.md Prior megaplan (IT-expert feedback fixes) — context for recent changes
  DOCS_INDEX.md           Full tracked-md index
Root                      README.md, DESIGN.md, PRODUCT.md, package.json, pyproject.toml,
                          requirements.txt, .env.example, docker-compose.yml, vercel.json
```

**Run/test commands** (Windows, Git Bash):
- Dev: `npm run dev` at root (Vite + `uvicorn main:app --reload --port 8000 --app-dir fastapi-backend`)
- Frontend tests: `cd react-frontend && npm run test:run` (vitest)
- Backend tests: `cd fastapi-backend && python -m pytest tests/`
- Unit/integration: `cd tests && python -m pytest tests/unit` / `tests/integration` (see `tests/pytest.ini`, `tests/conftest.py` — integration may require a live server/env)
- Collect-only (safe count reconciliation): `python -m pytest --collect-only -q` per suite
- Env contract per `.env.example`: `DATABASE_URL`/`SUPABASE_DB_URL` or discrete `DB_*`,
  `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, NASA POWER ingestion tunables
  (`START_YEAR=2018`, `ONLY_MISSING=true`, `BATCH_SIZE=500`, rate-limit/retry knobs), ETL tuning
  (`HTTP_*`, `CACHE_TTL_DAYS`, `DRY_RUN`, `RESUME_FROM_CACHE`), `LOG_LEVEL`. LLM/Redis/Gmail SMTP
  vars — confirm names in `app/config/` and `.env` without copying values.

---

## 4. Embedded ground truth — copy these numbers verbatim

Source: `LUMI-Final-Defense-Agent-Guide.md` §1–§4 (itself extracted from the PDF). **Do not
invent, round, or extend figures.** Where repo/paper disagree, report both + flag.

### 4.1 Identity
- Title: **LUMI: Data-Driven Environmental Intelligence System for Renewable Energy Decision Support**
- Team: Alexander Jon Solis (Developer), Lerrica Jeremy Torreno (Principal Researcher & Data
  Analyst), Sean Maverick Virata (Technical Writer). Tagline: "Cleaner Energy, Brighter Tomorrow."
- Type: web-based decision support system; target users: households; study area: Region IV-A
  (CALABARZON); system coverage nationwide at province + municipality level.
- Modules: **EnergyHub** (national/provincial data, maps, forecasting), **EcoSim** (what-if
  simulation + recommendations), **AI Assistant** (generated explanations).
- Methods: Weighted Multi-Criteria Decision-Making (MCDM), ARIMA(1,1,1) forecasting,
  RAG + LLM explanations. Sources: solar, wind, hydropower; geothermal = **reference only**.
- Research design: mixed-method developmental research (Needs Assessment → System Development →
  System Evaluation).

### 4.2 Household evaluation (n=100, CALABARZON)
- Usability (12 items): **4.73/5** (Strongly Agree); vs. prior/conventional methods (7 items):
  **4.79/5** (Strongly Agree); clarity of charts/maps/units/results: **4.70/5**.
- Cronbach's α: usability **0.923** (Excellent), comparison **0.868** (Good).
- Hypothesis: **t(99) = 55.47, p < .001** vs. neutral benchmark 3.00 → reject H₀.
- H₀: "LUMI does not significantly improve perceived support for household renewable-energy
  evaluation and decision-making compared with users' prior or conventional methods."

### 4.3 Expert evaluation
- IT experts (n=10), ISO/IEC 25010 weighted mean: **4.47/5** (Excellent) — NOTE: the deck's own
  appendix table says **4.46**, SD **0.60**. Both are cited; flag, don't resolve silently.
- Engineering experts (n=5, EE/ECE), technical assessment: **3.27/5** (Satisfactory).
- IT rating — Energy Dashboard & Map: **4.50/5** (SO1); EcoSim: **4.40/5** (SO4).
- Internal dev-team self-evaluation (appendix): **3.60/5** (Good).
- ISO/IEC 25010 breakdown: Compatibility **4.65** (high), Maintainability 4.60, Safety 4.50,
  Performance Efficiency 4.46, Security 4.46, Reliability 4.43, Functional Suitability 4.40,
  Flexibility **4.20** (low).

### 4.4 Recommendation-engine validation (Weighted MCDM)
- Overall agreement with engineering experts: **82.22%** = **37 of 45** valid assessments, across
  **9 locations**. Solar + Wind **85%**; Hydropower **60%**; Geothermal **N/A** (not evaluated).

### 4.5 ML / AI results
- ARIMA(1,1,1), national electricity consumption: held-out MAPE **5.67%**; MAE **6,829.09 GWh**;
  RMSE **8,257.12 GWh**; peak demand MAE **1,019.66 MW**.
- Generative AI: live model call **~7.1 s**; provider-fallback path **~1.9 s**; providers Groq/Gemini.

### 4.6 System testing (as reported in paper/deck)
- Automated: **315 passed**, 2 integration skipped. Breakdown: Unit **177**
  (`lumi_tests/tests/unit/` → now `tests/tests/unit/`), Backend **106**
  (`fastapi-backend/tests/`), Frontend Vitest **9** (3 files), Integration **23** (+2 skipped,
  live-server cases deselected).
- Live API endpoint sweep: **82/82** passed after corrections.
- Performance: **~104 ms** overall local-API average; no failures at tested 100-user load.
- Security probes: **16/18** passed; one warning + informational findings.
- Deck appendix names: `test_security_fixes.py` (29 cases: boundary validation, 404/422 mapping,
  invalid renewable types, map levels, forecast metrics), `test_catchment_enrichment.py` (21 cases:
  catchment CSV integrity, municipality coverage, no duplicate IDs, no nulls in key columns, valid
  match methods), `test_calibration.py` (19 cases: wind/hydro score functions, power-curve bounds,
  scoring baselines).

### 4.7 Caveats & claims to avoid (reproduce in the pack)
- NOT "nationally representative"/"validated nationwide" — coverage is national, the household
  sample is CALABARZON only.
- Recommendations are **preliminary** decision support — not a substitute for engineering or
  feasibility studies.
- Geothermal is reference information only; agreement not evaluated.
- 82.22% is agreement with engineering experts on 9 selected locations (37/45) — NOT a general
  accuracy figure. Hydropower agreement is 60%.
- Engineering experts rated 3.27/5 (Satisfactory); the 4.47 Excellent is IT experts on software
  quality. Don't conflate.
- Commercial viability/revenue/willingness-to-pay: proposed only, **not yet validated**.
- ~104 ms = local API average; ~7.1 s = live generative-AI call; ~1.9 s = fallback path.
- Hypothesis result = perceived support vs. neutral benchmark 3.00 — not a controlled comparison
  against another system.
- Security: 16/18 passed with one warning — never say "fully secure".
- Slide 9 misspells "Cronbach's" as "Cronback's"; slides 2, 23, 25, 27 are image-only.

### 4.8 Known drift to reconcile (observed when this prompt was written — re-verify)
- `tests/tests/unit/`: **177** `def test_` — matches deck exactly. ✓
- `fastapi-backend/tests/`: **121** `def test_` vs reported 106 (parametrization, post-paper
  additions, or deselection — investigate; don't assume which).
- `tests/tests/integration/`: **99** test-function defs vs reported 23 run / 2 skipped.
- Frontend vitest files: **~10** (`components/__tests__/`×3, `src/utils/`×4, `src/__tests__/`×3)
  vs reported 9 tests / 3 files.
- Slide 26 says "eight characteristics" — the 25010 chart indeed shows eight.

---

## 5. Deliverables — `ThesisDefensePrep/` at repo root

If any single file would exceed ~3–4k lines, split it into `NN-name/` with an index file and say
so in the README. All file references inside the docs use repo-relative paths; add `#L<line>`
anchors where useful.

### 5.0 `README.md` — pack index
- What this folder is, who it's for (the developer defending), how the docs relate.
- Table of the five docs with one-line purpose each + suggested reading order.
- How to rehearse (which docs for slides, which for Q&A) + pointer to the demo-day checklist in 05.
- Regeneration note: produced by `docs/megaplan-thesis-defense.md`.

### 5.1 `01-PRESENTATION-GUIDE-AND-SCRIPT.md` — presentation guide + script
**Purpose:** rehearse the 27-slide deck cold. Structure: front matter then one section per slide.
- Front matter: runtime target (suggest 15–20 min for 27 slides; state the implied ~40–45 s/slide
  budget), pre-flight checklist (env running, demo tab order, fallback assets ready), how to use
  the two script formats.
- Per slide (S1–S27), using the Agent Guide §4 slide breakdown as the skeleton:
  - **On screen:** what the audience sees (from the guide; mark `[image-only]` slides).
  - **Verbatim script:** word-for-word spoken English, first-person plural ("we"), ~60–90 s per
    content slide, natural and confident; embeds the §4 numbers exactly.
  - **Talking points:** 3–6 bullets — the condensed version for someone who won't memorize.
  - **Delivery notes:** emphasis cues, the exact transition sentence into the next slide, timing
    (per-slide + cumulative), what to cut if running over.
  - **If asked here:** 1–3 likely panel questions for that slide + short grounded answers.
- Special handling:
  - S2 (poster), S25 (photos), S27 (questionnaire tabulation) are image-only → insert
    `[USER INPUT NEEDED — describe what the image shows]` placeholders plus a suggested narration
    scaffold (what a panel expects to hear at that moment).
  - S23 (system demonstration) → write a **live-demo choreography** section: exact screen sequence
    (e.g., login → Dashboard pick a municipality → EcoSim wizard 5 steps → results + AI
    explanation → Saved Simulations → EnergyHub map/forecast), what to click, what to say while it
    loads (esp. the ~7.1 s AI wait), and a **backup plan** (17 named evidence screenshots
    `B-01…B-17` under `docs/09-Technical-Evaluation/artifacts/screenshots/` — pytest runs, endpoint
    sweep, security probes, locust load tests; plus any recordings under `video/`).
  - S26 → script must recite the named test files and counts from memory-friendly phrasing.
  - S22 (monetization) → keep every claim in "proposed/unvalidated" language per §4.7.

### 5.2 `02-PAPER-TO-CODE-AUDIT.md` — paper ↔ code traceability
**Purpose:** answer any "show me the code for X in the paper" question in seconds. Three parts:

**Part A — Traceability matrix.** One row per claim/feature/section of the paper & deck. Columns:
`Paper/deck ref (§ or S#) | Claim / feature | Implementing file(s) (repo path[:line]) | What it
does | Decision rationale (cite or *inferred*)`. Cover at minimum:
- All eight specific objectives SO1–SO8 → their modules and evidence files.
- Weighted MCDM: `services/mcda.py`, `mcda_weights_service.py`,
  `municipality_suitability_builder.py`, `confidence.py`; where the criteria/weights come from;
  `routes/ecosim.py`, `geothermal/` handling (reference-only per caveats).
- ARIMA(1,1,1): `ml/predictor.py`, `services/forecasting.py`, `ml_worker_proxy.py`,
  `routes/forecast.py`; dataset prep `python_scripts/prepare_national_energy_csv.py`; the paper's
  model-selection rationale (search thesis §2.7.2.2.8, §3.3.13.3, §3.3.13.9 — quote it if found,
  else `UNVERIFIED`).
- RAG/AI assistant: `rag_pipeline.py`, `rag_hybrid.py`, `rag_faiss.py`, `rag_pgvector_store.py`,
  `rag_embeddings_client.py`, `rag_knowledge_builder.py`, `rag_gemini_funcs.py`, `llm_client.py`,
  `groq_client.py`, `gemini_funcs.py`, `llm_sanitizer.py`, `routes/chat.py`; `prepare_rag_products.py`.
- EcoSim calculations: `services/ecosim.py`, `financials.py`, `solar_output_calc.py`,
  `hydro_output_calc.py`, `hydro_plants.py`, `products.py`; the `meralco_rate` franchise-area card.
- Catchment enrichment (hydro): `build_catchment_enrichment.py`, `catchment_data.py`,
  `load_catchment_to_supabase.py`, `supabase/migrations/0022_catchment_enrichment.sql`,
  `scripts/precompute_aquifer_scores.py`.
- EnergyHub & maps: `services/energyhub.py`, `atlas_data.py`, `climate_service.py`,
  `map_service.py`, `geospatial_service.py`; routes `energyhub.py`, `map.py`, `geospatial.py`,
  `geothermal.py`; `scripts/*atlas*`, `extract_era5_wind.py`, `ingest_*`, `scrape_philatlas.py`,
  `sync_psgc_data.py`.
- Auth & accounts: `context/AuthContext.jsx`, `auth/jwt.py`, `routes/protected.py`,
  `pages/Login.jsx`, `MFASetup.jsx`, `SecuritySettings.jsx`, `AuthCallback.jsx`; Supabase GoTrue
  (email/password, Google OAuth, TOTP 2FA), Gmail SMTP confirmations, RLS policies
  (`supabase/migrations/0009_rls_hardening.sql` and later).
- Saved simulations & locations: `routes/simulations.py`, `services/savedLocations.js`,
  `pages/SavedSimulations.jsx`, autosave (migration `0023_profiles_ecosim_autosave.sql`,
  profile payload in `protected.py`).
- Every named data source (DOE, NASA POWER, PhilAtlas, PSGC, ERA5, terrain/elevation, aquifer,
  wind/hydro plant lists, products/providers directory) → its ingestion file + table.
- Frontend surfaces: each page/component group → the feature it renders.
- Evaluation instruments/results in the paper (survey instruments, ISO 25010 rubric, engineering
  instrument) → where they're documented (`docs/`, `tests/docs`, appendices).

**Part B — Exhaustive file inventory.** Every code file in scope, grouped by directory, table
columns: `File | Purpose | Key exports/functions | Rationale/notes (cite or *inferred*)`. In
scope: `fastapi-backend/` (app + tests), `react-frontend/src/`, `python_scripts/`, `scripts/`,
`tests/`, `api/`, `supabase/` (migrations summarized per-file), plus root config files worth
explaining (`vercel.json`, `docker-compose*.yml`, `pyproject.toml`, `package.json` scripts).
Explicit exclusions: `node_modules/`, `.venv/`, `__pycache__/`, `dist/`, `.git/`, `data/` raw
datasets (summarize by category/table instead of per-file), binary assets, `expo-mobile/` (note:
stub, future work).

**Part C — Bidirectional gap lists.**
- Code in the repo the paper never mentions (e.g., admin routes, ETL ops scripts) — one line each
  on why it exists.
- Paper/deck claims with no locatable implementing code — flag each with what you searched; do NOT
  fabricate a mapping.

**Acceptance:** every SO1–SO8 row and every §4-listed component resolves to ≥1 verified path or an
explicit flag; every in-scope file has an inventory row or an exclusion reason.

### 5.3 `03-SYSTEM-DESIGN-AUDIT.md` — architecture & decision rationale
**Purpose:** the developer's in-depth "why we built it this way" reference. Sections:
- **System context:** actors (households, evaluators, admin), external systems (Supabase, Groq,
  Gemini, NASA POWER, DOE/PhilAtlas/PSGC/ERA5 sources), deployment topology (Vercel serverless via
  `api/index.py` + `vercel.json`; `docker-compose` alternative; uvicorn local).
- **Module map:** EnergyHub, EcoSim, AI Assistant + supporting (auth, saved simulations,
  providers directory, admin) — each with its routes/services/frontend files.
- **Input → Process → Output** per slide 10, expanded to name the real components on each arrow.
- **Data pipeline narrative:** sources → ingestion (`python_scripts/`, `scripts/`,
  `etl_orchestrator.py`) → Supabase tables/materialized averages → serving (`data_cache.py`,
  `redis_client.py` w/ fallback, `services/local_data/`) → API → UI. Include the idempotent/
  `ONLY_MISSING`/`RESUME_FROM_CACHE`/`DRY_RUN` design and why it exists.
- **Decision log** — the core of the doc. One subsection per decision: `Decision | What the code
  does | Why (cite docs/, comments, git log — or *inferred*) | Alternatives/trade-offs`. Cover at
  minimum: FastAPI; React+Vite+Tailwind+shadcn-style primitives; Supabase Postgres + GoTrue +
  RLS; Redis/server cache; ARIMA(1,1,1) (quote the paper's rationale if present); weighted MCDM +
  weight provenance; catchment enrichment for hydropower; hybrid RAG (FAISS + pgvector);
  Groq→Gemini provider fallback; LLM output sanitization; TOTP-only MFA (Twilio out of scope);
  municipality-level granularity + duplicate names kept; city-only picker (hide-not-delete
  convention, per stakeholder); autosave-default-ON; i18n en/fil; precomputed atlas/suitability
  averages; Vercel + uvicorn topology.
- **Security model:** auth flow (OAuth callback, JWT, MFA), RLS, sanitization, rate limiting —
  cite `docs/09-Technical-Evaluation/security-test-results.md` and `auth/`, `middleware/`,
  `llm_sanitizer.py`.
- **Data-accuracy defenses:** cite `DATA_ACCURACY_AND_THESIS_DEFENSE_GUIDE.md` + calibration/
  catchment/scoring code — how the system keeps scores honest (and where it can't).
- **Known limitations mapped to code:** geothermal reference-only, hydro 60% agreement,
  preliminary-only assessments, sample limitations — show where each is encoded or disclosed in
  the UI/paper.
- **Migration history:** `supabase/migrations/0001→0025` one-line each — what changed and why
  (esp. 0022 catchment, 0023 autosave, 0024 audit fixes, 0025 security lint).

### 5.4 `04-TESTING-AUDIT.md` — every test, justified
**Purpose:** defend every test claim in the paper and deck. Sections:
- **Suite inventory:** `| Suite | Location | Files | How to run | Reported result (paper/deck) |
  Collected count now | Status |` — unit (177 reported, `tests/tests/unit/`), backend (106
  reported, `fastapi-backend/tests/`), frontend vitest (9 / 3 files reported,
  `react-frontend/src/**/__tests__` + `utils/*.test.*`), integration (23 + 2 skipped reported,
  `tests/tests/integration/`), live endpoint sweep (82/82), load/perf (~104 ms, 100-user),
  security probes (16/18), pilot run (`tests/pilot_run/evaluate_models.py`).
- **Per-file breakdown:** every test file — what it covers, which claim(s) it substantiates, any
  notable cases (esp. deck-named `test_security_fixes.py` 29 / `test_catchment_enrichment.py` 21 /
  `test_calibration.py` 19 — verify the case counts in-file).
- **Reconciliation section:** explain each drift item in §4.8. Investigate with
  `python -m pytest --collect-only -q` per suite and `git log --follow -- <testfile>` to date
  post-snapshot additions; explain parametrization/deselection (live-server cases) where relevant.
  If a count can't be reconciled, mark `UNVERIFIED:` with evidence gathered — do not assert a
  cause you didn't find.
- **Evidence trails:** what each artifact proves and where it lives —
  `docs/09-Technical-Evaluation/{functional,load,perf,security}-*results.md`,
  `artifacts/{load,perf,security,functional,live_captures,rerun-2026-09-15}/`,
  `tests/reports/test_results_report.md`, `tests/test_results/`. Map each reported number
  (82/82, ~104 ms, 16/18, 100-user) to its artifact file.
- **Justification matrix:** `| Claim in paper/PPT | Evidence | Where it lives | How to re-prove
  it live (exact command) |`.
- **Coverage gaps:** untested or thin areas discovered during the audit — own them before the
  panel does.
- **Reproducibility:** exact env/commands to re-run everything (env vars needed, which suites need
  a live server or DB, expected runtime).

### 5.5 `05-DEFENSE-KNOWLEDGE-BASE.md` — everything else you need to know
**Purpose:** the catch-all "things I didn't know to ask about" doc. Sections:
- **Discrepancy watchlist:** `| Item | Deck/paper says | Repo/other source says | What to say if
  asked |` — include: 4.46 vs 4.47 IT mean; "Cronback's" typo (S9); image-only slides;
  test-count drift items; engineering 3.27 framing; hydro 60%; internal self-eval 3.60; anything
  new you find.
- **Caveats & claims to avoid:** reproduce §4.7 verbatim + any additions discovered.
- **Panel Q&A bank:** start with the Agent Guide §7's 8 grounded Q&As verbatim, then add
  code-grounded ones this repo can now answer, e.g.: why ARIMA(1,1,1) (pull the paper's
  model-selection section); how MCDM weights were derived/validated; what happens when Groq is
  down (fallback chain ~1.9 s); why TOTP-only 2FA; behavior without Redis; cold-start/connection
  pooling; data freshness & update cadence; why municipality-level (not barangay); what the admin
  routes do; mobile-app status (stub); why Vitest coverage is small relative to backend; how
  scores are calibrated; what the LLM sanitizer strips. Tag each answer with its evidence.
- **Ops quick-reference:** required env vars (names only — where each is consumed), `npm run dev`,
  local URLs, demo account/seed notes if discoverable, and a **demo-day checklist** incl. offline
  fallback (artifacts/screenshots, `video/` assets).
- **Repo quick-map:** "if asked about X, open file Y" index for live code navigation.
- **Glossary:** extend the Agent Guide's with repo terms (MCDA naming, catchment, atlas averages,
  PSGC, ERA5, GoTrue, RLS, TOTP, FAISS, pgvector, holdout MAPE, parametrize).
- **Interesting-but-unasked:** anything notable you find that a panelist might latch onto —
  e.g., the `confidence.py` scoring, `local_data/` fallbacks, `etl_orchestrator` idempotency,
  admin export, `i18n` coverage tests, `Audit`/`security_lint` migrations, `.benchmarks/`,
  deployment modes (Vercel vs docker).

---

## 6. Non-goals

- No code changes and no "fixing" discrepancies — document them.
- No inventing content for image-only slides — placeholders + scaffold only.
- No commits, branches, or PRs. No `.env` values or secrets in any output.
- No re-deriving statistics — cite reported values; verification = re-run evidence, not new math.
- `expo-mobile/` is a stub — document as future work, don't audit it as a feature.
- Don't duplicate what `docs/` already proves — cite/synthesize it instead.

---

## 7. Suggested slice order

1. **Scaffold:** create `ThesisDefensePrep/` + `README.md` skeleton; run source extraction —
   grep the thesis for section offsets, `pdftotext` the PDF to a temp file; record both in notes.
2. **`04-TESTING-AUDIT.md`** — most objective; the `--collect-only` runs double as drift checks.
3. **`02-PAPER-TO-CODE-AUDIT.md`** — largest; its matrix feeds 03 and 05.
4. **`03-SYSTEM-DESIGN-AUDIT.md`** — synthesizes 02 + docs/ + git history.
5. **`01-PRESENTATION-GUIDE-AND-SCRIPT.md`** — write once all facts are settled.
6. **`05-DEFENSE-KNOWLEDGE-BASE.md`** — catches everything the others surfaced.
7. **Finalize `README.md` + self-verification pass** — re-check every cited path exists and every
   number matches §4 verbatim.

Keep each file self-sufficient (a panelist question might send the developer to only one doc).

---

## 8. Verification checklist (all must hold before you're done)

- [ ] `ThesisDefensePrep/` exists with all six files; README indexes them with one-line purposes.
- [ ] Every SO1–SO8 and every §4 component maps to ≥1 verified repo path — or is flagged with the
      searches tried.
- [ ] Every in-scope code file has a Part B inventory row — or an explicit exclusion reason.
- [ ] Every cited path was verified to exist; every number matches §4 verbatim (spot-check all of
      4.2–4.6 in the output docs).
- [ ] The script covers all 27 slides: verbatim + talking-points + delivery notes + if-asked;
      image-only slides have `[USER INPUT NEEDED]` placeholders; S23 has demo choreography +
      backup plan; a total-runtime estimate exists.
- [ ] The reconciliation table addresses every §4.8 item — resolved or `UNVERIFIED:` with evidence.
- [ ] Caveats in §4.7 appear verbatim in 01 and 05; no doc overclaims (nationwide, accuracy,
      security, commercial).
- [ ] No files outside `ThesisDefensePrep/` created or modified; no commits; no secrets.

---

## 9. Constraints

- Markdown must render cleanly on GitHub (tables, anchors, code fences).
- Windows environment: Git Bash syntax; `pdftotext`, `python`, `pytest`, `npm` on PATH.
- Terminology must match the deck exactly; first-person plural in scripts.
- If the thesis file is unreadable in a section (corrupt conversion, pure images), mark
  `[USER INPUT NEEDED]` and move on — do not stall.
