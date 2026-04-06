#!/usr/bin/env python3
"""
Automated PyPI publication script for arifosmcp v2026.3.13-FORGED
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent
DIST_DIR = REPO_ROOT / "dist"


def run(cmd, cwd=None, timeout=300):
    """Run command and return result."""
    print(f"\n>>> {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or REPO_ROOT, capture_output=True, text=True, timeout=timeout
    )
    if result.stdout:
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.stderr:
        print(
            result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr, file=sys.stderr
        )
    return result


def main():
    print("=" * 60)
    print("PYPI PUBLICATION: arifosmcp v2026.3.13-FORGED")
    print("=" * 60)

    # 1. Clean
    print("\n[1/5] Cleaning dist folder...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(exist_ok=True)

    # 2. Build sdist
    print("\n[2/5] Building sdist...")
    result = run(f"{sys.executable} setup.py sdist --dist-dir dist", timeout=120)
    if result.returncode != 0:
        print("ERROR: sdist build failed")
        return 1

    # 3. Build wheel
    print("\n[3/5] Building wheel...")
    result = run(f"{sys.executable} setup.py bdist_wheel --dist-dir dist", timeout=120)
    if result.returncode != 0:
        print("ERROR: wheel build failed")
        return 1

    # 4. Verify artifacts
    print("\n[4/5] Verifying artifacts...")
    artifacts = list(DIST_DIR.glob("*"))
    if not artifacts:
        print("ERROR: No artifacts found!")
        return 1

    for a in artifacts:
        size = a.stat().st_size / 1024  # KB
        print(f"  ✓ {a.name} ({size:.1f} KB)")

    # 5. Verify with twine
    print("\n[5/5] Verifying with twine...")
    result = run("twine check dist/*", timeout=30)
    if result.returncode != 0:
        print("WARNING: Twine check had issues, proceeding anyway...")

    # 6. Upload to PyPI
    print("\n" + "=" * 60)
    print("UPLOADING TO PYPI...")
    print("=" * 60)
    result = run("twine upload dist/*", timeout=120)
    if result.returncode != 0:
        print("ERROR: Upload failed!")
        return 1

    print("\n" + "=" * 60)
    print("SUCCESS! Package published to PyPI")
    print("pip install arifosmcp==2026.3.13")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
