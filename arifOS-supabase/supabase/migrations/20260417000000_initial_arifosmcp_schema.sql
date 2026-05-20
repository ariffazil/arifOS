-- ============================================================
-- arifOS Supabase Migration — Initial Schema
-- Version: 1.0.0
-- Date: 2026-04-17
-- Author: A-FORGE Agent (arifOS constitutional runtime)
-- Purpose: Replace all /root/... and /tmp/... JSON state files
--          with proper Postgres-backed persistent layer
-- ============================================================
-- Migration ID: 20260417000000
-- Run with: supabase db push
-- Dry run first: supabase db push --dry-run
-- ============================================================

-- ── VAULT999: Immutable seal ledger ────────────────────────
CREATE TABLE IF NOT EXISTS arifosmcp_vault_seals (
  id                         BIGSERIAL PRIMARY KEY,
  seal_id                     TEXT NOT NULL UNIQUE,
  session_id                  TEXT NOT NULL,
  verdict                     TEXT NOT NULL,
  timestamp                   TIMESTAMPTZ NOT NULL,
  -- Spec v2.0 Merkle fields (required for chain verification)
  record_id                   TEXT,
  prev_hash                   TEXT,
  hashofinput                 TEXT,
  -- Constitutional telemetry
  telemetrysnapshot           JSONB,
  floors_triggered            TEXT[],
  irreversibilityacknowledged BOOLEAN DEFAULT false,
  -- Content
  task                        TEXT,
  final_text                  TEXT,
  turn_count                  INTEGER DEFAULT 0,
  profile_name                TEXT,
  -- Full record preserved as JSONB for complete reconstruction
  data                        JSONB NOT NULL DEFAULT '{}',
  created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_vault_seals_session    ON arifosmcp_vault_seals(session_id);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_vault_seals_verdict    ON arifosmcp_vault_seals(verdict);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_vault_seals_timestamp  ON arifosmcp_vault_seals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_vault_seals_record_id  ON arifosmcp_vault_seals(record_id);

-- Append-only enforcement (immutability NOT automatic — trigger enforces it)
CREATE OR REPLACE FUNCTION enforce_vault_seal_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'arifosmcp_vault_seals is append-only. UPDATE and DELETE are forbidden.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_arifosmcp_vault_seal_mutation
  BEFORE UPDATE OR DELETE ON arifosmcp_vault_seals
  FOR EACH ROW EXECUTE FUNCTION enforce_vault_seal_immutability();

-- ── AGENT SESSIONS (replaces /root/WELL/state.json) ─────────
CREATE TABLE IF NOT EXISTS arifosmcp_sessions (
  id              BIGSERIAL PRIMARY KEY,
  session_id      TEXT NOT NULL UNIQUE,
  agent_id        TEXT NOT NULL,
  initiated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  risk_tier       TEXT DEFAULT 'medium',
  declared_intent TEXT DEFAULT '',
  final_verdict   TEXT,
  closed_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_sessions_agent     ON arifosmcp_sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_sessions_initiated  ON arifosmcp_sessions(initiated_at DESC);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_sessions_session_id ON arifosmcp_sessions(session_id);

-- ── TOOL CALL AUDIT LOG ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS arifosmcp_tool_calls (
  id              BIGSERIAL PRIMARY KEY,
  run_id          TEXT,
  session_id      TEXT NOT NULL,
  tool_name       TEXT NOT NULL,
  organ           TEXT,
  input_hash      TEXT,
  output_hash     TEXT,
  tool_args       JSONB,
  tool_result     TEXT,
  duration_ms     INTEGER DEFAULT 0,
  floor_triggered TEXT[],
  verdict         TEXT NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_tool_calls_session ON arifosmcp_tool_calls(session_id);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_tool_calls_tool    ON arifosmcp_tool_calls(tool_name);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_tool_calls_created  ON arifosmcp_tool_calls(created_at DESC);

-- ── CANON RECORDS (ARCHIVIST ADR ledger — every SEAL writes here)
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

CREATE INDEX IF NOT EXISTS idx_arifosmcp_canon_records_adr       ON arifosmcp_canon_records(adr_id);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_canon_records_session  ON arifosmcp_canon_records(session_id);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_canon_records_agent    ON arifosmcp_canon_records(agent_id);

-- ── APPROVAL TICKETS (888_HOLD queue) ──────────────────────
CREATE TABLE IF NOT EXISTS arifosmcp_approval_tickets (
  id              BIGSERIAL PRIMARY KEY,
  ticket_id       TEXT NOT NULL UNIQUE,
  session_id      TEXT NOT NULL,
  status          TEXT NOT NULL,
  risk_level      TEXT NOT NULL,
  intent_model    TEXT NOT NULL,
  domain          TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  data            JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_approval_tickets_session ON arifosmcp_approval_tickets(session_id);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_approval_tickets_status  ON arifosmcp_approval_tickets(status);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_approval_tickets_risk    ON arifosmcp_approval_tickets(risk_level);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_approval_tickets_created ON arifosmcp_approval_tickets(created_at DESC);

-- ── CONSTITUTIONAL FLOOR RULES (F1–F13 thresholds) ──────────
CREATE TABLE IF NOT EXISTS arifosmcp_floor_rules (
  id              BIGSERIAL PRIMARY KEY,
  floor_id        TEXT NOT NULL UNIQUE,
  code            TEXT NOT NULL,
  name            TEXT NOT NULL,
  type            TEXT NOT NULL,
  description     TEXT,
  seal_threshold  NUMERIC,
  void_threshold   NUMERIC,
  active          BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_floor_rules_code ON arifosmcp_floor_rules(code);

-- ── AGENT TELEMETRY (MerkleV3 source rows — thermodynamic metrics)
CREATE TABLE IF NOT EXISTS arifosmcp_agent_telemetry (
  id              BIGSERIAL PRIMARY KEY,
  epoch           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  session_id      TEXT,
  agent_id        TEXT,
  ds              NUMERIC,
  peace2          NUMERIC,
  kappa_r         NUMERIC,
  shadow          NUMERIC,
  confidence      NUMERIC,
  psi_le          NUMERIC,
  verdict         TEXT,
  witness_human   NUMERIC,
  witness_ai      NUMERIC,
  witness_earth   NUMERIC,
  qdf             TEXT,
  prev_hash       TEXT,
  row_hash        TEXT
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_telemetry_epoch    ON arifosmcp_agent_telemetry(epoch DESC);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_telemetry_session  ON arifosmcp_agent_telemetry(session_id);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_telemetry_row_hash ON arifosmcp_agent_telemetry(row_hash);

-- ── DAILY MERKLE ROOTS (MerkleV3 daily anchor) ───────────────
CREATE TABLE IF NOT EXISTS arifosmcp_daily_roots (
  id              BIGSERIAL PRIMARY KEY,
  root_date       DATE NOT NULL UNIQUE,
  row_count       INTEGER NOT NULL DEFAULT 0,
  merkle_root     TEXT NOT NULL,
  anchored        BOOLEAN DEFAULT false,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_daily_roots_date ON arifosmcp_daily_roots(root_date);

-- ── WEALTH: Transaction ledger ──────────────────────────────
CREATE TABLE IF NOT EXISTS arifosmcp_transactions (
  id              BIGSERIAL PRIMARY KEY,
  tx_type         TEXT NOT NULL,
  asset           TEXT,
  amount          NUMERIC,
  currency        TEXT DEFAULT 'MYR',
  metadata        JSONB NOT NULL DEFAULT '{}',
  epoch           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_transactions_type   ON arifosmcp_transactions(tx_type);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_transactions_asset  ON arifosmcp_transactions(asset);
CREATE INDEX IF NOT EXISTS idx_arifosmcp_transactions_epoch  ON arifosmcp_transactions(epoch DESC);

-- ── WEALTH: Portfolio snapshots ─────────────────────────────
CREATE TABLE IF NOT EXISTS arifosmcp_portfolio_snapshots (
  id              BIGSERIAL PRIMARY KEY,
  snapshot_ts     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  holdings        JSONB NOT NULL DEFAULT '{}',
  total_value     NUMERIC,
  currency        TEXT DEFAULT 'MYR'
);

CREATE INDEX IF NOT EXISTS idx_arifosmcp_snapshots_ts ON arifosmcp_portfolio_snapshots(snapshot_ts DESC);

-- ── MIGRATION LEDGER (managed by Supabase CLI — do not edit) ─
-- Table: supabase_migrations.schema_migrations
-- Created automatically by supabase db push