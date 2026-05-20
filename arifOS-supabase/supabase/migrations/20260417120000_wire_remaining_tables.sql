-- ============================================================
-- VAULT999 Completion Migration
-- Wires: sessions, tool_calls, canon_records, floor_rules,
--        agent_telemetry + drops duplicate trigger
-- ============================================================

-- Drop the duplicate legacy immutability trigger
DROP TRIGGER IF EXISTS no_vault_seal_mutation ON arifosmcp_vault_seals;

-- ============================================================
-- SESSIONS — track session open/close per agent
-- ============================================================
ALTER TABLE arifosmcp_sessions
  ADD COLUMN IF NOT EXISTS session_id TEXT NOT NULL DEFAULT gen_random_uuid()::text,
  ADD COLUMN IF NOT EXISTS agent_id TEXT,
  ADD COLUMN IF NOT EXISTS opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ADD COLUMN IF NOT EXISTS closed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS anchor_seal_id TEXT,
  ADD COLUMN IF NOT EXISTS close_seal_id TEXT,
  ADD COLUMN IF NOT EXISTS state_snapshot JSONB DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS verdict TEXT;

CREATE INDEX IF NOT EXISTS idx_sessions_agent
  ON arifosmcp_sessions(agent_id);

CREATE INDEX IF NOT EXISTS idx_sessions_opened
  ON arifosmcp_sessions(opened_at DESC);

-- ============================================================
-- TOOL_CALLS — per-tool audit log
-- ============================================================
ALTER TABLE arifosmcp_tool_calls
  ADD COLUMN IF NOT EXISTS session_id TEXT,
  ADD COLUMN IF NOT EXISTS tool_name TEXT,
  ADD COLUMN IF NOT EXISTS agent_id TEXT,
  ADD COLUMN IF NOT EXISTS input_hash TEXT,
  ADD COLUMN IF NOT EXISTS result_code TEXT,
  ADD COLUMN IF NOT EXISTS duration_ms INTEGER,
  ADD COLUMN IF NOT EXISTS peace2 NUMERIC(4,3),
  ADD COLUMN IF NOT EXISTS error_msg TEXT,
  ADD COLUMN IF NOT EXISTS epoch TIMESTAMPTZ DEFAULT now();

CREATE INDEX IF NOT EXISTS idx_tool_calls_session
  ON arifosmcp_tool_calls(session_id);

CREATE INDEX IF NOT EXISTS idx_tool_calls_tool
  ON arifosmcp_tool_calls(tool_name);

CREATE INDEX IF NOT EXISTS idx_tool_calls_epoch
  ON arifosmcp_tool_calls(epoch DESC);

-- ============================================================
-- CANON_RECORDS — ARCHIVIST agent output: ADRs, F13 decisions
-- ============================================================
ALTER TABLE arifosmcp_canon_records
  ADD COLUMN IF NOT EXISTS record_type TEXT,
  ADD COLUMN IF NOT EXISTS reference_id TEXT,
  ADD COLUMN IF NOT EXISTS body JSONB DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS verdict TEXT,
  ADD COLUMN IF NOT EXISTS witness JSONB,
  ADD COLUMN IF NOT EXISTS epoch TIMESTAMPTZ DEFAULT now();

CREATE INDEX IF NOT EXISTS idx_canon_type
  ON arifosmcp_canon_records(record_type);

-- ============================================================
-- FLOOR_RULES — constitutional floor definitions in DB
-- Replaces hardcoded floors in Python
-- ============================================================
ALTER TABLE arifosmcp_floor_rules
  ADD COLUMN IF NOT EXISTS rule_id TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS rule_name TEXT NOT NULL,
  ADD COLUMN IF NOT EXISTS description TEXT,
  ADD COLUMN IF NOT EXISTS threshold NUMERIC,
  ADD COLUMN IF NOT EXISTS metric TEXT,
  ADD COLUMN IF NOT EXISTS action TEXT DEFAULT 'BLOCK',
  ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT true,
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now();

-- Seed the core constitutional floors
INSERT INTO arifosmcp_floor_rules
  (rule_id, rule_name, description, threshold, metric, action)
VALUES
  ('F01', 'peace2_minimum',     'Minimum peace² value for any agent action',      0.5,  'peace2',   'BLOCK'),
  ('F02', 'confidence_minimum', 'Minimum confidence for vault seal',               0.5,  'confidence','WARN'),
  ('F03', 'shadow_prohibition', 'Shadow state is constitutionally prohibited',     0.0,  'shadow',    'BLOCK'),
  ('F04', 'kappa_r_maximum',    'Maximum risk-resonance (kappa_r) before hold',   0.15, 'kappa_r',   'HOLD'),
  ('F05', 'psi_le_maximum',     'Maximum lateral entropy before intervention',     0.1,  'psi_le',    'WARN'),
  ('F13', 'human_veto',         'F13 human veto — sovereign override, always wins', NULL, 'human',   'VETO')
ON CONFLICT (rule_id) DO NOTHING;

-- ============================================================
-- AGENT_TELEMETRY — metabolic stream per agent action
-- metabolic_guard trigger already installed on this table
-- Adding index for time-series queries
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_telemetry_agent
  ON arifosmcp_agent_telemetry(agent_id);

CREATE INDEX IF NOT EXISTS idx_telemetry_epoch
  ON arifosmcp_agent_telemetry(epoch DESC);

CREATE INDEX IF NOT EXISTS idx_telemetry_metric
  ON arifosmcp_agent_telemetry(metric_name);
