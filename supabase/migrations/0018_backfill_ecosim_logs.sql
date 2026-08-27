-- Migration 0018: Backfill user_ecosim_logs from existing saved_simulations.
-- Each saved simulation required an EcoSim calculation, so we treat the
-- saved row as an EcoSim request at the same timestamp. New calculations
-- from this point forward are logged by the FastAPI backend.

INSERT INTO public.user_ecosim_logs (user_id, municipality_id, created_at)
SELECT s.user_id, s.municipality_id, s.created_at
FROM public.saved_simulations s
WHERE NOT EXISTS (
    SELECT 1 FROM public.user_ecosim_logs e
    WHERE e.user_id = s.user_id
      AND e.municipality_id = s.municipality_id
      AND e.created_at = s.created_at
);
