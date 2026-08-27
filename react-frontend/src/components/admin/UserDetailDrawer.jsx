import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { getApiBaseUrl } from "@/utils/env";

export default function UserDetailDrawer({ user, open, onClose, onUserChange }) {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  const [detail, setDetail] = useState(null);
  const [sims, setSims] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [banLoading, setBanLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    full_name: "",
    organization: "",
    location: "",
    preferred_municipality_id: "",
  });

  useEffect(() => {
    if (!user || !open) return;
    setActiveTab("overview");
    setDetail(null);
    setSims([]);
    setReport(null);
    setIsEditing(false);
    fetchDetail();
  }, [user, open]);

  useEffect(() => {
    if (detail?.profile) {
      setEditForm({
        full_name: detail.profile.full_name || "",
        organization: detail.profile.organization || "",
        location: detail.profile.location || "",
        preferred_municipality_id: detail.profile.preferred_municipality_id || "",
      });
    }
  }, [detail]);

  const fetchDetail = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/users/${user.id}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await res.json();
      setDetail(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const fetchSimulations = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/simulations`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const data = await res.json();
      setSims(data.simulations || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const fetchReport = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/reports`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const data = await res.json();
      setReport(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleTab = (tab) => {
    setActiveTab(tab);
    if (tab === "simulations" && sims.length === 0) fetchSimulations();
    if (tab === "reports" && !report) fetchReport();
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/profile`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify(editForm),
        }
      );
      if (!res.ok) throw new Error("Update failed");
      await fetchDetail();
      setIsEditing(false);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "—");

  const handleForceReset = async () => {
    if (!window.confirm("Send a password reset email to this user?")) return;
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/force-password-reset`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${accessToken}` },
        }
      );
      if (!res.ok) throw new Error("Reset failed");
      toast.success("Password reset email sent");
    } catch {
      toast.error("Could not send reset email");
    }
  };

  const handleBanToggle = async () => {
    setBanLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/ban`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${accessToken}` },
        }
      );
      if (!res.ok) throw new Error("Ban toggle failed");
      await fetchDetail();
      if (onUserChange) onUserChange();
    } catch (err) {
      toast.error(err.message || "Ban toggle failed");
    } finally {
      setBanLoading(false);
    }
  };

  if (!user) return null;

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{t("admin.userDetail.title")}</SheetTitle>
        </SheetHeader>

        <div className="mt-4 flex gap-2 border-b pb-2">
          {["overview", "simulations", "reports"].map((tab) => (
            <button
              key={tab}
              onClick={() => handleTab(tab)}
              className={`text-sm px-3 py-1 rounded-md capitalize ${
                activeTab === tab
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted"
              }`}
            >
              {t(`admin.userDetail.tabs.${tab}`)}
            </button>
          ))}
        </div>

        {loading && <p className="text-sm text-muted-foreground py-4">{t("admin.userDetail.loading")}</p>}

        {activeTab === "overview" && detail && !isEditing && (
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.email")}</span>
              <span className="font-medium">{detail.email || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.name")}</span>
              <span className="font-medium">{detail.profile?.full_name || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.organization")}</span>
              <span className="font-medium">{detail.profile?.organization || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.location")}</span>
              <span className="font-medium">{detail.profile?.location || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.municipality")}</span>
              <span className="font-medium">{detail.profile?.preferred_municipality_id || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">{t("admin.userDetail.role")}</span>
              <Badge variant="outline" className="capitalize">
                {detail.role}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">{t("admin.userDetail.status")}</span>
              <div className="flex items-center gap-2">
                <Badge
                  variant={detail.profile?.is_active ? "default" : "destructive"}
                >
                  {detail.profile?.is_active ? t("admin.userDetail.active") : t("admin.userDetail.banned")}
                </Badge>
                <Button
                  size="sm"
                  variant={detail.profile?.is_active ? "destructive" : "outline"}
                  onClick={handleBanToggle}
                  disabled={banLoading}
                >
                  {detail.profile?.is_active ? t("admin.usersPage.ban") : t("admin.usersPage.unban")}
                </Button>
              </div>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.joined")}</span>
              <span>{formatDate(detail.created_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.lastSignIn")}</span>
              <span>{formatDate(detail.last_sign_in_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.emailConfirmed")}</span>
              <span>{detail.email_confirmed ? t("admin.userDetail.yes") : t("admin.userDetail.no")}</span>
            </div>
            <div className="flex gap-2 pt-2">
              <Button
                variant="outline"
                onClick={() => setIsEditing(true)}
                disabled={loading}
              >
                {t("common.edit")}
              </Button>
              <Button
                variant="outline"
                onClick={handleForceReset}
              >
                Force reset password
              </Button>
            </div>
          </div>
        )}

        {activeTab === "overview" && detail && isEditing && (
          <div className="mt-4 space-y-3 text-sm">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">
                {t("admin.userDetail.name")}
              </label>
              <Input
                value={editForm.full_name}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, full_name: e.target.value }))
                }
                placeholder={t("admin.userDetail.name")}
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">
                {t("admin.userDetail.organization")}
              </label>
              <Input
                value={editForm.organization}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, organization: e.target.value }))
                }
                placeholder={t("admin.userDetail.organization")}
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">
                {t("admin.userDetail.location")}
              </label>
              <Input
                value={editForm.location}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, location: e.target.value }))
                }
                placeholder={t("admin.userDetail.location")}
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">
                {t("admin.userDetail.municipality")}
              </label>
              <Input
                value={editForm.preferred_municipality_id}
                onChange={(e) =>
                  setEditForm((f) => ({
                    ...f,
                    preferred_municipality_id: e.target.value,
                  }))
                }
                placeholder={t("admin.userDetail.municipality")}
              />
            </div>
            <div className="flex gap-2 pt-2">
              <Button onClick={handleSave} disabled={loading}>
                {loading ? t("common.saving") : t("common.save")}
              </Button>
              <Button
                variant="outline"
                onClick={() => setIsEditing(false)}
                disabled={loading}
              >
                {t("common.cancel")}
              </Button>
            </div>
          </div>
        )}

        {activeTab === "simulations" && (
          <div className="mt-4 space-y-2">
            {sims.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("admin.userDetail.noSavedSimulations")}</p>
            ) : (
              sims.map((s) => (
                <div key={s.id} className="border rounded-lg p-3 text-sm">
                  <p className="font-medium">{s.label || t("admin.userDetail.untitled")}</p>
                  <p className="text-muted-foreground">
                    {t("admin.userDetail.municipality")}: {s.municipalities?.name || s.municipality_id || t("common.notAvailable")}
                  </p>
                  <p className="text-muted-foreground">{formatDate(s.created_at)}</p>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "reports" && report && (
          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.totalSimulations")}</p>
                <p className="text-xl font-bold">{report.total_simulations}</p>
              </div>
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.totalEcosim")}</p>
                <p className="text-xl font-bold">{report.total_ecosim}</p>
              </div>
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.simulationsThisMonth")}</p>
                <p className="text-xl font-bold">{report.simulations_this_month}</p>
              </div>
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.ecosimThisMonth")}</p>
                <p className="text-xl font-bold">{report.ecosim_this_month}</p>
              </div>
            </div>
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t("admin.userDetail.peakMunicipality")}</span>
                <span className="font-medium">
                  {report.peak_municipality_id || t("common.notAvailable")}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t("admin.userDetail.lastActive")}</span>
                <span>{formatDate(report.last_active)}</span>
              </div>
            </div>
            {report.monthly_breakdown?.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">{t("admin.userDetail.monthlyBreakdown")}</p>
                <div className="space-y-1">
                  {report.monthly_breakdown.map((m) => (
                    <div key={m.month} className="flex justify-between text-sm border-b py-1">
                      <span className="text-muted-foreground">{m.month}</span>
                      <span className="font-medium">
                        {m.saved_simulations} sims / {m.ecosim_calculations} EcoSim
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {report.recent_simulations?.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">{t("admin.userDetail.recentSimulations")}</p>
                <div className="space-y-2">
                  {report.recent_simulations.map((s) => (
                    <div key={s.id} className="border rounded-lg p-2 text-sm">
                      <p className="font-medium">{s.label || t("admin.userDetail.untitled")}</p>
                      <p className="text-muted-foreground text-xs">
                        {s.municipality_name || s.municipality_id || t("common.notAvailable")} — {formatDate(s.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
