# arifOS Supabase Deployment Guide

## Overview

This guide walks through adding Supabase as the persistent data layer for arifOS. You are replacing all `/root/...` and `/tmp/...` JSON state files with proper Postgres-backed tables.

**Time estimate:** 55 minutes for full deployment.

---

## Before You Start

**F13 HOLD — Account Ownership Decision**

You must decide before proceeding:

| Option | URL Structure | Who Controls | Billing |
|--------|---------------|--------------|---------|
| **Personal account** | `https://xxxxx.supabase.co` | Arif (you) | Personal card |
| **`arifos` org** | `https://xxxxx.supabase.co` | Organization | Org billing |

This is sovereignty. Not a technical question.
**You hold final veto, Arif.**

---

## Step 1 — Create Supabase Project

1. Go to [supabase.com](https://supabase.com) → Sign in → New Project
2. Choose **Southeast Asia (Singapore)** region — lowest latency from Seri Kembangan
3. Name: `arifosmcp` (all lowercase, no spaces)
4. Set a strong DB password — **save it, it cannot be recovered later**
5. Tier: **Free** (2 active projects, 500 MB DB, 1 GB Storage)

---

## Step 2 — Install Supabase CLI

```bash
# Option A: Homebrew (macOS/Linux)
brew install supabase/tap/supabase

# Option B: npm
npm install -g supabase

# Verify installation
supabase --version
```

---

## Step 3 — Link CLI to Project

```bash
# Navigate to migration project
cd /root/arifOS-supabase

# Login to Supabase
supabase login

# Get project-ref from: Dashboard → Settings → General
# It looks like: xxxxx-xxxxx-xxxxx
supabase link --project-ref <YOUR_PROJECT_REF>
```

---

## Step 4 — Run Migration

The migration file is at `supabase/migrations/20260417000000_initial_arifosmcp_schema.sql`.

It creates 9 tables with proper indexes, triggers for append-only enforcement, and all columns needed for MerkleV3 chain verification.

```bash
# Dry run first (validates without applying)
supabase db push --dry-run

# If dry-run passes, apply
supabase db push
```

**What happens:**
- Supabase creates `supabase_migrations.schema_migrations` table (migration ledger)
- Creates 9 tables with indexes
- Creates append-only trigger on `arifosmcp_vault_seals`
- No data is lost — this is schema-only

---

## Step 5 — Verify Tables Created

Go to Supabase Dashboard → Table Editor. You should see:

| Table | Purpose |
|-------|---------|
| `arifosmcp_vault_seals` | VAULT999 immutable ledger |
| `arifosmcp_sessions` | Agent session lifecycle |
| `arifosmcp_tool_calls` | Per-tool audit log |
| `arifosmcp_canon_records` | ARCHIVIST ADR ledger |
| `arifosmcp_approval_tickets` | 888_HOLD queue |
| `arifosmcp_floor_rules` | F1–F13 thresholds |
| `arifosmcp_agent_telemetry` | MerkleV3 source rows |
| `arifosmcp_daily_roots` | MerkleV3 daily anchors |
| `arifosmcp_transactions` | WEALTH transaction ledger |
| `arifosmcp_portfolio_snapshots` | WEALTH portfolio snapshots |

Run this SQL to verify programmatically:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'arifosmcp_%'
ORDER BY table_name;
```

---

## Step 6 — Get API Credentials

From Supabase Dashboard → Settings → API, copy:

- **Project URL**: `https://<project-ref>.supabase.co`
- **service_role key**: The JWT under `service_role` (NOT anon key)

**Store the service_role key securely.** It cannot be retrieved again after leaving the page.

---

## Step 7 — Wire Env Vars into Horizon

Go to Prefect Horizon → AFWELL env var panel:

```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_jwt>
```

Then WEALTH panel (same values):

```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_jwt>
```

Restart both services after adding.

---

## Step 8 — Install Python Client

On your Horizon project shell:

```bash
pip install supabase
```

This installs `supabase-py v2` with both sync and async support.

---

## Step 9 — Test Connection

```python
from supabase import create_client
import os

sb = create_client(
    os.environ['SUPABASE_URL'],
    os.environ['SUPABASE_SERVICE_ROLE_KEY']
)

# Test session table
result = sb.table('arifosmcp_sessions').select('count').execute()
print(f"Session count: {result.count}")
```

Expected output: `Session count: 0` (empty at start)
No auth errors.

---

## Step 10 — Replace First JSON State Write

Find in your code:

```python
# OLD — file-based state
import json
with open('/root/WELL/state.json', 'w') as f:
    json.dump(state, f)
```

Replace with:

```python
# NEW — Supabase
from supabase_client import open_session

open_session(
    session_id=session_id,
    agent_id=agent_id,
    risk_tier='medium',
    declared_intent='explore'
)
```

Find and replace all:
- `/root/WELL/state.json` → `arifosmcp_sessions`
- `/root/.agent-workbench/vault999.jsonl` → `arifosmcp_vault_seals`
- `/root/.arifos/tickets.jsonl` → `arifosmcp_approval_tickets`

---

## Step 11 — Verify Data Persists

Run an agent cycle on Horizon:
1. Observe session record in `arifosmcp_sessions` (Supabase dashboard)
2. Observe tool calls in `arifosmcp_tool_calls`
3. Observe seal in `arifosmcp_vault_seals`
4. **Redeploy** the Horizon service
5. Check data is still there — this confirms persistence

---

## Step 12 — Verify MerkleV3 Compatible

```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'arifosmcp_vault_seals'
AND column_name IN ('record_id', 'prev_hash');
```

Both columns must exist for MerkleV3 chain verification to work.

---

## Step 13 — Commit to Git

```bash
cd /root/arifOS-supabase
git init
git add supabase/migrations/20260417000000_initial_arifosmcp_schema.sql
git add clients/
git add docs/
git commit -m "arifOS Supabase schema v1.0 — 9 tables, migration-ready

- VAULT999 seal ledger with MerkleV3 support
- Session state replacing /root/WELL/state.json
- Tool call audit log
- ARCHIVIST canon records
- 888_HOLD approval tickets
- F1-F13 floor rules
- Agent telemetry + daily roots for MerkleV3
- WEALTH transaction ledger and portfolio snapshots

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE"
```

---

## Troubleshooting

**`supabase db push` fails:**
- Check project-ref is correct
- Check you're logged in: `supabase status`
- Run with `--dry-run` first for full error details

**Auth errors in Python client:**
- Verify `SUPABASE_SERVICE_ROLE_KEY` (not anon key)
- Verify `SUPABASE_URL` is correct (ends in `.supabase.co`)

**Tables not appearing:**
- Wait 30 seconds after migration — dashboard can lag
- Run SQL query above to check programmatically

**Trigger error on insert:**
- `enforce_vault_seal_immutability` trigger blocks UPDATE/DELETE
- This is intentional. Inserts work normally.

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

```
Epoch: 2026-04-17T18:00+08
Verdict: SUPABASE_DEPLOYMENT_GUIDE_SEALED
QDF: READY_FOR_F13_ACCOUNT_DECISION
```