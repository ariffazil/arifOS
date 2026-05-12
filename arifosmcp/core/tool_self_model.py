"""
arifOS Tool Self-Model — Runtime Tool Self-Awareness
═══════════════════════════════════════════════════════════════════════════════

The agent knows its own tools at runtime:
- What each tool can do
- What it cannot do
- What permissions it needs vs has
- What its failure modes are
- What tools compose safely with it
- What it predicted vs what reality returned (disequilibrium)

441_SURPRISE: When prediction falsification exceeds critical threshold,
the agent must halt forward execution and repair its model. This is the
bridge from statistical mimicry to causal self-awareness.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CognitiveAxis(str, Enum):
    """
    11 orthogonal cognitive vectors + 2 lifecycle verbs.
    Enables intent-based routing prior to domain resolution.
    """

    IDENTITY = "identity"   # Who/what is this?
    OBSERVE  = "observe"    # What is the raw state?
    TRACE    = "trace"      # How did we get here?
    BOUNDARY = "boundary"   # What are the limits?
    VERIFY   = "verify"     # Is this true? [F2]
    REASON   = "reason"     # What does this mean?
    VITALITY = "vitality"   # Can we sustain?
    REFLECT  = "reflect"    # Are we thinking right?
    CRITIQUE = "critique"   # Is this ethical/coherent?
    JUDGE    = "judge"      # What's the verdict?
    SEAL     = "seal"       # Lock it in? [W_scar]
    REPAIR   = "repair"     # Do we fix?
    EXECUTE  = "execute"    # Do it?


COGNITIVE_AXIS_VECTORS: dict[CognitiveAxis, tuple[float, float]] = {
    CognitiveAxis.IDENTITY: (0.3, 0.1),
    CognitiveAxis.OBSERVE:  (0.2, 0.0),
    CognitiveAxis.TRACE:    (0.6, 0.1),
    CognitiveAxis.BOUNDARY: (0.5, 0.3),
    CognitiveAxis.VERIFY:   (0.9, 0.2),
    CognitiveAxis.REASON:   (0.4, 0.4),
    CognitiveAxis.VITALITY: (0.5, 0.5),
    CognitiveAxis.REFLECT:  (0.3, 0.1),
    CognitiveAxis.CRITIQUE: (0.7, 0.3),
    CognitiveAxis.JUDGE:    (0.8, 0.7),
    CognitiveAxis.SEAL:     (1.0, 0.9),
    CognitiveAxis.REPAIR:   (0.5, 0.6),
    CognitiveAxis.EXECUTE:  (0.9, 1.0),
}


class BlastRadius(str, Enum):
    """How widely effects propagate from this tool."""

    LOW = "low"  # Isolated, contained
    MEDIUM = "medium"  # Affects current session
    HIGH = "high"  # Affects multiple sessions or systems
    CRITICAL = "critical"  # Affects federation, irreversible


class ToolCapability(BaseModel):
    """A single capability of a tool."""

    name: str = Field(description="Capability identifier")
    description: str = Field(description="What this capability does")
    parameters: list[str] = Field(default_factory=list, description="Required parameter names")
    output_fields: list[str] = Field(default_factory=list, description="Output fields produced")


class ToolLimitation(BaseModel):
    """A known limitation of a tool."""

    name: str = Field(description="Limitation identifier")
    description: str = Field(description="What the tool cannot do")
    severity: str = Field(default="medium", description="'high' | 'medium' | 'low'")


class ToolFailureMode(BaseModel):
    """A known failure mode for a tool."""

    pattern: str = Field(description="What triggers this failure")
    symptom: str = Field(description="How the failure appears")
    recovery: str = Field(description="How to recover from this failure")
    severity: str = Field(default="medium", description="'high' | 'medium' | 'low'")


class ToolManifest(BaseModel):
    """
    Complete self-description of a tool.

    Every tool must declare this at registration time.
    """

    tool_id: str = Field(description="Canonical tool identifier")
    tool_name: str = Field(description="Human-readable name")
    domain: str = Field(description="AOS | WELL | WEALTH | GEOX")
    description: str = Field(default="", description="What this tool does")
    version: str = Field(default="1.0.0")

    # Capabilities
    capabilities: list[ToolCapability] = Field(
        default_factory=list, description="What this tool can do"
    )
    limitations: list[ToolLimitation] = Field(
        default_factory=list, description="What this tool cannot do"
    )

    # Risk classification
    blast_radius: BlastRadius = Field(
        default=BlastRadius.LOW, description="How widely effects propagate"
    )
    risk_tier: str = Field(default="T1", description="T0-T4 risk classification")

    # Reversibility
    reversibility: str = Field(
        default="reversible", description="'reversible' | 'partial' | 'irreversible'"
    )

    # Permissions
    required_permissions: list[str] = Field(
        default_factory=list, description="Permissions needed to execute"
    )
    required_floors: list[str] = Field(
        default_factory=list, description="F01-F13 floors that apply"
    )

    # Composition
    safe_compose_with: list[str] = Field(
        default_factory=list,
        description="Tool IDs that compose safely after this",
    )
    dangerous_compose_with: list[str] = Field(
        default_factory=list,
        description="Tool IDs that should not follow this",
    )

    # Failure modes
    known_failure_modes: list[ToolFailureMode] = Field(default_factory=list)

    # Visibility — somatic membrane gate
    expose: bool = Field(
        default=False,
        description="If True, tool appears in public MCP surface. If False, internal/autonomic only.",
    )

    # Cognitive axis — intent-based routing vector
    cognitive_axis: CognitiveAxis | None = Field(
        default=None,
        description="The orthogonal cognitive axis for intent-based routing.",
    )

    # Example
    example_params: dict[str, Any] | None = Field(default=None, description="Example parameters")

    def capability_hash(self) -> str:
        """Stable hash of this tool's capabilities."""
        data = json.dumps(
            {
                "tool_id": self.tool_id,
                "capabilities": [c.model_dump() for c in self.capabilities],
                "limitations": [lim.model_dump() for lim in self.limitations],
                "blast_radius": self.blast_radius.value,
                "risk_tier": self.risk_tier,
                "reversibility": self.reversibility,
            },
            sort_keys=True,
        )
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class PredictionRecord(BaseModel):
    """
    A single prediction-reality comparison.

    The agent must stake a claim before every tool execution:
    - What it expects to happen
    - How confident it is
    - What would falsify its internal model

    After execution, this is compared against reality to compute δ_surprise.
    """

    predicted_outcome: str = Field(description="Structured prediction of expected state change")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in prediction (0.0-1.0)")
    falsification_condition: str = Field(
        description="Specific alternative outcome that would invalidate current model"
    )
    actual_outcome: str | None = Field(default=None, description="What actually happened")
    prediction_error: float = Field(
        default=0.0, ge=0.0, description="MSE between predicted and actual"
    )
    delta_surprise: float = Field(
        default=0.0, ge=0.0, description="δ_surprise = f(confidence, error)"
    )
    triggered_surprise: bool = Field(
        default=False, description="Did δ_surprise exceed critical threshold?"
    )
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def compute_delta_surprise(
        self,
        actual_outcome: str,
        model_importance: float = 1.0,
        critical_threshold: float = 0.70,
    ) -> float:
        """
        Compute δ_surprise — the disequilibrium signal.

        δ_surprise = confidence × prediction_error × model_importance

        Where prediction_error is a semantic distance (0.0 = exact match, 1.0 = total mismatch).
        High confidence × high error = maximum surprise.
        Low confidence × high error = expected uncertainty.
        """
        self.actual_outcome = actual_outcome

        # Prediction error: exact match = 0.0, total mismatch = 1.0
        if self.predicted_outcome == actual_outcome:
            self.prediction_error = 0.0
        elif not self.predicted_outcome or not actual_outcome:
            self.prediction_error = 0.5
        else:
            # Simple semantic distance: string difference ratio
            s1 = self.predicted_outcome.lower().strip()
            s2 = actual_outcome.lower().strip()
            if s1 == s2:
                self.prediction_error = 0.0
            else:
                # Levenshtein-like: character overlap ratio inverted
                longer = max(len(s1), len(s2))
                if longer == 0:
                    self.prediction_error = 0.0
                else:
                    matches = sum(1 for a, b in zip(s1, s2, strict=False) if a == b)
                    self.prediction_error = 1.0 - (matches / longer)

        # δ_surprise: confident prediction that was wrong = maximum structural surprise
        self.delta_surprise = self.confidence * self.prediction_error * model_importance
        self.triggered_surprise = self.delta_surprise >= critical_threshold

        return self.delta_surprise


# ── Disequilibrium Thresholds ──────────────────────────────────────────────────
#
# δ_surprise = confidence × prediction_error × model_importance
#
# Boundary analysis:
#   Range: [0.0, 3.0]  (max when c=1.0, err=1.0, imp=3.0 for T4)
#
#   T0 (c=0.9, imp=0.3): δ_max = 0.27 — never triggers 441 (correct: T0 is observe-only)
#   T1 (c=0.85, imp=0.5): δ_max = 0.425 — never triggers 441
#   T2 (c=0.7, imp=1.0):  δ_max = 0.70 — triggers exactly at threshold (correct: T2 is consequential)
#   T3 (c=0.5, imp=2.0):  δ_max = 1.00 — triggers easily (correct: T3 is high stakes)
#   T4 (c=0.3, imp=3.0):  δ_max = 0.90 — triggers (correct: T4 is critical)
#
# Therefore SURPRISE_CRITICAL_THRESHOLD = 0.70:
#   - T0/T1 tools never trigger surprise (they are low-risk observations)
#   - T2 tools trigger only at maximum error (strong signal required)
#   - T3/T4 tools trigger at moderate error (correct: high-stakes tools must be right)
#
# SURPRISE_CONTRADICTION_LIMIT = 3:
#   - One surprise = possible anomaly (could be noise)
#   - Two surprises = pattern emerging (caution warranted)
#   - Three surprises in sliding window of 10 = structural model failure (halt required)
#   - This prevents false positives from transient errors while catching real degradation
#
SURPRISE_WINDOW_SIZE = 10
SURPRISE_CRITICAL_THRESHOLD = 0.70
SURPRISE_CONTRADICTION_LIMIT = 3


class ToolSelfModelEntry(BaseModel):
    """
    Runtime state of a single tool in the agent's body.

    Tracks what the agent actually knows about this tool
    and whether that knowledge has been contradicted by reality.
    """

    manifest: ToolManifest = Field(description="Tool's self-declaration")
    last_used: str | None = Field(default=None, description="ISO timestamp of last use")
    last_result_summary: str | None = Field(
        default=None, description="One-line summary of last result"
    )
    use_count: int = Field(default=0, description="Total times used")
    failure_count: int = Field(default=0, description="Times this tool failed")
    last_error: str | None = Field(default=None, description="Last error message")

    # Prediction histor y — the agent's record of what it expected vs what happened
    prediction_history: deque = Field(
        default_factory=lambda: deque(maxlen=SURPRISE_WINDOW_SIZE),
        description="Rolling window of PredictionRecord entries",
    )
    contradiction_count: int = Field(
        default=0, description="Number of δ_surprise events exceeding critical threshold in window"
    )
    model_contradicted: bool = Field(
        default=False,
        description="Flag: tool's self-model has been contradicted and needs re-evaluation",
    )

    # Agent's actual permissions (populated at runtime from session)
    actual_permissions: list[str] = Field(
        default_factory=list, description="Permissions the agent actually has"
    )

    # Computed
    @property
    def permission_gap(self) -> list[str]:
        """Permissions required but not held."""
        required = set(self.manifest.required_permissions)
        actual = set(self.actual_permissions)
        return sorted(required - actual)

    @property
    def has_permission_gap(self) -> bool:
        """Does this tool call require permissions the agent lacks?"""
        return len(self.permission_gap) > 0

    @property
    def is_safe_to_execute(self) -> bool:
        """Can this tool be executed safely right now?

        A contradicted model is NOT safe to execute until repaired.
        """
        if self.model_contradicted:
            return False
        return not self.has_permission_gap and self.failure_count < 3

    @property
    def surprise_rate(self) -> float:
        """Proportion of recent predictions that triggered surprise."""
        if not self.prediction_history:
            return 0.0
        triggered = sum(1 for p in self.prediction_history if p.triggered_surprise)
        return triggered / len(self.prediction_history)

    def mark_used(self, result_summary: str, error: str | None = None) -> None:
        """Update runtime state after tool execution."""
        self.last_used = datetime.now(timezone.utc).isoformat()
        self.last_result_summary = result_summary
        self.use_count += 1
        if error:
            self.failure_count += 1
            self.last_error = error

    def record_prediction(self, prediction: PredictionRecord) -> None:
        """Record a prediction-reality comparison and update contradiction state.

        This is the core of the disequilibrium loop:
        1. Append the prediction to the rolling window
        2. Recalculate contradiction count from window
        3. If contradiction_count exceeds limit, flag model as contradicted
        """
        self.prediction_history.append(prediction)
        self.contradiction_count = sum(1 for p in self.prediction_history if p.triggered_surprise)
        if self.contradiction_count >= SURPRISE_CONTRADICTION_LIMIT:
            self.model_contradicted = True

    def reset_model(self) -> None:
        """Reset the contradiction state after model repair."""
        self.prediction_history.clear()
        self.contradiction_count = 0
        self.model_contradicted = False
        self.failure_count = 0


class ToolSelfModel:
    """
    The agent's complete runtime self-model of its own tools.

    The agent queries this before every tool call.

    Usage:
        self_model = ToolSelfModel()
        self_model.register(my_tool_charter)
        entry = self_model.get("arif_mind_reason")
        if entry.has_permission_gap:
            return HOLD("Missing permissions: {}".format(entry.permission_gap))
    """

    def __init__(self):
        self._tools: dict[str, ToolSelfModelEntry] = {}
        self._agent_permissions: set[str] = set()

    def register(self, manifest: ToolManifest) -> None:
        """Register a tool with its manifest."""
        self._tools[manifest.tool_id] = ToolSelfModelEntry(manifest=manifest)

    def get(self, tool_id: str) -> ToolSelfModelEntry | None:
        """Get runtime state for a tool."""
        return self._tools.get(tool_id)

    def get_or_raise(self, tool_id: str) -> ToolSelfModelEntry:
        """Get runtime state or raise KeyError."""
        entry = self._tools.get(tool_id)
        if entry is None:
            raise KeyError(f"Tool {tool_id} not registered in self-model")
        return entry

    def list_all(self) -> list[ToolSelfModelEntry]:
        """List all registered tools."""
        return list(self._tools.values())

    def set_agent_permissions(self, permissions: set[str]) -> None:
        """Set the agent's actual permission set."""
        self._agent_permissions = permissions
        for entry in self._tools.values():
            entry.actual_permissions = sorted(
                permissions & set(entry.manifest.required_permissions)
            )

    def get_tools_by_domain(self, domain: str) -> list[ToolSelfModelEntry]:
        """Get all tools for a specific domain."""
        return [e for e in self._tools.values() if e.manifest.domain == domain]

    def get_tools_by_risk(self, tier: str) -> list[ToolSelfModelEntry]:
        """Get all tools matching a risk tier."""
        return [e for e in self._tools.values() if e.manifest.risk_tier == tier]

    def get_executable_tools(self) -> list[ToolSelfModelEntry]:
        """Get all tools that can be safely executed now."""
        return [e for e in self._tools.values() if e.is_safe_to_execute]

    def update_from_outcome(
        self,
        tool_id: str,
        result: dict[str, Any] | None = None,
        error: str | None = None,
        prediction: PredictionRecord | None = None,
    ) -> dict[str, Any]:
        """
        Update tool runtime state from an execution outcome.

        Called by EmbodiedTool.postflight() after every tool execution.
        This closes the feedback loop:

            PREDICT → EXECUTE → COMPARE → IF δ_surprise > threshold → FLAG CONTRADICTED

        When a tool's self-model is contradicted enough times, future
        preflight checks will return HOLD until the model is repaired.

        Args:
            tool_id: Canonical tool identifier
            result: Tool result dict containing verdict, confidence, etc.
            error: Error message if execution failed.
            prediction: The PredictionRecord from preflight, if one was made.

        Returns:
            Dict with delta_surprise, triggered_surprise, model_contradicted flags.
        """
        entry = self._tools.get(tool_id)
        if entry is None:
            return {"delta_surprise": 0.0, "triggered_surprise": False, "model_contradicted": False}

        if error:
            entry.mark_used(result_summary=f"ERROR: {error[:80]}", error=error)
            # An error with a confident prediction is high surprise
            if prediction and prediction.confidence > 0.5:
                prediction.compute_delta_surprise(
                    actual_outcome=f"ERROR: {error[:80]}",
                    model_importance=2.0,
                    critical_threshold=SURPRISE_CRITICAL_THRESHOLD,
                )
                entry.record_prediction(prediction)
            return {
                "delta_surprise": prediction.delta_surprise if prediction else 0.0,
                "triggered_surprise": prediction.triggered_surprise if prediction else False,
                "model_contradicted": entry.model_contradicted,
            }

        if result is None:
            entry.mark_used(result_summary="OK", error=None)
            if prediction:
                prediction.compute_delta_surprise(
                    actual_outcome="OK",
                    model_importance=0.5,
                    critical_threshold=SURPRISE_CRITICAL_THRESHOLD,
                )
                entry.record_prediction(prediction)
            return {
                "delta_surprise": prediction.delta_surprise if prediction else 0.0,
                "triggered_surprise": prediction.triggered_surprise if prediction else False,
                "model_contradicted": entry.model_contradicted,
            }

        verdict = result.get("verdict") or result.get("status") or "OK"
        raw_confidence = result.get("confidence") or result.get("result", {}).get("confidence")
        confidence_str = f"{raw_confidence:.2f}" if raw_confidence else "?"
        latency = result.get("latency_ms")

        summary_parts = [verdict]
        if confidence_str != "?":
            summary_parts.append(f"conf={confidence_str}")
        if latency:
            summary_parts.append(f"lat={latency:.0f}ms")

        entry.mark_used(result_summary=" | ".join(summary_parts), error=None)

        # ── PLASTICITY HANDLER: Compare prediction against reality ──
        if prediction:
            actual_outcome = str(verdict)
            model_importance = 1.0
            # Higher risk tools get higher model importance (bigger surprise when wrong)
            risk_map = {"T0": 0.3, "T1": 0.5, "T2": 1.0, "T3": 2.0, "T4": 3.0}
            model_importance = risk_map.get(entry.manifest.risk_tier, 1.0)

            # If tool had high confidence but result was low, that's HOLD-level surprise
            if raw_confidence is not None:
                result_confidence = float(raw_confidence)
                if prediction.confidence > 0.8 and result_confidence < 0.3:
                    model_importance *= 2.0

            prediction.compute_delta_surprise(
                actual_outcome=actual_outcome,
                model_importance=model_importance,
                critical_threshold=SURPRISE_CRITICAL_THRESHOLD,
            )
            entry.record_prediction(prediction)

            if prediction.triggered_surprise:
                logger.warning(
                    f"441_SURPRISE: tool={tool_id} "
                    f"δ={prediction.delta_surprise:.3f} "
                    f"predicted={prediction.predicted_outcome[:40]} "
                    f"actual={actual_outcome[:40]}"
                )

        return {
            "delta_surprise": prediction.delta_surprise if prediction else 0.0,
            "triggered_surprise": prediction.triggered_surprise if prediction else False,
            "model_contradicted": entry.model_contradicted,
        }

    def check_composition(self, tool_a: str, tool_b: str) -> tuple[bool, str]:
        """
        Check if tool_b can safely follow tool_a.

        Returns: (is_safe, reason)
        """
        entry_a = self.get(tool_a)
        if entry_a is None:
            return True, "tool_a not in model"

        if tool_b in entry_a.manifest.dangerous_compose_with:
            return False, f"{tool_b} is marked as dangerous to follow {tool_a}"

        if tool_b not in entry_a.manifest.safe_compose_with:
            return True, "no composition rule — proceeding with caution"

        return True, f"{tool_b} is explicitly safe to follow {tool_a}"

    def set_surprise_threshold(self, threshold: float) -> None:
        """Override the global SURPRISE_CRITICAL_THRESHOLD for all entries."""
        import arifosmcp.core.tool_self_model as tm

        tm.SURPRISE_CRITICAL_THRESHOLD = max(0.0, min(1.0, threshold))

    def get_contradicted_tools(self) -> list[ToolSelfModelEntry]:
        """Get all tools whose self-model has been contradicted."""
        return [e for e in self._tools.values() if e.model_contradicted]

    def get_prediction_summary(self) -> dict[str, Any]:
        """Return a summary of prediction health across all tools."""
        total = len(self._tools)
        contradicted = len(self.get_contradicted_tools())
        total_predictions = sum(len(e.prediction_history) for e in self._tools.values())
        total_surprises = sum(e.contradiction_count for e in self._tools.values())
        return {
            "total_tools": total,
            "contradicted_tools": contradicted,
            "contradiction_rate": round(contradicted / total, 4) if total else 0.0,
            "total_predictions": total_predictions,
            "total_surprises": total_surprises,
            "surprise_rate": (
                round(total_surprises / total_predictions, 4) if total_predictions else 0.0
            ),
        }

    def summary(self) -> dict[str, Any]:
        """Return a human-readable summary of the tool body."""
        by_domain: dict[str, int] = {}
        by_risk: dict[str, int] = {}
        executable = 0
        contradicted = 0

        for entry in self._tools.values():
            d = entry.manifest.domain
            by_domain[d] = by_domain.get(d, 0) + 1
            r = entry.manifest.risk_tier
            by_risk[r] = by_risk.get(r, 0) + 1
            if entry.is_safe_to_execute:
                executable += 1
            if entry.model_contradicted:
                contradicted += 1

        return {
            "total_tools": len(self._tools),
            "executable_now": executable,
            "contradicted": contradicted,
            "by_domain": by_domain,
            "by_risk": by_risk,
            "agent_permissions": sorted(self._agent_permissions),
        }


# Global singleton
_tool_self_model: ToolSelfModel | None = None


def get_tool_self_model() -> ToolSelfModel:
    """Get the global tool self-model singleton."""
    global _tool_self_model
    if _tool_self_model is None:
        _tool_self_model = ToolSelfModel()
    return _tool_self_model


def register_tool_in_self_model(manifest: ToolManifest) -> None:
    """Register a tool in the global self-model."""
    get_tool_self_model().register(manifest)


__all__ = [
    "BlastRadius",
    "CognitiveAxis",
    "COGNITIVE_AXIS_VECTORS",
    "ToolCapability",
    "ToolLimitation",
    "ToolFailureMode",
    "ToolManifest",
    "PredictionRecord",
    "ToolSelfModelEntry",
    "ToolSelfModel",
    "get_tool_self_model",
    "register_tool_in_self_model",
    "SURPRISE_CRITICAL_THRESHOLD",
    "SURPRISE_CONTRADICTION_LIMIT",
]
