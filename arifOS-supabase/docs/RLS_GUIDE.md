# arifOS Row Level Security (RLS) Guide

**Status:** Future — Do not implement until tables are stable and data is flowing correctly.

> Premature RLS creates invisible failures. Design RLS only after proving the database layer works end-to-end.

---

## Why RLS Matters

Supabase Auth (GoTrue) issues JWTs. Row Level Security policies determine which rows a given JWT can read/write. For your architecture:

- **`service_role` key** — bypasses ALL RLS. Your Python/TypeScript agents use this.
- **`anon` key** — RLS policies apply. For future browser/public clients.

**Current architecture:** All agent services are server-side trusted code. They use `service_role` key and bypass RLS entirely. RLS is not blocking anything today.

**When RLS becomes relevant:**
- Browser clients accessing arifOS MCP
- Public API endpoints with per-user access control
- Multi-tenant scenarios where agents must only see their own data

---

## RLS Design Pattern for arifOS

### Step 1 — Enable RLS on a table

```sql
ALTER TABLE arifosmcp_well_states ENABLE ROW LEVEL SECURITY;
```

This does NOT block `service_role` key — it only affects requests using `anon` key or other user JWTs.

### Step 2 — Create explicit service_role policy (redundant but documented)

```sql
-- Allow service_role full access (bypass RLS)
CREATE POLICY "service_role_full_access"
  ON arifosmcp_well_states
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
```

Even though service_role bypasses RLS by default, explicit policies document intent.

### Step 3 — Future per-agent access via JWT claims

When you wire Supabase Auth into the operator gateway:

```sql
-- Per-agent access: agent can only see its own sessions
CREATE POLICY "agent_own_sessions"
  ON arifosmcp_sessions
  FOR SELECT
  TO authenticated
  USING (auth.jwt() ->> 'agent_id' = agent_id);
```

This requires your auth tokens to carry `agent_id` as a claim. Design this when you add Supabase Auth to the operator layer.

---

## Tables and Recommended Future RLS

| Table | RLS Recommendation | Reason |
|-------|-------------------|--------|
| `arifosmcp_vault_seals` | service_role full only | Immutable audit ledger — no user-level read restriction needed |
| `arifosmcp_sessions` | future per-agent | May want agents to only see their own sessions in multi-tenant future |
| `arifosmcp_tool_calls` | service_role full only | Audit log — append only, no read restriction needed |
| `arifosmcp_canon_records` | future public read | ADR ledger may need to be publicly readable |
| `arifosmcp_approval_tickets` | operator only | 888_HOLD queue — only operators should see pending tickets |
| `arifosmcp_floor_rules` | public read | Constitutional rules — no access restriction |
| `arifosmcp_agent_telemetry` | service_role full only | Internal telemetry — no external access needed |
| `arifosmcp_daily_roots` | public read | Merkle proofs — verifiable by anyone |
| `arifosmcp_transactions` | future per-user | WEALTH ledger — users should only see their own transactions |
| `arifosmcp_portfolio_snapshots` | future per-user | Portfolio data — users should only see their own snapshots |

---

## RLS Anti-Patterns to Avoid

1. **Don't enable RLS without creating policies first**
   - All access will be blocked, including service_role
   - Always create explicit policies before enabling RLS

2. **Don't confuse service_role and anon key behavior**
   - service_role bypasses RLS by default (can be disabled in Supabase config)
   - anon key always respects RLS

3. **Don't design RLS before table boundaries are stable**
   - Changes to table structure may require policy rewrites
   - Prove data flows first, design RLS second

4. **Don't implement RLS for access control that should be at application layer**
   - If your operator gateway already authenticates requests, RLS at DB layer is defense-in-depth, not primary control

---

## Migration Path

```
Phase 1 (now):     No RLS. service_role key only.
Phase 2 (later):   Enable RLS on tables with explicit service_role policies.
Phase 3 (future):  Wire Supabase Auth JWTs into operator gateway.
Phase 4 (future):  Implement per-agent, per-user policies.
```

---

## Testing RLS

After enabling RLS, test with both keys:

```python
# Test with anon key — should be blocked or filtered
anon_sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
result = anon_sb.table('arifosmcp_sessions').select('*').execute()
# Should return only rows matching RLS policy

# Test with service_role key — should see everything
service_sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
result = service_sb.table('arifosmcp_sessions').select('*').execute()
# Should see all rows
```

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

```
Epoch: 2026-04-17T18:00+08
Verdict: RLS_GUIDE_SEALED_DEFERRED_UNTIL_STABLE
QDF: PHASE_1_NO_RLS
```