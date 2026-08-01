import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { getApiBaseUrl } from "@/utils/env";

export default function AdminAnalytics() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${getApiBaseUrl()}/admin/analytics`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((r) => r.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [accessToken]);

  if (loading) return <p className="p-6">{t("common.loading")}</p>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">{t("admin.analyticsPage.title")}</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{t("admin.analyticsPage.totalUsers")}</p>
          <p className="text-2xl font-bold">{stats?.total_users ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{t("admin.analyticsPage.simulations")}</p>
          <p className="text-2xl font-bold">{stats?.total_simulations ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{t("admin.analyticsPage.chatSessions")}</p>
          <p className="text-2xl font-bold">{stats?.total_chat_sessions ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{t("admin.analyticsPage.freePremium")}</p>
          <p className="text-2xl font-bold">
            {stats?.free_users ?? 0} / {stats?.premium_users ?? 0}
          </p>
        </div>
      </div>
    </div>
  );
}
