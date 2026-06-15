import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { getHome, getHomeSimulations, updateHome } from "@/services/apiClient";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";

const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0);

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0,
  }).format(value ?? 0);

export default function HomeDetail() {
  const { homeId } = useParams();
  const { accessToken } = useAuth();

  const [home, setHome] = useState(null);
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let isActive = true;

    const load = async () => {
      try {
        const [homeData, simsData] = await Promise.all([
          getHome(accessToken, homeId),
          getHomeSimulations(accessToken, homeId),
        ]);
        if (!isActive) return;
        setHome(homeData);
        setEditName(homeData.name);
        setSimulations(simsData?.items || []);
      } catch (err) {
        if (!isActive) return;
        setError(err?.message || "Failed to load home details.");
      } finally {
        if (isActive) setLoading(false);
      }
    };

    load();
    return () => {
      isActive = false;
    };
  }, [accessToken, homeId]);

  const handleSaveName = async () => {
    setSaving(true);
    try {
      const updated = await updateHome(accessToken, homeId, { name: editName });
      setHome((prev) => ({ ...prev, ...updated }));
      setEditing(false);
    } catch (err) {
      setError(err?.message || "Failed to update home.");
    } finally {
      setSaving(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 70) return "text-green-600";
    if (score >= 40) return "text-yellow-600";
    return "text-red-600";
  };

  if (loading) return <LoadingSkeleton />;
  if (error && !home) {
    return (
      <section className="page-container">
        <Card className="border-destructive text-destructive">
          <CardContent className="py-4">{error}</CardContent>
        </Card>
      </section>
    );
  }

  return (
    <section className="page-container stack">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link to="/homes" className="hover:underline">My Homes</Link>
        <span>/</span>
        <span>{home.name}</span>
      </div>

      <div className="flex items-center justify-between">
        <div className="space-y-1">
          {editing ? (
            <div className="flex items-center gap-2">
              <Input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="w-64"
              />
              <Button size="sm" onClick={handleSaveName} disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </Button>
              <Button size="sm" variant="outline" onClick={() => setEditing(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <h1 onClick={() => setEditing(true)} className="cursor-pointer" title="Click to rename">
              {home.name}
            </h1>
          )}
          <p className="text-muted-foreground">
            {home.municipality_name || "Unknown municipality"}
          </p>
        </div>
        <Link to="/ecosim">
          <Button>Run New Simulation</Button>
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {["overview", "simulations", "comparison"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={
              "px-4 py-2 text-sm font-medium capitalize transition-colors " +
              (activeTab === tab
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground")
            }
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Total simulations</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-semibold">{home.total_simulations || 0}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Carbon reduction</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-semibold">
                {formatNumber(home.total_carbon_reduction_kg || 0)} kg
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Avg independence</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-semibold">
                {home.avg_independence_score != null
                  ? `${formatNumber(home.avg_independence_score)} %`
                  : "N/A"}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Latest simulation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-semibold">
                {simulations.length
                  ? new Date(simulations[0].created_at).toLocaleDateString()
                  : "None yet"}
              </p>
            </CardContent>
          </Card>

          {home.latest_profile && (
            <Card className="md:col-span-2 lg:col-span-4">
              <CardHeader>
                <CardTitle>Latest Energy Profile</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-3">
                <div>
                  <Label className="text-muted-foreground">Monthly consumption</Label>
                  <p className="text-xl font-semibold">
                    {formatNumber(home.latest_profile.monthly_consumption_kwh)} kWh
                  </p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Monthly bill</Label>
                  <p className="text-xl font-semibold">
                    {formatCurrency(home.latest_profile.monthly_bill_php)}
                  </p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Rate</Label>
                  <p className="text-xl font-semibold">
                    {formatCurrency(home.latest_profile.electricity_rate_php_per_kwh)} / kWh
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Simulations Tab */}
      {activeTab === "simulations" && (
        <div className="space-y-4">
          {simulations.length === 0 ? (
            <Card className="text-center">
              <CardContent className="py-12">
                <p className="text-muted-foreground">
                  No simulations saved yet. Run a simulation in EcoSim and save it to this home.
                </p>
                <Link to="/ecosim" className="inline-block mt-4">
                  <Button>Go to EcoSim</Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {simulations.map((sim) => (
                <Card key={sim.simulation_id}>
                  <CardHeader>
                    <CardTitle className="text-base">{sim.simulation_name}</CardTitle>
                    <CardDescription>
                      {new Date(sim.created_at).toLocaleDateString()} — {sim.recommended_source}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Suitability</span>
                      <span className={`font-medium ${getScoreColor(sim.suitability_score)}`}>
                        {formatNumber(sim.suitability_score, 2)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Generation</span>
                      <span className="font-medium">{formatNumber(sim.estimated_generation_kwh)} kWh/mo</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Savings</span>
                      <span className="font-medium">{formatCurrency(sim.monthly_savings_php)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Payback</span>
                      <span className="font-medium">
                        {sim.payback_years ? `${formatNumber(sim.payback_years, 1)} yrs` : "N/A"}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Independence</span>
                      <span className="font-medium">{formatNumber(sim.independence_score)} %</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Carbon reduction</span>
                      <span className="font-medium">{formatNumber(sim.carbon_reduction_kg)} kg/mo</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Comparison Tab */}
      {activeTab === "comparison" && (
        <Card className="text-center">
          <CardContent className="py-12">
            <p className="text-muted-foreground">
              Side-by-side comparison feature coming soon. Select simulations to compare metrics.
            </p>
          </CardContent>
        </Card>
      )}
    </section>
  );
}
