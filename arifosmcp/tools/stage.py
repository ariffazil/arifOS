"""
arifosmcp/tools/stage.py — KERNEL STAGING

Session-gated staging buffer. Agent proposes a payload; the kernel
hash-locks it and returns a stg_hash. Only a sovereign-verified
caller can arif_commit the staged proposal.

Design: 888-APEX Option A (Decoupled Staging Protocol), 2026-08-03
Floors: F1 (AMANAH — reversible staging, auto-expires)
        F2 (TRUTH — hash-locked, tamper-proof)
        F11 (AUDIT — every stage has provenance receipt)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)

STAGE_DIR = os.environ.get("ARIFOS_STAGE_DIR", "/opt/arifos/app/stage")
STAGE_DEFAULT_TTL = int(os.environ.get("ARIFOS_STAGE_TTL", "86400"))  # 24h


@dataclass
class StageOutput:
    """Structured return for arif_stage. Mirrors SealOutput convention."""

    mode: str = "stage"
    status: str = "STAGED"
    verdict: str = "SABAR"  # Staging is neutral — neither SEAL nor HOLD
    stg_hash: str = ""
    stg_timestamp: int = 0
    expires_at: int = 0
    artifact_path: str = ""
    artifact_sha256: str = ""
    staged_by: str = ""
    session_id: str = ""
    ttl_seconds: int = STAGE_DEFAULT_TTL
    reasons: list[str] = field(default_factory=list)
    next_safe_action: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


async def arif_stage(
    mode: Literal["stage", "verify", "list"] = "stage",
    payload: str = "",
    session_id: str | None = None,
    actor_id: str | None = None,
    session_token: str | None = None,
    seal_purpose: str = "",
    artifact_path: str = "",
    artifact_sha256: str = "",
    ttl_seconds: int = STAGE_DEFAULT_TTL,
    epistemic_labels: dict[str, Any] | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
) -> StageOutput:
    """Stage a proposal for sovereign review.

    The agent PROPOSES. The sovereign COMMITS (via arif_commit).
    An agent can NEVER commit its own staging.

    Args:
        mode: 'stage' (default), 'verify' (check staging status), 'list' (list staged)
        payload: Seal payload content (text or JSON)
        session_id: Agent's session ID (for provenance, NOT authority)
        actor_id: Staging actor (e.g., '333-AGI')
        session_token: Agent's SCT (verified for staging, NOT for commit)
        seal_purpose: Human-readable reason for sealing
        artifact_path: Filesystem path to referenced artifact
        artifact_sha256: SHA256 of referenced artifact (for verification)
        ttl_seconds: Time-to-live before auto-expiry (default: 24h, max: 168h)
        epistemic_labels: OBS/DER/INT/SPEC tagging per claim
        constitutional_chain_id: cc_id from prior arif_judge SEAL (if available)
        judge_state_hash: judge state hash for chain binding

    Returns:
        StageOutput with stg_hash and expiry timestamp
    """
    os.makedirs(STAGE_DIR, exist_ok=True)

    # ── SCT standing (Spine P0) ──
    _standing_authority: str = "OBSERVE_ONLY"
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
                    actor_id = _standing.actor_id
                _standing_authority = _standing.authority or "OBSERVE_ONLY"
            elif session_token:
                return StageOutput(
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

    # ── Verify mode ──
    if mode == "verify":
        return await _verify_staging(session_id=session_id or "", actor_id=actor_id or "")

    if mode == "list":
        return await _list_staging(session_id=session_id or "")

    # ── Stage mode ──
    if not payload:
        return StageOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=["F2 TRUTH: payload is required for staging"],
            next_safe_action="Provide a non-empty payload",
        )

    # ── Cap TTL ──
    ttl_seconds = min(max(ttl_seconds, 60), 604800)  # 1 min - 7 days

    # ── Build staging entry ──
    ts = int(time.time())
    nonce = secrets.token_hex(16)

    staging_entry: dict[str, Any] = {
        "schema": "arifos.stage.v1",
        "payload": payload,
        "session_id": session_id or "",
        "actor_id": actor_id or "",
        "staged_at": ts,
        "expires_at": ts + ttl_seconds,
        "nonce": nonce,
        "seal_purpose": seal_purpose,
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "ttl_seconds": ttl_seconds,
        "epistemic_labels": epistemic_labels or {},
        "constitutional_chain_id": constitutional_chain_id or "",
        "judge_state_hash": judge_state_hash or "",
        "standing_authority": _standing_authority,
    }

    # ── Compute stg_hash (hash-lock the proposal) ──
    canonical = json.dumps(staging_entry, sort_keys=True, ensure_ascii=False)
    stg_hash = hashlib.sha256(canonical.encode()).hexdigest()
    staging_entry["stg_hash"] = stg_hash

    # ── Persist to staging buffer ──
    stage_path = os.path.join(STAGE_DIR, f"{stg_hash}.json")
    try:
        with open(stage_path, "w") as f:
            json.dump(staging_entry, f, indent=2, ensure_ascii=False)
    except OSError as exc:
        logger.exception("Failed to write staging file %s: %s", stage_path, exc)
        return StageOutput(
            status="HOLD",
            verdict="HOLD",
            reasons=[f"F1 AMANAH: Cannot write staging file: {exc}"],
            next_safe_action="Check disk space and permissions on stage directory",
        )

    logger.info(
        "STAGED: hash=%s actor=%s session=%s expires_in=%ds",
        stg_hash[:16],
        actor_id,
        session_id,
        ttl_seconds,
    )

    return StageOutput(
        mode="stage",
        status="STAGED",
        verdict="SABAR",
        stg_hash=stg_hash,
        stg_timestamp=ts,
        expires_at=ts + ttl_seconds,
        artifact_path=artifact_path,
        artifact_sha256=artifact_sha256,
        staged_by=actor_id or "",
        session_id=session_id or "",
        ttl_seconds=ttl_seconds,
        reasons=[f"Staged by {actor_id}. Sovereign commit required."],
        next_safe_action=f"Arif: execute arif_commit {stg_hash}",
        meta={
            "artifact_path": artifact_path,
            "preview_uri": f"arifos://stage/{stg_hash}",
        },
    )


async def _verify_staging(
    session_id: str = "",
    actor_id: str = "",
) -> StageOutput:
    """Check staging status without mutating."""
    # Scan stage directory for entries from this session/actor
    try:
        files = sorted(os.listdir(STAGE_DIR))
    except OSError:
        return StageOutput(
            mode="verify",
            status="EMPTY",
            reasons=["No staging directory or cannot read"],
        )

    staged_entries: list[dict[str, Any]] = []
    for fname in files:
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(STAGE_DIR, fname)
        try:
            with open(fpath) as f:
                entry = json.load(f)
            if session_id and entry.get("session_id") != session_id:
                continue
            staged_entries.append(
                {
                    "stg_hash": entry.get("stg_hash", fname.replace(".json", "")),
                    "staged_by": entry.get("actor_id", ""),
                    "staged_at": entry.get("staged_at", 0),
                    "expires_at": entry.get("expires_at", 0),
                    "expired": entry.get("expires_at", 0) < int(time.time()),
                    "seal_purpose": entry.get("seal_purpose", ""),
                    "artifact_path": entry.get("artifact_path", ""),
                }
            )
        except Exception:
            continue

    return StageOutput(
        mode="verify",
        status="OK",
        reasons=[f"Found {len(staged_entries)} staged proposal(s)"],
        meta={"staged": staged_entries},
    )


async def _list_staging(session_id: str = "") -> StageOutput:
    """List all active staged proposals (not expired)."""
    now = int(time.time())
    try:
        files = sorted(os.listdir(STAGE_DIR))
    except OSError:
        return StageOutput(
            mode="list",
            status="EMPTY",
            reasons=["No staging directory or cannot read"],
        )

    active: list[dict[str, Any]] = []
    for fname in files:
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(STAGE_DIR, fname)
        try:
            with open(fpath) as f:
                entry = json.load(f)
            expires = entry.get("expires_at", 0)
            if expires < now:
                continue  # Expired — skip
            active.append(
                {
                    "stg_hash": entry.get("stg_hash", fname.replace(".json", "")),
                    "staged_by": entry.get("actor_id", ""),
                    "session_id": entry.get("session_id", ""),
                    "expires_at": expires,
                    "expires_in_s": max(expires - now, 0),
                    "seal_purpose": entry.get("seal_purpose", ""),
                }
            )
        except Exception:
            continue

    return StageOutput(
        mode="list",
        status="OK",
        reasons=[f"{len(active)} active staged proposal(s)"],
        meta={"active": active},
    )


# ── Auto-cleanup: remove expired staging files ──
def _purge_expired_staging(now: int | None = None) -> int:
    """Remove expired staging files. Returns count purged."""
    if now is None:
        now = int(time.time())
    purged = 0
    try:
        for fname in os.listdir(STAGE_DIR):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(STAGE_DIR, fname)
            try:
                with open(fpath) as f:
                    entry = json.load(f)
                if entry.get("expires_at", 0) < now:
                    os.remove(fpath)
                    purged += 1
                    logger.info("PURGED expired staging: %s", fname)
            except Exception:
                # Corrupt file — remove anyway
                try:
                    os.remove(fpath)
                    purged += 1
                except Exception:
                    pass
    except OSError:
        pass
    return purged
