# 05 — Defense Knowledge Base

> Everything else needed on the stand: discrepancy watchlist, claims discipline, expanded Q&A
> bank, glossary, and demo-day operations reference. Cross-links: slides → `01`, code → `02`,
> architecture → `03`, tests → `04`, code logic → `02` Part D + `06a`–`06d`.

---

## 1. Discrepancy watchlist (know these before the panel finds them)

| # | Discrepancy | Facts | Rehearsed answer |
|---|---|---|---|
| W1 | **IT score 4.47 vs 4.46** | Deck/results say 4.47 ("Excellent"); appendix tabulation reports 4.46 | "The summary rounds to 4.47; the item-level tabulation computes to 4.46 — both inside the Excellent band. We kept both verbatim rather than silently aligning them." |
| W2 | **LLM provider order** | Paper §2.7.2.2.9 names **Gemini 2.5 Flash** as primary; `llm_client.py:28` runtime default is **groq**; deck says "Groq/Gemini-supported" | "Gemini was primary during development; by evaluation the live stack runs Groq first with Gemini in the supported path — the deck's 'Groq/Gemini-supported' phrasing reflects that shared support. Provider order changed as free-tier model availability changed (Sept 2026 re-verification)." |
| W3 | **Test counts drift** | Reported aggregate 315; current runs: unit 177, backend 119p+2f, integration 67p+30e, vitest 71 — varies by suite selection (`-m mock` etc.) | "The 315 figure is the documented defense-time aggregate across suites; re-runs vary because integration tests are environment-gated. The full reconciliation is documented in our testing audit." → `04-TESTING-AUDIT.md` §5 |
| W4 | **Two backend test failures** | `TestETLTableAllowlist` ×2 fail as "async def not natively supported" | "Tooling gap — those are async tests run without an async pytest plugin (pytest-asyncio). It's a test-environment issue, not an application defect; the same validations are exercised elsewhere." |
| W5 | **Integration errors (30)** | DB-dependent tests error without `TEST_DATABASE_URL`/test DB | "Integration tests need a dedicated test database; without it they're environment-blocked. We don't run them against production Supabase." |
| W6 | **Endpoint sweep counts** | Historical artifacts: 70/75, then 79/82, final artifact set shows 82 passing | "The sweep grew as endpoints were fixed; the final artifact set is 82/82." |
| W7 | **`lumi_tests/` vs `tests/`** | Deck references `lumi_tests/`; repo uses `tests/` after Sep-8 reorganization | "Same suite — the folder was renamed during repo reorganization; artifacts were re-homed." |
| W8 | **"AI Assistant" module** | Deck implies an assistant; `routes/chat.py` + `ChatPage.jsx` exist but are **unmounted** | "The assistant lives inside EcoSim/EnergyHub as explanation endpoints today; a standalone chat surface exists in code but isn't currently routed — we descoped it." |
| W9 | **GitHub OAuth** | Old functional-test doc lists GitHub sign-in; only **Google** OAuth is evidenced in `AuthContext`/`AuthCallback` | "Google OAuth is what's implemented; the GitHub entry in an early test document was aspirational. UNVERIFIED." |
| W10 | **Geothermal** | Reference-only on deck; code has full geothermal service stack | "Geothermal computation exists in the system, but it was presented as reference information — its recommendations were not part of expert agreement validation." |
| W11 | **Barangay granularity** | Code exposes barangay endpoints + climate fallback to barangay; deck scope = province/municipality | "Suitability scoring operates at municipality level; barangays appear in the climate-data fallback hierarchy, not as scored units." |
| W12 | **Needs-assessment N** | Paper cites ~196 household decision-makers in needs assessment; final eval = 100 | "Different phases: ~196 informed design; 100 households did the final evaluation." |

## 2. Claims discipline — say / never-say

| Never say | Say instead |
|---|---|
| "82% accurate" | "82.22% agreement with engineering experts — 37 of 45 assessments" |
| "Nationally validated" | "Nationwide data coverage; evaluation sample was CALABARZON" |
| "Fully secure" | "16 of 18 live probes passed; residual findings are documented" |
| "Replaces feasibility studies" | "Preliminary decision support — the system itself recommends consulting an engineer" |
| "Geothermal was validated/recommended" | "Geothermal is reference information only" |
| "Engineering rated it excellent" | "Engineering's technical assessment was 3.27 — Satisfactory" |
| "Proven business model" | "Proposed monetization; willingness-to-pay not yet validated" |
| "4.47 exactly" (if pressed) | "4.47 in the summary; 4.46 in the tabulated appendix — rounding-level" |
| "All tests pass" | "315 at documentation time; current re-run details in the testing audit" |
| "Real-time data" | "Curated datasets ingested through offline ETL — no runtime third-party calls" |

## 3. Panel Q&A bank

### Methodology / evaluation

**Q: Why a one-sample t-test against 3.00?**
A: The comparison items asked whether LUMI improves on *prior/conventional* methods; 3.00 is the
neutral midpoint — significantly above it means respondents lean toward improvement. It tests
*perceived* support, which is what the hypothesis claims — nothing more.

**Q: Why is engineering's rating (3.27) so much lower than IT's (4.47)?**
A: Different instruments and stakes. IT experts scored ISO 25010 *software quality*; engineers
scored *technical* dimensions — suitability correctness, reliability, safety — where they apply
professional standards a preliminary tool can't fully meet. We report both honestly and it shaped
our recommendations.

**Q: Is 82.22% good enough?**
A: 37/45 agreement across 9 locations supports *potential* — the deck's own conclusion says
further engineering validation remains necessary. Hydropower's 60% is the weakest and drove the
criteria-refinement recommendation (catchment enrichment via Boothroyd 2023 was one response).

**Q: Why mixed-method developmental research?**
A: The work is build-and-evaluate: iterative development plus quantitative instruments
(usability means, t-test, ISO scores, agreement rate) plus qualitative consultation (barangay
officials, engineers).

**Q: Sample of 100 — is it enough?**
A: It's the declared scope: CALABARZON households, not nationally representative — stated on the
limitations slide itself. Cronbach's α (0.923/0.868) confirms instrument reliability within it.

### Technical

**Q: Why FastAPI / React / Supabase?**
A: → `03` Decision log D1–D3. Short version: Pydantic boundary validation + Python DS ecosystem;
mature SPA ecosystem; managed Postgres+Auth+RLS on a free tier.

**Q: Why weighted MCDM instead of a learned model?**
A: Expert-validated weights are inspectable — engineers can challenge a weight, not a neural
network. We add AHP consistency checks and a PROMETHEE II cross-check; the agreement-rate
validation was only possible because the logic is transparent.

**Q: Why ARIMA(1,1,1)?**
A: Selected via AIC grid search (`ml/aic_grid.csv`) and pilot comparison vs linear/Holt/RF
(`tests/pilot_run/`); held-out MAPE 5.67%. It's a forecasting baseline a thesis can defend —
interpretable orders (p,d,q), standard diagnostics.

**Q: How does the AI stay honest?**
A: RAG grounding: retrieval over our own knowledge chunks (products, national stats, climate/
terrain) → structured prompts with grounding rules → `llm_sanitizer` strips wrappers/CoT →
cached outputs versioned by prompt (migration 0020 clears stale cache). Live call ~7.1 s; cached/
fallback ~1.9 s.

**Q: Two RAG backends?**
A: `RAG_BACKEND=pgvector` on Vercel (FAISS can't run serverless); FAISS locally for dev. Same
retrieval interface either way.

**Q: Where does the data come from?**
A: Offline ETL only: DOE statistics, NASA POWER climate, Solar/Wind Atlas rasters, ERA5 wind,
PSGC/PhilAtlas hierarchy, terrain rasters, Boothroyd 2023 catchments, GEM/IHFC geothermal,
Wikipedia plant lists, DOE 2026 provider registry → `02` §A.10. No runtime third-party calls —
that's why the API is ~104 ms.

**Q: What happens when external services fail?**
A: Degradation ladder: Supabase → bundled CSV/JSON fallbacks; pgvector → FAISS; Groq↔Gemini
fallback paths; Redis → `NullRedis` no-op + in-memory counters; explanations served from cache
(migration 0019 exists precisely so cards render without an AI call). Verified: TC-FR-02 Gemini
timeout → fallback dict in 61 ms.

**Q: Security posture?**
A: Supabase GoTrue + RLS; fail-closed auth deps; per-IP quotas; merged Redis rate counters;
boundary validation with `extra=forbid`; sanitized 500s with request IDs; client IP from socket/
platform headers only. Residual findings (XFF edge case, dependency vulns, docs exposure in one
env, RLS not directly probed) are documented — `04` §6.

**Q: What would you do with more time?**
A: Hydropower criteria refinement (60% agreement); more engineering validation sites; RLS
direct probing; async pytest plugin; province→barangay scoring depth; the dormant chat surface.

### Tricky / trap questions

**Q: "Your API is fast but your AI is slow — contradiction?"**
A: Different paths by design: local API ~104 ms serves curated data; the ~7.1 s is a live LLM
call; cached/fallback explanations ~1.9 s. We chose honest latency over fake speed.

**Q: "GWh-scale MAE sounds terrible."**
A: It's national demand — tens of thousands of GWh; MAPE 5.67% is the normalized figure. That's
why we report both.

**Q: "Why should households trust a recommendation?"**
A: Three signals: expert agreement rate (82.22%), the confidence score we surface per source
(data coverage + model uncertainty), and transparent criteria users can inspect.

**Q: "Is this just a wrapper on APIs?"**
A: No — third-party calls happen offline in ETL; the runtime system computes scoring, formulas,
forecasting, and retrieval itself. Show `services/mcda.py`, `*_output_calc.py`, `forecasting.py`.

**Q: "What's NOT tested?"**
A: RLS policies not directly probed; load beyond the tested 100-user level; barangay scoring;
province-mode edge cases in older artifacts; the dormant chat route. → `04` §7.

## 4. Glossary (deck/paper terminology — use their words)

| Term | Working definition in this project |
|---|---|
| **LUMI** | Data-Driven Environmental Intelligence System for Renewable Energy Decision Support |
| **EnergyHub** | Module: national/provincial statistics, interactive maps, demand forecasting |
| **EcoSim** | Module: household what-if simulation — generation, savings, payback, recommendations |
| **Weighted MCDM** | Multi-criteria decision-making with expert/AHP-derived weights + weighted sum + PROMETHEE II cross-check |
| **Suitability score** | Location's composite score per renewable source (municipality/province level) |
| **Composite score** | Aggregated renewable-potential score used on maps/dashboard |
| **Confidence score** | 0–100 per-source honesty signal from data coverage + model uncertainty |
| **ARIMA(1,1,1)** | Autoregressive Integrated Moving Average (p=1,d=1,q=1) demand forecaster |
| **Held-out MAPE** | Mean absolute percentage error on data the model never trained on — 5.67% |
| **RAG** | Retrieval-Augmented Generation — LLM answers grounded in retrieved project knowledge |
| **pgvector / FAISS** | The two retrieval backends (Supabase-hosted vs local) |
| **Agreement rate** | % of expert assessments matching system output — 37/45 = 82.22% |
| **ISO/IEC 25010:2023** | Software-quality standard used for the IT-expert instrument |
| **Cronbach's α** | Internal-consistency reliability (0.923 usability / 0.868 comparison) |
| **Neutral benchmark 3.00** | Scale midpoint the t-test compared ratings against |
| **CALABARZON / Region IV-A** | Evaluation sample area |
| **Data coverage vs validation** | Coverage = where data exists; validation = who evaluated. Never conflate. |
| **Preliminary decision support** | Guidance before (not instead of) professional feasibility study |
| **Run-of-river micro-hydro** | Hydro model: ρ·g·Q·H·η with slope-derived runoff coefficient |
| **NOCT** | Nominal Operating Cell Temperature — basis of the solar temperature factor |
| **PR (performance ratio)** | Solar loss aggregation: temp, dust, inverter, mismatch, wiring, degradation |
| **Betz limit** | 16/27 ≈ 59.3% theoretical max wind extraction — Cp bounded by it |
| **Boothroyd 2023 catchments** | Watershed geodatabase behind hydro runoff/stream inputs (migration 0022) |
| **PSGC/PSA** | Philippine geographic code hierarchy (regions→provinces→municipalities→barangays) |
| **GoTrue** | Supabase auth service (email, Google OAuth, TOTP 2FA) |
| **RLS** | Postgres row-level security — user-data isolation at the DB |
| **Anon vs service-role keys** | Publishable client key vs backend-only privileged key |
| **Upsert/materialized view** | `mv_province_map_data`/`mv_municipality_map_data` precomputed map aggregates |
| **`UNVERIFIED:`** | Our own tag: claim attempted but not confirmed — honesty marker |

## 5. Demo-day / operations quick reference

- **URLs:** frontend `lumi-frontend-xi.vercel.app`; backend `lumi-backend-ten.vercel.app`
  (`vercel.json`, appendix user manual).
- **Readiness check (2 min before demo):** hit `/api/v1/health/detailed` — expect supabase/redis/
  rag_index all ok; then load Dashboard → picker → one EcoSim run to warm caches.
- **Latency expectations:** API ~104 ms local (slower on cold serverless — warm it); AI
  explanations ~7 s live, ~2 s cached — narrate the wait ("this is a live model call").
- **If the LLM stalls:** the fallback path serves cached analysis; per-source modals have cached
  fallbacks (migration 0019). Worst case → B-01…B-17 screenshots in
  `docs/09-Technical-Evaluation/artifacts/screenshots/`.
- **Auth demo:** email/password + Google + TOTP enroll (MFASetup shows QR + manual secret).
  Don't promise GitHub.
- **Numbers at your fingertips:** 4.73 · 4.79 · 4.47(4.46) · 3.27 · 82.22% (37/45) · 85%/60%/N-A
  · 5.67% · 6,829.09 · 8,257.12 · 1,019.66 MW · ~104 ms · ~7.1 s · ~1.9 s · 315+2 · 82/82 ·
  16/18+warn · α .923/.868 · t(99)=55.47.
- **Cold-start note:** serverless first-hit can be slow — hit health + homepage during setup,
  not during the demo.

## 6. Auth & deployment notes (for "how is it run" questions)

- Local dev: `npm run dev` (Vite + uvicorn). Backend tests: `fastapi-backend/.venv`.
- Env contract lives in `.env.example`/`settings.py` — names only, never quote values.
- Deploys: Vercel frontend + serverless backend (`api/index.py`), Supabase cloud, Upstash Redis;
  optional Docker worker (`docker-compose*.yml`) for heavy ML paths via `ML_WORKER_URL`.
- Migrations: `supabase/migrations/` 0001→0025, all idempotent — apply in order, nothing manual.

## 7. Honest-limitations script (30 s, memorizable)

"LUMI is preliminary decision support. The household sample is CALABARZON, not national. The
82.22% figure is expert *agreement*, not accuracy — and hydropower at 60% needs work. Geothermal
is reference-only. Security probes passed 16 of 18 with documented residuals. And our own
recommendations list exactly what we'd strengthen next: hydro criteria, more validation sites,
broader datasets, deeper simulation."
