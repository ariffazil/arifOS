# SUPABASE_PHASE1_SPEC.md — arifOS Governance Ledger

> **DITEMPA BUKAN DIBERI** — This spec is written, not executed. No SQL runs until Arif approves.

---

## 1. What This Is

Phase 1 migration spec for arifOS Supabase governance ledger.
Writes: `/root/arifOS/docs/architecture/SUPABASE_PHASE1_SPEC.md`
Status: DRAFT — awaiting F13 SOVEREIGN approval before any SQL execution

---

## 2. Architecture Summary

```
Before: MCPs worked → some logs, some seals, some partial DB rows
After:  MCPs work → Supabase records official trail → AAA sees → VAULT999 seals
```

Supabase becomes the **official record office** behind the MCPs.
arifOS remains the brain. Supabase becomes the spine for records.

**What Supabase IS NOT:**
- Not the control plane
- Not the routing authority
- Not agent auth system
- Not NATS replacement
- Not Qdrant replacement
- Not session authority

**What Supabase IS:**
- Structured ledger and evidence layer
- s000 = intake/receipts/evidence
- s999 = immutable seal/outcome ledger
- AAA = cockpit read-model views

---

## 3. Current Table Map

| Table | Status | Action |
|-------|--------|--------|
| `vault999` | Generic key-value artifact. Not the real seal chain. | IGNORE. Do not use. Do not delete. |
| `vault_sealed_events` | Real immutable seal records, ~1,337 rows | KEEP. Add append-only trigger. Backfill to vault999_ledger later. |
| `vault_outcomes` | Decision outcomes, ~12,269 rows | KEEP. Add append-only trigger. |
| `vault_shim_hits` | Tool alias shim hits, ~4 rows | KEEP. Add append-only trigger. |
| `arifosmcp_tool_calls` | Tool execution audit | KEEP. Protect from mutation. |
| `arifosmcp_approval_tickets` | Human approval queue | KEEP. Protect from mutation. |
| `arifosmcp_floor_rules` | Constitutional floor rules | KEEP. Seed/normalize F1-F13. |
| `memory_records` | Working/semantic/episodic memory | KEEP. Already populated. |
| `memory_embeddings` | pgvector embeddings | KEEP. |
| `memory_store` | Entity-tagged episodic store | KEEP. |
| `memory_contradictions` | Conflict tracking | KEEP. |

---

## 4. New Schema: s000 — Intake / Receipts

### 4.1 `judge_verdicts`

Stores 888_JUDGE decisions before sealing.

```sql
CREATE TABLE IF NOT EXISTS s000_judge_verdicts (
  id              BIGSERIAL PRIMARY KEY,
  verdict_id      TEXT NOT NULL UNIQUE,
  session_id      TEXT NOT NULL,
  actor_id        TEXT NOT NULL,
  organ           TEXT NOT NULL,  -- arifOS, GEOX, WEALTH, WELL
  candidate       TEXT NOT NULL,
  verdict         TEXT NOT NULL,   -- SEAL / SABAR / HOLD / VOID
  evidence_level  TEXT DEFAULT 'unverified',
  confidence      NUMERIC(4,3),
  floors_checked  TEXT[],
  floors_triggered TEXT[],
  risk_tier       TEXT DEFAULT 'medium',
  deliberation_ms INTEGER,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_judge_verdicts_session ON s000_judge_verdicts(session_id);
CREATE INDEX IF NOT EXISTS idx_judge_verdicts_verdict ON s000_judge_verdicts(verdict);
CREATE INDEX IF NOT EXISTS idx_judge_verdicts_organ   ON s000_judge_verdicts(organ);
```

### 4.2 `evidence_items`

F2 TRUTH evidence shelf. Stores evidence receipts for MCP operations.

```sql
CREATE TABLE IF NOT EXISTS s000_evidence_items (
  id              BIGSERIAL PRIMARY KEY,
  evidence_id     TEXT NOT NULL UNIQUE,
  source_organ    TEXT NOT NULL,  -- GEOX, WEALTH, WELL, arifOS
  source_url      TEXT,
  source_type     TEXT NOT NULL,  -- web_fetch, document, api_response, computed
  query_used      TEXT,
  content_hash    TEXT NOT NULL,  -- sha256 of content
  content_preview TEXT,           -- first 500 chars
  retrieved_at    TIMESTAMPTZ DEFAULT NOW(),
  confidence      NUMERIC(4,3),
  authority       TEXT DEFAULT 'system_inferred', -- explicit_user, document, system_inferred
  tags            TEXT[],
  metadata        JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON s000_evidence_items(source_organ);
CREATE INDEX IF NOT EXISTS idx_evidence_hash  ON s000_evidence_items(content_hash);
```

### 4.3 `evidence_citations`

Links evidence to the tool calls / verdicts that used them.

```sql
CREATE TABLE IF NOT EXISTS s000_evidence_citations (
  id              BIGSERIAL PRIMARY KEY,
  citation_id      TEXT NOT NULL UNIQUE,
  evidence_id      TEXT NOT NULL REFERENCES s000_evidence_items(evidence_id),
  citing_session   TEXT NOT NULL,
  citing_tool      TEXT,
  citing_verdict   TEXT,
  used_for         TEXT,          -- reasoning, grounding, validation
  created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_citations_evidence ON s000_evidence_citations(evidence_id);
CREATE INDEX IF NOT EXISTS idx_citations_session  ON s000_evidence_citations(citing_session);
```

### 4.4 `artifacts`

Indexes Supabase Storage files and agent-generated outputs.

```sql
CREATE TABLE IF NOT EXISTS s000_artifacts (
  id              BIGSERIAL PRIMARY KEY,
  artifact_id     TEXT NOT NULL UNIQUE,
  organ           TEXT NOT NULL,
  artifact_type   TEXT NOT NULL,  -- image, pdf, json, report, model_output, document
  storage_path    TEXT,            -- Supabase Storage path or URL
  content_hash    TEXT,
  file_size_bytes BIGINT,
  generated_at    TIMESTAMPTZ DEFAULT NOW(),
  session_id      TEXT,
  tool_call_id    TEXT,
  summary         TEXT,
  tags            TEXT[],
  metadata        JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_artifacts_organ     ON s000_artifacts(organ);
CREATE INDEX IF NOT EXISTS idx_artifacts_type      ON s000_artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifacts_session   ON s000_artifacts(session_id);
```

### 4.5 `service_identities`

HMAC/Ed25519 service identity registry for MCP servers.

```sql
CREATE TABLE IF NOT EXISTS s000_service_identities (
  id              BIGSERIAL PRIMARY KEY,
  identity_id     TEXT NOT NULL UNIQUE,
  organ           TEXT NOT NULL,  -- arifOS, GEOX, WEALTH, WELL, AAA
  service_name    TEXT NOT NULL,
  key_type        TEXT NOT NULL,  -- ed25519, hmac-sha256
  public_key_fingerprint TEXT,
  registered_at   TIMESTAMPTZ DEFAULT NOW(),
  is_active       BOOLEAN DEFAULT TRUE,
  last_seen       TIMESTAMPTZ,
  metadata        JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_identities_organ    ON s000_service_identities(organ);
CREATE INDEX IF NOT EXISTS idx_identities_active   ON s000_service_identities(is_active) WHERE is_active = TRUE;
```

### 4.6 `mcp_servers`

MCP server registry snapshot.

```sql
CREATE TABLE IF NOT EXISTS s000_mcp_servers (
  id              BIGSERIAL PRIMARY KEY,
  server_id       TEXT NOT NULL UNIQUE,
  organ           TEXT NOT NULL,
  server_name     TEXT NOT NULL,
  endpoint_url    TEXT,
  port            INTEGER,
  is_active       BOOLEAN DEFAULT TRUE,
  version         TEXT,
  registered_at   TIMESTAMPTZ DEFAULT NOW(),
  last_ping       TIMESTAMPTZ,
  health_status   TEXT DEFAULT 'unknown',
  metadata        JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_organ   ON s000_mcp_servers(organ);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_health  ON s000_mcp_servers(health_status);
```

### 4.7 `mcp_tools`

MCP tool manifest and risk tier registry.

```sql
CREATE TABLE IF NOT EXISTS s000_mcp_tools (
  id              BIGSERIAL PRIMARY KEY,
  tool_id         TEXT NOT NULL UNIQUE,
  tool_name       TEXT NOT NULL,
  server_id       TEXT REFERENCES s000_mcp_servers(server_id),
  organ           TEXT NOT NULL,
  risk_tier       TEXT NOT NULL,  -- T1 operational, T2 approval, T3 critical
  description     TEXT,
  parameters_schema JSONB,
  is_enabled      BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_server   ON s000_mcp_tools(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_risk     ON s000_mcp_tools(risk_tier);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_organ    ON s000_mcp_tools(organ);
```

### 4.8 `mcp_manifest_snapshots`

Tool surface drift detection — periodic snapshots of what tools exist.

```sql
CREATE TABLE IF NOT EXISTS s000_mcp_manifest_snapshots (
  id              BIGSERIAL PRIMARY KEY,
  snapshot_id     TEXT NOT NULL UNIQUE,
  server_id       TEXT REFERENCES s000_mcp_servers(server_id),
  snapshot_at     TIMESTAMPTZ DEFAULT NOW(),
  tool_count      INTEGER,
  tool_names      TEXT[],
  added_tools     TEXT[],  -- tools in this snapshot not in previous
  removed_tools   TEXT[],  -- tools missing from previous snapshot
  drift_detected  BOOLEAN DEFAULT FALSE,
  metadata        JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_manifest_server     ON s000_mcp_manifest_snapshots(server_id);
CREATE INDEX IF NOT EXISTS idx_manifest_drift     ON s000_mcp_manifest_snapshots(drift_detected) WHERE drift_detected = TRUE;
```

---

## 5. New Schema: s999 — Immutable Seal Ledger

### 5.1 `vault999_ledger` (v2 canonical)

Canonical VAULT999 ledger. Path B — keeps vault_sealed_events as-is, creates new table as canonical v2.

```sql
CREATE TABLE IF NOT EXISTS s999_vault999_ledger (
  id              BIGSERIAL PRIMARY KEY,
  ledger_id       TEXT NOT NULL UNIQUE,
  seal_id         TEXT NOT NULL UNIQUE,
  prev_hash       TEXT NOT NULL,
  payload_hash    TEXT NOT NULL,  -- blake3 of canonical JSON payload
  actor_id        TEXT NOT NULL,
  organ           TEXT NOT NULL,
  action          TEXT NOT NULL,
  payload         JSONB NOT NULL DEFAULT '{}',
  epoch           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  human_witness   TEXT,           -- Arif's Ed25519 signature (base64)
  ai_witness      TEXT,           -- agent identity
  evidence_refs   TEXT[],         -- evidence_ids used
  artifact_refs   TEXT[],         -- artifact_ids produced
  verdict_ref     TEXT,           -- judge_verdicts.verdict_id
  confidence      NUMERIC(4,3),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ledger_prev_hash   ON s999_vault999_ledger(prev_hash);
CREATE INDEX IF NOT EXISTS idx_ledger_seal_id     ON s999_vault999_ledger(seal_id);
CREATE INDEX IF NOT EXISTS idx_ledger_organ       ON s999_vault999_ledger(organ);
CREATE INDEX IF NOT EXISTS idx_ledger_epoch       ON s999_vault999_ledger(epoch);
```

### 5.2 Append-Only Triggers (all s999 tables)

```sql
CREATE OR REPLACE FUNCTION enforce_append_only()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'This table is append-only. UPDATE and DELETE are forbidden.';
END;
$$ LANGUAGE plpgsql;

-- Apply to vault_sealed_events
CREATE OR REPLACE TRIGGER no_vault_sealed_events_mutation
  BEFORE UPDATE OR DELETE ON vault_sealed_events
  FOR EACH ROW EXECUTE FUNCTION enforce_append_only();

-- Apply to vault_outcomes
CREATE OR REPLACE TRIGGER no_vault_outcomes_mutation
  BEFORE UPDATE OR DELETE ON vault_outcomes
  FOR EACH ROW EXECUTE FUNCTION enforce_append_only();

-- Apply to vault_shim_hits
CREATE OR REPLACE TRIGGER no_vault_shim_hits_mutation
  BEFORE UPDATE OR DELETE ON vault_shim_hits
  FOR EACH ROW EXECUTE FUNCTION enforce_append_only();

-- Apply to s999_vault999_ledger
CREATE OR REPLACE TRIGGER no_vault999_ledger_mutation
  BEFORE UPDATE OR DELETE ON s999_vault999_ledger
  FOR EACH ROW EXECUTE FUNCTION enforce_append_only();
```

---

## 6. New Schema: AAA — Cockpit Read Model

All AAA views are SELECT-only. No write authority.

```sql
-- Pending approvals requiring human decision
CREATE OR REPLACE VIEW aaa_pending_approvals AS
SELECT
  ticket_id,
  action_plan,
  requested_at,
  epoch,
  status
FROM arifosmcp_approval_tickets
WHERE human_verdict = 'PENDING'
ORDER BY requested_at DESC;

-- Recent tool calls across all organs
CREATE OR REPLACE VIEW aaa_recent_tool_calls AS
SELECT
  id, organ, session_id, tool_name, agent_id,
  verdict, floor_triggered, duration_ms, epoch
FROM arifosmcp_tool_calls
ORDER BY epoch DESC
LIMIT 100;

-- Recent sealed events
CREATE OR REPLACE VIEW aaa_recent_seals AS
SELECT
  seal_id, organ, action, epoch,
  human_witness, ai_witness, confidence,
  payload
FROM s999_vault999_ledger
ORDER BY epoch DESC
LIMIT 100;

-- Evidence index
CREATE OR REPLACE VIEW aaa_evidence_index AS
SELECT
  evidence_id, source_organ, source_type,
  query_used, confidence, retrieved_at, tags
FROM s000_evidence_items
ORDER BY retrieved_at DESC;

-- Artifact index
CREATE OR REPLACE VIEW aaa_artifact_index AS
SELECT
  artifact_id, organ, artifact_type,
  generated_at, session_id, summary, tags
FROM s000_artifacts
ORDER BY generated_at DESC;

-- MCP surface (what tools exist)
CREATE OR REPLACE VIEW aaa_mcp_surface AS
SELECT
  t.tool_name, t.organ, t.risk_tier,
  s.server_name, s.endpoint_url, s.health_status
FROM s000_mcp_tools t
JOIN s000_mcp_servers s ON t.server_id = s.server_id
WHERE t.is_enabled = TRUE AND s.is_active = TRUE;

-- Risk dashboard (Tier 2/3 tool calls this week)
CREATE OR REPLACE VIEW aaa_risk_dashboard AS
SELECT
  organ,
  COUNT(*) FILTER (WHERE risk_tier IN ('T2', 'T3')) AS high_risk_calls,
  COUNT(*) AS total_calls,
  COUNT(*) FILTER (WHERE verdict = 'SEAL') AS approved,
  COUNT(*) FILTER (WHERE verdict = 'VOID') AS rejected,
  AVG(confidence) AS avg_confidence
FROM arifosmcp_tool_calls t
LEFT JOIN s000_mcp_tools m ON t.tool_name = m.tool_name
WHERE epoch > NOW() - INTERVAL '7 days'
GROUP BY organ;

-- Organ registry snapshot
CREATE OR REPLACE VIEW aaa_organ_registry_snapshot AS
SELECT
  organ,
  is_active,
  registered_at,
  last_ping,
  health_status
FROM s000_mcp_servers
ORDER BY organ;

-- Tool manifest drift
CREATE OR REPLACE VIEW aaa_manifest_drift AS
SELECT
  server_id,
  snapshot_at,
  drift_detected,
  added_tools,
  removed_tools,
  tool_count
FROM s000_mcp_manifest_snapshots
WHERE drift_detected = TRUE
ORDER BY snapshot_at DESC;
```

---

## 7. Constitutional Floor Seeding

Normalize F1-F13 in arifosmcp_floor_rules:

```sql
INSERT INTO arifosmcp_floor_rules (floor_code, rule_name, constraint_definition, is_active)
VALUES
  ('F01', 'AMANAH',  '{"type": "HARD", "invariant": "Reversible-first; irreversible → 888_HOLD"}', TRUE),
  ('F02', 'TRUTH',   '{"type": "HARD", "invariant": "≥0.99 accuracy or declare uncertainty band"}', TRUE),
  ('F03', 'WITNESS', '{"type": "SOFT", "invariant": "Theory · constitution · intent must align"}', TRUE),
  ('F04', 'CLARITY', '{"type": "SOFT", "invariant": "Every output reduces entropy (ΔS ≤ 0)"}', TRUE),
  ('F05', 'PEACE',   '{"type": "SOFT", "invariant": "Peace ≥ 1.0; de-escalate, guard maruah"}', TRUE),
  ('F06', 'EMPATHY', '{"type": "SOFT", "invariant": "Dignity-first; ASEAN/MY context"}', TRUE),
  ('F07', 'HUMILITY', '{"type": "SOFT", "invariant": "Uncertainty band 0.03–0.05; no fake certainty"}', TRUE),
  ('F08', 'GENIUS',  '{"type": "SOFT", "invariant": "Maintain intelligence quality, system health"}', TRUE),
  ('F09', 'ANTIHANTU', '{"type": "HARD", "invariant": "C_dark < 0.30, no consciousness claims"}', TRUE),
  ('F10', 'ONTOLOGY', '{"type": "HARD", "invariant": "AI-only ontology; no soul/feelings claims"}', TRUE),
  ('F11', 'AUTH',    '{"type": "HARD", "invariant": "Verify identity before sensitive ops"}', TRUE),
  ('F12', 'INJECTION', '{"type": "HARD", "invariant": "Sanitize inputs; no prompt injection"}', TRUE),
  ('F13', 'SOVEREIGN', '{"type": "HARD", "invariant": "Human veto absolute"}', TRUE)
ON CONFLICT (floor_code) DO NOTHING;
```

---

## 8. Migration Sequence

### Phase A — Write adapter (before any DB changes)

Before SQL runs, build the write path adapter:

```
arifOS MCP
  ↓
record_tool_call(tool_name, organ, session_id, verdict, risk_tier)
record_approval(ticket_id, action_plan, human_verdict)
record_judge_verdict(verdict_id, session_id, organ, candidate, verdict, confidence)
record_evidence(evidence_id, source_organ, source_url, content_hash, confidence)
record_artifact(artifact_id, organ, artifact_type, storage_path, session_id)
seal_vault999(seal_id, prev_hash, payload, human_witness)
  ↓
Supabase adapter (graceful fallback: if Supabase is down, log locally)
```

This adapter must handle Supabase being offline — local fallback writes to JSONL, retries when connection restores.

### Phase B — Append-only triggers (first SQL)

Apply append-only triggers to existing tables:
1. `vault_sealed_events`
2. `vault_outcomes`
3. `vault_shim_hits`
4. `arifosmcp_tool_calls`
5. `arifosmcp_approval_tickets`

Verify each trigger fires correctly with a test INSERT + attempted UPDATE.

### Phase C — s000 tables (second SQL wave)

Create in order:
1. `s000_judge_verdicts`
2. `s000_evidence_items`
3. `s000_evidence_citations`
4. `s000_artifacts`
5. `s000_service_identities`
6. `s000_mcp_servers`
7. `s000_mcp_tools`
8. `s000_mcp_manifest_snapshots`

Apply indexes after each table.

### Phase D — s999 vault (third SQL wave)

1. Create `s999_vault999_ledger`
2. Apply append-only trigger
3. Verify hash chain with test entry

### Phase E — AAA views (fourth SQL wave)

Create all AAA views. No data modification.

### Phase F — F1-F13 seed

Seed constitutional floor rules. Idempotent — safe to re-run.

### Phase G — Backfill plan

After Phase A-F complete, backfill plan:
- Some historical tool_calls and approvals may need review
- vault_sealed_events backfill into s999_vault999_ledger: TBD — after review
- Not done in initial Phase 1

---

## 9. What Supabase Is NOT

These are out of scope for this phase:

- Supabase Auth for agent login — not needed
- Supabase Edge Functions as organ gateways — NATS handles this
- Supabase pg_cron as health authority — Prometheus still owns this
- Supabase pgmq as NATS replacement — NATS still owns this
- Supabase pgvector as Qdrant replacement — Qdrant still owns this
- Supabase as session authority — arifOS MCP still owns this

arifOS remains sovereign. Supabase is ledger, not engine.

---

## 10. Rollback Plan

If migration fails mid-way:
1. All new tables use `IF NOT EXISTS` / `CREATE TABLE IF NOT EXISTS` — idempotent
2. Append-only triggers do not block SELECT — reads always work
3. Existing tables unchanged except triggers — safe to drop triggers
4. No data destruction in any step

---

## 11. Verification Checklist

After each phase, verify:

- [ ] Append-only triggers block UPDATE/DELETE on protected tables
- [ ] New tables have correct indexes
- [ ] AAA views return expected data shape
- [ ] F1-F13 floor rules seeded correctly
- [ ] arifOS can write to Supabase and fall back to local JSONL if offline
- [ ] Tool calls, approvals, verdicts all route through adapter

---

## 12. Files to Produce

| File | Purpose |
|------|---------|
| `docs/architecture/SUPABASE_PHASE1_SPEC.md` | This spec |
| `arifosmcp/adapters/record_receipts.py` | Write path adapter |
| `arifosmcp/adapters/supabase_fallback.py` | Graceful offline fallback |
| `supabase/migrations/004_append_only_triggers.sql` | Phase B |
| `supabase/migrations/005_s000_intake_tables.sql` | Phase C |
| `supabase/migrations/006_s999_vault_ledger.sql` | Phase D |
| `supabase/migrations/007_aaa_views.sql` | Phase E |
| `supabase/migrations/008_floor_rules_seed.sql` | Phase F |

---

**DITEMPA BUKAN DIBERI** — Spec written. No SQL executed. Awaiting Arif's approval.