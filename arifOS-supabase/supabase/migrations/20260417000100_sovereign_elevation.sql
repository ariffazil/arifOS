-- ============================================================
-- arifOS VAULT999 Consolidation & Elevation Migration
-- Version: 2.1.0 (Tall Architecture Intelligence)
-- ============================================================

-- 1. Correct the Metabolic Guard for Tall Table
CREATE OR REPLACE FUNCTION validate_metabolic_stability()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if we are inserting Peace² and if it violates thresholds
    IF (NEW.metric_name = 'peace2' AND NEW.value < 0.5) THEN
        RAISE EXCEPTION 'Constitutional Violation: Peace² dropped below critical threshold (0.5). Action Blocked.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Create the Sovereign Unified View (Aligned with Tall schema)
CREATE OR REPLACE VIEW sovereign_audit_trail AS
SELECT 
    'SEAL' as entry_type,
    seal_id as id,
    epoch as ts,
    agent_id as actor,
    action as summary,
    payload as details
FROM arifosmcp_vault_seals
UNION ALL
SELECT 
    'TELEMETRY' as entry_type,
    id::text as id,
    epoch as ts,
    agent_id as actor,
    metric_name || ': ' || value::text as summary,
    tags as details
FROM arifosmcp_agent_telemetry;

-- 3. Ensure Missing Dimension Tables (Projected State)
CREATE TABLE IF NOT EXISTS arifosmcp_canon_records (
  id              BIGSERIAL PRIMARY KEY,
  adr_id          TEXT NOT NULL UNIQUE,
  title           TEXT,
  decision        TEXT,
  rationale       TEXT,
  agent_id        TEXT,
  session_id      TEXT,
  epoch           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sealed_by       TEXT NOT NULL DEFAULT 'Muhammad Arif bin Fazil',
  payload         JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS arifosmcp_tool_calls (
  id              BIGSERIAL PRIMARY KEY,
  session_id      TEXT NOT NULL,
  tool_name       TEXT NOT NULL,
  tool_args       JSONB,
  tool_result     TEXT,
  duration_ms     INTEGER DEFAULT 0,
  verdict         TEXT NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
