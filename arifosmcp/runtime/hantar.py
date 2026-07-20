"""
hantar.py — The Governed Inter-Node Envelope
=============================================

HANTAR is the mandatory envelope for all inter-node communication in the
arifOS federation. Every tool result, every organ handoff, every state
transfer MUST be wrapped in HANTAR.

Not raw dicts. Not string labels. A governed object with state, evidence,
repair routes, and witness requirements.

Grammar: WAJIB → HANTAR → SESAT → JALAN → BAIK → LANTAI → PARUT → TEBUS → SAKSI → LURUS

Forged: 2026-07-06 by FORGE (000Ω)
Source: /root/A-FORGE/forge_work/2026-07-06/SESAT_RESILIENCE_ZEN.md
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from arifosmcp.runtime.sesat_event import SesatEvent


class HantarState(str, Enum):
    LURUS = "LURUS"  # Clean proceed state
    SESAT = "SESAT"  # Failure detected
    HOLD = "HOLD"  # Waiting for human/external
    VOID = "VOID"  # Constitutionally prohibited


class OutputKind(str, Enum):
    TEXT = "text"
    ARTIFACT = "artifact"
    TOOL_RESULT = "tool_result"
    VERDICT = "verdict"
    OBSERVATION = "observation"
    ACTION_PLAN = "action_plan"


@dataclass
class HantarEvidence:
    """Evidence attached to the envelope."""

    sha256: str | None = None
    byte_length: int | None = None
    mime_type: str | None = None
    storage_uri: str | None = None
    access_method: str = (
        "local_only"  # telegram | scp | rsync | signed_url | inline | base64 | local_only
    )
    receipt_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class MaluState:
    """MALU scalar state in the envelope."""

    current_total: float = 0.0
    threshold_hold: float = 0.85

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_total": self.current_total,
            "threshold_hold": self.threshold_hold,
        }


@dataclass
class ParutState:
    """PARUT (scar memory) state in the envelope."""

    triggered: bool = False
    parut_id: str | None = None
    repeated_failure_count: int = 0
    constraint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class TebusState:
    """TEBUS (redemption) requirements in the envelope."""

    required: bool = False
    route: str | None = None
    saksi_required: bool = False
    evidence_required: list[str] = field(default_factory=list)
    resume_condition: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class HantarEnvelope:
    """The governed inter-node envelope. WAJIB on every communication.

    Every tool result, every organ handoff, every state transfer
    MUST be wrapped in this envelope. No raw dicts. No string labels.

    State must be one of: LURUS, SESAT, HOLD, VOID.
    If state = SESAT, sesat field MUST be populated.
    """

    id: str = field(default_factory=lambda: f"hantar-{uuid.uuid4().hex[:12]}")
    source_node: str = ""
    target_node: str = ""
    source_surface: str = ""
    target_surface: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    state: HantarState = HantarState.LURUS

    output_kind: OutputKind = OutputKind.TOOL_RESULT
    output_content: dict[str, Any] = field(default_factory=dict)

    affordance: dict[str, Any] = field(
        default_factory=lambda: {
            "requires_judge": False,
            "requires_seal": False,
        }
    )

    evidence: HantarEvidence = field(default_factory=HantarEvidence)

    sesat: SesatEvent | None = None

    malu: MaluState = field(default_factory=MaluState)
    parut: ParutState = field(default_factory=ParutState)
    tebus: TebusState = field(default_factory=TebusState)

    next_node: str | None = None

    def __post_init__(self) -> None:
        # If state is SESAT, sesat MUST be populated
        if self.state == HantarState.SESAT and self.sesat is None:
            self.sesat = SesatEvent(
                source_node=self.source_node,
                failed_claim="(auto-generated — caller did not provide SESAT)",
                observed_reality="State=SESAT but no SESAT event provided",
            )
        # If sesat is present, state MUST be SESAT
        if self.sesat is not None and self.state == HantarState.LURUS:
            self.state = HantarState.SESAT
        # If SESAT, TEBUS is required
        if self.state == HantarState.SESAT:
            self.tebus.required = True
            if self.sesat and self.sesat.saksi_required:
                self.tebus.saksi_required = True

    def to_dict(self) -> dict[str, Any]:
        result = {
            "id": self.id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "timestamp": self.timestamp,
            "state": self.state.value,
            "output": {
                "kind": self.output_kind.value,
                "content": self.output_content,
            },
            "affordance": self.affordance,
            "evidence": self.evidence.to_dict(),
            "malu": self.malu.to_dict(),
            "parut": self.parut.to_dict(),
            "tebus": self.tebus.to_dict(),
        }
        if self.sesat is not None:
            result["sesat"] = self.sesat.to_dict()
        if self.next_node is not None:
            result["next_node"] = self.next_node
        if self.source_surface:
            result["source_surface"] = self.source_surface
        if self.target_surface:
            result["target_surface"] = self.target_surface
        return result

    def to_json(self, indent: int = 2) -> str:
        import json

        return json.dumps(self.to_dict(), indent=indent)


def hantar_wrap(
    source_node: str,
    target_node: str,
    state: str | HantarState,
    output_content: dict[str, Any],
    output_kind: str | OutputKind = OutputKind.TOOL_RESULT,
    sesat: SesatEvent | None = None,
    malu_total: float = 0.0,
    **kwargs: Any,
) -> HantarEnvelope:
    """Convenience wrapper to create a HANTAR envelope.

    WAJIB: call this for every inter-node communication.
    """
    st = state if isinstance(state, HantarState) else HantarState(state)
    ok = output_kind if isinstance(output_kind, OutputKind) else OutputKind(output_kind)

    return HantarEnvelope(
        source_node=source_node,
        target_node=target_node,
        state=st,
        output_kind=ok,
        output_content=output_content,
        sesat=sesat,
        malu=MaluState(current_total=malu_total),
        **kwargs,
    )
