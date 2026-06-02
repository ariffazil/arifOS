-- ═══════════════════════════════════════════════════════════════════════════
-- F13 RATIFIED — 2026-06-03 — s000.constitutional_floors schema extension
-- Migration file: 20260603012600_add_floor_type_columns.sql
-- DITEMPA BUKAN DIBEI — Forged, Not Given
-- ═══════════════════════════════════════════════════════════════════════════
-- Sovereign sign-off: Muhammad Arif bin Fazil · Q1-Q6 + F12 ratified
-- F13 RATIFICATION epoch: 2026-06-03T01:26:00+08:00 (≈ 2026-06-02T17:26:00Z)
-- Wraps ALTER + UPDATE in single transaction for atomicity
-- ═══════════════════════════════════════════════════════════════════════════
--
-- RATIFIED AXES (orthogonal to enforcement_level):
--   HARD    (9): F1, F2, F4, F7, F9, F10, F11, F12, F13
--   SOFT    (2): F5, F6
--   DERIVED (2): F3, F8
--
-- ENFORCEMENT LEVEL UNCHANGED: blocking/required column preserved
-- CANON_NAME = DB name per Q6 strict reading (no alias overrides)
-- ═══════════════════════════════════════════════════════════════════════════

BEGIN;

-- 1. ADD NEW COLUMNS (additive only; enforcement_level UNCHANGED)
ALTER TABLE s000.constitutional_floors
  ADD COLUMN IF NOT EXISTS floor_type   TEXT,            -- HARD | SOFT | DERIVED
  ADD COLUMN IF NOT EXISTS canon_name   TEXT,            -- canon doc name (mirrors DB name per Q6)
  ADD COLUMN IF NOT EXISTS patched_at   TIMESTAMPTZ,     -- ratify timestamp
  ADD COLUMN IF NOT EXISTS patch_note   TEXT,            -- F13 reference
  ADD COLUMN IF NOT EXISTS patched_by   TEXT;            -- sovereign

-- 2. ENCODE RATIFIED FLOOR_TYPE (orthogonal to enforcement_level)
UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'AMANAH',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F1';

UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'TRUTH',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F2';

UPDATE s000.constitutional_floors SET
  floor_type = 'DERIVED', canon_name = 'WITNESS',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F3';

UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'CLARITY',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F4';

UPDATE s000.constitutional_floors SET
  floor_type = 'SOFT',    canon_name = 'PEACE2',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F5';

UPDATE s000.constitutional_floors SET
  floor_type = 'SOFT',    canon_name = 'EMPATHY',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F6';

UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'HUMILITY',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F7';

UPDATE s000.constitutional_floors SET
  floor_type = 'DERIVED', canon_name = 'GENIUS',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F8';

UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'ANTIHANTU',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F9';

UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'ONTOLOGY',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F10';

UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'AUTH',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F11';

UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'INJECTION',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F12';

UPDATE s000.constitutional_floors SET
  floor_type = 'HARD',    canon_name = 'SOVEREIGN',
  patched_at = '2026-06-02T17:27:00Z',
  patch_note = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by = 'Muhammad Arif bin Fazil'
WHERE id = 'F13';

COMMIT;

-- ═══════════════════════════════════════════════════════════════════════════
-- POST-MIGRATION VERIFICATION (read-only, idempotent)
-- Expected: 13 rows, 9 HARD + 2 SOFT + 2 DERIVED, enforcement_level UNCHANGED
-- ═══════════════════════════════════════════════════════════════════════════
-- SELECT
--   floor_type, COUNT(*) AS n
-- FROM s000.constitutional_floors
-- GROUP BY floor_type
-- ORDER BY floor_type;
--
-- Expected:
--   DERIVED | 2
--   HARD    | 9
--   SOFT    | 2
-- ═══════════════════════════════════════════════════════════════════════════
