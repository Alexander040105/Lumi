import { describe, it, expect } from "vitest";
import { resolveSourceAnalysis } from "./ecosimAnalysis";

describe("resolveSourceAnalysis", () => {
  it("prefers ai_analysis.renewable_analysis when present", () => {
    const result = {
      ai_analysis: { renewable_analysis: { wind: "AI text" } },
      explanations: { wind: "deterministic text" },
    };
    expect(resolveSourceAnalysis(result, "wind", "fallback")).toBe("AI text");
  });

  it("falls back to result.explanations when renewable_analysis is empty", () => {
    const result = {
      ai_analysis: { renewable_analysis: { wind: "" } },
      explanations: { wind: "deterministic text" },
    };
    expect(resolveSourceAnalysis(result, "wind", "fallback")).toBe("deterministic text");
  });

  it("falls back to result.explanations when ai_analysis is null", () => {
    const result = { ai_analysis: null, explanations: { solar: "deterministic text" } };
    expect(resolveSourceAnalysis(result, "solar", "fallback")).toBe("deterministic text");
  });

  it("uses the provided fallback when nothing else exists", () => {
    expect(resolveSourceAnalysis({}, "hydro", "fallback")).toBe("fallback");
  });

  it("returns undefined without a fallback when nothing exists", () => {
    expect(resolveSourceAnalysis({ ai_analysis: null }, "hydro")).toBeUndefined();
  });
});
