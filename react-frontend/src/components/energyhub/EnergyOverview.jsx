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
      interpretation: `The Philippines used ${latest.total_consumption_gwh.toLocaleString()} billion kWh of electricity in ${latest.year}. That's enough to power millions of homes.`,
      icon: Zap,
      color: "text-amber-500",
      bg: "bg-amber-50",
    },
    {
      label: "Peak Demand",
      value: `${latest.total_peak_demand_mw.toLocaleString()} MW`,
      sub: `Year ${latest.year}`,
      interpretation: `The highest electricity demand ever recorded. When demand is high, prices can spike and brownouts become more likely.`,
      icon: Activity,
      color: "text-rose-500",
      bg: "bg-rose-50",
    },
    {
      label: "Renewable Share",
      value: `${latest.renewable_share_pct}%`,
      sub: `${latest.renewable_generation_gwh.toLocaleString()} GWh generated`,
      interpretation: `${latest.renewable_share_pct}% of electricity comes from clean sources like solar, wind, and hydro. The Philippines aims to reach 35% by 2030.`,
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
      interpretation: forecast_summary?.forecast_growth_pct
        ? `By 2030, electricity use is expected to grow ${forecast_summary.forecast_growth_pct}%. More clean energy is needed to meet this demand.`
        : "Future electricity demand projections help plan for new power plants and renewable energy investments.",
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
          <div className="flex items-start justify-between">
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-muted-foreground">{card.label}</p>
              <p className="mt-1 text-2xl font-bold tracking-tight">{card.value}</p>
              <p className="mt-0.5 text-xs text-muted-foreground">{card.sub}</p>
              {card.interpretation && (
                <p className="mt-2 text-xs text-slate-600 leading-relaxed border-t pt-2 border-slate-100">
                  {card.interpretation}
                </p>
              )}
            </div>
            <div className={`rounded-lg p-2.5 ${card.bg} shrink-0 ml-3`}>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
