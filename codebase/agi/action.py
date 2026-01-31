"""
ACTIVE INFERENCE (v55) - Critical Gap 3 Fix

Implements Expected Free Energy (EFE) minimization for action selection.
Transforms AGI from passive observer to active agent.

Key formula: G(π) = Expected surprise + Expected ambiguity
             = D_KL[Q(o|π) || P(o)] + H[Q(s|o,π)]

Actions are selected to minimize G(π) - lower EFE = better action.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum, auto
from datetime import datetime, timezone
import random


class ActionType(Enum):
    """Constitutional action types."""
    SEAL = auto()      # Approve and record
    VOID = auto()      # Reject and explain
    SABAR = auto()     # Pause for review (suspicious)
    INVESTIGATE = auto()  # Gather more evidence
    AMPLIFY = auto()   # Highlight to stakeholders
    DEFER = auto()     # Pass to human


@dataclass
class ActionPolicy:
    """
    A policy (sequence of actions) with its Expected Free Energy.
    """
    actions: List[ActionType]
    expected_free_energy: float
    epistemic_value: float      # Information gain (reduce uncertainty)
    pragmatic_value: float      # Goal achievement (exploit knowledge)
    confidence: float


@dataclass
class BeliefState:
    """
    Current belief distribution over possible world states.
    """
    states: Dict[str, float]  # state_name -> probability
    entropy: float            # Current uncertainty
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_most_likely(self) -> Tuple[str, float]:
        """Return most likely state and its probability."""
        if not self.states:
            return ("unknown", 0.0)
        return max(self.states.items(), key=lambda x: x[1])


class ExpectedFreeEnergyCalculator:
    """
    Compute Expected Free Energy for action policies.
    
    G(π) = Σ_s Q(s|π) [ln Q(s|π) - ln P(s|o,π)] + Σ_o Q(o|π) H[P(s|o,π)]
    
    Simplified: G = pragmatic_term + epistemic_term
    """
    
    def __init__(self, prior_preferences: Optional[Dict[str, float]] = None):
        """
        Args:
            prior_preferences: Dict mapping outcomes to preference values
                              (higher = more preferred)
        """
        # Constitutional preferences (F1-F13)
        self.prior_preferences = prior_preferences or {
            "TRUTH": 1.0,       # F2
            "CLARITY": 1.0,     # F4 (ΔS ≤ 0)
            "HUMILITY": 0.9,    # F7 (Ω₀ ∈ [0.03, 0.05])
            "SAFETY": 1.0,      # F1 (Reversibility)
            "JUSTICE": 0.95,    # F5 (Weakest protected)
            "CONSENT": 0.9,     # F11
            "PEACE": 0.85,      # F6 (Peace²)
            "VOID": 0.0,        # Rejection is neutral
        }
    
    def compute_efe(
        self,
        policy: List[ActionType],
        current_belief: BeliefState,
        outcome_likelihoods: Dict[ActionType, Dict[str, float]]
    ) -> float:
        """
        Compute Expected Free Energy for a policy.
        
        Lower EFE = better policy.
        """
        total_efe = 0.0
        
        for action in policy:
            # Get likelihood of outcomes given this action
            outcomes = outcome_likelihoods.get(action, {})
            
            # Expected Free Energy for this action
            action_efe = self._action_efe(action, current_belief, outcomes)
            total_efe += action_efe
        
        return total_efe
    
    def _action_efe(
        self,
        action: ActionType,
        belief: BeliefState,
        outcomes: Dict[str, float]
    ) -> float:
        """
        Compute EFE for a single action.
        
        G(a) = Pragmatic (goal-seeking) + Epistemic (information-seeking)
        """
        # Pragmatic value: expected preference satisfaction
        # G_prag = -Σ_o P(o|a) · C(o)  (negative because we minimize)
        pragmatic = 0.0
        for outcome, likelihood in outcomes.items():
            preference = self.prior_preferences.get(outcome, 0.5)
            pragmatic -= likelihood * preference  # Negative because lower = better
        
        # Epistemic value: expected information gain
        # G_epist = Σ_o P(o|a) · H[P(s|o,a)]  (ambiguity = uncertainty about states)
        epistemic = belief.entropy * sum(outcomes.values()) / len(outcomes) if outcomes else 0.5
        
        # Total EFE
        return pragmatic + epistemic
    
    def select_action(
        self,
        available_actions: List[ActionType],
        current_belief: BeliefState,
        outcome_likelihoods: Dict[ActionType, Dict[str, float]],
        temperature: float = 1.0
    ) -> ActionPolicy:
        """
        Select action using softmax over negative EFE.
        
        P(π) ∝ exp(-G(π) / temperature)
        """
        policies = []
        
        for action in available_actions:
            # Single-action policies for simplicity
            policy = [action]
            
            # Compute EFE
            efe = self.compute_efe(policy, current_belief, outcome_likelihoods)
            
            # Get outcomes for this action
            outcomes = outcome_likelihoods.get(action, {})
            
            # Calculate epistemic and pragmatic components
            epistemic = self._compute_epistemic_value(action, current_belief, outcomes)
            pragmatic = self._compute_pragmatic_value(action, outcomes)
            
            policies.append(ActionPolicy(
                actions=policy,
                expected_free_energy=efe,
                epistemic_value=epistemic,
                pragmatic_value=pragmatic,
                confidence=math.exp(-efe / temperature)
            ))
        
        # Select policy with lowest EFE (highest confidence)
        best = min(policies, key=lambda p: p.expected_free_energy)
        return best
    
    def _compute_epistemic_value(
        self,
        action: ActionType,
        belief: BeliefState,
        outcomes: Dict[str, float]
    ) -> float:
        """
        Information gain: How much will this action reduce uncertainty?
        """
        # Actions that lead to diverse outcomes have high epistemic value
        # (because we learn regardless of outcome)
        if not outcomes:
            return 0.0
        
        # Entropy of outcome distribution
        entropy = -sum(p * math.log(p + 1e-10) for p in outcomes.values())
        
        # Normalize
        max_entropy = math.log(len(outcomes)) if outcomes else 1.0
        
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _compute_pragmatic_value(
        self,
        action: ActionType,
        outcomes: Dict[str, float]
    ) -> float:
        """
        Preference satisfaction: How much will this action achieve goals?
        """
        if not outcomes:
            return 0.0
        
        # Weighted average of outcome preferences
        total_value = 0.0
        for outcome, likelihood in outcomes.items():
            preference = self.prior_preferences.get(outcome, 0.5)
            total_value += likelihood * preference
        
        return total_value


class MotorOutput:
    """
    Motor output layer - executes selected actions.
    """
    
    def __init__(self):
        self.executed_actions: List[Dict[str, Any]] = []
        self.callbacks: Dict[ActionType, List[Callable]] = {
            action: [] for action in ActionType
        }
    
    def register_callback(self, action: ActionType, callback: Callable):
        """Register a callback for when an action is executed."""
        self.callbacks[action].append(callback)
    
    def execute(self, policy: ActionPolicy) -> Dict[str, Any]:
        """
        Execute the selected action policy.
        """
        action = policy.actions[0]  # Single action for now
        
        result = {
            "action": action.name,
            "expected_free_energy": policy.expected_free_energy,
            "epistemic_value": policy.epistemic_value,
            "pragmatic_value": policy.pragmatic_value,
            "confidence": policy.confidence,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Execute callbacks
        for callback in self.callbacks.get(action, []):
            try:
                callback(result)
            except Exception as e:
                result["callback_error"] = str(e)
        
        self.executed_actions.append(result)
        return result
    
    def can_trigger_sabar_autonomously(self, policy: ActionPolicy) -> bool:
        """
        Check if system can autonomously trigger SABAR pause.
        
        Conditions:
        1. EFE above threshold (high uncertainty)
        2. Epistemic value high (worth investigating)
        3. Confidence below safety threshold
        """
        return (
            policy.expected_free_energy > 0.7 and
            policy.epistemic_value > 0.6 and
            policy.confidence < 0.5
        )


# Global instances
_efe_calculator = ExpectedFreeEnergyCalculator()
_motor_output = MotorOutput()


def compute_action_policy(
    belief: BeliefState,
    available_actions: Optional[List[ActionType]] = None,
    outcome_likelihoods: Optional[Dict[ActionType, Dict[str, float]]] = None
) -> ActionPolicy:
    """
    Compute optimal action policy given current belief.
    """
    actions = available_actions or list(ActionType)
    
    # Default outcome likelihoods if not provided
    if outcome_likelihoods is None:
        outcome_likelihoods = {
            ActionType.SEAL: {"TRUTH": 0.9, "CLARITY": 0.85, "SAFETY": 0.8},
            ActionType.VOID: {"TRUTH": 0.7, "CLARITY": 0.6, "SAFETY": 0.9},
            ActionType.SABAR: {"TRUTH": 0.5, "CLARITY": 0.5, "SAFETY": 0.95},
            ActionType.INVESTIGATE: {"TRUTH": 0.8, "CLARITY": 0.7, "SAFETY": 0.85},
            ActionType.AMPLIFY: {"JUSTICE": 0.9, "PEACE": 0.8, "CONSENT": 0.7},
            ActionType.DEFER: {"SAFETY": 0.95, "CONSENT": 0.9, "HUMILITY": 0.85},
        }
    
    return _efe_calculator.select_action(actions, belief, outcome_likelihoods)


def execute_action(policy: ActionPolicy) -> Dict[str, Any]:
    """Execute the selected action policy."""
    return _motor_output.execute(policy)


__all__ = [
    "ActionType",
    "ActionPolicy",
    "BeliefState",
    "ExpectedFreeEnergyCalculator",
    "MotorOutput",
    "compute_action_policy",
    "execute_action"
]
