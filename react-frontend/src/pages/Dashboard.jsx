import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
import { useI18n } from "../i18n";
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
import CoverageDashboard from "../components/CoverageDashboard";
import ForecastPanel from "../components/ForecastPanel";

export default function Dashboard() {
  const { user, refreshProfile, isAdmin } = useAuth();
  const { t } = useI18n();
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

        }

        // Municipalities for dropdown and name lookup
        const { data: munis } = await supabase
          .from("municipalities")
          .select("municipality_id, name")
          .order("name", { ascending: true })
          .limit(500);
        const muniMap = new Map((munis || []).map((m) => [m.municipality_id, m.name]));
        setMunicipalities(munis || []);

        if (isLoggedIn) {
          // Saved locations: try joined query, fall back to plain select with client-side name lookup
          let { data: locs } = await supabase
            .from("saved_locations")
            .select("*, municipalities(name)")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false });
          if (!locs) {
            ({ data: locs } = await supabase
              .from("saved_locations")
              .select("*")
              .eq("user_id", user.id)
              .order("created_at", { ascending: false }));
          }
          setSavedLocations(
            (locs || []).map((loc) => ({
              ...loc,
              municipality_name: loc.municipalities?.name || muniMap.get(loc.municipality_id) || "",
            }))
          );

          // Saved simulations: same pattern
          let { data: sims } = await supabase
            .from("saved_simulations")
            .select("*, municipalities(name)")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false });
          if (!sims) {
            ({ data: sims } = await supabase
              .from("saved_simulations")
              .select("*")
              .eq("user_id", user.id)
              .order("created_at", { ascending: false }));
          }
          setSavedSimulations(
            (sims || []).map((sim) => ({
              ...sim,
              municipality_name: sim.municipalities?.name || muniMap.get(sim.municipality_id) || "",
            }))
          );
        }
      } catch (err) {
        toast.error(t("dashboard.loadError"));
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
      toast.info(t("dashboard.loginToSaveProfileToast"));
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
      toast.success(t("dashboard.profileUpdated"));
    } catch (err) {
      toast.error(t("dashboard.profileUpdateFailed"));
    } finally {
      setSavingProfile(false);
    }
  };

  // Avatar upload
  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !isLoggedIn) return;

    if (file.size > 2 * 1024 * 1024) {
      toast.error(t("dashboard.imageTooLarge"));
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
      toast.success(t("dashboard.photoUpdated"));
    } catch (err) {
      toast.error(t("dashboard.uploadFailed") + err.message);
    } finally {
      setSavingProfile(false);
    }
  };

  const displayName = profile?.full_name || user?.email || t("common.guest");
  const displayOrg = profile?.organization || "";
  const displayLoc = profile?.location || "";
  const avatarUrl = profile?.avatar_url || "";

  if (loading) {
    return (
      <section className="page-container stack">
        <h1 className="text-2xl font-bold">{t("dashboard.title")}</h1>
        <LoadingSkeleton />
      </section>
    );
  }

  return (
    <section className="page-container stack space-y-6">
      {isAdmin && (
        <div className="rounded-lg border bg-primary/10 p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <p className="text-sm font-medium">{t("dashboard.adminLink")}</p>
          <Link to="/admin">
            <Button variant="outline" size="sm">{t("nav.adminPortal")}</Button>
          </Link>
        </div>
      )}
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
                    {savingProfile ? "..." : t("common.edit")}
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
                      <Link to="/login" className="underline text-primary">{t("nav.login")}</Link>{" "}{t("dashboard.loginToSaveProfile")}
                    </p>
                  )}
                </div>
              ) : (
                <div className="space-y-2 max-w-md">
                  <input
                    type="text"
                    placeholder={t("dashboard.fullNamePlaceholder")}
                    value={editForm.full_name}
                    onChange={(e) => setEditForm((p) => ({ ...p, full_name: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder={t("dashboard.organizationPlaceholder")}
                    value={editForm.organization}
                    onChange={(e) => setEditForm((p) => ({ ...p, organization: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder={t("dashboard.locationPlaceholder")}
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
                    {t("dashboard.editProfile")}
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost" onClick={() => setIsEditingProfile(false)}>
                      {t("common.cancel")}
                    </Button>
                    <Button size="sm" onClick={handleSaveProfile} disabled={savingProfile}>
                      {savingProfile ? t("common.saving") : t("common.save")}
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
            <CardTitle>{t("dashboard.overview")}</CardTitle>
            <CardDescription>{t("dashboard.overviewDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              value={selectedMuni}
              onChange={(e) => setSelectedMuni(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">{t("dashboard.selectMunicipality")}</option>
              {municipalities.map((m) => (
                <option key={m.municipality_id} value={m.municipality_id}>
                  {m.name}
                </option>
              ))}
            </select>

            {selectedMuni && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>{t("dashboard.compositeScore")}</span>
                  <span className="font-bold">{compositeScore}/100</span>
                </div>
                <Progress value={compositeScore} className="h-3" />
                <p className="text-xs text-muted-foreground">
                  {t("dashboard.compositeDescription")}
                </p>
              </div>
            )}

            {!selectedMuni && (
              <p className="text-sm text-muted-foreground text-center py-4">
                {t("dashboard.selectPrompt")}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.quickActions")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link to="/ecosim" className="block">
              <Button className="w-full">{t("dashboard.runEcosim")}</Button>
            </Link>
            <Link to="/energyhub" className="block">
              <Button variant="outline" className="w-full">{t("dashboard.viewEnergyHub")}</Button>
            </Link>
            <Link to="/mfa" className="block">
              <Button variant="outline" className="w-full">{t("dashboard.mfaLink")}</Button>
            </Link>
          </CardContent>
        </Card>

        {/* Saved Locations */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.savedLocations")}</CardTitle>
            <CardDescription>{t("dashboard.savedLocationsDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            {!isLoggedIn ? (
              <p className="text-sm text-muted-foreground">
                <Link to="/login" className="underline text-primary">{t("nav.login")}</Link>{" "}{t("dashboard.loginToSaveLocations")}
              </p>
            ) : savedLocations.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("dashboard.noSavedLocations")}</p>
            ) : (
              <ul className="space-y-2">
                {savedLocations.map((loc) => (
                  <li key={loc.id} className="flex items-center justify-between text-sm">
                    <span>{loc.label || loc.municipality_name || t("dashboard.municipality")}</span>
                    <Link to={`/ecosim?municipality=${loc.municipality_id}`}>
                      <Button variant="ghost" size="sm">{t("common.open")}</Button>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Saved Simulations CTA */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.savedSims")}</CardTitle>
            <CardDescription>{t("dashboard.savedSimsDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            {!isLoggedIn ? (
              <p className="text-sm text-muted-foreground">
                <Link to="/login" className="underline text-primary">{t("nav.login")}</Link>{" "}{t("dashboard.loginToSaveSims")}
              </p>
            ) : (
              <Link to="/saved-simulations">
                <Button variant="outline" className="w-full">
                  {t("dashboard.viewAllSavedSims")}
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>

      </div>

      {/* Forecasting & Coverage */}
      <div className="grid gap-4 md:grid-cols-2 mt-4">
        {isAdmin && <ForecastPanel />}
        <CoverageDashboard />
      </div>
    </section>
  );
}
