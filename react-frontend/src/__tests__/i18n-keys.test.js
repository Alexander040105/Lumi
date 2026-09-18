import { describe, it, expect } from "vitest";
import en from "../i18n/en.json";
import fil from "../i18n/fil.json";

// Scan every source file for literal t("dotted.key") calls. Dynamic keys
// (t(`prefix.${var}`) or t("prefix." + x)) are excluded — their templates
// can't be statically resolved, and deliberately end with ".".
const sources = import.meta.glob("../**/*.{js,jsx,ts,tsx}", {
  query: "?raw",
  import: "default",
  eager: true,
});

const KEY_RE = /t\(\s*["'`]([a-zA-Z0-9_.]+)["'`]/g;

function flatten(obj, prefix = "") {
  const out = {};
  for (const [k, v] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) {
      Object.assign(out, flatten(v, path));
    } else {
      out[path] = v;
    }
  }
  return out;
}

function usedKeys() {
  const keys = new Set();
  for (const code of Object.values(sources)) {
    for (const match of code.matchAll(KEY_RE)) {
      const key = match[1];
      if (key.includes(".") && !key.endsWith(".")) keys.add(key);
    }
  }
  return [...keys].sort();
}

const enKeys = flatten(en);
const filKeys = flatten(fil);
const used = usedKeys();

describe("i18n key coverage", () => {
  it("extracts a sane number of literal t() keys", () => {
    expect(used.length).toBeGreaterThan(100);
  });

  it("every literal t() key exists in en.json", () => {
    const missing = used.filter((k) => !(k in enKeys));
    expect(missing).toEqual([]);
  });

  it("every literal t() key exists in fil.json", () => {
    const missing = used.filter((k) => !(k in filKeys));
    expect(missing).toEqual([]);
  });
});
