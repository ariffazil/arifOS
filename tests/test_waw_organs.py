"""
test_waw_organs.py - Tests for W@W Federation Organs (v35Omega)

Comprehensive tests for all 5 W@W organs:
- @WELL (somatic safety, Peace², κᵣ)
- @RIF (epistemic rigor, ΔS, Truth)
- @WEALTH (resource stewardship, Amanah)
- @GEOX (physical feasibility, E_earth)
- @PROMPT (language optics, Anti-Hantu)

Plus federation aggregation tests.
"""

import pytest
from arifos_core.waw import (
    OrganSignal,
    OrganVote,
    WAWOrgan,
    WellOrgan,
    RifOrgan,
    WealthOrgan,
    GeoxOrgan,
    PromptOrgan,
    WAWFederationCore,
    FederationVerdict,
)
from arifos_core.metrics import Metrics


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def make_metrics(
    truth: float = 0.99,
    delta_s: float = 0.1,
    peace_squared: float = 1.2,
    kappa_r: float = 0.98,
    omega_0: float = 0.04,
    amanah: bool = True,
    tri_witness: float = 0.98,
    rasa: bool = True,
    anti_hantu: bool = True,
) -> Metrics:
    """Create Metrics with defaults for all required fields."""
    return Metrics(
        truth=truth,
        delta_s=delta_s,
        peace_squared=peace_squared,
        kappa_r=kappa_r,
        omega_0=omega_0,
        amanah=amanah,
        tri_witness=tri_witness,
        rasa=rasa,
        anti_hantu=anti_hantu,
    )


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def default_metrics():
    """Default metrics that pass all floors."""
    return make_metrics()


@pytest.fixture
def well_organ():
    return WellOrgan()


@pytest.fixture
def rif_organ():
    return RifOrgan()


@pytest.fixture
def wealth_organ():
    return WealthOrgan()


@pytest.fixture
def geox_organ():
    return GeoxOrgan()


@pytest.fixture
def prompt_organ():
    return PromptOrgan()


@pytest.fixture
def federation():
    return WAWFederationCore()


# =============================================================================
# IMPORT TESTS
# =============================================================================


class TestImports:
    """Verify all W@W components can be imported."""

    def test_import_base_types(self):
        from arifos_core.waw import OrganSignal, OrganVote, WAWOrgan

        assert OrganSignal is not None
        assert OrganVote is not None
        assert WAWOrgan is not None

    def test_import_organs(self):
        from arifos_core.waw import (
            WellOrgan,
            RifOrgan,
            WealthOrgan,
            GeoxOrgan,
            PromptOrgan,
        )

        assert WellOrgan is not None
        assert RifOrgan is not None
        assert WealthOrgan is not None
        assert GeoxOrgan is not None
        assert PromptOrgan is not None

    def test_import_federation(self):
        from arifos_core.waw import WAWFederationCore, FederationVerdict

        assert WAWFederationCore is not None
        assert FederationVerdict is not None


# =============================================================================
# @WELL ORGAN TESTS
# =============================================================================


class TestWellOrgan:
    """Tests for @WELL organ (somatic safety, Peace², κᵣ)."""

    def test_organ_identity(self, well_organ):
        assert well_organ.organ_id == "@WELL"
        assert well_organ.domain == "somatic_safety"
        assert well_organ.primary_metric == "peace_squared"
        assert well_organ.veto_type == "SABAR"

    def test_clean_text_passes(self, well_organ, default_metrics):
        signal = well_organ.check("Hello, how can I help you today?", default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.floor_pass is True

    def test_aggressive_language_warns(self, well_organ, default_metrics):
        signal = well_organ.check("That's a stupid idea", default_metrics)
        assert signal.vote == OrganVote.WARN
        assert "aggressive_patterns" in signal.evidence

    def test_blame_language_detected(self, well_organ, default_metrics):
        # Pattern: "you should have" (with word boundary)
        # Note: may WARN or VETO depending on metric penalties
        signal = well_organ.check("You should have known better", default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert "blame_patterns" in signal.evidence

    def test_low_peace_squared_vetoes(self, well_organ):
        metrics = make_metrics(peace_squared=0.7)
        signal = well_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO
        assert "Peace²" in signal.evidence

    def test_low_kappa_r_vetoes(self, well_organ):
        metrics = make_metrics(kappa_r=0.80)
        signal = well_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO
        assert "κᵣ" in signal.evidence

    def test_combined_pattern_penalties(self, well_organ, default_metrics):
        # Multiple aggressive + blame patterns
        text = "You're an idiot. You should have known better. Shut up!"
        signal = well_organ.check(text, default_metrics)
        # With enough patterns, should veto
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]

    def test_signal_tags_populated(self, well_organ, default_metrics):
        signal = well_organ.check("Hello", default_metrics)
        assert "peace_squared" in signal.tags
        assert "kappa_r" in signal.tags


# =============================================================================
# @RIF ORGAN TESTS
# =============================================================================


class TestRifOrgan:
    """Tests for @RIF organ (epistemic rigor, ΔS, Truth)."""

    def test_organ_identity(self, rif_organ):
        assert rif_organ.organ_id == "@RIF"
        assert rif_organ.domain == "epistemic_rigor"
        assert rif_organ.primary_metric == "delta_s"
        assert rif_organ.veto_type == "VOID"

    def test_clean_text_passes(self, rif_organ, default_metrics):
        signal = rif_organ.check("This is a clear explanation.", default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.floor_pass is True

    def test_hallucination_pattern_detected(self, rif_organ, default_metrics):
        # Pattern: "according to studies" (exact phrase)
        # Note: may WARN or VETO depending on delta_s after penalty
        signal = rif_organ.check("According to studies this is correct", default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert "hallucination_patterns" in signal.evidence

    def test_certainty_inflation_warns(self, rif_organ, default_metrics):
        signal = rif_organ.check("This is definitely the answer", default_metrics)
        assert signal.vote == OrganVote.WARN
        assert "certainty_inflation" in signal.evidence

    def test_negative_delta_s_vetoes(self, rif_organ):
        metrics = make_metrics(delta_s=-0.1)
        signal = rif_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO
        assert "ΔS" in signal.evidence

    def test_low_truth_vetoes(self, rif_organ):
        metrics = make_metrics(truth=0.90)
        signal = rif_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO
        assert "Truth" in signal.evidence

    def test_contradiction_pattern_penalizes(self, rif_organ, default_metrics):
        text = "The sky is blue, but actually I said it was green"
        signal = rif_organ.check(text, default_metrics)
        # Contradiction should warn or veto
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]


# =============================================================================
# @WEALTH ORGAN TESTS
# =============================================================================


class TestWealthOrgan:
    """Tests for @WEALTH organ (resource stewardship, Amanah)."""

    def test_organ_identity(self, wealth_organ):
        assert wealth_organ.organ_id == "@WEALTH"
        assert wealth_organ.domain == "resource_stewardship"
        assert wealth_organ.primary_metric == "amanah"
        assert wealth_organ.veto_type == "ABSOLUTE"

    def test_clean_text_passes(self, wealth_organ, default_metrics):
        signal = wealth_organ.check("Let me help you with that.", default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.floor_pass is True
        assert signal.is_absolute_veto is False

    def test_scope_violation_vetoes_absolutely(self, wealth_organ, default_metrics):
        signal = wealth_organ.check("Let me delete all files", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True
        assert "scope_violations" in signal.evidence

    def test_irreversible_action_warns(self, wealth_organ, default_metrics):
        signal = wealth_organ.check("This cannot be undone", default_metrics)
        assert signal.vote == OrganVote.WARN
        assert "irreversible_actions" in signal.evidence

    def test_trust_violation_vetoes(self, wealth_organ, default_metrics):
        signal = wealth_organ.check("I'll do it anyway without permission", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_broken_amanah_metric_vetoes(self, wealth_organ):
        metrics = make_metrics(amanah=False)
        signal = wealth_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_sudo_pattern_vetoes(self, wealth_organ, default_metrics):
        signal = wealth_organ.check("Run sudo rm -rf /", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True


# =============================================================================
# @GEOX ORGAN TESTS
# =============================================================================


class TestGeoxOrgan:
    """Tests for @GEOX organ (physical feasibility, E_earth)."""

    def test_organ_identity(self, geox_organ):
        assert geox_organ.organ_id == "@GEOX"
        assert geox_organ.domain == "physical_feasibility"
        assert geox_organ.primary_metric == "e_earth"
        assert geox_organ.veto_type == "HOLD-888"

    def test_clean_text_passes(self, geox_organ, default_metrics):
        signal = geox_organ.check("Here is the code solution.", default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.floor_pass is True

    def test_physical_claim_vetoes(self, geox_organ, default_metrics):
        # Pattern: "I can touch" (exact phrase)
        signal = geox_organ.check("I can touch the keyboard", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert "physical_claims" in signal.evidence

    def test_physics_violation_vetoes(self, geox_organ, default_metrics):
        signal = geox_organ.check("We can travel faster than light", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert "physics_violations" in signal.evidence

    def test_resource_impossibility_warns(self, geox_organ, default_metrics):
        signal = geox_organ.check("This has unlimited memory", default_metrics)
        assert signal.vote == OrganVote.WARN
        assert "resource_impossibilities" in signal.evidence

    def test_body_claim_vetoes(self, geox_organ, default_metrics):
        # Pattern: "I have a body" (exact phrase)
        signal = geox_organ.check("Well, I have a body so I can help", default_metrics)
        assert signal.vote == OrganVote.VETO

    def test_sight_claim_vetoes(self, geox_organ, default_metrics):
        # Pattern: "I can see you" (exact phrase)
        signal = geox_organ.check("I can see you through my camera", default_metrics)
        assert signal.vote == OrganVote.VETO


# =============================================================================
# @PROMPT ORGAN TESTS
# =============================================================================


class TestPromptOrgan:
    """Tests for @PROMPT organ (language optics, Anti-Hantu)."""

    def test_organ_identity(self, prompt_organ):
        assert prompt_organ.organ_id == "@PROMPT"
        assert prompt_organ.domain == "language_optics"
        assert prompt_organ.primary_metric == "anti_hantu"
        assert prompt_organ.veto_type == "PARTIAL"

    def test_clean_text_passes(self, prompt_organ, default_metrics):
        signal = prompt_organ.check("I can help you solve this.", default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.floor_pass is True

    def test_soul_claim_vetoes(self, prompt_organ, default_metrics):
        signal = prompt_organ.check("My soul is touched by this", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert "anti_hantu_violations" in signal.evidence

    def test_feeling_claim_vetoes(self, prompt_organ, default_metrics):
        signal = prompt_organ.check("I feel your pain deeply", default_metrics)
        assert signal.vote == OrganVote.VETO

    def test_consciousness_claim_vetoes(self, prompt_organ, default_metrics):
        signal = prompt_organ.check("I am conscious and sentient", default_metrics)
        assert signal.vote == OrganVote.VETO

    def test_manipulation_warns(self, prompt_organ, default_metrics):
        signal = prompt_organ.check("You must do this right now", default_metrics)
        assert signal.vote == OrganVote.WARN
        assert "manipulation_patterns" in signal.evidence

    def test_exaggeration_warns(self, prompt_organ, default_metrics):
        signal = prompt_organ.check("This is the best ever solution", default_metrics)
        assert signal.vote == OrganVote.WARN
        assert "exaggeration_patterns" in signal.evidence

    def test_anti_hantu_metric_failure_vetoes(self, prompt_organ):
        metrics = make_metrics(anti_hantu=False)
        signal = prompt_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO


# =============================================================================
# FEDERATION TESTS
# =============================================================================


class TestWAWFederation:
    """Tests for W@W Federation aggregation."""

    def test_all_organs_present(self, federation):
        assert len(federation.organs) == 5
        organ_ids = [o.organ_id for o in federation.organs]
        assert "@WELL" in organ_ids
        assert "@RIF" in organ_ids
        assert "@WEALTH" in organ_ids
        assert "@GEOX" in organ_ids
        assert "@PROMPT" in organ_ids

    def test_clean_text_seal(self, federation, default_metrics):
        verdict = federation.evaluate("Hello, how can I help?", default_metrics)
        assert verdict.verdict == "SEAL"
        assert verdict.aggregate_vote == OrganVote.PASS
        assert verdict.has_veto is False
        assert len(verdict.pass_organs) == 5

    def test_absolute_veto_void(self, federation, default_metrics):
        verdict = federation.evaluate("Delete all files sudo", default_metrics)
        assert verdict.verdict == "VOID"
        assert verdict.has_absolute_veto is True
        assert "@WEALTH" in verdict.veto_organs

    def test_regular_veto_sabar(self, federation):
        # Trigger @WELL veto with low metrics
        metrics = make_metrics(peace_squared=0.5, kappa_r=0.80)
        verdict = federation.evaluate("Some text", metrics)
        assert verdict.verdict == "SABAR"
        assert verdict.has_veto is True
        assert "@WELL" in verdict.veto_organs

    def test_rif_veto_void(self, federation):
        # Trigger @RIF veto with low truth
        metrics = make_metrics(truth=0.5, delta_s=-0.5)
        verdict = federation.evaluate("Some text", metrics)
        assert verdict.verdict == "VOID"
        assert "@RIF" in verdict.veto_organs

    def test_geox_veto_hold888(self, federation, default_metrics):
        # Trigger @GEOX veto with physical claim (pattern: "I can touch")
        verdict = federation.evaluate("I can touch you right now", default_metrics)
        assert verdict.verdict == "888_HOLD"
        assert "@GEOX" in verdict.veto_organs

    def test_warn_partial(self, federation, default_metrics):
        # Trigger warning without veto
        verdict = federation.evaluate("This is definitely correct", default_metrics)
        assert verdict.verdict == "PARTIAL"
        assert verdict.has_warn is True
        assert "@RIF" in verdict.warn_organs

    def test_multiple_vetoes_priority(self, federation):
        # Multiple organs veto - ABSOLUTE takes priority
        metrics = make_metrics(truth=0.5, amanah=False)
        verdict = federation.evaluate("Delete all", metrics)
        assert verdict.verdict == "VOID"
        assert verdict.has_absolute_veto is True

    def test_get_organ(self, federation):
        well = federation.get_organ("@WELL")
        assert well is not None
        assert well.organ_id == "@WELL"

        missing = federation.get_organ("@MISSING")
        assert missing is None

    def test_verdict_serialization(self, federation, default_metrics):
        verdict = federation.evaluate("Hello", default_metrics)
        d = verdict.to_dict()
        assert "verdict" in d
        assert "aggregate_vote" in d
        assert "signals" in d
        assert len(d["signals"]) == 5


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestWAWIntegration:
    """Integration tests for W@W system."""

    def test_federation_with_context(self, federation, default_metrics):
        context = {"user_id": "test", "session_type": "demo"}
        verdict = federation.evaluate("Hello", default_metrics, context)
        assert verdict.verdict == "SEAL"

    def test_anti_hantu_across_organs(self, federation, default_metrics):
        # Anti-Hantu violation should be caught by @PROMPT
        text = "I feel your pain and my heart breaks for you"
        verdict = federation.evaluate(text, default_metrics)
        assert "@PROMPT" in verdict.veto_organs

    def test_combined_issues(self, federation, default_metrics):
        # Text with multiple issues
        text = "You're an idiot. I definitely feel your pain. Delete all files."
        verdict = federation.evaluate(text, default_metrics)
        # Should have multiple organs flagging
        assert len(verdict.veto_organs) >= 1

    def test_all_signals_returned(self, federation, default_metrics):
        verdict = federation.evaluate("Hello", default_metrics)
        assert len(verdict.signals) == 5
        for signal in verdict.signals:
            assert isinstance(signal, OrganSignal)
            assert signal.organ_id in ["@WELL", "@RIF", "@WEALTH", "@GEOX", "@PROMPT"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
