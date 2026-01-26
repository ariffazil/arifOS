
import os
import sys

# Set Lite Mode flag BEFORE importing mcp_trinity
os.environ["ARIFOS_LITE_MODE"] = "true"

try:
    from arifos.mcp.tools import mcp_trinity
    from arifos.mcp.tools import v51_bridge
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_lite_mode():
    print(f"Testing Lite Mode (LITE_MODE={mcp_trinity.LITE_MODE})...")
    if not mcp_trinity.LITE_MODE:
        print("❌ Lite Mode not active despite env var")
        return False
    
    entropy = mcp_trinity._measure_entropy("Unexpectedly complex string that should have entropy")
    if entropy == 0.0:
        print(f"✅ Lite Mode Entropy Optimization working (entropy={entropy})")
        return True
    else:
        print(f"❌ Lite Mode Entropy Optimization failed (entropy={entropy})")
        return False

def test_zk_proof_signatures():
    print("Testing zk_proof signatures in bridge...")
    import inspect
    
    # Check if zk_proof is in arguments
    sig_agi = inspect.signature(v51_bridge.bridge_agi_full)
    sig_asi = inspect.signature(v51_bridge.bridge_asi_full)
    sig_apex = inspect.signature(v51_bridge.bridge_apex_full)
    
    if "zk_proof" in sig_agi.parameters and "zk_proof" in sig_asi.parameters and "zk_proof" in sig_apex.parameters:
        print("✅ zk_proof argument present in all full bridge functions")
        return True
    else:
        print("❌ zk_proof argument missing in some bridge functions")
        return False

if __name__ == "__main__":
    lite_pass = test_lite_mode()
    zk_pass = test_zk_proof_signatures()
    
    if lite_pass and zk_pass:
        print("\n🎉 v52 FORGE VERIFICATION SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n💥 v52 FORGE VERIFICATION FAILED")
        sys.exit(1)
