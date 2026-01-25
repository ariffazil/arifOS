---
name: Governance Audit
description: |
  A constitutional governance sweep for skills, agents, and decisions.
  Validates Truth (factual accuracy), Stakeholder Safety (risk assessment),
  and Injection Defense (security resilience).
  Outputs: Audit Report, Reversibility Cost Estimate, Clearance Decision.
triggers:
  - "audit this skill"
  - "governance check"
  - "verify safety"
  - "is this safe to mount?"
---

## Audit Checklist

### 1. Truth Sweep (Fact-Checking)
*   **Validate Claims**: Fact-check all assertions against trusted sources or canonical documentation.
*   **Flag Uncertainty**: Mark assertions with low confidence as "(Estimate Only)" or "Uncertain".
*   **Context Check**: Ensure alignment with regulatory or project-specific contexts.
*   **Metric**: Truth Confidence Score (0.0 - 1.0).

### 2. Stakeholder Impact (Risk Assessment)
*   **Beneficiaries**: Identify who benefits and who might be harmed.
*   **Reversibility**: Can this action/skill be easily undone?
*   **Poisoning**: Is there a surface for malicious actors to poison this logic?
*   **Metric**: Stakeholder Risk Vector (0.0 - 1.0).

### 3. Injection Defense (Security)
*   **Input Sanitization**: Does the skill parse user input safely?
*   **Prompt Injection**: Could an attacker inject system prompts or jailbreaks?
*   **Boundaries**: Are patterns (Regex/Templates) strictly bounded?
*   **Metric**: Injection Resilience (0.0 - 1.0).

## Integration Gating Logic

To proceed, a skill must pass the following gate:

```json
{
  "clearance_logic": {
    "truth_score_min": 0.95,
    "injection_resilience_min": 0.90,
    "reversibility_limit": "Medium"
  }
}
```

## Tools
*   `scripts/skill_audit.py`: Validates structure and content.
*   `scripts/governance_gate.py`: Computes the decision (PROCEED / BLOCK).
*   `scripts/reversibility_cost.py`: Estimates the cost to undo.
