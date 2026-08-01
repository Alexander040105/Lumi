import { Zap, TrendingUp, Sun, Activity } from "lucide-react";
import { useI18n } from "@/i18n";

export default function EnergyOverview({ data }) {
  const { t } = useI18n();
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
      label: t("energyHub.overview.consumption.label"),
      value: t("energyHub.overview.consumption.value", { value: latest.total_consumption_gwh.toLocaleString() }),
      sub: t("energyHub.overview.consumption.sub", { year: latest.year }),
      interpretation: t("energyHub.overview.consumption.interpretation", { value: latest.total_consumption_gwh.toLocaleString(), year: latest.year }),
      icon: Zap,
      color: "text-amber-500",
      bg: "bg-amber-50",
    },
    {
      label: t("energyHub.overview.peakDemand.label"),
      value: t("energyHub.overview.peakDemand.value", { value: latest.total_peak_demand_mw.toLocaleString() }),
      sub: t("energyHub.overview.peakDemand.sub", { year: latest.year }),
      interpretation: t("energyHub.overview.peakDemand.interpretation"),
      icon: Activity,
      color: "text-rose-500",
      bg: "bg-rose-50",
    },
    {
      label: t("energyHub.overview.renewableShare.label"),
      value: t("energyHub.overview.renewableShare.value", { share: latest.renewable_share_pct }),
      sub: t("energyHub.overview.renewableShare.sub", { generated: latest.renewable_generation_gwh.toLocaleString() }),
      interpretation: t("energyHub.overview.renewableShare.interpretation", { share: latest.renewable_share_pct }),
      icon: Sun,
      color: "text-emerald-500",
      bg: "bg-emerald-50",
    },
    {
      label: t("energyHub.overview.forecastGrowth.label"),
      value: t("energyHub.overview.forecastGrowth.value", {
        value: forecast_summary?.forecast_growth_pct
          ? `+${forecast_summary.forecast_growth_pct}%`
          : t("energyHub.overview.forecastGrowth.na")
      }),
      sub: forecast_summary?.forecast_2030_gwh
        ? t("energyHub.overview.forecastGrowth.sub", { value: forecast_summary.forecast_2030_gwh.toLocaleString() })
        : t("energyHub.overview.forecastGrowth.subEmpty"),
      interpretation: forecast_summary?.forecast_growth_pct
        ? t("energyHub.overview.forecastGrowth.interpretation", { pct: forecast_summary.forecast_growth_pct })
        : t("energyHub.overview.forecastGrowth.interpretationFallback"),
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
