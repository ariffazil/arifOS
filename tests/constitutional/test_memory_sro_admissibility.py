"""
Constitutional Tests — Memory SRO Admissibility Read Gate
═════════════════════════════════════════════════════════

Origin: SRO schema unification 2026-09-12 (99/99 arifos_memory points SRO v1)
+ external verdict GO_MEMORY_RETRIEVAL_POLICY_GATE. The WRITE side already had
a policy engine (policies.py / Memory Promotion Gate); the READ side had no
gate — an EXPIRED memory could be recalled as if current.

Constitutional contract under test:
  - F2 TRUTH:     A structurally-valid but EXPIRED/SUPERSEDED record is NOT
                  admissible for operational recall. Uniform schema ≠ uniform
                  truth.
  - F9 ANTI-HANTU: Old memory must never surface as present fact. Historical
                  mode must label every non-ACTIVE record.
  - Void Guard:   Refusals are counted with reason codes in the response —
                  never dropped silently ("no data" ≠ "all clear").
  - Fail-closed:  Unknown mode, missing SRO, wrong version, malformed block —
                  all refuse; the gate never improvises an admit.
  - Writer gate:  Fresh vector_store writes carry an SRO v1 block stamped at
                  the writer boundary, so new points can never predate SRO.

Policy SOT under test: config/memory-admissibility-policy.yaml (versioned).
Gate module: arifosmcp/memory/admissibility.py.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.memory import vector_memory_qdrant  # noqa: E402
from arifosmcp.memory.admissibility import (  # noqa: E402
    evaluate,
    load_policy,
    summarize_exclusions,
)

# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

_NOW = datetime(2026, 9, 12, tzinfo=UTC)


def _sro(status="ACTIVE", expires_at=None, superseded_by=None, version=1, confidence=None):
    return {
        "supersession": {
            "supersedes": None,
            "superseded_by": superseded_by,
            "supersession_reason": None,
            "supersession_date": None,
        },
        "expiry": {
            "expires_at": expires_at,
            "review_by": None,
            "status": status,
        },
        "calibration": {
            "confidence_at_creation": confidence,
            "outcome_observed": None,
            "outcome_date": None,
            "calibration_error": None,
        },
        "sro_version": version,
        "sro_migrated_at": "2026-09-12T00:00:00+00:00",
    }


def _payload(sro):
    return {"content": "probe", "sro": sro}


_FUTURE = (_NOW + timedelta(days=30)).isoformat()
_PAST = (_NOW - timedelta(days=30)).isoformat()


class _FakeHit:
    def __init__(self, pid, payload, score=0.95):
        self.id = pid
        self.score = score
        self.payload = payload


class _FakeQueryResponse:
    def __init__(self, points):
        self.points = points


class _FakeQdrantClient:
    def __init__(self, points):
        self._points = points
        self.upserted = []

    def query_points(self, **kwargs):
        return _FakeQueryResponse(self._points)

    def upsert(self, collection_name, points):
        self.upserted.extend(points)


def _install_fake_vector_backend(monkeypatch, points):
    client = _FakeQdrantClient(points)
    monkeypatch.setattr(vector_memory_qdrant, "_ensure_collection", lambda: None)
    monkeypatch.setattr(vector_memory_qdrant, "_get_qdrant_client", lambda: client)
    monkeypatch.setattr(
        vector_memory_qdrant, "_generate_embedding", lambda text: [0.1] * 1024
    )
    return client


# ─────────────────────────────────────────────────────────────────────
# 1. Gate unit tests — pure evaluate() decisions
# ─────────────────────────────────────────────────────────────────────


def test_active_with_future_expiry_is_admitted_default_mode():
    policy = load_policy()
    d = evaluate(_payload(_sro("ACTIVE", _FUTURE)), policy, mode="default", now=_NOW)
    assert d.admitted and d.reason_code is None and d.label is None


def test_expired_status_refused_default_mode():
    policy = load_policy()
    d = evaluate(_payload(_sro("EXPIRED")), policy, mode="default", now=_NOW)
    assert not d.admitted
    assert d.reason_code == "STATUS_NOT_ADMISSIBLE"
    assert d.effective_status == "EXPIRED"


def test_active_but_past_expires_at_refused_as_expired_by_time():
    """Temporal drift guard: the status field says ACTIVE, the clock says
    otherwise. Time wins (EXPIRED_BY_TIME), and historical mode still
    admits it — labelled."""
    policy = load_policy()
    d = evaluate(_payload(_sro("ACTIVE", _PAST)), policy, mode="default", now=_NOW)
    assert not d.admitted
    assert d.reason_code == "EXPIRED_BY_TIME"
    assert d.effective_status == "EXPIRED"

    h = evaluate(_payload(_sro("ACTIVE", _PAST)), policy, mode="historical", now=_NOW)
    assert h.admitted
    assert h.label == "HISTORICAL"
    assert h.effective_status == "EXPIRED"


def test_superseded_chain_refused_default_mode():
    policy = load_policy()
    d = evaluate(
        _payload(_sro("ACTIVE", _FUTURE, superseded_by="successor-1")),
        policy,
        mode="default",
        now=_NOW,
    )
    assert not d.admitted
    assert d.reason_code == "SUPERSEDED"


def test_missing_sro_block_refused_not_improvised():
    """Fail-closed: a point without an SRO block (predates SRO or ungated
    writer) is refused — the gate never guesses it fresh."""
    policy = load_policy()
    d = evaluate({"content": "old shape, no sro"}, policy, mode="default", now=_NOW)
    assert not d.admitted
    assert d.reason_code == "SRO_MISSING"


def test_wrong_sro_version_refused():
    policy = load_policy()
    d = evaluate(_payload(_sro("ACTIVE", _FUTURE, version=2)), policy, mode="default", now=_NOW)
    assert not d.admitted
    assert d.reason_code == "SRO_VERSION_MISMATCH"


def test_malformed_sro_status_refused():
    policy = load_policy()
    d = evaluate(_payload(_sro("ZOMBIE")), policy, mode="default", now=_NOW)
    assert not d.admitted
    assert d.reason_code == "MALFORMED_SRO"


def test_unknown_mode_refused_fail_closed():
    policy = load_policy()
    d = evaluate(_payload(_sro("ACTIVE", _FUTURE)), policy, mode="yolo", now=_NOW)
    assert not d.admitted
    assert d.reason_code == "MODE_UNKNOWN"


def test_historical_mode_admits_expired_with_label_active_stays_unlabelled():
    policy = load_policy()
    e = evaluate(_payload(_sro("EXPIRED")), policy, mode="historical", now=_NOW)
    assert e.admitted and e.label == "HISTORICAL"

    a = evaluate(_payload(_sro("ACTIVE", _FUTURE)), policy, mode="historical", now=_NOW)
    assert a.admitted and a.label is None, "ACTIVE record is current — no HISTORICAL label"


def test_low_confidence_refused_when_threshold_set():
    """min_confidence is null in the shipped policy (disabled), but the gate
    must enforce it the day it is switched on. None confidence passes —
    cannot evaluate, do not fabricate a refusal."""
    policy = load_policy()
    policy["modes"]["default"]["min_confidence"] = 0.8
    refused = evaluate(
        _payload(_sro("ACTIVE", _FUTURE, confidence=0.5)), policy, mode="default", now=_NOW
    )
    assert not refused.admitted and refused.reason_code == "LOW_CONFIDENCE"

    unknown = evaluate(_payload(_sro("ACTIVE", _FUTURE)), policy, mode="default", now=_NOW)
    assert unknown.admitted, "None confidence cannot be evaluated — passes"


def test_exclusion_summary_counts_reason_codes():
    policy = load_policy()
    ds = [
        evaluate(_payload(_sro("EXPIRED")), policy, now=_NOW),
        evaluate(_payload(_sro("EXPIRED")), policy, now=_NOW),
        evaluate(_payload(_sro("ACTIVE", _PAST)), policy, now=_NOW),
        evaluate(_payload(_sro("ACTIVE", _FUTURE)), policy, now=_NOW),
    ]
    assert summarize_exclusions(ds) == {
        "STATUS_NOT_ADMISSIBLE": 2,
        "EXPIRED_BY_TIME": 1,
    }


# ─────────────────────────────────────────────────────────────────────
# 2. Policy SOT — the shipped YAML must parse and carry the contract
# ─────────────────────────────────────────────────────────────────────


def test_policy_yaml_is_loadable_and_versioned():
    policy = load_policy()
    assert policy.get("policy_version") == 1
    assert policy.get("sro_schema_version") == 1
    modes = policy.get("modes", {})
    assert set(modes) >= {"default", "historical"}
    assert modes["default"]["admit_statuses"] == ["ACTIVE"]
    assert policy.get("temporal", {}).get("enforce_expires_at") is True
    days = policy.get("expiry_defaults_days", {})
    assert {days.get(k) for k in ("OBS", "DER", "INT", "SPEC")} == {365, 180, 90, 30}


def test_policy_load_failure_degrades_to_failsafe_not_crash(tmp_path):
    policy = load_policy(path=tmp_path / "does-not-exist.yaml")
    assert policy.get("modes", {}).get("default", {}).get("admit_statuses") == ["ACTIVE"]
    assert load_policy(path=tmp_path / "does-not-exist.yaml") is not None


# ─────────────────────────────────────────────────────────────────────
# 3. Writer gate — vector_store stamps SRO v1 at the boundary
# ─────────────────────────────────────────────────────────────────────


def test_vector_store_stamps_sro_v1_block(monkeypatch):
    client = _install_fake_vector_backend(monkeypatch, [])
    result = asyncio.run(
        vector_memory_qdrant.vector_store(
            content='{"claim": "SRO gate wired", "source": "test"}',
            metadata={"source": "test", "verified": True, "truth_class": "OBS"},
            session_id="sro-gate-test",
            actor_id="fi003",
        )
    )
    assert result.get("ok") is True, f"store failed: {result}"
    assert result.get("sro_version") == 1
    assert result.get("expires_at") is not None

    upserted = client.upserted[0]
    sro = upserted["payload"]["sro"]
    assert sro["sro_version"] == 1
    assert sro["expiry"]["status"] == "ACTIVE"
    # OBS truth class → 365-day window per policy SOT
    expires = datetime.fromisoformat(sro["expiry"]["expires_at"])
    assert timedelta(days=360) < (expires - datetime.now(UTC)) < timedelta(days=370)
    assert sro["calibration"]["confidence_at_creation"] == result["truth_score"]


# ─────────────────────────────────────────────────────────────────────
# 4. Reader gate — vector_query refuses + counts, labels in historical
# ─────────────────────────────────────────────────────────────────────


def _mixed_points():
    md = {"truth_score": 1.0, "ontology_class": "memory"}
    return [
        _FakeHit("active-1", {"content": "current fact", "metadata": md,
                              "sro": _sro("ACTIVE", _FUTURE)}),
        _FakeHit("expired-1", {"content": "may 2026 artifact", "metadata": md,
                               "sro": _sro("EXPIRED")}),
        _FakeHit("superseded-1", {"content": "old doctrine", "metadata": md,
                                  "sro": _sro("ACTIVE", _FUTURE, superseded_by="nx")}),
        _FakeHit("timebomb-1", {"content": "status lies, clock speaks", "metadata": md,
                                "sro": _sro("ACTIVE", _PAST)}),
    ]


def test_vector_query_default_mode_excludes_and_counts_refusals(monkeypatch):
    _install_fake_vector_backend(monkeypatch, _mixed_points())
    result = asyncio.run(vector_memory_qdrant.vector_query(query="probe", top_k=10))

    adm = result["admissibility"]
    assert adm["mode"] == "default"
    assert adm["silent"] is False
    assert adm["admitted"] == 1
    assert adm["refused"] == {
        "STATUS_NOT_ADMISSIBLE": 1,
        "SUPERSEDED": 1,
        "EXPIRED_BY_TIME": 1,
    }
    assert [r["point_id"] for r in result["results"]] == ["active-1"]
    assert all("admissibility_label" not in r for r in result["results"])


def test_vector_query_historical_mode_labels_every_non_active(monkeypatch):
    _install_fake_vector_backend(monkeypatch, _mixed_points())
    result = asyncio.run(
        vector_memory_qdrant.vector_query(query="probe", top_k=10, recall_mode="historical")
    )

    assert result["admissibility"]["admitted"] == 4
    assert result["admissibility"]["refused"] == {}
    labelled = {r["point_id"]: r.get("admissibility_label") for r in result["results"]}
    assert labelled == {
        "active-1": None,
        "expired-1": "HISTORICAL",
        "superseded-1": "HISTORICAL",
        "timebomb-1": "HISTORICAL",
    }


def test_vector_query_unknown_mode_fails_closed_everywhere(monkeypatch):
    _install_fake_vector_backend(monkeypatch, _mixed_points())
    result = asyncio.run(
        vector_memory_qdrant.vector_query(query="probe", top_k=10, recall_mode="yolo")
    )
    assert result["ok"] is True  # the query itself is fine
    assert result["results"] == []
    assert result["admissibility"]["refused"] == {"MODE_UNKNOWN": 4}
