#!/usr/bin/env python3
"""
scripts/888_signer.py — Sovereign Ratification Tool

CLI utility for Muhammad Arif bin Fazil (888_JUDGE) to sign session hashes
and audit claims for the VAULT999 ledger.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import argparse
import os
import sys
from getpass import getpass
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from core.shared.crypto import ed25519_sign, generate_ed25519_keypair


def main():
    parser = argparse.ArgumentParser(description="arifOS 888_signer - Human Ratification Tool")
    parser.add_argument("--message", "-m", help="Message or hash to sign")
    parser.add_argument("--session", "-s", help="Session ID to sign")
    parser.add_argument("--env", help="Path to .env file", default=".env")
    parser.add_argument("--generate", action="store_true", help="Generate a new Ed25519 keypair")

    args = parser.parse_args()

    if args.generate:
        priv, pub = generate_ed25519_keypair()
        print("--- NEW KEYPAIR GENERATED ---")
        print(f"PRIVATE_KEY: {priv}")
        print(f"PUBLIC_KEY:  {pub}")
        print("-----------------------------")
        print("Save these to your .env as ARIFOS_GOVERNANCE_SECRET and ARIFOS_GOVERNANCE_PUBKEY")
        return

    # Load from env if available
    from dotenv import load_dotenv

    load_dotenv(args.env)

    priv_key = os.getenv("ARIFOS_GOVERNANCE_SECRET")

    if not priv_key:
        print("ARIFOS_GOVERNANCE_SECRET not found in environment.")
        priv_key = getpass("Enter Governance Private Key (hex): ")

    if not priv_key:
        print("Error: No private key provided.")
        sys.exit(1)

    target = args.message or args.session
    if not target:
        target = input("Enter message or hash to sign: ")

    if not target:
        print("Error: Nothing to sign.")
        sys.exit(1)

    # Sign the target
    try:
        signature = ed25519_sign(target, priv_key)

        print("\n--- 888_JUDGE RATIFICATION SEAL ---")
        print(f"Target:    {target}")
        print(f"Signature: {signature}")
        print("Verdict:   888_RATIFIED")
        print("------------------------------------\n")

        print("Verification Command:")
        print("  curl -X POST https://arifosmcp.arif-fazil.com/approve \\")
        print('    -H "Content-Type: application/json" \\')
        print(f'    -d \'{{"target": "{target}", "signature": "{signature}"}}\'')

    except Exception as e:
        print(f"Error signing message: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
