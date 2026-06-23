"""
arifOS Route Query Audit Logger — Structured, deterministic, F11-compliant.

Every route decision is logged with full provenance for:
  - F11 AUDITABILITY: Every decision logged, inspectable, attributable
  - F2 TRUTH:     No fabricated audit entries
  - F4 CLARITY:   Single structured format, no ambiguity
  - L0 GOVERNANCE: Floor compliance auditable per-query

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ── Audit Record ───────────────────────────────────────────────────────────


@dataclass
class RouteAuditRecord:
    """Full F11 audit entry for a single route_query call."""

    # Identity
    session_id: str
    actor_id: str
    agent_name: str = "unknown"

    # Query
    query: str
    query_hash: str  # SHA256 truncated to 12 chars
    query_length: int = 0

    # Routing decision
    lane: str  # exploit | explore | hybrid
    reason: str  # Why this lane was chosen
    explicit_mode: str | None = None
    exploration_triggered: bool = False

    # Tool assignments
    exploit_tools: list[str] = field(default_factory=list)
    explore_tools: list[str] = field(default_factory=list)
    target_tools: list[str] = field(default_factory=list)

    # Budget state
    budget_exploit_remaining: int = 0
    budget_explore_remaining: int = 0
    session_explore_ratio: float = 0.0
    session_contradiction_count: int = 0
    contradiction_quota_met: bool = False
    explore_quota_met: bool = False

    # Governance
    floors_checked: list[str] = field(default_factory=list)
    auth_identity_verified: bool = False
    entitlement_level: str = "unknown"

    # Performance
    latency_ms: float = 0.0
    timestamp: str = ""
    fallback_used: bool = False
    error: str | None = None

    # F2 provenance
    audit_record_hash: str = ""
    previous_audit_hash: str | None = None


# ── Audit Logger ───────────────────────────────────────────────────────────


class RouteAuditLogger:
    """
    F11-compliant structured audit logger for arifos_route_query.

    Writes to:
      - stdout (JSONL, for journald/systemd capture)
      - Memory ring buffer (last 100 entries)
      - Optional file output

    Thread-safe. F2: every entry has hash chain. F4: single format.
    """

    _instance: RouteAuditLogger | None = None
    _lock = threading.Lock()

    def __init__(self, output_file: str | None = None):
        self._records: list[RouteAuditRecord] = []
        self._max_memory = 100
        self._output_file = output_file
        self._previous_hash: str | None = None
        self._total_queries = 0
        self._total_fallbacks = 0

    @classmethod
    def get_instance(cls, output_file: str | None = None) -> RouteAuditLogger:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(output_file=output_file)
        return cls._instance

    def log(self, record: RouteAuditRecord) -> None:
        """Log a route decision. F11: every call logged. Thread-safe."""
        import hashlib

        # Chain hash for integrity (like VAULT999)
        record.audit_record_hash = hashlib.sha256(
            json.dumps(
                {
                    "query_hash": record.query_hash,
                    "lane": record.lane,
                    "timestamp": record.timestamp,
                    "previous": self._previous_hash or "GENESIS",
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()[:16]
        record.previous_audit_hash = self._previous_hash
        self._previous_hash = record.audit_record_hash

        with self._lock:
            # Memory ring buffer
            self._records.append(record)
            if len(self._records) > self._max_memory:
                self._records = self._records[-self._max_memory :]

            self._total_queries += 1
            if record.fallback_used:
                self._total_fallbacks += 1

        # stdout JSONL (for journald)
        try:
            print(json.dumps(asdict(record), default=str), flush=True)
        except Exception:
            pass  # Don't crash on audit log failure

        # Optional file output
        if self._output_file:
            try:
                os.makedirs(os.path.dirname(self._output_file), exist_ok=True)
                with open(self._output_file, "a") as f:
                    f.write(json.dumps(asdict(record), default=str) + "\n")
            except Exception as e:
                logger.warning(f"Failed to write audit log to file: {e}")

        logger.debug(
            "route_query audit | lane=%s reason=%s latency=%.1fms fallback=%s",
            record.lane,
            record.reason,
            record.latency_ms,
            record.fallback_used,
        )

    def get_summary(self) -> dict[str, Any]:
        """Return audit summary — F4 CLARITY."""
        with self._lock:
            return {
                "total_queries": self._total_queries,
                "total_fallbacks": self._total_fallbacks,
                "fallback_rate": (
                    self._total_fallbacks / self._total_queries if self._total_queries > 0 else 0.0
                ),
                "memory_buffer_size": len(self._records),
                "last_query_hash": self._previous_hash,
                "last_query_at": (self._records[-1].timestamp if self._records else None),
                "floors": ["F2", "F4", "F11"],
            }

    def get_recent(self, n: int = 10) -> list[dict[str, Any]]:
        """Return last n audit records."""
        with self._lock:
            return [asdict(r) for r in self._records[-n:]]


# ── Convenience ────────────────────────────────────────────────────────────


def log_route_decision(
    decision: Any,  # RouteDecision from route_policy
    query: str,
    floors_checked: list[str] | None = None,
    auth_verified: bool = False,
    entitlement: str = "unknown",
    agent_name: str = "unknown",
) -> None:
    """Log a route decision from the policy engine."""
    audit = decision.audit
    record = RouteAuditRecord(
        session_id=audit.session_id,
        actor_id=audit.actor_id,
        agent_name=agent_name,
        query=query,
        query_hash=audit.query_hash,
        query_length=len(query),
        lane=audit.lane,
        reason=audit.reason,
        exploration_triggered=audit.exploration_triggered,
        exploit_tools=audit.exploit_tools,
        explore_tools=audit.explore_tools,
        target_tools=decision.target_tools,
        budget_exploit_remaining=audit.budget_exploit_results,
        budget_explore_remaining=audit.budget_explore_results,
        session_explore_ratio=audit.session_explore_ratio,
        session_contradiction_count=audit.session_contradiction_count,
        contradiction_quota_met=audit.contradiction_quota_met,
        explore_quota_met=decision.constraints.get("explore_quota_met", False),
        floors_checked=floors_checked or [],
        auth_identity_verified=auth_verified,
        entitlement_level=entitlement,
        latency_ms=audit.latency_ms,
        timestamp=audit.timestamp,
        fallback_used=audit.fallback_used,
        error=audit.error,
    )
    RouteAuditLogger.get_instance().log(record)
