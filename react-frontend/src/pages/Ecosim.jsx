import { useEffect, useMemo, useRef, useState } from "react";
import { getApiBaseUrl } from "@/utils/env";
import { useSearchParams } from "react-router-dom";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";
import { getEcosim, getMunicipalities } from "@/services/apiClient";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";
import { supabase } from "@/services/supabaseClient";

const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0);

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0
  }).format(value ?? 0);

export default function Ecosim() {
  const { user, accessToken, plan, isFree, isPro, isPremium } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const [municipalityId, setMunicipalityId] = useState("");
  const [municipalities, setMunicipalities] = useState([]);
  const [municipalitiesLoading, setMunicipalitiesLoading] = useState(true);
  const [municipalitiesError, setMunicipalitiesError] = useState(null);
  const [muniQuery, setMuniQuery] = useState("");
  const [muniOpen, setMuniOpen] = useState(false);
  const muniRef = useRef(null);
  const [monthlyConsumption, setMonthlyConsumption] = useState(350);
  const [monthlyBill, setMonthlyBill] = useState(5000);
  const [desiredSavings, setDesiredSavings] = useState(50);
  const [includeAi, setIncludeAi] = useState(true);
  const [aiInsightInfo, setAiInsightInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Save simulation dialog state
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [saveLabel, setSaveLabel] = useState("");
  const [saving, setSaving] = useState(false);

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
      setMunicipalitiesLoading(true);
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
      } finally {
        if (isActive) setMunicipalitiesLoading(false);
      }
    };

    loadMunicipalities();
    return () => {
      isActive = false;
    };
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (muniRef.current && !muniRef.current.contains(event.target)) {
        setMuniOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Load saved simulation from query param ?simulation_id={id}
  useEffect(() => {
    const simId = searchParams.get("simulation_id");
    if (!simId || !user?.id) return;

    let isActive = true;
    const loadSaved = async () => {
      try {
        const { data: sim, error } = await supabase
          .from("saved_simulations")
          .select("*")
          .eq("id", simId)
          .eq("user_id", user.id)
          .single();

        if (error || !sim) throw new Error(error?.message || "Simulation not found");
        if (!isActive) return;

        // Pre-populate inputs
        const inputs = sim.inputs || {};
        if (inputs.monthly_consumption_kwh) {
          setMonthlyConsumption(inputs.monthly_consumption_kwh);
        }
        if (inputs.monthly_bill_php) {
          setMonthlyBill(inputs.monthly_bill_php);
        }
        if (inputs.desired_savings_pct !== undefined) {
          setDesiredSavings(inputs.desired_savings_pct);
        }
        if (inputs.include_ai !== undefined) {
          setIncludeAi(inputs.include_ai);
        }
        if (sim.municipality_id) {
          setMunicipalityId(String(sim.municipality_id));
          const found = municipalities.find(
            (m) => String(m.municipality_id) === String(sim.municipality_id)
          );
          if (found) setMuniQuery(found.name);
        }
        // Pre-populate results
        if (sim.results) {
          setResult(sim.results);
        }
        toast.success("Loaded saved simulation");
      } catch (err) {
        toast.error(err?.message || "Failed to load saved simulation");
      }
    };

    loadSaved();
    return () => {
      isActive = false;
    };
  }, [searchParams, user, municipalities]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    setAiInsightInfo(null);

    try {
      const data = await getEcosim({
        municipalityId: String(municipalityId).trim(),
        monthlyConsumption: Number(monthlyConsumption),
        monthlyBill: Number(monthlyBill),
        desiredSavings: Number(desiredSavings) / 100,
        includeAi,
      });
      setResult(data);
      setAiInsightInfo(data?.ai_insight_info || null);
    } catch (err) {
      setError(err?.message || "Unable to load Ecosim data.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSimulation = async () => {
    if (!user || !accessToken) {
      toast.error("Please log in to save simulations");
      return;
    }
    if (!result || !municipalityId) {
      toast.error("Run a simulation first");
      return;
    }

    const defaultLabel = `${result.municipality || "Simulation"} — ${result.recommended_source || "Renewable"}`;
    const label = saveLabel.trim() || defaultLabel;

    setSaving(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/simulations`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            label,
            municipality_id: Number(municipalityId),
            inputs: {
              monthly_consumption_kwh: Number(monthlyConsumption),
              monthly_bill_php: Number(monthlyBill),
              desired_savings_pct: Number(desiredSavings),
              include_ai: includeAi,
            },
            results: result,
          }),
        }
      );

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        if (res.status === 403 && errData.detail?.upgrade) {
          toast.error(`Save limit reached (${errData.detail.limit}). Upgrade to save more.`);
        } else {
          toast.error(errData.detail?.message || "Failed to save simulation");
        }
        return;
      }

      toast.success("Simulation saved successfully");
      setSaveDialogOpen(false);
      setSaveLabel("");
    } catch (err) {
      toast.error(err?.message || "Failed to save simulation");
    } finally {
      setSaving(false);
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
          <form className="grid gap-4 md:grid-cols-3 lg:grid-cols-6" onSubmit={handleSubmit}>
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
            <div ref={muniRef} className="relative space-y-2">
              <label className="text-sm font-medium">Municipality</label>
              <Input
                type="text"
                placeholder={municipalitiesLoading ? "Loading municipalities..." : "Search municipality..."}
                value={muniQuery}
                onChange={(e) => {
                  setMuniQuery(e.target.value);
                  setMuniOpen(true);
                }}
                onFocus={() => setMuniOpen(true)}
                disabled={loading || municipalitiesLoading}
                autoComplete="off"
              />
              {muniOpen && (
                <div className="absolute z-50 mt-1 max-h-56 w-full min-w-[240px] overflow-auto rounded-md border border-input bg-popover text-popover-foreground shadow-md">
                  {municipalitiesLoading ? (
                    <div className="px-3 py-2.5 text-sm text-muted-foreground">
                      Loading...
                    </div>
                  ) : filteredMunicipalities.length ? (
                    filteredMunicipalities.map((item) => (
                      <button
                        key={item.municipality_id}
                        type="button"
                        className={
                          "w-full px-3 py-2.5 text-left text-sm text-popover-foreground transition-colors hover:bg-accent hover:text-accent-foreground " +
                          (String(item.municipality_id) === municipalityId
                            ? "bg-accent font-medium text-accent-foreground"
                            : "")
                        }
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
                    <div className="px-3 py-2.5 text-sm text-muted-foreground">
                      {municipalitiesError ? "Failed to load" : "No results found"}
                    </div>
                  )}
                </div>
              )}
              {municipalitiesError && (
                <p className="text-xs text-destructive">{municipalitiesError}</p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Desired savings (%)</label>
              <Input
                type="number"
                min="0"
                max="100"
                value={desiredSavings}
                onChange={(event) => setDesiredSavings(Number(event.target.value))}
              />
            </div>
            <div className="flex items-end space-x-2">
              <label className="flex items-center space-x-2 text-sm">
                <input
                  type="checkbox"
                  checked={includeAi}
                  onChange={(e) => setIncludeAi(e.target.checked)}
                  disabled={
                    loading ||
                    (aiInsightInfo?.ai_insight_remaining !== null &&
                      aiInsightInfo?.ai_insight_remaining <= 0)
                  }
                  className="h-4 w-4 rounded border-brand-light text-primary accent-primary focus:ring-primary disabled:opacity-50"
                />
                <span>
                  Include AI analysis
                  {plan && (
                    <span className="ml-1 text-xs text-muted-foreground">
                      ({aiInsightInfo?.ai_insight_remaining ?? (isFree ? 1 : isPro ? 5 : 20)} /{" "}
                      {isFree ? 1 : isPro ? 5 : 20} left)
                    </span>
                  )}
                </span>
              </label>
            </div>
            {aiInsightInfo?.message && (
              <div className="col-span-full text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1">
                {aiInsightInfo.message}{" "}
                <a href="/pricing" className="underline font-semibold">Upgrade</a>
              </div>
            )}
            <div className="flex items-end">
              <Button type="submit" disabled={loading || !municipalityId} className="w-full">
                {loading ? "Running simulation..." : "Run simulation"}
              </Button>
            </div>
            {result && user && (
              <div className="flex items-end">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    const defaultLabel = `${result.municipality || "Simulation"} — ${result.recommended_source || "Renewable"}`;
                    setSaveLabel(defaultLabel);
                    setSaveDialogOpen(true);
                  }}
                >
                  Save Simulation
                </Button>
              </div>
            )}
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
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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
                    <span className="text-muted-foreground">Daily output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.solar_output?.daily_solar_output, 2)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Monthly output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.solar_output?.monthly_solar_output, 1)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Annual output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.solar_output?.annual_solar_output, 0)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Suitability score</span>
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
                    <span className="text-muted-foreground">Daily output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.wind_output?.daily_energy_kwh, 2)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Monthly output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.wind_output?.monthly_energy_kwh, 1)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Annual output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.wind_output?.annual_wind_output_kwh, 0)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Suitability score</span>
                    <span className="font-medium">{formatNumber((result.renewable_energy_results.wind_output?.capacity_factor || 0) * 100, 0)} / 100</span>
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
                    <span className="text-muted-foreground">Daily output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.hydro_output?.daily_hydro_output, 1)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Monthly output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.hydro_output?.monthly_hydro_output, 0)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Annual output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.hydro_output?.annual_hydro_output, 0)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Suitability score</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.hydro_output?.hydro_score, 0)} / 100</span>
                  </div>
                </CardContent>
              </Card>

              {/* Geothermal */}
              <Card className="border-t-4 border-t-chart-geothermal">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="inline-block h-3 w-3 rounded-full bg-chart-geothermal" />
                    Geothermal output
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Daily output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.geothermal_output?.daily_energy_kwh, 1)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Monthly output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.geothermal_output?.monthly_energy_kwh, 1)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Annual output</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.geothermal_output?.annual_energy_kwh, 0)} kWh</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Suitability score</span>
                    <span className="font-medium">{formatNumber(result.renewable_energy_results.geothermal_output?.suitability_score, 1)} / 100</span>
                  </div>
                  {result.nearby_geothermal_plants && result.nearby_geothermal_plants.length > 0 && (
                    <div className="mt-2 rounded-md bg-orange-50 p-2 text-xs text-orange-800">
                      <span className="font-semibold">Nearby plant(s): </span>
                      {result.nearby_geothermal_plants.slice(0, 3).map((p, i) => (
                        <span key={i}>
                          {i > 0 && ", "}
                          {p.project_name} ({p.capacity_mw} MW, {p.distance_km} km)
                        </span>
                      ))}
                    </div>
                  )}
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
                  <p className="text-sm text-muted-foreground">Target ({desiredSavings}% savings)</p>
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
                <CardDescription>Prescriptive renewable energy insights</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4">
                {/* Prescriptive Recommendation (new structure) */}
                {result.ai_analysis.prescriptive_recommendation && (
                  <div className="grid gap-3">
                    {result.ai_analysis.prescriptive_recommendation.observation && (
                      <div className="rounded-md border bg-muted/30 p-4 text-sm">
                        <p className="font-semibold text-emerald-700 mb-1">Observation</p>
                        <p className="text-muted-foreground whitespace-pre-line">
                          {result.ai_analysis.prescriptive_recommendation.observation}
                        </p>
                      </div>
                    )}
                    {result.ai_analysis.prescriptive_recommendation.interpretation && (
                      <div className="rounded-md border bg-muted/30 p-4 text-sm">
                        <p className="font-semibold text-emerald-700 mb-2">Interpretation</p>
                        <div className="text-muted-foreground whitespace-pre-line space-y-2">
                          {result.ai_analysis.prescriptive_recommendation.interpretation
                            .split(/\n\s*-\s+|\n\s*\*\s+/)
                            .filter(Boolean)
                            .map((chunk, i) => {
                              const trimmed = chunk.trim();
                              const match = trimmed.match(/^\*\*(.+?)\*\*[:\s]*(.+)$/s);
                              if (match) {
                                const [, label, body] = match;
                                const colorMap = {
                                  Solar: "text-amber-600",
                                  Wind: "text-sky-600",
                                  Hydro: "text-cyan-600",
                                  Geothermal: "text-rose-600",
                                };
                                return (
                                  <div key={i} className="flex gap-2">
                                    <span className={`font-semibold shrink-0 ${colorMap[label] || "text-emerald-700"}`}>
                                      {label}:
                                    </span>
                                    <span>{body.trim()}</span>
                                  </div>
                                );
                              }
                              return <p key={i}>{trimmed}</p>;
                            })}
                        </div>
                      </div>
                    )}
                    {result.ai_analysis.prescriptive_recommendation.recommendation && (
                      <div className="rounded-md border bg-emerald-50 p-4 text-sm">
                        <p className="font-semibold text-emerald-800 mb-2">Recommendation</p>
                        <div className="text-emerald-900 space-y-1.5">
                          {result.ai_analysis.prescriptive_recommendation.recommendation
                            .split(/\n\s*-\s+/)
                            .filter(Boolean)
                            .map((chunk, i) => {
                              const trimmed = chunk.trim();
                              if (i === 0 && !trimmed.startsWith("•") && !trimmed.startsWith("-")) {
                                return <p key={i} className="font-medium">{trimmed}</p>;
                              }
                              return (
                                <div key={i} className="flex gap-2 items-start">
                                  <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
                                  <span>{trimmed}</span>
                                </div>
                              );
                            })}
                        </div>
                      </div>
                    )}
                    {result.ai_analysis.prescriptive_recommendation.reason && (
                      <div className="rounded-md border bg-muted/30 p-4 text-sm">
                        <p className="font-semibold text-emerald-700 mb-1">Reason</p>
                        <p className="text-muted-foreground whitespace-pre-line">
                          {result.ai_analysis.prescriptive_recommendation.reason}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Fallback: legacy summary display */}
                {!result.ai_analysis.prescriptive_recommendation?.recommendation && result.ai_analysis.summary && (
                  <div className="rounded-md border bg-muted/30 p-4 text-sm">
                    <p className="font-medium mb-1">Summary</p>
                    <p className="text-muted-foreground whitespace-pre-line">{result.ai_analysis.summary}</p>
                  </div>
                )}

                {/* Fallback: legacy per-type analysis */}
                {!result.ai_analysis.prescriptive_recommendation?.recommendation && result.ai_analysis.renewable_analysis && (
                  <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-4">
                    {["solar", "wind", "hydro", "geothermal"].map((key) =>
                      result.ai_analysis.renewable_analysis[key] ? (
                        <div key={key} className="rounded-md border bg-muted/30 p-3 text-sm">
                          <p className="font-medium capitalize mb-1">{key}</p>
                          <p className="text-muted-foreground">{result.ai_analysis.renewable_analysis[key]}</p>
                        </div>
                      ) : null
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Renewable comparison bars */}
          <Card>
            <CardHeader>
              <CardTitle>Renewable comparison</CardTitle>
              <CardDescription>Monthly generation, cost, and payback across options.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              {result.options.map((option) => {
                const barColor =
                  option.source === "Solar"
                    ? "bg-chart-solar"
                    : option.source === "Wind"
                    ? "bg-chart-wind"
                    : option.source === "Geothermal"
                    ? "bg-chart-geothermal"
                    : "bg-chart-hydro";
                const isUtility = option.scale === "utility";
                return (
                  <div key={option.source} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{option.source}</span>
                        {isUtility && (
                          <span className="rounded bg-orange-100 px-1.5 py-0.5 text-[10px] font-semibold text-orange-700">
                            Municipal plant
                          </span>
                        )}
                      </div>
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
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                      <span>{option.explanation}</span>
                      {!isUtility && (
                        <>
                          <span className="hidden sm:inline">·</span>
                          <span>Install: {formatCurrency(option.installation_cost)}</span>
                          <span className="hidden sm:inline">·</span>
                          <span>Savings: {formatCurrency(option.monthly_savings)}/mo</span>
                          {option.payback_years !== null && option.payback_years !== undefined && (
                            <>
                              <span className="hidden sm:inline">·</span>
                              <span>Payback: {option.payback_years.toFixed(1)} yrs</span>
                            </>
                          )}
                        </>
                      )}
                      {isUtility && (
                        <span className="italic text-orange-600">Utility-scale — not a household install</span>
                      )}
                    </div>
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
        </div>
      )}

      {/* Save Simulation Dialog */}
      <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save Simulation</DialogTitle>
            <DialogDescription>
              Give your simulation a name so you can revisit it later.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <label className="text-sm font-medium">Simulation name</label>
            <Input
              value={saveLabel}
              onChange={(e) => setSaveLabel(e.target.value)}
              placeholder="e.g., Calamba Solar Feasibility"
              className="mt-2"
              autoFocus
            />
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">
                Cancel
              </Button>
            </DialogClose>
            <Button
              type="button"
              onClick={handleSaveSimulation}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}
