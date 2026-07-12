import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getProvincialDemand } from "@/services/energyhub";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Lightbulb, Info } from "lucide-react";

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
        if (!cancelled) setError(err?.message || "Failed to load provincial demand.");
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
          <CardTitle>Provincial Demand</CardTitle>
          <CardDescription>Loading DOE Annex 8 regional consumption data...</CardDescription>
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
          <CardTitle>Provincial Demand</CardTitle>
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
          <CardTitle>Provincial Demand</CardTitle>
          <CardDescription>{data?.note || "No data available."}</CardDescription>
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
        <CardTitle>Provincial Demand (2025)</CardTitle>
        <CardDescription>
          Electricity consumption by sector per region (GWh). Sourced from DOE Annex 8.
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
                labelFormatter={(label) => `Region: ${label}`}
              />
              {SECTORS.map((sector) => (
                <Bar
                  key={sector}
                  dataKey={sector}
                  stackId="a"
                  fill={COLORS[sector]}
                  name={sector}
                  radius={[0, 0, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="rounded-md bg-sky-50 border border-sky-100 p-3 space-y-2">
          <div className="flex items-center gap-1.5 text-sky-800">
            <Lightbulb className="h-3.5 w-3.5" />
            <span className="text-xs font-semibold">What you are seeing</span>
          </div>
          <p className="text-xs text-sky-700 leading-relaxed">
            This chart shows how much electricity each Philippine region used in 2025, broken down by who uses it: homes (green), businesses (blue), factories (orange), and government or street lighting (gray). NCR and Calabarzon (IV-A) tower over the rest because they are the country’s economic and population hubs — think of them as the “engine rooms” of the Philippines. Smaller bars do not mean those regions are less important; they simply have fewer people and industries connected to the main grid. Some remote or island regions may also rely more on local generators rather than the national grid, so their numbers here can look lower than their actual energy use.
          </p>
          <div className="flex items-center gap-1.5 text-sky-800 pt-1">
            <Info className="h-3.5 w-3.5" />
            <span className="text-xs font-semibold">Why 17 regions?</span>
          </div>
          <p className="text-xs text-sky-700 leading-relaxed">
            The Philippines has 17 administrative regions. The data here follows the Department of Energy’s 2025 reporting format, which still labels the Bangsamoro region as “ARMM” (its older name). The now-dissolved Negros Island Region (NIR) is excluded because it was re-merged into Western Visayas (VI) and Central Visayas (VII) in 2015.
          </p>
        </div>
        <p className="text-xs text-muted-foreground">{data?.note || ""}</p>
      </CardContent>
    </Card>
  );
}
