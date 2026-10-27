"""Phase 1 · Lane 3 + Lane 4 — honest labels and a declared judge affordance.

Lane 3: apex_scalars attached by arif_judge must carry the same
        "federation baseline, not this session's score" provenance that
        arif_init already attaches.
Lane 4: the judge must resolve to its declared constitutional affordance even
        when the caller uses the transport-prefixed MCP name.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.tools import get_full_affordance
from arifosmcp.tools.judge import _tag_apex_scope


def test_apex_scalars_carry_federation_scope():
    tagged = _tag_apex_scope({"G": 0.5799, "h": 0.8428})

    assert tagged["scope"] == "federation"
    assert "not this session" in tagged["note"].lower()
    # Values must not be rewritten — only labelled.
    assert tagged["G"] == 0.5799 and tagged["h"] == 0.8428


def test_apex_scope_label_is_idempotent():
    once = _tag_apex_scope({"G": 0.5})
    twice = _tag_apex_scope(once)
    assert twice["note"] == once["note"] and twice["scope"] == "federation"


@pytest.mark.parametrize("name", ["arif_judge", "arifos_arif_judge", "arifos.arif_judge"])
def test_judge_affordance_is_known_on_every_transport_name(name: str):
    affordance = get_full_affordance(name)

    assert affordance.get("known") is True, f"{name} resolved to the _default contract"
    assert "not yet declared" not in str(affordance.get("purpose", "")).lower()
    assert affordance.get("output_is_approval") is False
