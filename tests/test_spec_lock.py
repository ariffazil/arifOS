"""
test_spec_lock.py — Tests for INV-L3-PIN (Lossless Constraint Persistence)
═══════════════════════════════════════════════════════════════════════════════

Verifies:
  1. SPEC.lock.json creation with 4 mandatory fields
  2. Compaction marks requires_spec_reread = True
  3. Reread marks requires_spec_reread = False
  4. Locus check allows matching paths, blocks non-matching
  5. Negative list blocks matching paths
  6. Freeze captures content hash, verify detects mutation
  7. Integrity check validates stored hash

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "/root")

import pytest


@pytest.fixture(autouse=True)
def isolated_spec(tmp_path, monkeypatch):
    """Redirect SPEC.lock to a temp directory for each test."""
    monkeypatch.setenv("ARIFOS_SPEC_LOCK_DIR", str(tmp_path))
    from AAA.state import spec_lock as spec_mod

    spec_mod._SPEC_LOCK_DIR = tmp_path
    yield tmp_path


class TestP1_SpecCreation:
    """SPEC.lock.json creation with mandatory fields."""

    def test_create_spec_has_all_fields(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, read_spec_lock

        spec = create_spec_lock(
            task_id="test-001",
            locus=["src/module_a/*.py", "src/module_b/"],
            signal="Refactor auth to use JWT",
            done=["All tests pass", "No hardcoded secrets"],
            done_v="pytest tests/ -v",
            negative=["src/database/migrations/"],
        )

        assert spec["version"] == 1
        assert spec["task_id"] == "test-001"
        assert "created_at" in spec
        assert "updated_at" in spec
        assert spec["constraints"]["locus"] == ["src/module_a/*.py", "src/module_b/"]
        assert spec["constraints"]["signal"] == "Refactor auth to use JWT"
        assert spec["constraints"]["done"] == ["All tests pass", "No hardcoded secrets"]
        assert spec["constraints"]["done_v"] == "pytest tests/ -v"
        assert spec["constraints"]["negative"] == ["src/database/migrations/"]
        assert spec["hash"] is not None
        assert len(spec["hash"]) == 16

    def test_read_spec_returns_created(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, read_spec_lock

        create_spec_lock(task_id="test-002", signal="test signal")
        read_back = read_spec_lock()

        assert read_back is not None
        assert read_back["task_id"] == "test-002"
        assert read_back["constraints"]["signal"] == "test signal"


class TestP1_CompactionHooks:
    """Compaction marks requires_spec_reread, reread clears it."""

    def test_mark_compaction_sets_reread_flag(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, mark_compaction, requires_reread

        create_spec_lock(task_id="test-003")
        assert requires_reread() is False

        mark_compaction()
        assert requires_reread() is True

        spec = read_spec_lock(isolated_spec)
        assert spec["state"]["compaction_count"] == 1

    def test_mark_reread_clears_flag(self, isolated_spec):
        from AAA.state.spec_lock import (
            create_spec_lock,
            mark_compaction,
            mark_reread,
            requires_reread,
        )

        create_spec_lock(task_id="test-004")
        mark_compaction()
        assert requires_reread() is True

        mark_reread()
        assert requires_reread() is False

        spec = read_spec_lock(isolated_spec)
        assert spec["state"]["last_reread_at"] is not None

    def test_multiple_compactions_increment(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, mark_compaction, mark_reread

        create_spec_lock(task_id="test-005")
        mark_compaction()
        mark_reread()
        mark_compaction()
        mark_reread()
        mark_compaction()

        spec = read_spec_lock(isolated_spec)
        assert spec["state"]["compaction_count"] == 3


class TestP1_LocusCheck:
    """Locus check allows matching, blocks non-matching."""

    def test_locus_allows_matching_path(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, check_locus

        create_spec_lock(
            task_id="test-006",
            locus=["src/auth/*.py", "src/api/"],
        )

        assert check_locus("src/auth/jwt.py") is True
        assert check_locus("src/api/routes.py") is True

    def test_locus_blocks_non_matching_path(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, check_locus

        create_spec_lock(
            task_id="test-007",
            locus=["src/auth/*.py"],
        )

        assert check_locus("src/database/models.py") is False
        assert check_locus("tests/test_auth.py") is False

    def test_empty_locus_allows_all(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, check_locus

        create_spec_lock(task_id="test-008", locus=[])
        assert check_locus("any/file.py") is True

    def test_no_spec_allows_all(self, isolated_spec):
        from AAA.state.spec_lock import check_locus

        assert check_locus("any/file.py") is True


class TestP1_NegativeCheck:
    """Negative list blocks matching paths."""

    def test_negative_blocks_matching(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, check_negative

        create_spec_lock(
            task_id="test-009",
            negative=["src/database/migrations/", "src/config/secrets.py"],
        )

        assert check_negative("src/database/migrations/001_init.py") is True
        assert check_negative("src/config/secrets.py") is True

    def test_negative_allows_non_matching(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, check_negative

        create_spec_lock(
            task_id="test-010",
            negative=["src/database/migrations/"],
        )

        assert check_negative("src/auth/jwt.py") is False


class TestP1_FreezeVerification:
    """Freeze captures hash, verify detects mutation."""

    def test_freeze_and_verify_unchanged(self, isolated_spec, tmp_path):
        from AAA.state.spec_lock import create_spec_lock, freeze_file, verify_frozen

        # Create a test file
        test_file = tmp_path / "test_module.py"
        test_file.write_text("def hello(): return 'world'")

        create_spec_lock(task_id="test-011")
        file_hash = freeze_file(str(test_file))

        assert file_hash is not None
        assert len(file_hash) == 16
        assert verify_frozen(str(test_file)) is True

    def test_freeze_detects_mutation(self, isolated_spec, tmp_path):
        from AAA.state.spec_lock import create_spec_lock, freeze_file, verify_frozen

        test_file = tmp_path / "test_module.py"
        test_file.write_text("def hello(): return 'world'")

        create_spec_lock(task_id="test-012")
        freeze_file(str(test_file))

        # Mutate the file
        test_file.write_text("def hello(): return 'MUTATED'")

        assert verify_frozen(str(test_file)) is False


class TestP1_IntegrityCheck:
    """Stored hash validates constraints integrity."""

    def test_integrity_passes_on_clean_spec(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock, validate_spec_integrity

        create_spec_lock(task_id="test-013", signal="test")
        assert validate_spec_integrity() is True


def read_spec_lock(isolated_spec):
    """Helper to read the spec file directly."""
    path = isolated_spec / "SPEC.lock.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())
