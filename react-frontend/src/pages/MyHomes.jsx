import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { createHome, deleteHome, getHomes, getMunicipalities } from "@/services/apiClient";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";

export default function MyHomes() {
  const { accessToken } = useAuth();
  const [homes, setHomes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [municipalities, setMunicipalities] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState(null);

  const [newName, setNewName] = useState("");
  const [newMuniQuery, setNewMuniQuery] = useState("");
  const [newMuniId, setNewMuniId] = useState("");
  const [newConsumption, setNewConsumption] = useState(350);
  const [newBill, setNewBill] = useState(5000);

  useEffect(() => {
    let isActive = true;

    const load = async () => {
      try {
        const [homesData, muniData] = await Promise.all([
          getHomes(accessToken),
          getMunicipalities(),
        ]);
        if (!isActive) return;
        setHomes(homesData?.items || []);
        setMunicipalities(muniData?.items || []);
      } catch (err) {
        if (!isActive) return;
        setError(err?.message || "Failed to load homes.");
      } finally {
        if (isActive) setLoading(false);
      }
    };

    load();
    return () => {
      isActive = false;
    };
  }, [accessToken]);

  const filteredMunicipalities = municipalities.filter((m) =>
    m.name.toLowerCase().includes(newMuniQuery.trim().toLowerCase())
  );

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreateError(null);
    setCreating(true);

    try {
      const payload = {
        name: newName || "My Home",
        municipality_id: Number(newMuniId),
        monthly_consumption_kwh: Number(newConsumption),
        monthly_bill_php: Number(newBill),
      };
      const home = await createHome(accessToken, payload);
      setHomes((prev) => [home, ...prev]);
      setShowCreate(false);
      setNewName("");
      setNewMuniQuery("");
      setNewMuniId("");
      setNewConsumption(350);
      setNewBill(5000);
    } catch (err) {
      setCreateError(err?.message || "Failed to create home.");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (homeId) => {
    if (!window.confirm("Are you sure you want to delete this home? All simulations will be lost.")) return;
    try {
      await deleteHome(accessToken, homeId);
      setHomes((prev) => prev.filter((h) => h.home_id !== homeId));
    } catch (err) {
      setError(err?.message || "Failed to delete home.");
    }
  };

  if (loading) return <LoadingSkeleton />;

  return (
    <section className="page-container stack">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1>My Homes</h1>
          <p className="text-muted-foreground">
            Manage your properties and view saved simulations.
          </p>
        </div>
        <Button onClick={() => setShowCreate((s) => !s)}>
          {showCreate ? "Cancel" : "Add Home"}
        </Button>
      </div>

      {error && (
        <Card className="border-destructive text-destructive">
          <CardContent className="py-4">{error}</CardContent>
        </Card>
      )}

      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Home</CardTitle>
            <CardDescription>Add a property to track renewable energy simulations.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Home name</Label>
                <Input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g., My House"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Municipality</Label>
                <Input
                  value={newMuniQuery}
                  onChange={(e) => {
                    setNewMuniQuery(e.target.value);
                    setNewMuniId("");
                  }}
                  placeholder="Search municipality..."
                  required
                />
                {newMuniQuery && !newMuniId && filteredMunicipalities.length > 0 && (
                  <div className="max-h-40 overflow-auto rounded-md border border-input bg-popover shadow-md">
                    {filteredMunicipalities.slice(0, 8).map((m) => (
                      <button
                        key={m.municipality_id}
                        type="button"
                        className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
                        onClick={() => {
                          setNewMuniQuery(m.name);
                          setNewMuniId(String(m.municipality_id));
                        }}
                      >
                        {m.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="space-y-2">
                <Label>Monthly consumption (kWh)</Label>
                <Input
                  type="number"
                  min={1}
                  value={newConsumption}
                  onChange={(e) => setNewConsumption(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Monthly bill (PHP)</Label>
                <Input
                  type="number"
                  min={1}
                  value={newBill}
                  onChange={(e) => setNewBill(e.target.value)}
                  required
                />
              </div>
              <div className="md:col-span-2">
                {createError && <p className="text-sm text-destructive">{createError}</p>}
              </div>
              <div className="md:col-span-2">
                <Button type="submit" disabled={creating || !newMuniId}>
                  {creating ? "Creating..." : "Create Home"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {homes.length === 0 && !showCreate ? (
        <Card className="text-center">
          <CardContent className="py-12">
            <p className="text-muted-foreground">
              You have no homes yet. Click "Add Home" to create your first property.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {homes.map((home) => (
            <Card key={home.home_id} className="relative">
              <CardHeader>
                <CardTitle>{home.name}</CardTitle>
                <CardDescription>{home.municipality_name || "Unknown municipality"}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Simulations</span>
                  <span className="font-medium">{home.total_simulations ?? 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Carbon reduced</span>
                  <span className="font-medium">
                    {new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(
                      home.total_carbon_reduction_kg || 0
                    )} kg
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Avg independence</span>
                  <span className="font-medium">
                    {home.avg_independence_score != null
                      ? `${new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(home.avg_independence_score)} %`
                      : "N/A"}
                  </span>
                </div>
                <div className="flex gap-2 pt-2">
                  <Link to={`/homes/${home.home_id}`} className="flex-1">
                    <Button variant="outline" className="w-full">
                      View Details
                    </Button>
                  </Link>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(home.home_id)}>
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </section>
  );
}
