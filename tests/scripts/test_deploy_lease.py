"""Acceptance matrix for the candidate-bound deploy lease.

Every test runs against an isolated state directory, app marker, and runtime
target. No test touches /var/lib/arifos, /opt/arifos, or systemd.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LEASE = ROOT / "scripts" / "deploy_lease.py"
BODY = ROOT / "scripts" / "deploy_local_body.sh"
MAKEFILE = ROOT / "Makefile"


def _run(env: dict[str, str], *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(LEASE), *args],
        env=env,
        text=True,
        capture_output=True,
    )


def _paths(env: dict[str, str]) -> tuple[Path, Path, Path]:
    state = Path(env["ARIFOS_STATE_DIRECTORY"])
    app = Path(env["ARIFOS_APP_DIR"])
    runtime = Path(env["ARIFOS_RUNTIME_TARGET"])
    return state, app, runtime


def _lease_bytes(env: dict[str, str]) -> bytes:
    state, _, _ = _paths(env)
    p = state / "deploy_lease.json"
    return p.read_bytes() if p.exists() else b""


def _ledger_bytes(env: dict[str, str]) -> bytes:
    state, _, _ = _paths(env)
    p = state / "deploy_epochs.jsonl"
    return p.read_bytes() if p.exists() else b""


def _marker(env: dict[str, str], sha: str) -> None:
    _, app, _ = _paths(env)
    (app / ".git_commit").write_text(sha)


def _envelope_path(env: dict[str, str]) -> Path:
    state, _, _ = _paths(env)
    return state / "deploy_envelope.json"


def _read_envelope(env: dict[str, str]) -> dict:
    return json.loads(_envelope_path(env).read_text())


def _write_envelope(env: dict[str, str], data: dict) -> None:
    path = _envelope_path(env)
    path.write_text(json.dumps(data, indent=2))
    path.chmod(0o600)


def _acquire(
    env: dict[str, str],
    *,
    actor: str = "A",
    session: str = "S",
    base: str = "cand",
    candidate: str = "cand",
    entry: str = "make:deploy-local",
    deployment_id: str = "dep-test",
) -> tuple[subprocess.CompletedProcess, dict, dict]:
    p = _run(
        env,
        "acquire",
        "--actor",
        actor,
        "--session",
        session,
        "--base",
        base,
        "--candidate",
        candidate,
        "--entry-point",
        entry,
        "--deployment-id",
        deployment_id,
    )
    assert p.returncode == 0, p.stdout + p.stderr
    payload = json.loads(p.stdout)
    return p, payload["lease"], _read_envelope(env)


def _rows(env: dict[str, str]) -> list[dict]:
    state, _, _ = _paths(env)
    p = state / "deploy_epochs.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def _last_released(env: dict[str, str]) -> dict:
    for row in reversed(_rows(env)):
        if row.get("event") == "RELEASED":
            return row
    raise AssertionError("no RELEASED row")


@pytest.fixture
def env(tmp_path: Path) -> dict[str, str]:
    state = tmp_path / "state"
    app = tmp_path / "app"
    runtime = tmp_path / "runtime" / "arifosmcp"
    state.mkdir()
    app.mkdir()
    runtime.mkdir(parents=True)
    (app / ".git_commit").write_text("old")
    (runtime / "fake.py").write_text("x = 1\n")
    e = os.environ.copy()
    e.update(
        {
            "ARIFOS_STATE_DIRECTORY": str(state),
            "ARIFOS_APP_DIR": str(app),
            "ARIFOS_RUNTIME_TARGET": str(runtime),
        }
    )
    return e


# ── ownership ──────────────────────────────────────────────────────────────
def test_acquire_pins_candidate_and_envelope_is_0600(env):
    p, lease, envelope = _acquire(env, candidate="abc123")
    assert lease["candidate_commit"] == "abc123"
    assert lease["session"] == "S"
    assert lease["rate_gate_version"] == 1
    assert lease["entry_point"] == "make:deploy-local"
    assert "holder_token" not in p.stdout
    assert envelope["holder_token"]
    state, _, _ = _paths(env)
    assert stat.S_IMODE(_envelope_path(env).stat().st_mode) == 0o600
    assert stat.S_IMODE((state / "deploy_lease.json").stat().st_mode) == 0o600


def test_second_acquire_refused_and_writes_nothing(env):
    _acquire(env)
    before = _lease_bytes(env)
    p = _run(
        env,
        "acquire",
        "--actor",
        "B",
        "--session",
        "S2",
        "--base",
        "cand",
        "--candidate",
        "cand2",
    )
    assert p.returncode == 3
    assert "HOLD_CONCURRENT_DEPLOY" in p.stdout
    assert _lease_bytes(env) == before


@pytest.mark.parametrize("missing", ["--actor", "--session"])
def test_missing_required_acquire_field_refused(env, missing):
    args = [
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    ]
    idx = args.index(missing)
    del args[idx : idx + 2]
    p = _run(env, *args)
    assert p.returncode != 0
    state, _, _ = _paths(env)
    assert not (state / "deploy_lease.json").exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("actor", "B"),
        ("session", "X"),
        ("lease_id", "wrong"),
        ("candidate_commit", "other"),
        ("holder_token", "wrong"),
        ("envelope_id", "wrong"),
    ],
)
def test_envelope_mismatch_refused_without_writes(env, field, value):
    _acquire(env)
    envelope = _read_envelope(env)
    envelope[field] = value
    _write_envelope(env, envelope)
    before = _lease_bytes(env)
    p = _run(env, "check-envelope", "--actor", "A", "--session", "S")
    assert p.returncode == 3
    assert "HOLD_NOT_OWNER" in p.stdout
    assert _lease_bytes(env) == before


def test_envelope_missing_token_refused(env):
    _acquire(env)
    envelope = _read_envelope(env)
    envelope.pop("holder_token")
    _write_envelope(env, envelope)
    before = _lease_bytes(env)
    p = _run(env, "check-envelope", "--actor", "A", "--session", "S")
    assert p.returncode == 3
    assert _lease_bytes(env) == before


def test_envelope_permissions_too_open_refused(env):
    _acquire(env)
    _envelope_path(env).chmod(0o644)
    p = _run(env, "check-envelope", "--actor", "A", "--session", "S")
    assert p.returncode == 7
    assert "HOLD_UNAPPROVED_ENTRY_POINT" in p.stdout


def test_release_without_actor_refused(env):
    _acquire(env)
    before = _lease_bytes(env)
    p = _run(env, "release", "--session", "S")
    assert p.returncode != 0
    assert _lease_bytes(env) == before


def test_correct_holder_release_succeeds_and_strips_token(env):
    _acquire(env, candidate="cand")
    _marker(env, "cand")
    p = _run(env, "release", "--actor", "A", "--session", "S", "--receipt", "ok")
    assert p.returncode == 0, p.stdout + p.stderr
    payload = json.loads(p.stdout)
    assert payload["status"] == "RELEASED"
    assert payload["candidate_bound"] is True
    assert not (Path(env["ARIFOS_STATE_DIRECTORY"]) / "deploy_lease.json").exists()
    assert not _envelope_path(env).exists()
    row = _last_released(env)
    blob = json.dumps(row)
    assert "holder_token" not in blob
    assert "holder_token_sha256" not in blob
    assert row["candidate_match"] is True


def test_rejected_release_preserves_lease_and_ledger(env):
    _acquire(env)
    envelope = _read_envelope(env)
    envelope["holder_token"] = "wrong"
    _write_envelope(env, envelope)
    lease_before = _lease_bytes(env)
    ledger_before = _ledger_bytes(env)
    p = _run(env, "release", "--actor", "A", "--session", "S")
    assert p.returncode == 3
    assert _lease_bytes(env) == lease_before
    assert _ledger_bytes(env) == ledger_before


def test_release_without_a_lease_is_refused(env):
    p = _run(env, "release", "--actor", "A", "--session", "S")
    assert p.returncode == 5
    assert "NO_ACTIVE_LEASE" in p.stdout


def test_release_without_envelope_is_refused(env):
    _acquire(env)
    _envelope_path(env).unlink()
    before = _lease_bytes(env)
    p = _run(env, "release", "--actor", "A", "--session", "S")
    assert p.returncode == 5
    assert _lease_bytes(env) == before


def test_expired_lease_does_not_block_forever(env):
    state, _, _ = _paths(env)
    state.mkdir(exist_ok=True)
    (state / "deploy_lease.json").write_text(
        json.dumps(
            {
                "lease_id": "dl-expired",
                "event": "ACQUIRED",
                "actor": "old",
                "session": "old",
                "base_commit": "b",
                "candidate_commit": "c",
                "deployment_epoch": 1,
                "expires_at": "2000-01-01T00:00:00Z",
            }
        )
    )
    p = _run(
        env,
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    )
    assert p.returncode == 0
    assert any(r.get("event") == "LEASE_EXPIRED_UNRELEASED" for r in _rows(env))


def test_verify_epoch_wrong_actor_or_session_refused(env):
    _, lease, _ = _acquire(env, candidate="cand")
    _marker(env, "cand")
    assert _run(env, "release", "--actor", "A", "--session", "S").returncode == 0
    p = _run(
        env,
        "verify-epoch",
        "--lease-id",
        lease["lease_id"],
        "--verdict",
        "PASS",
        "--evidence",
        "x",
        "--actor",
        "B",
        "--session",
        "S",
    )
    assert p.returncode == 3
    assert "HOLD_NOT_OWNER" in p.stdout


# ── candidate binding and rate gate ────────────────────────────────────────
def test_verify_epoch_before_release_is_unknown(env):
    _, lease, _ = _acquire(env)
    p = _run(
        env,
        "verify-epoch",
        "--lease-id",
        lease["lease_id"],
        "--verdict",
        "PASS",
        "--evidence",
        "x",
        "--actor",
        "A",
        "--session",
        "S",
    )
    assert p.returncode == 5
    assert "UNKNOWN_EPOCH" in p.stdout


def test_release_then_verify_epoch_pass_clears_rate_gate(env):
    _, lease, _ = _acquire(env, candidate="cand")
    _marker(env, "cand")
    assert _run(env, "release", "--actor", "A", "--session", "S").returncode == 0
    p = _run(
        env,
        "verify-epoch",
        "--lease-id",
        lease["lease_id"],
        "--verdict",
        "PASS",
        "--evidence",
        "ok",
        "--actor",
        "A",
        "--session",
        "S",
    )
    assert p.returncode == 0, p.stdout + p.stderr
    assert json.loads(p.stdout)["verdict"] == "PASS"
    nxt = _run(
        env,
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    )
    assert nxt.returncode == 0


def test_rate_gate_blocks_until_verdict(env):
    _, lease, _ = _acquire(env, candidate="cand")
    _marker(env, "cand")
    assert _run(env, "release", "--actor", "A", "--session", "S").returncode == 0
    p = _run(
        env,
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    )
    assert p.returncode == 6
    assert "HOLD_UNVERIFIED_DEPLOY" in p.stdout
    assert (
        _run(
            env,
            "verify-epoch",
            "--lease-id",
            lease["lease_id"],
            "--verdict",
            "PASS",
            "--evidence",
            "ok",
            "--actor",
            "A",
            "--session",
            "S",
        ).returncode
        == 0
    )
    p2 = _run(
        env,
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    )
    assert p2.returncode == 0


def test_candidate_mismatch_release_blocks_and_cannot_pass(env):
    _, lease, _ = _acquire(env, candidate="cand")
    # marker intentionally stays "old"
    p = _run(env, "release", "--actor", "A", "--session", "S")
    assert p.returncode == 11
    assert "HOLD_CANDIDATE_MISMATCH" in p.stdout
    row = _last_released(env)
    assert row["candidate_match"] is False
    assert row["verification_status"] == "CANDIDATE_MISMATCH"
    v = _run(
        env,
        "verify-epoch",
        "--lease-id",
        lease["lease_id"],
        "--verdict",
        "PASS",
        "--evidence",
        "x",
        "--actor",
        "A",
        "--session",
        "S",
    )
    assert v.returncode == 12
    assert "candidate_mismatch" in v.stdout


def test_failed_epoch_requires_f13_resolution_then_unblocks(env):
    _, lease, _ = _acquire(env, candidate="cand")
    # marker stays "old" -> candidate mismatch epoch
    assert _run(env, "release", "--actor", "A", "--session", "S").returncode == 11
    blocked = _run(
        env,
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    )
    assert blocked.returncode == 6
    refused = _run(
        env,
        "resolve-epoch",
        "--lease-id",
        lease["lease_id"],
        "--authority",
        "agent",
        "--receipt",
        "x",
        "--reason",
        "x",
        "--actor",
        "A",
        "--session",
        "S",
    )
    assert refused.returncode == 3
    resolved = _run(
        env,
        "resolve-epoch",
        "--lease-id",
        lease["lease_id"],
        "--authority",
        "F13",
        "--receipt",
        "ARIFOS-TEST",
        "--reason",
        "known test failure",
        "--actor",
        "ARIF",
        "--session",
        "F13",
    )
    assert resolved.returncode == 0, resolved.stdout + resolved.stderr
    assert json.loads(resolved.stdout)["status"] == "RESOLVED"
    allowed = _run(
        env,
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    )
    assert allowed.returncode == 0


def test_body_exit_nonzero_cannot_be_stamped_pass(env):
    _, lease, _ = _acquire(env, candidate="cand")
    _marker(env, "cand")
    p = _run(
        env,
        "release",
        "--actor",
        "A",
        "--session",
        "S",
        "--exit-code",
        "9",
    )
    assert p.returncode == 0  # artifact matches; the body itself failed
    v = _run(
        env,
        "verify-epoch",
        "--lease-id",
        lease["lease_id"],
        "--verdict",
        "PASS",
        "--evidence",
        "x",
        "--actor",
        "A",
        "--session",
        "S",
    )
    assert v.returncode == 12
    assert "body_exit_nonzero" in v.stdout


def test_verify_baseline_drift(env):
    _acquire(env)
    _marker(env, "different")
    p = _run(env, "verify-baseline")
    assert p.returncode == 4
    assert "HOLD_ARTIFACT_DRIFT" in p.stdout


def test_verify_candidate_unobservable(env):
    _acquire(env, candidate="cand")
    _marker(env, "cand")
    _, _, runtime = _paths(env)
    shutil.rmtree(runtime)
    p = _run(env, "verify-candidate", "--actor", "A", "--session", "S")
    assert p.returncode == 7
    assert "ARTIFACT_UNOBSERVABLE" in p.stdout


def test_verify_candidate_pass_and_mismatch(env):
    _acquire(env, candidate="cand")
    _marker(env, "cand")
    p = _run(env, "verify-candidate", "--actor", "A", "--session", "S")
    assert p.returncode == 0
    assert "CANDIDATE_BOUND" in p.stdout
    _marker(env, "other")
    p2 = _run(env, "verify-candidate", "--actor", "A", "--session", "S")
    assert p2.returncode == 11
    assert "HOLD_CANDIDATE_MISMATCH" in p2.stdout


def test_verify_artifact_and_candidate(env):
    _acquire(env, candidate="cand")
    _marker(env, "cand")
    assert _run(env, "release", "--actor", "A", "--session", "S").returncode == 0
    p = _run(env, "verify")
    assert p.returncode == 0, p.stdout + p.stderr
    assert "ARTIFACT_UNCHANGED" in p.stdout
    # manifest change alone must fail
    _, _, runtime = _paths(env)
    (runtime / "fake.py").write_text("y = 2\n")
    p2 = _run(env, "verify")
    assert p2.returncode == 4
    payload = json.loads(p2.stdout)
    assert payload["checks"]["manifest_same"] is False
    # restore manifest; candidate marker mismatch must still fail
    (runtime / "fake.py").write_text("x = 1\n")
    _marker(env, "other")
    p3 = _run(env, "verify")
    assert p3.returncode == 4
    assert json.loads(p3.stdout)["checks"]["candidate_same"] is False


def test_unobservable_is_not_unchanged(env):
    _acquire(env, candidate="cand")
    _marker(env, "cand")
    assert _run(env, "release", "--actor", "A", "--session", "S").returncode == 0
    _, _, runtime = _paths(env)
    shutil.rmtree(runtime)
    p = _run(env, "verify")
    assert p.returncode == 7
    assert "ARTIFACT_UNOBSERVABLE" in p.stdout


def test_historical_and_non_governed_epochs_do_not_block(env):
    state, _, _ = _paths(env)
    ledger = state / "deploy_epochs.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "event": "RELEASED",
                "lease_id": "dl-probe",
                "deployment_epoch": 4,
                "entry_point": "unknown",
                "candidate_match": False,
            }
        )
        + "\n"
    )
    p = _run(
        env,
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    )
    assert p.returncode == 0


def test_governed_release_without_verdict_blocks(env):
    state, _, _ = _paths(env)
    ledger = state / "deploy_epochs.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "event": "RELEASED",
                "lease_id": "dl-governed",
                "deployment_epoch": 1,
                "entry_point": "make:deploy-local",
                "rate_gate_version": 1,
                "candidate_match": True,
            }
        )
        + "\n"
    )
    p = _run(
        env,
        "acquire",
        "--actor",
        "A",
        "--session",
        "S",
        "--base",
        "cand",
        "--candidate",
        "cand",
    )
    assert p.returncode == 6
    assert "HOLD_UNVERIFIED_DEPLOY" in p.stdout


# ── body preflights ────────────────────────────────────────────────────────
@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    (r / "scripts").mkdir(parents=True)
    shutil.copy(LEASE, r / "scripts" / "deploy_lease.py")
    shutil.copy(BODY, r / "scripts" / "deploy_local_body.sh")
    (r / "seed.txt").write_text("seed\n")
    subprocess.run(["git", "init", "-q"], cwd=r, check=True)
    subprocess.run(["git", "add", "."], cwd=r, check=True)
    subprocess.run(
        ["git", "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-qm", "seed"],
        cwd=r,
        check=True,
    )
    return r


def _git_head(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _git_commit(repo: Path, name: str, text: str) -> str:
    (repo / name).write_text(text)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=a@b",
            "-c",
            "user.name=a",
            "commit",
            "-qm",
            name,
        ],
        check=True,
    )
    return _git_head(repo)


def _body_env(env: dict[str, str], repo: Path, **over: str) -> dict[str, str]:
    e = dict(env)
    e.update(
        {
            "DIR": str(repo),
            "PYTHON": sys.executable,
            "DEPLOY_ACTOR": "A",
            "DEPLOY_SESSION": "S",
            "DEPLOY_DRY_RUN": "1",
            "CONFORMANCE_CMD": "true",
        }
    )
    e.update(over)
    return e


def _body(env: dict[str, str], repo: Path, **over: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(repo / "scripts" / "deploy_local_body.sh")],
        env=_body_env(env, repo, **over),
        text=True,
        capture_output=True,
    )


def test_body_clean_dry_run_succeeds(env, repo):
    head = _git_head(repo)
    _marker(env, head)
    _acquire(env, base=head, candidate=head)
    p = _body(env, repo)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "verify-epoch PASS" in p.stdout
    assert any(r.get("event") == "VERDICT" and r.get("verdict") == "PASS" for r in _rows(env))


def test_body_candidate_changed_stops_before_writes(env, repo):
    head = _git_head(repo)
    _marker(env, head)
    _acquire(env, base=head, candidate=head)
    new_head = _git_commit(repo, "second.txt", "second\n")
    p = _body(env, repo)
    assert p.returncode == 9
    assert "HOLD_CANDIDATE_CHANGED" in p.stderr
    row = _last_released(env)
    assert row["observed_head"] == new_head
    assert row["source_match"] is False
    assert row["candidate_match"] is False


def test_body_abort_path_releases_and_preserves_exit_code(env, repo):
    head = _git_head(repo)
    _marker(env, head)
    _acquire(env, base=head, candidate=head)
    p = _body(env, repo, CONFORMANCE_CMD="false")
    assert p.returncode == 1
    assert not (Path(env["ARIFOS_STATE_DIRECTORY"]) / "deploy_lease.json").exists()
    row = _last_released(env)
    assert str(row["body_exit_code"]) == "1"


def test_body_dirty_source_stops(env, repo):
    head = _git_head(repo)
    _marker(env, head)
    _acquire(env, base=head, candidate=head)
    (repo / "seed.txt").write_text("dirty\n")
    p = _body(env, repo)
    assert p.returncode == 8
    assert "HOLD_DIRTY_SOURCE" in p.stderr


def test_body_unapproved_entry_point_stops(env, repo):
    head = _git_head(repo)
    _marker(env, head)
    _acquire(env, base=head, candidate=head, entry="unknown")
    p = _body(env, repo)
    assert p.returncode == 7
    assert "HOLD_UNAPPROVED_ENTRY_POINT" in p.stderr
    # the valid envelope lets the trap release the lease; no PASS verdict exists
    assert not (Path(env["ARIFOS_STATE_DIRECTORY"]) / "deploy_lease.json").exists()


def test_body_missing_envelope_leaves_lease_fail_closed(env, repo):
    head = _git_head(repo)
    _marker(env, head)
    _acquire(env, base=head, candidate=head)
    _envelope_path(env).unlink()
    p = _body(env, repo)
    assert p.returncode == 7
    status = _run(env, "status", "--json")
    assert json.loads(status.stdout)["state"] == "LEASED"


# ── static security regressions ────────────────────────────────────────────
def test_body_never_passes_token_through_argv():
    text = BODY.read_text()
    assert "--token" not in text
    assert "check-envelope" in text
    assert "verify-baseline" in text
    assert "HOLD_CANDIDATE_CHANGED" in text


def test_body_uses_fixed_runtime_for_site_packages():
    text = BODY.read_text()
    assert 'SITE_PACKAGES="$("$RUNTIME_PYTHON" -c' in text
    assert 'SITE_PACKAGES="$("$PYTHON" -c' not in text


def test_body_keeps_deployed_commit_stamp():
    text = BODY.read_text()
    assert "/opt/arifos/releases/deployed-commit" in text


def test_body_deploys_from_git_archive_not_mutable_worktree():
    text = BODY.read_text()
    assert 'git -C "$DIR" archive' in text
    assert '"$EXPORT_DIR/" /opt/arifos/app/' in text
    assert "resolve-epoch" not in text


def test_makefile_never_passes_token_through_argv():
    text = MAKEFILE.read_text()
    block = text.split("deploy-local:", 1)[1].split("\nsot-check:", 1)[0]
    assert "--token" not in block
    assert "DEPLOY_SESSION" in block
