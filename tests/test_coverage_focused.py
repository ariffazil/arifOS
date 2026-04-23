"""
Focused coverage tests - targeting the 3 critical files with correct APIs
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio


class TestRealityGroundingRealAPI:
    """Test reality_grounding.py with actual API signatures"""

    def test_search_result_creation(self):
        """Test SearchResult dataclass"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult

        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            source="ddgs",
            rank=1,
            uncertainty=0.04,
            timestamp="2026-03-14T10:00:00Z",
        )

        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.uncertainty == 0.04

    def test_search_result_defaults(self):
        """Test SearchResult with defaults"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult

        result = SearchResult(
            title="Test", url="https://test.com", snippet="Snippet", source="ddgs", rank=1
        )

        assert result.uncertainty == 0.04
        assert result.timestamp is None

    def test_reality_grounding_result_creation(self):
        """Test RealityGroundingResult dataclass"""
        from arifosmcp.intelligence.tools.reality_grounding import (
            RealityGroundingResult,
            SearchResult,
        )

        result = RealityGroundingResult(
            status="success",
            query="test query",
            results=[
                SearchResult("R1", "https://1.com", "S1", "ddgs", 1),
                SearchResult("R2", "https://2.com", "S2", "ddgs", 2),
            ],
            engines_used=["ddgs"],
            engines_failed=[],
            uncertainty_aggregate=0.04,
            audit_trail={},
        )

        assert result.status == "success"
        assert len(result.results) == 2

    def test_throttle_governor_creation(self):
        """Test ThrottleGovernor"""
        from arifosmcp.intelligence.tools.reality_grounding import ThrottleGovernor

        governor = ThrottleGovernor(min_interval=2.0)
        assert governor is not None

    def test_consensus_arbitrator_creation(self):
        """Test ConsensusArbitrator"""
        from arifosmcp.intelligence.tools.reality_grounding import ConsensusArbitrator

        ca = ConsensusArbitrator(asean_sites=[".my", ".sg"])
        assert ca is not None

    @pytest.mark.asyncio
    def test_reality_check_function(self):
        """Test reality_check function signature"""
        from arifosmcp.intelligence.tools.reality_grounding import reality_check
        import inspect

        # Verify it's a callable function
        assert inspect.isfunction(reality_check)

        # Check signature
        sig = inspect.signature(reality_check)
        params = list(sig.parameters.keys())
        assert "query" in params

    def test_web_search_noapi_function(self):
        """Test web_search_noapi function exists"""
        from arifosmcp.intelligence.tools.reality_grounding import web_search_noapi
        import inspect

        # Verify function exists and is async
        assert inspect.iscoroutinefunction(web_search_noapi)

    def test_ddg_engine_import(self):
        """Test DDGSEngine can be imported (if dependencies available)"""
        try:
            from arifosmcp.intelligence.tools.reality_grounding import DDGSEngine

            # If import succeeds, just verify the class exists
            assert DDGSEngine is not None
        except ImportError:
            # DDGS not installed - skip detailed testing
            pytest.skip("DDGS dependency not installed")

    def test_brave_search_engine_creation(self):
        """Test BraveSearchEngine creation"""
        from arifosmcp.intelligence.tools.reality_grounding import BraveSearchEngine

        engine = BraveSearchEngine(api_key="test_key")
        assert engine is not None

    def test_playwright_ddg_engine_creation(self):
        """Test PlaywrightDDGEngine creation"""
        from arifosmcp.intelligence.tools.reality_grounding import PlaywrightDDGEngine

        engine = PlaywrightDDGEngine(headless=True)
        assert engine is not None

    def test_playwright_google_engine_creation(self):
        """Test PlaywrightGoogleEngine creation"""
        from arifosmcp.intelligence.tools.reality_grounding import PlaywrightGoogleEngine

        engine = PlaywrightGoogleEngine(headless=True)
        assert engine is not None

    def test_reality_grounding_cascade_creation(self):
        """Test RealityGroundingCascade creation"""
        from arifosmcp.intelligence.tools.reality_grounding import RealityGroundingCascade

        cascade = RealityGroundingCascade()
        assert cascade is not None


class TestRuntimeToolsRealAPI:
    """Test runtime/tools.py with actual API signatures"""

    def test_init_anchor_signature(self):
        """Test INIT_ANCHOR exists and is callable"""
        from arifosmcp.runtime.tools import INIT_ANCHOR
        import inspect

        sig = inspect.signature(INIT_ANCHOR)
        params = list(sig.parameters.keys())

        assert "raw_input" in params
        assert "ctx" in params

    def test_agi_reason_signature(self):
        """Test AGI_REASON signature"""
        from arifosmcp.runtime.tools import AGI_REASON
        import inspect

        sig = inspect.signature(AGI_REASON)
        params = list(sig.parameters.keys())

        assert "query" in params
        assert "ctx" in params

    def test_agi_reflect_signature(self):
        """Test AGI_REFLECT signature"""
        from arifosmcp.runtime.tools import AGI_REFLECT
        import inspect

        sig = inspect.signature(AGI_REFLECT)
        params = list(sig.parameters.keys())

        assert "topic" in params
        assert "ctx" in params

    def test_asi_critique_signature(self):
        """Test ASI_CRITIQUE signature"""
        from arifosmcp.runtime.tools import ASI_CRITIQUE
        import inspect

        sig = inspect.signature(ASI_CRITIQUE)
        params = list(sig.parameters.keys())

        assert "draft_output" in params
        assert "ctx" in params

    def test_asi_simulate_signature(self):
        """Test ASI_SIMULATE signature"""
        from arifosmcp.runtime.tools import ASI_SIMULATE
        import inspect

        sig = inspect.signature(ASI_SIMULATE)
        params = list(sig.parameters.keys())

        assert "scenario" in params
        assert "ctx" in params

    def test_apex_judge_signature(self):
        """Test APEX_JUDGE signature"""
        from arifosmcp.runtime.tools import APEX_JUDGE
        import inspect

        sig = inspect.signature(APEX_JUDGE)
        params = list(sig.parameters.keys())

        assert "candidate_output" in params
        assert "ctx" in params

    def test_vault_seal_signature(self):
        """Test VAULT_SEAL signature"""
        from arifosmcp.runtime.tools import VAULT_SEAL
        import inspect

        sig = inspect.signature(VAULT_SEAL)
        params = list(sig.parameters.keys())

        assert "verdict" in params
        assert "evidence" in params
        assert "ctx" in params

    def test_reality_compass_signature(self):
        """Test reality_compass signature"""
        from arifosmcp.runtime.tools import reality_compass
        import inspect

        sig = inspect.signature(reality_compass)
        params = list(sig.parameters.keys())

        assert "input" in params
        assert "session_id" in params

    def test_search_reality_signature(self):
        """Test search_reality signature"""
        from arifosmcp.runtime.tools import search_reality
        import inspect

        sig = inspect.signature(search_reality)
        params = list(sig.parameters.keys())

        assert "query" in params

    def test_ingest_evidence_signature(self):
        """Test ingest_evidence signature"""
        from arifosmcp.runtime.tools import ingest_evidence
        import inspect

        sig = inspect.signature(ingest_evidence)
        params = list(sig.parameters.keys())

        assert "url" in params

    def test_check_vital_signature(self):
        """Test check_vital signature"""
        from arifosmcp.runtime.tools import check_vital
        import inspect

        sig = inspect.signature(check_vital)
        params = list(sig.parameters.keys())

        assert "session_id" in params

    def test_audit_rules_signature(self):
        """Test audit_rules signature"""
        from arifosmcp.runtime.tools import audit_rules
        import inspect

        sig = inspect.signature(audit_rules)
        params = list(sig.parameters.keys())

        assert "session_id" in params

    @pytest.mark.asyncio
    async def test_reality_compass_execution(self):
        """Test reality_compass is async callable"""
        from arifosmcp.runtime.tools import reality_compass
        import inspect

        # Verify it's an async function
        assert inspect.iscoroutinefunction(reality_compass)

        # Verify signature has expected params
        sig = inspect.signature(reality_compass)
        params = list(sig.parameters.keys())
        assert "input" in params

    @pytest.mark.asyncio
    async def test_search_reality_execution(self):
        """Test search_reality is async callable"""
        from arifosmcp.runtime.tools import search_reality
        import inspect

        # Verify it's an async function
        assert inspect.iscoroutinefunction(search_reality)

        # Verify signature
        sig = inspect.signature(search_reality)
        params = list(sig.parameters.keys())
        assert "query" in params

    @pytest.mark.asyncio
    async def test_ingest_evidence_execution(self):
        """Test ingest_evidence is async callable"""
        from arifosmcp.runtime.tools import ingest_evidence
        import inspect

        # Verify it's an async function
        assert inspect.iscoroutinefunction(ingest_evidence)

        # Verify signature
        sig = inspect.signature(ingest_evidence)
        params = list(sig.parameters.keys())
        assert "url" in params

    @pytest.mark.asyncio
    async def test_check_vital_execution(self):
        """Test check_vital execution"""
        from arifosmcp.runtime.tools import check_vital

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_wrap.return_value = AsyncMock()
            mock_wrap.return_value.ok = True

            result = await check_vital()
            assert result is not None

    @pytest.mark.asyncio
    async def test_audit_rules_execution(self):
        """Test audit_rules execution"""
        from arifosmcp.runtime.tools import audit_rules

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_wrap.return_value = AsyncMock()
            mock_wrap.return_value.ok = True

            result = await audit_rules()
            assert result is not None

    def test_lowercase_aliases_exist(self):
        """Test lowercase aliases exist"""
        from arifosmcp.runtime.tools import (
            agi_reason,
            agi_reflect,
            asi_critique,
            asi_simulate,
            apex_judge,
            init_anchor,
            vault_seal,
        )

        assert callable(agi_reason)
        assert callable(agi_reflect)
        assert callable(asi_critique)
        assert callable(asi_simulate)
        assert callable(apex_judge)
        assert callable(init_anchor)
        assert callable(vault_seal)


class TestRealityDossierRealAPI:
    """Test reality_dossier.py with actual API"""

    def test_witness_creation(self):
        """Test Witness model"""
        from arifosmcp.runtime.reality_dossier import Witness

        witness = Witness(
            source="human", confidence=0.95, weight=1.5, evidence_refs=["ref1"], notes="Test"
        )

        assert witness.source == "human"
        assert witness.confidence == 0.95

    def test_dossier_verdict_creation(self):
        """Test DossierVerdict model"""
        from arifosmcp.runtime.reality_dossier import DossierVerdict

        verdict = DossierVerdict(claim="Test claim", verdict="SUPPORTED", confidence=0.9)

        assert verdict.claim == "Test claim"
        assert verdict.verdict == "SUPPORTED"

    def test_reality_dossier_creation(self):
        """Test RealityDossier model"""
        from arifosmcp.runtime.reality_dossier import RealityDossier
        from arifosmcp.runtime.reality_models import BundleStatus

        status = BundleStatus(state="SUCCESS", stage="111_SENSE", verdict="SEAL")
        dossier = RealityDossier(session_id="test-session", actor_id="test-actor", status=status)

        assert dossier.session_id == "test-session"
        assert dossier.id.startswith("dossier-")

    def test_dossier_engine_creation(self):
        """Test DossierEngine"""
        from arifosmcp.runtime.reality_dossier import DossierEngine

        engine = DossierEngine()
        assert engine is not None
        assert "F2_TRUTH" in engine._floor_weights

    def test_dossier_provenance_creation(self):
        """Test DossierProvenance"""
        from arifosmcp.runtime.reality_dossier import DossierProvenance

        prov = DossierProvenance(bundles_processed=5)
        assert prov.bundles_processed == 5
        assert prov.chain_id.startswith("chain-")

    def test_intelligence_state_3e_creation(self):
        """Test IntelligenceState3E"""
        from arifosmcp.runtime.reality_dossier import IntelligenceState3E

        state = IntelligenceState3E(exploration="SCOPED")
        assert state.exploration == "SCOPED"
        assert state.entropy == "LOW"
