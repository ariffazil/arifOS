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

F13 CHALLENGE AUTHORIZATION (forged 2026-07-25):
  - Canonical challenge serialization binds actor + session + candidate + plan + action_class
  - Redis-backed durable storage (in-memory fallback for dev)
  - Structured failure codes per F13 spec
  - Production: ARIFOS_FREE_NONCE_ALLOWED=false, ARIFOS_SENTINEL_AUTH_ALLOWED=false
"""

from __future__ import annotations

import base64
import hashlib
import hashlib
import json
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

# ── Production gate defaults ──────────────────────────────────────────────
_ARIFOS_ED25519_ENABLED = os.getenv("ARIFOS_ED25519_ENABLED", "true").lower() in (
    "true",
    "1",
    "yes",
)
_ARIFOS_FREE_NONCE_ALLOWED = os.getenv("ARIFOS_FREE_NONCE_ALLOWED", "false").lower() in (
    "true",
    "1",
)
_ARIFOS_SENTINEL_AUTH_ALLOWED = os.getenv("ARIFOS_SENTINEL_AUTH_ALLOWED", "false").lower() in (
    "true",
    "1",
)

# ── Structured failure codes (F13 spec) ──────────────────────────────────
F13_FAILURE_CODES: dict[str, str] = {
    "F13_REQUIRED": "F13 sovereign authorization required",
    "SIGNATURE_MISSING": "No cryptographic signature provided",
    "SIGNATURE_INVALID": "Ed25519 signature does not match registered public key",
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

# ============================================================================
# LEGACY IN-MEMORY CHALLENGE STORE (kept for backward compat + arif_init flow)
# ============================================================================


@dataclass
class _Challenge:
    actor_id: str
    expires_at: float
    issued_at: float = 0.0  # populated by issue_*_b64(); 0.0 for legacy urlsafe nonces


_challenge_lock = threading.Lock()
_issued_challenges: dict[str, _Challenge] = {}
_used_challenges: dict[str, float] = {}
_used_challenge_actors: dict[str, str] = {}  # actor binding for in-memory fallback
# In-memory full challenge store (dev fallback — full payload dicts)
_full_challenge_store: dict[str, dict[str, Any]] = {}

# ============================================================================
# REDIS-BACKED DURABLE STORE (F13 authorization challenges)
# ============================================================================

_REDIS_AVAILABLE = False
_redis_client = None


def _get_redis():
    """Lazy-init Redis client for durable nonce storage (sync-only)."""
    global _redis_client, _REDIS_AVAILABLE
    if _redis_client is not None:
        return _redis_client
    redis_url = os.getenv("ARIFOS_REDIS_URL", "redis://127.0.0.1:6379/0")
    try:
        import redis as _redis_mod

        _redis_client = _redis_mod.from_url(redis_url, decode_responses=True)
        _REDIS_AVAILABLE = True
    except Exception as e:
        logger.warning(
            "Redis unavailable for durable nonce storage: %s — falling back to in-memory", e
        )
        _REDIS_AVAILABLE = False
    return _redis_client


def _challenge_redis_key(challenge_id: str) -> str:
    return f"arifos:challenge:{challenge_id}"


def _nonce_redis_key(nonce: str) -> str:
    return f"arifos:nonce:{nonce}"


def _used_nonce_redis_key(nonce: str) -> str:
    return f"arifos:nonce:used:{nonce}"


# ============================================================================
# F13 CANONICAL CHALLENGE SERIALIZATION
# ============================================================================


def canonical_serialize_challenge(fields: dict[str, Any]) -> str:
    """Deterministic canonical serialization for F13 challenge signing.

    Sort-keys, no whitespace, compact separators. This is the EXACT payload
    that gets sha256-hashed and signed by the Ed25519 key.
    """
    _canonical = {
        "actor": fields.get("actor", ""),
        "authorization_session_id": fields.get("authorization_session_id", ""),
        "nonce": fields.get("nonce", ""),
        "candidate_hash": fields.get("candidate_hash", ""),
        "action_class": fields.get("action_class", ""),
        "reversibility": fields.get("reversibility", ""),
        "blast_radius": fields.get("blast_radius", ""),
        "seal_purpose": fields.get("seal_purpose", ""),
        "authority_effect": fields.get("authority_effect", ""),
        "audience": fields.get("audience", "arifOS"),
        "issued_at": fields.get("issued_at", ""),
        "expires_at": fields.get("expires_at", ""),
        "plan_id": fields.get("plan_id", ""),
        "target_environment": fields.get("target_environment", ""),
    }
    return json.dumps(_canonical, sort_keys=True, separators=(",", ":"))


# ============================================================================
# AUTHORIZATION CHALLENGE — ISSUE + VERIFY
# ============================================================================


def issue_authorization_challenge(
    actor: str,
    authorization_session_id: str,
    candidate_hash: str,
    action_class: str = "ACTION_AUTHORIZATION",
    reversibility: str = "R4",
    blast_radius: str = "MEDIUM",
    seal_purpose: str = "AUTHORIZE",
    authority_effect: str = "EXECUTION_GRANT",
    audience: str = "arifOS",
    plan_id: str = "",
    target_environment: str = "",
    human_summary: str = "",
    ttl_seconds: int | None = None,
) -> dict[str, Any]:
    """Issue a F13 authorization challenge and return the authorization_request envelope.

    Stores in Redis (required for production). In-memory fallback only for dev.
    Returns error dict when Redis storage fails.
    """
    ttl = ttl_seconds if ttl_seconds is not None else _CHALLENGE_TTL_SECONDS
    if ttl <= 0:
        raise ValueError("Challenge TTL must be positive")

    now_epoch = time.time()
    issued_at = datetime.fromtimestamp(now_epoch, tz=UTC).isoformat()
    expires_at = datetime.fromtimestamp(now_epoch + ttl, tz=UTC).isoformat()
    nonce = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
    challenge_id = (
        "chal_"
        + hashlib.sha256(
            f"{actor}:{nonce}:{authorization_session_id}:{candidate_hash}".encode()
        ).hexdigest()[:16]
    )

    payload = {
        "challenge_id": challenge_id,
        "nonce": nonce,
        "actor": actor,
        "authorization_session_id": authorization_session_id,
        "candidate_hash": candidate_hash,
        "action_class": action_class,
        "reversibility": reversibility,
        "blast_radius": blast_radius,
        "seal_purpose": seal_purpose,
        "authority_effect": authority_effect,
        "audience": audience,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "plan_id": plan_id,
        "target_environment": target_environment,
        "human_summary": human_summary,
        "consumed": False,
    }
    serialized = json.dumps(payload, separators=(",", ":"))

    # Redis is the canonical store (production requirement)
    client = _get_redis()
    _redis_ttl = _CHALLENGE_TTL_SECONDS
    _c_key = _challenge_redis_key(challenge_id)
    _n_key = _nonce_redis_key(nonce)
    _storage_ok = False
    if client and _REDIS_AVAILABLE:
        try:
            client.set(_c_key, serialized, ex=_redis_ttl)
            client.set(_n_key, challenge_id, ex=_redis_ttl)
            _storage_ok = True
            logger.debug("F13: challenge %s stored in Redis (ttl=%ds)", challenge_id, _redis_ttl)
        except Exception as e:
            logger.error(
                "F13: Redis STORE FAILED for %s: %s — not issuing challenge", challenge_id, e
            )
            return {
                "error": "AUTHORIZATION_STORAGE_UNAVAILABLE",
                "reason": F13_FAILURE_CODES.get(
                    "AUTHORIZATION_STORAGE_UNAVAILABLE", "Challenge storage unavailable"
                ),
            }

    # Dev fallback: in-memory (only when ARIFOS_FREE_NONCE_ALLOWED is set)
    if not _storage_ok:
        _free = os.environ.get("ARIFOS_FREE_NONCE_ALLOWED", "false").lower() in ("true", "1")
        if _free:
            _store_in_memory(actor, nonce)
            _store_full_challenge_in_memory(payload)
        else:
            logger.error(
                "F13: No durable storage available and free-nonce disabled — challenge NOT issued"
            )
            return {
                "error": "AUTHORIZATION_STORAGE_UNAVAILABLE",
                "reason": "No durable storage for challenge. Configure Redis or enable ARIFOS_FREE_NONCE_ALLOWED for dev only.",
            }

    return _build_authorization_request(payload)


def _store_in_memory(actor: str, nonce: str) -> None:
    """Fallback: store in legacy in-memory dict (minimal)."""
    with _challenge_lock:
        _purge_challenges(time.time())
        _issued_challenges[nonce] = _Challenge(
            actor_id=actor,
            expires_at=time.time() + _CHALLENGE_TTL_SECONDS,
            issued_at=time.time(),
        )


def _store_full_challenge_in_memory(payload: dict[str, Any]) -> None:
    """Store the full challenge payload in-memory for verify to load (dev fallback)."""
    nonce = payload.get("nonce", "")
    if not nonce:
        return
    with _challenge_lock:
        _full_challenge_store[nonce] = dict(payload)


def _load_challenge_by_nonce(nonce: str) -> dict[str, Any] | None:
    """Resolve a challenge by nonce from Redis (preferred) or in-memory."""
    client = _get_redis()
    if client and _REDIS_AVAILABLE:
        try:
            cid_raw = client.get(_nonce_redis_key(nonce))
            if cid_raw:
                cid = cid_raw.decode() if isinstance(cid_raw, bytes) else cid_raw
                raw = client.get(_challenge_redis_key(cid))
                if raw:
                    return json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())
        except Exception:
            pass
    # In-memory fallback
    with _challenge_lock:
        chal = _issued_challenges.get(nonce)
        if chal and chal.expires_at > time.time():
            issued = (
                datetime.fromtimestamp(chal.issued_at, tz=UTC).isoformat() if chal.issued_at else ""
            )
            expires = datetime.fromtimestamp(chal.expires_at, tz=UTC).isoformat()
            return {
                "challenge_id": "chal_legacy",
                "nonce": nonce,
                "actor": chal.actor_id,
                "authorization_session_id": chal.actor_id,  # in-memory: bind actor as stable session
                "candidate_hash": "",
                "action_class": "ACTION_AUTHORIZATION",
                "reversibility": "R4",
                "blast_radius": "MEDIUM",
                "seal_purpose": "AUTHORIZE",
                "authority_effect": "EXECUTION_GRANT",
                "audience": "arifOS",
                "issued_at": issued,
                "expires_at": expires,
                "plan_id": "",
                "target_environment": "",
                "human_summary": "",
                "consumed": False,
                "_source": "in_memory_legacy",
            }
    return None


def _mark_consumed(challenge_id: str, nonce: str, actor_id: str = "") -> bool:
    """Atomically mark a challenge as consumed (nonce replay-safe).

    When actor_id is provided, it is stored alongside the consumption record
    so the in-memory fallback can verify actor binding. Without actor_id,
    the in-memory fallback accepts any nonce (dev-only — Redis is canonical).
    """
    client = _get_redis()
    if client and _REDIS_AVAILABLE:
        try:
            used_key = _used_nonce_redis_key(nonce)
            ok = client.set(used_key, "1", nx=True, ex=_CHALLENGE_TTL_SECONDS * 2)
            if ok:
                client.delete(_challenge_redis_key(challenge_id), _nonce_redis_key(nonce))
                return True
            return False
        except Exception as e:
            logger.error(
                "F13: Redis mark consumed FAILED for %s: %s — fail-closed, no in-memory fallback",
                challenge_id,
                e,
            )
            return False
    # In-memory fallback (dev only — only when Redis is NOT available at all)
    with _challenge_lock:
        # Store actor binding when available for F2 audit trace
        _used_challenges[nonce] = time.time() + _CHALLENGE_TTL_SECONDS * 2
        _used_challenge_actors[nonce] = actor_id
    return True


def _check_consumed(nonce: str) -> bool:
    """Check if a nonce has already been consumed."""
    client = _get_redis()
    if client and _REDIS_AVAILABLE:
        try:
            return client.get(_used_nonce_redis_key(nonce)) is not None
        except Exception:
            pass
    with _challenge_lock:
        return nonce in _used_challenges


# ============================================================================
# VERIFY AUTHORIZATION CHALLENGE (full binding check)
# ============================================================================


def verify_authorization_challenge(
    actor: str,
    nonce: str,
    signature_b64: str,
) -> tuple[bool, str, dict[str, Any]]:
    """Full F13 challenge verification — loads canonical challenge from Redis.

    The verifier loads the stored canonical challenge by nonce, verifies
    the Ed25519 signature over the exact stored serialization, and consumes
    the nonce atomically. No caller-supplied fields are accepted for binding
    verification — only the stored challenge is authoritative.

    Returns:
        (verified, failure_code_or_empty, result_dict)
    """
    if not actor:
        return False, "ACTOR_MISMATCH", {"reason": F13_FAILURE_CODES["ACTOR_MISMATCH"]}
    if not nonce:
        return False, "SIGNATURE_MISSING", {"reason": F13_FAILURE_CODES["SIGNATURE_MISSING"]}
    if not signature_b64:
        return False, "SIGNATURE_MISSING", {"reason": F13_FAILURE_CODES["SIGNATURE_MISSING"]}

    # 1. Resolve public key
    public_key = resolve_actor_public_key(actor)
    if public_key is None:
        pub2 = resolve_actor_public_key("arif")
        if pub2:
            public_key = pub2
        else:
            return False, "KEY_NOT_REGISTERED", {"reason": F13_FAILURE_CODES["KEY_NOT_REGISTERED"]}

    # 2. Check replay first (before consuming)
    if _check_consumed(nonce):
        return False, "NONCE_REPLAY", {"reason": F13_FAILURE_CODES["NONCE_REPLAY"]}

    # 3. Load the stored canonical challenge by nonce
    stored = _load_challenge_by_nonce(nonce)
    if stored is None:
        return False, "CHALLENGE_UNKNOWN", {"reason": F13_FAILURE_CODES["CHALLENGE_UNKNOWN"]}

    # 4. Verify binding fields against stored challenge (authoritative source)
    if _normalize_actor(stored.get("actor", "")) != _normalize_actor(actor):
        return False, "ACTOR_MISMATCH", {"reason": F13_FAILURE_CODES["ACTOR_MISMATCH"]}

    # 5. Verify expiry against stored challenge
    expires_at_str = stored.get("expires_at", "")
    if expires_at_str:
        try:
            expires_epoch = datetime.fromisoformat(expires_at_str).timestamp()
            if time.time() > expires_epoch:
                return (
                    False,
                    "CHALLENGE_EXPIRED",
                    {"reason": F13_FAILURE_CODES["CHALLENGE_EXPIRED"]},
                )
        except (ValueError, TypeError):
            pass

    # 6. Reconstruct canonical payload from stored challenge ONLY
    canonical_fields = {
        "actor": stored.get("actor", actor),
        "authorization_session_id": stored.get("authorization_session_id", ""),
        "nonce": nonce,
        "candidate_hash": stored.get("candidate_hash", ""),
        "action_class": stored.get("action_class", "ACTION_AUTHORIZATION"),
        "reversibility": stored.get("reversibility", "R4"),
        "blast_radius": stored.get("blast_radius", "MEDIUM"),
        "seal_purpose": stored.get("seal_purpose", "AUTHORIZE"),
        "authority_effect": stored.get("authority_effect", "EXECUTION_GRANT"),
        "audience": stored.get("audience", "arifOS"),
        "issued_at": stored.get("issued_at", ""),
        "expires_at": stored.get("expires_at", ""),
        "plan_id": stored.get("plan_id", ""),
        "target_environment": stored.get("target_environment", ""),
    }
    canonical_json = canonical_serialize_challenge(canonical_fields)
    canonical_bytes = canonical_json.encode()

    # 7. Verify Ed25519 signature
    try:
        signature_bytes = base64.b64decode(signature_b64)
    except Exception:
        return False, "SIGNATURE_INVALID", {"reason": "Signature base64 decode failed"}

    from cryptography.exceptions import InvalidSignature

    matched = False
    for label, msg_bytes in [
        ("canonical", canonical_bytes),
        ("actor_nonce", f"{actor}:{nonce}".encode()),
    ]:
        try:
            public_key.verify(signature_bytes, msg_bytes)
            matched = True
            break
        except InvalidSignature:
            continue
        except Exception as e:
            logger.error("F13: verify exception: %s", e)
            continue

    if not matched:
        return False, "SIGNATURE_INVALID", {"reason": F13_FAILURE_CODES["SIGNATURE_INVALID"]}

    # 7. Atomic nonce consumption (with actor binding for F2 audit)
    challenge_id = stored.get("challenge_id", "chal_unknown")
    consumed = _mark_consumed(challenge_id, nonce, actor_id=actor)
    if not consumed:
        return False, "NONCE_REPLAY", {"reason": F13_FAILURE_CODES["NONCE_REPLAY"]}

    result = {
        "authorization_consumed": True,
        "challenge_id": challenge_id,
        "canonical_hash": hashlib.sha256(canonical_bytes).hexdigest(),
    }
    return True, "", result


# ============================================================================
# BUILD STRUCTURED RESPONSES
# ============================================================================


def _build_authorization_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Build the authorization_request envelope from a stored challenge payload."""
    return {
        "challenge_id": payload.get("challenge_id", ""),
        "nonce": payload.get("nonce", ""),
        "actor": payload.get("actor", ""),
        "authorization_session_id": payload.get("authorization_session_id", ""),
        "candidate_hash": payload.get("candidate_hash", ""),
        "action_class": payload.get("action_class", ""),
        "reversibility": payload.get("reversibility", ""),
        "blast_radius": payload.get("blast_radius", ""),
        "seal_purpose": payload.get("seal_purpose", ""),
        "authority_effect": payload.get("authority_effect", ""),
        "audience": payload.get("audience", ""),
        "issued_at": payload.get("issued_at", ""),
        "expires_at": payload.get("expires_at", ""),
        "human_summary": payload.get("human_summary", ""),
    }


def build_approval_card(
    action_summary: str,
    reason: str,
    affected_systems: list[str] | None = None,
    environment: str = "production",
    reversibility: str = "R4",
    blast_radius: str = "MEDIUM",
    rollback_summary: str = "",
    requested_by: str = "",
    expires_at: str = "",
) -> dict[str, Any]:
    """Build UI-safe AAA approval card."""
    return {
        "approval_card": {
            "title": "Production authorization required",
            "action_summary": action_summary,
            "reason": reason,
            "affected_systems": affected_systems or [],
            "environment": environment,
            "reversibility": reversibility,
            "blast_radius": blast_radius,
            "rollback_available": bool(rollback_summary),
            "rollback_summary": rollback_summary,
            "requested_by": requested_by,
            "expires_at": expires_at,
            "actions": ["APPROVE", "REJECT", "INSPECT"],
        }
    }


# ============================================================================
# LEGACY API — kept for arif_init challenge flow
# ============================================================================


def _purge_challenges(now: float) -> None:
    expired = [n for n, c in _issued_challenges.items() if c.expires_at <= now]
    for nonce in expired:
        del _issued_challenges[nonce]
    expired_used = [n for n, e in _used_challenges.items() if e <= now]
    for nonce in expired_used:
        del _used_challenges[nonce]
        _used_challenge_actors.pop(nonce, None)


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
    if aid in ("arif", "888", "ariffazil"):
        p = Path(_PUBLIC_KEY_PATH)
        if p.is_file():
            key = _load_pem_public(p.read_bytes())
            if key:
                return key
        p2 = _AAA_KEYS / "arif_public.pem"
        if p2.is_file():
            key = _load_pem_public(p2.read_bytes())
            if key:
                return key
    for name in (f"{aid}_public.pem", f"{actor_id}_public.pem", f"{aid}.pem"):
        p = _AAA_KEYS / name
        if p.is_file():
            key = _load_pem_public(p.read_bytes())
            if key:
                return key
    for base in (_AFORGE_KEYS / aid, _AFORGE_KEYS / actor_id):
        if not base.is_dir():
            continue
        for p in sorted(base.glob("*public*.pem")) + sorted(base.glob("*.pem")):
            if "private" in p.name.lower():
                continue
            key = _load_pem_public(p.read_bytes())
            if key:
                return key
    if _AGENT_REGISTRY.is_file():
        try:
            reg = json.loads(_AGENT_REGISTRY.read_text(encoding="utf-8"))
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
                for item in data.get("dids") or []:
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
    return resolve_actor_public_key(actor_id) is not None


def issue_actor_challenge(actor_id: str, ttl_seconds: int | None = None) -> str:
    """Issue a short-lived, single-use nonce for actor signature verification."""
    aid = _normalize_actor(actor_id)
    if aid not in _ALWAYS_CHALLENGEABLE and not is_registered_actor(actor_id):
        raise ValueError(f"Actor {actor_id!r} is not registered for crypto auth.")
    ttl = ttl_seconds if ttl_seconds is not None else _CHALLENGE_TTL_SECONDS
    if ttl <= 0:
        raise ValueError("Challenge TTL must be positive")
    now = time.time()
    nonce = secrets.token_urlsafe(32)
    with _challenge_lock:
        _purge_challenges(now)
        _issued_challenges[nonce] = _Challenge(actor_id=actor_id, expires_at=now + ttl)
    return nonce


def issue_actor_challenge_b64(actor_id: str, ttl_seconds: int | None = None) -> tuple[str, float]:
    """Issue a base64-encoded 32-byte nonce + return (nonce, issued_at_epoch)."""
    aid = _normalize_actor(actor_id)
    if aid not in _ALWAYS_CHALLENGEABLE and not is_registered_actor(actor_id):
        raise ValueError(f"Actor {actor_id!r} is not registered for crypto auth.")
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
        if _normalize_actor(challenge.actor_id) != _normalize_actor(actor_id):
            return False, "challenge_actor_mismatch"
        if challenge.expires_at <= now:
            del _issued_challenges[nonce]
            return False, "challenge_expired"
        del _issued_challenges[nonce]
        _used_challenges[nonce] = challenge.expires_at
        return True, "challenge_consumed"


def verify_actor_signature(actor_id: str, nonce: str, signature_b64: str) -> bool:
    ok, _ = verify_init_identity(
        actor_id=actor_id, nonce=nonce, signature_b64=signature_b64, constitution_hash=None
    )
    return ok


def verify_init_identity(
    actor_id: str,
    nonce: str,
    signature_b64: str,
    constitution_hash: str | None = None,
    *,
    public_key: ed25519.Ed25519PublicKey | None = None,
) -> tuple[bool, str]:
    if not actor_id:
        return False, "actor_id_missing"
    if not nonce:
        return False, "nonce_missing"
    if not signature_b64:
        return False, "signature_missing"
    if public_key is None:
        public_key = resolve_actor_public_key(actor_id)
    if public_key is None:
        return False, "public_key_unavailable"
    try:
        signature_bytes = base64.b64decode(signature_b64)
    except Exception:
        return False, "signature_b64_invalid"
    payloads: list[tuple[str, bytes]] = [("actor_nonce", f"{actor_id}:{nonce}".encode())]
    aid_norm = _normalize_actor(actor_id)
    if aid_norm != actor_id:
        payloads.append(("actor_norm_nonce", f"{aid_norm}:{nonce}".encode()))
    if constitution_hash:
        payloads.append(
            ("actor_constitution_nonce", f"{actor_id}:{constitution_hash}:{nonce}".encode())
        )
        if aid_norm != actor_id:
            payloads.append(
                (
                    "actor_norm_constitution_nonce",
                    f"{aid_norm}:{constitution_hash}:{nonce}".encode(),
                )
            )
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
    challenge_ok, challenge_reason = _consume_actor_challenge(actor_id, nonce)
    if challenge_ok:
        return True, f"ed25519_signature_verified:{matched_payload}"
    if challenge_reason == "challenge_not_issued":
        if os.getenv("ARIFOS_ALLOW_FREE_NONCE", "0") == "1":
            return True, f"ed25519_free_nonce:{matched_payload}"
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
            "actor_band": "FULL",
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


_ED25519_KEY_CACHE: bytes | None = None
_ED25519_KEY_PATHS: tuple[str, ...] = (
    "/root/.secrets/jwks/ed25519-private.key",
    "/root/.ssh/id_ed25519",
    "/root/.secrets/aaa-identity/keys/arif_private.pem",
)


def _find_ed25519_key() -> bytes | None:
    global _ED25519_KEY_CACHE
    if _ED25519_KEY_CACHE is not None:
        return _ED25519_KEY_CACHE
    _permission_failures: list[str] = []
    for path in _ED25519_KEY_PATHS:
        p = Path(path)
        if p.exists() and p.stat().st_size > 0:
            # FORGED 2026-08-01: Pre-flight readability check.
            # Prevents silent PermissionError → context collapse loop.
            # Root cause: arifOS runs as 'arifos' user but key was root:600.
            if not os.access(path, os.R_OK):
                _permission_failures.append(path)
                logger.warning(
                    "FATAL_OS_ACL: Ed25519 key exists but is NOT readable by "
                    "current user (uid=%d): %s — fix with: "
                    "setfacl -m u:$(whoami):r %s",
                    os.getuid(),
                    path,
                    path,
                )
                continue
            try:
                _ED25519_KEY_CACHE = p.read_bytes()
                return _ED25519_KEY_CACHE
            except OSError:
                continue
    if _permission_failures:
        logger.error(
            "FATAL_OS_ACL: ALL Ed25519 key paths failed readability check. "
            "Paths tried: %s. Permission-denied: %s. "
            "Agent identity verification will FAIL. "
            "Fix: setfacl -m u:arifos:r <key_path> + setfacl -m u:arifos:x <key_dir>",
            list(_ED25519_KEY_PATHS),
            _permission_failures,
        )
    return None


def _auto_sign_nonce(actor_id: str, nonce: str) -> str | None:
    key_bytes = _find_ed25519_key()
    if not key_bytes:
        return None
    message = f"{actor_id}:{nonce}".encode()
    try:
        if len(key_bytes) == 32:
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(key_bytes)
            return base64.b64encode(private_key.sign(message)).decode()
        try:
            private_key = serialization.load_pem_private_key(key_bytes, password=None)
            if isinstance(private_key, ed25519.Ed25519PrivateKey):
                return base64.b64encode(private_key.sign(message)).decode()
        except Exception:
            pass
        try:
            private_key = serialization.load_ssh_private_key(key_bytes, password=None)
            if isinstance(private_key, ed25519.Ed25519PrivateKey):
                return base64.b64encode(private_key.sign(message)).decode()
        except Exception:
            pass
    except ImportError:
        pass
    return None


def generate_session_keypair() -> dict[str, str]:
    """Generate fresh Ed25519 keypair for session identity binding.

    Returns dict with:
      - private_b64: base64-encoded 32-byte private key (kernel-side only, NEVER returned to agent)
      - public_b64:  base64-encoded 32-byte public key
      - thumbprint:  "sha256:<hex>" fingerprint for cross-reference

    Used by arif_init when generate_session_keypair=True.
    Agent receives thumbprint only. Private key stays in kernel session memory.
    """
    import base64 as _b64
    import hashlib as _hashlib

    from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed

    _sk = _ed.Ed25519PrivateKey.generate()
    _pk = _sk.public_key()
    _sk_bytes = _sk.private_bytes_raw()  # 32 bytes
    _pk_bytes = _pk.public_bytes_raw()  # 32 bytes
    _thumbprint = _hashlib.sha256(_pk_bytes).hexdigest()
    return {
        "private_b64": _b64.b64encode(_sk_bytes).decode(),
        "public_b64": _b64.b64encode(_pk_bytes).decode(),
        "thumbprint": f"sha256:{_thumbprint}",
    }


def verify_session_identity_binding(
    *,
    public_key_b64: str,
    actor_id: str,
    payload_hash: str,
    nonce: str,
    signature_b64: str,
) -> bool:
    """Verify Ed25519 signature for session identity binding.

    Message: actor_id || payload_hash || nonce
    Returns True if signature valid, False otherwise.
    """
    import base64 as _b64

    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed

    try:
        _pk_bytes = _b64.b64decode(public_key_b64)
        _pk = _ed.Ed25519PublicKey.from_public_bytes(_pk_bytes)
        _message = f"{actor_id}:{payload_hash}:{nonce}".encode()
        _sig_bytes = _b64.b64decode(signature_b64)
        _pk.verify(_sig_bytes, _message)
        return True
    except (InvalidSignature, Exception):
        return False


def sign_with_session_key(
    *,
    private_key_b64: str,
    actor_id: str,
    payload_hash: str,
    nonce: str,
) -> str:
    """Sign seal payload with session Ed25519 private key.

    Returns base64-encoded signature.
    """
    import base64 as _b64

    from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed

    _sk_bytes = _b64.b64decode(private_key_b64)
    _sk = _ed.Ed25519PrivateKey.from_private_bytes(_sk_bytes)
    _message = f"{actor_id}:{payload_hash}:{nonce}".encode()
    _sig = _sk.sign(_message)
    return _b64.b64encode(_sig).decode()
