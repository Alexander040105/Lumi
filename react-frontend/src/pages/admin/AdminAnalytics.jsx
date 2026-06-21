import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { getApiBaseUrl } from "@/utils/env";

export default function AdminAnalytics() {
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

  if (loading) return <p className="p-6">Loading...</p>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">System Analytics</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">Total Users</p>
          <p className="text-2xl font-bold">{stats?.total_users ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">Simulations</p>
          <p className="text-2xl font-bold">{stats?.total_simulations ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">Chat Sessions</p>
          <p className="text-2xl font-bold">{stats?.total_chat_sessions ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">Free / Premium</p>
          <p className="text-2xl font-bold">
            {stats?.free_users ?? 0} / {stats?.premium_users ?? 0}
          </p>
        </div>
      </div>
    </div>
  );
}
