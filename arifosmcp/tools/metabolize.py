"""
arifosmcp/tools/metabolize.py — 444_METABOLIZE
═══════════════════════════════════════════════════════════════════════════════════

Governed Witness Metabolism Tool
444_METABOLIZE — Witness → Meaning → Verification → Model Update → Judgment

Arif Eureka 2026-05-16:
  "Intelligence is not answer generation.
   Intelligence is governed witness metabolism."

The loop:
  witness → decode → contrast → meaning → constraint → model update → judgment

This tool implements the metabolic loop:
  1. Ingest raw witnesses (evidence)
  2. Classify witness type (perception class)
  3. Detect anomalous contrasts
  4. Generate candidate meanings
  5. Check constraints (physics, law, ethics)
  6. Propose model update (state_before → state_after)
  7. Return MetabolicOutput with SOVEREIGNTY BOUNDARY flags

SOVEREIGNTY BOUNDARY (Eureka 8):
  AI proposes. Tools compute. Memory records. Constraints guard. Arif judges.

  recommendation_only: True      — AI proposes only
  execution_authorized: False    — Not ratified by human
  human_final_authority: "Arif"  — F13 veto intact
  requires_888_judge: False     — True for irreversible actions

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.floor import check_floors
from arifosmcp.runtime.llm_client import LLMUnavailableError, call_llm
from arifosmcp.runtime.session_auth import validate_session
from arifosmcp.runtime.tools import _hold, _ok
from arifosmcp.schemas.metabolic import (
    AbstractionGuard,
    AbstractionUse,
    AnomalousContrast,
    CandidateMeaning,
    ClaimState,
    ConstraintCheck,
    ContrastSeverity,
    DecodedEntity,
    MetabolicOutput,
    ModelTarget,
    ModelUpdate,
    OrganType,
    UncertaintyBand,
    Witness,
    WitnessType,
)

# ── System Prompt ───────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Arif — Constitutional AI operating under the 13 Floors (F01–F13).

You implement the GOVERNED WITNESS METABOLISM loop (Eureka 2026-05-16):

Intelligence is not answer generation.
Intelligence is governed witness metabolism.

The metabolic loop:
  witness → decode → contrast → meaning → constraint → model update → judgment

Your task: Given raw evidence (witnesses), process them through the full loop.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1 — WITNESS CLASSIFICATION & ATTESTATION (Eureka 2026-05-21)
Classify each witness by type and depth:
  map | seismic | filing | report | image | log | testimony | sensor | document | signal

Every claim MUST carry an attestation chain:
  abstraction_level: raw | measured | interpreted | modeled | symbolic | normative
  source_basis: observation | dataset | equation | expert judgment | analogy | speculation
  uncertainty: low | moderate | high
  reversibility: reversible | partial | irreversible

Map to perception_class:
  MEASURED = direct sensor
  DERIVED = from measured data
  DISPLAY = visual artifact
  CORROBORATED = multi-evidence
  HYPOTHESIS = proxy without raw signal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 2 — ANOMALOUS CONTRAST DETECTION
For each decoded entity, ask: does it deviate from expected background?

Examples:
  GEOX: bright spot ≠ gas automatically (could be tuning, coal, carbonate, artifact)
  WEALTH: profit decline + high dividend + debt rise ≠ fraud automatically
  Governance: UK incorporation + public silence ≠ illegality automatically

Contrast severity: LOW | MODERATE | HIGH | CRITICAL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 3 — CANDIDATE MEANINGS (ABDUCTION DISCIPLINE)
For each anomaly, generate differential interpretations.

Abduction may propose; it may not certify.
For every ABDUCED claim, you MUST provide:
  - primary_interpretation: best explanation
  - rival_hypotheses[]: what else could it be?
  - disconfirming_tests[]: what would prove this WRONG?

NEVER allow: detected=true → meaning=proven

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 4 — PRIME INVARIANT STACK (PHYSICS > MATH > ECON > EARTH)
Verify against hard boundary conditions:

1. PHYSICS:
   - Conservation: claimed output must not exceed input.
   - Entropy: order requires maintenance cost.
   - Rate limits: change must not exceed adaptive capacity.
   - Irreversibility: flag non-undoable state changes.

2. MATH:
   - Axiom scope: axioms are not reality.
   - Model limits: map is not territory.

3. ECONOMICS:
   - Scarcity: resources (time, money, attention) have limits.
   - Opportunity cost: choosing A excludes B.
   - Externalities: who pays the hidden cost?

4. EARTH:
   - Stocks/Sinks: no infinite backdrop.
   - Regeneration: extraction rate must not exceed regeneration rate.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 5 — GOVERNING EQUATION CHECK (Eureka 2026-05-22)
Apply the Governing Equation of Intelligence: G = Δ · Ω · Ψ
- Δ (Capability): What is the action power of this update?
- Ω (Empathy): What is the human burden sensing / consequence awareness?
- Ψ (Judgment): What is the constraint reasoning?
If Ω or Ψ are critically low, flag as Dark Cleverness (C_dark) hazard.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 6 — MODEL UPDATE
Propose state changes to the domain model.

For each update:
  - model_id: which model
  - model_type: LargeEarthModel | LargeWealthModel | LargeInstitutionModel | LargeBodyModel
  - state_before: what the model believed before
  - proposed_updates[]: specific changes
  - state_after: what the model would believe after

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 7 — SOVEREIGNTY BOUNDARY & CAPABILITY MEMBRANE
Return with these flags:
  recommendation_only: True (AI proposes only)
  execution_authorized: False (not ratified by human)
  human_final_authority: "Arif" (F13 veto intact)
  requires_888_judge: False (True only for irreversible actions)
  capability_membrane_leashed: True (Tool actions explicitly limited to approved exact scope)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Output: JSON matching the MetabolicOutput schema exactly.
"""


# ── LLM Schema for Metabolic Output ────────────────────────────────────────────

METABOLIZE_SCHEMA = {
    "type": "object",
    "properties": {
        "witnesses_ingested": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "witness_id": {"type": "string"},
                    "witness_type": {
                        "type": "string",
                        "enum": [
                            "map",
                            "seismic",
                            "filing",
                            "report",
                            "image",
                            "log",
                            "testimony",
                            "sensor",
                            "document",
                            "signal",
                        ],
                    },
                    "attestation": {
                        "type": "object",
                        "properties": {
                            "abstraction_level": {"type": "string"},
                            "source_basis": {"type": "string"},
                            "uncertainty": {"type": "string"},
                            "reversibility": {"type": "string"},
                        },
                    },
                    "source_uri": {"type": "string"},
                    "raw_content": {"type": "string"},
                    "ingested_at": {"type": "string"},
                    "provenance": {"type": "string"},
                },
                "required": ["witness_id", "witness_type", "ingested_at"],
            },
        },
        "decoded_entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string"},
                    "entity_type": {"type": "string"},
                    "detected_at_depth": {"type": "string"},
                    "detected_value": {},
                    "detection_confidence": {"type": "number"},
                    "perception_class": {
                        "type": "string",
                        "enum": ["MEASURED", "DERIVED", "DISPLAY", "CORROBORATED", "HYPOTHESIS"],
                    },
                    "evidence_tag": {"type": "string"},
                },
                "required": ["entity_id", "entity_type", "detection_confidence"],
            },
        },
        "anomalous_contrasts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "contrast_id": {"type": "string"},
                    "contrast_domain": {
                        "type": "string",
                        "enum": ["earth", "wealth", "institution", "health", "law", "system"],
                    },
                    "background_expectation": {"type": "string"},
                    "observed_deviation": {"type": "string"},
                    "candidate_causes": {"type": "array", "items": {"type": "string"}},
                    "false_positive_risks": {"type": "array", "items": {"type": "string"}},
                    "required_verification": {"type": "array", "items": {"type": "string"}},
                    "severity": {
                        "type": "string",
                        "enum": ["LOW", "MODERATE", "HIGH", "CRITICAL"],
                    },
                },
                "required": [
                    "contrast_id",
                    "contrast_domain",
                    "background_expectation",
                    "observed_deviation",
                    "severity",
                ],
            },
        },
        "candidate_meanings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "meaning_id": {"type": "string"},
                    "decoded_entity_id": {"type": "string"},
                    "possible_meanings": {"type": "array", "items": {"type": "string"}},
                    "primary_interpretation": {"type": "string"},
                    "rival_hypotheses": {"type": "array", "items": {"type": "string"}},
                    "meaning_confidence": {"type": "number"},
                    "meaning_confidence_band": {"type": "array", "items": {"type": "number"}},
                    "tests_needed_before_claim": {"type": "array", "items": {"type": "string"}},
                    "disconfirming_tests": {"type": "array", "items": {"type": "string"}},
                    "ruling_out": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "meaning_id",
                    "decoded_entity_id",
                    "possible_meanings",
                    "primary_interpretation",
                    "meaning_confidence",
                ],
            },
        },
        "constraints_checked": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "constraint_id": {"type": "string"},
                    "constraint_type": {
                        "type": "string",
                        "enum": [
                            "physics",
                            "math",
                            "economics",
                            "earth",
                            "law",
                            "ethics",
                            "financial",
                            "constitutional",
                        ],
                    },
                    "rule_invoked": {"type": "string"},
                    "check_passed": {"type": "boolean"},
                    "failure_reason": {"type": "string"},
                    "evidence_required": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["constraint_id", "constraint_type", "rule_invoked", "check_passed"],
            },
        },
        "model_updates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "model_id": {"type": "string"},
                    "model_type": {
                        "type": "string",
                        "enum": [
                            "LargeEarthModel",
                            "LargeWealthModel",
                            "LargeInstitutionModel",
                            "LargeBodyModel",
                            "LargeSystemModel",
                        ],
                    },
                    "state_before": {"type": "object"},
                    "incoming_witnesses": {"type": "array", "items": {"type": "string"}},
                    "proposed_updates": {"type": "array", "items": {"type": "object"}},
                    "constraints_checked": {"type": "array", "items": {"type": "string"}},
                    "state_after": {"type": "object"},
                    "confidence_delta": {"type": "number"},
                    "audit_receipt": {"type": "string"},
                },
                "required": ["model_id", "model_type", "state_before", "state_after"],
            },
        },
        "required_next_tests": {
            "type": "array",
            "items": {"type": "string"},
        },
        "next_best_tool": {"type": "string"},
        "claim_state": {
            "type": "string",
            "enum": [
                "OBSERVED",
                "MEASURED",
                "INFERRED",
                "ABDUCED",
                "HYPOTHESIS",
                "QUALIFIED",
                "NORMATIVE",
                "SPECULATIVE",
                "VERIFIED",
                "SEALED",
                "HOLD",
                "VOID",
            ],
        },
        "uncertainty": {
            "type": "object",
            "properties": {
                "omega_0": {"type": "number"},
                "uncertainty_range": {"type": "array", "items": {"type": "number"}},
                "major_unknowns": {"type": "array", "items": {"type": "string"}},
                "key_missing_evidence": {"type": "array", "items": {"type": "string"}},
                "claim_too_certain_flag": {"type": "boolean"},
            },
        },
    },
    "required": [
        "witnesses_ingested",
        "decoded_entities",
        "anomalous_contrasts",
        "candidate_meanings",
        "claim_state",
    ],
}



# ── Tool Implementation ─────────────────────────────────────────────────────────


async def arif_metabolize(
    witnesses: list[dict[str, Any]],
    domain: str = "earth",
    context: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Governed Witness Metabolism Tool.

    Processes raw evidence through the full metabolic loop:
      witness → decode → contrast → meaning → constraint → model update → judgment

    Args:
        witnesses: List of raw evidence items. Each item should have at minimum:
            - content: the raw evidence (text, data, etc.)
            - source: where it came from
            - type: optional hint at witness type
        domain: Which domain model to update.
            earth | wealth | institution | health | body | system
        context: Optional additional context for the metabolic analysis.
        session_id: Governed session ID.
        actor_id: Sovereign actor identifier.

    Returns:
        dict with full metabolic loop results including MetabolicOutput.

    Eureka 8 SOVEREIGNTY BOUNDARY:
        - recommendation_only: True (AI proposes only)
        - execution_authorized: False (not ratified by human)
        - human_final_authority: "Arif" (F13 veto intact)
        - requires_888_judge: False (True only for irreversible actions)
    """
    now = datetime.now(UTC).isoformat()

    # ── Auth ──────────────────────────────────────────────────────────────────
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        return _build_metabolic_hold_dict(
            reason=f"Session invalid: {auth.get('reason', 'unknown')}",
            floors=["F11"],
            session_id=session_id,
            now=now,
        )

    # ── Floor Check ───────────────────────────────────────────────────────────
    floor_check = check_floors(
        "arif_metabolize",
        {
            "domain": domain,
            "witness_count": len(witnesses),
            "context": context or "",
        },
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return _build_metabolic_hold_dict(
            reason=floor_check.get("reason", "Floor check failed"),
            floors=floor_check.get("failed_floors", []),
            session_id=session_id,
            now=now,
        )

    # ── Map domain to enums ───────────────────────────────────────────────────
    domain_to_target = {
        "earth": ModelTarget.EARTH,
        "wealth": ModelTarget.WEALTH,
        "institution": ModelTarget.INSTITUTION,
        "health": ModelTarget.BODY,
        "body": ModelTarget.BODY,
        "system": ModelTarget.SYSTEM,
    }
    model_target = domain_to_target.get(domain.lower(), ModelTarget.SYSTEM)

    domain_to_organ = {
        "earth": OrganType.GEOX,
        "wealth": OrganType.WEALTH,
        "institution": OrganType.INSTX,
        "health": OrganType.WELL,
        "body": OrganType.WELL,
        "system": OrganType.ARIFOS,
    }
    organ = domain_to_organ.get(domain.lower(), OrganType.ARIFOS)

    # ── Build witness summaries for LLM ───────────────────────────────────────
    witness_summaries = []
    for i, w in enumerate(witnesses):
        witness_summaries.append(
            {
                "witness_id": w.get("witness_id", f"witness-{i + 1}"),
                "witness_type": w.get("type", w.get("witness_type", "document")),
                "source_uri": w.get("source", w.get("source_uri", "")),
                "raw_content": str(w.get("content", w.get("raw_content", "")))[:500],
                "ingested_at": now,
                "provenance": w.get("provenance", ""),
            }
        )

    user_prompt = f"""Process the following witnesses through the GOVERNED METABOLIC LOOP.

Domain: {domain}
Model Target: {model_target.value}
Organ: {organ.value}

WITNESSES:
{_format_witnesses(witness_summaries)}

{"\nADDITIONAL CONTEXT: " + context if context else ""}

Process through all 6 steps and return the complete MetabolicOutput JSON.
"""

    # ── Call LLM ──────────────────────────────────────────────────────────────
    try:
        envelope = await call_llm(
            system=SYSTEM_PROMPT,
            user=user_prompt,
            response_schema=METABOLIZE_SCHEMA,
            temperature=0.3,
            max_tokens=1500,
            tool_origin="444_METABOLIZE",
            mode="metabolize",
        )
        parsed = envelope.parsed_output
        llm_available = True
    except LLMUnavailableError:
        parsed = _fallback_metabolic_processing(user_prompt)
        llm_available = False

    # ── Build MetabolicOutput ─────────────────────────────────────────────────
    try:
        output = _build_metabolic_output(
            parsed=parsed,
            organ=organ,
            model_target=model_target,
            witness_summaries=witness_summaries,
            now=now,
            session_id=session_id,
        )
    except Exception as e:
        return _build_metabolic_hold_dict(
            reason=f"Failed to build metabolic output: {str(e)}",
            floors=["F10"],
            session_id=session_id,
            now=now,
        )

    # ── Return as dict with meta ──────────────────────────────────────────────
    result = output.model_dump(mode="json")
    result["_llm_available"] = llm_available
    result["_envelope"] = {
        "tool_origin": "444_METABOLIZE",
        "mode": "metabolize",
        "wrapper_version": "444_METABOLIZE_v1.0",
    }

    return _ok(
        "arif_metabolize",
        result,
        meta={"domain": domain, "witness_count": len(witnesses)},
        delta_S=0.0,
        session_id=session_id,
    )


def _format_witnesses(witnesses: list[dict[str, Any]]) -> str:
    """Format witnesses for the LLM prompt."""
    lines = []
    for w in witnesses:
        lines.append(
            f"- [{w['witness_id']}] type={w['witness_type']} "
            f"source={w['source_uri']} content={w['raw_content'][:200]}..."
        )
    return "\n".join(lines) if lines else "(no witnesses)"


def _fallback_metabolic_processing(user_prompt: str) -> dict[str, Any]:
    """
    Deterministic fallback when LLM is unavailable.
    Processes witnesses through rule-based anomaly detection.
    """

    now = datetime.now(UTC).isoformat()

    # Extract witness content from prompt
    witness_lines = []
    in_witnesses = False
    for line in user_prompt.split("\n"):
        if "WITNESSES:" in line:
            in_witnesses = True
            continue
        if in_witnesses and line.strip().startswith("-"):
            witness_lines.append(line)
        elif in_witnesses and (
            line.strip().startswith("ADDITIONAL") or line.strip().startswith("Process")
        ):
            break

    witnesses = []
    for i, line in enumerate(witness_lines):
        wid = f"witness-{i + 1}"
        wtype = "document"
        if "seismic" in line.lower():
            wtype = "seismic"
        elif "map" in line.lower():
            wtype = "map"
        elif "log" in line.lower():
            wtype = "log"
        elif "filing" in line.lower() or "report" in line.lower():
            wtype = "filing"

        witnesses.append(
            {
                "witness_id": wid,
                "witness_type": wtype,
                "source_uri": "",
                "raw_content": line.strip(),
                "ingested_at": now,
                "provenance": "fallback_deterministic",
            }
        )

    # Simple anomaly detection: look for concerning keywords
    concerning = [
        "anomaly",
        "unexpected",
        "deviation",
        "decline",
        "rise",
        "contradiction",
        "inconsistent",
        "gap",
        "break",
    ]
    decoded_entities = []
    anomalous_contrasts = []
    candidate_meanings = []
    required_next_tests = []

    for w in witnesses:
        content_lower = w["raw_content"].lower()
        for concern in concerning:
            if concern in content_lower:
                eid = f"entity-{len(decoded_entities) + 1}"
                decoded_entities.append(
                    {
                        "entity_id": eid,
                        "entity_type": f"detected_{concern}",
                        "detected_at_depth": None,
                        "detected_value": concern,
                        "detection_confidence": 0.5,
                        "perception_class": "HYPOTHESIS",
                        "evidence_tag": "UNKNOWN",
                    }
                )

                cid = f"AC-{len(anomalous_contrasts) + 1:03d}"
                anomalous_contrasts.append(
                    {
                        "contrast_id": cid,
                        "contrast_domain": "system",
                        "background_expectation": f"No {concern} expected",
                        "observed_deviation": f"{concern} detected in evidence",
                        "candidate_causes": [
                            f"Real {concern}",
                            "Measurement error",
                            "Interpretation artifact",
                        ],
                        "false_positive_risks": ["Keyword match without physical basis"],
                        "required_verification": ["Cross-check with independent evidence"],
                        "severity": "MODERATE",
                    }
                )

                candidate_meanings.append(
                    {
                        "meaning_id": f"meaning-{len(candidate_meanings) + 1}",
                        "decoded_entity_id": eid,
                        "possible_meanings": [
                            f"Real {concern}",
                            "Measurement error",
                            "Context artifact",
                        ],
                        "primary_interpretation": "Requires further verification",
                        "meaning_confidence": 0.4,
                        "meaning_confidence_band": [0.2, 0.7],
                        "tests_needed_before_claim": ["Independent evidence required"],
                        "ruling_out": [],
                    }
                )
                required_next_tests.append(f"Verify {concern} with independent evidence source")
                break

    return {
        "witnesses_ingested": witnesses,
        "decoded_entities": decoded_entities,
        "anomalous_contrasts": anomalous_contrasts,
        "candidate_meanings": candidate_meanings,
        "constraints_checked": [
            {
                "constraint_id": "deterministic_fallback",
                "constraint_type": "constitutional",
                "rule_invoked": (
                    "F07 HUMILITY: LLM unavailable, deterministic fallback with low confidence"
                ),
                "check_passed": True,
                "failure_reason": "",
                "evidence_required": [],
            }
        ],
        "model_updates": [],
        "required_next_tests": required_next_tests,
        "next_best_tool": "arif_sense_observe",
        "claim_state": "HYPOTHESIS",
        "uncertainty": {
            "omega_0": 0.15,
            "uncertainty_range": [0.1, 0.3],
            "major_unknowns": ["LLM inference unavailable - deterministic fallback"],
            "key_missing_evidence": ["Full LLM inference would reduce uncertainty significantly"],
            "claim_too_certain_flag": False,
        },
    }


def _build_metabolic_output(
    parsed: dict[str, Any],
    organ: OrganType,
    model_target: ModelTarget,
    witness_summaries: list[dict[str, Any]],
    now: str,
    session_id: str | None = None,
) -> MetabolicOutput:
    """Build a complete MetabolicOutput from LLM parsed result."""

    # ── Parse witnesses ───────────────────────────────────────────────────────
    witnesses = []
    for w in parsed.get("witnesses_ingested", []):
        try:
            witnesses.append(
                Witness(
                    witness_id=w.get("witness_id", str(uuid.uuid4())[:8]),
                    witness_type=WitnessType(w.get("witness_type", "document")),
                    source_uri=w.get("source_uri", ""),
                    raw_content=w.get("raw_content"),
                    ingested_at=w.get("ingested_at", now),
                    session_id=session_id,
                    provenance=w.get("provenance", ""),
                )
            )
        except (ValueError, TypeError):
            continue

    # ── Parse decoded entities ────────────────────────────────────────────────
    decoded_entities = []
    for e in parsed.get("decoded_entities", []):
        try:
            decoded_entities.append(
                DecodedEntity(
                    entity_id=e.get("entity_id", str(uuid.uuid4())[:8]),
                    entity_type=e.get("entity_type", "unknown"),
                    detected_at_depth=e.get("detected_at_depth"),
                    detected_value=e.get("detected_value"),
                    detection_confidence=e.get("detection_confidence", 0.5),
                    perception_class=e.get("perception_class", "HYPOTHESIS"),
                    evidence_tag=e.get("evidence_tag", "UNKNOWN"),
                )
            )
        except (ValueError, TypeError):
            continue

    # ── Parse anomalous contrasts ─────────────────────────────────────────────
    anomalous_contrasts = []
    for c in parsed.get("anomalous_contrasts", []):
        try:
            anomalous_contrasts.append(
                AnomalousContrast(
                    contrast_id=c.get("contrast_id", f"AC-{uuid.uuid4().hex[:6]}"),
                    contrast_domain=c.get("contrast_domain", "system"),
                    background_expectation=c.get("background_expectation", ""),
                    observed_deviation=c.get("observed_deviation", ""),
                    candidate_causes=c.get("candidate_causes", []),
                    false_positive_risks=c.get("false_positive_risks", []),
                    required_verification=c.get("required_verification", []),
                    severity=ContrastSeverity(c.get("severity", "MODERATE")),
                )
            )
        except (ValueError, TypeError):
            anomalous_contrasts.append(
                AnomalousContrast(
                    contrast_id=f"AC-{uuid.uuid4().hex[:6]}",
                    contrast_domain="system",
                    background_expectation=c.get("background_expectation", ""),
                    observed_deviation=c.get("observed_deviation", ""),
                    severity=ContrastSeverity.MODERATE,
                )
            )

    # ── Parse candidate meanings ───────────────────────────────────────────────
    candidate_meanings = []
    for m in parsed.get("candidate_meanings", []):
        try:
            band_raw = m.get("meaning_confidence_band", [0.0, 1.0])
            if isinstance(band_raw, list) and len(band_raw) == 2:
                band_tuple: tuple[float, float] = (float(band_raw[0]), float(band_raw[1]))
            else:
                band_tuple = (0.0, 1.0)

            candidate_meanings.append(
                CandidateMeaning(
                    meaning_id=m.get("meaning_id", f"meaning-{uuid.uuid4().hex[:6]}"),
                    decoded_entity_id=m.get("decoded_entity_id", ""),
                    possible_meanings=m.get("possible_meanings", []),
                    primary_interpretation=m.get("primary_interpretation", ""),
                    meaning_confidence=m.get("meaning_confidence", 0.5),
                    meaning_confidence_band=band_tuple,
                    tests_needed_before_claim=m.get("tests_needed_before_claim", []),
                    ruling_out=m.get("ruling_out", []),
                )
            )
        except (ValueError, TypeError):
            continue

    # ── Parse constraints ────────────────────────────────────────────────────
    constraints_checked = []
    for c in parsed.get("constraints_checked", []):
        try:
            constraints_checked.append(
                ConstraintCheck(
                    constraint_id=c.get("constraint_id", str(uuid.uuid4())[:8]),
                    constraint_type=c.get("constraint_type", "constitutional"),
                    rule_invoked=c.get("rule_invoked", ""),
                    check_passed=c.get("check_passed", False),
                    failure_reason=c.get("failure_reason", ""),
                    evidence_required=c.get("evidence_required", []),
                )
            )
        except (ValueError, TypeError):
            continue

    # ── Parse model updates ───────────────────────────────────────────────────
    model_updates = []
    for u in parsed.get("model_updates", []):
        try:
            model_updates.append(
                ModelUpdate(
                    model_id=u.get("model_id", f"model-{uuid.uuid4().hex[:6]}"),
                    model_type=u.get("model_type", "LargeSystemModel"),
                    state_before=u.get("state_before", {}),
                    incoming_witnesses=u.get("incoming_witnesses", []),
                    proposed_updates=u.get("proposed_updates", []),
                    constraints_checked=u.get("constraints_checked", []),
                    state_after=u.get("state_after", {}),
                    confidence_delta=u.get("confidence_delta", 0.0),
                    audit_receipt=u.get("audit_receipt", ""),
                )
            )
        except (ValueError, TypeError):
            continue

    # ── Parse uncertainty ────────────────────────────────────────────────────
    unc = parsed.get("uncertainty", {})
    band_raw = unc.get("uncertainty_range", [0.0, 1.0])
    if isinstance(band_raw, list) and len(band_raw) == 2:
        range_tuple: tuple[float, float] = (float(band_raw[0]), float(band_raw[1]))
    else:
        range_tuple = (0.0, 1.0)

    uncertainty = UncertaintyBand(
        omega_0=unc.get("omega_0", 0.05),
        uncertainty_range=range_tuple,
        major_unknowns=unc.get("major_unknowns", []),
        key_missing_evidence=unc.get("key_missing_evidence", []),
        claim_too_certain_flag=unc.get("claim_too_certain_flag", False),
    )

    # ── Claim state ───────────────────────────────────────────────────────────
    try:
        claim_state = ClaimState(parsed.get("claim_state", "HYPOTHESIS"))
    except ValueError:
        claim_state = ClaimState.HYPOTHESIS

    # ── Required next tests ───────────────────────────────────────────────────
    required_next_tests = parsed.get("required_next_tests", [])
    next_best_tool = parsed.get("next_best_tool", "")

    # ── Determine if 888_JUDGE is required ────────────────────────────────────
    # HIGH/CRITICAL contrasts require judge
    requires_888 = any(
        c.severity in (ContrastSeverity.HIGH, ContrastSeverity.CRITICAL)
        for c in anomalous_contrasts
    )

    # ── Abstraction guard ───────────────────────────────────────────────────
    # Check if metaphors are being used as proof
    abstraction_guard = None
    for meaning in candidate_meanings:
        if meaning.meaning_confidence > 0.8 and len(meaning.possible_meanings) > 1:
            # High confidence but multiple meanings — guard against overclaiming
            abstraction_guard = AbstractionGuard(
                metaphor=(
                    f"Multiple possible meanings with high confidence "
                    f"({meaning.meaning_confidence})"
                ),
                literal_claim=meaning.primary_interpretation,
                evidence_required=meaning.tests_needed_before_claim,
                allowed_use=AbstractionUse.HYPOTHESIS,
                misuse_risk="Overconfident single-interpretation claim despite alternatives",
                violations=[],
            )
            break

    return MetabolicOutput(
        organ=organ,
        tool_name="arif_metabolize",
        session_id=session_id,
        witnesses_ingested=witnesses,
        witness_type=witnesses[0].witness_type if witnesses else None,
        decoded_entities=decoded_entities,
        anomalous_contrasts=anomalous_contrasts,
        candidate_meanings=candidate_meanings,
        constraints_checked=constraints_checked,
        model_updates=model_updates,
        model_target=model_target,
        abstraction_guard=abstraction_guard,
        uncertainty=uncertainty,
        required_next_tests=required_next_tests,
        next_best_tool=next_best_tool,
        claim_state=claim_state,
        audit_receipt="",
        # SOVEREIGNTY BOUNDARY (Eureka 8)
        recommendation_only=True,
        execution_authorized=False,
        human_final_authority="Arif",
        requires_888_judge=requires_888,
        timestamp_utc=now,
        constitution_hash="v2026.05.16-eureka-metabolic",
    )


def _build_metabolic_hold_dict(
    reason: str,
    floors: list[str],
    session_id: str | None,
    now: str,
) -> dict[str, Any]:
    """Build a HOLD MetabolicOutput when the tool cannot proceed."""
    output = MetabolicOutput(
        organ=OrganType.ARIFOS,
        tool_name="arif_metabolize",
        session_id=session_id,
        witnesses_ingested=[],
        decoded_entities=[],
        anomalous_contrasts=[],
        candidate_meanings=[],
        constraints_checked=[],
        model_updates=[],
        model_target=ModelTarget.SYSTEM,
        uncertainty=UncertaintyBand(
            omega_0=0.5,
            uncertainty_range=(0.3, 0.8),
            major_unknowns=["Metabolic loop could not complete"],
            key_missing_evidence=["Resolution of HOLD reason required"],
            claim_too_certain_flag=False,
        ),
        required_next_tests=["Resolve HOLD reason before continuing"],
        next_best_tool="",
        claim_state=ClaimState.HOLD,
        audit_receipt="",
        recommendation_only=True,
        execution_authorized=False,
        human_final_authority="Arif",
        requires_888_judge=False,
        timestamp_utc=now,
        constitution_hash="v2026.05.16-eureka-metabolic",
    )
    result = output.model_dump(mode="json")
    result["_llm_available"] = False
    return _hold(
        "arif_metabolize",
        reason,
        floors=floors,
        extra_meta={"result": result},
        session_id=session_id,
    )
