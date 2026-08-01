import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import CreateUserModal from "@/components/admin/CreateUserModal";
import UserDetailDrawer from "@/components/admin/UserDetailDrawer";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { getApiBaseUrl } from "@/utils/env";

export default function AdminUsers() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterRole, setFilterRole] = useState("all");
  const [filterPlan, setFilterPlan] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/users`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await res.json();
      setUsers(data.users || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [accessToken]);

  const filtered = useMemo(() => {
    return users.filter((u) => {
      const matchesSearch =
        (u.email || "").toLowerCase().includes(search.toLowerCase()) ||
        (u.full_name || "").toLowerCase().includes(search.toLowerCase());
      const matchesRole = filterRole === "all" || u.role === filterRole;
      const matchesPlan = filterPlan === "all" || u.plan === filterPlan;
      const matchesStatus =
        filterStatus === "all"
          ? true
          : filterStatus === "active"
          ? u.is_active
          : !u.is_active;
      return matchesSearch && matchesRole && matchesPlan && matchesStatus;
    });
  }, [users, search, filterRole, filterPlan, filterStatus]);

  const handleAction = async (url, method = "POST", body = null) => {
    try {
      await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: body ? JSON.stringify(body) : undefined,
      });
      fetchUsers();
    } catch {
      // ignore
    }
  };

  const openDetail = (u) => {
    setSelectedUser(u);
    setDrawerOpen(true);
  };

  const formatDate = (d) => (d ? new Date(d).toLocaleDateString() : "—");

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t("admin.usersPage.title")}</h1>
        <Button onClick={() => setCreateOpen(true)}>{t("admin.usersPage.createUser")}</Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <Input
          placeholder={t("admin.usersPage.searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">{t("admin.usersPage.allRoles")}</option>
          <option value="user">{t("admin.usersPage.roleUser")}</option>
          <option value="admin">{t("admin.usersPage.roleAdmin")}</option>
          <option value="dev">{t("admin.usersPage.roleDev")}</option>
        </select>
        <select
          value={filterPlan}
          onChange={(e) => setFilterPlan(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">{t("admin.usersPage.allPlans")}</option>
          <option value="free">{t("admin.usersPage.planFree")}</option>
          <option value="premium">{t("admin.usersPage.planPremium")}</option>
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">{t("admin.usersPage.allStatus")}</option>
          <option value="active">{t("admin.usersPage.statusActive")}</option>
          <option value="banned">{t("admin.usersPage.statusBanned")}</option>
        </select>
      </div>

      {loading ? (
        <p className="text-muted-foreground">{t("admin.usersPage.loading")}</p>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted">
              <tr>
                <th className="text-left p-3">{t("admin.usersPage.columns.user")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.email")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.role")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.plan")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.status")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.joined")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => {
                const initials = (u.full_name || u.email || "U")
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .slice(0, 2)
                  .toUpperCase();
                return (
                <tr key={u.id} className="border-t hover:bg-muted/50">
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      {u.avatar_url ? (
                        <img
                          src={u.avatar_url}
                          alt=""
                          className="h-8 w-8 rounded-full object-cover border"
                          onError={(e) => { e.target.style.display = "none"; }}
                        />
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
                          {initials}
                        </div>
                      )}
                      <span>{u.full_name || t("common.notAvailable")}</span>
                    </div>
                  </td>
                  <td className="p-3 text-xs text-muted-foreground truncate max-w-[160px]">
                    {u.email || t("common.notAvailable")}
                  </td>
                  <td className="p-3">
                    <Badge variant="outline" className="capitalize">
                      {u.role === "admin" ? t("admin.usersPage.roleAdmin") : u.role === "dev" ? t("admin.usersPage.roleDev") : t("admin.usersPage.roleUser")}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge variant="secondary" className="capitalize">
                      {u.role === "admin" || u.role === "dev" ? t("admin.usersPage.planPremium") : (u.plan === "premium" ? t("admin.usersPage.planPremium") : t("admin.usersPage.planFree"))}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge
                      variant={u.is_active ? "default" : "destructive"}
                      className="text-xs"
                    >
                      {u.is_active ? t("admin.usersPage.statusActive") : t("admin.usersPage.statusBanned")}
                    </Badge>
                  </td>
                  <td className="p-3">{formatDate(u.created_at)}</td>
                  <td className="p-3">
                    <div className="flex flex-wrap gap-1">
                      <Button size="sm" variant="outline" onClick={() => openDetail(u)}>
                        {t("admin.usersPage.view")}
                      </Button>
                      <Button
                        size="sm"
                        variant={u.is_active ? "destructive" : "default"}
                        onClick={() =>
                          handleAction(
                            `${getApiBaseUrl()}/admin/users/${u.id}/ban`
                          )
                        }
                      >
                        {u.is_active ? t("admin.usersPage.ban") : t("admin.usersPage.unban")}
                      </Button>
                      <select
                        value={u.role}
                        onChange={(e) =>
                          handleAction(
                            `${getApiBaseUrl()}/admin/users/${u.id}/role`,
                            "PUT",
                            { role: e.target.value }
                          )
                        }
                        className="rounded-md border px-2 py-1 text-xs"
                      >
                        <option value="user">{t("admin.usersPage.roleUser")}</option>
                        <option value="admin">{t("admin.usersPage.roleAdmin")}</option>
                        <option value="dev">{t("admin.usersPage.roleDev")}</option>
                      </select>
                      <select
                        value={u.plan}
                        onChange={(e) =>
                          handleAction(
                            `${getApiBaseUrl()}/admin/users/${u.id}/plan`,
                            "PUT",
                            { plan: e.target.value }
                          )
                        }
                        className="rounded-md border px-2 py-1 text-xs"
                      >
                        <option value="free">{t("admin.usersPage.planFree")}</option>
                        <option value="premium">{t("admin.usersPage.planPremium")}</option>
                      </select>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-destructive"
                        onClick={() => {
                          if (confirm(t("admin.usersPage.deleteConfirm"))) {
                            handleAction(
                              `${getApiBaseUrl()}/admin/users/${u.id}`,
                              "DELETE"
                            );
                          }
                        }}
                      >
                        {t("admin.usersPage.delete")}
                      </Button>
                    </div>
                  </td>
                </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-muted-foreground">
                    {t("admin.usersPage.noResults")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <CreateUserModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={fetchUsers}
      />

      <UserDetailDrawer
        user={selectedUser}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}
