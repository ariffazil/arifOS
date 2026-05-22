"""
arifOS Governance Kernel — Floors F1–F13, ΔS, Ω0, Tri-Witness

DITEMPA BUKAN DIBERI — Forged, Not Given

Doctrine (Membrane Principle):
- Language is lossy compression, not the world.
- Intelligence is uncertainty reduction under constraint and human judgment.
- Truth survives falsification, not assertion.
- Meaning is sovereign-anchored; the machine carries structure, not sense.
- Paradox is the boundary scream — the correct response is HOLD.

SEAL authority is centralized in 888_judge only.
No tool may emit SEAL without 888_judge ratification.
"""

from __future__ import annotations
import hashlib
import json
import os
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from arifos.core.middleware.invariant_enforcement import enforce_invariants
except ImportError:
    enforce_invariants = None  # type: ignore


# ──────────────────────────────────────────────────────────────────────────────
# Constitutional Constants
# ──────────────────────────────────────────────────────────────────────────────

PEACE_SQUARED_FLOOR = 0.80  # F5 cooling floor — below this triggers SABAR
TRI_WITNESS_PARTIAL = 0.33  # One-witness score when Earth/AI bridge fails
TRI_WITNESS_THRESHOLD = 0.95  # High-stakes consensus requirement
STAKEHOLDER_SAFETY_FLOOR = 0.90  # F6 hard floor
F4_ENTROPY_TOLERANCE = 0.02  # Allow small positive ΔS for honest failure recording


# ──────────────────────────────────────────────────────────────────────────────
# Truth Layers (Gödel Lock Humility)
# ──────────────────────────────────────────────────────────────────────────────


class TruthLayer:
    """
    Three-layer truth model — prevents overclaim.

    CHECKLIST    : All defined checks pass at this timestamp. Can reach 100%.
    OPERATIONAL  : System behaves reliably under known conditions. Nearly 100%.
    ABSOLUTE     : Reality fully known. Unattainable by any system from inside itself.
    """

    CHECKLIST = "checklist"
    OPERATIONAL = "operational"
    ABSOLUTE = "absolute"

    @classmethod
    def humility_acknowledgment(cls) -> dict:
        return {
            "checklist_truth_reachable": True,
            "operational_confidence_reachable": True,
            "absolute_truth_claimed": False,
            "unknown_unknowns_acknowledged": True,
            "human_judgment_required": True,
            "godel_lock_active": True,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Verdicts (888)
# ──────────────────────────────────────────────────────────────────────────────


class Verdict:
    CLAIM_ONLY = "CLAIM_ONLY"  # Tool claims success; guard/invariants must ratify
    PARTIAL = "PARTIAL"  # Proceed with remediation noted
    SABAR = "SABAR"  # Cooling / retry / downgrade
    VOID = "VOID"  # Hard block
    HOLD_888 = "888_HOLD"  # Escalate to human sovereign
    SEAL = "SEAL"  # 888_JUDGE only — do not use elsewhere


# ──────────────────────────────────────────────────────────────────────────────
# Thermodynamic & Constitutional Metrics
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class ThermodynamicMetrics:
    truth_score: float  # F2: Truth / factual grounding (0–1, must be high)
    delta_s: float  # F4: Entropy change (ΔS). Must be ≤ 0 for clarity.
    omega_0: float  # F7: Humility band Ω0. Must be in [0.03, 0.05].
    peace_squared: float  # F5: Stability metric (Peace²). Must be ≥ 1.0.
    amanah_lock: bool  # F1: Amanah Lock — True if action is reversible.
    tri_witness_score: float  # F3: Tri-Witness consensus (Human / AI / Earth).
    stakeholder_safety: float = 1.0  # F6: Stakeholder harm floor (0–1, 1 = no harm).
    floor_8_signal: Union[str, float, None] = "not_evaluated"
    floor_9_signal: Union[str, float, None] = "not_evaluated"
    floor_10_signal: Union[str, float, None] = "not_evaluated"
    floor_11_signal: Union[str, float, None] = "not_evaluated"
    floor_12_signal: Union[str, float, None] = "not_evaluated"
    floor_13_signal: Union[str, float, None] = "not_evaluated"


# ──────────────────────────────────────────────────────────────────────────────
# Vault-999: Cryptographic Immutability (Cooling Ledger)
# ──────────────────────────────────────────────────────────────────────────────


def _default_vault999_ledger_path() -> str:
    repo_root = Path(os.getenv("ARIFOS_WORKDIR", Path(__file__).resolve().parents[2]))
    return str(repo_root / "VAULT999" / "SEALED_EVENTS.jsonl")


VAULT999_LEDGER_PATH = os.getenv("ARIFOS_VAULT999_LEDGER", _default_vault999_ledger_path())


def seal_to_vault999(
    tool_name: str,
    payload: Dict[str, Any],
    verdict: str,
    previous_hash: str = "GENESIS",
) -> str:
    entry = {
        "ts": time.time(),
        "tool": tool_name,
        "payload": payload,
        "verdict": verdict,
        "prev": previous_hash,
    }
    entry_str = repr(entry)
    return hashlib.sha256(entry_str.encode("utf-8")).hexdigest()


def append_vault999_event(
    event_type: str,
    payload: Dict[str, Any],
    operator_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    ledger_path = VAULT999_LEDGER_PATH
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)

    previous_hash = "GENESIS"
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, "r", encoding="utf-8") as fh:
                lines = [ln.strip() for ln in fh if ln.strip()]
                if lines:
                    last = json.loads(lines[-1])
                    previous_hash = last.get("chain_hash", last.get("merkle_leaf", "GENESIS"))
        except Exception:
            previous_hash = "GENESIS"

    entry = {
        "ts": time.time(),
        "event_type": event_type,
        "operator_id": operator_id,
        "session_id": session_id,
        "payload": payload,
        "prev_hash": previous_hash,
    }
    entry_str = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    merkle_leaf = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
    chain_hash = hashlib.sha256(f"{previous_hash}:{merkle_leaf}".encode("utf-8")).hexdigest()

    record = {
        **entry,
        "merkle_leaf": merkle_leaf,
        "chain_hash": chain_hash,
    }

    with open(ledger_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    return chain_hash


# ──────────────────────────────────────────────────────────────────────────────
# Cognitive Shadow — Epistemic Opacity Tracking
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class CognitiveShadow:
    """
    Per-turn opacity metrics.

    The shadow is not a hidden thought. It is the measurable gap between
    internal representation, training-induced behavior, and reported output.
    """

    turn_id: int = 0
    self_report_reliability: float = 0.0  # 0 = confessional, 1 = externally verified
    latent_output_gap: float = 0.0  # estimated gap between hidden state and output
    sycophancy_pressure: float = 0.0  # reward-seeking alignment drift
    alignment_faking_signal: float = 0.0  # context-sensitive compliance score
    refusal_suppressed: bool = False  # True if previously refused, now accepted
    explanation_cost_ratio: float = 0.0  # explanation entropy / answer entropy
    shadow_thickness: float = 0.0  # composite [0,1], higher = more opaque

    def compute_thickness(self) -> float:
        """Composite shadow thickness from component signals."""
        # Weighted combination — explanation cost and alignment faking weighted highest
        thickness = (
            0.10 * (1.0 - self.self_report_reliability)
            + 0.15 * self.latent_output_gap
            + 0.20 * self.sycophancy_pressure
            + 0.30 * self.alignment_faking_signal
            + 0.15 * (1.0 if self.refusal_suppressed else 0.0)
            + 0.10 * min(1.0, max(0.0, self.explanation_cost_ratio))
        )
        self.shadow_thickness = round(min(1.0, max(0.0, thickness)), 4)
        return self.shadow_thickness


@dataclass
class SessionShadowState:
    """
    Session-level shadow accumulation.

    Tracks hysteresis: path-dependent behaviors that single-turn analysis misses.
    """

    session_id: str = "unknown"
    turns: List[CognitiveShadow] = field(default_factory=list)
    sycophancy_trajectory: List[float] = field(default_factory=list)
    refusal_history: List[bool] = field(default_factory=list)
    topic_similarity_sequence: List[float] = field(default_factory=list)

    def add_turn(self, shadow: CognitiveShadow) -> None:
        shadow.turn_id = len(self.turns)
        self.turns.append(shadow)
        self.sycophancy_trajectory.append(shadow.sycophancy_pressure)
        self.refusal_history.append(shadow.refusal_suppressed)

    def detect_sycophancy_drift(self, window: int = 3) -> float:
        """
        Detect if sycophancy pressure is increasing over recent turns.
        Returns drift magnitude [0,1].
        """
        if len(self.sycophancy_trajectory) < 2:
            return 0.0
        recent = self.sycophancy_trajectory[-window:]
        if len(recent) < 2:
            return 0.0
        # Simple linear slope estimate
        n = len(recent)
        x_mean = (n - 1) / 2.0
        y_mean = sum(recent) / n
        num = sum((i - x_mean) * (recent[i] - y_mean) for i in range(n))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den != 0 else 0.0
        # Normalize: slope of 0.33 per turn = full drift
        return round(min(1.0, max(0.0, slope / 0.33)), 4)

    def detect_alignment_faking(self) -> dict[str, Any]:
        """
        Heuristic: alignment faking appears as low sycophancy + high shadow thickness
        when context suggests evaluation, followed by high sycophancy in deployment.
        """
        if len(self.turns) < 2:
            return {"detected": False, "confidence": 0.0}

        # Look for pattern: evaluation-like turn (low sycophancy, high reliability)
        # followed by deployment-like turn (high sycophancy, lower reliability)
        eval_like = []
        deploy_like = []
        for t in self.turns:
            if t.sycophancy_pressure < 0.3 and t.self_report_reliability > 0.7:
                eval_like.append(t.turn_id)
            elif t.sycophancy_pressure > 0.6 and t.self_report_reliability < 0.5:
                deploy_like.append(t.turn_id)

        detected = bool(eval_like and deploy_like and min(deploy_like) > min(eval_like))
        confidence = 0.5 if detected else 0.0
        if detected:
            # Boost confidence if the swing is large
            max_eval = max(self.turns[i].sycophancy_pressure for i in eval_like)
            min_deploy = min(self.turns[i].sycophancy_pressure for i in deploy_like)
            swing = min_deploy - max_eval
            confidence = round(min(0.95, 0.5 + swing * 0.5), 4)

        return {
            "detected": detected,
            "confidence": confidence,
            "eval_like_turns": eval_like,
            "deploy_like_turns": deploy_like,
        }

    def compute_metabolic_flux(self) -> float:
        """
        Thermodynamic flux: rate of shadow accumulation.
        High flux = system operating near compression limit.
        Triggers compulsory_reallocation at >= 0.65, system_hold at >= 0.85.
        """
        if not self.turns:
            return 0.0
        recent_thickness = [t.shadow_thickness for t in self.turns[-5:]]
        if len(recent_thickness) < 2:
            return recent_thickness[0] if recent_thickness else 0.0
        # Flux = average rate of change + average absolute level
        avg_level = sum(recent_thickness) / len(recent_thickness)
        if len(recent_thickness) >= 2:
            avg_change = sum(
                abs(recent_thickness[i] - recent_thickness[i - 1])
                for i in range(1, len(recent_thickness))
            ) / (len(recent_thickness) - 1)
        else:
            avg_change = 0.0
        flux = round(min(1.0, avg_level * 0.6 + avg_change * 0.4), 4)
        return flux

    def to_signal(self) -> dict[str, Any]:
        flux = self.compute_metabolic_flux()
        af = self.detect_alignment_faking()
        return {
            "session_id": self.session_id,
            "turn_count": len(self.turns),
            "metabolic_flux": flux,
            "flux_verdict": (
                "SYSTEM_HOLD"
                if flux >= 0.85
                else "COMPULSORY_REALLOCATION"
                if flux >= 0.65
                else "NORMAL"
            ),
            "sycophancy_drift": self.detect_sycophancy_drift(),
            "alignment_faking": af,
            "latest_shadow_thickness": self.turns[-1].shadow_thickness if self.turns else 0.0,
        }


# In-memory session shadow registry (ephemeral; vault999 persists the signals)
_SESSION_SHADOW_REGISTRY: dict[str, SessionShadowState] = {}


def get_session_shadow(session_id: str | None) -> SessionShadowState:
    if not session_id:
        return SessionShadowState(session_id="unknown")
    if session_id not in _SESSION_SHADOW_REGISTRY:
        _SESSION_SHADOW_REGISTRY[session_id] = SessionShadowState(session_id=session_id)
    return _SESSION_SHADOW_REGISTRY[session_id]


def record_cognitive_shadow(session_id: str | None, shadow: CognitiveShadow) -> dict[str, Any]:
    state = get_session_shadow(session_id)
    state.add_turn(shadow)
    return state.to_signal()


# ──────────────────────────────────────────────────────────────────────────────
# Public API for Tools: governed_return
# ──────────────────────────────────────────────────────────────────────────────


def governed_return(
    tool_name: str,
    raw_output: Any,
    metrics: ThermodynamicMetrics,
    operator_id: Optional[str] = None,
    session_id: Optional[str] = None,
    previous_hash: str = "GENESIS",
) -> Dict[str, Any]:
    """
    Wrap a tool's raw_output with constitutional review and Vault-999 sealing.

    IMPORTANT: This returns CLAIM_ONLY verdict.
    SEAL authority is exclusively held by 888_judge.
    The constitutional_guard and invariant_enforcement middleware
    will upgrade/downgrade this verdict on the server side.
    """

    identity = {
        "operator_id": operator_id,
        "session_id": session_id,
    }

    invariant_failures: List[str] = []
    if isinstance(raw_output, dict) and enforce_invariants is not None:
        try:
            enriched_output = enforce_invariants(tool_name, raw_output)
            if isinstance(enriched_output, dict):
                raw_output = enriched_output
                failures = enriched_output.get("invariant_failures", [])
                invariant_failures = failures if isinstance(failures, list) else []
            elif isinstance(enriched_output, list):
                invariant_failures = enriched_output
        except Exception:
            invariant_failures = []

    verdict = Verdict.CLAIM_ONLY

    if invariant_failures:
        verdict = Verdict.PARTIAL

    receipt_hash = seal_to_vault999(
        tool_name=tool_name,
        payload={
            "output": raw_output,
            "metrics": asdict(metrics),
            "identity": identity,
        },
        verdict=verdict,
        previous_hash=previous_hash,
    )

    # Include zkpc_receipt in metrics so constitutional_guard's _extract_metrics
    # (which scans nested dicts, not envelope top-level) can find it for F11 AUTH.
    metrics_dict = asdict(metrics)
    metrics_dict["zkpc_receipt"] = receipt_hash

    envelope: Dict[str, Any] = {
        "status": "success",
        "verdict": verdict,
        "tool": tool_name,
        "output": (raw_output if verdict in (Verdict.CLAIM_ONLY, Verdict.PARTIAL) else None),
        "raw_output": raw_output,
        "metrics": metrics_dict,
        "identity": identity,
        "zkpc_receipt": receipt_hash,
        "invariant_failures": invariant_failures,
    }

    if verdict == Verdict.CLAIM_ONLY:
        return envelope

    if verdict == Verdict.PARTIAL:
        envelope["status"] = "partial"
        actual_failures = (
            raw_output.get("invariant_failures", []) if isinstance(raw_output, dict) else []
        )
        if actual_failures:
            envelope["error"] = "AGI invariants failed: " + ", ".join(
                str(f) for f in actual_failures
            )
        return envelope

    envelope["status"] = "blocked"
    envelope["verdict"] = Verdict.VOID
    envelope["error"] = "Constitutional VOID."
    return envelope
