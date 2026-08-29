-- Migration 0021: Add province_id and mode to saved_simulations
-- so province-level simulations can be saved without a municipality FK.

ALTER TABLE public.saved_simulations
  ADD COLUMN IF NOT EXISTS province_id int;

ALTER TABLE public.saved_simulations
  ADD COLUMN IF NOT EXISTS mode text NOT NULL DEFAULT 'municipality';

ALTER TABLE public.saved_simulations
  DROP CONSTRAINT IF EXISTS saved_simulations_province_id_fkey;

ALTER TABLE public.saved_simulations
  ADD CONSTRAINT saved_simulations_province_id_fkey
    FOREIGN KEY (province_id) REFERENCES public.provinces(province_id)
    ON UPDATE CASCADE ON DELETE SET NULL;
