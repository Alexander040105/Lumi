-- LUMI Municipality Suitability Migration
-- Adds renewable energy suitability scoring columns to the municipalities table.
-- Run this against your Supabase project after confirming the municipalities table exists.

-- =============================================================================
-- SOLAR SUITABILITY
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS solar_suitability_score NUMERIC(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS solar_classification VARCHAR(20) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS solar_factors JSONB DEFAULT NULL;

-- =============================================================================
-- WIND SUITABILITY
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS wind_suitability_score NUMERIC(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS wind_classification VARCHAR(20) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS wind_factors JSONB DEFAULT NULL;

-- =============================================================================
-- HYDRO SUITABILITY
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS hydro_suitability_score NUMERIC(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS hydro_classification VARCHAR(20) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS hydro_factors JSONB DEFAULT NULL;

-- =============================================================================
-- GEOTHERMAL SUITABILITY
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS geothermal_suitability_score NUMERIC(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS geothermal_classification VARCHAR(20) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS geothermal_factors JSONB DEFAULT NULL;

-- =============================================================================
-- COMPOSITE SUITABILITY (average of available individual scores)
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS composite_suitability_score NUMERIC(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS composite_classification VARCHAR(20) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS composite_factors JSONB DEFAULT NULL;

-- =============================================================================
-- METADATA
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS suitability_updated_at TIMESTAMPTZ DEFAULT NULL;

-- =============================================================================
-- INDEXES for fast choropleth map queries
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_muni_solar_score
    ON public.municipalities(solar_suitability_score)
    WHERE solar_suitability_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_muni_wind_score
    ON public.municipalities(wind_suitability_score)
    WHERE wind_suitability_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_muni_hydro_score
    ON public.municipalities(hydro_suitability_score)
    WHERE hydro_suitability_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_muni_geo_score
    ON public.municipalities(geothermal_suitability_score)
    WHERE geothermal_suitability_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_muni_composite_score
    ON public.municipalities(composite_suitability_score)
    WHERE composite_suitability_score IS NOT NULL;

-- =============================================================================
-- HELPER FUNCTION: Classification from score
-- =============================================================================
CREATE OR REPLACE FUNCTION public.get_suitability_classification(score NUMERIC)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF score IS NULL THEN RETURN NULL; END IF;
    IF score >= 81 THEN RETURN 'Very High'; END IF;
    IF score >= 61 THEN RETURN 'High'; END IF;
    IF score >= 41 THEN RETURN 'Moderate'; END IF;
    IF score >= 21 THEN RETURN 'Low'; END IF;
    RETURN 'Very Low';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =============================================================================
-- COMMENTS for documentation
-- =============================================================================
COMMENT ON COLUMN public.municipalities.solar_suitability_score IS 'Solar suitability 0-100 based on irradiance and temperature';
COMMENT ON COLUMN public.municipalities.wind_suitability_score IS 'Wind suitability 0-100 based on wind speed';
COMMENT ON COLUMN public.municipalities.hydro_suitability_score IS 'Hydropower suitability 0-100 based on terrain and rainfall';
COMMENT ON COLUMN public.municipalities.geothermal_suitability_score IS 'Geothermal suitability 0-100 based on heat flow and fault proximity';
COMMENT ON COLUMN public.municipalities.composite_suitability_score IS 'Average of available renewable suitability scores';
COMMENT ON COLUMN public.municipalities.composite_factors IS 'JSONB of individual scores that contributed to the composite';
COMMENT ON COLUMN public.municipalities.suitability_updated_at IS 'Timestamp of last suitability recalculation';
