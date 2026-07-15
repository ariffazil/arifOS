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


def test_vector_query_returns_sabar_on_qdrant_offline():
    """FIXED (P0-01b): vector_memory_qdrant.vector_query now catches the
    Qdrant-unreachable exception and returns a structured SABAR verdict
    instead of raising.

    Verdict envelope (F9 ANTI-HANTU + F11 AUDIT contract):
      - ok=False, verdict="SABAR", floor_violation="F9"
      - evidence_honesty="QDRANT_UNREACHABLE" (explicit string tag)
      - reason: human-readable failure explanation
      - remediation: operator-facing fix instruction
      - overall_confidence: 0.0 (no fabrication on missing data)
      - empty_count: 0, total_outputs: 0 (honest zeros)
      - results: [] (empty list, NOT a hallucinated zero-vector)
      - backend_status: "qdrant_offline"
    """
    from arifosmcp.memory import vector_memory_qdrant

    _install_broken_qdrant(vector_memory_qdrant)
    vector_memory_qdrant._qdrant_client = None

    result = asyncio.run(vector_memory_qdrant.vector_query(query="audit-probe-p1-04"))

    assert result is not None, "Must return a dict, not None"
    assert isinstance(result, dict)
    assert result.get("ok") is False, "Must return ok=False on Qdrant offline"
    assert result.get("verdict") == "SABAR", (
        f"Verdict must be SABAR (soft floor), got {result.get('verdict')!r}"
    )
    # F9 ANTI-HANTU — explicit string tag (P0-01b envelope shape).
    assert result.get("evidence_honesty") == "QDRANT_UNREACHABLE", (
        f"Must flag evidence_honesty='QDRANT_UNREACHABLE' — no fabrication, "
        f"got {result.get('evidence_honesty')!r}"
    )
    assert result.get("floor_violation") == "F9"
    assert "reason" in result and "vector store offline" in result["reason"].lower()
    assert "remediation" in result and "qdrant" in result["remediation"].lower()
    # F2 TRUTH — honest zeros, not fabricated confidence.
    assert result.get("overall_confidence") == 0.0, (
        "F2 TRUTH: overall_confidence must be 0.0 on missing data, "
        f"got {result.get('overall_confidence')!r}"
    )
    assert result.get("empty_count") == 0
    assert result.get("total_outputs") == 0
    # F9 — no hallucinated vectors / placeholder results.
    assert result.get("results") == [], (
        "F9 ANTI-HANTU: must return empty results, NOT a zero-vector "
        "placeholder or fabricated partial data"
    )
    assert result.get("backend_status") == "qdrant_offline"


@pytest.mark.parametrize(
    "op_call",
    [
        pytest.param(
            lambda m: m.vector_query(query="audit-probe-p0-01b-store"),
            id="vector_query",
        ),
        pytest.param(
            lambda m: m.vector_store(content="audit-probe-p0-01b-store-content"),
            id="vector_store",
        ),
    ],
)
def test_vector_query_and_store_return_sabar_with_evidence_honesty_on_qdrant_offline(op_call):
    """P0-01b: Both vector_query and vector_store MUST return a SABAR
    verdict (not raise) when Qdrant is unreachable. The verdict MUST
    carry the explicit `evidence_honesty: "QDRANT_UNREACHABLE"` tag so
    F2/F9 consumers can detect the failure mode without ambiguity.

    Covers the issue #585 regression surface for both public entry points.
    """
    from arifosmcp.memory import vector_memory_qdrant

    _install_broken_qdrant(vector_memory_qdrant)
    vector_memory_qdrant._qdrant_client = None

    # MUST NOT raise — the wrapper swallows connection failures into
    # a structured SABAR verdict.
    raised: BaseException | None = None
    result: dict | None = None
    try:
        result = asyncio.run(op_call(vector_memory_qdrant))
    except BaseException as exc:  # noqa: BLE001 — we explicitly want to catch
        raised = exc

    assert raised is None, (
        f"F9/F11 violation: {op_call.__doc__ or 'op'} raised "
        f"{type(raised).__name__}: {raised} — wrapper MUST return SABAR "
        "verdict, not propagate the exception"
    )
    assert isinstance(result, dict)
    # Core SABAR envelope — see _sabar_qdrant_unreachable() in the
    # production module for the canonical shape.
    assert result.get("ok") is False
    assert result.get("verdict") == "SABAR"
    assert result.get("evidence_honesty") == "QDRANT_UNREACHABLE", (
        "evidence_honesty tag MUST be the explicit string "
        "'QDRANT_UNREACHABLE' per P0-01b spec (not boolean True, not "
        f"None) — got {result.get('evidence_honesty')!r}"
    )
    assert result.get("floor_violation") == "F9"
    assert result.get("backend_status") == "qdrant_offline"
    # No fabricated content.
    assert result.get("results") == []
    assert result.get("overall_confidence") == 0.0


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
