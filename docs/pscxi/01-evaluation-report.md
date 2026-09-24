# LUMI Evaluation Report — PSC XI Readiness & App Health

**Date:** 2026-09-24 · **Scope:** static code review + live probing of the deployed backend (`lumi-backend-ten.vercel.app`) + local dev server + `impeccable` critique of the judge-facing flow · **Method:** adversarial; every finding carries file:line or live evidence.

---

## Verdicts

### PSC XI verdict: **YES, ENTER — with 3 gaps to close first**

LUMI is a working, deployed, bilingual, data-grounded product — far past the ideation/MVP stage PSC targets, and eligibility fits (college student team, ICT/AI-enabled solution). The entry's biggest risks are **not technical**:

1. **Judges can't try the product.** `/ecosim` and `/energyhub` sit behind `ProtectedRoute` — the first click lands on a login form (P0-H1 below).
2. **The money answer never appears on screen.** Monthly savings / install cost / payback exist in the API and PDF but are deliberately unmounted — the homeowner's core question goes unanswered in the demo (P0-H2).
3. **Business substance is team-supplied.** Market sizing, business model choice, financials, traction evidence — sections 7/8/10 of the concept note — cannot be generated from the repo; `[TEAM INPUT]` markers in `02-concept-note-draft.md`.

### App health verdict: **NEAR-READY** — prior launch-blockers are fixed; remaining items are polish + ops

All findings from the 2026-09-17 prelaunch audit were re-verified **fixed in code** (see Re-verification table). Remaining work: one production CORS config drift (M1), a demo-blocking auth/quota interaction (H1), the hidden financial layer decision (H2), and a tail of LOW polish items.

---

## CRITICAL

None. The prior C1 (PostgREST privilege escalation) is fixed and verified.

## HIGH

### H1. Login wall blocks all product value — anonymous quota is unreachable from the UI

`AppRoutes.jsx:72-85` wraps `/ecosim` and `/energyhub` in `ProtectedRoute` → anonymous visitors are redirected to `/login` before seeing anything. Meanwhile the backend ships an anonymous quota path (`app/dependencies/quota.py:150-191`, `anonymous_ecosim_quota`) and the UI renders `remaining_anonymous_requests` copy (`EcosimResults.jsx`) — anonymous access was designed but is unreachable through the app.

**Compounding factor:** `anonymous_ecosim_quota = 1` per `86400`s window (`settings.py:71-72`), keyed on direct peer IP. Under Philippine CGNAT (mobile carriers, offices, schools share IPs), a judge on a shared network may get **zero** runs even if the route were public. Verified live: first anonymous `GET /ecosim/?...` → `401 "Please log in to continue using EcoSim."`

**Impact:** a PSC judge doing a 3-minute click-through hits a signup wall; real first-contact users on shared IPs get a login wall too.

**Fix:** make `/ecosim` (and likely `/energyhub`) public — gate *saving*, not *running*; or ship a "Try a sample estimate" path on the landing page. Revisit `anonymous_ecosim_quota` (1/day is demo-hostile) and show remaining quota in the wizard before users invest effort.

### H2. The financial layer exists but never renders

The API returns `monthly_savings`, `installation_cost`, `payback_years`; the PDF export prints them (`utils/ecosimPdf.js:790-821`); localized `ecosim.results.financial.*` / `lcoe.*` / `productRecs.*` strings exist in `en.json`/`fil.json`; and `EcosimBOM.jsx` is complete — but **nothing mounts any of it**. `EcosimBOM` has zero importers (grep-verified). `EcosimResults.jsx:457` comments: `{/* Scenario comparison hidden until financial modeling is reliable */}` — a deliberate withholding, not a bug.

**Impact:** the product's stated job — "understand estimated cost, payback period, monthly savings … before committing money" (PRODUCT.md) — is answered only inside a PDF the user may never open. For judging, the most persuasive artifacts (BOM, financial impact) are invisible.

**Fix:** decide deliberately: either render a hedged "Your Financial Impact" card (bill → est. new bill → ₱ savings → install cost → payback, with `costNote` disclaimers) + mount `EcosimBOM`, or document the withholding and de-scope the promise from landing copy. Do not leave it ambiguous.

## MEDIUM

### M1. Production backend admits localhost CORS origins — VERIFIED LIVE

`OPTIONS`/`GET` with `Origin: http://127.0.0.1:5173` against `https://lumi-backend-ten.vercel.app` returns `Access-Control-Allow-Origin: http://127.0.0.1:5173` + `Access-Control-Allow-Credentials: true`. Code (`main.py:74-80`) drops localhost only when `ENVIRONMENT=production`, and `settings.py:27-30,32` defaults `cors_origins` to include `localhost:5173` and `environment` to `"development"`. The deploy is missing `ENVIRONMENT=production` and/or `CORS_ORIGINS` — or predates the M6 fix.

**Impact:** any locally-hosted page can make credentialed calls to the prod API on a user's machine. JWT still required for protected routes; blast radius is modest but nonzero.

**Fix:** set `ENVIRONMENT=production` + explicit `CORS_ORIGINS` (no localhost) in Vercel env; defense-in-depth: strip localhost from `_DEFAULT_CORS_ORIGINS` when `environment == "production"`.

### M2. `npm audit`: 4 vulnerabilities (2 critical)

`maplibre-gl` XSS-sanitizer bypass (GHSA-jrc7-96c5-q579) via `plotly.js`; `vitest` path traversal via `@vitest/mocker` (GHSA-82fw-gwwq-j7x9, dev-only). LUMI has no `dangerouslySetInnerHTML` and escapes markdown, so the maplibre path is likely unreachable today — but plotly-rendered untrusted content could reach `DOM.sanitize`.

**Fix:** `npm audit fix` where non-breaking; pin/upgrade `plotly.js` or switch to `plotly.js-basic-dist`/partial bundles (also shrinks the 4.9 MB lazy chunk); add `npm audit` to CI.

### M3. `energyHub.map.explanationTitle` structure mismatch breaks Filipino titles

`en.json:883` defines `explanationTitle` as an object with 5 metric keys; `fil.json:902` defines it as a flat string. `MapExplanationCard.jsx:82` resolves `t('energyHub.map.explanationTitle.${metric}')` → in Filipino this resolves against a string leaf and degrades (raw key/fallback).

**Fix:** mirror the en object shape in `fil.json` with translated per-metric titles.

### M4. No error tracking / alerting in production

Frontend has `@vercel/analytics` (`App.jsx:4`); backend has request-id/timing/rate-limit middleware + logging. But no Sentry-class error tracking, no uptime monitor, no web-vitals RUM. A silent 500 during judging or user testing would be invisible.

**Fix:** add Sentry (or Vercel log drains + an uptime ping on `/health/detailed`) before real-user testing.

### M5. `forecast/run` returns `{"error": ...}` with HTTP 200

`forecast.py:61-62` returns a 200 with an error body when historical data is missing — inconsistent with the 4xx/5xx semantics elsewhere; also reaches into private `ml._historical`.

**Fix:** return 503/404 + move the readiness check behind a public method on the service.

## LOW

- **L1.** Municipality auto-preselected: `Ecosim.jsx:179-182` sets `items[0]` on load → one-tap run on the wrong town. Leave the field empty. (`[skill: impeccable clarify]`)
- **L2.** Step-2 Next is silently disabled until `electricityRate > 0` while copy frames it optional (`EcosimWizard.jsx:31`); the computed-rate chip appears only after other fields are filled — the stuck state is the common case. (`[skill: impeccable clarify]`)
- **L3.** "Save as PDF" mounts only when `aiReady` (`EcosimWizard.jsx:401`) — invisible for up to ~30s of AI polling; actions live at top of page while results render far below on mobile. (`[skill: impeccable adapt]`)
- **L4.** `SearchableSelect` has combobox/listbox roles but no arrow-key nav / `aria-activedescendant` / Enter-select (`SearchableSelect.jsx:29-59`) — the app's core control fails keyboard WCAG. (`[skill: impeccable audit]` → fix)
- **L5.** i18n polish leaks: literal `**markdown**` asterisks rendered to users (`en.json:1034-1035` via `EcosimWizard.jsx:261-265`); raw enum "Hydropower" unlocalized in the completion dialog (`Ecosim.jsx:686`); `fil.json:1014` typo "pino- refine"; hardcoded EN fallbacks on wizard buttons (`EcosimWizard.jsx:398,414`); `document.documentElement.lang` never switches to `fil`. (`[skill: impeccable harden]` + i18n)
- **L6.** Localized step names `wizard.steps.step1-5` exist in both locales but the indicator renders only "Step X of 5" (`EcosimWizard.jsx:96-123`). (`[skill: impeccable clarify]`)
- **L7.** Hero primary CTA "Explore Energy in my Area" routes to `/energyhub` (analyst tool) not `/ecosim` (homeowner tool) — inverted CTA hierarchy for the primary persona (`Home.jsx:150-155`). (`[skill: impeccable shape]`)
- **L8.** Navbar mobile menu is a custom dropdown, not the `Sheet` DESIGN.md specifies — no Escape/focus management (`Navbar.jsx:226-238`). Two logo assets (`/logo.png` vs `/lumi-logo.png`) — verify same mark. (`[skill: frontend-ui-engineering]`)
- **L9.** Dead surface: `MapPage`, `ChatPage`, `ProfilePage`, `AdminModeration` unrouted; apiClient carries `createItem`, `runClimateEtl`, `getLineage`, `sendChatMessage`, `getChatSessions`, `getChatSessionMessages` that hit 404s (routers disabled). Unused `Table` import + `comparisonMax` in `Ecosim.jsx`. (`[skill: deprecation-and-migration]` / `code-simplification`)
- **L10.** `main.py:96` uses deprecated `@app.on_event("startup")` → migrate to lifespan handler. (`[skill: code-simplification]`)
- **L11.** Dev-env nits: `pytest-asyncio` absent from requirements (2 async tests need it); Windows lacks `python` alias (`py` only — README says `python -m venv`); local `node_modules` drifted from lockfile (react-tabs missing until `npm install`). (`[skill: ci-cd-and-automation]` / docs)
- **L12.** Completion modal fires *and* scrolls behind itself (`Ecosim.jsx:291-299`); renders raw `recommended_source`; step-2 icon uses `text-warning` while siblings use `text-primary`. (`[skill: impeccable polish]`)
- **L13.** Unverifiable: Supabase dashboard SMTP config (audit L9 — email-send rate limit hit previously; verify custom SMTP before user testing) and duplicate `server` response header (audit L5).

## Prior-audit re-verification (all FIXED at code level)

| Audit item | Status | Evidence |
|---|---|---|
| C1 PostgREST `plan`/`is_active` self-escalation | **Fixed** | `migrations/0024`: table-level UPDATE revoked; column grant = profile fields only |
| H1 User-deletion FK violations | **Fixed** | `0024`: CASCADE on `saved_simulations`, `saved_locations`, `chat_sessions`, `user_usage_limits`; `SET NULL` on `admin_audit_log`; `user_ecosim_logs` had CASCADE at creation (0015:6); `chat_messages` cascades via session (schema:2055); `profiles`/`user_roles` CASCADE (schema:2150,2180) |
| H2 Missing i18n keys (33 fil + 3 en) | **Fixed** | key-diff script: 795 `t()` keys, 0 real misses; new `i18n-keys.test.js` CI check exists |
| H3 6.4 MB unbundled entry | **Fixed** | `vite build`: entry `index-*.js` = **610.8 kB** (gzip 182.7); route-level lazy chunks (Ecosim 112 kB, EnergyHub 55 kB); vendor splits (plotly 4.9 MB, pdfmake 1.9 MB, recharts 554 kB, leaflet 162 kB) — `AppRoutes.jsx:18-29` `React.lazy` |
| M1 secrets in `react-frontend/.env` | **Fixed** | only 3 `VITE_` vars remain |
| M2 simulations 500-vs-404 | **Fixed** | `simulations.py` catches `.single()` empty → 404 (lines 123-139, 170-176, 223-238) |
| M3 role/ban cache delay | **Fixed** | `admin.py` calls `cache_delete_sync` on auth keys at lines 291, 342-343, 377, 499-501 |
| M5 dead routers unguarded | **Fixed** | `etl.py` has `Depends(require_admin)` (46,79,91); `chat.py` guarded (109,185,207) — both still disabled in `api.py` |
| M6 CORS regex | **Fixed in code** / **open in prod** — see M1 |
| L1 `municipality_id=-5` | **Fixed** | `Field(ge=0)` `simulations.py:27` |
| L2 label `<script>` | **Fixed** | `_sanitize_label` strips `<>` `simulations.py:17-22` |
| L4 missing profile fail-open | **Fixed** | deny on PGRST116, `auth.py:243-249` |
| L7 `auth.get_user` per request | **Fixed** | per-token claims cache, 60s TTL, `auth.py:103-140` |

## Verified clean / working

| Area | Evidence |
|---|---|
| impeccable detector | `detect --json react-frontend/src` → **0 findings** (exit 0) |
| Frontend tests | **71/71 pass** (10 files) incl. i18n-keys + theme-contrast CI tests |
| Backend tests | **121/121 pass** (fresh venv; 2 needed `pytest-asyncio` — see L11) |
| Production API | `health/` 200, `ecosim/municipalities` 200 (**1,600 items**), `energyhub/overview` 200 — ~2-4s cold-start |
| Route guards | protected 6/6, admin 19/19, simulations 5/5 guarded; public routers are read-only + quota-gated (`get_*_optional_user_or_quota`) |
| Forecast access | premium/admin only, `forecast.py:31-44` |
| Rate limiting | 60/min global, localhost-exempt, direct-peer-IP (XFF-spoof-safe) |
| Security lint | `0025`: security_invoker views, RLS on atlas/era5 tables, DEFINER EXECUTE revoked, storage listing policies scoped; `is_admin` residual documented |
| Images/alt | all `<img>` carry alt (avatar `alt=""` decorative — correct) |
| Focus rings | `focus-visible:ring-2` on shared button/input primitives |
| XSS sinks | no `dangerouslySetInnerHTML`; react-markdown default-escaped |
| Feature completeness | PDF export, autosave setting + migration 0023, MFA pages, dark theme, en/fil toggle, saved sims, DOE provider cards — all present in code |

## Not tested (explicit limits)

- **Browser-visual pass** — no browser automation in this environment; UX findings are code-level (impeccable critique ran dual-assessment; detector clean; browser overlay skipped, fallback documented).
- **Auth'd flows end-to-end** — signup/OAuth/MFA/email delivery not exercised (no throwaway account created; production Supabase untouched).
- **LLM paths** — Gemini/Groq/RAG not invoked (quota conservation); verified statically.
- **Sustained load**, **mobile physical devices**, **EcoSim formula correctness** (math sanity-checked, not re-derived).

## Skills applied (traceability)

| Lifecycle skill | Applied to | Output |
|---|---|---|
| interview-me | Requirement clarification (deliverable/scope/mechanics Q&A) | This run's scope decisions |
| idea-refine | PSC XI entry stress-test | Concept note §2/§6 framing, gap analysis |
| spec-driven-development | Concept note structure | `02-concept-note-draft.md` |
| planning-and-task-breakdown | Work-item slicing | `03-improvement-work-items.md` slices |
| api-and-interface-design | Route/error-semantics review | M5, L-findings on API consistency |
| frontend-ui-engineering + **impeccable** (`context`,`critique`,`audit` refs, `detect`) | Judge-facing UX axis | Design review (Nielsen 28/40), detector-clean verdict |
| incremental-implementation | Slice ordering in work items | Commit-per-slice plan |
| test-driven-development | Test coverage review | Verified 71/71 + 121/121; i18n CI check exists |
| debugging-and-error-recovery | Root-cause on 401/CORS/pytest | M1 root cause, quota mechanics |
| security-and-hardening | Prior-audit re-verification + threat checks | Re-verification table, M1/M2 |
| observability-and-instrumentation | Telemetry gap analysis | M4 |
| performance-optimization | Bundle/backend measurement | H3-verified, bundle table, API latency |
| code-simplification | Dead-code sweep | L9/L10 |
| documentation-and-adrs | Deliverable authoring | This folder |
| code-review-and-quality | Five-axis review lens | Findings severity structure |
| git-workflow-and-versioning | Slice/commit conventions | Work-items header |
| deprecation-and-migration | Dead routers/pages/clients | L9 |
| shipping-and-launch | Readiness framing | Verdicts + `04-submission-checklist.md` |

## Recommended fix order

1. **H1** — public `/ecosim` + quota copy in wizard (PSC demo blocker).
2. **H2** — decide and ship the financial-impact card + BOM, or document the withholding.
3. **M1** — set `ENVIRONMENT=production` + `CORS_ORIGINS` on Vercel; re-probe.
4. **M3** — fil.json `explanationTitle` object parity.
5. **M2/M4** — `npm audit fix` + Sentry/uptime before real-user testing.
6. LOW tail — L1-L3 UX blockers next (they hit the same judge path).
