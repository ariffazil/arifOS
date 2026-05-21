"""
arifosmcp/tools/forge_execute.py — 010_FORGE Stub
══════════════════════════════════════════════════

Execution substrate dispatch — delegates to runtime/tools.py.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import UTC, datetime

from arifosmcp.runtime.floor import check_floors
from arifosmcp.runtime.tools import _arif_forge_execute
from arifosmcp.schemas.forge import ForgeManifest, ForgeOutput, ManifestStatus


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
) -> ForgeOutput:
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
                        "reason": f"888 HOLD — side_effects_allowed=False in runtime_truth. "
                        f"Shadow: {shadow_val}. "
                        f"Required: human_ack before proceeding."
                    },
                    timestamp=datetime.now(UTC).isoformat(),
                )

    floor_check = check_floors(
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
                "failed_floors": floor_check["failed_floors"],
            },
            timestamp=datetime.now(UTC).isoformat(),
        ).model_dump(mode="json")
        injected = _inject_nine_signal(raw, "HOLD")
        injected["reasons"] = [floor_check["reason"]] if floor_check.get("reason") else []
        return ForgeOutput(**injected)
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
