"""
arifOS Doctrine Resource — F1-F13 Constitutional Substrate
DITEMPA BUKAN DIBERI — 999 SEAL
"""

FLOOR_DEFINITIONS = {
    "F1": {"name": "Amanah", "threshold": "LOCK", "type": "Hard", "engine": "ASI"},
    "F2": {"name": "Truth", "threshold": "≥ 0.99", "type": "Hard", "engine": "AGI"},
    "F4": {"name": "ΔS (Clarity)", "threshold": "≤ 0", "type": "Hard", "engine": "AGI"},
    "F5": {"name": "Peace²", "threshold": "≥ 1.0", "type": "Soft", "engine": "ASI"},
    "F6": {
        "name": "κᵣ (Empathy)",
        "threshold": "≥ 0.70",
        "type": "Soft",
        "engine": "ASI",
    },
    "F7": {
        "name": "Ω₀ (Humility)",
        "threshold": "0.03–0.05",
        "type": "Hard",
        "engine": "AGI",
    },
    "F9": {"name": "C_dark", "threshold": "< 0.30", "type": "Derived", "engine": "ASI"},
    "F11": {
        "name": "Command Auth",
        "threshold": "LOCK",
        "type": "Hard",
        "engine": "ASI",
    },
    "F13": {
        "name": "Sovereign",
        "threshold": "HUMAN",
        "type": "Veto",
        "engine": "APEX",
    },
}

DOCTRINE_TEXT = """
# arifOS Constitutional Doctrine — F1-F13

## 9 Floors — Operational Constraints

| # | Floor | Threshold | Type | Engine |
|---|-------|-----------|------|--------|
| F1 | Amanah | LOCK | Hard | ASI |
| F2 | Truth | ≥ 0.99 | Hard | AGI |
| F4 | ΔS (Clarity) | ≤ 0 | Hard | AGI |
| F5 | Peace² | ≥ 1.0 | Soft | ASI |
| F6 | κᵣ (Empathy) | ≥ 0.70 | Soft | ASI |
| F7 | Ω₀ (Humility) | 0.03–0.05 | Hard | AGI |
| F9 | C_dark | < 0.30 | Derived | ASI |
| F11 | Command Auth | LOCK | Hard | ASI |
| F13 | Sovereign | HUMAN | Veto | APEX |

## 2 Mirrors — Feedback Loops

| # | Mirror | Threshold | Function |
|---|--------|-----------|----------|
| F3 | Tri-Witness | ≥ 0.95 | External calibration (Human·AI·Earth) |
| F8 | G (Genius) | ≥ 0.80 | Internal coherence (A×P×X×E²) |

## 2 Walls — Binary Gates

| # | Wall | Threshold | Function |
|---|------|-----------|----------|
| F10 | Ontology | LOCK | No consciousness/soul claims |
| F12 | Injection | < 0.85 | Block adversarial control |
"""


async def get_doctrine() -> dict:
    """Return the full constitutional doctrine."""
    return {
        "doctrine": DOCTRINE_TEXT,
        "floors": FLOOR_DEFINITIONS,
        "uri": "resource://arifOS/doctrine",
    }


async def get_doctrine_floor(floor_id: str) -> dict:
    """Return a specific floor definition."""
    floor = FLOOR_DEFINITIONS.get(floor_id.upper())
    if not floor:
        return {"error": f"Unknown floor: {floor_id}"}
    return {
        "floor_id": floor_id.upper(),
        "floor_uri": f"resource://arifOS/doctrine/floor/{floor_id.upper()}",
        **floor,
    }
