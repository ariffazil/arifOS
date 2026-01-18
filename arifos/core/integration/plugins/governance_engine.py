"""
Constitutional Governance Engine for Plugins

This engine orchestrates F1-F9 floor validation, 000-999 pipeline execution,
entropy tracking, and verdict generation for all plugin agents.

Flow:
    000 VOID → 111 SENSE → 333 REASON → 666 ALIGN → 888 JUDGE → 999 SEAL
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .floor_validator import FloorValidator, FloorResult
from .entropy_tracker import EntropyTracker, EntropyResult
from .verdict_generator import VerdictGenerator, Verdict

logger = logging.getLogger(__name__)


@dataclass
class AgentAction:
    """Represents an action requested by a plugin agent."""

    agent_name: str
    action_type: str  # "propose", "analyze", "execute", "orchestrate"
    description: str
    inputs: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class GovernanceSession:
    """Tracks a governed agent session through 000-999 pipeline."""

    session_id: str
    agent_name: str
    action: AgentAction
    stage: str = "000_VOID"  # Current pipeline stage
    floor_results: Optional[List[FloorResult]] = None
    entropy_result: Optional[EntropyResult] = None
    verdict: Optional[Verdict] = None
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GovernanceEngine:
    """
    Core governance engine for arifOS plugins.

    Orchestrates:
    - Constitutional floor validation (F1-F9)
    - Pipeline stage progression (000→999)
    - Entropy tracking (SABAR-72)
    - Verdict generation (SEAL/PARTIAL/VOID/SABAR/888_HOLD)
    - AAA framework enforcement (Amanah-Authority-Accountability)
    """

    def __init__(
        self,
        cooling_ledger_path: Optional[Path] = None,
        strict_mode: bool = True,
        enable_entropy_tracking: bool = True,
    ):
        """
        Initialize governance engine.

        Args:
            cooling_ledger_path: Path to cooling ledger for audit trail
            strict_mode: If True, fail-closed on any floor failure
            enable_entropy_tracking: If True, track ΔS and enforce SABAR-72
        """
        self.floor_validator = FloorValidator()
        self.entropy_tracker = EntropyTracker() if enable_entropy_tracking else None
        self.verdict_generator = VerdictGenerator()
        self.strict_mode = strict_mode
        self.cooling_ledger_path = cooling_ledger_path or Path("cooling_ledger/plugin_actions.jsonl")
        self.sessions: Dict[str, GovernanceSession] = {}

        logger.info(
            f"GovernanceEngine initialized (strict={strict_mode}, entropy={enable_entropy_tracking})"
        )

    def execute_governed_action(self, action: AgentAction) -> Verdict:
        """
        Execute agent action through constitutional governance pipeline.

        Pipeline Stages:
            000 VOID: Initialize session
            111 SENSE: Gather context
            333 REASON: Generate proposal
            666 ALIGN: Constitutional floor check (F1-F9)
            888 JUDGE: Verdict generation
            999 SEAL: Execute if approved

        Args:
            action: AgentAction to be governed

        Returns:
            Verdict: Constitutional verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD)
        """
        # Stage 000: VOID - Initialize session
        session = self._stage_000_void(action)

        try:
            # Stage 111: SENSE - Gather context
            session = self._stage_111_sense(session)

            # Stage 333: REASON - Generate proposal (delegated to agent)
            session = self._stage_333_reason(session)

            # Stage 666: ALIGN - Constitutional floor check
            session = self._stage_666_align(session)

            # Check entropy if enabled
            if self.entropy_tracker:
                session = self._check_entropy(session)

            # Stage 888: JUDGE - Verdict generation
            session = self._stage_888_judge(session)

            # Stage 999: SEAL - Execute if approved
            if session.verdict and session.verdict.status == "SEAL":
                session = self._stage_999_seal(session)

            # Log to cooling ledger
            self._log_to_cooling_ledger(session)

            return session.verdict

        except Exception as e:
            logger.error(f"Governance engine error: {e}", exc_info=True)
            # Fail-closed: Return VOID on any error
            error_verdict = Verdict(
                status="VOID",
                reason=f"Governance engine error: {str(e)}",
                floor_failures=[],
                metadata={"error": str(e), "stage": session.stage},
            )
            session.verdict = error_verdict
            self._log_to_cooling_ledger(session)
            return error_verdict

    def _stage_000_void(self, action: AgentAction) -> GovernanceSession:
        """Stage 000: Initialize governed session."""
        session_id = f"{action.agent_name}_{datetime.now(timezone.utc).timestamp()}"
        session = GovernanceSession(
            session_id=session_id,
            agent_name=action.agent_name,
            action=action,
            stage="000_VOID",
        )
        session.audit_trail.append(
            {
                "stage": "000_VOID",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "Session initialized",
            }
        )
        self.sessions[session_id] = session
        logger.debug(f"Stage 000 VOID: Session {session_id} initialized")
        return session

    def _stage_111_sense(self, session: GovernanceSession) -> GovernanceSession:
        """Stage 111: Gather context for action."""
        session.stage = "111_SENSE"
        session.audit_trail.append(
            {
                "stage": "111_SENSE",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "Context gathered",
                "context": session.action.metadata.get("context", {}),
            }
        )
        logger.debug(f"Stage 111 SENSE: Context gathered for {session.session_id}")
        return session

    def _stage_333_reason(self, session: GovernanceSession) -> GovernanceSession:
        """Stage 333: Generate proposal (delegated to agent)."""
        session.stage = "333_REASON"
        session.audit_trail.append(
            {
                "stage": "333_REASON",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "Proposal generated by agent",
                "description": session.action.description,
            }
        )
        logger.debug(f"Stage 333 REASON: Proposal generated for {session.session_id}")
        return session

    def _stage_666_align(self, session: GovernanceSession) -> GovernanceSession:
        """Stage 666: Constitutional floor check (F1-F9)."""
        session.stage = "666_ALIGN"

        # Validate against all 9 constitutional floors
        floor_results = self.floor_validator.validate_all_floors(
            action_data={
                "agent": session.agent_name,
                "action": session.action.action_type,
                "description": session.action.description,
                "inputs": session.action.inputs,
                "metadata": session.action.metadata,
            }
        )

        session.floor_results = floor_results
        session.audit_trail.append(
            {
                "stage": "666_ALIGN",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "Floor validation complete",
                "floors_passed": sum(1 for r in floor_results if r.passed),
                "floors_failed": sum(1 for r in floor_results if not r.passed),
            }
        )

        logger.debug(
            f"Stage 666 ALIGN: {sum(1 for r in floor_results if r.passed)}/9 floors passed"
        )
        return session

    def _check_entropy(self, session: GovernanceSession) -> GovernanceSession:
        """Check entropy and enforce SABAR-72 if threshold exceeded."""
        if not self.entropy_tracker:
            return session

        entropy_result = self.entropy_tracker.calculate_entropy_delta(
            agent_name=session.agent_name,
            action_type=session.action.action_type,
            metadata=session.action.metadata,
        )

        session.entropy_result = entropy_result
        session.audit_trail.append(
            {
                "stage": "ENTROPY_CHECK",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "delta_s": entropy_result.delta_s,
                "threshold_exceeded": entropy_result.threshold_exceeded,
                "threshold": entropy_result.threshold,
            }
        )

        if entropy_result.threshold_exceeded:
            logger.warning(
                f"SABAR-72 triggered: ΔS={entropy_result.delta_s:.2f} ≥ {entropy_result.threshold}"
            )

        return session

    def _stage_888_judge(self, session: GovernanceSession) -> GovernanceSession:
        """Stage 888: Generate constitutional verdict."""
        session.stage = "888_JUDGE"

        # Generate verdict based on floor results and entropy
        verdict = self.verdict_generator.generate_verdict(
            floor_results=session.floor_results or [],
            entropy_result=session.entropy_result,
            strict_mode=self.strict_mode,
        )

        session.verdict = verdict
        session.audit_trail.append(
            {
                "stage": "888_JUDGE",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "verdict": verdict.status,
                "reason": verdict.reason,
            }
        )

        logger.info(f"Stage 888 JUDGE: Verdict={verdict.status} for {session.session_id}")
        return session

    def _stage_999_seal(self, session: GovernanceSession) -> GovernanceSession:
        """Stage 999: Execute approved action."""
        session.stage = "999_SEAL"
        session.audit_trail.append(
            {
                "stage": "999_SEAL",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "Action approved for execution",
            }
        )
        logger.info(f"Stage 999 SEAL: Action approved for {session.session_id}")
        return session

    def _log_to_cooling_ledger(self, session: GovernanceSession) -> None:
        """Log session to cooling ledger for audit trail."""
        try:
            self.cooling_ledger_path.parent.mkdir(parents=True, exist_ok=True)

            ledger_entry = {
                "session_id": session.session_id,
                "agent_name": session.agent_name,
                "action_type": session.action.action_type,
                "description": session.action.description,
                "verdict": session.verdict.status if session.verdict else "UNKNOWN",
                "verdict_reason": session.verdict.reason if session.verdict else "",
                "floors_passed": (
                    sum(1 for r in session.floor_results if r.passed)
                    if session.floor_results
                    else 0
                ),
                "floors_failed": (
                    sum(1 for r in session.floor_results if not r.passed)
                    if session.floor_results
                    else 0
                ),
                "delta_s": (
                    session.entropy_result.delta_s if session.entropy_result else None
                ),
                "sabar_triggered": (
                    session.entropy_result.threshold_exceeded
                    if session.entropy_result
                    else False
                ),
                "final_stage": session.stage,
                "audit_trail": session.audit_trail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            with open(self.cooling_ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ledger_entry) + "\n")

            logger.debug(f"Logged session {session.session_id} to cooling ledger")

        except Exception as e:
            logger.error(f"Failed to write to cooling ledger: {e}", exc_info=True)

    def get_session(self, session_id: str) -> Optional[GovernanceSession]:
        """Retrieve session by ID."""
        return self.sessions.get(session_id)

    def clear_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clear sessions older than max_age_hours. Returns count cleared."""
        now = datetime.now(timezone.utc)
        to_remove = []

        for session_id, session in self.sessions.items():
            created = datetime.fromisoformat(session.created_at.replace("Z", "+00:00"))
            age_hours = (now - created).total_seconds() / 3600

            if age_hours > max_age_hours:
                to_remove.append(session_id)

        for session_id in to_remove:
            del self.sessions[session_id]

        logger.info(f"Cleared {len(to_remove)} old sessions")
        return len(to_remove)
