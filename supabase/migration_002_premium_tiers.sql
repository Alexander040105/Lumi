-- Migration: Premium Tier Quota System
-- Run this in the Supabase SQL Editor (or via psql)

-- ---------------------------------------------------------------------------
-- 1. Extend user_usage_limits with new gated-feature counters
-- ---------------------------------------------------------------------------

ALTER TABLE public.user_usage_limits
ADD COLUMN IF NOT EXISTS ecosim_ai_runs_this_month int DEFAULT 0,
ADD COLUMN IF NOT EXISTS energyhub_ai_insights_this_month int DEFAULT 0,
ADD COLUMN IF NOT EXISTS energyhub_chart_analyses_this_month int DEFAULT 0,
ADD COLUMN IF NOT EXISTS exports_this_month int DEFAULT 0,
ADD COLUMN IF NOT EXISTS month_window date DEFAULT date_trunc('month', now());

-- Add primary key if not already present
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_usage_limits_pkey'
    ) THEN
        ALTER TABLE public.user_usage_limits ADD PRIMARY KEY (user_id);
    END IF;
END $$;

-- Add FK to profiles
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_usage_limits_user_id_fkey'
    ) THEN
        ALTER TABLE public.user_usage_limits
        ADD CONSTRAINT user_usage_limits_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE;
    END IF;
END $$;


-- ---------------------------------------------------------------------------
-- 2. Create plans_config table (authoritative source for free/premium limits)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.plans_config (
    plan text PRIMARY KEY,
    limits jsonb NOT NULL DEFAULT '{}',
    updated_at timestamptz DEFAULT now()
);

-- Seed default limits
INSERT INTO public.plans_config (plan, limits) VALUES
('free', '{
    "ecosim_ai_runs": 3,
    "energyhub_ai_insights": 5,
    "energyhub_chart_analyses": 5,
    "chat_messages": 10,
    "saved_simulations": 3,
    "exports": 0
}'::jsonb),
('premium', '{
    "ecosim_ai_runs": null,
    "energyhub_ai_insights": null,
    "energyhub_chart_analyses": null,
    "chat_messages": null,
    "saved_simulations": null,
    "exports": null
}'::jsonb)
ON CONFLICT (plan) DO UPDATE SET limits = EXCLUDED.limits;


-- ---------------------------------------------------------------------------
-- 3. RPC: increment_usage (safe column increment)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.increment_usage(p_user_id uuid, p_column text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.user_usage_limits (user_id)
    VALUES (p_user_id)
    ON CONFLICT (user_id) DO NOTHING;

    EXECUTE format(
        'UPDATE public.user_usage_limits SET %I = COALESCE(%I, 0) + 1 WHERE user_id = %L',
        p_column, p_column, p_user_id
    );
END;
$$;


-- ---------------------------------------------------------------------------
-- 4. RPC: reset_monthly_usage (cron-friendly monthly reset)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.reset_monthly_usage()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE public.user_usage_limits
    SET
        chat_messages_this_month = 0,
        simulations_this_month = 0,
        ecosim_ai_runs_this_month = 0,
        energyhub_ai_insights_this_month = 0,
        energyhub_chart_analyses_this_month = 0,
        exports_this_month = 0,
        month_window = date_trunc('month', now())
    WHERE month_window < date_trunc('month', now());
END;
$$;

-- Optional: schedule with pg_cron if extension is enabled
-- SELECT cron.schedule('reset-monthly-usage', '0 0 1 * *', 'SELECT public.reset_monthly_usage()');
