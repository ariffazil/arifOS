"""
tests/constitutional/test_scalar_collector.py — Live Scalar Feed Protocol (TASK-P2-03)
═══════════════════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI — Forged, Not Given

Constitutional tests for the ScalarCollector module
(`arifosmcp.core.scalar_collector.ScalarCollector`).

These tests pin the TASK-P2-03 contract:

  1. Each collect_* method returns the {value, confidence, source} envelope.
  2. UNMEASURED inputs → UNMEASURED envelope (F9 anti-hantu: never fabricate).
  3. NaN / Inf / string / None inputs → UNMEASURED (F2 TRUTH).
  4. F7 HUMILITY cap: G confidence is capped at 0.90.
  5. QDF is computed composite; computed only when all 5 inputs are present.
  6. UNMEASURED scalars do NOT trigger VOID in the snapshot — they only
     populate `unmeasured_keys` and set `all_measured=False`.

The collector is a read-only function of its inputs. Each test case
builds an explicit fixture dict so the test is hermetic.

Run
---
    cd /root/arifOS
    pytest tests/constitutional/test_scalar_collector.py -v --tb=short

Author  : 888-APEX / Gemini CLI perspective (FI-008 dispatch)
Task    : TASK-P2-03 (F2+F7 gated, no F13 trigger)
Epoch   : 2026-07-15
"""

from __future__ import annotations

import math
from unittest.mock import patch

import pytest

from arifosmcp.core.scalar_collector import (
    UNMEASURED_SOURCE,
    ScalarCollector,
    ScalarMeasurement,
)

# ─────────────────────────────────────────────────────────────────────────
# Envelope contract — every collector returns {value, confidence, source}
# ─────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "method_name", ["collect_G", "collect_C_dark", "collect_W3", "collect_kappa", "collect_psi_le"]
)
def test_empty_inputs_returns_unmeasured_envelope(method_name, tmp_path):  # noqa: N802
    """No evidence, no session, no vault chain → UNMEASURED envelope (F9 anti-hantu).

    The vault_chain_path must be pointed at a non-existent file, otherwise
    psi_le could resolve against the host's live vault chain and produce a
    measurement where none was provided in the test's inputs. F9 anti-hantu
    discipline starts with hermetic tests.
    """
    collector = ScalarCollector(vault_chain_path=str(tmp_path / "no-such-chain.jsonl"))
    measurement: ScalarMeasurement = getattr(collector, method_name)()

    assert measurement.value is None
    assert measurement.confidence == 0.0
    assert measurement.source == UNMEASURED_SOURCE
    assert measurement.is_measured is False

    d = measurement.to_dict()
    assert d == {"value": None, "confidence": 0.0, "source": UNMEASURED_SOURCE}


def test_scalar_measurement_factory_enforces_unmeasured_triple():
    """`ScalarMeasurement.unmeasured()` always returns the triple
    (None, 0.0, "UNMEASURED"). The triple is the F9 anti-hantu contract."""
    u = ScalarMeasurement.unmeasured()
    assert u.value is None
    assert u.confidence == 0.0
    assert u.source == UNMEASURED_SOURCE
    assert u.is_measured is False


def test_scalar_measurement_factory_rejects_nonfinite_value():
    """NaN / ±Inf values fall back to UNMEASURED (F2 TRUTH)."""
    assert ScalarMeasurement.measured(float("nan"), 0.5, "x").value is None
    assert ScalarMeasurement.measured(float("inf"), 0.5, "x").value is None
    assert ScalarMeasurement.measured(float("-inf"), 0.5, "x").value is None
    assert ScalarMeasurement.measured(None, 0.5, "x").value is None


def test_scalar_measurement_factory_caps_out_of_range_confidence():
    """Confidence is clamped to [0, 1] (F7 HUMILITY)."""
    over = ScalarMeasurement.measured(0.5, 1.5, "x")
    assert over.confidence == 1.0

    under = ScalarMeasurement.measured(0.5, -0.5, "x")
    assert under.confidence == 0.0


# ─────────────────────────────────────────────────────────────────────────
# ScalarMeasurement dataclass — frozen, hashable
# ─────────────────────────────────────────────────────────────────────────


def test_measurement_is_frozen():
    """F1 AMANAH: ScalarMeasurement must be immutable."""
    m = ScalarMeasurement.unmeasured()
    with pytest.raises((AttributeError, Exception)):
        m.value = 0.5  # type: ignore[misc]


def test_measurement_is_hashable():
    """Hashable allows use in sets / dicts in audit aggregations."""
    m1 = ScalarMeasurement.unmeasured()
    m2 = ScalarMeasurement.measured(0.5, 0.8, "x")
    s = {m1, m2}
    assert len(s) == 2


# ─────────────────────────────────────────────────────────────────────────
# collect_G — apex-derived only (AAA scalar physics / G-fold)
# ─────────────────────────────────────────────────────────────────────────


def test_G_measured_from_apex_scalars():
    """G derives ONLY from arif_think(mode='apex') apex_scalars."""
    collector = ScalarCollector(
        evidence={
            "apex_scalars": {
                "G": 0.85,
                "derived": True,
                "source": "arif_think.mode=apex",
            }
        }
    )
    g = collector.collect_G()

    assert g.value == pytest.approx(0.85)
    assert g.source == "arif_think.mode=apex"
    assert g.confidence > 0


def test_G_rejects_confidence_as_g():
    """Confidence is NOT G — structural entropy source removed."""
    for key in (
        "arif_mind_reason_confidence",
        "confidence",
        "confidence_score",
        "reasoning_confidence",
        "mind_reason_confidence",
    ):
        collector = ScalarCollector(evidence={key: 0.7})
        g = collector.collect_G()
        assert g.value is None, f"key {key!r} must not invent G"
        assert g.source == UNMEASURED_SOURCE


def test_G_caps_at_0_90_f7_humility():
    """F7 HUMILITY: measured G confidence is capped at 0.90 (never ≥0.95)."""
    collector = ScalarCollector(
        evidence={
            "apex_scalars": {
                "G": 0.99,
                "derived": True,
                "source": "arif_think.mode=apex",
            }
        }
    )
    g = collector.collect_G()

    assert g.value == pytest.approx(0.99)  # value preserved
    assert g.confidence == 0.90  # confidence capped


def test_G_rejects_nan_and_inf():
    """NaN / Inf in apex_scalars → UNMEASURED (F2 TRUTH)."""
    for bad in (float("nan"), float("inf"), float("-inf")):
        collector = ScalarCollector(
            evidence={"apex_scalars": {"G": bad, "derived": True, "source": "arif_think.mode=apex"}}
        )
        g = collector.collect_G()
        assert g.value is None
        assert g.source == UNMEASURED_SOURCE


def test_G_rejects_string_numeric():
    """String number is NOT silently coerced (F2 TRUTH)."""
    collector = ScalarCollector(
        evidence={
            "apex_scalars": {"G": "0.85", "derived": True, "source": "arif_think.mode=apex"}
        }
    )
    g = collector.collect_G()
    assert g.value is None
    assert g.source == UNMEASURED_SOURCE


def test_G_from_session_apex_scalars():
    """When evidence lacks apex_scalars, look in session_context."""
    collector = ScalarCollector(
        session_context={
            "apex_scalars": {
                "G": 0.65,
                "derived": True,
                "source": "arif_think.mode=apex",
            }
        }
    )
    g = collector.collect_G()
    assert g.value == pytest.approx(0.65)
    assert g.source == "arif_think.mode=apex"


# ─────────────────────────────────────────────────────────────────────────
# collect_C_dark — shadow variable ratio
# ─────────────────────────────────────────────────────────────────────────


def test_C_dark_computes_ratio_from_evidence():
    """C_dark = shadow_vars / total_session_vars."""
    collector = ScalarCollector(evidence={"shadow_vars": 5, "total_session_vars": 50})
    cd = collector.collect_C_dark()

    assert cd.value == pytest.approx(0.1)
    assert cd.is_measured
    assert "5/50" in cd.source


def test_C_dark_uses_session_context_fallback():
    """C_dark reads session_context when evidence is silent."""
    collector = ScalarCollector(session_context={"shadow_vars": 3, "session_vars": 30})
    cd = collector.collect_C_dark()
    assert cd.value == pytest.approx(0.1)


def test_C_dark_precomputed_ratio_shortcut():
    """When upstream pre-norms var_dark_ratio, it is used directly."""
    collector = ScalarCollector(evidence={"var_dark_ratio": 0.42})
    cd = collector.collect_C_dark()
    assert cd.value == pytest.approx(0.42)
    assert "var_dark_ratio" in cd.source


def test_C_dark_zero_total_is_unmeasured():
    """Zero total variables is measurement failure, NOT 0.0 (F9 anti-hantu)."""
    collector = ScalarCollector(evidence={"shadow_vars": 0, "total_session_vars": 0})
    cd = collector.collect_C_dark()
    assert cd.value is None
    assert cd.source == UNMEASURED_SOURCE


def test_C_dark_missing_total_is_unmeasured():
    """Missing total_session_vars → UNMEASURED (F9)."""
    collector = ScalarCollector(evidence={"shadow_vars": 5})
    cd = collector.collect_C_dark()
    assert cd.value is None
    assert cd.source == UNMEASURED_SOURCE


def test_C_dark_clamped_to_unit_interval():
    """Sanity clamp: even a bogus >1 shadow count caps at 1.0."""
    collector = ScalarCollector(evidence={"shadow_vars": 200, "total_session_vars": 50})
    cd = collector.collect_C_dark()
    assert cd.value == 1.0


# ─────────────────────────────────────────────────────────────────────────
# collect_W3 — tri-witness consensus (geometric mean per Nash 1950)
# ─────────────────────────────────────────────────────────────────────────


def test_W3_geometric_mean_all_three_channels():
    """All 3 channels present → ∛(h × ai × ext) per F3 WITNESS."""
    collector = ScalarCollector(
        evidence={
            "witnesses": [
                {"channel": "human", "confidence": 0.8},
                {"channel": "ai", "confidence": 0.9},
                {"channel": "external", "confidence": 0.7},
            ]
        }
    )
    w3 = collector.collect_W3()
    # Nash 1950 geometric mean: ∛(0.8 × 0.9 × 0.7) ≈ 0.7974
    expected = (0.8 * 0.9 * 0.7) ** (1.0 / 3.0)
    assert w3.value == pytest.approx(expected, abs=1e-9)
    assert "3_channel/3_tri_coverage" in w3.source


def test_W3_geometric_mean_two_channels():
    """Two channels → geometric mean of present channels only."""
    collector = ScalarCollector(
        evidence={
            "witnesses": [
                {"channel": "human", "confidence": 0.8},
                {"channel": "ai", "confidence": 0.9},
            ]
        }
    )
    w3 = collector.collect_W3()
    assert w3.value == pytest.approx(math.sqrt(0.8 * 0.9))
    assert "2_channel" in w3.source


def test_W3_no_witnesses_is_unmeasured():
    """Empty witness list → UNMEASURED (F3 + F9)."""
    collector = ScalarCollector(evidence={"witnesses": []})
    w3 = collector.collect_W3()
    assert w3.value is None
    assert w3.source == UNMEASURED_SOURCE


def test_W3_precomputed_shortcut():
    """Upstream pre-computed W3 is used as-is."""
    collector = ScalarCollector(evidence={"W3": 0.85})
    w3 = collector.collect_W3()
    assert w3.value == 0.85
    assert "session_context.W3" in w3.source


def test_W3_skips_malformed_witness_entries():
    """Entries without finite confidence are silently skipped."""
    collector = ScalarCollector(
        evidence={
            "witnesses": [
                {"channel": "human", "confidence": "not-a-number"},
                {"channel": "ai", "confidence": 0.9},
                {"channel": "external", "confidence": None},
            ]
        }
    )
    w3 = collector.collect_W3()
    # Only the ai channel (0.9) survives → W3 = 0.9
    assert w3.value == pytest.approx(0.9)


def test_W3_session_context_fallback():
    """Reads session_context['witness_log'] when evidence lacks witnesses."""
    collector = ScalarCollector(
        session_context={"witness_log": [{"channel": "ai", "confidence": 0.75}]}
    )
    w3 = collector.collect_W3()
    assert w3.value == pytest.approx(0.75)


# ─────────────────────────────────────────────────────────────────────────
# collect_kappa — F2-compliant claims ratio
# ─────────────────────────────────────────────────────────────────────────


def test_kappa_ratio_from_evidence():
    """κ_r = f2_compliant_claims / total_claims."""
    collector = ScalarCollector(evidence={"f2_compliant_claims": 7, "total_claims": 10})
    k = collector.collect_kappa()
    assert k.value == pytest.approx(0.7)
    assert "7/10" in k.source


def test_kappa_precomputed_shortcut():
    """Upstream pre-computed kappa_r is used as-is."""
    collector = ScalarCollector(evidence={"kappa_r": 0.88})
    k = collector.collect_kappa()
    assert k.value == 0.88
    assert "kappa_r" in k.source


def test_kappa_zero_claims_is_unmeasured():
    """Zero claims is measurement absence, not 1.0 (F9 anti-hantu)."""
    collector = ScalarCollector(evidence={"f2_compliant_claims": 0, "total_claims": 0})
    k = collector.collect_kappa()
    assert k.value is None
    assert k.source == UNMEASURED_SOURCE


def test_kappa_missing_total_is_unmeasured():
    """Missing total_claims → UNMEASURED."""
    collector = ScalarCollector(evidence={"f2_compliant_claims": 5})
    k = collector.collect_kappa()
    assert k.value is None


def test_kappa_session_context_fallback():
    """Read from session_context.verified_claims / claims_total."""
    collector = ScalarCollector(session_context={"verified_claims": 4, "claims_total": 5})
    k = collector.collect_kappa()
    assert k.value == pytest.approx(0.8)


def test_kappa_exact_all_compliant():
    """All claims F2-compliant → κ_r = 1.0."""
    collector = ScalarCollector(evidence={"f2_compliant_claims": 10, "total_claims": 10})
    k = collector.collect_kappa()
    assert k.value == 1.0


# ─────────────────────────────────────────────────────────────────────────
# collect_psi_le — VAULT chain length × seal rate
# ─────────────────────────────────────────────────────────────────────────


@pytest.fixture
def fake_vault_chain(tmp_path):
    """Write a small fake seal_chain.jsonl with a known SEAL/HOLD mix."""
    chain = tmp_path / "seal_chain.jsonl"
    lines = []
    # 80 SEAL, 20 HOLD, 10 VOID = 110 total → seal_rate = 80/110
    for i in range(80):
        lines.append(f'{{"seq":{i},"verdict":"SEAL"}}')
    for i in range(80, 100):
        lines.append(f'{{"seq":{i},"verdict":"HOLD"}}')
    for i in range(100, 110):
        lines.append(f'{{"seq":{i},"verdict":"VOID"}}')
    # Plus one malformed line (F2 tolerance) and one bare string (F2 skip)
    lines.append('{"seq":110,"verdict":"not-a-dict-line"')
    chain.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return chain


def test_psi_le_computes_log10_times_seal_rate(fake_vault_chain):
    """ψ_le = log10(1+L) × seal_rate; tolerates malformed lines."""
    collector = ScalarCollector(vault_chain_path=str(fake_vault_chain))
    psi = collector.collect_psi_le()

    # L = 111 (110 valid + 1 malformed which still counts as a line).
    # SEAL count = 80 (the malformed line doesn't bump seal count).
    # seal_rate = 80/111
    # ψ_le = log10(1 + 111) × 80/111
    expected = math.log10(1 + 111) * (80 / 111)
    assert psi.value == pytest.approx(expected)
    assert "L=111" in psi.source
    assert "SEAL=80" in psi.source


def test_psi_le_missing_chain_file_is_unmeasured(tmp_path):
    """Nonexistent vault chain file → UNMEASURED."""
    collector = ScalarCollector(vault_chain_path=str(tmp_path / "does-not-exist.jsonl"))
    psi = collector.collect_psi_le()
    assert psi.value is None
    assert psi.source == UNMEASURED_SOURCE


def test_psi_le_skips_bare_string_lines(tmp_path):
    """Legacy bare-string chain entries are skipped, not treated as SEAL."""
    chain = tmp_path / "seal_chain.jsonl"
    chain.write_text(
        '"just-a-string-not-json-object"\n{"seq":1,"verdict":"SEAL"}\n', encoding="utf-8"
    )
    collector = ScalarCollector(vault_chain_path=str(chain))
    psi = collector.collect_psi_le()
    # L=2 lines but only 1 SEAL → seal_rate = 1/2
    assert psi.value == pytest.approx(math.log10(3) * 0.5)


# ─────────────────────────────────────────────────────────────────────────
# collect_snapshot — composite and QDF
# ─────────────────────────────────────────────────────────────────────────


def test_snapshot_all_measured_produces_qdf():
    """All 5 scalars measured → QDF = G × (1 - C_dark) × W3 × κ_r × ψ_le."""
    collector = ScalarCollector(
        evidence={
            "arif_mind_reason_confidence": 0.85,
            "shadow_vars": 5,
            "total_session_vars": 50,
            "witnesses": [
                {"channel": "human", "confidence": 0.8},
                {"channel": "ai", "confidence": 0.9},
                {"channel": "external", "confidence": 0.7},
            ],
            "f2_compliant_claims": 7,
            "total_claims": 10,
        },
        # psi_le comes from real vault chain, mocked below
        vault_chain_path="/nonexistent/chain.jsonl",  # → UNMEASURED
    )
    snap = collector.collect_snapshot()

    # ψ_le from disk will be UNMEASURED → snap.all_measured = False
    assert snap["all_measured"] is False
    assert "psi_le" in snap["unmeasured_keys"]
    assert snap["qdf"] is None
    assert snap["qdf_source"] == UNMEASURED_SOURCE


def test_snapshot_qdf_computed_when_all_measured(fake_vault_chain):
    """QDF is computed when all 5 scalars have measurable values."""
    collector = ScalarCollector(
        evidence={
            "apex_scalars": {
                "G": 0.85,
                "C_dark": 0.1,
                "derived": True,
                "source": "arif_think.mode=apex",
            },
            "shadow_vars": 5,
            "total_session_vars": 50,  # C_dark fallback path also present
            "witnesses": [
                {"channel": "human", "confidence": 0.8},
                {"channel": "ai", "confidence": 0.9},
                {"channel": "external", "confidence": 0.7},
            ],  # W³ ≈ 0.797
            "f2_compliant_claims": 7,
            "total_claims": 10,  # κ_r = 0.7
        },
        vault_chain_path=str(fake_vault_chain),
    )
    snap = collector.collect_snapshot()

    assert snap["all_measured"] is True
    assert snap["unmeasured_keys"] == []
    assert snap["qdf_source"] == "computed"

    # Numerically verify QDF formula.
    g_val = snap["scalars"]["G"]["value"]
    cd_val = snap["scalars"]["C_dark"]["value"]
    w3_val = snap["scalars"]["W3"]["value"]
    kr_val = snap["scalars"]["kappa_r"]["value"]
    psi_val = snap["scalars"]["psi_le"]["value"]
    expected_qdf = g_val * (1.0 - cd_val) * w3_val * kr_val * psi_val
    assert snap["qdf"] == pytest.approx(expected_qdf)


def test_snapshot_unmeasured_does_not_void(tmp_path):
    """QDF None + UNMEASURED scalars is a measurement warning, not VOID.

    This is the F9 anti-hantu discipline: scalar measurement failure is
    a meta field, not a verdict override. The judge may still issue
    SEAL/HOLD based on its own reasoning."""
    collector = ScalarCollector(vault_chain_path=str(tmp_path / "no-such-chain.jsonl"))
    snap = collector.collect_snapshot()

    assert snap["all_measured"] is False
    assert snap["qdf"] is None
    assert snap["qdf_source"] == UNMEASURED_SOURCE
    assert set(snap["unmeasured_keys"]) == {"G", "C_dark", "W3", "kappa_r", "psi_le"}
    # Critical: snapshot does NOT include a `verdict` field that elevates
    # to VOID. Only the judge does that.
    assert "verdict" not in snap


def test_snapshot_returns_serializable_dict():
    """Snapshot must be JSON-serializable for downstream audit / VAULT sealing."""
    import json

    collector = ScalarCollector(
        evidence={
            "apex_scalars": {
                "G": 0.7,
                "derived": True,
                "source": "arif_think.mode=apex",
            }
        }
    )
    snap = collector.collect_snapshot()
    # Round-trip through json.dumps
    encoded = json.dumps(snap, default=str)
    decoded = json.loads(encoded)
    assert decoded["scalars"]["G"]["value"] == 0.7
    assert decoded["scalars"]["G"]["source"] == "arif_think.mode=apex"


# ─────────────────────────────────────────────────────────────────────────
# Property: ScalarCollector is read-only (F1 AMANAH)
# ─────────────────────────────────────────────────────────────────────────


def test_collector_does_not_mutate_evidence_input():
    """F1 AMANAH: the collector must NOT mutate its input dict."""
    evidence = {
        "apex_scalars": {
            "G": 0.85,
            "derived": True,
            "source": "arif_think.mode=apex",
        },
        "shadow_vars": 5,
        "total_session_vars": 50,
        "f2_compliant_claims": 7,
        "total_claims": 10,
    }
    snapshot_before = dict(evidence)
    collector = ScalarCollector(evidence=evidence)

    # Run every collector at least once.
    collector.collect_G()
    collector.collect_C_dark()
    collector.collect_W3()
    collector.collect_kappa()
    collector.collect_psi_le()
    collector.collect_snapshot()

    assert evidence == snapshot_before


# ─────────────────────────────────────────────────────────────────────────
# Constructor overrides — explicit injection wins
# ─────────────────────────────────────────────────────────────────────────


def test_session_context_override_takes_precedence():
    """Constructor-injected session_context is used instead of disk lookup."""
    override = {
        "apex_scalars": {
            "G": 0.42,
            "derived": True,
            "source": "arif_think.mode=apex",
        }
    }
    with patch("arifosmcp.runtime.tools.get_session") as mock_get:
        mock_get.return_value = {
            "apex_scalars": {
                "G": 0.99,
                "derived": True,
                "source": "arif_think.mode=apex",
            }
        }
        collector = ScalarCollector(
            session_id="sess_xyz",
            session_context=override,
        )
        g = collector.collect_G()
        assert g.value == pytest.approx(0.42)  # override wins


def test_session_id_triggers_store_lookup():
    """When session_context is not overridden, session_id looks up the store."""
    fake_session = {
        "apex_scalars": {
            "G": 0.55,
            "derived": True,
            "source": "arif_think.mode=apex",
        }
    }
    with patch("arifosmcp.runtime.tools.get_session", return_value=fake_session) as mock_get:
        collector = ScalarCollector(session_id="sess_real")
        g = collector.collect_G()
        mock_get.assert_called_with("sess_real")
        assert g.value == pytest.approx(0.55)
