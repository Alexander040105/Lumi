import { useEffect, useState } from "react";

import { useAuth } from "../hooks/useAuth";
import { getProtectedMe, getHealth } from "../services/apiClient";

export default function Dashboard() {
  const { accessToken, user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!accessToken) return;

    Promise.all([getProtectedMe(accessToken), getHealth()])
      .then(([me, healthStatus]) => {
        setProfile(me.user);
        setHealth(healthStatus);
      })
      .catch((err) => setError(err.message));
  }, [accessToken]);

  return (
    <section>
      <h1>Dashboard</h1>
      <p>Signed in as {user?.email || "unknown"}</p>
      {error && <div>{error}</div>}
      {profile && (
        <div>
          <h2>JWT Claims</h2>
          <pre>{JSON.stringify(profile, null, 2)}</pre>
        </div>
      )}
      {health && (
        <div>
          <h2>API Health</h2>
          <pre>{JSON.stringify(health, null, 2)}</pre>
        </div>
      )}
    </section>
  );
}
