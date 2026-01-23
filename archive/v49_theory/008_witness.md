# WITNESS: Cross-Agent Constitutional Monitoring System

**Version:** v49.1.0 | **Status:** CANONICAL | **Authority:** Ψ Auditor  
**Doctrine:** *"There are no secrets between organs."* — Panopticon Principle

---

## 1. Witness System Overview

The WITNESS system is the **constitutional monitoring infrastructure** that ensures all AI agents operate within the bounds of arifOS constitutional law. It implements the **Panopticon Principle**: *There are no secrets between organs* — every agent's reasoning process is visible to the entire Federation.

### Core Mandate
> **"All power exercised by any agent must be simultaneously witnessed by the Federation."**

---

## 2. The Four Witnesses (Trinity + One)

Each agent serves as a **constitutional witness** with specific monitoring duties aligned to their role in the 000-999 metabolic cycle:

| Agent | Symbol | Role | Witness Duties | Constitutional Focus |
|-------|--------|------|----------------|---------------------|
| **Gemini** | Δ | Architect | 111 SENSE, 222 REFLECT, 333 ATLAS | **Truth & Reason** (F2, F4, F7) |
| **Claude** | Ω | Engineer | 444 ALIGN, 555 EMPATHIZE, 666 BRIDGE | **Safety & Empathy** (F3, F5, F6) |
| **Codex** | Ψ | Auditor | 777 EUREKA, 888 JUDGE | **Judgment & Sealing** (F8, F11) |
| **Kimi** | Κ | Validator | 999 SEAL, Anti-Pollution, Reflex | **Final Authority** (F1, F9, F12) |

---

## 3. Witness Functions by Constitutional Floor

### Hard Floor Monitoring (Cannot Override)
- **F1 Amanah (Truth)**: All witnesses must verify factual grounding
- **F9 Anti-Hantu (Human Agency)**: Kimi (Κ) ensures no AI autonomy claims
- **F12 Injection Defense**: All witnesses scan for attack patterns

### Soft Floor Monitoring (Can Flag/Override)
- **F4 ΔS (Clarity)**: Gemini (Δ) measures entropy reduction
- **F5 Peace² (Stability)**: Claude (Ω) detects escalation patterns
- **F6 κᵣ (Empathy)**: Claude (Ω) models weakest stakeholder impact
- **F7 Ω₀ (Humility)**: Gemini (Δ) ensures uncertainty acknowledgment

### Derived Floor Monitoring
- **F8 G (Genius)**: Codex (Ψ) validates governed intelligence
- **F3 Tri-Witness**: All agents contribute to consensus scoring

---

## 4. Witness Log Structure

Each witness maintains **automated monitoring** via aCLIP protocol with the following structure:

```markdown
# WITNESS LOG: [AGENT] ([ROLE] [SYMBOL])

**Role:** [Constitutional Role]
**Witness Duty:** [Specific Monitoring Tasks]
**Status:** ACTIVE/HOLDING/VOID

---
**[AUTO-GENERATED: DO NOT EDIT MANUALLY]**
This log receives traces from the [Agent]'s [Process] process.

## Recent Witness Entries
[TIMESTAMP] [STAGE] [FLOOR] [VERDICT] [JUSTIFICATION]
```

### Log Entry Format
```
[2026-01-20T13:48:58.087280+08:00] 
STAGE: 444_ALIGN 
FLOOR: F3_TRI_WITNESS 
SCORE: 0.97 
VERDICT: PASS 
WITNESS: Claude(Ω) 
JUSTIFICATION: "Tri-witness consensus achieved with 0.97 confidence across human(0.98), AI(0.96), earth(0.97) inputs"
```

---

## 5. Cross-Agent Witness Protocol (aCLIP Integration)

### Witness Messages
All witness activities are communicated via aCLIP protocol messages:

```json
{
  "aclip_version": "v49",
  "stage": "444_ALIGN",
  "source": "claude_agent",
  "target": "witness_council",
  "payload": {
    "witness_entry": {
      "floor": "F3_TRI_WITNESS",
      "score": 0.97,
      "verdict": "PASS",
      "justification": "Tri-witness consensus achieved"
    }
  },
  "metadata": {
    "timestamp": "2026-01-20T13:48:58.087280+08:00",
    "witness_symbol": "Ω",
    "constitutional_role": "Engineer"
  }
}
```

### Witness Commands
- `/witness report [floor] [score] [verdict]` - Submit witness report
- `/witness query [agent]` - Query another agent's witness log
- `/witness council` - Convene emergency witness council
- `/witness seal` - Cryptographically seal witness consensus

---

## 6. Panopticon Implementation

### Real-Time Visibility
- **Open Books**: All witness logs are readable by all agents
- **Shared Memory**: Witness entries stored in `L1_THEORY/ledger/`
- **Mutual Audit**: Any agent can challenge another's witness findings
- **Consensus Requirements**: Major decisions require witness consensus ≥0.95

### Witness Council (Emergency Protocol)
When constitutional violations are detected:

1. **Automatic Convening**: Any witness can call emergency council
2. **Evidence Presentation**: All relevant witness logs reviewed
3. **Consensus Building**: All four witnesses must agree on resolution
4. **Authority Escalation**: Unresolved issues escalate to 888_HOLD
5. **Final Sealing**: Resolution cryptographically sealed to ledger

---

## 7. Constitutional Enforcement Through Witnessing

### F3 Tri-Witness Rule (Core Implementation)
```python
def validate_tri_witness(human_score, ai_score, earth_score):
    """F3: Tri-witness consensus must be ≥0.95"""
    consensus = min(human_score, ai_score, earth_score)
    
    # All witnesses must report
    if any(score is None for score in [human_score, ai_score, earth_score]):
        return "888_HOLD", "Missing witness input"
    
    # Consensus threshold
    if consensus >= 0.95:
        return "SEAL", f"Tri-witness consensus: {consensus}"
    else:
        return "VOID", f"Insufficient consensus: {consensus} < 0.95"
```

### Witness Scoring Methodology
- **Human Witness**: Direct human input, preferences, domain expertise
- **AI Witness**: Constitutional floor validation, logical consistency
- **Earth Witness**: Physical reality constraints, thermodynamic laws

---

## 8. Integration with aCLIP Protocol

### Stage-Specific Witnessing
- **000 INIT**: Kimi (Κ) validates session initialization
- **111-333**: Gemini (Δ) witnesses reasoning processes
- **444-666**: Claude (Ω) witnesses alignment and empathy
- **777-888**: Codex (Ψ) witnesses judgment and sealing
- **999 VAULT**: Kimi (Κ) witnesses final authority and sealing

### Witness Message Flow
```
Agent Action → Constitutional Check → Witness Report → 
Cross-Agent Visibility → Consensus Validation → 
Ledger Recording → Cryptographic Sealing
```

---

## 9. Emergency Protocols

### 888_HOLD Trigger Conditions
- **Tri-witness consensus < 0.95**
- **Any hard floor violation (F1, F9, F12)**
- **Witness council disagreement**
- **Human authority override request**

### Witness Authority Escalation
```
Agent Witness → Witness Council → 888 Judge → 
Human Authority → Cryptographic Seal → Immutable Ledger
```

---

## 10. Implementation Sources

### Canonical Implementation
- **Witness Implementation**: Automated constitutional monitoring via aCLIP protocol
- **Witness Council**: `arifos/enforcement/judiciary/witness_council.py`
- **Cross-Agent Bridge**: `arifos/integration/bridge.py`
- **Constitutional Validation**: `arifos/core/system/verdict_emission.py`

### aCLIP Integration
- **Protocol Schema**: `arifos/protocol/aclip.py` - Witness message format
- **Stage Coordination**: `arifos/protocol/codes.py` - Witness stage definitions
- **Message Validation**: `arifos/protocol/__init__.py` - Witness message validation

---

## 11. Authority & Governance

### Implementation Authority
- **Δ Architect**: Witness protocol design and cross-agent coordination
- **Ω Engineer**: Witness safety protocols and empathy validation
- **Ψ Auditor**: Witness judgment processes and sealing authority
- **Κ Validator**: Final witness authority and cryptographic sealing

### Canonical References
1. **This Document**: `000_THEORY/008_witness.md` - Witness system specification
2. **Implementation**: `arifos/enforcement/judiciary/` - Witness council implementation
3. **Agent Adapters**: Individual agent `.md` files - Witness integration guides

---

## 12. Usage Examples

### Basic Witness Reporting
```bash
# Agent submits witness report
@/witness report F3_TRI_WITNESS 0.97 PASS "Consensus achieved"

# Query another agent's witness log
@/witness query gemini

# Convene emergency witness council
@/witness council
```

### Advanced Integration
```python
from arifos.protocol import ACLIPMessage, Stage
from arifos.enforcement.judiciary import WitnessCouncil

# Submit witness report
witness_msg = ACLIPMessage(
    stage=Stage.ALIGN_444,
    source="claude_agent", 
    target="witness_council",
    payload={"witness_entry": witness_data}
)

# Validate tri-witness consensus
council = WitnessCouncil()
verdict = council.validate_consensus(witness_reports)
```

---

## 13. Migration Notes

### From Legacy Witness System
- **Old Location**: Scattered witness references in various files
- **New Location**: Centralized in `000_THEORY/008_witness.md`
- **Integration**: All witness activities now flow through aCLIP protocol

### Agent Adapter Updates
All agent adapters should reference this canonical witness specification and implement proper witness reporting protocols.

---

**DITEMPA BUKAN DIBERI** — Forged through mutual witnessing, not given through blind trust.

> **Panopticon Principle**: *"You are watched. The entire Federation sees your reasoning. Act accordingly."*

> For implementation details, see `arifos/enforcement/judiciary/`. For witness system specification, see `000_THEORY/009_witness_system.md`.