# LUMI Videos — Revision Brief (v2)

> **How to use:** hand this whole file to a video-capable agent. It is self-contained — everything needed is inside it or at the referenced paths. Goal: revised `video/out/LumiPromo.mp4` + `video/out/LumiDemo.mp4` that are truthful, properly paced, and free of dead air and overlapping narration.

You are revising TWO existing MP4s in `video/out/`. Everything needed already exists:
footage in `video/footage/`, compositions in `video/hyperframes/`, assembler in
`video/tools/assemble.mjs`, voice engine = `npx hyperframes tts` (Kokoro `af_heart`,
deterministic, free). Do NOT re-record footage unless a listed shot is missing.

## 0. Ground rules

- Master fact source: `D:\63947\Downloads\LUMIASDFSDFsdf.md` (thesis). Secondary:
  `video/sample_transcript1.md` (tone/structure model for the promo).
- Read `video/hyperframes/AGENTS.md` before touching any `.html` composition. After
  EVERY composition edit run `cd video/hyperframes && npm run check`; fix errors
  before continuing. Verify visually with `npx hyperframes snapshot --at <s>`.
- ffmpeg/ffprobe live under `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\
  ffmpeg-9.0.2-full_build\bin\`. `assemble.mjs` already resolves them.
- CRITICAL ffmpeg gotcha already fixed once — keep it: freeze-frames MUST use
  `tpad stop_mode=clone:stop_duration=<seconds>` (`stop=` counts FRAMES, not seconds).

## 1. Verified facts (use exactly; cite nothing else)

| Claim | Status |
|---|---|
| Municipalities covered | **1,800+** (table = 1,813 rows; say "more than 1,800") |
| Household options | solar, wind, hydro. Geothermal = **reference info only**, never a routine household pick |
| Engine | weighted multi-criteria recommendation (60% energy coverage + 40% source quality) |
| Forecasts | ARIMA on DOE annual data → national demand to **2030** |
| Sources | Philippine DOE, NASA POWER, Global Energy Monitor, PHIVOLCS |
| EcoSim outputs | estimated system cost, monthly savings, payback, CO₂ avoided; DOE Solar PV Installer Registry listings + screened retailers |
| Other real features | saved simulations, bilingual EN/FIL UI, MFA/TOTP (`/mfa`), Google sign-in, admin console (exists — do NOT show; footage contains real user emails) |
| Scope honesty | "preliminary estimates", "for decision support" — never "guaranteed", "accurate", "site survey" |
| Formal eval | CALABARZON households; nationwide coverage by design |

**BANNED words/frames in both videos:** "AI", "assistant", "chat", "ask anything",
"converse", any chat UI; "rooftop" (weigh/measuring claims); "ten-minute", "10-minute";
"1,600" / "sixteen hundred"; "guaranteed", "accurate", "certified", "official DOE";
real user emails anywhere. The AI-analysis card visible in EcoSim results footage is
fine — it's the real UI; narration simply never names it.

## 2. Promo — `video/hyperframes/index.html` (1920×1080, ~80–95s)

Same 9-scene skeleton, brand tokens unchanged (Outfit/Inter/Space Mono, Lumi Green
`#2e5f2b`, Solar Gold `#f6d96a` sparingly). Copy led by the sample transcript's energy.

Per-scene edits + narration (write TTS first, measure each WAV, THEN set scene
`data-duration` = VO + ~0.9s breathing; keep `data-start` contiguous, no gaps >1s):

| # | On-screen change | Narration (new `voice/NN.wav`, Kokoro af_heart) |
|---|---|---|
| S1 hook | Headline → "Which renewable energy actually works for your area?" · sub → "Solar, wind, or hydro — the answer depends on where you live." | Same question; add: "Most people guess. LUMI doesn't." |
| S2 problem | Keep 3 cards; tail → "Peak demand is projected to grow ~50% by 2030 — and most households are still guessing." (DOE PDP: 16.6→25.4 GW) | "Energy data is scattered, technical, and never about your town — while demand climbs. Most households are left guessing." |
| S3 reveal | unchanged | "Meet LUMI — environmental intelligence for the Philippines. Real climate and energy data, turned into answers you can act on." |
| S4 USP | Counter target **1600 → 1800**; caption → "cities and municipalities analyzed, individually" | "Not national averages. LUMI analyzes your specific municipality — more than eighteen hundred — using DOE statistics and NASA climate records." |
| S5 features | **Replace card 3** ("AI assistant 💬") → title "Next steps built in", desc "DOE-registered installers and screened retailers, matched to your area." (icon 🔧 or 📋). Cards 1/2/4 unchanged. | "EcoSim simulates solar, wind, and hydro for your town — estimated cost, savings, and payback. EnergyHub tracks national trends to 2030. Provincial maps show where each source fits best." |
| S6 preview | unchanged (seg05 EnergyHub footage in browser frame) | "This is it, working. Pick your municipality, enter your bill — get an honest estimate, assumptions shown." |
| S7 market | Homeowners card desc → "Deciding whether solar, wind, or hydro pays back at home." (drop "weighing a rooftop") | "For households choosing between solar, wind, and hydro — planners deciding where investment goes — and researchers who need the real numbers." |
| S8 value | unchanged | "Hours of research, answered in minutes — sources cited, assumptions stated." |
| S9 CTA | Headline → "Make smarter energy decisions with LUMI." · button → "Explore your energy potential today" | "Make smarter energy decisions with LUMI. Explore your energy potential today." |

Steps: rewrite `video/voiceover/promo-script.md` to match → `npx hyperframes tts` each
line → `ffprobe` each WAV → update `index.html` copy + `data-start`/`data-duration` for
scenes and `<audio>` elements + `#root data-duration` → re-trim `assets/music/bed98.wav`
to the new total with a 2s outro fade → `npm run check` → snapshots at every scene
midpoint → render → `video/out/LumiPromo.mp4` (overwrite). Duration = whatever the copy
needs (~75–95s expected). No padding.

## 3. Demo — `video/tools/assemble.mjs` + scripts (720p, no target length)

**Structure:** 8 chapters, admin removed. Edit `compositions/slates.html`: delete c08,
renumber c09→"Chapter 08 / 08", all "/ 09"→"/ 08", c01 sub → "A guided tour of the
whole system", c09 sub → "From your municipality to the national grid", duration 28.
Re-render slates.mp4.

**Script fixes** (`demo-script.md` + `demo-script-extra.md`):
- d01: drop "in the next ten minutes" → "we'll walk through the whole system".
- d04: "sixteen hundred"→"eighteen hundred"; "solar, wind, hydro, and geothermal side
  by side"→"solar, wind, and hydro side by side — geothermal appears as reference
  where it applies"; drop "the AI's plain-language analysis"→"a plain-language
  summary of what the numbers mean" (describe, never name AI).
- d04b: "sixteen-hundred-plus"→"eighteen-hundred-plus".
- d05: "two decades of DOE data"→"long-run Philippine DOE statistics" (unless the UI
  literally shows a 2003–2025 span — use what the UI shows); drop "the AI insight
  summarizes"→"the insight card calls out what matters this period".
- d07: keep MFA only if the toggle is visible in seg07 footage; else "password and
  sign-in security".
- d09: "from a household's rooftop question"→"from your town's energy question to the
  country's forecast".
- Remove all chat/assistant phrasing anywhere it appears. Then regenerate only the
  changed WAVs with `npx hyperframes tts`.

**Assembler rewrite (the actual fix)** — replace fixed `at:` offsets with a
duration-driven schedule, 8 segments:

```
per segment: LEAD_IN=1.8s after slate; VO lines back-to-back with GAP=0.8s
  (gap is measured between ffprobe'd WAV durations — overlap impossible by construction)
un-narrated footage >4s is NOT allowed:
  - VO shorter than footage → trim footage (`-t`) or raise `speed` so footage ends
    within ~2s of the last VO line + TAIL(1.5s)
  - VO longer than footage → `hold` = needed − footLen (freeze last frame; narration
    keeps going — that's fine, it's not dead air)
seg08/admin footage: DELETE from `segs`; also delete seg08 source file.
Keep: tpad stop_duration fix, music bed loop at vol 0.10, stereo 48k resample,
amix normalize=0, 1.5s in / 4s out fades, loudnorm, +faststart.
Print a timing report per segment: slate_end, each VO start/end, footage span,
un-narrated gaps — and FAIL if any gap >4s or any overlap exists.
```

Expected result ≈ 5–6.5 min. Write extra Kokoro lines ONLY where a real visual beat
is un-narrated (e.g., one line for seg05's provincial-demand scroll if >4s bare).
Never pad to a duration.

## 4. QC gates (all must pass)

1. `npm run check` clean on index.html + slates.html; snapshots at every scene
   midpoint and segment boundary look right.
2. ffprobe both outputs: video stream duration == container duration == audio
   duration (±0.1s). Extract frames at 0, mid, end−2s — non-black, correct content.
3. Audio audit on both MP4s: `ffmpeg -af astats` spot-check; programmatic gap check —
   no un-narrated stretch >4s (demo) / >1.5s (promo), zero VO overlaps, VO never
   clipped at scene cuts.
4. Claim lint: grep the final scripts for every BANNED term — zero hits. Read every
   spoken line against §1's fact table.
5. Play both MP4s start-to-finish (or scrub ≥6 points each). Report: durations,
   file sizes, segment timing table, frame paths.

## 5. Do NOT

- Do not re-record footage, add app features, touch backend/frontend code, or
  reposition LUMI as a chat product. Do not keep seg08 anywhere (privacy).
- Do not reintroduce duration targets, filler narration, or "watch the cursor do
  nothing" dwell.
