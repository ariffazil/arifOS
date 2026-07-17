"""R2 — Active SOT v2 operational tests.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from pathlib import Path

from arifosmcp.runtime.sot_active import (
    ACTIVE_SOT_ID,
    get_active_sot,
    resolve_sot_path,
    seal_sot_supersession,
)


def test_sot_v2_artifact_resolves():
    path = resolve_sot_path()
    assert path is not None, "apex-sot-v2.json must exist on af-forge"
    assert path.exists()
    assert path.name == "apex-sot-v2.json"


def test_active_sot_hash_matches_companion():
    sot = get_active_sot()
    assert sot["sot_id"] == ACTIVE_SOT_ID or sot["sot_id"] == "apex-sot-v2"
    assert sot["active"] is True, sot
    assert sot["sot_hash"].startswith("sha256:")
    assert sot["hold_reason"] == ""
    assert sot["operational"] is True

    # Cross-check companion file
    path = Path(sot["path"])
    sha_file = path.parent / "apex-sot-v2.SHA256"
    assert sha_file.exists()
    expected = sha_file.read_text().strip().split()[0].lower()
    actual = sot["sot_hash"].removeprefix("sha256:")
    assert actual == expected


def test_seal_sot_supersession_idempotent():
    first = seal_sot_supersession(actor="unit-test", reason="R2 test")
    assert first["verdict"] == "SEAL"
    assert first["sealed"] is True
    second = seal_sot_supersession(actor="unit-test", reason="R2 test replay")
    assert second["verdict"] == "SEAL"
    assert second["sealed"] is True
    # second call should be idempotent when hash matches
    assert second.get("idempotent") is True or second["receipt"]["sot_hash"] == first["receipt"][
        "sot_hash"
    ]
