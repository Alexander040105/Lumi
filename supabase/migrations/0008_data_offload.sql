-- ============================================================
-- LUMI Data Offload Migration
-- Stores local CSV/GeoJSON datasets in Supabase so the backend
-- can run without reading files from disk.
-- Run this in the Supabase SQL Editor before deploying.
-- ============================================================

-- Generic DOE dataset store.  Each row holds the full parsed contents
-- of one CSV as a JSONB array of objects.  This keeps the migration
-- small and robust against future column changes while still letting
-- the backend reconstruct a pandas DataFrame.
CREATE TABLE IF NOT EXISTS public.doe_datasets (
    dataset_name text PRIMARY KEY,
    row_count integer NOT NULL DEFAULT 0,
    data jsonb NOT NULL DEFAULT '[]'::jsonb,
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE public.doe_datasets IS
    'Stores DOE CSV files as JSONB arrays.  The backend loads a dataset by name and converts it to a DataFrame.';

CREATE INDEX IF NOT EXISTS idx_doe_datasets_name
    ON public.doe_datasets(dataset_name);

-- Municipality climate averages (module-level loaded by ecosim.py)
CREATE TABLE IF NOT EXISTS public.municipality_climate_averages (
    municipality_id integer PRIMARY KEY,
    avg_t2m double precision,
    avg_t2m_max double precision,
    avg_t2m_min double precision,
    avg_rh2m double precision,
    avg_rhoa double precision,
    avg_prectotcorr double precision,
    avg_ws10m double precision,
    avg_allsky_sfc_sw_dwn double precision,
    avg_cloud_amt double precision,
    avg_surface_pressure double precision,
    elevation integer,
    updated_at timestamptz DEFAULT now(),
    CONSTRAINT municipality_climate_averages_municipality_id_fkey
        FOREIGN KEY (municipality_id) REFERENCES public.municipalities(municipality_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE public.municipality_climate_averages IS
    'Pre-computed NASA POWER climate averages per municipality (used by EcoSim).';

CREATE INDEX IF NOT EXISTS idx_municipality_climate_averages_municipality_id
    ON public.municipality_climate_averages(municipality_id);

-- Renewable energy product catalogue (loaded by products.py)
CREATE TABLE IF NOT EXISTS public.products (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    product_name text,
    product_name_raw text,
    product_name_normalized text,
    price_raw text,
    price_value decimal(14, 4),
    currency text,
    energy_category text,
    energy_subcategory text,
    source_site text,
    source_file text,
    url text,
    ratings text,
    reviews text,
    price_note text,
    rejection_reason text,
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE public.products IS
    'Cleaned renewable energy product catalogue used by the product recommendation service.';

CREATE INDEX IF NOT EXISTS idx_products_category
    ON public.products(energy_category);
CREATE INDEX IF NOT EXISTS idx_products_normalized
    ON public.products(product_name_normalized);

-- Individual wind product rows for summary calculation
CREATE TABLE IF NOT EXISTS public.wind_products (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    source_file text,
    source_site text,
    name text,
    price text,
    ratings text,
    reviews text,
    url text,
    power_w decimal(14, 4),
    diameter_m decimal(14, 4),
    rotor_radius_m decimal(14, 4),
    wind_speed_mps decimal(14, 4),
    power_coefficient decimal(14, 4),
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE public.wind_products IS
    'Parsed wind turbine product data used to compute average rotor radius and power coefficient.';

CREATE INDEX IF NOT EXISTS idx_wind_products_rotor
    ON public.wind_products(rotor_radius_m) WHERE rotor_radius_m IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_wind_products_cp
    ON public.wind_products(power_coefficient) WHERE power_coefficient IS NOT NULL;

-- Pre-computed wind summary for the output calculator
CREATE TABLE IF NOT EXISTS public.wind_products_summary (
    variant text PRIMARY KEY,
    avg_rotor_radius_m double precision,
    avg_power_coefficient double precision,
    rotor_count integer,
    cp_count integer,
    summary_rotor text,
    summary_cp text,
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE public.wind_products_summary IS
    'Pre-computed summary statistics from wind_products used by wind_output_calc.py.';

-- Geothermal heat flow measurements
CREATE TABLE IF NOT EXISTS public.geothermal_heatflow (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    lat double precision,
    lon double precision,
    heat_flow_mw_m2 double precision,
    elevation double precision,
    environment text,
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE public.geothermal_heatflow IS
    'IHFC heat flow measurements used for geothermal suitability scoring.';

CREATE INDEX IF NOT EXISTS idx_geothermal_heatflow_lat_lon
    ON public.geothermal_heatflow(lat, lon);

-- Geothermal fault line markers
CREATE TABLE IF NOT EXISTS public.geothermal_faults (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name text,
    lat double precision,
    lon double precision,
    length_km double precision,
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE public.geothermal_faults IS
    'PHIVOLCS active fault markers used for geothermal distance/density scoring.';

CREATE INDEX IF NOT EXISTS idx_geothermal_faults_lat_lon
    ON public.geothermal_faults(lat, lon);

-- Volcano markers
CREATE TABLE IF NOT EXISTS public.geothermal_volcanoes (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name text,
    lat double precision,
    lon double precision,
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE public.geothermal_volcanoes IS
    'Smithsonian volcano dataset used for geothermal proximity scoring.';

CREATE INDEX IF NOT EXISTS idx_geothermal_volcanoes_lat_lon
    ON public.geothermal_volcanoes(lat, lon);

-- Extend existing geothermal_suitability to hold precomputed aquifer values
ALTER TABLE public.geothermal_suitability
    ADD COLUMN IF NOT EXISTS aquifer_score double precision,
    ADD COLUMN IF NOT EXISTS aquifer_porosity double precision,
    ADD COLUMN IF NOT EXISTS aquifer_permeability_log10 double precision,
    ADD COLUMN IF NOT EXISTS aquifer_thickness_m double precision,
    ADD COLUMN IF NOT EXISTS aquifer_depth_m double precision,
    ADD COLUMN IF NOT EXISTS aquifer_basin_name text,
    ADD COLUMN IF NOT EXISTS aquifer_fallback boolean,
    ADD COLUMN IF NOT EXISTS aquifer_distance_km double precision,
    ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now();

CREATE INDEX IF NOT EXISTS idx_geothermal_suitability_aquifer
    ON public.geothermal_suitability(municipality_id, aquifer_score);

-- Map Supabase province names to GeoJSON adm2_en names (Option A from the plan)
ALTER TABLE public.provinces
    ADD COLUMN IF NOT EXISTS geojson_name text;

CREATE INDEX IF NOT EXISTS idx_provinces_geojson_name
    ON public.provinces(geojson_name);

-- Create a public storage bucket for GeoJSON geometry files.
-- The backend only reads province names from the DB; the frontend can
-- fetch the actual geometry from this bucket.
INSERT INTO storage.buckets (id, name, public)
VALUES ('geojsons', 'geojsons', true)
ON CONFLICT (id) DO NOTHING;

-- Public read policy for the geojsons bucket.
DROP POLICY IF EXISTS "Public read on geojsons bucket" ON storage.objects;
CREATE POLICY "Public read on geojsons bucket"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'geojsons');

-- Row Level Security
ALTER TABLE public.doe_datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.municipality_climate_averages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wind_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wind_products_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.geothermal_heatflow ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.geothermal_faults ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.geothermal_volcanoes ENABLE ROW LEVEL SECURITY;

-- Public read for all data tables (data is reference/open)
DROP POLICY IF EXISTS "Allow public read on doe_datasets" ON public.doe_datasets;
CREATE POLICY "Allow public read on doe_datasets"
    ON public.doe_datasets FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read on municipality_climate_averages" ON public.municipality_climate_averages;
CREATE POLICY "Allow public read on municipality_climate_averages"
    ON public.municipality_climate_averages FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read on products" ON public.products;
CREATE POLICY "Allow public read on products"
    ON public.products FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read on wind_products" ON public.wind_products;
CREATE POLICY "Allow public read on wind_products"
    ON public.wind_products FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read on wind_products_summary" ON public.wind_products_summary;
CREATE POLICY "Allow public read on wind_products_summary"
    ON public.wind_products_summary FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read on geothermal_heatflow" ON public.geothermal_heatflow;
CREATE POLICY "Allow public read on geothermal_heatflow"
    ON public.geothermal_heatflow FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read on geothermal_faults" ON public.geothermal_faults;
CREATE POLICY "Allow public read on geothermal_faults"
    ON public.geothermal_faults FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read on geothermal_volcanoes" ON public.geothermal_volcanoes;
CREATE POLICY "Allow public read on geothermal_volcanoes"
    ON public.geothermal_volcanoes FOR SELECT USING (true);

-- Authenticated write (migration scripts, backend updates)
DROP POLICY IF EXISTS "Allow authenticated write on doe_datasets" ON public.doe_datasets;
CREATE POLICY "Allow authenticated write on doe_datasets"
    ON public.doe_datasets FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow authenticated write on municipality_climate_averages" ON public.municipality_climate_averages;
CREATE POLICY "Allow authenticated write on municipality_climate_averages"
    ON public.municipality_climate_averages FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow authenticated write on products" ON public.products;
CREATE POLICY "Allow authenticated write on products"
    ON public.products FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow authenticated write on wind_products" ON public.wind_products;
CREATE POLICY "Allow authenticated write on wind_products"
    ON public.wind_products FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow authenticated write on wind_products_summary" ON public.wind_products_summary;
CREATE POLICY "Allow authenticated write on wind_products_summary"
    ON public.wind_products_summary FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow authenticated write on geothermal_heatflow" ON public.geothermal_heatflow;
CREATE POLICY "Allow authenticated write on geothermal_heatflow"
    ON public.geothermal_heatflow FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow authenticated write on geothermal_faults" ON public.geothermal_faults;
CREATE POLICY "Allow authenticated write on geothermal_faults"
    ON public.geothermal_faults FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow authenticated write on geothermal_volcanoes" ON public.geothermal_volcanoes;
CREATE POLICY "Allow authenticated write on geothermal_volcanoes"
    ON public.geothermal_volcanoes FOR ALL USING (auth.role() = 'authenticated');
