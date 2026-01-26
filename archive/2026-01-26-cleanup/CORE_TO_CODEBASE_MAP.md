# CORE MIGRATION MAP (v51 -> v52.5.1)

This document maps the legacy `arifos/core` (v51) components to the hardened `codebase` (v52.5.1) structure.

## 1. Trinity Engines

| Legacy (`arifos/core`) | Hardened (`codebase`) | Notes |
|------------------------|-----------------------|-------|
| `engines/agi` | `agi_room/` | AGI Logic (111-333) |
| `engines/asi` | `asi_room/` | ASI Logic (555-666) |
| `engines/apex` | `apex/` | APEX Logic (777-999) |

## 2. Metabolism / Pipeline

| Legacy (`arifos/core`) | Hardened (`codebase`) | Notes |
|------------------------|-----------------------|-------|
| `metabolism/000_void` | `init/000_init/` | Initialization |
| `metabolism/111_sense` | `agi_room/stage_111_sense.py` | |
| `metabolism/222_reflect`| `agi_room/stage_222_think.py` | Renamed 'Reflect' -> 'Think' |
| `metabolism/333_reason` | `agi_room/stage_333_reason.py` | |
| `metabolism/444_evidence`| `stages/stage_444.py` | Collapse point |
| `metabolism/555_empathize`| `stages/stage_555.py` | |
| `metabolism/666_align` | `stages/stage_666.py` | |
| `metabolism/777_forge` | `stages/stage_777_forge.py` | |
| `metabolism/888_judge` | `stages/stage_888_judge.py` | |
| `metabolism/889_proof` | `stages/stage_889_proof.py` | |
| `metabolism/999_seal` | `apex/kernel.py` & `vault/` | Seal logic integrated in Kernel/Vault |

## 3. System & Governance

| Legacy (`arifos/core`) | Hardened (`codebase`) | Notes |
|------------------------|-----------------------|-------|
| `system/pipeline.py` | `micro_loop/micro_loop_core.py` | Linear pipeline -> Metabolic Loop |
| `enforcement/` | `codebase/enforcement.py` & `floors.py` | Constitutional checks |
| `governance/` | `apex/governance/` | Ledger & Voting |
| `guards/` | `mcp/rate_limiter.py` etc. | Guards distributed |

## 4. MCP

| Legacy (`arifos/core`) | Hardened (`codebase`) | Notes |
|------------------------|-----------------------|-------|
| `integration/servers/` | `mcp/servers/` | |
| `integration/api/` | `mcp/` | |

## 5. Memory & Vault

| Legacy (`arifos/core`) | Hardened (`codebase`) | Notes |
|------------------------|-----------------------|-------|
| `memory/` | `vault/` | |
| `vault/` | `vault/` | |

## Action Plan

1. **Verify**: Ensure `codebase` is functional (imports work).
2. **Archive**: Move `arifos/core` to `archive/v51_core`.
3. **Switch**: Ensure root `main.py` or entry points point to `codebase`.

**Status**: `codebase` appears to be a fully refactored, cleaner implementation. Migration should focus on archiving the old core to prevent import confusion.
