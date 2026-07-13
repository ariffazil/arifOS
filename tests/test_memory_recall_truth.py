import os
import subprocess
import sys

from arifosmcp.tools import memory


def test_constructed_metadata_is_quarantined_and_lowers_confidence():
    record = memory._classify_recall_result(
        {"memory_id": "m1", "summary": "metadata only", "score": 0.9, "tier": "working"}
    )

    assert record["usable"] is False
    assert record["_quarantine"]["reason"] == "synthetic_text_from_metadata"
    confidence = memory._compute_memory_confidence([record])
    assert confidence["content_integrity"] == 0.0
    assert confidence["overall_confidence"] == 0.0


def test_empty_usable_recall_hold_preserves_quarantine_diagnostics(monkeypatch):
    monkeypatch.setattr(
        memory,
        "_memory_search",
        lambda **_: {
            "results": [
                {"memory_id": "m1", "summary": "metadata only", "score": 0.9}
            ]
        },
    )

    result = memory.arif_memory_recall(query="missing evidence")

    assert result["status"] == "HOLD"
    assert result["meta"]["count"] == 0
    assert result["meta"]["memory_quality"]["quarantined_hits"] == 1
    quarantined = result["meta"]["quarantined_results"][0]
    assert quarantined["_quarantine"]["reason"] == "synthetic_text_from_metadata"


def test_vault_registry_import_respects_user_data_home(tmp_path):
    env = os.environ.copy()
    env.pop("ARIFOS_VAULT_DIR", None)
    env["XDG_DATA_HOME"] = str(tmp_path)

    completed = subprocess.run(
        [sys.executable, "-c", "import arifosmcp.runtime.vault_registry"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "arifos" / "vault999").is_dir()
