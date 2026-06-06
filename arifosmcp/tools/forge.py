"""
arifosmcp/tools/forge_execute.py — 010_FORGE Stub
══════════════════════════════════════════════════

Execution substrate dispatch — delegates to runtime/tools.py.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import UTC, datetime

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _add_floor_compat, _arif_forge_execute
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


def arif_forge_execute(
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
) -> ForgeOutput:
    """
    010_FORGE_EXECUTE: Sovereign execution bridge to A-FORGE.

    MUTATE and ATOMIC modes ONLY. For read-only operations, use forge_query.
    For planning, use forge_plan. For simulation, use forge_dry_run.

    Executes approved builds, deployments, or system changes ONLY after
    arif_judge_deliberate has issued a SEAL verdict and explicit ack.

    Args:
        mode: "engineer" | "write" | "generate" | "commit" | "deploy".
        manifest: JSON manifest describing the action to execute.
        artifact_id: Reference to a prior artifact (e.g., plan output).
        session_id: Constitutional session ID from arif_session_init.
        ack_irreversible: Must be True to confirm irreversible execution.
        judge_state_hash: REQUIRED for all MUTATE/ATOMIC modes.
        plan_id: Approved plan_id from forge_plan (required for engineer/write/generate).
        action_tier: "standard" | "sovereign" | "c4" | "c5".
        permitted_scope: Bounding scope dict for the execution.
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

    # ── v3.1: judge_state_hash REQUIRED for MUTATE/ATOMIC ─────────────────────
    if not judge_state_hash:
        _meta = {
            "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
            "reason": (
                "888 HOLD — judge_state_hash is REQUIRED for MUTATE/ATOMIC forge modes. "
                "Call arif_judge_deliberate first, then pass the returned state_hash."
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
                        f"Required: human_ack before proceeding."
                    },
                    timestamp=datetime.now(UTC).isoformat(),
                )

    floor_check = check_laws(
        "arif_forge_execute",
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

    result = ForgeOutput(
        **_arif_forge_execute(
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
    )
    _register_forge_cooldown(result, mode, manifest, artifact_id, session_id)
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
