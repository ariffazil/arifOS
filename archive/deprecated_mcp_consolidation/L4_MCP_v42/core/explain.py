"""
Explanation Generator for L4_MCP.

Generates human-readable explanations for verdicts.
"""

from typing import List

from L4_MCP.apex.schema import Verdict


def generate_explanation(
    verdict: Verdict,
    reason_codes: List[str],
    required_evidence: List[str],
    constraints: List[str],
    context_hint: str = "",
) -> str:
    """
    Generate a human-readable explanation of the verdict decision.

    Args:
        verdict: The final verdict (SEAL/VOID/SABAR/HOLD_888)
        reason_codes: List of triggered rule codes
        required_evidence: Evidence needed to proceed
        constraints: Execution constraints imposed
        context_hint: Additional context for the explanation

    Returns:
        Multi-line human-readable explanation string
    """
    lines = []

    # Verdict line
    verdict_emoji = {
        Verdict.SEAL: "✅",
        Verdict.VOID: "🚫",
        Verdict.SABAR: "⏸️",
        Verdict.HOLD_888: "🔒",
    }.get(verdict, "❓")

    lines.append(f"{verdict_emoji} Verdict: {verdict.value}")

    # Reason codes
    if reason_codes:
        lines.append(f"Reason(s): {', '.join(reason_codes)}")

    # Required evidence
    if required_evidence:
        lines.append(f"Required evidence: {', '.join(required_evidence)}")

    # Constraints
    if constraints:
        lines.append(f"Constraints: {', '.join(constraints)}")

    # Context hint
    if context_hint:
        lines.append(f"Context: {context_hint}")

    return "\n".join(lines)
