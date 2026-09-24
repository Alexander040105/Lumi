# LUMI Improvement Work Items (PSC-XI-prioritized, skill-tagged)

Implementation backlog generated from `01-evaluation-report.md`. Same genre as
`docs/megaplan-it-feedback.md`: each item has root cause, file references, concrete change, and
acceptance criteria. **Every item is tagged with the agent-skill that governs it** — a follow-up
implementation session should load that SKILL.md before starting the item.

Commit convention: one slice per commit, concise message + `Generated with
[Devin](https://devin.ai)` / `Co-Authored-By` trailer.

Ordering rationale: **Slice 1 unblocks the judge demo, Slice 2 makes the demo persuasive, Slice 3
closes launch blockers, Slice 4 is polish.** Verify every file:line before editing — numbers drift.

---

## Slice 1 — Judge-demo unblocking (PSC XI critical path)

### W1 — Public EcoSim access + honest quota UX `[skill: frontend-ui-engineering]`

**Root cause:** `AppRoutes.jsx:72-85` wraps `/ecosim` (and `/energyhub`) in `ProtectedRoute`, while
the backend already supports anonymous runs via `get_ecosim_optional_user_or_quota`
(`quota.py:150-191`). The anonymous path is unreachable from the UI; UI copy for
`remaining_anonymous_requests` already exists.

**Change:**
- Remove `ProtectedRoute` from `/ecosim` (and `/energyhub` if the team wants it public).
- Keep auth gates on *saving*: the save button keeps the login-required flow for guests.
- Surface quota honestly in the wizard: when `remaining_anonymous_requests` is present, show
  "You have N free estimate(s) today — sign up for more" near the run button; on the 401 quota
  response, route to a friendly login wall that says *why* ("You've used today's free estimate —
  create a free account to keep going") rather than a bare form. New i18n keys in `en.json` +
  `fil.json`.
- Raise `anonymous_ecosim_quota` from `1` to a demo-sane value (e.g., 3–5 per window) in settings
  or env — CGNAT means shared-IP users otherwise get nothing (`settings.py:71`).

**Acceptance:** a logged-out visitor can land → pick municipality → run one simulation → see
results; the save path asks for login; quota exhaustion shows the friendly wall; no console errors.

### W2 — Landing page: CTA hierarchy + specificity `[skill: impeccable shape]`

**Root cause:** hero primary CTA "Explore Energy in my Area" routes to `/energyhub` (analyst tool),
not `/ecosim` (homeowner tool) — `Home.jsx:150-155`. Stats strip carries vague values
("10K+ data points", "Real-time" as a stat value) — `Home.jsx:165-181`. Nothing above the fold
previews the per-municipality differentiator.

**Change:** point the primary CTA at `/ecosim` (post-W1 this is guest-reachable); make EnergyHub a
secondary/"for planners" CTA. Replace vague stats with verifiable ones (1,600 municipalities,
2003–2024 DOE data span, 4 renewable sources, EN/FIL). Add a thin "what you'll get" strip or inline
mini-preview above the fold if cheap — the differentiator should be visible in the first screen.

**Acceptance:** primary persona's first click reaches EcoSim; every stat on Home is literally
verifiable; no fabricated claims.

## Slice 2 — Make the demo persuasive

### W3 — Decide + ship the financial layer `[skill: impeccable clarify]` + `[skill: spec-driven-development]`

**Root cause:** `EcosimBOM.jsx` is unmounted (zero imports); `EcosimResults.jsx:457` withholds the
comparison "until financial modeling is reliable"; `financial.*`/`lcoe.*`/`productRecs.*` strings
exist in both locales but render nowhere; PDF prints the numbers (`ecosimPdf.js:790-821`).

**Change (decision required — product call, not a bug):**
- **Option A (recommended for PSC):** render a "Your Financial Impact" card under the hero —
  current bill → est. new bill → monthly ₱ savings → install cost → payback — hedged per the
  "estimates, not promises" voice (existing `costNote` copy); mount `EcosimBOM` behind the existing
  expandable/technical pattern. Numbers already come back in the API response.
- **Option B:** keep hidden, but then remove the money promise from landing copy and document the
  decision in `docs/` — ambiguity is worse than either choice.

**Acceptance:** a judge sees ₱-denominated savings/cost/payback on screen (hedged), or the promise
is verifiably de-scoped everywhere it's implied.

### W4 — Judge-path UX blockers `[skill: impeccable clarify]` (L1+L2+L3 combined)

**Changes:**
- `Ecosim.jsx:179-182`: do **not** auto-select `items[0]`; leave the municipality empty with the
  placeholder doing the work (prevents silent wrong-town runs).
- `EcosimWizard.jsx:31`: when Next is disabled on step 2, show the inline reason and the
  computed-rate rescue — never a dead button with no explanation. Align `billGuide` row order with
  field order (`en.json:1039-1042` vs fields at `EcosimWizard.jsx:243-257`).
- `EcosimWizard.jsx:401-417`: always render "Save as PDF" — disabled with a "waiting for analysis"
  caption while AI polls; duplicate the action row at the bottom of `EcosimResults` for mobile.

**Acceptance:** no silent disabled states on the demo path; actions reachable after results on a
phone-sized viewport; no auto-selected municipality.

### W5 — Results-page ending + step identity `[skill: impeccable polish]`

- Render localized step names (`wizard.steps.step1-5` exist unused) in the progress indicator.
- Drop or downgrade the completion modal (it scrolls behind itself, `Ecosim.jsx:291-299`) to an
  inline "estimate ready" banner; localize `recommended_source` values ("Hydropower" is raw
  English at `Ecosim.jsx:686`).
- Ensure "next steps" (get 3 quotes / net metering) is the visible ending — move it above the
  technical-details toggle.

**Acceptance:** run end-state reads as a complete advisor answer; no raw enums or unused i18n.

## Slice 3 — Launch blockers / ops hardening

### W6 — Production env + CORS `[skill: security-and-hardening]` + `[skill: shipping-and-launch]`

**Root cause:** deployed backend returns `Access-Control-Allow-Origin: http://127.0.0.1:5173` with
credentials (verified live 2026-09-24). `settings.py:27-32` defaults `cors_origins` to include
localhost and `environment` to `development`; `main.py:76-80` only drops localhost under
`ENVIRONMENT=production`.

**Change:** Vercel env: set `ENVIRONMENT=production` and explicit `CORS_ORIGINS` (prod + preview
naming only, no localhost). Code hardening: in `parse_cors_origins`, strip localhost entries from
the default list when `environment == "production"` (defense-in-depth). Re-probe with a fake and a
localhost `Origin` header — expect no allow-origin on both.

**Acceptance:** prod rejects localhost origins; preview/prod origins still work; re-verification
probe documented.

### W7 — Error tracking + uptime `[skill: observability-and-instrumentation]`

**Root cause:** no Sentry-class tracking; only `@vercel/analytics` + server logs. Silent prod
failures are invisible during user testing / judging.

**Change:** add Sentry (frontend + FastAPI integrations — free tier suffices) or minimally Vercel
log drains + an uptime ping against `/health/detailed`. Add `VITE_`/backend env vars; do not commit
secrets.

**Acceptance:** a forced test error appears in the tracker with request-id correlation; uptime
check runs on a schedule.

### W8 — Dependency audit + test-env fix `[skill: ci-cd-and-automation]`

- `npm audit fix` (non-breaking) → 4 vulns (2 critical: maplibre-gl via plotly, vitest mocker).
  If maplibre can't upgrade through plotly, pin `plotly.js` upgrade or evaluate
  `plotly.js-basic-dist` (shrinks the 4.9 MB lazy chunk too — note perf overlap).
- Add `npm audit --audit-level=high` to CI.
- Add `pytest-asyncio` to `fastapi-backend/requirements.txt` (2 async tests silently need it;
  fresh-env runs fail without it).
- README: use `py -m venv` on Windows (no `python` alias on this machine).

**Acceptance:** `npm audit` shows 0 critical; `pytest tests/` green in a clean venv per README
steps.

### W9 — `fil.json` explanationTitle parity `[skill: frontend-ui-engineering]` (i18n)

`fil.json:902` `energyHub.map.explanationTitle` is a flat string; `en.json:883` is a 5-key object
resolved per metric at `MapExplanationCard.jsx:82`. Mirror the object shape with Filipino titles.
Add the structural-mismatch case to `i18n-keys.test.js` (compare value *types* per key, not just
presence).

**Acceptance:** Filipino map cards show per-metric titles; type-parity test catches future drift.

## Slice 4 — Polish tail (post-demo, pre-launch)

### W10 — Keyboard-complete SearchableSelect `[skill: impeccable audit]` fix

`SearchableSelect.jsx:29-59`: add ArrowUp/Down/Enter/Escape + `aria-activedescendant`; the core
control currently fails WCAG keyboard requirements. Alternatively port to the Radix combobox
pattern already in the stack.

### W11 — i18n polish leaks `[skill: impeccable harden]`

Strip/render the literal `**` in `en.json:1034-1035` (via Markdown component); fix `fil.json:1014`
typo; remove redundant hardcoded EN fallbacks at `EcosimWizard.jsx:398,414`; set
`document.documentElement.lang` on locale switch (`en`/`fil`); add retry UI for
municipalities-load failure.

### W12 — Dead code removal `[skill: deprecation-and-migration]` + `[skill: code-simplification]`

Remove or document: unrouted `MapPage`, `ChatPage`, `ProfilePage`, `AdminModeration`; dead
apiClient functions (`createItem`, `runClimateEtl`, `getLineage`, `sendChatMessage`,
`getChatSessions`, `getChatSessionMessages`); unused `Table` import + `comparisonMax` in
`Ecosim.jsx`. `expo-mobile/` stays untouched (documented non-shipping scaffold).

### W13 — API consistency + FastAPI lifespan `[skill: api-and-interface-design]`

`forecast.py:61-62`: return proper status code instead of `{"error":…}` with 200; expose a public
readiness method instead of `ml._historical`. `main.py:96`: migrate `on_event("startup")` to the
lifespan API (deprecation warning fires on boot).

### W14 — Navbar Sheet + logo single-source `[skill: frontend-ui-engineering]`

Move the mobile menu to `components/ui/sheet.jsx` (Escape/focus management per DESIGN.md);
reconcile `/logo.png` vs `/lumi-logo.png` to one brand asset.

---

## Non-goals (explicit)

- No changes to simulation math/scoring — correctness audit of formulas is a separate, deeper task.
- No re-implementation of chat/ETL routers — they stay disabled.
- No fabricated metrics anywhere — `[TEAM INPUT]` markers stand until the team supplies real values.
- Meralco `meralco_rate` card and province-mode hidden code paths stay as-is (stakeholder decisions).
