-- Migration 0016: Usage reports with EcoSim tracking and fixed role casting.

-- Admin list view: per-user usage totals.
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
    total_ecosim bigint,
    ecosim_this_month bigint,
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
      COALESCE(r.role::text, 'user') AS role
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
  ecosim AS (
    SELECT e.user_id,
      count(*) AS total,
      count(*) FILTER (WHERE e.created_at >= date_trunc('month', now())) AS this_month
    FROM public.user_ecosim_logs e
    GROUP BY e.user_id
  ),
  last_active AS (
    SELECT user_id, max(created_at) AS last FROM (
      SELECT user_id, created_at FROM public.saved_simulations
      UNION ALL
      SELECT user_id, created_at FROM public.chat_sessions
      UNION ALL
      SELECT user_id, created_at FROM public.user_ecosim_logs
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
    COALESCE(e.total, 0) AS total_ecosim,
    COALESCE(e.this_month, 0) AS ecosim_this_month,
    la.last AS last_active,
    u.created_at
  FROM users u
  LEFT JOIN auth.users au ON au.id = u.id
  LEFT JOIN sims s ON s.user_id = u.id
  LEFT JOIN chats c ON c.user_id = u.id
  LEFT JOIN ecosim e ON e.user_id = u.id
  LEFT JOIN last_active la ON la.user_id = u.id
  ORDER BY la.last DESC NULLS LAST, u.created_at DESC
  LIMIT p_limit OFFSET p_offset;
$$;

GRANT EXECUTE ON FUNCTION public.get_admin_usage_summary(integer, integer, text) TO postgres;
GRANT EXECUTE ON FUNCTION public.get_admin_usage_summary(integer, integer, text) TO service_role;

-- Single-user drill-down report for the admin user detail drawer.
CREATE OR REPLACE FUNCTION public.get_user_usage_report(p_user_id uuid)
RETURNS TABLE (
    total_simulations bigint,
    simulations_this_month bigint,
    total_chat_sessions bigint,
    chat_sessions_this_month bigint,
    total_ecosim bigint,
    ecosim_this_month bigint,
    last_active timestamp with time zone,
    peak_municipality_id integer,
    recent_simulations jsonb,
    monthly_breakdown jsonb
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public, auth
AS $$
  WITH sims AS (
    SELECT s.*, m.name AS municipality_name
    FROM public.saved_simulations s
    LEFT JOIN public.municipalities m ON m.municipality_id = s.municipality_id
    WHERE s.user_id = p_user_id
  ),
  sim_counts AS (
    SELECT
      count(*) AS total,
      count(*) FILTER (WHERE created_at >= date_trunc('month', now())) AS this_month
    FROM public.saved_simulations
    WHERE user_id = p_user_id
  ),
  chat_counts AS (
    SELECT
      count(*) AS total,
      count(*) FILTER (WHERE created_at >= date_trunc('month', now())) AS this_month
    FROM public.chat_sessions
    WHERE user_id = p_user_id
  ),
  ecosim_counts AS (
    SELECT
      count(*) AS total,
      count(*) FILTER (WHERE created_at >= date_trunc('month', now())) AS this_month
    FROM public.user_ecosim_logs
    WHERE user_id = p_user_id
  ),
  last_active AS (
    SELECT max(created_at) AS last FROM (
      SELECT created_at FROM public.saved_simulations WHERE user_id = p_user_id
      UNION ALL
      SELECT created_at FROM public.chat_sessions WHERE user_id = p_user_id
      UNION ALL
      SELECT created_at FROM public.user_ecosim_logs WHERE user_id = p_user_id
    ) x
  ),
  months AS (
    SELECT date_trunc('month', now()) - (generate_series(0, 11) * interval '1 month') AS month
  )
  SELECT
    (SELECT total FROM sim_counts),
    (SELECT this_month FROM sim_counts),
    (SELECT total FROM chat_counts),
    (SELECT this_month FROM chat_counts),
    (SELECT total FROM ecosim_counts),
    (SELECT this_month FROM ecosim_counts),
    (SELECT last FROM last_active),
    (SELECT mode() WITHIN GROUP (ORDER BY municipality_id) FROM sims),
    (
      SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'id', s.id,
        'label', s.label,
        'municipality_name', s.municipality_name,
        'created_at', s.created_at
      ) ORDER BY s.created_at DESC), '[]'::jsonb)
      FROM (SELECT * FROM sims ORDER BY created_at DESC LIMIT 5) s
    ),
    (
      SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'month', to_char(m.month, 'YYYY-MM'),
        'saved_simulations', COALESCE(ss.cnt, 0),
        'chat_sessions', COALESCE(cs.cnt, 0),
        'ecosim_calculations', COALESCE(el.cnt, 0)
      ) ORDER BY m.month DESC), '[]'::jsonb)
      FROM months m
      LEFT JOIN (
        SELECT date_trunc('month', created_at) AS month, count(*) AS cnt
        FROM public.saved_simulations WHERE user_id = p_user_id GROUP BY 1
      ) ss ON ss.month = m.month
      LEFT JOIN (
        SELECT date_trunc('month', created_at) AS month, count(*) AS cnt
        FROM public.chat_sessions WHERE user_id = p_user_id GROUP BY 1
      ) cs ON cs.month = m.month
      LEFT JOIN (
        SELECT date_trunc('month', created_at) AS month, count(*) AS cnt
        FROM public.user_ecosim_logs WHERE user_id = p_user_id GROUP BY 1
      ) el ON el.month = m.month
    );
$$;

GRANT EXECUTE ON FUNCTION public.get_user_usage_report(uuid) TO postgres;
GRANT EXECUTE ON FUNCTION public.get_user_usage_report(uuid) TO service_role;
