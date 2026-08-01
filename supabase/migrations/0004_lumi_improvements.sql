-- LUMI Phase 1 — Schema hardening & coexistence migration
-- Goals:
--   1. Keep legacy suitability_* columns untouched for existing clients.
--   2. Add v2 suitability columns + confidence/factors on municipalities.
--   3. Add normalized municipality_suitability_v2 table.
--   4. Add audit/quality/cache tables.
--   5. Add indexes, materialized views, and helper functions.
--   6. Add basic RLS policies for user-scoped tables.

BEGIN;

-- ========================================================================
-- 1. Coexistence columns on municipalities (legacy + v2)
-- ========================================================================

ALTER TABLE public.municipalities
    ADD COLUMN IF NOT EXISTS solar_suitability_score_v2 numeric(5,2),
    ADD COLUMN IF NOT EXISTS solar_classification_v2 character varying(20),
    ADD COLUMN IF NOT EXISTS solar_confidence numeric(5,2),
    ADD COLUMN IF NOT EXISTS solar_factors_v2 jsonb,
    ADD COLUMN IF NOT EXISTS wind_suitability_score_v2 numeric(5,2),
    ADD COLUMN IF NOT EXISTS wind_classification_v2 character varying(20),
    ADD COLUMN IF NOT EXISTS wind_confidence numeric(5,2),
    ADD COLUMN IF NOT EXISTS wind_factors_v2 jsonb,
    ADD COLUMN IF NOT EXISTS hydro_suitability_score_v2 numeric(5,2),
    ADD COLUMN IF NOT EXISTS hydro_classification_v2 character varying(20),
    ADD COLUMN IF NOT EXISTS hydro_confidence numeric(5,2),
    ADD COLUMN IF NOT EXISTS hydro_factors_v2 jsonb,
    ADD COLUMN IF NOT EXISTS geothermal_suitability_score_v2 numeric(5,2),
    ADD COLUMN IF NOT EXISTS geothermal_classification_v2 character varying(20),
    ADD COLUMN IF NOT EXISTS geothermal_confidence numeric(5,2),
    ADD COLUMN IF NOT EXISTS geothermal_factors_v2 jsonb,
    ADD COLUMN IF NOT EXISTS composite_suitability_score_v2 numeric(5,2),
    ADD COLUMN IF NOT EXISTS composite_classification_v2 character varying(20),
    ADD COLUMN IF NOT EXISTS composite_confidence numeric(5,2),
    ADD COLUMN IF NOT EXISTS composite_factors_v2 jsonb,
    ADD COLUMN IF NOT EXISTS suitability_v2_updated_at timestamp with time zone;

COMMENT ON COLUMN public.municipalities.solar_suitability_score_v2 IS 'Improved solar suitability 0-100 with confidence and explainability.';
COMMENT ON COLUMN public.municipalities.solar_confidence IS 'Confidence 0-100 for the v2 solar suitability score.';

-- ========================================================================
-- 2. Normalized v2 suitability table (alternative to denormalized columns)
-- ========================================================================

CREATE TABLE IF NOT EXISTS public.municipality_suitability_v2 (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    municipality_id integer NOT NULL REFERENCES public.municipalities(municipality_id) ON DELETE CASCADE,
    renewable_type text NOT NULL CHECK (renewable_type IN ('solar','wind','hydro','geothermal','composite')),
    score numeric(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
    classification character varying(20),
    confidence numeric(5,2) CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 100)),
    factors jsonb,
    model_version text DEFAULT 'v2.0',
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT municipality_renewable_unique UNIQUE (municipality_id, renewable_type)
);

COMMENT ON TABLE public.municipality_suitability_v2 IS 'Normalized, versioned suitability scores. Coexists with legacy columns on municipalities.';

CREATE INDEX IF NOT EXISTS idx_muni_suit_v2_municipality_id ON public.municipality_suitability_v2 USING btree (municipality_id);
CREATE INDEX IF NOT EXISTS idx_muni_suit_v2_renewable_type_score ON public.municipality_suitability_v2 USING btree (renewable_type, score DESC);

-- ========================================================================
-- 3. Audit / request logs
-- ========================================================================

CREATE TABLE IF NOT EXISTS public.request_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    request_id text,
    method text NOT NULL,
    path text NOT NULL,
    status_code integer,
    duration_ms numeric(10,2),
    client_ip text,
    user_id uuid,
    user_agent text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_request_logs_created_at ON public.request_logs USING btree (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_request_logs_user_id ON public.request_logs USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_request_logs_path_method ON public.request_logs USING btree (path, method, created_at DESC);

COMMENT ON TABLE public.request_logs IS 'API access log for security, rate-limit tuning, and performance analytics.';

-- ========================================================================
-- 4. Data quality & ETL tracking
-- ========================================================================

CREATE TABLE IF NOT EXISTS public.data_quality_scores (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    source text NOT NULL,
    table_name text NOT NULL,
    record_count integer,
    missing_fields jsonb,
    outlier_count integer,
    duplicate_count integer,
    quality_score numeric(5,2),
    checked_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_data_quality_table ON public.data_quality_scores USING btree (table_name, checked_at DESC);

CREATE TABLE IF NOT EXISTS public.etl_run_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    pipeline text NOT NULL,
    run_type text NOT NULL CHECK (run_type IN ('scrape','clean','transform','load','full')),
    status text NOT NULL CHECK (status IN ('running','success','failed','partial')),
    records_processed integer,
    records_inserted integer,
    records_updated integer,
    records_failed integer,
    error_log jsonb,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone
);

CREATE INDEX IF NOT EXISTS idx_etl_run_log_pipeline_started ON public.etl_run_log USING btree (pipeline, started_at DESC);

-- ========================================================================
-- 5. Forecast cache table improvement (add composite index)
-- ========================================================================

CREATE INDEX IF NOT EXISTS idx_forecast_cache_target_model
    ON public.forecast_cache USING btree (target_variable, model_id, created_at DESC);

-- ========================================================================
-- 6. Materialized views for fast province/region aggregation
-- ========================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_province_renewable_potential AS
SELECT
    p.province_id,
    p.name AS province_name,
    p.region_id,
    COUNT(m.municipality_id) AS municipality_count,
    ROUND(AVG(m.solar_suitability_score_v2), 2) AS avg_solar_score,
    ROUND(AVG(m.wind_suitability_score_v2), 2) AS avg_wind_score,
    ROUND(AVG(m.hydro_suitability_score_v2), 2) AS avg_hydro_score,
    ROUND(AVG(m.geothermal_suitability_score_v2), 2) AS avg_geo_score,
    ROUND(AVG(m.composite_suitability_score_v2), 2) AS avg_composite_score,
    ROUND(MAX(m.solar_suitability_score_v2), 2) AS max_solar_score,
    ROUND(MAX(m.wind_suitability_score_v2), 2) AS max_wind_score,
    ROUND(MAX(m.hydro_suitability_score_v2), 2) AS max_hydro_score,
    ROUND(MAX(m.geothermal_suitability_score_v2), 2) AS max_geo_score
FROM public.provinces p
LEFT JOIN public.municipalities m ON m.province_id = p.province_id
GROUP BY p.province_id, p.name, p.region_id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_province_renewable_potential_id
    ON public.mv_province_renewable_potential (province_id);

CREATE INDEX IF NOT EXISTS idx_mv_province_renewable_composite
    ON public.mv_province_renewable_potential USING btree (avg_composite_score DESC NULLS LAST);

COMMENT ON MATERIALIZED VIEW public.mv_province_renewable_potential IS 'Pre-aggregated province-level renewable potential for map APIs and dashboards.';

-- ========================================================================
-- 7. Functions & triggers
-- ========================================================================

-- Update timestamp trigger helper
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_municipality_suitability_v2_updated_at
    ON public.municipality_suitability_v2;
CREATE TRIGGER trg_municipality_suitability_v2_updated_at
    BEFORE UPDATE ON public.municipality_suitability_v2
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Keep municipalities.suitability_v2_updated_at current when v2 table is written to.
CREATE OR REPLACE FUNCTION public.sync_municipality_suitability_timestamp()
RETURNS trigger AS $$
BEGIN
    UPDATE public.municipalities
    SET suitability_v2_updated_at = now()
    WHERE municipality_id = NEW.municipality_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_muni_suit_v2_timestamp
    ON public.municipality_suitability_v2;
CREATE TRIGGER trg_sync_muni_suit_v2_timestamp
    AFTER INSERT OR UPDATE ON public.municipality_suitability_v2
    FOR EACH ROW EXECUTE FUNCTION public.sync_municipality_suitability_timestamp();

-- Refresh materialized view helper (can be called by ETL or scheduled job)
CREATE OR REPLACE FUNCTION public.refresh_province_renewable_potential()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_province_renewable_potential;
END;
$$ LANGUAGE plpgsql;

-- ========================================================================
-- 8. RLS policies for user-scoped tables
-- ========================================================================

ALTER TABLE public.saved_locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS saved_locations_owner_policy ON public.saved_locations;
CREATE POLICY saved_locations_owner_policy ON public.saved_locations
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS saved_simulations_owner_policy ON public.saved_simulations;
CREATE POLICY saved_simulations_owner_policy ON public.saved_simulations
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS chat_sessions_owner_policy ON public.chat_sessions;
CREATE POLICY chat_sessions_owner_policy ON public.chat_sessions
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS chat_messages_owner_policy ON public.chat_messages;
CREATE POLICY chat_messages_owner_policy ON public.chat_messages
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.chat_sessions cs
            WHERE cs.id = chat_messages.session_id AND cs.user_id = auth.uid()
        )
    );

-- Admins can see request logs; service role bypasses RLS by default.
ALTER TABLE public.request_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS request_logs_admin_policy ON public.request_logs;
CREATE POLICY request_logs_admin_policy ON public.request_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            WHERE ur.user_id = auth.uid() AND ur.role = 'admin'
        )
    );

-- ========================================================================
-- 9. Data quality constraints on existing tables
-- ========================================================================

-- Ensure climate monthly year/month are sane
ALTER TABLE public.municipality_climate_monthly
    DROP CONSTRAINT IF EXISTS municipality_climate_monthly_year_check,
    ADD CONSTRAINT municipality_climate_monthly_year_check CHECK ((year >= 2010));

-- Ensure suitability scores are 0-100 when present
ALTER TABLE public.municipality_suitability_v2
    ADD CONSTRAINT municipality_suitability_v2_score_check
    CHECK (score >= 0 AND score <= 100);

-- Ensure lat/lon ranges for Philippines-ish bounding box (loose check)
ALTER TABLE public.municipalities
    ADD CONSTRAINT municipalities_lat_check CHECK (lat IS NULL OR (lat >= 4.0 AND lat <= 21.5)),
    ADD CONSTRAINT municipalities_lon_check CHECK (lon IS NULL OR (lon >= 116.0 AND lon <= 127.0));

-- National energy year must be recent/historical
ALTER TABLE public.national_energy_annual
    ADD CONSTRAINT national_energy_annual_year_check CHECK (year >= 1990 AND year <= 2100);

COMMIT;
