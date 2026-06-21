"""Regression tests for the VAULT999 bridge surface."""

from __future__ import annotations

import pytest

from arifosmcp.runtime.organ_attestation import _ORGAN_CONFIG
from arifosmcp.runtime.vault_bridge import list_vault_tools


def test_vault999_is_registered_as_an_organ() -> None:
    cfg = _ORGAN_CONFIG.get("VAULT999")
    assert cfg is not None
    assert cfg["role"] == "immutable_ledger"
    assert cfg["health_fn"] == "vault_health_check"
    assert cfg["list_fn"] == "list_vault_tools"
    assert cfg["identity_anchor_type"] == "vault_manifest"


@pytest.mark.asyncio
async def test_vault_bridge_exposes_canonical_rest_tools() -> None:
    tools = await list_vault_tools()
    names = {tool["name"] for tool in tools}

    assert "health" in names
    assert "vault_status" in names
    assert "vault_audit" in names
    assert "vault_receipt" in names
    assert "cli_pending" in names
    assert "cli_inspect" in names
