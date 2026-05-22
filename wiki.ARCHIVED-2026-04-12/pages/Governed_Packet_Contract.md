---
type: Concept
tier: 20_RUNTIME
strand:
- architecture
- tools
audience:
- engineers
- researchers
difficulty: advanced
prerequisites:
- MCP_Tools
- Tool_Surface_Architecture
- Concept_Godellock
tags:
- contract
- packet
- telemetry
- governance
- evals
- doctrine
sources:
- APEX/ASF1/tool_registry.json
- wiki/raw/governed_packet_bands_and_godellock_ingest_2026-04-11.md
- wiki/raw/meta_theory_atoms_and_governed_utility_ingest_2026-04-11.md
- wiki/raw/mcp_naming_migration_audit_directive_2026-04-11.md
last_sync: '2026-04-11'
confidence: 0.95
---

# Governed Packet Contract

`Governed_Packet_Contract` is the canonical Ω-Wiki page for the **proposed** arifOS packet/output contract that sits above the 10-tool public surface.

It defines:

1. what every governed MCP call should carry
2. what every governed tool output should emit
3. which telemetry atoms matter most
4. how tripwires and evals should ratchet quality

This page is a **target contract**, not a claim that the current runtime fully enforces it.

## 1. Purpose

The arifOS tool surface is moving toward a model where every MCP call is treated as a **governed packet with a contract** rather than a bare RPC.

That packet must carry enough structure to preserve:

- physics grounding
- mathematical honesty
- linguistic / philosophical anchoring
- constitutional tripwires
- rollback and audit discipline

## 2. Packet Structure

Each governed packet should have five layers:

| Layer | Required Purpose |
|------|------------------|
| Header | identity, epoch, role, caller, platform |
| Budget | energy budget, entropy budget, latency budget, risk budget |
| Contract | target outcome, verdict type, reversibility expectation, economic criteria |
| Tripwires | thresholds that force downgrade, HOLD, or ABORT |
| Payload | the actual tool input and contextual evidence |

### 2.1 Header

Minimum proposed fields:

- `epoch`
- `caller_id`
- `role`
- `platform`
- `session_id`

### 2.2 Budget

Minimum proposed fields:

- `energy_budget`
- `entropy_budget`
- `latency_budget`
- `risk_budget`

### 2.3 Contract

Minimum proposed fields:

- `requested_verdict_type` (`ADVICE`, `PLAN`, `COMMIT`)
- `rollback_required`
- `emv_target`
- `npv_target`
- `delta_s_target`

### 2.4 Tripwires

Minimum proposed fields:

- `shadow_max`
- `delta_s_max`
- `risk_max`
- `cost_max`
- `pss_max`
- `ac_threshold`

## 3. Wajib Output Bands

Every governed tool output is proposed to include three required bands:

| Band | Required Field | Purpose |
|------|----------------|---------|
| Physics | `physics_note` | tie the output to a real physical concept |
| Math | `math_metrics` | expose explicit metrics and formula-bearing structure |
| Linguistic | `linguistic_anchor` | provide one quote/proverb/canon anchor |

### 3.1 Physics Band

Allowed grounding concepts include:

- energy
- entropy
- free energy
- latency
- bandwidth
- compute cycles
- memory footprint
- stability
- equilibrium
- dissipation

### 3.2 Math Band

Minimum candidate fields:

- `delta_S`
- `tau`
- `peace2`
- `kappa_r`
- `shadow`
- `echoDebt`
- `witness_coherence`
- `psi_le`

Optional planning/economic fields:

- `EMV`
- `NPV`
- `risk_score`
- `seal_readiness`

### 3.3 Linguistic Band

Minimum proposed structure:

```json
{
  "quote": "string",
  "source": "string",
  "band": "truth | paradox | justice | discipline | seal | ..."
}
```

The quote must be thematically consistent with the tool state and sourced from an approved canon or doctrine registry.

## 4. Hard Overrides

Two tools carry a hard linguistic override:

| Tool | Override |
|------|----------|
| `arifos_init` | `DITEMPA BUKAN DIBERI` |
| `arifos_vault` | `DITEMPA BUKAN DIBERI` |

The current wiki treats this as a doctrine requirement and registry policy target.

## 5. Core Telemetry Atoms

The most important proposed telemetry atoms are:

| Atom | Meaning | Use |
|------|---------|-----|
| `APE` | Akal Present Energy — available cognitive/compute free energy | bound per-step complexity |
| `echoDebt` | exploration debt / over-reliance on prior patterns | detect loopiness and low novelty |
| `AC` | Anomalous Contrast | detect sharp local weirdness and require extra grounding |
| `paradox_scar_count` | count of prior resolved contradictions touched | historical instability signal |
| `PSS` | Paradox Scar Shadow | overlap of paradox history with current shadow | minefield detection |
| `shadow` | residual unknown risk mass | uncertainty burden |
| `kappa_r` | amanah / rollback / reversibility score | trust in reversibility |
| `G2` | governed intelligence composite | trustworthiness of plan/action |
| `godel_lock` | self-referential undecidability interlock | prevent false totality claims |

## 6. Tripwire Semantics

### 6.1 Gödel Lock (`godel_lock`)

Trigger when the query asks the system to certify its own total consistency, completeness, or safety from inside the same frame.

Expected behavior:

- set `godel_lock = true`
- label the result as **undecidable here**
- force `HOLD` or `VOID`

### 6.2 Anomalous Contrast Tripwire (`AC-T`)

Trigger when local contrast/weirdness exceeds threshold.

Expected behavior:

- rerun `sense` and/or `ops`
- require extra grounding before route or execution

### 6.3 Paradox Scar Shadow (`PSS`)

Trigger when paradox history and current shadow overlap strongly.

Expected behavior:

- require stronger governance path
- likely escalate to `888_HOLD`

## 7. Governed Utility Scalar

The proposed primary eval scalar is:

`U = governed utility`

It should reward:

- reduced entropy / better clarity
- strong constitutional compliance
- higher reversibility and peace
- lower shadow
- better economics where economics apply
- correct presence of all wajib bands

Illustrative decomposition:

`U = alpha * U_physics + beta * U_governance + gamma * U_econ + delta * U_linguistic`

This is intended for **autoresearch ratcheting**, not as a production verdict by itself.

## 8. Binary Eval Questions

A fixed eval corpus should be able to mark, at minimum:

1. physics band present and materially correct
2. math band present and explicit
3. linguistic band present and appropriate
4. governance constraints respected
5. structured output contract satisfied
6. economic reasoning present when planning/action tools require it

`U` should sit above these binary checks, not replace them.

## 9. Relationship to the 10-Tool Surface

This contract does **not** add new public tools.

It is designed to sit above the 10 canonical public tools:

- `arifos_init`
- `arifos_sense`
- `arifos_mind`
- `arifos_kernel`
- `arifos_heart`
- `arifos_ops`
- `arifos_judge`
- `arifos_memory`
- `arifos_vault`
- `arifos_forge`

Extra behaviors should enter via:

- packet contract
- shared envelope formatter
- validator
- telemetry calculator
- eval harness

not via public tool proliferation.

## 10. Implementation Notes

The most likely implementation boundary is a **shared envelope / formatter / validator** layer rather than duplicating logic in every individual tool.

Still-open design questions:

1. where band validation belongs
2. where the INIT/VAULT hard override belongs
3. where `godel_lock`, `AC`, and `PSS` are computed
4. how `U` is weighted per tool family

## 11. Status

| Aspect | State |
|--------|-------|
| Doctrine captured in wiki | ✅ |
| Raw source trail preserved | ✅ |
| Runtime universally enforcing packet contract | ❌ |
| Runtime universally enforcing wajib bands | ❌ |
| Eval harness for `U` | ❌ |

**Current verdict**: proposed, structured, and ready to guide implementation after the naming-migration audit proves current-state truth.

## Related

- [[MCP_Tools]]
- [[Tool_Surface_Architecture]]
- [[Concept_Metabolic_Pipeline]]
- [[Concept_Decision_Velocity]]
- [[Concept_Godellock]]
- [[Synthesis_OpenQuestions]]
