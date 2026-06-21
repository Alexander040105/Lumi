import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useAuth } from "@/hooks/useAuth";
import { getApiBaseUrl } from "@/utils/env";

export default function UserDetailDrawer({ user, open, onClose }) {
  const { accessToken } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  const [detail, setDetail] = useState(null);
  const [sims, setSims] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user || !open) return;
    setActiveTab("overview");
    setDetail(null);
    setSims([]);
    setReport(null);
    fetchDetail();
  }, [user, open]);

  const fetchDetail = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/users/${user.id}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await res.json();
      setDetail(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const fetchSimulations = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/simulations`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const data = await res.json();
      setSims(data.simulations || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const fetchReport = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/reports`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const data = await res.json();
      setReport(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleTab = (tab) => {
    setActiveTab(tab);
    if (tab === "simulations" && sims.length === 0) fetchSimulations();
    if (tab === "reports" && !report) fetchReport();
  };

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "—");

  if (!user) return null;

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader>
          <SheetTitle>User Details</SheetTitle>
        </SheetHeader>

        <div className="mt-4 flex gap-2 border-b pb-2">
          {["overview", "simulations", "reports"].map((tab) => (
            <button
              key={tab}
              onClick={() => handleTab(tab)}
              className={`text-sm px-3 py-1 rounded-md capitalize ${
                activeTab === tab
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {loading && <p className="text-sm text-muted-foreground py-4">Loading...</p>}

        {activeTab === "overview" && detail && (
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Email</span>
              <span className="font-medium">{detail.email || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Name</span>
              <span className="font-medium">{detail.profile?.full_name || "—"}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Role</span>
              <Badge variant="outline" className="capitalize">
                {detail.role}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Plan</span>
              <Badge variant="secondary" className="capitalize">
                {detail.role === "admin" || detail.role === "dev"
                  ? "premium (admin)"
                  : (detail.profile?.plan || "free")}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <Badge
                variant={detail.profile?.is_active ? "default" : "destructive"}
              >
                {detail.profile?.is_active ? "Active" : "Banned"}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Joined</span>
              <span>{formatDate(detail.created_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Last Sign In</span>
              <span>{formatDate(detail.last_sign_in_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Email Confirmed</span>
              <span>{detail.email_confirmed ? "Yes" : "No"}</span>
            </div>
          </div>
        )}

        {activeTab === "simulations" && (
          <div className="mt-4 space-y-2">
            {sims.length === 0 ? (
              <p className="text-sm text-muted-foreground">No saved simulations.</p>
            ) : (
              sims.map((s) => (
                <div key={s.id} className="border rounded-lg p-3 text-sm">
                  <p className="font-medium">{s.name || "Untitled Simulation"}</p>
                  <p className="text-muted-foreground">
                    Municipality: {s.municipality_id || "—"}
                  </p>
                  <p className="text-muted-foreground">{formatDate(s.created_at)}</p>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "reports" && report && (
          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">Total Simulations</p>
                <p className="text-xl font-bold">{report.total_simulations}</p>
              </div>
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">Chat Sessions</p>
                <p className="text-xl font-bold">{report.total_chat_sessions}</p>
              </div>
            </div>
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Peak Municipality</span>
                <span className="font-medium">
                  {report.peak_municipality_id || "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Active</span>
                <span>{formatDate(report.last_active)}</span>
              </div>
            </div>
            {report.recent_simulations?.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Recent Simulations</p>
                <div className="space-y-2">
                  {report.recent_simulations.map((s) => (
                    <div key={s.id} className="border rounded-lg p-2 text-sm">
                      <p className="font-medium">{s.name || "Untitled"}</p>
                      <p className="text-muted-foreground text-xs">
                        {formatDate(s.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
