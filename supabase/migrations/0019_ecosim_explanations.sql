-- Migration 0019: Cache per-municipality EcoSim renewable-source explanations
-- so the backend never calls the AI just to show the "Why this estimate
-- looks this way" cards.

CREATE TABLE IF NOT EXISTS public.municipality_renewable_explanations (
    municipality_id integer PRIMARY KEY
        REFERENCES public.municipalities(municipality_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    solar text,
    wind text,
    hydro text,
    geothermal text,
    updated_at timestamp with time zone DEFAULT now()
);

ALTER TABLE public.municipality_renewable_explanations ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE public.municipality_renewable_explanations IS
    'Cached, deterministic fallback explanations for EcoSim renewable-source cards.';

-- Everyone can read the cached explanations; only the service role writes.
CREATE POLICY "municipality_renewable_explanations_select_public"
  ON public.municipality_renewable_explanations
  FOR SELECT TO authenticated, anon
  USING (true);

GRANT ALL ON TABLE public.municipality_renewable_explanations TO service_role;
GRANT SELECT ON TABLE public.municipality_renewable_explanations TO authenticated;
GRANT SELECT ON TABLE public.municipality_renewable_explanations TO anon;
