import { createContext, useEffect, useMemo, useState } from "react";

import { supabase } from "../services/supabaseClient";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    supabase.auth.getSession().then(({ data }) => {
      if (!isMounted) return;
      setSession(data.session);
      setLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
    });

    return () => {
      isMounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  // Fetch user role from profiles/user_roles whenever the session changes
  useEffect(() => {
    if (!session?.user) {
      setRole(null);
      return;
    }

    const fetchRole = async () => {
      try {
        const { data, error } = await supabase
          .from("user_roles")
          .select("role")
          .eq("user_id", session.user.id)
          .single();
        if (!error && data) {
          setRole(data.role);
        } else {
          setRole("user");
        }
      } catch {
        setRole("user");
      }
    };

    fetchRole();

    // Sync OAuth avatar from auth metadata to profiles
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/protected/sync-avatar`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.access_token}` },
    }).catch(() => {});
  }, [session]);

  const isAdmin = role === "admin" || role === "dev";
  const effectivePlan = isAdmin ? "premium" : "free";
  const isPremium = isAdmin;

  const value = useMemo(
    () => ({
      session,
      user: session?.user ?? null,
      accessToken: session?.access_token ?? null,
      loading,
      role,
      isAdmin,
      effectivePlan,
      isPremium,
      signInWithProvider: (provider) => supabase.auth.signInWithOAuth({ provider }),
      signInWithPassword: (email, password) =>
        supabase.auth.signInWithPassword({ email, password }),
      signUp: (email, password) => supabase.auth.signUp({ email, password }),
      resetPassword: (email) =>
        supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/reset-password`
        }),
      updatePassword: (newPassword) => supabase.auth.updateUser({ password: newPassword }),
      signOut: () => supabase.auth.signOut()
    }),
    [session, loading, role, isAdmin, effectivePlan, isPremium]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
