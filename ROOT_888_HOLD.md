# 888_HOLD — Root/Submodule Restructure

**Status:** HOLD
**Owner approval required:** Arif Fazil (F13 SOVEREIGN)
**Date:** 2026-05-26
**Audit source:** External GitHub audit + internal verification

---

## Do Not Restructure or Delete Without Explicit Approval

The following are **structural repository topology decisions** — not documentation cleanups. They may encode historical, deployment, submodule, or federation-path assumptions. Treat as repo surgery.

### Submodule & Case Dual Naming

| Path | Type | Risk |
|------|------|------|
| `GEOX/` | Git submodule (commit 7d662d6) | Canonical GEOX reference |
| `geox/` | Git submodule (commit 44cb5de) | Different commit — may be experimental |
| `CONFIG/` | Git tree | Uppercase config registry |
| `config/` | Git tree | Lowercase config — possible duplicate or override |

**Risk:** Renaming or merging may break submodule references, deploy scripts, CI paths, or federation organ routing.

### Root Working-State Directories

| Path | Contents | Risk |
|------|---------|------|
| `.archive/` | Root-level dot-archive | May encode historical state |
| `archive/` | Staged patchplans, legacy docs | May reference deployment paths |
| `scratch/` | ad-hoc scripts (check_db_schema.py, etc.) | May be referenced by ops |
| `staging/` | Agent inventory, alignment docs | May be federation state |

### Reason

These paths were present in the audit snapshot and may reflect:
- Historical submodule deployment states
- Cross-repo federation path assumptions
- CI/CD or hook references
- Agent inventory or alignment state

**Action required:** Architectural review before any move/rename/delete.

---

## Resolved Issues (This Session)

| Issue | Fix | Commit |
|-------|-----|--------|
| Dockerfile port 8080→8088 | Fixed | `dcaaf8fa` |
| README stage map drift | Fixed | `dcaaf8fa` |
| README badges + quick start | Fixed | `d1e96419` |
| DITEMPA translation | Fixed | `d1e96419` |
| Cryptic F2 language | Removed | `d1e96419` |

---

*Last Updated: 2026-05-26 | DITEMPA BUKAN DIBERI | 888_HOLD*
