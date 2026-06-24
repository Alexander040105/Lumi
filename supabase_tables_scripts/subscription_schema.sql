-- ============================================================
-- LUMI Subscription Schema Migration
-- Adds usage tracking and feature permissions for Free/Pro/Premium tiers
-- Compatible with existing lumi_schema_v4.sql
-- ============================================================

-- 1. usage_tracking table
-- Tracks per-user consumption of AI-powered and gated features.
CREATE TABLE IF NOT EXISTS usage_tracking (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    feature_type text NOT NULL CHECK (feature_type IN (
        'chat', 'simulation', 'ai_insight_ecosim', 'ai_insight_energyhub'
    )),
    tokens_input int NOT NULL DEFAULT 0,
    tokens_output int NOT NULL DEFAULT 0,
    metadata jsonb DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_feature
    ON usage_tracking(user_id, feature_type, created_at);

CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_created
    ON usage_tracking(user_id, created_at);

COMMENT ON TABLE usage_tracking IS 'Tracks per-user consumption for feature gating and cost analytics';
COMMENT ON COLUMN usage_tracking.feature_type IS 'Type of gated feature: chat, simulation, ai_insight_ecosim, ai_insight_energyhub';
COMMENT ON COLUMN usage_tracking.tokens_input IS 'Number of input tokens consumed (for LLM-based features)';
COMMENT ON COLUMN usage_tracking.tokens_output IS 'Number of output tokens generated (for LLM-based features)';

-- 2. feature_permissions table
-- Centralized, database-driven plan configuration.
CREATE TABLE IF NOT EXISTS feature_permissions (
    plan text PRIMARY KEY CHECK (plan IN ('free', 'pro', 'premium')),
    limits jsonb NOT NULL DEFAULT '{}',
    features jsonb NOT NULL DEFAULT '{}',
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- Seed default plan permissions
INSERT INTO feature_permissions (plan, limits, features)
VALUES
    ('free',
     '{"simulations": 3, "chat_messages": 5, "ai_insights": 1}',
     '{"chat_persistence": false, "data_export": false, "batch_compare": false, "priority_response": false}'
    ),
    ('pro',
     '{"simulations": 20, "chat_messages": 50, "ai_insights": 5}',
     '{"chat_persistence": true, "data_export": false, "batch_compare": false, "priority_response": false}'
    ),
    ('premium',
     '{"simulations": 999999, "chat_messages": 200, "ai_insights": 20}',
     '{"chat_persistence": true, "data_export": true, "batch_compare": true, "priority_response": true}'
    )
ON CONFLICT (plan) DO UPDATE
    SET limits = EXCLUDED.limits,
        features = EXCLUDED.features,
        updated_at = now();

COMMENT ON TABLE feature_permissions IS 'Defines feature limits and capabilities for each subscription plan';

-- 3. Auto-update trigger for feature_permissions.updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_feature_permissions_updated_at ON feature_permissions;
CREATE TRIGGER trigger_feature_permissions_updated_at
    BEFORE UPDATE ON feature_permissions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 4. RLS policies for usage_tracking (users can only see their own usage)
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS usage_tracking_user_select ON usage_tracking;
CREATE POLICY usage_tracking_user_select
    ON usage_tracking FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS usage_tracking_user_insert ON usage_tracking;
CREATE POLICY usage_tracking_user_insert
    ON usage_tracking FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- 5. RLS policies for feature_permissions (public read, admin write)
ALTER TABLE feature_permissions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS feature_permissions_public_read ON feature_permissions;
CREATE POLICY feature_permissions_public_read
    ON feature_permissions FOR SELECT
    USING (true);
