# tests/test_seal_proposed_canon_v36.py
"""
Test: Phoenix-72 Seal Protocol (v36Ω)
------------------------------------

This test validates the integrity of the sealing script:

1. A proposed canon file is created.
2. `seal_proposed_canon.py` is invoked programmatically.
3. The resulting sealed entry MUST:
   - Have type "999_SEAL"
   - Contain `previous_hash` matching last ledger entry
   - Have correct `hash` (SHA-256 computed from entry content)
   - Update the Merkle root in L1_merkle_root.txt
4. The proposed file must be archived, ensuring an immutable audit trail.

This test ensures the Cooling Ledger behavior is *predictable*, *verifiable*,
and safe for irreversible constitutional commits.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from arifos_core.governance.ledger_hashing import (
    load_jsonl,
    compute_entry_hash,
    HASH_FIELD,
    PREVIOUS_HASH_FIELD,
    GENESIS_PREVIOUS_HASH,
)
from arifos_core.governance.merkle import build_merkle_tree


# Get the repo root (where scripts/ lives)
REPO_ROOT = Path(__file__).parent.parent


class TestPhoenix72SealProtocol:
    """Tests for the Phoenix-72 Seal Protocol."""

    @pytest.fixture
    def seal_workspace(self, tmp_path: Path):
        """
        Create an isolated workspace with the seal script and required modules.
        """
        # Create directory structure
        (tmp_path / "cooling_ledger" / "proposed" / "archived").mkdir(parents=True)
        (tmp_path / "scripts").mkdir(parents=True)
        (tmp_path / "arifos_core").mkdir(parents=True)

        # Copy the seal script
        seal_script_src = REPO_ROOT / "scripts" / "seal_proposed_canon.py"
        seal_script_dst = tmp_path / "scripts" / "seal_proposed_canon.py"
        shutil.copy(seal_script_src, seal_script_dst)

        # Copy required modules
        for module in ["ledger_hashing.py", "merkle.py", "__init__.py"]:
            src = REPO_ROOT / "arifos_core" / module
            dst = tmp_path / "arifos_core" / module
            if src.exists():
                shutil.copy(src, dst)

        # Create __init__.py if it doesn't exist
        init_file = tmp_path / "arifos_core" / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8")

        return tmp_path

    def test_seal_creates_valid_999_seal_entry(self, seal_workspace: Path):
        """
        Sealing a proposed canon must create a valid 999_SEAL entry.
        """
        # Create a proposed canon
        proposed = {
            "id": "PROPOSED_CANON_TEST001",
            "timestamp": "2025-12-07T00:00:00Z",
            "type": "PROPOSED_CANON",
            "source": "test_harness",
            "from_receipt_id": "ZKPC-TEST-0001",
            "canon": {
                "principle": "Test Canon Principle",
                "law": "This is a test law.",
                "checks": ["check1", "check2"],
                "tags": ["test"],
            },
        }

        proposed_path = seal_workspace / "cooling_ledger" / "proposed" / "PROPOSED_CANON_TEST001.json"
        proposed_path.write_text(json.dumps(proposed, indent=2), encoding="utf-8")

        # Run the seal script
        proc = subprocess.run(
            [
                sys.executable,
                "-m", "scripts.seal_proposed_canon",
                "--file", str(proposed_path),
                "--yes",
            ],
            cwd=str(seal_workspace),
            capture_output=True,
            text=True,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(seal_workspace)},
        )

        assert proc.returncode == 0, f"Seal script failed: {proc.stderr}\n{proc.stdout}"

        # Load and verify ledger
        ledger_path = seal_workspace / "cooling_ledger" / "L1_cooling_ledger.jsonl"
        assert ledger_path.exists(), "Ledger file not created"

        entries = load_jsonl(str(ledger_path))
        assert len(entries) == 1, "Should have exactly one entry"

        entry = entries[0]
        assert entry["type"] == "999_SEAL"
        assert entry["from_receipt_id"] == "ZKPC-TEST-0001"

    def test_seal_maintains_hash_chain_integrity(self, seal_workspace: Path):
        """
        The sealed entry must have correct previous_hash and hash fields.
        """
        proposed = {
            "id": "PROPOSED_CANON_HASH_TEST",
            "timestamp": "2025-12-07T01:00:00Z",
            "type": "PROPOSED_CANON",
            "source": "test_harness",
            "from_receipt_id": "ZKPC-HASH-001",
            "canon": {
                "principle": "Hash Chain Test",
                "law": "Verify hash chain integrity.",
                "checks": [],
                "tags": [],
            },
        }

        proposed_path = seal_workspace / "cooling_ledger" / "proposed" / "PROPOSED_CANON_HASH_TEST.json"
        proposed_path.write_text(json.dumps(proposed, indent=2), encoding="utf-8")

        proc = subprocess.run(
            [
                sys.executable,
                "-m", "scripts.seal_proposed_canon",
                "--file", str(proposed_path),
                "--yes",
            ],
            cwd=str(seal_workspace),
            capture_output=True,
            text=True,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(seal_workspace)},
        )

        assert proc.returncode == 0, f"Seal failed: {proc.stderr}"

        ledger_path = seal_workspace / "cooling_ledger" / "L1_cooling_ledger.jsonl"
        entries = load_jsonl(str(ledger_path))
        entry = entries[0]

        # First entry should have GENESIS as previous_hash
        assert entry[PREVIOUS_HASH_FIELD] == GENESIS_PREVIOUS_HASH

        # Recompute hash and verify
        expected_hash = compute_entry_hash(entry)
        assert entry[HASH_FIELD] == expected_hash, "Hash mismatch - entry integrity compromised"

    def test_seal_updates_merkle_root(self, seal_workspace: Path):
        """
        Sealing must update the Merkle root correctly.
        """
        proposed = {
            "id": "PROPOSED_CANON_MERKLE_TEST",
            "timestamp": "2025-12-07T02:00:00Z",
            "type": "PROPOSED_CANON",
            "source": "test_harness",
            "from_receipt_id": "ZKPC-MERKLE-001",
            "canon": {
                "principle": "Merkle Root Test",
                "law": "Verify Merkle root update.",
                "checks": [],
                "tags": [],
            },
        }

        proposed_path = seal_workspace / "cooling_ledger" / "proposed" / "PROPOSED_CANON_MERKLE_TEST.json"
        proposed_path.write_text(json.dumps(proposed, indent=2), encoding="utf-8")

        proc = subprocess.run(
            [
                sys.executable,
                "-m", "scripts.seal_proposed_canon",
                "--file", str(proposed_path),
                "--yes",
            ],
            cwd=str(seal_workspace),
            capture_output=True,
            text=True,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(seal_workspace)},
        )

        assert proc.returncode == 0, f"Seal failed: {proc.stderr}"

        # Check Merkle root file exists
        merkle_path = seal_workspace / "cooling_ledger" / "L1_merkle_root.txt"
        assert merkle_path.exists(), "Merkle root file not created"

        merkle_root = merkle_path.read_text().strip()

        # For single entry, Merkle root = entry hash
        ledger_path = seal_workspace / "cooling_ledger" / "L1_cooling_ledger.jsonl"
        entries = load_jsonl(str(ledger_path))
        expected_root = entries[0][HASH_FIELD]

        assert merkle_root == expected_root, "Merkle root incorrect for single-entry ledger"

    def test_seal_archives_proposed_file(self, seal_workspace: Path):
        """
        After sealing, the proposed file must be moved to archived/.
        """
        proposed = {
            "id": "PROPOSED_CANON_ARCHIVE_TEST",
            "timestamp": "2025-12-07T03:00:00Z",
            "type": "PROPOSED_CANON",
            "source": "test_harness",
            "from_receipt_id": "ZKPC-ARCHIVE-001",
            "canon": {
                "principle": "Archive Test",
                "law": "Verify proposed file archiving.",
                "checks": [],
                "tags": [],
            },
        }

        proposed_path = seal_workspace / "cooling_ledger" / "proposed" / "PROPOSED_CANON_ARCHIVE_TEST.json"
        proposed_path.write_text(json.dumps(proposed, indent=2), encoding="utf-8")

        proc = subprocess.run(
            [
                sys.executable,
                "-m", "scripts.seal_proposed_canon",
                "--file", str(proposed_path),
                "--yes",
            ],
            cwd=str(seal_workspace),
            capture_output=True,
            text=True,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(seal_workspace)},
        )

        assert proc.returncode == 0, f"Seal failed: {proc.stderr}"

        # Original proposed file should be gone
        assert not proposed_path.exists(), "Proposed file should be moved, not copied"

        # Archived file should exist
        archived_path = seal_workspace / "cooling_ledger" / "proposed" / "archived" / "PROPOSED_CANON_ARCHIVE_TEST.json"
        assert archived_path.exists(), "Proposed file must be archived after sealing"

    def test_seal_multiple_entries_maintains_chain(self, seal_workspace: Path):
        """
        Sealing multiple entries must maintain a valid hash chain.
        """
        # Create and seal first entry
        proposed1 = {
            "id": "PROPOSED_CANON_CHAIN_001",
            "timestamp": "2025-12-07T04:00:00Z",
            "type": "PROPOSED_CANON",
            "source": "test_harness",
            "from_receipt_id": "ZKPC-CHAIN-001",
            "canon": {"principle": "First", "law": "First law", "checks": [], "tags": []},
        }
        path1 = seal_workspace / "cooling_ledger" / "proposed" / "PROPOSED_CANON_CHAIN_001.json"
        path1.write_text(json.dumps(proposed1, indent=2), encoding="utf-8")

        subprocess.run(
            [sys.executable, "-m", "scripts.seal_proposed_canon", "--file", str(path1), "--yes"],
            cwd=str(seal_workspace),
            capture_output=True,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(seal_workspace)},
        )

        # Create and seal second entry
        proposed2 = {
            "id": "PROPOSED_CANON_CHAIN_002",
            "timestamp": "2025-12-07T05:00:00Z",
            "type": "PROPOSED_CANON",
            "source": "test_harness",
            "from_receipt_id": "ZKPC-CHAIN-002",
            "canon": {"principle": "Second", "law": "Second law", "checks": [], "tags": []},
        }
        path2 = seal_workspace / "cooling_ledger" / "proposed" / "PROPOSED_CANON_CHAIN_002.json"
        path2.write_text(json.dumps(proposed2, indent=2), encoding="utf-8")

        proc = subprocess.run(
            [sys.executable, "-m", "scripts.seal_proposed_canon", "--file", str(path2), "--yes"],
            cwd=str(seal_workspace),
            capture_output=True,
            text=True,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(seal_workspace)},
        )

        assert proc.returncode == 0, f"Second seal failed: {proc.stderr}"

        # Verify chain
        ledger_path = seal_workspace / "cooling_ledger" / "L1_cooling_ledger.jsonl"
        entries = load_jsonl(str(ledger_path))

        assert len(entries) == 2, "Should have two entries"

        # First entry: previous_hash = GENESIS
        assert entries[0][PREVIOUS_HASH_FIELD] == GENESIS_PREVIOUS_HASH

        # Second entry: previous_hash = first entry's hash
        assert entries[1][PREVIOUS_HASH_FIELD] == entries[0][HASH_FIELD]

        # Verify Merkle root for two entries
        merkle_path = seal_workspace / "cooling_ledger" / "L1_merkle_root.txt"
        actual_root = merkle_path.read_text().strip()

        leaf_hashes = [e[HASH_FIELD] for e in entries]
        tree = build_merkle_tree(leaf_hashes)
        expected_root = tree.root

        assert actual_root == expected_root, "Merkle root incorrect for two-entry ledger"
