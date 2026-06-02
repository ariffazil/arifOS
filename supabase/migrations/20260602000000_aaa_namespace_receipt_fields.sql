-- ============================================================
-- arifOS Schema — AAA Namespace Receipt Fields
-- Migration: 20260602000000_aaa_namespace_receipt_fields.sql
-- Authority: AAA-HF doctrine v1.2, AAA_NAMESPACE_DOCTRINE.md
-- REPO=arifOS
-- ============================================================
-- Purpose: Make every constitutional receipt explicit about
-- which surface of AAA defined the law it was recorded under.
--
-- Without these fields, records say "this happened".
-- With these fields, records say "this happened, under version
-- v1.2 of the AAA-HF doctrine, citing floor F1 and F12,
-- and this is a constitutional_receipt — not just a log row."
--
-- Core insight: aaa_surface ≠ aaa_app_version.
--   aaa_surface is jurisdictional (AAA-HF / AAA-Cockpit).
--   aaa_doctrine_version is the law version in effect.
-- ============================================================

-- -----------------------------------------------
-- 1. arifosmcp_tool_calls — The Daily Constitutional Log
-- -----------------------------------------------
ALTER TABLE arifosmcp_tool_calls
  ADD COLUMN IF NOT EXISTS aaa_surface          TEXT    DEFAULT 'AAA-HF',
  ADD COLUMN IF NOT EXISTS aaa_doctrine_version TEXT,
  ADD COLUMN IF NOT EXISTS aaa_canon_refs       TEXT[],
  ADD COLUMN IF NOT EXISTS floor_refs           TEXT[],
  ADD COLUMN IF NOT EXISTS record_class         TEXT    DEFAULT 'constitutional_receipt';

COMMENT ON COLUMN arifosmcp_tool_calls.aaa_surface IS
  'Which AAA surface governed this record. Values: AAA-HF | AAA-Cockpit | AAA-Doctrine. Default: AAA-HF (doctrine corpus).';
COMMENT ON COLUMN arifosmcp_tool_calls.aaa_doctrine_version IS
  'Version of the AAA-HF doctrine corpus in effect when this record was written. Format: vMAJOR.MINOR (e.g. v1.2).';
COMMENT ON COLUMN arifosmcp_tool_calls.aaa_canon_refs IS
  'Array of canonical references from the AAA-HF corpus that apply to this record. e.g. ARRAY[''aaa-0000'', ''aaa-0042''].';
COMMENT ON COLUMN arifosmcp_tool_calls.floor_refs IS
  'Array of constitutional floors triggered or relevant. e.g. ARRAY[''F1'', ''F3'', ''F12'']. Replaces bare floor_triggered for multi-floor records.';
COMMENT ON COLUMN arifosmcp_tool_calls.record_class IS
  'Semantic class of this record. Values: constitutional_receipt | audit_trail | evidence_record | approval_record | telemetry.';

-- -----------------------------------------------
-- 2. arifosmcp_vault_seals — Immutable Seal Ledger
-- -----------------------------------------------
ALTER TABLE arifosmcp_vault_seals
  ADD COLUMN IF NOT EXISTS aaa_surface          TEXT    DEFAULT 'AAA-HF',
  ADD COLUMN IF NOT EXISTS aaa_doctrine_version TEXT,
  ADD COLUMN IF NOT EXISTS aaa_canon_refs       TEXT[],
  ADD COLUMN IF NOT EXISTS floor_refs           TEXT[],
  ADD COLUMN IF NOT EXISTS record_class         TEXT    DEFAULT 'constitutional_receipt';

COMMENT ON COLUMN arifosmcp_vault_seals.aaa_surface IS
  'AAA surface governing this seal. Always AAA-HF for doctrinal seals.';
COMMENT ON COLUMN arifosmcp_vault_seals.aaa_doctrine_version IS
  'AAA-HF doctrine version at time of sealing. Must be set for all VAULT999-bound seals.';
COMMENT ON COLUMN arifosmcp_vault_seals.floor_refs IS
  'Floors satisfied at time of sealing. Must include at minimum F1 (AMANAH) and F11 (AUDIT).';
COMMENT ON COLUMN arifosmcp_vault_seals.record_class IS
  'Always constitutional_receipt for vault seals.';

-- -----------------------------------------------
-- 3. arifosmcp_approval_tickets — Hold Queue
-- -----------------------------------------------
ALTER TABLE arifosmcp_approval_tickets
  ADD COLUMN IF NOT EXISTS aaa_surface          TEXT    DEFAULT 'AAA-HF',
  ADD COLUMN IF NOT EXISTS aaa_doctrine_version TEXT,
  ADD COLUMN IF NOT EXISTS aaa_canon_refs       TEXT[],
  ADD COLUMN IF NOT EXISTS record_class         TEXT    DEFAULT 'approval_receipt';

COMMENT ON COLUMN arifosmcp_approval_tickets.aaa_surface IS
  'AAA surface governing this approval. Displayed by AAA-Cockpit, defined by AAA-HF.';
COMMENT ON COLUMN arifosmcp_approval_tickets.record_class IS
  'Always approval_receipt for hold queue entries.';

-- -----------------------------------------------
-- 4. arifosmcp_canon_records — Constitutional Artifacts
-- -----------------------------------------------
ALTER TABLE arifosmcp_canon_records
  ADD COLUMN IF NOT EXISTS aaa_surface          TEXT    DEFAULT 'AAA-HF',
  ADD COLUMN IF NOT EXISTS aaa_doctrine_version TEXT,
  ADD COLUMN IF NOT EXISTS record_class         TEXT    DEFAULT 'canon_receipt';

COMMENT ON COLUMN arifosmcp_canon_records.aaa_surface IS
  'Source surface of this canon record. ADRs and floor changes: AAA-HF. Cockpit state: AAA-Cockpit.';
COMMENT ON COLUMN arifosmcp_canon_records.record_class IS
  'Always canon_receipt for constitutional artifacts.';

-- -----------------------------------------------
-- Indexes for AAA namespace queries
-- -----------------------------------------------
CREATE INDEX IF NOT EXISTS idx_tool_calls_aaa_surface
  ON arifosmcp_tool_calls(aaa_surface);
CREATE INDEX IF NOT EXISTS idx_tool_calls_record_class
  ON arifosmcp_tool_calls(record_class);
CREATE INDEX IF NOT EXISTS idx_vault_seals_aaa_surface
  ON arifosmcp_vault_seals(aaa_surface);

-- -----------------------------------------------
-- Validation constraint: aaa_surface must be a known surface
-- -----------------------------------------------
ALTER TABLE arifosmcp_tool_calls
  ADD CONSTRAINT IF NOT EXISTS chk_tool_calls_aaa_surface
  CHECK (aaa_surface IN ('AAA-HF', 'AAA-Cockpit', 'AAA-Doctrine', 'AAA-Interface', 'AAA-Eval'));

ALTER TABLE arifosmcp_vault_seals
  ADD CONSTRAINT IF NOT EXISTS chk_vault_seals_aaa_surface
  CHECK (aaa_surface IN ('AAA-HF', 'AAA-Cockpit', 'AAA-Doctrine', 'AAA-Interface', 'AAA-Eval'));

-- ============================================================
-- Invariant reminder (comment for future maintainers):
--
-- AAA-HF defines doctrine.
-- arifOS applies doctrine.
-- MCP tools execute.
-- Supabase records.
-- VAULT999 seals.
-- AAA-Cockpit displays.
-- Arif decides.
--
-- aaa_surface = which surface of AAA defined the law
-- aaa_doctrine_version = which version of that law was active
-- record_class = what kind of constitutional record this is
-- ============================================================
