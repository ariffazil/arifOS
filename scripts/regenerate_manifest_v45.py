"""
regenerate_manifest_v45.py - Regenerate SHA-256 Manifest for Track B v45 Specs

Usage:
    python scripts/regenerate_manifest_v45.py           # Regenerate manifest
    python scripts/regenerate_manifest_v45.py --check   # Verify manifest (CI mode)

Generates spec/v45/MANIFEST.sha256.json with SHA-256 hashes for all v45 spec files.
Run this after intentional modifications to v45 specs.

Check mode (--check):
    Verifies that current file hashes match manifest.
    Exit 0 if all match (CI passes).
    Exit 1 if any mismatch (CI fails, prints diff).

WARNING: Only run this if you INTENTIONALLY modified spec files.
Regenerating the manifest after unauthorized tampering defeats the purpose of integrity verification.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def check_manifest():
    """
    Check mode: Verify current file hashes match manifest (CI verification).

    Returns:
        0 if all hashes match (success)
        1 if any mismatch (failure)
    """
    manifest_path = Path("spec/v45/MANIFEST.sha256.json")

    # Load existing manifest
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found: {manifest_path}")
        print("Run without --check to generate manifest.")
        return 1

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    print("Verifying v45 spec integrity against manifest...")
    print(f"Manifest version: {manifest['version']}")
    print(f"Created at: {manifest['created_at']}")
    print()

    # Check all files in manifest
    mismatches = []
    missing_files = []

    for file_path, expected_hash in manifest['files'].items():
        path = Path(file_path)

        if not path.exists():
            missing_files.append(file_path)
            print(f"[FAIL] MISSING: {file_path}")
        else:
            actual_hash = compute_sha256(path)
            if actual_hash == expected_hash:
                print(f"[OK] {file_path}")
            else:
                mismatches.append((file_path, expected_hash, actual_hash))
                print(f"[FAIL] MISMATCH: {file_path}")
                print(f"  Expected: {expected_hash}")
                print(f"  Actual:   {actual_hash}")

    # Summary
    print()
    if not mismatches and not missing_files:
        print(f"[SUCCESS] All {len(manifest['files'])} files match manifest.")
        print("Spec integrity verified. No tampering detected.")
        return 0
    else:
        print("[FAILURE] Manifest verification failed!")
        if missing_files:
            print(f"\nMissing files ({len(missing_files)}):")
            for path in missing_files:
                print(f"  - {path}")
        if mismatches:
            print(f"\nHash mismatches ({len(mismatches)}) - FILES HAVE BEEN MODIFIED:")
            for path, expected, actual in mismatches:
                print(f"  - {path}")
        print("\nTo fix:")
        print("  1. Restore original files from git: git restore spec/v45/")
        print("  2. Or regenerate manifest (if changes are intentional): python scripts/regenerate_manifest_v45.py")
        return 1


def regenerate_manifest():
    """Regenerate v45 manifest with current SHA-256 hashes."""
    # Files to include in manifest
    files = [
        'spec/v45/constitutional_floors.json',
        'spec/v45/genius_law.json',
        'spec/v45/session_physics.json',
        'spec/v45/red_patterns.json',
        'spec/v45/schema/constitutional_floors.schema.json',
        'spec/v45/schema/genius_law.schema.json',
        'spec/v45/schema/session_physics.schema.json',
        'spec/v45/schema/red_patterns.schema.json',
    ]

    # Compute hashes
    manifest = {
        'version': 'v45.0',
        'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'algorithm': 'SHA-256',
        'description': 'Cryptographic manifest for Track B v45 specifications (tamper-evident integrity)',
        'files': {}
    }

    print("Computing SHA-256 hashes for v45 specs...")
    for file in files:
        path = Path(file)
        if path.exists():
            hash_value = compute_sha256(path)
            manifest['files'][file] = hash_value
            print(f"  {file}: {hash_value[:16]}...")
        else:
            print(f"  WARNING: {file} NOT FOUND (skipping)")

    # Write manifest
    manifest_path = Path("spec/v45/MANIFEST.sha256.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')  # Trailing newline

    print(f"\n[SUCCESS] Manifest regenerated: {manifest_path}")
    print(f"  Files verified: {len(manifest['files'])}")
    print(f"  Created at: {manifest['created_at']}")
    print("\nNOTE: Commit this manifest along with any spec changes.")
    return 0


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Regenerate or verify SHA-256 manifest for Track B v45 specs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/regenerate_manifest_v45.py           # Regenerate manifest
  python scripts/regenerate_manifest_v45.py --check   # Verify manifest (CI mode)
        """
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check mode: verify current hashes match manifest (exit 0 if OK, 1 if mismatch)'
    )

    args = parser.parse_args()

    if args.check:
        return check_manifest()
    else:
        return regenerate_manifest()


if __name__ == '__main__':
    sys.exit(main())
