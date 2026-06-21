import { Navigate, useLocation } from "react-router-dom";
import { useState } from "react";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
import { supabase } from "../services/supabaseClient";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function Login() {
  const { session, signInWithProvider, signInWithPassword, signUp, resetPassword } = useAuth();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || "/dashboard";
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [signupStatus, setSignupStatus] = useState(null); // 'confirm' | 'auto' | null

  if (session) {
    return <Navigate to={redirectTo} replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setSignupStatus(null);

    try {
      if (mode === "signup" && password !== confirmPassword) {
        toast.error("Passwords do not match");
        return;
      }

      if (mode === "login") {
        const { error } = await signInWithPassword(email, password);
        if (error) throw error;
        toast.success("Signed in successfully");
      }

      if (mode === "signup") {
        const result = await signUp(email, password);
        if (result.error) throw result.error;

        if (result.confirmationRequired) {
          setSignupStatus("confirm");
          toast.success("Account created. Please check your email to confirm.");
        } else {
          setSignupStatus("auto");
          toast.success("Account created and signed in!");
        }
      }

      if (mode === "reset") {
        const { error } = await resetPassword(email);
        if (error) throw error;
        toast.success("Password reset email sent");
      }
    } catch (error) {
      toast.error(error?.message || "Authentication failed");
    } finally {
      setBusy(false);
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
      toast.success("Confirmation email resent. Check your inbox.");
    } catch (error) {
      toast.error(error?.message || "Failed to resend email");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>Welcome back</CardTitle>
          <CardDescription>Use email/password or Google sign in.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button
              type="button"
              variant={mode === "login" ? "default" : "outline"}
              className="w-full"
              onClick={() => setMode("login")}
            >
              Sign in
            </Button>
            <Button
              type="button"
              variant={mode === "signup" ? "default" : "outline"}
              className="w-full"
              onClick={() => setMode("signup")}
            >
              Sign up
            </Button>
          </div>

          <form className="space-y-3" onSubmit={handleSubmit}>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
            {mode !== "reset" && (
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            )}
            {mode === "signup" && (
              <Input
                type="password"
                placeholder="Confirm password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
              />
            )}

            <Button className="w-full" type="submit" disabled={busy}>
              {mode === "login" && "Sign in"}
              {mode === "signup" && "Create account"}
              {mode === "reset" && "Send reset email"}
            </Button>

            {mode === "signup" && signupStatus === "confirm" && (
              <div className="rounded-md bg-amber-50 p-3 text-sm text-amber-800 border border-amber-200">
                <p className="font-medium">Check your email</p>
                <p className="mt-1">
                  We sent a confirmation link to <strong>{email}</strong>. Click it to verify your account.
                </p>
                <Button
                  type="button"
                  variant="link"
                  className="h-auto p-0 text-amber-700 underline"
                  onClick={resendConfirmation}
                  disabled={busy}
                >
                  Didn&apos;t receive it? Resend
                </Button>
              </div>
            )}

            {mode === "signup" && signupStatus === "auto" && (
              <div className="rounded-md bg-green-50 p-3 text-sm text-green-800 border border-green-200">
                <p className="font-medium">Account created!</p>
                <p className="mt-1">
                  You&apos;re signed in. No email confirmation required for this domain.
                </p>
              </div>
            )}
          </form>

          <div className="flex items-center justify-between text-sm">
            <Button type="button" variant="ghost" onClick={() => setMode("reset")}>
              Forgot password?
            </Button>
            {mode === "reset" && (
              <Button type="button" variant="ghost" onClick={() => setMode("login")}
              >
                Back to sign in
              </Button>
            )}
          </div>

          <div className="space-y-2">
            <Button className="w-full" variant="outline" onClick={() => signInWithProvider("google")}>
              Continue with Google
            </Button>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
