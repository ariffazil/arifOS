"""
capability_token.py — THIN FACADE (Spine P0, 2026-07-09)

Canonical wire format is **sct_v1** via `arifosmcp.runtime.sct`.
This module re-exports useful helpers and never dual-mints `arifos.v1`.

Do not add a second birth path here. Merge new features into sct.py.
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.sct import (
    AUTHORITY_VERBS,
    AuthorityDelta,
    compute_authority_delta,
    derive_authority,
    derive_verbs,
    mint_sct,
    unmeasured_apex,
    verify_sct,
)
from arifosmcp.runtime.sct import (
    apply_caveats as _apply_caveats_claims,
)

# Re-export names used by older call sites
__all__ = [
    "AUTHORITY_VERBS",
    "AuthorityDelta",
    "TokenInvalidError",
    "apply_caveats",
    "build_session_token",
    "compute_authority_delta",
    "derive_authority",
    "derive_verbs",
    "sign_token",
    "verify_token",
    "verify_token_or_raise",
]


class TokenInvalidError(ValueError):
    """Structured token verification failure — always a sesat_event."""

    def __init__(self, token: str):
        self.token_prefix = token[:30] if token else "(none)"
        super().__init__(
            f"Session token invalid or expired. Re-authenticate via arif_init. "
            f"Token prefix: {self.token_prefix}..."
        )

    def sesat_event(self) -> dict:
        return {
            "sesat": True,
            "type": "TOKEN_INVALID",
            "malu_delta": 0.05,
            "tebus_required": "re-authenticate via arif_init",
            "token_prefix": self.token_prefix,
        }


def build_session_token(
    session_id: str,
    actor_id: str,
    sovereign_id: str = "",
    G: Any = None,
    C_dark: Any = None,
    W3: Any = None,
    h: Any = None,
    confidence: float = 0.0,
    authority: str = "OBSERVE_ONLY",
    verdict: str = "OK",
    witness_diversity: str = "NONE",
    witness_active: int = 0,
    witness_missing: list | None = None,
    alignment_loaded: bool = False,
    adversarial_loaded: bool = False,
    ttl_seconds: int = 3600,
    **_kwargs: Any,
) -> str:
    """Build **sct_v1** token. Apex numbers only if real floats; else UNMEASURED."""
    apex = unmeasured_apex()
    for key, val in (("G", G), ("C_dark", C_dark), ("W3", W3), ("h", h)):
        if isinstance(val, (int, float)) and val is not None:
            # Only accept as measured when caller also passes a non-zero measure signal
            # Birth paths should pass None → UNMEASURED
            if key == "h" and (val == "UNMEASURED" or val is None):
                continue
            if key != "h":
                # Refuse default theater values (0.0625 / 0.0 as "measured")
                # Callers with real measure pass explicit floats after compute_apex
                pass
        if val == "UNMEASURED" or val is None:
            continue
        if isinstance(val, (int, float)):
            apex[key] = val
        elif key == "h" and isinstance(val, str) and val != "UNMEASURED":
            apex[key] = val

    # 2026-08-05 W-12 FIX: Removed hardcoded 0.0625 / 0.0 catch.
    # The upstream APEX math (apex_primitives.py, apex_canonical.py) now
    # produces the canonical 4-factor geometric mean (A·P·E·X)^(1/4).
    # A 0.0625 = 0.5^4 phantom can no longer originate here.

    token, _claims = mint_sct(
        sid=session_id,
        actor=actor_id or "anonymous",
        auth=authority,
        av=bool(witness_active > 0),
        verdict_state=verdict or "OK",
        allowed=derive_verbs(authority),
        apex=apex,
        witness={
            "active": int(witness_active or 0),
            "diversity": witness_diversity or "NONE",
        },
        ttl=int(ttl_seconds or 3600),
    )
    return token


def sign_token(payload: Any) -> str:
    """Legacy name — if dict claims, mint sct_v1; if string, return as-is."""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        token, _ = mint_sct(
            sid=str(payload.get("sid") or payload.get("sub") or ""),
            actor=str(payload.get("actor") or payload.get("act") or "anonymous"),
            auth=str(payload.get("auth") or "OBSERVE_ONLY"),
            av=bool(payload.get("av", False)),
            allowed=list(payload.get("allowed") or payload.get("verbs") or []),
            apex=payload.get("apex") if isinstance(payload.get("apex"), dict) else None,
        )
        return token
    raise TypeError("sign_token expects claims dict or token string")


def verify_token(token: str) -> dict | None:
    """Return normalized sct claims dict, or None."""
    return verify_sct(token)


def verify_token_or_raise(token: str) -> dict:
    claims = verify_sct(token)
    if claims is None:
        raise TokenInvalidError(token)
    return claims


def apply_caveats(payload: Any, new_caveats: list[dict]) -> dict:
    """Attenuate claims dict (or dict-like). Returns new claims — re-mint to sign."""
    if hasattr(payload, "to_dict"):
        claims = payload.to_dict()
        # Map legacy TokenPayload shape → sct claims
        if "sub" in claims and "sid" not in claims:
            claims = {
                "sid": claims.get("sub"),
                "actor": claims.get("act"),
                "auth": claims.get("auth"),
                "allowed": claims.get("verbs") or [],
                "apex": claims.get("apex"),
                "caveats": claims.get("caveats") or [],
            }
    elif isinstance(payload, dict):
        claims = dict(payload)
    else:
        raise TypeError("apply_caveats expects claims dict")
    return _apply_caveats_claims(claims, new_caveats)
