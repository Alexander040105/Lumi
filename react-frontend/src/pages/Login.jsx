import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Login() {
  const { session, signInWithProvider } = useAuth();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || "/dashboard";

  if (session) {
    return <Navigate to={redirectTo} replace />;
  }

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>Welcome back</CardTitle>
          <CardDescription>Sign in with an OAuth provider configured in Supabase.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button className="w-full" onClick={() => signInWithProvider("google")}>
            Continue with Google
          </Button>
          <Button className="w-full" variant="outline" onClick={() => signInWithProvider("github")}>
            Continue with GitHub
          </Button>
        </CardContent>
      </Card>
    </section>
  );
}
