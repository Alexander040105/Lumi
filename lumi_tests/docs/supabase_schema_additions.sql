-- LUMI Supabase Schema Additions
-- Run this script in the Supabase SQL Editor to create all tables,
-- triggers, RLS policies, and enums required for the Auth, Chatbot,
-- Dashboard, and Admin Portal features.
--
-- Tables created:
--   user_roles, profiles, saved_simulations, saved_locations,
--   chat_sessions, chat_messages, user_usage_limits, admin_audit_log

-- ---------------------------------------------------------------------------
-- 1. Enum types
-- ---------------------------------------------------------------------------
CREATE TYPE public.app_role AS ENUM ('user', 'admin', 'dev');

-- ---------------------------------------------------------------------------
-- 2. Core auth extension tables
-- ---------------------------------------------------------------------------

-- user_roles: one row per Supabase auth user
CREATE TABLE public.user_roles (
    user_id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
    role public.app_role NOT NULL DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.user_roles IS 'Role-based access control mapping for LUMI users.';

-- profiles: editable user profile data (extends auth.users metadata)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
    full_name TEXT,
    avatar_url TEXT,
    organization TEXT,
    location TEXT,
    preferred_municipality_id INTEGER,
    plan TEXT DEFAULT 'free',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.profiles IS 'Extended user profile for personalization and dashboard display.';

-- ---------------------------------------------------------------------------
-- 3. Saved data tables (Feature A: saved simulations & locations)
-- ---------------------------------------------------------------------------

CREATE TABLE public.saved_simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users NOT NULL,
    label TEXT,
    municipality_id INTEGER,
    inputs JSONB DEFAULT '{}',
    results JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.saved_simulations IS 'Persisted EcoSim simulation inputs and results per user.';

CREATE TABLE public.saved_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users NOT NULL,
    municipality_id INTEGER NOT NULL,
    label TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, municipality_id)
);

COMMENT ON TABLE public.saved_locations IS 'User bookmarked municipalities for quick access.';

-- ---------------------------------------------------------------------------
-- 4. Chatbot tables (Feature F: RAG-powered chat)
-- ---------------------------------------------------------------------------

CREATE TABLE public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users NOT NULL,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.chat_sessions IS 'Chat session grouping for the LUMI AI assistant.';

CREATE TABLE public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.chat_sessions ON DELETE CASCADE,
    role TEXT CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    retrieved_chunks JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.chat_messages IS 'Individual chat messages with RAG context metadata.';

-- ---------------------------------------------------------------------------
-- 5. Usage limits / plan gating
-- ---------------------------------------------------------------------------

CREATE TABLE public.user_usage_limits (
    user_id UUID PRIMARY KEY REFERENCES auth.users,
    chat_messages_this_month INTEGER DEFAULT 0,
    simulations_this_month INTEGER DEFAULT 0,
    plan TEXT DEFAULT 'free'
);

COMMENT ON TABLE public.user_usage_limits IS 'Tracks monthly usage against free/premium plan limits.';

-- ---------------------------------------------------------------------------
-- 6. Admin audit log
-- ---------------------------------------------------------------------------

CREATE TABLE public.admin_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID REFERENCES auth.users,
    action TEXT NOT NULL,
    target_user_id UUID REFERENCES auth.users,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.admin_audit_log IS 'Immutable log of administrative actions for accountability.';

-- ---------------------------------------------------------------------------
-- 7. Auto-create profile + role + usage limits on signup
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name');

    INSERT INTO public.user_roles (user_id, role)
    VALUES (NEW.id, 'user');

    INSERT INTO public.user_usage_limits (user_id, plan)
    VALUES (NEW.id, 'free');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ---------------------------------------------------------------------------
-- 8. Row-Level Security (RLS) Policies
-- ---------------------------------------------------------------------------

-- profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- saved_simulations
ALTER TABLE public.saved_simulations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can CRUD own simulations"
    ON public.saved_simulations FOR ALL
    USING (auth.uid() = user_id);

-- saved_locations
ALTER TABLE public.saved_locations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can CRUD own locations"
    ON public.saved_locations FOR ALL
    USING (auth.uid() = user_id);

-- chat_sessions
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can CRUD own chat sessions"
    ON public.chat_sessions FOR ALL
    USING (auth.uid() = user_id);

-- chat_messages (via session ownership)
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can CRUD own chat messages"
    ON public.chat_messages FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.chat_sessions s
            WHERE s.id = session_id AND s.user_id = auth.uid()
        )
    );

-- user_usage_limits
ALTER TABLE public.user_usage_limits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own usage"
    ON public.user_usage_limits FOR SELECT
    USING (auth.uid() = user_id);

-- admin_audit_log: admins only (service-role or backend bypass recommended)
ALTER TABLE public.admin_audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view audit log"
    ON public.admin_audit_log FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles r
            WHERE r.user_id = auth.uid()
              AND r.role IN ('admin', 'dev')
        )
    );

-- ---------------------------------------------------------------------------
-- 9. Indexes for performance
-- ---------------------------------------------------------------------------
CREATE INDEX idx_saved_simulations_user_id ON public.saved_simulations(user_id);
CREATE INDEX idx_saved_locations_user_id ON public.saved_locations(user_id);
CREATE INDEX idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX idx_admin_audit_admin_id ON public.admin_audit_log(admin_id);
CREATE INDEX idx_admin_audit_created_at ON public.admin_audit_log(created_at DESC);
