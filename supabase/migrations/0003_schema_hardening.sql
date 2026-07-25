-- ============================================================================
-- LUMI Schema Hardening Migration
-- Migration: 0003_schema_hardening.sql
-- Additive only: new tables, indexes, constraints, triggers, views, RLS
-- ============================================================================

-- SECTION 1: New Tables

CREATE TABLE IF NOT EXISTS "public"."cost_benchmarks" (
    "id" uuid DEFAULT "gen_random_uuid"() NOT NULL,
    "category" text NOT NULL,
    "component" text NOT NULL,
    "brand" text,
    "model" text,
    "capacity_w" numeric(12,2),
    "unit_price_php" numeric(12,2),
    "installation_cost_php" numeric(12,2),
    "source" text,
    "source_url" text,
    "recorded_date" date DEFAULT CURRENT_DATE,
    "created_at" timestamptz DEFAULT now() NOT NULL,
    "updated_at" timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT "cost_benchmarks_pkey" PRIMARY KEY ("id")
);
ALTER TABLE "public"."cost_benchmarks" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."du_rate_schedules" (
    "id" uuid DEFAULT "gen_random_uuid"() NOT NULL,
    "du_name" text NOT NULL,
    "province" text,
    "rate_class" text NOT NULL,
    "generation_charge_php_kwh" numeric(10,4),
    "transmission_charge_php_kwh" numeric(10,4),
    "distribution_charge_php_kwh" numeric(10,4),
    "supply_charge_php_kwh" numeric(10,4),
    "metering_charge_php_kwh" numeric(10,4),
    "lifeline_rate_php_kwh" numeric(10,4),
    "intermediate_rate_php_kwh" numeric(10,4),
    "standard_rate_php_kwh" numeric(10,4),
    "effective_date" date NOT NULL,
    "expiry_date" date,
    "source" text,
    "source_url" text,
    "created_at" timestamptz DEFAULT now() NOT NULL,
    "updated_at" timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT "du_rate_schedules_pkey" PRIMARY KEY ("id")
);
ALTER TABLE "public"."du_rate_schedules" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."mcda_weights" (
    "id" uuid DEFAULT "gen_random_uuid"() NOT NULL,
    "energy_type" text NOT NULL,
    "criterion" text NOT NULL,
    "weight" numeric(5,4) NOT NULL,
    "is_active" boolean DEFAULT true NOT NULL,
    "created_at" timestamptz DEFAULT now() NOT NULL,
    "updated_at" timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT "mcda_weights_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "mcda_weights_weight_check" CHECK ("weight" >= 0 AND "weight" <= 1),
    CONSTRAINT "mcda_weights_energy_type_check" CHECK ("energy_type" IN ('solar','wind','hydro','geothermal'))
);
ALTER TABLE "public"."mcda_weights" OWNER TO "postgres";
CREATE UNIQUE INDEX IF NOT EXISTS "idx_mcda_weights_unique"
    ON "public"."mcda_weights" ("energy_type","criterion") WHERE "is_active" = true;

CREATE TABLE IF NOT EXISTS "public"."coverage_summary" (
    "municipality_id" integer NOT NULL,
    "has_climate_data" boolean DEFAULT false NOT NULL,
    "has_solar_score" boolean DEFAULT false NOT NULL,
    "has_wind_score" boolean DEFAULT false NOT NULL,
    "has_hydro_score" boolean DEFAULT false NOT NULL,
    "has_geothermal_score" boolean DEFAULT false NOT NULL,
    "has_population_data" boolean DEFAULT false NOT NULL,
    "has_tariff_data" boolean DEFAULT false NOT NULL,
    "climate_records_count" integer DEFAULT 0,
    "last_updated" timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT "coverage_summary_pkey" PRIMARY KEY ("municipality_id")
);
ALTER TABLE "public"."coverage_summary" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."data_lineage" (
    "id" uuid DEFAULT "gen_random_uuid"() NOT NULL,
    "source_name" text NOT NULL,
    "source_type" text NOT NULL,
    "table_name" text,
    "records_inserted" integer DEFAULT 0,
    "records_updated" integer DEFAULT 0,
    "records_failed" integer DEFAULT 0,
    "status" text NOT NULL DEFAULT 'success',
    "error_message" text,
    "run_started_at" timestamptz NOT NULL,
    "run_finished_at" timestamptz,
    "metadata" jsonb,
    "created_at" timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT "data_lineage_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "data_lineage_status_check" CHECK ("status" IN ('success','partial','failed','running'))
);
ALTER TABLE "public"."data_lineage" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."forecast_model_runs" (
    "id" uuid DEFAULT "gen_random_uuid"() NOT NULL,
    "model_id" uuid,
    "run_type" text NOT NULL DEFAULT 'train',
    "target_variable" text NOT NULL,
    "hyperparameters" jsonb,
    "metrics" jsonb,
    "artifact_path" text,
    "started_at" timestamptz NOT NULL,
    "finished_at" timestamptz,
    "status" text NOT NULL DEFAULT 'running',
    "created_at" timestamptz DEFAULT now() NOT NULL,
    "updated_at" timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT "forecast_model_runs_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "forecast_model_runs_status_check" CHECK ("status" IN ('running','success','failed','cancelled')),
    CONSTRAINT "forecast_model_runs_run_type_check" CHECK ("run_type" IN ('train','backtest','retrain','evaluate'))
);
ALTER TABLE "public"."forecast_model_runs" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."solar_suitability" (
    "municipality_id" integer NOT NULL,
    "province_id" integer NOT NULL,
    "municipality_name" text NOT NULL,
    "ghi_kwh_m2_day" double precision,
    "dni_kwh_m2_day" double precision,
    "dhi_kwh_m2_day" double precision,
    "avg_temp_c" double precision,
    "cloud_cover_pct" double precision,
    "terrain_slope_deg" double precision,
    "land_use_factor" double precision,
    "suitability_score" numeric(5,2),
    "classification" varchar(20),
    "factors" jsonb,
    "updated_at" timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT "solar_suitability_pkey" PRIMARY KEY ("municipality_id"),
    CONSTRAINT "solar_suitability_score_check" CHECK ("suitability_score" IS NULL OR ("suitability_score" >= 0 AND "suitability_score" <= 100))
);
ALTER TABLE "public"."solar_suitability" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."wind_suitability" (
    "municipality_id" integer NOT NULL,
    "province_id" integer NOT NULL,
    "municipality_name" text NOT NULL,
    "ws10m_ms" double precision,
    "ws50m_ms" double precision,
    "ws100m_ms" double precision,
    "elevation_m" double precision,
    "terrain_roughness" double precision,
    "air_density_kg_m3" double precision,
    "land_use_factor" double precision,
    "suitability_score" numeric(5,2),
    "classification" varchar(20),
    "factors" jsonb,
    "updated_at" timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT "wind_suitability_pkey" PRIMARY KEY ("municipality_id"),
    CONSTRAINT "wind_suitability_score_check" CHECK ("suitability_score" IS NULL OR ("suitability_score" >= 0 AND "suitability_score" <= 100))
);
ALTER TABLE "public"."wind_suitability" OWNER TO "postgres";

-- SECTION 2: Foreign Keys

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'coverage_summary_municipality_id_fkey') THEN
        ALTER TABLE "public"."coverage_summary" ADD CONSTRAINT "coverage_summary_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'forecast_model_runs_model_id_fkey') THEN
        ALTER TABLE "public"."forecast_model_runs" ADD CONSTRAINT "forecast_model_runs_model_id_fkey"
            FOREIGN KEY ("model_id") REFERENCES "public"."ml_model_registry"("model_id") ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'solar_suitability_municipality_id_fkey') THEN
        ALTER TABLE "public"."solar_suitability" ADD CONSTRAINT "solar_suitability_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'solar_suitability_province_id_fkey') THEN
        ALTER TABLE "public"."solar_suitability" ADD CONSTRAINT "solar_suitability_province_id_fkey"
            FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'wind_suitability_municipality_id_fkey') THEN
        ALTER TABLE "public"."wind_suitability" ADD CONSTRAINT "wind_suitability_municipality_id_fkey"
            FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id") ON UPDATE CASCADE ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'wind_suitability_province_id_fkey') THEN
        ALTER TABLE "public"."wind_suitability" ADD CONSTRAINT "wind_suitability_province_id_fkey"
            FOREIGN KEY ("province_id") REFERENCES "public"."provinces"("province_id") ON UPDATE CASCADE ON DELETE RESTRICT;
    END IF;
END $$;

-- SECTION 3: CHECK Constraints on Existing Score Columns

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'municipalities_solar_score_range') THEN
        ALTER TABLE "public"."municipalities" ADD CONSTRAINT "municipalities_solar_score_range"
            CHECK ("solar_suitability_score" IS NULL OR ("solar_suitability_score" >= 0 AND "solar_suitability_score" <= 100));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'municipalities_wind_score_range') THEN
        ALTER TABLE "public"."municipalities" ADD CONSTRAINT "municipalities_wind_score_range"
            CHECK ("wind_suitability_score" IS NULL OR ("wind_suitability_score" >= 0 AND "wind_suitability_score" <= 100));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'municipalities_hydro_score_range') THEN
        ALTER TABLE "public"."municipalities" ADD CONSTRAINT "municipalities_hydro_score_range"
            CHECK ("hydro_suitability_score" IS NULL OR ("hydro_suitability_score" >= 0 AND "hydro_suitability_score" <= 100));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'municipalities_geo_score_range') THEN
        ALTER TABLE "public"."municipalities" ADD CONSTRAINT "municipalities_geo_score_range"
            CHECK ("geothermal_suitability_score" IS NULL OR ("geothermal_suitability_score" >= 0 AND "geothermal_suitability_score" <= 100));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'municipalities_composite_score_range') THEN
        ALTER TABLE "public"."municipalities" ADD CONSTRAINT "municipalities_composite_score_range"
            CHECK ("composite_suitability_score" IS NULL OR ("composite_suitability_score" >= 0 AND "composite_suitability_score" <= 100));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'geothermal_suitability_score_range') THEN
        ALTER TABLE "public"."geothermal_suitability" ADD CONSTRAINT "geothermal_suitability_score_range"
            CHECK ("suitability_score" IS NULL OR ("suitability_score" >= 0 AND "suitability_score" <= 100));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'hydropower_suitability_score_range') THEN
        ALTER TABLE "public"."hydropower_suitability" ADD CONSTRAINT "hydropower_suitability_score_range"
            CHECK ("suitability_score" IS NULL OR ("suitability_score" >= 0 AND "suitability_score" <= 100));
    END IF;
END $$;

-- SECTION 4: Additional Indexes

CREATE INDEX IF NOT EXISTS "idx_municipalities_province_name" ON "public"."municipalities" USING "btree" ("province_id","name");
CREATE INDEX IF NOT EXISTS "idx_municipalities_lat_lon" ON "public"."municipalities" USING "btree" ("lat","lon") WHERE "lat" IS NOT NULL AND "lon" IS NOT NULL;
CREATE INDEX IF NOT EXISTS "idx_coverage_summary_gaps" ON "public"."coverage_summary" USING "btree" ("has_climate_data") WHERE "has_climate_data" = false;
CREATE INDEX IF NOT EXISTS "idx_data_lineage_source_date" ON "public"."data_lineage" USING "btree" ("source_name","created_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_data_lineage_table" ON "public"."data_lineage" USING "btree" ("table_name","created_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_forecast_model_runs_model" ON "public"."forecast_model_runs" USING "btree" ("model_id","started_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_forecast_model_runs_target" ON "public"."forecast_model_runs" USING "btree" ("target_variable","started_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_cost_benchmarks_category" ON "public"."cost_benchmarks" USING "btree" ("category","component");
CREATE INDEX IF NOT EXISTS "idx_cost_benchmarks_date" ON "public"."cost_benchmarks" USING "btree" ("recorded_date" DESC);
CREATE INDEX IF NOT EXISTS "idx_du_rate_schedules_du" ON "public"."du_rate_schedules" USING "btree" ("du_name","effective_date" DESC);
CREATE INDEX IF NOT EXISTS "idx_du_rate_schedules_province" ON "public"."du_rate_schedules" USING "btree" ("province");
CREATE INDEX IF NOT EXISTS "idx_solar_suitability_province_id" ON "public"."solar_suitability" USING "btree" ("province_id");
CREATE INDEX IF NOT EXISTS "idx_solar_suitability_score" ON "public"."solar_suitability" USING "btree" ("suitability_score" DESC) WHERE "suitability_score" IS NOT NULL;
CREATE INDEX IF NOT EXISTS "idx_wind_suitability_province_id" ON "public"."wind_suitability" USING "btree" ("province_id");
CREATE INDEX IF NOT EXISTS "idx_wind_suitability_score" ON "public"."wind_suitability" USING "btree" ("suitability_score" DESC) WHERE "suitability_score" IS NOT NULL;

-- SECTION 5: Updated_at Triggers

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'barangays' AND trigger_name = 'trg_barangays_updated') THEN
        CREATE TRIGGER "trg_barangays_updated" BEFORE UPDATE ON "public"."barangays" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'chat_messages' AND trigger_name = 'trg_chat_messages_updated') THEN
        CREATE TRIGGER "trg_chat_messages_updated" BEFORE UPDATE ON "public"."chat_messages" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'chat_sessions' AND trigger_name = 'trg_chat_sessions_updated') THEN
        CREATE TRIGGER "trg_chat_sessions_updated" BEFORE UPDATE ON "public"."chat_sessions" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'forecast_cache' AND trigger_name = 'trg_forecast_cache_updated') THEN
        CREATE TRIGGER "trg_forecast_cache_updated" BEFORE UPDATE ON "public"."forecast_cache" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'geothermal_output' AND trigger_name = 'trg_geothermal_output_updated') THEN
        CREATE TRIGGER "trg_geothermal_output_updated" BEFORE UPDATE ON "public"."geothermal_output" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'geothermal_suitability' AND trigger_name = 'trg_geothermal_suitability_updated') THEN
        CREATE TRIGGER "trg_geothermal_suitability_updated" BEFORE UPDATE ON "public"."geothermal_suitability" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'hydropower_suitability' AND trigger_name = 'trg_hydropower_suitability_updated') THEN
        CREATE TRIGGER "trg_hydropower_suitability_updated" BEFORE UPDATE ON "public"."hydropower_suitability" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'municipalities' AND trigger_name = 'trg_municipalities_updated') THEN
        CREATE TRIGGER "trg_municipalities_updated" BEFORE UPDATE ON "public"."municipalities" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'municipality_climate_monthly' AND trigger_name = 'trg_climate_monthly_updated') THEN
        CREATE TRIGGER "trg_climate_monthly_updated" BEFORE UPDATE ON "public"."municipality_climate_monthly" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'profiles' AND trigger_name = 'trg_profiles_updated') THEN
        CREATE TRIGGER "trg_profiles_updated" BEFORE UPDATE ON "public"."profiles" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'provinces' AND trigger_name = 'trg_provinces_updated') THEN
        CREATE TRIGGER "trg_provinces_updated" BEFORE UPDATE ON "public"."provinces" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'regions' AND trigger_name = 'trg_regions_updated') THEN
        CREATE TRIGGER "trg_regions_updated" BEFORE UPDATE ON "public"."regions" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'saved_simulations' AND trigger_name = 'trg_saved_simulations_updated') THEN
        CREATE TRIGGER "trg_saved_simulations_updated" BEFORE UPDATE ON "public"."saved_simulations" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'user_usage_limits' AND trigger_name = 'trg_user_usage_limits_updated') THEN
        CREATE TRIGGER "trg_user_usage_limits_updated" BEFORE UPDATE ON "public"."user_usage_limits" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'cost_benchmarks' AND trigger_name = 'trg_cost_benchmarks_updated') THEN
        CREATE TRIGGER "trg_cost_benchmarks_updated" BEFORE UPDATE ON "public"."cost_benchmarks" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'du_rate_schedules' AND trigger_name = 'trg_du_rate_schedules_updated') THEN
        CREATE TRIGGER "trg_du_rate_schedules_updated" BEFORE UPDATE ON "public"."du_rate_schedules" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'mcda_weights' AND trigger_name = 'trg_mcda_weights_updated') THEN
        CREATE TRIGGER "trg_mcda_weights_updated" BEFORE UPDATE ON "public"."mcda_weights" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'forecast_model_runs' AND trigger_name = 'trg_forecast_model_runs_updated') THEN
        CREATE TRIGGER "trg_forecast_model_runs_updated" BEFORE UPDATE ON "public"."forecast_model_runs" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'solar_suitability' AND trigger_name = 'trg_solar_suitability_updated') THEN
        CREATE TRIGGER "trg_solar_suitability_updated" BEFORE UPDATE ON "public"."solar_suitability" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'wind_suitability' AND trigger_name = 'trg_wind_suitability_updated') THEN
        CREATE TRIGGER "trg_wind_suitability_updated" BEFORE UPDATE ON "public"."wind_suitability" FOR EACH ROW EXECUTE FUNCTION "public"."set_updated_at"();
    END IF;
END $$;

-- SECTION 6: Materialized Views

CREATE MATERIALIZED VIEW IF NOT EXISTS "public"."mv_province_map_data" AS
SELECT p."province_id", p."name" AS province_name, p."region_id", r."name" AS region_name,
       p."psgc_code", p."lat", p."lon",
       COUNT(DISTINCT m."municipality_id") AS municipality_count,
       AVG(m."solar_suitability_score") AS avg_solar_score,
       AVG(m."wind_suitability_score") AS avg_wind_score,
       AVG(m."hydro_suitability_score") AS avg_hydro_score,
       AVG(m."geothermal_suitability_score") AS avg_geothermal_score,
       AVG(m."composite_suitability_score") AS avg_composite_score,
       MAX(m."suitability_updated_at") AS last_suitability_update
FROM "public"."provinces" p
LEFT JOIN "public"."regions" r ON p."region_id" = r."region_id"
LEFT JOIN "public"."municipalities" m ON p."province_id" = m."province_id"
GROUP BY p."province_id", p."name", p."region_id", r."name", p."psgc_code", p."lat", p."lon"
WITH DATA;
ALTER MATERIALIZED VIEW "public"."mv_province_map_data" OWNER TO "postgres";
CREATE UNIQUE INDEX IF NOT EXISTS "idx_mv_province_map_data_id" ON "public"."mv_province_map_data" ("province_id");

CREATE MATERIALIZED VIEW IF NOT EXISTS "public"."mv_municipality_map_data" AS
SELECT m."municipality_id", m."name" AS municipality_name, m."province_id",
       p."name" AS province_name, p."region_id", r."name" AS region_name,
       m."psgc_code", m."lat", m."lon",
       m."solar_suitability_score", m."solar_classification",
       m."wind_suitability_score", m."wind_classification",
       m."hydro_suitability_score", m."hydro_classification",
       m."geothermal_suitability_score", m."geothermal_classification",
       m."composite_suitability_score", m."composite_classification",
       m."suitability_updated_at"
FROM "public"."municipalities" m
JOIN "public"."provinces" p ON m."province_id" = p."province_id"
JOIN "public"."regions" r ON p."region_id" = r."region_id"
WITH DATA;
ALTER MATERIALIZED VIEW "public"."mv_municipality_map_data" OWNER TO "postgres";
CREATE UNIQUE INDEX IF NOT EXISTS "idx_mv_municipality_map_data_id" ON "public"."mv_municipality_map_data" ("municipality_id");

CREATE OR REPLACE FUNCTION "public"."refresh_map_views"() RETURNS void
LANGUAGE plpgsql AS $$ BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY "public"."mv_province_map_data";
    REFRESH MATERIALIZED VIEW CONCURRENTLY "public"."mv_municipality_map_data";
END; $$;
ALTER FUNCTION "public"."refresh_map_views"() OWNER TO "postgres";

-- SECTION 7: RLS Hardening

CREATE OR REPLACE FUNCTION "public"."is_admin"() RETURNS boolean
LANGUAGE sql SECURITY DEFINER AS $$
    SELECT EXISTS (SELECT 1 FROM "public"."user_roles" WHERE "user_id" = "auth"."uid"() AND "role" = 'admin');
$$;
ALTER FUNCTION "public"."is_admin"() OWNER TO "postgres";

ALTER TABLE "public"."cost_benchmarks" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."du_rate_schedules" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."mcda_weights" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."coverage_summary" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."data_lineage" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."forecast_model_runs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."solar_suitability" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."wind_suitability" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read on cost_benchmarks" ON "public"."cost_benchmarks" FOR SELECT USING (true);
CREATE POLICY "Public read on du_rate_schedules" ON "public"."du_rate_schedules" FOR SELECT USING (true);
CREATE POLICY "Public read on mcda_weights" ON "public"."mcda_weights" FOR SELECT USING (true);
CREATE POLICY "Public read on coverage_summary" ON "public"."coverage_summary" FOR SELECT USING (true);
CREATE POLICY "Public read on solar_suitability" ON "public"."solar_suitability" FOR SELECT USING (true);
CREATE POLICY "Public read on wind_suitability" ON "public"."wind_suitability" FOR SELECT USING (true);
CREATE POLICY "Admin write on cost_benchmarks" ON "public"."cost_benchmarks" FOR ALL USING ("public"."is_admin"()) WITH CHECK ("public"."is_admin"());
CREATE POLICY "Admin write on du_rate_schedules" ON "public"."du_rate_schedules" FOR ALL USING ("public"."is_admin"()) WITH CHECK ("public"."is_admin"());
CREATE POLICY "Admin write on mcda_weights" ON "public"."mcda_weights" FOR ALL USING ("public"."is_admin"()) WITH CHECK ("public"."is_admin"());
CREATE POLICY "Admin write on coverage_summary" ON "public"."coverage_summary" FOR ALL USING ("public"."is_admin"()) WITH CHECK ("public"."is_admin"());
CREATE POLICY "Service role all on data_lineage" ON "public"."data_lineage" FOR ALL USING ("auth"."role"() = 'service_role') WITH CHECK ("auth"."role"() = 'service_role');
CREATE POLICY "Service role all on forecast_model_runs" ON "public"."forecast_model_runs" FOR ALL USING ("auth"."role"() = 'service_role') WITH CHECK ("auth"."role"() = 'service_role');
CREATE POLICY "Admin write on solar_suitability" ON "public"."solar_suitability" FOR ALL USING ("public"."is_admin"()) WITH CHECK ("public"."is_admin"());
CREATE POLICY "Admin write on wind_suitability" ON "public"."wind_suitability" FOR ALL USING ("public"."is_admin"()) WITH CHECK ("public"."is_admin"());

-- Grants
GRANT SELECT ON "public"."cost_benchmarks" TO "anon","authenticated";
GRANT SELECT ON "public"."du_rate_schedules" TO "anon","authenticated";
GRANT SELECT ON "public"."mcda_weights" TO "anon","authenticated";
GRANT SELECT ON "public"."coverage_summary" TO "anon","authenticated";
GRANT SELECT ON "public"."solar_suitability" TO "anon","authenticated";
GRANT SELECT ON "public"."wind_suitability" TO "anon","authenticated";
GRANT SELECT ON "public"."mv_province_map_data" TO "anon","authenticated";
GRANT SELECT ON "public"."mv_municipality_map_data" TO "anon","authenticated";
GRANT ALL ON "public"."cost_benchmarks" TO "service_role";
GRANT ALL ON "public"."du_rate_schedules" TO "service_role";
GRANT ALL ON "public"."mcda_weights" TO "service_role";
GRANT ALL ON "public"."coverage_summary" TO "service_role";
GRANT ALL ON "public"."data_lineage" TO "service_role";
GRANT ALL ON "public"."forecast_model_runs" TO "service_role";
GRANT ALL ON "public"."solar_suitability" TO "service_role";
GRANT ALL ON "public"."wind_suitability" TO "service_role";
GRANT ALL ON "public"."mv_province_map_data" TO "service_role";
GRANT ALL ON "public"."mv_municipality_map_data" TO "service_role";
