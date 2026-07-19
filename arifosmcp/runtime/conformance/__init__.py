"""
PR7 — Conformance runner.

Honest three-level conformance per audit-4. The previous "9/9 GREEN while
live checks skipped" failure mode is structurally impossible here: any
skipped check forces the substrate_gate to AMBER and the verdict to
UNVERIFIED (for FULL_CONFORMANCE).

Future work: replace the default placeholder checks with real probes
that hit the live runtime. The substrate gate semantics do not change.
"""

from .levels import (
    CheckResult,
    ConformanceReport,
    FastVerdict,
    FullVerdict,
    LiveVerdict,
    SubstrateGate,
    run_fast,
    run_live_transport,
    run_full,
)

__all__ = [
    "CheckResult",
    "ConformanceReport",
    "FastVerdict",
    "FullVerdict",
    "LiveVerdict",
    "SubstrateGate",
    "run_fast",
    "run_live_transport",
    "run_full",
]
