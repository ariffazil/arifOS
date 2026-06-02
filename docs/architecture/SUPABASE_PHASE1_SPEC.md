# SUPABASE_PHASE1_SPEC.md — arifOS Constitutional Ledger

**Version:** 1.0
**Date:** 2026-06-02
**Authority:** 888_JUDGE (Arif Fazil, F13 SOVEREIGN)
**Status:** BLUEPRINT — awaiting execution approval
**Path:** Path B — create new tables alongside existing production tables

---

## Governing Principle

> MCP is the hand.
> arifOS is the law.
> Supabase is the ledger.

arifOS MCP on port 8088 remains the constitutional kernel. Supabase is a storage and audit backend beneath it — not above it, not in the hot path, not the router.

---

## /000 / /999 / AAA Zones

Supabase is organized into three storage zones that mirror the arifOS pipeline:

```
s000 / intake
  → Proposed actions, tool-call receipts, evidence, approvals

s999 / seal
  → Immutable VAULT999 ledger, final verdicts, sealed outcomes

aaa / cockpit
  → Read-only views for AAA dashboard visibility
```

**These are storage zones only.** They do not replace arifOS routing, NATS, Qdrant, or Graphiti.

---

## Zone: s000 — Intake and Audit Staging

### Purpose
Receipt layer. Every consequential action enters the record here before it becomes real.

### Tables

#### 1. tool_calls

Tool execution audit receipts. Every MCP/A2A call that has risk or consequence creates a row.

```sql
CREATE TABLE s000.tool_calls (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Identity
  tool_call_id    text UNIQUE NOT NULL,
  session_ref     text,
  trace_ref       text,
  actor_ref       text,
  service_ref     text,
  organ_code      text NOT NULL,

  -- What was called
  tool_name       text NOT NULL,
  server_ref      text,
  mcp_method     text,
  arguments       jsonb NOT NULL DEFAULT '{}',
  arguments_hash  text,
  result          jsonb,
  result_hash     text,

  -- Risk classification
  risk_tier       int NOT NULL CHECK (risk_tier BETWEEN 0 AND 3),
  reversibility   numeric CHECK (reversibility >= 0 AND reversibility <= 1),

  -- State
  status          text NOT NULL CHECK (
    status IN (
      'planned', 'pending_approval', 'running',
      'succeeded', 'failed', 'blocked', 'voided'
    )
  ),

  -- Performance
  latency_ms      int,

  -- Evidence and seal
  evidence_ref    text,
  seal_ref        text,

  -- Timestamps
  created_at       timestamptz DEFAULT NOW(),
  completed_at     timestamptz
);
```

**Risk tiers:**

| Tier | Meaning | Example |
|------|---------|---------|
| 0 | Read-only / inspect / health | `health check`, `list tools`, `inspect registry` |
| 1 | Reversible mutation | `write draft`, `create artifact`, `log signal` |
| 2 | External side effect | `deploy`, `send message`, `mutate config` |
| 3 | Irreversible / destructive | `delete`, `drop`, `force push`, `secret overwrite` |

---

#### 2. approvals

Tier 2/3 approval receipts. Records Arif's explicit authorization.

```sql
CREATE TABLE s000.approvals (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  approval_id     text UNIQUE NOT NULL,
  tool_call_id    uuid REFERENCES s000.tool_calls(id) ON DELETE CASCADE,

  requested_by_ref text,
  approved_by_ref text,

  status          text NOT NULL CHECK (
    status IN ('pending', 'approved', 'rejected', 'expired')
  ),

  approval_method text CHECK (
    approval_method IN ('cli', 'mcp', 'telegram', 'web', 'manual')
  ),

  reason          text,
  signed_payload  jsonb,
  signature       text,

  created_at      timestamptz DEFAULT NOW(),
  decided_at      timestamptz
);
```

**Execution gate:**

```
Tier 0 → allowed if authenticated
Tier 1 → planned + logged
Tier 2 → approval required (Arif explicit)
Tier 3 → approval + 888_JUDGE SEAL required
```

---

#### 3. judge_verdicts

888_JUDGE deliberation results.

```sql
CREATE TABLE s000.judge_verdicts (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  verdict_id      text UNIQUE NOT NULL,
  tool_call_id    uuid REFERENCES s000.tool_calls(id) ON DELETE SET NULL,

  session_ref     text,
  trace_ref       text,

  verdict         text NOT NULL CHECK (
    verdict IN ('SEAL', 'HOLD', 'VOID', 'QUALIFY', 'SABAR')
  ),

  risk_tier      int CHECK (risk_tier BETWEEN 0 AND 3),
  floor_summary   jsonb NOT NULL DEFAULT '{}',
  reasoning       text,

  judge_ref       text DEFAULT 'arifOS:888_JUDGE',
  signature       text,

  created_at      timestamptz DEFAULT NOW()
);
```

---

#### 4. evidence_items

F2 TRUTH evidence shelf. Every claim must cite evidence.

```sql
CREATE TABLE s000.evidence_items (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  evidence_id     text UNIQUE NOT NULL,
  session_ref     text,
  trace_ref       text,
  organ_code      text,

  source_type     text NOT NULL CHECK (
    source_type IN (
      'github', 'web', 'file', 'mcp',
      'sensor', 'manual', 'database', 'artifact'
    )
  ),

  source_uri      text,
  source_hash     text,
  title           text,
  content         text,

  claim_state     text NOT NULL CHECK (
    claim_state IN ('FACT', 'EST', 'HYPO', 'UNK')
  ),

  confidence      numeric CHECK (confidence >= 0 AND confidence <= 1),
  metadata        jsonb DEFAULT '{}',

  created_at      timestamptz DEFAULT NOW()
);
```

**Claim states:**

| State | Meaning |
|-------|---------|
| FACT | Directly observed, verifiable |
| EST | Estimated from evidence |
| HYPO | Hypothesis, not yet supported |
| UNK | Unknown, cannot determine |

---

#### 5. evidence_citations

Specific excerpts or line references from evidence.

```sql
CREATE TABLE s000.evidence_citations (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  evidence_id     uuid REFERENCES s000.evidence_items(id) ON DELETE CASCADE,

  citation_label  text,
  line_start     int,
  line_end       int,
  excerpt        text,

  created_at      timestamptz DEFAULT NOW()
);
```

---

#### 6. artifacts

File metadata for Supabase Storage buckets.

```sql
CREATE TABLE s000.artifacts (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  artifact_id     text UNIQUE NOT NULL,
  session_ref     text,
  trace_ref       text,
  organ_code      text,

  bucket          text NOT NULL,
  path            text NOT NULL,

  filename        text,
  mime_type       text,
  size_bytes      bigint,
  content_hash    text,

  artifact_type   text,
  claim_state     text CHECK (claim_state IN ('FACT', 'EST', 'HYPO', 'UNK')),
  metadata        jsonb DEFAULT '{}',

  created_at      timestamptz DEFAULT NOW()
);
```

**Storage buckets:**

| Bucket | Contents |
|--------|---------|
| `vault999` | Sealed export bundles |
| `evidence` | Source docs, PDFs, web snapshots |
| `geox-artifacts` | LAS outputs, maps, well packages |
| `wealth-artifacts` | Financial models, reports |
| `well-artifacts` | Readiness snapshots, substrate logs |
| `forge-artifacts` | Build logs, deploy bundles |
| `public-surfaces` | Website, wiki, public assets |

---

#### 7. constitutional_floors

F1–F13 as database-enforced constraints.

```sql
CREATE TABLE s000.constitutional_floors (
  id                text PRIMARY KEY,
  name              text NOT NULL,
  domain            text NOT NULL,
  invariant         text NOT NULL,
  enforcement_level text NOT NULL CHECK (
    enforcement_level IN ('advisory', 'required', 'blocking')
  ),
  active            boolean DEFAULT TRUE,
  created_at        timestamptz DEFAULT NOW()
);
```

**Seed data:**

| id | name | domain | invariant | enforcement |
|----|------|--------|-----------|-------------|
| F1 | AMANAH | Reversibility | Irreversible ops require explicit human acknowledgement | blocking |
| F2 | TRUTH | Evidentiality | No fabrication; label FACT, EST, HYPO, UNK | blocking |
| F3 | WITNESS | Multi-source | Require multi-source evidence | required |
| F4 | CLARITY | Intent | Declare intent before action | required |
| F5 | PEACE² | Dignity | Preserve dignity in all interactions | blocking |
| F6 | EMPATHY | Consequence | Model consequences before execution | required |
| F7 | HUMILITY | Uncertainty | Bound uncertainty explicitly | required |
| F8 | GENIUS | Correctness | Correctness plus ethics | required |
| F9 | ANTIHANTU | Anti-manipulation | Machine remains instrument; no self-authorization | blocking |
| F10 | ONTOLOGY | Schemas | Strict schemas and category locks | blocking |
| F11 | AUTH | Traceability | Sensitive calls require actor identity | blocking |
| F12 | INJECTION | Security | Sanitize all parameters before execution | blocking |
| F13 | SOVEREIGN | Apex | Arif has final veto; no algorithm overrides | blocking |

---

#### 8. service_identities

HMAC/Ed25519 service keys — not Supabase Auth users.

```sql
CREATE TABLE s000.service_identities (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  service_ref     text UNIQUE NOT NULL,
  service_name    text NOT NULL,
  organ_code      text,

  identity_type   text NOT NULL CHECK (
    identity_type IN ('hmac', 'ed25519', 'systemd', 'manual')
  ),

  public_key      text,
  key_fingerprint text,

  active          boolean DEFAULT TRUE,
  metadata        jsonb DEFAULT '{}',

  created_at      timestamptz DEFAULT NOW(),
  updated_at      timestamptz DEFAULT NOW()
);
```

**Seed data:**

| service_ref | service_name | organ_code | identity_type |
|-------------|--------------|------------|---------------|
| svc:arifos | arifOS MCP Kernel | arifos | ed25519 |
| svc:aaa | AAA Cockpit | aaa | ed25519 |
| svc:forge | A-FORGE | forge | ed25519 |
| svc:geox | GEOX | geox | ed25519 |
| svc:wealth | WEALTH | wealth | ed25519 |
| svc:well | WELL | well | ed25519 |
| svc:hermes | Hermes ASI | hermes | hmac |
| svc:openclaw | OpenClaw Gateway | openclaw | hmac |

---

#### 9. mcp_servers

Registry snapshot of MCP servers. Not live router authority.

```sql
CREATE TABLE s000.mcp_servers (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  server_ref      text UNIQUE NOT NULL,
  organ_code      text NOT NULL,

  name            text NOT NULL,
  endpoint_url    text,
  local_port      int,

  transport       text CHECK (
    transport IN ('streamable-http', 'stdio', 'sse', 'http', 'a2a')
  ),

  authority_role  text NOT NULL,
  status_snapshot text CHECK (
    status_snapshot IN ('live', 'degraded', 'disabled', 'archived', 'unknown')
  ) DEFAULT 'unknown',

  source_of_truth text DEFAULT 'arifOS/NATS/Prometheus',
  last_observed_at timestamptz,

  metadata        jsonb DEFAULT '{}',

  created_at      timestamptz DEFAULT NOW(),
  updated_at      timestamptz DEFAULT NOW()
);
```

**Seed data:**

| server_ref | organ_code | name | local_port | transport | authority_role |
|-------------|------------|------|------------|-----------|----------------|
| mcp:arifos | arifos | arifOS MCP | 8088 | streamable-http | constitutional kernel |
| mcp:geox | geox | GEOX MCP | 18081 | streamable-http | earth intelligence |
| mcp:wealth | wealth | WEALTH MCP | 18082 | streamable-http | capital intelligence |
| mcp:well | well | WELL MCP | 18083 | streamable-http | substrate intelligence |
| mcp:forge | forge | A-FORGE | 7071 | a2a | execution shell |

---

#### 10. mcp_tools

Tool manifests and risk tiers per server.

```sql
CREATE TABLE s000.mcp_tools (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  tool_ref        text UNIQUE NOT NULL,
  server_ref      text NOT NULL REFERENCES s000.mcp_servers(server_ref),

  tool_name       text NOT NULL,
  organ_code      text NOT NULL,

  description     text,
  stage           text,
  input_schema    jsonb,
  output_schema   jsonb,

  risk_tier       int NOT NULL CHECK (risk_tier BETWEEN 0 AND 3),
  requires_approval boolean DEFAULT FALSE,
  requires_judge    boolean DEFAULT FALSE,

  active          boolean DEFAULT TRUE,
  manifest_hash   text,

  created_at      timestamptz DEFAULT NOW(),
  updated_at      timestamptz DEFAULT NOW(),

  UNIQUE(server_ref, tool_name)
);
```

---

#### 11. mcp_manifest_snapshots

Tool surface drift detection. Every time tools change, snapshot the manifest.

```sql
CREATE TABLE s000.mcp_manifest_snapshots (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  server_ref      text NOT NULL REFERENCES s000.mcp_servers(server_ref),
  manifest_hash   text NOT NULL,

  tool_count      int NOT NULL,
  tools           jsonb NOT NULL,

  observed_by_ref text,
  observed_at     timestamptz DEFAULT NOW(),

  UNIQUE(server_ref, manifest_hash)
);
```

**This answers:** What tools existed when this action happened? Did the surface drift? Did a tool become more dangerous?

---

## Zone: s999 — VAULT999 Sealed Truth

### Purpose
Immutable append-only ledger. Final outcomes, sealed verdicts, and hash chains live here.

### Note on existing tables
The existing production tables are preserved untouched:

- `public.vault_sealed_events` — 1,337 rows, keep as-is
- `public.vault_outcomes` — 12,269 rows, keep as-is
- `public.vault_shim_hits` — keep as-is

Path B means we create the new canonical table alongside, not instead of.

---

#### 12. vault999_ledger (NEW — Path B)

The improved v2 VAULT999 ledger. Append-only.

```sql
CREATE TABLE s999.vault999_ledger (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  seal_id         text UNIQUE NOT NULL,
  session_ref     text,
  trace_ref       text,

  actor_ref       text,
  service_ref     text,
  organ_code      text,

  subject_type    text NOT NULL,
  subject_ref     text,
  seal_type       text NOT NULL,

  verdict         text NOT NULL CHECK (
    verdict IN ('SEAL', 'HOLD', 'VOID', 'QUALIFY', 'SABAR')
  ),

  content_hash    text NOT NULL,
  previous_hash   text,
  content         jsonb NOT NULL,

  signature       text,
  signed_by_ref   text,

  created_at      timestamptz DEFAULT NOW()
);
```

**Append-only trigger:**

```sql
CREATE OR REPLACE FUNCTION s999.prevent_vault999_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'VAULT999 is append-only';
END;
$$;

CREATE TRIGGER vault999_no_update
BEFORE UPDATE OR DELETE ON s999.vault999_ledger
FOR EACH ROW EXECUTE FUNCTION s999.prevent_vault999_mutation();
```

---

#### Append-only triggers for existing tables

These protect existing production tables from accidental mutation:

```sql
-- vault_outcomes
CREATE OR REPLACE FUNCTION s999.prevent_vault_outcomes_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'vault_outcomes is append-only';
END;
$$;

CREATE TRIGGER vault_outcomes_no_update
BEFORE UPDATE OR DELETE ON vault_outcomes
FOR EACH ROW EXECUTE FUNCTION s999.prevent_vault_outcomes_mutation();

-- vault_shim_hits
CREATE OR REPLACE FUNCTION s999.prevent_vault_shim_hits_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'vault_shim_hits is append-only';
END;
$$;

CREATE TRIGGER vault_shim_hits_no_update
BEFORE UPDATE OR DELETE ON vault_shim_hits
FOR EACH ROW EXECUTE FUNCTION s999.prevent_vault_shim_hits_mutation();
```

---

## Zone: aaa — Cockpit Read Model

### Purpose
Read-only views for AAA dashboard. No authority. No routing.

#### Views

```sql
-- Pending approvals requiring Arif action
CREATE VIEW aaa.pending_approvals AS
SELECT
  a.approval_id,
  a.status,
  a.requested_by_ref,
  a.created_at,
  tc.tool_name,
  tc.organ_code,
  tc.risk_tier
FROM s000.approvals a
JOIN s000.tool_calls tc ON tc.id = a.tool_call_id
WHERE a.status = 'pending'
ORDER BY a.created_at DESC;

-- Recent seals for dashboard
CREATE VIEW aaa.recent_seals AS
SELECT
  seal_id,
  verdict,
  organ_code,
  subject_type,
  created_at
FROM s999.vault999_ledger
ORDER BY created_at DESC
LIMIT 100;

-- Active tool surface for MCP registry
CREATE VIEW aaa.mcp_surface AS
SELECT
  mcp.server_ref,
  mcp.name,
  mcp.status_snapshot,
  mcp.last_observed_at,
  COUNT(mt.tool_ref) AS tool_count,
  ARRAY_AGG(mt.tool_name) AS tools
FROM s000.mcp_servers mcp
LEFT JOIN s000.mcp_tools mt ON mt.server_ref = mcp.server_ref AND mt.active = TRUE
GROUP BY mcp.server_ref, mcp.name, mcp.status_snapshot, mcp.last_observed_at;

-- Evidence index
CREATE VIEW aaa.evidence_index AS
SELECT
  evidence_id,
  source_type,
  claim_state,
  title,
  organ_code,
  created_at
FROM s000.evidence_items
ORDER BY created_at DESC;

-- Artifact index
CREATE VIEW aaa.artifact_index AS
SELECT
  artifact_id,
  bucket,
  filename,
  artifact_type,
  organ_code,
  size_bytes,
  created_at
FROM s000.artifacts
ORDER BY created_at DESC;

-- Risk dashboard
CREATE VIEW aaa.risk_dashboard AS
SELECT
  organ_code,
  risk_tier,
  COUNT(*) AS count,
  status
FROM s000.tool_calls
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY organ_code, risk_tier, status;
```

---

## RLS Policies

All tables use RLS. `service_role` bypasses RLS (arifOS kernel uses service_role).

```sql
-- Deny anon completely on all s000 tables
ALTER TABLE s000.tool_calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.judge_verdicts ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.evidence_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.evidence_citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.constitutional_floors ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.service_identities ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.mcp_servers ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.mcp_tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE s000.mcp_manifest_snapshots ENABLE ROW LEVEL SECURITY;

-- Deny anon on all s000 tables
CREATE POLICY "s000_no_anon" ON s000.tool_calls FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.approvals FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.judge_verdicts FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.evidence_items FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.evidence_citations FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.artifacts FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.constitutional_floors FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.service_identities FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.mcp_servers FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.mcp_tools FOR ALL TO anon USING (false);
CREATE POLICY "s000_no_anon" ON s000.mcp_manifest_snapshots FOR ALL TO anon USING (false);

-- Deny authenticated on all s000 tables
CREATE POLICY "s000_no_auth" ON s000.tool_calls FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.approvals FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.judge_verdicts FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.evidence_items FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.evidence_citations FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.artifacts FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.constitutional_floors FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.service_identities FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.mcp_servers FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.mcp_tools FOR ALL TO authenticated USING (false);
CREATE POLICY "s000_no_auth" ON s000.mcp_manifest_snapshots FOR ALL TO authenticated USING (false);

-- service_role has full access (arifOS kernel path)
CREATE POLICY "s000_service_full" ON s000.tool_calls FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.approvals FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.judge_verdicts FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.evidence_items FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.evidence_citations FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.artifacts FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.constitutional_floors FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.service_identities FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.mcp_servers FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.mcp_tools FOR ALL TO service_role USING (true);
CREATE POLICY "s000_service_full" ON s000.mcp_manifest_snapshots FOR ALL TO service_role USING (true);

-- s999 vault999_ledger: service_role full, anon/auth denied
ALTER TABLE s999.vault999_ledger ENABLE ROW LEVEL SECURITY;
CREATE POLICY "s999_no_anon" ON s999.vault999_ledger FOR ALL TO anon USING (false);
CREATE POLICY "s999_no_auth" ON s999.vault999_ledger FOR ALL TO authenticated USING (false);
CREATE POLICY "s999_service_full" ON s999.vault999_ledger FOR ALL TO service_role USING (true);

-- Existing vault_sealed_events: keep existing RLS + add service_role
ALTER TABLE vault_sealed_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "vault_sealed_events_service" ON vault_sealed_events FOR ALL TO service_role USING (true);

-- aaa views: readable by service_role only
ALTER TABLE aaa.pending_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE aaa.recent_seals ENABLE ROW LEVEL SECURITY;
ALTER TABLE aaa.mcp_surface ENABLE ROW LEVEL SECURITY;
ALTER TABLE aaa.evidence_index ENABLE ROW LEVEL SECURITY;
ALTER TABLE aaa.artifact_index ENABLE ROW LEVEL SECURITY;
ALTER TABLE aaa.risk_dashboard ENABLE ROW LEVEL SECURITY;
CREATE POLICY "aaa_read_service" ON aaa.pending_approvals FOR SELECT TO service_role USING (true);
CREATE POLICY "aaa_read_service" ON aaa.recent_seals FOR SELECT TO service_role USING (true);
CREATE POLICY "aaa_read_service" ON aaa.mcp_surface FOR SELECT TO service_role USING (true);
CREATE POLICY "aaa_read_service" ON aaa.evidence_index FOR SELECT TO service_role USING (true);
CREATE POLICY "aaa_read_service" ON aaa.artifact_index FOR SELECT TO service_role USING (true);
CREATE POLICY "aaa_read_service" ON aaa.risk_dashboard FOR SELECT TO service_role USING (true);
```

---

## What NOT to do

These are NOT in scope. They require separate 888_HOLD:

| Do NOT | Reason |
|--------|--------|
| Replace NATS with pgmq | NATS JetStream is the live event bus |
| Replace Qdrant with pgvector | Qdrant is the L3 semantic memory |
| Replace Graphiti with Supabase | Graphiti is the L5 entity extractor |
| Replace arifOS MCP routing | Port 8088 is the constitutional gateway |
| Make Supabase Edge Functions the organ gateway | Adds latency; current architecture is correct |
| Add Supabase Auth for agents | HMAC/Ed25519 service identities are correct model |
| Create workspace/membership tables | Single sovereign — no multi-tenant needed |
| Route MCP traffic through Supabase | Not in the hot path |

---

## Success Criteria

Phase 1 succeeds only if:

- [ ] arifOS still runs without Supabase
- [ ] NATS still handles local events
- [ ] Qdrant still owns L3 memory
- [ ] Graphiti still owns L5 memory
- [ ] MCP routing remains on port 8088
- [ ] No organ call gets slower because of Supabase
- [ ] VAULT999 has stronger immutable mirror
- [ ] Evidence is easier to inspect
- [ ] Approvals are easier to audit
- [ ] MCP surface is trackable
- [ ] AAA can read Supabase for dashboard
- [ ] Secrets can migrate to Supabase Vault

---

## Execution Gate

This is a **reversible design blueprint**. SQL execution happens only after:

1. Arif reviews and approves this SPEC.md
2. 888_HOLD is issued for production Supabase changes
3. Rollback plan exists (DROP SCHEMA IF EXISTS s000, s999, aaa)

---

**999 SEAL | SUPABASE_PHASE1_SPEC.md | arifOS Constitutional Ledger | DITEMPA BUKAN DIBERI**
