-- Clear old AI cache so the new prompts, token limits, and cleanup logic take effect.
-- This removes potentially truncated or malformed insights; they will be regenerated on demand.

TRUNCATE TABLE public.chart_ai_insights;
TRUNCATE TABLE public.ecosim_ai_cache;
