"""
arifOS Identity Consistency — P1 Single Authority Source.

DITEMPA BUKAN DIBERI

Forged 2026-07-16 under F13 SOVEREIGN directive (audit cycle 2026-07-16).

Closes the chaos documented in the Fable-5 audit (2026-07-16):

  - Identity is computed in ≥4 places (tools.py:7943, 8111, 16964,
    tools_internal.py:360), with direct writes to legacy session fields
    (tools.py:8282: `sess["authority_level"] = ...`) bypassing the
    canonical `bind_authority_state`/`read_authority_state` helpers
    in authority.py.
  - Symptom: response payloads contained `actor_verified`, `authority_level`,
    `runtime_authority`, `human_authority`, nested `actor.authority_level`,
    and `authority_state.runtime_grant.level` — six independently
    derivable values. Coherent today, fork-risk tomorrow.

This module introduces a SINGLE composer and a SINGLE verifier:

  1. `compose_identity_envelope(session_id, actor_id, request)`
     — reads the canonical `AuthorityState` via `read_authority_state`,
       derives the five legacy fields atomically, returns one dict.
       This is the ONLY place those fields are derived.

  2. `verify_identity_consistency(response, composed)` — walks the
       final response dict, finds every identity-bearing field, and
       compares each to the canonical `composed` value. Any drift
       returns a list of violation strings. Empty list = consistent.

  3. `_attach_canonical_identity(response, composed)` — replaces
       identity-bearing fields in the response with the canonical
       values from `composed`, and attaches a `_identity_drift_violations`
       field listing any pre-existing drift that was corrected.

This module is wired into `_wrap_handler` in tools.py so every response
passes through it. A non-empty drift list narrows the response verdict
to HOLD (per WS1 P0-1 contract, 2026-07-12) and the violations are
sealed as a constitutional SCAR.

Reversible: this is a T2 ANNOUNCE change. Removal is to delete the
identity_consistency call from `_wrap_handler` and delete this file.

Compat note: `bind_authority_state` and `read_authority_state` in
authority.py remain the canonical writers/readers of the canonical
AuthorityState. This module reads from them, never writes.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── Identity-bearing fields the verifier scans in the final response ────────
# Each entry: (path_in_response, kind)
#   kind = "bool"   — compared as boolean
#   kind = "level"  — compared as one of SOVEREIGN/OPERATOR/L4_WARGA/OBSERVER/ANONYMOUS/OPERATOR_CLAIMED
#   kind = "band"   — compared as one of FULL/SOVEREIGN/LIMITED_MUTATE/OBSERVE_ONLY
_IDENTITY_FIELDS: list[tuple[str, str]] = [
    # Top-level fields (set by _attach_canonical_identity or legacy writers)
    ("actor_verified", "bool"),
    ("authority_level", "level"),
    ("authority", "band"),
    ("human_authority", "level"),
    ("runtime_authority", "band"),
    # Meta block
    ("meta.actor_verified", "bool"),
    # Top-level actor block (arif_init, session tools — Fable-5 audit)
    ("actor.identity_verified", "bool"),
    ("actor.authority_level", "level"),
    ("actor.claimed_id", "actor_id"),
    # Nested result.actor block (some tools wrap in result)
    ("result.actor_verified", "bool"),
    ("result.authority.actor_verified", "bool"),
    ("result.authority.human_authority", "level"),
    ("result.authority.runtime_authority", "band"),
    ("result.actor.identity_verified", "bool"),
    ("result.actor.authority_level", "level"),
    # Authority state (canonical + nested)
    ("authority_state.actor.verified", "bool"),
    ("authority_state.runtime_grant.level", "band"),
    ("result.authority_state.actor.verified", "bool"),
    ("result.authority_state.runtime_grant.level", "band"),
]


def _get_path(obj: Any, dotted: str) -> Any:
    """Walk a dotted path through nested dicts. Return _MISSING on miss."""
    cur: Any = obj
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return _MISSING
    return cur


_MISSING = object()


def compose_identity_envelope(
    session_id: str | None,
    actor_id: str | None,
    *,
    request_actor_verified: bool | None = None,
) -> dict[str, Any]:
    """P1: single-source identity composer. Replaces all ad-hoc derivations.

    Reads canonical AuthorityState via `read_authority_state(sess)`.
    Falls back to a conservative default if no session is bound.

    Returned dict is the ONLY source for identity-bearing fields in
    downstream response shapes. All other code MUST consult this
    object instead of re-deriving from legacy session keys.

    The returned dict is always flat and JSON-serializable.
    """
    from arifosmcp.runtime.authority import authority_envelope_for_session

    env = authority_envelope_for_session(
        session_id,
        actor_id,
        actor_verified_flag=request_actor_verified,
    )

    # Enrich with the derived level strings (mirror legacy mirror writer
    # in bind_authority_state, but DERIVED — never independently computed).
    level = "OBSERVER"
    band = env.get("runtime_authority", "OBSERVE_ONLY")
    if env.get("actor_verified"):
        # SOVEREIGN by known sovereign id (mirror logic in authority.py:376)
        known_sovereign = (actor_id or "").strip().lower() in (
            "arif",
            "888",
            "ariffazil",
            "arif_fazil",
        )
        level = "SOVEREIGN" if known_sovereign else "OPERATOR"
    elif actor_id and actor_id != "anonymous":
        level = "OPERATOR_CLAIMED"
    else:
        level = "OBSERVER"

    # P1 consistency: human_authority must agree with authority_level
    # (they share the same identity source). If authority_envelope disagreed,
    # trust our single-source derivation.
    human_authority = level

    # P1 consistency: authority (legacy band alias) must equal runtime_authority
    authority_band = env.get("runtime_authority") or band

    return {
        # Canonical scalars — every consumer reads from here.
        "actor_id": actor_id or "anonymous",
        "session_id": session_id or None,
        "actor_verified": bool(env.get("actor_verified")),
        "authority_level": level,
        "human_authority": human_authority,
        "runtime_authority": authority_band,
        "authority": authority_band,  # legacy alias — must equal runtime_authority
        "mutation_allowed": bool(env.get("mutation_allowed", False)),
        "seal_allowed": bool(env.get("seal_allowed", False)),
        # Provenance — where this composition came from.
        "_source": "identity_consistency.compose_identity_envelope",
        "_single_source_of_truth": True,
    }


def _normalize_actual(actual: Any, kind: str) -> Any:
    """Normalize a response field value for comparison.

    Handles the case where a field like `authority` is a dict
    (e.g. {"RUNTIME_AUTHORITY": "FULL", ...}) instead of a scalar.
    Extracts the relevant sub-field for the given kind.
    """
    if actual is _MISSING:
        return _MISSING
    if not isinstance(actual, dict):
        return actual
    # Dict where we expected a scalar — extract the relevant key.
    if kind == "band":
        return actual.get("RUNTIME_AUTHORITY", actual.get("runtime_authority", actual))
    if kind == "level":
        return actual.get(
            "HUMAN_AUTHORITY",
            actual.get(
                "human_authority",
                actual.get("AUTHORITY_LEVEL", actual.get("authority_level", actual)),
            ),
        )
    if kind == "bool":
        return actual.get("ACTOR_VERIFIED", actual.get("actor_verified", actual))
    if kind == "actor_id":
        return actual.get("CLAIMED_ID", actual.get("claimed_id", actual))
    return actual


def verify_identity_consistency(
    response: dict[str, Any],
    composed: dict[str, Any],
) -> list[str]:
    """P1: scan response for identity-bearing fields and diff against canonical.

    Returns a list of human-readable violation strings. Empty list = clean.
    Each violation describes one drifted field with both values for audit.

    This is the tripwire that detects parallel-authority drift before it
    can poison downstream consumers. Wired into _wrap_handler so every
    response passes through it.
    """
    if not isinstance(response, dict) or not isinstance(composed, dict):
        return []

    violations: list[str] = []
    canonical_actor_id = str(composed.get("actor_id", "anonymous"))
    canonical_av = bool(composed.get("actor_verified"))
    canonical_level = str(composed.get("authority_level", "OBSERVER"))
    canonical_band = str(composed.get("runtime_authority", "OBSERVE_ONLY"))

    for path, kind in _IDENTITY_FIELDS:
        actual = _get_path(response, path)
        if actual is _MISSING:
            continue

        # Normalize: if the field is a dict (e.g. authority={...}), extract
        # the relevant sub-value before comparing. Prevents dict-vs-string
        # false positives (Fable-5 Defect B).
        actual = _normalize_actual(actual, kind)

        if kind == "bool":
            try:
                actual_bool = bool(actual)
            except Exception:
                continue
            if actual_bool != canonical_av:
                violations.append(
                    f"identity_drift: {path}={actual_bool} "
                    f"≠ canonical_actor_verified={canonical_av} "
                    f"(session_id={composed.get('session_id')})"
                )
        elif kind == "actor_id":
            actual_str = str(actual).strip()
            if actual_str != canonical_actor_id and actual_str != "anonymous":
                # Only flag if the actual value is a relay placeholder that
                # contradicts the canonical actor_id
                if actual_str in ("openclaw-anon", "unknown", "null", ""):
                    violations.append(
                        f"identity_drift: {path}={actual_str} "
                        f"≠ canonical_actor_id={canonical_actor_id} "
                        f"(session_id={composed.get('session_id')})"
                    )
        elif kind == "level":
            actual_str = str(actual).strip().upper()
            if actual_str != canonical_level.upper():
                violations.append(
                    f"identity_drift: {path}={actual_str} "
                    f"≠ canonical_authority_level={canonical_level.upper()} "
                    f"(session_id={composed.get('session_id')})"
                )
        elif kind == "band":
            actual_str = str(actual).strip().upper()
            if actual_str != canonical_band.upper():
                violations.append(
                    f"identity_drift: {path}={actual_str} "
                    f"≠ canonical_runtime_authority={canonical_band.upper()} "
                    f"(session_id={composed.get('session_id')})"
                )

    return violations


def _attach_canonical_identity(
    response: dict[str, Any],
    composed: dict[str, Any],
    drift: list[str],
) -> dict[str, Any]:
    """Replace identity fields with canonical values at ALL levels.

    Fixes top-level, meta, actor, authority_state, AND result.* blocks.
    Fable-5 Defect A: detect-but-not-correct on result.* paths is closed
    by walking the same paths the verifier scans and overwriting drifted values.
    """
    if not isinstance(response, dict):
        return response

    canonical_av = bool(composed.get("actor_verified"))
    canonical_level = str(composed.get("authority_level", "OBSERVER"))
    canonical_band = str(composed.get("runtime_authority", "OBSERVE_ONLY"))
    canonical_human = str(composed.get("human_authority", "OBSERVER"))
    canonical_cid = str(composed.get("actor_id", "anonymous")).strip()

    # ── Top-level scalar fields ──
    response["actor_verified"] = canonical_av
    response["authority_level"] = canonical_level
    response["authority"] = canonical_band
    response["human_authority"] = canonical_human
    response["runtime_authority"] = canonical_band

    # ── Meta block ──
    meta = response.get("meta")
    if isinstance(meta, dict):
        meta["actor_verified"] = canonical_av
        meta["authority_level"] = canonical_level
        meta["human_authority"] = canonical_human
        meta["runtime_authority"] = canonical_band
        if drift:
            meta["_identity_drift_violations"] = list(drift)
            meta["_identity_consistency_applied"] = True

    # ── Top-level actor block ──
    _fix_actor_block(response.get("actor"), canonical_av, canonical_level, canonical_cid)

    # ── Top-level authority_state block ──
    _fix_authority_state(response.get("authority_state"), canonical_av, canonical_band)

    # ── result.actor block (Defect A fix) ──
    result = response.get("result")
    if isinstance(result, dict):
        _fix_actor_block(result.get("actor"), canonical_av, canonical_level, canonical_cid)
        _fix_authority_state(result.get("authority_state"), canonical_av, canonical_band)
        # result.authority can be a dict or scalar
        result_auth = result.get("authority")
        if isinstance(result_auth, dict):
            result_auth["actor_verified"] = canonical_av
            result_auth["human_authority"] = canonical_human
            result_auth["runtime_authority"] = canonical_band
        # result-level scalar fields
        if "actor_verified" in result:
            result["actor_verified"] = canonical_av

    if drift:
        response.setdefault("_identity_drift_violations", list(drift))
        response["_identity_consistency_applied"] = True

    return response


def _fix_actor_block(
    actor_block: Any,
    canonical_av: bool,
    canonical_level: str,
    canonical_cid: str,
) -> None:
    """Fix an actor dict (top-level or result.actor) in place."""
    if not isinstance(actor_block, dict):
        return
    # identity_verified
    if "identity_verified" in actor_block:
        actor_block["identity_verified"] = canonical_av
    # authority_level
    if "authority_level" in actor_block:
        actor_block["authority_level"] = canonical_level
    # claimed_id — only fix relay placeholders
    cid = str(actor_block.get("claimed_id", "")).strip()
    if cid in ("openclaw-anon", "unknown", "null", "") and canonical_cid not in (
        "anonymous",
        "openclaw-anon",
    ):
        actor_block["claimed_id"] = canonical_cid


def _fix_authority_state(
    auth_state: Any,
    canonical_av: bool,
    canonical_band: str,
) -> None:
    """Fix an authority_state dict in place."""
    if not isinstance(auth_state, dict):
        return
    as_actor = auth_state.get("actor")
    if isinstance(as_actor, dict) and "verified" in as_actor:
        as_actor["verified"] = canonical_av
    as_rg = auth_state.get("runtime_grant")
    if isinstance(as_rg, dict) and "level" in as_rg:
        as_rg["level"] = canonical_band


def apply_identity_consistency(
    response: dict[str, Any],
    *,
    session_id: str | None,
    actor_id: str | None,
    request_actor_verified: bool | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """P1 entry point: compose → verify → attach. Returns (response, drift).

    This is the single function `_wrap_handler` calls. It does not modify
    the kernel's authority_state (read-only here) — only the response
    shape and meta. The canonical source remains authority_state in the
    session store.

    A non-empty drift list should be treated as a constitutional SCAR.
    The caller (typically `_wrap_handler`) is responsible for narrowing
    the verdict to HOLD and sealing the drift evidence to VAULT999.

    Always attaches `_identity_consistency_applied` and `_identity_drift_count`
    sentinel fields so callers (and live probes) can verify the wrapper ran.
    """
    composed = compose_identity_envelope(
        session_id,
        actor_id,
        request_actor_verified=request_actor_verified,
    )
    drift = verify_identity_consistency(response, composed)
    if drift:
        logger.warning(
            "identity_drift_detected: session_id=%s actor_id=%s drift_count=%d first=%s",
            session_id,
            actor_id,
            len(drift),
            drift[0] if drift else "",
        )
    response = _attach_canonical_identity(response, composed, drift)
    # Always-on sentinels (P1f): enable live verification that the wrapper ran.
    if isinstance(response, dict):
        response["_identity_consistency_applied"] = True
        response["_identity_drift_count"] = len(drift)
        if drift:
            response["_identity_drift_first"] = drift[0]
        _meta = response.get("meta")
        if isinstance(_meta, dict):
            _meta["_identity_consistency_applied"] = True
            _meta["_identity_drift_count"] = len(drift)
    return response, drift


__all__ = [
    "compose_identity_envelope",
    "verify_identity_consistency",
    "_attach_canonical_identity",
    "apply_identity_consistency",
]
