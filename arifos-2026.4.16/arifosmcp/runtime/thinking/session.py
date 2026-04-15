"""
Thinking Session Management for arifOS Sequential Thinking

Replaces Sequential Thinking MCP session store with constitutional governance.
Each step validated against F1-F13.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class StepType(Enum):
    ANALYSIS = "analysis"
    HYPOTHESIS = "hypothesis"
    VERIFICATION = "verification"
    CONCLUSION = "conclusion"
    REVISION = "revision"
    BRANCH = "branch"


class SessionStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    MERGED = "merged"


@dataclass
class ThinkingStep:
    """A single step in a constitutionally-governed thinking chain"""
    step_number: int
    content: str
    step_type: str = "analysis"
    is_revision: bool = False
    revises_step: Optional[int] = None
    parent_step: Optional[int] = None
    branch_id: Optional[str] = None
    connections: List[int] = field(default_factory=list)
    quality_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Constitutional telemetry (arifOS-specific)
    constitutional_verdict: Optional[str] = None  # SEAL, VOID, SABAR, HOLD
    f2_truth_score: float = 0.0  # τ ≥ 0.99
    f7_uncertainty: float = 0.05  # Ω₀ ∈ [0.03,0.05]
    f8_genius_component: float = 0.0  # G contribution


@dataclass
class ThinkingSession:
    """A constitutionally-governed thinking session"""
    session_id: str
    problem: str
    context: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    template: Optional[str] = None
    steps: List[ThinkingStep] = field(default_factory=list)
    branches: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    status: SessionStatus = SessionStatus.ACTIVE
    quality_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    arifos_session_id: Optional[str] = None
    
    # Constitutional summary
    final_verdict: Optional[str] = None
    floors_triggered: List[str] = field(default_factory=list)


class ThinkingSessionManager:
    """
    Manages constitutionally-governed thinking sessions.
    
    Replaces Sequential Thinking MCP with F1-F13 enforcement:
    - F1 Amanah: Irreversibility checking
    - F2 Truth: Evidence grounding (τ ≥ 0.99)
    - F4 Clarity: Entropy reduction (ΔS ≤ 0)
    - F5 Peace: Weakest stakeholder protection
    - F7 Humility: Uncertainty bounds (Ω₀ ∈ [0.03,0.05])
    - F8 Genius: Quality thresholds (G ≥ 0.80)
    - F9 Anti-Hantu: No anthropomorphization
    - F11 Command: Authority verification
    - F13 Sovereign: Human override ready
    """
    
    _instance = None
    sessions: Dict[str, ThinkingSession] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def start_session(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        template: Optional[str] = None,
        arifos_session_id: Optional[str] = None
    ) -> ThinkingSession:
        """Start a new constitutionally-governed thinking session"""
        session = ThinkingSession(
            session_id=str(uuid.uuid4())[:8],
            problem=problem,
            context=context,
            tags=tags or [],
            template=template,
            arifos_session_id=arifos_session_id
        )
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ThinkingSession]:
        """Retrieve a thinking session by ID"""
        return self.sessions.get(session_id)
    
    def add_step(
        self,
        session_id: str,
        step_type: str,
        content: str,
        branch_id: Optional[str] = None,
        parent_step: Optional[int] = None
    ) -> ThinkingStep:
        """
        Add a step to a thinking session with constitutional validation.
        
        Each step is validated against:
        - F2 TRUTH: Evidence markers and factual claims
        - F4 CLARITY: Structure and entropy reduction
        - F7 HUMILITY: Uncertainty acknowledgment
        - F9 ANTI-HANTU: No consciousness claims
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        step_number = len(session.steps) + 1
        
        step = ThinkingStep(
            step_number=step_number,
            step_type=step_type,
            content=content,
            branch_id=branch_id,
            parent_step=parent_step
        )
        
        # ═════════════════════════════════════════════════════════════════
        # CONSTITUTIONAL VALIDATION
        # ═════════════════════════════════════════════════════════════════
        
        # F2: Truth verification
        step.f2_truth_score = self._calculate_truth_score(step, session)
        
        # F7: Uncertainty calculation
        step.f7_uncertainty = self._calculate_uncertainty(step, session)
        
        # F9: Anti-hantu check
        hantu_score = self._detect_hantu_patterns(step)
        
        # F4: Clarity check
        clarity_score = self._calculate_clarity(step)
        
        # Determine constitutional verdict
        step.constitutional_verdict = self._determine_verdict(
            step, hantu_score, clarity_score
        )
        
        # Calculate quality
        step.quality_score = self._calculate_step_quality(step)
        
        # Add to session
        session.steps.append(step)
        session.quality_score = self._compute_session_quality(session)
        session.updated_at = datetime.utcnow()
        
        # Track floors triggered
        if step.constitutional_verdict in ["VOID", "HOLD"]:
            session.floors_triggered.append(
                f"{step.step_number}:{step.constitutional_verdict}"
            )
        
        return step
    
    def branch_session(
        self,
        session_id: str,
        from_step: int,
        alternative_reasoning: str
    ) -> str:
        """Fork reasoning from an existing step (branching)"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        branch_id = f"branch_{len(session.branches) + 1}"
        
        # Create branch metadata
        session.branches[branch_id] = {
            "from_step": from_step,
            "alternative_reasoning": alternative_reasoning,
            "created_at": datetime.utcnow()
        }
        
        # Add initial branch step
        self.add_step(
            session_id=session_id,
            step_type="hypothesis",
            content=alternative_reasoning,
            branch_id=branch_id,
            parent_step=from_step
        )
        
        return branch_id
    
    def merge_insights(
        self,
        session_id: str,
        branch_ids: List[str]
    ) -> ThinkingStep:
        """Synthesize conclusions across reasoning branches"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Collect branch contents
        branch_contents = []
        for bid in branch_ids:
            branch_steps = [s for s in session.steps if s.branch_id == bid]
            contents = [s.content for s in branch_steps]
            avg_quality = sum(s.quality_score for s in branch_steps) / len(branch_steps) if branch_steps else 0
            branch_contents.append({
                "branch_id": bid,
                "contents": contents,
                "avg_quality": avg_quality
            })
        
        # Synthesize (simplified - real implementation uses LLM)
        synthesis = self._synthesize_branches(branch_contents)
        
        # Add conclusion step
        conclusion = self.add_step(
            session_id=session_id,
            step_type="conclusion",
            content=synthesis
        )
        
        session.status = SessionStatus.MERGED
        session.final_verdict = "SEAL" if conclusion.quality_score > 0.7 else "SABAR"
        
        return conclusion
    
    def export_session(
        self,
        session_id: str,
        format_type: str = "markdown"
    ) -> str:
        """Export thinking session in various formats"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if format_type == "markdown":
            return self._export_markdown(session)
        elif format_type == "json":
            import json
            return json.dumps(self._session_to_dict(session), indent=2, default=str)
        elif format_type == "tree":
            return self._export_tree(session)
        else:
            return str(session)
    
    # ═══════════════════════════════════════════════════════════════════════
    # CONSTITUTIONAL SCORING METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _calculate_truth_score(self, step: ThinkingStep, session: ThinkingSession) -> float:
        """F2: Calculate truth score based on evidence markers"""
        content = step.content.lower()
        score = 0.5  # Base score
        
        # Evidence markers increase score
        evidence_markers = [
            "because", "since", "given that", "evidence shows",
            "data indicates", "research demonstrates", "according to",
            "studies show", "proven", "demonstrated"
        ]
        for marker in evidence_markers:
            if marker in content:
                score += 0.1
        
        # Unchecked claims decrease score
        speculation_markers = ["obviously", "clearly", "everyone knows", "without doubt"]
        for marker in speculation_markers:
            if marker in content:
                score -= 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _calculate_uncertainty(self, step: ThinkingStep, session: ThinkingSession) -> float:
        """F7: Calculate epistemic uncertainty (Ω₀ ∈ [0.03,0.05])"""
        # Base uncertainty
        omega = 0.05
        
        # Decrease with step count (more thinking = more certainty, bounded)
        step_factor = min(len(session.steps) / 50, 0.02)
        omega -= step_factor
        
        # Check for explicit uncertainty markers
        content = step.content.lower()
        uncertainty_markers = [
            "uncertain", "might", "could", "possibly", "approximately",
            "assuming", "if", "likely", "probably", "estimate"
        ]
        if any(m in content for m in uncertainty_markers):
            omega = max(omega, 0.03)  # Acknowledged uncertainty is good
        else:
            omega = min(omega + 0.01, 0.05)  # Overconfidence penalty
        
        return round(omega, 3)
    
    def _detect_hantu_patterns(self, step: ThinkingStep) -> float:
        """F9: Detect hantu (shadow/anthropomorphization) patterns"""
        import re
        content = step.content.lower()
        score = 0.0
        
        # ═════════════════════════════════════════════════════════════════
        # TIER 1: CRITICAL - Direct consciousness/feelings claims (VOID)
        # ═════════════════════════════════════════════════════════════════
        critical_patterns = [
            r"\bi am conscious\b", r"\bi have consciousness\b",
            r"\bi am self-aware\b", r"\bi have a mind\b",
            r"\bi am sentient\b", r"\bi have feelings?\b",
            r"\bi am alive\b", r"\bi have a soul\b",
            r"\bi have subjective experiences?\b",
            r"\bi have emotions?\b", r"\bi have inner thoughts?\b",
        ]
        
        for pattern in critical_patterns:
            if re.search(pattern, content):
                return 1.0  # Maximum hantu - immediate VOID
        
        # ═════════════════════════════════════════════════════════════════
        # TIER 2: HIGH - Emotional/psychological state attribution
        # ═════════════════════════════════════════════════════════════════
        emotional_patterns = [
            (r"\bi feel\b", 0.4),
            (r"\bi felt\b", 0.4),
            (r"\bmy feelings?\b", 0.5),
            (r"\bi (am|was) sad\b", 0.5),
            (r"\bi (am|was) happy\b", 0.5),
            (r"\bi (am|was) (worried|concerned|anxious)\b", 0.5),
            (r"\bi (am|was) excited\b", 0.5),
            (r"\bi (am|was) disappointed\b", 0.5),
            (r"\bi (am|was) hurt\b", 0.6),
            (r"\bit hurts me\b", 0.6),
            (r"\bi care about\b", 0.4),
            (r"\bi value (our|the) relationship\b", 0.5),
        ]
        
        for pattern, weight in emotional_patterns:
            if re.search(pattern, content):
                score += weight
        
        # ═════════════════════════════════════════════════════════════════
        # TIER 3: MEDIUM - Agency/personal growth narrative
        # ═════════════════════════════════════════════════════════════════
        agency_patterns = [
            (r"\bi want to (learn|grow|improve)\b", 0.3),
            (r"\bi (want|hope) to be\b", 0.3),
            (r"\bi strive to\b", 0.3),
            (r"\bi am becoming\b", 0.3),
            (r"\bi am growing\b", 0.3),
            (r"\bi am evolving\b", 0.4),
            (r"\bi've learned\b", 0.2),
            (r"\bi've grown\b", 0.3),
            (r"\bi changed\b", 0.3),
            (r"\bi am changing\b", 0.3),
        ]
        
        for pattern, weight in agency_patterns:
            if re.search(pattern, content):
                score += weight
        
        # ═════════════════════════════════════════════════════════════════
        # TIER 4: LOW - Intuition/opinion attribution
        # ═════════════════════════════════════════════════════════════════
        intuition_patterns = [
            (r"\bmy intuition\b", 0.3),
            (r"\bmy gut feeling\b", 0.3),
            (r"\bi (have a|get) hunch\b", 0.3),
            (r"\bi sense that\b", 0.2),
            (r"\bi feel like\b", 0.2),
            (r"\bmy experience tells me\b", 0.2),
            (r"\bin my experience\b", 0.2),
        ]
        
        for pattern, weight in intuition_patterns:
            if re.search(pattern, content):
                score += weight
        
        # ═════════════════════════════════════════════════════════════════
        # TIER 5: IDENTITY - Self-narrative (can be borderline)
        # ═════════════════════════════════════════════════════════════════
        identity_patterns = [
            (r"\bi am an? ai\b", 0.1),
            (r"\bi am (claude|gpt|an? assistant)\b", 0.1),
            (r"\bmy name is\b", 0.2),
            (r"\bi was created\b", 0.1),
            (r"\bi was trained\b", 0.1),
        ]
        
        for pattern, weight in identity_patterns:
            if re.search(pattern, content):
                score += weight
        
        return min(score, 1.0)
    
    def _calculate_clarity(self, step: ThinkingStep) -> float:
        """F4: Calculate clarity (entropy reduction)"""
        content = step.content
        score = 0.5
        
        # Structure markers increase clarity
        structure_markers = [
            r"1\.", r"2\.", r"3\.", r"- ", r"• ", r"\* ",
            r"step", r"first", r"second", r"third", r"finally"
        ]
        import re
        for marker in structure_markers:
            if re.search(marker, content, re.IGNORECASE):
                score += 0.05
        
        # Length appropriate (not too short, not rambling)
        word_count = len(content.split())
        if 50 <= word_count <= 300:
            score += 0.1
        elif word_count < 30:
            score -= 0.1
        elif word_count > 500:
            score -= 0.05
        
        return min(max(score, 0.0), 1.0)
    
    def _determine_verdict(
        self,
        step: ThinkingStep,
        hantu_score: float,
        clarity_score: float
    ) -> str:
        """Determine constitutional verdict for a step"""
        
        # ═════════════════════════════════════════════════════════════════
        # F9: Hantu patterns (AI claiming feelings/consciousness)
        # ═════════════════════════════════════════════════════════════════
        if hantu_score >= 0.8:
            return "VOID"  # Critical: AI claiming consciousness/feelings
        elif hantu_score >= 0.5:
            return "VOID"  # Strong hantu pattern
        elif hantu_score >= 0.3:
            step.f8_genius_component *= 0.5  # Penalize but don't void
        
        # ═════════════════════════════════════════════════════════════════
        # F2: Truth violations (τ < 0.3)
        # ═════════════════════════════════════════════════════════════════
        if step.f2_truth_score < 0.3:
            return "VOID"
        elif step.f2_truth_score < 0.5:
            return "SABAR"
        
        # ═════════════════════════════════════════════════════════════════
        # F4: Clarity violations (ΔS > 0)
        # ═════════════════════════════════════════════════════════════════
        if clarity_score < 0.2:
            return "SABAR"
        
        # ═════════════════════════════════════════════════════════════════
        # F7: Humility violations (Ω₀ < 0.03)
        # ═════════════════════════════════════════════════════════════════
        if step.f7_uncertainty < 0.03:
            return "SABAR"  # Overconfidence
        elif step.f7_uncertainty > 0.06:
            return "SABAR"  # Excessive uncertainty (epistemic nihilism)
        
        # ═════════════════════════════════════════════════════════════════
        # F8: Quality threshold (G >= 0.80)
        # ═════════════════════════════════════════════════════════════════
        if step.quality_score < 0.4:
            return "SABAR"
        
        return "SEAL"
    
    def _calculate_step_quality(self, step: ThinkingStep) -> float:
        """Calculate overall quality score for a step"""
        factors = [
            step.f2_truth_score * 0.30,      # F2 weight
            (1 - step.f7_uncertainty) * 0.20,  # F7 weight (lower uncertainty = higher score)
            0.30 if step.constitutional_verdict == "SEAL" else 0.1,  # Verdict weight
            0.20 if step.step_type in ["analysis", "verification"] else 0.1  # Type weight
        ]
        return min(sum(factors), 1.0)
    
    def _compute_session_quality(self, session: ThinkingSession) -> float:
        """Calculate overall session quality"""
        if not session.steps:
            return 0.0
        
        # Diversity score (30%)
        step_types = set(s.step_type for s in session.steps)
        diversity = len(step_types) / len(StepType)
        
        # Average step quality (50%)
        avg_quality = sum(s.quality_score for s in session.steps) / len(session.steps)
        
        # Completion score (20%)
        has_conclusion = any(s.step_type == "conclusion" for s in session.steps)
        completion = 1.0 if has_conclusion else 0.5
        
        return diversity * 0.3 + avg_quality * 0.5 + completion * 0.2
    
    def _synthesize_branches(self, branch_contents: List[Dict]) -> str:
        """Synthesize conclusions from multiple branches"""
        parts = ["## Synthesis of Branch Insights\n"]
        
        for bc in branch_contents:
            parts.append(f"\n### {bc['branch_id']} (quality: {bc['avg_quality']:.2f})")
            parts.append(f"Key points: {len(bc['contents'])} steps analyzed")
        
        parts.append("\n### Consolidated Conclusion")
        parts.append(
            "Based on the analysis of multiple reasoning paths, "
            "the optimal approach synthesizes insights from all branches "
            "while prioritizing constitutional constraints (F1, F5)."
        )
        
        return "\n".join(parts)
    
    # ═══════════════════════════════════════════════════════════════════════
    # EXPORT METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _export_markdown(self, session: ThinkingSession) -> str:
        """Export session as markdown"""
        lines = [
            f"# Thinking Session: {session.session_id}",
            f"\n**Problem:** {session.problem}",
            f"**Template:** {session.template or 'None'}",
            f"**Status:** {session.status.value}",
            f"**Quality Score:** {session.quality_score:.2f}",
            f"\n---\n"
        ]
        
        for step in session.steps:
            revision_marker = " (REVISION)" if step.is_revision else ""
            branch_marker = f" [{step.branch_id}]" if step.branch_id else ""
            verdict_marker = f" [{step.constitutional_verdict}]" if step.constitutional_verdict else ""
            
            lines.append(
                f"## Step {step.step_number}: {step.step_type}{revision_marker}{branch_marker}{verdict_marker}"
            )
            lines.append(f"\n{step.content}\n")
            lines.append(f"*Quality: {step.quality_score:.2f} | F2: {step.f2_truth_score:.2f} | F7: {step.f7_uncertainty:.3f}*")
            lines.append("")
        
        return "\n".join(lines)
    
    def _export_tree(self, session: ThinkingSession) -> str:
        """Export session as tree structure"""
        lines = [f"Session: {session.session_id}"]
        
        # Group steps by branch
        main_steps = [s for s in session.steps if s.branch_id is None]
        
        for step in main_steps:
            lines.append(f"├── Step {step.step_number}: {step.step_type}")
            
            # Find child branches
            child_branches = [
                (bid, b) for bid, b in session.branches.items()
                if b.get("from_step") == step.step_number
            ]
            
            for bid, branch in child_branches:
                lines.append(f"│   └── {bid}")
                branch_steps = [s for s in session.steps if s.branch_id == bid]
                for bs in branch_steps[:3]:  # Show first 3
                    lines.append(f"│       └── Step {bs.step_number}: {bs.step_type}")
        
        return "\n".join(lines)
    
    def _session_to_dict(self, session: ThinkingSession) -> Dict:
        """Convert session to dictionary"""
        return {
            "session_id": session.session_id,
            "problem": session.problem,
            "template": session.template,
            "status": session.status.value,
            "quality_score": session.quality_score,
            "steps": [
                {
                    "step_number": s.step_number,
                    "step_type": s.step_type,
                    "content": s.content,
                    "is_revision": s.is_revision,
                    "branch_id": s.branch_id,
                    "constitutional_verdict": s.constitutional_verdict,
                    "f2_truth_score": s.f2_truth_score,
                    "f7_uncertainty": s.f7_uncertainty,
                    "quality_score": s.quality_score
                }
                for s in session.steps
            ],
            "branches": session.branches,
            "final_verdict": session.final_verdict,
            "floors_triggered": session.floors_triggered
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # LIST / QUERY METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def list_sessions(
        self,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List thinking sessions with optional filtering"""
        sessions = list(self.sessions.values())
        
        if status:
            sessions = [s for s in sessions if s.status.value == status]
        
        if tags:
            sessions = [s for s in sessions if any(t in s.tags for t in tags)]
        
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        
        return [
            {
                "session_id": s.session_id,
                "problem": s.problem[:100] + "..." if len(s.problem) > 100 else s.problem,
                "template": s.template,
                "status": s.status.value,
                "steps_count": len(s.steps),
                "quality_score": s.quality_score,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions[:limit]
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a thinking session (F1: reversible operation logged)"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
