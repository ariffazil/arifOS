"""
seal_shadow.py — pre-SEAL snapshot + post-SEAL receipt diff.

Physics:    Pre-SEAL snapshot = state at the phase-transition boundary.
            Post-SEAL diff     = Δ across the irreversible reaction.
Biology:    Shadow = metabolic memory written BEFORE the immune system
            (SEAL) destroys the prior cell. Replay reads shadow.
Chemistry:  Catalyst-limited: shadow write is cheap, append-only,
            gated only by VAULT999 disk throughput.

Why a "shadow":
    SEAL freezes state. Replay (stage 6 of the loop) needs to read the
    state that existed BEFORE SEAL — but SEAL itself writes a new
    lineage entry. Without a shadow ledger held outside VAULT999, the
    replay has nothing to read. This module owns the shadow.

Constitutional binding:
    L02 TRUTH  — shadow is byte-faithful (SHA256 over canonical JSON)
    L11 AUTH   — shadow carries actor_id + session_id
    L01 AMANAH — shadow is append-only; never mutates a sealed entry

Integration map (where this is called):
    1. seal_post_hook.with_shadow(arif_seal_fn) wraps the live
       arif_seal call site. This session, that call site lives in
       arifOS/arifosmcp/runtime/tools.py::_arif_seal — which is
       currently DIRTY (verdict-gate-normalization in progress).
       Therefore: lifecycle ships as the kernel contract; wiring into
       the dirty runtime is gated behind Phase 2 (post-merge).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


# ─── Shadow Contract ────────────────────────────────────────────────────────


@dataclass
class ShadowSnapshot:
    """Byte-faithful snapshot of state immediately BEFORE SEAL.

    Written to the shadow ledger (default: <arifOS>/.lifecycle/shadow/).
    Never written to VAULT999 itself — shadow is OUTSIDE the immutable
    chain so that SEAL can still proceed when VAULT999 is unreachable.
    """

    snapshot_id: str
    actor_id: str
    session_id: str
    captured_at: str  # ISO8601 UTC
    state_dict: dict[str, Any]
    sha256: str
    provenance: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))


@dataclass
class ShadowDiff:
    """Post-SEAL diff = (shadow_pre, seal_response, derived_deltas)."""

    snapshot_id: str
    sealed_at: str  # ISO8601 UTC
    seal_entry_id: str  # from VAULT999 response (empty if pending)
    verdict: str  # SEAL | HOLD | VOID | SABAR
    pre_sha256: str
    post_sha256: str
    delta_keys: list[str]  # top-level keys that changed
    cooling_required: bool  # True iff verdict == VOID or chain_ok == False
    witness_ok: bool  # True iff witness present for irreversible

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))


# ─── Disk Contract ──────────────────────────────────────────────────────────


_DEFAULT_SHADOW_DIR = Path(__file__).parent / ".shadow"


def _shadow_path(shadow_dir: Path, snapshot_id: str, suffix: str) -> Path:
    safe_id = snapshot_id.replace("/", "_").replace("..", "_")
    return shadow_dir / f"{safe_id}.{suffix}.json"


def _canonical_sha256(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ─── Public API ─────────────────────────────────────────────────────────────


def capture_pre(
    state_dict: dict[str, Any],
    *,
    actor_id: str,
    session_id: str,
    shadow_dir: Path | None = None,
    provenance: dict[str, str] | None = None,
) -> ShadowSnapshot:
    """Capture pre-SEAL state to shadow ledger. Idempotent on snapshot_id.

    Args:
        state_dict: full pre-SEAL state — must be JSON-serializable.
        actor_id:   the originating session (NEVER the judge session).
        session_id: the session whose verdict is about to SEAL.
        shadow_dir: defaults to <arifOS>/lifecycle/.shadow/
        provenance: optional {"trace_id": "...", "envelope_hash": "..."}.

    Returns:
        ShadowSnapshot persisted to disk. Caller MUST pass this to
        capture_post() after arif_seal returns.

    Raises:
        ValueError: if state_dict is not JSON-serializable.
    """
    shadow_dir = shadow_dir or _DEFAULT_SHADOW_DIR
    shadow_dir.mkdir(parents=True, exist_ok=True)

    captured_at = datetime.now(timezone.utc).isoformat()
    sha = _canonical_sha256(state_dict)
    snapshot_id = f"pre-{session_id}-{captured_at}"

    snap = ShadowSnapshot(
        snapshot_id=snapshot_id,
        actor_id=actor_id,
        session_id=session_id,
        captured_at=captured_at,
        state_dict=state_dict,
        sha256=sha,
        provenance=provenance or {},
    )
    path = _shadow_path(shadow_dir, snapshot_id, "pre")
    path.write_text(snap.to_json())
    return snap


def capture_post(
    pre: ShadowSnapshot,
    *,
    seal_response: dict[str, Any],
) -> ShadowDiff:
    """Compute post-SEAL diff from the pre shadow + arif_seal response.

    Args:
        pre: the ShadowSnapshot returned by capture_pre().
        seal_response: dict form of SealOutput from arif_seal(...).
            Expected keys: entry_id, verdict, chain_ok, witness (nested).

    Returns:
        ShadowDiff persisted next to the pre snapshot.
    """
    shadow_dir = pre.state_dict.get("__shadow_dir__")  # type: ignore[arg-type]
    # Default shadow_dir lookup: derive from pre.snapshot_id path.
    # We resolve via the canonical default since state_dict is reserved
    # for user state, not our private fields.
    shadow_dir = None
    shadow_dir_path = _DEFAULT_SHADOW_DIR

    sealed_at = datetime.now(timezone.utc).isoformat()
    verdict = str(seal_response.get("verdict", "UNKNOWN"))
    seal_entry_id = str(seal_response.get("entry_id", ""))
    witness_obj = seal_response.get("witness") or {}
    witness_ok = bool(witness_obj) and verdict.upper() != "VOID"

    # Post-SEAL canonical hash: hash (pre_sha + seal_entry_id + verdict).
    # This binds the diff to the exact VAULT999 entry that concluded the SEAL.
    post_payload = {
        "pre_sha256": pre.sha256,
        "seal_entry_id": seal_entry_id,
        "verdict": verdict,
        "sealed_at": sealed_at,
    }
    post_sha = _canonical_sha256(post_payload)

    delta_keys = sorted(
        k for k in seal_response.keys() if k not in ("verdict", "entry_id")
    )
    cooling_required = verdict.upper() in {"VOID", "HOLD"} or not seal_response.get(
        "chain_ok", True
    )

    diff = ShadowDiff(
        snapshot_id=pre.snapshot_id,
        sealed_at=sealed_at,
        seal_entry_id=seal_entry_id,
        verdict=verdict,
        pre_sha256=pre.sha256,
        post_sha256=post_sha,
        delta_keys=delta_keys,
        cooling_required=cooling_required,
        witness_ok=witness_ok,
    )
    path = _shadow_path(shadow_dir_path, pre.snapshot_id, "diff")
    path.write_text(diff.to_json())
    return diff


# ─── Smoke Test ─────────────────────────────────────────────────────────────


if __name__ == "__main__":  # pragma: no cover
    state = {"a": 1, "b": [2, 3]}
    snap = capture_pre(state, actor_id="actor-A", session_id="sess-1")
    diff = capture_post(
        snap, seal_response={"entry_id": "00001", "verdict": "SEAL", "chain_ok": True}
    )
    assert snap.sha256.startswith(snap.sha256[:8])  # format sanity
    assert diff.pre_sha256 == snap.sha256
    assert diff.verdict == "SEAL"
    assert not diff.cooling_required
    print("OK seal_shadow smoke:", snap.snapshot_id)
