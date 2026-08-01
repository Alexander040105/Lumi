-- ============================================================================
-- Migration: 0006_add_forecast_module_tables.sql
-- Purpose: Add all tables needed by the forecasting module:
--          national_energy_annual, ml_model_registry, forecast_cache,
--          and forecast_model_runs.
-- Safe to re-run. Run in the Supabase SQL Editor or via `supabase db push`.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Helper: auto-update updated_at
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
-- 1. national_energy_annual
--    Stores DOE national-level historical energy statistics for ML training.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.national_energy_annual (
    year smallint PRIMARY KEY,

    -- Consumption by sector (GWh)
    total_consumption_gwh             decimal(12, 2),
    residential_consumption_gwh       decimal(12, 2),
    commercial_consumption_gwh        decimal(12, 2),
    industrial_consumption_gwh        decimal(12, 2),
    others_consumption_gwh            decimal(12, 2),
    electricity_sales_gwh             decimal(12, 2),
    utilities_own_use_gwh             decimal(12, 2),
    system_losses_gwh                 decimal(12, 2),

    -- Peak demand by grid (MW)
    luzon_peak_demand_mw              decimal(12, 2),
    visayas_peak_demand_mw            decimal(12, 2),
    mindanao_peak_demand_mw           decimal(12, 2),
    total_peak_demand_mw              decimal(12, 2),

    -- Generation by grid (GWh)
    luzon_generation_gwh              decimal(12, 2),
    visayas_generation_gwh            decimal(12, 2),
    mindanao_generation_gwh           decimal(12, 2),

    -- Generation by plant type (GWh)
    coal_generation_gwh               decimal(12, 2),
    oil_based_generation_gwh          decimal(12, 2),
    natural_gas_generation_gwh        decimal(12, 2),
    renewable_generation_gwh          decimal(12, 2),
    geothermal_generation_gwh         decimal(12, 2),
    hydro_generation_gwh              decimal(12, 2),
    biomass_generation_gwh            decimal(12, 2),
    solar_generation_gwh              decimal(12, 2),
    wind_generation_gwh               decimal(12, 2),

    -- Capacity (MW)
    total_installed_capacity_mw       decimal(12, 2),
    total_dependable_capacity_mw      decimal(12, 2),

    -- Metadata
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),

    CONSTRAINT valid_year CHECK (year >= 2000 AND year <= 2100),
    CONSTRAINT non_negative_consumption CHECK (total_consumption_gwh >= 0),
    CONSTRAINT non_negative_peak_demand CHECK (total_peak_demand_mw >= 0)
);

COMMENT ON TABLE public.national_energy_annual IS
    'Philippine national energy statistics (annual) extracted from DOE Power Statistics. Used as target variables for ML forecasting.';

CREATE INDEX IF NOT EXISTS idx_national_energy_year
    ON public.national_energy_annual(year);

ALTER TABLE public.national_energy_annual ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'national_energy_annual' AND policyname = 'Allow public read on national_energy_annual') THEN
        CREATE POLICY "Allow public read on national_energy_annual"
            ON public.national_energy_annual
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'national_energy_annual' AND policyname = 'Allow authenticated write on national_energy_annual') THEN
        CREATE POLICY "Allow authenticated write on national_energy_annual"
            ON public.national_energy_annual
            FOR ALL USING (auth.role() = 'authenticated');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'national_energy_annual' AND trigger_name = 'trg_national_energy_annual_updated') THEN
        CREATE TRIGGER trg_national_energy_annual_updated
            BEFORE UPDATE ON public.national_energy_annual
            FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
    END IF;
END $$;

GRANT ALL ON TABLE public.national_energy_annual TO anon, authenticated, service_role;

-- ----------------------------------------------------------------------------
-- 2. ml_model_registry
--    Tracks trained forecasting model versions, metrics, and active flag.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ml_model_registry (
    model_id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name      text NOT NULL,
    model_version   text NOT NULL,
    model_type      text NOT NULL CHECK (model_type IN ('SARIMA', 'LightGBM', 'XGBoost', 'Prophet')),
    target_variable text NOT NULL,
    train_date      date NOT NULL,
    metrics         jsonb,
    model_path      text,
    is_active       boolean DEFAULT false,
    created_at      timestamptz DEFAULT now(),
    updated_at      timestamptz DEFAULT now()
);

COMMENT ON TABLE public.ml_model_registry IS
    'Registry of trained forecasting models. Only one model per target_variable should be is_active=true at a time.';

CREATE UNIQUE INDEX IF NOT EXISTS idx_ml_model_active_unique
    ON public.ml_model_registry(target_variable, is_active)
    WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_ml_model_type_target
    ON public.ml_model_registry(model_type, target_variable, train_date DESC);

ALTER TABLE public.ml_model_registry ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'ml_model_registry' AND policyname = 'Allow public read on ml_model_registry') THEN
        CREATE POLICY "Allow public read on ml_model_registry"
            ON public.ml_model_registry
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'ml_model_registry' AND policyname = 'Allow authenticated write on ml_model_registry') THEN
        CREATE POLICY "Allow authenticated write on ml_model_registry"
            ON public.ml_model_registry
            FOR ALL USING (auth.role() = 'authenticated');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE event_object_table = 'ml_model_registry' AND trigger_name = 'trg_ml_model_registry_updated') THEN
        CREATE TRIGGER trg_ml_model_registry_updated
            BEFORE UPDATE ON public.ml_model_registry
            FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
    END IF;
END $$;

GRANT ALL ON TABLE public.ml_model_registry TO anon, authenticated, service_role;

-- ----------------------------------------------------------------------------
-- 3. forecast_cache
--    Stores previously computed forecasts to avoid re-computation.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.forecast_cache (
    forecast_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id          uuid NOT NULL REFERENCES public.ml_model_registry(model_id) ON DELETE CASCADE,
    target_variable   text NOT NULL,
    horizon_years     smallint NOT NULL CHECK (horizon_years > 0 AND horizon_years <= 10),
    forecast_year     smallint NOT NULL,
    forecast_month    smallint CHECK (forecast_month IS NULL OR (forecast_month >= 1 AND forecast_month <= 12)),
    predicted_value   decimal(14, 4) NOT NULL,
    lower_bound       decimal(14, 4),
    upper_bound       decimal(14, 4),
    created_at        timestamptz DEFAULT now()
);

COMMENT ON TABLE public.forecast_cache IS
    'Cached forecast results per model, target, and horizon. TTL managed by application logic (e.g., 24h).';

CREATE INDEX IF NOT EXISTS idx_forecast_cache_lookup
    ON public.forecast_cache(target_variable, forecast_year, forecast_month);

CREATE INDEX IF NOT EXISTS idx_forecast_cache_model
    ON public.forecast_cache(model_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_forecast_cache_created
    ON public.forecast_cache(created_at DESC);

ALTER TABLE public.forecast_cache ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'forecast_cache' AND policyname = 'Allow authenticated read on forecast_cache') THEN
        CREATE POLICY "Allow authenticated read on forecast_cache"
            ON public.forecast_cache
            FOR SELECT USING (auth.role() = 'authenticated');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'forecast_cache' AND policyname = 'Allow authenticated write on forecast_cache') THEN
        CREATE POLICY "Allow authenticated write on forecast_cache"
            ON public.forecast_cache
            FOR ALL USING (auth.role() = 'authenticated');
    END IF;
END $$;

GRANT ALL ON TABLE public.forecast_cache TO anon, authenticated, service_role;

-- ----------------------------------------------------------------------------
-- 4. forecast_model_runs
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

CREATE INDEX IF NOT EXISTS idx_forecast_model_runs_model
    ON public.forecast_model_runs (model_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_forecast_model_runs_target
    ON public.forecast_model_runs (target_variable, started_at DESC);

-- Foreign key to ml_model_registry (only if the table already exists)
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

GRANT ALL ON TABLE public.forecast_model_runs TO service_role;
