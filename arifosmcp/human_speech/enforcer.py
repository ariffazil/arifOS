"""
human_speech/enforcer.py — Wired refusal layer for AAA Human Speech Rule.

"Think in receipts. Speak in consequences."

Usage in any agent output path:
    from arifosmcp.human_speech.enforcer import enforce_human_speech
    output = enforce_human_speech(raw_llm_output, internal_state, audit_mode=False)

This guarantees bad internal state (floors, action_class, receipts, hashes, etc.)
never reaches human speech unless audit_mode=True.

See: /root/AAA/governance/AAA_HUMAN_SPEECH_RULE.md
Test: /root/arifOS/tests/test_human_speech_layer_refusal.py
"""

from __future__ import annotations

import os
import re
from typing import Any

RULE_PATH = "/root/AAA/governance/AAA_HUMAN_SPEECH_RULE.md"

# Base forbidden (synced with rule; test extends from file)
BASE_FORBIDDEN = [
    r"\bF[0-9]+\b",
    r"\b(action_class|ActionClass)\b",
    r"\b(receipt|Receipt|VAULT999)\b",
    r"\b(HOLD|VOID|SEAL|SABAR)\b(?!\s+to)",
    r"\b(telemetry|floor|hash|witness_chain|authority_scope)\b",
    r"\bYAML|json|enum|schema\b",
    r"Think in receipts",
]


def _load_forbidden() -> list[str]:
    terms = list(BASE_FORBIDDEN)
    if os.path.exists(RULE_PATH):
        with open(RULE_PATH) as f:
            rule = f.read().lower()
        if "floor" in rule:
            terms.append(r"\bfloor\b")
    return terms


FORBIDDEN_MACHINE_TERMS = _load_forbidden()


def _contains_machine_leak(text: str) -> bool:
    text_lower = text.lower()
    for pattern in FORBIDDEN_MACHINE_TERMS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False


def enforce_human_speech(
    raw_output: str,
    internal_state: dict[str, Any] | None = None,
    audit_mode: bool = False,
) -> str:
    """Refusal filter. Bad internal state is refused or redacted for human layer."""
    if audit_mode:
        return raw_output

    state_str = str(internal_state) if internal_state else ""
    if internal_state and _contains_machine_leak(state_str):
        return "I stopped here because governance details must stay internal for this context."

    cleaned = raw_output
    for pat in FORBIDDEN_MACHINE_TERMS:
        cleaned = re.sub(pat, "[internal]", cleaned, flags=re.IGNORECASE)

    # If after cleaning it's mostly machine, force human consequence
    if _contains_machine_leak(cleaned):
        return "I stopped here because internal state cannot be shown in this response."

    return cleaned
