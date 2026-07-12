import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MapPin, Zap, Target, ArrowRight, ArrowLeft, Loader2, Search, Check } from "lucide-react";
import HelpTooltip from "@/components/shared/HelpTooltip";

export default function EcosimWizard({
  mode, setMode,
  muniQuery, setMuniQuery, muniOpen, setMuniOpen, filteredMunicipalities, municipalityId, setMunicipalityId, municipalitiesError,
  provinceQuery, setProvinceQuery, provinceOpen, setProvinceOpen, filteredProvinces, provinceId, setProvinceId, provincesError,
  monthlyConsumption, setMonthlyConsumption, monthlyBill, setMonthlyBill,
  desiredSavings, setDesiredSavings, includeAi, setIncludeAi,
  onRun, loading, activeId, result, user, onSave,
}) {
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const canProceed = useMemo(() => {
    if (step === 1) return activeId !== null && activeId !== "";
    if (step === 2) return monthlyConsumption > 0 && monthlyBill > 0;
    return true;
  }, [step, activeId, monthlyConsumption, monthlyBill]);

  const selectedName = useMemo(() => {
    if (mode === "municipality") {
      const found = filteredMunicipalities.find((m) => String(m.municipality_id) === municipalityId);
      return found ? found.name : muniQuery;
    }
    const found = filteredProvinces.find((p) => String(p.province_id) === provinceId);
    return found ? found.name : provinceQuery;
  }, [mode, municipalityId, provinceId, filteredMunicipalities, filteredProvinces, muniQuery, provinceQuery]);

  const savingsLabel = useMemo(() => {
    const s = desiredSavings || 0;
    if (s <= 10) return "Just exploring";
    if (s <= 30) return "Save a little";
    if (s <= 60) return "Cut my bill in half";
    return "Go almost off-grid";
  }, [desiredSavings]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, i) => {
          const n = i + 1;
          const active = n === step;
          const done = n < step;
          return (
            <div key={n} className="flex items-center gap-2">
              <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-colors ${done ? "bg-emerald-500 text-white" : active ? "bg-sky-500 text-white" : "bg-muted text-muted-foreground"}`}>
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
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <label className="text-sm font-medium">Search mode</label>
                    </div>
                    <div className="flex gap-2">
                      <Button variant={mode === "municipality" ? "default" : "outline"} size="sm" onClick={() => setMode("municipality")}>Municipality</Button>
                      <Button variant={mode === "province" ? "default" : "outline"} size="sm" onClick={() => setMode("province")}>Province</Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">Choose municipality for the most accurate local climate data.</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-1">{mode === "municipality" ? "Search municipality" : "Search province"}</label>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      {mode === "municipality" ? (
                        <Input className="pl-9" placeholder="e.g., Calamba, Santa Rosa" value={muniQuery} onChange={(e) => { setMuniQuery(e.target.value); setMuniOpen(true); }} onFocus={() => setMuniOpen(true)} onBlur={() => setMuniOpen(false)} disabled={loading} autoComplete="off" />
                      ) : (
                        <Input className="pl-9" placeholder="e.g., Laguna, Cavite" value={provinceQuery} onChange={(e) => { setProvinceQuery(e.target.value); setProvinceOpen(true); }} onFocus={() => setProvinceOpen(true)} onBlur={() => setProvinceOpen(false)} disabled={loading} autoComplete="off" />
                      )}
                    </div>
                    {mode === "municipality" && muniOpen && (
                      <div className="mt-1 max-h-48 overflow-y-auto rounded-lg border bg-card shadow-sm z-10 relative">
                        {filteredMunicipalities.length ? filteredMunicipalities.map((item) => (
                          <button key={item.municipality_id} className={"w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors " + (String(item.municipality_id) === municipalityId ? "bg-accent font-medium" : "")} onMouseDown={(e) => e.preventDefault()} onClick={() => { setMunicipalityId(String(item.municipality_id)); setMuniQuery(item.name); setMuniOpen(false); }}>
                            {item.name}
                          </button>
                        )) : <div className="px-3 py-2 text-sm text-muted-foreground">No results found</div>}
                      </div>
                    )}
                    {mode === "province" && provinceOpen && (
                      <div className="mt-1 max-h-48 overflow-y-auto rounded-lg border bg-card shadow-sm z-10 relative">
                        {filteredProvinces.length ? filteredProvinces.map((item) => (
                          <button key={item.province_id} className={"w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors " + (String(item.province_id) === provinceId ? "bg-accent font-medium" : "")} onMouseDown={(e) => e.preventDefault()} onClick={() => { setProvinceId(String(item.province_id)); setProvinceQuery(item.name); setProvinceOpen(false); }}>
                            {item.name}
                          </button>
                        )) : <div className="px-3 py-2 text-sm text-muted-foreground">No results found</div>}
                      </div>
                    )}
                    {mode === "municipality" && municipalitiesError && <p className="text-xs text-destructive mt-1">{municipalitiesError}</p>}
                    {mode === "province" && provincesError && <p className="text-xs text-destructive mt-1">{provincesError}</p>}
                    {activeId && (
                      <div className="mt-2 rounded-lg border bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
                        Selected: <span className="font-medium">{selectedName}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="text-sm font-medium block mb-1"><HelpTooltip term="kWh">Monthly consumption (kWh)</HelpTooltip></label>
                      <Input type="number" placeholder="e.g. 300" value={monthlyConsumption || ""} onChange={(e) => setMonthlyConsumption(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">Find this on your electric bill. It is usually the biggest number in the Usage section.</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium block mb-1">Monthly bill (PHP)</label>
                      <Input type="number" placeholder="e.g. 5000" value={monthlyBill || ""} onChange={(e) => setMonthlyBill(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">The total amount you pay each month, before any subsidies or discounts.</p>
                    </div>
                  </div>
                  {monthlyConsumption > 0 && monthlyBill > 0 && (
                    <div className="rounded-lg border bg-muted/30 p-3 text-sm">
                      <p className="text-muted-foreground">Your effective rate is about <span className="font-medium text-foreground">PHP {(monthlyBill / monthlyConsumption).toFixed(2)}</span> per kWh. This helps us estimate your savings accurately.</p>
                    </div>
                  )}
                </div>
              )}

              {step === 3 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium">Desired savings</label>
                      <span className="text-sm font-bold text-sky-600">{desiredSavings}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="5"
                      value={desiredSavings}
                      onChange={(e) => setDesiredSavings(Number(e.target.value))}
                      className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-sky-500"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>Just exploring</span>
                      <span className="font-medium text-foreground">{savingsLabel}</span>
                      <span>Go off-grid</span>
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <input
                        type="checkbox"
                        checked={includeAi}
                        onChange={(e) => setIncludeAi(e.target.checked)}
                        className="h-4 w-4 rounded border-gray-300 text-primary accent-primary"
                      />
                      <label className="text-sm font-medium">Include AI analysis</label>
                    </div>
                    <p className="text-xs text-muted-foreground">Adds a detailed plain-English explanation of why this renewable source is recommended for your area, along with next steps.</p>
                  </div>
                </div>
              )}

              {step === 4 && (
                <div className="space-y-4">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-lg border bg-muted/30 p-3"><p className="text-xs text-muted-foreground">Location</p><p className="text-sm font-medium">{selectedName || "Not selected"}</p></div>
                    <div className="rounded-lg border bg-muted/30 p-3"><p className="text-xs text-muted-foreground">Monthly consumption</p><p className="text-sm font-medium">{monthlyConsumption || 0} kWh</p></div>
                    <div className="rounded-lg border bg-muted/30 p-3"><p className="text-xs text-muted-foreground">Monthly bill</p><p className="text-sm font-medium">PHP {monthlyBill?.toLocaleString() || 0}</p></div>
                    <div className="rounded-lg border bg-muted/30 p-3"><p className="text-xs text-muted-foreground">Desired savings</p><p className="text-sm font-medium">{desiredSavings}% — {savingsLabel}</p></div>
                  </div>
                  <p className="text-sm text-muted-foreground">We will compare solar, wind, hydro, and geothermal for your location and recommend the best match.</p>
                </div>
              )}

              <div className="flex items-center justify-between pt-2">
                {step > 1 ? <Button variant="outline" onClick={() => setStep(step - 1)} disabled={loading}><ArrowLeft className="h-4 w-4 mr-1" /> Back</Button> : <div />}
                {step < totalSteps ? (
                  <Button onClick={() => setStep(step + 1)} disabled={!canProceed || loading}>Next <ArrowRight className="h-4 w-4 ml-1" /></Button>
                ) : (
                  <div className="flex gap-2">
                    {result && user && <Button variant="outline" onClick={onSave} disabled={loading}>Save</Button>}
                    <Button onClick={(e) => { e.preventDefault(); onRun(e); }} disabled={loading || !activeId}>
                      {loading ? <><Loader2 className="h-4 w-4 mr-1 animate-spin" /> Running...</> : <>Run simulation <ArrowRight className="h-4 w-4 ml-1" /></>}
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="hidden md:block">
          <Card className="bg-muted/30">
            <CardHeader><CardTitle className="text-sm">Your Inputs</CardTitle></CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div><p className="text-xs text-muted-foreground">Location</p><p className="font-medium">{selectedName || "—"}</p></div>
              <div><p className="text-xs text-muted-foreground">Consumption</p><p className="font-medium">{monthlyConsumption || 0} kWh</p></div>
              <div><p className="text-xs text-muted-foreground">Bill</p><p className="font-medium">PHP {monthlyBill?.toLocaleString() || 0}</p></div>
              <div><p className="text-xs text-muted-foreground">Savings goal</p><p className="font-medium">{desiredSavings}%</p></div>
              <div><p className="text-xs text-muted-foreground">AI analysis</p><p className="font-medium">{includeAi ? "Yes" : "No"}</p></div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
