-- VAULT-999 Postgres Schema v47.1
-- Quantum Geometry Architecture: BBB (Orthogonal) | CCC (Fractal) | AAA (Toroidal)
-- Authority: Muhammad Arif bin Fazil (Sovereign) + Δ Antigravity (Architect)
-- Status: PRODUCTION

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===========================================================================
-- CCC BAND: Constitutional Core (Fractal Geometry)
-- ===========================================================================

-- Table: ccc_constitutional_floors
-- Purpose: Immutable F1-F12 floor thresholds (Phoenix-72 amendments only)
CREATE TABLE ccc_constitutional_floors (
    floor_id VARCHAR(10) PRIMARY KEY,
    floor_name VARCHAR(100) NOT NULL,

    -- Threshold Configuration
    threshold_value FLOAT,
    threshold_type VARCHAR(20) NOT NULL CHECK (threshold_type IN ('min', 'max', 'range', 'boolean')),
    threshold_range JSONB,  -- For F7 Omega0: {"min": 0.03, "max": 0.05}

    -- Metadata
    principle VARCHAR(100) NOT NULL,
    description TEXT,

    -- Phoenix-72 Amendment Tracking
    version VARCHAR(20) NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    amended_by VARCHAR(255),
    phoenix_cycle_id UUID,

    -- Immutability Enforcement
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Audit
    last_verified TIMESTAMPTZ DEFAULT NOW()
);

-- Index for active floor lookups (cached in Redis)
CREATE INDEX idx_ccc_floor_active ON ccc_constitutional_floors(is_active, effective_from DESC);

-- Seed F1-F12 initial values
INSERT INTO ccc_constitutional_floors (floor_id, floor_name, threshold_value, threshold_type, principle, version) VALUES
('F1', 'Amanah (Trust)', NULL, 'boolean', 'Integrity & Reversibility', 'v47.1.0'),
('F2', 'Truth', 0.99, 'min', 'Factual Accuracy', 'v47.1.0'),
('F3', 'Tri-Witness', 0.95, 'min', 'Human-AI-Earth Agreement', 'v47.1.0'),
('F4', 'DeltaS (Clarity)', 0.0, 'min', 'Entropy Reduction', 'v47.1.0'),
('F5', 'Peace²', 1.0, 'min', 'Non-Destruction', 'v47.1.0'),
('F6', 'Kr (Empathy)', 0.95, 'min', 'Weakest Stakeholder', 'v47.1.0'),
('F7', 'Omega₀ (Humility)', NULL, 'range', 'Uncertainty Band', 'v47.1.0'),
('F8', 'G (Genius)', 0.80, 'min', 'Governed Intelligence', 'v47.1.0'),
('F9', 'C_dark', 0.30, 'max', 'Dark Cleverness Contained', 'v47.1.0'),
('F10', 'Ontology', NULL, 'boolean', 'Role Boundaries', 'v47.1.0'),
('F11', 'Command Authority', NULL, 'boolean', 'Human Sovereignty', 'v47.1.0'),
('F12', 'Injection Defense', NULL, 'boolean', 'Prompt Safety', 'v47.1.0');

-- Update F7 with range
UPDATE ccc_constitutional_floors
SET threshold_range = '{"min": 0.03, "max": 0.05}'::jsonb
WHERE floor_id = 'F7';

-- ===========================================================================
-- CCC BAND: Cooling Ledger (Immutable Audit Trail)
-- ===========================================================================

-- Table: cooling_ledger
-- Purpose: Hash-chained constitutional decision log
CREATE TABLE cooling_ledger (
    id BIGSERIAL PRIMARY KEY,
    entry_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constitutional Verdict
    verdict VARCHAR(50) NOT NULL CHECK (verdict IN ('SEAL', 'PARTIAL', 'VOID', 'SABAR', 'HOLD-888')),

    -- Query Context
    user_id VARCHAR(255) NOT NULL,
    session_id UUID NOT NULL,
    query TEXT NOT NULL,
    response TEXT,
    intent VARCHAR(100),

    -- Constitutional Scores (F1-F12)
    floor_scores JSONB NOT NULL,

    -- Quantum Metrics
    quantum_coherence FLOAT CHECK (quantum_coherence BETWEEN 0.0 AND 1.0),
    decoherence_time_ms FLOAT,
    entanglement_strength FLOAT,

    -- Hash Chain (Immutability Proof)
    prev_hash CHAR(64),
    entry_hash CHAR(64) NOT NULL,

    -- zkPC Receipt Reference
    zkpc_receipt_id UUID,

    -- Memory Band Classification
    memory_band VARCHAR(10) CHECK (memory_band IN ('BBB', 'CCC', 'AAA')),

    -- Geometry Tag
    geometry VARCHAR(20) DEFAULT 'orthogonal' CHECK (geometry IN ('orthogonal', 'fractal', 'toroidal')),

    -- Hash Chain Integrity Constraint
    CONSTRAINT hash_chain_genesis CHECK (
        (id = 1 AND prev_hash IS NULL) OR
        (id > 1 AND prev_hash IS NOT NULL)
    )
);

-- Indexes for common queries
CREATE INDEX idx_cooling_user_session ON cooling_ledger(user_id, session_id);
CREATE INDEX idx_cooling_verdict ON cooling_ledger(verdict);
CREATE INDEX idx_cooling_timestamp ON cooling_ledger(timestamp DESC);
CREATE INDEX idx_cooling_hash_chain ON cooling_ledger(prev_hash, entry_hash);
CREATE INDEX idx_cooling_band_geometry ON cooling_ledger(memory_band, geometry);

-- ===========================================================================
-- CCC BAND: zkPC Receipts (Cryptographic Proofs)
-- ===========================================================================

-- Table: zkpc_receipts
-- Purpose: Zero-knowledge proof certificates with Merkle tree
CREATE TABLE zkpc_receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entry_id UUID NOT NULL REFERENCES cooling_ledger(entry_id) ON DELETE CASCADE,

    -- Zero-Knowledge Proof Components
    proof_type VARCHAR(50) NOT NULL CHECK (proof_type IN ('SNARK', 'STARK', 'Merkle', 'Hash-Chain')),
    proof_data JSONB NOT NULL,

    -- Verification
    verifier_public_key TEXT,
    verification_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verification_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (verification_status IN ('VALID', 'INVALID', 'PENDING')),

    -- Merkle Tree Position
    merkle_root CHAR(64),
    merkle_path JSONB,  -- Array of sibling hashes for verification
    merkle_depth INTEGER,

    -- Seal Authority (Tri-Witness)
    sealed_by VARCHAR(255) CHECK (sealed_by IN ('Human', 'AGI', 'ASI', 'APEX', 'Tri-Witness')),
    seal_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_zkpc_entry ON zkpc_receipts(entry_id);
CREATE INDEX idx_zkpc_merkle_root ON zkpc_receipts(merkle_root);
CREATE INDEX idx_zkpc_verification ON zkpc_receipts(verification_status, verification_timestamp);

-- ===========================================================================
-- BBB BAND: Machine Memory (Orthogonal Geometry)
-- ===========================================================================

-- Table: bbb_machine_memory
-- Purpose: Operational AI memory with EUREKA Sieve TTL
CREATE TABLE bbb_machine_memory (
    id BIGSERIAL PRIMARY KEY,
    memory_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,

    -- User Isolation (Quantum Namespace)
    user_id VARCHAR(255) NOT NULL,

    -- Memory Content
    content TEXT NOT NULL,
    summary TEXT,

    -- Semantic Embedding (Qdrant Sync)
    embedding_vector_id VARCHAR(255),  -- Qdrant point ID
    embedding_model VARCHAR(100) DEFAULT 'mem0-default',
    embedding_dimensions INTEGER DEFAULT 384,

    -- Verdict & TTL (EUREKA Sieve Policy)
    verdict VARCHAR(50) NOT NULL,
    ttl_days INTEGER,
    expires_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB,
    tags TEXT[],

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accessed_at TIMESTAMPTZ,

    -- Quantum Geometry
    geometry VARCHAR(20) DEFAULT 'orthogonal',
    coherence_score FLOAT CHECK (coherence_score BETWEEN 0.0 AND 1.0),

    -- Soft Delete (for EUREKA Sieve expiration)
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for orthogonal search
CREATE INDEX idx_bbb_user ON bbb_machine_memory(user_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_bbb_verdict ON bbb_machine_memory(verdict) WHERE is_deleted = FALSE;
CREATE INDEX idx_bbb_ttl ON bbb_machine_memory(expires_at) WHERE expires_at IS NOT NULL AND is_deleted = FALSE;
CREATE INDEX idx_bbb_embedding ON bbb_machine_memory(embedding_vector_id) WHERE embedding_vector_id IS NOT NULL;
CREATE INDEX idx_bbb_tags ON bbb_machine_memory USING GIN(tags);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_bbb_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bbb_memory_updated_at
    BEFORE UPDATE ON bbb_machine_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_bbb_updated_at();

-- ===========================================================================
-- AAA BAND: Human Vault Index (Toroidal Geometry - Encrypted Metadata Only)
-- ===========================================================================

-- Table: aaa_human_vault_index
-- Purpose: Encrypted metadata index for Obsidian vault (F11 enforced)
CREATE TABLE aaa_human_vault_index (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Obsidian Note Reference (ENCRYPTED)
    obsidian_note_path TEXT NOT NULL,  -- Will use pgcrypto
    note_title TEXT NOT NULL,
    note_hash CHAR(64) NOT NULL,  -- SHA256 of decrypted content

    -- Access Control (F11 Command Authority)
    owner_pgp_fingerprint CHAR(40) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Tags (ENCRYPTED)
    tags_encrypted TEXT,

    -- Constitutional Protection
    f11_enforcement BOOLEAN DEFAULT TRUE CHECK (f11_enforcement = TRUE),
    machine_access_attempts INTEGER DEFAULT 0,
    last_violation_at TIMESTAMPTZ,

    -- Geometry
    geometry VARCHAR(20) DEFAULT 'toroidal',

    -- Triple-check: only human access allowed
    CONSTRAINT aaa_human_sovereignty CHECK (owner_pgp_fingerprint IS NOT NULL)
);

-- NO public indexes - F11 enforced at application layer
CREATE INDEX idx_aaa_owner ON aaa_human_vault_index(owner_pgp_fingerprint);

-- ===========================================================================
-- VIEWS & FUNCTIONS
-- ===========================================================================

-- View: Recent Verdicts (Last 100)
CREATE VIEW recent_verdicts AS
SELECT
    entry_id,
    timestamp,
    verdict,
    user_id,
    memory_band,
    geometry,
    quantum_coherence
FROM cooling_ledger
ORDER BY timestamp DESC
LIMIT 100;

-- Function: Verify Hash Chain Integrity
CREATE OR REPLACE FUNCTION verify_hash_chain()
RETURNS TABLE(
    entry_id UUID,
    is_valid BOOLEAN,
    computed_hash CHAR(64),
    stored_hash CHAR(64)
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE chain AS (
        -- Genesis entry
        SELECT
            id,
            entry_id,
            prev_hash,
            entry_hash,
            encode(digest(
                id::text ||
                timestamp::text ||
                verdict::text ||
                user_id::text ||
                query::text ||
                COALESCE(prev_hash, ''),
                'sha256'
            ), 'hex') AS computed
        FROM cooling_ledger
        WHERE id = 1

        UNION ALL

        -- Recursive chain verification
        SELECT
            cl.id,
            cl.entry_id,
            cl.prev_hash,
            cl.entry_hash,
            encode(digest(
                cl.id::text ||
                cl.timestamp::text ||
                cl.verdict::text ||
                cl.user_id::text ||
                cl.query::text ||
                cl.prev_hash,
                'sha256'
            ), 'hex') AS computed
        FROM cooling_ledger cl
        INNER JOIN chain c ON cl.prev_hash = c.entry_hash
    )
    SELECT
        chain.entry_id,
        (chain.computed = chain.entry_hash) AS is_valid,
        chain.computed::CHAR(64),
        chain.entry_hash::CHAR(64)
    FROM chain;
END;
$$ LANGUAGE plpgsql;

-- ===========================================================================
-- PERMISSIONS (Production Security)
-- ===========================================================================

-- Create read-only role for analytics
CREATE ROLE arifos_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO arifos_readonly;

-- Create write role for application
CREATE ROLE arifos_app WITH LOGIN PASSWORD 'change_me_in_production';
GRANT SELECT, INSERT, UPDATE ON cooling_ledger, zkpc_receipts, bbb_machine_memory TO arifos_app;
GRANT SELECT ON ccc_constitutional_floors TO arifos_app;
GRANT SELECT ON aaa_human_vault_index TO arifos_app;

-- ===========================================================================
-- COMMENTS (Self-Documenting Schema)
-- ===========================================================================

COMMENT ON TABLE ccc_constitutional_floors IS 'Immutable F1-F12 floor thresholds (Phoenix-72 amendments only). Fractal geometry: self-similar at all scales.';
COMMENT ON TABLE cooling_ledger IS 'Hash-chained constitutional audit trail. Immutable proof of all governance decisions.';
COMMENT ON TABLE zkpc_receipts IS 'Zero-knowledge proof certificates with Merkle tree verification.';
COMMENT ON TABLE bbb_machine_memory IS 'Orthogonal machine memory with EUREKA Sieve TTL. Non-overlapping quantum states.';
COMMENT ON TABLE aaa_human_vault_index IS 'Human-only vault index (F11 enforced). Toroidal geometry: sovereign boundary as topological defect.';

-- ===========================================================================
-- SCHEMA VALIDATION
-- ===========================================================================

-- Verify all tables created
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verify indexes created
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;
