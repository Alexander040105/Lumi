import { useEffect, useMemo, useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";
import { getEcosim, getMunicipalities } from "@/services/apiClient";

const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0);

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0
  }).format(value ?? 0);

export default function Ecosim() {
  const [municipalityId, setMunicipalityId] = useState("");
  const [municipalities, setMunicipalities] = useState([]);
  const [municipalitiesError, setMunicipalitiesError] = useState(null);
  const [monthlyConsumption, setMonthlyConsumption] = useState(350);
  const [monthlyBill, setMonthlyBill] = useState(5000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const comparisonMax = useMemo(() => {
    if (!result?.options?.length) return 0;
    return Math.max(...result.options.map((item) => item.estimated_generation_kwh || 0), 1);
  }, [result]);

  useEffect(() => {
    let isActive = true;

    const loadMunicipalities = async () => {
      try {
        const data = await getMunicipalities();
        if (!isActive) return;
        const items = data?.items || [];
        setMunicipalities(items);
        if (!municipalityId && items.length) {
          setMunicipalityId(String(items[0].municipality_id));
        }
      } catch (err) {
        if (!isActive) return;
        setMunicipalitiesError(err?.message || "Unable to load municipalities.");
      }
    };

    loadMunicipalities();
    return () => {
      isActive = false;
    };
  }, [municipalityId]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await getEcosim({
        municipalityId: String(municipalityId).trim(),
        monthlyConsumption: String(monthlyConsumption).trim(),
        monthlyBill: String(monthlyBill).trim()
      });
      setResult(data);
    } catch (err) {
      setError(err?.message || "Unable to load Ecosim data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page-container stack">
      <div className="space-y-2">
        <h1>Renewable Energy Simulation</h1>
        <p className="text-muted-foreground">
          Ecosim evaluates solar, wind, and hydropower options for your location based on
          consumption patterns and environmental data.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Simulation Inputs</CardTitle>
          <CardDescription>Provide your current usage and location to generate a recommendation.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 md:grid-cols-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium">Monthly consumption (kWh)</label>
              <Input
                type="number"
                min="1"
                value={monthlyConsumption}
                onChange={(event) => setMonthlyConsumption(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Monthly bill (PHP)</label>
              <Input
                type="number"
                min="1"
                value={monthlyBill}
                onChange={(event) => setMonthlyBill(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Municipality</label>
              <select
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={municipalityId}
                onChange={(event) => setMunicipalityId(event.target.value)}
              >
                {municipalities.map((item) => (
                  <option key={item.municipality_id} value={item.municipality_id}>
                    {item.name}
                  </option>
                ))}
              </select>
              {municipalitiesError && (
                <p className="text-xs text-destructive">{municipalitiesError}</p>
              )}
            </div>
            <div className="flex items-end">
              <Button type="submit" disabled={loading || !municipalityId} className="w-full">
                {loading ? "Running simulation..." : "Run simulation"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive text-destructive">
          <CardHeader>
            <CardTitle>Simulation error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      )}

      {loading && <LoadingSkeleton />}

      {result && !loading && (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Recommendation</CardTitle>
              <CardDescription>Best-fit renewable source for {result.municipality}</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 md:grid-cols-3">
              <div>
                <p className="text-sm text-muted-foreground">Recommended source</p>
                <p className="text-2xl font-semibold">{result.recommended_source}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Suitability score</p>
                <p className="text-2xl font-semibold">{formatNumber(result.suitability_score, 2)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Estimated generation</p>
                <p className="text-2xl font-semibold">
                  {formatNumber(result.estimated_generation_kwh)} kWh/mo
                </p>
              </div>
              <div className="md:col-span-3 rounded-md border bg-muted/30 p-4 text-sm text-muted-foreground">
                {result.explanation}
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Estimated monthly generation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold">
                  {formatNumber(result.estimated_generation_kwh)} kWh
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Estimated savings</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold">{formatCurrency(result.monthly_savings)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Installation cost</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold">{formatCurrency(result.installation_cost)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Payback period</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold">
                  {result.payback_years ? `${formatNumber(result.payback_years, 1)} yrs` : "N/A"}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Carbon reduction</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold">
                  {formatNumber(result.carbon_reduction)} kg CO2/mo
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Renewable comparison</CardTitle>
              <CardDescription>Monthly generation and savings across options.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              {result.options.map((option) => (
                <div key={option.source} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{option.source}</span>
                    <span className="text-muted-foreground">
                      {formatNumber(option.estimated_generation_kwh)} kWh/mo
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-muted">
                    <div
                      className="h-2 rounded-full bg-primary"
                      style={{ width: `${(option.estimated_generation_kwh / comparisonMax) * 100}%` }}
                    />
                  </div>
                  <div className="text-xs text-muted-foreground">{option.explanation}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Scenario comparison</CardTitle>
              <CardDescription>Current usage vs recommended renewable offset.</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Scenario</TableHead>
                    <TableHead>Consumption (kWh)</TableHead>
                    <TableHead>Monthly bill</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>Current</TableCell>
                    <TableCell>{formatNumber(result.comparison.current_monthly_consumption_kwh)}</TableCell>
                    <TableCell>{formatCurrency(result.comparison.current_monthly_bill)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>With {result.recommended_source}</TableCell>
                    <TableCell>{formatNumber(result.comparison.renewable_monthly_consumption_kwh)}</TableCell>
                    <TableCell>{formatCurrency(result.comparison.renewable_monthly_bill)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}
    </section>
  );
}
