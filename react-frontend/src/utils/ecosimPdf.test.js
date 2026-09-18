import { describe, it, expect } from "vitest";
import { buildEcosimPdf, formatNumber, formatCurrency } from "./ecosimPdf";

const sampleInputs = {
  mode: "municipality",
  selectedName: "Quezon City, NCR",
  monthlyConsumption: 350,
  monthlyBill: 5000,
  electricityRate: 14.29,
  desiredSavings: 50,
  includeAi: true,
};

const sampleResult = {
  municipality: "Quezon City",
  province: "NCR",
  recommended_source: "Solar",
  explanation:
    "High solar irradiance and consistent sunlight make solar the best home-scale option for this location.",
  municipality_id: 12345,
  monthly_consumption_kwh: 350,
  monthly_bill: 5000,
  effective_consumption_kwh: 350,
  carbon_reduction: 85,
  meralco_rate: {
    rate_php_per_kwh: 13.66,
    year: 2024,
    customer_class: "Residential",
    note: "Average generation charge",
  },
  options: [
    {
      source: "Solar",
      suitability_score: 95,
      estimated_generation_kwh: 150,
      monthly_output: 150,
      generation_score: 85,
      monthly_savings: 1200,
      installation_cost: 120000,
      payback_years: 8.3,
      carbon_reduction: 85,
      explanation: "High solar potential.",
    },
    {
      source: "Wind",
      suitability_score: 40,
      estimated_generation_kwh: 80,
      monthly_output: 80,
      generation_score: 40,
      monthly_savings: 600,
      installation_cost: 90000,
      payback_years: 12.5,
      carbon_reduction: 45,
      explanation: "Low average wind speeds.",
    },
    {
      source: "Hydropower",
      suitability_score: 20,
      estimated_generation_kwh: 40,
      monthly_output: 40,
      generation_score: 20,
      monthly_savings: 300,
      installation_cost: 70000,
      payback_years: 19.4,
      carbon_reduction: 22,
      explanation: "No reliable stream nearby.",
    },
  ],
  renewable_energy_results: {
    solar_output: {
      daily_solar_output: 5,
      monthly_solar_output: 150,
      annual_solar_output: 1800,
      solar_score: 95,
      generation_score: 85,
    },
    wind_output: {
      daily_energy_kwh: 2.6,
      monthly_energy_kwh: 80,
      annual_wind_output_kwh: 960,
      wind_score: 40,
      generation_score: 40,
    },
    hydro_output: {
      daily_hydro_output: 1.3,
      monthly_hydro_output: 40,
      annual_hydro_output: 480,
      hydro_score: 20,
      generation_score: 20,
    },
    geothermal_output: {
      suitability_score: 30,
      annual_energy_gwh: 0.01,
      monthly_energy_kwh: 833,
      classification: "utility",
      source: "reference",
    },
    climate: {
      avg_t2m: 27,
      avg_rh2m: 75,
      avg_prectotcorr: 8,
      avg_ws10m: 2.5,
      avg_allsky_sfc_sw_dwn: 5.2,
      avg_cloud_amt: 50,
      avg_surface_pressure: 101,
      elevation: 50,
    },
  },
  climate: {
    avg_t2m: 27,
    avg_rh2m: 75,
    avg_prectotcorr: 8,
    avg_ws10m: 2.5,
    avg_allsky_sfc_sw_dwn: 5.2,
    avg_cloud_amt: 50,
    avg_surface_pressure: 101,
    elevation: 50,
  },
  ai_analysis: {
    summary:
      "Solar is strongly recommended because of high irradiance and reliable sunlight. **Wind** and *hydro* are less suitable.",
    renewable_analysis: {
      solar: "Excellent irradiance and limited shading.",
      wind: "Low average wind speeds limit wind potential.",
      hydro: "No reliable stream nearby.",
      geothermal: "Geothermal exists at utility scale only.",
    },
  },
};

function flatText(node, out = []) {
  if (node == null) return out;
  if (typeof node === "string") {
    out.push(node);
    return out;
  }
  if (Array.isArray(node)) {
    for (const child of node) flatText(child, out);
    return out;
  }
  if (node.text != null) {
    if (typeof node.text === "string") {
      out.push(node.text);
    } else if (Array.isArray(node.text)) {
      for (const child of node.text) flatText(child, out);
    }
  }
  for (const key of ["stack", "columns", "ul", "ol", "table", "content"]) {
    if (node[key] != null) flatText(node[key], out);
  }
  if (Array.isArray(node.body)) flatText(node.body, out);
  return out;
}

describe("ecosimPdf", () => {
  it("formats numbers and currency", () => {
    expect(formatNumber(1234.5, 1)).toBe("1,234.5");
    expect(formatNumber(0)).toBe("0");
    expect(formatCurrency(1234.5).startsWith("₱")).toBe(true);
  });

  it("builds a docDefinition with all required sections", () => {
    const doc = buildEcosimPdf({ result: sampleResult, inputs: sampleInputs });
    expect(doc).toBeDefined();
    expect(doc.pageSize).toBe("A4");
    expect(doc.content).toBeDefined();

    const allText = flatText(doc).join(" ");
    expect(allText).toContain("Simulation Inputs");
    expect(allText).toContain("Recommendation");
    expect(allText).toContain("Supporting Metrics");
    expect(allText).toContain("Why This Source");
    expect(allText).toContain("AI Analysis");
    expect(allText).toContain("Source Comparison");
    expect(allText).toContain("Technical / Climate Details");
    expect(allText).toContain("Recommended Providers");
    expect(allText).toContain("LUMI EcoSim Feasibility Report");
    expect(allText).toContain("Quezon City");
  });

  it("renders bold/italic markdown inside AI text", () => {
    const doc = buildEcosimPdf({ result: sampleResult, inputs: sampleInputs });
    const allText = flatText(doc);
    expect(allText.join(" ")).toContain("Wind");
    expect(allText.join(" ")).toContain("hydro");
  });

  it("matches DOE-registered providers for the region", () => {
    const doc = buildEcosimPdf({ result: sampleResult, inputs: sampleInputs });
    const allText = flatText(doc).join(" ");
    // NCR providers include Solaric, PHILERGY, etc.
    expect(allText).toMatch(/Solaric|PHILERGY|MSpectrum/);
  });

  it("cleanses real AI markdown for PDF output", () => {
    const result = {
      ...sampleResult,
      ai_analysis: {
        summary:
          "## Observation\n" +
          "Dasmariñas City is warm year‑round with an average temperature of about 27.7 °C and high humidity around 80 %. " +
          "Average wind speed is 5.3 m s⁻¹ and rainfall averages 7.5 mm (moderate).\n\n" +
          "## Interpretation\n" +
          "- **Solar** – With 5 kWh/m²/day of sunshine, output is roughly 146 kWh (≈350 kWh use).\n" +
          "- **Wind** – The average wind speed of 5.3 m s⁻¹ gives about 190 kWh per month.\n\n" +
          "## Recommendation\n" +
          "The backend recommendation of **Wind** is confirmed.",
        renewable_analysis: {
          solar: "Irradiance of 5 kWh/m²/day is strong.",
        },
      },
    };
    const doc = buildEcosimPdf({ result, inputs: sampleInputs });
    const allText = flatText(doc).join(" ");

    // Headings render as text, never as literal "##"
    expect(allText).toContain("Observation");
    expect(allText).toContain("Interpretation");
    expect(allText).not.toContain("##");

    // Roboto-unrenderable characters are normalized away
    expect(allText).not.toMatch(/[\u202f\u00a0⁻¹⁰]/);
    expect(allText).not.toContain("‑");

    // Units survive: slash notation and superscript-two are preserved
    expect(allText).toContain("kWh/m²/day");
    expect(allText).toContain("5.3 m/s");
    expect(allText).toContain("27.7 °C");
    expect(allText).toContain("year-round");

    // ≈ renders in Roboto and is preserved as-is
    expect(allText).toContain("≈350");
  });

  it("turns heading-plus-bullet sections into real list blocks", () => {
    const result = {
      ...sampleResult,
      ai_analysis: {
        summary:
          "## Interpretation\n" +
          "- **Solar** – first point\n" +
          "- **Wind** – second point\n\n" +
          "Trailing paragraph.",
      },
    };
    const doc = buildEcosimPdf({ result, inputs: sampleInputs });

    const ulBlocks = [];
    (function walk(node) {
      if (Array.isArray(node)) return node.forEach(walk);
      if (node && typeof node === "object") {
        if (node.ul) ulBlocks.push(node.ul);
        for (const key of ["stack", "columns", "content", "table"])
          if (node[key]) walk(node[key]);
      }
    })(doc.content);

    const aiList = ulBlocks.find((items) =>
      items.some((i) => flatText(i).join("").includes("first point"))
    );
    expect(aiList).toBeDefined();
    expect(aiList).toHaveLength(2);

    // Bold segment inside the bullet is preserved
    const itemText = aiList[0].text;
    const boldSeg = itemText.find((s) => s.bold);
    expect(boldSeg?.text).toBe("Solar");
  });

  it("handles malformed markdown without crashing", () => {
    const result = {
      ...sampleResult,
      ai_analysis: {
        summary:
          "Unclosed **bold and `code here\n\n* lone star\n\n> quoted note\n\n---\n\n[Link](https://example.com) end.",
        renewable_analysis: { wind: null },
      },
    };
    const doc = buildEcosimPdf({ result, inputs: sampleInputs });
    const allText = flatText(doc).join(" ");
    expect(allText).toContain("Unclosed");
    expect(allText).toContain("quoted note");
    expect(allText).toContain("Link");
  });
});
