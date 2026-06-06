# Tool Risk Classes

Use this reference when classifying a tool's governance posture.

## Taxonomy

Every tool in the federation MUST declare one of four risk classes. This is distinct from `ActionClass` (OBSERVE/PREPARE/MUTATE/ATOMIC) — `ToolClass` describes the policy/approval posture, not the execution phase.

| Class | Meaning | Approval gate | Examples |
|---|---|---|---|
| **observe** | Read-only, no side effects, local scope | None | `arif_ops_measure`, `arif_sense_observe` |
| **retrieve** | Fetch from external or persistent source | Low — attestation only | `arif_evidence_fetch`, `arif_memory_recall` |
| **decide** | Judgment, routing, evaluation, planning | Medium — floor check + receipt | `arif_mind_reason`, `arif_kernel_route` |
| **mutate** | Write, modify, execute, deploy, seal | High — 888_JUDGE or F13 | `arif_forge_execute`, `arif_vault_seal` |

## Escalation ladder

```text
observe → retrieve → decide → mutate
   ↑         ↑          ↑         ↑
  none    attestation  floor    888_JUDGE
                    + receipt   or F13
```

## Mapping to existing schema

- `ToolClass.observe` → `ActionClass.OBSERVE` + `RiskTier.T0/T1`
- `ToolClass.retrieve` → `ActionClass.OBSERVE` + `RiskTier.T1/T2` + external source
- `ToolClass.decide` → `ActionClass.PREPARE` + `RiskTier.T2/T3`
- `ToolClass.mutate` → `ActionClass.MUTATE/ATOMIC` + `RiskTier.T3/T4/T5`

## Integration point

`RiskPassport.tool_class` (StrEnum) is the canonical field. The `risk_classifier.py` engine populates it from keyword heuristics alongside the existing `action_class` and `tier` fields.

## Anti-pattern

Do NOT classify open-ended tools (shell, URL-fetch, eval) as `observe` or `retrieve`. They are `mutate` with `BlastRadius.INFRA`.
