"""
Endpoint Drift Detector — arifOS Federation
════════════════════════════════════════════

P0.3 from the 2026-06-09 readiness audit:
"Canonical manifest must be shipped. Runtime surface must match declared
MCP surface. Drift should produce HOLD, not silent mismatch."

This module reads the canonical mcp_surface.yaml and compares it against
the LIVE runtime surface. Any drift → automatic HOLD degradation.

NO STATIC TRUTH — the manifest is verified against live probes every check cycle.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum

import yaml


class DriftVerdict(StrEnum):
    CLEAN = "CLEAN"  # No drift — manifest matches runtime
    WARNING = "WARNING"  # Minor drift — tool count mismatch
    HOLD = "HOLD"  # Significant drift — tool missing/extra
    VOID = "VOID"  # Catastrophic drift — surface broken


@dataclass
class DriftReport:
    """Result of comparing canonical manifest against live runtime."""

    verdict: DriftVerdict = DriftVerdict.CLEAN
    manifest_tool_count: int = 0
    runtime_tool_count: int = 0
    missing_tools: list[str] = field(default_factory=list)
    extra_tools: list[str] = field(default_factory=list)
    manifest_port: int = 0
    runtime_port: int = 0
    port_mismatch: bool = False
    checked_at: float = field(default_factory=time.time)
    error: str | None = None

    @property
    def has_drift(self) -> bool:
        return self.verdict != DriftVerdict.CLEAN

    @property
    def summary(self) -> str:
        if self.error:
            return f"DRIFT_ERROR: {self.error}"
        if self.verdict == DriftVerdict.CLEAN:
            return f"DRIFT_CLEAN: {self.runtime_tool_count}/{self.manifest_tool_count} tools match"
        if self.verdict == DriftVerdict.WARNING:
            return (
                f"DRIFT_WARNING: manifest={self.manifest_tool_count}, "
                f"runtime={self.runtime_tool_count}"
            )
        if self.missing_tools:
            return f"DRIFT_HOLD: missing tools: {self.missing_tools}"
        if self.extra_tools:
            return f"DRIFT_HOLD: extra tools in runtime: {self.extra_tools}"
        if self.port_mismatch:
            return f"DRIFT_HOLD: port mismatch manifest={self.manifest_port} runtime={self.runtime_port}"
        return f"DRIFT_{self.verdict.value}"


def load_manifest(manifest_path: str = "contracts/mcp_surface.yaml") -> dict:
    """Load the canonical MCP surface manifest."""
    with open(manifest_path) as f:
        return yaml.safe_load(f)


def check_drift(
    manifest: dict,
    runtime_tool_names: list[str],
    runtime_port: int,
) -> DriftReport:
    """Compare canonical manifest against live runtime surface.

    Args:
        manifest: Parsed mcp_surface.yaml
        runtime_tool_names: List of tool names currently registered
        runtime_port: Actual port the server is listening on

    Returns:
        DriftReport with verdict and details.
    """
    manifest_tools = set(manifest.get("canonical_tools", []))
    manifest_port = manifest.get("runtime_surface", {}).get("primary_port", 0)
    runtime_tools = set(runtime_tool_names)

    report = DriftReport(
        manifest_tool_count=len(manifest_tools),
        runtime_tool_count=len(runtime_tools),
        manifest_port=manifest_port,
        runtime_port=runtime_port,
        port_mismatch=(manifest_port != runtime_port),
    )

    missing = manifest_tools - runtime_tools
    extra = runtime_tools - manifest_tools

    report.missing_tools = sorted(missing)
    report.extra_tools = sorted(extra)

    # Determine verdict
    if missing:
        # Missing canonical tools is a HOLD — the surface is degraded
        report.verdict = DriftVerdict.HOLD
    elif extra:
        # Extra tools in runtime is a WARNING — possible unregistered tool
        report.verdict = DriftVerdict.WARNING
    elif report.port_mismatch:
        report.verdict = DriftVerdict.WARNING
    else:
        report.verdict = DriftVerdict.CLEAN

    return report
