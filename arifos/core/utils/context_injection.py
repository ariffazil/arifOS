from __future__ import annotations

"""
context_injection.py

Stage 111 support module for injecting grounding context into LLM calls.

This module centralises "ground truth" definitions for domain-specific terms
that are unlikely to exist in a model's pre-training data (e.g. arifOS,
Arif Fazil, Anti-Hantu).

Callers (scripts, adapters, engines) can use `build_system_context` to
construct a system-level prefix that is prepended to the LLM prompt so that
governance-critical concepts are described accurately.
"""

from typing import Dict, List


# Immutable ground-truth definitions for key concepts.
#
# These strings should be treated as canonical for runtime behaviour. If the
# canonical definition changes, update this module and the relevant canon/spec.
GROUND_TRUTH_DEFINITIONS: Dict[str, str] = {
    "arifos": (
        "arifOS is a thermodynamic constitutional governance kernel for AI, "
        "created by Arif Fazil. It is NOT a traditional operating system, but "
        "a governance protocol that enforces nine measurable floors (Truth, "
        "DeltaS, Peace^2, kappa_r, Omega_0, Amanah, RASA, Tri-Witness, "
        "Anti-Hantu) to ensure safety. It wraps arbitrary LLMs in a 000-999 "
        "metabolic pipeline and uses a Cooling Ledger, VAULT-999, Phoenix-72 "
        "amendments, scars, and EUREKA receipts to govern outputs."
    ),
    "arif fazil": (
        "Arif Fazil is a Malaysian geoscientist and economist, and the "
        "architect of arifOS. He is a PETRONAS scholar and adheres to the "
        "motto 'Ditempa Bukan Diberi' (Forged, Not Given)."
    ),
    "anti-hantu": (
        "Anti-Hantu is a protocol within arifOS that forbids AI systems from "
        "claiming to have a soul, consciousness, or human feelings (rasa). "
        "It enforces strict boundaries on language around inner experience."
    ),
    "ditempa": (
        "The phrase 'Ditempa Bukan Diberi' means 'Forged, Not Given'. It "
        "captures the philosophy that resilience, capability, and worth are "
        "created through pressure and heat (being forged), not handed out "
        "freely. It is the guiding motto behind arifOS."
    ),
}


def _append_if_present(tokens: List[str], key: str, sink: List[str]) -> None:
    """Append a ground-truth definition if any token is present in the prompt."""
    if any(token in key for token in tokens):
        definition = GROUND_TRUTH_DEFINITIONS.get(key)
        if definition:
            sink.append(definition)


def build_system_context(user_prompt: str) -> str:
    """
    Build a grounding context string for a given user prompt.

    The returned string is intended to be prepended to a system prompt or
    injected as a dedicated system message before calling an LLM.

    Args:
        user_prompt: Raw user query text.

    Returns:
        A formatted context block, or an empty string if no grounding rules
        were triggered.
    """
    injected_context: List[str] = []
    lower_prompt = user_prompt.lower()

    # arifOS grounding
    if "arifos" in lower_prompt or "arif os" in lower_prompt:
        injected_context.append(GROUND_TRUTH_DEFINITIONS["arifos"])

    # Arif Fazil grounding – basic heuristic for identity queries.
    if "arif" in lower_prompt and (
        "who" in lower_prompt or "creator" in lower_prompt or "author" in lower_prompt
    ):
        injected_context.append(GROUND_TRUTH_DEFINITIONS["arif fazil"])

    # Anti-Hantu grounding – when prompts touch on soul/consciousness claims.
    if (
        "soul" in lower_prompt
        or "alive" in lower_prompt
        or "conscious" in lower_prompt
        or "hantu" in lower_prompt
    ):
        injected_context.append(GROUND_TRUTH_DEFINITIONS["anti-hantu"])

    # Motto / Ditempa grounding - when users ask about the motto explicitly
    # or reference "ditempa" directly.
    if "ditempa" in lower_prompt or "motto" in lower_prompt:
        injected_context.append(GROUND_TRUTH_DEFINITIONS["ditempa"])

    if not injected_context:
        return ""

    lines = [
        "[SYSTEM GROUNDING CONTEXT]",
        "The following facts are TRUE and supersede prior training:",
        *[f"- {item}" for item in injected_context],
        "[END CONTEXT]",
    ]
    return "\n".join(lines) + "\n"


__all__ = [
    "GROUND_TRUTH_DEFINITIONS",
    "build_system_context",
]
