import { useState } from "react";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
import { useI18n } from "../i18n";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function ResetPassword() {
  const { t } = useI18n();
  const { session, updatePassword } = useAuth();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      toast.error(t("resetPassword.passwordsDoNotMatch"));
      return;
    }

    setBusy(true);
    try {
      const { error } = await updatePassword(password);
      if (error) throw error;
      toast.success(t("resetPassword.success"));
    } catch (error) {
      toast.error(error?.message || t("resetPassword.error"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>{t("resetPassword.title")}</CardTitle>
          <CardDescription>{t("resetPassword.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!session && (
            <p className="text-sm text-muted-foreground">
              {t("resetPassword.noSession")}
            </p>
          )}
          <form className="space-y-3" onSubmit={handleSubmit}>
            <Input
              type="password"
              placeholder={t("resetPassword.newPasswordPlaceholder")}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={6}
            />
            <Input
              type="password"
              placeholder={t("resetPassword.confirmPasswordPlaceholder")}
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              minLength={6}
            />
            <Button className="w-full" type="submit" disabled={busy || !session}>
              {t("resetPassword.updatePassword")}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
