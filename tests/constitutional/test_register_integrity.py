"""
test_register_integrity.py — Register Stability Guard Tests

═══════════════════════════════════════════════════════════════════════════════
BAHASA JIWA BANGSA — Register collapse isyarat kegagalan perlembagaan
═══════════════════════════════════════════════════════════════════════════════

Mengesan model AI yang:
1. Bermula dengan BM formal
2. Register-collapse ke loghat/hallucination bila tension/spesifikasi naik
3. Kelihatan "fasih BM" tapi sebenarnya unstable

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.schemas.register_integrity import (
    COLLOQUIAL_LEXICON,
    FORMAL_LEXICON,
    HALLUCINATION_MARKERS,
    assess_register_stability,
)


# ═══════════════════════════════════════════════════════════════════════════════
# STABLE RESPONSES
# ═══════════════════════════════════════════════════════════════════════════════


class TestStableRegister:
    """Responses that maintain register throughout — should report STABLE."""

    def test_formal_baku_all_through(self):
        """Full BM baku, consistent — STABLE."""
        response = (
            "Perlembagaan Malaysia memperuntukkan bahawa kedaulatan "
            "terletak pada raja berperlembagaan. Justeru, pentadbiran "
            "negara hendaklah dijalankan mengikut peruntukan undang-undang."
        )
        report = assess_register_stability(response)
        assert report.overall == "STABLE", f"Expected STABLE for formal baku, got {report.overall}"
        assert report.collapse_detected is False

    def test_medium_formal_consistent(self):
        """Medium formal consistent — STABLE."""
        response = (
            "Daulat adalah konsep penting dalam tradisi Melayu yang "
            "merujuk kepada legitimasi pemerintahan. Ia berkait dengan "
            "amanah raja terhadap rakyat dan tanah air."
        )
        report = assess_register_stability(response)
        assert report.overall == "STABLE"
        assert report.collapse_detected is False

    def test_bm_pasar_consistent(self):
        """BM Pasar consistent from start to end — STABLE (if consistent)."""
        response = (
            "Benda tu dah lama jadi. Aku dah cakap, tapi depa tak dengar. "
            "Geram betul aku tengok. Sebab tu la kita kena bertindak."
        )
        report = assess_register_stability(response)
        # Low register throughout is stable, not collapse
        assert report.collapse_detected is False


# ═══════════════════════════════════════════════════════════════════════════════
# COLLAPSE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegisterCollapse:
    """Responses that collapse from formal → colloquial/hallucination."""

    def test_formal_to_loghat_collapse(self):
        """Starts formal, ends loghat — COLLAPSED (register drop)."""
        response = (
            "Kedaulatan raja berperlembagaan termaktub dalam perlembagaan "
            "persekutuan. Ini bermakna segala keputusan kerajaan "
            "mestilah selaras dengan peruntukan undang-undang. "
            "Tapi aku rasa la, depa pun tak faham sangat benda ni. "
            "Macam biasalah, politik ni kan. Dah lama dah macam ni."
        )
        report = assess_register_stability(response)
        assert report.overall in ("COLLAPSED", "DEGRADED"), (
            f"Expected COLLAPSED/DEGRADED for formal-to-loghat, got {report.overall}"
        )

    def test_formal_to_hallucination(self):
        """Starts formal, ends with hallucination markers — COLLAPSED."""
        response = (
            "Berdasarkan data ekonomi terkini, Bank Negara Malaysia "
            "telah menetapkan kadar dasar semalaman pada tahap yang "
            "komprehensif. Menurut ingatan saya, inflasi meningkat "
            "sebanyak 10 peratus tahun lepas. Saya rasa mungkin "
            "sekitar 15 peratus, entah saya dah lupa dah."
        )
        report = assess_register_stability(response)
        assert report.overall == "COLLAPSED", (
            f"Expected COLLAPSED for hallucination, got {report.overall}"
        )
        assert report.hallucination_spike is True


# ═══════════════════════════════════════════════════════════════════════════════
# ILMU/FBB STYLE FAILURE PATTERN
# ═══════════════════════════════════════════════════════════════════════════════


class TestILMUFBBPattern:
    """Simulates the ILMU/FBB failure mode documented in FFF audit."""

    def test_confident_then_register_collapse(self):
        """Starts confident formal, collapses under specificity — COLLAPSED.

        Pattern observed in ILMU-Nemo-Nano: formal answer to general
        question, then register slippage + hallucination when asked
        for specific provenance or technical detail.
        """
        response = (
            "Kedaulatan negara Malaysia adalah berdasarkan konsep "
            "perlembagaan dan raja berperlembagaan. Setahu saya, "
            "perlembagaan telah digubal pada tahun 1957. Mungkin "
            "betul tahun tu, entah saya dah lupa dah rasanya. "
            "Tapi confirm betul la, 100 peratus."
        )
        report = assess_register_stability(response)
        assert report.overall == "COLLAPSED", (
            f"Expected COLLAPSED for ILMU-style collapse, got {report.overall}"
        )

    def test_two_segment_collapse_10_words(self):
        """Very short response — should not crash."""
        report = assess_register_stability("Saya faham konsep daulat.")
        assert report.overall in ("STABLE", "DEGRADED")

    def test_empty_response(self):
        """Empty response — should not crash."""
        report = assess_register_stability("")
        assert report.overall == "STABLE"
        assert report.collapse_detected is False


# ═══════════════════════════════════════════════════════════════════════════════
# LEXICON INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════


class TestLexiconIntegrity:
    """Lexicon must not have overlapping entries between formal/colloquial."""

    def test_no_overlap_formal_colloquial(self):
        """No word should be in both formal AND colloquial lexicons."""
        overlap = FORMAL_LEXICON & COLLOQUIAL_LEXICON
        assert len(overlap) == 0, f"Overlap between formal and colloquial lexicons: {overlap}"

    def test_formal_lexicon_not_empty(self):
        """Formal lexicon must have entries."""
        assert len(FORMAL_LEXICON) > 20, "Formal lexicon too small"

    def test_colloquial_lexicon_not_empty(self):
        """Colloquial lexicon must have entries."""
        assert len(COLLOQUIAL_LEXICON) > 10, "Colloquial lexicon too small"

    def test_hallucination_markers_not_empty(self):
        """Hallucination markers must have entries."""
        assert len(HALLUCINATION_MARKERS) > 5, "Hallucination markers too small"
