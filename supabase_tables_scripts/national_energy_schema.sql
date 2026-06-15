-- ============================================================
-- LUMI ML Forecasting Module — National Energy Schema
-- Run this in Supabase SQL Editor
-- ============================================================

-- --------------------------------------------------------
-- 1. national_energy_annual
--    Stores DOE Power Statistics (2003–2024) for ML training
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.national_energy_annual (
    year smallint PRIMARY KEY,

    -- Consumption by sector (GWh)
    total_consumption_gwh             decimal(12, 2),
    residential_consumption_gwh       decimal(12, 2),
    commercial_consumption_gwh        decimal(12, 2),
    industrial_consumption_gwh        decimal(12, 2),
    others_consumption_gwh            decimal(12, 2),
    electricity_sales_gwh           decimal(12, 2),
    utilities_own_use_gwh           decimal(12, 2),
    system_losses_gwh               decimal(12, 2),

    -- Peak demand by grid (MW)
    luzon_peak_demand_mw              decimal(12, 2),
    visayas_peak_demand_mw            decimal(12, 2),
    mindanao_peak_demand_mw           decimal(12, 2),
    total_peak_demand_mw              decimal(12, 2),

    -- Generation by grid (GWh)
    luzon_generation_gwh              decimal(12, 2),
    visayas_generation_gwh            decimal(12, 2),
    mindanao_generation_gwh         decimal(12, 2),

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

    -- Constraints
    CONSTRAINT valid_year CHECK (year >= 2000 AND year <= 2100),
    CONSTRAINT non_negative_consumption CHECK (total_consumption_gwh >= 0),
    CONSTRAINT non_negative_peak_demand CHECK (total_peak_demand_mw >= 0)
);

-- Comments for documentation
COMMENT ON TABLE public.national_energy_annual IS
    'Philippine national energy statistics (annual) extracted from DOE Power Statistics. Used as target variables for ML forecasting.';

COMMENT ON COLUMN public.national_energy_annual.total_consumption_gwh IS
    'Total electricity consumption including system losses and utilities own use';
COMMENT ON COLUMN public.national_energy_annual.total_peak_demand_mw IS
    'Total non-coincident peak demand across Luzon, Visayas, and Mindanao grids';
COMMENT ON COLUMN public.national_energy_annual.renewable_generation_gwh IS
    'Combined RE generation: geothermal + hydro + biomass + solar + wind';

-- Index: primary key already indexed; add index on year for range queries
CREATE INDEX IF NOT EXISTS idx_national_energy_year
    ON public.national_energy_annual(year);

-- --------------------------------------------------------
-- 2. ml_model_registry
--    Tracks trained model versions, metrics, and active flag
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ml_model_registry (
    model_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name        text NOT NULL,
    model_version     text NOT NULL,
    model_type        text NOT NULL CHECK (model_type IN ('SARIMA', 'ARIMA', 'LinearTrend', 'HoltWinters', 'RandomForest', 'LightGBM', 'XGBoost', 'Prophet')),
    target_variable   text NOT NULL,  -- e.g. 'total_consumption_gwh', 'total_peak_demand_mw'
    train_date        date NOT NULL,
    metrics           jsonb,           -- {'mape': 5.2, 'rmse': 1234.5, 'mae': 890.1}
    model_path        text,            -- relative path to serialized model file
    is_active         boolean DEFAULT false,
    created_at        timestamptz DEFAULT now(),
    updated_at        timestamptz DEFAULT now()
);

COMMENT ON TABLE public.ml_model_registry IS
    'Registry of trained forecasting models. Only one model per target_variable should be is_active=true at a time.';

-- Composite index for fetching the active model quickly
CREATE UNIQUE INDEX IF NOT EXISTS idx_ml_model_active_unique
    ON public.ml_model_registry(target_variable, is_active)
    WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_ml_model_type_target
    ON public.ml_model_registry(model_type, target_variable, train_date DESC);

-- --------------------------------------------------------
-- 3. forecast_cache
--    Stores previously computed forecasts to avoid re-computation
-- --------------------------------------------------------
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

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_forecast_cache_lookup
    ON public.forecast_cache(target_variable, forecast_year, forecast_month);

CREATE INDEX IF NOT EXISTS idx_forecast_cache_model
    ON public.forecast_cache(model_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_forecast_cache_created
    ON public.forecast_cache(created_at DESC);

-- --------------------------------------------------------
-- 4. Row-Level Security Policies
-- --------------------------------------------------------

-- Enable RLS on all tables
ALTER TABLE public.national_energy_annual ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ml_model_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.forecast_cache ENABLE ROW LEVEL SECURITY;

-- national_energy_annual: public read, admin write
CREATE POLICY "Allow public read on national_energy_annual"
    ON public.national_energy_annual
    FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on national_energy_annual"
    ON public.national_energy_annual
    FOR ALL USING (auth.role() = 'authenticated');

-- ml_model_registry: public read (users see all models), admin write
CREATE POLICY "Allow public read on ml_model_registry"
    ON public.ml_model_registry
    FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write on ml_model_registry"
    ON public.ml_model_registry
    FOR ALL USING (auth.role() = 'authenticated');

-- forecast_cache: authenticated read (users see forecasts), admin/system write
CREATE POLICY "Allow authenticated read on forecast_cache"
    ON public.forecast_cache
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated write on forecast_cache"
    ON public.forecast_cache
    FOR ALL USING (auth.role() = 'authenticated');

-- --------------------------------------------------------
-- 5. Auto-update updated_at trigger
-- --------------------------------------------------------
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_national_energy_annual_updated
    BEFORE UPDATE ON public.national_energy_annual
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_ml_model_registry_updated
    BEFORE UPDATE ON public.ml_model_registry
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
