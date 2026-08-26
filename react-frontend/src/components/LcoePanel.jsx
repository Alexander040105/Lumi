import { useMemo } from "react";
import { useI18n } from "@/i18n";

export default function LcoePanel({ options }) {
  const { t } = useI18n();
  if (!options || !Array.isArray(options) || options.length === 0) {
    return null;
  }

  const sorted = useMemo(
    () => [...options].sort((a, b) => (a.lcoe_php_kwh ?? Infinity) - (b.lcoe_php_kwh ?? Infinity)),
    [options]
  );

  const bestLcoe = sorted[0]?.lcoe_php_kwh;
  const tariff = options[0]?.monthly_savings && options[0]?.estimated_generation_kwh
    ? options[0].monthly_savings / options[0].estimated_generation_kwh
    : null;

  return (
    <div className="bg-card rounded-xl shadow-sm border border-border p-6">
      <h3 className="text-lg font-bold text-foreground mb-1">{t("ecosim.lcoe.title")}</h3>
      <p className="text-sm text-muted-foreground mb-4">
        {t("ecosim.lcoe.description")}
        {tariff && (
          <span className="ml-1 text-blue-600">
            {t("ecosim.lcoe.rateText", { rate: tariff.toFixed(2) })}
          </span>
        )}
      </p>

      <div className="space-y-3">
        {sorted.map((opt) => {
          const lcoe = opt.lcoe_php_kwh;
          const isBest = lcoe === bestLcoe && lcoe != null;
          const gridTariff = tariff ?? 12.0;
          const barWidth = lcoe != null
            ? Math.min((lcoe / gridTariff) * 100, 200)
            : 0;

          return (
            <div key={opt.source} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-foreground">{opt.source}</span>
                  {isBest && (
                    <span className="inline-block px-2 py-0.5 rounded text-xs bg-primary/10 text-primary font-medium">
                      {t("ecosim.lcoe.bestLcoe")}
                    </span>
                  )}
                </div>
                <div className="text-right">
                  <span className={`font-bold ${isBest ? "text-primary" : "text-foreground"}`}>
                    {lcoe != null ? `₱${lcoe.toFixed(2)}` : "—"}
                  </span>
                  <span className="text-muted-foreground text-xs ml-1">/kWh</span>
                </div>
              </div>

              {/* LCOE bar */}
              <div className="relative h-6 bg-muted rounded-lg overflow-hidden">
                <div
                  className={`h-full rounded-lg transition-all ${
                    isBest ? "bg-green-500" : lcoe != null && lcoe < gridTariff ? "bg-blue-400" : "bg-orange-400"
                  }`}
                  style={{ width: `${barWidth}%` }}
                />
                {/* Grid tariff marker */}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-gray-700"
                  style={{ left: "50%" }}
                  title={t("ecosim.lcoe.gridTariff", { rate: gridTariff.toFixed(2) })}
                />
              </div>

              {/* Financial details */}
              <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                <span>{t("ecosim.lcoe.npv")}: {opt.npv_php != null ? `₱${(opt.npv_php / 1e6).toFixed(1)}M` : "—"}</span>
                <span>{t("ecosim.lcoe.irr")}: {opt.irr != null ? `${(opt.irr * 100).toFixed(1)}%` : "—"}</span>
                <span>{t("ecosim.lcoe.discountedPayback")}: {opt.discounted_payback_years != null ? `${opt.discounted_payback_years.toFixed(1)} yrs` : "—"}</span>
                <span>{t("ecosim.lcoe.bcr")}: {opt.benefit_cost_ratio != null ? opt.benefit_cost_ratio.toFixed(2) : "—"}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-border text-xs text-muted-foreground">
        {t("ecosim.lcoe.formula")}
      </div>
    </div>
  );
}
