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
import EcosimResults from "@/components/ecosim/EcosimResults";
import EcosimWizard from "@/components/ecosim/EcosimWizard";
import { getEcosim, getEcosimAI, getMunicipalities, getProvinces } from "@/services/apiClient";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";
import { supabase } from "@/services/supabaseClient";
import { useI18n } from "@/i18n";

export default function Ecosim() {
  const { t } = useI18n();
  const { user, accessToken } = useAuth();
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
  const clearAiPoll = () => {
    if (aiPollTimerRef.current) {
      clearTimeout(aiPollTimerRef.current);
      aiPollTimerRef.current = null;
    }
  };
  useEffect(() => clearAiPoll, []);

  // Save simulation dialog state
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [saveLabel, setSaveLabel] = useState("");
  const [saving, setSaving] = useState(false);

  const filteredMunicipalities = useMemo(() => {
    const q = muniQuery.trim().toLowerCase();
    if (!q) return municipalities;
    return municipalities
      .map((m) => {
        const name = m.name.toLowerCase();
        const prov = (m.province_name || "").toLowerCase();
        const nameIdx = name.indexOf(q);
        const provIdx = prov.indexOf(q);
        // Match if query is in municipality name OR province name
        const matchIdx = nameIdx >= 0 ? nameIdx : provIdx;
        return { ...m, _matchIdx: matchIdx, _startsWith: nameIdx === 0, _provinceMatch: provIdx >= 0 && nameIdx < 0 };
      })
      .filter((m) => m._matchIdx >= 0)
      .sort((a, b) => {
        if (a._startsWith !== b._startsWith) return a._startsWith ? -1 : 1;
        if (a._provinceMatch !== b._provinceMatch) return a._provinceMatch ? 1 : -1;
        return a._matchIdx - b._matchIdx || a.name.localeCompare(b.name);
      });
  }, [municipalities, muniQuery]);

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

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (runningRef.current) return;
    runningRef.current = true;
    setError(null);
    setLoading(true);
    setAiLoading(false);
    clearAiPoll();

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

      if (includeAi) {
        const aiParams = {
          municipalityId: String(activeId).trim(),
          monthlyConsumption: Number(monthlyConsumption),
          monthlyBill: Number(monthlyBill),
          electricityRate: Number(electricityRate),
          desiredSavings: Number(desiredSavings) / 100,
          mode,
        };

        const loadAi = (attempt = 1) => {
          setAiLoading(true);
          getEcosimAI(aiParams)
            .then((aiData) => {
              const analysis = aiData?.ai_analysis;
              if (analysis?.error?.includes("timed out") && attempt < 10) {
                aiPollTimerRef.current = setTimeout(() => {
                  loadAi(attempt + 1);
                }, 15000);
              } else {
                setResult((prev) =>
                  prev ? { ...prev, ai_analysis: analysis } : prev
                );
                setAiLoading(false);
              }
            })
            .catch((err) => {
              console.error("AI analysis failed:", err);
              setAiLoading(false);
            });
        };

        loadAi();
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

  const handleSaveSimulation = async () => {
    if (!user || !accessToken) {
      toast.error(t("ecosim.toasts.loginRequired"));
      return;
    }
    if (!result || !activeId) {
      toast.error(t("ecosim.toasts.runFirst"));
      return;
    }

    const defaultLabel = `${result.municipality || t("ecosim.defaults.simulation")} — ${result.recommended_source || t("ecosim.defaults.renewable")}`;
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
            results: result,
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
        return;
      }

      toast.success(t("ecosim.toasts.saveSuccess"));
      setSaveDialogOpen(false);
      setSaveLabel("");
    } catch (err) {
      toast.error(err?.message || t("ecosim.toasts.saveFailed"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page-container stack">
      <div className="space-y-2">
        <h1>{t("ecosim.title")}</h1>
        <p className="text-muted-foreground">
          {t("ecosim.subtitle")}
        </p>
      </div>

      <EcosimWizard
        mode={mode}
        setMode={setMode}
        muniQuery={muniQuery}
        setMuniQuery={setMuniQuery}
        muniOpen={muniOpen}
        setMuniOpen={setMuniOpen}
        filteredMunicipalities={filteredMunicipalities}
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
        activeId={activeId}
        result={result}
        user={user}
        onSave={() => {
          const defaultLabel = `${result.municipality || t("ecosim.defaults.simulation")} — ${result.recommended_source || t("ecosim.defaults.renewable")}`;
          setSaveLabel(defaultLabel);
          setSaveDialogOpen(true);
        }}
      />

      {error && (
        <Card className="border-destructive text-destructive">
          <CardHeader>
            <CardTitle>{t("ecosim.errorCardTitle")}</CardTitle>
            <CardDescription>
              {error.network
                ? "Could not reach the EcoSim server. Please check your connection and try again."
                : error.status === 401 || error.status === 429
                ? error.message
                : error.status === 404
                ? "We don't have data for this location yet. Try another municipality or province."
                : error.status >= 500
                ? `${error.message} (Request failed on the server — please try again.)`
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
                {loading ? "Retrying…" : "Try again"}
              </Button>
            </CardContent>
          )}
        </Card>
      )}

      {loading && <LoadingSkeleton />}

      {result && !loading && (
        <EcosimResults result={result} aiLoading={aiLoading} />
      )}

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
            <label className="text-sm font-medium">{t("ecosim.saveDialog.label")}</label>
            <Input
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
