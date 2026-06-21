import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
import { supabase } from "../services/supabaseClient";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";

export default function Dashboard() {
  const { user, refreshProfile } = useAuth();
  const isLoggedIn = !!user;

  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editForm, setEditForm] = useState({ full_name: "", organization: "", location: "" });
  const [savingProfile, setSavingProfile] = useState(false);

  const [savedLocations, setSavedLocations] = useState([]);
  const [savedSimulations, setSavedSimulations] = useState([]);
  const [municipalities, setMunicipalities] = useState([]);
  const [selectedMuni, setSelectedMuni] = useState("");
  const [compositeScore, setCompositeScore] = useState(0);

  const fileInputRef = useRef(null);

  // Load dashboard data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Profile (if logged in)
        if (isLoggedIn) {
          const { data: prof } = await supabase
            .from("profiles")
            .select("*")
            .eq("id", user.id)
            .single();
          setProfile(prof);
          setEditForm({
            full_name: prof?.full_name || "",
            organization: prof?.organization || "",
            location: prof?.location || "",
          });

          // Saved locations
          const { data: locs } = await supabase
            .from("saved_locations")
            .select("*, municipalities(name)")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false });
          setSavedLocations(locs || []);

          // Saved simulations
          const { data: sims } = await supabase
            .from("saved_simulations")
            .select("*, municipalities(name)")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false });
          setSavedSimulations(sims || []);
        }

        // Municipalities for dropdown
        const { data: munis } = await supabase
          .from("municipalities")
          .select("municipality_id, name")
          .order("name", { ascending: true })
          .limit(500);
        setMunicipalities(munis || []);
      } catch (err) {
        toast.error("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isLoggedIn, user?.id]);

  const fetchCompositeScore = async (muniId) => {
    if (!muniId) return;
    try {
      const [solar, wind, hydro, geo] = await Promise.all([
        supabase.from("solar_suitability").select("solar_score").eq("municipality_id", muniId).single(),
        supabase.from("wind_suitability").select("wind_score").eq("municipality_id", muniId).single(),
        supabase.from("hydropower_suitability").select("hydro_suitability_score").eq("municipality_id", muniId).single(),
        supabase.from("geothermal_suitability").select("geothermal_score").eq("municipality_id", muniId).single(),
      ]);
      const scores = [
        solar.data?.solar_score || 0,
        wind.data?.wind_score || 0,
        hydro.data?.hydro_suitability_score || 0,
        geo.data?.geothermal_score || 0,
      ];
      const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
      setCompositeScore(Math.round(Math.min(100, Math.max(0, avg))));
    } catch {
      setCompositeScore(0);
    }
  };

  useEffect(() => {
    if (selectedMuni) fetchCompositeScore(selectedMuni);
  }, [selectedMuni]);

  // Profile save
  const handleSaveProfile = async () => {
    if (!isLoggedIn) {
      toast.info("Please log in to save your profile.");
      return;
    }
    setSavingProfile(true);
    try {
      const { error } = await supabase
        .from("profiles")
        .update({
          full_name: editForm.full_name,
          organization: editForm.organization,
          location: editForm.location,
          updated_at: new Date().toISOString(),
        })
        .eq("id", user.id);

      if (error) throw error;

      setProfile((prev) => ({
        ...prev,
        full_name: editForm.full_name,
        organization: editForm.organization,
        location: editForm.location,
      }));
      setIsEditingProfile(false);
      toast.success("Profile updated");
    } catch (err) {
      toast.error("Failed to update profile");
    } finally {
      setSavingProfile(false);
    }
  };

  // Avatar upload
  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !isLoggedIn) return;

    if (file.size > 2 * 1024 * 1024) {
      toast.error("Image must be under 2MB");
      return;
    }

    const ext = file.name.split(".").pop();
    const path = `${user.id}/avatar.${ext}`;

    try {
      setSavingProfile(true);
      const { error: uploadError } = await supabase.storage
        .from("avatars")
        .upload(path, file, { upsert: true });

      if (uploadError) throw uploadError;

      const { data: urlData } = supabase.storage.from("avatars").getPublicUrl(path);
      const avatarUrl = urlData.publicUrl;

      const { error: updateError } = await supabase
        .from("profiles")
        .update({ avatar_url: avatarUrl })
        .eq("id", user.id);

      if (updateError) throw updateError;

      setProfile((prev) => ({ ...prev, avatar_url: avatarUrl }));
      if (refreshProfile) await refreshProfile();
      toast.success("Profile photo updated");
    } catch (err) {
      toast.error("Upload failed: " + err.message);
    } finally {
      setSavingProfile(false);
    }
  };

  const displayName = profile?.full_name || user?.email || "Guest";
  const displayOrg = profile?.organization || "";
  const displayLoc = profile?.location || "";
  const avatarUrl = profile?.avatar_url || "";

  if (loading) {
    return (
      <section className="page-container stack">
        <h1 className="text-2xl font-bold">Decision Dashboard</h1>
        <LoadingSkeleton />
      </section>
    );
  }

  return (
    <section className="page-container stack space-y-6">
      {/* ===== Profile Card ===== */}
      <Card className="overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 to-primary/5 px-6 py-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            {/* Avatar */}
            <div className="relative shrink-0">
              <div className="w-20 h-20 rounded-full bg-muted border-2 border-background overflow-hidden flex items-center justify-center">
                {avatarUrl ? (
                  <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-2xl font-bold text-muted-foreground">
                    {displayName.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              {isLoggedIn && (
                <>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute -bottom-1 -right-1 bg-primary text-primary-foreground text-xs rounded-full px-2 py-0.5 shadow hover:bg-primary/90"
                    disabled={savingProfile}
                  >
                    {savingProfile ? "..." : "Edit"}
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleAvatarUpload}
                  />
                </>
              )}
            </div>

            {/* Profile Info */}
            <div className="flex-1 min-w-0">
              {!isEditingProfile ? (
                <div className="space-y-1">
                  <h2 className="text-xl font-bold truncate">{displayName}</h2>
                  {(displayOrg || displayLoc) && (
                    <p className="text-sm text-muted-foreground">
                      {displayOrg && <span className="mr-3">{displayOrg}</span>}
                      {displayLoc && <span>{displayLoc}</span>}
                    </p>
                  )}
                  {!isLoggedIn && (
                    <p className="text-sm text-muted-foreground">
                      <Link to="/login" className="underline text-primary">Log in</Link> to save your profile and data.
                    </p>
                  )}
                </div>
              ) : (
                <div className="space-y-2 max-w-md">
                  <input
                    type="text"
                    placeholder="Full Name"
                    value={editForm.full_name}
                    onChange={(e) => setEditForm((p) => ({ ...p, full_name: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder="Organization"
                    value={editForm.organization}
                    onChange={(e) => setEditForm((p) => ({ ...p, organization: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder="Location"
                    value={editForm.location}
                    onChange={(e) => setEditForm((p) => ({ ...p, location: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                </div>
              )}
            </div>

            {/* Edit Actions */}
            {isLoggedIn && (
              <div className="shrink-0">
                {!isEditingProfile ? (
                  <Button variant="outline" size="sm" onClick={() => setIsEditingProfile(true)}>
                    Edit Profile
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost" onClick={() => setIsEditingProfile(false)}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={handleSaveProfile} disabled={savingProfile}>
                      {savingProfile ? "Saving..." : "Save"}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* ===== Dashboard Grid ===== */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Overview */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Overview</CardTitle>
            <CardDescription>Select a municipality to see its renewable potential.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              value={selectedMuni}
              onChange={(e) => setSelectedMuni(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Select a municipality</option>
              {municipalities.map((m) => (
                <option key={m.municipality_id} value={m.municipality_id}>
                  {m.name}
                </option>
              ))}
            </select>

            {selectedMuni && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Composite Renewable Score</span>
                  <span className="font-bold">{compositeScore}/100</span>
                </div>
                <Progress value={compositeScore} className="h-3" />
                <p className="text-xs text-muted-foreground">
                  Averaged across solar, wind, hydro, and geothermal suitability.
                </p>
              </div>
            )}

            {!selectedMuni && (
              <p className="text-sm text-muted-foreground text-center py-4">
                Choose a municipality to display its renewable potential score.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link to="/ecosim" className="block">
              <Button className="w-full">Run EcoSim</Button>
            </Link>
            <Link to="/chat" className="block">
              <Button variant="outline" className="w-full">Ask LUMI AI</Button>
            </Link>
            <Link to="/energyhub" className="block">
              <Button variant="outline" className="w-full">View EnergyHub</Button>
            </Link>
          </CardContent>
        </Card>

        {/* Saved Locations */}
        <Card>
          <CardHeader>
            <CardTitle>Saved Locations</CardTitle>
            <CardDescription>Your bookmarked municipalities.</CardDescription>
          </CardHeader>
          <CardContent>
            {!isLoggedIn ? (
              <p className="text-sm text-muted-foreground">
                <Link to="/login" className="underline text-primary">Log in</Link> to save locations.
              </p>
            ) : savedLocations.length === 0 ? (
              <p className="text-sm text-muted-foreground">No saved locations yet.</p>
            ) : (
              <ul className="space-y-2">
                {savedLocations.map((loc) => (
                  <li key={loc.id} className="flex items-center justify-between text-sm">
                    <span>{loc.label || loc.municipalities?.name || "Municipality"}</span>
                    <Link to={`/ecosim?municipality=${loc.municipality_id}`}>
                      <Button variant="ghost" size="sm">Open</Button>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Saved Simulations */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Saved Simulations</CardTitle>
            <CardDescription>Your persisted EcoSim analyses.</CardDescription>
          </CardHeader>
          <CardContent>
            {!isLoggedIn ? (
              <p className="text-sm text-muted-foreground">
                <Link to="/login" className="underline text-primary">Log in</Link> to save simulations.
              </p>
            ) : savedSimulations.length === 0 ? (
              <p className="text-sm text-muted-foreground">No saved simulations yet.</p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {savedSimulations.map((sim) => {
                  const res = sim.results || {};
                  const recSource = res.recommended_source || "—";
                  const municipality = res.municipality || sim.municipalities?.name || "—";
                  const gen = res.estimated_generation_kwh;
                  const created = sim.created_at
                    ? new Date(sim.created_at).toLocaleDateString()
                    : "";
                  return (
                    <div
                      key={sim.id}
                      className="rounded-lg border bg-card p-4 hover:shadow-sm transition-shadow"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <h3
                          className="font-semibold text-sm truncate flex-1"
                          title={sim.label || "Unnamed Simulation"}
                        >
                          {sim.label || "Unnamed Simulation"}
                        </h3>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {municipality} • {recSource}
                      </p>
                      {gen !== undefined && gen !== null && (
                        <p className="text-xs mt-2">
                          <span className="font-medium">{Math.round(gen).toLocaleString()}</span>{" "}
                          kWh/mo
                        </p>
                      )}
                      {created && (
                        <p className="text-xs text-muted-foreground mt-1">{created}</p>
                      )}
                      <div className="flex items-center gap-2 mt-3">
                        <Link to={`/ecosim?simulation_id=${sim.id}`} className="flex-1">
                          <Button variant="outline" size="sm" className="w-full">
                            Open
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={async () => {
                            if (!window.confirm("Delete this simulation?")) return;
                            try {
                              const { error } = await supabase
                                .from("saved_simulations")
                                .delete()
                                .eq("id", sim.id)
                                .eq("user_id", user.id);
                              if (error) throw error;
                              setSavedSimulations((prev) =>
                                prev.filter((s) => s.id !== sim.id)
                              );
                              toast.success("Simulation deleted");
                            } catch (err) {
                              toast.error("Failed to delete simulation");
                            }
                          }}
                          className="text-destructive hover:text-destructive"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Center */}
        <Card>
          <CardHeader>
            <CardTitle>AI Center</CardTitle>
            <CardDescription>Quick insights from the LUMI assistant.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Ask the AI about renewable energy in your area.
            </p>
            <div className="flex gap-2 flex-wrap">
              <Link to="/chat">
                <Button size="sm" variant="secondary">
                  "Is solar good for Calamba?"
                </Button>
              </Link>
              <Link to="/chat">
                <Button size="sm" variant="secondary">
                  "Compare wind vs hydro"
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
