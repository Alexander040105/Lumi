-- supabase/migrations/0022_catchment_enrichment.sql

-- ---------------------------------------------------------------------------
-- Municipality catchment enrichment (Boothroyd et al. 2023)
-- ---------------------------------------------------------------------------
-- Per-municipality catchment morphology and nearest-stream data from the
-- national-scale geodatabase of Philippine catchment characteristics.
--
-- Data source (CC-BY 4.0):
--   Boothroyd, R.J., Williams, R.D., Hoey, T.B., et al. (2023).
--   National-scale geodatabase of catchment characteristics in the
--   Philippines for river management applications.
--   PLOS ONE, 18(3), e0281933.
--   https://pmc.ncbi.nlm.nih.gov/articles/PMC9994713/
--
-- Coverage: 46.3% of municipalities fall within a catchment polygon;
-- 53.7% use nearest-catchment fallback. 100% have nearest-stream data.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.municipality_catchment_enrichment (
    municipality_id integer NOT NULL,
    province_id integer NOT NULL,

    -- Catchment assignment
    catchment_name text,
    catchment_match_method text,          -- 'within' or 'nearest'
    catchment_distance_m double precision, -- 0 if within

    -- Catchment morphology (from shapefile + topographic CSV)
    catchment_area_km2 double precision,
    catchment_mean_slope_deg double precision,
    catchment_relief_m double precision,
    catchment_drainage_density_km_km2 double precision,
    catchment_hypsometric_integral double precision,
    catchment_ruggedness_number double precision,
    catchment_melton_ruggedness double precision,
    catchment_mean_stream_slope_m_m double precision,

    -- Nearest household-relevant stream (order 1-2)
    nearest_stream_gradient_m_m double precision,
    nearest_stream_upstream_area_km2 double precision,
    nearest_stream_order integer,
    nearest_stream_elevation_m double precision,
    distance_to_nearest_stream_m double precision,

    -- Derived household-scale fields
    effective_catchment_area_km2 double precision,
    stream_head_m double precision,
    stream_feasibility_penalty double precision,
    enriched_runoff_coefficient double precision,

    -- Metadata
    data_source text NOT NULL DEFAULT 'Boothroyd et al. 2023 (PMC9994713)',
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT municipality_catchment_enrichment_pkey PRIMARY KEY (municipality_id),
    CONSTRAINT municipality_catchment_enrichment_municipality_id_fkey
        FOREIGN KEY (municipality_id) REFERENCES public.municipalities(municipality_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT municipality_catchment_enrichment_province_id_fkey
        FOREIGN KEY (province_id) REFERENCES public.provinces(province_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_catchment_enrichment_province
    ON public.municipality_catchment_enrichment (province_id);

CREATE INDEX IF NOT EXISTS idx_catchment_enrichment_catchment_name
    ON public.municipality_catchment_enrichment (catchment_name);

COMMENT ON TABLE public.municipality_catchment_enrichment IS
    'Per-municipality catchment morphology and nearest-stream data from Boothroyd et al. 2023 national geodatabase (PMC9994713). Used by EcoSim to replace fixed hydro assumptions with real terrain data.';

COMMENT ON COLUMN public.municipality_catchment_enrichment.catchment_match_method IS
    'How the municipality was assigned to a catchment: "within" (centroid inside polygon) or "nearest" (closest catchment by distance).';

COMMENT ON COLUMN public.municipality_catchment_enrichment.stream_head_m IS
    'Estimated hydraulic head from nearest stream gradient × assumed penstock length (100 m). Replaces DEM-derived municipal head.';

COMMENT ON COLUMN public.municipality_catchment_enrichment.stream_feasibility_penalty IS
    '0.1-1.0 multiplier reflecting distance to nearest stream. 1.0 within 2 km, decays to 0.1 at 10+ km.';

COMMENT ON COLUMN public.municipality_catchment_enrichment.effective_catchment_area_km2 IS
    'Household-scale catchment area = real basin area × 0.001 fraction, capped at 1.0 km². Replaces fixed 1.0 km² assumption.';

COMMENT ON COLUMN public.municipality_catchment_enrichment.enriched_runoff_coefficient IS
    'Runoff coefficient refined by drainage density and hypsometric integral. Replaces slope-only coefficient.';

-- Row Level Security (matching the pattern from 0010_ecosim_climate_and_ai_cache.sql)
ALTER TABLE public.municipality_catchment_enrichment ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "catchment_enrichment_select_public"
    ON public.municipality_catchment_enrichment;
CREATE POLICY "catchment_enrichment_select_public"
    ON public.municipality_catchment_enrichment FOR SELECT TO anon, authenticated
    USING (true);

DROP POLICY IF EXISTS "catchment_enrichment_write_admin"
    ON public.municipality_catchment_enrichment;
CREATE POLICY "catchment_enrichment_write_admin"
    ON public.municipality_catchment_enrichment FOR ALL TO authenticated
    USING (public.is_admin())
    WITH CHECK (public.is_admin());
