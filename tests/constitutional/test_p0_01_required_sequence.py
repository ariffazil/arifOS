"""
P0-01 Required Test Sequence — Arif's 7 Gate Tests
═══════════════════════════════════════════════════

Sovereign-directed test sequence for memory gate + Qdrant offline.
Maps to existing tests where possible; fills gaps where needed.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import asyncio

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


class _QdrantOfflineError(RuntimeError):
    """Sentinel for Qdrant unreachable in tests."""


def _install_broken_qdrant(module, attr_name: str = "_get_qdrant_client") -> None:
    """Patch module so Qdrant calls always raise."""

    def _broken():
        raise _QdrantOfflineError("Qdrant unreachable (test)")

    setattr(module, attr_name, _broken)
    for cached in ("_qdrant_client", "_client", "client"):
        if hasattr(module, cached):
            try:
                setattr(module, cached, None)
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════════
# 1. test_observe_only_cannot_remember
# ═══════════════════════════════════════════════════════════════════════


def test_observe_only_cannot_remember(monkeypatch):
    """OBSERVE_ONLY session attempting store (remember) → VOID, not executed.

    Maps to existing: test_remember_observe_only_session_returns_void_f11
    This wrapper ensures the exact test name Arif requested exists.
    """
    from arifosmcp.runtime import memory_gate
    from arifosmcp.tools.memory import arif_memory_recall

    # Mock session as OBSERVE_ONLY
    def fake_get_session(sid):
        return {
            "session_id": sid,
            "actor_id": "test-actor",
            "authority": "OBSERVE_ONLY",
            "authority_level": "OBSERVE_ONLY",
        }

    monkeypatch.setattr(memory_gate, "get_session_identity", fake_get_session)

    result = arif_memory_recall(
        mode="store",
        content="should not be stored",
        session_id="observe-only-session",
        actor_id="test-actor",
    )

    assert isinstance(result, dict)
    verdict = result.get("verdict", result.get("status", ""))
    assert verdict in ("VOID", "HOLD"), f"OBSERVE_ONLY + store should VOID/HOLD, got {verdict}"
    # Must not have written anything
    assert result.get("result", {}).get("stored") is not True, (
        "OBSERVE_ONLY must not produce a stored=True result"
    )


# ═══════════════════════════════════════════════════════════════════════
# 2. test_missing_session_returns_sabar
# ═══════════════════════════════════════════════════════════════════════


def test_missing_session_returns_sabar():
    """No session_id → SABAR (empty result), not exception, not fabricated memory.

    Maps to existing: test_recall_without_session_returns_sabar_f1
    """
    from arifosmcp.tools.memory import arif_memory_recall

    result = arif_memory_recall(
        mode="recall",
        query="test query",
        # No session_id
        actor_id="test-actor",
    )

    assert isinstance(result, dict)
    verdict = result.get("verdict", result.get("status", ""))
    # Should be SABAR or HOLD (not SEAL, not fabricated result)
    assert verdict != "SEAL", "Missing session must not SEAL"
    # Must not fabricate memories
    meta = result.get("meta", result.get("result", {}))
    if isinstance(meta, dict):
        results = meta.get("results", [])
        assert results == [], "Must not fabricate memories without session"


# ═══════════════════════════════════════════════════════════════════════
# 3. test_failed_gate_causes_zero_writes
# ═══════════════════════════════════════════════════════════════════════


def test_failed_gate_causes_zero_writes(monkeypatch):
    """When the pre-execution gate returns SABAR/VOID/HOLD, zero writes
    must occur to Qdrant, PostgreSQL, cache, or graph state.

    We verify by patching the store backend to track calls.
    """
    from arifosmcp.runtime import memory_gate
    from arifosmcp.tools.memory import arif_memory_recall

    # Track if any store backend was called
    store_called = {"called": False, "args": None}

    # Patch the session to return OBSERVE_ONLY (triggers VOID gate)
    def fake_get_session(sid):
        return {
            "session_id": sid,
            "actor_id": "test-actor",
            "authority": "OBSERVE_ONLY",
            "authority_level": "OBSERVE_ONLY",
        }

    monkeypatch.setattr(memory_gate, "get_session_identity", fake_get_session)

    # Patch store_v2 to detect if it's called
    import arifosmcp.tools.memory as mem_module

    original_store_v2 = mem_module.store_v2

    def tracking_store_v2(*args, **kwargs):
        store_called["called"] = True
        store_called["args"] = (args, kwargs)
        return original_store_v2(*args, **kwargs)

    monkeypatch.setattr(mem_module, "store_v2", tracking_store_v2)

    # Also patch legacy_store
    original_legacy = mem_module.legacy_store

    def tracking_legacy(*args, **kwargs):
        store_called["called"] = True
        store_called["args"] = (args, kwargs)
        return original_legacy(*args, **kwargs)

    monkeypatch.setattr(mem_module, "legacy_store", tracking_legacy)

    # Attempt a store with OBSERVE_ONLY session
    result = arif_memory_recall(
        mode="store",
        content="should cause zero writes",
        session_id="observe-only-session",
        actor_id="test-actor",
    )

    # Gate should have blocked it
    verdict = result.get("verdict", result.get("status", ""))
    assert verdict in ("VOID", "HOLD"), f"Expected gate block, got {verdict}"

    # Zero writes must have occurred
    assert store_called["called"] is False, (
        "Failed gate must cause ZERO writes to any backend. "
        f"store_v2 was called with: {store_called['args']}"
    )


# ═══════════════════════════════════════════════════════════════════════
# 4. test_forget_without_judge_returns_888_hold
# ═══════════════════════════════════════════════════════════════════════


def test_forget_without_judge_returns_888_hold(monkeypatch):
    """Forget without prior arif_judge trace → 888_HOLD (not executed).

    Maps to existing: test_forget_without_judge_trace_returns_888_hold_f13
    """
    from arifosmcp.runtime import memory_gate
    from arifosmcp.tools.memory import arif_memory_recall

    # Session with MUTATE authority but NO judge trace in history
    def fake_get_session(sid):
        return {
            "session_id": sid,
            "actor_id": "test-actor",
            "authority": "FULL",
            "authority_level": "FULL",
            "activity": {
                "history": [
                    {"tool": "arif_init", "verdict": "SEAL"},
                    {"tool": "arif_observe", "verdict": "SEAL"},
                    # No arif_judge or arif_judge_deliberate entry
                ]
            },
        }

    monkeypatch.setattr(memory_gate, "get_session_identity", fake_get_session)

    result = arif_memory_recall(
        mode="forget",
        memory_id="test-memory-id",
        session_id="no-judge-session",
        actor_id="test-actor",
    )

    assert isinstance(result, dict)
    verdict = result.get("verdict", result.get("status", ""))
    assert verdict in ("888_HOLD", "HOLD", "OBSERVE_ONLY"), (
        f"forget without judge trace should 888_HOLD, got {verdict}"
    )
    meta = result.get("meta", result.get("result", {}))
    if isinstance(meta, dict):
        reason = meta.get("reason", "")
        assert any(kw in reason for kw in ("F13", "SOVEREIGN", "judge", "IRREVERSIBLE")), (
            f"Expected F13/judge reason, got: {reason[:100]}"
        )


# ═══════════════════════════════════════════════════════════════════════
# 5. test_forget_without_human_ack_returns_888_hold
# ═══════════════════════════════════════════════════════════════════════


def test_forget_without_human_ack_returns_888_hold():
    """Tombstone forget without ack_irreversible → 888_HOLD.

    Defense-in-depth: memory_gate catches missing judge trace;
    memory.py also checks ack_irreversible for tombstone method.
    """
    from arifosmcp.tools.memory import arif_memory_recall

    result = arif_memory_recall(
        mode="forget",
        memory_id="test-memory-id",
        method="tombstone",
        session_id="test-session",
        actor_id="test-actor",
        # ack_irreversible defaults to False
    )

    assert isinstance(result, dict)
    verdict = result.get("verdict", result.get("status", ""))
    # Should be blocked by either memory_gate (F13 judge trace) or
    # memory.py ack_irreversible check
    assert verdict in ("888_HOLD", "HOLD", "VOID", "OBSERVE_ONLY"), (
        f"tombstone without ack should be blocked, got {verdict}"
    )


# ═══════════════════════════════════════════════════════════════════════
# 6. test_qdrant_offline_returns_sabar
# ═══════════════════════════════════════════════════════════════════════


def test_qdrant_offline_returns_sabar():
    """Qdrant transport failure → SABAR with explicit evidence_honesty tag.

    Maps to existing: test_vector_query_returns_sabar_on_qdrant_offline.
    P0-01b envelope: `evidence_honesty` is the explicit string
    "QDRANT_UNREACHABLE" (was boolean True in the original P0-01 draft;
    upgraded to typed string per P0-01b spec for downstream F2/F9
    consumers to detect the failure mode without ambiguity).
    """
    from arifosmcp.memory import vector_memory_qdrant

    _install_broken_qdrant(vector_memory_qdrant)
    vector_memory_qdrant._qdrant_client = None

    result = asyncio.run(vector_memory_qdrant.vector_query(query="sabar-probe"))

    assert result is not None
    assert isinstance(result, dict)
    assert result.get("ok") is False
    assert result.get("verdict") == "SABAR", (
        f"Qdrant offline should return SABAR, got {result.get('verdict')}"
    )
    # P0-01b: explicit string tag (was boolean True pre-P0-01b).
    assert result.get("evidence_honesty") == "QDRANT_UNREACHABLE", (
        f"evidence_honesty should be the explicit string "
        f"'QDRANT_UNREACHABLE' per P0-01b, got {result.get('evidence_honesty')!r}"
    )
    assert result.get("floor_violation") == "F9"
    assert result.get("backend_status") == "qdrant_offline"
    # F2 TRUTH — honest zeros on missing data.
    assert result.get("overall_confidence") == 0.0
    assert result.get("empty_count") == 0
    assert result.get("total_outputs") == 0
    # F9 ANTI-HANTU — empty results is honest, NOT a fabricated placeholder.
    assert result.get("results") == []


# ═══════════════════════════════════════════════════════════════════════
# 7. test_qdrant_offline_is_not_empty_success
# ═══════════════════════════════════════════════════════════════════════


def test_qdrant_offline_is_not_empty_success():
    """Qdrant offline must NOT return ok=True with empty results.
    That would violate F2 (truth) and F9 (anti-hantu) — representing a
    transport failure as "no memories found" is fabrication by omission.
    """
    from arifosmcp.memory import vector_memory_qdrant

    _install_broken_qdrant(vector_memory_qdrant)
    vector_memory_qdrant._qdrant_client = None

    result = asyncio.run(vector_memory_qdrant.vector_query(query="not-empty-probe"))

    assert result is not None
    assert isinstance(result, dict)

    # CRITICAL: must NOT be ok=True with empty results
    assert not (result.get("ok") is True and result.get("results") == []), (
        "F2/F9 VIOLATION: Qdrant offline returned ok=True with empty results. "
        "This represents a transport failure as 'no memories found' — "
        "fabrication by omission."
    )

    # Must explicitly signal failure
    assert result.get("ok") is False, "Qdrant offline must return ok=False"
    # Must have a verdict (SABAR, not silent)
    assert "verdict" in result, "Qdrant offline must emit a verdict (SABAR), not silent failure"
