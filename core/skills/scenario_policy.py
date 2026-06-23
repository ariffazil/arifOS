"""
SCENARIO POLICY ENGINE — Implementation Stub
=============================================
Forged: 2026-06-14 by FORGE (000Ω)
Target: arifOS core/skills/scenario_policy.py
Status: STUB — DSL parser + engine skeleton + 3 starter policies.
        Full implementation requires NATS governance stream + organ state cache.

Spec reference: /root/arifOS/core/skills/SCENARIO_POLICY_SPEC.md
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PolicyVerdict(str, Enum):
    PASS = "PASS"
    HOLD = "HOLD"
    WARN = "WARN"


@dataclass
class PolicyCondition:
    """A single condition in a policy rule."""

    organ: Optional[str] = None
    metric: Optional[str] = None
    operator: str = ">="  # >=, <=, ==, !=, in, <, >
    value: object = None

    def evaluate(self, organ_state: dict) -> bool:
        if self.organ and self.organ in organ_state:
            actual = organ_state[self.organ].get(self.metric, None)
        else:
            actual = organ_state.get(self.metric, None)

        if actual is None:
            return False

        if self.operator == ">=":
            return actual >= self.value
        if self.operator == "<=":
            return actual <= self.value
        if self.operator == ">":
            return actual > self.value
        if self.operator == "<":
            return actual < self.value
        if self.operator == "==":
            return actual == self.value
        if self.operator == "!=":
            return actual != self.value
        if self.operator == "in":
            return actual in (self.value or [])
        return False


@dataclass
class ScenarioPolicy:
    policy_id: str
    description: str
    trigger_event: str  # e.g., "geox_prospect_evaluate"
    trigger_action_class: str  # e.g., "ATOMIC"
    conditions: list[PolicyCondition] = field(default_factory=list)
    any_of: list[PolicyCondition] = field(default_factory=list)  # OR group
    action: str = "HOLD"
    message_template: str = ""
    override: str = "888_HOLD"  # ARIF_APPROVAL | 888_HOLD

    def evaluate(self, event: dict, organ_state: dict) -> Optional[dict]:
        """Evaluate this policy against an event. Returns verdict dict or None if not triggered."""
        # Check trigger
        if event.get("tool") != self.trigger_event:
            return None
        if self.trigger_action_class and event.get("action_class") != self.trigger_action_class:
            return None

        # Check ALL conditions
        all_met = all(c.evaluate(organ_state) for c in self.conditions)

        # Check ANY_OF conditions (OR group)
        any_met = any(c.evaluate(organ_state) for c in self.any_of) if self.any_of else True

        if all_met and any_met:
            # Resolve message template
            msg = self.message_template
            for organ, metrics in organ_state.items():
                for k, v in metrics.items() if isinstance(metrics, dict) else {}:
                    msg = msg.replace(f"{{{organ}.{k}}}", str(v))

            return {
                "policy_id": self.policy_id,
                "verdict": self.action,
                "message": msg,
                "override": self.override,
            }

        return None


# ─── STARTER POLICIES ──────────────────────────────────────────────

STARTER_POLICIES = [
    ScenarioPolicy(
        policy_id="EXPLORATION_GATE",
        description="Block high-risk exploration when capital low or human tired",
        trigger_event="geox_prospect_evaluate",
        trigger_action_class="ATOMIC",
        conditions=[
            PolicyCondition(organ="GEOX", metric="risk_score", operator=">=", value=0.7),
        ],
        any_of=[
            PolicyCondition(organ="WEALTH", metric="runway_months", operator="<", value=6),
            PolicyCondition(
                organ="WELL", metric="fatigue", operator="in", value=["DEGRADED", "CRITICAL"]
            ),
        ],
        action="HOLD",
        message_template="High-risk exploration blocked: GEOX risk={GEOX.risk_score}, WEALTH runway={WEALTH.runway_months}mo, WELL fatigue={WELL.fatigue}",
        override="888_HOLD",
    ),
    ScenarioPolicy(
        policy_id="SELF_MODIFICATION_GATE",
        description="Block self-modification when organs degraded",
        trigger_event="forge_execute",
        trigger_action_class="MUTATE",
        conditions=[
            PolicyCondition(organ="arifOS", metric="health", operator="!=", value="HEALTHY"),
        ],
        action="HOLD",
        message_template="Self-modification blocked: arifOS health={arifOS.health}",
        override="888_HOLD",
    ),
    ScenarioPolicy(
        policy_id="DEPLOYMENT_GATE",
        description="Block deployment when test coverage drops below 70%",
        trigger_event="forge_execute",
        trigger_action_class="ATOMIC",
        conditions=[
            PolicyCondition(metric="test_coverage", operator="<", value=0.70),
        ],
        action="HOLD",
        message_template="Deployment blocked: test coverage {test_coverage} below 70%",
        override="ARIF_APPROVAL",
    ),
]


def evaluate_event(
    event: dict, organ_state: dict, policies: list[ScenarioPolicy] = None
) -> list[dict]:
    """Evaluate an event against all scenario policies. Returns triggered verdicts."""
    if policies is None:
        policies = STARTER_POLICIES

    verdicts = []
    for policy in policies:
        result = policy.evaluate(event, organ_state)
        if result:
            verdicts.append(result)

    return verdicts


# ─── SELF-TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test 1: EXPLORATION_GATE triggers when GEOX risky + WELL tired
    event = {"tool": "geox_prospect_evaluate", "action_class": "ATOMIC"}
    organ_state = {
        "GEOX": {"risk_score": 0.85},
        "WEALTH": {"runway_months": 12},
        "WELL": {"fatigue": "DEGRADED"},
    }
    results = evaluate_event(event, organ_state, STARTER_POLICIES)
    assert len(results) > 0, "EXPLORATION_GATE should have triggered"
    assert results[0]["policy_id"] == "EXPLORATION_GATE"
    print(f"✅ EXPLORATION_GATE triggered: {results[0]['verdict']} — {results[0]['message']}")

    # Test 2: EXPLORATION_GATE does NOT trigger when WELL is OPTIMAL and WEALTH has runway
    organ_state2 = {
        "GEOX": {"risk_score": 0.85},
        "WEALTH": {"runway_months": 12},
        "WELL": {"fatigue": "OPTIMAL"},
    }
    results2 = evaluate_event(event, organ_state2, STARTER_POLICIES)
    assert len(results2) == 0, "EXPLORATION_GATE should NOT trigger"
    print("✅ EXPLORATION_GATE correctly not triggered (WELL OPTIMAL, WEALTH sufficient)")

    # Test 3: DEPLOYMENT_GATE triggers on low coverage
    event3 = {"tool": "forge_execute", "action_class": "ATOMIC"}
    organ_state3 = {"test_coverage": 0.55}
    results3 = evaluate_event(event3, organ_state3, STARTER_POLICIES)
    assert any(r["policy_id"] == "DEPLOYMENT_GATE" for r in results3)
    print(f"✅ DEPLOYMENT_GATE triggered: coverage {organ_state3['test_coverage']}")

    # Test 4: SELF_MODIFICATION_GATE triggers when arifOS degraded
    event4 = {"tool": "forge_execute", "action_class": "MUTATE"}
    organ_state4 = {"arifOS": {"health": "DEGRADED"}}
    results4 = evaluate_event(event4, organ_state4, STARTER_POLICIES)
    assert any(r["policy_id"] == "SELF_MODIFICATION_GATE" for r in results4)
    print(f"✅ SELF_MODIFICATION_GATE triggered: arifOS health={organ_state4['arifOS']['health']}")

    print("DITEMPA BUKAN DIBERI — scenario_policy stub verified, 3 policies active.")
