"""
tests/golden/organs/judge/test_judge_golden.py — 888_JUDGE Golden Contract Tests

Phase 0: Paradox anchors were removed 2026-07-04 (ABC falsifier proved they
only enriched meta, never affected VerdictCode). Tests updated to verify
the sentinel and that judge.py still imports cleanly.

ECHO/PaW tests added 2026-07-21: schema parity validation, gradient injection,
SCHEMA_BRIDGE integrity.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations


class TestJudgeAnchorRegistry:
    """Verify paradox anchors were intentionally removed, not accidentally lost."""

    def test_paradox_anchors_removed_sentinel(self):
        """The sentinel flag confirms intentional removal, not accidental deletion."""
        from arifosmcp.tools.judge import PARADOX_ANCHORS_REMOVED_TO_CANON

        assert PARADOX_ANCHORS_REMOVED_TO_CANON is True

    def test_judge_module_imports_cleanly(self):
        """Judge module must import without error despite anchor removal."""
        import arifosmcp.tools.judge as judge_mod

        # Verify the module has the expected public surface
        assert hasattr(judge_mod, "PARADOX_ANCHORS_REMOVED_TO_CANON")

    def test_removed_symbols_do_not_exist(self):
        """The old symbols must NOT be re-importable — they are canon, not runtime."""
        import arifosmcp.tools.judge as judge_mod

        removed = [
            "JUDGE_PARADOX_ANCHORS",
            "_JUDGE_BY_CELL",
            "_JUDGE_BY_ID",
            "_inject_judge_paradox",
            "_judge_paradox_for_verdict",
        ]
        for symbol in removed:
            assert not hasattr(judge_mod, symbol), (
                f"{symbol} was removed 2026-07-04 but reappeared. "
                "Check docs/canon/paradox_anchors.md for the preserved canon."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# ECHO/PaW — Schema Parity + Gradient Injection tests (2026-07-21)
# ═══════════════════════════════════════════════════════════════════════════════


class TestSchemaBridge:
    """SCHEMA_BRIDGE: strict 1:1 key parity between prediction and observation."""

    def test_schema_bridge_exists(self):
        """SCHEMA_BRIDGE constant must be importable from judge module."""
        import arifosmcp.tools.judge as judge_mod

        assert hasattr(judge_mod, "SCHEMA_BRIDGE")
        assert isinstance(judge_mod.SCHEMA_BRIDGE, dict)

    def test_schema_bridge_empty_by_default(self):
        """SCHEMA_BRIDGE should be empty — keys already 1:1 parity with substrate."""
        import arifosmcp.tools.judge as judge_mod

        assert judge_mod.SCHEMA_BRIDGE == {}

    def test_observation_schema_keys_frozenset(self):
        """OBSERVATION_SCHEMA_KEYS must be a frozenset of canonical keys."""
        import arifosmcp.tools.judge as judge_mod

        assert hasattr(judge_mod, "OBSERVATION_SCHEMA_KEYS")
        keys = judge_mod.OBSERVATION_SCHEMA_KEYS
        assert isinstance(keys, frozenset)
        # Core WELL substrate keys
        assert "well_score" in keys
        assert "human_ready" in keys
        assert "clarity" in keys
        assert "has_telemetry" in keys
        assert "truth_status" in keys
        assert "active_violations" in keys
        # Vitals keys from arif_measure(mode='vitals')
        assert "g_score" in keys
        assert "delta_S" in keys
        assert "omega" in keys
        assert "psi_le" in keys
        # Evidence keys
        assert "runtime_drift" in keys
        assert "floors_checked" in keys
        assert "floors_violated" in keys


class TestValidateSchemaParity:
    """_validate_schema_parity: congruence check before delta computation."""

    def test_parity_ok_identical_keys(self):
        """Same keys on both sides → parity_ok=True, no drift."""
        from arifosmcp.tools.judge import _validate_schema_parity

        predicted = {"well_score": 85, "human_ready": "OPTIMAL"}
        observed = {"well_score": 80, "human_ready": "FUNCTIONAL"}
        result = _validate_schema_parity(predicted, observed)
        assert result["parity_ok"] is True
        assert result["schema_drift"] is False
        assert result["warning"] is None

    def test_parity_ok_different_keys_not_drift(self):
        """Extra keys not in OBSERVATION_SCHEMA_KEYS don't trigger drift."""
        from arifosmcp.tools.judge import _validate_schema_parity

        predicted = {"well_score": 85, "extra_pred_meta": "foo"}
        observed = {"well_score": 80, "extra_obs_info": "bar"}
        result = _validate_schema_parity(predicted, observed)
        # unmatched keys exist but not valid schema keys → no drift
        assert result["unmatched_predictions"] == ["extra_pred_meta"]
        assert result["unmatched_observations"] == ["extra_obs_info"]

    def test_parity_schema_drift_detected(self):
        """Valid schema key in prediction but not observation → schema_drift."""
        from arifosmcp.tools.judge import _validate_schema_parity

        predicted = {"well_score": 85, "g_score": 0.97}
        observed = {"well_score": 80}  # missing g_score
        result = _validate_schema_parity(predicted, observed)
        assert result["schema_drift"] is True
        assert result["warning"] is not None
        assert "SCHEMA_DRIFT" in result["warning"]

    def test_parity_returns_schema_versions(self):
        """Both sides carry their schema version for version checking."""
        from arifosmcp.tools.judge import _validate_schema_parity

        predicted = {"well_score": 85}
        observed = {"well_score": 80}
        result = _validate_schema_parity(predicted, observed)
        assert result["prediction_schema_version"] == "v1.0"
        assert result["observation_schema_version"] == "v1.0"

    def test_parity_empty_dicts_no_drift(self):
        """Empty prediction and observation → parity_ok with no drift."""
        from arifosmcp.tools.judge import _validate_schema_parity

        result = _validate_schema_parity({}, {})
        assert result["parity_ok"] is True
        assert result["schema_drift"] is False


class TestPredictionGradient:
    """_query_prediction_gradient: L3 gradient injection from L2 deltas."""

    def test_gradient_query_function_exists(self):
        """_query_prediction_gradient must be importable."""
        import arifosmcp.tools.judge as judge_mod

        assert hasattr(judge_mod, "_query_prediction_gradient")

    def test_gradient_query_returns_none_gracefully(self):
        """When no memory backend available, returns None gracefully."""
        from arifosmcp.tools.judge import _query_prediction_gradient

        result = _query_prediction_gradient(session_id="test-nonexistent")
        assert result is None


class TestEchoPawSchemaVersionConstants:
    """PREDICTION_SCHEMA_VERSION and OBSERVATION_SCHEMA_VERSION integrity."""

    def test_schema_versions_defined(self):
        """Both version constants must exist."""
        import arifosmcp.tools.judge as judge_mod

        assert judge_mod.PREDICTION_SCHEMA_VERSION == "v1.0"
        assert judge_mod.OBSERVATION_SCHEMA_VERSION == "v1.0"
