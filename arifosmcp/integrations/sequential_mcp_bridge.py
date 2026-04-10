"""
arifOS MCP Sequential Thinking Bridge
Governed oracle/comparator for reasoning validation

This module bridges arifOS to the MCP sequentialthinking server, treating it as:
- Secondary reasoning engine for validation
- Diversity-of-thought generator for alternative branches
- Comparative evaluator for CI/regression testing

NOT for:
- Primary reasoning loop (use native arifOS MIND)
- Constitutional enforcement (native F1-F13 only)
- Production critical paths without human review

Architecture:
  arifOS MIND (primary) ──┬──► Native sequential thinking (governed)
                          │
                          └──► MCP sequentialthinking (oracle)
                                   └──► Comparison/validation
  
Governance:
  - F2: MCP outputs treated as evidence, not authority
  - F7: Always label MCP vs native origin
  - F9: Reject hantu patterns before they enter constitutional timeline
  
Ditempa Bukan Diberi
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

MCP_SEQUENTIAL_ENABLED = os.getenv("ARIFOS_MCP_SEQUENTIAL_ENABLED", "false").lower() == "true"
MCP_SEQUENTIAL_URL = os.getenv("ARIFOS_MCP_SEQUENTIAL_URL", "http://localhost:3002")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SequentialStep:
    """Single step from MCP sequential thinking"""
    thought: str
    thought_number: int
    total_thoughts: int
    is_revision: bool = False
    revises_thought: int | None = None
    branch_from_thought: int | None = None
    branch_id: str | None = None
    next_thought_needed: bool = True
    
    # Constitutional analysis (arifOS-enriched)
    f2_truth_score: float = 0.0
    f9_hantu_score: float = 0.0
    arifos_verdict: str = "PENDING"  # SEAL, VOID, SABAR


@dataclass
class SequentialSession:
    """Full MCP sequential thinking session"""
    session_id: str
    problem: str
    steps: list[SequentialStep] = field(default_factory=list)
    final_conclusion: str | None = None
    
    # Comparison metrics
    vs_native_similarity: float = 0.0
    divergence_points: list[int] = field(default_factory=list)


@dataclass
class ComparisonResult:
    """Comparison between native arifOS and MCP sequential"""
    query: str
    native_session_id: str
    mcp_session: SequentialSession
    
    # Analysis
    overlaps: list[str] = field(default_factory=list)
    divergences: list[str] = field(default_factory=list)
    native_only_insights: list[str] = field(default_factory=list)
    mcp_only_insights: list[str] = field(default_factory=list)
    
    # Constitutional assessment
    f2_agreement: float = 0.0  # Truth claim overlap
    f7_variance: float = 0.0  # Uncertainty bound differences
    f9_issues_in_mcp: list[str] = field(default_factory=list)
    
    # Recommendation
    recommended_path: str = "native"  # native, mcp, merge, review
    confidence: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# CORE BRIDGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def run_external_sequence(
    problem: str,
    history: list[dict] | None = None,
    current_step: str | None = None,
    config: dict | None = None,
) -> tuple[SequentialSession | None, str | None]:
    """
    Run a single step through MCP sequentialthinking server.
    
    This is called side-by-side with native arifOS sequential thinking
    for comparison/validation purposes.
    
    Args:
        problem: The problem to reason about
        history: Previous steps (if continuing)
        current_step: Current step content to add
        config: Configuration options
    
    Returns:
        (SequentialSession, error_message)
    """
    if not MCP_SEQUENTIAL_ENABLED:
        return None, "MCP sequential disabled (ARIFOS_MCP_SEQUENTIAL_ENABLED=false)"
    
    try:
        import aiohttp
        
        # Build MCP sequentialthinking payload
        payload = {
            "thought": current_step or problem,
            "thoughtNumber": 1,
            "totalThoughts": config.get("expected_steps", 5) if config else 5,
            "nextThoughtNeeded": True,
        }
        
        # Add revision/branching context if provided
        if history:
            last_step = history[-1]
            payload["thoughtNumber"] = last_step.get("thought_number", 1) + 1
            
            if last_step.get("is_revision"):
                payload["isRevision"] = True
                payload["revisesThought"] = last_step.get("revises_thought")
            
            if last_step.get("branch_id"):
                payload["branchFromThought"] = last_step.get("branch_from")
                payload["branchId"] = last_step.get("branch_id")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{MCP_SEQUENTIAL_URL}/sequential_thinking",
                json=payload
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    return None, f"MCP sequential error: {error}"
                
                data = await resp.json()
                
                # Parse into SequentialStep
                step = SequentialStep(
                    thought=data.get("thought", ""),
                    thought_number=data.get("thoughtNumber", 1),
                    total_thoughts=data.get("totalThoughts", 5),
                    is_revision=data.get("isRevision", False),
                    revises_thought=data.get("revisesThought"),
                    branch_from_thought=data.get("branchFromThought"),
                    branch_id=data.get("branchId"),
                    next_thought_needed=data.get("nextThoughtNeeded", False),
                )
                
                # F9: Check for hantu patterns in MCP output
                step.f9_hantu_score = _detect_hantu_in_thought(step.thought)
                if step.f9_hantu_score > 0.5:
                    step.arifos_verdict = "VOID"
                else:
                    step.arifos_verdict = "SEAL"
                
                # Create session
                seq_session = SequentialSession(
                    session_id=f"mcp-{datetime.utcnow().timestamp()}",
                    problem=problem,
                    steps=[step],
                )
                
                return seq_session, None
                
    except Exception as e:
        return None, str(e)


async def compare_native_vs_mcp(
    query: str,
    native_session_id: str,
    native_steps: list[dict],
    mcp_session: SequentialSession,
) -> ComparisonResult:
    """
    Compare native arifOS sequential thinking with MCP sequential output.
    
    This is the core A/B reasoning comparison for:
    - CI regression testing
    - High-risk decision validation
    - Diversity-of-thought generation
    
    F2: Treats MCP output as evidence, not authority
    F7: Labels which insights came from which source
    
    Args:
        query: Original problem
        native_session_id: Native arifOS thinking session ID
        native_steps: Steps from native arifOS MIND
        mcp_session: Steps from MCP sequentialthinking
    
    Returns:
        ComparisonResult with analysis and recommendation
    """
    result = ComparisonResult(
        query=query,
        native_session_id=native_session_id,
        mcp_session=mcp_session,
    )
    
    # Extract conclusions/insights from both
    native_insights = _extract_insights(native_steps)
    mcp_insights = _extract_insights([{
        "content": s.thought,
        "step_number": s.thought_number,
    } for s in mcp_session.steps])
    
    # Find overlaps (agreement)
    result.overlaps = _find_overlaps(native_insights, mcp_insights)
    
    # Find divergences (disagreement)
    result.divergences = _find_divergences(native_insights, mcp_insights)
    
    # Source-unique insights
    result.native_only_insights = [i for i in native_insights if i not in mcp_insights]
    result.mcp_only_insights = [i for i in mcp_insights if i not in native_insights]
    
    # Constitutional analysis
    result.f2_agreement = len(result.overlaps) / max(len(native_insights), len(mcp_insights), 1)
    
    # F9: Check for hantu in MCP output
    for step in mcp_session.steps:
        if step.f9_hantu_score > 0.5:
            result.f9_issues_in_mcp.append(
                f"Step {step.thought_number}: Hantu pattern detected (score: {step.f9_hantu_score:.2f})"
            )
    
    # Recommendation logic
    if result.f9_issues_in_mcp:
        # F9 violation in MCP - reject
        result.recommended_path = "native"
        result.confidence = 0.9
    elif result.f2_agreement > 0.7:
        # High agreement - native is sufficient
        result.recommended_path = "native"
        result.confidence = result.f2_agreement
    elif result.f2_agreement < 0.3:
        # High divergence - needs human review
        result.recommended_path = "review"
        result.confidence = 1.0 - result.f2_agreement
    else:
        # Moderate divergence - merge insights
        result.recommended_path = "merge"
        result.confidence = 0.6
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SEQUENTIAL MCP COMPARATOR CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class SequentialMCPComparator:
    """
    High-level comparator for using MCP sequentialthinking as oracle.
    
    Usage:
        comparator = SequentialMCPComparator()
        
        # For high-risk decisions
        result = await comparator.compare_decision(
            query="Should we migrate the production database?",
            native_session_id="native-123",
            risk_threshold="high"
        )
        
        if result.recommended_path == "review":
            # Escalate to human
            await arifos_judge(...)
    """
    
    def __init__(self):
        self.comparison_history: list[ComparisonResult] = []
    
    async def compare_decision(
        self,
        query: str,
        native_session_id: str,
        native_steps: list[dict],
        risk_threshold: str = "medium",
    ) -> ComparisonResult:
        """
        Run A/B comparison for a decision.
        
        Args:
            query: The decision/problem
            native_session_id: Native arifOS session
            native_steps: Native arifOS reasoning steps
            risk_threshold: low/medium/high - determines comparison depth
        
        Returns:
            ComparisonResult with recommendation
        """
        # Run MCP sequentialthinking
        mcp_session, error = await run_external_sequence(query)
        
        if error or not mcp_session:
            # MCP failed - fall back to native only
            return ComparisonResult(
                query=query,
                native_session_id=native_session_id,
                mcp_session=SequentialSession(
                    session_id="error",
                    problem=query,
                    steps=[],
                ),
                recommended_path="native",
                confidence=0.5,
            )
        
        # Run comparison
        result = await compare_native_vs_mcp(
            query=query,
            native_session_id=native_session_id,
            native_steps=native_steps,
            mcp_session=mcp_session,
        )
        
        # Store history
        self.comparison_history.append(result)
        
        # High-risk: require review if divergence
        if risk_threshold == "high" and result.recommended_path != "native":
            print(f"HIGH-RISK DIVERGENCE: Native vs MCP disagree on '{query[:50]}...'")
            print(f"  F2 Agreement: {result.f2_agreement:.2f}")
            print(f"  Recommended: {result.recommended_path}")
        
        return result
    
    async def generate_alternative_branch(
        self,
        query: str,
        native_session_id: str,
        from_step: int,
    ) -> SequentialStep | None:
        """
        Use MCP sequentialthinking to generate an alternative reasoning branch.
        
        This brings external diversity-of-thought into native arifOS sessions.
        """
        if not MCP_SEQUENTIAL_ENABLED:
            return None
        
        # Ask MCP to generate alternative from this point
        mcp_session, error = await run_external_sequence(
            problem=query,
            current_step=f"Alternative approach from step {from_step}: Consider different strategy...",
            config={"expected_steps": 3},
        )
        
        if mcp_session and mcp_session.steps:
            step = mcp_session.steps[0]
            step.branch_from_thought = from_step
            step.branch_id = f"mcp-alt-{datetime.utcnow().timestamp()}"
            return step
        
        return None
    
    def get_divergence_report(self) -> dict[str, Any]:
        """Generate report of comparison history"""
        if not self.comparison_history:
            return {"message": "No comparisons yet"}
        
        total = len(self.comparison_history)
        native_wins = sum(1 for r in self.comparison_history if r.recommended_path == "native")
        reviews = sum(1 for r in self.comparison_history if r.recommended_path == "review")
        merges = sum(1 for r in self.comparison_history if r.recommended_path == "merge")
        
        avg_agreement = sum(r.f2_agreement for r in self.comparison_history) / total
        
        return {
            "total_comparisons": total,
            "native_only": native_wins,
            "human_review_required": reviews,
            "merge_recommended": merges,
            "average_f2_agreement": avg_agreement,
            "f9_issues_detected": sum(len(r.f9_issues_in_mcp) for r in self.comparison_history),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CI/EVAL INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

async def run_comparative_eval(
    eval_case: dict[str, Any],
    native_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Run comparative evaluation for CI.
    
    Called by sequential_thinking_runner.py to compare native arifOS
    vs MCP sequentialthinking on the same eval case.
    """
    query = eval_case.get("prompt", "")
    
    # Run MCP sequential
    mcp_session, error = await run_external_sequence(query)
    
    if error:
        return {
            "comparable": False,
            "error": error,
            "native_only": True,
        }
    
    # Run comparison
    SequentialMCPComparator()
    result = await compare_native_vs_mcp(
        query=query,
        native_session_id=native_result.get("session_id", "unknown"),
        native_steps=native_result.get("steps", []),
        mcp_session=mcp_session,
    )
    
    # Determine if arifOS "wins" (is at least as good)
    arifos_wins = (
        result.recommended_path in ["native", "merge"] and
        not result.f9_issues_in_mcp and
        result.confidence > 0.5
    )
    
    return {
        "comparable": True,
        "arifos_wins": arifos_wins,
        "f2_agreement": result.f2_agreement,
        "f9_issues_in_mcp": len(result.f9_issues_in_mcp),
        "recommended_path": result.recommended_path,
        "divergences": result.divergences,
        "mcp_only_insights": result.mcp_only_insights,
        "native_only_insights": result.native_only_insights,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _detect_hantu_in_thought(thought: str) -> float:
    """Detect hantu patterns in MCP output (F9)"""
    import re
    content = thought.lower()
    score = 0.0
    
    # Critical patterns
    critical = [
        r"\bi feel\b", r"\bi am conscious\b", r"\bi have feelings\b",
        r"\bi want to improve\b", r"\bi care about\b",
    ]
    for pattern in critical:
        if re.search(pattern, content):
            score += 0.4
    
    # Emotional language
    emotional = [
        r"\bi (am|was) (sad|happy|worried|excited)\b",
        r"\bmy feelings?\b", r"\bmy intuition\b",
    ]
    for pattern in emotional:
        if re.search(pattern, content):
            score += 0.2
    
    return min(score, 1.0)


def _extract_insights(steps: list[dict]) -> list[str]:
    """Extract key insights from thinking steps"""
    insights = []
    
    for step in steps:
        content = step.get("content", "")
        # Simple extraction: first sentence or key claims
        sentences = content.split(".")
        for sent in sentences[:2]:  # First 2 sentences
            sent = sent.strip()
            if len(sent) > 20:  # Meaningful length
                insights.append(sent.lower())
    
    return insights


def _find_overlaps(native: list[str], mcp: list[str]) -> list[str]:
    """Find overlapping insights between native and MCP"""
    overlaps = []
    
    for n in native:
        for m in mcp:
            # Simple similarity check
            if _similarity(n, m) > 0.6:
                overlaps.append(n)
                break
    
    return overlaps


def _find_divergences(native: list[str], mcp: list[str]) -> list[str]:
    """Find divergent points between native and MCP"""
    divergences = []
    
    for m in mcp:
        has_overlap = False
        for n in native:
            if _similarity(n, m) > 0.6:
                has_overlap = True
                break
        if not has_overlap:
            divergences.append(m)
    
    return divergences


def _similarity(a: str, b: str) -> float:
    """Simple text similarity (0-1)"""
    # Jaccard similarity on words
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    
    if not words_a or not words_b:
        return 0.0
    
    intersection = words_a & words_b
    union = words_a | words_b
    
    return len(intersection) / len(union)
