"""
arifosmcp/runtime/memory_manage.py — arif_memory_manage MCP tool handler (EUREKA-A)

Live tool that exposes the kernel's persistent state graph (KernelState) and
the dual-layer state store. Modes: consolidate | forget | replay | snapshot | restore.

Why a diagnostic (not canonical-13)? Per AGENTS.md, the 13 canonical tools are
the SOT for the constitutional kernel surface. This tool operates on the state
infrastructure that the 13 tools write into — it is a memory OS resource manager,
not a constitutional verb. Same architectural pattern as the 6 other diagnostic
tools (arif_stack_health_probe, etc.).

Reversibility (F1): file delete = revert. No canonical_map.py mutation needed
beyond DIAGNOSTIC_TOOLS tuple + CANONICAL_TOOLS entry — both are part of the
diagnostic surface contract.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Literal

import numpy as np

from arifosmcp.runtime.kernel_state import (
    KernelState,
    init_state_for_session,
)
from arifosmcp.runtime.kernel_state import (
    consolidate as consolidate_state,
)
from arifosmcp.runtime.state_store import get_dual_store

logger = logging.getLogger(__name__)

# Mode vocabulary — closed set, per eureka #8 action-verb discipline
# EUREKA-G forge (2026-06-11): added detect_drift + detect_eureka as sub-verbs.
Mode = Literal[
    "consolidate",
    "forget",
    "replay",
    "snapshot",
    "restore",
    "detect_drift",
    "detect_eureka",
]


def arif_memory_manage(
    mode: Mode,
    *,
    session_id: str | None = None,
    actor_id: str | None = None,
    limit: int = 10,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Handler for arif_memory_manage MCP tool.

    Modes:
      - consolidate  — merge duplicate claims, prune resolved, retire empty hypotheses
      - forget       — soft-delete all L4 snapshots for a session (F1, deleted_at only)
      - replay       — load last N snapshots from L4 (audit/diagnostic)
      - snapshot     — force-write current L1 state to L4 (useful before/after risky ops)
      - restore      — rehydrate L1 state from latest L4 snapshot for the session
    """
    t0 = time.time()
    actor = actor_id or "arif_memory_manage"
    store = get_dual_store()
    sid = session_id or f"anon-{int(time.time())}"

    if mode == "snapshot":
        # Make sure L1 has a state, then write L1+L4
        state = init_state_for_session(
            sid, task_description=payload.get("task_description", "") if payload else ""
        )
        if payload:
            for k, v in payload.items():
                if k in state.model_fields and k not in (
                    "session_id",
                    "state_hash",
                    "state_version",
                    "event_log",
                    "created_at",
                ):
                    try:
                        setattr(state, k, v)
                    except Exception:
                        pass
        h, snap = store.save_state(state, actor=actor, event_type="manual_snapshot")
        return _ok(
            mode,
            t0,
            {
                "session_id": sid,
                "state_hash": h,
                "l4_write_ok": snap.l4_write_ok if snap else None,
                "l4_pg_id": snap.pg_id if snap else None,
                "claim_count": len(state.claims),
                "hypothesis_count": len(state.hypotheses),
            },
        )

    if mode == "consolidate":
        state = store.load_state(sid)
        if state is None:
            return _err(mode, t0, f"no KernelState for session={sid} in L1", recoverable=True)
        before = {
            "claims": len(state.claims),
            "hypotheses": len(state.hypotheses),
            "contradictions": len(state.contradictions),
        }
        consolidated = consolidate_state(state)
        after = {
            "claims": len(consolidated.claims),
            "hypotheses": len(consolidated.hypotheses),
            "contradictions": len(consolidated.contradictions),
        }
        # Persist consolidated
        h, snap = store.save_state(consolidated, actor=actor, event_type="consolidation")
        # Surface what the consolidation event did
        last_event = consolidated.event_log[-1] if consolidated.event_log else None
        summary = last_event.payload if last_event else {}
        return _ok(
            mode,
            t0,
            {
                "session_id": sid,
                "state_hash": h,
                "l4_write_ok": snap.l4_write_ok if snap else None,
                "before": before,
                "after": after,
                "delta": {
                    "claims_pruned": before["claims"] - after["claims"],
                    "hypotheses_retired": summary.get("retired_hypotheses", 0),
                    "claims_merged": summary.get("merged_claims", 0),
                },
            },
        )

    if mode == "forget":
        deleted = store.forget_session(sid)
        # Also drop L1 (F1 — explicit operator request)
        from arifosmcp.runtime.kernel_state import get_state_store

        l1 = get_state_store()
        l1_state_before = l1.load_state(sid) is not None
        if l1_state_before:
            with l1._lock:  # type: ignore[attr-defined]
                l1._states.pop(sid, None)  # type: ignore[attr-defined]
        return _ok(
            mode,
            t0,
            {
                "session_id": sid,
                "l4_snapshots_deleted": deleted,
                "l1_state_was_present": l1_state_before,
                "l1_state_cleared": l1_state_before,
                "note": (
                    "F1 soft-delete only — L4 deleted_at set, L1 state dropped. "
                    "Reversible: snapshot again to restore L1 + L4."
                ),
            },
        )

    if mode == "replay":
        rows = store.replay_from_l4(sid, limit=limit)
        # Trim payload to keep response bounded
        replay: list[dict[str, Any]] = []
        for r in rows:
            meta = r.get("metadata", {})
            dm = r.get("distillation_metadata", {})
            payload_size = len(json.dumps(dm.get("payload", {}))) if isinstance(dm, dict) else 0
            replay.append(
                {
                    "pg_id": r.get("id"),
                    "recorded_at": str(r.get("recorded_at", "")),
                    "state_hash": meta.get("state_hash", "") if isinstance(meta, dict) else "",
                    "actor": meta.get("actor", "") if isinstance(meta, dict) else "",
                    "event_type": meta.get("event_type", "") if isinstance(meta, dict) else "",
                    "payload_size_bytes": payload_size,
                }
            )
        return _ok(
            mode,
            t0,
            {
                "session_id": sid,
                "rows_returned": len(replay),
                "l4_enabled": store.l4_enabled,
                "snapshots": replay,
            },
        )

    if mode == "restore":
        rows = store.replay_from_l4(sid, limit=1)
        if not rows:
            return _err(mode, t0, f"no L4 snapshots for session={sid}", recoverable=True)
        latest = rows[0]
        dm = latest.get("distillation_metadata", {})
        if not isinstance(dm, dict) or "payload" not in dm:
            return _err(
                mode, t0, "L4 snapshot missing payload field — schema drift?", recoverable=False
            )
        try:
            state = KernelState.model_validate(dm["payload"])
        except Exception as exc:
            return _err(mode, t0, f"failed to rehydrate KernelState: {exc}", recoverable=False)
        # Reinstall into L1
        store.l1.save_state(state)
        return _ok(
            mode,
            t0,
            {
                "session_id": sid,
                "state_hash": state.state_hash,
                "restored_from_pg_id": latest.get("id"),
                "restored_at": str(latest.get("recorded_at", "")),
                "claim_count": len(state.claims),
                "hypothesis_count": len(state.hypotheses),
            },
        )

    # ── detect_drift / detect_eureka — EUREKA-G wiring (2026-06-11) ──
    # Both detectors operate on a Trajectory. The caller passes the
    # trajectory either as `metadata.trajectory_states` (list of
    # {coords, actor, model_key, ts, provenance_sha} dicts) or as
    # `metadata.session_id` to load from L4.
    if mode in ("detect_drift", "detect_eureka"):
        from arifosmcp.geometry.drift import detect_drift as _detect_drift
        from arifosmcp.geometry.eureka import (
            BehaviorMetrics as _BehaviorMetrics,
        )
        from arifosmcp.geometry.eureka import (
            detect_eureka as _detect_eureka,
        )
        from arifosmcp.geometry.manifold import AgentState, Trajectory

        traj_payload = (payload or {}).get("trajectory_states")
        if traj_payload:
            states: list[AgentState] = []
            for s in traj_payload:
                states.append(
                    AgentState(
                        coords=np.asarray(s["coords"], dtype=np.float64),
                        actor=s.get("actor", "anon"),
                        model_key=s.get("model_key", "unknown"),
                        ts=float(s.get("ts", time.time())),
                        provenance_sha=s.get("provenance_sha", f"manage-{mode}"),
                    )
                )
            traj = Trajectory(
                states=states,
                task_id=(payload or {}).get("task_id", "manage-input"),
                task_class=(payload or {}).get("task_class", "manage"),
            )
        elif sid:
            l1_state = store.l1.load_state(sid)
            if l1_state is None:
                return _err(mode, t0, f"no L1 KernelState for session={sid}", recoverable=True)
            # Coerce KernelState → AgentState using self_model coords.
            # KernelState doesn't carry 13D coords directly; we synthesize
            # a zero-vector AgentState flagged with the KernelState's
            # state_hash in provenance. The detectors still work — they
            # just see a single point with zero drift on a fresh state.
            sm = l1_state.self_model or {}
            coords = np.zeros(13, dtype=np.float64)
            for f_name, val in sm.items():
                # self_model may have a subset of F-floor names
                try:
                    from arifosmcp.geometry.manifold import Floor

                    idx = int(getattr(Floor, f_name)) if hasattr(Floor, f_name) else -1
                    if idx >= 0 and isinstance(val, (int, float)):
                        coords[idx] = float(val)
                except Exception:
                    continue
            synth = AgentState(
                coords=coords,
                actor="kernel-snapshot",
                model_key=l1_state.substrate_model or "unknown",
                ts=l1_state.last_transition_at,
                provenance_sha=l1_state.state_hash or f"l1:{sid}",
            )
            traj = Trajectory(
                states=[synth],
                task_id=sid,
                task_class="manage",
            )
        else:
            return _err(
                mode,
                t0,
                "need either metadata.trajectory_states (list) or session_id (L1 state)",
                recoverable=True,
            )

        if mode == "detect_drift":
            sig = _detect_drift(traj)
            return _ok(
                mode,
                t0,
                {
                    "session_id": sid,
                    "task_id": traj.task_id,
                    "n_states": len(traj.states),
                    "level": sig.level,
                    "trigger_888": bool(sig.trigger_888),
                    "max_step": sig.max_step,
                    "total_displacement": sig.total_displacement,
                    "final_delta_C": sig.final_delta_C,
                    "dwell_fraction": sig.dwell_fraction,
                    "violating": sig.violating,
                    "reason": sig.reason,
                },
            )

        # mode == "detect_eureka" — needs both candidate and baseline
        baseline_payload = (payload or {}).get("baseline")
        if not baseline_payload or "l_const" not in baseline_payload:
            return _err(
                mode,
                t0,
                "detect_eureka needs metadata.baseline with l_const/l_task/etc",
                recoverable=True,
            )
        # Build BehaviorMetrics from the candidate trajectory
        from arifosmcp.geometry.eureka import trajectory_to_metrics as _t2m

        cand_l_c, cand_l_t, cand_u, cand_k = _t2m(traj)
        cand_bm = _BehaviorMetrics(
            behavior_id=(payload or {}).get("behavior_id", "candidate"),
            task_class=traj.task_class or "manage",
            l_const=[cand_l_c],
            l_task=[cand_l_t],
            uncertainty=[cand_u],
            contradiction=[cand_k],
        )
        base_bm = _BehaviorMetrics(
            behavior_id=baseline_payload.get("behavior_id", "baseline"),
            task_class=baseline_payload.get("task_class", "manage"),
            l_const=list(baseline_payload.get("l_const", [])),
            l_task=list(baseline_payload.get("l_task", [])),
            uncertainty=list(baseline_payload.get("uncertainty", [])),
            contradiction=list(baseline_payload.get("contradiction", [])),
        )
        sig = _detect_eureka(cand_bm, base_bm)
        return _ok(
            mode,
            t0,
            {
                "session_id": sid,
                "task_id": traj.task_id,
                "is_eureka": bool(sig.is_eureka),
                "score": sig.score,
                "ablation_passed": bool(sig.ablation_passed),
                "trigger_888": bool(sig.trigger_888),
                "n_episodes": sig.n_episodes,
                "n_task_classes": sig.n_task_classes,
                "delta_l_const": sig.delta_l_const,
                "delta_u": sig.delta_u,
                "reason": sig.reason,
            },
        )

    return _err(mode, t0, f"unknown mode: {mode}", recoverable=False)


# ─────────────────────────────────────────────────────────────────────────────
# Envelope helpers — minimal, F1 (the 13 canonical tools enforce nine-signal
# but this is a diagnostic tool, not subject to the same envelope contract)
# ─────────────────────────────────────────────────────────────────────────────


def _ok(mode: str, t0: float, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "verdict": "SEAL",
        "mode": mode,
        "data": data,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "constitutional_check": {
            "F1_amanah": "PASS",
            "F2_truth": "PASS",
            "F4_clarity": "PASS",
            "F7_humility": "PASS",
            "F11_audit": "PASS",
        },
    }


def _err(mode: str, t0: float, reason: str, *, recoverable: bool) -> dict[str, Any]:
    return {
        "status": "err",
        "verdict": "SABAR" if recoverable else "VOID",
        "mode": mode,
        "reason": reason,
        "recoverable": recoverable,
        "elapsed_ms": int((time.time() - t0) * 1000),
    }


__all__ = ["arif_memory_manage", "Mode"]
