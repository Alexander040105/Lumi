import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getProvincialDemand } from "@/services/energyhub";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useI18n } from "@/i18n";
import ExpandableBlock from "@/components/shared/ExpandableBlock";

const SECTORS = ["Residential", "Commercial", "Industrial", "Others"];
const VALID_REGIONS = new Set([
  "ARMM", "CAR", "NCR", "I", "II", "III", "IV-A", "IV-B", "V",
  "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "BARMM", "MIMAROPA",
]);
const COLORS = {
  Residential: "#22c55e",
  Commercial: "#3b82f6",
  Industrial: "#f59e0b",
  Others: "#64748b",
};

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value ?? 0);
}

export default function ProvincialDemand({ region = null }) {
  const { t } = useI18n();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getProvincialDemand(region)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message || t("energyHub.provincialDemand.error"));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [region]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("energyHub.provincialDemand.title")}</CardTitle>
          <CardDescription>{t("energyHub.provincialDemand.loading")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 animate-pulse rounded bg-muted" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("energyHub.provincialDemand.title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-destructive text-sm">{error}</p>
        </CardContent>
      </Card>
    );
  }

  const items = data?.items || [];
  if (!items.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("energyHub.provincialDemand.title")}</CardTitle>
          <CardDescription>{data?.note || t("energyHub.provincialDemand.noData")}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  // Build chart data: normalize region names, aggregate by region+sector,
  // then produce one row per unique region.
  const aggregated = {};
  for (const item of items) {
    const region = (item.region ?? "").trim();
    if (!region) continue;
    // Skip rows where region looks like a number (corrupted data)
    if (/^\d{1,3}(,\d{3})+$/.test(region)) continue;
    if (!VALID_REGIONS.has(region.toUpperCase())) continue;
    const sector = item.sector;
    const key = `${region}||${sector}`;
    if (!aggregated[key]) {
      aggregated[key] = { region, sector, value_mwh: 0 };
    }
    aggregated[key].value_mwh += item.value_mwh ?? 0;
  }

  const regionSet = new Set();
  for (const key in aggregated) {
    regionSet.add(aggregated[key].region);
  }

  // Sort regions by total consumption (descending) for visual impact
  const regions = [...regionSet].sort((a, b) => {
    const totalA = SECTORS.reduce((sum, s) => sum + (aggregated[`${a}||${s}`]?.value_mwh ?? 0), 0);
    const totalB = SECTORS.reduce((sum, s) => sum + (aggregated[`${b}||${s}`]?.value_mwh ?? 0), 0);
    return totalB - totalA;
  });

  const chartData = regions.map((r) => {
    const row = { region: r };
    for (const sector of SECTORS) {
      const key = `${r}||${sector}`;
      row[sector] = aggregated[key] ? aggregated[key].value_mwh / 1000 : 0;
    }
    return row;
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("energyHub.provincialDemand.title")} (2025)</CardTitle>
        <CardDescription>
          {t("energyHub.provincialDemand.note")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis tickFormatter={(v) => `${v.toFixed(0)}`} />
              <Tooltip
                formatter={(value, name) => [formatNumber(value) + " GWh", name]}
                labelFormatter={(label) => t("energyHub.provincialDemand.regionLabel", { region: label })}
              />
              {SECTORS.map((sector) => (
                <Bar
                  key={sector}
                  dataKey={sector}
                  stackId="a"
                  fill={COLORS[sector]}
                  name={t(`energyHub.provincialDemand.sectors.${sector.toLowerCase()}`)}
                  radius={[0, 0, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
        <ExpandableBlock
          title={t("energyHub.provincialDemand.insight.title")}
          content={t("energyHub.provincialDemand.insight.description")}
        />
        <ExpandableBlock
          title={t("energyHub.provincialDemand.insight.whyTitle")}
          content={t("energyHub.provincialDemand.insight.whyDescription")}
        />
        <p className="text-xs text-muted-foreground">{data?.note || ""}</p>
      </CardContent>
    </Card>
  );
}
