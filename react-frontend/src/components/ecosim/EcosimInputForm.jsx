import { useState, useMemo } from "react";
import { useI18n } from "@/i18n";
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
  const { t } = useI18n();
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
    if (s <= 10) return t("ecosim.wizard.savingsLevels.exploring");
    if (s <= 30) return t("ecosim.wizard.savingsLevels.little");
    if (s <= 60) return t("ecosim.wizard.savingsLevels.half");
    return t("ecosim.wizard.savingsLevels.offGrid");
  }, [desiredSavings, t]);

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
                {t("ecosim.wizard.step", { current: step, total: totalSteps })}
              </CardTitle>
              <CardDescription>
                {step === 1 && t("ecosim.wizard.steps.step1")}
                {step === 2 && t("ecosim.wizard.steps.step2")}
                {step === 3 && t("ecosim.wizard.steps.step3")}
                {step === 4 && t("ecosim.wizard.steps.step4")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Step 1: Location */}
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <label className="text-sm font-medium">{t("ecosim.wizard.searchMode")}</label>
                      <HelpTooltip term="municipality">
                        <span className="text-sm font-medium">{t("ecosim.wizard.municipality")}</span>
                      </HelpTooltip>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant={mode === "municipality" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setMode("municipality")}
                      >
                        {t("ecosim.wizard.municipality")}
                      </Button>
                      <Button
                        variant={mode === "province" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setMode("province")}
                      >
                        {t("ecosim.wizard.province")}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {t("ecosim.wizard.municipalityHint")}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium block mb-1">
                      {mode === "municipality" ? t("ecosim.wizard.searchMunicipality") : t("ecosim.wizard.searchProvince")}
                    </label>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        className="pl-9"
                        placeholder={mode === "municipality" ? t("ecosim.wizard.placeholderMunicipality") : t("ecosim.wizard.placeholderProvince")}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                    {searching && <p className="text-xs text-muted-foreground mt-1">{t("common.loading")}</p>}
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
                        {t("ecosim.wizard.selected", { name: selectedName })}
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
                        <HelpTooltip term="kWh">{t("ecosim.wizard.consumptionLabel")}</HelpTooltip>
                      </label>
                      <Input
                        type="number"
                        placeholder={t("ecosim.wizard.consumptionPlaceholder")}
                        value={monthlyConsumption || ""}
                        onChange={(e) => setMonthlyConsumption(Number(e.target.value))}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        {t("ecosim.wizard.consumptionHint")}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium block mb-1">{t("ecosim.wizard.billLabel")}</label>
                      <Input
                        type="number"
                        placeholder={t("ecosim.wizard.billPlaceholder")}
                        value={monthlyBill || ""}
                        onChange={(e) => setMonthlyBill(Number(e.target.value))}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        {t("ecosim.wizard.billHint")}
                      </p>
                    </div>
                  </div>
                  {monthlyConsumption > 0 && monthlyBill > 0 && (
                    <div className="rounded-lg border bg-muted/30 p-3 text-sm">
                      <p className="text-muted-foreground">
                        {t("ecosim.wizard.rateText", { rate: (monthlyBill / monthlyConsumption).toFixed(2) })}
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
                      <label className="text-sm font-medium">{t("ecosim.wizard.savingsLabel")}</label>
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
                      <span>{t("ecosim.wizard.savingsSliderStart")}</span>
                      <span className="font-medium text-foreground">{savingsLabel}</span>
                      <span>{t("ecosim.wizard.savingsSliderEnd")}</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Switch checked={includeAi} onCheckedChange={setIncludeAi} />
                      <label className="text-sm font-medium">{t("ecosim.wizard.aiAnalysis")}</label>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {t("ecosim.wizard.aiAnalysisHint")}
                    </p>
                  </div>
                </div>
              )}

              {/* Step 4: Review & Run */}
              {step === 4 && (
                <div className="space-y-4">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.location")}</p>
                      <p className="text-sm font-medium">{selectedName || t("ecosim.wizard.notSelected")}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p>
                      <p className="text-sm font-medium">{monthlyConsumption || 0} kWh</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p>
                      <p className="text-sm font-medium">₱{monthlyBill?.toLocaleString() || 0}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p>
                      <p className="text-sm font-medium">{desiredSavings}% — {savingsLabel}</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {t("ecosim.wizard.compareText")}
                  </p>
                </div>
              )}

              {/* Navigation buttons */}
              <div className="flex items-center justify-between pt-2">
                {step > 1 ? (
                  <Button variant="outline" onClick={() => setStep(step - 1)} disabled={loading}>
                    <ArrowLeft className="h-4 w-4 mr-1" /> {t("ecosim.wizard.back")}
                  </Button>
                ) : (
                  <div />
                )}
                {step < totalSteps ? (
                  <Button onClick={() => setStep(step + 1)} disabled={!canProceed || loading}>
                    {t("ecosim.wizard.next")} <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={onSave} disabled={loading}>
                      {t("ecosim.wizard.save")}
                    </Button>
                    <Button onClick={onRun} disabled={loading}>
                      {loading ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-1 animate-spin" /> {t("ecosim.wizard.running")}
                        </>
                      ) : (
                        <>
                          {t("ecosim.wizard.runSimulation")} <ArrowRight className="h-4 w-4 ml-1" />
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
              <CardTitle className="text-sm">{t("ecosim.wizard.summaryTitle")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.location")}</p>
                <p className="font-medium">{selectedName || t("common.notAvailable")}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p>
                <p className="font-medium">{monthlyConsumption || 0} kWh</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p>
                <p className="font-medium">₱{monthlyBill?.toLocaleString() || 0}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p>
                <p className="font-medium">{desiredSavings}%</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.aiAnalysis")}</p>
                <p className="font-medium">{includeAi ? t("ecosim.wizard.yes") : t("ecosim.wizard.no")}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
