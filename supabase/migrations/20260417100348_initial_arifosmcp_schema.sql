-- ============================================================
-- arifOS Schema v1.0 — Initial Migration (HARDENED)
-- ============================================================

-- 1. VAULT999: Immutable seal ledger (MerkleV3 Support)
CREATE TABLE IF NOT EXISTS arifosmcp_vault_seals (
  id            BIGSERIAL PRIMARY KEY,
  record_id     UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  seal_id       TEXT NOT NULL UNIQUE,
  prev_hash     TEXT NOT NULL, -- MerkleV3 requirement
  agent_id      TEXT NOT NULL,
  action        TEXT NOT NULL,
  payload       JSONB NOT NULL DEFAULT '{}',
  confidence    NUMERIC(4,3),
  epoch         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. SESSIONS: Unified session state
CREATE TABLE IF NOT EXISTS arifosmcp_sessions (
  id            BIGSERIAL PRIMARY KEY,
  session_id    TEXT NOT NULL UNIQUE,
  actor_id      TEXT NOT NULL,
  status        TEXT DEFAULT 'active',
  risk_tier     TEXT DEFAULT 'medium',
  verdict       TEXT DEFAULT 'PENDING',
  telemetry     JSONB NOT NULL DEFAULT '{}',
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. TOOL CALLS: Enhanced Audit Log
CREATE TABLE IF NOT EXISTS arifosmcp_tool_calls (
  id              BIGSERIAL PRIMARY KEY,
  organ           TEXT NOT NULL, -- arifOS, GEOX, WEALTH
  session_id      TEXT,
  tool_name       TEXT NOT NULL,
  agent_id        TEXT,
  input_hash      TEXT,
  verdict         TEXT,
  floor_triggered TEXT,
  duration_ms     INTEGER,
  epoch           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. CANON RECORDS: Governance, ADRs, and Votes
CREATE TABLE IF NOT EXISTS arifosmcp_canon_records (
  id            BIGSERIAL PRIMARY KEY,
  record_type   TEXT NOT NULL, -- ADR, F13_VOTE, POLICY
  reference_id  TEXT, -- ADR link
  body          JSONB NOT NULL DEFAULT '{}',
  verdict       TEXT,
  witness       JSONB,
  sealed_by     TEXT,
  epoch         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. FLOOR RULES: Constitutional Constraints
CREATE TABLE IF NOT EXISTS arifosmcp_floor_rules (
  id            BIGSERIAL PRIMARY KEY,
  floor_code    TEXT NOT NULL UNIQUE, -- F1, F2...
  rule_name     TEXT NOT NULL,
  constraint_definition JSONB NOT NULL DEFAULT '{}',
  is_active     BOOLEAN DEFAULT TRUE,
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. AGENT TELEMETRY: Performance Metrics
CREATE TABLE IF NOT EXISTS arifosmcp_agent_telemetry (
  id            BIGSERIAL PRIMARY KEY,
  agent_id      TEXT NOT NULL,
  metric_name   TEXT NOT NULL,
  value         NUMERIC,
  tags          JSONB,
  epoch         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. DAILY ROOTS: Daily Merkle Anchors
CREATE TABLE IF NOT EXISTS arifosmcp_daily_roots (
  id            BIGSERIAL PRIMARY KEY,
  root_hash     TEXT NOT NULL UNIQUE,
  sealed_day    DATE NOT NULL UNIQUE DEFAULT CURRENT_DATE,
  event_count   INTEGER,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. WEALTH: Transaction Ledger
CREATE TABLE IF NOT EXISTS wealth_transactions (
  id            BIGSERIAL PRIMARY KEY,
  tx_type       TEXT NOT NULL,
  asset         TEXT,
  amount        NUMERIC,
  currency      TEXT DEFAULT 'MYR',
  metadata      JSONB NOT NULL DEFAULT '{}',
  epoch         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. PORTFOLIO SNAPSHOTS
CREATE TABLE IF NOT EXISTS arifosmcp_portfolio_snapshots (
  id            BIGSERIAL PRIMARY KEY,
  snapshot_ts   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  holdings      JSONB NOT NULL DEFAULT '{}',
  total_value   NUMERIC,
  currency      TEXT DEFAULT 'MYR'
);

-- 10. APPROVAL TICKETS: F13 Sovereign Veto
CREATE TABLE IF NOT EXISTS arifosmcp_approval_tickets (
  id            BIGSERIAL PRIMARY KEY,
  ticket_id     TEXT NOT NULL UNIQUE,
  action_plan   JSONB NOT NULL,
  human_verdict TEXT DEFAULT 'PENDING', -- APPROVED, REJECTED
  requested_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at   TIMESTAMPTZ
);

-- ============================================================
-- Append-only enforcement on vault_seals
-- ============================================================
CREATE OR REPLACE FUNCTION enforce_vault_seal_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'vault_seals is append-only. UPDATE and DELETE are forbidden.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_vault_seal_mutation
  BEFORE UPDATE OR DELETE ON arifosmcp_vault_seals
  FOR EACH ROW EXECUTE FUNCTION enforce_vault_seal_immutability();

-- Indexes
CREATE INDEX IF NOT EXISTS idx_v3_prev_hash ON arifosmcp_vault_seals(prev_hash);
CREATE INDEX IF NOT EXISTS idx_tool_calls_organ ON arifosmcp_tool_calls(organ);
CREATE INDEX IF NOT EXISTS idx_sessions_actor ON arifosmcp_sessions(actor_id);
