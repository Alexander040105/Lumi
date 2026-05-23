import { Navigate, useLocation } from "react-router-dom";
import { useState } from "react";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
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

  if (session) {
    return <Navigate to={redirectTo} replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);

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
        const { error } = await signUp(email, password);
        if (error) throw error;
        toast.success("Check your email to confirm your account");
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
