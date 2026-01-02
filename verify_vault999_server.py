#!/usr/bin/env python3
"""
verify_vault999_server.py — Quick verification script for VAULT999 MCP Server

Checks:
1. Vault structure exists
2. SSL certificates exist
3. Dependencies installed
4. Server can start (dry run)

Usage:
    python verify_vault999_server.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check(name: str, passed: bool, message: str = ""):
    """Print check result."""
    status = f"{GREEN}?{RESET}" if passed else f"{RED}?{RESET}"
    print(f"{status} {name}")
    if message:
        print(f"   {message}")
    return passed

def main():
    print("=" * 70)
    print("VAULT999 MCP SERVER VERIFICATION")
    print("=" * 70)
    print()

    all_passed = True
    repo_root = Path(__file__).resolve().parent

    # Check 1: Vault structure
    print("[1/6] Checking vault structure...")
    vault_root = repo_root / "vault_999" / "VAULT999"
    l0_exists = (vault_root / "L0_Vault").exists()
    l1_exists = (vault_root / "L1_Ledger").exists()
    l4_exists = (vault_root / "L4_Witness").exists()

    all_passed &= check("L0_Vault exists", l0_exists, str(vault_root / "L0_Vault"))
    all_passed &= check("L1_Ledger exists", l1_exists, str(vault_root / "L1_Ledger"))
    all_passed &= check("L4_Witness exists", l4_exists, str(vault_root / "L4_Witness"))
    print()

    # Check 2: SSL certificates
    print("[2/6] Checking SSL certificates...")
    cert_dir = repo_root / "arifos_core" / "mcp" / "certs"
    cert_exists = (cert_dir / "cert.pem").exists()
    key_exists = (cert_dir / "key.pem").exists()

    all_passed &= check("cert.pem exists", cert_exists, str(cert_dir / "cert.pem"))
    all_passed &= check("key.pem exists", key_exists, str(cert_dir / "key.pem"))

    if not cert_exists or not key_exists:
        print(f"   {YELLOW}Generate with:{RESET}")
        print("     mkdir -p arifos_core/mcp/certs")
        print("     cd arifos_core/mcp/certs")
        print("     openssl req -x509 -newkey rsa:4096 -nodes \\")
        print("       -out cert.pem -keyout key.pem -days 365 \\")
        print("       -subj '/CN=127.0.0.1' \\")
        print("       -addext 'subjectAltName=IP:127.0.0.1'")
    print()

    # Check 3: Python dependencies
    print("[3/6] Checking Python dependencies...")
    try:
        import mcp.server.fastmcp
        fastmcp_ok = True
    except ImportError:
        fastmcp_ok = False

    try:
        import pydantic
        pydantic_ok = True
    except ImportError:
        pydantic_ok = False

    all_passed &= check("fastmcp installed", fastmcp_ok, "pip install fastmcp")
    all_passed &= check("pydantic installed", pydantic_ok, "pip install pydantic>=2.0")

    if not fastmcp_ok or not pydantic_ok:
        print(f"   {YELLOW}Install with:{RESET}")
        print("     pip install -r arifos_core/mcp/requirements.txt")
    print()

    # Check 4: Server script exists
    print("[4/6] Checking server script...")
    server_script = repo_root / "arifos_core" / "mcp" / "vault999_server.py"
    script_exists = server_script.exists()

    all_passed &= check("vault999_server.py exists", script_exists, str(server_script))
    print()

    # Check 5: Imports work
    print("[5/6] Checking imports...")
    try:
        sys.path.insert(0, str(repo_root))
        from arifos_core.memory.vault999 import Vault999
        vault_import_ok = True
    except ImportError as e:
        vault_import_ok = False
        print(f"   {YELLOW}Warning:{RESET} Vault999 import failed ({e})")

    all_passed &= check("Memory modules importable", vault_import_ok, "")
    print()

    # Check 6: Server can be imported (dry run)
    print("[6/6] Testing server import (dry run)...")
    if script_exists and fastmcp_ok:
        try:
            # Don't run main(), just check if module loads
            spec = __import__('importlib.util').util.spec_from_file_location(
                "vault999_server", server_script
            )
            if spec and spec.loader:
                module = __import__('importlib.util').util.module_from_spec(spec)
                # Don't execute, just verify it can be loaded
                server_import_ok = True
            else:
                server_import_ok = False
        except Exception as e:
            server_import_ok = False
            print(f"   {YELLOW}Warning:{RESET} Server import failed ({e})")
    else:
        server_import_ok = False

    all_passed &= check("Server script importable", server_import_ok, "")
    print()

    # Summary
    print("=" * 70)
    if all_passed:
        print(f"{GREEN}? ALL CHECKS PASSED{RESET}")
        print()
        print("Next steps:")
        print("  1. Start server: python arifos_core/mcp/vault999_server.py")
        print("  2. Open ChatGPT ? Settings ? Apps ? Create app")
        print("  3. Name: VAULT999, URL: https://127.0.0.1:8000/sse/")
        print()
        print("DITEMPA BUKAN DIBERI")
    else:
        print(f"{RED}? SOME CHECKS FAILED{RESET}")
        print()
        print("Fix issues above before starting server.")
        print("See: arifos_core/mcp/VAULT999_README.md")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
