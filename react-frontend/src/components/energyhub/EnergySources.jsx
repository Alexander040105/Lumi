import { useMemo } from "react";

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

function DonutSegment({ start, end, color }) {
  const r = 36;
  const c = 2 * Math.PI * r;
  const dash = `${(end - start) * c} ${c}`;
  const offset = -start * c;
  return (
    <circle
      r={r}
      cx="50"
      cy="50"
      fill="transparent"
      stroke={color}
      strokeWidth="12"
      strokeDasharray={dash}
      strokeDashoffset={offset}
      transform="rotate(-90 50 50)"
    />
  );
}

export default function EnergySources({ breakdown }) {
  const chartData = useMemo(() => {
    if (!breakdown || !breakdown.share_pct) return [];
    const entries = Object.entries(breakdown.share_pct)
      .filter(([, v]) => v > 0)
      .sort(([, a], [, b]) => b - a);

    let acc = 0;
    return entries.map(([key, value]) => {
      const start = acc;
      acc += value / 100;
      return {
        key,
        label: SOURCE_META[key]?.label || key,
        color: SOURCE_META[key]?.color || "#cbd5e1",
        share: value,
        gwh: breakdown.generation_gwh?.[key] || 0,
        start,
        end: acc,
      };
    });
  }, [breakdown]);

  if (!breakdown || chartData.length === 0) {
    return (
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Energy Source Comparison</h3>
        <div className="mt-4 h-48 bg-muted rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <h3 className="text-lg font-semibold">
        Energy Source Comparison ({breakdown.year})
      </h3>
      <p className="text-sm text-muted-foreground">
        Total Generation: {breakdown.total_generation_gwh.toLocaleString()} GWh
      </p>

      <div className="mt-4 flex flex-col md:flex-row items-center gap-6">
        <div className="relative w-48 h-48 shrink-0">
          <svg viewBox="0 0 100 100" className="w-full h-full">
            {chartData.map((d) => (
              <DonutSegment key={d.key} start={d.start} end={d.end} color={d.color} />
            ))}
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <p className="text-xl font-bold">{breakdown.year}</p>
              <p className="text-xs text-muted-foreground">GWh</p>
            </div>
          </div>
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
                <div className="text-right">
                  <span className="text-sm font-semibold">{d.share}%</span>
                  <span className="ml-2 text-xs text-muted-foreground">
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
