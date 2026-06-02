-- ════════════════════════════════════════════════════════════════════════════════
-- F13 SOVEREIGN PATCH ENFORCEMENT TRIGGER
-- Date: 2026-06-03
-- Authority: F13 SOVEREIGN — Muhammad Arif bin Fazil
-- Purpose: Convert F13 from "human catches it" to "DB catches it"
-- Task: #1 of post-falsification operationalization
-- Reversible: DROP TRIGGER trg_f13_sovereign_patch ON s000.constitutional_floors
-- ════════════════════════════════════════════════════════════════════════════════

BEGIN;

CREATE OR REPLACE FUNCTION s000.enforce_sovereign_patch()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = s000, public
AS $$
BEGIN
  -- F13 enforcement: only the sovereign may patch constitutional floors.
  -- Triggers on BEFORE INSERT OR UPDATE.
  -- The current sovereign per F13 RATIFICATION 2026-06-03.
  IF NEW.patched_by IS DISTINCT FROM 'Muhammad Arif bin Fazil' THEN
    RAISE EXCEPTION 'F13 VIOLATION: s000.constitutional_floors.patched_by must be the sovereign. Got: %',
      NEW.patched_by
      USING ERRCODE = 'integrity_constraint_violation';
  END IF;

  -- F4 CLARITY: validate floor_type if present.
  -- Ratified types per F13 RATIFICATION 2026-06-03: HARD, SOFT, DERIVED.
  -- VETO is reserved (constitutional_kernel.py supports it; not in DB yet).
  IF NEW.floor_type IS NOT NULL
     AND NEW.floor_type NOT IN ('HARD', 'SOFT', 'DERIVED', 'VETO') THEN
    RAISE EXCEPTION 'F4 CLARITY VIOLATION: floor_type=%. Must be one of HARD, SOFT, DERIVED, VETO.',
      NEW.floor_type
      USING ERRCODE = 'invalid_parameter_value';
  END IF;

  RETURN NEW;
END;
$$;

-- Drop existing trigger if present (idempotent).
DROP TRIGGER IF EXISTS trg_f13_sovereign_patch ON s000.constitutional_floors;

CREATE TRIGGER trg_f13_sovereign_patch
BEFORE INSERT OR UPDATE ON s000.constitutional_floors
FOR EACH ROW EXECUTE FUNCTION s000.enforce_sovereign_patch();

-- F11 audit trail: anyone reading pg_description sees who authorized this.
COMMENT ON TRIGGER trg_f13_sovereign_patch ON s000.constitutional_floors IS
'F13 SOVEREIGN PATCH ENFORCEMENT — sealed 2026-06-03 by Muhammad Arif bin Fazil. '
'Blocks any INSERT or UPDATE on s000.constitutional_floors where patched_by != sovereign. '
'Also validates floor_type ∈ {HARD, SOFT, DERIVED, VETO}. '
'Conversion of F13 invariant from social contract to DB-enforced rule. '
'Task #1 of post-falsification operationalization. '
'Reversible: DROP TRIGGER trg_f13_sovereign_patch ON s000.constitutional_floors;';

COMMIT;
