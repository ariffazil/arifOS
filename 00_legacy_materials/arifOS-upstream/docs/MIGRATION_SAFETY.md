# Migration Safety Guide

**Classification:** Operations | **Authority:** arifOS Engineering
**Version:** 1.0.0 | **Epoch:** 2026-04-19

---

## Purpose

arifOS has a history of versioned snapshots (`arifos-YYYY.MM.DD/`) coexisting with the live `arifOS/` module. This creates **stale-canon risk** — agents loading from wrong directory get wrong governance rules.

This document maps frozen-archive vs. live-canonical and enforces a pre-commit safety hook.

---

## Canonical File Classification

### 🔴 LIVE — Source of Truth (SoT)

Files in this category are **always authoritative**. Agents MUST load from these.

| Path | Purpose | Version Source |
|------|---------|----------------|
| `arifOS/000/` | F0-F13 Constitution | Git-tracked |
| `arifOS/AGENTS.md` | Agent governance contract | Git-tracked |
| `arifOS/SEALING_CHECKLIST.md` | Release quality gates | Git-tracked |
| `arifOS/SESSION_SEAL*.md` | Epoch session seals | Git-tracked |
| `arifOS/arifosmcp/runtime/` | Live MCP runtime | Docker image |
| `arifOS/arifosmcp/contracts/` | Pydantic contract models | Git-tracked |
| `arifOS/core/` | Constitutional kernel | Git-tracked |

### 🟡 FROZEN — Archived Snapshots

Files in `archive/`, `deprecated/`, and date-versioned directories are **never authoritative**. They exist for historical reference only.

| Path | Status | Rationale |
|------|--------|-----------|
| `archive/arifos-YYYY.MM.DD/` | FROZEN | Old snapshots, may not build |
| `deprecated/` | FROZEN | Known broken, retained for comparison |
| `AAA/` | FROZEN | Pre-consolidation mirror, obsolete |
| `APEX/archive/` | FROZEN | Historical architectural state |

**RULE: No agent may load governance from a FROZEN path.**

---

## Versioned Snapshot Risk

The following date-versioned directories have been identified as stale canon risks:

```
arifos-2026.04.16/  ← STALE — was live in April 2026, now superseded
arifos-2026.04.12/  ← STALE
arifos-2026.04.09/  ← STALE
```

**Action required:** These should be moved to `archive/arifos-YYYY.MM.DD/` with a `CANONICAL_VERSION: YYYY.MM.DD` marker.

---

## Migration Safety Checklist

Before any agent or MCP client loads from arifOS:

- [ ] Verify the loaded `arifOS/AGENTS.md` matches git HEAD SHA
- [ ] Verify the loaded constitution has `F0_SOVEREIGN_FLOOR.md` at root of constitution
- [ ] Confirm no stale date-versioned directories are in `sys.path` or Python import path
- [ ] For MCP clients: verify `source_commit` in `/health` endpoint matches expected SHA
- [ ] For SDK adapters: verify `AdapterBus` is loading from `arifosmcp/contracts/` not archived copies

---

## Pre-Commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# pre-commit: prevent FROZEN files from being staged as live

FROZEN_PATTERNS=(
  "arifos-20[0-9][0-9].[0-9][0-9].[0-9][0-9]/"
  "archive/arifos-"
  "deprecated/"
  "AAA/"
)

for pattern in "${FROZEN_PATTERNS[@]}"; do
  if git diff --cached --name-only | grep -q "$pattern"; then
    echo "ERROR: Attempting to commit frozen archive file: $pattern"
    echo "Frozen files (archive/, deprecated/, arifos-YYYY.MM.DD/) are never authoritative."
    echo "Commit rejected. Move to archive/arifos-YYYY.MM.DD/ if intentional."
    exit 1
  fi
done
```

---

## Rollback Procedure

If stale canon is loaded in production:

1. **Detect**: Check `source_commit` in `/health` — compare to expected git SHA
2. **Isolate**: Kill affected MCP session, preserve trace_id
3. **Reload**: Restart container from current image tag
4. **Audit**: Query VAULT999 for any seal issued during stale period
5. **Report**: File `FLOOR_VIOLATION` event with trace_id and expected SHA

---

**Seal:** VAULT999 | **DITEMPA BUKAN DIBERI**
