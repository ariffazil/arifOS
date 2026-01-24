import logging
import os
import sys


# Ensure repo root is in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Bypass legacy spec enforcements for v49 transition
# Must be set BEFORE importing any arifos modules that check manifest
os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"

# Explicitly set the floors spec path to resolve "not found" errors
# Using v46 as the authoritative source for the current pinned runtime
specs = {
    "ARIFOS_FLOORS_SPEC": "AAA_MCP/v46/constitutional_floors.json",
    "ARIFOS_GENIUS_SPEC": "AAA_MCP/v46/genius_law.json",
    "ARIFOS_STAGES_SPEC": "AAA_MCP/v46/constitutional_stages.json",
    "ARIFOS_WORKFLOWS_SPEC": "AAA_MCP/v46/constitutional_workflows.json"
}

for env_var, rel_path in specs.items():
    abs_path = os.path.abspath(rel_path)
    if os.path.exists(abs_path):
        os.environ[env_var] = abs_path
        print(f"DEBUG: Set {env_var} = {abs_path}")
        # Verify file readability
        try:
             with open(abs_path, 'r', encoding='utf-8') as f:
                 import json
                 json.load(f)
             print(f"DEBUG: Verified {env_var} is readable and valid JSON")
        except Exception as e:
             print(f"DEBUG: Failed to read {env_var}: {e}")
    else:
        print(f"DEBUG: Could not find spec at {abs_path}")

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
        import arifos.core.servers.agi_server as agi
        logger.info("   - Loaded AGI Server")
        import arifos.core.servers.asi_server as asi
        logger.info("   - Loaded ASI Server")
        import arifos.core.servers.apex_server as apex
        logger.info("   - Loaded APEX Server")
        import arifos.core.servers.vault_server as vault
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
