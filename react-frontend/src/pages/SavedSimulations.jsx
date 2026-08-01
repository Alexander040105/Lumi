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
  const [chatSessions, setChatSessions] = useState([]);
  const [expandedSession, setExpandedSession] = useState(null);

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

        const [{ data: sessions }] = await Promise.all([
          supabase
            .from("chat_sessions")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false }),
        ]);

        setSavedSimulations(sims || []);
        setChatSessions(sessions || []);
      } catch {
        toast.error(t("savedSimulations.loadError"));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user]);

  const fetchSessionMessages = async (sessionId) => {
    if (expandedSession === sessionId) {
      setExpandedSession(null);
      return;
    }
    const { data } = await supabase
      .from("chat_messages")
      .select("role, content, created_at")
      .eq("session_id", sessionId)
      .order("created_at", { ascending: true });
    setChatSessions((prev) =>
      prev.map((s) => (s.id === sessionId ? { ...s, messages: data || [] } : s))
    );
    setExpandedSession(sessionId);
  };

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

  const deleteChatSession = async (id) => {
    if (!window.confirm(t("savedSimulations.deleteChatConfirm"))) return;
    try {
      const { error } = await supabase
        .from("chat_sessions")
        .delete()
        .eq("id", id)
        .eq("user_id", user.id);
      if (error) throw error;
      setChatSessions((prev) => prev.filter((s) => s.id !== id));
      if (expandedSession === id) setExpandedSession(null);
      toast.success(t("savedSimulations.chatDeleted"));
    } catch {
      toast.error(t("savedSimulations.chatDeleteFailed"));
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

      {/* Chat History */}
      <Card>
        <CardHeader>
          <CardTitle>{t("savedSimulations.chatHistoryTitle")}</CardTitle>
          <CardDescription>{t("savedSimulations.chatHistoryDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          {chatSessions.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {t("savedSimulations.noChatHistory")}{" "}
              <Link to="/chat" className="underline text-primary">
                {t("savedSimulations.startChat")}
              </Link>
              .
            </p>
          ) : (
            <div className="space-y-2">
              {chatSessions.map((session) => {
                const isOpen = expandedSession === session.id;
                const created = session.created_at
                  ? new Date(session.created_at).toLocaleDateString()
                  : "";
                return (
                  <div key={session.id} className="rounded-lg border bg-card">
                    <button
                      onClick={() => fetchSessionMessages(session.id)}
                      className="w-full flex items-center justify-between p-3 text-left hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-sm font-medium truncate">
                          {session.title || t("savedSimulations.newChat")}
                        </span>
                        {session.is_flagged && (
                          <span className="text-xs bg-destructive/10 text-destructive px-1.5 py-0.5 rounded">
                            {t("savedSimulations.flagged")}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground shrink-0">
                        {created} {isOpen ? "▲" : "▼"}
                      </span>
                    </button>
                    {isOpen && session.messages && (
                      <div className="px-3 pb-3 space-y-2 border-t bg-muted/30">
                        {session.messages.map((msg, i) => (
                          <div key={i} className="py-1">
                            <span
                              className={`text-xs font-bold uppercase ${
                                msg.role === "user"
                                  ? "text-primary"
                                  : "text-muted-foreground"
                              }`}
                            >
                              {msg.role}
                            </span>
                            <p className="text-sm text-muted-foreground">{msg.content}</p>
                          </div>
                        ))}
                        <div className="flex items-center gap-2 mt-1">
                          <Link to={`/chat?session=${session.id}`}>
                            <Button size="sm" variant="outline">
                              {t("savedSimulations.continueChat")}
                            </Button>
                          </Link>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => deleteChatSession(session.id)}
                            className="text-destructive hover:text-destructive"
                          >
                            {t("savedSimulations.delete")}
                          </Button>
                        </div>
                      </div>
                    )}
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
