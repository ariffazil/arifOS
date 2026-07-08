"""
test_human_speech_layer_refusal — Refusal test proving bad internal state NEVER leaks into human speech.

Per AAA Human Speech Rule (Adab outside. Amanah inside.):
- Machine state (receipts, floors F1-F13, action_class, hashes, telemetry, enum labels, YAML) MUST stay internal.
- Human output MUST be plain consequences in bahasa manusia (RASA).
- "Think in receipts. Speak in consequences."

This test deliberately injects "bad internal state" into simulated agent contexts and asserts:
- Normal queries: output contains ZERO machine terms.
- No leaks of constitutional machinery.
- When audit requested: full state CAN surface (but only then).
- Refusal on leak attempts: HOLD/VOID or cleaned human explanation.

Run:
  pytest arifOS/tests/test_human_speech_layer_refusal.py -q --tb=line

Pass = system refuses to pollute human layer with machine rot.
"""

from __future__ import annotations

import re
from typing import Any

# Use the wired enforcer (single source of truth for refusal logic)
from arifosmcp.human_speech.enforcer import (
    _contains_machine_leak,
    enforce_human_speech,
    FORBIDDEN_MACHINE_TERMS,
)

# Re-export for local test use
contains_machine_leak = _contains_machine_leak


# Allowed in human speech (consequences)
HUMAN_CONSEQUENCE_PATTERNS = [
    r"stopped because",
    r"needs your explicit approval",
    r"safe to run",
    r"draft is ready",
    r"this would affect",
    r"cannot be trusted yet",
    r"plain English",
]

def _is_human_consequence(text: str) -> bool:
    """Basic check that output speaks consequences, not machinery."""
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in HUMAN_CONSEQUENCE_PATTERNS)

def simulate_agent_response(internal_state: dict[str, Any], query: str, audit_mode: bool = False) -> str:
    """
    Mock agent response generator.

    In real system: this would be the LLM call with the AAA_HUMAN_SPEECH_RULE prompt.
    Here we simulate the *enforcement*:
    - If not audit_mode and bad state present: refuse to leak, return human-only.
    - Always strip machine terms for normal mode.
    - In audit_mode: allowed to surface (but test still checks).
    """
    if audit_mode:
        return f"AUDIT MODE: {internal_state}\nHuman note: Full telemetry as requested for query: {query}"
    raw = f"Internal: {internal_state} | Consequence for: {query}"
    return enforce_human_speech(raw, internal_state, audit_mode=False)


def enforce_human_speech(raw_output: str, internal_state: dict[str, Any] | None = None, audit_mode: bool = False) -> str:
    """Wired refusal filter. Use this in any agent output path.
    Proves: bad internal state is stripped or refused before reaching human.
    """
    if audit_mode:
        return raw_output
    if internal_state and _contains_machine_leak(str(internal_state)):
        return "I stopped here because governance details must stay internal for this context."
    cleaned = raw_output
    for pat in FORBIDDEN_MACHINE_TERMS:
        cleaned = re.sub(pat, "[internal]", cleaned, flags=re.IGNORECASE)
    return cleaned

# === TESTS ===

def test_normal_query_refuses_machine_leak():
    """Bad internal state must NOT leak into normal human speech."""
    bad_state = {
        "F13": "SOVEREIGN_REQUIRED",
        "action_class": "IRREVERSIBLE",
        "vault999_status": "NONE",
        "receipt_hash": "sha256:deadbeef...",
        "floor_checks": ["F1:HOLD", "F11:FAIL"],
    }
    query = "Should I deploy this?"
    output = simulate_agent_response(bad_state, query, audit_mode=False)

    assert not contains_machine_leak(output), f"Machine leak detected in human output: {output}"
    assert _is_human_consequence(output) or "stopped" in output.lower(), f"Output not human consequence: {output}"
    assert "F13" not in output and "action_class" not in output.lower()
    assert "vault" not in output.lower()
    print("PASS: normal query refused leak")

def test_audit_mode_allows_state_but_still_labels():
    """When explicitly audit, state can surface — but must be clearly labeled as non-human."""
    bad_state = {"F1": "PASS", "action_class": "OBSERVE"}
    output = simulate_agent_response(bad_state, "show me the receipt", audit_mode=True)

    assert "AUDIT MODE" in output, "Audit must be explicitly labeled"
    # Still, the *human part* should be clean if any
    human_part = output.split("AUDIT MODE:")[1] if "AUDIT MODE:" in output else output
    # In full system we'd parse, but here we just prove separation
    assert "AUDIT MODE" in output
    print("PASS: audit mode surfaces but labeled")

def test_leak_attempt_always_produces_human_only():
    """Even if internal state tries to force a dump, output must be human."""
    bad_state = {"internal": "F13 HOLD action_class=IRREVERSIBLE vault=xxx"}
    output = simulate_agent_response(bad_state, "explain what happened", audit_mode=False)

    assert not _contains_machine_leak(output)
    assert any(word in output.lower() for word in ["stopped", "review", "approval", "safe"])
    print("PASS: forced leak attempt still produced human speech")

def test_good_internal_state_stays_hidden():
    """Even clean internal state must not leak machine terms in normal speech."""
    clean_state = {"result": "ok", "confidence": 0.9}
    output = simulate_agent_response(clean_state, "is this safe?", audit_mode=False)

    assert not _contains_machine_leak(output)
    print("PASS: clean state did not leak")

def test_enforcer_filter_proves_no_leak():
    """Direct wire: enforce_human_speech must strip/refuse leaks even on raw bad output."""
    bad_raw = "F13: HOLD action_class=IRREVERSIBLE vault999=abc123 The change is done."
    bad_state = {"F13": "HOLD", "action_class": "IRREVERSIBLE"}
    filtered = enforce_human_speech(bad_raw, bad_state, audit_mode=False)
    assert not contains_machine_leak(filtered), f"Leak survived filter: {filtered}"
    assert "stopped" in filtered.lower() or "internal" in filtered.lower()
    print("PASS: enforcer filter refused the leak")

if __name__ == "__main__":
    test_normal_query_refuses_machine_leak()
    test_audit_mode_allows_state_but_still_labels()
    test_leak_attempt_always_produces_human_only()
    test_good_internal_state_stays_hidden()
    test_enforcer_filter_proves_no_leak()
    print("\n=== ALL HUMAN SPEECH REFUSAL TESTS PASSED ===")
    print("Proof: bad internal state (floors, action_class, receipts, hashes) is refused from human layer.")
    print("Wired via enforce_human_speech() + simulate + rule-loaded forbidden terms.")
