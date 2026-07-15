# Tool Sync Report — `smithery.yaml` ↔ `arifosmcp/tool_registry.json`

**Task:** TASK-P0-03 · F4 gate · 1h effort
**Date:** 2026-07-15
**Author:** 333-AGI / Copilot perspective subagent (FI-008 dispatched)
**Scope:** Verify sync between public MCP manifest (`smithery.yaml`) and implementation registry (`arifosmcp/tool_registry.json`).
**Ground truth (per task):** `smithery.yaml` (public MCP manifest). Registry extras (ping, selftest, hermes, etc.) are expected.

---

## 1. Executive Summary

| Metric | `smithery.yaml` | `tool_registry.json` | Δ |
|---|---|---|---|
| Declared canonical/headline count | `kernel_capability_count: 8` | `canonical_count: 8` | ✅ |
| Actually-exposed tool names | **6** | `canonical_order` = 8 names | **−2** |
| `public_tool_count` field | 6 | (n/a) | — |
| Internal-only canonical | (n/a) | 6 (`internal_canonical_order`) | — |
| Diagnostic / federated | (n/a) | 40 (`diagnostic_order`) | — |
| **Total implementation surface** | 6 | 65 (`total_surface`) | expected |

**Verdict:** ❌ **DRIFT DETECTED.**
`smithery.yaml` exposes 6 of 8 canonical tools. Two canonical tools — `arif_forge` (stage **010**) and `arif_seal` (stage **999**) — are missing from the public manifest despite being declared canonical (`tier="canonical"`, `public_exposed=true`) in the implementation registry. Both stages fall inside the canonical range specified by the task (**000–999 + 010**).

`smithery.yaml` also carries an **internal contradiction**: it declares `kernel_capability_count: 8` but its `tools:` list contains only 6 entries. The headline number is the truth; the list is the lie.

A separate, lower-severity issue exists in stage labeling (see §4) — not a "missing tool" drift but a documentation inconsistency.

---

## 2. Tool-by-Tool Comparison (canonical band)

| # | Tool | `smithery.yaml` (public) | `tool_registry.json` canonical_order | Stage | Drift? |
|---|---|---|---|---|---|
| 1 | `arif_init` | ✅ KERNEL 000 | ✅ | 000 | OK |
| 2 | `arif_observe` | ✅ KERNEL 111 | ✅ | 111 | OK |
| 3 | `arif_think` | ✅ KERNEL 333 | ✅ | 333 | OK |
| 4 | `arif_route` | ✅ KERNEL 444 | ✅ | 555 | stage-label drift (see §4) |
| 5 | `arif_memory` | ✅ KERNEL memory | ✅ | 555m | stage-label drift (see §4) |
| 6 | `arif_judge` | ✅ KERNEL 888 | ✅ | 888 | OK |
| 7 | **`arif_forge`** | ❌ **MISSING** | ✅ | **010** | **DRIFT (canonical)** |
| 8 | **`arif_seal`** | ❌ **MISSING** | ✅ | **999** | **DRIFT (canonical)** |

### 2.1 In `smithery.yaml` but not in `registry.canonical_order`
**None.** The 6 public tools are a strict subset of the 8 canonical tools. No false-positive entries in the public manifest.

### 2.2 In `registry.canonical_order` but not in `smithery.yaml` (canonical drift)
| Tool | Stage | Registry says | Why missing from public? |
|---|---|---|---|
| `arif_forge` | 010 | `tier=canonical`, `access=internal_only`, `public_exposed=true`, `action_class=MUTATE`, `risk_tier=HIGH`, `blast_radius=PUBLIC`, `reversibility=0.5` | Implementation says it should be public, but it is **mutating** (`requires_lease=true`, `autonomy_floor=PRINCIPAL_APPROVAL_REQUIRED`). Likely intentionally gated from MCP wire until L11/L13 lease primitive is live on the public surface. |
| `arif_seal` | 999 | `tier=canonical`, `access=authenticated`, `public_exposed=true`, `action_class=IRREVERSIBLE`, `risk_tier=ATOMIC`, `blast_radius=PUBLIC`, `reversibility=0.0` | The VAULT999 SEAL verb. **Irreversible** (`reversibility=0.0`) and requires `ack_irreversible=True`. Likely withheld from public MCP until principal-auth handshake is signed. |

Both belong to the canonical range (000–999 + 010) per task rule §5 → **GitHub issue opened with label `registry-drift`**.

---

## 3. Registry Extras (expected, not drift)

The task expects extras such as ping / selftest. The registry contains **65** total implementation tools across 11 tiers. Categories present but NOT in `smithery.yaml`:

| Tier | Count | Notes |
|---|---|---|
| `internal` | 6 | `arif_act`, `arif_fetch`, `arif_judge_deliberate`, `arif_kernel_intercept`, `arif_measure` (deprecated → `arif_runtime_health`), `arif_triage` |
| `hermes` | 7 | Hermes ASI cross-verification (`hermes_system_status`, `arif_vault_query`, `hermes_epistemic_check`, `hermes_fact_check`, `hermes_cross_verify`, `hermes_plan_review`, `hermes_memory_steward`). Gated behind `ARIFOS_MCP_EXPOSE_DEV_TOOLS=true`. Most marked `deprecated: true` with reason `Not in CANONICAL_TOOLS — Phase 2 registry cleanup 2026-07-11`. |
| `canary` | 7 | Transport/protocol echo (`arif_canary`, `arif_ping`, `arif_schema_echo`, `arif_version_echo`, `arif_transport_echo`, `arif_initialize_probe`, `arif_conformance_report`). All deprecated 2026-07-11. The task explicitly mentions **ping** as expected — confirmed present (deprecated). |
| `lease` | 3 | `arif_lease_inspect`, `arif_lease_issue`, `arif_lease_revoke` — all deprecated. |
| `attest` | 7 | Federation organ attestation (`arif_os_attest`, `arif_organ_attest`, `arif_organ_attest_all`, `arif_heartbeat`, `arif_peer_contract_validate`, `arif_peer_contract_attest`, `arif_peer_contract_forbid`). |
| `forge-sub` | 3 | `forge_dry_run`, `forge_plan`, `forge_query` — A-FORGE sub-tools. Registry header notes these are **deprecated 2026-07-15**: *"removed 2026-07-15"*. |
| `narrative` | 2 | `arif_detect_institutional_shadow_drift`, `arif_detect_narrative_tension`. |
| `diagnostic` | 9 | `arif_stack_health_probe`, `arif_scan_local_instructions`, `arif_organ_consensus`, `arif_session_budget`, `arif_floor_status`, `mcp_drift_check`, `arif_gate_judge`, `arif_self_evaluate`, `arif_model_compare`. Task explicitly mentions **selftest** — `arif_self_evaluate` (deprecated) is present. |
| `discovery` | 1 | `arif_resolve_tool` |
| `chatgpt-shim` | 2 | `arif_fetch`, `arif_search` — kept for backward compat with ChatGPT connector. |

**Documentation surfaces** (declared in `canonical_order` but absent from `canonical_count` arithmetic):
- `internal_canonical_count: 6` ← matches 6 entries ✓
- `diagnostic_count: 40` ← matches 40 entries ✓
- `total_surface: 65` ← matches full `tools` dict count ✓

The registry's `_surface_sync` block declares `public_count: 8`, which **agrees with `smithery.yaml`'s `kernel_capability_count: 8`** but **contradicts `smithery.yaml`'s actual `public_tool_count: 6`**. This is the same internal contradiction as above.

### 3.1 Floor / law accounting
Both files reference the 13-floor system. Both files list all 13 laws (L01–L13). Floor binding coverage is consistent with task scope — not part of this drift check.

---

## 4. Stage-Label Drift (lower severity, not canonical-drift)

The task scope is "missing tool" drift, but two stage-label mismatches are worth noting for housekeeping:

| Tool | `smithery.yaml` description says | `tool_registry.json` stage | Resolution |
|---|---|---|---|
| `arif_route` | "KERNEL 444" | `555` | Registry is authoritative (matches `constitutional_map.py` `CANONICAL_TOOLS` entry). Smithery description is stale. |
| `arif_memory` | "KERNEL memory governor" | `555m` | Both refer to the same tool; smithery omits the stage suffix `555m` (= memory lane). |

These are NOT "missing from either file" — both tools appear in both. They are description-vs-stage inconsistencies. Not blocking. Worth a follow-up commit to `scripts/sync_kernel_abi.py` or the description field.

---

## 5. Recommendations

1. **Decide intent for `arif_forge` and `arif_seal` on the public MCP surface:**
   - **Option A (promote):** Add both to `smithery.yaml`. Requires L11/L13 lease primitive to be live on public wire, and `arif_seal` requires signed principal-auth handshake. Big blast radius (`PUBLIC`, `risk_tier=ATOMIC`).
   - **Option B (withhold intentionally):** Update `arif_forge` and `arif_seal` in `tool_registry.json` to set `public_exposed: false` and add `deprecation_reason` / `expose_until` fields so the registry matches the manifest. This is the **cleanest path forward** — the manifest becomes the single source of truth for the public wire, and the registry accurately reflects what is actually shipped.
2. **Fix `public_tool_count` vs `kernel_capability_count` contradiction** in `smithery.yaml`: either expose the 2 missing tools (Option A) or drop the headline to 6.
3. **Refresh stage labels** in `smithery.yaml` tool descriptions: change `KERNEL 444` → `KERNEL 555` for `arif_route`, and add `555m` for `arif_memory`. Or update `scripts/sync_kernel_abi.py` to source the stage from `constitutional_map.py`.
4. **Re-run `scripts/sync_kernel_abi.py`** after the fix to keep `smithery.yaml` and `tool_registry.json` both derived from the same Python source.

---

## 6. Methodology

| Step | Tool | Source |
|---|---|---|
| 1. Extract `smithery.yaml` tools + stage hints | `yaml.safe_load` + regex `KERNEL\s+(\S+)` | `/root/arifOS/smithery.yaml` |
| 2. Extract `tool_registry.json` canonical_order + per-tool stage | `json.loads` + dict lookup | `/root/arifOS/arifosmcp/tool_registry.json` |
| 3. Diff `smithery set` ↔ `canonical_order set` | Python `set` difference | in-memory |
| 4. Cross-reference source-of-truth | `grep CANONICAL_TOOLS` + Read | `/root/arifOS/arifosmcp/constitutional_map.py:552` and `/root/arifOS/arifosmcp/abi/capability_registry.json` |
| 5. Inventory registry extras | tier-bucketed count | `tool_registry.json` |
| 6. GitHub issue for canonical drift | `gh issue create --label registry-drift` | `ariffazil/arifOS` |

All comparisons made **at 2026-07-15T04:34Z** against the working tree at commit `127223c1a` (HEAD: feat(kernel): forge platform-neutral capability ABI).

---

## 7. Constitutional Floor Compliance

| Floor | Status | Note |
|---|---|---|
| F1 AMANAH | PASS | Reversible audit (report + commit). No mutation of source files. |
| F2 TRUTH | PASS | All stage labels sourced from registry JSON, not invented. Where a number was unmeasured (none in this scope) we did not fabricate. |
| F4 CLARITY | PASS | This report reduces ambiguity — surface is now enumerated. |
| F9 ANTI-HANTU | PASS | No scalars fabricated. Stage labels verified against source JSON. |
| F11 AUDIT | PASS | This file is the audit artifact. Commit hash captured in §6. |
| F13 SOVEREIGN | NOT TRIGGERED | No F13-gated action taken; only file write + report + GitHub issue (no policy mutation, no F13 floor change). |

---

## 8. Receipt

| Field | Value |
|---|---|
| Files read | `/root/arifOS/smithery.yaml`, `/root/arifOS/arifosmcp/tool_registry.json`, `/root/arifOS/arifosmcp/constitutional_map.py` (lines 540–1295), `/root/arifOS/arifosmcp/abi/capability_registry.json` |
| Files created | `/root/arifOS/docs/tool_sync_report.md` |
| Files modified | None outside this report. Working-tree drift in unrelated files (see git status) was left untouched per task scope. |
| Issues opened | See GitHub issue with `registry-drift` label |
| Commit | `[AUDIT] smithery.yaml ↔ tool_registry.json sync check — P0-03` |
| Tests run | None (this task is config/manifest sync, not code). |
| Push | **NOT PERFORMED** (888 HOLD per task workflow). |

*— DITEMPA BUKAN DIBERI.*
