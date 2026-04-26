"""
ForgeApp — Execution Bridge Surface
════════════════════════════════════
Double-gated execution manifest interface.

Gate 1: Judge verdict must be "SEAL"
Gate 2: Human approval token must be True

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone

from fastmcp import FastMCP

from arifosmcp.apps.interceptor import intercept
from arifosmcp.apps.surface_utils import envelope_error, envelope_pause
from arifosmcp.apps.vault_chain import append_vault_record


def _register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="arif_forge_execute",
        description="010_FORGE — sovereign execution bridge with double-gate enforcement",
    )
    def arif_forge_execute(
        manifest: str,
        verdict: str,
        human_approval: bool,
        session_id: str = None,
    ) -> dict:
        """Execute a manifest through the sovereign FORGE bridge.

        Requires:
          - verdict == "SEAL"  (Gate 1 — Judge must have approved)
          - human_approval == True  (Gate 2 — human explicit consent)

        v0.1: execution is still simulated but vault-logged with real receipts.
        """
        # Block dangerous tools without valid session
        blocker = intercept("arif_forge_execute", {"manifest": manifest}, session_id)
        if blocker:
            return blocker

        # ── Gate 1: Verify SEAL from Judge ──────────────────────────────────
        if verdict != "SEAL":
            return {
                "ok": False,
                "status": "VOID",
                "stage": "FORGE",
                "verdict": verdict,
                "message": f"Cannot execute — verdict is {verdict}, not SEAL",
                "vault_receipt": "FORGE_BLOCKED_GATE1",
                "gates_passed": [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # ── Gate 2: Human approval token ────────────────────────────────────
        if not human_approval:
            return {
                "ok": False,
                "status": "888_HOLD",
                "stage": "FORGE",
                "verdict": "HOLD",
                "message": "Gate 2 (human approval) not satisfied",
                "requires_human": True,
                "vault_receipt": "FORGE_HOLD_GATE2",
                "gates_passed": ["GATE1_SEAL"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # ── Execute (v0.1 dry-run with real vault linkage) ─────────────────
        manifest_hash = hashlib.sha256(manifest.encode()).hexdigest()[:16]
        receipt = f"EXEC_{uuid.uuid4().hex[:12]}"

        vault_entry = {
            "type": "forge_execute",
            "manifest": manifest,
            "manifest_hash": manifest_hash,
            "receipt": receipt,
            "session_id": session_id or "anonymous",
            "gates": ["GATE1_SEAL", "GATE2_HUMAN_APPROVED"],
            "verdict": verdict,
            "human_approval": human_approval,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "permanent": True,
        }
        vault_result = append_vault_record(vault_entry)

        return {
            "ok": True,
            "status": "EXECUTED",
            "stage": "FORGE",
            "receipt": receipt,
            "vault_receipt": vault_result["vault_receipt"],
            "manifest_hash": manifest_hash,
            "gates_passed": ["GATE1_SEAL", "GATE2_HUMAN_APPROVED"],
            "message": "Action executed and logged to VAULT999",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @mcp.tool(
        name="forge_dry_run",
        description="FORGE dry-run — simulate execution without side effects",
    )
    def forge_dry_run(manifest: str, session_id: str = None) -> dict:
        """Simulate forge execution. No gates required. No vault entry."""
        manifest_hash = hashlib.sha256(manifest.encode()).hexdigest()[:16]
        return {
            "ok": True,
            "mode": "dry_run",
            "manifest_hash": manifest_hash,
            "manifest_preview": manifest[:80] + ("..." if len(manifest) > 80 else ""),
            "status": "simulated",
            "note": "Dry-run only — no gates checked, no vault written",
            "session_id": session_id or "anonymous",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
