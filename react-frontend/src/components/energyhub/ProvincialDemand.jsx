import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getProvincialDemand } from "@/services/energyhub";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const SECTORS = ["Residential", "Commercial", "Industrial", "Others"];
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
  const regions = [...regionSet].sort((a, b) => a.localeCompare(b));

  const chartData = regions.map((r) => {
    const row = { region: r };
    for (const sector of SECTORS) {
      const key = `${r}||${sector}`;
      row[sector] = aggregated[key] ? aggregated[key].value_mwh / 1000 : 0;
    }
    const totalKey = `${r}||Total Consumption`;
    row["Total"] = aggregated[totalKey] ? aggregated[totalKey].value_mwh / 1000 : 0;
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
        <p className="text-xs text-muted-foreground">{data?.note || ""}</p>
      </CardContent>
    </Card>
  );
}
