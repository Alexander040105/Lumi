import { useEffect, useState } from "react";
import { useAuth } from "./useAuth";
import { getApiBaseUrl } from "@/utils/env";

export function useQuota(feature) {
  const { accessToken, isPremium } = useAuth();
  const [quota, setQuota] = useState(null);

  useEffect(() => {
    if (!accessToken) {
      setQuota(null);
      return;
    }
    if (isPremium) {
      setQuota({ limit: null, current: 0, remaining: null, upgrade: false });
      return;
    }

    fetch(`${getApiBaseUrl()}/protected/quota/${feature}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setQuota(d))
      .catch(() => setQuota(null));
  }, [accessToken, feature, isPremium]);

  return quota; // { feature, plan, limit, current, remaining, upgrade }
}
