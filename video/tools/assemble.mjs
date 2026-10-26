// LUMI demo assembler v3: chapter slates + beat-level footage + narration + music → LumiDemo.mp4
//
// v3 changes:
// - chapters are built from BEATS: each beat is a footage range (cut at recorder
//   markers from footage/<clip>.json sidecars) paired with the narration line(s)
//   that describe exactly that moment — VO can no longer drift off its footage.
// - footage is retimed to its narration (speed clamped [MIN_SPEED, MAX_SPEED]),
//   then held/trimmed so no stretch goes un-narrated > MAXBARE seconds.
// - AUDIO BUG FIX: VO is delayed while MONO, then upmixed to stereo
//   (aformat=mono → adelay → pan). v2 delayed stereo with a single adelay value,
//   which only delayed channel 0 — every VO played at t=0 on the right channel.
// - QC gates fail the build on: missing VO/markers, channel asymmetry
//   (the v2 bug's signature), or silence outside the narration schedule.
// Usage: node assemble.mjs
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const F = path.join(ROOT, "video", "footage");
const A = path.join(ROOT, "video", "hyperframes", "assets");
const WORK = path.join(ROOT, "video", "footage", "_work");
const OUT = path.join(ROOT, "video", "out");
fs.mkdirSync(WORK, { recursive: true });
fs.mkdirSync(OUT, { recursive: true });

const BIN = path.join(os.homedir(), "AppData", "Local", "Microsoft", "WinGet", "Packages");
let FFMPEG = "ffmpeg", FFPROBE = "ffprobe";
for (const p of fs.readdirSync(BIN)) {
  if (p.startsWith("Gyan.FFmpeg")) {
    FFMPEG = `"${path.join(BIN, p, "ffmpeg-9.0.2-full_build", "bin", "ffmpeg.exe")}"`;
    FFPROBE = `"${path.join(BIN, p, "ffmpeg-9.0.2-full_build", "bin", "ffprobe.exe")}"`;
  }
}
const dur = (f) => parseFloat(execSync(`${FFPROBE} -v error -show_entries format=duration -of csv=p=0 "${f}"`).toString());
const run = (cmd) => { console.log(">>", cmd.slice(0, 140) + (cmd.length > 140 ? "…" : "")); execSync(cmd, { stdio: "pipe" }); };

// ---------- pacing constants ----------
const SLATE = `${F}/slates.mp4`;
const SLATE_DUR = 3.5;
const BEAT_LEAD = 0.5;   // silence at beat start before its first VO line
const BEAT_TAIL = 0.6;   // silence after a beat's last VO line
const LINE_GAP = 0.7;    // between consecutive VO lines inside one beat
const MIN_SPEED = 0.6, MAX_SPEED = 1.4; // retime bounds — stays natural-looking
const MAXBARE = 4;       // max un-narrated footage seconds per beat

// ---------- chapter → beats model ----------
// from/to are marker labels in footage/<clip>.json; "start"/"end" are clip bounds.
const chapters = [
  { n: "01", slate: 0, beats: [
    { clip: "seg01-landing", from: "start", to: "end", vo: ["d01"] },
  ]},
  { n: "02", slate: 1, beats: [
    { clip: "seg02-account", from: "start", to: "loginform", vo: ["d02a"] },
    { clip: "seg02-account", from: "loginform", to: "end", vo: ["d02b"] },
  ]},
  { n: "03", slate: 2, beats: [
    { clip: "seg03-dashboard", from: "top", to: "quick-actions", vo: ["d03a"] },
    { clip: "seg03-dashboard", from: "quick-actions", to: "saved", vo: ["d03b"] },
    { clip: "seg03-dashboard", from: "saved", to: "end", vo: ["d03c"] },
  ]},
  { n: "04", slate: 3, beats: [
    { clip: "seg04-ecosim", from: "wizard-start", to: "location-selected", vo: ["d04a", "d04b"] },
    { clip: "seg04-ecosim", from: "location-selected", to: "rate-filled", vo: ["d04c"] },
    { clip: "seg04-ecosim", from: "rate-filled", to: "review", vo: ["d04d"] },
    { clip: "seg04-ecosim", from: "review", to: "computed", vo: ["d04e"] },
    { clip: "seg04-ecosim", from: "computed", to: "results", vo: [] }, // modal → reveal, a breath
    { clip: "seg04-ecosim", from: "results", to: "breakdown", vo: ["d04f"] },
    { clip: "seg04-ecosim", from: "breakdown", to: "summary", vo: ["d04g"] },
    { clip: "seg04-ecosim", from: "summary", to: "end", vo: ["d04h"] },
  ]},
  { n: "05", slate: 4, beats: [
    { clip: "seg05-energyhub", from: "overview", to: "trends", vo: ["d05a"] },
    { clip: "seg05-energyhub", from: "trends", to: "breakdown", vo: ["d05b"] },
    { clip: "seg05-energyhub", from: "breakdown", to: "benchmark", vo: ["d05c"] },
    { clip: "seg05-energyhub", from: "benchmark", to: "end", vo: ["d05d"] },
  ]},
  { n: "06", slate: 5, beats: [
    { clip: "seg06-maps", from: "map-visible", to: "layer-switch", vo: ["d06a"] },
    { clip: "seg06-maps", from: "layer-switch", to: "zoom", vo: ["d06b"] },
    { clip: "seg06-maps", from: "zoom", to: "end", vo: ["d06c"] },
  ]},
  { n: "07", slate: 6, beats: [
    { clip: "seg07-saved", from: "list", to: "opening", vo: ["d07a"] },
    { clip: "seg07-saved", from: "opening", to: "open-sim", vo: ["d07b"] },
    { clip: "seg07-saved", from: "open-sim", to: "security", vo: [] }, // navigate back → settings
    { clip: "seg07-saved", from: "security", to: "end", vo: ["d07c"] },
  ]},
  { n: "08", slate: 7, beats: [
    { clip: "seg08-recap", from: "recap", to: "end", vo: ["d08"] },
  ]},
];

// ---------- resolve markers (flash-calibrated) ----------
// Recorder markers are wall-clock offsets from page creation; the video clock
// starts ~2-6s later (browser/context/encoder warmup). Every take fires a
// 650ms black syncFlash — blackdetect locates it in the video, and
// offset = syncMarker.t - blackStart converts marker time → video time.
// "start" resolves to just past the flash (dead load footage trimmed).
const sidecars = {};
const calib = {};
const calibrate = (clip) => {
  if (calib[clip]) return calib[clip];
  const p = `${F}/${clip}.json`;
  if (!fs.existsSync(p)) throw new Error(`missing sidecar ${p}`);
  const sc = JSON.parse(fs.readFileSync(p, "utf8"));
  sidecars[clip] = sc;
  const sync = sc.markers.find((x) => x.label === "sync");
  let offset = 0, clipStart = 0;
  try {
    const out = execSync(
      `${FFMPEG} -ss 0 -t 20 -i "${F}/${clip}.mp4" -vf blackdetect=d=0.2:pix_th=0.08 -an -f null - 2>&1`,
      { shell: true }
    ).toString();
    const bs = out.match(/black_start:([\d.]+)/), be = out.match(/black_end:([\d.]+)/);
    if (sync && bs && be) {
      offset = sync.t - parseFloat(bs[1]);
      clipStart = parseFloat(be[1]) + 0.15;
      console.log(`calib ${clip}: flash@${bs[1]}s sync@${sync.t}s offset=${offset.toFixed(2)}s`);
    } else {
      console.warn(`  ! no sync flash in ${clip} — markers used raw (drift possible)`);
    }
  } catch { console.warn(`  ! blackdetect failed for ${clip}`); }
  calib[clip] = { offset, clipStart, sc };
  return calib[clip];
};
const marker = (clip, label) => {
  const { offset, clipStart, sc } = calibrate(clip);
  if (label === "start") return clipStart;
  if (label === "end") return sc.duration;
  const m = sc.markers.find((x) => x.label === label);
  if (!m) throw new Error(`marker "${label}" not in ${clip}.json (have: ${sc.markers.map((x) => x.label).join(", ")})`);
  return Math.min(m.t - offset, sc.duration);
};

// ---------- schedule ----------
const problems = [];
const report = [];
const voWindows = []; // absolute {start,end} for QC gates
let t = 0;
for (const ch of chapters) {
  const chStart = t;
  let cur = SLATE_DUR;
  for (const b of ch.beats) {
    const clipPath = `${F}/${b.clip}.mp4`;
    if (!fs.existsSync(clipPath)) { problems.push(`missing footage ${b.clip}.mp4`); continue; }
    const from = marker(b.clip, b.from), to = marker(b.clip, b.to);
    const rawLen = to - from;
    if (rawLen < 1) { problems.push(`ch${ch.n} ${b.clip}: beat ${b.from}→${b.to} is ${rawLen.toFixed(1)}s`); continue; }

    b.voDurs = b.vo.map((f) => {
      const p = `${A}/voice/${f}.wav`;
      if (!fs.existsSync(p)) { problems.push(`missing VO ${f}.wav`); return 0; }
      return dur(p);
    });
    const voSpan = b.voDurs.reduce((a, x) => a + x, 0) + LINE_GAP * Math.max(0, b.vo.length - 1);
    const needed = BEAT_LEAD + voSpan + BEAT_TAIL;

    // retime so footage ≈ narration span; hold if too short, trim if too long
    const speed = Math.min(MAX_SPEED, Math.max(MIN_SPEED, rawLen / needed));
    let footLen = rawLen / speed;
    let hold = Math.max(0, needed - footLen);
    let srcLen = rawLen;
    if (footLen - needed > MAXBARE) { footLen = needed + 2; srcLen = footLen * speed; hold = 0; }
    b.plan = { from, rawLen, speed, footLen, srcLen, hold, needed, bare: footLen - (needed - BEAT_TAIL) };
    if (!b.vo.length) { // transition beats: natural speed; long ones keep the arrival tail
      let sFrom = from, srcLen = rawLen;
      if (rawLen > MAXBARE + 1) { sFrom = to - (MAXBARE + 1); srcLen = MAXBARE + 1; }
      b.plan = { from: sFrom, rawLen, speed: 1, footLen: srcLen, srcLen, hold: 0, needed: srcLen, bare: srcLen };
    }

    // VO offsets (absolute)
    let at = chStart + cur + BEAT_LEAD;
    b.voAt = [];
    b.vo.forEach((f, i) => { b.voAt.push(at); voWindows.push({ f, start: at, end: at + b.voDurs[i] }); at += b.voDurs[i] + LINE_GAP; });
    if (at - LINE_GAP - (chStart + cur + footLen + hold) > 0.5) problems.push(`ch${ch.n} beat ${b.from}: VO overruns beat end`);

    report.push(
      `ch${ch.n} ${b.from}→${b.to}: raw=${rawLen.toFixed(1)}s speed=${speed.toFixed(2)} foot=${footLen.toFixed(1)}s` +
      (hold > 0 ? ` hold=+${hold.toFixed(1)}` : "") +
      ` vo=[${b.vo.map((f, i) => `${f}@${b.voAt[i].toFixed(1)}`).join(",")}]`
    );
    cur += footLen + hold;
  }
  ch.segLen = cur;
  ch.absStart = chStart;
  t += cur;
}
const TOTAL = t;
console.log("---- schedule ----");
report.forEach((r) => console.log(r));
console.log(`total ${TOTAL.toFixed(1)}s (${(TOTAL / 60).toFixed(1)}min) — ${voWindows.length} VO lines`);
if (problems.length) { console.error("SCHEDULE FAILED:\n" + problems.join("\n")); process.exit(1); }

// ---------- per-chapter silent video: slate + beats ----------
const segFiles = [];
let ci = 0;
for (const ch of chapters) {
  const inputs = [`-ss ${ch.slate * SLATE_DUR} -t ${SLATE_DUR} -i "${SLATE}"`];
  const filters = [`[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1,format=yuv420p[v0]`];
  const labels = ["[v0]"];
  ch.beats.forEach((b, i) => {
    const idx = i + 1;
    inputs.push(`-ss ${b.plan.from.toFixed(2)} -t ${b.plan.srcLen.toFixed(2)} -i "${F}/${b.clip}.mp4"`);
    filters.push(
      `[${idx}:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1,setpts=${(1 / b.plan.speed).toFixed(4)}*PTS,tpad=stop_mode=clone:stop_duration=${b.plan.hold.toFixed(3)},format=yuv420p[v${idx}]`
    );
    labels.push(`[v${idx}]`);
  });
  filters.push(`${labels.join("")}concat=n=${labels.length}:v=1:a=0[v]`);
  const out = `${WORK}/ch_${ch.n}.mp4`;
  // -t on the OUTPUT caps the chapter at its scheduled length — input-side
  // -ss/-t over-delivers a few frames per beat, which would drift VO late
  run(`${FFMPEG} -y ${inputs.join(" ")} -filter_complex "${filters.join(";")}" -map "[v]" -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -t ${ch.segLen.toFixed(3)} "${out}"`);
  segFiles.push(out);
  ci++;
}

// ---------- concat ----------
const list = `${WORK}/concat.txt`;
fs.writeFileSync(list, segFiles.map((f) => `file '${f.replace(/\\/g, "/")}'`).join("\n"));
run(`${FFMPEG} -y -f concat -safe 0 -i "${list}" -c copy "${WORK}/demo_video.mp4"`);

// ---------- audio: music bed + VO (delay while MONO, then upmix — the v2 fix) ----------
const inputs = [`-stream_loop -1 -i "${A}/music/bed.wav"`];
const voMix = [];
let part = "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.10[bed];";
let idx = 1;
for (const ch of chapters) for (const b of ch.beats) {
  b.vo.forEach((f, i) => {
    inputs.push(`-i "${A}/voice/${f}.wav"`);
    part += `[${idx}:a]aresample=48000,aformat=channel_layouts=mono,adelay=${Math.round(b.voAt[i] * 1000)},pan=stereo|c0=c0|c1=c0[a${idx}];`;
    voMix.push(`[a${idx}]`);
    idx++;
  });
}
part += `[bed]${voMix.join("")}amix=inputs=${1 + voMix.length}:normalize=0,afade=t=in:d=1.5,afade=t=out:st=${(TOTAL - 4).toFixed(1)}:d=4,atrim=0:${TOTAL.toFixed(1)},loudnorm=I=-16:TP=-1.5:LRA=11[aout]`;
run(`${FFMPEG} -y ${inputs.join(" ")} -filter_complex "${part}" -map "[aout]" -c:a aac -b:a 160k "${WORK}/demo_audio.m4a"`);

// ---------- mux ----------
run(`${FFMPEG} -y -i "${WORK}/demo_video.mp4" -i "${WORK}/demo_audio.m4a" -map 0:v -map 1:a -c:v copy -c:a copy -movflags +faststart "${OUT}/LumiDemo.mp4"`);

// ---------- QC gates ----------
const finalPath = `${OUT}/LumiDemo.mp4`;
const meanVol = (ch, start, len) => parseFloat(
  execSync(`${FFMPEG} -ss ${start} -t ${len} -i "${finalPath}" -af "pan=mono|c0=${ch},volumedetect" -f null - 2>&1`, { shell: true })
    .toString().match(/mean_volume: (-?[\d.]+)/)?.[1] || "0"
);
// gate 1: channel symmetry — the v2 bug put all VO on the right at t=0.
// music-only window (inside first slate) and a mid VO window must be balanced.
const mid = voWindows[Math.floor(voWindows.length / 2)];
const checks = [
  { name: "music-only window (L)", l: meanVol("FL", 1.2, 2), r: meanVol("FR", 1.2, 2) },
  { name: `VO window ${mid.f} (L)`, l: meanVol("FL", mid.start + 0.3, 2), r: meanVol("FR", mid.start + 0.3, 2) },
];
for (const c of checks) {
  console.log(`gate ${c.name}: L=${c.l}dB R=${c.r}dB`);
  if (Math.abs(c.l - c.r) > 4) { console.error(`CHANNEL ASYMMETRY — ${c.name} L/R differ by ${Math.abs(c.l - c.r).toFixed(1)}dB`); process.exit(1); }
}
// gate 2: stream parity
const v = parseFloat(execSync(`${FFPROBE} -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "${finalPath}"`).toString());
const a = parseFloat(execSync(`${FFPROBE} -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 "${finalPath}"`).toString());
console.log(`streams v=${v}s a=${a}s`);
if (Math.abs(v - TOTAL) > 0.2 || Math.abs(a - TOTAL) > 0.5) { console.error("STREAM PARITY FAILED"); process.exit(1); }
console.log("DONE", finalPath, dur(finalPath), "s");
