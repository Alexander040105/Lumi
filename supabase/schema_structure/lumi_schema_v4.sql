


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






CREATE TYPE "public"."app_role" AS ENUM (
    'user',
    'admin',
    'dev'
);


ALTER TYPE "public"."app_role" OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_suitability_classification"("score" numeric) RETURNS character varying
    LANGUAGE "plpgsql" IMMUTABLE
    AS $$
BEGIN
    IF score IS NULL THEN RETURN NULL; END IF;
    IF score >= 81 THEN RETURN 'Very High'; END IF;
    IF score >= 61 THEN RETURN 'High'; END IF;
    IF score >= 41 THEN RETURN 'Moderate'; END IF;
    IF score >= 21 THEN RETURN 'Low'; END IF;
    RETURN 'Very Low';
END;
$$;


ALTER FUNCTION "public"."get_suitability_classification"("score" numeric) OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."handle_new_user"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name');

    INSERT INTO public.user_roles (user_id, role)
    VALUES (NEW.id, 'user');

    INSERT INTO public.user_usage_limits (user_id, plan)
    VALUES (NEW.id, 'free');

    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."handle_new_user"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."set_updated_at"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."set_updated_at"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."admin_audit_log" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "admin_id" "uuid",
    "action" "text" NOT NULL,
    "target_user_id" "uuid",
    "details" "jsonb" DEFAULT '{}'::"jsonb",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."admin_audit_log" OWNER TO "postgres";


COMMENT ON TABLE "public"."admin_audit_log" IS 'Immutable log of administrative actions for accountability.';



CREATE TABLE IF NOT EXISTS "public"."barangays" (
    "barangay_id" integer NOT NULL,
    "municipality_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision
);


ALTER TABLE "public"."barangays" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."chart_ai_insights" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "chart_type" "text" NOT NULL,
    "chart_data_hash" "text" NOT NULL,
    "insight" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."chart_ai_insights" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."chat_messages" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "session_id" "uuid",
    "role" "text",
    "content" "text" NOT NULL,
    "retrieved_chunks" "jsonb" DEFAULT '[]'::"jsonb",
    "created_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "chat_messages_role_check" CHECK (("role" = ANY (ARRAY['user'::"text", 'assistant'::"text"])))
);


ALTER TABLE "public"."chat_messages" OWNER TO "postgres";


COMMENT ON TABLE "public"."chat_messages" IS 'Individual chat messages with RAG context metadata.';



CREATE TABLE IF NOT EXISTS "public"."chat_sessions" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "title" "text",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."chat_sessions" OWNER TO "postgres";


COMMENT ON TABLE "public"."chat_sessions" IS 'Chat session grouping for the LUMI AI assistant.';



CREATE TABLE IF NOT EXISTS "public"."forecast_cache" (
    "forecast_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "model_id" "uuid" NOT NULL,
    "target_variable" "text" NOT NULL,
    "horizon_years" smallint NOT NULL,
    "forecast_year" smallint NOT NULL,
    "forecast_month" smallint,
    "predicted_value" numeric(14,4) NOT NULL,
    "lower_bound" numeric(14,4),
    "upper_bound" numeric(14,4),
    "created_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "forecast_cache_forecast_month_check" CHECK ((("forecast_month" IS NULL) OR (("forecast_month" >= 1) AND ("forecast_month" <= 12)))),
    CONSTRAINT "forecast_cache_horizon_years_check" CHECK ((("horizon_years" > 0) AND ("horizon_years" <= 10)))
);


ALTER TABLE "public"."forecast_cache" OWNER TO "postgres";


COMMENT ON TABLE "public"."forecast_cache" IS 'Cached forecast results per model, target, and horizon. TTL managed by application logic (e.g., 24h).';



CREATE TABLE IF NOT EXISTS "public"."geothermal_output" (
    "municipality_id" integer NOT NULL,
    "reservoir_temperature_c" double precision,
    "estimated_flow_rate_kg_s" double precision,
    "thermal_power_mw" double precision,
    "electric_power_mw" double precision,
    "annual_energy_gwh" double precision,
    "confidence_score" double precision,
    "source" "text",
    "assumption" "text"
);


ALTER TABLE "public"."geothermal_output" OWNER TO "postgres";


COMMENT ON TABLE "public"."geothermal_output" IS 'Pre-computed geothermal energy output per municipality using physics-based reservoir temperature and thermal power estimates.';



COMMENT ON COLUMN "public"."geothermal_output"."reservoir_temperature_c" IS 'Estimated reservoir temperature using Ts + (G × Depth) where Depth=2000m default.';



COMMENT ON COLUMN "public"."geothermal_output"."estimated_flow_rate_kg_s" IS 'Inferred flow rate from aquifer permeability when direct measurement is unavailable.';



COMMENT ON COLUMN "public"."geothermal_output"."thermal_power_mw" IS 'Q = m · Cp · ΔT in MW.';



COMMENT ON COLUMN "public"."geothermal_output"."electric_power_mw" IS 'P = Q × efficiency (binary 0.12 or flash 0.15).';



COMMENT ON COLUMN "public"."geothermal_output"."annual_energy_gwh" IS 'Annual electric energy estimate (GWh/year).';



COMMENT ON COLUMN "public"."geothermal_output"."confidence_score" IS 'Data availability confidence (0-1).';



COMMENT ON COLUMN "public"."geothermal_output"."source" IS 'Data provenance: IHFC, NASA POWER, PHIVOLCS, Smithsonian, Zenodo.';



COMMENT ON COLUMN "public"."geothermal_output"."assumption" IS 'Key assumptions for transparency, e.g., reservoir depth default.';



CREATE TABLE IF NOT EXISTS "public"."geothermal_suitability" (
    "municipality_id" integer NOT NULL,
    "heat_flow_score" double precision,
    "fault_density" double precision,
    "fault_distance_km" double precision,
    "volcano_distance_km" double precision,
    "aquifer_score" double precision,
    "temperature_score" double precision,
    "geothermal_score" double precision,
    "classification" "text"
);


ALTER TABLE "public"."geothermal_suitability" OWNER TO "postgres";


COMMENT ON TABLE "public"."geothermal_suitability" IS 'Pre-computed geothermal suitability metrics per municipality derived from IHFC heat flow, PHIVOLCS fault data, Smithsonian volcano data, and Zenodo aquifer properties.';



COMMENT ON COLUMN "public"."geothermal_suitability"."heat_flow_score" IS 'Normalized IHFC heat flow score (0-1), range 40-120 mW/m².';



COMMENT ON COLUMN "public"."geothermal_suitability"."fault_density" IS 'Fault length (km) / municipality area (km²).';



COMMENT ON COLUMN "public"."geothermal_suitability"."fault_distance_km" IS 'Haversine distance to nearest active fault (km).';



COMMENT ON COLUMN "public"."geothermal_suitability"."volcano_distance_km" IS 'Haversine distance to nearest volcano (km).';



COMMENT ON COLUMN "public"."geothermal_suitability"."aquifer_score" IS 'Composite aquifer suitability (0-1) from permeability, porosity, and thickness.';



COMMENT ON COLUMN "public"."geothermal_suitability"."temperature_score" IS 'Surface temperature anomaly score from NASA POWER (0-1).';



COMMENT ON COLUMN "public"."geothermal_suitability"."geothermal_score" IS 'Overall weighted geothermal suitability (0-1).';



COMMENT ON COLUMN "public"."geothermal_suitability"."classification" IS 'Categorical class: Low, Moderate, Good, High.';



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


CREATE TABLE IF NOT EXISTS "public"."ml_model_registry" (
    "model_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "model_name" "text" NOT NULL,
    "model_version" "text" NOT NULL,
    "model_type" "text" NOT NULL,
    "target_variable" "text" NOT NULL,
    "train_date" "date" NOT NULL,
    "metrics" "jsonb",
    "model_path" "text",
    "is_active" boolean DEFAULT false,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "ml_model_registry_model_type_check" CHECK (("model_type" = ANY (ARRAY['SARIMA'::"text", 'LightGBM'::"text", 'XGBoost'::"text", 'Prophet'::"text"])))
);


ALTER TABLE "public"."ml_model_registry" OWNER TO "postgres";


COMMENT ON TABLE "public"."ml_model_registry" IS 'Registry of trained forecasting models. Only one model per target_variable should be is_active=true at a time.';



CREATE TABLE IF NOT EXISTS "public"."municipalities" (
    "municipality_id" integer NOT NULL,
    "province_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision,
    "solar_suitability_score" numeric(5,2) DEFAULT NULL::numeric,
    "solar_classification" character varying(20) DEFAULT NULL::character varying,
    "solar_factors" "jsonb",
    "wind_suitability_score" numeric(5,2) DEFAULT NULL::numeric,
    "wind_classification" character varying(20) DEFAULT NULL::character varying,
    "wind_factors" "jsonb",
    "hydro_suitability_score" numeric(5,2) DEFAULT NULL::numeric,
    "hydro_classification" character varying(20) DEFAULT NULL::character varying,
    "hydro_factors" "jsonb",
    "geothermal_suitability_score" numeric(5,2) DEFAULT NULL::numeric,
    "geothermal_classification" character varying(20) DEFAULT NULL::character varying,
    "geothermal_factors" "jsonb",
    "geothermal_score_mcda" numeric(5,2) DEFAULT NULL::numeric,
    "composite_suitability_score" numeric(5,2) DEFAULT NULL::numeric,
    "composite_classification" character varying(20) DEFAULT NULL::character varying,
    "suitability_updated_at" timestamp with time zone
);


ALTER TABLE "public"."municipalities" OWNER TO "postgres";


COMMENT ON COLUMN "public"."municipalities"."solar_suitability_score" IS 'Solar suitability 0-100 based on irradiance and temperature';



COMMENT ON COLUMN "public"."municipalities"."wind_suitability_score" IS 'Wind suitability 0-100 based on wind speed';



COMMENT ON COLUMN "public"."municipalities"."hydro_suitability_score" IS 'Hydropower suitability 0-100 based on terrain and rainfall';



COMMENT ON COLUMN "public"."municipalities"."geothermal_suitability_score" IS 'Geothermal suitability 0-100 based on heat flow and fault proximity';



COMMENT ON COLUMN "public"."municipalities"."geothermal_score_mcda" IS 'AHP-based MCDA geothermal score 0-100 using IDW heat flow and distance-decay proximity';



COMMENT ON COLUMN "public"."municipalities"."composite_suitability_score" IS 'Average of available renewable suitability scores';



COMMENT ON COLUMN "public"."municipalities"."suitability_updated_at" IS 'Timestamp of last suitability recalculation';



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
    CONSTRAINT "municipality_climate_monthly_year_check" CHECK (("year" >= 2010))
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



CREATE TABLE IF NOT EXISTS "public"."national_energy_annual" (
    "year" smallint NOT NULL,
    "total_consumption_gwh" numeric(12,2),
    "residential_consumption_gwh" numeric(12,2),
    "commercial_consumption_gwh" numeric(12,2),
    "industrial_consumption_gwh" numeric(12,2),
    "others_consumption_gwh" numeric(12,2),
    "electricity_sales_gwh" numeric(12,2),
    "utilities_own_use_gwh" numeric(12,2),
    "system_losses_gwh" numeric(12,2),
    "luzon_peak_demand_mw" numeric(12,2),
    "visayas_peak_demand_mw" numeric(12,2),
    "mindanao_peak_demand_mw" numeric(12,2),
    "total_peak_demand_mw" numeric(12,2),
    "luzon_generation_gwh" numeric(12,2),
    "visayas_generation_gwh" numeric(12,2),
    "mindanao_generation_gwh" numeric(12,2),
    "coal_generation_gwh" numeric(12,2),
    "oil_based_generation_gwh" numeric(12,2),
    "natural_gas_generation_gwh" numeric(12,2),
    "renewable_generation_gwh" numeric(12,2),
    "geothermal_generation_gwh" numeric(12,2),
    "hydro_generation_gwh" numeric(12,2),
    "biomass_generation_gwh" numeric(12,2),
    "solar_generation_gwh" numeric(12,2),
    "wind_generation_gwh" numeric(12,2),
    "total_installed_capacity_mw" numeric(12,2),
    "total_dependable_capacity_mw" numeric(12,2),
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "non_negative_consumption" CHECK (("total_consumption_gwh" >= (0)::numeric)),
    CONSTRAINT "non_negative_peak_demand" CHECK (("total_peak_demand_mw" >= (0)::numeric)),
    CONSTRAINT "valid_year" CHECK ((("year" >= 2000) AND ("year" <= 2100)))
);


ALTER TABLE "public"."national_energy_annual" OWNER TO "postgres";


COMMENT ON TABLE "public"."national_energy_annual" IS 'Philippine national energy statistics (annual) extracted from DOE Power Statistics. Used as target variables for ML forecasting.';



COMMENT ON COLUMN "public"."national_energy_annual"."total_consumption_gwh" IS 'Total electricity consumption including system losses and utilities own use';



COMMENT ON COLUMN "public"."national_energy_annual"."total_peak_demand_mw" IS 'Total non-coincident peak demand across Luzon, Visayas, and Mindanao grids';



COMMENT ON COLUMN "public"."national_energy_annual"."renewable_generation_gwh" IS 'Combined RE generation: geothermal + hydro + biomass + solar + wind';



CREATE TABLE IF NOT EXISTS "public"."profiles" (
    "id" "uuid" NOT NULL,
    "full_name" "text",
    "avatar_url" "text",
    "organization" "text",
    "location" "text",
    "preferred_municipality_id" integer,
    "plan" "text" DEFAULT 'free'::"text",
    "is_active" boolean DEFAULT true,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."profiles" OWNER TO "postgres";


COMMENT ON TABLE "public"."profiles" IS 'Extended user profile for personalization and dashboard display.';



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


CREATE TABLE IF NOT EXISTS "public"."saved_locations" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "municipality_id" integer NOT NULL,
    "label" "text",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."saved_locations" OWNER TO "postgres";


COMMENT ON TABLE "public"."saved_locations" IS 'User bookmarked municipalities for quick access.';



CREATE TABLE IF NOT EXISTS "public"."saved_simulations" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "label" "text",
    "municipality_id" integer,
    "inputs" "jsonb" DEFAULT '{}'::"jsonb",
    "results" "jsonb" DEFAULT '{}'::"jsonb",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."saved_simulations" OWNER TO "postgres";


COMMENT ON TABLE "public"."saved_simulations" IS 'Persisted EcoSim simulation inputs and results per user.';



CREATE TABLE IF NOT EXISTS "public"."user_roles" (
    "user_id" "uuid" NOT NULL,
    "role" "public"."app_role" DEFAULT 'user'::"public"."app_role" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."user_roles" OWNER TO "postgres";


COMMENT ON TABLE "public"."user_roles" IS 'Role-based access control mapping for LUMI users.';



CREATE TABLE IF NOT EXISTS "public"."user_usage_limits" (
    "user_id" "uuid" NOT NULL,
    "chat_messages_this_month" integer DEFAULT 0,
    "simulations_this_month" integer DEFAULT 0,
    "plan" "text" DEFAULT 'free'::"text"
);


ALTER TABLE "public"."user_usage_limits" OWNER TO "postgres";


COMMENT ON TABLE "public"."user_usage_limits" IS 'Tracks monthly usage against free/premium plan limits.';



ALTER TABLE ONLY "public"."admin_audit_log"
    ADD CONSTRAINT "admin_audit_log_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."barangays"
    ADD CONSTRAINT "barangays_pkey" PRIMARY KEY ("barangay_id");



ALTER TABLE ONLY "public"."chart_ai_insights"
    ADD CONSTRAINT "chart_ai_insights_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."chat_messages"
    ADD CONSTRAINT "chat_messages_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."chat_sessions"
    ADD CONSTRAINT "chat_sessions_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."forecast_cache"
    ADD CONSTRAINT "forecast_cache_pkey" PRIMARY KEY ("forecast_id");



ALTER TABLE ONLY "public"."geothermal_output"
    ADD CONSTRAINT "geothermal_output_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."geothermal_suitability"
    ADD CONSTRAINT "geothermal_suitability_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."ml_model_registry"
    ADD CONSTRAINT "ml_model_registry_pkey" PRIMARY KEY ("model_id");



ALTER TABLE ONLY "public"."municipalities"
    ADD CONSTRAINT "municipalities_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."municipality_climate_monthly"
    ADD CONSTRAINT "municipality_climate_monthly_pkey" PRIMARY KEY ("municipality_id", "year", "month");



ALTER TABLE ONLY "public"."national_energy_annual"
    ADD CONSTRAINT "national_energy_annual_pkey" PRIMARY KEY ("year");



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."provinces"
    ADD CONSTRAINT "provinces_pkey" PRIMARY KEY ("province_id");



ALTER TABLE ONLY "public"."regions"
    ADD CONSTRAINT "regions_pkey" PRIMARY KEY ("region_id");



ALTER TABLE ONLY "public"."saved_locations"
    ADD CONSTRAINT "saved_locations_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."saved_locations"
    ADD CONSTRAINT "saved_locations_user_id_municipality_id_key" UNIQUE ("user_id", "municipality_id");



ALTER TABLE ONLY "public"."saved_simulations"
    ADD CONSTRAINT "saved_simulations_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_pkey" PRIMARY KEY ("user_id");



ALTER TABLE ONLY "public"."user_usage_limits"
    ADD CONSTRAINT "user_usage_limits_pkey" PRIMARY KEY ("user_id");



CREATE INDEX "idx_admin_audit_admin_id" ON "public"."admin_audit_log" USING "btree" ("admin_id");



CREATE INDEX "idx_admin_audit_created_at" ON "public"."admin_audit_log" USING "btree" ("created_at" DESC);



CREATE INDEX "idx_barangays_municipality_id" ON "public"."barangays" USING "btree" ("municipality_id");



CREATE INDEX "idx_chart_ai_type_hash" ON "public"."chart_ai_insights" USING "btree" ("chart_type", "chart_data_hash");



CREATE INDEX "idx_chat_messages_session_id" ON "public"."chat_messages" USING "btree" ("session_id");



CREATE INDEX "idx_chat_sessions_user_id" ON "public"."chat_sessions" USING "btree" ("user_id");



CREATE INDEX "idx_climate_monthly_municipality_id" ON "public"."municipality_climate_monthly" USING "btree" ("municipality_id");



CREATE INDEX "idx_climate_monthly_municipality_year_month" ON "public"."municipality_climate_monthly" USING "btree" ("municipality_id", "year", "month");



CREATE INDEX "idx_climate_monthly_year_month" ON "public"."municipality_climate_monthly" USING "btree" ("year", "month");



CREATE INDEX "idx_forecast_cache_created" ON "public"."forecast_cache" USING "btree" ("created_at" DESC);



CREATE INDEX "idx_forecast_cache_lookup" ON "public"."forecast_cache" USING "btree" ("target_variable", "forecast_year", "forecast_month");



CREATE INDEX "idx_forecast_cache_model" ON "public"."forecast_cache" USING "btree" ("model_id", "created_at" DESC);



CREATE INDEX "idx_geothermal_output_municipality_id" ON "public"."geothermal_output" USING "btree" ("municipality_id");



CREATE INDEX "idx_geothermal_suitability_municipality_id" ON "public"."geothermal_suitability" USING "btree" ("municipality_id");



CREATE INDEX "idx_hydropower_suitability_municipality_name" ON "public"."hydropower_suitability" USING "btree" ("municipality_name");



CREATE INDEX "idx_hydropower_suitability_province_id" ON "public"."hydropower_suitability" USING "btree" ("province_id");



CREATE UNIQUE INDEX "idx_ml_model_active_unique" ON "public"."ml_model_registry" USING "btree" ("target_variable", "is_active") WHERE ("is_active" = true);



CREATE INDEX "idx_ml_model_type_target" ON "public"."ml_model_registry" USING "btree" ("model_type", "target_variable", "train_date" DESC);



CREATE INDEX "idx_muni_composite_score" ON "public"."municipalities" USING "btree" ("composite_suitability_score") WHERE ("composite_suitability_score" IS NOT NULL);



CREATE INDEX "idx_muni_geo_score" ON "public"."municipalities" USING "btree" ("geothermal_suitability_score") WHERE ("geothermal_suitability_score" IS NOT NULL);



CREATE INDEX "idx_muni_hydro_score" ON "public"."municipalities" USING "btree" ("hydro_suitability_score") WHERE ("hydro_suitability_score" IS NOT NULL);



CREATE INDEX "idx_muni_solar_score" ON "public"."municipalities" USING "btree" ("solar_suitability_score") WHERE ("solar_suitability_score" IS NOT NULL);



CREATE INDEX "idx_muni_wind_score" ON "public"."municipalities" USING "btree" ("wind_suitability_score") WHERE ("wind_suitability_score" IS NOT NULL);



CREATE INDEX "idx_municipalities_province_id" ON "public"."municipalities" USING "btree" ("province_id");



CREATE INDEX "idx_national_energy_year" ON "public"."national_energy_annual" USING "btree" ("year");



CREATE INDEX "idx_provinces_region_id" ON "public"."provinces" USING "btree" ("region_id");



CREATE INDEX "idx_saved_locations_user_id" ON "public"."saved_locations" USING "btree" ("user_id");



CREATE INDEX "idx_saved_simulations_user_id" ON "public"."saved_simulations" USING "btree" ("user_id");



CREATE OR REPLACE TRIGGER "trg_ml_model_registry_updated" BEFORE UPDATE ON "public"."ml_model_registry" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



CREATE OR REPLACE TRIGGER "trg_national_energy_annual_updated" BEFORE UPDATE ON "public"."national_energy_annual" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



ALTER TABLE ONLY "public"."admin_audit_log"
    ADD CONSTRAINT "admin_audit_log_admin_id_fkey" FOREIGN KEY ("admin_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."admin_audit_log"
    ADD CONSTRAINT "admin_audit_log_target_user_id_fkey" FOREIGN KEY ("target_user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."barangays"
    ADD CONSTRAINT "barangays_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."chat_messages"
    ADD CONSTRAINT "chat_messages_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."chat_sessions"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."chat_sessions"
    ADD CONSTRAINT "chat_sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."forecast_cache"
    ADD CONSTRAINT "forecast_cache_model_id_fkey" FOREIGN KEY ("model_id") REFERENCES "public"."ml_model_registry"("model_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."geothermal_output"
    ADD CONSTRAINT "geothermal_output_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."geothermal_suitability"
    ADD CONSTRAINT "geothermal_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."municipalities"
    ADD CONSTRAINT "municipalities_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."municipality_climate_monthly"
    ADD CONSTRAINT "municipality_climate_monthly_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_id_fkey" FOREIGN KEY ("id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."provinces"
    ADD CONSTRAINT "provinces_region_id_fkey" FOREIGN KEY ("region_id") REFERENCES "public"."regions"("region_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."saved_locations"
    ADD CONSTRAINT "saved_locations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."saved_simulations"
    ADD CONSTRAINT "saved_simulations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_usage_limits"
    ADD CONSTRAINT "user_usage_limits_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



CREATE POLICY "Admins can view audit log" ON "public"."admin_audit_log" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM "public"."user_roles" "r"
  WHERE (("r"."user_id" = "auth"."uid"()) AND ("r"."role" = ANY (ARRAY['admin'::"public"."app_role", 'dev'::"public"."app_role"]))))));



CREATE POLICY "Allow authenticated read on forecast_cache" ON "public"."forecast_cache" FOR SELECT USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on forecast_cache" ON "public"."forecast_cache" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on ml_model_registry" ON "public"."ml_model_registry" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on national_energy_annual" ON "public"."national_energy_annual" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow public read on ml_model_registry" ON "public"."ml_model_registry" FOR SELECT USING (true);



CREATE POLICY "Allow public read on national_energy_annual" ON "public"."national_energy_annual" FOR SELECT USING (true);



CREATE POLICY "Users can CRUD own chat messages" ON "public"."chat_messages" USING ((EXISTS ( SELECT 1
   FROM "public"."chat_sessions" "s"
  WHERE (("s"."id" = "chat_messages"."session_id") AND ("s"."user_id" = "auth"."uid"())))));



CREATE POLICY "Users can CRUD own chat sessions" ON "public"."chat_sessions" USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users can CRUD own locations" ON "public"."saved_locations" USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users can CRUD own simulations" ON "public"."saved_simulations" USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users can update own profile" ON "public"."profiles" FOR UPDATE USING (("auth"."uid"() = "id"));



CREATE POLICY "Users can view own profile" ON "public"."profiles" FOR SELECT USING (("auth"."uid"() = "id"));



CREATE POLICY "Users can view own usage" ON "public"."user_usage_limits" FOR SELECT USING (("auth"."uid"() = "user_id"));



ALTER TABLE "public"."admin_audit_log" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."chat_messages" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."chat_sessions" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."forecast_cache" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."ml_model_registry" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."national_energy_annual" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."profiles" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."saved_locations" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."saved_simulations" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_usage_limits" ENABLE ROW LEVEL SECURITY;




ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";






















































































































































GRANT ALL ON FUNCTION "public"."get_suitability_classification"("score" numeric) TO "anon";
GRANT ALL ON FUNCTION "public"."get_suitability_classification"("score" numeric) TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_suitability_classification"("score" numeric) TO "service_role";



GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "anon";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "service_role";



GRANT ALL ON FUNCTION "public"."set_updated_at"() TO "anon";
GRANT ALL ON FUNCTION "public"."set_updated_at"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."set_updated_at"() TO "service_role";


















GRANT ALL ON TABLE "public"."admin_audit_log" TO "anon";
GRANT ALL ON TABLE "public"."admin_audit_log" TO "authenticated";
GRANT ALL ON TABLE "public"."admin_audit_log" TO "service_role";



GRANT ALL ON TABLE "public"."barangays" TO "anon";
GRANT ALL ON TABLE "public"."barangays" TO "authenticated";
GRANT ALL ON TABLE "public"."barangays" TO "service_role";



GRANT ALL ON TABLE "public"."chart_ai_insights" TO "anon";
GRANT ALL ON TABLE "public"."chart_ai_insights" TO "authenticated";
GRANT ALL ON TABLE "public"."chart_ai_insights" TO "service_role";



GRANT ALL ON TABLE "public"."chat_messages" TO "anon";
GRANT ALL ON TABLE "public"."chat_messages" TO "authenticated";
GRANT ALL ON TABLE "public"."chat_messages" TO "service_role";



GRANT ALL ON TABLE "public"."chat_sessions" TO "anon";
GRANT ALL ON TABLE "public"."chat_sessions" TO "authenticated";
GRANT ALL ON TABLE "public"."chat_sessions" TO "service_role";



GRANT ALL ON TABLE "public"."forecast_cache" TO "anon";
GRANT ALL ON TABLE "public"."forecast_cache" TO "authenticated";
GRANT ALL ON TABLE "public"."forecast_cache" TO "service_role";



GRANT ALL ON TABLE "public"."geothermal_output" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_output" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_output" TO "service_role";



GRANT ALL ON TABLE "public"."geothermal_suitability" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_suitability" TO "service_role";



GRANT ALL ON TABLE "public"."hydropower_suitability" TO "anon";
GRANT ALL ON TABLE "public"."hydropower_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."hydropower_suitability" TO "service_role";



GRANT ALL ON TABLE "public"."ml_model_registry" TO "anon";
GRANT ALL ON TABLE "public"."ml_model_registry" TO "authenticated";
GRANT ALL ON TABLE "public"."ml_model_registry" TO "service_role";



GRANT ALL ON TABLE "public"."municipalities" TO "anon";
GRANT ALL ON TABLE "public"."municipalities" TO "authenticated";
GRANT ALL ON TABLE "public"."municipalities" TO "service_role";



GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "anon";
GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "authenticated";
GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "service_role";



GRANT ALL ON TABLE "public"."national_energy_annual" TO "anon";
GRANT ALL ON TABLE "public"."national_energy_annual" TO "authenticated";
GRANT ALL ON TABLE "public"."national_energy_annual" TO "service_role";



GRANT ALL ON TABLE "public"."profiles" TO "anon";
GRANT ALL ON TABLE "public"."profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."profiles" TO "service_role";



GRANT ALL ON TABLE "public"."provinces" TO "anon";
GRANT ALL ON TABLE "public"."provinces" TO "authenticated";
GRANT ALL ON TABLE "public"."provinces" TO "service_role";



GRANT ALL ON TABLE "public"."regions" TO "anon";
GRANT ALL ON TABLE "public"."regions" TO "authenticated";
GRANT ALL ON TABLE "public"."regions" TO "service_role";



GRANT ALL ON TABLE "public"."regional_lookup" TO "anon";
GRANT ALL ON TABLE "public"."regional_lookup" TO "authenticated";
GRANT ALL ON TABLE "public"."regional_lookup" TO "service_role";



GRANT ALL ON TABLE "public"."saved_locations" TO "anon";
GRANT ALL ON TABLE "public"."saved_locations" TO "authenticated";
GRANT ALL ON TABLE "public"."saved_locations" TO "service_role";



GRANT ALL ON TABLE "public"."saved_simulations" TO "anon";
GRANT ALL ON TABLE "public"."saved_simulations" TO "authenticated";
GRANT ALL ON TABLE "public"."saved_simulations" TO "service_role";



GRANT ALL ON TABLE "public"."user_roles" TO "anon";
GRANT ALL ON TABLE "public"."user_roles" TO "authenticated";
GRANT ALL ON TABLE "public"."user_roles" TO "service_role";



GRANT ALL ON TABLE "public"."user_usage_limits" TO "anon";
GRANT ALL ON TABLE "public"."user_usage_limits" TO "authenticated";
GRANT ALL ON TABLE "public"."user_usage_limits" TO "service_role";









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






























