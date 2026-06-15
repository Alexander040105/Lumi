import { useContext, useEffect, useMemo, useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";
import { getEcosim, getHomes, getMunicipalities, getSeasonalEcosim, saveSimulation } from "@/services/apiClient";
import { AuthContext } from "@/context/AuthContext";

const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0);

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0
  }).format(value ?? 0);

export default function Ecosim() {
  const { session, accessToken } = useContext(AuthContext);

  const [municipalityId, setMunicipalityId] = useState("");
  const [municipalities, setMunicipalities] = useState([]);
  const [municipalitiesError, setMunicipalitiesError] = useState(null);
  const [muniQuery, setMuniQuery] = useState("");
  const [muniOpen, setMuniOpen] = useState(false);
  const [monthlyConsumption, setMonthlyConsumption] = useState(350);
  const [monthlyBill, setMonthlyBill] = useState(5000);
  const [includeAi, setIncludeAi] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Save-to-home state
  const [homes, setHomes] = useState([]);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [selectedHomeId, setSelectedHomeId] = useState("");
  const [simulationName, setSimulationName] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Seasonal state
  const [seasonalMode, setSeasonalMode] = useState(false);
  const [seasonalData, setSeasonalData] = useState(null);
  const [seasonalLoading, setSeasonalLoading] = useState(false);
  const [seasonalError, setSeasonalError] = useState(null);

  const filteredMunicipalities = useMemo(() => {
    const q = muniQuery.trim().toLowerCase();
    if (!q) return municipalities;
    return municipalities.filter((m) => m.name.toLowerCase().includes(q));
  }, [municipalities, muniQuery]);

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
        if (items.length) {
          setMunicipalityId(String(items[0].municipality_id));
          setMuniQuery(items[0].name);
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
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    setSaveSuccess(false);

    try {
      const data = await getEcosim({
        municipalityId: String(municipalityId).trim(),
        monthlyConsumption: Number(monthlyConsumption),
        monthlyBill: Number(monthlyBill),
        includeAi,
      });
      setResult(data);
    } catch (err) {
      setError(err?.message || "Unable to load Ecosim data.");
    } finally {
      setLoading(false);
    }
  };

  const openSaveModal = async () => {
    setSaveError(null);
    setSaveSuccess(false);
    setSimulationName(`${result.recommended_source} — ${result.municipality}`);
    try {
      const data = await getHomes(accessToken);
      setHomes(data?.items || []);
      if (data?.items?.length) {
        setSelectedHomeId(data.items[0].home_id);
      }
      setShowSaveModal(true);
    } catch (err) {
      setSaveError(err?.message || "Unable to load your homes.");
    }
  };

  const handleSaveSimulation = async () => {
    if (!selectedHomeId) {
      setSaveError("Please select a home.");
      return;
    }
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);

    const payload = {
      simulation_name: simulationName || `${result.recommended_source} — ${result.municipality}`,
      recommended_source: result.recommended_source,
      suitability_score: result.suitability_score,
      estimated_generation_kwh: result.estimated_generation_kwh,
      monthly_savings_php: result.monthly_savings,
      installation_cost_php: result.installation_cost,
      payback_years: result.payback_years,
      carbon_reduction_kg: result.carbon_reduction,
      independence_score: result.independence_score,
      results_json: {
        options: result.options,
        comparison: result.comparison,
        climate: result.climate,
        renewable_energy_results: result.renewable_energy_results,
      },
      ai_analysis_json: result.ai_analysis,
    };

    try {
      await saveSimulation(accessToken, selectedHomeId, payload);
      setSaveSuccess(true);
      setTimeout(() => setShowSaveModal(false), 1200);
    } catch (err) {
      setSaveError(err?.message || "Failed to save simulation.");
    } finally {
      setSaving(false);
    }
  };

  const fetchSeasonalData = async () => {
    if (!municipalityId) return;
    setSeasonalLoading(true);
    setSeasonalError(null);
    try {
      const data = await getSeasonalEcosim(String(municipalityId).trim());
      setSeasonalData(data);
    } catch (err) {
      setSeasonalError(err?.message || "Failed to load seasonal data.");
    } finally {
      setSeasonalLoading(false);
    }
  };

  const toggleSeasonal = () => {
    const next = !seasonalMode;
    setSeasonalMode(next);
    if (next && !seasonalData) {
      fetchSeasonalData();
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
                onChange={(event) => setMonthlyConsumption(Number(event.target.value))}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Monthly bill (PHP)</label>
              <Input
                type="number"
                min="1"
                value={monthlyBill}
                onChange={(event) => setMonthlyBill(Number(event.target.value))}
              />
            </div>
            <div className="relative space-y-2">
              <label className="text-sm font-medium">Municipality</label>
              <Input
                type="text"
                placeholder="Search municipality..."
                value={muniQuery}
                onChange={(e) => {
                  setMuniQuery(e.target.value);
                  setMuniOpen(true);
                }}
                onFocus={() => setMuniOpen(true)}
                onBlur={() => setMuniOpen(false)}
                disabled={loading}
                autoComplete="off"
              />
              {muniOpen && (
                <div className="absolute z-10 mt-1 max-h-56 w-full overflow-auto rounded-md border border-input bg-popover shadow-md">
                  {filteredMunicipalities.length ? (
                    filteredMunicipalities.map((item) => (
                      <button
                        key={item.municipality_id}
                        type="button"
                        className={
                          "w-full px-3 py-2 text-left text-sm transition-colors hover:bg-accent " +
                          (String(item.municipality_id) === municipalityId
                            ? "bg-accent font-medium"
                            : "")
                        }
                        onMouseDown={(e) => e.preventDefault()}
                        onClick={() => {
                          setMunicipalityId(String(item.municipality_id));
                          setMuniQuery(item.name);
                          setMuniOpen(false);
                        }}
                      >
                        {item.name}
                      </button>
                    ))
                  ) : (
                    <div className="px-3 py-2 text-sm text-muted-foreground">
                      No results found
                    </div>
                  )}
                </div>
              )}
              {municipalitiesError && (
                <p className="text-xs text-destructive">{municipalitiesError}</p>
              )}
            </div>
            <div className="flex items-end space-x-2">
              <label className="flex items-center space-x-2 text-sm">
                <input
                  type="checkbox"
                  checked={includeAi}
                  onChange={(e) => setIncludeAi(e.target.checked)}
                  disabled={loading}
                  className="h-4 w-4 rounded border-brand-light text-primary accent-primary focus:ring-primary"
                />
                <span>Include AI analysis</span>
              </label>
            </div>
            <div className="flex items-end space-x-2">
              <label className="flex items-center space-x-2 text-sm">
                <input
                  type="checkbox"
                  checked={seasonalMode}
                  onChange={toggleSeasonal}
                  disabled={loading}
                  className="h-4 w-4 rounded border-brand-light text-primary accent-primary focus:ring-primary"
                />
                <span>Seasonal breakdown</span>
              </label>
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
          {/* Recommendation */}
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

          {/* KPIs */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
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
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Energy independence</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold">
                  {formatNumber(result.independence_score)} %
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Save-to-home action */}
          {session && (
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={openSaveModal}>
                Save to Home
              </Button>
            </div>
          )}

          {/* Save modal */}
          {showSaveModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
              <Card className="w-full max-w-md">
                <CardHeader>
                  <CardTitle>Save Simulation</CardTitle>
                  <CardDescription>Save this result to one of your homes.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {homes.length === 0 ? (
                    <p className="text-sm text-muted-foreground">
                      You have no homes yet. Create one in the My Homes page first.
                    </p>
                  ) : (
                    <>
                      <div className="space-y-2">
                        <Label>Home</Label>
                        <select
                          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          value={selectedHomeId}
                          onChange={(e) => setSelectedHomeId(e.target.value)}
                        >
                          {homes.map((h) => (
                            <option key={h.home_id} value={h.home_id}>
                              {h.name} — {h.municipality_name || "Unknown"}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label>Simulation name</Label>
                        <Input
                          value={simulationName}
                          onChange={(e) => setSimulationName(e.target.value)}
                          placeholder="e.g., Solar option — January 2026"
                        />
                      </div>
                    </>
                  )}
                  {saveError && (
                    <p className="text-sm text-destructive">{saveError}</p>
                  )}
                  {saveSuccess && (
                    <p className="text-sm text-green-600">Simulation saved successfully!</p>
                  )}
                </CardContent>
                <CardContent className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowSaveModal(false)}>
                    Cancel
                  </Button>
                  {homes.length > 0 && (
                    <Button onClick={handleSaveSimulation} disabled={saving}>
                      {saving ? "Saving..." : "Save"}
                    </Button>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* Climate data */}
          {result.climate && (
            <Card>
              <CardHeader>
                <CardTitle>Climate data</CardTitle>
                <CardDescription>Average conditions for this municipality (NASA POWER)</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-3 lg:grid-cols-4">
                <div>
                  <p className="text-sm text-muted-foreground">Temperature</p>
                  <p className="text-lg font-semibold">{formatNumber(result.climate.avg_t2m, 1)} °C</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Humidity</p>
                  <p className="text-lg font-semibold">{formatNumber(result.climate.avg_rh2m, 1)} %</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Rainfall</p>
                  <p className="text-lg font-semibold">{formatNumber(result.climate.avg_prectotcorr, 1)} mm/day</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Solar irradiance</p>
                  <p className="text-lg font-semibold">{formatNumber(result.climate.avg_allsky_sfc_sw_dwn, 2)} kWh/m²/day</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Wind speed</p>
                  <p className="text-lg font-semibold">{formatNumber(result.climate.avg_ws10m, 2)} m/s</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Cloud coverage</p>
                  <p className="text-lg font-semibold">{formatNumber(result.climate.avg_cloud_amt, 1)} %</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Surface pressure</p>
                  <p className="text-lg font-semibold">{formatNumber(result.climate.avg_surface_pressure, 1)} kPa</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Elevation</p>
                  <p className="text-lg font-semibold">{formatNumber(result.climate.elevation, 0)} m</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Detailed renewable outputs */}
          {result.renewable_energy_results && (
            <div className="grid gap-4 md:grid-cols-3">
              {/* Solar */}
              <Card className="border-t-4 border-t-chart-solar">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="inline-block h-3 w-3 rounded-full bg-chart-solar" />
                    Solar output
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">System size</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.solar_output?.system_kwp, 2)} kWp</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Daily output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.solar_output?.daily_solar_output, 2)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Monthly output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.solar_output?.monthly_solar_output, 1)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Solar score</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.solar_output?.solar_score, 0)} / 100</span>
                  </div>
                </CardContent>
              </Card>

              {/* Wind */}
              <Card className="border-t-4 border-t-chart-wind">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="inline-block h-3 w-3 rounded-full bg-chart-wind" />
                    Wind output
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Swept area</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.wind_output?.swept_area_m2, 1)} m²</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Rated power</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.wind_output?.rated_power_kw, 3)} kW</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Capacity factor</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.wind_output?.capacity_factor, 2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Daily output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.wind_output?.daily_energy_kwh, 2)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Monthly output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.wind_output?.monthly_energy_kwh, 1)} kWh</span>
                  </div>
                </CardContent>
              </Card>

              {/* Hydro */}
              <Card className="border-t-4 border-t-chart-hydro">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="inline-block h-3 w-3 rounded-full bg-chart-hydro" />
                    Hydro output
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">System size</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.hydro_output?.system_kwp, 2)} kWp</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Daily output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.hydro_output?.daily_hydro_output, 1)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Monthly output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.hydro_output?.monthly_hydro_output, 0)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Hydro score</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.hydro_output?.hydro_score, 0)} / 100</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Consumption results */}
          {result.consumption_results && (
            <Card>
              <CardHeader>
                <CardTitle>Consumption breakdown</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-3">
                <div>
                  <p className="text-sm text-muted-foreground">Monthly consumption</p>
                  <p className="text-lg font-semibold">{formatNumber(result.consumption_results.monthly_consumption_kwh, 1)} kWh</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Daily consumption</p>
                  <p className="text-lg font-semibold">{formatNumber(result.consumption_results.daily_consumption_kwh, 2)} kWh</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Target (50% savings)</p>
                  <p className="text-lg font-semibold">{formatNumber(result.consumption_results.target_monthly_consumption_kwh, 1)} kWh</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* AI Analysis */}
          {result.ai_analysis && (
            <Card>
              <CardHeader>
                <CardTitle>AI Analysis</CardTitle>
                <CardDescription>Gemini-powered insights</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4">
                {result.ai_analysis.summary && (
                  <div className="rounded-md border bg-muted/30 p-4 text-sm">
                    <p className="font-medium mb-1">Summary</p>
                    <p className="text-muted-foreground">{result.ai_analysis.summary}</p>
                  </div>
                )}
                {result.ai_analysis.renewable_analysis && (
                  <div className="grid gap-2 md:grid-cols-3">
                    {["solar", "wind", "hydro"].map((key) =>
                      result.ai_analysis.renewable_analysis[key] ? (
                        <div key={key} className="rounded-md border bg-muted/30 p-3 text-sm">
                          <p className="font-medium capitalize mb-1">{key}</p>
                          <p className="text-muted-foreground">{result.ai_analysis.renewable_analysis[key]}</p>
                        </div>
                      ) : null
                    )}
                  </div>
                )}
                {result.ai_analysis.recommendation?.best_option && (
                  <div className="rounded-md border bg-muted/30 p-4 text-sm">
                    <p className="font-medium mb-1">Recommendation</p>
                    <p className="text-muted-foreground">
                      <strong>{result.ai_analysis.recommendation.best_option}</strong>
                      {result.ai_analysis.recommendation.reason && (
                        <span> — {result.ai_analysis.recommendation.reason}</span>
                      )}
                    </p>
                  </div>
                )}
                {result.ai_analysis.environmental_impact && (
                  <div className="rounded-md border bg-muted/30 p-4 text-sm">
                    <p className="font-medium mb-1">Environmental impact</p>
                    <p className="text-muted-foreground">{result.ai_analysis.environmental_impact}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Renewable comparison bars */}
          <Card>
            <CardHeader>
              <CardTitle>Renewable comparison</CardTitle>
              <CardDescription>Monthly generation and savings across options.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              {result.options.map((option) => {
                const barColor =
                  option.source === "Solar"
                    ? "bg-chart-solar"
                    : option.source === "Wind"
                    ? "bg-chart-wind"
                    : "bg-chart-hydro";
                return (
                  <div key={option.source} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{option.source}</span>
                      <span className="text-muted-foreground">
                        {formatNumber(option.estimated_generation_kwh)} kWh/mo
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-muted">
                      <div
                        className={`h-2 rounded-full ${barColor}`}
                        style={{ width: `${(option.estimated_generation_kwh / comparisonMax) * 100}%` }}
                      />
                    </div>
                    <div className="text-xs text-muted-foreground">{option.explanation}</div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* Scenario comparison table */}
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

          {/* Seasonal breakdown */}
          {seasonalMode && (
            <Card>
              <CardHeader>
                <CardTitle>Seasonal Breakdown</CardTitle>
                <CardDescription>
                  Monthly renewable generation across 12 months using latest NASA POWER data.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {seasonalLoading && <p className="text-sm text-muted-foreground">Loading seasonal data...</p>}
                {seasonalError && <p className="text-sm text-destructive">{seasonalError}</p>}
                {seasonalData && !seasonalLoading && (
                  <div className="overflow-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Month</TableHead>
                          <TableHead>Solar (kWh)</TableHead>
                          <TableHead>Wind (kWh)</TableHead>
                          <TableHead>Hydro (kWh)</TableHead>
                          <TableHead>Irradiance</TableHead>
                          <TableHead>Wind Speed</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {seasonalData.map((row) => (
                          <TableRow key={row.month}>
                            <TableCell className="font-medium">
                              {new Date(2024, row.month - 1).toLocaleString("default", { month: "short" })}
                            </TableCell>
                            <TableCell>{formatNumber(row.solar_output_kwh, 1)}</TableCell>
                            <TableCell>{formatNumber(row.wind_output_kwh, 1)}</TableCell>
                            <TableCell>{formatNumber(row.hydro_output_kwh, 1)}</TableCell>
                            <TableCell>{formatNumber(row.solar_irradiance, 2)}</TableCell>
                            <TableCell>{formatNumber(row.wind_speed, 2)} m/s</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </section>
  );
}
