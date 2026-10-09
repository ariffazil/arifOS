"""P0 surface fix regression: authority_token must reach the F13 gate.

Gap history (2026-10-03): challenge-response machinery worked end-to-end
(issue → sign → verify TRUE in redis) but arif_judge's MCP surface never
exposed `authority_token`, so a correctly answered challenge had no path
back into the verdict — F13 HOLD forever, even with valid sovereign key.
"""

import inspect
import sys
from unittest.mock import patch

sys.path.insert(0, "/root/arifOS")


def test_judge_surface_exposes_authority_token():
    from arifosmcp.tools.judge import arif_judge

    params = inspect.signature(arif_judge).parameters
    assert "authority_token" in params, "arif_judge must expose authority_token"
    assert params["authority_token"].default is None


def test_intercept_forwards_authority_token_to_f13_gate():
    from arifosmcp.tools import arif_kernel_intercept as ik

    captured = {}

    def fake_verify(**kwargs):
        captured.update(kwargs)
        return True  # sovereign grant verified

    with patch.object(ik, "_verify_sovereign_token", side_effect=fake_verify):
        import asyncio

        res = asyncio.run(
            ik._arif_kernel_intercept(
                actor="ariffazil",
                intent="session close seal",
                requested_capability="kernel.seal",
                domain="governance",
                reversibility_level="irreversible",
                blast_radius="organ",
                authority_token="chal_test:grant_signed_payload",
            )
        )

    assert captured.get("token") == "chal_test:grant_signed_payload", (
        "F13 gate must receive the authority_token grant"
    )
    decision = str(res.get("decision") or res.get("status") or "").upper()
    assert decision not in ("DENY",), (
        "verified sovereign grant must not be denied at F13 gate"
    )
