-- Migration 0014: Paginated, searchable admin user list
--
-- Returns a single RPC result so the Vercel serverless function stays within
-- the 10 s limit and does not have to enumerate all auth.users rows.

CREATE OR REPLACE FUNCTION public.get_admin_users_list(
    p_limit integer DEFAULT 50,
    p_offset integer DEFAULT 0,
    p_search text DEFAULT NULL,
    p_role text DEFAULT NULL,
    p_plan text DEFAULT NULL,
    p_is_active boolean DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    full_name text,
    email text,
    role text,
    plan text,
    is_active boolean,
    avatar_url text,
    created_at timestamp with time zone
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public, auth
AS $$
  SELECT
    p.id,
    p.full_name,
    au.email,
    r.role,
    p.plan,
    p.is_active,
    p.avatar_url,
    p.created_at
  FROM public.profiles p
  LEFT JOIN public.user_roles r ON r.user_id = p.id
  LEFT JOIN auth.users au ON au.id = p.id
  WHERE
    (p_search IS NULL OR p.full_name ILIKE '%' || p_search || '%' OR au.email ILIKE '%' || p_search || '%')
    AND (p_role IS NULL OR r.role = p_role)
    AND (p_plan IS NULL OR p.plan = p_plan)
    AND (p_is_active IS NULL OR p.is_active = p_is_active)
  ORDER BY p.created_at DESC
  LIMIT p_limit OFFSET p_offset;
$$;

GRANT EXECUTE ON FUNCTION public.get_admin_users_list(integer, integer, text, text, text, boolean) TO postgres;
GRANT EXECUTE ON FUNCTION public.get_admin_users_list(integer, integer, text, text, text, boolean) TO service_role;

-- Helpers for the most common filter and sort cases.
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON public.profiles (created_at DESC);
