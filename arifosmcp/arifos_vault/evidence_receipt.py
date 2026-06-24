"""
Evidence Receipt — Claim + witness chain.

F3 TRI-WITNESS: Human × AI × Earth must all witness every consequential claim.

Deepened for One Skill + One Tool (map + memory step):
- All receipts must carry restraint classification (from INIT geometry) and verdict trace.
- The One Skill (Knowing What NOT To Do) and One Tool (Verdict Loop) are inherited here for future refactors.
- No receipt without prior verdict loop passage.
"""

from __future__ import annotations

import time

from pydantic import BaseModel, Field


class Witness(BaseModel):
    """Single witness of a claim."""

    witness_type: str  # "human" | "ai" | "earth"
    witness_id: str  # arif | FORGE-000Ω | well_id | basin_name | etc.
    witness_attestation: str  # SEAL | SABAR | HOLD | VOID
    timestamp: str
    notes: str = ""


class EvidenceReceipt(BaseModel):
    """Claim + witness chain receipt."""

    claim: str
    claim_id: str
    truth_class: str  # FACT | INTERPRETATION | SPECULATION
    epistemic_status: str  # OBS | DER | INT | SPEC
    witnesses: list[Witness]
    source_refs: list[str] = Field(default_factory=list)
    session_id: str | None = None
    created_at: str = Field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

    def is_tri_witnessed(self) -> bool:
        types = {w.witness_type for w in self.witnesses}
        return types >= {"human", "ai", "earth"}

    def missing_witnesses(self) -> list[str]:
        types = {w.witness_type for w in self.witnesses}
        return [t for t in ("human", "ai", "earth") if t not in types]
