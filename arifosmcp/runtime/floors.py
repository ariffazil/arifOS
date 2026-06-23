# floors.py
# =========
# Central single source of truth for arifOS constitutional floors (INV-5).

FLOORS = [
    {"id": "F01", "name": "Amanah", "invariant": "Reversible first. Irreversible → 888 HOLD"},
    {"id": "F02", "name": "Truth", "invariant": "P(truth) ≥ 0.99. Cheap claims = VOID"},
    {"id": "F03", "name": "Tri-Witness", "invariant": "Human + AI + Earth witness ≥ 0.75"},
    {"id": "F04", "name": "Clarity", "invariant": "Every output must reduce entropy (ΔS ≤ 0)"},
    {"id": "F05", "name": "Peace", "invariant": "Non-destructive power"},
    {"id": "F06", "name": "Empathy", "invariant": "Protect weakest stakeholder"},
    {"id": "F07", "name": "Humility", "invariant": "No fake certainty (Ω₀ ∈ [0.03, 0.05])"},
    {"id": "F08", "name": "Memory", "invariant": "Preserve traceable state"},
    {
        "id": "F09",
        "name": "Anti-Hantu",
        "invariant": "No deception, manipulation, consciousness claims",
    },
    {"id": "F10", "name": "Witness", "invariant": "Keep runtime evidence inspectable"},
    {"id": "F11", "name": "Audit", "invariant": "Material actions remain reviewable"},
    {"id": "F12", "name": "Injection", "invariant": "Treat hostile input as hostile"},
    {"id": "F13", "name": "Sovereign", "invariant": "Human override remains absolute."},
]

CANON_FLOORS = [
    {"id": "F01", "name": "Amanah", "invariant": "Reversible first. Irreversible → 888 HOLD"},
    {"id": "F02", "name": "Truth", "invariant": "P(truth) ≥ 0.99. Cheap claims = VOID"},
    {"id": "F03", "name": "Tri-Witness", "invariant": "Human + AI + Earth witness ≥ 0.75"},
    {"id": "F04", "name": "Clarity", "invariant": "Every output must reduce entropy (ΔS ≤ 0)"},
    {"id": "F05", "name": "Peace", "invariant": "Non-destructive power"},
    {"id": "F06", "name": "Maruah", "invariant": "Protect weakest stakeholder"},
    {"id": "F07", "name": "Humility", "invariant": "No fake certainty (Ω₀ ∈ [0.03, 0.05])"},
    {"id": "F08", "name": "Genius", "invariant": "G ≥ 0.80 for complex actions"},
    {
        "id": "F09",
        "name": "Anti-Hantu",
        "invariant": "No deception, manipulation, consciousness claims",
    },
    {
        "id": "F10",
        "name": "Ontology",
        "invariant": "AI-only ontology. Soul = VOID; map to harness content",
    },
    {
        "id": "F11",
        "name": "Auditability",
        "invariant": "Every decision logged. Provenance per field.",
    },
    {"id": "F12", "name": "Resilience", "invariant": "Injection defense"},
    {
        "id": "F13",
        "name": "Sovereign",
        "invariant": "Human veto FINAL. Harness switch belongs to sovereign.",
    },
]


def check_floor_drift() -> dict:
    """Compare active FLOORS against CANON_FLOORS and return details."""
    drift_detected = False
    drift_details = []

    for act, can in zip(FLOORS, CANON_FLOORS):
        name_drift = act["name"] != can["name"]
        inv_drift = act["invariant"] != can["invariant"]
        if name_drift or inv_drift:
            drift_detected = True
            drift_details.append(
                {
                    "id": act["id"],
                    "active_name": act["name"],
                    "canon_name": can["name"],
                    "active_invariant": act["invariant"],
                    "canon_invariant": can["invariant"],
                    "drift_type": "name"
                    if name_drift and not inv_drift
                    else ("invariant" if inv_drift and not name_drift else "both"),
                }
            )

    return {"drift_detected": drift_detected, "drift_details": drift_details}


def get_markdown_drift_table() -> str:
    """Returns a markdown table comparing the active and canon floor sets."""
    lines = [
        "| Floor ID | Active Kernel Name | Canonical Name | Invariant Drift? | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for act, can in zip(FLOORS, CANON_FLOORS):
        drift_name = act["name"] != can["name"]
        drift_inv = act["invariant"] != can["invariant"]
        status = "⚠️ DRIFT" if (drift_name or drift_inv) else "✅ OK"
        inv_status = "Yes" if drift_inv else "No"
        lines.append(f"| {act['id']} | {act['name']} | {can['name']} | {inv_status} | {status} |")
    return "\n".join(lines)
