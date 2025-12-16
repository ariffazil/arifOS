"""
Authority token validation (v2) — HMAC + expiry + repo-binding

Modes:
- Production: set ARIFOS_CLIP_AUTH_SECRET (required for validation) to enforce cryptographic tokens.
- Dev/MVP: if no secret is set, validation returns False (safe-by-default; no sealing).

Token format (ASCII):
  CLIP1.<session_id>.<exp_unix>.<repo_fpr>.<sig>

Where:
- session_id: from session.data["id"]
- exp_unix: unix epoch seconds (expiry)
- repo_fpr: repo fingerprint (derived from remote.origin.url or cwd)
- sig: base64url(HMAC_SHA256(secret, f"{session_id}.{exp_unix}.{repo_fpr}"))
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import subprocess
import time
from typing import Optional, Tuple

TOKEN_PREFIX = "CLIP1"
DEFAULT_TTL_SECONDS = 15 * 60  # 15 minutes


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("ascii"))


def fingerprint(value: str, length: int = 12) -> str:
    """Short, non-reversible fingerprint for logging/audit (NOT auth)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def _get_repo_id() -> str:
    """
    Repo identity source (stable enough for binding):
    1) ARIFOS_CLIP_REPO_ID env override (recommended for CI)
    2) git remote.origin.url (if available)
    3) cwd absolute path fallback
    """
    env_repo = os.getenv("ARIFOS_CLIP_REPO_ID")
    if env_repo:
        return env_repo.strip()

    try:
        out = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except Exception:
        pass

    return os.path.abspath(os.getcwd())


def get_repo_fingerprint(length: int = 12) -> str:
    """Repo binding value carried in token."""
    return fingerprint(_get_repo_id(), length=length)


def _sign(secret: str, session_id: str, exp_unix: int, repo_fpr: str) -> str:
    msg = f"{session_id}.{exp_unix}.{repo_fpr}".encode("utf-8")
    mac = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).digest()
    return _b64url_encode(mac)


def create_token(
    session_id: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    repo_fpr: Optional[str] = None,
    secret: Optional[str] = None,
    now_unix: Optional[int] = None,
) -> str:
    """
    Helper to mint a token (requires ARIFOS_CLIP_AUTH_SECRET if secret not provided).
    """
    if not session_id:
        raise ValueError("session_id is required")

    if secret is None:
        secret = os.getenv("ARIFOS_CLIP_AUTH_SECRET", "")
    if not secret:
        raise ValueError("ARIFOS_CLIP_AUTH_SECRET is not set (cannot mint token)")

    if repo_fpr is None:
        repo_fpr = get_repo_fingerprint()

    if now_unix is None:
        now_unix = int(time.time())

    exp_unix = now_unix + int(ttl_seconds)
    sig = _sign(secret, session_id=session_id, exp_unix=exp_unix, repo_fpr=repo_fpr)
    return f"{TOKEN_PREFIX}.{session_id}.{exp_unix}.{repo_fpr}.{sig}"


def _parse_token(token: str) -> Tuple[str, str, int, str, str]:
    """
    Returns: (prefix, session_id, exp_unix, repo_fpr, sig)
    Raises ValueError on malformed input.
    """
    parts = token.split(".")
    if len(parts) != 5:
        raise ValueError("token must have 5 dot-separated parts")
    prefix, session_id, exp_s, repo_fpr, sig = parts
    if prefix != TOKEN_PREFIX:
        raise ValueError("token prefix mismatch")
    if not session_id:
        raise ValueError("session_id missing")
    try:
        exp_unix = int(exp_s)
    except Exception as e:
        raise ValueError("exp must be an int unix timestamp") from e
    if not repo_fpr:
        raise ValueError("repo_fpr missing")
    if not sig:
        raise ValueError("sig missing")
    repo_fpr.encode("ascii")
    sig.encode("ascii")
    return prefix, session_id, exp_unix, repo_fpr, sig


def validate_token(
    token: Optional[str],
    *,
    session_id: Optional[str] = None,
    repo_fpr: Optional[str] = None,
    now_unix: Optional[int] = None,
) -> bool:
    """
    Validate token for sealing.

    Production: ARIFOS_CLIP_AUTH_SECRET must be set, and token must match session_id, repo_fpr, expiry, and HMAC.
    Dev/MVP: if no secret is set, returns False (safe-by-default; no sealing authority).
    """
    if token is None or token == "":
        return False

    secret = os.getenv("ARIFOS_CLIP_AUTH_SECRET", "")
    if not secret:
        return False

    if repo_fpr is None:
        repo_fpr = get_repo_fingerprint()

    if now_unix is None:
        now_unix = int(time.time())

    try:
        _, tok_session_id, exp_unix, tok_repo_fpr, tok_sig = _parse_token(token)
    except Exception:
        return False

    if session_id is not None and tok_session_id != session_id:
        return False

    if tok_repo_fpr != repo_fpr:
        return False

    if exp_unix < now_unix:
        return False

    expected_sig = _sign(secret, session_id=tok_session_id, exp_unix=exp_unix, repo_fpr=tok_repo_fpr)
    return hmac.compare_digest(tok_sig, expected_sig)
