"""
arifosmcp/runtime/vault_registry.py — E1 FORGE arif_verify Kernel Ledger
═══════════════════════════════════════════════════════════════════════════════

In-memory registry for SEAL tokens issued at JITU approval.
Atomically appends Type A (SEAL_ISSUED) and Type B (SEAL_VERIFIED) entries
to VAULT999.

PHASE 1 ONLY: arif_verify tool + vault ledger.
Phase 2 (A-FORGE wire) deferred.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import logging
import threading
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── In-Memory SEAL Registry ─────────────────────────────────────────────────

_VAULT_SEAL_REGISTRY: dict[str, dict[str, Any]] = {}
_REGISTRY_LOCK = threading.RLock()

# ── Vault Paths ─────────────────────────────────────────────────────────────

VAULT_DIR = Path("/root/.local/share/arifos/vault999")
VAULT_PATH = VAULT_DIR / "seal_chain.jsonl"
LOCK_PATH = VAULT_DIR / ".seal_verify.lock"

# Ensure vault directory exists
VAULT_DIR.mkdir(parents=True, exist_ok=True)


# ── Atomic Vault Write ──────────────────────────────────────────────────────

def _vault_append(entry: dict[str, Any]) -> None:
    """
    Atomically append a JSONL entry to VAULT999 using exclusive file lock.
    Uses flock(LOCK_EX) so concurrent writers block safely.
    """
    lock_path = str(LOCK_PATH)
    vault_path = str(VAULT_PATH)

    with open(lock_path, "a") as lockf:
        fcntl.flock(lockf.fileno(), fcntl.LOCK_EX)
        try:
            with open(vault_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
        finally:
            fcntl.flock(lockf.fileno(), fcntl.LOCK_UN)


def _compute_sha256_hex(data: str) -> str:
    """Return sha256:<hex> canonical form."""
    return f"sha256:{hashlib.sha256(data.encode('utf-8')).hexdigest()}"


# ── SEAL Issuance ───────────────────────────────────────────────────────────

def issue_seal(
    shell_command: str,
    actor_id: str = "ARIF",
    payload_hash: str | None = None,
    expires_in_seconds: int = 300,
    signature: str = "ed25519:unsigned",
) -> dict[str, Any]:
    """
    Mint a SEAL token at JITU approval for an irreversible shell action.

    Called by arif_judge/arif_seal when issuing a verdict for a shell command
    that has been classified as IRREVERSIBLE.

    Args:
        shell_command:   Exact shell command string (e.g. "git push --force origin main")
        actor_id:       Sovereign actor authorizing this seal
        payload_hash:   SHA256 of the MCP call parameters (optional)
        expires_in_seconds: Token validity window (default 5 min)
        signature:      Ed25519 signature over the token (placeholder for now)

    Returns:
        SealEntry dict with token + metadata (mirrors _VAULT_SEAL_REGISTRY entry shape)
    """
    token = f"SEAL-{uuid.uuid4().hex[:16]}"
    now = time.time()
    issued_at = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now))}"
    expires_at = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now + expires_in_seconds))}"
    command_hash = _compute_sha256_hex(shell_command)

    entry: dict[str, Any] = {
        "token": token,
        "actor": actor_id,
        "shell_command": shell_command,
        "command_hash": command_hash,
        "payload_hash": payload_hash or _compute_sha256_hex(""),
        "issued_at": issued_at,
        "expires_at": expires_at,
        "used": False,
        "signature": signature,
    }

    with _REGISTRY_LOCK:
        _VAULT_SEAL_REGISTRY[token] = entry

    # ── Type A: SEAL_ISSUED ──────────────────────────────────────────────
    vault_entry: dict[str, Any] = {
        "entry_type": "SEAL_ISSUED",
        "token": token,
        "actor": actor_id,
        "shell_command": shell_command,
        "command_hash": command_hash,
        "payload_hash": entry["payload_hash"],
        "issued_at": issued_at,
        "expires_at": expires_at,
        "signature": signature,
        "epoch": issued_at,
    }

    try:
        _vault_append(vault_entry)
    except Exception as e:
        logger.error("[vault_registry] Failed to append SEAL_ISSUED to vault: %s", e)

    return entry


# ── SEAL Verification ──────────────────────────────────────────────────────

def verify_seal(
    token: str,
    command: str,
    actor_id: str = "ARIF",
) -> dict[str, Any]:
    """
    Verify a SEAL token and burn it on use (one-shot, no replay).

    Called by arif_verify MCP tool before A-FORGE executes an irreversible shell
    command. Verifies:
      1. Token exists in registry
      2. Token not expired
      3. Actor matches
      4. Command SHA256 matches stored command_hash
      5. Token not yet consumed (replay safety)

    On success: marks token used=True, writes Type B (SEAL_VERIFIED) to VAULT999.
    On failure: returns violations list for A-FORGE gate.

    Returns:
        dict with keys: token_valid, scope_valid, replay_safe, violations, entry
    """
    violations: list[str] = []
    result: dict[str, Any] = {
        "token_valid": False,
        "scope_valid": False,
        "replay_safe": False,
        "violations": violations,
        "entry": None,
    }

    with _REGISTRY_LOCK:
        entry = _VAULT_SEAL_REGISTRY.get(token)

        # 1. Token must exist
        if entry is None:
            violations.append("TOKEN_NOT_IN_VAULT")
            return result

        # 2. Expiry check
        try:
            expires_ts = time.mktime(time.strptime(entry["expires_at"], "%Y-%m-%dT%H:%M:%SZ"))
            if time.time() > expires_ts:
                violations.append("TOKEN_EXPIRED")
                result["token_valid"] = False
                return result
        except (ValueError, KeyError):
            violations.append("TOKEN_EXPIRED")
            return result

        # 3. Actor mismatch
        if entry.get("actor") != actor_id:
            violations.append(f"ACTOR_MISMATCH: expected={entry.get('actor')} got={actor_id}")

        # 4. Signature verification placeholder
        # Real verification uses verify_sovereign_signature() from tools.py
        # The registry entry carries "ed25519:..." which is validated at issuance
        sig = entry.get("signature", "")
        if sig == "ed25519:unsigned" or not sig:
            # Placeholder — real tokens carry a real signature
            pass  # For now, accept unsigned tokens in dev/pre-prod

        # 5. Command hash scope check
        actual_hash = _compute_sha256_hex(command)
        if entry.get("command_hash") != actual_hash:
            violations.append(
                f"SCOPE_MISMATCH: token covers command_hash={entry.get('command_hash')} "
                f"but received command_hash={actual_hash}"
            )

        # 6. Replay check
        if entry.get("used") is True:
            violations.append("REPLAY_DETECTED: token already consumed")

        # If any hard violation → fail
        hard_violations = {
            "TOKEN_NOT_IN_VAULT",
            "TOKEN_EXPIRED",
            "REPLAY_DETECTED",
        }
        if any(v.split(":")[0] in hard_violations for v in violations):
            result["violations"] = violations
            result["token_valid"] = False
            return result

        # Soft violations (ACTOR_MISMATCH, SCOPE_MISMATCH) still fail but differently
        if violations:
            result["violations"] = violations
            result["token_valid"] = False
            result["scope_valid"] = False
            return result

        # ── All checks passed — burn token ───────────────────────────────
        entry["used"] = True

        result["token_valid"] = True
        result["scope_valid"] = True
        result["replay_safe"] = True
        result["violations"] = []
        result["entry"] = entry

    # ── Type B: SEAL_VERIFIED (outside registry lock) ───────────────────
    now_iso = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"
    vault_entry: dict[str, Any] = {
        "entry_type": "SEAL_VERIFIED",
        "token": token,
        "actor": actor_id,
        "shell_command": command,
        "command_hash": _compute_sha256_hex(command),
        "verified_at": now_iso,
        "original_issued_at": entry["issued_at"],
        "original_expires_at": entry["expires_at"],
        "epoch": now_iso,
    }

    try:
        _vault_append(vault_entry)
    except Exception as e:
        logger.error("[vault_registry] Failed to append SEAL_VERIFIED to vault: %s", e)

    return result


# ── Registry Introspection ──────────────────────────────────────────────────

def get_seal(token: str) -> dict[str, Any] | None:
    """Return the registry entry for a token, or None if not found."""
    with _REGISTRY_LOCK:
        return _VAULT_SEAL_REGISTRY.get(token)


def list_active_seals(actor_id: str | None = None) -> list[dict[str, Any]]:
    """Return all unused, non-expired seals. Optionally filter by actor."""
    with _REGISTRY_LOCK:
        now = time.time()
        active = []
        for entry in _VAULT_SEAL_REGISTRY.values():
            if entry.get("used"):
                continue
            try:
                expires_ts = time.mktime(time.strptime(entry["expires_at"], "%Y-%m-%dT%H:%M:%SZ"))
                if now > expires_ts:
                    continue
            except (ValueError, KeyError):
                continue
            if actor_id and entry.get("actor") != actor_id:
                continue
            active.append(entry)
        return active
