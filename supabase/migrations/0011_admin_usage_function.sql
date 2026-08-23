-- Optimized admin usage summary for Vercel free tier.
-- Single RPC call returns a paginated, searchable list of users with
-- simulation/chat usage counts and last-active timestamp.

CREATE INDEX IF NOT EXISTS idx_saved_simulations_user_id_created
    ON public.saved_simulations (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id_created
    ON public.chat_sessions (user_id, created_at DESC);

DROP FUNCTION IF EXISTS public.get_admin_usage_summary(integer, integer, text);

CREATE OR REPLACE FUNCTION public.get_admin_usage_summary(
    p_limit integer DEFAULT 50,
    p_offset integer DEFAULT 0,
    p_search text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    full_name text,
    email text,
    role text,
    plan text,
    is_active boolean,
    total_simulations bigint,
    simulations_this_month bigint,
    total_chat_sessions bigint,
    chat_sessions_this_month bigint,
    last_active timestamp with time zone,
    created_at timestamp with time zone
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public, auth
AS $$
  WITH users AS (
    SELECT
      p.id,
      p.full_name,
      p.plan,
      p.is_active,
      p.created_at,
      r.role
    FROM public.profiles p
    LEFT JOIN public.user_roles r ON r.user_id = p.id
    WHERE (p_search IS NULL OR p.full_name ILIKE '%' || p_search || '%')
  ),
  sims AS (
    SELECT s.user_id,
      count(*) AS total,
      count(*) FILTER (WHERE s.created_at >= date_trunc('month', now())) AS this_month
    FROM public.saved_simulations s
    GROUP BY s.user_id
  ),
  chats AS (
    SELECT c.user_id,
      count(*) AS total,
      count(*) FILTER (WHERE c.created_at >= date_trunc('month', now())) AS this_month
    FROM public.chat_sessions c
    GROUP BY c.user_id
  ),
  last_active AS (
    SELECT user_id, max(created_at) AS last FROM (
      SELECT user_id, created_at FROM public.saved_simulations
      UNION ALL
      SELECT user_id, created_at FROM public.chat_sessions
    ) all_activity
    GROUP BY user_id
  )
  SELECT
    u.id,
    u.full_name,
    au.email,
    u.role,
    u.plan,
    u.is_active,
    COALESCE(s.total, 0) AS total_simulations,
    COALESCE(s.this_month, 0) AS simulations_this_month,
    COALESCE(c.total, 0) AS total_chat_sessions,
    COALESCE(c.this_month, 0) AS chat_sessions_this_month,
    la.last AS last_active,
    u.created_at
  FROM users u
  LEFT JOIN auth.users au ON au.id = u.id
  LEFT JOIN sims s ON s.user_id = u.id
  LEFT JOIN chats c ON c.user_id = u.id
  LEFT JOIN last_active la ON la.user_id = u.id
  ORDER BY la.last DESC NULLS LAST, u.created_at DESC
  LIMIT p_limit OFFSET p_offset;
$$;

GRANT EXECUTE ON FUNCTION public.get_admin_usage_summary(integer, integer, text) TO postgres;
GRANT EXECUTE ON FUNCTION public.get_admin_usage_summary(integer, integer, text) TO service_role;
