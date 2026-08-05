-- ============================================================================
-- Migration 0009: RLS Hardening
-- ============================================================================
-- Replaces all over-permissive RLS policies with a least-privilege model.
--
-- Bootstrap admin (run once after migration, in Supabase SQL Editor):
--   UPDATE public.user_roles SET role = 'admin' WHERE user_id = '<uuid>';
--
-- Categories:
--   A: User-owned data (authenticated CRUD on own rows)
--   B: Public reference data (anon+authenticated SELECT, admin/dev write)
--   C: Suitability/output data (anon+authenticated SELECT, admin/dev write)
--   D: ML/forecast (authenticated SELECT, admin/dev write)
--   E: RAG & AI insights (SELECT varies, admin/dev write)
--   F: Admin-only (admin/dev SELECT, service_role INSERT)
-- ============================================================================

BEGIN;

-- ============================================================================
-- STEP 1: Drop ALL existing policies
-- ============================================================================

-- Category A: User-owned
DROP POLICY IF EXISTS "Admins read all profiles" ON public.profiles;
DROP POLICY IF EXISTS "Admins read all roles" ON public.user_roles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can view own usage" ON public.user_usage_limits;
DROP POLICY IF EXISTS "Users read own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users read own role" ON public.user_roles;
DROP POLICY IF EXISTS "Users update own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can CRUD own chat messages" ON public.chat_messages;
DROP POLICY IF EXISTS "Users can CRUD own chat sessions" ON public.chat_sessions;
DROP POLICY IF EXISTS "Users can CRUD own locations" ON public.saved_locations;
DROP POLICY IF EXISTS "Users can CRUD own simulations" ON public.saved_simulations;
DROP POLICY IF EXISTS "Users manage own chat messages" ON public.chat_messages;
DROP POLICY IF EXISTS "Users manage own chat sessions" ON public.chat_sessions;
DROP POLICY IF EXISTS "Users manage own simulations" ON public.saved_simulations;

-- Category B/C: Public reference + suitability
DROP POLICY IF EXISTS "Allow public read on barangay_climate_monthly" ON public.barangay_climate_monthly;
DROP POLICY IF EXISTS "Allow public read on composite_suitability" ON public.composite_suitability;
DROP POLICY IF EXISTS "Allow public read on doe_datasets" ON public.doe_datasets;
DROP POLICY IF EXISTS "Allow public read on geospatial_metadata" ON public.geospatial_metadata;
DROP POLICY IF EXISTS "Allow public read on geothermal_faults" ON public.geothermal_faults;
DROP POLICY IF EXISTS "Allow public read on geothermal_heatflow" ON public.geothermal_heatflow;
DROP POLICY IF EXISTS "Allow public read on geothermal_volcanoes" ON public.geothermal_volcanoes;
DROP POLICY IF EXISTS "Allow public read on hydro_suitability" ON public.hydro_suitability;
DROP POLICY IF EXISTS "Allow public read on ml_model_registry" ON public.ml_model_registry;
DROP POLICY IF EXISTS "Allow public read on municipal_population" ON public.municipal_population;
DROP POLICY IF EXISTS "Allow public read on municipality_climate_averages" ON public.municipality_climate_averages;
DROP POLICY IF EXISTS "Allow public read on national_energy_annual" ON public.national_energy_annual;
DROP POLICY IF EXISTS "Allow public read on population_data" ON public.population_data;
DROP POLICY IF EXISTS "Allow public read on products" ON public.products;
DROP POLICY IF EXISTS "Allow public read on province_climate_monthly" ON public.province_climate_monthly;
DROP POLICY IF EXISTS "Allow public read on solar_suitability" ON public.solar_suitability;
DROP POLICY IF EXISTS "Allow public read on wind_products" ON public.wind_products;
DROP POLICY IF EXISTS "Allow public read on wind_products_summary" ON public.wind_products_summary;
DROP POLICY IF EXISTS "Allow public read on wind_suitability" ON public.wind_suitability;
DROP POLICY IF EXISTS "Allow authenticated write on barangay_climate_monthly" ON public.barangay_climate_monthly;
DROP POLICY IF EXISTS "Allow authenticated write on composite_suitability" ON public.composite_suitability;
DROP POLICY IF EXISTS "Allow authenticated write on doe_datasets" ON public.doe_datasets;
DROP POLICY IF EXISTS "Allow authenticated write on geospatial_metadata" ON public.geospatial_metadata;
DROP POLICY IF EXISTS "Allow authenticated write on geothermal_faults" ON public.geothermal_faults;
DROP POLICY IF EXISTS "Allow authenticated write on geothermal_heatflow" ON public.geothermal_heatflow;
DROP POLICY IF EXISTS "Allow authenticated write on geothermal_volcanoes" ON public.geothermal_volcanoes;
DROP POLICY IF EXISTS "Allow authenticated write on hydro_suitability" ON public.hydro_suitability;
DROP POLICY IF EXISTS "Allow authenticated write on ml_model_registry" ON public.ml_model_registry;
DROP POLICY IF EXISTS "Allow authenticated write on municipal_population" ON public.municipal_population;
DROP POLICY IF EXISTS "Allow authenticated write on municipality_climate_averages" ON public.municipality_climate_averages;
DROP POLICY IF EXISTS "Allow authenticated write on national_energy_annual" ON public.national_energy_annual;
DROP POLICY IF EXISTS "Allow authenticated write on population_data" ON public.population_data;
DROP POLICY IF EXISTS "Allow authenticated write on products" ON public.products;
DROP POLICY IF EXISTS "Allow authenticated write on province_climate_monthly" ON public.province_climate_monthly;
DROP POLICY IF EXISTS "Allow authenticated write on solar_suitability" ON public.solar_suitability;
DROP POLICY IF EXISTS "Allow authenticated write on wind_products" ON public.wind_products;
DROP POLICY IF EXISTS "Allow authenticated write on wind_products_summary" ON public.wind_products_summary;
DROP POLICY IF EXISTS "Allow authenticated write on wind_suitability" ON public.wind_suitability;

-- Category D: ML/forecast
DROP POLICY IF EXISTS "Allow authenticated read on forecast_cache" ON public.forecast_cache;
DROP POLICY IF EXISTS "Allow authenticated write on forecast_cache" ON public.forecast_cache;
DROP POLICY IF EXISTS "Service role all on forecast_model_runs" ON public.forecast_model_runs;

-- Category E: RAG
DROP POLICY IF EXISTS "rag_chunks_select_policy" ON public.rag_chunks;
DROP POLICY IF EXISTS "rag_chunks_write_policy" ON public.rag_chunks;

-- Category F: Admin
DROP POLICY IF EXISTS "Admins can view audit log" ON public.admin_audit_log;
DROP POLICY IF EXISTS "Admins read audit log" ON public.admin_audit_log;
DROP POLICY IF EXISTS "Admins update system config" ON public.system_config;
DROP POLICY IF EXISTS "Anyone read system config" ON public.system_config;

-- ============================================================================
-- STEP 2: Fix GRANTs (revoke all, re-grant with least privilege)
-- ============================================================================

-- ---- Category A: User-owned tables ----

REVOKE ALL ON TABLE public.profiles FROM anon, authenticated;
GRANT SELECT, UPDATE ON TABLE public.profiles TO authenticated;
GRANT ALL ON TABLE public.profiles TO service_role;

REVOKE ALL ON TABLE public.user_roles FROM anon, authenticated;
GRANT SELECT ON TABLE public.user_roles TO authenticated;
GRANT ALL ON TABLE public.user_roles TO service_role;

REVOKE ALL ON TABLE public.user_usage_limits FROM anon, authenticated;
GRANT SELECT ON TABLE public.user_usage_limits TO authenticated;
GRANT ALL ON TABLE public.user_usage_limits TO service_role;

REVOKE ALL ON TABLE public.saved_locations FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.saved_locations TO authenticated;
GRANT ALL ON TABLE public.saved_locations TO service_role;

REVOKE ALL ON TABLE public.saved_simulations FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.saved_simulations TO authenticated;
GRANT ALL ON TABLE public.saved_simulations TO service_role;

REVOKE ALL ON TABLE public.chat_sessions FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.chat_sessions TO authenticated;
GRANT ALL ON TABLE public.chat_sessions TO service_role;

REVOKE ALL ON TABLE public.chat_messages FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.chat_messages TO authenticated;
GRANT ALL ON TABLE public.chat_messages TO service_role;

-- ---- Category B: Public reference tables ----

REVOKE ALL ON TABLE public.regions FROM anon, authenticated;
GRANT SELECT ON TABLE public.regions TO anon, authenticated;
GRANT ALL ON TABLE public.regions TO service_role;

REVOKE ALL ON TABLE public.provinces FROM anon, authenticated;
GRANT SELECT ON TABLE public.provinces TO anon, authenticated;
GRANT ALL ON TABLE public.provinces TO service_role;

REVOKE ALL ON TABLE public.municipalities FROM anon, authenticated;
GRANT SELECT ON TABLE public.municipalities TO anon, authenticated;
GRANT ALL ON TABLE public.municipalities TO service_role;

REVOKE ALL ON TABLE public.barangays FROM anon, authenticated;
GRANT SELECT ON TABLE public.barangays TO anon, authenticated;
GRANT ALL ON TABLE public.barangays TO service_role;

REVOKE ALL ON TABLE public.geospatial_metadata FROM anon, authenticated;
GRANT SELECT ON TABLE public.geospatial_metadata TO anon, authenticated;
GRANT ALL ON TABLE public.geospatial_metadata TO service_role;

REVOKE ALL ON TABLE public.barangay_climate_monthly FROM anon, authenticated;
GRANT SELECT ON TABLE public.barangay_climate_monthly TO anon, authenticated;
GRANT ALL ON TABLE public.barangay_climate_monthly TO service_role;

REVOKE ALL ON TABLE public.municipality_climate_monthly FROM anon, authenticated;
GRANT SELECT ON TABLE public.municipality_climate_monthly TO anon, authenticated;
GRANT ALL ON TABLE public.municipality_climate_monthly TO service_role;

REVOKE ALL ON TABLE public.province_climate_monthly FROM anon, authenticated;
GRANT SELECT ON TABLE public.province_climate_monthly TO anon, authenticated;
GRANT ALL ON TABLE public.province_climate_monthly TO service_role;

REVOKE ALL ON TABLE public.municipality_climate_averages FROM anon, authenticated;
GRANT SELECT ON TABLE public.municipality_climate_averages TO anon, authenticated;
GRANT ALL ON TABLE public.municipality_climate_averages TO service_role;

REVOKE ALL ON TABLE public.municipal_population FROM anon, authenticated;
GRANT SELECT ON TABLE public.municipal_population TO anon, authenticated;
GRANT ALL ON TABLE public.municipal_population TO service_role;

REVOKE ALL ON TABLE public.population_data FROM anon, authenticated;
GRANT SELECT ON TABLE public.population_data TO anon, authenticated;
GRANT ALL ON TABLE public.population_data TO service_role;

REVOKE ALL ON TABLE public.national_energy_annual FROM anon, authenticated;
GRANT SELECT ON TABLE public.national_energy_annual TO anon, authenticated;
GRANT ALL ON TABLE public.national_energy_annual TO service_role;

REVOKE ALL ON TABLE public.doe_datasets FROM anon, authenticated;
GRANT SELECT ON TABLE public.doe_datasets TO anon, authenticated;
GRANT ALL ON TABLE public.doe_datasets TO service_role;

-- ---- Category C: Suitability/output tables ----

REVOKE ALL ON TABLE public.solar_suitability FROM anon, authenticated;
GRANT SELECT ON TABLE public.solar_suitability TO anon, authenticated;
GRANT ALL ON TABLE public.solar_suitability TO service_role;

REVOKE ALL ON TABLE public.wind_suitability FROM anon, authenticated;
GRANT SELECT ON TABLE public.wind_suitability TO anon, authenticated;
GRANT ALL ON TABLE public.wind_suitability TO service_role;

REVOKE ALL ON TABLE public.hydro_suitability FROM anon, authenticated;
GRANT SELECT ON TABLE public.hydro_suitability TO anon, authenticated;
GRANT ALL ON TABLE public.hydro_suitability TO service_role;

REVOKE ALL ON TABLE public.geothermal_suitability FROM anon, authenticated;
GRANT SELECT ON TABLE public.geothermal_suitability TO anon, authenticated;
GRANT ALL ON TABLE public.geothermal_suitability TO service_role;

REVOKE ALL ON TABLE public.composite_suitability FROM anon, authenticated;
GRANT SELECT ON TABLE public.composite_suitability TO anon, authenticated;
GRANT ALL ON TABLE public.composite_suitability TO service_role;

REVOKE ALL ON TABLE public.geothermal_output FROM anon, authenticated;
GRANT SELECT ON TABLE public.geothermal_output TO anon, authenticated;
GRANT ALL ON TABLE public.geothermal_output TO service_role;

REVOKE ALL ON TABLE public.geothermal_faults FROM anon, authenticated;
GRANT SELECT ON TABLE public.geothermal_faults TO anon, authenticated;
GRANT ALL ON TABLE public.geothermal_faults TO service_role;

REVOKE ALL ON TABLE public.geothermal_heatflow FROM anon, authenticated;
GRANT SELECT ON TABLE public.geothermal_heatflow TO anon, authenticated;
GRANT ALL ON TABLE public.geothermal_heatflow TO service_role;

REVOKE ALL ON TABLE public.geothermal_volcanoes FROM anon, authenticated;
GRANT SELECT ON TABLE public.geothermal_volcanoes TO anon, authenticated;
GRANT ALL ON TABLE public.geothermal_volcanoes TO service_role;

REVOKE ALL ON TABLE public.hydropower_suitability FROM anon, authenticated;
GRANT SELECT ON TABLE public.hydropower_suitability TO anon, authenticated;
GRANT ALL ON TABLE public.hydropower_suitability TO service_role;

REVOKE ALL ON TABLE public.products FROM anon, authenticated;
GRANT SELECT ON TABLE public.products TO anon, authenticated;
GRANT ALL ON TABLE public.products TO service_role;

REVOKE ALL ON TABLE public.wind_products FROM anon, authenticated;
GRANT SELECT ON TABLE public.wind_products TO anon, authenticated;
GRANT ALL ON TABLE public.wind_products TO service_role;

REVOKE ALL ON TABLE public.wind_products_summary FROM anon, authenticated;
GRANT SELECT ON TABLE public.wind_products_summary TO anon, authenticated;
GRANT ALL ON TABLE public.wind_products_summary TO service_role;

REVOKE ALL ON TABLE public.mcda_weights FROM anon, authenticated;
GRANT SELECT ON TABLE public.mcda_weights TO anon, authenticated;
GRANT ALL ON TABLE public.mcda_weights TO service_role;

-- ---- Category D: ML/forecast tables ----

REVOKE ALL ON TABLE public.ml_model_registry FROM anon, authenticated;
GRANT SELECT ON TABLE public.ml_model_registry TO authenticated;
GRANT ALL ON TABLE public.ml_model_registry TO service_role;

REVOKE ALL ON TABLE public.forecast_cache FROM anon, authenticated;
GRANT SELECT ON TABLE public.forecast_cache TO authenticated;
GRANT ALL ON TABLE public.forecast_cache TO service_role;

REVOKE ALL ON TABLE public.forecast_model_runs FROM anon, authenticated;
GRANT ALL ON TABLE public.forecast_model_runs TO service_role;

-- ---- Category E: RAG & AI insights ----

REVOKE ALL ON TABLE public.rag_chunks FROM anon, authenticated;
GRANT SELECT ON TABLE public.rag_chunks TO anon, authenticated;
GRANT ALL ON TABLE public.rag_chunks TO service_role;

REVOKE ALL ON TABLE public.chart_ai_insights FROM anon, authenticated;
GRANT SELECT ON TABLE public.chart_ai_insights TO authenticated;
GRANT ALL ON TABLE public.chart_ai_insights TO service_role;

-- ---- Category F: Admin-only tables ----

REVOKE ALL ON TABLE public.admin_audit_log FROM anon, authenticated;
GRANT SELECT ON TABLE public.admin_audit_log TO authenticated;
GRANT ALL ON TABLE public.admin_audit_log TO service_role;

REVOKE ALL ON TABLE public.system_config FROM anon, authenticated;
GRANT SELECT ON TABLE public.system_config TO anon, authenticated;
GRANT ALL ON TABLE public.system_config TO service_role;

-- ---- Views (inherit RLS from base tables) ----

REVOKE ALL ON TABLE public.province_climate_annual FROM anon, authenticated;
GRANT SELECT ON TABLE public.province_climate_annual TO anon, authenticated;
GRANT ALL ON TABLE public.province_climate_annual TO service_role;

REVOKE ALL ON TABLE public.regional_lookup FROM anon, authenticated;
GRANT SELECT ON TABLE public.regional_lookup TO anon, authenticated;
GRANT ALL ON TABLE public.regional_lookup TO service_role;

REVOKE ALL ON TABLE public.regional_lookup_v2 FROM anon, authenticated;
GRANT SELECT ON TABLE public.regional_lookup_v2 TO anon, authenticated;
GRANT ALL ON TABLE public.regional_lookup_v2 TO service_role;

-- ---- Sequences: revoke anon, keep authenticated USAGE+SELECT ----

REVOKE ALL ON SEQUENCE public.geothermal_faults_id_seq FROM anon;
GRANT USAGE, SELECT ON SEQUENCE public.geothermal_faults_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.geothermal_faults_id_seq TO service_role;

REVOKE ALL ON SEQUENCE public.geothermal_heatflow_id_seq FROM anon;
GRANT USAGE, SELECT ON SEQUENCE public.geothermal_heatflow_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.geothermal_heatflow_id_seq TO service_role;

REVOKE ALL ON SEQUENCE public.geothermal_volcanoes_id_seq FROM anon;
GRANT USAGE, SELECT ON SEQUENCE public.geothermal_volcanoes_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.geothermal_volcanoes_id_seq TO service_role;

REVOKE ALL ON SEQUENCE public.mcda_weights_id_seq FROM anon;
GRANT USAGE, SELECT ON SEQUENCE public.mcda_weights_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.mcda_weights_id_seq TO service_role;

REVOKE ALL ON SEQUENCE public.products_id_seq FROM anon;
GRANT USAGE, SELECT ON SEQUENCE public.products_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.products_id_seq TO service_role;

REVOKE ALL ON SEQUENCE public.rag_chunks_id_seq FROM anon;
GRANT USAGE, SELECT ON SEQUENCE public.rag_chunks_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.rag_chunks_id_seq TO service_role;

REVOKE ALL ON SEQUENCE public.wind_products_id_seq FROM anon;
GRANT USAGE, SELECT ON SEQUENCE public.wind_products_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.wind_products_id_seq TO service_role;

-- ============================================================================
-- STEP 3: Enable RLS on tables that are missing it
-- ============================================================================

ALTER TABLE public.barangays ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chart_ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.geothermal_output ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.geothermal_suitability ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hydropower_suitability ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mcda_weights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.municipalities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.municipality_climate_monthly ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.provinces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regions ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- STEP 4: Create new policies
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Category A: User-owned data
-- ----------------------------------------------------------------------------

-- profiles: SELECT + UPDATE own row; admin can see/update all
CREATE POLICY "profiles_select_own_or_admin"
  ON public.profiles FOR SELECT TO authenticated
  USING (auth.uid() = id OR public.is_admin());

CREATE POLICY "profiles_update_own_or_admin"
  ON public.profiles FOR UPDATE TO authenticated
  USING (auth.uid() = id OR public.is_admin())
  WITH CHECK (auth.uid() = id OR public.is_admin());

-- user_roles: SELECT own or admin; no user INSERT/UPDATE/DELETE
CREATE POLICY "user_roles_select_own_or_admin"
  ON public.user_roles FOR SELECT TO authenticated
  USING (auth.uid() = user_id OR public.is_admin());

-- user_usage_limits: SELECT own or admin
CREATE POLICY "usage_limits_select_own_or_admin"
  ON public.user_usage_limits FOR SELECT TO authenticated
  USING (auth.uid() = user_id OR public.is_admin());

-- saved_locations: full CRUD own rows; admin can SELECT all
CREATE POLICY "saved_locations_select_own_or_admin"
  ON public.saved_locations FOR SELECT TO authenticated
  USING (auth.uid() = user_id OR public.is_admin());

CREATE POLICY "saved_locations_insert_own"
  ON public.saved_locations FOR INSERT TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "saved_locations_update_own"
  ON public.saved_locations FOR UPDATE TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "saved_locations_delete_own"
  ON public.saved_locations FOR DELETE TO authenticated
  USING (auth.uid() = user_id);

-- saved_simulations: full CRUD own rows; admin can SELECT all
CREATE POLICY "saved_simulations_select_own_or_admin"
  ON public.saved_simulations FOR SELECT TO authenticated
  USING (auth.uid() = user_id OR public.is_admin());

CREATE POLICY "saved_simulations_insert_own"
  ON public.saved_simulations FOR INSERT TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "saved_simulations_update_own"
  ON public.saved_simulations FOR UPDATE TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "saved_simulations_delete_own"
  ON public.saved_simulations FOR DELETE TO authenticated
  USING (auth.uid() = user_id);

-- chat_sessions: full CRUD own rows; admin can SELECT all
CREATE POLICY "chat_sessions_select_own_or_admin"
  ON public.chat_sessions FOR SELECT TO authenticated
  USING (auth.uid() = user_id OR public.is_admin());

CREATE POLICY "chat_sessions_insert_own"
  ON public.chat_sessions FOR INSERT TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "chat_sessions_update_own"
  ON public.chat_sessions FOR UPDATE TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "chat_sessions_delete_own"
  ON public.chat_sessions FOR DELETE TO authenticated
  USING (auth.uid() = user_id);

-- chat_messages: CRUD via session ownership; admin can SELECT all
CREATE POLICY "chat_messages_select_own_or_admin"
  ON public.chat_messages FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.chat_sessions s
      WHERE s.id = chat_messages.session_id
        AND s.user_id = auth.uid()
    )
    OR public.is_admin()
  );

CREATE POLICY "chat_messages_insert_own"
  ON public.chat_messages FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.chat_sessions s
      WHERE s.id = chat_messages.session_id
        AND s.user_id = auth.uid()
    )
  );

CREATE POLICY "chat_messages_update_own"
  ON public.chat_messages FOR UPDATE TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.chat_sessions s
      WHERE s.id = chat_messages.session_id
        AND s.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.chat_sessions s
      WHERE s.id = chat_messages.session_id
        AND s.user_id = auth.uid()
    )
  );

CREATE POLICY "chat_messages_delete_own"
  ON public.chat_messages FOR DELETE TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.chat_sessions s
      WHERE s.id = chat_messages.session_id
        AND s.user_id = auth.uid()
    )
  );

-- ----------------------------------------------------------------------------
-- Category B: Public reference data (anon+authenticated SELECT, admin/dev write)
-- ----------------------------------------------------------------------------

-- regions
CREATE POLICY "regions_select_public"
  ON public.regions FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "regions_write_admin"
  ON public.regions FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- provinces
CREATE POLICY "provinces_select_public"
  ON public.provinces FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "provinces_write_admin"
  ON public.provinces FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- municipalities
CREATE POLICY "municipalities_select_public"
  ON public.municipalities FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "municipalities_write_admin"
  ON public.municipalities FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- barangays
CREATE POLICY "barangays_select_public"
  ON public.barangays FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "barangays_write_admin"
  ON public.barangays FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- geospatial_metadata
CREATE POLICY "geospatial_metadata_select_public"
  ON public.geospatial_metadata FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "geospatial_metadata_write_admin"
  ON public.geospatial_metadata FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- barangay_climate_monthly
CREATE POLICY "barangay_climate_monthly_select_public"
  ON public.barangay_climate_monthly FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "barangay_climate_monthly_write_admin"
  ON public.barangay_climate_monthly FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- municipality_climate_monthly
CREATE POLICY "municipality_climate_monthly_select_public"
  ON public.municipality_climate_monthly FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "municipality_climate_monthly_write_admin"
  ON public.municipality_climate_monthly FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- province_climate_monthly
CREATE POLICY "province_climate_monthly_select_public"
  ON public.province_climate_monthly FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "province_climate_monthly_write_admin"
  ON public.province_climate_monthly FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- municipality_climate_averages
CREATE POLICY "municipality_climate_averages_select_public"
  ON public.municipality_climate_averages FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "municipality_climate_averages_write_admin"
  ON public.municipality_climate_averages FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- municipal_population
CREATE POLICY "municipal_population_select_public"
  ON public.municipal_population FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "municipal_population_write_admin"
  ON public.municipal_population FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- population_data
CREATE POLICY "population_data_select_public"
  ON public.population_data FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "population_data_write_admin"
  ON public.population_data FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- national_energy_annual
CREATE POLICY "national_energy_annual_select_public"
  ON public.national_energy_annual FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "national_energy_annual_write_admin"
  ON public.national_energy_annual FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- doe_datasets
CREATE POLICY "doe_datasets_select_public"
  ON public.doe_datasets FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "doe_datasets_write_admin"
  ON public.doe_datasets FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ----------------------------------------------------------------------------
-- Category C: Suitability/output data (anon+authenticated SELECT, admin/dev write)
-- ----------------------------------------------------------------------------

-- solar_suitability
CREATE POLICY "solar_suitability_select_public"
  ON public.solar_suitability FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "solar_suitability_write_admin"
  ON public.solar_suitability FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- wind_suitability
CREATE POLICY "wind_suitability_select_public"
  ON public.wind_suitability FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "wind_suitability_write_admin"
  ON public.wind_suitability FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- hydro_suitability
CREATE POLICY "hydro_suitability_select_public"
  ON public.hydro_suitability FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "hydro_suitability_write_admin"
  ON public.hydro_suitability FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- geothermal_suitability
CREATE POLICY "geothermal_suitability_select_public"
  ON public.geothermal_suitability FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "geothermal_suitability_write_admin"
  ON public.geothermal_suitability FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- composite_suitability
CREATE POLICY "composite_suitability_select_public"
  ON public.composite_suitability FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "composite_suitability_write_admin"
  ON public.composite_suitability FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- geothermal_output
CREATE POLICY "geothermal_output_select_public"
  ON public.geothermal_output FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "geothermal_output_write_admin"
  ON public.geothermal_output FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- geothermal_faults
CREATE POLICY "geothermal_faults_select_public"
  ON public.geothermal_faults FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "geothermal_faults_write_admin"
  ON public.geothermal_faults FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- geothermal_heatflow
CREATE POLICY "geothermal_heatflow_select_public"
  ON public.geothermal_heatflow FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "geothermal_heatflow_write_admin"
  ON public.geothermal_heatflow FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- geothermal_volcanoes
CREATE POLICY "geothermal_volcanoes_select_public"
  ON public.geothermal_volcanoes FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "geothermal_volcanoes_write_admin"
  ON public.geothermal_volcanoes FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- hydropower_suitability
CREATE POLICY "hydropower_suitability_select_public"
  ON public.hydropower_suitability FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "hydropower_suitability_write_admin"
  ON public.hydropower_suitability FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- products
CREATE POLICY "products_select_public"
  ON public.products FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "products_write_admin"
  ON public.products FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- wind_products
CREATE POLICY "wind_products_select_public"
  ON public.wind_products FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "wind_products_write_admin"
  ON public.wind_products FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- wind_products_summary
CREATE POLICY "wind_products_summary_select_public"
  ON public.wind_products_summary FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "wind_products_summary_write_admin"
  ON public.wind_products_summary FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- mcda_weights
CREATE POLICY "mcda_weights_select_public"
  ON public.mcda_weights FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "mcda_weights_write_admin"
  ON public.mcda_weights FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ----------------------------------------------------------------------------
-- Category D: ML/forecast (authenticated SELECT, admin/dev write)
-- ----------------------------------------------------------------------------

-- ml_model_registry
CREATE POLICY "ml_model_registry_select_authenticated"
  ON public.ml_model_registry FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "ml_model_registry_write_admin"
  ON public.ml_model_registry FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- forecast_cache
CREATE POLICY "forecast_cache_select_authenticated"
  ON public.forecast_cache FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "forecast_cache_write_admin"
  ON public.forecast_cache FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- forecast_model_runs: service_role only — no policies needed
-- (GRANT only to service_role; RLS enabled but no policies = no access for anon/authenticated)

-- ----------------------------------------------------------------------------
-- Category E: RAG & AI insights
-- ----------------------------------------------------------------------------

-- rag_chunks: public SELECT, admin/dev write
CREATE POLICY "rag_chunks_select_public"
  ON public.rag_chunks FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "rag_chunks_write_admin"
  ON public.rag_chunks FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- chart_ai_insights: authenticated SELECT, admin/dev write
CREATE POLICY "chart_ai_insights_select_authenticated"
  ON public.chart_ai_insights FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "chart_ai_insights_write_admin"
  ON public.chart_ai_insights FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ----------------------------------------------------------------------------
-- Category F: Admin-only
-- ----------------------------------------------------------------------------

-- admin_audit_log: admin/dev SELECT, service_role INSERT (via backend), no UPDATE/DELETE
CREATE POLICY "admin_audit_log_select_admin"
  ON public.admin_audit_log FOR SELECT TO authenticated
  USING (public.is_admin());

CREATE POLICY "admin_audit_log_insert_service"
  ON public.admin_audit_log FOR INSERT TO authenticated
  WITH CHECK (auth.role() = 'service_role');

-- system_config: public SELECT, admin/dev write
CREATE POLICY "system_config_select_public"
  ON public.system_config FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "system_config_write_admin"
  ON public.system_config FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ============================================================================
-- STEP 5: Verify (informational — safe to run after migration)
-- ============================================================================

-- List any tables still missing RLS (should return 0 rows):
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND rowsecurity = false;

-- List all policies (should be exactly the ones created above):
-- SELECT tablename, policyname, cmd, roles FROM pg_policies WHERE schemaname = 'public' ORDER BY tablename, policyname;

COMMIT;
