"""
Tests for Peer Federation Contract v1 support in arifOS.

Covers:
  - Schema loading and validation
  - Constitutional constraint enforcement
  - Tool-level validate / attest / forbid
  - HTTP discovery endpoint

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.peer_contract import (
    _load_contract_dict,
    arif_peer_contract_attest,
    arif_peer_contract_forbid,
    arif_peer_contract_unforbid,
    arif_peer_contract_validate,
    get_arifos_peer_contract,
    get_arifos_peer_contract_hash,
    get_arifos_peer_contract_url,
    is_peer_forbidden,
)
from arifosmcp.schemas.peer_federation_contract import (
    AuthorityClass,
    PeerFederationContract,
)
from tests.conftest import SyncASGIClient


def test_contract_loads_and_validates():
    contract = get_arifos_peer_contract()
    assert isinstance(contract, PeerFederationContract)
    assert contract.peer_id.organ == "arifOS"
    assert contract.authority_class == AuthorityClass.JUDGE


def test_contract_hash_stable():
    h1 = get_arifos_peer_contract_hash()
    h2 = get_arifos_peer_contract_hash()
    assert h1.startswith("sha256:")
    assert h1 == h2


def test_contract_url_is_https():
    url = get_arifos_peer_contract_url()
    assert url.startswith("https://")
    assert ".well-known/peer-contract.json" in url


@pytest.mark.asyncio
async def test_validate_arifos_contract_passes():
    result = await arif_peer_contract_validate(contract=_load_contract_dict())
    assert result["status"] == "OK"
    assert result["verdict"] == "SEAL"
    assert result["result"]["valid"] is True
    assert result["result"]["organ"] == "arifOS"


@pytest.mark.asyncio
async def test_validate_rejects_non_arifos_judge():
    contract = _load_contract_dict()
    contract["peer_id"]["organ"] = "A-FORGE"
    contract["peer_id"]["did"] = "did:arifos:a-forge-alpha"
    contract["authority_class"] = "judge"
    result = await arif_peer_contract_validate(contract=contract)
    assert result["verdict"] == "HOLD"
    assert result["result"]["valid"] is False
    assert any("judge" in e and "arifOS" in e for e in result["result"]["errors"])


@pytest.mark.asyncio
async def test_validate_rejects_non_judge_without_lease():
    contract = _load_contract_dict()
    contract["authority_class"] = "execute"
    contract["lease_required"] = False
    result = await arif_peer_contract_validate(contract=contract)
    assert result["verdict"] == "HOLD"
    assert result["result"]["valid"] is False
    assert any("lease_required" in e for e in result["result"]["errors"])


@pytest.mark.asyncio
async def test_validate_rejects_empty_forbidden_actions():
    contract = _load_contract_dict()
    contract["forbidden_actions"] = []
    result = await arif_peer_contract_validate(contract=contract)
    assert result["verdict"] in ("HOLD", "DEGRADED")
    assert result["result"]["valid"] is False


@pytest.mark.asyncio
async def test_forbid_then_validate_denies():
    await arif_peer_contract_forbid("WEALTH", reason="test")
    contract = {
        "contract_version": "1.0.0",
        "peer_id": {
            "organ": "WEALTH",
            "instance_id": "00000000-0000-0000-0000-000000000000",
            "did": "did:arifos:wealth-alpha",
            "public_key_fingerprint": "wealth-ed25519-stub",
        },
        "authority_class": "evidence",
        "capability_card": {
            "schema_hash": "peer-federation-contract-v1",
            "tool_manifest_url": "https://wealth.arif-fazil.com/tools/list",
            "allowed_action_classes": ["OBSERVE"],
            "max_risk_tier": "T3",
        },
        "lease_required": True,
        "reversibility_score": 1.0,
        "forbidden_actions": ["judge"],
        "audit_sink": {
            "vault999_endpoint": "https://vault999.arif-fazil.com/seal",
            "receipt_format": "arifos_vault999_v2",
        },
        "human_veto": {"f13_absolute": True, "override_paths": []},
    }
    result = await arif_peer_contract_validate(contract=contract)
    assert result["result"]["forbidden"] is True
    assert is_peer_forbidden("WEALTH")
    # Clean up so other tests are not affected.
    await arif_peer_contract_unforbid("WEALTH")
    assert not is_peer_forbidden("WEALTH")


@pytest.mark.asyncio
async def test_attest_returns_contract_metadata():
    result = await arif_peer_contract_attest()
    assert result["status"] == "OK"
    assert result["verdict"] == "SEAL"
    assert result["result"]["peer_contract_url"] == get_arifos_peer_contract_url()
    assert result["result"]["peer_contract_hash"] == get_arifos_peer_contract_hash()
    assert result["result"]["authority_class"] == "judge"
    assert "contract" in result["result"]


@pytest.mark.asyncio
async def test_peer_contract_id_propagates_to_judge_meta():
    from arifosmcp.runtime.tools import _arif_judge_deliberate_tool

    result = await _arif_judge_deliberate_tool(
        mode="history",
        candidate="peer-contract-propagation-test",
        session_id="test-session",
        actor_id="test-actor",
        peer_contract_id="p2p-v1-aaa-a-forge-arifos",
    )
    assert isinstance(result, dict)
    assert result.get("meta", {}).get("peer_contract_id") == "p2p-v1-aaa-a-forge-arifos"


def test_peer_contract_http_route():
    from arifosmcp.server import app

    client = SyncASGIClient(app)
    resp = client.get("/.well-known/peer-contract.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["peer_id"]["organ"] == "arifOS"
    assert data["contract_version"] == "1.0.0"
    assert data["authority_class"] == "judge"
