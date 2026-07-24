"""
arifosmcp/federation/federation_envelope.py — Kernel-to-Organ Bridge Envelope
═══════════════════════════════════════════════════════════════════════════════

Workstream 9: Every bridged organ call carries this envelope so the target organ
receives full identity, session, authority, governance, and trace context.

Bridge rules (F1/F11/F13):
  1. No authority upgrade across the bridge
  2. No identity substitution
  3. No dropping the governing session
  4. No organ result represented as kernel evidence without provenance
  5. Direct and bridged calls with same payload must be comparable
  6. DEGRADED_CLAIM must name: what degraded, where degraded, whether evidence
     was produced, whether result is usable, next safe action

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════════

FEDERATION_ENVELOPE_VERSION = "ws9-v1"

# Evidence layers (L0-L5) — canonical classification
EVIDENCE_LAYERS = {
    "L0": "unverified",
    "L1": "self_consistent",
    "L2": "schema_validated",
    "L3": "cross_organ_verified",
    "L4": "live_probe_witnessed",
    "L5": "cryptographically_sealed",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Envelope builder
# ═══════════════════════════════════════════════════════════════════════════════


def _sha256(data: Any) -> str:
    """Canonical SHA-256 hex digest (sort_keys for dicts)."""
    raw: bytes
    if isinstance(data, dict):
        raw = json.dumps(data, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    else:
        raw = json.dumps(data, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def compute_request_hash(tool_name: str, arguments: dict[str, Any] | None) -> str:
    """LEGACY single-hash request hash.

    DEPRECATED for federation envelope use. Kept only for backward-compat
    callers that already depend on the old single-hash shape. New code MUST
    use ``compute_raw_request_hash`` + ``compute_normalized_payload_hash``
    so canonical and alias payloads produce distinct raw hashes but a
    shared canonical semantic hash.

    Args:
        tool_name: The target tool name.
        arguments: The raw call arguments.

    Returns:
        24-char SHA-256 hex digest.
    """
    payload = {"tool_name": tool_name, "arguments": arguments or {}}
    return _sha256(payload)


def compute_raw_request_hash(
    *,
    actor_id: str | None,
    session_id: str | None,
    organ: str | None,
    tool: str,
    arguments: dict[str, Any] | None,
) -> str:
    """P0f — Raw request hash covering actor + session + organ + tool + raw args.

    This is the binding that proves the request was issued by a specific
    actor in a specific session against a specific tool with a specific
    argument payload. Two distinct payloads must produce two distinct
    raw_request_hash values (proving replay integrity at the wire level).

    Used in addition to ``compute_normalized_payload_hash``: a canonical
    payload and its exact alias equivalent will produce the same physics
    verdict and the same ``normalized_payload_hash``, but distinct
    ``raw_request_hash`` values (because the on-wire argument shape differs).
    """
    payload = {
        "actor_id": actor_id or "",
        "session_id": session_id or "",
        "organ": organ or "",
        "tool": tool or "",
        "arguments": arguments or {},
    }
    return _sha256(payload)


def compute_normalized_payload_hash(payload: dict[str, Any] | None) -> str:
    """P0f — Canonical (semantic) payload hash for parity comparison.

    After alias normalisation, the canonical and alias payloads produce
    identical canonical dicts. Their ``normalized_payload_hash`` MUST match,
    proving that the physics-layer verdict is genuinely equivalent across
    on-wire shapes.

    Pass the canonicalised (post-normalise) dict from the harness layer.
    """
    return _sha256(payload or {})


def compute_response_hash(response: dict[str, Any]) -> str:
    """Deterministic hash of the response content."""
    return _sha256(response)


def build_federation_envelope(
    *,
    # ── Caller identity ─────────────────────────────────────────────
    actor_id: str | None = None,
    identity_verified: bool = False,
    authority_state: dict[str, Any] | None = None,
    # ── Session context ─────────────────────────────────────────────
    session_id: str | None = None,
    session_token: str | None = None,
    authority: str = "OBSERVE_ONLY",
    allowed_scope: list[str] | None = None,
    # ── Request context ─────────────────────────────────────────────
    intent: str = "",
    source_tool: str = "",
    target_organ: str = "",
    target_tool: str = "",
    # ── Governance context ──────────────────────────────────────────
    evidence_layer: str = "L2",
    reversibility: str = "reversible",
    constitutional_chain_id: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """
    Build a full federation envelope for kernel-to-organ bridge dispatch.

    Bridge rules (F1/F11/F13) are enforced structurally:
      - ``identity_verified`` is OBSERVED, never inferred
      - ``authority`` is the session band, never upgraded
      - ``session_id`` is passed verbatim from kernel session
      - Every field has a non-null default — no silent drops

    Args:
        actor_id:          Calling actor identifier from session
        identity_verified: Whether the actor identity was cryptographically verified
        authority_state:   Full AuthorityState dict from session (compute_authority_state)
        session_id:        Governing kernel session ID
        session_token:     SCT session capability token string (sct_v1.*)
        authority:         Session authority band (OBSERVE_ONLY / LIMITED_MUTATE / FULL)
        allowed_scope:     Verbs the session allows
        intent:            Natural-language intent description
        source_tool:       Kernel tool that initiated the bridge (arif_route / arif_bridge_connect)
        target_organ:      Target organ (GEOX / WEALTH / WELL)
        target_tool:       Target organ tool name
        evidence_layer:    Evidence layer classification (L0-L5)
        reversibility:     reversibility classification (reversible / costly / irreversible)
        constitutional_chain_id: CCID for constitutional audit trail
        trace_id:          Distributed trace identifier

    Returns:
        Full federation envelope dict conforming to the WS9 spec.
    """
    now_iso = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

    # P0 BOUNDARY FIX (2026-07-19): canonicalize the caller identity at the
    # federation envelope boundary. Without this, an ingress "ARIF" arrives
    # here unchanged and the GEOX / WEALTH / WELL validators compare against
    # their canonical-lowercase forms and reject with ACTOR_MISMATCH. The
    # canonical machine actor is lowercase ``arif``; "ARIF" / "Muhammad
    # Arif" / greeting variants collapse via the existing normalizer.
    from arifosmcp.runtime.governance_identity import normalize_actor_id

    canonical_actor = normalize_actor_id(actor_id) if actor_id else None

    # ── Resolve auth state ───────────────────────────────────────────
    effective_actor = canonical_actor or "anonymous"
    effective_verified = bool(identity_verified)
    effective_auth = (authority or "OBSERVE_ONLY").upper()
    if effective_auth not in ("OBSERVE_ONLY", "LIMITED_MUTATE", "FULL", "SOVEREIGN"):
        effective_auth = "OBSERVE_ONLY"

    effective_scope = list(allowed_scope or [])
    effective_ccid = constitutional_chain_id or (session_id or "cc-none")

    # ── Build authority_state section ───────────────────────────────
    # If authority_state provided, use it; otherwise derive minimal from session fields
    if authority_state and isinstance(authority_state, dict):
        auth_section = dict(authority_state)
    else:
        auth_section = {
            "identity": {
                "claimed_actor_id": effective_actor,
                "sovereign_identity": "ARIF_FAZIL",
                "claim_recognized": bool(actor_id),
                "cryptographically_verified": effective_verified,
                "verification_method": "session" if session_id else "none",
                "verification_reason": "workstream_9_bridge",
            },
            "constitutional_role": {
                "role": "SOVEREIGN"
                if effective_auth == "SOVEREIGN"
                else ("OPERATOR" if effective_verified else "ANONYMOUS"),
                "source": "federation_envelope",
            },
            "runtime_grant": {
                "level": effective_auth,
                "source": "session_capability_token" if session_token else "session_store",
                "allowed_verbs": effective_scope,
                "mutation_allowed": effective_auth in ("LIMITED_MUTATE", "FULL", "SOVEREIGN"),
                "seal_allowed": effective_auth in ("FULL", "SOVEREIGN"),
                "expires_at": "",
            },
            "session": {
                "bound": bool(session_id),
                "session_id": session_id or "",
                "actor_bound": bool(actor_id),
            },
            "effective_action_authority": {
                "authorized": effective_verified
                and bool(session_id)
                and effective_auth != "OBSERVE_ONLY",
                "reason_code": (
                    "authorized"
                    if (effective_verified and session_id and effective_auth != "OBSERVE_ONLY")
                    else "observe_only_grant"
                ),
            },
        }

    # ── Request hashes (P0f) — split into raw vs canonical semantic ──
    # raw_request_hash covers actor+session+organ+tool+raw arguments; canonical
    # and alias payloads produce distinct raw hashes because their on-wire
    # shape differs. normalized_payload_hash covers the geological payload
    # only (canonicalised); canonical and alias produce identical normalized
    # hashes, proving physics-layer equivalence.
    raw_request_hash = compute_raw_request_hash(
        actor_id=effective_actor,
        session_id=session_id,
        organ=target_organ,
        tool=target_tool,
        arguments=None,  # raw args are not known at envelope-build time;
                          # the bridge layer stamps this after args are bound.
    )

    # ── Build envelope ──────────────────────────────────────────────
    envelope: dict[str, Any] = {
        "__federation_envelope_version": FEDERATION_ENVELOPE_VERSION,
        "caller": {
            "actor_id": effective_actor,
            "identity_verified": effective_verified,
            "authority_state": auth_section,
        },
        "session": {
            "session_id": session_id or "",
            "session_token": session_token or "",
            "authority": effective_auth,
            "allowed_scope": effective_scope,
        },
        "request": {
            "intent": intent,
            "source_tool": source_tool,
            "target_organ": target_organ,
            "target_tool": target_tool,
            "raw_request_hash": raw_request_hash,
            "normalized_payload_hash": None,  # stamped by bridge after payload normalisation
            # Legacy single hash kept for backward compat with consumers that
            # haven't migrated to raw/normalized split. Equals raw_request_hash
            # when no arguments are bound (envelope build-time).
            "request_hash": raw_request_hash,
        },
        "governance": {
            "evidence_layer": evidence_layer,
            "reversibility": reversibility,
            "constitutional_chain_id": effective_ccid,
            "trace_id": trace_id or _sha256(f"{session_id}-{target_tool}-{time.time()}"),
        },
        "response": {
            "organ_status": "",
            "provenance": "",
            "degradation": None,
            "response_hash": "",
        },
        "_meta": {
            "envelope_version": FEDERATION_ENVELOPE_VERSION,
            "built_at": now_iso,
            "built_by": source_tool or "federation_envelope",
        },
    }

    return envelope


def inject_envelope_into_call_args(
    call_args: dict[str, Any],
    envelope: dict[str, Any],
) -> dict[str, Any]:
    """
    Merge the federation envelope into tool call arguments.
    Never drops existing identity — only upgrades.

    The envelope goes into call_args["_envelope"] as the authoritative source.
    The previous envelope contents are preserved (deep-merged) so organ-side
    bridges that read legacy _envelope fields continue to work.
    """
    args = dict(call_args)
    prev_env = args.get("_envelope")
    if isinstance(prev_env, dict):
        # Deep merge: federation_envelope wins for ws9 keys, legacy preserved for compat
        merged = dict(prev_env)
        merged["__federation_envelope"] = envelope
        # Legacy compat: promote ws9 fields into flat _envelope
        merged["actor_id"] = envelope["caller"]["actor_id"]
        merged["session_id"] = envelope["session"]["session_id"]
        merged["trace_id"] = envelope["governance"]["trace_id"]
        merged["constitutional_chain_id"] = envelope["governance"]["constitutional_chain_id"]
        if envelope["session"]["session_token"]:
            merged["session_token"] = envelope["session"]["session_token"]
        merged["authority"] = envelope["session"]["authority"]
        merged["authority_state"] = envelope["caller"]["authority_state"]
        merged["evidence_layer"] = envelope["governance"]["evidence_layer"]
        merged["reversibility"] = envelope["governance"]["reversibility"]
        args["_envelope"] = merged
    else:
        # First insertion — wrap envelope with legacy compat fields
        args["_envelope"] = {
            "__federation_envelope": envelope,
            "actor_id": envelope["caller"]["actor_id"],
            "session_id": envelope["session"]["session_id"],
            "trace_id": envelope["governance"]["trace_id"],
            "constitutional_chain_id": envelope["governance"]["constitutional_chain_id"],
            **(
                {"session_token": envelope["session"]["session_token"]}
                if envelope["session"]["session_token"]
                else {}
            ),
            "authority": envelope["session"]["authority"],
            "authority_state": envelope["caller"]["authority_state"],
            "evidence_layer": envelope["governance"]["evidence_layer"],
            "reversibility": envelope["governance"]["reversibility"],
        }
    return args


# ═══════════════════════════════════════════════════════════════════════════════
# DEGRADED_CLAIM response structure
# ═══════════════════════════════════════════════════════════════════════════════


def build_degraded_claim(
    *,
    what_degraded: str = "",
    where_degraded: str = "",
    evidence_produced: bool = False,
    result_usable: bool = False,
    next_safe_action: str = "",
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a DEGRADED_CLAIM response block.

    Per bridge rule 6: must name what degraded, where degraded, whether evidence
    was produced, whether result is usable, and the next safe action.

    Args:
        what_degraded:     Description of the degradation (e.g. "identity propagation dropped")
        where_degraded:    Where the degradation occurred (e.g. "WELL bridge dispatch")
        evidence_produced: Whether the organ produced any evidence despite degradation
        result_usable:     Whether the result can be used (maybe partially)
        next_safe_action:  What to do next (e.g. "retry with explicit session_id")
        detail:            Optional additional detail dict

    Returns:
        DEGRADED_CLAIM dict conforming to WS9 spec.
    """
    claim: dict[str, Any] = {
        "degraded_claim": {
            "what_degraded": what_degraded or "unknown degradation",
            "where_degraded": where_degraded or "unknown",
            "evidence_produced": bool(evidence_produced),
            "result_usable": bool(result_usable),
            "next_safe_action": next_safe_action or "investigate and retry",
        }
    }
    if detail:
        claim["degraded_claim"]["detail"] = dict(detail)
    return claim


def attach_degraded_claim(
    response: dict[str, Any],
    *,
    what_degraded: str = "",
    where_degraded: str = "",
    evidence_produced: bool = False,
    result_usable: bool = False,
    next_safe_action: str = "",
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Attach a DEGRADED_CLAIM block to an existing response dict.
    Idempotent — only sets if not already present.
    """
    if not isinstance(response, dict):
        return response
    if "degraded_claim" not in response:
        response["degraded_claim"] = build_degraded_claim(
            what_degraded=what_degraded,
            where_degraded=where_degraded,
            evidence_produced=evidence_produced,
            result_usable=result_usable,
            next_safe_action=next_safe_action,
            detail=detail,
        )["degraded_claim"]
    return response


def finalize_response_envelope(
    response: dict[str, Any],
    envelope: dict[str, Any] | None,
    *,
    organ_status: str = "",
    provenance: str = "",
    degradation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Finalize the response section of a federation envelope after an organ call.

    Computes ``response_hash`` from the response content and stamps the
    ``response`` section with organ status and provenance.

    Args:
        response:   The organ response dict (mutated in place)
        envelope:   The request federation envelope (for echo comparison)
        organ_status: Health/product status of the organ response
        provenance:  Provenance string (e.g. "well_mcp_via_bridge")
        degradation: Optional DEGRADED_CLAIM dict if the call degraded

    Returns:
        The response dict with response envelope fields attached.
    """
    if not isinstance(response, dict):
        return response

    # Compute response hash from actual organ output
    resp_hash = compute_response_hash({k: v for k, v in response.items() if k != "_envelope"})

    # Build response envelope section
    resp_section: dict[str, Any] = {
        "response": {
            "organ_status": organ_status or "unknown",
            "provenance": provenance or "",
            "degradation": degradation or None,
            "response_hash": resp_hash,
        }
    }

    # Echo request envelope for parity check (if available)
    # Handle two shapes:
    #   1. envelope is the raw federation_envelope (has __federation_envelope_version)
    #   2. envelope is call_args["_envelope"] (has __federation_envelope as sub-key)
    if envelope and isinstance(envelope, dict):
        fed_env: dict[str, Any] | None = None
        if "__federation_envelope_version" in envelope:
            fed_env = envelope
        elif "__federation_envelope" in envelope:
            fed_env = envelope["__federation_envelope"]
        if isinstance(fed_env, dict):
            req = fed_env.get("request", {})
            # P0f: echo BOTH raw and normalized hashes so consumers can prove
            # replay integrity (raw) AND physics-layer equivalence (normalized).
            resp_section["response"]["raw_request_hash"] = req.get("raw_request_hash", "")
            resp_section["response"]["normalized_payload_hash"] = req.get(
                "normalized_payload_hash", ""
            )
            # Legacy single hash (kept for backward compat)
            resp_section["response"]["request_hash"] = req.get("request_hash", "")
            resp_section["response"]["target_organ"] = req.get("target_organ", "")
            resp_section["response"]["target_tool"] = req.get("target_tool", "")

    response.update(resp_section)

    # Also attach as top-level envelope_echo for bridge consumers
    response.setdefault("_envelope_echo", {})
    if isinstance(response["_envelope_echo"], dict):
        response["_envelope_echo"] = {
            **response["_envelope_echo"],
            **resp_section.get("response", {}),
        }

    return response


# ═══════════════════════════════════════════════════════════════════════════════
# Direct-vs-bridged parity check
# ═══════════════════════════════════════════════════════════════════════════════


def check_bridge_parity(
    direct_result: dict[str, Any],
    bridged_result: dict[str, Any],
    *,
    key_fields: list[str] | None = None,
    tolerance: float | None = None,
) -> dict[str, Any]:
    """
    Compare direct and bridged organ call results for parity.

    Bridge rule 5: direct and bridged calls with same payload must be comparable.
    This function compares key structural fields between the two results.

    Args:
        direct_result:   Result from a direct MCP call to the organ
        bridged_result:  Result from a bridged call (via arif_route/arif_bridge_connect)
        key_fields:      Fields to compare (default: status, ok, result keys)
        tolerance:       Numerical tolerance for float comparison (default: 0.01)

    Returns:
        Parity report: {parity: bool, mismatches: [...], direct_keys: [...], bridged_keys: [...]}
    """
    if not isinstance(direct_result, dict) or not isinstance(bridged_result, dict):
        return {
            "parity": False,
            "mismatches": ["Both results must be dicts"],
            "direct_result": direct_result,
            "bridged_result": bridged_result,
        }

    if key_fields is None:
        key_fields = ["status", "ok", "verdict", "error"]
        # Also include top-level keys common to both
        common_keys = set(direct_result.keys()) & set(bridged_result.keys())
        key_fields.extend([k for k in common_keys if k not in key_fields])

    mismatches: list[str] = []
    for field in key_fields:
        dv = direct_result.get(field)
        bv = bridged_result.get(field)
        if dv != bv:
            # Numerical tolerance
            if isinstance(dv, (int, float)) and isinstance(bv, (int, float)):
                if tolerance is not None and abs(float(dv) - float(bv)) <= tolerance:
                    continue
            mismatches.append(f"{field}: direct={dv!r} vs bridged={bv!r}")

    # Check that bridged result carries envelope echo
    envelope_echo = bridged_result.get("_envelope_echo") or bridged_result.get("_envelope", {})
    bridged_has_identity = bool(
        isinstance(envelope_echo, dict)
        and (envelope_echo.get("actor_id") or envelope_echo.get("session_id"))
    )

    return {
        "parity": len(mismatches) == 0 and bridged_has_identity,
        "mismatches": mismatches,
        "bridged_has_identity": bridged_has_identity,
        "direct_keys": sorted(direct_result.keys()),
        "bridged_keys": sorted(bridged_result.keys()),
        "bridged_envelope_echo_keys": sorted(envelope_echo.keys())
        if isinstance(envelope_echo, dict)
        else [],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Quick smoke test
    env = build_federation_envelope(
        actor_id="test-agent",
        identity_verified=True,
        session_id="sess-test-001",
        session_token="sct_v1.testtoken",
        authority="LIMITED_MUTATE",
        allowed_scope=["arif_observe", "arif_think"],
        intent="test bridge parity",
        source_tool="arif_bridge_connect",
        target_organ="WELL",
        target_tool="well_health_check",
        evidence_layer="L2",
        reversibility="reversible",
        constitutional_chain_id="cc-test-001",
        trace_id="trace-test-001",
    )

    assert env["__federation_envelope_version"] == FEDERATION_ENVELOPE_VERSION
    assert env["caller"]["actor_id"] == "test-agent"
    assert env["caller"]["identity_verified"] is True
    assert env["session"]["session_id"] == "sess-test-001"
    assert env["session"]["authority"] == "LIMITED_MUTATE"
    assert env["request"]["target_organ"] == "WELL"
    assert env["request"]["target_tool"] == "well_health_check"
    assert env["request"]["request_hash"] is not None
    assert env["governance"]["evidence_layer"] == "L2"
    assert env["governance"]["constitutional_chain_id"] == "cc-test-001"
    assert env["governance"]["trace_id"] == "trace-test-001"

    # Test inject_envelope_into_call_args
    args = inject_envelope_into_call_args({"mode": "health"}, env)
    assert args["_envelope"]["__federation_envelope"] is not None
    assert args["_envelope"]["actor_id"] == "test-agent"
    assert args["_envelope"]["session_id"] == "sess-test-001"

    # Test DEGRADED_CLAIM
    degraded = build_degraded_claim(
        what_degraded="identity_verification_dropped",
        where_degraded="WELL_bridge_dispatch",
        evidence_produced=True,
        result_usable=False,
        next_safe_action="retry_with_explicit_session_id",
    )
    assert degraded["degraded_claim"]["what_degraded"] == "identity_verification_dropped"
    assert degraded["degraded_claim"]["evidence_produced"] is True
    assert degraded["degraded_claim"]["result_usable"] is False

    # Test finalize_response_envelope
    mock_response = {"status": "healthy", "organ": "WELL"}
    finalized = finalize_response_envelope(
        mock_response,
        env,
        organ_status="healthy",
        provenance="well_mcp_via_bridge",
    )
    assert finalized["response"]["organ_status"] == "healthy"
    assert finalized["response"]["response_hash"] is not None
    assert finalized["response"]["request_hash"] == env["request"]["request_hash"]

    # Test check_bridge_parity
    parity = check_bridge_parity(
        {"status": "healthy", "ok": True},
        {
            "status": "healthy",
            "ok": True,
            "_envelope_echo": {"actor_id": "test", "session_id": "s1"},
        },
    )
    assert parity["parity"] is True

    print("✅ federation_envelope self-test passes")
