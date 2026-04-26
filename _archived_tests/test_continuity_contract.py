import pytest

from arifosmcp.runtime import tools as runtime_tools
from arifosmcp.runtime.models import (
    CanonicalAuthority,
    ClaimStatus,
    RuntimeEnvelope,
    RuntimeStatus,
    Verdict,
)


@pytest.mark.asyncio
async def test_init_anchor_exposes_canonical_continuity_contract():
    envelope = await runtime_tools.init_anchor(
        actor_id="arif",
        intent="establish continuity contract",
        session_id="contract-init-001",
    )

    assert envelope.contract_version == "0.1.0"
    assert envelope.operator_summary is not None
    assert envelope.state is not None
    assert envelope.state["session"]["continuity_version"] == 1
    assert envelope.state["session"]["current_tool"] == "init_anchor"
    assert envelope.state["authorization"]["max_risk_tier"] == "low"
    assert envelope.handoff["produced_by"] == "init_anchor"
    assert envelope.payload["continuity"]["contract_version"] == "0.1.0"


@pytest.mark.asyncio
async def test_continuity_contract_persists_authority_across_tool_handoff(monkeypatch):
    session_id = "contract-handoff-002"
    await runtime_tools.init_anchor(
        actor_id="arif",
        intent="bootstrap continuity",
        session_id=session_id,
    )

    async def _stub_agi_mind(*args, **kwargs):
        return RuntimeEnvelope(
            ok=True,
            tool="agi_mind",
            stage="333_MIND",
            session_id=session_id,
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            authority=CanonicalAuthority(
                actor_id="arif",
                claim_status=ClaimStatus.CLAIMED,
                auth_state="claimed_only",
            ),
            allowed_next_tools=["asi_heart"],
            payload={
                "data": {
                    "coherence": {"verdict": "STABLE"},
                    "quad_witness_valid": False,
                    "session_continuity": {
                        "total_queries": 1,
                        "failed_queries": 0,
                        "success_rate": 1.0,
                    },
                }
            },
        )

    monkeypatch.setattr(runtime_tools, "_mega_agi_mind", _stub_agi_mind)

    envelope = await runtime_tools.agi_mind(
        mode="reason",
        query="reduce entropy",
        session_id=session_id,
        actor_id="arif",
    )

    assert envelope.state["session"]["continuity_version"] == 2
    assert envelope.state["session"]["previous_tool"] == "init_anchor"
    assert envelope.state["authorization"]["max_risk_tier"] == "low"
    assert envelope.operator_summary["privilege_drift"] == "None"
    assert envelope.state["governance_closure"]["proof_status"] == "incomplete"
    assert envelope.handoff["produced_by"] == "agi_mind"


@pytest.mark.asyncio
async def test_authority_widening_becomes_explicit_transition(monkeypatch):
    session_id = "contract-transition-003"
    await runtime_tools.init_anchor(
        actor_id="arif",
        intent="bootstrap authority snapshot",
        session_id=session_id,
    )

    async def _stub_asi_heart(*args, **kwargs):
        return RuntimeEnvelope(
            ok=True,
            tool="asi_heart",
            stage="666_HEART",
            session_id=session_id,
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            authority=CanonicalAuthority(
                actor_id="arif",
                claim_status=ClaimStatus.CLAIMED,
                auth_state="claimed_only",
            ),
            payload={
                "self_claim_boundary": {
                    "tools": {
                        "max_risk_tier": "high",
                        "allowed_modes": ["simulate"],
                    }
                }
            },
        )

    monkeypatch.setattr(runtime_tools, "_mega_asi_heart", _stub_asi_heart)

    envelope = await runtime_tools.asi_heart(
        mode="simulate",
        content="model consequences",
        session_id=session_id,
        actor_id="arif",
    )

    assert any(t["type"] == "authority_transition" for t in envelope.transitions)
    assert envelope.diagnostics["hard_guardrails"]["privilege_drift_detected"] is True
    assert envelope.state["authorization"]["max_risk_tier"] == "high"
