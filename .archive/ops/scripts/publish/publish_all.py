#!/usr/bin/env python3
"""
Combined PyPI + npm publication script for arifOS v2026.03.17-ANTICHAOS

Usage:
    python publish_all.py --pypi    # Publish to PyPI only
    python publish_all.py --npm     # Publish to npm only
    python publish_all.py --all     # Publish to both (default)
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
DIST_DIR = REPO_ROOT / "dist"
NPM_DIR = REPO_ROOT / "npm" / "arifos-mcp"


def run(cmd, cwd=None, timeout=300, shell=True):
    """Run command and return result."""
    print(f"\n>>> {cmd}")
    result = subprocess.run(
        cmd, shell=shell, cwd=cwd or REPO_ROOT, capture_output=True, text=True, timeout=timeout
    )
    if result.stdout:
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.stderr:
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr, file=sys.stderr)
    return result


def publish_pypi():
    """Publish Python package to PyPI."""
    print("=" * 60)
    print("PYPI PUBLICATION: arifosmcp v2026.03.17-ANTICHAOS")
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
        return False

    # 3. Build wheel
    print("\n[3/5] Building wheel...")
    result = run(f"{sys.executable} setup.py bdist_wheel --dist-dir dist", timeout=120)
    if result.returncode != 0:
        print("ERROR: wheel build failed")
        return False

    # 4. Verify artifacts
    print("\n[4/5] Verifying artifacts...")
    artifacts = list(DIST_DIR.glob("*"))
    if not artifacts:
        print("ERROR: No artifacts found!")
        return False

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
        print("ERROR: PyPI upload failed!")
        return False

    print("\n✅ PyPI publication successful!")
    print("   pip install arifosmcp==2026.3.17")
    return True


def publish_npm():
    """Publish npm package."""
    print("\n" + "=" * 60)
    print("NPM PUBLICATION: @arifos/mcp v2026.3.17")
    print("=" * 60)

    if not NPM_DIR.exists():
        print(f"ERROR: npm directory not found: {NPM_DIR}")
        return False

    # Check npm is installed
    result = run("npm --version", cwd=NPM_DIR, timeout=30)
    if result.returncode != 0:
        print("ERROR: npm not found. Please install Node.js: https://nodejs.org")
        return False

    # Check if already logged in
    print("\n[1/3] Checking npm authentication...")
    result = run("npm whoami", cwd=NPM_DIR, timeout=30)
    if result.returncode != 0:
        print("Not logged in to npm. Please run: npm login")
        login = input("Would you like to login now? (y/n): ")
        if login.lower() == 'y':
            result = run("npm login", cwd=NPM_DIR, timeout=120, shell=False)
            if result.returncode != 0:
                print("ERROR: npm login failed!")
                return False
        else:
            print("ERROR: Cannot publish without npm login")
            return False

    # Install dependencies
    print("\n[2/3] Installing npm dependencies...")
    result = run("npm install", cwd=NPM_DIR, timeout=120)
    if result.returncode != 0:
        print("WARNING: npm install had issues, continuing...")

    # Publish
    print("\n[3/3] Publishing to npm...")
    result = run("npm publish --access public", cwd=NPM_DIR, timeout=120)
    if result.returncode != 0:
        # Check if version already exists
        if "already exists" in result.stderr:
            print("WARNING: Version already published on npm")
            return True
        print("ERROR: npm publish failed!")
        return False

    print("\n✅ npm publication successful!")
    print("   npm install -g @arifos/mcp")
    return True


def main():
    parser = argparse.ArgumentParser(description="Publish arifOS to PyPI and npm")
    parser.add_argument("--pypi", action="store_true", help="Publish to PyPI only")
    parser.add_argument("--npm", action="store_true", help="Publish to npm only")
    parser.add_argument("--all", action="store_true", help="Publish to both (default)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without publishing")
    args = parser.parse_args()

    # Default to --all if no specific target given
    if not args.pypi and not args.npm:
        args.all = True

    print("=" * 60)
    print("arifOS PUBLICATION SCRIPT")
    print("Version: 2026.03.17-ANTICHAOS")
    print("=" * 60)

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No actual publishing will occur")
        if args.all or args.pypi:
            print("   Would publish to PyPI: arifosmcp==2026.3.17")
        if args.all or args.npm:
            print("   Would publish to npm: @arifos/mcp@2026.3.17")
        return 0

    results = []

    # Publish to PyPI
    if args.all or args.pypi:
        try:
            pypi_ok = publish_pypi()
            results.append(("PyPI", pypi_ok))
        except Exception as e:
            print(f"\n❌ PyPI publication failed: {e}")
            results.append(("PyPI", False))

    # Publish to npm
    if args.all or args.npm:
        try:
            npm_ok = publish_npm()
            results.append(("npm", npm_ok))
        except Exception as e:
            print(f"\n❌ npm publication failed: {e}")
            results.append(("npm", False))

    # Summary
    print("\n" + "=" * 60)
    print("PUBLICATION SUMMARY")
    print("=" * 60)

    for name, ok in results:
        status = "✅ SUCCESS" if ok else "❌ FAILED"
        print(f"  {name}: {status}")

    all_ok = all(ok for _, ok in results)

    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 ALL PUBLICATIONS SUCCESSFUL!")
        print("\nInstallation:")
        if args.all or args.pypi:
            print("  pip install arifosmcp==2026.3.17")
        if args.all or args.npm:
            print("  npm install -g @arifos/mcp@2026.3.17")
    else:
        print("⚠️  SOME PUBLICATIONS FAILED")
    print("=" * 60)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
