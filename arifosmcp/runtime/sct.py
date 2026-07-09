"""
Session Capability Token (SCT) — Spine P0 (inhabit, don't interrogate)

State rides with a signed token; the store is optional cache only.

Wire format (canonical — only birth path):
    sct_v1.<base64url(payload_json)>.<hmac_sha256_hex>

Legacy verify-only (never mint):
    arifos.v1.<b64>.<b64sig>  → normalized into sct claims

Merged from capability_token.py (2026-07-09 Spine P0):
  derive_verbs, apply_caveats, compute_authority_delta, derive_authority (measured only)

Spec: /root/A-FORGE/forge_work/2026-07-09/SESSION-CAPABILITY-TOKEN-SPEC.md
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SCT_PREFIX = "sct_v1"
SCT_VERSION = 1
DEFAULT_TTL_SECONDS = 3600
UNMEASURED = "UNMEASURED"

VALID_AUTH = frozenset(
    {"OBSERVE_ONLY", "LIMITED_MUTATE", "FULL", "SOVEREIGN", "OPERATOR", "ANONYMOUS"}
)

# Metabolic verbs by authority band (no arif_act — public surface uses arif_forge)
AUTHORITY_VERBS: dict[str, list[str]] = {
    "OBSERVE_ONLY": [
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_compose",
        "arif_critique",
        "arif_memory",
    ],
    "LIMITED_MUTATE": [
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_compose",
        "arif_critique",
        "arif_memory",
        "arif_judge",
        "arif_forge",
    ],
    "FULL": [
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_compose",
        "arif_critique",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_seal",
    ],
    "SOVEREIGN": [
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_compose",
        "arif_critique",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_seal",
    ],
}

_AUTH_ORDER = {"OBSERVE_ONLY": 0, "LIMITED_MUTATE": 1, "FULL": 2, "SOVEREIGN": 3}

_FALLBACK_SECRET = "fallback-ephemeral-secret"  # nosec B105 — detected + warned
_PROD_SIGNING_KEY_PATHS = (
    "/opt/arifos/app/.signing_key",
    os.path.expanduser("~/.arifos/signing_key"),
)


def _get_signing_secret() -> bytes:
    """HMAC key. Prefer ARIFOS_SESSION_SECRET; then 32-byte prod key file; warn if fallback."""
    secret = os.getenv("ARIFOS_SESSION_SECRET")
    if not secret:
        secret_file = os.getenv("ARIFOS_SESSION_SECRET_FILE")
        if secret_file and os.path.exists(secret_file):
            try:
                secret = Path(secret_file).read_text().strip()
            except OSError:
                secret = None
    if secret:
        return secret.encode() if isinstance(secret, str) else secret

    # Production 32-byte key file (merged from capability_token path)
    for path in _PROD_SIGNING_KEY_PATHS:
        try:
            p = Path(path)
            if p.is_file():
                raw = p.read_bytes()
                if len(raw) == 32:
                    return raw
                # Accept text secrets stored in that path
                text = raw.decode("utf-8", errors="ignore").strip()
                if text:
                    return text.encode()
        except OSError:
            continue

    logger.warning(
        "SCT: using fallback session secret — set ARIFOS_SESSION_SECRET in prod"
    )
    return _FALLBACK_SECRET.encode()


def derive_verbs(authority: str) -> list[str]:
    """Derive allowed_next_verbs from authority band. Never includes arif_act."""
    auth = (authority or "OBSERVE_ONLY").upper()
    verbs = list(AUTHORITY_VERBS.get(auth, AUTHORITY_VERBS["OBSERVE_ONLY"]))
    return ["arif_forge" if v == "arif_act" else v for v in verbs]


def derive_authority(
    G: float,
    C_dark: float,
    W3: float,
    profiles_ok: bool,
    witness_div: str,
    id_verified: bool,
    sig_verified: bool,
    context_score: float,
) -> tuple[str, str]:
    """
    Map *measured* APEX scalars → (authority, verdict).

    HARD RULE: call only when G/C_dark/W3 are real measurements.
    Birth with no measure stays identity band + UNMEASURED apex — do not call this.
    """
    if not id_verified:
        return ("OBSERVE_ONLY", "OBSERVE_ONLY")
    if W3 < 0.30:
        return ("OBSERVE_ONLY", "SABAR")
    if G < 0.50 or C_dark >= 0.30:
        return ("OBSERVE_ONLY", "VOID")
    if G < 0.80:
        return ("LIMITED_MUTATE", "SABAR")
    if not profiles_ok or witness_div == "NONE":
        return ("LIMITED_MUTATE", "SABAR")
    if W3 < 0.75:
        return ("LIMITED_MUTATE", "SABAR")
    if context_score < 0.50:
        return ("LIMITED_MUTATE", "SABAR")
    if sig_verified:
        return ("SOVEREIGN", "SEAL")
    return ("FULL", "SEAL")


def identity_band_authority(
    *,
    actor_verified: bool,
    signature_verified: bool = False,
    is_sovereign_principal: bool = False,
) -> str:
    """Birth authority without measured apex — identity only, no G theater."""
    if not actor_verified:
        return "OBSERVE_ONLY"
    if signature_verified and is_sovereign_principal:
        return "FULL"  # measured apex still required for SOVEREIGN theater
    return "LIMITED_MUTATE"


@dataclass
class AuthorityDelta:
    from_auth: str
    to_auth: str
    reason: str
    sufficient: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "from": self.from_auth,
            "to": self.to_auth,
            "reason": self.reason,
            "sufficient": self.sufficient,
        }


def compute_authority_delta(
    token_auth: str,
    required: str,
    tool_name: str,
) -> AuthorityDelta:
    """Explicit authority delta for every tool call (attenuation-aware)."""
    token_level = _AUTH_ORDER.get((token_auth or "").upper(), -1)
    required_level = _AUTH_ORDER.get((required or "").upper(), -1)
    sufficient = token_level >= required_level
    return AuthorityDelta(
        from_auth=token_auth or "OBSERVE_ONLY",
        to_auth=required or "OBSERVE_ONLY",
        reason=f"{tool_name} requires {required}",
        sufficient=sufficient,
    )


def apply_caveats(
    claims: dict[str, Any],
    new_caveats: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Attenuate claims only — never widen authority or verbs.
    Returns a *new* claims dict (caller must re-mint/sign).
    """
    out = dict(claims)
    current_auth = str(out.get("auth") or "OBSERVE_ONLY")
    current_level = _AUTH_ORDER.get(current_auth, 0)
    narrowed_auth = current_auth
    narrowed_verbs = list(out.get("allowed") or derive_verbs(current_auth))
    caveats = list(out.get("caveats") or [])

    for caveat in new_caveats:
        ctype = caveat.get("type")
        value = caveat.get("value")
        if ctype == "max_action_class":
            requested = str(value or "OBSERVE_ONLY").upper()
            requested_level = _AUTH_ORDER.get(requested, -1)
            if requested_level > current_level:
                raise ValueError(
                    f"Caveat attempts to WIDEN authority: {current_auth} → {requested}. "
                    "Caveats can only narrow."
                )
            narrowed_auth = requested
            allowed_for = set(AUTHORITY_VERBS.get(requested, []))
            narrowed_verbs = [v for v in narrowed_verbs if v in allowed_for]
        elif ctype == "max_verb":
            if value not in narrowed_verbs:
                raise ValueError(
                    f"Caveat references verb '{value}' not in current scope."
                )
            idx = narrowed_verbs.index(value)
            narrowed_verbs = narrowed_verbs[: idx + 1]
        elif ctype == "forbid_tool":
            if value in narrowed_verbs:
                narrowed_verbs = [v for v in narrowed_verbs if v != value]
        caveats.append(dict(caveat))

    out["auth"] = narrowed_auth
    out["allowed"] = narrowed_verbs
    out["caveats"] = caveats
    return out


def unmeasured_apex() -> dict[str, Any]:
    """Honest apex at birth — never invent G/C_dark/W3/h."""
    return {
        "G": UNMEASURED,
        "C_dark": UNMEASURED,
        "W3": UNMEASURED,
        "h": UNMEASURED,
    }


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _sign(payload_b64: str) -> str:
    return hmac.new(
        _get_signing_secret(), payload_b64.encode("ascii"), hashlib.sha256
    ).hexdigest()


def mint_sct(
    *,
    sid: str,
    actor: str,
    auth: str,
    av: bool,
    stage: str = "000",
    lane: str = "AGI",
    verdict_state: str = "OK",
    dominant_reason: str | None = None,
    allowed: list[str] | None = None,
    apex: dict[str, Any] | None = None,
    witness: dict[str, Any] | None = None,
    ttl: int = DEFAULT_TTL_SECONDS,
    kid: str = "default",
) -> tuple[str, dict[str, Any]]:
    """
    Mint a signed session capability token.

    Returns (token_string, claims_dict).
    apex values must be numbers or UNMEASURED — never fabricate scores.
    """
    now = int(time.time())
    auth_norm = (auth or "OBSERVE_ONLY").upper()
    if auth_norm not in VALID_AUTH:
        auth_norm = "OBSERVE_ONLY"

    allowed_list = list(allowed) if allowed is not None else derive_verbs(auth_norm)
    # Public surface: never leak internal alias arif_act
    allowed_list = ["arif_forge" if a == "arif_act" else a for a in allowed_list]

    apex_out = unmeasured_apex()
    if apex:
        for k in ("G", "C_dark", "W3", "h"):
            if k in apex:
                v = apex[k]
                if v == UNMEASURED or isinstance(v, (int, float)):
                    apex_out[k] = v
                # else leave UNMEASURED — refuse invented strings

    claims: dict[str, Any] = {
        "sct_v": SCT_VERSION,
        "sid": sid,
        "actor": actor or "anonymous",
        "auth": auth_norm,
        "av": bool(av),
        "stage": stage or "000",
        "lane": lane or "AGI",
        "iat": now,
        "exp": now + int(ttl),
        "ttl": int(ttl),
        "nbf": now,
        "kid": kid,
        "verdict": {
            "state": verdict_state or "OK",
            "dominant_reason": dominant_reason,
        },
        "apex": apex_out,
        "witness": witness
        or {
            "active": 1 if av else 0,
            "diversity": "PARTIAL" if av else "NONE",
        },
        "allowed": allowed_list,
    }

    dump = json.dumps(claims, sort_keys=True, separators=(",", ":"))
    payload_b64 = _b64url_encode(dump.encode("utf-8"))
    sig = _sign(payload_b64)
    token = f"{SCT_PREFIX}.{payload_b64}.{sig}"
    return token, claims


def verify_sct(
    token: str | None,
    *,
    expected_actor: str | None = None,
    now: float | None = None,
) -> dict[str, Any] | None:
    """
    Verify SCT signature + exp. Returns claims dict or None.

    Does not consult the session store.
    """
    if not token or not isinstance(token, str):
        return None

    if token.startswith("arifos.v1."):
        try:
            from arifosmcp.runtime.capability_token import verify_token
            payload = verify_token(token)
            if payload:
                claims = {
                    "sct_v": 1,
                    "sid": payload.sub,
                    "actor": payload.act,
                    "auth": payload.auth,
                    "av": payload.witness.active_count > 0,
                    "stage": "000",
                    "lane": "AGI",
                    "iat": payload.iat,
                    "exp": payload.exp,
                    "ttl": payload.exp - payload.iat,
                    "nbf": payload.iat,
                    "kid": "default",
                    "verdict": {
                        "state": payload.apex.verdict,
                        "dominant_reason": None,
                    },
                    "apex": {
                        "G": payload.apex.G,
                        "C_dark": payload.apex.C_dark,
                        "W3": payload.apex.W3,
                        "h": payload.apex.h,
                    },
                    "witness": {
                        "active": payload.witness.active_count,
                        "diversity": payload.witness.diversity,
                    },
                    "allowed": payload.verbs,
                }
                if expected_actor:
                    if claims.get("actor") != expected_actor:
                        return None
                return claims
        except Exception:
            pass
        return None

    parts = token.split(".")
    if len(parts) != 3:
        return None
    prefix, payload_b64, sig = parts
    if prefix != SCT_PREFIX:
        return None

    expected = _sign(payload_b64)
    if not hmac.compare_digest(expected, sig):
        return None

    try:
        raw = _b64url_decode(payload_b64)
        claims = json.loads(raw.decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None

    if not isinstance(claims, dict):
        return None
    if claims.get("sct_v") != SCT_VERSION:
        return None

    ts = now if now is not None else time.time()
    exp = claims.get("exp")
    if exp is not None and ts > float(exp):
        return None
    nbf = claims.get("nbf")
    if nbf is not None and ts < float(nbf):
        return None

    if expected_actor:
        claim_actor = str(claims.get("actor") or "")
        if claim_actor and claim_actor != expected_actor:
            return None

    return claims


@dataclass
class Standing:
    """Resolved agent standing for one hop — inhabit this, don't re-earn."""

    valid: bool
    source: str  # sct | store | ephemeral | deny
    reason: str
    claims: dict[str, Any] = field(default_factory=dict)
    session_token: str | None = None
    session_id: str | None = None
    actor_id: str | None = None
    authority: str = "OBSERVE_ONLY"
    actor_verified: bool = False
    stage: str = "000"
    allowed: list[str] = field(default_factory=list)
    apex: dict[str, Any] = field(default_factory=unmeasured_apex)
    authority_delta: dict[str, Any] | None = None
    expired: bool = False

    def as_session_dict(self) -> dict[str, Any]:
        """Shape compatible with legacy validate_session()['session']."""
        return {
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "actor_verified": self.actor_verified,
            "authority": self.authority,
            "stage": self.stage,
            "lane": self.claims.get("lane", "AGI"),
            "allowed_next_verbs": list(self.allowed),
            "sct_source": self.source,
            "apex": dict(self.apex),
        }

    def as_auth_dict(self) -> dict[str, Any]:
        """Shape compatible with legacy validate_session() return."""
        return {
            "valid": self.valid,
            "session": self.as_session_dict() if self.valid else None,
            "reason": self.reason,
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "session_token": self.session_token,
            "authority": self.authority,
            "actor_verified": self.actor_verified,
            "source": self.source,
            "expired": self.expired,
            "apex_scalars": dict(self.apex),
            "authority_delta": self.authority_delta,
            "claims": dict(self.claims) if self.claims else {},
        }


def _claims_to_standing(
    claims: dict[str, Any],
    token: str,
    source: str,
    reason: str,
) -> Standing:
    apex = claims.get("apex") or unmeasured_apex()
    return Standing(
        valid=True,
        source=source,
        reason=reason,
        claims=claims,
        session_token=token,
        session_id=claims.get("sid"),
        actor_id=claims.get("actor"),
        authority=str(claims.get("auth") or "OBSERVE_ONLY"),
        actor_verified=bool(claims.get("av")),
        stage=str(claims.get("stage") or "000"),
        allowed=list(claims.get("allowed") or []),
        apex=dict(apex) if isinstance(apex, dict) else unmeasured_apex(),
    )


def refresh_sct_if_needed(
    claims: dict[str, Any],
    token: str,
    *,
    half_life_ratio: float = 0.5,
) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    """
    Re-mint when past half TTL so standing stays continuous.
    Returns (token, claims, authority_delta|None).
    """
    now = int(time.time())
    iat = int(claims.get("iat") or now)
    exp = int(claims.get("exp") or (now + DEFAULT_TTL_SECONDS))
    ttl = int(claims.get("ttl") or DEFAULT_TTL_SECONDS)
    remaining = exp - now
    if remaining > ttl * half_life_ratio:
        return token, claims, None

    new_token, new_claims = mint_sct(
        sid=str(claims.get("sid") or ""),
        actor=str(claims.get("actor") or "anonymous"),
        auth=str(claims.get("auth") or "OBSERVE_ONLY"),
        av=bool(claims.get("av")),
        stage=str(claims.get("stage") or "000"),
        lane=str(claims.get("lane") or "AGI"),
        verdict_state=str((claims.get("verdict") or {}).get("state") or "OK"),
        dominant_reason=(claims.get("verdict") or {}).get("dominant_reason"),
        allowed=list(claims.get("allowed") or []),
        apex=claims.get("apex") if isinstance(claims.get("apex"), dict) else None,
        witness=claims.get("witness") if isinstance(claims.get("witness"), dict) else None,
        ttl=ttl,
        kid=str(claims.get("kid") or "default"),
    )
    # Same authority — delta is null (TTL refresh only)
    return new_token, new_claims, None


def mint_from_session_record(sess: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Mint SCT from a legacy in-memory / file session row."""
    sid = str(sess.get("session_id") or sess.get("sid") or "")
    actor = str(sess.get("actor_id") or sess.get("actor") or "anonymous")
    auth = str(sess.get("authority") or sess.get("authority_mode") or "OBSERVE_ONLY")
    av = bool(sess.get("actor_verified", False))
    allowed = sess.get("allowed_next_verbs")
    if not isinstance(allowed, list):
        allowed = None
    return mint_sct(
        sid=sid,
        actor=actor,
        auth=auth,
        av=av,
        stage=str(sess.get("stage") or "000"),
        lane=str(sess.get("lane") or "AGI"),
        verdict_state=str(sess.get("verdict") or auth or "OK"),
        allowed=allowed,
        apex=sess.get("apex") if isinstance(sess.get("apex"), dict) else None,
    )


def resolve_standing(
    session_token: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    *,
    tool: str | None = None,
    mode: str | None = None,
    allow_store: bool = True,
) -> Standing:
    """
    Resolve standing for one hop.

    Priority:
      1. SCT verify (no store)
      2. Store rehydrate by session_id (legacy) → mint SCT
      3. Deny

    Ephemeral observe-only is left to the tool layer (sense.py) when
    source=deny and mode is pure sense.
    """
    # ── 1. Capability token path ──────────────────────────────────────────
    if session_token:
        claims = verify_sct(session_token, expected_actor=actor_id)
        if claims is None:
            # Distinguish expiry vs bad sig when possible
            raw_claims = None
            try:
                parts = session_token.split(".")
                if len(parts) == 3 and parts[0] == SCT_PREFIX:
                    raw_claims = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
                    if raw_claims and time.time() > float(raw_claims.get("exp", 0)):
                        return Standing(
                            valid=False,
                            source="deny",
                            reason="L11 AUTH: SCT expired",
                            session_id=raw_claims.get("sid") or session_id,
                            actor_id=actor_id or raw_claims.get("actor"),
                            expired=True,
                        )
            except Exception:
                pass
            return Standing(
                valid=False,
                source="deny",
                reason="L11 AUTH: SCT invalid (signature or actor mismatch)",
                session_id=session_id,
                actor_id=actor_id,
            )

        token, claims, delta = refresh_sct_if_needed(claims, session_token)
        standing = _claims_to_standing(
            claims, token, source="sct", reason="L11 AUTH: SCT valid"
        )
        standing.authority_delta = delta
        return standing

    # ── 2. Legacy store path ──────────────────────────────────────────────
    if allow_store and session_id:
        try:
            from arifosmcp.runtime.tools import _SESSIONS

            sess = _SESSIONS.get(session_id)
        except Exception:
            sess = None

        if sess and isinstance(sess, dict):
            # Actor mismatch
            if actor_id and sess.get("actor_id") and sess.get("actor_id") != actor_id:
                return Standing(
                    valid=False,
                    source="deny",
                    reason="L11 AUTH: actor_id mismatch",
                    session_id=session_id,
                    actor_id=actor_id,
                )
            # TTL
            expires_at = sess.get("expires_at_unix", float("inf"))
            try:
                if time.time() > float(expires_at) + 300:
                    return Standing(
                        valid=False,
                        source="deny",
                        reason="L11 AUTH: session expired (24h limit + grace exceeded)",
                        session_id=session_id,
                        actor_id=actor_id or sess.get("actor_id"),
                        expired=True,
                    )
            except (TypeError, ValueError):
                pass

            token, claims = mint_from_session_record(sess)
            # Prefer explicit actor from call if session lacks it
            if actor_id and not claims.get("actor"):
                claims["actor"] = actor_id
            standing = _claims_to_standing(
                claims,
                token,
                source="store",
                reason="L11 AUTH: session valid (store; token minted)",
            )
            return standing

        # Persisted identity store fallback (existing dual path)
        try:
            from arifosmcp.runtime.session import _ensure_active_record

            persisted = _ensure_active_record(session_id)
            if persisted:
                row = {
                    "session_id": session_id,
                    "actor_id": persisted.get("actor_id") or actor_id or "anonymous",
                    "actor_verified": bool(persisted.get("signature_verified")),
                    "authority": "OBSERVE_ONLY",
                    "stage": persisted.get("stage", "000"),
                    "lane": persisted.get("lane", "AGI"),
                    "expires_at_unix": persisted.get(
                        "expires_at_unix", time.time() + DEFAULT_TTL_SECONDS
                    ),
                }
                token, claims = mint_from_session_record(row)
                return _claims_to_standing(
                    claims,
                    token,
                    source="store",
                    reason="L11 AUTH: session valid (persisted identity; token minted)",
                )
        except Exception:
            pass

        return Standing(
            valid=False,
            source="deny",
            reason="L11 AUTH: session_id not found or expired",
            session_id=session_id,
            actor_id=actor_id,
        )

    if not session_id and not session_token:
        return Standing(
            valid=False,
            source="deny",
            reason="L11 AUTH: session_id missing",
            actor_id=actor_id,
        )

    return Standing(
        valid=False,
        source="deny",
        reason="L11 AUTH: session_id not found or expired",
        session_id=session_id,
        actor_id=actor_id,
    )


def attach_continuity(response: dict[str, Any], standing: Standing) -> dict[str, Any]:
    """Echo next hop continuity fields onto a tool response dict."""
    if not isinstance(response, dict):
        return response
    if standing.session_token:
        response["session_token"] = standing.session_token
    if standing.session_id:
        response.setdefault("session_id", standing.session_id)
    response.setdefault("authority", standing.authority)
    response.setdefault("actor_verified", standing.actor_verified)
    response.setdefault("apex_scalars", dict(standing.apex))
    response.setdefault("standing_source", standing.source)
    if standing.authority_delta is not None:
        response["authority_delta"] = standing.authority_delta
    # Put token in result blob too if present
    result = response.get("result")
    if isinstance(result, dict) and standing.session_token:
        result.setdefault("session_token", standing.session_token)
        result.setdefault("apex_scalars", dict(standing.apex))
        result.setdefault("standing_source", standing.source)
    return response
