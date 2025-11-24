
from pathlib import Path
import tempfile, shutil

from arifos_core.memory.vault999 import Vault999, VaultConfig

def test_vault_initialization_and_amendment_flow():
    tmp = tempfile.mkdtemp()
    try:
        cpath = Path(tmp) / "constitution.json"
        vault = Vault999(VaultConfig(vault_path=cpath))
        assert "floors" in vault.get_constitution()
        amend = {
            "id": "TEST-AMEND",
            "reason": "test scar",
            "applied_at": "now",
            "details": {"note": "unit test"}
        }
        vault.apply_amendment(amend)
        vault2 = Vault999(VaultConfig(vault_path=cpath))
        amendments = vault2.list_amendments()
        assert any(a["id"] == "TEST-AMEND" for a in amendments)
    finally:
        shutil.rmtree(tmp)
