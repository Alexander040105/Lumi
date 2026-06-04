export function getSupabaseUrl(): string {
  return process.env.EXPO_PUBLIC_SUPABASE_URL || '';
}

export function getSupabaseAnonKey(): string {
  return process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || '';
}

export function getApiBaseUrl(): string {
  return (
    process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
  );
}
