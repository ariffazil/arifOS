from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DistilledKernelTemplate:
    invariants: tuple[str, ...]
    heuristics: tuple[str, ...]
    patterns: tuple[str, ...]
    safety_anchors: tuple[str, ...]
    thermodynamic_constraints: tuple[str, ...]


DEFAULT_DISTILLED_KERNEL = DistilledKernelTemplate(
    invariants=(
        "Every tool emits governed output through governed_return.",
        "Tool names remain underscore-only and immutable.",
        "Prompts and resources stay separate from governance logic.",
    ),
    heuristics=(
        "Prefer explicit state transitions over implicit mutation.",
        "Collapse ambiguity before execution, not after failure.",
        "Use vitality regressions to trigger SABAR before deployment.",
    ),
    patterns=(
        "Stage-local execute() surface with stable arguments.",
        "Append-only vitality and forget ledgers.",
        "Blind MCP bridge with logic delegated to tools and runtime helpers.",
    ),
    safety_anchors=(
        "F1 amanah_lock must remain true for production mutations.",
        "F2 truth_score stays above seal threshold for live execution.",
        "F3/F6 slippage escalates to HOLD_888 rather than silent degradation.",
    ),
    thermodynamic_constraints=(
        "delta_s should stay <= 0 for clear, governed flow.",
        "omega_0 should remain in the calibrated humility band.",
        "peace_squared should not drop below stable operating threshold.",
    ),
)


def load_distilled_kernel() -> DistilledKernelTemplate:
    return DEFAULT_DISTILLED_KERNEL
