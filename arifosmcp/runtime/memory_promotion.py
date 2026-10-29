"""memory_promotion.py — the deterministic promotion gate.

FI-003, 2026-10-29 — Phase 4, per ARIFOS::TTME_MEMORY_METABOLISM_EXECUTION.

What this decides
-----------------
Whether ONE typed experience record may move up the promotion ladder. It is a
pure function: same record + same inputs -> same decision, every time. It
reads no clock except the one passed in, touches no file, and mutates nothing.

GRAMMAR IS SEPARATE, ON PURPOSE
-------------------------------
The decisions below (PROMOTE / REVIEW / REJECT / HOLD / UNKNOWN) are
MEMORY-PROMOTION grammar. They are NOT constitutional verdicts. In particular
the word HOLD here means "a human must arbitrate this record", and MUST NOT be
passed to arif_judge, arif_seal, or any gate that expects a constitutional
verdict. Every result carries ``decision_grammar: "memory_promotion/1.0"`` so
the two vocabularies cannot be confused by a downstream consumer.

PROMOTE means ELIGIBLE — it never makes a record ACTIVE on its own. ACTIVE is
an authority step (F13). The gate's highest effect is "REVIEWED: eligible for
ratification".

Why this exists
---------------
The 2026-10-29 audit found the promotion ladder had a field but no engine:
CHRON's own promotion gate reports "external validation is not implemented", so
0 of 14 lessons ever reached ACTIVE. This module is that missing half —
deterministic, testable, and wired to the typed contract
(arifosmcp/runtime/contracts/experience-memory.schema.json).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from typing import Any, Iterable

from arifosmcp.runtime.experience_memory import ExperienceMemory

DECISION_GRAMMAR = "memory_promotion/1.0"

# ── decisions ───────────────────────────────────────────────────────────────
PROMOTE = "PROMOTE"
REVIEW = "REVIEW"
REJECT = "REJECT"
HOLD = "HOLD"
UNKNOWN = "UNKNOWN"

DECISIONS = (PROMOTE, REVIEW, REJECT, HOLD, UNKNOWN)

# ── reason codes ────────────────────────────────────────────────────────────
# The mandate's twelve, plus four extensions this substrate needed. Every code
# is emitted with the decision; the caller sees ALL gaps, not just the first.
MISSING_PROVENANCE = "MISSING_PROVENANCE"
MISSING_OUTCOME = "MISSING_OUTCOME"
NO_CHECKER_EVIDENCE = "NO_CHECKER_EVIDENCE"
SCOPE_TOO_BROAD = "SCOPE_TOO_BROAD"
CONTRADICTORY_EVIDENCE = "CONTRADICTORY_EVIDENCE"
NO_CONSUMER = "NO_CONSUMER"
SELF_VALIDATION_ONLY = "SELF_VALIDATION_ONLY"
DUPLICATE = "DUPLICATE"
LOW_INFORMATION = "LOW_INFORMATION"
TEST_ACTOR_ONLY = "TEST_ACTOR_ONLY"
EXPIRED = "EXPIRED"
INVALID_SCHEMA = "INVALID_SCHEMA"
# extensions
NO_FALSIFIER = "NO_FALSIFIER"            # criterion 6 needs a reason code
NOT_REVERSIBLE = "NOT_REVERSIBLE"        # criterion 9
AUTHORITY_CLAIM = "AUTHORITY_CLAIM"      # criterion 10 (memory may not claim law)
INDEPENDENCE_NOT_VERIFIED = "INDEPENDENCE_NOT_VERIFIED"  # criterion 11

REASON_CODES = frozenset(
    {
        MISSING_PROVENANCE,
        MISSING_OUTCOME,
        NO_CHECKER_EVIDENCE,
        SCOPE_TOO_BROAD,
        CONTRADICTORY_EVIDENCE,
        NO_CONSUMER,
        SELF_VALIDATION_ONLY,
        DUPLICATE,
        LOW_INFORMATION,
        TEST_ACTOR_ONLY,
        EXPIRED,
        INVALID_SCHEMA,
        NO_FALSIFIER,
        NOT_REVERSIBLE,
        AUTHORITY_CLAIM,
        INDEPENDENCE_NOT_VERIFIED,
    }
)

# Reason codes that make a record never promotable as-is.
REJECT_CODES = frozenset(
    {
        INVALID_SCHEMA,
        LOW_INFORMATION,
        TEST_ACTOR_ONLY,
        SELF_VALIDATION_ONLY,
        AUTHORITY_CLAIM,
        EXPIRED,
        NOT_REVERSIBLE,
    }
)
# Reason codes that need a human to arbitrate.
HOLD_CODES = frozenset({CONTRADICTORY_EVIDENCE})


class PromotionDecision:
    """The result of one gate evaluation."""

    def __init__(
        self,
        decision: str,
        reason_codes: Iterable[str],
        *,
        next_promotion_status: str,
        notes: Iterable[str] = (),
    ) -> None:
        self.decision = decision
        self.reason_codes = sorted(set(reason_codes))
        self.next_promotion_status = next_promotion_status
        self.notes = list(notes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_grammar": DECISION_GRAMMAR,
            "decision": self.decision,
            "reason_codes": list(self.reason_codes),
            "next_promotion_status": self.next_promotion_status,
            "notes": list(self.notes),
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"PromotionDecision({self.decision}, {self.reason_codes})"


def fingerprint(memory: ExperienceMemory) -> str:
    """Stable fingerprint for near-duplicate detection.

    Normalised on the distilled lesson (falling back to the observation), so
    two records saying the same thing in the same words collide, and two
    records saying it differently do not.
    """
    body = (memory.distilled_lesson or memory.observation or "").strip().lower()
    body = " ".join(body.split())
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def _is_test_actor(memory: ExperienceMemory) -> bool:
    """Test/synthetic provenance, read from the preserved original payload."""
    payload = memory.source_payload or {}
    actor = str(payload.get("actor_id") or memory.actor_id or "")
    session = str(payload.get("session_id") or "")
    if actor.startswith("test-actor"):
        return True
    if "audit-session" in session:
        return True
    return actor == "arifos-federation" and session.startswith("audit-session")


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001 — an unparseable date is simply unknown
        return None


def evaluate_promotion(
    memory: ExperienceMemory,
    *,
    duplicate_of: str | None = None,
    contradictions: list[str] | None = None,
    independent_verified: bool | None = None,
    now: datetime | None = None,
) -> PromotionDecision:
    """Evaluate one record against the promotion criteria. Pure.

    Parameters
    ----------
    duplicate_of:
        fingerprint of an equivalent record already in the store. A duplicate
        is REVIEW, not a new promotion — duplicates are linked, not multiplied.
    contradictions:
        contradictions found against this record. Any contradiction means a
        human must arbitrate: HOLD.
    independent_verified:
        whether an independent verifier has checked this record. None means
        "not verified", False means "verified as self-approval only".
    now:
        clock, injected so expiry is testable and deterministic.
    """
    now = now or datetime.now(timezone.utc)
    codes: list[str] = []
    notes: list[str] = []

    # ── 0. schema validity ────────────────────────────────────────────────
    if memory.schema_version != "experience-memory/1.0" or not memory.memory_id:
        codes.append(INVALID_SCHEMA)

    # ── 1. low information / test-only provenance ─────────────────────────
    body = (memory.distilled_lesson or memory.observation or "").strip()
    if memory.memory_class == "NOISE" or len(body) <= 2:
        codes.append(LOW_INFORMATION)
    if _is_test_actor(memory):
        codes.append(TEST_ACTOR_ONLY)

    # ── 2. provenance ──────────────────────────────────────────────────────
    has_provenance = bool(
        memory.actor_id or memory.evidence_refs or memory.source_record_id
    )
    if not has_provenance:
        codes.append(MISSING_PROVENANCE)

    # ── 3. outcome must be typed and observed ──────────────────────────────
    if memory.outcome in ("UNKNOWN", "UNOBSERVED"):
        codes.append(MISSING_OUTCOME)

    # ── 4. checker evidence (or its explicit absence) ─────────────────────
    if not memory.checker_type and not memory.outcome_evidence:
        codes.append(NO_CHECKER_EVIDENCE)

    # ── 5. scope must be bounded ──────────────────────────────────────────
    if not memory.applicability_scope:
        codes.append(SCOPE_TOO_BROAD)

    # ── 6. falsifier must be declared ─────────────────────────────────────
    if not memory.falsifier:
        codes.append(NO_FALSIFIER)

    # ── 7. contradictions ──────────────────────────────────────────────────
    if contradictions:
        codes.append(CONTRADICTORY_EVIDENCE)
        notes.append(f"{len(contradictions)} contradiction(s) recorded")

    # ── 8. a target consumer must exist ───────────────────────────────────
    if not memory.eligible_consumers:
        codes.append(NO_CONSUMER)

    # ── 9. reversibility ───────────────────────────────────────────────────
    if memory.reversible is False:
        codes.append(NOT_REVERSIBLE)
    elif memory.reversible is None and memory.promotion_status in ("CANDIDATE", "REVIEWED"):
        notes.append("reversibility not declared")

    # ── 10. memory may not claim authority ────────────────────────────────
    if memory.authorized_by and memory.promotion_status != "ACTIVE":
        codes.append(AUTHORITY_CLAIM)
        notes.append("record carries an authorization it has not been granted")

    # ── 11. independence ──────────────────────────────────────────────────
    proposer = memory.proposed_by or memory.actor_id
    verifier = memory.verified_by or memory.reviewed_by
    if proposer and verifier and proposer == verifier and independent_verified is not True:
        codes.append(SELF_VALIDATION_ONLY)
    if independent_verified is False:
        codes.append(SELF_VALIDATION_ONLY)
    elif independent_verified is None and memory.promotion_status in ("CANDIDATE", "REVIEWED"):
        codes.append(INDEPENDENCE_NOT_VERIFIED)

    # ── 12. duplicates are linked, not multiplied ─────────────────────────
    if duplicate_of:
        codes.append(DUPLICATE)
        notes.append(f"equivalent record already present: {duplicate_of}")

    # ── 13. expiry ────────────────────────────────────────────────────────
    expires = _parse_ts(memory.expires_at)
    if expires is not None and expires <= now:
        codes.append(EXPIRED)

    # ── resolution ────────────────────────────────────────────────────────
    if any(c in REJECT_CODES for c in codes):
        decision = REJECT
    elif any(c in HOLD_CODES for c in codes):
        decision = HOLD
    elif codes:
        decision = REVIEW
    else:
        decision = PROMOTE

    if decision == PROMOTE:
        # ELIGIBLE. ACTIVE is an authority step (F13) and is NOT taken here.
        next_status = "REVIEWED"
        notes.append("eligible for ratification; ACTIVE requires authority (F13)")
    elif decision == REVIEW:
        next_status = "CANDIDATE"
    elif decision == HOLD:
        next_status = "CANDIDATE"
    elif decision == REJECT:
        next_status = "REJECTED"
    else:
        next_status = "RAW"

    return PromotionDecision(decision, codes, next_promotion_status=next_status, notes=notes)


def evaluate_payload(
    payload: dict[str, Any],
    **kwargs: Any,
) -> PromotionDecision:
    """Evaluate a raw dict (legacy row) by adapting it first."""
    from arifosmcp.runtime.experience_memory import (
        from_adaptation,
        from_chron_lesson,
        from_dream_proposal,
        from_rsi_decision,
        from_seal_c_proposal,
    )

    # A typed memory object is evaluated as-is: re-adapting it would strip the
    # fields the gate reads (the adapters exist for LEGACY rows).
    if "memory_class" in payload and "schema_version" in payload:
        try:
            typed = ExperienceMemory.model_validate(payload)
        except Exception as exc:  # noqa: BLE001 — an invalid object is a schema failure
            return PromotionDecision(
                UNKNOWN,
                [INVALID_SCHEMA],
                next_promotion_status="RAW",
                notes=[f"typed object failed validation: {type(exc).__name__}"],
            )
        return evaluate_promotion(typed, **kwargs)

    # A typed memory object is evaluated as-is: re-adapting it would strip the
    # fields the gate reads (the adapters exist for LEGACY rows).
    if "memory_class" in payload and "schema_version" in payload:
        try:
            typed = ExperienceMemory.model_validate(payload)
        except Exception as exc:  # noqa: BLE001 — an invalid object is a schema failure
            return PromotionDecision(
                UNKNOWN,
                [INVALID_SCHEMA],
                next_promotion_status="RAW",
                notes=[f"typed object failed validation: {type(exc).__name__}"],
            )
        return evaluate_promotion(typed, **kwargs)

    surface = str(payload.get("source_surface") or payload.get("_surface") or "")
    if not surface:
        if "lesson_id" in payload:
            surface = "chron_lesson"
        elif "decision_id" in payload:
            surface = "rsi_decision"
        elif "proposition" in payload:
            surface = "dream_proposal"
        elif "measured_delta" in payload or "falsifier" in payload:
            surface = "adaptation"
        elif "proposal_id" in payload:
            surface = "seal_c_proposal"
    adapter = {
        "chron_lesson": from_chron_lesson,
        "rsi_decision": from_rsi_decision,
        "dream_proposal": from_dream_proposal,
        "adaptation": from_adaptation,
        "seal_c_proposal": from_seal_c_proposal,
    }.get(surface)
    if adapter is None:
        return PromotionDecision(
            UNKNOWN,
            [INVALID_SCHEMA],
            next_promotion_status="RAW",
            notes=[f"no adapter for surface {surface!r}"],
        )
    memory = adapter(payload)
    return evaluate_promotion(memory, **kwargs)


def main(argv: list[str] | None = None) -> int:
    """CLI: evaluate a memory JSON file and print the decision.

    This is the route for other organs (e.g. CHRON) that must not import
    arifOS: they call this as a subprocess and read the JSON on stdout.
    """
    ap = argparse.ArgumentParser(description="Evaluate one memory record for promotion.")
    ap.add_argument("path", help="path to a JSON memory object")
    ap.add_argument("--duplicate-of", default=None)
    ap.add_argument("--contradictions", default=None, help="comma-separated contradiction notes")
    ap.add_argument("--independent-verified", choices=("true", "false"), default=None)
    args = ap.parse_args(argv)

    with open(args.path, encoding="utf-8") as fh:
        payload = json.load(fh)

    kwargs: dict[str, Any] = {}
    if args.duplicate_of:
        kwargs["duplicate_of"] = args.duplicate_of
    if args.contradictions:
        kwargs["contradictions"] = [c.strip() for c in args.contradictions.split(",") if c.strip()]
    if args.independent_verified is not None:
        kwargs["independent_verified"] = args.independent_verified == "true"

    result = evaluate_payload(payload, **kwargs)
    json.dump(result.to_dict(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.decision in (PROMOTE, REVIEW, HOLD, UNKNOWN) else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
