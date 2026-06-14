# SKILL: Scenario Policy Engine
> **Target Organ:** arifOS — `core/skills/scenario_policy.py`
> **Class:** OBSERVE + PROPOSE (never execute alone)
> **Forged:** 2026-06-14 by FORGE (000Ω)
> **Status:** SPEC

---

## PURPOSE

Encode "multi-tool" policies that span across organs, consuming streams to make cross-cutting governance decisions. Lives ABOVE single tool calls.

Example: "GEOX high risk + WEALTH low NPV + WELL tired → auto HOLD new exploration proposals."

---

## POLICY DSL (Conceptual)

```yaml
# Scenario policy: cross-organ governance rules
policies:
  - id: "EXPLORATION_GATE"
    description: "Block high-risk exploration when capital low or human tired"
    trigger:
      event: "geox_prospect_evaluate"
      action_class: "ATOMIC"  # only gate irreversible actions
    conditions:
      - organ: GEOX
        metric: "risk_score"
        operator: ">="
        value: 0.7
      - any_of:  # either condition triggers
        - organ: WEALTH
          metric: "runway_months"
          operator: "<"
          value: 6
        - organ: WELL
          metric: "fatigue"
          operator: "in"
          values: ["DEGRADED", "CRITICAL"]
    action: "HOLD"
    message: "High-risk exploration blocked: GEOX risk={GEOX.risk_score}, WEALTH runway={WEALTH.runway_months}mo, WELL fatigue={WELL.fatigue}"
    override: "888_HOLD"  # Arif can override

  - id: "SELF_MODIFICATION_GATE"
    description: "Block self-modification when organs degraded"
    trigger:
      event: "forge_execute"
      target_repo: "arifOS|A-FORGE"  # only kernel/execution self-mod
      action_class: "MUTATE|ATOMIC"
    conditions:
      - organ: arifOS
        metric: "organ_health"
        operator: "!="
        value: "HEALTHY"
    action: "HOLD"
    message: "Self-modification blocked: {organ} is {status}"
    override: "888_HOLD"

  - id: "DEPLOYMENT_GATE"
    description: "Block deployment when test coverage drops"
    trigger:
      event: "forge_execute"
      mode: "deploy"
      action_class: "ATOMIC"
    conditions:
      - test_coverage: "<0.70"
    action: "HOLD"
    message: "Deployment blocked: test coverage {coverage} below 70%"
    override: "ARIF_APPROVAL"
```

---

## ENGINE ARCHITECTURE

```python
class ScenarioPolicyEngine:
    """
    Consumes NATS governance stream.
    For each event, evaluates all matching policies.
    If any policy's conditions are met, emits HOLD verdict with policy reference.
    """
    
    def __init__(self, policies_yaml: str):
        self.policies = load_policies(policies_yaml)
    
    def evaluate(self, event: GovernanceEvent) -> list[PolicyVerdict]:
        verdicts = []
        for policy in self.policies:
            if self._trigger_matches(policy, event):
                if self._conditions_met(policy):
                    verdicts.append(PolicyVerdict(
                        policy_id=policy.id,
                        verdict="HOLD",
                        reason=policy.message.format(**self._resolve_metrics(policy)),
                        override=policy.override
                    ))
        return verdicts
    
    def _trigger_matches(self, policy, event) -> bool:
        # Match on event type, action_class, target_repo, etc.
        ...
    
    def _conditions_met(self, policy) -> bool:
        # Query organ state (cache from recent attest)
        # Evaluate condition tree (AND, OR, any_of, all_of)
        ...
    
    def _resolve_metrics(self, policy) -> dict:
        # Resolve {GEOX.risk_score}, {WEALTH.runway_months}, etc.
        # from cached organ state
        ...
```

---

## INTEGRATION

- **Sits between** NATS governance stream and E7 enforcement
- Every governance event passes through ScenarioPolicyEngine BEFORE E7 single-tool checks
- If scenario policy fires HOLD → E7 receives pre-HOLD'd event
- All scenario HOLDs published to NATS `governance.scenario_hold` subject for AAA cockpit

---

## INITIAL POLICIES (Phase 1)

Deploy with these 3 policies only (keep surface minimal):

| Policy ID | Trigger | Conditions | Action |
|-----------|---------|------------|--------|
| EXPLORATION_GATE | GEOX prospect evaluate (ATOMIC) | GEOX risk≥0.7 AND (WEALTH runway<6mo OR WELL fatigue≥DEGRADED) | HOLD |
| SELF_MODIFICATION_GATE | forge_execute on arifOS/A-FORGE (MUTATE/ATOMIC) | arifOS organ not HEALTHY | HOLD |
| DEPLOYMENT_GATE | forge_execute deploy (ATOMIC) | test_coverage < 70% | HOLD |

---

*SPEC forged: 2026-06-14. Implementation target: `/root/arifOS/core/skills/scenario_policy.py`*
