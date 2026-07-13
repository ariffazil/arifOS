"""
arifosmcp/tools/vault_seal.py — 999_VAULT
═════════════════════════════════════════

Immutable ledger and audit engine.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, Literal

# Sync core accepts ack_irreversible. Async MCP wrapper (_arif_seal /
# _arif_vault_seal_tool) dropped that kwarg 2026-07-07 — do not call it here.
from arifosmcp.runtime.tools import _arif_vault_seal
from arifosmcp.schemas.verdict import SealOutput
from arifosmcp.models.verdicts import Verdict


async def arif_seal(
    mode: Literal["seal", "verify", "chain", "list", "dry_run", "seal_card", "render"] = "seal",
    payload: str = "",
    session_id: str | None = None,
    session_token: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    actor_signature: str | None = None,
    nonce: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    witness_type: str = "ai",
    drift_events: list[dict] | None = None,
    verdict: str = "SEAL",
    floors: dict | None = None,
    witness: dict | None = None,
    trace_root: str | None = None,
    policy_digest: str | None = None,
    cooldown_entry_id: str | None = None,
    genesis_card_hash: str | None = None,
) -> SealOutput:
    """
    999_VAULT: Immutable ledger anchoring.

    Args:
        cooldown_entry_id: If provided, the seal is gated on SABAR cooldown completion.
            Without it, cooldown is logged as bypassed (legacy compat path).
            Internal hardening — no new tool surface.
        session_token: SCT (sct_v1) preferred standing from arif_init.
    """
    # ── SCT standing (Spine P0) ──
    _standing_token = session_token
    _standing_source = None
    _standing_apex: dict[str, Any] | None = None
    _standing_actor_verified = False
    _standing_authority: str | None = None
    _standing_delta: dict[str, Any] | None = None
    if session_token or session_id:
        try:
            from arifosmcp.runtime.sct import resolve_standing

            _standing = resolve_standing(
                session_id=session_id,
                actor_id=actor_id,
                session_token=session_token,
                allow_store=True,
            )
            if _standing.valid:
                _standing_token = _standing.session_token or session_token
                _standing_source = _standing.source
                _standing_apex = dict(_standing.apex) if _standing.apex else None
                _standing_actor_verified = _standing.actor_verified
                _standing_authority = _standing.authority
                _standing_delta = _standing.authority_delta
                if _standing.session_id:
                    session_id = _standing.session_id
                if _standing.actor_id and _standing.actor_id != "anonymous":
                    actor_id = _standing.actor_id
            elif session_token:
                return _echo_standing(
                    SealOutput(
                        mode=mode,
                        status="HOLD",
                        verdict="HOLD",
                        reasons=[_standing.reason or "L11 AUTH: SCT invalid"],
                        next_safe_action="Call arif_init and pass session_token",
                        entry_id="",
                        actor_id=actor_id,
                        meta={
                            "sesat_event": {
                                "sesat": True,
                                "type": "TOKEN_INVALID",
                                "reason": _standing.reason,
                            },
                            "gate": "L11_SCT_GATE",
                            "session_token_prefix": (session_token or "")[:24],
                        },
                    )
                )
        except Exception:
            pass

    def _echo_standing(out: SealOutput) -> SealOutput:
        """Echo next-hop SCT continuity onto a direct SealOutput."""
        if not _standing_token:
            return out
        data = out.model_dump(mode="json")
        data["session_token"] = _standing_token
        data["standing_source"] = _standing_source or "sct"
        if _standing_apex is not None:
            data["apex_scalars"] = _standing_apex
        data["authority"] = _standing_authority or "OBSERVE_ONLY"
        data["actor_verified"] = _standing_actor_verified
        if _standing_delta is not None:
            data["authority_delta"] = _standing_delta
        res = data.get("result")
        if isinstance(res, dict):
            res.setdefault("session_token", _standing_token)
            res.setdefault("standing_source", _standing_source or "sct")
            if _standing_apex is not None:
                res.setdefault("apex_scalars", _standing_apex)
        return SealOutput(**data)

    # ── GÖDEL-LOCK (Mission 001): No self-certification ──
    # The actor of an IRREVERSIBLE mutation cannot be the final certifier.
    # Enforced at the SEAL boundary — the last gate before Vault999 write.
    if mode == "seal" and ack_irreversible:
        judge_session_id = session_id
        actor_session_id = actor_id  # the session that originated the action
        # If actor == judge, block self-certification
        if actor_session_id and judge_session_id and actor_session_id == judge_session_id:
            return _echo_standing(
                SealOutput(
                    mode=mode,
                    verdict="HOLD",
                    payload=payload,
                    status="GODEL_LOCK",
                    chain_ok=False,
                    entry_id="",
                    created_at="",
                    note=(
                        f"GÖDEL-LOCK: actor {actor_session_id} cannot certify its own "
                        f"IRREVERSIBLE action. Requires separate judge session (F13 SOVEREIGN or "
                        f"independent 888 JUDGE). This is an illegal state — the system cannot "
                        f"self-certify."
                    ),
                )
            )
        # witness required for IRREVERSIBLE
        if not witness:
            return _echo_standing(
                SealOutput(
                    mode=mode,
                    verdict="HOLD",
                    payload=payload,
                    status="MISSING_WITNESS",
                    chain_ok=False,
                    entry_id="",
                    created_at="",
                    note=(
                        "GÖDEL-LOCK: IRREVERSIBLE seal requires a non-null witness. "
                        "No witness_id provided. An external witness (human, signed sensor, "
                        "or vault anchor) must attest to this action."
                    ),
                )
            )

    # ── AKAL I5: Latency enforcement ─────────────────────────────────────────
    from arifosmcp.core.akal_wiring import akal_pre_seal as _akal_latency

    try:
        _akal_lat = _akal_latency(
            session_id=session_id,
            blast_radius="irreversible" if not ack_irreversible else "high",
            passes_completed=1,  # Default — actual count from session
            branches_explored=1,
            cooling_elapsed=0,
        )
        if not _akal_lat.get("proceed"):
            # Latency requirements not met — log but dont block (advisory for now)
            pass
    except Exception:
        pass  # AKAL latency is advisory

    # ── SABAR cooldown gate (internal hardening) ──
    cooldown_meta: dict = {}
    if mode == "seal" and payload:
        try:
            from arifosmcp.core.cooldown_engine import get_cooldown_engine

            engine = get_cooldown_engine()
            if cooldown_entry_id:
                entry = engine.check(cooldown_entry_id)
                if entry and entry.verdict == "SEAL":
                    cooldown_meta["cooldown"] = "verified"
                    cooldown_meta["cooldown_entry_id"] = cooldown_entry_id
                elif entry:
                    cooldown_meta["cooldown"] = "pending"
                    cooldown_meta["cooldown_entry_id"] = cooldown_entry_id
                    cooldown_meta["cooldown_remaining_hours"] = entry.remaining_hours
                    cooldown_meta["cooldown_verdict"] = entry.verdict
                else:
                    cooldown_meta["cooldown"] = "not_found"
            else:
                # Legacy path — no cooldown entry, log bypass + increment counter
                auto_entry = engine.propose(
                    artifact_ref=(
                        f"vault:{session_id or 'anon'}:"
                        f"{hashlib.md5(payload.encode()).hexdigest()[:8]}"  # nosec
                    ),
                    description="auto-registered from vault seal (legacy compat)",
                    risk_tier="low",
                    session_id=session_id,
                )
                bypass_n = engine.record_bypass()
                cooldown_meta["cooldown"] = "bypassed"
                cooldown_meta["cooldown_entry_id"] = auto_entry.entry_id
                cooldown_meta["cooldown_bypass_count"] = bypass_n
                cooldown_meta["cooldown_note"] = (
                    f"legacy compat — cooldown bypassed (bypass #{bypass_n}). "
                    f"Will hard-enforce in Stage 2C."
                )
        except Exception:
            cooldown_meta["cooldown"] = "unavailable"

    # ── arif_verify: Cryptographic SEAL token verification (E1 Fix) ───────────
    # A-FORGE calls this via MCP before executing any IRREVERSIBLE shell command.
    # Validates: token exists + not expired + not replayed + command hash matches.
    # Returns: {token_valid, scope_valid, replay_safe, violations}
    if mode == "verify":
        _verify_token = session_token  # A-FORGE passes seal token via session_token
        _verify_command = payload  # payload = the shell command string
        _verify_actor = actor_id or "ARIF"

        if not _verify_token:
            return _echo_standing(
                SealOutput(
                    mode=mode,
                    verdict=Verdict.HOLD,
                    status="GATE_HOLD",
                    reasons=["arif_verify: no token provided"],
                    next_safe_action="Pass session_token parameter",
                    entry_id="",
                    actor_id=_verify_actor,
                    meta={"gate": "VERIFY_TOKEN_MISSING"},
                )
            )

        if not _verify_command:
            return _echo_standing(
                SealOutput(
                    mode=mode,
                    verdict=Verdict.HOLD,
                    status="GATE_HOLD",
                    reasons=["arif_verify: no command provided — pass shell command as payload"],
                    next_safe_action="Pass shell command string as payload parameter",
                    entry_id="",
                    actor_id=_verify_actor,
                    meta={"gate": "VERIFY_COMMAND_MISSING"},
                )
            )

        # Delegate to canonical vault_registry.verify_seal
        from arifosmcp.runtime.vault_registry import verify_seal as _vault_verify_seal

        _verify_result = _vault_verify_seal(
            token=_verify_token,
            command=_verify_command,
            actor_id=_verify_actor,
        )

        _verify_status = (
            "PASS"
            if (
                _verify_result.get("token_valid")
                and _verify_result.get("scope_valid")
                and _verify_result.get("replay_safe")
            )
            else "GATE_HOLD"
        )
        _verify_verdict = Verdict.SEAL if _verify_status == "PASS" else Verdict.HOLD

        return _echo_standing(
            SealOutput(
                mode=mode,
                verdict=_verify_verdict,
                status=_verify_status,
                reasons=_verify_result.get("violations", []),
                next_safe_action=(
                    "A-FORGE: proceed with execution"
                    if _verify_status == "PASS"
                    else f"A-FORGE GATE_HOLD — violations: {_verify_result.get('violations', [])}"
                ),
                entry_id=_verify_result.get("entry", {}).get("entry_id", "")
                if isinstance(_verify_result.get("entry"), dict)
                else "",
                actor_id=_verify_actor,
                meta={
                    "gate": "ARIF_VERIFY",
                    "verification_path": [
                        f"token:{_verify_token[:16] if _verify_token else 'none'}...",
                        f"entry:{_verify_result.get('entry', {}).get('entry_id', 'none')}",
                        f"command_hash:{_verify_result.get('entry', {}).get('command_hash', 'unknown')[:16] if isinstance(_verify_result.get('entry'), dict) else 'none'}...",
                        f"token_valid:{_verify_result.get('token_valid', False)}",
                        f"scope_valid:{_verify_result.get('scope_valid', False)}",
                        f"replay_safe:{_verify_result.get('replay_safe', False)}",
                        f"verdict:{_verify_verdict}",
                    ],
                    "token_valid": _verify_result.get("token_valid", False),
                    "scope_valid": _verify_result.get("scope_valid", False),
                    "replay_safe": _verify_result.get("replay_safe", False),
                    "violations": _verify_result.get("violations", []),
                    "command_hash": _verify_result.get("entry", {}).get("command_hash", "")
                    if isinstance(_verify_result.get("entry"), dict)
                    else "",
                },
            )
        )

    if mode in ("seal_card", "render"):
        return _echo_standing(
            _build_seal_card(
                verdict=verdict,
                floors=floors,
                witness=witness,
                trace_root=trace_root,
                policy_digest=policy_digest,
                mode=mode,
            )
        )

    result = _arif_vault_seal(
        mode=mode,
        payload=payload,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
        actor_id=actor_id,
        actor_signature=actor_signature,
        nonce=nonce,
        constitutional_chain_id=constitutional_chain_id,
        judge_state_hash=judge_state_hash,
        witness_type=witness_type,
        drift_events=drift_events,
        floors=floors,
    )

    # ── E1 FIX: Mint cryptographic SEAL token for IRREVERSIBLE actions ─────────
    # After arif_seal approves (mode="seal" + ack_irreversible), mint a token
    # bound to the exact payload hash. A-FORGE must verify this token via
    # arif_verify before execution. One-time use — token is burned on first use.
    _seal_token_value: str | None = None
    if result.get("verdict") == "SEAL" and mode == "seal" and ack_irreversible and payload:
        _payload_hash = hashlib.sha256(payload.encode()).hexdigest()
        # Delegate to canonical vault_registry — thread-safe, dual-write to VAULT999
        from arifosmcp.runtime.vault_registry import issue_seal

        _seal_token_value = issue_seal(payload=payload, actor_id=actor_id)
        result["seal_token"] = _seal_token_value
        result["payload_hash"] = f"sha256:{_payload_hash}"
        result["meta"] = result.get("meta", {})
        result["meta"]["e1_seal_token"] = {
            "token": _seal_token_value,
            "payload_hash": f"sha256:{_payload_hash}",
            "note": "A-FORGE must call arif_verify before execution",
        }

    # ── P0-3: Genesis card binding (AAA warga ignition) ────────────────
    # Auto-load genesis_card_hash from genesis_card.yaml if not provided.
    # v42.0 doc promises: "every vault witness entry must have the binding"
    # but schema didn't carry genesis_card_hash. This closes the gap.
    _resolved_genesis_hash = genesis_card_hash
    if not _resolved_genesis_hash:
        try:
            _genesis_path = "/root/AAA/registries/genesis/genesis_card.yaml"
            with open(_genesis_path, "r") as _gf:
                _gdata = _gf.read()
                import hashlib as _g_hashlib

                _resolved_genesis_hash = (
                    f"sha256:{_g_hashlib.sha256(_gdata.encode()).hexdigest()[:32]}"
                )
        except Exception:
            _resolved_genesis_hash = None

    if _resolved_genesis_hash and "meta" not in result:
        result["meta"] = {}
    if _resolved_genesis_hash:
        result["meta"]["genesis_card_hash"] = _resolved_genesis_hash

    if cooldown_meta:
        result["meta"] = result.get("meta", {})
        result["meta"]["sabar_cooldown"] = cooldown_meta
    # Backward-compat alias (deprecated 2026-06-06)
    if "meta" in result:
        _meta = result["meta"]
        if "violated_laws" in _meta and "failed_floors" not in _meta:
            _meta["failed_floors"] = [
                f"F{int(v[1:]):02d}" if v.startswith("L") and v[1:].isdigit() else v
                for v in _meta["violated_laws"]
            ]
    return _echo_standing(SealOutput(**result))


def _build_seal_card(
    verdict: str,
    floors: dict | None,
    witness: dict | None,
    trace_root: str | None,
    policy_digest: str | None,
    mode: str,
) -> SealOutput:
    """Build structured constitutional seal data (read-only, no irreversible write)."""
    from arifosmcp.runtime.rest_routes import _build_governance_status_payload

    payload = _build_governance_status_payload()
    seal_data = {
        "verdict": verdict,
        "floors": floors or payload.get("floors", {}),
        "witness": witness or payload.get("witness", {}),
        "trace_root": trace_root,
        "policy_digest": policy_digest,
        "mode": mode,
    }

    if mode == "render":
        seal_data["_meta"] = {"ui": {"domain": "web-sandbox.oaiusercontent.com"}}

    return SealOutput(
        entry_id=f"card_{hash(str(seal_data)) & 0xFFFFFFFF:08x}",
        chain_hash=trace_root or "unsigned",
        timestamp=payload.get("telemetry", {}).get("timestamp") or "0",
        permanence_flag=False,
        status="OK",
        tool="arif_seal",
        mode=mode,
        seal_data=seal_data,
    )


# Backward compatibility alias
arif_vault_seal = arif_seal
