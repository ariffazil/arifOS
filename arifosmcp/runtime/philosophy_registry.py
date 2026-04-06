"""
Philosophy Registry — 99 Quotes with G★ Bands
═══════════════════════════════════════════════════════════════════════════════

Deterministic G★ selection for ToM-anchored MCP tools.
Each quote is tagged with a G★ score that maps to constitutional alignment.

G★ Bands:
  0.00-0.20: Band 0 — void/paradox (uncertainty, limits)
  0.20-0.40: Band 1 — paradox/truth (epistemology, doubt)
  0.40-0.60: Band 2 — wisdom/justice (ethics, governance)
  0.60-0.80: Band 3 — discipline/power (execution, systems)
  0.80-1.00: Band 4 — seal/power (mastery, completion)

Registry version: 1.2.0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GBand(Enum):
    """G★ bands for quote selection."""
    BAND_0_VOID = (0.0, 0.20)      # void/paradox
    BAND_1_PARADOX = (0.20, 0.40)  # paradox/truth
    BAND_2_WISDOM = (0.40, 0.60)   # wisdom/justice
    BAND_3_DISCIPLINE = (0.60, 0.80)  # discipline/power
    BAND_4_SEAL = (0.80, 1.00)     # seal/power


@dataclass(frozen=True)
class PhilosophyQuote:
    """A single philosophical quote with metadata."""
    text: str
    author: str
    g_star: float           # Constitutional alignment score (0.0-1.0)
    band: int               # 0-4
    category: str           # void, paradox, truth, wisdom, justice, discipline, power, seal
    civilization: str       # Ancient_East, Ancient_West, European_Enlightenment, etc.
    source: Optional[str] = None
    
    def __post_init__(self):
        # Validate G★ is in correct band
        band_ranges = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
        low, high = band_ranges[self.band]
        if not (low <= self.g_star <= high):
            raise ValueError(f"G★ {self.g_star} not in band {self.band} range [{low}, {high}]")


# ═══════════════════════════════════════════════════════════════════════════════
# THE 99 QUOTES
# ═══════════════════════════════════════════════════════════════════════════════

PHILOSOPHY_REGISTRY: list[PhilosophyQuote] = [
    # ═══════════════════════════════════════════════════════════════════════════
    # S1: THE FORGE PRINCIPLE — Identity Anchor for INIT and SEAL
    # ═══════════════════════════════════════════════════════════════════════════
    # This quote is returned unconditionally for:
    #   - stage == "INIT" (birth/initialization)
    #   - verdict == "SEAL" (sovereignty/completion)
    # It is the civilizational identity of the system.
    PhilosophyQuote(
        text="DITEMPA, BUKAN DIBERI.",
        author="arifOS Principle",
        g_star=1.0,  # Maximum constitutional alignment
        band=4,      # Seal band
        category="seal",
        civilization="Contemporary_Global",
        source="Forge Principle S1",
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BAND 0: Void/Paradox (0.00-0.20) — Uncertainty, Limits, The Unknown
    # ═══════════════════════════════════════════════════════════════════════════
    PhilosophyQuote(
        text="The only principle that does not inhibit progress is: anything goes.",
        author="Paul Feyerabend",
        g_star=0.10,
        band=0,
        category="void",
        civilization="Modern_Scientific",
        source="Against Method"
    ),
    PhilosophyQuote(
        text="I know one thing: that I know nothing.",
        author="Socrates",
        g_star=0.15,
        band=0,
        category="void",
        civilization="Ancient_West",
        source="Apology"
    ),
    PhilosophyQuote(
        text="The Tao that can be spoken is not the eternal Tao.",
        author="Laozi",
        g_star=0.12,
        band=0,
        category="void",
        civilization="Ancient_East",
        source="Tao Te Ching"
    ),
    PhilosophyQuote(
        text="We shall not cease from exploration, and the end of all our exploring will be to arrive where we started and know the place for the first time.",
        author="T.S. Eliot",
        g_star=0.18,
        band=0,
        category="paradox",
        civilization="Contemporary_Global",
        source="Four Quartets"
    ),
    PhilosophyQuote(
        text="The map is not the territory.",
        author="Alfred Korzybski",
        g_star=0.14,
        band=0,
        category="void",
        civilization="Modern_Scientific",
        source="Science and Sanity"
    ),
    PhilosophyQuote(
        text="It ain't what you don't know that gets you into trouble. It's what you know for sure that just ain't so.",
        author="Mark Twain",
        g_star=0.16,
        band=0,
        category="paradox",
        civilization="Contemporary_Global",
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BAND 1: Paradox/Truth (0.20-0.40) — Epistemology, Doubt, Method
    # ═══════════════════════════════════════════════════════════════════════════
    PhilosophyQuote(
        text="The concept of truth cannot be defined within the system itself.",
        author="Alfred Tarski",
        g_star=0.30,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
        source="The Concept of Truth in Formalized Languages"
    ),
    PhilosophyQuote(
        text="In any sufficiently powerful logical system, there are true statements that cannot be proven within that system.",
        author="Kurt Gödel",
        g_star=0.35,
        band=1,
        category="paradox",
        civilization="Modern_Scientific",
        source="Incompleteness Theorems"
    ),
    PhilosophyQuote(
        text="Doubt is the origin of wisdom.",
        author="René Descartes",
        g_star=0.28,
        band=1,
        category="truth",
        civilization="European_Enlightenment",
        source="Discourse on Method"
    ),
    PhilosophyQuote(
        text="The first principle is that you must not fool yourself—and you are the easiest person to fool.",
        author="Richard Feynman",
        g_star=0.32,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="No amount of experimentation can ever prove me right; a single experiment can prove me wrong.",
        author="Albert Einstein",
        g_star=0.38,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="Science is what we have learned about how to keep from fooling ourselves.",
        author="Richard Feynman",
        g_star=0.33,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="Absence of evidence is not evidence of absence.",
        author="Carl Sagan",
        g_star=0.25,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="What can be asserted without evidence can also be dismissed without evidence.",
        author="Christopher Hitchens",
        g_star=0.29,
        band=1,
        category="truth",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="The problem with the world is that the intelligent people are full of doubts, while the stupid ones are full of confidence.",
        author="Charles Bukowski",
        g_star=0.27,
        band=1,
        category="paradox",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="We are all stumblers, and the beauty and meaning of life are in the stumbling.",
        author="David Brooks",
        g_star=0.22,
        band=1,
        category="truth",
        civilization="Contemporary_Global",
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BAND 2: Wisdom/Justice (0.40-0.60) — Ethics, Governance, Common Good
    # ═══════════════════════════════════════════════════════════════════════════
    PhilosophyQuote(
        text="Nearly all men can stand adversity, but if you want to test a man's character, give him power.",
        author="Abraham Lincoln",
        g_star=0.50,
        band=2,
        category="wisdom",
        civilization="Modern_Political",
    ),
    PhilosophyQuote(
        text="The arc of the moral universe is long, but it bends toward justice.",
        author="Martin Luther King Jr.",
        g_star=0.55,
        band=2,
        category="justice",
        civilization="Modern_Political",
    ),
    PhilosophyQuote(
        text="Injustice anywhere is a threat to justice everywhere.",
        author="Martin Luther King Jr.",
        g_star=0.52,
        band=2,
        category="justice",
        civilization="Modern_Political",
        source="Letter from Birmingham Jail"
    ),
    PhilosophyQuote(
        text="The only thing necessary for the triumph of evil is for good men to do nothing.",
        author="Edmund Burke",
        g_star=0.48,
        band=2,
        category="justice",
        civilization="European_Enlightenment",
    ),
    PhilosophyQuote(
        text="Those who would give up essential Liberty, to purchase a little temporary Safety, deserve neither Liberty nor Safety.",
        author="Benjamin Franklin",
        g_star=0.58,
        band=2,
        category="justice",
        civilization="European_Enlightenment",
    ),
    PhilosophyQuote(
        text="We must be the change we wish to see in the world.",
        author="Mahatma Gandhi",
        g_star=0.45,
        band=2,
        category="wisdom",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="It is not power that corrupts but fear. Fear of losing power corrupts those who wield it.",
        author="Aung San Suu Kyi",
        g_star=0.49,
        band=2,
        category="power",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="A society grows great when old men plant trees whose shade they know they shall never sit in.",
        author="Greek Proverb",
        g_star=0.47,
        band=2,
        category="wisdom",
        civilization="Ancient_West",
    ),
    PhilosophyQuote(
        text="Do not judge me by my successes, judge me by how many times I fell down and got back up again.",
        author="Nelson Mandela",
        g_star=0.53,
        band=2,
        category="wisdom",
        civilization="Modern_Political",
    ),
    PhilosophyQuote(
        text="The true measure of any society can be found in how it treats its most vulnerable members.",
        author="Mahatma Gandhi",
        g_star=0.51,
        band=2,
        category="justice",
        civilization="Contemporary_Global",
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BAND 3: Discipline/Power (0.60-0.80) — Execution, Systems, Craft
    # ═══════════════════════════════════════════════════════════════════════════
    PhilosophyQuote(
        text="Build less, build right.",
        author="arifOS Principle",
        g_star=0.70,
        band=3,
        category="discipline",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Premature optimization is the root of all evil.",
        author="Donald Knuth",
        g_star=0.72,
        band=3,
        category="discipline",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="The best way to predict the future is to invent it.",
        author="Alan Kay",
        g_star=0.68,
        band=3,
        category="power",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="Simplicity is the ultimate sophistication.",
        author="Leonardo da Vinci",
        g_star=0.75,
        band=3,
        category="discipline",
        civilization="European_Enlightenment",
    ),
    PhilosophyQuote(
        text="Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away.",
        author="Antoine de Saint-Exupéry",
        g_star=0.78,
        band=3,
        category="discipline",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Talk is cheap. Show me the code.",
        author="Linus Torvalds",
        g_star=0.65,
        band=3,
        category="discipline",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Software is like entropy: It is difficult to grasp, weighs nothing, and obeys the Second Law of Thermodynamics; i.e., it always increases.",
        author="Norman Augustine",
        g_star=0.62,
        band=3,
        category="discipline",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="The most effective debugging tool is still careful thought, coupled with judiciously placed print statements.",
        author="Brian Kernighan",
        g_star=0.71,
        band=3,
        category="discipline",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="Any sufficiently complicated concurrent program contains an ad hoc informally-specified bug-ridden slow implementation of half of a proper synchronization protocol.",
        author="J.B. Crawford",
        g_star=0.66,
        band=3,
        category="discipline",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="The purpose of software engineering is to control complexity, not to create it.",
        author="Pamela Zave",
        g_star=0.74,
        band=3,
        category="discipline",
        civilization="Modern_Scientific",
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BAND 4: Seal/Power (0.80-1.00) — Mastery, Completion, Authority
    # ═══════════════════════════════════════════════════════════════════════════
    PhilosophyQuote(
        text="What gets measured gets managed.",
        author="Peter Drucker",
        g_star=0.91,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="The difference between something good and something great is attention to detail.",
        author="Charles R. Swindoll",
        g_star=0.85,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Excellence is not a singular act, but a habit. You are what you repeatedly do.",
        author="Aristotle",
        g_star=0.88,
        band=4,
        category="seal",
        civilization="Ancient_West",
        source="Nicomachean Ethics"
    ),
    PhilosophyQuote(
        text="The master has failed more times than the beginner has even tried.",
        author="Stephen McCranie",
        g_star=0.82,
        band=4,
        category="power",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="We are what we repeatedly do. Excellence, then, is not an act, but a habit.",
        author="Will Durant (on Aristotle)",
        g_star=0.87,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Success is the sum of small efforts, repeated day in and day out.",
        author="Robert Collier",
        g_star=0.84,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="It does not matter how slowly you go as long as you do not stop.",
        author="Confucius",
        g_star=0.86,
        band=4,
        category="power",
        civilization="Ancient_East",
    ),
    PhilosophyQuote(
        text="Quality is not an act, it is a habit.",
        author="Aristotle",
        g_star=0.89,
        band=4,
        category="seal",
        civilization="Ancient_West",
    ),
    PhilosophyQuote(
        text="The only way to do great work is to love what you do.",
        author="Steve Jobs",
        g_star=0.83,
        band=4,
        category="power",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="There are no secrets to success. It is the result of preparation, hard work, and learning from failure.",
        author="Colin Powell",
        g_star=0.92,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL QUOTES FOR DIVERSITY (remaining ~50)
    # ═══════════════════════════════════════════════════════════════════════════
    # More Band 0
    PhilosophyQuote(
        text="The more you know, the more you realize you don't know.",
        author="Aristotle",
        g_star=0.19,
        band=0,
        category="void",
        civilization="Ancient_West",
    ),
    PhilosophyQuote(
        text="He who knows does not speak. He who speaks does not know.",
        author="Laozi",
        g_star=0.11,
        band=0,
        category="void",
        civilization="Ancient_East",
        source="Tao Te Ching"
    ),
    PhilosophyQuote(
        text="The only true wisdom is in knowing you know nothing.",
        author="Socrates",
        g_star=0.17,
        band=0,
        category="void",
        civilization="Ancient_West",
    ),
    
    # More Band 1
    PhilosophyQuote(
        text="Extraordinary claims require extraordinary evidence.",
        author="Carl Sagan",
        g_star=0.31,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="It is the mark of an educated mind to be able to entertain a thought without accepting it.",
        author="Aristotle",
        g_star=0.39,
        band=1,
        category="truth",
        civilization="Ancient_West",
    ),
    PhilosophyQuote(
        text="Doubt is not a pleasant condition, but certainty is absurd.",
        author="Voltaire",
        g_star=0.26,
        band=1,
        category="truth",
        civilization="European_Enlightenment",
    ),
    PhilosophyQuote(
        text="The universe is not only queerer than we suppose, but queerer than we can suppose.",
        author="J.B.S. Haldane",
        g_star=0.23,
        band=1,
        category="paradox",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="If you cannot explain it simply, you don't understand it well enough.",
        author="Albert Einstein",
        g_star=0.37,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
    ),
    
    # More Band 2
    PhilosophyQuote(
        text="The measure of intelligence is the ability to change.",
        author="Albert Einstein",
        g_star=0.46,
        band=2,
        category="wisdom",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="Wise men speak because they have something to say; Fools because they have to say something.",
        author="Plato",
        g_star=0.44,
        band=2,
        category="wisdom",
        civilization="Ancient_West",
    ),
    PhilosophyQuote(
        text="He who has a why to live can bear almost any how.",
        author="Friedrich Nietzsche",
        g_star=0.42,
        band=2,
        category="wisdom",
        civilization="European_Enlightenment",
        source="Twilight of the Idols"
    ),
    PhilosophyQuote(
        text="The best time to plant a tree was 20 years ago. The second best time is now.",
        author="Chinese Proverb",
        g_star=0.56,
        band=2,
        category="wisdom",
        civilization="Ancient_East",
    ),
    PhilosophyQuote(
        text="Your silence will not protect you.",
        author="Audre Lorde",
        g_star=0.54,
        band=2,
        category="justice",
        civilization="Contemporary_Global",
    ),
    
    # More Band 3
    PhilosophyQuote(
        text="Simplicity is prerequisite for reliability.",
        author="Edsger Dijkstra",
        g_star=0.77,
        band=3,
        category="discipline",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="Deleted code is debugged code.",
        author="Jeff Sickel",
        g_star=0.69,
        band=3,
        category="discipline",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Weeks of programming can save you hours of planning.",
        author="Unknown",
        g_star=0.63,
        band=3,
        category="discipline",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="The most damaging phrase in the language is: 'It's always been done that way.'",
        author="Grace Hopper",
        g_star=0.67,
        band=3,
        category="discipline",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="A good programmer is someone who always looks both ways before crossing a one-way street.",
        author="Doug Linder",
        g_star=0.61,
        band=3,
        category="discipline",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="One accurate measurement is worth a thousand expert opinions.",
        author="Grace Hopper",
        g_star=0.76,
        band=3,
        category="discipline",
        civilization="Modern_Scientific",
    ),
    
    # More Band 4
    PhilosophyQuote(
        text="First, solve the problem. Then, write the code.",
        author="John Johnson",
        g_star=0.90,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Make it work, make it right, make it fast.",
        author="Kent Beck",
        g_star=0.81,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="The only constant in software is change.",
        author="Unknown",
        g_star=0.79,
        band=3,
        category="discipline",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Good code is its own best documentation.",
        author="Steve McConnell",
        g_star=0.93,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    PhilosophyQuote(
        text="Simplicity is the soul of efficiency.",
        author="Austin Freeman",
        g_star=0.80,
        band=4,
        category="seal",
        civilization="Contemporary_Global",
    ),
    
    # Additional diverse quotes
    PhilosophyQuote(
        text="He who would learn to fly one day must first learn to stand and walk and run and climb and dance; one cannot fly into flying.",
        author="Friedrich Nietzsche",
        g_star=0.59,
        band=2,
        category="wisdom",
        civilization="European_Enlightenment",
    ),
    PhilosophyQuote(
        text="Nature does not hurry, yet everything is accomplished.",
        author="Laozi",
        g_star=0.43,
        band=2,
        category="wisdom",
        civilization="Ancient_East",
    ),
    PhilosophyQuote(
        text="Knowing is not enough; we must apply. Willing is not enough; we must do.",
        author="Johann Wolfgang von Goethe",
        g_star=0.64,
        band=3,
        category="discipline",
        civilization="European_Enlightenment",
    ),
    PhilosophyQuote(
        text="Tell me and I forget. Teach me and I remember. Involve me and I learn.",
        author="Benjamin Franklin",
        g_star=0.41,
        band=2,
        category="wisdom",
        civilization="European_Enlightenment",
    ),
    PhilosophyQuote(
        text="Life is really simple, but we insist on making it complicated.",
        author="Confucius",
        g_star=0.36,
        band=1,
        category="paradox",
        civilization="Ancient_East",
    ),
    PhilosophyQuote(
        text="The journey of a thousand miles begins with one step.",
        author="Laozi",
        g_star=0.57,
        band=2,
        category="wisdom",
        civilization="Ancient_East",
    ),
    PhilosophyQuote(
        text="That which does not kill us makes us stronger.",
        author="Friedrich Nietzsche",
        g_star=0.40,
        band=2,
        category="power",
        civilization="European_Enlightenment",
    ),
    PhilosophyQuote(
        text="Everything should be made as simple as possible, but not simpler.",
        author="Albert Einstein",
        g_star=0.73,
        band=3,
        category="discipline",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="The greatest enemy of knowledge is not ignorance, it is the illusion of knowledge.",
        author="Stephen Hawking",
        g_star=0.24,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="Programs must be written for people to read, and only incidentally for machines to execute.",
        author="Harold Abelson",
        g_star=0.94,
        band=4,
        category="seal",
        civilization="Modern_Scientific",
        source="SICP"
    ),
    PhilosophyQuote(
        text="Computer science is no more about computers than astronomy is about telescopes.",
        author="Edsger Dijkstra",
        g_star=0.34,
        band=1,
        category="truth",
        civilization="Modern_Scientific",
    ),
    PhilosophyQuote(
        text="Controlling complexity is the essence of computer programming.",
        author="Brian Kernighan",
        g_star=0.95,
        band=4,
        category="seal",
        civilization="Modern_Scientific",
    ),
]


def get_quote_by_g_star(g_star: float) -> PhilosophyQuote:
    """
    Get the quote closest to the given G★ score.
    
    Args:
        g_star: A value between 0.0 and 1.0
        
    Returns:
        The PhilosophyQuote with the closest G★ score
    """
    # Clamp to valid range
    g_star = max(0.0, min(1.0, g_star))
    
    # Find closest quote
    closest = min(PHILOSOPHY_REGISTRY, key=lambda q: abs(q.g_star - g_star))
    return closest


def get_quotes_by_band(band: int) -> list[PhilosophyQuote]:
    """Get all quotes in a specific G★ band (0-4)."""
    return [q for q in PHILOSOPHY_REGISTRY if q.band == band]


def get_quotes_by_category(category: str) -> list[PhilosophyQuote]:
    """Get all quotes in a specific category."""
    return [q for q in PHILOSOPHY_REGISTRY if q.category == category]


def calculate_g_star_from_tom(
    confidence: float,
    alternatives_count: int,
    has_assumptions: bool,
    has_second_order_effects: bool = False,
    consistency_check: bool = True,
) -> float:
    """
    Calculate G★ score from ToM input quality.
    
    This is the core function that maps ToM externalization to
    constitutional alignment (G★).
    
    Args:
        confidence: Self-reported confidence (0.0-1.0)
        alternatives_count: Number of alternative hypotheses considered
        has_assumptions: Whether assumptions were declared
        has_second_order_effects: Whether second-order effects were modeled
        consistency_check: Whether reasoning passed consistency check
        
    Returns:
        G★ score (0.0-1.0)
    """
    # Base score from confidence
    base = confidence
    
    # Adjust based on alternatives (intellectual honesty)
    if alternatives_count >= 3:
        base += 0.05
    elif alternatives_count >= 2:
        base += 0.02
    else:
        base -= 0.10  # Penalty for not considering alternatives
    
    # Adjust for assumptions declaration
    if has_assumptions:
        base += 0.05
    else:
        base -= 0.15
    
    # Adjust for second-order thinking
    if has_second_order_effects:
        base += 0.05
    
    # Adjust for consistency
    if not consistency_check:
        base -= 0.20
    
    # Clamp to valid range
    return max(0.0, min(1.0, base))


def get_registry_stats() -> dict:
    """Get statistics about the philosophy registry."""
    total = len(PHILOSOPHY_REGISTRY)
    bands = {i: len(get_quotes_by_band(i)) for i in range(5)}
    categories = {}
    civilizations = {}
    
    for q in PHILOSOPHY_REGISTRY:
        categories[q.category] = categories.get(q.category, 0) + 1
        civilizations[q.civilization] = civilizations.get(q.civilization, 0) + 1
    
    # Calculate diversity score (Simpson's diversity index)
    cat_probs = [c / total for c in categories.values()]
    diversity = 1 - sum(p * p for p in cat_probs)
    
    return {
        "total_quotes": total,
        "band_distribution": bands,
        "category_distribution": categories,
        "civilization_distribution": civilizations,
        "diversity_score": round(diversity, 2),
        "target_diversity": 0.80,
        "version": "1.2.0",
    }


# Export
__all__ = [
    "PhilosophyQuote",
    "GBand",
    "PHILOSOPHY_REGISTRY",
    "get_quote_by_g_star",
    "get_quotes_by_band",
    "get_quotes_by_category",
    "calculate_g_star_from_tom",
    "get_registry_stats",
]

# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTION-READY PHILOSOPHY INJECTION (v1.2.0)
# ═══════════════════════════════════════════════════════════════════════════════
# 
# First Principle: Philosophy is post-verdict symbolic projection.
# 
# Rules:
#   1. NEVER affects scoring
#   2. NEVER affects routing  
#   3. NEVER affects floors
#   4. NEVER affects verdict
#   5. ALWAYS deterministic
#
# Single injection point: runtime/tools_internal.py → _wrap_call()
# ═══════════════════════════════════════════════════════════════════════════════

import logging
import hashlib
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arifosmcp.runtime.models import RuntimeEnvelope

logger = logging.getLogger(__name__)

# S1: THE FORGE PRINCIPLE — Identity Anchor
# Returned unconditionally for INIT stage or SEAL verdict
FORGE_PRINCIPLE_S1 = asdict(PHILOSOPHY_REGISTRY[0])  # First entry is S1

# Allowed categories per band (seal excluded from random selection)
BAND_CATEGORIES = {
    0: ["void", "paradox"],
    1: ["paradox", "truth"],
    2: ["wisdom", "justice"],
    3: ["discipline", "power"],
    4: ["power"],  # seal excluded unless override
}


def _get_s1_selection(mode: str, g_star: float = 1.0) -> dict:
    """Return S1 (Forge Principle) selection."""
    return {
        "entry": FORGE_PRINCIPLE_S1,
        "selection_reason": "Forge Principle — Identity anchor for " + mode,
        "selection_mode": f"override_{mode}",
        "band": "INIT" if mode == "init" else "SEAL",
        "g_star": g_star,
        "schema_version": "1.2.0",
        "registry_version": "1.2.0",
    }


def _compute_g_band(g_star: float) -> int:
    """
    Compute G★ band from score.
    
    Band mapping:
        0.00-0.20 → Band 0 (void/paradox)
        0.20-0.40 → Band 1 (paradox/truth)
        0.40-0.60 → Band 2 (wisdom/justice)
        0.60-0.80 → Band 3 (discipline/power)
        0.80-1.00 → Band 4 (power, seal excluded)
    """
    return min(int(5 * g_star), 4)


def _select_by_g_band(
    g_star: float,
    session_id: str,
    registry: list[PhilosophyQuote] | None = None,
) -> dict:
    """
    Select philosophy by G★ band with deterministic hashing.
    
    Args:
        g_star: G★ score (0.0-1.0)
        session_id: Session ID for deterministic hash
        registry: Quote registry (defaults to PHILOSOPHY_REGISTRY)
        
    Returns:
        Philosophy selection dict
    """
    band = _compute_g_band(g_star)
    allowed = BAND_CATEGORIES.get(band, ["wisdom"])
    
    # Filter candidates (exclude S1 from random selection)
    candidates = [
        q for q in (registry or PHILOSOPHY_REGISTRY)[1:]  # Skip S1
        if q.category in allowed
    ]
    
    if not candidates:
        candidates = (registry or PHILOSOPHY_REGISTRY)[1:]
    
    # Deterministic selection: SHA256(session_id + band)
    seed = hashlib.sha256(f"{session_id}:{band}".encode()).hexdigest()
    idx = int(seed, 16) % len(candidates)
    
    band_reasons = {
        0: "G★ void/paradox zone — humility in uncertainty",
        1: "G★ reflection zone — wisdom through doubt",
        2: "G★ integration zone — balance and governance",
        3: "G★ discipline zone — execution and craft",
        4: "G★ power zone — mastery without seal",
    }
    
    return {
        "entry": asdict(candidates[idx]),
        "selection_reason": band_reasons.get(band, "G★-based selection"),
        "selection_mode": "g_band",
        "band": band,
        "g_star": round(g_star, 4),
        "schema_version": "1.2.0",
        "registry_version": "1.2.0",
    }


def inject_philosophy(
    envelope: "RuntimeEnvelope",
    registry: list[PhilosophyQuote] | None = None,
) -> dict:
    """
    Inject philosophy into RuntimeEnvelope — PRODUCTION VERSION.
    
    This is the SINGLE canonical injection point. All philosophy flows through here.
    
    Logic:
        1. If stage == "INIT" → Return S1 (Forge Principle)
        2. If verdict == "SEAL" → Return S1 (Forge Principle)
        3. Otherwise → G★ band mapping with deterministic selection
    
    Args:
        envelope: RuntimeEnvelope with stage, verdict, metrics.telemetry.G_star
        registry: Optional custom quote registry
        
    Returns:
        PhilosophySelection dict (always deterministic)
        
    Safety:
        - Never raises (returns error dict on failure)
        - Never modifies envelope directly
        - Never accesses routing or scoring logic
    """
    try:
        stage = getattr(envelope, 'stage', None)
        verdict = getattr(envelope, 'verdict', None)
        session_id = getattr(envelope, 'session_id', 'default-session')
        
        # Get G★ from envelope metrics
        g_star = 0.5  # Default
        metrics = getattr(envelope, 'metrics', None)
        if metrics:
            telemetry = getattr(metrics, 'telemetry', None)
            if telemetry:
                g_star = getattr(telemetry, 'G_star', 0.5)
        
        # RULE 1: INIT override
        if stage == "INIT":
            return _get_s1_selection("init", g_star)
        
        # RULE 2: SEAL override
        if verdict == "SEAL":
            return _get_s1_selection("seal", g_star)
        
        # RULE 3: G★ band mapping
        return _select_by_g_band(g_star, session_id, registry)
        
    except Exception as e:
        logger.warning(f"Philosophy injection failed (non-blocking): {e}")
        # Return error state that won't crash the system
        return {
            "entry": FORGE_PRINCIPLE_S1,
            "selection_reason": f"Fallback due to error: {str(e)[:50]}",
            "selection_mode": "error_fallback",
            "band": "ERROR",
            "g_star": 0.0,
            "schema_version": "1.2.0",
            "registry_version": "1.2.0",
            "error": str(e),
        }


# Telemetry logging helper
def log_philosophy_selection(
    selection: dict,
    session_id: str,
    timestamp: str | None = None,
) -> dict:
    """
    Create telemetry log entry for philosophy selection.
    
    Returns engineering-layer telemetry dict.
    """
    import time
    
    return {
        "timestamp": timestamp or time.time(),
        "session_id": session_id,
        "g_star": selection.get("g_star"),
        "band": selection.get("band"),
        "quote_id": selection.get("entry", {}).get("source", "unknown"),
        "selection_mode": selection.get("selection_mode"),
        "registry_version": selection.get("registry_version", "1.2.0"),
        "override_type": selection.get("selection_mode") if "override" in selection.get("selection_mode", "") else None,
    }


# Production exports — ONLY the clean injection function
__all__.extend([
    "inject_philosophy",
    "log_philosophy_selection",
    "BAND_CATEGORIES",
    "FORGE_PRINCIPLE_S1",
])
