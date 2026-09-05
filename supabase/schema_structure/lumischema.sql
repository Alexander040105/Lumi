


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";





SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."barangays" (
    "barangay_id" integer NOT NULL,
    "municipality_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision
);


ALTER TABLE "public"."barangays" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."hydropower_suitability" (
    "municipality_id" integer NOT NULL,
    "province_id" integer NOT NULL,
    "municipality_name" "text" NOT NULL,
    "province" "text" NOT NULL,
    "latitude" double precision,
    "longitude" double precision,
    "elevation_m" double precision,
    "mean_elevation_m" double precision,
    "min_elevation_m" double precision,
    "max_elevation_m" double precision,
    "elevation_range_m" double precision,
    "mean_slope_deg" double precision,
    "hydraulic_head_m" double precision,
    "terrain_ruggedness" double precision,
    "watershed_gradient" double precision,
    "hydro_suitability_score" double precision,
    "estimated_hydropower_potential_kw" double precision,
    "runoff_potential" double precision,
    "gravity_flow_potential" double precision,
    "terrain_flatness" double precision,
    "slope_classification" "text",
    "elevation_classification" "text",
    "ridge_elevation" double precision,
    "terrain_exposure_index" double precision
);


ALTER TABLE "public"."hydropower_suitability" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."municipalities" (
    "municipality_id" integer NOT NULL,
    "province_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision
);


ALTER TABLE "public"."municipalities" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."municipality_climate_monthly" (
    "municipality_id" integer NOT NULL,
    "year" smallint NOT NULL,
    "month" smallint NOT NULL,
    "t2m" double precision,
    "t2m_max" double precision,
    "t2m_min" double precision,
    "rh2m" double precision,
    "prectotcorr" double precision,
    "ws10m" double precision,
    "allsky_sfc_sw_dwn" double precision,
    "source" "text" DEFAULT 'NASA POWER'::"text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "cloud_amt" double precision,
    "surface_pressure" double precision,
    "elevation" double precision,
    "rhoa" double precision,
    CONSTRAINT "municipality_climate_monthly_month_check" CHECK ((("month" >= 1) AND ("month" <= 12))),
    CONSTRAINT "municipality_climate_monthly_year_check" CHECK (("year" >= 2018))
);


ALTER TABLE "public"."municipality_climate_monthly" OWNER TO "postgres";


COMMENT ON TABLE "public"."municipality_climate_monthly" IS 'Monthly historical climate data by municipality from NASA POWER.';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."t2m" IS 'Mean air temperature at 2m (C).';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."t2m_max" IS 'Maximum air temperature at 2m (C).';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."t2m_min" IS 'Minimum air temperature at 2m (C).';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."rh2m" IS 'Relative humidity at 2m (%).';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."prectotcorr" IS 'Precipitation corrected (mm/day).';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."ws10m" IS 'Wind speed at 10m (m/s).';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."allsky_sfc_sw_dwn" IS 'All-sky surface shortwave downward irradiance (kWh/m^2/day).';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."source" IS 'Data source identifier.';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."elevation" IS 'Elevation factor for Hydropower';



COMMENT ON COLUMN "public"."municipality_climate_monthly"."rhoa" IS 'Surface Air Density';



CREATE TABLE IF NOT EXISTS "public"."provinces" (
    "province_id" integer NOT NULL,
    "region_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision
);


ALTER TABLE "public"."provinces" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."regions" (
    "region_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision
);


ALTER TABLE "public"."regions" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."regional_lookup" AS
 SELECT "r"."region_id",
    "r"."name" AS "region_name",
    "r"."lat" AS "region_lat",
    "r"."lon" AS "region_lon",
    "p"."province_id",
    "p"."name" AS "province_name",
    "p"."lat" AS "province_lat",
    "p"."lon" AS "province_lon",
    "m"."municipality_id",
    "m"."name" AS "municipality_name",
    "m"."lat" AS "municipality_lat",
    "m"."lon" AS "municipality_lon",
    "b"."barangay_id",
    "b"."name" AS "barangay_name",
    "b"."lat" AS "barangay_lat",
    "b"."lon" AS "barangay_lon"
   FROM ((("public"."regions" "r"
     JOIN "public"."provinces" "p" ON (("p"."region_id" = "r"."region_id")))
     JOIN "public"."municipalities" "m" ON (("m"."province_id" = "p"."province_id")))
     JOIN "public"."barangays" "b" ON (("b"."municipality_id" = "m"."municipality_id")));


ALTER VIEW "public"."regional_lookup" OWNER TO "postgres";


ALTER TABLE ONLY "public"."barangays"
    ADD CONSTRAINT "barangays_pkey" PRIMARY KEY ("barangay_id");



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."municipalities"
    ADD CONSTRAINT "municipalities_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."municipality_climate_monthly"
    ADD CONSTRAINT "municipality_climate_monthly_pkey" PRIMARY KEY ("municipality_id", "year", "month");



ALTER TABLE ONLY "public"."provinces"
    ADD CONSTRAINT "provinces_pkey" PRIMARY KEY ("province_id");



ALTER TABLE ONLY "public"."regions"
    ADD CONSTRAINT "regions_pkey" PRIMARY KEY ("region_id");



CREATE INDEX "idx_barangays_municipality_id" ON "public"."barangays" USING "btree" ("municipality_id");



CREATE INDEX "idx_climate_monthly_municipality_id" ON "public"."municipality_climate_monthly" USING "btree" ("municipality_id");



CREATE INDEX "idx_climate_monthly_municipality_year_month" ON "public"."municipality_climate_monthly" USING "btree" ("municipality_id", "year", "month");



CREATE INDEX "idx_climate_monthly_year_month" ON "public"."municipality_climate_monthly" USING "btree" ("year", "month");



CREATE INDEX "idx_hydropower_suitability_municipality_name" ON "public"."hydropower_suitability" USING "btree" ("municipality_name");



CREATE INDEX "idx_hydropower_suitability_province_id" ON "public"."hydropower_suitability" USING "btree" ("province_id");



CREATE INDEX "idx_municipalities_province_id" ON "public"."municipalities" USING "btree" ("province_id");



CREATE INDEX "idx_provinces_region_id" ON "public"."provinces" USING "btree" ("region_id");



ALTER TABLE ONLY "public"."barangays"
    ADD CONSTRAINT "barangays_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."municipalities"
    ADD CONSTRAINT "municipalities_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."municipality_climate_monthly"
    ADD CONSTRAINT "municipality_climate_monthly_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."provinces"
    ADD CONSTRAINT "provinces_region_id_fkey" FOREIGN KEY ("region_id") REFERENCES "public"."regions"("region_id") ON UPDATE CASCADE ON DELETE RESTRICT;





ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";





































































































































































GRANT ALL ON TABLE "public"."barangays" TO "anon";
GRANT ALL ON TABLE "public"."barangays" TO "authenticated";
GRANT ALL ON TABLE "public"."barangays" TO "service_role";



GRANT ALL ON TABLE "public"."hydropower_suitability" TO "anon";
GRANT ALL ON TABLE "public"."hydropower_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."hydropower_suitability" TO "service_role";



GRANT ALL ON TABLE "public"."municipalities" TO "anon";
GRANT ALL ON TABLE "public"."municipalities" TO "authenticated";
GRANT ALL ON TABLE "public"."municipalities" TO "service_role";



GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "anon";
GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "authenticated";
GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "service_role";



GRANT ALL ON TABLE "public"."provinces" TO "anon";
GRANT ALL ON TABLE "public"."provinces" TO "authenticated";
GRANT ALL ON TABLE "public"."provinces" TO "service_role";



GRANT ALL ON TABLE "public"."regions" TO "anon";
GRANT ALL ON TABLE "public"."regions" TO "authenticated";
GRANT ALL ON TABLE "public"."regions" TO "service_role";



GRANT ALL ON TABLE "public"."regional_lookup" TO "anon";
GRANT ALL ON TABLE "public"."regional_lookup" TO "authenticated";
GRANT ALL ON TABLE "public"."regional_lookup" TO "service_role";









ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";































