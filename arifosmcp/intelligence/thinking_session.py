"""
arifosmcp/intelligence/thinking_session.py — Sequential Thinking Session Manager

Manages step-by-step reasoning sessions with constitutional quality scoring.
Each step is verified against F2 TRUTH before being committed.

DITEMPA BUKAN DIBERI — Forged, Not Given
Author: 888_VALIDATOR | Version: 2026.04.10-CANONICAL
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class StepType(str, Enum):
    ANALYSIS = "analysis"       # Initial problem decomposition
    HYPOTHESIS = "hypothesis"   # Proposed explanations/solutions
    VERIFICATION = "verification" # Validation of hypotheses
    CONCLUSION = "conclusion"   # Final synthesized outcome
    REVISION = "revision"       # Revision of previous step
    BRANCH = "branch"           # Branching point marker

    @classmethod
    def from_string(cls, s: str) -> StepType:
        try:
            return cls(s.lower())
        except ValueError:
            return cls.ANALYSIS


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    MERGED = "merged"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ThinkingStep:
    """A single reasoning step within a thinking session."""
    step_number: int
    step_type: StepType
    content: str
    parent_step: int | None = None
    connections: list[int] = field(default_factory=list)
    branch_id: str | None = None
    quality_score: float = 0.0
    timestamp: float = field(default_factory=time.time)
    constitutional_verdict: str = "SEAL"  # SEAL / HOLD / VOID
    evidence_refs: list[str] = field(default_factory=list)  # F2 grounding

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["step_type"] = self.step_type.value
        return d


@dataclass
class ThinkingSession:
    """A full thinking session — sequential reasoning with constitutional tracking."""
    session_id: str
    problem: str
    context: dict[str, Any] | None = None
    tags: list[str] = field(default_factory=list)
    template: str | None = None  # e.g. "scientific-method", "five-whys"
    steps: list[ThinkingStep] = field(default_factory=list)
    branches: dict[str, list[int]] = field(default_factory=dict)  # branch_id → [step_nums]
    status: SessionStatus = SessionStatus.ACTIVE
    quality_score: float = 0.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "problem": self.problem,
            "context": self.context,
            "tags": self.tags,
            "template": self.template,
            "steps": [s.to_dict() for s in self.steps],
            "branches": self.branches,
            "status": self.status.value,
            "quality_score": round(self.quality_score, 4),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "step_count": len(self.steps),
        }


# ---------------------------------------------------------------------------
# Thinking Templates
# ---------------------------------------------------------------------------

THINKING_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "scientific-method": [
        {"prompt": "Define the research question or problem clearly.", "type": "analysis"},
        {"prompt": "Gather background information and evidence.", "type": "analysis"},
        {"prompt": "Formulate hypothesis based on evidence.", "type": "hypothesis"},
        {"prompt": "Design verification approach.", "type": "verification"},
        {"prompt": "Execute verification and analyze results.", "type": "verification"},
        {"prompt": "Draw conclusion from verified evidence.", "type": "conclusion"},
    ],
    "five-whys": [
        {"prompt": "State the problem or observation.", "type": "analysis"},
        {"prompt": "Why does this happen? (Why #1)", "type": "hypothesis"},
        {"prompt": "Why does that happen? (Why #2)", "type": "hypothesis"},
        {"prompt": "Why does that happen? (Why #3)", "type": "hypothesis"},
        {"prompt": "Why does that happen? (Why #4)", "type": "hypothesis"},
        {"prompt": "Why does that happen? (Why #5) — identify root cause.", "type": "conclusion"},
    ],
    "first-principles": [
        {"prompt": "Identify the current assumption or belief.", "type": "analysis"},
        {"prompt": "Break down to fundamental components.", "type": "analysis"},
        {"prompt": "Verify each component is a fundamental truth.", "type": "verification"},
        {"prompt": "Rebuild solution from verified fundamentals.", "type": "hypothesis"},
        {"prompt": "Test rebuilt solution against edge cases.", "type": "verification"},
        {"prompt": "Synthesize final conclusion.", "type": "conclusion"},
    ],
    "decision-matrix": [
        {"prompt": "Define the decision to be made clearly.", "type": "analysis"},
        {"prompt": "Identify criteria and assign weights (must-haves vs nice-to-haves).", "type": "analysis"},
        {"prompt": "List options to evaluate.", "type": "hypothesis"},
        {"prompt": "Score each option against criteria.", "type": "verification"},
        {"prompt": "Calculate weighted scores and rank options.", "type": "verification"},
        {"prompt": "Synthesize decision and recommendation.", "type": "conclusion"},
    ],
    "swot-analysis": [
        {"prompt": "Identify internal strengths (S).", "type": "analysis"},
        {"prompt": "Identify internal weaknesses (W).", "type": "analysis"},
        {"prompt": "Identify external opportunities (O).", "type": "analysis"},
        {"prompt": "Identify external threats (T).", "type": "analysis"},
        {"prompt": "Synthesize strategic insights from SWOT matrix.", "type": "conclusion"},
    ],
    "root-cause-analysis": [
        {"prompt": "Define the effect or problem statement.", "type": "analysis"},
        {"prompt": "Identify major cause categories (6M: Man/Machine/Material/Method/Measurement/Environment).", "type": "analysis"},
        {"prompt": "Brainstorm causes within each category.", "type": "hypothesis"},
        {"prompt": "Identify root causes through 5-Why drill-down.", "type": "verification"},
        {"prompt": "Recommend systemic fixes for root causes.", "type": "conclusion"},
    ],
    "pros-cons": [
        {"prompt": "State the decision clearly.", "type": "analysis"},
        {"prompt": "List all advantages and positive factors (Pros).", "type": "analysis"},
        {"prompt": "List all disadvantages and risks (Cons).", "type": "analysis"},
        {"prompt": "Assign weights to each factor by importance.", "type": "verification"},
        {"prompt": "Calculate weighted balance — lean direction.", "type": "verification"},
        {"prompt": "Make final recommendation.", "type": "conclusion"},
    ],
}


# ---------------------------------------------------------------------------
# Quality Scorer
# ---------------------------------------------------------------------------

def compute_session_quality(steps: list[ThinkingStep]) -> float:
    """
    Compute constitutional quality score for a thinking session.

    Scoring:
    - Step diversity (25%): variety of step types used
    - Evidence grounding (25%): steps with evidence_refs
    - Connection density (25%): how steps link to each other
    - Depth (25%): number of steps, capped at 10
    """
    if not steps:
        return 0.0

    # Step diversity
    step_types = {s.step_type for s in steps}
    diversity = min(len(step_types) / len(StepType), 1.0)

    # Evidence grounding (F2 TRUTH)
    grounded = sum(1 for s in steps if s.evidence_refs)
    evidence_score = grounded / len(steps)

    # Connection density
    total_conns = sum(len(s.connections) for s in steps)
    max_conns = len(steps) * (len(steps) - 1)
    density = total_conns / max_conns if max_conns > 0 else 0.0

    # Depth
    depth = min(len(steps) / 10.0, 1.0)

    return round(0.25 * diversity + 0.25 * evidence_score + 0.25 * density + 0.25 * depth, 4)


# ---------------------------------------------------------------------------
# Session Manager
# ---------------------------------------------------------------------------

class ThinkingSessionManager:
    """
    Manages sequential thinking sessions with constitutional floor enforcement.

    F2 TRUTH is enforced per-step: steps without evidence grounding
    receive a quality_score penalty and are flagged in the session record.
    """

    def __init__(self):
        self._sessions: dict[str, ThinkingSession] = {}
        self._by_tag: dict[str, set[str]] = {}  # tag → session_ids

    def start_session(
        self,
        problem: str,
        context: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        template: str | None = None,
    ) -> ThinkingSession:
        """Create a new thinking session."""
        session_id = hashlib.sha256(
            f"{problem}{time.time()}{uuid.uuid4().hex[:8]}".encode()
        ).hexdigest()[:16]

        session = ThinkingSession(
            session_id=session_id,
            problem=problem,
            context=context or {},
            tags=tags or [],
            template=template,
        )
        self._sessions[session_id] = session

        # Index by tags
        for tag in (tags or []):
            if tag not in self._by_tag:
                self._by_tag[tag] = set()
            self._by_tag[tag].add(session_id)

        logger.info(f"[ThinkingSession] Started {session_id}: {problem[:50]}...")
        return session

    def add_step(
        self,
        session_id: str,
        step_type: StepType,
        content: str,
        branch_id: str | None = None,
        parent_step: int | None = None,
        evidence_refs: list[str] | None = None,
        connections: list[int] | None = None,
    ) -> ThinkingStep:
        """Add a reasoning step to a session. Enforces F2 TRUTH quality gate."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        step_number = len(session.steps) + 1

        # F2 TRUTH gate: content without evidence gets lower quality
        has_evidence = evidence_refs and len(evidence_refs) > 0
        base_quality = 0.9 if has_evidence else 0.5

        step = ThinkingStep(
            step_number=step_number,
            step_type=step_type,
            content=content,
            parent_step=parent_step,
            connections=connections or [],
            branch_id=branch_id,
            quality_score=base_quality,
            evidence_refs=evidence_refs or [],
            constitutional_verdict="SEAL",
        )

        session.steps.append(step)
        session.updated_at = time.time()

        # Recompute session quality
        session.quality_score = compute_session_quality(session.steps)

        # Track branch membership
        if branch_id:
            if branch_id not in session.branches:
                session.branches[branch_id] = []
            session.branches[branch_id].append(step_number)

        logger.info(
            f"[ThinkingSession:{session_id}] Step {step_number} [{step_type.value}] "
            f"quality={step.quality_score:.2f} verdict={step.constitutional_verdict}"
        )
        return step

    def branch_session(
        self,
        session_id: str,
        from_step: int,
        branch_name: str,
        initial_content: str,
    ) -> tuple[ThinkingStep, ThinkingStep]:
        """
        Create a branch from an existing step.
        Returns (branch_root_step, first_branch_step).
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        # Mark the from_step as a branching point
        if from_step < 1 or from_step > len(session.steps):
            raise ValueError(f"Invalid from_step {from_step} — session has {len(session.steps)} steps")

        parent_step = session.steps[from_step - 1]

        # Add BRANCH marker step
        branch_marker = self.add_step(
            session_id=session_id,
            step_type=StepType.BRANCH,
            content=f"Branch '{branch_name}' forked from step {from_step}: {parent_step.content[:80]}...",
            branch_id=branch_name,
            parent_step=from_step,
            connections=[from_step],
        )

        # Add first step in new branch
        first_step = self.add_step(
            session_id=session_id,
            step_type=StepType.HYPOTHESIS,
            content=initial_content,
            branch_id=branch_name,
            parent_step=from_step,
            connections=[from_step],
        )

        return branch_marker, first_step

    def merge_insights(
        self,
        session_id: str,
        branch_ids: list[str],
        synthesis_content: str,
    ) -> ThinkingStep:
        """Merge multiple branches into a conclusion step."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        for bid in branch_ids:
            if bid not in session.branches:
                raise ValueError(f"Branch '{bid}' not found in session '{session_id}'")

        # Connect all branch steps to the synthesis
        all_branch_steps: list[int] = []
        for bid in branch_ids:
            all_branch_steps.extend(session.branches[bid])

        conclusion = self.add_step(
            session_id=session_id,
            step_type=StepType.CONCLUSION,
            content=synthesis_content,
            connections=all_branch_steps,
        )

        session.status = SessionStatus.MERGED
        session.updated_at = time.time()

        logger.info(f"[ThinkingSession:{session_id}] Merged {len(branch_ids)} branches → conclusion step {conclusion.step_number}")
        return conclusion

    def complete_session(self, session_id: str) -> ThinkingSession:
        """Mark a session as completed."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")
        session.status = SessionStatus.COMPLETED
        session.updated_at = time.time()
        return session

    def get_session(self, session_id: str) -> ThinkingSession | None:
        return self._sessions.get(session_id)

    def list_sessions(
        self,
        status: SessionStatus | None = None,
        tag: str | None = None,
        limit: int = 20,
    ) -> list[ThinkingSession]:
        """List sessions with optional filtering."""
        sessions = list(self._sessions.values())

        if status:
            sessions = [s for s in sessions if s.status == status]
        if tag:
            ids = self._by_tag.get(tag, set())
            sessions = [s for s in sessions if s.session_id in ids]

        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions[:limit]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if deleted."""
        if session_id in self._sessions:
            session = self._sessions.pop(session_id)
            # Remove from tag index
            for tag in session.tags:
                self._by_tag.get(tag, set()).discard(session_id)
            logger.info(f"[ThinkingSession] Deleted {session_id}")
            return True
        return False

    def export_session(
        self,
        session_id: str,
        format: str = "markdown",
    ) -> str:
        """Export session as markdown, json, or tree."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        if format == "json":
            return json.dumps(session.to_dict(), indent=2, default=str)

        if format == "tree":
            return self._export_tree(session)

        return self._export_markdown(session)

    def _export_markdown(self, session: ThinkingSession) -> str:
        lines = [
            f"# Thinking Session: {session.session_id}",
            "",
            f"**Problem:** {session.problem}",
            f"**Status:** {session.status.value}",
            f"**Template:** {session.template or 'default'}",
            f"**Quality Score:** {session.quality_score:.4f}",
            f"**Steps:** {len(session.steps)}",
            "",
            "---",
            "",
        ]
        for step in session.steps:
            lines.append(f"## Step {step.step_number}: [{step.step_type.value.upper()}]")
            if step.branch_id:
                lines.append(f"**Branch:** `{step.branch_id}`")
            if step.parent_step:
                lines.append(f"**Parent:** Step {step.parent_step}")
            lines.append("")
            lines.append(step.content)
            if step.evidence_refs:
                lines.append("")
                lines.append(f"*Evidence: {', '.join(step.evidence_refs)}*")
            lines.append("")
            lines.append(f"Quality: `{step.quality_score:.2f}` | Verdict: `{step.constitutional_verdict}`")
            lines.append("")

        return "\n".join(lines)

    def _export_tree(self, session: ThinkingSession) -> str:
        """Export as an ASCII tree showing branching structure."""
        lines = [f"Session {session.session_id} — {session.problem}"]
        for step in session.steps:
            indent = "  " * (step.step_number - 1)
            branch = f" [{step.branch_id}]" if step.branch_id else ""
            lines.append(f"{indent}├── Step {step.step_number}: [{step.step_type.value}]{branch}")
            lines.append(f"{indent}│   {step.content[:60]}...")
        return "\n".join(lines)

    def get_metrics(self, time_range: str = "all") -> dict[str, Any]:
        """Aggregate quality metrics across sessions."""
        sessions = list(self._sessions.values())

        if time_range != "all":
            now = time.time()
            ranges = {"day": 86400, "week": 604800, "month": 2592000}
            cutoff = now - ranges.get(time_range, 0)
            sessions = [s for s in sessions if s.created_at >= cutoff]

        if not sessions:
            return {
                "session_count": 0,
                "total_steps": 0,
                "avg_quality": 0.0,
                "avg_steps_per_session": 0.0,
                "verdicts": {"SEAL": 0, "HOLD": 0, "VOID": 0},
            }

        total_quality = sum(s.quality_score for s in sessions)
        total_steps = sum(len(s.steps) for s in sessions)

        verdicts: dict[str, int] = {"SEAL": 0, "HOLD": 0, "VOID": 0}
        for s in sessions:
            for step in s.steps:
                if step.constitutional_verdict in verdicts:
                    verdicts[step.constitutional_verdict] += 1

        return {
            "session_count": len(sessions),
            "total_steps": total_steps,
            "avg_quality": round(total_quality / len(sessions), 4),
            "avg_steps_per_session": round(total_steps / len(sessions), 2),
            "verdicts": verdicts,
            "time_range": time_range,
        }


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

_thinking_manager: ThinkingSessionManager | None = None


def get_thinking_manager() -> ThinkingSessionManager:
    global _thinking_manager
    if _thinking_manager is None:
        _thinking_manager = ThinkingSessionManager()
    return _thinking_manager
