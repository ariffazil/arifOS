"""S3 regression — human-reality queries must not be routed to domain organs.

Discovered 2026-10-17 (FI-008): the lane classifier already returned CARE for
Malay grief/feeling queries, but the *organ* resolver overturned it whenever a
domain noun co-occurred ("portfolio sedih" -> WEALTH, "basin duka" -> GEOX).

Gate: "redha takdir" -> CARE lane; emotional queries -> human organ (WELL),
not GEOX/WEALTH. Technical intents and explicit organ pins are unaffected.
"""

from __future__ import annotations

import pytest

from core.shared.atlas import Lane, Λ
from arifosmcp.tools.kernel_canonical import _route_intent_to_organ


@pytest.mark.parametrize(
    "query",
    [
        "redha takdir",
        "duka yang tak berkesudahan",
        "hati saya sedih",
        "perasaan bercampur",
        "saya rasa sunyi",
        "bagaimana nak hadapi kehilangan",
        "sedih dengan takdir",
    ],
)
def test_emotional_queries_classify_care(query: str):
    assert Λ(query) == Lane.CARE


@pytest.mark.parametrize(
    "query",
    [
        "redha takdir",
        "duka yang tak berkesudahan",
        "portfolio sedih",
        "basin duka",
    ],
)
def test_emotional_queries_route_to_human_organ(query: str):
    organ = _route_intent_to_organ(query)
    assert organ == "well", f"{query!r} routed to {organ!r}, expected 'well'"


def test_domain_queries_still_route_to_domains():
    assert _route_intent_to_organ("assess portfolio risk").lower() == "wealth"
    assert _route_intent_to_organ("seismic basin porosity").lower() == "geox"


def test_explicit_organ_pin_wins():
    assert _route_intent_to_organ("sedih", "geox") == "geox"
