-- Enable pgvector extension if it is not already enabled.
-- On Supabase the extension may already be toggled on in the dashboard under
-- Database -> Extensions; this statement is idempotent.
CREATE EXTENSION IF NOT EXISTS vector;

-- Make sure the extensions schema is in the search path for this migration so
-- the vector type and operators resolve correctly.
SET search_path TO public, extensions;

-- RAG chunk storage.
-- Chunks and their 384-d embeddings (all-MiniLM-L6-v2) are kept here instead
-- of the local FAISS index so Vercel serverless functions can retrieve them.
CREATE TABLE IF NOT EXISTS public.rag_chunks (
    id              BIGSERIAL PRIMARY KEY,
    chunk_text      TEXT NOT NULL,
    renewable_type  TEXT,
    category        TEXT,
    product_type    TEXT,
    sources         JSONB,
    embedding       VECTOR(384),
    search_vector   TSVECTOR
                    GENERATED ALWAYS AS (to_tsvector('english', COALESCE(chunk_text, ''))) STORED,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ivfflat index for approximate nearest-neighbor vector search.
-- List count 100 is the pgvector default and is fine for the current chunk count.
CREATE INDEX IF NOT EXISTS rag_chunks_embedding_idx
    ON public.rag_chunks USING ivfflat (embedding vector_cosine_ops);

-- Metadata indexes for the renewable_type / category filters used by chat and ecosim.
CREATE INDEX IF NOT EXISTS rag_chunks_renewable_type_idx
    ON public.rag_chunks (renewable_type);

CREATE INDEX IF NOT EXISTS rag_chunks_category_idx
    ON public.rag_chunks (category);

-- GIN index for the keyword/hybrid search component.
CREATE INDEX IF NOT EXISTS rag_chunks_search_vector_idx
    ON public.rag_chunks USING GIN (search_vector);

-- Row-level security: chunks are public read, writable only by the service role.
ALTER TABLE public.rag_chunks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS rag_chunks_select_policy ON public.rag_chunks;
CREATE POLICY rag_chunks_select_policy ON public.rag_chunks
    FOR SELECT USING (true);

DROP POLICY IF EXISTS rag_chunks_write_policy ON public.rag_chunks;
CREATE POLICY rag_chunks_write_policy ON public.rag_chunks
    FOR ALL USING (false) WITH CHECK (false);

-- RPC that performs cosine-similarity retrieval with optional metadata filters.
-- `embedding <=> query_embedding` is pgvector cosine distance, so
-- similarity = 1 - distance.
CREATE OR REPLACE FUNCTION public.match_rag_chunks(
    query_embedding       VECTOR(384),
    match_count           INT DEFAULT 20,
    similarity_threshold  FLOAT DEFAULT 0.25,
    filter_renewable_type TEXT DEFAULT NULL,
    filter_category       TEXT DEFAULT NULL
)
RETURNS TABLE (
    id             BIGINT,
    chunk_text     TEXT,
    renewable_type TEXT,
    category       TEXT,
    product_type   TEXT,
    sources        JSONB,
    similarity     FLOAT
)
LANGUAGE SQL
SECURITY DEFINER
SET search_path = public, extensions
AS $$
    SELECT
        id,
        chunk_text,
        renewable_type,
        category,
        product_type,
        sources,
        (1.0 - (embedding <=> query_embedding))::FLOAT AS similarity
    FROM public.rag_chunks
    WHERE
        (filter_renewable_type IS NULL OR renewable_type = filter_renewable_type)
        AND (filter_category IS NULL OR category = filter_category)
        AND (1.0 - (embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
