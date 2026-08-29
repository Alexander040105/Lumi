-- Migration 0017: Confirm admin audit log grants and indexes.
-- The actual audit-log improvements (target_user_id / details population)
-- are implemented in the FastAPI admin routes.

GRANT SELECT ON TABLE public.admin_audit_log TO authenticated;

-- Ensure the detail indexes exist for quick filtering.
CREATE INDEX IF NOT EXISTS idx_admin_audit_action ON public.admin_audit_log (action);
CREATE INDEX IF NOT EXISTS idx_admin_audit_target_user_id ON public.admin_audit_log (target_user_id);
