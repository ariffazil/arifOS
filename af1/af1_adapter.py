"""
af1_adapter.py — AF1 Gate Shadow Mode Adapter

AF1 first, action second. No AF1, no execution.

This module wraps the universal dispatch chokepoint (HARDENED_DISPATCH_MAP)
in shadow mode. Every tool call produces an AF1 receipt. Nothing is blocked yet.

DITEMPA BUKAN DIBERI — Forged, Not Given

Phase: 2A Shadow Mode
Rule: observe, log, do not yet enforce
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable

# AF1 Validator
from af1.af1_validator import AF1Validator

# Receipt logger
from af1.af1_receipt_logger import AF1ReceiptLogger, AF1Receipt

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# AF1 GATE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


class AF1GateConfig:
    """Shadow mode configuration. Hard blocking disabled until parity proven."""

    # Shadow mode: validate + log, do NOT block
    SHADOW_MODE: bool = True

    # AF1 enabled (toggle for full disable if needed)
    AF1_ENABLED: bool = True

    # Receipt log path
    RECEIPT_LOG_PATH: str = os.environ.get(
        "AF1_RECEIPT_LOG", "/root/.openclaw/workspace/af1_receipts.jsonl"
    )

    # Coverage report path
    COVERAGE_REPORT_PATH: str = os.environ.get(
        "AF1_COVERAGE_REPORT", "/root/.openclaw/workspace/af1_coverage.json"
    )

    # Paths not yet covered by AF1 adapter
    EXCLUDED_PATHS: set[str] = {
        "/health",
        "/metadata",
        "/version",
        "/.well-known/mcp/server.json",
        "/openapi.json",
        "/humans.txt",
    }

    def __init__(self):
        self._receipt_logger: AF1ReceiptLogger | None = None
        self._validator: AF1Validator | None = None
        self._coverage: dict[str, dict[str, Any]] = {}
        self._dispatch_map_loaded: bool = False
        self._original_dispatch_map: dict[str, Callable[..., Awaitable[Any]]] = {}

    @property
    def validator(self) -> AF1Validator:
        if self._validator is None:
            self._validator = AF1Validator()
        return self._validator

    @property
    def receipt_logger(self) -> AF1ReceiptLogger:
        if self._receipt_logger is None:
            self._receipt_logger = AF1ReceiptLogger(self.RECEIPT_LOG_PATH)
        return self._receipt_logger

    def record_call(self, tool_name: str, call_source: str, validation_status: str):
        """Track which tools/paths have produced AF1 receipts."""
        if tool_name not in self._coverage:
            self._coverage[tool_name] = {
                "total_calls": 0,
                "pass_count": 0,
                "block_count": 0,
                "sources": set(),
                "last_seen": None,
            }
        self._coverage[tool_name]["total_calls"] += 1
        if validation_status == "PASS":
            self._coverage[tool_name]["pass_count"] += 1
        elif validation_status == "BLOCK":
            self._coverage[tool_name]["block_count"] += 1
        self._coverage[tool_name]["sources"].add(call_source)
        self._coverage[tool_name]["last_seen"] = datetime.now(timezone.utc).isoformat()

    def write_coverage_report(self):
        """Write coverage report showing which tools produced receipts."""
        # Convert sets to lists for JSON serialization
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "shadow_mode": self.SHADOW_MODE,
            "total_tools_seen": len(self._coverage),
            "tools": {
                tool: {
                    "total_calls": data["total_calls"],
                    "pass_count": data["pass_count"],
                    "block_count": data["block_count"],
                    "sources": sorted(list(data["sources"])),
                    "last_seen": data["last_seen"],
                }
                for tool, data in self._coverage.items()
            },
            "paths_not_covered": sorted(list(self.EXCLUDED_PATHS)),
        }
        with open(self.COVERAGE_REPORT_PATH, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"AF1 coverage report written to {self.COVERAGE_RECEIPT_PATH}")


# Singleton
AF1_GATE: AF1GateConfig = AF1GateConfig()


# ═══════════════════════════════════════════════════════════════════════════════
# AF1 GATE WRAPPER
# ═══════════════════════════════════════════════════════════════════════════════


def af1_wrap_handler(
    tool_name: str,
    original_handler: Callable[..., Awaitable[Any]],
    call_source: str = "unknown",
) -> Callable[..., Awaitable[Any]]:
    """
    Wrap a tool handler with AF1 validation + receipt emission.

    In shadow mode: validates, logs, emits receipt, calls original.
    In enforce mode: validates, blocks if invalid, emits receipt, calls original.

    Args:
        tool_name: Canonical tool name
        original_handler: Original dispatch handler
        call_source: Identifier for the invocation path (for bypass detection)

    Returns:
        Wrapped handler that enforces AF1 before calling original
    """

    async def wrapped_handler(**kwargs: Any) -> Any:
        if not AF1_GATE.AF1_ENABLED:
            return await original_handler(**kwargs)

        call_id = str(uuid.uuid4())[:12]
        received_at = datetime.now(timezone.utc).isoformat()

        # Extract inputs for hashing
        raw_inputs = kwargs.copy()

        # Build AF1 validation object
        af1_obj = {
            "intent": kwargs.get("intent", f"call:{tool_name}"),
            "tool": tool_name,
            "scope": [tool_name],
            "inputs": raw_inputs,
            "expected_effect": "tool_execution",
            "risk_level": AF1_GATE.validator.get_tool_risk(tool_name).value,
            "requires_human_confirmation": AF1_GATE.validator.requires_confirmation(
                tool_name
            ),
            "reason": f"AF1 gate pre-flight for {tool_name}",
            "evidence_ref": call_id,
            "ttl_seconds": 300,
        }

        # Validate AF1
        validation_result = AF1_GATE.validator.validate(af1_obj)

        # Determine call_source from kwargs if not provided
        actual_call_source = call_source
        if actual_call_source == "unknown":
            if kwargs.get("platform") == "chatgpt_apps":
                actual_call_source = "rest_chatgpt"
            elif kwargs.get("platform") == "api":
                actual_call_source = "rest_api"
            elif kwargs.get("ctx") is not None:
                actual_call_source = "fastmcp_ctx"
            else:
                actual_call_source = "dispatch_map"

        # Build receipt
        receipt = AF1Receipt(
            af1_id=call_id,
            tool=tool_name,
            call_source=actual_call_source,
            risk_level=af1_obj["risk_level"],
            validation_status=validation_result.status.value,
            validation_reason=validation_result.reason,
            af1_object=af1_obj,
            received_at=received_at,
            completed_at=None,
            blocked=validation_result.status == "BLOCK",
            input_hash=hashlib.sha256(
                json.dumps(raw_inputs, sort_keys=True).encode()
            ).hexdigest()[:16],
        )

        # Log receipt
        AF1_GATE.receipt_logger.emit(receipt)
        AF1_GATE.record_call(
            tool_name, actual_call_source, validation_result.status.value
        )

        # Shadow mode: always call original
        if AF1_GATE.SHADOW_MODE:
            logger.debug(
                f"[AF1 SHADOW] tool={tool_name} source={actual_call_source} "
                f"validation={validation_result.status.value} call_id={call_id}"
            )
            result = await original_handler(**kwargs)
            receipt = AF1_GATE.receipt_logger.update_completed(receipt, result)
            return result

        # Enforce mode: block if validation failed
        if validation_result.status == "BLOCK":
            logger.warning(
                f"[AF1 BLOCK] tool={tool_name} source={actual_call_source} "
                f"reason={validation_result.reason}"
            )
            return {
                "ok": False,
                "af1_blocked": True,
                "tool": tool_name,
                "call_id": call_id,
                "reason": validation_result.reason,
                "verdict": "VOID",
                "action": "AF1_HARD_BLOCK",
                "message": "AF1 validation failed. Fix AF1 object and retry.",
            }

        # Enforce mode: proceed
        result = await original_handler(**kwargs)
        receipt = AF1_GATE.receipt_logger.update_completed(receipt, result)
        return result

    # Preserve handler metadata
    wrapped_handler.__name__ = f"af1_wrapped_{tool_name}"
    wrapped_handler._original_handler = original_handler  # type: ignore
    wrapped_handler._tool_name = tool_name  # type: ignore

    return wrapped_handler


# ═══════════════════════════════════════════════════════════════════════════════
# DISPATCH MAP WRAPPER — The universal chokepoint
# ═══════════════════════════════════════════════════════════════════════════════


def wrap_dispatch_map(
    call_source: str = "dispatch_map",
) -> dict[str, Callable[..., Awaitable[Any]]]:
    """
    Wrap every handler in HARDENED_DISPATCH_MAP with AF1 gate.

    This is the universal chokepoint: ALL tool calls (canonical + legacy)
    flow through HARDENED_DISPATCH_MAP. Wrapping here gives AF1 visibility
    and receipts for every consequential call.

    Args:
        call_source: Identifier for this wrapper instantiation

    Returns:
        Wrapped dispatch map (same structure, AF1-wrapped handlers)
    """
    # Import here to avoid circular dependency at module load
    try:
        from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
    except ImportError:
        logger.warning("[AF1] Could not import HARDENED_DISPATCH_MAP — skipping wrap")
        return {}

    wrapped = {}
    for tool_name, handler in HARDENED_DISPATCH_MAP.items():
        wrapped[tool_name] = af1_wrap_handler(tool_name, handler, call_source)
        logger.debug(f"[AF1] wrapped tool={tool_name} via {call_source}")

    return wrapped


def install_af1_adapter(
    call_source: str = "dispatch_map",
) -> dict[str, Callable[..., Awaitable[Any]]]:
    """
    Install AF1 adapter into HARDENED_DISPATCH_MAP.

    Replaces the live dispatch map with AF1-wrapped versions.
    Call this once at server startup.

    Returns:
        The wrapped dispatch map (for verification)
    """
    logger.info(f"[AF1] Installing adapter — shadow_mode={AF1_GATE.SHADOW_MODE}")
    wrapped_map = wrap_dispatch_map(call_source)

    try:
        from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP

        HARDENED_DISPATCH_MAP.update(wrapped_map)
        logger.info(f"[AF1] Adapter installed — {len(wrapped_map)} tools wrapped")
    except ImportError:
        logger.error("[AF1] Could not update HARDENED_DISPATCH_MAP")

    return wrapped_map


def uninstall_af1_adapter() -> None:
    """
    Remove AF1 adapter, restore original handlers.

    Rollback plan if AF1 causes issues.
    """
    logger.info("[AF1] Uninstalling adapter — restoring original handlers")

    try:
        from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP

        for tool_name, handler in HARDENED_DISPATCH_MAP.items():
            if hasattr(handler, "_original_handler"):
                HARDENED_DISPATCH_MAP[tool_name] = handler._original_handler
                logger.debug(f"[AF1] restored tool={tool_name}")

        logger.info("[AF1] Adapter uninstalled")
    except ImportError:
        logger.error("[AF1] Could not restore HARDENED_DISPATCH_MAP")


def get_coverage_report() -> dict[str, Any]:
    """Return current coverage report as dict."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shadow_mode": AF1_GATE.SHADOW_MODE,
        "total_tools_seen": len(AF1_GATE._coverage),
        "tools": dict(AF1_GATE._coverage),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# REST ROUTE INTERCEPTOR — Secondary chokepoint for /tools/{name} path
# ═══════════════════════════════════════════════════════════════════════════════


async def af1_rest_intercept(
    tool_name: str,
    payload: dict[str, Any],
    request_kwargs: dict[str, Any],
    call_source: str = "rest_direct",
) -> dict[str, Any]:
    """
    Intercept REST tool calls at the /tools/{tool_name} endpoint.

    This is a secondary chokepoint for direct REST tool calls
    that may bypass the dispatch map in some transport paths.

    Args:
        tool_name: Tool being called
        payload: Request payload
        request_kwargs: Additional request context
        call_source: How this was called

    Returns:
        AF1 validation result with receipt
    """
    call_id = str(uuid.uuid4())[:12]
    received_at = datetime.now(timezone.utc).isoformat()

    af1_obj = {
        "intent": payload.get("intent", f"rest_call:{tool_name}"),
        "tool": tool_name,
        "scope": [tool_name],
        "inputs": payload,
        "expected_effect": "tool_execution",
        "risk_level": AF1_GATE.validator.get_tool_risk(tool_name).value,
        "requires_human_confirmation": AF1_GATE.validator.requires_confirmation(
            tool_name
        ),
        "reason": f"AF1 REST intercept for {tool_name}",
        "evidence_ref": call_id,
        "ttl_seconds": 300,
    }

    validation_result = AF1_GATE.validator.validate(af1_obj)

    input_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()[:16]

    receipt = AF1Receipt(
        af1_id=call_id,
        tool=tool_name,
        call_source=call_source,
        risk_level=af1_obj["risk_level"],
        validation_status=validation_result.status.value,
        validation_reason=validation_result.reason,
        af1_object=af1_obj,
        received_at=received_at,
        completed_at=None,
        blocked=validation_result.status == "BLOCK",
        input_hash=input_hash,
    )

    AF1_GATE.receipt_logger.emit(receipt)
    AF1_GATE.record_call(tool_name, call_source, validation_result.status.value)

    return {
        "af1_receipt": receipt.to_dict(),
        "validation_status": validation_result.status.value,
        "validation_reason": validation_result.reason,
        "shadow_mode": AF1_GATE.SHADOW_MODE,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FASTMCP HOOK — on_call_tool hook for FastMCP transport
# ═══════════════════════════════════════════════════════════════════════════════


async def af1_on_call_tool(
    tool_name: str, kwargs: dict[str, Any]
) -> dict[str, Any] | None:
    """
    FastMCP on_call_tool hook. FastMCP calls this before every tool invocation.

    This is the transport-level chokepoint for STDIO and HTTP(S) MCP paths.

    In shadow mode: validate + log + emit receipt + proceed
    In enforce mode: validate + block if invalid + emit receipt

    Returns:
        None = proceed normally
        dict = override response (used when AF1 blocks in enforce mode)
    """
    call_id = str(uuid.uuid4())[:12]
    received_at = datetime.now(timezone.utc).isoformat()

    af1_obj = {
        "intent": kwargs.get("intent", f"fastmcp_call:{tool_name}"),
        "tool": tool_name,
        "scope": [tool_name],
        "inputs": kwargs,
        "expected_effect": "tool_execution",
        "risk_level": AF1_GATE.validator.get_tool_risk(tool_name).value,
        "requires_human_confirmation": AF1_GATE.validator.requires_confirmation(
            tool_name
        ),
        "reason": f"AF1 FastMCP hook for {tool_name}",
        "evidence_ref": call_id,
        "ttl_seconds": 300,
    }

    validation_result = AF1_GATE.validator.validate(af1_obj)

    input_hash = hashlib.sha256(
        json.dumps(kwargs, sort_keys=True).encode()
    ).hexdigest()[:16]

    receipt = AF1Receipt(
        af1_id=call_id,
        tool=tool_name,
        call_source="fastmcp_on_call_tool",
        risk_level=af1_obj["risk_level"],
        validation_status=validation_result.status.value,
        validation_reason=validation_result.reason,
        af1_object=af1_obj,
        received_at=received_at,
        completed_at=None,
        blocked=validation_result.status == "BLOCK",
        input_hash=input_hash,
    )

    AF1_GATE.receipt_logger.emit(receipt)
    AF1_GATE.record_call(
        tool_name, "fastmcp_on_call_tool", validation_result.status.value
    )

    # Shadow mode: always proceed
    if AF1_GATE.SHADOW_MODE:
        return None

    # Enforce mode: block if invalid
    if validation_result.status == "BLOCK":
        return {
            "ok": False,
            "af1_blocked": True,
            "tool": tool_name,
            "call_id": call_id,
            "reason": validation_result.reason,
            "verdict": "VOID",
            "action": "AF1_HARD_BLOCK",
            "message": "AF1 validation failed at FastMCP hook. Fix AF1 object and retry.",
        }

    return None
