"""
ART verdict — reflex decision enum and reason codes.

Extracted from runtime/art.py.

DITEMPA BUKAN DIBERI — Verdict is forged, not configured.
"""

from __future__ import annotations
from enum import StrEnum


class ArtVerdict(StrEnum):
    """What ART decides."""
    PROCEED = "proceed"                # green — call tool
    HOLD = "hold"                      # yellow — ask Arif or delay
    BLOCK = "block"                    # red — cannot call
    DEFAULT_OBSERVE = "observe_only"   # not enough info — observe only


class ArtReason(StrEnum):
    """Why ART reached this verdict."""
    # State-based
    TOOL_ABANDONED = "tool abandoned — blocked"
    TOOL_FALLBACK = "tool in fallback — hold until re-verified"
    TOOL_UNTRUSTED = "tool untrusted — observe only"
    TOOL_OBSERVED_MUTATE = "tool observed — propose only for mutate"
    TOOL_OBSERVED_EXECUTE = "tool observed — cannot execute"

    # Check 1: Power
    BLAST_RADIUS_UNKNOWN = "blast radius unknown — default observe"
    IRREVERSIBLE_NO_ROLLBACK = "irreversible action without rollback"
    EXECUTE_NEEDS_ACK = "execute action always needs ack"
    EXTERNAL_SURFACE_UNACKNOWLEDGED = "mutate on external surface without ack — hold"

    # Check 2: Trust
    ACTOR_UNRESOLVED = "non-observe action without resolved actor"
    TRUST_LEVEL_UNKNOWN = "trust level unknown — default observe"
    VERDICT_WITHOUT_SCHEMA = "tool returns verdict but schema unverified"
    UNVERIFIED_SCHEMA_SOURCE = "schema source unverified — default observe"

    # Check 3: System
    DEGRADED_MUTATION = "system degraded — cannot mutate"
    FAILURE_RATE_HIGH = "failure rate exceeds threshold — fallback suggested"
    DRIFT_DETECTED = "schema/permission drift detected — fallback suggested"
    CUMULATIVE_SILENT_FALLBACK = "cumulative silent fallback detected — hold"

    # Abandonment
    TOOL_STALE = "tool unused >90 days — abandon candidate"

    # All clear
    ALL_CHECKS_PASSED = "all checks passed — proceed"
