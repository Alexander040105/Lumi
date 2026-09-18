-- Migration 0024: Pre-launch audit fixes.
--
-- C1: Column-scope UPDATE privileges on user-owned tables. Table-level
--     GRANT UPDATE previously allowed users to modify ANY column on their own
--     rows via direct PostgREST calls — including plan (self-upgrade to
--     premium) and is_active (self-unban) on profiles. RLS scopes which ROWS
--     are visible; these grants scope which COLUMNS are writable.
-- H1: Missing ON DELETE actions blocked user deletion whenever a user had
--     saved_simulations (FK violation -> HTTP 500 on account delete and admin
--     delete). User-owned tables now CASCADE; the audit log preserves history
--     via SET NULL.

-- ---------------------------------------------------------------------------
-- C1a. profiles: only the profile-edit fields are user-writable.
--      plan / is_active / id / created_at are service-role only.
--      (REVOKE table-level UPDATE first — column-level REVOKE cannot subtract
--      from an existing table-level grant.)
-- ---------------------------------------------------------------------------

REVOKE UPDATE ON TABLE public.profiles FROM authenticated;
REVOKE UPDATE ON TABLE public.profiles FROM anon;

GRANT UPDATE (full_name, organization, location, preferred_municipality_id,
              avatar_url, ecosim_autosave, updated_at)
  ON public.profiles TO authenticated;

-- ---------------------------------------------------------------------------
-- C1b. saved_locations: user may rename / re-target a bookmark but never
--      reassign ownership (user_id) or the row id.
-- ---------------------------------------------------------------------------

REVOKE UPDATE ON TABLE public.saved_locations FROM authenticated;
REVOKE UPDATE ON TABLE public.saved_locations FROM anon;

GRANT UPDATE (label, municipality_id)
  ON public.saved_locations TO authenticated;

-- ---------------------------------------------------------------------------
-- H1a. User-owned rows cascade with the account.
-- ---------------------------------------------------------------------------

ALTER TABLE public.saved_simulations
  DROP CONSTRAINT IF EXISTS saved_simulations_user_id_fkey,
  ADD CONSTRAINT saved_simulations_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE public.saved_locations
  DROP CONSTRAINT IF EXISTS saved_locations_user_id_fkey,
  ADD CONSTRAINT saved_locations_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE public.chat_sessions
  DROP CONSTRAINT IF EXISTS chat_sessions_user_id_fkey,
  ADD CONSTRAINT chat_sessions_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE public.user_usage_limits
  DROP CONSTRAINT IF EXISTS user_usage_limits_user_id_fkey,
  ADD CONSTRAINT user_usage_limits_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- ---------------------------------------------------------------------------
-- H1b. Audit log keeps history: preserve rows but detach the deleted user.
--      (admin_id / target_user_id are already nullable.)
-- ---------------------------------------------------------------------------

ALTER TABLE public.admin_audit_log
  DROP CONSTRAINT IF EXISTS admin_audit_log_admin_id_fkey,
  ADD CONSTRAINT admin_audit_log_admin_id_fkey
    FOREIGN KEY (admin_id) REFERENCES auth.users(id) ON DELETE SET NULL;

ALTER TABLE public.admin_audit_log
  DROP CONSTRAINT IF EXISTS admin_audit_log_target_user_id_fkey,
  ADD CONSTRAINT admin_audit_log_target_user_id_fkey
    FOREIGN KEY (target_user_id) REFERENCES auth.users(id) ON DELETE SET NULL;
