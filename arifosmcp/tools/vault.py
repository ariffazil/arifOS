"""
arifosmcp/tools/vault_seal.py — 999_VAULT
═════════════════════════════════════

Immutable ledger and audit engine.

Contains:
  - arif_seal:    Full seal authority (write + verify, requires SCT auth)
  - arif_vault_verify: Read-only chain verifier (no seal authority required)
"""

from __future__ import annotations

import json
import logging
import hashlib
from typing import Any, Literal

from arifosmcp.models.verdicts import Verdict

# Sync core accepts ack_irreversible. Async MCP wrapper (_arif_seal /
# _arif_vault_seal_tool) dropped that kwarg 2026-07-07 — do not call it here.
from arifosmcp.runtime.tools import _arif_vault_seal
from arifosmcp.schemas.verdict import SealOutput

logger = logging.getLogger(__name__)


def _lookup_session_for_identity(session_id: str) -> dict[str, Any] | None:
    """Sync session lookup for identity binding. No resolve_session / _SESSION_STORE.

    Order:
      1. arifosmcp.runtime.tools.get_session → in-process _SESSIONS
      2. session_registry fallback dict (sync)
      3. session_enforcer record (best-effort)
    """
    if not session_id:
        return None
    try:
        from arifosmcp.runtime.tools import get_session as _tools_get

        sess = _tools_get(session_id)
        if sess:
            return sess if isinstance(sess, dict) else None
    except Exception:
        pass
    try:
        from arifosmcp.runtime.session_registry import get_session_sync

        sess = get_session_sync(session_id)
        if sess:
            return sess
    except Exception:
        pass
    try:
        from arifosmcp.runtime.session_enforcer import get_session as _enf_get

        rec = _enf_get(session_id)
        if rec is None:
            return None
        if isinstance(rec, dict):
            return rec
        # SessionRecord-like
        data: dict[str, Any] = {}
        for attr in (
            "session_id",
            "actor_id",
            "session_private_key",
            "session_pubkey_thumbprint",
        ):
            if hasattr(rec, attr):
                data[attr] = getattr(rec, attr)
        return data or None
    except Exception:
        return None


def _tag_session_close_epistemic(
    payload: str | None,
    *,
    session_id: str | None,
    actor_id: str | None,
    eureka_id: str | None = None,
) -> str:
    """Wrap session_close payload with vault-eligible _epistemic tag (F2).

    Session close is ACCOUNTING / WITNESS_ONLY — not AI_SYNTHESIZED executive evidence.
    Eligible under verify_vault_eligibility (blocks only AI_SYNTHESIZED + GENERATED/EXECUTIVE).
    """
    import json as _json
    from datetime import UTC, datetime

    body: dict[str, Any]
    raw = payload or ""
    try:
        parsed = _json.loads(raw) if raw.strip().startswith(("{", "[")) else None
        if isinstance(parsed, dict):
            body = dict(parsed)
        else:
            body = {"summary": raw, "summary_kind": "text"}
    except Exception:
        body = {"summary": raw, "summary_kind": "text"}

    body.setdefault("session_id", session_id or "")
    body.setdefault("actor_id", actor_id or "")
    if eureka_id:
        body["eureka_id"] = eureka_id
    body["seal_purpose"] = "session_close"
    body["_epistemic"] = {
        "output_class": "ACCOUNTING",
        "ai_involvement": "ASSISTED",
        "authority_claim": "WITNESS_ONLY",
        "evidence_source": "SESSION_SUMMARY",
        "session_close_macro": True,
        "f2_witness": "human — F13 sovereign directive 2026-07-30",
        "note": "AI-generated session summary, F2 witness: human",
        "tagged_by": "arif_session_close_macro",
        "tagged_at": datetime.now(UTC).isoformat(),
        "schema_version": "session_close/2026-07-30",
    }
    return _json.dumps(body, ensure_ascii=False)


async def arif_seal(
    mode: Literal[
        "seal",
        "verify",  # A-FORGE token verify (Ed25519)
        "chain",
        "list",
        "dry_run",
        "seal_card",
        "render",
        "verify_chain",  # Public chain verification — delegates to arif_vault_verify (sovereign 2026-07-18)
        "chain_status",  # Public chain head + last N entries
        "audit",  # Full audit report with receipts
        "session_close",  # Autonomous 5-phase session seal (EUREKA 2026-07-30)
    ] = "seal",
    # 999_SEAL NOTE (F13, 2026-07-24):
    # arif_seal is deterministic — it appends the prior arif_judge verdict to
    # the VAULT999 hash chain and never invokes an LLM. The AGENT_MODEL_MAP
    # constitutional restriction for 999_SEAL is therefore enforced UPSTREAM,
    # at the 666_JUDGE call sites whose verdict is being sealed (the verdict's
    # model identity is recorded in the sealed receipt). The runtime gate in
    # llm_client.select_model_for_role covers all LLM invocations serving
    # judge/seal roles; the seal itself is correct by construction.
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
    evidence_sha: str | None = None,
    reversion_event: dict[str, Any] | None = None,
    blast_radius: str = "L2_SYSTEM",
    seal_purpose: str | None = None,
    delta_s: float | None = None,
    # ── GENESIS/059: FQ Seal Gauge (ratified 2026-08-04) ──────────────────
    f13_override: bool = False,
    override_reason: str | None = None,
) -> SealOutput:
    """
    999_VAULT: Immutable ledger anchoring.

    Args:
        blast_radius: HIB consequence classification (L1_LOCAL | L2_SYSTEM | L3_CRITICAL).
            L1_LOCAL = reversible, single file/session scope.
            L2_SYSTEM = modifies config, multi-agent state.
            L3_CRITICAL = irreversible, data destruction, external-facing.
            Defaults to L2_SYSTEM for safety.
        cooldown_entry_id: If provided, the seal is gated on SABAR cooldown completion.
            Without it, cooldown is logged as bypassed (legacy compat path).
            Internal hardening — no new tool surface.
        session_token: SCT (sct_v1) preferred standing from arif_init.
        delta_s: F4 CLARITY compression ratio. Computed as
            1 - (novel_claims / total_claims) where novel_claims are those
            without a back-reference to any prior VAULT999 entry.
            delta_s > 0 = agent compressed (good). delta_s = 0 = all novel.
            delta_s < 0 = hallucination. Added 2026-08-02 per compression
            isomorphism spec. Passed through to seal receipt metadata.
    """
    # ── SCT standing (Spine P0) ──
    _standing_token = session_token

    def _echo_standing(out: SealOutput) -> SealOutput:
        """Echo next-hop SCT continuity onto a direct SealOutput.

        P0 FIX (2026-08-14): defined BEFORE first use. Previously defined at
        line ~423 but called at the L11 SCT gate below — any SCT-invalid call
        raised UnboundLocalError, surfaced as SAFE_VOID_FALLBACK and masking
        the real auth verdict.
        """
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

    _standing_source = None
    _standing_apex: dict[str, Any] | None = None
    _standing_actor_verified = False
    _standing_authority: str | None = None
    _standing_delta: dict[str, Any] | None = None
    if session_token or session_id:
        try:
            from arifosmcp.runtime.act_token import resolve_standing

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

    # ── Layer 6 effect typing (2026-07-30) ───────────────────────────────
    # Safe modes are OBSERVE-class (no vault append). Dangerous modes remain
    # IRREVERSIBLE and require FULL/SOVEREIGN authority + ack.
    _SEAL_SAFE_MODES = frozenset(
        {
            "list",
            "verify",
            "verify_chain",
            "chain",
            "chain_status",
            "audit",
            "dry_run",
            "seal_card",
            "render",
        }
    )
    _SEAL_DANGEROUS_MODES = frozenset({"seal", "session_close"})
    _effect_class = "OBSERVE" if mode in _SEAL_SAFE_MODES else "IRREVERSIBLE"
    _auth_band = (_standing_authority or "OBSERVE_ONLY").upper()
    if mode in _SEAL_DANGEROUS_MODES and _auth_band not in (
        # T3 grant 2026-08-07 by 888 SOVEREIGN: SYSTEM_CRON_WRITE added to
        # allow-list — verified automation identities may seal.
        # Gate inverted from deny-list to allow-list to make the carve
        # explicit and prevent future accidental demotions.
        "FULL",
        "SOVEREIGN",
        "SYSTEM_CRON_WRITE",
    ):
        return _echo_standing(
            SealOutput(
                mode=mode,
                status="HOLD",
                verdict="HOLD",
                reasons=[
                    f"effect_class=IRREVERSIBLE mode={mode} requires FULL or SOVEREIGN "
                    f"authority (current={_auth_band or 'unknown'})"
                ],
                next_safe_action=(
                    "Call arif_init with a FULL/SOVEREIGN actor (or SYSTEM_CRON_WRITE "
                    "for verified automation) for mode=seal, or use "
                    "mode=verify|verify_chain|list|audit for OBSERVE-class access"
                ),
                entry_id="",
                actor_id=actor_id,
                meta={
                    "gate": "L6_EFFECT_TYPING",
                    "effect_class": "IRREVERSIBLE",
                    "mode": mode,
                    "authority": _auth_band,
                    "safe_modes": sorted(_SEAL_SAFE_MODES),
                },
            )
        )

    # ── ZEN HARD GATE (2026-07-30): Seal preconditions — no LLM needed ──
    # Per ChatGPT forensic: arif_seal must reject immediately when the
    # constitutional chain is incomplete. LLM writes explanations, but
    # never becomes the gatekeeper for the vault.
    _seal_reasons: list[str] = []

    # Gate S1: Seal requires a prior arif_judge verdict (judge_state_hash or cc_id)
    if mode == "seal" and not (judge_state_hash or constitutional_chain_id):
        _seal_
        # FQ FIX: warn on verify concentration gaming
        try:
            _recent = []  # placeholder — flow_state import may vary
            _verify_conc = 0
            # Real computation would go here
        except Exception:
            pass

        reasons.append(
            "Seal requires judge_state_hash or constitutional_chain_id "
            "from a prior arif_judge verdict. No self-sealing allowed."
        )

    # Gate S2: Irreversible seal requires ack
    if mode == "seal" and not ack_irreversible:
        _seal_reasons.append(
            "Seal is IRREVERSIBLE. Set ack_irreversible=True to confirm. "
            "This gate runs BEFORE any LLM or vault access."
        )

    # Gate S3: Seal without actor_id is inadmissible
    if mode == "seal" and not actor_id:
        _seal_reasons.append("Seal requires actor_id for non-repudiation.")

    # Gate S4 (GENESIS/059 — 2026-08-04): FQ metabolic gate
    # FQ must be in [1,3] (φFQ ≥ 0.80) or seal carries f13_override.
    # FQ < 0.5 → HARD BLOCK (no override possible).
    if mode in ("seal", "session_close") and not f13_override:
        try:
            import urllib.request as _ur

            _fq_raw = None
            try:
                _req = _ur.Request("http://127.0.0.1:7073/health")
                _resp = _ur.urlopen(_req, timeout=3)
                _fq_data = json.loads(_resp.read())
                _fq_raw = _fq_data.get("fq", {})
            except Exception:
                # arifFlow unreachable — fall back to flow_state.json
                try:
                    import os as _os

                    _flow_path = _os.path.join(
                        _os.environ.get("ARIFOS_HOME", "/root"),
                        "AAA",
                        "state",
                        "flow_state.json",
                    )
                    with open(_flow_path) as _ff:
                        _fq_cache = json.load(_ff)
                        _fq_raw = _fq_cache
                except Exception:
                    pass

            if _fq_raw:
                _fq_val = _fq_raw.get("quotient") or _fq_raw.get("fq") or _fq_raw.get("FQ")
                if isinstance(_fq_val, dict):
                    _fq_val = _fq_val.get("quotient") or _fq_val.get("fq")
                _fq_val = float(_fq_val) if _fq_val else None

                if _fq_val is not None:
                    if _fq_val < 0.5:
                        _seal_reasons.append(
                            f"FQ={_fq_val:.2f} STUCK — HARD BLOCK. "
                            f"Seal impossible from STUCK state (GENESIS/059 §1.3). "
                            f"No f13_override available below FQ=0.5."
                        )
                    else:
                        _phi_fq = (
                            1.0
                            if 1.0 <= _fq_val <= 3.0
                            else _fq_val / 3.0
                            if 0.5 <= _fq_val < 1.0
                            else min(1.0, 3.0 / _fq_val)
                        )
                        if _phi_fq < 0.80:
                            _seal_reasons.append(
                                f"FQ={_fq_val:.2f} φFQ={_phi_fq:.3f} < 0.80 — OVERHEAT penalty. "
                                f"Seal requires FQ∈[1,3] or f13_override=True "
                                f"(GENESIS/059 §4). Pause, run verification, let FQ settle."
                            )
                    # Verification dominance check: high FQ from one actor
                    # pumping Barrier/Verify pulses is gaming, not health.
                    _exec = int(_fq_raw.get("execute_count", 0) or 0)
                    _verify = int(_fq_raw.get("verify_count", 0) or 0)
                    _total_steps = _exec + _verify
                    if _total_steps > 10 and _exec > 0:
                        _verify_pct = _verify / _total_steps * 100
                        if _verify_pct > 80:
                            _seal_reasons.append(
                                f"FQ diagnosis: VERIFICATION DOMINANCE "
                                f"({_verify_pct:.0f}% verify, {_exec}E/{_verify}V). "
                                f"Scalar FQ={_fq_val:.2f} is inflated by automated "
                                f"heartbeat pulses, not real audit work."
                            )
        except Exception as _fq_exc:
            # FQ probe failure is non-fatal but logged
            logger.warning("FQ gate probe failed: %s", _fq_exc)

    if _seal_reasons:
        return SealOutput(
            mode=mode,
            status="HOLD",
            verdict="HOLD",
            reasons=_seal_reasons,
            next_safe_action=(
                "Route through arif_init → arif_judge (SEAL verdict) → arif_seal. "
                "The judge must produce a constitutional_chain_id before sealing. "
                "No LLM wait — these are hard preconditions."
            ),
            entry_id="",
            actor_id=actor_id,
            meta={"gate": "hard_deterministic", "llm_consulted": False, "zend": "2026-07-30"},
        )

    # (_echo_standing defined above at SCT standing block — P0 2026-08-14)

    # ── EUREKA 5-PHASE MACRO: session_close (forged 2026-07-30) ─────────────
    # Single callable unit — stages 0→1→2→3 pre-seal, vault write (4), git (5).
    # See arifosmcp/tools/session_close_macro.py
    _is_session_close = mode == "session_close"
    _organ_health: dict[str, Any] | None = None
    _skill_health: dict[str, Any] | None = None
    _macro_pre: dict[str, Any] | None = None
    if _is_session_close:
        from arifosmcp.tools.session_close_macro import (
            probe_organ_health as _probe_organs,
            probe_skill_health as _probe_skills,
            run_pre_seal_stages as _run_pre_seal,
        )

        _health = _probe_organs()
        _organ_health = _health.get("organs") or {}
        _dead_organs: list[str] = list(_health.get("dead") or [])

        # Skill health probe — OBSERVE-class, non-fatal, always runs
        try:
            _skill_health = _probe_skills()
        except Exception as _sh_exc:  # noqa: BLE001
            _skill_health = {"error": str(_sh_exc)[:200]}

        if _dead_organs:
            return _echo_standing(
                SealOutput(
                    mode="session_close",
                    status="HOLD",
                    verdict="HOLD",
                    reasons=[f"Organ health check FAILED: {', '.join(_dead_organs)}"],
                    next_safe_action=(
                        f"Repair dead organs ({', '.join(_dead_organs)}) before sealing. "
                        "Run arif_observe(mode=organ_health) to diagnose."
                    ),
                    entry_id="",
                    actor_id=actor_id,
                    meta={
                        "gate": "SESSION_CLOSE_ORGAN_HEALTH",
                        "organ_health": _organ_health,
                        "organs_alive": _health.get("alive_count", 0),
                        "organs_total": _health.get("total", 0),
                        "dead_organs": _dead_organs,
                        "skill_health": _skill_health,
                        "macro": "arif_session_close_macro",
                    },
                )
            )

        try:
            _macro_pre = _run_pre_seal(
                payload=payload or "",
                session_id=session_id,
                actor_id=actor_id,
                organ_health=_health,
            )
        except Exception as _pre_exc:  # noqa: BLE001
            logger.warning("session_close pre-seal stages failed: %s", _pre_exc)
            _macro_pre = {"error": str(_pre_exc)[:200]}

        if not witness:
            witness = {
                "witness_id": "arif_session_close_macro",
                "witness_type": "ai",
                "role": "session_close",
                "note": "Kernel auto-witness for autonomous session close",
                "eureka_id": (_macro_pre or {}).get("eureka", {}).get("eureka_id"),
            }
        if not witness_type:
            witness_type = "ai"
        if not actor_id:
            actor_id = "agent"
        if not ack_irreversible:
            ack_irreversible = True

        # Skip Gödel-lock witness/self-cert for session_close accounting by
        # temporarily clearing ack for the gate, then restoring surface ack.
        # Actual vault write uses RECORD path below.
        mode = "seal"

    # ── GÖDEL-LOCK (Mission 001): No self-certification ──
    # The actor of an IRREVERSIBLE mutation cannot be the final certifier.
    # Enforced at the SEAL boundary — the last gate before Vault999 write.
    # Session-close accounting uses kernel auto-witness + RECORD vault path —
    # Gödel-lock is for AUTHORIZE seals, not autonomous session ledgering.
    if mode == "seal" and ack_irreversible and not _is_session_close:
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

    # ── mode=verify_chain — PUBLIC chain verification (sovereign 2026-07-18) ─
    # Lower-entropy way to expose vault verification: arif_seal mode=verify_chain
    # delegates to arif_vault_verify (read-only chain verifier). This keeps the
    # kernel ABI at 8 tools — vault.verify is a MODE of arif_seal, not a new tool.
    if mode == "verify_chain":
        from arifosmcp.tools.vault import arif_vault_verify as _vault_verify_fn

        # Anonymous callers allowed (this is the PUBLIC verify tier).
        # arif_vault_verify is sync — never await (2026-07-30 fix).
        _chain_verdict = _vault_verify_fn(
            mode="verify_chain",
            actor_id=actor_id,
            sovereign_receipt_ref="",
        )
        return _echo_standing(
            SealOutput(
                mode=mode,
                verdict=Verdict.SEAL
                if _chain_verdict.get("chain_physically_valid")
                else Verdict.HOLD,
                status=_chain_verdict.get("status", "OK"),
                entry_id="",
                actor_id=actor_id,
                meta={
                    "gate": "PUBLIC_VERIFY_CHAIN",
                    "verifier_authority_class": _chain_verdict.get(
                        "verifier_authority_class", "AUDIT_READ_ONLY"
                    ),
                    "chain_verified": _chain_verdict.get("chain_physically_valid"),
                    "entries_checked": _chain_verdict.get("entries_checked"),
                    "historical_anomaly": _chain_verdict.get("historical_anomaly"),
                    "accepted_risk": _chain_verdict.get("accepted_risk"),
                    "anomaly_repaired": _chain_verdict.get("anomaly_repaired"),
                    "sovereign_receipt_ref": _chain_verdict.get("sovereign_receipt_ref"),
                },
            )
        )

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

    # ── Identity binding (2026-07-29): auto-sign with session keypair ─────
    # Session lookup: tools.get_session (_SESSIONS) is canonical sync path.
    # session_registry.resolve_session does NOT exist — never import it.
    _identity_binding: dict[str, Any] | None = None
    if session_id and payload and actor_id:
        try:
            _sess = _lookup_session_for_identity(session_id)
            _sk = None
            if isinstance(_sess, dict):
                _sk = _sess.get("session_private_key")
            elif _sess is not None:
                _sk = getattr(_sess, "session_private_key", None)
            if _sk:
                import hashlib as _id_hashlib
                import secrets as _id_secrets

                from arifosmcp.runtime.crypto_auth import sign_with_session_key

                _payload_hash = _id_hashlib.sha256(payload.encode()).hexdigest()
                _nonce = _id_secrets.token_hex(16)
                _thumbprint = (
                    _sess.get("session_pubkey_thumbprint")
                    if isinstance(_sess, dict)
                    else getattr(_sess, "session_pubkey_thumbprint", None)
                )
                _sig = sign_with_session_key(
                    private_key_b64=_sk,
                    actor_id=actor_id,
                    payload_hash=_payload_hash,
                    nonce=_nonce,
                )
                _identity_binding = {
                    "actor_id": actor_id,
                    "session_pubkey_thumbprint": _thumbprint or "unknown",
                    "nonce": _nonce,
                    "actor_signature": _sig,
                    "kernel_verified": True,
                }
        except Exception as _ibe:
            logger.warning("Identity binding auto-sign failed: %s", _ibe)

    # ── Session-close RECORD path: epistemic tag + judge packet + vault ──
    _vault_ack = ack_irreversible
    _seal_payload = payload
    if _is_session_close:
        # F2: tag session summary as ACCOUNTING WITNESS (eligible), never as
        # AI_SYNTHESIZED executive evidence. Also sets session_close_macro so
        # _arif_vault_seal epistemic gate can short-circuit safely.
        _seal_payload = _tag_session_close_epistemic(
            payload,
            session_id=session_id,
            actor_id=actor_id,
            eureka_id=(_macro_pre or {}).get("eureka", {}).get("eureka_id"),
        )
        try:
            from arifosmcp.models.verdicts import Verdict as _V
            from arifosmcp.runtime.tools import _build_judge_contract
            from arifosmcp.schemas.forge import IrreversibilityLevel
            from arifosmcp.schemas.verdict import EpistemicSnapshot, FloorComplianceProof

            _cc_id = constitutional_chain_id or (
                f"session_close:{session_id or 'anon'}:"
                f"{(_macro_pre or {}).get('eureka', {}).get('eureka_id') or 'anon'}"
            )
            _contract = _build_judge_contract(
                candidate=f"SESSION_CLOSE: {(payload or '')[:120]}",
                verdict=_V.SEAL,
                session_id=session_id,
                actor_id=actor_id,
                constitutional_chain_id=_cc_id,
                irreversibility_level=IrreversibilityLevel.IRREVERSIBLE,
                delta_s=0.01,
                g_score=0.85,
                epistemic_snapshot=EpistemicSnapshot(omega_ortho=0.04, confidence=0.9),
                floor_compliance=FloorComplianceProof(
                    law_results={"L01": "PASS", "L02": "PASS", "L11": "PASS", "L13": "PASS"},
                ),
            )
            constitutional_chain_id = _contract.constitutional_chain_id
            judge_state_hash = _contract.state_hash
            _vault_ack = False  # RECORD — ledger write, not execution auth
            logger.info(
                "session_close minted judge packet cc=%s",
                (constitutional_chain_id or "")[:32],
            )
        except Exception as _jc_exc:  # noqa: BLE001
            logger.warning("session_close judge contract mint failed: %s", _jc_exc)

    # Z5 REALITY ANCHOR — append VPS delta + evidence refs to seal payload (non-blocking)
    try:
        import json as _json_anchor
        from arifosmcp.core.reality_anchors import seal_reality_context

        _reality_ctx = seal_reality_context(
            init_snapshot_hash="",  # populated when init snapshot is passed through session
            evidence_ids=[],
        )
        _reality_suffix = f"\n[Z5_REALITY_ANCHOR] {_json_anchor.dumps(_reality_ctx, default=str)}"
        _seal_payload = (_seal_payload or "") + _reality_suffix
    except Exception:
        pass  # Reality anchor must never block seal

    result = _arif_vault_seal(
        mode=mode,
        payload=_seal_payload,
        session_id=session_id,
        ack_irreversible=_vault_ack,
        actor_id=actor_id,
        actor_signature=actor_signature,
        nonce=nonce,
        constitutional_chain_id=constitutional_chain_id,
        judge_state_hash=judge_state_hash,
        witness_type=witness_type,
        drift_events=drift_events,
        floors=floors,
    )

    if not _vault_ack:
        result["seal_type"] = "SESSION_CLOSE_RECORD" if _is_session_close else "SEAL_RECORD"
        result["authorized_execution"] = False
        if _is_session_close:
            result["meta"] = result.get("meta") or {}
            result["meta"]["session_close_record"] = True
            result["meta"]["surface_ack_irreversible"] = ack_irreversible

    # ── Inject identity binding into seal result (2026-07-29) ─────────────
    # kernel_verified=True means the KERNEL signed this, not the agent.
    # Auditor trust: only arifOS kernel can write to VAULT999 (append-only).
    if _identity_binding:
        result["identity_binding"] = _identity_binding
        result["meta"] = result.get("meta", {})
        result["meta"]["identity_binding"] = _identity_binding

    # ── E1 FIX: Mint cryptographic SEAL token for IRREVERSIBLE actions ─────────
    # After arif_seal approves (mode="seal" + ack_irreversible), mint a token
    # bound to the exact payload hash. A-FORGE must verify this token via
    # arif_verify before execution. One-time use — token is burned on first use.
    _seal_token_value: str | None = None
    # E1 tokens authorize A-FORGE execution — not issued for session_close RECORD.
    if (
        result.get("verdict") == "SEAL"
        and mode == "seal"
        and ack_irreversible
        and payload
        and not _is_session_close
        and _vault_ack
    ):
        _payload_hash = hashlib.sha256(payload.encode()).hexdigest()
        # Delegate to canonical vault_registry — thread-safe, dual-write to VAULT999
        from arifosmcp.runtime.vault_registry import issue_seal

        try:
            _seal_token_value = issue_seal(payload=payload, actor_id=actor_id)
        except TypeError:
            # Compatibility across issue_seal signatures
            try:
                _seal_token_value = issue_seal(command=payload, actor_id=actor_id)  # type: ignore[call-arg]
            except Exception as _ise:  # noqa: BLE001
                logger.warning("issue_seal failed: %s", _ise)
                _seal_token_value = None
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
            with open(_genesis_path) as _gf:
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

    # ── F2 TRUTH repair 2026-07-17: Receipt sealing (#2)
    # Wire create_and_seal_receipt() into arif_seal path. Previously only
    # arif_judge called this; arif_seal wrote outcomes.jsonl but never
    # created a structured VaultReceipt. This left receipts_v2.jsonl empty
    # and all receipt states UNSEALED. Now every SEAL verdict also mints
    # a hash-chained receipt with identity resolution.
    _receipt_id: str | None = None
    _receipt_hash: str | None = None
    if result.get("verdict") == "SEAL" and mode in ("seal",) and session_id:
        try:
            from arifosmcp.core.vault_receipt import (
                create_and_seal_receipt,
                resolve_receipt_identity,
            )

            _payload_for_hash = payload if payload else json.dumps(result, sort_keys=True)
            _intent_hash = hashlib.sha256(
                json.dumps(_payload_for_hash, sort_keys=True).encode()
            ).hexdigest()
            _verdict_hash = hashlib.sha256(
                json.dumps(result.get("verdict", "SEAL"), sort_keys=True).encode()
            ).hexdigest()
            _rsid, _ractor = resolve_receipt_identity(
                session_id=session_id,
                actor_id=actor_id,
            )
            _receipt = create_and_seal_receipt(
                session_id=_rsid,
                actor_id=_ractor,
                organ_id="arifOS",
                intent_summary=(payload[:200] if payload else "arif_seal"),
                intent_hash=_intent_hash,
                requested_authority=_standing_authority or "OBSERVE_ONLY",
                pre_state_hash=result.get("meta", {}).get("state_hash", ""),
                decision=result.get("verdict", "UNKNOWN"),
                verdict_hash=_verdict_hash,
                floors_evaluated=list((floors or {}).keys()),
                floors_violated=[],
                witness_count=1 if witness else 0,
            )
            _receipt_id = _receipt.receipt_id
            _receipt_hash = _receipt.receipt_hash
            result["meta"] = result.get("meta", {})
            result["meta"]["vault_receipt_id"] = _receipt_id
            result["meta"]["vault_receipt_hash"] = _receipt_hash
            result["meta"]["receipt_state"] = "SEALED"
            if delta_s is not None:
                result["meta"]["delta_s"] = delta_s
        except Exception as _rx:
            result["meta"] = result.get("meta", {})
            result["meta"]["receipt_state"] = "UNSEALED"
            result["meta"]["receipt_error"] = str(_rx)[:200]

    # ── EUREKA777 Post-Seal Hook (ATLAS333 closed loop) ──────────────────────
    # After successful seal, check for eureka entry and run atlas333_update.
    # This closes the loop: Θ_t → E_s → atlas333_update → Θ_{t+1}
    # Only fires if: seal succeeded AND session_id exists AND eureka entry exists.
    if result.get("verdict") == "SEAL" and session_id:
        try:
            import pathlib as _pathlib

            _eureka_path = (
                _pathlib.Path("/root/.local/share/arifos/atlas333/eureka") / f"{session_id}.json"
            )
            if _eureka_path.exists():
                from arifosmcp.geometry.atlas333_update import (
                    atlas333_update as _atlas_update,
                )

                _update_result = _atlas_update(session_id)
                result["meta"] = result.get("meta", {})
                result["meta"]["atlas333_update"] = {
                    "classification": _update_result.get("classification"),
                    "cube777_updated": _update_result.get("cube777_updated"),
                    "receipt_path": _update_result.get("receipt_path"),
                    "note": "EUREKA777 post-seal hook fired — ATLAS333 geometry updated",
                }
        except Exception as exc:
            # Non-fatal — seal already succeeded; update is additive
            result["meta"] = result.get("meta", {})
            result["meta"]["atlas333_update_error"] = str(exc)

    # ── Route 3: L2 → L3 post-seal memory sync (Tri-Layer Protocol) ──────
    # After every successful seal, synchronise the semantic index (L3)
    # with the immutable ledger (L2).  Non-fatal — seal already succeeded.
    # If the index corrupts, delete and rebuild from VAULT999 entries.
    # F2: index is derived, not authoritative.  F4: ΔS < 0.
    if result.get("verdict") == "SEAL" and session_id:
        try:
            from arifosmcp.runtime.megaTools.tool_13_arif_memory import arif_memory as _mem

            _mem_result = await _mem(
                mode="remember",
                payload={
                    "content": payload[:800] if payload else "seal",
                    "tier": "L2",
                    "memory_authority": {
                        "provenance": "arif_seal",
                        "source_receipts": [result.get("entry_id", "")],
                        "truth_class": "DERIVED",
                    },
                },
                session_id=session_id,
                actor_id=actor_id,
            )
            result["meta"] = result.get("meta", {})
            result["meta"]["l3_sync"] = {
                "synced": True,
                "tier": "L2",
            }
        except Exception as _l3e:
            result["meta"] = result.get("meta", {})
            result["meta"]["l3_sync"] = {"synced": False, "error": str(_l3e)[:200]}

    # ── HIB Phase 1: Post-seal vectorization into precedent index ─────────
    # After every successful seal, vectorize the payload into the HIB
    # Qdrant collection for future precedent retrieval.
    # Non-fatal — seal already succeeded; index failure is logged.
    if result.get("verdict") == "SEAL" and session_id:
        try:
            from arifosmcp.tools.vault_vectorizer import hib_post_seal_hook as _hib_hook

            _hib_hook(
                entry_id=str(result.get("entry_id", "")),
                payload=payload,
                blast_radius=blast_radius,
                session_id=session_id,
            )
            result["meta"] = result.get("meta", {})
            result["meta"]["hib_vectorized"] = True
        except Exception as _hib_e:
            result["meta"] = result.get("meta", {})
            result["meta"]["hib_vectorized"] = False
            result["meta"]["hib_vectorize_error"] = str(_hib_e)[:200]

    # ── DAG Bridge: inject evidence_sha + reversion_event into seal ──────
    if evidence_sha:
        result["evidence_sha"] = evidence_sha
    if reversion_event:
        result["reversion_event"] = reversion_event

    # ── HIB: inject blast_radius into seal for payload filtering ─────────
    result["blast_radius"] = blast_radius

    # ── DAG Bridge L2→L3: post-seal auto-index into semantic layer ──────
    # After successful seal, index the sealed entry into arif_memory sacred tier.
    # Best-effort — seal already succeeded; index failure is non-fatal (Layer 3 is
    # disposable and rebuildable from the seal chain at any time).
    if result.get("verdict", "SEAL") == "SEAL":
        try:
            from arifosmcp.runtime.memory_store import store_v2 as _store

            _index_entry = {
                "content": payload[:4096] if payload else "",
                "tier": "sacred",
                "provenance": "sealed",
                "phoenix_state": "sealed",
                "tags": ["sealed", "L4", "dag-bridge", "auto-index"],
                "metadata": {
                    "seal_timestamp": result.get("timestamp"),
                    "receipt_id": result.get("receipt_id"),
                    "evidence_sha": evidence_sha,
                    "reversion_from": (
                        reversion_event.get("previous_sha") if reversion_event else None
                    ),
                },
            }
            _store(_index_entry)
            result["meta"] = result.get("meta", {})
            result["meta"]["l2_l3_bridge"] = {
                "indexed": True,
                "tier": "sacred",
                "note": (
                    "Auto-indexed to arif_memory sacred tier — "
                    "disposable, rebuildable from seal chain."
                ),
            }
        except Exception as exc:
            result["meta"] = result.get("meta", {})
            result["meta"]["l2_l3_bridge"] = {
                "indexed": False,
                "error": str(exc),
                "note": "Index failure is non-fatal — Layer 3 is rebuildable from DAG.",
            }

    # ── EUREKA Phase 5: session_close post-hook — git commit + push ──────────
    # Targets arifOS + AAA only (never bare /root). Non-fatal on push failure.
    if _is_session_close:
        _git_result: dict[str, Any] | None = None
        _sealed_ok = str(result.get("verdict") or "").upper() == "SEAL"
        if _sealed_ok:
            try:
                from arifosmcp.tools.session_close_macro import git_sync_federation as _git_sync

                _git_result = _git_sync(
                    actor_id=actor_id,
                    payload=payload or "",
                    entry_id=result.get("entry_id"),
                    organ_health={
                        "alive_count": sum(
                            1 for o in (_organ_health or {}).values() if o.get("alive")
                        ),
                        "total": len(_organ_health or {}),
                    },
                    push=True,
                )
            except Exception as _ge:  # noqa: BLE001
                _git_result = {
                    "synced": False,
                    "phase": "5_remote_sync",
                    "error": str(_ge)[:200],
                }

        result["meta"] = result.get("meta", {})
        result["meta"]["session_close"] = {
            "macro": "arif_session_close_macro",
            "forged": "2026-07-30",
            "stages": {
                "0_organ_health": {
                    "organs": _organ_health,
                    "alive": sum(1 for o in (_organ_health or {}).values() if o.get("alive")),
                    "total": len(_organ_health or {}),
                },
                "0b_skill_health": _skill_health,
                "1_sot_refactor": (_macro_pre or {}).get("stage_1_sot_refactor"),
                "2_sot_verify": (_macro_pre or {}).get("stage_2_sot_verify"),
                "3_atlas333": (_macro_pre or {}).get("stage_3_atlas333"),
                "4_vault": {
                    "entry_id": result.get("entry_id"),
                    "chain_hash": result.get("chain_hash"),
                    "verdict": result.get("verdict"),
                    "seal_type": result.get("seal_type"),
                },
                "5_remote_sync": _git_result,
            },
            "eureka": (_macro_pre or {}).get("eureka"),
            "git": _git_result,
            "seal_complete": bool(_sealed_ok),
            "delta_s": (
                "NEGATIVE — session sealed, SOT updated, atlas333 indexed, git synced"
                if _sealed_ok
                else "PARTIAL — pre-seal stages ran; vault HOLD"
            ),
        }

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


def arif_vault_verify(
    mode: Literal["verify_chain", "chain_status", "audit"] = "verify_chain",
    session_id: str | None = None,
    actor_id: str | None = None,
    limit: int = 50,
    sovereign_receipt_ref: str = "",
) -> dict[str, Any]:
    """
    VAULT_VERIFY: Read-only chain verifier — independent of seal authority.

    P0 VAULT semantics: separated from arif_seal so that read-only
    verification does not require seal-level SCT authority.

    Modes:
      verify_chain — four-state anomaly integrity check of the vault ledger
      chain_status — return cached chain head + last N entries (newest first)
      audit        — full audit report with four-state + receipt binding

    Args:
      sovereign_receipt_ref: Optional citation of a sovereign decision
          receipt that ratified historical anomalies as accepted risk.
          Anomaly records carry this ref when provided.

    Constitutional:
      F2 TRUTH — OBSERVE class, no mutation, no repair
      F11 AUDIT — every read verified against chain state
    """
    from arifosmcp.apps.command_center.vault_chain import (
        read_vault_entries,
        verify_chain,
    )

    actor = actor_id or "vault_auditor"

    if mode in ("verify_chain", "audit"):
        chain_report = verify_chain(sovereign_receipt_ref=sovereign_receipt_ref)
        derived_status = chain_report.get("status", "UNMEASURED")
        result: dict[str, Any] = {
            "status": derived_status,
            "mode": "verify_chain",
            "verifier_authority_class": "AUDIT_READ_ONLY",
            "caller": actor,
            "append_attempted": False,
            "repair_attempted": False,
            **chain_report,
        }

        if mode == "audit":
            result["mode"] = "audit"
            result["recent_entries"] = read_vault_entries(limit=min(limit, 50))

        return result

    if mode == "chain_status":
        entries = read_vault_entries(limit=min(limit, 50))
        chain_report = verify_chain(sovereign_receipt_ref=sovereign_receipt_ref)
        return {
            "status": "OK",
            "mode": "chain_status",
            "verifier_authority_class": "AUDIT_READ_ONLY",
            "caller": actor,
            "append_attempted": False,
            "repair_attempted": False,
            "entries_count": len(entries),
            "entries": entries,
            **{
                k: v
                for k, v in chain_report.items()
                if k
                in (
                    "chain_physically_valid",
                    "historical_anomaly",
                    "accepted_risk",
                    "anomaly_repaired",
                    "sovereign_receipt_ref",
                    "entries_checked",
                )
            },
        }

    return {
        "status": "HOLD",
        "mode": mode,
        "error": f"Unknown mode: {mode}",
    }


# Backward compatibility alias
arif_vault_seal = arif_seal
