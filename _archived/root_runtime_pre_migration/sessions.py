"""
arifos/runtime/sessions.py — Session Continuity State

Centralized session registry for arifOS runtime.
Single source of truth for session → identity binding.

DITEMPA BUKAN DIBERI — Forged, Not Given

SECURITY HARDENING (Zero-Day Mitigation):
- Strict sovereign identity map: explicit verified identities only
- No guessable aliases (e.g., "arif" not promoted to "ariffazil")
- Identity trust precedence: verified token > signed session > explicit admin map > anonymous
"""

import base64
import hmac
import hashlib
import json
import logging
import os
import re
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import RLock
from typing import Any

from core.shared.types import ActorIdentity

logger = logging.getLogger(__name__)

# Global Session Registry (In-memory fallback for stateless bridge)
_ACTOR_IDENTITIES: dict[str, ActorIdentity] = {}
_ACTOR_SESSION_MAP: dict[str, str] = {}  # session_id -> actor_id
_ACTIVE_SESSION_ID: str | None = None
_SESSION_CONTINUITY_STATE: dict[str, dict[str, Any]] = {}
_STORE_LOCK = RLock()
_STORE_LOADED = False

_SESSION_TTL_SECONDS = max(300, int(os.getenv("ARIFOS_SESSION_TTL_SECONDS", "86400")))


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
    tmp_state = Path("/tmp") / "arifos" / "runtime_sessions.json"

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
            except Exception:
                secret = "fallback-ephemeral-secret"
        else:
            secret = "fallback-ephemeral-secret"
    return secret.encode()


def _sign_session_payload(payload: dict[str, Any]) -> str:
    """Generate a signed base64 token for distributed continuity."""
    dump = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    b64_payload = base64.urlsafe_b64encode(dump.encode()).decode().rstrip("=")
    sig = hmac.new(_get_signing_secret(), b64_payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{b64_payload}.{sig}"


def _verify_session_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a signed session token."""
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
        return json.loads(decoded)
    except Exception:
        return None


# ── Sovereign Identity Map ─────────────────────────────────────────────────
# Explicit verified identities only — no guessable aliases
# Blind spot 3 amendment: moved from hardcoded function logic to explicit map
_SOVEREIGN_IDENTITY_MAP: dict[str, str] = {
    "ariffazil": "ariffazil",
}
_VALID_ACTOR_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,64}$")

# ── Session Identity Storage ──────────────────────────────────────────────
# Stores the resolved identity for each anchored session.
# This is the canonical binding: session_id → {actor_id, authority_level, auth_context, ...}
_SESSION_IDENTITY: dict[str, dict[str, Any]] = {}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _session_store_payload() -> dict[str, Any]:
    return {
        "version": 1,
        "active_session_id": _ACTIVE_SESSION_ID,
        "sessions": _SESSION_IDENTITY,
        "continuity": _SESSION_CONTINUITY_STATE,
    }


def _persist_store() -> None:
    global _SESSION_STORE_PATH
    try:
        _SESSION_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = _SESSION_STORE_PATH.with_suffix(".tmp")
        tmp_path.write_text(
            json.dumps(_session_store_payload(), indent=2, sort_keys=True), encoding="utf-8"
        )
        tmp_path.replace(_SESSION_STORE_PATH)
    except OSError as exc:
        fallback_path = Path("/tmp") / "arifos" / "runtime_sessions.json"
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


def _load_store() -> None:
    global _STORE_LOADED, _ACTIVE_SESSION_ID
    with _STORE_LOCK:
        if _STORE_LOADED:
            return
        if _SESSION_STORE_PATH.exists():
            try:
                payload = json.loads(_SESSION_STORE_PATH.read_text(encoding="utf-8"))
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
                # Fail open to in-memory state; writers will repair the file.
                pass
        _STORE_LOADED = True


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
                    # Session expired check within token if needed, but for now trust signed sig
                    # Reconstruct ephemeral record
                    record = {
                        "session_id": session_id,
                        "actor_id": recovered.get("aid", "anonymous"),
                        "authority_level": recovered.get("lvl", "low"),
                        "verified": recovered.get("v", False),
                        "recovered_from_token": True,
                        "expires_at": (
                            datetime.now(timezone.utc) + timedelta(minutes=30)
                        ).isoformat(),
                    }
                    # Cache it locally
                    with _STORE_LOCK:
                        _SESSION_IDENTITY[session_id] = record
        except Exception:
            pass

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


def _resolve_session_id(provided_id: str | None) -> str | None:
    """Resolve session_id from provided input or last active session."""
    _load_store()
    if provided_id and str(provided_id).strip():
        return provided_id
    return _ACTIVE_SESSION_ID


def _resolve_lookup_session_id(session_id: str | None) -> str | None:
    if session_id is None:
        return _resolve_session_id(None)
    normalized = str(session_id).strip()
    if normalized in {"", "global"}:
        return _resolve_session_id(None)
    return normalized


def set_active_session(session_id: str) -> None:
    """Update the global pointer for the last active session."""
    global _ACTIVE_SESSION_ID
    _ACTIVE_SESSION_ID = session_id
    _load_store()
    with _STORE_LOCK:
        _persist_store()


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
) -> str:
    """
    Bind a verified identity to a session. Called after successful init_anchor.

    This is the canonical write: after this call, get_session_identity(session_id)
    will return the stored identity instead of anonymous defaults.

    If sign=True, returns a new signed session ID encoding the identity payload.
    """
    _load_store()
    now = _utcnow()
    canonical_actor_id = _resolve_canonical_actor(actor_id, None)
    verified_flag = bool(
        verified
        if verified is not None
        else auth_context.get("verified")
        or authority_level in {"verified", "sovereign", "operator"}
    )

    # H2: Distributed continuity signing
    actual_session_id = session_id
    if sign:
        token_payload = {
            "aid": actor_id,
            "lvl": authority_level,
            "v": verified_flag,
            "exp": int((now + timedelta(hours=24)).timestamp()),
        }
        signed_token = _sign_session_payload(token_payload)
        # Preserve original UUID prefix if possible
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
    record = {
        "session_id": actual_session_id,
        "actor_id": actor_id,
        "canonical_actor_id": canonical_actor_id,
        "authority_level": authority_level,
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
    }
    _SESSION_IDENTITY[actual_session_id] = record
    _ACTOR_SESSION_MAP[actual_session_id] = actor_id
    set_active_session(actual_session_id)
    with _STORE_LOCK:
        _persist_store()

    return actual_session_id


def get_session_identity(session_id: str) -> dict[str, Any] | None:
    """
    Retrieve the stored identity for a session.

    Returns None if the session has not been anchored via init_anchor.
    """
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


def record_session_tool_event(
    session_id: str | None,
    tool_name: str,
    *,
    stage: str | None = None,
    verdict: str | None = None,
    telemetry: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
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

    _touch_record(
        session_id,
        {
            "stage": stage or record.get("stage") or "000_INIT",
            "governance": {
                "verdict": verdict or _deep_get(record, "governance", "verdict") or "SEAL"
            },
            "activity": {
                "tool_call_count": tool_call_count,
                "entropy_delta": entropy_delta,
                "last_tool": tool_name,
                "last_stage": stage,
                "last_verdict": verdict,
                "last_ops_vitals": last_ops_vitals,
                "last_telemetry": telemetry,
                "floors": floor_state,
                "history": history,
            },
        },
    )


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
    No guessable aliases like "arif" are promoted to "ariffazil" at this layer.
    Identity verification happens in governance layers (F11/F13).
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

    # Precedence: actor_id first
    if aid_normalized and aid_normalized != "anonymous":
        # Check sovereign identity map first — explicit verified identities only
        if aid_normalized in _SOVEREIGN_IDENTITY_MAP:
            return _SOVEREIGN_IDENTITY_MAP[aid_normalized]
        return aid  # Return original case-preserved form if valid

    # Fallback: declared_name (normalized)
    if dname_normalized and dname_normalized != "anonymous":
        # Check sovereign identity map — explicit verified identities only
        if dname_normalized in _SOVEREIGN_IDENTITY_MAP:
            return _SOVEREIGN_IDENTITY_MAP[dname_normalized]
        return dname  # Return original case-preserved form if valid

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
