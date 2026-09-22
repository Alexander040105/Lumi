-- ============================================================================
-- Migration 0025: Supabase security lint fixes
--
-- Source: Supabase Performance Security Lints (husnkzlccdrjpwlqcfbt).csv
--         (25 findings in 7 categories, project husnkzlccdrjpwlqcfbt)
--
-- Categories addressed:
--   A. security_definer_view                    (3 ERROR) -> security_invoker views
--   B. rls_disabled_in_public                   (4 ERROR) -> enable RLS + policies
--   C. function_search_path_mutable             (3 WARN)  -> fixed search_path
--   D. anon_security_definer_function_executable      (6 WARN)  -> revoke EXECUTE
--   E. authenticated_security_definer_function_executable (6 WARN) -> revoke EXECUTE
--   F. public_bucket_allows_listing             (2 WARN)  -> drop broad SELECT policies
--   G. auth_leaked_password_protection          (1 WARN)  -> manual dashboard step (see bottom)
--   +. rls_enabled_no_policy                    (1 INFO)  -> forecast_model_runs policy
--
-- Accepted residuals (documented, intentional):
--   - public.is_admin() remains executable by `authenticated` because RLS
--     policies call it during evaluation. See Category D/E notes below.
--   - Leaked password protection is an Auth dashboard setting, not SQL.
--
-- This file is idempotent: every statement uses IF EXISTS / OR REPLACE /
-- plain REVOKE-GRANT, so it is safe to run more than once.
--
-- Architecture note: the FastAPI backend always connects via the
-- service_role key (app/services/supabase_service.py), which bypasses RLS,
-- so restricting anon/authenticated access cannot break backend processing.
-- ============================================================================


-- ============================================================================
-- Category A: security_definer_view (3 ERRORs)
--
-- These views were created without security_invoker, so they ran with the
-- view creator's (postgres) permissions and bypassed querying-user RLS.
-- Recreated identically WITH (security_invoker = true). Underlying tables
-- (regions, provinces, municipalities, barangays, geospatial_metadata,
-- province_climate_monthly) already have public SELECT grants + policies
-- from 0009_rls_hardening.sql, so reads keep working.
-- ============================================================================

CREATE OR REPLACE VIEW "public"."province_climate_annual"
WITH (security_invoker = true) AS
SELECT
    "province_id",
    "year",
    AVG("t2m") AS "avg_t2m",
    AVG("t2m_max") AS "avg_t2m_max",
    AVG("t2m_min") AS "avg_t2m_min",
    AVG("rh2m") AS "avg_rh2m",
    AVG("prectotcorr") AS "avg_prectotcorr",
    AVG("ws10m") AS "avg_ws10m",
    AVG("allsky_sfc_sw_dwn") AS "avg_allsky_sfc_sw_dwn",
    AVG("cloud_amt") AS "avg_cloud_amt",
    AVG("surface_pressure") AS "avg_surface_pressure",
    AVG("elevation") AS "avg_elevation",
    AVG("rhoa") AS "avg_rhoa"
FROM "public"."province_climate_monthly"
GROUP BY "province_id", "year"
ORDER BY "province_id", "year";

ALTER VIEW "public"."province_climate_annual" OWNER TO "postgres";

COMMENT ON VIEW "public"."province_climate_annual" IS 'Annual climate averages per province, aggregated from monthly data.';

-- regional_lookup was created manually via table_scripts/schema.sql (not in a
-- numbered migration); definition inlined here from the live database.
CREATE OR REPLACE VIEW "public"."regional_lookup"
WITH (security_invoker = true) AS
SELECT
    r."region_id",
    r."name" AS "region_name",
    r."lat" AS "region_lat",
    r."lon" AS "region_lon",
    p."province_id",
    p."name" AS "province_name",
    p."lat" AS "province_lat",
    p."lon" AS "province_lon",
    m."municipality_id",
    m."name" AS "municipality_name",
    m."lat" AS "municipality_lat",
    m."lon" AS "municipality_lon",
    b."barangay_id",
    b."name" AS "barangay_name",
    b."lat" AS "barangay_lat",
    b."lon" AS "barangay_lon"
FROM "public"."regions" r
JOIN "public"."provinces" p ON p."region_id" = r."region_id"
JOIN "public"."municipalities" m ON m."province_id" = p."province_id"
JOIN "public"."barangays" b ON b."municipality_id" = m."municipality_id";

ALTER VIEW "public"."regional_lookup" OWNER TO "postgres";

CREATE OR REPLACE VIEW "public"."regional_lookup_v2"
WITH (security_invoker = true) AS
SELECT
    r."region_id", r."name" AS "region_name",
    p."province_id", p."name" AS "province_name",
    m."municipality_id", m."name" AS "municipality_name",
    b."barangay_id", b."name" AS "barangay_name",
    -- Region geospatial
    rg."centroid_lat" AS "region_lat", rg."centroid_lon" AS "region_lon",
    rg."area_km2" AS "region_area_km2", rg."elevation_m" AS "region_elevation_m",
    -- Province geospatial
    pg."centroid_lat" AS "province_lat", pg."centroid_lon" AS "province_lon",
    pg."area_km2" AS "province_area_km2", pg."elevation_m" AS "province_elevation_m",
    -- Municipality geospatial
    mg."centroid_lat" AS "municipality_lat", mg."centroid_lon" AS "municipality_lon",
    mg."area_km2" AS "municipality_area_km2", mg."elevation_m" AS "municipality_elevation_m",
    -- Barangay geospatial
    bg."centroid_lat" AS "barangay_lat", bg."centroid_lon" AS "barangay_lon",
    bg."area_km2" AS "barangay_area_km2", bg."elevation_m" AS "barangay_elevation_m"
FROM "public"."regions" r
LEFT JOIN "public"."geospatial_metadata" rg ON rg."region_id" = r."region_id"
JOIN "public"."provinces" p ON p."region_id" = r."region_id"
LEFT JOIN "public"."geospatial_metadata" pg ON pg."province_id" = p."province_id"
JOIN "public"."municipalities" m ON m."province_id" = p."province_id"
LEFT JOIN "public"."geospatial_metadata" mg ON mg."municipality_id" = m."municipality_id"
JOIN "public"."barangays" b ON b."municipality_id" = m."municipality_id"
LEFT JOIN "public"."geospatial_metadata" bg ON bg."barangay_id" = b."barangay_id";

ALTER VIEW "public"."regional_lookup_v2" OWNER TO "postgres";

COMMENT ON VIEW "public"."regional_lookup_v2" IS 'Full geographic hierarchy with geospatial metadata. Extends regional_lookup with area and elevation.';

-- Re-issue view grants (0009 convention: SELECT for anon/authenticated,
-- ALL for service_role).
REVOKE ALL ON "public"."province_climate_annual" FROM PUBLIC, anon, authenticated, service_role;
GRANT SELECT ON "public"."province_climate_annual" TO anon, authenticated;
GRANT ALL ON "public"."province_climate_annual" TO service_role;

REVOKE ALL ON "public"."regional_lookup" FROM PUBLIC, anon, authenticated, service_role;
GRANT SELECT ON "public"."regional_lookup" TO anon, authenticated;
GRANT ALL ON "public"."regional_lookup" TO service_role;

REVOKE ALL ON "public"."regional_lookup_v2" FROM PUBLIC, anon, authenticated, service_role;
GRANT SELECT ON "public"."regional_lookup_v2" TO anon, authenticated;
GRANT ALL ON "public"."regional_lookup_v2" TO service_role;


-- ============================================================================
-- Category B: rls_disabled_in_public (4 ERRORs)
--
-- Public reference climate tables were exposed to PostgREST with no RLS.
-- Live state also showed anon/authenticated held ALL table privileges;
-- they are revoked down to SELECT, matching the 0009 convention.
-- The backend reads these via service_role and is unaffected.
-- ============================================================================

ALTER TABLE "public"."municipality_atlas_averages" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE "public"."municipality_atlas_averages" FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE "public"."municipality_atlas_averages" TO anon, authenticated;
GRANT ALL ON TABLE "public"."municipality_atlas_averages" TO service_role;
DROP POLICY IF EXISTS "municipality_atlas_averages_select_public" ON "public"."municipality_atlas_averages";
CREATE POLICY "municipality_atlas_averages_select_public"
  ON "public"."municipality_atlas_averages" FOR SELECT TO anon, authenticated
  USING (true);

ALTER TABLE "public"."province_atlas_averages" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE "public"."province_atlas_averages" FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE "public"."province_atlas_averages" TO anon, authenticated;
GRANT ALL ON TABLE "public"."province_atlas_averages" TO service_role;
DROP POLICY IF EXISTS "province_atlas_averages_select_public" ON "public"."province_atlas_averages";
CREATE POLICY "province_atlas_averages_select_public"
  ON "public"."province_atlas_averages" FOR SELECT TO anon, authenticated
  USING (true);

ALTER TABLE "public"."municipality_era5_averages" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE "public"."municipality_era5_averages" FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE "public"."municipality_era5_averages" TO anon, authenticated;
GRANT ALL ON TABLE "public"."municipality_era5_averages" TO service_role;
DROP POLICY IF EXISTS "municipality_era5_averages_select_public" ON "public"."municipality_era5_averages";
CREATE POLICY "municipality_era5_averages_select_public"
  ON "public"."municipality_era5_averages" FOR SELECT TO anon, authenticated
  USING (true);

ALTER TABLE "public"."province_era5_averages" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE "public"."province_era5_averages" FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE "public"."province_era5_averages" TO anon, authenticated;
GRANT ALL ON TABLE "public"."province_era5_averages" TO service_role;
DROP POLICY IF EXISTS "province_era5_averages_select_public" ON "public"."province_era5_averages";
CREATE POLICY "province_era5_averages_select_public"
  ON "public"."province_era5_averages" FOR SELECT TO anon, authenticated
  USING (true);

-- Bonus (INFO): forecast_model_runs has RLS enabled but zero policies.
-- Backend-only table; add an explicit service_role policy.
DROP POLICY IF EXISTS "forecast_model_runs_service_role" ON "public"."forecast_model_runs";
CREATE POLICY "forecast_model_runs_service_role"
  ON "public"."forecast_model_runs" TO service_role
  USING (true) WITH CHECK (true);


-- ============================================================================
-- Category C: function_search_path_mutable (3 WARNs)
--
-- Functions without a fixed search_path can be hijacked via schema
-- precedence. Signatures verified against the live database.
-- ============================================================================

ALTER FUNCTION "public"."set_updated_at"() SET search_path = pg_catalog, public;
ALTER FUNCTION "public"."get_suitability_classification"(numeric) SET search_path = pg_catalog, public;
ALTER FUNCTION "public"."handle_new_user"() SET search_path = pg_catalog, public;

-- (public.is_admin() already sets search_path = public in
--  0013_fix_is_admin_dev.sql — no change needed.)


-- ============================================================================
-- Categories D/E: executable SECURITY DEFINER functions (12 WARNs)
--
-- Postgres grants EXECUTE to PUBLIC by default, so these were callable via
-- /rest/v1/rpc/ by anyone. All are backend-only (service_role) or trigger
-- functions (triggers don't need EXECUTE grants).
--
-- match_rag_chunks NOTE: it previously relied on the implicit PUBLIC grant
-- (no explicit grant exists in 0007_rag_pgvector.sql), so the service_role
-- grant below is REQUIRED for RAG search to keep working.
-- ============================================================================

REVOKE EXECUTE ON FUNCTION "public"."get_admin_usage_summary"(integer, integer, text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION "public"."get_admin_usage_summary"(integer, integer, text) TO service_role;

REVOKE EXECUTE ON FUNCTION "public"."get_admin_users_list"(integer, integer, text, text, text, boolean) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION "public"."get_admin_users_list"(integer, integer, text, text, text, boolean) TO service_role;

REVOKE EXECUTE ON FUNCTION "public"."get_user_usage_report"(uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION "public"."get_user_usage_report"(uuid) TO service_role;

REVOKE EXECUTE ON FUNCTION "public"."handle_new_user"() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION "public"."handle_new_user"() TO service_role;

REVOKE EXECUTE ON FUNCTION "public"."match_rag_chunks"(extensions.vector, integer, double precision, text, text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION "public"."match_rag_chunks"(extensions.vector, integer, double precision, text, text) TO service_role;

-- is_admin(): PARTIAL revoke only — intentional.
--
-- is_admin() is called inside RLS policy expressions (USING (public.is_admin()))
-- across migrations 0009, 0010, 0015, and 0022. Postgres checks EXECUTE
-- against the querying role during policy evaluation, so revoking
-- `authenticated` would break every admin policy. The function returns only
-- a boolean about the current caller — no data exposure.
--
-- ACCEPTED RESIDUAL: the linter will continue to warn that `authenticated`
-- can execute a SECURITY DEFINER function. The alternative (inlining the
-- admin EXISTS check into ~10 policies) was rejected for maintainability —
-- the definition of "admin" changed once already (0013 added the dev role),
-- and a single helper is the only sane place for that logic.
REVOKE EXECUTE ON FUNCTION "public"."is_admin"() FROM PUBLIC, anon;
-- KEEP: authenticated + service_role (granted in 0013_fix_is_admin_dev.sql)


-- ============================================================================
-- Category F: public_bucket_allows_listing (2 WARNs)
--
-- Public buckets serve files by URL without any policy — these broad SELECT
-- policies only enabled anonymous listing of every filename in `avatars`
-- and `geojsons`. Dropping them does NOT break public URL access.
-- Verified: no `.list()` / `.download()` calls on these buckets in
-- react-frontend/src or expo-mobile.
-- ============================================================================

DROP POLICY IF EXISTS "Allow public read" ON storage.objects;
DROP POLICY IF EXISTS "Public read avatars" ON storage.objects;
DROP POLICY IF EXISTS "Public read on geojsons bucket" ON storage.objects;

-- Avatar uploads: the frontend calls
--   supabase.storage.from("avatars").upload("<uid>/avatar.ext", file, { upsert: true })
-- as an authenticated user. Upsert needs INSERT + UPDATE + SELECT, scoped to
-- the caller's own top-level folder. Equivalent scoped policies already
-- exist ("Allow authenticated upload/update", "Users manage own avatar");
-- these are kept explicit so uploads never depend on dashboard-created
-- policies.
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


-- ============================================================================
-- Category G: auth_leaked_password_protection (1 WARN) — MANUAL STEP
--
-- Not fixable in SQL. After applying this migration, enable it in:
--   Supabase Dashboard → Authentication → Attack Protection →
--   "Leaked password protection" (HaveIBeenPwned)
-- ============================================================================
