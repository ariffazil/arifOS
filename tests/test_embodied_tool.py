"""
Embodied Tool Intelligence Tests
═══════════════════════════════════════════════════════════════════════════════

Tests the 10-stage embodied loop:
RECEIVE → SENSE → BOUND → CLASSIFY → CHECK AUTHORITY
→ CHECK REVERSIBILITY → SIMULATE → ACT OR HOLD → WITNESS → REVIEW

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import tempfile

import pytest

from arifosmcp.core.embodied_tool_engine import (
    EmbodiedDecision,
    EmbodiedToolEngine,
    embodied_tool,
)
from arifosmcp.core.reversibility_engine import (
    ReversibilityClass,
    ReversibilityEngine,
    classify_tool_base,
)
from arifosmcp.core.tool_self_model import (
    BlastRadius,
    ToolManifest,
    ToolSelfModel,
    get_tool_self_model,
)
from arifosmcp.core.witness_log import WitnessLog
from arifosmcp.resources.embodied_resources import (
    DOMAIN_BOUNDARY_POLICY,
    RESOURCE_HANDLERS,
    get_domain_boundaries_resource,
    get_tool_permissions_resource,
    get_tool_self_model_resource,
    handle_resource,
)
from arifosmcp.schemas.embodied_tool import (
    Domain,
    EmbodiedToolEnvelope,
    ExecutionStatus,
    Reversibility,
    RiskTier,
    build_embodied_envelope,
)
from arifosmcp.tools.embodied import (
    ARIFOS_TOOL_CHARTERS,
    EmbodiedTool,
    register_all_arifos_tools,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset global singletons between tests."""
    import arifosmcp.core.embodied_tool_engine as _ete
    import arifosmcp.core.tool_self_model as _tsm
    import arifosmcp.core.witness_log as _wl

    _ete._embodied_engine = None
    _tsm._tool_self_model = None
    _wl._witness_log = None
    yield
    _ete._embodied_engine = None
    _tsm._tool_self_model = None
    _wl._witness_log = None


@pytest.fixture
def fresh_self_model():
    """Return a fresh ToolSelfModel."""
    return ToolSelfModel()


@pytest.fixture
def fresh_engine(fresh_self_model):
    """Return a fresh EmbodiedToolEngine."""
    return EmbodiedToolEngine(tool_self_model=fresh_self_model)


@pytest.fixture
def temp_witness_log():
    """Return a WitnessLog backed by a temporary file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        path = f.name
    log = WitnessLog(path=path)
    yield log
    os.unlink(path)


# ── Self-Model Tests ─────────────────────────────────────────────────────────


def test_register_all_arifos_tools():
    """All canonical tools (13 AOS + 13 WELL = 26) must be registered in the self-model."""
    model = get_tool_self_model()
    register_all_arifos_tools()

    assert len(model.list_all()) == len(ARIFOS_TOOL_CHARTERS)
    for tool_id in ARIFOS_TOOL_CHARTERS:
        entry = model.get(tool_id)
        assert entry is not None, f"{tool_id} not registered"
        assert entry.manifest.tool_id == tool_id


def test_permission_gap_detection(fresh_self_model):
    """ToolSelfModel must detect missing permissions."""
    manifest = ToolManifest(
        tool_id="test_tool",
        tool_name="Test Tool",
        domain="AOS",
        required_permissions=["admin", "session_init"],
        risk_tier="T2",
    )
    fresh_self_model.register(manifest)
    fresh_self_model.set_agent_permissions({"session_init"})

    entry = fresh_self_model.get("test_tool")
    assert entry.has_permission_gap
    assert "admin" in entry.permission_gap
    assert "session_init" not in entry.permission_gap
    assert not entry.is_safe_to_execute


def test_self_model_accepts_structured_confidence(fresh_self_model):
    """Postflight learning must tolerate structured confidence payloads."""
    manifest = ToolManifest(
        tool_id="test_tool",
        tool_name="Test Tool",
        domain="AOS",
        risk_tier="T1",
    )
    fresh_self_model.register(manifest)

    outcome = fresh_self_model.update_from_outcome(
        tool_id="test_tool",
        result={"status": "OK", "confidence": {"overall_confidence": 0.72}},
    )

    assert outcome["delta_surprise"] == 0.0
    assert fresh_self_model.get("test_tool").use_count == 1


def test_composition_safety(fresh_self_model):
    """Composition matrix must flag dangerous pairings."""
    manifest_a = ToolManifest(
        tool_id="tool_a",
        tool_name="Tool A",
        domain="AOS",
        dangerous_compose_with=["tool_b"],
        safe_compose_with=["tool_c"],
    )
    manifest_b = ToolManifest(tool_id="tool_b", tool_name="Tool B", domain="AOS")
    manifest_c = ToolManifest(tool_id="tool_c", tool_name="Tool C", domain="AOS")
    fresh_self_model.register(manifest_a)
    fresh_self_model.register(manifest_b)
    fresh_self_model.register(manifest_c)

    safe, reason = fresh_self_model.check_composition("tool_a", "tool_b")
    assert not safe
    assert "dangerous" in reason

    safe2, reason2 = fresh_self_model.check_composition("tool_a", "tool_c")
    assert safe2
    assert "safe" in reason2


# ── Reversibility Engine Tests ───────────────────────────────────────────────


def test_reversibility_trivial():
    """Read operations are TRIVIAL."""
    engine = ReversibilityEngine()
    verdict = engine.assess("read_file", {"path": "/tmp/test.txt"})
    assert verdict.reversibility_class == ReversibilityClass.TRIVIAL
    assert not verdict.requires_888_hold


def test_reversibility_irreversible():
    """Delete operations are IRREVERSIBLE."""
    engine = ReversibilityEngine()
    verdict = engine.assess("delete_file", {"path": "/tmp/test.txt"})
    assert verdict.reversibility_class == ReversibilityClass.IRREVERSIBLE
    assert verdict.requires_888_hold
    assert verdict.is_irreversible


def test_reversibility_critical():
    """Sudo operations are CRITICAL."""
    engine = ReversibilityEngine()
    verdict = engine.assess("run_command", {"command": "sudo rm -rf /"})
    assert verdict.reversibility_class == ReversibilityClass.CRITICAL
    assert verdict.is_critical
    assert verdict.requires_888_hold


def test_reversibility_partial():
    """Edit operations are PARTIAL."""
    engine = ReversibilityEngine()
    verdict = engine.assess("edit_file", {"path": "/tmp/test.txt"})
    assert verdict.reversibility_class == ReversibilityClass.PARTIAL
    assert not verdict.requires_888_hold


def test_classify_tool_base():
    """Tool base classification must map canonical tools."""
    assert classify_tool_base("arif_mind_reason") == "read"
    assert classify_tool_base("arif_forge_execute") == "execute"
    assert classify_tool_base("arif_vault_seal") == "execute"
    assert classify_tool_base("unknown_tool") == "unknown"


# ── Embodied Tool Engine Tests ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_preflight_seals_t1_tool(fresh_engine):
    """T1 tool with no dangerous params should SEAL."""
    fresh_engine.self_model.register(ARIFOS_TOOL_CHARTERS["arif_mind_reason"])
    decision = await fresh_engine.run_preflight(
        tool_id="arif_mind_reason",
        params={"query": "What is 2+2?"},
        actor_id="arif",
        session_id="sess_test",
    )
    assert decision.can_proceed
    assert decision.status == "SEAL"
    assert decision.risk_tier == RiskTier.T1


@pytest.mark.asyncio
async def test_preflight_holds_t4_tool(fresh_engine):
    """T4 tool should HOLD without explicit authority."""
    fresh_engine.self_model.register(ARIFOS_TOOL_CHARTERS["arif_vault_seal"])
    decision = await fresh_engine.run_preflight(
        tool_id="arif_vault_seal",
        params={"payload": "test"},
        actor_id="arif",
        session_id="sess_test",
    )
    assert not decision.can_proceed
    assert decision.status == "HOLD"
    assert decision.risk_tier == RiskTier.T4


@pytest.mark.asyncio
async def test_preflight_voids_critical_action(fresh_engine):
    """CRITICAL reversibility should VOID."""
    fresh_engine.self_model.register(
        ToolManifest(
            tool_id="dangerous_cmd",
            tool_name="Dangerous Command",
            domain="AOS",
            risk_tier="T3",
            reversibility="irreversible",
            blast_radius=BlastRadius.CRITICAL,
        )
    )
    decision = await fresh_engine.run_preflight(
        tool_id="dangerous_cmd",
        params={"command": "sudo mkfs /dev/sda1"},
        actor_id="arif",
        session_id="sess_test",
    )
    assert not decision.can_proceed
    assert decision.status == "VOID"


@pytest.mark.asyncio
async def test_preflight_holds_missing_session(fresh_engine):
    """T2+ tool without session_id should HOLD."""
    fresh_engine.self_model.register(ARIFOS_TOOL_CHARTERS["arif_kernel_route"])
    decision = await fresh_engine.run_preflight(
        tool_id="arif_kernel_route",
        params={"task": "route to forge"},
        actor_id="arif",
        session_id=None,
    )
    assert not decision.can_proceed
    assert decision.status == "HOLD"


@pytest.mark.asyncio
async def test_postflight_builds_envelope(fresh_engine):
    """Postflight must return a complete EmbodiedToolEnvelope."""
    fresh_engine.self_model.register(ARIFOS_TOOL_CHARTERS["arif_mind_reason"])
    decision = EmbodiedDecision(
        can_proceed=True,
        status="SEAL",
        reason="All checks passed",
        risk_tier=RiskTier.T1,
        reversibility=Reversibility.REVERSIBLE,
        authority_required=False,
        authority_verified=True,
        uncertainty=[],
    )
    envelope = await fresh_engine.run_postflight(
        tool_id="arif_mind_reason",
        params={"query": "test"},
        actor_id="arif",
        session_id="sess_test",
        decision=decision,
        result={"answer": "4"},
        latency_ms=100.0,
        confidence=0.95,
        reasoning_summary="Simple math",
    )
    assert isinstance(envelope, EmbodiedToolEnvelope)
    assert envelope.status == "SEAL"
    assert envelope.tool_id == "arif_mind_reason"
    assert envelope.witness.input_hash is not None
    assert envelope.witness.actor_id == "arif"


# ── Witness Log Tests ────────────────────────────────────────────────────────


def test_witness_log_append_and_query(temp_witness_log):
    """WitnessLog append and query must work."""
    log = temp_witness_log
    record = log.append(
        tool_id="arif_mind_reason",
        actor_id="arif",
        session_id="sess_abc",
        domain="AOS",
        risk_tier="T1",
        reversibility="reversible",
        status="SEAL",
        confidence=0.9,
        authority_verified=True,
        input_hash="sha256:test",
        reasoning_summary="Test reasoning",
    )
    assert record.tool_id == "arif_mind_reason"
    assert record.session_id == "sess_abc"

    results = log.query(session_id="sess_abc")
    assert len(results) == 1
    assert results[0].tool_id == "arif_mind_reason"


def test_witness_log_chain_integrity(temp_witness_log):
    """Chain verification must pass for valid log."""
    log = temp_witness_log
    log.append(
        tool_id="tool_a",
        actor_id="arif",
        session_id="sess_1",
        domain="AOS",
        risk_tier="T1",
        reversibility="reversible",
        status="SEAL",
        confidence=0.8,
        authority_verified=True,
        input_hash="sha256:a",
    )
    log.append(
        tool_id="tool_b",
        actor_id="arif",
        session_id="sess_1",
        domain="AOS",
        risk_tier="T1",
        reversibility="reversible",
        status="SEAL",
        confidence=0.8,
        authority_verified=True,
        input_hash="sha256:b",
    )

    valid, message = log.verify_chain()
    assert valid
    assert "valid" in message.lower()


def test_witness_log_stats(temp_witness_log):
    """Stats must aggregate correctly."""
    log = temp_witness_log
    log.append(
        tool_id="t1",
        actor_id="arif",
        session_id="s1",
        domain="AOS",
        risk_tier="T1",
        reversibility="reversible",
        status="SEAL",
        confidence=0.8,
        authority_verified=True,
        input_hash="h1",
    )
    log.append(
        tool_id="t2",
        actor_id="arif",
        session_id="s1",
        domain="AOS",
        risk_tier="T4",
        reversibility="irreversible",
        status="HOLD",
        confidence=0.5,
        authority_verified=False,
        input_hash="h2",
    )

    stats = log.stats()
    assert stats["total_records"] == 2
    assert stats["seal_rate"] == 0.5
    assert stats["hold_rate"] == 0.5
    assert stats["void_rate"] == 0.0


# ── Resource Tests ───────────────────────────────────────────────────────────


def test_self_model_resource():
    """arifos://tools/self-model must return registered tools."""
    register_all_arifos_tools()
    resource = get_tool_self_model_resource()
    assert resource["uri"] == "arifos://tools/self-model"
    assert "tools" in resource["body"]
    assert len(resource["body"]["tools"]) == len(ARIFOS_TOOL_CHARTERS)


def test_permissions_resource():
    """arifos://tools/permissions must return permission state."""
    register_all_arifos_tools()
    resource = get_tool_permissions_resource()
    assert resource["uri"] == "arifos://tools/permissions"
    assert "executable_count" in resource["body"]
    assert "blocked_count" in resource["body"]


def test_domain_boundaries_resource():
    """arifos://boundaries/domain must return policy for all domains."""
    resource = get_domain_boundaries_resource()
    assert resource["uri"] == "arifos://boundaries/domain"
    body = resource["body"]
    assert "AOS" in body
    assert "WELL" in body
    assert "WEALTH" in body
    assert "GEOX" in body
    assert "hard_gate" in body["AOS"]
    assert "must_not" in body["WELL"]


def test_handle_resource_unknown_uri():
    """Unknown URI must return error with available resources."""
    result = handle_resource("arifos://unknown")
    assert "error" in result
    assert "available" in result


def test_resource_handlers_coverage():
    """All embodied resources must have handlers."""
    expected = {
        "arifos://tools/self-model",
        "arifos://tools/permissions",
        "arifos://tools/composition-matrix",
        "arifos://witness/log",
        "arifos://witness/stats",
        "arifos://boundaries/domain",
    }
    assert expected.issubset(set(RESOURCE_HANDLERS.keys()))


# ── EmbodiedTool Base Class Tests ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_embodied_tool_run_pipeline():
    """EmbodiedTool.run() must execute full pipeline and return envelope."""
    register_all_arifos_tools()

    class TestTool(EmbodiedTool):
        tool_id = "arif_mind_reason"
        tool_name = "Test Mind Reason"
        domain = "AOS"
        risk_tier = "T1"
        reversibility = "reversible"

        async def execute(self, params: dict, ctx) -> dict:
            return {"answer": params.get("query", "")}

    tool = TestTool()
    tool.register()

    class FakeCtx:
        actor_id = "arif"
        session_id = "sess_test"

    envelope = await tool.run(
        params={"query": "hello"},
        ctx=FakeCtx(),
        actor_id="arif",
        session_id="sess_test",
    )
    assert isinstance(envelope, EmbodiedToolEnvelope)
    assert envelope.tool_id == "arif_mind_reason"
    assert envelope.status == "SEAL"


# ── Decorator Tests ──────────────────────────────────────────────────────────


def test_embodied_tool_decorator():
    """@embodied_tool decorator must register tool in self-model."""
    import arifosmcp.core.tool_self_model as _tsm

    _tsm._tool_self_model = None

    @embodied_tool(
        tool_id="decorated_tool",
        tool_name="Decorated Tool",
        domain="AOS",
        risk_tier="T1",
        required_permissions=["test_perm"],
    )
    async def my_tool(params, ctx):
        return {"ok": True}

    model = get_tool_self_model()
    entry = model.get("decorated_tool")
    assert entry is not None
    assert entry.manifest.tool_name == "Decorated Tool"
    assert "test_perm" in entry.manifest.required_permissions


# ── Build Envelope Factory Tests ─────────────────────────────────────────────


def test_build_embodied_envelope_defaults():
    """Factory must produce valid envelope with defaults."""
    envelope = build_embodied_envelope(
        tool_id="test",
        tool_name="Test",
        domain=Domain.AOS,
        actor_id="arif",
        session_id="sess",
        risk_tier=RiskTier.T1,
        reversibility=Reversibility.REVERSIBLE,
        authority_required=False,
        authority_verified=True,
        result={"ok": True},
        witness_input_hash="sha256:abc",
    )
    assert envelope.status == "SEAL"
    assert envelope.witness.execution_status == ExecutionStatus.EXECUTED
    assert envelope.next_safe_action == "Proceed to 888_JUDGE if action is consequential."


def test_build_embodied_envelope_hold():
    """HOLD status must set correct next action."""
    envelope = build_embodied_envelope(
        tool_id="test",
        tool_name="Test",
        domain=Domain.AOS,
        actor_id="arif",
        session_id=None,
        risk_tier=RiskTier.T4,
        reversibility=Reversibility.IRREVERSIBLE,
        authority_required=True,
        authority_verified=False,
        result={},
        witness_input_hash="sha256:abc",
        status="HOLD",
    )
    assert envelope.status == "HOLD"
    assert "Await Arif approval" in envelope.next_safe_action
    assert envelope.witness.execution_status == ExecutionStatus.HELD


# ── Domain Boundary Policy Tests ─────────────────────────────────────────────


def test_domain_boundary_aos_must_not():
    """AOS must_not list must prevent impersonation."""
    policy = DOMAIN_BOUNDARY_POLICY["AOS"]
    must_not = policy["must_not"]
    assert any("impersonate" in item for item in must_not)
    assert any("WELL" in item for item in must_not)
    assert "hard_gate" in policy


def test_domain_boundary_well_reflexes():
    """WELL reflexes must handle distress and fatigue."""
    reflexes = DOMAIN_BOUNDARY_POLICY["WELL"]["reflexes"]
    assert "distress_high" in reflexes
    assert "fatigue_high" in reflexes
    assert "self_harm_risk" in reflexes


def test_domain_boundary_wealth_hard_gate():
    """WEALTH hard gate must block money movement."""
    policy = DOMAIN_BOUNDARY_POLICY["WEALTH"]
    assert "No money movement without explicit Arif approval" in policy["hard_gate"]
    assert "execute_trades" in policy["must_not"]


def test_domain_boundary_geox_hard_gate():
    """GEOX hard gate must require human review for physical actions."""
    policy = DOMAIN_BOUNDARY_POLICY["GEOX"]
    assert "human geoscientist review" in policy["hard_gate"]
    assert "claim_certainty_beyond_data" in policy["must_not"]
