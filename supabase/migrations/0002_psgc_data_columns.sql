-- ============================================================================
-- LUMI PSGC Data Columns Migration
-- Migration: 0002_psgc_data_columns.sql
--
-- This migration:
--   1. Creates municipal_population table (referenced by energyhub.py but missing)
--   2. Creates population_data table for historical population tracking
--   3. Adds PSGC attribute columns to regions, provinces, municipalities, barangays
--   4. Adds indexes for new columns
--   5. Grants permissions and sets RLS
--
-- Safety: All CREATE TABLE use IF NOT EXISTS. All ALTER TABLE use IF NOT EXISTS.
-- No existing columns are dropped or modified.
-- ============================================================================

-- ============================================================================
-- SECTION 1: Create municipal_population table
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."municipal_population" (
    "municipality_id" integer NOT NULL,
    "province_id" integer NOT NULL,
    "population_2015" bigint,
    "population_2020" bigint,
    "population_2024" bigint,
    CONSTRAINT "municipal_population_pkey" PRIMARY KEY ("municipality_id")
);

ALTER TABLE "public"."municipal_population" OWNER TO "postgres";

COMMENT ON TABLE "public"."municipal_population" IS 'PSA population data per municipality. Used for population-weighted demand estimation in EnergyHub.';

COMMENT ON COLUMN "public"."municipal_population"."population_2015" IS 'PSA 2015 Census of Population.';
COMMENT ON COLUMN "public"."municipal_population"."population_2020" IS 'PSA 2020 Census of Population.';
COMMENT ON COLUMN "public"."municipal_population"."population_2024" IS 'PSA 2024 updated population estimates.';

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'municipal_population_municipality_id_fkey') THEN
        ALTER TABLE "public"."municipal_population"
            ADD CONSTRAINT "municipal_population_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'municipal_population_province_id_fkey') THEN
        ALTER TABLE "public"."municipal_population"
            ADD CONSTRAINT "municipal_population_province_id_fkey"
            FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id")
            ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================================
-- SECTION 2: Create population_data table for historical tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."population_data" (
    "id" uuid DEFAULT "gen_random_uuid"() NOT NULL,
    "psgc_code" text NOT NULL,
    "geographic_level" text NOT NULL,
    "year" integer NOT NULL,
    "population" bigint,
    CONSTRAINT "population_data_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "population_data_psgc_code_year_key" UNIQUE ("psgc_code", "year")
);

ALTER TABLE "public"."population_data" OWNER TO "postgres";

COMMENT ON TABLE "public"."population_data" IS 'Historical population records from PSA for all geographic levels. Supports time-series analysis.';

COMMENT ON COLUMN "public"."population_data"."psgc_code" IS '10-digit PSGC code identifying the geographic unit.';
COMMENT ON COLUMN "public"."population_data"."geographic_level" IS 'Level: region, province, municipality, or barangay.';
COMMENT ON COLUMN "public"."population_data"."year" IS 'Census year (e.g., 2015, 2020, 2024).';
COMMENT ON COLUMN "public"."population_data"."population" IS 'Population count for that year.';

-- ============================================================================
-- SECTION 3: Add PSGC attribute columns to admin tables
-- ============================================================================

-- regions
ALTER TABLE "public"."regions"
    ADD COLUMN IF NOT EXISTS "island_group" text;
ALTER TABLE "public"."regions"
    ADD COLUMN IF NOT EXISTS "population_2015" bigint;
ALTER TABLE "public"."regions"
    ADD COLUMN IF NOT EXISTS "population_2020" bigint;
ALTER TABLE "public"."regions"
    ADD COLUMN IF NOT EXISTS "population_2024" bigint;
ALTER TABLE "public"."regions"
    ADD COLUMN IF NOT EXISTS "geographic_level" text;

-- provinces
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "island_group" text;
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "income_classification" text;
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "population_2015" bigint;
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "population_2020" bigint;
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "population_2024" bigint;
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "geographic_level" text;
ALTER TABLE "public"."provinces"
    ADD COLUMN IF NOT EXISTS "old_name" text;

-- municipalities
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "island_group" text;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "income_classification" text;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "city_class" text;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "is_city" boolean DEFAULT false;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "population_2015" bigint;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "population_2020" bigint;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "population_2024" bigint;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "geographic_level" text;
ALTER TABLE "public"."municipalities"
    ADD COLUMN IF NOT EXISTS "old_name" text;

-- barangays
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "island_group" text;
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "urban_rural" text;
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "population_2015" bigint;
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "population_2020" bigint;
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "population_2024" bigint;
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "geographic_level" text;
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "old_name" text;
ALTER TABLE "public"."barangays"
    ADD COLUMN IF NOT EXISTS "status" text;

-- ============================================================================
-- SECTION 4: Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS "idx_municipal_population_province_id"
    ON "public"."municipal_population" USING "btree" ("province_id");

CREATE INDEX IF NOT EXISTS "idx_population_data_psgc_code"
    ON "public"."population_data" USING "btree" ("psgc_code");

CREATE INDEX IF NOT EXISTS "idx_population_data_level_year"
    ON "public"."population_data" USING "btree" ("geographic_level", "year");

CREATE INDEX IF NOT EXISTS "idx_barangays_psgc_code"
    ON "public"."barangays" USING "btree" ("psgc_code")
    WHERE "psgc_code" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "idx_municipalities_psgc_code"
    ON "public"."municipalities" USING "btree" ("psgc_code")
    WHERE "psgc_code" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "idx_provinces_psgc_code"
    ON "public"."provinces" USING "btree" ("psgc_code")
    WHERE "psgc_code" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "idx_regions_psgc_code"
    ON "public"."regions" USING "btree" ("psgc_code")
    WHERE "psgc_code" IS NOT NULL;

-- ============================================================================
-- SECTION 5: Grants and RLS
-- ============================================================================

GRANT ALL ON TABLE "public"."municipal_population" TO "anon";
GRANT ALL ON TABLE "public"."municipal_population" TO "authenticated";
GRANT ALL ON TABLE "public"."municipal_population" TO "service_role";

GRANT ALL ON TABLE "public"."population_data" TO "anon";
GRANT ALL ON TABLE "public"."population_data" TO "authenticated";
GRANT ALL ON TABLE "public"."population_data" TO "service_role";

ALTER TABLE "public"."municipal_population" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."population_data" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read on municipal_population"
    ON "public"."municipal_population" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on municipal_population"
    ON "public"."municipal_population" USING ("auth"."role"() = 'authenticated'::text);

CREATE POLICY "Allow public read on population_data"
    ON "public"."population_data" FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on population_data"
    ON "public"."population_data" USING ("auth"."role"() = 'authenticated'::text);
