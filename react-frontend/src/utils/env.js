export function getSupabaseUrl() {
  return import.meta.env.VITE_SUPABASE_URL || "";
}

export function getSupabaseAnonKey() {
  return import.meta.env.VITE_SUPABASE_ANON_KEY || "";
}

export function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
}
