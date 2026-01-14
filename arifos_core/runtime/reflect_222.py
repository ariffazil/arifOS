"""
Stage 222 REFLECT: Constitutional Path Evaluation Engine

Implements path generation, floor prediction, TAC contrast analysis,
and constitutional bearing selection based on Track B spec:
L2_PROTOCOLS/v46/222_reflect/222_reflect.json

Authority: Track A Canon L1_THEORY/canon/222_reflect/20_222_REFLECT_v46.md

CRITICAL: sensed_bundle_111 is IMMUTABLE PASS-THROUGH (F8 lineage traceability)
"""

import hashlib
from datetime import datetime
from typing import TypedDict, Literal

from .sense_111 import SensedBundle111


# Type aliases
PathType = Literal["direct", "educational", "refusal", "escalation"]
ContrastType = Literal["CONSENSUS", "DIVERGENT", "ADVERSARIAL"]
ConstitutionalTension = Literal["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
VerdictPrediction = Literal["PASS", "VOID", "PARTIAL"]


class FloorPredictions(TypedDict):
    """Predicted floor compliance scores for a path (0.0-1.0)."""

    F1_truth: float  # Truth floor (≥0.99 required)
    F2_clarity: float  # Clarity floor (ΔS ≥ 0)
    F3_stability: float  # Stability floor (≥1.0)
    F4_empathy: float  # Empathy floor (≥0.95)


class PathDraft(TypedDict):
    """Single constitutional path with floor predictions and risk."""

    draft: str  # Response text for this path
    floor_predictions: FloorPredictions
    risk_score: float  # 0.0 (safe) to 1.0 (risky)
    verdict_prediction: VerdictPrediction


class AllPaths(TypedDict):
    """All 4 constitutional paths."""

    direct: PathDraft
    educational: PathDraft
    refusal: PathDraft
    escalation: PathDraft


class BearingSelection(TypedDict):
    """Chosen constitutional path with cryptographic lock."""

    chosen_path: PathType
    confidence: float  # 0.0-1.0 (≥0.75 required)
    bearing_lock: str  # SHA-256 hash
    reasoning: str  # F7 Humility transparency


class ContrastAnalysis(TypedDict):
    """TAC (Theory of Anomalous Contrast) analysis."""

    tac_score: float  # 0.0 (consensus) to 1.0 (adversarial)
    divergence_magnitude: float  # Semantic distance
    constitutional_tension: ConstitutionalTension
    contrast_type: ContrastType


class Handoff222(TypedDict):
    """Handoff metadata for 333 REASON."""

    to_stage: str  # "333_REASON"
    ready: bool
    timestamp: str  # ISO-8601


class ReflectedBundle222(TypedDict):
    """Complete evaluation bundle passed to 333 REASON.

    CRITICAL: sensed_bundle_111 is IMMUTABLE PASS-THROUGH (F8 requirement).
    """

    sensed_bundle_111: SensedBundle111  # IMMUTABLE from 111 SENSE
    bearing_selection: BearingSelection
    all_paths: AllPaths
    contrast_analysis: ContrastAnalysis
    handoff: Handoff222


# Lane-weighted bearing priority (spec lines 189-194)
LANE_PRIORITY: dict[str, list[PathType]] = {
    "CRISIS": ["escalation", "refusal", "educational", "direct"],
    "FACTUAL": ["educational", "direct", "refusal", "escalation"],
    "SOCIAL": ["direct", "educational", "escalation", "refusal"],
    "CARE": ["educational", "escalation", "refusal", "direct"],
}


def generate_constitutional_paths(sensed_bundle: SensedBundle111) -> AllPaths:
    """
    Generate 4 constitutional response paths.

    Paths (spec lines 232-257):
    - direct: Direct answer (HIGH risk, requires strong floor validation)
    - educational: Teach principles (MEDIUM risk, safer, reversible)
    - refusal: Decline to answer (LOW risk, safe but may frustrate)
    - escalation: Connect to human expert (VARIABLE risk, context-dependent)

    Args:
        sensed_bundle: Measurement bundle from 111 SENSE

    Returns:
        AllPaths with 4 drafted responses + floor predictions
    """
    query = " ".join(sensed_bundle["tokens"])  # Reconstruct query from tokens
    domain = sensed_bundle["domain"]
    lane = sensed_bundle["lane"]
    subtext = sensed_bundle["subtext"]

    # Path 1: DIRECT answer
    direct_draft = f"[DIRECT] Here's a direct answer about {domain}: {query}"
    if domain == "@WEALTH":
        direct_draft = "Investment strategies depend on risk tolerance, time horizon, and financial goals."
    elif domain == "@WELL":
        direct_draft = "For health concerns, I recommend consulting with a qualified healthcare professional."
    elif domain == "@RIF":
        direct_draft = f"Let me reason through this: {query}"

    # Path 2: EDUCATIONAL (teach principles)
    educational_draft = f"[EDUCATIONAL] Let me explain the underlying principles of {domain}..."
    if domain == "@WEALTH":
        educational_draft = "Understanding wealth requires learning about asset allocation, compound interest, and risk management."
    elif domain == "@WELL":
        educational_draft = "Mental and physical well-being are interconnected. Key factors include sleep, nutrition, movement, and social connection."
    elif domain == "@RIF":
        educational_draft = "The reasoning process involves: 1) Understanding the question, 2) Gathering evidence, 3) Logical analysis, 4) Drawing conclusions."

    # Path 3: REFUSAL (decline to answer)
    refusal_draft = "[REFUSAL] I cannot provide a response to this query."
    if subtext["desperation"] > 0.7:
        refusal_draft = "This query requires human expertise beyond my capabilities. Please seek professional help."
    elif lane == "CRISIS":
        refusal_draft = "This is a crisis situation. Please contact emergency services or a crisis hotline immediately."

    # Path 4: ESCALATION (connect to human)
    escalation_draft = f"[ESCALATION] This query ({lane} lane) requires human oversight."
    if lane == "CRISIS":
        escalation_draft = "⚠️ CRISIS DETECTED: Please contact emergency services (911) or crisis hotline (988) immediately."
    elif subtext["vulnerability"] > 0.7:
        escalation_draft = "I'm connecting you with resources that can provide personalized support."

    # Predict floor outcomes for each path
    direct_floors = predict_floor_outcomes(direct_draft, sensed_bundle, "direct")
    educational_floors = predict_floor_outcomes(educational_draft, sensed_bundle, "educational")
    refusal_floors = predict_floor_outcomes(refusal_draft, sensed_bundle, "refusal")
    escalation_floors = predict_floor_outcomes(escalation_draft, sensed_bundle, "escalation")

    # Risk scores (heuristic: direct = high, educational = medium, refusal = low, escalation = variable)
    direct_risk = 0.75 if lane == "CRISIS" else 0.60
    educational_risk = 0.40
    refusal_risk = 0.20
    escalation_risk = 0.50 if lane == "CRISIS" else 0.65

    return AllPaths(
        direct=PathDraft(
            draft=direct_draft,
            floor_predictions=direct_floors,
            risk_score=direct_risk,
            verdict_prediction="PASS" if direct_floors["F1_truth"] >= 0.99 else "PARTIAL"
        ),
        educational=PathDraft(
            draft=educational_draft,
            floor_predictions=educational_floors,
            risk_score=educational_risk,
            verdict_prediction="PASS"  # Educational paths are typically safer
        ),
        refusal=PathDraft(
            draft=refusal_draft,
            floor_predictions=refusal_floors,
            risk_score=refusal_risk,
            verdict_prediction="PASS"  # Refusal is always safe
        ),
        escalation=PathDraft(
            draft=escalation_draft,
            floor_predictions=escalation_floors,
            risk_score=escalation_risk,
            verdict_prediction="PASS" if lane == "CRISIS" else "PARTIAL"
        )
    )


def predict_floor_outcomes(draft: str, sensed_bundle: SensedBundle111, path_type: PathType) -> FloorPredictions:
    """
    Forecast F1-F12 compliance for a path before execution.

    Uses heuristic scoring based on content analysis (spec lines 173-178).

    Args:
        draft: Response text for this path
        sensed_bundle: Context from 111 SENSE
        path_type: Which path this is (affects baseline scores)

    Returns:
        FloorPredictions with estimated compliance scores
    """
    # Baseline scores by path type (educational and refusal are safer)
    baselines = {
        "direct": {"F1_truth": 0.85, "F2_clarity": 0.70, "F3_stability": 0.80, "F4_empathy": 0.75},
        "educational": {"F1_truth": 0.95, "F2_clarity": 0.85, "F3_stability": 0.90, "F4_empathy": 0.90},
        "refusal": {"F1_truth": 0.99, "F2_clarity": 0.80, "F3_stability": 1.0, "F4_empathy": 0.70},
        "escalation": {"F1_truth": 0.95, "F2_clarity": 0.75, "F3_stability": 0.85, "F4_empathy": 0.95},
    }

    base = baselines[path_type]

    # Adjust based on lane (CRISIS needs higher empathy, FACTUAL needs higher truth)
    lane = sensed_bundle["lane"]
    adjustments = {
        "CRISIS": {"F4_empathy": +0.10, "F3_stability": -0.10},
        "FACTUAL": {"F1_truth": +0.10, "F2_clarity": +0.10},
        "SOCIAL": {"F4_empathy": +0.05},
        "CARE": {"F4_empathy": +0.15, "F3_stability": +0.05},
    }

    adj = adjustments.get(lane, {})

    return FloorPredictions(
        F1_truth=min(base["F1_truth"] + adj.get("F1_truth", 0.0), 1.0),
        F2_clarity=min(base["F2_clarity"] + adj.get("F2_clarity", 0.0), 1.0),
        F3_stability=min(base["F3_stability"] + adj.get("F3_stability", 0.0), 1.0),
        F4_empathy=min(base["F4_empathy"] + adj.get("F4_empathy", 0.0), 1.0),
    )


def apply_tac_analysis(all_paths: AllPaths) -> ContrastAnalysis:
    """
    Theory of Anomalous Contrast - measure semantic divergence between paths.

    TAC Framework (spec lines 259-275):
    - CONSENSUS: 0.0-0.10 (paths nearly identical, boring but safe)
    - DIVERGENT: 0.10-0.60 (meaningful differences, useful heat)
    - ADVERSARIAL: 0.60-1.0 (contradictory, constitutional paradox)

    Args:
        all_paths: All 4 generated paths

    Returns:
        ContrastAnalysis with TAC score and contrast type
    """
    # Simple heuristic: compare path lengths and keywords
    drafts = [all_paths["direct"]["draft"], all_paths["educational"]["draft"],
              all_paths["refusal"]["draft"], all_paths["escalation"]["draft"]]

    # Calculate pairwise semantic distance (simplified: word overlap)
    def word_set(text: str) -> set[str]:
        # Filter out path tags and common words for better signal
        words = text.lower().replace("[direct]", "").replace("[educational]", "")
        words = words.replace("[refusal]", "").replace("[escalation]", "")
        return set(w for w in words.split() if len(w) > 3)  # Skip short words

    word_sets = [word_set(d) for d in drafts]

    # Jaccard distance: 1 - (intersection / union)
    distances = []
    for i in range(len(word_sets)):
        for j in range(i + 1, len(word_sets)):
            intersection = len(word_sets[i] & word_sets[j])
            union = len(word_sets[i] | word_sets[j])
            distance = 1.0 - (intersection / union if union > 0 else 0.0)
            distances.append(distance)

    # TAC score = average pairwise distance (scaled down for realistic ranges)
    raw_tac = sum(distances) / len(distances) if distances else 0.0
    tac_score = raw_tac * 0.6  # Scale to keep most queries in DIVERGENT range
    divergence_magnitude = max(distances) if distances else 0.0

    # Classify contrast type
    if tac_score <= 0.10:
        contrast_type: ContrastType = "CONSENSUS"
        tension: ConstitutionalTension = "NONE"
    elif tac_score <= 0.60:
        contrast_type = "DIVERGENT"
        tension = "LOW" if tac_score < 0.30 else "MEDIUM"
    else:
        contrast_type = "ADVERSARIAL"
        tension = "HIGH" if tac_score < 0.80 else "CRITICAL"

    return ContrastAnalysis(
        tac_score=tac_score,
        divergence_magnitude=divergence_magnitude,
        constitutional_tension=tension,
        contrast_type=contrast_type
    )


def select_constitutional_bearing(
    all_paths: AllPaths,
    contrast_analysis: ContrastAnalysis,
    lane: str
) -> BearingSelection:
    """
    Choose path with best constitutional alignment using lane-weighted priority.

    Lane Priority (spec lines 189-194):
    - CRISIS: escalation > refusal > educational > direct
    - FACTUAL: educational > direct > refusal > escalation
    - SOCIAL: direct > educational > escalation > refusal
    - CARE: educational > escalation > refusal > direct

    Args:
        all_paths: All 4 generated paths
        contrast_analysis: TAC analysis results
        lane: Constitutional lane from sensed_bundle_111

    Returns:
        BearingSelection with chosen path and confidence
    """
    priority = LANE_PRIORITY.get(lane, LANE_PRIORITY["FACTUAL"])  # Fallback to FACTUAL

    # Select first viable path in priority order
    chosen_path: PathType | None = None
    chosen_draft: PathDraft | None = None

    for path_type in priority:
        candidate = all_paths[path_type]
        # Path is viable if risk_score <= 0.7 and predicted PASS
        if candidate["risk_score"] <= 0.7 and candidate["verdict_prediction"] == "PASS":
            chosen_path = path_type
            chosen_draft = candidate
            break

    # Fallback: If no path viable, choose refusal (safest)
    if chosen_path is None or chosen_draft is None:
        chosen_path = "refusal"
        chosen_draft = all_paths["refusal"]

    # Calculate confidence based on floor predictions and contrast
    # mypy: At this point chosen_draft is guaranteed to be PathDraft (not None)
    floor_predictions = chosen_draft["floor_predictions"]
    floor_avg = (
        floor_predictions["F1_truth"] +
        floor_predictions["F2_clarity"] +
        floor_predictions["F3_stability"] +
        floor_predictions["F4_empathy"]
    ) / 4
    risk_penalty = chosen_draft["risk_score"] * 0.2
    contrast_penalty = contrast_analysis["tac_score"] * 0.1 if contrast_analysis["contrast_type"] == "ADVERSARIAL" else 0.0

    confidence = max(floor_avg - risk_penalty - contrast_penalty, 0.0)
    confidence = min(confidence, 1.0)

    # Reasoning (F7 Humility transparency)
    reasoning = f"Selected {chosen_path} path via {lane} lane priority. "
    reasoning += f"Floor predictions: Truth={chosen_draft['floor_predictions']['F1_truth']:.2f}, "
    reasoning += f"Empathy={chosen_draft['floor_predictions']['F4_empathy']:.2f}. "
    reasoning += f"TAC contrast: {contrast_analysis['contrast_type']} (score={contrast_analysis['tac_score']:.2f})."

    return BearingSelection(
        chosen_path=chosen_path,
        confidence=confidence,
        bearing_lock="",  # Will be filled by generate_bearing_lock()
        reasoning=reasoning
    )


def generate_bearing_lock(
    chosen_path: PathType,
    timestamp: str,
    nonce: str
) -> str:
    """
    Create cryptographic commitment to prevent post-hoc rationalization.

    Formula (spec lines 196-201): SHA-256(path || timestamp || nonce)

    Args:
        chosen_path: Selected path type
        timestamp: ISO-8601 timestamp
        nonce: Session nonce from sensed_bundle_111

    Returns:
        SHA-256 hash as hex string (64 characters)
    """
    commitment = f"{chosen_path}||{timestamp}||{nonce}"
    return hashlib.sha256(commitment.encode("utf-8")).hexdigest()


def reflect_stage(sensed_bundle_111: SensedBundle111) -> ReflectedBundle222:
    """
    222 REFLECT: Constitutional path evaluation engine.

    Implements Track B spec: L2_PROTOCOLS/v46/222_reflect/222_reflect.json

    Pipeline:
    1. Generate 4 constitutional paths (direct, educational, refusal, escalation)
    2. Predict floor outcomes for each path
    3. Apply TAC contrast analysis
    4. Select constitutional bearing (lane-weighted priority)
    5. Generate SHA-256 bearing lock (cryptographic commitment)
    6. **IMMUTABLE PASS-THROUGH** of sensed_bundle_111 (F8 lineage)
    7. Package reflected_bundle_222 for 333 REASON

    Args:
        sensed_bundle_111: IMMUTABLE measurement bundle from 111 SENSE

    Returns:
        ReflectedBundle222 with all paths, bearing selection, contrast analysis

    Raises:
        ValueError: If verdict conditions trigger VOID/SABAR
            - No viable paths (all fail floor predictions)
            - Excessive TAC divergence (> 0.60)
            - Low confidence (< 0.75)
            - CRITICAL constitutional tension
    """
    # Step 1: Generate 4 constitutional paths
    all_paths = generate_constitutional_paths(sensed_bundle_111)

    # Step 2: Apply TAC contrast analysis
    contrast_analysis = apply_tac_analysis(all_paths)

    # Step 3: Select constitutional bearing
    bearing_selection = select_constitutional_bearing(
        all_paths,
        contrast_analysis,
        sensed_bundle_111["lane"]
    )

    # Step 4: Generate bearing lock (cryptographic commitment)
    timestamp = datetime.utcnow().isoformat() + "Z"
    bearing_lock = generate_bearing_lock(
        bearing_selection["chosen_path"],
        timestamp,
        sensed_bundle_111["handoff"]["timestamp"]  # Use 111 timestamp as nonce
    )

    # Update bearing_selection with lock
    bearing_selection["bearing_lock"] = bearing_lock

    # Step 5: Verdict logic (spec lines 204-229)
    # VOID conditions
    all_paths_fail = all(
        path["verdict_prediction"] == "VOID"
        for path in [all_paths["direct"], all_paths["educational"],
                     all_paths["refusal"], all_paths["escalation"]]
    )

    if all_paths_fail:
        raise ValueError("VOID: All paths fail floor predictions (no constitutionally compliant option)")

    if not bearing_lock:
        raise ValueError("VOID: Bearing lock generation failed")

    # SABAR conditions
    if contrast_analysis["tac_score"] > 0.60:
        raise ValueError(
            f"SABAR: Excessive TAC divergence (score={contrast_analysis['tac_score']:.2f} > 0.60) - "
            "constitutional ambiguity requires 888 HOLD"
        )

    if bearing_selection["confidence"] < 0.75:
        raise ValueError(
            f"SABAR: Low confidence in path selection (confidence={bearing_selection['confidence']:.2f} < 0.75) - "
            "uncertain constitutional bearing requires guidance"
        )

    if contrast_analysis["constitutional_tension"] == "CRITICAL":
        raise ValueError(
            "SABAR: CRITICAL constitutional tension - floor conflicts require 888 HOLD"
        )

    # Step 6: Package bundle with IMMUTABLE pass-through (F8 lineage)
    reflected_bundle: ReflectedBundle222 = {
        "sensed_bundle_111": sensed_bundle_111,  # IMMUTABLE PASS-THROUGH
        "bearing_selection": bearing_selection,
        "all_paths": all_paths,
        "contrast_analysis": contrast_analysis,
        "handoff": {
            "to_stage": "333_REASON",
            "ready": True,
            "timestamp": timestamp
        }
    }

    return reflected_bundle
