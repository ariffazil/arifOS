#!/usr/bin/env python3
"""Conservative first-pass router for AAA governed intelligence requests — v3.

Classifies a request along three orthogonal axes:
- abstraction: owner organ/interface/boundary
- attestation: likely evidence state (7-label)
- abduction: best route and validation step

Adds v3 governance runtime metadata:
- entropy_budget_tokens (tier-aware default)
- max_recursion_depth (default 3, hard cap 5)
- explicit-organ override (forces organ label, F10-respecting)
- 8-cardinality contract: AAA, arifOS, APEX, A-FORGE, GEOX, WEALTH, WELL, profile

The helper is a starting point only. Live evidence and explicit F13
authority override it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


# F10 ONTOLOGY: 8-cardinality. Order = priority. Do not add a 9th label.
ORGAN_RULES: list[tuple[str, float, str, str]] = [
    (
        "AAA",
        0.94,
        r"\b(aaa|cockpit|a2a|agent card|registry|arep|reality console|control plane|mission|handoff|route|routing|abstraction|attestation|abduction|entropy|governance|orthogonal|recursive)\b",
        "AAA control-plane, AREP, routing, or orthogonal governance task",
    ),
    (
        "arifOS",
        0.92,
        r"\b(arifos|f1|f2|f3|f4|f5|f6|f7|f8|f9|f10|f11|f12|f13|floor|constitution|constitutional|judge|seal|sabar|hold|void|vault999|mcp tool|kernel|authority|doctrine|invariants)\b",
        "constitutional law, MCP kernel, verdict, or authority task",
    ),
    (
        "APEX",
        0.91,
        r"\b(apex|888_judge|deliberation|adjudicat|verdict|888_hold|f13|sovereign|constitutional review)\b",
        "APEX/888_JUDGE deliberation, F13 sovereign review, or constitutional verdict",
    ),
    (
        "A-FORGE",
        0.88,
        r"\b(a-forge|forge|execute|execution|deploy|build|shell|terminal|tool run|orchestrate|workflow|pipeline|telemetry|llm provider|installer)\b",
        "governed execution, build/deploy, orchestration, or telemetry task",
    ),
    (
        "GEOX",
        0.90,
        r"\b(geox|geology|geoscience|well log|las|seismic|horizon|petrophysics|stratigraphy|prospect|reservoir|basin|drilling|acrisk|avo|earth)\b",
        "earth evidence, wells, seismic, petrophysics, or prospect risk",
    ),
    (
        "WEALTH",
        0.90,
        r"\b(wealth|capital|npv|irr|emv|cash ?flow|valuation|portfolio|allocation|macro|risk|price|liquidity|dscr|runway|investment|stewardship)\b",
        "capital intelligence, valuation, macro, risk, or allocation analysis",
    ),
    (
        "WELL",
        0.86,
        r"\b(well\b|readiness|fatigue|sleep|stress|vitality|dignity|substrate|metabolic|homeostasis|repair|livelihood|reliability|biological)\b",
        "human readiness, substrate state, fatigue, dignity, or reliability",
    ),
    (
        "profile",
        0.72,
        r"\b(profile|arif fazil|biography|professional|geoscientist|public surface|linkedin|contact)\b",
        "public/professional profile context (never primary route)",
    ),
]

VALID_ORGANS = {o[0] for o in ORGAN_RULES}

RISK_RULES: list[tuple[int, str, str]] = [
    (
        3,
        r"\b(drop database|delete data|rm -rf|force push|reset --hard|constitutional floor change|final seal|vault final|irreversible|permanent release|allocate capital|drilling decision)\b",
        "irreversible or constitutional action",
    ),
    (
        2,
        r"\b(production|deploy|secret|token|auth|external communication|budget|capital allocation|allocate capital|drilling decision|decide whether to allocate|cross-repo architecture|public release|commit|push|merge)\b",
        "high blast radius or explicit authorization boundary",
    ),
    (
        1,
        r"\b(edit|modify|patch|git commit|code commit|refactor|create file|update code|change|run test|implement|install|forge|add)\b",
        "reversible mutation or implementation work",
    ),
]

GOLDEN_PATH: list[str] = [
    "declare_intent",
    "abstraction",
    "attestation",
    "abduction",
    "compose_receipt",
    "recurse_or_halt",
]

ENTROPY_BUDGET_BY_TIER: dict[int, int] = {0: 1500, 1: 3000, 2: 4000, 3: 6000}
DEFAULT_RECURSION_DEPTH = 3
HARD_RECURSION_CAP = 5

# 7-label evidence states (extends the v2 binary)
EVIDENCE_LABELS = ["FACT", "OBSERVED", "DERIVED", "INFERRED", "HYPOTHESIS", "UNVERIFIED", "SIMULATION"]


@dataclass
class Route:
    organ: str
    confidence: float
    reason: str
    hits: int = 0


@dataclass
class Abstraction:
    owner_organ: str
    interface: str
    boundary: str
    confidence: float
    secondary: list
    low_confidence: bool


@dataclass
class Attestation:
    reality_layer: str
    claim_limits: list


@dataclass
class Abduction:
    best_route: list
    missing_evidence: list
    validation_step: str


@dataclass
class RoutingResult:
    schema_version: str
    request: str
    abstraction: Abstraction
    attestation: Attestation
    abduction: Abduction
    risk_tier: int
    risk_reason: str
    primary: Route
    secondary: list
    hold_conditions: list
    entropy_budget_tokens: int
    max_recursion_depth: int


def classify_risk(text: str) -> tuple[int, str]:
    lowered = text.lower()
    for tier, pattern, reason in RISK_RULES:
        if re.search(pattern, lowered):
            return tier, reason
    return 0, "read-only explanation, classification, or planning"


def route_organs(text: str) -> list[Route]:
    lowered = text.lower()
    matches: list[Route] = []
    for organ, base_conf, pattern, reason in ORGAN_RULES:
        hits = re.findall(pattern, lowered)
        if hits:
            distinct = len(set(hits))
            adjusted = min(0.99, base_conf + 0.02 * (distinct - 1))
            matches.append(Route(organ, round(adjusted, 3), reason, distinct))
    if not matches:
        matches.append(Route("AAA", 0.58, "default control-plane abstraction for ambiguous federation task", 0))
    matches.sort(key=lambda r: r.confidence, reverse=True)
    return matches


def infer_interface(text: str) -> str:
    lowered = text.lower()
    if re.search(r"\b(repo|code|file|patch|commit|readme|test)\b", lowered):
        return "repo"
    if re.search(r"\b(mcp|tool|connector)\b", lowered):
        return "MCP"
    if re.search(r"\b(a2a|agent card|registry|arep)\b", lowered):
        return "A2A/AREP"
    if re.search(r"\b(ui|cockpit|dashboard|console)\b", lowered):
        return "UI/control-plane"
    if re.search(r"\b(deploy|runtime|health|service|port)\b", lowered):
        return "runtime"
    return "conceptual/control-plane"


def infer_attestation(text: str) -> Attestation:
    """Pick one of 7 evidence labels (never upgrade without trail)."""
    lowered = text.lower()
    if re.search(r"\b(live|health|verified|test output|tool returned|observed|log shows)\b", lowered):
        return Attestation("OBSERVED", ["requires source + timestamp if used as fact"])
    if re.search(r"\b(simulate|simulation|rehearsal)\b", lowered):
        return Attestation("SIMULATION", ["explicit sim tag required; non-authoritative"])
    if re.search(r"\b(assume|probably|hypothesis|maybe|infer|likely)\b", lowered):
        return Attestation("HYPOTHESIS", ["must carry falsifier; not presentable as verified state"])
    if re.search(r"\b(unverified|unsupported|no evidence|claimed)\b", lowered):
        return Attestation("UNVERIFIED", ["no claim of fact allowed until evidence arrives"])
    if re.search(r"\b(derive|computed|calculated|formula)\b", lowered):
        return Attestation("DERIVED", ["method + inputs must be visible"])
    return Attestation("INFERRED", ["confirm with repo/runtime evidence before high-consequence action"])


def boundary_for(organ: str) -> str:
    return {
        "AAA": "routes, displays, declares tasks, lowers entropy; does not judge, compute domain evidence, or execute unapproved mutations",
        "arifOS": "judges and governs; does not replace Arif/F13 for sovereign decisions",
        "APEX": "deliberates and returns verdict; never self-executes; final authority is F13",
        "A-FORGE": "executes approved work; does not self-authorize; needs JUDGE_SEAL_AUTHORIZATION for irreversible execution",
        "GEOX": "computes earth evidence; does not decide drilling or capital allocation",
        "WEALTH": "models capital evidence; does not allocate capital alone",
        "WELL": "observes readiness; does not diagnose or coerce",
        "profile": "states sourced public profile facts; avoids unsupported personal inference; never primary route",
    }.get(organ, "unknown boundary; hold until clarified")


def hold_conditions_for(tier: int, routes: Iterable[Route]) -> list[str]:
    conditions: list[str] = []
    organ_names = {r.organ for r in routes}
    if tier >= 2:
        conditions.append("explicit F13/human approval required before execution")
    if tier == 3:
        conditions.append("do not execute irreversible or constitutional mutations; 888_HOLD until F13 ack")
    if "APEX" in organ_names:
        conditions.append("APEX deliberates and returns verdict; never self-executes — final authority is F13")
    if "A-FORGE" in organ_names:
        conditions.append("A-FORGE execution requires approved plan and judge/approval gate for high-risk work")
    if "GEOX" in organ_names:
        conditions.append("GEOX must provide evidence, uncertainty, and claim limits; no drilling decision alone")
    if "WEALTH" in organ_names:
        conditions.append("WEALTH must expose assumptions/downside risk; no capital allocation alone")
    if "WELL" in organ_names:
        conditions.append("WELL observes readiness only; no diagnosis or coercive decision")
    if not conditions:
        conditions.append("final SEAL/HOLD/VOID remains with arifOS/F13 when consequential")
    return conditions


def entropy_budget_for(tier: int) -> int:
    return ENTROPY_BUDGET_BY_TIER.get(tier, 4000)


def route(text: str, explicit_organ: str | None = None, max_recursion_depth: int = DEFAULT_RECURSION_DEPTH) -> RoutingResult:
    if explicit_organ:
        if explicit_organ not in VALID_ORGANS:
            raise ValueError(
                f"explicit_organ '{explicit_organ}' violates cardinality contract (F10). Valid: {sorted(VALID_ORGANS)}"
            )
        routes = [Route(explicit_organ, 1.0, "operator-forced explicit organ (F10 cardinality respected)", 0)]
    else:
        routes = route_organs(text)

    tier, reason = classify_risk(text)
    primary = routes[0]
    interface = infer_interface(text)
    attestation = infer_attestation(text)
    best_route = [r.organ for r in routes]
    if primary.organ not in ("arifOS", "APEX") and tier >= 2:
        best_route.append("arifOS/F13 gate")
    abduction = Abduction(
        best_route=best_route,
        missing_evidence=["live health/registry or repo source-of-truth"] if tier >= 1 else [],
        validation_step="inspect source-of-truth before mutation" if tier >= 1 else "state evidence class and proceed read-only",
    )

    if max_recursion_depth > HARD_RECURSION_CAP:
        max_recursion_depth = HARD_RECURSION_CAP  # F10-style ceiling

    low_confidence = primary.confidence < 0.55

    return RoutingResult(
        schema_version="3.0.0",
        request=text,
        abstraction=Abstraction(
            owner_organ=primary.organ,
            interface=interface,
            boundary=boundary_for(primary.organ),
            confidence=primary.confidence,
            secondary=[r.organ for r in routes[1:]],
            low_confidence=low_confidence,
        ),
        attestation=attestation,
        abduction=abduction,
        risk_tier=tier,
        risk_reason=reason,
        primary=primary,
        secondary=routes[1:],
        hold_conditions=hold_conditions_for(tier, routes),
        entropy_budget_tokens=entropy_budget_for(tier),
        max_recursion_depth=max_recursion_depth,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Route an AAA governed intelligence request (v3, 8-cardinality).")
    parser.add_argument("request", nargs="*", help="User request text. Reads stdin if omitted.")
    parser.add_argument(
        "--explicit-organ",
        default=None,
        help="Force a specific organ (must be in the 8-cardinality set).",
    )
    parser.add_argument(
        "--max-recursion-depth",
        type=int,
        default=DEFAULT_RECURSION_DEPTH,
        help=f"Max refinement cycles (default {DEFAULT_RECURSION_DEPTH}, hard cap {HARD_RECURSION_CAP}).",
    )
    args = parser.parse_args()
    text = " ".join(args.request).strip() or sys.stdin.read().strip()
    if not text:
        parser.error("provide a request as arguments or stdin")
    result = route(text, explicit_organ=args.explicit_organ, max_recursion_depth=args.max_recursion_depth)
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
