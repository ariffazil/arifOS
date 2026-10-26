#!/usr/bin/env python3
"""Deploy lease — ONE production mutation at a time.

WHY THIS EXISTS (measured failure class, 2026-10-26)
----------------------------------------------------
Three runtime code states in 21 minutes on one host:

    03:20Z  bb756d958   pre-fix behaviour
    03:34Z  8359618fe   fix deployed, effect-verified (F1 via FQ, F8 unmeasured)
    03:41Z  cd28e52cf   another session deployed; the fix silently regressed

Every individual deploy was legitimate. The sequence was not. Conclusion:
**correctness at deploy time is not persistence of deployed state.** A verified
artifact that can be silently replaced before its observation window closes is
not a stable deployed state.

This tool is the minimum that makes the race visible and refusable:

    IDLE ──acquire──▶ LEASED(owner, base, candidate, expiry)
                                │ build / verify / deploy / effect-verify
                                ▼
                             release ──▶ IDLE   (epoch ledger append)

A second acquire while the state is not IDLE exits HOLD_CONCURRENT_DEPLOY and
writes nothing. `verify` answers the sibling question: is the artifact that is
RUNNING still the artifact that was APPROVED?

It is deliberately small: one flock, one JSON record, one append-only ledger.
No service, no daemon, no new registry. If a deploy path does not call it, the
gate is decoration (K6) — so `make deploy-local` calls it.

USAGE
    deploy_lease.py acquire --actor 333-AGI --base <sha> --candidate <sha> [--ttl 1800]
    deploy_lease.py release --actor <a> --session <s> --lease-id <id> --token <t> [--receipt <p>]
    (acquire returns holder_token ONCE; only its sha256 is stored)
    deploy_lease.py status [--json]
    deploy_lease.py verify            # expected_artifact vs observed_artifact

EXIT CODES
    0  ok
    3  HOLD_CONCURRENT_DEPLOY (another lease is active)
    4  ARTIFACT_CHANGED (running runtime differs from the approved manifest)
    5  NO_ACTIVE_LEASE
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

APP_DIR = Path("/opt/arifos/app")
VENV_ROOT = Path(os.environ.get("ARIFOS_ACTIVE_VENV_ROOT", "/opt/arifos/current/venv"))
SITE_PKGS = VENV_ROOT / "lib" / "python3.13" / "site-packages" / "arifosmcp"
RUNTIME_TARGET = str(SITE_PKGS)


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


def artifact_manifest() -> dict:
    """Hash the code that is actually imported by the running kernel.

    Not the git tree, not /opt/arifos/app — the venv package, because that is
    what `python -c "from arifosmcp.runtime.__main__ import main"` loads.
    """
    files: list[str] = []
    h = hashlib.sha256()
    if SITE_PKGS.is_dir():
        for p in sorted(SITE_PKGS.rglob("*.py")):
            rel = str(p.relative_to(SITE_PKGS))
            digest = _sha_file(p)
            files.append(f"{rel}:{digest}")
            h.update(f"{rel}\0{digest}\0".encode())
    return {
        "manifest_sha256": h.hexdigest() if files else "EMPTY",
        "module_count": len(files),
        "target_runtime": RUNTIME_TARGET,
        "app_git_commit": (APP_DIR / ".git_commit").read_text().strip()
        if (APP_DIR / ".git_commit").exists()
        else None,
    }


def _read_lease() -> dict | None:
    if not LEASE_PATH.exists():
        return None
    try:
        return json.loads(LEASE_PATH.read_text())
    except (ValueError, OSError):
        return None


def _is_live(lease: dict | None) -> bool:
    if not lease:
        return False
    try:
        expires = datetime.fromisoformat(str(lease["expires_at"]).replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return False
    return _now() < expires


def _write_lease(lease: dict | None) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if lease is None:
        LEASE_PATH.unlink(missing_ok=True)
    else:
        tmp = LEASE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(lease, indent=2))
        tmp.replace(LEASE_PATH)


def _append_ledger(entry: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")


def _next_epoch() -> int:
    if not LEDGER_PATH.exists():
        return 1
    n = 0
    with LEDGER_PATH.open() as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n + 1


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


# ── commands ───────────────────────────────────────────────────────────────
def cmd_acquire(a) -> int:
    with _Lock():
        current = _read_lease()
        if _is_live(current):
            out = {
                "status": "HOLD_CONCURRENT_DEPLOY",
                "holder": current,
                "message": (
                    "another deployment owns production. Nothing was written. "
                    "Wait for release or expiry, or coordinate with the holder."
                ),
            }
            print(json.dumps(out, indent=2))
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
        epoch = _next_epoch()
        lease = {
            "lease_id": f"dl-{uuid.uuid4().hex[:12]}",
            "event": "ACQUIRED",
            "actor": a.actor,
            "session": a.session,
            "base_commit": a.base,
            "candidate_commit": a.candidate,
            "target_runtime": RUNTIME_TARGET,
            "acquired_at": _iso(),
            "expires_at": _iso(_now() + timedelta(seconds=int(a.ttl))),
            "deployment_epoch": epoch,
            "previous_artifact": artifact_manifest(),
            "resulting_artifact": None,
            "receipt": None,
        }
        # opaque holder capability: the token is shown ONCE, only its digest is
        # stored. A release without it cannot prove it is the same holder even
        # if it knows actor/session/lease_id (all of which are visible in the
        # lease file and in /tmp/arifos-deploy-lease.json).
        holder_token = secrets.token_urlsafe(32)
        lease["holder_token_sha256"] = hashlib.sha256(holder_token.encode()).hexdigest()
        lease["holder_capability"] = (
            "opaque token presented once at acquire; only its sha256 is stored"
        )
        _write_lease(lease)
        print(
            json.dumps(
                {"status": "LEASED", "lease": lease, "holder_token": holder_token}, indent=2
            )
        )
        return 0


def cmd_release(a) -> int:
    """Release is four-way ownership: actor + session + lease_id + holder token.

    Before 2026-10-26 the guard was `if a.actor and ...`, so omitting --actor
    cleared anyone's lease (measured). Even with --actor required, three of the
    four fields are readable from /tmp/arifos-deploy-lease.json by any process
    on the box, so actor/session/lease_id alone prove knowledge, not ownership.
    Only the token is secret; only its digest is stored.
    """
    with _Lock():
        lease = _read_lease()
        if not _is_live(lease):
            print(json.dumps({"status": "NO_ACTIVE_LEASE"}, indent=2))
            return 5
        stored = str(lease.get("holder_token_sha256") or "")
        if not stored:
            print(
                json.dumps(
                    {
                        "status": "HOLD_NOT_OWNER",
                        "reason": "legacy_lease_without_holder_token",
                        "message": "this lease predates capability tokens; it can only expire",
                    },
                    indent=2,
                )
            )
            return 3
        def same(x: object, y: object) -> bool:
            return hmac.compare_digest(str(x or ""), str(y or ""))

        mismatched: list[str] = []
        if not same(a.actor, lease.get("actor")):
            mismatched.append("actor")
        if not same(a.session, lease.get("session")):
            mismatched.append("session")
        if not same(a.lease_id, lease.get("lease_id")):
            mismatched.append("lease_id")
        presented = hashlib.sha256(str(a.token or "").encode()).hexdigest()
        if not hmac.compare_digest(presented, stored):
            mismatched.append("token")
        if mismatched:
            print(
                json.dumps(
                    {
                        "status": "HOLD_NOT_OWNER",
                        "mismatched": mismatched,
                        "holder": lease.get("actor"),
                        "message": "nothing was written; the lease is unchanged",
                    },
                    indent=2,
                )
            )
            return 3
        lease = dict(lease)
        lease.pop("holder_token_sha256", None)
        lease.pop("holder_capability", None)
        lease["resulting_artifact"] = artifact_manifest()
        lease["receipt"] = a.receipt
        lease["released_at"] = _iso()
        lease["event"] = "RELEASED"
        _append_ledger(lease)
        _write_lease(None)
        print(
            json.dumps(
                {
                    "status": "RELEASED",
                    "epoch": lease["deployment_epoch"],
                    "artifact": lease["resulting_artifact"],
                },
                indent=2,
            )
        )
        return 0


def cmd_status(a) -> int:
    lease = _read_lease()
    live = _is_live(lease)
    payload = {
        "state": "LEASED" if live else ("STALE_UNRELEASED" if lease else "IDLE"),
        "lease": lease,
        "observed_artifact": artifact_manifest(),
        "epoch_ledger": str(LEDGER_PATH),
        "epoch_ledger_entries": sum(1 for _ in LEDGER_PATH.open()) if LEDGER_PATH.exists() else 0,
    }
    if a.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"state: {payload['state']}")
        if lease:
            print(f"  owner : {lease.get('actor')} ({lease.get('lease_id')})")
            print(
                f"  base  : {str(lease.get('base_commit'))[:12]} -> "
                f"candidate {str(lease.get('candidate_commit'))[:12]}"
            )
            print(f"  expires: {lease.get('expires_at')}  epoch={lease.get('deployment_epoch')}")
        art = payload["observed_artifact"]
        print(
            f"  live  : {art['module_count']} modules {art['manifest_sha256'][:12]} "
            f"app_commit={str(art['app_git_commit'])[:12]}"
        )
    return 0


def cmd_verify(a) -> int:
    """expected_artifact != observed_artifact → epistemic invalidation."""
    last = None
    if LEDGER_PATH.exists():
        for line in LEDGER_PATH.open():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("event") == "RELEASED":
                last = row
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
    same = (
        expected.get("manifest_sha256") == observed["manifest_sha256"]
        and expected.get("module_count") == observed["module_count"]
    )
    payload = {
        "status": "ARTIFACT_UNCHANGED" if same else "ARTIFACT_CHANGED",
        "expected": {
            "manifest_sha256": expected.get("manifest_sha256"),
            "module_count": expected.get("module_count"),
            "epoch": last.get("deployment_epoch"),
            "released_at": last.get("released_at"),
        },
        "observed": observed,
        "meaning": (
            "the running runtime is the artifact that was approved"
            if same
            else "SOMETHING REPLACED PRODUCTION OUTSIDE THE LEASE — measurements "
            "taken after this change describe an unapproved artifact"
        ),
    }
    print(json.dumps(payload, indent=2))
    return 0 if same else 4


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="arifOS deploy lease — one production mutation at a time"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("acquire")
    pa.add_argument("--actor", required=True)
    pa.add_argument("--session", required=True)
    pa.add_argument("--base", required=True)
    pa.add_argument("--candidate", required=True)
    pa.add_argument("--ttl", default="1800", help="seconds; default 1800")
    pa.set_defaults(fn=cmd_acquire)

    pr = sub.add_parser("release")
    # --actor is REQUIRED (2026-10-26, 333-AGI). It was optional, and the owner
    # check reads `if a.actor and lease.get("actor") and a.actor != ...` — so a
    # second deployer could clear the holder's lease by omitting the flag, then
    # acquire and deploy unopposed. A gate that can be opened by forgetting a
    # flag is decoration (K6). The deploy body always passes --actor.
    pr.add_argument("--actor", required=True)
    pr.add_argument("--session", required=True)
    pr.add_argument("--lease-id", required=True, dest="lease_id")
    pr.add_argument("--token", required=True)
    pr.add_argument("--receipt", default=None)
    pr.set_defaults(fn=cmd_release)

    ps = sub.add_parser("status")
    ps.add_argument("--json", action="store_true")
    ps.set_defaults(fn=cmd_status)

    pv = sub.add_parser("verify")
    pv.set_defaults(fn=cmd_verify)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
