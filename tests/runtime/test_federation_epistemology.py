from __future__ import annotations

from arifosmcp.runtime.federation_epistemology import FederationEpistemicLedger
from arifosmcp.runtime.server import app as server_app
from arifosmcp.schemas.claim import (
    AuthorityClass,
    ClaimPolarity,
    EpistemicEventType,
    FederationEpistemicEvent,
)
from tests.conftest import SyncASGIClient


def _seed_env(monkeypatch, tmp_path) -> None:
    vault_dir = tmp_path / "VAULT999"
    monkeypatch.setenv("VAULT999_PATH", str(vault_dir))
    monkeypatch.setenv("ARIFOS_VAULT_DIR", str(vault_dir))


def test_belief_state_synthesizes_sealed_federation_claim(monkeypatch, tmp_path) -> None:
    _seed_env(monkeypatch, tmp_path)
    ledger = FederationEpistemicLedger()
    try:
        for event in (
            FederationEpistemicEvent(
                subject_id="well-17",
                subject_name="Well 17",
                claim_id="claim-fracture-viable",
                claim_text="Well 17 shows fracture viability",
                predicate="has_fracture_viability",
                node_id="GEOX",
                agent_role="earth_intelligence_processor",
                authority_class=AuthorityClass.GROUND_EVIDENCE,
                confidence=0.93,
                evidence_refs=["geo-log-17"],
                witness_required=True,
            ),
            FederationEpistemicEvent(
                subject_id="well-17",
                subject_name="Well 17",
                claim_id="claim-fracture-viable",
                claim_text="Well 17 shows fracture viability",
                predicate="has_fracture_viability",
                event_type=EpistemicEventType.VERIFICATION,
                node_id="Hermes",
                agent_role="deliberative_relay",
                authority_class=AuthorityClass.DELIBERATIVE_JUDGMENT,
                confidence=0.88,
                evidence_refs=["geo-log-17", "fracture-verify-1"],
                witness_required=True,
            ),
            FederationEpistemicEvent(
                subject_id="well-17",
                subject_name="Well 17",
                claim_id="claim-fracture-viable",
                claim_text="Well 17 shows fracture viability",
                predicate="has_fracture_viability",
                event_type=EpistemicEventType.DECISION,
                node_id="WEALTH",
                agent_role="capital_intelligence_processor",
                authority_class=AuthorityClass.CAPITAL_ANALYSIS,
                confidence=0.74,
                evidence_refs=["emv-sheet-17"],
                decision_refs=["capital-alloc-17"],
            ),
            FederationEpistemicEvent(
                subject_id="well-17",
                subject_name="Well 17",
                claim_id="claim-fracture-viable",
                claim_text="Well 17 shows fracture viability",
                predicate="has_fracture_viability",
                event_type=EpistemicEventType.SEAL,
                node_id="Hermes",
                agent_role="deliberative_relay",
                authority_class=AuthorityClass.GOVERNANCE_CONTROL,
                confidence=0.91,
                evidence_refs=["seal-999-17"],
                seal_level="999",
                claim_status="sealed",
            ),
        ):
            ledger.record_event(event)

        state = ledger.belief_state(subject_id="well-17")
    finally:
        ledger.close()

    assert state["status"] == "ok"
    assert state["federation_position"] == "sealed"
    assert state["subject_id"] == "well-17"
    assert set(state["contributors"]) == {"GEOX", "Hermes", "WEALTH"}
    assert state["witness_status"] == "trace-complete"
    assert state["claims"][0]["state"] == "sealed"
    assert state["claims"][0]["decision_refs"] == ["capital-alloc-17"]


def test_belief_state_marks_contested_claims(monkeypatch, tmp_path) -> None:
    _seed_env(monkeypatch, tmp_path)
    ledger = FederationEpistemicLedger()
    try:
        ledger.record_event(
            FederationEpistemicEvent(
                subject_id="project-x",
                subject_name="Project X",
                claim_id="claim-project-x-positive",
                claim_text="Project X should proceed",
                predicate="is_capital_positive",
                node_id="WEALTH",
                agent_role="capital_intelligence_processor",
                authority_class=AuthorityClass.CAPITAL_ANALYSIS,
                confidence=0.86,
                evidence_refs=["emv-x-1"],
            )
        )
        ledger.record_event(
            FederationEpistemicEvent(
                subject_id="project-x",
                subject_name="Project X",
                claim_id="claim-project-x-positive",
                claim_text="Project X should proceed",
                predicate="is_capital_positive",
                event_type=EpistemicEventType.ASSERTION,
                polarity=ClaimPolarity.CONTRADICTS,
                node_id="Hermes",
                agent_role="deliberative_relay",
                authority_class=AuthorityClass.DELIBERATIVE_JUDGMENT,
                confidence=0.82,
                evidence_refs=["delib-x-2"],
                witness_required=True,
            )
        )
        state = ledger.belief_state(subject_id="project-x")
        audit = ledger.witness_audit(subject_id="project-x")
    finally:
        ledger.close()

    assert state["claims"][0]["state"] == "contested"
    assert audit["status"] == "trace-partial"
    assert "witness_missing" in audit["gaps"]


def test_federation_belief_routes(monkeypatch, tmp_path) -> None:
    _seed_env(monkeypatch, tmp_path)
    ledger = FederationEpistemicLedger()
    try:
        ledger.record_event(
            FederationEpistemicEvent(
                subject_id="well-42",
                subject_name="Well 42",
                claim_id="claim-well-42-fracture",
                claim_text="Well 42 has fracture signal",
                predicate="has_fracture_signal",
                node_id="GEOX",
                agent_role="earth_intelligence_processor",
                authority_class=AuthorityClass.GROUND_EVIDENCE,
                confidence=0.9,
                evidence_refs=["geo-log-42"],
            )
        )
    finally:
        ledger.close()

    client = SyncASGIClient(server_app)

    belief_response = client.get("/federation/beliefs?subject_id=well-42")
    assert belief_response.status_code == 200
    belief_payload = belief_response.json()
    assert belief_payload["subject_id"] == "well-42"
    assert belief_payload["claims"][0]["predicate"] == "has_fracture_signal"

    witness_response = client.get("/federation/witness?claim_id=claim-well-42-fracture")
    assert witness_response.status_code == 200
    assert witness_response.json()["claim_id"] == "claim-well-42-fracture"
