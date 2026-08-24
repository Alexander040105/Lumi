import { createContext, useEffect, useMemo, useRef, useState } from "react";

import { supabase } from "../services/supabaseClient";
import { getApiBaseUrl } from "../utils/env";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [role, setRole] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [emailConfirmed, setEmailConfirmed] = useState(false);

  useEffect(() => {
    let isMounted = true;

    supabase.auth.getSession().then(({ data }) => {
      if (!isMounted) return;
      setSession(data.session);
      setEmailConfirmed(!!data.session?.user?.email_confirmed_at);
      setLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      setEmailConfirmed(!!newSession?.user?.email_confirmed_at);
    });

    return () => {
      isMounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  // Fetch user role and profile once per user, ignoring token refreshes
  const lastFetchedUserId = useRef(null);
  useEffect(() => {
    const userId = session?.user?.id;
    if (!userId) {
      setRole(null);
      setProfile(null);
      lastFetchedUserId.current = null;
      return;
    }

    if (lastFetchedUserId.current === userId) {
      return;
    }
    lastFetchedUserId.current = userId;

    const controller = new AbortController();
    const signal = controller.signal;

    const fetchRoleAndProfile = async () => {
      try {
        // Fetch role + profile from backend (bypasses RLS, authoritative source)
        const res = await fetch(`${getApiBaseUrl()}/protected/me`, {
          headers: { Authorization: `Bearer ${session.access_token}` },
          signal,
        });
        if (res.ok) {
          const data = await res.json();
          const backendRole = data.user?.role;
          if (backendRole) {
            console.log("[AuthContext] Role from backend:", backendRole);
            setRole(backendRole);
          } else {
            setRole("user");
          }
        } else {
          console.error("[AuthContext] /protected/me failed:", res.status);
          setRole("user");
        }

        // Fetch profile from backend (bypasses RLS infinite recursion)
        const profileRes = await fetch(`${getApiBaseUrl()}/protected/profile`, {
          headers: { Authorization: `Bearer ${session.access_token}` },
          signal,
        });
        if (profileRes.ok) {
          const profileJson = await profileRes.json();
          if (profileJson.profile) {
            setProfile(profileJson.profile);
          }
        } else {
          console.error("[AuthContext] /protected/profile failed:", profileRes.status);
        }
      } catch (err) {
        if (err.name === "AbortError") return;
        console.error("[AuthContext] Unexpected error fetching role/profile:", err);
        setRole("user");
      }
    };

    fetchRoleAndProfile();

    // Sync OAuth avatar from auth metadata to profiles once per user
    fetch(`${getApiBaseUrl()}/protected/sync-avatar`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.access_token}` },
      signal,
    }).catch(() => {});

    return () => controller.abort();
  }, [session?.user?.id]);

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
      emailConfirmed,
      signInWithProvider: (provider) =>
        supabase.auth.signInWithOAuth({
          provider,
          options: { redirectTo: `${window.location.origin}/login` },
        }),
      signInWithPassword: (email, password) =>
        supabase.auth.signInWithPassword({ email, password }),
      signUp: async (email, password, options = {}) => {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            ...options,
            emailRedirectTo: options.emailRedirectTo || `${window.location.origin}/login`,
          },
        });
        if (error) console.error("[AuthContext] signup error:", error);
        return {
          user: data?.user ?? null,
          session: data?.session ?? null,
          error,
          // If session is null, email confirmation is required
          confirmationRequired: !data?.session && !error,
        };
      },
      resetPassword: (email) =>
        supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/reset-password`
        }),
      updatePassword: (newPassword) => supabase.auth.updateUser({ password: newPassword }),
      signOut: () => {
        setEmailConfirmed(false);
        return supabase.auth.signOut();
      },
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
    [session, loading, role, isAdmin, effectivePlan, isPremium, profile, emailConfirmed]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
