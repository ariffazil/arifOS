"""
codebase.mcp.tools.reality_grounding (v53.2.2)
Gate for General Reality Grounding (Brave Search).
F7 (Humility): Explicit uncertainty boundary and disclosure.
"""

import logging

logger = logging.getLogger(__name__)

def should_reality_check(
    query: str,
    lane: str,
    intent: str,
    scar_weight: float
) -> tuple[bool, str]:
    """
    Decide: Does this query need current external facts?
    
    Returns:
        (bool, str): (should_check, reason)
        None in first position means "defer to consensus".
    """
    
    # Signals that need reality grounding
    TIME_SENSITIVE_INTENTS = [
        "current_facts", "recent_news", "latest_data",
        "market_price", "policy_update", "breaking_news",
        "economics", "politics", "news"
    ]
    
    # Signals that DON'T need reality grounding
    TIMELESS_INTENTS = [
        "explain_concept", "historical_context",
        "define_term", "architecture_review", "debug_code"
    ]
    
    query_lower = query.lower()
    
    # Rule 1: Timeless intent → use memory
    if intent in TIMELESS_INTENTS:
        logger.info(f"Reality Gate: USE_MEMORY (Timeless intent: {intent})")
        return False, f"Timeless intent ({intent}) - internal memory sufficient"
    
    # Rule 2: Explicit sovereign request for "search" or "latest"
    if scar_weight >= 1.0 and any(kw in query_lower for kw in ["search", "latest", "current", "news"]):
        logger.info("Reality Gate: BRAVE (Sovereign explicit request)")
        return True, "Sovereign explicit request for real-time data"
    
    # Rule 3: Time-sensitive intent
    if intent in TIME_SENSITIVE_INTENTS:
        logger.info(f"Reality Gate: BRAVE (Time-sensitive intent: {intent})")
        return True, f"Time-sensitive intent ({intent})"
    
    # Rule 4: GUEST + Reality query → allowed but will be disclosed
    if scar_weight < 1.0 and any(kw in query_lower for kw in ["what's happening", "news", "price"]):
        logger.info("Reality Gate: BRAVE (Guest reality-curious)")
        return True, "Guest requested current facts (external source required)"
    
    # Rule 5: Unknown intent → ask tri-witness
    logger.info(f"Reality Gate: DEFER (Uncertain intent={intent})")
    return None, "Uncertain intent - defer to tri-witness consensus"
