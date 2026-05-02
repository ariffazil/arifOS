# End-to-End Traceability Spine
**v2026.05.03 · SEALED**
> DITEMPA BUKAN DIBERI — Intelligence is forged, not given.

---

## Core Principle

> **No output without lineage. No action without authority. No claim without state. No seal without readback.**

From the first human intent to the final Vault seal, every claim, tool call, evidence object, decision, and side effect must share **one trace spine**. Not logs everywhere. A single lineage.

---

## 1. Trace Spine — Required Fields

```json
{
  "trace_id": "TRACE-20260503-xxxx",
  "session_id": "SEAL-xxxx",
  "epoch_id": "epoch/2026-05-02-immune-system",
  "actor_id": "Muhammad Arif bin Fazil",
  "model_governance_card_hash": "sha256:...",
  "judge_state_hash": null,
  "vault_entry_id": null
}
```

| Field | Purpose |
|---|---|
| `trace_id` | End-to-end operation ID |
| `session_id` | arifOS governed session |
| `epoch_id` | Release / campaign / decision epoch |
| `actor_id` | Human sovereign or delegated agent |
| `model_governance_card_hash` | Proves which model/runtime boundary was active |
| `judge_state_hash` | Proves what 888_JUDGE decided |
| `vault_entry_id` | Final immutable anchor |

The `trace_id` must appear in every MCP call payload, result, log, artifact, and Vault event.

---

## 2. Four-Witness Trace Model

| MCP | Witness type | What it proves |
|---|---|---|
| arifOS | Constitutional witness | Was this allowed? |
| GEOX | Reality witness | What evidence supports the Earth claim? |
| WEALTH | Value witness | What is the economic / allocation consequence? |
| WELL | Readiness witness | Was the human-machine substrate fit? |

**Reality + Value + Readiness + Judgment = Traceable Decision**

---

## 3. Canonical Trace Packet

```json
{
  "trace": {
    "trace_id": "TRACE-20260503-0001",
    "parent_trace_id": null,
    "session_id": "SEAL-xxxx",
    "epoch_id": "epoch/2026-05-02-immune-system",
    "actor_id": "Muhammad Arif bin Fazil",
    "intent": "Evaluate prospect and decide whether to proceed",
    "decision_class": "C4",
    "reversibility": "reversible_until_commitment",
    "model_governance_card_hash": "sha256:...",
    "created_at": "2026-05-03T01:17:00+08:00"
  },
  "lineage": {
    "inputs": [],
    "evidence_refs": [],
    "tool_calls": [],
    "artifacts": [],
    "drift_events": [],
    "judge_state_hash": null,
    "vault_entry_id": null
  },
  "claim_state": {
    "status": "IN_PROGRESS",
    "truth_band": "UNVERIFIED",
    "confidence": null,
    "known_gaps": []
  }
}
```

---

## 4. Tool Call Log Format

Every tool call appends this record:

```json
{
  "call_id": "CALL-0007",
  "trace_id": "TRACE-20260503-0001",
  "mcp": "GEOX",
  "tool": "geox_data_qc_bundle",
  "input_hash": "sha256:...",
  "output_hash": "sha256:...",
  "status": "PASS",
  "claim_state_before": "INGESTED",
  "claim_state_after": "QC_VERIFIED",
  "started_at": "...",
  "ended_at": "...",
  "warnings": [],
  "human_decision_required": false
}
```

This prevents "I did it" claims without tool proof.

---

## 5. Claim-State Ladder

```
DECLARED
  → OBSERVED
  → INGESTED
  → QC_VERIFIED
  → COMPUTED
  → INFERRED
  → JUDGE_REVIEWED
  → VAULT_SEALED
  → VOID
```

**No claim may jump the ladder.**

| Claim | Required state |
|---|---|
| "LAS file exists" | OBSERVED or INGESTED |
| "GR curve passed QC" | QC_VERIFIED |
| "Net pay = X m" | COMPUTED |
| "Prospect is attractive" | INFERRED + WEALTH |
| "Proceed" | JUDGE_REVIEWED |
| "Final decision sealed" | VAULT_SEALED |

---

## 6. End-to-End Trace Flow (Prospect Decision)

```
000_INIT
  → creates session_id + model_governance_card + trace_id

WELL precheck
  → human/machine readiness packet → attach readiness_ref to trace

GEOX ingest
  → evidence_ref: LAS artifact → claim_state: INGESTED

GEOX QC
  → QC_VERIFIED evidence → call_log appended

GEOX candidates
  → computed Vsh / porosity / netpay → claim_state: COMPUTED

GEOX integrity
  → physics check → QC_VERIFIED or VOID

WEALTH EVOI / NPV
  → value witness → analysis_ref appended → claim_state: INFERRED

666_HEART
  → dignity / risk critique → risk_witness appended

888_JUDGE
  → judge_state_hash → claim_state: JUDGE_REVIEWED

010_FORGE
  → action only if judge_state_hash present

999_VAULT
  → vault_entry_id + trace sealed → claim_state: VAULT_SEALED
```

The final Vault payload carries all prior refs — not raw giant outputs.

---

## 7. Final Vault Trace Seal (Black Box Recorder)

```json
{
  "trace_id": "TRACE-20260503-0001",
  "session_id": "SEAL-xxxx",
  "actor_id": "Muhammad Arif bin Fazil",
  "intent": "Evaluate prospect and decide whether to proceed",
  "model_governance_card_hash": "sha256:...",
  "witnesses": {
    "well": {
      "readiness_ref": "WELL-...",
      "verdict": "CAUTION"
    },
    "geox": {
      "evidence_refs": ["GEOX-ART-001", "GEOX-QC-002"],
      "claim_state": "QC_VERIFIED"
    },
    "wealth": {
      "analysis_ref": "WEALTH-EVOI-003",
      "claim_state": "COMPUTED"
    },
    "arifos": {
      "judge_state_hash": "sha256:...",
      "verdict": "SEAL"
    }
  },
  "tool_calls": ["CALL-0001", "CALL-0002", "CALL-0003"],
  "drift_events": [],
  "final_claim_state": "VAULT_SEALED"
}
```

---

## 8. Seal Tests (5 Gates)

### TRACE_STATIC_SEAL
Pass if every result carries: `trace_id`, `session_id`, `actor_id`, `tool name`, `input_hash`, `output_hash`, `claim_state`.

### CROSS_MCP_CONTINUITY_SEAL
Pass if same `trace_id` appears in arifOS + GEOX + WEALTH + WELL outputs.

### NO_ORPHAN_ARTIFACT_SEAL
Pass if:
- Every `artifact_ref` has a parent `trace_id`
- Every `judge_state_hash` has `evidence_refs`
- Every `vault_entry_id` has `judge_state_hash`

### DRIFT_TRACE_SEAL
Pass if: `drift_event` emitted → vault seal → readback → same `trace_id` → `count >= 1`.

### FULL_TRACE_RECONSTRUCTION_SEAL
Pass if: `intent → evidence → computation → critique → judgment → forge/vault` is reconstructable from IDs alone.

---

## 9. No-New-Tools Implementation — Organ Patch Duties

| Existing organ | Trace duty |
|---|---|
| 000_INIT | Create `trace_id` or accept incoming |
| 111_SENSE | Attach observations to trace |
| 222_FETCH | Attach source/evidence refs |
| 333_MIND | Attach reasoning claim state |
| 666_HEART | Attach risk witness |
| 444_KERNEL | Route with trace continuity |
| 888_JUDGE | Produce `judge_state_hash` |
| 010_FORGE | Require judge hash for side effects |
| 999_VAULT | Seal full trace packet |
| 777_OPS | Measure trace completeness % |
| GEOX | Attach evidence/artifact refs |
| WEALTH | Attach value-analysis refs |
| WELL | Attach readiness packet ref |

**One spine. Existing organs. No new tools.**

---

## 10. Forge Directive (OpenCode Agent Prompt)

```
FORGE DIRECTIVE — END-TO-END TRACEABILITY

Mode:
  No new tools.
  No new MCP servers.
  No schema explosion.
  Patch existing payloads only.

Mission:
  Implement a single cross-MCP trace spine across arifOS, GEOX, WEALTH, and WELL.

Required object: trace_packet

Required fields:
  trace_id, parent_trace_id, session_id, epoch_id, actor_id,
  intent, decision_class, reversibility, model_governance_card_hash,
  evidence_refs, tool_calls, artifacts, drift_events,
  judge_state_hash, vault_entry_id, claim_state

Rules:
  1. 000_INIT creates trace_id if absent.
  2. Every tool accepts or propagates trace_id where possible.
  3. Every output includes trace_id.
  4. Every artifact_ref includes trace_id.
  5. Every drift_event includes trace_id.
  6. 888_JUDGE outputs judge_state_hash linked to trace_id.
  7. 010_FORGE refuses side effects unless judge_state_hash exists.
  8. 999_VAULT seals the final trace packet.
  9. 777_OPS reports trace completeness percentage.
  10. No claim may jump claim-state ladder.

Claim-state ladder:
  DECLARED → OBSERVED → INGESTED → QC_VERIFIED → COMPUTED
  → INFERRED → JUDGE_REVIEWED → VAULT_SEALED → VOID

Seal tests:
  TRACE_STATIC_SEAL
  CROSS_MCP_CONTINUITY_SEAL
  NO_ORPHAN_ARTIFACT_SEAL
  DRIFT_TRACE_SEAL
  FULL_TRACE_RECONSTRUCTION_SEAL

Do not deploy until all 5 tests pass.

Final report:
  1. Files changed
  2. Trace fields added
  3. Tools patched
  4. Tests run
  5. Trace reconstruction demo
  6. Remaining gaps
  7. Seal classification

DITEMPA BUKAN DIBERI.
```

---

## Stack Hygiene Law

> **Every tool must either reduce uncertainty, reduce risk, or reduce irreversible error. If not, it is noise.**

---

*Sealed: 2026-05-03T01:18:00+08:00 · Witness: Arif Fazil · Co-architect: arifOS*  
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
