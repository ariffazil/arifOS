import pytest
import os
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from core.vault999.layer1_epistemic.blockchain_anchor import (
    EpistemicAnchorClient,
    BlockchainAnchor,
    get_anchor_client
)

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("POLYGON_PRIVATE_KEY", "0x" + "a"*64)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_aws_key")
    monkeypatch.setenv("GCP_SERVICE_ACCOUNT_KEY", '{"type": "service_account"}')
    monkeypatch.setenv("B2_APPLICATION_KEY_ID", "b2_id")
    monkeypatch.setenv("B2_APPLICATION_KEY", "b2_key")

@pytest.mark.asyncio
async def test_blockchain_anchor_client_init(mock_env):
    client = EpistemicAnchorClient()
    assert client.polygon_enabled is True
    assert client.opentimestamp_enabled is True
    assert client.cloud_enabled is True
    
    # Test singleton
    c1 = get_anchor_client()
    c2 = get_anchor_client()
    assert c1 is c2

@pytest.mark.asyncio
async def test_anchor_seal(mock_env):
    client = EpistemicAnchorClient()
    
    with patch.object(client, '_anchor_to_polygon', new_callable=AsyncMock) as mock_poly, \
         patch.object(client, '_anchor_to_opentimestamp', new_callable=AsyncMock) as mock_btc, \
         patch.object(client, '_replicate_to_cloud', new_callable=AsyncMock) as mock_cloud:
         
        mock_poly.return_value = "0x_poly_tx"
        mock_btc.return_value = "proof123"
        mock_cloud.return_value = ["s3:us-east-1:hash", "gcs:multi:hash"]
        
        anchor = await client.anchor_seal("hash123", {"metadata": "test"})
        
        assert anchor.seal_hash == "hash123"
        assert anchor.polygon_tx_hash == "0x_poly_tx"
        assert anchor.opentimestamp_proof == "proof123"
        assert len(anchor.cloud_replicas) == 2
        
        mock_poly.assert_awaited_once_with("hash123", {"metadata": "test"})
        mock_btc.assert_awaited_once_with("hash123")
        mock_cloud.assert_awaited_once_with("hash123", {"metadata": "test"})

@pytest.mark.asyncio
async def test_replicate_to_cloud(mock_env):
    client = EpistemicAnchorClient()
    
    with patch.object(client, '_store_s3', new_callable=AsyncMock) as mock_s3, \
         patch.object(client, '_store_gcs', new_callable=AsyncMock) as mock_gcs, \
         patch.object(client, '_store_b2', new_callable=AsyncMock) as mock_b2:
         
        mock_s3.return_value = "s3_hash"
        mock_gcs.return_value = "gcs_hash"
        mock_b2.return_value = "b2_hash"
        
        replicas = await client._replicate_to_cloud("hash123", {})
        
        # 3 regions for S3, 1 for GCS, 1 for B2 = 5 replicas total
        assert len(replicas) == 5
        assert "s3:us-east-1:s3_hash" in replicas
        assert "gcs:multi:gcs_hash" in replicas
        assert "b2:us:b2_hash" in replicas

@pytest.mark.asyncio
async def test_verify_anchor():
    client = EpistemicAnchorClient()
    anchor = BlockchainAnchor(
        seal_hash="hash123",
        timestamp=datetime.utcnow(),
        polygon_tx_hash="0x_tx",
        opentimestamp_proof="proof"
    )
    
    with patch.object(client, '_verify_polygon_tx', new_callable=AsyncMock) as mock_v_poly, \
         patch.object(client, '_verify_opentimestamp', new_callable=AsyncMock) as mock_v_btc:
         
        mock_v_poly.return_value = True
        mock_v_btc.return_value = True
        
        results = await client.verify_anchor(anchor)
        
        assert results["polygon_verified"] is True
        assert results["opentimestamp_verified"] is True

    # Test failure case
    with patch.object(client, '_verify_polygon_tx', new_callable=AsyncMock) as mock_v_poly, \
         patch.object(client, '_verify_opentimestamp', new_callable=AsyncMock) as mock_v_btc:
         
        mock_v_poly.return_value = False
        mock_v_btc.return_value = False
        
        results = await client.verify_anchor(anchor)
        
        assert results["polygon_verified"] is False
        assert results["opentimestamp_verified"] is False

@pytest.mark.asyncio
async def test_anchor_seal_failures(mock_env):
    # Test that failures in one system don't crash the whole process
    client = EpistemicAnchorClient()
    
    with patch.object(client, '_anchor_to_polygon', new_callable=AsyncMock) as mock_poly, \
         patch.object(client, '_anchor_to_opentimestamp', new_callable=AsyncMock) as mock_btc, \
         patch.object(client, '_replicate_to_cloud', new_callable=AsyncMock) as mock_cloud:
         
        mock_poly.side_effect = Exception("Polygon down")
        mock_btc.side_effect = Exception("Bitcoin down")
        mock_cloud.side_effect = Exception("Cloud down")
        
        anchor = await client.anchor_seal("hash123", {"test": "test"})
        
        assert anchor.polygon_tx_hash is None
        assert anchor.opentimestamp_proof is None
        # Could be an empty list or None depending on init, but we initialized it to []
        assert anchor.cloud_replicas == []

