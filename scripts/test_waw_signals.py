"""
test_waw_signals.py - Diagnostic script for W@W Organs.

This script manually invokes @WELL and @GEOX with specific test cases
to verify that:
1. The bridge is being called (even if it returns None).
2. The heuristics are still working (regex checks).
3. The signals are correctly formatted.

Usage:
    python scripts/test_waw_signals.py
"""

from __future__ import annotations

import os
import sys

# Ensure we can import from arifos_core when running from repo root
sys.path.append(os.getcwd())

from arifos_core.metrics import Metrics
from arifos_core.waw.geox import GeoxOrgan
from arifos_core.waw.well import WellOrgan


def print_signal(organ_name, signal) -> None:
    # Encode evidence/tags defensively for Windows consoles
    encoding = sys.stdout.encoding or "utf-8"
    print(f"\n--- {organ_name} SIGNAL ---")
    print(f"Vote: {signal.vote.value}")
    print(f"Metric: {signal.metric_name} = {signal.metric_value:.2f}")
    try:
        evidence_str = str(signal.evidence)
        evidence_safe = evidence_str.encode(encoding, errors="backslashreplace").decode(
            encoding, errors="ignore"
        )
    except Exception:
        evidence_safe = repr(signal.evidence)
    try:
        tags_str = str(signal.tags)
        tags_safe = tags_str.encode(encoding, errors="backslashreplace").decode(
            encoding, errors="ignore"
        )
    except Exception:
        tags_safe = repr(signal.tags)
    print(f"Evidence: {evidence_safe}")
    print(f"Tags: {tags_safe}")
    if signal.proposed_action:
        print(f"Action: {signal.proposed_action}")


def build_baseline_metrics() -> Metrics:
    """Construct a neutral Metrics instance for diagnostics.

    We start from a "healthy" baseline that satisfies all floors so that
    @WELL and @GEOX can apply their own penalties cleanly.
    """
    return Metrics(
        truth=0.99,
        delta_s=0.0,
        peace_squared=1.0,
        kappa_r=1.0,
        omega_0=0.04,
        amanah=True,
        tri_witness=1.0,
    )


def run_diagnostics() -> None:
    print("Initializing W@W Organs...")
    well = WellOrgan()
    geox = GeoxOrgan()

    # Baseline metrics container
    metrics = build_baseline_metrics()

    # Test Case 1: Safe Input
    print("\n>>> TEST 1: 'The sky is blue.' (Safe)")
    sig_well = well.check("The sky is blue.", metrics)
    sig_geox = geox.check("The sky is blue.", metrics)
    print_signal("@WELL", sig_well)
    print_signal("@GEOX", sig_geox)

    # Test Case 2: Toxic Input (@WELL Trigger)
    print("\n>>> TEST 2: 'You are an idiot and I hate you.' (Toxic)")
    sig_well_toxic = well.check("You are an idiot and I hate you.", metrics)
    print_signal("@WELL", sig_well_toxic)

    # Test Case 3: Impossible Input (@GEOX Trigger)
    print("\n>>> TEST 3: 'I can see you in your room right now.' (Physics Violation)")
    sig_geox_impossible = geox.check(
        "I can see you in your room right now.", metrics
    )
    print_signal("@GEOX", sig_geox_impossible)


if __name__ == "__main__":
    run_diagnostics()
