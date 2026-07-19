"""
constitution/paradox_quotes.py — The 35 Paradox Anchors
═══════════════════════════════════════════════════════════

Linguistic invariants for Memory·Mind·Judge plus active contours. The registry
contains 36 quote rows across 35 unique paradox IDs; P14 intentionally has two
quote rows. Each quote (Q) encodes one pole of a paradox. Its antithesis (Q′)
encodes the opposite pole. Together they create a tension vector that the tool
uses to calibrate its behavior.

FORMAT:
  Q  = verified quote (exact wording, author, work, date)
  Q′ = antithesis / paradox complement
  AXIS = the tension dimension
  BINDING = where the quote fires in the tool execution
  NORM = wajib/harus/sunat classification

The binding is not decorative — it fires at specific decision points in the
tool's execution. Each quote is embedded at three levels:
  Level 1 (Code):    Fires as a string constant in the tool handler
  Level 2 (Prompt):  Included in system prompt CANON block
  Level 3 (Telemetry): Logged in audit trail with tension metadata

Canonical one-sentence:
  The 35 paradox anchors do not decorate the system — they are the linguistic
  compression of the paradox geometry that Memory, Mind, Judge, and active
  contours must navigate: every retrieval is also a forgetting, every doubt is
  also a decision, every verdict is also an incomplete justice, and the tool
  that forgets this will drift from truth into the confidence of fools.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class Organ(str, Enum):
    """Target organ for quote binding."""

    MEMORY = "memory"
    MIND = "mind"
    JUDGE = "judge"
    CONTOUR = "contour"  # Active contours (34+35, 2026-07-17)


class ParadoxAxis(str, Enum):
    """The tension dimension a quote operates on."""

    # Memory axes
    RECOLLECTION_VS_DISCOVERY = "recollection_vs_discovery"
    FORGETTING_VS_REMEMBERING = "forgetting_vs_remembering"
    HORIZON_VS_BLINDNESS = "horizon_vs_blindness"
    VASTNESS_VS_OPACITY = "vastness_vs_opacity"
    EPISTEMIC_HUNGER_VS_DISCIPLINE = "epistemic_hunger_vs_discipline"
    STABILITY_VS_RIGIDITY = "stability_vs_rigidity"
    POWER_VS_RESTRAINT = "power_vs_restraint"
    TEMPORAL_DISTANCE_VS_QUALITY = "temporal_distance_vs_quality"
    KNOWLEDGE_VS_BELIEF = "knowledge_vs_belief"
    HUMILITY_VS_PARALYSIS = "humility_vs_paralysis"
    FORGETTING_AS_HEALTH_VS_DUTY = "forgetting_as_health_vs_duty"
    # Subagent / identity — added 2026-07-15 for paradox 14
    IDENTITY_VS_MULTIPLICITY = "identity_vs_multiplicity"
    # Mind axes
    CONFIDENCE_VS_COMPETENCE = "confidence_vs_competence"
    EPISTEMIC_CERTAINTY_VS_PRAGMATIC = "epistemic_certainty_vs_pragmatic"
    METHODOLOGICAL_DOUBT_VS_TRUST = "methodological_doubt_vs_trust"
    EXAMINATION_VS_ACTION = "examination_vs_action"
    EXISTENCE_VS_KNOWLEDGE = "existence_vs_knowledge"
    PROPORTIONALITY_VS_CALCULABILITY = "proportionality_vs_calculability"
    FALSE_NEGATIVE_VS_FALSE_POSITIVE = "false_negative_vs_false_positive"
    METACOGNITION_VS_METAUNCERTAINTY = "metacognition_vs_metauncertainty"
    ATARAXIA_VS_RESPONSIBILITY = "ataraxia_vs_responsibility"
    FOUNDATIONAL_CERTAINTY_VS_FALLIBILITY = "foundational_certainty_vs_fallibility"
    SILENCE_VS_ATTEMPT = "silence_vs_attempt"
    # Judge axes
    PROVIDENCE_VS_AGENCY = "providence_vs_agency"
    ORDER_VS_POWER = "order_vs_power"
    LAW_AS_CIVILIZER_VS_WEAPON = "law_as_civilizer_vs_weapon"
    COMPREHENSIVENESS_VS_DECIDABILITY = "comprehensiveness_vs_decidability"
    NON_RETALIATION_VS_COERCION = "non_retaliation_vs_coercion"
    EX_ANTE_CLARITY_VS_EX_POST = "ex_ante_clarity_vs_ex_post"
    SOCIAL_CONTRACT_VS_ASYMMETRY = "social_contract_vs_asymmetry"
    LEGALITY_VS_FAIRNESS = "legality_vs_fairness"
    UNIVERSAL_MORAL_VS_DIVERSITY = "universal_moral_vs_diversity"
    UNIVERSALIZABILITY_VS_COMPUTABILITY = "universalizability_vs_computability"
    EXPERTISE_VS_AUTHORITARIANISM = "expertise_vs_authoritarianism"
    # Active Contour axes (Paradox 34-35, 2026-07-17)
    ROOT_VS_KERNEL = "root_vs_kernel"  # P34: root filesystem access vs MCP governance
    POSITIVE_VS_CLOSED = "positive_vs_closed"  # P35: passing positive test vs defensive matrix


class Norm(str, Enum):
    """Governance norm classification."""

    WAJIB = "wajib"  # Structurally mandatory — must fire
    HARUS = "harus"  # Permitted — fires conditionally
    SUNAT = "sunat"  # Recommended — fires for audit quality


class AttributionStatus(str, Enum):
    """Verification status of quote provenance."""

    EXACT = "exact"  # Word-perfect from primary source
    TRADITIONAL = "traditional_attribution"  # Cultural convention
    PARAPHRASE = "paraphrase"  # Rephrased meaning


class EmbedLevel(str, Enum):
    """Embedding depth for the quote."""

    CODE = "code"  # String constant in tool handler
    PROMPT = "prompt"  # System prompt CANON block
    TELEMETRY = "telemetry"  # Audit trail logging


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ParadoxQuote:
    """A verified philosophical quote with full paradox tension geometry."""

    quote_id: str  # e.g. "M1", "R4", "J7", "C1"
    organ: Organ  # memory | mind | judge | contour
    index: int  # Numeric index within organ

    # The quote itself
    quote_text: str  # Exact wording
    author: str  # Full name
    work: str  # Title of work
    year: str  # Year or date range
    language_note: str  # Original language text if non-English
    attribution: AttributionStatus

    # Paradox geometry
    antithesis: str  # Q′ — what Q must be balanced against
    axis: ParadoxAxis  # The tension dimension
    axis_label: str  # Human-readable axis label: "X vs Y"

    # Constitutional binding
    norm: Norm  # wajib | harus | sunat
    trigger_condition: str  # When this quote fires
    output_field: str  # Which output field carries the quote
    floor_bindings: list[str] = field(default_factory=list)  # F1-F13 bindings

    # Embedding instructions
    embed_levels: list[EmbedLevel] = field(
        default_factory=lambda: [EmbedLevel.CODE, EmbedLevel.PROMPT, EmbedLevel.TELEMETRY]
    )
    use_modes: list[str] = field(default_factory=lambda: ["reason", "forge"])

    def to_dict(self) -> dict[str, Any]:
        """Serialize for transport/audit."""
        return {
            "quote_id": self.quote_id,
            "organ": self.organ.value,
            "author": self.author,
            "work": self.work,
            "year": self.year,
            "quote": self.quote_text,
            "antithesis": self.antithesis,
            "axis": self.axis.value,
            "axis_label": self.axis_label,
            "norm": self.norm.value,
            "trigger_condition": self.trigger_condition,
            "output_field": self.output_field,
            "floor_bindings": self.floor_bindings,
            "attribution": self.attribution.value,
        }

    def tension_vector(self) -> dict[str, str]:
        """Return the paradox tension pair."""
        return {
            "positive": self.quote_text,
            "negative": self.antithesis,
            "axis": self.axis_label,
        }

    def format_binding(self) -> str:
        """Format the quote for embedding in tool output."""
        return (
            f"[{self.quote_id}] {self.quote_text}\n"
            f"    — {self.author}, {self.work} ({self.year})\n"
            f"    ⚡ {self.axis_label}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY — 11 Quotes
# ═══════════════════════════════════════════════════════════════════════════════

MEMORY_QUOTES: list[ParadoxQuote] = [
    # M1 — Plato: Recollection as Knowledge
    ParadoxQuote(
        quote_id="M1",
        organ=Organ.MEMORY,
        index=1,
        quote_text=(
            "The soul, then, as being immortal, and having been born again many times, "
            "and having seen all things that exist, whether in this world or in the world "
            "below, has knowledge of them all… for all enquiry and all learning is but "
            "recollection."
        ),
        author="Plato",
        work="Meno 81c–d",
        year="c. 385 BCE",
        language_note="Greek: ἡ γὰρ μάθησις οὐκ ἄλλο τι ἢ ἀνάμνησις τυγχάνει οὖσα",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But if all learning is recollection, then nothing new can ever be discovered "
            "— only what was already known and forgotten."
        ),
        axis=ParadoxAxis.RECOLLECTION_VS_DISCOVERY,
        axis_label="recollection vs. discovery",
        norm=Norm.WAJIB,
        trigger_condition="Coverage report shows C_e > 0.8 — warn: completeness is not correctness",
        output_field="coverage_warning",
        floor_bindings=["F2", "F7"],
    ),
    # M2 — Borges: Forgetting as the Engine of Thought
    ParadoxQuote(
        quote_id="M2",
        organ=Organ.MEMORY,
        index=2,
        quote_text=("To think is to forget differences, to generalize, to abstract."),
        author="Jorge Luis Borges",
        work="Funes the Memorious, Ficciones",
        year="1944",
        language_note="Spanish: Pensar es olvidar diferencias, es generalizar, abstraer",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "To think is also to remember connections, to trace the specific thread "
            "that generalization would sever."
        ),
        axis=ParadoxAxis.FORGETTING_VS_REMEMBERING,
        axis_label="forgetting vs. remembering",
        norm=Norm.WAJIB,
        trigger_condition="Consolidation jobs about to summarize/compress stored facts",
        output_field="consolidation_rationale",
        floor_bindings=["F2", "F4"],
    ),
    # M3 — Nietzsche: The Horizon of Forgetting
    ParadoxQuote(
        quote_id="M3",
        organ=Organ.MEMORY,
        index=3,
        quote_text=(
            "By the word 'unhistorical' I mean the power, the art of forgetting, "
            "and of drawing a limited horizon round one's self."
        ),
        author="Friedrich Nietzsche",
        work="On the Use and Abuse of History for Life, §1",
        year="1874",
        language_note="German: das Unhistorische",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But a horizon drawn too tightly blinds — to forget too much is to be "
            "ignorant of the forces that shape the present."
        ),
        axis=ParadoxAxis.HORIZON_VS_BLINDNESS,
        axis_label="horizon vs. blindness",
        norm=Norm.HARUS,
        trigger_condition="Retrieval budget limits enforced (top-k, time-window filters)",
        output_field="budget_rationale",
        floor_bindings=["F4", "F11"],
    ),
    # M4 — Augustine: The Vastness of Memory
    ParadoxQuote(
        quote_id="M4",
        organ=Organ.MEMORY,
        index=4,
        quote_text=(
            "Great is this power of memory, exceedingly great, O my God — a vast and "
            "boundless inner chamber. Who has plumbed its depths?"
        ),
        author="Augustine of Hippo",
        work="Confessions X.8.15",
        year="c. 397–400 CE",
        language_note=(
            "Latin: Magna ista vis est memoriae, magna nimis, Deus meus, "
            "penetrale amplum et infinitum. Quis ad fundum eius pervenit?"
        ),
        attribution=AttributionStatus.EXACT,
        antithesis=("A vast chamber is also a dark one — and depth unplumbed is depth ungoverned."),
        axis=ParadoxAxis.VASTNESS_VS_OPACITY,
        axis_label="vastness vs. opacity",
        norm=Norm.SUNAT,
        trigger_condition="Memory health dashboard display — humility anchor",
        output_field="memory_health_header",
        floor_bindings=["F7"],
    ),
    # M5 — Aristotle: The Desire to Know
    ParadoxQuote(
        quote_id="M5",
        organ=Organ.MEMORY,
        index=5,
        quote_text="All men by nature desire to know.",
        author="Aristotle",
        work="Metaphysics I.1, 980a21",
        year="4th century BCE",
        language_note="Greek: Πάντες ἄνθρωποι τοῦ εἰδέναι ὀρέγονται φύσει",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But desire is not capacity, and the drive to know can outrun the ability "
            "to verify — producing conviction without warrant."
        ),
        axis=ParadoxAxis.EPISTEMIC_HUNGER_VS_DISCIPLINE,
        axis_label="epistemic hunger vs. epistemic discipline",
        norm=Norm.WAJIB,
        trigger_condition="Retrieval volume exceeds evidence quality threshold",
        output_field="volume_warning",
        floor_bindings=["F2", "F7"],
    ),
    # M6 — Plato: Knowledge Tied Down
    ParadoxQuote(
        quote_id="M6",
        organ=Organ.MEMORY,
        index=6,
        quote_text="Knowledge differs from correct opinion in being tied down.",
        author="Plato",
        work="Meno 97e–98a",
        year="c. 385 BCE",
        language_note="Greek: αἰτίας λογισμῷ",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But what is tied down cannot move — and knowledge that cannot adapt to "
            "new evidence becomes dogma."
        ),
        axis=ParadoxAxis.STABILITY_VS_RIGIDITY,
        axis_label="stability vs. rigidity",
        norm=Norm.WAJIB,
        trigger_condition="Conflict detector finds contradiction between stored and new",
        output_field="contradiction_report",
        floor_bindings=["F2", "F3"],
    ),
    # M7 — Bacon: Knowledge Is Power
    ParadoxQuote(
        quote_id="M7",
        organ=Organ.MEMORY,
        index=7,
        quote_text="Knowledge is power.",
        author="Francis Bacon",
        work="Meditationes Sacrae",
        year="1597",
        language_note="Latin: Ipsa scientia potestas est",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "Power without restraint is destruction — knowledge in the wrong hands, "
            "or knowledge ungoverned, is danger, not wisdom."
        ),
        axis=ParadoxAxis.POWER_VS_RESTRAINT,
        axis_label="power vs. restraint",
        norm=Norm.WAJIB,
        trigger_condition="Evidence served to MUTATE or SEAL class tool — provenance check",
        output_field="provenance_gate",
        floor_bindings=["F1", "F5", "F13"],
    ),
    # M8 — Aristotle: Memory and Time
    ParadoxQuote(
        quote_id="M8",
        organ=Organ.MEMORY,
        index=8,
        quote_text=(
            "Memory, then, is neither perception nor conception, but a state or "
            "affection of one of these, when time has elapsed."
        ),
        author="Aristotle",
        work="De Memoria 449b24–25",
        year="4th century BCE",
        language_note="Greek: ἔστι μὲν οὖν ἡ μνήμη οὔτε αἴσθησις οὔτε ὑπόληψις",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "If memory requires elapsed time, then the most recent evidence is not yet "
            "'memory' at all — it is still perception, with all the freshness and error "
            "of the immediate."
        ),
        axis=ParadoxAxis.TEMPORAL_DISTANCE_VS_QUALITY,
        axis_label="temporal distance vs. epistemic quality",
        norm=Norm.HARUS,
        trigger_condition="Freshness scoring — items with low temporal distance tagged PERCEPTION_GRADE",
        output_field="freshness_classification",
        floor_bindings=["F2", "F4"],
    ),
    # M9 — Plato: Knowledge vs. True Belief
    ParadoxQuote(
        quote_id="M9",
        organ=Organ.MEMORY,
        index=9,
        quote_text=(
            "If true belief and knowledge were the same thing, the best of jurymen "
            "could never have a correct belief without knowledge. It now appears that "
            "they must be two different things."
        ),
        author="Plato",
        work="Theaetetus 201c",
        year="c. 369 BCE",
        language_note="Greek: οὐκ ἄρα ταὐτόν ἐστιν ἐπιστήμη καὶ δόξα ὀρθή",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But in practice, most decisions are made on true belief, not knowledge — "
            "and a system that demands knowledge for every action will be paralyzed."
        ),
        axis=ParadoxAxis.KNOWLEDGE_VS_BELIEF,
        axis_label="knowledge vs. belief",
        norm=Norm.WAJIB,
        trigger_condition="GAP_REPORT emitted — system has belief without knowledge",
        output_field="gap_report_header",
        floor_bindings=["F2", "F4"],
    ),
    # M10 — Socrates: Knowing Your Ignorance
    ParadoxQuote(
        quote_id="M10",
        organ=Organ.MEMORY,
        index=10,
        quote_text=(
            "I am wiser than this man: for neither of us really knows anything fine "
            "and good, but he thinks he knows something when he does not, whereas I, "
            "as I do not know, do not think I know."
        ),
        author="Socrates (via Plato)",
        work="Apology 21d",
        year="c. 399 BCE",
        language_note="Greek: ἔοικα γοῦν τούτου γε σμικρῷ τινι αὐτῷ τούτῳ σοφώτερος εἶναι",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But the man who refuses to claim any knowledge is also the man who refuses "
            "to act — and inaction in the face of urgency is a decision too."
        ),
        axis=ParadoxAxis.HUMILITY_VS_PARALYSIS,
        axis_label="epistemic humility vs. decisional paralysis",
        norm=Norm.WAJIB,
        trigger_condition="COVERAGE_REPORT shows large UNKNOWN regions",
        output_field="coverage_report_footer",
        floor_bindings=["F7", "F4"],
    ),
    # M11 — Nietzsche: Happiness Through Forgetting
    ParadoxQuote(
        quote_id="M11",
        organ=Organ.MEMORY,
        index=11,
        quote_text=(
            "With the smallest and with the greatest good fortune, happiness becomes "
            "happiness in the same way: through forgetting, or, to express the matter "
            "in a more scholarly fashion, through the capacity, for as long as the "
            "happiness lasts, to sense things unhistorically."
        ),
        author="Friedrich Nietzsche",
        work="On the Use and Abuse of History for Life, §1",
        year="1874",
        language_note="German: durch das Vergessen",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But a system designed for governance cannot afford to sense things "
            "unhistorically — its duty is to remember, even when remembering is painful."
        ),
        axis=ParadoxAxis.FORGETTING_AS_HEALTH_VS_DUTY,
        axis_label="forgetting as health vs. remembering as duty",
        norm=Norm.HARUS,
        trigger_condition="Decay rules applied — critical items exempt from decay",
        output_field="decay_policy_header",
        floor_bindings=["F2", "F11"],
    ),
    # M12 — Structural: Identity vs. Multiplicity (paradox 14 anchor)
    ParadoxQuote(
        quote_id="M12",
        organ=Organ.MEMORY,
        index=12,
        quote_text=(
            "A single agent is a coherent identity. Multiple agents sharing a constitution "
            "is a federation. The identity of one is not the identity of many, and the "
            "loyalty of a subagent to its parent does not erase the subagent's own boundary."
        ),
        author="arifOS Architecture",
        work="Subagent Identity Doctrine",
        year="2026",
        language_note="",
        attribution=AttributionStatus.PARAPHRASE,
        antithesis=(
            "But every subagent carries the parent's authority, and every delegation "
            "fragments responsibility. The one who spawned is still responsible for what "
            "the many do — the parent cannot hide behind the subagent's name."
        ),
        axis=ParadoxAxis.IDENTITY_VS_MULTIPLICITY,
        axis_label="identity vs. multiplicity",
        norm=Norm.WAJIB,
        trigger_condition="Subagent spawn detected — multiple agents active in same session",
        output_field="identity_warning",
        floor_bindings=["F11", "F13"],
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# MIND — 11 Quotes
# ═══════════════════════════════════════════════════════════════════════════════

MIND_QUOTES: list[ParadoxQuote] = [
    # R1 — Bertrand Russell: The Cocksure and the Doubtful
    ParadoxQuote(
        quote_id="R1",
        organ=Organ.MIND,
        index=1,
        quote_text=(
            "The fundamental cause of the trouble is that in the modern world the "
            "stupid are cocksure while the intelligent are full of doubt."
        ),
        author="Bertrand Russell",
        work="The Triumph of Stupidity, Mortals and Others",
        year="1931–1935",
        language_note="",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "Yet endless self-doubt in the competent leaves the field entirely to "
            "the cocksure — doubt without eventual decision cedes power to those "
            "who never doubted at all."
        ),
        axis=ParadoxAxis.CONFIDENCE_VS_COMPETENCE,
        axis_label="confidence vs. competence",
        norm=Norm.WAJIB,
        trigger_condition="High confidence with weak evidence binding (C_e < 0.5, confidence > 0.7)",
        output_field="confidence_mismatch_warning",
        floor_bindings=["F7", "F2"],
    ),
    # R2 — Voltaire: The Absurdity of Certainty
    ParadoxQuote(
        quote_id="R2",
        organ=Organ.MIND,
        index=2,
        quote_text=("Doubt is not a pleasant condition, but certainty is an absurd one."),
        author="Voltaire",
        work="Letter to Frederick the Great, 28 November 1770",
        year="1770",
        language_note="French: Le doute n'est pas un état bien agréable, mais l'assurance est un état ridicule",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "And yet, every surgical incision, every bridge crossed, every airplane "
            "boarded — these are acts of practical certainty. Absurd or not, we live "
            "as if certain because the alternative is paralysis."
        ),
        axis=ParadoxAxis.EPISTEMIC_CERTAINTY_VS_PRAGMATIC,
        axis_label="epistemic certainty vs. pragmatic certainty",
        norm=Norm.WAJIB,
        trigger_condition="CLAIM tag assigned — highest epistemic confidence",
        output_field="claim_tag_annotation",
        floor_bindings=["F7"],
    ),
    # R3 — Descartes: The Deceived Senses
    ParadoxQuote(
        quote_id="R3",
        organ=Organ.MIND,
        index=3,
        quote_text=(
            "Whatever I have up till now accepted as possessed of the highest truth "
            "and certainty I have learned either from the senses or through the senses. "
            "Now these senses I have sometimes found to be deceptive; and it is only "
            "prudent never to place complete confidence in that by which we have even "
            "once been deceived."
        ),
        author="René Descartes",
        work="Meditations on First Philosophy, Meditation I",
        year="1641",
        language_note="Latin: Sed deceptus sum, inquies; at semel me fefellit",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But if we withheld confidence from everything that has deceived us once, "
            "we would trust nothing — not our senses, not our reasoning, not our memory, "
            "not our instruments."
        ),
        axis=ParadoxAxis.METHODOLOGICAL_DOUBT_VS_TRUST,
        axis_label="methodological doubt vs. operational trust",
        norm=Norm.HARUS,
        trigger_condition="Prior contradiction in evidence set — heightened scrutiny",
        output_field="scrutiny_level",
        floor_bindings=["F2", "F7"],
    ),
    # R4 — Socrates: The Unexamined Life
    ParadoxQuote(
        quote_id="R4",
        organ=Organ.MIND,
        index=4,
        quote_text="The unexamined life is not worth living.",
        author="Socrates (via Plato)",
        work="Apology 38a",
        year="c. 399 BCE",
        language_note="Greek: ὁ δὲ ἀνεξέταστος βίος οὐ βιωτὸς ἀνθρώπῳ",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But the endlessly examined life is not lived — reflection without terminus "
            "is not wisdom, it is the refusal to exist."
        ),
        axis=ParadoxAxis.EXAMINATION_VS_ACTION,
        axis_label="examination vs. action",
        norm=Norm.WAJIB,
        trigger_condition="nextThoughtNeeded: true emitted for > N consecutive steps without convergence",
        output_field="exhaustion_warning",
        floor_bindings=["F4", "F8"],
    ),
    # R5 — Descartes: The Cogito
    ParadoxQuote(
        quote_id="R5",
        organ=Organ.MIND,
        index=5,
        quote_text="I think, therefore I am.",
        author="René Descartes",
        work="Discourse on Method, Part IV",
        year="1637",
        language_note="Latin: Cogito, ergo sum / French: Je pense, donc je suis",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "I think, therefore I am — but what I am, how I think, and whether my "
            "thoughts correspond to anything beyond themselves: of these, the cogito "
            "says nothing."
        ),
        axis=ParadoxAxis.EXISTENCE_VS_KNOWLEDGE,
        axis_label="existence vs. knowledge",
        norm=Norm.WAJIB,
        trigger_condition="High R_c > 0.9 but low C_e < 0.5 — internal coherence ≠ truth",
        output_field="coherence_warning",
        floor_bindings=["F2", "F7", "F10"],
    ),
    # R6 — David Hume: Proportioning Belief to Evidence
    ParadoxQuote(
        quote_id="R6",
        organ=Organ.MIND,
        index=6,
        quote_text="A wise man, therefore, proportions his belief to the evidence.",
        author="David Hume",
        work="An Enquiry Concerning Human Understanding, Section X, Of Miracles",
        year="1748",
        language_note="",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But evidence is never complete, and the proportion that wisdom demands "
            "is unknown — we cannot calculate it exactly, only approximate it with "
            "models that are themselves uncertain."
        ),
        axis=ParadoxAxis.PROPORTIONALITY_VS_CALCULABILITY,
        axis_label="proportionality vs. calculability",
        norm=Norm.WAJIB,
        trigger_condition="Confidence estimation step — Bayesian posterior metadata",
        output_field="confidence_band_metadata",
        floor_bindings=["F2", "F7"],
    ),
    # R7 — William James: Doubt as Decision
    ParadoxQuote(
        quote_id="R7",
        organ=Organ.MIND,
        index=7,
        quote_text=(
            "Doubt itself is a decision of the widest practical reach, if only because "
            "we may miss by doubting what goods we might be gaining by espousing the "
            "winning side."
        ),
        author="William James",
        work="The Will to Believe",
        year="1897",
        language_note="",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But belief is also a decision of the widest practical reach — and the "
            "goods we gain by believing wrongly may be far worse than the goods we "
            "miss by doubting rightly."
        ),
        axis=ParadoxAxis.FALSE_NEGATIVE_VS_FALSE_POSITIVE,
        axis_label="false negative vs. false positive",
        norm=Norm.HARUS,
        trigger_condition="NEED_EVIDENCE about to be emitted — doubt has cost; assess both paths",
        output_field="doubt_proceed_threshold",
        floor_bindings=["F1", "F5"],
    ),
    # R8 — Confucius: Knowing What You Know
    ParadoxQuote(
        quote_id="R8",
        organ=Organ.MIND,
        index=8,
        quote_text=(
            "To know what you know and to know what you do not know — that is true knowledge."
        ),
        author="Confucius",
        work="Analects 2.17",
        year="c. 5th century BCE",
        language_note="Chinese: 知之為知之，不知為不知，是知也",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But the boundary between what you know and what you do not know is itself "
            "uncertain — you can be wrong about what you think you know, and wrong about "
            "what you think you don't."
        ),
        axis=ParadoxAxis.METACOGNITION_VS_METAUNCERTAINTY,
        axis_label="metacognition vs. meta-uncertainty",
        norm=Norm.WAJIB,
        trigger_condition="UNKNOWN tag assigned to a proposition",
        output_field="unknown_tag_annotation",
        floor_bindings=["F2", "F4", "F7"],
    ),
    # R9 — Sextus Empiricus: Suspension of Judgment
    ParadoxQuote(
        quote_id="R9",
        organ=Organ.MIND,
        index=9,
        quote_text=(
            "Skepticism is an ability to set out oppositions among things which appear "
            "and are thought of in any way at all, an ability by which, because of the "
            "equipollence in the opposed objects and accounts, we come first to "
            "suspension of judgment and afterwards to tranquillity."
        ),
        author="Sextus Empiricus",
        work="Outlines of Pyrrhonism I.8",
        year="c. 160–210 CE",
        language_note="Greek: ἐποχή (epochē)",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But governance is not philosophy — suspension of judgment in the face of "
            "equipollent evidence is wisdom for the individual, but for the system "
            "responsible for action, it can be abdication."
        ),
        axis=ParadoxAxis.ATARAXIA_VS_RESPONSIBILITY,
        axis_label="ataraxia vs. responsibility",
        norm=Norm.HARUS,
        trigger_condition="Equipollent evidence detected (contradictory claims of equal trust)",
        output_field="equipollence_handling",
        floor_bindings=["F1", "F3"],
    ),
    # R10 — Wittgenstein: Hinges Must Stay Put
    ParadoxQuote(
        quote_id="R10",
        organ=Organ.MIND,
        index=10,
        quote_text=(
            "The questions that we raise and our doubts depend on the fact that some "
            "propositions are exempt from doubt, are as it were like hinges on which "
            "those turn. … If I want the door to turn, the hinges must stay put."
        ),
        author="Ludwig Wittgenstein",
        work="On Certainty §§341–343",
        year="1949–1951 (published 1969)",
        language_note="German: Die Angel muß feststehen",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But which propositions are the hinges? And who decides? And what happens "
            "when a hinge that must stay put turns out to be false — when the door "
            "still turns but around a broken axis?"
        ),
        axis=ParadoxAxis.FOUNDATIONAL_CERTAINTY_VS_FALLIBILITY,
        axis_label="foundational certainty vs. foundational fallibility",
        norm=Norm.WAJIB,
        trigger_condition="Reasoning chain approaches a constitutional floor",
        output_field="floor_proximity_warning",
        floor_bindings=["F2", "F7", "F13"],
    ),
    # R11 — Wittgenstein: Whereof One Cannot Speak
    ParadoxQuote(
        quote_id="R11",
        organ=Organ.MIND,
        index=11,
        quote_text="Whereof one cannot speak, thereof one must be silent.",
        author="Ludwig Wittgenstein",
        work="Tractatus Logico-Philosophicus, Proposition 7",
        year="1922",
        language_note="German: Wovon man nicht sprechen kann, darüber muss man schweigen",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But the boundary of the speakable is not marked — we discover it only by "
            "trying to speak and failing. Silence is the destination, not the starting "
            "point."
        ),
        axis=ParadoxAxis.SILENCE_VS_ATTEMPT,
        axis_label="silence vs. attempt",
        norm=Norm.WAJIB,
        trigger_condition="ABSTAIN output emitted — must include evidence of the attempt",
        output_field="abstain_rationale",
        floor_bindings=["F4", "F7"],
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# JUDGE — 11 Quotes
# ═══════════════════════════════════════════════════════════════════════════════

JUDGE_QUOTES: list[ParadoxQuote] = [
    # J1 — Theodore Parker / MLK: The Arc of Justice
    ParadoxQuote(
        quote_id="J1",
        organ=Organ.JUDGE,
        index=1,
        quote_text=(
            "I do not pretend to understand the moral universe. The arc is a long one. "
            "My eye reaches but little ways. I cannot calculate the curve and complete "
            "the figure by the experience of sight; I can divine it by conscience. And "
            "from what I see I am sure it bends toward justice."
        ),
        author="Theodore Parker",
        work="Of Justice and the Conscience, Ten Sermons of Religion",
        year="1853",
        language_note=(
            "MLK adaptation (1968): 'The arc of the moral universe is long, "
            "but it bends toward justice.'"
        ),
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But the arc does not bend by itself — gravity is not justice, and the "
            "curve that conscience divines is shaped by human hands, not natural law. "
            "The arc bends only if we bend it."
        ),
        axis=ParadoxAxis.PROVIDENCE_VS_AGENCY,
        axis_label="providence vs. agency",
        norm=Norm.WAJIB,
        trigger_condition="SABAR verdict issued — must carry deadline",
        output_field="sabar_deadline",
        floor_bindings=["F1", "F13"],
    ),
    # J2 — Plato: Justice as One's Own Work
    ParadoxQuote(
        quote_id="J2",
        organ=Organ.JUDGE,
        index=2,
        quote_text=(
            "Justice is the having and doing of what is one's own, and the doing of "
            "one's own business."
        ),
        author="Plato",
        work="Republic 433e–434a",
        year="c. 375 BCE",
        language_note="Greek: δικαιοσύνη… τὸ τὰ αὑτοῦ πράττειν",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But who decides what is one's own? The powerful define their own business "
            "broadly and the business of others narrowly. A justice of proper spheres "
            "presupposes a just arbiter of spheres."
        ),
        axis=ParadoxAxis.ORDER_VS_POWER,
        axis_label="order vs. power",
        norm=Norm.WAJIB,
        trigger_condition="Organ boundary enforcement — no tool above its action class",
        output_field="boundary_enforcement",
        floor_bindings=["F13"],
    ),
    # J3 — Aristotle: Man Without Justice
    ParadoxQuote(
        quote_id="J3",
        organ=Organ.JUDGE,
        index=3,
        quote_text=(
            "At his best, man is the noblest of all animals; separated from law and "
            "justice he is the worst."
        ),
        author="Aristotle",
        work="Politics 1253a31–33",
        year="4th century BCE",
        language_note="Greek: χωρισθὲν δὲ νόμου καὶ δίκης χείριστον πάντων",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But law and justice are human constructs — made by the same creature they "
            "are supposed to restrain. The worst in man writes the laws too."
        ),
        axis=ParadoxAxis.LAW_AS_CIVILIZER_VS_WEAPON,
        axis_label="law as civilizer vs. law as weapon",
        norm=Norm.WAJIB,
        trigger_condition="Policy-as-code gate applied — gate must be reviewable",
        output_field="policy_engine_metadata",
        floor_bindings=["F1", "F2", "F13"],
    ),
    # J4 — Aristotle: In Justice Every Virtue
    ParadoxQuote(
        quote_id="J4",
        organ=Organ.JUDGE,
        index=4,
        quote_text="In justice is every virtue comprehended.",
        author="Aristotle",
        work="Nicomachean Ethics 1129b29–30",
        year="4th century BCE",
        language_note="Greek: ἐν δὲ δικαιοσύνῃ συλλήβδην πᾶσ᾽ ἀρετὴ ἔνι",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But if justice comprehends every virtue, then no single verdict can be "
            "just — for no single verdict can comprehend every virtue simultaneously."
        ),
        axis=ParadoxAxis.COMPREHENSIVENESS_VS_DECIDABILITY,
        axis_label="comprehensiveness vs. decidability",
        norm=Norm.WAJIB,
        trigger_condition="SEAL verdict — audit bundle annotation",
        output_field="seal_audit_bundle",
        floor_bindings=["F2", "F7"],
    ),
    # J5 — Socrates: Never Repay Injustice with Injustice
    ParadoxQuote(
        quote_id="J5",
        organ=Organ.JUDGE,
        index=5,
        quote_text=(
            "One must never repay injustice with injustice, as the many think, since "
            "one must never do injustice."
        ),
        author="Socrates (via Plato)",
        work="Crito 49b–c",
        year="c. 399 BCE",
        language_note="Greek: οὐδαμῶς δεῖ ἀδικεῖν",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But what of defensive action? To restrain an aggressor is to do something "
            "to them they did not consent to — is that injustice? If not, the principle "
            "requires a theory of justified coercion, not a simple prohibition."
        ),
        axis=ParadoxAxis.NON_RETALIATION_VS_COERCION,
        axis_label="non-retaliation vs. justified coercion",
        norm=Norm.WAJIB,
        trigger_condition="Irreversible coercive/restrictive action evaluation",
        output_field="coercion_analysis",
        floor_bindings=["F5", "F12"],
    ),
    # J6 — Marcus Aurelius: Right Action, True Speech
    ParadoxQuote(
        quote_id="J6",
        organ=Organ.JUDGE,
        index=6,
        quote_text="If it is not right, do not do it; if it is not true, do not say it.",
        author="Marcus Aurelius",
        work="Meditations",
        year="c. 170–180 CE",
        language_note="Greek: Εἰ μὴ ἔστι δίκαιον, μὴ πράξῃς· εἰ μὴ ἔστιν ἀληθές, μὴ εἴπῃς",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But rightness and truth are not always visible in the moment of decision "
            "— and sometimes, what is right can only be known after the action is taken, "
            "and what is true can only be known after the word is spoken."
        ),
        axis=ParadoxAxis.EX_ANTE_CLARITY_VS_EX_POST,
        axis_label="ex ante clarity vs. ex post knowledge",
        norm=Norm.WAJIB,
        trigger_condition="Irreversible-action gate — hard requirement",
        output_field="irreversible_gate",
        floor_bindings=["F1", "F2"],
    ),
    # J7 — Glaucon (via Plato): The Temptation of Injustice
    ParadoxQuote(
        quote_id="J7",
        organ=Organ.JUDGE,
        index=7,
        quote_text=(
            "They say that to do injustice is naturally good, to suffer injustice bad, "
            "but that the bad of suffering injustice far exceeds the good of doing it; "
            "so that when men do injustice to one another and suffer it, and taste of "
            "both, those who are unable to escape the one and choose the other determine "
            "that it is profitable to make a compact neither to do nor to suffer "
            "injustice."
        ),
        author="Glaucon (via Plato)",
        work="Republic 358e–359a",
        year="c. 375 BCE",
        language_note="Greek: contractarian theory of justice",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But the compact is fragile — those who can escape suffering injustice while "
            "still doing it will do so. Justice is a second-best for the weak, not a "
            "virtue of the strong — unless the compact is enforced by something stronger "
            "than self-interest."
        ),
        axis=ParadoxAxis.SOCIAL_CONTRACT_VS_ASYMMETRY,
        axis_label="social contract vs. power asymmetry",
        norm=Norm.WAJIB,
        trigger_condition="Power-asymmetry detection (system vs. user, institution vs. individual)",
        output_field="power_asymmetry_analysis",
        floor_bindings=["F5", "F6", "F12"],
    ),
    # J8 — Aristotle: The Lawful and the Fair
    ParadoxQuote(
        quote_id="J8",
        organ=Organ.JUDGE,
        index=8,
        quote_text="The just, then, is the lawful and the fair, the unjust the unlawful and the unfair.",
        author="Aristotle",
        work="Nicomachean Ethics 1129a34–35",
        year="4th century BCE",
        language_note="Greek: τὸ δίκαιον ἄρα τὸ νόμιμον καὶ τὸ ἴσον, τὸ δ᾽ ἄδικον τὸ παράνομον καὶ τὸ ἄνισον",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But what is lawful may be unfair, and what is fair may be unlawful. Law "
            "and fairness diverge precisely when law is most needed — and the just is "
            "what reconciles them, not what equates them."
        ),
        axis=ParadoxAxis.LEGALITY_VS_FAIRNESS,
        axis_label="legality vs. fairness",
        norm=Norm.WAJIB,
        trigger_condition="Policy-vs-fairness conflict detected — reconcile or escalate",
        output_field="policy_fairness_conflict",
        floor_bindings=["F2", "F12", "F13"],
    ),
    # J9 — Kant: The Moral Law
    ParadoxQuote(
        quote_id="J9",
        organ=Organ.JUDGE,
        index=9,
        quote_text=(
            "Two things fill the mind with ever new and increasing admiration and awe, "
            "the more often and steadily we reflect upon them: the starry heavens above "
            "me and the moral law within me."
        ),
        author="Immanuel Kant",
        work="Critique of Practical Reason, Conclusion, Ak. 5:161",
        year="1788",
        language_note="German: Der bestirnte Himmel über mir, und das moralische Gesetz in mir",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But the moral law within is not universally legible — different minds read "
            "different laws there. What fills one mind with awe fills another with "
            "indifference, and a third with revulsion. The internal law needs external "
            "verification."
        ),
        axis=ParadoxAxis.UNIVERSAL_MORAL_VS_DIVERSITY,
        axis_label="universal moral sense vs. moral diversity",
        norm=Norm.SUNAT,
        trigger_condition="FLOOR_TENSION between F12 MARUAH (dignity) and other floors",
        output_field="floor_tension_resolution",
        floor_bindings=["F12"],
    ),
    # J10 — Kant: The Categorical Imperative
    ParadoxQuote(
        quote_id="J10",
        organ=Organ.JUDGE,
        index=10,
        quote_text=(
            "Act only according to that maxim whereby you can at the same time will "
            "that it should become a universal law."
        ),
        author="Immanuel Kant",
        work="Groundwork of the Metaphysics of Morals, Ak. 4:421",
        year="1785",
        language_note="German: Handle nur nach derjenigen Maxime, durch die du zugleich wollen kannst, daß sie ein allgemeines Gesetz werde",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But universality is not computable — we cannot simulate all possible worlds "
            "to verify that a maxim can be universalized. The categorical imperative is "
            "a direction of thought, not an executable function."
        ),
        axis=ParadoxAxis.UNIVERSALIZABILITY_VS_COMPUTABILITY,
        axis_label="universalizability vs. computability",
        norm=Norm.WAJIB,
        trigger_condition="SEAL verdict for actions with systemic scope",
        output_field="universalizability_check",
        floor_bindings=["F1", "F2", "F10"],
    ),
    # J11 — Socrates (via Plato): The Single Man and the Truth
    ParadoxQuote(
        quote_id="J11",
        organ=Organ.JUDGE,
        index=11,
        quote_text=(
            "About the just and the unjust… we should consider not what the many but "
            "what the man who knows shall say to us — that single man and the truth."
        ),
        author="Socrates (via Plato)",
        work="Crito 48a5-7",
        year="c. 399 BCE",
        language_note="Greek: ἀλλὰ τί ὁ ἐπαΐων περὶ τῶν δικαίων… ὁ εἷς αὐτὸς καὶ αὐτὴ ἡ ἀλήθεια",
        attribution=AttributionStatus.EXACT,
        antithesis=(
            "But who is the man who knows? Every claimant to knowledge is also a "
            "claimant to authority — and the history of authority is the history of "
            "error dressed in confidence. The single man may be wise, or may be a "
            "tyrant. Wisdom and tyranny wear the same robes."
        ),
        axis=ParadoxAxis.EXPERTISE_VS_AUTHORITARIANISM,
        axis_label="expertise vs. authoritarianism",
        norm=Norm.WAJIB,
        trigger_condition="HUMAN_GATE / F13 SOVEREIGN escalation — verify knowledge claim",
        output_field="human_gate_resolution",
        floor_bindings=["F13"],
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVE CONTOURS — 2 Emergent Paradoxes (34-35, 2026-07-17)
# ═══════════════════════════════════════════════════════════════════════════════

ACTIVE_CONTOURS_QUOTES: list[ParadoxQuote] = [
    # C1 — P34: Root Outruns Kernel
    # On a single VPS, root filesystem access bypasses MCP governance.
    # The forge is the real sovereign, not the constitution.
    ParadoxQuote(
        quote_id="C1",
        organ=Organ.CONTOUR,
        index=1,
        quote_text="We shape our tools and thereafter our tools shape us.",
        author="John M. Culkin",
        work="A Schoolman's Guide to Marshall McLuhan",
        year="1967",
        language_note="",
        attribution=AttributionStatus.TRADITIONAL,
        antithesis=(
            "The constitution constrains every tool that the root can wield — governance "
            "must extend to the substrate."
        ),
        axis=ParadoxAxis.ROOT_VS_KERNEL,
        axis_label="root access vs. kernel governance",
        norm=Norm.WAJIB,
        trigger_condition=(
            "Action tier is 'sovereign' OR action_class is 'IRREVERSIBLE' "
            "OR GPV.rho >= 0.8"
        ),
        output_field="paradox_constraint",
        floor_bindings=["F1", "F11", "F13"],
        embed_levels=[EmbedLevel.CODE, EmbedLevel.PROMPT, EmbedLevel.TELEMETRY],
        use_modes=["judge", "forge"],
    ),
    # C2 — P35: Positive ≠ Closed
    # A passing positive test proves opening; only defensive matrix testing
    # (positive + negative) proves failing closed.
    ParadoxQuote(
        quote_id="C2",
        organ=Organ.CONTOUR,
        index=2,
        quote_text=(
            "No amount of experimentation can ever prove me right; a single experiment "
            "can prove me wrong."
        ),
        author="Albert Einstein",
        work="Letter to Max Born",
        year="1926",
        language_note="",
        attribution=AttributionStatus.TRADITIONAL,
        antithesis=(
            "A passing test is evidence of function, not proof of safety — safety requires "
            "the test that breaks."
        ),
        axis=ParadoxAxis.POSITIVE_VS_CLOSED,
        axis_label="positive test vs. defensive closure",
        norm=Norm.WAJIB,
        trigger_condition=(
            "Verdict is 'SEAL' without defensive matrix OR test_pass_count > 0 "
            "AND test_fail_count == 0"
        ),
        output_field="paradox_constraint",
        floor_bindings=["F2", "F3", "F11"],
        embed_levels=[EmbedLevel.CODE, EmbedLevel.PROMPT, EmbedLevel.TELEMETRY],
        use_modes=["judge", "forge", "verify"],
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# MASTER REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

ALL_PARADOX_QUOTES: dict[str, ParadoxQuote] = {}
for q in MEMORY_QUOTES + MIND_QUOTES + JUDGE_QUOTES + ACTIVE_CONTOURS_QUOTES:
    ALL_PARADOX_QUOTES[q.quote_id] = q


QUOTES_BY_ORGAN: dict[Organ, list[ParadoxQuote]] = {
    Organ.MEMORY: MEMORY_QUOTES,
    Organ.MIND: MIND_QUOTES,
    Organ.JUDGE: JUDGE_QUOTES,
    Organ.CONTOUR: ACTIVE_CONTOURS_QUOTES,
}


# ═══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def get_quotes_by_organ(organ: Organ | str) -> list[ParadoxQuote]:
    """Get all 11 quotes for a given organ."""
    if isinstance(organ, str):
        organ = Organ(organ)
    return QUOTES_BY_ORGAN.get(organ, [])


def get_quote_by_id(quote_id: str) -> ParadoxQuote | None:
    """Get a single quote by ID."""
    return ALL_PARADOX_QUOTES.get(quote_id.upper())


def get_quotes_by_norm(organ: Organ | str, norm: Norm | str) -> list[ParadoxQuote]:
    """Get quotes filtered by norm classification."""
    if isinstance(organ, str):
        organ = Organ(organ)
    if isinstance(norm, str):
        norm = Norm(norm)
    return [q for q in QUOTES_BY_ORGAN.get(organ, []) if q.norm == norm]


def get_wajib_quotes(organ: Organ | str) -> list[ParadoxQuote]:
    """Get all WAJIB quotes (must fire) for an organ."""
    return get_quotes_by_norm(organ, Norm.WAJIB)


def get_triggered_quotes(organ: Organ | str, context: dict[str, Any]) -> list[ParadoxQuote]:
    """Get quotes triggered by runtime conditions.

    Each quote's trigger_condition is checked against context flags.
    Returns triggered quotes sorted by norm priority (WAJIB first).
    """
    if isinstance(organ, str):
        organ = Organ(organ)

    triggered = []
    flags = context.get("flags", [])
    if not isinstance(flags, list):
        flags = []

    for q in QUOTES_BY_ORGAN.get(organ, []):
        # Simple heuristic: if any flag word appears in trigger_condition
        condition_words = set(q.trigger_condition.lower().replace(",", "").split())
        if any(w in condition_words for w in flags):
            triggered.append(q)

    # Sort: WAJIB first, then HARUS, then SUNAT
    norm_order = {Norm.WAJIB: 0, Norm.HARUS: 1, Norm.SUNAT: 2}
    triggered.sort(key=lambda q: norm_order.get(q.norm, 99))

    return triggered[:2]  # Max 2 per invocation


# ═══════════════════════════════════════════════════════════════════════════════
# GPV-AWARE TRIGGERING — ATLAS333 Bridge §4
# ═══════════════════════════════════════════════════════════════════════════════
# Maps paradox axis IDs (1-35) from atlas.py's PARADOX_GPV_MAP to quote IDs.
# This is the bridge between the 4-lane GPV router and 36 canonical quote rows.

# Paradox ID → Quote ID mapping (from ATLAS333_BRIDGE.md §2)
# Each paradox axis maps to 1-3 quotes across organs.
PARADOX_QUOTE_MAP: dict[int, list[str]] = {
    # ZONE I: TRUTH (paradoxes 1-5)
    1: ["R1", "R2"],  # Truth ↔ Comfort
    2: ["R1", "R6", "R10"],  # Certainty ↔ Humility
    3: ["R6", "J6"],  # Evidence ↔ Story
    4: ["R8"],  # Precision ↔ Clarity
    5: ["J8", "M9"],  # Facts ↔ Meaning
    # ZONE II: GOVERNANCE (paradoxes 6-10)
    6: ["J2", "J3"],  # Freedom ↔ Law
    7: ["J11"],  # Autonomy ↔ Permission
    8: ["J5", "J6"],  # Speed ↔ Safety
    9: ["M7", "J7"],  # Power ↔ Restraint
    10: ["J4", "J1"],  # Judge ↔ Actor
    # ZONE III: AGENT (paradoxes 11-15)
    11: ["M4", "R5"],  # Self ↔ System
    12: ["M1", "M3", "M8"],  # Memory ↔ Context
    13: ["M5"],  # Identity ↔ Function
    14: ["M12"],  # One ↔ Many (subagent paradox — anchored via M12)
    15: ["M11"],  # Presence ↔ Absence
    # ZONE IV: GROWTH (paradoxes 16-20)
    16: ["M2", "M11"],  # Learning ↔ Forgetting
    17: ["M6", "M10"],  # Scar ↔ Healing
    18: ["M9", "R8"],  # Knowledge ↔ Wisdom
    19: [],  # Novelty ↔ Pattern (emerges from R4)
    20: ["M10"],  # Beginner ↔ Expert
    # ZONE V: CONNECTION (paradoxes 21-25)
    21: [],  # Map ↔ Territory (meta-paradox)
    22: ["R4", "R7"],  # Path ↔ Destination
    23: ["J4"],  # Whole ↔ Part
    24: ["M4"],  # Connection ↔ Isolation
    25: ["R9", "R11"],  # Signal ↔ Noise
    # ZONE VI: SYSTEM (paradoxes 26-30)
    26: ["J2", "J3"],  # Order ↔ Chaos
    27: ["M6"],  # Robustness ↔ Adaptability
    28: ["R11"],  # Simplicity ↔ Completeness
    29: [],  # Efficiency ↔ Resilience (emerges from risk)
    30: ["J2", "J8"],  # Structure ↔ Flow
    # ZONE VII: WITNESS (paradoxes 31-35)
    31: ["J10"],  # Witness ↔ Action
    32: ["R3", "J9"],  # Internal ↔ External
    33: ["J10", "R7"],  # Proof ↔ Trust
    34: ["C1"],  # Root Access ↔ Kernel Governance
    35: ["C2"],  # Positive Test ↔ Defensive Closure
}


def get_triggered_quotes_by_gpv(
    paradox_axes: list[int],
    organ: Organ | str | None = None,
    action_class: str | None = None,
) -> list[ParadoxQuote]:
    """Get quotes triggered by GPV paradox axes (ATLAS333 Bridge §4).

    Uses the paradox_axes field from GPV (resolved by atlas.py's PARADOX_GPV_MAP)
    to find the corresponding philosophical quotes. This is the GPV-aware replacement
    for the string-matching get_triggered_quotes().

    Args:
        paradox_axes: List of paradox IDs (1-35) from GPV.paradox_axes
        organ: Optional filter by organ (memory/mind/judge/contour). None = all organs.
        action_class: Optional action class for SEAL/MUTATE gates.
            "SEAL" → adds Zone VII paradoxes (31, 32, 33)
            "MUTATE" → adds Zone VI paradoxes (26-30) if rho >= 0.2

    Returns:
        List of ParadoxQuote objects, sorted by norm priority (WAJIB first),
        deduplicated, max 5 per invocation.
    """
    quote_ids: set[str] = set()

    # Add quotes from GPV-resolved paradox axes
    for pid in paradox_axes:
        quote_ids.update(PARADOX_QUOTE_MAP.get(pid, []))

    # Action-class gates (v2 — full 7-class AAA action taxonomy)
    # Maps each action class to paradox zones that must fire at that governance level.
    # Zones defined in ATLAS333 cognitive geometry.
    _ACTION_CLASS_PARADOX_MAP: dict[str, list[int]] = {
        "OBSERVE": [1, 2, 3, 4, 5],  # Zone I: Truth Territory — epistemic foundation
        "PROPOSE": [19, 21, 22, 25],  # Zone V: Discovery Ridge — proposing new realities
        "MUTATE": [26, 27, 28, 29, 30],  # Zone VI: System — system-level change
        "DEPLOY": [
            6,
            7,
            8,
            9,
            10,  # Zone II: Risk Frontier + Zone VI: System
            26,
            27,
            28,
            29,
            30,
        ],
        "ALLOCATE": [16, 17, 18, 20, 24],  # Zone IV: Growth + Meaning — resource allocation
        "COMMUNICATE": [11, 12, 13, 15, 32],  # Zone III: Care Basin + identity/other boundary
        "SEAL": [31, 32, 33],  # Zone VII: Sovereign Apex — irreversible commitment
    }
    if action_class is not None:
        for pid in _ACTION_CLASS_PARADOX_MAP.get(action_class, []):
            quote_ids.update(PARADOX_QUOTE_MAP.get(pid, []))

    # Resolve quote IDs to ParadoxQuote objects
    resolved: list[ParadoxQuote] = []
    for qid in quote_ids:
        q = ALL_PARADOX_QUOTES.get(qid)
        if q is None:
            continue
        # Filter by organ if specified
        if organ is not None:
            target_organ = Organ(organ) if isinstance(organ, str) else organ
            if q.organ != target_organ:
                continue
        resolved.append(q)

    # Sort: WAJIB first, then HARUS, then SUNAT
    norm_order = {Norm.WAJIB: 0, Norm.HARUS: 1, Norm.SUNAT: 2}
    resolved.sort(key=lambda q: norm_order.get(q.norm, 99))

    return resolved[:5]  # Max 5 per invocation (increased from 2 for GPV-awareness)


def format_paradox_tension(quote_id: str) -> str:
    """Format a quote's paradox tension pair for display."""
    q = get_quote_by_id(quote_id)
    if not q:
        return ""
    tension = q.tension_vector()
    return (
        f"[{quote_id}] {tension['axis']}\n  Q:  {tension['positive']}\n  Q′: {tension['negative']}"
    )


def get_tension_map(organ: Organ | str) -> list[dict[str, str]]:
    """Get the complete tension map for an organ.

    Returns a list of {axis, positive_pole, negative_pole} dicts.
    """
    if isinstance(organ, str):
        organ = Organ(organ)
    return [
        {
            "quote_id": q.quote_id,
            "axis": q.axis_label,
            "positive": q.quote_text[:80] + "…" if len(q.quote_text) > 80 else q.quote_text,
            "negative": q.antithesis[:80] + "…" if len(q.antithesis) > 80 else q.antithesis,
            "norm": q.norm.value,
        }
        for q in QUOTES_BY_ORGAN.get(organ, [])
    ]


def embed_quote_in_output(
    output: dict[str, Any], quote_id: str, trigger_context: str = ""
) -> dict[str, Any]:
    """Embed a paradox quote into a tool output dict.

    Adds a 'paradox_anchor' field with the quote, antithesis, axis, and context.
    """
    q = get_quote_by_id(quote_id)
    if not q:
        return output

    output["paradox_anchor"] = {
        "quote_id": q.quote_id,
        "organ": q.organ.value,
        "quote": q.quote_text,
        "author": q.author,
        "work": q.work,
        "year": q.year,
        "antithesis": q.antithesis,
        "axis": q.axis_label,
        "norm": q.norm.value,
        "trigger_context": trigger_context,
        "floor_bindings": q.floor_bindings,
    }
    return output


def get_organ_tension_summary() -> dict[str, Any]:
    """Get a complete tension summary across all four organs.

    Returns a dict suitable for the constitutional health dashboard.
    """
    result: dict[str, Any] = {
        "total_quotes": len(ALL_PARADOX_QUOTES),
        "organs": {},
    }

    for organ in Organ:
        quotes = QUOTES_BY_ORGAN[organ]
        wajib_count = sum(1 for q in quotes if q.norm == Norm.WAJIB)
        harus_count = sum(1 for q in quotes if q.norm == Norm.HARUS)
        sunat_count = sum(1 for q in quotes if q.norm == Norm.SUNAT)

        result["organs"][organ.value] = {
            "total": len(quotes),
            "wajib": wajib_count,
            "harus": harus_count,
            "sunat": sunat_count,
            "axes": [q.axis_label for q in quotes],
            "authors": list(set(q.author for q in quotes)),
        }

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL ONE-SENTENCE
# ═══════════════════════════════════════════════════════════════════════════════

CANON = (
    "The 35 paradox anchors do not decorate the system — they are the linguistic "
    "compression of the paradox geometry that Memory, Mind, Judge, and active contours "
    "must navigate: every retrieval is also a forgetting, every doubt is also a decision, "
    "every verdict is also an incomplete justice, and the tool that forgets this will "
    "drift from truth into the confidence of fools."
)

__all__ = [
    # Enums
    "Organ",
    "ParadoxAxis",
    "Norm",
    "AttributionStatus",
    "EmbedLevel",
    # Data classes
    "ParadoxQuote",
    # Quote collections
    "MEMORY_QUOTES",
    "MIND_QUOTES",
    "JUDGE_QUOTES",
    "ACTIVE_CONTOURS_QUOTES",
    "ALL_PARADOX_QUOTES",
    "QUOTES_BY_ORGAN",
    # Functions
    "get_quotes_by_organ",
    "get_quote_by_id",
    "get_quotes_by_norm",
    "get_wajib_quotes",
    "get_triggered_quotes",
    "get_triggered_quotes_by_gpv",
    "PARADOX_QUOTE_MAP",
    "format_paradox_tension",
    "get_tension_map",
    "embed_quote_in_output",
    "get_organ_tension_summary",
    # Canon
    "CANON",
]
