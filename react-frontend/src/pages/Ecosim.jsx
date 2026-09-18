import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { getApiBaseUrl } from "@/utils/env";
import { downloadEcosimPdf } from "@/utils/ecosimPdf";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

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
import EcosimResults from "@/components/ecosim/EcosimResults";
import EcosimWizard from "@/components/ecosim/EcosimWizard";
import { CheckCircle2 } from "lucide-react";
import { getEcosim, getEcosimAI, getMunicipalities, getProvinces } from "@/services/apiClient";
import { saveLocation } from "@/services/savedLocations";
import { filterMunicipalities, formatMunicipalityLabel } from "@/utils/municipalities";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";
import { supabase } from "@/services/supabaseClient";
import { useI18n } from "@/i18n";

export default function Ecosim() {
  const { t } = useI18n();
  const { user, accessToken, profile } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [mode, setMode] = useState("municipality");
  const [municipalityId, setMunicipalityId] = useState("");
  const [municipalities, setMunicipalities] = useState([]);
  const [municipalitiesError, setMunicipalitiesError] = useState(null);
  const [muniQuery, setMuniQuery] = useState("");
  const [muniOpen, setMuniOpen] = useState(false);
  const [provinceId, setProvinceId] = useState("");
  const [provinces, setProvinces] = useState([]);
  const [provincesError, setProvincesError] = useState(null);
  const [provinceQuery, setProvinceQuery] = useState("");
  const [provinceOpen, setProvinceOpen] = useState(false);
  const [monthlyConsumption, setMonthlyConsumption] = useState(350);
  const [monthlyBill, setMonthlyBill] = useState(5000);
  const [electricityRate, setElectricityRate] = useState(0);
  const [desiredSavings, setDesiredSavings] = useState(50);
  const [includeAi, setIncludeAi] = useState(true);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const aiPollTimerRef = useRef(null);
  const runningRef = useRef(false);
  const MAX_AI_ATTEMPTS = 6;
  const AI_POLL_INTERVAL_MS = 5000;
  const clearAiPoll = () => {
    if (aiPollTimerRef.current) {
      clearTimeout(aiPollTimerRef.current);
      aiPollTimerRef.current = null;
    }
  };
  useEffect(() => clearAiPoll, []);

  // Save simulation dialog state
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false);
  const [saveLabel, setSaveLabel] = useState("");
  const [saving, setSaving] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const resultRef = useRef(null);

  const hasCompleteDialogBeenShownRef = useRef(false);
  const aiParamsRef = useRef(null);
  const aiAttemptsRef = useRef(0);
  const aiInFlightRef = useRef(false);

  const [aiError, setAiError] = useState(null);

  const startAiPoll = useCallback((params, attempt) => {
    const nextAttempt = attempt ?? aiAttemptsRef.current + 1;
    if (nextAttempt > MAX_AI_ATTEMPTS) {
      setAiLoading(false);
      setAiError(t("ecosim.toasts.aiFailed"));
      toast.error(t("ecosim.toasts.aiFailed"));
      aiInFlightRef.current = false;
      return;
    }
    aiAttemptsRef.current = nextAttempt;
    aiInFlightRef.current = true;
    setAiLoading(true);
    setAiError(null);
    getEcosimAI(params)
      .then((aiData) => {
        const analysis = aiData?.ai_analysis;
        if (
          (analysis?.error?.includes("timed out") || analysis?.status === "pending") &&
          nextAttempt < MAX_AI_ATTEMPTS
        ) {
          aiPollTimerRef.current = setTimeout(() => {
            startAiPoll(params);
          }, AI_POLL_INTERVAL_MS);
        } else if (analysis?.status === "failed" || (analysis?.error && !analysis?.summary)) {
          setAiError(t("ecosim.toasts.aiFailed"));
          toast.error(t("ecosim.toasts.aiFailed"));
          setAiLoading(false);
        } else {
          setResult((prev) =>
            prev ? { ...prev, ai_analysis: analysis } : prev
          );
          setAiError(null);
          setAiLoading(false);
        }
        aiInFlightRef.current = false;
      })
      .catch((err) => {
        console.error("AI analysis failed:", err);
        setAiError(t("ecosim.toasts.aiFailed"));
        toast.error(t("ecosim.toasts.aiFailed"));
        setAiLoading(false);
        aiInFlightRef.current = false;
      });
  }, [t]);

  useEffect(() => {
    hasCompleteDialogBeenShownRef.current = true;
  }, []);

  const filteredMunicipalities = useMemo(
    () => filterMunicipalities(municipalities, muniQuery),
    [municipalities, muniQuery]
  );

  const filteredProvinces = useMemo(() => {
    const q = provinceQuery.trim().toLowerCase();
    if (!q) return provinces;
    return provinces
      .map((p) => {
        const name = p.name.toLowerCase();
        const idx = name.indexOf(q);
        return { ...p, _matchIdx: idx, _startsWith: idx === 0 };
      })
      .filter((p) => p._matchIdx >= 0)
      .sort((a, b) => {
        if (a._startsWith !== b._startsWith) return a._startsWith ? -1 : 1;
        return a._matchIdx - b._matchIdx || a.name.localeCompare(b.name);
      });
  }, [provinces, provinceQuery]);

  const selectedName = useMemo(() => {
    if (mode === "municipality") {
      const found = filteredMunicipalities.find((m) => String(m.municipality_id) === municipalityId);
      if (!found) return muniQuery;
      return found.province_name ? `${found.name}, ${found.province_name}` : found.name;
    }
    const found = filteredProvinces.find((p) => String(p.province_id) === provinceId);
    return found ? found.name : provinceQuery;
  }, [mode, municipalityId, provinceId, filteredMunicipalities, filteredProvinces, muniQuery, provinceQuery]);

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
        setMunicipalitiesError(err?.message || t("ecosim.toasts.municipalitiesError"));
      }
    };

    loadMunicipalities();
    return () => {
      isActive = false;
    };
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

        if (error || !sim) throw new Error(error?.message || t("ecosim.toasts.loadFailed"));
        if (!isActive) return;

        // Pre-populate inputs
        const inputs = sim.inputs || {};
        if (inputs.monthly_consumption_kwh) {
          setMonthlyConsumption(inputs.monthly_consumption_kwh);
        }
        if (inputs.monthly_bill_php) {
          setMonthlyBill(inputs.monthly_bill_php);
        }
        if (inputs.electricity_rate !== undefined) {
          setElectricityRate(inputs.electricity_rate);
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
          loadedFromSavedRef.current = true;
        }
        toast.success(t("ecosim.toasts.loadSuccess"));
      } catch (err) {
        toast.error(err?.message || t("ecosim.toasts.loadFailed"));
      }
    };

    loadSaved();
    return () => {
      isActive = false;
    };
  }, [searchParams, user, municipalities]);

  const loadedFromSavedRef = useRef(false);
  const autoSavedResultRef = useRef(null);

  // Preselect municipality from query param ?municipality={id} (e.g. dashboard saved locations)
  const muniParamHandledRef = useRef(null);
  useEffect(() => {
    if (searchParams.get("simulation_id")) return;
    const muniParam = searchParams.get("municipality");
    if (!muniParam || !municipalities.length || muniParamHandledRef.current === muniParam) return;
    const found = municipalities.find((m) => String(m.municipality_id) === String(muniParam));
    setMunicipalityId(String(muniParam));
    setMuniQuery(found ? formatMunicipalityLabel(found) : muniParam);
    muniParamHandledRef.current = muniParam;
  }, [searchParams, municipalities]);

  const [locationSaved, setLocationSaved] = useState(false);
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  useEffect(() => setLocationSaved(false), [municipalityId]);

  const handleSaveLocation = async () => {
    if (!user) return;
    const res = await saveLocation({
      userId: user.id,
      municipalityId: Number(municipalityId),
      label: selectedName,
    });
    if (res.status === "duplicate") {
      toast.info(t("dashboard.locationAlreadySaved"));
      setLocationSaved(true);
    } else if (res.status === "saved") {
      toast.success(t("dashboard.locationSavedToast"));
      setLocationSaved(true);
    } else {
      toast.error(t("dashboard.locationSaveFailed"));
    }
  };

  useEffect(() => {
    if (result && !loading && !hasCompleteDialogBeenShownRef.current) {
      setCompleteDialogOpen(true);
      hasCompleteDialogBeenShownRef.current = true;
      requestAnimationFrame(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }, [result, loading]);

  useEffect(() => {
    const onVisibility = () => {
      if (document.hidden) {
        clearAiPoll();
      } else if (
        aiLoading &&
        !result?.ai_analysis &&
        !aiInFlightRef.current &&
        !aiPollTimerRef.current
      ) {
        startAiPoll(aiParamsRef.current);
      }
    };
    document.addEventListener("visibilitychange", onVisibility);
    return () => document.removeEventListener("visibilitychange", onVisibility);
  }, [aiLoading, result, startAiPoll]);

  useEffect(() => {
    let isActive = true;

    const loadProvinces = async () => {
      try {
        const data = await getProvinces();
        if (!isActive) return;
        const items = data?.items || [];
        setProvinces(items);
        if (items.length && !provinceId) {
          setProvinceId(String(items[0].province_id));
          setProvinceQuery(items[0].name);
        }
      } catch (err) {
        if (!isActive) return;
        setProvincesError(err?.message || t("ecosim.toasts.provincesError"));
      }
    };

    loadProvinces();
    return () => {
      isActive = false;
    };
  }, []);

  const activeId = mode === "province" ? provinceId : municipalityId;

  const validateInputs = () => {
    const id = String(activeId).trim();
    const consumption = Number(monthlyConsumption);
    const bill = Number(monthlyBill);
    const rate = Number(electricityRate);
    const savings = Number(desiredSavings);

    if (!id) return t("ecosim.validation.selectLocation");
    if (!Number.isFinite(consumption) || consumption <= 0) {
      return t("ecosim.validation.consumptionPositive");
    }
    if (!Number.isFinite(bill) || bill <= 0) {
      return t("ecosim.validation.billPositive");
    }
    if (!Number.isFinite(rate) || rate < 0) {
      return t("ecosim.validation.rateNegative");
    }
    if (!Number.isFinite(savings) || savings < 0 || savings > 100) {
      return t("ecosim.validation.savingsRange");
    }
    return null;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (runningRef.current) return;
    runningRef.current = true;
    loadedFromSavedRef.current = false;
    autoSavedResultRef.current = null;
    setError(null);
    setLoading(true);
    setAiLoading(false);
    setAiError(null);
    setCompleteDialogOpen(false);
    clearAiPoll();
    aiAttemptsRef.current = 0;
    aiInFlightRef.current = false;
    aiParamsRef.current = null;

    const validationError = validateInputs();
    if (validationError) {
      setError({ message: validationError });
      setLoading(false);
      runningRef.current = false;
      return;
    }

    try {
      const data = await getEcosim({
        municipalityId: String(activeId).trim(),
        monthlyConsumption: Number(monthlyConsumption),
        monthlyBill: Number(monthlyBill),
        electricityRate: Number(electricityRate),
        desiredSavings: Number(desiredSavings) / 100,
        includeAi: false,
        mode,
      });
      setResult(data);
      hasCompleteDialogBeenShownRef.current = false;

      if (user && profile?.ecosim_autosave !== false && !loadedFromSavedRef.current) {
        saveSimulation(defaultSaveLabel(data), data).then((ok) => {
          if (!ok) return;
          autoSavedResultRef.current = data;
          toast.success(t("ecosim.toasts.autoSaved"), {
            action: { label: t("common.view"), onClick: () => navigate("/saved-simulations") },
          });
        });
      }

      if (includeAi) {
        const aiParams = {
          municipalityId: String(activeId).trim(),
          monthlyConsumption: Number(monthlyConsumption),
          monthlyBill: Number(monthlyBill),
          electricityRate: Number(electricityRate),
          desiredSavings: Number(desiredSavings) / 100,
          mode,
        };
        aiParamsRef.current = aiParams;
        startAiPoll(aiParams);
      }
    } catch (err) {
      const network = err?.name === "TypeError" || err?.name === "AbortError" || (err?.message && /fetch|network|abort/i.test(err.message));
      setError({
        message: err?.message || t("ecosim.toasts.ecosimError"),
        status: err?.status,
        network,
      });
    } finally {
      runningRef.current = false;
      setLoading(false);
    }
  };

  const defaultSaveLabel = (data) =>
    `${data?.municipality || t("ecosim.defaults.simulation")} — ${data?.recommended_source || t("ecosim.defaults.renewable")}`;

  const saveSimulation = async (label, simResult = result) => {
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
            municipality_id: mode === "province" ? null : Number(activeId),
            province_id: mode === "province" ? Number(activeId) : null,
            mode,
            inputs: {
              monthly_consumption_kwh: Number(monthlyConsumption),
              monthly_bill_php: Number(monthlyBill),
              electricity_rate: Number(electricityRate),
              desired_savings_pct: Number(desiredSavings),
              include_ai: includeAi,
              mode,
            },
            results: simResult,
          }),
        }
      );

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        if (res.status === 403 && errData.detail?.upgrade) {
          toast.error(t("ecosim.toasts.saveLimit", { limit: errData.detail.limit }));
        } else {
          toast.error(errData.detail?.message || t("ecosim.toasts.saveFailed"));
        }
        return false;
      }
      return true;
    } catch (err) {
      toast.error(err?.message || t("ecosim.toasts.saveFailed"));
      return false;
    }
  };

  const handleSaveSimulation = async () => {
    if (!user || !accessToken) {
      toast.error(t("ecosim.toasts.loginRequired"));
      return;
    }
    if (!result || !activeId) {
      toast.error(t("ecosim.toasts.runFirst"));
      return;
    }
    if (result === autoSavedResultRef.current || loadedFromSavedRef.current) {
      toast.info(t("ecosim.toasts.alreadySaved"));
      return;
    }

    const label = saveLabel.trim() || defaultSaveLabel(result);

    setSaving(true);
    const ok = await saveSimulation(label);
    setSaving(false);
    if (ok) {
      toast.success(t("ecosim.toasts.saveSuccess"));
      setSaveDialogOpen(false);
      setSaveLabel("");
    }
  };

  const handleDownloadPdf = async () => {
    if (!result) {
      toast.error(t("ecosim.toasts.runFirst"));
      return;
    }
    setPdfLoading(true);
    try {
      await downloadEcosimPdf({
        result,
        inputs: {
          mode,
          selectedName,
          monthlyConsumption,
          monthlyBill,
          electricityRate,
          desiredSavings,
          includeAi,
        },
      });
    } catch (err) {
      console.error("PDF generation failed:", err);
      toast.error(t("ecosim.toasts.pdfFailed"));
    } finally {
      setPdfLoading(false);
    }
  };

  const handleAiRetry = () => {
    if (!aiParamsRef.current) return;
    aiAttemptsRef.current = 0;
    setAiError(null);
    startAiPoll(aiParamsRef.current);
  };

  return (
    <section className="page-container stack">
      <nav aria-label="Breadcrumb" className="text-sm text-muted-foreground">
        <ol className="flex items-center gap-2">
          <li>
            <Link to="/" className="hover:text-foreground hover:underline">
              {t("nav.home")}
            </Link>
          </li>
          <li>/</li>
          <li className="text-foreground">{t("nav.ecosim")}</li>
        </ol>
      </nav>

      <div className="space-y-2">
        <h1>{t("ecosim.title")}</h1>
        <p className="text-muted-foreground">
          {t("ecosim.subtitle")}
        </p>
      </div>

      <Card className="bg-muted/50">
        <CardContent className="pt-4 text-sm text-muted-foreground space-y-2">
          <p>
            <strong>{t("ecosim.disclaimerLead")}</strong>{" "}
            <Button
              variant="ghost"
              size="sm"
              className="h-auto px-1 py-0 text-xs text-muted-foreground underline decoration-dotted"
              onClick={() => setShowDisclaimer((v) => !v)}
              aria-expanded={showDisclaimer}
            >
              {t("ecosim.disclaimerWhy")}
            </Button>
          </p>
          {showDisclaimer && <p>{t("ecosim.disclaimerBody")}</p>}
        </CardContent>
      </Card>

      <EcosimWizard
        mode={mode}
        setMode={setMode}
        muniQuery={muniQuery}
        setMuniQuery={setMuniQuery}
        muniOpen={muniOpen}
        setMuniOpen={setMuniOpen}
        filteredMunicipalities={filteredMunicipalities}
        municipalities={municipalities}
        municipalityId={municipalityId}
        setMunicipalityId={setMunicipalityId}
        municipalitiesError={municipalitiesError}
        provinceQuery={provinceQuery}
        setProvinceQuery={setProvinceQuery}
        provinceOpen={provinceOpen}
        setProvinceOpen={setProvinceOpen}
        filteredProvinces={filteredProvinces}
        provinceId={provinceId}
        setProvinceId={setProvinceId}
        provincesError={provincesError}
        monthlyConsumption={monthlyConsumption}
        setMonthlyConsumption={setMonthlyConsumption}
        monthlyBill={monthlyBill}
        setMonthlyBill={setMonthlyBill}
        electricityRate={electricityRate}
        setElectricityRate={setElectricityRate}
        desiredSavings={desiredSavings}
        setDesiredSavings={setDesiredSavings}
        includeAi={includeAi}
        setIncludeAi={setIncludeAi}
        onRun={handleSubmit}
        loading={loading}
        aiLoading={aiLoading}
        aiError={aiError}
        activeId={activeId}
        result={result}
        user={user}
        onSave={() => {
          setSaveLabel(defaultSaveLabel(result));
          setSaveDialogOpen(true);
        }}
        onDownloadPdf={handleDownloadPdf}
        downloadPdfLoading={pdfLoading}
        onSaveLocation={handleSaveLocation}
        locationSaved={locationSaved}
        resultSaved={result === autoSavedResultRef.current || loadedFromSavedRef.current}
      />

      {error && (
        <Card className="border-destructive" role="alert">
          <CardHeader>
            <CardTitle className="text-destructive">{t("ecosim.errorCardTitle")}</CardTitle>
            <CardDescription>
              {error.network
                ? t("ecosim.errors.network")
                : error.status === 401 || error.status === 429
                ? error.message
                : error.status === 404
                ? t("ecosim.errors.noData")
                : error.status >= 500
                ? t("ecosim.errors.server", { message: error.message })
                : error.message}
            </CardDescription>
          </CardHeader>
          {(error.network || error.status >= 500) && (
            <CardContent>
              <Button
                type="button"
                variant="outline"
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? t("ecosim.errors.retrying") : t("ecosim.errors.retry")}
              </Button>
            </CardContent>
          )}
        </Card>
      )}

      {loading && <LoadingSkeleton />}

      {result && !loading && (
        <div id="ecosim-result" ref={resultRef}>
          <EcosimResults result={result} aiLoading={aiLoading} aiError={aiError} onAiRetry={handleAiRetry} />
        </div>
      )}

      {/* Completion Dialog */}
      <Dialog open={completeDialogOpen} onOpenChange={setCompleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <div className="flex items-center gap-2 text-primary">
              <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
              <DialogTitle>{t("ecosim.completion.title")}</DialogTitle>
            </div>
            <DialogDescription>
              {t("ecosim.completion.description")}
            </DialogDescription>
          </DialogHeader>
          <div className="py-2 text-sm text-muted-foreground">
            {t("ecosim.completion.recommendedLabel")}: {result?.recommended_source || "—"}
          </div>
          <DialogFooter>
            <Button
              type="button"
              onClick={() => {
                setCompleteDialogOpen(false);
                resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
              }}
            >
              {t("ecosim.completion.viewResults")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Save Simulation Dialog */}
      <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("ecosim.saveDialog.title")}</DialogTitle>
            <DialogDescription>
              {t("ecosim.saveDialog.description")}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <label htmlFor="save-simulation-label" className="text-sm font-medium">
              {t("ecosim.saveDialog.label")}
            </label>
            <Input
              id="save-simulation-label"
              value={saveLabel}
              onChange={(e) => setSaveLabel(e.target.value)}
              placeholder={t("ecosim.saveDialog.placeholder")}
              className="mt-2"
              autoFocus
            />
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">
                {t("ecosim.saveDialog.cancel")}
              </Button>
            </DialogClose>
            <Button
              type="button"
              onClick={handleSaveSimulation}
              disabled={saving}
            >
              {saving ? t("ecosim.saveDialog.saving") : t("ecosim.saveDialog.save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}
