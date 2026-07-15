"""
Seal token guard — prose_mode (F12 seal-gate tuning / Round 2)
════════════════════════════════════════════════════════════════

Operational prose in seal receipts often mentions "seal", F13, credentials,
and keys as *meta* language. STRICT mode without prose_mode quarantines bare
"seal". prose_mode=True allows operational context while still flagging
truly bare ambiguous seals.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from arifosmcp.core.seal_token_guard import GuardMode, scan


class TestSealTokenProseMode:
    def test_bare_seal_strict_quarantines(self):
        v = scan("please seal this now", mode=GuardMode.STRICT, prose_mode=False)
        assert v.quarantined is True
        assert v.disambiguation_required is True
        assert len(v.hits) >= 1

    def test_qualified_vault_seal_clean(self):
        v = scan("emit vault_seal for receipt", mode=GuardMode.STRICT, prose_mode=False)
        assert v.quarantined is False
        assert v.is_clean or "vault_seal" in str(v.detected_domains) or not v.hits

    def test_prose_mode_allows_receipt_mentioning_seal_and_f13(self):
        text = (
            "Seal receipt: F13 sovereign ack recorded; credential class noted; "
            "no raw key material. Audit trail complete."
        )
        v = scan(text, mode=GuardMode.STRICT, prose_mode=True)
        assert v.quarantined is False
        assert v.guard_log_entry.get("prose_mode") is True

    def test_prose_mode_allows_operational_credential_meta(self):
        text = (
            "Operational note: seal completed under floor F11; "
            "api_key class = present (value redacted)."
        )
        v = scan(text, mode=GuardMode.STRICT, prose_mode=True)
        assert v.quarantined is False

    def test_prose_mode_still_quarantines_ambiguous_bare_seal_alone(self):
        # No operational markers at all — still bare.
        v = scan("seal", mode=GuardMode.STRICT, prose_mode=True)
        # Single token "seal" with no prose markers → still quarantine
        assert v.quarantined is True

    def test_geological_domain_still_works(self):
        v = scan(
            "The geological seal integrity is high across the trap",
            mode=GuardMode.STRICT,
            prose_mode=False,
        )
        assert v.quarantined is False
