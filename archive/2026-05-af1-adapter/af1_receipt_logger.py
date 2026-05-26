"""
af1_receipt_logger.py — AF1 Receipt Logger

Every AF1-validated call emits a receipt.
Receipts are append-only JSONL.
Used for audit, bypass detection, and coverage analysis.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# RECEIPT SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(slots=True, frozen=False)
class AF1Receipt:
    """
    Canonical AF1 receipt for every validated tool call.

    Every stage appends. Nothing is overwritten.
    This is the audit trail that makes AF1 enforceable at scale.
    """

    af1_id: str  # Unique per call (UUID[:12])
    tool: str  # Canonical tool name
    call_source: str  # How it was invoked: fastmcp_ctx, rest_api, rest_chatgpt, dispatch_map, legacy_alias, test, etc.
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    validation_status: str  # PASS, BLOCK, SKIP (AF1 disabled)
    validation_reason: str  # Human-readable validation result

    # AF1 object snapshot (immutable once issued)
    af1_object: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    received_at: str  # ISO 8601 when AF1 received the call
    completed_at: str | None = None  # ISO 8601 when tool execution completed

    # Execution metadata
    blocked: bool = False  # True if AF1 blocked this call (enforce mode)
    input_hash: str = ""  # SHA256[:16] of inputs for tamper evidence
    output_hash: str = ""  # SHA256[:16] of output (added on completion)
    execution_duration_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AF1ReceiptLogger:
    """
    Append-only JSONL receipt logger.

    Thread-safe. Appends to a single file.
    Used for:
    - Audit trail
    - Bypass detection (receipts without matching legacy log = bypass)
    - Coverage analysis (which tools/paths produced receipts)
    - AF1 vs legacy behavior comparison
    """

    LOCK = threading.Lock()

    def __init__(self, log_path: str | None = None):
        self.log_path: str = log_path or os.environ.get(
            "AF1_RECEIPT_LOG", "/root/.openclaw/workspace/af1_receipts.jsonl"
        )
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Create log file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                f.write("")  # Create empty file

    def emit(self, receipt: AF1Receipt) -> None:
        """Append a receipt to the log file. Thread-safe."""
        line = json.dumps(receipt.to_dict(), sort_keys=False) + "\n"
        with self.LOCK:
            with open(self.log_path, "a") as f:
                f.write(line)
        logger.debug(
            f"[AF1 RECEIPT] id={receipt.af1_id} tool={receipt.tool} "
            f"source={receipt.call_source} status={receipt.validation_status}"
        )

    def update_completed(
        self,
        receipt: AF1Receipt,
        result: Any,
        execution_time_ms: int | None = None,
    ) -> AF1Receipt:
        """
        Update a receipt with completion metadata.

        Called after tool execution completes.
        Adds output hash and execution time.
        Re-emits as new line (append-only log).
        """
        completed_at = datetime.now(timezone.utc).isoformat()
        output_hash = ""
        if result is not None:
            try:
                output_str = json.dumps(result, sort_keys=True, default=str)
                import hashlib

                output_hash = hashlib.sha256(output_str.encode()).hexdigest()[:16]
            except Exception:
                output_hash = "unhashable"

        updated = AF1Receipt(
            af1_id=receipt.af1_id,
            tool=receipt.tool,
            call_source=receipt.call_source,
            risk_level=receipt.risk_level,
            validation_status=receipt.validation_status,
            validation_reason=receipt.validation_reason,
            af1_object=receipt.af1_object,
            received_at=receipt.received_at,
            completed_at=completed_at,
            blocked=receipt.blocked,
            input_hash=receipt.input_hash,
            output_hash=output_hash,
            execution_duration_ms=execution_time_ms,
        )

        self.emit(updated)
        return updated

    def read_receipts(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Read receipts from log file. For debugging and analysis."""
        receipts = []
        try:
            with open(self.log_path, "r") as f:
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                    if line.strip():
                        receipts.append(json.loads(line))
        except FileNotFoundError:
            pass
        return receipts

    def count_by_tool(self) -> dict[str, int]:
        """Count receipts per tool. For coverage analysis."""
        counts: dict[str, int] = {}
        for receipt in self.read_receipts():
            tool = receipt.get("tool", "unknown")
            counts[tool] = counts.get(tool, 0) + 1
        return counts

    def count_by_source(self) -> dict[str, int]:
        """Count receipts per call_source. For bypass detection."""
        counts: dict[str, int] = {}
        for receipt in self.read_receipts():
            source = receipt.get("call_source", "unknown")
            counts[source] = counts.get(source, 0) + 1
        return counts

    def get_unmatched_sources(self) -> set[str]:
        """
        Find call_sources that have receipts but may not be expected.

        Called after deployment to detect unexpected paths.
        """
        expected_sources = {
            "fastmcp_on_call_tool",  # FastMCP transport hook
            "rest_api",  # REST /tools/{name} from API
            "rest_chatgpt",  # REST /tools/{name} from ChatGPT
            "dispatch_map",  # Hardened dispatch map wrapper
        }
        actual_sources = set(self.count_by_source().keys())
        return actual_sources - expected_sources
