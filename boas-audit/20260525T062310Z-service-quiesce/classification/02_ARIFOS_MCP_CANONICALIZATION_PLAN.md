# ARIFOS_MCP_CANONICALIZATION_PLAN.md
**Mission:** Define how `arifosmcp/` migrates to `arifos_mcp/`.
**Date:** 2026-05-25
**Rule:** Extract insight only. No direct copy unless criteria are met.

---

## Current State

```
/root/arifOS/arifos_mcp/     ← PHOENIX-99 canonical target (ACTIVE)
/root/arifOS/arifosmcp/      ← Legacy monolithic source (READ-ONLY)
```

### arifos_mcp/ canonical structure:
```
arifos_mcp/
├── arifos_mcp/              ← actual Python package
│   ├── __init__.py
│   ├── __main__.py
│   ├── adapters/
│   ├── discovery/
│   ├── governance/
│   ├── manifests/
│   ├── prompts/
│   ├── resources/
│   ├── schemas/
│   ├── server/
│   ├── tools/
│   └── transports/
├── docs/
├── manifests/
├── static/
├── tests/
├── MCP_A2A_MAP.md
├── TOOL_NAMESPACING.md
└── [migration docs]
```

### arifosmcp/ legacy structure (46 subdirs):
```
arifosmcp/
├── __init__.py, __main__.py, server.py, pyproject.toml, Dockerfile
├── abi/ agents/ agentzero/ apps/ archive/ arifos/ audit/ commands/
├── config/ contracts/ core/ data/ docs/ evals/ evidence/
├── infrastructure/ integrations/ intelligence/ memory/ metadata/
├── migrations/ models/ packages/ prompts/ protocols/ providers/
├── resources/ runtime/ schema/ schemas/ sessions/ sites/ specs/
├── static/ telemetry/ tests/ tools/ transforms/ transport/ widgets/
└── ARIFOS_MCP_AGENT_SEED.json, ARIFOS_MCP_FINAL_SEAL.md, VAULT999/
```

---

## Canonicalization Criteria

**Before any code from `arifosmcp/` becomes canonical in `arifos_mcp/`, it must pass ALL of:**

| # | Criterion | Owner |
|---|-----------|-------|
| 1 | Manifest authority — must be registered in `manifests/` | arifos_mcp/manifests/ |
| 2 | Stage/floor/risk map — must have F1-F13 classification | governance/ |
| 3 | Strict Pydantic schema — input/output validated | schemas/ |
| 4 | Canonical envelope — must use `arif_*` tool naming | tools/ |
| 5 | Test coverage — must pass existing test suite | tests/ |
| 6 | Drift check — must not regress `build != live` | CI/CD |

---

## What to Extract (Not Copy) from arifosmcp/

### High-Value Extractions (pass criteria):

| Source | Target | Notes |
|--------|--------|-------|
| `arifosmcp/arifos/core/` | `arifos_mcp/arifos_mcp/governance/` | Floor enforcement logic — review and re-implement |
| `arifosmcp/arifos/tools/` | `arifos_mcp/arifos_mcp/tools/` | Tool implementations — validate and migrate one-by-one |
| `arifosmcp/arifos/contracts/` | `arifos_mcp/manifests/` | Contract schemas — validate and register |
| `arifosmcp/arifos/memory/` | `arifos_mcp/arifos_mcp/` | Memory layer — review architecture, don't copy |
| `ARIFOS_MCP_AGENT_SEED.json` | `arifos_mcp/manifests/agent_config.json` | Valid config values only |

### DO NOT Extract (entropy risk):

| Source | Reason |
|--------|--------|
| `arifosmcp/.env` | Live secrets — do not import |
| `arifosmcp/VAULT999/` | Append-only ledger — separate vault-ops decision |
| `arifosmcp/__pycache__/` | Generated — discard |
| `arifosmcp/.ruff_cache/` | Generated — discard |
| `arifosmcp/agentzero/` | ASI deliberative — needs APEX review before any merge |
| `arifosmcp/archive/` | Deprecated — archive only |
| `arifosmcp/sites/` | Public surfaces — separate `arif-sites` repo |

---

## Migration Phases

### Phase 1: Inventory (DONE)
- [x] Map `arifosmcp/` contents
- [x] Map `arifos_mcp/` canonical structure
- [x] Classify each item

### Phase 2: Extraction Gate (PENDING)
- [ ] Define `manifests/` schema for new tools
- [ ] Create F1-F13 governance map for each extracted tool
- [ ] Write Pydantic schemas for all tool inputs/outputs
- [ ] Define canonical envelope naming convention

### Phase 3: Incremental Migration (PENDING)
- [ ] One tool at a time from `arifosmcp/tools/` → `arifos_mcp/tools/`
- [ ] Pass all 6 criteria before promoting
- [ ] Update `manifests/` after each addition
- [ ] Run test suite after each addition

### Phase 4: Freeze & Seal (PENDING)
- [ ] All canonical tools migrated and tested
- [ ] `arifosmcp/` marked FROZEN (read-only archive)
- [ ] Migration seal issued via 888_JUDGE
- [ ] Repo push with migration receipt

---

## Blockers

1. **Container drift** — live != build commit; must resolve before Phase 3
2. **888 HOLD** — needed for `arifOS_QUARANTINED_20260524/` finalization
3. **arifOS_LEGACY/** — already frozen; no action needed
4. **APEX/HERMES review** — ASI deliberative paths need APEX verdict before merge

---

## Key Rule

> **arifosmcp/ is a reference library, not a source of truth.**
> Every tool, schema, and contract must be re-registered in `arifos_mcp/manifests/` before it is canonical.
> The fact that something exists in `arifosmcp/` does not make it valid.

*Ditempa Bukan Diberi — Intelligence is forged, not given.*
