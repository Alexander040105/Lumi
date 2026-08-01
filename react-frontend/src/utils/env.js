export function getSupabaseUrl() {
  return import.meta.env.VITE_SUPABASE_URL || "";
}

export function getSupabaseAnonKey() {
  return import.meta.env.VITE_SUPABASE_ANON_KEY || "";
}

export function getApiBaseUrl() {
  if (import.meta.env.DEV) {
    return "/api/v1";
  }
  return import.meta.env.VITE_API_BASE_URL || "/api/v1";
}
