# ADR-009: Constitutional Contract Compiler + SSOT Architecture

**Status:** RATIFIED
**Date:** 2026-06-22
**Sovereign:** arif (F13)
**Forge session:** FORGE-000Ω
**Supersedes:** none
**Related:** ADR-010 (channel policy), ADR-011 (plan enforcement membrane), ADR-012 (receipt lineage)

---

## Context

The arifOS kernel previously maintained its tool registry as a hand-coded Python
dictionary in `arifosmcp/kernel/capability_registry.py`. Every tool addition required
manual edits, and there was no single source of truth (SSOT) that the kernel
interceptor, the tool manifest, the audit schemas, and the conformance tests
could all be derived from. This produced **structural drift** — for example, 13 of
21 canonical tools were missing from the capability graph even though they
appeared in `AGENTS.md` and the MCP manifest. The kernel returned `KERNEL_DENY:
Unknown capability` for tools the sovereign was actively invoking.

## Decision

Establish a **compiled constitutional runtime (CCR)** with three layers:

```
┌─────────────────────────────────────────────────────────────┐
│  contracts/tools.yaml  ── THE SINGLE SOURCE OF TRUTH         │
│    • 10 frozen taxonomies (reversibility, blast_radius,     │
│      authority_required, channel, verdicts, witness_legs,   │
│      pipeline_stages, contract_class, mutation_class,        │
│      retryability)                                          │
│    • 12 governance axes (000_KERNEL → 999_SEAL)              │
│    • 22 denial codes (code, floor, severity,                 │
│      retryability, description, remediation)                │
│    • 14 audit events (intent_created → drift_detected)        │
│    • 21 legacy aliases (arifos_* → arif_*, sunset 2026-12-31)│
│    • 22 tools in 4 explicit sections:                        │
│        - 13 canonical (arif_init, …, arif_seal)              │
│        - 1 diagnostic (arif_measure)                          │
│        - 7 federated (arif_route, …, arif_canary)            │
│        - 1 sanctioned_non_arif (hermes_vault_query)          │
└─────────────────────────────────────────────────────────────┘
                          │
                          │  contracts/compiler.py
                          │  (8 passes: load → validate_meta_schema
                          │   → normalize_names_and_aliases →
                          │   expand_taxonomies → emit 4 artifacts)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  generated/  (NEVER hand-edited; rebuilt by compiler)         │
│    • capability_graph.json     — runtime capability graph    │
│    • tool_validators.py        — Pydantic input/output models│
│    • audit_schemas.json        — JSON schemas per event      │
│    • conformance_fixtures.json — 5 fixture classes:         │
│        1. happy                  (22 fixtures)              │
│        2. schema_pass_constitution_fail (22 fixtures)         │
│        3. schema_pass_channel_fail (4 fixtures)               │
│        4. schema_pass_witness_fail (0 fixtures, expandable)   │
│        5. legacy_alias_pass      (21 fixtures)               │
└─────────────────────────────────────────────────────────────┘
                          │
                          │  contracts/kernel_status.py
                          │  (4 of 9 modes: discover,                 │
                          │   list_capabilities, show_contract,        │
                          │   find_orphans — others stubbed)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  RUNTIME  (kernel interceptor + capability graph)            │
│    • CapabilityNode ← generated/capability_graph.json         │
│    • Floor 1 (Unknown capability) ← generated conformance    │
│    • Floor 7b (allowed_actors) ← SSOT allowed_actors field   │
│    • Seal-class tools (contract_class=seal) require          │
│      verdict_token + epoch_id + receipt_parent_ids            │
│    • Gateway-class tools (contract_class=gateway) require     │
│      plan_id (PLAN → VERDICT → EXECUTE path)                 │
└─────────────────────────────────────────────────────────────┘
```

## Tool contract shape (16 required fields + meta)

```yaml
- canonical_name: arif_seal                          # canonical
  role: vault_sealing                                 # human-readable role
  axis: "999_SEAL"                                    # governance axis
  pipeline_stage: seal                               # INTAKE → SEAL
  contract_class: seal                               # ordinary|gateway|verdict|seal|diagnostic
  mutation_class: seal                               # read|write|execute|seal
  requires_plan: true                                # PLAN→VERDICT→EXECUTE
  modes: [seal, verify, ledger, changelog, audit]    # bounded behaviors
  input_schema: {...}                                # JSON Schema
  output_schema: {...}
  reversibility: irreversible                        # reversible|guarded|irreversible
  blast_radius: civilizational                        # low|medium|high|civilizational
  authority_required: sovereign                      # public|operator|sovereign
  channel: stable                                     # stable|beta|sandbox
  hold_conditions: [actor_must_be_sovereign, requires_verdict_token, requires_epoch_id, requires_receipt_parent_ids]
  denial_codes: [IRREVERSIBLE_WITHOUT_HOLD, AUTHORITY_INSUFFICIENT, HUMAN_VETO_REQUIRED, VERDICT_TOKEN_MISSING, EPOCH_MISMATCH]
  audit_events: [verdict_issued, witness_attached, seal_written]
  witness_requirements: [human, ai]                  # explicit set
  requires_verdict_token: true                       # SEAL class
  requires_epoch_id: true
  requires_receipt_parent_ids: true
  contract_version: "1.0.0"                          # semver
  notes: "..."
```

## Compiler — 8 passes (deliberately boring)

```python
def compile_all() -> dict:
    doc = load_yaml(SSOT_PATH)              # Pass 1
    validate_meta_schema(doc)               # Pass 2
    norm = normalize_names_and_aliases(doc)  # Pass 3 — resolves legacy arifos_* → arif_*
    tax = expand_taxonomies(doc)             # Pass 4 — freeze enum sets
    graph = generate_capability_graph(doc, norm, tax)  # Pass 5
    schemas = generate_audit_schemas(doc)    # Pass 6
    fixtures = generate_conformance_fixtures(doc)  # Pass 7 — 5 fixture classes
    validators = emit_runtime_validators(doc) # Pass 8
    # ... write 4 artifacts
```

**Pass design rationale (per sovereign directive 2026-06-22):** keeping passes
small and named makes diffing and incident forensics cheap. Each pass is
independently testable.

## kernel_status — 4 of 9 modes

The arif_kernel_status engine is the kernel's self-introspection surface. The
**stable response envelope** is:

```json
{
  "mode": str,
  "ok": bool,
  "generated_from_contract_version": str,
  "counts": dict,
  "items": list,
  "orphans": list,
  "warnings": list,
  "denials": list
}
```

This envelope is identical across all 9 modes so the other 5 modes (show_audit_map,
find_contract_drift, explain_denial, show_channel_matrix, show_floor_coverage)
slot in without breaking callers.

The 4 implemented modes:

1. **`discover`** — returns counts (sections, channels, contract_classes, mutation_classes, authorities, axes) and frozen taxonomies.
2. **`list_capabilities`** — normalized list of 22 tools with axis, stage, channel, authority, reversibility, fingerprint, legacy_aliases.
3. **`show_contract(tool_name)`** — full contract object + referenced denial codes + audit events. Resolves via legacy alias map.
4. **`find_orphans`** — three-way drift detection: SSOT ∩ graph ∩ live MCP. Caught **4 real MCP drift orphans** in first run.

## Constitutional compliance

| Floor | Compliance | Evidence |
|---|---|---|
| F1 AMANAH | ✓ | Compiler is side-effect-free; 4 generated artifacts are deterministic from SSOT; rollback = `git checkout`. |
| F2 TRUTH | ✓ | Every denial code maps to floor + severity + retryability + remediation. Compiler fails loud (sys.exit) on schema violations. |
| F4 CLARITY | ✓ | One SSOT, one compiler, one engine. No parallel registries. |
| F7 HUMILITY | ✓ | Confidence cap implicit — 4 of 9 modes implemented; others explicitly stubbed with warning. |
| F8 LAW | ✓ | No architectural floor change. Only adds the compiler pattern. |
| F9 ANTI-HANTU | ✓ | No consciousness/soul/sentience vocabulary. compiler, kernel_status, generated — all mechanical. |
| F10 MECHANICAL | ✓ | `alignment_profile` / `adversarial_profile` not in tool names. |
| F11 AUDIT | ✓ | Every compile emits a fingerprint per tool. find_orphans catches drift. |
| F13 SOVEREIGN | ✓ | No push to main without 888_HOLD (per AGENTS.md). |

## Consequences

### Positive

- **Drift detection is now real.** find_orphans already caught 4 MCP drift orphans.
- **Schema is versioned.** `meta_schema.version: "0.1.0"` is in the SSOT itself.
- **Denial codes are constitutional primitives**, not random exceptions.
- **arif_seal got the special treatment it needed**: requires verdict_token, epoch_id, receipt_parent_ids.
- **Legacy aliases (arifos_*) are tracked** with deprecated_after dates — sunset 2026-12-31.

### Negative

- **Build step is now mandatory.** Every SSOT change requires `python contracts/compiler.py` to run before tests.
- **The kernel's runtime `CapabilityNode` and the generated capability graph can drift** if the kernel is restarted without a recompile. (Mitigation: `find_orphans` catches it at runtime.)
- **The other agents' compiler (constitutional_map → YAML) is now wrong direction.** Their work is preserved at `/root/forge_work/parallel-work-2026-06-22/`.

### Risks and mitigations

| Risk | Mitigation |
|---|---|
| Compiler drift from runtime | `find_orphans` runs against live MCP. Add to `make health`. |
| Schema breaking changes | `meta_schema.breaking_change_policy` field documents the rule. |
| Generated files committed | Add `contracts/generated/` to `.gitignore` (carry-forward). |
| Legacy aliases never removed | `deprecated_after: 2026-12-31` in alias map. Runtime can hard-fail aliases after that date (carry-forward). |

## Success criteria (all met)

- [x] `tools.yaml` loads with zero schema errors.
- [x] Compiler emits all 4 generated artifacts.
- [x] `kernel_status(mode=discover)` returns stable counts.
- [x] `kernel_status(mode=list_capabilities)` lists all 22 SSOT tools.
- [x] `kernel_status(mode=show_contract, "arif_seal")` returns full contract.
- [x] `kernel_status(mode=find_orphans)` returned 4 real MCP drift orphans on first run.
- [x] Conformance fixtures generated: 22 happy + 22 fail + 4 channel + 0 witness + 21 legacy = 69 total.

## Decision

**Adopted.** The compiler pattern is the canonical path forward. Hand-maintained
capability graphs are now illegal — any change to arifOS tooling must be in
`tools.yaml` first, then compiled.

DITEMPA BUKAN DIBERI — Compiled, not hand-waved.
