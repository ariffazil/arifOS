#!/usr/bin/env python3
"""
Build and publish script for arifosmcp v2026.3.13-FORGED
Auto-publication to PyPI
"""

import subprocess
import sys
from pathlib import Path


def run(cmd, **kwargs):
    """Run command and return result."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def main():
    repo_root = Path(__file__).parent.parent
    dist_dir = repo_root / "dist"

    # Clean
    print("=== Cleaning previous builds ===")
    if dist_dir.exists():
        import shutil

        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)

    # Build sdist
    print("\n=== Building sdist ===")
    result = run(f"cd {repo_root} && python -m setuptools.build_meta . --sdist --outdir dist")
    if result.returncode != 0:
        # Fallback to python setup.py
        result = run(f"cd {repo_root} && python setup.py sdist --dist-dir dist")

    # Build wheel
    print("\n=== Building wheel ===")
    result = run(f"cd {repo_root} && pip wheel . --no-deps -w dist")

    # Check what was built
    print("\n=== Built artifacts ===")
    artifacts = list(dist_dir.glob("*"))
    for a in artifacts:
        print(f"  {a.name} ({a.stat().st_size} bytes)")

    if not artifacts:
        print("ERROR: No build artifacts found!")
        return 1

    # Verify with twine
    print("\n=== Verifying with twine ===")
    result = run(f"twine check {dist_dir}/*")
    if result.returncode != 0:
        print("WARNING: Twine check failed")

    # Upload to PyPI
    print("\n=== Uploading to PyPI ===")
    result = run(f"twine upload {dist_dir}/*")
    if result.returncode != 0:
        print("ERROR: Upload failed!")
        return 1

    print("\n=== SUCCESS! ===")
    print("Package published to PyPI: arifosmcp==2026.3.13")
    return 0


if __name__ == "__main__":
    sys.exit(main())
