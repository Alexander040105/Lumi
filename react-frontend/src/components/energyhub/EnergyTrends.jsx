import { useMemo, useState } from "react";
import { Sparkles, Loader2, Maximize2 } from "lucide-react";
import { useI18n } from "@/i18n";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { sanitizeLLMOutput } from "@/utils/llmText";
import ReadAloud from "@/components/shared/ReadAloud";
import PlotlyChart from "./PlotlyChart";
import ChartExplanation from "./ChartExplanation";

function cssVarColor(name, fallback) {
  if (typeof window === "undefined") return fallback;
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v ? `hsl(${v})` : fallback;
}

function ChartAiPanel({ chartKey, analysis, onAnalyze, onRefresh, loading }) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);
  if (!analysis && !loading) {
    return (
      <button
        onClick={onAnalyze}
        className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-warning/10 px-3 py-2 min-h-[40px] text-xs font-medium text-foreground border border-warning/20 hover:bg-warning/20 transition-colors"
      >
        <Sparkles className="h-3 w-3 text-warning" aria-hidden="true" />
        {t("energyHub.trends.aiExplain")}
      </button>
    );
  }

  if (loading) {
    return (
      <div className="mt-2 inline-flex items-center gap-2 rounded-md bg-warning/10 px-3 py-2 text-xs text-foreground border border-warning/20">
        <Loader2 className="h-3 w-3 animate-spin text-warning" aria-hidden="true" />
        {t("energyHub.trends.generating")}
      </div>
    );
  }

  const displayText = sanitizeLLMOutput(analysis?.insight);
  const isLong = displayText.length > 350;

  return (
    <div className="mt-2 rounded-lg bg-warning/10 border border-warning/20 p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p
            className={`text-xs leading-relaxed text-foreground whitespace-pre-line ${
              expanded ? "" : "line-clamp-4"
            }`}
          >
            {displayText}
          </p>
          {isLong && (
            <button
              type="button"
              onClick={() => setExpanded((v) => !v)}
              aria-expanded={expanded}
              className="mt-1 text-xs font-medium text-foreground underline underline-offset-2 hover:text-primary transition-colors"
            >
              {expanded ? t("energyHub.trends.showLess") : t("energyHub.trends.readMore")}
            </button>
          )}
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1.5">
          <ReadAloud text={displayText} />
          {onRefresh && (
            <button
              onClick={onRefresh}
              title={t("energyHub.trends.getDifferent")}
              className="inline-flex items-center gap-1 rounded-md bg-warning/10 px-2 py-1 min-h-[36px] text-xs font-medium text-foreground border border-warning/20 hover:bg-warning/20 transition-colors"
            >
              <Sparkles className="h-3 w-3 text-warning" aria-hidden="true" />
              {t("energyHub.trends.refresh")}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function EnergyTrends({ trends, chartAnalyses, llmLoading, onAnalyzeChart }) {
  const { t } = useI18n();
  const [modal, setModal] = useState(null);
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
        line: { color: cssVarColor("--brand-success", "#10b981"), width: 3 },
        marker: { size: 6 },
        hovertemplate: t("energyHub.trends.hover.consumption", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.historical") }),
      },
      {
        x: forecastX,
        y: forecastY,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.legend.forecast"),
        line: { color: cssVarColor("--destructive", "#f87171"), width: 3, dash: "dash" },
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
      legend: { orientation: "h", y: -0.25, font: { size: 11 } },
      margin: { t: 16, r: 8, b: 48, l: 56 },
    }),
    [t]
  );

  const peakDemandTraces = useMemo(() => {
    const hist = series.total_peak_demand_mw || [];
    const fYears = trends?.forecast_peak?.forecast_years || [];
    const fValues = trends?.forecast_peak?.forecast_values || [];
    const allYears = [...years, ...fYears];
    const allValues = [...hist, ...fValues];
    const isF = [...Array(hist.length).fill(false), ...Array(fValues.length).fill(true)];
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
        line: { color: cssVarColor("--brand-success", "#10b981"), width: 2 },
        marker: { size: 5 },
        hovertemplate: t("energyHub.trends.hover.peakDemand", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.historical") }),
      },
      {
        x: forecastX,
        y: forecastY,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.legend.forecast"),
        line: { color: cssVarColor("--destructive", "#f87171"), width: 2, dash: "dash" },
        marker: { size: 5 },
        hovertemplate: t("energyHub.trends.hover.peakDemand", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.forecast") }),
      },
    ];
  }, [years, series, trends, t]);

  const peakDemandLayout = useMemo(
    () => ({
      xaxis: { title: t("energyHub.trends.chartAxis.year"), tickmode: "linear", dtick: 1 },
      yaxis: { title: t("energyHub.trends.chartAxis.mw") },
      legend: { orientation: "h", y: -0.25, font: { size: 11 } },
      margin: { t: 16, r: 8, b: 48, l: 56 },
    }),
    [t]
  );

  const renewableGenTraces = useMemo(() => {
    const hist = series.renewable_generation_gwh || [];
    const fYears = trends?.forecast_renewable?.forecast_years || [];
    const fValues = trends?.forecast_renewable?.forecast_values || [];
    const histX = [...years];
    const histY = [...hist];
    const forecastX = [...fYears];
    const forecastY = [...fValues];

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
        line: { color: cssVarColor("--brand-success", "#10b981"), width: 2 },
        marker: { size: 5, color: cssVarColor("--brand-success", "#10b981") },
        hovertemplate: t("energyHub.trends.hover.renewable", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.historical") }),
      },
      {
        x: forecastX,
        y: forecastY,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.legend.forecast"),
        line: { color: cssVarColor("--destructive", "#f87171"), width: 2, dash: "dash" },
        marker: { size: 5 },
        hovertemplate: t("energyHub.trends.hover.renewable", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.forecast") }),
      },
    ];
  }, [years, series, trends, t]);

  const renewableGenLayout = useMemo(
    () => ({
      xaxis: { title: t("energyHub.trends.chartAxis.year"), tickmode: "linear", dtick: 1 },
      yaxis: { title: t("energyHub.trends.chartAxis.gwh") },
      legend: { orientation: "h", y: -0.25, font: { size: 11 } },
      margin: { t: 16, r: 8, b: 48, l: 56 },
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
            <span className="inline-block h-2 w-2 rounded-full bg-success" />
            {t("energyHub.trends.legend.historical")}
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-destructive" />
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
        <div className="relative rounded-lg border bg-card p-3 h-64 overflow-hidden">
          <button
            type="button"
            onClick={() =>
              setModal({
                title: t("energyHub.trends.consumption.title"),
                subtitle: t("energyHub.trends.consumption.subtitle"),
                data: consumptionTraces,
                layout: consumptionLayout,
              })
            }
            className="absolute top-2 right-2 z-10 flex h-10 w-10 items-center justify-center rounded-md border bg-card p-2 text-muted-foreground hover:text-foreground shadow-sm"
            aria-label={t("energyHub.trends.enlarge")}
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </button>
          <div role="img" aria-label={t("energyHub.trends.consumption.title")} className="h-full w-full">
            <PlotlyChart data={consumptionTraces} layout={consumptionLayout} />
          </div>
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
          <div className="relative rounded-lg border bg-card p-3 h-52 overflow-hidden">
            <button
              type="button"
              onClick={() =>
                setModal({
                  title: t("energyHub.trends.peakDemand.title"),
                  subtitle: t("energyHub.trends.peakDemand.subtitle"),
                  data: peakDemandTraces,
                  layout: peakDemandLayout,
                })
              }
              className="absolute top-2 right-2 z-10 flex h-10 w-10 items-center justify-center rounded-md border bg-card p-2 text-muted-foreground hover:text-foreground shadow-sm"
              aria-label={t("energyHub.trends.enlarge")}
            >
              <Maximize2 className="h-3.5 w-3.5" />
            </button>
            <div role="img" aria-label={t("energyHub.trends.peakDemand.title")} className="h-full w-full">
              <PlotlyChart data={peakDemandTraces} layout={peakDemandLayout} />
            </div>
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
          <div className="relative rounded-lg border bg-card p-3 h-52 overflow-hidden">
            <button
              type="button"
              onClick={() =>
                setModal({
                  title: t("energyHub.trends.renewable.title"),
                  subtitle: t("energyHub.trends.renewable.subtitle"),
                  data: renewableGenTraces,
                  layout: renewableGenLayout,
                })
              }
              className="absolute top-2 right-2 z-10 flex h-10 w-10 items-center justify-center rounded-md border bg-card p-2 text-muted-foreground hover:text-foreground shadow-sm"
              aria-label={t("energyHub.trends.enlarge")}
            >
              <Maximize2 className="h-3.5 w-3.5" />
            </button>
            <div role="img" aria-label={t("energyHub.trends.renewable.title")} className="h-full w-full">
              <PlotlyChart data={renewableGenTraces} layout={renewableGenLayout} />
            </div>
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

      <Dialog open={!!modal} onOpenChange={() => setModal(null)}>
        <DialogContent className="max-w-4xl h-[80vh] p-4 flex flex-col">
          <DialogHeader>
            <DialogTitle>{modal?.title}</DialogTitle>
            <DialogDescription>{modal?.subtitle}</DialogDescription>
          </DialogHeader>
          <div className="flex-1 min-h-0">
            {modal && (
              <div role="img" aria-label={modal.title} className="h-full w-full">
                <PlotlyChart data={modal.data} layout={modal.layout} />
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
