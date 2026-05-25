# UNTRACKED_CLASSIFICATION.md
**Mission:** Classify all untracked arifOS migration items.
**Date:** 2026-05-25
**Rule:** No delete. No rebuild. No chmod. Classification only.

---

## Summary Table

| Item | Classification | Risk | Decision Needed |
|------|---------------|------|-----------------|
| `arifos_mcp/` | **CANONICAL** (migration target) | LOW | None — confirmed target |
| `arifosmcp/` | **LEGACY SOURCE** (mine, then freeze) | MEDIUM | Confirm no direct copy back |
| `arifOS_LEGACY/` | **ARCHIVE** (frozen reference) | LOW | None — already frozen |
| `arifOS_QUARANTINED_20260524/` | **QUARANTINE** (pending 888 HOLD) | MEDIUM | Operator must ratify |
| `arifosmcp/ARIFOS_MCP_AGENT_SEED.json` | **EXTRACT** (config insight only) | LOW | Extract valid config to new contracts |
| `arifosmcp/ARIFOS_MCP_FINAL_SEAL.md` | **HISTORICAL RECEIPT** (not authority) | LOW | Archive, do not cite as current truth |
| `arifosmcp/sessions/INFRA_NOTICE.md` | **EXTRACT** (docs if still valid) | LOW | Review and migrate if still true |

---

## Detailed Classification

### 1. `arifos_mcp/` — **CANONICAL** ✓

**Status:** Active PHOENIX-99 migration target. This is where all new implementation lives.

**Contents:**
- `arifos_mcp/` (nested — the actual package)
- `manifests/`, `docs/`, `static/`, `tests/`
- Migration execution plan docs

**Canonical source of truth for:**
- MCP server implementation
- Tool schemas
- Governance contracts

**Rule:** Nothing from `arifosmcp/` copies here unless it passes manifest + schema + test + drift criteria.

---

### 2. `arifosmcp/` — **LEGACY SOURCE** ⚠

**Status:** Full old monolithic arifOS MCP implementation. **Do not treat as canonical.**

**Contents (46 subdirs):**
```
abi/ agents/ agentzero/ apps/ archive/ arifos/ audit/ commands/
config/ contracts/ core/ data/ docs/ evals/ evidence/ infrastructure/
integrations/ intelligence/ memory/ metadata/ migrations/ models/
packages/ prompts/ protocols/ providers/ resources/ runtime/
schema/ schemas/ sessions/ sites/ specs/ static/ telemetry/
tests/ tools/ transforms/ transport/ widgets/
```

**Also contains:**
- `ARIFOS_MCP_AGENT_SEED.json` — config artifact
- `ARIFOS_MCP_FINAL_SEAL.md` — historical receipt
- `sessions/INFRA_NOTICE.md` — infrastructure notice
- `VAULT999/` — local vault artifacts
- `.env` — live secrets (⚠ DO NOT import)

**Classification rule:**
- Mine for historical context
- Extract valid config values only
- Do not copy implementation code directly
- Treat as read-only reference

---

### 3. `arifOS_LEGACY/` — **ARCHIVE** ✓

**Status:** Already frozen per its own README. Reference only.

**Contents:**
- `README.md` — self-documenting as FROZEN
- No active implementation

**Rule:** Leave as-is. No edits. No imports.

---

### 4. `arifOS_QUARANTINED_20260524/` — **QUARANTINE** ⏳

**Status:** Incomplete operator action, pending 888 HOLD ratification.

**Contents:**
- `README.QUARANTINE.md` — self-documenting quarantine status
- `arifosmcp/runtime/` — moved-aside tree fragment

**Rule:** Read-only. Do not edit, promote, or delete without explicit 888 HOLD.

**Required action:** Arif must ratify either:
- **Finalize:** retire contents permanently, OR
- **Unwind:** restore contents to original location

---

### 5. `ARIFOS_MCP_AGENT_SEED.json` (inside `arifosmcp/`) — **EXTRACT**

**Status:** Historical config artifact.

**Action:** Review contents. If valid current config (endpoints, model keys, floor assignments), extract into canonical contracts under `arifos_mcp/manifests/`. If stale or superseded, archive as historical.

---

### 6. `ARIFOS_MCP_FINAL_SEAL.md` (inside `arifosmcp/`) — **HISTORICAL RECEIPT**

**Status:** Past verdict receipt. **Not current authority.**

**Action:** Archive. Do not cite as governing document for current implementation.

---

### 7. `sessions/INFRA_NOTICE.md` (inside `arifosmcp/`) — **EXTRACT**

**Status:** May contain still-valid infrastructure notices.

**Action:** Review. If content is still true (routing, ports, service names), migrate to `arifos_mcp/docs/`. If obsolete, archive.

---

## Items NOT Classified (need Arif decision)

| Item | Reason |
|------|--------|
| `arifosmcp/.env` | Contains live secrets — must NOT be imported; confirm purge/rotate |
| `arifosmcp/VAULT999/` | Append-only ledger artifacts — needs vault-ops review |
| `arifOS_QUARANTINED_20260524/arifosmcp/runtime/` | Quarantine fragment — needs 888 HOLD |

---

## Migration Invariant (BOAS)

```
arifos_mcp/  = canonical PHOENIX-99 target  ← active development
arifosmcp/   = legacy mine/quarantine         ← extract only, then freeze
arifOS_LEGACY/ = frozen archive               ← reference only
arifOS_QUARANTINED_20260524/ = pending        ← 888 HOLD required
```

*Ditempa Bukan Diberi — Intelligence is forged, not given.*
