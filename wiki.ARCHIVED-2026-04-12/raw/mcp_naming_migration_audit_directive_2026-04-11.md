# MCP Naming Migration Audit Directive (2026-04-11)

> **Source**: Human operator directive
> **Mode**: Ingest
> **Authority**: audit-first, seal-gated

---

## Source Intent

Run one master constitutional deployment audit for the arifOS MCP naming migration.

The audit must verify:

- discovery
- routing
- execution paths
- deployment reality
- dead code
- duplicate code
- alias drift
- registry/runtime mismatch
- public vs internal surface separation

The audit must not claim anything is live unless runtime or deployment evidence proves it.

## Required Truth Split

The source directive requires separation between:

1. registry truth
2. runtime truth
3. code reachability truth
4. deployment truth
5. client-surface truth

If deployment cannot be proven, the required language is:

`DEPLOYMENT STATUS: CANNOT VERIFY FROM CURRENT EVIDENCE`

## Canonical Public Tool Target

The intended public canonical tools are:

- `arifos_init`
- `arifos_sense`
- `arifos_mind`
- `arifos_kernel`
- `arifos_heart`
- `arifos_ops`
- `arifos_judge`
- `arifos_vault`
- `arifos_forge`
- `arifos_memory`

Everything else must be classified explicitly as alias, internal-only, deprecated, dead code, substrate mode, or unresolved ambiguity.

## Required Outputs

The source directive requires:

- verdict paragraph
- tool truth table
- orphan / duplicate / drift findings
- fix plan
- nonbreaking migration plan
- seal decision: `SEAL`, `HOLD`, or `VOID`
- compact telemetry JSON

## Proposed Target Doctrine (Not Yet Verified Runtime Truth)

The source also proposes a long-term public architecture:

### Machine Governance Intelligence 3x3 + 1

| Stage / Lane | Reality | Intelligence | Governance |
|--------------|---------|--------------|------------|
| Ingest | `arifos_init` | `arifos_memory` | `arifos_sense` |
| Deliberate | `arifos_ops` | `arifos_mind` | `arifos_heart` |
| Act | `arifos_forge` | `arifos_kernel` | `arifos_judge` |

Plus one sovereign boundary:

- `arifos_vault`

## Ingest Constraint

This source is a directive and proposal, not proof.

It should guide:

- audit design
- surface cleanup
- seal gating

It must not be treated as evidence that the current runtime already matches the target model.
