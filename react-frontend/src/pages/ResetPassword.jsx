import { useState } from "react";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function ResetPassword() {
  const { session, updatePassword } = useAuth();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setBusy(true);
    try {
      const { error } = await updatePassword(password);
      if (error) throw error;
      toast.success("Password updated. You can sign in again.");
    } catch (error) {
      toast.error(error?.message || "Password update failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>Reset your password</CardTitle>
          <CardDescription>Set a new password after confirming your email.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!session && (
            <p className="text-sm text-muted-foreground">
              Open this page from the reset link in your email.
            </p>
          )}
          <form className="space-y-3" onSubmit={handleSubmit}>
            <Input
              type="password"
              placeholder="New password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={6}
            />
            <Input
              type="password"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              minLength={6}
            />
            <Button className="w-full" type="submit" disabled={busy || !session}>
              Update password
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
