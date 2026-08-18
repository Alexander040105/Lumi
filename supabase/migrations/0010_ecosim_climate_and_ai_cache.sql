-- supabase/migrations/0010_ecosim_climate_and_ai_cache.sql

-- ---------------------------------------------------------------------------
-- EcoSim climate data (Option B: Supabase source of truth)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.municipality_climate_averages (
    municipality_id integer PRIMARY KEY,
    avg_t2m double precision,
    avg_t2m_max double precision,
    avg_t2m_min double precision,
    avg_rh2m double precision,
    avg_rhoa double precision,
    avg_prectotcorr double precision,
    avg_ws10m double precision,
    avg_allsky_sfc_sw_dwn double precision,
    avg_cloud_amt double precision,
    avg_surface_pressure double precision,
    elevation double precision,
    updated_at timestamptz DEFAULT now(),
    CONSTRAINT municipality_climate_averages_municipality_id_fkey
        FOREIGN KEY (municipality_id) REFERENCES public.municipalities(municipality_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- If the table was already created by 0008 with elevation as integer, widen it.
ALTER TABLE public.municipality_climate_averages
    ALTER COLUMN elevation TYPE double precision USING elevation::double precision;

CREATE INDEX IF NOT EXISTS idx_municipality_climate_averages_municipality_id
    ON public.municipality_climate_averages(municipality_id);

COMMENT ON TABLE public.municipality_climate_averages IS
    'Pre-computed NASA POWER climate averages per municipality (used by EcoSim).';

ALTER TABLE public.municipality_climate_averages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "municipality_climate_averages_select_public" ON public.municipality_climate_averages;
CREATE POLICY "municipality_climate_averages_select_public"
    ON public.municipality_climate_averages FOR SELECT TO anon, authenticated
    USING (true);

DROP POLICY IF EXISTS "municipality_climate_averages_write_admin" ON public.municipality_climate_averages;
CREATE POLICY "municipality_climate_averages_write_admin"
    ON public.municipality_climate_averages FOR ALL TO authenticated
    USING (public.is_admin())
    WITH CHECK (public.is_admin());

-- ---------------------------------------------------------------------------
-- EcoSim AI response cache
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.ecosim_ai_cache (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cache_key text NOT NULL UNIQUE,
    municipality_id integer,
    inputs_hash text NOT NULL,
    ai_result jsonb NOT NULL,
    model_version text DEFAULT 'v1',
    expires_at timestamptz NOT NULL,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ecosim_ai_cache_lookup
    ON public.ecosim_ai_cache (cache_key, expires_at);

COMMENT ON TABLE public.ecosim_ai_cache IS
    'Cached Gemini AI analyses for EcoSim to avoid token exhaustion and timeouts.';

ALTER TABLE public.ecosim_ai_cache ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "ecosim_ai_cache_select_public" ON public.ecosim_ai_cache;
CREATE POLICY "ecosim_ai_cache_select_public"
    ON public.ecosim_ai_cache FOR SELECT TO anon, authenticated
    USING (true);

DROP POLICY IF EXISTS "ecosim_ai_cache_write_admin" ON public.ecosim_ai_cache;
CREATE POLICY "ecosim_ai_cache_write_admin"
    ON public.ecosim_ai_cache FOR ALL TO authenticated
    USING (public.is_admin())
    WITH CHECK (public.is_admin());
