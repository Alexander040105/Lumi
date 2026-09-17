import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MapPin, Zap, Target, ArrowRight, ArrowLeft, Loader2, Check, Save, Printer, Bookmark, Receipt, Calculator, Sparkles } from "lucide-react";
import HelpTooltip from "@/components/shared/HelpTooltip";
import SearchableSelect from "@/components/shared/SearchableSelect";
import { formatMunicipalityLabel } from "@/utils/municipalities";
import { useI18n } from "@/i18n";

const ENABLE_PROVINCE_MODE = false;

export default function EcosimWizard({
  mode, setMode,
  muniQuery, setMuniQuery, muniOpen, setMuniOpen, filteredMunicipalities, municipalityId, setMunicipalityId, municipalitiesError,
  provinceQuery, setProvinceQuery, provinceOpen, setProvinceOpen, filteredProvinces, provinceId, setProvinceId, provincesError,
  monthlyConsumption, setMonthlyConsumption, monthlyBill, setMonthlyBill, electricityRate, setElectricityRate,
  desiredSavings, setDesiredSavings, includeAi, setIncludeAi,
  onRun, loading, activeId, result, user, onSave, onDownloadPdf, downloadPdfLoading,
  onSaveLocation, locationSaved, resultSaved, aiLoading, aiError,
}) {
  const { t } = useI18n();
  const [step, setStep] = useState(1);
  const totalSteps = 5;

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

  const aiReady = !includeAi || aiError || (!aiLoading && result?.ai_analysis?.summary && result.ai_analysis?.status !== "pending");

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
                {step === 4 && <Sparkles className="h-5 w-5 text-sky-500" />}
                {step === 5 && <ArrowRight className="h-5 w-5 text-destructive" />}
                {t("ecosim.wizard.step", { current: step, total: totalSteps })}
              </CardTitle>
              <CardDescription>
                {t(`ecosim.wizard.stepDescriptions.step${step}`)}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {step === 1 && (
                <div className="space-y-4">
                  {ENABLE_PROVINCE_MODE && (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <label className="text-sm font-medium">{t("ecosim.wizard.searchMode")}</label>
                      </div>
                      <div className="flex gap-2">
                        <Button variant={mode === "municipality" ? "default" : "outline"} size="sm" onClick={() => setMode("municipality")}>{t("ecosim.wizard.municipality")}</Button>
                        <Button variant={mode === "province" ? "default" : "outline"} size="sm" onClick={() => setMode("province")}>{t("ecosim.wizard.province")}</Button>
                      </div>
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium block mb-1">{ENABLE_PROVINCE_MODE && mode === "province" ? t("ecosim.wizard.searchProvince") : t("ecosim.wizard.searchMunicipality")}</label>
                    {ENABLE_PROVINCE_MODE && mode === "province" ? (
                      <SearchableSelect
                        query={provinceQuery}
                        onQueryChange={setProvinceQuery}
                        open={provinceOpen}
                        onOpenChange={setProvinceOpen}
                        items={filteredProvinces}
                        getOptionId={(item) => item.province_id}
                        getOptionLabel={(item) => item.name}
                        selectedId={provinceId}
                        onSelect={(item) => { setProvinceId(String(item.province_id)); setProvinceQuery(item.name); setProvinceOpen(false); }}
                        placeholder={t("ecosim.wizard.placeholderProvince")}
                        disabled={loading}
                        error={provincesError}
                        emptyText={t("ecosim.wizard.noResults")}
                        moreResultsText={(count, total) => t("ecosim.wizard.moreResults", { count, total })}
                      />
                    ) : (
                      <SearchableSelect
                        query={muniQuery}
                        onQueryChange={setMuniQuery}
                        open={muniOpen}
                        onOpenChange={setMuniOpen}
                        items={filteredMunicipalities}
                        getOptionId={(item) => item.municipality_id}
                        getOptionLabel={formatMunicipalityLabel}
                        selectedId={municipalityId}
                        onSelect={(item) => { setMunicipalityId(String(item.municipality_id)); setMuniQuery(formatMunicipalityLabel(item)); setMuniOpen(false); }}
                        placeholder={t("ecosim.wizard.placeholderMunicipality")}
                        disabled={loading}
                        error={municipalitiesError}
                        emptyText={t("ecosim.wizard.noResults")}
                        moreResultsText={(count, total) => t("ecosim.wizard.moreResults", { count, total })}
                      />
                    )}
                    <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.municipalityHint")}</p>
                    {activeId && (
                      <div className="mt-2 rounded-lg border bg-primary/10 px-3 py-2 text-sm text-primary flex items-center justify-between gap-2">
                        <span>{t("ecosim.wizard.selected", { name: selectedName })}</span>
                        {user && mode === "municipality" && onSaveLocation && (
                          <button
                            type="button"
                            onClick={onSaveLocation}
                            className="shrink-0 text-primary hover:text-primary/70"
                            aria-label={locationSaved ? t("ecosim.wizard.locationSavedChip") : t("ecosim.wizard.saveLocation")}
                            title={locationSaved ? t("ecosim.wizard.locationSavedChip") : t("ecosim.wizard.saveLocation")}
                          >
                            {locationSaved ? <Check className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-6">
                  <div className="rounded-lg border bg-muted/30 p-4 space-y-2">
                    <p className="text-sm font-medium">{t("ecosim.wizard.billGuide.title")}</p>
                    <div className="flex items-start gap-2 text-xs text-muted-foreground">
                      <Zap className="h-4 w-4 shrink-0 mt-0.5" />
                      <span>{t("ecosim.wizard.billGuide.kwh")}</span>
                    </div>
                    <div className="flex items-start gap-2 text-xs text-muted-foreground">
                      <Receipt className="h-4 w-4 shrink-0 mt-0.5" />
                      <span>{t("ecosim.wizard.billGuide.bill")}</span>
                    </div>
                    <div className="flex items-start gap-2 text-xs text-muted-foreground">
                      <Calculator className="h-4 w-4 shrink-0 mt-0.5" />
                      <span>{t("ecosim.wizard.billGuide.rate")}</span>
                    </div>
                  </div>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <label className="text-sm font-medium flex items-center min-h-[2.5rem] leading-tight mb-1"><HelpTooltip term="kWh">{t("ecosim.wizard.consumptionLabel")}</HelpTooltip></label>
                      <Input type="number" min="0" step="0.01" placeholder={t("ecosim.wizard.consumptionPlaceholder")} value={monthlyConsumption || ""} onChange={(e) => setMonthlyConsumption(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.consumptionHint")}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium flex items-center min-h-[2.5rem] leading-tight mb-1">{t("ecosim.wizard.rateLabel")}</label>
                      <Input type="number" min="0" step="0.01" placeholder={t("ecosim.wizard.ratePlaceholder")} value={electricityRate || ""} onChange={(e) => setElectricityRate(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.rateHint")}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium flex items-center min-h-[2.5rem] leading-tight mb-1">{t("ecosim.wizard.billLabel")}</label>
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
                </div>
              )}

              {step === 4 && (
                <div className="space-y-4">
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
                  <p className="text-sm text-muted-foreground">{t("ecosim.wizard.explanationPreview")}</p>
                </div>
              )}

              {step === 5 && (
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
                        <button type="button" onClick={() => setStep(4)} className="text-xs text-primary hover:underline">{t("ecosim.wizard.edit")}</button>
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
                  <div className="flex flex-wrap items-center gap-2 justify-end">
                      {result && user && !resultSaved && (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={onSave}
                          disabled={loading}
                        >
                          <Save className="mr-2 h-4 w-4" />
                          {t("ecosim.wizard.saveToAccount") || "Save to Account"}
                        </Button>
                      )}
                      {result && aiReady && (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={(e) => { e.preventDefault(); onDownloadPdf?.(); }}
                          disabled={downloadPdfLoading || loading || !onDownloadPdf}
                        >
                          {downloadPdfLoading ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          ) : (
                            <Printer className="mr-2 h-4 w-4" />
                          )}
                          {downloadPdfLoading
                            ? t("ecosim.wizard.generatingPdf") || "Generating..."
                            : t("ecosim.wizard.saveAsPdf") || "Save as PDF"}
                        </Button>
                      )}
                      <Button
                        type="button"
                        onClick={(e) => { e.preventDefault(); onRun(e); }}
                        disabled={loading || !activeId}
                      >
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
