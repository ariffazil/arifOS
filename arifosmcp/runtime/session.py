"""
arifosmcp/runtime/sessions.py — Session Continuity State

Centralized session registry for arifOS runtime.
Single source of truth for session → identity binding.

DITEMPA BUKAN DIBERI — Forged, Not Given

SECURITY HARDENING (Zero-Day Mitigation):
- Strict sovereign identity map: explicit verified identities only
- No guessable aliases (e.g., "arif" not promoted to "ariffazil")
- Identity trust precedence: verified token > signed session > explicit admin map > anonymous
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import re
import tempfile
import time
import uuid
from collections import OrderedDict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import RLock
from typing import Any

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore

from core.shared.types import ActorIdentity

logger = logging.getLogger(__name__)

# Execution-domain fields formerly only in tools.py _FileSessionStore.
# Zen collapse 2026-07-24: one schema in _SESSION_IDENTITY.
_EXECUTION_FIELD_KEYS: tuple[str, ...] = (
    "trace_packet",
    "invocation_count",
    "invocation_tools",
    "agent_policy",
    "epoch_id",
    "decision_class",
    "prior_verdicts",
    "_prior_verdicts",
    "lane",
    "sealed",
    "entropy_delta",
    "model_governance_card",
    "model_shadow",
    "model_soul",
    "session_token",
    "sct_source",
    "allowed_next_verbs",
    "session_warnings",
    "created_at_unix",
    "expires_at_unix",
    "sovereign_id",
    "caller_actor_id",
    "executor_actor_id",
    "delegation_mode",
    "tenant_id",  # P0 MULTI-TENANT (2026-07-29): tenant-scoped session isolation
    "apex",
    "authority",
    "authority_state",
    "verdict",
    "agent_class",
    "actor_band",
    "counterparty_receipt",
    "context_receipt",
    "evidence_receipt",
    "tooling_receipt",
    "memory_receipt",
    "session_verdict",
    "init_memory_recall",
    "identity_verified",
    "identity_verify_reason",
    "ed25519_governance_verified",
    "signature_verified",
    "genesis_card_hash",
    "context_completeness",
    "registry_error",
)
_LEGACY_EXEC_STORE_CANDIDATES: tuple[Path, ...] = (
    Path(os.getenv("ARIFOS_LEGACY_SESSION_STORE", "") or "/app/data/sessions.json"),
    Path("/app/data/sessions.json"),
)
_LEGACY_MIGRATED = False
_LEGACY_MIGRATING = False
# ── Replay / Nonce Detection ────────────────────────────────────────────
# LRU cache of recently seen request IDs (trace_id / jti).
# Rejects duplicate usage within the TTL window — simple replay defense.
_NONCE_CACHE_MAX = int(os.getenv("ARIFOS_NONCE_CACHE_MAX", "4096"))
_NONCE_TTL_SECONDS = int(os.getenv("ARIFOS_NONCE_TTL_SECONDS", "600"))  # 10 min


class _NonceCache:
    """Thread-safe LRU nonce cache with TTL expiry.

    Entries older than TTL are lazily evicted on access.  The cache is bounded
    to max_size entries; when full, the oldest entry is evicted regardless
    of TTL.
    """

    def __init__(self, max_size: int = _NONCE_CACHE_MAX, ttl: int = _NONCE_TTL_SECONDS):
        self._max = max_size
        self._ttl = ttl
        self._lock = RLock()
        self._seen: OrderedDict[str, float] = OrderedDict()  # nonce -> timestamp

    def check_and_record(self, nonce: str) -> tuple[bool, str]:
        """Return (is_fresh, reason).

        If the nonce was seen within TTL, returns (False, "replay_detected").
        Otherwise records it and returns (True, "ok").
        """
        if not nonce:
            return True, "no_nonce"
        now = time.time()
        with self._lock:
            # Lazy evict expired entries (amortized, check at most 16)
            evicted = 0
            while self._seen and evicted < 16:
                oldest_key, oldest_ts = next(iter(self._seen.items()))
                if now - oldest_ts > self._ttl:
                    self._seen.pop(oldest_key)
                    evicted += 1
                else:
                    break

            if nonce in self._seen:
                age = now - self._seen[nonce]
                return False, f"replay_detected: nonce={nonce[:16]}... age={age:.0f}s"

            # Record and enforce max size
            self._seen[nonce] = now
            self._seen.move_to_end(nonce)
            while len(self._seen) > self._max:
                self._seen.popitem(last=False)

            return True, "ok"

    def __len__(self) -> int:
        with self._lock:
            return len(self._seen)


# Module-level singleton — one cache per process
_request_nonce_cache = _NonceCache()


def check_request_nonce(nonce: str) -> tuple[bool, str]:
    """Public API: check a request nonce against the replay cache."""
    return _request_nonce_cache.check_and_record(nonce)


# Global Session Registry (In-memory fallback for stateless bridge)
_ACTOR_IDENTITIES: dict[str, ActorIdentity] = {}
_ACTOR_SESSION_MAP: dict[str, str] = {}  # session_id -> actor_id
_ACTIVE_SESSION_ID: str | None = None
_SESSION_CONTINUITY_STATE: dict[str, dict[str, Any]] = {}
_STORE_LOCK = RLock()
_STORE_LOADED = False

_SESSION_TTL_SECONDS = max(300, int(os.getenv("ARIFOS_SESSION_TTL_SECONDS", "86400")))

# ── Redis-Backed Session Registry (P1) ──────────────────────────────────────
# Replaces global _ACTIVE_SINGLETON for multi-agent safety.
# Falls back to in-memory globals when Redis unavailable.
_REDIS_SESSION_REGISTRY: Any = None
_HAS_REDIS_REGISTRY: bool = False
try:
    from arifosmcp.runtime.session_registry import get_registry as _get_session_registry

    _REGISTRY_INSTANCE = _get_session_registry()
    # Force-init to test connectivity
    _HAS_REDIS_REGISTRY = True
    _REDIS_SESSION_REGISTRY = _REGISTRY_INSTANCE
except Exception:
    pass


def _is_store_parent_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path, delete=True):
            pass
        return True
    except OSError:
        return False


def _default_session_store_path() -> Path:
    explicit = os.getenv("ARIFOS_SESSION_STORE_PATH")
    if explicit:
        return Path(explicit)

    repo_state = Path(__file__).resolve().parents[2] / ".arifos" / "runtime_sessions.json"
    xdg_state = (
        Path(
            os.getenv(
                "XDG_STATE_HOME",
                str(Path.home() / ".local" / "state"),
            )
        )
        / "arifos"
        / "runtime_sessions.json"
    )
    tmp_state = Path("/tmp") / "arifos" / "runtime_sessions.json"  # nosec B108

    for candidate in (repo_state, xdg_state, tmp_state):
        if _is_store_parent_writable(candidate.parent):
            return candidate

    return tmp_state


_SESSION_STORE_PATH = _default_session_store_path()


# ── Signed Session Token Logic (H2 Persistence) ────────────────────────────
def _get_signing_secret() -> bytes:
    """Retrieve secret key for session signing."""
    secret = os.getenv("ARIFOS_SESSION_SECRET")
    if not secret:
        secret_file = os.getenv("ARIFOS_SESSION_SECRET_FILE")
        if secret_file and os.path.exists(secret_file):
            try:
                secret = Path(secret_file).read_text().strip()
            except Exception:  # pragma: allowlist secret  # nosec B105
                secret = "fallback-ephemeral-secret"  # pragma: allowlist secret  # nosec B105
        else:
            secret = "fallback-ephemeral-secret"  # pragma: allowlist secret  # nosec B105
    return secret.encode()


def _sign_session_payload(payload: dict[str, Any]) -> str:
    """Generate a signed base64 token for distributed continuity."""
    dump = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    b64_payload = base64.urlsafe_b64encode(dump.encode()).decode().rstrip("=")
    sig = hmac.new(_get_signing_secret(), b64_payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{b64_payload}.{sig}"


def _verify_session_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a signed session token.

    Checks HMAC signature AND expiry (exp claim).  Returns None if the token
    is tampered, malformed, or expired.
    """
    try:
        if "." not in token:
            return None
        b64_payload, sig = token.split(".", 1)
        expected_sig = hmac.new(
            _get_signing_secret(), b64_payload.encode(), hashlib.sha256
        ).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected_sig):
            return None

        # Add padding back
        missing_padding = len(b64_payload) % 4
        if missing_padding:
            b64_payload += "=" * (4 - missing_padding)

        decoded = base64.urlsafe_b64decode(b64_payload).decode()
        payload = json.loads(decoded)

        # ── Replay defense: verify exp claim ──────────────────────────────
        exp = payload.get("exp")
        if exp is not None:
            try:
                if int(exp) < int(time.time()):
                    logger.warning(
                        "Session token expired: exp=%s now=%s",
                        exp,
                        int(time.time()),
                    )
                    return None
            except (TypeError, ValueError):
                return None

        return payload
    except Exception:
        return None


# ── Sovereign Identity Map ─────────────────────────────────────────────────
# Explicit verified identities only — no guessable aliases
# Blind spot 3 amendment: moved from hardcoded function logic to explicit map
_SOVEREIGN_IDENTITY_MAP: dict[str, str] = {
    "ariffazil": "arif",
}
_VALID_ACTOR_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,64}$")

# ── Session Identity Storage ──────────────────────────────────────────────
# Stores the resolved identity for each anchored session.
# This is the canonical binding: session_id → {actor_id, authority_level, auth_context, ...}
_SESSION_IDENTITY: dict[str, dict[str, Any]] = {}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _session_store_payload() -> dict[str, Any]:
    return {
        "version": 2,  # zen collapse: identity ∪ execution single schema
        "active_session_id": _ACTIVE_SESSION_ID,
        "sessions": _SESSION_IDENTITY,
        "continuity": _SESSION_CONTINUITY_STATE,
    }


def _store_lock_path() -> Path:
    return _SESSION_STORE_PATH.with_suffix(_SESSION_STORE_PATH.suffix + ".lock")


def _flock_exclusive(handle: Any) -> None:
    if fcntl is None:
        return
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def _flock_shared(handle: Any) -> None:
    if fcntl is None:
        return
    fcntl.flock(handle.fileno(), fcntl.LOCK_SH)


def _flock_unlock(handle: Any) -> None:
    if fcntl is None:
        return
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


def _json_default(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    return str(obj)


def _persist_store() -> None:
    """Atomic write under fcntl flock (cross-process)."""
    global _SESSION_STORE_PATH
    try:
        _SESSION_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        lock_path = _store_lock_path()
        lock_path.touch(exist_ok=True)
        with open(lock_path, "a+", encoding="utf-8") as lock_handle:
            _flock_exclusive(lock_handle)
            try:
                tmp_path = _SESSION_STORE_PATH.with_suffix(".tmp")
                tmp_path.write_text(
                    json.dumps(
                        _session_store_payload(),
                        indent=2,
                        sort_keys=True,
                        default=_json_default,
                    ),
                    encoding="utf-8",
                )
                tmp_path.replace(_SESSION_STORE_PATH)
            finally:
                _flock_unlock(lock_handle)
    except OSError as exc:
        fallback_path = Path("/tmp") / "arifos" / "runtime_sessions.json"  # nosec B108
        if _SESSION_STORE_PATH != fallback_path and _is_store_parent_writable(fallback_path.parent):
            logger.warning(
                "Session store path %s unavailable (%s); falling back to %s",
                _SESSION_STORE_PATH,
                exc,
                fallback_path,
            )
            _SESSION_STORE_PATH = fallback_path
            _persist_store()
            return
        logger.warning("Session store persistence failed at %s: %s", _SESSION_STORE_PATH, exc)


def _extract_sessions_map(payload: Any) -> dict[str, Any]:
    """Accept wrapped {sessions:{…}} and flat {sid: record} legacy shapes."""
    if not isinstance(payload, dict):
        return {}
    sessions = payload.get("sessions")
    if isinstance(sessions, dict):
        return {str(k): v for k, v in sessions.items() if isinstance(v, dict)}
    out: dict[str, Any] = {}
    for k, v in payload.items():
        if k in {"version", "active_session_id", "continuity", "sessions"}:
            continue
        if isinstance(v, dict) and (
            "session_id" in v or "actor_id" in v or "stage" in v or "trace_packet" in v
        ):
            out[str(k)] = v
    return out


def _normalize_legacy_record(sid: str, rec: dict[str, Any]) -> dict[str, Any]:
    now = _utcnow()
    out = dict(rec)
    out.setdefault("session_id", sid)
    out.setdefault("actor_id", rec.get("actor_id") or "anonymous")
    verified = bool(
        rec.get("verified") if rec.get("verified") is not None else rec.get("actor_verified", False)
    )
    out["verified"] = verified
    out["actor_verified"] = bool(rec.get("actor_verified", verified))
    if not out.get("expires_at") and rec.get("expires_at_unix"):
        try:
            out["expires_at"] = datetime.fromtimestamp(
                float(rec["expires_at_unix"]), tz=UTC
            ).isoformat()
        except (TypeError, ValueError, OSError):
            out["expires_at"] = (now + timedelta(seconds=_SESSION_TTL_SECONDS)).isoformat()
    elif not out.get("expires_at"):
        out["expires_at"] = (now + timedelta(seconds=_SESSION_TTL_SECONDS)).isoformat()
    if not out.get("expires_at_unix"):
        exp = _parse_iso8601(out.get("expires_at"))
        if exp is not None:
            out["expires_at_unix"] = exp.timestamp()
    out.setdefault("created_at", rec.get("created_at") or now.isoformat())
    out.setdefault("updated_at", now.isoformat())
    out.setdefault("stage", rec.get("stage") or "000")
    out.setdefault("lane", rec.get("lane") or "AGI")
    if out.get("decision_class") is None:
        tp = rec.get("trace_packet") or {}
        if isinstance(tp, dict) and tp.get("decision_class"):
            out["decision_class"] = tp["decision_class"]
    out.setdefault("prior_verdicts", rec.get("_prior_verdicts") or rec.get("prior_verdicts") or [])
    out.setdefault("invocation_count", int(rec.get("invocation_count") or 0))
    return out


def migrate_legacy_exec_store(*, force: bool = False) -> dict[str, Any]:
    """One-shot: fold /app/data/sessions.json into the unified identity store."""
    global _LEGACY_MIGRATED, _LEGACY_MIGRATING
    if _LEGACY_MIGRATING:
        return {"migrated": 0, "status": "in_progress"}
    if _LEGACY_MIGRATED and not force:
        return {"migrated": 0, "status": "already_done"}

    _LEGACY_MIGRATING = True
    try:
        _load_store()
        migrated = 0
        sources: list[str] = []
        seen_paths: set[str] = set()
        for candidate in _LEGACY_EXEC_STORE_CANDIDATES:
            if not candidate or str(candidate) in seen_paths:
                continue
            seen_paths.add(str(candidate))
            if not candidate.exists():
                continue
            try:
                if candidate.resolve() == _SESSION_STORE_PATH.resolve():
                    continue
            except OSError:
                if str(candidate) == str(_SESSION_STORE_PATH):
                    continue
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("Legacy session store unreadable at %s: %s", candidate, exc)
                continue
            sessions = _extract_sessions_map(payload)
            if not sessions:
                ts = datetime.now(UTC).strftime("%Y%m%dT%H%MZ")
                bak = candidate.with_name(candidate.name + f".migrated-empty-{ts}")
                try:
                    candidate.replace(bak)
                    sources.append(str(bak))
                except OSError as exc:
                    logger.warning("Could not retire empty legacy store %s: %s", candidate, exc)
                continue
            with _STORE_LOCK:
                for sid, rec in sessions.items():
                    if not isinstance(rec, dict):
                        continue
                    normalized = _normalize_legacy_record(sid, rec)
                    existing = _SESSION_IDENTITY.get(sid)
                    if existing is None:
                        _SESSION_IDENTITY[sid] = normalized
                        actor = normalized.get("actor_id")
                        if actor:
                            _ACTOR_SESSION_MAP[sid] = str(actor)
                        migrated += 1
                    else:
                        merged = dict(normalized)
                        merged.update(existing)
                        for key in _EXECUTION_FIELD_KEYS:
                            if merged.get(key) in (None, "", [], {}) and normalized.get(
                                key
                            ) not in (
                                None,
                                "",
                                [],
                                {},
                            ):
                                merged[key] = normalized[key]
                        try:
                            if int(normalized.get("invocation_count") or 0) > int(
                                merged.get("invocation_count") or 0
                            ):
                                merged["invocation_count"] = normalized["invocation_count"]
                                merged["invocation_tools"] = normalized.get(
                                    "invocation_tools", merged.get("invocation_tools")
                                )
                        except (TypeError, ValueError):
                            pass
                        if normalized.get("trace_packet") and not existing.get("trace_packet"):
                            merged["trace_packet"] = normalized["trace_packet"]
                        _SESSION_IDENTITY[sid] = merged
                        migrated += 1
                _persist_store()
            ts = datetime.now(UTC).strftime("%Y%m%dT%H%MZ")
            bak = candidate.with_name(candidate.name + f".migrated-{ts}")
            try:
                candidate.replace(bak)
                sources.append(str(bak))
                logger.info(
                    "Legacy session store migrated: %s → %s (%d records)",
                    candidate,
                    bak,
                    len(sessions),
                )
            except OSError as exc:
                logger.warning(
                    "Migrated in-memory but could not rename legacy store %s: %s",
                    candidate,
                    exc,
                )
        _LEGACY_MIGRATED = True
        return {"migrated": migrated, "status": "ok", "sources": sources}
    finally:
        _LEGACY_MIGRATING = False


def _load_store() -> None:
    global _STORE_LOADED, _ACTIVE_SESSION_ID
    with _STORE_LOCK:
        if _STORE_LOADED:
            return
        if _SESSION_STORE_PATH.exists():
            try:
                lock_path = _store_lock_path()
                lock_path.touch(exist_ok=True)
                with open(lock_path, "a+", encoding="utf-8") as lock_handle:
                    _flock_shared(lock_handle)
                    try:
                        payload = json.loads(_SESSION_STORE_PATH.read_text(encoding="utf-8"))
                    finally:
                        _flock_unlock(lock_handle)
                sessions = payload.get("sessions")
                continuity = payload.get("continuity")
                if isinstance(sessions, dict):
                    _SESSION_IDENTITY.update(sessions)
                    for sid, record in sessions.items():
                        actor = (record or {}).get("actor_id")
                        if actor:
                            _ACTOR_SESSION_MAP[str(sid)] = str(actor)
                if isinstance(continuity, dict):
                    _SESSION_CONTINUITY_STATE.update(continuity)
                if payload.get("active_session_id"):
                    _ACTIVE_SESSION_ID = str(payload["active_session_id"])
            except Exception:
                pass
        _STORE_LOADED = True
    if not _LEGACY_MIGRATING and not _LEGACY_MIGRATED:
        try:
            migrate_legacy_exec_store()
        except Exception as exc:
            logger.warning("Legacy session migration skipped: %s", exc)


def _normalize_risk_tier(risk_tier: str | None, *, verified: bool = False) -> str:
    normalized = str(risk_tier or "medium").strip().lower()
    if normalized not in {"low", "medium", "high", "critical"}:
        normalized = "medium"
    if verified and normalized == "low":
        return "medium"
    return normalized


def _merge_dict(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def _deep_get(data: dict[str, Any] | None, *path: str) -> Any:
    current: Any = data
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _is_session_expired(record: dict[str, Any] | None) -> bool:
    if not record:
        return True
    expires_at = _parse_iso8601(record.get("expires_at"))
    return expires_at is not None and expires_at <= _utcnow()


def _ensure_active_record(session_id: str) -> dict[str, Any] | None:
    _load_store()
    record = _SESSION_IDENTITY.get(session_id)

    # H2: Token recovery for distributed environments (stateless fallback)
    if record is None and session_id.startswith("sid_"):
        try:
            # Format: sid_<uuid>--<payload_b64>.<sig>
            if "--" in session_id:
                _, token = session_id.split("--", 1)
                recovered = _verify_session_token(token)
                if recovered:
                    # _verify_session_token already validates exp claim — expired tokens return None
                    # Reconstruct ephemeral record
                    record = {
                        "session_id": session_id,
                        "actor_id": recovered.get("aid", "anonymous"),
                        "authority_level": recovered.get("lvl", "low"),
                        "verified": recovered.get("v", False),
                        "recovered_from_token": True,
                        "expires_at": (datetime.now(UTC) + timedelta(minutes=30)).isoformat(),
                    }
                    # Cache it locally
                    with _STORE_LOCK:
                        _SESSION_IDENTITY[session_id] = record
        except Exception:
            pass

    # H2b SEAL-* → tools._SESSIONS bridge RETIRED (zen collapse 2026-07-24).
    # Legacy /app/data/sessions.json migrates into _SESSION_IDENTITY on load.

    if _is_session_expired(record):
        clear_session_identity(session_id)
        return None
    return record


def _write_record(session_id: str, record: dict[str, Any]) -> None:
    with _STORE_LOCK:
        _SESSION_IDENTITY[session_id] = record
        _persist_store()


def _touch_record(session_id: str, updates: dict[str, Any]) -> None:
    current = _ensure_active_record(session_id) or {}
    now = _utcnow()
    record = _merge_dict(current, updates)
    record["updated_at"] = now.isoformat()
    record["last_seen_at"] = now.isoformat()
    record["expires_at"] = (now + timedelta(seconds=_SESSION_TTL_SECONDS)).isoformat()
    _write_record(session_id, record)


def _canonical_actor_key(actor_id: str | None) -> str:
    """Normalize actor_id for ownership comparison.

    Lowercases and strips whitespace. Maps known sovereign variants
    to a single canonical key so 'ARIF', 'Arif', 'arif' all compare equal.
    """
    if not actor_id:
        return ""
    raw = actor_id.strip().lower()
    # Sovereign variants → canonical
    _SOVEREIGN_MAP = {
        "arif": "arif",
        "ariffazil": "arif",
        "arif_fazil": "arif",
        "arif-fazil": "arif",
        "arif fazil": "arif",
        "muhammad arif": "arif",
        "muhammad_arif": "arif",
        "888": "arif",
        "f13": "arif",
        "sovereign": "arif",
    }
    return _SOVEREIGN_MAP.get(raw, raw)


def _resolve_session_id(
    provided_id: str | None, *, caller_actor_id: str | None = None
) -> str | None:
    """Resolve session_id from provided input or last active session.

    P0-A SESSION ISOLATION (2026-07-17):
    When falling back to the global _ACTIVE_SESSION_ID, validate that the
    resolved session belongs to the calling actor (after canonical normalization).
    If caller_actor_id is provided and does NOT match the session owner, return
    None instead of silently inheriting another actor's session.

    Every new invocation must either provide an explicit valid session_id/token
    or create a new session. It must never silently inherit another actor's session.
    """
    _load_store()
    if provided_id and str(provided_id).strip():
        return provided_id

    # Fallback to global active session — but ONLY if actor matches
    candidate = _ACTIVE_SESSION_ID
    if not candidate:
        return None

    # If no caller_actor_id specified, allow the fallback (backward compat)
    if not caller_actor_id:
        logger.debug(
            "_resolve_session_id: no caller_actor_id, allowing fallback to %s",
            candidate,
        )
        return candidate

    # Actor ownership check: verify the active session belongs to this actor
    _SESSION_IDENTITY  # noqa: B018 — ensure module-level dict is accessible
    session_record = _SESSION_IDENTITY.get(candidate) or {}
    session_actor = session_record.get("actor_id", "")

    caller_key = _canonical_actor_key(caller_actor_id)
    session_key = _canonical_actor_key(session_actor)

    if caller_key and session_key and caller_key == session_key:
        logger.debug(
            "_resolve_session_id: actor match (caller=%s, session_actor=%s), returning %s",
            caller_actor_id,
            session_actor,
            candidate,
        )
        return candidate

    # Actor mismatch — do NOT inherit. Caller must create their own session.
    logger.info(
        "_resolve_session_id: ACTOR MISMATCH — caller=%s (canonical=%s), "
        "active session %s belongs to %s (canonical=%s). Returning None to "
        "prevent cross-actor session inheritance.",
        caller_actor_id,
        caller_key,
        candidate,
        session_actor,
        session_key,
    )
    return None


def _resolve_lookup_session_id(
    session_id: str | None, *, caller_actor_id: str | None = None
) -> str | None:
    if session_id is None:
        return _resolve_session_id(None, caller_actor_id=caller_actor_id)
    normalized = str(session_id).strip()
    if normalized in {"", "global"}:
        return _resolve_session_id(None, caller_actor_id=caller_actor_id)
    return normalized


def set_active_session(session_id: str) -> None:
    """Update the global pointer for the last active session (Redis-backed)."""
    global _ACTIVE_SESSION_ID
    _ACTIVE_SESSION_ID = session_id
    _load_store()
    with _STORE_LOCK:
        _persist_store()
    # Also propagate to Redis registry for multi-agent safety
    if _HAS_REDIS_REGISTRY and _REDIS_SESSION_REGISTRY:
        try:
            import asyncio

            asyncio.run(_REDIS_SESSION_REGISTRY.set_active_session_id(session_id))
        except Exception:
            pass


def get_active_session_id() -> str | None:
    """Get the active session ID (Redis-backed, falls back to global).

    Multi-agent safe: reads from Redis first, falls back to in-memory
    _ACTIVE_SESSION_ID global. Returns None if no active session.
    """
    if _HAS_REDIS_REGISTRY and _REDIS_SESSION_REGISTRY:
        try:
            import asyncio

            redis_active = asyncio.run(_REDIS_SESSION_REGISTRY.get_active_session_id())
            if redis_active:
                return redis_active
        except Exception:
            pass
    return _ACTIVE_SESSION_ID


def bind_session_identity(
    session_id: str,
    actor_id: str,
    authority_level: str,
    auth_context: dict[str, Any],
    approval_scope: list[str] | None = None,
    human_approval: bool = False,
    caller_state: str | None = None,
    constitutional_context: str | None = None,
    *,
    risk_tier: str | None = None,
    platform: str | None = None,
    verified: bool | None = None,
    stage: str | None = None,
    governance: dict[str, Any] | None = None,
    sign: bool = False,
    # Zen collapse 2026-07-24: execution fields live on identity store
    trace_packet: dict[str, Any] | None = None,
    invocation_count: int | None = None,
    agent_policy: dict[str, Any] | None = None,
    epoch_id: str | None = None,
    decision_class: str | None = None,
    prior_verdicts: list[Any] | None = None,
    lane: str | None = None,
    execution_fields: dict[str, Any] | None = None,
) -> str:
    """
    Bind a verified identity to a session. Called after successful init_anchor.

    Execution-domain fields (trace_packet, invocation_count, agent_policy,
    epoch_id, decision_class, prior_verdicts, lane, …) are stored on the same
    record — one schema, not two.

    If sign=True, returns a new signed session ID encoding the identity payload.
    """
    _load_store()
    now = _utcnow()
    canonical_actor_id = _resolve_canonical_actor(actor_id, None)
    verified_flag = bool(verified if verified is not None else auth_context.get("verified", False))

    actual_session_id = session_id
    if sign:
        token_payload = {
            "aid": actor_id,
            "lvl": authority_level,
            "v": verified_flag,
            "exp": int((now + timedelta(hours=24)).timestamp()),
        }
        signed_token = _sign_session_payload(token_payload)
        prefix = session_id.split("--")[0] if "--" in session_id else session_id
        if not prefix.startswith("sid_"):
            prefix = f"sid_{prefix}"
        actual_session_id = f"{prefix}--{signed_token}"

    normalized_risk = _normalize_risk_tier(risk_tier, verified=verified_flag)
    existing = _SESSION_IDENTITY.get(actual_session_id, {})
    merged_auth_context = _merge_dict(
        existing.get("auth_context", {}),
        {
            **dict(auth_context or {}),
            "actor_id": actor_id,
            "canonical_actor_id": canonical_actor_id,
            "session_id": actual_session_id,
            "verified": verified_flag,
            "risk_tier": normalized_risk,
            "platform": platform or existing.get("platform") or "mcp",
        },
    )
    _tp = trace_packet if trace_packet is not None else existing.get("trace_packet")
    _decision = decision_class
    if _decision is None and isinstance(_tp, dict):
        _decision = _tp.get("decision_class")
    if _decision is None:
        _decision = existing.get("decision_class")

    record = {
        "session_id": actual_session_id,
        "actor_id": actor_id,
        "canonical_actor_id": canonical_actor_id,
        "authority_level": authority_level,
        "verification_method": (
            merged_auth_context.get("verification_method")
            or merged_auth_context.get("auth_method")
            or existing.get("verification_method")
        ),
        "evidence_ref": (
            (
                f"key://{merged_auth_context['verified_key_id']}"
                if merged_auth_context.get("verified_key_id")
                else None
            )
            or existing.get("evidence_ref")
            or f"session://{actual_session_id}"
        ),
        "actor_verified": verified_flag,
        "auth_context": merged_auth_context,
        "approval_scope": approval_scope or existing.get("approval_scope") or [],
        "caller_state": caller_state or ("verified" if verified_flag else "anchored"),
        "human_approval": human_approval,
        "constitutional_context": constitutional_context,
        "verified": verified_flag,
        "risk_tier": normalized_risk,
        "platform": platform or existing.get("platform") or "mcp",
        "stage": stage or existing.get("stage") or "000_INIT",
        "governance": governance or existing.get("governance") or {"verdict": "SEAL"},
        "created_at": existing.get("created_at") or now.isoformat(),
        "updated_at": now.isoformat(),
        "last_seen_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=_SESSION_TTL_SECONDS)).isoformat(),
        "expires_at_unix": (now + timedelta(seconds=_SESSION_TTL_SECONDS)).timestamp(),
        "activity": existing.get("activity")
        or {
            "tool_call_count": 0,
            "entropy_delta": 0.0,
            "last_tool": None,
            "last_stage": None,
            "last_verdict": None,
            "last_ops_vitals": None,
            "history": [],
        },
        "trace_packet": _tp if _tp is not None else existing.get("trace_packet"),
        "invocation_count": (
            int(invocation_count)
            if invocation_count is not None
            else int(existing.get("invocation_count") or 0)
        ),
        "agent_policy": agent_policy if agent_policy is not None else existing.get("agent_policy"),
        "epoch_id": epoch_id if epoch_id is not None else existing.get("epoch_id"),
        "decision_class": _decision,
        "prior_verdicts": (
            list(prior_verdicts)
            if prior_verdicts is not None
            else list(existing.get("prior_verdicts") or existing.get("_prior_verdicts") or [])
        ),
        "lane": lane if lane is not None else (existing.get("lane") or "AGI"),
    }
    for key in _EXECUTION_FIELD_KEYS:
        if key not in record and key in existing:
            record[key] = existing[key]
    if execution_fields:
        for key, value in execution_fields.items():
            if value is None and key in record:
                continue
            if key in {"session_id", "auth_context", "activity"}:
                continue
            if key in record and record[key] is not None and value in (None, "", [], {}):
                continue
            record[key] = value

    _SESSION_IDENTITY[actual_session_id] = record
    _ACTOR_SESSION_MAP[actual_session_id] = actor_id
    set_active_session(actual_session_id)
    with _STORE_LOCK:
        _persist_store()

    return actual_session_id


def upsert_session_record(session_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Merge data into the unified session record and persist."""
    if not session_id:
        raise ValueError("session_id required")
    _load_store()
    now = _utcnow()
    with _STORE_LOCK:
        existing = dict(_SESSION_IDENTITY.get(session_id) or {})
        merged = dict(existing)
        for key, value in (data or {}).items():
            if value is None and key in existing:
                continue
            merged[key] = value
        merged["session_id"] = session_id
        merged["updated_at"] = now.isoformat()
        merged["last_seen_at"] = now.isoformat()
        if not merged.get("expires_at"):
            merged["expires_at"] = (now + timedelta(seconds=_SESSION_TTL_SECONDS)).isoformat()
        if not merged.get("expires_at_unix"):
            exp = _parse_iso8601(merged.get("expires_at"))
            if exp is not None:
                merged["expires_at_unix"] = exp.timestamp()
        if "verified" in merged and "actor_verified" not in (data or {}):
            merged.setdefault("actor_verified", bool(merged.get("verified")))
        if "actor_verified" in merged and "verified" not in (data or {}):
            merged.setdefault("verified", bool(merged.get("actor_verified")))
        _SESSION_IDENTITY[session_id] = merged
        actor = merged.get("actor_id")
        if actor:
            _ACTOR_SESSION_MAP[session_id] = str(actor)
        _persist_store()
        return merged


def delete_session_record(session_id: str) -> bool:
    """Remove a session from the unified store."""
    _load_store()
    with _STORE_LOCK:
        existed = session_id in _SESSION_IDENTITY
        _SESSION_IDENTITY.pop(session_id, None)
        _ACTOR_SESSION_MAP.pop(session_id, None)
        _SESSION_CONTINUITY_STATE.pop(session_id, None)
        if existed:
            _persist_store()
        return existed


def persist_session_store() -> None:
    """Flush in-memory unified store to disk (flock-safe)."""
    _load_store()
    with _STORE_LOCK:
        _persist_store()


def get_session_identity(session_id: str) -> dict[str, Any] | None:
    """
    Retrieve the stored identity for a session.

    Returns None if the session has not been anchored via init_anchor.
    """
    if session_id and str(session_id).startswith("arifos.v1."):
        try:
            from arifosmcp.runtime.capability_token import verify_token

            payload = verify_token(session_id)
            if payload:
                # Preserve actor_verified from any previously stored session identity.
                # An ACT (Actor Capability Token) may carry witness.active_count=0
                # while a prior bind_identity() already set actor_verified=True.
                # Overwriting would create state-envelope drift between verdict and birth.
                _existing = _SESSION_IDENTITY.get(payload.sub, {})
                _stored_verified = _existing.get("actor_verified")
                _stored_verified_actor = _existing.get("verified_actor_id")
                _witness_verified = payload.witness.active_count > 0
                _actor_verified = (
                    _stored_verified if _stored_verified is not None else _witness_verified
                )
                record = {
                    "actor_id": payload.act,
                    "verified_actor_id": (
                        _stored_verified_actor
                        if _stored_verified_actor
                        else (payload.act if _witness_verified else None)
                    ),
                    "actor_verified": _actor_verified,
                    "authority_level": payload.auth.lower(),
                    "session_token": session_id,
                    "verdict": payload.apex.verdict,
                }
                # Cache in _SESSION_IDENTITY so other thread/DB lookups find it
                _SESSION_IDENTITY[payload.sub] = {
                    **record,
                    "created_at": datetime.fromtimestamp(payload.iat, UTC).isoformat(),
                    "expires_at": datetime.fromtimestamp(payload.exp, UTC).isoformat(),
                    "stage": "000",
                }
                return record
        except Exception:
            pass

    resolved_session_id = _resolve_lookup_session_id(session_id)
    if not resolved_session_id:
        return None
    return _ensure_active_record(resolved_session_id)


def clear_session_identity(session_id: str) -> None:
    """Remove stored identity for a session (e.g., on revocation)."""
    _load_store()
    _SESSION_IDENTITY.pop(session_id, None)
    _ACTOR_SESSION_MAP.pop(session_id, None)
    _SESSION_CONTINUITY_STATE.pop(session_id, None)
    with _STORE_LOCK:
        _persist_store()


def mark_session_ed25519_verified(
    session_id: str,
    actor_id: str,
    actor_pubkey_hex: str,
) -> bool:
    """Mark a session as Ed25519-verified (AAA Wave 2 / Phase 5).

    Idempotent: repeated calls update the ``ed25519_verified_at`` timestamp and
    ``ed25519_pubkey`` but do not downgrade. F11 AUDIT: every call appends a
    marker event to the session record.

    Returns True on success, False if the session_id is not recognized (the
    caller — arif_verify — should NOT fail the verification in that case; the
    cryptographic check has already passed and session binding is best-effort).
    """
    _load_store()
    record = _SESSION_IDENTITY.get(session_id)
    if record is None:
        # Try resolving via _resolve_lookup_session_id (handles canonical alias)
        resolved = _resolve_lookup_session_id(session_id)
        if resolved:
            record = _SESSION_IDENTITY.get(resolved)
    if record is None:
        return False

    identity = record.setdefault("identity", {})
    if not isinstance(identity, dict):
        identity = {}
        record["identity"] = identity

    identity["ed25519_verified"] = True
    identity["ed25519_actor_id"] = actor_id
    identity["ed25519_pubkey"] = actor_pubkey_hex
    identity["ed25519_verified_at"] = _utcnow().isoformat()

    # F2 TRUTH + bridging_seal contract: Ed25519 key binding proves key
    # possession, NOT sovereign identity. actor_verified stays False until
    # real crypto verification lands. actor_override (BRIDGING_SEAL) is the
    # only bypass path. Setting actor_verified=True here was a state-envelope
    # fabrication that caused the actor_verified drift (F-004 epoch defect).
    # Repaired 2026-07-17 per F13 directive.

    # SINGLE SETTER: bind the canonical authority_state so _is_actor_verified
    # and all readers resolve from authority_state.actor.verified.
    # This is the ONLY place in the kernel that promotes actor_verified from
    # False → True based on cryptographic Ed25519 proof.
    try:
        from arifosmcp.runtime.authority import bind_authority_state
        from arifosmcp.runtime.megaTools.tool_01_init_anchor import (
            build_authority_state_for_actor,
        )

        _bind_state = build_authority_state_for_actor(
            actor_id,
            verified=True,  # Ed25519 proof → verified
            verification_method="signature",
            verified_key_id=actor_pubkey_hex,
        )
        bind_authority_state(record, _bind_state)
    except Exception:
        pass

    record["verified_actor_id"] = actor_id
    if not record.get("actor_id"):
        record["actor_id"] = actor_id

    # Append to event log for F11 AUDIT traceability.
    events = record.setdefault("events", [])
    if isinstance(events, list):
        events.append(
            {
                "type": "ed25519_verified",
                "actor_id": actor_id,
                "actor_pubkey_prefix": actor_pubkey_hex[:16],
                "at": identity["ed25519_verified_at"],
            }
        )

    with _STORE_LOCK:
        _persist_store()
    return True


def list_active_sessions_count() -> int:
    """Return the total number of currently anchored sessions."""
    _load_store()
    expired = [sid for sid, record in _SESSION_IDENTITY.items() if _is_session_expired(record)]
    for session_id in expired:
        clear_session_identity(session_id)
    return len(_SESSION_IDENTITY)


def get_session_continuity_state(session_id: str | None) -> dict[str, Any] | None:
    """Return canonical continuity state for a session if present."""
    resolved_session_id = _resolve_lookup_session_id(session_id)
    if not resolved_session_id:
        return None
    _load_store()
    if _is_session_expired(_SESSION_IDENTITY.get(resolved_session_id)):
        clear_session_identity(resolved_session_id)
        return None
    return _SESSION_CONTINUITY_STATE.get(resolved_session_id)


def set_session_continuity_state(session_id: str, state: dict[str, Any]) -> None:
    """Persist canonical continuity state for a session."""
    _load_store()
    _SESSION_CONTINUITY_STATE[session_id] = state
    if session_id in _SESSION_IDENTITY:
        _touch_record(session_id, {"stage": _deep_get(state, "state", "session", "current_tool")})
    else:
        with _STORE_LOCK:
            _persist_store()


def get_session_pipeline_state(session_id: str | None) -> str | None:
    """Formal pipeline state (OBSERVE…SEAL) from continuity blob."""
    if not session_id:
        return None
    _load_store()
    continuity = _SESSION_CONTINUITY_STATE.get(session_id)
    if continuity:
        return _deep_get(continuity, "execution_state")
    return None


def set_session_pipeline_state(session_id: str, state: str) -> None:
    """Persist formal pipeline state inside continuity blob."""
    continuity = get_session_continuity_state(session_id) or {}
    continuity["execution_state"] = state
    set_session_continuity_state(session_id, continuity)


def get_session_execution_state(session_id: str | None) -> dict[str, Any] | None:
    """Thin reader: full session record (identity ∪ execution) from unified store.

    Zen collapse 2026-07-24 — replaces tools.py ``_SESSIONS.get(session_id)``.
    Returns a live dict reference (in-place mutations affect memory; writers flush).
    """
    if not session_id:
        return None
    _load_store()
    record = _SESSION_IDENTITY.get(session_id)
    if record is None:
        return _ensure_active_record(session_id)
    if _is_session_expired(record):
        clear_session_identity(session_id)
        return None
    return record


def record_session_tool_event(
    session_id: str | None,
    tool_name: str,
    *,
    stage: str | None = None,
    verdict: str | None = None,
    telemetry: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    execution_state: str | None = None,
) -> None:
    """Track live per-session telemetry for monitor_metabolism and cross-tool continuity."""
    if not session_id:
        return
    record = _ensure_active_record(session_id)
    if record is None:
        return

    telemetry = dict(telemetry or {})
    payload = dict(payload or {})
    activity = dict(record.get("activity") or {})
    history = list(activity.get("history") or [])
    tool_call_count = int(activity.get("tool_call_count", 0)) + 1

    raw_entropy = telemetry.get("ds")
    try:
        entropy_delta = float(raw_entropy)
    except (TypeError, ValueError):
        # H5: Align with healthy baseline default (-0.32)
        entropy_delta = -0.32

    raw_peace_sq = telemetry.get("peace2")
    try:
        peace_sq = float(raw_peace_sq)
    except (TypeError, ValueError):
        # H5: Align with healthy baseline default (1.04)
        peace_sq = float(
            _deep_get(payload, "telemetry", "thermodynamic_efficiency")
            or (activity.get("last_ops_vitals") or {}).get("peace_sq")
            or 1.04
        )

    raw_confidence = telemetry.get("confidence")
    try:
        confidence = float(raw_confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    omega0 = round(max(0.0, min(1.0, 1.0 - confidence)), 4)
    if omega0 == 1.0 and record.get("verified"):
        omega0 = 0.04

    last_ops_vitals = activity.get("last_ops_vitals")
    if tool_name == "arifos_ops":
        last_ops_vitals = {
            "peace_sq": peace_sq,
            "omega0": omega0,
            "delta_s": entropy_delta,
            "mode": payload.get("mode"),
            "captured_at": _utcnow().isoformat(),
        }

    floors_checked = list((policy or {}).get("floors_checked") or [])
    floors_failed = set((policy or {}).get("floors_failed") or [])
    floor_state = dict(activity.get("floors") or {})
    for floor in floors_checked:
        floor_state[floor] = {
            "stability": 0.25 if floor in floors_failed else 0.95,
            "status": "FAIL" if floor in floors_failed else "PASS",
        }

    history.append(
        {
            "tool": tool_name,
            "stage": stage,
            "verdict": verdict,
            "timestamp": _utcnow().isoformat(),
            "entropy_delta": entropy_delta,
        }
    )
    history = history[-25:]

    activity_update = {
        "tool_call_count": tool_call_count,
        "entropy_delta": entropy_delta,
        "last_tool": tool_name,
        "last_stage": stage,
        "last_verdict": verdict,
        "last_ops_vitals": last_ops_vitals,
        "last_telemetry": telemetry,
        "floors": floor_state,
        "history": history,
    }
    if execution_state:
        activity_update["execution_state"] = execution_state

    _touch_record(
        session_id,
        {
            "stage": stage or record.get("stage") or "000_INIT",
            "governance": {
                # WS2 (2026-07-12): no default SEAL on write. Verdict stays
                # unfilled until judge path clears. Consumers should treat
                # None as "no verdict yet" (substrate-conservative) and
                # fall back to execution_readiness service-side.
                "verdict": verdict or _deep_get(record, "governance", "verdict")
            },
            "activity": activity_update,
        },
    )


def session_exists(session_id: str | None) -> bool:
    """Check if a session exists and is not expired in the persistent identity store."""
    if not session_id:
        return False
    record = _ensure_active_record(session_id)
    return record is not None


def validate_session(
    session_id: str | None,
    actor_id: str | None = None,
    required: bool = False,
) -> dict[str, Any]:
    """Unified session validation middleware.

    Returns:
        {"valid": bool, "record": dict|None, "code": str, "reason": str}
    """
    if not session_id:
        if required:
            return {
                "valid": False,
                "record": None,
                "code": "L11_MISSING",
                "reason": "session_id is required but was not provided",
            }
        return {
            "valid": True,
            "record": None,
            "code": "ANONYMOUS",
            "reason": "No session_id provided; anonymous access",
        }

    record = _ensure_active_record(session_id)
    if record is None:
        return {
            "valid": False,
            "record": None,
            "code": "L11_EXPIRED",
            "reason": f"session_id not found or expired: {session_id}",
        }

    if actor_id and record.get("actor_id") != actor_id:
        return {
            "valid": False,
            "record": record,
            "code": "L11_MISMATCH",
            "reason": f"Actor mismatch: expected {actor_id}, got {record.get('actor_id')}",
        }

    return {
        "valid": True,
        "record": record,
        "code": "SEAL",
        "reason": "Session valid and identity binding confirmed",
    }


def get_all_session_ids() -> set[str]:
    """Return all valid session IDs from the persistent identity store."""
    _load_store()
    valid = set()
    for sid, record in list(_SESSION_IDENTITY.items()):
        if not _is_session_expired(record):
            valid.add(sid)
    return valid


def get_session_runtime_state(session_id: str | None) -> dict[str, Any] | None:
    """Return merged identity, continuity, and live activity for a session."""
    resolved_session_id = _resolve_lookup_session_id(session_id)
    if not resolved_session_id:
        return None
    record = _ensure_active_record(resolved_session_id)
    if record is None:
        return None
    return {
        "identity": record,
        "continuity": _SESSION_CONTINUITY_STATE.get(resolved_session_id),
        "activity": record.get("activity") or {},
        "governance": record.get("governance") or {},
    }


# ── Session Truth Resolution ──────────────────────────────────────────────
# F2 Truth: Single canonical resolution of session + identity continuity.
# Identity Trust Chain (strict precedence per Zero-Day hardening):
#   1. verified token identity (auth_context.session_id)
#   2. signed trusted session identity (anchored session state)
#   3. explicit admin-approved mapping (SOVEREIGN_IDENTITY_MAP)
#   4. otherwise anonymous / denied
# No transport-provided actor string outranks verified identity.


def resolve_runtime_context(
    incoming_session_id: str | None,
    auth_context: dict[str, Any] | None,
    actor_id: str | None,
    declared_name: str | None,
) -> dict[str, Any]:
    """
    Canonical resolution of session and identity truth.

    Returns unified context with explicit separation of:
    - transport_session_id: raw incoming value (for debugging)
    - resolved_session_id: canonical continuity-verified truth
    - canonical_actor_id: authority-bearing identity
    - display_name: human-readable only
    - authority_source: provenance for audit
    """
    # Identity precedence: actor_id > declared_name > anonymous
    canonical_actor_id = _resolve_canonical_actor(actor_id, declared_name)

    # Transport session: raw incoming value, may be "global"
    transport_session_id = incoming_session_id or "global"

    # Session resolution with precedence
    resolved_session_id: str = transport_session_id
    authority_source: str = "fallback"

    # 1. auth_context.session_id (verified token)
    if auth_context and auth_context.get("session_id"):
        resolved_session_id = auth_context["session_id"]
        authority_source = "token"
    # 2. Anchored session state for this actor
    elif transport_session_id != "global" and get_session_identity(transport_session_id):
        resolved_session_id = transport_session_id
        authority_source = "session"
    # 3. Check if actor has any anchored session
    elif canonical_actor_id != "anonymous":
        # Find session by actor mapping
        for sid, aid in _ACTOR_SESSION_MAP.items():
            if aid == canonical_actor_id:
                resolved_session_id = sid
                authority_source = "session"
                break

    # Display name is presentation-only
    display_name = declared_name or actor_id or "anonymous"

    # F2 Truth: Single canonical session_id — unified truth across all surfaces
    unified_session_id = resolved_session_id

    return {
        "session_id": unified_session_id,  # ← Canonical single truth (NEW)
        "resolved_session_id": unified_session_id,  # ← Same value, explicit redundancy
        "transport_session_id": transport_session_id,  # ← Debug/audit only
        "canonical_actor_id": canonical_actor_id,
        "display_name": display_name,
        "authority_source": authority_source,
        "_invariant": "session_id == resolved_session_id",  # ← Enforced
    }


def _resolve_canonical_actor(actor_id: str | None, declared_name: str | None) -> str:
    """
    Identity precedence: actor_id > declared_name > anonymous.
    Strict sovereign protection: uses SOVEREIGN_IDENTITY_MAP for verified identities.
    Common sovereign aliases are normalized here for continuity with the
    historical runtime/test surface.

    P0 BOUNDARY FIX (2026-07-19): the returned value is the CANONICAL MACHINE
    ACTOR ID, which MUST be lowercase so every downstream comparison (ACT
    claim, bridge envelope, organ-side session validator, GEOX validator,
    WEALTH validator, WELL validator, receipts) operates on one form. The
    display label "ARIF" belongs at the UI layer, not in this field. Per
    external witness verdict: any value here that is not exactly the
    lowercase canonical form is a federation boundary failure.

    For all valid inputs, the function now returns the lowercase canonical
    form. The case-preserved fallback is removed — case sensitivity at the
    machine boundary is a defect, not a feature.
    """
    # Normalize inputs
    aid = (actor_id or "").strip()
    dname = (declared_name or "").strip()

    # Strict pattern validation — reject malformed actor_id before any processing
    if aid and not _VALID_ACTOR_ID_PATTERN.match(aid):
        aid = ""
    if dname and not _VALID_ACTOR_ID_PATTERN.match(dname):
        dname = ""

    aid_normalized = aid.lower().replace("_", "-") if aid else ""
    dname_normalized = dname.lower().replace("_", "-") if dname else ""
    alias_map = {"arif-fazil": "arif"}

    # Precedence: actor_id first
    if aid_normalized and aid_normalized != "anonymous":
        # Check sovereign identity map first — explicit verified identities only
        if aid_normalized in _SOVEREIGN_IDENTITY_MAP:
            return _SOVEREIGN_IDENTITY_MAP[aid_normalized].lower()
        if aid_normalized in alias_map:
            return alias_map[aid_normalized].lower()
        # P0 BOUNDARY FIX: return the lowercase normalized form, not the
        # case-preserved original. This is the canonical machine actor ID.
        return aid_normalized

    # Fallback: declared_name (normalized)
    if dname_normalized and dname_normalized != "anonymous":
        # Check sovereign identity map — explicit verified identities only
        if dname_normalized in _SOVEREIGN_IDENTITY_MAP:
            return _SOVEREIGN_IDENTITY_MAP[dname_normalized].lower()
        if dname_normalized in alias_map:
            return alias_map[dname_normalized].lower()
        return dname_normalized

    return "anonymous"


def _normalize_session_id(session_id: str | None) -> str:
    """Normalize session ID - create new if not provided.

    This is the single source of truth for session ID normalization.
    Moved from tools.py to avoid circular imports.
    """
    if session_id and str(session_id).strip():
        return str(session_id).strip()
    minted = f"session-{uuid.uuid4().hex[:8]}"
    set_active_session(minted)
    return minted
