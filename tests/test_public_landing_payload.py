from __future__ import annotations

from arifosmcp.runtime.public_surface import CANONICAL_9
from arifosmcp.runtime.rest_routes.rest_routes import (
    _public_landing_payload,
    _public_mcp_meta_payload,
)


def test_public_landing_payload_uses_canonical_public_registry() -> None:
    payload = _public_landing_payload()

    assert payload["tool_count"] == len(CANONICAL_9) == 9
    assert payload["tools"] == list(CANONICAL_9)


def test_public_mcp_meta_payload_uses_canonical_public_registry() -> None:
    payload = _public_mcp_meta_payload()

    assert payload["tool_count"] == len(CANONICAL_9) == 9
