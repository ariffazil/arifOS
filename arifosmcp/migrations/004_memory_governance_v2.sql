-- Migration: 004_memory_governance_v2.sql
-- Phase 1e: Constitutional Memory Governance v2
--
-- Adds provenance, risk, virtue, and governance columns to memory_store.
-- All columns are nullable for backward compat with existing records.
-- New writes populate these via store_v2 envelope path.
--
-- DITEMPA BUKAN DIBERI — Forged, Not Given

-- ============================================================================
-- 1. Provenance columns
-- ============================================================================

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS memory_intent TEXT DEFAULT NULL;

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS niat TEXT DEFAULT NULL;

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS source_type TEXT DEFAULT NULL;

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS source_uri TEXT DEFAULT NULL;

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS source_confidence FLOAT DEFAULT NULL;

-- ============================================================================
-- 2. Risk / M-tier columns
-- ============================================================================

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS m_tier TEXT DEFAULT NULL
    CONSTRAINT chk_memory_m_tier CHECK (m_tier IS NULL OR m_tier IN ('M0', 'M1', 'M2', 'M3', 'M4'));

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS authority_effect TEXT DEFAULT NULL
    CONSTRAINT chk_memory_authority_effect CHECK (authority_effect IS NULL OR authority_effect IN ('none', 'advisory', 'operational', 'sovereign'));

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS privacy_level TEXT DEFAULT NULL
    CONSTRAINT chk_memory_privacy CHECK (privacy_level IS NULL OR privacy_level IN ('public', 'internal', 'sensitive', 'secret'));

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS reversibility TEXT DEFAULT NULL
    CONSTRAINT chk_memory_reversibility CHECK (reversibility IS NULL OR reversibility IN ('high', 'medium', 'low'));

-- ============================================================================
-- 3. Governance columns
-- ============================================================================

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS requires_888 BOOLEAN DEFAULT FALSE;

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS can_authorize_action BOOLEAN DEFAULT FALSE;

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS memory_status TEXT DEFAULT 'active'
    CONSTRAINT chk_memory_status CHECK (memory_status IS NULL OR memory_status IN ('active', 'quarantined', 'sealed', 'tombstoned', 'revoked'));

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS supersedes_id UUID DEFAULT NULL;

-- ============================================================================
-- 4. Virtue receipt columns
-- ============================================================================

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS virtue_amanah TEXT DEFAULT NULL
    CONSTRAINT chk_virtue_amanah CHECK (virtue_amanah IS NULL OR virtue_amanah IN ('PASS', 'FAIL', 'DEFER'));

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS virtue_beradab TEXT DEFAULT NULL
    CONSTRAINT chk_virtue_beradab CHECK (virtue_beradab IS NULL OR virtue_beradab IN ('PASS', 'FAIL', 'DEFER'));

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS virtue_berhikmah TEXT DEFAULT NULL
    CONSTRAINT chk_virtue_berhikmah CHECK (virtue_berhikmah IS NULL OR virtue_berhikmah IN ('PASS', 'FAIL', 'DEFER'));

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS virtue_berakal TEXT DEFAULT NULL
    CONSTRAINT chk_virtue_berakal CHECK (virtue_berakal IS NULL OR virtue_berakal IN ('PASS', 'FAIL', 'DEFER'));

-- ============================================================================
-- 5. Indexes for governance queries
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_memory_m_tier
    ON memory_store(m_tier)
    WHERE m_tier IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_memory_status
    ON memory_store(memory_status)
    WHERE memory_status IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_memory_source_type
    ON memory_store(source_type)
    WHERE source_type IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_memory_can_authorize
    ON memory_store(can_authorize_action)
    WHERE can_authorize_action = TRUE;

CREATE INDEX IF NOT EXISTS idx_memory_supersedes
    ON memory_store(supersedes_id)
    WHERE supersedes_id IS NOT NULL;

-- ============================================================================
-- 6. Comments (governance documentation)
-- ============================================================================

COMMENT ON COLUMN memory_store.memory_intent IS
    'Why this memory exists: preference, fact, verdict, case_law, identity, authority, operational, emotional, project';

COMMENT ON COLUMN memory_store.niat IS
    'Moral intent behind this memory — the why, not the what';

COMMENT ON COLUMN memory_store.source_type IS
    'Provenance: user_direct, tool_observed, file_evidence, web_evidence, inference, agent_generated';

COMMENT ON COLUMN memory_store.m_tier IS
    'Memory risk tier: M0 (ephemeral) to M4 (sealed constitutional). Computed, not caller-set.';

COMMENT ON COLUMN memory_store.can_authorize_action IS
    'HARD DEFAULT FALSE. Memory may not authorize action at storage time. Authority granted at recall by judge.';

COMMENT ON COLUMN memory_store.memory_status IS
    'Lifecycle: active, quarantined, sealed, tombstoned, revoked';

COMMENT ON COLUMN memory_store.virtue_amanah IS
    'Trustworthiness gate result: PASS, FAIL, DEFER';

COMMENT ON COLUMN memory_store.virtue_beradab IS
    'Proper conduct gate result: PASS, FAIL, DEFER';

COMMENT ON COLUMN memory_store.virtue_berhikmah IS
    'Wisdom gate result: PASS, FAIL, DEFER';

COMMENT ON COLUMN memory_store.virtue_berakal IS
    'Reason gate result: PASS, FAIL, DEFER';

-- ============================================================================
-- 7. Backfill legacy records with safe defaults
-- ============================================================================

UPDATE memory_store
SET memory_status = 'active'
WHERE memory_status IS NULL;

UPDATE memory_store
SET can_authorize_action = FALSE
WHERE can_authorize_action IS NULL;

UPDATE memory_store
SET m_tier = 'M1'
WHERE m_tier IS NULL AND tier IN ('canon', 'canonical');

UPDATE memory_store
SET m_tier = 'M0'
WHERE m_tier IS NULL AND tier = 'ephemeral';

UPDATE memory_store
SET m_tier = 'M4'
WHERE m_tier IS NULL AND tier = 'sacred';

RAISE NOTICE 'Migration 004_memory_governance_v2 complete.';
