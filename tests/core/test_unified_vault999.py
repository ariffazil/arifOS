"""
Tests for SovereignVault999 (unified_vault999.py).
Exercises the integration layer across all 4 vault security layers.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# We need to mock the organs._4_vault before importing unified_vault999
import sys

# Create lightweight mocks for heavy dependencies
mock_arch_result = MagicMock()
mock_arch_result.seal_record.hash = "abc123def456" + "0" * 52
mock_arch_result.hash_chain.entry_hash = "merkle_root_hash" + "0" * 48

# Mock the architectural seal function
mock_seal_fn = AsyncMock(return_value=mock_arch_result)

# Patch core organs before importing unified module
with patch.dict(sys.modules, {"core.organs._4_vault": MagicMock(seal=mock_seal_fn)}):
    from core.vault999.unified_vault999 import (
        SovereignVault999,
        PhenomenologicalVaultRecord,
        get_sovereign_vault,
    )


@pytest.fixture
def vault(tmp_path, monkeypatch):
    """Create a SovereignVault999 with mocked architectural seal."""
    monkeypatch.setenv("ARIFOS_VAULT_DIR", str(tmp_path))

    with patch("core.vault999.unified_vault999.architectural_seal", new=mock_seal_fn):
        v = SovereignVault999(vault_path=tmp_path / "vault")
    return v


@pytest.mark.asyncio
async def test_seal_with_phenomenology_basic(vault):
    """Test the main sealing path without execution envelope."""
    with (
        patch.object(vault.anchor_client, "anchor_seal", new_callable=AsyncMock) as mock_anchor,
        patch("core.vault999.unified_vault999.architectural_seal", new=mock_seal_fn),
    ):
        mock_anchor.return_value = MagicMock()

        record = await vault.seal_with_phenomenology(
            session_id="sess-001",
            summary="Test session summary",
            verdict="SEAL",
            floor_scores={"F1": 0.9, "F7": 0.85},
            rasa_scores={"receive": 0.8},
        )

    assert isinstance(record, PhenomenologicalVaultRecord)
    assert record.session_id == "sess-001"
    assert record.verdict == "SEAL"
    assert record.seal_hash
    assert record.merkle_root
    assert record.qualia_trace is not None
    assert record.autonoetic_marker is not None
    assert record.execution_envelope is None  # Not requested


@pytest.mark.asyncio
async def test_seal_with_execution_envelope(vault):
    """Test sealing with requires_execution=True generates an envelope."""
    with (
        patch.object(vault.anchor_client, "anchor_seal", new_callable=AsyncMock) as mock_anchor,
        patch.object(vault.attestor, "sign_envelope", new_callable=AsyncMock) as mock_sign,
        patch("core.vault999.unified_vault999.architectural_seal", new=mock_seal_fn),
    ):
        mock_anchor.return_value = MagicMock()
        mock_sign.side_effect = lambda e: e  # return envelope unchanged

        record = await vault.seal_with_phenomenology(
            session_id="sess-002",
            summary="Execution required",
            verdict="SEAL",
            requires_execution=True,
        )

    assert record.execution_envelope is not None
    mock_sign.assert_awaited_once()


@pytest.mark.asyncio
async def test_seal_anchor_failure_doesnt_crash(vault):
    """Blockchain anchoring failure must be non-fatal."""
    with (
        patch.object(vault.anchor_client, "anchor_seal", new_callable=AsyncMock) as mock_anchor,
        patch("core.vault999.unified_vault999.architectural_seal", new=mock_seal_fn),
    ):
        mock_anchor.side_effect = Exception("Polygon down")

        record = await vault.seal_with_phenomenology(
            session_id="sess-003",
            summary="Anchor should fail gracefully",
            verdict="HOLD",
        )

    assert record is not None
    assert record.blockchain_anchor is None  # Gracefully None on failure


@pytest.mark.asyncio
async def test_verify_integrity(vault):
    """verify_integrity should return a structured report."""
    with patch.object(
        vault.autonoetic_system, "assess_identity_continuity", return_value={"score": 0.95}
    ):
        report = await vault.verify_integrity()

    assert "layers" in report
    assert "phenomenological" in report
    assert report["layers"]["epistemic"] == "verified"
    assert "identity_continuity" in report["phenomenological"]


@pytest.mark.asyncio
async def test_verify_integrity_with_mirrors(vault, tmp_path):
    """verify_integrity includes mirror check when mirror_sync is set."""
    from core.vault999.layer4_survivability.cold_storage import MirrorSynchronizer

    mirrors = [{"region": "us-east"}, {"region": "eu-west"}]
    vault.mirror_sync = MirrorSynchronizer(mirrors)

    with (
        patch.object(
            vault.mirror_sync, "verify_mirror_integrity", new_callable=AsyncMock
        ) as mock_mir,
        patch.object(
            vault.autonoetic_system, "assess_identity_continuity", return_value={"score": 0.9}
        ),
    ):
        mock_mir.return_value = {"us-east": True, "eu-west": True}
        report = await vault.verify_integrity()

    assert "mirrors" in report["layers"]
    assert report["layers"]["mirrors"]["us-east"] is True


@pytest.mark.asyncio
async def test_emergency_backup(vault):
    """emergency_backup should call cold storage."""
    with patch.object(
        vault.cold_storage, "create_encrypted_backup", new_callable=AsyncMock
    ) as mock_bak:
        mock_bak_result = MagicMock()
        mock_bak_result.integrity_proof = "proof_hash_123"
        mock_bak_result.timestamp = datetime.utcnow()
        mock_bak.return_value = mock_bak_result

        result = await vault.emergency_backup()

    assert result["status"] == "BACKUP_COMPLETE"
    assert "backup_hash" in result
    mock_bak.assert_awaited_once()


def test_get_life_narrative(vault):
    narrative = vault.get_life_narrative()
    assert isinstance(narrative, list)


def test_get_vivid_memories(vault):
    memories = vault.get_vivid_memories()
    assert isinstance(memories, list)


def test_phenomenological_record_to_dict(vault):
    """PhenomenologicalVaultRecord.to_dict should serialize all layers."""
    from core.vault999.phenomenological.qualia_trace import QualiaTrace
    from core.vault999.phenomenological.autonoetic import NarrativeContinuity

    qualia = QualiaTrace.from_session_context(
        session_id="sess-test",
        verdict="SEAL",
        floor_scores={"F1": 0.9},
        rasa_scores={},
    )
    autonoetic = vault.autonoetic_system.create_autonoetic_memory(
        session_id="sess-test",
        timestamp=datetime.utcnow(),
        phenomenological_intensity=0.8,
    )
    narrative = NarrativeContinuity(
        chapter_title="Test Chapter",
        narrative_role="formative",
    )

    record = PhenomenologicalVaultRecord(
        seal_hash="abc123",
        merkle_root="root123",
        timestamp=datetime.utcnow(),
        session_id="sess-test",
        verdict="SEAL",
        qualia_trace=qualia,
        autonoetic_marker=autonoetic,
        narrative_thread=narrative,
    )

    d = record.to_dict()
    assert "architectural" in d
    assert "experiential" in d
    assert d["architectural"]["verdict"] == "SEAL"
    assert "qualia" in d["experiential"]


def test_get_sovereign_vault_singleton(tmp_path, monkeypatch):
    """get_sovereign_vault returns same singleton each call."""
    import core.vault999.unified_vault999 as uv

    # Reset singleton
    uv._vault999_instance = None

    monkeypatch.setenv("ARIFOS_VAULT_DIR", str(tmp_path))
    v1 = get_sovereign_vault()
    v2 = get_sovereign_vault()
    assert v1 is v2
    # Reset for other tests
    uv._vault999_instance = None
