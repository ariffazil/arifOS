#!/usr/bin/env python3
"""Deploy lease — ONE production mutation at a time, bound to ONE candidate.

WHY THIS EXISTS (measured failure classes, 2026-10-26)
------------------------------------------------------
1. Three runtime code states in 21 minutes on one host:
       03:20Z  bb756d958   pre-fix behaviour
       03:34Z  8359618fe   fix deployed, effect-verified
       03:41Z  cd28e52cf   another session deployed; the fix silently regressed
2. Epoch 2 proved the deeper defect: the lease authorized candidate 50dff242,
   but the body re-read HEAD and deployed 48a9d877. The lock was serialized; the
   artifact was not bound.
3. A release without --actor cleared the holder's live lease because the owner
   check was `if a.actor and ...`.

The lease now carries four things that must all agree before release:
    actor + session + lease_id + opaque holder token (only the token hash is stored).

The token is written once to a 0600 authorization envelope. It is never placed
in argv, never printed by acquire, and never written to the epoch ledger. The
body reads it from the envelope and proves sha256(token) == lease.holder_token_sha256
before the first protected write.

Candidate binding is a first-class invariant:
    ACQUIRE pins candidate_commit
      -> body receives LEASE_CANDIDATE from the live lease
      -> body asserts HEAD == LEASE_CANDIDATE before any write
      -> marker and release stamp are written FROM LEASE_CANDIDATE
      -> release records candidate_commit and deployed_commit separately
      -> release refuses to call the epoch verified when they differ
      -> verify-epoch re-checks candidate == marker == manifest before PASS

Rate governance: a governed release (entry_point=make:deploy-local,
rate_gate_version=1) without a PASS verdict blocks the next acquire. Historical
epochs and non-governed probes are never treated as production deployments.

USAGE
    deploy_lease.py acquire --actor A --session S --base B --candidate C \
        --entry-point make:deploy-local --deployment-id D
    deploy_lease.py check-envelope --envelope P --actor A --session S
    deploy_lease.py verify-baseline
    deploy_lease.py verify-candidate --envelope P --actor A --session S
    deploy_lease.py release --envelope P --actor A --session S --receipt R
    deploy_lease.py verify-epoch --lease-id L --verdict PASS --evidence R \
        --actor A --session S
    deploy_lease.py status [--json]
    deploy_lease.py verify

EXIT CODES
    0  ok
    3  HOLD_CONCURRENT_DEPLOY / HOLD_NOT_OWNER
    4  ARTIFACT_CHANGED / HOLD_ARTIFACT_DRIFT
    5  NO_ACTIVE_LEASE / NO_BASELINE / UNKNOWN_EPOCH
    6  HOLD_UNVERIFIED_DEPLOY
    7  ARTIFACT_UNOBSERVABLE / HOLD_UNAPPROVED_ENTRY_POINT
    8  HOLD_DIRTY_SOURCE (body)
    9  HOLD_CANDIDATE_CHANGED (body)
    11 HOLD_CANDIDATE_MISMATCH (release)
    12 HOLD_VERDICT_FAILED (verify-epoch)
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import hmac
import json
import os
import secrets
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATE_DIR = Path(os.environ.get("ARIFOS_STATE_DIRECTORY", "/var/lib/arifos"))
LEASE_PATH = STATE_DIR / "deploy_lease.json"
LEDGER_PATH = STATE_DIR / "deploy_epochs.jsonl"
LOCK_PATH = STATE_DIR / "deploy.lock"
ENVELOPE_PATH = STATE_DIR / "deploy_envelope.json"

APP_DIR = Path(os.environ.get("ARIFOS_APP_DIR", "/opt/arifos/app"))
VENV_ROOT = Path(os.environ.get("ARIFOS_ACTIVE_VENV_ROOT", "/opt/arifos/current/venv"))
SITE_PKGS = Path(
    os.environ.get(
        "ARIFOS_RUNTIME_TARGET",
        str(VENV_ROOT / "lib" / "python3.13" / "site-packages" / "arifosmcp"),
    )
)
RUNTIME_TARGET = str(SITE_PKGS)

RATE_GATE_VERSION = 1
CANONICAL_ENTRY_POINT = "make:deploy-local"


# ── helpers ────────────────────────────────────────────────────────────────
def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).isoformat(timespec="seconds").replace("+00:00", "Z")


def _sha_file(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return "MISSING"


def _token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _same(x: object, y: object) -> bool:
    return hmac.compare_digest(str(x or ""), str(y or ""))


def artifact_manifest() -> dict:
    """Hash the code actually imported by the running kernel (not the git tree)."""
    files: list[str] = []
    h = hashlib.sha256()
    if SITE_PKGS.is_dir():
        for p in sorted(SITE_PKGS.rglob("*.py")):
            rel = str(p.relative_to(SITE_PKGS))
            digest = _sha_file(p)
            files.append(f"{rel}:{digest}")
            h.update(f"{rel}\0{digest}\0".encode())
    observable = bool(files)
    reason = None
    if not SITE_PKGS.is_dir():
        reason = f"site_packages_absent:{SITE_PKGS}"
    elif not files:
        reason = f"no_python_modules_under:{SITE_PKGS}"
    return {
        "observable": observable,
        "unobservable_reason": reason,
        "manifest_sha256": h.hexdigest() if files else "EMPTY",
        "module_count": len(files),
        "target_runtime": RUNTIME_TARGET,
        "app_git_commit": (APP_DIR / ".git_commit").read_text().strip()
        if (APP_DIR / ".git_commit").exists()
        else None,
    }


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (ValueError, OSError):
        return None


def _read_lease() -> dict | None:
    return _read_json(LEASE_PATH)


def _is_live(lease: dict | None) -> bool:
    if not lease:
        return False
    try:
        expires = datetime.fromisoformat(str(lease["expires_at"]).replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return False
    return _now() < expires


def _atomic_write(path: Path, text: str, mode: int = 0o600) -> None:
    """Write a secret-bearing file atomically with no group/other permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    try:
        os.write(fd, text.encode())
        os.fchmod(fd, mode)
    finally:
        os.close(fd)
    os.replace(tmp, path)
    os.chmod(path, mode)


def _write_lease(lease: dict | None) -> None:
    if lease is None:
        LEASE_PATH.unlink(missing_ok=True)
    else:
        _atomic_write(LEASE_PATH, json.dumps(lease, indent=2), 0o600)


def _read_envelope(path: Path) -> dict:
    st = path.stat()
    if st.st_mode & 0o077:
        raise ValueError(f"envelope_permissions_too_open:{oct(st.st_mode & 0o777)}")
    if st.st_uid not in (0, os.geteuid()):
        raise ValueError(f"envelope_owner_mismatch:{st.st_uid}")
    data = _read_json(path)
    if not isinstance(data, dict):
        raise ValueError("envelope_unreadable")
    return data


def _write_envelope(envelope: dict) -> None:
    _atomic_write(ENVELOPE_PATH, json.dumps(envelope, indent=2), 0o600)


def _append_ledger(entry: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")


def _ledger_rows() -> list[dict]:
    if not LEDGER_PATH.exists():
        return []
    rows: list[dict] = []
    for line in LEDGER_PATH.open():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def _next_epoch() -> int:
    epochs = [
        int(r.get("deployment_epoch", 0))
        for r in _ledger_rows()
        if isinstance(r.get("deployment_epoch"), int)
    ]
    return max(epochs, default=0) + 1


def _governed_release() -> dict | None:
    """Newest release that claims the governed entry point and rate-gate version."""
    for row in reversed(_ledger_rows()):
        if (
            row.get("event") == "RELEASED"
            and row.get("entry_point") == CANONICAL_ENTRY_POINT
            and row.get("rate_gate_version") == RATE_GATE_VERSION
        ):
            return row
    return None


def _verdict_for(lease_id: str) -> dict | None:
    for row in reversed(_ledger_rows()):
        if row.get("event") == "VERDICT" and row.get("lease_id") == lease_id:
            return row
    return None


def _resolution_for(lease_id: str) -> dict | None:
    """F13 recovery lane: a failed epoch is resolved by explicit sovereign receipt."""
    for row in reversed(_ledger_rows()):
        if row.get("event") == "RESOLVED" and row.get("lease_id") == lease_id:
            return row
    return None


class _Lock:
    """flock around read-modify-write so two acquires cannot both win."""

    def __enter__(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.fh = LOCK_PATH.open("a+")
        fcntl.flock(self.fh, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()
        return False


def _validate_envelope(
    envelope_path: str, actor: str, session: str
) -> tuple[dict | None, dict | None, int]:
    """Prove the caller owns the live lease. Returns (lease, envelope, rc)."""
    lease = _read_lease()
    if not _is_live(lease):
        return None, None, 5
    assert lease is not None
    try:
        envelope = _read_envelope(Path(envelope_path))
    except (OSError, ValueError) as exc:
        return None, None, 7 if isinstance(exc, ValueError) else 5

    mismatched: list[str] = []
    if not _same(actor, lease.get("actor")):
        mismatched.append("actor")
    if not _same(session, lease.get("session")):
        mismatched.append("session")
    if not _same(envelope.get("actor"), lease.get("actor")):
        mismatched.append("envelope_actor")
    if not _same(envelope.get("session"), lease.get("session")):
        mismatched.append("envelope_session")
    if not _same(envelope.get("lease_id"), lease.get("lease_id")):
        mismatched.append("lease_id")
    if not _same(envelope.get("envelope_id"), lease.get("envelope_id")):
        mismatched.append("envelope_id")
    if not _same(envelope.get("candidate_commit"), lease.get("candidate_commit")):
        mismatched.append("candidate_commit")
    if not _same(envelope.get("entry_point"), lease.get("entry_point")):
        mismatched.append("entry_point")

    stored = str(lease.get("holder_token_sha256") or "")
    presented = _token_digest(str(envelope.get("holder_token") or ""))
    if not stored or not hmac.compare_digest(presented, stored):
        mismatched.append("token")

    if mismatched:
        return None, {"mismatched": mismatched}, 3
    return lease, envelope, 0


# ── commands ───────────────────────────────────────────────────────────────
def cmd_acquire(a) -> int:
    with _Lock():
        current = _read_lease()
        if _is_live(current):
            print(
                json.dumps(
                    {
                        "status": "HOLD_CONCURRENT_DEPLOY",
                        "holder": current,
                        "message": (
                            "another deployment owns production. Nothing was written. "
                            "Wait for release or expiry, or coordinate with the holder."
                        ),
                    },
                    indent=2,
                )
            )
            return 3
        if current:  # expired: retire it loudly rather than silently overwrite
            _append_ledger(
                {
                    "event": "LEASE_EXPIRED_UNRELEASED",
                    "lease_id": current.get("lease_id"),
                    "actor": current.get("actor"),
                    "expires_at": current.get("expires_at"),
                    "observed_at": _iso(),
                }
            )

        # Rate governance: the last GOVERNED release must carry a PASS verdict.
        # Historical epochs (no rate_gate_version) and non-governed probes are
        # evidence, but they are not production deployments.
        last = _governed_release()
        if last is not None:
            verdict = _verdict_for(str(last.get("lease_id") or ""))
            resolved = _resolution_for(str(last.get("lease_id") or ""))
            if (
                verdict is None or str(verdict.get("verdict") or "").upper() != "PASS"
            ) and resolved is None:
                print(
                    json.dumps(
                        {
                            "status": "HOLD_UNVERIFIED_DEPLOY",
                            "unverified_epoch": last.get("deployment_epoch"),
                            "lease_id": last.get("lease_id"),
                            "released_at": last.get("released_at"),
                            "verdict": verdict,
                            "message": (
                                "ONE_UNVERIFIED_PRODUCTION_DEPLOYMENT_MAXIMUM: the last "
                                "governed release has no PASS verdict. Run verify-epoch, "
                                "or resolve the failed epoch through F13. Nothing was written."
                            ),
                        },
                        indent=2,
                    )
                )
                return 6

        epoch = _next_epoch()
        lease_id = f"dl-{uuid.uuid4().hex[:12]}"
        envelope_id = uuid.uuid4().hex
        deployment_id = a.deployment_id or f"dep-{uuid.uuid4().hex[:12]}"
        holder_token = secrets.token_urlsafe(32)
        lease = {
            "lease_id": lease_id,
            "event": "ACQUIRED",
            "actor": a.actor,
            "session": a.session,
            "base_commit": a.base,
            "candidate_commit": a.candidate,
            "deployment_id": deployment_id,
            "entry_point": a.entry_point,
            "rate_gate_version": RATE_GATE_VERSION,
            "envelope_id": envelope_id,
            "target_runtime": RUNTIME_TARGET,
            "acquired_at": _iso(),
            "expires_at": _iso(_now() + timedelta(seconds=int(a.ttl))),
            "deployment_epoch": epoch,
            "previous_artifact": artifact_manifest(),
            "resulting_artifact": None,
            "receipt": None,
            "holder_token_sha256": _token_digest(holder_token),
            "holder_capability": "opaque token presented once at acquire; only sha256 stored",
        }
        envelope = {
            "envelope_id": envelope_id,
            "lease_id": lease_id,
            "actor": a.actor,
            "session": a.session,
            "candidate_commit": a.candidate,
            "base_commit": a.base,
            "entry_point": a.entry_point,
            "deployment_id": deployment_id,
            "issued_at": _iso(),
            "holder_token": holder_token,
        }
        try:
            _write_lease(lease)
            _write_envelope(envelope)
        except OSError:
            LEASE_PATH.unlink(missing_ok=True)
            raise
        public = {k: v for k, v in lease.items() if k != "holder_token_sha256"}
        print(
            json.dumps(
                {
                    "status": "LEASED",
                    "lease": public,
                    "envelope": {
                        "path": str(ENVELOPE_PATH),
                        "envelope_id": envelope_id,
                        "mode": "0600",
                    },
                },
                indent=2,
            )
        )
        return 0


def cmd_check_envelope(a) -> int:
    lease, envelope, rc = _validate_envelope(a.envelope, a.actor, a.session)
    if rc:
        status = {
            3: "HOLD_NOT_OWNER",
            5: "NO_ACTIVE_LEASE",
            7: "HOLD_UNAPPROVED_ENTRY_POINT",
        }[rc]
        print(json.dumps({"status": status, **(envelope or {})}, indent=2))
        return rc
    assert lease is not None
    if lease.get("entry_point") != CANONICAL_ENTRY_POINT:
        print(
            json.dumps(
                {
                    "status": "HOLD_UNAPPROVED_ENTRY_POINT",
                    "entry_point": lease.get("entry_point"),
                    "message": "the body is reachable only through make:deploy-local",
                },
                indent=2,
            )
        )
        return 7
    print(
        json.dumps(
            {
                "status": "ENVELOPE_OK",
                "lease_id": lease["lease_id"],
                "candidate_commit": lease["candidate_commit"],
                "actor": lease["actor"],
                "session": lease["session"],
                "entry_point": lease["entry_point"],
            },
            indent=2,
        )
    )
    return 0


def cmd_release(a) -> int:
    with _Lock():
        lease, envelope, rc = _validate_envelope(a.envelope, a.actor, a.session)
        if rc or lease is None:
            status = {
                3: "HOLD_NOT_OWNER",
                5: "NO_ACTIVE_LEASE",
                7: "HOLD_UNAPPROVED_ENTRY_POINT",
            }[rc]
            print(json.dumps({"status": status, **(envelope or {})}, indent=2))
            return rc

        resulting = artifact_manifest()
        deployed = resulting.get("app_git_commit")
        candidate = lease.get("candidate_commit")
        observed_head = a.observed_head if a.observed_head is not None else deployed
        source_match = _same(observed_head, candidate) if a.observed_head is not None else True
        candidate_match = bool(candidate) and deployed == candidate and source_match

        row = dict(lease)
        row.pop("holder_token_sha256", None)
        row.pop("holder_capability", None)
        row["resulting_artifact"] = resulting
        row["deployed_commit"] = deployed
        row["observed_head"] = observed_head
        row["source_match"] = source_match
        row["candidate_match"] = candidate_match
        row["verification_status"] = (
            "CANDIDATE_BOUND"
            if candidate_match
            else ("SOURCE_MISMATCH" if not source_match else "CANDIDATE_MISMATCH")
        )
        row["receipt"] = a.receipt
        row["body_exit_code"] = a.exit_code
        row["rollback_snapshot"] = a.rollback_snapshot
        row["stale_pruned"] = a.stale_pruned
        row["released_at"] = _iso()
        row["event"] = "RELEASED"

        _append_ledger(row)
        _write_lease(None)
        try:
            Path(a.envelope).unlink()
        except OSError:
            pass

        if candidate_match:
            print(
                json.dumps(
                    {
                        "status": "RELEASED",
                        "epoch": row["deployment_epoch"],
                        "candidate_commit": candidate,
                        "deployed_commit": deployed,
                        "candidate_bound": True,
                        "artifact": resulting,
                    },
                    indent=2,
                )
            )
            return 0

        print(
            json.dumps(
                {
                    "status": "HOLD_CANDIDATE_MISMATCH",
                    "epoch": row["deployment_epoch"],
                    "candidate_commit": candidate,
                    "deployed_commit": deployed,
                    "observed_head": observed_head,
                    "source_match": source_match,
                    "candidate_bound": False,
                    "message": (
                        "the released artifact is not the authorized candidate; "
                        "the epoch is recorded as CANDIDATE_MISMATCH and the next "
                        "acquire remains blocked until F13 resolves it"
                    ),
                },
                indent=2,
            )
        )
        return 11


def cmd_verify_baseline(a) -> int:
    lease = _read_lease()
    if not _is_live(lease):
        print(json.dumps({"status": "NO_ACTIVE_LEASE"}, indent=2))
        return 5
    assert lease is not None
    previous = lease.get("previous_artifact") or {}
    observed = artifact_manifest()
    if not observed.get("observable") or not previous.get("observable"):
        print(
            json.dumps(
                {
                    "status": "ARTIFACT_UNOBSERVABLE",
                    "previous": previous,
                    "observed": observed,
                },
                indent=2,
            )
        )
        return 7
    same = (
        previous.get("manifest_sha256") == observed.get("manifest_sha256")
        and previous.get("module_count") == observed.get("module_count")
        and previous.get("app_git_commit") == observed.get("app_git_commit")
    )
    print(
        json.dumps(
            {
                "status": "BASELINE_OK" if same else "HOLD_ARTIFACT_DRIFT",
                "expected": {
                    "manifest_sha256": previous.get("manifest_sha256"),
                    "module_count": previous.get("module_count"),
                    "app_git_commit": previous.get("app_git_commit"),
                },
                "observed": {
                    "manifest_sha256": observed.get("manifest_sha256"),
                    "module_count": observed.get("module_count"),
                    "app_git_commit": observed.get("app_git_commit"),
                },
            },
            indent=2,
        )
    )
    return 0 if same else 4


def cmd_verify_candidate(a) -> int:
    lease, envelope, rc = _validate_envelope(a.envelope, a.actor, a.session)
    if rc or lease is None:
        status = {
            3: "HOLD_NOT_OWNER",
            5: "NO_ACTIVE_LEASE",
            7: "HOLD_UNAPPROVED_ENTRY_POINT",
        }[rc]
        print(json.dumps({"status": status, **(envelope or {})}, indent=2))
        return rc
    observed = artifact_manifest()
    if not observed.get("observable"):
        print(
            json.dumps(
                {
                    "status": "ARTIFACT_UNOBSERVABLE",
                    "reason": observed.get("unobservable_reason"),
                    "observed": observed,
                },
                indent=2,
            )
        )
        return 7
    candidate = lease.get("candidate_commit")
    same = observed.get("app_git_commit") == candidate
    print(
        json.dumps(
            {
                "status": "CANDIDATE_BOUND" if same else "HOLD_CANDIDATE_MISMATCH",
                "candidate_commit": candidate,
                "observed_commit": observed.get("app_git_commit"),
                "manifest_sha256": observed.get("manifest_sha256"),
            },
            indent=2,
        )
    )
    return 0 if same else 11


def cmd_verify_epoch(a) -> int:
    with _Lock():
        target = None
        for row in reversed(_ledger_rows()):
            if row.get("event") == "RELEASED" and row.get("lease_id") == a.lease_id:
                target = row
                break
        if target is None:
            print(json.dumps({"status": "UNKNOWN_EPOCH", "lease_id": a.lease_id}, indent=2))
            return 5
        if not _same(a.actor, target.get("actor")) or not _same(a.session, target.get("session")):
            print(
                json.dumps(
                    {
                        "status": "HOLD_NOT_OWNER",
                        "mismatched": [
                            x
                            for x in ("actor", "session")
                            if not _same(getattr(a, x), target.get(x))
                        ],
                    },
                    indent=2,
                )
            )
            return 3
        existing = _verdict_for(a.lease_id)
        if existing is not None:
            print(
                json.dumps(
                    {
                        "status": "VERDICT_ALREADY_RECORDED",
                        "verdict": existing.get("verdict"),
                        "epoch": existing.get("deployment_epoch"),
                    },
                    indent=2,
                )
            )
            return 0 if existing.get("verdict") == a.verdict.upper() else 3

        observed = artifact_manifest()
        expected = target.get("resulting_artifact") or {}
        reasons: list[str] = []
        if a.verdict.upper() == "PASS":
            if str(target.get("body_exit_code", "0")) != "0":
                reasons.append("body_exit_nonzero")
            if target.get("entry_point") != CANONICAL_ENTRY_POINT:
                reasons.append("not_governed")
            if target.get("rate_gate_version") != RATE_GATE_VERSION:
                reasons.append("legacy_epoch")
            if not target.get("candidate_match"):
                reasons.append("candidate_mismatch")
            if target.get("candidate_commit") != target.get("deployed_commit"):
                reasons.append("candidate_deployed_mismatch")
            if not observed.get("observable"):
                reasons.append("artifact_unobservable")
            if observed.get("app_git_commit") != target.get("candidate_commit"):
                reasons.append("running_commit_mismatch")
            if expected.get("manifest_sha256") != observed.get("manifest_sha256"):
                reasons.append("manifest_mismatch")
            if expected.get("module_count") != observed.get("module_count"):
                reasons.append("module_count_mismatch")
        verdict = "PASS" if not reasons else "FAIL"
        if a.verdict.upper() == "FAIL":
            verdict = "FAIL"
        entry = {
            "event": "VERDICT",
            "lease_id": a.lease_id,
            "deployment_epoch": target.get("deployment_epoch"),
            "verdict": verdict,
            "requested": a.verdict.upper(),
            "reasons": reasons,
            "evidence": a.evidence,
            "actor": a.actor,
            "session": a.session,
            "candidate_commit": target.get("candidate_commit"),
            "deployed_commit": target.get("deployed_commit"),
            "observed_artifact": {
                "manifest_sha256": observed.get("manifest_sha256"),
                "module_count": observed.get("module_count"),
                "app_git_commit": observed.get("app_git_commit"),
            },
            "observed_at": _iso(),
        }
        _append_ledger(entry)
        print(
            json.dumps(
                {
                    "status": "VERDICT_RECORDED",
                    "epoch": entry["deployment_epoch"],
                    "verdict": verdict,
                    "reasons": reasons,
                },
                indent=2,
            )
        )
        return 0 if verdict == "PASS" else 12


def cmd_resolve_epoch(a) -> int:
    """F13-only recovery for a failed/unverified governed epoch.

    The governed path never calls this. Without it, a single failed preflight
    would block every future deployment forever. The resolution is an explicit
    F13 receipt in the append-only ledger; raw tokens are never involved.
    """
    with _Lock():
        target = None
        for row in reversed(_ledger_rows()):
            if row.get("event") == "RELEASED" and row.get("lease_id") == a.lease_id:
                target = row
                break
        if target is None:
            print(json.dumps({"status": "UNKNOWN_EPOCH", "lease_id": a.lease_id}, indent=2))
            return 5
        if a.authority != "F13":
            print(
                json.dumps(
                    {
                        "status": "HOLD_NOT_OWNER",
                        "reason": "resolve-epoch is F13-only",
                        "authority": a.authority,
                    },
                    indent=2,
                )
            )
            return 3
        existing = _resolution_for(a.lease_id)
        if existing is not None:
            print(
                json.dumps(
                    {
                        "status": "RESOLUTION_ALREADY_RECORDED",
                        "epoch": target.get("deployment_epoch"),
                        "resolved_at": existing.get("resolved_at"),
                    },
                    indent=2,
                )
            )
            return 0
        verdict = _verdict_for(a.lease_id)
        if verdict is not None and str(verdict.get("verdict")).upper() == "PASS":
            print(
                json.dumps(
                    {
                        "status": "ALREADY_VERIFIED",
                        "epoch": target.get("deployment_epoch"),
                        "verdict": "PASS",
                    },
                    indent=2,
                )
            )
            return 0
        entry = {
            "event": "RESOLVED",
            "lease_id": a.lease_id,
            "deployment_epoch": target.get("deployment_epoch"),
            "authority": "F13",
            "receipt": a.receipt,
            "reason": a.reason,
            "actor": a.actor,
            "session": a.session,
            "resolved_at": _iso(),
        }
        _append_ledger(entry)
        print(
            json.dumps(
                {
                    "status": "RESOLVED",
                    "epoch": entry["deployment_epoch"],
                    "authority": "F13",
                    "receipt": a.receipt,
                },
                indent=2,
            )
        )
        return 0


def cmd_check_ancestry(a) -> int:
    """Regression guard (888 recurrence signal, 2026-10-26).

    The deployed artifact must be an ANCESTOR of the candidate. Deploying a
    main that fell behind the live lineage silently rolls back floor work —
    measured twice in 19h (bdc4ec515, then this stack's first 888 HOLD).
    Unknown deployed sha fails closed: cannot prove no regression => HOLD.
    """
    import subprocess

    deployed = (a.deployed or "").strip()
    if not deployed:
        print(json.dumps({
            "status": "NO_DEPLOYED_MARKER",
            "ancestor": None,
            "message": "no deployed-commit marker; nothing to regress against",
        }))
        return 0
    r = subprocess.run(
        ["git", "-C", a.repo, "merge-base", "--is-ancestor", deployed, a.candidate],
        capture_output=True,
    )
    if r.returncode == 0:
        print(json.dumps({
            "status": "ANCESTOR_OK",
            "deployed": deployed,
            "candidate": a.candidate,
        }))
        return 0
    known = subprocess.run(
        ["git", "-C", a.repo, "cat-file", "-e", f"{deployed}^{{commit}}"],
        capture_output=True,
    )
    print(json.dumps({
        "status": "DEPLOY_REGRESSION_RISK",
        "reason": "DEPLOYED_UNKNOWN_TO_REPO" if known.returncode != 0 else "DEPLOYED_NOT_ANCESTOR",
        "deployed": deployed,
        "candidate": a.candidate,
        "message": (
            "the deployed artifact is not an ancestor of the candidate; merge "
            "the deployed lineage before deploying. Zero protected writes."
        ),
    }, indent=2))
    return 13


def cmd_status(a) -> int:
    lease = _read_lease()
    live = _is_live(lease)
    public_lease = None
    if lease:
        public_lease = {k: v for k, v in lease.items() if k != "holder_token_sha256"}
    payload = {
        "state": "LEASED" if live else ("STALE_UNRELEASED" if lease else "IDLE"),
        "lease": public_lease,
        "observed_artifact": artifact_manifest(),
        "envelope_present": ENVELOPE_PATH.exists(),
        "epoch_ledger": str(LEDGER_PATH),
        "epoch_ledger_entries": len(_ledger_rows()),
    }
    if a.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"state: {payload['state']}")
        if public_lease:
            print(f"  owner : {public_lease.get('actor')} ({public_lease.get('lease_id')})")
            print(
                f"  base  : {str(public_lease.get('base_commit'))[:12]} -> "
                f"candidate {str(public_lease.get('candidate_commit'))[:12]}"
            )
            print(
                f"  expires: {public_lease.get('expires_at')} "
                f"epoch={public_lease.get('deployment_epoch')}"
            )
        art = payload["observed_artifact"]
        print(
            f"  live  : {art['module_count']} modules {art['manifest_sha256'][:12]} "
            f"app_commit={str(art['app_git_commit'])[:12]}"
        )
    return 0


def cmd_verify(a) -> int:
    """Expected artifact == observed artifact AND candidate == observed commit."""
    last = None
    for row in reversed(_ledger_rows()):
        if row.get("event") == "RELEASED":
            last = row
            break
    if last is None:
        print(
            json.dumps(
                {
                    "status": "NO_BASELINE",
                    "message": "no RELEASED lease in ledger",
                    "observed_artifact": artifact_manifest(),
                },
                indent=2,
            )
        )
        return 5

    expected = last.get("resulting_artifact") or {}
    observed = artifact_manifest()
    if not observed.get("observable"):
        print(
            json.dumps(
                {
                    "status": "ARTIFACT_UNOBSERVABLE",
                    "reason": observed.get("unobservable_reason"),
                    "expected": {
                        "manifest_sha256": expected.get("manifest_sha256"),
                        "module_count": expected.get("module_count"),
                        "epoch": last.get("deployment_epoch"),
                    },
                    "observed": observed,
                    "meaning": "the imported runtime could not be read; this is NOT a match",
                },
                indent=2,
            )
        )
        return 7

    manifest_same = expected.get("manifest_sha256") == observed.get(
        "manifest_sha256"
    ) and expected.get("module_count") == observed.get("module_count")
    candidate_same = last.get("candidate_commit") == observed.get("app_git_commit")
    same = manifest_same and candidate_same
    payload = {
        "status": "ARTIFACT_UNCHANGED" if same else "ARTIFACT_CHANGED",
        "expected": {
            "manifest_sha256": expected.get("manifest_sha256"),
            "module_count": expected.get("module_count"),
            "candidate_commit": last.get("candidate_commit"),
            "epoch": last.get("deployment_epoch"),
            "released_at": last.get("released_at"),
        },
        "observed": observed,
        "checks": {
            "manifest_same": manifest_same,
            "candidate_same": candidate_same,
        },
        "meaning": (
            "the running runtime is the candidate that was approved"
            if same
            else "manifest equality alone is insufficient: the candidate and/or "
            "artifact changed outside the lease"
        ),
    }
    print(json.dumps(payload, indent=2))
    return 0 if same else 4


def cmd_require(a) -> int:
    """Fail-closed gate for repository-controlled production writers."""
    lease = _read_lease()
    if _is_live(lease):
        return 0
    print(
        json.dumps(
            {
                "status": "NO_ACTIVE_LEASE",
                "action": "refused_before_mutation",
                "caller": a.caller,
                "message": (
                    "no live deployment lease. Acquire one through the canonical "
                    "entrypoint (make deploy-local)."
                ),
                "holder": lease,
            },
            indent=2,
        )
    )
    return 6


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="arifOS deploy lease — one production mutation, one candidate"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("acquire")
    pa.add_argument("--actor", required=True)
    pa.add_argument("--session", required=True)
    pa.add_argument("--base", required=True)
    pa.add_argument("--candidate", required=True)
    pa.add_argument("--entry-point", default="unknown", dest="entry_point")
    pa.add_argument("--deployment-id", default=None, dest="deployment_id")
    pa.add_argument("--ttl", default="1800", help="seconds; default 1800")
    pa.set_defaults(fn=cmd_acquire)

    pc = sub.add_parser("check-envelope")
    pc.add_argument("--envelope", default=str(ENVELOPE_PATH))
    pc.add_argument("--actor", required=True)
    pc.add_argument("--session", required=True)
    pc.set_defaults(fn=cmd_check_envelope)

    pr = sub.add_parser("release")
    pr.add_argument("--envelope", default=str(ENVELOPE_PATH))
    pr.add_argument("--actor", required=True)
    pr.add_argument("--session", required=True)
    pr.add_argument("--receipt", default=None)
    pr.add_argument("--exit-code", default="0", dest="exit_code")
    pr.add_argument("--observed-head", default=None, dest="observed_head")
    pr.add_argument("--rollback-snapshot", default=None, dest="rollback_snapshot")
    pr.add_argument("--stale-pruned", default=None, dest="stale_pruned")
    pr.set_defaults(fn=cmd_release)

    pvc = sub.add_parser("verify-candidate")
    pvc.add_argument("--envelope", default=str(ENVELOPE_PATH))
    pvc.add_argument("--actor", required=True)
    pvc.add_argument("--session", required=True)
    pvc.set_defaults(fn=cmd_verify_candidate)

    pvb = sub.add_parser("verify-baseline")
    pvb.set_defaults(fn=cmd_verify_baseline)

    pve = sub.add_parser("verify-epoch")
    pve.add_argument("--lease-id", required=True, dest="lease_id")
    pve.add_argument("--verdict", choices=("PASS", "FAIL"), default="PASS")
    pve.add_argument("--evidence", required=True)
    pve.add_argument("--actor", required=True)
    pve.add_argument("--session", required=True)
    pve.set_defaults(fn=cmd_verify_epoch)

    prs = sub.add_parser("resolve-epoch")
    prs.add_argument("--lease-id", required=True, dest="lease_id")
    prs.add_argument("--authority", required=True)
    prs.add_argument("--receipt", required=True)
    prs.add_argument("--reason", required=True)
    prs.add_argument("--actor", required=True)
    prs.add_argument("--session", required=True)
    prs.set_defaults(fn=cmd_resolve_epoch)

    pca = sub.add_parser("check-ancestry")
    pca.add_argument("--deployed", default="")
    pca.add_argument("--candidate", required=True)
    pca.add_argument("--repo", default=".")
    pca.set_defaults(fn=cmd_check_ancestry)

    ps = sub.add_parser("status")
    ps.add_argument("--json", action="store_true")
    ps.set_defaults(fn=cmd_status)

    pv = sub.add_parser("verify")
    pv.set_defaults(fn=cmd_verify)

    pq = sub.add_parser("require")
    pq.add_argument("--caller", default=None)
    pq.set_defaults(fn=cmd_require)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
