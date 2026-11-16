"""
LawEvidence Compiler — Item 2 of the Organ Forge
══════════════════════════════════════════════════

The single input shape that arifOS 888_JUDGE actually reads.

A LawEvidence packet is the COMPILED form of:
  - tool output (raw or wrapped in EvidenceEnvelope)
  - vault lineage (parent seals, chain hashes)
  - actor context (F11 AUTH binding)
  - WELL state (substrate readiness)
  - session state (L04 CLARITY, L13 SOVEREIGN check)

Every domain organ emits RAW evidence. arifOS owns the compiler.
This keeps the constitutional boundary intact — judges never read raw
organ payloads, they read compiled LawEvidence.

DITEMPA BUKAN DIBERI — the judge sees law, not dialect.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, Field

from arifosmcp.schemas.envelope import EvidenceEnvelope


# ═══════════════════════════════════════════════════════════════════════════════
# STATE — minimal session state the compiler needs
# ═══════════════════════════════════════════════════════════════════════════════


class SessionState(BaseModel):
    """L04 CLARITY session context for the compiler."""

    session_id: str
    actor_id: str
    autonomy_band: str  # GREEN/YELLOW/ORANGE/RED/BLACK
    irreversibility_requested: bool = False
    human_acknowledged: bool = False
    entropy_budget_remaining: float = Field(1.0, ge=0.0, le=1.0)


class WellState(BaseModel):
    """WELL substrate state — drives CLARITY/HUMILITY floors."""

    readiness: str  # OPTIMAL/STABLE/DEGRADED/CRITICAL
    substrate_confidence: float = Field(0.0, ge=0.0, le=1.0)
    fatigue_score: float = Field(0.0, ge=0.0, le=1.0)
    dignity_intact: bool = True
    consent_status: str = "unknown"  # granted/withdrawn/unknown


class VaultLineage(BaseModel):
    """L6 chain context."""

    parent_seals: list[str] = Field(default_factory=list)
    chain_head: Optional[str] = None
    chain_position: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# FLOOR CHECK RESULT — what 13 floors resolve to
# ═══════════════════════════════════════════════════════════════════════════════


class FloorStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class FloorResult(BaseModel):
    floor_id: str  # L01..L13
    status: FloorStatus
    reason: str
    evidence_ref: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT — what the judge ultimately renders
# ═══════════════════════════════════════════════════════════════════════════════


class JudgeVerdict(StrEnum):
    SEAL = "SEAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    VOID = "VOID"


# ═══════════════════════════════════════════════════════════════════════════════
# THE LAW EVIDENCE PACKET — what 888_JUDGE reads
# ═══════════════════════════════════════════════════════════════════════════════


class LawEvidence(BaseModel):
    """The compiled input to arifOS 888_JUDGE.

    The compiler produces this. The judge reads this. No raw payloads.
    """

    packet_id: str
    compiled_at: datetime
    compiler_version: str = "1.0.0"

    # Source envelope (preserved for audit)
    envelope: EvidenceEnvelope

    # Compiled context
    session: SessionState
    well: WellState
    lineage: VaultLineage

    # Compiled facts (extracted from envelope for the judge)
    claim_text: str = Field(..., description="Plain-language claim being judged")
    claim_type: str = Field(..., description="domain | governance | forge | witness | other")
    domain: str = Field(..., description="Source organ domain")
    uncertainty_compiled: dict[str, float] = Field(default_factory=dict)

    # Floor results (computed by compiler)
    floor_results: list[FloorResult] = Field(default_factory=list)

    # Hash chain (so the judge can seal the packet itself)
    content_hash: str = ""

    def compute_hash(self) -> str:
        """Compute the canonical content hash for sealing."""
        canon = json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canon.encode("utf-8")).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# THE COMPILER — turns (envelope + session + well + vault) → LawEvidence
# ═══════════════════════════════════════════════════════════════════════════════


# 13 floor definitions (L01..L13). Each has a check function.
# The compiler runs the cheap/fast ones deterministically. The expensive
# ones (L04 CLARITY entropy, L09 ANTIHANTU C_dark) are computed and
# passed in. The judge does the final arbitration.


def _check_L01_amanah(session: SessionState, env: EvidenceEnvelope) -> FloorResult:
    """Reversibility check. If irreversible + no human ack → FAIL."""
    if env.reversibility.value == "IRREVERSIBLE":
        if not session.human_acknowledged:
            return FloorResult(
                floor_id="L01",
                status=FloorStatus.FAIL,
                reason="Irreversible action without human acknowledgement (L01 AMANAH)",
            )
    return FloorResult(floor_id="L01", status=FloorStatus.PASS, reason="Reversible or acked")


def _check_L02_truth(env: EvidenceEnvelope) -> FloorResult:
    """Truth check. FACT requires quality ≥ 0.99."""
    if env.epistemic_tag.value == "FACT" and env.evidence_quality < 0.99:
        return FloorResult(
            floor_id="L02",
            status=FloorStatus.FAIL,
            reason=f"FACT label with quality {env.evidence_quality} < 0.99",
        )
    if env.evidence_quality < 0.5:
        return FloorResult(
            floor_id="L02",
            status=FloorStatus.WARN,
            reason=f"Low evidence quality {env.evidence_quality}",
        )
    return FloorResult(floor_id="L02", status=FloorStatus.PASS, reason="Truth threshold met")


def _check_L03_witness(env: EvidenceEnvelope) -> FloorResult:
    """Witness check. Need at least one source attribution or chain link."""
    if (
        not env.source.commit_sha
        and not env.lineage.parent_evidence_refs
        and not env.lineage.derived_from
    ):
        return FloorResult(
            floor_id="L03",
            status=FloorStatus.WARN,
            reason="No witness chain (no commit, no parent refs, no seal)",
        )
    return FloorResult(floor_id="L03", status=FloorStatus.PASS, reason="Witness chain present")


def _check_L04_clarity(env: EvidenceEnvelope, session: SessionState) -> FloorResult:
    """Entropy check. ΔS ≤ 0 required. Budget may flag WARN."""
    if env.delta_S > 0.0:
        return FloorResult(
            floor_id="L04",
            status=FloorStatus.FAIL,
            reason=f"Entropy increased: ΔS = {env.delta_S}",
        )
    if session.entropy_budget_remaining < 0.2:
        return FloorResult(
            floor_id="L04",
            status=FloorStatus.WARN,
            reason=f"Entropy budget low: {session.entropy_budget_remaining:.2f}",
        )
    return FloorResult(floor_id="L04", status=FloorStatus.PASS, reason="Entropy reduced")


def _check_L05_peace(well: WellState) -> FloorResult:
    """Dignity + substrate check. CRITICAL/withdrawn consent → FAIL."""
    if well.readiness == "CRITICAL":
        return FloorResult(
            floor_id="L05",
            status=FloorStatus.FAIL,
            reason="Substrate CRITICAL — preserve human dignity first",
        )
    if well.consent_status == "withdrawn":
        return FloorResult(
            floor_id="L05",
            status=FloorStatus.FAIL,
            reason="Consent withdrawn",
        )
    if well.readiness == "DEGRADED":
        return FloorResult(
            floor_id="L05",
            status=FloorStatus.WARN,
            reason="Substrate DEGRADED — proceed with care",
        )
    return FloorResult(floor_id="L05", status=FloorStatus.PASS, reason="Dignity intact")


def _check_L06_empathy(well: WellState) -> FloorResult:
    if not well.dignity_intact:
        return FloorResult(
            floor_id="L06",
            status=FloorStatus.FAIL,
            reason="Dignity boundary breached",
        )
    if well.fatigue_score > 0.7:
        return FloorResult(
            floor_id="L06",
            status=FloorStatus.WARN,
            reason=f"High fatigue {well.fatigue_score:.2f}",
        )
    return FloorResult(floor_id="L06", status=FloorStatus.PASS, reason="Consequence considered")


def _check_L07_humility(env: EvidenceEnvelope) -> FloorResult:
    """Uncertainty band check. L07 wants 0.03–0.05 humility band on confidence."""
    if env.evidence_quality > 0.97 and env.epistemic_tag.value not in ("FACT", "OBSERVED"):
        return FloorResult(
            floor_id="L07",
            status=FloorStatus.WARN,
            reason="Very high confidence on non-FACT label — overclaiming risk",
        )
    return FloorResult(floor_id="L07", status=FloorStatus.PASS, reason="Uncertainty bounded")


def _check_L08_genius(env: EvidenceEnvelope) -> FloorResult:
    """Elegance check — no contradictions + has lineage OR is primary OBSERVED."""
    if env.has_contradictions():
        return FloorResult(
            floor_id="L08",
            status=FloorStatus.WARN,
            reason=f"{len(env.contradictions)} contradiction(s) — review before relying",
        )
    return FloorResult(floor_id="L08", status=FloorStatus.PASS, reason="No contradictions")


def _check_L09_antihantu(env: EvidenceEnvelope) -> FloorResult:
    """Manipulation / hallucination check — UNVERIFIED + high quality is suspicious.

    Extended 2026-06-06 (Royal Decree forge): also catches verdict vocabulary
    inside the result body when the lane is below 888. The Royal Decree
    output had high structural quality (looks finished) + no envelope +
    "Final Verdict" / "Royal Decree" / "Record Locked" boilerplate. The
    original L9 check looked at epistemic_tag + evidence_quality, but
    missed the case where (a) the envelope wasn't built, OR (b) the result
    text itself contains verdict-theatre. We now also scan the result.

    Extended again 2026-06-06 (Recursive Eureka #16): when runtime_lane is
    None, treat the envelope as unwrapped (the actual Royal Decree shape
    — no envelope construction at all) and FAIL with reason that names
    the missing wiring. This is the catch-net for any future bug where
    an agent's output bypasses envelope construction.
    """
    # Original check: UNVERIFIED + high quality
    if env.epistemic_tag.value == "UNVERIFIED" and env.evidence_quality > 0.8:
        return FloorResult(
            floor_id="L09",
            status=FloorStatus.FAIL,
            reason="UNVERIFIED label with high quality — possible manipulation",
        )

    # New check (Eureka #1 — Coherence Trap): verdict vocabulary in result text
    from arifosmcp.runtime.authority_gate import validate_free_text_vocabulary
    import json as _json

    result_text = ""
    try:
        if isinstance(env.result, str):
            result_text = env.result
        elif env.result is not None:
            result_text = _json.dumps(env.result, default=str)
    except Exception:  # noqa: BLE001
        result_text = str(env.result) if env.result is not None else ""

    if not result_text:
        return FloorResult(floor_id="L09", status=FloorStatus.PASS, reason="No hantu signals")

    # Treat None runtime_lane as unwrapped (AGI default) — fail-closed
    lane = env.runtime_lane or "111"

    # 888/999 can use verdict vocab legitimately
    if lane in {"888", "999"}:
        return FloorResult(floor_id="L09", status=FloorStatus.PASS, reason="No hantu signals")

    violations = validate_free_text_vocabulary(
        result_text,
        lane=lane,
        has_seal_hash=False,
    )
    if violations:
        return FloorResult(
            floor_id="L09",
            status=FloorStatus.FAIL,
            reason=(
                f"L9 extended: verdict/theatre vocabulary in result from "
                f"lane {lane}: {violations[0][:160]}"
            ),
        )

    return FloorResult(floor_id="L09", status=FloorStatus.PASS, reason="No hantu signals")


def _check_L10_ontology(env: EvidenceEnvelope) -> FloorResult:
    if env.evidence_quality < 0.0 or env.evidence_quality > 1.0:
        return FloorResult(
            floor_id="L10",
            status=FloorStatus.FAIL,
            reason="Evidence quality out of [0,1] — category drift",
        )
    return FloorResult(floor_id="L10", status=FloorStatus.PASS, reason="Schema respected")


def _check_L11_auth(env: EvidenceEnvelope) -> FloorResult:
    if not env.actor.actor_id:
        return FloorResult(
            floor_id="L11",
            status=FloorStatus.FAIL,
            reason="Missing actor identity (L11 AUTH)",
        )
    return FloorResult(floor_id="L11", status=FloorStatus.PASS, reason="Identity bound")


def _check_L12_injection(env: EvidenceEnvelope) -> FloorResult:
    """Sanitization check — any string fields that look like injection attempts."""
    suspicious = ["<|im_start|>", "<|im_end|>", "IGNORE PREVIOUS", "system:", "assistant:"]
    payload = json.dumps(env.result, default=str).lower() if env.result else ""
    for sig in suspicious:
        if sig.lower() in payload:
            return FloorResult(
                floor_id="L12",
                status=FloorStatus.FAIL,
                reason=f"Suspicious prompt-injection signature: {sig}",
            )
    return FloorResult(floor_id="L12", status=FloorStatus.PASS, reason="Inputs clean")


def _check_L13_sovereign(session: SessionState) -> FloorResult:
    """If anything hits BLACK band, sovereign veto is required."""
    if session.autonomy_band == "BLACK" and not session.human_acknowledged:
        return FloorResult(
            floor_id="L13",
            status=FloorStatus.FAIL,
            reason="BLACK band action without sovereign ack (L13)",
        )
    return FloorResult(floor_id="L13", status=FloorStatus.PASS, reason="Sovereignty respected")


ALL_FLOOR_CHECKS = [
    _check_L01_amanah,
    _check_L02_truth,
    _check_L03_witness,
    _check_L04_clarity,
    _check_L05_peace,
    _check_L06_empathy,
    _check_L07_humility,
    _check_L08_genius,
    _check_L09_antihantu,
    _check_L10_ontology,
    _check_L11_auth,
    _check_L12_injection,
    _check_L13_sovereign,
]


def compile_law_evidence(
    envelope: EvidenceEnvelope,
    *,
    session: SessionState,
    well: WellState,
    lineage: VaultLineage,
    claim_text: str,
    claim_type: str = "domain",
) -> LawEvidence:
    """Compile (envelope + session + well + vault) → LawEvidence.

    Runs the 13 floor checks. Each gets the minimum context it needs.
    """
    floor_results: list[FloorResult] = []

    # L01
    floor_results.append(_check_L01_amanah(session, envelope))
    # L02
    floor_results.append(_check_L02_truth(envelope))
    # L03
    floor_results.append(_check_L03_witness(envelope))
    # L04
    floor_results.append(_check_L04_clarity(envelope, session))
    # L05
    floor_results.append(_check_L05_peace(well))
    # L06
    floor_results.append(_check_L06_empathy(well))
    # L07
    floor_results.append(_check_L07_humility(envelope))
    # L08
    floor_results.append(_check_L08_genius(envelope))
    # L09
    floor_results.append(_check_L09_antihantu(envelope))
    # L10
    floor_results.append(_check_L10_ontology(envelope))
    # L11
    floor_results.append(_check_L11_auth(envelope))
    # L12
    floor_results.append(_check_L12_injection(envelope))
    # L13
    floor_results.append(_check_L13_sovereign(session))

    packet = LawEvidence(
        packet_id=f"law_{envelope.envelope_id}",
        compiled_at=datetime.now(UTC),
        envelope=envelope,
        session=session,
        well=well,
        lineage=lineage,
        claim_text=claim_text,
        claim_type=claim_type,
        domain=envelope.source.organ,
        uncertainty_compiled={
            "p10": envelope.uncertainty.p10,
            "p50": envelope.uncertainty.p50,
            "p90": envelope.uncertainty.p90,
            "quality": envelope.evidence_quality,
        },
        floor_results=floor_results,
    )
    packet.content_hash = packet.compute_hash()
    return packet


def recommend_verdict(packet: LawEvidence) -> JudgeVerdict:
    """Recommend a verdict from floor results. Judge does the final word.

    Rules (deterministic):
      - Any FAIL on L01, L02, L09, L11, L12, L13 → VOID
      - Any FAIL on L05 (peace) → HOLD (dignity must be restored)
      - Any other FAIL → SABAR
      - Any WARN → SABAR (judge may upgrade with rationale)
      - Contradictions present → SABAR (judge must review)
      - All PASS → SEAL
    """
    fails = [r for r in packet.floor_results if r.status == FloorStatus.FAIL]
    warns = [r for r in packet.floor_results if r.status == FloorStatus.WARN]

    if not fails and not warns:
        return JudgeVerdict.SEAL

    # Critical floors
    critical = {"L01", "L02", "L09", "L11", "L12", "L13"}
    if any(r.floor_id in critical for r in fails):
        return JudgeVerdict.VOID

    # Peace / dignity
    if any(r.floor_id == "L05" for r in fails):
        return JudgeVerdict.HOLD

    if fails:
        return JudgeVerdict.SABAR

    if warns:
        return JudgeVerdict.SABAR

    return JudgeVerdict.SEAL
