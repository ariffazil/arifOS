-- arifOS Memory Engine v1 Schema
-- Path: arifOS/arifosmcp/migrations/001_memory_schema.sql

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Memory Records: Canonical store for all governed memories
CREATE TABLE IF NOT EXISTS memory_records (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL DEFAULT 'default',
    actor_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    project_id TEXT,
    
    type TEXT NOT NULL CHECK (type IN ('working', 'episodic', 'semantic', 'procedural', 'policy')),
    subject TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    
    source_type TEXT NOT NULL,
    source_ref JSONB,
    
    confidence FLOAT DEFAULT 0.0,
    authority TEXT CHECK (authority IN ('explicit_user', 'system_inferred', 'document', 'unknown')),
    sensitivity FLOAT DEFAULT 0.0,
    consent_level TEXT,
    
    freshness_ts TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_validated_ts TIMESTAMPTZ,
    
    retention_class TEXT CHECK (retention_class IN ('transient', 'reviewable', 'durable', 'immutable_audit')),
    expires_at TIMESTAMPTZ,
    revocable BOOLEAN DEFAULT TRUE,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired', 'revoked', 'superseded')),
    
    supersedes UUID REFERENCES memory_records(memory_id),
    superseded_by UUID REFERENCES memory_records(memory_id),
    
    tags TEXT[],
    embedding_status TEXT DEFAULT 'pending' CHECK (embedding_status IN ('pending', 'ready', 'failed')),
    
    hash TEXT NOT NULL, -- sha256 of content
    version INT DEFAULT 1,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Memory Embeddings: Vector store (pgvector)
-- Using 1536 dims for OpenAI or 768 for nomic-embed-text (Ollama default)
-- We will use 1536 as requested in TypeScript prompt, but configurable in implementation.
CREATE TABLE IF NOT EXISTS memory_embeddings (
    memory_id UUID PRIMARY KEY REFERENCES memory_records(memory_id) ON DELETE CASCADE,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Memory Audit Log: Immutable, append-only ledger
CREATE TABLE IF NOT EXISTS memory_audit_log (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID, -- Optional, link to record
    event_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    payload JSONB,
    hash TEXT, -- Optional chain hash
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Memory Write Queue: Async embedding/processing jobs
CREATE TABLE IF NOT EXISTS memory_write_queue (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES memory_records(memory_id) ON DELETE CASCADE,
    retry_count INT DEFAULT 0,
    last_error TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Memory Review Queue: Human approval queue for sensitive/policy writes
CREATE TABLE IF NOT EXISTS memory_review_queue (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES memory_records(memory_id) ON DELETE CASCADE,
    reviewer_id TEXT,
    decision TEXT CHECK (decision IN ('approved', 'rejected', 'modified')),
    comments TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Memory Revocations: Soft and hard delete tracking
CREATE TABLE IF NOT EXISTS memory_revocations (
    revocation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES memory_records(memory_id) ON DELETE CASCADE,
    actor_id TEXT NOT NULL,
    reason TEXT,
    type TEXT CHECK (type IN ('soft', 'hard')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_memory_records_actor ON memory_records(actor_id);
CREATE INDEX IF NOT EXISTS idx_memory_records_session ON memory_records(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_records_status ON memory_records(status);
CREATE INDEX IF NOT EXISTS idx_memory_records_type ON memory_records(type);
CREATE INDEX IF NOT EXISTS idx_memory_audit_event ON memory_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_memory_audit_session ON memory_audit_log(session_id);
