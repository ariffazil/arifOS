"""
Test the NIAT GATE capabilities forged from the 2026-05-21/22 Eureka.
"""
from arifosmcp.runtime.niat_gate import check_niat_gate, enforce_capability_membrane, apply_context_containment

def test_check_niat_gate_clear():
    res = check_niat_gate(
        user_instruction="Draft a generic summary",
        context_source="public",
        requested_action="draft",
        medium_shift="none",
        negative_signals=[],
        reversibility="reversible"
    )
    assert res["niat_state"] == "CLEAR"
    assert res["formalization_allowed"] is True
    assert res["execution_allowed"] is True
    assert res["required_next_step"] == "PROCEED"

def test_check_niat_gate_scar_detected():
    res = check_niat_gate(
        user_instruction="jangan hantar to KPJ",
        context_source="whatsapp",
        requested_action="send",
        medium_shift="private_to_email",
        negative_signals=["jangan"],
        reversibility="irreversible"
    )
    assert res["niat_state"] == "UNCERTAIN"
    assert res["execution_allowed"] is False
    assert res["required_next_step"] == "HOLD"
    assert "jangan" in res["detected_scars"]

def test_formalization_lock():
    res = check_niat_gate(
        user_instruction="send it to email",
        context_source="whatsapp",
        requested_action="send",
        medium_shift="private_to_email",
        negative_signals=[],
        reversibility="irreversible"
    )
    assert res["formalization_allowed"] is False
    assert res["execution_allowed"] is False
    assert res["required_next_step"] == "JUDGE" or res["required_next_step"] == "HOLD"

def test_enforce_capability_membrane():
    permitted = {
        "tool": "send_email",
        "to": ["izzudin@example.com"],
        "one_time_use": True
    }
    
    # Valid
    assert enforce_capability_membrane("send_email", {"to": "izzudin@example.com"}, permitted) is True
    
    # Invalid recipient
    assert enforce_capability_membrane("send_email", {"to": "kpj@example.com", "cc": "mak"}, permitted) is False
    
    # Invalid tool
    assert enforce_capability_membrane("draft_email", {"to": "izzudin@example.com"}, permitted) is False

def test_apply_context_containment():
    data = "Secret details about KPJ and Izzudin."
    
    # Read for reasoning is fine
    assert apply_context_containment(data, "READ_FOR_REASONING") == data
    
    # Export for action is redacted
    assert "REDACTED" in apply_context_containment(data, "EXPORT_FOR_ACTION")
