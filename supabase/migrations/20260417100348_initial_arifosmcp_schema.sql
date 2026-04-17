-- ============================================================
-- arifOS Schema v1.0 — Initial Migration
-- ============================================================

-- VAULT999: Immutable seal ledger
-- append-only enforced via trigger below
CREATE TABLE IF NOT EXISTS arifosmcp_vault_seals (
  id            BIGSERIAL PRIMARY KEY,
  seal_id       TEXT NOT NULL UNIQUE,
  agent_id      TEXT NOT NULL,
  action        TEXT NOT NULL,
  payload       JSONB NOT NULL DEFAULT '{}',
  confidence    NUMERIC(4,3),
  epoch         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- WELL state: persistent agent/session state
-- replaces /root/WELL/state.json
CREATE TABLE IF NOT EXISTS arifosmcp_well_states (
  id            BIGSERIAL PRIMARY KEY,
  agent_id      TEXT NOT NULL,
  state_key     TEXT NOT NULL,
  state_value   JSONB NOT NULL DEFAULT '{}',
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(agent_id, state_key)
);

-- Tool call audit log
CREATE TABLE IF NOT EXISTS arifosmcp_tool_calls (
  id            BIGSERIAL PRIMARY KEY,
  tool_name     TEXT NOT NULL,
  agent_id      TEXT,
  input_hash    TEXT,
  result_code   TEXT,
  duration_ms   INTEGER,
  epoch         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Canon records: governance decisions, F13 votes, holds
CREATE TABLE IF NOT EXISTS arifosmcp_canon_records (
  id            BIGSERIAL PRIMARY KEY,
  record_type   TEXT NOT NULL,
  reference_id  TEXT,
  body          JSONB NOT NULL DEFAULT '{}',
  verdict       TEXT,
  witness       JSONB,
  epoch         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- WEALTH vault: transaction ledger
CREATE TABLE IF NOT EXISTS wealth_transactions (
  id            BIGSERIAL PRIMARY KEY,
  tx_type       TEXT NOT NULL,
  asset         TEXT,
  amount        NUMERIC,
  currency      TEXT DEFAULT 'MYR',
  metadata      JSONB NOT NULL DEFAULT '{}',
  epoch         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- WEALTH snapshots: portfolio state at point in time
CREATE TABLE IF NOT EXISTS wealth_portfolio_snapshots (
  id            BIGSERIAL PRIMARY KEY,
  snapshot_ts   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  holdings      JSONB NOT NULL DEFAULT '{}',
  total_value   NUMERIC,
  currency      TEXT DEFAULT 'MYR'
);

-- ============================================================
-- Append-only enforcement on vault_seals
-- CLAIM: immutability is NOT automatic — this trigger enforces it
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

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_well_states_agent ON arifosmcp_well_states(agent_id);
CREATE INDEX IF NOT EXISTS idx_vault_seals_agent ON arifosmcp_vault_seals(agent_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_epoch ON arifosmcp_tool_calls(epoch DESC);
CREATE INDEX IF NOT EXISTS idx_canon_records_type ON arifosmcp_canon_records(record_type);
