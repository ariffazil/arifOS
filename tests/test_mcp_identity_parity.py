"""Parity test: every MCP surface must report ONE build identity.

WHY (measured 2026-11-01 11:2x MYT, FI-002)
-------------------------------------------
Live kernel :8088, same process, two answers:

    server/discover  -> _meta.serverInfo.version = "kanon-2026.08.09"   (stale literal)
    initialize       -> serverInfo.version       = "kanon-2026.10.31+024ff90"  (true)

canonical_identity().version == "kanon-2026.10.31+024ff90".

`arifosmcp/runtime/mcp_transport_bridge.py` never imports canonical_identity; it
carries three hardcoded literals (lines 625, 665, 679). The spec-2026-07-28
preferred boot door (discover) is therefore the one that lies, while the legacy
door (initialize) tells the truth. Backwards.

RED today, GREEN after the literal -> canonical_identity() wiring.

Install at: /root/arifOS/tests/test_mcp_identity_parity.py
After chattr -i on tests/ (immutable directory).
"""
from __future__ import annotations

from arifosmcp.runtime.deployment_identity import canonical_identity
from arifosmcp.runtime.mcp_transport_bridge import (
    MCPProtocolVersionMiddleware as _M,
)

META = "io.modelcontextprotocol/serverInfo"
STALE = "kanon-2026.08.09"


def _canon() -> str:
    return canonical_identity()["version"]


def test_t1_discover_meta_version_is_canonical() -> None:
    """The preferred 2026-07-28 boot door must report the real build."""
    result = _M._discover_result(1)["result"]
    assert result["_meta"][META]["version"] == _canon()


def test_t2_initialize_result_2026_is_canonical() -> None:
    """The 2026-07-28 stateless initializer must agree.

    Live call site: mcp_transport_bridge.py:522. Not dead code — an earlier note
    claiming that was withdrawn after grep, not after assumption.
    """
    result = _M._initialize_result_2026(1)["result"]
    assert result["serverInfo"]["version"] == _canon()
    assert result["_meta"][META]["version"] == _canon()


def test_t3_no_stale_literal_survives() -> None:
    version = _M._discover_result(1)["result"]["_meta"][META]["version"]
    assert version != STALE, "hardcoded stale build stamp still served"
    assert version.startswith("kanon-"), f"unexpected version shape: {version!r}"


def test_t4_discover_and_initialize_agree() -> None:
    """The parity invariant: two doors, one process, one identity.

    CAVEAT (measured 2026-11-01): this assertion PASSES before the fix, because
    both builders carry the same stale literal. Agreement is not truth — two
    surfaces can agree and both be wrong. t1/t2 are the load-bearing tests; t4
    only catches the case where they drift apart later.
    """
    discover = _M._discover_result(1)["result"]["_meta"][META]["version"]
    initialise = _M._initialize_result_2026(1)["result"]["serverInfo"]["version"]
    assert discover == initialise, (
        f"identity split: discover={discover!r} initialize={initialise!r}"
    )
