"""
Policy Constraint Engine for WEALTH
Enforces hard numeric constraints on allocation decisions.
"""

import math
from typing import Any, Dict, List, Optional

DEFAULT_CONSTRAINTS = {
    "gini_max": 0.40,
    "dscr_min": 1.25,
    "carbon_intensity_max": 0.05,
    "social_stability_min": 0.60,
    "maruah_floor": 0.60,
    "peace2_min": 1.0,
    "entropy_max": 0.30,
    "runway_min_months": 3.0,
    "leverage_max": 0.80,
}


class PolicyEngine:
    """Evaluates allocation proposals against configurable constitutional constraints."""

    def __init__(self, constraints: Optional[Dict[str, float]] = None):
        self.constraints = {**DEFAULT_CONSTRAINTS, **(constraints or {})}

    def evaluate(self, proposal: Dict[str, Any], scale_mode: str = "enterprise") -> Dict[str, Any]:
        flags: List[str] = []
        details: Dict[str, Any] = {}

        # Distributional justice (Gini)
        gini = proposal.get("gini_coefficient")
        if gini is not None and gini > self.constraints["gini_max"]:
            flags.append("GINI_VIOLATION")
            details["gini"] = {"value": gini, "limit": self.constraints["gini_max"]}

        # Debt survivability (DSCR)
        dscr = proposal.get("dscr")
        if dscr is not None and dscr < self.constraints["dscr_min"]:
            flags.append("DSCR_VIOLATION")
            details["dscr"] = {"value": dscr, "limit": self.constraints["dscr_min"]}

        # Ecological boundary (Carbon intensity)
        carbon = proposal.get("carbon_intensity")
        if carbon is not None and carbon > self.constraints["carbon_intensity_max"]:
            flags.append("CARBON_VIOLATION")
            details["carbon_intensity"] = {"value": carbon, "limit": self.constraints["carbon_intensity_max"]}

        # Social stability
        stability = proposal.get("social_stability_index")
        if stability is not None and stability < self.constraints["social_stability_min"]:
            flags.append("STABILITY_VIOLATION")
            details["social_stability"] = {"value": stability, "limit": self.constraints["social_stability_min"]}

        # Maruah / dignity
        maruah = proposal.get("maruah_score")
        if maruah is not None and maruah < self.constraints["maruah_floor"]:
            flags.append("MARUAH_VIOLATION")
            details["maruah"] = {"value": maruah, "limit": self.constraints["maruah_floor"]}

        # Peace / entropy
        peace2 = proposal.get("peace2")
        if peace2 is not None and peace2 < self.constraints["peace2_min"]:
            flags.append("PEACE_VIOLATION")
            details["peace2"] = {"value": peace2, "limit": self.constraints["peace2_min"]}

        entropy = proposal.get("dS")
        if entropy is not None and entropy > self.constraints["entropy_max"]:
            flags.append("ENTROPY_VIOLATION")
            details["entropy"] = {"value": entropy, "limit": self.constraints["entropy_max"]}

        # Liquidity / runway
        runway = proposal.get("runway_months")
        if runway is not None and runway != math.inf and runway < self.constraints["runway_min_months"]:
            flags.append("RUNWAY_VIOLATION")
            details["runway"] = {"value": runway, "limit": self.constraints["runway_min_months"]}

        # Leverage cap
        leverage = proposal.get("leverage_ratio")
        if leverage is not None and leverage > self.constraints["leverage_max"]:
            flags.append("LEVERAGE_VIOLATION")
            details["leverage"] = {"value": leverage, "limit": self.constraints["leverage_max"]}

        # Scale-specific overrides
        if scale_mode == "crisis":
            # In crisis, lower acceptance bars for liquidity but tighten survival constraints
            if "RUNWAY_VIOLATION" in flags:
                # Keep it as a warning unless truly catastrophic (<1 month)
                if runway is not None and runway >= 1.0:
                    flags.remove("RUNWAY_VIOLATION")
                    flags.append("RUNWAY_WARNING")

        if scale_mode == "civilization":
            # For civilization scale, carbon and stability are hard blocks
            if any(f in flags for f in ("CARBON_VIOLATION", "STABILITY_VIOLATION", "MARUAH_VIOLATION")):
                flags = list(dict.fromkeys([*flags, "CIVILIZATION_HARD_BLOCK"]))

        policy_pass = len([f for f in flags if not f.endswith("_WARNING")]) == 0

        return {
            "policy_pass": policy_pass,
            "flags": flags,
            "details": details,
            "constraints_applied": list(self.constraints.keys()),
            "scale_mode": scale_mode,
        }

    def evaluate_envelope(self, envelope: Dict[str, Any], scale_mode: str = "enterprise") -> Dict[str, Any]:
        """Derive a proposal dict from a WEALTH envelope and evaluate it."""
        primary = envelope.get("primary_result", {})
        secondary = envelope.get("secondary_metrics", {})

        proposal = {
            "dscr": primary.get("dscr"),
            "runway_months": primary.get("runway_months") if primary.get("runway_months") is not None else secondary.get("runway_months"),
            "maruah_score": envelope.get("_audit", {}).get("maruah_score"),
            "peace2": envelope.get("_audit", {}).get("peace2"),
            "dS": envelope.get("_audit", {}).get("dS"),
            "gini_coefficient": envelope.get("_audit", {}).get("gini_coefficient"),
            "carbon_intensity": envelope.get("_audit", {}).get("carbon_intensity"),
            "social_stability_index": envelope.get("_audit", {}).get("social_stability_index"),
            "leverage_ratio": envelope.get("_audit", {}).get("leverage_ratio"),
        }

        # Remove None values so defaults don't misfire
        proposal = {k: v for k, v in proposal.items() if v is not None}
        return self.evaluate(proposal, scale_mode)
