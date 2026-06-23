"""Test the agentic search FSM in arif_memory_recall."""


def _payload(result):
    """Extract the data payload from _ok wrapper."""
    return result.get("result", result)


def test_agentic_mode_dispatches():
    """agentic mode should be a valid dispatch target — not 'Unknown mode'."""
    from arifosmcp.runtime.tools import _arif_memory_recall

    result = _arif_memory_recall(mode="agentic", query="what is the Malay Basin?")
    p = _payload(result)
    assert result.get("status") == "OK", f"Got {result.get('status')}: {result}"
    assert "telemetry" in p, f"No telemetry in: {list(p.keys())}"


def test_agentic_telemetry_schema():
    """Telemetry must include all required fields per spec v0.1."""
    from arifosmcp.runtime.tools import _arif_memory_recall

    result = _arif_memory_recall(mode="agentic", query="arifOS governance")
    p = _payload(result)
    t = p.get("telemetry", {})
    required = [
        "spec_version",
        "epoch",
        "qdf",
        "loops",
        "tools_used",
        "coverage_score",
        "conflict_score",
        "confidence",
        "verdict",
        "witness",
        "states_visited",
    ]
    for field in required:
        assert field in t, f"Missing telemetry field: {field}"
    assert t["spec_version"] == "v0.1"
    assert t["verdict"] in ("OK", "PARTIAL", "DISPUTED", "FAIL", "PENDING")
    assert 0.0 <= t["confidence"] <= 0.90, f"Confidence {t['confidence']} out of band"
    assert "PLAN" in t["states_visited"], "PLAN state missing"
    assert "STOP" in t["states_visited"], "STOP state missing"


def test_agentic_sub_questions_fallback():
    """When Ollama fails, sub-questions fall back to original query."""
    from arifosmcp.runtime.tools import _arif_memory_recall

    result = _arif_memory_recall(mode="agentic", query="what is arifOS?")
    p = _payload(result)
    sqs = p.get("sub_questions", [])
    assert isinstance(sqs, list), f"sub_questions not a list: {type(sqs)}"
    assert len(sqs) >= 1, "Should have at least 1 sub-question"
    # Fallback: original query preserved
    assert sqs[0] == "what is arifOS?", f"Fallback should preserve original: {sqs}"


def test_agentic_search_governance():
    """Summary must include WHAT/WHERE/WHY/HOW/WHEN/STOP governance fields."""
    from arifosmcp.runtime.tools import _arif_memory_recall

    result = _arif_memory_recall(mode="agentic", query="test governance")
    p = _payload(result)
    sg = p.get("summary", {}).get("search_governance", {})
    dims = ["WHAT", "WHERE", "WHY", "HOW", "WHEN", "STOP"]
    for dim in dims:
        assert dim in sg, f"Missing governance dimension: {dim}"
        assert sg[dim], f"Governance dimension {dim} is empty"


def test_agentic_not_mutating():
    """agentic mode should NOT require MUTATE lease — it's read-only."""
    from arifosmcp.runtime.tools import _MUTATING_MEMORY_MODES

    assert "agentic" not in _MUTATING_MEMORY_MODES, (
        "agentic mode should not be in MUTATING_MEMORY_MODES — it is read-only"
    )


def test_agentic_evidence_structure():
    """Evidence list must have required fields."""
    from arifosmcp.runtime.tools import _arif_memory_recall

    result = _arif_memory_recall(mode="agentic", query="arifOS")
    p = _payload(result)
    evidence = p.get("evidence", [])
    assert isinstance(evidence, list), f"evidence is not a list: {type(evidence)}"
    if evidence:
        e = evidence[0]
        for field in ["source", "sub_q", "content", "relevance"]:
            assert field in e, f"Missing evidence field: {field}"
        assert e["source"] in ("memory", "web"), f"Bad source: {e['source']}"


if __name__ == "__main__":
    test_agentic_mode_dispatches()
    print("  PASS: mode_dispatches")
    test_agentic_telemetry_schema()
    print("  PASS: telemetry_schema")
    test_agentic_sub_questions_fallback()
    print("  PASS: sub_questions_fallback")
    test_agentic_search_governance()
    print("  PASS: search_governance")
    test_agentic_not_mutating()
    print("  PASS: not_mutating")
    test_agentic_evidence_structure()
    print("  PASS: evidence_structure")
    print("ALL 6 AGENTIC SEARCH TESTS PASSED")
