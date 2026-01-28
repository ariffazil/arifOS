# arifOS Migration Analysis: Archiving the `arifos/` Module

**Date:** 2026-01-29  
**Scope:** Full analysis of what needs to be refactored before `arifos/` can be archived  
**Status:** v53.2.5-CODEBASE (Active Development)

---

## Executive Summary

The `arifos/` directory contains the legacy v52 and earlier implementation. The new `codebase/` module (v53+) is the canonical implementation. To fully archive/delete `arifos/`, we need to:

1. **Migrate entry points** from `arifos.mcp.*` to `codebase.mcp.*`
2. **Update scripts** that import from `arifos`
3. **Migrate or archive session data** in `arifos/mcp/sessions/`
4. **Update pyproject.toml** to remove legacy entry points
5. **Migrate spec files** if still needed

---

## 1. Entry Points Analysis (pyproject.toml)

### Currently Using `arifos` (NEED MIGRATION)

| Entry Point | Current Target | Should Target | Priority |
|-------------|----------------|---------------|----------|
| `aaa-mcp` | `arifos.mcp.__main__:main` | `codebase.mcp.server:main` | **CRITICAL** |
| `aaa-mcp-sse` | `arifos.mcp.sse:main` | `codebase.mcp.sse:main` | **CRITICAL** |
| `aaa-mcp-stdio` | `arifos.mcp.server:main_stdio` | `codebase.mcp.server:main_stdio` | **CRITICAL** |
| `arifos-mcp` | `arifos.mcp.__main__:main` | Archive | Low |
| `arifos-mcp-sse` | `arifos.mcp.sse:main` | Archive | Low |
| `arifos-mcp-stdio` | `arifos.mcp.server:main_stdio` | Archive | Low |
| `aaa-mcp-utils` | `arifos.mcp.mcp_utils_server:main` | `codebase.mcp.mcp_utils_server:main` | Medium |
| `arifos-api` | `arifos.api.server:run_server` | `codebase.api.server:run_server` | Medium |
| `000-999` | `arifos.clip.aclip.cli._dispatcher*:main` | Archive or migrate | Low |

### Already Using `codebase` (GOOD)

| Entry Point | Target | Status |
|-------------|--------|--------|
| `codebase-mcp` | `codebase.mcp.server:main` | ✅ Active |
| `codebase-mcp-stdio` | `codebase.mcp.server:main_stdio` | ✅ Active |
| `codebase-mcp-sse` | `codebase.mcp.sse:main` | ✅ Active |

---

## 2. Scripts Requiring Migration

### Scripts with `arifos` Imports (NEED UPDATE)

| Script | Imports From `arifos` | Action | Priority |
|--------|----------------------|--------|----------|
| `commission_aaa_cluster.py` | `arifos.mcp.servers.axis`, `arifos.mcp.servers.arif`, `arifos.mcp.servers.apex` | Migrate imports or archive | Medium |
| `apply_thermodynamic_fix.py` | Unknown | Check and migrate | Low |
| `fix_imports.py` | Unknown | Likely legacy - archive | Low |
| `generate_constitutional_vault.py` | `arifos.constitutional_constants` | Migrate constants | Medium |
| `create_genesis_block.py` | Unknown | Check and migrate | Low |
| `test_mcp_compliance.py` | `arifos.mcp.server` | Migrate to `codebase.mcp.server` | Medium |
| `verify_v52_forge.py` | `arifos` | Archive (v52-specific) | Low |
| `verify_aaa_cluster.py` | `arifos.mcp.servers.*` | Migrate or archive | Medium |

### Scripts to Archive (v52-specific)

| Script | Reason |
|--------|--------|
| `verify_v52_forge.py` | v52-specific verification |
| `fix_imports.py` | Likely legacy import fixer |

---

## 3. Session Data Migration

### `arifos/mcp/sessions/` Directory

**Contents:** ~1000+ JSON session files  
**Status:** May contain active session data  
**Action Required:**

1. Check if sessions are still being written here
2. If yes, migrate session storage path to `codebase/mcp/sessions/`
3. If no, archive to `archive/session_history/`

**Migration Path:**
```python
# OLD path in session_ledger.py
SESSION_PATH = Path(__file__).parent / "sessions"  # arifos/mcp/sessions

# NEW path should be
SESSION_PATH = Path(__file__).parent.parent.parent / "VAULT999" / "sessions"
```

---

## 4. Codebase Files Importing from `arifos`

### Files with `arifos` References (Comments Only - OK)

| File | Reference Type | Action |
|------|---------------|--------|
| `codebase/mcp/session_ledger.py` | Comment only (line 50) | None needed |
| `codebase/engines/asi/asi_components.py` | Comment only (line 47) | None needed |
| `codebase/apex/governance/merkle_ledger.py` | Comment only (line 8) | None needed |

### Files Needing Attention

| File | Issue | Action |
|------|-------|--------|
| `codebase/init/000_init/mcp_bridge.py` | Header comment references extraction from `arifos/mcp/tools/mcp_trinity.py` | Update comment |
| `codebase/mcp/tools/_archive/mcp_trinity.py` | Archived file - may import from arifos | Check and archive |

---

## 5. Critical Data to Migrate

### A. MCP Server Session Ledger

**File:** `arifos/mcp/session_ledger.py`  
**Status:** Has session files in `arifos/mcp/sessions/`  
**Migration:** 
- Check if `codebase/mcp/session_ledger.py` exists and is active
- Migrate session files if needed
- Update session path

### B. Runtime Configuration

**File:** `arifos/core/system/constitutional_runtime_config_v46.py`  
**Status:** May contain active runtime config  
**Migration:** Check if still used by `codebase`

### C. Spec Files

**Directory:** `arifos/spec/`  
**Status:** Contains v46, v47 specs  
**Migration:** 
- `arifos/spec/v46/` - Archive (old)
- `arifos/spec/v47/` - Check if still referenced
- `arifos/spec/v53/` - Keep if exists

---

## 6. Migration Plan

### Phase 1: Critical Entry Points (Immediate)

Update `pyproject.toml` to point `aaa-mcp*` commands to `codebase`:

```toml
[project.scripts]
# AAA MCP Server Commands (Primary v53)
codebase-mcp = "codebase.mcp.server:main"
codebase-mcp-stdio = "codebase.mcp.server:main_stdio"
codebase-mcp-sse = "codebase.mcp.sse:main"
aaa-mcp = "codebase.mcp.server:main"          # CHANGED from arifos
aaa-mcp-sse = "codebase.mcp.sse:main"        # CHANGED from arifos
aaa-mcp-stdio = "codebase.mcp.server:main_stdio"  # CHANGED from arifos

# Remove deprecated arifos-mcp* aliases
# arifos-mcp = "arifos.mcp.__main__:main"     # REMOVE
# arifos-mcp-sse = "arifos.mcp.sse:main"      # REMOVE
# arifos-mcp-stdio = "arifos.mcp.server:main_stdio"  # REMOVE
```

### Phase 2: Session Data (Before Archive)

1. Check if sessions are being written to `arifos/mcp/sessions/`
2. If yes:
   - Copy existing sessions to `codebase/mcp/sessions/`
   - Update `codebase/mcp/session_ledger.py` to use new path
3. If no:
   - Archive `arifos/mcp/sessions/` to `archive/session_history/`

### Phase 3: Scripts (Staged)

1. Update scripts that import from `arifos`:
   - `commission_aaa_cluster.py` → Use `codebase.mcp.servers.*`
   - `test_mcp_compliance.py` → Use `codebase.mcp.server`
   - `generate_constitutional_vault.py` → Use `codebase.constants`

2. Archive v52-specific scripts:
   - `verify_v52_forge.py`
   - `fix_imports.py`

### Phase 4: Spec Files (Staged)

1. Check if `codebase/spec/` exists
2. Migrate active specs from `arifos/spec/v47/`
3. Archive old specs:
   - `arifos/spec/v42/` → Archive
   - `arifos/spec/v45/` → Archive
   - `arifos/spec/v46/` → Archive
   - `arifos/spec/v47/` → Review, archive if not used

### Phase 5: Final Archive (After Verification)

1. Verify Railway deployment uses `codebase-mcp-sse`
2. Verify local development uses `codebase-mcp`
3. Verify no active imports from `arifos`
4. Move `arifos/` to `archive/arifos_v52_backup/`

---

## 7. Verification Checklist

Before archiving `arifos/`, verify:

- [ ] `aaa-mcp` entry point points to `codebase`
- [ ] `aaa-mcp-sse` entry point points to `codebase`
- [ ] Railway deployment uses `codebase-mcp-sse`
- [ ] `codebase/mcp/session_ledger.py` uses correct path
- [ ] Session files migrated (if needed)
- [ ] Scripts updated or archived
- [ ] Spec files migrated or archived
- [ ] No tests import from `arifos`
- [ ] No codebase files import from `arifos`
- [ ] Docker build uses `codebase`

---

## 8. Files Safe to Archive Now

These `arifos/` subdirectories are safe to archive immediately:

| Directory | Reason |
|-----------|--------|
| `arifos/clip/` | CLI tools - replaced by `codebase/mcp/` |
| `arifos/config/` | Configs - moved to root/config |
| `arifos/core/agi/paradox/` | Empty or legacy |
| `arifos/core/apex/paradox/` | Empty or legacy |
| `arifos/core/bridge/` | Empty |
| `arifos/core/hypervisor/` | Duplicates `codebase/guards/` |
| `arifos/ledger/` | Legacy ledger - use `codebase/vault/` |
| `arifos/logs/` | Empty |
| `arifos/protocol/` | Legacy protocol |
| `arifos/runtime/` | Minimal, likely legacy |
| `arifos/spec/archive/` | Already archived specs |
| `arifos/spec/v42/` | Very old specs |
| `arifos/spec/v45/` | Old specs |
| `arifos/spec/v46/` | Old specs |
| `arifos/mcp/_archive/` | Already archived |
| `arifos/mcp/servers/` | May be used - verify |
| `arifos/mcp/sessions/` | Verify if active |
| `arifos/mcp/tools/` | May be used - verify |

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Active sessions in `arifos/mcp/sessions/` | Medium | High | Verify before archive |
| Entry points still using `arifos` | High | Critical | Update pyproject.toml first |
| Scripts breaking due to import changes | Medium | Medium | Test scripts after migration |
| Spec files still referenced | Medium | Medium | Check codebase/spec first |
| Session ledger path issues | Medium | High | Update path before archive |

---

## 10. Recommended Immediate Actions

1. **Update pyproject.toml entry points** (Critical)
2. **Check session activity** in `arifos/mcp/sessions/`
3. **Test Railway deployment** with `codebase-mcp-sse`
4. **Migrate or archive** `arifos/mcp/sessions/`
5. **Update scripts** with arifos imports

---

**Authority:** Constitutional Housekeeping  
**Verdict:** SEAL with migration plan  
**DITEMPA BUKAN DIBERI**
