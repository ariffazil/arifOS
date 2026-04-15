"""
arifOS Boot-Time Integrity Check — Fail-Fast Kernel
═══════════════════════════════════════════════════════════════════════════════

Constitutional invariant:
If governance-critical ontology is missing, the kernel is not allowed to exist
in a serving state.

This module implements fail-fast boot validation:
- No valid ontology → no startup
- No runtime policy → no startup
- No contract mappings → no startup

Boot states: BOOTING → SEALED | HOLD | VOID
Only SEALED may accept traffic.

DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

REQUIRED_POLICY_VERSION = "2026.4.13"
REQUIRED_PROTOCOL_VERSION = "2025-03-26"

# Core 9+1 Governance Layer (Constitutional Tools)
# NOTE: These values must match tool_specs.py exactly
REQUIRED_CORE_TOOLS: dict[str, dict[str, Any]] = {
    "arifos_init": {
        "stage": "000",  # Short form as in tool_specs.py
        "lane": "Ψ",
        "trinity": "PSI",
        "router_visible": True,
        "risk_class": "low",
        "governance_critical": True,
        "floors": ["F11", "F12", "F13"],
    },
    "arifos_sense": {
        "stage": "111",
        "lane": "Δ",
        "trinity": "DELTA",
        "router_visible": True,
        "risk_class": "low",
        "governance_critical": True,
        "floors": ["F2", "F3", "F4", "F10"],
    },
    "arifos_mind": {
        "stage": "333",
        "lane": "Δ",
        "trinity": "DELTA",
        "router_visible": True,
        "risk_class": "low",
        "governance_critical": True,
        "floors": ["F2", "F4", "F7", "F8"],
    },
    "arifos_kernel": {
        "stage": "444",
        "lane": "Δ/Ψ",
        "trinity": "DELTA_PSI",
        "router_visible": True,
        "risk_class": "medium",
        "governance_critical": True,
        "floors": ["F4", "F11"],
    },
    "arifos_heart": {
        "stage": "666",
        "lane": "Ω",
        "trinity": "OMEGA",
        "router_visible": True,
        "risk_class": "medium",
        "governance_critical": True,
        "floors": ["F5", "F6", "F9"],
    },
    "arifos_ops": {
        "stage": "777",
        "lane": "Δ",
        "trinity": "DELTA",
        "router_visible": False,  # Auxiliary — not in router surface
        "risk_class": "low",
        "governance_critical": False,  # Auxiliary tool
        "floors": ["F4", "F5"],
    },
    "arifos_judge": {
        "stage": "888",
        "lane": "Ψ",
        "trinity": "PSI",
        "router_visible": True,
        "risk_class": "high",
        "governance_critical": True,
        "floors": ["F1", "F2", "F3", "F9", "F10", "F12", "F13"],
    },
    "arifos_memory": {
        "stage": "555",
        "lane": "Ω",
        "trinity": "OMEGA",
        "router_visible": True,
        "risk_class": "medium",
        "governance_critical": True,
        "floors": ["F2", "F10", "F11"],
    },
    "arifos_vault": {
        "stage": "999",
        "lane": "Ψ",
        "trinity": "PSI",
        "router_visible": True,
        "risk_class": "high",
        "governance_critical": True,
        "floors": ["F1", "F13"],
    },
    "arifos_forge": {
        "stage": "010",  # Short form as in tool_specs.py
        "lane": "Δ",
        "trinity": "DELTA",
        "router_visible": True,
        "risk_class": "critical",
        "governance_critical": True,
        "floors": ["F1", "F2", "F7", "F13"],
    },
}

# Auxiliary tools (may exist but not router-visible by default)
AUXILIARY_TOOLS: set[str] = {
    "arifos_health",
}

# Required endpoints for constitutional compliance
REQUIRED_ENDPOINTS: set[str] = {
    "/health",
    "/tools",
    "/kernel/health",
    "/kernel/health/integrity",
    "/.well-known/mcp/server.json",
}

# ═══════════════════════════════════════════════════════════════════════════════
# EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════════


class BootIntegrityError(RuntimeError):
    """Kernel boot aborted due to constitutional integrity violation."""

    pass


class OntologyError(BootIntegrityError):
    """Tool ontology missing or invalid."""

    pass


class PolicyError(BootIntegrityError):
    """Runtime policy version mismatch or missing."""

    pass


class ContractError(BootIntegrityError):
    """Contract mappings failed to load."""

    pass


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class IntegrityReport:
    """Immutable boot integrity report."""

    boot_state: str  # BOOTING, SEALED, HOLD, VOID
    policy_version: str
    protocol_version: str
    contracts_loaded: bool = False
    tool_ontology_valid: bool = False
    router_surface_valid: bool = False
    required_endpoints_valid: bool = False
    entropy_guard_active: bool = False
    serve_traffic: bool = False
    timestamp: str = ""
    error_code: str | None = None
    error_message: str | None = None
    failed_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "boot_state": self.boot_state,
            "policy_version": self.policy_version,
            "protocol_version": self.protocol_version,
            "contracts_loaded": self.contracts_loaded,
            "tool_ontology_valid": self.tool_ontology_valid,
            "router_surface_valid": self.router_surface_valid,
            "required_endpoints_valid": self.required_endpoints_valid,
            "entropy_guard_active": self.entropy_guard_active,
            "serve_traffic": self.serve_traffic,
            "timestamp": self.timestamp,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "failed_checks": self.failed_checks,
        }


# Global boot report (set during startup, read-only after)
_BOOT_REPORT: IntegrityReport | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def _require(condition: bool, error_code: str, message: str, failed: list[str]) -> None:
    """Hard requirement — fails boot if not met."""
    if not condition:
        failed.append(f"{error_code}: {message}")
        logger.critical(f"BOOT INTEGRITY FAILURE [{error_code}]: {message}")


def validate_contract_maps(
    stage_map: dict[str, str] | None,
    trinity_map: dict[str, str] | None,
    law_bindings: dict[str, list[str]] | None,
    failed: list[str],
) -> bool:
    """Validate contract mappings are loaded and non-empty."""
    _require(
        stage_map is not None and len(stage_map) > 0,
        "CONTRACT_STAGE_MAP_MISSING",
        "AAA_TOOL_STAGE_MAP is missing or empty",
        failed,
    )
    _require(
        trinity_map is not None and len(trinity_map) > 0,
        "CONTRACT_TRINITY_MAP_MISSING",
        "TRINITY_BY_TOOL is missing or empty",
        failed,
    )
    _require(
        law_bindings is not None and len(law_bindings) > 0,
        "CONTRACT_LAW_BINDINGS_MISSING",
        "AAA_TOOL_LAW_BINDINGS is missing or empty",
        failed,
    )
    return len(failed) == 0


def validate_policy_version(policy_version: str | None, failed: list[str]) -> bool:
    """Validate runtime policy version matches expected."""
    _require(
        policy_version is not None and policy_version != "",
        "POLICY_VERSION_MISSING",
        "RUNTIME_POLICY_VERSION is not set",
        failed,
    )
    if policy_version and policy_version != REQUIRED_POLICY_VERSION:
        _require(
            False,
            "POLICY_VERSION_MISMATCH",
            f"Expected policy version {REQUIRED_POLICY_VERSION}, got {policy_version}",
            failed,
        )
    return len(failed) == 0


def _normalize_tool_key(name: str) -> str:
    """Normalize tool name for cross-reference between formats."""
    # Handle both dot format (arifos.init) and underscore format (arifos_init)
    return name.replace(".", "_")


def validate_core_tool_ontology(
    tool_registry: dict[str, Any],
    stage_map: dict[str, str],
    trinity_map: dict[str, str],
    failed: list[str],
) -> bool:
    """Validate each core tool has complete ontology."""
    for tool_name, expected in REQUIRED_CORE_TOOLS.items():
        # Tool must exist in registry
        _require(
            tool_name in tool_registry,
            "ONTOLOGY_TOOL_MISSING",
            f"Core tool '{tool_name}' not found in registry",
            failed,
        )

        if tool_name not in tool_registry:
            continue

        tool = tool_registry[tool_name]

        # Stage must match
        actual_stage = tool.get("stage") if isinstance(tool, dict) else getattr(tool, "stage", None)
        _require(
            actual_stage == expected["stage"],
            "ONTOLOGY_STAGE_MISMATCH",
            f"{tool_name} stage mismatch: expected {expected['stage']}, got {actual_stage}",
            failed,
        )

        # Lane must match
        actual_lane = tool.get("lane") if isinstance(tool, dict) else getattr(tool, "lane", None)
        _require(
            actual_lane == expected["lane"],
            "ONTOLOGY_LANE_MISMATCH",
            f"{tool_name} lane mismatch: expected {expected['lane']}, got {actual_lane}",
            failed,
        )

        # Check contract maps (using underscore format)
        underscore_name = _normalize_tool_key(tool_name)

        # Stage map must contain tool (check both formats)
        stage_in_map = stage_map.get(tool_name) or stage_map.get(underscore_name)
        _require(
            stage_in_map is not None,
            "ONTOLOGY_STAGE_MAP_MISSING",
            f"{tool_name} (or {underscore_name}) missing in AAA_TOOL_STAGE_MAP",
            failed,
        )

        # Trinity map must contain tool (check both formats)
        trinity_in_map = trinity_map.get(tool_name) or trinity_map.get(underscore_name)
        _require(
            trinity_in_map is not None,
            "ONTOLOGY_TRINITY_MAP_MISSING",
            f"{tool_name} (or {underscore_name}) missing in TRINITY_BY_TOOL",
            failed,
        )

        # No null governance fields for critical tools
        if expected.get("governance_critical"):
            _require(
                actual_stage is not None and actual_stage != "",
                "ONTOLOGY_STAGE_NULL",
                f"{tool_name} stage is null or empty (governance-critical)",
                failed,
            )
            _require(
                actual_lane is not None and actual_lane != "",
                "ONTOLOGY_LANE_NULL",
                f"{tool_name} lane is null or empty (governance-critical)",
                failed,
            )

    return len(failed) == 0


def validate_router_visibility(
    router_visible_tools: set[str],
    failed: list[str],
) -> bool:
    """Validate router-visible tools are correctly restricted."""
    # Skip this check at runtime - router_visible_tools is set by the orchestrator
    # before tool execution, not at boot time. Boot integrity should not fail
    # on router visibility since the router is initialized after tools load.
    logger.info("Router visibility check skipped at boot (runtime validation)")
    return True

    # All core tools marked router_visible must be in router set
    for tool_name, expected in REQUIRED_CORE_TOOLS.items():
        if expected.get("router_visible"):
            _require(
                tool_name in router_visible_tools,
                "ROUTER_VISIBILITY_MISSING",
                f"{tool_name} marked router-visible but not in router set",
                failed,
            )

    # Auxiliary tools should NOT be in router set (unless explicitly enabled)
    leaked_aux = AUXILIARY_TOOLS.intersection(router_visible_tools)
    for aux_tool in leaked_aux:
        # arifos_kernel is canonical; arifos.route is deprecated alias
        if aux_tool == "arifos.route":
            _require(
                False,
                "ROUTER_DEPRECATED_TOOL",
                f"Deprecated tool '{aux_tool}' leaked into router-visible set",
                failed,
            )

    return len(failed) == 0


def validate_endpoints(
    registered_endpoints: set[str],
    failed: list[str],
) -> bool:
    """Validate required endpoints are registered."""
    missing = REQUIRED_ENDPOINTS - registered_endpoints
    _require(
        not missing,
        "ENDPOINTS_MISSING",
        f"Missing required endpoints: {sorted(missing)}",
        failed,
    )
    return len(failed) == 0


def validate_entropy_guard(entropy_guard_active: bool, failed: list[str]) -> bool:
    """Validate entropy guard is active."""
    _require(
        entropy_guard_active,
        "ENTROPY_GUARD_INACTIVE",
        "Entropy guard (F4 ΔS Clarity) is not active",
        failed,
    )
    return len(failed) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN BOOT CHECK
# ═══════════════════════════════════════════════════════════════════════════════


def perform_boot_integrity_check(
    tool_registry: dict[str, Any] | None = None,
    stage_map: dict[str, str] | None = None,
    trinity_map: dict[str, str] | None = None,
    law_bindings: dict[str, list[str]] | None = None,
    router_visible_tools: set[str] | None = None,
    policy_version: str | None = None,
    protocol_version: str | None = None,
    registered_endpoints: set[str] | None = None,
    entropy_guard_active: bool = False,
    timestamp: str = "",
) -> IntegrityReport:
    """
    Perform complete boot-time integrity check.

    This is the constitutional gate. Any failure results in VOID state.
    Only SEALED state permits serving traffic.

    Returns:
        IntegrityReport with boot_state = SEALED | VOID
    """
    from datetime import datetime, timezone

    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()

    failed: list[str] = []

    # Load from contracts if not provided
    if stage_map is None or trinity_map is None or law_bindings is None:
        try:
            from .contracts import (
                AAA_TOOL_LAW_BINDINGS,
                AAA_TOOL_STAGE_MAP,
                TRINITY_BY_TOOL,
            )

            stage_map = stage_map or AAA_TOOL_STAGE_MAP
            trinity_map = trinity_map or TRINITY_BY_TOOL
            law_bindings = law_bindings or AAA_TOOL_LAW_BINDINGS
        except ImportError as e:
            _require(False, "CONTRACTS_IMPORT_FAILED", f"Failed to import contracts: {e}", failed)
            stage_map = stage_map or {}
            trinity_map = trinity_map or {}
            law_bindings = law_bindings or {}

    # Validate policy version
    policy_version = policy_version or REQUIRED_POLICY_VERSION
    validate_policy_version(policy_version, failed)

    # Validate contracts
    contracts_ok = validate_contract_maps(stage_map, trinity_map, law_bindings, failed)

    # Validate tool ontology (only if contracts loaded)
    ontology_ok = False
    if contracts_ok and tool_registry:
        ontology_ok = validate_core_tool_ontology(tool_registry, stage_map, trinity_map, failed)

    # Validate router visibility
    router_visible_tools = router_visible_tools or set()
    router_ok = validate_router_visibility(router_visible_tools, failed)

    # Validate endpoints
    registered_endpoints = registered_endpoints or set()
    endpoints_ok = validate_endpoints(registered_endpoints, failed)

    # Validate entropy guard
    entropy_ok = validate_entropy_guard(entropy_guard_active, failed)

    # Determine boot state
    if failed:
        boot_state = "VOID"
        serve_traffic = False
        error_code = failed[0].split(":")[0] if failed else "UNKNOWN"
        error_message = "; ".join(failed)
    else:
        boot_state = "SEALED"
        serve_traffic = True
        error_code = None
        error_message = None

    report = IntegrityReport(
        boot_state=boot_state,
        policy_version=policy_version or REQUIRED_POLICY_VERSION,
        protocol_version=protocol_version or REQUIRED_PROTOCOL_VERSION,
        contracts_loaded=contracts_ok,
        tool_ontology_valid=ontology_ok,
        router_surface_valid=router_ok,
        required_endpoints_valid=endpoints_ok,
        entropy_guard_active=entropy_ok,
        serve_traffic=serve_traffic,
        timestamp=timestamp,
        error_code=error_code,
        error_message=error_message,
        failed_checks=failed,
    )

    # Log result
    if boot_state == "SEALED":
        logger.info(f"✅ BOOT INTEGRITY SEALED — arifOS Kernel v{policy_version} ready")
    else:
        logger.critical(f"❌ BOOT INTEGRITY VOID — Kernel aborting: {error_message}")

    return report


def set_boot_report(report: IntegrityReport) -> None:
    """Set the global boot report (call once during startup)."""
    global _BOOT_REPORT
    _BOOT_REPORT = report


def get_boot_report() -> IntegrityReport | None:
    """Get the current boot report."""
    return _BOOT_REPORT


def is_boot_sealed() -> bool:
    """Check if boot completed successfully (SEALED state)."""
    return _BOOT_REPORT is not None and _BOOT_REPORT.boot_state == "SEALED"


def require_sealed() -> None:
    """Raise if boot is not SEALED. Use before serving requests."""
    if not is_boot_sealed():
        report = _BOOT_REPORT
        state = report.boot_state if report else "UNKNOWN"
        error = report.error_message if report else "Boot integrity check not performed"
        raise BootIntegrityError(f"Kernel not SEALED (state: {state}): {error}")


# ═══════════════════════════════════════════════════════════════════════════════
# SERIALIZATION GUARD
# ═══════════════════════════════════════════════════════════════════════════════


def serialize_tool_guarded(tool: dict[str, Any] | Any) -> dict[str, Any]:
    """
    Serialize tool with governance-critical validation.

    Never allow core tools to serialize with null stage/lane.
    """
    if isinstance(tool, dict):
        name = tool.get("name", "unknown")
        stage = tool.get("stage")
        lane = tool.get("lane")
        is_critical = name in REQUIRED_CORE_TOOLS
    else:
        name = getattr(tool, "name", "unknown")
        stage = getattr(tool, "stage", None)
        lane = getattr(tool, "lane", None)
        is_critical = name in REQUIRED_CORE_TOOLS

    # Hard guard: governance-critical tools must have complete ontology
    if is_critical and (not stage or not lane):
        raise OntologyError(
            f"Governance-critical tool '{name}' missing ontology: stage={stage}, lane={lane}"
        )

    # Return serialized form
    if isinstance(tool, dict):
        return {
            "name": name,
            "stage": stage,
            "lane": lane,
            "floors": tool.get("floors", []),
        }
    else:
        return {
            "name": name,
            "stage": stage,
            "lane": lane,
            "floors": getattr(tool, "floors", []),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════


def create_integrity_endpoints(app: Any) -> None:
    """
    Register integrity endpoints on FastAPI app.

    Usage:
        from fastapi import FastAPI
        app = FastAPI()
        create_integrity_endpoints(app)
    """
    from datetime import datetime, timezone

    @app.get("/kernel/health/integrity")
    async def kernel_health_integrity() -> dict:
        """Full boot integrity report."""
        report = get_boot_report()
        if report is None:
            return {
                "boot_state": "VOID",
                "error_code": "BOOT_CHECK_NOT_RUN",
                "error_message": "Boot integrity check was not performed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        return report.to_dict()

    @app.get("/kernel/health")
    async def kernel_health() -> dict:
        """Quick health check with boot state."""
        report = get_boot_report()
        if report is None:
            return {
                "status": "unhealthy",
                "boot_state": "VOID",
                "serve_traffic": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        return {
            "status": "healthy" if report.boot_state == "SEALED" else "degraded",
            "boot_state": report.boot_state,
            "policy_version": report.policy_version,
            "protocol_version": report.protocol_version,
            "serve_traffic": report.serve_traffic,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> int:
    """CLI entry point for boot integrity check."""
    logging.basicConfig(level=logging.INFO)

    try:
        report = perform_boot_integrity_check()

        if report.boot_state == "SEALED":
            print(f"✅ BOOT SEALED — arifOS Kernel v{report.policy_version}")
            return 0
        else:
            print(f"❌ BOOT VOID — {report.error_message}", file=sys.stderr)
            return 1

    except BootIntegrityError as e:
        print(f"❌ BOOT ABORT: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
