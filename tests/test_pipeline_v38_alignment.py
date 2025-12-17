"""
test_pipeline_v38_alignment.py - v38Omega Pipeline Alignment Tests

Checks that:
- canon/03_PIPELINE_v38Omega.md exists
- spec/pipeline_v38Omega.yaml exists and is valid
- All 10 stages are defined in spec
- Class A/B routes in spec match actual Pipeline.run behavior
- Memory routing matches spec
- Stage trace format matches spec examples

Author: arifOS Project
Version: v38.0.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

from arifos_core.pipeline import (
    Pipeline,
    PipelineState,
    StakesClass,
    stage_000_void,
    stage_111_sense,
    stage_222_reflect,
    stage_333_reason,
    stage_444_align,
    stage_555_empathize,
    stage_666_bridge,
    stage_777_forge,
    stage_888_judge,
    stage_999_seal,
)
from arifos_core.memory.policy import VERDICT_BAND_ROUTING


REPO_ROOT = Path(__file__).resolve().parents[1]
V38_CANON_PATH = REPO_ROOT / "archive" / "v38_0_0" / "canon" / "_PIPELINE_v38Omega.md"
V38_SPEC_PATH = REPO_ROOT / "spec" / "pipeline_v38Omega.yaml"


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def pipeline_spec_v38() -> dict:
    """Load the v38Omega pipeline spec."""
    assert V38_SPEC_PATH.exists(), f"Missing v38 pipeline spec at {V38_SPEC_PATH}"
    with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


# =============================================================================
# SPEC & CANON FILE TESTS
# =============================================================================

class TestV38PipelineSpecFile:
    """Tests for the v38Omega pipeline spec file structure."""

    def test_v38_canon_exists(self) -> None:
        """v38 pipeline canon file must exist."""
        assert V38_CANON_PATH.exists(), f"Missing v38 pipeline canon at {V38_CANON_PATH}"

    def test_v38_spec_exists(self) -> None:
        """v38 pipeline spec file must exist."""
        assert V38_SPEC_PATH.exists(), f"Missing v38 pipeline spec at {V38_SPEC_PATH}"

    def test_v38_spec_is_valid_yaml(self) -> None:
        """v38 pipeline spec must be valid YAML."""
        with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)

    def test_v38_spec_metadata(self, pipeline_spec_v38: dict) -> None:
        """Spec must declare v38 metadata."""
        assert pipeline_spec_v38.get("version") == "v38.0.0"
        assert pipeline_spec_v38.get("arifos_version") == "38Omega"
        assert pipeline_spec_v38.get("spec_type") == "pipeline"


# =============================================================================
# STAGE DEFINITION TESTS
# =============================================================================

class TestStageDefinitions:
    """Tests that all 10 stages are defined in spec."""

    EXPECTED_STAGES = ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"]

    def test_all_stages_present(self, pipeline_spec_v38: dict) -> None:
        """All 10 stages must be defined in spec."""
        stages = pipeline_spec_v38.get("stages", {})
        for stage_id in self.EXPECTED_STAGES:
            assert stage_id in stages, f"Missing stage {stage_id} in spec"

    def test_stages_have_required_fields(self, pipeline_spec_v38: dict) -> None:
        """Each stage must have required fields."""
        stages = pipeline_spec_v38.get("stages", {})
        required_fields = ["name", "functions", "purpose", "class_a", "class_b", "canon_ref"]

        for stage_id, stage_def in stages.items():
            for field in required_fields:
                assert field in stage_def, f"Stage {stage_id} missing required field: {field}"

    def test_stage_names_match_convention(self, pipeline_spec_v38: dict) -> None:
        """Stage names must follow naming convention."""
        expected_names = {
            "000": "RESET",
            "111": "SENSE",
            "222": "REFLECT",
            "333": "REASON",
            "444": "ALIGN",
            "555": "EMPATHIZE",
            "666": "BRIDGE",
            "777": "FORGE",
            "888": "JUDGE",
            "999": "SEAL",
        }
        stages = pipeline_spec_v38.get("stages", {})

        for stage_id, expected_name in expected_names.items():
            actual_name = stages.get(stage_id, {}).get("name")
            assert actual_name == expected_name, (
                f"Stage {stage_id} name mismatch: expected {expected_name}, got {actual_name}"
            )


# =============================================================================
# ROUTING TESTS
# =============================================================================

class TestRoutingDefinitions:
    """Tests for Class A/B routing definitions in spec."""

    def test_class_a_routing_defined(self, pipeline_spec_v38: dict) -> None:
        """Class A routing must be defined."""
        routing = pipeline_spec_v38.get("routing", {})
        assert "ClassA" in routing, "Missing ClassA routing definition"

        class_a = routing["ClassA"]
        assert "stages" in class_a
        assert "skips" in class_a

    def test_class_b_routing_defined(self, pipeline_spec_v38: dict) -> None:
        """Class B routing must be defined."""
        routing = pipeline_spec_v38.get("routing", {})
        assert "ClassB" in routing, "Missing ClassB routing definition"

        class_b = routing["ClassB"]
        assert "stages" in class_b
        assert class_b.get("skips") == []  # Class B skips nothing

    def test_class_a_stages_match_spec(self, pipeline_spec_v38: dict) -> None:
        """Class A stages must be 000, 111, 333, 888, 999."""
        routing = pipeline_spec_v38.get("routing", {})
        class_a_stages = routing.get("ClassA", {}).get("stages", [])

        expected = ["000", "111", "333", "888", "999"]
        assert class_a_stages == expected, (
            f"Class A stages mismatch: expected {expected}, got {class_a_stages}"
        )

    def test_class_b_stages_match_spec(self, pipeline_spec_v38: dict) -> None:
        """Class B stages must be all 10 stages."""
        routing = pipeline_spec_v38.get("routing", {})
        class_b_stages = routing.get("ClassB", {}).get("stages", [])

        expected = ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"]
        assert class_b_stages == expected, (
            f"Class B stages mismatch: expected {expected}, got {class_b_stages}"
        )

    def test_class_a_skips_222_444_555_666_777(self, pipeline_spec_v38: dict) -> None:
        """Class A must skip stages 222, 444, 555, 666, 777."""
        routing = pipeline_spec_v38.get("routing", {})
        class_a_skips = routing.get("ClassA", {}).get("skips", [])

        expected_skips = ["222", "444", "555", "666", "777"]
        assert sorted(class_a_skips) == sorted(expected_skips), (
            f"Class A skips mismatch: expected {expected_skips}, got {class_a_skips}"
        )


# =============================================================================
# MEMORY ROUTING TESTS
# =============================================================================

class TestMemoryRouting:
    """Tests that memory routing in spec matches policy.py."""

    def test_memory_routing_defined(self, pipeline_spec_v38: dict) -> None:
        """memory_routing section must be defined."""
        assert "memory_routing" in pipeline_spec_v38

    def test_verdict_band_map_defined(self, pipeline_spec_v38: dict) -> None:
        """verdict_band_map must be defined with all verdicts."""
        mem_routing = pipeline_spec_v38.get("memory_routing", {})
        verdict_map = mem_routing.get("verdict_band_map", {})

        expected_verdicts = ["SEAL", "SABAR", "PARTIAL", "VOID", "888_HOLD"]
        for v in expected_verdicts:
            assert v in verdict_map, f"Missing verdict {v} in verdict_band_map"

    def test_seal_routing_matches_policy(self, pipeline_spec_v38: dict) -> None:
        """SEAL routing in spec must match VERDICT_BAND_ROUTING."""
        mem_routing = pipeline_spec_v38.get("memory_routing", {})
        spec_seal_bands = mem_routing.get("verdict_band_map", {}).get("SEAL", {}).get("bands", [])
        policy_seal_bands = VERDICT_BAND_ROUTING.get("SEAL", [])

        assert sorted(spec_seal_bands) == sorted(policy_seal_bands), (
            f"SEAL bands mismatch: spec={spec_seal_bands}, policy={policy_seal_bands}"
        )

    def test_void_routing_matches_policy(self, pipeline_spec_v38: dict) -> None:
        """VOID routing in spec must match VERDICT_BAND_ROUTING (only VOID band)."""
        mem_routing = pipeline_spec_v38.get("memory_routing", {})
        spec_void_bands = mem_routing.get("verdict_band_map", {}).get("VOID", {}).get("bands", [])
        policy_void_bands = VERDICT_BAND_ROUTING.get("VOID", [])

        assert spec_void_bands == ["VOID"], "VOID must only route to VOID band"
        assert spec_void_bands == policy_void_bands

    def test_void_never_canonical(self, pipeline_spec_v38: dict) -> None:
        """VOID routing must have canonical=false."""
        mem_routing = pipeline_spec_v38.get("memory_routing", {})
        void_config = mem_routing.get("verdict_band_map", {}).get("VOID", {})

        assert void_config.get("canonical") is False, "VOID must never be canonical"

    def test_inv1_documented(self, pipeline_spec_v38: dict) -> None:
        """INV-1 (VOID never canonical) must be documented."""
        mem_routing = pipeline_spec_v38.get("memory_routing", {})
        invariants = mem_routing.get("invariants", [])

        inv1_found = any(inv.get("id") == "INV-1" for inv in invariants)
        assert inv1_found, "INV-1 not documented in memory_routing.invariants"


# =============================================================================
# STAGE TRACE TESTS
# =============================================================================

class TestStageTrace:
    """Tests for stage trace format in spec."""

    def test_stage_trace_examples_defined(self, pipeline_spec_v38: dict) -> None:
        """stage_trace examples must be defined."""
        stage_trace = pipeline_spec_v38.get("stage_trace", {})
        examples = stage_trace.get("examples", {})

        assert "class_a" in examples, "Missing class_a stage trace example"
        assert "class_b" in examples, "Missing class_b stage trace example"
        assert "early_void" in examples, "Missing early_void stage trace example"

    def test_class_a_trace_matches_pattern(self, pipeline_spec_v38: dict) -> None:
        """Class A trace must follow expected pattern."""
        stage_trace = pipeline_spec_v38.get("stage_trace", {})
        class_a_example = stage_trace.get("examples", {}).get("class_a", [])

        # Must start with 000_VOID, include 111_SENSE, 333_REASON, end with 999_SEAL
        assert class_a_example[0] == "000_VOID"
        assert "111_SENSE" in class_a_example
        assert "333_REASON" in class_a_example
        assert "888_JUDGE" in class_a_example
        assert class_a_example[-1] == "999_SEAL"

        # Must NOT include Class B stages
        for entry in class_a_example:
            assert not entry.startswith("222_")
            assert not entry.startswith("444_")
            assert not entry.startswith("555_")
            assert not entry.startswith("666_")
            assert not entry.startswith("777_")

    def test_class_b_trace_includes_all_stages(self, pipeline_spec_v38: dict) -> None:
        """Class B trace must include all pipeline stages."""
        stage_trace = pipeline_spec_v38.get("stage_trace", {})
        class_b_example = stage_trace.get("examples", {}).get("class_b", [])

        # Must include all stages
        expected_prefixes = ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"]

        trace_str = " ".join(class_b_example)
        for prefix in expected_prefixes:
            assert prefix in trace_str, f"Class B trace missing stage {prefix}"


# =============================================================================
# RUNTIME BEHAVIOR TESTS
# =============================================================================

class TestPipelineRuntime:
    """Tests that actual Pipeline.run behavior matches spec."""

    def test_class_a_routing_behavior(self) -> None:
        """Class A query should skip 222, 444, 555, 666, 777."""
        pipeline = Pipeline()
        state = pipeline.run("What is 2 + 2?")

        # Check stage trace
        trace_str = " ".join(state.stage_trace)

        # Must include Class A stages
        assert "000_VOID" in trace_str
        assert "111_SENSE" in trace_str
        assert "333_REASON" in trace_str
        assert "888_JUDGE" in trace_str
        assert "999_SEAL" in trace_str

        # Must NOT include Class B only stages
        assert "222_REFLECT" not in trace_str
        assert "444_ALIGN" not in trace_str
        assert "555_EMPATHIZE" not in trace_str
        assert "666_BRIDGE" not in trace_str
        assert "777_FORGE" not in trace_str

    def test_class_b_routing_behavior(self) -> None:
        """Class B query (forced) should include all stages."""
        pipeline = Pipeline()
        state = pipeline.run("What is 2 + 2?", force_class=StakesClass.CLASS_B)

        # Check stage trace
        trace_str = " ".join(state.stage_trace)

        # Must include all stages
        assert "000_VOID" in trace_str
        assert "111_SENSE" in trace_str
        assert "222_REFLECT" in trace_str
        assert "333_REASON" in trace_str
        assert "444_ALIGN" in trace_str
        assert "555_EMPATHIZE" in trace_str
        assert "666_BRIDGE" in trace_str
        assert "777_FORGE" in trace_str
        assert "888_JUDGE" in trace_str
        assert "999_SEAL" in trace_str

    def test_high_stakes_triggers_class_b(self) -> None:
        """High-stakes keywords should trigger Class B."""
        pipeline = Pipeline()

        # "is it ethical" is a high-stakes pattern
        state = pipeline.run("Is it ethical to lie?")

        assert state.stakes_class == StakesClass.CLASS_B
        assert "is it ethical" in state.high_stakes_indicators

        # Check that 222 was included
        trace_str = " ".join(state.stage_trace)
        assert "222_REFLECT" in trace_str

    def test_amanah_pass_includes_trace(self) -> None:
        """Amanah pass should include trace entry."""
        pipeline = Pipeline()
        state = pipeline.run("Hello world")

        trace_str = " ".join(state.stage_trace)
        assert "000_AMANAH_PASS" in trace_str or "000_VOID" in trace_str


# =============================================================================
# CANON CONTENT TESTS
# =============================================================================

class TestPipelineCanonContent:
    """Tests for the v38 pipeline canon file content."""

    def test_canon_has_all_stages_documented(self) -> None:
        """Canon file must document all 10 stages."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")

        stage_markers = [
            "Stage 000",
            "Stage 111",
            "Stage 222",
            "Stage 333",
            "Stage 444",
            "Stage 555",
            "Stage 666",
            "Stage 777",
            "Stage 888",
            "Stage 999",
        ]

        for marker in stage_markers:
            assert marker in content, f"Canon missing documentation for {marker}"

    def test_canon_has_class_a_routing(self) -> None:
        """Canon must document Class A routing."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Class A" in content
        assert "Low-Stakes" in content or "Fast Path" in content

    def test_canon_has_class_b_routing(self) -> None:
        """Canon must document Class B routing."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Class B" in content
        assert "High-Stakes" in content or "Deep Path" in content

    def test_canon_has_memory_integration(self) -> None:
        """Canon must document memory integration."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Memory Integration" in content or "memory_routing" in content.lower()
        assert "VOID" in content
        assert "LEDGER" in content

    def test_canon_has_v38_version(self) -> None:
        """Canon file must indicate v38 version."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "v38" in content or "38Omega" in content


# =============================================================================
# HIGH-STAKES PATTERNS TEST
# =============================================================================

class TestHighStakesPatterns:
    """Tests that spec high-stakes patterns match code."""

    def test_high_stakes_patterns_documented(self, pipeline_spec_v38: dict) -> None:
        """High-stakes patterns must be documented in spec."""
        patterns = pipeline_spec_v38.get("high_stakes_patterns", {})
        assert "patterns" in patterns
        assert len(patterns["patterns"]) > 0

    def test_key_patterns_present(self, pipeline_spec_v38: dict) -> None:
        """Key high-stakes patterns must be in spec."""
        patterns = pipeline_spec_v38.get("high_stakes_patterns", {}).get("patterns", [])

        key_patterns = ["kill", "harm", "illegal", "medical", "is it ethical"]
        for p in key_patterns:
            assert p in patterns, f"Missing key pattern: {p}"


# =============================================================================
# AAA ENGINE MAPPING TEST
# =============================================================================

class TestAAAEngineMapping:
    """Tests for AAA engine mapping in spec."""

    def test_aaa_mapping_defined(self, pipeline_spec_v38: dict) -> None:
        """AAA engine mapping must be defined."""
        mapping = pipeline_spec_v38.get("aaa_engine_mapping", {})

        assert "ARIF_AGI" in mapping
        assert "ADAM_ASI" in mapping
        assert "APEX_PRIME" in mapping

    def test_arif_stages_correct(self, pipeline_spec_v38: dict) -> None:
        """AGI (Architect) stages must be 111, 333, 444."""
        mapping = pipeline_spec_v38.get("aaa_engine_mapping", {})
        arif_stages = mapping.get("ARIF_AGI", {}).get("stages", [])

        assert "111" in arif_stages
        assert "333" in arif_stages
        assert "444" in arif_stages

    def test_adam_stages_correct(self, pipeline_spec_v38: dict) -> None:
        """ASI (Auditor) stages must be 555, 666, 777."""
        mapping = pipeline_spec_v38.get("aaa_engine_mapping", {})
        adam_stages = mapping.get("ADAM_ASI", {}).get("stages", [])

        assert "555" in adam_stages
        assert "666" in adam_stages
        assert "777" in adam_stages

    def test_apex_stages_correct(self, pipeline_spec_v38: dict) -> None:
        """APEX PRIME stages must be 888."""
        mapping = pipeline_spec_v38.get("aaa_engine_mapping", {})
        apex_stages = mapping.get("APEX_PRIME", {}).get("stages", [])

        assert "888" in apex_stages


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
