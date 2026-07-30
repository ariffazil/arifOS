"""
arifOS Mission Router — Deterministic Core (Phase 1)

DITEMPA BUKAN DIBERI — Forged 2026-07-30

Zero model dependency. Registry-backed. Dry-run only.

Architecture:
    intent → classify_mission() → mission
    mission → resolve_capabilities() → capability list
    capabilities → resolve_tools() → tool list (from live registry spine)
    tools → build_graph() → execution graph
    graph → validate() → READY_FOR_DRY_RUN | HOLD

Never: declare verdict, grant authority, bypass evidence, execute mutation, seal.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# DATA TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class RouterVerdict(Enum):
    READY = "READY_FOR_DRY_RUN"
    HOLD_EVIDENCE = "HOLD_FOR_EVIDENCE"
    HOLD_CAPABILITY = "HOLD_FOR_CAPABILITY"
    HOLD_INTENT = "HOLD_FOR_INTENT"
    REJECTED = "REJECTED"


class Mission(Enum):
    OBSERVE = "OBSERVE"  # What is happening?
    EXPLAIN = "EXPLAIN"  # Why did this happen?
    DECIDE = "DECIDE"  # Should we do X?
    ACT = "ACT"  # Execute the plan
    MONITOR = "MONITOR"  # Watch this for me
    RECALL = "RECALL"  # What did we decide?


@dataclass
class CapabilityRef:
    """A capability requirement from the mission template."""

    organ: str
    capability: str  # e.g. "observe", "query", "interpret"
    stage: int


@dataclass
class ResolvedTool:
    """A capability resolved to an actual callable tool from the registry spine."""

    capability_ref: CapabilityRef
    tool_name: str
    tool_class: str  # PUBLIC_CANONICAL, INTERNAL_CALLABLE, etc.
    tool_desc: str
    organ: str
    selection_reason: str


@dataclass
class PipelineStage:
    """One stage in the execution graph."""

    stage: int
    organ: str
    tools: list[ResolvedTool]
    can_parallel: bool
    mutation: bool


@dataclass
class RouterResult:
    """Complete router output."""

    verdict: RouterVerdict
    mission: Mission | None
    risk_class: str
    pipeline: list[PipelineStage]
    mutation_allowed: bool
    missing_evidence: list[str]
    warnings: list[str]
    errors: list[str]
    graph_hash: str
    generated_at: str


# ═══════════════════════════════════════════════════════════════════════════════
# MISSION CLASSIFIER (deterministic keyword-based, no model)
# ═══════════════════════════════════════════════════════════════════════════════

MISSION_TRIGGERS: dict[Mission, dict[str, Any]] = {
    Mission.OBSERVE: {
        "positive": [
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
            "show me",
            "current state",
            "fetch",
            "inspect",
            "examine",
            "look at",
            "review status",
            "what changed",
            "any changes",
            "delta",
            "diff",
            "validate",
            "verify data",
            "health",
            "measure",
        ],
        "negative": [
            "why",
            "should we",
            "decide",
            "deploy",
            "execute",
            "build",
            "remember",
            "recall",
            "what did we decide",
            "explain",
            "cause",
        ],
    },
    Mission.EXPLAIN: {
        "positive": [
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
        "negative": [
            "should we",
            "decide",
            "deploy",
            "execute",
            "build",
            "remember",
            "recall",
            "what did we decide",
        ],
    },
    Mission.DECIDE: {
        "positive": [
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
        "negative": ["deploy", "execute", "build now", "memory", "recall"],
    },
    Mission.ACT: {
        "positive": [
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
        "negative": ["why", "what if", "should we", "decide", "remember"],
    },
    Mission.MONITOR: {
        "positive": [
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
        "negative": ["why", "should we", "decide", "deploy", "build"],
    },
    Mission.RECALL: {
        "positive": [
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
        "negative": ["deploy", "execute", "build", "should we", "decide"],
    },
}


def classify_intent(intent: str) -> tuple[Mission, float, list[str]]:
    """Classify natural language intent into a mission.

    Returns (mission, confidence, matched_triggers).
    Pure keyword matching. No model. Deterministic.
    """
    intent_lower = intent.lower().strip()
    scores: dict[Mission, tuple[int, int, list[str]]] = {}

    for mission, triggers in MISSION_TRIGGERS.items():
        positive = 0
        negative = 0
        matched: list[str] = []

        for word in triggers["positive"]:
            if word in intent_lower:
                positive += 1
                matched.append(word)

        for word in triggers["negative"]:
            if word in intent_lower:
                negative += 1

        scores[mission] = (positive, negative, matched)

    # Filter disqualified missions
    eligible = {m: s for m, s in scores.items() if s[1] == 0}

    if not eligible:
        best = Mission.OBSERVE
        positive, _, matched = scores[best]
        confidence = 0.15
    else:
        best = max(eligible, key=lambda m: eligible[m][0])
        positive, _, matched = eligible[best]
        total = sum(s[0] for s in eligible.values())
        confidence = min(positive / max(total, 1), 0.95) if total > 0 else 0.15

    if positive == 0:
        best = Mission.OBSERVE
        confidence = 0.10
        matched = ["(fallback — no keyword match)"]

    return best, round(confidence, 2), matched


# ═══════════════════════════════════════════════════════════════════════════════
# CAPABILITY → TOOL RESOLVER
# ═══════════════════════════════════════════════════════════════════════════════

# Maps mission template capability references to tool selection rules.
# "organ:capability" → how to find tools in the spine.
CAPABILITY_TOOL_MAP: dict[str, dict[str, Any]] = {
    # arifOS capabilities
    "arifOS:observe": {
        "tool_names": ["arif_observe"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:think": {
        "tool_names": ["arif_think"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:synthesize": {
        "tool_names": ["arif_think"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:judge": {
        "tool_names": ["arif_judge"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:seal_prepare": {
        "tool_names": ["arif_seal"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:seal": {
        "tool_names": ["arif_seal"],
        "organ": "arifOS",
        "mutation": True,
        "can_parallel": False,
    },
    "arifOS:validate_authority": {
        "tool_names": ["arif_init"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:observe_continuous": {
        "tool_names": ["arif_observe"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:delta_report": {
        "tool_names": ["arif_observe"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:memory_recall": {
        "tool_names": ["arif_memory"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:verify_chain": {
        "tool_names": ["arif_seal"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    "arifOS:memory_store": {
        "tool_names": ["arif_memory"],
        "organ": "arifOS",
        "mutation": False,
        "can_parallel": False,
    },
    # GEOX capabilities
    "GEOX:query": {
        "tool_names": [
            "geox_basin",
            "geox_well_ingest",
            "geox_well_view",
            "geox_deep_time_state",
            "geox_stac_discover",
        ],
        "organ": "GEOX",
        "mutation": False,
        "can_parallel": True,
    },
    "GEOX:interpret": {
        "tool_names": [
            "geox_contradiction_scan",
            "geox_falsify",
            "geox_petrophysics",
            "geox_geological_model_generate",
            "geox_sequence",
            "geox_dde_reason",
            "geox_thermal_maturity_history",
        ],
        "organ": "GEOX",
        "mutation": False,
        "can_parallel": True,
    },
    "GEOX:consequence": {
        "tool_names": ["geox_prospect", "geox_falsify", "geox_petrophysics"],
        "organ": "GEOX",
        "mutation": False,
        "can_parallel": True,
    },
    "GEOX:data_freshness": {
        "tool_names": ["geox_surface_status"],
        "organ": "GEOX",
        "mutation": False,
        "can_parallel": True,
    },
    # WEALTH capabilities
    "WEALTH:query": {
        "tool_names": ["wealth_reality_intake_loop", "capital_market", "capital_health"],
        "organ": "WEALTH",
        "mutation": False,
        "can_parallel": True,
    },
    "WEALTH:diagnose": {
        "tool_names": ["capital_diagnose", "capital_entropy"],
        "organ": "WEALTH",
        "mutation": False,
        "can_parallel": True,
    },
    "WEALTH:consequence": {
        "tool_names": [
            "capital_primitive",
            "capital_wisdom",
            "capital_entropy",
            "wealth_institutional_stress_index",
            "wealth_cascade_model",
        ],
        "organ": "WEALTH",
        "mutation": False,
        "can_parallel": True,
    },
    "WEALTH:market_health": {
        "tool_names": ["capital_health", "capital_market"],
        "organ": "WEALTH",
        "mutation": False,
        "can_parallel": True,
    },
    # WELL capabilities
    "WELL:sense": {
        "tool_names": ["well_machine_diagnose", "well_classify_substrate", "well_trace_lineage"],
        "organ": "WELL",
        "mutation": False,
        "can_parallel": True,
    },
    "WELL:reflect": {
        "tool_names": ["well_assess_homeostasis"],
        "organ": "WELL",
        "mutation": False,
        "can_parallel": True,
    },
    "WELL:readiness": {
        "tool_names": ["well_validate_vitality", "well_assess_homeostasis"],
        "organ": "WELL",
        "mutation": False,
        "can_parallel": True,
    },
    "WELL:machine_health": {
        "tool_names": ["well_machine_diagnose", "well_assess_reliability"],
        "organ": "WELL",
        "mutation": False,
        "can_parallel": True,
    },
    # A-FORGE capabilities
    "A-FORGE:status": {
        "tool_names": ["forge_probe", "forge_health_check"],
        "organ": "A-FORGE",
        "mutation": False,
        "can_parallel": True,
    },
    "A-FORGE:plan": {
        "tool_names": ["forge_session_init"],
        "organ": "A-FORGE",
        "mutation": False,
        "can_parallel": False,
    },
    "A-FORGE:dry_run": {
        "tool_names": ["forge_shell_dryrun", "forge_sandbox_run"],
        "organ": "A-FORGE",
        "mutation": False,
        "can_parallel": False,
    },
    "A-FORGE:execute": {
        "tool_names": ["forge_execute", "forge_shell"],
        "organ": "A-FORGE",
        "mutation": True,
        "can_parallel": False,
    },
    # VAULT999
    "VAULT999:record": {
        "tool_names": ["arif_seal"],
        "organ": "arifOS",
        "mutation": True,
        "can_parallel": False,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY SPINE LOADER
# ═══════════════════════════════════════════════════════════════════════════════


def load_registry_spine(path: str | None = None) -> dict[str, Any]:
    """Load the federation registry spine. Uses canonical contract path by default."""
    if path is None:
        path = "/root/AAA/contracts/federation-registry-spine.json"
    with open(path) as f:
        return json.load(f)


def load_mission_templates(path: str | None = None) -> dict[str, Any]:
    """Load the mission templates."""
    if path is None:
        path = "/root/AAA/contracts/mission-templates.json"
    with open(path) as f:
        return json.load(f)


def get_callable_tools(spine: dict, organ: str) -> dict[str, dict]:
    """Extract callable tools from the registry spine for a given organ.

    Returns {tool_name: {class, desc, organ}} for PUBLIC_CANONICAL tools only.
    Rejects INTERNAL_CALLABLE, DEPRECATED, DEV_ONLY, SDK_ALIAS.
    """
    organs = spine.get("organs", {})
    organ_data = organs.get(organ, {})
    tools_by_class = organ_data.get("tools", {})

    callable_tools: dict[str, dict] = {}

    # Only PUBLIC_CANONICAL tools are callable by the router
    for tool in tools_by_class.get("PUBLIC_CANONICAL", []):
        name = tool.get("name", "")
        if name:
            callable_tools[name] = {
                "class": "PUBLIC_CANONICAL",
                "desc": tool.get("desc", ""),
                "organ": organ,
            }

    return callable_tools


def get_all_callable(spine: dict) -> dict[str, dict[str, dict]]:
    """Get all callable tools across all organs. Returns {organ: {tool_name: info}}."""
    result: dict[str, dict[str, dict]] = {}
    for organ in spine.get("organs", {}):
        result[organ] = get_callable_tools(spine, organ)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# MISSION PIPELINE BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

MISSION_PIPELINES: dict[Mission, list[str]] = {
    Mission.OBSERVE: [
        "arifOS:observe",
        "GEOX:query",
        "WEALTH:query",
        "WELL:sense",
        "A-FORGE:status",
        "arifOS:synthesize",
    ],
    Mission.EXPLAIN: [
        "arifOS:think",
        "GEOX:interpret",
        "WEALTH:diagnose",
        "WELL:reflect",
        "arifOS:synthesize",
    ],
    Mission.DECIDE: [
        "arifOS:think",
        "GEOX:consequence",
        "WEALTH:consequence",
        "WELL:readiness",
        "arifOS:judge",
        "arifOS:seal_prepare",
    ],
    Mission.ACT: [
        "arifOS:validate_authority",
        "A-FORGE:plan",
        "A-FORGE:dry_run",
        "arifOS:seal",
        "A-FORGE:execute",
        "VAULT999:record",
    ],
    Mission.MONITOR: [
        "arifOS:observe_continuous",
        "WELL:machine_health",
        "WEALTH:market_health",
        "GEOX:data_freshness",
        "arifOS:delta_report",
    ],
    Mission.RECALL: [
        "arifOS:memory_recall",
        "arifOS:verify_chain",
        "arifOS:memory_store",
    ],
}


def resolve_capability(
    cap_ref: str,
    stage_num: int,
    all_callable: dict[str, dict[str, dict]],
) -> list[ResolvedTool]:
    """Resolve a capability reference to actual callable tools from the registry.

    Args:
        cap_ref: e.g. "GEOX:interpret"
        stage_num: execution stage number
        all_callable: {organ: {tool_name: info}} from registry spine

    Returns:
        List of ResolvedTool instances. Empty if no tools found → HOLD.
    """
    if cap_ref not in CAPABILITY_TOOL_MAP:
        return []

    cap_def = CAPABILITY_TOOL_MAP[cap_ref]
    organ = cap_def["organ"]
    desired_tools = cap_def["tool_names"]
    callable_in_organ = all_callable.get(organ, {})

    resolved: list[ResolvedTool] = []

    for tool_name in desired_tools:
        if tool_name in callable_in_organ:
            info = callable_in_organ[tool_name]
            resolved.append(
                ResolvedTool(
                    capability_ref=CapabilityRef(
                        organ=organ,
                        capability=cap_ref.split(":")[1],
                        stage=stage_num,
                    ),
                    tool_name=tool_name,
                    tool_class=info["class"],
                    tool_desc=info["desc"],
                    organ=organ,
                    selection_reason=f"Capability '{cap_ref}' → tool '{tool_name}' (PUBLIC_CANONICAL, callable)",
                )
            )

    return resolved


def route(intent: str, spine_path: str | None = None) -> RouterResult:
    """The main entry point. Classify intent → resolve capabilities → build pipeline.

    Args:
        intent: Natural language from Arif, e.g. "Assess this prospect and
                tell me what could destroy the case."
        spine_path: Optional path to registry spine JSON.

    Returns:
        RouterResult with verdict, pipeline, and diagnostics.
    """
    errors: list[str] = []
    warnings: list[str] = []
    missing: list[str] = []

    # Load spine
    try:
        spine = load_registry_spine(spine_path)
    except Exception as e:
        return RouterResult(
            verdict=RouterVerdict.REJECTED,
            mission=None,
            risk_class="UNKNOWN",
            pipeline=[],
            mutation_allowed=False,
            missing_evidence=[],
            warnings=[],
            errors=[f"Failed to load registry spine: {e}"],
            graph_hash="",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    all_callable = get_all_callable(spine)

    # Classify intent
    mission, confidence, triggers = classify_intent(intent)

    if confidence < 0.15:
        return RouterResult(
            verdict=RouterVerdict.HOLD_INTENT,
            mission=mission,
            risk_class="UNKNOWN",
            pipeline=[],
            mutation_allowed=False,
            missing_evidence=[],
            warnings=[f"Low confidence classification ({confidence:.0%}). Triggers: {triggers}"],
            errors=[],
            graph_hash="",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    # Get pipeline
    pipeline_refs = MISSION_PIPELINES.get(mission, [])

    # Build stages
    stages: list[PipelineStage] = []
    current_stage = 0
    mutation_allowed = False

    for cap_ref_str in pipeline_refs:
        current_stage += 1
        resolved = resolve_capability(cap_ref_str, current_stage, all_callable)

        if not resolved:
            missing.append(cap_ref_str)
            warnings.append(f"No callable tools found for capability: {cap_ref_str}")
            continue

        cap_def = CAPABILITY_TOOL_MAP.get(cap_ref_str, {})

        stage = PipelineStage(
            stage=current_stage,
            organ=cap_def.get("organ", "UNKNOWN"),
            tools=resolved,
            can_parallel=cap_def.get("can_parallel", False),
            mutation=cap_def.get("mutation", False),
        )
        stages.append(stage)

        if cap_def.get("mutation", False):
            mutation_allowed = True

    # Verdict logic
    if missing:
        verdict = RouterVerdict.HOLD_CAPABILITY
    elif mission == Mission.ACT and not mutation_allowed:
        verdict = RouterVerdict.HOLD_EVIDENCE
        errors.append("ACT mission requires mutation capability but no mutation tools resolved")
    else:
        verdict = RouterVerdict.READY

    # Compute graph hash
    graph_data = json.dumps(
        [
            {
                "stage": s.stage,
                "organ": s.organ,
                "tools": [t.tool_name for t in s.tools],
                "mutation": s.mutation,
            }
            for s in stages
        ],
        sort_keys=True,
    )
    graph_hash = hashlib.sha256(graph_data.encode()).hexdigest()[:16]

    # Risk class
    risk_class = _compute_risk_class(mission, mutation_allowed, stages)

    return RouterResult(
        verdict=verdict,
        mission=mission,
        risk_class=risk_class,
        pipeline=stages,
        mutation_allowed=mutation_allowed,
        missing_evidence=missing,
        warnings=warnings,
        errors=errors,
        graph_hash=graph_hash,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


def _compute_risk_class(mission: Mission, mutation: bool, stages: list[PipelineStage]) -> str:
    """Compute risk class C1-C5 based on mission and mutation status."""
    if mission == Mission.ACT:
        return "C5" if mutation else "C4"
    elif mission == Mission.DECIDE:
        return "C3"
    elif mission == Mission.MONITOR:
        return "C2"
    else:
        return "C1"


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════


def format_router_output(result: RouterResult) -> dict[str, Any]:
    """Format RouterResult into the P0 router contract output shape."""
    return {
        "mission": result.mission.value if result.mission else None,
        "risk_class": result.risk_class,
        "pipeline": [
            {
                "stage": s.stage,
                "organ": s.organ,
                "capability": s.tools[0].capability_ref.capability if s.tools else "unknown",
                "tools": [t.tool_name for t in s.tools],
                "mode": "read_only" if not s.mutation else "mutation_gated",
                "can_parallel": s.can_parallel,
                "selection_reasons": [t.selection_reason for t in s.tools],
            }
            for s in result.pipeline
        ],
        "mutation_allowed": result.mutation_allowed,
        "missing_evidence": result.missing_evidence,
        "warnings": result.warnings,
        "errors": result.errors,
        "status": result.verdict.value,
        "graph_hash": result.graph_hash,
        "generated_at": result.generated_at,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════════════════════

TEST_CASES = [
    # (intent, expected_mission, expected_verdict, description)
    (
        "Assess this prospect and tell me what could destroy the case.",
        Mission.DECIDE,
        RouterVerdict.READY,
        "Prospect evaluation → DECIDE",
    ),
    (
        "What's happening with the VPS?",
        Mission.OBSERVE,
        RouterVerdict.READY,
        "Status check → OBSERVE",
    ),
    ("Why did the well test fail?", Mission.EXPLAIN, RouterVerdict.READY, "Root cause → EXPLAIN"),
    (
        "Should we drill prospect Alpha?",
        Mission.DECIDE,
        RouterVerdict.READY,
        "Drill decision → DECIDE",
    ),
    ("Deploy the fix for the auth bug.", Mission.ACT, RouterVerdict.READY, "Deploy → ACT"),
    (
        "Watch the CPU and alert me if it exceeds 90%.",
        Mission.MONITOR,
        RouterVerdict.READY,
        "Watch → MONITOR",
    ),
    (
        "What did we decide about the Malay Basin prospect?",
        Mission.RECALL,
        RouterVerdict.READY,
        "Recall → RECALL",
    ),
    (
        "Check the health of everything.",
        Mission.MONITOR,
        RouterVerdict.READY,
        "Health check → MONITOR",
    ),
    (
        "Find all evidence about reservoir quality in well X.",
        Mission.OBSERVE,
        RouterVerdict.READY,
        "Evidence → OBSERVE",
    ),
    (
        "Give me competing explanations for the AVO anomaly.",
        Mission.EXPLAIN,
        RouterVerdict.READY,
        "Interpretation → EXPLAIN",
    ),
    (
        "Is this investment worth the risk?",
        Mission.DECIDE,
        RouterVerdict.READY,
        "Investment → DECIDE",
    ),
    ("Execute the approved deployment plan.", Mission.ACT, RouterVerdict.READY, "Execute → ACT"),
    # Edge cases
    ("asdfghjkl", Mission.OBSERVE, RouterVerdict.HOLD_INTENT, "Gibberish → HOLD"),
    ("", Mission.OBSERVE, RouterVerdict.HOLD_INTENT, "Empty → HOLD"),
]


def run_tests() -> dict[str, Any]:
    """Run all router tests. Returns report."""
    results = {"total": len(TEST_CASES), "passed": 0, "failed": 0, "details": []}

    for intent, expected_mission, expected_verdict, desc in TEST_CASES:
        result = route(intent)

        mission_ok = result.mission == expected_mission
        verdict_ok = result.verdict == expected_verdict
        passed = mission_ok and verdict_ok

        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1

        results["details"].append(
            {
                "intent": intent[:80],
                "desc": desc,
                "expected_mission": expected_mission.value,
                "got_mission": result.mission.value if result.mission else "NONE",
                "expected_verdict": expected_verdict.value,
                "got_verdict": result.verdict.value,
                "mission_ok": mission_ok,
                "verdict_ok": verdict_ok,
                "passed": passed,
                "pipeline_stages": len(result.pipeline),
                "graph_hash": result.graph_hash,
            }
        )

    return results


if __name__ == "__main__":
    report = run_tests()
    print(f"Router Tests: {report['passed']}/{report['total']} passed")
    print()
    for d in report["details"]:
        status = "✅" if d["passed"] else "❌"
        print(f"{status} [{d['got_mission']}] {d['desc']}")
        if not d["passed"]:
            print(
                f"   Expected: {d['expected_mission']}/{d['expected_verdict']}  Got: {d['got_mission']}/{d['got_verdict']}"
            )
        print(f"   Pipeline: {d['pipeline_stages']} stages, hash={d['graph_hash']}")
        print()
