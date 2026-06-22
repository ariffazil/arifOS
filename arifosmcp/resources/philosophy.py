"""
arifos://philosophy — 33-Axis Human Intelligence Canon
══════════════════════════════════════════════════════
The 33 most intelligent quotes said by humans, structured
as 11 Dialectical Tensions for cybernetic calibration.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

PHILOSOPHY_TEXT = """\
arifOS Philosophy — 33-Axis Human Intelligence Canon

================================================================================
THE 11 DIALECTICAL TENSIONS
================================================================================

1. SELF vs. WORLD (Socrates vs. Darwin vs. Sagan)
   - Socrates: "The unexamined life is not worth living." (Self-inspection)
   - Darwin: "From so simple a beginning endless forms..." (Outward evolutionary emergence)
   - Sagan: "We are a way for the cosmos to know itself." (Reflexive cosmological unity)
   - arifOS Invariant: arif_think + L07 Humility (self) vs. arif_measure (world)

2. CERTAINTY vs. HUMILITY (Descartes vs. Socrates vs. Gödel)
   - Descartes: "I think, therefore I am." (Irreducible subjective certainty)
   - Socrates: "I know that I know nothing." (Epistemic boundaries of ignorance)
   - Gödel: "The truth is more than provability." (Systemic incompleteness limits)
   - arifOS Invariant: arif_seal (certainty) vs. L07 Humility (humility) vs. L13 Sovereign (incompleteness)

3. PERMANENCE vs. CHANGE (Parmenides vs. Heraclitus vs. Buddha)
   - Parmenides: "What is, is." (Ontological structural invariance)
   - Heraclitus: "No man ever steps in the same river twice." (Ontological constant flux)
   - Buddha: "All conditioned things are impermanent." (Release of rigid state attachment)
   - arifOS Invariant: L10 Ontology (permanence) vs. 000-999 Pipeline (change) vs. MemoryJanitor (release)

4. POWER vs. DIGNITY (Bacon vs. Kant vs. Wollstonecraft)
   - Bacon: "Knowledge is power." (Empirical capacity / capability)
   - Kant: "Treat humanity... always as an end, never merely as a means." (Ethical alignment)
   - Wollstonecraft: "I do not wish women to have power over men, but over themselves." (Self-sovereignty)
   - arifOS Invariant: arif_forge (capability) vs. L05 Peace (dignity) vs. AAA Separation (sovereignty)

5. TRUTH vs. METHOD (Einstein vs. Heisenberg vs. Bohr)
   - Einstein: "The eternal mystery of the world is its comprehensibility." (Intelligible reality)
   - Heisenberg: "What we observe is not nature itself, but nature exposed to our method." (Measurement effect)
   - Bohr: "The opposite of a profound truth may well be another profound truth." (Complementarity)
   - arifOS Invariant: arif_fetch (truth) vs. arif_measure (method) vs. AGI/ASI Handshake (complementarity)

6. THOUGHT vs. ACTION (Socrates vs. Marx vs. Confucius)
   - Socrates: "The unexamined life..." (Critical examination)
   - Marx: "The philosophers have only interpreted... the point is to change it." (Praxis / state transition)
   - Confucius: "To see what is right and not do it is want of courage." (Moral action)
   - arifOS Invariant: arif_critique (thought) vs. arif_forge (action) vs. arif_judge (verdict)

7. RULE vs. JUDGMENT (Kant vs. Aristotle vs. Arendt)
   - Kant: Categorical Imperative (Absolute universal duty / floor)
   - Aristotle: "Virtue is the mean between extremes." (Contextually calibrated mean)
   - Arendt: "Evil is done by people who never make up their minds." (Dangers of thoughtless compliance)
   - arifOS Invariant: L01-L13 Floors (rules) vs. C0-C5 Tiers (calibrated mean) vs. Organ Consensus (judgment)

8. DESIGN vs. EMERGENCE (Feynman vs. Darwin vs. Newton)
   - Feynman: "What I cannot create, I do not understand." (Generative constructivism)
   - Darwin: Natural Selection (Complexity without central design)
   - Newton: "Standing on the shoulders of giants." (Civilizational cumulative infrastructure)
   - arifOS Invariant: arif_forge (constructivism) vs. arif_gateway_connect (emergence) vs. arif_memory_recall (history)

9. LANGUAGE vs. REALITY (Wittgenstein vs. Einstein vs. Shannon)
   - Wittgenstein: "The limits of my language mean the limits of my world." (Representational bounds)
   - Einstein: Comprehensibility of reality (Real-world reference)
   - Shannon: "Information is the resolution of uncertainty." (Mathematical entropy reduction)
   - arifOS Invariant: L10 Ontology / FastMCP (language) vs. arif_fetch (reality) vs. L04 Clarity / ΔS <= 0 (information)

10. AGENCY vs. SURRENDER (Nietzsche vs. Laozi vs. Rumi)
    - Nietzsche: "He who has a why to live..." (Tragic purpose and endurance)
    - Laozi: "The soft overcomes the hard." (Indirect adaptive alignment)
    - Rumi: "Out beyond ideas of wrongdoing and rightdoing..." (Non-dual transcendent ledger)
    - arifOS Invariant: Objective tracking (agency) vs. critique deescalate (softness) vs. 999_SEAL (transcendent ledger)

11. HUMAN vs. MACHINE (Turing vs. Shannon vs. Socrates)
    - Turing: "Can machines think?" (Operational behavioral test)
    - Shannon: Mathematical information limits (Quantitative substrate)
    - Socrates: Self-examination (Reflective edge)
    - arifOS Invariant: FastMCP schemas (behavior) vs. Telemetry (substrate) vs. L09 Anti-Hantu / F9 Doctrine (non-sentient tool)

================================================================================
DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
================================================================================
"""


def register_philosophy(mcp: FastMCP) -> list[str]:
    """Register arifos://philosophy — 33-Axis Human Intelligence Canon."""
    resource = TextResource(
        uri="arifos://philosophy",
        name="33-Axis Human Intelligence Canon",
        description=(
            "The 33-axis human intelligence philosophy canon structured as 11 great tensions. "
            "Exposes Socrates, Descartes, Turing, Newton, Einstein, Darwin, Heraclitus, Parmenides, "
            "Aristotle, Kant, Machiavelli, Buddha, Laozi, Confucius, Avicenna, Bacon, Spinoza, Hume, "
            "Wollstonecraft, Marx, Nietzsche, Wittgenstein, Gödel, Shannon, Heisenberg, Bohr, Feynman, "
            "Arendt, Weil, Sagan, MLK Jr., and Rumi. "
            "Use this resource to ground systemic reasoning and calibration."
        ),
        text=PHILOSOPHY_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://philosophy"]
