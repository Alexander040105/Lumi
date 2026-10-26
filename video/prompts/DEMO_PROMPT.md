# LUMI — Ten-Minute Video Demonstration Prompt

> **How to use:** hand this whole file to a video-capable agent (or follow it manually). Goal: a clear, properly sequenced **~10:00 MP4** demonstrating LUMI's major features — ready to present, playable without technical issues. This is a *recorded demonstration with AI narration*, not an interactive tour. Preferred engine: **HyperFrames** (`video/hyperframes/`); fallback: **Remotion** (`video/remotion/`, segment skeleton matches §3).

---

## 1. What this video is

A screen-recorded walkthrough of the real LUMI app running at `http://localhost:5173`, cut into titled segments, narrated by a professional AI voice, with the LUMI brand kit on titles/transitions. Viewer: a panel evaluating the system. It should feel like a competent colleague giving the tour — unhurried, honest, complete.

## 2. Recording setup

- [ ] Run the app: `cd react-frontend && npm run dev` → `http://localhost:5173` (backend must be up if the demo hits logged-in data — see `video/README.md` for the test account).
- [ ] Record at **1920×1080** (browser window maximized, zoom 100%, hide bookmarks bar — full-screen the window with F11 for clean chrome).
- [ ] Recorder: OBS Studio / Screenity / Playwright — one **separate clip per segment** below (makes re-takes cheap).
- [ ] Record the whole segment in **one continuous take**; don't chase the cursor. Cuts and zooms happen in editing, not live.
- [ ] Use a seeded **test account** (fill in `video/README.md` §accounts before recording). If an **admin** account exists, record segment 9; else skip it and pad segment 5 by 30 s.
- [ ] Land clips in `video/hyperframes/assets/shots/` or `video/remotion/public/shots/` as `NN-name.mp4`.

## 3. Run of show — ≈ 10:00 total

| # | Segment | Time | Must show | Narration outline (`voiceover/demo-script.md`) |
|---|---|---|---|---|
| 1 | Title & agenda | 0:00–0:20 | LUMI logo title card + 5-bullet agenda | Who LUMI is for; what this demo covers in order |
| 2 | Sign up & log in | 0:20–1:10 | Signup form → email confirmation note → login → landing on dashboard | "Create an account or sign in with Google — first thing you see is your dashboard" |
| 3 | Dashboard tour | 1:10–2:10 | Dashboard widgets, quick actions, profile area, navbar sections | What a signed-in user sees; where everything lives |
| 4 | **EcoSim end-to-end** | 2:10–4:40 | Municipality picker → energy inputs → run → results (savings, payback, CO₂) → AI analysis → provider recommendations → **Save simulation** | The hero flow, slow enough to read: "pick your municipality… set your budget… here's an honest estimate — sources cited" |
| 5 | **EnergyHub** | 4:40–7:10 | Overview stats → trend charts → source breakdown → forecast chart (~2030) → AI insight card | "The national picture: two decades of DOE data, where it's heading, explained in plain language" |
| 6 | Maps & geospatial | 7:10–8:00 | EnergyHub map: provincial suitability layers, legend, a drill-in | "Where each source fits best — the map answers it" |
| 7 | Saved work & security | 8:00–9:00 | Re-open the saved EcoSim → Saved Simulations list → Security settings (MFA toggle visible) | "Your work persists — log out, log back in, it's still there" |
| 8 | Admin *(optional)* | 9:00–9:30 | `/admin` area: users/analytics/config/usage/logs — whatever an admin account actually shows | "Administrators get their own console" — **only if an admin account exists; otherwise cut and pad §5** |
| 9 | Recap & close | 9:30–10:00 | Recap card (what we covered) + LUMI logo closing card | "Every estimate grounded in real data — LUMI" |

*Timing flex:* EcoSim and EnergyHub are the showcases — let them breathe; shave seconds from 3, 6, 8 if the cut runs long.

## 4. On-screen standards

- Each segment opens with a **lower-third or title card** naming it (use registry `lt-*` / caption blocks in HyperFrames; `SceneCard` titles in Remotion).
- **Punch-in/zoom** on key numbers (savings ₱, payback years, CO₂ t) for ~2 s each — don't leave the viewer hunting.
- Callouts/arrows only where the cursor action isn't obvious (municipality search, Save button, MFA toggle).
- Dead air > 1.5 s gets cut (`auto-editor` or manual trims); loading waits get a 2× speed-ramp or a cut to the loaded state.
- Captions: optional burned-in lower-third captions of the narration; keep inside 80% title-safe.

## 5. Technical spec & delivery

- **Output:** `video/out/LumiDemo.mp4` — MP4 H.264 + AAC, **1920×1080, 30 fps**, **~10:00 ± 20 s**.
- **Narration:** AI voiceover, same voice as the promo for consistency (see `voiceover/ENGINE_NOTES.md`); one `voice/NN.wav` per segment from `voiceover/demo-script.md`, laid under its segment; quiet music bed at −15 dB or none for the demo — narration clarity first.
- **Playback check (required):** `ffprobe` reports ~10:00 duration, non-zero audio stream; open in a browser/`vlc` and scrub start/middle/end; confirm no black gaps between segments and narration isn't clipped at cuts.
- Brand kit: same rules as `PROMO_PROMPT.md` §2 (Lumi Green family, Solar Gold sparingly, honest/advisor voice — say "estimated", never promise savings).
- Truthfulness: only show features that actually render (maps live inside EnergyHub; profile inside Dashboard; admin pages only if reachable by the test account).

## 6. Engine paths — pick ONE

### A. HyperFrames (preferred)

`video/hyperframes/`: invoke `/hyperframes` (type: explainer — read `references/types/explainer.md`). Structure: `index.html` root + one `compositions/NN-*.html` per segment; each segment = title card (2–3 s) + `<video muted src="assets/shots/NN.mp4">` + narration `<audio>` + zoom/callout overlays from the registry. Then `lint` → `check --json` → `snapshot` mid-segments → `preview --background` → `render --quality delivery --output ../out/LumiDemo.mp4`.

### B. Remotion

`video/remotion/`: `src/compositions/LumiDemo.tsx` already has the §3 segment `<Sequence>`s — replace each `SceneCard` with `<Video src={staticFile('shots/NN.mp4')} />` + `<Audio>` narration + overlay titles. `npm run render:demo` → `video/out/LumiDemo.mp4`. (Note: a 10-min Remotion render takes a while — `draft` concurrency first.)

## 7. Done means

- [ ] `video/out/LumiDemo.mp4` — ~10:00, plays start to finish with narration, no dead gaps.
- [ ] Every numbered segment present (or §8 correctly folded), titled, sequenced as §3.
- [ ] Real footage throughout; key numbers zoomed; brand kit on all title cards.
- [ ] Playback test passed in at least one player; file is the submission-ready copy.
