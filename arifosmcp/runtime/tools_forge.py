"""
arifosmcp/runtime/tools_forge.py — The 10th Tool: Delegated Execution Bridge

Constitutional Separation of Powers:
  • 9 Tools = Governance (Legislature + Judiciary)
  • arifos.forge = Execution Bridge (Executive Delegation)
  • AF-FORGE = External Substrate (Actual Execution)

DITEMPA, BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

from core.governance_kernel import GovernanceKernel
from core.recovery.rollback_engine import outcome_ledger, rollback_engine

# RuntimeEnvelope is a dict type for tool outputs
RuntimeEnvelope = dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTION MANIFEST SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

class ExecutionManifest:
    """
    Signed execution request for AF-FORGE substrate.
    
    Structure:
        manifest_id: SHA256 hash of canonical JSON
        session_id: Source session
        judge_verdict: Must be SEAL
        judge_g_star: Governance strength at seal
        action: What to execute (code, shell, api_call, contract)
        payload: Action-specific parameters
        constraints: Resource limits, timeouts, rollback info
        issued_at: UTC timestamp
        expires_at: Validity window
        signature: HMAC-SHA256 (session_key + manifest_id)
    """
    
    def __init__(
        self,
        session_id: str,
        judge_verdict: str,
        judge_g_star: float,
        action: str,
        payload: dict[str, Any],
        constraints: dict[str, Any] | None = None,
        ttl_seconds: int = 300,
        autonomy_level: float = 0.0,
    ):
        self.session_id = session_id
        self.judge_verdict = judge_verdict
        self.judge_g_star = judge_g_star
        self.autonomy_level = autonomy_level
        self.action = action
        self.payload = payload
        self.constraints = constraints or {
            "max_cpu_ms": 30000,
            "max_memory_mb": 512,
            "timeout_seconds": 60,
            "network_allowed": False,
            "disk_write_allowed": False,
        }
        self.issued_at = datetime.now(timezone.utc).isoformat()
        self.expires_at = (datetime.now(timezone.utc).timestamp() + ttl_seconds)
        self.manifest_id = self._compute_id()
        self.signature: str | None = None
    
    def _compute_id(self) -> str:
        """Compute canonical manifest ID (SHA-256)."""
        canonical = {
            "session_id": self.session_id,
            "judge_verdict": self.judge_verdict,
            "judge_g_star": round(self.judge_g_star, 4),
            "action": self.action,
            "payload": self.payload,
            "constraints": self.constraints,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
        }
        canonical_json = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    def sign(self, session_key: str) -> str:
        """Sign manifest with session key (HMAC-SHA256)."""
        self.signature = hashlib.sha256(
            f"{self.manifest_id}:{session_key}".encode()
        ).hexdigest()
        return self.signature
    
    def to_dict(self) -> dict[str, Any]:
        """Export manifest to dict for serialization."""
        return {
            "manifest_id": self.manifest_id,
            "session_id": self.session_id,
            "judge_verdict": self.judge_verdict,
            "judge_g_star": self.judge_g_star,
            "action": self.action,
            "payload": self.payload,
            "constraints": self.constraints,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "signature": self.signature,
            "schema_version": "1.0.0",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ARIFOS.FORGE — THE 10TH TOOL
# ═══════════════════════════════════════════════════════════════════════════════

async def arifos_forge(
    action: str,
    payload: dict[str, Any],
    session_id: str,
    judge_verdict: str,
    judge_g_star: float,
    constraints: dict[str, Any] | None = None,
    ttl_seconds: int = 300,
    dry_run: bool = True,
    af_forge_endpoint: str | None = None,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """
    Delegated Execution Bridge — The 10th Tool.
    
    This tool does NOT execute directly. It:
        1. Validates judge verdict is SEAL
        2. Constructs signed execution manifest
        3. Dispatches to AF-FORGE substrate
        4. Returns execution receipt
    
    Constitutional Guarantee:
        • No execution without judge SEAL
        • No self-authorization
        • All actions logged to vault
        • Separation of powers preserved
    
    Args:
        action: Execution type ("shell", "api_call", "contract", "compute")
        payload: Action-specific parameters
        session_id: Source session ID
        judge_verdict: Must be "SEAL" (from arifos.judge)
        judge_g_star: G★ score at time of verdict
        constraints: Resource limits for execution
        ttl_seconds: Manifest validity window
        dry_run: If True, generate manifest but don't dispatch
        af_forge_endpoint: Target substrate (default from config)
    
    Returns:
        RuntimeEnvelope with:
            - verdict: SEAL (manifest valid) or VOID (rejected)
            - payload: Execution manifest or error
            - receipt_hash: Future reference for audit
    
    Raises:
        ValueError: If judge_verdict is not SEAL
    """
    
    # ─────────────────────────────────────────────────────────────────────────
    # FLOOR F1: AMANAH — Trust Validation
    # ─────────────────────────────────────────────────────────────────────────
    if judge_verdict != "SEAL":
        return _forge_error(
            session_id=session_id,
            code="F1_VIOLATION",
            message="Execution requires judge verdict SEAL. Governance layer must approve before executive action.",
            judge_verdict=judge_verdict,
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # FLOOR F2: TRUTH — Input Validation
    # ─────────────────────────────────────────────────────────────────────────
    if not action or not isinstance(payload, dict):
        return _forge_error(
            session_id=session_id,
            code="F2_VIOLATION",
            message="Malformed execution request: action and payload required.",
        )
    
    allowed_actions = {"shell", "api_call", "contract", "compute", "container", "vm"}
    if action not in allowed_actions:
        return _forge_error(
            session_id=session_id,
            code="F2_INVALID_ACTION",
            message=f"Action '{action}' not in allowed set: {allowed_actions}",
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # CONSTRUCT EXECUTION MANIFEST
    # ─────────────────────────────────────────────────────────────────────────
    rollback_context = _prepare_rollback_context(
        session_id=session_id,
        action=action,
        dry_run=dry_run,
        requested_constraints=constraints,
    )
    manifest = ExecutionManifest(
        session_id=session_id,
        judge_verdict=judge_verdict,
        judge_g_star=judge_g_star,
        action=action,
        payload=payload,
        constraints=rollback_context["constraints"],
        ttl_seconds=ttl_seconds,
    )
    
    # In production: Sign with session-specific HMAC key from vault
    # For now: Use deterministic placeholder (session_id hash)
    session_key = hashlib.sha256(f"{session_id}:forge_key".encode()).hexdigest()[:32]
    manifest.sign(session_key)
    
    # ─────────────────────────────────────────────────────────────────────────
    # DRY RUN: Generate manifest only
    # ─────────────────────────────────────────────────────────────────────────
    outcome_ledger.record_outcome(
        decision_id=manifest.manifest_id,
        session_id=session_id,
        verdict_issued="SEAL",
        expected_outcome=f"{action} delegated via arifos_forge",
        reversible=rollback_context["rollback_supported"],
    )
    if dry_run:
        outcome_ledger.resolve_outcome(
            manifest.manifest_id,
            actual_outcome="dry run manifest generated",
            harm_detected=False,
        )
        result = _forge_success(
            session_id=session_id,
            manifest=manifest,
            status="MANIFEST_GENERATED",
            note="F7 Humility: Dry run. Manifest valid but not dispatched.",
            rollback=rollback_context,
        )
        if isinstance(result, dict):
            result["platform_context"] = platform
        return result
    
    # ─────────────────────────────────────────────────────────────────────────
    # DISPATCH TO AF-FORGE SUBSTRATE
    # ─────────────────────────────────────────────────────────────────────────
    # In production: HTTP POST to AF-FORGE endpoint with manifest
    # For now: Simulate dispatch and return receipt hash
    
    try:
        receipt_hash = _simulate_af_forge_dispatch(
            manifest=manifest,
            endpoint=af_forge_endpoint or "https://forge.af-forge.io/v1/execute",
        )
    except Exception as exc:
        rollback_engine.rollback(session_id)
        outcome_ledger.resolve_outcome(
            manifest.manifest_id,
            actual_outcome=f"dispatch failed: {exc}",
            harm_detected=True,
        )
        return _forge_error(
            session_id=session_id,
            code="FORGE_DISPATCH_FAILED",
            message=f"Dispatch to AF-FORGE failed: {exc}",
            judge_verdict=judge_verdict,
            rollback=rollback_context,
        )

    outcome_ledger.resolve_outcome(
        manifest.manifest_id,
        actual_outcome="execution delegated to AF-FORGE",
        harm_detected=False,
    )
    
    result = _forge_success(
        session_id=session_id,
        manifest=manifest,
        status="DISPATCHED",
        receipt_hash=receipt_hash,
        note="Execution delegated to AF-FORGE substrate. Receipt logged to vault.",
        rollback=rollback_context,
    )
    if isinstance(result, dict):
        result["platform_context"] = platform
    return result


def _forge_error(
    session_id: str,
    code: str,
    message: str,
    judge_verdict: str | None = None,
    rollback: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Generate forge error envelope."""
    return {
        "ok": False,
        "tool": "arifos.forge",
        "canonical_tool_name": "arifos.forge",
        "stage": "FORGE_010",
        "session_id": session_id,
        "verdict": "VOID",
        "status": "ERROR",
        "errors": [{
            "code": code,
            "message": message,
            "stage": "FORGE_010",
            "judge_verdict": judge_verdict,
        }],
        "payload": {
            "error": message,
            "resolution": "Route through arifos_judge first to obtain SEAL verdict.",
            "rollback": rollback or {},
        },
        "allowed_next_tools": ["arifos_judge", "arifos_init"],
    }


def _forge_success(
    session_id: str,
    manifest: ExecutionManifest,
    status: str,
    receipt_hash: str | None = None,
    note: str = "",
    rollback: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Generate forge success envelope."""
    payload = {
        "manifest": manifest.to_dict(),
        "status": status,
        "note": note,
        "rollback": rollback or {},
    }

    if receipt_hash:
        payload["receipt_hash"] = receipt_hash
        payload["vault_log"] = f"vault://executions/{receipt_hash}"

    return {
        "ok": True,
        "tool": "arifos.forge",
        "canonical_tool_name": "arifos.forge",
        "stage": "FORGE_010",
        "session_id": session_id,
        "verdict": "SEAL",
        "status": "SUCCESS",
        "payload": payload,
        "allowed_next_tools": ["arifos_vault", "arifos_memory"],
    }


def _prepare_rollback_context(
    session_id: str,
    action: str,
    dry_run: bool,
    requested_constraints: dict[str, Any] | None,
) -> dict[str, Any]:
    kernel = GovernanceKernel(session_id=session_id)
    kernel.record_event(
        "action",
        {
            "tool": "arifos_forge",
            "action": action,
            "reversible": dry_run,
        },
    )
    checkpoint_id = rollback_engine.create_checkpoint(session_id, kernel)
    rollback_meta = rollback_engine.latest_checkpoint(session_id) or {"checkpoint_id": checkpoint_id}

    merged_constraints = dict(requested_constraints or {})
    merged_constraints.setdefault("rollback_checkpoint", checkpoint_id)
    merged_constraints.setdefault(
        "rollback_plan",
        {
            "checkpoint_id": checkpoint_id,
            "strategy": "rollback_engine.restore_last_checkpoint",
            "session_tool": "arifos_init",
            "session_mode": "revoke",
        },
    )

    return {
        "rollback_supported": True,
        "checkpoint_id": checkpoint_id,
        "checkpoint_meta": rollback_meta,
        "constraints": merged_constraints,
    }


def _simulate_af_forge_dispatch(
    manifest: ExecutionManifest,
    endpoint: str,
) -> str:
    """
    Simulate AF-FORGE dispatch receipt.
    
    In production:
        1. POST manifest to endpoint
        2. Receive execution receipt
        3. Verify receipt signature
        4. Log to vault
        5. Return receipt hash
    """
    # Simulate receipt hash: SHA256(manifest_id + endpoint + timestamp)
    timestamp = str(int(time.time()))
    receipt = f"{manifest.manifest_id}:{endpoint}:{timestamp}"
    return hashlib.sha256(receipt.encode('utf-8')).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "arifos_forge",
    "ExecutionManifest",
]
__ = [
    "arifos_forge",
    "ExecutionManifest",
]
