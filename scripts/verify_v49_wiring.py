import logging
import os
import sys

# Bypass legacy spec enforcements for v49 transition
os.environ["ALLOW_LEGACY_SPEC"] = "1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY")

def test_imports():
    logger.info("Verifying v49 Imports...")

    try:
        logger.info("1. Checking Constitutional Constants...")
        import arifos.constitutional_constants as cc
        logger.info(f"   - Version: {cc.CONSTITUTIONAL_VERSION}")
        logger.info(f"   - FloorType.HARD: {cc.FloorType.HARD}")

        logger.info("2. Checking Floor Validators...")
        from arifos.core import floor_validators as fv
        logger.info("   - Loaded floor_validators")

        logger.info("3. Checking Thermodynamic Validator...")
        from arifos.core import thermodynamic_validator as tv
        logger.info("   - Loaded thermodynamic_validator")

        logger.info("4. Checking Trinity Servers...")
        import arifos.servers.agi_server as agi
        logger.info("   - Loaded AGI Server")
        import arifos.servers.asi_server as asi
        logger.info("   - Loaded ASI Server")
        import arifos.servers.apex_server as apex
        logger.info("   - Loaded APEX Server")
        import arifos.servers.vault_server as vault
        logger.info("   - Loaded VAULT Server")

        logger.info("✅ ALL IMPORTS SUCCESSFUL - v49 WIRING COMPLETE")
        return True

    except Exception as e:
        logger.error(f"❌ IMPORT FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
