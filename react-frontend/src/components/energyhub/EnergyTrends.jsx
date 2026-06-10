import { useMemo } from "react";

function SimpleLine({ data, color = "#3b82f6", height = 160 }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const width = data.length;
  const points = data
    .map((v, i) => {
      const x = (i / (width - 1 || 1)) * 100;
      const y = 100 - ((v - min) / range) * 100;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full" style={{ height }}>
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
        points={points}
      />
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

export default function EnergyTrends({ trends }) {
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

      <div className="mt-4">
        <p className="text-sm text-muted-foreground mb-2">Total Consumption (GWh) — Historical vs Forecast</p>
        <div className="relative rounded-lg border bg-white p-3">
          <SimpleLine data={consumptionSeries.values} color="#3b82f6" height={200} />
          <div className="mt-2 flex justify-between text-xs text-muted-foreground">
            <span>{consumptionSeries.years[0]}</span>
            <span>{consumptionSeries.years[consumptionSeries.years.length - 1]}</span>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-muted-foreground mb-2">Peak Demand (MW)</p>
          <div className="rounded-lg border bg-white p-3">
            <SimpleLine data={series.total_peak_demand_mw || []} color="#f43f5e" height={140} />
          </div>
        </div>
        <div>
          <p className="text-sm text-muted-foreground mb-2">Renewable Generation (GWh)</p>
          <div className="rounded-lg border bg-white p-3">
            <SimpleBar data={series.renewable_generation_gwh || []} color="#10b981" height={140} />
          </div>
        </div>
      </div>
    </div>
  );
}
