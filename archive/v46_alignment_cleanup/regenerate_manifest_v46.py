"""
regenerate_manifest_v46.py - Regenerate SHA-256 Manifest for L2_PROTOCOLS v46 Specs

Usage:
    python scripts/regenerate_manifest_v46.py           # Regenerate manifest
    python scripts/regenerate_manifest_v46.py --check   # Verify manifest (CI mode)

Generates L2_PROTOCOLS/v46/MANIFEST.sha256.json with SHA-256 hashes for all v46 spec files.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

MANIFEST_PATH = repo_root / "L2_PROTOCOLS" / "v46" / "MANIFEST.sha256.json"
BASE_DIR = repo_root / "L2_PROTOCOLS" / "v46"

def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_spec_files():
    """Recursively find all spec files in L2_PROTOCOLS/v46."""
    files = []
    for root, _, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            if filename == "MANIFEST.sha256.json":
                continue
            if filename.endswith(".json") or filename.endswith(".md"):
                full_path = Path(root) / filename
                # Store relative path from repo root for portability
                rel_path = full_path.relative_to(repo_root).as_posix()
                files.append(rel_path)

    # Also include L1 Canon anchor
    l1_anchor = "L1_THEORY/canon/000_MASTER_INDEX_v46.md"
    if (repo_root / l1_anchor).exists():
        files.append(l1_anchor)

    return sorted(files)

def check_manifest():
    """Check mode: Verify current file hashes match manifest."""
    if not MANIFEST_PATH.exists():
        print(f"ERROR: Manifest not found: {MANIFEST_PATH}")
        return 1

    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    print("Verifying L2_PROTOCOLS v46 spec integrity...")
    print(f"Manifest version: {manifest.get('version', 'unknown')}")

    mismatches = []
    missing_files = []

    for file_path, expected_hash in manifest['files'].items():
        path = repo_root / file_path
        if not path.exists():
            missing_files.append(file_path)
            print(f"[FAIL] MISSING: {file_path}")
        else:
            actual_hash = compute_sha256(path)
            if actual_hash != expected_hash:
                mismatches.append(file_path)
                print(f"[FAIL] MISMATCH: {file_path}")

    if not mismatches and not missing_files:
        print("[SUCCESS] Integrity verified.")
        return 0
    else:
        print("[FAILURE] Integrity check failed.")
        return 1

def regenerate_manifest():
    """Regenerate manifest with current SHA-256 hashes."""
    files = get_spec_files()

    manifest = {
        'version': 'v46.1',
        'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'description': 'Cryptographic manifest for L2_PROTOCOLS v46.1 (Sovereign Witness)',
        'files': {}
    }

    print("Computing SHA-256 hashes...")
    for file_path in files:
        path = repo_root / file_path
        if path.exists():
            manifest['files'][file_path] = compute_sha256(path)
            print(f"  {file_path} ... OK")
        else:
            print(f"  WARNING: {file_path} NOT FOUND")

    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')

    print(f"\n[SUCCESS] Manifest generated: {MANIFEST_PATH}")
    return 0

def main():
    parser = argparse.ArgumentParser(description='Manage L2_PROTOCOLS v46 manifest')
    parser.add_argument('--check', action='store_true', help='Verify manifest')
    args = parser.parse_args()

    if args.check:
        return check_manifest()
    else:
        return regenerate_manifest()

if __name__ == '__main__':
    sys.exit(main())
