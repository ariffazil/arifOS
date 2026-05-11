"""
arifOS Tool Self-Model — Runtime Tool Self-Awareness
═══════════════════════════════════════════════════════════════════════════════

The agent knows its own tools at runtime:
- What each tool can do
- What it cannot do
- What permissions it needs vs has
- What its failure modes are
- What tools compose safely with it

This is the embodied self-model for tools.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
    parameters: list[str] = Field(
        default_factory=list, description="Required parameter names"
    )
    output_fields: list[str] = Field(
        default_factory=list, description="Output fields produced"
    )


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

    # Example
    example_params: dict[str, Any] | None = Field(
        default=None, description="Example parameters"
    )

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


class ToolSelfModelEntry(BaseModel):
    """
    Runtime state of a single tool in the agent's body.

    Tracks what the agent actually knows about this tool.
    """

    manifest: ToolManifest = Field(description="Tool's self-declaration")
    last_used: str | None = Field(default=None, description="ISO timestamp of last use")
    last_result_summary: str | None = Field(
        default=None, description="One-line summary of last result"
    )
    use_count: int = Field(default=0, description="Total times used")
    failure_count: int = Field(default=0, description="Times this tool failed")
    last_error: str | None = Field(default=None, description="Last error message")

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
        """Can this tool be executed safely right now?"""
        return not self.has_permission_gap and self.failure_count < 3

    def mark_used(self, result_summary: str, error: str | None = None) -> None:
        """Update runtime state after tool execution."""
        self.last_used = datetime.now(timezone.utc).isoformat()
        self.last_result_summary = result_summary
        self.use_count += 1
        if error:
            self.failure_count += 1
            self.last_error = error


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
    ) -> None:
        """
        Update tool runtime state from an execution outcome.

        Called by EmbodiedTool.postflight() after every tool execution.
        This closes the feedback loop: execute → update self-model → future
        preflight decisions are informed by past performance.

        Args:
            tool_id: Canonical tool identifier
            result: Tool result dict. For arif_mind_reason this contains
                verdict, confidence, synthesis. Used to build result_summary.
            error: Error message if execution failed.
        """
        entry = self._tools.get(tool_id)
        if entry is None:
            return

        if error:
            entry.mark_used(result_summary=f"ERROR: {error[:80]}", error=error)
            return

        if result is None:
            entry.mark_used(result_summary="OK", error=None)
            return

        verdict = result.get("verdict") or result.get("status") or "OK"
        confidence = result.get("confidence") or result.get("result", {}).get(
            "confidence"
        )
        confidence_str = f"{confidence:.2f}" if confidence else "?"
        latency = result.get("latency_ms")

        summary_parts = [verdict]
        if confidence_str != "?":
            summary_parts.append(f"conf={confidence_str}")
        if latency:
            summary_parts.append(f"lat={latency:.0f}ms")

        entry.mark_used(result_summary=" | ".join(summary_parts), error=None)

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

    def summary(self) -> dict[str, Any]:
        """Return a human-readable summary of the tool body."""
        by_domain: dict[str, int] = {}
        by_risk: dict[str, int] = {}
        executable = 0

        for entry in self._tools.values():
            d = entry.manifest.domain
            by_domain[d] = by_domain.get(d, 0) + 1
            r = entry.manifest.risk_tier
            by_risk[r] = by_risk.get(r, 0) + 1
            if entry.is_safe_to_execute:
                executable += 1

        return {
            "total_tools": len(self._tools),
            "executable_now": executable,
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
    "ToolCapability",
    "ToolLimitation",
    "ToolFailureMode",
    "ToolManifest",
    "ToolSelfModelEntry",
    "ToolSelfModel",
    "get_tool_self_model",
    "register_tool_in_self_model",
]
