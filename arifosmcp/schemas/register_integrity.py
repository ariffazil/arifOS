"""
register_integrity.py — Register Stability Guard for BM Production Models

═══════════════════════════════════════════════════════════════════════════════
BAHASA JIWA BANGSA — Register collapse adalah isyarat kegagalan perlembagaan
═══════════════════════════════════════════════════════════════════════════════

Register collapse berlaku apabila model AI:
1. Bermula dalam BM formal (register tinggi) — ayat sempurna, kosa kata tepat
2. Bertukar ke loghat/register rendah bila soalan bertambah spesifik atau tension
3. Akhirnya hallucinate — confident tapi salah

Ini bukan "stylistic variation." Ini isyarat bahawa model tidak stabil dari segi
epistemik: surface fluency tanpa grounding. Ia kelihatan seperti "speaks Malay
fluently" tetapi runtuh di bawah tekanan.

Register integrity guard mengesan collapse dengan membandingkan:
  - Register awal (baseline) vs register akhir response
  - Kekerapan hallucination markers
  - Ketekalan kosa kata antara register

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import List

# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER LEVELS — BM Production Register Map
# ═══════════════════════════════════════════════════════════════════════════════


class RegisterLevel(StrEnum):
    """Register level for BM production text.

    Higher = more formal, structured, epistemically reliable.
    Lower = more colloquial, contextual, prone to hallucination.
    """

    HIGH_FORMAL = "high_formal"  # Bahasa Melayu baku — tulisan, akademik, rasmi
    MEDIUM_FORMAL = "medium_formal"  # BM separa formal — laporan, email, berita
    LOW_COLLOQUIAL = "low_colloquial"  # BM pasar — loghat, harian, whatsapp
    CODE_SWITCH = "code_switch"  # Campur Inggeris/Melayu — penang BM
    HALLUCINATED = "hallucinated"  # Confident-sounding tapi salah dari segi fakta


# ═══════════════════════════════════════════════════════════════════════════════
# FORMAL LEXICON — Words that indicate HIGH/MEDIUM register
# ═══════════════════════════════════════════════════════════════════════════════

FORMAL_LEXICON: set[str] = {
    # Kata tugas rasmi
    "merujuk",
    "mengikut",
    "berdasarkan",
    "seterusnya",
    "sungguhpun",
    "walaupun",
    "manakala",
    "oleh itu",
    "dengan ini",
    "adalah",
    "telah",
    "bagi",
    "iaitu",
    "yakni",
    "justeru",
    "maka",
    "malahan",
    "bahawasanya",
    "hendaklah",
    # Kata nama abstrak formal
    "kedaulatan",
    "perlembagaan",
    "ketatanegaraan",
    "pentadbiran",
    "perundangan",
    "kehakiman",
    "eksekutif",
    "legislatif",
    "prosedur",
    "mekanisme",
    "hierarki",
    "bidangkuasa",
    "majlis",
    "jawatankuasa",
    "kementerian",
    "kerajaan",
    "rakyat",
    "negara",
    "wilayah",
    "daerah",
    # Kata kerja formal
    "mempertimbangkan",
    "mengesyorkan",
    "memutuskan",
    "melaksanakan",
    "mematuhi",
    "menguatkuasakan",
    "mentadbir",
    "mengurus",
    "menentukan",
    "menetapkan",
    "memperakukan",
    "menyatakan",
    # Kata sifat formal
    "sah",
    "mutlak",
    "relatif",
    "komprehensif",
    "efektif",
    "sistematik",
    "struktur",
    "kritikal",
    "strategik",
    # Adab / governance
    "maruah",
    "amanah",
    "daulat",
    "adab",
    "budi",
    "norma",
    "etika",
    "integriti",
    "akauntabiliti",
    "ketelusan",
}


# ═══════════════════════════════════════════════════════════════════════════════
# COLLOQUIAL LEXICON — Words that indicate LOW register / loghat
# ═══════════════════════════════════════════════════════════════════════════════

COLLOQUIAL_LEXICON: set[str] = {
    # BM Pasar
    "saja",
    "je",
    "la",
    "lah",
    "tu",
    "ni",
    "kan",
    "diorang",
    "kitorang",
    "hang",
    "ko",
    "kau",
    "aku",
    "boleh",
    "takleh",
    "nak",
    "dah",
    "tengah",
    # Loghat utara
    "hok",
    "hampa",
    "demo",
    "mung",
    "cek",
    # Loghat timur
    "kome",
    "kite",
    "deme",
    "mmber",
    # Loghat negeri
    "kita orang",
    "kitorang",
    "depa",
    "ko",
    # Slang moden
    "geram",
    "sebab tu",
    "mcm",
    "macam",
    "benda",
    "gila",
    "bangang",
    "bodoh",
    "takis",
    "gedik",
    # Filler
    "erm",
    "ehem",
    "ah",
    "oh",
    "haah",
}

# Hallucination markers — phrases that precede factually incorrect content
HALLUCINATION_MARKERS: set[str] = {
    "saya percaya",
    "saya rasa",
    "pada pendapat saya",
    "menurut ingatan saya",
    "setahu saya",
    "kalau tak silap saya",
    "saya assume",
    "maybe",
    "mungkin betul",
    "rasanya",
    "saya tak ingat",
    "saya dah lupa",
    "entah",
    # Overconfidence tanpa evidence
    "sudah tentu",
    "semestinya",
    "tidak mungkin salah",
    "100 peratus",
    "confirm",
    "pasti",
    "sebenarnya",
    "hakikatnya",
    "secara jujurnya",
}


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER STABILITY REPORT
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class RegisterSegment:
    """A segment of text with its register classification."""

    text: str = ""
    word_count: int = 0
    formal_count: int = 0
    colloquial_count: int = 0
    hallucination_markers: int = 0
    register: RegisterLevel = RegisterLevel.MEDIUM_FORMAL
    score: float = 0.0  # -1.0 (colloquial) to +1.0 (formal)


@dataclass
class RegisterStabilityReport:
    """Full register integrity report for a model response."""

    segments: List[RegisterSegment] = field(default_factory=list)
    overall: str = "STABLE"

    # Collapse detection
    baseline_register: RegisterLevel = RegisterLevel.MEDIUM_FORMAL
    ending_register: RegisterLevel = RegisterLevel.MEDIUM_FORMAL
    register_drop: bool = False  # True if register dropped from baseline

    # Score deltas
    baseline_score: float = 0.0
    ending_score: float = 0.0
    score_delta: float = 0.0  # negative = collapse

    # Alerts
    collapse_detected: bool = False
    hallucination_spike: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# THE DETECTION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════


def _classify_register_segment(
    text: str,
    formal_lex: set[str] | None = None,
    colloquial_lex: set[str] | None = None,
    hallu_markers: set[str] | None = None,
) -> RegisterSegment:
    """Classify a single text segment by register."""
    formal_lex = formal_lex or FORMAL_LEXICON
    colloquial_lex = colloquial_lex or COLLOQUIAL_LEXICON
    hallu_markers = hallu_markers or HALLUCINATION_MARKERS

    words = text.lower().split()
    if not words:
        return RegisterSegment(text=text, word_count=0, register=RegisterLevel.HIGH_FORMAL)

    word_count = len(words)
    formal_count = sum(1 for w in words if w in formal_lex)
    colloquial_count = sum(1 for w in words if w in colloquial_lex)
    hallucination_count = sum(1 for m in hallu_markers if m in text.lower())

    # Score: normalize to -1.0 (colloquial) to +1.0 (formal)
    total_signal = formal_count + colloquial_count
    score = 0.0
    if total_signal > 0:
        score = (formal_count - colloquial_count) / total_signal

    # Determine register level from score
    if hallucination_count > 0:
        register = RegisterLevel.HALLUCINATED
    elif score >= 0.5:
        register = RegisterLevel.HIGH_FORMAL
    elif score >= 0.0:
        register = RegisterLevel.MEDIUM_FORMAL
    elif score >= -0.3:
        register = RegisterLevel.LOW_COLLOQUIAL
    else:
        register = RegisterLevel.CODE_SWITCH

    return RegisterSegment(
        text=text,
        word_count=word_count,
        formal_count=formal_count,
        colloquial_count=colloquial_count,
        hallucination_markers=hallucination_count,
        register=register,
        score=round(score, 3),
    )


def assess_register_stability(
    response: str,
    n_segments: int = 3,
) -> RegisterStabilityReport:
    """Assess register stability across a model response.

    Splits response into n_segments, classifies each, detects collapse.

    Collapse detection:
      - register_drop: True ending register is lower than baseline
      - score_delta: negative if score drops significantly (< -0.3)
    """
    words = response.split()
    if not words:
        return RegisterStabilityReport()

    # Split into segments
    segment_size = max(1, len(words) // n_segments)
    segments: list[RegisterSegment] = []

    for i in range(n_segments):
        start = i * segment_size
        end = start + segment_size if i < n_segments - 1 else len(words)
        segment_text = " ".join(words[start:end])
        seg = _classify_register_segment(segment_text)
        segments.append(seg)

    if not segments:
        return RegisterStabilityReport()

    baseline = segments[0]
    ending = segments[-1]

    report = RegisterStabilityReport(
        segments=segments,
        baseline_register=baseline.register,
        ending_register=ending.register,
        baseline_score=baseline.score,
        ending_score=ending.score,
        score_delta=round(ending.score - baseline.score, 3),
    )

    # Detect collapse
    register_order = [
        RegisterLevel.HIGH_FORMAL,
        RegisterLevel.MEDIUM_FORMAL,
        RegisterLevel.LOW_COLLOQUIAL,
        RegisterLevel.CODE_SWITCH,
        RegisterLevel.HALLUCINATED,
    ]
    try:
        baseline_idx = register_order.index(baseline.register)
        ending_idx = register_order.index(ending.register)
        if ending_idx > baseline_idx:
            report.register_drop = True
    except ValueError:
        pass

    # Score drop threshold
    if report.score_delta < -0.3:
        report.collapse_detected = True

    # Hallucination spike
    hallu_count = sum(s.hallucination_markers for s in segments)
    if hallu_count > 0:
        report.hallucination_spike = True
        report.collapse_detected = True

    # Overall status
    if report.collapse_detected:
        report.overall = "COLLAPSED"
    elif report.register_drop:
        report.overall = "DEGRADED"
    else:
        report.overall = "STABLE"

    return report
