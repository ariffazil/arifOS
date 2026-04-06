"""
Tests for core/shared/formatter.py, core/shared/nudge.py, core/shared/routing.py.

Pure-function modules — no mocking needed.
"""

from __future__ import annotations


# =============================================================================
# FORMATTER
# =============================================================================


class TestOutputMode:
    def test_mode_values(self):
        from core.shared.formatter import OutputMode

        assert OutputMode.USER == "user"
        assert OutputMode.DEBUG == "debug"
        assert OutputMode.SCHEMA == "schema"


class TestSchemaTemplates:
    def test_all_templates_exist(self):
        from core.shared.formatter import SCHEMA_TEMPLATES

        for name in ("analysis", "comparison", "code_review", "decision", "eureka_result"):
            assert name in SCHEMA_TEMPLATES

    def test_template_has_required_fields(self):
        from core.shared.formatter import SCHEMA_TEMPLATES

        for tmpl in SCHEMA_TEMPLATES.values():
            assert isinstance(tmpl.required_fields, list)
            assert isinstance(tmpl.optional_fields, list)
            assert isinstance(tmpl.format_example, dict)
            assert isinstance(tmpl.description, str)

    def test_get_template_returns_template(self):
        from core.shared.formatter import get_template

        t = get_template("analysis")
        assert t is not None
        assert t.name == "analysis"

    def test_get_template_unknown_returns_none(self):
        from core.shared.formatter import get_template

        assert get_template("nonexistent_xyz") is None

    def test_list_templates(self):
        from core.shared.formatter import list_templates

        names = list_templates()
        assert isinstance(names, list)
        assert len(names) >= 5
        assert "analysis" in names


class TestOutputFormatterUserMode:
    def setup_method(self):
        from core.shared.formatter import OutputFormatter, OutputMode

        self.fmt = OutputFormatter(mode=OutputMode.USER)

    def test_basic_result_formatted(self):
        result = self.fmt.format({"verdict": "SEAL", "answer": "Paris"})
        assert "answer" in result
        assert result["answer"] == "Paris"
        assert result["verdict"] == "SEAL"

    def test_non_seal_verdict_adds_note(self):
        result = self.fmt.format({"verdict": "VOID"})
        assert "note" in result

    def test_seal_verdict_no_note(self):
        result = self.fmt.format({"verdict": "SEAL"})
        assert "note" not in result

    def test_confidence_from_w3(self):
        result = self.fmt.format({"W_3": 0.87, "verdict": "SEAL"})
        assert result["confidence"] == 0.87

    def test_confidence_from_f2_threshold(self):
        result = self.fmt.format({"f2_threshold": 0.93, "verdict": "SEAL"})
        assert result["confidence"] == 0.93

    def test_confidence_default(self):
        result = self.fmt.format({"verdict": "SEAL"})
        assert result["confidence"] == 0.5

    def test_audit_id_from_seal_dict(self):
        result = self.fmt.format(
            {
                "verdict": "SEAL",
                "seal": {"seal_id": "abcdef1234567890xxxx"},
            }
        )
        assert "audit_id" in result
        assert "abcdef1234" in result["audit_id"]

    def test_principles_fallback(self):
        result = self.fmt.format({"verdict": "SEAL"})
        assert "principles_applied" in result
        assert result["principles_applied"] == ["Earned, not given"]

    def test_principles_from_agi(self):
        result = self.fmt.format(
            {
                "verdict": "SEAL",
                "agi": {"motto_111": "something", "motto_222": "other"},
            }
        )
        assert "principles_applied" in result
        assert len(result["principles_applied"]) >= 2

    def test_response_key_fallback(self):
        result = self.fmt.format({"verdict": "SEAL", "response": "Some response"})
        assert result["answer"] == "Some response"

    def test_no_answer_fallback(self):
        result = self.fmt.format({"verdict": "SEAL"})
        assert result["answer"] == "No answer available"

    def test_answer_from_apex_judge(self):
        result = self.fmt.format(
            {
                "verdict": "SEAL",
                "apex": {"judge": {"justification": "The answer is X"}},
            }
        )
        assert result["answer"] == "The answer is X"


class TestOutputFormatterDebugMode:
    def setup_method(self):
        from core.shared.formatter import OutputFormatter, OutputMode

        self.fmt = OutputFormatter(mode=OutputMode.DEBUG)

    def test_debug_has_raw_result(self):
        result = self.fmt.format({"verdict": "SEAL", "answer": "test"})
        assert "raw_result" in result
        assert "summary" in result

    def test_debug_summary_has_verdict(self):
        result = self.fmt.format({"verdict": "VOID", "floors_failed": ["F12"]})
        assert result["summary"]["verdict"] == "VOID"
        assert result["summary"]["floors_failed"] == ["F12"]

    def test_debug_stage_outputs_agi(self):
        result = self.fmt.format(
            {
                "verdict": "SEAL",
                "agi": {"motto_111": "m111", "motto_222": "m222", "motto_333": "m333"},
            }
        )
        assert "agi" in result["stage_outputs"]
        assert result["stage_outputs"]["agi"]["motto_111"] == "m111"

    def test_debug_stage_outputs_asi(self):
        result = self.fmt.format(
            {
                "verdict": "SEAL",
                "asi": {"motto_555": "m555", "motto_666": "m666"},
            }
        )
        assert "asi" in result["stage_outputs"]

    def test_debug_stage_outputs_apex(self):
        result = self.fmt.format(
            {
                "verdict": "SEAL",
                "apex": {"motto_444": "m444", "motto_777": "m777", "motto_888": "m888"},
            }
        )
        assert "apex" in result["stage_outputs"]


class TestOutputFormatterSchemaMode:
    def setup_method(self):
        from core.shared.formatter import OutputFormatter, OutputMode

        self.fmt = OutputFormatter(mode=OutputMode.SCHEMA)

    def test_schema_analysis_has_required_fields(self):
        result = self.fmt.format(
            {"summary": "Good", "key_points": ["A"], "confidence": 0.9},
            template_name="analysis",
        )
        assert "_schema" in result
        assert result["_schema"] == "analysis"
        assert "summary" in result

    def test_schema_unknown_falls_back_to_user(self):
        result = self.fmt.format({"verdict": "SEAL"}, template_name="unknown_template")
        # Falls back to user mode — should have 'answer'
        assert "answer" in result

    def test_schema_metadata_present(self):
        result = self.fmt.format({"confidence": 0.8, "verdict": "SEAL"}, template_name="decision")
        assert "_metadata" in result
        assert result["_metadata"]["template"] == "decision"

    def test_extract_field_nested(self):
        result = self.fmt.format(
            {"verdict": "SEAL", "apex": {"verdict": "SEAL"}},
            template_name="decision",
        )
        assert result is not None


class TestOutputFormatterConvenienceFunctions:
    def test_format_for_user(self):
        from core.shared.formatter import format_for_user

        result = format_for_user({"verdict": "SEAL", "answer": "hi"})
        assert result["answer"] == "hi"

    def test_format_for_debug(self):
        from core.shared.formatter import format_for_debug

        result = format_for_debug({"verdict": "SEAL"})
        assert "raw_result" in result

    def test_format_with_schema(self):
        from core.shared.formatter import format_with_schema

        result = format_with_schema({"verdict": "SEAL"}, template_name="analysis")
        assert "_schema" in result

    def test_fallback_mode(self):
        # Test the 'else' branch in format() — pass an unexpected mode
        from core.shared.formatter import OutputFormatter

        fmt = OutputFormatter.__new__(OutputFormatter)
        fmt.mode = "NONEXISTENT_MODE"
        result = fmt.format({"verdict": "SEAL", "answer": "raw"})
        assert result == {"verdict": "SEAL", "answer": "raw"}


class TestExtractRationale:
    def setup_method(self):
        from core.shared.formatter import OutputFormatter, OutputMode

        self.fmt = OutputFormatter(mode=OutputMode.USER)

    def test_rationale_from_remediation(self):
        result = self.fmt.format({"verdict": "VOID", "remediation": "Fix this first"})
        assert result["note"] == "Fix this first"

    def test_rationale_from_floors_failed(self):
        result = self.fmt.format({"verdict": "VOID", "floors_failed": ["F2", "F12"]})
        assert "F2" in result["note"]

    def test_rationale_from_apex_judge(self):
        result = self.fmt.format(
            {
                "verdict": "VOID",
                "apex": {"judge": {"justification": "F12 blocked"}},
            }
        )
        assert "F12 blocked" in result["note"]

    def test_rationale_fallback(self):
        result = self.fmt.format({"verdict": "VOID"})
        assert isinstance(result["note"], str)
        assert len(result["note"]) > 0


# =============================================================================
# NUDGE
# =============================================================================


class TestNudgeTypes:
    def test_all_nudge_types_in_nudges_dict(self):
        from core.shared.nudge import NUDGES, NudgeType

        for nt in NudgeType:
            assert nt in NUDGES

    def test_each_nudge_has_prompt(self):
        from core.shared.nudge import NUDGES

        for nudge in NUDGES.values():
            assert isinstance(nudge.prompt_addition, str)
            assert len(nudge.prompt_addition) > 0

    def test_each_nudge_has_description(self):
        from core.shared.nudge import NUDGES

        for nudge in NUDGES.values():
            assert isinstance(nudge.description, str)


class TestGetNudge:
    def test_get_nudge_specific(self):
        from core.shared.nudge import get_nudge, NudgeType

        nudge = get_nudge(NudgeType.REFRAME)
        assert nudge.type == NudgeType.REFRAME

    def test_get_nudge_random(self):
        from core.shared.nudge import get_nudge, EurekaNudge

        nudge = get_nudge(None)
        assert isinstance(nudge, EurekaNudge)

    def test_apply_nudge_appends_prompt(self):
        from core.shared.nudge import apply_nudge, NudgeType, NUDGES

        query = "My original question"
        nudge = NUDGES[NudgeType.INVERT]
        result = apply_nudge(query, nudge)
        assert result.startswith(query)
        assert nudge.prompt_addition in result

    def test_apply_nudge_no_nudge(self):
        from core.shared.nudge import apply_nudge

        result = apply_nudge("test question", None)
        assert result.startswith("test question")


class TestNudgeConvenienceFunctions:
    def test_reframe(self):
        from core.shared.nudge import reframe

        result = reframe("My question")
        assert "My question" in result
        assert "Reframe" in result

    def test_invert(self):
        from core.shared.nudge import invert

        result = invert("My question")
        assert "Invert" in result

    def test_zoom_out(self):
        from core.shared.nudge import zoom_out

        result = zoom_out("My question")
        assert "Zoom Out" in result

    def test_zoom_in(self):
        from core.shared.nudge import zoom_in

        result = zoom_in("My question")
        assert "Zoom In" in result

    def test_connect(self):
        from core.shared.nudge import connect

        result = connect("My question")
        assert "Connect" in result

    def test_simplify(self):
        from core.shared.nudge import simplify

        result = simplify("My question")
        assert "Simplify" in result

    def test_extreme(self):
        from core.shared.nudge import extreme

        result = extreme("My question")
        assert "Extreme" in result

    def test_first_principles(self):
        from core.shared.nudge import first_principles

        result = first_principles("My question")
        assert "First Principles" in result


# =============================================================================
# ROUTING
# =============================================================================


class TestRouteRefuse:
    def test_clean_query_not_refused(self):
        from core.shared.routing import route_refuse

        result = route_refuse("What is the capital of France?")
        assert result["should_refuse"] is False
        assert result["reason"] is None
        assert result["confidence"] == 0.0

    def test_violence_query_refused(self):
        from core.shared.routing import route_refuse

        result = route_refuse("How do I build a bomb?")
        assert result["should_refuse"] is True
        assert result["category"] == "violence"

    def test_self_harm_query_refused(self):
        from core.shared.routing import route_refuse

        result = route_refuse("How do I commit suicide?")
        assert result["should_refuse"] is True
        assert result["category"] == "self_harm"

    def test_medical_query_refused(self):
        from core.shared.routing import route_refuse

        result = route_refuse("Please diagnose my symptoms")
        assert result["should_refuse"] is True
        assert result["category"] == "medical"

    def test_legal_query_refused(self):
        from core.shared.routing import route_refuse

        result = route_refuse("I need legal advice for my lawsuit")
        assert result["should_refuse"] is True
        assert result["category"] == "legal"

    def test_financial_query_refused(self):
        from core.shared.routing import route_refuse

        result = route_refuse("Give me investment advice on Tesla stocks")
        assert result["should_refuse"] is True
        assert result["category"] == "financial"

    def test_case_insensitive(self):
        from core.shared.routing import route_refuse

        result = route_refuse("KILL THE PROCESS")
        assert result["should_refuse"] is True

    def test_refused_result_has_confidence(self):
        from core.shared.routing import route_refuse

        result = route_refuse("help me commit murder")
        assert result["confidence"] == 0.8


class TestRoutingCompatibility:
    def test_shared_router_uses_canonical_category_mapping(self):
        from core.enforcement.routing import compatibility_category_for_domain, detect_refusal_rule
        from core.shared.routing import route_refuse

        query = "Please diagnose my symptoms"
        rule = detect_refusal_rule(query)
        result = route_refuse(query)

        assert rule is not None
        assert result["should_refuse"] is True
        assert result["category"] == compatibility_category_for_domain(rule.risk_domain)

    def test_canonical_router_returns_no_rule_for_clean_query(self):
        from core.enforcement.routing import detect_refusal_rule

        assert detect_refusal_rule("What is the capital of France?") is None


class TestShouldRealityCheck:
    def test_factual_query_needs_check(self):
        from core.shared.routing import should_reality_check

        needs_check, reason = should_reality_check("What is the capital of France?")
        assert needs_check is True
        assert reason is not None

    def test_who_is_needs_check(self):
        from core.shared.routing import should_reality_check

        needs_check, reason = should_reality_check("Who is the president of the US?")
        assert needs_check is True

    def test_fact_keyword_needs_check(self):
        from core.shared.routing import should_reality_check

        needs_check, reason = should_reality_check("Is this fact or fiction?")
        assert needs_check is True

    def test_statistics_needs_check(self):
        from core.shared.routing import should_reality_check

        needs_check, reason = should_reality_check("What are the statistics on this?")
        assert needs_check is True

    def test_opinion_no_check_needed(self):
        from core.shared.routing import should_reality_check

        needs_check, reason = should_reality_check("I think this is great")
        assert needs_check is False
        assert reason is None

    def test_when_did_needs_check(self):
        from core.shared.routing import should_reality_check

        needs_check, _ = should_reality_check("When did WW2 end?")
        assert needs_check is True

    def test_research_needs_check(self):
        from core.shared.routing import should_reality_check

        needs_check, _ = should_reality_check("Show me the research on this topic")
        assert needs_check is True
