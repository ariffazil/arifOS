"""
EpistemicTag — Classification of assertion certainty
DITEMPA BUKAN DIBERI
"""

from enum import Enum


class EpistemicTag(str, Enum):
    CLAIM = "CLAIM"
    PLAUSIBLE = "PLAUSIBLE"
    HYPOTHESIS = "HYPOTHESIS"
    ESTIMATE = "ESTIMATE"
    UNKNOWN = "UNKNOWN"


def isValidEpistemicTag(tag: str) -> bool:
    return tag in [e.value for e in EpistemicTag]


HIERARCHY = {
    EpistemicTag.UNKNOWN: 0,
    EpistemicTag.ESTIMATE: 1,
    EpistemicTag.HYPOTHESIS: 2,
    EpistemicTag.PLAUSIBLE: 3,
    EpistemicTag.CLAIM: 4,
}


def canUpgradeTag(from_tag: EpistemicTag, to_tag: EpistemicTag) -> bool:
    return HIERARCHY[to_tag] >= HIERARCHY[from_tag]