"""
healing_errors.py — Self-Healing Error Envelope Builder
═══════════════════════════════════════════════════════════════════════════════

P0: Canonical recovery envelope inspired by Faucet's self-correcting error pattern.

Every MCP tool error should return:
  - Stable machine-readable error code
  - Human-readable message
  - Bounded alternatives (filtered through caller's auth scope)
  - Explicit discovery tool for more options
  - Retryability indicator

Governance requirements (888-APEX ratified):
  - No secrets, hidden resources, or unauthorized names disclosed
  - Alternatives filtered through the caller's authorization scope
  - Alternatives deterministically bounded (max 10)
  - Existing clients still receive a stable message field

Usage:
    from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes

    # Simple healing error
    return healing_error(
        code=ErrorCodes.INVALID_FIELD,
        message='Field "reservoir_pressure" is unavailable.',
        organ="geox",
        tool="geox_well_log",
        parameter="field",
        received="reservoir_pressure",
        available=["pressure_kpa", "pressure_gradient", "formation_pressure"],
        discovery_tool="geox_describe",
    )

    # Or build a CanonicalError directly with context + recovery
    from arifosmcp.runtime.model import CanonicalError, RecoveryContext
    err = CanonicalError(
        code="INVALID_FIELD",
        message="...",
        context={"organ": "geox", "tool": "geox_well_log"},
        recovery=RecoveryContext(available=[...], discovery_tool="geox_describe"),
    )

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import difflib
import hashlib
from typing import Any

from arifosmcp.runtime.model import CanonicalError, RecoveryContext
from arifosmcp.runtime.failure_wal import wal_append

# Strategy bank import — graceful if unavailable
try:
    from AAA.state.strategy_bank import record_failure, lookup_recovery

    _STRATEGY_BANK_AVAILABLE = True
except ImportError:
    _STRATEGY_BANK_AVAILABLE = False

# Maximum alternatives returned to prevent token explosion.
MAX_ALTERNATIVES = 10


# ── Canonical Error Codes ────────────────────────────────────────────────────
# Stable machine-readable codes. Add new codes; never rename existing ones.
class ErrorCodes:
    """Canonical error codes for the arifOS federation."""

    # Tool/parameter errors
    INVALID_FIELD = "INVALID_FIELD"
    INVALID_TOOL = "INVALID_TOOL"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    TYPE_MISMATCH = "TYPE_MISMATCH"

    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    ORGAN_UNAVAILABLE = "ORGAN_UNAVAILABLE"

    # Authorization errors
    FORBIDDEN = "FORBIDDEN"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    INSUFFICIENT_SCOPE = "INSUFFICIENT_SCOPE"

    # Governance errors
    GOVERNANCE_HOLD = "GOVERNANCE_HOLD"
    GOVERNANCE_VOID = "GOVERNANCE_VOID"
    CONSTITUTIONAL_VIOLATION = "CONSTITUTIONAL_VIOLATION"

    # Execution errors
    EXECUTION_FAILED = "EXECUTION_FAILED"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"


def healing_error(
    *,
    code: str,
    message: str,
    organ: str | None = None,
    tool: str | None = None,
    parameter: str | None = None,
    received: Any = None,
    available: list[str] | None = None,
    discovery_tool: str | None = None,
    retryable: bool = True,
    rejected_fields: list[str] | None = None,
    level: str | None = None,
    stage: str | None = None,
) -> CanonicalError:
    """Build a CanonicalError with self-healing recovery context.

    Args:
        code: Stable machine-readable error code (use ErrorCodes constants).
        message: Human-readable error message.
        organ: Organ name (geox, wealth, well, arifos, aforge).
        tool: Tool name that was called.
        parameter: Parameter name that was invalid.
        received: The invalid value that was received.
        available: Bounded list of valid alternatives. Capped at MAX_ALTERNATIVES.
        discovery_tool: Tool to call for more options (e.g. "geox_describe").
        retryable: Whether retrying with corrected input may succeed.
        rejected_fields: Explicit list of rejected field/value names (P-1).
        level: Recovery level — "field" or "tool" (P-1, optional).
        stage: Constitutional stage (optional).

    Returns:
        CanonicalError with context and recovery fields populated.
    """
    # Build structured context
    context: dict[str, Any] = {}
    if organ:
        context["organ"] = organ
    if tool:
        context["tool"] = tool
    if parameter:
        context["parameter"] = parameter
    if received is not None:
        context["received"] = received

    # Build recovery hints — bounded alternatives
    avail = (available or [])[:MAX_ALTERNATIVES]

    # P-1: derive rejected fields — explicit list, else a single `received`
    # value when this is a field-level rejection.
    rejected = list(rejected_fields) if rejected_fields else []
    if not rejected and parameter == "field" and isinstance(received, str) and received:
        rejected = [received]

    recovery = RecoveryContext(
        available=avail,
        discovery_tool=discovery_tool,
        retryable=retryable,
        level=level,
        rejected_fields=rejected,
        closest_match=_closest_matches(rejected, avail),
    )

    err = CanonicalError(
        code=code,
        message=message,
        stage=stage,
        context=context if context else None,
        recovery=recovery,
    )

    # INV-L5-WAL: Synchronous append to failure telemetry ledger.
    # WAL failure MUST NEVER block the error response.
    try:
        wal_append(
            code=code,
            message=message,
            organ=organ,
            tool=tool,
            parameter=parameter,
            received=received,
            available=available,
            discovery_tool=discovery_tool,
            context=context if context else None,
        )
    except Exception:
        pass

    # INV-L5-REFLEX: Strategy bank lookup for auto-recovery injection.
    # If signature hash matches a known recovery skill, inject it.
    if _STRATEGY_BANK_AVAILABLE:
        try:
            # Record this failure in the strategy bank
            sig_hash = _sig_hash(tool, code, context)
            record_failure(sig_hash=sig_hash, code=code, organ=organ, tool=tool)

            # Look up known recovery
            skill = lookup_recovery(sig_hash)
            if skill and skill.get("recovery_steps"):
                # Inject recovery steps into the error message
                recovery_hint = " | ".join(skill["recovery_steps"][:3])
                err.message = f"{err.message} [RECOVERY KNOWN: {recovery_hint}]"
        except Exception:
            pass

    return err


def _sig_hash(tool: str | None, code: str, context: dict[str, Any] | None) -> str:
    """Deterministic signature hash for strategy bank lookup.

    Must match the hash function in failure_wal.py.
    """
    parts = [tool or "", code]
    if context:
        for k in sorted(context.keys()):
            v = context[k]
            parts.append(f"{k}={v}" if v is not None else k)
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _closest_matches(
    rejected_fields: list[str], available_fields: list[str], cutoff: float = 0.6
) -> dict[str, list[str]]:
    """Map each rejected field to its nearest valid alternatives.

    P-1 (Layer 1.5 field recovery). Order: substring containment first
    (stronger, structure-preserving), then difflib close matches. Case-insensitive;
    returns original casing. Empty inputs -> empty dict.
    """
    if not rejected_fields or not available_fields:
        return {}
    avail_lower = [str(a).lower() for a in available_fields]
    result: dict[str, list[str]] = {}
    for field in rejected_fields:
        if not isinstance(field, str) or not field.strip():
            result[field] = []
            continue
        fl = field.lower()
        matched: list[str] = []
        # 1) substring containment (either direction)
        for orig, low in zip(available_fields, avail_lower):
            if fl in low or low in fl:
                if orig not in matched:
                    matched.append(orig)
        # 2) difflib close matches
        for m in difflib.get_close_matches(fl, avail_lower, n=3, cutoff=cutoff):
            idx = avail_lower.index(m)
            orig = available_fields[idx]
            if orig not in matched:
                matched.append(orig)
        result[field] = matched
    return result


def tool_not_found_error(
    *,
    tool_name: str,
    organ: str | None = None,
    available_tools: list[str] | None = None,
) -> CanonicalError:
    """Healing error for invalid tool name.

    Args:
        tool_name: The tool name that was not found.
        organ: Organ that was targeted.
        available_tools: List of available tool names on this organ.
    """
    return healing_error(
        code=ErrorCodes.INVALID_TOOL,
        message=f'Tool "{tool_name}" not found.',
        organ=organ,
        tool=tool_name,
        available=available_tools,
        discovery_tool=f"{organ}_list" if organ else None,
        retryable=bool(available_tools),
    )


def field_not_found_error(
    *,
    field_name: str,
    organ: str,
    tool: str,
    available_fields: list[str],
    discovery_tool: str | None = None,
) -> CanonicalError:
    """Healing error for invalid field/column name.

    Args:
        field_name: The field name that was not found.
        organ: Organ name.
        tool: Tool that was called.
        available_fields: List of valid field names.
        discovery_tool: Tool to discover more fields.
    """
    return healing_error(
        code=ErrorCodes.INVALID_FIELD,
        message=f'Field "{field_name}" is unavailable.',
        organ=organ,
        tool=tool,
        parameter="field",
        received=field_name,
        available=available_fields,
        discovery_tool=discovery_tool or f"{organ}_describe",
        rejected_fields=[field_name],
        level="field",
    )


def parameter_error(
    *,
    parameter: str,
    received: Any,
    expected: str,
    organ: str,
    tool: str,
    available: list[str] | None = None,
) -> CanonicalError:
    """Healing error for invalid parameter value.

    Args:
        parameter: Parameter name.
        received: The invalid value received.
        expected: Description of expected value.
        organ: Organ name.
        tool: Tool name.
        available: List of valid values (if enumerable).
    """
    msg = f'Parameter "{parameter}" received invalid value "{received}". Expected: {expected}'
    return healing_error(
        code=ErrorCodes.INVALID_PARAMETER,
        message=msg,
        organ=organ,
        tool=tool,
        parameter=parameter,
        received=received,
        available=available,
    )


def service_unavailable_error(
    *,
    service: str,
    organ: str | None = None,
    available_services: list[str] | None = None,
) -> CanonicalError:
    """Healing error for unavailable service/database.

    Args:
        service: The service name that was unavailable.
        organ: Organ name.
        available_services: List of available services.
    """
    return healing_error(
        code=ErrorCodes.SERVICE_UNAVAILABLE,
        message=f'Service "{service}" is not available.',
        organ=organ,
        parameter="service",
        received=service,
        available=available_services,
        retryable=True,
    )
