-- ============================================================================
-- LUMI Geospatial Database Architecture Migration
-- Migration: 0001_geospatial_architecture.sql
--
-- This migration:
--   1. Adds psgc_code/area_km2 to admin tables where missing
--   2. Creates geospatial_metadata table (centroids, area, elevation)
--   3. Creates province_climate_monthly table
--   4. Creates barangay_climate_monthly table
--   5. Extracts suitability scores into standalone tables
--   6. Migrates data from municipalities → new suitability tables
--   7. Migrates terrain data from hydropower_suitability → new hydro_suitability
--   8. Adds geo_level/geo_id to forecast_cache
--   9. Creates province_climate_annual view
--  10. Creates regional_lookup_v2 view
--  11. Grants permissions and sets RLS
--  12. Adds updated_at triggers
--
-- Safety: All CREATE TABLE use IF NOT EXISTS. Old columns in municipalities
-- are NOT dropped — they are deprecated and will be removed in a future cleanup.
-- ============================================================================

-- ============================================================================
-- SECTION 1: ALTER existing admin tables
-- ============================================================================

-- Add psgc_code and area_km2 to regions
ALTER TABLE "public"."regions"
    ADD COLUMN IF NOT EXISTS "psgc_code" text;
ALTER TABLE "public"."regions"
    ADD COLUMN IF NOT EXISTS "area_km2" double precision;

-- Add psgc_code and area_km2 to provinces
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "psgc_code" text;
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "area_km2" double precision;

-- Add psgc_code and area_km2 to municipalities
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "psgc_code" text;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "area_km2" double precision;

-- Add psgc_code and area_km2 to barangays
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "psgc_code" text;
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "area_km2" double precision;

-- ============================================================================
-- SECTION 2: geospatial_metadata table
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."geospatial_metadata" (
    "id" uuid DEFAULT gen_random_uuid() NOT NULL,
    "region_id" integer,
    "province_id" integer,
    "municipality_id" integer,
    "barangay_id" integer,
    "centroid_lat" double precision,
    "centroid_lon" double precision,
    "area_km2" double precision,
    "elevation_m" double precision,
    "crs" text DEFAULT 'EPSG:4326' NOT NULL,
    "source" text,
    "created_at" timestamp with time zone DEFAULT now() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT "geospatial_metadata_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "geospatial_metadata_exactly_one_geo" CHECK (
        (CASE WHEN region_id IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN province_id IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN municipality_id IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN barangay_id IS NOT NULL THEN 1 ELSE 0 END) = 1
    )
);

ALTER TABLE "public"."geospatial_metadata" OWNER TO "postgres";

COMMENT ON TABLE "public"."geospatial_metadata" IS 'Geospatial metadata (centroid, area, elevation) for each administrative level. Exactly one geo FK must be set.';

COMMENT ON COLUMN "public"."geospatial_metadata"."centroid_lat" IS 'Latitude of the centroid — used for NASA POWER API, OpenWeather API, map centering.';
COMMENT ON COLUMN "public"."geospatial_metadata"."centroid_lon" IS 'Longitude of the centroid — used for NASA POWER API, OpenWeather API, map centering.';
COMMENT ON COLUMN "public"."geospatial_metadata"."area_km2" IS 'Land area in km² — used for density calculations and area-weighted interpolation.';
COMMENT ON COLUMN "public"."geospatial_metadata"."elevation_m" IS 'Mean elevation in meters — affects solar efficiency, hydropower head, wind extrapolation.';
COMMENT ON COLUMN "public"."geospatial_metadata"."crs" IS 'Coordinate Reference System identifier. Default EPSG:4326 (WGS84).';
COMMENT ON COLUMN "public"."geospatial_metadata"."source" IS 'Data provenance: PSA, PhilAtlas, GeoJSON centroid, etc.';

-- Indexes for geospatial_metadata
CREATE INDEX IF NOT EXISTS "idx_geospatial_region_id"
    ON "public"."geospatial_metadata" USING "btree" ("region_id")
    WHERE "region_id" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "idx_geospatial_province_id"
    ON "public"."geospatial_metadata" USING "btree" ("province_id")
    WHERE "province_id" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "idx_geospatial_municipality_id"
    ON "public"."geospatial_metadata" USING "btree" ("municipality_id")
    WHERE "municipality_id" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "idx_geospatial_barangay_id"
    ON "public"."geospatial_metadata" USING "btree" ("barangay_id")
    WHERE "barangay_id" IS NOT NULL;

-- Foreign keys for geospatial_metadata
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'geospatial_metadata_region_id_fkey') THEN
        ALTER TABLE "public"."geospatial_metadata"
            ADD CONSTRAINT "geospatial_metadata_region_id_fkey"
            FOREIGN KEY ("region_id") REFERENCES "public"."regions"("region_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'geospatial_metadata_province_id_fkey') THEN
        ALTER TABLE "public"."geospatial_metadata"
            ADD CONSTRAINT "geospatial_metadata_province_id_fkey"
            FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'geospatial_metadata_municipality_id_fkey') THEN
        ALTER TABLE "public"."geospatial_metadata"
            ADD CONSTRAINT "geospatial_metadata_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'geospatial_metadata_barangay_id_fkey') THEN
        ALTER TABLE "public"."geospatial_metadata"
            ADD CONSTRAINT "geospatial_metadata_barangay_id_fkey"
            FOREIGN KEY ("barangay_id") REFERENCES "public"."barangays"("barangay_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================================
-- SECTION 3: province_climate_monthly table
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."province_climate_monthly" (
    "province_id" integer NOT NULL,
    "year" smallint NOT NULL,
    "month" smallint NOT NULL,
    "t2m" double precision,
    "t2m_max" double precision,
    "t2m_min" double precision,
    "rh2m" double precision,
    "prectotcorr" double precision,
    "ws10m" double precision,
    "allsky_sfc_sw_dwn" double precision,
    "source" text DEFAULT 'NASA POWER' NOT NULL,
    "created_at" timestamp with time zone DEFAULT now() NOT NULL,
    "cloud_amt" double precision,
    "surface_pressure" double precision,
    "elevation" double precision,
    "rhoa" double precision,
    CONSTRAINT "province_climate_monthly_pkey" PRIMARY KEY ("province_id", "year", "month"),
    CONSTRAINT "province_climate_monthly_month_check" CHECK (("month" >= 1 AND "month" <= 12)),
    CONSTRAINT "province_climate_monthly_year_check" CHECK ("year" >= 2010)
);

ALTER TABLE "public"."province_climate_monthly" OWNER TO "postgres";

COMMENT ON TABLE "public"."province_climate_monthly" IS 'Monthly historical climate data by province from NASA POWER. Aggregated from municipality climate data or direct API calls.';

COMMENT ON COLUMN "public"."province_climate_monthly"."t2m" IS 'Mean air temperature at 2m (C).';
COMMENT ON COLUMN "public"."province_climate_monthly"."t2m_max" IS 'Maximum air temperature at 2m (C).';
COMMENT ON COLUMN "public"."province_climate_monthly"."t2m_min" IS 'Minimum air temperature at 2m (C).';
COMMENT ON COLUMN "public"."province_climate_monthly"."rh2m" IS 'Relative humidity at 2m (%).';
COMMENT ON COLUMN "public"."province_climate_monthly"."prectotcorr" IS 'Precipitation corrected (mm/day).';
COMMENT ON COLUMN "public"."province_climate_monthly"."ws10m" IS 'Wind speed at 10m (m/s).';
COMMENT ON COLUMN "public"."province_climate_monthly"."allsky_sfc_sw_dwn" IS 'All-sky surface shortwave downward irradiance (kWh/m^2/day).';
COMMENT ON COLUMN "public"."province_climate_monthly"."source" IS 'Data source identifier.';
COMMENT ON COLUMN "public"."province_climate_monthly"."elevation" IS 'Mean elevation for the province (m).';
COMMENT ON COLUMN "public"."province_climate_monthly"."rhoa" IS 'Surface air density.';

CREATE INDEX IF NOT EXISTS "idx_province_climate_monthly_province_id"
    ON "public"."province_climate_monthly" USING "btree" ("province_id");

CREATE INDEX IF NOT EXISTS "idx_province_climate_monthly_province_year_month"
    ON "public"."province_climate_monthly" USING "btree" ("province_id", "year", "month");

CREATE INDEX IF NOT EXISTS "idx_province_climate_monthly_year_month"
    ON "public"."province_climate_monthly" USING "btree" ("year", "month");

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'province_climate_monthly_province_id_fkey') THEN
        ALTER TABLE "public"."province_climate_monthly"
            ADD CONSTRAINT "province_climate_monthly_province_id_fkey"
            FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id")
            ON UPDATE CASCADE ON DELETE RESTRICT;
    END IF;
END $$;

-- ============================================================================
-- SECTION 4: barangay_climate_monthly table
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."barangay_climate_monthly" (
    "barangay_id" integer NOT NULL,
    "year" smallint NOT NULL,
    "month" smallint NOT NULL,
    "t2m" double precision,
    "t2m_max" double precision,
    "t2m_min" double precision,
    "rh2m" double precision,
    "prectotcorr" double precision,
    "ws10m" double precision,
    "allsky_sfc_sw_dwn" double precision,
    "source" text DEFAULT 'NASA POWER' NOT NULL,
    "created_at" timestamp with time zone DEFAULT now() NOT NULL,
    "cloud_amt" double precision,
    "surface_pressure" double precision,
    "elevation" double precision,
    "rhoa" double precision,
    CONSTRAINT "barangay_climate_monthly_pkey" PRIMARY KEY ("barangay_id", "year", "month"),
    CONSTRAINT "barangay_climate_monthly_month_check" CHECK (("month" >= 1 AND "month" <= 12)),
    CONSTRAINT "barangay_climate_monthly_year_check" CHECK ("year" >= 2010)
);

ALTER TABLE "public"."barangay_climate_monthly" OWNER TO "postgres";

COMMENT ON TABLE "public"."barangay_climate_monthly" IS 'Monthly historical climate data by barangay. Populated via NASA POWER API using barangay centroids, or interpolated from parent municipality data.';

COMMENT ON COLUMN "public"."barangay_climate_monthly"."t2m" IS 'Mean air temperature at 2m (C).';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."t2m_max" IS 'Maximum air temperature at 2m (C).';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."t2m_min" IS 'Minimum air temperature at 2m (C).';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."rh2m" IS 'Relative humidity at 2m (%).';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."prectotcorr" IS 'Precipitation corrected (mm/day).';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."ws10m" IS 'Wind speed at 10m (m/s).';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."allsky_sfc_sw_dwn" IS 'All-sky surface shortwave downward irradiance (kWh/m^2/day).';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."source" IS 'Data source identifier.';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."elevation" IS 'Elevation at barangay centroid (m).';
COMMENT ON COLUMN "public"."barangay_climate_monthly"."rhoa" IS 'Surface air density.';

CREATE INDEX IF NOT EXISTS "idx_barangay_climate_monthly_barangay_id"
    ON "public"."barangay_climate_monthly" USING "btree" ("barangay_id");

CREATE INDEX IF NOT EXISTS "idx_barangay_climate_monthly_barangay_year_month"
    ON "public"."barangay_climate_monthly" USING "btree" ("barangay_id", "year", "month");

CREATE INDEX IF NOT EXISTS "idx_barangay_climate_monthly_year_month"
    ON "public"."barangay_climate_monthly" USING "btree" ("year", "month");

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'barangay_climate_monthly_barangay_id_fkey') THEN
        ALTER TABLE "public"."barangay_climate_monthly"
            ADD CONSTRAINT "barangay_climate_monthly_barangay_id_fkey"
            FOREIGN KEY ("barangay_id") REFERENCES "public"."barangays"("barangay_id")
            ON UPDATE CASCADE ON DELETE RESTRICT;
    END IF;
END $$;

-- ============================================================================
-- SECTION 5: Standalone suitability tables (extracted from municipalities)
-- ============================================================================

-- solar_suitability
CREATE TABLE IF NOT EXISTS "public"."solar_suitability" (
    "municipality_id" integer NOT NULL,
    "score" numeric(5,2),
    "classification" character varying(20),
    "factors" jsonb,
    "updated_at" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT "solar_suitability_pkey" PRIMARY KEY ("municipality_id")
);

ALTER TABLE "public"."solar_suitability" OWNER TO "postgres";

COMMENT ON TABLE "public"."solar_suitability" IS 'Solar energy suitability scores per municipality. Extracted from municipalities table for normalization.';

CREATE INDEX IF NOT EXISTS "idx_solar_suitability_score"
    ON "public"."solar_suitability" USING "btree" ("score")
    WHERE "score" IS NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'solar_suitability_municipality_id_fkey') THEN
        ALTER TABLE "public"."solar_suitability"
            ADD CONSTRAINT "solar_suitability_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
END $$;

-- wind_suitability
CREATE TABLE IF NOT EXISTS "public"."wind_suitability" (
    "municipality_id" integer NOT NULL,
    "score" numeric(5,2),
    "classification" character varying(20),
    "factors" jsonb,
    "updated_at" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT "wind_suitability_pkey" PRIMARY KEY ("municipality_id")
);

ALTER TABLE "public"."wind_suitability" OWNER TO "postgres";

COMMENT ON TABLE "public"."wind_suitability" IS 'Wind energy suitability scores per municipality. Extracted from municipalities table for normalization.';

CREATE INDEX IF NOT EXISTS "idx_wind_suitability_score"
    ON "public"."wind_suitability" USING "btree" ("score")
    WHERE "score" IS NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'wind_suitability_municipality_id_fkey') THEN
        ALTER TABLE "public"."wind_suitability"
            ADD CONSTRAINT "wind_suitability_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
END $$;

-- hydro_suitability (clean — replaces denormalized hydropower_suitability)
CREATE TABLE IF NOT EXISTS "public"."hydro_suitability" (
    "municipality_id" integer NOT NULL,
    "score" numeric(5,2),
    "classification" character varying(20),
    "factors" jsonb,
    "hydraulic_head_m" double precision,
    "mean_elevation_m" double precision,
    "min_elevation_m" double precision,
    "max_elevation_m" double precision,
    "elevation_range_m" double precision,
    "mean_slope_deg" double precision,
    "terrain_ruggedness" double precision,
    "watershed_gradient" double precision,
    "runoff_potential" double precision,
    "gravity_flow_potential" double precision,
    "terrain_flatness" double precision,
    "estimated_hydropower_potential_kw" double precision,
    "slope_classification" text,
    "elevation_classification" text,
    "ridge_elevation" double precision,
    "terrain_exposure_index" double precision,
    "updated_at" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT "hydro_suitability_pkey" PRIMARY KEY ("municipality_id")
);

ALTER TABLE "public"."hydro_suitability" OWNER TO "postgres";

COMMENT ON TABLE "public"."hydro_suitability" IS 'Hydropower suitability and terrain metrics per municipality. Normalized version — no duplicated admin columns.';

CREATE INDEX IF NOT EXISTS "idx_hydro_suitability_score"
    ON "public"."hydro_suitability" USING "btree" ("score")
    WHERE "score" IS NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'hydro_suitability_municipality_id_fkey') THEN
        ALTER TABLE "public"."hydro_suitability"
            ADD CONSTRAINT "hydro_suitability_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
END $$;

-- composite_suitability
CREATE TABLE IF NOT EXISTS "public"."composite_suitability" (
    "municipality_id" integer NOT NULL,
    "score" numeric(5,2),
    "classification" character varying(20),
    "updated_at" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT "composite_suitability_pkey" PRIMARY KEY ("municipality_id")
);

ALTER TABLE "public"."composite_suitability" OWNER TO "postgres";

COMMENT ON TABLE "public"."composite_suitability" IS 'Composite renewable energy suitability score per municipality. Average of available renewable suitability scores.';

CREATE INDEX IF NOT EXISTS "idx_composite_suitability_score"
    ON "public"."composite_suitability" USING "btree" ("score")
    WHERE "score" IS NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'composite_suitability_municipality_id_fkey') THEN
        ALTER TABLE "public"."composite_suitability"
            ADD CONSTRAINT "composite_suitability_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================================
-- SECTION 6: Migrate data from municipalities → new suitability tables
-- ============================================================================

INSERT INTO "public"."solar_suitability" ("municipality_id", "score", "classification", "factors", "updated_at")
SELECT "municipality_id", "solar_suitability_score", "solar_classification", "solar_factors", COALESCE("suitability_updated_at", now())
FROM "public"."municipalities"
WHERE "solar_suitability_score" IS NOT NULL
ON CONFLICT ("municipality_id") DO NOTHING;

INSERT INTO "public"."wind_suitability" ("municipality_id", "score", "classification", "factors", "updated_at")
SELECT "municipality_id", "wind_suitability_score", "wind_classification", "wind_factors", COALESCE("suitability_updated_at", now())
FROM "public"."municipalities"
WHERE "wind_suitability_score" IS NOT NULL
ON CONFLICT ("municipality_id") DO NOTHING;

INSERT INTO "public"."composite_suitability" ("municipality_id", "score", "classification", "updated_at")
SELECT "municipality_id", "composite_suitability_score", "composite_classification", COALESCE("suitability_updated_at", now())
FROM "public"."municipalities"
WHERE "composite_suitability_score" IS NOT NULL
ON CONFLICT ("municipality_id") DO NOTHING;

-- ============================================================================
-- SECTION 7: Migrate terrain data from hydropower_suitability → new hydro_suitability
-- ============================================================================

INSERT INTO "public"."hydro_suitability" (
    "municipality_id", "score", "classification",
    "hydraulic_head_m", "mean_elevation_m", "min_elevation_m", "max_elevation_m",
    "elevation_range_m", "mean_slope_deg", "terrain_ruggedness", "watershed_gradient",
    "runoff_potential", "gravity_flow_potential", "terrain_flatness",
    "estimated_hydropower_potential_kw", "slope_classification", "elevation_classification",
    "ridge_elevation", "terrain_exposure_index", "updated_at"
)
SELECT
    h."municipality_id",
    m."hydro_suitability_score",
    m."hydro_classification",
    h."hydraulic_head_m",
    h."mean_elevation_m",
    h."min_elevation_m",
    h."max_elevation_m",
    h."elevation_range_m",
    h."mean_slope_deg",
    h."terrain_ruggedness",
    h."watershed_gradient",
    h."runoff_potential",
    h."gravity_flow_potential",
    h."terrain_flatness",
    h."estimated_hydropower_potential_kw",
    h."slope_classification",
    h."elevation_classification",
    h."ridge_elevation",
    h."terrain_exposure_index",
    COALESCE(m."suitability_updated_at", now())
FROM "public"."hydropower_suitability" h
JOIN "public"."municipalities" m ON h."municipality_id" = m."municipality_id"
ON CONFLICT ("municipality_id") DO NOTHING;

-- Also migrate hydro_factors from municipalities
UPDATE "public"."hydro_suitability" hs
SET "factors" = m."hydro_factors"
FROM "public"."municipalities" m
WHERE hs."municipality_id" = m."municipality_id"
  AND m."hydro_factors" IS NOT NULL
  AND hs."factors" IS NULL;

-- ============================================================================
-- SECTION 8: Add geo_level/geo_id to forecast_cache
-- ============================================================================

ALTER TABLE "public"."forecast_cache"
    ADD COLUMN IF NOT EXISTS "geo_level" text DEFAULT 'national';
ALTER TABLE "public"."forecast_cache"
    ADD COLUMN IF NOT EXISTS "geo_id" integer;

-- Add CHECK constraint for geo_level
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'forecast_cache_geo_level_check') THEN
        ALTER TABLE "public"."forecast_cache"
            ADD CONSTRAINT "forecast_cache_geo_level_check"
            CHECK ("geo_level" IN ('national', 'province', 'municipality', 'barangay'));
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS "idx_forecast_cache_geo"
    ON "public"."forecast_cache" USING "btree" ("geo_level", "geo_id")
    WHERE "geo_id" IS NOT NULL;

COMMENT ON COLUMN "public"."forecast_cache"."geo_level" IS 'Geographic level: national (default), province, municipality, or barangay.';
COMMENT ON COLUMN "public"."forecast_cache"."geo_id" IS 'Geographic ID — province_id, municipality_id, or barangay_id. NULL for national.';

-- ============================================================================
-- SECTION 9: province_climate_annual view
-- ============================================================================

CREATE OR REPLACE VIEW "public"."province_climate_annual" AS
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

-- ============================================================================
-- SECTION 10: regional_lookup_v2 view (includes geospatial_metadata)
-- ============================================================================

CREATE OR REPLACE VIEW "public"."regional_lookup_v2" AS
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

-- ============================================================================
-- SECTION 11: Migrate existing lat/lon from admin tables to geospatial_metadata
-- ============================================================================

-- Regions
INSERT INTO "public"."geospatial_metadata" ("region_id", "centroid_lat", "centroid_lon", "source")
SELECT "region_id", "lat", "lon", 'existing'
FROM "public"."regions"
WHERE "lat" IS NOT NULL AND "lon" IS NOT NULL
ON CONFLICT DO NOTHING;

-- Provinces
INSERT INTO "public"."geospatial_metadata" ("province_id", "centroid_lat", "centroid_lon", "source")
SELECT "province_id", "lat", "lon", 'existing'
FROM "public"."provinces"
WHERE "lat" IS NOT NULL AND "lon" IS NOT NULL
ON CONFLICT DO NOTHING;

-- Municipalities
INSERT INTO "public"."geospatial_metadata" ("municipality_id", "centroid_lat", "centroid_lon", "source")
SELECT "municipality_id", "lat", "lon", 'existing'
FROM "public"."municipalities"
WHERE "lat" IS NOT NULL AND "lon" IS NOT NULL
ON CONFLICT DO NOTHING;

-- Barangays
INSERT INTO "public"."geospatial_metadata" ("barangay_id", "centroid_lat", "centroid_lon", "source")
SELECT "barangay_id", "lat", "lon", 'existing'
FROM "public"."barangays"
WHERE "lat" IS NOT NULL AND "lon" IS NOT NULL
ON CONFLICT DO NOTHING;

-- ============================================================================
-- SECTION 12: Triggers for updated_at on new tables
-- ============================================================================

CREATE OR REPLACE TRIGGER "trg_geospatial_metadata_updated"
    BEFORE UPDATE ON "public"."geospatial_metadata"
    FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();

CREATE OR REPLACE TRIGGER "trg_solar_suitability_updated"
    BEFORE UPDATE ON "public"."solar_suitability"
    FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();

CREATE OR REPLACE TRIGGER "trg_wind_suitability_updated"
    BEFORE UPDATE ON "public"."wind_suitability"
    FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();

CREATE OR REPLACE TRIGGER "trg_hydro_suitability_updated"
    BEFORE UPDATE ON "public"."hydro_suitability"
    FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();

CREATE OR REPLACE TRIGGER "trg_composite_suitability_updated"
    BEFORE UPDATE ON "public"."composite_suitability"
    FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();

-- ============================================================================
-- SECTION 13: Grants and permissions
-- ============================================================================

-- geospatial_metadata
GRANT ALL ON TABLE "public"."geospatial_metadata" TO "anon";
GRANT ALL ON TABLE "public"."geospatial_metadata" TO "authenticated";
GRANT ALL ON TABLE "public"."geospatial_metadata" TO "service_role";

-- province_climate_monthly
GRANT ALL ON TABLE "public"."province_climate_monthly" TO "anon";
GRANT ALL ON TABLE "public"."province_climate_monthly" TO "authenticated";
GRANT ALL ON TABLE "public"."province_climate_monthly" TO "service_role";

-- barangay_climate_monthly
GRANT ALL ON TABLE "public"."barangay_climate_monthly" TO "anon";
GRANT ALL ON TABLE "public"."barangay_climate_monthly" TO "authenticated";
GRANT ALL ON TABLE "public"."barangay_climate_monthly" TO "service_role";

-- solar_suitability
GRANT ALL ON TABLE "public"."solar_suitability" TO "anon";
GRANT ALL ON TABLE "public"."solar_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."solar_suitability" TO "service_role";

-- wind_suitability
GRANT ALL ON TABLE "public"."wind_suitability" TO "anon";
GRANT ALL ON TABLE "public"."wind_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."wind_suitability" TO "service_role";

-- hydro_suitability
GRANT ALL ON TABLE "public"."hydro_suitability" TO "anon";
GRANT ALL ON TABLE "public"."hydro_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."hydro_suitability" TO "service_role";

-- composite_suitability
GRANT ALL ON TABLE "public"."composite_suitability" TO "anon";
GRANT ALL ON TABLE "public"."composite_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."composite_suitability" TO "service_role";

-- Views
GRANT ALL ON TABLE "public"."province_climate_annual" TO "anon";
GRANT ALL ON TABLE "public"."province_climate_annual" TO "authenticated";
GRANT ALL ON TABLE "public"."province_climate_annual" TO "service_role";

GRANT ALL ON TABLE "public"."regional_lookup_v2" TO "anon";
GRANT ALL ON TABLE "public"."regional_lookup_v2" TO "authenticated";
GRANT ALL ON TABLE "public"."regional_lookup_v2" TO "service_role";

-- ============================================================================
-- SECTION 14: RLS policies (public read for geospatial and climate data)
-- ============================================================================

ALTER TABLE "public"."geospatial_metadata" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."province_climate_monthly" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."barangay_climate_monthly" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."solar_suitability" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."wind_suitability" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."hydro_suitability" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."composite_suitability" ENABLE ROW LEVEL SECURITY;

-- Public read policies
CREATE POLICY "Allow public read on geospatial_metadata"
    ON "public"."geospatial_metadata" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on geospatial_metadata"
    ON "public"."geospatial_metadata" USING ("auth"."role"() = 'authenticated'::text);

CREATE POLICY "Allow public read on province_climate_monthly"
    ON "public"."province_climate_monthly" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on province_climate_monthly"
    ON "public"."province_climate_monthly" USING ("auth"."role"() = 'authenticated'::text);

CREATE POLICY "Allow public read on barangay_climate_monthly"
    ON "public"."barangay_climate_monthly" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on barangay_climate_monthly"
    ON "public"."barangay_climate_monthly" USING ("auth"."role"() = 'authenticated'::text);

CREATE POLICY "Allow public read on solar_suitability"
    ON "public"."solar_suitability" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on solar_suitability"
    ON "public"."solar_suitability" USING ("auth"."role"() = 'authenticated'::text);

CREATE POLICY "Allow public read on wind_suitability"
    ON "public"."wind_suitability" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on wind_suitability"
    ON "public"."wind_suitability" USING ("auth"."role"() = 'authenticated'::text);

CREATE POLICY "Allow public read on hydro_suitability"
    ON "public"."hydro_suitability" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on hydro_suitability"
    ON "public"."hydro_suitability" USING ("auth"."role"() = 'authenticated'::text);

CREATE POLICY "Allow public read on composite_suitability"
    ON "public"."composite_suitability" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on composite_suitability"
    ON "public"."composite_suitability" USING ("auth"."role"() = 'authenticated'::text);

-- ============================================================================
-- COMPLETE
-- ============================================================================
