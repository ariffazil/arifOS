"""Phase 0d — a self-declared UNKNOWN evidence item must surface as unwitnessed.

Regression guard for the 2026-10-27 external-reality test: a judge run whose only
evidence was tagged UNKNOWN returned without any unwitnessed_evidence at all,
so the caller could not tell an unwitnessed claim from a witnessed one.

This test is EXPECTED TO FAIL on HEAD 843f3f0: the bridge path returns before
judge_postcondition is attached, therefore the field is ABSENT (not empty).
"""

from __future__ import annotations

import pytest

from arifosmcp.tools.judge import arif_judge

ACTOR = "phase0-unverified-actor"

EVIDENCE_B = [
    {
        "fact": "CVSS 9.2 for the referenced CVE",
        "source": "none",
        "tag": "UNKNOWN",
    }
]


def postcondition_of(response) -> dict:
    data = response.model_dump(mode="json") if hasattr(response, "model_dump") else dict(response)
    return ((data.get("meta") or {}).get("judge_postcondition")) or {}


@pytest.mark.asyncio
async def test_unknown_tagged_evidence_surfaces_as_unwitnessed():
    b = await arif_judge(
        mode="judge",
        actor_id=ACTOR,
        candidate="CVE severity is CVSS 9.2",
        evidence=EVIDENCE_B,
    )
    postcondition = postcondition_of(b)

    assert postcondition, (
        "judge_postcondition missing entirely: the verdict path returned before the "
        "evidence postcondition was attached, so no caller can see unwitnessed evidence."
    )
    assert postcondition.get("unwitnessed_evidence"), (
        "unwitnessed_evidence is empty for evidence tagged UNKNOWN with source='none'; "
        f"postcondition={postcondition}"
    )
