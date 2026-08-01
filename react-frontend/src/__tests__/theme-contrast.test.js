import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const cssPath = resolve(__dirname, "../styles/globals.css");
const css = readFileSync(cssPath, "utf-8");

function removeComments(source) {
  return source.replace(/\/\*[\s\S]*?\*\//g, "");
}

function parseBlock(name) {
  const cleaned = removeComments(css);
  const regex = new RegExp(`${name}\\s*\\{([^}]+)\\}`, "i");
  const match = cleaned.match(regex);
  if (!match) return {};
  const block = match[1];
  const vars = {};
  const propRegex = /--([\w-]+):\s*([0-9.\s%]+);/g;
  let m;
  while ((m = propRegex.exec(block)) !== null) {
    const key = `--${m[1]}`;
    const value = m[2].trim();
    vars[key] = value;
  }
  return vars;
}

function parseHsl(hslString) {
  const parts = hslString.split(/\s+/).map((p) => parseFloat(p.replace(/[^0-9.]/g, "")));
  return [parts[0] || 0, parts[1] || 0, parts[2] || 0];
}

function hslToRgb(h, s, l) {
  s /= 100;
  l /= 100;
  const k = (n) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  return [f(0), f(8), f(4)];
}

function relativeLuminance(rgb) {
  const [r, g, b] = rgb.map((c) => {
    c = c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    return c;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrastRatio(fg, bg) {
  const l1 = relativeLuminance(fg);
  const l2 = relativeLuminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function getColor(variables, key) {
  const raw = variables[key];
  if (!raw) throw new Error(`Missing CSS variable ${key}`);
  const [h, s, l] = parseHsl(raw);
  return hslToRgb(h, s, l);
}

const light = parseBlock(":root");
const dark = parseBlock("\\.dark");

const PAIRS = [
  ["--foreground", "--background"],
  ["--card-foreground", "--card"],
  ["--popover-foreground", "--popover"],
  ["--primary-foreground", "--primary"],
  ["--secondary-foreground", "--secondary"],
  ["--muted-foreground", "--muted"],
  ["--accent-foreground", "--accent"],
  ["--destructive-foreground", "--destructive"],
  ["--warning-foreground", "--warning"],
];

function assertContrast(theme, name) {
  for (const [fgKey, bgKey] of PAIRS) {
    const fg = getColor(theme, fgKey);
    const bg = getColor(theme, bgKey);
    const ratio = contrastRatio(fg, bg);
    expect(
      ratio,
      `${name}: ${fgKey} on ${bgKey} must meet WCAG 2.1 AA (4.5:1)`
    ).toBeGreaterThanOrEqual(4.5);
  }
}

describe("Theme color contrast", () => {
  it("meets WCAG 2.1 AA for light mode", () => {
    assertContrast(light, "light");
  });

  it("meets WCAG 2.1 AA for dark mode", () => {
    assertContrast(dark, "dark");
  });

  it("does not use a cream/yellow background in light mode", () => {
    const [h, s, l] = parseHsl(light["--background"]);
    expect(
      h,
      "light mode background hue should be in the green family, not yellow/cream"
    ).toBeGreaterThanOrEqual(80);
    expect(h).toBeLessThanOrEqual(150);
  });
});
