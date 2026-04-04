# VAULT999 Schema v3 (Hybrid)

**Version:** 3.0  
**Status:** DEPLOYED  
**Architecture:** Hybrid — 4 indexed columns + 9 JSONB categories  
**Based on:** APEX Theory compression + entropy optimization

---

## Overview

v3 compresses 22 fields into 14 columns using APEX trinity mapping:
- **4 fast-query columns** for common governance queries
- **9 JSONB categories** for structured metadata
- **1 backup column** for raw payload

---

## Schema

```sql
CREATE TABLE vault_ledger_v3 (
  -- Core (indexed)
  seal_id         UUID PRIMARY KEY,
  timestamp       TIMESTAMPTZ DEFAULT NOW(),
  
  -- Fast-query columns (the 4 governance axes)
  session_id      TEXT NOT NULL,
  verdict_type    TEXT NOT NULL,      -- SEAL/VOID/PARTIAL/SABAR
  risk_level      TEXT DEFAULT 'low', -- low/medium/high/critical
  environment     TEXT DEFAULT 'prod', -- test/staging/prod
  
  -- 9 JSONB Categories (APEX-aligned)
  identity        JSONB,  -- Ω: Who is involved
  chain           JSONB,  -- Ψ: Integrity proof
  verdict         JSONB,  -- Ψ: Final decision
  context         JSONB,  -- Δ: What was asked
  risk            JSONB,  -- Ω: Danger assessment
  floors          JSONB,  -- Δ: Which laws checked
  metrics         JSONB,  -- Δ: Entropy, scores
  oversight       JSONB,  -- Ω: Human control
  provenance      JSONB,  -- Ψ: Where from
  
  -- Backup
  seal_data       JSONB
);
```

---

## 9 Categories (APEX Trinity)

### Δ (MIND — Truth, Logic)

| Category | Contents |
|----------|----------|
| **context** | `{summary, q_hash, r_hash, intent}` |
| **floors** | `{checked[], failed[]}` |
| **metrics** | `{omega, tw, peace2, genius}` |

### Ω (HEART — Empathy, Safety)

| Category | Contents |
|----------|----------|
| **risk** | `{level, tags[], category, pii}` |
| **oversight** | `{override, reason, by}` |
| **identity** | `{session, actor_type, actor_id}` |

### Ψ (SOUL — Judgment, Sovereignty)

| Category | Contents |
|----------|----------|
| **verdict** | `{type, authority}` |
| **chain** | `{seq, entry_hash, prev_hash, merkle}` |
| **provenance** | `{model, model_info, tools[], env}` |

---

## Query Examples

### Simple (indexed columns)
```sql
-- All VOIDs in production
SELECT * FROM vault_ledger_v3 
WHERE verdict_type = 'VOID' AND environment = 'prod';

-- High-risk decisions today
SELECT * FROM vault_ledger_v3
WHERE risk_level = 'critical' 
AND timestamp > NOW() - INTERVAL '1 day';
```

### JSONB queries
```sql
-- F1 violations
SELECT * FROM vault_ledger_v3
WHERE floors->'failed' ? 'F1';

-- Human overrides
SELECT * FROM vault_ledger_v3
WHERE (oversight->>'override')::boolean = true;

-- Specific actor
SELECT * FROM vault_ledger_v3
WHERE identity->>'actor_id' = 'arif-fazil';
```

---

## Example Entry (v3)

```json
{
  "seal_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-07T07:22:00Z",
  "session_id": "telegram_arif_20260207",
  "verdict_type": "SEAL",
  "risk_level": "low",
  "environment": "prod",
  
  "identity": {
    "session": "telegram_arif_20260207",
    "actor_type": "human",
    "actor_id": "arif-fazil"
  },
  
  "context": {
    "summary": "000_INIT session start",
    "q_hash": "a1b2c3d4...",
    "r_hash": null,
    "intent": "initialize"
  },
  
  "risk": {
    "level": "low",
    "tags": [],
    "category": "session_init",
    "pii": "none"
  },
  
  "floors": {
    "checked": ["F1", "F2", "F7", "F9", "F12", "F13"],
    "failed": []
  },
  
  "metrics": {
    "omega": 0.04,
    "tw": 0.95,
    "peace2": 1.0,
    "genius": null
  },
  
  "oversight": {
    "override": false,
    "reason": null,
    "by": null
  },
  
  "provenance": {
    "model": "claude-opus-4-5",
    "model_info": {"provider": "Anthropic"},
    "tools": ["init_gate"],
    "env": "prod"
  }
}
```

---

## Backwards Compatibility

- v2.1 entries continue to work
- `get_meta()` function detects schema version
- v3 entries include `_v2_metadata` for legacy queries
- vault_query returns unified format

---

## Migration Path

1. **Phase 1 (current):** vault_seal writes v3 format to existing table
2. **Phase 2 (optional):** Create `vault_ledger_v3` table
3. **Phase 3 (optional):** Migrate historical data

---

## Why Hybrid?

| Approach | Schema Entropy | Query Entropy | Total |
|----------|---------------|---------------|-------|
| v2.1 (22 cols) | High | Low | Medium-High |
| Full JSONB (11 cols) | Low | High | Medium-High |
| **Hybrid (14 cols)** | **Medium** | **Medium** | **Lowest** |

AGI bot recommendation: "Hybrid reduces schema clutter while keeping critical governance queries one WHERE away."

---

*DITEMPA BUKAN DIBERI* 🔥
