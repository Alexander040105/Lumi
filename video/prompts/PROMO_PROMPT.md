# LUMI — Marketing Promotional Video Prompt

> **How to use:** hand this whole file to a video-capable agent (or follow it manually). It is a complete, self-contained brief — everything needed is inside it. Preferred engine: **HyperFrames** (`video/hyperframes/`, skills installed); fallback: **Remotion** (`video/remotion/`, scene skeleton already matches §4). Produce a finished MP4, not an interactive demo.

---

## 1. Product card

| | |
|---|---|
| **Name** | LUMI |
| **Pitch** | Environmental intelligence for the Philippines — household renewable-energy simulation and national energy analytics, explained in plain language by AI. |
| **Purpose** | Help a Filipino homeowner, planner, or researcher answer: "Would solar/wind/hydro/geothermal actually work *here*, and is it worth it?" |
| **Tagline options** | "Your municipality. Your energy answer." · "Ground every decision in data." · "From climate data to household savings." |
| **Logo** | `react-frontend/public/logo.png` (use the real file; never redraw it) |
| **What it actually does** | EcoSim: per-municipality simulation of solar/wind/hydro/geothermal — costs, estimated savings, payback, CO₂ reduction, installer recommendations. EnergyHub: national analytics built on Philippine DOE data (2003–2025), trends and source breakdown, ARIMA forecasts toward ~2030, provincial suitability maps, AI-generated insights. AI assistant answers energy questions (Groq primary, Gemini fallback). Auth via Supabase (email + Google), optional MFA. English/Filipino UI. |

## 2. Brand kit (from `DESIGN.md` — do not deviate)

- **Lumi Green** `#2e5f2b` — primary, buttons, brand mark. All greens must stay in the Lumi family (hue ~108–142).
- **Solar Gold** `#f6d96a` — the only warm accent; reserve it for solar/savings/emphasis moments, max once or twice per scene.
- **Forest Ink** `#0f260d` text · **Pale Meadow** `#f4fbf4` light bg · **Forest Deep** `#133913` dark sections · **Card White** `#ffffff` surfaces · **Leaf Border** `#c6e0c6` strokes.
- Data colors only for data: Solar Glow `#ffe175`, Wind Green `#64be60`, Hydro = Lumi Green, Geothermal Ember `#cb6b0b`.
- **Type:** `ui-sans-serif, system-ui, sans-serif`. Display 800 weight for hero lines, semibold max elsewhere.
- **Voice:** the "Municipal Energy Advisor" — calm, trustworthy, plain-spoken, honest about estimates ("estimated", "may work in your area"). No alarmist crisis framing, no hype adjectives ("revolutionary", "game-changing").
- **No** pure blacks/grays, no second hue family (no blue/purple/teal chrome), no invented logos/icons.

## 3. Audience & goal

Panel/judges first, prospective users second: Filipino **homeowners**, **LGU/community energy planners**, **researchers & students**. Goal: after 2 minutes the viewer knows what LUMI does, who it's for, and wants to try it.

## 4. Storyboard — required 9 parts, target ≈ 2:00 (hard max 5:00)

| # | Part | Time | On screen | Visual direction | Narration line (see `voiceover/promo-script.md`) |
|---|---|---|---|---|---|
| 1 | Attention-grabbing opening | 0:00–0:10 | A Philippine map → a single household rooftop in sunlight | Quick zoom on the map; gold sunlight pulse on the roof | "What would solar actually save your household? Not a rough guess — a real answer, for your municipality." |
| 2 | Problem & market need | 0:10–0:25 | Split: scattered data sources / a confused user / a generic calculator | Flat cards on Pale Meadow; muted tone; no crisis imagery | "Renewable energy data is scattered, technical, and never about *your* town. Most people are left guessing." |
| 3 | Product introduction | 0:25–0:40 | Logo reveal, name + tagline, product purpose | Clean logo card on Pale Meadow, Lumi Green headline | "Meet LUMI — environmental intelligence for the Philippines. It turns real climate and energy data into answers you can act on." |
| 4 | Unique selling proposition | 0:40–0:55 | Municipality search narrowing 1,600+ LGUs to one | Show the picker zooming to one municipality | "Not generic advice. LUMI analyzes your specific municipality — over 1,600 of them — using Philippine DOE data and NASA climate records." |
| 5 | Key features & benefits | 0:55–1:25 | 3 quick beats: EcoSim results card → EnergyHub forecast chart → AI insight card | One beat each ~10 s; benefit caption under each feature | "Simulate solar, wind, hydro or geothermal — see estimated savings and payback. Explore national trends and forecasts to 2030. Ask the AI assistant anything, in English or Filipino." |
| 6 | Product preview | 1:25–1:50 | Real UI: EcoSim wizard → results; EnergyHub overview + map | Captured footage (checklist §6), subtle punch-in on key numbers | "This is it, working. Pick your municipality, set your budget — get an honest estimate. Explore the country's energy story in EnergyHub." |
| 7 | Target market | 1:50–2:05 | Three quiet cards: homeowner, LGU planner, researcher | Simple icon-free cards; advisor tone | "Built for homeowners weighing a rooftop, planners choosing where to invest, and researchers who need the real numbers." |
| 8 | Value proposition | 2:05–2:20 | Time/steps visual: scattered research vs one result card | Before/after wipe; keep honest | "Hours of research, answered in minutes — with the sources cited and the assumptions stated, not hidden." |
| 9 | Call to action | 2:20–2:30 | Logo + tagline + "Try LUMI" closing card | End on Lumi Green; hold logo to end | "LUMI — your municipality. Your energy answer. Try it today." |

*Shorter cut (~1:30):* trim beats in rows 5–6 to 8 s each, merge 7+8. *Longer (~3:00):* expand row 6 with a third UI capture and give each feature beat 12 s.

## 5. Technical spec

- **Output:** MP4 (H.264 + AAC), **1920×1080, 30 fps**, **1–3 min** (target 2:00–2:30, hard max 5:00).
- **Narration:** professional AI voiceover — warm, clear, mid-pace English (optionally generate a Filipino version after). Engine-agnostic: produce `voice/01.wav`…`voice/09.wav` from `voiceover/promo-script.md`, one file per storyboard row; see `voiceover/ENGINE_NOTES.md` for free engines (`npx hyperframes tts` → Kokoro, `py -m edge_tts`, or local Kokoro directly).
- **Music:** one calm, optimistic bed under the whole film, ducked ~12 dB under narration. Free paths: `media-use` resolve → local MusicGen / CC-BY track, or bundled library.
- **Sound design:** soft UI swoosh on scene transitions; a subtle "chime" on result reveals. Optional.
- **Captions:** burned-in or sidecar is acceptable; keep key text inside 80% title-safe.
- **Branding:** palette/type/rules from §2 throughout; logo visible in intro (§3 row 3) and outro (row 9).

## 6. Asset checklist (capture the REAL app)

- [ ] App running locally: `cd react-frontend && npm run dev` → `http://localhost:5173`
- [ ] Captures needed (screenshots or short clips, 1920×1080):
  - [ ] Home/landing hero
  - [ ] EcoSim wizard (municipality picker open)
  - [ ] EcoSim results (savings/payback cards + recommendation cards)
  - [ ] EnergyHub overview (charts/headline stats)
  - [ ] EnergyHub forecast chart
  - [ ] EnergyHub map view (provincial suitability)
  - [ ] (optional) AI assistant / insight card
- [ ] Fastest path: `npx hyperframes capture http://localhost:5173 --json` for the site subject, plus manual clips for the logged-in flows (sign in with the test account in `video/README.md`, then record each screen).
- [ ] Logo from `react-frontend/public/logo.png`. Fonts: system stack only.

## 7. Truthfulness rules (hard requirement)

**Allowed claims** (backed by the repo): 1,600+ municipalities; solar/wind/hydro/geothermal simulation; estimated costs, savings, payback, CO₂; Philippine DOE data 2003–2025; NASA POWER climate data; ARIMA-based forecasts toward ~2030; AI assistant (Groq primary, Gemini fallback); installer/provider recommendations; English/Filipino UI; free to use in this project context.

**Banned:** invented user counts, partnerships, awards, "official DOE product", guaranteed savings/returns, "100% accurate", real-time data, claims about pages that aren't reachable (no standalone map/chat/profile pages — maps live inside EnergyHub, profile lives in Dashboard).

## 8. Engine paths — pick ONE

### A. HyperFrames (preferred — agent skills installed)

Working dir: `video/hyperframes/`.

1. Invoke the `/hyperframes` skill; read `references/types/launch.md` and `references/story.md` — draft 3 storylines and pick the one closest to §4 (or go straight to SPEC since the storyboard is approved here).
2. Write `SPEC.md` per `references/spec.md`: every adjective → numbers; shot-by-shot timing from §4.
3. Scaffold scenes: `index.html` root + one `compositions/*.html` per storyboard row. Search the registry first (`npx hyperframes catalog --query "..."` → `npx hyperframes add <name>`) for title cards, kinetic type, `browser-device-stage` for UI captures, transitions, `before-after-wipe`.
4. Media: `npx hyperframes media-use resolve --type voice ...` or `npx hyperframes tts` (free Kokoro) for each narration line → `assets/voice/`; resolve a `bgm` bed → `assets/music/`; ingest captures → `assets/shots/`.
5. `npx hyperframes lint` → `npx hyperframes check --json` until clean → `npx hyperframes snapshot --at <scene midpoints>` and look at the frames → `npx hyperframes preview --background` for review → `npx hyperframes render --quality delivery --output ../out/LumiPromo.mp4`.

### B. Remotion

Working dir: `video/remotion/` (deps installed; `src/compositions/LumiPromo.tsx` already encodes §4 timing — replace `SceneCard` internals with real scenes, drop captures via `staticFile('shots/...')`, voiceover via `<Audio>` per Sequence). Preview: `npm run studio`. Render: `npm run render:promo` → `video/out/LumiPromo.mp4`.

## 9. Done means

- [ ] `video/out/LumiPromo.mp4` exists, `ffprobe` duration within spec, plays start-to-end with audio (test in VLC/browser).
- [ ] All 9 required parts present, on time, with narration synced to scenes.
- [ ] Brand kit honored; no banned claims; real UI footage in the preview section.
- [ ] Logo real file, end card holds ≥ 2 s.
