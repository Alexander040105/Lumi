-- =============================================================================
-- LUMI ml_model_registry Extension Script
-- =============================================================================
-- Purpose: Add individual metric columns to the existing ml_model_registry table
--          for queryability, indexing, and ORM compatibility.
--
-- Prerequisites: Table public.ml_model_registry already exists (confirmed in
--              live Supabase instance).
--
-- Safety: All ALTER statements use IF NOT EXISTS. All UPDATE statements are
--         idempotent (can be re-run safely).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. ALTER TABLE — Add individual metric columns
-- ---------------------------------------------------------------------------

ALTER TABLE public.ml_model_registry
    ADD COLUMN IF NOT EXISTS mae double precision,
    ADD COLUMN IF NOT EXISTS rmse double precision,
    ADD COLUMN IF NOT EXISTS mape double precision,
    ADD COLUMN IF NOT EXISTS r2 double precision,
    ADD COLUMN IF NOT EXISTS mpe double precision,
    ADD COLUMN IF NOT EXISTS aic double precision,
    ADD COLUMN IF NOT EXISTS bic double precision,
    ADD COLUMN IF NOT EXISTS directional_accuracy double precision,
    ADD COLUMN IF NOT EXISTS picp double precision,
    ADD COLUMN IF NOT EXISTS train_time_sec double precision,
    ADD COLUMN IF NOT EXISTS infer_time_ms double precision,
    ADD COLUMN IF NOT EXISTS n_train integer,
    ADD COLUMN IF NOT EXISTS n_test integer,
    ADD COLUMN IF NOT EXISTS test_period text,
    ADD COLUMN IF NOT EXISTS train_period text;

-- ---------------------------------------------------------------------------
-- 2. CREATE INDEX — For fast leaderboard and ranking queries
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ml_model_mape
    ON public.ml_model_registry USING btree (target_variable, mape);

CREATE INDEX IF NOT EXISTS idx_ml_model_mae
    ON public.ml_model_registry USING btree (target_variable, mae);

CREATE INDEX IF NOT EXISTS idx_ml_model_train_date
    ON public.ml_model_registry USING btree (target_variable, train_date DESC);

-- ---------------------------------------------------------------------------
-- 3. UPDATE existing rows — Extract values from JSONB metrics into columns
-- ---------------------------------------------------------------------------
-- These updates populate the new columns for all 7 existing records
-- (6 consumption models + 1 peak demand model).

UPDATE public.ml_model_registry
SET
    mae  = COALESCE((metrics->>'mae')::double precision, mae),
    rmse = COALESCE((metrics->>'rmse')::double precision, rmse),
    mape = COALESCE((metrics->>'mape')::double precision, mape),
    n_train = COALESCE((metrics->>'n_train')::integer, n_train),
    n_test  = COALESCE((metrics->>'n_test')::integer, n_test),
    test_period  = COALESCE(metrics->>'test_period', test_period),
    train_period = COALESCE(metrics->>'train_period', train_period)
WHERE metrics IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 4. Update model_type check constraint — ensure it covers all model types
-- ---------------------------------------------------------------------------
-- The existing CHECK constraint only allows: SARIMA, LightGBM, XGBoost, Prophet.
-- This is sufficient for the current registry taxonomy.

-- ---------------------------------------------------------------------------
-- 5. Verify the migration
-- ---------------------------------------------------------------------------

SELECT
    model_name,
    target_variable,
    model_type,
    mae,
    rmse,
    mape,
    r2,
    mpe,
    aic,
    bic,
    directional_accuracy,
    picp,
    train_time_sec,
    infer_time_ms,
    is_active
FROM public.ml_model_registry
ORDER BY target_variable, mape;

-- ---------------------------------------------------------------------------
-- 6. Notes for thesis documentation
-- ---------------------------------------------------------------------------
-- JSONB (metrics) is retained for unstructured / extensible metadata.
-- Individual columns enable:
--   - Fast ORDER BY queries for dashboard leaderboards
--   - Direct indexing for performance
--   - Clear schema documentation for thesis readers
--   - ORM auto-mapping without JSONB parsing
--
-- When inserting NEW models from the DOE_model_registry notebook:
--   1. Populate BOTH the JSONB metrics blob AND the individual columns.
--   2. The JSONB blob serves as an audit trail / full snapshot.
--   3. The individual columns serve as the query-optimized "hot path."
-- =============================================================================
