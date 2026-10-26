# LUMI Videos

Toolchain and workspace for producing LUMI's videos: a **marketing promo** (\~85 s) and a **guided feature demonstration** (no fixed duration — paced by narration). Two engines are scaffolded — **HyperFrames** (preferred, agent skills installed) and **Remotion** — plus free local TTS for voiceover.

## Layout

```
video/
├── prompts/        # the briefs — hand one to an agent to produce the video
│   ├── PROMO_PROMPT.md
│   ├── DEMO_PROMPT.md
│   └── REVISION_PROMPT.md   # v2 revision spec (zero AI mentions, no admin, pacing rules)
├── voiceover/      # narration scripts + free-TTS engine notes
├── hyperframes/    # HyperFrames project (index.html + compositions/, hyperframes@0.8.196 pinned)
├── remotion/       # Remotion project (scene skeletons matching the prompts)
└── out/            # rendered MP4s (gitignored)
```

## Quickstart

1. **Serve the production build** on `http://localhost:5173` (required — dev mode proxies `/api` to a local backend):
   `cd react-frontend && npm run build && npx vite preview --port 5173 --strictPort`
   The baked `VITE_API_BASE_URL` points at the deployed backend, and `localhost:5173` is already in its CORS allowlist.
2. **Create a demo account** (throwaway; needs the service-role key from root `.env`):
   `node video/tools/make-user.mjs` → writes `video/tools/creds.json` (**gitignored — never commit it**). To grant admin, set `public.user_roles.role='admin'` for that user id.
3. **Record footage:** `node video/tools/record/run.mjs all` (or one segment name) → `video/footage/*.mp4` + `*.json` marker sidecars. Requires the preview server from step 1. Each take fires a black **sync flash** near its start and drops timestamped `mark()`ers at every meaningful beat (search typed, option picked, results revealed…) — `assemble.mjs` uses them to cut footage to narration. The admin tour was cut (its User Usage table shows real user PII) — do not re-add without masking. EcoSim takes hide the wizard's "AI analysis" labels via a MutationObserver (`hideAiMentions`) and decline the optional-analysis checkbox; the landing take scrubs its "Powered by AI"/"AI Insights" chips (`scrubLandingAi`).
4. **Voiceover:** WAVs are already generated in `hyperframes/assets/voice/` (Kokoro `af_heart`). Regenerate with `npx hyperframes tts "<line>" -o assets/voice/NN.wav` or Edge-TTS — see `voiceover/ENGINE_NOTES.md`.
5. **Render the promo:** `cd video/hyperframes && npm run check && npm run render` → `video/out/LumiPromo.mp4` (~84 s).
6. **Assemble the demo:** `node video/tools/assemble.mjs` → `video/out/LumiDemo.mp4` (8 chapters). v3 is **beat-level**: every chapter is footage ranges bounded by calibrated markers, each paired with exactly the narration describing it — EcoSim narration can't drift over EnergyHub footage. Footage retimes to its narration (clamped 0.6–1.4×), then holds/trims so no stretch is un-narrated >4 s. VO is delayed while **mono**, then upmixed — never `adelay` on a stereo-formatted stream (that's what played all narration at t=0 on the right channel in v2). Post-build gates fail on: channel asymmetry, stream-duration mismatch, missing markers/WAVs, or VO overrunning its beat.
   - Gotchas: use `tpad stop_duration=` (seconds), not `stop=` (frames); cap each chapter encode with output `-t <segLen>` — input-side `-ss/-t` over-delivers frames and drifts late chapters.
7. **Verify:** `ffprobe -show_entries stream=codec_type,duration` — both streams should span the full runtime; spot-check frames at each beat boundary; probe the right channel inside slate windows for leaked speech (should be silent).

## Outputs

| File | Duration | Contents |
| --- | --- | --- |
| `video/out/LumiPromo.mp4` | 1:24 | HyperFrames promo — 9 scenes, Kokoro VO, music bed, real product preview |
| `video/out/LumiDemo.mp4` | 4:11 | 8 chapter slates + beat-synced walkthrough (welcome → login → dashboard → EcoSim [Calamba, Laguna] → EnergyHub → map → saved/security → recap) + VO/music |

## Test accounts

| Role | Email | Password | Notes |
| --- | --- | --- | --- |
| Demo user | _(deleted after production)_ | — | Recreate with `video/tools/make-user.mjs` |

## Toolchain status

| Tool | Version | Use |
| --- | --- | --- |
| `remotion` + `@remotion/cli` | 4.0.538 (global npm) | Remotion path |
| `hyperframes` | 0.8.196 (pinned in `hyperframes/package.json`) | HyperFrames path |
| FFmpeg | 9.0.2 (winget) | HyperFrames render + audio post |
| `edge-tts` | 7.3.1 (`py -m edge_tts`) | Free TTS option |
| `kokoro-onnx` + `soundfile` | pip | On-device TTS used by `npx hyperframes tts` |

## Troubleshooting

- `ffmpeg` **not found:** winget added it — open a *new* terminal (PATH refresh), or `winget install Gyan.FFmpeg`.
- `python` **opens the Microsoft Store:** Windows' App-execution alias stub shadows real Python. Fixed here by prepending `…\Python313` + `…\Python313\Scripts` to the *user* PATH — use a **new terminal** so it takes effect (or call `py` explicitly).
- **Remotion Chrome download:** first render/studio launch downloads a headless Chrome — allow it.
- **HyperFrames check fails:** `npx hyperframes doctor --json` diagnoses Chrome/FFmpeg.
- **Kokoro first run** downloads \~300 MB of models — expect a pause once (already done: `hyperframes/assets/voice/01.wav` proves it).
- **Preview stalls:** use `npx hyperframes preview --background` (agents) not `npm run dev`.

## Known warnings (assessed, no action needed)

- `npm audit` **in** `video/remotion`**:** 10 highs, all one transitive dep (`zod <4.6.6`) inside `@remotion/*` packages. `npm audit fix --force` would **downgrade** `@remotion/cli` off your pinned 4.0.538 — don't run it. Risk is a memory-exhaustion DoS on untrusted input to a local render tool; acceptable for this use. Revisit when Remotion ships a zod-bumped release.
- **Doctor flags:** `TTS (Kokoro)` may still report "not installed" in pre-PATH-fix shells; low free RAM (\~0.8 GB) and \~10 GB free disk — close apps / free space before long renders; Docker not running is fine (only needed for `--docker` renders); MusicGen/whisper-cpp are optional extras (`pip install transformers torch soundfile numpy` if you want generated BGM).