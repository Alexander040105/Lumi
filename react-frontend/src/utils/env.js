export function getSupabaseUrl() {
  const url = import.meta.env.VITE_SUPABASE_URL;
  if (!url) {
    throw new Error("VITE_SUPABASE_URL is required");
  }
  return url;
}

export function getSupabaseAnonKey() {
  const key = import.meta.env.VITE_SUPABASE_ANON_KEY;
  if (!key) {
    throw new Error("VITE_SUPABASE_ANON_KEY is required");
  }
  return key;
}

export function getApiBaseUrl() {
  if (import.meta.env.DEV) {
    return "/api/v1";
  }
  const base = import.meta.env.VITE_API_BASE_URL;
  if (!base) {
    throw new Error("VITE_API_BASE_URL is required");
  }
  // Force IPv4 to avoid browsers resolving "localhost" to ::1 when the server is IPv4-only.
  const trimmed = base.trim().replace(/\/+$/, "").replace("/localhost:", "/127.0.0.1:");
  if (trimmed.endsWith("/api/v1")) {
    return trimmed;
  }
  if (trimmed.endsWith("/api")) {
    return `${trimmed}/v1`;
  }
  return `${trimmed}/api/v1`;
}
