"""
arifos_core.spec.manifest_verifier - Cryptographic Manifest Verification

Provides SHA-256 manifest verification for Track B v44 specifications.
Ensures tamper-evident integrity at load-time (fail-closed).

Usage:
    verify_manifest(repo_root, manifest_path, allow_legacy=False)

Behavior:
- If manifest missing and allow_legacy=False → RuntimeError (fail-closed)
- If file hash mismatch → RuntimeError with specific file details
- If all hashes match → Returns silently (verification passed)

NO external dependencies beyond stdlib (uses hashlib for SHA-256).
NO imports from arifos_core.utils (avoids circular dependencies).
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple


def compute_sha256(file_path: Path) -> str:
    """
    Compute SHA-256 hex digest of a file.

    Args:
        file_path: Path to file to hash

    Returns:
        Lowercase hex digest (64 characters)
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_manifest(manifest_path: Path) -> dict:
    """
    Load cryptographic manifest from JSON file.

    Args:
        manifest_path: Path to MANIFEST.sha256.json

    Returns:
        Manifest dictionary with 'files' key mapping paths to SHA-256 hashes

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        json.JSONDecodeError: If manifest is invalid JSON
        ValueError: If manifest missing required keys
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    # Validate manifest structure
    if 'files' not in manifest:
        raise ValueError(f"Invalid manifest: missing 'files' key in {manifest_path}")

    if 'version' not in manifest:
        raise ValueError(f"Invalid manifest: missing 'version' key in {manifest_path}")

    return manifest


def verify_file_hash(repo_root: Path, relative_path: str, expected_hash: str) -> Tuple[bool, str]:
    """
    Verify a single file's SHA-256 hash against expected value.

    Args:
        repo_root: Repository root directory
        relative_path: Relative path from repo root (e.g., "spec/v45/constitutional_floors.json")
        expected_hash: Expected SHA-256 hex digest

    Returns:
        Tuple of (is_valid, actual_hash)
    """
    file_path = repo_root / relative_path

    if not file_path.exists():
        return False, "FILE_MISSING"

    actual_hash = compute_sha256(file_path)
    is_valid = actual_hash == expected_hash

    return is_valid, actual_hash


def verify_manifest(
    repo_root: Path,
    manifest_path: Path,
    allow_legacy: bool = False
) -> None:
    """
    Verify Track B specs against cryptographic manifest (fail-closed).

    Args:
        repo_root: Repository root directory
        manifest_path: Path to MANIFEST.sha256.json
        allow_legacy: If True, skip verification if manifest missing (NOT RECOMMENDED)

    Raises:
        RuntimeError: If verification fails (manifest missing, file missing, hash mismatch)

    Side Effects:
        None (pure verification, no state modification)
    """
    # Legacy mode: skip all verification
    if allow_legacy:
        return

    # Check if manifest exists
    if not manifest_path.exists():
        # Fail-closed: manifest must exist
        raise RuntimeError(
            f"TRACK B AUTHORITY FAILURE: Cryptographic manifest not found: {manifest_path}. "
            f"Manifest verification is required for spec integrity. "
            f"Set ARIFOS_ALLOW_LEGACY_SPEC=1 to disable (NOT RECOMMENDED)."
        )

    # Load manifest
    try:
        manifest = load_manifest(manifest_path)
    except Exception as e:
        raise RuntimeError(
            f"TRACK B AUTHORITY FAILURE: Failed to load manifest {manifest_path}: {e}"
        )

    # Verify all files in manifest
    mismatches: List[Tuple[str, str, str]] = []  # (path, expected, actual)
    missing_files: List[str] = []

    for relative_path, expected_hash in manifest['files'].items():
        is_valid, actual_hash = verify_file_hash(repo_root, relative_path, expected_hash)

        if not is_valid:
            if actual_hash == "FILE_MISSING":
                missing_files.append(relative_path)
            else:
                mismatches.append((relative_path, expected_hash, actual_hash))

    # Report errors (fail-closed)
    if missing_files or mismatches:
        error_lines = ["TRACK B AUTHORITY FAILURE: Manifest verification failed."]

        if missing_files:
            error_lines.append(f"\nMissing files ({len(missing_files)}):")
            for path in missing_files:
                error_lines.append(f"  - {path}")

        if mismatches:
            error_lines.append(f"\nHash mismatches ({len(mismatches)}) - FILES HAVE BEEN TAMPERED:")
            for path, expected, actual in mismatches:
                error_lines.append(f"  - {path}")
                error_lines.append(f"    Expected: {expected}")
                error_lines.append(f"    Actual:   {actual}")

        error_lines.append("\nTo fix:")
        error_lines.append("  1. Restore original files from git")
        error_lines.append("  2. Or regenerate manifest: python -m arifos_core.spec.regenerate_manifest")
        error_lines.append("  3. Or bypass (NOT RECOMMENDED): set ARIFOS_ALLOW_LEGACY_SPEC=1")

        raise RuntimeError("\n".join(error_lines))

    # All hashes verified - silent success (fail-closed validated)
