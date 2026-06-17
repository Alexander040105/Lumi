import { useMemo, useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";

function SimpleLine({ data, color = "#3b82f6", height = 160, isForecast = [] }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const width = data.length;

  const buildPoints = (indices) =>
    indices
      .map((i) => {
        const x = (i / (width - 1 || 1)) * 100;
        const y = 100 - ((data[i] - min) / range) * 100;
        return `${x},${y}`;
      })
      .join(" ");

  const histIndices = data.map((_, i) => i).filter((i) => !isForecast[i]);
  const forecastIndices = data.map((_, i) => i).filter((i) => isForecast[i]);

  // Include junction point in both series so the line is continuous
  const lastHist = histIndices.length > 0 ? histIndices[histIndices.length - 1] : null;
  const firstForecast = forecastIndices.length > 0 ? forecastIndices[0] : null;

  const histPoints = buildPoints(histIndices);
  const forecastPoints =
    lastHist !== null && firstForecast !== null
      ? buildPoints([lastHist, ...forecastIndices])
      : buildPoints(forecastIndices);

  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full" style={{ height }}>
      {histPoints && (
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
          points={histPoints}
        />
      )}
      {forecastPoints && (
        <polyline
          fill="none"
          stroke="#f87171"
          strokeWidth="2"
          strokeDasharray="4 3"
          vectorEffect="non-scaling-stroke"
          points={forecastPoints}
        />
      )}
    </svg>
  );
}

function SimpleBar({ data, color = "#3b82f6", height = 160 }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data);
  return (
    <svg viewBox={`0 0 ${data.length * 10} 100`} preserveAspectRatio="none" className="w-full" style={{ height }}>
      {data.map((v, i) => {
        const h = max ? (v / max) * 90 : 0;
        return (
          <rect
            key={i}
            x={i * 10 + 1}
            y={100 - h}
            width={8}
            height={h}
            fill={color}
            rx={2}
          />
        );
      })}
    </svg>
  );
}

function ChartAiPanel({ chartKey, analysis, onAnalyze, onRefresh, loading }) {
  if (!analysis && !loading) {
    return (
      <button
        onClick={onAnalyze}
        className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 border border-amber-200 hover:bg-amber-100 transition-colors"
      >
        <Sparkles className="h-3 w-3" />
        AI Explain
      </button>
    );
  }

  if (loading) {
    return (
      <div className="mt-2 inline-flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700 border border-amber-200">
        <Loader2 className="h-3 w-3 animate-spin" />
        Generating analysis...
      </div>
    );
  }

  return (
    <div className="mt-2 rounded-lg bg-amber-50 border border-amber-100 p-3">
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs leading-relaxed text-amber-900 whitespace-pre-line flex-1">{analysis?.insight}</p>
        {onRefresh && (
          <button
            onClick={onRefresh}
            title="Get a different explanation"
            className="shrink-0 inline-flex items-center gap-1 rounded-md bg-amber-100 px-2 py-1 text-[10px] font-medium text-amber-700 border border-amber-200 hover:bg-amber-200 transition-colors"
          >
            <Sparkles className="h-3 w-3" />
            Refresh
          </button>
        )}
      </div>
    </div>
  );
}

export default function EnergyTrends({ trends, chartAnalyses, llmLoading, onAnalyzeChart }) {
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

  if (!years.length) {
    return (
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Energy Trends</h3>
        <div className="mt-4 h-48 bg-muted rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Energy Trends</h3>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-blue-500" />
            Historical
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-red-400" />
            Forecast
          </span>
        </div>
      </div>

      {/* Consumption trend */}
      <div className="mt-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">Total Consumption (GWh) — Historical vs Forecast</p>
        </div>
        <div className="relative rounded-lg border bg-white p-3">
          <SimpleLine data={consumptionSeries.values} color="#3b82f6" height={200} isForecast={consumptionSeries.isForecast} />
          <div className="mt-2 flex justify-between text-xs text-muted-foreground">
            <span>{consumptionSeries.years[0]}</span>
            <span>{consumptionSeries.years[consumptionSeries.years.length - 1]}</span>
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
          <p className="text-sm text-muted-foreground mb-2">Peak Demand (MW)</p>
          <div className="rounded-lg border bg-white p-3">
            <SimpleLine data={series.total_peak_demand_mw || []} color="#f43f5e" height={140} />
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
          <p className="text-sm text-muted-foreground mb-2">Renewable Generation (GWh)</p>
          <div className="rounded-lg border bg-white p-3">
            <SimpleBar data={series.renewable_generation_gwh || []} color="#10b981" height={140} />
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
