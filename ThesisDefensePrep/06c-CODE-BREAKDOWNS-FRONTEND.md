# 06c — Code Breakdowns: Frontend

> Logic walkthrough for every cited `react-frontend/src` file. React component breakdowns describe
> render structure → state/hooks → handlers → what the user sees/does. Same uniform template.
>
> **TOC:** [Entry & shell](#entry--shell) · [Pages](#pages) · [Admin pages](#admin-pages) ·
> [Services & data layer](#services--data-layer) · [Utils](#utils) · [Context/hooks/i18n](#contexthooksi18n) ·
> [Ecosim components](#ecosim-components) · [EnergyHub components](#energyhub-components) ·
> [Shared components](#shared-components) · [Layout](#layout) · [Admin components](#admin-components) ·
> [UI primitives](#ui-primitives) · [Data files](#data-files)

---

## Entry & shell

### `main.jsx` (20 ln) — bootstrap
- Renders `<App/>` into `#root` w/ StrictMode; imports `styles/globals.css` (Tailwind 4 + theme tokens).

### `App.jsx` (14 ln) — root component
- `export default App` — wraps providers (`I18nProvider`, `ThemeProvider`, `AuthProvider`) + `AppRoutes` + `ErrorBoundary`.

### `routes/AppRoutes.jsx` (166 ln) — route table
- **Logic:** `lazy()` imports per page (code-splitting) → `<Routes>`: public (`/`, `/about`, `/privacy`, `/terms`, `/login`, `/auth/callback`, `/reset-password`) → `ProtectedRoute`-wrapped (`/dashboard`, `/ecosim`, `/energyhub`, `/saved-simulations`, `/mfa-setup`, `/security`, `/profile`) → `AdminRoute`-wrapped (`/admin/*`) → `NotFound`.
- **Tie:** `ChatPage` is absent from the table — proof of the dormant surface (W8). Deep links `?municipality=`/`?simulation_id=` handled inside pages.

### `layouts/MainLayout.jsx` (16 ln) — page shell
- Renders `Navbar` + `<Outlet/>` + `Footer` — chrome around every routed page.

## Pages

### `pages/Home.jsx` (344 ln) — landing
- Sub-components: `SectionHeading`, `FeatureCard`, `StepCard`, `EnergyTypeCard` (per-source card w/ `citationIds` → `data/references.json`). `Home` composes hero → features → how-it-works → energy types → CTA. Citations rendered inline → S1 marketing-style but sources are real.

### `pages/About.jsx` (343 ln) — about/methodology
- `SectionHeading`/`ValueCard`/`TechItem` + `About` — narrative about the system, tech list, values.

### `pages/Dashboard.jsx` (542 ln) — municipality dashboard
- **State:** profile + edit form, `savedLocations`, `savedSimulations`, `municipalities`(+error), picker (`muniQuery`/`muniOpen`/`selectedMuni`), composite score card.
- **Logic:** on mount → load profile + saved lists + municipality list (coverage-filtered) → `SearchableSelect` pick → fetch dashboard data → composite-score card; save/remove location via `savedLocations.js`; deep-link `?municipality=` preselects.
- **Tie:** S11's entry surface; "real composite score" added in expert-feedback round (`4b485a0`).

### `pages/EnergyHub.jsx` (364 ln) — EnergyHub host
- **State:** overview/trends/mapData/sourceBreakdown/insight frames, `mapMetric`+`mapLevel`, `useLlm` toggle, per-chart `chartAnalyses` + `llmLoading` flags.
- **Logic:** mount → parallel `energyhub.js` calls → render `EnergyOverview`, `EnergyTrends`, `EnergyMap`, `ProvincialDemand`, `AiInsightPanel`; map control refetches `getEnergyHubMapData(metric, level)`; `onAnalyzeChart` posts chart JSON → cached insight; LLM toggle switches static↔LLM insight.
- **Tie:** SO1/SO3 UI; static-first AI = page works fully without LLM.

### `pages/Ecosim.jsx` (742 ln) — EcoSim host + wizard flow
- **State:** `mode` (municipality/province), geo pickers ×2 (query/open/selected per level), `monthlyConsumption`, bill, `desiredSavings`, `dataSource`, results object, AI state (loading/pending/failed/retry), autosave flag.
- **Logic:** load pickers (coverage-filtered lists) → `EcosimWizard` steps collect inputs → POST `/ecosim/` → `EcosimResults` + `EcosimBOM` + `ExplanationModal`s + `ProviderRecommendations` → optional `/ecosim/ai` call w/ **status polling** (`53649f4`: pending → poll visibility-aware until summary lands) → if authenticated + `profile.ecosim_autosave` → auto-POST saved simulation → PDF export via `ecosimPdf.js`.
- **Tie:** S13–15 entire flow; AI polling explains the "~7 s live / ~1.9 s cached" UX.

### `pages/SavedSimulations.jsx` (173 ln) — saved runs list
- Load list → render rows (label, geo, date, source) → open (deep-links back into Ecosim) / delete.

### `pages/Login.jsx` (345 ln) — auth entry
- **State:** `mode` (login/signup), email/password/confirm, `signupStatus` (`confirm|auto|exists` — anti-enumeration UX), `mfaRequired`/`mfaFactorId`/`mfaCode` (TOTP challenge inline).
- **Logic:** submit → `AuthContext.login/signup` → on session → `checkMfa` → factor present → show TOTP code field → `verifyMfa` → redirect. Google OAuth button → Supabase `signInWithOAuth` → `/auth/callback` return.
- **Tie:** S16; "account-exists" notice (commit `8446422`) gives UX without leaking whether an email is registered.

### `pages/AuthCallback.jsx` (76 ln) — OAuth/email landing
- **Logic:** parse URL (tokens/error) → session exchange → `checkMfa`/profile → redirect dashboard or login. Three `useEffect`s handle init/session-change/error paths. Commit `6fc9c76` made ALL auth emails land here (not `/login`).

### `pages/MFASetup.jsx` (262 ln) — TOTP enrollment
- **State:** `factors` (enrolled), `enrolling`, `verifying`, `enrollment` `{id, qr_code, secret}`, `code`, `unenroll {factorId, code}`.
- **Logic:** list factors → enroll (shows **QR image + manual secret + app guidance**) → verify 6-digit → enrolled. Unenroll requires a current TOTP code (can't be locked out silently).
- **Tie:** the TOTP-only 2FA UX (D14).

### `pages/SecuritySettings.jsx` (331 ln) — account security
- **State:** email/password change forms, delete-account (password confirmation), **`ecosimAutosave` toggle + `savingAutosave`**.
- **Logic:** each section PUTs `/protected/profile` or Supabase auth; autosave writes `profiles.ecosim_autosave` (migration 0023).

### `pages/ProfilePage.jsx` (255 ln) — profile editing
- Load profile → edit full_name/org/location → `PUT /protected/profile` → avatar upload → `POST /protected/sync-avatar`.

### `pages/ResetPassword.jsx` (78 ln) — password reset completion
- New+confirm password → Supabase `updateUser` → redirect login.

### `pages/ChatPage.jsx` (198 ln) — dormant chat UI
- `formatCitations` (footnote markers); state messages/input/isLoading/sessionId; load history → POST `/chat` → render exchange w/ citations. **Unrouted** — code present, no menu/route (W8).

### `pages/NotFound.jsx` (22 ln), `Privacy.jsx` (51 ln), `Terms.jsx` (52 ln) — static pages.

## Admin pages

All `pages/admin/*` — internal portal (NOT a defended feature; see `02` Part C):

- `AdminDashboard.jsx` (129 ln) — headline stats (users, simulations) fetch.
- `AdminUsers.jsx` (275 ln) — paginated user table: `search`, `filterRole`, `filterStatus`, offset pagination (LIMIT=50), `CreateUserModal`, `UserDetailDrawer`.
- `AdminAnalytics.jsx` (138 ln) — stats/charts feed (powered by `user_ecosim_logs`, migration 0015).
- `AdminConfig.jsx` (94 ln) — runtime-config form.
- `AdminUsage.jsx` (200 ln) — per-user usage report + drawer + CSV export.
- `AdminLogs.jsx` (193 ln) — audit-log viewer (action filter, pagination, export).
- `AdminModeration.jsx` (158 ln) — chat-session moderation (expandable rows).

## Services & data layer

### `services/apiClient.js` (277 ln) — HTTP client
- **Constants:** `DEFAULT_TIMEOUT_MS=30000`, `MAX_RETRIES=3`, `INITIAL_RETRY_DELAY_MS=500`.
- **Logic:** `generateRequestId` (per-call ID for support correlation); `sleep`; `fetchWithTimeout` (AbortController); `request(path, {token, timeoutMs, options})` — attach bearer + JSON headers → retry loop w/ **exponential backoff (500×2ⁿ ms)** → **skip retry on 429** (respects Retry-After) and on client errors → throw `ApiError(status, detail, requestId)`; typed helpers `getHealth`, `getProtectedMe`, `createItem`, etc.
- **Tie:** client-side resilience layer — the same degradation philosophy as the backend.

### `services/energyhub.js` (97 ln) — EnergyHub endpoints
- Thin wrappers: `getEnergyHubOverview/Forecast(metric)/Trends/MapData(metric,level)/SourceBreakdown/GridBreakdown/ModelComparison/AiInsight(useLlm)/GeothermalSummary/GeothermalPlants/ProvincialDemand(region)` — each → `request()`.

### `services/savedLocations.js` (17 ln) — saved locations
- `saveLocation({userId, municipalityId, label})` → Supabase insert (RLS: own rows only).

### `services/supabaseClient.js` (11 ln) — client singleton
- `createClient(url, anonKey)` — **anon key only**; used for auth + own-row CRUD under RLS.

### `utils/env.js` (45 ln) — env access
- `getSupabaseUrl/getSupabaseAnonKey/getCartoApiKey/getApiBaseUrl` — reads `VITE_*` w/ baked-in fallbacks (anon key is publishable-by-design; documented in security report).

### `utils/municipalities.js` (50 ln) — geo helpers
- `filterMunicipalities(items, query)` (name search), `formatMunicipalityLabel`, `haversineKm`, `nearestMunicipality` (geolocation picker — `2a17ce9`).

### `utils/ecosimAnalysis.js` (7 ln) — analysis resolver
- `resolveSourceAnalysis(result, key, fallback)` — pulls per-source text w/ graceful default.

### `utils/ecosimPdf.js` (1,027 ln) — PDF export (pdfmake)
- `COLORS`/`SOURCE_META`/`PDF_SUPERSCRIPTS`; `formatNumber/formatCurrency/formatPercent`; `slugify`, `sourceDisplayName`, `getSourceMeta`, `savingsLabel`; `normalizePdfText` (unicode→PDF-safe + superscripts); `parseMarkdownInline` (**bold/italic**→pdfmake inline chunks); document builder: summary → per-source cards → comparison → BOM → providers (`b004c64` Equipment Retailers section w/ regional filtering + disclaimer) → methodology/citations footer.
- **Tie:** S15 deliverable — a take-home PDF; bundled fonts (`dfb78f7` — dropped self-hosted Roboto TTFs).

### `utils/pdfFonts.js` (30 ln) — font loader
- `getPdfMake()` — lazy-loads pdfmake + `vfs_fonts` bundle on first export (keeps initial bundle small).

### `utils/matchProviders.js` (74 ln) — provider matching
- `normalizeTechnology`, `providerHasTechnology`, `providerCategory`, `byFitThenVerified` (sort: fit → DOE-verified), `matchProviders({providers, region, technology, category})` — provider-agnostic matching against `data/providers.json` (2026 DOE registry, `896843d9`).

### `utils/regionMap.js` (75 ln) — province→region lookup
- `PROVINCE_TO_REGION` map + `getRegionFromProvince/Municipality` — for regional provider filtering.

### `utils/glossary.js` (64 ln) — term glossary
- `GLOSSARY` dict + `getGlossary(term)` — powers `HelpTooltip` hover definitions (SO5).

### `utils/cssVarToHsl.js` (29 ln) — theme color bridge
- `hslToRgb`, `cssVarToHsl(name, fallback)` — reads live CSS variables → colors for PDF/charts (theme-consistent exports).

## Context/hooks/i18n

### `context/AuthContext.jsx` (174 ln) — auth state
- `AuthProvider` — wraps Supabase session: `signup` (incl. anti-enumeration handling: maps "already registered" to `exists` status), `login`, `loginWithGoogle` (OAuth redirect → `/auth/callback`), `logout`, `checkMfa`/`enrollMfa`/`verifyMfa`/`unenrollMfa` (TOTP), `profile` fetch+refresh. Exposes `{user, profile, loading, ...actions}`.
- **Tie:** S16's client half; every auth UX decision (anti-enumeration, guided 2FA) traces here.

### `context/ThemeContext.jsx` (32 ln) — theme provider
- `lumi-theme` localStorage + `data-theme` attribute + toggle.

### `hooks/useAuth.js` / `useTheme.js` (7 ln) — context accessors (guard-throw if outside provider).

### `i18n/index.jsx` (66 ln) — i18n provider
- `DICTIONARIES={en,fil}`; `getByPath` (dot-path lookup); `I18nProvider` — `t(k, vars)` w/ `{{var}}` interpolation; `useI18n()` hook; `<Trans k components>` for JSX interpolation.
- `en.json`/`fil.json` — locale dictionaries (parity enforced by `__tests__/i18n-keys.test.js`).

## Ecosim components

### `components/ecosim/EcosimWizard.jsx` (448 ln) — 5-step input wizard
- `export default EcosimWizard` — step state + per-step validation → step 1 location (SearchableSelect + geolocation) → 2 consumption/bill (guide: provider-agnostic bill guide, `5ac75b0`) → 3 target savings → 4 options (data source, AI toggle) → 5 review → submit.
- **Tie:** expert-feedback reworked it to 5 steps with hidden province mode.

### `components/ecosim/EcosimResults.jsx` (462 ln) — results display
- Helpers `solarInfo/windInfo/hydroInfo/geoInfo` (per-source labels+icons); renders score cards, comparison table, `InterpretationBadge`s, per-source `ExplanationModal` triggers, AI panel (loading/pending/error → `onAiRetry`), `EcosimBOM`, provider matches, PDF button (gated on AI completion, `cf38957`).

### `components/ecosim/EcosimBOM.jsx` (148 ln) — bill of materials
- `deriveSystemKw(source, generationKwh)` — per-source sizing proxy; renders components/costs table for the recommended source.

### `components/ecosim/ExplanationModal.jsx` (43 ln) — per-source explainer
- Modal: static `content` + `aiSummary` slot + `aiPending` state — explanation shown on demand.

### `components/ecosim/ProviderRecommendations.jsx` (228 ln) — provider directory
- `providerTechnologies`, `ProviderCard` (badges: verified/registry/retailer/products/nationwide), `ProviderList` (matched + `showFallbackNotice`), default export — filters `providers.json` by recommended source + region via `matchProviders`; nationwide fallback when no regional match.

## EnergyHub components

### `components/energyhub/EnergyMap.jsx` (709 ln) — Leaflet choropleth
- **Logic:** `isSuitabilityMetric`, `getColorForValue` (score→color ramp), `getClassificationLabel`, `formatFactors` (evidence tooltip), `removeAccents`/`normalizeGeoName` (name joining), `computeCentroid`, `matchByCoordinates` (**fallback matching: name → coordinates ≤0.8°** — handles naming mismatches between PSGC and GeoJSON); renders polygons colored by metric per level, hover factors, legend.
- **Tie:** the S11/S12 interactive map; coordinate-fallback join is a real-world-data-hardening detail.

### `components/energyhub/EnergyOverview.jsx` (112 ln) — national snapshot cards.

### `components/energyhub/EnergyTrends.jsx` (435 ln) — charts + AI panels
- `cssVarColor` (theme→chart colors), `sanitizeLLMOutput` (frontend-side scrub too — defense in depth), `ChartAiPanel` (per-chart analyze/refresh/loading), `EnergyTrends` — historical+forecast charts w/ per-chart AI analysis buttons.

### `components/energyhub/EnergySources.jsx` (127 ln) — source/grid breakdown charts.

### `components/energyhub/ProvincialDemand.jsx` (169 ln) — provincial demand
- `SECTORS`, `COLORS`, `formatNumber`, component — sector-split demand bars per region.

### `components/energyhub/AiInsightPanel.jsx` (116 ln) — insight card w/ LLM toggle.

### `components/energyhub/ChartExplanation.jsx` (38 ln) — what/why/action explainer block.

### `components/energyhub/MapExplanationCard.jsx` (153 ln) — map explainer
- `getHiddenSet`/`saveHiddenSet` (localStorage dismissal persistence) + component — narrative explanation + citation sources for the current map.

### `components/energyhub/PlotlyChart.jsx` (76 ln) — Plotly wrapper (data/layout/config passthrough).

## Shared components

- `shared/ProtectedRoute.jsx` (19 ln) — `useAuth` → loading→skeleton, no user→`/login` redirect.
- `shared/AdminRoute.jsx` (23 ln) — + role check → non-admin redirected.
- `shared/SearchableSelect.jsx` (64 ln) — searchable dropdown (query state, filtered list, selection) — the Dashboard/EcoSim pickers.
- `shared/Markdown.jsx` (23 ln) — minimal markdown renderer for AI text (paragraph/bold/list subset — sanitized input upstream).
- `shared/CitationSources.jsx` (67 ln) — numbered source list; `citationIds` → `data/references.json` entries.
- `shared/InterpretationBadge.jsx` (44 ln) — `RATINGS` bands + `getRating(score, max)` → star/badge — makes raw scores readable (SO5).
- `shared/InsightCard.jsx` (50 ln) — headline-insight card (icon+title+body+trend).
- `shared/ExpandableBlock.jsx` (40 ln) — collapse/expand content block.
- `shared/HelpTooltip.jsx` (49 ln) — glossary-term hover (`utils/glossary.js`).
- `shared/InfoTooltip.jsx` (28 ln) — generic info hover.
- `shared/NextStepList.jsx` (29 ln) — recommended-actions list (S15's "next steps").
- `shared/LanguageToggle.jsx` (33 ln), `ThemeToggle.jsx` (16 ln) — chrome toggles.
- `shared/Loading.jsx` (6 ln), `LoadingSkeleton.jsx` (14 ln) — placeholders.
- `components/ErrorBoundary.jsx` (66 ln) — class component `getDerivedStateFromError`/`componentDidCatch` → `ErrorState` fallback (React crash isolation).
- `components/ErrorState.jsx` (52 ln) — `ErrorState` (+retry), `LoadingState`, `EmptyState` exports.

## Layout

- `layout/Navbar.jsx` (241 ln) — `UserAvatar` (profile pic/initials), `LumLogo`, `Navbar` — nav links, auth-aware menu, theme/language toggles, mobile sheet.
- `layout/Footer.jsx` (46 ln) — footer links/credits.

## Admin components

- `admin/CreateUserModal.jsx` (164 ln) — admin user-creation form → `POST /admin/users`.
- `admin/UserDetailDrawer.jsx` (427 ln) — per-user detail panel: profile, role/status edits, simulations list, reports — calls the `admin.py` endpoints.

## UI primitives

`components/ui/{badge,button,card,dialog,dropdown-menu,form,input,progress,sheet,skeleton,sonner,table,tabs,tooltip}.jsx` — vendored shadcn-style primitives: styled wrappers (cva variants + `cn()`) over semantic elements/Radix — the design-system layer (D20). Each is small (20-200 ln) and purely presentational.

## Data files

- `data/providers.json` — 32 DOE-registry provider entries (name, region, technologies, badges).
- `data/references.json` — citation registry powering `CitationSources` + `citationIds`.
- `test/setup.js` — vitest jsdom/testing-library setup (covered in `06d`).

---
*Component descriptions come from real signature/hook scans; `*(inferred)*` where intent wasn't recorded.*
