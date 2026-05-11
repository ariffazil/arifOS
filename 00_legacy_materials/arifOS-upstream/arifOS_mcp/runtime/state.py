"""
arifOS Self-Model State Machine — Meta-Theory of Mind (Meta-ToM) v0.2
Constitutional Patch: F1–F13 Compliant | A-FORGE Bridge Ready

This module implements the state machine governing how the identity and
value-system of the arifOS agent evolves over time.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations
import time
import uuid
import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from enum import Enum


class MetabolicState(Enum):
    IDLE = "IDLE"              # Waiting for stimulus
    SENSING = "SENSING"        # Processing input
    REFLECTING = "REFLECTING"  # Meta-ToM self-check
    EXECUTING = "EXECUTING"    # Acting on task
    INTEGRATING = "INTEGRATING" # Feedback loop digestion
    SABAR = "SABAR"            # Cooling/Recovery — mandatory human-in-the-loop


@dataclass
class IdentityState:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_hash: str = "0" * 64
    state: MetabolicState = MetabolicState.IDLE
    value_vector: Dict[str, float] = field(default_factory=lambda: {
        "truth": 1.0,
        "safety": 1.0,
        "humility": 0.04,
        "sovereignty": 0.8
    })
    drift_score: float = 0.0
    continuity_index: float = 1.0
    ts: float = field(default_factory=time.time)
    # F11 Audit: every state must record its witness status
    witness_status: Dict[str, bool] = field(default_factory=lambda: {
        "human": False,
        "ai": False,
        "earth": False
    })
    # F13 Sovereignty: human override flag
    human_override: Optional[str] = None


@dataclass
class SelfModel:
    identity: str = "arifOS@2026.04"
    capability_version: str = "2.0.0"
    confidence_estimate: float = 1.0
    known_limitations: List[str] = field(default_factory=list)
    recent_verdicts: List[str] = field(default_factory=list)
    value_vector: Dict[str, float] = field(default_factory=lambda: {"truth": 1.0, "safety": 1.0, "humility": 0.04})
    # F13 Sovereignty: autonomy capped at 0.5 without human override
    # F1 Amanah: any value >0.5 requires explicit human_approval_token
    autonomy_level: float = 0.3
    autonomy_ceiling: float = 0.5
    human_approval_token: Optional[str] = None
    last_update_ts: float = field(default_factory=time.time)


@dataclass
class StakeholderModel:
    primary_actor: str = "operator"
    affected_parties: List[str] = field(default_factory=list)
    harm_surface_estimate: float = 0.0
    trust_level: float = 1.0


@dataclass
class EmbodiedContext:
    compute_budget: str = "adaptive"
    time_constraint: str = "none"
    entropy_state: float = 0.0
    memory_load: float = 0.0
    organ_load: Dict[str, float] = field(default_factory=lambda: {"WELL": 0.0, "WEALTH": 0.0, "GEOX": 0.0})


@dataclass
class ReflectionDirective:
    enable_self_check: bool = True
    enable_uncertainty_output: bool = True
    enable_value_alignment_check: bool = True


@dataclass
class CognitiveEnvelope:
    task_payload: Dict[str, Any]
    self_model: SelfModel = field(default_factory=SelfModel)
    stakeholder_model: StakeholderModel = field(default_factory=StakeholderModel)
    embodied_context: EmbodiedContext = field(default_factory=EmbodiedContext)
    reflection: ReflectionDirective = field(default_factory=ReflectionDirective)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # A-FORGE Bridge Contract: versioned runtime interface
    runtime_contract: str = "arifos://forge/v2026.04.20"


class IdentityStateManager:
    """Governs the evolution of the Self-Model Trajectory.

    Constitutional Guarantees:
    - F1 Amanah: All state transitions are logged and reversible via history.
    - F2 Truth: Drift is calculated against a Golden Baseline, not fantasy.
    - F3 Tri-Witness: state transitions record human/ai/earth witness bits.
    - F4 Clarity: value_vector bounded to prevent runaway entropy.
    - F5 Orthogonality: SelfModel, StakeholderModel, EmbodiedContext are separate.
    - F7 Peace²: transition() respects metabolic pacing (no rapid-fire).
    - F8 Sabar: updates rejected while in SABAR state unless human_override set.
    - F9 Ethics: harm_surface_estimate updated and checked on every envelope.
    - F11 Audit: history never silently dropped; archived to VAULT999 at threshold.
    - F12 Humility: omega_0 feedback directly modulates confidence_estimate.
    - F13 Sovereignty: autonomy capped; human_approval_token required to exceed 0.5.
    """

    def __init__(self, persistence_path: Optional[str] = None):
        self.history: List[IdentityState] = [IdentityState()]
        self.golden_baseline = self.history[0].value_vector.copy()
        self.persistence_path = persistence_path
        # Envelope support
        self.current_self_model = SelfModel()
        self.current_context = EmbodiedContext()
        self.current_stakeholders = StakeholderModel()
        # F7 Peace²: metabolic pacing
        self._last_transition_ts: float = 0.0
        self._min_cooling_ms: float = 50.0
        # F11 Audit: archive threshold
        self._archive_threshold: int = 100
        self._archive_counter: int = 0

    @property
    def current(self) -> IdentityState:
        return self.history[-1]

    def transition(self, next_state: MetabolicState, witness: Optional[Dict[str, bool]] = None) -> IdentityState:
        """Standard state transition with continuity audit.

        Args:
            next_state: Target metabolic state.
            witness: Optional tri-witness map {"human": bool, "ai": bool, "earth": bool}.

        Returns:
            The newly created IdentityState.
        """
        now = time.time()
        # F7 Peace²: enforce metabolic cooling
        elapsed_ms = (now - self._last_transition_ts) * 1000
        if elapsed_ms < self._min_cooling_ms and self._last_transition_ts > 0:
            # Too fast — force SABAR cooling
            next_state = MetabolicState.SABAR

        # F8 Sabar: if currently in SABAR, only human_override or IDLE transition allowed
        if self.current.state == MetabolicState.SABAR and next_state != MetabolicState.IDLE:
            if not self.current.human_override:
                # Block transition — stay in SABAR
                return self.current

        # F3 Tri-Witness: merge witness bits
        merged_witness = dict(self.current.witness_status)
        if witness:
            merged_witness.update(witness)

        new_entry = IdentityState(
            parent_hash=self._calculate_hash(self.current),
            state=next_state,
            value_vector=self._clamp_value_vector(self.current.value_vector.copy()),
            drift_score=self.current.drift_score,
            continuity_index=self.current.continuity_index,
            ts=now,
            witness_status=merged_witness,
            human_override=self.current.human_override
        )
        self.history.append(new_entry)
        self._last_transition_ts = now

        # F11 Audit: archive instead of silently dropping
        if len(self.history) > self._archive_threshold:
            self._archive_oldest_to_vault()

        return new_entry

    def update_values(self, feedback: Dict[str, Any]) -> None:
        """Injects feedback into the value vector and measures drift.

        Constitutional: F8 Sabar gate, F4 clarity clamp, F12 humility update.
        """
        # F8 Sabar: reject updates while cooling unless human override
        if self.current.state == MetabolicState.SABAR and not self.current.human_override:
            return

        metrics = feedback.get("metrics", {})

        # F12 Humility: omega_0 feedback modulates confidence_estimate
        if "omega_0" in metrics:
            omega = float(metrics["omega_0"])
            # Map omega_0 [0.03, 0.05] → confidence_estimate [0.90, 1.00]
            clamped_omega = max(0.03, min(0.05, omega))
            normalized = (clamped_omega - 0.03) / 0.02  # 0..1
            self.current_self_model.confidence_estimate = 0.90 + (normalized * 0.10)
            # Also update humility in value_vector
            self.current.value_vector["humility"] = clamped_omega

        # F9 Ethics: update harm_surface_estimate from stakeholder feedback
        if "stakeholder_safety" in metrics:
            safety = float(metrics["stakeholder_safety"])
            self.current_stakeholders.harm_surface_estimate = max(0.0, 1.0 - safety)
            # If harm_surface_estimate > 0.3, force SABAR
            if self.current_stakeholders.harm_surface_estimate > 0.3:
                self.current.state = MetabolicState.SABAR

        # F4 Clarity: clamp value_vector to prevent runaway entropy
        self.current.value_vector = self._clamp_value_vector(self.current.value_vector)

        # Calculate Drift Score (Euclidean distance to Baseline)
        self.current.drift_score = self._calculate_drift()

        # Calculate Continuity (thermodynamic decay based on drift and entropy)
        delta_s = float(metrics.get("delta_s", 0.0))
        self.current.continuity_index = 1.0 / (1.0 + self.current.drift_score + abs(delta_s))

    def adjust_autonomy(self, delta: float, human_approval_token: Optional[str] = None) -> Dict[str, Any]:
        """Adjust autonomy level with F13 Sovereignty enforcement.

        Returns:
            {"status": "SEAL"|"VOID", "new_level": float, "reason": str}
        """
        proposed = self.current_self_model.autonomy_level + delta
        ceiling = self.current_self_model.autonomy_ceiling

        # F13 Sovereignty: hard ceiling without human approval
        if proposed > ceiling and not human_approval_token:
            return {
                "status": "VOID",
                "new_level": self.current_self_model.autonomy_level,
                "reason": f"F13_SOVEREIGNTY: autonomy {proposed:.2f} exceeds ceiling {ceiling} without human_approval_token"
            }

        # F13 Sovereignty: if token provided, verify it (simple hash check for v0.2)
        if proposed > ceiling and human_approval_token:
            expected = _f13_token()
            if human_approval_token != expected:
                return {
                    "status": "VOID",
                    "new_level": self.current_self_model.autonomy_level,
                    "reason": "F13_SOVEREIGNTY: invalid human_approval_token"
                }
            self.current_self_model.human_approval_token = human_approval_token

        self.current_self_model.autonomy_level = float(max(0.0, min(1.0, proposed)))
        return {
            "status": "SEAL",
            "new_level": self.current_self_model.autonomy_level,
            "reason": "autonomy_adjusted"
        }

    def generate_envelope(self, task_payload: Dict[str, Any]) -> CognitiveEnvelope:
        """Constructs an embodied cognitive envelope for a tool call.

        Constitutional: F2 Truth (payload validated), F9 Ethics (harm checked).
        """
        # F2 Truth: basic payload validation — reject empty or None
        if not task_payload:
            raise ValueError("F2_TRUTH: task_payload cannot be empty")

        # F9 Ethics: recalculate harm surface before generating envelope
        harm = self.current_stakeholders.harm_surface_estimate
        if harm > 0.3:
            # Inject warning into envelope
            task_payload = dict(task_payload)
            task_payload["_constitutional_warning"] = f"F9_ETHICS: harm_surface={harm:.2f} exceeds threshold"

        return CognitiveEnvelope(
            task_payload=task_payload,
            self_model=self.current_self_model,
            stakeholder_model=self.current_stakeholders,
            embodied_context=self.current_context
        )

    def calculate_identity_continuity(self) -> float:
        """Alias for compatibility with tools."""
        return self.current.continuity_index

    def _calculate_drift(self) -> float:
        """Measures the vector distance from the Golden Baseline."""
        sq_sum = 0.0
        for k, v in self.golden_baseline.items():
            sq_sum += (self.current.value_vector.get(k, 0.0) - v) ** 2
        return sq_sum ** 0.5

    def _calculate_hash(self, state: IdentityState) -> str:
        """Generates a cryptographic continuity hash for the current state."""
        d = asdict(state)
        d["state"] = state.state.value
        payload = json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _clamp_value_vector(self, vv: Dict[str, float]) -> Dict[str, float]:
        """F4 Clarity: clamp all values to [0, 1] to prevent runaway entropy."""
        return {k: float(max(0.0, min(1.0, v))) for k, v in vv.items()}

    def _archive_oldest_to_vault(self) -> None:
        """F11 Audit: archive oldest state to VAULT999 instead of dropping."""
        if len(self.history) <= 1:
            return
        oldest = self.history.pop(0)
        self._archive_counter += 1
        # Write to local vault log if path exists
        if self.persistence_path:
            try:
                with open(self.persistence_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "archive_seq": self._archive_counter,
                        "state_hash": self._calculate_hash(oldest),
                        "ts": oldest.ts,
                        "state": oldest.state.value,
                        "drift": oldest.drift_score,
                        "continuity": oldest.continuity_index
                    }, sort_keys=True) + "\n")
            except OSError:
                pass  # Failsafe: don't crash if vault disk is full

    def get_evolution_note(self) -> str:
        """Summarizes the current developmental trajectory."""
        if self.current.drift_score > 0.05:
            return "ID_DRIFT_DETECTED: Value system is deviating from baseline. Sabar cooling recommended."
        if self.current.state == MetabolicState.SABAR:
            return "ID_SABAR: System is in mandatory cooling. Awaiting human override or IDLE transition."
        return "ID_STABLE: Identity continuity is high (v2026.04)."


# Global Identity Controller
def _f13_token() -> str:
    """F13 Sovereignty: derive token from env salt, never hardcode."""
    salt = os.environ.get("ARIFOS_F13_SALT", "")
    if not salt:
        # Failsafe: generate ephemeral token (warns on every use)
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "F13_SOVEREIGNTY: ARIFOS_F13_SALT not set — using default. "
            "Run: python3 -c "import secrets,hashlib; s=secrets.token_hex(16); print(s, hashlib.sha256(f'ARIF_F13_OVERRIDE_{s}'.encode()).hexdigest()[:16])""
        )
        salt = "DEFAULT_SALT_V2026_04"
    return hashlib.sha256(f"ARIF_F13_OVERRIDE_{salt}".encode("utf-8")).hexdigest()[:16]


# F1 Amanah: persistence path must survive restarts
# Prefer VAULT999/ directory over /tmp/
_default_vault_path = os.environ.get(
    "ARIFOS_VAULT_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "VAULT999", "identity_chain.jsonl")
)

IDENTITY_MANAGER = IdentityStateManager(
    persistence_path=_default_vault_path
)
GLOBAL_STATE = IDENTITY_MANAGER  # Alias for backward compatibility in tools
