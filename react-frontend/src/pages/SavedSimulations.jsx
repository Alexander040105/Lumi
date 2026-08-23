import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { supabase } from "@/services/supabaseClient";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";

export default function SavedSimulations() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [savedSimulations, setSavedSimulations] = useState([]);

  useEffect(() => {
    if (!user) return;
    const load = async () => {
      setLoading(true);
      try {
        // Try joined query first; fall back to plain select if FK/RLS blocks it
        let simsQuery = supabase
          .from("saved_simulations")
          .select("*, municipalities(name)")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });
        let { data: sims, error: simsError } = await simsQuery;

        if (simsError || !sims) {
          ({ data: sims, error: simsError } = await supabase
            .from("saved_simulations")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false }));
        }

        setSavedSimulations(sims || []);
      } catch {
        toast.error(t("savedSimulations.loadError"));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user]);

  const deleteSimulation = async (id) => {
    if (!window.confirm(t("savedSimulations.deleteSimConfirm"))) return;
    try {
      const { error } = await supabase
        .from("saved_simulations")
        .delete()
        .eq("id", id)
        .eq("user_id", user.id);
      if (error) throw error;
      setSavedSimulations((prev) => prev.filter((s) => s.id !== id));
      toast.success(t("savedSimulations.simDeleted"));
    } catch {
      toast.error(t("savedSimulations.simDeleteFailed"));
    }
  };

  if (!user) return <p className="p-6">{t("savedSimulations.pleaseLogin")}</p>;
  if (loading) {
    return (
      <section className="page-container stack">
        <h1 className="text-2xl font-bold">{t("savedSimulations.title")}</h1>
        <LoadingSkeleton />
      </section>
    );
  }

  return (
    <section className="page-container stack space-y-6">
      <h1 className="text-2xl font-bold">{t("savedSimulations.title")}</h1>

      {/* EcoSim Saves */}
      <Card>
        <CardHeader>
          <CardTitle>{t("savedSimulations.ecoSimsTitle")}</CardTitle>
          <CardDescription>{t("savedSimulations.ecoSimsDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          {savedSimulations.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {t("savedSimulations.noSimulations")}{" "}
              <Link to="/ecosim" className="underline text-primary">
                {t("savedSimulations.runOne")}
              </Link>
              .
            </p>
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
                        title={sim.label || t("savedSimulations.unnamedSimulation")}
                      >
                        {sim.label || t("savedSimulations.unnamedSimulation")}
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
                          {t("savedSimulations.open")}
                        </Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteSimulation(sim.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        {t("savedSimulations.delete")}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

    </section>
  );
}
