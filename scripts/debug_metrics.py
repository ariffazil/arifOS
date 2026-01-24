
import json
import os
import sys
from pathlib import Path

# Add repo root to path
sys.path.append(os.getcwd())

# Setup env as verify script does
os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"
os.environ["ARIFOS_FLOORS_SPEC"] = str(Path("AAA_MCP/v46/constitutional_floors.json").resolve())

print("DEBUG: Starting metrics debug")
print(f"DEBUG: Spec path: {os.environ['ARIFOS_FLOORS_SPEC']}")

try:
    with open("AAA_MCP/v46/constitutional_floors.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print("DEBUG: JSON load successful")
    
    # Try manual validation
    if "constitutional_floors" in data:
        print("DEBUG: 'constitutional_floors' key present")
        floors = data["constitutional_floors"]
        req = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]
        missing = [key for key in req if key not in floors]
        if missing:
            print(f"DEBUG: Missing keys: {missing}")
        else:
            print("DEBUG: All required keys present")
            
        # Check F7
        f7 = floors["F7"]
        if "threshold_min" in f7 and "threshold_max" in f7:
            print("DEBUG: F7 thresholds present")
        else:
            print(f"DEBUG: F7 malformed: {f7}")
            
except Exception as e:
    print(f"DEBUG: Manual check failed: {e}")

print("DEBUG: Attempting to import metrics...")
try:
    from arifos.core.enforcement import metrics
    print("DEBUG: Import successful")
    print(f"DEBUG: Loaded from: {metrics._FLOORS_SPEC.get('_loaded_from', 'UNKNOWN')}")
except RuntimeError as e:
    print(f"DEBUG: Import failed with RuntimeError: {e}")
except Exception as e:
    print(f"DEBUG: Import failed with {type(e)}: {e}")
