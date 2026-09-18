# Megaplan: IT Experts Feedback Implementation (SWE-2 Max Prompt)

You are implementing a batch of user-feedback fixes and stakeholder revisions for **Lumi**, a
Philippine renewable-energy decision-support app. Work through the items below in the suggested
slice order, commit each slice separately, and verify with the commands at the end.

Everything you need is in this document — root causes are already identified with file and line
references. Verify each reference before editing (line numbers may drift slightly).

---

## 1. Repository orientation

- **Frontend**: `react-frontend/` — React 18 + Vite, Tailwind CSS 4, shadcn-style primitives in
  `src/components/ui/` (includes `dialog.jsx`, `button.jsx`, `card.jsx`, `input.jsx`), toasts via
  `sonner`, routing in `src/routes/AppRoutes.jsx`, Supabase client at `src/services/supabaseClient.js`,
  backend calls via `src/services/apiClient.js`.
- **Backend**: `fastapi-backend/` — FastAPI; routes in `app/routes/`, services in `app/services/`,
  Supabase via `app/services/supabase_service.py`.
- **Database/Auth**: Supabase Postgres + GoTrue. Schema dumps in `supabase/schema_structure/`,
  numbered migrations in `supabase/migrations/` (latest is `0022`; new migrations go next).
- **i18n**: `react-frontend/src/i18n/en.json` and `fil.json`. Every new or changed user-facing
  string needs a key in **both** files. Interpolation syntax is `{{var}}`.
- **Run locally**: `npm run dev` at repo root (starts Vite + `uvicorn main:app --reload --port 8000
  --app-dir fastapi-backend` concurrently).
- **Tests**: `cd react-frontend && npm run test:run` (vitest + testing-library);
  `cd fastapi-backend && python -m pytest tests/`.

### Original feedback being addressed (context, verbatim-condensed)

**IT experts (Google Forms):**
1. No confirmation email after signing up with an email already registered via "Continue with Google".
2. "Select a municipality" dropdown in the dashboard is tedious — needs a search box.
3. Duplicate municipality names in the dropdown (Burgos ×6, Carmen ×6, Buenavista ×5, ...) — confusing.
4. Several municipalities show "Composite Renewable Score" of 0/100 — unclear if real or broken.
5. "Saved Locations" exists on the dashboard but there is no way to save a location.
6. EcoSim runs are not saved automatically; tester expected results in the dashboard. There is a
   manual save button, but an **autosave account setting (default ON)** was requested.
7. Check whether 2FA works without QR; guide users through Microsoft/Google Authenticator; explore
   what other 2FA options the current setup allows.
8. Results should be visible immediately after a run (auto-scroll) — may already be fixed; verify.

**Sir Kenneth's revisions:**
1. Choose by city only — hide the province option in the EcoSim interface (do NOT delete the code).
2. Step 2 of EcoSim: fix label alignment so fields line up evenly.
3. Remove the Meralco bill image; replace with provider-agnostic guidance on where to find each
   value on any Philippine electric bill. DO NOT hide this behind a toggle — dedicated visible spot.
4. Step 3: remove the duplicated question "How much would you like to reduce your monthly
   electricity bill?", fix formatting, and add a NEW step after it so "Include simple explanation"
   gets a dedicated step.
5. (Skipped — out of scope.)
6. Make things less text-heavy and more user-centric.
7. Turn the "Why this estimate looks this way" dropdowns into modals.

---

## 2. Work items

### A1 — Signup with an already-registered (Google) email

**Root cause**: `supabase.auth.signUp` for an email that already exists returns success with a
`data.user` whose `identities` array is empty (Supabase anti-enumeration) and no session. The
wrapper in `react-frontend/src/context/AuthContext.jsx:131-148` then reports
`confirmationRequired: true`, and `react-frontend/src/pages/Login.jsx:263-277` shows the
"check your email" box — but Supabase never sends a confirmation because the account exists.

**Change**: Detect the empty-`identities` case in the signup flow (either in `AuthContext.signUp`'s
return value or in `Login.jsx` where `result.confirmationRequired` is handled). Instead of the
check-email box, show a distinct notice, e.g.:

> "An account with this email already exists. If you signed up with Google, use 'Continue with
> Google'. To also enable email/password sign-in, use 'Forgot password' to set a password."

Add i18n keys in `en.json` and `fil.json`. Genuine new signups keep the existing confirm-email box.

**Acceptance**: Signing up with a Google-OAuth email shows the account-exists notice (no false
"email sent" claim); a brand-new email still shows the confirmation-sent box.

---

### A2 — 2FA setup instructions (MFA page)

**Root cause**: `react-frontend/src/pages/MFASetup.jsx` renders a QR image (`enrollment.totp.qr_code`,
lines 207–213) and the raw secret (lines 214–216) with no instructions. Manual entry already works —
the secret is displayed — but users aren't told that, or which app to use.

**Change**: In the enrollment card, add a numbered how-to list covering both **Microsoft
Authenticator** and **Google Authenticator**: install app → add account → scan QR. Add a
"Can't scan the QR code?" path telling the user to choose manual/setup-key entry in their app and
paste the secret; add a copy-to-clipboard button for the secret (optionally expose
`enrollment.totp.uri`). Keep the existing no-recovery-codes warning. Add one line explaining what
happens at login (enter the current 6-digit code after password).

Also record (code comment or a short docs note in `docs/`) the alternatives audit: Supabase Auth as
configured supports **TOTP only**; SMS/WhatsApp MFA would require a paid Twilio Verify integration —
out of scope. Recommendation: keep TOTP.

**Acceptance**: Enrollment card shows step-by-step instructions for both named apps, a copyable
manual secret, and the recovery warning. Manual-entry path works with Microsoft Authenticator.

---

### B1 — Dashboard municipality picker → searchable combobox

**Root cause**: `react-frontend/src/pages/Dashboard.jsx:347-358` uses a plain `<select>` populated
with `.select("municipality_id, name").order("name").limit(500)` (lines 62–66) — no search, and
truncated (the Philippines has ~1,600 municipalities). Duplicate names show no disambiguation.

**Change**: Replace the `<select>` with the same searchable-dropdown pattern used in
`EcosimWizard.jsx:100-126` (search input + filtered scrollable list, cap ~50 visible rows +
"N more — refine your search" footer). Populate it from `getMunicipalities()` in
`src/services/apiClient.js` (backend `GET /ecosim/municipalities`, `fastapi-backend/app/services/
ecosim.py:293-345`) — it returns `{ municipality_id, name, province_name }` for the full set and is
server-cached. Render every option as `Name, Province` — this resolves the "duplicate names"
complaint: they are legitimately distinct municipalities (e.g., Burgos, Ilocos Norte vs Burgos,
Pangasinan); do NOT deduplicate rows.

Optional but welcome: extract the dropdown into `src/components/shared/SearchableSelect.jsx` and
reuse it in `EcosimWizard` — duplicating the pattern is acceptable if extraction gets messy.

**Acceptance**: Typing filters the list; every option shows `Name, Province`; all municipalities
are reachable (no 500-row cutoff); selection updates the score panel.

---

### B2 — Composite Renewable Score fix

**Root cause**: `fetchCompositeScore` in `Dashboard.jsx:105-125` queries
`solar_suitability.solar_score` and `wind_suitability.wind_score`, but those tables' columns are
named `score` (see `supabase/schema_structure/lumi_schema_latest.sql:1374-1380, 1484-1490`) — the
queries error out and each missing/errored value silently becomes `|| 0`. Meanwhile
`municipalities.composite_suitability_score` already holds the precomputed composite
(schema line 832).

**Change**: Replace the 4-table fan-out with a single read of `composite_suitability_score` (and
optionally `composite_classification`) from `municipalities`. When the value is NULL, render an
explicit "No suitability data yet for this municipality" state (new i18n key) — never show 0/100
for missing data. When numeric, show the score + `Progress` bar as today. Update
`dashboard.compositeDescription` copy if needed.

**Acceptance**: A municipality with data shows its real score; one without shows the explicit
no-data state. No silent 0/100.

---

### B3 — Saved Locations: write path + deep-link fix

**Root cause**: `saved_locations` is only ever read (`Dashboard.jsx:71-81`); nothing inserts. Its
"Open" links point to `/ecosim?municipality=<id>` (`Dashboard.jsx:417`), but `Ecosim.jsx:210` only
reads `?simulation_id=` — the deep link is dead.

**Change**:
- In the Dashboard overview card, when a municipality is selected, show a "Save this location"
  button → `insert` into `saved_locations` with `user_id`, `municipality_id`, and `label` =
  "Name, Province". The unique constraint `(user_id, municipality_id)` (schema line ~1678) will
  reject duplicates — catch the conflict (PostgREST 409 / code 23505) and toast "already saved"
  instead of an error.
- Add a small delete/remove control per item in the Saved Locations list (RLS delete-own policy
  exists — `supabase/migrations/0009_rls_hardening.sql`).
- In `Ecosim.jsx`, consume `?municipality=<id>`: after municipalities load, set `municipalityId`
  and `muniQuery` (use the `Name, Province` form) — mirror the existing `?simulation_id=` loader
  pattern at lines 209–264.
- Stretch (only if trivial): a bookmark button on the wizard's "Selected:" chip
  (`EcosimWizard.jsx:147-151`).

**Acceptance**: User can save, list, open (lands in EcoSim preselected), and remove locations;
duplicate saves don't error.

---

### C1 — Hide province mode in EcoSim (reversible)

Sir Kenneth: choose by city only. Per stakeholder direction, **hide — do not delete** — the
province path.

**Change**: In `EcosimWizard.jsx` step 1 (lines 87-153), stop rendering the mode toggle
(`searchMode` block, lines 89-98) and the province search branch; gate it behind a clearly-named
flag (e.g., `const ENABLE_PROVINCE_MODE = false;`) so re-enabling is a one-line change. Keep
`mode` state, the `getProvinces` fetch, `filteredProvinces`, and the backend `mode` param intact —
everything continues to work if flipped back on. Leave the province i18n keys in place.

**Acceptance**: Step 1 offers only city/municipality search; no console errors; `mode` stays
"municipality" in API calls.

---

### C2 — Step 2: provider-agnostic bill guidance + label alignment

**Root cause**: `EcosimWizard.jsx:158-165` renders `public/MeralcoBillWithBoxes.png`; per-field help
is hidden behind three `BillHelpModal` toggles (lines 170, 182, 194) which themselves embed the same
image (`components/shared/BillHelpModal.jsx:36-40`). i18n copy says "Meralco bill"
(`en.json:811, 830, 836, 840-846, 873-874`). The three `md:grid-cols-3` fields have uneven
label-row heights → misaligned inputs.

**Change**:
- Remove the image block and all `BillHelpModal` triggers. `BillHelpModal.jsx` becomes unused —
  delete it. Remove `public/MeralcoBillWithBoxes.png` once no references remain.
- Add an always-visible panel on step 2 titled "Where to find these on your bill": a compact
  3-row guide mapping each input to what to look for on ANY Philippine electric bill:
  - kWh used → "Actual Consumption" / metered kWh for the billing period
  - Total bill → "Total Amount Due" / "Current Charges" (before subsidies or discounts)
  - Rate per kWh → "Generation Charge" or effective ₱/kWh; if not printed, divide bill ÷ kWh
- Reword Meralco-specific i18n strings to provider-neutral ("your electric bill") in en + fil.
- Fix alignment: give each field a uniform structure (e.g., `min-h-[2.5rem]` on the label row,
  consistent hint placement) so the three inputs line up horizontally.

Note: the `meralco_rate` results card (`EcosimResults.jsx:327-349`) is a separate data feature shown
only for franchise areas — leave it.

**Acceptance**: No Meralco image or hidden help toggles; the always-visible guide names exactly
what to find on any provider's bill; the three inputs are visually aligned.

---

### C3 — Step 3 dedupe + new dedicated "simple explanation" step

**Root cause**: `en.json:812` `stepDescriptions.step3` and `en.json:848` `savingsLabel` are the same
sentence. The `includeAi` checkbox ("Include simple explanation") sits inside step 3
(`EcosimWizard.jsx:256-267`).

**Change**:
- Change `stepDescriptions.step3` to a distinct line (e.g., "Choose how much of your bill
  renewable energy should cover."). Keep `savingsLabel`. Fix step-3 layout/formatting.
- `totalSteps` 4 → 5 (`EcosimWizard.jsx:20`). New **step 4 = "Explanation"**: holds the includeAi
  checkbox plus a one-line preview of what it adds. Old step 4 (Review) becomes step 5.
- Update: `wizard.steps` keys (step4 = Explanation, step5 = Review), `stepDescriptions`, the icon
  map in `CardTitle` (lines 76-79), `canProceed`, and the summary card edit-targets
  (`aiAnalysis` → step 4; savings stays → step 3).
- Mirror all string changes in `fil.json`.

**Acceptance**: Wizard shows 5 steps; the question appears once on step 3; "Include simple
explanation" has its own step; review step still edits correctly.

---

### C4 — Autosave EcoSim runs + account setting (default ON)

**Root cause**: Saving is manual-only via the save dialog (`Ecosim.jsx:401-460`). The stakeholder
wants autosave, controlled by an account setting defaulting to ON.

**Change**:
- **Migration** `supabase/migrations/0023_profiles_ecosim_autosave.sql`:
  `alter table public.profiles add column if not exists ecosim_autosave boolean not null default true;`
  Flag in your final notes that this migration must be applied to the Supabase project.
- **Backend** `fastapi-backend/app/routes/protected.py`: add
  `ecosim_autosave: bool | None = None` to `ProfileUpdatePayload` (it uses `extra = "forbid"` —
  without the field, PUT 422s). Verify `GET /protected/profile` returns the new column.
- **Settings UI**: add a "Preferences" (or "EcoSim") card in `react-frontend/src/pages/
  SecuritySettings.jsx` (route `/settings/security`) with a toggle "Automatically save my EcoSim
  runs" → `PUT /protected/profile { ecosim_autosave: bool }` → toast on success/failure.
- **Ecosim.jsx**: after a successful run (`setResult(data)` in `handleSubmit`), if
  `user && profile?.ecosim_autosave` → auto-POST `/simulations` with the existing default-label
  format. Refactor `handleSaveSimulation` so manual and auto paths share one
  `saveSimulation(label)` helper. On success: toast "Saved to your account" with a View link to
  `/saved-simulations`. On 403 save-limit: show the upgrade/limit toast, never break the run.
  Suppress the manual "Save to Account" button once auto-saved (track saved state per result), and
  skip autosave when results were loaded via `?simulation_id=`. Guests keep the existing
  login-required behavior.
- `AuthContext` already fetches the profile via `/protected/profile` — `profile.ecosim_autosave`
  will be available once the backend returns it.

**Acceptance**: Fresh account (default ON): run → appears in `/saved-simulations` + toast. Toggle
OFF → runs aren't saved; manual save still works. Guests unaffected.

---

### C5 — "Why this estimate looks this way" → modals

**Root cause**: These are `<details>` dropdowns in `EcosimResults.jsx` — once in the comparison list
(lines 309-317) and again per technical output card (lines 428-437). Key:
`ecosim.results.aiExplanation`.

**Change**: Replace both with a `Dialog`-based modal (reuse `components/ui/dialog.jsx`): a subtle
trigger button (keep the dotted-underline style) opens a modal rendering the explanation via the
existing `Markdown` component. Implement one shared `ExplanationModal` (title + content props);
manage open state at the `EcosimResults` level.

**Acceptance**: Both explanation entry points open a readable modal; no `<details>` left for these;
content identical.

---

### C6 — Reduce text-heaviness on the EcoSim flow

Bounded pass — target ≈40% less visible body copy, never delete the required disclaimer:

- Condense the top "Important:" disclaimer card (`Ecosim.jsx:517-525`) to one line plus a "Why?"
  expandable/modal for the full text.
- Shorten wizard `stepDescriptions` to ≤1 line each.
- `whyRecommended.locationText` currently renders `Municipality — ID {id}`
  (`en.json:920`, used at `EcosimResults.jsx:196`) — show "Municipality, Province" instead of the
  raw ID.
- Trim redundant `CardDescription`s where the content already explains itself.

**Acceptance**: Noticeably lighter page; disclaimer still accessible; nothing informative lost —
just relocated into tooltips/modals.

---

### C7 — Verify results auto-scroll

`Ecosim.jsx:266-272` already opens the completion dialog and calls `scrollIntoView`; the dialog's
"View results" button scrolls again (line 629). Verify in a real browser run that the user lands on
the results without manual scrolling; if the modal opening swallows the scroll, scroll on dialog
open or defer until it's dismissed.

**Acceptance**: After a run completes, the user sees the results without needing to scroll.

---

## 3. Explicit non-goals

- Kenneth item 5 ("Upper right yung question mark, slider, image, explanation") — deferred by
  stakeholder.
- SMS/WhatsApp/passkey MFA — not supported by the current Supabase setup (TOTP only).
- Deleting province-mode code paths — hidden, not removed (C1).
- Deduplicating the `municipalities` table — shared names are legitimate distinct rows.
- Changing `meralco_rate` data/backend scoring, or admin features.

---

## 4. Suggested slice order (commit each slice separately)

1. **Dashboard**: B1 + B2 + B3 — picker, score, saved locations.
2. **Wizard**: C1 + C2 + C3 — hidden province, step 2 rework, 5-step flow.
3. **Results**: C5 + C6 + C7 — modals, de-cluttering, scroll verify.
4. **Auth**: A1 + A2 — signup message, 2FA instructions.
5. **Autosave**: C4 — migration + backend + settings + EcoSim (needs the DB migration applied;
   call it out in the final summary).

Use the repo's commit convention: concise message + `Generated with [Devin](https://devin.ai)` /
`Co-Authored-By` trailer.

---

## 5. Verification

- `cd react-frontend && npm run test:run && npm run build` — green.
- `cd fastapi-backend && python -m pytest tests/` — green (run if backend touched).
- Manual browser pass (`npm run dev` at root):
  1. Sign up with an existing Google-OAuth email → account-exists notice, no fake confirm.
  2. Dashboard: combobox search filters; `Name, Province` labels; real or explicit-no-data score;
     save → open → remove a location (open lands in EcoSim preselected).
  3. EcoSim: 5 steps; bill guide always visible; aligned fields; explanation modals; auto-scroll
     to results; autosave toast + entry in `/saved-simulations`; toggle off stops autosave.
  4. MFA page: instructions + copyable secret; verify a code from Microsoft Authenticator.

---

## 6. Constraints

- Both `en.json` and `fil.json` updated for every string change (`{{var}}` interpolation).
- Reuse existing primitives (`dialog.jsx`, `sonner`, `apiClient.request`) — no new dependencies
  unless strictly necessary.
- Backend `mode` param, `simulations` API, and saved-simulation `mode` values stay compatible.
- Follow existing code style: compact, no unnecessary comments, Tailwind utility classes.
- Do not commit secrets or touch `.env` files.
