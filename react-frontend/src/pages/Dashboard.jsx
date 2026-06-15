import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { getDashboardStats, getHealth, getHomes } from "../services/apiClient";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";

const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0);

export default function Dashboard() {
  const { accessToken, user } = useAuth();
  const [stats, setStats] = useState(null);
  const [homes, setHomes] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!accessToken) return;

    Promise.all([
      getDashboardStats(accessToken),
      getHomes(accessToken),
      getHealth(),
    ])
      .then(([statsData, homesData, healthStatus]) => {
        setStats(statsData);
        setHomes(homesData?.items?.slice(0, 3) || []);
        setHealth(healthStatus);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [accessToken]);

  if (loading) return <LoadingSkeleton />;

  return (
    <section className="page-container stack">
      <div className="space-y-2">
        <h1>Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.email || "User"}. Here is your renewable energy overview.
        </p>
      </div>

      {error && (
        <Card className="border-destructive text-destructive">
          <CardContent className="py-4">{error}</CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Homes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">{stats?.total_homes || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Simulations</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">{stats?.total_simulations || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Carbon Reduced</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">
              {formatNumber(stats?.total_carbon_reduction_kg || 0)} kg
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Avg Independence</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">
              {formatNumber(stats?.avg_independence_score || 0)} %
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">API Status</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg font-semibold">
              {health?.status === "ok" ? (
                <span className="text-green-600">Online</span>
              ) : (
                <span className="text-red-600">Offline</span>
              )}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Homes Preview */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Your Homes</h2>
          <Link to="/homes">
            <Button variant="outline" size="sm">View All</Button>
          </Link>
        </div>

        {homes.length === 0 ? (
          <Card className="text-center">
            <CardContent className="py-10">
              <p className="text-muted-foreground">
                You have no homes yet. Add one to start tracking your renewable energy potential.
              </p>
              <Link to="/homes" className="inline-block mt-4">
                <Button>Add Your First Home</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {homes.map((home) => (
              <Link key={home.home_id} to={`/homes/${home.home_id}`}>
                <Card className="h-full transition-shadow hover:shadow-md">
                  <CardHeader>
                    <CardTitle className="text-base">{home.name}</CardTitle>
                    <CardDescription>{home.municipality_name || "Unknown"}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Simulations</span>
                      <span className="font-medium">{home.total_simulations ?? 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Carbon reduced</span>
                      <span className="font-medium">
                        {formatNumber(home.total_carbon_reduction_kg || 0)} kg
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Run Simulation</CardTitle>
            <CardDescription>Evaluate renewable options for any municipality.</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/ecosim">
              <Button className="w-full">Go to EcoSim</Button>
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">National Analytics</CardTitle>
            <CardDescription>Explore energy trends and forecasts.</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/energyhub">
              <Button variant="outline" className="w-full">Go to EnergyHub</Button>
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Manage Homes</CardTitle>
            <CardDescription>Add, edit, or remove properties.</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/homes">
              <Button variant="outline" className="w-full">My Homes</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
