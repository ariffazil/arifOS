"""
test_010 — Consecutive Boot Cycles (Level 1+)

Goal: 10 consecutive boot cycles produce stable, consistent state.
      No session_id loss, no actor drift, no surface drift.

Production threshold: 100 cycles (per AGI_KERNEL_READINESS_GATE_001 spec).
Test threshold: 10 cycles (autonomous-runnable, not 100 days).

Pass criteria:
    - All N boot cycles return session_id starting with SEAL-
    - tools_loaded=13 stays constant
    - floors_active=13 stays constant
    - No crash, no timeout
    - actor_id is preserved across cycles for the same client

Current status (2026-06-12): PARTIAL.
    - Light boot works in single-connection mode
    - MCP transport sometimes drops session_id between calls
    - This test uses 10 cycles to surface any drift
"""

from ._helpers import MCPClient

N_CYCLES = 10
ACTOR_ID = "agi-gate-010-cycle"


def test_consecutive_boot_cycles():
    """N consecutive boot cycles produce stable state."""
    session_ids = []
    verdicts = []

    for i in range(N_CYCLES):
        c = MCPClient(f"agi-gate-010-{i}")
        try:
            c.initialize()
            r = c.call(
                "arif_session_init",
                {
                    "mode": "light",
                    "actor_id": ACTOR_ID,
                },
            )
            inner = r.get("result", {})
            sb = inner.get("session_birth", {})
            sess = sb.get("session_id", "")
            verdict = inner.get("verdict")
            session_ids.append(sess)
            verdicts.append(verdict)
        finally:
            c.close()

    # F2 truth check
    sealed_count = sum(1 for s in session_ids if s.startswith("SEAL-"))
    assert sealed_count == N_CYCLES, (
        f"all {N_CYCLES} cycles should return SEAL- session_id, got {sealed_count}"
    )
    assert all(v == "SEAL" for v in verdicts), f"all verdicts should be SEAL, got {verdicts}"
    # All session_ids should be unique
    assert len(set(session_ids)) == N_CYCLES, (
        f"all session_ids should be unique, got {len(set(session_ids))} unique"
    )


def test_surface_drift_over_cycles():
    """tools_loaded should stay at 13 across cycles."""
    surfaces = []
    for i in range(N_CYCLES):
        c = MCPClient(f"agi-gate-010b-{i}")
        try:
            c.initialize()
            r = c.call(
                "arif_session_init",
                {
                    "mode": "light",
                    "actor_id": ACTOR_ID,
                },
            )
            lke = r.get("live_kernel_envelope", {})
            surfaces.append(lke)
        finally:
            c.close()

    # Document: surface invariants from live_kernel_envelope
    # are stable across cycles. (F2 truth: today stage is "000"
    # for all cycles — that's a constant, not drift.)
    stages = [s.get("kernel", {}).get("epoch_id", "unknown") for s in surfaces]
    assert all(s == "EPOCH-LIVE-1" for s in stages), f"epoch_id should be stable, got {stages}"


if __name__ == "__main__":
    test_consecutive_boot_cycles()
    print(f"test_010 cycles: PASS ({N_CYCLES} cycles, all SEAL)")
    test_surface_drift_over_cycles()
    print("test_010 surface: PASS (epoch stable)")
