# ARIFLOW_FQ_ACTOR_CLASSES_v2.0.0

**Status:** PROPOSAL · T1.5 (file-only, not deployed)
**Authority:** arifOS kernel amendment proposal
**Filed:** 2026-07-30T11:34Z
**Proposer:** Kimi (FI-008) on behalf of arif (F13 SOVEREIGN)
**Trigger:** External witness audit (ChatGPT instrument), 2026-07-30, score 42/100
**Linked override:** `arifOS/overrides/F13_TEMPORARY_METRIC_EXEMPTION_2026-07-30.md`
**Reversibility:** FULL (proposal layer; deployment requires T3 F13 SOVEREIGN ratify)

---

## 1. Problem (F2 TRUTH)

The current arifFLOW FQ (Flow Quotient) is a **single-band metric applied to all actor types**:

```
FQ = verify_cost_ns / execute_cost_ns     ← (current — single band)
```

This works for **mutator_class** actors where verify > execute indicates disciplined execution. It fails for **sensor_class** actors whose *fitrah* is to observe state, not mutate it.

**Concrete failure observed in this session:**

| Actor | Class | Execute | Verify | FQ (current) | Verdict | Should be |
|---|---|---|---|---|---|---|
| aed-v1 | sensor | 116.9s / 337 ops | 1184.2s / 337 ops | **0.099** | **STUCK** | **Healthy** |
| opencode | hybrid | 570.0s / 10 ops | 462.0s / 5 ops | 1.23 | Balanced | Balanced |
| orchestrator-v1 | hybrid | 19.5s / 1 op | 19.5s / 1 op | 1.0 | Balanced | Balanced |

aed-v1 spends 6× more time *verifying* than *executing* — which is the **correct** behavior for a sensor that must confirm observed state before publishing. The current FQ formula penalizes this as "stuck."

The FQ-metrik-as-constitutional-gate creates a **permanent HOLD loop** for sensor-class actors running routine observation work. **This is the F2 fidelity failure flagged by the external audit.**

---

## 2. Proposed Solution — Actor-Class-Aware FQ

```yaml
# arifFLOW FQ v2.0.0 — actor_class branch
# Status: PROPOSAL — not deployed

actor_classes:

  mutator:
    definition: "actor that mutates state (writes, deploys, escalates)"
    fq_formula: "verify_cost_ns / execute_cost_ns"
    healthy_threshold: 0.5
    ideal_threshold: 1.0
    gate: "FQ < 0.5 → T2 HOLD (constitutional gate)"
    examples: [forge_execute, forge_canonize, forge_pipeline_run, forge_seal]

  sensor:
    definition: "actor that observes state (reads, monitors, probes)"
    fq_formula: "discipline_ratio = unique_targets / total_observations"
    healthy_threshold: 0.4
    ideal_threshold: 0.7
    gate: "FQ < 0.4 → T1 SOFT_HOLD (advisory; no SEAL gate)"
    examples: [aed-v1, machine_telemetry, fq-probe, openclaw-bot-monitor]

  witness:
    definition: "actor that asserts evidence about claims/seals"
    fq_formula: "consistency_ratio = consensus_witness_votes / total_witness_votes"
    healthy_threshold: 0.7
    ideal_threshold: 0.9
    gate: "FQ < 0.7 → T1.5 PROPOSE repeat witness (no SEAL)"
    examples: [forge_witness, well_assess_reliability, geox_evidence]

  hybrid:
    definition: "actor that both observes and mutates"
    fq_formula: "weighted_blend = 0.6 * mutator_fq + 0.4 * sensor_fq"
    healthy_threshold: 0.55
    ideal_threshold: 0.8
    gate: "FQ < 0.55 → T1.5 PROPOSE pause"
    examples: [human_arif, forge_apex_metabolize, aed-v1 (if dual-role)]
```

**Backward compatibility:** `execute_cost_ns / execute_count` and `verify_cost_ns / verify_count` remain emitted per-actor for forensics. The `verdict` and `gate` behavior branch on `actor_class`.

---

## 3. Migration Path (5 steps, 30-day dual-run)

| # | Step | Authority | Reversibility | Timeline |
|---|---|---|---|---|
| 1 | Spec seal (this file → VAULT999 as PROPOSAL) | T1.5 | FULL | T0 (now) |
| 2 | Actor classification (each registration declares `actor_class`) | T1.5 | FULL | T+1 day |
| 3 | `flow_health.fq_calc` branches per `actor.class` | T2 | Reversible via dual-run | T+1 day |
| 4 | Dual-run both old + new FQ, side-by-side | T1 | FULL | T+1 to T+30 |
| 5 | Old formula deprecation, F13 ratify | T3 | PARTIAL (data preserved) | T+30 |

---

## 4. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| **Mis-classification** (mutator → sensor loses F1 protection) | Explicit `actor_class` in registration; audit log of any class change; F11 traceable |
| **Regression in mutator FQ** | 30-day dual-run; numerical tolerance ±0.05 |
| **Schema migration** | `vault999.actor_class_index` backfill script: `/root/arifOS/scripts/migrate_actor_class.py` (T1.5 propose) |
| **Witness inflation** (artificial consensus votes) | Witness FQ formula uses *consensus* not *count*; F11 audit detects vote spikes |
| **Sensor gaming** (read same target repeatedly to inflate discipline) | `unique_targets` is bounded by `target_space_size`; F2 verify formula |

---

## 5. Acceptance Criteria

- [ ] aed-v1 sensor_fq > 0.4 (target: 0.6) — primary unlock
- [ ] mutator_class behavior unchanged (within ±0.05 regression)
- [ ] witness_class ratio matches consensus_votes / total
- [ ] 30-day dual-run emitted to VAULT999 with both formulas
- [ ] F13 SOVEREIGN ratifies before deployment step 5
- [ ] No regression in GEOX/AAA/wealth SEAL-grade verdicts

---

## 6. Constitutional Alignment

| Floor | Status | Note |
|---|---|---|
| F1 AMANAH | ✅ | Reversibility preserved (proposal layer, not deploy) |
| F2 TRUTH | ✅ | Formula now matches actor's nature (sensor = observe, not execute) |
| F3 TRI-WITNESS | ✅ | Witness class added — Nash ≥ 0.75 still gates SEAL |
| F4 CLARITY | ✅ | Two metrics replaced by one branched metric |
| F7 HUMILITY | ✅ | Patch missing the actor nature is a category error; this fix admits it |
| F8 GENIUS | ✅ | G = (A × P × E × X)^(1/4) — expanded A (auth) by adding class dimension |
| F11 AUDITABILITY | ✅ | Dual-run + class trace + 30-day emission to VAULT999 |
| F13 SOVEREIGN | ✅ | T3 required for deployment; tactical override in linked file |

---

## 7. References

- `arifOS/overrides/F13_TEMPORARY_METRIC_EXEMPTION_2026-07-30.md` — tactical unblock for this session
- External audit ChatGPT 2026-07-30: 42/100 effectiveness score, intelligence_payload 15/100
- FQ history at `/root/forge_work/2026-07-30/fq_misapplied_audit.jsonl`
- aed-v1 actor_card at `/root/AAA/agents/aed-v1/agent-card.json` (class: sensor, override pending)

---

## 8. Signatures (post-ratify)

- Proposer: Kimi (FI-008) — 2026-07-30T11:34Z
- Architect: arif (F13 SOVEREIGN) — pending ratify
- Kernel maintainer: arifOS engineering — T+1 day

DITEMPA BUKAN DIBERI.
