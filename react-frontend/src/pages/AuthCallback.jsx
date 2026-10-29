import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { useI18n } from "../i18n";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function AuthCallback() {
  const { t } = useI18n();
  const { session, loading } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  useEffect(() => {
    // Supabase surfaces failures (expired link, bad token) as error params in
    // the callback URL. Read both query and hash before the SDK cleans them.
    const params = new URLSearchParams(window.location.search);
    const hash = new URLSearchParams(window.location.hash.slice(1));
    const description =
      params.get("error_description") ||
      hash.get("error_description") ||
      params.get("error") ||
      hash.get("error");
    if (description) {
      setError(decodeURIComponent(description.replace(/\+/g, " ")));
    }
  }, []);

  useEffect(() => {
    // Hand the new session to Login, which owns the MFA check and the final
    // redirect to the requested page or dashboard.
    if (session) {
      navigate("/login", { replace: true });
    }
  }, [session, navigate]);

  useEffect(() => {
    // If neither a session nor a URL error appears, the link was malformed.
    if (error || session || loading) return undefined;
    const timeout = setTimeout(
      () => setError(t("authCallback.expiredError")),
      10000,
    );
    return () => clearTimeout(timeout);
  }, [error, session, loading, t]);

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>
            {error ? t("authCallback.errorTitle") : t("authCallback.title")}
          </CardTitle>
          {!error && <CardDescription>{t("authCallback.description")}</CardDescription>}
        </CardHeader>
        <CardContent className="space-y-3">
          {error ? (
            <>
              <p className="text-sm text-muted-foreground">{error}</p>
              <Button className="w-full" onClick={() => navigate("/login", { replace: true })}>
                {t("authCallback.backToSignIn")}
              </Button>
            </>
          ) : (
            <div
              className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent"
              role="status"
              aria-label={t("authCallback.title")}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
