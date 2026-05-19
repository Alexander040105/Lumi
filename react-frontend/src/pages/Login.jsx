import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { session, signInWithProvider } = useAuth();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || "/dashboard";

  if (session) {
    return <Navigate to={redirectTo} replace />;
  }

  return (
    <section>
      <h1>Sign in</h1>
      <p>Use an OAuth provider configured in Supabase.</p>
      <div>
        <button type="button" onClick={() => signInWithProvider("google")}>
          Continue with Google
        </button>
        <button type="button" onClick={() => signInWithProvider("github")}>
          Continue with GitHub
        </button>
      </div>
    </section>
  );
}
