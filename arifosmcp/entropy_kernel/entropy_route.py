"""
arif_entropy_route — Route domain questions to the correct organ.

Routes based on signal class and domain content.
Does NOT produce observations — only routes.
"""

ROUTING_TABLE = {
    "INFORMATION_LOSS": {"primary": "KERNEL", "secondary": "GEOX"},
    "POSSIBILITY_COLLAPSE": {"primary": "WEALTH", "secondary": "GEOX"},
    "FEEDBACK_CORRUPTION": {"primary": "KERNEL", "secondary": "WELL"},
    "DEFENSIVE_OVERHEAD": {"primary": "WELL", "secondary": "WEALTH"},
    "CASCADE_PROPAGATION": {"primary": "GEOX", "secondary": "WEALTH"},
    "CORRECTION_FAILURE": {"primary": "KERNEL", "secondary": "WELL"},
    "BRITTLE_ORDER": {"primary": "ALL", "secondary": None},
}

DOMAIN_KEYWORDS = {
    "WELL": [
        "stress", "fatigue", "sleep", "recovery", "trust", "dignity",
        "vitality", "regulation", "emotion", "burnout", "wellbeing",
        "sabar", "patience", "response latency", "biological",
    ],
    "WEALTH": [
        "incentive", "capital", "profit", "cost", "budget", "metric",
        "KPI", "power", "consequence", "liability", "responsibility",
        "governance", "board", "compensation", "equity", "debt",
    ],
    "GEOX": [
        "physical", "geology", "water", "contamination", "erosion",
        "subsidence", "habitat", "emission", "irreversible", "material",
        "earth", "ecological", "monitoring", "sensor", "measurement",
    ],
    "AFORGE": [
        "implementation", "deployment", "test", "build", "schema",
        "migration", "runtime", "service", "container", "CI/CD",
        "code", "infrastructure", "monitoring", "alert",
    ],
}


def _detect_domain(question: str) -> str | None:
    """Detect domain from question text."""
    q_lower = question.lower()
    scores = {}
    for organ, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in q_lower)
        if score > 0:
            scores[organ] = score
    if scores:
        return max(scores, key=scores.get)
    return None


def arif_entropy_route(
    signal_class: str | None = None,
    question: str | None = None,
    domain_hint: str | None = None,
) -> dict:
    """
    Route domain questions to the correct organ.

    Args:
        signal_class: One of the 7 entropy signal classes
        question: Natural language question to route
        domain_hint: Explicit organ hint (overrides detection)

    Returns:
        {
            "route_to": str,
            "route_secondary": str | None,
            "routing_reason": str,
            "available_tools": [str],
        }
    """
    # Priority: domain_hint > signal_class > question detection
    if domain_hint:
        return {
            "route_to": domain_hint,
            "route_secondary": None,
            "routing_reason": f"Explicit domain hint: {domain_hint}",
            "available_tools": _get_tools(domain_hint),
        }

    if signal_class and signal_class in ROUTING_TABLE:
        route = ROUTING_TABLE[signal_class]
        return {
            "route_to": route["primary"],
            "route_secondary": route["secondary"],
            "routing_reason": f"Signal class {signal_class} routes to {route['primary']}",
            "available_tools": _get_tools(route["primary"]),
        }

    if question:
        detected = _detect_domain(question)
        if detected:
            return {
                "route_to": detected,
                "route_secondary": None,
                "routing_reason": f"Domain keywords detected: {detected}",
                "available_tools": _get_tools(detected),
            }

    # Default to kernel for unclassifiable
    return {
        "route_to": "KERNEL",
        "route_secondary": None,
        "routing_reason": "No clear domain — defaulting to kernel for assessment",
        "available_tools": _get_tools("KERNEL"),
    }


def _get_tools(organ: str) -> list[str]:
    """Return available entropy tools per organ."""
    tools = {
        "KERNEL": [
            "arif_entropy_observe", "arif_j_state_assess", "arif_correction_probe",
            "arif_consequence_trace", "arif_j_gate",
        ],
        "WELL": [
            "well_dark_geometry_mirror", "well_sabar_latency", "well_trust_compression",
            "well_niat_impact_mirror", "well_correction_capacity", "well_regulation_recovery",
        ],
        "WEALTH": [
            "wealth_power_consequence_map", "wealth_metric_purpose_audit",
            "wealth_responsibility_ledger", "wealth_trust_capital_decay",
            "wealth_coercive_order_cost", "wealth_entropy_externality",
        ],
        "GEOX": [
            "geox_consequence_footprint", "geox_optionality_loss",
            "geox_feedback_integrity", "geox_material_truth_challenge",
            "geox_cascade_pathway",
        ],
        "AFORGE": [
            "forge_entropy_schema", "forge_dark_geometry_detector",
            "forge_detector_test_corpus", "forge_counterfactual_test",
            "forge_calibration_report", "forge_prompt_injection_test",
        ],
    }
    return tools.get(organ, [])
