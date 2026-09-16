-- Migration 0023: Add ecosim_autosave preference to profiles.
-- When true (default), each EcoSim run is saved to the user's account automatically.

ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS ecosim_autosave boolean NOT NULL DEFAULT true;
