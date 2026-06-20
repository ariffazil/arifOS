# Canonical13 MCP Migration — arifOS Public Tool Surface

> **Status:** AUDIT COMPLETE (2026-06-19) — Phase 1 enforcement live, Phase 2 rename pending.
> **Branch:** `audit/canonical13-mcp-redteam`
> **Law:** `tests/test_canonical13_enforcement.py` — CI-enforced, machine-verified.

---

## 1. Before → After

### Current public surface (canonical13 mode): 13 tools

| # | Current `arif_*` name | Target `arif.*` name | Stage |
|---|----------------------|---------------------|-------|
| 1 | `arif_session_init` | `arif.session` | 000_INIT |
| 2 | `arif_sense_observe` | `arif.observe` | 111_OBSERVE |
| 3 | `arif_evidence_fetch` | *(folded into arif.observe)* | 222_EVIDENCE |
| 4 | `arif_mind_reason` | `arif.reason` | 333_REASON |
| 5 | `arif_heart_critique` | *(folded into arif.reason)* | 444_CRITIQUE |
| 6 | `arif_reply_compose` | `arif.reply` | 444r_REPLY |
| 7 | `arif_kernel_route` | `arif.route` | 555_ROUTE |
| 8 | `arif_memory_recall` | `arif.memory` | 555m_MEMORY |
| 9 | `arif_gateway_connect` | *(folded into arif.route)* | 666g_GATEWAY |
| 10 | `arif_forge_execute` | `arif.forge` | 666_FORGE |
| 11 | `arif_ops_measure` | `arif.ops` | 777_OPS |
| 12 | `arif_judge_deliberate` | `arif.judge` | 888_JUDGE |
| 13 | `arif_vault_seal` | `arif.vault` | 999_VAULT |

### Target surface (Phase 2): 13 dot-separated tools

```
arif.session    — session bootstrap + identity binding
arif.observe    — observation + evidence + fact-check + epistemic
arif.reason     — reasoning + critique + plan review
arif.judge      — constitutional verdict (sole authority)
arif.reply      — governed response composition
arif.route      — intent routing + gateway connect
arif.ops        — health + vitals + cost + budget + probes
arif.lease      — bounded authority lease lifecycle
arif.memory     — recall + steward + vault query
arif.forge      — query + plan + dry_run + simulate + execute
arif.vault      — seal + verify + query + receipt
arif.attest     — organ attestation + peer contracts
arif.shadow     — institutional shadow + narrative tension
```

---

## 2. Legacy Alias Map

Every old tool name must be hidden from `tools/list` and mapped to a canonical tool + mode.

### Hermes (7) → folded

| Legacy Name | Canonical Tool | Canonical Mode | Status |
|-------------|---------------|----------------|--------|
| `hermes_system_status` | `arif.ops` | `system_status` | DIAGNOSTIC, hidden |
| `hermes_vault_query` | `arif.memory` | `vault_query` | DIAGNOSTIC, hidden |
| `hermes_epistemic_check` | `arif.observe` | `epistemic_check` | DIAGNOSTIC, hidden |
| `hermes_fact_check` | `arif.observe` | `fact_check` | DIAGNOSTIC, hidden |
| `hermes_cross_verify` | `arif.observe` | `cross_verify` | DIAGNOSTIC, hidden |
| `hermes_plan_review` | `arif.reason` | `plan_review` | DIAGNOSTIC, hidden |
| `hermes_memory_steward` | `arif.memory` | `steward` | DIAGNOSTIC, hidden |

### Canary (6) → folded into arif.ops

| Legacy Name | Canonical Tool | Canonical Mode | Status |
|-------------|---------------|----------------|--------|
| `arif_ping` | `arif.ops` | `ping` | Hidden from canonical13 |
| `arif_schema_echo` | `arif.ops` | `schema` | Hidden from canonical13 |
| `arif_version_echo` | `arif.ops` | `version` | Hidden from canonical13 |
| `arif_transport_echo` | `arif.ops` | `transport` | Hidden from canonical13 |
| `arif_initialize_probe` | `arif.session` | `probe` | Hidden from canonical13 |
| `arif_conformance_report` | `arif.judge` | `conformance_report` | Hidden from canonical13 |

### Forge sub-tools (3) → folded into arif.forge

| Legacy Name | Canonical Tool | Canonical Mode | Status |
|-------------|---------------|----------------|--------|
| `forge_dry_run` | `arif.forge` | `dry_run` | Deprecated proxy |
| `forge_plan` | `arif.forge` | `plan` | Deprecated proxy |
| `forge_query` | `arif.forge` | `query` | Deprecated proxy |
| `forge_plan_and_simulate` | `arif.forge` | `plan_simulate` | Deprecated proxy |
| `forge_execute` | `arif.forge` | `execute` | Deprecated proxy |

### Lease (3) → canonical

| Legacy Name | Canonical Tool | Canonical Mode |
|-------------|---------------|----------------|
| `arif_lease_inspect` | `arif.lease` | `inspect` |
| `arif_lease_issue` | `arif.lease` | `issue` |
| `arif_lease_revoke` | `arif.lease` | `revoke` |

### Attestation (7) → canonical

| Legacy Name | Canonical Tool | Canonical Mode |
|-------------|---------------|----------------|
| `arif_os_attest` | `arif.attest` | `os` |
| `arif_organ_attest` | `arif.attest` | `organ` |
| `arif_organ_attest_all` | `arif.attest` | `organ_all` |
| `arif_heartbeat` | `arif.ops` | `heartbeat` |
| `arif_peer_contract_attest` | `arif.attest` | `peer_contract_attest` |
| `arif_peer_contract_validate` | `arif.attest` | `peer_contract_validate` |
| `arif_peer_contract_forbid` | `arif.attest` | `peer_contract_forbid` |

### Narrative/Shadow (2) → canonical

| Legacy Name | Canonical Tool | Canonical Mode |
|-------------|---------------|----------------|
| `arif_detect_institutional_shadow_drift` | `arif.shadow` | `institutional_shadow` |
| `arif_detect_narrative_tension` | `arif.shadow` | `narrative_tension` |

---

## 3. Deprecation Policy

1. **Legacy aliases are HIDDEN from `tools/list`** — they never appear in discovery.
2. **Legacy aliases remain CALLABLE** for backward compatibility if existing clients depend on them.
3. **Every legacy call returns deprecation metadata:**
   ```json
   {
     "deprecation": {
       "legacy_tool": "hermes_system_status",
       "canonical_tool": "arif.ops",
       "canonical_mode": "system_status",
       "remove_after": "2026-09-01",
       "migration_status": "DEPRECATED"
     }
   }
   ```
4. **Removal date:** 2026-09-01 (3 months from audit).
5. **Aliases do NOT bypass** auth, lease, judge, vault, or schema checks.

---

## 4. Client Migration Examples

### Before (chatty surface)
```json
{"tool": "Hermes system status", "mode": "full"}
{"tool": "Forge dry run", "intent": "build something"}
{"tool": "A Arif ping"}
{"tool": "Vault Seal", "payload": "..."}
```

### After (canonical surface)
```json
{"tool": "arif.ops", "mode": "system_status"}
{"tool": "arif.forge", "mode": "dry_run", "intent": "build something"}
{"tool": "arif.ops", "mode": "ping"}
{"tool": "arif.vault", "mode": "seal", "payload": "..."}
```

---

## 5. Rollback Instructions

To restore the expanded surface for debugging:
```bash
export ARIFOS_PUBLIC_SURFACE_MODE=expanded45
# Restart server
```

The `expanded45` mode exposes all diagnostic tools alongside canonicals.
It is for internal use only, not for production MCP clients.

---

## 6. Enforcement

The permanent law is in `tests/test_canonical13_enforcement.py`:
- 13 tools exactly in canonical13 mode
- No legacy names (hermes_*, forge_*, etc.)
- No canary probes as separate tools
- No blocked prefixes
- Schema completeness
- Registry truth

CI MUST fail if any of these tests fail.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given.*
