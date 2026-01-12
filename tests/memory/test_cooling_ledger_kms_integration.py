import json
from pathlib import Path
from typing import Dict, Any

import pytest

# Adjust these imports to match your repository layout.
# If your cooling ledger lives at arifos_core.memory.cooling_ledger use that path.
from arifos_core.memory.cooling_ledger import append_entry, verify_chain
from arifos_core.utils.kms_signer import KmsSigner, KmsSignerConfig

try:
    # Preferred when tests is importable as a top-level module
    from tests.test_kms_signer import FakeKmsClient  # type: ignore
except ModuleNotFoundError:
    # Fallback when running as a flat test file
    from test_kms_signer import FakeKmsClient  # type: ignore


def test_ledger_appends_kms_signature_when_signer_present(tmp_path: Path) -> None:
    """
    End-to-end pipeline test (staging-style) that exercises:
      - append_entry computes hash
      - append_entry uses the provided KmsSigner to sign the digest
      - stored ledger line contains hash, kms_key_id, and kms_signature
      - verify_chain still validates the chain (does not require verifying KMS signature)
    """

    ledger_path = tmp_path / "ledger.jsonl"

    fake_client = FakeKmsClient()
    signer = KmsSigner(config=KmsSignerConfig(key_id="kms-key-abc"), client=fake_client)

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "signed_entry",
        "payload": {"idx": 1},
    }

    # The append_entry function in your repo must accept kms_signer optional arg.
    append_entry(ledger_path, entry, kms_signer=signer)

    # Read back the single stored line
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    stored = json.loads(lines[0])

    # Basic fields required by the harness design
    assert "hash" in stored
    assert stored.get("kms_key_id") == signer.config.key_id
    assert "kms_signature" in stored
    assert isinstance(stored["kms_signature"], str)

    # verify_chain should still validate structural integrity and prev_hash linkage
    ok, details = verify_chain(ledger_path)
    assert ok, f"Ledger verification failed: {details}"


@pytest.mark.parametrize("tamper_field", ["payload", "event"])
def test_ledger_tampering_after_sign_should_fail(tmp_path: Path, tamper_field: str) -> None:
    """
    Build a small signed chain then tamper with an earlier entry.
    verify_chain should detect hash mismatch.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    fake_client = FakeKmsClient()
    signer = KmsSigner(config=KmsSignerConfig(key_id="kms-key-abc"), client=fake_client)

    # Create two signed entries
    append_entry(ledger_path, {"timestamp": "2025-11-24T00:00:00Z", "event": "a", "payload": {"i": 1}}, kms_signer=signer)
    append_entry(ledger_path, {"timestamp": "2025-11-24T00:00:01Z", "event": "b", "payload": {"i": 2}}, kms_signer=signer)

    # Tamper first line
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    # Modify the tamper_field
    if tamper_field == "payload":
        first["payload"]["i"] = 9999
    else:
        first["event"] = "tampered"
    lines[0] = json.dumps(first, sort_keys=True, separators=(",", ":"))
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, details = verify_chain(ledger_path)
    assert not ok, "Tampered ledger should fail verification"
    assert "hash" in details.lower() or "mismatch" in details.lower()
