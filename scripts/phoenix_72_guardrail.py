#!/usr/bin/env python3
"""
Phoenix-72 Guardrail: Constitutional Drift & Entropy Detector
==============================================================

Enforces two invariants:
1. THRESHOLD SOVEREIGNTY: No hardcoded constitutional thresholds (spec is authority)
2. ENTROPY CONSTRAINT: Delta_S_new + Delta_S_existing <= 0 (net LOC cannot grow without justification)

Usage:
    # Run both checks
    python scripts/phoenix_72_guardrail.py

    # Run specific check
    python scripts/phoenix_72_guardrail.py --check thresholds
    python scripts/phoenix_72_guardrail.py --check entropy

    # Update baseline (after approved growth)
    python scripts/phoenix_72_guardrail.py --update-baseline

    # Run in warn mode (prints violations, exit 0)
    python scripts/phoenix_72_guardrail.py --mode warn

    # Run in strict mode (exit 1 on violations)
    python scripts/phoenix_72_guardrail.py --mode strict

Exit codes:
    0: All checks pass (or warn mode)
    1: Threshold drift detected (strict mode)
    2: Entropy growth without justification (strict mode)
    3: Both violations (strict mode)

Configuration:
    .phoenix_config.json - Optional config file for mode defaults
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Set

# =============================================================================
# Configuration
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[1]
ARIFOS_CORE = REPO_ROOT / "arifos_core"
BASELINE_FILE = REPO_ROOT / ".phoenix_baseline.json"
JUSTIFICATION_FILE = REPO_ROOT / ".phoenix_justifications.json"
CONFIG_FILE = REPO_ROOT / ".phoenix_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "threshold_mode": "warn",  # "warn" or "strict"
    "entropy_mode": "strict",  # "warn" or "strict"
    "target_violation_max": 50,
    "deadline": "2026-01-15"
}

# Constitutional thresholds that must ONLY appear via spec imports
CONSTITUTIONAL_THRESHOLDS = {
    0.99: "F2 Truth SEAL threshold (spec/v44/constitutional_floors.json:20)",
    0.95: "F3 Tri-Witness, F6 kappa_r threshold (spec/v44/constitutional_floors.json:59,135)",
    0.90: "Truth hallucination block (TRUTH_BLOCK_MIN)",
    0.80: "F8 G SEAL threshold (spec/v44/genius_law.json:22)",
    0.50: "F8 G MIN threshold (spec/v44/genius_law.json:23)",
    0.30: "F9 C_dark SEAL threshold (spec/v44/genius_law.json:43)",
    0.60: "F9 C_dark PARTIAL threshold (spec/v44/genius_law.json:44)",
    0.05: "F7 Omega0 upper band (spec/v44/constitutional_floors.json:73)",
    0.03: "F7 Omega0 lower band (spec/v44/constitutional_floors.json:72)",
    1.0: "F5 Peace-squared threshold (spec/v44/constitutional_floors.json:46)",
}

# Patterns indicating spec-aligned constants (ALLOWED)
ALLOWED_PATTERNS = [
    r"TRUTH_MIN\s*=\s*TRUTH_THRESHOLD",  # Import from metrics
    r"from.*spec.*import",  # Spec loader imports
    r"load.*spec.*json",  # Dynamic spec loading
    r"# spec/v\d+/",  # Explicit spec anchor comment
    r"@LAW audit",  # Audit-approved constant
    r"# v\d+Ω.*spec",  # Version-tagged spec reference
    r"=\s*(TRUTH_|KAPPA_|TRI_|PEACE_|G_|C_DARK_|OMEGA_)",  # Import from constant
    r"\"threshold\":\s*",  # JSON spec file itself
    r"assert.*==",  # Test assertion
    r"truth=0\.",  # Test fixture data
    r"kappa_r=0\.",  # Test fixture data
    r"tri_witness=0\.",  # Test fixture data
]

# Files/directories to exclude from threshold scan
EXCLUDE_PATHS = {
    "tests/",
    "__pycache__/",
    ".venv/",
    "archive/",
    ".git/",
    "spec/",  # Spec files define thresholds
    "docs/",  # Documentation can reference thresholds
    "scripts/",  # Scripts can reference thresholds for checks
}

# =============================================================================
# Configuration Loading
# =============================================================================

def load_config() -> Dict:
    """Load Phoenix-72 configuration from file or use defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Merge with defaults
                return {**DEFAULT_CONFIG, **config}
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


# =============================================================================
# Threshold Drift Detector
# =============================================================================

def is_in_string_literal(line: str, position: int) -> bool:
    """Check if position in line is inside a string literal."""
    # Count quotes before position
    before = line[:position]
    single_quotes = before.count("'") - before.count("\\'")
    double_quotes = before.count('"') - before.count('\\"')

    # If odd number of quotes, we're inside a string
    return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)


def scan_for_hardcoded_thresholds() -> List[Tuple[str, int, float, str]]:
    """
    Scan arifos_core/ for hardcoded constitutional thresholds.

    Skips:
    - Multi-line docstrings
    - String literals
    - Comments
    - Test fixture data

    Returns:
        List of (file_path, line_num, threshold_value, context_line)
    """
    violations = []

    for py_file in ARIFOS_CORE.rglob("*.py"):
        # Skip excluded paths
        if any(excl in str(py_file) for excl in EXCLUDE_PATHS):
            continue

        # Skip __init__.py (public API helpers, not enforcement logic)
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except Exception:
            continue

        in_docstring = False
        docstring_marker = None

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Track multi-line docstrings
            if '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    # Starting docstring
                    if stripped.count('"""') == 1:
                        in_docstring = True
                        docstring_marker = '"""'
                    elif stripped.count("'''") == 1:
                        in_docstring = True
                        docstring_marker = "'''"
                else:
                    # Ending docstring
                    if docstring_marker in stripped:
                        in_docstring = False
                        docstring_marker = None
                continue

            # Skip if inside docstring
            if in_docstring:
                continue

            # Skip pure comment lines
            if stripped.startswith("#"):
                continue

            # Check if line is allowed (spec reference)
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in ALLOWED_PATTERNS):
                continue

            # Scan for threshold literals
            for threshold, description in CONSTITUTIONAL_THRESHOLDS.items():
                # Match threshold as standalone number
                pattern = r'\b' + str(threshold) + r'\b'
                matches = list(re.finditer(pattern, line))

                for match in matches:
                    position = match.start()

                    # Skip if in string literal
                    if is_in_string_literal(line, position):
                        continue

                    # Skip if in end-of-line comment
                    if '#' in line:
                        comment_pos = line.find('#')
                        if position > comment_pos:
                            continue

                    # Found a real violation
                    rel_path = py_file.relative_to(REPO_ROOT)
                    violations.append((str(rel_path), line_num, threshold, line.rstrip()))
                    break  # One violation per line

    return violations


def report_threshold_violations(violations: List[Tuple[str, int, float, str]], mode: str = "strict") -> bool:
    """
    Print threshold violations and return True if any found.

    Args:
        violations: List of (file_path, line_num, threshold, context)
        mode: "strict" (exit 1) or "warn" (exit 0)
    """
    if not violations:
        print("[OK] THRESHOLD SOVEREIGNTY: No hardcoded thresholds detected")
        return False

    # Count by file
    file_counts = {}
    for file_path, _, _, _ in violations:
        file_counts[file_path] = file_counts.get(file_path, 0) + 1

    # Sort by count
    top_offenders = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)

    if mode == "warn":
        print(f"[WARN] THRESHOLD DRIFT: {len(violations)} violations (warn mode)")
    else:
        print(f"[ERROR] THRESHOLD DRIFT DETECTED: {len(violations)} violations")

    print("\nConstitutional thresholds must be imported from spec-loaded modules.")
    print("See: spec/v44/constitutional_floors.json, spec/v44/genius_law.json")

    print(f"\nTop 10 offenders:")
    for file_path, count in top_offenders[:10]:
        print(f"  {file_path}: {count} violations")

    print(f"\nShowing first 10 violations (total: {len(violations)}):")
    for file_path, line_num, threshold, context in violations[:10]:
        desc = CONSTITUTIONAL_THRESHOLDS.get(threshold, "Unknown threshold")
        print(f"\n  {file_path}:{line_num}")
        print(f"    Threshold: {threshold} ({desc})")
        # Windows-safe context print (replace non-ASCII chars)
        safe_context = context[:80].encode('ascii', 'replace').decode('ascii')
        print(f"    Line: {safe_context}")

    print("\nFix: Import from spec-loaded constants or add spec anchor comment:")
    print("  # spec/v44/constitutional_floors.json:20 (F2 Truth)")

    if mode == "warn":
        print("\n[WARN] Running in WARN mode - violations reported but not blocking")
        return False  # Don't block in warn mode

    return True  # Block in strict mode


# =============================================================================
# Entropy Growth Detector
# =============================================================================

def count_loc(directory: Path) -> int:
    """Count non-comment, non-blank lines of code in Python files."""
    total = 0

    for py_file in directory.rglob("*.py"):
        # Skip excluded paths
        if any(excl in str(py_file) for excl in EXCLUDE_PATHS):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            continue

        for line in lines:
            stripped = line.strip()
            # Skip blank lines and pure comment lines
            if stripped and not stripped.startswith("#"):
                # Skip docstring lines (rough heuristic)
                if not (stripped.startswith('"""') or stripped.startswith("'''")):
                    total += 1

    return total


def load_baseline() -> Dict:
    """Load baseline LOC from file."""
    if not BASELINE_FILE.exists():
        return {"loc": 0, "date": "never"}

    with open(BASELINE_FILE, "r") as f:
        return json.load(f)


def save_baseline(loc: int):
    """Save current LOC as baseline."""
    from datetime import datetime
    baseline = {
        "loc": loc,
        "date": datetime.now().isoformat(),
        "note": "Phoenix-72 entropy baseline"
    }
    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=2)
    print(f"[OK] Baseline updated: {loc} LOC")


def load_justifications() -> List[Dict]:
    """Load entropy growth justifications."""
    if not JUSTIFICATION_FILE.exists():
        return []

    with open(JUSTIFICATION_FILE, "r") as f:
        return json.load(f)


def check_entropy_growth(current_loc: int, baseline_loc: int) -> Tuple[bool, int]:
    """
    Check if entropy growth is justified.

    Returns:
        (is_justified, delta_loc)
    """
    delta = current_loc - baseline_loc

    if delta <= 0:
        # LOC decreased or stayed same - always good
        return True, delta

    # LOC increased - check justifications
    justifications = load_justifications()
    total_justified = sum(j.get("delta_loc", 0) for j in justifications)

    return total_justified >= delta, delta


def report_entropy_violation(current: int, baseline: int, delta: int) -> bool:
    """Print entropy violation and return True if violation found."""
    is_justified, _ = check_entropy_growth(current, baseline)

    if is_justified:
        if delta > 0:
            print(f"[OK] ENTROPY CONSTRAINT: Growth justified (+{delta} LOC)")
        else:
            print(f"[OK] ENTROPY CONSTRAINT: LOC decreased ({delta} LOC)")
        return False

    print(f"[ERROR] ENTROPY GROWTH DETECTED: +{delta} LOC without justification")
    print(f"\n  Baseline: {baseline} LOC")
    print(f"  Current:  {current} LOC")
    print(f"  Delta:    +{delta} LOC")
    print("\nPhoenix-72 Constraint: ΔS_new + ΔS_existing ≤ 0")
    print("\nTo fix, either:")
    print("  1. Remove equivalent LOC elsewhere in arifos_core/")
    print("  2. Add justification to .phoenix_justifications.json:")
    print('     [{"date": "2025-12-26", "delta_loc": %d, "reason": "...", "approved_by": "human"}]' % delta)
    print("  3. Run: python scripts/phoenix_72_guardrail.py --update-baseline")

    return True


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Phoenix-72 Guardrail: Drift & Entropy Detector")
    parser.add_argument(
        "--check",
        choices=["thresholds", "entropy", "all"],
        default="all",
        help="Which check to run (default: all)"
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Update LOC baseline to current value"
    )
    parser.add_argument(
        "--mode",
        choices=["warn", "strict"],
        help="Enforcement mode: 'warn' (report only) or 'strict' (block on violations). Defaults from .phoenix_config.json"
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Determine effective modes (CLI args override config)
    threshold_mode = args.mode or config.get("threshold_mode", "strict")
    entropy_mode = config.get("entropy_mode", "strict")  # Always strict for now

    exit_code = 0

    if args.update_baseline:
        current_loc = count_loc(ARIFOS_CORE)
        save_baseline(current_loc)
        return 0

    print("=" * 80)
    print("  Phoenix-72 Guardrail: Constitutional Drift & Entropy Detector")
    print("=" * 80)
    print()

    # Check 1: Threshold Drift
    if args.check in {"thresholds", "all"}:
        print("[1/2] Scanning for hardcoded thresholds...")
        violations = scan_for_hardcoded_thresholds()
        if report_threshold_violations(violations, mode=threshold_mode):
            exit_code |= 1
        print()

    # Check 2: Entropy Growth
    if args.check in {"entropy", "all"}:
        print("[2/2] Checking entropy constraint (Delta_S <= 0)...")
        current_loc = count_loc(ARIFOS_CORE)
        baseline = load_baseline()
        baseline_loc = baseline.get("loc", current_loc)  # First run: use current as baseline

        delta = current_loc - baseline_loc
        if report_entropy_violation(current_loc, baseline_loc, delta):
            exit_code |= 2
        print()

    # Summary
    print("=" * 80)
    if exit_code == 0:
        print("  [SEAL] All Phoenix-72 constraints satisfied")
    elif exit_code == 1:
        print("  [VOID] Threshold drift detected")
    elif exit_code == 2:
        print("  [VOID] Entropy growth unjustified")
    elif exit_code == 3:
        print("  [VOID] Threshold drift + Entropy growth")
    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
