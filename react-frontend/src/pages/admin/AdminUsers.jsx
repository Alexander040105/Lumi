import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import CreateUserModal from "@/components/admin/CreateUserModal";
import UserDetailDrawer from "@/components/admin/UserDetailDrawer";
import { useAuth } from "@/hooks/useAuth";
import { getApiBaseUrl } from "@/utils/env";

export default function AdminUsers() {
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
        <h1 className="text-2xl font-bold">User Management</h1>
        <Button onClick={() => setCreateOpen(true)}>Create User</Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <Input
          placeholder="Search by email or name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">All Roles</option>
          <option value="user">User</option>
          <option value="admin">Admin</option>
          <option value="dev">Dev</option>
        </select>
        <select
          value={filterPlan}
          onChange={(e) => setFilterPlan(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">All Plans</option>
          <option value="free">Free</option>
          <option value="premium">Premium</option>
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="banned">Banned</option>
        </select>
      </div>

      {loading ? (
        <p className="text-muted-foreground">Loading users...</p>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted">
              <tr>
                <th className="text-left p-3">User</th>
                <th className="text-left p-3">Email</th>
                <th className="text-left p-3">Role</th>
                <th className="text-left p-3">Plan</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Joined</th>
                <th className="text-left p-3">Actions</th>
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
                      <span>{u.full_name || "—"}</span>
                    </div>
                  </td>
                  <td className="p-3 text-xs text-muted-foreground truncate max-w-[160px]">
                    {u.email || "—"}
                  </td>
                  <td className="p-3">
                    <Badge variant="outline" className="capitalize">
                      {u.role || "user"}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge variant="secondary" className="capitalize">
                      {u.role === "admin" || u.role === "dev" ? "premium" : (u.plan || "free")}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge
                      variant={u.is_active ? "default" : "destructive"}
                      className="text-xs"
                    >
                      {u.is_active ? "Active" : "Banned"}
                    </Badge>
                  </td>
                  <td className="p-3">{formatDate(u.created_at)}</td>
                  <td className="p-3">
                    <div className="flex flex-wrap gap-1">
                      <Button size="sm" variant="outline" onClick={() => openDetail(u)}>
                        View
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
                        {u.is_active ? "Ban" : "Unban"}
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
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                        <option value="dev">Dev</option>
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
                        <option value="free">Free</option>
                        <option value="premium">Premium</option>
                      </select>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-destructive"
                        onClick={() => {
                          if (confirm("Soft-delete this user? They will be banned and anonymised.")) {
                            handleAction(
                              `${getApiBaseUrl()}/admin/users/${u.id}`,
                              "DELETE"
                            );
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </td>
                </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-muted-foreground">
                    No users match your filters.
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
