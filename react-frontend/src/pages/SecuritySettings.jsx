import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { supabase } from "@/services/supabaseClient";
import { getApiBaseUrl } from "@/utils/env";

export default function SecuritySettings() {
  const { user, accessToken, signOut, refreshProfile } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [deletePassword, setDeletePassword] = useState("");
  const [savingEmail, setSavingEmail] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [ecosimAutosave, setEcosimAutosave] = useState(true);
  const [savingAutosave, setSavingAutosave] = useState(false);

  useEffect(() => {
    if (!user?.id) return;
    supabase
      .from("profiles")
      .select("ecosim_autosave")
      .eq("id", user.id)
      .single()
      .then(({ data }) => {
        if (data?.ecosim_autosave != null) setEcosimAutosave(data.ecosim_autosave);
      });
  }, [user?.id]);

  const handleAutosaveChange = async (checked) => {
    setEcosimAutosave(checked);
    setSavingAutosave(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ ecosim_autosave: checked }),
      });
      if (!res.ok) throw new Error(t("security.preferences.saveFailed"));
      toast.success(t("security.preferences.saved"));
      refreshProfile?.();
    } catch (err) {
      setEcosimAutosave(!checked);
      toast.error(err.message || t("security.preferences.saveFailed"));
    } finally {
      setSavingAutosave(false);
    }
  };

  const reauthenticate = async (password) => {
    const { error } = await supabase.auth.signInWithPassword({
      email: user?.email || "",
      password,
    });
    return error;
  };

  const handleChangeEmail = async (e) => {
    e.preventDefault();
    if (!newEmail.trim()) {
      toast.error(t("security.changeEmail.enterEmail"));
      return;
    }
    setSavingEmail(true);
    try {
      const err = await reauthenticate(currentPassword);
      if (err) throw err;

      const { error } = await supabase.auth.updateUser({ email: newEmail.trim() });
      if (error) throw error;

      toast.success(t("security.changeEmail.sent"));
      setNewEmail("");
      setCurrentPassword("");
    } catch (err) {
      toast.error(err.message || t("security.changeEmail.failed"));
    } finally {
      setSavingEmail(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPassword.length < 6) {
      toast.error(t("security.changePassword.tooShort"));
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error(t("security.changePassword.mismatch"));
      return;
    }
    setSavingPassword(true);
    try {
      const err = await reauthenticate(currentPassword);
      if (err) throw err;

      const { error } = await supabase.auth.updateUser({ password: newPassword });
      if (error) throw error;

      toast.success(t("security.changePassword.success"));
      setNewPassword("");
      setConfirmPassword("");
      setCurrentPassword("");
    } catch (err) {
      toast.error(err.message || t("security.changePassword.failed"));
    } finally {
      setSavingPassword(false);
    }
  };

  const handleDeleteAccount = async (e) => {
    e.preventDefault();
    if (!deletePassword) {
      toast.error(t("security.deleteAccount.confirmPassword"));
      return;
    }
    if (!window.confirm(t("security.deleteAccount.confirm"))) return;
    setDeleting(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: user?.email || "",
        password: deletePassword,
      });
      if (error) throw error;

      const res = await fetch(`${getApiBaseUrl()}/protected/me`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(t("security.deleteAccount.failed"));

      toast.success(t("security.deleteAccount.success"));
      await signOut();
      navigate("/");
    } catch (err) {
      toast.error(err.message || t("security.deleteAccount.failed"));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <section className="page-container max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">{t("security.title")}</h1>

      <Card>
        <CardHeader>
          <CardTitle>{t("security.changeEmail.title")}</CardTitle>
          <CardDescription>
            {t("security.changeEmail.description")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangeEmail} className="space-y-4">
            <div>
              <label htmlFor="security-email-current" className="text-sm font-medium">
                {t("security.currentPassword")}
              </label>
              <Input
                id="security-email-current"
                type="password"
                autoComplete="current-password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>
            <div>
              <label htmlFor="security-new-email" className="text-sm font-medium">
                {t("security.changeEmail.newEmail")}
              </label>
              <Input
                id="security-new-email"
                type="email"
                autoComplete="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                required
              />
            </div>
            <Button type="submit" disabled={savingEmail}>
              {savingEmail ? t("security.changeEmail.submitting") : t("security.changeEmail.submit")}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("security.changePassword.title")}</CardTitle>
          <CardDescription>
            {t("security.changePassword.description")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label htmlFor="security-pw-current" className="text-sm font-medium">
                {t("security.currentPassword")}
              </label>
              <Input
                id="security-pw-current"
                type="password"
                autoComplete="current-password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>
            <div>
              <label htmlFor="security-pw-new" className="text-sm font-medium">
                {t("security.changePassword.newPassword")}
              </label>
              <Input
                id="security-pw-new"
                type="password"
                autoComplete="new-password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
            <div>
              <label htmlFor="security-pw-confirm" className="text-sm font-medium">
                {t("security.changePassword.confirm")}
              </label>
              <Input
                id="security-pw-confirm"
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
            <Button type="submit" disabled={savingPassword}>
              {savingPassword ? t("security.changePassword.submitting") : t("security.changePassword.submit")}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("security.mfa.title")}</CardTitle>
          <CardDescription>
            {t("security.mfa.description")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            className="w-full"
            onClick={() => navigate("/mfa")}
          >
            {t("security.mfa.enable")}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("security.preferences.title")}</CardTitle>
          <CardDescription>
            {t("security.preferences.description")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-start gap-2">
            <input
              type="checkbox"
              id="ecosim-autosave"
              checked={ecosimAutosave}
              onChange={(e) => handleAutosaveChange(e.target.checked)}
              disabled={savingAutosave}
              className="mt-0.5 h-4 w-4 rounded border-input text-primary accent-primary"
            />
            <div>
              <label htmlFor="ecosim-autosave" className="text-sm font-medium">{t("security.preferences.autosaveLabel")}</label>
              <p className="text-xs text-muted-foreground">{t("security.preferences.autosaveHint")}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">{t("security.deleteAccount.title")}</CardTitle>
          <CardDescription>
            {t("security.deleteAccount.description")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleDeleteAccount} className="space-y-4">
            <div>
              <label htmlFor="security-delete-pw" className="text-sm font-medium">
                {t("security.currentPassword")}
              </label>
              <Input
                id="security-delete-pw"
                type="password"
                autoComplete="current-password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" variant="destructive" disabled={deleting}>
              {deleting ? t("security.deleteAccount.submitting") : t("security.deleteAccount.submit")}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
