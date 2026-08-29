import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MapPin, Zap, Target, ArrowRight, ArrowLeft, Loader2, Search, Check } from "lucide-react";
import HelpTooltip from "@/components/shared/HelpTooltip";
import BillHelpModal from "@/components/shared/BillHelpModal";
import { useI18n } from "@/i18n";

export default function EcosimWizard({
  mode, setMode,
  muniQuery, setMuniQuery, muniOpen, setMuniOpen, filteredMunicipalities, municipalityId, setMunicipalityId, municipalitiesError,
  provinceQuery, setProvinceQuery, provinceOpen, setProvinceOpen, filteredProvinces, provinceId, setProvinceId, provincesError,
  monthlyConsumption, setMonthlyConsumption, monthlyBill, setMonthlyBill, electricityRate, setElectricityRate,
  desiredSavings, setDesiredSavings, includeAi, setIncludeAi,
  onRun, loading, activeId, result, user, onSave,
}) {
  const { t } = useI18n();
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const canProceed = useMemo(() => {
    if (step === 1) return activeId !== null && activeId !== "";
    if (step === 2) return monthlyConsumption > 0 && monthlyBill > 0 && electricityRate > 0;
    return true;
  }, [step, activeId, monthlyConsumption, monthlyBill, electricityRate]);

  const selectedName = useMemo(() => {
    if (mode === "municipality") {
      const found = filteredMunicipalities.find((m) => String(m.municipality_id) === municipalityId);
      if (!found) return muniQuery;
      return found.province_name ? `${found.name}, ${found.province_name}` : found.name;
    }
    const found = filteredProvinces.find((p) => String(p.province_id) === provinceId);
    return found ? found.name : provinceQuery;
  }, [mode, municipalityId, provinceId, filteredMunicipalities, filteredProvinces, muniQuery, provinceQuery]);

  const savingsLabel = useMemo(() => {
    const s = desiredSavings || 0;
    if (s <= 25) return t("ecosim.wizard.savingsLevels.exploring");
    if (s <= 50) return t("ecosim.wizard.savingsLevels.little");
    if (s <= 75) return t("ecosim.wizard.savingsLevels.half");
    return t("ecosim.wizard.savingsLevels.offGrid");
  }, [desiredSavings, t]);

  const computedRate = useMemo(() => {
    if (monthlyConsumption > 0 && monthlyBill > 0) {
      return monthlyBill / monthlyConsumption;
    }
    return 0;
  }, [monthlyConsumption, monthlyBill]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, i) => {
          const n = i + 1;
          const active = n === step;
          const done = n < step;
          return (
            <div key={n} className="flex items-center gap-2">
              <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-colors ${done ? "bg-primary text-primary-foreground" : active ? "bg-sky-500 text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                {done ? <Check className="h-4 w-4" /> : n}
              </div>
              {n < totalSteps && <div className={`h-0.5 w-6 ${done ? "bg-primary" : "bg-muted"}`} />}
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
                {step === 2 && <Zap className="h-5 w-5 text-warning" />}
                {step === 3 && <Target className="h-5 w-5 text-primary" />}
                {step === 4 && <ArrowRight className="h-5 w-5 text-destructive" />}
                {t("ecosim.wizard.step", { current: step, total: totalSteps })}
              </CardTitle>
              <CardDescription>
                {t(`ecosim.wizard.stepDescriptions.step${step}`)}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <label className="text-sm font-medium">{t("ecosim.wizard.searchMode")}</label>
                    </div>
                    <div className="flex gap-2">
                      <Button variant={mode === "municipality" ? "default" : "outline"} size="sm" onClick={() => setMode("municipality")}>{t("ecosim.wizard.municipality")}</Button>
                      <Button variant={mode === "province" ? "default" : "outline"} size="sm" onClick={() => setMode("province")}>{t("ecosim.wizard.province")}</Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.municipalityHint")}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-1">{mode === "municipality" ? t("ecosim.wizard.searchMunicipality") : t("ecosim.wizard.searchProvince")}</label>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      {mode === "municipality" ? (
                        <Input className="pl-9" placeholder={t("ecosim.wizard.placeholderMunicipality")} value={muniQuery} onChange={(e) => { setMuniQuery(e.target.value); setMuniOpen(true); }} onFocus={() => setMuniOpen(true)} onBlur={() => setMuniOpen(false)} disabled={loading} autoComplete="off" />
                      ) : (
                        <Input className="pl-9" placeholder={t("ecosim.wizard.placeholderProvince")} value={provinceQuery} onChange={(e) => { setProvinceQuery(e.target.value); setProvinceOpen(true); }} onFocus={() => setProvinceOpen(true)} onBlur={() => setProvinceOpen(false)} disabled={loading} autoComplete="off" />
                      )}
                    </div>
                    {mode === "municipality" && muniOpen && (
                      <div className="mt-1 max-h-64 overflow-y-auto rounded-lg border bg-card shadow-sm z-10 relative">
                        {filteredMunicipalities.length ? (
                          <>
                            {filteredMunicipalities.slice(0, 50).map((item) => (
                              <button key={item.municipality_id} className={"w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors " + (String(item.municipality_id) === municipalityId ? "bg-accent font-medium" : "")} onMouseDown={(e) => e.preventDefault()} onClick={() => { setMunicipalityId(String(item.municipality_id)); setMuniQuery(item.province_name ? `${item.name}, ${item.province_name}` : item.name); setMuniOpen(false); }}>
                                {item.province_name ? `${item.name}, ${item.province_name}` : item.name}
                              </button>
                            ))}
                            {filteredMunicipalities.length > 50 && (
                              <div className="px-3 py-2 text-xs text-muted-foreground border-t">
                                {t("ecosim.wizard.moreResults", { count: filteredMunicipalities.length - 50, total: filteredMunicipalities.length })}
                              </div>
                            )}
                          </>
                        ) : <div className="px-3 py-2 text-sm text-muted-foreground">{t("ecosim.wizard.noResults")}</div>}
                      </div>
                    )}
                    {mode === "province" && provinceOpen && (
                      <div className="mt-1 max-h-64 overflow-y-auto rounded-lg border bg-card shadow-sm z-10 relative">
                        {filteredProvinces.length ? (
                          <>
                            {filteredProvinces.slice(0, 50).map((item) => (
                              <button key={item.province_id} className={"w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors " + (String(item.province_id) === provinceId ? "bg-accent font-medium" : "")} onMouseDown={(e) => e.preventDefault()} onClick={() => { setProvinceId(String(item.province_id)); setProvinceQuery(item.name); setProvinceOpen(false); }}>
                                {item.name}
                              </button>
                            ))}
                            {filteredProvinces.length > 50 && (
                              <div className="px-3 py-2 text-xs text-muted-foreground border-t">
                                {t("ecosim.wizard.moreResults", { count: filteredProvinces.length - 50, total: filteredProvinces.length })}
                              </div>
                            )}
                          </>
                        ) : <div className="px-3 py-2 text-sm text-muted-foreground">{t("ecosim.wizard.noResults")}</div>}
                      </div>
                    )}
                    {mode === "municipality" && municipalitiesError && <p className="text-xs text-destructive mt-1">{municipalitiesError}</p>}
                    {mode === "province" && provincesError && <p className="text-xs text-destructive mt-1">{provincesError}</p>}
                    {activeId && (
                      <div className="mt-2 rounded-lg border bg-primary/10 px-3 py-2 text-sm text-primary">
                        {t("ecosim.wizard.selected", { name: selectedName })}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-6">
                  <div className="rounded-xl border border-border/60 bg-card p-3">
                    <img
                      src="/MeralcoBillWithBoxes.png"
                      alt={t("ecosim.wizard.billImageAlt")}
                      className="w-full max-w-2xl mx-auto rounded-lg object-contain"
                    />
                    <p className="text-xs text-center text-muted-foreground mt-2">{t("ecosim.wizard.billImageCaption")}</p>
                  </div>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium"><HelpTooltip term="kWh">{t("ecosim.wizard.consumptionLabel")}</HelpTooltip></label>
                        <BillHelpModal
                          triggerText={t("ecosim.wizard.billHelpTrigger")}
                          title={t("ecosim.wizard.billHelp.consumptionTitle")}
                          description={t("ecosim.wizard.billHelp.consumptionDescription")}
                        />
                      </div>
                      <Input type="number" min="0" step="0.01" placeholder={t("ecosim.wizard.consumptionPlaceholder")} value={monthlyConsumption || ""} onChange={(e) => setMonthlyConsumption(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.consumptionHint")}</p>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium">{t("ecosim.wizard.rateLabel")}</label>
                        <BillHelpModal
                          triggerText={t("ecosim.wizard.billHelpTrigger")}
                          title={t("ecosim.wizard.billHelp.rateTitle")}
                          description={t("ecosim.wizard.billHelp.rateDescription")}
                        />
                      </div>
                      <Input type="number" min="0" step="0.01" placeholder={t("ecosim.wizard.ratePlaceholder")} value={electricityRate || ""} onChange={(e) => setElectricityRate(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.rateHint")}</p>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium">{t("ecosim.wizard.billLabel")}</label>
                        <BillHelpModal
                          triggerText={t("ecosim.wizard.billHelpTrigger")}
                          title={t("ecosim.wizard.billHelp.billTitle")}
                          description={t("ecosim.wizard.billHelp.billDescription")}
                        />
                      </div>
                      <Input type="number" min="0" step="0.01" placeholder={t("ecosim.wizard.billPlaceholder")} value={monthlyBill || ""} onChange={(e) => setMonthlyBill(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.billHint")}</p>
                    </div>
                  </div>
                  {electricityRate > 0 ? (
                    <div className="rounded-lg border bg-muted/30 p-3 text-sm">
                      <p className="text-muted-foreground">{t("ecosim.wizard.rateText", { rate: electricityRate.toFixed(2) })}</p>
                    </div>
                  ) : computedRate > 0 ? (
                    <div className="rounded-lg border bg-muted/30 p-3 text-sm flex items-center justify-between gap-3">
                      <p className="text-muted-foreground">{t("ecosim.wizard.rateComputedHint", { rate: computedRate.toFixed(2) })}</p>
                      <Button type="button" variant="outline" size="sm" onClick={() => setElectricityRate(Number(computedRate.toFixed(2)))}>
                        {t("ecosim.wizard.useComputedRate")}
                      </Button>
                    </div>
                  ) : null}
                </div>
              )}

              {step === 3 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium">{t("ecosim.wizard.savingsLabel")}</label>
                      <span className="text-sm font-bold text-sky-600">{desiredSavings}% — {savingsLabel}</span>
                    </div>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {(t("ecosim.wizard.quickSelect") || ["25%", "50%", "75%", "100%"]).map((pct) => {
                        const value = Number(pct.replace("%", ""));
                        return (
                          <Button
                            key={pct}
                            type="button"
                            size="sm"
                            variant={desiredSavings === value ? "default" : "outline"}
                            onClick={() => setDesiredSavings(value)}
                          >
                            {pct}
                          </Button>
                        );
                      })}
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
                      <span>{t("ecosim.wizard.savingsSliderStart")}</span>
                      <span>{t("ecosim.wizard.savingsSliderEnd")}</span>
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
                      <label className="text-sm font-medium">{t("ecosim.wizard.aiAnalysis")}</label>
                    </div>
                    <p className="text-xs text-muted-foreground">{t("ecosim.wizard.aiAnalysisHint")}</p>
                  </div>
                </div>
              )}

              {step === 4 && (
                <div className="space-y-4">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.location")}</p>
                        <button type="button" onClick={() => setStep(1)} className="text-xs text-primary hover:underline">{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{selectedName || t("ecosim.wizard.notSelected")}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p>
                        <button type="button" onClick={() => setStep(2)} className="text-xs text-primary hover:underline">{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{monthlyConsumption || 0} kWh</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p>
                        <button type="button" onClick={() => setStep(2)} className="text-xs text-primary hover:underline">{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">₱{monthlyBill?.toLocaleString() || 0}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.rate")}</p>
                        <button type="button" onClick={() => setStep(2)} className="text-xs text-primary hover:underline">{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">₱{electricityRate?.toFixed(2) || 0}/kWh</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p>
                        <button type="button" onClick={() => setStep(3)} className="text-xs text-primary hover:underline">{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{desiredSavings}% — {savingsLabel}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.aiAnalysis")}</p>
                        <button type="button" onClick={() => setStep(3)} className="text-xs text-primary hover:underline">{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{includeAi ? t("ecosim.wizard.yes") : t("ecosim.wizard.no")}</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">{t("ecosim.wizard.compareText")}</p>
                </div>
              )}

              <div className="flex items-center justify-between pt-2">
                {step > 1 ? <Button variant="outline" onClick={() => setStep(step - 1)} disabled={loading}><ArrowLeft className="h-4 w-4 mr-1" /> {t("ecosim.wizard.back")}</Button> : <div />}
                {step < totalSteps ? (
                  <Button onClick={() => setStep(step + 1)} disabled={!canProceed || loading}>{t("ecosim.wizard.next")} <ArrowRight className="h-4 w-4 ml-1" /></Button>
                ) : (
                  <div className="flex gap-2">
                    {result && user && <Button variant="outline" onClick={onSave} disabled={loading}>{t("ecosim.wizard.save")}</Button>}
                    <Button onClick={(e) => { e.preventDefault(); onRun(e); }} disabled={loading || !activeId}>
                      {loading ? <><Loader2 className="h-4 w-4 mr-1 animate-spin" /> {t("ecosim.wizard.running")}</> : <>{t("ecosim.wizard.runSimulation")} <ArrowRight className="h-4 w-4 ml-1" /></>}
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="hidden md:block">
          <Card className="bg-muted/30">
            <CardHeader><CardTitle className="text-sm">{t("ecosim.wizard.summaryTitle")}</CardTitle></CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.location")}</p><p className="font-medium">{selectedName || "—"}</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p><p className="font-medium">{monthlyConsumption || 0} kWh</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p><p className="font-medium">₱{monthlyBill?.toLocaleString() || 0}</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.rate")}</p><p className="font-medium">₱{electricityRate?.toFixed(2) || 0}/kWh</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p><p className="font-medium">{desiredSavings}%</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.aiAnalysis")}</p><p className="font-medium">{includeAi ? t("ecosim.wizard.yes") : t("ecosim.wizard.no")}</p></div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
