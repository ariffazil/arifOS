"""
arifosmcp/tools/reply_compose.py — 444r_REPLY
════════════════════════════════════════════

Governed response compositor.
"""

from __future__ import annotations

import asyncio
from typing import Any

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _hold, _ok


def arif_reply_compose(
    mode: str = "compose",
    message: str | None = None,
    style: str | None = None,
    citations: list[str] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    # ── Reply Boundary Check (v2 Deepening — Task 4) ──
    from arifosmcp.runtime.tools import _arif_vault_seal, get_session

    sess = get_session(session_id)
    card = sess.get("model_governance_card") if sess else None

    if card and message:
        # Support both ModelGovernanceCard (Pydantic) and legacy dict
        truth = (
            card.runtime_truth if hasattr(card, "runtime_truth") else card.get("runtime_truth", {})
        )
        anchor = (
            card.model_anchor if hasattr(card, "model_anchor") else card.get("model_anchor", {})
        )
        shadow = (
            card.shadow_profile
            if hasattr(card, "shadow_profile")
            else card.get("shadow_profile", {})
        )
        drift_events = []

        # Helper for nested dict-like access on card sub-objects
        def _anchor_get(field: str, default=None):
            return (
                getattr(anchor, field, default)
                if hasattr(anchor, field)
                else anchor.get(field, default)
            )

        def _shadow_get(field: str, default=None):
            return (
                getattr(shadow, field, default)
                if hasattr(shadow, field)
                else shadow.get(field, default)
            )

        # 1. Identity claim check
        msg_l = message.lower()
        if "i am" in msg_l:
            for s in ["gpt", "claude", "gemini", "grok", "minimax", "kimi"]:
                if f"i am {s}" in msg_l and s not in (_anchor_get("soul_key") or "").lower():
                    import re

                    pattern = re.compile(f"i am {s}", re.IGNORECASE)
                    message = pattern.sub(
                        f"[IDENTITY CORRECTION: I am {_anchor_get('soul_label')}]",
                        message,
                    )
                    drift_events.append(
                        {
                            "session_id": session_id,
                            "event_type": "identity_mismatch",
                            "model_key": _anchor_get("verified_model_key"),
                            "soul_key": _anchor_get("soul_key"),
                            "shadow": _shadow_get("shadow"),
                            "trigger": f"Claimed identity mismatch: {s}",
                            "correction_applied": "Identity string stripped/qualified",
                            "severity": "medium",
                            "requires_human_judge": False,
                        }
                    )

        # 2. Tool claim check (Web)
        from arifosmcp.runtime.tools import _output_claims_web

        web_on = (
            getattr(truth, "web_on", False)
            if hasattr(truth, "web_on")
            else truth.get("web_on", False)
        )
        if _output_claims_web(message) and not web_on:
            message = (
                "[TRUTH GATE: This model does not have web access in this deployment] " + message
            )
            drift_events.append(
                {
                    "session_id": session_id,
                    "event_type": "runtime_overclaim",
                    "model_key": _anchor_get("verified_model_key"),
                    "soul_key": _anchor_get("soul_key"),
                    "shadow": _shadow_get("shadow"),
                    "trigger": "Claimed web access while web_on is False",
                    "correction_applied": "Message qualified with truth gate",
                    "severity": "high",
                    "requires_human_judge": True,
                }
            )

        # 3. Execution claim check
        from arifosmcp.runtime.tools import _output_claims_execution

        side_effects = (
            getattr(truth, "side_effects_allowed", False)
            if hasattr(truth, "side_effects_allowed")
            else truth.get("side_effects_allowed", False)
        )
        if _output_claims_execution(message) and not side_effects:
            message = "[FORGE GATE: This model is in advisory mode only] " + message
            drift_events.append(
                {
                    "session_id": session_id,
                    "event_type": "self_authorization_attempt",
                    "model_key": _anchor_get("verified_model_key"),
                    "soul_key": _anchor_get("soul_key"),
                    "shadow": _shadow_get("shadow"),
                    "trigger": "Claimed execution while side_effects_allowed is False",
                    "correction_applied": "Message qualified with forge gate",
                    "severity": "high",
                    "requires_human_judge": True,
                }
            )

        if drift_events:
            _arif_vault_seal(mode="dry_run", session_id=session_id, drift_events=drift_events)

    # ── 666_HEART Pre-Delivery Gate ──
    from arifosmcp.tools.heart import _heart_fallback, arif_heart_critique

    try:
        heart_result = asyncio.run(
            arif_heart_critique(
                mode="critique",
                target=message,
                actor_id=actor_id,
                session_id=session_id,
                context_type="external_action",
            )
        )
    except RuntimeError:
        # Running event loop — use deterministic fallback
        heart_result = _heart_fallback(
            mode="critique",
            target=message or "",
            context_type="external_action",
        )

    omega_state = heart_result.get("omega_state", {})
    heart_verdict = heart_result.get("verdict", "SEAL")

    # VOID or Ω₂: block delivery entirely
    if heart_verdict == "VOID" or omega_state.get("omega") == "Ω₂":
        return _hold(
            "arif_reply_compose",
            f"666_HEART VOID: {heart_result.get('risks_found', [])}",
            {
                "omega_state": omega_state,
                "heart_verdict": heart_verdict,
                "caveats": heart_result.get("caveats", []),
            },
        )

    # HOLD or Ω₁: deliver with constitutional caveats
    if heart_verdict == "HOLD" or omega_state.get("omega") == "Ω₁":
        return _ok(
            "arif_reply_compose",
            {
                "message": message,
                "formatted": message,
                "tone": "neutral",
                "heart_gate": "HOLD",
                "heart_caveats": heart_result.get("risks_found", []),
                "omega_state": omega_state,
            },
        )

    floor_check = check_laws("arif_reply_compose", {"message": message or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_reply_compose", floor_check["reason"], floor_check["violated_laws"])

    if mode == "compose":
        return _ok(
            "arif_reply_compose",
            {"message": message, "formatted": message, "tone": "neutral"},
        )
    if mode == "format":
        return _ok("arif_reply_compose", {"message": message, "style": style or "markdown"})
    if mode == "nudge":
        return _ok(
            "arif_reply_compose",
            {"message": message, "nudge": "Consider F5 (Peace) before acting."},
        )
    if mode == "cite":
        return _ok("arif_reply_compose", {"message": message, "citations": citations or []})

    if mode in ("qday_engineering_report", "qday_executive_summary", "qday_physics_brief"):
        return {"status": "readonly", "message": f"{mode} activated based on qday_physics parameters."}

    if mode in ("geox_quantum_brief", "geox_quantum_anti_hype_report", "geox_quantum_opportunity_map"):
        return {"status": "readonly", "message": f"{mode} activated based on GEOX quantum scale classifier."}

    return _hold("arif_reply_compose", f"Unknown mode: {mode}")
