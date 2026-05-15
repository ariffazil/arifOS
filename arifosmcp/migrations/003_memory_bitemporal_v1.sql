-- Migration: 003_memory_bitemporal_v1.sql
-- Phase 1d: Bi-temporal Schema for F2 Temporal Truth Enforcement
--
-- Adds:
--   - valid_at (TIMESTAMPTZ): World-time when the fact is true in the real world.
--     NULL = unknown (fact asserted without specific temporal anchor).
--   - recorded_at (TIMESTAMPTZ): System-time when the fact was recorded.
--     Defaults to created_at for backward compat.
--
-- F2 TRUTH Gate: valid_at <= recorded_at (world-time cannot be in the future
-- of recording time). Enforced at application level with a DB CHECK constraint
-- as backup. NULL valid_at is exempt (unknown world-time cannot be falsified).
--
-- Bitemporal model:
--   - valid_at  : When the fact was true in the world (source timestamp or inferred)
--   - recorded_at: When the fact was stored in this system
--   - created_at : Alias/backup for recorded_at (legacy column, kept for compat)
--
-- Use cases:
--   - "What did the system know at time T?"     → Query by recorded_at
--   - "What was true in the world at time T?"   → Query by valid_at
--   - "Show current facts"                     → valid_at <= now() AND recorded_at <= now()
--   - "Fact with future valid_at"               → REJECT (F2 violation)
--
-- DITEMPA BUKAN DIBERI — Forged, Not Given

-- ============================================================================
-- 1. Add valid_at — world-time of the factual claim
-- ============================================================================

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS valid_at TIMESTAMPTZ DEFAULT NULL;

-- ============================================================================
-- 2. Add recorded_at — explicit system-time of record creation
-- Default to created_at for existing rows (backward compat).
-- New writes should set recorded_at = created_at (or explicit if different).
-- ============================================================================

ALTER TABLE memory_store
    ADD COLUMN IF NOT EXISTS recorded_at TIMESTAMPTZ DEFAULT NULL;

-- Backfill recorded_at = created_at for existing rows (no change to semantics)
UPDATE memory_store
SET recorded_at = created_at
WHERE recorded_at IS NULL;

-- Make NOT NULL after backfill (new rows always get a value)
ALTER TABLE memory_store
    ALTER COLUMN recorded_at SET NOT NULL;

-- ============================================================================
-- 3. F2 CHECK constraint — valid_at cannot be after recorded_at
-- NULL valid_at is exempt: unknown world-time cannot be falsified.
-- ============================================================================

DO $$
BEGIN
    -- Only add if not exists (idempotent)
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_memory_store_valid_at'
    ) THEN
        ALTER TABLE memory_store
            ADD CONSTRAINT chk_memory_store_valid_at
            CHECK (
                valid_at IS NULL
                OR recorded_at IS NULL
                OR valid_at <= recorded_at
            );
        RAISE NOTICE 'Constraint chk_memory_store_valid_at added.';
    END IF;
END $$;

-- ============================================================================
-- 4. Indexes for bitemporal queries
-- ============================================================================

-- "What facts were known at time T?" (record-time queries)
CREATE INDEX IF NOT EXISTS idx_memory_recorded_at
    ON memory_store(recorded_at DESC)
    WHERE recorded_at IS NOT NULL;

-- "What was true in the world at time T?" (world-time queries)
CREATE INDEX IF NOT EXISTS idx_memory_valid_at
    ON memory_store(valid_at DESC)
    WHERE valid_at IS NOT NULL;

-- Composite: active facts (current in both timelines)
CREATE INDEX IF NOT EXISTS idx_memory_bitemporal_active
    ON memory_store(valid_at DESC, recorded_at DESC)
    WHERE valid_at IS NOT NULL AND recorded_at IS NOT NULL;

-- ============================================================================
-- 5. Comments (F2/F4 governance documentation)
-- ============================================================================

COMMENT ON COLUMN memory_store.valid_at IS
    'F2/TRUTH: World-time when the factual claim is true in the real world. '
    'Extracted from source timestamp or inferred from context. '
    'NULL = unknown (asserted fact without temporal anchor — cannot be falsified). '
    'F2 Gate: valid_at must be <= recorded_at (a fact cannot be known before it was true).';

COMMENT ON COLUMN memory_store.recorded_at IS
    'F2: System-time when this fact was stored in memory_store. '
    'Default: created_at (legacy). Represents the record-time timeline. '
    'Use with valid_at for bitemporal queries: '
    '  "What did we know at T?"      → WHERE recorded_at <= T '
    '  "What was true at T in world?" → WHERE valid_at <= T';

COMMENT ON CONSTRAINT chk_memory_store_valid_at ON memory_store IS
    'F2: World-time (valid_at) cannot be after system-time (recorded_at). '
    'Enforces: a fact cannot be recorded before it was true in the real world. '
    'NULL valid_at is exempt (unknown world-time cannot be falsified).';

-- ============================================================================
-- 6. Verify
-- ============================================================================

DO $$
BEGIN
    -- Verify columns exist
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'memory_store' AND column_name = 'valid_at'
    ), 'valid_at column missing';
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'memory_store' AND column_name = 'recorded_at'
    ), 'recorded_at column missing';
    -- Verify constraint exists
    ASSERT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_memory_store_valid_at'
    ), 'chk_memory_store_valid_at constraint missing';
    -- Verify not null on recorded_at
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'memory_store'
          AND column_name = 'recorded_at'
          AND is_nullable = 'NO'
    ), 'recorded_at should be NOT NULL';
    RAISE NOTICE 'Migration 003_memory_bitemporal_v1: OK';
END $$;

-- ============================================================================
-- DITEMPA BUKAN DIBERI — Forged, Not Given
