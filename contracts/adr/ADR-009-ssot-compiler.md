# ADR-009: SSOT Compiler Architecture

**Status:** RATIFIED
**Date:** 2026-06-22
**Decision-makers:** F13 SOVEREIGN (Arif), FORGE agent
**Supersedes:** None (new)

## Context

arifOS has 22 canonical tools governed by 13 constitutional floors. Tool metadata was scattered across multiple files:

- `arifosmcp/constitutional_map.py` — CANONICAL_TOOLS dict (21 tools, Python dataclasses)
- `contracts/tools.yaml` — hand-maintained manifest (13 tools, stale)
- `arifosmcp/schemas/kernel_envelope.py` — ToolManifestEntry (Pydantic)
- `arifosmcp/mcp_surface_registry.yaml` — MCP surface registration
- `arifosmcp/runtime/tools.py` — 13-tool registration (17K lines)

Each file described overlapping subsets of the same tools with different field names, different counts, and different levels of detail. Drift was inevitable and undetectable.

## Decision

**One YAML SSOT. One compiler. Four generated artifacts.**

### Architecture

```
contracts/tools.yaml          ← THE SSOT (hand-maintained, 22 tools)
    │
    ▼
contracts/compiler.py         ← reads tools.yaml, validates, emits
    │
    ├── generated/capability_graph.json      (runtime capability graph)
    ├── generated/tool_validators.py         (Pydantic input/output validators)
    ├── generated/audit_schemas.json         (audit event payload schemas)
    └── generated/conformance_fixtures.json  (happy + denial path fixtures)
```

### SSOT fields (per tool)

Every tool in `tools.yaml` carries these fields (frozen taxonomies):

| Field | Type | Purpose |
|-------|------|---------|
| `canonical_name` | string | Unique tool identifier |
| `axis` | enum | Governance lane (identity, observe, reason, etc.) |
| `pipeline_stage` | enum | Metabolic stage (intake, intent, plan, verdict, execute, receipt, seal) |
| `role` | string | Human-readable role description |
| `modes` | list | Allowed invocation modes |
| `input_schema` | object | JSON Schema for tool input |
| `output_schema` | object | JSON Schema for tool output |
| `reversibility` | enum | reversible / guarded / irreversible |
| `blast_radius` | enum | low / medium / high / civilizational |
| `authority_required` | enum | public / operator / sovereign |
| `channel` | enum | stable / beta / sandbox |
| `hold_conditions` | list | Conditions that trigger HOLD |
| `denial_codes` | list | Machine-readable denial reasons |
| `audit_events` | list | Events emitted to VAULT999 |
| `witness_requirements` | list | Required witness legs (human/ai/earth) |
| `contract_version` | string | Semver for this tool's contract |

### Tool universe (locked)

| Section | Count | Description |
|---------|-------|-------------|
| `canonical_tools` | 13 | Core kernel surface |
| `diagnostic` | 1 | Read-only health/telemetry |
| `federated_organs` | 7 | Organ boundary + bridge + forge |
| `sanctioned_non_arif` | 1 | Hermes vault query |

Total: 22. Count drift = conformance failure.

### Compiler validation

The compiler validates every tool against frozen taxonomies:
- All enum values must exist in `taxonomies` section
- Beta channel must have `authority_required=sovereign` OR `hold_conditions`
- Sandbox must be `reversible`
- `irreversible` must require `sovereign` authority
- `civilizational` blast radius must require `sovereign` authority
- No duplicate `canonical_name`
- All `denial_codes` and `audit_events` must exist in taxonomy

### Denial code taxonomy

32 denial codes, each mapped to:
- Constitutional floor (F1-F13)
- Severity (hard = VOID, soft = HOLD)
- Description
- Remediation path
- Kernel action

Defined in `contracts/denial_codes.py` as `DenialCode` enum + `DenialRecord` dataclass.

### Introspection engine

`contracts/kernel_status.py` provides 4 modes:
- `discover` — contract family, counts, stages, channels, taxonomies
- `list_capabilities` — normalized tool list with governance metadata
- `show_contract(tool_name)` — full contract + derived audit/denial
- `find_orphans` — three-way drift: YAML ↔ generated graph ↔ runtime registry

## Consequences

### Positive
- One file to edit when adding/modifying tools
- Compiler catches taxonomy violations at build time
- Drift detection is automatic (find_orphans)
- Every tool has machine-readable denial codes and audit schemas
- Conformance tests verify the contract at CI time

### Negative
- `tools.yaml` must be kept in sync with actual tool implementations
- Compiler must be re-run after any tools.yaml change
- Generated artifacts must not be hand-edited

### Mitigations
- `find_orphans` mode detects YAML ↔ runtime drift
- `.gitignore` should exclude `generated/` (build artifacts)
- Conformance tests run in CI

## Related
- ADR-010: Channel Policy
- ADR-011: Plan Enforcement Membrane
- ADR-012: Receipt Lineage and Sealing

## Verification

```bash
# 1. Compile
python contracts/compiler.py

# 2. Verify introspection
python contracts/kernel_status.py discover
python contracts/kernel_status.py find_orphans

# 3. Run conformance tests
python -m pytest tests/test_contract_conformance.py -v

# 4. Check denial codes
python contracts/denial_codes.py list
```

DITEMPA BUKAN DIBERI — Compiled, not hand-waved.
