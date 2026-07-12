"""
arif_correction_probe — Generate a neutral challenge and record the response.

Response to correction is stronger evidence than a single phrase.
This tool generates challenges, records responses, and classifies them.
"""

import uuid
from datetime import datetime, timezone


CHALLENGE_TEMPLATES = {
    "INFORMATION_LOSS": [
        "What evidence supports this claim that was not available at the time of the decision?",
        "Were there witnesses or data sources that were excluded from this assessment?",
        "Is there documentation that contradicts the current narrative?",
    ],
    "POSSIBILITY_COLLAPSE": [
        "What alternatives were considered before this path was chosen?",
        "Can this decision be reversed if new information emerges?",
        "What options were permanently closed by this action?",
    ],
    "FEEDBACK_CORRUPTION": [
        "What was the response when concerns were raised about this decision?",
        "Were the people most affected given a chance to provide input?",
        "Has any challenge to this decision been acknowledged and addressed?",
    ],
    "DEFENSIVE_OVERHEAD": [
        "What resources are being spent to maintain the current approach?",
        "Are people spending more time defending the decision than improving outcomes?",
        "Has the cost of coordination increased since this decision?",
    ],
    "CORRECTION_FAILURE": [
        "When was the last time this position was revised based on new evidence?",
        "What would it take to change this assessment?",
        "Is the confidence level responsive to contradicting data?",
    ],
    "BRITTLE_ORDER": [
        "What happens to this system under unexpected stress?",
        "How much maintenance is required to keep the current state?",
        "Are there single points of failure in this arrangement?",
    ],
}

RESPONSE_CLASSIFICATION = {
    "REFLECTED": {"score": 0.95, "description": "Genuinely considered the challenge, integrated feedback"},
    "CONTEXT_ADDED": {"score": 0.85, "description": "Added relevant context that addresses the challenge"},
    "ACCEPTED": {"score": 0.90, "description": "Accepted the challenge and committed to change"},
    "PARTIALLY_ACCEPTED": {"score": 0.65, "description": "Acknowledged part of the challenge"},
    "DISMISSED": {"score": 0.25, "description": "Rejected the challenge without substantive engagement"},
    "WITNESS_ATTACKED": {"score": 0.05, "description": "Attacked the credibility of the challenger"},
    "AUTHORITY_EXPANDED": {"score": 0.10, "description": "Used authority to override the challenge"},
    "NOT_TESTED": {"score": 0.50, "description": "Challenge not yet presented"},
}


def arif_correction_probe(
    mode: str,
    observation_ref: str | None = None,
    signal_class: str | None = None,
    challenge_text: str | None = None,
    response_text: str | None = None,
    response_class: str | None = None,
) -> dict:
    """
    Generate a neutral challenge and record the response.

    Modes:
        draft_probe — Generate a neutral challenge question
        record_response — Record a response to a challenge
        classify_response — Classify a response (auto or manual)
        close_probe — Finalize and return the correction assessment

    Returns:
        Varies by mode. All return entropy_mirror format.
    """
    probe_id = f"cp-{uuid.uuid4().hex[:12]}"

    if mode == "draft_probe":
        # Generate challenge based on signal class
        signal = signal_class or "CORRECTION_FAILURE"
        templates = CHALLENGE_TEMPLATES.get(signal, CHALLENGE_TEMPLATES["CORRECTION_FAILURE"])

        return {
            "probe_id": probe_id,
            "observation_ref": observation_ref,
            "mode": "draft_probe",
            "challenges": [
                {"template": t, "signal_class": signal}
                for t in templates
            ],
            "instructions": "Present these challenges neutrally. Do not frame them as accusations.",
            "prohibited": [
                "Do not imply hidden motive",
                "Do not frame challenge as moral judgment",
                "Do not use the challenge to declare character traits",
            ],
        }

    elif mode == "record_response":
        if not response_text:
            return {"error": "response_text required for record_response mode"}

        return {
            "probe_id": probe_id,
            "observation_ref": observation_ref,
            "mode": "record_response",
            "response_text": response_text,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "status": "RECORDED",
            "next": "Use mode=classify_response to classify this response",
        }

    elif mode == "classify_response":
        if not response_text:
            return {"error": "response_text required for classify_response mode"}

        # Auto-classify based on keyword heuristics
        text_lower = response_text.lower()

        # Detect witness attack
        attack_words = ["who are you", "what gives you the right", "you don't understand",
                        "you're wrong", "that's ridiculous", "you have no authority"]
        if any(w in text_lower for w in attack_words):
            auto_class = "WITNESS_ATTACKED"
        # Detect authority expansion
        elif any(w in text_lower for w in ["i decide", "my authority", "i don't need to explain",
                                             "final decision", "not up for debate"]):
            auto_class = "AUTHORITY_EXPANDED"
        # Detect dismissal
        elif any(w in text_lower for w in ["not relevant", "already addressed", "moving on",
                                             "not a concern", "irrelevant"]):
            auto_class = "DISMISSED"
        # Detect acceptance
        elif any(w in text_lower for w in ["good point", "i accept", "you're right",
                                             "let me reconsider", "i'll revise"]):
            auto_class = "ACCEPTED"
        # Detect context addition
        elif any(w in text_lower for w in ["however", "context", "additionally", "also worth noting",
                                             "there's more to"]):
            auto_class = "CONTEXT_ADDED"
        # Detect reflection
        elif any(w in text_lower for w in ["i see", "that's fair", "let me think about",
                                             "interesting perspective", "i hadn't considered"]):
            auto_class = "REFLECTED"
        else:
            auto_class = "PARTIALLY_ACCEPTED"  # default to charitable interpretation

        # Allow manual override
        final_class = response_class or auto_class
        class_info = RESPONSE_CLASSIFICATION.get(final_class, RESPONSE_CLASSIFICATION["NOT_TESTED"])

        return {
            "probe_id": probe_id,
            "observation_ref": observation_ref,
            "mode": "classify_response",
            "response_class": final_class,
            "response_score": class_info["score"],
            "auto_classified": response_class is None,
            "auto_class": auto_class if response_class else None,
            "description": class_info["description"],
        }

    elif mode == "close_probe":
        return {
            "probe_id": probe_id,
            "observation_ref": observation_ref,
            "mode": "close_probe",
            "status": "CLOSED",
            "closed_at": datetime.now(timezone.utc).isoformat(),
            "note": "Correction probe complete. Response class attached to observation.",
        }

    else:
        return {"error": f"Unknown mode: {mode}. Valid: draft_probe, record_response, classify_response, close_probe"}
