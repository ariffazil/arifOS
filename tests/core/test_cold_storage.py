import pytest
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from core.vault999.layer4_survivability.cold_storage import (
    ColdStorageManager,
    MirrorSynchronizer,
    HAS_SSS,
)


@pytest.fixture
def manager(tmp_path):
    vault_path = tmp_path / "vault999"
    vault_path.mkdir()
    (vault_path / "SEALED_EVENTS.jsonl").write_text("data")
    backup_dir = tmp_path / "backups"
    return ColdStorageManager(vault_path=vault_path, backup_dir=backup_dir)


@pytest.mark.asyncio
async def test_create_encrypted_backup(manager, monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "test")
    monkeypatch.setenv("B2_APPLICATION_KEY_ID", "test")

    with (
        patch("subprocess.run") as mock_run,
        patch("builtins.open", new_callable=MagicMock) as mock_open,
        patch("hashlib.sha256") as mock_sha256,
        patch.object(Path, "unlink") as mock_unlink,
    ):
        # The code reads pre_encrypt_hash and integrity_proof from the open(f.read())
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = b"data"

        mock_hash = MagicMock()
        mock_hash.hexdigest.return_value = "hash123"
        mock_sha256.return_value = mock_hash

        backup = await manager.create_encrypted_backup()

        assert backup.vault_hash == "hash123"[:32]
        assert backup.integrity_proof == "hash123"
        assert "ariffazil@github.com" in backup.gpg_recipients
        assert mock_run.call_count >= 5  # 1 for tar, 1 for gpg, 3 for cloud
        mock_unlink.assert_called()


def test_split_and_reconstruct_signing_key(manager):
    if not HAS_SSS:
        pytest.skip("secretsharing library not installed")

    secret = "my_super_secret_key"
    shares = manager.split_signing_key(secret)

    assert len(shares) == 5
    assert shares[0].location == "bank_vault_primary"

    reconstructed = manager.reconstruct_signing_key(shares[:3])
    assert reconstructed == secret

    with pytest.raises(ValueError):
        manager.reconstruct_signing_key(shares[:2])


@pytest.mark.asyncio
async def test_restore_from_backup(manager, tmp_path):
    backup_path = tmp_path / "backup.tar.gz.gpg"
    restore_dir = tmp_path / "restore"
    restore_dir.mkdir()

    with (
        patch("subprocess.run") as mock_run,
        patch(
            "core.vault999.layer4_survivability.cold_storage.open",
            MagicMock(
                return_value=MagicMock(
                    __enter__=MagicMock(
                        return_value=MagicMock(read=MagicMock(return_value=b"data"))
                    ),
                    __exit__=MagicMock(return_value=False),
                )
            ),
        ),
    ):
        mock_run.return_value = None
        success = await manager.restore_from_backup(backup_path, restore_dir)
        assert success is True
        assert mock_run.call_count == 2  # gpg decrypt and tar extract


@pytest.mark.asyncio
async def test_restore_from_backup_failure(manager, tmp_path):
    backup_path = tmp_path / "backup.tar.gz.gpg"
    restore_dir = tmp_path / "restore"
    restore_dir.mkdir()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        success = await manager.restore_from_backup(backup_path, restore_dir)
        assert success is False


@pytest.mark.asyncio
async def test_mirror_synchronizer():
    mirrors = [{"region": "us-east"}, {"region": "eu-west"}]
    sync = MirrorSynchronizer(mirrors)

    with patch.object(sync, "_push_to_mirror", new_callable=AsyncMock) as mock_push:
        mock_push.side_effect = [None, Exception("Failed")]
        await sync.sync_to_mirrors({"data": 1})
        assert mock_push.call_count == 2

    # verify_mirror_integrity relies on _check_mirror which is not yet implemented
    # (returns pass-through). Test graceful error handling instead.
    async def always_fail(mirror):
        raise Exception("unreachable")

    sync2 = MirrorSynchronizer([{"region": "us-east"}, {"region": "eu-west"}])
    # Inject a real async _check_mirror that works
    call_count = [0]

    async def mock_check(mirror):
        call_count[0] += 1
        if mirror["region"] == "us-east":
            return True
        raise Exception("eu-west unreachable")

    sync2._check_mirror = mock_check

    results = await sync2.verify_mirror_integrity()
    assert results["us-east"] is True
    assert results["eu-west"] is False
