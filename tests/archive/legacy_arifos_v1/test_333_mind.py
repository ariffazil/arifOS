"""
Tests for arifos/tools/_333_mind.py — mode: reason/reflect/forge + multimodal.

conftest.py installs arifosmcp.core.governance mocks at collection time.
All mocks: Verdict, ThermodynamicMetrics, append_vault999_event, governed_return.

Envelope shape (governed_return wrap):
    result = {
        status, verdict, tool, output={...report...}, raw_output,
        metrics, identity, zkpc_receipt, invariant_failures,
        metabolic_metadata={...}
    }
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import arifosmcp.tools._333_mind as _mind_mod

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — valid bind artifact
# ─────────────────────────────────────────────────────────────────────────────


def make_valid_bind_artifact(**overrides):
    artifact = {
        "schema_version": "2.0.0",
        "session_id": "session-test-123",
        "epoch": "2026.04",
        "actor_binding": {
            "operator_id": "arif",
            "identity_verified": True,
            "identity_reason": "test",
        },
        "agent_identity": {
            "type": "AI_instrument",
            "nature": "governed_machine_not_person",
            "not_claiming": [],
            "role": "general",
        },
        "godel_lock": {
            "acknowledged": True,
            "lock_items": list(_mind_mod.GODEL_LOCK_INVARIANTS),
        },
        "floors": {
            "F0_SOVEREIGN": {"name": "SOVEREIGN"},
            "F1_AMANAH": {"name": "AMANAH"},
            "F2_TRUTH": {"name": "TRUTH"},
            "F8_GOVERNANCE": {"name": "GOVERNANCE"},
            "F9_ANTIHANTU": {"name": "ANTI-HANTU"},
            "L10_ONTOLOGY": {"name": "ONTOLOGY"},
        },
        "lifecycle": {
            "current_stage": "333_FORGE",
            "verdict_authority": "888_JUDGE",
            "next_stage": "444_MIND",
        },
        "lane": {
            "constraints": {
                "may": ["reason", "query"],
                "may_not": ["irreversible_actions_without_HOLD"],
            }
        },
        "telemetry_baseline": {
            "omega": 0.72,
            "delta_S": -0.05,
            "psi": 0.1,
            "kappa_r": 1.0,
        },
    }
    for k, v in overrides.items():
        keys = k.split(".", 1)
        if len(keys) == 2:
            artifact[keys[0]][keys[1]] = v
        else:
            artifact[k] = v
    return artifact


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestBindArtifactValidation:
    """Tests for bind_artifact validation."""

    def test_valid_bind_artifact_passes(self):
        artifact = make_valid_bind_artifact()
        result = _mind_mod._validate_bind_artifact(artifact)
        assert result["session_id"] == "session-test-123"

    def test_missing_bind_artifact_raises(self):
        with pytest.raises(_mind_mod.BindArtifactError) as exc:
            _mind_mod._validate_bind_artifact(None)
        assert exc.value.field == "bind_artifact"

    def test_wrong_schema_version_raises(self):
        artifact = make_valid_bind_artifact(schema_version="99.99")
        with pytest.raises(_mind_mod.BindArtifactError) as exc:
            _mind_mod._validate_bind_artifact(artifact)
        assert exc.value.field == "schema_version"

    def test_missing_required_top_level_field_raises(self):
        artifact = make_valid_bind_artifact()
        del artifact["session_id"]
        with pytest.raises(_mind_mod.BindArtifactError) as exc:
            _mind_mod._validate_bind_artifact(artifact)
        assert exc.value.field == "required_fields"

    def test_missing_required_floors_raises(self):
        artifact = make_valid_bind_artifact()
        del artifact["floors"]["F9_ANTIHANTU"]
        with pytest.raises(_mind_mod.BindArtifactError) as exc:
            _mind_mod._validate_bind_artifact(artifact)
        assert "Missing required floors" in exc.value.reason

    def test_godel_lock_not_acknowledged_raises(self):
        artifact = make_valid_bind_artifact()
        artifact["godel_lock"]["acknowledged"] = False
        with pytest.raises(_mind_mod.BindArtifactError) as exc:
            _mind_mod._validate_bind_artifact(artifact)
        assert exc.value.field == "godel_lock.acknowledged"

    def test_missing_godel_lock_items_raises(self):
        artifact = make_valid_bind_artifact()
        artifact["godel_lock"]["lock_items"] = ["only_one"]
        with pytest.raises(_mind_mod.BindArtifactError) as exc:
            _mind_mod._validate_bind_artifact(artifact)
        assert "Missing required" in exc.value.reason

    def test_wrong_lifecycle_stage_raises(self):
        artifact = make_valid_bind_artifact()
        artifact["lifecycle"]["current_stage"] = "111_OBSERVE"
        with pytest.raises(_mind_mod.BindArtifactError) as exc:
            _mind_mod._validate_bind_artifact(artifact)
        # Stage was renamed from 333_REASON → 333_MIND
        assert "333_MIND" in exc.value.reason or "111_OBSERVE" in exc.value.reason

    def test_extract_godel_invariants(self):
        artifact = make_valid_bind_artifact()
        result = _mind_mod._extract_godel_invariants(artifact)
        assert result == _mind_mod.GODEL_LOCK_INVARIANTS

    def test_extract_telemetry_baseline(self):
        artifact = make_valid_bind_artifact()
        result = _mind_mod._extract_telemetry_baseline(artifact)
        assert result["omega"] == 0.72

    def test_extract_lane_constraints(self):
        artifact = make_valid_bind_artifact()
        result = _mind_mod._extract_lane_constraints(artifact)
        assert "may" in result


class TestReasoningLanes:
    """Tests for reasoning lane evaluation."""

    def test_logic_lane_active_on_analyze(self):
        lanes = _mind_mod._evaluate_reasoning_lanes({"query": "analyze the logic"})
        assert lanes["logic"]["status"] == "ACTIVE"
        assert lanes["logic"]["score"] > 0.5

    def test_safety_lane_active_on_risk(self):
        lanes = _mind_mod._evaluate_reasoning_lanes({"query": "assess risk"})
        assert lanes["safety"]["status"] == "ACTIVE"

    def test_sovereignty_lane_active_on_veto(self):
        lanes = _mind_mod._evaluate_reasoning_lanes({"query": "veto override"})
        assert lanes["sovereignty"]["status"] == "ACTIVE"

    def test_physics_lane_active_on_geo_query(self):
        lanes = _mind_mod._evaluate_reasoning_lanes({"query": "geological formation"})
        assert lanes["physics"]["status"] == "ACTIVE"

    def test_all_lanes_dormant_for_vague_query(self):
        lanes = _mind_mod._evaluate_reasoning_lanes({"query": "hello world"})
        for lane_id in ["logic", "safety", "sovereignty", "physics"]:
            assert lanes[lane_id]["status"] == "DORMANT"


class TestExecute:
    """Tests for execute() main entry point.

    Envelope structure (result from governed_return):
        {
            status, verdict, tool,
            output={ query, context, depth, mode, reasoning_lanes, global_confidence, reasoning_hash, ... },
            raw_output, metrics, identity, zkpc_receipt, invariant_failures,
            metabolic_metadata={ ... }
        }
    """

    @pytest.mark.asyncio
    async def test_execute_with_valid_bind_artifact(self):
        artifact = make_valid_bind_artifact()
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "test reasoning", "context": "test"},
        )
        assert result["status"] == "ACTIVE"
        assert result["verdict"] == "CLAIM_ONLY"
        assert result["output"]["query"] == "test reasoning"

    @pytest.mark.asyncio
    async def test_execute_without_bind_artifact_returns_void(self):
        result = await _mind_mod.execute(
            bind_artifact=None,
            problem_set={"query": "test"},
        )
        assert result["status"] == "BOUND_FAIL"
        assert result["verdict"] == "VOID"

    @pytest.mark.asyncio
    async def test_execute_with_invalid_schema_version(self):
        artifact = make_valid_bind_artifact(schema_version="0.0.1")
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "test"},
        )
        assert result["status"] == "BOUND_FAIL"
        assert result["verdict"] == "VOID"

    @pytest.mark.asyncio
    async def test_execute_inherits_telemetry_baseline(self):
        artifact = make_valid_bind_artifact()
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "test"},
        )
        # global_confidence lives in output (reasoning report)
        assert result["output"]["global_confidence"] == 0.72
        # metabolic_metadata carries telemetry inheritance proof
        assert result["metabolic_metadata"]["confidence_score"] == 0.72
        assert result["metabolic_metadata"]["bind_schema_version"] == "2.0.0"
        assert result["metabolic_metadata"]["godel_inherited_count"] == 5

    @pytest.mark.asyncio
    async def test_execute_returns_reasoning_hash(self):
        artifact = make_valid_bind_artifact()
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "test reasoning", "context": "test context"},
        )
        assert "reasoning_hash" in result["output"]
        assert len(result["output"]["reasoning_hash"]) == 64  # SHA-256 hex

    @pytest.mark.asyncio
    async def test_execute_reason_mode(self):
        artifact = make_valid_bind_artifact()
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "analyze this"},
            mode="reason",
        )
        assert result["output"]["mode"] == "reason"
        assert result["status"] == "ACTIVE"

    @pytest.mark.asyncio
    async def test_execute_reflect_mode(self):
        artifact = make_valid_bind_artifact()
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "compare approaches"},
            mode="reflect",
        )
        assert result["output"]["mode"] == "reflect"

    @pytest.mark.asyncio
    async def test_execute_forge_mode(self):
        artifact = make_valid_bind_artifact()
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "design solution"},
            mode="forge",
        )
        assert result["output"]["mode"] == "forge"


class TestGodelLockInheritance:
    """Tests verifying Gödel lock is properly inherited."""

    @pytest.mark.asyncio
    async def test_godel_inherited_count_in_metadata(self):
        artifact = make_valid_bind_artifact()
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "test"},
        )
        assert result["metabolic_metadata"]["godel_inherited_count"] == len(
            _mind_mod.GODEL_LOCK_INVARIANTS
        )

    @pytest.mark.asyncio
    async def test_bind_epoch_in_output(self):
        artifact = make_valid_bind_artifact(epoch="2026.05")
        result = await _mind_mod.execute(
            bind_artifact=artifact,
            problem_set={"query": "test"},
        )
        # epoch is embedded in the reasoning report inside output
        assert result["output"]["bind_epoch"] == "2026.05"


class TestMultimodalHelpers:
    """Tests for individual multimodal helper functions."""

    @pytest.mark.asyncio
    async def test_web_search_returns_structure(self):
        result = await _mind_mod._web_search("test query")
        assert result["capability"] == "web_search"
        assert result["verdict"] == "CLAIM_ONLY"
        assert result["query"] == "test query"

    @pytest.mark.asyncio
    async def test_understand_image_returns_structure(self):
        result = await _mind_mod._interpret_image_signals(
            "http://example.com/img.png", "what is this?"
        )
        assert result["capability"] == "visual_signal_interpretation"
        assert result["image_url"] == "http://example.com/img.png"
        assert result["question"] == "what is this?"

    @pytest.mark.asyncio
    async def test_text_to_image_returns_structure(self):
        result = await _mind_mod._text_to_image("a beautiful sunset")
        assert result["capability"] == "text_to_image"

    @pytest.mark.asyncio
    async def test_text_to_audio_returns_structure(self):
        result = await _mind_mod._text_to_audio("Hello world")
        assert result["capability"] == "text_to_audio"
        assert result["text"] == "Hello world"

    @pytest.mark.asyncio
    async def test_music_generation_returns_structure(self):
        result = await _mind_mod._music_generation("energetic rock song")
        assert result["capability"] == "music_generation"

    @pytest.mark.asyncio
    async def test_generate_video_returns_structure(self):
        result = await _mind_mod._generate_video("a cat playing piano")
        assert result["capability"] == "video_generation"
        assert result["prompt"] == "a cat playing piano"
