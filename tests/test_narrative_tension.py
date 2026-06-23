"""
tests/test_narrative_tension.py
═══════════════════════════════════════════════════════════════════
Unit tests for the Narrative Tension / Perception Kernel.

Covers:
- Golden-case loading (Putra Heights Kosmo 2026-06-12)
- Heuristic analysis on generic text
- Schema validation of response objects
- VAULT999 consequential-tool membership

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations


import pytest

from arifosmcp.runtime.narrative_tension import arif_detect_narrative_tension
from arifosmcp.runtime.vault_sealer import CONSEQUENTIAL_TOOLS
from arifosmcp.schemas.narrative_tension import NarrativeTensionResponse


PUTRA_TITLE = (
    "Laporan kebakaran paip gas Putra Heights: MB Selangor nafi sorok, dedah kekangan undang-undang"
)
PUTRA_TEXT = (
    "MB Selangor menjelaskan kerajaan negeri bersedia mendedahkan laporan "
    "siasatan kebakaran paip gas Putra Heights. Laporan telah diserah April "
    "lalu tetapi masih belum boleh didedahkan kerana terdapat kekangan "
    "undang-undang melibatkan agensi persekutuan seperti Petronas yang perlu "
    "diteliti semula."
)


@pytest.mark.asyncio
async def test_golden_case_putra_heights():
    """The pre-computed Putra Heights analysis must load intact."""
    result = await arif_detect_narrative_tension(
        article_id="ARTICLE-kosmo-putra-2026-06-12",
        title=PUTRA_TITLE,
        text=PUTRA_TEXT,
        source="Kosmo",
        author="Iskandar Shah Mohamed",
        published_at="2026-06-12T08:00:00+08:00",
    )

    response = NarrativeTensionResponse.model_validate(result)
    assert response.status == "OK"
    assert response.verdict == "ESCALATE"
    assert response.kernel_verdict.smoking_gun == "PH-T3"
    assert response.kernel_verdict.max_severity == 0.95
    assert len(response.frame_graph.tensions) == 7
    assert any(t.tension_class == "SLIP_PHRASE" for t in response.frame_graph.tensions)


@pytest.mark.asyncio
async def test_heuristic_detects_contradiction():
    """Generic text must trigger at least one tension via heuristics."""
    result = await arif_detect_narrative_tension(
        title="Government promises action, says report under review",
        text=(
            "The Ministry said it is ready to release the investigation report. "
            "However, the report submitted last year still cannot be disclosed "
            "because there are legal constraints. Residents said the collapse "
            "could have been prevented. The Ministry found no negligence."
        ),
        source="Test News",
    )

    response = NarrativeTensionResponse.model_validate(result)
    assert response.status == "OK"
    assert len(response.frame_graph.tensions) >= 1
    assert response.frame_graph.article.full_text_hash is not None


def test_vault_sealer_includes_tool():
    """Narrative tension detection must be sealed as a consequential transition."""
    assert "arif_detect_narrative_tension" in CONSEQUENTIAL_TOOLS


@pytest.mark.asyncio
async def test_response_has_kernel_verdict():
    """Every response must carry a kernel verdict with constitutional hash."""
    result = await arif_detect_narrative_tension(
        title="Test headline",
        text="A short text with no obvious tension.",
        source="Test",
    )
    response = NarrativeTensionResponse.model_validate(result)
    assert response.kernel_verdict is not None
    assert response.kernel_verdict.constitution_hash is not None
