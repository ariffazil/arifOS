"""
Contradiction Memory — Item 3b of the Organ Forge
═════════════════════════════════════════════════

When two organs disagree on the same artifact, the disagreement is
a first-class event in L4 (structured) and L5 (relational), not
a buried log line.

The store tracks:
  - the disputed artifact
  - the contradicting evidence entries
  - the parties (organs, actors)
  - the witness count (how many independent organs side with each)
  - the resolution (if any)

After N=3 repeated contradictions on the same artifact, the dispute
promotes itself to a HOLD trigger — the executive must rule.

DITEMPA BUKAN DIBERI — disagreement is the immune system.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from arifosmcp.schemas.envelope import ContradictionEntry, EvidenceEnvelope

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# RECORDS
# ═══════════════════════════════════════════════════════════════════════════════


class DisputedArtifact(BaseModel):
    """The thing being contradicted."""

    artifact_ref: str  # e.g. a claim_id, evidence_id, or geo feature
    description: str = ""


class ContradictionSide(BaseModel):
    """One side of a contradiction."""

    evidence_ref: str
    envelope: Optional[EvidenceEnvelope] = Field(
        default=None,
        description="The full envelope — optional if we only have a ref",
    )
    organ: str
    epistemic_tag: str
    summary: str
    weight: float = 1.0
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ContradictionRecord(BaseModel):
    """A full contradiction event."""

    contradiction_id: str = Field(default_factory=lambda: f"ctr_{uuid4().hex[:12]}")
    artifact: DisputedArtifact
    sides: list[ContradictionSide] = Field(default_factory=list)
    opened_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved: bool = False
    resolution: Optional[str] = None
    hold_triggered: bool = False
    recurrence_count: int = 1  # how many times this artifact has been disputed


# ═══════════════════════════════════════════════════════════════════════════════
# THE STORE — in-memory reference; can be backed by L4 (Supabase)
# ═══════════════════════════════════════════════════════════════════════════════


class ContradictionStore:
    """In-process contradiction memory. Persist to L4 in production."""

    def __init__(self, hold_threshold: int = 3):
        # artifact_ref → list[ContradictionRecord]
        self._by_artifact: dict[str, list[ContradictionRecord]] = defaultdict(list)
        self._hold_threshold = hold_threshold

    def record_contradiction(
        self,
        *,
        artifact_ref: str,
        artifact_kind: str,
        description: str,
        contradictor_envelope: EvidenceEnvelope,
        original_envelope: EvidenceEnvelope,
        summary: str = "",
    ) -> ContradictionRecord:
        """Record a new contradiction. Returns the (possibly merged) record.

        If the artifact has been disputed before, we increment
        recurrence_count. If it crosses the threshold, hold_triggered=True.
        """
        side_a = ContradictionSide(
            evidence_ref=original_envelope.envelope_id,
            envelope=original_envelope,
            organ=original_envelope.source.organ,
            epistemic_tag=original_envelope.epistemic_tag.value,
            summary="Original claim",
        )
        side_b = ContradictionSide(
            evidence_ref=contradictor_envelope.envelope_id,
            envelope=contradictor_envelope,
            organ=contradictor_envelope.source.organ,
            epistemic_tag=contradictor_envelope.epistemic_tag.value,
            summary=summary or "Contradicting claim",
        )

        existing = self._by_artifact[artifact_ref]
        if existing:
            # Merge: bump recurrence, append the new side
            head = existing[0]
            head.recurrence_count += 1
            head.sides.append(side_b)
            head.hold_triggered = head.recurrence_count >= self._hold_threshold
            if head.hold_triggered:
                logger.warning(
                    f"Contradiction {head.contradiction_id} on {artifact_ref} "
                    f"hit threshold {self._hold_threshold} — HOLD triggered"
                )
            return head

        rec = ContradictionRecord(
            artifact=DisputedArtifact(
                artifact_ref=artifact_ref,
                artifact_kind=artifact_kind,
                description=description,
            ),
            sides=[side_a, side_b],
            recurrence_count=1,
            hold_triggered=False,
        )
        self._by_artifact[artifact_ref].append(rec)
        return rec

    def record_from_envelope(
        self,
        envelope: EvidenceEnvelope,
        *,
        artifact_ref: Optional[str] = None,
        artifact_kind: str = "evidence",
        description: str = "",
    ) -> list[ContradictionRecord]:
        """Convenience: read contradictions off an envelope and record them all.

        The envelope's ``contradictions`` list contains the refs. We need
        the original envelopes to register them as sides — for that, the
        caller should have them. Here we record the envelope as side B
        with the contradiction list preserved.
        """
        records: list[ContradictionRecord] = []
        for ctr in envelope.contradictions:
            # We have the contradicting ref but not the original envelope.
            # In a real system, fetch it from L4. Here we record the bare
            # contradiction so the store knows about it.
            side = ContradictionSide(
                evidence_ref=ctr.evidence_ref,
                organ=ctr.organ,
                epistemic_tag=ctr.epistemic_tag.value,
                summary=ctr.summary,
                weight=ctr.weight,
            )
            artifact = artifact_ref or envelope.envelope_id
            existing = self._by_artifact[artifact]
            if existing:
                head = existing[0]
                head.recurrence_count += 1
                head.sides.append(side)
                head.hold_triggered = head.recurrence_count >= self._hold_threshold
                records.append(head)
            else:
                # New dispute: this side is the opening side. The other side
                # is the *envelope itself* acting as the first witness.
                opening_side = ContradictionSide(
                    evidence_ref=envelope.envelope_id,
                    envelope=envelope,
                    organ=envelope.source.organ,
                    epistemic_tag=envelope.epistemic_tag.value,
                    summary="Opening witness",
                )
                rec = ContradictionRecord(
                    artifact=DisputedArtifact(
                        artifact_ref=artifact,
                        artifact_kind=artifact_kind,
                        description=description,
                    ),
                    sides=[opening_side, side],
                    recurrence_count=1,
                    hold_triggered=False,
                )
                self._by_artifact[artifact].append(rec)
                records.append(rec)
        return records

    def get(self, artifact_ref: str) -> list[ContradictionRecord]:
        return list(self._by_artifact.get(artifact_ref, []))

    def open_disputes(self) -> list[ContradictionRecord]:
        out: list[ContradictionRecord] = []
        for recs in self._by_artifact.values():
            for r in recs:
                if not r.resolved:
                    out.append(r)
        return out

    def holds_pending(self) -> list[ContradictionRecord]:
        return [r for r in self.open_disputes() if r.hold_triggered]

    def resolve(self, artifact_ref: str, resolution: str) -> bool:
        recs = self._by_artifact.get(artifact_ref, [])
        for r in recs:
            if not r.resolved:
                r.resolved = True
                r.resolution = resolution
                r.hold_triggered = False  # resolved = no longer holding
                return True
        return False

    def stats(self) -> dict[str, Any]:
        all_recs = [r for recs in self._by_artifact.values() for r in recs]
        return {
            "total_artifacts_disputed": len(self._by_artifact),
            "total_contradiction_events": len(all_recs),
            "open_disputes": len(self.open_disputes()),
            "holds_pending": len(self.holds_pending()),
            "hold_threshold": self._hold_threshold,
        }


# Module-level singleton (suitable for in-process use)
_store: Optional[ContradictionStore] = None


def get_store() -> ContradictionStore:
    global _store
    if _store is None:
        _store = ContradictionStore()
    return _store
