"""Regression tests for deploy-release.sh lease session consistency (DP-E)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPLOY_RELEASE_SH = REPO_ROOT / "scripts" / "deploy-release.sh"
DEPLOY_LEASE_PY = REPO_ROOT / "scripts" / "deploy_lease.py"


def test_deploy_release_single_session_flag_in_acquire() -> None:
    """Acquire and both release paths in deploy-release.sh must use the same _LEASE_SESSION."""
    text = DEPLOY_RELEASE_SH.read_text(encoding="utf-8")

    acquire_match = re.search(
        r'if ! "\$_ARIFOS_PY" "\$_ARIFOS_LEASE" acquire .*?then',
        text,
        re.DOTALL,
    )
    assert acquire_match is not None, "acquire block not found in deploy-release.sh"
    acquire_block = acquire_match.group(0)

    session_flags = re.findall(r'--session\s+"[^"]+"', acquire_block)
    assert session_flags == ['--session "$_LEASE_SESSION"'], (
        f"Expected single --session \"$_LEASE_SESSION\" in acquire, got: {session_flags}"
    )

    release_sessions = re.findall(
        r'"\$_ARIFOS_LEASE"\s+release\b.*?--session\s+"([^"]+)"',
        text,
        re.DOTALL,
    )
    assert len(release_sessions) == 2, f"Expected trap + green release calls, got: {release_sessions}"
    assert all(s == "$_LEASE_SESSION" for s in release_sessions)


def _run_lease(state_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ARIFOS_STATE_DIRECTORY"] = str(state_dir)
    return subprocess.run(
        [sys.executable, str(DEPLOY_LEASE_PY), *args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_deploy_lease_acquire_wrong_session_rejected_and_matching_releases(tmp_path: Path) -> None:
    """Wrong-session release must fail with HOLD_NOT_OWNER; matching session must release cleanly."""
    for session_val in ("manual-20261114T084700Z", "custom-deploy-session-42"):
        state_dir = tmp_path / session_val
        state_dir.mkdir()

        acq = _run_lease(
            state_dir,
            "acquire",
            "--actor",
            "root",
            "--session",
            session_val,
            "--base",
            "0afa6ef0b80f",
            "--candidate",
            "0afa6ef0b80f",
            "--ttl",
            "600",
        )
        assert acq.returncode == 0, acq.stderr
        lease_data = json.loads((state_dir / "deploy_lease.json").read_text(encoding="utf-8"))
        lease_id = lease_data["lease_id"]

        wrong_sess = _run_lease(
            state_dir,
            "release",
            "--actor",
            "root",
            "--session",
            "deploy-999999",
            "--receipt",
            "test-trap",
        )
        assert wrong_sess.returncode == 3
        wrong_data = json.loads(wrong_sess.stdout)
        assert wrong_data["status"] == "HOLD_NOT_OWNER"
        assert wrong_data["mismatched"] == ["session"]

        wrong_lease_id = _run_lease(
            state_dir,
            "release",
            "--actor",
            "root",
            "--session",
            lease_id,
            "--receipt",
            "test-trap",
        )
        assert wrong_lease_id.returncode == 3

        good_rel = _run_lease(
            state_dir,
            "release",
            "--actor",
            "root",
            "--session",
            session_val,
            "--receipt",
            "deploy-release.sh",
            "--exit-code",
            "0",
            "--observed-head",
            "0afa6ef0b80f",
        )
        assert good_rel.returncode == 0, good_rel.stderr

        status = _run_lease(state_dir, "status")
        assert status.returncode == 0
        assert "state: IDLE" in status.stdout
