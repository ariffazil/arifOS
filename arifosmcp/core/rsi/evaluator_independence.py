"""
RSI Constitutional Kernel — Evaluator Independence Test
═══════════════════════════════════════════════════════════════════════════════

Before /555 (adversarial verification) runs, the kernel requires proof
that the evaluator differs from the proposer in at least one meaningful dimension.

This prevents "syndicate improvement" — two agents from the same family
confirming each other's work.

Ratified: 2026-09-15
Authority: F13 SOVEREIGN

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# INDEPENDENCE DIMENSIONS
# ═══════════════════════════════════════════════════════════════════════════════

class IndependenceDimension(StrEnum):
    """At least ONE of these must differ between proposer and verifier."""
    DIFFERENT_MODEL = "different_model"         # Different LLM family
    DIFFERENT_CONTEXT = "different_context"      # Different prompt/context window
    DIFFERENT_IDENTITY = "different_identity"    # Different agent ID
    DIFFERENT_CORPUS = "different_corpus"        # Different retrieval corpus
    DIFFERENT_HUMAN = "different_human"          # Different human reviewer


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentProfile:
    """Profile of an agent for independence comparison."""
    agent_id: str
    model_family: str          # e.g., "qwen", "kimi", "gpt-4", "claude"
    context_window: str        # e.g., "standard", "extended", "custom"
    identity: str              # agent ID or role name
    retrieval_corpus: str      # e.g., "aaa-default", "forge-specific", "web"
    human_reviewer: str | None # human who reviews this agent's work


@dataclass
class IndependenceCheck:
    """Result of an independence check."""
    is_independent: bool
    dimensions_differ: list[IndependenceDimension]
    dimensions_same: list[IndependenceDimension]
    reason: str
    minimum_required: int = 1


# ═══════════════════════════════════════════════════════════════════════════════
# EVALUATOR INDEPENDENCE GATE
# ═══════════════════════════════════════════════════════════════════════════════

class EvaluatorIndependenceGate:
    """
    Before /555 adversarial verification, this gate checks that the
    evaluator (verifier) is meaningfully independent from the proposer.
    
    Syndicate improvement: two agents from the same family confirming
    each other's work → false confidence.
    
    Independence = at least one meaningful dimension differs.
    """

    # Model families that are too similar to count as independent
    # (same provider, minor variant)
    SIMILAR_FAMILIES: dict[str, set[str]] = {
        "qwen": {"qwen", "qwen-turbo", "qwen-plus", "qwen-max"},
        "kimi": {"kimi", "kimi-light"},
        "gpt": {"gpt-4", "gpt-4o", "gpt-4-turbo", "gpt-4o-mini"},
        "claude": {"claude-3", "claude-3.5", "claude-4"},
        "gemini": {"gemini-1.5", "gemini-2.0", "gemini-2.5"},
        "deepseek": {"deepseek", "deepseek-v2", "deepseek-v3"},
    }

    def check(
        self,
        proposer: AgentProfile,
        verifier: AgentProfile,
        minimum_dimensions: int = 1,
    ) -> IndependenceCheck:
        """
        Check that verifier differs from proposer in at least
        `minimum_dimensions` meaningful dimension(s).
        """
        differ: list[IndependenceDimension] = []
        same: list[IndependenceDimension] = []

        # Dimension 1: Model family
        if self._models_are_different(proposer.model_family, verifier.model_family):
            differ.append(IndependenceDimension.DIFFERENT_MODEL)
        else:
            same.append(IndependenceDimension.DIFFERENT_MODEL)

        # Dimension 2: Context window
        if proposer.context_window != verifier.context_window:
            differ.append(IndependenceDimension.DIFFERENT_CONTEXT)
        else:
            same.append(IndependenceDimension.DIFFERENT_CONTEXT)

        # Dimension 3: Identity
        if proposer.identity != verifier.identity:
            differ.append(IndependenceDimension.DIFFERENT_IDENTITY)
        else:
            same.append(IndependenceDimension.DIFFERENT_IDENTITY)

        # Dimension 4: Retrieval corpus
        if proposer.retrieval_corpus != verifier.retrieval_corpus:
            differ.append(IndependenceDimension.DIFFERENT_CORPUS)
        else:
            same.append(IndependenceDimension.DIFFERENT_CORPUS)

        # Dimension 5: Human reviewer
        if (
            proposer.human_reviewer is not None
            and verifier.human_reviewer is not None
            and proposer.human_reviewer != verifier.human_reviewer
        ):
            differ.append(IndependenceDimension.DIFFERENT_HUMAN)
        elif (
            proposer.human_reviewer is None
            or verifier.human_reviewer is None
        ):
            # Can't compare if one is None — don't count as same
            pass
        else:
            same.append(IndependenceDimension.DIFFERENT_HUMAN)

        is_independent = len(differ) >= minimum_dimensions

        if is_independent:
            reason = (
                f"Independent: differs in {len(differ)} dimension(s): "
                f"{', '.join(d.value for d in differ)}"
            )
        else:
            reason = (
                f"NOT independent: only {len(differ)} dimension(s) differ "
                f"(need {minimum_dimensions}). Same: "
                f"{', '.join(d.value for d in same)}"
            )

        return IndependenceCheck(
            is_independent=is_independent,
            dimensions_differ=differ,
            dimensions_same=same,
            reason=reason,
            minimum_required=minimum_dimensions,
        )

    def _models_are_different(self, family_a: str, family_b: str) -> bool:
        """
        Two models are different if they belong to different provider families
        OR if they're in the same family but not 'similar' variants.
        """
        if family_a == family_b:
            return False

        # Check if they're in the same similarity group
        for _group_name, members in self.SIMILAR_FAMILIES.items():
            if family_a in members and family_b in members:
                return False  # Same group → too similar

        return True  # Different groups → independent


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def assert_evaluator_independent(
    proposer: AgentProfile,
    verifier: AgentProfile,
    minimum_dimensions: int = 1,
) -> IndependenceCheck:
    """
    Assert evaluator is independent. Raises ValueError if not.
    Use before /555 adversarial verification.
    """
    gate = EvaluatorIndependenceGate()
    result = gate.check(proposer, verifier, minimum_dimensions)

    if not result.is_independent:
        raise ValueError(
            f"Evaluator independence check FAILED: {result.reason}. "
            f"Cannot proceed to /555 adversarial verification."
        )

    return result
