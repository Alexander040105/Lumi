# Megaplan: UI Panel Feedback — Contrast, Imagery, Density, Logo, Mobile (SWE-2 Max Prompt)

You are implementing a batch of UI improvements for **Lumi** driven by thesis-defense panel feedback:
*"the UI's text has bad contrast which made it unreadable — the text and the background are too light."*
Plus stakeholder asks: less text-heaviness via imagery (especially EcoSim + EnergyHub), less dead
white space, a bigger navbar logo, and better mobile/accessibility — **while preserving the brand**
(green family + Solar Gold; see `DESIGN.md`, binding identity confirmed).

Work through the items in the suggested slice order, commit each slice separately (atomic commits,
message ≤50 chars, **no Devin attribution lines**), and verify with the commands at the end.
Create a branch first, e.g. `git checkout -b ui/panel-feedback-overhaul`.

Everything you need is in this document — root causes are identified with file and line references.
Verify each reference before editing (line numbers may drift slightly).

---

## 1. Repository orientation

- **Frontend**: `react-frontend/` — React 18 + Vite, Tailwind CSS 4, shadcn-style primitives in
  `src/components/ui/`, i18n via `src/i18n/en.json` + `fil.json` (every string change lands in both;
  interpolation `{{var}}`).
- **Design tokens**: `react-frontend/src/styles/globals.css` (`:root` light + `.dark`); resolved via
  `hsl(var(--token))`. Brand rules in `DESIGN.md`: One Family Rule (only green hues as chrome),
  Gold Reserve Rule (gold = solar/emphasis, ≤1–2 uses per screen), No-Pure-Neutral Rule,
  Flat-By-Default shadows, Semibold Ceiling.
- **Contrast gate**: `src/__tests__/theme-contrast.test.js` parses `globals.css` and asserts
  WCAG AA 4.5:1 on token pairs — extend it when tokens change.
- **Imagery**: there are currently **no illustrations** in the app — only lucide-react icons and
  `public/logo.png` / `public/lumi-logo.png` (both 500×500). `public/` also holds geojson + two
  geothermal PNG overlays (map-only).
- **Run locally**: `npm run dev` at repo root (Vite :5173 + uvicorn :8000). Frontend-only work also
  runs via `npm run dev --prefix react-frontend` (pages needing API data will show empty states).
- **Tests**: `cd react-frontend && npx vitest run src/__tests__/theme-contrast.test.js` (targeted)
  and `npm run test:run` (full), `npm run build`.

### Non-negotiables

- WCAG AA is a hard gate (PRODUCT.md principle 4). Every changed text/background pair must hit
  4.5:1 (3:1 allowed for ≥18px bold / ≥24px regular text and non-text UI).
- i18n: any new user-facing string lands in **both** `en.json` and `fil.json`.
- No new dependencies. Build illustrations as inline SVG React components, not image files.
- Decorative SVGs get `aria-hidden="true"`; meaningful ones get `role="img"` + `<title>`.

---

## 2. Imagery strategy (stakeholder asked: "what images and how")

**Decision: hand-built inline SVG illustrations in brand tokens.** Rationale: zero network payload
(matters for PH mobile connections), auto re-theming in dark mode via `hsl(var(--token))`, exact
brand palette, no licensing, consistent with the flat friendly system. Stock photos would fight the
aesthetic and add weight; pure lucide scaling is cheapest but visually weakest.

**Build once**: `src/components/illustrations/` — small functional components, ~120–200px display
size, accepting a `className` prop:

| Component | Depicts | Tokens used |
|---|---|---|
| `IllustrationLocation` | PH archipelago dots + location pin | primary, accent pin, muted water |
| `IllustrationBill` | generic electric bill with 3 highlighted zones (kWh used / amount due / ₱ per kWh) | card, border, accent+primary zone tints |
| `IllustrationSavings` | gauge/dial arc | primary arc, accent needle |
| `IllustrationAI` | document + sparkles | muted doc, accent sparkles |
| `IllustrationReview` | clipboard checklist | primary checks, border |
| `IllustrationSolar` | panel array + sun | accent sun, primary panel |
| `IllustrationWind` | turbine + motion lines | brand-success turbine |
| `IllustrationHydro` | stream + drop | chart-hydro water |
| `IllustrationEmpty` | leaf + magnifier (empty/error states) | muted + primary |

**Placement strategy** (fill space AND cut copy — pair each visual with a one-line caption, not a
paragraph): wizard steps get a per-step visual anchor; tables/stats get icon-glyph headers; empty
and error states get `IllustrationEmpty`; the results hero gets the recommended source's scene.
Per Gold Reserve Rule, gold appears in an illustration only where solar/emphasis is the point.

---

## 3. Work items

### S1 — Contrast & readability (the panel's headline complaint)

**Root causes (verified)**:

- `globals.css:27` — `--muted-foreground: 120 30% 28%` (#3a5c3b) is only ~6.9:1 on the page
  background and drops further on tinted fills; with `p { @apply text-muted-foreground }`
  (`globals.css:186-188`) **every paragraph in the app renders muted** — this is why the whole app
  "reads light."
- Tinted-on-tinted: `text-warning` (#aa4411) on `bg-warning/10` ≈ 3.9:1 — fails
  (`EnergyTrends.jsx:22,32,43-49,68`, `EcosimResults.jsx:113-118,248`, `AiInsightPanel.jsx:93-104`,
  `EcosimWizard.jsx:199`, `ProviderRecommendations.jsx:105,117`).
- Opacity-reduced text: `text-primary/80` (Home.jsx:102), `text-primary-foreground/70,80,85` on
  `bg-primary` (Home.jsx:80,84,225) — white@70% on #2e5f2b ≈ 4.0:1 for 12px text → fail.
- Muted-on-muted: `text-muted-foreground` on `bg-muted`/`bg-muted/40`/`bg-muted/50`
  (`ChartExplanation.jsx:12-30`, `MapExplanationCard.jsx:89,143`, `Ecosim.jsx:568-575`,
  `EcosimResults.jsx:143`, `AiInsightPanel.jsx:83`, `Home.jsx:61`) — weakest combos in the app.
- Microcopy floor: 131× `text-xs`, plus `text-[10px]` (Home.jsx:47, EnergyTrends.jsx:58,68,
  EnergyMap.jsx:225,227) and `text-[11px]` (ProviderRecommendations.jsx:67) — small + muted = the
  unreadable text the panel saw.
- Charts: `ProvincialDemand.jsx:138-139` Recharts axes unstyled → default #666 gray on light bg;
  `EnergySources.jsx:51` white `textfont` inside pie slices fails on the light Solar slice;
  `EnergyMap.jsx:374-397` Leaflet tooltip HTML uses muted-foreground at 11–12px.
- Invisible hover bug: `EnergyTrends.jsx:22` — `hover:bg-warning/10` on a `bg-warning/10` element
  (hover does nothing).

**Changes**:

- `globals.css`: `--muted-foreground: 120 32% 22%` (≈#2c472e, ~9:1 on card/background, still in
  family). Verify dark `--muted-foreground` stays ≥4.5:1 on `--muted` (current ~10:1, keep).
- Tinted-callout pattern: in `EnergyTrends` `ChartAiPanel`, `EcosimResults` warning/pending boxes,
  `AiInsightPanel`, `ProviderRecommendations` fallback boxes — body text → `text-foreground`;
  keep `text-warning` only on the small icon, or introduce `--warning-strong` (~`22 85% 30%`) for
  headings inside warning-tinted surfaces. Fix the invisible hover: `bg-warning/10` → `hover:bg-warning/20`.
- Replace `text-primary/80` → `text-primary`; `text-primary-foreground/70|80|85` →
  `text-primary-foreground` (or `/90` minimum where a hierarchy step is needed).
- Microcopy floor: nothing below `text-xs`; bump `text-[10px]`/`text-[11px]` → `text-xs`; bump
  `text-xs` → `text-sm` where the text carries meaning the user needs (bill-guide rows
  `EcosimWizard.jsx:229-237`, input hints `:246-256`, disclaimer toggle `Ecosim.jsx:575`,
  provider disclaimers `:142-148`, summary tile labels `:339-374`).
- `ChartExplanation` / `MapExplanationCard`: text → `text-foreground` (they're muted on `bg-muted/40`).
- Charts: `ProvincialDemand` XAxis/YAxis `tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}`;
  `EnergySources` pie labels — dark `textfont` (foreground) on the Solar/light slices (or labels
  outside with connector lines); Leaflet tooltip text → foreground at 12px min.
- Extend `theme-contrast.test.js` `PAIRS`: `["--muted-foreground","--background"]`,
  `["--muted-foreground","--card"]`, `["--primary","--card"]`, `["--warning","--card"]`, and a
  dark-mode equivalent for each.

**Acceptance**: contrast test passes incl. new pairs; no `text-[10px]`/`text-[11px]` remain; no
opacity-slashed text (`/70|/80|/85`) on colored fills; spot-check shows body copy visibly darker.

---

### S2 — Illustration system (build once)

Create `src/components/illustrations/` per §2 strategy — 9 components, ~30-60 lines of inline SVG
each, props `className`. Decorative → `aria-hidden`; the bill diagram gets `role="img"` + title
since it teaches. Add i18n `aria-label`/title strings in en+fil for the bill diagram.

**Acceptance**: components render in both themes without hard-coded hex outside brand tokens;
no new deps; each ~120-200px, `className`-resizable.

---

### S3 — EcoSim imagery + whitespace fills

- `EcosimWizard.jsx:124-126` — add per-step illustration beside the `CardHeader` (steps 1–5:
  Location, Bill, Savings, AI, Review) — fills the sparse right side of steps 3–4 cards.
- `EcosimWizard.jsx:227-241` — bill guide: prepend `IllustrationBill` (annotated zones) so the
  3 rows become captions under a diagram instead of standalone explanations.
- `EcosimWizard.jsx:432-444` — "Your Inputs" sidebar shows "—" placeholders until filled: render
  only set values + a compact step illustration on top; when nothing is set show one quiet
  "Complete the steps to see your inputs" line (new i18n key) instead of 5 empty rows.
- `EcosimWizard.jsx:274-313` (step 3) & `:315-332` (step 4): add `IllustrationSavings` /
  `IllustrationAI` so the single-control cards aren't empty.
- `EcosimResults.jsx:125-159` — hero right column: keep the kWh number, add the recommended
  source's `Illustration*` + a small coverage bar/gauge under it (fills the imbalance).
- `EcosimResults.jsx:186-220` — "Why recommended": keep text, add a climate-glyph mini-row
  (Sun/Wind/Droplets lucide + one value each) above the two text boxes.
- `EcosimResults.jsx:395-409` — climate grid: prepend a small lucide glyph per metric label.
- `ProviderRecommendations.jsx:105-117` — fallback/empty boxes get `IllustrationEmpty`.
- `Ecosim.jsx:568-575` — disclaimer card gets a small `Info` icon left of the text (already icon'd?
  verify — if not, add); `Ecosim.jsx:674-699` completion dialog gets the recommended source's
  illustration centered above the message.
- `EcosimBOM.jsx` is **dead code** (zero imports) — decide: revive it inside `EcosimResults` as a
  collapsible "Estimated components" card (wrap table in `overflow-x-auto`, add `<caption>`), or
  delete the file. Prefer revive only if trivial; otherwise delete.

**Acceptance**: every wizard step and major results section has a visual anchor; bill guide is
diagram-led; sidebar never renders 5 dead placeholders; no layout shift on step transitions.

---

### S4 — EnergyHub + marketing imagery + whitespace fills

- `EnergySources.jsx:105-121` — source legend rows: prepend per-source lucide icon (Sun/Wind/
  Droplets/Flame/Factory…) in the row's own color instead of bare color square.
- `EnergyHub.jsx:275-309` — IRENA stat tiles: add a small icon each; tighten `p-6`/`p-3` tiles to
  `p-4`/`p-2.5` (density tightening, worst offender).
- `ProvincialDemand.jsx:62-85` — error/no-data states get `IllustrationEmpty`.
- `EnergyHub.jsx:249-251` — disclaimer banner: add `Info` icon; `MapExplanationCard.jsx:142-146` —
  add small metric icon anchoring the AI paragraph.
- `Home.jsx:277-289` — insight banner right side is empty: add `IllustrationSolar` (or the
  location illustration) on the right in `sm:flex-row` so the `justify-between` has a second child.
- `About.jsx:113-146` — dead left column under the problem paragraph: place `IllustrationLocation`
  (or a 3-glyph "data → estimate → decision" mini-diagram) to balance the 2×2 stat grid.
- Optional/stretch: Home hero subtle backdrop illustration behind the logo block — only if it
  stays under ~10% visual weight; skip if it fights the logo.

**Acceptance**: no large empty regions remain at the flagged spots; EnergyHub sections read as
visual-first, text-second; density tightening limited to the flagged cards.

---

### S5 — Logo

`Navbar.jsx:67-73` — `h-14` → `h-16 md:h-20` (56px → 64/80px). Bigger mark only, no wordmark
(user decision). Ensure the header still fits: the `page-container` row already uses
`items-center justify-between`; the larger image simply grows the header. `Home.jsx:130-134`
hero logo `h-20 sm:h-24` → `h-24 sm:h-28` for consistency.

**Acceptance**: navbar logo visibly larger at all breakpoints; no layout overflow; mobile menu
unchanged.

---

### S6 — Mobile + accessibility

**Touch targets (floor ~40px):**
- `ui/button.jsx:20` — `sm` size `h-9` (36px) → `h-10` (40px). One-line fix covering every
  `size="sm"` button (wizard quick-selects, Use My Location, retries, show-all, toggles).
- `EcosimWizard.jsx:209-217` — bookmark icon button ~16px: wrap in a `h-10 w-10` padded button.
- `EcosimWizard.jsx:340-375` — six "Edit" text buttons: add `aria-label` with the field name
  (new i18n keys like `summaryEdit.location`) + padding to ≥32px.
- `EnergyMap.jsx:572-604,614,629` — selects/toggles `px-2 py-1` ~26-28px → `py-1.5` min or
  `min-h-[40px]`; `MapExplanationCard.jsx:116,129` icon buttons `h-6 w-6` → `h-9 w-9`;
  `EnergyTrends.jsx:318,357,393` enlarge buttons `p-1` → `p-2` (32px→40px);
  `ChartAiPanel`/`EnergyTrends.jsx:22` analyze button → `py-2` min-height 36–40px.
- `EcosimWizard.jsx:297-306` — range input: acceptable track, but ensure thumb ≥24px
  (`accent-primary` + custom thumb class if trivial).

**Responsive:**
- `EcosimWizard.jsx:432` — summary sidebar is `hidden md:block`: add a compact collapsible
  summary strip on mobile (above the Next button, reuse the same values; `<details>` is fine).
- `EnergyMap.jsx:409` — fixed `height: 480` → class `h-[300px] md:h-[480px]`; loading placeholder
  L651 same.
- `EnergySources.jsx:99` — donut `w-80 h-80` → add `max-w-full` (or `w-64 h-64 sm:w-80 sm:h-80`).
- `ProvincialDemand.jsx:134` — `h-80` + 18 crowded x-labels: `angle={-35}` + `interval={0}` +
  `height={26}` tick, or `interval="preserveStartEnd"`; keep `h-80` desktop, `h-64` on `sm` if
  trivial via ResponsiveContainer wrapper class.
- `EnergyTrends.jsx:152-153,214-215,263-264` — plotly legend `x:1` + `r:100-120` margin eats ~⅓ of
  plot width on phones: switch legend to `{ orientation: "h", y: -0.25 }` + smaller right margin
  (set `r: 8`) at all sizes — simplest fix, acceptable on desktop.
- `ui/table.jsx` — tables have no scroll wrapper: wrap usages (BOM if revived, admin tables) in
  `overflow-x-auto` containers.
- `ProviderRecommendations.jsx:197-199` — TabsList: add `flex-wrap` for long Filipino labels.

**Aria/SR:**
- `EcosimWizard.jsx:96` — step dots `aria-hidden` with no SR progress: add `role="group"` +
  `aria-label={t("wizard.progress", {step, total})}` on the strip, `aria-current="step"` on the
  active dot.
- `EnergyHub.jsx:240-241` — breadcrumb `/` separator → `aria-hidden="true"`; current crumb gets
  `aria-current="page"`.
- `EnergyMap.jsx:575,593` — selects: `focus:outline-none` → keep but add `focus-visible:ring-2
  ring-ring`; `MapContainer` L410 → `aria-label` on wrapper (map is mouse-first; document that).
- `EcosimResults.jsx:133,189,249,296,360` — missing `aria-hidden` on decorative icons (matches
  existing convention in the file).
- `ExplanationModal.jsx:17-22` — trigger adds `aria-haspopup="dialog"`.
- Charts: add `role="img"` + `aria-label` (chart title string) on the wrapping divs of
  `PlotlyChart`/`ProvincialDemand` charts.
- Ghost button quirk `ui/button.jsx:15` — ghost hover dims to muted-foreground; fine per se but
  `Ecosim.jsx:575` disclaimer toggle needs `hover:text-foreground` to stay readable.

**Acceptance**: all interactive elements ≥~36-40px touch; wizard summary reachable on mobile;
map/donut/charts fit 360px viewports without clipping; axe-style pass on the listed aria items.

---

### S7 — Branding fixes (maintain, don't restyle)

- `EcosimResults.jsx:24` — `sourceMeta.Solar` uses `--warning` burnt orange → switch to
  `--accent`/`--chart-solar` gold circle + bar (solar = gold per DESIGN.md).
- `EcosimWizard.jsx:118` — step-2 `Zap` icon `text-warning` → `text-accent-foreground`-safe
  gold treatment or `text-primary` (pick whichever stays AA on card).
- Gold budget: after S3/S4, count gold uses per screen — keep ≤2 (Gold Reserve Rule). The solar
  swap counts as the screen's one gold.
- Cleanup: remove unused lucide imports (`ChevronRight` Home.jsx:15; `FlaskConical`,
  `LayoutDashboard`, `Microscope` About.jsx:9-13); `public/philippine_geojson_file_per_provinces.json`
  (unminified) is unused — leave on disk, no action needed (referenced only by docs).
- Dark-mode `--accent` stays luminous green per DESIGN.md — do not "fix" it to gold; it's a
  deliberate token decision already on record.

**Acceptance**: solar visuals read gold in both EcoSim and EnergyHub; no new hue families in
chrome; build passes with unused imports gone.

---

## 4. Explicit non-goals

- No photography/stock images; no new icon or illustration libraries.
- No restyling of the green palette or adding new hue families.
- No backend/API changes; no i18n restructure (only additive keys).
- `expo-mobile/` untouched (abandoned scaffold).
- No full-app density overhaul — tightening only at flagged spots.
- Admin pages out of scope except where the shared `ui/button.jsx` sm-size fix lands automatically.

---

## 5. Suggested slice order → atomic commits

Create branch `ui/panel-feedback-overhaul`. One commit per slice, message ≤50 chars, no
co-author/attribution trailers:

| # | Slice | Suggested commit |
|---|---|---|
| 1 | S1 contrast tokens + targeted fixes + extended test | `fix(ui): raise text contrast for panel feedback` |
| 2 | S2 illustration components | `feat(ui): add brand SVG illustration set` |
| 3 | S3 EcoSim imagery + fills | `feat(ecosim): illustrate wizard and results` |
| 4 | S4 EnergyHub/Home/About imagery + fills | `feat(energyhub): add icons and empty-state art` |
| 5 | S5 logo | `feat(nav): enlarge brand logo` |
| 6 | S6 mobile + a11y | `fix(a11y): touch targets, aria, mobile layout` |
| 7 | S7 branding fixes | `fix(brand): solar gold theming and cleanup` |

If S2-S4 land together that's fine — but keep S1 separate so the contrast fix is bisectable.

---

## 6. Verification

- `cd react-frontend && npx vitest run src/__tests__/theme-contrast.test.js` — new pairs pass.
- `npm run test:run && npm run build` — green.
- **Browser check is mandatory** (project rule): run `npm run dev`, then verify via Playwright
  (`npx playwright screenshot` / playwright-cli) or chrome-devtools MCP:
  1. `/ecosim` — wizard steps 1–5 visuals, bill diagram, filled sidebar, summary strip on 390px.
  2. `/ecosim` results (needs backend data; if backend is down, verify wizard + empty states).
  3. `/energyhub` — legend icons, IRENA tiles, disclaimer icon, map height on mobile width.
  4. `/` + `/about` — logo size, insight banner illustration, About infographic.
  5. Dark mode toggle — illustrations and new text colors still pass contrast.
- Targeted vitest only during iteration; run the full suite once at the end.

---

## 7. Constraints

- Both `en.json` and `fil.json` updated for every string change (`{{var}}` interpolation).
- Reuse existing primitives (`dialog.jsx`, `sonner`, lucide icons, token classes) — zero new deps.
- Every new text/bg combo ≥4.5:1; keep the extended contrast test authoritative.
- Follow existing code style: compact, Tailwind utilities, no unnecessary comments.
- `.env` files never committed; nothing in `public/` gets deleted without checking references.
