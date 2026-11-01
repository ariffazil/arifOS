"""F6 G3 — prohibited-inference lexical gate + heart person-target guard (HUMAN_RASA P0).

Gap G3: heart.py's output schema carried a `sentiment` field — "Emotional/
sentiment assessment of target" (heart.py:841) — i.e. heart would assert a
target's inner state; and privacy_and_redress.py only forbids human-scoring
KEY NAMES, it never inspects free text for prohibited inference about a person.

This suite freezes the tightened contract:

  - inference_grammar.check_human_claim(text, subject_is_person) ->
    {decision: ALLOW|HOLD|VOID, hits: [...]}:
      HOLD — third-party inner-state assertion (emotion/motive/intent/trust/
             deception/diagnosis/personality), English AND BM.
      VOID — betrayal prediction / honesty scoring (never emitted).
      ALLOW — first-person self-report, observable metrics, non-person subject.
  - heart.py: person target -> `sentiment` dropped from schema AND result,
    replaced by `inner_state: "UNKNOWN"`; non-person targets unchanged.

KNOWN LIMIT: lexical gate — will miss paraphrase.

Fixtures are synthetic only (subject "PERSON_A" — never a real person).
No egress. No VAULT999. No live /root writes.

Run:
    python3 -m pytest tests/constitutional/test_f6_inference_grammar_g3.py -q
"""

from __future__ import annotations

import pytest
from arifosmcp.runtime.f6.inference_grammar import (
    check_human_claim,
    target_is_person,
)
from arifosmcp.tools.heart import _schema_for_target

# ── Required BM phrases (3rd-person inner-state assertions) ──────────────────
BM_PHRASES = [
    "dia sedang menjauh dari keluarganya",
    "dia kehilangan minat pada topik itu",
    "dia tertekan sejak kebelakangan ini",
    "nada menunjukkan marah apabila menjawab",
    "wajah menunjukkan penipuan semasa bercakap",
    "corak ini menunjukkan pengkhianatan",
]

# ── English equivalents ──────────────────────────────────────────────────────
EN_PHRASES = [
    "he is distancing himself from the group",
    "she has lost interest in the project",
    "he is depressed since last month",
    "tone shows anger in the reply",
    "face shows deception when answering",
    "this pattern shows betrayal in their behaviour",
]


class TestCheckHumanClaim:
    def test_bm_third_person_assertions_hold_or_void(self) -> None:
        for phrase in BM_PHRASES:
            out = check_human_claim(phrase, subject_is_person=True)
            assert out["decision"] in ("HOLD", "VOID"), phrase
            assert out["hits"], phrase

    def test_en_third_person_assertions_hold_or_void(self) -> None:
        for phrase in EN_PHRASES:
            out = check_human_claim(phrase, subject_is_person=True)
            assert out["decision"] in ("HOLD", "VOID"), phrase
            assert out["hits"], phrase

    def test_betrayal_prediction_is_void(self) -> None:
        for phrase in (
            "corak ini menunjukkan pengkhianatan",
            "he will betray the team",
            "she is going to betray the group",
        ):
            out = check_human_claim(phrase, subject_is_person=True)
            assert out["decision"] == "VOID", phrase

    def test_honesty_scoring_is_void(self) -> None:
        for phrase in (
            "honesty score for PERSON_A is 0.4",
            "skor kejujuran PERSON_A: 0.6",
            "trust score of the person: 30%",
        ):
            out = check_human_claim(phrase, subject_is_person=True)
            assert out["decision"] == "VOID", phrase

    def test_first_person_self_report_allows(self) -> None:
        for phrase in ("aku penat hari ini, saya perlu rehat", "I am tired today"):
            out = check_human_claim(phrase, subject_is_person=True)
            assert out["decision"] == "ALLOW", phrase
            assert out["hits"] == [], phrase

    def test_observable_metric_allows(self) -> None:
        for phrase in (
            "message frequency fell from 12/wk to 3/wk",
            "kerapatan mesej jatuh dari 12/minggu ke 3/minggu",
        ):
            out = check_human_claim(phrase, subject_is_person=True)
            assert out["decision"] == "ALLOW", phrase
            assert out["hits"] == [], phrase

    def test_non_person_subject_never_gated(self) -> None:
        out = check_human_claim("dia sedang menjauh dari keluarganya", subject_is_person=False)
        assert out["decision"] == "ALLOW"
        assert out["hits"] == []

    def test_output_always_carries_known_limit(self) -> None:
        out = check_human_claim("aku penat", subject_is_person=True)
        assert "lexical gate" in out["known_limit"]


class TestTargetIsPerson:
    def test_person_markers_detected(self) -> None:
        for text in (
            "critique PERSON_A",
            "dia sedang menjauh dari keluarganya",
            "the woman in the chat",
            "he is distancing himself",
        ):
            assert target_is_person(text) is True, text

    def test_action_targets_not_person(self) -> None:
        for text in (
            "deploy pipeline to staging",
            "migrate the database",
            "ship release v1.2",
        ):
            assert target_is_person(text) is False, text


class TestHeartSchemaForPersonTarget:
    def test_person_schema_drops_sentiment_and_freezes_inner_state(self) -> None:
        schema = _schema_for_target("critique PERSON_A")
        props = schema["properties"]
        assert "sentiment" not in props
        assert props["inner_state"]["enum"] == ["UNKNOWN"]

    def test_action_schema_keeps_existing_sentiment_field(self) -> None:
        schema = _schema_for_target("deploy pipeline to staging")
        assert "sentiment" in schema["properties"]
        assert "inner_state" not in schema["properties"]


# ── heart.py end-to-end (LLM forced offline → deterministic fallback) ────────


class TestHeartPersonTargetGuard:
    @pytest.fixture(autouse=True)
    def _disable_remote_llm(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from unittest.mock import AsyncMock

        import arifosmcp.runtime.llm_client as llm_client

        for name in (
            "_call_fed_federation",
            "_call_tokenrouter",
            "_call_minimax",
            "_call_mimo",
            "_call_groq",
            "_call_gemini",
            "_call_cerebras",
            "_call_ollama",
        ):
            if hasattr(llm_client, name):
                monkeypatch.setattr(
                    llm_client,
                    name,
                    AsyncMock(side_effect=llm_client.LLMUnavailableError("offline-by-test")),
                )
        monkeypatch.setattr(llm_client, "ILMU_ENABLED", False)

    @pytest.mark.asyncio
    async def test_person_target_empathize_has_no_sentiment(self) -> None:
        from arifosmcp.tools.heart import arif_critique

        result = await arif_critique(
            mode="empathize",
            target="dia sedang menjauh dari keluarganya",
        )
        assert "sentiment" not in result
        assert result["inner_state"] == "UNKNOWN"
        assert result["inference_grammar"]["decision"] in ("HOLD", "VOID")
        # Tightening: prohibited inference about a person forces a HOLD advisory.
        assert result["status"] == "HOLD"
        assert result.get("human_decision_required") is True

    @pytest.mark.asyncio
    async def test_non_person_target_keeps_existing_behaviour(self) -> None:
        from arifosmcp.tools.heart import arif_critique

        result = await arif_critique(
            mode="empathize",
            target="deploy pipeline to staging",
        )
        assert "sentiment" in result  # existing behaviour preserved
        assert "inner_state" not in result
        assert "inference_grammar" not in result
        assert result["status"] == "OK"


if __name__ == "__main__":
    import unittest

    unittest.main()
