import { useEffect, useMemo, useState } from "react";
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
import LcoePanel from "../components/LcoePanel";
import { getEcosim, getMunicipalities, getProvinces, getProductRecommendations } from "@/services/apiClient";
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
  const [desiredSavings, setDesiredSavings] = useState(50);
  const [includeAi, setIncludeAi] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [productRecs, setProductRecs] = useState(null);
  const [productLoading, setProductLoading] = useState(false);

  // Save simulation dialog state
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [saveLabel, setSaveLabel] = useState("");
  const [saving, setSaving] = useState(false);

  const filteredMunicipalities = useMemo(() => {
    const q = muniQuery.trim().toLowerCase();
    if (!q) return municipalities;
    return municipalities.filter((m) => m.name.toLowerCase().includes(q));
  }, [municipalities, muniQuery]);

  const filteredProvinces = useMemo(() => {
    const q = provinceQuery.trim().toLowerCase();
    if (!q) return provinces;
    return provinces.filter((p) => p.name.toLowerCase().includes(q));
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
        setMunicipalitiesError(err?.message || "Unable to load municipalities.");
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
        setProvincesError(err?.message || "Unable to load provinces.");
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
    setError(null);
    setLoading(true);

    try {
      const data = await getEcosim({
        municipalityId: String(activeId).trim(),
        monthlyConsumption: Number(monthlyConsumption),
        monthlyBill: Number(monthlyBill),
        desiredSavings: Number(desiredSavings) / 100,
        includeAi,
        mode,
      });
      setResult(data);
      // Fetch product recommendations for the recommended source
      const source = data?.recommended_source?.toLowerCase();
      if (source && source !== "geothermal") {
        setProductLoading(true);
        try {
          const recs = await getProductRecommendations(source, null, 4);
          setProductRecs(recs);
        } catch {
          setProductRecs(null);
        } finally {
          setProductLoading(false);
        }
      } else {
        setProductRecs(null);
      }
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
          const defaultLabel = `${result.municipality || "Simulation"} — ${result.recommended_source || "Renewable"}`;
          setSaveLabel(defaultLabel);
          setSaveDialogOpen(true);
        }}
      />

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
        <EcosimResults
          result={result}
          productRecs={productRecs}
          productLoading={productLoading}
        />
      )}

      {result?.options && !loading && (
        <div className="mt-4">
          <LcoePanel options={result.options} />
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
