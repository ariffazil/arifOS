"""Deploy lease — production mutation must be serialized (2026-10-26).

Failure class this guards (measured): three runtime code states in 21 minutes on
one host. 8359618fe was deployed and effect-verified, then silently overwritten
by another session's deploy of cd28e52cf; the verified fix regressed.

These tests exercise the CLI exactly as the deploy path does, with the state
directory redirected into tmp_path so they never touch /var/lib/arifos.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "deploy_lease.py"


def _run(state_dir: Path, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["ARIFOS_STATE_DIRECTORY"] = str(state_dir)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env
    )


def test_acquire_then_concurrent_acquire_is_refused(tmp_path: Path) -> None:
    first = _run(tmp_path, "acquire", "--actor", "agent-a", "--base", "b1", "--candidate", "c1")
    assert first.returncode == 0, first.stderr
    lease = json.loads(first.stdout)["lease"]
    assert lease["deployment_epoch"] >= 1
    assert lease["target_runtime"].endswith("arifosmcp")

    second = _run(tmp_path, "acquire", "--actor", "agent-b", "--base", "b2", "--candidate", "c2")
    assert second.returncode == 3, "a second deploy must be refused, not silently accepted"
    payload = json.loads(second.stdout)
    assert payload["status"] == "HOLD_CONCURRENT_DEPLOY"
    assert payload["holder"]["actor"] == "agent-a"

    # Nothing was written by the refused attempt: the holder is unchanged.
    status = json.loads(_run(tmp_path, "status", "--json").stdout)
    assert status["lease"]["actor"] == "agent-a"


def test_only_the_owner_may_release(tmp_path: Path) -> None:
    _run(tmp_path, "acquire", "--actor", "agent-a", "--base", "b1", "--candidate", "c1")
    wrong = _run(tmp_path, "release", "--actor", "agent-b")
    assert wrong.returncode == 3
    assert json.loads(wrong.stdout)["status"] == "HOLD_NOT_OWNER"

    right = _run(tmp_path, "release", "--actor", "agent-a")
    assert right.returncode == 0
    out = json.loads(right.stdout)
    assert out["status"] == "RELEASED"
    assert out["artifact"]["module_count"] > 0


def test_release_appends_an_epoch_to_the_ledger(tmp_path: Path) -> None:
    _run(tmp_path, "acquire", "--actor", "agent-a", "--base", "b1", "--candidate", "c1")
    _run(tmp_path, "release", "--actor", "agent-a")
    ledger = tmp_path / "deploy_epochs.jsonl"
    rows = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
    assert [r["event"] for r in rows] == ["RELEASED"]
    for field in (
        "lease_id",
        "actor",
        "base_commit",
        "candidate_commit",
        "target_runtime",
        "acquired_at",
        "expires_at",
        "previous_artifact",
        "resulting_artifact",
        "deployment_epoch",
    ):
        assert field in rows[0], f"ownership record missing {field}"


def test_verify_detects_an_unapproved_artifact_replacement(tmp_path: Path) -> None:
    _run(tmp_path, "acquire", "--actor", "agent-a", "--base", "b1", "--candidate", "c1")
    _run(tmp_path, "release", "--actor", "agent-a")

    ok = _run(tmp_path, "verify")
    assert ok.returncode == 0
    assert json.loads(ok.stdout)["status"] == "ARTIFACT_UNCHANGED"

    # Simulate "someone replaced production outside the lease" by rewriting the
    # approved manifest in the ledger.
    ledger = tmp_path / "deploy_epochs.jsonl"
    rows = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
    rows[0]["resulting_artifact"]["manifest_sha256"] = "0" * 64
    ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    changed = _run(tmp_path, "verify")
    assert changed.returncode == 4
    assert json.loads(changed.stdout)["status"] == "ARTIFACT_CHANGED"


def test_release_without_a_lease_is_refused(tmp_path: Path) -> None:
    out = _run(tmp_path, "release", "--actor", "agent-a")
    assert out.returncode == 5
    assert json.loads(out.stdout)["status"] == "NO_ACTIVE_LEASE"


def test_expired_lease_does_not_block_forever(tmp_path: Path) -> None:
    # ttl=0 → already expired at the next read. Must not deadlock production.
    _run(
        tmp_path, "acquire", "--actor", "agent-a", "--base", "b1", "--candidate", "c1", "--ttl", "0"
    )
    again = _run(tmp_path, "acquire", "--actor", "agent-b", "--base", "b2", "--candidate", "c2")
    assert again.returncode == 0, "an expired lease must not permanently block deploys"
    assert json.loads(again.stdout)["lease"]["actor"] == "agent-b"
