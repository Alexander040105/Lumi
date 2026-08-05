


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






CREATE EXTENSION IF NOT EXISTS "vector" WITH SCHEMA "extensions";






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
begin
  insert into public.profiles (id, full_name, plan, is_active, created_at)
  values (new.id, new.raw_user_meta_data->>'full_name', 'free', true, now())
  on conflict (id) do nothing;

  insert into public.user_roles (user_id, role, created_at)
  values (new.id, 'user', now())
  on conflict (user_id) do nothing;

  return new;
end;
$$;


ALTER FUNCTION "public"."handle_new_user"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."is_admin"() RETURNS boolean
    LANGUAGE "sql" SECURITY DEFINER
    SET "search_path" TO 'public'
    AS $$
  select exists (
    select 1 from public.user_roles
    where user_id = auth.uid() and role in ('admin', 'dev')
  );
$$;


ALTER FUNCTION "public"."is_admin"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."match_rag_chunks"("query_embedding" "extensions"."vector", "match_count" integer DEFAULT 20, "similarity_threshold" double precision DEFAULT 0.25, "filter_renewable_type" "text" DEFAULT NULL::"text", "filter_category" "text" DEFAULT NULL::"text") RETURNS TABLE("id" bigint, "chunk_text" "text", "renewable_type" "text", "category" "text", "product_type" "text", "sources" "jsonb", "similarity" double precision)
    LANGUAGE "sql" SECURITY DEFINER
    SET "search_path" TO 'public', 'extensions'
    AS $$
    SELECT
        id,
        chunk_text,
        renewable_type,
        category,
        product_type,
        sources,
        (1.0 - (embedding <=> query_embedding))::FLOAT AS similarity
    FROM public.rag_chunks
    WHERE
        (filter_renewable_type IS NULL OR renewable_type = filter_renewable_type)
        AND (filter_category IS NULL OR category = filter_category)
        AND (1.0 - (embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;


ALTER FUNCTION "public"."match_rag_chunks"("query_embedding" "extensions"."vector", "match_count" integer, "similarity_threshold" double precision, "filter_renewable_type" "text", "filter_category" "text") OWNER TO "postgres";


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


COMMENT ON TABLE "public"."admin_audit_log" IS 'Immutable log of admin actions for accountability.';



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
    "source" "text" DEFAULT 'NASA POWER'::"text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "cloud_amt" double precision,
    "surface_pressure" double precision,
    "elevation" double precision,
    "rhoa" double precision,
    CONSTRAINT "barangay_climate_monthly_month_check" CHECK ((("month" >= 1) AND ("month" <= 12))),
    CONSTRAINT "barangay_climate_monthly_year_check" CHECK (("year" >= 2010))
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



CREATE TABLE IF NOT EXISTS "public"."barangays" (
    "barangay_id" integer NOT NULL,
    "municipality_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision,
    "psgc_code" "text",
    "area_km2" double precision,
    "island_group" "text",
    "urban_rural" "text",
    "population_2015" bigint,
    "population_2020" bigint,
    "population_2024" bigint,
    "geographic_level" "text",
    "old_name" "text",
    "status" "text"
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



CREATE TABLE IF NOT EXISTS "public"."composite_suitability" (
    "municipality_id" integer NOT NULL,
    "score" numeric(5,2),
    "classification" character varying(20),
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."composite_suitability" OWNER TO "postgres";


COMMENT ON TABLE "public"."composite_suitability" IS 'Composite renewable energy suitability score per municipality. Average of available renewable suitability scores.';



CREATE TABLE IF NOT EXISTS "public"."doe_datasets" (
    "dataset_name" "text" NOT NULL,
    "row_count" integer DEFAULT 0 NOT NULL,
    "data" "jsonb" DEFAULT '[]'::"jsonb" NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."doe_datasets" OWNER TO "postgres";


COMMENT ON TABLE "public"."doe_datasets" IS 'Stores DOE CSV files as JSONB arrays.  The backend loads a dataset by name and converts it to a DataFrame.';



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
    "geo_level" "text" DEFAULT 'national'::"text",
    "geo_id" integer,
    CONSTRAINT "forecast_cache_forecast_month_check" CHECK ((("forecast_month" IS NULL) OR (("forecast_month" >= 1) AND ("forecast_month" <= 12)))),
    CONSTRAINT "forecast_cache_geo_level_check" CHECK (("geo_level" = ANY (ARRAY['national'::"text", 'province'::"text", 'municipality'::"text", 'barangay'::"text"]))),
    CONSTRAINT "forecast_cache_horizon_years_check" CHECK ((("horizon_years" > 0) AND ("horizon_years" <= 10)))
);


ALTER TABLE "public"."forecast_cache" OWNER TO "postgres";


COMMENT ON TABLE "public"."forecast_cache" IS 'Cached forecast results per model, target, and horizon. TTL managed by application logic (e.g., 24h).';



COMMENT ON COLUMN "public"."forecast_cache"."geo_level" IS 'Geographic level: national (default), province, municipality, or barangay.';



COMMENT ON COLUMN "public"."forecast_cache"."geo_id" IS 'Geographic ID — province_id, municipality_id, or barangay_id. NULL for national.';



CREATE TABLE IF NOT EXISTS "public"."forecast_model_runs" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "model_id" "uuid",
    "run_type" "text" DEFAULT 'train'::"text" NOT NULL,
    "target_variable" "text" NOT NULL,
    "hyperparameters" "jsonb",
    "metrics" "jsonb",
    "artifact_path" "text",
    "started_at" timestamp with time zone NOT NULL,
    "finished_at" timestamp with time zone,
    "status" "text" DEFAULT 'running'::"text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    CONSTRAINT "forecast_model_runs_run_type_check" CHECK (("run_type" = ANY (ARRAY['train'::"text", 'backtest'::"text", 'retrain'::"text", 'evaluate'::"text"]))),
    CONSTRAINT "forecast_model_runs_status_check" CHECK (("status" = ANY (ARRAY['running'::"text", 'success'::"text", 'failed'::"text", 'cancelled'::"text"])))
);


ALTER TABLE "public"."forecast_model_runs" OWNER TO "postgres";


COMMENT ON TABLE "public"."forecast_model_runs" IS 'Log of forecasting model training and backtest runs.';



CREATE TABLE IF NOT EXISTS "public"."geospatial_metadata" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "region_id" integer,
    "province_id" integer,
    "municipality_id" integer,
    "barangay_id" integer,
    "centroid_lat" double precision,
    "centroid_lon" double precision,
    "area_km2" double precision,
    "elevation_m" double precision,
    "crs" "text" DEFAULT 'EPSG:4326'::"text" NOT NULL,
    "source" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    CONSTRAINT "geospatial_metadata_exactly_one_geo" CHECK (((((
CASE
    WHEN ("region_id" IS NOT NULL) THEN 1
    ELSE 0
END +
CASE
    WHEN ("province_id" IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN ("municipality_id" IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN ("barangay_id" IS NOT NULL) THEN 1
    ELSE 0
END) = 1))
);


ALTER TABLE "public"."geospatial_metadata" OWNER TO "postgres";


COMMENT ON TABLE "public"."geospatial_metadata" IS 'Geospatial metadata (centroid, area, elevation) for each administrative level. Exactly one geo FK must be set.';



COMMENT ON COLUMN "public"."geospatial_metadata"."centroid_lat" IS 'Latitude of the centroid — used for NASA POWER API, OpenWeather API, map centering.';



COMMENT ON COLUMN "public"."geospatial_metadata"."centroid_lon" IS 'Longitude of the centroid — used for NASA POWER API, OpenWeather API, map centering.';



COMMENT ON COLUMN "public"."geospatial_metadata"."area_km2" IS 'Land area in km² — used for density calculations and area-weighted interpolation.';



COMMENT ON COLUMN "public"."geospatial_metadata"."elevation_m" IS 'Mean elevation in meters — affects solar efficiency, hydropower head, wind extrapolation.';



COMMENT ON COLUMN "public"."geospatial_metadata"."crs" IS 'Coordinate Reference System identifier. Default EPSG:4326 (WGS84).';



COMMENT ON COLUMN "public"."geospatial_metadata"."source" IS 'Data provenance: PSA, PhilAtlas, GeoJSON centroid, etc.';



CREATE TABLE IF NOT EXISTS "public"."geothermal_faults" (
    "id" bigint NOT NULL,
    "name" "text",
    "lat" double precision,
    "lon" double precision,
    "length_km" double precision,
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."geothermal_faults" OWNER TO "postgres";


COMMENT ON TABLE "public"."geothermal_faults" IS 'PHIVOLCS active fault markers used for geothermal distance/density scoring.';



ALTER TABLE "public"."geothermal_faults" ALTER COLUMN "id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."geothermal_faults_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."geothermal_heatflow" (
    "id" bigint NOT NULL,
    "lat" double precision,
    "lon" double precision,
    "heat_flow_mw_m2" double precision,
    "elevation" double precision,
    "environment" "text",
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."geothermal_heatflow" OWNER TO "postgres";


COMMENT ON TABLE "public"."geothermal_heatflow" IS 'IHFC heat flow measurements used for geothermal suitability scoring.';



ALTER TABLE "public"."geothermal_heatflow" ALTER COLUMN "id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."geothermal_heatflow_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



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
    "classification" "text",
    "geothermal_score_mcda" double precision,
    "aquifer_porosity" double precision,
    "aquifer_permeability_log10" double precision,
    "aquifer_thickness_m" double precision,
    "aquifer_depth_m" double precision,
    "aquifer_basin_name" "text",
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "aquifer_fallback" boolean,
    "aquifer_distance_km" double precision
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



COMMENT ON COLUMN "public"."geothermal_suitability"."geothermal_score_mcda" IS 'AHP-based MCDA geothermal suitability score (0-1) using distance-decay fault/volcano proximity.';



CREATE TABLE IF NOT EXISTS "public"."geothermal_volcanoes" (
    "id" bigint NOT NULL,
    "name" "text",
    "lat" double precision,
    "lon" double precision,
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."geothermal_volcanoes" OWNER TO "postgres";


COMMENT ON TABLE "public"."geothermal_volcanoes" IS 'Smithsonian volcano dataset used for geothermal proximity scoring.';



ALTER TABLE "public"."geothermal_volcanoes" ALTER COLUMN "id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."geothermal_volcanoes_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."hydro_suitability" (
    "municipality_id" integer NOT NULL,
    "score" numeric(5,2),
    "classification" character varying(20),
    "factors" "jsonb",
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
    "slope_classification" "text",
    "elevation_classification" "text",
    "ridge_elevation" double precision,
    "terrain_exposure_index" double precision,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."hydro_suitability" OWNER TO "postgres";


COMMENT ON TABLE "public"."hydro_suitability" IS 'Hydropower suitability and terrain metrics per municipality. Normalized version — no duplicated admin columns.';



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


CREATE TABLE IF NOT EXISTS "public"."mcda_weights" (
    "id" integer NOT NULL,
    "energy_type" "text" NOT NULL,
    "criterion" "text" NOT NULL,
    "weight" double precision NOT NULL,
    "version" integer DEFAULT 1 NOT NULL,
    "is_active" boolean DEFAULT true NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."mcda_weights" OWNER TO "postgres";


COMMENT ON TABLE "public"."mcda_weights" IS 'AHP-derived MCDA criterion weights for renewable energy suitability scoring. Manage via admin panel or SQL.';



CREATE SEQUENCE IF NOT EXISTS "public"."mcda_weights_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."mcda_weights_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."mcda_weights_id_seq" OWNED BY "public"."mcda_weights"."id";



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



CREATE TABLE IF NOT EXISTS "public"."municipal_population" (
    "municipality_id" integer NOT NULL,
    "province_id" integer NOT NULL,
    "population_2015" bigint,
    "population_2020" bigint,
    "population_2024" bigint
);


ALTER TABLE "public"."municipal_population" OWNER TO "postgres";


COMMENT ON TABLE "public"."municipal_population" IS 'PSA population data per municipality. Used for population-weighted demand estimation in EnergyHub.';



COMMENT ON COLUMN "public"."municipal_population"."population_2015" IS 'PSA 2015 Census of Population.';



COMMENT ON COLUMN "public"."municipal_population"."population_2020" IS 'PSA 2020 Census of Population.';



COMMENT ON COLUMN "public"."municipal_population"."population_2024" IS 'PSA 2024 updated population estimates.';



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
    "composite_suitability_score" numeric(5,2) DEFAULT NULL::numeric,
    "composite_classification" character varying(20) DEFAULT NULL::character varying,
    "suitability_updated_at" timestamp with time zone,
    "geothermal_score_mcda" numeric(5,2) DEFAULT NULL::numeric,
    "psgc_code" "text",
    "area_km2" double precision,
    "island_group" "text",
    "income_classification" "text",
    "city_class" "text",
    "is_city" boolean DEFAULT false,
    "population_2015" bigint,
    "population_2020" bigint,
    "population_2024" bigint,
    "geographic_level" "text",
    "old_name" "text"
);


ALTER TABLE "public"."municipalities" OWNER TO "postgres";


COMMENT ON COLUMN "public"."municipalities"."solar_suitability_score" IS 'Solar suitability 0-100 based on irradiance and temperature';



COMMENT ON COLUMN "public"."municipalities"."wind_suitability_score" IS 'Wind suitability 0-100 based on wind speed';



COMMENT ON COLUMN "public"."municipalities"."hydro_suitability_score" IS 'Hydropower suitability 0-100 based on terrain and rainfall';



COMMENT ON COLUMN "public"."municipalities"."geothermal_suitability_score" IS 'Geothermal suitability 0-100 based on heat flow and fault proximity';



COMMENT ON COLUMN "public"."municipalities"."composite_suitability_score" IS 'Average of available renewable suitability scores';



COMMENT ON COLUMN "public"."municipalities"."suitability_updated_at" IS 'Timestamp of last suitability recalculation';



COMMENT ON COLUMN "public"."municipalities"."geothermal_score_mcda" IS 'AHP-based MCDA geothermal score 0-100 using IDW heat flow and distance-decay proximity';



CREATE TABLE IF NOT EXISTS "public"."municipality_climate_averages" (
    "municipality_id" integer NOT NULL,
    "avg_t2m" double precision,
    "avg_t2m_max" double precision,
    "avg_t2m_min" double precision,
    "avg_rh2m" double precision,
    "avg_rhoa" double precision,
    "avg_prectotcorr" double precision,
    "avg_ws10m" double precision,
    "avg_allsky_sfc_sw_dwn" double precision,
    "avg_cloud_amt" double precision,
    "avg_surface_pressure" double precision,
    "elevation" integer,
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."municipality_climate_averages" OWNER TO "postgres";


COMMENT ON TABLE "public"."municipality_climate_averages" IS 'Pre-computed NASA POWER climate averages per municipality (used by EcoSim).';



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



CREATE TABLE IF NOT EXISTS "public"."population_data" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "psgc_code" "text" NOT NULL,
    "geographic_level" "text" NOT NULL,
    "year" integer NOT NULL,
    "population" bigint
);


ALTER TABLE "public"."population_data" OWNER TO "postgres";


COMMENT ON TABLE "public"."population_data" IS 'Historical population records from PSA for all geographic levels. Supports time-series analysis.';



CREATE TABLE IF NOT EXISTS "public"."products" (
    "id" bigint NOT NULL,
    "product_name" "text",
    "product_name_raw" "text",
    "product_name_normalized" "text",
    "price_raw" "text",
    "price_value" numeric(14,4),
    "currency" "text",
    "energy_category" "text",
    "energy_subcategory" "text",
    "source_site" "text",
    "source_file" "text",
    "url" "text",
    "ratings" "text",
    "reviews" "text",
    "price_note" "text",
    "rejection_reason" "text",
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."products" OWNER TO "postgres";


COMMENT ON TABLE "public"."products" IS 'Cleaned renewable energy product catalogue used by the product recommendation service.';



ALTER TABLE "public"."products" ALTER COLUMN "id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."products_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



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


COMMENT ON TABLE "public"."profiles" IS 'Extended user profile linked to Supabase Auth.';



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
    "source" "text" DEFAULT 'NASA POWER'::"text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "cloud_amt" double precision,
    "surface_pressure" double precision,
    "elevation" double precision,
    "rhoa" double precision,
    CONSTRAINT "province_climate_monthly_month_check" CHECK ((("month" >= 1) AND ("month" <= 12))),
    CONSTRAINT "province_climate_monthly_year_check" CHECK (("year" >= 2010))
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



CREATE OR REPLACE VIEW "public"."province_climate_annual" AS
 SELECT "province_id",
    "year",
    "avg"("t2m") AS "avg_t2m",
    "avg"("t2m_max") AS "avg_t2m_max",
    "avg"("t2m_min") AS "avg_t2m_min",
    "avg"("rh2m") AS "avg_rh2m",
    "avg"("prectotcorr") AS "avg_prectotcorr",
    "avg"("ws10m") AS "avg_ws10m",
    "avg"("allsky_sfc_sw_dwn") AS "avg_allsky_sfc_sw_dwn",
    "avg"("cloud_amt") AS "avg_cloud_amt",
    "avg"("surface_pressure") AS "avg_surface_pressure",
    "avg"("elevation") AS "avg_elevation",
    "avg"("rhoa") AS "avg_rhoa"
   FROM "public"."province_climate_monthly"
  GROUP BY "province_id", "year"
  ORDER BY "province_id", "year";


ALTER VIEW "public"."province_climate_annual" OWNER TO "postgres";


COMMENT ON VIEW "public"."province_climate_annual" IS 'Annual climate averages per province, aggregated from monthly data.';



CREATE TABLE IF NOT EXISTS "public"."provinces" (
    "province_id" integer NOT NULL,
    "region_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision,
    "psgc_code" "text",
    "area_km2" double precision,
    "island_group" "text",
    "income_classification" "text",
    "population_2015" bigint,
    "population_2020" bigint,
    "population_2024" bigint,
    "geographic_level" "text",
    "old_name" "text",
    "geojson_name" "text"
);


ALTER TABLE "public"."provinces" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."rag_chunks" (
    "id" bigint NOT NULL,
    "chunk_text" "text" NOT NULL,
    "renewable_type" "text",
    "category" "text",
    "product_type" "text",
    "sources" "jsonb",
    "embedding" "extensions"."vector"(384),
    "search_vector" "tsvector" GENERATED ALWAYS AS ("to_tsvector"('"english"'::"regconfig", COALESCE("chunk_text", ''::"text"))) STORED,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."rag_chunks" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."rag_chunks_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."rag_chunks_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."rag_chunks_id_seq" OWNED BY "public"."rag_chunks"."id";



CREATE TABLE IF NOT EXISTS "public"."regions" (
    "region_id" integer NOT NULL,
    "name" "text" NOT NULL,
    "lat" double precision,
    "lon" double precision,
    "psgc_code" "text",
    "area_km2" double precision,
    "island_group" "text",
    "population_2015" bigint,
    "population_2020" bigint,
    "population_2024" bigint,
    "geographic_level" "text"
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


CREATE OR REPLACE VIEW "public"."regional_lookup_v2" AS
 SELECT "r"."region_id",
    "r"."name" AS "region_name",
    "p"."province_id",
    "p"."name" AS "province_name",
    "m"."municipality_id",
    "m"."name" AS "municipality_name",
    "b"."barangay_id",
    "b"."name" AS "barangay_name",
    "rg"."centroid_lat" AS "region_lat",
    "rg"."centroid_lon" AS "region_lon",
    "rg"."area_km2" AS "region_area_km2",
    "rg"."elevation_m" AS "region_elevation_m",
    "pg"."centroid_lat" AS "province_lat",
    "pg"."centroid_lon" AS "province_lon",
    "pg"."area_km2" AS "province_area_km2",
    "pg"."elevation_m" AS "province_elevation_m",
    "mg"."centroid_lat" AS "municipality_lat",
    "mg"."centroid_lon" AS "municipality_lon",
    "mg"."area_km2" AS "municipality_area_km2",
    "mg"."elevation_m" AS "municipality_elevation_m",
    "bg"."centroid_lat" AS "barangay_lat",
    "bg"."centroid_lon" AS "barangay_lon",
    "bg"."area_km2" AS "barangay_area_km2",
    "bg"."elevation_m" AS "barangay_elevation_m"
   FROM ((((((("public"."regions" "r"
     LEFT JOIN "public"."geospatial_metadata" "rg" ON (("rg"."region_id" = "r"."region_id")))
     JOIN "public"."provinces" "p" ON (("p"."region_id" = "r"."region_id")))
     LEFT JOIN "public"."geospatial_metadata" "pg" ON (("pg"."province_id" = "p"."province_id")))
     JOIN "public"."municipalities" "m" ON (("m"."province_id" = "p"."province_id")))
     LEFT JOIN "public"."geospatial_metadata" "mg" ON (("mg"."municipality_id" = "m"."municipality_id")))
     JOIN "public"."barangays" "b" ON (("b"."municipality_id" = "m"."municipality_id")))
     LEFT JOIN "public"."geospatial_metadata" "bg" ON (("bg"."barangay_id" = "b"."barangay_id")));


ALTER VIEW "public"."regional_lookup_v2" OWNER TO "postgres";


COMMENT ON VIEW "public"."regional_lookup_v2" IS 'Full geographic hierarchy with geospatial metadata. Extends regional_lookup with area and elevation.';



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



CREATE TABLE IF NOT EXISTS "public"."solar_suitability" (
    "municipality_id" integer NOT NULL,
    "score" numeric(5,2),
    "classification" character varying(20),
    "factors" "jsonb",
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."solar_suitability" OWNER TO "postgres";


COMMENT ON TABLE "public"."solar_suitability" IS 'Solar energy suitability scores per municipality. Extracted from municipalities table for normalization.';



CREATE TABLE IF NOT EXISTS "public"."system_config" (
    "key" "text" NOT NULL,
    "value" "jsonb" DEFAULT '{}'::"jsonb" NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."system_config" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_roles" (
    "user_id" "uuid" NOT NULL,
    "role" "public"."app_role" DEFAULT 'user'::"public"."app_role" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."user_roles" OWNER TO "postgres";


COMMENT ON TABLE "public"."user_roles" IS 'Role-based access control (user/admin/dev).';



CREATE TABLE IF NOT EXISTS "public"."user_usage_limits" (
    "user_id" "uuid" NOT NULL,
    "chat_messages_this_month" integer DEFAULT 0,
    "simulations_this_month" integer DEFAULT 0,
    "plan" "text" DEFAULT 'free'::"text"
);


ALTER TABLE "public"."user_usage_limits" OWNER TO "postgres";


COMMENT ON TABLE "public"."user_usage_limits" IS 'Tracks monthly usage against free/premium plan limits.';



CREATE TABLE IF NOT EXISTS "public"."wind_products" (
    "id" bigint NOT NULL,
    "source_file" "text",
    "source_site" "text",
    "name" "text",
    "price" "text",
    "ratings" "text",
    "reviews" "text",
    "url" "text",
    "power_w" numeric(14,4),
    "diameter_m" numeric(14,4),
    "rotor_radius_m" numeric(14,4),
    "wind_speed_mps" numeric(14,4),
    "power_coefficient" numeric(14,4),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."wind_products" OWNER TO "postgres";


COMMENT ON TABLE "public"."wind_products" IS 'Parsed wind turbine product data used to compute average rotor radius and power coefficient.';



ALTER TABLE "public"."wind_products" ALTER COLUMN "id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."wind_products_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."wind_products_summary" (
    "variant" "text" NOT NULL,
    "avg_rotor_radius_m" double precision,
    "avg_power_coefficient" double precision,
    "rotor_count" integer,
    "cp_count" integer,
    "summary_rotor" "text",
    "summary_cp" "text",
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."wind_products_summary" OWNER TO "postgres";


COMMENT ON TABLE "public"."wind_products_summary" IS 'Pre-computed summary statistics from wind_products used by wind_output_calc.py.';



CREATE TABLE IF NOT EXISTS "public"."wind_suitability" (
    "municipality_id" integer NOT NULL,
    "score" numeric(5,2),
    "classification" character varying(20),
    "factors" "jsonb",
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."wind_suitability" OWNER TO "postgres";


COMMENT ON TABLE "public"."wind_suitability" IS 'Wind energy suitability scores per municipality. Extracted from municipalities table for normalization.';



ALTER TABLE ONLY "public"."mcda_weights" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."mcda_weights_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."rag_chunks" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."rag_chunks_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."admin_audit_log"
    ADD CONSTRAINT "admin_audit_log_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."barangay_climate_monthly"
    ADD CONSTRAINT "barangay_climate_monthly_pkey" PRIMARY KEY ("barangay_id", "year", "month");



ALTER TABLE ONLY "public"."barangays"
    ADD CONSTRAINT "barangays_pkey" PRIMARY KEY ("barangay_id");



ALTER TABLE ONLY "public"."chart_ai_insights"
    ADD CONSTRAINT "chart_ai_insights_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."chat_messages"
    ADD CONSTRAINT "chat_messages_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."chat_sessions"
    ADD CONSTRAINT "chat_sessions_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."composite_suitability"
    ADD CONSTRAINT "composite_suitability_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."doe_datasets"
    ADD CONSTRAINT "doe_datasets_pkey" PRIMARY KEY ("dataset_name");



ALTER TABLE ONLY "public"."forecast_cache"
    ADD CONSTRAINT "forecast_cache_pkey" PRIMARY KEY ("forecast_id");



ALTER TABLE ONLY "public"."forecast_model_runs"
    ADD CONSTRAINT "forecast_model_runs_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."geospatial_metadata"
    ADD CONSTRAINT "geospatial_metadata_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."geothermal_faults"
    ADD CONSTRAINT "geothermal_faults_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."geothermal_heatflow"
    ADD CONSTRAINT "geothermal_heatflow_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."geothermal_output"
    ADD CONSTRAINT "geothermal_output_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."geothermal_suitability"
    ADD CONSTRAINT "geothermal_suitability_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."geothermal_volcanoes"
    ADD CONSTRAINT "geothermal_volcanoes_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."hydro_suitability"
    ADD CONSTRAINT "hydro_suitability_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."mcda_weights"
    ADD CONSTRAINT "mcda_weights_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."ml_model_registry"
    ADD CONSTRAINT "ml_model_registry_pkey" PRIMARY KEY ("model_id");



ALTER TABLE ONLY "public"."municipal_population"
    ADD CONSTRAINT "municipal_population_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."municipalities"
    ADD CONSTRAINT "municipalities_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."municipality_climate_averages"
    ADD CONSTRAINT "municipality_climate_averages_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."municipality_climate_monthly"
    ADD CONSTRAINT "municipality_climate_monthly_pkey" PRIMARY KEY ("municipality_id", "year", "month");



ALTER TABLE ONLY "public"."national_energy_annual"
    ADD CONSTRAINT "national_energy_annual_pkey" PRIMARY KEY ("year");



ALTER TABLE ONLY "public"."population_data"
    ADD CONSTRAINT "population_data_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."population_data"
    ADD CONSTRAINT "population_data_psgc_code_year_key" UNIQUE ("psgc_code", "year");



ALTER TABLE ONLY "public"."products"
    ADD CONSTRAINT "products_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."province_climate_monthly"
    ADD CONSTRAINT "province_climate_monthly_pkey" PRIMARY KEY ("province_id", "year", "month");



ALTER TABLE ONLY "public"."provinces"
    ADD CONSTRAINT "provinces_pkey" PRIMARY KEY ("province_id");



ALTER TABLE ONLY "public"."rag_chunks"
    ADD CONSTRAINT "rag_chunks_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."regions"
    ADD CONSTRAINT "regions_pkey" PRIMARY KEY ("region_id");



ALTER TABLE ONLY "public"."saved_locations"
    ADD CONSTRAINT "saved_locations_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."saved_locations"
    ADD CONSTRAINT "saved_locations_user_id_municipality_id_key" UNIQUE ("user_id", "municipality_id");



ALTER TABLE ONLY "public"."saved_simulations"
    ADD CONSTRAINT "saved_simulations_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."solar_suitability"
    ADD CONSTRAINT "solar_suitability_pkey" PRIMARY KEY ("municipality_id");



ALTER TABLE ONLY "public"."system_config"
    ADD CONSTRAINT "system_config_pkey" PRIMARY KEY ("key");



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_pkey" PRIMARY KEY ("user_id");



ALTER TABLE ONLY "public"."user_usage_limits"
    ADD CONSTRAINT "user_usage_limits_pkey" PRIMARY KEY ("user_id");



ALTER TABLE ONLY "public"."wind_products"
    ADD CONSTRAINT "wind_products_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."wind_products_summary"
    ADD CONSTRAINT "wind_products_summary_pkey" PRIMARY KEY ("variant");



ALTER TABLE ONLY "public"."wind_suitability"
    ADD CONSTRAINT "wind_suitability_pkey" PRIMARY KEY ("municipality_id");



CREATE INDEX "idx_admin_audit_admin_id" ON "public"."admin_audit_log" USING "btree" ("admin_id");



CREATE INDEX "idx_admin_audit_created_at" ON "public"."admin_audit_log" USING "btree" ("created_at" DESC);



CREATE INDEX "idx_barangay_climate_monthly_barangay_id" ON "public"."barangay_climate_monthly" USING "btree" ("barangay_id");



CREATE INDEX "idx_barangay_climate_monthly_barangay_year_month" ON "public"."barangay_climate_monthly" USING "btree" ("barangay_id", "year", "month");



CREATE INDEX "idx_barangay_climate_monthly_year_month" ON "public"."barangay_climate_monthly" USING "btree" ("year", "month");



CREATE INDEX "idx_barangays_municipality_id" ON "public"."barangays" USING "btree" ("municipality_id");



CREATE INDEX "idx_barangays_psgc_code" ON "public"."barangays" USING "btree" ("psgc_code") WHERE ("psgc_code" IS NOT NULL);



CREATE INDEX "idx_chart_ai_type_hash" ON "public"."chart_ai_insights" USING "btree" ("chart_type", "chart_data_hash");



CREATE INDEX "idx_chat_messages_session_id" ON "public"."chat_messages" USING "btree" ("session_id");



CREATE INDEX "idx_chat_sessions_user_id" ON "public"."chat_sessions" USING "btree" ("user_id");



CREATE INDEX "idx_climate_monthly_municipality_id" ON "public"."municipality_climate_monthly" USING "btree" ("municipality_id");



CREATE INDEX "idx_climate_monthly_municipality_year_month" ON "public"."municipality_climate_monthly" USING "btree" ("municipality_id", "year", "month");



CREATE INDEX "idx_climate_monthly_year_month" ON "public"."municipality_climate_monthly" USING "btree" ("year", "month");



CREATE INDEX "idx_composite_suitability_score" ON "public"."composite_suitability" USING "btree" ("score") WHERE ("score" IS NOT NULL);



CREATE INDEX "idx_doe_datasets_name" ON "public"."doe_datasets" USING "btree" ("dataset_name");



CREATE INDEX "idx_forecast_cache_created" ON "public"."forecast_cache" USING "btree" ("created_at" DESC);



CREATE INDEX "idx_forecast_cache_geo" ON "public"."forecast_cache" USING "btree" ("geo_level", "geo_id") WHERE ("geo_id" IS NOT NULL);



CREATE INDEX "idx_forecast_cache_lookup" ON "public"."forecast_cache" USING "btree" ("target_variable", "forecast_year", "forecast_month");



CREATE INDEX "idx_forecast_cache_model" ON "public"."forecast_cache" USING "btree" ("model_id", "created_at" DESC);



CREATE INDEX "idx_forecast_model_runs_model" ON "public"."forecast_model_runs" USING "btree" ("model_id", "started_at" DESC);



CREATE INDEX "idx_forecast_model_runs_target" ON "public"."forecast_model_runs" USING "btree" ("target_variable", "started_at" DESC);



CREATE INDEX "idx_geospatial_barangay_id" ON "public"."geospatial_metadata" USING "btree" ("barangay_id") WHERE ("barangay_id" IS NOT NULL);



CREATE INDEX "idx_geospatial_municipality_id" ON "public"."geospatial_metadata" USING "btree" ("municipality_id") WHERE ("municipality_id" IS NOT NULL);



CREATE INDEX "idx_geospatial_province_id" ON "public"."geospatial_metadata" USING "btree" ("province_id") WHERE ("province_id" IS NOT NULL);



CREATE INDEX "idx_geospatial_region_id" ON "public"."geospatial_metadata" USING "btree" ("region_id") WHERE ("region_id" IS NOT NULL);



CREATE INDEX "idx_geothermal_faults_lat_lon" ON "public"."geothermal_faults" USING "btree" ("lat", "lon");



CREATE INDEX "idx_geothermal_heatflow_lat_lon" ON "public"."geothermal_heatflow" USING "btree" ("lat", "lon");



CREATE INDEX "idx_geothermal_output_municipality_id" ON "public"."geothermal_output" USING "btree" ("municipality_id");



CREATE INDEX "idx_geothermal_suitability_aquifer" ON "public"."geothermal_suitability" USING "btree" ("municipality_id", "aquifer_score");



CREATE INDEX "idx_geothermal_suitability_municipality_id" ON "public"."geothermal_suitability" USING "btree" ("municipality_id");



CREATE INDEX "idx_geothermal_volcanoes_lat_lon" ON "public"."geothermal_volcanoes" USING "btree" ("lat", "lon");



CREATE INDEX "idx_hydro_suitability_score" ON "public"."hydro_suitability" USING "btree" ("score") WHERE ("score" IS NOT NULL);



CREATE INDEX "idx_hydropower_suitability_municipality_name" ON "public"."hydropower_suitability" USING "btree" ("municipality_name");



CREATE INDEX "idx_hydropower_suitability_province_id" ON "public"."hydropower_suitability" USING "btree" ("province_id");



CREATE UNIQUE INDEX "idx_mcda_weights_active" ON "public"."mcda_weights" USING "btree" ("energy_type", "criterion") WHERE ("is_active" = true);



CREATE UNIQUE INDEX "idx_ml_model_active_unique" ON "public"."ml_model_registry" USING "btree" ("target_variable", "is_active") WHERE ("is_active" = true);



CREATE INDEX "idx_ml_model_type_target" ON "public"."ml_model_registry" USING "btree" ("model_type", "target_variable", "train_date" DESC);



CREATE INDEX "idx_muni_composite_score" ON "public"."municipalities" USING "btree" ("composite_suitability_score") WHERE ("composite_suitability_score" IS NOT NULL);



CREATE INDEX "idx_muni_geo_score" ON "public"."municipalities" USING "btree" ("geothermal_suitability_score") WHERE ("geothermal_suitability_score" IS NOT NULL);



CREATE INDEX "idx_muni_hydro_score" ON "public"."municipalities" USING "btree" ("hydro_suitability_score") WHERE ("hydro_suitability_score" IS NOT NULL);



CREATE INDEX "idx_muni_solar_score" ON "public"."municipalities" USING "btree" ("solar_suitability_score") WHERE ("solar_suitability_score" IS NOT NULL);



CREATE INDEX "idx_muni_wind_score" ON "public"."municipalities" USING "btree" ("wind_suitability_score") WHERE ("wind_suitability_score" IS NOT NULL);



CREATE INDEX "idx_municipal_population_province_id" ON "public"."municipal_population" USING "btree" ("province_id");



CREATE INDEX "idx_municipalities_province_id" ON "public"."municipalities" USING "btree" ("province_id");



CREATE INDEX "idx_municipalities_psgc_code" ON "public"."municipalities" USING "btree" ("psgc_code") WHERE ("psgc_code" IS NOT NULL);



CREATE INDEX "idx_municipality_climate_averages_municipality_id" ON "public"."municipality_climate_averages" USING "btree" ("municipality_id");



CREATE INDEX "idx_national_energy_year" ON "public"."national_energy_annual" USING "btree" ("year");



CREATE INDEX "idx_population_data_level_year" ON "public"."population_data" USING "btree" ("geographic_level", "year");



CREATE INDEX "idx_population_data_psgc_code" ON "public"."population_data" USING "btree" ("psgc_code");



CREATE INDEX "idx_products_category" ON "public"."products" USING "btree" ("energy_category");



CREATE INDEX "idx_products_normalized" ON "public"."products" USING "btree" ("product_name_normalized");



CREATE INDEX "idx_province_climate_monthly_province_id" ON "public"."province_climate_monthly" USING "btree" ("province_id");



CREATE INDEX "idx_province_climate_monthly_province_year_month" ON "public"."province_climate_monthly" USING "btree" ("province_id", "year", "month");



CREATE INDEX "idx_province_climate_monthly_year_month" ON "public"."province_climate_monthly" USING "btree" ("year", "month");



CREATE INDEX "idx_provinces_geojson_name" ON "public"."provinces" USING "btree" ("geojson_name");



CREATE INDEX "idx_provinces_psgc_code" ON "public"."provinces" USING "btree" ("psgc_code") WHERE ("psgc_code" IS NOT NULL);



CREATE INDEX "idx_provinces_region_id" ON "public"."provinces" USING "btree" ("region_id");



CREATE INDEX "idx_regions_psgc_code" ON "public"."regions" USING "btree" ("psgc_code") WHERE ("psgc_code" IS NOT NULL);



CREATE INDEX "idx_saved_locations_user_id" ON "public"."saved_locations" USING "btree" ("user_id");



CREATE INDEX "idx_saved_simulations_municipality_id" ON "public"."saved_simulations" USING "btree" ("municipality_id");



CREATE INDEX "idx_saved_simulations_user_id" ON "public"."saved_simulations" USING "btree" ("user_id");



CREATE INDEX "idx_solar_suitability_score" ON "public"."solar_suitability" USING "btree" ("score") WHERE ("score" IS NOT NULL);



CREATE INDEX "idx_wind_products_cp" ON "public"."wind_products" USING "btree" ("power_coefficient") WHERE ("power_coefficient" IS NOT NULL);



CREATE INDEX "idx_wind_products_rotor" ON "public"."wind_products" USING "btree" ("rotor_radius_m") WHERE ("rotor_radius_m" IS NOT NULL);



CREATE INDEX "idx_wind_suitability_score" ON "public"."wind_suitability" USING "btree" ("score") WHERE ("score" IS NOT NULL);



CREATE INDEX "rag_chunks_category_idx" ON "public"."rag_chunks" USING "btree" ("category");



CREATE INDEX "rag_chunks_embedding_idx" ON "public"."rag_chunks" USING "ivfflat" ("embedding" "extensions"."vector_cosine_ops");



CREATE INDEX "rag_chunks_renewable_type_idx" ON "public"."rag_chunks" USING "btree" ("renewable_type");



CREATE INDEX "rag_chunks_search_vector_idx" ON "public"."rag_chunks" USING "gin" ("search_vector");



CREATE OR REPLACE TRIGGER "trg_composite_suitability_updated" BEFORE UPDATE ON "public"."composite_suitability" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



CREATE OR REPLACE TRIGGER "trg_forecast_model_runs_updated" BEFORE UPDATE ON "public"."forecast_model_runs" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



CREATE OR REPLACE TRIGGER "trg_geospatial_metadata_updated" BEFORE UPDATE ON "public"."geospatial_metadata" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



CREATE OR REPLACE TRIGGER "trg_hydro_suitability_updated" BEFORE UPDATE ON "public"."hydro_suitability" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



CREATE OR REPLACE TRIGGER "trg_ml_model_registry_updated" BEFORE UPDATE ON "public"."ml_model_registry" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



CREATE OR REPLACE TRIGGER "trg_national_energy_annual_updated" BEFORE UPDATE ON "public"."national_energy_annual" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



CREATE OR REPLACE TRIGGER "trg_solar_suitability_updated" BEFORE UPDATE ON "public"."solar_suitability" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



CREATE OR REPLACE TRIGGER "trg_wind_suitability_updated" BEFORE UPDATE ON "public"."wind_suitability" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();



ALTER TABLE ONLY "public"."admin_audit_log"
    ADD CONSTRAINT "admin_audit_log_admin_id_fkey" FOREIGN KEY ("admin_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."admin_audit_log"
    ADD CONSTRAINT "admin_audit_log_target_user_id_fkey" FOREIGN KEY ("target_user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."barangay_climate_monthly"
    ADD CONSTRAINT "barangay_climate_monthly_barangay_id_fkey" FOREIGN KEY ("barangay_id") REFERENCES "public"."barangays"("barangay_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."barangays"
    ADD CONSTRAINT "barangays_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."chat_messages"
    ADD CONSTRAINT "chat_messages_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."chat_sessions"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."chat_sessions"
    ADD CONSTRAINT "chat_sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."composite_suitability"
    ADD CONSTRAINT "composite_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."forecast_cache"
    ADD CONSTRAINT "forecast_cache_model_id_fkey" FOREIGN KEY ("model_id") REFERENCES "public"."ml_model_registry"("model_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."forecast_model_runs"
    ADD CONSTRAINT "forecast_model_runs_model_id_fkey" FOREIGN KEY ("model_id") REFERENCES "public"."ml_model_registry"("model_id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."geospatial_metadata"
    ADD CONSTRAINT "geospatial_metadata_barangay_id_fkey" FOREIGN KEY ("barangay_id") REFERENCES "public"."barangays"("barangay_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."geospatial_metadata"
    ADD CONSTRAINT "geospatial_metadata_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."geospatial_metadata"
    ADD CONSTRAINT "geospatial_metadata_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."geospatial_metadata"
    ADD CONSTRAINT "geospatial_metadata_region_id_fkey" FOREIGN KEY ("region_id") REFERENCES "public"."regions"("region_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."geothermal_output"
    ADD CONSTRAINT "geothermal_output_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."geothermal_suitability"
    ADD CONSTRAINT "geothermal_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."hydro_suitability"
    ADD CONSTRAINT "hydro_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."hydropower_suitability"
    ADD CONSTRAINT "hydropower_suitability_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."municipal_population"
    ADD CONSTRAINT "municipal_population_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."municipal_population"
    ADD CONSTRAINT "municipal_population_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."municipalities"
    ADD CONSTRAINT "municipalities_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."municipality_climate_averages"
    ADD CONSTRAINT "municipality_climate_averages_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."municipality_climate_monthly"
    ADD CONSTRAINT "municipality_climate_monthly_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_id_fkey" FOREIGN KEY ("id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."province_climate_monthly"
    ADD CONSTRAINT "province_climate_monthly_province_id_fkey" FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."provinces"
    ADD CONSTRAINT "provinces_region_id_fkey" FOREIGN KEY ("region_id") REFERENCES "public"."regions"("region_id") ON UPDATE CASCADE ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."saved_locations"
    ADD CONSTRAINT "saved_locations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."saved_simulations"
    ADD CONSTRAINT "saved_simulations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."solar_suitability"
    ADD CONSTRAINT "solar_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_usage_limits"
    ADD CONSTRAINT "user_usage_limits_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."wind_suitability"
    ADD CONSTRAINT "wind_suitability_municipality_id_fkey" FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;



CREATE POLICY "Admins can view audit log" ON "public"."admin_audit_log" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM "public"."user_roles" "r"
  WHERE (("r"."user_id" = "auth"."uid"()) AND ("r"."role" = ANY (ARRAY['admin'::"public"."app_role", 'dev'::"public"."app_role"]))))));



CREATE POLICY "Admins read all profiles" ON "public"."profiles" FOR SELECT USING ("public"."is_admin"());



CREATE POLICY "Admins read all roles" ON "public"."user_roles" FOR SELECT USING ("public"."is_admin"());



CREATE POLICY "Admins read audit log" ON "public"."admin_audit_log" FOR SELECT USING ("public"."is_admin"());



CREATE POLICY "Admins update system config" ON "public"."system_config" USING ("public"."is_admin"());



CREATE POLICY "Allow authenticated read on forecast_cache" ON "public"."forecast_cache" FOR SELECT USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on barangay_climate_monthly" ON "public"."barangay_climate_monthly" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on composite_suitability" ON "public"."composite_suitability" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on doe_datasets" ON "public"."doe_datasets" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on forecast_cache" ON "public"."forecast_cache" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on geospatial_metadata" ON "public"."geospatial_metadata" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on geothermal_faults" ON "public"."geothermal_faults" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on geothermal_heatflow" ON "public"."geothermal_heatflow" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on geothermal_volcanoes" ON "public"."geothermal_volcanoes" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on hydro_suitability" ON "public"."hydro_suitability" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on ml_model_registry" ON "public"."ml_model_registry" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on municipal_population" ON "public"."municipal_population" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on municipality_climate_averages" ON "public"."municipality_climate_averages" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on national_energy_annual" ON "public"."national_energy_annual" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on population_data" ON "public"."population_data" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on products" ON "public"."products" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on province_climate_monthly" ON "public"."province_climate_monthly" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on solar_suitability" ON "public"."solar_suitability" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on wind_products" ON "public"."wind_products" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on wind_products_summary" ON "public"."wind_products_summary" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow authenticated write on wind_suitability" ON "public"."wind_suitability" USING (("auth"."role"() = 'authenticated'::"text"));



CREATE POLICY "Allow public read on barangay_climate_monthly" ON "public"."barangay_climate_monthly" FOR SELECT USING (true);



CREATE POLICY "Allow public read on composite_suitability" ON "public"."composite_suitability" FOR SELECT USING (true);



CREATE POLICY "Allow public read on doe_datasets" ON "public"."doe_datasets" FOR SELECT USING (true);



CREATE POLICY "Allow public read on geospatial_metadata" ON "public"."geospatial_metadata" FOR SELECT USING (true);



CREATE POLICY "Allow public read on geothermal_faults" ON "public"."geothermal_faults" FOR SELECT USING (true);



CREATE POLICY "Allow public read on geothermal_heatflow" ON "public"."geothermal_heatflow" FOR SELECT USING (true);



CREATE POLICY "Allow public read on geothermal_volcanoes" ON "public"."geothermal_volcanoes" FOR SELECT USING (true);



CREATE POLICY "Allow public read on hydro_suitability" ON "public"."hydro_suitability" FOR SELECT USING (true);



CREATE POLICY "Allow public read on ml_model_registry" ON "public"."ml_model_registry" FOR SELECT USING (true);



CREATE POLICY "Allow public read on municipal_population" ON "public"."municipal_population" FOR SELECT USING (true);



CREATE POLICY "Allow public read on municipality_climate_averages" ON "public"."municipality_climate_averages" FOR SELECT USING (true);



CREATE POLICY "Allow public read on national_energy_annual" ON "public"."national_energy_annual" FOR SELECT USING (true);



CREATE POLICY "Allow public read on population_data" ON "public"."population_data" FOR SELECT USING (true);



CREATE POLICY "Allow public read on products" ON "public"."products" FOR SELECT USING (true);



CREATE POLICY "Allow public read on province_climate_monthly" ON "public"."province_climate_monthly" FOR SELECT USING (true);



CREATE POLICY "Allow public read on solar_suitability" ON "public"."solar_suitability" FOR SELECT USING (true);



CREATE POLICY "Allow public read on wind_products" ON "public"."wind_products" FOR SELECT USING (true);



CREATE POLICY "Allow public read on wind_products_summary" ON "public"."wind_products_summary" FOR SELECT USING (true);



CREATE POLICY "Allow public read on wind_suitability" ON "public"."wind_suitability" FOR SELECT USING (true);



CREATE POLICY "Anyone read system config" ON "public"."system_config" FOR SELECT TO "authenticated", "anon" USING (true);



CREATE POLICY "Service role all on forecast_model_runs" ON "public"."forecast_model_runs" USING (("auth"."role"() = 'service_role'::"text")) WITH CHECK (("auth"."role"() = 'service_role'::"text"));



CREATE POLICY "Users can CRUD own chat messages" ON "public"."chat_messages" USING ((EXISTS ( SELECT 1
   FROM "public"."chat_sessions" "s"
  WHERE (("s"."id" = "chat_messages"."session_id") AND ("s"."user_id" = "auth"."uid"())))));



CREATE POLICY "Users can CRUD own chat sessions" ON "public"."chat_sessions" USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users can CRUD own locations" ON "public"."saved_locations" USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users can CRUD own simulations" ON "public"."saved_simulations" USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users can update own profile" ON "public"."profiles" FOR UPDATE USING (("auth"."uid"() = "id"));



CREATE POLICY "Users can view own profile" ON "public"."profiles" FOR SELECT USING (("auth"."uid"() = "id"));



CREATE POLICY "Users can view own usage" ON "public"."user_usage_limits" FOR SELECT USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users manage own chat messages" ON "public"."chat_messages" USING ((EXISTS ( SELECT 1
   FROM "public"."chat_sessions" "cs"
  WHERE (("cs"."id" = "chat_messages"."session_id") AND ("cs"."user_id" = "auth"."uid"())))));



CREATE POLICY "Users manage own chat sessions" ON "public"."chat_sessions" USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users manage own simulations" ON "public"."saved_simulations" USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users read own profile" ON "public"."profiles" FOR SELECT USING (("auth"."uid"() = "id"));



CREATE POLICY "Users read own role" ON "public"."user_roles" FOR SELECT USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users update own profile" ON "public"."profiles" FOR UPDATE USING (("auth"."uid"() = "id")) WITH CHECK (("auth"."uid"() = "id"));



ALTER TABLE "public"."admin_audit_log" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."barangay_climate_monthly" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."chat_messages" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."chat_sessions" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."composite_suitability" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."doe_datasets" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."forecast_cache" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."forecast_model_runs" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."geospatial_metadata" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."geothermal_faults" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."geothermal_heatflow" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."geothermal_volcanoes" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."hydro_suitability" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."ml_model_registry" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."municipal_population" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."municipality_climate_averages" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."national_energy_annual" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."population_data" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."products" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."profiles" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."province_climate_monthly" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."rag_chunks" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "rag_chunks_select_policy" ON "public"."rag_chunks" FOR SELECT USING (true);



CREATE POLICY "rag_chunks_write_policy" ON "public"."rag_chunks" USING (false) WITH CHECK (false);



ALTER TABLE "public"."saved_locations" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."saved_simulations" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."solar_suitability" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."system_config" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_roles" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_usage_limits" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."wind_products" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."wind_products_summary" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."wind_suitability" ENABLE ROW LEVEL SECURITY;




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



GRANT ALL ON FUNCTION "public"."is_admin"() TO "anon";
GRANT ALL ON FUNCTION "public"."is_admin"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."is_admin"() TO "service_role";






GRANT ALL ON FUNCTION "public"."set_updated_at"() TO "anon";
GRANT ALL ON FUNCTION "public"."set_updated_at"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."set_updated_at"() TO "service_role";






























GRANT ALL ON TABLE "public"."admin_audit_log" TO "anon";
GRANT ALL ON TABLE "public"."admin_audit_log" TO "authenticated";
GRANT ALL ON TABLE "public"."admin_audit_log" TO "service_role";



GRANT ALL ON TABLE "public"."barangay_climate_monthly" TO "anon";
GRANT ALL ON TABLE "public"."barangay_climate_monthly" TO "authenticated";
GRANT ALL ON TABLE "public"."barangay_climate_monthly" TO "service_role";



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



GRANT ALL ON TABLE "public"."composite_suitability" TO "anon";
GRANT ALL ON TABLE "public"."composite_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."composite_suitability" TO "service_role";



GRANT ALL ON TABLE "public"."doe_datasets" TO "anon";
GRANT ALL ON TABLE "public"."doe_datasets" TO "authenticated";
GRANT ALL ON TABLE "public"."doe_datasets" TO "service_role";



GRANT ALL ON TABLE "public"."forecast_cache" TO "anon";
GRANT ALL ON TABLE "public"."forecast_cache" TO "authenticated";
GRANT ALL ON TABLE "public"."forecast_cache" TO "service_role";



GRANT ALL ON TABLE "public"."forecast_model_runs" TO "anon";
GRANT ALL ON TABLE "public"."forecast_model_runs" TO "authenticated";
GRANT ALL ON TABLE "public"."forecast_model_runs" TO "service_role";



GRANT ALL ON TABLE "public"."geospatial_metadata" TO "anon";
GRANT ALL ON TABLE "public"."geospatial_metadata" TO "authenticated";
GRANT ALL ON TABLE "public"."geospatial_metadata" TO "service_role";



GRANT ALL ON TABLE "public"."geothermal_faults" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_faults" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_faults" TO "service_role";



GRANT ALL ON SEQUENCE "public"."geothermal_faults_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."geothermal_faults_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."geothermal_faults_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."geothermal_heatflow" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_heatflow" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_heatflow" TO "service_role";



GRANT ALL ON SEQUENCE "public"."geothermal_heatflow_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."geothermal_heatflow_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."geothermal_heatflow_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."geothermal_output" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_output" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_output" TO "service_role";



GRANT ALL ON TABLE "public"."geothermal_suitability" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_suitability" TO "service_role";



GRANT ALL ON TABLE "public"."geothermal_volcanoes" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_volcanoes" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_volcanoes" TO "service_role";



GRANT ALL ON SEQUENCE "public"."geothermal_volcanoes_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."geothermal_volcanoes_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."geothermal_volcanoes_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."hydro_suitability" TO "anon";
GRANT ALL ON TABLE "public"."hydro_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."hydro_suitability" TO "service_role";



GRANT ALL ON TABLE "public"."hydropower_suitability" TO "anon";
GRANT ALL ON TABLE "public"."hydropower_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."hydropower_suitability" TO "service_role";



GRANT ALL ON TABLE "public"."mcda_weights" TO "anon";
GRANT ALL ON TABLE "public"."mcda_weights" TO "authenticated";
GRANT ALL ON TABLE "public"."mcda_weights" TO "service_role";



GRANT ALL ON SEQUENCE "public"."mcda_weights_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."mcda_weights_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."mcda_weights_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."ml_model_registry" TO "anon";
GRANT ALL ON TABLE "public"."ml_model_registry" TO "authenticated";
GRANT ALL ON TABLE "public"."ml_model_registry" TO "service_role";



GRANT ALL ON TABLE "public"."municipal_population" TO "anon";
GRANT ALL ON TABLE "public"."municipal_population" TO "authenticated";
GRANT ALL ON TABLE "public"."municipal_population" TO "service_role";



GRANT ALL ON TABLE "public"."municipalities" TO "anon";
GRANT ALL ON TABLE "public"."municipalities" TO "authenticated";
GRANT ALL ON TABLE "public"."municipalities" TO "service_role";



GRANT ALL ON TABLE "public"."municipality_climate_averages" TO "anon";
GRANT ALL ON TABLE "public"."municipality_climate_averages" TO "authenticated";
GRANT ALL ON TABLE "public"."municipality_climate_averages" TO "service_role";



GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "anon";
GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "authenticated";
GRANT ALL ON TABLE "public"."municipality_climate_monthly" TO "service_role";



GRANT ALL ON TABLE "public"."national_energy_annual" TO "anon";
GRANT ALL ON TABLE "public"."national_energy_annual" TO "authenticated";
GRANT ALL ON TABLE "public"."national_energy_annual" TO "service_role";



GRANT ALL ON TABLE "public"."population_data" TO "anon";
GRANT ALL ON TABLE "public"."population_data" TO "authenticated";
GRANT ALL ON TABLE "public"."population_data" TO "service_role";



GRANT ALL ON TABLE "public"."products" TO "anon";
GRANT ALL ON TABLE "public"."products" TO "authenticated";
GRANT ALL ON TABLE "public"."products" TO "service_role";



GRANT ALL ON SEQUENCE "public"."products_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."products_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."products_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."profiles" TO "anon";
GRANT ALL ON TABLE "public"."profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."profiles" TO "service_role";



GRANT ALL ON TABLE "public"."province_climate_monthly" TO "anon";
GRANT ALL ON TABLE "public"."province_climate_monthly" TO "authenticated";
GRANT ALL ON TABLE "public"."province_climate_monthly" TO "service_role";



GRANT ALL ON TABLE "public"."province_climate_annual" TO "anon";
GRANT ALL ON TABLE "public"."province_climate_annual" TO "authenticated";
GRANT ALL ON TABLE "public"."province_climate_annual" TO "service_role";



GRANT ALL ON TABLE "public"."provinces" TO "anon";
GRANT ALL ON TABLE "public"."provinces" TO "authenticated";
GRANT ALL ON TABLE "public"."provinces" TO "service_role";



GRANT ALL ON TABLE "public"."rag_chunks" TO "anon";
GRANT ALL ON TABLE "public"."rag_chunks" TO "authenticated";
GRANT ALL ON TABLE "public"."rag_chunks" TO "service_role";



GRANT ALL ON SEQUENCE "public"."rag_chunks_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."rag_chunks_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."rag_chunks_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."regions" TO "anon";
GRANT ALL ON TABLE "public"."regions" TO "authenticated";
GRANT ALL ON TABLE "public"."regions" TO "service_role";



GRANT ALL ON TABLE "public"."regional_lookup" TO "anon";
GRANT ALL ON TABLE "public"."regional_lookup" TO "authenticated";
GRANT ALL ON TABLE "public"."regional_lookup" TO "service_role";



GRANT ALL ON TABLE "public"."regional_lookup_v2" TO "anon";
GRANT ALL ON TABLE "public"."regional_lookup_v2" TO "authenticated";
GRANT ALL ON TABLE "public"."regional_lookup_v2" TO "service_role";



GRANT ALL ON TABLE "public"."saved_locations" TO "anon";
GRANT ALL ON TABLE "public"."saved_locations" TO "authenticated";
GRANT ALL ON TABLE "public"."saved_locations" TO "service_role";



GRANT ALL ON TABLE "public"."saved_simulations" TO "anon";
GRANT ALL ON TABLE "public"."saved_simulations" TO "authenticated";
GRANT ALL ON TABLE "public"."saved_simulations" TO "service_role";



GRANT ALL ON TABLE "public"."solar_suitability" TO "anon";
GRANT ALL ON TABLE "public"."solar_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."solar_suitability" TO "service_role";



GRANT ALL ON TABLE "public"."system_config" TO "anon";
GRANT ALL ON TABLE "public"."system_config" TO "authenticated";
GRANT ALL ON TABLE "public"."system_config" TO "service_role";



GRANT ALL ON TABLE "public"."user_roles" TO "anon";
GRANT ALL ON TABLE "public"."user_roles" TO "authenticated";
GRANT ALL ON TABLE "public"."user_roles" TO "service_role";



GRANT ALL ON TABLE "public"."user_usage_limits" TO "anon";
GRANT ALL ON TABLE "public"."user_usage_limits" TO "authenticated";
GRANT ALL ON TABLE "public"."user_usage_limits" TO "service_role";



GRANT ALL ON TABLE "public"."wind_products" TO "anon";
GRANT ALL ON TABLE "public"."wind_products" TO "authenticated";
GRANT ALL ON TABLE "public"."wind_products" TO "service_role";



GRANT ALL ON SEQUENCE "public"."wind_products_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."wind_products_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."wind_products_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."wind_products_summary" TO "anon";
GRANT ALL ON TABLE "public"."wind_products_summary" TO "authenticated";
GRANT ALL ON TABLE "public"."wind_products_summary" TO "service_role";



GRANT ALL ON TABLE "public"."wind_suitability" TO "anon";
GRANT ALL ON TABLE "public"."wind_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."wind_suitability" TO "service_role";









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































