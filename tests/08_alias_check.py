"""
tests/08_alias_check.py — Internal function alias tests.

Updated 2026-07-08: inspect_path signature changed (max_depth), check_connectivity is async.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import asyncio

from arifosmcp.intelligence.tools.fs_inspector import inspect_path
from arifosmcp.intelligence.tools.net_monitor import check_connectivity


def test_aliases():
    print("Testing internal function aliases...")

    # Test inspect_path
    res_fs = inspect_path(path=".", max_depth=1)
    if res_fs.get("status") in ["SEAL", "ok"]:
        print("✅ inspect_path alias works")
    else:
        print(f"❌ inspect_path failed: {res_fs}")

    # Test check_connectivity (async)
    res_net = asyncio.get_event_loop().run_until_complete(
        check_connectivity(host="https://example.com", timeout=2.0)
    )
    if res_net.get("status") in ["SEAL", "ok", "connected"]:
        print("✅ check_connectivity alias works")
    else:
        print(f"❌ check_connectivity failed: {res_net}")


if __name__ == "__main__":
    test_aliases()
