"""
Audit receipt logger — Append-only JSONL + hash-chained receipts v0.1
═══════════════════════════════════════════════════════════════

Every MCP interaction emits a receipt with:
  - Full subject envelope (human_id, agent_id, session_id, org_id)
  - Upstream snapshot (server, tool, schema_hash)
  - Lease snapshot (id, risk_class, reversibility, invocation counts)
  - Gateway decision (verdict, reason, http_status)
  - Hash chain (prior_receipt_hash → receipt_hash)
  - Runtime data (duration_ms, schema_validated, forwarded_upstream)

v0.1: JSONL append-only + hash chaining.
v0.2+: VAULT999 Merkle sealing.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════
# CANONICAL RECEIPT (spec v0.1)
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class SubjectSnapshot:
    """Subject identity at time of call."""

    human_id: str = ""
    agent_id: str = ""
    session_id: str = ""
    org_id: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "human_id": self.human_id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "org_id": self.org_id,
        }


@dataclass
class UpstreamSnapshot:
    """Upstream server and tool info."""

    upstream_id: str = ""
    server_url_hash: str = ""
    tool: str = ""
    tool_schema_hash: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "upstream_id": self.upstream_id,
            "server_url_hash": self.server_url_hash,
            "tool": self.tool,
            "tool_schema_hash": self.tool_schema_hash,
        }


@dataclass
class LeaseSnapshot:
    """Lease state before/after call."""

    lease_id: str = ""
    risk_class: str = "LOW"
    reversibility: str = "FULL"
    remaining_invocations_before: int = 0
    remaining_invocations_after: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "risk_class": self.risk_class,
            "reversibility": self.reversibility,
            "remaining_invocations_before": self.remaining_invocations_before,
            "remaining_invocations_after": self.remaining_invocations_after,
        }


@dataclass
class DecisionSnapshot:
    """Gateway decision."""

    gateway_decision: str = "UNKNOWN"  # DENIED, PENDING_888, EXECUTED, ERROR
    reason: str = ""
    http_status: int = 200

    def to_dict(self) -> dict[str, Any]:
        return {
            "gateway_decision": self.gateway_decision,
            "reason": self.reason,
            "http_status": self.http_status,
        }


@dataclass
class HashBundle:
    """Cryptographic hashes for the receipt."""

    params_hash: str = ""
    result_hash: str | None = None
    prior_receipt_hash: str = ""
    receipt_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "params_hash": self.params_hash,
            "result_hash": self.result_hash,
            "prior_receipt_hash": self.prior_receipt_hash,
            "receipt_hash": self.receipt_hash,
        }


@dataclass
class RuntimeSnapshot:
    """Execution metadata."""

    duration_ms: int = 0
    schema_validated: bool = False
    forwarded_upstream: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "duration_ms": self.duration_ms,
            "schema_validated": self.schema_validated,
            "forwarded_upstream": self.forwarded_upstream,
            "error": self.error,
        }


@dataclass
class CanonicalReceipt:
    """Full canonical receipt matching spec v0.1."""

    receipt_id: str
    timestamp: str = ""
    event_type: str = "MCP_TOOL_CALL"
    direction: str = "tools/call"
    subject: SubjectSnapshot = field(default_factory=SubjectSnapshot)
    upstream: UpstreamSnapshot = field(default_factory=UpstreamSnapshot)
    lease: LeaseSnapshot = field(default_factory=LeaseSnapshot)
    decision: DecisionSnapshot = field(default_factory=DecisionSnapshot)
    hashes: HashBundle = field(default_factory=HashBundle)
    runtime: RuntimeSnapshot = field(default_factory=RuntimeSnapshot)

    def compute_hash(self) -> str:
        """Compute SHA-256 over canonical JSON of all fields except receipt_hash."""
        d = self.to_dict()
        d["hashes"].pop("receipt_hash", None)  # exclude self-referential hash
        payload = json.dumps(d, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode()).hexdigest()

    def seal(self, prior_receipt_hash: str = "") -> str:
        """Finalize receipt: set prior hash, compute receipt hash, return receipt_hash."""
        self.hashes.prior_receipt_hash = prior_receipt_hash
        self.hashes.receipt_hash = self.compute_hash()
        return self.hashes.receipt_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "direction": self.direction,
            "subject": self.subject.to_dict(),
            "upstream": self.upstream.to_dict(),
            "lease": self.lease.to_dict(),
            "decision": self.decision.to_dict(),
            "hashes": self.hashes.to_dict(),
            "runtime": self.runtime.to_dict(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# LEGACY FLAT RECEIPT (backward compat)
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ReceiptRecord:
    """LEGACY flat receipt — kept for backward compat."""

    receipt_id: str
    timestamp: str = ""
    direction: str = "call_tool"
    subject: str = "anonymous"
    tool: str = ""
    upstream: str = ""
    verdict: str = "UNKNOWN"
    lease_id: str = ""
    risk_class: str = "LOW"
    params_hash: str = ""
    duration_ms: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "timestamp": self.timestamp,
            "direction": self.direction,
            "subject": self.subject,
            "tool": self.tool,
            "upstream": self.upstream,
            "verdict": self.verdict,
            "lease_id": self.lease_id,
            "risk_class": self.risk_class,
            "params_hash": self.params_hash,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


# ═══════════════════════════════════════════════════════════════════════════
# RECEIPT LOGGER WITH HASH CHAINING
# ═══════════════════════════════════════════════════════════════════════════


class HashChainVerifier:
    """Verify receipt hash chain integrity."""

    @staticmethod
    def verify_chain(receipts: list[dict[str, Any]]) -> tuple[bool, int | None]:
        """Verify a list of receipt dicts forms a valid hash chain.

        Returns (is_valid, first_broken_index).
        """
        for i in range(1, len(receipts)):
            prev = receipts[i - 1]
            curr = receipts[i]

            prev_hash = prev.get("hashes", {}).get("receipt_hash", "") or prev.get(
                "receipt_hash", ""
            )
            claimed_prior = curr.get("hashes", {}).get("prior_receipt_hash", "") or curr.get(
                "prior_receipt_hash", ""
            )

            if claimed_prior and prev_hash and claimed_prior != prev_hash:
                return False, i

        return True, None


class ReceiptLogger:
    """Append-only receipt logger with JSONL persistence and hash chaining.

    v0.1: in-memory buffer + JSONL append + SHA-256 hash chain.
    v0.2+: VAULT999 Merkle sealing.

    Usage:
        logger = ReceiptLogger()
        receipt = logger.emit(
            tool_name="geox.read_well_plan",
            subject=subject_snapshot,
            upstream=upstream_snapshot,
            lease=lease_snapshot,
            decision=decision_snapshot,
            runtime=runtime_snapshot,
        )
    """

    def __init__(self, log_path: str | None = None) -> None:
        self._receipts: list[CanonicalReceipt] = []
        self._legacy_receipts: list[ReceiptRecord] = []
        self._log_path = log_path or os.environ.get(
            "ARIFOS_GATEWAY_RECEIPTS_LOG",
            "/var/lib/arifos/gateway/receipts.jsonl",
        )
        self._last_hash: str = ""  # hash of previous receipt for chaining
        os.makedirs(os.path.dirname(self._log_path), exist_ok=True)

    # ── Canonical emit (NEW — use this) ──────────────────────────────────

    def emit(
        self,
        tool_name: str,
        subject: SubjectSnapshot | None = None,
        upstream: UpstreamSnapshot | None = None,
        lease: LeaseSnapshot | None = None,
        decision: DecisionSnapshot | None = None,
        hashes: HashBundle | None = None,
        runtime: RuntimeSnapshot | None = None,
        direction: str = "tools/call",
        event_type: str = "MCP_TOOL_CALL",
    ) -> CanonicalReceipt:
        """Emit a canonical receipt with hash chaining.

        Returns the sealed receipt with receipt_hash computed.
        """
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        receipt = CanonicalReceipt(
            receipt_id=f"RCPT-{uuid.uuid4().hex[:16].upper()}",
            timestamp=ts,
            event_type=event_type,
            direction=direction,
            subject=subject or SubjectSnapshot(),
            upstream=upstream or UpstreamSnapshot(tool=tool_name),
            lease=lease or LeaseSnapshot(),
            decision=decision or DecisionSnapshot(),
            hashes=hashes or HashBundle(),
            runtime=runtime or RuntimeSnapshot(),
        )

        # Hash chain: link to prior receipt
        receipt.seal(prior_receipt_hash=self._last_hash)
        self._last_hash = receipt.hashes.receipt_hash

        self._receipts.append(receipt)

        # Persist to JSONL
        try:
            with open(self._log_path, "a") as f:
                f.write(json.dumps(receipt.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass

        return receipt

    # ── Legacy emit (backward compat) ────────────────────────────────────

    def log(
        self,
        tool_name: str,
        subject: str,
        upstream_id: str,
        arguments: dict[str, Any],
        verdict: str,
        lease_id: str = "",
        risk_class: str = "LOW",
        params_hash: str = "",
        duration_ms: int = 0,
        error: str | None = None,
    ) -> ReceiptRecord:
        """LEGACY: emit a flat receipt. Prefer emit() for new code."""
        receipt = ReceiptRecord(
            receipt_id=f"RCPT-{uuid.uuid4().hex[:16].upper()}",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            subject=subject,
            tool=tool_name,
            upstream=upstream_id,
            verdict=verdict,
            lease_id=lease_id,
            risk_class=risk_class,
            params_hash=params_hash,
            duration_ms=duration_ms,
            error=error,
        )
        self._legacy_receipts.append(receipt)

        try:
            with open(self._log_path, "a") as f:
                f.write(json.dumps(receipt.to_dict()) + "\n")
        except OSError:
            pass

        return receipt

    # ── Queries ──────────────────────────────────────────────────────────

    def list_recent(self, limit: int = 50) -> list[CanonicalReceipt]:
        """Return most recent canonical receipts."""
        return self._receipts[-limit:]

    def count(self) -> int:
        """Total canonical receipts logged this session."""
        return len(self._receipts)

    def total_count(self) -> int:
        """All receipts (canonical + legacy)."""
        return len(self._receipts) + len(self._legacy_receipts)

    def last_hash(self) -> str:
        """Return hash of last sealed receipt (for chain continuity)."""
        return self._last_hash

    def verify(self) -> tuple[bool, int | None]:
        """Verify hash chain integrity of canonical receipts.

        Returns (is_valid, first_broken_index).
        """
        return HashChainVerifier.verify_chain([r.to_dict() for r in self._receipts])

    def chain_export(self) -> list[dict[str, str]]:
        """Export minimal hash chain: [(receipt_id, receipt_hash), ...]."""
        return [
            {"receipt_id": r.receipt_id, "receipt_hash": r.hashes.receipt_hash}
            for r in self._receipts
        ]
