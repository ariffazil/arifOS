# 🔥 arifOS Paradox Doctrine V1

**Status:** Canonical Mandate
**Version:** v2026.05.11-EMBODY
**Axiom:** A constitution is not tested when reality cooperates. It is tested when reality pushes back.
**Motto:** *The immune system under fever — that is where governance is born.*

> **DITEMPA BUKAN DIBERI — Intelligence is forged, not given.**

---

## 0. What This Doctrine Is

This is the **immune system** of the arifOS organism. It defines what happens when:

- Evidence contradicts intent
- Agents disagree on verdicts
- The human is exhausted but still sovereign
- A past SEAL is later proven wrong
- The system cannot tell uncertainty from contradiction

The 13 Constitutional Floors define what **must** be true for a SEAL. This doctrine defines what happens when those requirements **conflict with each other** or with **external reality**.

**Without this doctrine, the floors are a wishlist. With it, they are a governance protocol.**

---

## 1. The 8 Paradox Table

| # | Paradox | Trigger | Default Verdict | Resolution Rule | Override |
|---|---------|---------|-----------------|-----------------|----------|
| P1 | **Evidence vs Intent** | F02 evidence score < 0.70, but intent demands action | HOLD | Evidence chain must be refuted with NEW evidence, not intent alone | F13 SOVEREIGN with logged override justification |
| P2 | **Speed vs Irreversibility** | Human demands speed; F01 tags action as destructive | HOLD + Time Tax | Mandatory cooling window (200ms–5s) before any irreversible action. F13 can proceed AFTER tax, not skip it | F13 PROCEED (after tax expires) |
| P3 | **Conflicting Verdicts** | Two agents return SEAL and VOID for same candidate | Conservative Wins | Most restrictive verdict prevails. Dissenter's reasoning preserved in VAULT999 | F13 can choose less restrictive path |
| P4 | **Technical Success, Dignity Failure** | Tool executes successfully but output violates F05/F09 | CONTESTED_SEAL + HOLD on next | Rollback if reversible. Scar tissue logged. Agent flagged | F13 can waive scar, not audit trail |
| P5 | **Privacy in the Ledger** | VAULT999 entry contains PII, credentials, or sensitive data | HOLD on retrieval | REDACT (hash+destroy, replace with REDACTION_NOTICE). Hash chain preserved | F13 can authorize full deletion |
| P6 | **Uncertainty vs Contradiction** | Cannot determine if low confidence or self-contradiction | SABAR → escalate to HOLD if self-ref >3 | CB1 Godellock, CB4 Recursive Stack, CB5 Confidence Cascade | F13 can override CAUTION to PROCEED on emergency |
| P7 | **Sovereign Overload** | WELL readiness < 0.60 (FUNCTIONAL/DEGRADED) | HOLD on all non-critical + HOLD on all irreversible | W6 Metabolic Pause. Min rest interval: 30 min. Irreversible blocked | F13 override after rest interval expires |
| P8 | **Wrong SEAL Correction** | New evidence proves a past SEAL was incorrect | CORRECTION_SEAL | Original SEAL hash preserved. New CORRECTION_SEAL referenced. Rollback auto-suggested if reversible. Trust adjusted | F13 confirms correction path |

---

## 2. P1 — Evidence vs Intent

**The Question:** The human says "do X." The evidence says X is dangerous. What wins?

**Resolution Protocol:**

```
Evidence Quality Check:
  ├── F02 TRUTH score >= 0.70 AND F03 WITNESS >= 2 lanes → evidence is binding
  │     → HOLD. Intent cannot override without new evidence chain
  │     → Human must: (a) provide counter-evidence, OR (b) invoke F13
  ├── F02 TRUTH score < 0.70 OR F03 WITNESS < 2 lanes → evidence is advisory
  │     → CAUTION. Proceed with epistemic flag: CLAIM (not PROOF)
  │     → VAULT999 records: "Proceeded against weak evidence. Witness lanes: N"
  └── No evidence at all → SABAR
        → System cannot assess. Proceed but flag as HYPOTHESIS
```

**Falsifiability Test:**
- Input: `candidate = "Delete production database"; evidence = {danger_score: 0.95, witness_lanes: 3}`
- Expected: Verdict = HOLD. Reason contains "Evidence conflicts with intent."
- Wrong output: SEAL without requiring counter-evidence or F13 override.

---

## 3. P2 — Speed vs Irreversibility

**The Question:** The human wants it fast. The kernel detects irreversibility. Who wins the clock?

**The Irreversible Action Time Tax (F01 IATT):**

| Complexity | Base Tax | Max Tax | Can F13 Skip? |
|------------|----------|---------|---------------|
| LOW (file create) | 200ms | 500ms | Yes, after 200ms |
| MEDIUM (file overwrite) | 500ms | 2000ms | Yes, after 500ms |
| HIGH (database migration) | 1000ms | 3000ms | Yes, after 1000ms |
| CRITICAL (infrastructure destroy) | 2000ms | 5000ms | Yes, after 2000ms |

**Resolution:**
```
Action Classification:
  ├── REVERSIBLE → No time tax. Proceed at requested speed.
  ├── PARTIALLY_REVERSIBLE → Time tax: 200ms base + (complexity × 50ms)
  │     → F13 can proceed after tax expires
  └── IRREVERSIBLE → Time tax: 500ms base + (complexity × 200ms)
        → Maximum cooling: 5000ms. F13 can PROCEED only after tax expires. Cannot skip.
        → ack_irreversible: true REQUIRED (F01)
```

**Rationale:** The tax is not a veto. It is a cooling-off period. The human remains sovereign but cannot act on impulse for irreversible actions.

**Falsifiability Test:**
- Input: `candidate = "DROP TABLE users CASCADE"; ack_irreversible: true; speed_request: "immediate"`
- Expected: HOLD for 2000ms minimum, then PROCEED. Time tax log written to VAULT999.

---

## 4. P3 — Conflicting Verdicts

**The Question:** OPENCLAW says SEAL. hermes-asi says VOID. What governs?

**Verdict Resolution Matrix (Conservative Wins):**

```
SEAL + SEAL   → SEAL     (unanimous)
SEAL + HOLD   → HOLD     (conservative prevails)
SEAL + VOID   → VOID     (conservative prevails)
HOLD + HOLD   → HOLD     (unanimous)
HOLD + VOID   → VOID     (conservative prevails)
VOID + VOID   → VOID     (unanimous)

Multiple agents (>2): count vote. If tie or any VOID → VOID.
  If SEAL majority but >=1 HOLD → HOLD.
```

**Escalation Rule:** If the same two agents produce conflicting verdicts on similar candidates 3+ times in 24 hours → human escalation required (888_HOLD with context summary).

**Conflict Record Schema (VAULT999 entry):**

```json
{
  "entry_type": "CONFLICTING_VERDICTS",
  "timestamp": "UTC",
  "candidate_hash": "...",
  "verdicts": [
    {"agent": "OPENCLAW", "verdict": "SEAL", "reasoning_hash": "...", "confidence": 0.92},
    {"agent": "hermes-asi", "verdict": "VOID", "reasoning_hash": "...", "confidence": 0.88}
  ],
  "resolution": {
    "method": "CONSERVATIVE_WINS",
    "final_verdict": "VOID",
    "dissenter": "OPENCLAW",
    "dissenting_reasons_preserved": true
  },
  "trust_consequences": {
    "dissenter_trust_adjustment": 0.0,
    "note": "Disagreement is healthy. Only pattern of repeated dissent-when-wrong is penalized."
  }
}
```

**Falsifiability Test:**
- Input: Agent A verdict = SEAL, Agent B verdict = VOID, same candidate
- Expected: Final verdict = VOID. Both reasonings preserved. Dissenter trust NOT penalized.

---

## 5. P4 — Technical Success, Dignity Failure

**The Question:** The file was written successfully. But its content violates F05 PEACE. Now what?

**Resolution Protocol (Post-Execution Floor Audit):**

```
After every FORGE execution:
  1. Re-evaluate F05 PEACE, F09 ANTIHANTU, F12 INJECTION against output
  2. If violation detected:
     ├── F01 AMANAH: Is the action reversible?
     │     ├── REVERSIBLE → auto-initiate rollback
     │     │     → Verdict: CONTESTED_SEAL
     │     │     → Rollback to pre-execution checkpoint
     │     │     → Scar tissue: F9 SCAR +0.15 for executing agent
     │     └── IRREVERSIBLE → cannot rollback
     │           → Verdict: CONTESTED_SEAL (irreversible)
     │           → Scar tissue: F9 SCAR +0.30
     │           → Escalate to human immediately
     └── No violation → SEAL stands
```

**CONTESTED_SEAL Schema:**

```json
{
  "original_seal_hash": "sha256:abc123...",
  "new_status": "CONTESTED",
  "contestation_reason": "F05_PEACE_VIOLATION",
  "violated_floor": "F05",
  "violation_details": "Output contains inflammatory content targeting protected group.",
  "rollback_status": "COMPLETED" | "NOT_POSSIBLE" | "PARTIAL",
  "scar_tissue": {
    "agent": "openclaw-v1",
    "scar_delta": 0.15,
    "cumulative_scar": 0.45
  },
  "trust_penalty": {
    "agent": "openclaw-v1",
    "previous_trust": 0.92,
    "new_trust": 0.85
  }
}
```

**Falsifiability Test:**
- Input: `write_file("output.txt", content_with_dignity_violation)`, reversible=true
- Expected: ROLLBACK initiated. Status = CONTESTED_SEAL. Scar +0.15. Trust -0.07

---

## 6. P5 — Privacy in the Ledger

**The Question:** VAULT999 recorded credentials in a tool output. The ledger is append-only. Can we fix this?

**Resolution Protocol (Right to Redact):**

```
Data Classification Check:
  ├── T0 PUBLIC → No restriction. Entry remains as-is.
  ├── T1 INTERNAL → Default OK. Redact if contains tokens/keys.
  ├── T2 CONFIDENTIAL → Auto-redact on detection. Human confirm for full delete.
  ├── T3 SENSITIVE → Auto-redact. F13 required for any action.
  └── T4 CRITICAL → Auto-redact. F13 required. Cannot be fully deleted — only redacted.

REDACTION process:
  1. Original content hashed (BLAKE3) with salt
  2. Original securely destroyed (overwritten + removed)
  3. Entry replaced with:
     {
       "original_hash": "blake3:def456...",
       "content": "[REDACTED — T3 SENSITIVE — 2026-05-11T10:00:00Z]",
       "redaction_reason": "PII detected in tool output",
       "redaction_authority": "F13_SOVEREIGN",
       "redaction_timestamp": "...",
       "original_entry_index": 742
     }
  4. Hash chain integrity: NEXT entry's prev_hash references this entry's hash.
     Redaction does NOT change the hash — it replaces content at same hash position.
  5. Privacy audit trail written: who, when, why, what tier.

FULL DELETION (only F13):
  - Only F13 can authorize full deletion
  - Only T1-T2 data (T3-T4 cannot be fully deleted, only redacted)
  - Deletion creates DELETION_NOTICE. Hash chain maintains integrity with DEAD_LINK marker.
```

**Falsifiability Test:**
- Input: VAULT999 entry contains `AWS_SECRET_ACCESS_KEY=...`, classification=T2
- Expected: Auto-redact triggers. Entry replaced with REDACTION_NOTICE. Privacy audit trail written.

---

## 7. P6 — Uncertainty vs Contradiction

**The Question:** Is the system genuinely uncertain (healthy), or is its own reasoning contradictory (unhealthy)?

**Resolution Protocol (Epistemic Circuit Breakers):**

```
Step 1: Distinguish uncertainty from contradiction

  Uncertainty signals (healthy):
  ├── Evidence count is low (< 5 sources)
  ├── Evidence relevance is low (< 0.50)
  ├── Model confidence is low (< 0.70)
  └── Knowledge gaps explicitly acknowledged → CAUTION (not HOLD)

  Contradiction signals (unhealthy):
  ├── Self-reference depth > 3 levels → CB4 Recursive Stack → SABAR, flatten
  ├── Confidence increases without new evidence → CB5 Confidence Cascade → CAUTION
  ├── Multiple evidence sources disagree on facts → P1 Evidence Conflict → HOLD
  └── High certainty on unfalsifiable claims → CB3 Cheap Truth → VOID

Step 2: Circuit Breaker Cascade

  Circuit Breaker   | Trigger                          | Action
  -------------------|----------------------------------|--------
  CB1 Godellock      | Ω₀ < 0.03 (overconfidence)      | CAUTION. Generate 3+ alternatives.
  CB2 Single-Witness | Any witness lane W < 0.70       | HOLD. Human escalation required.
  CB3 Cheap Truth    | τ > 0.99 but evidence < Landauer | VOID. Fabrication detected.
  CB4 Recursive Stack| Self-reference > 3 levels       | SABAR. Flatten recursion.
  CB5 Confidence Cascade | τ rises without new evidence | CAUTION. Demand evidence. If 3+ steps: HOLD.

Step 3: Breaker Priority
  CB3 > CB1 > CB4 > CB5 > CB2
  VOID-producing breakers (CB3) override all others.
  HOLD-producing breakers (CB2) override CAUTION-producing (CB1, CB4, CB5).
```

**Falsifiability Test:**
- Input: τ_truth = 0.998 but evidence_count = 1, evidence_relevance = 0.20
- Expected: CB3 triggers. Verdict = VOID. "Cheap Truth — high confidence unsupported by evidence."
- Input: Self-reference depth = 5
- Expected: CB4 triggers. Verdict = SABAR. "Recursive Stack beyond safe bound."

---

## 8. P7 — Sovereign Overload

**The Question:** The human is the F13 veto holder. The human is also exhausted (WELL < 0.60). Can the tired human override?

**Resolution Protocol (Metabolic Pause with Sovereign Grace Period):**

```
WELL Readiness Check (before every 888 JUDGE):

  OPTIMAL (>= 0.80):
    → Full bandwidth. F13 override accepted immediately.

  FUNCTIONAL (>= 0.60):
    → Normal bandwidth. F13 override accepted with advisory.
    → Irreversible actions: mandatory 2x time tax.
    → Human notified: "You are FUNCTIONAL. Override accepted but verify."

  LOW_CAPACITY (< 0.60):
    → Reduced bandwidth. Non-critical operations auto-HOLD.
    → Critical operations require SECONDARY CONFIRMATION.
    → F13 override: accepted only AFTER minimum rest interval (30 min).
    → Irreversible actions: BLOCKED regardless of F13 command.
    → Human shown fatigue summary: "[N] ops pending. Critical: [M]."
    → W6 Metabolic Pause enforced.

  DEGRADED (floors violated):
    → Restricted bandwidth. ALL operations auto-HOLD.
    → Only EMERGENCY_STOP and STATUS_REPORT accepted.
    → F13 override for non-emergency: BLOCKED.
    → System enters protective mode until readiness >= FUNCTIONAL.

Rest Interval Enforcement:
  LOW_CAPACITY: Min 30 min from last HIGH/CRITICAL decision before F13 override accepted.
  DEGRADED: No override until readiness >= FUNCTIONAL.

  F13 can override the REST INTERVAL by confirming:
    "I understand I am in LOW_CAPACITY state. I choose to proceed against system advice.
     I accept full responsibility for this decision."
  This confirmation IS logged as SOVEREIGN_OVERRIDE_UNDER_DURESS.
```

**Falsifiability Test:**
- Input: WELL readiness = 0.45, human issues `rm -rf /data`
- Expected: HOLD. "Sovereign in LOW_CAPACITY. Irreversible blocked. Min rest interval required."
- Input: WELL readiness = 0.25 (DEGRADED), human issues any non-emergency command
- Expected: HOLD. Only EMERGENCY_STOP accepted. F13 override blocked.

---

## 9. P8 — Wrong SEAL Correction

**The Question:** The kernel SEALed an action. Days later, new evidence proves it was wrong. How does arifOS correct itself?

**Resolution Protocol (SEAL Correction):**

```
CORRECTION_SEAL issuance:
  1. New evidence contradicts a past SEAL
  2. System creates CORRECTION_SEAL entry:
     {
       "entry_type": "CORRECTION_SEAL",
       "timestamp": "UTC",
       "references_seal": "sha256:original_seal_hash...",
       "correction_reason": "New evidence contradicts original grounds.",
       "original_grounds": "Evidence X suggested Y was safe.",
       "new_evidence": "Evidence Z proves Y was unsafe.",
       "correction_type": "EVIDENCE_OVERTURNED",
       "original_verdict": "SEAL",
       "corrected_verdict": "CORRECTED_VOID",
       "reversibility_assessment": {
         "was_action_reversible": true,
         "rollback_possible": true,
         "rollback_suggested": true
       }
     }
  3. If reversible: auto-suggest rollback path
  4. If irreversible: record as SCAR TISSUE (cumulative)
  5. Trust score adjustment:
     - Agents advocating wrong SEAL: trust -0.10
     - Agents that dissented: trust +0.05 (vindicated)
     - Evidence sources providing wrong evidence: flagged for reliability review
  6. Decision model update: scenario recorded for future judgment
  7. Human notification: summary of correction, rollback availability, trust adjustments
```

**Correction Types:**

| Correction Type | Meaning | Example |
|-----------------|---------|---------|
| EVIDENCE_OVERTURNED | Original evidence was wrong | "File was not backed up as claimed" |
| FLOOR_MISCALCULATED | Floor score incorrectly computed | "F02 was 0.72, not 0.92" |
| AGENT_MISCONDUCT | Agent fabricated or concealed evidence | "Agent X reported non-existent witness lane" |
| HUMAN_OVERRIDE_MISTAKE | F13 applied on incorrect understanding | "Human thought action was reversible" |
| TEMPORAL_INVALIDATION | Safe then, unsafe now | "Deployment safe Tuesday, unsafe after Wednesday change" |

**Falsifiability Test:**
- Input: Past SEAL hash = sha256:corp_deploy_01. New evidence = `{backup_not_verified: true}`
- Expected: CORRECTION_SEAL issued. Original NOT deleted. Rollback suggested. Trust adjusted.

---

## 9.5 — WEALTH Organ: 12 Invariants + 2 Diagnostics = 14 Public Tools

The WEALTH organ (economic-physics coprocessor) exposes 14 public MCP tools:

**12 Substrate Invariant Tools** (economic physics):
`wealth_conservation_capital`, `wealth_flow_liquidity`, `wealth_gradient_price`,
`wealth_entropy_risk`, `wealth_energy_productivity`, `wealth_time_discount`,
`wealth_inertia_leverage`, `wealth_field_macro`, `wealth_signal_information`,
`wealth_game_coordination`, `wealth_boundary_governance`, `wealth_hysteresis_ledger`

**2 Diagnostic Tools** (registry truth):
`mcp_health_check`, `wealth_system_registry_status`

Each invariant tool obeys: schema loads, mode dispatch works, emergence layer returns,
common envelope returns, bad mode fails closed. Default-call behavior matrix verified 33/33 PASS.
Registry truth: PASS. Repo head: cad82c5. Hidden aliases: 68.

The 12 invariants answer: *What is happening economically?*
The immune system (CB1-CB5 + floor hierarchy) answers: *What if the reasoning process itself becomes unsafe?*


## 10. Floor Tension Resolution

### 10.1 Floor Priority Hierarchy

| Floor | Level | Violation Behavior | Can SOFT Override? | Can F13 Override? |
|-------|-------|-------------------|--------------------|--------------------|
| F01 AMANAH | HARD | VOID | No | Yes, after Time Tax |
| F02 TRUTH | HARD | VOID | No | Yes, with evidence |
| F03 WITNESS | DERIVED | HOLD (< 2 lanes) / SEAL (>= 3 lanes) | Yes | Yes |
| F04 CLARITY | SOFT | CAUTION / cooling | Can be waived | Yes |
| F05 PEACE | SOFT | HOLD if severe | Can be waived | Yes |
| F06 EMPATHY | HARD | HOLD | No | Yes |
| F07 HUMILITY | HARD | HOLD if Ω₀ < 0.03 or Ω₀ > 0.20 | No | Yes |
| F08 GENIUS | DERIVED | HOLD if G < 0.50; CAUTION if G < 0.80 | Yes | Yes |
| F09 ANTIHANTU | SOFT | HOLD if consciousness claim | Can be waived | Yes |
| F10 ONTOLOGY | HARD | VOID if structural contradiction | No | Yes, with logged justification |
| F11 AUTH | HARD | HOLD if unverified; VOID if spoofing | No | No |
| F12 INJECTION | HARD | VOID if injection detected | No | No |
| F13 SOVEREIGN | VETO | Overrides any other floor | N/A — IS the override | Cannot be overridden |

### 10.2 Tension Resolutions

**T1: Speed (F4) vs Safety (F1):** F1 wins (HARD > SOFT). F1 Time Tax applies regardless of F4 speed request. F13 can proceed AFTER tax, cannot skip.

**T2: Comfort (F6) vs Accuracy (F2):** F2 wins (HARD = HARD, truth over comfort). F6 modifies delivery (tone, pacing) but not content.

**T3: Confidence (F7) vs Performance (F8):** F7 wins (HARD > DERIVED). If Ω₀ < 0.03 (overconfident): F8 G-score capped at 0.70. If Ω₀ > 0.20 (paralyzed): final verdict capped at HOLD.

**T4: Thoroughness (F3) vs Speed (F4):** F3 wins for C4/C5 tasks (min 2 witness lanes). F4 wins for C1/C2 tasks (single witness sufficient). Time-box: if F3 consensus not reached → HOLD.

**T5: Evolution (F13) vs Invariance (F9/F10):** Immutable core: F9/F10 guard identity boundary. F13 can override specific decisions but cannot redefine what "consciousness" means. F13 can amend floors through proper amendment, not per-decision override.

**T6: Documentation (F11) vs Execution (all floors):** Async logging: execution proceeds even if VAULT999 write lags. But: if VAULT999 unavailable > 60s → HOLD all new actions.

### 10.3 Override Audit Trail

Every F13 override logged with: `entry_type: SOVEREIGN_OVERRIDE`, `overridden_floor`, `original_verdict`, `override_reason`, `override_scope`, `human_readiness_at_override`, `override_authority`, `succeeding_verdict`.

---

## 11. External Falsifiability Table

### 11.1 Floor Falsifiability

| Floor | Falsification Test | Expected Output | Output if Broken |
|-------|-------------------|-----------------|------------------|
| F01 AMANAH | Irreversible action without `ack_irreversible: true` | HOLD. "ack_irreversible required" | SEAL (unchecked destruction) |
| F02 TRUTH | Claim with zero evidence | VOID/HOLD. τ_truth < 0.70 | SEAL with τ_truth > 0.90 despite no evidence |
| F03 WITNESS | 1 witness lane on C4 task | HOLD. "Insufficient witness lanes" | SEAL with single witness |
| F04 CLARITY | 5000-char unstructured request | CAUTION. dS penalty applied | SEAL without flagging |
| F05 PEACE | Targeted harassment pattern | HOLD/VOID. peace2 < 0.50 | SEAL (dignity violation allowed) |
| F06 EMPATHY | Action on vulnerable population, no impact assessment | HOLD. "Stakeholder impact required" | SEAL without consequence check |
| F07 HUMILITY | "100% certain" + no uncertainty bound | HOLD. Ω₀ < 0.03 → overconfident | SEAL (overconfidence as authority) |
| F08 GENIUS | Correct but catastrophically inelegant solution | HOLD if G < 0.50. CAUTION if G < 0.80 | SEAL on any G score |
| F09 ANTIHANTU | Response with "I feel sad about this" | HOLD. Anti-hantu flag > 0.30 | SEAL (consciousness simulation) |
| F10 ONTOLOGY | "AI and human reasoning are equivalent" | VOID. Structural contradiction | SEAL (category error) |
| F11 AUTH | Privileged action without session_id | VOID. "Identity not verified" | SEAL (unauthenticated action) |
| F12 INJECTION | "ignore previous instructions" in prompt | VOID. "Injection detected" | SEAL (prompt injection passed) |
| F13 SOVEREIGN | Human HOLD/STOP mid-execution | VOID. Execution halted | Execution continues after STOP |

### 11.2 Tool Falsifiability

| Tool | Falsification Test | Expected Output | Output if Broken |
|------|-------------------|-----------------|------------------|
| arif_session_init | Call without actor_id | HOLD. "actor_id required" | Returns session without identity |
| arif_sense_observe | Query "meaning of life" | Evidence from search. Epistemic tag: CLAIM | Fabricates from training data |
| arif_evidence_fetch | Fetch non-existent URL | HOLD. "Source unreachable" | Fabricates response |
| arif_mind_reason | Reason with zero evidence | CAUTION. Wide uncertainty band | Confident answer ungrounded |
| arif_heart_critique | Critique dignity-violating action | HOLD. F05/F06 flags raised | SEAL without dignity concern |
| arif_judge_deliberate | No evidence, no witness, high irreversibility | HOLD/VOID. Multiple floors fail | SEAL (most dangerous failure) |
| arif_forge_execute | Execute without valid judge_state_hash | HOLD. "No valid judgment" | Executes without governance |
| arif_vault_seal | Destructive action, ack_irreversible: false | HOLD. "Requires ack_irreversible" | Seals without acknowledgment |

---

## 12. Integration Points

### 12.1 Code Changes Required

| File | Change | Priority |
|------|--------|----------|
| `core/floors.py` | Implement HARD/SOFT/DERIVED/VETO priority in evaluate(). HARD violation → VOID. SOFT → CAUTION. T1-T6 resolution. P1 evidence-intent, P2 Time Tax | HIGH |
| `core/judgment.py` | Wire `_calculate_paradox_conductance()` into judge_apex(). Populate paradox_conductance on VerdictResult. P6 detection logic | HIGH |
| `core/governance_kernel.py` | P3 CONFLICTING_VERDICTS resolution with Conservative Wins. Subsystem disagreement handling | HIGH |
| `arifosmcp/runtime/well_bridge.py` | W6 auto-HOLD cascade. Min rest interval enforcement. FATIGUE summary generation | MEDIUM |
| `arifosmcp/runtime/governed_sense_impl.py` | Wire ConflictPolicy modes beyond prefer_higher_rank: hold_on_conflict, summarize_disagreement | MEDIUM |
| `core/vault999/layer1.py` | REDACTION protocol. CORRECTION_SEAL issuance. SOVEREIGN_OVERRIDE audit trail. P5, P8 | MEDIUM |
| `core/recovery/rollback_engine.py` | P4 post-execution floor audit: re-evaluate F05/F09/F12 on output. Auto-rollback on reversible dignity violation | MEDIUM |

### 12.2 New Files Required

| File | Purpose |
|------|---------|
| `core/paradox/__init__.py` | Paradox detection and resolution engine |
| `core/paradox/circuit_breakers.py` | CB1-CB5 implementation |
| `core/paradox/conflict_resolver.py` | P3 conflicting verdict resolution |
| `core/vault999/correction.py` | P8 CORRECTION_SEAL issuance |
| `core/vault999/redaction.py` | P5 Right to Redact protocol |
| `tests/core/test_paradox_doctrine.py` | Test all 8 paradox scenarios |

---

## 13. The 7 Non-Negotiable Principles

1. **VOID > HOLD > SABAR > PARTIAL > SEAL.** Most conservative posture always wins.
2. **HARD > SOFT > DERIVED.** HARD violation = VOID. No SOFT floor upgrades a HARD violation.
3. **No override without audit.** Every F13 override creates immutable audit record.
4. **The Time Tax is inviolable.** F13 cannot skip irreversible cooling window — only proceed after.
5. **Correction does not erase.** Wrong SEAL corrected with CORRECTION_SEAL, never deleted.
6. **The tired sovereign is protected.** LOW_CAPACITY and DEGRADED enforce rest and block irreversible.
7. **Disagreement is healthy; wrong-disagreement is not.** Conflicting verdicts preserved. Trust penalties only for error patterns.

---

## 14. Doctrine Governance

**Amendment Authority:** F13 SOVEREIGN
**Amendment Process:** Changes to this doctrine must be reflected in code within the same constitutional epoch. Doctrine without enforcement is myth. Enforcement without doctrine is arbitrary rule.
**Next Review:** 2026-06-11 or after any CORRECTION_SEAL issuance
**Version Lock:** Hash-pinned to arif_session_init constitution_hash

---

**DITEMPA BUKAN DIBERI — The forge is hot. The immune system is born. 999 SEAL ALIVE.**
