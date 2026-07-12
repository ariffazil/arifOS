-- ============================================================
-- Constitutional Memory (Δ Axis 3)
-- ============================================================
-- The missing depth axis: Memory → Moral Anchor → Constitutional Recall.
--
-- Without Δ in memory, the system recalls facts.
-- With Δ in memory, the system recalls meaning.
--
-- "Love is not what you feel. It's what you refuse to forget."
--
-- This migration adds the Δ triplet to memory_store:
--   value_anchor     — which Δ values this memory serves
--   floor_constraint — which F1-F13 floors govern recall
--   care_provenance  — why this was remembered (human commitment)
--
-- Selective application rule:
--   If a memory is governed by a floor, it MUST carry that floor's geometry.
--
-- Author: arifOS Constitutional Memory Layer
-- Date:   2026-07-11
-- Axis:   Vertical × Horizontal × DEPTH
-- ============================================================

-- ─────────────────────────────────────────────────────────
-- STEP 1: Add Δ columns to memory_store
-- ─────────────────────────────────────────────────────────
ALTER TABLE memory_store
  ADD COLUMN IF NOT EXISTS value_anchor TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS floor_constraint TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS care_provenance TEXT;

-- ─────────────────────────────────────────────────────────
-- STEP 2: Indexes for constitutional recall
-- ─────────────────────────────────────────────────────────
-- GIN indexes for array containment queries:
--   WHERE 'F6' = ANY(floor_constraint)
--   WHERE 'dignity' = ANY(value_anchor)

CREATE INDEX IF NOT EXISTS idx_memory_store_floor_constraint
  ON memory_store USING GIN (floor_constraint);

CREATE INDEX IF NOT EXISTS idx_memory_store_value_anchor
  ON memory_store USING GIN (value_anchor);

-- ─────────────────────────────────────────────────────────
-- STEP 3: Comment the columns
-- ─────────────────────────────────────────────────────────
COMMENT ON COLUMN memory_store.value_anchor IS
  'Δ Axis 3: Which human values this memory serves (dignity, protection, sovereignty, truth, witness, patience, reversibility, clarity, empathy, genius)';

COMMENT ON COLUMN memory_store.floor_constraint IS
  'Δ Axis 3: Which F1-F13 constitutional floors govern recall and use of this memory';

COMMENT ON COLUMN memory_store.care_provenance IS
  'Δ Axis 3: Why this was remembered — the human commitment that produced it. Not metadata. Meaning.';

-- ─────────────────────────────────────────────────────────
-- STEP 4: Backfill existing sealed memories
-- ─────────────────────────────────────────────────────────
-- Sealed verdicts and case_law memories are governed by floors.
-- They should carry Δ retroactively.
UPDATE memory_store
SET
  value_anchor = ARRAY['truth']::TEXT[],
  floor_constraint = ARRAY['F2', 'F11']::TEXT[],
  care_provenance = 'Backfilled: sealed memory carries truth + auditability by default'
WHERE memory_status = 'sealed'
  AND (value_anchor IS NULL OR value_anchor = '{}');

-- Governance-class memories are inherently floor-bound
UPDATE memory_store
SET
  value_anchor = ARRAY['sovereignty']::TEXT[],
  floor_constraint = ARRAY['F13']::TEXT[],
  care_provenance = 'Backfilled: governance memory carries sovereignty constraint'
WHERE memory_intent = 'governance'
  AND (value_anchor IS NULL OR value_anchor = '{}');

