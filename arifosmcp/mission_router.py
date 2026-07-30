"""
arifOS Mission Router — The Nervous System

DITEMPA BUKAN DIBERI — Forged 2026-07-30 under F13 directive.
"You should not use the tools. The agents should."

This module is the bridge between human language and silent organ orchestration.
It takes Arif's natural language intent, classifies it into one of six missions,
selects the organ pipeline, and returns a MissionPlan.

When the arif_route bridge is implemented (mode=bridge), the plan executes
automatically. Until then, it serves as the classification and blueprint layer.

Architecture:
    INTENT (natural language)
        ↓
    classify_mission() → mission + confidence
        ↓
    build_pipeline()  → organ chain + tool selection rules
        ↓
    MissionPlan       → what to execute, how to format output, autonomy level
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# MISSION DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════


class Mission(Enum):
    INVESTIGATE = "investigate"
    INTERPRET = "interpret"
    DECIDE = "decide"
    BUILD = "build"
    MONITOR = "monitor"
    REMEMBER = "remember"


@dataclass
class OrganStage:
    """One stage in a mission pipeline — organ + capability + tool hints."""

    organ: str
    capability: str  # e.g. "observe", "query", "interpret", "judge"
    stage: int  # execution order
    tools_hint: list[str] = field(default_factory=list)  # suggested tools (router selects)
    can_parallel: bool = False  # can run concurrently with previous stage


@dataclass
class MissionPlan:
    """The complete execution plan for one mission."""

    mission: Mission
    confidence: float  # classifier confidence [0-1]
    human_label: str  # what to tell Arif (e.g. "Investigating — gathering evidence")
    organ_pipeline: list[OrganStage]
    output_format: str  # what Arif receives
    autonomy: str  # AUTO_DO, ASK, or AUTO_DO_SILENT
    matched_triggers: list[str]  # which trigger words matched
    classified_by: str = "keyword_router_v1"  # upgrade path to ML classifier


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL MISSION TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

MISSION_TEMPLATES: dict[Mission, dict[str, Any]] = {
    Mission.INVESTIGATE: {
        "label": "Investigate — Gather and test reality",
        "trigger_words": [
            "what is",
            "what's happening",
            "what are",
            "check",
            "status",
            "gather",
            "find",
            "scan",
            "search",
            "probe",
            "observe",
            "discover",
            "measure",
            "show me",
            "current state",
            "fetch",
            "ingest",
            "load data",
            "is this valid",
            "validate",
            "verify data",
            "what exists",
            "inspect",
            "examine",
            "look at",
            "review status",
            "what changed",
            "any changes",
            "delta",
            "diff",
        ],
        "negative_triggers": [
            "why",
            "should we",
            "decide",
            "deploy",
            "execute",
            "build",
            "remember",
            "recall",
            "what did we decide",
        ],
        "pipeline": [
            OrganStage("arifOS", "observe", 1, tools_hint=["arif_observe"], can_parallel=False),
            OrganStage(
                "GEOX",
                "query",
                2,
                tools_hint=["geox_basin", "geox_surface_status"],
                can_parallel=True,
            ),
            OrganStage(
                "WEALTH",
                "query",
                2,
                tools_hint=["capital_market", "capital_health"],
                can_parallel=True,
            ),
            OrganStage(
                "WELL",
                "sense",
                2,
                tools_hint=["well_machine_diagnose", "well_classify_substrate"],
                can_parallel=True,
            ),
            OrganStage(
                "A-FORGE",
                "status",
                2,
                tools_hint=["forge_probe", "forge_health_check"],
                can_parallel=True,
            ),
            OrganStage("arifOS", "synthesize", 3, tools_hint=["arif_think"], can_parallel=False),
        ],
        "output": "Structured evidence bundle with epistemic tags and confidence bands.",
        "autonomy": "AUTO_DO",
    },
    Mission.INTERPRET: {
        "label": "Interpret — Build competing explanations",
        "trigger_words": [
            "why",
            "explain",
            "interpret",
            "what caused",
            "what does this mean",
            "analyze",
            "hypothesize",
            "what if",
            "competing",
            "alternative",
            "possible reason",
            "root cause",
            "what led to",
            "correlate",
            "synthesize",
            "reason about",
            "model this",
            "simulate",
            "assess this",
            "evaluate this prospect",
            "evaluate this basin",
        ],
        "negative_triggers": [
            "should we",
            "decide",
            "deploy",
            "execute",
            "build",
            "remember",
            "recall",
            "what did we decide",
        ],
        "pipeline": [
            OrganStage("arifOS", "think", 1, tools_hint=["arif_think"], can_parallel=False),
            OrganStage(
                "GEOX",
                "interpret",
                2,
                tools_hint=[
                    "geox_contradiction_scan",
                    "geox_falsify",
                    "geox_petrophysics",
                    "geox_geological_model_generate",
                ],
                can_parallel=True,
            ),
            OrganStage(
                "WEALTH",
                "diagnose",
                2,
                tools_hint=["capital_diagnose", "capital_entropy"],
                can_parallel=True,
            ),
            OrganStage(
                "WELL", "reflect", 2, tools_hint=["well_assess_homeostasis"], can_parallel=True
            ),
            OrganStage("arifOS", "synthesize", 3, tools_hint=["arif_think"], can_parallel=False),
        ],
        "output": "Ranked hypotheses with evidence support, contradictions surfaced, uncertainty explicit.",
        "autonomy": "AUTO_DO",
    },
    Mission.DECIDE: {
        "label": "Decide — Compare consequences and uncertainty",
        "trigger_words": [
            "should we",
            "decide",
            "choose",
            "compare",
            "option",
            "what happens if",
            "consequence",
            "risk",
            "reward",
            "worth",
            "viable",
            "drill",
            "invest",
            "allocate",
            "approve",
            "reject",
            "recommend",
            "safest path",
            "best option",
            "decision",
            "go or no-go",
            "advance or hold",
            "what's the call",
            "prospect evaluation",
            "should we drill",
            "economic",
        ],
        "negative_triggers": ["deploy", "execute", "build now", "memory", "recall"],
        "pipeline": [
            OrganStage(
                "arifOS",
                "think",
                1,
                tools_hint=["arif_think(mode=plan,critique)"],
                can_parallel=False,
            ),
            OrganStage(
                "GEOX",
                "consequence",
                2,
                tools_hint=["geox_prospect", "geox_falsify"],
                can_parallel=True,
            ),
            OrganStage(
                "WEALTH",
                "consequence",
                2,
                tools_hint=[
                    "capital_primitive(emv,npv)",
                    "capital_wisdom",
                    "capital_entropy",
                    "wealth_institutional_stress_index",
                ],
                can_parallel=True,
            ),
            OrganStage(
                "WELL",
                "readiness",
                2,
                tools_hint=["well_validate_vitality", "well_assess_homeostasis"],
                can_parallel=True,
            ),
            OrganStage("arifOS", "judge", 3, tools_hint=["arif_judge"], can_parallel=False),
            OrganStage(
                "arifOS",
                "seal_prepare",
                4,
                tools_hint=["arif_seal(mode=prepare)"],
                can_parallel=False,
            ),
        ],
        "output": "Single recommendation with: kill criteria, confidence, reversibility, what would change the decision.",
        "autonomy": "ASK",
    },
    Mission.BUILD: {
        "label": "Build — Prepare and execute approved changes",
        "trigger_words": [
            "deploy",
            "execute",
            "build",
            "make the change",
            "run",
            "commit",
            "push",
            "install",
            "create",
            "forge",
            "mutate",
            "apply",
            "implement",
            "ship",
            "release",
            "do it",
        ],
        "negative_triggers": ["why", "what if", "should we", "decide", "remember"],
        "pipeline": [
            OrganStage(
                "arifOS", "validate_authority", 1, tools_hint=["arif_init"], can_parallel=False
            ),
            OrganStage("A-FORGE", "plan", 2, tools_hint=["forge_session_init"], can_parallel=False),
            OrganStage(
                "A-FORGE",
                "dry_run",
                3,
                tools_hint=["forge_shell_dryrun", "forge_sandbox_run"],
                can_parallel=False,
            ),
            OrganStage(
                "arifOS", "seal", 4, tools_hint=["arif_seal", "arif_judge"], can_parallel=False
            ),
            OrganStage(
                "A-FORGE",
                "execute",
                5,
                tools_hint=["forge_execute", "forge_shell"],
                can_parallel=False,
            ),
            OrganStage("arifOS", "record", 6, tools_hint=["arif_seal"], can_parallel=False),
        ],
        "output": "Execution receipt with rollback path, before/after hashes, and immutable seal.",
        "autonomy": "ASK",
    },
    Mission.MONITOR: {
        "label": "Monitor — Detect change, degradation, or danger",
        "trigger_words": [
            "watch",
            "monitor",
            "alert",
            "tell me if",
            "notify",
            "is everything healthy",
            "what degraded",
            "any anomalies",
            "health check",
            "status check",
            "keep an eye on",
            "warn me",
            "track",
            "surveillance",
        ],
        "negative_triggers": ["why", "should we", "decide", "deploy", "build"],
        "pipeline": [
            OrganStage(
                "arifOS",
                "observe_continuous",
                1,
                tools_hint=["arif_observe(mode=vitals)"],
                can_parallel=False,
            ),
            OrganStage(
                "WELL",
                "machine_health",
                2,
                tools_hint=["well_machine_diagnose", "well_assess_reliability"],
                can_parallel=True,
            ),
            OrganStage(
                "WEALTH",
                "market_health",
                2,
                tools_hint=["capital_health", "capital_market"],
                can_parallel=True,
            ),
            OrganStage(
                "GEOX", "data_freshness", 2, tools_hint=["geox_surface_status"], can_parallel=True
            ),
            OrganStage(
                "arifOS",
                "delta_report",
                3,
                tools_hint=["arif_observe(mode=entropy_dS)"],
                can_parallel=False,
            ),
        ],
        "output": "Delta report: what changed, what degraded, what needs attention. Silent when all healthy.",
        "autonomy": "AUTO_DO_SILENT",
    },
    Mission.REMEMBER: {
        "label": "Remember — Retrieve and preserve governed knowledge",
        "trigger_words": [
            "remember",
            "recall",
            "what did we decide",
            "what do we know",
            "memory",
            "history",
            "past",
            "previous",
            "prior",
            "preserve",
            "seal this",
            "archive",
            "ledger",
            "record",
            "find everything about",
            "what happened during",
            "show me the evidence for",
        ],
        "negative_triggers": ["deploy", "execute", "build", "should we", "decide"],
        "pipeline": [
            OrganStage(
                "arifOS",
                "memory_recall",
                1,
                tools_hint=["arif_memory(recall,inspect)"],
                can_parallel=False,
            ),
            OrganStage(
                "arifOS",
                "verify_chain",
                2,
                tools_hint=["arif_seal(mode=verify,ledger)"],
                can_parallel=False,
            ),
            OrganStage(
                "arifOS",
                "memory_store",
                3,
                tools_hint=["arif_memory(remember,promote)"],
                can_parallel=False,
            ),
        ],
        "output": "Retrieved knowledge with provenance chain and seal verification.",
        "autonomy": "AUTO_DO",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# MISSION CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════


def _score_mission(intent_lower: str, mission: Mission) -> tuple[int, int, list[str]]:
    """Score an intent against a mission's trigger words.

    Returns (positive_score, negative_score, matched_triggers).
    Higher positive = better match. Any negative hit = disqualified.
    """
    template = MISSION_TEMPLATES[mission]
    positive = 0
    negative = 0
    matched: list[str] = []

    for word in template["trigger_words"]:
        if word in intent_lower:
            positive += 1
            matched.append(word)

    for word in template["negative_triggers"]:
        if word in intent_lower:
            negative += 1

    # Short intents: fewer words = each match counts more
    word_count = max(len(intent_lower.split()), 1)
    if word_count <= 3:
        positive *= 2  # short, direct commands get amplified signal

    return positive, negative, matched


def plan_from_mission_id(mission_id: str) -> MissionPlan:
    """Build a MissionPlan from an explicit mission_id (human cockpit binding).

    Bypasses keyword classification — sovereign or agent already chose the mission.
    Invalid IDs raise ValueError (caller converts to HOLD).
    """
    mid = (mission_id or "").strip().lower()
    try:
        mission = Mission(mid)
    except ValueError as e:
        valid = ", ".join(m.value for m in Mission)
        raise ValueError(f"unknown mission_id '{mission_id}'. Valid: {valid}") from e
    template = MISSION_TEMPLATES[mission]
    return MissionPlan(
        mission=mission,
        confidence=1.0,
        human_label=template["label"],
        organ_pipeline=list(template["pipeline"]),
        output_format=template["output"],
        autonomy=template["autonomy"],
        matched_triggers=[f"mission_id={mission.value}"],
        classified_by="mission_id_binding_v1",
    )


def plan_to_dict(plan: MissionPlan) -> dict[str, Any]:
    """Serialize MissionPlan for MCP JSON envelopes (no tool inventory dump)."""
    return {
        "mission_id": plan.mission.value,
        "confidence": plan.confidence,
        "human_label": plan.human_label,
        "autonomy": plan.autonomy,
        "output_format": plan.output_format,
        "classified_by": plan.classified_by,
        "matched_triggers": plan.matched_triggers,
        "pipeline": [
            {
                "stage": s.stage,
                "organ": s.organ,
                "capability": s.capability,
                "tools_hint": s.tools_hint,  # engine-room only; not for human display
                "can_parallel": s.can_parallel,
            }
            for s in plan.organ_pipeline
        ],
        "primary_organ": plan.organ_pipeline[0].organ if plan.organ_pipeline else "arifOS",
        # Cockpit contract — what Arif sees
        "human_facing": format_for_arif(plan, results=None),
        "web_zen": {
            "cli": "/root/arif-fazil.com/scripts/web-zen/web_zen.py",
            "doctor": "python3 /root/arif-fazil.com/scripts/web-zen/web_zen.py doctor",
            "when": "site / deploy / missions / vitals / caddy / SPA work",
        },
    }


def classify_mission(intent: str) -> MissionPlan:
    """Classify natural language intent into the closest mission.

    Args:
        intent: Natural language from Arif, e.g. "Assess this prospect
                and tell me what could destroy the case."

    Returns:
        MissionPlan with classified mission, confidence, pipeline, and output format.
    """
    intent_lower = intent.lower().strip()

    # Score every mission
    scores: dict[Mission, tuple[int, int, list[str]]] = {}
    for mission in Mission:
        scores[mission] = _score_mission(intent_lower, mission)

    # Filter out missions with negative hits (disqualified)
    eligible = {
        m: s
        for m, s in scores.items()
        if s[1] == 0  # no negative triggers matched
    }

    if not eligible:
        # All missions disqualified by negative triggers — default to INVESTIGATE
        best_mission = Mission.INVESTIGATE
        positive, _, matched = scores[best_mission]
        confidence = 0.3  # low confidence — fallback
    else:
        # Pick mission with highest positive score
        best_mission = max(eligible, key=lambda m: eligible[m][0])
        positive, _, matched = eligible[best_mission]

        # Confidence: ratio of best score to total signal
        total_positive = sum(s[0] for s in eligible.values())
        confidence = min(positive / max(total_positive, 1), 0.95)

    # If zero matches, default to INVESTIGATE with low confidence
    if positive == 0:
        best_mission = Mission.INVESTIGATE
        confidence = 0.15
        matched = ["(no keyword match — defaulting to investigate)"]

    template = MISSION_TEMPLATES[best_mission]

    return MissionPlan(
        mission=best_mission,
        confidence=round(confidence, 2),
        human_label=template["label"],
        organ_pipeline=template["pipeline"],
        output_format=template["output"],
        autonomy=template["autonomy"],
        matched_triggers=matched,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════


def format_for_arif(plan: MissionPlan, results: dict[str, Any] | None = None) -> str:
    """Format mission results into the Arif-facing output contract.

    What Arif ALWAYS sees:
    - The recommendation (one clear statement)
    - The confidence level
    - What would change the recommendation
    - Whether any irreversible action was taken
    - Evidence trail available on request

    What Arif NEVER sees:
    - Tool names, organ names, tool counts, registry classifications
    """
    lines = []

    if results is None:
        # Pre-execution: show the plan classification
        lines.append(f"**Mission:** {plan.human_label}")
        lines.append(f"**Confidence in classification:** {plan.confidence:.0%}")
        lines.append(f"**Autonomy:** {plan.autonomy}")
        lines.append(f"**Pipeline stages:** {len(plan.organ_pipeline)}")
        lines.append("")
        lines.append("_No tools will be shown. The federation handles them silently._")
        return "\n".join(lines)

    # Post-execution: show the results in Arif-friendly format
    verdict = results.get("verdict", results.get("recommendation", "INCONCLUSIVE"))
    confidence = results.get("confidence", 0.5)
    reason = results.get("reason", results.get("main_reason", "Insufficient evidence"))
    change_condition = results.get(
        "what_would_change", results.get("kill_criteria", "Additional evidence required")
    )
    irreversible = results.get("irreversible_action", "None")
    evidence_hash = results.get("evidence_hash", results.get("receipt", "Not sealed"))

    lines.append(f"**{verdict}**")
    lines.append("")
    lines.append(f"**Main reason:** {reason}")
    lines.append(
        f"**Confidence:** {confidence:.0%}"
        if isinstance(confidence, float)
        else f"**Confidence:** {confidence}"
    )
    lines.append(f"**What would change the decision:** {change_condition}")
    lines.append(f"**Irreversible action:** {irreversible}")
    lines.append("")
    lines.append(f"_Evidence trail: `{evidence_hash}`_")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-TEST (run with: python -m arifosmcp.mission_router)
# ═══════════════════════════════════════════════════════════════════════════════

TEST_CASES = [
    ("Assess this prospect and tell me what could destroy the case.", Mission.DECIDE),
    ("What's happening with the VPS?", Mission.INVESTIGATE),
    ("Why did the well test fail?", Mission.INTERPRET),
    ("Should we drill prospect Alpha?", Mission.DECIDE),
    ("Deploy the fix for the auth bug.", Mission.BUILD),
    ("Watch the CPU and alert me if it exceeds 90%.", Mission.MONITOR),
    ("What did we decide about the Malay Basin prospect?", Mission.REMEMBER),
    ("Check the health of everything.", Mission.MONITOR),
    ("Find all evidence about reservoir quality in well X.", Mission.INVESTIGATE),
    ("Give me competing explanations for the AVO anomaly.", Mission.INTERPRET),
    ("Is this investment worth the risk?", Mission.DECIDE),
    ("Execute the approved deployment plan.", Mission.BUILD),
    ("Show me the current state of all organs.", Mission.INVESTIGATE),
    ("What happened during the July 29 session?", Mission.REMEMBER),
]


def run_tests() -> dict[str, Any]:
    """Run the classifier against test cases. Returns accuracy report."""
    results = {"total": len(TEST_CASES), "correct": 0, "wrong": 0, "details": []}

    for intent, expected in TEST_CASES:
        plan = classify_mission(intent)
        correct = plan.mission == expected
        if correct:
            results["correct"] += 1
        else:
            results["wrong"] += 1

        results["details"].append(
            {
                "intent": intent,
                "expected": expected.value,
                "classified": plan.mission.value,
                "correct": correct,
                "confidence": plan.confidence,
                "triggers": plan.matched_triggers,
            }
        )

    results["accuracy"] = round(results["correct"] / results["total"], 2)
    return results


if __name__ == "__main__":
    import json

    report = run_tests()
    print(f"Accuracy: {report['accuracy']:.0%} ({report['correct']}/{report['total']})")
    print()
    for d in report["details"]:
        status = "✅" if d["correct"] else "❌"
        print(f"{status} [{d['classified']}] confidence={d['confidence']:.0%}")
        print(f"   Intent: {d['intent'][:80]}")
        print(f"   Triggers: {d['triggers']}")
        print()
