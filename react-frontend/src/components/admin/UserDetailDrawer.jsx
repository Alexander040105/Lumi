import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { getApiBaseUrl } from "@/utils/env";

export default function UserDetailDrawer({ user, open, onClose }) {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  const [detail, setDetail] = useState(null);
  const [sims, setSims] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user || !open) return;
    setActiveTab("overview");
    setDetail(null);
    setSims([]);
    setReport(null);
    fetchDetail();
  }, [user, open]);

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

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "—");

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

        {activeTab === "overview" && detail && (
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.email")}</span>
              <span className="font-medium">{detail.email || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.name")}</span>
              <span className="font-medium">{detail.profile?.full_name || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">{t("admin.userDetail.role")}</span>
              <Badge variant="outline" className="capitalize">
                {detail.role}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">{t("admin.userDetail.plan")}</span>
              <Badge variant="secondary" className="capitalize">
                {detail.role === "admin" || detail.role === "dev"
                  ? t("admin.usersPage.planPremium")
                  : (detail.profile?.plan ? detail.profile.plan === "premium" ? t("admin.usersPage.planPremium") : t("admin.usersPage.planFree") : t("admin.usersPage.planFree"))}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.status")}</span>
              <Badge
                variant={detail.profile?.is_active ? "default" : "destructive"}
              >
                {detail.profile?.is_active ? t("admin.userDetail.active") : t("admin.userDetail.banned")}
              </Badge>
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
          </div>
        )}

        {activeTab === "simulations" && (
          <div className="mt-4 space-y-2">
            {sims.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("admin.userDetail.noSavedSimulations")}</p>
            ) : (
              sims.map((s) => (
                <div key={s.id} className="border rounded-lg p-3 text-sm">
                  <p className="font-medium">{s.name || t("admin.userDetail.untitled")}</p>
                  <p className="text-muted-foreground">
                    {t("admin.userDetail.municipality")}: {s.municipality_id || t("common.notAvailable")}
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
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.chatSessions")}</p>
                <p className="text-xl font-bold">{report.total_chat_sessions}</p>
              </div>
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.simulationsThisMonth")}</p>
                <p className="text-xl font-bold">{report.simulations_this_month}</p>
              </div>
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.chatSessionsThisMonth")}</p>
                <p className="text-xl font-bold">{report.chat_sessions_this_month}</p>
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
            {report.recent_simulations?.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">{t("admin.userDetail.recentSimulations")}</p>
                <div className="space-y-2">
                  {report.recent_simulations.map((s) => (
                    <div key={s.id} className="border rounded-lg p-2 text-sm">
                      <p className="font-medium">{s.name || t("admin.userDetail.untitled")}</p>
                      <p className="text-muted-foreground text-xs">
                        {formatDate(s.created_at)}
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
