-- ============================================================================
-- Migration: 0005_add_forecast_model_runs.sql
-- Purpose: Create the forecast_model_runs table used by the forecasting module.
-- Run this in the Supabase SQL Editor or via `supabase db push`.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Helper: auto-update updated_at (safe to re-run)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.set_updated_at()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

ALTER FUNCTION public.set_updated_at() OWNER TO postgres;

-- ----------------------------------------------------------------------------
-- 1. forecast_model_runs
--    Logs every train/backtest/retrain/evaluation run.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.forecast_model_runs (
    id              uuid DEFAULT gen_random_uuid() NOT NULL,
    model_id        uuid,
    run_type        text NOT NULL DEFAULT 'train',
    target_variable text NOT NULL,
    hyperparameters jsonb,
    metrics         jsonb,
    artifact_path   text,
    started_at      timestamptz NOT NULL,
    finished_at     timestamptz,
    status          text NOT NULL DEFAULT 'running',
    created_at      timestamptz DEFAULT now() NOT NULL,
    updated_at      timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT forecast_model_runs_pkey PRIMARY KEY (id),
    CONSTRAINT forecast_model_runs_status_check CHECK (status IN ('running','success','failed','cancelled')),
    CONSTRAINT forecast_model_runs_run_type_check CHECK (run_type IN ('train','backtest','retrain','evaluate'))
);

ALTER TABLE public.forecast_model_runs OWNER TO postgres;

COMMENT ON TABLE public.forecast_model_runs IS
    'Log of forecasting model training and backtest runs.';

-- ----------------------------------------------------------------------------
-- 2. Indexes
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_forecast_model_runs_model
    ON public.forecast_model_runs (model_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_forecast_model_runs_target
    ON public.forecast_model_runs (target_variable, started_at DESC);

-- ----------------------------------------------------------------------------
-- 3. Foreign key to ml_model_registry (only if the table already exists)
-- ----------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'ml_model_registry'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'forecast_model_runs_model_id_fkey'
    ) THEN
        ALTER TABLE public.forecast_model_runs
            ADD CONSTRAINT forecast_model_runs_model_id_fkey
            FOREIGN KEY (model_id) REFERENCES public.ml_model_registry(model_id)
            ON DELETE SET NULL;
    END IF;
END $$;

-- ----------------------------------------------------------------------------
-- 4. updated_at trigger
-- ----------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers
        WHERE event_object_table = 'forecast_model_runs'
          AND trigger_name = 'trg_forecast_model_runs_updated'
    ) THEN
        CREATE TRIGGER trg_forecast_model_runs_updated
            BEFORE UPDATE ON public.forecast_model_runs
            FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
    END IF;
END $$;

-- ----------------------------------------------------------------------------
-- 5. Row Level Security
-- ----------------------------------------------------------------------------
ALTER TABLE public.forecast_model_runs ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'forecast_model_runs'
          AND policyname = 'Service role all on forecast_model_runs'
    ) THEN
        CREATE POLICY "Service role all on forecast_model_runs"
            ON public.forecast_model_runs
            FOR ALL
            USING (auth.role() = 'service_role')
            WITH CHECK (auth.role() = 'service_role');
    END IF;
END $$;

-- ----------------------------------------------------------------------------
-- 6. Grants
-- ----------------------------------------------------------------------------
GRANT ALL ON TABLE public.forecast_model_runs TO service_role;
