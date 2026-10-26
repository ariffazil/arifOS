"""Production writer mediation — inventory completeness + fail-closed artifact proof.

P0 (2026-10-26): the lease only serialised writers that called it. This suite
holds the repository-controlled writer surface to one contract:

  * every file the scan finds mutating the production runtime must appear in
    scripts/production_writers.json;
  * a writer marked mediated=True must reference the lease authority BEFORE its
    first mutation (mutate-then-check is not mediation);
  * a writer marked mediated=False must carry an explicit reason;
  * the artifact verifier must never manufacture equality from missing evidence.

SCOPE: tests/ is skipped — a fixture that contains the pattern as a string is not a
production writer (this file would otherwise match itself).

KNOWN LIMITATION (asserted here, not hidden): the scan matches literal paths and
unit names. Variable-indirected calls (systemctl restart $SERVICE_NAME) are not
matched — scripts/deploy-release.sh was found by reading, and is carried in the
inventory with discovery="manual". These tests bound the common forms; they do
not prove exhaustiveness.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INVENTORY = REPO / "scripts" / "production_writers.json"
LEASE_TOOL = REPO / "scripts" / "deploy_lease.py"
BODY = REPO / "scripts" / "deploy_local_body.sh"

SKIP_DIRS = {".venv", "build", "node_modules", ".git", "docs", "archive", "_retired", ".worktrees", "tests"}
PATTERNS = {
    "rsync_to_production": re.compile(r"\brsync\b[^\n]*/opt/arifos"),
    "cp_into_production": re.compile(r"\b(cp|install|mv)\b[^\n]*/opt/arifos/(app|current|venv)"),
    "systemctl_arifos": re.compile(r"systemctl[^\n]*\b(restart|reload|start|stop)\b[^\n]*\barifos"),
    "pip_into_production": re.compile(r"pip3?[^\n]*install[^\n]*/opt/arifos"),
}


def _scan() -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for p in REPO.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(REPO).parts):
            continue
        if p.suffix not in {".sh", ".py", ".yml", ".yaml", ".mk"} and p.name != "Makefile":
            continue
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        found = sorted({k for k, rx in PATTERNS.items() if rx.search(text)})
        if found:
            hits[str(p.relative_to(REPO))] = found
    return hits


def _inventory() -> dict:
    return json.loads(INVENTORY.read_text())


def test_inventory_exists_and_is_well_formed() -> None:
    inv = _inventory()
    assert inv["schema"] == "production-writers/v1"
    assert inv["authority"]["primitive"] == "scripts/deploy_lease.py"
    ids = [w["writer_id"] for w in inv["writers"]]
    assert len(ids) == len(set(ids)), "duplicate writer_id in inventory"
    for w in inv["writers"]:
        assert {"file", "writer_id", "mediation", "mediated", "discovery"} <= set(w), w
        if not w["mediated"]:
            assert w.get("reason"), f"{w['writer_id']} claims non-mediated with no reason"
            assert w.get("classification") in {"OPEN", "NOT_A_WRITER"}, w["writer_id"]


def test_every_scanned_writer_is_in_the_inventory() -> None:
    """A new production writer that skips the inventory fails this test."""
    listed = {w["file"] for w in _inventory()["writers"]}
    missing = {f: k for f, k in _scan().items() if f not in listed}
    assert not missing, (
        "unlisted production writers found — add them to scripts/production_writers.json "
        f"with a mediation or an explicit OPEN reason: {missing}"
    )


def test_mediated_writers_hold_the_lease_before_they_mutate() -> None:
    """Mutate-then-check is not mediation: the lease token must come first."""
    problems: list[str] = []
    for w in _inventory()["writers"]:
        if not w["mediated"]:
            continue
        path = REPO / w["file"]
        if not path.exists():
            problems.append(f"{w['file']}: mediated but missing")
            continue
        text = path.read_text(errors="replace")
        lease_at = text.find("deploy_lease.py")
        if lease_at == -1:
            problems.append(f"{w['file']}: marked mediated but never references the lease")
            continue
        muts = [m.start() for m in (rx.search(text) for rx in PATTERNS.values()) if m]
        if muts and lease_at > min(muts):
            problems.append(f"{w['file']}: lease reference appears AFTER the first mutation")
    assert not problems, "; ".join(problems)


def _run_lease(
    state_dir: Path, *args: str, env_extra: dict | None = None
) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["ARIFOS_STATE_DIRECTORY"] = str(state_dir)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(LEASE_TOOL), *args], capture_output=True, text=True, env=env
    )


def test_verify_returns_unobservable_when_the_runtime_cannot_be_read(tmp_path: Path) -> None:
    """Missing evidence may not manufacture equality (the original fail-open)."""
    blind = {"ARIFOS_ACTIVE_VENV_ROOT": str(tmp_path / "no-such-venv")}
    acq = _run_lease(
        tmp_path, "acquire", "--actor", "a", "--base", "b", "--candidate", "c", env_extra=blind
    )
    assert acq.returncode == 0, acq.stderr
    rel = _run_lease(tmp_path, "release", "--actor", "a", env_extra=blind)
    assert rel.returncode == 0, rel.stderr

    out = _run_lease(tmp_path, "verify", env_extra=blind)
    assert out.returncode == 7, f"expected UNOBSERVABLE(7), got {out.returncode}"
    payload = json.loads(out.stdout)
    assert payload["status"] == "ARTIFACT_UNOBSERVABLE"
    assert payload["observed"]["observable"] is False
    assert "site_packages_absent" in payload["reason"]


def test_body_refuses_to_mutate_without_a_lease(tmp_path: Path) -> None:
    env = dict(os.environ)
    env.update(
        {
            "ARIFOS_STATE_DIRECTORY": str(tmp_path),
            "DEPLOY_DRY_RUN": "1",
            "PYTHON": sys.executable,
            "DIR": str(REPO),
            "GIT_SHA": "deadbeef",
        }
    )
    run = subprocess.run(["bash", str(BODY)], capture_output=True, text=True, env=env)
    assert run.returncode == 6, f"expected NO_ACTIVE_LEASE(6), got {run.returncode}"
    assert not (tmp_path / "deploy_epochs.jsonl").exists()


def test_canonical_body_with_an_owned_lease_runs_and_releases(tmp_path: Path) -> None:
    acq = _run_lease(tmp_path, "acquire", "--actor", "agent-a", "--base", "b1", "--candidate", "c1")
    assert acq.returncode == 0
    env = dict(os.environ)
    env.update(
        {
            "ARIFOS_STATE_DIRECTORY": str(tmp_path),
            "DEPLOY_DRY_RUN": "1",
            "CONFORMANCE_CMD": "true",
            "DEPLOY_ACTOR": "agent-a",
            "PYTHON": sys.executable,
            "DIR": str(REPO),
            "GIT_SHA": "deadbeef",
        }
    )
    run = subprocess.run(["bash", str(BODY)], capture_output=True, text=True, env=env)
    assert run.returncode == 0, run.stdout + run.stderr
    assert not (tmp_path / "deploy_lease.json").exists(), "lease not released on success"
    rows = [
        json.loads(line)
        for line in (tmp_path / "deploy_epochs.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert [r["event"] for r in rows] == ["RELEASED"]
