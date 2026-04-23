from arifosmcp.intelligence.tools.fs_inspector import inspect_path
from arifosmcp.intelligence.tools.net_monitor import check_connectivity
import os

def test_aliases():
    print("Testing internal function aliases...")
    
    # Test inspect_path
    res_fs = inspect_path(path=".", depth=1)
    if res_fs.get("status") in ["SEAL", "ok"]:
        print("✅ inspect_path alias works")
    else:
        print(f"❌ inspect_path failed: {res_fs}")

    # Test check_connectivity
    res_net = check_connectivity(check_ports=False)
    if res_net.get("status") in ["SEAL", "ok"]:
        print("✅ check_connectivity alias works")
    else:
        print(f"❌ check_connectivity failed: {res_net}")

if __name__ == "__main__":
    test_aliases()
