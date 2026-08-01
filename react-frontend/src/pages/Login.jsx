import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
import { supabase } from "../services/supabaseClient";
import { useI18n } from "../i18n";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function Login() {
  const { t } = useI18n();
  const { session, signInWithProvider, signInWithPassword, signUp, resetPassword } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const redirectTo = location.state?.from?.pathname || "/dashboard";
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [signupStatus, setSignupStatus] = useState(null); // 'confirm' | 'auto' | null

  // MFA state
  const [mfaRequired, setMfaRequired] = useState(null); // null = checking, false = no mfa, true = mfa needed
  const [mfaFactorId, setMfaFactorId] = useState(null);
  const [mfaCode, setMfaCode] = useState("");
  const [verifying, setVerifying] = useState(false);

  const checkMfa = async () => {
    try {
      // Supabase MFA may not be available in all projects; fail open (treat as no MFA)
      if (!supabase.auth.mfa || typeof supabase.auth.mfa.getAuthenticatorAssuranceLevel !== "function") {
        setMfaRequired(false);
        return;
      }

      const { data: aal, error: aalError } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
      if (aalError) throw aalError;

      if (aal?.nextLevel === "aal2" && aal?.currentLevel === "aal1") {
        const { data: factors, error: fError } = await supabase.auth.mfa.listFactors();
        if (fError) throw fError;

        const factor =
          factors?.totp?.find((f) => f.status === "verified") ||
          factors?.all?.find((f) => f.status === "verified");

        if (factor) {
          setMfaFactorId(factor.id);
          setMfaRequired(true);
          return;
        }
      }
    } catch (error) {
      // MFA check failed (e.g., not enabled or network) — do not block the user
      console.error("[Login] MFA check failed:", error);
    }
    setMfaRequired(false);
  };

  useEffect(() => {
    if (session) {
      checkMfa();
    } else {
      setMfaRequired(null);
    }
  }, [session]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setSignupStatus(null);

    try {
      if (mode === "signup" && password !== confirmPassword) {
        toast.error(t("mfa.passwordsDoNotMatch"));
        return;
      }

      if (mode === "login") {
        const { error } = await signInWithPassword(email, password);
        if (error) throw error;
        // Session will trigger useEffect, which calls checkMfa.
      }

      if (mode === "signup") {
        const result = await signUp(email, password);
        if (result.error) throw result.error;

        if (result.confirmationRequired) {
          setSignupStatus("confirm");
          toast.success(t("login.accountCreated"));
        } else {
          setSignupStatus("auto");
          toast.success(t("login.accountCreated"));
        }
      }

      if (mode === "reset") {
        const { error } = await resetPassword(email);
        if (error) throw error;
        toast.success(t("mfa.resetSent"));
      }
    } catch (error) {
      toast.error(error?.message || t("login.error"));
    } finally {
      setBusy(false);
    }
  };

  const handleVerifyMfa = async (event) => {
    event.preventDefault();
    if (!mfaFactorId || !mfaCode) return;

    setVerifying(true);
    try {
      const { data: challenge, error: challengeError } = await supabase.auth.mfa.challenge({
        factorId: mfaFactorId,
      });
      if (challengeError) throw challengeError;

      const { error } = await supabase.auth.mfa.verify({
        factorId: mfaFactorId,
        challengeId: challenge.id,
        code: mfaCode.replace(/\s/g, ""),
      });
      if (error) throw error;

      toast.success(t("mfa.verified"));
      navigate(redirectTo, { replace: true });
    } catch (error) {
      toast.error(error?.message || t("mfa.verifyError"));
    } finally {
      setVerifying(false);
    }
  };

  const resendConfirmation = async () => {
    setBusy(true);
    try {
      const { error } = await supabase.auth.resend({
        type: "signup",
        email,
      });
      if (error) throw error;
      toast.success(t("mfa.confirmResent"));
    } catch (error) {
      toast.error(error?.message || t("mfa.resendError"));
    } finally {
      setBusy(false);
    }
  };

  // Fully authenticated with no pending MFA
  if (session && mfaRequired === false) {
    return <Navigate to={redirectTo} replace />;
  }

  // Authenticated but waiting for MFA verification
  if (session && mfaRequired === true) {
    return (
      <section className="page-container">
        <Card className="mx-auto max-w-md">
          <CardHeader>
            <CardTitle>{t("mfa.verifyTitle")}</CardTitle>
            <CardDescription>{t("mfa.verifyDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleVerifyMfa} className="space-y-3">
              <Input
                value={mfaCode}
                onChange={(event) => setMfaCode(event.target.value)}
                placeholder={t("mfa.codePlaceholder")}
                maxLength={10}
                autoComplete="one-time-code"
                inputMode="numeric"
              />
              <Button className="w-full" type="submit" disabled={verifying || !mfaCode}>
                {verifying ? t("common.loading") : t("mfa.verify")}
              </Button>
            </form>
          </CardContent>
        </Card>
      </section>
    );
  }

  // Session present but MFA state is still being checked
  if (session && mfaRequired === null) {
    return (
      <section className="page-container flex items-center justify-center">
        <p className="text-muted-foreground">{t("common.loading")}</p>
      </section>
    );
  }

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>{t("login.welcomeBack")}</CardTitle>
          <CardDescription>{t("login.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button
              type="button"
              variant={mode === "login" ? "default" : "outline"}
              className="w-full"
              onClick={() => setMode("login")}
            >
              {t("login.signIn")}
            </Button>
            <Button
              type="button"
              variant={mode === "signup" ? "default" : "outline"}
              className="w-full"
              onClick={() => setMode("signup")}
            >
              {t("login.signUp")}
            </Button>
          </div>

          <form className="space-y-3" onSubmit={handleSubmit}>
            <Input
              type="email"
              placeholder={t("login.email")}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
            {mode !== "reset" && (
              <Input
                type="password"
                placeholder={t("login.password")}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            )}
            {mode === "signup" && (
              <Input
                type="password"
                placeholder={t("login.confirmPassword")}
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
              />
            )}

            <Button className="w-full" type="submit" disabled={busy}>
              {mode === "login" && t("login.signIn")}
              {mode === "signup" && t("login.createAccount")}
              {mode === "reset" && t("login.sendResetEmail")}
            </Button>

            {mode === "signup" && signupStatus === "confirm" && (
              <div className="rounded-md bg-warning/10 p-3 text-sm text-foreground border border-warning/20">
                <p className="font-medium">{t("login.checkYourEmail")}</p>
                <p className="mt-1">{t("login.confirmationSentDesc", { email })}</p>
                <Button
                  type="button"
                  variant="link"
                  className="h-auto p-0 text-primary underline"
                  onClick={resendConfirmation}
                  disabled={busy}
                >
                  {t("login.resend")}
                </Button>
              </div>
            )}

            {mode === "signup" && signupStatus === "auto" && (
              <div className="rounded-md bg-secondary p-3 text-sm text-foreground border border-border">
                <p className="font-medium">{t("login.accountCreated")}</p>
                <p className="mt-1">{t("login.noEmailConfirmation")}</p>
              </div>
            )}
          </form>

          <div className="flex items-center justify-between text-sm">
            <Button type="button" variant="ghost" onClick={() => setMode("reset")}>
              {t("login.forgotPassword")}
            </Button>
            {mode === "reset" && (
              <Button type="button" variant="ghost" onClick={() => setMode("login")}>
                {t("login.backToSignIn")}
              </Button>
            )}
          </div>

          <div className="space-y-2">
            <Button className="w-full" variant="outline" onClick={() => signInWithProvider("google")}>
              {t("login.continueWithGoogle")}
            </Button>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
