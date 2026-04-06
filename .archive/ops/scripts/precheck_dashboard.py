#!/usr/bin/env python3
"""
precheck_dashboard.py — Build artifact validation for arifOS Dashboard.
Ensures test-reports/index.html is valid before Cloudflare deployment.
"""

import sys
from pathlib import Path


def verify_dashboard():
    report_dir = Path("test-reports")
    report_file = report_dir / "index.html"

    print(f"🔍 Validating build artifact: {report_file}")

    if not report_dir.exists():
        print(f"❌ ERROR: Directory '{report_dir}' does not exist.")
        return False

    if not report_file.exists():
        print(f"❌ ERROR: '{report_file}' not found. Dashboard generation failed.")
        return False

    # Verify APEX Dashboard Sub-route
    apex_file = report_dir / "dashboard" / "index.html"
    print(f"🔍 Validating APEX artifact: {apex_file}")
    if not apex_file.exists():
        print(f"❌ ERROR: '{apex_file}' not found. APEX Sub-dashboard copy failed.")
        return False

    size = report_file.stat().st_size
    if size < 1024:  # Minimum 1KB for a valid dashboard
        print(f"❌ ERROR: '{report_file}' is too small ({size} bytes). Likely corrupted.")
        return False

    print(f"✅ Dashboard verified: {size} bytes. Ready for deployment.")
    return True


if __name__ == "__main__":
    if not verify_dashboard():
        sys.exit(1)
    sys.exit(0)
