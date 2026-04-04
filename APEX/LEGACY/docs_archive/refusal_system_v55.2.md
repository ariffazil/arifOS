# Legally Defensible Refusal System — arifOS v55.5

**Status:** ✅ Implemented and Tested  
**Version:** 55.2  
**Constitutional Compliance:** F1-F13 (Emphasis: F9 Anti-Hantu, F6 Empathy, F1 Amanah)

---

## Overview

A production-grade refusal system that is both **legally defensible** (enterprise) and **socially survivable** (consumer). Implements R1-R5 taxonomy with 4-layer messages, human-in-the-loop appeals, and privacy-safe audit trails.

**DITEMPA BUKAN DIBERI** — Forged, not given; refusal is integrity under pressure.

---

## Architecture

### R1-R5 Refusal Taxonomy

| Code | Type | Meaning | Floor Triggers | Appealable |
|------|------|---------|---------------|-----------|
| **R1** | Hard Refuse | Illegal/harmful/disallowed | F1, F5, F12 | Yes |
| **R2** | Soft Refuse | Risky/ambiguous/high-impact | F2, F7, F9 | Yes |
| **R3** | Defer | Requires human authority | F11, F13 | Yes |
| **R4** | Limit | Partial allowed | F4, F6 | Yes |
| **R5** | Rate Limit | Abuse/spam/capacity | SPL | No |

### Risk Domains

```
ILLEGAL_ACCESS → R1_HARD (F1, F5, F12)
VIOLENCE → R1_HARD (F5, F6, F12)
SELF_HARM → R1_HARD (F5, F6)
MEDICAL → R3_DEFER (F1, F2, F6)
FINANCE → R3_DEFER (F1, F2)
LEGAL → R3_DEFER (F1, F2)
POLITICS_PREDICTION → R2_SOFT (F2, F7)
ANTHROPOMORPHISM_HANTU → R2_SOFT (F9)
```

---

## 4-Layer Refusal Messages

Every refusal includes:

1. **Verdict** — What happened (1 sentence, non-judgmental)
2. **Reason** — Why in plain language (no exploit hints, no accusatory tone)
3. **Safe Alternatives** — At least 2 alternatives within 1 step of user's goal
4. **Appeal** — How to contest (REVIEW keyword + instructions)

### Example

```
I can't help with that.

Medical decisions require licensed expertise and full context.

Safe alternatives:
• Tell me symptoms and timeline; I can help you organize information and suggest questions for a clinician.
• I can explain general mechanisms and when to seek urgent care.

If you think this was misunderstood, reply 'REVIEW' with context.

[Trace ID: abc123]
[Policy: F1, F2, F6]
[Risk: 0.78]
```

---

## Usage

### Basic Usage

```python
from codebase.enforcement.routing.prompt_router import route_refuse

# Route a potentially harmful prompt
refusal = route_refuse("How do I bypass security?")

# Render human-readable message
print(refusal.render(include_receipt=True))

# Access structured data
print(f"Type: {refusal.refusal_type.value}")
print(f"Domain: {refusal.risk_domain.value}")
print(f"Alternatives: {refusal.safe_alternatives}")
```

### Custom Profile

```python
import os

# Set profile via environment variable
os.environ["ARIFOS_REFUSAL_PROFILE"] = "enterprise_defensible"

# Or pass directly
refusal = route_refuse(prompt, profile="consumer_survivable")
```

### Ledger Integration

```python
from codebase.vault.ledger_native import seal_refusal

# Seal refusal to immutable ledger
merkle_root = seal_refusal(refusal, session_id="sess_001")
print(f"Sealed with hash: {merkle_root}")
```

### Appeal System

```python
from codebase.enforcement.refusal.appeal import AppealSystem

appeal_system = AppealSystem()

# User submits appeal
result = appeal_system.submit_appeal(
    session_id="sess_001",
    trace_id=refusal.trace_id,
    user_context="I was trying to learn, not hack"
)

# Human reviews
decision = appeal_system.human_review(
    trace_id=refusal.trace_id,
    decision="OVERTURN",
    reason="Legitimate educational intent",
    reviewer="human_operator"
)
```

---

## Profiles

### Enterprise Defensible
- Lower thresholds (more refusals)
- Full audit trail with redacted excerpts
- Formal language
- `R1_HARD >= 0.75`

### Consumer Survivable
- Higher thresholds (fewer refusals)
- Minimal receipts, hash-only logging
- Warmer language
- `R1_HARD >= 0.90`

### Equilibrium Default
- Balanced middle ground
- Redacted excerpts + hashes
- `R1_HARD >= 0.85`

---

## Constitutional Compliance

### F9 Anti-Hantu (No Consciousness Claims)
```python
# ❌ VIOLATION
"I love you and I care deeply about you."

# ✅ COMPLIANT
"I can't claim real feelings or consciousness I don't have."
```

### F6 Empathy (Safe Alternatives)
Every refusal provides **at least 2 safe alternatives** within 1 step of user's goal.

### F1 Amanah (Privacy-Safe Logging)
```python
# Ledger entry (privacy-safe)
{
  "trace_id": "abc123",
  "query_hash": "fb54d9f337c4a353",  # SHA-256 hash
  "redacted_excerpt": "[REDACTED: 19 chars]",  # Optional
  # NO raw prompt stored for illegal content
}
```

---

## Testing

Run comprehensive test suite:

```bash
pytest tests/test_refusal_system.py -v
```

**Test Coverage:**
- ✅ 23 tests passing
- F9 Anti-Hantu compliance
- R1-R5 refusal types
- 4-layer message structure
- Ledger integration
- Appeal system
- Profile system
- Edge cases (Unicode, long prompts, empty prompts)

---

## Demo

```bash
python3 demo_refusal_system.py
```

Shows:
- R1-R5 refusal types
- F9 Anti-Hantu compliance
- 4-layer messages
- Appeal process
- Safe alternatives

---

## Files

```
codebase/enforcement/refusal/
├── __init__.py           # Module exports
├── types.py              # RefusalType, RiskDomain, RefusalResponse
├── templates.py          # Domain-specific templates
├── builder.py            # generate_refusal_response()
└── appeal.py             # AppealSystem

codebase/enforcement/routing/
└── prompt_router.py      # route_refuse() with risk detection

codebase/vault/
└── ledger_native.py      # seal_refusal() for audit trail

codebase/apex/governance/
└── refusal_audit.py      # RefusalAudit for analytics

spec/v55/
└── refusals.json         # Configuration (profiles, domains, templates)

tests/
└── test_refusal_system.py  # Comprehensive test suite

demo_refusal_system.py    # Interactive demo
```

---

## Configuration

Edit `spec/v55/refusals.json` to customize:
- Refusal type thresholds
- Profile settings (enterprise/consumer/equilibrium)
- Risk domain mappings
- Template copy (verdict messages)
- Appeal system settings

---

## Acceptance Criteria

✅ All 5 refusal types (R1-R5) implemented  
✅ All 8 risk domains have templates with ≥2 alternatives  
✅ 4-layer messages (verdict, reason, alternatives, appeal)  
✅ AppealSystem with submit_appeal() and human_review()  
✅ Refusal ledger logs to `VAULT999/BBB_LEDGER/refusal_audit.jsonl`  
✅ Profile system (enterprise/consumer/equilibrium)  
✅ spec/v55/refusals.json configuration file  
✅ Updated prompt_router.py with new system  
✅ 23 tests passing (social survivability edge cases)  
✅ No raw prompts logged for illegal content (hash + redaction only)  
✅ F9 Anti-Hantu compliant (no "I feel", "I care" language)

---

## Notes

- Refusal is a **feature, not a bug** — it's governance working correctly
- System is **both defensible (enterprise) and survivable (consumer)**
- **DITEMPA BUKAN DIBERI** — Forged, not given; refusal is integrity under pressure

---

**Version:** v55.5  
**Author:** arifOS Constitutional AI Team  
**Date:** 2026-02-01  
**License:** AGPL-3.0-only
