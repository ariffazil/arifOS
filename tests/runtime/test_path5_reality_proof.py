"""
Path-5 Reality Conversion — Proof that Lease → Worktree → Mutation → Validation →
Reconciliation → Receipt is a REAL pipeline, not a design.

This test converts RATIFIED_DESIGN into SEAL_CAPABILITY by demonstrating the
full pipeline executes with two concurrent agents on a real git repo.

Success criteria (from ARIFOS::REALITY_LANDING_EXECUTION::v1):
  - Lease A + Lease B issued concurrently
  - Worktree A + Worktree B isolated
  - Mutation A + Mutation B in separate branches
  - Validation A + Validation B pass
  - Reconciliation merges both into main without contradiction
  - Receipts emitted with full provenance
  - Test runs in CI automatically (pytest)

If this test fails, Path-5 is not a capability — it is a belief.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

# Make lease_engine importable
sys.path.insert(0, "/root/A-FORGE/leases")
from lease_engine import engine  # noqa: E402

RECEIPT_DIR = Path("/root/.local/share/arifos/vault999/REALITY_LANDING/path5")


def _git(cwd: str, *args: str, check: bool = True) -> str:
    """Run a git command, return stdout."""
    r = subprocess.run(
        ["git", "-C", cwd, *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and r.returncode != 0:
        raise RuntimeError(f"git {args} failed in {cwd}: {r.stderr}")
    return r.stdout.strip()


def _make_test_repo(tmp: Path) -> str:
    """Create a fresh git repo with one initial commit on main."""
    repo = tmp / "path5_proof_repo"
    repo.mkdir()
    _git(str(repo), "init", "-q", "-b", "main")
    _git(str(repo), "config", "user.email", "path5-proof@arifos.local")
    _git(str(repo), "config", "user.name", "Path-5 Reality Proof")
    (repo / "README.md").write_text("# Path-5 Proof Repo\n\nWitness of pipeline shape.\n")
    _git(str(repo), "add", "README.md")
    _git(str(repo), "commit", "-q", "-m", "chore: initial commit (main)")
    return str(repo)


def _make_branch_worktree(repo: str, worktree_dir: Path, branch: str) -> str:
    """Create a worktree at worktree_dir on new branch, return path."""
    wt_path = str(worktree_dir)
    _git(repo, "worktree", "add", "-b", branch, wt_path)
    return wt_path


def _emit_receipt(stage: str, payload: dict) -> Path:
    """Emit a Path-5 stage receipt to REALITY_LANDING/path5/."""
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    f = RECEIPT_DIR / f"{ts}_{stage}.json"
    f.write_text(
        json.dumps(
            {
                "stage": stage,
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                **payload,
            },
            indent=2,
            default=str,
        )
    )
    return f


# ─────────────────────────────────────────────────────────────────────────────
# THE PROOF
# ─────────────────────────────────────────────────────────────────────────────


def test_path5_full_pipeline_two_concurrent_agents(tmp_path: Path):
    """
    Path-5: 6 stages, 2 agents, concurrent.

    Agent A and Agent B both:
      1. Request + activate a lease (concurrent threads)
      2. Receive a worktree on their own branch
      3. Mutate DIFFERENT files (no merge conflict)
      4. Validate via lease_engine.validate()
      5. Emit receipt at each stage

    After both finish, reconciliation merges both branches into main.
    Final assertion: both mutations visible on main, no contradiction.
    """

    repo = _make_test_repo(tmp_path)

    # ── Stage 1: LEASE — two concurrent lease issuances ──────────────────
    lease_a_box: dict = {}
    lease_b_box: dict = {}

    def request_lease(actor: str, scope: dict, box: dict):
        req = engine.request(actor_id=actor, scope=scope, ttl_seconds=300)
        active = engine.activate(req, judge_verdict="SEAL")
        box["lease"] = active
        engine.receipt(
            active["lease_id"],
            "lease.activate",
            {"actor": actor, "scope": scope, "status": "ACTIVE"},
        )

    t_a = threading.Thread(
        target=request_lease,
        args=("agent-a-path5", {"connector": "git", "verbs": ["mutate", "validate"]}, lease_a_box),
    )
    t_b = threading.Thread(
        target=request_lease,
        args=("agent-b-path5", {"connector": "git", "verbs": ["mutate", "validate"]}, lease_b_box),
    )
    t_a.start()
    t_b.start()
    t_a.join()
    t_b.join()

    lease_a = lease_a_box["lease"]
    lease_b = lease_b_box["lease"]

    assert lease_a["status"] == "ACTIVE", f"lease_a not active: {lease_a}"
    assert lease_b["status"] == "ACTIVE", f"lease_b not active: {lease_b}"
    assert lease_a["lease_id"] != lease_b["lease_id"], "leases must have distinct IDs"
    _emit_receipt(
        "01_lease_issued",
        {
            "lease_a_id": lease_a["lease_id"],
            "lease_b_id": lease_b["lease_id"],
            "actor_a": lease_a["actor_id"],
            "actor_b": lease_b["actor_id"],
            "concurrent_threads": True,
            "verdict": "RATIFIED_DESIGN → PARTIAL",
        },
    )

    # ── Stage 2: WORKTREE — isolated mutation surfaces ─────────────────────
    wt_a_dir = tmp_path / "wt_agent_a"
    wt_b_dir = tmp_path / "wt_agent_b"
    wt_a = _make_branch_worktree(repo, wt_a_dir, "agent-a-mutation")
    wt_b = _make_branch_worktree(repo, wt_b_dir, "agent-b-mutation")

    assert Path(wt_a, "README.md").exists()
    assert Path(wt_b, "README.md").exists()
    assert _git(repo, "worktree", "list").count("agent-") == 2
    _emit_receipt(
        "02_worktree_created",
        {
            "worktree_a": wt_a,
            "branch_a": "agent-a-mutation",
            "worktree_b": wt_b,
            "branch_b": "agent-b-mutation",
            "isolation": "verified (separate dirs, separate branches)",
            "verdict": "PARTIAL → WITNESSED",
        },
    )

    # ── Stage 3: MUTATION — each agent writes to DIFFERENT file ───────────
    file_a = Path(wt_a) / "evidence_a.json"
    file_b = Path(wt_b) / "evidence_b.json"
    payload_a = {
        "agent": "A",
        "lease_id": lease_a["lease_id"],
        "mutation_kind": "evidence_drop",
        "value": 42,
    }
    payload_b = {
        "agent": "B",
        "lease_id": lease_b["lease_id"],
        "mutation_kind": "evidence_drop",
        "value": 99,
    }
    file_a.write_text(json.dumps(payload_a, indent=2))
    file_b.write_text(json.dumps(payload_b, indent=2))

    _git(wt_a, "add", "evidence_a.json")
    _git(wt_a, "commit", "-q", "-m", f"feat(a): drop evidence via {lease_a['lease_id']}")
    _git(wt_b, "add", "evidence_b.json")
    _git(wt_b, "commit", "-q", "-m", f"feat(b): drop evidence via {lease_b['lease_id']}")

    engine.receipt(
        lease_a["lease_id"], "git.mutate", {"file": "evidence_a.json", "branch": "agent-a-mutation"}
    )
    engine.receipt(
        lease_b["lease_id"], "git.mutate", {"file": "evidence_b.json", "branch": "agent-b-mutation"}
    )
    _emit_receipt(
        "03_mutated",
        {
            "agent_a_file": "evidence_a.json",
            "agent_a_branch": "agent-a-mutation",
            "agent_b_file": "evidence_b.json",
            "agent_b_branch": "agent-b-mutation",
            "no_merge_conflict_design": "different files on different branches",
            "verdict": "WITNESSED",
        },
    )

    # ── Stage 4: VALIDATION — both leases validate before reconcile ───────
    valid_a = engine.validate(lease_a["lease_id"], {"connector": "git", "verbs": ["mutate"]})
    valid_b = engine.validate(lease_b["lease_id"], {"connector": "git", "verbs": ["mutate"]})
    assert valid_a["valid"] is True, f"lease_a failed validation: {valid_a}"
    assert valid_b["valid"] is True, f"lease_b failed validation: {valid_b}"
    engine.receipt(lease_a["lease_id"], "lease.validate", valid_a)
    engine.receipt(lease_b["lease_id"], "lease.validate", valid_b)
    _emit_receipt(
        "04_validated",
        {
            "lease_a_valid": valid_a["valid"],
            "lease_b_valid": valid_b["valid"],
            "scope_connector": "git",
            "scope_verbs": ["mutate"],
            "verdict": "WITNESSED",
        },
    )

    # ── Stage 5: RECONCILIATION — merge both branches into main ────────────
    _git(
        repo,
        "merge",
        "--no-ff",
        "agent-a-mutation",
        "-m",
        f"reconcile: agent A via {lease_a['lease_id']}",
    )
    _git(
        repo,
        "merge",
        "--no-ff",
        "agent-b-mutation",
        "-m",
        f"reconcile: agent B via {lease_b['lease_id']}",
    )

    main_log_stat = _git(repo, "log", "--stat", "-n", "10")
    assert "evidence_a.json" in main_log_stat, "agent A evidence missing from main"
    assert "evidence_b.json" in main_log_stat, "agent B evidence missing from main"

    # Verify the actual content is on main (file existence + provenance round-trip)
    assert Path(repo, "evidence_a.json").exists(), "evidence_a.json not on main"
    assert Path(repo, "evidence_b.json").exists(), "evidence_b.json not on main"
    assert json.loads(Path(repo, "evidence_a.json").read_text())["lease_id"] == lease_a["lease_id"]
    assert json.loads(Path(repo, "evidence_b.json").read_text())["lease_id"] == lease_b["lease_id"]
    _emit_receipt(
        "05_reconciled",
        {
            "main_branch_commits_observed": len(main_log_stat.split("commit ")) - 1,
            "agent_a_evidence_on_main": True,
            "agent_b_evidence_on_main": True,
            "merge_strategy": "no-ff (preserve topology)",
            "verdict": "WITNESSED → SEAL_CAPABILITY",
        },
    )

    # ── Stage 6: RECEIPT — all lease receipts + path5 receipts witnessed ──
    receipts_log = Path("/root/A-FORGE/leases/receipts.jsonl")
    assert receipts_log.exists(), "receipts.jsonl must exist"
    receipts_lines = receipts_log.read_text().strip().split("\n")
    # The 4 receipts we wrote (lease.activate x2 + git.mutate x2 + lease.validate x2 = 6)
    our_receipts = [
        r for r in receipts_lines if lease_a["lease_id"] in r or lease_b["lease_id"] in r
    ]
    assert len(our_receipts) >= 6, (
        f"expected ≥6 receipts for both leases, found {len(our_receipts)}"
    )
    _emit_receipt(
        "06_receipted",
        {
            "receipts_log": str(receipts_log),
            "receipts_for_our_leases": len(our_receipts),
            "lease_a_id": lease_a["lease_id"],
            "lease_b_id": lease_b["lease_id"],
            "verdict": "SEAL_CAPABILITY → SEAL_OPERATIONAL",
        },
    )

    # ── CLEANUP: revoke both leases + remove worktrees ───────────────────
    engine.revoke(lease_a["lease_id"])
    engine.revoke(lease_b["lease_id"])
    _git(repo, "worktree", "remove", wt_a, "--force")
    _git(repo, "worktree", "remove", wt_b, "--force")

    _emit_receipt(
        "07_cleanup",
        {
            "lease_a_revoked": True,
            "lease_b_revoked": True,
            "worktrees_removed": True,
            "verdict": "Pipeline closed. No state leak.",
        },
    )


def test_path5_lease_revocation_blocks_midflight(tmp_path: Path):
    """Lease revocation must actually block — not just record intent."""
    req = engine.request(
        actor_id="agent-x-revoke", scope={"connector": "git", "verbs": ["mutate"]}, ttl_seconds=600
    )
    lease = engine.activate(req, judge_verdict="SEAL")
    assert lease["status"] == "ACTIVE"

    pre = engine.validate(lease["lease_id"], {"connector": "git", "verbs": ["mutate"]})
    assert pre["valid"] is True

    engine.revoke(lease["lease_id"])

    post = engine.validate(lease["lease_id"], {"connector": "git", "verbs": ["mutate"]})
    assert post["valid"] is False
    assert post["reason"] == "LEASE_REVOKED"
    _emit_receipt(
        "08_revocation_proof",
        {
            "lease_id": lease["lease_id"],
            "pre_revoke_valid": pre["valid"],
            "post_revoke_valid": post["valid"],
            "post_revoke_reason": post["reason"],
            "verdict": "Lease is a real capability boundary, not a marker.",
        },
    )


def test_path5_lease_expiry_blocks_midflight(tmp_path: Path):
    """Expired leases must refuse to validate — TTL is real, not advisory."""
    req = engine.request(
        actor_id="agent-y-expire", scope={"connector": "git", "verbs": ["mutate"]}, ttl_seconds=1
    )
    lease = engine.activate(req, judge_verdict="SEAL")
    pre = engine.validate(lease["lease_id"], {"connector": "git", "verbs": ["mutate"]})
    assert pre["valid"] is True
    time.sleep(1.5)
    post = engine.validate(lease["lease_id"], {"connector": "git", "verbs": ["mutate"]})
    assert post["valid"] is False
    assert "EXPIRED" in post["reason"]
    _emit_receipt(
        "09_expiry_proof",
        {
            "lease_id": lease["lease_id"],
            "ttl_seconds": 1,
            "pre_expiry_valid": pre["valid"],
            "post_expiry_valid": post["valid"],
            "post_expiry_reason": post["reason"],
            "verdict": "TTL is enforced, not advisory.",
        },
    )


def test_path5_lease_scope_mismatch_blocks(tmp_path: Path):
    """A lease for one connector cannot validate verbs for another."""
    req = engine.request(
        actor_id="agent-z-scope", scope={"connector": "email", "verbs": ["send"]}, ttl_seconds=300
    )
    lease = engine.activate(req, judge_verdict="SEAL")
    wrong = engine.validate(lease["lease_id"], {"connector": "git", "verbs": ["mutate"]})
    assert wrong["valid"] is False
    assert wrong["reason"] == "SCOPE_CONNECTOR_MISMATCH"
    _emit_receipt(
        "10_scope_proof",
        {
            "lease_id": lease["lease_id"],
            "scope_granted": "email.send",
            "scope_requested": "git.mutate",
            "verdict": "Scope is enforced, not advisory.",
        },
    )
    engine.revoke(lease["lease_id"])


def test_path5_lease_judge_rejection_blocks():
    """A non-SEAL judge verdict must produce a REJECTED lease, not ACTIVE."""
    req = engine.request(
        actor_id="agent-j-rejected",
        scope={"connector": "git", "verbs": ["mutate"]},
        ttl_seconds=300,
    )
    rejected = engine.activate(req, judge_verdict="VOID")
    assert rejected["status"] == "REJECTED"
    v = engine.validate(rejected["lease_id"], {"connector": "git", "verbs": ["mutate"]})
    assert v["valid"] is False
    _emit_receipt(
        "11_judge_rejection_proof",
        {
            "lease_id": rejected["lease_id"],
            "judge_verdict": "VOID",
            "lease_status": rejected["status"],
            "verdict": "Judge verdict is enforced — lease cannot self-activate.",
        },
    )
