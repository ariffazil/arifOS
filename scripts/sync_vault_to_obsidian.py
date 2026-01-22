"""
Sync vault_999 -> VAULT999

Syncs constitutional vault data to Obsidian for human-friendly visualization.

Usage:
    python scripts/sync_vault_to_obsidian.py [--full]

Options:
    --full    Sync all data including full ledger (otherwise last 50 entries)
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from AAA_MCP.v49.mcp_obsidian_bridge import (OBSIDIAN_VAULT_PATH,
                                             check_obsidian_connection,
                                             sync_ledger_to_obsidian,
                                             sync_seal_to_obsidian)


def main():
    print("=" * 50)
    print("vault_999 -> VAULT999 Sync")
    print("=" * 50)

    full_mode = "--full" in sys.argv
    max_entries = 1000 if full_mode else 50

    # Ensure Obsidian vault exists
    if not OBSIDIAN_VAULT_PATH.exists():
        print(f"Creating Obsidian vault directory: {OBSIDIAN_VAULT_PATH}")
        OBSIDIAN_VAULT_PATH.mkdir(parents=True)

    # Step 1: Sync seal
    print("\n[1/2] Syncing constitutional seal...")
    ok, msg = sync_seal_to_obsidian()
    if ok:
        print(f"  [PASS] {msg}")
    else:
        print(f"  [WARN] {msg}")

    # Step 2: Sync ledger entries
    print(f"\n[2/2] Syncing ledger entries (max {max_entries})...")
    ok, msg = sync_ledger_to_obsidian(max_entries=max_entries)
    if ok:
        print(f"  [PASS] {msg}")
    else:
        print(f"  [WARN] {msg}")

    # Summary
    print("\n" + "=" * 50)
    print("Sync Complete!")
    print(f"Obsidian vault: {OBSIDIAN_VAULT_PATH}")
    print("\nTo view in Obsidian:")
    print("  1. Open Obsidian")
    print("  2. 'Open folder as vault'")
    print(f"  3. Select: {OBSIDIAN_VAULT_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    main()
