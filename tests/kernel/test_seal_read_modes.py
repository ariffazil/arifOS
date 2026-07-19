from __future__ import annotations

from arifosmcp.kernel.interceptor import intercept
from arifosmcp.kernel.models import AdmissibilityVerdict


def _seal_request(mode: str, actor_id: str = "arif") -> dict:
    return {
        "params": {
            "name": "arif_seal",
            "arguments": {
                "mode": mode,
                "actor_id": actor_id,
            },
        }
    }


def test_read_only_seal_modes_bypass_mutation_gates() -> None:
    for mode in (
        "verify",
        "ledger",
        "chain",
        "list",
        "audit",
        "changelog",
        "dry_run",
        "retrieve_audit",
    ):
        decision = intercept(_seal_request(mode))
        assert decision.verdict == AdmissibilityVerdict.ADMIT_READ, mode
        assert decision.mutation_class is not None
        assert decision.mutation_class.value == "NONE"


def test_seal_write_still_requires_external_anchor() -> None:
    from arifosmcp.runtime.jwt_auth import set_request_auth_lineage
    try:
        set_request_auth_lineage({"sub": "arif", "auth_method": "jwt"})
        decision = intercept(_seal_request("seal"))
        assert decision.verdict == AdmissibilityVerdict.DENY
        assert "external anchor" in decision.reason.lower()
    finally:
        set_request_auth_lineage(None)


def test_read_only_seal_modes_do_not_require_sovereign_actor() -> None:
    decision = intercept(_seal_request("verify", actor_id="session-worker"))
    assert decision.verdict == AdmissibilityVerdict.ADMIT_READ
