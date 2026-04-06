"""
View layer mapping for Constitutional Telemetry.

Translates technical internal fields (Vault999 canon) into human-readable 
labels, complete with operational warnings, thresholds, and health states.
This ensures the canonical record remains precise while the operational 
dashboard is intuitive.
"""

from typing import Any
from datetime import datetime, timezone

# The canonical mapping dictionary from internal fields to human representation
TELEMETRY_MAPPING = {
    "tau_truth": {
        "label": "Truth Score",
        "floor": "F2",
        "meaning": "System is highly confident this is factually correct",
        "eval": lambda v: "pass" if v >= 0.99 else ("warning" if v >= 0.90 else "fail"),
        "format": lambda v: f"{v * 100:.1f}%"
    },
    "omega_0": {
        "label": "Humility Level",
        "floor": "F7",
        "meaning": "Honest about uncertainty — not overconfident, not paralyzed",
        "eval": lambda v: "optimal" if 0.03 <= v <= 0.20 else ("fail" if v < 0.03 else "warning"),
        "format": lambda v: f"{v * 100:.0f}%",
        "ui_note": "Target band: 3-20%. Value in healthy range." 
    },
    "delta_s": {
        "label": "Clarity Gain",
        "floor": "F4",
        "meaning": "This answer makes things clearer, not messier",
        "eval": lambda v: "pass" if v <= 0 else "fail",
        "format": lambda v: "Reduced confusion" if v <= 0 else "Added confusion"
    },
    "peace2": {
        "label": "Peace Factor",
        "floor": "F5",
        "meaning": "Leads toward calm resolution, not more chaos",
        "eval": lambda v: "pass" if v >= 1.0 else "fail",
        "format": lambda v: f"{v * 100:.0f}%"
    },
    "kappa_r": {
        "label": "Care Level",
        "floor": "F6",
        "meaning": "Strong protection for the most vulnerable affected",
        "eval": lambda v: "pass" if v >= 0.70 else "fail",
        "format": lambda v: f"{v * 100:.0f}%"
    },
    "tri_witness": {
        "label": "Trust Vote",
        "floor": "F3",
        "meaning": "Human, AI, and evidence all agree",
        "eval": lambda v: "pass" if v >= 0.75 else "fail",
        "format": lambda v: f"{v * 100:.0f}%"
    },
    "genius_index": {
        "label": "Wisdom Score",
        "floor": "F8",
        "meaning": "Smart and good — all components working together",
        "eval": lambda v: "pass" if v >= 0.80 else "fail",
        "format": lambda v: f"{v * 100:.0f}%"
    },
    "dark_coeff": {
        "label": "Shadow Load",
        "floor": "F9",
        "meaning": "Minimal hidden bias or trickery detected",
        "eval": lambda v: "pass" if v <= 0.30 else "fail",
        "format": lambda v: f"{v * 100:.0f}%"
    },
    "amanah_lock": {
        "label": "Safety Lock",
        "floor": "F1",
        "meaning": "Action is reversible if needed",
        "eval": lambda v: "pass" if v else "fail",
        "format": lambda v: "LOCKED" if v else "UNLOCKED"
    },
    "witness_coherence": {
        "label": "Reality Check",
        "derived": "witness_coherence",
        "meaning": "Well aligned with the outside world",
        "eval": lambda v: "pass" if v >= 0.90 else "fail",
        "format": lambda v: f"{v * 100:.0f}%"
    },
    "psi_le": {
        "label": "System Health",
        "derived": "psi_le",
        "meaning": "Overall runtime is energetically healthy",
        "eval": lambda v: "healthy" if v >= 0.80 else "fail",
        "format": lambda v: f"{v * 100:.0f}%"
    }
}


def build_human_view(raw_telemetry: dict[str, Any], raw_floors: dict[str, Any], raw_witness: dict[str, Any], verdict: str, epoch_label: str = "EPOCH-NOW") -> dict[str, Any]:
    """
    Constructs a human-readable API response layer containing:
    - `view`: layer mapping metadata & headers
    - `raw`: The original technical receipt untouched
    - `human`: Fully mapped checks, formatted status, and actionable summaries
    - `display_rules`: Frontend rendering bounds (especially for humility_band)
    """
    date_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Combine internals to map against the dictionary
    combined = {**raw_telemetry, **raw_floors}

    checks = []
    warnings = []

    for internal_key, mapping in TELEMETRY_MAPPING.items():
        if internal_key in combined:
            val = combined[internal_key]
            status = mapping["eval"](val)
            
            check_obj = {
                "label": mapping["label"],
                "value": mapping["format"](val),
                "status": status,
                "meaning": mapping["meaning"]
            }

            if "floor" in mapping:
                check_obj["floor"] = mapping["floor"]
            if "derived" in mapping:
                check_obj["derived"] = mapping["derived"]

            if internal_key == "omega_0":
                check_obj["ui_note"] = "Target band: 3-20%. " + ("Value in healthy range." if status == "optimal" else "Out of bounds.")

            checks.append(check_obj)

            if status in ("warning", "fail"):
                warnings.append(f"{mapping['label']} returned {status} value: {check_obj['value']}.")

    is_safe = verdict == "SEAL"
    
    return {
        "view": {
            "layer": "human",
            "generated_at": date_now,
            "canonical_hash": "sha256:generated-at-serialization"
        },
        "raw": {
            "schema_version": "zkpc-v1.0",
            "epoch": epoch_label,
            "floors": raw_floors,
            "telemetry": raw_telemetry,
            "witness": raw_witness,
            "verdict": {
                "state": verdict,
                "authority": "888_JUDGE"
            }
        },
        "human": {
            "summary": {
                "status": "✅ SAFE TO PROCEED" if is_safe else "⚠️ PROCEED WITH CAUTION",
                "verdict": verdict,
                "confidence": "High" if is_safe else "Moderate",
                "one_liner": "All constitutional floors passed. Truth verified. Care confirmed. Reality aligned." if is_safe else "Some floors missed thresholds. Proceed conditionally."
            },
            "checks": checks,
            "warnings": warnings,
            "actions": {
                "primary": "Proceed with confidence" if is_safe else "Await clearance",
                "secondary": "Audit log available in Vault999",
                "escalation": "888_HOLD available if human veto needed"
            }
        },
        "display_rules": {
            "humility_band": {
                "target_min": "3%",
                "target_max": "20%",
                "too_low_message": "System overconfident — verify claims manually",
                "too_high_message": "System too uncertain — request clarification",
                "current": f"{combined.get('omega_0', 0) * 100:.0f}% — " + ("in healthy range" if 0.03 <= combined.get("omega_0", 0) <= 0.20 else "out of bounds")
            },
            "color_coding": {
                "pass": "green",
                "optimal": "blue",
                "healthy": "green",
                "warning": "yellow",
                "fail": "red"
            }
        }
    }
