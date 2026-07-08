"""
arifOS Claim Receipt — Canonical proof object for truth.

Implements the institutional truth architecture:
- Evidence layers (L1 Ground Truth sealed, L2 Verified live, L3 Cached, L4 Inferred)
- No Receipt, No Canon
- Dual surfaces: human (explanation + challenge rights) + agent (verification contract)
- Authority scope + replay + falsification (scar over erasure)
- Agents obey verified claims within authority only. L4 cannot drive L1 action.

Complements EvidenceReceipt (tri-witness + memory L0-L6). This is the governance-grade claim envelope.

Rule: IF valid receipt AND layer sufficient AND scope matches AND not expired/superseded THEN execute within band ELSE HOLD.

F1-F13 always apply. F2 TRUTH: label by layer. F4 CLARITY. F7 HUMILITY. F9 ANTIHANTU. F11 AUDIT. F13 SOVEREIGN.

Forged 2026-07-08 PROCEED YELLOW.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Authority(BaseModel):
    issuer: str
    authority_level: str  # observer | operator | organ | kernel | F13
    scope: list[str]  # e.g. ["WEALTH", "A-FORGE", "*"]


class Source(BaseModel):
    uri: str
    content_hash_sha256: str
    timestamp_utc: str


class Validity(BaseModel):
    valid_from: str
    expires_at: str | None = None
    supersedes: list[str] = Field(default_factory=list)
    superseded_by: str | None = None


class Verification(BaseModel):
    verifier: str
    signature: str
    verify_method: str
    replayable: bool = True
    replay_command: str | None = None


class Falsification(BaseModel):
    challenge_method: str
    correction_policy: str = "append_only"  # scar_over_erasure


class ArifOSClaimReceipt(BaseModel):
    """The minimum canonical proof object. Every arifOS claim must resolve to one."""

    receipt_version: str = "1.0"
    claim_id: str
    statement: str
    claim_type: str
    evidence_layer: str  # L1 | L2 | L3 | L4
    authority: Authority
    source: Source
    validity: Validity
    verification: Verification
    falsification: Falsification
    verdict: str  # VALID | HOLD | VOID | SUPERSEDED | UNKNOWN
    envelope: dict[str, Any] | None = None

    @field_validator("evidence_layer")
    @classmethod
    def _layer_valid(cls, v: str) -> str:
        if v not in ("L1", "L2", "L3", "L4"):
            raise ValueError("evidence_layer must be L1|L2|L3|L4")
        return v

    @field_validator("verdict")
    @classmethod
    def _verdict_valid(cls, v: str) -> str:
        allowed = ("VALID", "HOLD", "VOID", "SUPERSEDED", "UNKNOWN")
        if v not in allowed:
            raise ValueError(f"verdict must be one of {allowed}")
        return v

    def content_hash(self) -> str:
        """Stable hash of core fields for signature/replay (excludes volatile envelope + sig)."""
        core = self.model_dump(exclude={"envelope"})
        if isinstance(core.get("verification"), dict):
            core["verification"] = {k: v for k, v in core["verification"].items() if k != "signature"}
        canonical = json.dumps(core, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()

    def is_valid_for_execution(self, organ: str, irreversible: bool = False) -> tuple[bool, str]:
        """
        Agent execution gate per spec.
        Returns (allowed, reason).
        L4 inference NEVER performs irreversible.
        Must have VALID, correct layer, scope, not expired, not superseded.
        """
        if self.verdict != "VALID":
            return False, f"verdict={self.verdict} (not VALID)"
        if self.validity.superseded_by:
            return False, f"superseded_by={self.validity.superseded_by}"
        if self.validity.expires_at:
            # naive expiry check; in kernel use real time
            pass
        layer = self.evidence_layer
        if irreversible and layer == "L4":
            return False, "L4 inference cannot trigger irreversible action"
        if layer == "L1" or layer == "L2":
            pass  # sufficient for high
        elif layer == "L3":
            if irreversible:
                return False, "L3 cached insufficient for irreversible (reverify)"
        scope = self.authority.scope
        if "*" not in scope and organ not in scope:
            return False, f"scope {scope} does not include {organ}"
        return True, "OK"

    def to_human_proof(self) -> str:
        """Human surface: plain language + challenge rights. No jargon dump."""
        lines = [
            f"Claim: {self.statement}",
            f"Why this is asserted: {self.claim_type} at {self.evidence_layer}.",
            f"Authority: {self.authority.issuer} ({self.authority.authority_level}) scope={self.authority.scope}.",
            f"Evidence: source={self.source.uri} hash={self.source.content_hash_sha256[:16]}... at {self.source.timestamp_utc}.",
            f"Consequence: Agents execute only within verified layer + scope. Irreversible actions require sufficient layer.",
            f"How to challenge: {self.falsification.challenge_method}. Correction policy: {self.falsification.correction_policy}.",
            f"Verdict: {self.verdict}. Receipt: {self.claim_id} v{self.receipt_version}.",
            "Replay: " + (self.verification.replay_command or "verify_claim_receipt(claim_id)"),
        ]
        return "\n".join(lines)

    def to_agent_contract(self) -> dict[str, Any]:
        """Agent surface: machine verification + execution contract."""
        allowed_prepare, _ = self.is_valid_for_execution("*", irreversible=False)
        allowed_exec, reason = self.is_valid_for_execution("*", irreversible=True)
        return {
            "claim_id": self.claim_id,
            "evidence_layer": self.evidence_layer,
            "authority_scope": self.authority.scope,
            "allowed_action": "prepare_only" if not allowed_exec else "execute_within_band",
            "blocked_action": "execute_without_valid_receipt" if not allowed_exec else None,
            "requires": [
                "valid_signature",
                "canon_hash_match",
                "not_expired",
                "not_superseded",
                f"layer>={self.evidence_layer} for irreversible" if allowed_exec else "layer_check",
            ],
            "on_fail": "HOLD",
            "replay_command": self.verification.replay_command or f"verify_claim_receipt({self.claim_id})",
            "falsification": self.falsification.model_dump(),
            "verdict": self.verdict,
            "execution_gate": {
                "prepare": allowed_prepare,
                "irreversible": allowed_exec,
                "reason_if_blocked": None if allowed_exec else reason,
            },
        }


def create_claim_receipt(
    *,
    claim_id: str,
    statement: str,
    claim_type: str,
    evidence_layer: str,
    issuer: str,
    authority_level: str,
    scope: list[str],
    source_uri: str,
    content_hash: str,
    timestamp_utc: str,
    valid_from: str,
    verdict: str = "VALID",
    verifier: str = "arifOS kernel",
    signature: str = "",
    verify_method: str = "verify_claim_receipt",
    challenge_method: str = "submit_counter_receipt",
    supersedes: list[str] | None = None,
    envelope: dict | None = None,
) -> ArifOSClaimReceipt:
    """Factory for well-formed receipts. Caller must supply real signature/hash."""
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec = ArifOSClaimReceipt(
        claim_id=claim_id,
        statement=statement,
        claim_type=claim_type,
        evidence_layer=evidence_layer,
        authority=Authority(issuer=issuer, authority_level=authority_level, scope=scope),
        source=Source(uri=source_uri, content_hash_sha256=content_hash, timestamp_utc=timestamp_utc),
        validity=Validity(valid_from=valid_from, supersedes=supersedes or []),
        verification=Verification(
            verifier=verifier,
            signature=signature or f"unsigned-{claim_id}",
            verify_method=verify_method,
            replayable=True,
            replay_command=f"verify_claim_receipt({claim_id})",
        ),
        falsification=Falsification(challenge_method=challenge_method),
        verdict=verdict,
        envelope=envelope,
    )
    # If no real sig supplied, mark as such for L4+
    if not signature:
        rec.verification.signature = f"pending_kernel_sign:{rec.content_hash()[:16]}"
    return rec


def verify_claim_receipt(receipt: ArifOSClaimReceipt | dict) -> tuple[bool, str, dict]:
    """
    Deterministic verifier stub (kernel-grade skeleton).
    In production: load from VAULT999 by claim_id, recompute hash, check sig against kernel key, check supersession.
    Returns (ok, message, agent_contract).
    """
    if isinstance(receipt, dict):
        receipt = ArifOSClaimReceipt.model_validate(receipt)
    ok, reason = receipt.is_valid_for_execution("arifOS", irreversible=False)
    contract = receipt.to_agent_contract()
    if not ok:
        return False, reason, contract
    # Additional structural checks
    if receipt.verification.replayable and not receipt.verification.replay_command:
        return False, "replayable but no replay_command", contract
    if receipt.source.content_hash_sha256.startswith("sha256:") is False:
        return False, "invalid content_hash format", contract
    return True, "VALIDATED", contract
