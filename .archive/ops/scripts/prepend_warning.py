"""
scripts/prepend_warning.py — arifOS Asset Safety Utility

Purpose: Prepend safety warnings to archived or non-law markdown assets.
Motto: DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import os

WARNING_TEXT = "> [!WARNING]\n> ARCHIVE SUBSTRATE ONLY. DO NOT PROMOTE TO ACTIVE LAW.\n\n"

# Search from repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRECTORIES_TO_SCAN = [
    os.path.join(REPO_ROOT, "000_THEORY", "archive"),
    os.path.join(REPO_ROOT, "333_APPS", "L1_PROMPT"),
]


def main():
    for d in DIRECTORIES_TO_SCAN:
        if not os.path.exists(d):
            print(f"Skipping missing directory: {d}")
            continue
        for root, _dirs, files in os.walk(d):
            for f in files:
                if f.endswith(".md"):
                    file_path = os.path.join(root, f)
                    with open(file_path, encoding="utf-8") as file:
                        content = file.read()

                    # Check if it already has the warning
                    if "> ARCHIVE SUBSTRATE ONLY" not in content:
                        with open(file_path, "w", encoding="utf-8") as file:
                            file.write(WARNING_TEXT + content)
                        print(f"Updated {file_path}")
                    else:
                        print(f"Skipped {file_path} (Already updated)")

    print("Done prepending warnings.")


if __name__ == "__main__":
    main()
