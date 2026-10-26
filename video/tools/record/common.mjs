// Shared recording helpers for LUMI demo/promo footage.
// Uses playwright-core with the already-downloaded ms-playwright chromium.
import { chromium } from "playwright-core";
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

// repo root = three levels up from video/tools/record/
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const FOOTAGE = path.join(ROOT, "video", "footage");
export const CREDS = JSON.parse(fs.readFileSync(path.join(ROOT, "video", "tools", "creds.json"), "utf8"));
export const BASE = "http://localhost:5173";

function findChromium() {
  const dir = path.join(os.homedir(), "AppData", "Local", "ms-playwright");
  const builds = fs.readdirSync(dir).filter((d) => /^chromium-\d+$/.test(d)).sort().reverse();
  for (const b of builds) {
    const exe = path.join(dir, b, "chrome-win64", "chrome.exe");
    if (fs.existsSync(exe)) return exe;
  }
  throw new Error("no chromium build found under " + dir);
}

function findFfmpeg() {
  try { execSync("ffmpeg -version", { stdio: "ignore" }); return "ffmpeg"; } catch {}
  const g = path.join(os.homedir(), "AppData", "Local", "Microsoft", "WinGet", "Packages");
  for (const p of fs.readdirSync(g)) {
    if (!p.startsWith("Gyan.FFmpeg")) continue;
    const exe = path.join(g, p, "ffmpeg-9.0.2-full_build", "bin", "ffmpeg.exe");
    if (fs.existsSync(exe)) return `"${exe}"`;
  }
  throw new Error("ffmpeg not found");
}
const FFMPEG = findFfmpeg();

export async function newSession(name) {
  const browser = await chromium.launch({
    executablePath: findChromium(),
    headless: true,
    args: ["--disable-blink-features=AutomationControlled"],
  });
  const videoDir = path.join(FOOTAGE, "raw-" + name);
  fs.mkdirSync(videoDir, { recursive: true });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: videoDir, size: { width: 1920, height: 1080 } },
    locale: "en-US",
  });
  // Playwright video t=0 ≈ page creation; markers are wall-clock offsets from
  // this instant, so assemble.mjs can cut beats at action boundaries.
  const t0 = Date.now();
  const page = await context.newPage();
  page.setDefaultTimeout(45000);
  const markers = [];
  return {
    page,
    mark(label) { markers.push({ label, t: +((Date.now() - t0) / 1000).toFixed(2) }); },
    async finish() {
      await context.close();
      await browser.close();
      const webm = fs.readdirSync(videoDir).find((f) => f.endsWith(".webm"));
      if (!webm) throw new Error("no webm produced for " + name);
      const out = path.join(FOOTAGE, name + ".mp4");
      execSync(`${FFMPEG} -y -i "${path.join(videoDir, webm)}" -c:v libx264 -pix_fmt yuv420p -movflags +faststart "${out}"`, { stdio: "pipe" });
      const meta = execSync(`${FFMPEG.replace("ffmpeg", "ffprobe").replace(/ffmpeg\.exe"$/, 'ffprobe.exe"')} -v error -show_entries format=duration -of csv=p=0 "${out}"`).toString().trim();
      if (markers.length) {
        fs.writeFileSync(
          path.join(FOOTAGE, name + ".json"),
          JSON.stringify({ clip: name + ".mp4", duration: +meta, markers }, null, 2)
        );
      }
      fs.rmSync(videoDir, { recursive: true, force: true });
      console.log(`${name}: ${out} (${meta}s, ${markers.length} markers)`);
    },
  };
}

export async function login(page, session = null) {
  await page.goto(BASE + "/login", { waitUntil: "networkidle" });
  if (session) await syncFlash(session); // fires right after the login page paints
  await page.getByPlaceholder(/email/i).first().fill(CREDS.email);
  await page.getByPlaceholder(/password/i).first().fill(CREDS.password);
  await page.locator("form").getByRole("button", { name: /^sign in$/i }).click();
  await page.waitForURL(/dashboard|ecosim|energyhub/, { timeout: 60000 });
  await page.waitForLoadState("networkidle").catch(() => {});
}

export const hold = (page, ms) => page.waitForTimeout(ms);

// Sync pulse: 600ms fullscreen black so assemble.mjs can find the wall-clock→video
// offset with blackdetect. Call right after the first page paint of each take;
// footage before the flash is dead load-time anyway and gets trimmed.
export async function syncFlash(session) {
  await session.page.evaluate(() => {
    const d = document.createElement("div");
    d.id = "__syncflash";
    d.style.cssText = "position:fixed;inset:0;background:#000;z-index:2147483647";
    document.body.appendChild(d);
  });
  session.mark("sync");
  await session.page.waitForTimeout(650);
  await session.page.evaluate(() => document.getElementById("__syncflash")?.remove());
}

// Hide shipped-UI placeholders we don't want on camera (e.g. EcoSim's "AI
// Analysis" card — includeAi is hardcoded false, so it sits pending forever).
export async function hideCardByHeading(page, headingText) {
  await page.evaluate((txt) => {
    const el = [...document.querySelectorAll("h1,h2,h3,h4,p,div")]
      .find((e) => e.childElementCount === 0 && e.textContent.trim() === txt);
    if (!el) return;
    let node = el;
    for (let i = 0; i < 7 && node.parentElement; i++) {
      node = node.parentElement;
      if (/rounded|border|card/i.test(node.className) && node.offsetHeight > 60) {
        node.style.display = "none";
        return;
      }
    }
    el.style.display = "none";
  }, headingText).catch(() => {});
}

// The video carries a zero-AI-mention rule: hide every "AI analysis" label the
// wizard/results render (sidebar summary row, step-5 review cell, step-4 opt-in
// block, results card). Installs a MutationObserver so React re-renders keep
// the labels hidden for the life of the document; re-call after full reloads.
export async function hideAiMentions(page) {
  await page.evaluate(() => {
    const zap = () => {
      for (const el of document.querySelectorAll("p,span,div,label")) {
        if (el.childElementCount === 0 && /^\s*AI analysis\s*$/i.test(el.textContent)) {
          const p = el.parentElement;
          if (!p) continue;
          // step-5 review cell: the leaf sits in a flex row next to an Edit
          // button — hide the whole bordered cell (one level up), not the Card
          if (p.querySelector("button")) {
            (p.parentElement || p).style.display = "none";
          } else if (p.childElementCount <= 2 && !/card|content/i.test(p.className)) {
            p.style.display = "none"; // sidebar summary row: plain div, two <p>s
          }
        }
      }
      const aiInput = document.getElementById("ecosim-include-ai"); // step-4 opt-in block
      if (aiInput) {
        const block = aiInput.parentElement?.parentElement;
        if (block) block.style.display = "none";
      }
      const head = [...document.querySelectorAll("h1,h2,h3,h4,p,div")] // results "AI Analysis" card
        .find((e) => e.childElementCount === 0 && e.textContent.trim() === "AI Analysis");
      if (head) {
        let n = head;
        for (let i = 0; i < 7 && n.parentElement; i++) {
          n = n.parentElement;
          if (/rounded|border|card/i.test(n.className) && n.offsetHeight > 60) { n.style.display = "none"; break; }
        }
      }
    };
    zap();
    if (!window.__zapAI) {
      window.__zapAI = new MutationObserver(zap);
      window.__zapAI.observe(document.body, { childList: true, subtree: true });
    }
  }).catch(() => {});
}

// Landing page marketing chips the videos must not show ("Powered by AI"
// badge, "AI Insights" tag) — plus soften the one sentence naming AI.
// Static page: one-shot scrub is enough, no observer needed.
export async function scrubLandingAi(page) {
  await page.evaluate(() => {
    for (const el of document.querySelectorAll("span,p,div")) {
      if (el.childElementCount !== 0) continue;
      const tx = el.textContent;
      if (/^\s*powered by ai\s*$/i.test(tx) || /^\s*ai insights\s*$/i.test(tx)) {
        el.style.display = "none";
      } else if (/ai-driven/i.test(tx)) {
        el.textContent = tx.replace(/AI-driven/i, "guided");
      }
    }
  }).catch(() => {});
}

export async function slowScroll(page, px, steps = 20, pause = 60) {
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, px / steps);
    await page.waitForTimeout(pause);
  }
}

export async function hideOverlays(page) {
  // Dismiss cookie banners/toasts that could sit in frame.
  await page.evaluate(() => {
    document.querySelectorAll('[data-sonner-toaster], [class*="toaster"]').forEach((el) => (el.style.display = "none"));
  }).catch(() => {});
}
