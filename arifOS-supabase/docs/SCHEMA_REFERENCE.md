# arifOS Schema Reference

## Table Index

| Table | Migration Line | Purpose |
|-------|----------------|---------|
| `arifosmcp_vault_seals` | CREATE TABLE #1 | VAULT999 immutable ledger |
| `arifosmcp_sessions` | CREATE TABLE #2 | Agent session lifecycle |
| `arifosmcp_tool_calls` | CREATE TABLE #3 | Per-tool audit log |
| `arifosmcp_canon_records` | CREATE TABLE #4 | ARCHIVIST ADR ledger |
| `arifosmcp_approval_tickets` | CREATE TABLE #5 | 888_HOLD queue |
| `arifosmcp_floor_rules` | CREATE TABLE #6 | F1–F13 thresholds |
| `arifosmcp_agent_telemetry` | CREATE TABLE #7 | MerkleV3 source rows |
| `arifosmcp_daily_roots` | CREATE TABLE #8 | MerkleV3 daily anchors |
| `arifosmcp_transactions` | CREATE TABLE #9 | WEALTH transaction ledger |
| `arifosmcp_portfolio_snapshots` | CREATE TABLE #10 | WEALTH portfolio snapshots |

---

## 1. arifosmcp_vault_seals

**Purpose:** VAULT999 immutable seal ledger. Every terminal verdict (SEAL/HOLD/SABAR/VOID) is written here and never modified or deleted.

**Trigger:** `no_arifosmcp_vault_seal_mutation` — blocks UPDATE and DELETE on this table. Immutability enforced at DB level.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `seal_id` | TEXT | Unique. UUID from `generateSealId()`. Used in `find_vault_seal(seal_id)` |
| `session_id` | TEXT | Agent session. Indexed for session-based queries |
| `verdict` | TEXT | SEAL \| HOLD \| SABAR \| VOID |
| `timestamp` | TIMESTAMPTZ | ISO epoch of verdict. Indexed DESC |
| `record_id` | TEXT | SHA-256 of full content. Merkle leaf ID. Used in MerkleV3 chain |
| `prev_hash` | TEXT | SHA-256 of previous record. Chain link. Row 1 prev_hash = row_hash (genesis seed) |
| `hashofinput` | TEXT | SHA-256(task + finalText + sessionId + turnCount) |
| `telemetrysnapshot` | JSONB | `{ dS, peace2, psi_le, W3, G }` |
| `floors_triggered` | TEXT[] | Array of floor codes triggered |
| `irreversibilityacknowledged` | BOOLEAN | Whether agent acknowledged irreversibility |
| `task` | TEXT | Full task description |
| `final_text` | TEXT | Agent final response text |
| `turn_count` | INTEGER | Number of turns in session |
| `profile_name` | TEXT | Agent profile used (e.g., "explore", "fix", "coordinator") |
| `data` | JSONB | Full VaultSealRecord as JSON. Preserved for complete reconstruction |
| `created_at` | TIMESTAMPTZ | Row creation time |

**Indexes:**
```sql
idx_arifosmcp_vault_seals_session    ON (session_id)
idx_arifosmcp_vault_seals_verdict    ON (verdict)
idx_arifosmcp_vault_seals_timestamp  ON (timestamp DESC)
idx_arifosmcp_vault_seals_record_id  ON (record_id)
```

**MerkleV3 Compatible:** Yes. `record_id` and `prev_hash` columns support full chain verification.

**Source in A-FORGE:** `PostgresVaultClient.seal()` → `VaultSealRecord`

---

## 2. arifosmcp_sessions

**Purpose:** Agent session lifecycle. Replaces `/root/WELL/state.json`.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `session_id` | TEXT | Unique session ID. Used in queries and foreign key |
| `agent_id` | TEXT | Agent identifier (e.g., "AAA-Agent", "ENGINEER-Agent") |
| `initiated_at` | TIMESTAMPTZ | Session start time |
| `risk_tier` | TEXT | low \| medium \| high \| critical. From session metadata |
| `declared_intent` | TEXT | Intent model: informational \| advisory \| execution \| speculative |
| `final_verdict` | TEXT | Set on session close. SEAL \| HOLD \| SABAR \| VOID |
| `closed_at` | TIMESTAMPTZ | Session close time. NULL until closed |

**Indexes:**
```sql
idx_arifosmcp_sessions_agent     ON (agent_id)
idx_arifosmcp_sessions_initiated ON (initiated_at DESC)
idx_arifosmcp_sessions_session_id ON (session_id)
```

**Source in A-FORGE:**
- `PostgresVaultClient.openSession()` — inserts at session start
- `PostgresVaultClient.sealSession()` — updates final_verdict + closed_at at session end

---

## 3. arifosmcp_tool_calls

**Purpose:** Per-tool execution audit log. Records every tool invocation with constitutional verdict.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `run_id` | TEXT | Optional run identifier |
| `session_id` | TEXT | Links to agent session |
| `tool_name` | TEXT | Tool name (e.g., "applyPatches", "run_command") |
| `organ` | TEXT | Tool category: EditorTools, ShellTools, SearchTools, etc. |
| `input_hash` | TEXT | SHA-256 of tool input |
| `output_hash` | TEXT | SHA-256 of tool output |
| `tool_args` | JSONB | Full tool arguments |
| `tool_result` | TEXT | Tool result text |
| `duration_ms` | INTEGER | Execution time in milliseconds |
| `floor_triggered` | TEXT[] | Array of floor codes triggered during this tool call |
| `verdict` | TEXT | Constitutional verdict: PASS \| HOLD \| VOID |
| `created_at` | TIMESTAMPTZ | Call time |

**Indexes:**
```sql
idx_arifosmcp_tool_calls_session ON (session_id)
idx_arifosmcp_tool_calls_tool   ON (tool_name)
idx_arifosmcp_tool_calls_created ON (created_at DESC)
```

**Source in A-FORGE:** `PostgresVaultClient.logToolCall()` → `ToolCallRecord`

---

## 4. arifosmcp_canon_records

**Purpose:** ARCHIVIST agent ADR ledger. Every SEAL verdict writes a canon record here.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `adr_id` | TEXT | Unique ADR identifier. Format: ADR-NNNNN or AUTO-XXXXXXXX |
| `title` | TEXT | First line of task, capped at 100 chars |
| `decision` | TEXT | finalText slice, 500 chars |
| `rationale` | TEXT | Full task text |
| `agent_id` | TEXT | Which agent generated this decision |
| `session_id` | TEXT | Links to agent session |
| `epoch` | TIMESTAMPTZ | Decision timestamp |
| `sealed_by` | TEXT | "Muhammad Arif bin Fazil" — sovereignty marker |
| `payload` | JSONB | Full VaultSealRecord as JSON |

**Indexes:**
```sql
idx_arifosmcp_canon_records_adr      ON (adr_id)
idx_arifosmcp_canon_records_session ON (session_id)
idx_arifosmcp_canon_records_agent   ON (agent_id)
```

**Source in A-FORGE:** `PostgresVaultClient.writeToCanon()` — called automatically on every SEAL verdict.

**ADR ID Extraction:**
- Looks for `ADR-[0-9]+` pattern in task text
- If found: uses that ADR ID
- If not found: generates `AUTO-<record_id.slice(0,8).toUpperCase()>`

---

## 5. arifosmcp_approval_tickets

**Purpose:** 888_HOLD human escalation queue. Tracks states: PENDING → DISPATCHED → [APPROVED|REJECTED|MODIFY_REQUIRED|EXPIRED] → REPLAYED.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `ticket_id` | TEXT | Unique ticket ID |
| `session_id` | TEXT | Agent session |
| `status` | TEXT | PENDING \| DISPATCHED \| ACKED \| APPROVED \| REJECTED \| MODIFY_REQUIRED \| EXPIRED \| REPLAYED |
| `risk_level` | TEXT | low \| medium \| high \| critical |
| `intent_model` | TEXT | informational \| advisory \| execution \| speculative |
| `domain` | TEXT | Optional domain label |
| `created_at` | TIMESTAMPTZ | Ticket creation time |
| `data` | JSONB | Full ApprovalTicket as JSON — preserves all fields |

**Indexes:**
```sql
idx_arifosmcp_approval_tickets_session ON (session_id)
idx_arifosmcp_approval_tickets_status  ON (status)
idx_arifosmcp_approval_tickets_risk    ON (risk_level)
idx_arifosmcp_approval_tickets_created ON (created_at DESC)
```

**Source in A-FORGE:** `PostgresTicketStore.createTicket()` → `ApprovalTicket`

---

## 6. arifosmcp_floor_rules

**Purpose:** F1–F13 constitutional floor thresholds. Loaded at startup for adaptive governance.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `floor_id` | TEXT | Unique floor ID (e.g., "F3", "F7") |
| `code` | TEXT | Floor code |
| `name` | TEXT | Floor name |
| `type` | TEXT | Floor type |
| `description` | TEXT | Floor description |
| `seal_threshold` | NUMERIC | Threshold for SEAL verdict |
| `void_threshold` | NUMERIC | Threshold for VOID verdict |
| `active` | BOOLEAN | Whether floor is active |

**Indexes:**
```sql
idx_arifosmcp_floor_rules_code ON (code)
```

**Source in A-FORGE:** `PostgresVaultClient.loadConstitution()`

---

## 7. arifosmcp_agent_telemetry

**Purpose:** Thermodynamic telemetry rows. Source data for MerkleV3Service chain building and verification.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `epoch` | TIMESTAMPTZ | Telemetry timestamp |
| `session_id` | TEXT | Optional session link |
| `agent_id` | TEXT | Optional agent identifier |
| `ds` | NUMERIC | Thermodynamic cost |
| `peace2` | NUMERIC | Peace metric |
| `kappa_r` | NUMERIC | Reversibility score |
| `shadow` | NUMERIC | Shadow metric |
| `confidence` | NUMERIC | Confidence score |
| `psi_le` | NUMERIC | PSI metric |
| `verdict` | TEXT | VaultVerdict |
| `witness_human` | NUMERIC | Human witness |
| `witness_ai` | NUMERIC | AI witness |
| `witness_earth` | NUMERIC | Earth witness |
| `qdf` | TEXT | Quality descriptor |
| `prev_hash` | TEXT | Previous row hash (chain link) |
| `row_hash` | TEXT | SHA-256 of content fields + prev_hash |

**Indexes:**
```sql
idx_arifosmcp_telemetry_epoch    ON (epoch DESC)
idx_arifosmcp_telemetry_session  ON (session_id)
idx_arifosmcp_telemetry_row_hash ON (row_hash)
```

**Source in A-FORGE:** `MerkleV3Service.buildChainForDate()` writes here; `MerkleV3Service.loadRowsForDate()` reads from here.

---

## 8. arifosmcp_daily_roots

**Purpose:** Daily Merkle root anchors. Upserted by `MerkleV3Service.computeAndAnchorRoot()` at end of day.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `root_date` | DATE | Unique date (one root per day) |
| `row_count` | INTEGER | Number of telemetry rows for that day |
| `merkle_root` | TEXT | SHA-256(sorted(all row_hash values)) |
| `anchored` | BOOLEAN | True when root is computed and verified |
| `created_at` | TIMESTAMPTZ | Anchor time |

**Indexes:**
```sql
idx_arifosmcp_daily_roots_date ON (root_date)
```

**Source in A-FORGE:** `MerkleV3Service.computeAndAnchorRoot()`

---

## 9. arifosmcp_transactions

**Purpose:** WEALTH transaction ledger.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `tx_type` | TEXT | Transaction type |
| `asset` | TEXT | Asset identifier |
| `amount` | NUMERIC | Transaction amount |
| `currency` | TEXT | Currency code (default: MYR) |
| `metadata` | JSONB | Additional transaction metadata |
| `epoch` | TIMESTAMPTZ | Transaction time |

**Indexes:**
```sql
idx_arifosmcp_transactions_type   ON (tx_type)
idx_arifosmcp_transactions_asset  ON (asset)
idx_arifosmcp_transactions_epoch  ON (epoch DESC)
```

---

## 10. arifosmcp_portfolio_snapshots

**Purpose:** WEALTH portfolio state at point in time.

**Columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | Primary key |
| `snapshot_ts` | TIMESTAMPTZ | Snapshot time |
| `holdings` | JSONB | Portfolio holdings as JSON |
| `total_value` | NUMERIC | Total portfolio value |
| `currency` | TEXT | Currency code (default: MYR) |

**Indexes:**
```sql
idx_arifosmcp_snapshots_ts ON (snapshot_ts DESC)
```

---

## Migration Version History

| Version | Date | Changes |
|---------|------|---------|
| 20260417000000 | 2026-04-17 | Initial schema — 9 tables, append-only trigger, MerkleV3 support |

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

```
Epoch: 2026-04-17T18:00+08
Verdict: SCHEMA_REFERENCE_SEALED
```