"""
arifOS Session Standing — canonical session/identity/authority object.

Epoch 1 / Item 1 of the Kernel Senescence Reduction plan.
The single composer of actor and authority. No wrapper may recompute.

Schema (from F13 epoch / audit spec):
    {
      "session_id": "SEAL-...",
      "actor": {
        "claimed_id": "arif",
        "canonical_id": "ARIF_FAZIL",
        "verified": false,
        "verification_method": null,
        "evidence_ref": null
      },
      "authority": {
        "band": "OBSERVE_ONLY",
        "mutation_allowed": false,
        "seal_allowed": false
      },
      "issued_at": "...",
      "expires_at": "...",
      "state_version": 1
    }

This is the ONLY source of actor.verified and authority.band. Every wrapper
that previously emitted actor_verified / authority_level / authority /
human_authority / runtime_authority must consume this object instead.

Net effect on the kernel: seven legacy identity fields collapse to four
structured fields; four nesting levels collapse to one.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


# Bump when the canonical shape changes; consumers use this to detect drift.
SESSION_STANDING_VERSION = 1

# Default session TTL (matches session.py _SESSION_TTL_SECONDS default 86400 = 24h)
# Used when no expires_at is recorded, to prevent instant-expiry standing.
_DEFAULT_SESSION_TTL_SECONDS = 86400

# Authority bands. Only these four values are emitted.
BAND_OBSERVE_ONLY = "OBSERVE_ONLY"
BAND_LIMITED_MUTATE = "LIMITED_MUTATE"
BAND_FULL = "FULL"
BAND_SOVEREIGN = "SOVEREIGN"

VALID_BANDS = frozenset({BAND_OBSERVE_ONLY, BAND_LIMITED_MUTATE, BAND_FULL, BAND_SOVEREIGN})

# Methods strong enough to elevate mutation/seal authority.
# identity_claim is a WEAK proof class: may bind name, never grant mutation.
STRONG_VERIFICATION_METHODS = frozenset(
    {
        "ed25519",
        "ed25519_signature",
        "sct_sovereign",
        "vault_seal",
        "capability_token",
    }
)

# Machine/component identities that must never absorb a human claim.
_COMPONENT_IDENTITY_MARKERS = frozenset(
    {
        "conformance-spine",
        "parent_agent",
        "parent-agent",
        "anonymous",
        "system",
        "kernel",
        "mcp-host",
    }
)


def _is_component_identity(actor: str | None) -> bool:
    if not actor:
        return True
    token = str(actor).strip().lower()
    if token in _COMPONENT_IDENTITY_MARKERS:
        return True
    # agi-gate-* cycle probes, forge component tags
    if token.startswith("agi-gate-"):
        return True
    if token.startswith("conformance"):
        return True
    return False


def _is_strong_method(method: str | None) -> bool:
    if not method:
        return False
    return str(method).strip().lower() in STRONG_VERIFICATION_METHODS


@dataclass(frozen=True)
class ActorStanding:
    claimed_id: str
    canonical_id: str
    verified: bool
    verification_method: str | None
    evidence_ref: str | None = None

    def __post_init__(self) -> None:
        """Schema-level proof-integrity invariant (T3a.2 / Claude Point 2).

        The system MUST NEVER emit ``verified=true`` without an attached
        verification_method AND evidence_ref. A positive assertion without
        evidence is ``C_dark`` — confidence exceeding proof.

        Construction with ``verified=true, method=None, evidence_ref=None``
        is structurally unrepresentable. Code that reaches this state must
        be fixed, not caught at runtime.
        """
        if self.verified:
            if not self.verification_method:
                raise ValueError(
                    f"ActorStanding invariant violation: "
                    f"verified=True requires verification_method, got None "
                    f"(claimed_id={self.claimed_id})"
                )
            if not self.evidence_ref:
                raise ValueError(
                    f"ActorStanding invariant violation: "
                    f"verified=True requires evidence_ref, got None "
                    f"(claimed_id={self.claimed_id})"
                )


@dataclass(frozen=True)
class AuthorityStanding:
    band: str
    mutation_allowed: bool
    seal_allowed: bool

    def __post_init__(self) -> None:
        """Seal authority requires SOVEREIGN band."""
        if self.seal_allowed and self.band != "SOVEREIGN":
            raise ValueError(
                f"AuthorityStanding invariant violation: "
                f"seal_allowed=True requires band=SOVEREIGN, got {self.band}"
            )


@dataclass(frozen=True)
class SessionStanding:
    session_id: str
    actor: ActorStanding
    authority: AuthorityStanding
    issued_at: str
    expires_at: str
    state_version: int = SESSION_STANDING_VERSION


def _read_session_record(session_id: str | None) -> dict[str, Any] | None:
    """Read the underlying session record. The only reader of legacy state."""
    if not session_id:
        return None
    try:
        from arifosmcp.runtime.session import get_session_identity

        record = get_session_identity(session_id)
        if record:
            return record
        # FIX 2026-07-24: get_session_identity only matches arifos.v1.* IDs.
        # SEAL-* sessions invisible → standing always OBSERVE_ONLY.
        # Fall back to global _SESSIONS store.
        from arifosmcp.runtime.tools import _SESSIONS

        sess = _SESSIONS.get(session_id)
        if sess:
            return dict(sess)
        return None
    except Exception:
        return None


def _normalize_band(level: Any) -> str:
    """Collapse every legacy authority token to one of the four canonical bands.

    This is the ONLY function that maps legacy authority strings to bands.
    """
    if not level:
        return BAND_OBSERVE_ONLY
    token = str(level).strip().upper()
    if token in {"SOVEREIGN", "888"}:
        return BAND_SOVEREIGN
    if token in {"FULL", "OPERATOR", "OPERATOR_CLAIMED", "L4_WARGA"}:
        return BAND_FULL if token == "FULL" else BAND_LIMITED_MUTATE
    if token in {"LIMITED_MUTATE", "OBSERVER", "ANONYMOUS", "LOW"}:
        return BAND_LIMITED_MUTATE if token == "LIMITED_MUTATE" else BAND_OBSERVE_ONLY
    return BAND_OBSERVE_ONLY


def _derive_authority_band(record: dict[str, Any] | None, actor_id: str | None) -> str:
    """Compute the single authority band. No other code path may compute it."""
    if not record:
        return BAND_OBSERVE_ONLY
    # Prefer runtime_authority (the canonical underlying field), then
    # authority_level (legacy alias). Both must converge to the same band.
    level = record.get("runtime_authority") or record.get("authority_level")
    return _normalize_band(level)


def _resolve_canonical_actor(actor_id: str | None, record: dict[str, Any] | None) -> str:
    """Resolve canonical_id from actor_id and session record."""
    if record:
        for key in ("canonical_actor_id", "verified_actor_id"):
            cid = record.get(key)
            if cid:
                return str(cid)
    return actor_id or "anonymous"


def _resolve_verification_method(record: dict[str, Any] | None) -> str | None:
    """Determine the verification method used, if any."""
    if not record:
        return None
    # Top-level first (bind_session_identity / T3a may set these)
    top = record.get("verification_method")
    if top:
        return str(top)
    auth_ctx = record.get("auth_context") or {}
    if isinstance(auth_ctx, dict):
        method = auth_ctx.get("verification_method") or auth_ctx.get("auth_method")
        if method:
            return str(method)
    identity = record.get("identity") or {}
    if isinstance(identity, dict) and identity.get("ed25519_verified"):
        return "ed25519"
    # Explicit weak class — still a method (not null), never strong
    if record.get("identity_claim_accepted") or auth_ctx.get("identity_claim_accepted"):
        return "identity_claim"
    return None


def _resolve_evidence_ref(record: dict[str, Any] | None) -> str | None:
    """Resolve evidence reference from session record.

    Tries (in order):
      1. record.evidence_ref — explicit evidence pointer
      2. Ed25519 verified_key_id — cryptographic key fingerprint
      3. session_id — fallback, always present on active sessions
    Returns None only when no session record exists at all.
    """
    if not record:
        return None
    ref = record.get("evidence_ref")
    if ref:
        return str(ref)
    auth_ctx = record.get("auth_context") or {}
    if isinstance(auth_ctx, dict):
        key_id = auth_ctx.get("verified_key_id")
        if key_id:
            return f"key://{key_id}"
    sid = record.get("session_id")
    if sid:
        return f"session://{sid}"
    return None


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def compose_standing(session_id: str | None, actor_id: str | None = None) -> SessionStanding:
    """Compose the canonical SessionStanding for a session.

    This is the ONLY function that derives actor.verified and authority.band.
    No other code path may compute these fields. Tools consume this object;
    wrappers do not recompute.

    P0 laws (2026-07-17 audit):
      1. One request → one actor, one session, one band, one method, one evidence.
      2. Unverified → OBSERVE_ONLY, mutation_allowed=false, seal_allowed=false.
      3. identity_claim is WEAK — never grants mutation or seal.
      4. Component identities (conformance-spine, agi-gate-*) cannot absorb a
         human/sovereign claim.
      5. verified=true without method+evidence is structurally unrepresentable.

    Returns a frozen SessionStanding. state_version marks the schema.
    """
    record = _read_session_record(session_id)

    # Claimed id prefers the caller argument (THIS request), not a stale record.
    # Case-normalize at intake (Claude audit 2026-07-17): ARIF → arif.
    claimed_id = actor_id or (record.get("actor_id") if record else None) or "anonymous"
    claimed_id = str(claimed_id).strip()
    try:
        from arifosmcp.runtime.governance_identity import normalize_actor_id

        _norm = normalize_actor_id(claimed_id)
        if _norm:
            claimed_id = _norm
    except Exception:
        claimed_id = claimed_id.lower() if claimed_id else "anonymous"

    if record:
        verification_method = _resolve_verification_method(record)
        evidence_ref = _resolve_evidence_ref(record)
        verified_raw = bool(
            record.get("verified")
            or record.get("actor_verified")
            or record.get("identity_verified")
        )
        # T3a.2 / Claude Point 2: HONEST_HOLD — if the record claims verified
        # but no verification_method or evidence_ref is available, SET
        # verified=False rather than emitting the structural contradiction
        # ``verified=true, method=null``. Same pattern as arif_memory's
        # honest-failure shape: admit what cannot be proved.
        if verified_raw and (not verification_method or not evidence_ref):
            logger.warning(
                "C_dark HONEST_HOLD: record claims verified=true but %s is "
                "missing. Setting verified=false. (claimed_id=%s)",
                "verification_method" if not verification_method else "evidence_ref",
                claimed_id,
            )
            verified = False
        else:
            verified = verified_raw
        issued_at = record.get("created_at") or _utcnow_iso()
        # P0-RT fix 2026-07-19: when expires_at is absent, use issued_at + default TTL
        # instead of _utcnow_iso() (which produces instant-expiry standing).
        _rec_expires = record.get("expires_at")
        if _rec_expires:
            expires_at = _rec_expires
        else:
            try:
                _issued_dt = datetime.fromisoformat(issued_at)
                expires_at = (
                    _issued_dt + timedelta(seconds=_DEFAULT_SESSION_TTL_SECONDS)
                ).isoformat()
            except Exception:
                expires_at = (
                    datetime.now(UTC) + timedelta(seconds=_DEFAULT_SESSION_TTL_SECONDS)
                ).isoformat()
        record_actor = str(record.get("actor_id") or record.get("canonical_actor_id") or "")
    else:
        verified = False
        verification_method = None
        evidence_ref = None
        issued_at = _utcnow_iso()
        # P0-RT fix 2026-07-19: no record → still give a reasonable TTL, not instant expiry.
        expires_at = (
            datetime.now(UTC) + timedelta(seconds=_DEFAULT_SESSION_TTL_SECONDS)
        ).isoformat()
        record_actor = ""

    canonical_id = _resolve_canonical_actor(claimed_id, record)

    # Identity leakage guard: human claim must not inherit component standing.
    record_mismatch = bool(
        record_actor
        and claimed_id
        and record_actor.lower() != claimed_id.lower()
        and str(canonical_id).lower() != claimed_id.lower()
    )
    component_leak = not _is_component_identity(claimed_id) and _is_component_identity(
        str(canonical_id)
    )
    if record_mismatch or component_leak:
        logger.warning(
            "Identity binding collapse: claimed=%s record_actor=%s canonical=%s "
            "→ refuse component/session leakage",
            claimed_id,
            record_actor,
            canonical_id,
        )
        canonical_id = claimed_id
        verified = False
        verification_method = None
        # Keep evidence_ref only if it points at THIS session
        if evidence_ref and session_id and f"session://{session_id}" not in str(evidence_ref):
            evidence_ref = f"session://{session_id}" if session_id else None
        elif session_id and not evidence_ref:
            evidence_ref = None

    band = _derive_authority_band(record, claimed_id)

    # AC / Option B constraint: unverified OR weak method → OBSERVE_ONLY.
    # identity_claim may bind a name; it must never elevate mutation/seal.
    if not verified or not _is_strong_method(verification_method):
        if band != BAND_OBSERVE_ONLY:
            logger.info(
                "Authority collapse: verified=%s method=%s band=%s→OBSERVE_ONLY (claimed=%s)",
                verified,
                verification_method,
                band,
                claimed_id,
            )
        band = BAND_OBSERVE_ONLY

    mutation_allowed = band in {BAND_LIMITED_MUTATE, BAND_FULL, BAND_SOVEREIGN}
    seal_allowed = band == BAND_SOVEREIGN and _is_strong_method(verification_method)

    # Final AC belt: if somehow mutation_allowed with unverified, hard-deny
    if not verified:
        mutation_allowed = False
        seal_allowed = False
        band = BAND_OBSERVE_ONLY

    actor = ActorStanding(
        claimed_id=claimed_id,
        canonical_id=str(canonical_id),
        verified=verified,
        verification_method=verification_method,
        evidence_ref=evidence_ref,
    )
    authority = AuthorityStanding(
        band=band,
        mutation_allowed=mutation_allowed,
        seal_allowed=seal_allowed,
    )

    return SessionStanding(
        session_id=session_id or "anonymous",
        actor=actor,
        authority=authority,
        issued_at=issued_at,
        expires_at=expires_at,
        state_version=SESSION_STANDING_VERSION,
    )


def standing_to_envelope(standing: SessionStanding) -> dict[str, Any]:
    """Serialize the SessionStanding into the canonical envelope shape.

    The shape is exactly the audit spec. No extra fields.
    """
    return {
        "session_id": standing.session_id,
        "actor": asdict(standing.actor),
        "authority": asdict(standing.authority),
        "issued_at": standing.issued_at,
        "expires_at": standing.expires_at,
        "state_version": standing.state_version,
    }


# Legacy identity-bearing field names emitted by the previous Fable-5 wrapper
# (identity_consistency.py, deleted). Kept as a single set so the wrapper
# migration is one deletion pass, not five separate scans.
_LEGACY_IDENTITY_TOP_LEVEL = (
    "actor_verified",
    "authority_level",
    "authority",
    "human_authority",
    "runtime_authority",
    "_identity_consistency_applied",
    "_identity_drift_count",
    "_identity_drift_first",
    "_identity_drift_violations",
    "authority_state",
)

_LEGACY_IDENTITY_NESTED = (
    "actor_verified",
    "authority_level",
    "authority",
    "human_authority",
    "runtime_authority",
    "_identity_consistency_applied",
    "_identity_drift_count",
)

_LEGACY_ACTOR_BLOCK_FIELDS = (
    "identity_verified",
    "authority_level",
    "claimed_id",
)

_LEGACY_AUTHORITY_DICT_KEYS = (
    "actor_verified",
    "human_authority",
    "runtime_authority",
    "AUTHORITY_LEVEL",
    "RUNTIME_AUTHORITY",
    "HUMAN_AUTHORITY",
    "ACTOR_VERIFIED",
)


def _strip_legacy_identity(response: dict[str, Any]) -> None:
    """Remove every legacy identity field from a response, at every nesting level.

    Mutates in place. After this call, the response contains no legacy
    identity-bearing field names — only the canonical standing block will
    remain (attached separately). Empty legacy containers are removed
    entirely so the response has no empty shell dicts either.
    """
    for key in _LEGACY_IDENTITY_TOP_LEVEL:
        response.pop(key, None)

    meta = response.get("meta")
    if isinstance(meta, dict):
        for key in _LEGACY_IDENTITY_NESTED:
            meta.pop(key, None)

    actor = response.get("actor")
    if isinstance(actor, dict):
        for key in _LEGACY_ACTOR_BLOCK_FIELDS:
            actor.pop(key, None)
        # If the legacy actor block is now empty, drop the block entirely.
        if not actor:
            response.pop("actor", None)

    auth_state = response.get("authority_state")
    if isinstance(auth_state, dict):
        auth_state.pop("actor", None)
        auth_state.pop("runtime_grant", None)
        if not auth_state:
            response.pop("authority_state", None)

    result = response.get("result")
    if isinstance(result, dict):
        for key in _LEGACY_IDENTITY_TOP_LEVEL:
            result.pop(key, None)
        result_actor = result.get("actor")
        if isinstance(result_actor, dict):
            for key in _LEGACY_ACTOR_BLOCK_FIELDS:
                result_actor.pop(key, None)
            if not result_actor:
                result.pop("actor", None)
        result_authority = result.get("authority")
        if isinstance(result_authority, dict):
            for key in _LEGACY_AUTHORITY_DICT_KEYS:
                result_authority.pop(key, None)
            if not result_authority:
                result.pop("authority", None)
        result_auth_state = result.get("authority_state")
        if isinstance(result_auth_state, dict):
            result_auth_state.pop("actor", None)
            result_auth_state.pop("runtime_grant", None)
            if not result_auth_state:
                result.pop("authority_state", None)


def _allowed_verbs_for_band(band: str) -> list[str]:
    """Verb allowlist derived from standing band only.

    The full public surface must be reachable under SOVEREIGN/FULL.
    """
    if band in (BAND_FULL, BAND_SOVEREIGN):
        return [
            "arif_init",
            "arif_observe",
            "arif_think",
            "arif_route",
            "arif_memory",
            "arif_judge",
            "arif_forge",
            "arif_seal",
        ]
    if band == BAND_LIMITED_MUTATE:
        return [
            "arif_init",
            "arif_observe",
            "arif_think",
            "arif_route",
            "arif_memory",
            "arif_judge",
            "arif_forge",
        ]
    return ["arif_init", "arif_observe", "arif_think", "arif_route"]


def _sync_authority_surfaces_from_standing(
    response: dict[str, Any],
    standing: SessionStanding,
) -> None:
    """P0: standing is the sole authority surface — kill dual narrative.

    session_birth / clarity_contract / top-level authority must not claim
    FULL/verified/mutation while standing says OBSERVE_ONLY/unverified.
    Mutates response in place.
    """
    env = standing_to_envelope(standing)
    actor = env["actor"]
    authority = env["authority"]
    band = authority["band"]
    verified = bool(actor["verified"])
    mutation = bool(authority["mutation_allowed"])
    allowed = _allowed_verbs_for_band(band)

    # Top-level mirrors (if present)
    if "actor_verified" in response:
        response["actor_verified"] = verified
    if "authority" in response and isinstance(response["authority"], str):
        response["authority"] = band
    if "authority_scope" in response:
        response["authority_scope"] = band
    if "authority_mode" in response:
        response["authority_mode"] = band
    if "allowed_next_verbs" in response:
        response["allowed_next_verbs"] = list(allowed)

    # session_birth — the dual-claim residual named by the auditor
    birth = response.get("session_birth")
    if isinstance(birth, dict):
        birth["actor_verified"] = verified
        birth["authority_mode"] = band
        birth["verdict"] = band
        birth["mutation_allowed"] = mutation
        birth["authority_source"] = "standing"
        # Align identity fields with standing
        birth["claimed_id"] = actor["claimed_id"]
        birth["canonical_id"] = actor["canonical_id"]
        birth["verification_method"] = actor["verification_method"]
        birth["evidence_ref"] = actor["evidence_ref"]
        if standing.session_id and standing.session_id != "anonymous":
            birth["session_id"] = standing.session_id
        # Invalidate pre-collapse SCT in birth — token may still claim FULL
        if birth.get("session_token") and not verified:
            birth["session_token_status"] = "SUPERSEDED_BY_STANDING"
            # Keep token for audit trail but mark non-authoritative
            birth["session_token_authoritative"] = False

    # Nested result.session_birth (some wrappers nest)
    result = response.get("result")
    if isinstance(result, dict):
        _sync_authority_surfaces_from_standing(result, standing)

    # clarity_contract mutation_allowed must match standing
    clarity = response.get("clarity_contract")
    if isinstance(clarity, dict):
        clarity["authority_band"] = band
        clarity["mutation_allowed"] = mutation
        clarity["actor_bound"] = verified
        clarity["evidence_honesty"] = "CLEAR" if verified else "FUZZY"

    # sct_claims.av must not claim verified if standing denies it
    sct = response.get("sct_claims")
    if isinstance(sct, dict):
        sct["av"] = verified
        sct["auth"] = band

    # meta.authority_mode residual
    meta = response.get("meta")
    if isinstance(meta, dict) and "authority_mode" in meta:
        meta["authority_mode"] = band

    # Re-mint SCT from standing when weak/unverified so wire token matches law
    if standing.session_id and standing.session_id != "anonymous":
        try:
            from arifosmcp.runtime.sct import mint_sct, unmeasured_apex

            token, claims = mint_sct(
                sid=standing.session_id,
                actor=str(actor["claimed_id"] or "anonymous"),
                auth=band,
                av=verified,
                stage="000",
                lane="AGI",
                verdict_state=band,
                dominant_reason=None,
                allowed=allowed,
                apex=unmeasured_apex(),
                witness={
                    "active": 1 if verified else 0,
                    "diversity": "PARTIAL" if verified else "NONE",
                },
            )
            response["session_token"] = token
            if isinstance(response.get("sct_claims"), dict) or "sct_claims" in response:
                response["sct_claims"] = {
                    "auth": claims.get("auth", band),
                    "av": claims.get("av", verified),
                    "exp": claims.get("exp"),
                    "sid": claims.get("sid", standing.session_id),
                    "sct_v": claims.get("sct_v"),
                }
            if isinstance(birth, dict):
                birth["session_token"] = token
                birth["session_token_authoritative"] = True
                birth.pop("session_token_status", None)
        except Exception as exc:
            logger.debug("SCT re-mint from standing skipped: %s", exc)


def attach_canonical_standing(
    response: Any,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> Any:
    """Attach the canonical SessionStanding to a response.

    Replaces the entire legacy identity-field surface (seven field names at
    four nesting levels) with one canonical `standing` block matching the
    audit spec. No drift sentinels — the canonical composer is the only
    source, so contradiction is structurally impossible.

    P0 2026-07-17: also syncs session_birth / clarity_contract / top-level
    authority fields FROM standing so dual narrative is impossible.

    The response is mutated in place and returned. Non-dict inputs are
    returned unchanged.
    """
    if not isinstance(response, dict):
        return response
    _strip_legacy_identity(response)
    # Prefer response-born session if caller did not pass one
    if not session_id:
        birth = (
            response.get("session_birth") if isinstance(response.get("session_birth"), dict) else {}
        )
        session_id = response.get("session_id") or birth.get("session_id") or session_id
    if not actor_id:
        birth = (
            response.get("session_birth") if isinstance(response.get("session_birth"), dict) else {}
        )
        actor_id = (
            response.get("actor_id") or response.get("actor") or birth.get("actor_id") or actor_id
        )
        if isinstance(actor_id, dict):
            actor_id = actor_id.get("claimed_id") or actor_id.get("id")
    standing = compose_standing(
        session_id, actor_id if isinstance(actor_id, str) or actor_id is None else str(actor_id)
    )
    response["standing"] = standing_to_envelope(standing)
    _sync_authority_surfaces_from_standing(response, standing)
    return response


def attach_canonical(
    response: Any,
    *,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> Any:
    """One-call canonical normalization: standing + effective_verdict.

    Replaces the legacy `apply_identity_consistency` shim. Sequences the
    two passes in their constitutional order — identity first (so
    OBSERVE_ONLY can downgrade a tool's self-reported SEAL), then verdict
    (which reads the resulting standing's authority band).

    Non-dict inputs are wrapped in {"result": response}, normalized, then
    unwrapped. Pass-through is preserved.
    """
    if not isinstance(response, dict):
        wrapped: dict[str, Any] = {"result": response}
        attach_canonical(wrapped, session_id=session_id, actor_id=actor_id)
        return wrapped.get("result")

    # Read inner verdict BEFORE the identity strip; the standing composer
    # preserves verdict (it is not a legacy identity field), but reading
    # it now gives the verdict composer the tool's claim to reduce.
    inner_verdict = response.get("verdict") if isinstance(response, dict) else None
    attach_canonical_standing(response, session_id=session_id, actor_id=actor_id)
    standing = response.get("standing") if isinstance(response, dict) else None
    band: str | None = None
    if isinstance(standing, dict):
        authority = standing.get("authority")
        if isinstance(authority, dict):
            band_value = authority.get("band")
            if isinstance(band_value, str):
                band = band_value

    from arifosmcp.runtime.verdict import attach_effective_verdict

    return attach_effective_verdict(
        response,
        inner_verdict=inner_verdict,
        session_authority_band=band,
    )


__all__ = [
    "ActorStanding",
    "AuthorityStanding",
    "SessionStanding",
    "SESSION_STANDING_VERSION",
    "BAND_OBSERVE_ONLY",
    "BAND_LIMITED_MUTATE",
    "BAND_FULL",
    "BAND_SOVEREIGN",
    "VALID_BANDS",
    "compose_standing",
    "standing_to_envelope",
    "attach_canonical_standing",
    "attach_canonical",
]
