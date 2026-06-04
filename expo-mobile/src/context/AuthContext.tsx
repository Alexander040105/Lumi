import { createContext, useEffect, useMemo, useState } from 'react';
import * as Linking from 'expo-linking';
import * as WebBrowser from 'expo-web-browser';
import { supabase } from '@/services/supabaseClient';

export interface AuthContextValue {
  session: ReturnType<typeof useState<Awaited<ReturnType<typeof supabase.auth.getSession>>['data']['session']>>[0];
  user: Record<string, unknown> | null;
  accessToken: string | null;
  loading: boolean;
  signInWithProvider: (provider: 'google') => Promise<{ error?: Error }>;
  signInWithPassword: (email: string, password: string) => Promise<{ error?: Error }>;
  signUp: (email: string, password: string) => Promise<{ error?: Error }>;
  resetPassword: (email: string) => Promise<{ error?: Error }>;
  updatePassword: (newPassword: string) => Promise<{ error?: Error }>;
  signOut: () => Promise<{ error?: Error }>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<AuthContextValue['session']>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    supabase.auth.getSession().then(({ data }) => {
      if (!isMounted) return;
      setSession(data.session);
      setLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, newSession) => {
        setSession(newSession);
      }
    );

    return () => {
      isMounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      user: (session?.user ?? null) as Record<string, unknown> | null,
      accessToken: (session?.access_token ?? null) as string | null,
      loading,
      signInWithProvider: async (provider) => {
        const redirectUri = Linking.createURL('auth/callback');
        console.log('OAuth redirect URI:', redirectUri);

        const { data, error } = await supabase.auth.signInWithOAuth({
          provider,
          options: { redirectTo: redirectUri, skipBrowserRedirect: true },
        });
        if (error) return { error };

        if (data?.url) {
          // Listen for deep link BEFORE opening browser
          let deepLinkUrl: string | null = null;
          const subscription = Linking.addEventListener('url', ({ url }) => {
            console.log('Deep link received:', url);
            if (
              url.includes('code=') ||
              url.includes('access_token=') ||
              url.includes('error=')
            ) {
              deepLinkUrl = url;
            }
          });

          // Open browser (no redirect tracking — rely on deep link)
          await WebBrowser.openBrowserAsync(data.url);

          // Wait for deep link
          const url = await new Promise<string | null>((resolve) => {
            const check = () => {
              if (deepLinkUrl) {
                resolve(deepLinkUrl);
                return;
              }
              setTimeout(check, 300);
            };
            check();
            setTimeout(() => resolve(null), 120000);
          });

          // Close browser
          try {
            await WebBrowser.dismissBrowser();
          } catch (e) {
            // Browser may already be closed
          }

          (subscription as any)?.remove?.();

          if (url) {
            console.log('Processing OAuth URL:', url);
            const parsed = new URL(url);

            // PKCE flow: code in query string
            const code = parsed.searchParams.get('code');

            // Implicit grant: tokens in fragment
            const hash = parsed.hash;
            const fragment = hash ? hash.substring(1) : '';
            const fragmentParams = new URLSearchParams(fragment);
            const accessToken = fragmentParams.get('access_token');
            const refreshToken = fragmentParams.get('refresh_token');
            const expiresAt = fragmentParams.get('expires_at');

            const errorParam =
              parsed.searchParams.get('error') || fragmentParams.get('error');
            const errorDesc =
              parsed.searchParams.get('error_description') ||
              fragmentParams.get('error_description');

            if (errorParam) {
              console.error('OAuth error:', errorParam, errorDesc);
              return { error: new Error(errorDesc || errorParam) };
            }

            if (code) {
              // PKCE flow
              console.log('OAuth code found, exchanging...');
              const { data: exchangeData, error: exchangeError } =
                await supabase.auth.exchangeCodeForSession(code);
              if (exchangeError) {
                console.error('exchangeCodeForSession error:', exchangeError.message);
                return { error: exchangeError };
              }
              console.log('exchangeCodeForSession success, session:', !!exchangeData.session);
              if (exchangeData.session) {
                setSession(exchangeData.session);
              }
            } else if (accessToken && refreshToken) {
              // Implicit grant flow — set session directly
              console.log('OAuth tokens found in fragment, setting session...');
              const { data, error: setError } = await supabase.auth.setSession({
                access_token: accessToken,
                refresh_token: refreshToken,
              });
              if (setError) {
                console.error('setSession error:', setError.message);
                return { error: setError };
              }
              console.log('setSession success, session:', !!data.session);
              if (data.session) {
                setSession(data.session);
              }
            } else {
              console.error('No code or tokens in OAuth redirect URL');
            }
          } else {
            console.error('No OAuth redirect URL received within timeout');
          }
        }
        return {};
      },
      signInWithPassword: async (email, password) => {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        return { error: error ?? undefined };
      },
      signUp: async (email, password) => {
        const { error } = await supabase.auth.signUp({ email, password });
        return { error: error ?? undefined };
      },
      resetPassword: async (email) => {
        const redirectUri = Linking.createURL('reset-password');
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: redirectUri,
        });
        return { error: error ?? undefined };
      },
      updatePassword: async (newPassword) => {
        const { error } = await supabase.auth.updateUser({
          password: newPassword,
        });
        return { error: error ?? undefined };
      },
      signOut: async () => {
        const { error } = await supabase.auth.signOut();
        return { error: error ?? undefined };
      },
    }),
    [session, loading]
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}
