import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { MapPin, Zap, Target, ArrowRight, ArrowLeft, Loader2, Search, Check } from "lucide-react";
import HelpTooltip from "@/components/shared/HelpTooltip";

export default function EcosimInputForm({
  mode,
  setMode,
  searchQuery,
  setSearchQuery,
  searchResults,
  searching,
  selectedId,
  handleSelect,
  monthlyConsumption,
  setMonthlyConsumption,
  monthlyBill,
  setMonthlyBill,
  desiredSavings,
  setDesiredSavings,
  includeAi,
  setIncludeAi,
  onRun,
  loading,
  onSave,
}) {
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const canProceed = useMemo(() => {
    if (step === 1) return selectedId !== null;
    if (step === 2) return monthlyConsumption > 0 && monthlyBill > 0;
    return true;
  }, [step, selectedId, monthlyConsumption, monthlyBill]);

  const selectedName = useMemo(() => {
    if (!selectedId) return "";
    const found = searchResults.find((r) => r.id === selectedId);
    return found ? `${found.name}, ${found.province || ""}` : "";
  }, [selectedId, searchResults]);

  const savingsLabel = useMemo(() => {
    const s = desiredSavings || 0;
    if (s <= 10) return "Just exploring";
    if (s <= 30) return "Save a little";
    if (s <= 60) return "Cut my bill in half";
    return "Go almost off-grid";
  }, [desiredSavings]);

  return (
    <div className="space-y-4">
      {/* Step indicator */}
      <div className="flex items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, i) => {
          const n = i + 1;
          const active = n === step;
          const done = n < step;
          return (
            <div key={n} className="flex items-center gap-2">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-colors ${
                  done
                    ? "bg-emerald-500 text-white"
                    : active
                    ? "bg-sky-500 text-white"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {done ? <Check className="h-4 w-4" /> : n}
              </div>
              {n < totalSteps && <div className={`h-0.5 w-6 ${done ? "bg-emerald-500" : "bg-muted"}`} />}
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {step === 1 && <MapPin className="h-5 w-5 text-sky-500" />}
                {step === 2 && <Zap className="h-5 w-5 text-amber-500" />}
                {step === 3 && <Target className="h-5 w-5 text-emerald-500" />}
                {step === 4 && <ArrowRight className="h-5 w-5 text-rose-500" />}
                Step {step} of {totalSteps}
              </CardTitle>
              <CardDescription>
                {step === 1 && "Select your city or municipality so we can analyze your local climate and resources."}
                {step === 2 && "Tell us how much electricity you use each month so we can estimate your savings."}
                {step === 3 && "How much of your bill would you like to eliminate with renewable energy?"}
                {step === 4 && "Review your inputs and run the analysis."}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Step 1: Location */}
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <label className="text-sm font-medium">Search mode</label>
                      <HelpTooltip term="municipality">
                        <span className="text-sm font-medium">Municipality</span>
                      </HelpTooltip>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant={mode === "municipality" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setMode("municipality")}
                      >
                        Municipality
                      </Button>
                      <Button
                        variant={mode === "province" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setMode("province")}
                      >
                        Province
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Choose municipality for the most accurate local climate data.
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium block mb-1">
                      {mode === "municipality" ? "Search municipality" : "Search province"}
                    </label>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        className="pl-9"
                        placeholder={mode === "municipality" ? "e.g., Calamba, Santa Rosa" : "e.g., Laguna, Cavite"}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                    {searching && <p className="text-xs text-muted-foreground mt-1">Searching...</p>}
                    {searchResults.length > 0 && !selectedId && (
                      <div className="mt-2 max-h-48 overflow-y-auto rounded-lg border bg-card shadow-sm">
                        {searchResults.map((item) => (
                          <button
                            key={item.id}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors"
                            onClick={() => handleSelect(item.id)}
                          >
                            <span className="font-medium">{item.name}</span>
                            {item.province && <span className="text-muted-foreground">, {item.province}</span>}
                          </button>
                        ))}
                      </div>
                    )}
                    {selectedId && (
                      <div className="mt-2 rounded-lg border bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
                        Selected: <span className="font-medium">{selectedName}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Step 2: Energy Use */}
              {step === 2 && (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="text-sm font-medium block mb-1">
                        <HelpTooltip term="kWh">Monthly consumption (kWh)</HelpTooltip>
                      </label>
                      <Input
                        type="number"
                        placeholder="e.g. 300"
                        value={monthlyConsumption || ""}
                        onChange={(e) => setMonthlyConsumption(Number(e.target.value))}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Find this on your electric bill. It's usually the biggest number in the "Usage" section.
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium block mb-1">Monthly bill (PHP)</label>
                      <Input
                        type="number"
                        placeholder="e.g. 5000"
                        value={monthlyBill || ""}
                        onChange={(e) => setMonthlyBill(Number(e.target.value))}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        The total amount you pay each month, before any subsidies or discounts.
                      </p>
                    </div>
                  </div>
                  {monthlyConsumption > 0 && monthlyBill > 0 && (
                    <div className="rounded-lg border bg-muted/30 p-3 text-sm">
                      <p className="text-muted-foreground">
                        Your effective rate is about{" "}
                        <span className="font-medium text-foreground">
                          PHP {(monthlyBill / monthlyConsumption).toFixed(2)}
                        </span>{" "}
                        per kWh. This helps us estimate your savings accurately.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Step 3: Goal */}
              {step === 3 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium">Desired savings</label>
                      <span className="text-sm font-bold text-sky-600">{desiredSavings}%</span>
                    </div>
                    <Slider
                      value={[desiredSavings]}
                      onValueChange={(v) => setDesiredSavings(v[0])}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>Just exploring</span>
                      <span className="font-medium text-foreground">{savingsLabel}</span>
                      <span>Go off-grid</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Switch checked={includeAi} onCheckedChange={setIncludeAi} />
                      <label className="text-sm font-medium">Include AI analysis</label>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Adds a detailed plain-English explanation of why this renewable source is recommended for your area, along with next steps.
                    </p>
                  </div>
                </div>
              )}

              {/* Step 4: Review & Run */}
              {step === 4 && (
                <div className="space-y-4">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">Location</p>
                      <p className="text-sm font-medium">{selectedName || "Not selected"}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">Monthly consumption</p>
                      <p className="text-sm font-medium">{monthlyConsumption || 0} kWh</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">Monthly bill</p>
                      <p className="text-sm font-medium">PHP {monthlyBill?.toLocaleString() || 0}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">Desired savings</p>
                      <p className="text-sm font-medium">{desiredSavings}% — {savingsLabel}</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    We'll compare solar, wind, hydro, and geothermal for your location and recommend the best match.
                  </p>
                </div>
              )}

              {/* Navigation buttons */}
              <div className="flex items-center justify-between pt-2">
                {step > 1 ? (
                  <Button variant="outline" onClick={() => setStep(step - 1)} disabled={loading}>
                    <ArrowLeft className="h-4 w-4 mr-1" /> Back
                  </Button>
                ) : (
                  <div />
                )}
                {step < totalSteps ? (
                  <Button onClick={() => setStep(step + 1)} disabled={!canProceed || loading}>
                    Next <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={onSave} disabled={loading}>
                      Save
                    </Button>
                    <Button onClick={onRun} disabled={loading}>
                      {loading ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-1 animate-spin" /> Running...
                        </>
                      ) : (
                        <>
                          Run simulation <ArrowRight className="h-4 w-4 ml-1" />
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar summary */}
        <div className="hidden md:block">
          <Card className="bg-muted/30">
            <CardHeader>
              <CardTitle className="text-sm">Your Inputs</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <p className="text-xs text-muted-foreground">Location</p>
                <p className="font-medium">{selectedName || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Consumption</p>
                <p className="font-medium">{monthlyConsumption || 0} kWh</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Bill</p>
                <p className="font-medium">PHP {monthlyBill?.toLocaleString() || 0}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Savings goal</p>
                <p className="font-medium">{desiredSavings}%</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">AI analysis</p>
                <p className="font-medium">{includeAi ? "Yes" : "No"}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
