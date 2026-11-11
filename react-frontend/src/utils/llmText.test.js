import { describe, it, expect } from "vitest";
import { sanitizeLLMOutput } from "./llmText";

describe("sanitizeLLMOutput", () => {
  it("does not truncate long text (regression: panels ended mid-sentence at 900 chars)", () => {
    const sentence = "The Department of Energy should act now. ";
    const long = sentence.repeat(40); // ~1,600 chars
    const out = sanitizeLLMOutput(long);
    expect(out.length).toBeGreaterThan(1200);
    expect(out.endsWith("…")).toBe(false);
    expect(out.endsWith("...")).toBe(false);
    expect(out.endsWith(".")).toBe(true);
    expect(out).toBe(long.trim());
  });

  it("returns empty string for empty input", () => {
    expect(sanitizeLLMOutput("")).toBe("");
    expect(sanitizeLLMOutput(null)).toBe("");
    expect(sanitizeLLMOutput(undefined)).toBe("");
  });

  it("strips the standard LUMI greeting line", () => {
    const out = sanitizeLLMOutput(
      "Hello there! I'm LUMI, your friendly energy advisor. Let's chat about your data.\nSolar is strong here."
    );
    expect(out).not.toMatch(/Hello there/i);
    expect(out).toContain("Solar is strong here.");
  });

  it("collapses runs of blank lines", () => {
    const out = sanitizeLLMOutput("First paragraph.\n\n\n\nSecond paragraph.");
    expect(out).toBe("First paragraph.\n\nSecond paragraph.");
  });

  it("renumbers restarted bold Recommendation blocks into one list", () => {
    const out = sanitizeLLMOutput(
      "Intro text.\n**Recommendation 1:** Do A.\n**Recommendation 1:** Do B.\n**Recommendation 2:** Do C."
    );
    expect(out).toContain("Recommendations:");
    expect(out).toContain("1. Do A.");
    expect(out).toContain("2. Do B.");
    expect(out).toContain("3. Do C.");
  });

  it("leaves plain-text 'Recommendation N' mentions untouched", () => {
    const text = "Intro. Recommendation 1: Do A. More prose follows.";
    expect(sanitizeLLMOutput(text)).toBe(text);
  });
});
