"""
Targeted tests for runtime/tools.py to boost coverage from 23% to 75%+
Focus on tool wrappers, stage definitions, and core tool functions
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
from arifosmcp.runtime.models import Verdict, Stage, RuntimeEnvelope


class TestStageEnum:
    """Test Stage enum definitions"""
    
    def test_stage_values(self):
        """Test stage enum has correct values"""
        from arifosmcp.runtime.tools import Stage
        
        assert Stage.INIT_000.value == "000_INIT"
        assert Stage.SENSE_111.value == "111_SENSE"
        assert Stage.MIND_333.value == "333_MIND"
        assert Stage.ROUTER_444.value == "444_ROUTER"
        assert Stage.JUDGE_888.value == "888_JUDGE"
        assert Stage.VAULT_999.value == "999_VAULT"


class TestNormalizeSessionId:
    """Test _normalize_session_id function"""
    
    def test_normalize_none_generates_uuid(self):
        """Test None generates UUID"""
        from arifosmcp.runtime.tools import _normalize_session_id
        
        result = _normalize_session_id(None)
        assert isinstance(result, str)
        assert len(result) > 10
    
    def test_normalize_existing_session(self):
        """Test existing session ID returned"""
        from arifosmcp.runtime.tools import _normalize_session_id
        
        existing = "test-session-123"
        result = _normalize_session_id(existing)
        assert result == existing


class TestWrapCall:
    """Test _wrap_call function - the universal bridge"""
    
    @pytest.mark.asyncio
    async def test_wrap_call_success(self):
        """Test successful wrap call"""
        from arifosmcp.runtime.tools import _wrap_call, Stage
        
        with patch('arifosmcp.runtime.tools.call_kernel', new_callable=AsyncMock) as mock_call:
            mock_data = {
                "ok": True,
                "tool": "test_tool",
                "session_id": "test-session",
                "stage": "000_INIT",
                "verdict": Verdict.SEAL,
                "status": "SUCCESS",
                "metrics": {"telemetry": {"confidence": 0.95, "G_star": 0.95}},
                "meta": {"motto": "test"},
                "intelligence_state": {}
            }
            mock_call.return_value = mock_data
            
            result = await _wrap_call(
                "test_tool", Stage.INIT_000, "test-session", {}, None
            )
            
            assert result is not None
            assert result.ok is True
    
    @pytest.mark.asyncio
    async def test_wrap_call_with_dry_run(self):
        """Test wrap call with dry_run flag"""
        from arifosmcp.runtime.tools import _wrap_call, Stage
        
        payload = {"dry_run": True, "debug": True}
        
        with patch('arifosmcp.runtime.tools.call_kernel') as mock_call:
            mock_call.return_value = AsyncMock()
            mock_call.return_value = {
                "ok": True,
                "tool": "test_tool",
                "session_id": "test",
                "stage": "000_INIT",
                "verdict": "SEAL",
                "status": "DRY_RUN",
                "meta": {}
            }
            
            result = await _wrap_call(
                "test_tool", Stage.INIT_000, "test-session", payload, None
            )
            
            assert result is not None


class TestInitAnchor:
    """Test INIT_ANCHOR tool"""
    
    @pytest.mark.asyncio
    async def test_init_anchor_basic(self):
        """Test basic init_anchor execution"""
        from arifosmcp.runtime.tools import init_anchor
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_wrap.return_value = mock_envelope
            
            result = await init_anchor(
                raw_input="Start session",
                declared_name="TestUser"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_init_anchor_with_intent(self):
        """Test init_anchor with intent object"""
        from arifosmcp.runtime.tools import init_anchor
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await init_anchor(
                intent={"query": "test query"},
                session_id="test-session"
            )
            
            assert result is not None


class TestAgiReason:
    """Test AGI_REASON tool"""
    
    @pytest.mark.asyncio
    async def test_agi_reason_basic(self):
        """Test basic agi_reason execution"""
        from arifosmcp.runtime.tools import agi_reason
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_envelope.metrics.model_dump.return_value = {"telemetry": {"verdict": "SEAL"}}
            mock_envelope.intelligence_state = {}
            mock_wrap.return_value = mock_envelope
            
            result = await agi_reason(
                query="Test reasoning query"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_agi_reason_with_context(self):
        """Test agi_reason with context"""
        from arifosmcp.runtime.tools import agi_reason
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_envelope.metrics.model_dump.return_value = {}
            mock_envelope.intelligence_state = {}
            mock_wrap.return_value = mock_envelope
            
            result = await agi_reason(
                query="Test",
                facts=["Additional fact"],
                causal_interventions=[{"var": "X", "val": 1}]
            )
            
            assert result is not None


class TestAgiReflect:
    """Test AGI_REFLECT tool"""
    
    @pytest.mark.asyncio
    async def test_agi_reflect_basic(self):
        """Test basic agi_reflect execution"""
        from arifosmcp.runtime.tools import agi_reflect
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await agi_reflect(
                topic="Test topic"
            )
            
            assert result is not None


class TestAsiCritique:
    """Test ASI_CRITIQUE tool"""
    
    @pytest.mark.asyncio
    async def test_asi_critique_basic(self):
        """Test basic asi_critique execution"""
        from arifosmcp.runtime.tools import asi_critique
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_envelope.stage = Stage.CRITIQUE_666.value
            mock_envelope.tool = "asi_critique"
            mock_envelope.metrics.telemetry.confidence = 0.04
            mock_envelope.metrics.telemetry.G_star = 0.95
            mock_envelope.metrics.telemetry.dS = 0.0
            mock_envelope.metrics.telemetry.peace2 = 1.0
            mock_envelope.metrics.telemetry.truth = 0.99
            mock_envelope.metrics.model_dump.return_value = {"telemetry": {"verdict": "Alive"}}
            mock_envelope.model_dump.return_value = {
                "ok": True, "tool": "asi_critique", "stage": Stage.CRITIQUE_666.value,
                "verdict": Verdict.SEAL.value
            }
            mock_wrap.return_value = mock_envelope
            
            result = await asi_critique(
                draft_output="Test draft output"
            )
            
            assert result is not None


class TestAsiSimulate:
    """Test ASI_SIMULATE tool"""
    
    @pytest.mark.asyncio
    async def test_asi_simulate_basic(self):
        """Test basic asi_simulate execution"""
        from arifosmcp.runtime.tools import asi_simulate
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_envelope.stage = Stage.HEART_666.value
            mock_envelope.tool = "asi_simulate"
            mock_envelope.metrics.telemetry.confidence = 0.04
            mock_envelope.metrics.telemetry.G_star = 0.95
            mock_envelope.metrics.telemetry.dS = 0.0
            mock_envelope.metrics.telemetry.peace2 = 1.0
            mock_envelope.metrics.telemetry.truth = 0.99
            mock_envelope.metrics.model_dump.return_value = {"telemetry": {"verdict": "Alive"}}
            mock_envelope.model_dump.return_value = {
                "ok": True, "tool": "asi_simulate", "stage": Stage.HEART_666.value,
                "verdict": Verdict.SEAL.value
            }
            mock_wrap.return_value = mock_envelope
            
            result = await asi_simulate(
                scenario="Test scenario"
            )
            
            assert result is not None


class TestForge:
    """Test FORGE tool - full pipeline"""
    
    @pytest.mark.asyncio
    async def test_forge_basic(self):
        """Test basic forge execution"""
        from arifosmcp.runtime.tools import forge
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_envelope.stage = Stage.JUDGE_888.value
            mock_envelope.tool = "forge"
            mock_envelope.metrics.telemetry.confidence = 0.04
            mock_envelope.metrics.telemetry.G_star = 0.95
            mock_envelope.metrics.telemetry.dS = 0.0
            mock_envelope.metrics.telemetry.peace2 = 1.0
            mock_envelope.metrics.telemetry.truth = 0.99
            mock_envelope.metrics.model_dump.return_value = {"telemetry": {"verdict": "Alive"}}
            mock_envelope.model_dump.return_value = {
                "ok": True, "tool": "forge", "stage": Stage.JUDGE_888.value,
                "verdict": Verdict.SEAL.value
            }
            mock_envelope.intelligence_state = {}
            mock_wrap.return_value = mock_envelope
            
            result = await forge(
                spec="Create a test artifact"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_forge_with_risk_tier(self):
        """Test forge with risk tier"""
        from arifosmcp.runtime.tools import forge
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_envelope.stage = Stage.JUDGE_888.value
            mock_envelope.tool = "forge"
            mock_envelope.metrics.telemetry.confidence = 0.04
            mock_envelope.metrics.telemetry.G_star = 0.95
            mock_envelope.metrics.telemetry.dS = 0.0
            mock_envelope.metrics.telemetry.peace2 = 1.0
            mock_envelope.metrics.telemetry.truth = 0.99
            mock_envelope.metrics.model_dump.return_value = {"telemetry": {"verdict": "Alive"}}
            mock_envelope.model_dump.return_value = {
                "ok": True, "tool": "forge", "stage": Stage.JUDGE_888.value,
                "verdict": Verdict.SEAL.value
            }
            mock_envelope.intelligence_state = {}
            mock_wrap.return_value = mock_envelope
            
            result = await forge(
                spec="High risk operation",
                risk_tier="high"
            )
            
            assert result is not None


class TestApexJudge:
    """Test APEX_JUDGE tool"""
    
    @pytest.mark.asyncio
    async def test_apex_judge_basic(self):
        """Test basic apex_judge execution"""
        from arifosmcp.runtime.tools import apex_judge
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_envelope.metrics.telemetry.G_star = 0.9
            mock_envelope.metrics.internal = {}
            mock_wrap.return_value = mock_envelope
            
            result = await apex_judge(
                candidate_output="Test output to judge"
            )
            
            assert result is not None
            assert result.verdict == Verdict.SEAL


class TestVaultSeal:
    """Test VAULT_SEAL tool"""
    
    @pytest.mark.asyncio
    async def test_vault_seal_basic(self):
        """Test basic vault_seal execution"""
        from arifosmcp.runtime.tools import vault_seal
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_envelope.verdict = Verdict.SEAL
            mock_wrap.return_value = mock_envelope
            
            result = await vault_seal(
                verdict="SEAL",
                evidence="Evidence for sealing"
            )
            
            assert result is not None


class TestAliasFunctions:
    """Test alias functions (lowercase)"""
    
    def test_aliases_exist(self):
        """Test that all aliases exist"""
        from arifosmcp.runtime.tools import (
            agi_reason, agi_reflect, asi_critique, asi_simulate,
            apex_judge, init_anchor, vault_seal
        )
        
        assert callable(agi_reason)
        assert callable(agi_reflect)
        assert callable(asi_critique)
        assert callable(asi_simulate)
        assert callable(apex_judge)
        assert callable(init_anchor)
        assert callable(vault_seal)


class TestRealityTools:
    """Test reality tools (compass, atlas, search, ingest)"""
    
    @pytest.mark.asyncio
    async def test_reality_compass(self):
        """Test reality_compass tool"""
        from arifosmcp.runtime.tools import reality_compass
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await reality_compass(
                input="Test query"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_search_reality(self):
        """Test search_reality tool"""
        from arifosmcp.runtime.tools import search_reality
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await search_reality(
                query="Search query"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_ingest_evidence(self):
        """Test ingest_evidence tool"""
        from arifosmcp.runtime.tools import ingest_evidence
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await ingest_evidence(
                url="https://example.com"
            )
            
            assert result is not None


class TestAgentZeroTools:
    """Test AgentZero tools"""
    
    @pytest.mark.asyncio
    async def test_agentzero_engineer(self):
        """Test agentzero_engineer tool"""
        from arifosmcp.runtime.tools import agentzero_engineer
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await agentzero_engineer(
                task_description="Write code"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_agentzero_validate(self):
        """Test agentzero_validate tool"""
        from arifosmcp.runtime.tools import agentzero_validate
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await agentzero_validate(
                input_to_validate="Test input"
            )
            
            assert result is not None


class TestUtilityTools:
    """Test utility tools"""
    
    @pytest.mark.asyncio
    async def test_check_vital(self):
        """Test check_vital tool"""
        from arifosmcp.runtime.tools import check_vital
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await check_vital()
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_audit_rules(self):
        """Test audit_rules tool"""
        from arifosmcp.runtime.tools import audit_rules
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await audit_rules()
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_verify_vault_ledger(self):
        """Test verify_vault_ledger tool"""
        from arifosmcp.runtime.tools import verify_vault_ledger
        
        with patch('arifosmcp.runtime.tools._wrap_call', new_callable=AsyncMock) as mock_wrap:
            mock_envelope = MagicMock()
            mock_envelope.ok = True
            mock_wrap.return_value = mock_envelope
            
            result = await verify_vault_ledger()
            
            assert result is not None


class TestErrorHandling:
    """Test error handling in tools"""
    
    @pytest.mark.asyncio
    async def test_tool_handles_arifos_error(self):
        """Test tool handles ArifOSError"""
        from arifosmcp.runtime.tools import agi_reason
        from arifosmcp.runtime.models import ArifOSError
        
        with patch('arifosmcp.runtime.tools.call_kernel', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = ArifOSError("Test error", "CONSTITUTIONAL", "F2_TRUTH", "VOID")
            
            with pytest.raises(ArifOSError):
                await agi_reason(query="test")
    
    @pytest.mark.asyncio
    async def test_tool_handles_generic_error(self):
        """Test tool handles generic error"""
        from arifosmcp.runtime.tools import agi_reason
        
        with patch('arifosmcp.runtime.tools.call_kernel') as mock_call:
            mock_call.side_effect = Exception("Generic error")
            
            # Should create error envelope, not raise
            result = await agi_reason(query="test")
            assert result is not None
