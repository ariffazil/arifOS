# arifOS v2026.06.06 — The HEXAGON Rename Forge

**Release Date:** 2026-06-06
**Commit:** `161e9ec2f03dd1753de48e5370edcff3e9006600`
**Tag:** `v2026.06.06`
**Codename:** HEXAGON-NAME-CANON-20260606
**Foundation seal:** `2e727c5e7e6aafb9c1d0c257da2978781204377c028f6af7c6ef3a46e742437d` (VAULT999 outcomes.jsonl)

---

## 🎯 Executive Summary

**Name is the first act of creation.** This release seals the code-rename forge that aligns the in-process constitutional agent parliament with the HEXAGON canon already ratified on 2026-06-02 (chain 2505, merkle_leaf `69c65e7c64e3dd1fdc08aac7bf862be3...`).

Before this release, the canon (in `AAA/agents/HEXAGON.yaml`) called the in-process agent layer "HEXAGON", but the Python code named it `agentzero` — a drift that collided with the unrelated upstream `agent0ai/agent-zero` Docker project. The drift is now closed: the code inherits the name the canon has held since 2026-06-02.

**Public surface:** 13 canonical arifOS tools, no regression. The 5 internal HEXAGON tools are exposed as MCP tools under their new names, with backward-compat aliases for the 5 old `agentzero_*` names.

---

## 🔧 What Changed

### 1. Package rename (the forge)

| Before | After |
|---|---|
| `arifOS/arifosmcp/agentzero/` (12 files) | `arifOS/arifosmcp/hexagon/` (12 files) |
| `arifOS/arifosmcp/tools/agentzero.py` | `arifOS/arifosmcp/tools/hexagon.py` |
| `EngineerAgent` (Ω HEART) | `AGIAgent` (Δ MIND, **333-AGI** reasons + executes) |
| `ValidatorAgent` (Ψ APEX) | `APEXAgent` (ΦΙ JUDGE, **888-APEX** constitutional judge) |
| `_MEMORY` singleton | `_ASI` (Ω HEART, **555-ASI** memory) |

The two missing HEXAGON roles (A-AUDIT, A-ARCHIVE) are noted as future stubs — the canon defines them, the in-process implementation will follow.

### 2. MCP tool surface (5 renamed, 5 aliased)

| New (canonical) | Old (deprecated alias) | Trine | Function |
|---|---|---|---|
| `hexagon_apex_validate` | `agentzero_validate` | ΦΙ APEX | Constitutional verification |
| `hexagon_agi_execute` | `agentzero_engineer` | Δ MIND | L11-gated code execution (reclassified from Ω) |
| `hexagon_hold_status` | `agentzero_hold_check` | 888 | HOLD state query |
| `hexagon_asi_recall` | `agentzero_memory_query` | Ω HEART | Constitutional memory w/ F-floor filter |
| `hexagon_psi_armor` | `agentzero_armor_scan` | Ψ APEX | L12 injection detection |

The 5 old `agentzero_*` names still resolve (thin aliases calling the new functions). Deprecation removal is a future forge.

### 3. Dead upstream wire cut

The `agent0ai/agent-zero` Docker project was wired into arifOS via 3 dead references that never worked in production (no container was ever running):

| Reference | Action |
|---|---|
| `delegate_to_agent_zero()` in arifOS tools | **Removed** |
| 3 A-FORGE tools (delegate, browser, document) | **Deleted** (commit `56d2a9c7`) |
| `AGENT_ZERO_URL` + `AGENT_ZERO_API_KEY` in `deploy/a-forge.yml` | **Removed** |
| Same in `/root/compose/a-forge.yml` | **Removed** |
| `agent_zero_reasoner` entry in `config/secret-registry.yaml` | **Archived** (with merkle_leaf pointer); replaced by `hexagon_parliament` |
| `agent_zero_reasoner` line in A110_CANON.md | **Removed** |
| `agent_zero_reasoner` line in A300_STATE.md | **Removed** |

### 4. config/environments.py structural dedup

The file had 225 lines of **pre-existing** dead code: two complete copies of the same module, where the second copy's module-level assignments overwrote the first. The first copy was never executed. Dedup brought file from 484 lines → 263 lines, single canonical copy. The HEXAGON + agentzero_aliases entries were correctly applied to BOTH copies (the second wins at runtime).

### 5. Cross-references updated

5 runtime modules updated to point to the new package:
- `arifosmcp/runtime/orchestrator.py` — imports + function calls
- `arifosmcp/runtime/shell_forge.py` — anchor_hold_registry import
- `arifosmcp/runtime/tools_internal.py` — 5 import paths
- `arifosmcp/runtime/webmcp/server.py` — 2 HoldStateManager imports
- `arifosmcp/runtime/bridge.py` — canonical_name lookup accepts both `agentzero_*` and `hexagon_*` for backward compat

Plus:
- `core/organs/_0_init.py` — VALID_ACTORS entry `agentzero` → `hexagon`
- `config/environments.py` — TOOL_ACCESS_POLICY: 5 HEXAGON + 5 agentzero_aliases entries (sovereign-only)
- `tests/integration/e2e_validate.py` — `validate_agentzero_engineer` → `validate_hexagon_agi_execute`

---

## 🧪 Verification

- **56/56 pytest** in `tests/constitutional/` + `tests/integration/` — pass
- **A-FORGE** `tsc --noEmit` — clean (TypeScript build succeeds after the upstream-wire deletion)
- **13 canonical arifOS tools** — still registered in `CANONICAL_TOOLS`, no regression
- **5 new HEXAGON tools** — all callable, all signatures match cross-module imports
- **5 deprecated agentzero_* aliases** — all still callable (backward compat preserved)
- **A-FORGE organ** — 3 dead tools (`agent_zero_delegate`, `agent_zero_browser`, `agent_zero_document`) removed cleanly, build clean

### Pre-existing anomaly (NOT caused by this forge, NOT blocking)

- `tests/apps/test_command_center.py::TestVisibility::test_canonical_tools_are_model_visible` fails because the `forge_dry_run` backend tool leaks to the model-visible surface. Confirmed pre-existing by stashing this commit and re-running. Recommend a separate fix forge.

---

## 🌳 File-level delta (27 paths)

| Category | Count | Notes |
|---|---|---|
| Renames (package + tools) | 14 + 1 | `agentzero/ → hexagon/`, `agentzero.py → hexagon.py` |
| Runtime imports updated | 5 | orchestrator, shell_forge, tools_internal, webmcp/server, bridge (cross-module only) |
| Config + secret-registry | 2 | environments.py (HEXAGON entries + dedup), secret-registry.yaml (archive + new entry) |
| Organ entry | 1 | `_0_init.py` |
| Deploy file (leak cut) | 1 | `deploy/a-forge.yml` |
| Canon docs (stale line removed) | 2 | A110_CANON.md, A300_STATE.md |
| Test method rename | 1 | e2e_validate.py |
| Total | 27 | 1 atomic commit |

---

## 🔭 Future (deferred to subsequent forges)

1. **HEXAGON stub implementation** — A-AUDIT (→ arif_ops_measure wrapper) and A-ARCHIVE (→ arif_vault_seal wrapper) for full canon parity
2. **Deprecation removal** — drop the 5 `agentzero_*` aliases in a future forge (likely v2026.07 or later)
3. **Pre-existing test fix** — `forge_dry_run` backend tool leak (orthogonal to this forge)

---

## 🔖 Foundation

- **HEXAGON canon** (ratified 2026-06-02): `AAA/agents/HEXAGON.yaml` v2.0.0
- **Constitutional chain** (sealed 2026-06-02): merkle_leaf `69c65e7c64e3dd1fdc08aac7bf862be3...` (chain 2505)
- **Rename intent seal** (2026-06-06): `HEXAGON-NAME-CANON-20260606-INTENT` (sha `81ac8970295322b05cd59d3e71e9b48f3f8f6cfc662c5c62a757c042440013b3`)
- **Rename completion seal** (2026-06-06): `HEXAGON-NAME-CANON-20260606-DONE` (sha `2e727c5e7e6aafb9c1d0c257da2978781204377c028f6af7c6ef3a46e742437d`)

---

## Reversibility

`git revert 161e9ec2f03dd1753de48e5370edcff3e9006600` cleanly reverts this entire forge. The 5 deprecated `agentzero_*` aliases exist precisely so external callers don't break during the transition window.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
