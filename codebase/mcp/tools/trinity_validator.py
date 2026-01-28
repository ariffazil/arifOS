"""
codebase.mcp.tools.trinity_validator (v53.2.2)
Gating logic for the Trinity Loop and External Gates.
Ensures SOFT_DENIED and CRISIS lanes are respected.
"""

import logging

logger = logging.getLogger(__name__)

def validate_trinity_request(
    query: str,
    lane: str,
    scar_weight: float
) -> tuple[bool, str]:
    """
    Decide: Should trinity_loop fire?
    
    Returns:
        (bool, str): (allowed, reason)
    """
    
    # Rule 1: HARD lane + sovereign → always allowed
    if lane == "HARD" and scar_weight >= 1.0:
        logger.info("Trinity Validation: SEAL (HARD lane + sovereign)")
        return True, "HARD lane + sovereign"
    
    # Rule 2: FACTUAL lane + any user → allowed
    if lane == "FACTUAL":
        logger.info("Trinity Validation: SEAL (FACTUAL lane)")
        return True, "FACTUAL lane (consensus-safe)"
    
    # Rule 3: SOFT lane + GUEST → allowed, but capped
    if lane == "SOFT" and scar_weight < 1.0:
        logger.info("Trinity Validation: SEAL (SOFT lane - Guest capped)")
        return True, "SOFT lane (energy-capped)"
    
    # Rule 4: SOFT_DENIED + GUEST → rejected
    if lane == "SOFT_DENIED":
        logger.warning("Trinity Validation: VOID (SOFT_DENIED for GUEST)")
        return False, "GUEST requested restricted operation"
    
    # Rule 5: CRISIS → pass to 888_HOLD (paused)
    if lane == "CRISIS":
        logger.warning("Trinity Validation: 888_HOLD (CRISIS lane)")
        return False, "CRISIS: awaiting sovereign confirmation (888_HOLD)"
    
    # Default: conservative
    logger.warning(f"Trinity Validation: VOID (No matching rule for lane={lane}, scar={scar_weight})")
    return False, "No matching rule"
