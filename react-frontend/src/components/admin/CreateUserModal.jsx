import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { getApiBaseUrl } from "@/utils/env";

export default function CreateUserModal({ open, onClose, onCreated }) {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("user");
  const [plan, setPlan] = useState("free");

  // Admins are always premium
  const isAdminRole = role === "admin" || role === "dev";
  const displayPlan = isAdminRole ? "premium" : plan;
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const reset = () => {
    setEmail("");
    setFullName("");
    setRole("user");
    setPlan("free");
    setResult(null);
    setError("");
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ email, full_name: fullName, role, plan }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || t("admin.createUserModal.createUser"));
      setResult(data);
      onCreated?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("admin.createUserModal.title")}</DialogTitle>
          <DialogDescription>
            {t("admin.createUserModal.description")}
          </DialogDescription>
        </DialogHeader>

        {result ? (
          <div className="space-y-4">
            <div className="rounded-lg bg-green-50 p-4 text-sm text-green-700">
              <p className="font-semibold">{t("admin.createUserModal.userCreated")}</p>
              <p className="mt-1">{t("admin.createUserModal.email")}: {result.email}</p>
              <p className="mt-1">{t("admin.createUserModal.role")}: {result.role}</p>
              <p className="mt-1">{t("admin.createUserModal.plan")}: {result.plan}</p>
              <p className="mt-2 break-all">
                <span className="font-semibold">{t("admin.createUserModal.tempPassword")}:</span>{" "}
                {result.temp_password}
              </p>
            </div>
            <Button onClick={reset} className="w-full">
              {t("admin.createUserModal.createAnother")}
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">{t("admin.createUserModal.emailLabel")}</label>
              <Input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("admin.createUserModal.emailPlaceholder")}
              />
            </div>
            <div>
              <label className="text-sm font-medium">{t("admin.createUserModal.fullNameLabel")}</label>
              <Input
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder={t("admin.createUserModal.fullNamePlaceholder")}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">{t("admin.createUserModal.roleLabel")}</label>
                <select
                  value={role}
                  onChange={(e) => {
                    const newRole = e.target.value;
                    setRole(newRole);
                    if (newRole === "admin" || newRole === "dev") {
                      setPlan("premium");
                    }
                  }}
                  className="w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="user">{t("admin.usersPage.roleUser")}</option>
                  <option value="admin">{t("admin.usersPage.roleAdmin")}</option>
                  <option value="dev">{t("admin.usersPage.roleDev")}</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">{t("admin.createUserModal.planLabel")}</label>
                <select
                  value={displayPlan}
                  onChange={(e) => setPlan(e.target.value)}
                  disabled={isAdminRole}
                  className="w-full rounded-md border px-3 py-2 text-sm disabled:opacity-50"
                >
                  <option value="free">{t("admin.usersPage.planFree")}</option>
                  <option value="premium">{t("admin.usersPage.planPremium")}</option>
                </select>
                {isAdminRole && (
                  <p className="text-xs text-muted-foreground mt-1">{t("admin.createUserModal.adminPremium")}</p>
                )}
              </div>
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={handleClose}>
                {t("admin.createUserModal.cancel")}
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? t("admin.createUserModal.creating") : t("admin.createUserModal.createUser")}
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
