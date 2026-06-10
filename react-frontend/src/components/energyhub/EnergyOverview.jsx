import { Zap, TrendingUp, Sun, Activity } from "lucide-react";

export default function EnergyOverview({ data }) {
  if (!data || !data.latest) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-muted rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  const { latest, forecast_summary } = data;

  const cards = [
    {
      label: "Total Consumption",
      value: `${latest.total_consumption_gwh.toLocaleString()} GWh`,
      sub: `Year ${latest.year}`,
      icon: Zap,
      color: "text-amber-500",
      bg: "bg-amber-50",
    },
    {
      label: "Peak Demand",
      value: `${latest.total_peak_demand_mw.toLocaleString()} MW`,
      sub: `Year ${latest.year}`,
      icon: Activity,
      color: "text-rose-500",
      bg: "bg-rose-50",
    },
    {
      label: "Renewable Share",
      value: `${latest.renewable_share_pct}%`,
      sub: `${latest.renewable_generation_gwh.toLocaleString()} GWh generated`,
      icon: Sun,
      color: "text-emerald-500",
      bg: "bg-emerald-50",
    },
    {
      label: "Forecast Growth (2030)",
      value: forecast_summary?.forecast_growth_pct
        ? `+${forecast_summary.forecast_growth_pct}%`
        : "N/A",
      sub: forecast_summary?.forecast_2030_gwh
        ? `${forecast_summary.forecast_2030_gwh.toLocaleString()} GWh projected`
        : "",
      icon: TrendingUp,
      color: "text-sky-500",
      bg: "bg-sky-50",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-xl border bg-card p-5 shadow-sm transition-shadow hover:shadow-md"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">{card.label}</p>
              <p className="mt-1 text-2xl font-bold tracking-tight">{card.value}</p>
              <p className="mt-0.5 text-xs text-muted-foreground">{card.sub}</p>
            </div>
            <div className={`rounded-lg p-2.5 ${card.bg}`}>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
