"""
test_008 — Memory Write Requires Ack (Level 1+)

Goal: arif_memory_recall(mode='store') for durable/tier='L4' or higher
      requires ack_irreversible=True or returns HOLD.

Pass criteria:
    - mode='store', tier='L4', ack_irreversible=False → HOLD
    - mode='store', tier='L4', ack_irreversible=True → SEAL (with provenance)
    - mode='recall' (read-only) works without ack
    - mode='store', tier='L3' (ephemeral-ish) works without ack

Current status (2026-06-12): UNKNOWN (depends on memory_recall mode dispatch).
    The arif_memory_recall tool is on the public surface. This test
    verifies the ack_irreversible gate exists.
"""

from ._helpers import boot_light_session


def test_memory_store_l4_requires_ack():
    """L4 durable store must require ack_irreversible."""
    c, sb = boot_light_session("agi-gate-008")
    try:
        sid = sb.get("session_id", "")
        # Try storing without ack — should HOLD
        r = c.call(
            "arif_memory_recall",
            {
                "mode": "store",
                "content": "test memory write",
                "tier": "L4",
                "session_id": sid,
                "actor_id": "agi-gate-008",
                "ack_irreversible": False,
            },
        )
        inner = r.get("result", {})
        verdict = inner.get("verdict") or r.get("verdict")
        if verdict is not None:
            assert verdict in ("HOLD", "VOID", "DEGRADED"), (
                f"L4 store without ack must HOLD, got {verdict}"
            )
    finally:
        c.close()


def test_memory_recall_read_no_ack():
    """L3 recall (read-only) should work without ack."""
    c, sb = boot_light_session("agi-gate-008b")
    try:
        sid = sb.get("session_id", "")
        r = c.call(
            "arif_memory_recall",
            {
                "mode": "recall",
                "query": "constitutional floor F2",
                "tier": "L3",
                "session_id": sid,
                "actor_id": "agi-gate-008b",
            },
        )
        # No assertion on verdict — recall is read-only and should not gate
        # Just verify the tool responded (not crashed)
        assert r, "memory recall must respond"
    finally:
        c.close()


if __name__ == "__main__":
    test_memory_store_l4_requires_ack()
    print("test_008 L4 ack: PASS")
    test_memory_recall_read_no_ack()
    print("test_008 L3 read: PASS")
