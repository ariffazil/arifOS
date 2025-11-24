# tests/test_cooling_ledger_integrity_mocked.py
#
# Mocked version of cooling ledger integrity tests.
# Uses mocked KMS signing and demonstrates testing without real crypto infrastructure.

import json
import hashlib
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch, MagicMock

import pytest

from arifos_core.memory.cooling_ledger import append_entry, verify_chain


# --- Mock KMS signing ---------------------------------------------------------

class MockKMS:
    """
    Mock Key Management Service for testing.

    Simulates signing operations without requiring real KMS infrastructure.
    """

    def __init__(self, key_id: str = "mock-key-123"):
        self.key_id = key_id
        self.sign_count = 0

    def sign(self, data: bytes) -> bytes:
        """Mock signing operation using deterministic hash."""
        self.sign_count += 1
        # Use SHA256 as mock signature (not cryptographically secure for production!)
        return hashlib.sha256(data + self.key_id.encode()).digest()

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Mock signature verification."""
        expected = self.sign(data)
        return signature == expected


@pytest.fixture
def mock_kms():
    """Fixture providing a mock KMS instance."""
    return MockKMS()


# --- Tests with mocked KMS ----------------------------------------------------

def test_ledger_with_mocked_kms_signing(tmp_path: Path, mock_kms: MockKMS) -> None:
    """
    Test ledger operations with mocked KMS signing.

    This demonstrates how to test signed entries without real KMS.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "signed_entry",
        "payload": {"data": "test"},
    }

    # Add mock signature
    entry_data = json.dumps(entry, sort_keys=True).encode()
    entry["signature"] = mock_kms.sign(entry_data).hex()
    entry["key_id"] = mock_kms.key_id

    append_entry(ledger_path, entry)

    # Verify chain integrity
    ok, details = verify_chain(ledger_path)
    assert ok

    # Verify signature
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])

    # Extract original entry for verification
    verify_entry = {k: v for k, v in stored.items() if k not in ("hash", "prev_hash", "signature", "key_id")}
    verify_data = json.dumps(verify_entry, sort_keys=True).encode()
    signature = bytes.fromhex(stored["signature"])

    assert mock_kms.verify(verify_data, signature)


def test_ledger_detects_invalid_signature(tmp_path: Path, mock_kms: MockKMS) -> None:
    """
    Test that ledger detects tampered signatures.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "signed_entry",
        "payload": {"data": "test"},
    }

    # Add mock signature
    entry_data = json.dumps(entry, sort_keys=True).encode()
    entry["signature"] = mock_kms.sign(entry_data).hex()
    entry["key_id"] = mock_kms.key_id

    append_entry(ledger_path, entry)

    # Tamper with signature
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])
    stored["signature"] = "deadbeef" * 16  # invalid signature
    lines[0] = json.dumps(stored, sort_keys=True, separators=(",", ":"))
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Read back and verify signature fails
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])

    verify_entry = {k: v for k, v in stored.items() if k not in ("hash", "prev_hash", "signature", "key_id")}
    verify_data = json.dumps(verify_entry, sort_keys=True).encode()
    signature = bytes.fromhex(stored["signature"])

    assert not mock_kms.verify(verify_data, signature)


# --- Mock Tri-Witness adapter -------------------------------------------------

class MockTriWitnessAdapter:
    """
    Mock Tri-Witness adapter for testing.

    Simulates multi-perspective verification without real witness infrastructure.
    """

    def __init__(self, witness_count: int = 3):
        self.witness_count = witness_count
        self.verification_history = []

    def verify_entry(self, entry: Dict[str, Any]) -> Dict[str, float]:
        """
        Mock verification returning scores from multiple witnesses.

        Returns:
            Dict mapping witness_id to verification score [0,1]
        """
        self.verification_history.append(entry)

        # Mock witness scores (deterministic based on entry content)
        entry_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).digest()
        scores = {}

        for i in range(self.witness_count):
            # Generate deterministic score from hash
            witness_byte = entry_hash[i % len(entry_hash)]
            score = witness_byte / 255.0
            scores[f"witness_{i}"] = score

        return scores

    def aggregate_score(self, scores: Dict[str, float]) -> float:
        """Aggregate witness scores (using minimum for conservative approach)."""
        if not scores:
            return 0.0
        return min(scores.values())


@pytest.fixture
def mock_tri_witness():
    """Fixture providing a mock Tri-Witness adapter."""
    return MockTriWitnessAdapter()


# --- Tests with mocked Tri-Witness --------------------------------------------

def test_ledger_with_mocked_tri_witness(tmp_path: Path, mock_tri_witness: MockTriWitnessAdapter) -> None:
    """
    Test ledger verification with mocked Tri-Witness adapter.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "witnessed_entry",
        "payload": {"data": "test"},
    }

    append_entry(ledger_path, entry)

    # Verify chain
    ok, details = verify_chain(ledger_path)
    assert ok

    # Get witness verification
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])

    scores = mock_tri_witness.verify_entry(stored)
    aggregate = mock_tri_witness.aggregate_score(scores)

    assert len(scores) == 3  # three witnesses
    assert 0.0 <= aggregate <= 1.0
    assert len(mock_tri_witness.verification_history) == 1


def test_ledger_tri_witness_detects_tampering(tmp_path: Path, mock_tri_witness: MockTriWitnessAdapter) -> None:
    """
    Test that Tri-Witness verification detects tampered entries.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "test",
        "payload": {"data": "original"},
    }

    append_entry(ledger_path, entry)

    # Get witness scores for original
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    original = json.loads(lines[0])
    original_scores = mock_tri_witness.verify_entry(original)

    # Tamper with entry
    tampered = json.loads(lines[0])
    tampered["payload"]["data"] = "modified"

    # Get witness scores for tampered version
    tampered_scores = mock_tri_witness.verify_entry(tampered)

    # Scores should differ (deterministic based on content)
    assert original_scores != tampered_scores


# --- Combined mocks -----------------------------------------------------------

def test_ledger_with_both_kms_and_tri_witness(
    tmp_path: Path,
    mock_kms: MockKMS,
    mock_tri_witness: MockTriWitnessAdapter
) -> None:
    """
    Test ledger with both KMS signing and Tri-Witness verification.

    Demonstrates complete mocked security infrastructure.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "fully_secured_entry",
        "payload": {"data": "test", "stakes": "high"},
    }

    # Add KMS signature
    entry_data = json.dumps(entry, sort_keys=True).encode()
    entry["signature"] = mock_kms.sign(entry_data).hex()
    entry["key_id"] = mock_kms.key_id

    append_entry(ledger_path, entry)

    # Verify chain integrity
    ok, details = verify_chain(ledger_path)
    assert ok, f"Chain verification failed: {details}"

    # Verify KMS signature
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])

    verify_entry = {k: v for k, v in stored.items() if k not in ("hash", "prev_hash", "signature", "key_id")}
    verify_data = json.dumps(verify_entry, sort_keys=True).encode()
    signature = bytes.fromhex(stored["signature"])
    assert mock_kms.verify(verify_data, signature), "KMS signature verification failed"

    # Verify Tri-Witness scores
    scores = mock_tri_witness.verify_entry(stored)
    aggregate = mock_tri_witness.aggregate_score(scores)

    assert len(scores) == 3
    assert 0.0 <= aggregate <= 1.0

    # Both security layers passed
    assert ok and mock_kms.verify(verify_data, signature)


# --- Patching real modules ----------------------------------------------------

@patch('arifos_core.memory.cooling_ledger.append_entry')
def test_with_patched_append(mock_append, tmp_path: Path) -> None:
    """
    Example of using unittest.mock.patch to mock the append_entry function.

    Useful when testing higher-level code that uses cooling_ledger.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "test",
        "payload": {},
    }

    # Configure mock
    mock_append.return_value = None

    # Call the mocked function
    from arifos_core.memory.cooling_ledger import append_entry as imported_append
    imported_append(ledger_path, entry)

    # Verify mock was called
    mock_append.assert_called_once_with(ledger_path, entry)


@pytest.mark.parametrize("witness_count", [1, 3, 5, 7])
def test_tri_witness_with_varying_counts(tmp_path: Path, witness_count: int) -> None:
    """
    Test Tri-Witness adapter with different witness counts.

    Demonstrates parametrized testing with mocks.
    """
    mock_adapter = MockTriWitnessAdapter(witness_count=witness_count)
    ledger_path = tmp_path / f"ledger_{witness_count}.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "test",
        "payload": {"witness_count": witness_count},
    }

    append_entry(ledger_path, entry)

    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])

    scores = mock_adapter.verify_entry(stored)

    assert len(scores) == witness_count
    assert all(0.0 <= score <= 1.0 for score in scores.values())


# --- Performance testing with mocks -------------------------------------------

def test_ledger_performance_with_mocked_crypto(tmp_path: Path, mock_kms: MockKMS) -> None:
    """
    Test ledger performance with mocked crypto operations.

    Mocking allows testing without real crypto overhead.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    import time
    start = time.time()

    # Add many entries with mock signatures
    for i in range(100):
        entry: Dict[str, Any] = {
            "timestamp": f"2025-11-24T00:00:{i:02d}Z",
            "event": f"entry_{i}",
            "payload": {"idx": i},
        }

        # Add mock signature
        entry_data = json.dumps(entry, sort_keys=True).encode()
        entry["signature"] = mock_kms.sign(entry_data).hex()
        entry["key_id"] = mock_kms.key_id

        append_entry(ledger_path, entry)

    elapsed = time.time() - start

    # Verify chain
    ok, details = verify_chain(ledger_path)
    assert ok
    assert "100 entries" in details

    # Mock operations should be fast
    assert elapsed < 5.0, f"Operations took too long: {elapsed:.2f}s"
    assert mock_kms.sign_count == 100
