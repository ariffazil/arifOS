"""
arifOS Federation — G02 Kernel Router
=====================================
Mandatory hub for all cross-axis calls.
Enforces Ω_ortho >= 0.95 correlation checks.

All perception/transformation/valuation/governance/execution/meta calls
MUST route through this router before execution.

Philosophy:
- No agent calls another agent directly
- All calls go through G02 for routing + correlation tracking
- G02 returns routing decision + correlation score
- Caller executes via the specified lane
"""

from __future__ import annotations

from typing import Any, Literal
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

from fastmcp import FastMCP


# =============================================================================
# AXIS DEFINITIONS
# =============================================================================


class Axis(str, Enum):
    PERCEPTION = "P"
    TRANSFORMATION = "T"
    VALUATION = "V"
    GOVERNANCE = "G"
    EXECUTION = "E"
    META = "M"


# =============================================================================
# CROSS-AXIS CALL GRAPH (from mcp-manifest-v2.json)
# =============================================================================

ALLOWED_CALLS: dict[str, set[str]] = {
    "P": {"T", "G"},  # Perception can call Transformation and Governance
    "T": {"V", "M"},  # Transformation can call Valuation and Meta
    "V": {"G"},  # Valuation can call Governance only
    "G": {"E", "M"},  # Governance can call Execution and Meta
    "E": set(),  # Execution cannot call anyone
    "M": {"P", "G"},  # Meta can call Perception and Governance
}


# =============================================================================
# Ω_ORTHO CORRELATION MATRIX
# =============================================================================

ORTHOGONALITY_MATRIX: dict[str, dict[str, int]] = {
    "P": {"P": 0, "T": 1, "V": 0, "G": 1, "E": 0, "M": 0},
    "T": {"P": 0, "T": 0, "V": 1, "G": 0, "E": 0, "M": 1},
    "V": {"P": 0, "T": 0, "V": 0, "G": 1, "E": 0, "M": 0},
    "G": {"P": 0, "T": 0, "V": 0, "G": 0, "E": 1, "M": 1},
    "E": {"P": 0, "T": 0, "V": 0, "G": 0, "E": 0, "M": 0},
    "M": {"P": 1, "T": 0, "V": 0, "G": 1, "E": 0, "M": 0},
}


# =============================================================================
# ROUTING REQUEST/RESPONSE MODELS
# =============================================================================


class RouteRequest(BaseModel):
    caller_agent: str = Field(description="Agent ID making the call (e.g., 'P01')")
    target_agent: str = Field(description="Agent ID being called (e.g., 'T01')")
    input_data: dict[str, Any] = Field(description="Input to pass to target agent")
    correlation_context: list[Any] = Field(
        default_factory=list, description="Recent agent outputs for correlation check"
    )


class RouteResponse(BaseModel):
    approved: bool = Field(description="Whether the call is approved")
    target_agent: str = Field(description="Agent to call")
    lane: str = Field(description="Execution lane")
    omega_ortho: float = Field(description="Computed orthogonality score")
    correlation_detected: bool = Field(description="Whether harmful correlation detected")
    reason: str = Field(description="Approval/rejection reason")


# =============================================================================
# CALL TRACKER (for Ω_ortho computation)
# =============================================================================


@dataclass
class CallRecord:
    caller: str
    target: str
    axis_caller: str
    axis_target: str
    omega: float
    approved: bool


class CorrelationTracker:
    """Tracks agent calls and computes Ω_ortho correlation."""

    def __init__(self, max_history: int = 100):
        self.history: list[CallRecord] = []
        self.max_history = max_history

    def record(self, caller: str, target: str, approved: bool) -> float:
        """Record a call and return the computed Ω_ortho."""
        axis_caller = caller[0]
        axis_target = target[0]

        if axis_caller in ORTHOGONALITY_MATRIX and axis_target in ORTHOGONALITY_MATRIX[axis_caller]:
            omega = ORTHOGONALITY_MATRIX[axis_caller][axis_target]
        else:
            omega = 0.0

        record = CallRecord(
            caller=caller,
            target=target,
            axis_caller=axis_caller,
            axis_target=axis_target,
            omega=omega,
            approved=approved,
        )
        self.history.append(record)

        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        return self.compute_omega()

    def compute_omega(self) -> float:
        """Compute overall Ω_ortho from call history."""
        if not self.history:
            return 1.0

        total = len(self.history)
        orthogonal = sum(1 for r in self.history if r.omega == 1)

        return orthogonal / total if total > 0 else 1.0

    def check_correlation(self, caller: str, target: str) -> tuple[bool, float]:
        """Check if a proposed call would create harmful correlation."""
        axis_caller = caller[0]
        axis_target = target[0]

        # Check allowed calls graph
        allowed = ALLOWED_CALLS.get(axis_caller, set())
        if axis_target not in allowed and axis_caller != axis_target:
            return True, 0.0

        # Check orthogonality matrix
        if axis_caller in ORTHOGONALITY_MATRIX:
            if axis_target in ORTHOGONALITY_MATRIX[axis_caller]:
                omega = ORTHOGONALITY_MATRIX[axis_caller][axis_target]
                if omega == 0:
                    return True, 0.0

        return False, ORTHOGONALITY_MATRIX.get(axis_caller, {}).get(axis_target, 0.0)


# =============================================================================
# G02 KERNEL ROUTER IMPLEMENTATION
# =============================================================================

_tracker = CorrelationTracker()


def route_call(request: RouteRequest) -> RouteResponse:
    """
    G02 Kernel Router — Mandatory routing for all cross-axis calls.

    Rules:
    1. Extract axis from caller and target agent IDs (first character)
    2. Check ALLOWED_CALLS graph
    3. Compute Ω_ortho from ORTHOGONALITY_MATRIX
    4. If correlation detected OR call not allowed → reject
    5. If approved → record call and return routing info
    """
    caller_axis = request.caller_agent[0]
    target_axis = request.target_agent[0]

    # Check for same-axis calls (always allowed within axis)
    if caller_axis == target_axis:
        correlation, omega = _tracker.check_correlation(request.caller_agent, request.target_agent)
        _tracker.record(request.caller_agent, request.target_agent, approved=True)
        return RouteResponse(
            approved=True,
            target_agent=request.target_agent,
            lane=f"{target_axis}-lane",
            omega_ortho=omega,
            correlation_detected=False,
            reason=f"Same-axis call ({caller_axis}), allowed",
        )

    # Check cross-axis allowed calls
    allowed_targets = ALLOWED_CALLS.get(caller_axis, set())
    if target_axis not in allowed_targets:
        _tracker.record(request.caller_agent, request.target_agent, approved=False)
        return RouteResponse(
            approved=False,
            target_agent=request.target_agent,
            lane="rejected",
            omega_ortho=0.0,
            correlation_detected=True,
            reason=f"Axis {caller_axis} cannot call axis {target_axis}. Allowed: {allowed_targets}",
        )

    # Check correlation
    correlation_detected, omega = _tracker.check_correlation(
        request.caller_agent, request.target_agent
    )

    if correlation_detected or omega < 0.95:
        _tracker.record(request.caller_agent, request.target_agent, approved=False)
        return RouteResponse(
            approved=False,
            target_agent=request.target_agent,
            lane="rejected",
            omega_ortho=omega,
            correlation_detected=True,
            reason=f"Correlation detected. Ω_ortho = {omega} < 0.95 threshold",
        )

    # Approved
    _tracker.record(request.caller_agent, request.target_agent, approved=True)
    return RouteResponse(
        approved=True,
        target_agent=request.target_agent,
        lane=f"{target_axis}-lane",
        omega_ortho=omega,
        correlation_detected=False,
        reason="Call approved",
    )


def get_omega_status() -> dict[str, Any]:
    """Get current Ω_ortho status."""
    return {
        "omega_ortho": _tracker.compute_omega(),
        "call_history_count": len(_tracker.history),
        "allowed_calls": dict(ALLOWED_CALLS),
        "orthogonality_matrix": ORTHOGONALITY_MATRIX,
    }


# =============================================================================
# FASTMCP INTEGRATION
# =============================================================================


def create_router_mcp() -> FastMCP:
    """Create FastMCP server with G02 Kernel Router."""
    mcp = FastMCP("arifOS-G02-Router")

    @mcp.tool(tags={"governance", "public"})
    def G02_route(
        caller_agent: str,
        target_agent: str,
        input_data: dict[str, Any],
        correlation_context: list[Any] | None = None,
    ) -> dict[str, Any]:
        """
        G02 Kernel Router — Mandatory hub for all cross-axis calls.

        All perception/transformation/valuation/governance/execution/meta calls
        MUST route through this router before execution.

        Returns:
            approved: bool - Whether the call is approved
            target_agent: str - Agent to call
            lane: str - Execution lane
            omega_ortho: float - Computed orthogonality score
            correlation_detected: bool - Whether harmful correlation detected
            reason: str - Approval/rejection reason
        """
        request = RouteRequest(
            caller_agent=caller_agent,
            target_agent=target_agent,
            input_data=input_data,
            correlation_context=correlation_context or [],
        )
        response = route_call(request)
        return response.model_dump()

    @mcp.tool(tags={"governance", "public"})
    def G02_omega_status() -> dict[str, Any]:
        """
        Get current Ω_ortho status and call history.

        Returns:
            omega_ortho: float - Current orthogonality score
            call_history_count: int - Number of recorded calls
            allowed_calls: dict - Cross-axis call permissions
            orthogonality_matrix: dict - Full orthogonality matrix
        """
        return get_omega_status()

    @mcp.tool(tags={"governance", "public"})
    def G02_validate_axis_call(
        caller_axis: str,
        target_axis: str,
    ) -> dict[str, Any]:
        """
        Validate if a cross-axis call is allowed without recording it.

        Args:
            caller_axis: Single letter axis (P/T/V/G/E/M)
            target_axis: Single letter axis (P/T/V/G/E/M)

        Returns:
            allowed: bool
            reason: str
            omega: float
        """
        allowed = ALLOWED_CALLS.get(caller_axis, set())
        if target_axis not in allowed:
            return {
                "allowed": False,
                "reason": f"Axis {caller_axis} cannot call axis {target_axis}",
                "omega": 0.0,
            }

        omega = ORTHOGONALITY_MATRIX.get(caller_axis, {}).get(target_axis, 0.0)
        if omega == 0:
            return {
                "allowed": False,
                "reason": f"Non-orthogonal call: {caller_axis} → {target_axis}",
                "omega": 0.0,
            }

        return {
            "allowed": True,
            "reason": f"Orthogonal call: {caller_axis} → {target_axis}",
            "omega": omega,
        }

    return mcp


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    mcp = create_router_mcp()
    mcp.run()
