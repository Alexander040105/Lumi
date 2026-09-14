import { getPdfMake } from "./pdfFonts";
import { getRegionFromProvince, getRegionFromMunicipality } from "./regionMap";
import providersData from "@/data/providers.json";

const COLORS = {
  primary: "#0f172a",
  text: "#1e293b",
  muted: "#64748b",
  border: "#e2e8f0",
  background: "#f8fafc",
  solar: "#f59e0b",
  solarBg: "#fffbeb",
  wind: "#3b82f6",
  windBg: "#eff6ff",
  hydro: "#06b6d4",
  hydroBg: "#ecfeff",
  geothermal: "#ef4444",
  geothermalBg: "#fef2f2",
  success: "#22c55e",
};

const SOURCE_META = {
  Solar: { label: "Solar", color: COLORS.solar, bg: COLORS.solarBg },
  Wind: { label: "Wind", color: COLORS.wind, bg: COLORS.windBg },
  Hydro: { label: "Hydro", color: COLORS.hydro, bg: COLORS.hydroBg },
  Geothermal: { label: "Geothermal", color: COLORS.geothermal, bg: COLORS.geothermalBg },
};

export function formatNumber(value, digits = 0) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: digits,
  }).format(value ?? 0);
}

export function formatCurrency(value, { symbol = true } = {}) {
  const formatter = new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 2,
  });
  let out = formatter.format(value ?? 0);
  if (!symbol) {
    out = out.replace("₱", "PHP ").trim();
  }
  return out;
}

export function formatPercent(value, digits = 0) {
  return `${formatNumber(value, digits)}%`;
}

function slugify(str) {
  return String(str || "report")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function sourceDisplayName(source) {
  return source === "Hydropower" ? "Hydro" : source;
}

function getSourceMeta(source) {
  return SOURCE_META[sourceDisplayName(source)] || SOURCE_META.Solar;
}

function savingsLabel(savings) {
  if (savings <= 25) return "Reduce a little";
  if (savings <= 50) return "Reduce more";
  if (savings <= 75) return "Reduce most of your electricity cost";
  return "Reduce as much as possible";
}

function parseMarkdownInline(text) {
  if (!text) return [];
  const out = [];
  const parts = String(text).split(/(\*\*[^*\n]+?\*\*|\*[^*\n]+?\*)/g);
  for (const part of parts) {
    if (!part) continue;
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      out.push({ text: part.slice(2, -2), bold: true });
    } else if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
      out.push({ text: part.slice(1, -1), italics: true });
    } else {
      out.push({ text: part });
    }
  }
  return out;
}

function parseMarkdownToBlocks(text) {
  if (!text) return [];
  const blocks = [];
  const paragraphs = String(text).split(/\n\n+/);

  for (const para of paragraphs) {
    const lines = para.split("\n").filter(Boolean).map((l) => l.trim());
    if (lines.length === 0) continue;

    const bulletRe = /^(\*|\-|\+)\s+/;
    const numberedRe = /^\d+\.\s+/;

    if (lines.every((l) => bulletRe.test(l))) {
      const items = lines.map((l) => ({
        text: parseMarkdownInline(l.replace(bulletRe, "")),
        margin: [0, 2, 0, 2],
      }));
      blocks.push({ ul: items, margin: [0, 0, 0, 8] });
    } else if (lines.every((l) => numberedRe.test(l))) {
      const items = lines.map((l) => ({
        text: parseMarkdownInline(l.replace(numberedRe, "")),
        margin: [0, 2, 0, 2],
      }));
      blocks.push({ ol: items, margin: [0, 0, 0, 8] });
    } else {
      const joined = lines.join(" ");
      blocks.push({
        text: parseMarkdownInline(joined),
        margin: [0, 0, 0, 8],
        lineHeight: 1.35,
      });
    }
  }

  return blocks;
}

function metricBlock(label, value, explanation) {
  return {
    columns: [
      {
        width: "*",
        stack: [
          { text: label, bold: true, fontSize: 10, color: COLORS.primary },
          {
            text: explanation,
            fontSize: 8,
            color: COLORS.muted,
            margin: [0, 2, 0, 0],
            lineHeight: 1.2,
          },
        ],
      },
      {
        width: "auto",
        text: value,
        bold: true,
        fontSize: 14,
        color: COLORS.success,
        alignment: "right",
      },
    ],
    columnGap: 8,
    margin: [0, 4, 0, 4],
  };
}

function styledTable(layout) {
  return {
    layout: {
      hLineColor: () => COLORS.border,
      vLineColor: () => COLORS.border,
      hLineWidth: (i, node) =>
        i === 0 || i === node.table.body.length ? 1 : 0.5,
      vLineWidth: () => 0.5,
      paddingLeft: () => 6,
      paddingRight: () => 6,
      paddingTop: () => 4,
      paddingBottom: () => 4,
      fillColor: (rowIndex) => (rowIndex === 0 ? COLORS.background : null),
      ...layout,
    },
  };
}

function headerCell(text) {
  return { text, bold: true, color: COLORS.primary, fontSize: 9 };
}

function cellText(value, { color = COLORS.text, bold = false } = {}) {
  return { text: value, color, bold, fontSize: 9 };
}

function buildInputsTable(inputs) {
  const {
    mode,
    selectedName,
    monthlyConsumption,
    monthlyBill,
    electricityRate,
    desiredSavings,
    includeAi,
  } = inputs;

  const rows = [
    ["Location", selectedName || "—"],
    ["Location mode", mode === "municipality" ? "City/Municipality" : "Province"],
    ["Monthly consumption", `${formatNumber(monthlyConsumption)} kWh`],
    ["Monthly bill", formatCurrency(monthlyBill)],
    ["Rate per kWh", `${formatCurrency(electricityRate)} / kWh`],
    ["Savings goal", `${desiredSavings}% — ${savingsLabel(desiredSavings)}`],
    ["Include AI analysis", includeAi ? "Yes" : "No"],
  ];

  return {
    table: {
      widths: ["35%", "*"],
      body: rows.map(([label, value]) => [
        cellText(label, { bold: true, color: COLORS.muted }),
        cellText(value, { bold: true }),
      ]),
    },
    ...styledTable({}),
  };
}

function buildComparisonTable(result) {
  const allSources = ["Solar", "Wind", "Hydro"];
  if (result.renewable_energy_results?.geothermal_output) {
    allSources.push("Geothermal");
  }

  const body = [
    [
      headerCell("Source"),
      headerCell("Projected output"),
      headerCell("Suitability / score"),
      headerCell("Key factor / AI note"),
      headerCell("Note"),
    ],
  ];

  for (const source of allSources) {
    const key = source.toLowerCase();
    const detail = result.renewable_energy_results?.[`${key}_output`];
    const optionSource = source === "Hydro" ? "Hydropower" : source;
    const option =
      result.options?.find((o) => o.source === optionSource) || {};
    const isGeothermal = source === "Geothermal";
    const outputKwh = isGeothermal
      ? detail?.annual_energy_gwh
        ? (detail.annual_energy_gwh * 1_000_000) / 12
        : detail?.monthly_energy_kwh || 0
      : option.monthly_output ||
        detail?.monthly_solar_output ||
        detail?.monthly_energy_kwh ||
        detail?.monthly_hydro_output ||
        0;
    const score = isGeothermal
      ? detail?.suitability_score || 0
      : option.generation_score ?? detail?.solar_score ?? detail?.wind_score ?? detail?.hydro_score ?? 0;
    const note = isGeothermal ? "Utility-scale reference" : "";
    const analysis =
      result.ai_analysis?.renewable_analysis?.[key] ||
      detail?.assumption ||
      "";

    const meta = getSourceMeta(source);
    body.push([
      cellText(getSourceMeta(source).label, {
        bold: true,
        color: meta.color,
      }),
      cellText(`${formatNumber(outputKwh, 0)} kWh/month`),
      cellText(`${formatNumber(score, 0)} / 100`),
      analysis
        ? { text: parseMarkdownInline(analysis), fontSize: 8 }
        : cellText("—"),
      cellText(note, { color: COLORS.muted }),
    ]);
  }

  return {
    table: {
      headerRows: 1,
      widths: ["auto", "auto", "auto", "*", "auto"],
      body,
    },
    ...styledTable({ fillColor: (rowIndex) => (rowIndex === 0 ? COLORS.background : null) }),
  };
}

function buildClimateTable(climate) {
  if (!climate || Object.keys(climate).length === 0) return null;

  const items = [
    ["Avg temperature", `${formatNumber(climate.avg_t2m, 1)} °C`],
    ["Humidity", `${formatNumber(climate.avg_rh2m, 1)}%`],
    ["Rainfall", `${formatNumber(climate.avg_prectotcorr, 1)} mm/day`],
    [
      "Solar irradiance",
      `${formatNumber(climate.avg_allsky_sfc_sw_dwn, 2)} kWh/m²/day`,
    ],
    ["Wind speed", `${formatNumber(climate.avg_ws10m, 2)} m/s`],
    ["Cloud coverage", `${formatNumber(climate.avg_cloud_amt, 1)}%`],
    ["Surface pressure", `${formatNumber(climate.avg_surface_pressure, 1)} kPa`],
    ["Elevation", `${formatNumber(climate.elevation, 0)} m`],
  ].filter(([_, v]) => !v.includes("NaN"));

  return {
    table: {
      widths: ["45%", "*"],
      body: items.map(([label, value]) => [
        cellText(label, { bold: true, color: COLORS.muted }),
        cellText(value),
      ]),
    },
    ...styledTable({}),
  };
}

function buildProviderTable(result) {
  const provinceName =
    result.province ||
    (result.municipality ? result.municipality.split(",")[1]?.trim() : null);
  const municipalityName = result.municipality;

  let region = getRegionFromProvince(provinceName);
  if (!region && municipalityName) {
    region = getRegionFromMunicipality(municipalityName);
  }

  const matched = region
    ? providersData.filter((p) => p.region === region)
    : [];

  if (matched.length === 0) {
    return {
      text: `No DOE-registered solar installers were found for this region (${region || "unknown"}). Try checking the provider registry directly.`,
      color: COLORS.muted,
      italics: true,
      margin: [0, 0, 0, 8],
    };
  }

  const body = [
    [
      headerCell("Provider"),
      headerCell("Location"),
      headerCell("Details"),
      headerCell("Website"),
    ],
  ];

  for (const p of matched) {
    const details = [p.type, p.years].filter(Boolean).join(" • ");
    body.push([
      cellText(p.name, { bold: true }),
      cellText(p.address || "—"),
      cellText(details || "—"),
      p.url
        ? { text: p.url, link: p.url, color: COLORS.wind, fontSize: 8, decoration: "underline" }
        : cellText("—"),
    ]);
  }

  return {
    table: {
      headerRows: 1,
      widths: ["auto", "*", "auto", "auto"],
      body,
    },
    ...styledTable({}),
  };
}

export function buildEcosimPdf({ result, inputs }) {
  const location =
    inputs?.selectedName ||
    result?.municipality ||
    result?.province ||
    "—";
  const generatedAt = new Date().toLocaleDateString("en-PH", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const rawRecommended = result?.recommended_source || "";
  const isGeothermalRec = rawRecommended === "Geothermal";
  const homeSources = ["Solar", "Wind", "Hydro"];
  const fallbackRec = isGeothermalRec
    ? (result?.options || [])
        .filter((o) => homeSources.includes(sourceDisplayName(o.source)))
        .sort((a, b) => (b.monthly_output || 0) - (a.monthly_output || 0))[0] ||
      (result?.options || [])[0] ||
      {}
    : null;
  const rec =
    fallbackRec ||
    result?.options?.find((o) => o.source === rawRecommended) ||
    {};
  const recSource = rec.source || rawRecommended;
  const recDisplay = sourceDisplayName(recSource);
  const meta = getSourceMeta(recDisplay);

  const cons = result?.monthly_consumption_kwh || 0;
  const bill = result?.monthly_bill || 0;
  const effectiveRate = cons > 0 ? bill / cons : 0;
  const coverage =
    cons > 0 && rec?.estimated_generation_kwh
      ? (rec.estimated_generation_kwh / cons) * 100
      : 0;

  const climate =
    result?.climate || result?.renewable_energy_results?.climate || {};

  const content = [];

  // Title block
  content.push({
    stack: [
      {
        text: "LUMI",
        bold: true,
        fontSize: 22,
        color: COLORS.primary,
      },
      {
        text: "EcoSim Feasibility Report",
        fontSize: 18,
        bold: true,
        color: COLORS.primary,
        margin: [0, 4, 0, 4],
      },
      {
        text: `Location: ${location}`,
        fontSize: 12,
        color: COLORS.muted,
      },
      {
        text: `Generated: ${generatedAt}`,
        fontSize: 10,
        color: COLORS.muted,
        margin: [0, 0, 0, 8],
      },
    ],
    margin: [0, 0, 0, 12],
  });

  // Inputs
  content.push({ text: "Simulation Inputs", style: "sectionHeading" });
  content.push(buildInputsTable(inputs));

  // Recommendation
  content.push({ text: "Recommendation", style: "sectionHeading" });
  content.push({
    table: {
      widths: ["*"],
      body: [
        [
          {
            stack: [
              { text: "Best match", bold: true, color: meta.color, fontSize: 10 },
              {
                text: meta.label,
                bold: true,
                fontSize: 28,
                color: meta.color,
                margin: [0, 4, 0, 4],
              },
              {
                text: `${formatNumber(rec?.estimated_generation_kwh, 0)} kWh/month`,
                bold: true,
                fontSize: 14,
                color: COLORS.text,
              },
              {
                text: isGeothermalRec
                  ? `Geothermal is shown as a reference only because it is typically utility-scale, not a home option. The recommendation is based on available data for ${meta.label}.`
                  : result?.explanation || "",
                fontSize: 9,
                color: COLORS.muted,
                margin: [0, 8, 0, 0],
                lineHeight: 1.3,
              },
            ],
            margin: 12,
          },
        ],
      ],
    },
    layout: {
      hLineColor: () => COLORS.border,
      vLineColor: () => COLORS.border,
      hLineWidth: () => 1,
      vLineWidth: () => 1,
      fillColor: () => meta.bg,
    },
    margin: [0, 0, 0, 12],
  });

  // Supporting metrics
  content.push({ text: "Supporting Metrics", style: "sectionHeading" });
  content.push(
    metricBlock(
      "Energy coverage",
      formatPercent(coverage, 0),
      "The % of your monthly electricity usage this system is expected to offset."
    )
  );
  content.push(
    metricBlock(
      "Monthly output",
      `${formatNumber(rec?.estimated_generation_kwh, 0)} kWh`,
      "Estimated electricity this system could generate each month."
    )
  );
  content.push(
    metricBlock(
      "Carbon reduction",
      `${formatNumber(result?.carbon_reduction, 0)} kg`,
      "Estimated CO₂ emissions avoided per month."
    )
  );

  if (result?.monthly_savings != null || rec?.monthly_savings != null) {
    const savings = result?.monthly_savings ?? rec?.monthly_savings ?? 0;
    content.push(
      metricBlock(
        "Estimated monthly savings",
        formatCurrency(savings),
        "Approximate value of the energy this system could generate each month."
      )
    );
  }

  if (result?.installation_cost != null || rec?.installation_cost != null) {
    const cost = result?.installation_cost ?? rec?.installation_cost ?? 0;
    content.push(
      metricBlock(
        "Estimated installation cost",
        formatCurrency(cost),
        "Indicative cost for a suitable system based on the estimate."
      )
    );
  }

  if (result?.payback_years != null || rec?.payback_years != null) {
    const years = result?.payback_years ?? rec?.payback_years ?? 0;
    content.push(
      metricBlock(
        "Payback period",
        `${formatNumber(years, 1)} years`,
        "Rough number of years before the system pays for itself through savings."
      )
    );
  }

  content.push(
    metricBlock(
      "Your effective rate",
      `${formatCurrency(effectiveRate)} / kWh`,
      "Your average cost per kWh based on bill and consumption."
    )
  );

  if (result?.meralco_rate?.rate_php_per_kwh) {
    content.push(
      metricBlock(
        "Meralco rate",
        `${formatCurrency(result.meralco_rate.rate_php_per_kwh)} / kWh`,
        `Published Meralco generation charge${result.meralco_rate.year ? ` for ${result.meralco_rate.year}` : ""}.`
      )
    );
    content.push(
      metricBlock(
        "Customer class",
        result.meralco_rate.customer_class || "—",
        "Meralco customer classification used for the rate."
      )
    );
  }

  // Why this source
  content.push({ text: "Why This Source", style: "sectionHeading" });
  content.push(
    ...parseMarkdownToBlocks(
      result?.explanation || "No explanation available for this recommendation."
    )
  );

  if (climate?.avg_allsky_sfc_sw_dwn != null && recDisplay === "Solar") {
    content.push({
      text: `Local solar irradiance is about ${formatNumber(
        climate.avg_allsky_sfc_sw_dwn,
        2
      )} kWh/m²/day — a key reason solar is favored here.`,
      fontSize: 9,
      color: COLORS.muted,
      margin: [0, 0, 0, 8],
    });
  } else if (climate?.avg_ws10m != null && recDisplay === "Wind") {
    content.push({
      text: `Average wind speed is about ${formatNumber(
        climate.avg_ws10m,
        2
      )} m/s — a key factor for wind potential.`,
      fontSize: 9,
      color: COLORS.muted,
      margin: [0, 0, 0, 8],
    });
  }

  // AI analysis
  if (result?.ai_analysis?.summary) {
    content.push({ text: "AI Analysis", style: "sectionHeading" });
    content.push(
      ...parseMarkdownToBlocks(result.ai_analysis.summary)
    );

    const sources = ["solar", "wind", "hydro", "geothermal"];
    for (const key of sources) {
      const analysis = result.ai_analysis.renewable_analysis?.[key];
      if (!analysis) continue;
      const display =
        key === "solar"
          ? "Solar"
          : key === "wind"
          ? "Wind"
          : key === "hydro"
          ? "Hydro"
          : "Geothermal";
      content.push({
        text: display,
        style: "subSection",
        color: getSourceMeta(display).color,
      });
      content.push(...parseMarkdownToBlocks(analysis));
    }
  } else if (inputs?.includeAi) {
    content.push({ text: "AI Analysis", style: "sectionHeading" });
    content.push({
      text: "AI analysis is still being generated. Run the simulation again or wait a moment, then export.",
      color: COLORS.muted,
      italics: true,
    });
  }

  // Comparison table
  content.push({ text: "Source Comparison", style: "sectionHeading" });
  content.push(buildComparisonTable(result));

  // Climate table
  if (Object.keys(climate).length > 0) {
    content.push({ text: "Technical / Climate Details", style: "sectionHeading" });
    const climateTable = buildClimateTable(climate);
    if (climateTable) content.push(climateTable);
  }

  // Providers
  content.push({ text: "Recommended Providers", style: "sectionHeading" });
  content.push(
    {
      text: "DOE-registered solar installers in your region. LUMI does not endorse any provider; contact them directly for quotes and site surveys.",
      fontSize: 9,
      color: COLORS.muted,
      margin: [0, 0, 0, 8],
    },
    buildProviderTable(result)
  );

  return {
    pageSize: "A4",
    pageMargins: [40, 80, 40, 80],
    defaultStyle: {
      font: "Roboto",
      fontSize: 10,
      color: COLORS.text,
    },
    styles: {
      sectionHeading: {
        fontSize: 14,
        bold: true,
        color: COLORS.primary,
        margin: [0, 16, 0, 8],
      },
      subSection: {
        fontSize: 12,
        bold: true,
        margin: [0, 10, 0, 4],
      },
    },
    header: (currentPage) => ({
      columns: [
        {
          text: "LUMI",
          bold: true,
          color: COLORS.primary,
          fontSize: 12,
          margin: [40, 20, 0, 0],
        },
        {
          text: `EcoSim — ${location}`,
          color: COLORS.muted,
          fontSize: 9,
          alignment: "right",
          margin: [0, 20, 40, 0],
        },
      ],
    }),
    footer: (currentPage, pageCount) => ({
      stack: [
        {
          canvas: [
            {
              type: "line",
              x1: 40,
              y1: 0,
              x2: 555,
              y2: 0,
              lineWidth: 0.5,
              lineColor: COLORS.border,
            },
          ],
          margin: [40, 10, 40, 0],
        },
        {
          columns: [
            {
              text:
                "Figures are model estimates based on your inputs and available climate/rate data, not guarantees.",
              color: COLORS.muted,
              fontSize: 8,
              margin: [40, 8, 0, 0],
            },
            {
              text: `${currentPage} / ${pageCount}`,
              alignment: "right",
              color: COLORS.muted,
              fontSize: 8,
              margin: [0, 8, 40, 0],
            },
          ],
        },
      ],
    }),
    content,
  };
}

export async function downloadEcosimPdf({ result, inputs }) {
  const pdfMake = await getPdfMake();
  const docDefinition = buildEcosimPdf({ result, inputs });
  const location = slugify(
    inputs?.selectedName || result?.municipality || result?.province || "report"
  );
  const date = new Date().toISOString().slice(0, 10);
  const fileName = `Lumi-EcoSim-${location}-${date}.pdf`;
  pdfMake.createPdf(docDefinition).download(fileName);
}
