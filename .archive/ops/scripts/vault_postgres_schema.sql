--
-- VAULT999 PostgreSQL Schema
-- arifOS Constitutional Ledger — Primary Source of Truth
-- DITEMPA BUKAN DIBERI — Forged, Not Given
--
-- This schema implements an append-only Merkle chain for constitutional audit.
-- All writes are INSERT-only (no UPDATE/DELETE on sealed records).
--

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. VAULT EVENTS (append-only canonical ledger)
-- ============================================================
CREATE TABLE IF NOT EXISTS vault_events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    event_type VARCHAR(64) NOT NULL,           -- 'seal', 'verify', 'sabar', 'void'
    session_id UUID NOT NULL,
    actor_id VARCHAR(128) NOT NULL,            -- 'validator.mcp', 'engineer.mcp', etc.
    
    -- Constitutional context
    stage VARCHAR(32) NOT NULL,                -- '999_VAULT', '888_JUDGE', etc.
    verdict VARCHAR(32) NOT NULL,              -- 'SEAL', 'SABAR', 'VOID', 'HOLD'
    risk_tier VARCHAR(16) NOT NULL DEFAULT 'medium',
    
    -- Payload (JSONB for flexibility)
    payload JSONB NOT NULL DEFAULT '{}',
    
    -- Merkle chain fields (for tamper detection)
    merkle_leaf VARCHAR(64) NOT NULL,          -- SHA-256 of this record's content
    prev_hash VARCHAR(64) NOT NULL,            -- Hash of previous record in chain
    chain_hash VARCHAR(64) NOT NULL,           -- Cumulative chain hash
    
    -- 888 Signature (when applicable)
    signature VARCHAR(256),
    signed_by VARCHAR(128),
    
    -- Timing
    sealed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Soft-delete marker (for purgatory/sabar states, not actual deletion)
    is_superseded BOOLEAN DEFAULT FALSE,
    superseded_by UUID REFERENCES vault_events(event_id)
);

-- Indexes for audit queries
CREATE INDEX IF NOT EXISTS idx_vault_events_session ON vault_events(session_id);
CREATE INDEX IF NOT EXISTS idx_vault_events_time ON vault_events(sealed_at);
CREATE INDEX IF NOT EXISTS idx_vault_events_type ON vault_events(event_type);
CREATE INDEX IF NOT EXISTS idx_vault_events_verdict ON vault_events(verdict);
CREATE INDEX IF NOT EXISTS idx_vault_events_actor ON vault_events(actor_id);
CREATE INDEX IF NOT EXISTS idx_vault_events_chain ON vault_events(chain_hash);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_vault_events_session_time ON vault_events(session_id, sealed_at DESC);

-- ============================================================
-- 2. VAULT SEALS (Merkle tree roots per batch)
-- ============================================================
CREATE TABLE IF NOT EXISTS vault_seals (
    id BIGSERIAL PRIMARY KEY,
    seal_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    
    -- Merkle tree state
    tree_size BIGINT NOT NULL,                 -- Number of leaves in tree
    merkle_root VARCHAR(64) NOT NULL,          -- RFC 6962 Merkle root
    prev_root VARCHAR(64) NOT NULL,            -- Previous tree root
    
    -- Tree boundaries (inclusive)
    first_event_id BIGINT REFERENCES vault_events(id),
    last_event_id BIGINT REFERENCES vault_events(id),
    
    -- 888 Signature
    signature VARCHAR(256) NOT NULL,
    signed_by VARCHAR(128) NOT NULL DEFAULT '888_AUDITOR',
    
    -- Timing
    sealed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Optional: link to filesystem archive
    archive_path VARCHAR(512)
);

CREATE INDEX IF NOT EXISTS idx_vault_seals_root ON vault_seals(merkle_root);
CREATE INDEX IF NOT EXISTS idx_vault_seals_time ON vault_seals(sealed_at);

-- ============================================================
-- 3. VAULT SESSIONS (session metadata)
-- ============================================================
CREATE TABLE IF NOT EXISTS vault_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_session_id UUID REFERENCES vault_sessions(session_id),
    
    -- Actor info
    actor_id VARCHAR(128) NOT NULL,
    actor_type VARCHAR(64) NOT NULL DEFAULT 'human', -- 'human', 'agent', 'system'
    
    -- Session context
    model_name VARCHAR(64),
    caller_info JSONB DEFAULT '{}',
    constitutional_context JSONB DEFAULT '{}',
    
    -- Risk classification
    max_risk_tier VARCHAR(16) DEFAULT 'medium',
    pns_enabled BOOLEAN DEFAULT TRUE,
    
    -- Lifecycle
    started_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    ended_at TIMESTAMPTZ,
    
    -- Session outcome
    final_verdict VARCHAR(32),
    event_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_vault_sessions_actor ON vault_sessions(actor_id);
CREATE INDEX IF NOT EXISTS idx_vault_sessions_time ON vault_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_vault_sessions_parent ON vault_sessions(parent_session_id);

-- ============================================================
-- 4. VAULT ARTIFACTS (filesystem pointers)
-- ============================================================
CREATE TABLE IF NOT EXISTS vault_artifacts (
    id BIGSERIAL PRIMARY KEY,
    artifact_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    
    -- Link to event
    event_id BIGINT REFERENCES vault_events(id) ON DELETE CASCADE,
    session_id UUID REFERENCES vault_sessions(session_id),
    
    -- Artifact metadata
    artifact_type VARCHAR(64) NOT NULL,        -- 'jsonl', 'image', 'log', 'export'
    file_path VARCHAR(512) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,            -- SHA-256 of file content
    file_size BIGINT,
    
    -- Content metadata
    content_type VARCHAR(128),
    description TEXT,
    
    -- Timing
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vault_artifacts_event ON vault_artifacts(event_id);
CREATE INDEX IF NOT EXISTS idx_vault_artifacts_session ON vault_artifacts(session_id);
CREATE INDEX IF NOT EXISTS idx_vault_artifacts_type ON vault_artifacts(artifact_type);

-- ============================================================
-- 5. VAULT MIRROR LOG (filesystem sync tracking)
-- ============================================================
CREATE TABLE IF NOT EXISTS vault_mirror_log (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT REFERENCES vault_events(id) ON DELETE CASCADE,
    mirror_type VARCHAR(32) NOT NULL DEFAULT 'filesystem', -- 'filesystem', 'qdrant', 's3'
    mirror_status VARCHAR(32) NOT NULL DEFAULT 'pending',  -- 'pending', 'synced', 'failed'
    mirror_path VARCHAR(512),
    error_message TEXT,
    attempted_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_mirror_log_event ON vault_mirror_log(event_id);
CREATE INDEX IF NOT EXISTS idx_mirror_log_status ON vault_mirror_log(mirror_status);

-- ============================================================
-- 6. FUNCTIONS FOR MERKLE CHAIN
-- ============================================================

-- Function to get the last chain hash
CREATE OR REPLACE FUNCTION get_last_chain_hash()
RETURNS VARCHAR(64) AS $$
DECLARE
    last_hash VARCHAR(64);
BEGIN
    SELECT chain_hash INTO last_hash
    FROM vault_events
    ORDER BY id DESC
    LIMIT 1;
    
    RETURN COALESCE(last_hash, repeat('0', 64));
END;
$$ LANGUAGE plpgsql;

-- Function to verify chain integrity
CREATE OR REPLACE FUNCTION verify_chain_integrity(start_id BIGINT DEFAULT 1)
RETURNS TABLE (
    is_valid BOOLEAN,
    broken_at_id BIGINT,
    expected_hash VARCHAR(64),
    actual_hash VARCHAR(64),
    total_checked BIGINT
) AS $$
DECLARE
    rec RECORD;
    expected_prev VARCHAR(64);
    check_count BIGINT := 0;
BEGIN
    expected_prev := repeat('0', 64);
    
    FOR rec IN 
        SELECT id, prev_hash, chain_hash
        FROM vault_events
        WHERE id >= start_id
        ORDER BY id
    LOOP
        check_count := check_count + 1;
        
        IF rec.prev_hash != expected_prev THEN
            RETURN QUERY SELECT 
                FALSE,
                rec.id,
                expected_prev,
                rec.prev_hash,
                check_count;
            RETURN;
        END IF;
        
        expected_prev := rec.chain_hash;
    END LOOP;
    
    RETURN QUERY SELECT TRUE, NULL::BIGINT, NULL::VARCHAR, NULL::VARCHAR, check_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 7. ROW-LEVEL SECURITY (optional, for multi-tenant)
-- ============================================================
-- Enable RLS on vault_events
-- ALTER TABLE vault_events ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- 8. MIGRATION: Migrate from vault_audit if exists
-- ============================================================

-- Check if old table exists and has data
DO $$
DECLARE
    old_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO old_count FROM vault_audit;
    
    IF old_count > 0 THEN
        RAISE NOTICE 'Found % rows in vault_audit. Consider migrating.', old_count;
        
        -- Insert old records into new schema (if not already present)
        INSERT INTO vault_events (
            event_type, session_id, actor_id, stage, verdict, risk_tier,
            payload, merkle_leaf, prev_hash, chain_hash, signature, signed_by, sealed_at
        )
        SELECT 
            COALESCE(stage, 'audit'),
            COALESCE(NULLIF(session_id, '')::UUID, uuid_generate_v4()),
            COALESCE(actor_id, 'migrated'),
            COALESCE(stage, '999_VAULT'),
            COALESCE(verdict, 'SEAL'),
            'medium',
            COALESCE(payload, '{}'),
            COALESCE(hash, encode(digest(id::text, 'sha256'), 'hex')),
            repeat('0', 64),  -- Cannot reconstruct chain from old data
            COALESCE(sha256_hash, repeat('0', 64)),
            ledger_id,
            '888_AUDITOR',
            COALESCE(created_at, NOW())
        FROM vault_audit
        WHERE NOT EXISTS (
            SELECT 1 FROM vault_events WHERE vault_events.sealed_at = vault_audit.created_at
        );
        
        RAISE NOTICE 'Migration complete. New row count: %', (SELECT COUNT(*) FROM vault_events);
    END IF;
END $$;

-- ============================================================
-- 9. GRANTS (if needed)
-- ============================================================
-- GRANT SELECT, INSERT ON vault_events TO arifos_app;
-- GRANT SELECT, INSERT ON vault_seals TO arifos_app;
-- GRANT SELECT, INSERT ON vault_sessions TO arifos_app;

-- ============================================================
-- Done
-- ============================================================
SELECT 'VAULT999 schema created successfully' AS status;
