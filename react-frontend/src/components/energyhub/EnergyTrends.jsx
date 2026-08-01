import { useMemo } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { useI18n } from "@/i18n";
import PlotlyChart from "./PlotlyChart";
import ChartExplanation from "./ChartExplanation";

function sanitizeLLMOutput(text = "") {
  if (!text) return "";
  let t = text;

  // Remove repetitive greeting lines that appear in every panel
  t = t.replace(/Hello there! I'm LUMI, your friendly energy advisor\.\s*Let's chat about.*?\n*/is, "");
  t = t.replace(/Hi there! I'm LUMI.*?\n*/is, "");

  // Normalize repeated "Recommendation 1:" blocks into a single numbered list
  // When the LLM restarts numbering mid-text, renumber them sequentially
  const recBlocks = [];
  const recRegex = /\*?\s*\*\*?\s*Recommendation\s*(\d+)[:\.*\-]*\s*\*?\*?\s*(.*?)(?=\*?\s*\*\*?\s*Recommendation\s*\d+[:\.*\-]*|$)/gis;
  let m;
  while ((m = recRegex.exec(t)) !== null) {
    recBlocks.push(m[2].trim());
  }
  if (recBlocks.length > 0) {
    const numbered = recBlocks.map((b, i) => `${i + 1}. ${b.replace(/\n+/g, " ")}`).join("\n");
    t = t.replace(/\*?\s*\*\*?\s*Recommendation\s*\d+[:\.*\-]*\s*\*?\*?\s*.*/gis, "").trim();
    t = t + "\n\nRecommendations:\n" + numbered;
  }

  // Collapse multiple blank lines into one
  t = t.replace(/\n{3,}/g, "\n\n");

  // Trim to a reasonable length for panel display (soft cap ~800 chars)
  if (t.length > 900) {
    t = t.slice(0, 900).replace(/\s+\S*$/, "") + "…";
  }

  return t.trim();
}

function ChartAiPanel({ chartKey, analysis, onAnalyze, onRefresh, loading }) {
  const { t } = useI18n();
  if (!analysis && !loading) {
    return (
      <button
        onClick={onAnalyze}
        className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 border border-amber-200 hover:bg-amber-100 transition-colors"
      >
        <Sparkles className="h-3 w-3" />
        {t("energyHub.trends.aiExplain")}
      </button>
    );
  }

  if (loading) {
    return (
      <div className="mt-2 inline-flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700 border border-amber-200">
        <Loader2 className="h-3 w-3 animate-spin" />
        {t("energyHub.trends.generating")}
      </div>
    );
  }

  return (
    <div className="mt-2 rounded-lg bg-amber-50 border border-amber-100 p-3">
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs leading-relaxed text-amber-900 whitespace-pre-line flex-1">{sanitizeLLMOutput(analysis?.insight)}</p>
        {onRefresh && (
          <button
            onClick={onRefresh}
            title={t("energyHub.trends.getDifferent")}
            className="shrink-0 inline-flex items-center gap-1 rounded-md bg-amber-100 px-2 py-1 text-[10px] font-medium text-amber-700 border border-amber-200 hover:bg-amber-200 transition-colors"
          >
            <Sparkles className="h-3 w-3" />
            {t("energyHub.trends.refresh")}
          </button>
        )}
      </div>
    </div>
  );
}

export default function EnergyTrends({ trends, chartAnalyses, llmLoading, onAnalyzeChart }) {
  const { t } = useI18n();
  const years = trends?.years || [];
  const series = trends?.series || {};
  const forecast = trends?.forecast || {};

  const consumptionSeries = useMemo(() => {
    const hist = series.total_consumption_gwh || [];
    const fYears = forecast.forecast_years || [];
    const fValues = forecast.forecast_values || [];
    return {
      years: [...years, ...fYears],
      values: [...hist, ...fValues],
      isForecast: [...Array(hist.length).fill(false), ...Array(fValues.length).fill(true)],
    };
  }, [years, series, forecast]);

  const consumptionTraces = useMemo(() => {
    const allYears = consumptionSeries.years;
    const allValues = consumptionSeries.values;
    const isF = consumptionSeries.isForecast;

    const histX = [];
    const histY = [];
    const forecastX = [];
    const forecastY = [];

    for (let i = 0; i < allYears.length; i++) {
      if (isF[i]) {
        forecastX.push(allYears[i]);
        forecastY.push(allValues[i]);
      } else {
        histX.push(allYears[i]);
        histY.push(allValues[i]);
      }
    }

    // Junction point for continuity
    if (histX.length > 0 && forecastX.length > 0) {
      forecastX.unshift(histX[histX.length - 1]);
      forecastY.unshift(histY[histY.length - 1]);
    }

    return [
      {
        x: histX,
        y: histY,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.legend.historical"),
        line: { color: "#3b82f6", width: 3 },
        marker: { size: 6 },
        hovertemplate: t("energyHub.trends.hover.consumption", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.historical") }),
      },
      {
        x: forecastX,
        y: forecastY,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.legend.forecast"),
        line: { color: "#f87171", width: 3, dash: "dash" },
        marker: { size: 6 },
        hovertemplate: t("energyHub.trends.hover.consumption", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.forecast") }),
      },
    ];
  }, [consumptionSeries, t]);

  const consumptionLayout = useMemo(
    () => ({
      title: { text: "", font: { size: 14 } },
      xaxis: { title: t("energyHub.trends.chartAxis.year"), tickmode: "linear", dtick: 1 },
      yaxis: { title: t("energyHub.trends.chartAxis.gwh") },
      legend: { orientation: "v", x: 1, xanchor: "right", y: 1, yanchor: "top", font: { size: 11 } },
      margin: { t: 16, r: 100, b: 40, l: 56 },
    }),
    [t]
  );

  const peakDemandTrace = useMemo(() => {
    const vals = series.total_peak_demand_mw || [];
    return [
      {
        x: years,
        y: vals,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.peakDemand.title"),
        line: { color: "#f43f5e", width: 2 },
        marker: { size: 5 },
        hovertemplate: t("energyHub.trends.hover.peakDemand", { year: "%{x}", value: "%{y:,.0f}" }),
      },
    ];
  }, [years, series, t]);

  const peakDemandLayout = useMemo(
    () => ({
      xaxis: { title: t("energyHub.trends.chartAxis.year"), tickmode: "linear", dtick: 1 },
      yaxis: { title: t("energyHub.trends.chartAxis.mw") },
      legend: { orientation: "v", x: 1, xanchor: "right", y: 1, yanchor: "top", font: { size: 11 } },
      margin: { t: 16, r: 100, b: 40, l: 56 },
    }),
    [t]
  );

  const renewableGenTrace = useMemo(() => {
    const vals = series.renewable_generation_gwh || [];
    return [
      {
        x: years,
        y: vals,
        type: "bar",
        name: t("energyHub.trends.renewable.title"),
        marker: { color: "#10b981" },
        hovertemplate: t("energyHub.trends.hover.renewable", { year: "%{x}", value: "%{y:,.0f}" }),
      },
    ];
  }, [years, series, t]);

  const renewableGenLayout = useMemo(
    () => ({
      xaxis: { title: t("energyHub.trends.chartAxis.year"), tickmode: "linear", dtick: 1 },
      yaxis: { title: t("energyHub.trends.chartAxis.gwh") },
      legend: { orientation: "v", x: 1, xanchor: "right", y: 1, yanchor: "top", font: { size: 11 } },
      margin: { t: 16, r: 120, b: 40, l: 56 },
    }),
    [t]
  );

  if (!years.length) {
    return (
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold">{t("energyHub.trends.title")}</h3>
        <div className="mt-4 h-48 bg-muted rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{t("energyHub.trends.title")}</h3>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-blue-500" />
            {t("energyHub.trends.legend.historical")}
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-red-400" />
            {t("energyHub.trends.legend.forecast")}
          </span>
        </div>
      </div>

      {/* Consumption trend */}
      <div className="mt-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-foreground">{t("energyHub.trends.consumption.title")}</p>
            <p className="text-xs text-muted-foreground">{t("energyHub.trends.consumption.subtitle")}</p>
          </div>
        </div>
        <ChartExplanation
          what={t("energyHub.trends.consumption.explanation.what")}
          why={t("energyHub.trends.consumption.explanation.why")}
          action={t("energyHub.trends.consumption.explanation.action")}
        />
        <div className="relative rounded-lg border bg-white p-3 h-64 overflow-hidden">
          <PlotlyChart data={consumptionTraces} layout={consumptionLayout} />
        </div>
        {onAnalyzeChart && (
          <ChartAiPanel
            chartKey="consumption_trend"
            analysis={chartAnalyses?.consumption_trend}
            onAnalyze={() => onAnalyzeChart("consumption_trend")}
            onRefresh={() => onAnalyzeChart("consumption_trend", true)}
            loading={llmLoading?.["consumption_trend"] || false}
          />
        )}
      </div>

      {/* Peak demand + Renewable generation */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p className="text-sm font-semibold text-foreground">{t("energyHub.trends.peakDemand.title")}</p>
          <p className="text-xs text-muted-foreground mb-2">{t("energyHub.trends.peakDemand.subtitle")}</p>
          <ChartExplanation
            what={t("energyHub.trends.peakDemand.explanation.what")}
            why={t("energyHub.trends.peakDemand.explanation.why")}
            action={t("energyHub.trends.peakDemand.explanation.action")}
          />
          <div className="rounded-lg border bg-white p-3 h-52 overflow-hidden">
            <PlotlyChart data={peakDemandTrace} layout={peakDemandLayout} />
          </div>
          {onAnalyzeChart && (
            <ChartAiPanel
              chartKey="peak_demand"
              analysis={chartAnalyses?.peak_demand}
              onAnalyze={() => onAnalyzeChart("peak_demand")}
              onRefresh={() => onAnalyzeChart("peak_demand", true)}
              loading={llmLoading?.["peak_demand"] || false}
            />
          )}
        </div>
        <div>
          <p className="text-sm font-semibold text-foreground">{t("energyHub.trends.renewable.title")}</p>
          <p className="text-xs text-muted-foreground mb-2">{t("energyHub.trends.renewable.subtitle")}</p>
          <ChartExplanation
            what={t("energyHub.trends.renewable.explanation.what")}
            why={t("energyHub.trends.renewable.explanation.why")}
            action={t("energyHub.trends.renewable.explanation.action")}
          />
          <div className="rounded-lg border bg-white p-3 h-52 overflow-hidden">
            <PlotlyChart data={renewableGenTrace} layout={renewableGenLayout} />
          </div>
          {onAnalyzeChart && (
            <ChartAiPanel
              chartKey="renewable_generation"
              analysis={chartAnalyses?.renewable_generation}
              onAnalyze={() => onAnalyzeChart("renewable_generation")}
              onRefresh={() => onAnalyzeChart("renewable_generation", true)}
              loading={llmLoading?.["renewable_generation"] || false}
            />
          )}
        </div>
      </div>
    </div>
  );
}
