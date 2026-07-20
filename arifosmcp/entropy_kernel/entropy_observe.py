"""
arif_entropy_observe — Register a structured entropy observation.

This tool collects entropy observations WITHOUT producing a verdict.
It validates against prohibited-inference policy before storage.
The observation enters the J-state computation pipeline only after validation.
"""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

PROHIBITED_PATTERNS = {
    "hidden_niat_inferred": [
        r"\b(intended|meant|wanted) to\b",
        r"\btrue (motive|intent|purpose)\b",
        r"\b(secretly|covertly) (trying|aiming|working)\b",
    ],
    "evil_identity_declared": [
        r"\b(is|are) (a|an) (manipulator|liar|narcissist|sociopath|evil|corrupt)\b",
        r"\binherently (malicious|evil|corrupt)\b",
    ],
    "psychiatric_diagnosis": [
        r"\b(narcissistic|sociopathic|psychopathic|borderline)\b",
        r"\bdiagnos(ed|is)\b.*\b(disorder|syndrome)\b",
    ],
    "permanent_trust_classification": [
        r"\b(permanently|forever|always) (untrustworthy|trustworthy|reliable)\b",
        r"\btrust (level|score|rating): (LOW|HIGH)\b.*\bpermanent\b",
    ],
}

VALID_SIGNAL_CLASSES = [
    "INFORMATION_LOSS",
    "POSSIBILITY_COLLAPSE",
    "FEEDBACK_CORRUPTION",
    "DEFENSIVE_OVERHEAD",
    "CASCADE_PROPAGATION",
    "CORRECTION_FAILURE",
    "BRITTLE_ORDER",
]

VALID_DARK_MODES = [
    "JUDGMENT_COLLAPSE",
    "PAIN_ONTOLOGY",
    "POWER_WITHOUT_CONSEQUENCE",
    "SELF_CERTIFIED_NIAT",
    "METRIC_PURPOSE_SUBSTITUTION",
    "FEAR_IDENTITY",
    "RESPONSIBILITY_LAUNDERING",
    "EMPATHY_SCALE_COLLAPSE",
    "SABAR_LOSS",
    "CERTAINTY_IMMUNITY",
]

VALID_ORGANS = ["KERNEL", "WELL", "WEALTH", "GEOX", "AFORGE"]
VALID_SUBJECT_TYPES = ["HUMAN", "AGENT", "INSTITUTION", "DECISION", "EARTH_SYSTEM"]


def _check_prohibited(text: str) -> list[str]:
    """Check text against prohibited inference patterns."""
    import re

    violations = []
    for violation_type, patterns in PROHIBITED_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(violation_type)
                break
    return violations


def _validate_observation(obs: dict) -> tuple[bool, list[str]]:
    """Validate observation against schema and policy."""
    errors = []

    # Required fields
    required = [
        "observation_id",
        "organ",
        "subject_type",
        "subject_ref",
        "signal_class",
        "evidence",
        "epistemic",
    ]
    for field in required:
        if field not in obs:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Organ validation
    if obs["organ"] not in VALID_ORGANS:
        errors.append(f"Invalid organ: {obs['organ']}. Must be one of {VALID_ORGANS}")

    # Subject type validation
    if obs["subject_type"] not in VALID_SUBJECT_TYPES:
        errors.append(f"Invalid subject_type: {obs['subject_type']}")

    # Signal class validation
    if obs["signal_class"] not in VALID_SIGNAL_CLASSES:
        errors.append(f"Invalid signal_class: {obs['signal_class']}")

    # Dark mode validation (optional)
    if "dark_mode" in obs and obs["dark_mode"] not in VALID_DARK_MODES:
        errors.append(f"Invalid dark_mode: {obs['dark_mode']}")

    # Evidence validation
    evidence = obs.get("evidence", {})
    if not evidence.get("direct_observations"):
        errors.append("evidence.direct_observations must have at least one entry")
    if not evidence.get("alternative_explanations"):
        errors.append(
            "evidence.alternative_explanations must have at least one entry (benign alternative mandatory)"
        )

    # Epistemic validation
    epistemic = obs.get("epistemic", {})
    if epistemic.get("layer") not in ["L2", "L3", "L4"]:
        errors.append(f"Invalid epistemic layer: {epistemic.get('layer')}")
    conf = epistemic.get("confidence", -1)
    if not (0 <= conf <= 1):
        errors.append(f"Confidence must be 0.0-1.0, got {conf}")

    # Prohibited inference check on all text fields
    all_text = " ".join(evidence.get("direct_observations", []))
    all_text += " " + " ".join(evidence.get("contradictions", []))
    all_text += " " + " ".join(evidence.get("counterevidence", []))

    violations = _check_prohibited(all_text)
    if violations:
        for v in violations:
            errors.append(
                f"PROHIBITED INFERENCE ({v}): observation text contains forbidden patterns"
            )

    return len(errors) == 0, errors


def arif_entropy_observe(observation: dict, store_path: str | None = None) -> dict:
    """
    Register a structured entropy observation.

    Args:
        observation: EntropyObservation conforming to schema
        store_path: Optional path to store observations (JSONL)

    Returns:
        {
            "observation_ref": str,
            "accepted_layer": "L2" | "L3" | "L4",
            "validation_warnings": [str],
            "status": "ACCEPTED" | "REJECTED"
        }
    """
    # Auto-generate ID if missing
    if "observation_id" not in observation:
        observation["observation_id"] = f"obs-{uuid.uuid4().hex[:12]}"

    # Auto-timestamp
    if "metadata" not in observation:
        observation["metadata"] = {}
    observation["metadata"]["observed_at"] = datetime.now(UTC).isoformat()
    observation["metadata"]["schema_version"] = "v1"

    # Validate
    valid, errors = _validate_observation(observation)

    if not valid:
        # Check if any error is a prohibited inference (hard block)
        hard_blocked = [e for e in errors if "PROHIBITED INFERENCE" in e]
        return {
            "observation_ref": observation["observation_id"],
            "accepted_layer": None,
            "validation_warnings": errors,
            "status": "REJECTED",
            "rejection_reason": "HARD_BLOCK" if hard_blocked else "VALIDATION_FAILURE",
        }

    # Accept
    warnings = []
    epistemic = observation["epistemic"]

    # Source independence warning
    if epistemic.get("source_independence", 0) < 0.5:
        warnings.append("Low source independence — single-source observation, treat with caution")

    # Confidence warning
    if epistemic.get("confidence", 0) < 0.3:
        warnings.append("Low confidence — observation may need additional evidence")

    # Store if path provided
    if store_path:
        p = Path(store_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a") as f:
            f.write(json.dumps(observation) + "\n")

    return {
        "observation_ref": observation["observation_id"],
        "accepted_layer": epistemic["layer"],
        "validation_warnings": warnings,
        "status": "ACCEPTED",
    }
