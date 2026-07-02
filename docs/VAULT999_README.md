# VAULT999 — Constitutional Append-Only Ledger

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

> **Last updated:** 2026-05-25  
> **Status:** Schema deployed to Supabase ✅ | Services NOT YET STARTED ❌  
> **Authority:** F13 SOVEREIGN — `ack_irreversible` blocked until services live  
> **Canonical doc:** This file. If you are an agent landing on this system, read this top-to-bottom before touching Vault999.

---

## 1. What Vault999 Is

Vault999 is the **immutable constitutional ledger** of the arifOS Federation. It records:
- **Sovereign SEALs** — binding, irreversible decisions ratified by Arif
- **VOIDs** — rejected actions with full audit trail
- **Audit receipts** — non-binding clerk/tool observations
- **Cooling queue** — actions awaiting human review
- **Human reviews** — ratification/void decisions with signatures

Every entry is:
- **Append-only** — never deleted, never modified
- **Cryptographically chained** — BLAKE3 hash chain linking `prev_seal_id` → current seal
- **Ed25519 signed** — sovereign signature over canonical payload
- **Multi-witnessed** — human + AI + evidence attestations

---

## 2. Architecture (Two Services)

Vault999 is **not one service** — it is two cooperating services:

```
┌─────────────────────────────────────────────────────────────┐
│                     VAULT999 ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐         ┌──────────────┐                │
│   │  vault999    │  HTTP   │vault999-     │                │
│   │  API Layer   │◄────────│writer        │                │
│   │  (port 8100) │         │(port 5001)   │                │
│   └──────┬───────┘         └──────┬───────┘                │
│          │                        │                         │
│          │  asyncpg pool          │  asyncpg pool          │
│          │                        │                         │
│          ▼                        ▼                         │
│   ┌─────────────────────────────────────┐                  │
│   │   Supabase PostgreSQL               │                  │
│   │   db.utbmmjmbolmuahwixjqc.        │                  │
│   │   supabase.co:5432                │                  │
│   │   Database: postgres                │                  │
│   │   Schema: public                    │                  │
│   └─────────────────────────────────────┘                  │
│                                                             │
│   Local fallback (JSONL):                                  │
│   /root/arifOS/VAULT999/outcomes.jsonl  (14,786 entries)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 vault999 (API Layer)
- **Port:** 8100
- **Source:** `/root/compose/vault999/server.py`
- **Role:** Exposes REST API for queries, audits, receipts, health
- **DB env:** `DATABASE_URL`
- **Writer env:** `VAULT_WRITER_URL` (points to writer on 5001)
- **Auth:** `VAULT_ADMIN_TOKEN` header for admin endpoints

### 2.2 vault999-writer (Write Layer)
- **Port:** 5001
- **Source:** Embedded in `compose-vault999-writer:v1.0.0` Docker image
- **Role:** **Only service allowed to INSERT into `vault_seals`**. Enforces Ed25519 signature validation.
- **DB env:** `VAULT999_DB`
- **Auth:** `VAULT_WRITER_TOKEN` header

**Separation of duties:** The API layer can read and queue. The writer layer alone can append to the ledger. This prevents a compromised API from forging seals.

---

## 3. Database Schema (11 Tables)

**Location:** Supabase `postgres` database, `public` schema  
**DDL source:** `/tmp/vault999_schema_clean.sql` (extracted from 2026-05-11 backup)

### Core Ledger Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `vault_seals` | **The canonical append-only ledger** | `id`, `seal_hash`, `chain_hash`, `action`, `epoch`, `payload`, `prev_seal_id`, `verdict` |
| `cooling_queue` | Pending human-review actions | `id`, `status` (`awaiting_human`\|`ratified`\|`voided`), `action_type`, `payload`, `session_id`, `proposal_hash` |
| `human_reviews` | Ratification/VOID decisions | `review_id`, `cooling_id`, `reviewer_id`, `decision`, `reason`, `human_signature` |
| `vault999_witness` | Cross-witness attestations | `ledger_id`, `human_witness`, `ai_witness`, `evidence_witness`, `w_score`, `metadata` |
| `approval_tickets` | Governance approval tickets | `ticket_id`, `session_id`, `status`, `risk_level`, `intent_model`, `data` (jsonb) |

### Memory Tables

| Table | Purpose |
|-------|---------|
| `memory_store` | L4 canonical memory records |
| `memory_records` | Memory record registry with self-referential FK |
| `memory_audit_log` | Memory audit trail |
| `memory_review_queue` | Pending memory reviews |
| `memory_revocations` | Revoked memory entries |
| `memory_write_queue` | Async memory writes |

### Sequences
- `cooling_queue_id_seq`
- `human_reviews_review_id_seq`
- `vault999_witness_id_seq`
- `vault_seals_id_seq`

### Indexes
15+ btree indexes on `session_id`, `actor_id`, `status`, `created_at`, `event_type`, etc.

### FK Constraints
- `vault_seals(prev_seal_id)` → `vault_seals(id)` (self-referential chain)
- `memory_records(superseded_by)` → `memory_records(memory_id)`
- `memory_review_queue(memory_id)` → `memory_records(memory_id)` ON DELETE CASCADE
- `memory_revocations(memory_id)` → `memory_records(memory_id)` ON DELETE CASCADE
- `memory_write_queue(memory_id)` → `memory_records(memory_id)` ON DELETE CASCADE

---

## 4. Environment Variables

Required in `/etc/arifOS/secrets.env` (or systemd `Environment=`):

```bash
# For vault999 API layer (port 8100)
DATABASE_URL=postgresql://postgres:<PASSWORD>@db.utbmmjmbolmuahwixjqc.supabase.co:5432/postgres?sslmode=require
VAULT_WRITER_URL=http://localhost:5001
VAULT_ADMIN_TOKEN=<strong-random-token>
PORT=8100

# For vault999-writer (port 5001)
VAULT999_DB=postgresql://postgres:<PASSWORD>@db.utbmmjmbolmuahwixjqc.supabase.co:5432/postgres?sslmode=require
VAULT_WRITER_TOKEN=<strong-random-token>
PORT=5001
```

**Critical notes:**
- `sslmode=require` is **mandatory** for Supabase
- Hostname is `db.utbmmjmbolmuahwixjqc.supabase.co` (NOT `utbmmjmbolmuahwixjqc.supabase.co`)
- Default Supabase database name is `postgres`, not `vault999`
- Tables live in `public` schema (verified by DDL)
- `VAULT_ADMIN_TOKEN` and `VAULT_WRITER_TOKEN` must match `compose/secrets/vault_writer_token`

---

## 5. API Reference

### 5.1 vault999 (API Layer) — Port 8100

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/health` | None | Service health |
| GET | `/cli/pending` | None | List `cooling_queue` awaiting human review |
| GET | `/cli/inspect/{cooling_id}` | None | Full cooling_queue record |
| POST | `/cli/ratify` | `VAULT_ADMIN_TOKEN` | Human ratifies SEAL or VOID |
| GET | `/vault/status` | None | Vault health + integrity (count seals, reviews, pending) |
| GET | `/vault/audit/{seal_id}` | None | Full audit trace for a seal |
| GET | `/vault/receipt/{seal_id}` | None | Human-readable seal receipt |
| GET | `/debug/test/{seal_id}` | None | Test endpoint |

**RatifyRequest payload:**
```json
{
  "cooling_id": "uuid-string",
  "decision": "SEAL",
  "human_signature": "base64-sig",
  "review_reason": "Minimum 10 chars required",
  "irreversibility_ack": true,
  "review_channel": "cli"
}
```

### 5.2 vault999-writer (Write Layer) — Port 5001

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/health` | None | Service health |
| GET | `/pending` | None | List awaiting_human cooling_queue |
| GET | `/inspect/{cooling_id}` | None | Single cooling_queue record |
| POST | `/seal` | `VAULT_WRITER_TOKEN` | Write SOVEREIGN SEAL (binding) |
| POST | `/audit-receipt` | `VAULT_WRITER_TOKEN` | Write non-binding audit receipt |
| POST | `/ratify` | `VAULT_WRITER_TOKEN` | Ratify from cooling queue |

**SovereignSealRequest payload:**
```json
{
  "cooling_id": "uuid-or-null",
  "cli_proposal_hash": "hash-or-null",
  "session_id": "session-uuid",
  "agent_id": "agent-name",
  "action": "action-description",
  "payload": {},
  "epoch": "2026-05-25T11:00:00Z",
  "verdict": "SEAL",
  "human_ratifier": "arif",
  "ed25519_signature": "base64-ed25519-sig",
  "ratified_at": "2026-05-25T11:00:00Z",
  "irreversibility_ack": true,
  "tags": [],
  "metadata": {}
}
```

---

## 6. How to Start / Stop

### Start (Bare-Metal, NOT Docker)

```bash
# 1. Ensure schema exists in Supabase
psql "$DATABASE_URL" -c "SELECT count(*) FROM vault_seals;"
# Expected: 0 (empty, ready)

# 2. Start writer first (API layer depends on it)
sudo systemctl start vault999-writer
sleep 2
curl -s http://localhost:5001/health

# 3. Start API layer
sudo systemctl start vault999
curl -s http://localhost:8100/health

# 4. Verify federation health
curl -s http://localhost:8088/health | python3 -m json.tool
# Expected: "vault999_health": "healthy"
```

### Stop

```bash
sudo systemctl stop vault999
sudo systemctl stop vault999-writer
```

### Logs

```bash
journalctl -u vault999 -f
journalctl -u vault999-writer -f
```

---

## 7. How to Verify Integrity

### 7.1 Check Chain Hash

```bash
curl -s http://localhost:8100/vault/status | python3 -m json.tool
```

Look for:
- `vault_seals_total` — count of seals
- `human_reviews_total` — count of reviews
- `cooling_queue_pending` — actions awaiting review
- `latest_seal.chain_hash` — should be non-null after first seal

### 7.2 Local JSONL vs Postgres

Local fallback ledger:
```bash
wc -l /root/arifOS/VAULT999/outcomes.jsonl
# 14,786 entries (historical, pre-Supabase)
```

Postgres ledger:
```bash
psql "$DATABASE_URL" -c "SELECT count(*) FROM vault_seals;"
# 0 entries (fresh Supabase, starts empty)
```

**Important:** The local `outcomes.jsonl` is historical data from before the Supabase migration. It is NOT automatically backfilled into Postgres. If you need historical data in Supabase, that's a separate migration task.

### 7.3 Daily Attestation Cron

```bash
# Runs daily at 03:00
0 3 * * * /usr/bin/python3 /root/arifOS/core/vault999/bridge_from_vault.py attest >> /var/log/vault999.log 2>&1
```

This creates a SHA-256 attestation of the local vault state. It does **not** write to Supabase — it attests the local JSONL file.

---

## 8. Troubleshooting

### Issue: `vault999_health: unreachable`

**Cause:** Services not running.  
**Fix:** `sudo systemctl start vault999-writer && sudo systemctl start vault999`

### Issue: `asyncpg.exceptions.InvalidPasswordError`

**Cause:** Wrong Supabase password or wrong hostname.  
**Fix:** Verify password from Supabase Dashboard → Database → Connection String. Verify hostname is `db.utbmmjmbolmuahwixjqc.supabase.co`.

### Issue: `asyncpg.exceptions.PostgresError: relation "vault_seals" does not exist`

**Cause:** Schema not applied to Supabase.  
**Fix:** `psql "$DATABASE_URL" -f /tmp/vault999_schema_clean.sql`

### Issue: `SSL negotiation failed`

**Cause:** Missing `?sslmode=require` in connection string.  
**Fix:** Append `?sslmode=require` to `DATABASE_URL` and `VAULT999_DB`.

### Issue: Writer returns `403 Forbidden`

**Cause:** `VAULT_WRITER_TOKEN` mismatch.  
**Fix:** Verify token in `/etc/arifOS/secrets.env` matches `/root/compose/secrets/vault_writer_token`.

### Issue: `ed25519_signature` verification fails

**Cause:** Signature computed over wrong canonical payload.  
**Fix:** Ensure signature is Ed25519 over `BLAKE3(action + epoch + payload_json)` in canonical form.

---

## 9. Security Model

| Layer | Protection |
|-------|-----------|
| **Network** | Both services bind `127.0.0.1` only (not 0.0.0.0). Caddy reverse-proxies `vault.arif-fazil.com` if needed. |
| **Authentication** | `VAULT_ADMIN_TOKEN` (API layer) and `VAULT_WRITER_TOKEN` (writer layer) — long random strings. |
| **Cryptographic** | Ed25519 signatures required for sovereign seals. `human_ratifier` must be `"arif"`. |
| **Chain integrity** | BLAKE3 hash chain: `chain_hash = BLAKE3(prev_chain_hash + action + epoch + payload)`. Tampering breaks the chain. |
| **Append-only** | No UPDATE or DELETE operations. `vault_seals` is insert-only. |
| **Backup** | Supabase point-in-time recovery + local JSONL attestation cron. |

---

## 10. For Agents: What You Can and Cannot Do

### ✅ Autonomous (No Human Approval)
- Read vault status, audit seals, inspect cooling queue
- Write **audit receipts** (non-binding, `claim_state: OBSERVED|DRAFT|HYPOTHESIS`)
- Query pending actions for Arif's review
- Check health endpoints

### ❌ Requires Human Approval (888_HOLD)
- Write **sovereign SEAL** (`verdict: SEAL`, `irreversibility_ack: true`)
- Write **VOID** (`verdict: VOID`)
- Ratify from cooling queue (`/cli/ratify`)
- Modify schema (DDL changes)
- Rotate `VAULT_ADMIN_TOKEN` or `VAULT_WRITER_TOKEN`
- Backfill historical `outcomes.jsonl` into Supabase

### ⚠️ Requires Sovereign Input
- `ack_irreversible` flag on any action → Arif must explicitly set `irreversibility_ack: true`
- Any decision with `human_ratifier: "arif"` → Arif must provide Ed25519 signature

---

## 11. Quick Reference

```bash
# Health checks
curl -s http://localhost:8100/health
curl -s http://localhost:5001/health

# Vault status
curl -s http://localhost:8100/vault/status | python3 -m json.tool

# Pending reviews
curl -s http://localhost:8100/cli/pending | python3 -m json.tool

# Inspect a cooling queue entry
curl -s http://localhost:8100/cli/inspect/123

# Audit a seal
curl -s http://localhost:8100/vault/audit/<seal_id>

# Write audit receipt (autonomous, non-binding)
curl -s -X POST http://localhost:5001/audit-receipt \
  -H "Authorization: Bearer $VAULT_WRITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"agent-name","action":"test","payload":{},"claim_state":"OBSERVED","binding":false}'
```

---

## 12. Current State (2026-05-25)

| Component | Status |
|-----------|--------|
| Supabase schema | ✅ Deployed (11 tables, 4 sequences, 15+ indexes) |
| vault999 service (8100) | ❌ Not started — needs systemd unit |
| vault999-writer service (5001) | ❌ Not started — needs systemd unit |
| Local JSONL ledger | ✅ 14,786 entries (`/root/arifOS/VAULT999/outcomes.jsonl`) |
| Daily attestation cron | ✅ Active (03:00 daily) |
| `arif_vault_seal` MCP tool | ✅ Registered, returns `HOLD` until services live |

**Next step:** Create systemd units for both services and start them. See Section 6.

---

*🪙 999 SEAL | VAULT999 Canonical | DITEMPA BUKAN DIBERI*
