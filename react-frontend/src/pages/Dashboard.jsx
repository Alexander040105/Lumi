import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Check, MapPin, Trash2 } from "lucide-react";

import { useAuth } from "../hooks/useAuth";
import { useI18n } from "../i18n";
import { supabase } from "../services/supabaseClient";
import { getMunicipalities } from "../services/apiClient";
import { saveLocation } from "../services/savedLocations";
import { filterMunicipalities, formatMunicipalityLabel } from "../utils/municipalities";
import { getApiBaseUrl } from "@/utils/env";
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
import SearchableSelect from "@/components/shared/SearchableSelect";

export default function Dashboard() {
  const { user, accessToken, refreshProfile, isAdmin } = useAuth();
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
  const [municipalitiesError, setMunicipalitiesError] = useState(null);
  const [muniQuery, setMuniQuery] = useState("");
  const [muniOpen, setMuniOpen] = useState(false);
  const [selectedMuni, setSelectedMuni] = useState("");
  const [compositeScore, setCompositeScore] = useState(null);
  const [compositeClassification, setCompositeClassification] = useState(null);
  const [savingLocation, setSavingLocation] = useState(false);

  const filteredMunicipalities = useMemo(
    () => filterMunicipalities(municipalities, muniQuery),
    [municipalities, muniQuery]
  );

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

        // Municipalities for dropdown and name lookup (full set via backend)
        let munis = [];
        try {
          const data = await getMunicipalities();
          munis = data?.items || [];
        } catch {
          setMunicipalitiesError(t("dashboard.municipalitiesError"));
        }
        const muniMap = new Map(munis.map((m) => [m.municipality_id, formatMunicipalityLabel(m)]));
        setMunicipalities(munis);

        if (isLoggedIn) {
          const { data: locs } = await supabase
            .from("saved_locations")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false });
          setSavedLocations(
            (locs || []).map((loc) => ({
              ...loc,
              municipality_name: muniMap.get(loc.municipality_id) || "",
            }))
          );

          const { data: sims } = await supabase
            .from("saved_simulations")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false });
          setSavedSimulations(
            (sims || []).map((sim) => ({
              ...sim,
              municipality_name: muniMap.get(sim.municipality_id) || "",
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
      const { data } = await supabase
        .from("municipalities")
        .select("composite_suitability_score, composite_classification")
        .eq("municipality_id", muniId)
        .single();
      const raw = data?.composite_suitability_score;
      setCompositeScore(raw == null ? null : Math.round(Number(raw)));
      setCompositeClassification(data?.composite_classification || null);
    } catch {
      setCompositeScore(null);
      setCompositeClassification(null);
    }
  };

  const handleSaveLocation = async () => {
    const found = municipalities.find((m) => String(m.municipality_id) === String(selectedMuni));
    const label = found ? formatMunicipalityLabel(found) : muniQuery;
    setSavingLocation(true);
    const res = await saveLocation({
      userId: user.id,
      municipalityId: Number(selectedMuni),
      label,
    });
    setSavingLocation(false);
    if (res.status === "duplicate") {
      toast.info(t("dashboard.locationAlreadySaved"));
    } else if (res.status === "saved") {
      toast.success(t("dashboard.locationSavedToast"));
      setSavedLocations((prev) => [{ ...res.row, municipality_name: label }, ...prev]);
    } else {
      toast.error(t("dashboard.locationSaveFailed"));
    }
  };

  const handleRemoveLocation = async (loc) => {
    const { error } = await supabase.from("saved_locations").delete().eq("id", loc.id);
    if (error) {
      toast.error(t("dashboard.locationRemoveFailed"));
      return;
    }
    setSavedLocations((prev) => prev.filter((l) => l.id !== loc.id));
    toast.success(t("dashboard.locationRemoved"));
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
      const res = await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          full_name: editForm.full_name,
          organization: editForm.organization,
          location: editForm.location,
        }),
      });
      if (!res.ok) throw new Error("Update failed");

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

      const res = await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ avatar_url: avatarUrl }),
      });
      if (!res.ok) throw new Error("Could not save avatar");

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
          <Button variant="outline" size="sm" asChild>
            <Link to="/admin">{t("nav.adminPortal")}</Link>
          </Button>
        </div>
      )}
      {/* ===== Profile Card ===== */}
      <Card className="overflow-hidden">
        <div className="bg-muted/50 px-6 py-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            {/* Avatar */}
            <div className="relative shrink-0">
              <div className="w-20 h-20 rounded-full bg-muted border-2 border-background overflow-hidden flex items-center justify-center">
                {avatarUrl ? (
                  <img src={avatarUrl} alt="" className="w-full h-full object-cover" />
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
                    aria-label={t("dashboard.fullNamePlaceholder")}
                    value={editForm.full_name}
                    onChange={(e) => setEditForm((p) => ({ ...p, full_name: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder={t("dashboard.organizationPlaceholder")}
                    aria-label={t("dashboard.organizationPlaceholder")}
                    value={editForm.organization}
                    onChange={(e) => setEditForm((p) => ({ ...p, organization: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder={t("dashboard.locationPlaceholder")}
                    aria-label={t("dashboard.locationPlaceholder")}
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
            <SearchableSelect
              query={muniQuery}
              onQueryChange={setMuniQuery}
              open={muniOpen}
              onOpenChange={setMuniOpen}
              items={filteredMunicipalities}
              getOptionId={(m) => m.municipality_id}
              getOptionLabel={formatMunicipalityLabel}
              selectedId={selectedMuni}
              onSelect={(item) => {
                setSelectedMuni(String(item.municipality_id));
                setMuniQuery(formatMunicipalityLabel(item));
                setMuniOpen(false);
              }}
              placeholder={t("dashboard.selectMunicipality")}
              emptyText={t("ecosim.wizard.noResults")}
              moreResultsText={(count, total) => t("ecosim.wizard.moreResults", { count, total })}
              error={municipalitiesError}
            />

            {selectedMuni && (
              <div className="space-y-2">
                {compositeScore === null ? (
                  <p className="text-sm text-muted-foreground">{t("dashboard.noScoreData")}</p>
                ) : (
                  <>
                    <div className="flex justify-between text-sm">
                      <span>{t("dashboard.compositeScore")}</span>
                      <span className="font-bold">{compositeScore}/100</span>
                    </div>
                    <Progress value={compositeScore} className="h-3" />
                    {compositeClassification && (
                      <p className="text-xs text-muted-foreground capitalize">{compositeClassification}</p>
                    )}
                    <p className="text-xs text-muted-foreground">
                      {t("dashboard.compositeDescription")}
                    </p>
                  </>
                )}
              </div>
            )}

            {selectedMuni && isLoggedIn && (
              <div>
                {savedLocations.some((l) => String(l.municipality_id) === String(selectedMuni)) ? (
                  <Button variant="outline" size="sm" disabled>
                    <Check className="h-4 w-4 mr-2" aria-hidden="true" />
                    {t("dashboard.locationSaved")}
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleSaveLocation}
                    disabled={savingLocation}
                  >
                    <MapPin className="h-4 w-4 mr-2" aria-hidden="true" />
                    {savingLocation ? t("common.saving") : t("dashboard.saveLocation")}
                  </Button>
                )}
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
            <Button className="w-full" asChild>
              <Link to="/ecosim">{t("dashboard.runEcosim")}</Link>
            </Button>
            <Button variant="outline" className="w-full" asChild>
              <Link to="/energyhub">{t("dashboard.viewEnergyHub")}</Link>
            </Button>
            <Button variant="outline" className="w-full" asChild>
              <Link to="/mfa">{t("dashboard.mfaLink")}</Link>
            </Button>
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
                  <li key={loc.id} className="flex items-center justify-between text-sm gap-2">
                    <span className="truncate">{loc.label || loc.municipality_name || t("dashboard.municipality")}</span>
                    <div className="flex items-center shrink-0">
                      <Button variant="ghost" size="sm" asChild>
                        <Link to={`/ecosim?municipality=${loc.municipality_id}`}>{t("common.open")}</Link>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveLocation(loc)}
                        aria-label={t("common.delete")}
                      >
                        <Trash2 className="h-4 w-4" aria-hidden="true" />
                      </Button>
                    </div>
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
              <Button variant="outline" className="w-full" asChild>
                <Link to="/saved-simulations">
                  {t("dashboard.viewAllSavedSims")}
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>

      </div>
    </section>
  );
}
