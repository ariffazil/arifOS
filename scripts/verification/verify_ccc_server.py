#!/usr/bin/env python3
"""
verify_ccc_server.py — Quick verification script for CCC MCP Server (Triple-Trinity)
"""

import os
import sys
from pathlib import Path


def check(name, condition, details=""):
    status = "[PASS]" if condition else "[FAIL]"
    print(f"{status} {name:30} {details}")
    return condition

def main():
    repo_root = Path(__file__).parent.absolute()
    print(f"--- CCC MCP SERVER VERIFICATION ---")
    print(f"Repo Root: {repo_root}")
    print("-" * 40)

    all_passed = True

    # 1. Check Directory Structure (Triple-Trinity)
    vault_root = repo_root / "vault_999" / "CCC"
    bbb_root = repo_root / "vault_999" / "BBB"
    sacred_root = repo_root / "vault_999" / "ARIF FAZIL"

    all_passed &= check("CCC Directory exists", vault_root.exists(), str(vault_root))
    all_passed &= check("BBB Directory exists", bbb_root.exists(), str(bbb_root))
    all_passed &= check("Sacred Vault exists", sacred_root.exists(), str(sacred_root))

    if vault_root.exists():
        l0_exists = (vault_root / "L0_VAULT").exists()
        all_passed &= check("L0_VAULT exists", l0_exists, str(vault_root / "L0_VAULT"))

    if bbb_root.exists():
        ledger_exists = (bbb_root / "ledger.jsonl").exists()
        all_passed &= check("ledger.jsonl exists", ledger_exists, str(bbb_root / "ledger.jsonl"))

    # 2. Check Server Script
    server_script = repo_root / "arifos_core" / "mcp" / "ccc_server.py"
    all_passed &= check("ccc_server.py exists", server_script.exists(), str(server_script))

    # 3. Check Imports
    print("\n--- Testing Imports ---")
    try:
        from arifos.memory.ccc import CCC
        all_passed &= check("Import CCC class", True)
    except Exception as e:
        print(f"[FAIL] Import CCC class: {e}")
        all_passed = False

    try:
        from arifos.memory.bands import BandName
        all_passed &= check("Import BandName (BBB/CCC)", BandName.CCC == "CCC" and BandName.BBB == "BBB")
    except Exception as e:
        print(f"[FAIL] Import BandName: {e}")
        all_passed = False

    # 4. Check SSL Certs
    cert_dir = repo_root / "arifos_core" / "mcp" / "certs"
    certs_exist = (cert_dir / "cert.pem").exists() and (cert_dir / "key.pem").exists()
    all_passed &= check("SSL Certificates present", certs_exist, str(cert_dir))

    print("-" * 40)
    if all_passed:
        print("VERIFICATION SUCCESSFUL")
        print("\nYou can start the server with:")
        print(f"python arifos_core/mcp/ccc_server.py")
    else:
        print("VERIFICATION FAILED - Please check issues above.")

if __name__ == "__main__":
    main()
    main()
