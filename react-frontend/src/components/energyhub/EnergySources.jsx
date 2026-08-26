import { useMemo } from "react";
import { useI18n } from "@/i18n";
import { useTheme } from "@/hooks/useTheme";
import PlotlyChart from "./PlotlyChart";
import ChartExplanation from "./ChartExplanation";

function hslValue(name) {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value ? `hsl(${value})` : "";
}

const SOURCE_META = {
  coal: { label: "Coal", color: "#64748b" },
  natural_gas: { label: "Natural Gas", color: "#3b82f6" },
  oil_based: { label: "Oil-Based", color: "#f59e0b" },
  geothermal: { label: "Geothermal", color: "#ef4444" },
  hydro: { label: "Hydro", color: "#06b6d4" },
  solar: { label: "Solar", color: "#eab308" },
  wind: { label: "Wind", color: "#22c55e" },
  biomass: { label: "Biomass", color: "#8b5cf6" },
};

export default function EnergySources({ breakdown }) {
  const { t } = useI18n();
  const { theme } = useTheme();
  const chartData = useMemo(() => {
    if (!breakdown || !breakdown.share_pct) return [];
    const entries = Object.entries(breakdown.share_pct)
      .filter(([, v]) => v > 0)
      .sort(([, a], [, b]) => b - a);

    return entries.map(([key, value]) => ({
      key,
      label: t(`energyHub.sources.labels.${key}`) || key,
      color: SOURCE_META[key]?.color || "#cbd5e1",
      share: value,
      gwh: breakdown.generation_gwh?.[key] || 0,
    }));
  }, [breakdown, t]);

  const plotlyData = useMemo(() => {
    if (chartData.length === 0) return [];
    return [
      {
        values: chartData.map((d) => d.share),
        labels: chartData.map((d) => d.label),
        type: "pie",
        hole: 0.55,
        marker: { colors: chartData.map((d) => d.color) },
        textinfo: "percent",
        textposition: "inside",
        insidetextorientation: "radial",
        textfont: { size: 11, color: "#ffffff" },
        hovertemplate: t("energyHub.sources.hover", { value: "%{value}", gwh: "%{customdata:,.0f}" }),
        customdata: chartData.map((d) => d.gwh),
        showlegend: false,
        sort: false,
      },
    ];
  }, [chartData]);

  const plotlyLayout = useMemo(
    () => ({
      showlegend: false,
      margin: { t: 12, r: 12, b: 12, l: 12 },
      annotations: [
        {
          text: `<b>${breakdown?.year || ""}</b><br><span style="font-size:11px;color:${hslValue("--muted-foreground")}">GWh</span>`,
          showarrow: false,
          font: { size: 20, color: hslValue("--foreground"), family: "Inter, sans-serif" },
        },
      ],
    }),
    [breakdown, theme]
  );

  if (!breakdown || chartData.length === 0) {
    return (
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold">{t("energyHub.sources.title")}</h3>
        <div className="mt-4 h-48 bg-muted rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <h3 className="text-lg font-semibold">
        {t("energyHub.sources.title")} ({breakdown.year})
      </h3>
      <p className="text-sm text-muted-foreground">
        {t("energyHub.sources.totalGeneration", { value: breakdown.total_generation_gwh.toLocaleString() })}
      </p>
      <ChartExplanation
        what={t("energyHub.sources.explanation.what")}
        why={t("energyHub.sources.explanation.why")}
        action={t("energyHub.sources.explanation.action")}
      />

      <div className="mt-4 flex flex-col md:flex-row items-center gap-6">
        <div className="w-80 h-80 shrink-0">
          <PlotlyChart data={plotlyData} layout={plotlyLayout} />
        </div>

        <div className="flex-1 w-full">
          <div className="space-y-2.5">
            {chartData.map((d) => (
              <div key={d.key} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block h-3 w-3 rounded-sm"
                    style={{ backgroundColor: d.color }}
                  />
                  <span className="text-sm font-medium">{d.label}</span>
                </div>
                <div className="text-right min-w-[70px]">
                  <span className="text-sm font-semibold">{d.share}%</span>
                  <span className="ml-4 text-xs text-muted-foreground">
                    {d.gwh.toLocaleString()} GWh
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
