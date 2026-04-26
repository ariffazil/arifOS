"""
tests/runtime/test_conformance_p0.py — P0 Remediation Validation

Proves:
1. Protected ID without token → Hard Fail (F11)
2. Structured intent → Accepted & Parsed
3. human_approval → Persisted in metadata
4. Forensic identity separation (claimed vs resolved)
"""

import pytest
from arifosmcp.runtime.tools import init_anchor
from arifosmcp.runtime.models import Verdict

@pytest.mark.asyncio
async def test_protected_id_hard_fail():
    """Verify arif cannot be claimed without a token (F11 Hardening)."""
    # Note: No auth_token provided
    res = await init_anchor(
        mode="init", 
        payload={"actor_id": "arif", "intent": "Audit"}
    )
    
    assert res.ok is False
    assert res.verdict == Verdict.VOID
    assert any("AUTH_FAILURE_PROTECTED_ID" in err.message for err in res.errors)
    assert res.payload["claim_status"] == "rejected_protected_id"
    assert res.payload["claimed_actor_id"] == "arif"
    assert res.payload["resolved_actor_id"] == "anonymous"

@pytest.mark.asyncio
async def test_structured_intent_acceptance():
    """Verify structured intent object is accepted and parsed."""
    payload = {
        "actor_id": "verifier-agent",
        "intent": {
            "query": "Validate quadrants",
            "domain": "engineering",
            "task_type": "audit",
            "desired_output": "report"
        },
        "human_approval": True
    }
    
    res = await init_anchor(mode="init", payload=payload)
    
    assert res.ok is True
    assert res.verdict == Verdict.SEAL
    assert res.payload["human_approval_persisted"] is True
    assert res.payload["abi_version"] == "1.0"
    assert res.payload["claim_status"] == "accepted"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
