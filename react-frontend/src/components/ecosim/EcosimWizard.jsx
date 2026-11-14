import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MapPin, Zap, Target, ArrowRight, ArrowLeft, Loader2, Check, Save, Printer, Bookmark, Receipt, Calculator, Sparkles, LocateFixed, SlidersHorizontal } from "lucide-react";
import HelpTooltip from "@/components/shared/HelpTooltip";
import SearchableSelect from "@/components/shared/SearchableSelect";
import { formatMunicipalityLabel, nearestMunicipality } from "@/utils/municipalities";
import { useI18n } from "@/i18n";
import {
  IllustrationLocation, IllustrationBill, IllustrationSavings,
  IllustrationSolar, IllustrationAI, IllustrationReview,
} from "@/components/illustrations";

const ENABLE_PROVINCE_MODE = false;

const STEP_ART = {
  1: IllustrationLocation,
  3: IllustrationSavings,
  4: IllustrationSolar,
  5: IllustrationAI,
  6: IllustrationReview,
};

export default function EcosimWizard({
  mode, setMode,
  muniQuery, setMuniQuery, muniOpen, setMuniOpen, filteredMunicipalities, municipalities = [], municipalityId, setMunicipalityId, municipalitiesError,
  provinceQuery, setProvinceQuery, provinceOpen, setProvinceOpen, filteredProvinces, provinceId, setProvinceId, provincesError,
  monthlyConsumption, setMonthlyConsumption, monthlyBill, setMonthlyBill, electricityRate, setElectricityRate,
  desiredSavings, setDesiredSavings, includeAi, setIncludeAi,
  includeBattery, setIncludeBattery, roofAreaM2, setRoofAreaM2, daytimeFraction, setDaytimeFraction,
  onRun, loading, activeId, result, user, onSave, onDownloadPdf, downloadPdfLoading,
  onSaveLocation, locationSaved, resultSaved, aiLoading, aiError,
}) {
  const { t } = useI18n();
  const [step, setStep] = useState(1);
  const [locating, setLocating] = useState(false);
  const [locateError, setLocateError] = useState(null);
  const [farDistanceKm, setFarDistanceKm] = useState(null);
  const totalSteps = 6;

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

  const StepArt = STEP_ART[step];

  const summaryRows = [
    { key: "location", label: t("ecosim.wizard.summary.location"), value: selectedName, set: Boolean(selectedName) },
    { key: "consumption", label: t("ecosim.wizard.summary.consumption"), value: `${monthlyConsumption || 0} kWh`, set: monthlyConsumption > 0 },
    { key: "bill", label: t("ecosim.wizard.summary.bill"), value: `₱${monthlyBill?.toLocaleString() || 0}`, set: monthlyBill > 0 },
    { key: "rate", label: t("ecosim.wizard.summary.rate"), value: `₱${electricityRate?.toFixed(2) || 0}/kWh`, set: electricityRate > 0 },
    { key: "savingsGoal", label: t("ecosim.wizard.summary.savingsGoal"), value: `${desiredSavings}%`, set: true },
    { key: "aiAnalysis", label: t("ecosim.wizard.summary.aiAnalysis"), value: includeAi ? t("ecosim.wizard.yes") : t("ecosim.wizard.no"), set: true },
    { key: "battery", label: t("ecosim.wizard.summary.battery"), value: includeBattery ? t("ecosim.wizard.yes") : t("ecosim.wizard.no"), set: true },
    { key: "roofArea", label: t("ecosim.wizard.summary.roofArea"), value: `${roofAreaM2} m²`, set: roofAreaM2 !== "" && roofAreaM2 != null },
    { key: "occupancy", label: t("ecosim.wizard.summary.occupancy"), value: daytimeFraction === 0.5 ? t("ecosim.wizard.occupancyHome") : t("ecosim.wizard.occupancyOut"), set: true },
  ].filter((r) => r.set);

  const summaryContent = summaryRows.length ? (
    <div className="space-y-3 text-sm">
      {summaryRows.map((r) => (
        <div key={r.key}>
          <p className="text-sm text-muted-foreground">{r.label}</p>
          <p className="font-medium">{r.value}</p>
        </div>
      ))}
    </div>
  ) : (
    <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summaryEmpty")}</p>
  );

  const handleLocate = () => {
    setLocateError(null);
    setFarDistanceKm(null);
    if (!navigator.geolocation) {
      setLocateError("ecosim.wizard.locationErrors.unsupported");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocating(false);
        const match = nearestMunicipality(municipalities, pos.coords.latitude, pos.coords.longitude);
        if (!match) {
          setLocateError("ecosim.wizard.locationErrors.noMatch");
          return;
        }
        setMunicipalityId(String(match.item.municipality_id));
        setMuniQuery(formatMunicipalityLabel(match.item));
        setMuniOpen(false);
        if (match.distanceKm > 150) {
          setFarDistanceKm(Math.round(match.distanceKm));
        }
      },
      (err) => {
        setLocating(false);
        const key = err.code === 1 ? "denied" : err.code === 2 ? "unavailable" : "timeout";
        setLocateError(`ecosim.wizard.locationErrors.${key}`);
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2" role="group" aria-label={t("ecosim.wizard.step", { current: step, total: totalSteps })}>
        {Array.from({ length: totalSteps }).map((_, i) => {
          const n = i + 1;
          const active = n === step;
          const done = n < step;
          return (
            <div key={n} className="flex items-center gap-2">
              <div
                aria-current={active ? "step" : undefined}
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-colors ${done ? "bg-primary/15 text-primary" : active ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
              >
                {done ? <Check className="h-4 w-4" /> : n}
              </div>
              {n < totalSteps && <div className={`h-0.5 w-6 ${done ? "bg-primary/40" : "bg-border"}`} />}
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
              <div className="space-y-1.5">
                <CardTitle className="flex items-center gap-2">
                  {step === 1 && <MapPin className="h-5 w-5 text-primary" aria-hidden="true" />}
                  {step === 2 && <Zap className="h-5 w-5 text-primary" aria-hidden="true" />}
                  {step === 3 && <Target className="h-5 w-5 text-primary" aria-hidden="true" />}
                  {step === 4 && <SlidersHorizontal className="h-5 w-5 text-primary" aria-hidden="true" />}
                  {step === 5 && <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" />}
                  {step === 6 && <ArrowRight className="h-5 w-5 text-primary" aria-hidden="true" />}
                  {t("ecosim.wizard.step", { current: step, total: totalSteps })}
                </CardTitle>
                <CardDescription>
                  {t(`ecosim.wizard.stepDescriptions.step${step}`)}
                </CardDescription>
              </div>
              {StepArt && (
                <StepArt className="h-14 w-14 shrink-0 md:h-16 md:w-16 pointer-events-none select-none" />
              )}
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
                    <label htmlFor="ecosim-location-search" className="text-sm font-medium block mb-1">{ENABLE_PROVINCE_MODE && mode === "province" ? t("ecosim.wizard.searchProvince") : t("ecosim.wizard.searchMunicipality")}</label>
                    {ENABLE_PROVINCE_MODE && mode === "province" ? (
                      <SearchableSelect
                        id="ecosim-location-search"
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
                        id="ecosim-location-search"
                        query={muniQuery}
                        onQueryChange={setMuniQuery}
                        open={muniOpen}
                        onOpenChange={setMuniOpen}
                        items={filteredMunicipalities}
                        getOptionId={(item) => item.municipality_id}
                        getOptionLabel={formatMunicipalityLabel}
                        selectedId={municipalityId}
                        onSelect={(item) => { setMunicipalityId(String(item.municipality_id)); setMuniQuery(formatMunicipalityLabel(item)); setMuniOpen(false); setLocateError(null); setFarDistanceKm(null); }}
                        placeholder={t("ecosim.wizard.placeholderMunicipality")}
                        disabled={loading}
                        error={municipalitiesError}
                        emptyText={t("ecosim.wizard.noResults")}
                        moreResultsText={(count, total) => t("ecosim.wizard.moreResults", { count, total })}
                      />
                    )}
                    <p className="text-sm text-muted-foreground mt-1">{t("ecosim.wizard.municipalityHint")}</p>
                    {(!ENABLE_PROVINCE_MODE || mode === "municipality") && (
                      <div className="mt-2">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={handleLocate}
                          disabled={loading || locating || municipalities.length === 0}
                          aria-busy={locating}
                        >
                          {locating ? <Loader2 className="h-4 w-4 animate-spin" /> : <LocateFixed className="h-4 w-4" />}
                          {t(locating ? "ecosim.wizard.locating" : "ecosim.wizard.useMyLocation")}
                        </Button>
                        {locateError && (
                          <p role="alert" className="text-xs text-destructive mt-1.5">{t(locateError)}</p>
                        )}
                        {farDistanceKm !== null && !locateError && (
                          <p role="status" className="text-xs text-warning mt-1.5">
                            {t("ecosim.wizard.locationFar", { name: selectedName, distance: farDistanceKm })}
                          </p>
                        )}
                      </div>
                    )}
                    {activeId && (
                      <div className="mt-2 rounded-lg border bg-primary/10 px-3 py-2 text-sm text-primary flex items-center justify-between gap-2">
                        <span>{t("ecosim.wizard.selected", { name: selectedName })}</span>
                        {user && mode === "municipality" && onSaveLocation && (
                          <button
                            type="button"
                            onClick={onSaveLocation}
                            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md text-primary hover:bg-primary/10"
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
                  <div className="rounded-lg border bg-muted/30 p-4 space-y-3">
                    <p className="text-sm font-medium">{t("ecosim.wizard.billGuide.title")}</p>
                    <div className="flex items-center gap-4">
                      <IllustrationBill
                        className="h-28 w-28 shrink-0"
                        title={t("ecosim.wizard.billGuide.illustrationTitle")}
                        desc={t("ecosim.wizard.billGuide.illustrationDesc")}
                      />
                      <div className="space-y-2">
                        <div className="flex items-start gap-2 text-sm text-muted-foreground">
                          <Zap className="h-4 w-4 shrink-0 mt-0.5" aria-hidden="true" />
                          <span>{t("ecosim.wizard.billGuide.kwh")}</span>
                        </div>
                        <div className="flex items-start gap-2 text-sm text-muted-foreground">
                          <Receipt className="h-4 w-4 shrink-0 mt-0.5" aria-hidden="true" />
                          <span>{t("ecosim.wizard.billGuide.bill")}</span>
                        </div>
                        <div className="flex items-start gap-2 text-sm text-muted-foreground">
                          <Calculator className="h-4 w-4 shrink-0 mt-0.5" aria-hidden="true" />
                          <span>{t("ecosim.wizard.billGuide.rate")}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <label htmlFor="ecosim-consumption" className="text-sm font-medium flex items-center min-h-[2.5rem] leading-tight mb-1"><HelpTooltip term="kWh">{t("ecosim.wizard.consumptionLabel")}</HelpTooltip></label>
                      <Input id="ecosim-consumption" type="number" min="0" step="0.01" placeholder={t("ecosim.wizard.consumptionPlaceholder")} value={monthlyConsumption || ""} onChange={(e) => setMonthlyConsumption(Number(e.target.value))} />
                      <p className="text-sm text-muted-foreground mt-1">{t("ecosim.wizard.consumptionHint")}</p>
                    </div>
                    <div>
                      <label htmlFor="ecosim-rate" className="text-sm font-medium flex items-center min-h-[2.5rem] leading-tight mb-1">{t("ecosim.wizard.rateLabel")}</label>
                      <Input id="ecosim-rate" type="number" min="0" step="0.01" placeholder={t("ecosim.wizard.ratePlaceholder")} value={electricityRate || ""} onChange={(e) => setElectricityRate(Number(e.target.value))} />
                      <p className="text-sm text-muted-foreground mt-1">{t("ecosim.wizard.rateHint")}</p>
                    </div>
                    <div>
                      <label htmlFor="ecosim-bill" className="text-sm font-medium flex items-center min-h-[2.5rem] leading-tight mb-1">{t("ecosim.wizard.billLabel")}</label>
                      <Input id="ecosim-bill" type="number" min="0" step="0.01" placeholder={t("ecosim.wizard.billPlaceholder")} value={monthlyBill || ""} onChange={(e) => setMonthlyBill(Number(e.target.value))} />
                      <p className="text-sm text-muted-foreground mt-1">{t("ecosim.wizard.billHint")}</p>
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
                      <label htmlFor="ecosim-savings" className="text-sm font-medium">{t("ecosim.wizard.savingsLabel")}</label>
                      <span className="text-sm font-bold text-primary">{desiredSavings}% — {savingsLabel}</span>
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
                      id="ecosim-savings"
                      type="range"
                      min="0"
                      max="100"
                      step="5"
                      value={desiredSavings}
                      onChange={(e) => setDesiredSavings(Number(e.target.value))}
                      className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:-mt-2 [&::-moz-range-thumb]:h-6 [&::-moz-range-thumb]:w-6 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:bg-primary"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-1">
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
                        id="ecosim-include-battery"
                        type="checkbox"
                        checked={includeBattery}
                        onChange={(e) => setIncludeBattery(e.target.checked)}
                        className="h-4 w-4 rounded border-input text-primary accent-primary"
                      />
                      <label htmlFor="ecosim-include-battery" className="text-sm font-medium">{t("ecosim.wizard.batteryLabel")}</label>
                    </div>
                    <p className="text-sm text-muted-foreground">{t("ecosim.wizard.batteryHint")}</p>
                  </div>

                  <div>
                    <label htmlFor="ecosim-roof-area" className="text-sm font-medium block mb-1">{t("ecosim.wizard.roofAreaLabel")}</label>
                    <Input
                      id="ecosim-roof-area"
                      type="number"
                      min="1"
                      step="0.5"
                      placeholder={t("ecosim.wizard.roofAreaPlaceholder")}
                      value={roofAreaM2}
                      onChange={(e) => setRoofAreaM2(e.target.value)}
                    />
                    <p className="text-sm text-muted-foreground mt-1">{t("ecosim.wizard.roofAreaHint")}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-2">{t("ecosim.wizard.occupancyLabel")}</p>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        type="button"
                        size="sm"
                        variant={daytimeFraction === 0.35 ? "default" : "outline"}
                        onClick={() => setDaytimeFraction(0.35)}
                      >
                        {t("ecosim.wizard.occupancyOut")}
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        variant={daytimeFraction === 0.5 ? "default" : "outline"}
                        onClick={() => setDaytimeFraction(0.5)}
                      >
                        {t("ecosim.wizard.occupancyHome")}
                      </Button>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{t("ecosim.wizard.occupancyHint")}</p>
                  </div>
                </div>
              )}

              {step === 5 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <input
                        id="ecosim-include-ai"
                        type="checkbox"
                        checked={includeAi}
                        onChange={(e) => setIncludeAi(e.target.checked)}
                        className="h-4 w-4 rounded border-input text-primary accent-primary"
                      />
                      <label htmlFor="ecosim-include-ai" className="text-sm font-medium">{t("ecosim.wizard.aiAnalysis")}</label>
                    </div>
                    <p className="text-sm text-muted-foreground">{t("ecosim.wizard.aiAnalysisHint")}</p>
                  </div>

                  <p className="text-sm text-muted-foreground">{t("ecosim.wizard.explanationPreview")}</p>
                </div>
              )}

              {step === 6 && (
                <div className="space-y-4">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.location")}</p>
                        <button type="button" onClick={() => setStep(1)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.location") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{selectedName || t("ecosim.wizard.notSelected")}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p>
                        <button type="button" onClick={() => setStep(2)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.consumption") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{monthlyConsumption || 0} kWh</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p>
                        <button type="button" onClick={() => setStep(2)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.bill") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">₱{monthlyBill?.toLocaleString() || 0}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.rate")}</p>
                        <button type="button" onClick={() => setStep(2)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.rate") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">₱{electricityRate?.toFixed(2) || 0}/kWh</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p>
                        <button type="button" onClick={() => setStep(3)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.savingsGoal") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{desiredSavings}% — {savingsLabel}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.aiAnalysis")}</p>
                        <button type="button" onClick={() => setStep(5)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.aiAnalysis") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{includeAi ? t("ecosim.wizard.yes") : t("ecosim.wizard.no")}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.battery")}</p>
                        <button type="button" onClick={() => setStep(4)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.battery") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{includeBattery ? t("ecosim.wizard.yes") : t("ecosim.wizard.no")}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.roofArea")}</p>
                        <button type="button" onClick={() => setStep(4)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.roofArea") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{roofAreaM2 ? `${roofAreaM2} m²` : t("ecosim.wizard.summary.roofAreaUnknown")}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">{t("ecosim.wizard.summary.occupancy")}</p>
                        <button type="button" onClick={() => setStep(4)} className="px-2 py-2 text-sm text-primary hover:underline" aria-label={t("ecosim.wizard.editField", { field: t("ecosim.wizard.summary.occupancy") })}>{t("ecosim.wizard.edit")}</button>
                      </div>
                      <p className="text-sm font-medium">{daytimeFraction === 0.5 ? t("ecosim.wizard.occupancyHome") : t("ecosim.wizard.occupancyOut")}</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">{t("ecosim.wizard.compareText")}</p>
                </div>
              )}

              <details className="md:hidden rounded-lg border bg-muted/30 p-3">
                <summary className="cursor-pointer text-sm font-medium">{t("ecosim.wizard.summaryTitle")}</summary>
                <div className="mt-2">{summaryContent}</div>
              </details>

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
            <CardHeader className="flex flex-row items-center gap-3 space-y-0">
              {StepArt && <StepArt className="h-10 w-10 shrink-0" />}
              <CardTitle className="text-sm">{t("ecosim.wizard.summaryTitle")}</CardTitle>
            </CardHeader>
            <CardContent>{summaryContent}</CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
