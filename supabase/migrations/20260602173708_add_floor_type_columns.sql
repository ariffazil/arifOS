-- ════════════════════════════════════════════════════════════════════════════════
-- arifOS Floor Classification Charter — F13 RATIFICATION 2026-06-03
-- Sovereign: Muhammad Arif bin Fazil
-- Migration author: omega-forge-agent (Ω) executing F13 directive
-- Epoch: 2026-06-03T01:34:00+08:00
-- Canonical commit time: 2026-06-02T17:27:00Z (UTC)
-- Source of truth: F13 RATIFICATION block (signed 2026-06-03)
-- ════════════════════════════════════════════════════════════════════════════════

BEGIN;

-- ── Migration A: ADD COLUMNS ────────────────────────────────────────────────────
ALTER TABLE s000.constitutional_floors
  ADD COLUMN IF NOT EXISTS floor_type  TEXT,
  ADD COLUMN IF NOT EXISTS canon_name  TEXT,
  ADD COLUMN IF NOT EXISTS patched_at  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS patch_note  TEXT,
  ADD COLUMN IF NOT EXISTS patched_by  TEXT;

-- ── Migration B: UPDATE 13 rows with F13-ratified values ───────────────────────
-- Q1: F3 WITNESS = DERIVED  (composite of F2 + F11)
UPDATE s000.constitutional_floors SET
  floor_type  = 'DERIVED',
  canon_name  = 'WITNESS',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'WITNESS';

-- Q2: F4 CLARITY = HARD  (enforcement_level=required = HOLD behaviour)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'CLARITY',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'CLARITY';

-- Q3: F5 PEACE2 = SOFT  (enforcement_level=blocking = VOID behaviour)
UPDATE s000.constitutional_floors SET
  floor_type  = 'SOFT',
  canon_name  = 'PEACE2',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'PEACE2';

-- F6 EMPATHY = SOFT  (post-fix reclassification ratified)
UPDATE s000.constitutional_floors SET
  floor_type  = 'SOFT',
  canon_name  = 'EMPATHY',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'EMPATHY';

-- Q4: F7 HUMILITY = HARD  (enforcement_level=required = HOLD behaviour)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'HUMILITY',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'HUMILITY';

-- Q5: F8 GENIUS = DERIVED  (composite of F2+F4+F7+F10)
UPDATE s000.constitutional_floors SET
  floor_type  = 'DERIVED',
  canon_name  = 'GENIUS',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'GENIUS';

-- F9 ANTIHANTU = HARD  (post-fix reclassification ratified; SOFT→HARD)
-- Note: canon_name = 'ANTIHANTU' (no hyphen, matches DB name column)
--       Python constant F9_ANTI_HANTU retained (underscore valid in Python)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'ANTIHANTU',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'ANTIHANTU';

-- F10 ONTOLOGY = HARD  (Q6: DB name canonical, not CONSCIENCE)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'ONTOLOGY',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'ONTOLOGY';

-- F11 AUTH = HARD  (Q6: DB name canonical, not AUDITABILITY)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'AUTH',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'AUTH';

-- F12 INJECTION = HARD  (F12 override: charter SOFT proposal was drafting artifact)
-- Note: canon_name = 'INJECTION' (DB name, not RESILIENCE)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'INJECTION',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'INJECTION';

-- F13 SOVEREIGN = HARD  (no change vs K000_LAW v2026.03.07)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'SOVEREIGN',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'SOVEREIGN';

-- F1 AMANAH = HARD  (no change vs K000_LAW v2026.03.07)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'AMANAH',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'AMANAH';

-- F2 TRUTH = HARD  (no change vs K000_LAW v2026.03.07)
UPDATE s000.constitutional_floors SET
  floor_type  = 'HARD',
  canon_name  = 'TRUTH',
  patched_at  = '2026-06-02T17:27:00Z',
  patch_note  = 'F13 ratification 2026-06-03 — floor_type + canon_name columns added per sovereign sign-off',
  patched_by  = 'Muhammad Arif bin Fazil'
WHERE name = 'TRUTH';

COMMIT;
