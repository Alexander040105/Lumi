import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import UserDetailDrawer from "@/components/admin/UserDetailDrawer";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { getApiBaseUrl } from "@/utils/env";

export default function AdminUsage() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [limit] = useState(50);
  const [selectedUser, setSelectedUser] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchUsage = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(offset),
      });
      if (search.trim()) params.set("search", search.trim());
      const res = await fetch(`${getApiBaseUrl()}/admin/usage?${params}`, {
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
    fetchUsage();
  }, [accessToken, offset]);

  const handleSearch = (e) => {
    e.preventDefault();
    setOffset(0);
    fetchUsage();
  };

  const openDetail = (u) => {
    setSelectedUser(u);
    setDrawerOpen(true);
  };

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "—");

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t("admin.usagePage.title")}</h1>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3 mb-4">
        <Input
          placeholder={t("admin.usagePage.searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
        <Button type="submit" variant="outline" disabled={loading}>
          {t("common.search")}
        </Button>
      </form>

      {loading ? (
        <p className="text-muted-foreground">{t("admin.usagePage.loading")}</p>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("admin.usersPage.columns.user")}</TableHead>
                <TableHead>{t("admin.usersPage.columns.email")}</TableHead>
                <TableHead>{t("admin.usersPage.columns.role")}</TableHead>
                <TableHead>{t("admin.usersPage.columns.status")}</TableHead>
                <TableHead className="text-right">{t("admin.usagePage.totalSims")}</TableHead>
                <TableHead className="text-right">{t("admin.usagePage.thisMonthSims")}</TableHead>
                <TableHead className="text-right">{t("admin.usagePage.totalEcosim")}</TableHead>
                <TableHead className="text-right">{t("admin.usagePage.thisMonthEcosim")}</TableHead>
                <TableHead>{t("admin.userDetail.lastActive")}</TableHead>
                <TableHead>{t("admin.usersPage.columns.actions")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((u) => (
                <TableRow key={u.id}>
                  <TableCell>{u.full_name || t("common.notAvailable")}</TableCell>
                  <TableCell className="text-xs text-muted-foreground truncate max-w-[160px]">
                    {u.email || t("common.notAvailable")}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="capitalize">
                      {u.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={u.is_active ? "default" : "destructive"}
                      className="text-xs"
                    >
                      {u.is_active ? t("admin.usersPage.statusActive") : t("admin.usersPage.statusBanned")}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">{u.total_simulations}</TableCell>
                  <TableCell className="text-right">{u.simulations_this_month}</TableCell>
                  <TableCell className="text-right">{u.total_ecosim}</TableCell>
                  <TableCell className="text-right">{u.ecosim_this_month}</TableCell>
                  <TableCell className="text-xs">{formatDate(u.last_active)}</TableCell>
                  <TableCell>
                    <Button size="sm" variant="outline" onClick={() => openDetail(u)}>
                      {t("admin.usersPage.view")}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {users.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9} className="p-6 text-center text-muted-foreground">
                    {t("admin.usagePage.noResults")}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}

      <div className="flex items-center justify-between mt-4">
        <Button
          variant="outline"
          onClick={() => setOffset((o) => Math.max(0, o - limit))}
          disabled={offset === 0 || loading}
        >
          {t("common.back")}
        </Button>
        <Button
          variant="outline"
          onClick={() => setOffset((o) => o + limit)}
          disabled={users.length < limit || loading}
        >
          {t("common.next")}
        </Button>
      </div>

      <UserDetailDrawer
        user={selectedUser}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}
