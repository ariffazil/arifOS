"""
Targeted tests for reality_dossier.py to boost coverage from 0% to 75%+
Focus on RealityDossier, DossierEngine, and verdict processing
"""
import pytest
from unittest.mock import Mock, patch
import json


class TestWitness:
    """Test Witness model"""
    
    def test_witness_creation(self):
        """Test Witness creation"""
        from arifosmcp.runtime.reality_dossier import Witness
        
        witness = Witness(
            source="human",
            confidence=0.95,
            weight=1.5,
            evidence_refs=["ref1", "ref2"],
            notes="Test notes"
        )
        
        assert witness.source == "human"
        assert witness.confidence == 0.95
        assert witness.weight == 1.5
        assert len(witness.evidence_refs) == 2
    
    def test_witness_defaults(self):
        """Test Witness with defaults"""
        from arifosmcp.runtime.reality_dossier import Witness
        
        witness = Witness(source="ai")
        
        assert witness.confidence >= 0.0
        assert witness.weight == 1.0
        assert witness.evidence_refs == []
        assert witness.notes == ""
    
    def test_witness_validation(self):
        """Test Witness validation"""
        from arifosmcp.runtime.reality_dossier import Witness
        
        with pytest.raises(ValueError):
            Witness(source="invalid", confidence=0.5)


class TestDossierVerdict:
    """Test DossierVerdict model"""
    
    def test_verdict_creation(self):
        """Test DossierVerdict creation"""
        from arifosmcp.runtime.reality_dossier import DossierVerdict, Witness
        
        verdict = DossierVerdict(
            claim="The sky is blue",
            verdict="SUPPORTED",
            confidence=0.95,
            witnesses=[
                Witness(source="human", confidence=0.95),
                Witness(source="earth", confidence=0.90)
            ]
        )
        
        assert verdict.claim == "The sky is blue"
        assert verdict.verdict == "SUPPORTED"
        assert len(verdict.witnesses) == 2
    
    def test_verdict_with_floor_impacts(self):
        """Test verdict with floor impacts"""
        from arifosmcp.runtime.reality_dossier import DossierVerdict
        
        verdict = DossierVerdict(
            claim="Test",
            verdict="UNCERTAIN",
            confidence=0.50,
            floor_impacts={"F2": 0.8, "F4": 0.6}
        )
        
        assert "F2" in verdict.floor_impacts
        assert verdict.floor_impacts["F2"] == 0.8
    
    def test_verdict_with_evidence_chain(self):
        """Test verdict with evidence chain"""
        from arifosmcp.runtime.reality_dossier import DossierVerdict
        
        verdict = DossierVerdict(
            claim="Test",
            verdict="SUPPORTED",
            confidence=0.90,
            evidence_chain=["source1", "source2", "source3"]
        )
        
        assert len(verdict.evidence_chain) == 3


class TestDossierProvenance:
    """Test DossierProvenance model"""
    
    def test_provenance_creation(self):
        """Test DossierProvenance creation"""
        from arifosmcp.runtime.reality_dossier import DossierProvenance
        
        prov = DossierProvenance(
            bundles_processed=5,
            atlas_nodes=10,
            completeness_score=0.85
        )
        
        assert prov.bundles_processed == 5
        assert prov.atlas_nodes == 10
        assert prov.completeness_score == 0.85
        assert prov.chain_id.startswith("chain-")
    
    def test_provenance_defaults(self):
        """Test DossierProvenance defaults"""
        from arifosmcp.runtime.reality_dossier import DossierProvenance
        
        prov = DossierProvenance()
        
        assert prov.bundles_processed == 0
        assert prov.atlas_nodes == 0
        assert prov.completeness_score == 0.0
        assert prov.chain_id.startswith("chain-")
        assert prov.created_at > 0


class TestIntelligenceState3E:
    """Test IntelligenceState3E model"""
    
    def test_state_creation(self):
        """Test IntelligenceState3E creation"""
        from arifosmcp.runtime.reality_dossier import IntelligenceState3E
        
        state = IntelligenceState3E(
            exploration="SCOPED",
            entropy="MANAGEABLE",
            eureka="PARTIAL",
            hypotheses=["h1", "h2"],
            stable_facts=["fact1"],
            uncertainties=["?"],
            insight="Partial insight"
        )
        
        assert state.exploration == "SCOPED"
        assert state.entropy == "MANAGEABLE"
        assert state.eureka == "PARTIAL"
        assert len(state.hypotheses) == 2
    
    def test_state_defaults(self):
        """Test IntelligenceState3E defaults"""
        from arifosmcp.runtime.reality_dossier import IntelligenceState3E
        
        state = IntelligenceState3E()
        
        assert state.exploration == "BROAD"
        assert state.entropy == "LOW"
        assert state.eureka == "NONE"
        assert state.hypotheses == []
        assert state.stable_facts == []
        assert state.insight is None


class TestRealityDossier:
    """Test RealityDossier model"""
    
    def test_dossier_creation(self):
        """Test RealityDossier creation"""
        from arifosmcp.runtime.reality_dossier import RealityDossier
        from arifosmcp.runtime.reality_models import BundleStatus
        
        dossier = RealityDossier(
            session_id="test-session",
            actor_id="test-actor",
            authority_level="admin",
            status=BundleStatus.COMPLETE
        )
        
        assert dossier.session_id == "test-session"
        assert dossier.actor_id == "test-actor"
        assert dossier.status == BundleStatus.COMPLETE
        assert dossier.id.startswith("dossier-")
    
    def test_dossier_defaults(self):
        """Test RealityDossier defaults"""
        from arifosmcp.runtime.reality_dossier import RealityDossier
        from arifosmcp.runtime.reality_models import BundleStatus
        
        dossier = RealityDossier(status=BundleStatus.PENDING)
        
        assert dossier.session_id == "global"
        assert dossier.actor_id == "anonymous"
        assert dossier.authority_level == "anonymous"
        assert dossier.machine_status == "READY"
        assert dossier.machine_issue is None
        assert isinstance(dossier.telemetry, dict)
    
    def test_dossier_with_verdicts(self):
        """Test RealityDossier with verdicts"""
        from arifosmcp.runtime.reality_dossier import RealityDossier, DossierVerdict
        from arifosmcp.runtime.reality_models import BundleStatus
        
        dossier = RealityDossier(
            status=BundleStatus.COMPLETE,
            verdicts=[
                DossierVerdict(claim="C1", verdict="SUPPORTED", confidence=0.9),
                DossierVerdict(claim="C2", verdict="UNCERTAIN", confidence=0.5)
            ]
        )
        
        assert len(dossier.verdicts) == 2
    
    def test_dossier_json_serialization(self):
        """Test RealityDossier JSON serialization"""
        from arifosmcp.runtime.reality_dossier import RealityDossier
        from arifosmcp.runtime.reality_models import BundleStatus
        
        dossier = RealityDossier(status=BundleStatus.COMPLETE)
        json_str = dossier.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "dossier-" in json_str
        assert "COMPLETE" in json_str


class TestDossierEngine:
    """Test DossierEngine"""
    
    def test_engine_creation(self):
        """Test DossierEngine creation"""
        from arifosmcp.runtime.reality_dossier import DossierEngine
        
        engine = DossierEngine()
        assert engine is not None
        assert "F2_TRUTH" in engine._floor_weights
        assert "F4_CLARITY" in engine._floor_weights
    
    def test_compute_witness_confidence(self):
        """Test witness confidence computation"""
        from arifosmcp.runtime.reality_dossier import DossierEngine
        from arifosmcp.runtime.reality_models import Claim
        
        engine = DossierEngine()
        claim = Claim(text="Test claim", confidence=0.8)
        bundles = []
        
        witnesses = engine._compute_witness_confidence(claim, bundles)
        
        assert len(witnesses) == 2  # human + ai
        assert witnesses[0].source == "human"
        assert witnesses[1].source == "ai"
    
    def test_compute_witness_confidence_weights(self):
        """Test witness confidence weight assignment"""
        from arifosmcp.runtime.reality_dossier import DossierEngine
        from arifosmcp.runtime.reality_models import Claim
        
        engine = DossierEngine()
        claim = Claim(text="Test", confidence=0.9)
        
        witnesses = engine._compute_witness_confidence(claim, [])
        
        # Human has higher weight
        human_witness = [w for w in witnesses if w.source == "human"][0]
        ai_witness = [w for w in witnesses if w.source == "ai"][0]
        
        assert human_witness.weight > ai_witness.weight
        assert human_witness.confidence > claim.confidence


class TestDossierProcessing:
    """Test dossier processing workflows"""
    
    @pytest.mark.asyncio
    async def test_process_evidence_bundle(self):
        """Test processing evidence bundle"""
        from arifosmcp.runtime.reality_dossier import DossierEngine
        from arifosmcp.runtime.reality_models import EvidenceBundle, Claim
        
        engine = DossierEngine()
        bundle = EvidenceBundle(
            id="bundle-1",
            claims=[Claim(text="Claim 1", confidence=0.9)]
        )
        
        with patch.object(engine, '_process_bundle') as mock_process:
            mock_process.return_value = Mock(verdicts=[Mock()])
            
            result = await engine.process_bundle(bundle)
            assert result is not None
    
    def test_generate_final_verdict(self):
        """Test final verdict generation"""
        from arifosmcp.runtime.reality_dossier import DossierEngine, DossierVerdict
        
        engine = DossierEngine()
        verdicts = [
            DossierVerdict(claim="C1", verdict="SUPPORTED", confidence=0.9),
            DossierVerdict(claim="C2", verdict="SUPPORTED", confidence=0.85)
        ]
        
        final = engine._generate_final_verdict(verdicts)
        
        assert final is not None
        assert final.verdict in ["SUPPORTED", "CONTRADICTED", "UNCERTAIN"]


class TestDossierValidation:
    """Test dossier validation"""
    
    def test_validate_dossier_complete(self):
        """Test validation of complete dossier"""
        from arifosmcp.runtime.reality_dossier import RealityDossier, DossierVerdict
        from arifosmcp.runtime.reality_models import BundleStatus
        
        dossier = RealityDossier(
            status=BundleStatus.COMPLETE,
            verdicts=[
                DossierVerdict(claim="C1", verdict="SUPPORTED", confidence=0.9)
            ]
        )
        
        from arifosmcp.runtime.reality_dossier import _validate_dossier
        is_valid = _validate_dossier(dossier)
        
        assert is_valid is True
    
    def test_validate_dossier_incomplete(self):
        """Test validation of incomplete dossier"""
        from arifosmcp.runtime.reality_dossier import RealityDossier
        from arifosmcp.runtime.reality_models import BundleStatus
        
        dossier = RealityDossier(status=BundleStatus.ERROR)
        
        from arifosmcp.runtime.reality_dossier import _validate_dossier
        is_valid = _validate_dossier(dossier)
        
        assert is_valid is False


class TestDossierMetrics:
    """Test dossier metrics calculation"""
    
    def test_calculate_completeness_score(self):
        """Test completeness score calculation"""
        from arifosmcp.runtime.reality_dossier import RealityDossier, DossierVerdict
        from arifosmcp.runtime.reality_models import BundleStatus
        
        dossier = RealityDossier(
            status=BundleStatus.COMPLETE,
            verdicts=[
                DossierVerdict(claim="C1", verdict="SUPPORTED", confidence=0.9),
                DossierVerdict(claim="C2", verdict="SUPPORTED", confidence=0.85)
            ]
        )
        
        from arifosmcp.runtime.reality_dossier import _calculate_completeness
        score = _calculate_completeness(dossier)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be reasonably complete
