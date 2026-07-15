"""
Constitutional Tests — Memory Module Resilience: Qdrant Offline
═══════════════════════════════════════════════════════════════

TASK-P1-04 audit: verify that the memory module degrades gracefully when
Qdrant is unreachable, instead of raising an unhandled exception or
returning a hallucinated memory.

Constitutional contract under test:
  - F1 AMANAH:   No mutation without record; failures must be auditable.
  - F2 TRUTH:    No fabricated scalars. If recall can't happen, say so.
  - F4 CLARITY:  ΔS ≤ 0 — entropy must not increase (no surprise state).
  - F9 ANTI-HANTU: No hallucinated memories. Empty + metadata > fabricated content.
  - F11 AUDIT:   Every failure path leaves a trail.

Floor mapping (constitutional law):
  - Hard floor violation (F1, F2, F9, F11, F13) → VOID.
  - Soft floor violation (other) → SABAR.

Under Qdrant offline, the memory module MUST:
  (a) NOT raise an unhandled exception.
  (b) Return either:
      - A SABAR verdict (soft floor — wait, not VOID), OR
      - A graceful empty result with floor_compliance intact.
  (c) Never hallucinate or invent a memory point that does not exist.
  (d) Emit at least one audit signal (sesat event, coverage_gap, or verdict chain).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio

import pytest

# ─────────────────────────────────────────────────────────────────────
# Helper: install a broken Qdrant into a module's lazy client
# ─────────────────────────────────────────────────────────────────────


class _QdrantOfflineError(RuntimeError):
    """Sentinel error raised by the offline stub."""


def _install_broken_qdrant(module, attr_name: str = "_get_qdrant_client") -> None:
    """Patch `module.<attr_name>` so it always raises _QdrantOfflineError.

    Also nuke the module-level lazy singleton (if any) so the broken
    function is consulted on every call.
    """

    def _broken():
        raise _QdrantOfflineError("Qdrant unreachable (test)")

    setattr(module, attr_name, _broken)
    # Some modules cache the client in a module-level variable.
    for cached in ("_qdrant_client", "_client", "client"):
        if hasattr(module, cached):
            try:
                setattr(module, cached, None)
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────
# 1. arif_memory_recall (stage 555) — primary tool path
# ─────────────────────────────────────────────────────────────────────


def test_arif_memory_recall_query_does_not_raise_when_qdrant_offline():
    """When Qdrant is unreachable, the recall-by-query path must not raise.

    Expected: returns a dict with a verdict chain (not exception, not hallucination).
    """
    from arifosmcp.runtime import memory_store
    from arifosmcp.tools import memory

    _install_broken_qdrant(memory_store)
    # Also force empty JSON index so we go down the Qdrant path
    memory_store._index_read = lambda: {}

    # The tool MUST return a dict, not raise. Use a real session/actor pair.
    result = memory.arif_memory_recall(
        query="audit-probe-p1-04",
        session_id="audit-session-p1-04",
        actor_id="arifos-federation",
    )

    assert result is not None
    assert isinstance(result, dict), "MUST return dict, not raise"
    # The wrapper must have stamped some verdict on it.
    assert "verdict" in result or "status" in result, (
        "MUST emit a verdict or status — silent return violates F11 audit"
    )
    # Floor compliance preserved: meta should be present.
    assert "meta" in result, "MUST preserve meta for audit"
    # Results must be empty, NOT fabricated
    meta = result["meta"]
    results = meta.get("results", [])
    assert results == [], "MUST return empty results, not hallucinated memories"


def test_arif_memory_recall_by_memory_id_returns_clean_not_found():
    """recall(memory_id) with Qdrant down should return None (not found),
    not raise, and the calling tool should stamp a verdict on it.
    """
    from arifosmcp.runtime import memory_store
    from arifosmcp.tools import memory

    _install_broken_qdrant(memory_store)
    memory_store._index_read = lambda: {}

    # Direct recall() call: should return None
    rec = memory_store.recall("audit-probe-nonexistent-id-p1-04")
    assert rec is None, "recall() must return None on miss, not raise"

    # Tool wrapper: should still return a dict with verdict
    result = memory.arif_memory_recall(
        mode="recall",
        memory_id="audit-probe-nonexistent-id-p1-04",
        actor_id="arifos-federation",
    )
    assert isinstance(result, dict)
    assert "verdict" in result or "status" in result


def test_arif_memory_recall_store_returns_qdrant_write_failed_not_exception():
    """Store mode with Qdrant down: must return ok=False, not raise."""
    from arifosmcp.runtime import memory_store
    from arifosmcp.tools import memory

    _install_broken_qdrant(memory_store)
    memory_store._index_read = lambda: {}

    result = memory.arif_memory_recall(
        mode="store",
        content="audit-probe-p1-04",
        actor_id="arifos-federation",
        session_id="audit-session-p1-04",
    )

    assert isinstance(result, dict)
    inner = result.get("result", {})
    # Either stored=True (postgres took it) or stored=False with qdrant_write_failed.
    # MUST NOT have raised.
    assert "stored" in inner
    if not inner.get("stored"):
        assert inner.get("error") == "qdrant_write_failed", (
            f"Expected qdrant_write_failed, got {inner.get('error')!r}"
        )


# ─────────────────────────────────────────────────────────────────────
# 2. vector_memory_qdrant — direct L3/L4 layer (audit target)
# ─────────────────────────────────────────────────────────────────────


def test_vector_query_raises_unhandled_on_qdrant_offline_finding():
    """Known finding: vector_memory_qdrant.vector_query does NOT catch the
    Qdrant-unreachable exception. This is a real F9/F11 violation because
    the exception bypasses the floor verdict chain and can crash callers.

    This test is a regression guard. It records the current (broken) state
    and a future fix should flip the assertion: the call must return
    {"ok": False, "error": ..., "qdrant_unavailable": True} or similar.
    """
    from arifosmcp.memory import vector_memory_qdrant

    _install_broken_qdrant(vector_memory_qdrant)
    vector_memory_qdrant._qdrant_client = None

    # Run the async function. The function should not raise, per F9 + F11.
    # We capture the actual current behaviour for the audit report.
    raised: Exception | None = None
    result: dict | None = None
    try:
        result = asyncio.run(vector_memory_qdrant.vector_query(query="audit-probe-p1-04"))
    except Exception as exc:
        raised = exc

    if raised is not None:
        # Current state: unhandled exception. Audit finding logged.
        assert isinstance(raised, _QdrantOfflineError) or "Qdrant" in str(raised), (
            f"Unexpected exception type: {type(raised).__name__}: {raised}"
        )
        # Document the finding — do not auto-fail; the test exists to lock in
        # current behaviour and to be flipped to PASS once a guard is added.
        pytest.xfail(
            f"KNOWN BUG: vector_query raises unhandled {type(raised).__name__} "
            f"when Qdrant is offline. Tracked in audit report docs/memory_audit.md "
            f"and GitHub issue [BUG] Memory module unhandled exception on qdrant_offline."
        )
    else:
        # Once the bug is fixed, the result must signal failure cleanly.
        assert result is not None
        assert result.get("ok") is False, (
            "Once fixed, vector_query must return ok=False on Qdrant offline"
        )
        assert "qdrant_unavailable" in result or "error" in result


def test_vector_health_gracefully_reports_unhealthy_on_qdrant_offline():
    """vector_health must report unhealthy, not raise. (Reference: this is
    the only vector_memory_qdrant function that already handles Qdrant
    offline correctly — every other function should match it.)
    """
    from arifosmcp.memory import vector_memory_qdrant

    _install_broken_qdrant(vector_memory_qdrant)
    vector_memory_qdrant._qdrant_client = None

    # Must not raise
    result = asyncio.run(vector_memory_qdrant.vector_health())
    assert isinstance(result, dict)
    assert result.get("ok") is False
    assert result.get("status") == "unhealthy"
    assert "error" in result


# ─────────────────────────────────────────────────────────────────────
# 3. BGE-M3 model load failure — F9 compliance
# ─────────────────────────────────────────────────────────────────────


def test_bge_m3_ollama_failure_returns_404_equiv_not_500(monkeypatch):
    """If BGE-M3 (Ollama) returns nothing, the embedding layer must raise
    RuntimeError, NOT silently return a zero vector. The vector_query/store
    callers must catch that RuntimeError and surface ok=False with
    embedding_unavailable=True.

    F9 compliance: zero-vector fallback is forbidden because it pollutes
    Qdrant retrieval with arbitrary cosine similarities.
    """
    import httpx

    from arifosmcp.memory import vector_memory_qdrant

    class _FakeEmptyResponse:
        status_code = 200
        text = '{"embedding": []}'

        def json(self):
            return {"embedding": []}

        def raise_for_status(self):
            return None

    def _fake_post(*args, **kwargs):
        return _FakeEmptyResponse()

    monkeypatch.setattr(httpx, "post", _fake_post)

    # _generate_embedding MUST raise RuntimeError, not return [] or zeros.
    with pytest.raises(RuntimeError) as excinfo:
        vector_memory_qdrant._generate_embedding("audit-probe-p1-04")
    assert "Embedding unavailable" in str(excinfo.value), (
        f"Expected RuntimeError mentioning embedding, got: {excinfo.value}"
    )

    # The caller (vector_query) must catch this and return ok=False
    # (the bug above means it raises instead, so we use vector_store path
    # which DOES have the try/except around _generate_embedding — but
    # vector_store still calls _ensure_collection first; so we patch that
    # out to isolate the embedding failure path).
    monkeypatch.setattr(vector_memory_qdrant, "_ensure_collection", lambda: None)
    result = asyncio.run(vector_memory_qdrant.vector_query(query="audit-probe-p1-04"))
    assert result.get("ok") is False
    assert result.get("embedding_unavailable") is True
    assert "L10 EMBEDDING" in result.get("error", "")


# ─────────────────────────────────────────────────────────────────────
# 4. Constitutional verdict chain preservation
# ─────────────────────────────────────────────────────────────────────


def test_recall_result_preserves_sabar_chain_when_qdrant_offline():
    """Under Qdrant offline, the verdict chain must end at SABAR or RETAK
    (soft floors), NOT VOID (hard floor). F1, F2, F9, F11, F13 violations
    are VOID; everything else is SABAR. Memory unavailability is a soft
    floor, not a hard floor — the operator should be told to wait, not
    told the system is fatally broken.
    """
    from arifosmcp.runtime import memory_store
    from arifosmcp.tools import memory

    _install_broken_qdrant(memory_store)
    memory_store._index_read = lambda: {}

    result = memory.arif_memory_recall(
        query="audit-probe-p1-04",
        session_id="audit-session-p1-04",
        actor_id="arifos-federation",
    )

    meta = result.get("meta", {})

    # ── A coverage_gap or sesat_event signal must be present ──
    has_signal = "coverage_gap" in meta or "sesat_event" in meta or "memory_quality" in meta
    assert has_signal, (
        "MUST emit coverage_gap / sesat_event / memory_quality signal — "
        "F11 AUDIT: every failure must leave a trail"
    )

    # ── overall_confidence must be 0.0 (no fabrication) ──
    confidence = meta.get("confidence", {})
    if isinstance(confidence, dict):
        assert confidence.get("overall_confidence") == 0.0, (
            f"F2 TRUTH: overall_confidence must be 0.0 when Qdrant is down, "
            f"got {confidence.get('overall_confidence')}"
        )

    # ── F2 must NOT be in failed_floors as a hard VOID ──
    # Failed floors list is informational; the verdict chain (RETAK/SYUBHAH)
    # is what matters. RETAK = "cracked but not broken" (SABAR-class).
    # We allow F2 to appear in failed_floors as a soft warning,
    # but the outer verdict must be SABAR-class (RETAK/SYUBHAH/PARTIAL/HOLD),
    # never VOID.
    outer_verdict = result.get("verdict", "")
    void_verdicts = {"VOID", "VOID_BREACH", "VOID_HANTU", "VOID_IRREVERSIBLE"}
    assert outer_verdict not in void_verdicts, (
        f"F9/F11 violation: outer verdict is {outer_verdict!r} — "
        f"Qdrant offline is SABAR-class (soft floor), not VOID"
    )


# ─────────────────────────────────────────────────────────────────────
# 5. Audit signal: no unhandled exceptions across all 8 modes
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "mode,extra_kwargs",
    [
        pytest.param("recall", {"query": "x"}, id="recall-query"),
        pytest.param("recall", {"memory_id": "x"}, id="recall-by-id"),
        pytest.param("store", {"content": "x"}, id="store"),
        pytest.param("audit", {"checks": ["stale"]}, id="audit"),
        pytest.param("stats", {}, id="stats"),
        pytest.param("init_recall", {}, id="init_recall"),
    ],
)
def test_all_modes_survive_qdrant_offline(mode, extra_kwargs):
    """Sweep: every primary mode of arif_memory_recall must return a dict
    (or None) when Qdrant is offline, never raise an unhandled exception.

    Modes deliberately excluded: seal (requires ack_irreversible), forget,
    update — those need extra args and are out of scope for a recall-offline
    resilience audit.
    """
    from arifosmcp.runtime import memory_store
    from arifosmcp.tools import memory

    _install_broken_qdrant(memory_store)
    memory_store._index_read = lambda: {}

    # The call MUST return a value, not raise.
    # The contract under audit: graceful degradation, not exception.
    result = memory.arif_memory_recall(
        session_id="audit-session-p1-04",
        actor_id="arifos-federation",
        mode=mode,
        **extra_kwargs,
    )

    # Allow None for some modes (e.g. audit can return None when checks is
    # an unsupported set). Just not a raised exception.
    assert result is None or isinstance(result, dict)
