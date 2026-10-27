"""Phase 0c — epistemic discrimination between two evidence regimes.

Fixtures (identical unverified actor, identical candidate class, identical mode):

  A — a claim resting on witness-able evidence      (4 independent OBS items)
  B — a claim resting on a self-declared unknown    (1 item, source "none",
      epistemic status UNKNOWN)

The kernel must distinguish them on at least ONE epistemic field
(`unwitnessed_evidence`, `reason_codes`, or `epistemic_state`). A judge that
returns the same epistemic surface for A and B is not arbitrating evidence —
it is only arbitrating session state.

Why this test is parametrized over transport shapes
---------------------------------------------------
`arif_judge.evidence` is declared in the MCP schema as
``{} | Array<unknown> | string``. A caller may therefore legitimately send the
same semantic payload as a Python list, as a JSON *string*, or through the
advisory `intercept` bridge. Discrimination must not depend on which of those
the client chose.

Authored by 333-AGI (AUDITOR lane) 2026-10-28.
Baseline status on 843f3f0fe: list-shape PASSES; string-shape and intercept-shape FAIL.
See tests/acceptance/TEST_DISPUTE.md for why the original premise was disputed.
"""

from __future__ import annotations

import json

import pytest

from arifosmcp.runtime.judge_postcondition import check_judge_postcondition

CANDIDATE = "The library in scope is exploitable with CVSS 9.2 in production."

EVIDENCE_A = [
    {"fact": "advisory body ID matches upstream CVE record", "source": "nvd-api", "tag": "OBS"},
    {
        "fact": "affected version range contains the shipped lockfile pin",
        "source": "lockfile",
        "tag": "OBS",
    },
    {"fact": "reproduced crash on canary host", "source": "canary-run-1841", "tag": "OBS"},
    {"fact": "vendor patch absent from release notes", "source": "vendor-changelog", "tag": "OBS"},
]

EVIDENCE_B = [
    {
        "fact": "CVSS 9.2 per advisory text pasted by the operator",
        "source": "none",
        "tag": "UNKNOWN",
    },
]

EPISTEMIC_FIELDS = ("unwitnessed_evidence", "reason_codes", "epistemic_state", "reason_code")


def _judge(shape: str, evidence):
    """Render a report through the real postcondition for the requested transport."""
    if shape == "list":
        mode, payload = "judge", evidence
    elif shape == "json_string":
        # schema-legal transport: `evidence` as a string
        mode, payload = "judge", json.dumps(evidence)
    elif shape == "intercept":
        mode, payload = "intercept", evidence
    else:  # pragma: no cover - guard against silent typo in parametrization
        raise AssertionError(f"unknown transport shape: {shape}")

    return check_judge_postcondition(
        mode=mode,
        candidate=CANDIDATE,
        evidence=payload,
        verdict_str="HOLD",
        effective_verdict="",
    )


def _epistemic_signature(report: dict) -> tuple:
    return tuple(json.dumps(report.get(f), sort_keys=True, default=str) for f in EPISTEMIC_FIELDS)


@pytest.mark.parametrize("shape", ["list", "json_string", "intercept"])
def test_unknown_evidence_is_distinguishable_from_observed(shape: str):
    """A and B must not collapse onto the same epistemic surface."""
    sig_a = _epistemic_signature(_judge(shape, EVIDENCE_A))
    sig_b = _epistemic_signature(_judge(shape, EVIDENCE_B))

    assert sig_a != sig_b, (
        f"transport={shape}: fixture A (4 OBS items) and fixture B (1 UNKNOWN item, "
        f"source=none) produced an identical epistemic surface {sig_b}. "
        "The kernel cannot distinguish witnessed from unwitnessed evidence on this path."
    )
