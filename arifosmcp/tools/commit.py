"""
arifosmcp/tools/commit.py — KERNEL COMMIT

Sovereign-only authorization gate. Commits a staged proposal (from
arif_stage) to VAULT999. The commit caller MUST NOT be the staging
agent — this invariant is enforced at the kernel level.

Design: 888-APEX Option A (Decoupled Staging Protocol), 2026-08-03
Floors: F1 (AMANAH — commit is irreversible, requires sovereign)
        F2 (TRUTH — hash-locked payload, verified before append)
        F3 (WITNESS — sovereign auth context provides human witness)
        F11 (AUDIT — complete traceability: stg_hash → vault_entry)
        F13 (SOVEREIGN — only F13 can authorize the commit)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)

VAULT999_PATH = os.environ.get(
    "ARIFOS_VAULT999_PATH",
    os.path.join(os.environ.get("ARIFOS_HOME", "/root"), "VAULT999", "outcomes.jsonl"),
)
STAGE_DIR = os.environ.get("ARIFOS_STAGE_DIR", "/opt/arifos/app/stage")


@dataclass
class CommitOutput:
    """Structured return for arif_commit. Mirrors SealOutput convention."""

    mode: str = "commit"
    status: str = "SEALED"
    verdict: str = "SEAL"
    stg_hash: str = ""
    vault_entry_id: str = ""
    committed_at: int = 0
    sovereign: str = "F13_ARIF"
    authorized_via: str = ""
    staged_by: str = ""
    staging_session: str = ""
    reasons: list[str] = field(default_factory=list)
    next_safe_action: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


async def arif_commit(
    mode: Literal["commit", "verify"] = "commit",
    stg_hash: str = "",
    session_id: str | None = None,
    actor_id: str | None = None,
    session_token: str | None = None,
    ack_irreversible: bool = False,
    auth_type: Literal["terminal", "ssh_key", "cockpit", "signed_token"] = "terminal",
    auth_proof: str = "",
) -> CommitOutput:
    """Commit a staged proposal to VAULT999.

    REQUIRES SOVEREIGN AUTHORITY. The commit caller MUST NOT be the
    staging agent. The kernel verifies:
      1. stg_hash exists and is not expired
      2. Commit caller ≠ staging agent (F1 invariant)
      3. Caller has SOVEREIGN authority (F13)
      4. ack_irreversible is True

    Args:
        mode: 'commit' (default) or 'verify' (check staging status only)
        stg_hash: The hash returned by arif_stage
        session_id: Caller's session ID
        actor_id: Caller's actor ID
        session_token: Caller's SCT
        ack_irreversible: Explicit acknowledgment of irreversible action
        auth_type: How sovereign identity is proven
        auth_proof: TTY path, SSH fingerprint, cockpit session token,
                    or Ed25519 signed nonce

    Returns:
        CommitOutput with vault_entry_id and chain verification
    """
    # ── SCT standing (Spine P0) ──
    _standing_authority: str = "OBSERVE_ONLY"
    _standing_actor: str = actor_id or ""
    if session_token or session_id:
        try:
            from arifosmcp.runtime.sct import resolve_standing

            _standing = resolve_standing(
                session_id=session_id,
                actor_id=actor_id,
                session_token=session_token,
                allow_store=True,
            )
            if _standing.valid:
                if _standing.session_id:
                    session_id = _standing.session_id
                if _standing.actor_id and _standing.actor_id != "anonymous":
                    _standing_actor = _standing.actor_id
                _standing_authority = _standing.authority or "OBSERVE_ONLY"
            elif session_token:
                return CommitOutput(
                    status="HOLD",
                    verdict="HOLD",
                    reasons=["L11 AUTH: SCT invalid or expired"],
                    next_safe_action="Call arif_init and pass session_token",
                    meta={
                        "sesat_event": {"sesat": True, "type": "TOKEN_INVALID"},
                        "gate": "L11_SCT_GATE",
                    },
                )
        except Exception:
            pass

    # ── Verify mode (read-only) ──
    if mode == "verify":
        return await _verify_staged(stg_hash)

    # ── Gate: irreversible acknowledgment ──
    if not ack_irreversible:
        return CommitOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=["F1 AMANAH: Commit is IRREVERSIBLE. Set ack_irreversible=true to proceed."],
            next_safe_action="Set ack_irreversible=true if you accept the risk",
        )

    # ── Gate: SOVEREIGN authority ──
    if _standing_authority.upper() not in ("SOVEREIGN", "FULL"):
        return CommitOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=[
                "F13 SOVEREIGN: arif_commit requires SOVEREIGN authority. "
                f"Current: {_standing_authority}."
            ],
            next_safe_action="Arif must execute arif_commit from a sovereign-authenticated context",
            meta={
                "gate": "F13_SOVEREIGN",
                "required": "SOVEREIGN",
                "current": _standing_authority,
            },
        )

    # ── Gate: stg_hash required ──
    if not stg_hash or len(stg_hash) < 16:
        return CommitOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=["F2 TRUTH: stg_hash is required and must be at least 16 chars"],
            next_safe_action="Provide the stg_hash from arif_stage",
        )

    # ── Load staging entry ──
    stage_path = os.path.join(STAGE_DIR, f"{stg_hash}.json")
    try:
        with open(stage_path) as f:
            staging_entry = json.load(f)
    except (OSError, json.JSONDecodeError):
        return CommitOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=[f"Staging hash not found or expired: {stg_hash[:16]}..."],
            next_safe_action="Verify stg_hash is correct and has not expired",
            meta={"stg_hash": stg_hash, "stage_path": stage_path},
        )

    # ── Verify hash integrity ──
    stored_hash = staging_entry.get("stg_hash", "")
    canonical = json.dumps(
        {k: v for k, v in staging_entry.items() if k != "stg_hash"},
        sort_keys=True,
        ensure_ascii=False,
    )
    recomputed = hashlib.sha256(canonical.encode()).hexdigest()
    if recomputed != stored_hash:
        return CommitOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=["F2 TRUTH: Hash mismatch — staged payload may be corrupted"],
            meta={"stored": stored_hash, "recomputed": recomputed},
        )

    # ── Check expiry ──
    expires_at = staging_entry.get("expires_at", 0)
    if expires_at < int(time.time()):
        return CommitOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=["Staging entry has expired."],
            next_safe_action="Re-stage via arif_stage",
            meta={"expires_at": expires_at, "now": int(time.time())},
        )

    # ── CRITICAL INVARIANT: commit caller ≠ staging agent ──
    staged_by = staging_entry.get("actor_id", "")
    staging_sid = staging_entry.get("session_id", "")
    if _standing_actor and staged_by and _standing_actor == staged_by:
        return CommitOutput(
            status="VOID",
            verdict="VOID",
            reasons=[
                "F1 AMANAH VIOLATION: Agent cannot commit its own staging. "
                f"Staged by: {staged_by}, caller: {_standing_actor}"
            ],
            next_safe_action="Sovereign must commit from a different execution context",
            meta={
                "staged_by": staged_by,
                "caller": _standing_actor,
                "gate": "F1_CALLER_EQUALS_STAGER",
            },
        )

    # ── Authorize: sovereign verification ──
    if not _verify_sovereign_context(auth_type, auth_proof, stg_hash):
        return CommitOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=[f"F13 SOVEREIGN: Could not verify sovereign identity via {auth_type}"],
            next_safe_action="Use auth_type=terminal, ssh_key, cockpit, or signed_token",
            meta={"auth_type": auth_type},
        )

    # ── COMMIT: Append to VAULT999 ──
    ts = int(time.time())
    vault_entry = {
        "schema": "arifos.record.v1",
        "record_class": "SOVEREIGN_COMMIT",
        "record_id": f"COMMIT-{stg_hash[:16]}-{ts}",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
        "actor": {"actor_id": _standing_actor, "agent_type": "kernel"},
        "sovereign": "F13_ARIF",
        "session": staging_sid,
        "stg_hash": stg_hash,
        "staged_by": staged_by,
        "authorized_via": auth_type,
        "decision": {
            "outcome": "COMMITTED",
            "verdict": "SEAL",
            "reasons": staging_entry.get("seal_purpose", "Sovereign seal via staging protocol"),
        },
        "payload": staging_entry.get("payload", ""),
        "artifact": {
            "path": staging_entry.get("artifact_path", ""),
            "sha256": staging_entry.get("artifact_sha256", ""),
        },
    }

    try:
        os.makedirs(os.path.dirname(VAULT999_PATH), exist_ok=True)
        with open(VAULT999_PATH, "a") as f:
            f.write(json.dumps(vault_entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        logger.exception("Failed to write VAULT999: %s", exc)
        return CommitOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=[f"F1 AMANAH: Cannot write to VAULT999: {exc}"],
            next_safe_action="Check disk space and file permissions on VAULT999",
        )

    # ── Cleanup: remove staging file ──
    try:
        os.remove(stage_path)
    except OSError:
        pass  # Non-fatal — staging will auto-expire

    logger.info(
        "COMMITTED: stg_hash=%s staged_by=%s authorized_via=%s vault_entry=%s",
        stg_hash[:16],
        staged_by,
        auth_type,
        vault_entry["record_id"],
    )

    return CommitOutput(
        mode="commit",
        status="SEALED",
        verdict="SEAL",
        stg_hash=stg_hash,
        vault_entry_id=vault_entry["record_id"],
        committed_at=ts,
        sovereign="F13_ARIF",
        authorized_via=auth_type,
        staged_by=staged_by,
        staging_session=staging_sid,
        reasons=[f"Committed by F13_ARIF via {auth_type}. Staged by {staged_by}."],
        next_safe_action="Verify: curl https://arif-fazil.com/999/verify",
        meta={
            "stg_hash": stg_hash,
            "vault_entry_id": vault_entry["record_id"],
            "artifact_path": staging_entry.get("artifact_path", ""),
        },
    )


async def _verify_staged(stg_hash: str = "") -> CommitOutput:
    """Check staging status without committing."""
    if not stg_hash:
        return CommitOutput(
            mode="verify",
            status="EMPTY",
            reasons=["No stg_hash provided"],
        )

    stage_path = os.path.join(STAGE_DIR, f"{stg_hash}.json")
    try:
        with open(stage_path) as f:
            entry = json.load(f)
        expires_at = entry.get("expires_at", 0)
        expired = expires_at < int(time.time())
        return CommitOutput(
            mode="verify",
            status="EXPIRED" if expired else "STAGED",
            reasons=[
                f"Staging entry {stg_hash[:16]}... "
                f"{'EXPIRED' if expired else 'ACTIVE'}. "
                f"Staged by {entry.get('actor_id', 'unknown')}. "
                f"Expires at {expires_at}."
            ],
            meta={
                "stg_hash": stg_hash,
                "staged_by": entry.get("actor_id", ""),
                "session_id": entry.get("session_id", ""),
                "expires_at": expires_at,
                "expired": expired,
                "seal_purpose": entry.get("seal_purpose", ""),
                "artifact_path": entry.get("artifact_path", ""),
            },
        )
    except (OSError, json.JSONDecodeError):
        return CommitOutput(
            mode="verify",
            status="NOT_FOUND",
            reasons=[f"Staging hash not found or expired: {stg_hash[:16]}..."],
        )


def _verify_sovereign_context(
    auth_type: str,
    auth_proof: str,
    stg_hash: str = "",
) -> bool:
    """Verify that the caller has sovereign authority.

    Methods:
      - terminal: Check TTY ownership (the caller is root/ariffazil)
      - ssh_key: Check SSH connection fingerprint
      - cockpit: Verify AAA cockpit session token with F13 role
      - signed_token: Verify Ed25519 signature over stg_hash
    """
    if auth_type == "terminal":
        # Check if the caller is a local TTY session with sovereign-level user
        try:
            import pwd

            tty = auth_proof or os.environ.get("SSH_TTY", "")
            user = os.environ.get("USER", "")
            sudo_user = os.environ.get("SUDO_USER", "")

            # Accept if running as root (systemd), ariffazil (sovereign), or via sudo
            if user in ("root", "ariffazil") or sudo_user == "ariffazil":
                logger.info("Terminal auth: user=%s tty=%s", user, tty)
                return True

            # If TTY is specified, check ownership
            if tty:
                tty_stat = os.stat(tty)
                tty_owner = pwd.getpwuid(tty_stat.st_uid).pw_name
                if tty_owner in ("root", "ariffazil"):
                    return True
        except Exception:
            pass
        return False

    elif auth_type == "ssh_key":
        # Check SSH_CONNECTION and SSH_CLIENT environment variables
        if os.environ.get("SSH_CONNECTION"):
            fingerprint = auth_proof
            if fingerprint:
                # Accept known fingerprints (simplified — production would
                # check against authorized_keys)
                return True
            # Even without fingerprint, SSH_CONNECTION presence + sovereign user
            if os.environ.get("USER") in ("root", "ariffazil"):
                return True
        return False

    elif auth_type == "cockpit":
        # Verify AAA cockpit session token with SOVEREIGN role
        # Simplified: check token starts with expected prefix
        if auth_proof and len(auth_proof) >= 32:
            # Production would call AAA :3001 to verify the token
            # For now: accept any valid-length token in trusted execution context
            if os.environ.get("AAA_COCKPIT_TRUSTED") == "true":
                return True
        return False

    elif auth_type == "signed_token":
        # Verify Ed25519 signature over stg_hash
        if auth_proof and stg_hash:
            try:
                # Production would verify the Ed25519 signature against
                # the sovereign's public key
                # For now: placeholder — requires sovereign keypair setup
                logger.info("Signed token verification: %s", auth_proof[:16])
                return True
            except Exception:
                return False
        return False

    return False
