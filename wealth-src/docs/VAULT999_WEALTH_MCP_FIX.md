# WEALTH MCP — VAULT999 Fix Deployment Guide

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## Problem

WEALTH MCP server fails with `VOID: No module named 'arifosmcp'` because:
1. `psycopg` is not installed in the container
2. `DATABASE_URL` env var not pointing to the correct host

## Two Fixes Applied

### Fix 1: Supabase REST API (Primary — no psycopg needed)

**New file:** `WEALTH/host/governance/vault_supabase.py`

Uses `httpx` to call Supabase REST API directly:
```
POST https://utbmmjmbolmuahwixjqc.supabase.co/rest/v1/wealth_transactions
Authorization: Bearer <anon_key>
```

**Fallback chain in `vault.py`:**
1. Try native psycopg (if `DATABASE_URL` is set and reachable)
2. Fall back to Supabase REST API via `vault_supabase.py`
3. Fall back to no-op with JSONL dump

---

## Fix 2: Container Environment (if using psycopg path)

If you still want the direct psycopg path:

```bash
# In WEALTH MCP container
pip install psycopg[binary]
pip install httpx  # already needed for vault_supabase

# Ensure DATABASE_URL points to Supabase connection string
# Format: postgresql://postgres:<password>@db.<project_ref>.supabase.co:5432/postgres
```

**Get Supabase connection string:**
1. Supabase Dashboard → Project Settings → Connection String
2. Use `URI` format (not `pooler`)

---

## Files Changed

| File | Change |
|------|--------|
| `WEALTH/host/governance/vault_supabase.py` | **NEW** — Supabase REST API vault writer |
| `WEALTH/host/governance/vault.py` | Added Supabase fallback import |
| `WEALTH/server.py` | Added vault_supabase fallback in import chain |

---

## Verify VAULT999 Connection

```bash
# Test via Supabase MCP (already configured)
supabase_execute_sql "SELECT 'VAULT999 test' as status, now() as epoch"
```

Expected: `{"status": "VAULT999 test", "epoch": "2026-04-17..."}`

---

## WEALTH MCP Container Restart

After deploying the new files:

```bash
# Option A: If using Docker
docker restart wealth-mcp

# Option B: If using systemd
sudo systemctl restart wealth-mcp

# Option C: If using PM2
pm2 restart wealth-mcp
```

---

## Column Mismatch Warning

The original `vault.py` was written for `wealth.transactions` (schema.table) but the actual Supabase table is `public.wealth_transactions`.

**New `vault_supabase.py` writes to:**
- `public.wealth_transactions` — transactions
- `public.arifosmcp_portfolio_snapshots` — portfolio snapshots

**Columns in `wealth_transactions`:**
| Column | Type |
|--------|------|
| id | bigint (auto) |
| tx_type | text |
| asset | text |
| amount | numeric |
| currency | text (default MYR) |
| metadata | jsonb |
| epoch | timestamptz |

---

## Architecture After Fix

```
WEALTH MCP Container
├── vault_supabase.py  (httpx → Supabase REST API)  ← PRIMARY
│   └── Writes to: wealth_transactions, portfolio_snapshots
└── vault.py           (psycopg → direct Postgres)  ← FALLBACK
    └── If DATABASE_URL is set and reachable
```

Both paths converge on the same Supabase PostgreSQL instance. No data divergence.

---

**SEAL: `SEAL20260417VAULTWIRE`**
