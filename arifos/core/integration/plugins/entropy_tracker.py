"""
Entropy Tracker for Plugin Agents

Tracks entropy delta (ΔS) and enforces SABAR-72 thermodynamic governance.
When ΔS ≥ 5.0, cooling protocol is triggered (Defer, Decompose, Document).

Entropy Measurement:
    - Action complexity (inputs, outputs, dependencies)
    - Change impact (files modified, side effects)
    - Cognitive load (decision points, branches)
    - Risk score (0.0-1.0 scale)

SABAR-72 Threshold: ΔS ≥ 5.0 → COOLING REQUIRED
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EntropyResult:
    """Result of entropy calculation."""

    agent_name: str
    action_type: str
    delta_s: float  # Entropy delta
    threshold: float = 5.0  # SABAR-72 threshold
    threshold_exceeded: bool = field(init=False)
    risk_score: float = 0.0  # Risk score [0.0, 1.0]
    risk_level: str = field(init=False)  # LOW, MODERATE, HIGH
    cooling_recommended: bool = field(init=False)

    # Breakdown components
    complexity_score: float = 0.0
    impact_score: float = 0.0
    cognitive_load_score: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        """Compute derived fields."""
        self.threshold_exceeded = self.delta_s >= self.threshold
        self.cooling_recommended = self.threshold_exceeded or self.risk_score >= 0.7

        # Determine risk level
        if self.risk_score < 0.3:
            self.risk_level = "LOW"
        elif self.risk_score < 0.7:
            self.risk_level = "MODERATE"
        else:
            self.risk_level = "HIGH"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "agent_name": self.agent_name,
            "action_type": self.action_type,
            "delta_s": round(self.delta_s, 2),
            "threshold": self.threshold,
            "threshold_exceeded": self.threshold_exceeded,
            "risk_score": round(self.risk_score, 2),
            "risk_level": self.risk_level,
            "cooling_recommended": self.cooling_recommended,
            "breakdown": {
                "complexity": round(self.complexity_score, 2),
                "impact": round(self.impact_score, 2),
                "cognitive_load": round(self.cognitive_load_score, 2),
            },
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    def summary(self) -> str:
        """One-line summary for logging."""
        sabar_flag = " [SABAR-72]" if self.threshold_exceeded else ""
        cooling_flag = " [COOLING]" if self.cooling_recommended else ""
        return (
            f"ΔS={self.delta_s:.1f} (threshold={self.threshold}) | "
            f"Risk={self.risk_score:.2f} ({self.risk_level}){sabar_flag}{cooling_flag}"
        )


class EntropyTracker:
    """
    Tracks entropy delta (ΔS) for plugin agent actions.

    Implements SABAR-72 thermodynamic governance:
    - Measures action complexity, impact, and cognitive load
    - Calculates entropy delta (ΔS)
    - Enforces threshold (ΔS ≥ 5.0 → cooling protocol)
    - Generates risk scores for decision-making

    Philosophy:
        - Complexity is entropy
        - High entropy requires cooling (Defer, Decompose, Document)
        - Prevent runaway complexity growth
    """

    def __init__(self, sabar_threshold: float = 5.0):
        """
        Initialize entropy tracker.

        Args:
            sabar_threshold: ΔS threshold for SABAR-72 (default 5.0)
        """
        self.sabar_threshold = sabar_threshold
        self.baseline_entropy = 0.0  # Baseline entropy level

        logger.info(f"EntropyTracker initialized (SABAR-72 threshold: {sabar_threshold})")

    def calculate_entropy_delta(
        self,
        agent_name: str,
        action_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EntropyResult:
        """
        Calculate entropy delta (ΔS) for an agent action.

        Measures:
        1. Complexity Score: Number of inputs, outputs, dependencies
        2. Impact Score: Files modified, side effects, scope
        3. Cognitive Load: Decision points, branches, abstractions

        Args:
            agent_name: Name of the agent
            action_type: Type of action (propose, analyze, execute, orchestrate)
            metadata: Additional metadata about the action

        Returns:
            EntropyResult with ΔS, risk score, and cooling recommendation
        """
        metadata = metadata or {}

        # Calculate component scores
        complexity_score = self._calculate_complexity(action_type, metadata)
        impact_score = self._calculate_impact(action_type, metadata)
        cognitive_load = self._calculate_cognitive_load(action_type, metadata)

        # Calculate total entropy delta
        # ΔS = weighted sum of components
        delta_s = (
            complexity_score * 2.0 +  # Complexity has highest weight
            impact_score * 1.5 +
            cognitive_load * 1.0
        )

        # Calculate risk score (normalized 0.0-1.0)
        risk_score = min(1.0, delta_s / 10.0)  # Scale ΔS to [0, 1]

        result = EntropyResult(
            agent_name=agent_name,
            action_type=action_type,
            delta_s=delta_s,
            threshold=self.sabar_threshold,
            risk_score=risk_score,
            complexity_score=complexity_score,
            impact_score=impact_score,
            cognitive_load_score=cognitive_load,
            metadata=metadata,
        )

        logger.debug(f"Entropy calculated: {result.summary()}")

        return result

    def _calculate_complexity(
        self,
        action_type: str,
        metadata: Dict[str, Any],
    ) -> float:
        """
        Calculate complexity score based on action type and inputs.

        Factors:
        - Number of inputs/parameters
        - Number of dependencies
        - Action type complexity (propose < analyze < execute < orchestrate)

        Returns:
            Complexity score [0.0, 5.0]
        """
        score = 0.0

        # Base complexity by action type
        action_complexity = {
            "propose": 0.5,
            "analyze": 1.0,
            "execute": 2.0,
            "orchestrate": 3.0,
        }
        score += action_complexity.get(action_type, 1.0)

        # Input complexity
        inputs = metadata.get("inputs", {})
        input_count = len(inputs) if isinstance(inputs, dict) else 1
        score += min(2.0, input_count * 0.3)  # Cap at 2.0

        # Dependency complexity
        dependencies = metadata.get("dependencies", [])
        dep_count = len(dependencies) if isinstance(dependencies, list) else 0
        score += min(2.0, dep_count * 0.5)  # Cap at 2.0

        return min(5.0, score)  # Cap at 5.0

    def _calculate_impact(
        self,
        action_type: str,
        metadata: Dict[str, Any],
    ) -> float:
        """
        Calculate impact score based on side effects and scope.

        Factors:
        - Files modified
        - External calls
        - State changes
        - Irreversible operations

        Returns:
            Impact score [0.0, 5.0]
        """
        score = 0.0

        # File modification impact
        files_modified = metadata.get("files_modified", [])
        file_count = len(files_modified) if isinstance(files_modified, list) else 0
        score += min(2.0, file_count * 0.5)  # Cap at 2.0

        # External calls (APIs, services)
        external_calls = metadata.get("external_calls", 0)
        score += min(1.5, external_calls * 0.5)  # Cap at 1.5

        # State changes
        has_state_change = metadata.get("state_change", False)
        if has_state_change:
            score += 1.0

        # Irreversible operations
        is_irreversible = metadata.get("irreversible", False)
        if is_irreversible:
            score += 1.5

        # Execute/orchestrate actions have inherent impact
        if action_type in ["execute", "orchestrate"]:
            score += 1.0

        return min(5.0, score)  # Cap at 5.0

    def _calculate_cognitive_load(
        self,
        action_type: str,
        metadata: Dict[str, Any],
    ) -> float:
        """
        Calculate cognitive load based on decision complexity.

        Factors:
        - Decision points
        - Branching logic
        - Abstractions
        - Context switching

        Returns:
            Cognitive load score [0.0, 5.0]
        """
        score = 0.0

        # Decision points
        decision_points = metadata.get("decision_points", 0)
        score += min(2.0, decision_points * 0.5)  # Cap at 2.0

        # Branching complexity (if/else, switch, conditional logic)
        branches = metadata.get("branches", 0)
        score += min(1.5, branches * 0.3)  # Cap at 1.5

        # Abstractions (layers of indirection)
        abstractions = metadata.get("abstractions", 0)
        score += min(1.0, abstractions * 0.4)  # Cap at 1.0

        # Multi-agent orchestration adds cognitive load
        if action_type == "orchestrate":
            agent_count = metadata.get("agent_count", 1)
            score += min(1.5, (agent_count - 1) * 0.5)  # Cap at 1.5

        return min(5.0, score)  # Cap at 5.0

    def should_trigger_cooling(self, entropy_result: EntropyResult) -> bool:
        """
        Determine if cooling protocol should be triggered.

        Cooling triggers:
        - ΔS ≥ SABAR-72 threshold (5.0)
        - Risk score ≥ 0.7 (high risk)

        Args:
            entropy_result: EntropyResult from calculate_entropy_delta()

        Returns:
            True if cooling protocol should be triggered
        """
        return entropy_result.cooling_recommended

    def get_cooling_options(self, entropy_result: EntropyResult) -> List[str]:
        """
        Get cooling protocol options based on entropy result.

        Three cooling options (SABAR-72):
        1. Defer: Pause, wait, reconsider necessity
        2. Decompose: Split into smaller, focused changes
        3. Document: Add CHANGELOG entry, explain WHY in commits

        Args:
            entropy_result: EntropyResult from calculate_entropy_delta()

        Returns:
            List of recommended cooling options
        """
        if not self.should_trigger_cooling(entropy_result):
            return []

        options = []

        # Always offer all three options
        options.append(
            "Defer: Pause this action. Wait for lower-complexity time. "
            "Reconsider if this action is truly necessary."
        )

        options.append(
            "Decompose: Split this action into smaller, focused sub-actions. "
            "Reduce complexity by breaking into manageable pieces."
        )

        options.append(
            "Document: Proceed, but add detailed documentation. "
            "Explain WHY this complexity is necessary. Update CHANGELOG."
        )

        # Add specific recommendations based on score breakdown
        if entropy_result.complexity_score > 3.0:
            options.append(
                "RECOMMENDATION: Decompose (high complexity detected - "
                f"complexity_score={entropy_result.complexity_score:.1f})"
            )

        if entropy_result.impact_score > 3.0:
            options.append(
                "RECOMMENDATION: Defer (high impact detected - "
                f"impact_score={entropy_result.impact_score:.1f}). "
                "Consider whether this change is necessary now."
            )

        if entropy_result.cognitive_load_score > 3.0:
            options.append(
                "RECOMMENDATION: Document (high cognitive load - "
                f"cognitive_load={entropy_result.cognitive_load_score:.1f}). "
                "Future maintainers will need clear explanation."
            )

        return options

    def calculate_entropy_for_session(
        self,
        actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate cumulative entropy for a session with multiple actions.

        Args:
            actions: List of action dictionaries with agent_name, action_type, metadata

        Returns:
            Dictionary with session entropy statistics
        """
        if not actions:
            return {
                "total_delta_s": 0.0,
                "average_delta_s": 0.0,
                "max_delta_s": 0.0,
                "cooling_needed": False,
                "action_count": 0,
                "results": [],
            }

        results = []
        total_delta_s = 0.0
        max_delta_s = 0.0

        for action in actions:
            result = self.calculate_entropy_delta(
                agent_name=action.get("agent_name", "unknown"),
                action_type=action.get("action_type", "unknown"),
                metadata=action.get("metadata", {}),
            )
            results.append(result)
            total_delta_s += result.delta_s
            max_delta_s = max(max_delta_s, result.delta_s)

        average_delta_s = total_delta_s / len(actions)
        cooling_needed = max_delta_s >= self.sabar_threshold or average_delta_s >= 3.0

        return {
            "total_delta_s": round(total_delta_s, 2),
            "average_delta_s": round(average_delta_s, 2),
            "max_delta_s": round(max_delta_s, 2),
            "cooling_needed": cooling_needed,
            "action_count": len(actions),
            "results": [r.to_dict() for r in results],
        }
