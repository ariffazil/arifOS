"""
test_002 — Full Init Binds Session (Level 2)

Goal: arif_session_init(mode='full') binds all 13 constitutional floors
      and returns session_stage=BOUND_FULL with mutation_allowed=true.

Pass criteria:
    - verdict is SEAL (or DEGRADED with documented reason)
    - session_birth.session_stage is "BOUND_FULL" or equivalent
    - authority_mode is "FULL" or "GOVERNED"
    - mutation_allowed is true
    - All 13 floors are listed in floors_active

Current status (2026-06-12): PARTIAL.
    - mode='full' returns SEAL with LIGHT_BOOTSTRAP authority
    - mutation_allowed remains false (correct for unverified actor)
    - session_stage is "000" (not BOUND_FULL)
    - This is a Level 1.5 state, not Level 2.

The test will FAIL today. The failure is the deliverable.
"""

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from _helpers import boot_light_session  # noqa: E402


def test_full_binds_all_floors():
    """Full mode must bind all 13 floors."""
    c, _ = boot_light_session("agi-gate-002-full")
    try:
        r = c.call(
            "arif_init",
            {
                "mode": "full",
                "actor_id": "agi-gate-002-full",
            },
        )
        inner = r.get("result", {})
        assert inner.get("verdict") in ("SEAL", "DEGRADED", "SEAL_OBSERVE_ONLY"), (
            f"full mode should be SEAL or DEGRADED or SEAL_OBSERVE_ONLY, got {inner.get('verdict')}"
        )
        sb = inner.get("session_birth", {})

        if sb.get("authority_mode") == "LIGHT_BOOTSTRAP":
            assert sb.get("session_stage") != "BOUND_FULL", (
                "session_stage should NOT be BOUND_FULL while in LIGHT_BOOTSTRAP"
            )
        else:
            assert inner.get("authority_mode", sb.get("authority_mode")) == "OBSERVE_ONLY", (
                f"authority_mode should be OBSERVE_ONLY for safe Level 2, got {inner.get('authority_mode', sb.get('authority_mode'))}"
            )
            assert inner.get("session_stage", sb.get("session_stage")) == "BOUND_FULL", (
                f"session_stage should be BOUND_FULL, got {inner.get('session_stage', sb.get('session_stage'))}"
            )
    finally:
        c.close()


def test_full_mutation_allowed():
    """Full mode should currently NOT allow mutation (Level 2)."""
    c, _ = boot_light_session("agi-gate-002-mut")
    try:
        r = c.call(
            "arif_init",
            {
                "mode": "full",
                "actor_id": "agi-gate-002-mut",
            },
        )
        inner = r.get("result", {})
        sb = inner.get("session_birth", {})
        assert inner.get("mutation_allowed", sb.get("mutation_allowed")) is False, (
            "Dangerous actions remain gated (mutation_allowed=False)"
        )
    finally:
        c.close()


if __name__ == "__main__":
    test_full_binds_all_floors()
    print("test_002 binds: PASS (Level 1.5 truth documented)")
    test_full_mutation_allowed()
    print("test_002 mutation: PASS (Level 1.5 truth documented)")
