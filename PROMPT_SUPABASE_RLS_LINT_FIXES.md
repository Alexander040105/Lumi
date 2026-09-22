# Prompt for SWE-2 High: Fix Supabase Security Lints

Copy everything below the horizontal rule into a new SWE-2 High session inside this repository (`Lumi`). It will produce one new migration that clears the database security lints.

---

## Context

You are SWE-2 High working in the **LUMI** repository. The project uses **Supabase** (project ref `husnkzlccdrjpwlqcfbt`) with **imperative migrations** in `supabase/migrations/` (files `0001`–`0024` exist; you will add `0025`). There is no `config.toml` or declarative `supabase/schemas/` — schema is managed by numbered migration files plus some manually-applied scripts in `supabase/table_scripts/`.

A Supabase database linter run produced a CSV at `C:\Users\Pixel-Tone\Downloads\Supabase Performance Security Lints (husnkzlccdrjpwlqcfbt).csv` with **25 findings in 7 categories**. Your job is to fix all SQL-fixable ones in a single new migration.

**Critical architecture fact:** the backend (`fastapi-backend`) always talks to Supabase through `get_supabase_client()`, which uses the **service_role key** (`app/services/supabase_service.py:108-125`) and therefore bypasses RLS entirely. Revoking anon/authenticated EXECUTE or SELECT on backend-only objects cannot break the app. The frontend (`react-frontend`) and mobile app (`expo-mobile`) never call the flagged functions or tables directly — verified by grep. The frontend only touches Supabase Storage for `avatars` uploads (`ProfilePage.jsx:87-92`, `Dashboard.jsx:225-230`).

## Task

Create exactly one new file: **`supabase/migrations/0025_security_lint_fixes.sql`**

The migration must be **idempotent** (safe to run twice): use `DROP POLICY IF EXISTS`, `CREATE OR REPLACE`, and plain `REVOKE`/`GRANT` (they're naturally idempotent). Start the file with a comment header listing the lint categories it addresses and the CSV filename. Do not modify any earlier migration. Do not drop tables, columns, or data.

## Category A — `security_definer_view` (3 ERRORs)

Views `public.province_climate_annual`, `public.regional_lookup`, `public.regional_lookup_v2` were created as SECURITY DEFINER (Postgres default), meaning they enforce the view *creator's* permissions instead of the querying user's. Fix: recreate each `WITH (security_invoker = true)` (requires Postgres 15+, which Supabase runs).

- `province_climate_annual` — full definition at `supabase/migrations/0001_geospatial_architecture.sql:483-500` (aggregates `province_climate_monthly`). Recreate identically, adding `WITH (security_invoker = true)` to the CREATE OR REPLACE VIEW statement, and keep the `ALTER VIEW ... OWNER TO postgres` and `COMMENT` lines.
- `regional_lookup` — full definition at `supabase/table_scripts/schema.sql:39-60` (joins `regions`/`provinces`/`municipalities`/`barangays`). It was never in a numbered migration — inline the definition in 0025 with `security_invoker = true`.
- `regional_lookup_v2` — full definition at `supabase/migrations/0001_geospatial_architecture.sql:510-535` (adds `geospatial_metadata` joins). Same treatment.

Safety check first (already true, but verify): all underlying tables (`regions`, `provinces`, `municipalities`, `barangays`, `geospatial_metadata`, `province_climate_monthly`) have public SELECT policies and SELECT grants to anon/authenticated from `0009_rls_hardening.sql:132-162,323-500`. Also preserve the existing view grants (`REVOKE ALL` + `GRANT SELECT` to anon/authenticated, `GRANT ALL` to service_role — see `0009:277-287`).

## Category B — `rls_disabled_in_public` (4 ERRORs)

Tables `public.municipality_atlas_averages`, `public.province_atlas_averages`, `public.municipality_era5_averages`, `public.province_era5_averages` are exposed to PostgREST with no RLS. They contain public reference climate data and are read only by the service-role backend (`app/services/atlas_data.py`), but RLS must be enabled to clear the ERROR and as defense in depth.

For each table, mirror the 0009 convention:

```sql
ALTER TABLE public.<table> ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "<table>_select_public" ON public.<table>;
CREATE POLICY "<table>_select_public"
  ON public.<table> FOR SELECT TO anon, authenticated
  USING (true);

GRANT SELECT ON TABLE public.<table> TO anon, authenticated;
GRANT ALL ON TABLE public.<table> TO service_role;
```

Their definitions live in `supabase/table_scripts/municipality_atlas_schema.sql`, `province_atlas_schema.sql`, `municipality_era5_schema.sql`, `province_era5_schema.sql` (for reference — do not edit those files).

## Category C — `function_search_path_mutable` (3 WARNs)

Functions with no fixed `search_path` can be hijacked via schema precedence. For each, add `ALTER FUNCTION ... SET search_path = pg_catalog, public`:

- `public.set_updated_at()` — trigger function, defined in `supabase/table_scripts/national_energy_schema.sql:172`
- `public.get_suitability_classification(numeric)` — defined in `supabase/table_scripts/supabase_suitability_migration.sql:77`
- `public.handle_new_user()` — trigger function, defined in `supabase/table_scripts/auth_admin_schema.sql:132`

(Note: `public.is_admin()` already sets `search_path = public` in `0013_fix_is_admin_dev.sql:12` — no change needed there.)

## Category D/E — executable SECURITY DEFINER functions (12 WARNs)

Postgres grants EXECUTE to PUBLIC by default on new functions, so these are callable via `/rest/v1/rpc/` by anyone. Apply the following — the decisions were already made, do not re-litigate them:

**Revoke from PUBLIC, anon, and authenticated; re-grant to service_role only:**

```sql
REVOKE EXECUTE ON FUNCTION public.get_admin_usage_summary(integer, integer, text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.get_admin_usage_summary(integer, integer, text) TO service_role;

REVOKE EXECUTE ON FUNCTION public.get_admin_users_list(integer, integer, text, text, text, boolean) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.get_admin_users_list(integer, integer, text, text, text, boolean) TO service_role;

REVOKE EXECUTE ON FUNCTION public.get_user_usage_report(uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_usage_report(uuid) TO service_role;

REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO service_role;

REVOKE EXECUTE ON FUNCTION public.match_rag_chunks(extensions.vector, integer, double precision, text, text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.match_rag_chunks(extensions.vector, integer, double precision, text, text) TO service_role;
```

Why each is safe:
- The three admin/report functions are only called from `fastapi-backend/app/routes/admin.py` via the service-role client (`admin.py:135,470,659,677`).
- `handle_new_user` is a trigger function — Postgres triggers don't need EXECUTE grants.
- `match_rag_chunks` is only called from `app/services/rag_pgvector_store.py` via the service client — **the re-grant to service_role is required**, because it currently relies on the PUBLIC default (no explicit grant exists in `0007_rag_pgvector.sql`).

**`public.is_admin()` — partial revoke only (decision made):**

```sql
REVOKE EXECUTE ON FUNCTION public.is_admin() FROM PUBLIC, anon;
-- KEEP authenticated + service_role (granted in 0013_fix_is_admin_dev.sql:22-23)
```

`is_admin()` is called inside RLS policy expressions (`USING (public.is_admin())` across `0009`, `0010`, `0015`, `0022`), and Postgres checks EXECUTE against the querying role — revoking `authenticated` would break every admin policy. The linter will keep warning that `authenticated` can execute a SECURITY DEFINER function. **Add a comment block in the migration documenting this as an accepted, intentional residual**: the function returns only a boolean about the caller, and the alternative (inlining the admin EXISTS check into ~10 policies) was rejected for maintainability.

## Category F — `public_bucket_allows_listing` (2 WARNs)

Public buckets `avatars` and `geojsons` have broad SELECT policies on `storage.objects` that let anyone *list* all files. Public buckets serve files by URL without any policy — these policies only enable listing and are safe to drop:

```sql
DROP POLICY IF EXISTS "Allow public read" ON storage.objects;
DROP POLICY IF EXISTS "Public read avatars" ON storage.objects;
DROP POLICY IF EXISTS "Public read on geojsons bucket" ON storage.objects;
```

(The geojsons policy was created in `0008_data_offload.sql:198-202`.)

Then make sure avatar **uploads** keep working: the frontend does `storage.from("avatars").upload(path, file, { upsert: true })` as an authenticated user, and upsert needs INSERT + UPDATE + SELECT on `storage.objects` scoped to the bucket and the user's own folder. Add:

```sql
DROP POLICY IF EXISTS "avatars_user_upload" ON storage.objects;
CREATE POLICY "avatars_user_upload"
  ON storage.objects FOR INSERT TO authenticated
  WITH CHECK (bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text);

DROP POLICY IF EXISTS "avatars_user_update" ON storage.objects;
CREATE POLICY "avatars_user_update"
  ON storage.objects FOR UPDATE TO authenticated
  USING (bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text)
  WITH CHECK (bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text);

DROP POLICY IF EXISTS "avatars_user_select_own" ON storage.objects;
CREATE POLICY "avatars_user_select_own"
  ON storage.objects FOR SELECT TO authenticated
  USING (bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text);
```

Before finalizing, grep `react-frontend/src` and `expo-mobile` for `.list(` / `.download(` on `avatars`/`geojsons` to confirm nothing lists bucket contents (verified at planning time: no such calls exist).

## Category G — `auth_leaked_password_protection` (1 WARN)

Not fixable in SQL — it's an Auth setting. Add a comment in the migration noting the manual step, and mention it in your summary: **Supabase Dashboard → Authentication → Attack Protection → enable "Leaked password protection" (HaveIBeenPwned).**

## Verification checklist (all required before finishing)

- [ ] `git status` shows exactly one new file: `supabase/migrations/0025_security_lint_fixes.sql`
- [ ] Every statement is idempotent — running the file twice produces no errors
- [ ] All 22 SQL-fixable lint items are addressed; the 3 residuals are documented in comments (`is_admin` authenticated warning ×1 lint, the auth-config toggle, and note the storage/function warnings cleared)
- [ ] The migration has a header comment mapping sections to lint categories + the CSV filename
- [ ] Underlying-table grants/policies for the security_invoker views verified present (0009)
- [ ] `match_rag_chunks` has an explicit `GRANT EXECUTE TO service_role`
- [ ] Tell the user in your summary: apply via `supabase db query` / SQL Editor / `supabase migration up`, then re-run the linter (Dashboard → Advisors) to confirm; expected residual = `is_admin` authenticated warning only

## Guardrails

- Do NOT modify any existing migration file (0001–0024) or `supabase/table_scripts/*`
- Do NOT drop tables, columns, views, or data
- Do NOT change backend or frontend code — the fix must be behavior-compatible (service_role bypasses RLS; frontend uses public URLs + authenticated uploads)
- If any REVOKE/GRANT signature fails because a function's signature differs from what's listed, inspect the live DB (`\df+ public.<name>` or `information_schema.routines`) and use the real signature — do not guess
