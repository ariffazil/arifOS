import os
import sys

# Add repo root to path
sys.path.append(os.getcwd())

print("Verifying imports...")

# 1. Floor Validators
try:
    from arifos.core.floor_validators import (
        validate_f1_amanah,
        validate_f5_peace,
        validate_f6_empathy,
        validate_f8_genius,
        validate_f9_cdark,
    )
    print("✅ Floor Validators imported.")
except ImportError as e:
    print(f"❌ Floor Validators failed: {e}")

# 2. Cooling
try:
    from arifos.core.asi.cooling import CoolingEngine
    print("✅ CoolingEngine imported.")
except ImportError as e:
    print(f"❌ CoolingEngine failed: {e}")

# 3. Memory Tower
try:
    from arifos.core.vault.memory_tower import EurekaSieve, store_memory
    print("✅ Memory Tower imported.")
except ImportError as e:
    print(f"❌ Memory Tower failed: {e}")

# 4. Stage 888 (APEX Prime)
try:
    from arifos.core.system.apex_prime import APEXPrime
    print("✅ APEXPrime module imported.")
    prime = APEXPrime()
    print("✅ APEXPrime instantiated.")
except ImportError as e:
    print(f"❌ APEXPrime failed: {e}")
except Exception as e:
    print(f"❌ APEXPrime instantiation failed: {e}")

# 5. Stage 999 (Seal)
try:
    from arifos.core.mcp.tools import mcp_999_seal
    print("✅ mcp_999_seal imported.")
except ImportError as e:
    print(f"❌ mcp_999_seal failed: {e}")

print("Verification complete.")
