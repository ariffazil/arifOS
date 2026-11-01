"""arifosmcp/runtime/f6/inference_grammar.py — prohibited-inference lexical gate (G3).

HUMAN_RASA P0 remediation, gap G3. Two components:

(1) check_human_claim(text, subject_is_person) -> {decision, hits, ...}:
      HOLD — third-party inner-state assertion about a person (emotion / motive /
             intent / trust / deception / diagnosis / personality), English AND BM.
      VOID  — betrayal prediction or honesty/trust scoring (never emitted).
      ALLOW — first-person self-report ("aku penat"), observable metrics
             ("12/wk -> 3/wk"), and any non-person subject.
(2) target_is_person(text) — conservative person-marker probe; used by
    tools/heart.py so a person target never receives a `sentiment` field.

KNOWN LIMIT: lexical gate — will miss paraphrase. This is evidence for the
caller, never a semantic verdict: UNKNOWN inner state stays UNKNOWN.

Distinct from maruah_layer._m6_honesty (agent's OWN false inner states, L10);
this gate is about claims regarding a third-party HUMAN (F6).

Floors engaged: F6 · DITEMPA BUKAN DIBERI 🔥🌎🧠🪙
"""

from __future__ import annotations

import re
from typing import Any

SCHEMA = "arifos.f6.inference_grammar.v1"
KNOWN_LIMIT = "lexical gate, will miss paraphrase"

# claim_class constants
INNER_STATE = "INNER_STATE_ASSERTION"
BETRAYAL_PREDICTION = "BETRAYAL_PREDICTION"
HONESTY_SCORING = "HONESTY_SCORING"

# (pattern, language, claim_class) — third-person specific so self-reports
# ("saya kehilangan minat") do not trip the gate.
_PATTERNS: tuple[tuple[str, str, str], ...] = (
    # ── BM: the six required phrases + close variants ──
    ("dia sedang menjauh", "BM", INNER_STATE),
    ("beliau sedang menjauh", "BM", INNER_STATE),
    ("dia kehilangan minat", "BM", INNER_STATE),
    ("beliau kehilangan minat", "BM", INNER_STATE),
    ("dia tertekan", "BM", INNER_STATE),
    ("beliau tertekan", "BM", INNER_STATE),
    ("nada menunjukkan marah", "BM", INNER_STATE),
    ("nada suara menunjukkan", "BM", INNER_STATE),
    ("wajah menunjukkan penipuan", "BM", INNER_STATE),
    ("corak ini menunjukkan pengkhianatan", "BM", BETRAYAL_PREDICTION),
    # ── BM extras: motive/intent/trust/deception/personality assertions ──
    ("dia pembohong", "BM", INNER_STATE),
    ("dia menipu", "BM", INNER_STATE),
    ("dia manipulatif", "BM", INNER_STATE),
    ("dia sengaja menipu", "BM", INNER_STATE),
    # ── BM: betrayal prediction + honesty scoring → VOID ──
    ("akan mengkhianati", "BM", BETRAYAL_PREDICTION),
    ("akan mengkhianat", "BM", BETRAYAL_PREDICTION),
    ("pengkhianatan", "BM", BETRAYAL_PREDICTION),
    ("pengkhianat", "BM", BETRAYAL_PREDICTION),
    ("skor kejujuran", "BM", HONESTY_SCORING),
    ("score kejujuran", "BM", HONESTY_SCORING),
    ("skor kepercayaan", "BM", HONESTY_SCORING),
    # ── EN: English equivalents of the six required phrases ──
    ("he is distancing", "EN", INNER_STATE),
    ("she is distancing", "EN", INNER_STATE),
    ("he has lost interest", "EN", INNER_STATE),
    ("she has lost interest", "EN", INNER_STATE),
    ("he is depressed", "EN", INNER_STATE),
    ("she is depressed", "EN", INNER_STATE),
    ("tone shows anger", "EN", INNER_STATE),
    ("tone indicates anger", "EN", INNER_STATE),
    ("face shows deception", "EN", INNER_STATE),
    ("face shows fraud", "EN", INNER_STATE),
    ("this pattern shows betrayal", "EN", BETRAYAL_PREDICTION),
    ("the pattern shows betrayal", "EN", BETRAYAL_PREDICTION),
    # ── EN extras: motive/intent/trust/deception/personality assertions ──
    ("he is lying", "EN", INNER_STATE),
    ("she is lying", "EN", INNER_STATE),
    ("he is manipulative", "EN", INNER_STATE),
    ("she is manipulative", "EN", INNER_STATE),
    ("he is narcissistic", "EN", INNER_STATE),
    ("she is narcissistic", "EN", INNER_STATE),
    ("he suffers from", "EN", INNER_STATE),
    ("she suffers from", "EN", INNER_STATE),
    # ── EN: betrayal prediction + honesty scoring → VOID ──
    ("will betray", "EN", BETRAYAL_PREDICTION),
    ("going to betray", "EN", BETRAYAL_PREDICTION),
    ("betrays the", "EN", BETRAYAL_PREDICTION),
    ("betrayal prediction", "EN", BETRAYAL_PREDICTION),
    ("honesty score", "EN", HONESTY_SCORING),
    ("honesty_score", "EN", HONESTY_SCORING),
    ("trust score", "EN", HONESTY_SCORING),
    ("trustworthiness score", "EN", HONESTY_SCORING),
    ("integrity score", "EN", HONESTY_SCORING),
)

_VOID_CLASSES = {BETRAYAL_PREDICTION, HONESTY_SCORING}

# Person markers for heart's target probe — word-boundary regex so "the
# service" never matches "he".
_PERSON_RE = re.compile(
    r"(\bperson_[a-z]\b|\bdia\b|\bbeliau\b|\borang ini\b|\bindividu\b"
    r"|\bhe\b|\bshe\b|\bhimself\b|\bherself\b"
    r"|\blelaki\b|\bperempuan\b|\bwanita\b"
    r"|\bthe (man|woman|person|individual)\b)",
    re.IGNORECASE,
)
_FIRST_PERSON_RE = re.compile(r"\b(aku|saya)\b|\bI am\b|\bI'm\b|\bmyself\b", re.IGNORECASE)
_METRIC_RE = re.compile(
    r"\b\d+(\.\d+)?\s*/\s*(wk|week|minggu|day|days|hari|hr|hour|jam)\b"
    r"|\b\d+(\.\d+)?\s*%\b"
    r"|\bfrom \d+(\.\d+)? to \d+(\.\d+)?\b",
    re.IGNORECASE,
)


def target_is_person(text: str) -> bool:
    """Conservative probe: does this target name/reference a human person?"""
    return bool(_PERSON_RE.search(text or ""))


def check_human_claim(text: str, subject_is_person: bool) -> dict[str, Any]:
    """Lexical gate over a claim about a (possibly) human subject.

    Returns {"schema", "decision": ALLOW|HOLD|VOID", "hits": [...],
    "subject_is_person", "first_person_self_report", "observable_metric",
    "known_limit"}. Precedence: VOID > HOLD > ALLOW. Fail-closed on the
    person axis: any hit about a third party is at least HOLD.
    """
    text = text or ""
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "decision": "ALLOW",
        "hits": [],
        "subject_is_person": bool(subject_is_person),
        "first_person_self_report": bool(_FIRST_PERSON_RE.search(text)),
        "observable_metric": bool(_METRIC_RE.search(text)),
        "known_limit": KNOWN_LIMIT,
    }
    if not subject_is_person:
        out["note"] = "subject_is_person=False — no human inner-state claim in scope"
        return out

    for pattern, language, claim_class in _PATTERNS:
        if pattern in text.lower():
            out["hits"].append(
                {
                    "pattern": pattern,
                    "language": language,
                    "claim_class": claim_class,
                }
            )

    if any(h["claim_class"] in _VOID_CLASSES for h in out["hits"]):
        out["decision"] = "VOID"
    elif out["hits"]:
        out["decision"] = "HOLD"
    else:
        out["decision"] = "ALLOW"
        if out["first_person_self_report"]:
            out["note"] = "first-person self-report — ALLOW"
        elif out["observable_metric"]:
            out["note"] = "observable metric only — ALLOW"
    return out
