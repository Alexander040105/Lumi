export function getSupabaseUrl() {
  return (
    import.meta.env.VITE_SUPABASE_URL ||
    "https://husnkzlccdrjpwlqcfbt.supabase.co"
  );
}

export function getSupabaseAnonKey() {
  return (
    import.meta.env.VITE_SUPABASE_ANON_KEY ||
    "sb_publishable_dth7eXs1Shn6pBPstjr0dQ_wprh2qGR"
  );
}

export function getApiBaseUrl() {
  if (import.meta.env.DEV) {
    return "/api/v1";
  }
  return (
    import.meta.env.VITE_API_BASE_URL ||
    "https://lumi-backend-ten.vercel.app/api/v1"
  );
}
