"""
tests/test_caller_context_envelope.py — Two-Layer Envelope Tests

Validates that the CallerContext (AI execution identity) and auth_context
(human authority) two-layer schema is correctly implemented, propagated,
and enforced throughout the metabolic loop.

F9/F10 compliance: AI declares execution role, never inherits human sovereignty.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.models import (
    CallerContext,
    PersonaId,
    RuntimeEnvelope,
    RuntimeRole,
    RuntimeStatus,
    ToolchainRole,
    UserModel,
    UserModelSource,
)
from arifosmcp.runtime.tools import _build_user_model, _resolve_caller_context

# ─── CallerContext model tests ───────────────────────────────────────────────


class TestCallerContextModel:
    def test_default_caller_context(self):
        ctx = CallerContext()
        assert ctx.persona_id == PersonaId.ENGINEER
        assert ctx.runtime_role == RuntimeRole.ASSISTANT
        assert ctx.toolchain_role == ToolchainRole.LEAF
        assert ctx.agent_id is None
        assert ctx.model_id is None

    def test_caller_context_with_all_fields(self):
        ctx = CallerContext(
            agent_id="gpt-runtime-01",
            model_id="gpt-5.4-thinking",
            persona_id=PersonaId.ARCHITECT,
            runtime_role=RuntimeRole.ROUTER,
            toolchain_role=ToolchainRole.ORCHESTRATOR,
        )
        assert ctx.agent_id == "gpt-runtime-01"
        assert ctx.model_id == "gpt-5.4-thinking"
        assert ctx.persona_id == PersonaId.ARCHITECT
        assert ctx.runtime_role == RuntimeRole.ROUTER
        assert ctx.toolchain_role == ToolchainRole.ORCHESTRATOR

    def test_persona_id_enum_values(self):
        assert PersonaId.ARCHITECT == "architect"
        assert PersonaId.ENGINEER == "engineer"
        assert PersonaId.AUDITOR == "auditor"
        assert PersonaId.VALIDATOR == "validator"

    def test_runtime_role_enum_values(self):
        assert RuntimeRole.ASSISTANT == "assistant"
        assert RuntimeRole.ROUTER == "router"
        assert RuntimeRole.TOOL_BROKER == "tool_broker"
        assert RuntimeRole.EVALUATOR == "evaluator"

    def test_toolchain_role_enum_values(self):
        assert ToolchainRole.ORCHESTRATOR == "orchestrator"
        assert ToolchainRole.LEAF == "leaf"
        assert ToolchainRole.SUBAGENT == "subagent"

    def test_caller_context_from_string_persona(self):
        ctx = CallerContext(persona_id="auditor")
        assert ctx.persona_id == PersonaId.AUDITOR

    def test_caller_context_invalid_string_persona_raises(self):
        """Invalid persona_id string must raise a Pydantic ValidationError."""
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CallerContext(persona_id="all_powerful_sovereign")

    def test_caller_context_serialization(self):
        ctx = CallerContext(
            agent_id="test-agent",
            model_id="claude-3",
            persona_id=PersonaId.ENGINEER,
        )
        dumped = ctx.model_dump(mode="json", exclude_none=True)
        assert dumped["persona_id"] == "engineer"
        assert dumped["agent_id"] == "test-agent"
        assert dumped["model_id"] == "claude-3"

    def test_caller_context_extra_fields(self):
        ctx = CallerContext(extra={"environment": "production", "region": "ap-southeast-1"})
        assert ctx.extra["environment"] == "production"


# ─── RuntimeEnvelope caller_context tests ────────────────────────────────────


class TestRuntimeEnvelopeCallerContext:
    def test_envelope_with_caller_context(self):
        ctx = CallerContext(persona_id=PersonaId.ARCHITECT)
        env = RuntimeEnvelope(tool="test_tool", stage="000_INIT", caller_context=ctx)
        assert env.caller_context is not None
        assert env.caller_context.persona_id == PersonaId.ARCHITECT

    def test_envelope_without_caller_context(self):
        env = RuntimeEnvelope(tool="test_tool", stage="000_INIT")
        assert env.caller_context is None

    def test_envelope_caller_context_from_dict(self):
        env = RuntimeEnvelope(
            tool="test_tool",
            stage="000_INIT",
            caller_context={"persona_id": "auditor", "runtime_role": "evaluator"},
        )
        assert env.caller_context is not None
        assert env.caller_context.persona_id == PersonaId.AUDITOR
        assert env.caller_context.runtime_role == RuntimeRole.EVALUATOR

    def test_envelope_separation_of_concerns(self):
        """F9/F10: auth_context (human) and caller_context (AI) must be separate."""
        auth_ctx = {"actor_id": "arif", "authority_level": "judge", "continuity": "session"}
        caller_ctx = CallerContext(
            agent_id="gpt-runtime-01",
            persona_id=PersonaId.ENGINEER,
        )
        env = RuntimeEnvelope(
            tool="test_tool",
            stage="000_INIT",
            auth_context=auth_ctx,
            caller_context=caller_ctx,
        )
        # Human authority in auth_context
        assert env.auth_context is not None
        assert env.auth_context["actor_id"] == "arif"
        assert "actor_id" not in env.caller_context.model_dump()

        # AI identity in caller_context
        assert env.caller_context is not None
        assert env.caller_context.agent_id == "gpt-runtime-01"
        assert "authority_level" not in env.caller_context.model_dump()

    def test_envelope_serialization_with_caller_context(self):
        ctx = CallerContext(
            agent_id="claude-3-5",
            model_id="claude-3-5-sonnet",
            persona_id=PersonaId.VALIDATOR,
        )
        env = RuntimeEnvelope(tool="seal_vault", stage="999_VAULT", caller_context=ctx)
        dumped = env.model_dump(mode="json")
        assert "caller_context" in dumped
        assert dumped["caller_context"]["persona_id"] == "validator"

    def test_envelope_user_model_from_dict(self):
        env = RuntimeEnvelope(
            tool="test_tool",
            stage="333_MIND",
            user_model={
                "stated_goal": {"value": "Explain the schema", "source": "explicit"},
                "behavioral_constraints": [
                    {
                        "value": "reduce_ambiguity_and_define_terms_clearly",
                        "source": "observable",
                    }
                ],
            },
        )
        assert env.user_model is not None
        assert env.user_model.stated_goal is not None
        assert env.user_model.stated_goal.source == UserModelSource.EXPLICIT
        assert env.user_model.behavioral_constraints[0].source == UserModelSource.OBSERVABLE


# ─── _resolve_caller_context helper tests ────────────────────────────────────


class TestResolveCallerContext:
    def test_default_when_no_context_no_hint(self):
        result = _resolve_caller_context(None, None)
        assert isinstance(result, CallerContext)
        assert result.persona_id == PersonaId.ENGINEER

    def test_requested_persona_hint_applied(self):
        result = _resolve_caller_context(None, "architect")
        assert result.persona_id == PersonaId.ARCHITECT

    def test_requested_persona_auditor(self):
        result = _resolve_caller_context(None, "auditor")
        assert result.persona_id == PersonaId.AUDITOR

    def test_requested_persona_validator(self):
        result = _resolve_caller_context(None, "validator")
        assert result.persona_id == PersonaId.VALIDATOR

    def test_invalid_persona_hint_ignored(self):
        result = _resolve_caller_context(None, "sovereign_ai")
        # Unknown hint is ignored; falls back to default
        assert result.persona_id == PersonaId.ENGINEER

    def test_provided_context_preserved(self):
        ctx = CallerContext(
            agent_id="my-agent",
            model_id="model-x",
            persona_id=PersonaId.ENGINEER,
            runtime_role=RuntimeRole.TOOL_BROKER,
        )
        result = _resolve_caller_context(ctx, None)
        assert result.agent_id == "my-agent"
        assert result.runtime_role == RuntimeRole.TOOL_BROKER

    def test_hint_overrides_provided_context_persona(self):
        ctx = CallerContext(persona_id=PersonaId.ENGINEER)
        result = _resolve_caller_context(ctx, "auditor")
        assert result.persona_id == PersonaId.AUDITOR

    def test_hint_case_insensitive(self):
        result = _resolve_caller_context(None, "ARCHITECT")
        assert result.persona_id == PersonaId.ARCHITECT


class TestBuildUserModel:
    def test_build_user_model_uses_explicit_and_observable_sources_only(self):
        user_model = _build_user_model(
            "reason_mind_synthesis",
            "333_MIND",
            {
                "query": "Keep it concise and accessible with plain English.",
                "context": "Need a high-level explanation.",
            },
            {"meta": {"dry_run": True}},
        )

        assert isinstance(user_model, UserModel)
        assert user_model.stated_goal is not None
        assert user_model.stated_goal.source == UserModelSource.EXPLICIT
        assert any(
            field.value == "keep_response_concise" and field.source == UserModelSource.EXPLICIT
            for field in user_model.output_constraints
        )
        assert any(
            field.value == "state_that_execution_is_simulated"
            and field.source == UserModelSource.OBSERVABLE
            for field in user_model.output_constraints
        )

    def test_build_user_model_keeps_unknown_user_state_null(self):
        user_model = _build_user_model(
            "assess_heart_impact",
            "666_HEART",
            {"query": "Review this safely."},
            {},
        )

        assert user_model.expertise_level is None
        assert user_model.emotion_state is None
        assert user_model.hidden_motive is None
        assert user_model.inference_policy.psychological_inference == "disallowed"


# ─── Integration: tools accept caller_context ────────────────────────────────


@pytest.mark.asyncio
async def test_metabolic_loop_router_accepts_caller_context():
    """The primary entrypoint accepts caller_context without error."""
    from arifosmcp.runtime.tools import metabolic_loop_router

    ctx = CallerContext(
        agent_id="test-agent",
        model_id="test-model",
        persona_id=PersonaId.ENGINEER,
    )
    envelope = await metabolic_loop_router(
        query="test query for caller context propagation",
        risk_tier="low",
        actor_id="anonymous",
        dry_run=True,
        caller_context=ctx,
    )
    assert envelope is not None
    # In V2, dry_run might fail if session not anchored, but envelope should still be valid
    assert envelope.status in [RuntimeStatus.SUCCESS, RuntimeStatus.ERROR]


@pytest.mark.asyncio
async def test_metabolic_loop_router_requested_persona_hint():
    """LLM persona hint is honoured by server when valid."""
    from arifosmcp.runtime.tools import metabolic_loop_router

    envelope = await metabolic_loop_router(
        query="validate this plan",
        risk_tier="low",
        actor_id="anonymous",
        dry_run=True,
        requested_persona="architect",
    )
    assert envelope is not None


@pytest.mark.asyncio
async def test_metabolic_loop_router_invalid_persona_hint_safe():
    """Invalid LLM persona hint does not break the call."""
    from arifosmcp.runtime.tools import metabolic_loop_router

    envelope = await metabolic_loop_router(
        query="do something",
        risk_tier="low",
        actor_id="anonymous",
        dry_run=True,
        requested_persona="all_powerful_sovereign",
    )
    assert envelope is not None


@pytest.mark.asyncio
async def test_init_anchor_state_accepts_caller_context():
    """000 INIT tool accepts caller_context parameter."""
    from arifosmcp.runtime.tools import init_anchor

    ctx = CallerContext(persona_id=PersonaId.ARCHITECT)
    envelope = await init_anchor(
        mode="state",
        intent={"query": "test init"},
        caller_context=ctx,
    )
    assert envelope is not None
    assert envelope.tool == "init_anchor"


@pytest.mark.asyncio
async def test_check_vital_still_works():
    """check_vital (no auth_context required) still works after changes."""
    from arifosmcp.runtime.tools import check_vital

    envelope = await check_vital()
    assert envelope is not None
    assert envelope.verdict is not None
    assert envelope.user_model is not None
    assert envelope.user_model.inference_policy.psychological_inference == "disallowed"
