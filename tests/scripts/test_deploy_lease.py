"""Deploy lease — production mutation must be serialized (2026-10-26).

Failure class this guards (measured): three runtime code states in 21 minutes on
one host. 8359618fe was deployed and effect-verified, then silently overwritten
by another session's deploy of cd28e52cf; the verified fix regressed.

Ownership is now four-way: actor + session + lease_id + opaque holder token.
Three of those are readable from /tmp/arifos-deploy-lease.json by any process on
the box, so they prove knowledge, not ownership. Only the token is secret, and
only its sha256 is stored (never in the epoch ledger).

These tests exercise the CLI exactly as the deploy path does, with the state
directory redirected into tmp_path so they never touch /var/lib/arifos.
"""

from __future__ import annotations

import hashlib
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


def _acquire(
    state_dir: Path,
    *,
    actor: str = "agent-a",
    session: str = "sess-a",
    base: str = "b1",
    candidate: str = "c1",
    ttl: str | None = None,
) -> subprocess.CompletedProcess:
    args = [
        "acquire",
        "--actor",
        actor,
        "--session",
        session,
        "--base",
        base,
        "--candidate",
        candidate,
    ]
    if ttl is not None:
        args += ["--ttl", ttl]
    return _run(state_dir, *args)


def _capability(acquired: subprocess.CompletedProcess) -> tuple[str, str]:
    payload = json.loads(acquired.stdout)
    return payload["lease"]["lease_id"], payload["holder_token"]


def _release(
    state_dir: Path,
    *,
    actor: str = "agent-a",
    session: str = "sess-a",
    lease_id: str,
    token: str,
) -> subprocess.CompletedProcess:
    return _run(
        state_dir,
        "release",
        "--actor",
        actor,
        "--session",
        session,
        "--lease-id",
        lease_id,
        "--token",
        token,
    )


def _lease_bytes(state_dir: Path) -> str:
    p = state_dir / "deploy_lease.json"
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "ABSENT"


def _ledger_len(state_dir: Path) -> int:
    p = state_dir / "deploy_epochs.jsonl"
    return sum(1 for line in p.read_text().splitlines() if line.strip()) if p.exists() else 0


def test_acquire_then_concurrent_acquire_is_refused(tmp_path: Path) -> None:
    first = _acquire(tmp_path)
    assert first.returncode == 0, first.stderr
    lease = json.loads(first.stdout)["lease"]
    assert lease["deployment_epoch"] >= 1
    assert lease["target_runtime"].endswith("arifosmcp")
    assert "holder_token_sha256" in lease
    assert "holder_token" not in lease, "the raw capability must never be stored on disk"

    before = _lease_bytes(tmp_path)
    second = _acquire(tmp_path, actor="agent-b", session="sess-b", base="b2", candidate="c2")
    assert second.returncode == 3, "a second deploy must be refused, not silently accepted"
    payload = json.loads(second.stdout)
    assert payload["status"] == "HOLD_CONCURRENT_DEPLOY"
    assert payload["holder"]["actor"] == "agent-a"
    assert _lease_bytes(tmp_path) == before, "the refused acquire wrote to the lease"


def test_correct_holder_releases(tmp_path: Path) -> None:
    acquired = _acquire(tmp_path)
    lease_id, token = _capability(acquired)
    out = _release(tmp_path, lease_id=lease_id, token=token)
    assert out.returncode == 0, out.stderr
    payload = json.loads(out.stdout)
    assert payload["status"] == "RELEASED"
    assert payload["artifact"]["module_count"] > 0
    assert not (tmp_path / "deploy_lease.json").exists()


def test_only_the_owner_may_release(tmp_path: Path) -> None:
    acquired = _acquire(tmp_path)
    lease_id, token = _capability(acquired)
    before = _lease_bytes(tmp_path)

    wrong = _release(tmp_path, actor="agent-b", lease_id=lease_id, token=token)
    assert wrong.returncode == 3
    assert json.loads(wrong.stdout)["status"] == "HOLD_NOT_OWNER"
    assert _lease_bytes(tmp_path) == before, "a refused release mutated the lease"

    right = _release(tmp_path, lease_id=lease_id, token=token)
    assert right.returncode == 0
    assert json.loads(right.stdout)["status"] == "RELEASED"


def test_missing_actor_is_refused_before_touching_the_lease(tmp_path: Path) -> None:
    acquired = _acquire(tmp_path)
    lease_id, token = _capability(acquired)
    before = _lease_bytes(tmp_path)

    out = _run(tmp_path, "release", "--session", "sess-a", "--lease-id", lease_id, "--token", token)
    assert out.returncode != 0, "release without --actor must be refused"
    assert _lease_bytes(tmp_path) == before
    assert json.loads(_run(tmp_path, "status", "--json").stdout)["state"] == "LEASED"


def test_wrong_session_is_refused(tmp_path: Path) -> None:
    acquired = _acquire(tmp_path)
    lease_id, token = _capability(acquired)
    before = _lease_bytes(tmp_path)

    out = _release(tmp_path, session="sess-B", lease_id=lease_id, token=token)
    assert out.returncode == 3
    payload = json.loads(out.stdout)
    assert payload["status"] == "HOLD_NOT_OWNER"
    assert "session" in payload["mismatched"]
    assert _lease_bytes(tmp_path) == before


def test_wrong_lease_id_is_refused(tmp_path: Path) -> None:
    acquired = _acquire(tmp_path)
    _lease_id, token = _capability(acquired)
    before = _lease_bytes(tmp_path)

    out = _release(tmp_path, lease_id="dl-not-the-one", token=token)
    assert out.returncode == 3
    assert "lease_id" in json.loads(out.stdout)["mismatched"]
    assert _lease_bytes(tmp_path) == before


def test_wrong_or_missing_token_is_refused(tmp_path: Path) -> None:
    acquired = _acquire(tmp_path)
    lease_id, _token = _capability(acquired)
    before = _lease_bytes(tmp_path)
    ledger_before = _ledger_len(tmp_path)

    out = _release(tmp_path, lease_id=lease_id, token="not-the-capability")
    assert out.returncode == 3
    payload = json.loads(out.stdout)
    assert "token" in payload["mismatched"]
    assert _lease_bytes(tmp_path) == before, "protected state changed on a refused release"
    assert _ledger_len(tmp_path) == ledger_before, "a refused release appended an epoch"


def test_release_appends_an_epoch_to_the_ledger(tmp_path: Path) -> None:
    acquired = _acquire(tmp_path)
    lease_id, token = _capability(acquired)
    _release(tmp_path, lease_id=lease_id, token=token)
    rows = [
        json.loads(line)
        for line in (tmp_path / "deploy_epochs.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert [r["event"] for r in rows] == ["RELEASED"]
    for field in (
        "lease_id",
        "actor",
        "session",
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
    assert "holder_token_sha256" not in rows[0], "capability digest leaked into the ledger"


def test_verify_detects_an_unapproved_artifact_replacement(tmp_path: Path) -> None:
    acquired = _acquire(tmp_path)
    lease_id, token = _capability(acquired)
    _release(tmp_path, lease_id=lease_id, token=token)

    ok = _run(tmp_path, "verify")
    assert ok.returncode == 0
    assert json.loads(ok.stdout)["status"] == "ARTIFACT_UNCHANGED"

    ledger = tmp_path / "deploy_epochs.jsonl"
    rows = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
    rows[0]["resulting_artifact"]["manifest_sha256"] = "0" * 64
    ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    changed = _run(tmp_path, "verify")
    assert changed.returncode == 4
    assert json.loads(changed.stdout)["status"] == "ARTIFACT_CHANGED"


def test_release_without_a_lease_is_refused(tmp_path: Path) -> None:
    out = _run(
        tmp_path,
        "release",
        "--actor",
        "agent-a",
        "--session",
        "sess-a",
        "--lease-id",
        "dl-absent",
        "--token",
        "absent",
    )
    assert out.returncode == 5
    assert json.loads(out.stdout)["status"] == "NO_ACTIVE_LEASE"


def test_expired_lease_does_not_block_forever(tmp_path: Path) -> None:
    # ttl=0 → already expired at the next read. Must not deadlock production.
    _acquire(tmp_path, ttl="0")
    again = _acquire(tmp_path, actor="agent-b", session="sess-b", base="b2", candidate="c2")
    assert again.returncode == 0, "an expired lease must not permanently block deploys"
    assert json.loads(again.stdout)["lease"]["actor"] == "agent-b"


def test_abort_path_releases_the_lease_and_preserves_exit_code(tmp_path: Path) -> None:
    """Measured defect (2026-10-26): the conformance spine exits 1 on CAUTION,
    which aborted `make deploy-local` before the release line, leaving production
    leased for the rest of the TTL. The body script must release on ANY exit and
    exit with the original status.

    Exercised with DEPLOY_DRY_RUN=1 so no production path is touched, and with
    CONFORMANCE_CMD=false to force the abort.
    """
    body = REPO / "scripts" / "deploy_local_body.sh"
    assert body.exists(), "deploy body script missing"

    acquired = _acquire(tmp_path)
    assert acquired.returncode == 0
    lease_id, token = _capability(acquired)
    assert (tmp_path / "deploy_lease.json").exists()

    env = dict(os.environ)
    env.update(
        {
            "ARIFOS_STATE_DIRECTORY": str(tmp_path),
            "DEPLOY_DRY_RUN": "1",
            "CONFORMANCE_CMD": "false",  # force the abort AFTER the lease is held
            "DEPLOY_ACTOR": "agent-a",
            "DEPLOY_SESSION": "sess-a",
            "DEPLOY_LEASE_ID": lease_id,
            "DEPLOY_HOLDER_TOKEN": token,
            "PYTHON": sys.executable,
            "DIR": str(REPO),
            "GIT_SHA": "deadbeefdeadbeef",
        }
    )
    run = subprocess.run(["bash", str(body)], capture_output=True, text=True, env=env)

    assert run.returncode != 0, "a failing conformance spine must fail the deploy"
    assert not (tmp_path / "deploy_lease.json").exists(), (
        "lease survived an aborted deploy — production stays leased and every "
        "subsequent deploy is refused until the TTL expires"
    )
    rows = [
        json.loads(line)
        for line in (tmp_path / "deploy_epochs.jsonl").read_text().splitlines()
        if line.strip()
    ]
    released = [r for r in rows if r.get("event") == "RELEASED"]
    assert len(released) == 1, f"expected exactly one RELEASED row, got {len(released)}"
    assert released[0]["actor"] == "agent-a"
    assert released[0]["receipt"] == "docs/releases"
    assert released[0]["resulting_artifact"]["module_count"] > 0
