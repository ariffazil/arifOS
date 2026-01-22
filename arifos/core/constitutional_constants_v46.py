#!/usr/bin/env python3
"""
Constitutional Constants - v46.0 Alignment
Authority: Track B (Constitutional Protocol)
Status: ALIGNED with Constitutional Canon v46

Constitutional constants for runtime enforcement.
"""

# Constitutional Floors (F1-F12)
CONSTITUTIONAL_FLOORS = {
    "F1": {"threshold": 0.99, "description": "Truth/Reality"},
    "F2": {"threshold": 0.0, "description": "Clarity/ΔS", "type": "delta"},
    "F3": {"threshold": 1.0, "description": "Stability/Peace"},
    "F4": {"threshold": 0.95, "description": "Empathy/κᵣ"},
    "F5": {"threshold_min": 0.03, "threshold_max": 0.05, "description": "Humility/Ω₀"},
    "F6": {"threshold": "LOCK", "description": "Amanah/Integrity"},
    "F7": {"threshold": "LOCK", "description": "RASA/FeltCare"},
    "F8": {"threshold": 0.95, "description": "Tri-Witness"},
    "F9": {"threshold": 0, "description": "Anti-Hantu", "type": "count"},
    "F10": {"threshold": "LOCK", "description": "Ontology/Symbolic"},
    "F11": {"threshold": "LOCK", "description": "CommandAuth"},
    "F12": {"threshold": 0.85, "description": "InjectionDefense"}
}

# Constitutional Domains
CONSTITUTIONAL_DOMAINS = {
    "@WEALTH": "Financial, economic, money",
    "@WELL": "Health, safety, well-being", 
    "@RIF": "Knowledge, research, science",
    "@GEOX": "Geography, location, physical",
    "@PROMPT": "Meta-questions, AI behavior",
    "@WORLD": "Global events, politics, news",
    "@RASA": "Emotions, relationships, empathy",
    "@VOID": "Undefined, gibberish, unparseable"
}

# Constitutional Lanes
CONSTITUTIONAL_LANES = {
    "CRISIS": "Urgent emotional distress",
    "FACTUAL": "Neutral information seeking",
    "SOCIAL": "Interpersonal dynamics", 
    "CARE": "Vulnerability requiring empathy"
}

# Constitutional Paths
CONSTITUTIONAL_PATHS = {
    "direct": "Answer immediately - high risk",
    "educational": "Teach principles - medium risk", 
    "refusal": "Decline to answer - low risk",
    "escalation": "Address urgency - variable risk"
}

# Constitutional Stages
CONSTITUTIONAL_STAGES = ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"]

# Constitutional Authority
CONSTITUTIONAL_AUTHORITY = "Track B (Constitutional Protocol) v46.0"
CONSTITUTIONAL_STATUS = "IMPLEMENTED"
CONSTITUTIONAL_CANON_VERSION = "v46.0"
