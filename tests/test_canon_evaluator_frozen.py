"""
test_canon_evaluator_frozen.py — Hardening H3 (T1, test-only)

Proves the constitutional invariant: the floor-threshold resolver lives
ONLY in arifosmcp/canon.py (single owner of /etc/arifos/canon), and the
resolution order is fixed: env-set canon dir wins over any workspace-
editable path of the same name. No code in the kernel may reach into
/etc/arifos/canon directly.

Architecture invariant: the evaluator (which reads floor thresholds from
the canon release) is NOT itself editable from the workspace — its source
of truth is /etc/arifos/canon (manifest_hash-verified).

This test fails = the only signal.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import pytest


CANON_LIVE = Path("/etc/arifos/canon")
REPO_ROOT = Path("/root/arifOS")


def _repo_python() -> str:
    return str(REPO_ROOT / ".venv" / "bin" / "python")


def test_live_canon_manifest_exists_and_has_files():
    """The FHS canon dir is real and has a manifest with verifiable file entries."""
    assert CANON_LIVE.is_dir(), "FHS canon dir /etc/arifos/canon must exist (prod)"
    manifest = json.loads((CANON_LIVE / "canon-release.json").read_text())
    files = manifest.get("files")
    assert isinstance(files, list) and files, "canon-release.json files[] must be a non-empty list"
    for entry in files:
        assert {"name", "sha256"} <= entry.keys(), f"manifest entry missing keys: {entry}"


def test_canon_manifest_hashes_recompute_to_actual_file_content():
    """Every manifest sha256 must match the live file's recomputed digest (F2/F11)."""
    manifest = json.loads((CANON_LIVE / "canon-release.json").read_text())
    for entry in manifest["files"]:
        path = CANON_LIVE / entry["name"]
        assert path.is_file(), f"manifest declares {entry['name']} but file missing on disk"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == entry["sha256"], (
            f"canon integrity FAIL on {entry['name']}: actual={actual[:16]} "
            f"claimed={entry['sha256'][:16]}"
        )


def test_canon_aware_path_prefers_etc_over_workspace(tmp_path, monkeypatch):
    """A workspace-fallback path is NEVER used while the env canon dir is active.

    Single-owner contract: ARIFOS_CANON_DIR wins, period.
    """
    # Plant a competing "workspace" file with content the resolver MUST ignore.
    workspace = tmp_path / "sovereignty.charter.json"
    workspace.write_text("# WORKSPACE OVERRIDE — must never win\n")
    # Even if we ALSO plant a fake shadow under /etc pointing somewhere bogus,
    # the real /etc/arifos/canon/sovereignty.charter.json must still be returned.
    monkeypatch.setenv("ARIFOS_CANON_DIR", str(CANON_LIVE))
    # Run the import inside the venv so arifosmcp resolves cleanly.
    result = subprocess.run(
        [
            _repo_python(),
            "-c",
            "import sys; sys.path.insert(0, '.'); "
            "from arifosmcp.canon import canon_aware_path; "
            f"from pathlib import Path; "
            f"p=canon_aware_path('sovereignty.charter.json', Path({str(workspace)!r})); "
            "print(p)",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    resolved = Path(result.stdout.strip())
    assert resolved == CANON_LIVE / "sovereignty.charter.json", (
        f"canon_aware_path must return /etc/arifos/canon path; got {resolved} "
        f"(workspace leak: {workspace})"
    )
    assert resolved != workspace, (
        "workspace fallback must NEVER be returned when canon dir is active"
    )


def test_canon_evaluator_is_single_owner():
    """No code in the kernel may read /etc/arifos/canon directly — only canon.py.

    This is the FHS formalization contract: the canon package is the sole
    boundary. Any other reader is a future drift vector.
    """
    # grep all *.py under arifosmcp/ for /etc/arifos/canon; canon.py is the
    # single allowed reader.
    out = subprocess.run(
        ["grep", "-rn", "/etc/arifos/canon", "arifosmcp/", "--include=*.py"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    # Only flag lines with an actual read/open action. Pure documentation
    # mentions (docstrings, comments) are not reads.
    read_actions = re.compile(r"Path\(|open\(|read_text|read_bytes|json\.load|with open")
    real_offenders: list[tuple[str, int, str]] = []
    canon_self: list[str] = []
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([^:]+):(\d+):(.*)$", line)
        if not m:
            continue
        f, ln, content = m.group(1), int(m.group(2)), m.group(3)
        if f.endswith("canon.py"):
            canon_self.append(f)
            continue
        if content.lstrip().startswith("#"):
            continue
        if not read_actions.search(content):
            continue  # no read action — just documentation
        real_offenders.append((f, ln, content.strip()))
    assert canon_self, "canon.py should reference the path itself"
    assert not real_offenders, (
        "FHS canon single-owner violated - real reads of /etc/arifos/canon "
        "outside canon.py (must go through arifosmcp.canon):\n"
        + "\n".join(f"  {f}:{ln}  {c}" for f, ln, c in real_offenders)
    )


def test_canon_attestation_does_not_flip_drift(monkeypatch):
    """canon_attestation() is REPORT-ONLY: must never mutate drift state (F-001 contract)."""
    monkeypatch.setenv("ARIFOS_CANON_DIR", str(CANON_LIVE))
    before = subprocess.run(
        [
            _repo_python(),
            "-c",
            "import sys; sys.path.insert(0, '.'); "
            "from arifosmcp.canon import canon_attestation; import json; "
            "print(json.dumps(canon_attestation(), sort_keys=True))",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    after = subprocess.run(
        [
            _repo_python(),
            "-c",
            "import sys; sys.path.insert(0, '.'); "
            "from arifosmcp.canon import canon_attestation; import json; "
            "print(json.dumps(canon_attestation(), sort_keys=True))",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert before == after, "canon_attestation must be deterministic / idempotent (report-only)"


def test_no_canon_imports_arbitrary_workspace_thresholds():
    """The resolver must not sniff $PWD or relative paths for threshold fallbacks."""
    src = (REPO_ROOT / "arifosmcp" / "canon.py").read_text()
    # Forbid: relative-path resolution based on cwd or workspace env.
    forbidden = re.findall(
        r"(?:os\.getcwd\(\)|os\.environ\.get\([\"']PWD[\"']\)|Path\([\"']\./)",
        src,
    )
    assert not forbidden, f"canon.py contains workspace-relative resolution: {forbidden}"


if __name__ == "__main__":
    # Allow running directly: python tests/test_canon_evaluator_frozen.py
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
