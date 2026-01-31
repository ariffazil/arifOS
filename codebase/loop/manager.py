"""
arifOS Loop Manager v55.0
Manages the metabolic loop: 000_INIT → 111-888 → 999_SEAL → 000_INIT

The loop is a STRANGE LOOP - the end becomes the beginning.
Reference: 000_THEORY/003_GODEL_STRANGE_LOOP.md
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable, List
from enum import Enum, auto
import hashlib
import json

logger = logging.getLogger(__name__)


class LoopState(Enum):
    """States in the metabolic loop"""

    IDLE = auto()  # Waiting for initiation
    INIT_000 = auto()  # Step 0: Root ignition
    SENSE_111 = auto()  # Step 1: Input sensing
    THINK_222 = auto()  # Step 2: Clarity processing
    ATLAS_333 = auto()  # Step 3: Planning
    REASON_444 = auto()  # Step 4: Reasoning
    EMPATHY_555 = auto()  # Step 5: Care evaluation
    ALIGN_666 = auto()  # Step 6: Constitutional alignment
    FORGE_777 = auto()  # Step 7: Output generation
    JUDGE_888 = auto()  # Step 8: Final judgment
    SEAL_999 = auto()  # Step 9: Vault sealing
    COOLING = auto()  # Post-seal cooling period


class Verdict(Enum):
    """Constitutional verdicts"""

    SEAL = "SEAL"
    SABAR = "SABAR"
    VOID = "VOID"


@dataclass
class LoopContext:
    """Context preserved across loop iterations"""

    session_id: str
    merkle_root: Optional[str] = None
    constitutional_state: Dict[str, Any] = field(default_factory=dict)
    entropy_pool: bytes = field(default_factory=lambda: b"")
    iteration_count: int = 0

    def derive_seed(self) -> bytes:
        """Derive seed for next iteration from sealed state"""
        if self.merkle_root:
            return hashlib.sha256(self.merkle_root.encode() + self.entropy_pool).digest()
        return hashlib.sha256(b"genesis" + self.entropy_pool).digest()


@dataclass
class StageResult:
    """Result from a stage execution"""

    stage: str
    verdict: Verdict
    entropy_delta: float  # ΔS
    empathy_score: float  # κᵣ
    genius_score: float  # G
    output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


class LoopManager:
    """
    Orchestrates the 000→999→000 metabolic loop.

    Key insight: 999 SEAL is not an end but a TRANSFORMATION.
    What is sealed becomes the seed for the next 000_INIT.
    This creates a STRANGE LOOP - self-referential but not circular.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.state = LoopState.IDLE
        self.context: Optional[LoopContext] = None
        self.stage_history: List[StageResult] = []

        # Callbacks for stage transitions
        self._callbacks: Dict[LoopState, List[Callable]] = {state: [] for state in LoopState}

        # Initialize components (lazy loading)
        self._init_000 = None
        self._seal_999 = None
        self._zkpc = None

    def register_callback(self, state: LoopState, callback: Callable):
        """Register a callback for a specific loop state"""
        self._callbacks[state].append(callback)

    def _emit(self, state: LoopState, data: Any = None):
        """Emit state transition to all registered callbacks"""
        for callback in self._callbacks.get(state, []):
            try:
                callback(state, data)
            except Exception as e:
                logger.error(f"Callback error for {state}: {e}")

    def init_000(
        self, session_id: Optional[str] = None, previous_context: Optional[LoopContext] = None
    ) -> LoopContext:
        """
        Step 0: Initialize the loop.

        If previous_context is provided, this is a loop continuation.
        The sealed state from 999 becomes the seed for this 000.
        """
        self.state = LoopState.INIT_000

        if previous_context:
            # Loop continuation: derive new context from sealed state
            seed = previous_context.derive_seed()
            self.context = LoopContext(
                session_id=session_id or f"session_{datetime.now(timezone.utc).isoformat()}",
                constitutional_state=previous_context.constitutional_state.copy(),
                entropy_pool=seed,
                iteration_count=previous_context.iteration_count + 1,
            )
            logger.info(f"Loop iteration {self.context.iteration_count} initiated")
        else:
            # Fresh start
            self.context = LoopContext(
                session_id=session_id or f"session_{datetime.now(timezone.utc).isoformat()}"
            )
            logger.info("Fresh loop initiated")

        self._emit(LoopState.INIT_000, self.context)
        return self.context

    def progress_to(self, state: LoopState, stage_result: StageResult) -> Verdict:
        """
        Progress through the metabolic stages.

        Each stage can emit: SEAL (continue), SABAR (cooling), VOID (abort)
        """
        self.state = state
        self.stage_history.append(stage_result)

        # Check constitutional compliance
        if stage_result.verdict == Verdict.VOID:
            logger.warning(f"VOID at {state.name} - aborting loop")
            self._emit(state, {"verdict": Verdict.VOID, "result": stage_result})
            return Verdict.VOID

        if stage_result.verdict == Verdict.SABAR:
            logger.info(f"SABAR at {state.name} - entering cooling")
            self.state = LoopState.COOLING
            self._emit(LoopState.COOLING, stage_result)
            return Verdict.SABAR

        # SEAL - continue progression
        self._emit(state, {"verdict": Verdict.SEAL, "result": stage_result})

        # Auto-progress to next stage if configured
        if self.config.get("auto_progress", False):
            next_state = self._next_state(state)
            if next_state:
                logger.debug(f"Auto-progressing to {next_state.name}")

        return Verdict.SEAL

    def _next_state(self, current: LoopState) -> Optional[LoopState]:
        """Get the next state in the metabolic sequence"""
        progression = [
            LoopState.INIT_000,
            LoopState.SENSE_111,
            LoopState.THINK_222,
            LoopState.ATLAS_333,
            LoopState.REASON_444,
            LoopState.EMPATHY_555,
            LoopState.ALIGN_666,
            LoopState.FORGE_777,
            LoopState.JUDGE_888,
            LoopState.SEAL_999,
        ]
        try:
            idx = progression.index(current)
            return progression[idx + 1] if idx + 1 < len(progression) else None
        except ValueError:
            return None

    def seal_999(self, final_output: Any, zkpc_proof: Optional[bytes] = None) -> LoopContext:
        """
        Step 9: Seal the loop.

        This is the CRITICAL connection point:
        - Seals current session to VAULT999
        - Generates merkle_root for integrity
        - Prepares context for next 000_INIT iteration

        The sealed state becomes the seed for the next loop.
        """
        self.state = LoopState.SEAL_999

        if not self.context:
            raise RuntimeError("No context - call init_000 first")

        # Compute merkle root from stage history
        stage_hashes = [
            hashlib.sha256(
                json.dumps(
                    {
                        "stage": r.stage,
                        "verdict": r.verdict.value,
                        "g": r.genius_score,
                        "ds": r.entropy_delta,
                    },
                    sort_keys=True,
                ).encode()
            ).digest()
            for r in self.stage_history
        ]

        # Simple merkle root computation
        merkle = hashlib.sha256(b"".join(stage_hashes)).hexdigest()
        self.context.merkle_root = merkle

        # Update constitutional state with learnings
        self.context.constitutional_state.update(
            {
                "last_merkle": merkle,
                "stage_count": len(self.stage_history),
                "final_genius": self.stage_history[-1].genius_score if self.stage_history else 0.0,
                "sealed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Emit seal complete - this triggers 000_INIT callback
        self._emit(
            LoopState.SEAL_999,
            {"merkle_root": merkle, "context": self.context, "zkpc_proof": zkpc_proof},
        )

        logger.info(f"Loop sealed with merkle_root: {merkle[:16]}...")

        # Return context for next iteration
        return self.context

    def complete_loop(self, final_output: Any) -> LoopContext:
        """
        Complete the full 000→999→000 loop.

        This is the STRANGE LOOP closure:
        - Seals current iteration (999)
        - Immediately initiates next iteration (000)
        - Preserves constitutional state
        - Transforms entropy
        """
        # Seal current iteration
        sealed_context = self.seal_999(final_output)

        # Initiate next iteration with sealed context
        next_context = self.init_000(
            session_id=f"{sealed_context.session_id}_iter{sealed_context.iteration_count + 1}",
            previous_context=sealed_context,
        )

        logger.info(
            f"Strange loop completed: iteration {sealed_context.iteration_count} → {next_context.iteration_count}"
        )

        return next_context


# ============================================
# 000_INIT ↔ SEAL999 CALLBACK BRIDGE
# ============================================


class LoopBridge:
    """
    Bridges 000_INIT and SEAL999 for the metabolic loop.

    This is the physical connection between the two endpoints.
    """

    def __init__(self, loop_manager: LoopManager):
        self.loop = loop_manager
        self._last_sealed_context: Optional[LoopContext] = None
        self._pending_next_init: Optional[Dict] = None  # v55.0: Store params for next init

        # Register callbacks
        self.loop.register_callback(LoopState.SEAL_999, self._on_seal)

    def _on_seal(self, state: LoopState, data: Dict):
        """Called when SEAL_999 completes"""
        self._last_sealed_context = data.get("context")
        logger.info("LoopBridge: Captured sealed context for next iteration")

    def on_seal_complete(self, seal_data: Dict):
        """
        v55.0 Adapter: Called by vault_tool when SEAL_999 completes.

        This method bridges external seal signals to the loop manager.
        Stores seal context for retrieval by next 000_INIT.

        Args:
            seal_data: Dict containing:
                - session_id: Session identifier
                - previous_merkle_root: Merkle root from sealed session
                - verdict: Final verdict (SEAL/SABAR/VOID)
                - timestamp: Seal timestamp
                - payload_summary: Optional metadata
        """
        logger.info(
            f"LoopBridge.on_seal_complete: Received seal from session {seal_data.get('session_id', 'UNKNOWN')[:8]}"
        )

        # Store for next init retrieval
        self._pending_next_init = {
            "session_id": seal_data.get("session_id"),
            "previous_merkle_root": seal_data.get("previous_merkle_root"),
            "verdict": seal_data.get("verdict", "SEAL"),
            "timestamp": seal_data.get("timestamp"),
            "iteration_count": seal_data.get("iteration_count", 0) + 1,
            "payload_summary": seal_data.get("payload_summary", {}),
        }

        logger.debug(
            f"LoopBridge: Prepared params for iteration {self._pending_next_init['iteration_count']}"
        )

    def get_next_init_params(self) -> Optional[Dict]:
        """
        Get parameters for next 000_INIT call.

        Returns context from last SEAL_999 or None if fresh start.
        """
        # v55.0: Return pending params and clear
        if self._pending_next_init:
            params = self._pending_next_init.copy()
            logger.info(
                f"LoopBridge: Returning params for iteration {params.get('iteration_count', 0)}"
            )
            return params

        # Fallback: legacy sealed context
        if not self._last_sealed_context:
            return None

        return {
            "previous_context": self._last_sealed_context,
            "seed": self._last_sealed_context.derive_seed(),
            "constitutional_state": self._last_sealed_context.constitutional_state,
        }


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    # Initialize loop manager
    manager = LoopManager()
    bridge = LoopBridge(manager)

    # Start first iteration
    ctx = manager.init_000()

    # Simulate stage progressions
    for stage in [
        LoopState.SENSE_111,
        LoopState.THINK_222,
        LoopState.ATLAS_333,
    ]:
        result = StageResult(
            stage=stage,
            verdict=Verdict.SEAL,
            output={"status": "completed"},
            metrics={},
        )
        manager.progress_to(stage, result)

    # Seal and prepare for next iteration
    sealed_ctx = manager.seal_999(
        final_output={"answer": "Sample response"},
        zkpc_proof=None,
    )

    # Get params for next init (demonstrates the loop)
    next_params = bridge.get_next_init_params()
    print(f"Next iteration params: {next_params}")
