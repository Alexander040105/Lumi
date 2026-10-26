// LUMI brand tokens — sourced from DESIGN.md. Keep in sync when DESIGN.md changes.
export const brand = {
  colors: {
    lumiGreen: "#2e5f2b", // primary / hydro chart
    ringGreen: "#3b6e38",
    forestDeep: "#133913", // brand-dark
    forestInk: "#0f260d", // foreground
    solarGold: "#f6d96a", // emphasis accent — use sparingly (Gold Reserve Rule)
    solarGlow: "#ffe175", // chart-solar
    windGreen: "#64be60", // chart-wind / success
    geothermalEmber: "#cb6b0b", // chart-geothermal
    harvestAmber: "#aa4411", // warning
    signalRed: "#dc2626", // destructive only
    paleMeadow: "#f4fbf4", // page background
    cardWhite: "#ffffff",
    mist: "#ebf6eb",
    meadowMist: "#dff6df",
    leafBorder: "#c6e0c6",
  },
  font: "ui-sans-serif, system-ui, sans-serif",
  radius: { sm: "0.5rem", md: "0.625rem", lg: "0.75rem", full: "9999px" },
} as const;

// Named rules worth honoring in video scenes:
// - One Family Rule: only greens (+ Solar Gold accents); no blue/purple chrome.
// - Gold Reserve: gold = solar/emphasis moments, max once or twice per scene.
// - No pure gray/black neutrals — all neutrals are green-tinted.
// - Honest voice: "estimated", "may work in your area" — never promise outcomes.
