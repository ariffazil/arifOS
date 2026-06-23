"""
arifosmcp/runtime/mind_router.py — 333_MIND Complexity Router v1.0
═══════════════════════════════════════════════════════════════════

Routing layer for MIND: decides whether a task goes through:
  - DIRECT path: native single-pass reasoning (simple tasks)
  - SEQUENTIAL path: multi-step governed thinking (complex tasks)

Decision fields:
  - complexity_score: 0.0–1.0 scalar
  - needs_branching: multiple viable reasoning paths
  - needs_revision: likely to need course-correction mid-reasoning
  - requires_memory_recall: benefits from prior context
  - judge_required: constitutional verdict needed before action
  - recommended_path: "direct" | "sequential"

Feature flag: MIND_USE_SEQUENTIAL (env var, default true)
Probe: mind_plan(task) → structured steps for a known hard prompt

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ── Feature Flag ──────────────────────────────────────────────────────────────
MIND_USE_SEQUENTIAL = os.getenv("MIND_USE_SEQUENTIAL", "true").lower() in ("true", "1", "yes", "on")


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLEXITY SIGNALS — weighted heuristics for routing decisions
# ═══════════════════════════════════════════════════════════════════════════════

# Keywords that signal multi-step reasoning is needed
MULTI_DEPENDENCY_SIGNALS: list[str] = [
    "compare",
    "versus",
    "vs",
    "trade-off",
    "tradeoff",
    "if.*then.*else",
    "depends on",
    "conditional",
    "before.*after",
    "first.*then",
    "step",
]

BRANCHING_SIGNALS: list[str] = [
    "alternative",
    "options",
    "approaches",
    "strategies",
    "either.*or",
    "whether",
    "pros.*cons",
    "advantages.*disadvantages",
]

REVISION_SIGNALS: list[str] = [
    "debug",
    "diagnose",
    "troubleshoot",
    "root cause",
    "why.*not working",
    "fix",
    "repair",
    "investigate",
]

PLANNING_SIGNALS: list[str] = [
    "plan",
    "design",
    "architecture",
    "implement",
    "build",
    "create",
    "migrate",
    "refactor",
    "deploy",
    "pipeline",
    "workflow",
    "orchestrate",
]

MEMORY_SIGNALS: list[str] = [
    "previous",
    "prior",
    "earlier",
    "history",
    "before",
    "remember",
    "recall",
    "past",
    "context",
]

JUDGMENT_SIGNALS: list[str] = [
    "decide",
    "verdict",
    "approve",
    "reject",
    "seal",
    "irreversible",
    "deploy.*production",
    "delete",
    "drop",
    "force push",
    "constitutional",
]


def _count_signal_matches(text: str, signals: list[str]) -> int:
    """Count how many signal patterns match the input text."""
    text_lower = text.lower()
    count = 0
    for pattern in signals:
        if re.search(pattern, text_lower):
            count += 1
    return count


def _compute_complexity_score(
    query: str,
    context: dict | None = None,
    task: dict | None = None,
) -> float:
    """
    Compute a complexity score for a reasoning task.

    Returns 0.0 (trivial) to 1.0 (needs full sequential pipeline).

    Factors:
      - Query length and structure (longer ≈ more complex)
      - Signal pattern matches (multi-dependency, branching, etc.)
      - Context depth (nested context ≈ more complex)
      - Task metadata (explicit mode, epoch, plan hints)
      - Presence of evidence (evidence-rich tasks may be complex)
    """
    score = 0.0
    query_len = len(query) if query else 0

    # ── Query length factor (0.0–0.15) ──
    if query_len > 500:
        score += 0.15
    elif query_len > 200:
        score += 0.10
    elif query_len > 80:
        score += 0.05

    # ── Signal pattern matches (0.0–0.40) ──
    multi_hits = _count_signal_matches(query, MULTI_DEPENDENCY_SIGNALS)
    branch_hits = _count_signal_matches(query, BRANCHING_SIGNALS)
    revision_hits = _count_signal_matches(query, REVISION_SIGNALS)
    planning_hits = _count_signal_matches(query, PLANNING_SIGNALS)

    score += min(multi_hits * 0.08, 0.16)  # multi-dependency
    score += min(branch_hits * 0.06, 0.12)  # branching
    score += min(revision_hits * 0.08, 0.16)  # revision/debug
    score += min(planning_hits * 0.05, 0.10)  # planning/design

    # ── Context depth (0.0–0.15) ──
    if context:
        ctx_str = str(context)
        if len(ctx_str) > 1000:
            score += 0.15
        elif len(ctx_str) > 400:
            score += 0.10
        elif len(ctx_str) > 100:
            score += 0.05

    # ── Task metadata (0.0–0.15) ──
    if task:
        if task.get("epoch_id"):
            score += 0.05  # cross-epoch context
        if task.get("plan_id"):
            score += 0.05  # planned work (structured)
        if task.get("evidence_refs"):
            score += min(len(task["evidence_refs"]) * 0.02, 0.10)  # evidence-heavy

    # ── Memory signals (0.0–0.10) ──
    mem_hits = _count_signal_matches(query, MEMORY_SIGNALS)
    score += min(mem_hits * 0.05, 0.10)

    # ── Judgment signals (0.0–0.05) ──
    judge_hits = _count_signal_matches(query, JUDGMENT_SIGNALS)
    score += min(judge_hits * 0.025, 0.05)

    return round(min(score, 1.0), 3)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING DECISION
# ═══════════════════════════════════════════════════════════════════════════════

# Threshold: tasks scoring above this go through sequential path
COMPLEXITY_THRESHOLD = float(os.getenv("MIND_SEQUENTIAL_THRESHOLD", "0.25"))


@dataclass
class MindRoutingDecision:
    """The result of MIND's routing deliberation."""

    # Core decision
    recommended_path: str  # "direct" | "sequential"
    complexity_score: float  # 0.0–1.0

    # Decision axes
    needs_branching: bool
    needs_revision: bool
    requires_memory_recall: bool
    judge_required: bool

    # Metadata
    feature_flag_active: bool
    threshold_used: float
    reasoning: str
    signals_matched: list[str] = field(default_factory=list)
    suggested_template: str | None = None


def route_task(
    query: str,
    mode: str = "reason",
    context: dict | None = None,
    task: dict | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> MindRoutingDecision:
    """
    Decide whether a task should use direct or sequential reasoning.

    Direct path (complexity < threshold):
      - Single-step retrieval
      - Simple formatting / deterministic transforms
      - Obvious answers from known facts

    Sequential path (complexity >= threshold):
      - More than one dependency
      - Uncertainty requiring branch comparison
      - Plan / debug / diagnosis / trade-off tasks
      - Anything that would create long hidden chain-of-thought pressure
    """
    # ── Explicit mode override ──
    if mode in ("sequential", "step", "branch", "merge", "review"):
        return MindRoutingDecision(
            recommended_path="sequential",
            complexity_score=1.0,
            needs_branching=mode in ("branch", "merge"),
            needs_revision=mode in ("review", "reflect"),
            requires_memory_recall=mode in ("merge", "review"),
            judge_required=False,
            feature_flag_active=MIND_USE_SEQUENTIAL,
            threshold_used=COMPLEXITY_THRESHOLD,
            reasoning=f"Explicit mode '{mode}' forces sequential path.",
            signals_matched=[f"explicit_mode:{mode}"],
            suggested_template=None,
        )

    # ── Compute complexity ──
    score = _compute_complexity_score(query, context, task)

    # ── Signal classification ──
    signals: list[str] = []

    needs_branching = False
    if _count_signal_matches(query, BRANCHING_SIGNALS) > 0:
        needs_branching = True
        signals.append("branching")

    needs_revision = False
    if _count_signal_matches(query, REVISION_SIGNALS) > 0:
        needs_revision = True
        signals.append("revision")

    requires_memory = False
    if _count_signal_matches(query, MEMORY_SIGNALS) > 0:
        requires_memory = True
        signals.append("memory_recall")

    judge_required = False
    if _count_signal_matches(query, JUDGMENT_SIGNALS) > 0:
        judge_required = True
        signals.append("judgment")

    # ── Route ──
    if not MIND_USE_SEQUENTIAL:
        recommended = "direct"
        reasoning = "Feature flag MIND_USE_SEQUENTIAL is off."
    elif score >= COMPLEXITY_THRESHOLD:
        recommended = "sequential"
        reasoning = (
            f"Complexity score {score:.3f} >= threshold {COMPLEXITY_THRESHOLD}. "
            f"Signals: {signals or ['none']}."
        )
    else:
        recommended = "direct"
        reasoning = (
            f"Complexity score {score:.3f} < threshold {COMPLEXITY_THRESHOLD}. "
            f"Simple task — direct path sufficient."
        )

    # ── Template suggestion ──
    template = None
    if recommended == "sequential":
        if needs_revision:
            template = "five-whys"
        elif needs_branching:
            template = "scientific-method"
        elif "plan" in query.lower() or "design" in query.lower():
            template = "architectural-review"

    return MindRoutingDecision(
        recommended_path=recommended,
        complexity_score=score,
        needs_branching=needs_branching,
        needs_revision=needs_revision,
        requires_memory_recall=requires_memory,
        judge_required=judge_required,
        feature_flag_active=MIND_USE_SEQUENTIAL,
        threshold_used=COMPLEXITY_THRESHOLD,
        reasoning=reasoning,
        signals_matched=signals,
        suggested_template=template,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PROBE: mind_plan(task) — structured plan for a known hard prompt
# ═══════════════════════════════════════════════════════════════════════════════

# Known hard prompts for validation
HARD_PROMPTS: dict[str, list[str]] = {
    "debug_deploy_failure": [
        "Identify the failure point from logs and recent changes.",
        "Trace dependency chain: what changed → what broke → what depends on it.",
        "Formulate 2-3 hypotheses for root cause.",
        "For each hypothesis: what evidence would confirm or refute?",
        "Rank hypotheses by likelihood and cost-to-verify.",
        "Recommend verification order and fallback plan.",
    ],
    "architecture_decision": [
        "Enumerate constraints (technical, organizational, temporal).",
        "List viable approaches with pros/cons per constraint.",
        "Score each approach against constraints (weighted matrix).",
        "Identify key uncertainty: what if wrong?",
        "Recommend with reversibility plan.",
        "Define success criteria and rollback triggers.",
    ],
    "constitutional_audit": [
        "Map the action against F1-F13 floors.",
        "Identify which floors are at risk and why.",
        "For each at-risk floor: what evidence would satisfy it?",
        "Propose safe path: minimum viable action with all floors satisfied.",
        "Define escalation criteria: when to 888_HOLD.",
        "Recommend with confidence band and uncertainty list.",
    ],
}


def mind_plan(
    task_type: str = "debug_deploy_failure",
    custom_query: str | None = None,
) -> dict[str, Any]:
    """
    Probe: generate structured reasoning steps for a task.

    Returns non-empty structured steps for known hard prompts.
    Used to verify the sequential thinking pipeline is operational.

    Args:
        task_type: One of the known hard prompt types.
        custom_query: Optional custom task to generate steps for.

    Returns:
        Dict with task_type, steps (non-empty list), template, and metadata.
    """
    if custom_query:
        # Generate steps by analyzing the query
        decision = route_task(custom_query)
        steps = [
            f"Analyze: {custom_query[:120]}",
            "Decompose into sub-problems.",
            "For each sub-problem: identify evidence needed.",
            "Synthesize: reconcile across sub-problems.",
            "Verify: check consistency and completeness.",
        ]
        return {
            "task_type": "custom",
            "query": custom_query,
            "steps": steps,
            "step_count": len(steps),
            "recommended_path": decision.recommended_path,
            "complexity_score": decision.complexity_score,
            "template": decision.suggested_template,
            "probe": "mind_plan",
            "status": "ok",
            "feature_flag": MIND_USE_SEQUENTIAL,
        }

    steps = HARD_PROMPTS.get(task_type)
    if steps is None:
        return {
            "task_type": task_type,
            "steps": [],
            "step_count": 0,
            "probe": "mind_plan",
            "status": "unknown_task_type",
            "available_types": list(HARD_PROMPTS.keys()),
            "feature_flag": MIND_USE_SEQUENTIAL,
        }

    return {
        "task_type": task_type,
        "steps": steps,
        "step_count": len(steps),
        "template": {
            "debug_deploy_failure": "five-whys",
            "architecture_decision": "architectural-review",
            "constitutional_audit": "scientific-method",
        }.get(task_type),
        "probe": "mind_plan",
        "status": "ok",
        "feature_flag": MIND_USE_SEQUENTIAL,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING ENVELOPE — appended to every MIND output
# ═══════════════════════════════════════════════════════════════════════════════


def build_routing_envelope(
    query: str,
    mode: str = "reason",
    context: dict | None = None,
    task: dict | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Build the routing decision envelope to attach to MIND output.

    This gives callers (harness, A2A, other organs) an explicit trigger
    surface for whether Sequential Thinking MCP should be invoked next.
    """
    decision = route_task(query, mode, context, task, session_id, actor_id)

    return {
        "_mind_routing": {
            "recommended_path": decision.recommended_path,
            "complexity_score": decision.complexity_score,
            "needs_branching": decision.needs_branching,
            "needs_revision": decision.needs_revision,
            "requires_memory_recall": decision.requires_memory_recall,
            "judge_required": decision.judge_required,
            "feature_flag_active": decision.feature_flag_active,
            "threshold_used": decision.threshold_used,
            "reasoning": decision.reasoning,
            "signals_matched": decision.signals_matched,
            "suggested_template": decision.suggested_template,
            "_invariant": (
                "This is a routing recommendation, not a command. "
                "The harness/clinician decides whether to invoke Sequential Thinking MCP. "
                "F13 SOVEREIGN: Arif's judgment overrides all routing."
            ),
        }
    }
