#!/usr/bin/env python3
"""Create spec_archive directory and extraction documents."""
import os
import sys
from pathlib import Path

# Create spec_archive directory
spec_archive = Path("spec_archive")
spec_archive.mkdir(exist_ok=True)
print(f"Created directory: {spec_archive}")

# Create placeholder files
files = [
    "arifOS-v38-Core-Brain.md",
    "arifOS-Constitution-9-Floors.md",
    "Cooling-Ledger-v35-Schema-and-Usage.md",
    "Memory-Bands-v38-Policy-Current-State.md",
    "GENIUS-LAW-Truth-Polarity-Extract.md",
    "L4-Jailbreak-Anti-Hantu-Defense.md",
    "Phase-4-Integration-Status-v38.md",
]

for fname in files:
    fpath = spec_archive / fname
    fpath.touch()
    print(f"  - {fname}")

print("\nAll files created in spec_archive/")
print("Ready for content extraction.")
