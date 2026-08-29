import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { getApiBaseUrl } from "@/utils/env";

const ACTION_OPTIONS = [
  "all",
  "create_user",
  "ban_user",
  "unban_user",
  "change_role",
  "soft_delete_user",
  "update_user_profile",
  "force_password_reset",
  "update_config",
];

export default function AdminLogs() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState("all");
  const [offset, setOffset] = useState(0);
  const [limit] = useState(50);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(offset),
      });
      if (action && action !== "all") params.set("action", action);
      const res = await fetch(`${getApiBaseUrl()}/admin/logs?${params}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await res.json();
      setLogs(data.logs || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [accessToken, offset, action]);

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "—");

  const formatDetails = (details) => {
    if (details == null) return "—";
    if (typeof details === "string") return details;
    if (typeof details === "object") {
      const entries = Object.entries(details)
        .filter(([, v]) => v !== undefined && v !== null)
        .map(([k, v]) => `${k}: ${typeof v === "object" ? JSON.stringify(v) : v}`);
      return entries.length ? entries.join("; ") : "—";
    }
    return String(details);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t("admin.logsPage.title")}</h1>
      </div>

      <div className="flex gap-3 mb-4">
        <select
          value={action}
          onChange={(e) => {
            setAction(e.target.value);
            setOffset(0);
          }}
          className="rounded-md border px-3 py-2 text-sm"
        >
          {ACTION_OPTIONS.map((a) => (
            <option key={a} value={a}>
              {a === "all" ? t("admin.logsPage.allActions") : a}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-muted-foreground">{t("admin.logsPage.loading")}</p>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("admin.logsPage.time")}</TableHead>
                <TableHead>{t("admin.logsPage.admin")}</TableHead>
                <TableHead>{t("admin.logsPage.action")}</TableHead>
                <TableHead>{t("admin.logsPage.target")}</TableHead>
                <TableHead>{t("admin.logsPage.details")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="text-xs whitespace-nowrap">
                    {formatDate(log.created_at)}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground truncate max-w-[140px]">
                    {log.admin_id || t("common.notAvailable")}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="capitalize text-xs">
                      {log.action}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground truncate max-w-[140px]">
                    {log.target_user_id || "—"}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground truncate max-w-[260px]">
                    {formatDetails(log.details)}
                  </TableCell>
                </TableRow>
              ))}
              {logs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="p-6 text-center text-muted-foreground">
                    {t("admin.logsPage.noResults")}
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
          disabled={logs.length < limit || loading}
        >
          {t("common.next")}
        </Button>
      </div>
    </div>
  );
}
