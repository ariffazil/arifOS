"""
canonical_core/ignition.py — System Ignition Script (Stage 000)

This is the "Power Button" for arifOS.
It executes Stage 000 (VOID) and verifies all constitutional floors are operational.

Usage:
    python -m canonical_core.ignition "System check"
"""

import sys
import json
import logging
from typing import Optional

# Use relative imports (we're inside the 000_init package)
from .stage_000_core import execute_stage_000, VerdictType

try:
    from codebase.constitutional_floors import ALL_FLOORS
except ImportError:
    ALL_FLOORS = {}  # Graceful fallback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IGNITION")

def ignite_system(query: str = "System Ignition Check", operator: str = "CLI") -> bool:
    """
    Ignite the arifOS system by running Stage 000.
    
    Args:
        query: The initial input/query to the system.
        operator: Source of the ignition command.
        
    Returns:
        True if ignition successful (SEAL), False otherwise.
    """
    logger.info(f"🔌 IGNITION SEQUENCE INITIATED by {operator}")
    logger.info(f"📝 Query: {query}")
    
    # 1. Verify Floors are Loaded
    logger.info(f"🏗️  Loading Constitutional Floors... ({len(ALL_FLOORS)} found)")
    for fid, floor_cls in ALL_FLOORS.items():
        logger.debug(f"   - {fid}: {floor_cls.__name__}")
        
    # 2. Execute Stage 000
    try:
        result = execute_stage_000(
            input_text=query,
            source=operator
        )
        
        logger.info("--------------------------------------------------")
        logger.info(f"🆔 Session ID: {result.metadata.session_id}")
        logger.info(f"⚖️  Verdict:    {result.verdict.value}")
        logger.info(f"🛡️  Hypervisor: {'PASS' if result.hypervisor.passed else 'FAIL'}")
        logger.info(f"🔒 Amanah:     {'PASS' if result.amanah.passed else 'FAIL'}")
        logger.info(f"🗝️  ZKPC Root:  {result.zkpc.canon_hash[:16]}...")
        logger.info("--------------------------------------------------")
        
        if result.verdict == VerdictType.SEAL:
            logger.info("✅ SYSTEM IGNITION SUCCESSFUL. READY TO METABOLIZE.")
            return True
        else:
            logger.error(f"❌ SYSTEM IGNITION FAILED. Verdict: {result.verdict.value}")
            if result.hypervisor.failures:
                logger.error(f"   Hypervisor Failures: {result.hypervisor.failures}")
            if not result.amanah.passed:
                logger.error(f"   Amanah Failure: {result.amanah.reason}")
            return False
            
    except Exception as e:
        logger.critical(f"💥 CRITICAL IGNITION FAILURE: {e}", exc_info=True)
        return False

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "System Ignition Check"
    success = ignite_system(query)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
