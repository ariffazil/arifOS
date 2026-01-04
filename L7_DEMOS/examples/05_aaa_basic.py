"""
Basic tests for AAA (L0).
"""

import json
import shutil
import tempfile
from pathlib import Path

from arifos_core.memory.aaa import AAA, AAAConfig


def test_aaa_initializes_if_missing():
    tmpdir = tempfile.mkdtemp()
    try:
        path = Path(tmpdir) / "constitution.json"
        vault = AAA(AAAConfig(vault_path=path))
        floors = vault.get_floors()
        assert "truth_min" in floors
        assert "kappa_r_min" in floors
        assert path.exists()
    finally:
        shutil.rmtree(tmpdir)


def test_aaa_applies_amendment_and_persists():
    tmpdir = tempfile.mkdtemp()
    try:
        path = Path(tmpdir) / "constitution.json"
        vault = AAA(AAAConfig(vault_path=path))

        amendment = {
            "id": "PHOENIX-72-TEST",
            "type": "TEST",
            "applied_at": "2025-11-24T00:00:00Z",
            "details": {"note": "test amendment"},
        }
        vault.apply_amendment(amendment)

        # reload
        vault2 = AAA(AAAConfig(vault_path=path))
        amendments = vault2.list_amendments()
        assert any(a["id"] == "PHOENIX-72-TEST" for a in amendments)
    finally:
        shutil.rmtree(tmpdir)
