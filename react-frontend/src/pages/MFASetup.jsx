import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { toast } from "sonner";
import { Shield, ShieldCheck, ShieldOff } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/services/supabaseClient";
import { useI18n } from "@/i18n";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function MFASetup() {
  const { t } = useI18n();
  const { user } = useAuth();

  const [factors, setFactors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [enrollment, setEnrollment] = useState(null); // { id, qr_code, secret }
  const [code, setCode] = useState("");

  const fetchFactors = async () => {
    try {
      const { data, error } = await supabase.auth.mfa.listFactors();
      if (error) throw error;
      setFactors(data?.all || []);
    } catch (err) {
      toast.error(t("mfa.factorError") + ": " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFactors();
  }, []);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const handleEnroll = async () => {
    setEnrolling(true);
    try {
      const { data, error } = await supabase.auth.mfa.enroll({
        factorType: "totp",
        friendlyName: "LUMI Authenticator",
      });
      if (error) throw error;
      setEnrollment(data);
    } catch (err) {
      toast.error(t("mfa.enrollError") + ": " + (err.message || err));
    } finally {
      setEnrolling(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!enrollment || !code) return;
    setVerifying(true);
    try {
      const { data: challenge, error: challengeError } = await supabase.auth.mfa.challenge({
        factorId: enrollment.id,
      });
      if (challengeError) throw challengeError;

      const { data, error } = await supabase.auth.mfa.verify({
        factorId: enrollment.id,
        challengeId: challenge.id,
        code: code.replace(/\s/g, ""),
      });
      if (error) throw error;

      toast.success(t("mfa.enabled"));
      setEnrollment(null);
      setCode("");
      await fetchFactors();
      if (data.session) {
        // The session is already refreshed by the MFA verify event in most cases,
        // but we can help the AuthContext along.
        supabase.auth.getSession().catch(() => {});
      }
    } catch (err) {
      toast.error(t("mfa.verifyError") + ": " + (err.message || err));
    } finally {
      setVerifying(false);
    }
  };

  const handleUnenroll = async (factorId) => {
    if (!window.confirm(t("mfa.disableConfirm"))) return;
    try {
      const { error } = await supabase.auth.mfa.unenroll({ factorId });
      if (error) throw error;
      toast.success(t("mfa.disabled"));
      await fetchFactors();
    } catch (err) {
      toast.error(t("mfa.unenrollError") + ": " + (err.message || err));
    }
  };

  const verifiedFactor = factors.find((f) => f.status === "verified");

  return (
    <div className="page-container stack max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Shield className="h-6 w-6 text-primary" />
        {t("mfa.title")}
      </h1>

      <Card>
        <CardHeader>
          <CardTitle>{t("mfa.status")}</CardTitle>
          <CardDescription>{t("mfa.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
          ) : verifiedFactor ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm">
                <ShieldCheck className="h-5 w-5 text-primary" />
                <span className="font-medium">{t("mfa.enabledStatus")}</span>
              </div>
              <Button
                type="button"
                variant="destructive"
                onClick={() => handleUnenroll(verifiedFactor.id)}
              >
                <ShieldOff className="h-4 w-4 mr-2" />
                {t("mfa.disable")}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">{t("mfa.disabledStatus")}</p>
              <Button type="button" onClick={handleEnroll} disabled={enrolling}>
                {enrolling ? t("common.loading") : t("mfa.enable")}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {enrollment && (
        <Card>
          <CardHeader>
            <CardTitle>{t("mfa.scanQR")}</CardTitle>
            <CardDescription>{t("mfa.scanQRDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-center">
              <img
                src={enrollment.totp?.qr_code}
                alt="TOTP QR code"
                className="rounded-lg border bg-card p-2"
              />
            </div>
            <div className="rounded bg-muted p-3 text-sm font-mono break-all">
              {enrollment.totp?.secret}
            </div>
            <form onSubmit={handleVerify} className="space-y-2">
              <Input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={t("mfa.codePlaceholder")}
                maxLength={10}
                autoComplete="one-time-code"
              />
              <Button type="submit" disabled={verifying || !code}>
                {verifying ? t("common.loading") : t("mfa.verify")}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
