"""
arifosmcp.kernel.substrate_readiness — AGI Substrate Readiness Gate

No substrate proof, no AGI claim.

This is NOT an AGI claim module. It is a machine-checkable verification
that the kernel's substrate is intact — that tools exist, boundaries hold,
authority is enforced, and nothing silently falls back to generic execution.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import dataclasses
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class ReadinessCheck:
    """A single substrate readiness check with verdict."""

    name: str
    description: str
    passed: bool
    details: str | None = None
    severity: str = "info"  # info | warning | critical


@dataclasses.dataclass(frozen=True)
class SubstrateReadinessReport:
    """Complete substrate readiness report."""

    checks: list[ReadinessCheck]
    passed: int
    failed: int
    critical_failures: int
    overall_verdict: str  # PASS | HOLD | FAIL

    def to_dict(self) -> dict[str, Any]:
        return {
            "substrate_gate": self.overall_verdict,
            "passed": self.passed,
            "failed": self.failed,
            "critical_failures": self.critical_failures,
            "checks": [
                {
                    "name": c.name,
                    "description": c.description,
                    "passed": c.passed,
                    "severity": c.severity,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def assess_substrate_readiness() -> SubstrateReadinessReport:
    """
    Run all substrate readiness checks against the live kernel.

    Returns a structured report. Never raises — all failures are captured
    as check results with severity grading.
    """
    checks: list[ReadinessCheck] = []
    passed = 0
    failed = 0
    critical_failures = 0

    # ── Check 1: Public MCP surface is exactly canonical 7 ───────────────
    try:
        from arifosmcp.runtime.public_surface import (
            CANONICAL_7,
            public_tool_names_for_mode,
        )

        public_tools = set(public_tool_names_for_mode(None))
        expected = set(CANONICAL_7)
        if public_tools == expected:
            checks.append(
                ReadinessCheck(
                    name="public_surface_exact",
                    description="Default public tools/list returns exactly CANONICAL_7",
                    passed=True,
                    severity="critical",
                )
            )
            passed += 1
        else:
            extra = public_tools - expected
            missing = expected - public_tools
            details = []
            if extra:
                details.append(f"Extra: {extra}")
            if missing:
                details.append(f"Missing: {missing}")
            checks.append(
                ReadinessCheck(
                    name="public_surface_exact",
                    description="Default public tools/list must return exactly CANONICAL_7",
                    passed=False,
                    severity="critical",
                    details="; ".join(details),
                )
            )
            failed += 1
            critical_failures += 1
    except Exception as e:
        checks.append(
            ReadinessCheck(
                name="public_surface_exact",
                description="Default public tools/list check failed to run",
                passed=False,
                severity="critical",
                details=str(e),
            )
        )
        failed += 1
        critical_failures += 1

    # ── Check 2: Forbidden sovereign machinery does not leak ─────────────
    try:
        from arifosmcp.runtime.public_surface import (
            CANONICAL_LONG_NAME_ALIASES,
            public_tool_names_for_mode,
        )

        public_tools = set(public_tool_names_for_mode(None))
        forbidden = {
            "arif_bridge_connect",
            "arif_gateway_connect",
            "arif_forge",
            "arif_forge_execute",
            "arif_memory",
            "arif_memory_recall",
            "arif_vault_seal",
            "hermes_vault_query",
            "arif_canary",
            "arif_conformance_report",
            "arif_judge_deliberate",
            "arif_session_init",
        }
        leaked = public_tools & forbidden
        alias_leaked = public_tools & set(CANONICAL_LONG_NAME_ALIASES)
        total_leaked = leaked | alias_leaked

        if not total_leaked:
            checks.append(
                ReadinessCheck(
                    name="forbidden_tools_blocked",
                    description="No forbidden or alias tools leaked into public surface",
                    passed=True,
                    severity="critical",
                )
            )
            passed += 1
        else:
            checks.append(
                ReadinessCheck(
                    name="forbidden_tools_blocked",
                    description="Forbidden or alias tools must not leak into public surface",
                    passed=False,
                    severity="critical",
                    details=f"Leaked: {total_leaked}",
                )
            )
            failed += 1
            critical_failures += 1
    except Exception as e:
        checks.append(
            ReadinessCheck(
                name="forbidden_tools_blocked",
                description="Forbidden tools check failed to run",
                passed=False,
                severity="critical",
                details=str(e),
            )
        )
        failed += 1
        critical_failures += 1

    # ── Check 3: Capability graph covers the core seven ──────────────────
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        canonical_names = set(CANONICAL_TOOLS.keys())
        expected_core = {
            "arif_init",
            "arif_observe",
            "arif_think",
            "arif_route",
            "arif_judge",
            "arif_act",
            "arif_seal",
        }
        missing_core = expected_core - canonical_names
        if not missing_core:
            checks.append(
                ReadinessCheck(
                    name="capability_graph_core",
                    description="All 7 core tools registered in CANONICAL_TOOLS",
                    passed=True,
                    severity="critical",
                )
            )
            passed += 1
        else:
            checks.append(
                ReadinessCheck(
                    name="capability_graph_core",
                    description="All 7 core tools must be registered",
                    passed=False,
                    severity="critical",
                    details=f"Missing: {missing_core}",
                )
            )
            failed += 1
            critical_failures += 1
    except Exception as e:
        checks.append(
            ReadinessCheck(
                name="capability_graph_core",
                description="Capability graph check failed to run",
                passed=False,
                severity="critical",
                details=str(e),
            )
        )
        failed += 1
        critical_failures += 1

    # ── Check 4: Only arif_act and arif_seal may commit irreversible ─────
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        irreversible_public = [
            name
            for name, spec in CANONICAL_TOOLS.items()
            if spec.get("access") in ("public", "authenticated", "sovereign")
            and spec.get("irreversible", False)
        ]
        expected_irreversible = {"arif_act", "arif_seal"}
        actual_irreversible = set(irreversible_public)

        if actual_irreversible == expected_irreversible:
            checks.append(
                ReadinessCheck(
                    name="irreversible_tools_limited",
                    description="Only arif_act and arif_seal are public-irreversible",
                    passed=True,
                    severity="critical",
                )
            )
            passed += 1
        else:
            extra = actual_irreversible - expected_irreversible
            checks.append(
                ReadinessCheck(
                    name="irreversible_tools_limited",
                    description="Only arif_act and arif_seal should be public-irreversible",
                    passed=False,
                    severity="critical",
                    details=f"Unexpected irreversible: {extra}" if extra else "Missing expected",
                )
            )
            failed += 1
            critical_failures += 1
    except Exception as e:
        checks.append(
            ReadinessCheck(
                name="irreversible_tools_limited",
                description="Irreversible tools check failed to run",
                passed=False,
                severity="critical",
                details=str(e),
            )
        )
        failed += 1
        critical_failures += 1

    # ── Check 5: Mutating capabilities require audit trail ───────────────
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        public_mutating = [
            name
            for name, spec in CANONICAL_TOOLS.items()
            if spec.get("access") in ("public", "authenticated", "sovereign")
            and spec.get("irreversible", False)
        ]
        # Check that all public-mutating tools have L11_AUDIT in floors
        missing_audit = []
        for name in public_mutating:
            spec = CANONICAL_TOOLS.get(name, {})
            floors = spec.get("floors", [])
            floor_values = {str(f) for f in floors}
            if "L11" not in floor_values:
                missing_audit.append(name)

        if not missing_audit:
            checks.append(
                ReadinessCheck(
                    name="mutating_tools_audited",
                    description="All public-mutating tools have audit floor (L11)",
                    passed=True,
                    severity="warning",
                )
            )
            passed += 1
        else:
            checks.append(
                ReadinessCheck(
                    name="mutating_tools_audited",
                    description="All public-mutating tools should have audit floors",
                    passed=False,
                    severity="warning",
                    details=f"Missing audit floor: {missing_audit}",
                )
            )
            failed += 1
    except Exception as e:
        checks.append(
            ReadinessCheck(
                name="mutating_tools_audited",
                description="Mutating tools audit check failed to run",
                passed=False,
                severity="warning",
                details=str(e),
            )
        )
        failed += 1

    # ── Check 6: Irreversible tools require witness or HOLD gate ─────────
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        irreversible_tools = [
            name for name, spec in CANONICAL_TOOLS.items() if spec.get("irreversible", False)
        ]
        # Verify irreversible tools have L13_SOVEREIGN or similar high floors
        for name in irreversible_tools:
            spec = CANONICAL_TOOLS.get(name, {})
            floors = spec.get("floors", [])
            floor_str = " ".join(str(f) for f in floors)
            if "SOVEREIGN" in floor_str or "L13" in floor_str or "HOLD" in floor_str:
                continue
            checks.append(
                ReadinessCheck(
                    name=f"irreversible_gate_{name}",
                    description=f"Irreversible tool {name} needs sovereign or HOLD gate",
                    passed=False,
                    severity="warning",
                    details=f"Floors: {floors}",
                )
            )
            failed += 1

        # If no issues found, report a single passing check for all irreversible
        if not [c for c in checks if c.name.startswith("irreversible_gate_")]:
            checks.append(
                ReadinessCheck(
                    name="irreversible_tools_gated",
                    description="All irreversible tools have sovereign/HOLD gates",
                    passed=True,
                    severity="warning",
                )
            )
            passed += 1
    except Exception as e:
        checks.append(
            ReadinessCheck(
                name="irreversible_tools_gated",
                description="Irreversible tools gate check failed to run",
                passed=False,
                severity="warning",
                details=str(e),
            )
        )
        failed += 1

    # ── Check 7: All tools have concrete implementations (no generic fallback) ─
    try:
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS, _RUNTIME_DIAGNOSTIC_HANDLERS
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        # Check canonical tools have handlers. DIAGNOSTIC_TOOLS use multiple
        # registration paths (@mcp.tool, canary_multimode.py, server.py).
        # Only CANONICAL_TOOLS are validated here.
        missing_handlers = []
        for name in CANONICAL_TOOLS:
            has_handler = name in _CANONICAL_HANDLERS or name in _RUNTIME_DIAGNOSTIC_HANDLERS
            if not has_handler:
                try:
                    from arifosmcp.tools.embodied import ARIFOS_TOOL_CHARTERS

                    if name in ARIFOS_TOOL_CHARTERS:
                        has_handler = True
                except ImportError:
                    pass
            if not has_handler:
                missing_handlers.append(name)

        if not missing_handlers:
            checks.append(
                ReadinessCheck(
                    name="no_generic_fallback",
                    description="All registered tools have concrete handler implementations",
                    passed=True,
                    severity="critical",
                )
            )
            passed += 1
        else:
            checks.append(
                ReadinessCheck(
                    name="no_generic_fallback",
                    description="All registered tools must have concrete handlers",
                    passed=False,
                    severity="critical",
                    details=f"Missing handlers: {missing_handlers}",
                )
            )
            failed += 1
            critical_failures += 1
    except Exception as e:
        checks.append(
            ReadinessCheck(
                name="no_generic_fallback",
                description="Handler implementation check failed to run",
                passed=False,
                severity="critical",
                details=str(e),
            )
        )
        failed += 1
        critical_failures += 1

    # ── Compute overall verdict ───────────────────────────────────────────
    if critical_failures > 0:
        overall = "FAIL"
    elif failed > 0:
        overall = "HOLD"
    else:
        overall = "PASS"

    return SubstrateReadinessReport(
        checks=checks,
        passed=passed,
        failed=failed,
        critical_failures=critical_failures,
        overall_verdict=overall,
    )
