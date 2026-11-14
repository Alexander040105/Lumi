-- Spec fields for the PH retailer product catalog refresh.
-- New columns carry brand/spec data scraped from solarwarehouse.ph,
-- solarportal.store, solarmallph.com.ph, prosolar.ph and RS Components PH.
ALTER TABLE public.products
    ADD COLUMN IF NOT EXISTS brand text,
    ADD COLUMN IF NOT EXISTS model_number text,
    ADD COLUMN IF NOT EXISTS short_description text,
    ADD COLUMN IF NOT EXISTS description text,
    ADD COLUMN IF NOT EXISTS specs jsonb,
    ADD COLUMN IF NOT EXISTS image_url text,
    ADD COLUMN IF NOT EXISTS price_type text DEFAULT 'fixed',
    ADD COLUMN IF NOT EXISTS wattage_w numeric,
    ADD COLUMN IF NOT EXISTS capacity_wh numeric,
    ADD COLUMN IF NOT EXISTS voltage_v numeric;

COMMENT ON COLUMN public.products.specs IS 'Vendor-native specification dict (jsonb), incl. dealer/wholesale price tiers where available.';
COMMENT ON COLUMN public.products.price_type IS 'fixed = listed PHP price; quote = price on request only.';

CREATE INDEX IF NOT EXISTS idx_products_subcategory
    ON public.products(energy_subcategory);
CREATE INDEX IF NOT EXISTS idx_products_source_site
    ON public.products(source_site);
