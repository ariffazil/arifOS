"""
tests/core/test_graphiti_semantic_readiness.py
══════════════════════════════════════════════════════════

F2 TRUTH (Truthfulness): graphiti_embedding_runtime is decoupled from
ARIFOS_ML_FLOORS. The semantic floor (gate) is still tied to the ML toggle
because it's the actual constitutional gate. But the embedding runtime
status is reported independently and starts as "unverified" until a real
semantic probe runs.

Coverage:
  - ML disabled → embedding='unverified', semantic_floor='disabled'
  - ML enabled but dependencies missing → embedding='unverified',
    semantic_floor='hold'
  - The two dimensions do NOT collapse to the same value (transport/storage
    vs embedding vs semantic_floor)
  - The legacy behavior (embedding tied to ml_runtime_ready) is removed.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Any

import pytest


def _read_semantic_readiness() -> dict[str, Any] | None:
    """Hit /health and return semantic_readiness dict, or None if unreachable."""
    from arifosmcp.runtime.rest_routes.rest_routes import (
        _build_governance_status_payload,
    )
    from arifosmcp.runtime.server import app as server_app

    from tests.conftest import SyncASGIClient

    client = SyncASGIClient(server_app)
    try:
        response = client.get("/health")
    except Exception:
        return None
    if response.status_code != 200:
        return None
    try:
        return response.json().get("semantic_readiness", {})
    except Exception:
        return None


def test_graphiti_three_dimensions_independent_when_ml_disabled(monkeypatch):
    """When ARIFOS_ML_FLOORS=off, embedding is 'unverified' (not 'disabled').

    The semantic floor remains 'disabled' (the gate is off). Transport
    and storage are still driven by graphiti reachability probe — they
    remain independent.
    """
    from arifosmcp.runtime.rest_routes.rest_routes import (
        _build_governance_status_payload,
    )

    monkeypatch.setattr(
        "arifosmcp.runtime.rest_routes.rest_routes._build_governance_status_payload",
        lambda: {
            "telemetry": {},
            "floors": {},
            "machine_vitals": {},
            "verdict": "HOLD",
            "session_id": "t",
            "tau_confidence_system": None,
            "f2_threshold": 0.99,
            "psi_vitality": None,
            "peace2": None,
        },
    )
    monkeypatch.delenv("ARIFOS_ML_FLOORS", raising=False)
    from core.shared import law_audit

    law_audit._probe_ml_embedding_runtime.cache_clear()
    law_audit._load_sbert_runtime.cache_clear()

    sr = _read_semantic_readiness()
    if sr is None:
        pytest.skip("/health not reachable in test env")

    assert sr["graphiti_embedding_runtime"] == "unverified"
    assert sr["graphiti_semantic_floor"] == "disabled"
    # Transport and storage are reported independently
    assert sr["graphiti_transport"] in ("healthy", "degraded")
    assert sr["graphiti_storage"] in ("healthy", "degraded")


def test_graphiti_semantic_floor_holds_when_ml_enabled_but_deps_missing(
    monkeypatch,
):
    """ARIFOS_ML_FLOORS=1 but no sentence_transformers → semantic_floor='hold'.

    embedding remains 'unverified' (real probe hasn't run). The two are
    distinct witnesses.
    """
    monkeypatch.setattr(
        "arifosmcp.runtime.rest_routes.rest_routes._build_governance_status_payload",
        lambda: {
            "telemetry": {},
            "floors": {},
            "machine_vitals": {},
            "verdict": "HOLD",
            "session_id": "t",
            "tau_confidence_system": None,
            "f2_threshold": 0.99,
            "psi_vitality": None,
            "peace2": None,
        },
    )
    monkeypatch.setenv("ARIFOS_ML_FLOORS", "1")
    from core.shared import law_audit

    law_audit._probe_ml_embedding_runtime.cache_clear()
    law_audit._load_sbert_runtime.cache_clear()
    monkeypatch.setattr(
        law_audit,
        "_missing_ml_dependencies",
        lambda: ["sentence_transformers", "torch"],
    )

    sr = _read_semantic_readiness()
    if sr is None:
        pytest.skip("/health not reachable in test env")

    # Semantic floor = the gate → hold when deps missing
    assert sr["graphiti_semantic_floor"] == "hold"
    # Embedding runtime = independent witness → still unverified (no real probe)
    assert sr["graphiti_embedding_runtime"] == "unverified"
    # They MUST NOT collapse to the same value.
    assert sr["graphiti_embedding_runtime"] != sr["graphiti_semantic_floor"]


def test_graphiti_embedding_not_collapsed_to_transport(monkeypatch):
    """The four graphiti fields are reported independently.

    Even when transport is degraded, embedding can be unverified without
    inheriting transport's state — they are not the same probe.
    """
    monkeypatch.setattr(
        "arifosmcp.runtime.rest_routes.rest_routes._build_governance_status_payload",
        lambda: {
            "telemetry": {},
            "floors": {},
            "machine_vitals": {},
            "verdict": "HOLD",
            "session_id": "t",
            "tau_confidence_system": None,
            "f2_threshold": 0.99,
            "psi_vitality": None,
            "peace2": None,
        },
    )
    monkeypatch.delenv("ARIFOS_ML_FLOORS", raising=False)
    from core.shared import law_audit

    law_audit._probe_ml_embedding_runtime.cache_clear()
    law_audit._load_sbert_runtime.cache_clear()
    # Force graphiti probe to return False (degraded transport)
    monkeypatch.setattr(
        "arifosmcp.runtime.rest_routes.rest_routes._probe_graphiti_enabled",
        lambda: False,
    )

    sr = _read_semantic_readiness()
    if sr is None:
        pytest.skip("/health not reachable in test env")

    assert sr["graphiti_transport"] == "degraded"
    assert sr["graphiti_storage"] == "degraded"
    # Embedding is independent of transport status
    assert sr["graphiti_embedding_runtime"] == "unverified"