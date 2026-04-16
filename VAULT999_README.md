# VAULT999 — Canonical Store

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## Source of Truth

**PostgreSQL on `arifos_core_network`** is the canonical vault.

```
postgresql://arifos_admin:ArifPostgresVault2026!@postgres:5432/arifos_vault
```

| Environment | Host | Note |
|-------------|------|------|
| VPS (local) | `postgres:5432` | Container on `arifos_core_network` |
| Railway (external) | `postgres.railway.internal:5432` | **DEPRECATED** — not used by this VPS |

---

## Schema Layout

```
arifos_vault
├── arifos (10 tables)  — Agent registry, sessions, telemetry, floor rules
├── geox   (5 tables)   — Wells, seismic, petrophysics, interpretations
└── wealth  (5 tables)   — Assets, transactions, portfolio, FX, watchlist
```

---

## Key Tables

| Table | Purpose |
|-------|---------|
| `arifos.agents` | Registered agents (9 currently active) |
| `arifos.sessions` | Per-agent constitutional session records |
| `arifos.tool_calls` | Every tool execution attributed to a session |
| `arifos.agent_telemetry` | SEAL/HOLD/VOID verdicts per agent |
| `arifos.floor_rules` | F1–F13 constitution loaded at startup |
| `arifos.daily_roots` | Merkle v3 chain anchors (source of truth) |

---

## Merkle Chain

The canonical Merkle chain lives in `arifos.daily_roots`. The filesystem mirrors under `*/VAULT999/` are secondary exports and may be stale.

To verify the live chain:
```bash
docker exec postgres psql -U arifos_admin -d arifos_vault \
  -c "SELECT root_date, merkle_root, row_count, anchored FROM arifos.daily_roots ORDER BY created_at DESC"
```

---

## No Railway Confusion

- `postgres.railway.internal` = Railway-managed PostgreSQL (external, NOT this VPS)
- `postgres:5432` = Local container on `arifos_core_network` (THIS VPS canonical vault)
- All services on this VPS use `postgresql://arifos_admin:ArifPostgresVault2026!@postgres:5432/arifos_vault`
- DO NOT reference Railway connection strings on this VPS

---

## Agent IDs on This VPS

```
ARIF-Perplexity   APEX   perplexity-sonnet-4.6
GEOX-Agent       AGI    arifos-unified
WEALTH-Agent     AGI    arifos-unified
AUDITOR-Agent    APEX   af-forge
VALIDATOR-Agent  ASI    af-forge
ENGINEER-Agent   AGI    af-forge
AAA-Agent        ASI    arifos-unified
ARCHIVIST-Agent  AGI    arifos-unified
NOTIFIER-Agent   TOOL   arifos-unified
```

---

SEAL: `SEAL20260413RESOURCECONSOLIDATION`