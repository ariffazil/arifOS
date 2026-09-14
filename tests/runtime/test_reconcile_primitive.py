"""CI test for A-FORGE reconciliation primitive (Diff→Validation→Policy→Drift Guard→Reconcile→Receipt→Witness)."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

RECONCILE = "/root/A-FORGE/leases/reconcile.py"
sys.path.insert(0, "/root/A-FORGE/leases")
from lease_engine import engine  # noqa: E402

def _git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, check=False)

def _setup(tmp: Path, fence_files: list[str]):
    repo = tmp / "rec_repo"
    repo.mkdir()
    _git(str(repo), "init", "-q", "-b", "main")
    _git(str(repo), "config", "user.email", "rec@arifos.local")
    _git(str(repo), "config", "user.name", "reconcile test")
    (repo / "main_only.txt").write_text("main-only content\n")
    _git(str(repo), "add", "main_only.txt")
    _git(str(repo), "commit", "-q", "-m", "init main")
    # create feature branch with mutation
    _git(str(repo), "checkout", "-q", "-b", "feature")
    for i, fn in enumerate(fence_files):
        (repo / fn).write_text(f"feature content {i}\n")
    _git(str(repo), "add", ".")
    _git(str(repo), "commit", "-q", "-m", "feature mutation")
    _git(str(repo), "checkout", "-q", "main")
    return str(repo)


def _lease(scope):
    req = engine.request(actor_id="reconcile-test", scope=scope, ttl_seconds=300)
    return engine.activate(req, judge_verdict="SEAL")


def test_reconcile_happy_path(tmp_path: Path):
    repo = _setup(tmp_path, ["feature_a.txt", "feature_b.txt"])
    lease = _lease({"connector": "git", "verbs": ["reconcile"]})
    fence = json.dumps({"max_diff_bytes": 100000, "banned_paths": ["/etc/shadow"]})
    r = subprocess.run(
        [sys.executable, RECONCILE, "--repo", repo, "--source", "feature", "--target", "main", "--lease", lease["lease_id"], "--actor", "reconcile-test", "--fence", fence],
        capture_output=True, text=True,
    )
    out = json.loads(r.stdout)
    assert out["final_ok"] is True, f"reconcile failed: {out}"
    stage_names = [s["stage"] for s in out["stages"]]
    assert stage_names == ["01_diff", "02_validation", "03_policy", "04_drift_guard", "05_reconcile", "06_receipt", "07_witness"], stage_names
    assert (Path(repo) / "feature_a.txt").exists()
    assert (Path(repo) / "feature_b.txt").exists()
    engine.revoke(lease["lease_id"])


def test_reconcile_blocks_on_lease_revoked(tmp_path: Path):
    repo = _setup(tmp_path, ["x.txt"])
    lease = _lease({"connector": "git", "verbs": ["reconcile"]})
    engine.revoke(lease["lease_id"])  # revoke FIRST
    r = subprocess.run(
        [sys.executable, RECONCILE, "--repo", repo, "--source", "feature", "--target", "main", "--lease", lease["lease_id"], "--actor", "reconcile-test", "--fence", "{}"],
        capture_output=True, text=True,
    )
    out = json.loads(r.stdout)
    assert out["final_ok"] is False
    assert out["halted_at"] == "02_validation"


def test_reconcile_blocks_on_banned_path(tmp_path: Path):
    repo = _setup(tmp_path, ["feature_ok.txt"])
    # inject a forbidden filename into feature branch
    _git(repo, "checkout", "-q", "feature")
    (Path(repo) / "evil.txt").write_text("evil\n")
    _git(repo, "add", "evil.txt")
    _git(repo, "commit", "-q", "-m", "evil drop")
    _git(repo, "checkout", "-q", "main")
    lease = _lease({"connector": "git", "verbs": ["reconcile"]})
    fence = json.dumps({"banned_paths": ["evil.txt"], "max_diff_bytes": 100000})
    r = subprocess.run(
        [sys.executable, RECONCILE, "--repo", repo, "--source", "feature", "--target", "main", "--lease", lease["lease_id"], "--actor", "reconcile-test", "--fence", fence],
        capture_output=True, text=True,
    )
    out = json.loads(r.stdout)
    assert out["final_ok"] is False
    assert out["halted_at"] == "03_policy"
    engine.revoke(lease["lease_id"])


def test_reconcile_blocks_on_max_diff_size(tmp_path: Path):
    repo = _setup(tmp_path, ["big.txt"])
    # inflate the file
    _git(repo, "checkout", "-q", "feature")
    (Path(repo) / "big.txt").write_text("x" * 10000)
    _git(repo, "add", "big.txt")
    _git(repo, "commit", "-q", "--amend", "--no-edit")
    _git(repo, "checkout", "-q", "main")
    lease = _lease({"connector": "git", "verbs": ["reconcile"]})
    fence = json.dumps({"max_diff_bytes": 1000})
    r = subprocess.run(
        [sys.executable, RECONCILE, "--repo", repo, "--source", "feature", "--target", "main", "--lease", lease["lease_id"], "--actor", "reconcile-test", "--fence", fence],
        capture_output=True, text=True,
    )
    out = json.loads(r.stdout)
    assert out["final_ok"] is False
    assert out["halted_at"] == "03_policy"
    engine.revoke(lease["lease_id"])
