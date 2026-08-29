-- Migration 0015: Track every authenticated EcoSim calculation request.
-- This powers per-user usage reports and the admin analytics charts.

CREATE TABLE IF NOT EXISTS public.user_ecosim_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    municipality_id integer REFERENCES public.municipalities(municipality_id) ON UPDATE CASCADE ON DELETE SET NULL,
    created_at timestamp with time zone DEFAULT now()
);

ALTER TABLE public.user_ecosim_logs ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE public.user_ecosim_logs IS 'One row per authenticated EcoSim request for usage reporting.';

-- Users can only see their own logs; admins can see all.
CREATE POLICY "user_ecosim_logs_select_own_or_admin"
  ON public.user_ecosim_logs FOR SELECT TO authenticated
  USING (auth.uid() = user_id OR public.is_admin());

CREATE INDEX IF NOT EXISTS idx_user_ecosim_logs_user_id_created
  ON public.user_ecosim_logs (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_ecosim_logs_created
  ON public.user_ecosim_logs (created_at DESC);

GRANT ALL ON TABLE public.user_ecosim_logs TO service_role;
GRANT SELECT ON TABLE public.user_ecosim_logs TO authenticated;
