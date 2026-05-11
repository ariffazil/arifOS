"""
Quick unit test for constitutional_guard.
Run: PYTHONPATH=/root python3 -m pytest tests/test_constitutional_guard.py -v
"""

from __future__ import annotations


from arifos.runtime.middleware.constitutional_guard import constitutional_guard


def test_guard_downgrades_shell_seal_when_floors_fail() -> None:
    """A tool returning SEAL with no metrics must be downgraded to VOID (hard floor F9 fails)."""
    raw = {
        "verdict": "SEAL",
        "session_id": "test-1",
        "actor_id": "arif",
        "intent": "test",
    }
    result = constitutional_guard("arifos_init", raw)

    assert result["verdict"] in ("PARTIAL", "VOID")
    assert "floor_results" in result
    assert "reasoning_hash" in result
    assert result["constitutional_guard_version"] == "v1"
    assert result["missing_output_fields"] == []


def test_guard_allows_seal_when_all_floors_pass() -> None:
    """If all floors pass, honest SEAL is granted."""
    raw = {
        "verdict": "SEAL",
        "session_id": "test-2",
        "actor_id": "arif",
        "intent": "test",
        "metrics": {
            "telemetry": {"G_star": 0.99, "confidence": 0.04, "shadow": 0.0},
            "witness": {"human": 1.0, "ai": 1.0, "earth": 1.0},
            "internal": {"zkpc_receipt": "receipt-123"},
            "policy": {"injection_score": 0.0, "amanah_lock": True},
        },
    }
    result = constitutional_guard("arifos_init", raw)

    assert result["verdict"] == "SEAL"
    assert result["floor_results"]["F2"]["passed"] is True
    assert result["floor_results"]["F3"]["passed"] is True
    assert result["floor_results"]["F7"]["passed"] is True


def test_guard_void_on_hard_floor_failure() -> None:
    """F2 failure must trigger VOID."""
    raw = {
        "verdict": "SEAL",
        "session_id": "test-3",
        "actor_id": "arif",
        "intent": "test",
        "metrics": {
            "telemetry": {"G_star": 0.50, "confidence": 0.04, "shadow": 0.0},
            "witness": {"human": 1.0, "ai": 1.0, "earth": 1.0},
            "internal": {"zkpc_receipt": "receipt-123"},
            "policy": {"injection_score": 0.0, "amanah_lock": True},
        },
    }
    result = constitutional_guard("arifos_init", raw)
    assert result["verdict"] == "VOID"
    assert result["floor_results"]["F2"]["passed"] is False


def test_guard_partial_on_missing_fields() -> None:
    """Missing required fields with passing hard floors must trigger PARTIAL."""
    raw = {
        "verdict": "SEAL",
        "metrics": {
            "telemetry": {"G_star": 0.99, "confidence": 0.04, "shadow": 0.0},
            "witness": {"human": 1.0, "ai": 1.0, "earth": 1.0},
            "internal": {"zkpc_receipt": "receipt-123"},
            "policy": {"injection_score": 0.0, "amanah_lock": True},
        },
    }
    result = constitutional_guard("arifos_init", raw)
    assert result["verdict"] == "PARTIAL"
    assert "session_id" in result["missing_output_fields"]


def test_guard_reasoning_hash_present() -> None:
    """reasoning_hash must be a valid hex string."""
    raw = {
        "verdict": "SEAL",
        "session_id": "test-4",
        "actor_id": "arif",
        "intent": "test",
    }
    result = constitutional_guard("arifos_init", raw)
    assert len(result["reasoning_hash"]) == 64
    assert all(c in "0123456789abcdef" for c in result["reasoning_hash"])
