"""Regression (2026-11-13): arif_judge must ADVERTISE its non-repudiation carrier.

Gate 2 in tools/judge.py refuses irreversible actions without actor_signature.
The public schema is additionalProperties:false, so if the carrier is stripped
from the advertised surface, strict MCP clients can never satisfy Gate 2.
"""
from arifosmcp.runtime.public_registry import _STRIP_UNADVERTISED_PARAMS

CARRIER = {"actor_signature", "nonce", "key_id", "authority_token"}


def test_judge_carrier_not_stripped():
    stripped = _STRIP_UNADVERTISED_PARAMS.get("arif_judge", set())
    assert not (CARRIER & stripped), f"carrier stripped: {CARRIER & stripped}"


def test_init_carrier_not_stripped():
    stripped = _STRIP_UNADVERTISED_PARAMS.get("arif_init", set())
    assert not ({"actor_signature", "nonce"} & stripped)
