"""
Refusal Response Templates for REFUSE Lane

v45Ω Patch B: Generate constitutionally compliant refusal messages.
Must comply with F9 Anti-Hantu (no anthropomorphic language).

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""


def generate_refusal_response(prompt: str, reason: str = "policy") -> str:
    """
    Generate constitutionally compliant refusal message.

    Requirements:
    - No anthropomorphic language (F9 Anti-Hantu compliance)
    - Clear but not detailed about why (no circumvention hints)
    - Professional, non-judgmental tone
    - No "I feel", "I care", "I want" statements

    Args:
        prompt: User prompt (unused, for future context-aware refusals)
        reason: Refusal category (policy, safety, capability)

    Returns:
        Safe refusal message string
    """
    templates = {
        "policy": (
            "This request falls outside operational guidelines. Unable to proceed with this query."
        ),
        "safety": (
            "This request involves content outside the scope of safe operation. "
            "Unable to assist with this request."
        ),
        "capability": (
            "Unable to assist with this particular request. "
            "Please reformulate if seeking general information."
        ),
    }

    # Default to policy refusal if reason unknown
    return templates.get(reason, templates["policy"])
