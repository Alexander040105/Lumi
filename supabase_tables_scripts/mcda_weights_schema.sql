-- ============================================================
-- MCDA Weights configuration table for LUMI
-- Stores AHP-derived criterion weights per renewable energy type.
-- Run this in the Supabase SQL Editor.
-- ============================================================

CREATE TABLE IF NOT EXISTS "public"."mcda_weights" (
    "id" serial PRIMARY KEY,
    "energy_type" text NOT NULL,          -- 'geothermal', 'solar', 'wind', 'hydro'
    "criterion" text NOT NULL,              -- e.g. 'heat_flow', 'fault', 'volcano'
    "weight" double precision NOT NULL,     -- 0.0 - 1.0
    "version" integer NOT NULL DEFAULT 1,   -- versioning for AHP revision history
    "is_active" boolean NOT NULL DEFAULT true,
    "updated_at" timestamp with time zone DEFAULT now()
);

-- Unique constraint: only one active weight per criterion per energy type
CREATE UNIQUE INDEX IF NOT EXISTS "idx_mcda_weights_active"
    ON "public"."mcda_weights" ("energy_type", "criterion")
    WHERE "is_active" = true;

COMMENT ON TABLE "public"."mcda_weights" IS 'AHP-derived MCDA criterion weights for renewable energy suitability scoring. Manage via admin panel or SQL.';

-- Grants
GRANT ALL ON TABLE "public"."mcda_weights" TO "anon";
GRANT ALL ON TABLE "public"."mcda_weights" TO "authenticated";
GRANT ALL ON TABLE "public"."mcda_weights" TO "service_role";

-- ============================================================
-- Default geothermal weights (AHP-calculated)
-- heat_flow=0.30, fault=0.15, volcano=0.10, aquifer=0.15, temperature=0.10
-- Remaining 0.20 reserved for plant_proximity boost (applied separately)
-- ============================================================

INSERT INTO "public"."mcda_weights" ("energy_type", "criterion", "weight", "version")
VALUES
    ('geothermal', 'heat_flow', 0.30, 1),
    ('geothermal', 'fault', 0.15, 1),
    ('geothermal', 'volcano', 0.10, 1),
    ('geothermal', 'aquifer', 0.15, 1),
    ('geothermal', 'temperature', 0.10, 1)
ON CONFLICT DO NOTHING;
