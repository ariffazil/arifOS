-- Migration: 002_memory_contradiction_v1.sql
-- Phase 1a: F4 Contradiction Handling
--
-- Adds:
--   - entity_tags (F4 categorical anchors for multi-hop query)
--   - temporal_marker (active | historical | unknown)
--   - superseded_by / superseded_at (supersession lineage)
--   - distillation_status / distillation_metadata (Phoenix-72 extension)
--   - memory_contradictions table (T1/T2/T3 conflict tracking)
--
-- F2 Gate: recorded_at >= valid_at (enforced at application level, not DB level)
-- F4 Clarity: entity_tags format = CATEGORY:VALUE (e.g. ORG:PETRONAS, GEO:Sabah Basin)
-- F10 Ontology: supersession lineage preserves epistemic continuity
--
-- Idempotent: uses ADD COLUMN IF NOT EXISTS / CREATE TABLE IF NOT EXISTS
-- Run order: after 001_memory_schema (if exists, otherwise standalone)
--
-- DITEMPA BUKAN DIBERI — Forged, Not Given

-- ============================================================================
-- 1. memory_store: new columns for F4 + contradiction handling
-- ============================================================================

ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS entity_tags TEXT[] DEFAULT NULL;

ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS temporal_marker VARCHAR(20) DEFAULT 'unknown';

ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS superseded_by UUID DEFAULT NULL;

ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS superseded_at TIMESTAMPTZ DEFAULT NULL;

ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS distillation_status VARCHAR(20) DEFAULT NULL;

ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS distillation_metadata JSONB DEFAULT NULL;

-- ============================================================================
-- 2. memory_contradictions: explicit contradiction log (F2/F4 audit trail)
-- ============================================================================

CREATE TABLE IF NOT EXISTS memory_contradictions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id_new           UUID NOT NULL,
    memory_id_old           UUID NOT NULL,
    conflict_type           VARCHAR(10) NOT NULL,          -- T1 | T2 | T3
    entity_pair             TEXT NOT NULL,                -- e.g. "ORG:PETRONAS:GEO:Basin C"
    signal                  VARCHAR(50) NOT NULL,         -- human-readable conflict signal
    confidence              FLOAT DEFAULT 0.0,            -- extraction confidence
    resolution              VARCHAR(20) NOT NULL,          -- supersede | merge | escalate | retire | void
    resolved_by             TEXT DEFAULT 'system',        -- system | actor_id
    resolved_at             TIMESTAMPTZ DEFAULT NOW(),
    metadata                JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contradictions_entity_pair
    ON memory_contradictions(entity_pair);

CREATE INDEX IF NOT EXISTS idx_contradictions_memory_new
    ON memory_contradictions(memory_id_new);

CREATE INDEX IF NOT EXISTS idx_contradictions_memory_old
    ON memory_contradictions(memory_id_old);

-- Index for supersession chain queries
CREATE INDEX IF NOT EXISTS idx_memory_superseded_by
    ON memory_store(superseded_by)
    WHERE superseded_by IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_memory_temporal_marker
    ON memory_store(temporal_marker)
    WHERE temporal_marker IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_memory_entity_tags
    ON memory_store USING GIN(entity_tags)
    WHERE entity_tags IS NOT NULL;

-- ============================================================================
-- 3. Comments (F2/F4/F10 governance documentation)
-- ============================================================================

COMMENT ON COLUMN memory_store.entity_tags IS
    'F4/Clarity: Extracted categorical anchors for multi-hop query. '
    'Format: CATEGORY:VALUE (e.g. ORG:PETRONAS, GEO:Sabah Basin, TECH:Seismic). '
    'Enables filtered vector search by entity type.';

COMMENT ON COLUMN memory_store.temporal_marker IS
    'F4: Temporal status of entity relationships. '
    'active=current relationship; historical=superseded by newer fact; '
    'unknown=no temporal signal in source text. '
    'Derived from F4 extraction + supersession events.';

COMMENT ON COLUMN memory_store.superseded_by IS
    'F10/Ontology: UUID of the memory entry that superseded this one. '
    'Used to build supersession chains for temporal queries. '
    'NULL = not superseded.';

COMMENT ON COLUMN memory_store.superseded_at IS
    'F10/Ontology: Timestamp when this entry was superseded (world-time of the superseding entry). '
    'Used to reconstruct what was known at time T.';

COMMENT ON COLUMN memory_store.distillation_status IS
    'Phoenix-72 extended lifecycle: pending | distilled | sealed | void | prune | contradiction_hold. '
    'distilled = transformed from episodic to semantic (via distillation pipeline). '
    'contradiction_hold = flagged for manual resolution.';

COMMENT ON COLUMN memory_store.distillation_metadata IS
    'Phoenix-72 + F4: JSON blob with distillation context. '
    'Contains: source_episodes[], distilled_fact, confidence, distillation_type, '
    'original_tier, constitutional_hash.';

COMMENT ON TABLE memory_contradictions IS
    'F2/F4: Explicit contradiction log for audit trail. '
    'Records T1 (direct negation), T2 (scope change), T3 (entity merge/split) conflicts. '
    'F2: Ensures no fabricated temporal truth — contradictions are surfaced, not silently resolved.';

COMMENT ON COLUMN memory_contradictions.conflict_type IS
    'T1 = Direct negation (Fact X and NOT-X for same entity); '
    'T2 = Scope change (cardinality change without explicit negation); '
    'T3 = Entity merge/split (identity period changes).';

COMMENT ON COLUMN memory_contradictions.resolution IS
    'supersede = newer valid_at wins; older marked historical. '
    'merge = both stored with valid_at ranges. '
    'escalate = neither stored; flagged for Arif review. '
    'retire = old entry marked retired; new stored. '
    'void = both flagged contradiction_hold; requires manual resolution.';

-- ============================================================================
-- 4. Verify
-- ============================================================================

DO $$
BEGIN
    -- Verify columns exist
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'memory_store' AND column_name = 'entity_tags'
    ), 'entity_tags column missing';
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'memory_store' AND column_name = 'temporal_marker'
    ), 'temporal_marker column missing';
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'memory_store' AND column_name = 'superseded_by'
    ), 'superseded_by column missing';
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'memory_store' AND column_name = 'distillation_status'
    ), 'distillation_status column missing';
    -- Verify table exists
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'memory_contradictions'
    ), 'memory_contradictions table missing';
    RAISE NOTICE 'Migration 002_memory_contradiction_v1: OK';
END $$;

-- DITEMPA BUKAN DIBERI — Forged, Not Given
