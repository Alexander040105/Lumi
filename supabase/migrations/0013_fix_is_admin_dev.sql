-- Migration 0013: Ensure is_admin() treats devs as admins
--
-- The backend already treats 'dev' as an admin (require_admin allows 'dev'),
-- but the RLS helper is_admin() in older migrations only checks 'admin'.
-- This can cause RLS policy mismatches for dev-role users when they access
-- admin-scoped data directly through the Supabase client.

CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = auth.uid() AND role IN ('admin', 'dev')
  );
$$;

-- Ensure the function is callable by authenticated users (needed for RLS) and
-- the service_role used by the backend. idempotent -- no error on re-grant.
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated;
GRANT EXECUTE ON FUNCTION public.is_admin() TO service_role;
