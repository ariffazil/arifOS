"""
tests/abis/test_penangprobe.py — Unit tests for the Penang linguistic-routing probe.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations


from arifosmcp.abi.penangprobe import (
    build_query,
    parse_probe_result,
    ratio_bm_to_en,
    token_efficiency_claim,
    _classify_url_language,
    _classify_title_language,
    CANONICAL_PAIRS,
)


class TestBuildQuery:
    def test_byte_count_utf8(self) -> None:
        q = build_query("apa cerita pasal arifOS kat Malaysia", "BM")
        assert q.byte_length == len("apa cerita pasal arifOS kat Malaysia".encode("utf-8"))
        assert q.byte_length == 36

    def test_word_count_simple(self) -> None:
        q = build_query("apa cerita pasal arifOS kat Malaysia", "BM")
        assert q.word_count == 6

    def test_label_preserved(self) -> None:
        q = build_query("test", "BM")
        assert q.language == "BM"


class TestURLClassification:
    def test_dot_my_is_bm(self) -> None:
        assert _classify_url_language("https://www.sinarharian.com.my/article/8553") == "BM"

    def test_dot_com_my_is_bm(self) -> None:
        assert _classify_url_language("https://www.bharian.com.my") == "BM"

    def test_dot_gov_is_empty(self) -> None:
        assert _classify_url_language("https://www.trade.gov/page") == ""

    def test_voaindonesia_not_bm_url(self) -> None:
        # voaindonesia.com is Indonesian, not Malaysian BM. URL-only heuristic.
        assert _classify_url_language("https://www.voaindonesia.com/article") == ""


class TestTitleClassification:
    def test_malay_body_particles_in_title(self) -> None:
        # "berita hari ini" has body-level BM particles (berita, hari, ini)
        assert _classify_title_language("berita hari ini") == "BM"

    def test_english_particles_in_title(self) -> None:
        assert _classify_title_language("Agreement Between the United States") == "EN"

    def test_neutral_title_unclassified(self) -> None:
        assert _classify_title_language("arifOS") == ""


class TestParseProbeResult:
    def test_bm_routing_differential(self) -> None:
        raw = {
            "result": {
                "results": [
                    {
                        "title": "Setelah Menang di Arbitrase",
                        "link": "https://www.sinarharian.com.my/x",
                        "snippet": "...",
                    },
                    {
                        "title": "Agreement Between Malaysia and the US",
                        "link": "https://www.trade.gov/x",
                        "snippet": "...",
                    },
                ]
            }
        }
        bm = parse_probe_result("BM", "test", raw)
        assert bm.n_results == 2
        assert bm.n_bm_routed == 1
        assert bm.n_en_routed == 1
        assert bm.routing_differential == 0

    def test_all_bm_routing(self) -> None:
        raw = {
            "result": {
                "results": [
                    {
                        "title": "Berita Malaysia",
                        "link": "https://www.bharian.com.my/x",
                        "snippet": "...",
                    },
                    {
                        "title": "Surat Kabar Harian",
                        "link": "https://www.sinarharian.com.my/y",
                        "snippet": "...",
                    },
                ]
            }
        }
        bm = parse_probe_result("BM", "test", raw)
        assert bm.n_bm_routed == 2
        assert bm.n_en_routed == 0
        assert bm.routing_differential == 2

    def test_empty_results(self) -> None:
        raw = {"result": {"results": []}}
        bm = parse_probe_result("BM", "test", raw)
        assert bm.n_results == 0
        assert bm.routing_differential == 0


class TestTokenEfficiency:
    def test_bm_shorter_than_en(self) -> None:
        bm = build_query("apa cerita pasal arifOS kat Malaysia", "BM")
        en = build_query("what is the state of arifOS in Malaysia", "EN")
        result = token_efficiency_claim(bm, en)
        assert result["bm_bytes"] < result["en_bytes"]
        assert result["interpretation"] == "BM shorter"
        assert result["ratio_bm_to_en"] < 1.0

    def test_caveat_present(self) -> None:
        bm = build_query("a", "BM")
        en = build_query("about arifOS in Malaysia now", "EN")
        result = token_efficiency_claim(bm, en)
        assert "caveat" in result

    def test_ratio_bm_to_en_helper(self) -> None:
        bm = build_query("a b c", "BM")  # 5 bytes
        en = build_query("a b c d e f", "EN")  # 11 bytes
        assert abs(ratio_bm_to_en(bm, en) - 5 / 11) < 0.001


class TestCanonicalPairs:
    def test_three_pairs(self) -> None:
        assert len(CANONICAL_PAIRS) == 3
        for bm, en in CANONICAL_PAIRS:
            assert bm.language == "BM"
            assert en.language == "EN"
