import { createContext, useEffect, useMemo, useState } from "react";

import { supabase } from "../services/supabaseClient";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [role, setRole] = useState(null);
  const [profile, setProfile] = useState(null);
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

  // Fetch user role and profile whenever the session changes
  useEffect(() => {
    if (!session?.user) {
      setRole(null);
      setProfile(null);
      return;
    }

    const fetchRoleAndProfile = async () => {
      try {
        // Fetch role
        const { data: roleData, error: roleError } = await supabase
          .from("user_roles")
          .select("role")
          .eq("user_id", session.user.id)
          .single();
        if (!roleError && roleData) {
          setRole(roleData.role);
        } else {
          setRole("user");
        }

        // Fetch profile
        const { data: profileData, error: profileError } = await supabase
          .from("profiles")
          .select("*")
          .eq("id", session.user.id)
          .single();
        if (!profileError && profileData) {
          setProfile(profileData);
        }
      } catch {
        setRole("user");
      }
    };

    fetchRoleAndProfile();

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
      profile,
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
      signOut: () => supabase.auth.signOut(),
      refreshProfile: async () => {
        if (!session?.user) return;
        const { data } = await supabase
          .from("profiles")
          .select("*")
          .eq("id", session.user.id)
          .single();
        if (data) setProfile(data);
      },
    }),
    [session, loading, role, isAdmin, effectivePlan, isPremium, profile]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
