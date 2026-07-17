"""
SE Stage Engine — Seal-A constitutional stage advancement.

R1 (Seal-A close path, 2026-07-17):
  Stage stays at ``000`` until a proof bundle is presented. Hand-editing
  the stage field is VOID. Advance is allowed only when ALL of:

    1. identity coherent (standing actor == birth actor == SCT claims actor)
    2. full spine GREEN (run_spine(fast=False), skipped=0, all_green=True)
    3. vault_replay PASS
    4. SOT active (or explicitly HOLD — advance still blocked until R2 seals SOT)

Forbidden:
  - Manual bump of stage to 111 / 222 / …
  - Fast-mode spine GREEN treated as proof
  - Partial proofs

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# SE stages for Seal-A civilization track (not the metabolic 000→999 loop).
# 000 = INIT (pre-proof). 111 = SENSE (first governed advance after proof).
SE_STAGE_ORDER: tuple[str, ...] = ("000", "111", "222", "333", "555", "666", "777", "888", "999")
SE_STAGE_INIT: str = "000"
SE_STAGE_SENSE: str = "111"

# Persistent store — reversible (delete file → back to 000).
_DEFAULT_STATE_PATH = Path("/var/lib/arifos/se_stage_state.json")
_FALLBACK_STATE_PATH = Path("/tmp/arifos_se_stage_state.json")

_lock = threading.RLock()


@dataclass(frozen=True)
class IdentityCoherence:
    """Three-way identity agreement required for stage advance."""

    standing_actor: str
    birth_actor: str
    sct_claims_actor: str

    @property
    def coherent(self) -> bool:
        a = (self.standing_actor or "").strip().lower()
        b = (self.birth_actor or "").strip().lower()
        c = (self.sct_claims_actor or "").strip().lower()
        if not a or not b or not c:
            return False
        return a == b == c


@dataclass(frozen=True)
class SpineProof:
    """Full (non-fast) conformance spine result excerpt."""

    all_green: bool
    skipped: int
    substrate_gate: str
    vault_replay_pass: bool
    fast_mode: bool
    score: str = ""
    constitutional_grade: bool = False

    @property
    def valid(self) -> bool:
        return (
            bool(self.all_green)
            and int(self.skipped) == 0
            and not bool(self.fast_mode)
            and str(self.substrate_gate).upper() == "GREEN"
            and bool(self.vault_replay_pass)
        )


@dataclass(frozen=True)
class SotProof:
    """Active SOT presence. R2 must seal operational SOT before advance."""

    active: bool
    sot_id: str = ""
    sot_hash: str = ""
    hold_reason: str = ""

    @property
    def valid(self) -> bool:
        return bool(self.active) and bool(self.sot_hash) and not self.hold_reason


@dataclass(frozen=True)
class StageProofBundle:
    """The only legitimate input to advance SE stage above 000."""

    identity: IdentityCoherence
    spine: SpineProof
    sot: SotProof
    target_stage: str = SE_STAGE_SENSE
    issued_at: str = ""
    issuer: str = "se_stage_engine"
    notes: str = ""

    def failure_reasons(self) -> list[str]:
        reasons: list[str] = []
        if not self.identity.coherent:
            reasons.append("identity_incoherent")
        if self.spine.fast_mode:
            reasons.append("spine_fast_mode_forbidden")
        if int(self.spine.skipped) > 0:
            reasons.append(f"spine_skipped={self.spine.skipped}")
        if not self.spine.all_green:
            reasons.append("spine_not_all_green")
        if str(self.spine.substrate_gate).upper() != "GREEN":
            reasons.append(f"substrate_gate={self.spine.substrate_gate}")
        if not self.spine.vault_replay_pass:
            reasons.append("vault_replay_not_pass")
        if not self.sot.valid:
            reasons.append(self.sot.hold_reason or "sot_not_active")
        if self.target_stage not in SE_STAGE_ORDER:
            reasons.append(f"unknown_target_stage={self.target_stage}")
        elif SE_STAGE_ORDER.index(self.target_stage) <= SE_STAGE_ORDER.index(SE_STAGE_INIT):
            reasons.append("target_not_beyond_000")
        return reasons

    @property
    def admissible(self) -> bool:
        return len(self.failure_reasons()) == 0


@dataclass
class SeStageState:
    """Mutable kernel SE stage record (persisted)."""

    stage: str = SE_STAGE_INIT
    advanced_at: str | None = None
    advanced_by: str | None = None
    proof_digest: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "advanced_at": self.advanced_at,
            "advanced_by": self.advanced_by,
            "proof_digest": self.proof_digest,
            "history": list(self.history),
        }


def _state_path() -> Path:
    try:
        _DEFAULT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Write probe
        probe = _DEFAULT_STATE_PATH.with_suffix(".probe")
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return _DEFAULT_STATE_PATH
    except OSError:
        return _FALLBACK_STATE_PATH


def _load_state() -> SeStageState:
    path = _state_path()
    if not path.exists():
        return SeStageState()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return SeStageState(
            stage=str(raw.get("stage") or SE_STAGE_INIT),
            advanced_at=raw.get("advanced_at"),
            advanced_by=raw.get("advanced_by"),
            proof_digest=raw.get("proof_digest"),
            history=list(raw.get("history") or []),
        )
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        logger.warning("se_stage_engine: corrupt state, reset to 000: %s", exc)
        return SeStageState()


def _save_state(state: SeStageState) -> None:
    path = _state_path()
    path.write_text(json.dumps(state.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


def _proof_digest(bundle: StageProofBundle) -> str:
    payload = {
        "identity": asdict(bundle.identity),
        "spine": asdict(bundle.spine),
        "sot": asdict(bundle.sot),
        "target_stage": bundle.target_stage,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def get_se_stage() -> dict[str, Any]:
    """Public read of current SE stage. Never advances."""
    with _lock:
        state = _load_state()
        return {
            "se_stage": state.stage,
            "at_init": state.stage == SE_STAGE_INIT,
            "advanced_at": state.advanced_at,
            "advanced_by": state.advanced_by,
            "proof_digest": state.proof_digest,
            "history_len": len(state.history),
            "law": "advance_only_on_proof_bundle",
            "forbidden": "manual_stage_bump",
        }


def set_stage_manual(target: str, *, actor: str = "unknown") -> dict[str, Any]:
    """Always VOID. Hand edits are constitutionally illegal (R1)."""
    with _lock:
        state = _load_state()
        return {
            "verdict": "VOID",
            "reason": "manual_stage_bump_forbidden",
            "requested_stage": target,
            "current_stage": state.stage,
            "actor": actor,
            "floor": "F1_AMANAH+F2_TRUTH",
            "doctrine": "Stage advances only via try_advance(proof_bundle)",
        }


def try_advance(bundle: StageProofBundle) -> dict[str, Any]:
    """Attempt SE stage advance under proof bundle.

    Returns structured receipt with verdict SEAL | HOLD | VOID.
    """
    with _lock:
        state = _load_state()
        reasons = bundle.failure_reasons()
        if reasons:
            return {
                "verdict": "HOLD",
                "advanced": False,
                "current_stage": state.stage,
                "requested_stage": bundle.target_stage,
                "reasons": reasons,
                "proof_digest": _proof_digest(bundle),
            }

        # Only allow forward by one hop from current (no skip).
        try:
            cur_idx = SE_STAGE_ORDER.index(state.stage)
            tgt_idx = SE_STAGE_ORDER.index(bundle.target_stage)
        except ValueError:
            return {
                "verdict": "VOID",
                "advanced": False,
                "current_stage": state.stage,
                "requested_stage": bundle.target_stage,
                "reasons": ["stage_not_in_order"],
            }

        if tgt_idx != cur_idx + 1:
            return {
                "verdict": "HOLD",
                "advanced": False,
                "current_stage": state.stage,
                "requested_stage": bundle.target_stage,
                "reasons": [f"not_adjacent_hop:{state.stage}->{bundle.target_stage}"],
            }

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        digest = _proof_digest(bundle)
        entry = {
            "from": state.stage,
            "to": bundle.target_stage,
            "at": now,
            "issuer": bundle.issuer,
            "proof_digest": digest,
            "notes": bundle.notes,
        }
        state.history.append(entry)
        state.stage = bundle.target_stage
        state.advanced_at = now
        state.advanced_by = bundle.issuer
        state.proof_digest = digest
        _save_state(state)
        logger.info(
            "se_stage_engine: advanced %s -> %s digest=%s",
            entry["from"],
            entry["to"],
            digest[:24],
        )
        return {
            "verdict": "SEAL",
            "advanced": True,
            "current_stage": state.stage,
            "from_stage": entry["from"],
            "to_stage": entry["to"],
            "advanced_at": now,
            "proof_digest": digest,
            "reasons": [],
        }


def evaluate_live_proof_for_advance(
    *,
    standing_actor: str,
    birth_actor: str,
    sct_claims_actor: str,
    target_stage: str = SE_STAGE_SENSE,
    spine: dict[str, Any] | None = None,
    sot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a live proof bundle and attempt advance.

    Callers may pass a precomputed spine/sot dict (tests) or leave None
    to probe live systems. Live probe of full spine is expensive — prefer
    injecting spine results from an already-run canary.
    """
    identity = IdentityCoherence(
        standing_actor=standing_actor,
        birth_actor=birth_actor,
        sct_claims_actor=sct_claims_actor,
    )

    if spine is None:
        try:
            from arifosmcp.transport.conformance_spine import run_spine

            live = run_spine(fast=False)
        except Exception as exc:
            live = {
                "all_green": False,
                "skipped": 9,
                "substrate_gate": "HOLD",
                "fast_mode": False,
                "score": "0/9",
                "constitutional_grade": False,
                "checks": [],
                "error": str(exc),
            }
    else:
        live = spine

    vault_pass = False
    for c in live.get("checks") or []:
        if c.get("check") == "vault_replay" and c.get("verdict") == "PASS":
            vault_pass = True
            break
    # Explicit override from caller
    if "vault_replay_pass" in live:
        vault_pass = bool(live["vault_replay_pass"])

    spine_proof = SpineProof(
        all_green=bool(live.get("all_green")),
        skipped=int(live.get("skipped") or 0),
        substrate_gate=str(live.get("substrate_gate") or "HOLD"),
        vault_replay_pass=vault_pass,
        fast_mode=bool(live.get("fast_mode")),
        score=str(live.get("score") or ""),
        constitutional_grade=bool(live.get("constitutional_grade")),
    )

    if sot is None:
        try:
            from arifosmcp.runtime.sot_active import get_active_sot

            sot_live = get_active_sot()
        except Exception as exc:
            sot_live = {
                "active": False,
                "sot_id": "",
                "sot_hash": "",
                "hold_reason": f"sot_probe_error:{exc}",
            }
    else:
        sot_live = sot

    sot_proof = SotProof(
        active=bool(sot_live.get("active")),
        sot_id=str(sot_live.get("sot_id") or ""),
        sot_hash=str(sot_live.get("sot_hash") or ""),
        hold_reason=str(sot_live.get("hold_reason") or ""),
    )

    bundle = StageProofBundle(
        identity=identity,
        spine=spine_proof,
        sot=sot_proof,
        target_stage=target_stage,
        issued_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        issuer="se_stage_engine.evaluate_live",
    )
    result = try_advance(bundle)
    result["bundle_admissible"] = bundle.admissible
    result["bundle_reasons"] = bundle.failure_reasons()
    result["identity_coherent"] = identity.coherent
    result["spine_valid"] = spine_proof.valid
    result["sot_valid"] = sot_proof.valid
    return result


def reset_for_tests() -> None:
    """Test-only: wipe SE stage state back to 000."""
    with _lock:
        path = _state_path()
        if path.exists():
            path.unlink()
        _save_state(SeStageState())


__all__ = [
    "SE_STAGE_ORDER",
    "SE_STAGE_INIT",
    "SE_STAGE_SENSE",
    "IdentityCoherence",
    "SpineProof",
    "SotProof",
    "StageProofBundle",
    "SeStageState",
    "get_se_stage",
    "set_stage_manual",
    "try_advance",
    "evaluate_live_proof_for_advance",
    "reset_for_tests",
]
