"""
arifosmcp/runtime/wisdom_quotes.py — Governed Wisdom Registry v2

Unified quote corpus mapped from real VPS sources:
  - /root/arifOS/arifosmcp/runtime/constitutional_quotes.json (100 tool-mapped quotes)
  - /root/arifOS/wiki/raw/wisdom_quotes.json (arifOS Foundry corpus)
  - /root/arifOS/wiki/pages/ (philosophy atlas — see wiki/pages/RECURSIVE_IMPROVEMENT_LOG.md)

v2 additions:
  - attribution_confidence
  - scar_weight / shadow_weight / paradox_weight
  - contrast_pair / polarity
  - verdict-aware selection with deterministic fallback
  - audit logging of quote injection

Categories: truth | humility | restraint | judgment | memory | discipline |
            responsibility | peribahasa | founder | seal | love | paradox | scar

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class WisdomQuote(TypedDict):
    id: str
    text: str
    author: str
    source: str
    category: str
    surfaces: list[str]
    tone: str
    language: str
    priority: int
    active: bool
    toolOrigin: str | None
    zoneId: str | None
    attribution_confidence: str
    source_url: str | None
    scar_weight: int
    shadow_weight: int
    paradox_weight: int
    contrast_pair: str | None
    polarity: str | None


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER A — Civilizational Canon
# ═══════════════════════════════════════════════════════════════════════════════
CIVILIZATIONAL_CANON: list[WisdomQuote] = [
    {
        "id": "INIT_Q_001",
        "text": "A journey of a thousand miles begins with a single step.",
        "author": "Lao Tzu",
        "source": "Tao Te Ching",
        "category": "discipline",
        "surfaces": ["anchor"],
        "tone": "calm",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": "arifos.init",
        "zoneId": None,
        "attribution_confidence": "commonly_attributed",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": "VAULT_Q_002",
        "polarity": "order",
    },
    {
        "id": "INIT_Q_004",
        "text": "The only true wisdom is in knowing you know nothing.",
        "author": "Socrates",
        "source": "Platonic Dialogues",
        "category": "humility",
        "surfaces": ["anchor", "sense"],
        "tone": "reflective",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": "arifos.init",
        "zoneId": None,
        "attribution_confidence": "commonly_attributed",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 2,
        "contrast_pair": "MIND_Q_004",
        "polarity": "doubt",
    },
    {
        "id": "INIT_Q_003",
        "text": "No wind serves him who addresses his voyage to no certain port.",
        "author": "Michel de Montaigne",
        "source": "Essays",
        "category": "discipline",
        "surfaces": ["anchor"],
        "tone": "firm",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": "arifos.init",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "SENSE_Q_002",
        "text": "The first principle is that you must not fool yourself—and you are the easiest person to fool.",
        "author": "Richard Feynman",
        "source": "Cargo Cult Science",
        "category": "truth",
        "surfaces": ["sense", "monitor", "mind"],
        "tone": "firm",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": "arifos.sense",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 1,
        "contrast_pair": "JUDGE_Q_005",
        "polarity": "truth",
    },
    {
        "id": "SENSE_Q_001",
        "text": "It is wrong always, everywhere, and for anyone, to believe anything upon insufficient evidence.",
        "author": "W. K. Clifford",
        "source": "The Ethics of Belief",
        "category": "truth",
        "surfaces": ["sense", "judge"],
        "tone": "severe",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": "arifos.sense",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "truth",
    },
    {
        "id": "SENSE_Q_004",
        "text": "No man ever steps in the same river twice.",
        "author": "Heraclitus",
        "source": "Fragments",
        "category": "truth",
        "surfaces": ["sense", "vault"],
        "tone": "reflective",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": "arifos.sense",
        "zoneId": None,
        "attribution_confidence": "commonly_attributed",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 2,
        "contrast_pair": None,
        "polarity": "chaos",
    },
    {
        "id": "MIND_Q_004",
        "text": "Doubt is not a pleasant condition, but certainty is absurd.",
        "author": "Voltaire",
        "source": "Letter to Frederick II",
        "category": "humility",
        "surfaces": ["mind", "judge", "partial"],
        "tone": "reflective",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": "arifos.mind",
        "zoneId": None,
        "attribution_confidence": "commonly_attributed",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 2,
        "contrast_pair": "INIT_Q_004",
        "polarity": "doubt",
    },
    {
        "id": "MIND_Q_005",
        "text": "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.",
        "author": "Antoine de Saint-Exupéry",
        "source": "Wind, Sand and Stars",
        "category": "discipline",
        "surfaces": ["mind", "forge"],
        "tone": "calm",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": "arifos.mind",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "HEART_Q_001",
        "text": "First, do no harm.",
        "author": "Hippocrates",
        "source": "Epidemics",
        "category": "restraint",
        "surfaces": ["heart", "judge", "hold"],
        "tone": "firm",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": "arifos.heart",
        "zoneId": None,
        "attribution_confidence": "traditional",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 0,
        "contrast_pair": "PW1",
        "polarity": "mercy",
    },
    {
        "id": "HEART_Q_002",
        "text": "Act in such a way that you treat humanity, whether in your own person or in the person of another, always as an end and never as a means only.",
        "author": "Immanuel Kant",
        "source": "Groundwork of the Metaphysics of Morals",
        "category": "responsibility",
        "surfaces": ["heart", "judge"],
        "tone": "severe",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": "arifos.heart",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "judgment",
    },
    {
        "id": "JUDGE_Q_002",
        "text": "Power tends to corrupt, and absolute power corrupts absolutely.",
        "author": "Lord Acton",
        "source": "Letter to Bishop Mandell Creighton",
        "category": "restraint",
        "surfaces": ["judge", "hold", "void"],
        "tone": "severe",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": "arifos.judge",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 1,
        "shadow_weight": 2,
        "paradox_weight": 1,
        "contrast_pair": "PW1",
        "polarity": "power",
    },
    {
        "id": "JUDGE_Q_004",
        "text": "Injustice anywhere is a threat to justice everywhere.",
        "author": "Martin Luther King Jr.",
        "source": "Letter from Birmingham Jail",
        "category": "judgment",
        "surfaces": ["judge"],
        "tone": "firm",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": "arifos.judge",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 1,
        "shadow_weight": 1,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "judgment",
    },
    {
        "id": "JUDGE_Q_005",
        "text": "The sad truth is that most evil is done by people who never make up their minds to be good or evil.",
        "author": "Hannah Arendt",
        "source": "The Life of the Mind",
        "category": "judgment",
        "surfaces": ["judge", "hold", "void"],
        "tone": "reflective",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": "arifos.judge",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 2,
        "shadow_weight": 2,
        "paradox_weight": 1,
        "contrast_pair": "SENSE_Q_002",
        "polarity": "shadow",
    },
    {
        "id": "FORGE_Q_001",
        "text": "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.",
        "author": "Antoine de Saint-Exupéry",
        "source": "Wind, Sand and Stars",
        "category": "discipline",
        "surfaces": ["forge"],
        "tone": "calm",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": "arifos.forge",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "OPS_Q_002",
        "text": "An ounce of practice is worth more than tons of preaching.",
        "author": "Mahatma Gandhi",
        "source": "",
        "category": "discipline",
        "surfaces": ["forge", "ops"],
        "tone": "firm",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": "arifos.ops",
        "zoneId": None,
        "attribution_confidence": "commonly_attributed",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "OPS_Q_001",
        "text": "Well done is better than well said.",
        "author": "Benjamin Franklin",
        "source": "Poor Richard's Almanack",
        "category": "discipline",
        "surfaces": ["forge", "ops"],
        "tone": "firm",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": "arifos.ops",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "VAULT_Q_002",
        "text": "Those who cannot remember the past are condemned to repeat it.",
        "author": "George Santayana",
        "source": "The Life of Reason",
        "category": "memory",
        "surfaces": ["vault"],
        "tone": "severe",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": "arifos.vault",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 1,
        "shadow_weight": 1,
        "paradox_weight": 1,
        "contrast_pair": "INIT_Q_001",
        "polarity": "memory",
    },
    {
        "id": "VAULT_Q_004",
        "text": "The struggle of man against power is the struggle of memory against forgetting.",
        "author": "Milan Kundera",
        "source": "The Book of Laughter and Forgetting",
        "category": "memory",
        "surfaces": ["vault", "void"],
        "tone": "reflective",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": "arifos.vault",
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 2,
        "shadow_weight": 2,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "memory",
    },
    {
        "id": "Z01-Q01",
        "text": "You have power over your mind—not outside events. Realize this, and you will find strength.",
        "author": "Marcus Aurelius",
        "source": "Meditations",
        "category": "power",
        "surfaces": ["monitor", "judge"],
        "tone": "calm",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": None,
        "zoneId": "Z01",
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "power",
    },
    {
        "id": "Z03-Q01",
        "text": "Everything can be taken from a man but one thing: the last of the human freedoms—to choose one's attitude.",
        "author": "Viktor Frankl",
        "source": "Man's Search for Meaning",
        "category": "wisdom",
        "surfaces": ["heart", "hold"],
        "tone": "firm",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": None,
        "zoneId": "Z03",
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 1,
        "shadow_weight": 1,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "mercy",
    },
    {
        "id": "Z05-Q01",
        "text": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.",
        "author": "Aristotle",
        "source": "Nicomachean Ethics",
        "category": "discipline",
        "surfaces": ["forge", "ops"],
        "tone": "calm",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": "Z05",
        "attribution_confidence": "commonly_attributed",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "Z19-Q01",
        "text": "Either mathematics is too big for the human mind, or the human mind is more than a machine.",
        "author": "Kurt Gödel",
        "source": "",
        "category": "paradox",
        "surfaces": ["mind", "judge", "partial"],
        "tone": "reflective",
        "language": "en",
        "priority": 7,
        "active": True,
        "toolOrigin": None,
        "zoneId": "Z19",
        "attribution_confidence": "commonly_attributed",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 3,
        "contrast_pair": None,
        "polarity": "doubt",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER B — Malay Wisdom (Peribahasa / Simpulan Bahasa)
# ═══════════════════════════════════════════════════════════════════════════════
MALAY_WISDOM: list[WisdomQuote] = [
    {
        "id": "MS_001",
        "text": "Ikut resmi padi, makin berisi makin tunduk.",
        "author": "Peribahasa Melayu",
        "source": "",
        "category": "humility",
        "surfaces": ["anchor", "heart", "judge"],
        "tone": "calm",
        "language": "ms",
        "priority": 10,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "traditional",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "humility",
    },
    {
        "id": "MS_002",
        "text": "Biar lambat, asal selamat.",
        "author": "Peribahasa Melayu",
        "source": "",
        "category": "restraint",
        "surfaces": ["hold", "judge", "forge"],
        "tone": "firm",
        "language": "ms",
        "priority": 10,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "traditional",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "restraint",
    },
    {
        "id": "MS_003",
        "text": "Sedikit-sedikit, lama-lama jadi bukit.",
        "author": "Peribahasa Melayu",
        "source": "",
        "category": "discipline",
        "surfaces": ["anchor", "forge", "ops", "sabar"],
        "tone": "calm",
        "language": "ms",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "traditional",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "MS_005",
        "text": "Harimau mati meninggalkan belang, manusia mati meninggalkan nama.",
        "author": "Peribahasa Melayu",
        "source": "",
        "category": "memory",
        "surfaces": ["vault"],
        "tone": "severe",
        "language": "ms",
        "priority": 8,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "traditional",
        "source_url": None,
        "scar_weight": 1,
        "shadow_weight": 1,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "memory",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER C — arifOS Forged Canon
# ═══════════════════════════════════════════════════════════════════════════════
ARIFOS_FORGED_CANON: list[WisdomQuote] = [
    {
        "id": "SE4",
        "text": "DITEMPA, BUKAN DIBERI.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "seal",
        "surfaces": ["anchor", "forge", "monitor"],
        "tone": "firm",
        "language": "ms",
        "priority": 11,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "seal",
    },
    {
        "id": "WI3",
        "text": "Truth ages well; shortcuts do not.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "truth",
        "surfaces": ["sense", "judge", "vault"],
        "tone": "calm",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "truth",
    },
    {
        "id": "WI6",
        "text": "Humility is an operating constraint, not a mood.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "humility",
        "surfaces": ["anchor", "monitor", "mind"],
        "tone": "firm",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "humility",
    },
    {
        "id": "WI7",
        "text": "If the witness is weak, the claim must wait.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "judgment",
        "surfaces": ["judge", "hold", "sense"],
        "tone": "severe",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "restraint",
    },
    {
        "id": "WI13",
        "text": "What you cannot explain clearly, do not ship proudly.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "discipline",
        "surfaces": ["forge", "ops"],
        "tone": "firm",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "PX20",
        "text": "The limit is part of the design, not the enemy of it.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "discipline",
        "surfaces": ["forge", "judge", "void"],
        "tone": "calm",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "restraint",
    },
    {
        "id": "PW1",
        "text": "Power without restraint is noise pretending to be force.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "restraint",
        "surfaces": ["judge", "hold", "forge", "void"],
        "tone": "severe",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 1,
        "shadow_weight": 2,
        "paradox_weight": 1,
        "contrast_pair": "HEART_Q_001",
        "polarity": "restraint",
    },
    {
        "id": "PW3",
        "text": "Command begins with self-command.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "discipline",
        "surfaces": ["forge", "ops", "judge"],
        "tone": "firm",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "SE1",
        "text": "What is forged with witness can survive the night.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "seal",
        "surfaces": ["vault", "forge"],
        "tone": "reflective",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "seal",
    },
    {
        "id": "LV3",
        "text": "Mercy does not erase truth; it carries it gently.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "love",
        "surfaces": ["heart", "judge"],
        "tone": "calm",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "mercy",
    },
    {
        "id": "LV8",
        "text": "The safest room is one where dignity remains intact.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "love",
        "surfaces": ["heart", "judge"],
        "tone": "firm",
        "language": "en",
        "priority": 8,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 1,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "mercy",
    },
    {
        "id": "ARIF_VOID_001",
        "text": "What is forbidden is not a mistake to fix; it is a boundary to honor.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "restraint",
        "surfaces": ["void", "judge"],
        "tone": "severe",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 2,
        "shadow_weight": 3,
        "paradox_weight": 1,
        "contrast_pair": "PX20",
        "polarity": "restraint",
    },
    {
        "id": "ARIF_VOID_002",
        "text": "Crossing the line once makes the line invisible forever.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "shadow",
        "surfaces": ["void", "judge"],
        "tone": "severe",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 3,
        "shadow_weight": 3,
        "paradox_weight": 2,
        "contrast_pair": None,
        "polarity": "shadow",
    },
    {
        "id": "ARIF_PARTIAL_001",
        "text": "Incomplete is not the same as broken. Some truths need more turns.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "paradox",
        "surfaces": ["partial", "judge"],
        "tone": "reflective",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 1,
        "shadow_weight": 1,
        "paradox_weight": 2,
        "contrast_pair": "MIND_Q_004",
        "polarity": "doubt",
    },
    {
        "id": "ARIF_PARTIAL_002",
        "text": "Sabar — the floor strains but does not break. Adjust, then proceed.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "discipline",
        "surfaces": ["partial", "sabar", "judge"],
        "tone": "calm",
        "language": "en",
        "priority": 9,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 1,
        "shadow_weight": 0,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "order",
    },
    {
        "id": "ARIF_HOLD_001",
        "text": "Restraint is the first act of sovereignty.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "restraint",
        "surfaces": ["hold", "judge"],
        "tone": "firm",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 2,
        "paradox_weight": 1,
        "contrast_pair": None,
        "polarity": "restraint",
    },
    {
        "id": "ARIF_SABAR_001",
        "text": "Stop, acknowledge, breathe, adjust, resume. The floor protects.",
        "author": "arifOS Foundry",
        "source": "",
        "category": "discipline",
        "surfaces": ["sabar", "anchor", "hold"],
        "tone": "calm",
        "language": "en",
        "priority": 10,
        "active": True,
        "toolOrigin": None,
        "zoneId": None,
        "attribution_confidence": "verified",
        "source_url": None,
        "scar_weight": 0,
        "shadow_weight": 0,
        "paradox_weight": 0,
        "contrast_pair": None,
        "polarity": "mercy",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════
WISDOM_REGISTRY: list[WisdomQuote] = CIVILIZATIONAL_CANON + MALAY_WISDOM + ARIFOS_FORGED_CANON

SURFACES = {
    "anchor",
    "monitor",
    "sense",
    "mind",
    "heart",
    "judge",
    "hold",
    "vault",
    "forge",
    "ops",
    "empty",
    "void",
    "partial",
    "sabar",
}

_DEFAULT_QUOTE: WisdomQuote = {
    "id": "DEFAULT",
    "text": "DITEMPA BUKAN DIBERI — Forged, not given.",
    "author": "arifOS",
    "source": "",
    "category": "seal",
    "surfaces": ["empty"],
    "tone": "firm",
    "language": "ms",
    "priority": 0,
    "active": True,
    "toolOrigin": None,
    "zoneId": None,
    "attribution_confidence": "verified",
    "source_url": None,
    "scar_weight": 0,
    "shadow_weight": 0,
    "paradox_weight": 0,
    "contrast_pair": None,
    "polarity": "seal",
}


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT LOGGING
# ═══════════════════════════════════════════════════════════════════════════════
_WISDOM_AUDIT_PATH = Path(os.path.expanduser("~/.arifos/wisdom_audit.jsonl"))


def _ensure_audit_dir() -> None:
    _WISDOM_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)


def audit_quote_injection(
    quote_id: str,
    surface: str,
    verdict: str | None,
    session_id: str | None = None,
    context: dict | None = None,
) -> None:
    """Append a quote-injection event to the wisdom audit log."""
    try:
        _ensure_audit_dir()
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "quote_id": quote_id,
            "surface": surface,
            "verdict": verdict,
            "session_id": session_id,
            "context": context or {},
        }
        with _WISDOM_AUDIT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# SELECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
def _score_candidate(candidate: WisdomQuote, tone: str | None, language: str | None, shadow_profile: str | None) -> float:
    """Score a candidate quote. Higher is better."""
    score = float(candidate["priority"])

    if tone and candidate["tone"] == tone:
        score += 5.0

    if language and candidate["language"] == language:
        score += 3.0

    if shadow_profile:
        # Map shadow_profile to weight boosts
        profile_map: dict[str, str] = {
            "scar": "scar_weight",
            "shadow": "shadow_weight",
            "paradox": "paradox_weight",
            "restraint": "shadow_weight",
            "humility": "shadow_weight",
            "doubt": "paradox_weight",
        }
        weight_key = profile_map.get(shadow_profile)
        if weight_key:
            score += float(candidate.get(weight_key, 0)) * 2.0  # type: ignore[literal-required]

    return score


def pick_quote(
    surface: str,
    tone: str | None = None,
    verdict: str | None = None,
    risk_tier: str | None = None,
    language: str | None = None,
    shadow_profile: str | None = None,
    audit: bool = True,
    session_id: str | None = None,
) -> WisdomQuote:
    """
    Deterministically select the best active quote for a surface.

    Fallback policy:
      1) strict filters (surface + tone + language + shadow_profile)
      2) relax language
      3) relax tone
      4) relax shadow_profile
      5) surface-only
      6) globally approved safe default
    """
    result = pick_quote_with_meta(
        surface=surface,
        tone=tone,
        verdict=verdict,
        risk_tier=risk_tier,
        language=language,
        shadow_profile=shadow_profile,
        audit=audit,
        session_id=session_id,
    )
    return result["quote"]


def pick_quote_with_meta(
    surface: str,
    tone: str | None = None,
    verdict: str | None = None,
    risk_tier: str | None = None,
    language: str | None = None,
    shadow_profile: str | None = None,
    audit: bool = True,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Deterministically select the best active quote for a surface.
    Returns quote + selection metadata (reason, priority score, fallback step).
    """
    if surface not in SURFACES:
        if audit:
            audit_quote_injection("DEFAULT", surface, verdict, session_id, {"reason": "unknown_surface"})
        return {
            "quote": _DEFAULT_QUOTE,
            "selection_reason": "safe_default",
            "display_priority": 0,
            "fallback_step": "unknown_surface",
        }

    candidates = [q for q in WISDOM_REGISTRY if q["active"] and surface in q["surfaces"]]

    reason_map = {
        (False, False, False): "exact_match",
        (True, False, False): "language_relaxed",
        (True, True, False): "tone_relaxed",
        (True, True, True): "shadow_relaxed",
    }

    # Fallback cascade
    for relax_lang, relax_tone, relax_shadow in [
        (False, False, False),
        (True, False, False),
        (True, True, False),
        (True, True, True),
    ]:
        step_candidates = list(candidates)
        _lang = None if relax_lang else language
        _tone = None if relax_tone else tone
        _shadow = None if relax_shadow else shadow_profile

        scored = [
            (_score_candidate(c, _tone, _lang, _shadow), c)
            for c in step_candidates
        ]
        scored.sort(key=lambda x: x[0], reverse=True)

        if scored:
            best = scored[0][1]
            priority_score = int(scored[0][0])
            if audit:
                audit_quote_injection(
                    best["id"],
                    surface,
                    verdict,
                    session_id,
                    {
                        "tone": _tone,
                        "language": _lang,
                        "shadow_profile": _shadow,
                        "risk_tier": risk_tier,
                        "fallback_step": f"lang={relax_lang},tone={relax_tone},shadow={relax_shadow}",
                        "display_priority": priority_score,
                    },
                )
            return {
                "quote": best,
                "selection_reason": reason_map.get((relax_lang, relax_tone, relax_shadow), "exact_match"),
                "display_priority": priority_score,
                "fallback_step": f"lang={relax_lang},tone={relax_tone},shadow={relax_shadow}",
            }

    # Ultimate fallback
    if audit:
        audit_quote_injection("DEFAULT", surface, verdict, session_id, {"reason": "no_candidates"})
    return {
        "quote": _DEFAULT_QUOTE,
        "selection_reason": "safe_default",
        "display_priority": 0,
        "fallback_step": "no_candidates",
    }


def quotes_for_surface(surface: str) -> list[WisdomQuote]:
    """Return all active quotes for a surface, sorted by priority."""
    if surface not in SURFACES:
        return []
    return sorted(
        [q for q in WISDOM_REGISTRY if q["active"] and surface in q["surfaces"]],
        key=lambda q: q["priority"],
        reverse=True,
    )


def registry_stats() -> dict:
    """Return coverage statistics."""
    total = len(WISDOM_REGISTRY)
    by_category: dict[str, int] = {}
    by_surface: dict[str, int] = {}
    by_language: dict[str, int] = {}
    by_polarity: dict[str, int] = {}
    by_attribution: dict[str, int] = {}
    active_count = 0
    for q in WISDOM_REGISTRY:
        if q["active"]:
            active_count += 1
        by_category[q["category"]] = by_category.get(q["category"], 0) + 1
        by_language[q["language"]] = by_language.get(q["language"], 0) + 1
        if q.get("polarity"):
            by_polarity[q["polarity"]] = by_polarity.get(q["polarity"], 0) + 1
        by_attribution[q["attribution_confidence"]] = by_attribution.get(q["attribution_confidence"], 0) + 1
        for s in q["surfaces"]:
            by_surface[s] = by_surface.get(s, 0) + 1
    return {
        "total": total,
        "active": active_count,
        "by_category": by_category,
        "by_surface": by_surface,
        "by_language": by_language,
        "by_polarity": by_polarity,
        "by_attribution_confidence": by_attribution,
    }


def arifos_wisdom_stats() -> dict[str, Any]:
    """Comprehensive observability over the governed wisdom registry."""
    stats = registry_stats()
    surfaces_list = sorted(SURFACES)
    coverage = {
        s: {
            "quote_count": stats["by_surface"].get(s, 0),
            "sample_quotes": [q["id"] for q in quotes_for_surface(s)[:3]],
        }
        for s in surfaces_list
    }
    return {
        "ok": True,
        "tool": "arifos_wisdom_stats",
        "registry": stats,
        "surfaces": coverage,
        "shadow_index": {
            "max_scar": max((q["scar_weight"] for q in WISDOM_REGISTRY), default=0),
            "max_shadow": max((q["shadow_weight"] for q in WISDOM_REGISTRY), default=0),
            "max_paradox": max((q["paradox_weight"] for q in WISDOM_REGISTRY), default=0),
            "high_scar_quotes": [q["id"] for q in WISDOM_REGISTRY if q["scar_weight"] >= 2],
            "high_shadow_quotes": [q["id"] for q in WISDOM_REGISTRY if q["shadow_weight"] >= 2],
            "high_paradox_quotes": [q["id"] for q in WISDOM_REGISTRY if q["paradox_weight"] >= 2],
        },
        "contrast_pairs": [
            {"quote_id": q["id"], "contrast_pair": q["contrast_pair"], "text": q["text"][:60]}
            for q in WISDOM_REGISTRY
            if q.get("contrast_pair")
        ],
    }
