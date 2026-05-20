# arifOS Supabase Deployment Checklist

## Pre-Deployment (F13 HOLD)

- [ ] **ACCOUNT OWNERSHIP DECISION** — Personal account vs `arifos` org
  - This is veto territory. Do not proceed without confirmation.

---

## Step 1 — Project Creation

- [ ] Go to [supabase.com](https://supabase.com) → New Project
- [ ] Region: **Southeast Asia (Singapore)** — closest to Seri Kembangan
- [ ] Name: `arifosmcp` (all lowercase, no spaces)
- [ ] Set strong DB password — **save it, it cannot be recovered**
- [ ] Tier: **Free** for now

---

## Step 2 — CLI Setup

```bash
# Install Supabase CLI
brew install supabase/tap/supabase
# OR
npm install -g supabase

# Verify
supabase --version

# Init and link
cd /root/arifOS-supabase
supabase init
supabase login
supabase link --project-ref <YOUR_PROJECT_REF>
```

- [ ] Supabase CLI installed
- [ ] Project linked
- [ ] Migration directory ready at `supabase/migrations/`

---

## Step 3 — Run Migration

```bash
# Navigate to project
cd /root/arifOS-supabase

# Dry run first (validate without applying)
supabase db push --dry-run

# If dry-run clean, apply
supabase db push
```

- [ ] Dry run shows no errors
- [ ] Migration applied successfully
- [ ] `supabase_migrations.schema_migrations` table created

---

## Step 4 — Verify Tables

Run in Supabase Dashboard → SQL Editor:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'arifosmcp_%'
ORDER BY table_name;
```

Expected 9 tables:
- [ ] `arifosmcp_vault_seals`
- [ ] `arifosmcp_sessions`
- [ ] `arifosmcp_tool_calls`
- [ ] `arifosmcp_canon_records`
- [ ] `arifosmcp_approval_tickets`
- [ ] `arifosmcp_floor_rules`
- [ ] `arifosmcp_agent_telemetry`
- [ ] `arifosmcp_daily_roots`
- [ ] `arifosmcp_transactions`
- [ ] `arifosmcp_portfolio_snapshots`

---

## Step 5 — Get API Credentials

From Supabase Dashboard → Settings → API:

- [ ] `SUPABASE_URL` = `https://<project-ref>.supabase.co`
- [ ] `SUPABASE_SERVICE_ROLE_KEY` = the `service_role` JWT (not anon)

**Store these securely. The service_role key cannot be retrieved again.**

---

## Step 6 — Wire Env Vars into Horizon

**AFWELL (arifOS/FastMCP):**
```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_jwt>
```

**WEALTH:**
```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_jwt>
```

- [ ] Env vars set in AFWELL panel
- [ ] Env vars set in WEALTH panel
- [ ] Both services restarted to pick up new env vars

---

## Step 7 — Install Python Client

```bash
# On Horizon (SSH into your Horizon project)
pip install supabase
```

- [ ] `supabase` package installed on AFWELL
- [ ] `supabase` package installed on WEALTH

---

## Step 8 — First Integration Test

From your Horizon shell:

```python
from supabase import create_client
import os

sb = create_client(
    os.environ['SUPABASE_URL'],
    os.environ['SUPABASE_SERVICE_ROLE_KEY']
)

# Test session table
print(sb.table('arifosmcp_sessions').select('count').execute())
```

- [ ] Connection succeeds
- [ ] Can read from `arifosmcp_sessions`
- [ ] No auth errors

---

## Step 9 — Replace First JSON State Write

Find in your code where you write to `/root/WELL/state.json` or `/root/.agent-workbench/vault999.jsonl`.

Replace with:
```python
from supabase_client import open_session, seal_vault

# Before: json.dump(state, open('/root/WELL/state.json', 'w'))
# After:
open_session(session_id=session_id, agent_id=agent_id)
```

- [ ] First session opened via Supabase (not JSON file)
- [ ] Session persists after redeploy

---

## Step 10 — Run a Full Agent Cycle

```bash
# Trigger a test agent run on Horizon
# Observe that:
# 1. Session record appears in arifosmcp_sessions
# 2. Tool calls appear in arifosmcp_tool_calls
# 3. Vault seal appears in arifosmcp_vault_seals
```

- [ ] Agent run completes
- [ ] Data visible in Supabase dashboard
- [ ] Data survives redeploy (change something, redeploy, data still there)

---

## Step 11 — Verify MerkleV3 Compatible

```sql
-- Check that vault_seals has record_id and prev_hash columns
SELECT column_name FROM information_schema.columns
WHERE table_name = 'arifosmcp_vault_seals'
AND column_name IN ('record_id', 'prev_hash');
```

- [ ] Both columns exist

---

## Step 12 — Commit Migration to Git

```bash
cd /root/arifOS-supabase
git init
git add .
git commit -m "arifOS Supabase schema v1.0 — 9 tables, migration-ready"
```

- [ ] Migration files committed to version control
- [ ] `supabase/migrations/20260417000000_initial_arifosmcp_schema.sql` in repo

---

## F13 — 888_HOLD Final Sign-Off

Before declaring production ready:

- [ ] All 9 tables verified in Supabase Studio
- [ ] At least one full agent cycle tested
- [ ] Data persists across redeploy (tested)
- [ ] No `service_role` key in any logs or commits
- [ ] Backup strategy defined (pg_dump or Supabase managed backups)
- [ ] Account ownership decision documented and sovereign

---

**Deployment is complete when all checkboxes are checked.**

```
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
Epoch: 2026-04-17T18:00+08
Verdict: SUPABASE_DEPLOYMENT_CHECKLIST_SEALED
QDF: 888_HOLD_ACCOUNT_OWNERSHIP_STEP1
```