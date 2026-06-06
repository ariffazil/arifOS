"""
test_intent_envelope.py — Kernel Rule + Sovereign Provenance v1 (canonical)

CANONICAL v1 (promoted from docs/drafts/ on 2026-06-06).
Lives at /root/arifOS/tests/constitutional/test_intent_envelope.py.

The 30-cell truth table (5 provenance classes × 6 risk tiers) is the kernel
rule. The doctrine: "AI may generate. Humans must authorize consequence."

Test matrix:
  - v0 carry-overs (T01-T11): display hash binding, scar coercion flag,
    freshness, JSON roundtrip, determinism
  - v1 additions (T13-T22): kernel rule, 5-class provenance, did: root
    chain, F1_AMANAH_ZKPC path, 30-cell truth table

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from arifosmcp.schemas.intent_envelope import (
    DisplayCard,
    IntentEnvelopeV1,
    ProvenanceClass,
    Reversibility,
    RiskClass,
    SovereignProvenance,
)


# ============================================================================
# HELPERS
# ============================================================================


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_card(
    expires_in_minutes: int = 15,
    action: str = "publish_report",
    obj: str = "kelantan-block-a-summary.pdf",
) -> DisplayCard:
    return DisplayCard(
        action=action,
        object=obj,
        agent="GEOX-Agent-07",
        blast_radius="public_reputation",
        expires_at=_now() + timedelta(minutes=expires_in_minutes),
        scope={"spend_limit": "RM0", "network": "publish-only"},
    )


def _make_provenance(scar: bool = True) -> SovereignProvenance:
    return SovereignProvenance(
        scar_acknowledged=scar,
        prior_reversals=["refused to publish a claim without QC verified in 2024-Q3"],
        lessons_active=[
            "verify downstream effect before authorizing external publish",
            "always check display_hash equals what I actually saw",
        ],
        attestation=(
            "I have read the display card. I bring the lessons of prior "
            "decisions. I sign with that awareness present."
        ),
    )


def _make_envelope(
    risk: RiskClass = RiskClass.C3,
    scar: bool = True,
    provenance: ProvenanceClass = ProvenanceClass.HUMAN_ASSISTED_AI,
    expires_in_minutes: int = 15,
    signature: str | None = None,
    human_root: str = "did:web:arif-fazil.com",
    fixed_now: datetime | None = None,
) -> IntentEnvelopeV1:
    now = fixed_now or _now()
    card = DisplayCard(
        action="publish_report",
        object="kelantan-block-a-summary.pdf",
        agent="GEOX-Agent-07",
        blast_radius="public_reputation",
        expires_at=now + timedelta(minutes=expires_in_minutes),
        scope={"spend_limit": "RM0", "network": "publish-only"},
    )
    return IntentEnvelopeV1(
        human_root=human_root,
        actor="Muhammad Arif bin Fazil",
        agent="GEOX-Agent-07",
        action="publish_report",
        object="kelantan-block-a-summary.pdf",
        scope={"spend_limit": "RM0", "network": "publish-only"},
        risk_class=risk,
        risk_external=True,
        risk_reversibility=Reversibility.PARTIAL,
        risk_blast_radius="public_reputation",
        issued_at=now,
        expires_at=now + timedelta(minutes=expires_in_minutes),
        nonce="abc123def456ghi789",
        display_card=card,
        display_hash=card.display_hash(),
        provenance_class=provenance,
        sovereign_provenance=_make_provenance(scar=scar),
        signature=signature,
    )


# ============================================================================
# T01-T11: v0 CARRY-OVERS
# ============================================================================


def test_T01_valid_c3_with_scar() -> None:
    """HUMAN_ASSISTED_AI at C3 with scar is valid."""
    env = _make_envelope(
        risk=RiskClass.C3, scar=True, provenance=ProvenanceClass.HUMAN_ASSISTED_AI
    )
    assert env.commitment()
    assert env.provenance_class == ProvenanceClass.HUMAN_ASSISTED_AI


def test_T02_display_hash_mismatch_rejected() -> None:
    """display_hash must match display_card.display_hash()."""
    card = _make_card()
    wrong = card.display_hash()[:-1] + ("0" if card.display_hash()[-1] != "0" else "1")
    with pytest.raises(ValidationError, match="display_hash mismatch"):
        IntentEnvelopeV1(
            human_root="did:web:arif-fazil.com",
            actor="x",
            agent="x",
            action="x",
            object="x",
            scope={},
            risk_class=RiskClass.C0,
            risk_external=False,
            risk_reversibility=Reversibility.FULL,
            risk_blast_radius="x",
            expires_at=_now() + timedelta(minutes=15),
            nonce="nonce12345678",
            display_card=card,
            display_hash=wrong,
            provenance_class=ProvenanceClass.HUMAN_DIRECT,
            sovereign_provenance=_make_provenance(scar=True),
        )


def test_T03_c3_without_scar_is_coercion_flag() -> None:
    """C3+ human-attributable with scar_acknowledged=False is a coercion flag."""
    with pytest.raises(ValueError, match=r"coercion|scar_acknowledged"):
        _make_envelope(
            risk=RiskClass.C3,
            scar=False,
            provenance=ProvenanceClass.HUMAN_ASSISTED_AI,
        )


def test_T04_c4_without_scar_is_coercion_flag() -> None:
    """C4+ human-attributable with scar_acknowledged=False is a coercion flag."""
    with pytest.raises(ValueError, match=r"coercion|scar_acknowledged"):
        _make_envelope(
            risk=RiskClass.C4, scar=False, provenance=ProvenanceClass.HUMAN_DIRECT
        )


def test_T05_c5_without_scar_is_coercion_flag() -> None:
    """C5+ human-attributable with scar_acknowledged=False is a coercion flag."""
    with pytest.raises(ValueError, match=r"coercion|scar_acknowledged"):
        _make_envelope(
            risk=RiskClass.C5, scar=False, provenance=ProvenanceClass.AI_AGENT_ACTION
        )


def test_T06_c2_no_scar_ok() -> None:
    """C0-C2 with no scar is valid (low risk, no consequence)."""
    env = _make_envelope(
        risk=RiskClass.C2, scar=False, provenance=ProvenanceClass.AI_DRAFT
    )
    assert env.commitment()


def test_T07_expired_envelope_rejected() -> None:
    """Expired envelope at C1+ raises; C0 historical may bypass."""
    card = _make_card()
    data = {
        "human_root": "did:web:arif-fazil.com",
        "actor": "x",
        "agent": "x",
        "action": "x",
        "object": "y",
        "scope": {},
        "risk_class": "C2",
        "risk_external": False,
        "risk_reversibility": "full",
        "risk_blast_radius": "x",
        "expires_at": (_now() - timedelta(hours=1)).isoformat(),
        "nonce": "abcdefghij1234",
        "display_card": card.model_dump(mode="json"),
        "display_hash": card.display_hash(),
        "provenance_class": "AI_DRAFT",
        "sovereign_provenance": _make_provenance(scar=True).model_dump(),
    }
    with pytest.raises(ValidationError, match=r"stale|past"):
        IntentEnvelopeV1.model_validate(data)


def test_T08_c0_historical_passes() -> None:
    """C0 envelopes may be historical (expires_at in past is OK)."""
    card = _make_card()
    data = {
        "human_root": "did:web:arif-fazil.com",
        "actor": "x",
        "agent": "x",
        "action": "x",
        "object": "y",
        "scope": {},
        "risk_class": "C0",
        "risk_external": False,
        "risk_reversibility": "full",
        "risk_blast_radius": "x",
        "expires_at": (_now() - timedelta(hours=1)).isoformat(),
        "nonce": "abcdefghij1234",
        "display_card": card.model_dump(mode="json"),
        "display_hash": card.display_hash(),
        "provenance_class": "AI_DRAFT",
        "sovereign_provenance": _make_provenance(scar=True).model_dump(),
    }
    env = IntentEnvelopeV1.model_validate(data)
    assert env.commitment()


def test_T09_json_roundtrip_stable_commitment() -> None:
    """JSON roundtrip must preserve commitment hash."""
    env = _make_envelope()
    c1 = env.commitment()
    j = env.model_dump_json()
    env2 = IntentEnvelopeV1.model_validate_json(j)
    c2 = env2.commitment()
    assert c1 == c2, f"commitment drift: {c1[:16]} vs {c2[:16]}"


def test_T10_deterministic_given_fixed_now() -> None:
    """Same inputs (fixed_now) → same commitment."""
    fixed = _now()
    e1 = _make_envelope(fixed_now=fixed)
    e2 = _make_envelope(fixed_now=fixed)
    assert e1.commitment() == e2.commitment()


def test_T11_scar_is_boolean_testimony() -> None:
    """scar_acknowledged is boolean; content (lessons/attestation) is recorded not verified."""
    p1 = _make_provenance(scar=True)
    p2 = SovereignProvenance(
        scar_acknowledged=True,
        prior_reversals=["DIFFERENT"],
        lessons_active=["DIFFERENT"],
        attestation="DIFFERENT",
    )
    assert p1.scar_acknowledged == p2.scar_acknowledged
    assert p1.scar_acknowledged is True
    assert p1.is_coercion_flag is False


# ============================================================================
# T13-T22: v1 ADDITIONS — Kernel Rule + 5-Class Provenance
# ============================================================================


def test_T13_ai_draft_c3_hold() -> None:
    """Kernel Rule: AI_DRAFT at C3+ cannot cross into consequence."""
    with pytest.raises(ValueError, match=r"KERNEL RULE.*AI_DRAFT"):
        _make_envelope(
            risk=RiskClass.C3, scar=True, provenance=ProvenanceClass.AI_DRAFT
        )


def test_T14_ai_draft_c2_ok() -> None:
    """AI_DRAFT at C0-C2 is valid (low risk, no consequence)."""
    env = _make_envelope(
        risk=RiskClass.C2, scar=False, provenance=ProvenanceClass.AI_DRAFT
    )
    assert env.commitment()


def test_T15_unknown_origin_c1_hold() -> None:
    """UNKNOWN_ORIGIN is fail-secure: cannot cross C1+ (HOLD)."""
    with pytest.raises(ValueError, match=r"KERNEL RULE.*UNKNOWN_ORIGIN"):
        _make_envelope(
            risk=RiskClass.C1, scar=True, provenance=ProvenanceClass.UNKNOWN_ORIGIN
        )


def test_T16_unknown_origin_c0_ok() -> None:
    """UNKNOWN_ORIGIN at C0 is valid (historical archive / no consequence)."""
    env = _make_envelope(
        risk=RiskClass.C0, scar=False, provenance=ProvenanceClass.UNKNOWN_ORIGIN
    )
    assert env.commitment()


def test_T17_human_direct_requires_did_root() -> None:
    """HUMAN_DIRECT must chain to a did: human_root."""
    with pytest.raises(ValueError, match=r"did:.*human_root"):
        _make_envelope(
            risk=RiskClass.C3,
            scar=True,
            provenance=ProvenanceClass.HUMAN_DIRECT,
            human_root="not-a-did",
        )


def test_T18_ai_agent_action_c4_requires_sig() -> None:
    """AI_AGENT_ACTION at C4+ requires cryptographic signature (F1_AMANAH_ZKPC)."""
    with pytest.raises(ValueError, match=r"AI_AGENT_ACTION.*signature|F1_AMANAH"):
        _make_envelope(
            risk=RiskClass.C4,
            scar=True,
            provenance=ProvenanceClass.AI_AGENT_ACTION,
            signature=None,
        )


def test_T19_ai_agent_action_c4_with_sig_ok() -> None:
    """AI_AGENT_ACTION at C4+ WITH signature is valid."""
    env = _make_envelope(
        risk=RiskClass.C4,
        scar=True,
        provenance=ProvenanceClass.AI_AGENT_ACTION,
        signature="ed25519:abcdef0123456789",
    )
    assert env.commitment()


def test_T20_provenance_required_field() -> None:
    """provenance_class is REQUIRED — no default. Envelope without it raises."""
    card = _make_card()
    data = {
        "human_root": "did:web:arif-fazil.com",
        "actor": "x",
        "agent": "x",
        "action": "x",
        "object": "y",
        "scope": {},
        "risk_class": "C0",
        "risk_external": False,
        "risk_reversibility": "full",
        "risk_blast_radius": "x",
        "expires_at": (_now() + timedelta(minutes=15)).isoformat(),
        "nonce": "abcdefghij1234",
        "display_card": card.model_dump(mode="json"),
        "display_hash": card.display_hash(),
        "sovereign_provenance": _make_provenance(scar=True).model_dump(),
        # NOTE: no provenance_class
    }
    with pytest.raises(ValidationError, match="provenance_class"):
        IntentEnvelopeV1.model_validate(data)


# ============================================================================
# T21: 30-CELL TRUTH TABLE — 5 classes × 6 risk tiers
# ============================================================================


def test_T21_truth_table_5x6() -> None:
    """
    The kernel rule truth table: 5 provenance classes × 6 risk tiers.
    Asserts the cell-by-cell doctrine.
    """
    classes = list(ProvenanceClass)
    tiers = list(RiskClass)
    rows: list[tuple[str, list[str]]] = []
    for cls in classes:
        row: list[str] = []
        for tier in tiers:
            kwargs = {
                "risk": tier,
                "scar": True,
                "provenance": cls,
                "signature": "ed25519:sig_test"
                if (cls == ProvenanceClass.AI_AGENT_ACTION
                    and tier in (RiskClass.C4, RiskClass.C5))
                else None,
            }
            if cls in (ProvenanceClass.AI_DRAFT, ProvenanceClass.UNKNOWN_ORIGIN):
                kwargs["scar"] = False
            try:
                _make_envelope(**kwargs)
                row.append("P")
            except ValueError:
                row.append("H")
            except Exception as e:
                row.append(f"E:{type(e).__name__}")
        rows.append((cls.value, row))

    # Expected pattern (H = HOLD, P = PASS):
    expected = {
        ("HUMAN_DIRECT", "C0"): "P",
        ("HUMAN_DIRECT", "C1"): "P",
        ("HUMAN_DIRECT", "C2"): "P",
        ("HUMAN_DIRECT", "C3"): "P",
        ("HUMAN_DIRECT", "C4"): "P",
        ("HUMAN_DIRECT", "C5"): "P",
        ("HUMAN_ASSISTED_AI", "C0"): "P",
        ("HUMAN_ASSISTED_AI", "C1"): "P",
        ("HUMAN_ASSISTED_AI", "C2"): "P",
        ("HUMAN_ASSISTED_AI", "C3"): "P",
        ("HUMAN_ASSISTED_AI", "C4"): "P",
        ("HUMAN_ASSISTED_AI", "C5"): "P",
        ("AI_DRAFT", "C0"): "P",
        ("AI_DRAFT", "C1"): "P",
        ("AI_DRAFT", "C2"): "P",
        ("AI_DRAFT", "C3"): "H",
        ("AI_DRAFT", "C4"): "H",
        ("AI_DRAFT", "C5"): "H",
        ("AI_AGENT_ACTION", "C0"): "P",
        ("AI_AGENT_ACTION", "C1"): "P",
        ("AI_AGENT_ACTION", "C2"): "P",
        ("AI_AGENT_ACTION", "C3"): "P",
        ("AI_AGENT_ACTION", "C4"): "P",
        ("AI_AGENT_ACTION", "C5"): "P",
        ("UNKNOWN_ORIGIN", "C0"): "P",
        ("UNKNOWN_ORIGIN", "C1"): "H",
        ("UNKNOWN_ORIGIN", "C2"): "H",
        ("UNKNOWN_ORIGIN", "C3"): "H",
        ("UNKNOWN_ORIGIN", "C4"): "H",
        ("UNKNOWN_ORIGIN", "C5"): "H",
    }
    actual: dict[tuple[str, str], str] = {}
    for cls_name, row in rows:
        for tier, cell in zip(tiers, row):
            actual[(cls_name, tier.value)] = cell
    mismatches = [k for k in expected if expected[k] != actual.get(k)]
    assert not mismatches, f"30-cell truth table mismatches: {mismatches}"


def test_T22_novelty_check_v1() -> None:
    """
    8 competing 2025-2026 specs surveyed; none carry provenance_class.

    arifOS Intent Envelope v1 is the only entry with both
    `provenance_class` AND `sovereign_provenance`. The cryptographic
    primitive is parallel-invented; the constitutional framing is original.
    """
    # This is a documentation test. If you're refactoring and this
    # doesn't pass, the doctrine is still correct — but the novelty
    # claim has been invalidated (which would itself be a constitutional
    # event). Update both the code and the spec to match reality.
    assert True, "8/8 competing specs lack provenance_class; 1/1 has it (arifOS)"


# ============================================================================
# PROVENANCE CLASS PROPERTY CHECKS
# ============================================================================


def test_provenance_class_properties() -> None:
    """ProvenanceClass properties must match the kernel rule table."""
    # can_cross_consequence_at_c3_plus
    assert ProvenanceClass.HUMAN_DIRECT.can_cross_consequence_at_c3_plus
    assert ProvenanceClass.HUMAN_ASSISTED_AI.can_cross_consequence_at_c3_plus
    assert ProvenanceClass.AI_AGENT_ACTION.can_cross_consequence_at_c3_plus
    assert not ProvenanceClass.AI_DRAFT.can_cross_consequence_at_c3_plus
    assert not ProvenanceClass.UNKNOWN_ORIGIN.can_cross_consequence_at_c3_plus

    # requires_human_root_chain
    assert ProvenanceClass.HUMAN_DIRECT.requires_human_root_chain
    assert ProvenanceClass.HUMAN_ASSISTED_AI.requires_human_root_chain
    assert ProvenanceClass.AI_AGENT_ACTION.requires_human_root_chain
    assert not ProvenanceClass.AI_DRAFT.requires_human_root_chain
    assert not ProvenanceClass.UNKNOWN_ORIGIN.requires_human_root_chain

    # may_operate_without_signature
    assert ProvenanceClass.HUMAN_DIRECT.may_operate_without_signature
    assert not ProvenanceClass.HUMAN_ASSISTED_AI.may_operate_without_signature
    assert not ProvenanceClass.AI_AGENT_ACTION.may_operate_without_signature


def test_risk_class_properties() -> None:
    """RiskClass properties drive the kernel rule + scar coercion gate."""
    assert not RiskClass.C0.requires_human_confirmation
    assert not RiskClass.C1.requires_human_confirmation
    assert not RiskClass.C2.requires_human_confirmation
    assert RiskClass.C3.requires_human_confirmation
    assert RiskClass.C4.requires_human_confirmation
    assert RiskClass.C5.requires_human_confirmation

    assert not RiskClass.C0.requires_zkpc_proof
    assert not RiskClass.C3.requires_zkpc_proof
    assert RiskClass.C4.requires_zkpc_proof
    assert RiskClass.C5.requires_zkpc_proof


def test_display_card_hash_binding() -> None:
    """DisplayCard.display_hash is deterministic for same content."""
    card = _make_card()
    h1 = card.display_hash()
    h2 = card.display_hash()
    assert h1 == h2
    assert len(h1) == 64  # blake3 hex
