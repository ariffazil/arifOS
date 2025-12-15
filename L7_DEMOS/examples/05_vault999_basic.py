"""
Basic tests for Vault999 (L0).
"""

from pathlib import Path
import json
import shutil
import tempfile

from arifos_core.memory.vault999 import Vault999, VaultConfig


def test_vault_initializes_if_missing():
    tmpdir = tempfile.mkdtemp()
    try:
        path = Path(tmpdir) / "constitution.json"
        vault = Vault999(VaultConfig(vault_path=path))
        floors = vault.get_floors()
        assert "truth_min" in floors
        assert "kappa_r_min" in floors
        assert path.exists()
    finally:
        shutil.rmtree(tmpdir)


def test_vault_applies_amendment_and_persists():
    tmpdir = tempfile.mkdtemp()
    try:
        path = Path(tmpdir) / "constitution.json"
        vault = Vault999(VaultConfig(vault_path=path))

        amendment = {
            "id": "PHOENIX-72-TEST",
            "type": "TEST",
            "applied_at": "2025-11-24T00:00:00Z",
            "details": {"note": "test amendment"},
        }
        vault.apply_amendment(amendment)

        # reload
        vault2 = Vault999(VaultConfig(vault_path=path))
        amendments = vault2.list_amendments()
        assert any(a["id"] == "PHOENIX-72-TEST" for a in amendments)
    finally:
        shutil.rmtree(tmpdir)