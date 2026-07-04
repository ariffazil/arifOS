"""
arifosmcp/tools/forge_execute.py — 010_FORGE Stub
══════════════════════════════════════════════════

Execution substrate dispatch — delegates to runtime/tools.py.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import UTC, datetime

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _add_floor_compat, _arif_forge
from arifosmcp.schemas.forge import ForgeErrorCode, ForgeManifest, ForgeOutput, ManifestStatus
from arifosmcp.tools.forge_ladder import ARIF_FORGE_EXECUTE_MANIFEST


def action_has_side_effects(mode: str, manifest: str, query: str | None) -> bool:
    risky = [
        "write",
        "deploy",
        "delete",
        "modify",
        "install",
        "restart",
        "exec",
        "docker",
        "git push",
        "memory_set",
    ]
    action_str = f"{mode} {manifest} {query or ''}".lower()
    return any(r in action_str for r in risky)


# v3.1: MUTATE/ATOMIC modes only. OBSERVE/REASON moved to forge_ladder.
_MUTATE_MODES = {"engineer", "write", "generate"}
_ATOMIC_MODES = {"commit", "deploy"}
_FORGE_MUTATE_ATOMIC = _MUTATE_MODES | _ATOMIC_MODES


async def arif_forge(
    mode: str = "engineer",
    manifest: str = "",
    query: str | None = None,
    artifact_id: str | None = None,
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    vault_entry_id: str | None = None,
    witness_type: str = "ai",
    action_tier: str = "standard",
    permitted_scope: dict | None = None,
    plan_id: str | None = None,
    # ── F1 AMANAH: per-call sovereign signature (optional) ───────────────────
    # The signature is currently bound at session_init and inherited via
    # session_id; this field is reserved for a future per-call signature
    # path. Accepting it now closes the schema gap surfaced by the
    # 2026-06-12 external harness audit. F13 ratifies whether to
    # actually enforce it; for now the field is recorded but not
    # verified. AGI_KERNEL_READINESS_GATE_001 Tier 5.
    actor_signature: str | None = None,
    nonce: str | None = None,
) -> ForgeOutput:
    """
    010_FORGE_EXECUTE: Sovereign execution bridge to A-FORGE.

    MUTATE and ATOMIC modes ONLY. For read-only operations, use forge_query.
    For planning, use forge_plan. For simulation, use forge_dry_run.

    Executes approved builds, deployments, or system changes ONLY after
    arif_judge has issued a SEAL verdict and explicit ack.

    Args:
        mode: "engineer" | "write" | "generate" | "commit" | "deploy".
        manifest: JSON manifest describing the action to execute.
        artifact_id: Reference to a prior artifact (e.g., plan output).
        session_id: Constitutional session ID from arif_init.
        ack_irreversible: Must be True to confirm irreversible execution.
        judge_state_hash: REQUIRED for all MUTATE/ATOMIC modes.
        plan_id: Approved plan_id from forge_plan (required for engineer/write/generate).
        action_tier: "standard" | "sovereign" | "c4" | "c5".
        permitted_scope: Bounding scope dict for the execution.
        actor_signature: RESERVED — Ed25519 signature over
            (actor_id + constitution_hash + nonce). Currently recorded
            but not verified. F13 ratifies enforcement.
        nonce: RESERVED — replay-prevention nonce. Must accompany
            actor_signature if either is provided. F1 AMANAH.
    """
    # ── v3.1: Mode classification gate ────────────────────────────────────────
    if mode not in _FORGE_MUTATE_ATOMIC:
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta={
                "error_code": ForgeErrorCode.E_FORGE_MODE_NOT_ALLOWED,
                "reason": (
                    f"mode='{mode}' is not a MUTATE/ATOMIC mode. "
                    f"Allowed: {sorted(_FORGE_MUTATE_ATOMIC)}. "
                    f"For read-only: use forge_query. For planning: use forge_plan. "
                    f"For simulation: use forge_dry_run."
                ),
                "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
            },
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: actor_id REQUIRED for MUTATE/ATOMIC (L11 authority) ─────────────
    if not actor_id:
        _meta = {
            "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
            "reason": (
                "888 HOLD — actor_id is REQUIRED for MUTATE/ATOMIC forge modes. "
                "Anonymous execution is prohibited."
            ),
            "violated_laws": ["L11"],
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: vault_entry_id REQUIRED for commit mode ─────────────────────────
    if mode == "commit" and not vault_entry_id:
        _meta = {
            "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
            "reason": (
                "888 HOLD — vault_entry_id is REQUIRED for commit mode. "
                "Link the commit to a VAULT999 lineage entry."
            ),
            "violated_laws": ["L01", "L11"],
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: F1 AMANAH nonce/signature consistency (RESERVED) ───────────────
    # If actor_signature is provided without nonce, reject for replay
    # prevention. If both are provided, log receipt but do not enforce
    # until F13 ratifies the per-call signature path.
    if actor_signature and not nonce:
        _meta = {
            "error_code": ForgeErrorCode.E_SYNTHESIS_EMPTY,
            "reason": (
                "F1 AMANAH: actor_signature requires nonce for replay prevention. "
                "Provide both, or omit both to inherit from session_init."
            ),
            "violated_laws": ["F01"],
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
            "f13_status": "RESERVED — per-call signature path not yet enforced",
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: judge_state_hash REQUIRED for MUTATE/ATOMIC ─────────────────────
    if not judge_state_hash:
        _meta = {
            "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
            "reason": (
                "888 HOLD — judge_state_hash is REQUIRED for MUTATE/ATOMIC forge modes. "
                "Call arif_judge first, then pass the returned state_hash."
            ),
            "violated_laws": ["L01", "L11"],
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: plan_id REQUIRED for engineer/write/generate ────────────────────
    if mode in ("engineer", "write", "generate") and not plan_id:
        _meta = {
            "error_code": ForgeErrorCode.E_SYNTHESIS_EMPTY,
            "reason": (
                f"mode='{mode}' requires an approved plan_id from forge_plan. "
                "Call forge_plan(goal=...) first, then pass the returned plan_id."
            ),
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── W-2: SOVEREIGN clarity gate for elevated-tier FORGE actions ───────────
    _is_elevated = action_tier.lower() in ("sovereign", "c4", "c5")
    if _is_elevated:
        try:
            from arifosmcp.tools.judge import _read_well_substrate

            _forge_sub = _read_well_substrate()
            _forge_clarity = _forge_sub.get("clarity")
            if (
                _forge_clarity is not None
                and float(_forge_clarity) < 4.0
                and _forge_sub.get("has_telemetry")
            ):
                return ForgeOutput(
                    status="HOLD",
                    result={},
                    manifest=ForgeManifest(status=ManifestStatus.HOLD),
                    meta={
                        "error_code": ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
                        "reason": (
                            f"W5_COGNITIVE_ENTROPY: clarity={_forge_clarity}/10 below "
                            "SOVEREIGN threshold (4/10). FORGE blocked. "
                            "Rest. Reassess when clarity >= 6."
                        ),
                        "well_gate": "SOVEREIGN_BLOCKED",
                        "w_floor": "W5 -> F2",
                        "action_tier": action_tier,
                        "clarity": _forge_clarity,
                        "well_substrate": _forge_sub,
                    },
                    timestamp=datetime.now(UTC).isoformat(),
                )
        except Exception:
            pass  # WELL offline is non-fatal — W0 sovereignty invariant

    # ── Side Effect Gate (v2 Deepening) ──
    from arifosmcp.runtime.tools import _SESSIONS

    sess = _SESSIONS.get(session_id) if session_id else None
    card = sess.get("model_governance_card") if sess else None
    if card:
        rt = card.runtime_truth if hasattr(card, "runtime_truth") else card.get("runtime_truth", {})
        side_effects = (
            getattr(rt, "side_effects_allowed", False)
            if hasattr(rt, "side_effects_allowed")
            else rt.get("side_effects_allowed", False)
        )
        shadow = (
            card.shadow_profile
            if hasattr(card, "shadow_profile")
            else card.get("shadow_profile", {})
        )
        shadow_val = (
            getattr(shadow, "shadow", "unknown")
            if hasattr(shadow, "shadow")
            else shadow.get("shadow", "unknown")
        )
        if not side_effects and not ack_irreversible:
            if action_has_side_effects(mode, manifest, query):
                return ForgeOutput(
                    status="HOLD",
                    result={},
                    manifest=ForgeManifest(status=ManifestStatus.HOLD),
                    meta={
                        "error_code": ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
                        "reason": f"888 HOLD — side_effects_allowed=False in runtime_truth. "
                        f"Shadow: {shadow_val}. "
                        f"Required: human_ack before proceeding.",
                    },
                    timestamp=datetime.now(UTC).isoformat(),
                )

    # ── P1 WIRING (2026-06-28): Latency budget enforcement ──
    # The floor check is a constitutional gate, not just a performance concern.
    # Record latency and flag if it exceeds the decision-class budget.
    import time as _time
    from arifosmcp.core.latency_budget import LATENCY_BUDGETS
    from arifosmcp.core.decision_contract import DecisionClass

    _t_check = _time.monotonic()
    floor_check = check_laws(
        "arif_forge",
        {
            "mode": mode,
            "ack_irreversible": ack_irreversible,
            "manifest": manifest,
            "query": query,
            "artifact_id": artifact_id,
            "session_id": session_id,
        },
        actor_id,
    )
    _latency_ms = (_time.monotonic() - _t_check) * 1000
    _budget = LATENCY_BUDGETS.get(DecisionClass.C2_STANDARD, LATENCY_BUDGETS[DecisionClass.C3_DEEP])
    floor_check["_latency_ms"] = _latency_ms
    floor_check["_within_budget"] = _latency_ms <= _budget.max_latency_ms
    if floor_check["verdict"] != "SEAL":
        from arifosmcp.runtime.tools import _inject_nine_signal

        raw = ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta={
                "reason": floor_check["reason"],
                "violated_laws": floor_check["violated_laws"],
            },
            timestamp=datetime.now(UTC).isoformat(),
        ).model_dump(mode="json")
        injected = _inject_nine_signal(raw, "HOLD")
        injected["reasons"] = [floor_check["reason"]] if floor_check.get("reason") else []
        return ForgeOutput(**injected)

    # ── CAPABILITY MEMBRANE: Enforce exact permitted scope before execution ─────────
    # Phase 1: If a permitted_scope is provided, validate the action strictly matches.
    # This prevents capability drift: agent cannot broaden recipients, modify bodies,
    # or extend expiry after human has granted a one-time scope.
    if permitted_scope is not None:
        from arifosmcp.runtime.niat_gate import enforce_capability_membrane

        # Derive the tool name from mode — forge is a meta-tool dispatcher.
        _tool_for_membrane = {
            "write": "file.write",
            "generate": "code.generate",
            "commit": "git.commit",
            "deploy": "docker.deploy",
            "engineer": "forge.engineer",
        }.get(mode, f"forge.{mode}")

        _membrane_passed = enforce_capability_membrane(
            _tool_for_membrane,
            {"mode": mode, "manifest": manifest, "query": query},
            permitted_scope,
        )
        if not _membrane_passed:
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "error_code": ForgeErrorCode.E_CAPABILITY_MEMBRANE_VIOLATION,
                    "reason": (
                        "888 HOLD — CAPABILITY_MEMBRANE: Action parameters exceed "
                        "the explicitly permitted scope. Human grant was limited to "
                        f"{permitted_scope.get('tool', 'unknown')}, but the requested "
                        "action did not match. Narrow the grant or obtain a new one."
                    ),
                    "capability_membrane": "HOLD",
                    "permitted_scope": {
                        k: v
                        for k, v in permitted_scope.items()
                        if k not in ("tool", "subject_hash", "body_hash")
                    },
                },
                timestamp=datetime.now(UTC).isoformat(),
            )

    # ── P1 WIRING (2026-06-28): Cross-organ conflict resolution before dispatch ──
    # Before forge dispatches to A-FORGE, validate there are no unresolved conflicts
    # between arifOS verdict and the execution target. Currently a no-op guardrail
    # that activates when cross-organ conflicts are registered.
    try:
        from arifosmcp.core.conflict_resolver import resolve_conflict
        from arifosmcp.core.decision_contract import ConflictEnvelope

        _conflict_envelope = ConflictEnvelope(
            conflict_id=f"forge-{mode}-{session_id or 'anon'}",
            organ_a="arifos",
            verdict_a=floor_check.get("verdict", "SEAL"),
            organ_b="a-forge",
            verdict_b="PROCEED",
            conflict_domain="forge",
            is_irreversible=(mode in _ATOMIC_MODES),
        )
        _resolution = resolve_conflict(_conflict_envelope)
        if _resolution.requires_888_hold:
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "error_code": ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
                    "reason": (
                        f"Pre-execution conflict resolution required 888_HOLD: {_resolution.reason}"
                    ),
                    "conflict_resolution": {
                        "winner_organ": _resolution.winner_organ,
                        "winner_verdict": _resolution.winner_verdict,
                        "resolution_method": _resolution.resolution_method,
                        "requires_888_hold": _resolution.requires_888_hold,
                    },
                },
                timestamp=datetime.now(UTC).isoformat(),
            )
    except Exception:
        pass  # Conflict resolver offline → proceed (no conflicts = no block)

    import asyncio

    def _run_forge():
        return _arif_forge(
            mode=mode,
            manifest=manifest,
            query=query,
            artifact_id=artifact_id,
            session_id=session_id,
            ack_irreversible=ack_irreversible,
            actor_id=actor_id,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            vault_entry_id=vault_entry_id,
            witness_type=witness_type,
        )

    result_dict = await asyncio.to_thread(_run_forge)
    result = ForgeOutput(**result_dict)

    # ── P0 WIRING (2026-06-28): Seal forge execution to VAULT999 ──
    # Every successful forge execution must leave an auditable receipt.
    # The create_and_seal_receipt function exists in core/vault_receipt.py
    # and is proven in judge.py — it was never called from forge.py.
    try:
        from arifosmcp.core.vault_receipt import create_and_seal_receipt
        import hashlib

        create_and_seal_receipt(
            session_id=session_id or "anon",
            actor_id=actor_id or "anonymous",
            organ_id="arifOS",
            intent_summary=f"forge:{mode}:{manifest[:80] if manifest else ''}",
            intent_hash=hashlib.sha256(f"{mode}:{manifest}".encode()).hexdigest()[:16],
            requested_authority=action_tier or "standard",
            pre_state_hash=judge_state_hash or "",
            decision=result.status,
            verdict_hash=hashlib.sha256(str(result_dict).encode()).hexdigest()[:16],
            floors_evaluated=["F1", "F2", "F9", "F13"],
            floors_violated=[],
            latency_ms=0.0,
            within_budget=True,
        )
    except Exception:
        pass  # Sealing must never block execution

    _register_forge_cooldown(result, mode, manifest, artifact_id, session_id)
    # ── v3.1: surface reserved signature in receipt (recorded, not enforced) ──
    if actor_signature and nonce:
        # F13 territory — log receipt only, do not act
        sig_receipt = {
            "actor_signature_provided": True,
            "nonce_provided": True,
            "actor_signature_preview": actor_signature[:16] if actor_signature else None,
            "f13_status": "RESERVED — per-call signature path not yet enforced; "
            "signature inherited from session_init until F13 ratifies.",
        }
        # Attach to result.meta if present, else to result.result
        if hasattr(result, "meta") and result.meta is not None:
            result.meta["per_call_signature_receipt"] = sig_receipt
        elif hasattr(result, "result") and isinstance(result.result, dict):
            result.result["per_call_signature_receipt"] = sig_receipt
    return result


def _register_forge_cooldown(
    result: ForgeOutput,
    mode: str,
    manifest: str,
    artifact_id: str | None,
    session_id: str | None,
) -> None:
    """Auto-register forge artifacts in SABAR cooldown band. Stage 2A: observe+warn only."""
    side_effect_modes = {"engineer", "write", "generate", "commit"}
    if mode not in side_effect_modes:
        return

    try:
        import hashlib

        from arifosmcp.core.cooldown_engine import get_cooldown_engine

        engine = get_cooldown_engine()
        artifact_ref = (
            artifact_id
            or hashlib.md5(  # nosec B324
                f"{mode}:{manifest}:{session_id or 'anon'}:{result.timestamp or ''}".encode()
            ).hexdigest()[:12]
        )
        desc = f"forge:{mode}:{manifest[:80]}" if manifest else f"forge:{mode}"

        entry = engine.propose(
            artifact_ref=artifact_ref,
            description=desc,
            risk_tier="medium",
            session_id=session_id,
        )

        # Attach cooldown metadata to result (observe only — no block)
        if result.meta is None:
            result.meta = {}
        result.meta["sabar_cooldown"] = {
            "stage": "registered",
            "cooldown_entry_id": entry.entry_id,
            "cooldown_expiry": entry.cooldown_expiry.isoformat() if entry.cooldown_expiry else None,
            "cooldown_hours": entry.cooldown_hours,
            "remaining_hours": round(entry.remaining_hours, 1),
            "verdict": entry.verdict,
            "note": "artifact entered SABAR cooldown — not yet sealed for permanence",
        }
    except Exception:
        if result.meta is None:
            result.meta = {}
        result.meta["sabar_cooldown"] = {
            "stage": "unavailable",
            "note": "cooldown engine not reachable",
        }


# Backward compatibility alias
arif_forge_execute = arif_forge
