"""
signed_envelope.py — SIGNED-ENVELOPE v1 (Ed25519 agent-call envelope)

GAP #1 slice: "Verified actor binding end-to-end".
Spec: arifosmcp/docs/SIGNED-ENVELOPE-v1.md. Flag: ARIF_ENVELOPE_SIGNED=1.

signing_input = CANON({actor_id, session_id, timestamp, nonce, payload_hash})
sig           = Ed25519(signing_input, signer_private_key)
payload_hash  = sha256(CANON(payload)) hex

CANON: UTF-8 JSON, recursively sorted keys, compact separators, no unicode
backslash-escaping.
Keys used for key resolution (verify side), in order:
  1. crypto_auth.resolve_actor_public_key (kernel single SOT)
  2. AAA DID registry YAML (organ_id match, public_key_hex)
  3. AAA raw hex keys {actor}_public.key
  4. AAA PEM {actor}_public.pem

Fail-closed: any present-but-invalid envelope rejects. Absent envelope is
pass-through while the flag runs verify-if-present (default-on rollout is a
later, separately authorized step).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import secrets
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)

ENVELOPE_VERSION = 1
ENVELOPE_ALG = "ed25519"
ENVELOPE_FIELD = "signed_envelope"

DEFAULT_WINDOW_SECONDS = 300
_MAX_NONCE_ENTRIES = 100_000

_SIGNED_FIELDS = ("actor_id", "session_id", "timestamp", "nonce", "payload_hash")
_REQUIRED_FIELDS = ("v", "alg", *_SIGNED_FIELDS, "sig")

# Failure codes (spec §6)
ENVELOPE_MISSING_FIELDS = "ENVELOPE_MISSING_FIELDS"
MALFORMED_ENVELOPE = "MALFORMED_ENVELOPE"
KEY_NOT_REGISTERED = "KEY_NOT_REGISTERED"
SIGNATURE_INVALID = "SIGNATURE_INVALID"
PAYLOAD_HASH_MISMATCH = "PAYLOAD_HASH_MISMATCH"
TIMESTAMP_OUT_OF_WINDOW = "TIMESTAMP_OUT_OF_WINDOW"
NONCE_REPLAY = "NONCE_REPLAY"


# ── Canonical serialization ──────────────────────────────────────────────


def canonical_bytes(obj: Any) -> bytes:
    """CANON: UTF-8 JSON, recursively sorted keys, compact, raw unicode."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    ).encode("utf-8")


def payload_digest(payload: Any) -> str:
    """SHA-256 hex over CANON(payload)."""
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def signing_input_bytes(
    actor_id: str, session_id: str, timestamp: int, nonce: str, payload_hash: str
) -> bytes:
    return canonical_bytes(
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "nonce": nonce,
            "payload_hash": payload_hash,
        }
    )


# ── Replay store (in-process; spec §5 limitation) ────────────────────────


class NonceStore:
    """Bounded in-process nonce → expiry map, single-use within window."""

    def __init__(self, max_entries: int = _MAX_NONCE_ENTRIES) -> None:
        self._seen: dict[str, float] = {}
        self._max_entries = max_entries

    def check_and_record(self, nonce: str, ttl_seconds: float, now: float) -> bool:
        """True if nonce is fresh (and now recorded); False on replay."""
        self._purge(now)
        expiry = self._seen.get(nonce)
        if expiry is not None and expiry > now:
            return False
        if len(self._seen) >= self._max_entries:
            # Bound exceeded: fail-closed rather than unbounded growth.
            return False
        self._seen[nonce] = now + ttl_seconds
        return True

    def _purge(self, now: float) -> None:
        if len(self._seen) < 1024:
            return
        expired = [n for n, exp in self._seen.items() if exp <= now]
        for n in expired:
            del self._seen[n]


_NONCE_STORE = NonceStore()


# ── Key resolution ───────────────────────────────────────────────────────


def _aaa_did_registry_path() -> str:
    return os.environ.get("ARIF_ENVELOPE_DID_REGISTRY", "/root/AAA/auth/did_registry.yaml")


def _aaa_hex_key_dir() -> str:
    return os.environ.get("AAA_ENVELOPE_KEY_DIR", "/root/AAA/auth/keys")


def _load_ed25519_public(raw_or_pem: bytes) -> Any:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    try:
        key = serialization.load_pem_public_key(raw_or_pem)
        if isinstance(key, ed25519.Ed25519PublicKey):
            return key
    except Exception:
        pass
    try:
        return ed25519.Ed25519PublicKey.from_public_bytes(raw_or_pem)
    except Exception:
        return None


def _resolve_from_did_registry(actor_id: str) -> Any:
    path = _aaa_did_registry_path()
    if not os.path.isfile(path):
        return None
    try:
        import yaml

        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as exc:
        logger.debug("DID registry load failed (%s): %s", path, exc)
        return None
    for item in data.get("dids") or []:
        organ = str(item.get("organ_id", "")).lower()
        did_suffix = str(item.get("did", "")).rsplit(":", 1)[-1].lower()
        if actor_id.lower() in (organ, did_suffix):
            hex_key = item.get("public_key_hex")
            if hex_key:
                try:
                    return _load_ed25519_public(bytes.fromhex(str(hex_key)))
                except ValueError:
                    return None
    return None


def resolve_public_key(actor_id: str) -> Any:
    """Resolve the actor's Ed25519 public key from federation registries."""
    if not actor_id:
        return None
    try:
        from arifosmcp.runtime.crypto_auth import resolve_actor_public_key

        key = resolve_actor_public_key(actor_id)
        if key is not None:
            return key
    except Exception as exc:
        logger.debug("crypto_auth key resolution unavailable for %s: %s", actor_id, exc)

    key = _resolve_from_did_registry(actor_id)
    if key is not None:
        return key

    hex_path = os.path.join(_aaa_hex_key_dir(), f"{actor_id}_public.key")
    try:
        if os.path.isfile(hex_path):
            with open(hex_path, encoding="utf-8") as fh:
                return _load_ed25519_public(bytes.fromhex(fh.read().strip()))
    except (OSError, ValueError) as exc:
        logger.debug("hex key load failed (%s): %s", hex_path, exc)

    pem_path = os.path.join("/root/AAA/IDENTITY/keys", f"{actor_id}_public.pem")
    try:
        if os.path.isfile(pem_path):
            with open(pem_path, "rb") as fh:
                return _load_ed25519_public(fh.read())
    except OSError as exc:
        logger.debug("PEM key load failed (%s): %s", pem_path, exc)

    return None


# ── Sign ─────────────────────────────────────────────────────────────────


def load_private_key_hex(hex_seed: str) -> Any:
    from cryptography.hazmat.primitives.asymmetric import ed25519

    return ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(hex_seed.strip()))


def load_private_key_file(path: str) -> Any:
    with open(path, encoding="utf-8") as fh:
        return load_private_key_hex(fh.read())


def sign_envelope(
    *,
    actor_id: str,
    session_id: str,
    payload: Any,
    private_key: Any | None = None,
    key_path: str | None = None,
    timestamp: int | None = None,
    nonce: str | None = None,
) -> dict[str, Any]:
    """Build a complete SIGNED-ENVELOPE v1 for `payload`."""
    if private_key is None:
        if key_path is None:
            key_path = os.path.join(_aaa_hex_key_dir(), f"{actor_id}_private.key")
        private_key = load_private_key_file(key_path)

    ts = int(time.time()) if timestamp is None else int(timestamp)
    n = nonce if nonce is not None else secrets.token_hex(16)
    p_hash = payload_digest(payload)
    sig = private_key.sign(signing_input_bytes(actor_id, session_id, ts, n, p_hash))
    return {
        "v": ENVELOPE_VERSION,
        "alg": ENVELOPE_ALG,
        "actor_id": actor_id,
        "session_id": session_id,
        "timestamp": ts,
        "nonce": n,
        "payload_hash": p_hash,
        "sig": base64.b64encode(sig).decode("ascii"),
    }


# ── Verify ───────────────────────────────────────────────────────────────


def verify_envelope(
    envelope: dict[str, Any],
    payload: Any,
    *,
    now: float | None = None,
    window_seconds: int | None = None,
    nonce_store: NonceStore | None = None,
    resolve_key: Callable[[str], Any] | None = None,
) -> tuple[bool, str]:
    """Verify a SIGNED-ENVELOPE v1 against `payload`. Returns (ok, code)."""
    if not isinstance(envelope, dict):
        return False, MALFORMED_ENVELOPE
    for field in _REQUIRED_FIELDS:
        if field not in envelope:
            return False, ENVELOPE_MISSING_FIELDS
    if envelope["v"] != ENVELOPE_VERSION or envelope["alg"] != ENVELOPE_ALG:
        return False, MALFORMED_ENVELOPE

    actor_id = envelope["actor_id"]
    if (
        not isinstance(actor_id, str)
        or not isinstance(envelope["session_id"], str)
        or not isinstance(envelope["timestamp"], int)
        or not isinstance(envelope["nonce"], str)
        or not isinstance(envelope["payload_hash"], str)
        or not isinstance(envelope["sig"], str)
    ):
        return False, MALFORMED_ENVELOPE
    if len(envelope["nonce"]) < 32:  # ≥16 bytes hex
        return False, MALFORMED_ENVELOPE

    ts = envelope["timestamp"]
    current = time.time() if now is None else now
    window = (
        int(os.environ.get("ARIF_ENVELOPE_WINDOW_SECONDS", DEFAULT_WINDOW_SECONDS))
        if window_seconds is None
        else window_seconds
    )
    if abs(current - ts) > window:
        return False, TIMESTAMP_OUT_OF_WINDOW

    if payload_digest(payload) != envelope["payload_hash"]:
        return False, PAYLOAD_HASH_MISMATCH

    resolver = resolve_key or resolve_public_key
    try:
        public_key = resolver(actor_id)
    except Exception:
        public_key = None
    if public_key is None:
        return False, KEY_NOT_REGISTERED

    try:
        sig = base64.b64decode(envelope["sig"], validate=True)
        public_key.verify(
            sig,
            signing_input_bytes(
                actor_id,
                envelope["session_id"],
                ts,
                envelope["nonce"],
                envelope["payload_hash"],
            ),
        )
    except Exception:
        return False, SIGNATURE_INVALID

    store = nonce_store if nonce_store is not None else _NONCE_STORE
    if not store.check_and_record(envelope["nonce"], ttl_seconds=window, now=current):
        return False, NONCE_REPLAY

    return True, "OK"


# ── Ingress helper (kernel wiring) ───────────────────────────────────────


def envelope_flag_enabled() -> bool:
    return os.environ.get("ARIF_ENVELOPE_SIGNED") == "1"


def check_arguments(
    arguments: dict[str, Any] | None,
    *,
    resolve_key: Callable[[str], Any] | None = None,
) -> dict[str, str] | None:
    """Flag-gated verify-if-present check for tools/call arguments.

    Returns None when the call may proceed unchanged:
      - flag off, or
      - no signed_envelope present, or
      - envelope verifies OK.
    Returns {"code", "detail"} when a PRESENT envelope is invalid (reject).
    """
    if not envelope_flag_enabled():
        return None
    if not isinstance(arguments, dict):
        return None
    envelope = arguments.get(ENVELOPE_FIELD)
    if envelope is None:
        return None  # absent → pass-through this slice (spec §6)
    payload = {k: v for k, v in arguments.items() if k != ENVELOPE_FIELD}
    ok, code = verify_envelope(envelope, payload, resolve_key=resolve_key)
    if ok:
        return None
    return {"code": code, "envelope_actor": str(envelope.get("actor_id", ""))}


# ── CLI (cross-language interop: node signs → this verifies) ─────────────

if __name__ == "__main__":  # pragma: no cover - exercised via integration run
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "verify" and "--stdin" in sys.argv:
        blob = json.load(sys.stdin)
        ok, code = verify_envelope(blob["envelope"], blob["payload"])
        print(json.dumps({"ok": ok, "code": code}))
        sys.exit(0 if ok else 1)
    print("usage: python -m arifosmcp.runtime.signed_envelope verify --stdin", file=sys.stderr)
    sys.exit(2)
