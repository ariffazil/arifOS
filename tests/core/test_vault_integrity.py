from __future__ import annotations

import hashlib
import json

from core.organs._4_vault import compute_vault_seal_hash, verify_vault_ledger, verify_vault_record


def _build_entry() -> dict[str, object]:
    from core.organs._4_vault import _CHAIN_SEED

    entry = {
        "session_id": "vault-test",
        "ledger_id": "LGR-TEST",
        "summary": "sealed summary",
        "verdict": "SEAL",
        "approved_by": "system",
        "approval_reference": None,
        "telemetry": {"trace": {"111_MIND": "SEAL"}},
        "timestamp": "2026-03-12T00:00:00+00:00",
    }
    seal_hash = compute_vault_seal_hash(entry)
    entry_hash = hashlib.sha256((_CHAIN_SEED + seal_hash).encode()).hexdigest()
    return {
        **entry,
        "seal_hash": seal_hash,
        "chain": {
            "payload_hash": seal_hash,
            "entry_hash": entry_hash,
            "prev_entry_hash": _CHAIN_SEED,
        },
    }


def test_verify_vault_record_accepts_canonical_entry() -> None:
    ok, reason = verify_vault_record(_build_entry())

    assert ok is True
    assert reason is None


def test_verify_vault_record_rejects_tampered_summary() -> None:
    entry = _build_entry()
    entry["summary"] = "mutated after seal"

    ok, reason = verify_vault_record(entry)

    assert ok is False
    assert reason == "seal hash mismatch"


def test_verify_vault_ledger_rejects_invalid_entry_hash(tmp_path) -> None:
    entry = _build_entry()
    entry["chain"]["entry_hash"] = "broken"
    ledger_path = tmp_path / "vault999.jsonl"
    ledger_path.write_text(json.dumps(entry) + "\n", encoding="utf-8")

    ok, reason = verify_vault_ledger(ledger_path)

    assert ok is False
    assert "entry hash mismatch" in str(reason)
