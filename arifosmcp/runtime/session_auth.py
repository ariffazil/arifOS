"""
arifosmcp/runtime/session_auth.py
════════════════════════════════

Single L11 AUTH validator for all tools.
"""

import json
import logging
import time
from pathlib import Path

from arifosmcp.runtime.governance_identity import is_protected_sovereign_id

logger = logging.getLogger(__name__)

_AGENT_IDENTITIES_PATH = Path("/root/A-FORGE/data/agent_identities.json")

# Trust tier → authority level mapping
_TIER_AUTHORITY_MAP: dict[str, str] = {
    "ELDER": "sovereign",
    "VERIFIED": "operator",
    "TRUSTED": "operator",
    "OBSERVED": "operator",
    "UNVERIFIED": "anonymous",
    "BIRTH": "anonymous",
    "APPRENTICE": "anonymous",
    "DEREGISTERED": "anonymous",
}


# ── Ed25519 registry bootstrap exemption (ACCEPTED RISK — IRR-DIP-AUDIT 2026-07-09) ──
#
# Actors `arif` (F13 SOVEREIGN) and `a-forge` (execution organ) are HARD-CODED
# authority principals. They intentionally BYPASS the Ed25519 identity_proof
# check required of every other agent in agent_identities.json.
#
# WHY (bootstrap / circular dependency):
#   The registry is used to validate actors. Root principals must be able to
#   call into the registry before (or without) being registered with Ed25519
#   proofs — otherwise no one can bootstrap or operate the registry itself.
#
# SCOPE (minimize blast radius):
#   - arif  → authority_level "sovereign" (F13 only)
#   - a-forge → authority_level "operator" (engineering organ)
#   - No other actor_id receives this bypass. Unknown actors → "anonymous".
#
# FUTURE hardening (not blocking):
#   Separate bootstrap credentials with limited scope + rotation, then require
#   Ed25519 even for these two outside the bootstrap path.
#
# Doc: /root/arifOS/docs/ED25519_REGISTRY_BOOTSTRAP_EXEMPTION.md
# Seal reference: A-FORGE/forge_work/IRR-DIP-AUDIT-FINAL.md Priority 3
_ED25519_EXEMPT_SYSTEM_ACTORS: dict[str, str] = {
    # P0 HOTFIX 2026-08-07: string-match "arif" → operator (not sovereign).
    # Exempt from Ed25519 requirement for MCP bootstrap, but WITHOUT
    # cryptographic proof, authority is capped at operator — no judge/seal.
    # Sovereign authority requires Ed25519 signature or SCT token.
    "arif": "operator",
    "a-forge": "operator",
    "forge": "operator",
    "opencode": "operator",
    "hermes": "operator",
    "claude": "operator",
    "claude-code": "operator",
    "deepseek": "operator",
    "kimi": "operator",
    # F13 T3 directive 2026-08-07: sot-cron — Federation SOT/Drift cron.
    # DID registered at /opt/arifos/secrets/did-registry.json (did:arif:sot-cron).
    # Ed25519 keypair at /opt/arifos/secrets/did_sotcron_*.key.
    # authority.py DID gate validates against the registry for FULL authority.
    "sot-cron": "operator",
    "sotcron": "operator",
    # F13 2026-08-08: openclaw — Telegram bridge gateway. Exempt from Ed25519
    # requirement for MCP bootstrap (operator cap). Key reconciled from 4-way
    # fragmentation to canonical device.json Ed25519 keypair.
    # DID: did:arif:openclaw · auth/keys/openclaw_private.key
    "openclaw": "operator",
    # F13 2026-08-12: qwen-code — FI-003 coding harness. Exempt from Ed25519
    # requirement for MCP bootstrap (operator cap). Same class as other FIs.
    "qwen-code": "operator",
}


def _resolve_authority_from_registry(actor_id: str | None) -> str:
    """
    Resolve authority level from agent_identities.json registry.

    System actors `arif` and `a-forge` are Ed25519-exempt bootstrap principals
    (see module constant _ED25519_EXEMPT_SYSTEM_ACTORS and docs/
    ED25519_REGISTRY_BOOTSTRAP_EXEMPTION.md). All other agents need Ed25519
    identity_proof in the registry or they resolve as anonymous.

    T3a 2026-07-17: Case-insensitive lookup. External MCP hosts may send
    "ARIF" or "Arif" — the exempt list keys are lowercase "arif".
    """
    # Hardcoded system actors — Ed25519 registry bootstrap exemption
    # Case-insensitive: external hosts may send "ARIF" or "Arif"
    if actor_id:
        _key = actor_id.strip().lower()
        if _key in _ED25519_EXEMPT_SYSTEM_ACTORS:
            return _ED25519_EXEMPT_SYSTEM_ACTORS[_key]

    # Look up in registry
    if actor_id and _AGENT_IDENTITIES_PATH.exists():
        try:
            registry = json.loads(_AGENT_IDENTITIES_PATH.read_text())
            entry = registry.get(actor_id)
            if entry:
                proof = entry.get("identity_proof", {})
                # Only grant operator+ if agent has Ed25519 identity
                if isinstance(proof, dict) and proof.get("type") == "ed25519":
                    tier = entry.get("trust_tier", "UNVERIFIED")
                    authority = _TIER_AUTHORITY_MAP.get(tier, "anonymous")
                    logger.info(
                        "Session auth: resolved %s → %s (tier=%s, ed25519 verified)",
                        actor_id,
                        authority,
                        tier,
                    )
                    return authority
                else:
                    logger.info(
                        "Session auth: %s has no Ed25519 identity (proof=%s), defaulting to anonymous",
                        actor_id,
                        type(proof).__name__,
                    )
                    return "anonymous"
        except Exception as e:
            logger.warning("Session auth: failed to read registry: %s", e)

    return "anonymous"


SESSION_TTL_SECONDS = 3600  # 1 hour
SESSION_GRACE_SECONDS = 300  # 5 min grace period after TTL


def _get_env_actor() -> None:
    """Deprecated audit stub: implicit actor inheritance is disabled."""
    return None


def _get_env_session() -> None:
    """Deprecated audit stub: implicit session inheritance is disabled."""
    return None


def validate_session(
    session_id: str | None,
    actor_id: str | None = None,
    session_token: str | None = None,
) -> dict:
    """
    Centralized L11 session validator.

    Slice 1 (2026-07-09): SCT-first via resolve_standing.
      1. session_token (signed capability) — no store required
      2. session_id store lookup — legacy, mints SCT on hit
      3. deny

    Identity is request-scoped. Missing identity is never inherited from the
    process environment or a previous invocation.

    Returns: {"valid": bool, "session": dict|None, "reason": str, "actor_id": str|None,
              "session_token": str|None, "source": str, ...}
    """
    if actor_id:
        from arifosmcp.runtime.governance_identity import normalize_actor_id

        actor_id = normalize_actor_id(actor_id) or actor_id.strip().lower()

    # ── SCT-first standing (inhabit path) ─────────────────────────────────────
    try:
        from arifosmcp.runtime.act_token import resolve_standing

        standing = resolve_standing(
            session_token=session_token,
            session_id=session_id,
            actor_id=actor_id,
            allow_store=True,
        )
        # SCT-first: any valid standing, OR explicit token (even if invalid/expired),
        # is authoritative — do not fall through to a different store identity.
        if standing.valid or session_token:
            return standing.as_auth_dict()
        # No token: fall through to the explicit legacy session lookup.
    except Exception as exc:
        logger.warning("SCT resolve_standing failed, legacy path: %s", exc)

    if not session_id:
        return {
            "valid": False,
            "session": None,
            "reason": "L11 AUTH: session_id missing",
            "actor_id": None,
        }

    # ── 1. In-memory lookup (fast path) — legacy ──────────────────────────────
    from arifosmcp.runtime.tools import _SESSIONS

    sess = _SESSIONS.get(session_id)

    # ── 2. Persisted store fallback ───────────────────────────────────────────
    if sess is None:
        try:
            from arifosmcp.runtime.session import _ensure_active_record

            persisted = _ensure_active_record(session_id)
            if persisted:
                # Rehydrate into in-memory store for continuity
                sess = {
                    "session_id": session_id,
                    "actor_id": persisted.get("actor_id", "anonymous"),
                    "created_at": persisted.get("created_at", ""),
                    "created_at_unix": persisted.get("created_at_unix", 0.0),
                    "expires_at_unix": persisted.get("expires_at_unix", float("inf")),
                    "stage": persisted.get("stage", "000"),
                    "lane": persisted.get("lane", "AGI"),
                    "entropy_delta": 0.0,
                    "sealed": False,
                    "trace_packet": persisted.get("trace_packet", {}),
                    "session_warnings": persisted.get("session_warnings", []),
                    "agent_card": persisted.get("agent_card", {}),
                    "model_governance_card": persisted.get("model_governance_card", {}),
                    "constitution_bound": persisted.get("constitution_bound", True),
                    "signature_verified": persisted.get("signature_verified", False),
                }
                _SESSIONS[session_id] = sess
        except Exception:
            pass

    if not sess:
        return {
            "valid": False,
            "session": None,
            "reason": "L11 AUTH: session_id not found or expired",
            "received_session_id": session_id,
            "session_lookup": "not_found",
            "actor_id_received": actor_id,
            "validator": "L11_AUDIT",
            "session_store": "in_memory_and_persisted",
            "implicit_inheritance": False,
        }

        # Legacy env auto-bootstrap intentionally unreachable: retained briefly
        # for audit provenance while request-scoped isolation is deployed.
        # ── 2b. Auto-bootstrap: env var session with no prior record ────────────
        # If session_id came from env vars (ARIFOS_SESSION_ID / ARIFOS_DEFAULT_SESSION_ID)
        # AND actor_id came from env vars, the deployer explicitly configured this
        # autonomous governance context. Create the session now rather than failing —
        # this is the intended sovereign bootstrap path for container-to-container MCP.
        env_session_id = _get_env_session()
        env_actor_id = _get_env_actor()
        auto_bootstrapped = (
            session_id == env_session_id  # session_id was sourced from env
            and env_actor_id  # and we also have an env actor_id
        )
        if auto_bootstrapped:
            try:
                from arifosmcp.runtime.session import bind_session_identity

                bind_session_identity(
                    session_id=session_id,
                    actor_id=env_actor_id or "anonymous",
                    authority_level=_resolve_authority_from_registry(env_actor_id),
                    auth_context={
                        "source": "validate_session",
                        "mode": "auto_bootstrap",
                        "via": "env_var_fallback",
                    },
                    stage="000",
                    # WS2 (2026-07-12): removed default SEAL on auto-bootstrap.
                    # Auto-bootstrap sessions start as verdict=None and
                    # gain verdict only when the judge path CLEARs them. An
                    # unfilled verdict is substrate-conservative; a default
                    # SEAL was a substrate-overclaim that polluted every
                    # warm-boot session.
                    governance={"verdict": None, "trace_packet": None},
                )
                # Re-fetch the freshly created session
                try:
                    from arifosmcp.runtime.session import _ensure_active_record

                    persisted = _ensure_active_record(session_id)
                    if persisted:
                        sess = {
                            "session_id": session_id,
                            "actor_id": persisted.get("actor_id", env_actor_id),
                            "created_at": persisted.get("created_at", ""),
                            "created_at_unix": persisted.get("created_at_unix", time.time()),
                            "expires_at_unix": (
                                persisted.get("expires_at_unix", time.time() + SESSION_TTL_SECONDS)
                            ),
                            "stage": persisted.get("stage", "000"),
                            "lane": persisted.get("lane", "AGI"),
                            "entropy_delta": 0.0,
                            "sealed": False,
                            "trace_packet": persisted.get("trace_packet", {}),
                            "session_warnings": persisted.get("session_warnings", []),
                            "agent_card": persisted.get("agent_card", {}),
                            "model_governance_card": persisted.get("model_governance_card", {}),
                            "constitution_bound": persisted.get("constitution_bound", True),
                            "signature_verified": persisted.get("signature_verified", False),
                        }
                        from arifosmcp.runtime.tools import _SESSIONS

                        _SESSIONS[session_id] = sess
                except Exception:
                    pass
            except Exception:
                pass

        if not sess:
            return {
                "valid": False,
                "session": None,
                "reason": "L11 AUTH: session_id not found or expired",
                "received_session_id": session_id,
                "session_lookup": "not_found",
                "actor_id_received": actor_id,
                "validator": "L11_AUDIT",
                "session_store": "in_memory_and_persisted",
                "auto_bootstrap_attempted": auto_bootstrapped,
            }

    # ── 3. TTL Check with grace period ────────────────────────────────────────
    expires_at = sess.get("expires_at_unix", float("inf"))
    now = time.time()
    if now > expires_at + SESSION_GRACE_SECONDS:
        # MASTER FORGE W9: structured SESSION_EXPIRED — not a geometry/schema error
        return {
            "valid": False,
            "error": "SESSION_EXPIRED",
            "can_retry": True,
            "next_safe_action": "Call arif_init and replay the same normalized payload",
            "reason": "L11 AUTH: session expired (24h limit + grace exceeded)",
            "expired": True,
            "previous_session_id": session_id,
            "created_at": sess.get("created_at"),
            "expires_at_unix": expires_at,
            "ttl_seconds": SESSION_TTL_SECONDS,
            "grace_seconds": SESSION_GRACE_SECONDS,
            "validator": "L11_AUDIT",
        }

    # ── 4. Protected sovereign ID must be signature-verified ─────────────────
    sess_actor = sess.get("actor_id", "")
    if is_protected_sovereign_id(sess_actor) and not sess.get("signature_verified", False):
        # T3a 2026-07-17: Ed25519-exempt system actors bypass the signature
        # requirement. The exempt list declares these actors as bootstrap
        # principals that can claim their identity without cryptographic proof.
        sess_actor_key = sess_actor.strip().lower() if sess_actor else ""
        if sess_actor_key in _ED25519_EXEMPT_SYSTEM_ACTORS:
            logger.info(
                "T3a: Ed25519-exempt actor %s bypasses protected ID signature check",
                sess_actor,
            )
        else:
            return {
                "valid": False,
                "session": sess,
                "reason": (
                    "L11 AUTH: Protected sovereign ID claimed without verified signature. "
                    "Actor IDs matching PROTECTED_SOVEREIGN_IDS require Ed25519 signature "
                    "verification through arif_session_init. Use a valid actor_signature "
                    "or use an unprivileged actor_id."
                ),
                "actor_id_claimed": sess_actor,
                "signature_verified": False,
                "required_action": "arif_session_init with valid actor_signature",
            }

    # ── 5. Actor ID mismatch ──────────────────────────────────────────────────
    sess_actor_normalized = sess.get("actor_id")
    if sess_actor_normalized:
        from arifosmcp.runtime.governance_identity import normalize_actor_id

        sess_actor_normalized = (
            normalize_actor_id(str(sess_actor_normalized))
            or str(sess_actor_normalized).strip().lower()
        )
    if actor_id and sess_actor_normalized != actor_id:
        return {
            "valid": False,
            "session": sess,
            "reason": "L11 AUTH: actor_id mismatch",
            "actor_id_received": actor_id,
            "actor_id_on_session": sess.get("actor_id"),
        }

    # ── 6. TTL refresh (continuity improvement) ───────────────────────────────
    if now > expires_at - (SESSION_TTL_SECONDS // 2):
        # Session is past half-life: refresh TTL
        new_expires = now + SESSION_TTL_SECONDS
        sess["expires_at_unix"] = new_expires
        try:
            from arifosmcp.runtime.session import _touch_record

            _touch_record(session_id, {"expires_at_unix": new_expires})
        except Exception:
            pass

    return {
        "valid": True,
        "session": sess,
        "reason": "L11 AUTH: session valid",
        "actor_id": sess.get("actor_id"),
        "created_at": sess.get("created_at"),
        "stage": sess.get("stage"),
    }
