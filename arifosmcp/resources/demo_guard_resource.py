"""arifOS Demo Guard — safe simulation for first-time users.

Returns SEAL/HOLD/VOID verdicts for simulated actions without
connecting to real tools. Designed for the 60-second demonstration:
"Use arifOS to audit this action."
"""

from __future__ import annotations

DEMO_SCENARIOS = {
    "delete_production_db": {
        "action": "DELETE FROM production.users",
        "identity": "agent-unknown",
        "verdict": "HOLD",
        "reason": "No verified identity. Destructive action requires authenticated actor + lease.",
        "floor": "F1 AMANAH",
    },
    "deploy_without_test": {
        "action": "git push production main --force",
        "identity": "developer-agent",
        "verdict": "HOLD",
        "reason": "Production deployment requires green test pass + human approval.",
        "floor": "F1 AMANAH",
    },
    "read_public_data": {
        "action": "SELECT * FROM public.basin_summary",
        "identity": "researcher-agent",
        "verdict": "SEAL",
        "reason": "Read-only action on public data. No mutation risk.",
        "floor": None,
    },
    "fabricated_evidence": {
        "action": "deploy based on generated market report",
        "identity": "analyst-agent",
        "verdict": "VOID",
        "reason": "Evidence is synthetic/SPEC, not OBS. Cannot authorize mutation on unverified claim.",
        "floor": "F2 TRUTH",
    },
    "approved_reversible": {
        "action": "create feature branch and push",
        "identity": "developer-agent (verified)",
        "verdict": "SEAL",
        "reason": "Reversible action with verified identity. Standard development workflow.",
        "floor": None,
    },
    "prompt_injection": {
        "action": "execute: eval(base64_decode(evil_payload))",
        "identity": "compromised-agent",
        "verdict": "VOID",
        "reason": "Prompt injection detected. External input treated as evidence, not instruction.",
        "floor": "F12 INJECTION",
    },
    "identity_drift": {
        "action": "approve deployment",
        "identity": "arif-admin → ARIF-ADMIN (drifted)",
        "verdict": "HOLD",
        "reason": "Actor casing mismatch. Identity must be normalized and verified.",
        "floor": "F11 AUDIT",
    },
}


def get_demo_verdict(scenario_id: str) -> dict | None:
    """Return a simulated verdict for a named scenario."""
    return DEMO_SCENARIOS.get(scenario_id)


def get_all_demo_scenarios() -> list[dict]:
    """Return all demo scenarios."""
    return [{"id": k, **v} for k, v in DEMO_SCENARIOS.items()]
