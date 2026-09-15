"""
FHS canon-plane tests — arifosmcp.canon resolution and /health attestation.

Covers the 2026-09-16 FHS formalization:
  - dev mode (no ARIFOS_CANON_DIR) → repo fallback, unchanged behavior
  - prod mode (canon dir set) → canon file wins when present
  - canon file absent from /etc → repo fallback (no silent breakage)
  - manifest verification: per-file sha256 → integrity ok / MISMATCH
  - /health attestation carries the canon block (report-only)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from arifosmcp.canon import (
    CANON_DIR_ENV,
    canon_attestation,
    canon_aware_path,
    canon_dir,
    canon_manifest,
)


@pytest.fixture()
def canon_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A valid /etc/arifos/canon stand-in with one canon file + manifest."""
    policy = tmp_path / "memory-admissibility-policy.yaml"
    policy.write_text("modes: {}\nstatus_vocabulary: []\n", encoding="utf-8")
    digest = hashlib.sha256(policy.read_bytes()).hexdigest()
    manifest = {
        "canon_version": "2026.09.16-r1",
        "ratified_by": "F13",
        "files": [{"name": "memory-admissibility-policy.yaml", "sha256": digest}],
    }
    (tmp_path / "canon-release.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setenv(CANON_DIR_ENV, str(tmp_path))
    return tmp_path


class TestCanonDir:
    def test_dev_mode_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(CANON_DIR_ENV, raising=False)
        assert canon_dir() is None

    def test_prod_mode_returns_dir(self, canon_tree: Path) -> None:
        assert canon_dir() == canon_tree

    def test_missing_dir_returns_none(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv(CANON_DIR_ENV, str(tmp_path / "nonexistent"))
        assert canon_dir() is None


class TestCanonAwarePath:
    def test_canon_file_wins_over_repo_fallback(self, canon_tree: Path) -> None:
        resolved = canon_aware_path("memory-admissibility-policy.yaml", Path("/repo/config/policy.yaml"))
        assert resolved == canon_tree / "memory-admissibility-policy.yaml"

    def test_absent_canon_file_falls_back_to_repo(self, canon_tree: Path) -> None:
        resolved = canon_aware_path("not-in-canon.yaml", Path("/repo/config/not-in-canon.yaml"))
        assert resolved == Path("/repo/config/not-in-canon.yaml")

    def test_dev_mode_uses_repo_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(CANON_DIR_ENV, raising=False)
        resolved = canon_aware_path("policy.yaml", Path("/repo/config/policy.yaml"))
        assert resolved == Path("/repo/config/policy.yaml")


class TestCanonManifest:
    def test_manifest_loads(self, canon_tree: Path) -> None:
        manifest = canon_manifest()
        assert manifest is not None
        assert manifest["canon_version"] == "2026.09.16-r1"
        assert manifest["ratified_by"] == "F13"

    def test_dev_mode_manifest_is_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(CANON_DIR_ENV, raising=False)
        assert canon_manifest() is None


class TestCanonAttestation:
    def test_dev_mode_report_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(CANON_DIR_ENV, raising=False)
        att = canon_attestation()
        assert att == {"source": "repo-fallback", "active": False}

    def test_integrity_ok_when_hashes_match(self, canon_tree: Path) -> None:
        att = canon_attestation()
        assert att["active"] is True
        assert att["version"] == "2026.09.16-r1"
        assert att["files"] == 1
        assert att["files_verified"] == 1
        assert att["integrity"] == "ok"

    def test_integrity_mismatch_on_tampered_file(self, canon_tree: Path) -> None:
        (canon_tree / "memory-admissibility-policy.yaml").write_text("tampered\n", encoding="utf-8")
        att = canon_attestation()
        assert att["files"] == 1
        assert att["files_verified"] == 0
        assert att["integrity"] == "MISMATCH"

    def test_missing_manifest_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(CANON_DIR_ENV, str(tmp_path))
        att = canon_attestation()
        assert att["active"] is True
        assert att["manifest"] == "MISSING_OR_UNPARSEABLE"


class TestAdmissibilityWiring:
    """load_policy must honor the canon dir at CALL time (not import time)."""

    def test_load_policy_reads_from_canon_dir(self, canon_tree: Path) -> None:
        import arifosmcp.memory.admissibility as adm

        loaded = adm.load_policy()
        assert isinstance(loaded, dict)
        assert loaded == {"modes": {}, "status_vocabulary": []}

    def test_explicit_env_override_still_wins(self, canon_tree: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        override = tmp_path / "override-policy.yaml"
        override.write_text("modes: {strict: true}\nstatus_vocabulary: [ACTIVE]\n", encoding="utf-8")
        monkeypatch.setenv("MEMORY_ADMISSIBILITY_POLICY", str(override))
        import arifosmcp.memory.admissibility as adm

        loaded = adm.load_policy()
        assert loaded == {"modes": {"strict": True}, "status_vocabulary": ["ACTIVE"]}


class TestHealthAttestationCarriesCanon:
    def test_runtime_attestation_has_canon_block(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(CANON_DIR_ENV, raising=False)
        from arifosmcp.runtime.build import get_runtime_attestation

        att = get_runtime_attestation()
        assert "canon" in att
        assert att["canon"]["active"] is False
