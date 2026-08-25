"""Regression tests for ART × arifFlow evidence gate wiring."""

from __future__ import annotations

import pytest

from arifosmcp.runtime.art_evidence_gate import (
    EvidenceVerdict,
    EvidenceGateResult,
    aggregate_evidence,
)
from arifosmcp.runtime.pre_execution_gate import _art_reflex_check
from arifosmcp.schemas.kernel_envelope import (
    ActionClass,
    KernelEnvelope,
)


def test_evidence_aggregation_prefers_inconsistent_and_insufficient():
    assert aggregate_evidence({"a": "INCONSISTENT", "b": "SUFFICIENT"}) == "INCONSISTENT"
    assert aggregate_evidence({"a": "INSUFFICIENT", "b": "SUFFICIENT"}) == "INSUFFICIENT"
    assert aggregate_evidence({"a": "UNKNOWN", "b": "SUFFICIENT"}) == "SUFFICIENT"


def test_kernel_audit_block_exposes_evidence_verdict(monkeypatch):
    """An evidence HOLD must become ART HOLD with arifFlow receipts visible."""

    import arifosmcp.runtime.art_evidence_gate as evidence_module

    def held(*, tool_name, action_class, is_reversible, session_id, actor_id, payload, canonical_tool):
        del tool_name, action_class, is_reversible, session_id, actor_id, payload, canonical_tool
        return EvidenceGateResult(
            verdict=EvidenceVerdict.INSUFFICIENT,
            gates={
                "selfcheck": {
                    "verdict": "INSUFFICIENT",
                    "source": "test:no_gene",
                }
            },
            receipts={"selfcheck": {"receipt_id": "test-receipt-001"}},
        )

    monkeypatch.setattr(evidence_module, "run_art_evidence_gates", held)

    envelope = KernelEnvelope(
        kernel={
            "actor_id": "333-AGI",
            "session_id": "session-art-evidence-1",
            "actor_verified": True,
        },
        organ={"tool_name": "arif_think"},
        authority={"action_class": ActionClass.ANALYZE},
        payload={"intent": "Execute a boundary check on the ledger"},
    )

    result = _art_reflex_check(
        envelope,
        ActionClass.ANALYZE,
        _manifest_entry("arif_think"),
    )

    assert result is not None
    assert result.verdict.value == "HOLD"
    assert "ART_EVIDENCE_INSUFFICIENT" in result.violations
    assert envelope.audit.evidence_verdict == "INSUFFICIENT"
    assert envelope.audit.evidence_flow_receipts == {
        "selfcheck": "test-receipt-001"
    }


def test_kernel_audit_keeps_sufficient_evidence(monkeypatch):
    import arifosmcp.runtime.art_evidence_gate as evidence_module

    monkeypatch.setattr(
        evidence_module,
        "run_art_evidence_gates",
        lambda **kwargs: EvidenceGateResult(
            verdict=EvidenceVerdict.SUFFICIENT,
            gates={"atomic_decomposition": {"verdict": "SUFFICIENT"}},
            receipts={},
        ),
    )
    envelope = KernelEnvelope(
        kernel={
            "actor_id": "333-AGI",
            "session_id": "session-art-evidence-2",
            "actor_verified": True,
        },
        organ={"tool_name": "arif_think"},
        authority={"action_class": ActionClass.ANALYZE},
        payload={"intent": "Execute a boundary check on the ledger"},
    )

    result = _art_reflex_check(
        envelope,
        ActionClass.ANALYZE,
        _manifest_entry("arif_think"),
    )

    assert result is None
    assert envelope.audit.evidence_verdict == "SUFFICIENT"


def _manifest_entry(tool_name: str):
    from arifosmcp.runtime.pre_execution_gate import CANONICAL_TOOL_MANIFEST

    return CANONICAL_TOOL_MANIFEST[tool_name]
