-- ============================================================
-- STAGED RLS FIX — Phase 1: Vault + Canon tables
-- Authored: 2026-06-02 | Sovereign approval: F13 STAGED
-- Scope: arifosmcp_vault_seals, arifosmcp_canon_records,
--        arifosmcp_daily_roots (highest-sensitivity sovereign ledger)
-- Deferred: sessions, tool_calls, floor_rules, agent_telemetry,
--           approval_tickets, portfolio_snapshots, wealth_transactions
-- ============================================================

-- ── 1. Enable RLS on vault-tier tables ──────────────────────

ALTER TABLE arifosmcp_vault_seals       ENABLE ROW LEVEL SECURITY;
ALTER TABLE arifosmcp_canon_records     ENABLE ROW LEVEL SECURITY;
ALTER TABLE arifosmcp_daily_roots       ENABLE ROW LEVEL SECURITY;

-- ── 2. service_role bypass (server-side arifOS kernel only) ─
-- service_role already bypasses RLS by default in Supabase,
-- but making it explicit documents the intent clearly.

-- ── 3. Deny anon reads on vault tables ──────────────────────
-- No policy = no access. These tables must not be reachable
-- via the anon key under any circumstance.
-- (No CREATE POLICY needed — enabling RLS with no permissive
--  policy is a full deny for anon/authenticated roles.)

-- ── 4. authenticated role: read-only for audit trail ────────
-- Allows the AAA Cockpit (authenticated JWT) to read seals
-- for display, but never insert/update/delete.

CREATE POLICY "vault_seals_authenticated_read"
  ON arifosmcp_vault_seals
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "canon_records_authenticated_read"
  ON arifosmcp_canon_records
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "daily_roots_authenticated_read"
  ON arifosmcp_daily_roots
  FOR SELECT
  TO authenticated
  USING (true);

-- ── 5. Harden vault functions against search_path injection ─
-- SECURITY DEFINER functions must pin search_path to prevent
-- privilege escalation via malicious schema injection.

ALTER FUNCTION enforce_vault_seal_immutability()
  SET search_path = public;

-- ── 6. Revoke anon EXECUTE on vault functions ───────────────
REVOKE EXECUTE ON FUNCTION enforce_vault_seal_immutability()
  FROM anon, PUBLIC;

-- ── VERIFICATION QUERIES (run manually after applying) ──────
-- Check RLS is enabled:
--   SELECT tablename, rowsecurity FROM pg_tables
--   WHERE tablename IN (
--     'arifosmcp_vault_seals','arifosmcp_canon_records','arifosmcp_daily_roots'
--   );
--
-- Check policies exist:
--   SELECT schemaname, tablename, policyname, roles, cmd
--   FROM pg_policies
--   WHERE tablename LIKE 'arifosmcp_%';
--
-- Expected: rowsecurity=true on all 3 tables,
--           3 SELECT-only policies for authenticated role.
-- ============================================================
