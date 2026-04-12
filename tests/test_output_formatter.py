from __future__ import annotations

from arifosmcp.runtime.models import (
    CanonicalAuthority,
    ClaimStatus,
    RiskClass,
    RuntimeEnvelope,
    RuntimeStatus,
    Verdict,
    VerdictCode,
    VerdictDetail,
)
from arifosmcp.runtime.output_formatter import format_output


def _build_envelope() -> RuntimeEnvelope:
    return RuntimeEnvelope(
        ok=True,
        tool="arifos_kernel",
        canonical_tool_name="arifos_kernel",
        stage="444_ROUTER",
        status=RuntimeStatus.SUCCESS,
        verdict=Verdict.SEAL,
        verdict_detail=VerdictDetail(
            code=VerdictCode.SEAL,
            reason_code="OK_ALL_PASS",
            message="Routing is allowed within the current governed scope.",
        ),
        risk_class=RiskClass.MEDIUM,
        session_id="sess-output-001",
        platform_context="mcp",
        authority=CanonicalAuthority(
            actor_id="arif",
            claim_status=ClaimStatus.CLAIMED,
        ),
        operator_summary={
            "identity": "Declared as arif; not verified",
            "session": "anchored and continuous",
            "authority": "query, reflect modes, max risk medium",
            "governance": "pass / proof incomplete",
        },
        next_action={"next_step": "Call arifos_heart before execution."},
        hint="Call arifos_heart before execution.",
        payload={"canonical_tool_name": "arifos_kernel"},
    )


def test_format_output_exposes_human_language_and_universal_context() -> None:
    output = format_output(_build_envelope())

    assert output["human_language"]["summary"].startswith("Routing completed.")
    assert output["human_language"]["next_step"] == "Call arifos_heart before execution."
    assert output["universal_context"] == {
        "actor": "arif",
        "session": "sess-output-001",
        "verified": False,
        "risk": "medium",
        "platform": "mcp",
        "tool": "arifos_kernel",
        "stage": "444_ROUTER",
    }


def test_format_output_api_uses_shared_human_language_contract() -> None:
    envelope = _build_envelope()
    envelope.platform_context = "api"

    output = format_output(envelope)

    assert "payload" not in output
    assert output["human_language"]["summary"].startswith("Routing completed.")
    assert output["universal_context"]["tool"] == "arifos_kernel"
    assert output["execution"]["status"] == "OK"
    assert output["governance"]["verdict"] == "SEAL"
