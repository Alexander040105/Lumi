# Free AI Voiceover Engines — installed options & how to pick

All four options below are **free** and installed/available on this machine. Generate the same two script lines in each, blind-listen, and pick one — then use that voice for **all** videos so they sound consistent.

| Engine | Quality | Speed | Notes |
|---|---|---|---|
| **A. `npx hyperframes tts`** (Kokoro, on-device) | Natural, warm | Fast after model download | **Recommended.** Integrated with the HyperFrames project — lands straight in `assets/voice/` with ledger entries. Uses `kokoro-onnx` (installed). First run downloads the model (~300 MB). |
| **B. Edge-TTS** (`py -m edge_tts`) | Very natural (Microsoft neural voices) | Fast, needs internet | Has Filipino voices (`fil-PH-BlessicaNeural`, `fil-PH-AngeloNeural`) for a localized cut. CLI: `py -m edge_tts --text "..." --voice en-US-ChristopherNeural --write-media out.mp3` |
| **C. Local Kokoro (direct)** | Natural | Slower (CPU) | Fully offline after install. `py -c "from kokoro_onnx import Kokoro; ..."` or via option A's CLI. Apache-2.0 weights — safe to publish. |
| **D. Piper** (optional, `pip install piper-tts`) | Robotic-leaning | Fastest | Fallback if A–C disappoint. |

## Option A — HyperFrames TTS (recommended for HyperFrames builds)

```bash
cd video/hyperframes
npx hyperframes tts --text "What would solar actually save your household?" --output assets/voice/01.wav
# see npx hyperframes tts --help for voice/style flags
```

## Option B — Edge-TTS

```bash
# list voices (incl. fil-PH):
py -m edge_tts --list-voices | grep -iE "en-US|fil"

# render one line (mp3; convert to wav with ffmpeg if needed):
py -m edge_tts --text "What would solar actually save your household?" \
  --voice en-US-ChristopherNeural --write-media voice/01.mp3
```

Good English voices: `en-US-ChristopherNeural` (M), `en-US-AriaNeural` / `en-US-JennyNeural` (F). Filipino: `fil-PH-BlessicaNeural` (F), `fil-PH-AngeloNeural` (M).

## Option C — Kokoro direct (offline)

```bash
py - <<'PY'
from kokoro_onnx import Kokoro
import soundfile as sf
k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")  # model files auto-download on first tts call via hyperframes, or fetch from the kokoro-onnx releases
audio, sr = k.create("Your line here", voice="af_heart", speed=1.0, lang="en-us")
sf.write("voice/01.wav", audio, sr)
PY
```

Voices: `af_heart` (F), `am_michael` (M), `bf_emma`, etc. — see kokoro-onnx docs.

## Post-processing (any engine)

- Normalize loudness so all lines match: `ffmpeg -i in.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 out.wav`
- Trim silence: `ffmpeg -i in.wav -af silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse out.wav`
- Lay under video as `<audio>` (HyperFrames) or `<Audio>` (Remotion); duck music ~12–15 dB under narration.

## Decision shortcut

If building in **HyperFrames** → use **A** (it writes into `assets/` correctly and mixes for you). If building in **Remotion** or want the **Filipino version** → use **B** (Edge-TTS has the only real fil-PH voices). **C** for fully-offline; **D** last resort.
