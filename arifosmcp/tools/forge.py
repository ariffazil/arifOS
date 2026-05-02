"""
arifosmcp/tools/forge_execute.py — 010_FORGE Stub
══════════════════════════════════════════════════

Execution substrate dispatch — delegates to runtime/tools.py.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import datetime, timezone

from arifosmcp.runtime.floors import check_floors
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
) -> ForgeOutput:
    # ── Side Effect Gate (v2 Deepening) ──
    from arifosmcp.runtime.tools import _SESSIONS

    sess = _SESSIONS.get(session_id) if session_id else None
    card = sess.get("model_governance_card") if sess else None
    if card:
        rt = card.get("runtime_truth", {})
        if not rt.get("side_effects_allowed", False) and not ack_irreversible:
            if action_has_side_effects(mode, manifest, query):
                return ForgeOutput(
                    status="HOLD",
                    result={},
                    manifest=ForgeManifest(status=ManifestStatus.HOLD),
                    meta={
                        "reason": f"888 HOLD — side_effects_allowed=False in runtime_truth. "
                        f"Shadow: {card['shadow_profile'].get('shadow')}. "
                        f"Required: human_ack before proceeding."
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
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
            timestamp=datetime.now(timezone.utc).isoformat(),
        ).model_dump(mode="json")
        injected = _inject_nine_signal(raw, "HOLD")
        injected["reasons"] = [floor_check["reason"]] if floor_check.get("reason") else []
        return ForgeOutput(**injected)
    return ForgeOutput(
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
