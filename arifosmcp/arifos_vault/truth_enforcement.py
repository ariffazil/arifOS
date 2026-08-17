"""
Truth-Chain Enforcement Module — for Hermes, OpenClaw, OpenCode, and all AAA warga agents.

This is the mechanical enforcement of the 2026-07-08 PROCEED verdict on arifOS truth receipts.

Core contract (from verdict):
- Truth is layered (L1 sealed canon, L2 verified live, L3 cached, L4 inference/analysis only)
- Every claim must be receipt-bound (10 fields minimum)
- L4 cannot trigger L1-grade / irreversible action
- No valid receipt → no canon. Invalid hash → HOLD. Superseded → do not execute.
- Agents obey verified claims within authority, not language.
- Dual surface: humans get meaning+challenge; agents get machine contract.
- Correction is scar (append-only), not erasure.
- Challenge rights are how humans trust the system.

Implements the truth chain:
Human statement → Claim record → Hash → Signature → Receipt → Kernel verify → Organ enforce → Audit + replay/scar

Usage for agents:
  from arifosmcp.arifos_vault.truth_enforcement import enforce_claim, require_receipt, assign_evidence_layer
  ok, receipt, contract, reason = enforce_claim(statement=..., organ="HERMES", irreversible=False, ...)

Falls back to L4 if no receipt provided (analysis only, never irreversible).

See: GENESIS/020_ARIFOS_TRUTH_RECEIPT_DOCTRINE.md
Schema + model: arifos_claim_receipt.*
"""

from __future__ import annotations

import time
from typing import Any

try:
    from .claim_receipt import (
        ArifOSClaimReceipt,
        create_claim_receipt,
        verify_claim_receipt,
    )
except ImportError:
    # Fallback for direct script / test execution outside package
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from claim_receipt import (
        ArifOSClaimReceipt,
        create_claim_receipt,
        verify_claim_receipt,
    )


def assign_evidence_layer(
    has_sealed_canon: bool = False,
    has_live_verification: bool = False,
    is_fresh_cache: bool = False,
    has_reasoning_only: bool = True,
) -> str:
    """Assign L1-L4 per verdict rules. Default conservative (L4)."""
    if has_sealed_canon and has_live_verification:
        return "L1"
    if has_live_verification:
        return "L2"
    if is_fresh_cache:
        return "L3"
    return "L4"  # inferred / analysis only


def require_receipt(
    claim: str,
    evidence_layer: str | None = None,
    organ: str = "UNKNOWN",
    irreversible: bool = False,
    existing_receipt: dict | ArifOSClaimReceipt | None = None,
) -> tuple[bool, str, dict | None]:
    """
    Gate: does this claim have sufficient proof for the requested action?
    Returns (allowed, reason, receipt_or_none)
    """
    if not claim or not claim.strip():
        return False, "empty claim", None

    if existing_receipt:
        if isinstance(existing_receipt, dict):
            try:
                rec = ArifOSClaimReceipt.model_validate(existing_receipt)
            except Exception as e:
                return False, f"invalid receipt shape: {e}", None
        else:
            rec = existing_receipt
        ok, msg, contract = verify_claim_receipt(rec)
        if not ok:
            return False, msg, contract
        exec_ok, exec_reason = rec.is_valid_for_execution(organ, irreversible=irreversible)
        if not exec_ok:
            return False, exec_reason, contract
        return True, "receipt validated", contract

    # No receipt provided → force L4
    layer = evidence_layer or "L4"
    if layer != "L4":
        # Caller claimed higher layer without receipt — downgrade + HOLD for irreversible
        if irreversible:
            return False, "claimed higher layer without receipt; L4 only for irreversible", None
        layer = "L4"

    if irreversible and layer == "L4":
        return False, "L4 inference cannot trigger irreversible action (verdict rule)", None

    return True, "L4 (no receipt) — analysis only, prepare permitted", None


def enforce_claim(
    *,
    statement: str,
    claim_type: str = "observation",
    organ: str = "HERMES",
    irreversible: bool = False,
    issuer: str = "agent/hermes",
    authority_level: str = "operator",
    scope: list[str] | None = None,
    source_uri: str = "agent:epistemic_check",
    content_hash: str | None = None,
    evidence_refs: list[str] | None = None,
    existing_receipt: dict | ArifOSClaimReceipt | None = None,
    actor_id: str | None = None,
) -> tuple[bool, ArifOSClaimReceipt | None, dict, str]:
    """
    Full enforcement entrypoint for agents.
    Returns: (allowed: bool, receipt: ArifOSClaimReceipt|None, agent_contract: dict, reason: str)

    If no receipt supplied, creates a minimal L4 receipt (inferred) and blocks irreversible.
    Always returns a contract the agent can obey.
    """
    scope = scope or [organ, "arifOS"]
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    layer = assign_evidence_layer(
        has_sealed_canon=bool(
            existing_receipt
            and (
                isinstance(existing_receipt, dict)
                and existing_receipt.get("evidence_layer") == "L1"
            )
        ),
        has_live_verification=bool(evidence_refs),
        is_fresh_cache=False,
        has_reasoning_only=not bool(existing_receipt),
    )

    allowed, reason, contract = require_receipt(
        claim=statement,
        evidence_layer=layer,
        organ=organ,
        irreversible=irreversible,
        existing_receipt=existing_receipt,
    )

    if not allowed and "L4" not in reason:
        # hard block
        dummy_receipt = create_claim_receipt(
            claim_id=f"claim-{now[:10]}-hold-{hash(statement) % 100000:05d}",
            statement=statement[:200],
            claim_type=claim_type,
            evidence_layer="L4",
            issuer=issuer,
            authority_level=authority_level,
            scope=scope,
            source_uri=source_uri,
            content_hash=content_hash or "sha256:" + "0" * 64,
            timestamp_utc=now,
            valid_from=now,
            verdict="HOLD",
        )
        return False, dummy_receipt, dummy_receipt.to_agent_contract(), reason

    if existing_receipt:
        if isinstance(existing_receipt, dict):
            rec = ArifOSClaimReceipt.model_validate(existing_receipt)
        else:
            rec = existing_receipt
        ok2, msg2, contract2 = verify_claim_receipt(rec)
        if not ok2:
            return False, rec, contract2, msg2
        return True, rec, contract2, "enforced from existing receipt"

    # Create a governed L4 (or higher if caller proved) receipt
    rec = create_claim_receipt(
        claim_id=f"claim-{now[:10]}-enf-{abs(hash(statement)) % 1000000:06d}",
        statement=statement,
        claim_type=claim_type,
        evidence_layer=layer,
        issuer=issuer,
        authority_level=authority_level,
        scope=scope,
        source_uri=source_uri,
        content_hash=content_hash or f"sha256:{abs(hash(statement + now)) % (2**256):064x}"[:70],
        timestamp_utc=now,
        valid_from=now,
        verdict="VALID" if layer != "L4" else "VALID",  # L4 is valid as inference
    )

    # Re-apply gate on the created receipt
    exec_ok, exec_reason = rec.is_valid_for_execution(organ, irreversible=irreversible)
    if not exec_ok:
        rec.verdict = "HOLD"
        return False, rec, rec.to_agent_contract(), exec_reason

    contract = rec.to_agent_contract()
    contract["enforcement_note"] = (
        "Generated by truth_enforcement; attach real source hash + kernel signature for L1/L2 elevation."
    )
    if evidence_refs:
        contract["evidence_refs"] = evidence_refs[:5]

    return True, rec, contract, "enforced (receipt created or validated)"


def hermes_claim_to_receipt(
    claim: str,
    evidence_context: str = "",
    actor_id: str = "hermes_agent",
    irreversible: bool = False,
) -> dict[str, Any]:
    """
    Adapter specifically for Hermes epistemic pipeline.
    Takes a raw claim + context, returns enforcement result + human proof surface.
    Use this to upgrade hermes_epistemic_check / fact_check to receipt-bound.
    """
    allowed, receipt, contract, reason = enforce_claim(
        statement=claim,
        claim_type="inference" if not evidence_context else "observation",
        organ="HERMES",
        irreversible=irreversible,
        issuer=f"hermes/{actor_id}",
        authority_level="operator",
        scope=["HERMES", "arifOS", "AAA"],
        source_uri="hermes:epistemic_check+context",
        evidence_refs=[evidence_context[:200]] if evidence_context else None,
        actor_id=actor_id,
    )

    human = receipt.to_human_proof() if receipt else "No receipt generated (HOLD)"
    return {
        "status": "OK" if allowed else "HOLD",
        "enforced": allowed,
        "reason": reason,
        "receipt": receipt.model_dump() if receipt else None,
        "agent_contract": contract,
        "human_proof": human,
        "layer": receipt.evidence_layer if receipt else "L4",
        "verdict": receipt.verdict if receipt else "HOLD",
        "recommendation": "Proceed only within contract"
        if allowed
        else "HOLD — obtain receipt or downgrade action",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# AAA WARGA EXTENSION — for all warga under AAA (opencode, openclaw, hermes-asi, grok-build, 333/555/777/888, etc.)
# Every warga that emits a claim/statement/assertion MUST use this.
# ═══════════════════════════════════════════════════════════════════════════════

AAA_WARGA_REGISTRY: dict[str, dict] = {
    "hermes": {
        "issuer": "hermes-000libra",
        "scope": ["HERMES", "arifOS", "AAA"],
        "authority": "operator",
    },
    "hermes-asi": {
        "issuer": "hermes-asi",
        "scope": ["HERMES", "arifOS", "AAA"],
        "authority": "operator",
    },
    "openclaw": {
        "issuer": "openclaw",
        "scope": ["OPENCLAW", "AAA", "arifOS"],
        "authority": "operator",
    },
    "opencode": {
        "issuer": "opencode",
        "scope": ["OPENCODE", "A-FORGE", "AAA", "arifOS"],
        "authority": "operator",
    },
    "grok": {"issuer": "grok-build", "scope": ["GROK", "AAA", "*"], "authority": "operator"},
    "grok-build": {"issuer": "grok-build", "scope": ["GROK", "AAA", "*"], "authority": "operator"},
    "333-agi": {
        "issuer": "333-agi",
        "scope": ["333-AGI", "AAA", "arifOS"],
        "authority": "operator",
    },
    "555-asi": {
        "issuer": "555-asi",
        "scope": ["555-ASI", "AAA", "arifOS"],
        "authority": "operator",
    },
    "777-forge": {
        "issuer": "777-forge",
        "scope": ["777-FORGE", "A-FORGE", "AAA", "arifOS"],
        "authority": "operator",
    },
    "888-apex": {
        "issuer": "888-apex",
        "scope": ["888-APEX", "AAA", "arifOS"],
        "authority": "kernel",
    },
    "a-audit": {
        "issuer": "a-audit",
        "scope": ["A-AUDIT", "AAA", "arifOS"],
        "authority": "operator",
    },
    "*": {"issuer": "aaa-warga", "scope": ["AAA", "arifOS"], "authority": "observer"},  # fallback
}


def get_warga_config(warga_id: str) -> dict:
    """Resolve warga to issuer/scope. Case-insensitive partial match."""
    w = warga_id.lower().strip()
    for key in AAA_WARGA_REGISTRY:
        if key in w or w in key:
            return AAA_WARGA_REGISTRY[key]
    return AAA_WARGA_REGISTRY["*"]


def enforce_for_warga(
    warga_id: str,
    statement: str,
    claim_type: str = "observation",
    irreversible: bool = False,
    evidence_refs: list[str] | None = None,
    existing_receipt: dict | ArifOSClaimReceipt | None = None,
    **extra,
) -> tuple[bool, ArifOSClaimReceipt | None, dict, str]:
    """
    Universal entry for ANY AAA warga agent.
    Auto-configures issuer/scope/authority from registry.
    All warga must call this (or hermes_claim_to_receipt equivalent) before asserting claims.
    """
    cfg = get_warga_config(warga_id)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return enforce_claim(
        statement=statement,
        claim_type=claim_type,
        organ=warga_id.upper(),
        irreversible=irreversible,
        issuer=cfg["issuer"],
        authority_level=cfg["authority"],
        scope=cfg["scope"],
        source_uri=f"warga:{warga_id}:{claim_type}",
        content_hash=extra.get("content_hash"),
        evidence_refs=evidence_refs,
        existing_receipt=existing_receipt,
        actor_id=extra.get("actor_id", warga_id),
    )


def claim_must_use_receipt(warga_id: str, statement: str, irreversible: bool = False) -> dict:
    """
    Lightweight gate for any warga (Python or via A2A/bridge).
    Returns the full agent_contract + human_proof ready for use.
    Non-Python warga (JS/TS) should POST or delegate to a Python warga that calls this.
    """
    allowed, receipt, contract, reason = enforce_for_warga(
        warga_id=warga_id, statement=statement, irreversible=irreversible
    )
    return {
        "warga": warga_id,
        "allowed": allowed,
        "reason": reason,
        "evidence_layer": receipt.evidence_layer if receipt else "L4",
        "verdict": receipt.verdict if receipt else "HOLD",
        "agent_contract": contract,
        "human_proof": receipt.to_human_proof() if receipt else "No receipt — HOLD",
        "receipt_id": receipt.claim_id if receipt else None,
        "replay_command": contract.get("replay_command", "verify_claim_receipt(claim_id)"),
        "instruction": "Obey agent_contract. L4 inference only. No receipt = no canon.",
    }


# ── MCP Tool ─────────────────────────────────────────────────────────────────
# arif_claim_gate — async MCP wrapper for claim_must_use_receipt()
# Replaces the execSync subprocess bridge from A-FORGE core.ts
# Wired into judgeProxyHandler (core.ts:1433) via callMCP("arifos.arif_claim_gate", ...)
# DITEMPA BUKAN DIBERI — Forged, Not Given

_mcp_gate_available = False
_mcp = None

try:
    from fastmcp import FastMCP as _FastMCP

    _mcp_gate_available = True
except ImportError:
    _FastMCP = None


def _build_arif_claim_gate() -> Any | None:
    """Return arif_claim_gate tool if FastMCP is available, else None."""
    global _mcp
    if not _mcp_gate_available or _FastMCP is None:
        return None
    if _mcp is not None:
        return _mcp

    _mcp = _FastMCP("arif_claim_gate")

    @_mcp.tool(annotations={"readOnlyHint": False})
    async def arif_claim_gate(
        warga_id: str,
        statement: str,
        irreversible: bool = False,
    ) -> dict[str, Any]:
        """
        Claim truth enforcement gate for A-FORGE and all AAA warga agents.

        Evaluates a claim/statement through the truth receipt enforcement chain
        and returns whether it may proceed. Used as the pre-judge gate in
        forge_judge_proxy — replaces execSync subprocess bridge.

        Parameters
        ----------
        warga_id : str
            Agent identifier (e.g. "opencode", "forge", "hermes")
        statement : str
            The claim or action description being submitted for judgment
        irreversible : bool
            True if the action is irreversible (tightens evidence requirements)

        Returns
        -------
        dict with keys:
            - allowed : bool  — True if claim may proceed
            - reason : str   — Human-readable gate result
            - evidence_layer : str  — Assigned evidence layer (L1-L4)
            - verdict : str — Internal verdict (SEAL / HOLD / VOID)
            - receipt_id : str | None
            - instruction : str — What the agent must do next
        """
        return claim_must_use_receipt(
            warga_id=warga_id,
            statement=statement,
            irreversible=irreversible,
        )

    @_mcp.tool(annotations={"readOnlyHint": True})
    async def arif_epoch_gate(
        parent_seal_hash: str | None = None,
        current_head_hash: str = "",
    ) -> dict[str, Any]:
        """
        Merkle Epoch Lock gate for anti-race condition sealing (Eureka 3).
        Validates that the agent's observed parent hash matches VAULT999 HEAD.
        """
        from arifosmcp.runtime.kernel_hardening_eurekas import check_merkle_epoch_lock
        verdict = check_merkle_epoch_lock(parent_seal_hash, current_head_hash)
        return {
            "status": verdict.status,
            "code": verdict.code,
            "expected_parent_hash": verdict.expected_parent_hash,
            "current_head_hash": verdict.current_head_hash,
            "message": verdict.message,
            "allowed": verdict.status == "PASS",
        }

    return _mcp


ARIF_CLAIM_GATE_TOOLS = _build_arif_claim_gate()
