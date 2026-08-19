-- Schema inicial: dados estruturados (SQL) + dados semânticos (pgvector)

CREATE EXTENSION IF NOT EXISTS vector;

-- ─────────────────────────────────────────────────────────────
-- Dados estruturados: requisitos de ambientes, materiais, famílias
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS requirements (
    id            SERIAL PRIMARY KEY,
    environment   TEXT NOT NULL,          -- ex: "sala", "quarto", "banheiro"
    area_min      NUMERIC,
    height_min    NUMERIC,
    doors         INTEGER,
    extra         JSONB DEFAULT '{}',     -- campos livres vindos de outras planilhas
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (environment)
);

CREATE TABLE IF NOT EXISTS materials (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    category    TEXT,
    properties  JSONB DEFAULT '{}',
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS families (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    category    TEXT,
    parameters  JSONB DEFAULT '{}',
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Cache local de níveis do projeto Revit ativo (populado pelo bridge C#)
CREATE TABLE IF NOT EXISTS revit_levels (
    id          SERIAL PRIMARY KEY,
    project_id  TEXT NOT NULL,
    name        TEXT NOT NULL,
    elevation   NUMERIC NOT NULL,
    synced_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (project_id, name)
);

-- ─────────────────────────────────────────────────────────────
-- Dados semânticos: normas/documentos para RAG vetorial
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents (
    id          SERIAL PRIMARY KEY,
    source      TEXT NOT NULL,           -- nome do arquivo/norma de origem
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(384),             -- dimensão do MiniLM multilingual
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING hnsw (embedding vector_cosine_ops);

-- Histórico de conversas do agente (opcional, útil para auditoria/debug)
CREATE TABLE IF NOT EXISTS chat_messages (
    id            SERIAL PRIMARY KEY,
    session_id    TEXT NOT NULL,
    role          TEXT NOT NULL,          -- user | assistant | tool
    content       TEXT NOT NULL,
    tool_calls    JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Alguns requisitos de exemplo (baseados no exemplo do documento original)
INSERT INTO requirements (environment, area_min, height_min, doors) VALUES
    ('sala', 12, 2.70, 1),
    ('quarto', 9, 2.70, 1),
    ('banheiro', 3, 2.40, 1)
ON CONFLICT (environment) DO NOTHING;
