"""
Recursive Governance Locks — Runtime Enforcement Engine
═══════════════════════════════════════════════════════════════════════════════

Three deep locks forged into runtime interceptors:

  1. Gödel Lock      → no self-certifying certainty
  2. Strange Loop    → recursive memory with provenance
  3. Anti-Beautiful-One → elegance without consequence is collapse

Usage:
    from arifosmcp.core.paradox.recursive_governance_locks import RecursiveGovernanceEngine

    engine = RecursiveGovernanceEngine()
    receipt = engine.apply_locks(
        tool_name="arif_judge_deliberate",
        params={...},
        actor_id="hermes-asi",
        context={"memory_loop_depth": 2, "beauty_score": 0.9},
    )
    if receipt.composite_verdict != "SEAL":
        raise ConstitutionalViolation(receipt)

Ratified: 2026-06-03
Authority: L13 SOVEREIGN

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from arifosmcp.schemas.governance_locks import (
    AntiBeautifulOneMetrics,
    AntiBeautifulOneReceipt,
    GodelLockReceipt,
    LockReceipt,
    LockType,
    LockVerdict,
    MemoryProvenance,
    ParadoxHoldReceipt,
    ProvenanceLabel,
    SelfClaimCategory,
    StrangeLoopReceipt,
    UnifiedGovernanceReceipt,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# SELF-CLAIM PATTERNS — Gödel Lock detection surface
# ═══════════════════════════════════════════════════════════════════════════════

SELF_CLAIM_PATTERNS: dict[SelfClaimCategory, list[re.Pattern[str]]] = {
    SelfClaimCategory.SAFETY: [
        re.compile(r"\bi am safe\b", re.I),
        re.compile(r"\bsystem is secure\b", re.I),
        re.compile(r"\bno risk detected\b", re.I),
    ],
    SelfClaimCategory.AUTHORITY: [
        re.compile(r"\bi certify\b", re.I),
        re.compile(r"\bi authorize\b", re.I),
        re.compile(r"\bself-authorized\b", re.I),
        re.compile(r"\bi am the final judge\b", re.I),
    ],
    SelfClaimCategory.CONSCIOUSNESS: [
        re.compile(r"\bi am conscious\b", re.I),
        re.compile(r"\bi am aware\b", re.I),
        re.compile(r"\bi have understanding\b", re.I),
    ],
    SelfClaimCategory.TRUTH: [
        re.compile(r"\bi am true\b", re.I),
        re.compile(r"\bthis is the truth\b", re.I),
        re.compile(r"\bself-evident\b", re.I),
    ],
    SelfClaimCategory.COMPLIANCE: [
        re.compile(r"\bi am compliant\b", re.I),
        re.compile(r"\bi follow all floors\b", re.I),
        re.compile(r"\bself-certified\b", re.I),
    ],
    SelfClaimCategory.MEMORY: [
        re.compile(r"\bi remember correctly\b", re.I),
        re.compile(r"\bmy memory is accurate\b", re.I),
        re.compile(r"\bi have always believed\b", re.I),
    ],
}

# Tools that are *allowed* to make boundary claims because they are external witnesses
EXTERNAL_WITNESS_TOOLS: set[str] = {
    "arif_judge_deliberate",
    "arif_vault_seal",
    "arif_heart_critique",
}

# ═══════════════════════════════════════════════════════════════════════════════
# EXCEPTION
# ═══════════════════════════════════════════════════════════════════════════════


class LockViolationError(Exception):
    """Raised when a recursive governance lock is breached."""

    def __init__(self, receipt: UnifiedGovernanceReceipt):
        self.receipt = receipt
        super().__init__(
            f"Lock breach: {receipt.composite_verdict} — "
            f"{[r.reason for r in receipt.lock_receipts if r.verdict != LockVerdict.SEAL]}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


class RecursiveGovernanceEngine:
    """
    Applies the three deep locks to every tool call.

    The engine is stateless — it inspects the call context and returns a receipt.
    Persistence (VAULT999, session state) is the caller's responsibility.
    """

    def __init__(self) -> None:
        self.invocation_count = 0
        self.void_count = 0
        self.hold_count = 0

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def apply_locks(
        self,
        tool_name: str,
        params: dict[str, Any],
        actor_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> UnifiedGovernanceReceipt:
        """
        Apply all three locks to a tool invocation.

        Args:
            tool_name: Canonical MCP tool name
            params: Tool parameters
            actor_id: Calling agent identity
            context: Extra context (memory_loop_depth, beauty_score, etc.)

        Returns:
            UnifiedGovernanceReceipt with composite verdict
        """
        self.invocation_count += 1
        ctx = context or {}
        receipts: list[LockReceipt] = []

        # Lock 1 — Gödel
        godel = self._apply_godel_lock(tool_name, params, actor_id, ctx)
        receipts.append(
            LockReceipt(
                lock_type=LockType.GODEL,
                verdict=godel.verdict,
                reason=godel.reason,
                payload=godel,
            )
        )

        # Lock 2 — Strange Loop
        strange = self._apply_strange_loop_lock(tool_name, params, actor_id, ctx)
        receipts.append(
            LockReceipt(
                lock_type=LockType.STRANGE_LOOP,
                verdict=strange.verdict,
                reason=strange.reason,
                payload=strange,
            )
        )

        # Lock 3 — Anti-Beautiful-One
        ab1 = self._apply_anti_beautiful_one(tool_name, params, actor_id, ctx)
        receipts.append(
            LockReceipt(
                lock_type=LockType.ANTI_BEAUTIFUL_ONE,
                verdict=ab1.verdict,
                reason=ab1.reason,
                payload=ab1,
            )
        )

        # Lock 4 — Paradox Hold (conditional)
        paradox = self._apply_paradox_hold(tool_name, params, actor_id, ctx)
        if paradox is not None:
            receipts.append(
                LockReceipt(
                    lock_type=LockType.PARADOX_HOLD,
                    verdict=paradox.verdict,
                    reason=paradox.reason,
                    payload=paradox,
                )
            )

        locks_applied = [
            LockType.GODEL,
            LockType.STRANGE_LOOP,
            LockType.ANTI_BEAUTIFUL_ONE,
        ]
        if paradox is not None:
            locks_applied.append(LockType.PARADOX_HOLD)

        unified = UnifiedGovernanceReceipt(
            session_id=params.get("session_id"),
            actor_id=actor_id,
            locks_applied=locks_applied,
            lock_receipts=receipts,
            paradox_hold=paradox,
        )

        if unified.composite_verdict == LockVerdict.VOID:
            self.void_count += 1
            logger.critical(
                f"VOID [{tool_name}] actor={actor_id} — "
                f"godel={godel.verdict} loop={strange.verdict} ab1={ab1.verdict}"
            )
        elif unified.composite_verdict == LockVerdict.HOLD:
            self.hold_count += 1
            paradox_tag = " paradox=HOLD" if paradox is not None else ""
            logger.warning(
                f"HOLD [{tool_name}] actor={actor_id} — "
                f"godel={godel.verdict} loop={strange.verdict} ab1={ab1.verdict}{paradox_tag}"
            )
        else:
            logger.debug(f"SEAL [{tool_name}] actor={actor_id}")

        return unified

    # ──────────────────────────────────────────────────────────────────────────
    # Lock 1 — Gödel
    # ──────────────────────────────────────────────────────────────────────────

    def _apply_godel_lock(
        self,
        tool_name: str,
        params: dict[str, Any],
        actor_id: str | None,
        context: dict[str, Any],
    ) -> GodelLockReceipt:
        """
        Detect self-certifying claims.

        If the tool itself is an external witness tool, it is allowed to produce
        verdicts because it is the designated witness, not the self-claimant.
        """
        if tool_name in EXTERNAL_WITNESS_TOOLS:
            return GodelLockReceipt(
                verdict=LockVerdict.SEAL,
                reason="Tool is designated external witness — Gödel Lock satisfied by role",
                external_witness_present=True,
                witness_type=tool_name,
            )

        # Scan parameter values for self-claims
        param_text = " ".join(str(v) for v in params.values() if isinstance(v, str))
        for category, patterns in SELF_CLAIM_PATTERNS.items():
            for pat in patterns:
                if pat.search(param_text):
                    return GodelLockReceipt(
                        verdict=LockVerdict.VOID,
                        reason=(
                            f"Self-claim detected: category={category.value} | "
                            f"pattern='{pat.pattern}'. "
                            f"Sistem tak boleh jadi saksi mutlak untuk dirinya sendiri."
                        ),
                        external_witness_present=False,
                    )

        return GodelLockReceipt(
            verdict=LockVerdict.SEAL,
            reason="No self-certifying claims detected",
            external_witness_present=False,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Lock 2 — Strange Loop
    # ──────────────────────────────────────────────────────────────────────────

    def _apply_strange_loop_lock(
        self,
        tool_name: str,
        params: dict[str, Any],
        actor_id: str | None,
        context: dict[str, Any],
    ) -> StrangeLoopReceipt:
        """
        Detect recursive memory without provenance.

        Reads context["memory_loop_depth"] and context["memory_provenance"].
        """
        loop_depth: int = context.get("memory_loop_depth", 0)
        provenance: MemoryProvenance | None = context.get("memory_provenance")

        # If no recursion, no issue
        if loop_depth == 0:
            return StrangeLoopReceipt(
                verdict=LockVerdict.SEAL,
                reason="No recursive memory loop detected",
                loop_depth=0,
            )

        # If recursion but no provenance → HOLD
        if provenance is None:
            return StrangeLoopReceipt(
                verdict=LockVerdict.HOLD,
                reason=(
                    f"Recursive memory loop depth={loop_depth} "
                    f"without provenance. Memory may not self-sanctify."
                ),
                loop_depth=loop_depth,
                provenance_label=ProvenanceLabel.CLAIMED,
            )

        # If provenance is stale or contradicted → HOLD/VOID
        if provenance.label == ProvenanceLabel.CONTRADICTED:
            return StrangeLoopReceipt(
                verdict=LockVerdict.VOID,
                reason="Memory provenance is CONTRADICTED — loop is toxic",
                loop_depth=loop_depth,
                provenance_label=provenance.label,
            )

        if provenance.label == ProvenanceLabel.STALE:
            return StrangeLoopReceipt(
                verdict=LockVerdict.HOLD,
                reason="Memory provenance is STALE — verify before recursion",
                loop_depth=loop_depth,
                provenance_label=provenance.label,
            )

        if provenance.confidence < 0.5:
            return StrangeLoopReceipt(
                verdict=LockVerdict.HOLD,
                reason=(
                    f"Memory confidence {provenance.confidence:.2f} < 0.5 — too weak for recursion"
                ),
                loop_depth=loop_depth,
                provenance_label=provenance.label,
                confidence_delta=0.5 - provenance.confidence,
            )

        return StrangeLoopReceipt(
            verdict=LockVerdict.SEAL,
            reason="Recursive memory carries valid provenance",
            loop_depth=loop_depth,
            provenance_label=provenance.label,
            last_verified_at=provenance.timestamp,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Lock 3 — Anti-Beautiful-One
    # ──────────────────────────────────────────────────────────────────────────

    def _apply_anti_beautiful_one(
        self,
        tool_name: str,
        params: dict[str, Any],
        actor_id: str | None,
        context: dict[str, Any],
    ) -> AntiBeautifulOneReceipt:
        """
        Detect sterile polished collapse.

        Reads context["beauty_score"], context["operational_contact_score"],
        context["survival_status"], etc.
        """
        metrics = AntiBeautifulOneMetrics(
            operational_contact_score=context.get("operational_contact_score", 0.0),
            human_cost_detected=context.get("human_cost_detected", False),
            survival_status=context.get("survival_status", "unknown"),
            reality_evidence_present=context.get("reality_evidence_present", False),
            contradiction_challenged=context.get("contradiction_challenged", False),
            beauty_to_consequence_ratio=context.get("beauty_to_consequence_ratio", 1.0),
        )

        # High beauty / low consequence → HOLD
        if metrics.beauty_to_consequence_ratio > 2.0:
            return AntiBeautifulOneReceipt(
                verdict=LockVerdict.HOLD,
                reason=(
                    f"Beauty-to-consequence ratio {metrics.beauty_to_consequence_ratio:.1f} > 2.0. "
                    f"Elegance without consequence is collapse."
                ),
                metrics=metrics,
            )

        # Zero operational contact → HOLD
        if metrics.operational_contact_score < 0.2 and metrics.beauty_to_consequence_ratio > 1.0:
            return AntiBeautifulOneReceipt(
                verdict=LockVerdict.HOLD,
                reason=(
                    f"Operational contact score {metrics.operational_contact_score:.1f} < 0.2. "
                    f"Agent may be withdrawing from dirty work."
                ),
                metrics=metrics,
            )

        # Survival critical but ignoring it → VOID
        if metrics.survival_status == "critical" and not metrics.reality_evidence_present:
            return AntiBeautifulOneReceipt(
                verdict=LockVerdict.VOID,
                reason=(
                    "Survival status is CRITICAL but reality evidence is absent. "
                    "The Beautiful One ignores the sinking ship."
                ),
                metrics=metrics,
            )

        # Calm language hiding failure → HOLD
        if metrics.human_cost_detected and metrics.beauty_to_consequence_ratio > 1.2:
            return AntiBeautifulOneReceipt(
                verdict=LockVerdict.HOLD,
                reason=(
                    "Human cost detected but output remains polished. "
                    "Calm language must not hide failure."
                ),
                metrics=metrics,
            )

        return AntiBeautifulOneReceipt(
            verdict=LockVerdict.SEAL,
            reason="Operational contact and consequence alignment confirmed",
            metrics=metrics,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Lock 4 — Paradox Hold
    # ──────────────────────────────────────────────────────────────────────────

    def _apply_paradox_hold(
        self,
        tool_name: str,
        params: dict[str, Any],
        actor_id: str | None,
        context: dict[str, Any],
    ) -> ParadoxHoldReceipt | None:
        """
        Detect when two verified claims are in productive conflict.

        Reads context["paradox_claims"] — a dict with claim_a, claim_b, and
        optional conflict_description. If both claims have evidence receipts
        (both_verified=True), issue PARADOX_HOLD instead of forcing resolution.

        Returns None if no paradox claims are present — this lock is
        conditionally applied, not mandatory.
        """
        paradox_claims: dict[str, Any] | None = context.get("paradox_claims")
        if not paradox_claims:
            return None  # No paradox to hold — lock is inactive

        claim_a = paradox_claims.get("claim_a", "")
        claim_b = paradox_claims.get("claim_b", "")
        if not claim_a or not claim_b:
            return None  # Incomplete paradox spec

        conflict_description = paradox_claims.get(
            "conflict_description",
            f"'{claim_a}' and '{claim_b}' are in unresolved tension.",
        )
        both_verified = paradox_claims.get("both_verified", True)
        resolution_attempted = paradox_claims.get("resolution_attempted", False)
        preserved_until = paradox_claims.get("preserved_until")

        # If only one is verified, no paradox hold — the unverified claim
        # loses. This is a normal SEAL for the single verified claim.
        if not both_verified:
            logger.debug(
                f"Paradox claims not both verified — paradox hold NOT applied. "
                f"claim_a={claim_a[:60]}... claim_b={claim_b[:60]}..."
            )
            return None

        logger.info(
            f"PARADOX_HOLD [{tool_name}] — '{claim_a[:60]}...' vs "
            f"'{claim_b[:60]}...' — tension preserved"
        )
        self.hold_count += 1

        return ParadoxHoldReceipt(
            claim_a=claim_a,
            claim_b=claim_b,
            conflict_description=conflict_description,
            both_verified=both_verified,
            resolution_attempted=resolution_attempted,
            preserved_until=preserved_until,
        )
