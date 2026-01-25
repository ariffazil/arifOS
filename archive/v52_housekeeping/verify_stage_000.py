import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arifos.core.metabolizer import Metabolizer


def main():
    print("🧪 Verifying Stage 000 Consolidation")
    metabolizer = Metabolizer(enable_execution=True)
    metabolizer.initialize({"session_id": "TEST_SESSION"})

    # Check for Stage 000 context items (from arifos/core/000_void/stage.py)
    # 1. status should be INITIALIZED
    # 2. entropy_history should exist
    # 3. metadata["session_id"] should be TEST_SESSION

    success = True
    if metabolizer.context.get("status") == "INITIALIZED":
        print("✅ Status is INITIALIZED")
    else:
        print(f"❌ Status is {metabolizer.context.get('status')}")
        success = False

    if "entropy_history" in metabolizer.context:
        print("✅ Entropy history initialized")
    else:
        print("❌ Entropy history missing")
        success = False

    if metabolizer.context.get("metadata", {}).get("session_id") == "TEST_SESSION":
        print("✅ Session ID correctly mapped")
    else:
        print("❌ Session ID missing or incorrect")
        success = False

    if success:
        print("\n✨ STAGE 000 CONSOLIDATION SUCCESSFUL")
    else:
        print("\n❌ STAGE 000 CONSOLIDATION FAILED")

if __name__ == "__main__":
    main()
