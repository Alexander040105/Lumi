import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/services/supabaseClient";
import { getApiBaseUrl } from "@/utils/env";

export default function SecuritySettings() {
  const { user, accessToken, signOut, refreshProfile } = useAuth();
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
      if (!res.ok) throw new Error("Could not save preference");
      toast.success("Preference saved");
      refreshProfile?.();
    } catch (err) {
      setEcosimAutosave(!checked);
      toast.error(err.message || "Could not save preference");
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
      toast.error("Enter a new email address");
      return;
    }
    setSavingEmail(true);
    try {
      const err = await reauthenticate(currentPassword);
      if (err) throw err;

      const { error } = await supabase.auth.updateUser({ email: newEmail.trim() });
      if (error) throw error;

      toast.success("A confirmation email has been sent to the new address.");
      setNewEmail("");
      setCurrentPassword("");
    } catch (err) {
      toast.error(err.message || "Could not change email");
    } finally {
      setSavingEmail(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPassword.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    setSavingPassword(true);
    try {
      const err = await reauthenticate(currentPassword);
      if (err) throw err;

      const { error } = await supabase.auth.updateUser({ password: newPassword });
      if (error) throw error;

      toast.success("Password updated. Use your new password to sign in next time.");
      setNewPassword("");
      setConfirmPassword("");
      setCurrentPassword("");
    } catch (err) {
      toast.error(err.message || "Could not change password");
    } finally {
      setSavingPassword(false);
    }
  };

  const handleDeleteAccount = async (e) => {
    e.preventDefault();
    if (!deletePassword) {
      toast.error("Enter your current password to confirm");
      return;
    }
    if (!window.confirm("Permanently delete your account? This cannot be undone.")) return;
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
      if (!res.ok) throw new Error("Delete failed");

      toast.success("Account deleted");
      await signOut();
      navigate("/");
    } catch (err) {
      toast.error(err.message || "Could not delete account");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <section className="page-container max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Security settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>Change email</CardTitle>
          <CardDescription>
            Confirm your current password, then enter the new email. A confirmation link will be sent to the new address.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangeEmail} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Current password</label>
              <Input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium">New email</label>
              <Input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                required
              />
            </div>
            <Button type="submit" disabled={savingEmail}>
              {savingEmail ? "Sending..." : "Change email"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Change password</CardTitle>
          <CardDescription>
            Confirm your current password, then enter a new password.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Current password</label>
              <Input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium">New password</label>
              <Input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Confirm new password</label>
              <Input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
            <Button type="submit" disabled={savingPassword}>
              {savingPassword ? "Updating..." : "Update password"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Two-factor authentication</CardTitle>
          <CardDescription>
            Add an extra layer of security to your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            className="w-full"
            onClick={() => navigate("/mfa")}
          >
            Enable two-factor authentication
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
          <CardDescription>
            Control how EcoSim behaves for your account.
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
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-primary accent-primary"
            />
            <div>
              <label htmlFor="ecosim-autosave" className="text-sm font-medium">Automatically save my EcoSim runs</label>
              <p className="text-xs text-muted-foreground">When on, each EcoSim run is saved to your account automatically.</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Delete account</CardTitle>
          <CardDescription>
            This will permanently delete your LUMI account and all associated data. This action cannot be undone.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleDeleteAccount} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Current password</label>
              <Input
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" variant="destructive" disabled={deleting}>
              {deleting ? "Deleting..." : "Delete account"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
