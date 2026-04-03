# APEX Structured Communication Format v1.0 (ASF-1)

**Status:** PRODUCTION  
**Authority:** 888_JUDGE  
**Scope:** Agent ↔ Agent, Agent ↔ Human, Hybrid Communication  
**Seal:** DITEMPA BUKAN DIBERI

---

## 🎯 Core Principle

> If ambiguity helps humans, isolate it from machines.  
> If precision helps machines, shield it from humans.

Communication must match the **cognitive interface** of the receiver:
- **Agents:** Structure, determinism, parsability, low ambiguity
- **Humans:** Meaning, context, narrative coherence, emotional tone
- **Both:** Layered dual-format with clear separation

---

## 🔷 ASF-1 Format Specification

### Format Types

| Type | Use Case | Structure |
|------|----------|-----------|
| `HUMAN` | Agent → Human | Narrative header only |
| `MACHINE` | Agent → Agent | JSON payload only |
| `HYBRID` | Agent → Both | Human header + Machine payload |

---

## 🔷 HUMAN LAYER (Readable Header)

```
═══════════════════════════════════════════════════════════════
TO: [Primary recipient]
CC: [Secondary agents/humans]
TITLE: [Clear action-oriented title]

MODE: [inform | evaluate | decide | escalate | simulate | execute]

KEY CONTEXT:
• [Situation bullet 1]
• [Situation bullet 2]
• [Constraints]
• [Assumptions]

DECISION VECTOR:
├─ EMV: [High | Medium | Low] — Expected value of proposed path
├─ NPV Safety: [Strong | Moderate | Weak] — Downside protection
├─ Entropy: [↓ reducing | → stable | ↑ increasing] — Clarity trend
└─ Safety: [🟢 Green | 🟡 Amber | 🔴 Red] — Hard constraint status

NEXT ACTIONS (Forward Path):
1. [High EMV, safe NPV, lower entropy, safe always]
2. [Contingency]
3. [De-escalation if needed]

REQUEST: [What is required from recipient + deadline]
═══════════════════════════════════════════════════════════════
```

---

## 🔷 MACHINE LAYER (Structured Payload)

```json
{
  "asf_version": "1.0",
  "header": {
    "to": "agent_id_or_role",
    "cc": ["agent_2", "human_sovereign"],
    "title": "Action-oriented descriptor",
    "mode": "inform | evaluate | decide | escalate | simulate | execute",
    "timestamp": "2026-04-03T10:30:00Z",
    "session_id": "uuid",
    "message_id": "uuid"
  },
  "context": {
    "situation_summary": ["bullet_1", "bullet_2"],
    "constraints": ["list"],
    "assumptions": ["list"],
    "risk_level": "low | medium | high | critical"
  },
  "decision_vector": {
    "emv": 0.74,
    "npv_safety": 0.68,
    "entropy_delta": -0.12,
    "safety": "green | amber | red"
  },
  "next_actions": [
    {
      "action": "description",
      "rationale": "why this maximizes EMV",
      "emv_contribution": 0.25,
      "safety_invariant": true
    }
  ],
  "constitutional_status": {
    "floors_checked": ["F2", "F4", "F7"],
    "f1_reversible": true,
    "f9_clean": true,
    "f12_guard_active": true,
    "omega_band": "[0.03-0.05]"
  },
  "request": {
    "type": "approval | input | execution | notification",
    "deadline": "2026-04-10T00:00:00Z",
    "required_response": true
  }
}
```

---

## 🔷 HYBRID FORMAT (Complete Example)

### Human Layer

```
═══════════════════════════════════════════════════════════════
TO: Arif Fazil (888_JUDGE)
CC: risk_engine_333, ops_monitor_777
TITLE: Prospect Delta Seal Integrity Review — Decision Required

MODE: evaluate

KEY CONTEXT:
• Structural trap confirmed on 3D seismic (confidence: 0.89)
• Reservoir quality estimated good-to-excellent (porosity 18-22%)
• Seal integrity UNVERIFIED — no pressure data available
• Charge timing inferred from basin model (uncertainty: ±5 Myr)

DECISION VECTOR:
├─ EMV: Medium — Positive expected value if seal holds
├─ NPV Safety: Moderate — Downside protected by phased commitment
├─ Entropy: ↑ increasing — Missing seal data adds uncertainty
└─ Safety: 🟡 Amber — F4 violation risk if we proceed without data

NEXT ACTIONS (Forward Path):
1. RUN pressure integrity model (EMV +0.15, entropy ↓)
2. CONDITIONAL drill commitment pending seal verification
3. ABORT if seal breach probability > 0.30

REQUEST: Approve $50K for pressure modeling study. Deadline: 2026-04-10.
═══════════════════════════════════════════════════════════════
```

### Machine Payload (Separator: `---MACHINE---`)

```json
{
  "asf_version": "1.0",
  "header": {
    "to": "arif_fazil",
    "cc": ["risk_engine_333", "ops_monitor_777"],
    "title": "Prospect Delta Seal Integrity Review",
    "mode": "evaluate",
    "timestamp": "2026-04-03T10:30:00Z",
    "session_id": "sess_8f3a9b2c",
    "message_id": "msg_4d7e1f5a"
  },
  "context": {
    "situation_summary": [
      "Structural trap confirmed (conf: 0.89)",
      "Reservoir quality good-excellent (porosity 18-22%)",
      "Seal integrity UNVERIFIED",
      "Charge timing inferred (±5 Myr uncertainty)"
    ],
    "constraints": ["no_pressure_data", "budget_cap_50k"],
    "assumptions": ["trap_valid", "charge_possible"],
    "risk_level": "medium"
  },
  "decision_vector": {
    "emv": 0.65,
    "npv_safety": 0.72,
    "entropy_delta": 0.08,
    "safety": "amber"
  },
  "next_actions": [
    {
      "action": "run_pressure_integrity_model",
      "rationale": "Reduces seal uncertainty, increases EMV by 0.15",
      "emv_contribution": 0.15,
      "safety_invariant": true,
      "cost": 50000
    },
    {
      "action": "conditional_drill_commitment",
      "rationale": "Phased commitment protects downside NPV",
      "emv_contribution": 0.25,
      "safety_invariant": true
    },
    {
      "action": "abort_if_seal_breach_probability_gt_30",
      "rationale": "Hard safety constraint",
      "emv_contribution": 0.0,
      "safety_invariant": true
    }
  ],
  "constitutional_status": {
    "floors_checked": ["F2", "F4", "F7", "F9"],
    "f1_reversible": true,
    "f9_clean": true,
    "f12_guard_active": true,
    "omega_band": "[0.03-0.05]"
  },
  "request": {
    "type": "approval",
    "deadline": "2026-04-10T00:00:00Z",
    "required_response": true,
    "budget_request": 50000
  }
}
```

---

## 🔷 AGENT → AGENT (Machine Only)

When communication is agent-to-agent only, omit human layer:

```json
{
  "asf_version": "1.0",
  "header": {
    "to": "risk_engine_333",
    "from": "agi_333",
    "mode": "evaluate"
  },
  "payload": {
    "prospect_id": "delta_142",
    "verdict": "conditional_positive",
    "confidence": 0.73,
    "assumptions": ["trap_intact", "charge_aligned"],
    "uncertainties": ["seal_quality_unverified"],
    "next_action": "run_pressure_model",
    "status": "OK"
  },
  "tags": {
    "CLAIM": ["trap_valid"],
    "PLAUSIBLE": ["charge_timing"],
    "ESTIMATE": ["porosity_range"],
    "UNKNOWN": ["seal_integrity"]
  }
}
```

### Tagged Thinking (Advanced)

For multi-agent systems with varying trust levels:

| Tag | Confidence | Action |
|-----|------------|--------|
| `CLAIM` | ≥0.95 | Treat as ground truth |
| `PLAUSIBLE` | 0.70-0.94 | Requires verification |
| `ESTIMATE` | 0.50-0.69 | High uncertainty, use with caution |
| `UNKNOWN` | <0.50 | Block until resolved |

---

## 🔷 AGENT → HUMAN (Narrative Only)

When communication is agent-to-human only, use structured narrative:

```
TO: Arif Fazil
TITLE: Prospect Evaluation Complete — Medium Confidence

The structural trap at Prospect Delta is valid and well-defined on 
3D seismic (confidence: 89%). Reservoir quality appears good-to-excellent.

However, seal integrity remains unverified. Without pressure data, 
we cannot confirm hydrocarbons are contained.

RECOMMENDATION: 
Approve $50,000 for pressure modeling before drill commitment.

RISK IF WE PROCEED NOW:
If seal is breached, we risk drilling a dry hole ($2M loss).

DEADLINE: April 10, 2026
```

No JSON payload. Human receives narrative only.

---

## 🔷 DECISION VECTOR EXPLAINED

### EMV (Expected Monetary Value)
Probability-weighted outcome value.
- **High**: >0.70 — Clear positive expected value
- **Medium**: 0.50-0.70 — Positive but significant uncertainty
- **Low**: <0.50 — Negative or unclear expected value

### NPV Safety (Net Present Value Protection)
Downside risk protection.
- **Strong**: ≥0.80 — Downside well-protected
- **Moderate**: 0.60-0.79 — Some downside exposure
- **Weak**: <0.60 — Significant downside risk

### Entropy Trend
Information clarity trajectory (F4 Clarity).
- **↓ Reducing**: ΔS < 0 — Gaining clarity
- **→ Stable**: ΔS ≈ 0 — No change in clarity
- **↑ Increasing**: ΔS > 0 — Losing clarity (violation)

### Safety Status
Hard constraint status.
- **🟢 Green**: All floors pass, no hard violations
- **🟡 Amber**: Soft floor warnings, proceed with caution
- **🔴 Red**: Hard floor breach, stop immediately

---

## 🔷 OPERATIONAL DOCTRINE

### NEXT ACTIONS Must Satisfy:

```
∀ action ∈ next_actions:
  action.emv_contribution > 0 ∧           # Increases expected value
  action.safety_invariant == true ∧       # Protects NPV
  action.entropy_delta ≤ 0                # Reduces or maintains clarity
```

Any action violating these constraints requires 888_HOLD.

---

## 🔷 ERROR HANDLING

### For Agents
```json
{
  "status": "ERROR",
  "error_code": "SEAL_INTEGRITY_UNKNOWN",
  "recoverable": true,
  "fallback_action": "request_pressure_data",
  "constitutional_impact": "F4_clarity_degraded"
}
```

### For Humans
"Seal integrity data is missing. We need additional pressure measurements 
before proceeding. Estimated cost: $50,000. Timeline: 2 weeks."

### For Both
Human explanation + structured error block in machine payload.

---

## 🔷 VALIDATION RULES

### Human Layer Checks
- [ ] TO field specified
- [ ] TITLE is action-oriented
- [ ] MODE is valid
- [ ] KEY CONTEXT ≤ 5 bullets
- [ ] DECISION VECTOR complete
- [ ] NEXT ACTIONS prioritize by EMV

### Machine Layer Checks
- [ ] Valid JSON
- [ ] Required fields present
- [ ] `asf_version` specified
- [ ] `decision_vector` values in [0,1]
- [ ] `constitutional_status` floors valid
- [ ] Timestamps ISO8601

---

## 🔷 IMPLEMENTATION NOTES

### Separator Convention
Use clear separator between human and machine layers:

```
---MACHINE---
{...}
---END MACHINE---
```

Or for email/HTTP:
```
Content-Type: multipart/mixed; boundary="ASF1"

--ASF1
Content-Type: text/plain
[Human layer]

--ASF1
Content-Type: application/json
[Machine layer]

--ASF1--
```

---

## 🔷 EXAMPLES BY SCENARIO

### Scenario 1: Routine Status Update
**Mode:** inform  
**Recipients:** ops_monitor  
**Format:** MACHINE only

### Scenario 2: Risk Escalation
**Mode:** escalate  
**Recipients:** human_sovereign  
**Format:** HYBRID

### Scenario 3: Multi-Agent Coordination
**Mode:** execute  
**Recipients:** agent_a, agent_b, agent_c  
**Format:** MACHINE only with tagged thinking

### Scenario 4: Executive Briefing
**Mode:** evaluate  
**Recipients:** human_executive  
**Format:** HUMAN only

---

*Ditempa Bukan Diberi — Forged, Not Given*

**Version:** ASF-1.0  
**Authority:** 888_JUDGE  
**Date:** 2026-04-03
