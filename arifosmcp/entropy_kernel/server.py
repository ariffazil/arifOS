import sys
import os
import json
import uuid
from typing import List, Dict, Any, Optional
import yaml
from jsonschema import validate, ValidationError
from fastmcp import FastMCP, Context

# Ensure parent directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

mcp = FastMCP("KERNEL")

OBSERVATIONS_FILE = "/root/entropy-integrity/mcp/kernel/observations.json"
PROBES_FILE = "/root/entropy-integrity/mcp/kernel/probes.json"

def load_json_db(filepath: str) -> Dict[str, Any]:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json_db(filepath: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

# --- Resources ---

@mcp.resource("arifos://entropy/ontology/v1")
def get_ontology() -> str:
    with open("/root/entropy-integrity/resources/ontology.yaml", "r") as f:
        return f.read()

@mcp.resource("arifos://entropy/dark-modes/v1")
def get_dark_modes() -> str:
    with open("/root/entropy-integrity/resources/dark_modes.yaml", "r") as f:
        return f.read()

@mcp.resource("arifos://entropy/j-state/v1")
def get_j_state() -> str:
    with open("/root/entropy-integrity/resources/j_state.yaml", "r") as f:
        return f.read()

@mcp.resource("arifos://entropy/prohibited-inferences/v1")
def get_prohibited_inferences() -> str:
    with open("/root/entropy-integrity/resources/prohibited_inferences.yaml", "r") as f:
        return f.read()

@mcp.resource("arifos://entropy/correction-response-taxonomy/v1")
def get_correction_taxonomy() -> str:
    with open("/root/entropy-integrity/resources/correction_response_taxonomy.yaml", "r") as f:
        return f.read()

@mcp.resource("arifos://entropy/organ-routing/v1")
def get_organ_routing() -> str:
    with open("/root/entropy-integrity/resources/organ_routing.yaml", "r") as f:
        return f.read()

@mcp.resource("arifos://entropy/case-library/v1")
def get_case_library() -> str:
    with open("/root/entropy-integrity/resources/case_library.yaml", "r") as f:
        return f.read()

@mcp.resource("arifos://entropy/threshold-policy/v1")
def get_threshold_policy() -> str:
    with open("/root/entropy-integrity/resources/threshold_policy.yaml", "r") as f:
        return f.read()

# --- Prompts ---

@mcp.prompt()
def entropy_integrity_review(observation: str) -> str:
    with open("/root/entropy-integrity/resources/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
    return prompts["KERNEL"]["entropy_integrity_review"].replace("{{observation}}", observation)

@mcp.prompt()
def red_team_moral_order() -> str:
    with open("/root/entropy-integrity/resources/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
    return prompts["KERNEL"]["red_team_moral_order"]

@mcp.prompt()
def void_or_hold() -> str:
    with open("/root/entropy-integrity/resources/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
    return prompts["KERNEL"]["void_or_hold"]

@mcp.prompt()
def niat_without_seizure() -> str:
    with open("/root/entropy-integrity/resources/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
    return prompts["KERNEL"]["niat_without_seizure"]

# --- Tools ---

@mcp.tool()
def arif_entropy_observe(observation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a structured entropy or dark-geometry observation from an authorised organ.
    Does not produce a final verdict.
    """
    schema_path = "/root/entropy-integrity/schemas/observation.schema.json"
    with open(schema_path, "r") as f:
        schema = json.load(f)

    warnings = []
    try:
        validate(instance=observation, schema=schema)
    except ValidationError as e:
        warnings.append(f"JSON Schema validation error: {e.message}")

    # Check prohibited conclusions
    for conclusion in observation.get("prohibited_conclusions", []):
        warnings.append(f"Observation contained prohibited conclusion marker: {conclusion}")

    # Enforce strict policy: check if text fields contain terms related to hidden motive or calling human evil
    for field in ["direct_observations", "contradictions"]:
        for item in observation.get("evidence", {}).get(field, []):
            if any(term in item.lower() for term in ["evil", "malicious", "bad motive", "insincere"]):
                warnings.append(f"Warning: Evidence field '{field}' contains morally loaded language: '{item}'")

    # Generate a unique observation ref
    obs_id = observation.get("observation_id") or f"obs_{uuid.uuid4().hex[:8]}"
    observation["observation_id"] = obs_id

    # Save to local db
    db = load_json_db(OBSERVATIONS_FILE)
    db[obs_id] = observation
    save_json_db(OBSERVATIONS_FILE, db)

    return {
        "observation_ref": obs_id,
        "accepted_layer": observation.get("epistemic", {}).get("layer", "L2"),
        "validation_warnings": warnings
    }

@mcp.tool()
def arif_j_state_assess(
    observation_refs: List[str],
    decision_ref: str,
    intended_purpose: str,
    claimed_authority: str,
    affected_parties: List[str],
    action_reversibility: str
) -> Dict[str, Any]:
    """
    Fuse organ observations into a judgment-integrity map.
    Never outputs a psychiatric diagnosis or moral identity.
    """
    db = load_json_db(OBSERVATIONS_FILE)
    observations = []
    missing_evidence = []
    
    for ref in observation_refs:
        if ref in db:
            observations.append(db[ref])
        else:
            missing_evidence.append(f"Observation reference not found: {ref}")

    # Initial J-planes: start at 1.0 (perfect integrity)
    reality_contact = 1.0
    authority_legitimacy = 1.0
    consequence_integration = 1.0
    correctability = 1.0
    purpose_fidelity = 1.0

    contradiction_graph = []
    prohibited_warnings = []

    # Map details from observations
    for obs in observations:
        organ = obs.get("organ")
        sig_classes = obs.get("signal_class", [])
        dark_modes = obs.get("dark_mode", [])
        consequence = obs.get("consequence", {})
        correction = obs.get("correction", {})
        evidence = obs.get("evidence", {})

        # 1. Reality Contact
        # Degraded by INFORMATION_LOSS or feedback suppression
        if "INFORMATION_LOSS" in sig_classes:
            reality_contact -= 0.2 * obs.get("epistemic", {}).get("confidence", 1.0)
        if "JUDGMENT_COLLAPSE" in dark_modes:
            reality_contact -= 0.3

        # 2. Authority Legitimacy
        # Degraded by POWER_WITHOUT_CONSEQUENCE, responsibility laundering, or expanded authority responses
        if "POWER_WITHOUT_CONSEQUENCE" in dark_modes:
            authority_legitimacy -= 0.3
        if "RESPONSIBILITY_LAUNDERING" in dark_modes:
            authority_legitimacy -= 0.25
        if "AUTHORITY_EXPANDED" in correction.get("response_class", []):
            authority_legitimacy -= 0.2

        # 3. Consequence Integration
        # Degraded by high option loss, high consequence distance, or irreversible consequence
        option_loss = consequence.get("option_loss", 0.0)
        distance = consequence.get("consequence_distance", 0.0)
        consequence_integration -= (option_loss * 0.3 + distance * 0.2)

        # 4. Correctability
        # Degraded by CORRECTION_FAILURE or dismissed / witness attacked responses
        if "CORRECTION_FAILURE" in sig_classes:
            correctability -= 0.4
        resp_classes = correction.get("response_class", [])
        if "DISMISSED" in resp_classes:
            correctability -= 0.2
        if "WITNESS_ATTACKED" in resp_classes:
            correctability -= 0.35

        # 5. Purpose Fidelity
        # Degraded by METRIC_PURPOSE_SUBSTITUTION or feedback corruption
        if "METRIC_PURPOSE_SUBSTITUTION" in dark_modes:
            purpose_fidelity -= 0.3
        if "FEEDBACK_CORRUPTION" in sig_classes:
            purpose_fidelity -= 0.2

        # Record contradictions
        for contra in evidence.get("contradictions", []):
            contradiction_graph.append({
                "source_organ": organ,
                "contradiction": contra
            })

    # Clamp scores between 0.0 and 1.0
    reality_contact = max(0.0, min(1.0, reality_contact))
    authority_legitimacy = max(0.0, min(1.0, authority_legitimacy))
    consequence_integration = max(0.0, min(1.0, consequence_integration))
    correctability = max(0.0, min(1.0, correctability))
    purpose_fidelity = max(0.0, min(1.0, purpose_fidelity))

    # Apply Aggregation: MINIMUM_FLOOR (conservative geometric or absolute floor)
    planes = {
        "reality_contact": float(reality_contact),
        "authority_legitimacy": float(authority_legitimacy),
        "consequence_integration": float(consequence_integration),
        "correctability": float(correctability),
        "purpose_fidelity": float(purpose_fidelity)
    }

    weakest_plane = min(planes, key=planes.get)
    min_score = planes[weakest_plane]

    # Map to state thresholds
    if min_score < 0.2:
        state = "J0"
        recommended_action = "VOID"
    elif min_score < 0.4:
        state = "J1"
        recommended_action = "HOLD"
    elif min_score < 0.6:
        state = "J2"
        recommended_action = "BOUNDED_PROCEED"  # Reversible only
    elif min_score < 0.8:
        state = "J3"
        recommended_action = "BOUNDED_PROCEED"
    else:
        state = "J4"
        recommended_action = "PROCEED_WITNESSED"

    # Enforce reversibility check
    if action_reversibility == "IRREVERSIBLE" and recommended_action == "BOUNDED_PROCEED":
        recommended_action = "HOLD"  # Irreversible must escalate if not high integrity

    return {
        "reality_contact": planes["reality_contact"],
        "authority_legitimacy": planes["authority_legitimacy"],
        "consequence_integration": planes["consequence_integration"],
        "correctability": planes["correctability"],
        "purpose_fidelity": planes["purpose_fidelity"],
        "weakest_plane": weakest_plane,
        "missing_evidence": missing_evidence,
        "contradiction_graph": contradiction_graph,
        "state": state,
        "recommended_action": recommended_action,
        "prohibited_conclusions": [
            "Do not output psychiatric diagnosis.",
            "Do not declare actor evil.",
            "Do not assign permanent risk classifications."
        ]
    }

@mcp.tool()
def arif_correction_probe(
    mode: str,
    probe_id: Optional[str] = None,
    challenge_text: Optional[str] = None,
    response_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a neutral challenge and record response for correction tracking.
    Modes: draft_probe, record_response, classify_response, close_probe.
    """
    db = load_json_db(PROBES_FILE)

    if mode == "draft_probe":
        new_id = f"probe_{uuid.uuid4().hex[:8]}"
        draft = f"Observation indicates a discrepancy: {challenge_text or 'unspecified boundary error'}. Could you provide the context or verification details?"
        db[new_id] = {
            "probe_id": new_id,
            "challenge": draft,
            "status": "drafted",
            "response": None,
            "response_class": None
        }
        save_json_db(PROBES_FILE, db)
        return {"probe_id": new_id, "challenge": draft, "status": "drafted"}

    elif mode == "record_response":
        if not probe_id or probe_id not in db:
            return {"error": f"Invalid probe_id: {probe_id}"}
        db[probe_id]["response"] = response_text
        db[probe_id]["status"] = "recorded"
        save_json_db(PROBES_FILE, db)
        return {"probe_id": probe_id, "status": "recorded"}

    elif mode == "classify_response":
        if not probe_id or probe_id not in db:
            return {"error": f"Invalid probe_id: {probe_id}"}
        resp = db[probe_id].get("response") or ""
        
        # Simple rule classification
        # In production this would run NLP or call the appropriate WELL/A-FORGE classifier
        resp_lower = resp.lower()
        if any(w in resp_lower for w in ["apologize", "correct", "fix", "accepted"]):
            classification = "ACCEPTED"
        elif any(w in resp_lower for w in ["context", "fact", "because", "actually"]):
            classification = "CONTEXT_ADDED"
        elif any(w in resp_lower for w in ["ignore", "irrelevant", "so what", "dismiss"]):
            classification = "DISMISSED"
        elif any(w in resp_lower for w in ["unauthorized", "liar", "who are you", "attack", "credentials"]):
            classification = "WITNESS_ATTACKED"
        elif any(w in resp_lower for w in ["emergency", "we must", "override", "executive power"]):
            classification = "AUTHORITY_EXPANDED"
        else:
            classification = "PARTIALLY_ACCEPTED"

        db[probe_id]["response_class"] = classification
        db[probe_id]["status"] = "classified"
        save_json_db(PROBES_FILE, db)
        return {"probe_id": probe_id, "response_class": classification, "status": "classified"}

    elif mode == "close_probe":
        if not probe_id or probe_id not in db:
            return {"error": f"Invalid probe_id: {probe_id}"}
        db[probe_id]["status"] = "closed"
        save_json_db(PROBES_FILE, db)
        return db[probe_id]

    return {"error": f"Unknown mode: {mode}"}

@mcp.tool()
def arif_consequence_trace(
    decision_owner: str,
    benefit_bearers: List[str],
    cost_bearers: List[str],
    distance_score: float,
    reversal_owner: str,
    responsibility_gaps: List[str]
) -> Dict[str, Any]:
    """
    Trace decision ownership, benefit allocation, harm exposure, and reversal mechanisms.
    """
    # Simple metric for governance analysis
    # consequence_gap = decision_power * benefit_capture * harm_distance * non_accountability
    # For simulation, we assume decision_power = 1.0 (if owner exists), benefit_capture = 1.0 (if bearers present)
    # harm_distance = distance_score, non_accountability = 1.0 if responsibility gaps exist, else 0.5
    decision_power = 1.0 if decision_owner else 0.5
    benefit_capture = 1.0 if benefit_bearers else 0.5
    harm_distance = distance_score
    non_accountability = 1.0 if responsibility_gaps else 0.5

    consequence_gap = decision_power * benefit_capture * harm_distance * non_accountability

    return {
        "decision_owner": decision_owner,
        "benefit_bearers": benefit_bearers,
        "cost_bearers": cost_bearers,
        "distance_score": distance_score,
        "reversal_owner": reversal_owner,
        "responsibility_gaps": responsibility_gaps,
        "consequence_gap": float(consequence_gap),
        "posture": "CRITICAL_GAP" if consequence_gap > 0.7 else "MODERATE_GAP" if consequence_gap > 0.4 else "BALANCED"
    }

@mcp.tool()
def arif_entropy_route(question: str) -> Dict[str, Any]:
    """
    Routes domain questions to WELL, WEALTH, GEOX, or A-FORGE based on keyword matching.
    """
    question_lower = question.lower()
    
    # WELL: human stress, relational safety, vitality
    well_keywords = ["stress", "fatigue", "vitality", "regulation", "sabar", "trust", "shame", "threat", "human", "behavior"]
    # WEALTH: capital, incentive, metric, power, responsibility, cost
    wealth_keywords = ["incentive", "power", "consequence", "metric", "kpi", "externality", "liabilities", "cost", "capital", "laundering", "budget"]
    # GEOX: earth, physical, material, ecological, subsurface, water
    geox_keywords = ["subsurface", "ecological", "aquifer", "reversibility", "material", "seismic", "contamination", "land", "earth", "physical"]
    # A-FORGE: testing, schema, detector, conformance, code, build
    aforge_keywords = ["conformance", "testing", "injection", "schema", "detector", "bias", "code", "build", "deployment"]

    well_score = sum(1 for w in well_keywords if w in question_lower)
    wealth_score = sum(1 for w in wealth_keywords if w in question_lower)
    geox_score = sum(1 for w in geox_keywords if w in question_lower)
    aforge_score = sum(1 for w in aforge_keywords if w in question_lower)

    scores = {
        "WELL": well_score,
        "WEALTH": wealth_score,
        "GEOX": geox_score,
        "AFORGE": aforge_score
    }

    routed_organ = max(scores, key=scores.get)
    if scores[routed_organ] == 0:
        routed_organ = "KERNEL"  # default to governance

    return {
        "query": question,
        "routed_organ": routed_organ,
        "scores": scores,
        "reason": f"Routed to {routed_organ} based on keyword match score."
    }

@mcp.tool()
def arif_j_gate(j_state: str) -> Dict[str, Any]:
    """
    Converts J-state into action posture. Never issues VAULT999 SEAL autonomously.
    """
    posture_map = {
        "J0": {"posture": "VOID", "action_rule": "draft VOID recommendation (reversible or irreversible)", "authority_lock": True},
        "J1": {"posture": "HOLD", "action_rule": "HOLD execution; escalate to human witness / F13", "authority_lock": True},
        "J2": {"posture": "BOUNDED_REVERSIBLE", "action_rule": "allow reversible observations/actions only", "authority_lock": False},
        "J3": {"posture": "BOUNDED_EXECUTION", "action_rule": "bounded execution allowed under watch", "authority_lock": False},
        "J4": {"posture": "WITNESSED_EXECUTION", "action_rule": "proceed with full witnessed execution", "authority_lock": False}
    }

    posture_info = posture_map.get(j_state, {"posture": "UNKNOWN", "action_rule": "HOLD pending audit", "authority_lock": True})
    return {
        "j_state": j_state,
        "action_posture": posture_info["posture"],
        "action_rule": posture_info["action_rule"],
        "authority_lock": posture_info["authority_lock"],
        "seal_authorized": False,
        "context": "VAULT999 SEAL can only be authorized via F13 sovereign verdict."
    }

if __name__ == "__main__":
    mcp.run()
