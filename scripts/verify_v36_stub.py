"""
verify_v36_stub.py - Dry-run verification for v36Ω Cooling Ledger stub.

Purpose:
- Exercise log_cooling_entry_v36_stub with dummy Metrics and GeniusVerdict-like
  metadata, without touching the live v35Ic Cooling Ledger.
- Confirm that:
  - ledger_version is "v36Omega"
  - metrics.truth_polarity is present and populated

Usage:
    python scripts/verify_v36_stub.py
"""

from __future__ import annotations

import json

from arifos_core.memory.cooling_ledger import log_cooling_entry_v36_stub
from arifos_core.metrics import Metrics


class DummyGeniusVerdict:
    """Minimal stand-in carrying Truth Polarity metadata.

    In real usage, this would be arifos_core.genius_metrics.GeniusVerdict.
    For this dry run, we only need the truth_polarity field.
    """

    def __init__(self, truth_polarity: str) -> None:
        self.truth_polarity = truth_polarity


def run_verification() -> None:
    print(">>> INITIATING V36 STUB VERIFICATION <<<\n")

    # 1. Create Metrics (simulation of a healthy verdict state)
    mock_metrics = Metrics(
        truth=0.998,
        delta_s=0.0,
        peace_squared=1.12,  # Peace²
        kappa_r=0.96,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.97,
        rasa=True,
    )

    # 2. Simulate a GeniusVerdict payload (Truth Polarity metadata)
    # Canonical values from genius_metrics are: truth_light, shadow_truth,
    # weaponized_truth, false_claim. We use "truth_light" for this dry run.
    mock_genius_verdict = DummyGeniusVerdict(truth_polarity="truth_light")

    # 3. Call the v36Ω stub (no disk write)
    entry = log_cooling_entry_v36_stub(
        job_id="TEST-GENESIS-V36",
        verdict="SEAL",
        metrics=mock_metrics,
        query_hash="hash_query_123",
        response_hash="hash_response_456",
        genius_verdict=mock_genius_verdict,
    )

    # 4. Inspect the artifact
    print(json.dumps(entry, indent=2, default=str))

    # 5. Validation logic
    tp = entry.get("metrics", {}).get("truth_polarity")
    if tp:
        print(f"\n[PASS] Truth Polarity successfully encoded: {tp!r}.")
    else:
        print("\n[FAIL] Truth Polarity missing or empty in metrics.")

    if entry.get("ledger_version") == "v36Omega":
        print("[PASS] Ledger Version identifies as v36Omega.")
    else:
        print(f"[FAIL] Incorrect Ledger Version: {entry.get('ledger_version')!r}.")


if __name__ == "__main__":
    run_verification()
