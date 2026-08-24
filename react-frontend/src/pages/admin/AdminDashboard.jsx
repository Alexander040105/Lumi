import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Users, BarChart3, Settings, Activity, ScrollText, LayoutDashboard } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/services/supabaseClient";
import { useI18n } from "@/i18n";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminDashboard() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [stats, setStats] = useState({ users: 0, simulations: 0, loading: true });

  useEffect(() => {
    let mounted = true;
    const fetchStats = async () => {
      try {
        const [{ count: users }, { count: simulations }] = await Promise.all([
          supabase.from("profiles").select("*", { count: "exact", head: true }),
          supabase.from("saved_simulations").select("*", { count: "exact", head: true }),
        ]);
        if (mounted) setStats({ users: users || 0, simulations: simulations || 0, loading: false });
      } catch {
        if (mounted) setStats({ users: 0, simulations: 0, loading: false });
      }
    };
    fetchStats();
    return () => {
      mounted = false;
    };
  }, []);

  const adminName = user?.user_metadata?.full_name || user?.email || t("common.user");

  const links = [
    {
      to: "/admin/users",
      icon: Users,
      title: t("admin.users"),
      desc: t("admin.usersDesc"),
    },
    {
      to: "/admin/analytics",
      icon: BarChart3,
      title: t("admin.analytics"),
      desc: t("admin.analyticsDesc"),
    },
    {
      to: "/admin/config",
      icon: Settings,
      title: t("admin.config"),
      desc: t("admin.configDesc"),
    },
    {
      to: "/admin/usage",
      icon: Activity,
      title: t("admin.usagePage.title"),
      desc: t("admin.usagePage.description"),
    },
    {
      to: "/admin/logs",
      icon: ScrollText,
      title: t("admin.logsPage.title"),
      desc: t("admin.logsPage.description"),
    },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <LayoutDashboard className="h-6 w-6 text-primary" />
          {t("admin.portal")}
        </h1>
        <p className="text-muted-foreground mt-1">
          {t("admin.welcome")} &mdash; {t("admin.summary")}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("common.user", { count: stats.users })}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.loading ? "..." : t("admin.usersCount", { count: stats.users })}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("nav.savedSims")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.loading ? "..." : t("admin.simsCount", { count: stats.simulations })}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="group flex items-start gap-4 p-6 border rounded-lg bg-card hover:bg-muted transition-colors"
          >
            <div className="p-3 rounded-lg bg-primary/10 text-primary">
              <link.icon className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-semibold group-hover:text-primary transition-colors">
                {link.title}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">{link.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      <p className="text-sm text-muted-foreground">
        {t("common.user")}: <span className="font-medium text-foreground">{adminName}</span>
      </p>
    </div>
  );
}
