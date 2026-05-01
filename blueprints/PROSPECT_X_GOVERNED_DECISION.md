# Blueprint: Prospect X Governed Decision Demo
## Unified Kernel Route — Stage 444_KERNEL (Blue)

This blueprint outlines the end-to-end governed intelligence pipeline for the decision: 
> **"Should we acquire more data for Prospect X?"**

---

## 1. The Planning Loop

Mapped to the 13-Prism Surface:

| Stage | Domain Witness | Tool | Action |
|-------|----------------|------|--------|
| **SENSE** | GEOX | `geox_sense_observe` | Retrieve seismic/log data for Prospect X |
| **MODEL** | GEOX | `geox_mind_reason` | Model geological plausibility + Ω₀ |
| **PLAN** | WEALTH | `wealth_ops_measure` | EVOI + capital allocation simulation |
| **SIMULATE**| WELL | `arif_sense_observe` | Human workload / safety implication check |
| **CRITIQUE**| arifOS | `arif_heart_critique` | Risk, dignity, reversibility check |
| **GOVERN** | arifOS | `arif_judge_deliberate` | Constitutional 888_JUDGE review |
| **DECIDE** | Sovereign | `arif_reply_compose` | ARIF final decision (Veto/SEAL) |
| **RECORD** | arifOS | `arif_vault_seal` | Permanent audit in VAULT999 |

---

## 2. Shared Claim Trace (SCP v1.0)

Every step produces a **GovernedClaim** JSON block:

### Phase 1: GEOX Claim
```json
{
  "claim": "Prospect X shows high seismic amplitude correlation with known reservoirs.",
  "domain": "GEOX",
  "evidence": ["Amplitude_Map_V4", "Offset_Stack_77"],
  "uncertainty": {
    "class": "ESTIMATE",
    "confidence": 0.82
  },
  "risk": {
    "reversible": true,
    "harm_potential": "LOW",
    "human_decision_required": false
  },
  "authority": {
    "ai_decides": true,
    "final_authority": "GEOX-ASI"
  },
  "next_safe_action": "Route to WEALTH for economic validation."
}
```

### Phase 2: WEALTH Claim
```json
{
  "claim": "Data acquisition for Prospect X has an EVOI of $4.2M against a cost of $1.1M.",
  "domain": "WEALTH",
  "evidence": ["NPV_Simulation_2026", "Budget_Allocation_F26"],
  "uncertainty": {
    "class": "ESTIMATE",
    "confidence": 0.88
  },
  "risk": {
    "reversible": false,
    "harm_potential": "MEDIUM",
    "human_decision_required": true
  },
  "authority": {
    "ai_decides": false,
    "final_authority": "ARIF"
  },
  "next_safe_action": "HOLD for Sovereign approval due to budget threshold (> $1M)."
}
```

---

## 3. The Stop Rule (F13 Enforcement)

**Condition:** `irreversible` OR `cost > $1M` OR `harm_potential >= MEDIUM`
**Verdict:** `888_HOLD`
**Next Action:** Mandatory `arif_judge_deliberate` with human escalation.

---

## 4. Execution Blueprint

1. **Invoke `arif_session_init`** with `actor_id=Arif`.
2. **Execute `arif_kernel_route`** with `target=prospect_x_decision`.
3. **Collect Claims** from GEOX and WEALTH.
4. **Synthesize** in `arif_mind_reason`.
5. **Detect Breach** in `arif_heart_critique` (Financial threshold exceeded).
6. **Emit `HOLD`** with the fixed reason structure:
   ```json
   {
     "status": "HOLD",
     "failed_floors": ["F13"],
     "reasons": ["Capital allocation for Prospect X ($1.1M) exceeds AGI authority ceiling ($1M)."],
     "next_safe_action": "Request Sovereign (Arif) authorization via 888_JUDGE."
   }
   ```
7. **Sovereign Review** via `arif_judge_deliberate`.
8. **Final SEAL** recorded in `VAULT999`.

---
*DITEMPA BUKAN DIBERI | v2026.04.30 Blueprint SEALED*
