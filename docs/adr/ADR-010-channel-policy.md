# ADR-010: Channel Policy (stable | beta | sandbox)

**Status:** STUB (Phase-1 contract frozen; enforcement lands in Phase-2)
**Date:** 2026-06-22
**Sovereign:** arif (F13)
**Forge session:** FORGE-000Ω
**Related:** ADR-009 (compiler + SSOT)

---

## Status

This ADR captures the **Phase-1 contract** for channel policy. The compiler
emits the contract into the generated capability graph. **Runtime enforcement
of the beta/sandbox channels lands in a future cycle** (carried forward).

---

## Decision

Every tool declares a `channel: stable | beta | sandbox` field in
`contracts/tools.yaml`. The compiler emits it into the runtime graph. The
**taxonomy** is frozen in the SSOT.

| Channel | Default | Mutation allowed | Required authority | Notes |
|---|---|---|---|---|
| `stable` | ✓ | yes | LOW / MEDIUM / HIGH / SOVEREIGN | Production-ready, all F1-F13 floors fully enforced. |
| `beta` | — | yes | **SOVEREIGN only** (or hold_conditions) | Pre-release. Beta **never relaxes floors**; it only restricts authority. |
| `sandbox` | — | **no** (live side effect) | any | Isolated test. Tool must have `reversibility: reversible`. Runs against fixtures only. |

## Conformance rules (already enforced by compiler)

- `tools[channel=beta].authority_required == sovereign OR tools[channel=beta].hold_conditions non-empty`
- `tools[channel=sandbox].reversibility == reversible`
- `tools[reversibility=irreversible].authority_required == sovereign`
- `tools[blast_radius=civilizational].authority_required == sovereign`

Current SSOT state: 22 tools on `stable`, 0 on `beta`, 0 on `sandbox`. As new
tools are added in beta or sandbox, the compiler will enforce the rules.

## Phase-2 (carry-forward)

1. The kernel interceptor at `arifosmcp/kernel/interceptor.py` should read the
   `channel` field from the runtime graph and apply the policy at admit time.
2. `arif_gateway_connect` (gateway class) should be a candidate first cut for
   beta/sandbox routing.
3. The `arif_kernel_attest` tool should expose channel coverage in its output.

DITEMPA BUKAN DIBERI — Beta never relaxes floors.
