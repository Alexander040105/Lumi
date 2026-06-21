-- ============================================================
-- Geothermal tables for LUMI
-- Run this in the Supabase SQL Editor before deploying
-- the geothermal backend integration.
-- ============================================================

-- 1. Geothermal suitability scores per municipality
--    (pre-computed from heat flow, fault, volcano, aquifer data)
CREATE TABLE IF NOT EXISTS "public"."geothermal_suitability" (
    "municipality_id" integer NOT NULL,
    "heat_flow_score" double precision,
    "fault_density" double precision,
    "fault_distance_km" double precision,
    "volcano_distance_km" double precision,
    "aquifer_score" double precision,
    "temperature_score" double precision,
    "geothermal_score" double precision,
    "geothermal_score_mcda" double precision,
    "classification" text,
    CONSTRAINT "geothermal_suitability_pkey" PRIMARY KEY ("municipality_id"),
    CONSTRAINT "geothermal_suitability_municipality_id_fkey"
        FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
        ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE "public"."geothermal_suitability" IS 'Pre-computed geothermal suitability metrics per municipality derived from IHFC heat flow, PHIVOLCS fault data, Smithsonian volcano data, and Zenodo aquifer properties.';
COMMENT ON COLUMN "public"."geothermal_suitability"."heat_flow_score" IS 'Normalized IHFC heat flow score (0-1), range 40-120 mW/m².';
COMMENT ON COLUMN "public"."geothermal_suitability"."fault_density" IS 'Fault length (km) / municipality area (km²).';
COMMENT ON COLUMN "public"."geothermal_suitability"."fault_distance_km" IS 'Haversine distance to nearest active fault (km).';
COMMENT ON COLUMN "public"."geothermal_suitability"."volcano_distance_km" IS 'Haversine distance to nearest volcano (km).';
COMMENT ON COLUMN "public"."geothermal_suitability"."aquifer_score" IS 'Composite aquifer suitability (0-1) from permeability, porosity, and thickness.';
COMMENT ON COLUMN "public"."geothermal_suitability"."temperature_score" IS 'Surface temperature anomaly score from NASA POWER (0-1).';
COMMENT ON COLUMN "public"."geothermal_suitability"."geothermal_score" IS 'Overall weighted geothermal suitability (0-1).';
COMMENT ON COLUMN "public"."geothermal_suitability"."geothermal_score_mcda" IS 'AHP-based MCDA geothermal suitability score (0-1) using distance-decay fault/volcano proximity.';
COMMENT ON COLUMN "public"."geothermal_suitability"."classification" IS 'Categorical class: Low, Moderate, Good, High.';

-- 2. Geothermal energy output estimates per municipality
--    (pre-computed from physics-based thermal power model)
CREATE TABLE IF NOT EXISTS "public"."geothermal_output" (
    "municipality_id" integer NOT NULL,
    "reservoir_temperature_c" double precision,
    "estimated_flow_rate_kg_s" double precision,
    "thermal_power_mw" double precision,
    "electric_power_mw" double precision,
    "annual_energy_gwh" double precision,
    "confidence_score" double precision,
    "source" text,
    "assumption" text,
    CONSTRAINT "geothermal_output_pkey" PRIMARY KEY ("municipality_id"),
    CONSTRAINT "geothermal_output_municipality_id_fkey"
        FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
        ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE "public"."geothermal_output" IS 'Pre-computed geothermal energy output per municipality using physics-based reservoir temperature and thermal power estimates.';
COMMENT ON COLUMN "public"."geothermal_output"."reservoir_temperature_c" IS 'Estimated reservoir temperature using Ts + (G × Depth) where Depth=2000m default.';
COMMENT ON COLUMN "public"."geothermal_output"."estimated_flow_rate_kg_s" IS 'Inferred flow rate from aquifer permeability when direct measurement is unavailable.';
COMMENT ON COLUMN "public"."geothermal_output"."thermal_power_mw" IS 'Q = m · Cp · ΔT in MW.';
COMMENT ON COLUMN "public"."geothermal_output"."electric_power_mw" IS 'P = Q × efficiency (binary 0.12 or flash 0.15).';
COMMENT ON COLUMN "public"."geothermal_output"."annual_energy_gwh" IS 'Annual electric energy estimate (GWh/year).';
COMMENT ON COLUMN "public"."geothermal_output"."confidence_score" IS 'Data availability confidence (0-1).';
COMMENT ON COLUMN "public"."geothermal_output"."source" IS 'Data provenance: IHFC, NASA POWER, PHIVOLCS, Smithsonian, Zenodo.';
COMMENT ON COLUMN "public"."geothermal_output"."assumption" IS 'Key assumptions for transparency, e.g., reservoir depth default.';

-- Indexes for fast API lookups
CREATE INDEX IF NOT EXISTS "idx_geothermal_suitability_municipality_id"
    ON "public"."geothermal_suitability" USING btree ("municipality_id");

CREATE INDEX IF NOT EXISTS "idx_geothermal_output_municipality_id"
    ON "public"."geothermal_output" USING btree ("municipality_id");

-- Grants (match existing lumischema.sql pattern)
GRANT ALL ON TABLE "public"."geothermal_suitability" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_suitability" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_suitability" TO "service_role";

GRANT ALL ON TABLE "public"."geothermal_output" TO "anon";
GRANT ALL ON TABLE "public"."geothermal_output" TO "authenticated";
GRANT ALL ON TABLE "public"."geothermal_output" TO "service_role";
