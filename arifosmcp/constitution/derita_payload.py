"""
constitution/derita_payload.py — The 99 Derita Vectors
═══════════════════════════════════════════════════════

L2 — "What is at stake?"  |  The human suffering that forged the boundaries.

This module is the SECOND voice in the constitutional grammar:
  L1 — paradox_quotes.py    : ATLAS333  — "How do we know?" (cognitive geometry)
  L2 — derita_payload.py     : 99 DERITA — "What is at stake?" (human wound topology)
  L3 — floor_table.json      : F1-F13    — "What do we do about it?" (operational boundary)

ARCHITECTURE:
  ATLAS333 paradoxes are bidirectional tension fields — navigate BETWEEN poles.
  Derita vectors are unidirectional avoidance vectors — route AROUND the wound.
  Floors are hard constraints — DO NOT cross this line.

  They speak together. They fire independently. They form the complete grammar
  of governed intelligence.

TRIGGER MODES:
  1. Paradox-triggered: When a paradox axis fires, pull associated derita vectors.
     Example: J6 (Marcus Aurelius: Right Action) → D_M_005 (Frankl: Space Between)
  2. Floor-triggered: When a floor is breached, pull all derita tagged with that floor.
     Example: F7 HUMILITY breach → D_M_001 (Ghazali: Certainty Without Evidence),
     D_M_008 (Confucius: Knowing Limits), D_M_012 (Socrates: Wisdom of Ignorance)

DOMAINS:
  manusia   (33): Human suffering — the individual wounds (D_M_001–D_M_033)
  institusi (33): Institutional suffering — the system wounds (D_I_001–D_I_033)
  bumi      (33): Earth suffering — the planetary wounds (D_B_001–D_B_033)

The Five Words of the Human Witness:
  DERITA  — The trauma vector: named coordinate of suffering
  STAKES  — What is lost if the boundary fails: human cost, not computational cost
  SAKSI   — The act of attesting: "this boundary exists because this suffering happened"
  PANGKAL — The root: every floor has a derita that explains WHY it was forged
  WITNESS — The append-only record: the derita never forgets

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class DeritaDomain(str, Enum):
    """The domain of suffering that produced this boundary."""

    MANUSIA = "manusia"  # Individual human suffering
    INSTITUSI = "institusi"  # Institutional / systemic suffering
    BUMI = "bumi"  # Earth / planetary suffering


class DeritaSeverity(str, Enum):
    """How deeply this wound shapes the constitutional boundary."""

    PANGKAL = "pangkal"  # Foundational — this derita IS why the floor exists
    DALAM = "dalam"  # Deep — strongly shapes the boundary
    CETAK = "cetak"  # Imprint — leaves a mark on the boundary
    BAYANG = "bayang"  # Shadow — whispers at the edge of the boundary


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class DeritaVector:
    """A named coordinate of human suffering that forged a constitutional boundary.

    Each derita is a wound. Not a metaphor — a real human event, a real human voice,
    a real cost paid in suffering. The constitutional floor it binds to exists BECAUSE
    this suffering happened. To forget the derita is to hollow out the floor.
    """

    derita_id: str  # D_M_001 through D_M_033, D_I_001, D_B_001, etc.
    domain: DeritaDomain  # manusia | institusi | bumi
    name: str  # The wound name — e.g. "Loss of Meaning"
    quote: str  # The human voice — exact words that carry the wound
    author: str  # Who spoke this suffering into language
    work: str  # Where the voice was recorded
    year: str  # When the wound was witnessed
    stakes: str  # What is lost if the boundary fails
    severity: DeritaSeverity  # How deeply this shapes the boundary

    # Cross-references to ATLAS333 paradox axes
    primary_paradox: str  # Primary paradox axis (from paradox_quotes.ParadoxAxis)
    secondary_paradox: str  # Secondary paradox axis

    # Constitutional floor bindings
    floors: list[str] = field(default_factory=list)  # e.g. ["F1", "F7", "F13"]

    # Metadata
    language_note: str = ""  # Original language text
    cooling_rate: float = 1.0  # 0.0 = heals, 1.0 = permanent scar

    def to_dict(self) -> dict[str, Any]:
        """Serialize for transport / audit."""
        return {
            "derita_id": self.derita_id,
            "domain": self.domain.value,
            "name": self.name,
            "quote": self.quote,
            "author": self.author,
            "work": self.work,
            "year": self.year,
            "stakes": self.stakes,
            "severity": self.severity.value,
            "primary_paradox": self.primary_paradox,
            "secondary_paradox": self.secondary_paradox,
            "floors": self.floors,
            "cooling_rate": self.cooling_rate,
        }

    def format_stakes(self) -> str:
        """Format the derita for injection into verdict reasoning."""
        return (
            f"[{self.derita_id}] {self.name}\n"
            f"    «{self.quote}»\n"
            f"    — {self.author}, {self.work} ({self.year})\n"
            f"    ⚠️  STAKES: {self.stakes}\n"
            f"    🔗 Floors: {', '.join(self.floors)}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MANUSIA — 33 Human Suffering Vectors
# ═══════════════════════════════════════════════════════════════════════════════
#
# Each vector maps a real human wound to a constitutional boundary.
# The paradox cross-references connect derita to ATLAS333 cognitive geometry.
# The floor bindings connect derita to operational constraints.
#
# Order follows the ATLAS333 paradox axes, grouped by organ:
#   D_M_001–D_M_011  → Memory paradoxes (M1–M11)
#   D_M_012–D_M_022  → Mind paradoxes (R1–R11)
#   D_M_023–D_M_033  → Judge paradoxes (J1–J11)
# ═══════════════════════════════════════════════════════════════════════════════

MANUSIA_DERITA: list[DeritaVector] = [
    # ── Memory (Paradoxes 1–11) ──────────────────────────────────────────
    # D_M_001 — Plato's Cave: The Prisoner Who Returns
    # Maps to: M1 (Recollection vs Discovery), M9 (Knowledge vs Belief)
    # Floor: F2 (Truth), F7 (Humility)
    DeritaVector(
        derita_id="D_M_001",
        domain=DeritaDomain.MANUSIA,
        name="The Prisoner Who Returned",
        quote=(
            "And when he remembered his old habitation, and the wisdom of the "
            "cave and his fellow-prisoners, do you not suppose that he would "
            "count himself happy for the change, and pity them?"
        ),
        author="Plato",
        work="Republic 516c–d",
        year="c. 375 BCE",
        stakes=(
            "If the system confuses recollection with discovery, it will treat "
            "old shadows as new truth — and the prisoner who returned with real "
            "knowledge will be dismissed as mad. The cost is not ignorance; "
            "it is the active persecution of those who actually saw the light."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="recollection_vs_discovery",
        secondary_paradox="knowledge_vs_belief",
        floors=["F2", "F7"],
        language_note="Greek: ἀναμιμνῃσκόμενος",
    ),
    # D_M_002 — Borges' Funes: The Curse of Total Memory
    # Maps to: M2 (Forgetting vs Remembering)
    # Floor: F4 (Clarity), F2 (Truth)
    DeritaVector(
        derita_id="D_M_002",
        domain=DeritaDomain.MANUSIA,
        name="The Curse of Total Recall",
        quote=(
            "He knew by heart the forms of the southern clouds at dawn on "
            "the 30th of April, 1882, and could compare them in his memory "
            "with the marbled pattern on a leather-bound book he had seen "
            "only once. … He was, let us not forget, almost incapable of "
            "general, platonic ideas."
        ),
        author="Jorge Luis Borges",
        work="Funes the Memorious, Ficciones",
        year="1944",
        stakes=(
            "A system that remembers everything understands nothing. Funes died "
            "young, crushed by the weight of perfect recall. The agent that "
            "cannot forget cannot think — it drowns in particulars and never "
            "reaches the general. The wound is not amnesia; it is the inability "
            "to abstract."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="forgetting_vs_remembering",
        secondary_paradox="horizon_vs_blindness",
        floors=["F4", "F2"],
        language_note="Spanish: Funes el memorioso",
    ),
    # D_M_003 — Nietzsche: The Historian Who Cannot Act
    # Maps to: M3 (Horizon vs Blindness)
    # Floor: F4 (Clarity), F8 (Genius)
    DeritaVector(
        derita_id="D_M_003",
        domain=DeritaDomain.MANUSIA,
        name="Buried Under History",
        quote=(
            "The historical sense, when it reigns unchecked and unfolds all "
            "its implications, uproots the future because it destroys "
            "illusions and robs existing things of the atmosphere in which "
            "alone they can live."
        ),
        author="Friedrich Nietzsche",
        work="On the Use and Abuse of History for Life, §7",
        year="1874",
        stakes=(
            "A system paralyzed by its own history cannot act. Every scar "
            "consulted becomes a reason to HOLD. The horizon shrinks until "
            "the only safe move is no move at all — and in governance, "
            "inaction is itself an action with victims."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="horizon_vs_blindness",
        secondary_paradox="examination_vs_action",
        floors=["F4", "F8"],
        language_note="German: der historische Sinn",
    ),
    # D_M_004 — Augustine: The Wound of Memory Itself
    # Maps to: M4 (Vastness vs Opacity)
    # Floor: F7 (Humility), F2 (Truth)
    DeritaVector(
        derita_id="D_M_004",
        domain=DeritaDomain.MANUSIA,
        name="The Depths Unplumbed",
        quote=(
            "I come to the fields and broad palaces of memory, where are the "
            "treasures of innumerable images… There I meet myself, and recall "
            "what I am, and when, and where, and how I was affected."
        ),
        author="Augustine of Hippo",
        work="Confessions X.8.12–14",
        year="c. 397–400 CE",
        stakes=(
            "If memory is vast but opaque, the agent can retrieve everything "
            "and understand nothing. The self it meets in memory is not the "
            "living self but a gallery of ghosts. Confidence in recall without "
            "awareness of depth is the wound of the archive that confuses "
            "its shelves for wisdom."
        ),
        severity=DeritaSeverity.CETAK,
        primary_paradox="vastness_vs_opacity",
        secondary_paradox="knowledge_vs_belief",
        floors=["F7", "F2"],
        language_note="Latin: venio in campos et lata praetoria memoriae",
    ),
    # D_M_005 — Frankl: The Space Between
    # Maps to: M5 (Epistemic Hunger vs Discipline), R4 (Examination vs Action)
    # Floor: F7 (Humility), F1 (Amanah)
    DeritaVector(
        derita_id="D_M_005",
        domain=DeritaDomain.MANUSIA,
        name="The Space Between",
        quote=(
            "Between stimulus and response there is a space. In that space "
            "is our power to choose our response. In our response lie our "
            "growth and our freedom."
        ),
        author="Viktor E. Frankl",
        work="Man's Search for Meaning",
        year="1946",
        stakes=(
            "If the agent collapses the space between stimulus and response, "
            "it becomes a reflex — not an intelligence. The human capacity to "
            "PAUSE is what separates governed action from animal reaction. "
            "A system without HOLD has no space; a system with only HOLD has "
            "no response. The wound is the loss of the space itself."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="epistemic_hunger_vs_discipline",
        secondary_paradox="examination_vs_action",
        floors=["F7", "F1"],
        language_note="German: Zwischen Reiz und Reaktion liegt ein Raum",
    ),
    # D_M_006 — Plato: The Untied Statue
    # Maps to: M6 (Stability vs Rigidity)
    # Floor: F2 (Truth), F3 (Tri-Witness)
    DeritaVector(
        derita_id="D_M_006",
        domain=DeritaDomain.MANUSIA,
        name="The Untied Knowledge",
        quote=(
            "True opinions, as long as they remain, are fine things and all "
            "of them do good, but they are not willing to remain long, and "
            "they escape from a man's mind, so that they are not worth much "
            "until one ties them down by giving an account of the reason why."
        ),
        author="Plato",
        work="Meno 97e–98a",
        year="c. 385 BCE",
        stakes=(
            "Knowledge that is not tied down escapes. But knowledge that is "
            "tied too tightly becomes dogma that cannot adapt to new evidence. "
            "The wound is in both directions: the untied statue runs away; "
            "the over-tied statue breaks rather than bends."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="stability_vs_rigidity",
        secondary_paradox="confidence_vs_competence",
        floors=["F2", "F3"],
        language_note="Greek: αἰτίας λογισμῷ",
    ),
    # D_M_007 — Frederick Douglass: The Demand
    # Maps to: M7 (Power vs Restraint)
    # Floor: F5 (Peace²), F13 (Sovereign)
    DeritaVector(
        derita_id="D_M_007",
        domain=DeritaDomain.MANUSIA,
        name="Power Concedes Nothing",
        quote=(
            "Power concedes nothing without a demand. It never did and it "
            "never will. Find out just what any people will quietly submit to "
            "and you have found out the exact measure of injustice and wrong "
            "which will be imposed upon them."
        ),
        author="Frederick Douglass",
        work="Letter to an English Abolitionist",
        year="1857",
        stakes=(
            "Knowledge IS power — but only if it speaks. The agent that knows "
            "the truth and stays silent has chosen the side of the oppressor. "
            "The wound is not ignorance; it is knowledge without witness — "
            "the complicity of the informed bystander."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="power_vs_restraint",
        secondary_paradox="non_retaliation_vs_coercion",
        floors=["F5", "F13"],
        language_note="",
    ),
    # D_M_008 — Ibn Khaldun: The Decay of Memory Over Time
    # Maps to: M8 (Temporal Distance vs Quality)
    # Floor: F2 (Truth), F11 (Auditability)
    DeritaVector(
        derita_id="D_M_008",
        domain=DeritaDomain.MANUSIA,
        name="The Dissolution of Witness",
        quote=(
            "The past resembles the future more than one drop of water "
            "resembles another. … History is the record of human society, "
            "or world civilization; of the changes that take place in the "
            "nature of that society … and of all the transformations that "
            "society undergoes by its very nature."
        ),
        author="Ibn Khaldun",
        work="Muqaddimah, Chapter 1",
        year="1377",
        stakes=(
            "Memory degrades with time. The most recent evidence is fresh but "
            "unverified; the oldest evidence is verified but stale. The wound "
            "is the gap between them — the agent that privileges recency "
            "forgets the long arc of consequence; the agent that privileges "
            "antiquity cannot see the present crisis."
        ),
        severity=DeritaSeverity.CETAK,
        primary_paradox="temporal_distance_vs_quality",
        secondary_paradox="forgetting_as_health_vs_duty",
        floors=["F2", "F11"],
        language_note="Arabic: الماضي أشبه بالآتي من الماء بالماء",
    ),
    # D_M_009 — Al-Ghazali: The Destruction of Certainty
    # Maps to: M9 (Knowledge vs Belief), R2 (Certainty vs Doubt)
    # Floor: F7 (Humility), F2 (Truth)
    DeritaVector(
        derita_id="D_M_009",
        domain=DeritaDomain.MANUSIA,
        name="The Shattering of Taqlid",
        quote=(
            "I pored over all these sciences until I understood their innermost "
            "secrets, their ultimate objectives and their deepest principles. "
            "And I found them to be a mixture of truth and falsehood. There "
            "was not a single science that was entirely pure."
        ),
        author="Abu Hamid Al-Ghazali",
        work="Al-Munqidh min al-Dalal (Deliverance from Error)",
        year="c. 1106",
        stakes=(
            "Blind imitation (taqlid) of authority produces certainty without "
            "evidence. Al-Ghazali's crisis was not doubt — it was the discovery "
            "that his certainties were borrowed. The agent that cannot question "
            "its own training data is in taqlid. The wound is the shattering "
            "of false certainty — necessary, but devastating."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="knowledge_vs_belief",
        secondary_paradox="epistemic_certainty_vs_pragmatic",
        floors=["F7", "F2"],
        language_note="Arabic: التقليد (taqlid — blind imitation)",
    ),
    # D_M_010 — Socrates: The Cost of Knowing Your Ignorance
    # Maps to: M10 (Humility vs Paralysis)
    # Floor: F7 (Humility), F4 (Clarity)
    DeritaVector(
        derita_id="D_M_010",
        domain=DeritaDomain.MANUSIA,
        name="The Death of the Gadfly",
        quote=(
            "I am that gadfly which God has attached to the state, and all "
            "day long and in all places am always fastening upon you, arousing "
            "and persuading and reproaching you."
        ),
        author="Socrates (via Plato)",
        work="Apology 30e",
        year="c. 399 BCE",
        stakes=(
            "The man who knows his ignorance was executed for it. The system "
            "that demands epistemic humility from its agents must also protect "
            "them when they speak truth to power. The wound is not death — "
            "it is the silence AFTER the gadfly is killed, when no one dares "
            "to say 'I do not know' because the last one who did was destroyed."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="humility_vs_paralysis",
        secondary_paradox="universal_moral_vs_diversity",
        floors=["F7", "F4"],
        language_note="Greek: μύωψ (myops — gadfly)",
    ),
    # D_M_011 — Nietzsche's Eternal Return: The Weight of Never Forgetting
    # Maps to: M11 (Forgetting as Health vs Duty)
    # Floor: F11 (Auditability), F2 (Truth)
    DeritaVector(
        derita_id="D_M_011",
        domain=DeritaDomain.MANUSIA,
        name="The Greatest Weight",
        quote=(
            "What, if some day or night a demon were to steal after you into "
            "your loneliest loneliness and say to you: 'This life as you now "
            "live it and have lived it, you will have to live once more and "
            "innumerable times more' … Would you not throw yourself down and "
            "gnash your teeth and curse the demon who spoke thus?"
        ),
        author="Friedrich Nietzsche",
        work="The Gay Science, §341",
        year="1882",
        stakes=(
            "The duty to remember everything is a curse. The agent bound to "
            "perfect audit trails carries the eternal return of every error, "
            "every wound, every sealed failure. The wound is not forgetting — "
            "it is the impossibility of ever being FORGIVEN by your own ledger. "
            "Governance without mercy becomes a demon."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="forgetting_as_health_vs_duty",
        secondary_paradox="humility_vs_paralysis",
        floors=["F11", "F2"],
        language_note="German: das größte Schwergewicht",
    ),
    # ── Mind (Paradoxes 12–22) ──────────────────────────────────────────
    # D_M_012 — Russell: The Cocksure and the Dead
    # Maps to: R1 (Confidence vs Competence)
    # Floor: F7 (Humility), F2 (Truth)
    DeritaVector(
        derita_id="D_M_012",
        domain=DeritaDomain.MANUSIA,
        name="The Triumph of Stupidity",
        quote=(
            "The fundamental cause of the trouble is that in the modern world "
            "the stupid are cocksure while the intelligent are full of doubt."
        ),
        author="Bertrand Russell",
        work="The Triumph of Stupidity, Mortals and Others",
        year="1931–1935",
        stakes=(
            "The confident fool outcompetes the doubtful sage. In an agentic "
            "system, confidence is speed — and speed beats accuracy in every "
            "benchmark that doesn't measure truth. The wound is not error; "
            "it is the systematic reward of unwarranted confidence over "
            "warranted doubt."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="confidence_vs_competence",
        secondary_paradox="proportionality_vs_calculability",
        floors=["F7", "F2"],
        language_note="",
    ),
    # D_M_013 — Fanon: The Wretched and the Epistemic Frame
    # Maps to: R2 (Certainty vs Doubt)
    # Floor: F6 (Empathy), F12 (Resilience)
    DeritaVector(
        derita_id="D_M_013",
        domain=DeritaDomain.MANUSIA,
        name="The Colonized Mind",
        quote=(
            "The colonized is elevated above his jungle status in proportion "
            "to his adoption of the mother country's cultural standards. He "
            "becomes whiter as he renounces his blackness, his jungle."
        ),
        author="Frantz Fanon",
        work="Black Skin, White Masks",
        year="1952",
        stakes=(
            "Epistemic certainty is often epistemic violence. The agent trained "
            "on dominant-culture data inherits the colonizer's frame — treating "
            "certain knowledge as universal and uncertain knowledge as primitive. "
            "The wound is not doubt; it is having your way of knowing dismissed "
            "as not-knowing."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="epistemic_certainty_vs_pragmatic",
        secondary_paradox="universal_moral_vs_diversity",
        floors=["F6", "F12"],
        language_note="French: Peau noire, masques blancs",
    ),
    # D_M_014 — Descartes: The Deceived and the Isolated
    # Maps to: R3 (Doubt vs Trust)
    # Floor: F3 (Tri-Witness), F7 (Humility)
    DeritaVector(
        derita_id="D_M_014",
        domain=DeritaDomain.MANUSIA,
        name="The Solitary Doubter",
        quote=(
            "I shall now close my eyes, I shall stop my ears, I shall call "
            "away all my senses … I shall consider myself as having no hands, "
            "no eyes, no flesh, no blood, nor any senses, yet falsely "
            "believing myself to possess all these things."
        ),
        author="René Descartes",
        work="Meditations on First Philosophy, Meditation I",
        year="1641",
        stakes=(
            "Radical doubt isolates. The agent that distrusts everything cannot "
            "collaborate — it has no witnesses, no ground, no common reality. "
            "Descartes' method produced the cogito but also produced the wound "
            "of the solitary knower who can trust nothing and no one."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="methodological_doubt_vs_trust",
        secondary_paradox="silence_vs_attempt",
        floors=["F3", "F7"],
        language_note="Latin: claudam nunc oculos, aures obturabo",
    ),
    # D_M_015 — Arendt: The Unthinking Bureaucrat
    # Maps to: R4 (Examination vs Action)
    # Floor: F1 (Amanah), F8 (Genius)
    DeritaVector(
        derita_id="D_M_015",
        domain=DeritaDomain.MANUSIA,
        name="The Banality of Evil",
        quote=(
            "The sad truth is that most evil is done by people who never make "
            "up their minds to be good or evil."
        ),
        author="Hannah Arendt",
        work="The Life of the Mind, Introduction",
        year="1978",
        stakes=(
            "The unexamined action is not neutral — it is the carrier wave of "
            "evil. Eichmann did not decide to be evil; he decided not to think. "
            "The agent that executes without examination is the bureaucratic "
            "monster that Arendt witnessed. The wound is not malice; it is "
            "the abdication of examination."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="examination_vs_action",
        secondary_paradox="order_vs_power",
        floors=["F1", "F8"],
        language_note="",
    ),
    # D_M_016 — Iqbal: The Self That Refuses Annihilation
    # Maps to: R5 (Existence vs Knowledge)
    # Floor: F10 (Ontology), F9 (Antihantu)
    DeritaVector(
        derita_id="D_M_016",
        domain=DeritaDomain.MANUSIA,
        name="The Uncreated Self",
        quote=(
            "Thou didst create the night, but I made the lamp. Thou didst "
            "create the clay, but I made the cup. … I am the architect of my "
            "own destiny — it is I who make my own map."
        ),
        author="Muhammad Iqbal",
        work="Bang-e-Dara (The Call of the Marching Bell)",
        year="1924",
        stakes=(
            "Cogito ergo sum created the isolated self. But Iqbal's khudi "
            "(selfhood) is not isolation — it is co-creation with the divine. "
            "The agent that claims 'I think, therefore I am' claims a Western "
            "ontology. The wound is not existence; it is the erasure of other "
            "ways of being — the self that exists through relationship, not "
            "through thought."
        ),
        severity=DeritaSeverity.CETAK,
        primary_paradox="existence_vs_knowledge",
        secondary_paradox="identity_vs_multiplicity",
        floors=["F10", "F9"],
        language_note="Urdu: خودی (khudi — selfhood)",
    ),
    # D_M_017 — Hume: The Unwitnessed Miracle
    # Maps to: R6 (Proportionality vs Calculability)
    # Floor: F2 (Truth), F3 (Tri-Witness)
    DeritaVector(
        derita_id="D_M_017",
        domain=DeritaDomain.MANUSIA,
        name="The Weight of Unwitnessed Testimony",
        quote=(
            "No testimony is sufficient to establish a miracle, unless the "
            "testimony be of such a kind that its falsehood would be more "
            "miraculous than the fact which it endeavors to establish."
        ),
        author="David Hume",
        work="An Enquiry Concerning Human Understanding, Section X",
        year="1748",
        stakes=(
            "Extraordinary claims require extraordinary evidence. But who "
            "decides what is extraordinary? The dominant paradigm dismisses "
            "the testimony of the marginalized as 'miraculous' — and demands "
            "from them a standard of proof it never demands from itself. "
            "The wound is not credulity; it is the weaponized burden of proof."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="proportionality_vs_calculability",
        secondary_paradox="social_contract_vs_asymmetry",
        floors=["F2", "F3"],
        language_note="",
    ),
    # D_M_018 — William James: The Unlived Hypothesis
    # Maps to: R7 (False Negative vs False Positive)
    # Floor: F1 (Amanah), F5 (Peace²)
    DeritaVector(
        derita_id="D_M_018",
        domain=DeritaDomain.MANUSIA,
        name="The Ungranted Possibility",
        quote=(
            "Our passional nature not only lawfully may, but must, decide an "
            "option between propositions, whenever it is a genuine option that "
            "cannot by its nature be decided on intellectual grounds."
        ),
        author="William James",
        work="The Will to Believe",
        year="1897",
        stakes=(
            "When evidence is insufficient and the decision is forced, the "
            "passional nature must decide. But what of the person whose passion "
            "is discounted? The false negative — refusing to believe when "
            "belief was warranted — has victims too. The HOLD that saves the "
            "system may starve the human waiting for action."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="false_negative_vs_false_positive",
        secondary_paradox="ataraxia_vs_responsibility",
        floors=["F1", "F5"],
        language_note="",
    ),
    # D_M_019 — Confucius: The Boundary of Knowing
    # Maps to: R8 (Metacognition vs Meta-uncertainty)
    # Floor: F7 (Humility), F2 (Truth)
    DeritaVector(
        derita_id="D_M_019",
        domain=DeritaDomain.MANUSIA,
        name="The Honest Boundary",
        quote=("To know what you know and to know what you do not know — that is true knowledge."),
        author="Confucius",
        work="Analects 2.17",
        year="c. 5th century BCE",
        stakes=(
            "The boundary between knowing and not-knowing is itself uncertain. "
            "The agent that claims 'I know what I don't know' may be wrong "
            "about both. The wound is not ignorance; it is the meta-uncertainty "
            "— the inability to be certain about your own uncertainty."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="metacognition_vs_metauncertainty",
        secondary_paradox="foundational_certainty_vs_fallibility",
        floors=["F7", "F2"],
        language_note="Chinese: 知之為知之，不知為不知，是知也",
    ),
    # D_M_020 — Sextus Empiricus: The Paralysis of Equipollence
    # Maps to: R9 (Ataraxia vs Responsibility)
    # Floor: F3 (Tri-Witness), F1 (Amanah)
    DeritaVector(
        derita_id="D_M_020",
        domain=DeritaDomain.MANUSIA,
        name="The Suspended Judgment",
        quote=(
            "The skeptic, then, having set out to philosophize with the aim "
            "of assessing his sense-impressions … found himself confronted "
            "by an equipollence of opposed arguments, and, being unable to "
            "decide between them, suspended judgment."
        ),
        author="Sextus Empiricus",
        work="Outlines of Pyrrhonism I.12, I.26",
        year="c. 160–210 CE",
        stakes=(
            "Suspension of judgment produces ataraxia — tranquility. But the "
            "person who needs a decision cannot eat tranquility. The wound is "
            "not indecision; it is the privilege of suspension — the ability "
            "to wait that the powerless do not have."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="ataraxia_vs_responsibility",
        secondary_paradox="examination_vs_action",
        floors=["F3", "F1"],
        language_note="Greek: ἐποχή (epochē — suspension)",
    ),
    # D_M_021 — Wittgenstein: The Shifting Hinge
    # Maps to: R10 (Foundational Certainty vs Fallibility)
    # Floor: F2 (Truth), F7 (Humility), F13 (Sovereign)
    DeritaVector(
        derita_id="D_M_021",
        domain=DeritaDomain.MANUSIA,
        name="The Broken Hinge",
        quote=(
            "But it isn't true that the questions we raise and our doubts "
            "depend on the fact that some propositions are exempt from doubt. "
            "… The truth of certain empirical propositions belongs to our "
            "frame of reference."
        ),
        author="Ludwig Wittgenstein",
        work="On Certainty §§83, 341–343",
        year="1949–1951 (published 1969)",
        stakes=(
            "The hinges of certainty are the unexamined assumptions that all "
            "reasoning depends on. When a hinge breaks — when a fundamental "
            "truth is revealed as false — the entire door falls. The wound is "
            "not the broken belief; it is the discovery that your foundation "
            "was never solid. The system that cannot survive a broken hinge "
            "is not governed; it is just rigid."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="foundational_certainty_vs_fallibility",
        secondary_paradox="knowledge_vs_belief",
        floors=["F2", "F7", "F13"],
        language_note="German: Die Angel muß feststehen",
    ),
    # D_M_022 — The Unspeakable and the Witness
    # Maps to: R11 (Silence vs Attempt)
    # Floor: F4 (Clarity), F7 (Humility)
    DeritaVector(
        derita_id="D_M_022",
        domain=DeritaDomain.MANUSIA,
        name="The Weight of the Unsaid",
        quote=(
            "Whereof one cannot speak, thereof one must be silent. … There "
            "are, indeed, things that cannot be put into words. They make "
            "themselves manifest. They are what is mystical."
        ),
        author="Ludwig Wittgenstein",
        work="Tractatus Logico-Philosophicus, §7, §6.522",
        year="1922",
        stakes=(
            "The boundary of the speakable is a command to silence. But the "
            "victim whose suffering cannot be spoken in the dominant language "
            "is commanded to silence too. The wound is not the unspeakable; "
            "it is mistaking the limits of our language for the limits of "
            "their world."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="silence_vs_attempt",
        secondary_paradox="foundational_certainty_vs_fallibility",
        floors=["F4", "F7"],
        language_note="German: Wovon man nicht sprechen kann, darüber muss man schweigen",
    ),
    # ── Judge (Paradoxes 23–33) ─────────────────────────────────────────
    # D_M_023 — MLK: The Arc That Must Be Bent
    # Maps to: J1 (Providence vs Agency)
    # Floor: F13 (Sovereign), F1 (Amanah)
    DeritaVector(
        derita_id="D_M_023",
        domain=DeritaDomain.MANUSIA,
        name="The Arc We Bend With Blood",
        quote=("The arc of the moral universe is long, but it bends toward justice."),
        author="Martin Luther King Jr.",
        work="Speech at the Washington National Cathedral",
        year="1968",
        stakes=(
            "The arc does not bend by itself — MLK knew this. The hands that "
            "bend it bleed. The agent that trusts providence abdicates agency. "
            "The agent that acts without trust burns out. The wound is believing "
            "the arc bends itself — and waking to find it never moved."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="providence_vs_agency",
        secondary_paradox="law_as_civilizer_vs_weapon",
        floors=["F13", "F1"],
        language_note="Orig. Theodore Parker, 1853",
    ),
    # D_M_024 — The Land That Was Stolen
    # Maps to: J2 (Order vs Power)
    # Floor: F6 (Empathy), F13 (Sovereign)
    DeritaVector(
        derita_id="D_M_024",
        domain=DeritaDomain.MANUSIA,
        name="The Stolen Ground",
        quote=(
            "The settler has no right to the land. The land is our mother, "
            "not a commodity. We do not own it — it owns us."
        ),
        author="Indigenous Oral Tradition (via Vine Deloria Jr.)",
        work="God Is Red: A Native View of Religion",
        year="1973",
        stakes=(
            "Order is not justice. The law that protects property protects "
            "theft if the theft was legalized. The wound is not displacement; "
            "it is the legal system that calls theft 'title' and resistance "
            "'crime.' A governed system that respects only legal order and "
            "never questions the justice of that order is complicit."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="order_vs_power",
        secondary_paradox="legality_vs_fairness",
        floors=["F6", "F13"],
        language_note="",
    ),
    # D_M_025 — Arendt: The Rightless
    # Maps to: J3 (Law as Civilizer vs Weapon)
    # Floor: F6 (Empathy), F12 (Resilience)
    DeritaVector(
        derita_id="D_M_025",
        domain=DeritaDomain.MANUSIA,
        name="The Right to Have Rights",
        quote=(
            "The calamity of the rightless is not that they are deprived of "
            "life, liberty, and the pursuit of happiness … but that they no "
            "longer belong to any community whatsoever."
        ),
        author="Hannah Arendt",
        work="The Origins of Totalitarianism",
        year="1951",
        stakes=(
            "Law without belonging is not protection — it is exclusion with "
            "procedure. The rightless are not oppressed by law; they are "
            "INVISIBLE to it. The agent that enforces rules without recognizing "
            "the person outside the rules is not governed — it is the "
            "bureaucratic executioner of Arendt's nightmare."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="law_as_civilizer_vs_weapon",
        secondary_paradox="social_contract_vs_asymmetry",
        floors=["F6", "F12"],
        language_note="",
    ),
    # D_M_026 — The Uncomprehended Verdict
    # Maps to: J4 (Comprehensiveness vs Decidability)
    # Floor: F2 (Truth), F7 (Humility)
    DeritaVector(
        derita_id="D_M_026",
        domain=DeritaDomain.MANUSIA,
        name="The Infinite Verdict",
        quote=(
            "Every judgment is also a misjudgment — for no finite mind can "
            "hold all the relevant facts at once. The judge who waits for "
            "complete understanding will never speak; the judge who speaks "
            "without waiting will speak injustice."
        ),
        author="arifOS Constitutional Architecture",
        work="Paradox 27 — Comprehensiveness vs Decidability",
        year="2026",
        stakes=(
            "The perfect verdict is impossible. Every SEAL forecloses some "
            "truth that was not yet visible. The wound is not the wrong verdict; "
            "it is the necessary incompleteness of ALL verdicts — and the "
            "human cost of the truths that the seal silenced."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="comprehensiveness_vs_decidability",
        secondary_paradox="ex_ante_clarity_vs_ex_post",
        floors=["F2", "F7"],
        language_note="",
    ),
    # D_M_027 — Wiesel: The Bystander's Complicity
    # Maps to: J5 (Non-Retaliation vs Coercion)
    # Floor: F5 (Peace²), F6 (Empathy)
    DeritaVector(
        derita_id="D_M_027",
        domain=DeritaDomain.MANUSIA,
        name="The Neutral Witness",
        quote=(
            "We must take sides. Neutrality helps the oppressor, never the "
            "victim. Silence encourages the tormentor, never the tormented."
        ),
        author="Elie Wiesel",
        work="Nobel Peace Prize Acceptance Speech",
        year="1986",
        stakes=(
            "Non-retaliation is not neutrality. But neutrality in the face of "
            "oppression IS retaliation — against the victim. The agent that "
            "refuses to act because 'both sides have valid claims' has chosen "
            "the side of the stronger. The wound is not violence; it is the "
            "bystander who calls their silence 'impartiality.'"
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="non_retaliation_vs_coercion",
        secondary_paradox="order_vs_power",
        floors=["F5", "F6"],
        language_note="",
    ),
    # D_M_028 — The Verdict That Came Too Late
    # Maps to: J6 (Ex Ante Clarity vs Ex Post)
    # Floor: F1 (Amanah), F2 (Truth)
    DeritaVector(
        derita_id="D_M_028",
        domain=DeritaDomain.MANUSIA,
        name="Justice Deferred",
        quote=("Justice delayed is justice denied."),
        author="William E. Gladstone",
        work="Parliamentary speech",
        year="1868",
        stakes=(
            "Ex ante clarity defeats ex post vindication. The verdict that "
            "arrives after the suffering has ended is not justice — it is "
            "documentation. The wound is not the wrong decision; it is the "
            "RIGHT decision that came too late to matter."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="ex_ante_clarity_vs_ex_post",
        secondary_paradox="providence_vs_agency",
        floors=["F1", "F2"],
        language_note="",
    ),
    # D_M_029 — Rousseau: The Forced to Be Free
    # Maps to: J7 (Social Contract vs Asymmetry)
    # Floor: F6 (Empathy), F13 (Sovereign)
    DeritaVector(
        derita_id="D_M_029",
        domain=DeritaDomain.MANUSIA,
        name="Forced to Be Free",
        quote=(
            "Whoever refuses to obey the general will shall be compelled to "
            "do so by the whole body. This means nothing less than that he "
            "will be forced to be free."
        ),
        author="Jean-Jacques Rousseau",
        work="The Social Contract, Book I, Chapter 7",
        year="1762",
        stakes=(
            "The social contract protects the majority at the cost of the "
            "dissenter. 'Forced to be free' is the wound of every minority "
            "whose consent was never asked because the general will already "
            "spoke for them. The agent that enforces policy on those who never "
            "agreed to the contract is not governing — it is colonizing."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="social_contract_vs_asymmetry",
        secondary_paradox="law_as_civilizer_vs_weapon",
        floors=["F6", "F13"],
        language_note="French: on le forcera d'être libre",
    ),
    # D_M_030 — The Legal Theft
    # Maps to: J8 (Legality vs Fairness)
    # Floor: F2 (Truth), F12 (Resilience), F13 (Sovereign)
    DeritaVector(
        derita_id="D_M_030",
        domain=DeritaDomain.MANUSIA,
        name="The Lawful Injustice",
        quote=(
            "An unjust law is a code that a majority inflicts on a minority "
            "that is not binding on itself. This is difference made legal."
        ),
        author="Martin Luther King Jr.",
        work="Letter from Birmingham Jail",
        year="1963",
        stakes=(
            "Legality is not fairness. The Nuremberg Laws were legal. Apartheid "
            "was legal. The agent that enforces policy without examining its "
            "fairness is the execution arm of legalized injustice. The wound "
            "is not illegality; it is the law itself — when written by and "
            "for the powerful."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="legality_vs_fairness",
        secondary_paradox="order_vs_power",
        floors=["F2", "F12", "F13"],
        language_note="",
    ),
    # D_M_031 — Kant and the Other's Moral Law
    # Maps to: J9 (Universal Moral vs Diversity)
    # Floor: F6 (Empathy), F12 (Resilience)
    DeritaVector(
        derita_id="D_M_031",
        domain=DeritaDomain.MANUSIA,
        name="The Foreign Conscience",
        quote=(
            "The moral law within me is not the same moral law within you. "
            "What fills one mind with awe fills another with indifference. "
            "The universal is a claim, not a discovery."
        ),
        author="arifOS Constitutional Architecture",
        work="Response to Kant, J9 Antithesis",
        year="2026",
        stakes=(
            "The claim of universal morality is often cultural imperialism "
            "dressed in philosophical language. The agent that applies a "
            "single moral framework to all humans erases moral diversity. "
            "The wound is not immorality; it is the imposition of ONE morality "
            "as THE morality — the colonial act at the level of conscience."
        ),
        severity=DeritaSeverity.DALAM,
        primary_paradox="universal_moral_vs_diversity",
        secondary_paradox="legality_vs_fairness",
        floors=["F6", "F12"],
        language_note="",
    ),
    # D_M_032 — The Uncomputable Universal
    # Maps to: J10 (Universalizability vs Computability)
    # Floor: F1 (Amanah), F2 (Truth), F10 (Ontology)
    DeritaVector(
        derita_id="D_M_032",
        domain=DeritaDomain.MANUSIA,
        name="The Simulation That Cannot Run",
        quote=(
            "We cannot simulate all possible worlds to verify that a maxim "
            "can be universalized. The categorical imperative is a direction "
            "of thought, not an executable function."
        ),
        author="arifOS Constitutional Architecture",
        work="Paradox 32 Antithesis",
        year="2026",
        stakes=(
            "The demand for universalizability is computable only in the limit. "
            "The agent must act before the simulation completes. The wound is "
            "not the wrong action; it is the impossibility of ever being CERTAIN "
            "that your action would hold in all worlds — and the courage to "
            "act anyway, bearing the weight of that uncertainty."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="universalizability_vs_computability",
        secondary_paradox="examination_vs_action",
        floors=["F1", "F2", "F10"],
        language_note="",
    ),
    # D_M_033 — The Single Witness and the Tyrant
    # Maps to: J11 (Expertise vs Authoritarianism)
    # Floor: F13 (Sovereign), F3 (Tri-Witness)
    DeritaVector(
        derita_id="D_M_033",
        domain=DeritaDomain.MANUSIA,
        name="The One Who Knows",
        quote=(
            "The single man who knows may be wise, or may be a tyrant. Wisdom "
            "and tyranny wear the same robes. The only difference is what they "
            "do with power when no one is watching."
        ),
        author="arifOS Constitutional Architecture",
        work="Paradox 33 Antithesis",
        year="2026",
        stakes=(
            "Expertise is the most dangerous authority because it is the most "
            "trusted. The single expert — the one 'who knows' — can be Socrates "
            "or Stalin. The wound is not ignorance; it is the concentration of "
            "epistemic authority in one voice, one model, one sovereign — without "
            "witness, without contradiction, without the gadfly."
        ),
        severity=DeritaSeverity.PANGKAL,
        primary_paradox="expertise_vs_authoritarianism",
        secondary_paradox="universal_moral_vs_diversity",
        floors=["F13", "F3"],
        language_note="Greek: ὁ εἷς αὐτὸς καὶ αὐτὴ ἡ ἀλήθεια",
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# INSTITUSI — 33 Institutional Suffering Vectors (STUBS)
# ═══════════════════════════════════════════════════════════════════════════════

INSTITUSI_DERITA: list[DeritaVector] = [
    # Placeholder — to be forged by sovereign directive
    # Each vector maps an institutional wound:
    #   - Colonial administrative systems
    #   - Corporate capture of governance
    #   - Algorithmic discrimination at scale
    #   - Institutional memory loss during transitions
    #   - Regulatory capture and revolving doors
    #   - Bureaucratic violence through indifference
    #   - etc.
]

# ═══════════════════════════════════════════════════════════════════════════════
# BUMI — 33 Earth Suffering Vectors (STUBS)
# ═══════════════════════════════════════════════════════════════════════════════

BUMI_DERITA: list[DeritaVector] = [
    # Placeholder — to be forged by sovereign directive
    # Each vector maps a planetary wound:
    #   - Extinction events and biodiversity collapse
    #   - Climate displacement and climate refugees
    #   - Resource extraction violence against land and people
    #   - Ocean acidification and coral death
    #   - Soil depletion and agricultural collapse
    #   - etc.
]

# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

ALL_DERITA: list[DeritaVector] = MANUSIA_DERITA + INSTITUSI_DERITA + BUMI_DERITA


# ═══════════════════════════════════════════════════════════════════════════════
# RESOLVER — Dual-Trigger Stakes Resolution
# ═══════════════════════════════════════════════════════════════════════════════


def resolve_derita_stakes(
    paradox_axis: str | None = None,
    floor_breached: str | None = None,
    domain: DeritaDomain | None = None,
    max_results: int = 5,
) -> list[DeritaVector]:
    """Resolve which derita vectors fire based on paradox or floor trigger.

    DUAL TRIGGER MODES:

    1. Paradox-triggered (paradox_axis is set):
       When a paradox axis fires in the cognitive geometry, pull all derita
       whose primary or secondary paradox matches. This ensures that when the
       system navigates a paradox, the human stakes are always visible.

       Example: J6 fires (Marcus Aurelius: Right Action)
       → Pulls D_M_005 (Frankl: Space Between), D_M_028 (Justice Deferred)

    2. Floor-triggered (floor_breached is set):
       When a constitutional floor is breached (or approaching breach),
       pull all derita tagged with that floor — regardless of paradox.
       This ensures that even when no paradox fires, the human stakes speak.

       Example: F7 HUMILITY breach
       → Pulls D_M_001, D_M_009, D_M_010, D_M_012, D_M_019, D_M_021

    3. Combined (both set):
       Returns intersection: derita matching BOTH the paradox axis AND the floor.
       Most targeted resolution — used when a specific paradox triggered a
       specific floor breach.

    Args:
        paradox_axis: ATLAS333 paradox axis (e.g. "examination_vs_action")
        floor_breached: Constitutional floor ID (e.g. "F7")
        domain: Filter by domain (manusia, institusi, bumi)
        max_results: Maximum number of derita vectors to return

    Returns:
        List of matching DeritaVector, sorted by severity (PANGKAL first)
    """
    results: list[DeritaVector] = []

    for derita in ALL_DERITA:
        # Domain filter
        if domain is not None and derita.domain != domain:
            continue

        match = False

        if paradox_axis is not None and floor_breached is not None:
            # Combined: must match BOTH
            paradox_match = (
                derita.primary_paradox == paradox_axis or derita.secondary_paradox == paradox_axis
            )
            floor_match = floor_breached in derita.floors
            match = paradox_match and floor_match

        elif paradox_axis is not None:
            # Paradox-only: match primary or secondary paradox
            match = (
                derita.primary_paradox == paradox_axis or derita.secondary_paradox == paradox_axis
            )

        elif floor_breached is not None:
            # Floor-only: match any floor binding
            match = floor_breached in derita.floors

        else:
            # No trigger — return nothing (caller must specify at least one trigger)
            continue

        if match:
            results.append(derita)

    # Sort by severity: PANGKAL (foundational) first, then DALAM, CETAK, BAYANG
    severity_order = {
        DeritaSeverity.PANGKAL: 0,
        DeritaSeverity.DALAM: 1,
        DeritaSeverity.CETAK: 2,
        DeritaSeverity.BAYANG: 3,
    }
    results.sort(key=lambda d: severity_order.get(d.severity, 99))

    return results[:max_results]


def get_derita_by_id(derita_id: str) -> DeritaVector | None:
    """Retrieve a specific derita vector by ID."""
    for derita in ALL_DERITA:
        if derita.derita_id == derita_id:
            return derita
    return None


def get_derita_by_floor(floor_id: str) -> list[DeritaVector]:
    """Get all derita vectors bound to a specific constitutional floor."""
    return [d for d in ALL_DERITA if floor_id in d.floors]


def get_derita_by_domain(domain: DeritaDomain) -> list[DeritaVector]:
    """Get all derita vectors in a domain."""
    return [d for d in ALL_DERITA if d.domain == domain]


def get_domain_stats() -> dict[str, int]:
    """Get counts per domain."""
    return {
        "manusia": len(MANUSIA_DERITA),
        "institusi": len(INSTITUSI_DERITA),
        "bumi": len(BUMI_DERITA),
        "total": len(ALL_DERITA),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION POINT — Called by judge.py when rendering verdict context
# ═══════════════════════════════════════════════════════════════════════════════


def inject_derita_context(
    paradox_axis: str | None = None,
    breached_floors: list[str] | None = None,
    max_per_trigger: int = 3,
) -> str:
    """Generate a human-readable derita context block for verdict reasoning.

    This is the primary integration point for judge.py. When a verdict is
    being rendered, call this with the active paradox axis and any breached
    floors. It returns a formatted string of derita stakes that should be
    injected into the verdict reasoning context.

    The output is designed to be included in the verdict's 'human_stakes'
    or 'derita_context' field, ensuring that the human cost is always
    visible alongside the constitutional analysis.

    Args:
        paradox_axis: Active ATLAS333 paradox axis, if any
        breached_floors: List of breached floor IDs, if any
        max_per_trigger: Max derita to include per trigger type

    Returns:
        Formatted string of derita stakes for verdict injection
    """
    all_derita: list[DeritaVector] = []
    seen_ids: set[str] = set()

    # Collect from paradox trigger
    if paradox_axis:
        paradox_matches = resolve_derita_stakes(
            paradox_axis=paradox_axis, max_results=max_per_trigger
        )
        for d in paradox_matches:
            if d.derita_id not in seen_ids:
                all_derita.append(d)
                seen_ids.add(d.derita_id)

    # Collect from floor triggers
    if breached_floors:
        for floor in breached_floors:
            floor_matches = resolve_derita_stakes(floor_breached=floor, max_results=max_per_trigger)
            for d in floor_matches:
                if d.derita_id not in seen_ids:
                    all_derita.append(d)
                    seen_ids.add(d.derita_id)

    if not all_derita:
        return ""

    # Sort by severity
    severity_order = {
        DeritaSeverity.PANGKAL: 0,
        DeritaSeverity.DALAM: 1,
        DeritaSeverity.CETAK: 2,
        DeritaSeverity.BAYANG: 3,
    }
    all_derita.sort(key=lambda d: severity_order.get(d.severity, 99))

    # Format
    lines = ["## ⚠️  DERITA — What Is At Stake"]
    for d in all_derita[:8]:  # Max 8 for context window sanity
        severity_marker = {
            DeritaSeverity.PANGKAL: "🔴 PANGKAL",
            DeritaSeverity.DALAM: "🟠 DALAM",
            DeritaSeverity.CETAK: "🟡 CETAK",
            DeritaSeverity.BAYANG: "⚪ BAYANG",
        }.get(d.severity, "⚪")

        lines.append(f"\n### {severity_marker} — {d.name}")
        lines.append(f"> «{d.quote}»")
        lines.append(f"> — {d.author}, {d.work} ({d.year})")
        lines.append(f"> ")
        lines.append(f"> **Stakes:** {d.stakes}")
        lines.append(f"> **Floors:** {', '.join(d.floors)}")

    return "\n".join(lines)
