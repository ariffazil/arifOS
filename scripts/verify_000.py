
import sys
from pathlib import Path

# Add repo root to path
sys.path.append(str(Path.cwd()))

import importlib

try:
    module = importlib.import_module("arifos.core.000_void.stage")
    execute_stage = module.execute_stage
    print("✅ SUCCESS: Imported arifos.core.000_void.stage via importlib")
except ImportError as e:
    print(f"❌ FAILURE: Could not import stage: {e}")
    sys.exit(1)

context = {"session_id": "test_verification"}
try:
    result = execute_stage(context)
    print("✅ SUCCESS: Executed execute_stage()")
    print(f"   Context Stage: {result.get('stage')}")
    print(f"   Context Status: {result.get('status')}")

    if result.get("stage") == "000" and result.get("status") == "INITIALIZED":
        print("✅ VERIFIED: 000 IS DOING 000 (Initialization)")
    else:
        print("❌ FAILURE: Stage logic incorrect")

except Exception as e:
    print(f"❌ FAILURE: Execution error: {e}")
