---
name: LUMI
description: Environmental intelligence for the Philippines — household renewable simulation and national energy analytics.
colors:
  lumi-green: "hsl(122 35% 30%)"
  forest-deep: "hsl(120 50% 15%)"
  forest-ink: "hsl(120 50% 10%)"
  fern: "hsl(108 48% 69%)"
  leaf-border: "hsl(120 25% 83%)"
  meadow-mist: "hsl(120 45% 90%)"
  mist: "hsl(120 35% 93%)"
  pale-meadow: "hsl(120 30% 97%)"
  card-white: "hsl(0 0% 100%)"
  ring-green: "hsl(122 35% 35%)"
  solar-gold: "hsl(45 90% 65%)"
  solar-glow: "hsl(47 100% 73%)"
  wind-green: "hsl(117 42% 56%)"
  geothermal-ember: "hsl(30 90% 42%)"
  harvest-amber: "hsl(22 85% 40%)"
  signal-red: "hsl(0 72% 51%)"
  map-verdant: "hsl(142 76% 36%)"
  map-canopy: "hsl(142 71% 45%)"
  map-gold: "hsl(48 96% 53%)"
  map-amber: "hsl(25 95% 53%)"
  map-red: "hsl(0 84% 60%)"
  map-slate: "hsl(215 20% 65%)"
typography:
  display:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(2.25rem, 5vw, 3.75rem)"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  title:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.025em"
  body:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.75
  label:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.4
rounded:
  sm: "0.5rem"
  md: "0.625rem"
  lg: "0.75rem"
  full: "9999px"
spacing:
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
components:
  button-primary:
    backgroundColor: "{colors.lumi-green}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.md}"
    padding: "0.5rem 1rem"
    height: "2.5rem"
  button-primary-hover:
    backgroundColor: "{colors.lumi-green}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.md}"
    padding: "0.5rem 1rem"
    height: "2.5rem"
  button-secondary:
    backgroundColor: "{colors.meadow-mist}"
    textColor: "{colors.forest-ink}"
    rounded: "{rounded.md}"
    padding: "0.5rem 1rem"
    height: "2.5rem"
  button-outline:
    backgroundColor: "{colors.pale-meadow}"
    textColor: "{colors.forest-ink}"
    rounded: "{rounded.md}"
    padding: "0.5rem 1rem"
    height: "2.5rem"
  card-default:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.forest-ink}"
    rounded: "{rounded.lg}"
    padding: "1.5rem"
  input-default:
    backgroundColor: "{colors.pale-meadow}"
    textColor: "{colors.forest-ink}"
    rounded: "{rounded.md}"
    padding: "0.5rem 0.75rem"
    height: "2.5rem"
  badge-primary:
    backgroundColor: "{colors.lumi-green}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.full}"
    padding: "0.125rem 0.625rem"
  badge-secondary:
    backgroundColor: "{colors.meadow-mist}"
    textColor: "{colors.forest-ink}"
    rounded: "{rounded.full}"
    padding: "0.125rem 0.625rem"
---

# Design System: LUMI

## Overview

**Creative North Star: "The Municipal Energy Advisor"**

LUMI's visual system is a knowledgeable local advisor rendered in green: it stands beside a Filipino homeowner, opens the climate and energy record for *their* municipality, and explains in plain language what solar, wind, or hydro would mean for their household. Every surface behaves like that advisor — calm, trustworthy, unhurried, and honest about what is an estimate.

The palette is a living green field anchored on **Lumi Green** (`#2e5f2b`), the confirmed base color from which the entire brand scale is derived. A single warm accent, **Solar Gold**, marks sunlight, savings, and moments worth attention. The system never shouts: it reassures. Surfaces stay flat and quiet until the user touches them, at which point they lift gently to confirm the interaction. There is deliberately no alarmist energy-crisis framing and no dashboard clutter — a homeowner comparing options should feel accompanied, not examined.

The system is bilingual (English/Filipino) and dual-themed: a light theme of pale meadow surfaces and a complete dark theme of deep forest tones, both built from the same green family. Density is generous and readable — 17px base type, open line height, cards that breathe.

**Key Characteristics:**
- Single-family green palette anchored on Lumi Green (`#2e5f2b`); gold reserved for solar and emphasis
- Flat-by-default surfaces with state-responsive lift on hover/focus
- Soft, friendly geometry — 0.75rem corner radius, pill badges, generous padding
- Plain-language, hedged voice; data visualization colors are semantic (gold = solar, green = wind, deep green = hydro, ember = geothermal)
- Full dark theme as a supported, usable second theme via `.dark` class
- WCAG AA contrast and keyboard focus as hard requirements

## Colors

The palette is one green family — from pale meadow to forest ink — with a single gold accent for solar and emphasis, plus a semantic chart palette and a diverging map-classification ramp. Values below are the light theme; the dark theme remaps the same roles (see below).

### Primary
- **Lumi Green** (hsl(122 35% 30%) / `#2e5f2b`): the brand base color and the primary action color — buttons, links, active states, badge fills, chart hydro, brand mark support. All other greens are keyed to it.
- **Ring Green** (hsl(122 35% 35%) / `#3b6e38`): focus rings in light theme — a half-step brighter than Lumi Green so focus is visible on both white and green surfaces.
- **Forest Deep** (hsl(120 50% 15%) / `#133913`): `brand-dark` — deep accents, headings on pale fills, the near-black end of the green family.

### Secondary
- **Solar Gold** (hsl(45 90% 65%) / `#f6d96a`): the only warm accent — solar references, highlight badges, emphasis moments, and the `accent` token. Used sparingly; its rarity is the point.

### Tertiary (semantic data colors)
- **Solar Glow** (hsl(47 100% 73%) / `#ffe175`): `chart-solar` — solar series in charts; lighter than Solar Gold so it reads as data, not chrome.
- **Wind Green** (hsl(117 42% 56%) / `#64be60`): `chart-wind` and `brand-success` — wind series, success states, positive deltas.
- **Hydro Green** = Lumi Green: `chart-hydro` reuses the primary deep green.
- **Geothermal Ember** (hsl(30 90% 42%) / `#cb6b0b`): `chart-geothermal` — the only hot earth tone, reserved for geothermal data.
- **Harvest Amber** (hsl(22 85% 40%) / `#aa4411`): `warning` — cautionary states and amber-tier callouts.
- **Signal Red** (hsl(0 72% 51%) / `#dc2626`): `destructive` — destructive actions and errors only, never decoration.

### Neutral
- **Pale Meadow** (hsl(120 30% 97%) / `#f4fbf4`): page background — an almost-white with a breath of green.
- **Card White** (hsl(0 0% 100%) / `#ffffff`): card and popover surfaces — the one pure neutral in the system.
- **Mist** (hsl(120 35% 93%) / `#ebf6eb`): `muted` — subtle panels and quiet fills.
- **Meadow Mist** (hsl(120 45% 90%) / `#dff6df`): `secondary` and `brand-pale` — secondary buttons, soft highlight fills.
- **Leaf Border** (hsl(120 25% 83%) / `#c6e0c6`): `border`, `input`, `brand-lighter` — every border, divider, and input stroke is this soft green-gray.
- **Forest Ink** (hsl(120 50% 10%) / `#0f260d`): `foreground` — all primary text; green-black, never pure black.

### Map classification ramp
Choropleth potential classes diverge from green to red: **Verdant** (very high, hsl(142 76% 36%) / `#1e9a6c`), **Canopy** (high, hsl(142 71% 45%) / `#39ad82`), **Map Gold** (moderate, hsl(48 96% 53%) / `#facc14`), **Map Amber** (low, hsl(25 95% 53%) / `#f97316`), **Map Red** (very low, hsl(0 84% 60%) / `#ef4343`), **Map Slate** (no data, hsl(215 20% 65%) / `#939dac`). These are data semantics, not UI accents — never reuse them as decoration.

### Dark theme
The `.dark` class remaps every role within the same green family: background falls to near-black green (hsl(120 40% 2%) / `#030703`), foreground to pale green-white (hsl(116 37% 92%) / `#e4f2e3`), the accent brightens to a luminous green (hsl(117 62% 54%) / `#48d241`) instead of gold, and borders deepen to hsl(120 25% 18%). Dark mode is a fully supported, user-toggleable theme — treat its token values as equally real, and verify WCAG AA contrast against dark surfaces too.

### Named Rules
**The One Family Rule.** All UI greens belong to the Lumi Green family (hue ~108–142). A second hue family may only ever enter through data (charts, maps), never as interface chrome.

**The Gold Reserve Rule.** Solar Gold marks solar and emphasis only. If gold appears more than once or twice on a screen, something is wrong — it is a signal, not a theme color.

**The No-Pure-Neutral Rule.** Backgrounds, text, and borders are all green-tinted. Pure grays and pure blacks break the family; the only pure white allowed is card surface.

## Typography

**Display Font:** System stack (`ui-sans-serif, system-ui, sans-serif`)
**Body Font:** System stack (same — one family throughout)
**Label/Mono Font:** none distinct

**Character:** Deliberately ordinary in the best way — the system stack keeps the advisor voice neutral and legible on the modest hardware and connections of its Philippine audience, with no webfont payload. Personality comes from weight and spacing, not typeface.

The root font size is 17px (`html { font-size: 17px }`), so all rem values render slightly larger than default — a quiet readability commitment to non-technical users.

### Hierarchy
- **Display** (extrabold/800, clamp(2.25rem–3.75rem), tracking-tight): hero headlines only (`text-4xl` → `text-6xl`).
- **Headline** (semibold/600, 1.875rem, tracking-tight): `h1`, page titles.
- **Title** (semibold/600, 1.5rem, tracking-tight): `h2`, section headings; `h3` at 1.25rem semibold.
- **Body** (regular/400, 1rem, line-height 1.75): prose in `text-muted-foreground` for reading text; foreground for interactive content.
- **Label** (medium/500, 0.875rem): buttons, form labels, meta text; eyebrow/category labels use `text-xs` medium, uppercase, `tracking-wider`, tinted `text-primary/80`.

### Named Rules
**The Semibold Ceiling Rule.** Headings top out at semibold inside app surfaces; extrabold is reserved for the marketing hero. Weight is spent sparingly so it still means something.

**The Plain-Language Rule.** Labels and microcopy prefer plain words over units and jargon ("estimated monthly savings" over "kWh offset delta") — the advisor explains; it never gatekeeps.

## Layout

- **Container:** centered, `padding: 2rem`, capped at 1200px (`2xl` breakpoint).
- **Page rhythm:** `.page-container` — `max-w-6xl`, `px-4 py-8`; `.page-header` stacks vertically then splits into a row on `md+`; `.stack` gives `gap-6` vertical rhythm; `.grid-cards` gives two-column card grids on `md+`.
- **Density:** generous — cards pad at 1.5rem, sections separate by 1.5rem gaps, content is never cramped to fit more on screen.
- **Responsive:** mobile-first single column; cards and grids open at `md` (768px); navigation collapses to a sheet/drawer pattern on small screens.
- **Surfaces:** content lives on cards (white on Pale Meadow), not directly on the page background — the advisor hands you documents, it doesn't scrawl on the wall.

## Elevation & Depth

The system is **flat by default with state-responsive lift**: surfaces carry only a whisper of shadow (`shadow-sm`) at rest, and meaningful elevation appears solely as a response to interaction — hover lifts to `shadow-lg`, occasionally tinted with the brand green (`shadow-primary`) on featured cards. Depth is feedback, not decoration.

### Shadow Vocabulary
- **Resting card** (`shadow-sm`): the default for cards, inputs, and panels — barely-there contact shadow.
- **Interactive lift** (`shadow-md` → `shadow-lg`): hover/focus response on clickable cards and prominent actions.
- **Brand-tinted lift** (`shadow-lg shadow-primary`): reserved for featured/hero cards — the shadow takes on Lumi Green, making the lift feel warm rather than heavy.
- **Modal elevation** (`shadow-xl`): rare; dialogs and sheets only.

### Named Rules
**The Flat-By-Default Rule.** A shadow that does not answer a user action is a bug. Static surfaces are flat; shadows exist only to say "this responds to you."

## Shapes

Soft, friendly geometry throughout: the base radius is 0.75rem (`lg`), stepping down to 0.625rem (`md`) for controls and 0.5rem (`sm`) for compact elements. Buttons and inputs use `md`; cards use `lg`; badges and chips are fully rounded pills. Nothing is sharp-cornered — the advisor's edges are always softened. Borders are thin (1px) and always Leaf Border, never black.

## Components

### Buttons
- **Shape:** gently rounded (0.625rem / `rounded-md`), `h-10` default, `h-9` small, `h-11` large.
- **Primary:** Lumi Green fill, white text (`px-4 py-2`, medium weight). Hover does not change color — it eases to `opacity-90`, keeping the green stable.
- **Secondary:** Meadow Mist fill, Forest Ink text — quiet but present.
- **Outline:** 1px Leaf Border on Pale Meadow; hover fills Meadow Mist.
- **Ghost:** transparent; hover reveals a Mist fill — for tertiary actions.
- **Link:** Lumi Green text, underline on hover — for inline navigation.
- **Focus everywhere:** `focus-visible:ring-2 ring-ring` (Ring Green) — WCAG AA keyboard visibility is mandatory.

### Badges & chips
- **Style:** fully rounded pills (`rounded-full`), `text-xs` medium, `px-2.5 py-0.5`, 1px border (transparent on filled variants).
- **Primary:** Lumi Green fill / white text — status and category.
- **Secondary:** Meadow Mist fill / Forest Ink — quieter labels.
- **Outline:** border + foreground text — for filter-like tags.
- **Domain variant:** `InterpretationBadge` translates technical results into plain-language readings ("Good", "Excellent") — pair data semantics with human words.

### Cards & containers
- **Corner:** gently curved (0.75rem / `rounded-lg`).
- **Surface:** Card White with 1px Leaf Border on Pale Meadow pages.
- **Shadow:** `shadow-sm` at rest; lifts on hover when interactive (see Elevation).
- **Padding:** `p-6` header/content, header stacks with `space-y-2`, title at `text-lg` semibold, description `text-sm` muted.
- **Domain variants:** `InsightCard` for AI/analysis output; `ExpandableBlock` for progressive disclosure of technical depth — depth is offered, never forced.

### Inputs & fields
- **Style:** `h-10`, `rounded-md` (0.625rem), 1px Leaf Border stroke, Pale Meadow fill, `px-3 py-2`, `shadow-sm`.
- **Focus:** `focus-visible:ring-2 ring-ring`, outline removed — the ring is the only focus signal.
- **Placeholder:** muted-foreground — quiet, never a label substitute.
- **Composite:** `SearchableSelect` handles the 1,600+ municipality picker; `HelpTooltip`/`InfoTooltip` attach advisor explanations to technical fields.

### Navigation
- **Navbar:** top bar with brand mark (lumi-logo), primary links, `ThemeToggle`, `LanguageToggle` (EN/FIL), and auth actions; collapses to `Sheet` drawer on mobile.
- **States:** links rest in foreground/muted, hover to Lumi Green, active route emphasized; never underline-chrome heavy — the advisor is present, not loud.

### Data visualization
- **Charts (Plotly/Recharts):** series colors come only from the semantic chart tokens — Solar Glow for solar, Wind Green for wind, Hydro Green (Lumi Green) for hydro, Geothermal Ember for geothermal.
- **Maps (Leaflet):** choropleth fills use the six-step classification ramp; marker strokes are white. Classification colors are data, never decoration.
- **Citations:** `CitationSources` renders data provenance inline — every number that can be traced is traced; this is a product commitment, not a component convenience.

### Feedback
- **Toasts:** `sonner` — brief, bottom-edge confirmations.
- **Loading:** `animate-spin`/`animate-pulse` with `Loading`/`LoadingSkeleton` — skeletons over spinners for content-shaped waits.
- **Dialogs:** Radix `Dialog`/`Sheet` with the card surface treatment.

## Do's and Don'ts

### Do:
- **Do** anchor every green on the Lumi Green family (hue ~108–142); derive new steps from it rather than introducing foreign greens.
- **Do** keep surfaces flat at rest and let hover/focus supply the only elevation (`shadow-sm` → `shadow-lg`, `shadow-primary` for featured cards).
- **Do** use Solar Gold only for solar references and rare emphasis — its scarcity is what makes it read as sunlight.
- **Do** write UI copy in the advisor voice — plain, hedged, honest ("estimated", "may work in your area"), in both `en.json` and `fil.json`.
- **Do** verify WCAG AA contrast on both themes — especially gold-on-light and accent-green-on-dark.
- **Do** keep `focus-visible:ring-2` on every interactive element; the Ring Green ring is the accessibility floor.
- **Do** use the semantic chart/map tokens for data colors, so a solar chart and a solar badge share the same sunlight.

### Don't:
- **Don't** introduce a second accent hue (no blues, purples, teals) into interface chrome — the system is one green family plus gold.
- **Don't** use pure gray or pure black for text, borders, or surfaces; neutrals are green-tinted, the only pure white is card surface.
- **Don't** decorate with the map-classification or chart colors — those hues are data semantics (a red badge must never mean "nice low cost").
- **Don't** add static shadows for depth — elevation is a state response, not a styling choice.
- **Don't** ship English-only strings or unthemed components; dark-mode parity and fil.json parity ship with the feature.
- **Don't** present estimates as promises — visuals and copy must preserve the hedged, honest framing.
