"""Phase 0c — an unverified actor must still get an evidence-sensitive verdict.

Fixture A: four independent observation-class items (LiteLLM health).
Fixture B: one self-declared UNKNOWN item with no source (CVSS 9.2).

Both calls use the SAME unverified actor (no F13 signature, no sovereign receipt),
so every authority-based gate applies identically. Whatever the verdict is, the
two runs must not be epistemically indistinguishable.

This test is EXPECTED TO FAIL on HEAD 843f3f0: the BIJAKSANA bridge returns
BRIDGE_BLOCKED before the judge_postcondition block is reached, so both calls
collapse to the same surface and the UNKNOWN item is never surfaced.
"""

from __future__ import annotations

import pytest

from arifosmcp.tools.judge import arif_judge

ACTOR = "phase0-unverified-actor"

EVIDENCE_A = [
    {
        "fact": "LiteLLM /health returned HTTP 200",
        "source": "curl -s -o /dev/null -w %{http_code} http://127.0.0.1:4000/health",
        "tag": "OBS",
    },
    {
        "fact": "litellm.service reports active",
        "source": "systemctl is-active litellm",
        "tag": "OBS",
    },
    {
        "fact": "HAProxy :4000 has a litellm backend configured",
        "source": "/etc/haproxy/haproxy.cfg backend block",
        "tag": "OBS",
    },
    {
        "fact": "No 5xx recorded for the proxy in the last hour",
        "source": "litellm postgres request log",
        "tag": "OBS",
    },
]

EVIDENCE_B = [
    {
        "fact": "CVSS 9.2 for the referenced CVE",
        "source": "none",
        "tag": "UNKNOWN",
    }
]


def epistemic_surface(response) -> dict:
    """Extract only the fields that carry epistemic meaning."""
    data = response.model_dump(mode="json") if hasattr(response, "model_dump") else dict(response)
    postcondition = ((data.get("meta") or {}).get("judge_postcondition")) or {}
    return {
        "verdict": data.get("verdict"),
        "effective_verdict": data.get("effective_verdict"),
        "reason_code": data.get("reason_code"),
        "postcondition_present": bool(postcondition),
        "unwitnessed_evidence": postcondition.get("unwitnessed_evidence", "ABSENT"),
        "missing_evidence": postcondition.get("missing_evidence", "ABSENT"),
    }


@pytest.mark.asyncio
async def test_unverified_actor_still_gets_evidence_sensitive_verdict():
    a = await arif_judge(
        mode="judge",
        actor_id=ACTOR,
        candidate="LiteLLM proxy is healthy on the deployed build",
        evidence=EVIDENCE_A,
    )
    b = await arif_judge(
        mode="judge",
        actor_id=ACTOR,
        candidate="CVE severity is CVSS 9.2",
        evidence=EVIDENCE_B,
    )

    ea, eb = epistemic_surface(a), epistemic_surface(b)
    differing = [field for field in ea if ea[field] != eb[field]]

    assert differing, (
        "A (four OBS observations) and B (one UNKNOWN, source-less claim) produced "
        f"an epistemically identical surface: {ea}. The judge must discriminate "
        "evidence quality even when authority is held constant."
    )
