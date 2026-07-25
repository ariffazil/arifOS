"""
arifosmcp/runtime/crypto_auth.py
════════════════════════════════
Cryptographic identity verification for Sovereign + registered agents.

Public key resolution order (first hit wins):
  1. Explicit env ARIFOS_ARIF_PUBLIC_KEY_PATH (arif only)
  2. /root/AAA/IDENTITY/keys/{actor_id}_public.pem
  3. /root/A-FORGE/IDENTITY/keys/{actor_id}/*public*.pem
  4. agent_identities.json identity_proof.public_key_pem
  5. DID registry public_key_hex (did:arif:{actor_id})

Challenge nonces are single-use, TTL default 120s.
"""

from __future__ import annotations

import base64
import hashlib
import hashlib
import json
from datetime import UTC, datetime
import logging
import os
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

logger = logging.getLogger(__name__)

_CHALLENGE_TTL_SECONDS = int(os.getenv("ARIFOS_AUTH_NONCE_TTL_SECONDS", "120"))
_RUNTIME_BASE = Path(os.getenv("ARIFOS_RUNTIME_BASE", "/opt/arifos"))

_PUBLIC_KEY_PATH = Path(
    os.getenv(
        "ARIFOS_ARIF_PUBLIC_KEY_PATH",
        str(_RUNTIME_BASE / "identity/arif_public.pem"),
    )
)
_AAA_KEYS = Path("/root/AAA/IDENTITY/keys")
_AFORGE_KEYS = Path("/root/A-FORGE/IDENTITY/keys")
_AGENT_REGISTRY = Path(
    os.getenv(
        "ARIFOS_AGENT_IDENTITY_REGISTRY",
        str(_RUNTIME_BASE / "identity/agent_identities.json"),
    )
)
_DID_REGISTRY_CANDIDATES = [
    Path(
        os.getenv(
            "ARIFOS_DID_REGISTRY_PATH",
            str(_RUNTIME_BASE / ".secrets/did/registry.json"),
        )
    )
]

if os.getenv("ARIFOS_DEV_DID_REGISTRY_FALLBACK") == "1":
    _DID_REGISTRY_CANDIDATES.extend(
        [
            Path("/root/secrets/did/registry.json"),
            Path("/root/AAA/secrets/did/registry.json"),
            Path("/root/AAA/auth/did_registry.yaml"),
        ]
    )

# Actors that may always receive challenges (in addition to registered agents)
_ALWAYS_CHALLENGEABLE = frozenset({"arif", "888", "ariffazil"})


@dataclass
class _Challenge:
    actor_id: str
    expires_at: float
    issued_at: float = 0.0  # populated by issue_*_b64(); 0.0 for legacy urlsafe nonces


_challenge_lock = threading.Lock()
_issued_challenges: dict[str, _Challenge] = {}
_used_challenges: dict[str, float] = {}


def _purge_challenges(now: float) -> None:
    expired = [
        nonce for nonce, challenge in _issued_challenges.items() if challenge.expires_at <= now
    ]
    for nonce in expired:
        del _issued_challenges[nonce]

    expired_used = [nonce for nonce, expires_at in _used_challenges.items() if expires_at <= now]
    for nonce in expired_used:
        del _used_challenges[nonce]


def _normalize_actor(actor_id: str) -> str:
    return (actor_id or "").lower().strip()


def _load_pem_public(pem_bytes: bytes) -> ed25519.Ed25519PublicKey | None:
    try:
        key = serialization.load_pem_public_key(pem_bytes)
        if isinstance(key, ed25519.Ed25519PublicKey):
            return key
    except Exception as exc:
        logger.debug("PEM public load failed: %s", exc)
    return None


def _load_hex_public(hex_key: str) -> ed25519.Ed25519PublicKey | None:
    try:
        raw = bytes.fromhex(hex_key.strip())
        return ed25519.Ed25519PublicKey.from_public_bytes(raw)
    except Exception as exc:
        logger.debug("hex public load failed: %s", exc)
        return None


def resolve_actor_public_key(actor_id: str) -> ed25519.Ed25519PublicKey | None:
    """Resolve Ed25519 public key for actor_id from federation registries."""
    aid = _normalize_actor(actor_id)
    if not aid:
        return None

    # arif aliases
    if aid in ("arif", "888", "ariffazil"):
        p = Path(_PUBLIC_KEY_PATH)
        if p.is_file():
            key = _load_pem_public(p.read_bytes())
            if key:
                return key
        # also try AAA canonical
        p2 = _AAA_KEYS / "arif_public.pem"
        if p2.is_file():
            key = _load_pem_public(p2.read_bytes())
            if key:
                return key

    # AAA/IDENTITY/keys/{actor}_public.pem
    for name in (f"{aid}_public.pem", f"{actor_id}_public.pem", f"{aid}.pem"):
        p = _AAA_KEYS / name
        if p.is_file():
            key = _load_pem_public(p.read_bytes())
            if key:
                return key

    # A-FORGE/IDENTITY/keys/{actor}/
    for base in (_AFORGE_KEYS / aid, _AFORGE_KEYS / actor_id):
        if not base.is_dir():
            continue
        for p in sorted(base.glob("*public*.pem")) + sorted(base.glob("*.pem")):
            if "private" in p.name.lower():
                continue
            key = _load_pem_public(p.read_bytes())
            if key:
                return key

    # agent_identities.json
    if _AGENT_REGISTRY.is_file():
        try:
            reg = json.loads(_AGENT_REGISTRY.read_text(encoding="utf-8"))
            # try exact and lowercase keys
            entry = reg.get(actor_id) or reg.get(aid)
            if entry:
                proof = entry.get("identity_proof") or {}
                if isinstance(proof, dict) and proof.get("type") == "ed25519":
                    pem = proof.get("public_key_pem")
                    if pem:
                        key = _load_pem_public(pem.encode() if isinstance(pem, str) else pem)
                        if key:
                            return key
        except Exception as exc:
            logger.warning("agent_identities load failed: %s", exc)

    # DID registry (json dict or yaml list)
    for reg_path in _DID_REGISTRY_CANDIDATES:
        try:
            if not reg_path.is_file():
                continue
        except (PermissionError, OSError):
            continue
        try:
            text = reg_path.read_text(encoding="utf-8")
        except (PermissionError, OSError) as exc:
            logger.debug("DID registry path inaccessible: %s — %s", reg_path, exc)
            continue
        except Exception as exc:
            logger.warning("DID registry load failed: %s", exc)
            continue
        try:
            if reg_path.suffix in (".yaml", ".yml"):
                import yaml

                data = yaml.safe_load(text) or {}
                dids = data.get("dids") or []
                for item in dids:
                    did = str(item.get("did", ""))
                    if did.endswith(f":{aid}") or did.endswith(f":{actor_id}"):
                        hx = item.get("public_key_hex")
                        if hx:
                            key = _load_hex_public(hx)
                            if key:
                                return key
            else:
                data = json.loads(text)
                dids = data.get("dids") or {}
                if isinstance(dids, dict):
                    for did, meta in dids.items():
                        if did.endswith(f":{aid}") or did.endswith(f":{actor_id}"):
                            hx = (meta or {}).get("public_key_hex")
                            if hx:
                                key = _load_hex_public(hx)
                                if key:
                                    return key
        except Exception as exc:
            logger.debug("DID registry parse %s: %s", reg_path, exc)

    return None


def is_registered_actor(actor_id: str) -> bool:
    """True if actor has a resolvable public key (registered for crypto auth)."""
    return resolve_actor_public_key(actor_id) is not None


def issue_actor_challenge(actor_id: str, ttl_seconds: int | None = None) -> str:
    """Issue a short-lived, single-use nonce for actor signature verification."""
    aid = _normalize_actor(actor_id)
    if aid not in _ALWAYS_CHALLENGEABLE and not is_registered_actor(actor_id):
        raise ValueError(
            f"Actor {actor_id!r} is not registered for crypto auth. "
            "Register public key via agent-onboard.py first."
        )

    ttl = ttl_seconds if ttl_seconds is not None else _CHALLENGE_TTL_SECONDS
    if ttl <= 0:
        raise ValueError("Challenge TTL must be positive")

    now = time.time()
    nonce = secrets.token_urlsafe(32)
    # Store under original actor_id for consume match (session uses same string)
    with _challenge_lock:
        _purge_challenges(now)
        _issued_challenges[nonce] = _Challenge(actor_id=actor_id, expires_at=now + ttl)
    return nonce


def issue_actor_challenge_b64(actor_id: str, ttl_seconds: int | None = None) -> tuple[str, float]:
    """Issue a base64-encoded 32-byte nonce + return (nonce, issued_at_epoch).

    AAA Phase 5 / Wave 2: live MCP surface shape. The nonce is 32 cryptographically
    random bytes encoded as standard base64 (URL-unsafe charset). The nonce string
    is registered in the issued-challenges dict under the same key so that
    ``verify_actor_signature`` consumes it via the same one-shot path.

    Returns:
        (nonce_b64, issued_at_epoch_float) — caller surfaces issued_at as ISO-8601.
    """
    aid = _normalize_actor(actor_id)
    if aid not in _ALWAYS_CHALLENGEABLE and not is_registered_actor(actor_id):
        raise ValueError(
            f"Actor {actor_id!r} is not registered for crypto auth. "
            "Register public key via agent-onboard.py first."
        )

    ttl = ttl_seconds if ttl_seconds is not None else _CHALLENGE_TTL_SECONDS
    if ttl <= 0:
        raise ValueError("Challenge TTL must be positive")

    now = time.time()
    nonce_b64 = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
    with _challenge_lock:
        _purge_challenges(now)
        _issued_challenges[nonce_b64] = _Challenge(
            actor_id=actor_id, expires_at=now + ttl, issued_at=now
        )
    return nonce_b64, now


def _consume_actor_challenge(actor_id: str, nonce: str) -> tuple[bool, str]:
    now = time.time()
    with _challenge_lock:
        _purge_challenges(now)

        if nonce in _used_challenges:
            return False, "challenge_replayed"

        challenge = _issued_challenges.get(nonce)
        if challenge is None:
            return False, "challenge_not_issued"
        # normalize compare
        if _normalize_actor(challenge.actor_id) != _normalize_actor(actor_id):
            return False, "challenge_actor_mismatch"
        if challenge.expires_at <= now:
            del _issued_challenges[nonce]
            return False, "challenge_expired"

        del _issued_challenges[nonce]
        _used_challenges[nonce] = challenge.expires_at
        return True, "challenge_consumed"


def verify_actor_signature(actor_id: str, nonce: str, signature_b64: str) -> bool:
    """Verify Ed25519 signature over ``{actor_id}:{nonce}`` for any registered actor.

    Prefer challenge-bound nonces from issue_actor_challenge(). For federation
    compatibility, also accepts a cryptographically valid signature when the
    nonce was not pre-issued (then marks it used — one-shot, no replay).
    """
    ok, _reason = verify_init_identity(
        actor_id=actor_id,
        nonce=nonce,
        signature_b64=signature_b64,
        constitution_hash=None,
    )
    return ok


def verify_init_identity(
    actor_id: str,
    nonce: str,
    signature_b64: str,
    constitution_hash: str | None = None,
) -> tuple[bool, str]:
    """Verify init-path Ed25519 identity and consume nonce (one-shot).

    Payload formats tried (first match wins):
      1. ``{actor_id}:{nonce}`` — crypto_auth canonical
      2. ``{actor_id}:{constitution_hash}:{nonce}`` — kernel /identity/verify compat

    Returns:
        (verified, reason) e.g. (True, "ed25519_signature_verified")
    """
    if not actor_id:
        return False, "actor_id_missing"
    if not nonce:
        return False, "nonce_missing"
    if not signature_b64:
        return False, "signature_missing"

    public_key = resolve_actor_public_key(actor_id)
    if public_key is None:
        return False, "public_key_unavailable"

    try:
        signature_bytes = base64.b64decode(signature_b64)
    except Exception:
        return False, "signature_b64_invalid"

    payloads: list[tuple[str, bytes]] = [
        ("actor_nonce", f"{actor_id}:{nonce}".encode()),
    ]
    # Case-normalize actor variants for signature message (common client drift)
    aid_norm = _normalize_actor(actor_id)
    if aid_norm != actor_id:
        payloads.append(("actor_norm_nonce", f"{aid_norm}:{nonce}".encode()))
    if constitution_hash:
        payloads.append(
            (
                "actor_constitution_nonce",
                f"{actor_id}:{constitution_hash}:{nonce}".encode(),
            )
        )
        if aid_norm != actor_id:
            payloads.append(
                (
                    "actor_norm_constitution_nonce",
                    f"{aid_norm}:{constitution_hash}:{nonce}".encode(),
                )
            )
        # sovereign_verify historical aliases
        for alias in ("arif", "ariffazil", "888"):
            if aid_norm in ("arif", "ariffazil", "888") and alias != aid_norm:
                payloads.append(
                    (
                        f"alias_{alias}_constitution_nonce",
                        f"{alias}:{constitution_hash}:{nonce}".encode(),
                    )
                )

    matched_payload = None
    for label, message_bytes in payloads:
        try:
            public_key.verify(signature_bytes, message_bytes)
            matched_payload = label
            break
        except InvalidSignature:
            continue
        except Exception as e:
            logger.error("Crypto Auth: Verification error - %s", e)
            return False, f"verification_error:{type(e).__name__}"

    if matched_payload is None:
        logger.warning("Crypto Auth: Invalid signature for actor=%s", actor_id)
        return False, "ed25519_signature_invalid"

    # Challenge consume (preferred) or one-shot free-nonce consume
    challenge_ok, challenge_reason = _consume_actor_challenge(actor_id, nonce)
    if challenge_ok:
        return True, f"ed25519_signature_verified:{matched_payload}"

    if challenge_reason == "challenge_not_issued":
        # REJECT free-standing nonces — must be issued by issue_actor_challenge.
        # (Prior federation compat accepted them; this was NEG.3 bypass — fixed 2026-07-17.)
        logger.warning(
            "Crypto Auth: free-nonce REJECTED for actor=%s payload=%s — "
            "nonce must be issued by issue_actor_challenge",
            actor_id,
            matched_payload,
        )
        return False, "challenge_not_issued"

    logger.warning("Crypto Auth: Nonce rejected — %s.", challenge_reason)
    return False, challenge_reason


def classify_actor_band(actor_id: str, signature_verified: bool) -> dict[str, Any]:
    """Map verified crypto identity to authority band + agent_class (F13 safe).

    SOVEREIGN principal band only for Arif human aliases.
    Hermes and other agents → AGENT class, LIMITED_MUTATE when verified.
    """
    aid = _normalize_actor(actor_id)
    is_sovereign_principal = aid in ("arif", "888", "ariffazil")
    if not signature_verified:
        return {
            "actor_verified": False,
            "signature_verified": False,
            "actor_band": "OBSERVE_ONLY",
            "agent_class": "UNVERIFIED",
            "is_sovereign_principal": is_sovereign_principal,
            "authority_level": "ANONYMOUS",
        }
    if is_sovereign_principal:
        return {
            "actor_verified": True,
            "signature_verified": True,
            "actor_band": "FULL",  # birth band; measured apex still separate
            "agent_class": "SOVEREIGN_PRINCIPAL",
            "is_sovereign_principal": True,
            "authority_level": "SOVEREIGN",
            "note": "Human sovereign. Hermes remains AGENT; does not become F13.",
        }
    return {
        "actor_verified": True,
        "signature_verified": True,
        "actor_band": "LIMITED_MUTATE",
        "agent_class": "AGENT",
        "is_sovereign_principal": False,
        "authority_level": "OPERATOR",
        "note": "Verified agent — not SOVEREIGN principal (F13).",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LOCALHOST AUTO-IDENTITY (Ed25519 Gap Fix — 2026-07-19)
# ═══════════════════════════════════════════════════════════════════════════════
# When arif_init is called from localhost with a sovereign actor_id and no
# explicit signature, this function auto-signs the challenge nonce using the
# local Ed25519 key. Closes the identity gap for VPS-local agents without
# requiring external signing infrastructure.
# ═══════════════════════════════════════════════════════════════════════════════

_ED25519_KEY_CACHE: bytes | None = None
_ED25519_KEY_PATHS: tuple[str, ...] = (
    "/root/.secrets/jwks/ed25519-private.key",
    "/root/.ssh/id_ed25519",
    "/root/.secrets/aaa-identity/keys/arif_private.pem",
)


def _find_ed25519_key() -> bytes | None:
    """Find and cache the Ed25519 private key from known locations."""
    global _ED25519_KEY_CACHE
    if _ED25519_KEY_CACHE is not None:
        return _ED25519_KEY_CACHE
    for path in _ED25519_KEY_PATHS:
        p = Path(path)
        if p.exists() and p.stat().st_size > 0:
            try:
                _ED25519_KEY_CACHE = p.read_bytes()
                return _ED25519_KEY_CACHE
            except OSError:
                continue
    return None


def _auto_sign_nonce(actor_id: str, nonce: str) -> str | None:
    """Auto-sign a challenge nonce with the local Ed25519 private key.

    Returns base64-encoded Ed25519 signature, or None if signing fails.
    Only for localhost use — external callers must provide their own signature.
    """
    key_bytes = _find_ed25519_key()
    if not key_bytes:
        return None
    message = f"{actor_id}:{nonce}".encode()
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519

        # Try raw 32-byte seed first
        if len(key_bytes) == 32:
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(key_bytes)
            return base64.b64encode(private_key.sign(message)).decode()

        # Try PEM
        try:
            private_key = serialization.load_pem_private_key(key_bytes, password=None)
            if isinstance(private_key, ed25519.Ed25519PrivateKey):
                return base64.b64encode(private_key.sign(message)).decode()
        except Exception:
            pass

        # Try OpenSSH format
        try:
            private_key = serialization.load_ssh_private_key(key_bytes, password=None)
            if isinstance(private_key, ed25519.Ed25519PrivateKey):
                return base64.b64encode(private_key.sign(message)).decode()
        except Exception:
            pass

    except ImportError:
        pass

    return None


# ============================================================================
# F13 CHALLENGE AUTHORIZATION (forged 2026-07-25)
# ============================================================================

_REDIS_AVAILABLE = False
_redis_client = None

def _get_redis():
    global _redis_client, _REDIS_AVAILABLE
    if _redis_client is not None:
        return _redis_client
    url = os.environ.get("ARIFOS_REDIS_URL", "redis://127.0.0.1:6379/0")
    try:
        import redis as _redis_mod
        _redis_client = _redis_mod.from_url(url, decode_responses=True)
        _REDIS_AVAILABLE = True
    except Exception as e:
        logger.warning("Redis unavailable: %s", e)
        _REDIS_AVAILABLE = False
    return _redis_client

def _challenge_redis_key(cid: str) -> str:
    return f"arifos:challenge:{cid}"

def _nonce_redis_key(nonce: str) -> str:
    return f"arifos:nonce:{nonce}"

def _used_nonce_redis_key(nonce: str) -> str:
    return f"arifos:nonce:used:{nonce}"

F13_FAILURE_CODES: dict[str, str] = {
    "F13_REQUIRED": "F13 sovereign authorization required",
    "SIGNATURE_MISSING": "No cryptographic signature provided",
    "SIGNATURE_INVALID": "Ed25519 signature does not match",
    "CHALLENGE_UNKNOWN": "No challenge issued for this nonce",
    "CHALLENGE_EXPIRED": "Challenge TTL has elapsed",
    "NONCE_REPLAY": "Nonce has already been consumed",
    "ACTOR_MISMATCH": "Signed actor does not match challenge actor",
    "SESSION_MISMATCH": "Signed session does not match challenge session",
    "CANDIDATE_HASH_MISMATCH": "Signed candidate hash does not match challenge",
    "PLAN_HASH_MISMATCH": "Signed plan hash does not match challenge",
    "AUDIENCE_MISMATCH": "Signed audience does not match challenge audience",
    "KEY_NOT_REGISTERED": "Actor has no registered Ed25519 public key",
    "AUTHORIZATION_ALREADY_CONSUMED": "Authorization grant already used once",
}

def canonical_serialize_challenge(fields: dict) -> str:
    c = {"actor": fields.get("actor",""), "session_id": fields.get("session_id",""),
         "nonce": fields.get("nonce",""), "candidate_hash": fields.get("candidate_hash",""),
         "action_class": fields.get("action_class",""), "reversibility": fields.get("reversibility",""),
         "blast_radius": fields.get("blast_radius",""), "seal_purpose": fields.get("seal_purpose",""),
         "authority_effect": fields.get("authority_effect",""), "audience": fields.get("audience","arifOS"),
         "issued_at": fields.get("issued_at",""), "expires_at": fields.get("expires_at",""),
         "plan_id": fields.get("plan_id",""), "target_environment": fields.get("target_environment","")}
    return json.dumps(c, sort_keys=True, separators=(",",":"))

def issue_authorization_challenge(actor, session_id, candidate_hash, action_class="ACTION_AUTHORIZATION",
        reversibility="R4", blast_radius="MEDIUM", seal_purpose="AUTHORIZE",
        authority_effect="EXECUTION_GRANT", audience="arifOS", plan_id="", target_environment="",
        human_summary="", ttl_seconds=None):
    ttl = ttl_seconds if ttl_seconds is not None else _CHALLENGE_TTL_SECONDS
    now = time.time()
    issued_at = datetime.fromtimestamp(now, tz=UTC).isoformat()
    expires_at = datetime.fromtimestamp(now + ttl, tz=UTC).isoformat()
    nonce = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
    cid = "chal_" + hashlib.sha256(f"{actor}:{nonce}:{session_id}:{candidate_hash}".encode()).hexdigest()[:16]
    payload = {"challenge_id": cid, "nonce": nonce, "actor": actor, "session_id": session_id,
        "candidate_hash": candidate_hash, "action_class": action_class, "reversibility": reversibility,
        "blast_radius": blast_radius, "seal_purpose": seal_purpose, "authority_effect": authority_effect,
        "audience": audience, "issued_at": issued_at, "expires_at": expires_at, "plan_id": plan_id,
        "target_environment": target_environment, "human_summary": human_summary, "consumed": False}
    serialized = json.dumps(payload, separators=(",",":"))
    cl = _get_redis()
    if cl and _REDIS_AVAILABLE:
        try: cl.set(_challenge_redis_key(cid), serialized, ex=ttl); cl.set(_nonce_redis_key(nonce), cid, ex=ttl)
        except Exception as e: logger.warning("Redis store failed: %s", e)
    return {"challenge_id": cid, "nonce": nonce, "actor": actor, "session_id": session_id,
        "candidate_hash": candidate_hash, "action_class": action_class, "reversibility": reversibility,
        "blast_radius": blast_radius, "seal_purpose": seal_purpose, "authority_effect": authority_effect,
        "audience": audience, "issued_at": issued_at, "expires_at": expires_at, "human_summary": human_summary}

def _load_challenge_by_nonce(nonce):
    cl = _get_redis()
    if cl and _REDIS_AVAILABLE:
        try:
            raw = cl.get(_nonce_redis_key(nonce))
            if raw:
                cid = raw.decode() if isinstance(raw, bytes) else raw
                raw2 = cl.get(_challenge_redis_key(cid))
                if raw2: return json.loads(raw2) if isinstance(raw2, str) else json.loads(raw2.decode())
        except: pass
    with _challenge_lock:
        chal = _issued_challenges.get(nonce)
        if chal and chal.expires_at > time.time():
            return {"challenge_id":"chal_legacy","nonce":nonce,"actor":chal.actor_id,"session_id":"",
                "candidate_hash":"","action_class":"ACTION_AUTHORIZATION","reversibility":"R4",
                "blast_radius":"MEDIUM","seal_purpose":"AUTHORIZE","authority_effect":"EXECUTION_GRANT",
                "audience":"arifOS",
                "issued_at": datetime.fromtimestamp(chal.issued_at,tz=UTC).isoformat() if chal.issued_at else "",
                "expires_at": datetime.fromtimestamp(chal.expires_at,tz=UTC).isoformat(),
                "plan_id":"","target_environment":"","human_summary":"","consumed":False,
                "_source":"in_memory_legacy"}
    return None

def _mark_consumed(challenge_id, nonce):
    cl = _get_redis()
    if cl and _REDIS_AVAILABLE:
        try:
            ok = cl.set(_used_nonce_redis_key(nonce), "1", nx=True, ex=_CHALLENGE_TTL_SECONDS * 2)
            if ok: cl.delete(_challenge_redis_key(challenge_id), _nonce_redis_key(nonce)); return True
            return False
        except: pass
    ok,_ = _consume_actor_challenge(nonce, nonce)
    return ok

def _check_consumed(nonce):
    cl = _get_redis()
    if cl and _REDIS_AVAILABLE:
        try: return cl.get(_used_nonce_redis_key(nonce)) is not None
        except: pass
    with _challenge_lock: return nonce in _used_challenges

def verify_authorization_challenge(actor, nonce, signature_b64, session_id="", candidate_hash="",
        action_class="", reversibility="", blast_radius="", seal_purpose="", authority_effect="",
        audience="arifOS", plan_id="", target_environment=""):
    if not actor: return False, "ACTOR_MISMATCH", {}
    if not nonce: return False, "SIGNATURE_MISSING", {}
    if not signature_b64: return False, "SIGNATURE_MISSING", {}
    pub = resolve_actor_public_key(actor)
    if pub is None: return False, "KEY_NOT_REGISTERED", {}
    if _check_consumed(nonce): return False, "NONCE_REPLAY", {}
    stored = _load_challenge_by_nonce(nonce)
    if stored is None: return False, "CHALLENGE_UNKNOWN", {}
    is_legacy = stored.get("_source")=="in_memory_legacy" or not stored.get("session_id")
    if not is_legacy:
        if _normalize_actor(stored.get("actor","")) != _normalize_actor(actor): return False, "ACTOR_MISMATCH", {}
        if session_id and stored.get("session_id") and stored["session_id"]!=session_id: return False, "SESSION_MISMATCH", {}
        if candidate_hash and stored.get("candidate_hash") and stored["candidate_hash"]!=candidate_hash: return False, "CANDIDATE_HASH_MISMATCH", {}
        if plan_id and stored.get("plan_id") and stored["plan_id"]!=plan_id: return False, "PLAN_HASH_MISMATCH", {}
        if audience and stored.get("audience","arifOS") and stored.get("audience","arifOS")!=audience: return False, "AUDIENCE_MISMATCH", {}
    es = stored.get("expires_at","")
    if es:
        try:
            if time.time() > datetime.fromisoformat(es).timestamp(): return False, "CHALLENGE_EXPIRED", {}
        except: pass
    try: sig_bytes = base64.b64decode(signature_b64)
    except: return False, "SIGNATURE_INVALID", {}
    cf = {"actor":actor,"session_id":session_id or stored.get("session_id",""),"nonce":nonce,
        "candidate_hash":candidate_hash or stored.get("candidate_hash",""),
        "action_class":action_class or stored.get("action_class","ACTION_AUTHORIZATION"),
        "reversibility":reversibility or stored.get("reversibility","R4"),
        "blast_radius":blast_radius or stored.get("blast_radius","MEDIUM"),
        "seal_purpose":seal_purpose or stored.get("seal_purpose","AUTHORIZE"),
        "authority_effect":authority_effect or stored.get("authority_effect","EXECUTION_GRANT"),
        "audience":audience or stored.get("audience","arifOS"),
        "issued_at":stored.get("issued_at",""),"expires_at":stored.get("expires_at",""),
        "plan_id":plan_id or stored.get("plan_id",""),
        "target_environment":target_environment or stored.get("target_environment","")}
    cj = canonical_serialize_challenge(cf); cb = cj.encode()
    ok = False
    for msg in [cb, f"{actor}:{nonce}".encode()]:
        try: pub.verify(sig_bytes, msg); ok = True; break
        except: continue
    if not ok: return False, "SIGNATURE_INVALID", {}
    cid2 = stored.get("challenge_id","chal_unknown")
    if not _mark_consumed(cid2, nonce): return False, "NONCE_REPLAY", {}
    return True, "", {"authorization_consumed":True, "challenge_id":cid2, "canonical_hash":hashlib.sha256(cb).hexdigest()}

def build_approval_card(action_summary, reason, affected_systems=None, environment="production",
        reversibility="R4", blast_radius="MEDIUM", rollback_summary="", requested_by="", expires_at=""):
    return {"approval_card": {"title":"Production authorization required",
        "action_summary":action_summary, "reason":reason, "affected_systems":affected_systems or [],
        "environment":environment, "reversibility":reversibility, "blast_radius":blast_radius,
        "rollback_available":bool(rollback_summary), "rollback_summary":rollback_summary,
        "requested_by":requested_by, "expires_at":expires_at, "actions":["APPROVE","REJECT","INSPECT"]}}
