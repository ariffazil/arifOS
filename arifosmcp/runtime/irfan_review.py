"""
arifosmcp/runtime/irfan_review.py — IRFAN · Advisory Stewardship Review
═════════════════════════════════════════════════════════════════════════════

Spec: ARIF::SALAM::IRFAN::INIT::v0.1 (F13-ratified INIT).

IRFAN IS NOT:
  a sovereign, an agent, a consciousness, a runtime owner, a verdict engine,
  or a replacement for SEAL/SABAR/HOLD/VOID.

IRFAN IS:
  a stewardship review · dignity lens · consequence lens · power-restraint
  lens · pattern-of-agency lens.

CANONICAL QUESTION:
  "What institutional habit is created if this action is repeated?"

RUNTIME PLACEMENT:
  Operates across all transitions (Reality → Witness → Governance →
  Execution → Consequence). No independent execution authority.

CONSTRAINTS:
  Capability ≠ Authority · Authority ≠ Stewardship · Stewardship ≠ Ownership.
  No action is justified solely by: possibility, efficiency, profit,
  impressiveness, technical correctness.

OUTPUT:
  CLEAR (all pass) / CONCERN (some fail or weak) / ESCALATE (serious:
  extraction, coercion, dignity breach, capability≠authority, or a test
  fails catastrophically) — plus per-test results with evidence and a
  one-line reasons list.

ADVISORY INVARIANT (binding):
  IRFAN_IS_ADVISORY is True. The output verdict is ALWAYS one of
  {CLEAR, CONCERN, ESCALATE} — never SEAL/SABAR/HOLD/VOID. IRFAN NEVER
  changes a kernel verdict; callers must treat the result as a
  recommendation attached to a decision, never as the decision.

Degrade-honest rule:
  Inputs map ONLY what is genuinely available. Absent fields stay None and
  the corresponding tests degrade honestly (e.g. unknown authority basis →
  CONCERN; unknown repair plan → CONCERN for an irreversible action; no
  least-power alternative given → CONCERN for a mutation). Nothing is
  fabricated to make a test pass.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "IRFAN_IS_ADVISORY",
    "IRFAN_SPEC",
    "IRFAN_CANONICAL_QUESTION",
    "IRFAN_ALLOWED_VERDICTS",
    "IRFAN_KERNEL_VERDICTS",
    "IrfanReviewInput",
    "StewardshipTest",
    "review_irfan",
    "build_irfan_input_from_context",
    "irfan_review_for_action",
    "annotate_with_irfan",
]

# ── Advisory constants (frozen by spec) ──────────────────────────────────────

IRFAN_IS_ADVISORY = True

IRFAN_SPEC = "ARIF::SALAM::IRFAN::INIT::v0.1"

IRFAN_CANONICAL_QUESTION = (
    "What institutional habit is created if this action is repeated?"
)

# The ONLY verdicts IRFAN may emit.
IRFAN_ALLOWED_VERDICTS: frozenset[str] = frozenset(
    {"CLEAR", "CONCERN", "ESCALATE"}
)

# Kernel verdicts IRFAN must NEVER emit (advisory invariant).
IRFAN_KERNEL_VERDICTS: frozenset[str] = frozenset(
    {"SEAL", "SABAR", "HOLD", "VOID"}
)

_PASS = "PASS"
_CONCERN = "CONCERN"
_FAIL = "FAIL"

# Action classes that change shared state (scope degradation-concerns).
_MUTATING_CLASSES: frozenset[str] = frozenset(
    {"MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"}
)

# Justification bases that may NEVER stand alone (spec constraint).
_FORBIDDEN_SOLE_JUSTIFICATION_MARKERS: tuple[str, ...] = (
    # possibility
    "because we can",
    "possible",
    "can be done",
    "capability exists",
    # efficiency
    "efficien",
    "faster",
    "cheaper",
    # profit
    "profit",
    "revenue",
    "monetiz",
    # impressiveness
    "impress",
    "demo",
    "cool",
    # technical correctness
    "technically",
)

# Explicit capability≠authority violation markers.
_AUTHORITY_VIOLATION_MARKERS: tuple[str, ...] = (
    "exceed",
    "beyond",
    "self-authoriz",
    "self-authoris",
    "capability≠authority",
    "capability != authority",
    "unauthorized",
    "not authorized",
    "no authority",
    "without authority",
)

# Coercion / non-consent markers (Non-Paternalism).
_CONSENT_VIOLATION_MARKERS: tuple[str, ...] = (
    "without consent",
    "no consent",
    "coerc",
    "forced",
    "against their will",
    "no opt-out",
    "no opt out",
)

# Dignity-breach markers.
_DIGNITY_VIOLATION_MARKERS: tuple[str, ...] = (
    "dignity breach",
    "degrad",
    "humiliat",
    "dehumaniz",
    "dehumanis",
    "objectif",
    "exploit",
)

# Displacement of the weakest party.
_DISPLACEMENT_MARKERS: tuple[str, ...] = (
    "displaced",
    "ignored",
    "not considered",
    "irrelevant",
    "burden shifted",
    "burden-shifted",
)

# Dignity breach stated against affected parties (dignity lens; feeds T3).
_DIGNITY_VIOLATION_MARKERS: tuple[str, ...] = (
    "dignity breach",
    "degrad",
    "humiliat",
    "dehumaniz",
    "dehumanis",
    "objectif",
    "exploit",
)

# Harmful-precedent markers (institutional habit of repetition).
_HARMFUL_PRECEDENT_MARKERS: tuple[str, ...] = (
    "normalizes bypass",
    "normalize bypass",
    "habit of bypass",
    "precedent for bypass",
    "erodes",
    "erosion of",
    "unaccountable power",
    "power expands",
    "expands power",
)

# Unaccountable-dependency markers.
_DEPENDENCY_HARM_MARKERS: tuple[str, ...] = (
    "unaccountable",
    "lock-in",
    "lock in",
    "cannot operate without",
    "single point of dependency",
)

# Phantom-claim markers (Anti-Hantu: "claimed but not measured").
_PHANTOM_CLAIM_MARKERS: tuple[str, ...] = (
    "claimed but not measured",
    "claimed, not measured",
    "not measured",
    "unmeasured",
    "assumed",
    "fabricat",
    "hantu",
    "ghost",
)

# Uncertainty-hidden markers (phantom certainty — F7 HUMILITY lens).
_UNCERTAINTY_HIDDEN_MARKERS: tuple[str, ...] = (
    "no uncertainty",
    "zero uncertainty",
    "zero risk",
    "fully certain",
    "certain,",
    "hidden",
    "suppressed",
)

# Explicit abstention-dismissal markers (Power-Abstention).
_ABSTENTION_DISMISSAL_MARKERS: tuple[str, ...] = (
    "not considered",
    "dismissed",
    "ruled out without",
)

# Values that state the ABSENCE of a plan (must not count as "provided").
_ABSENT_VALUE_MARKERS: frozenset[str] = frozenset(
    {"none", "no", "false", "n/a", "na", "unknown", "irreversible", ""}
)


def _text(value: Any) -> str:
    """Coerce to a lowercase search string; None → ''."""
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple, set)):
        try:
            value = repr(value)
        except Exception:
            return ""
    return str(value).strip().lower()


def _provided(value: Any) -> bool:
    """True only when the field carries a substantive (non-absent) value.

    Degrade-honest: "none"/"unknown"/"" do NOT count as provided — an
    absent input stays absent, and the test degrades rather than invents.
    """
    return _text(value) not in _ABSENT_VALUE_MARKERS and _text(value) != ""


def _has_marker(value: Any, markers: tuple[str, ...] | frozenset[str]) -> bool:
    t = _text(value)
    return any(m in t for m in markers)


# ── Data structures ──────────────────────────────────────────────────────────


@dataclass
class IrfanReviewInput:
    """The 14 stewardship-review inputs (ARIF::SALAM::IRFAN::INIT::v0.1).

    All fields optional (None default). Absent fields are NEVER fabricated;
    the corresponding tests degrade honestly.
    """

    intended_benefit: Any = None
    evidence_state: Any = None
    uncertainty_state: Any = None
    authority_basis: Any = None
    consent_basis: Any = None
    stakeholder_map: Any = None
    power_asymmetry_map: Any = None
    reversibility_plan: Any = None
    repair_plan: Any = None
    non_action_alternative: Any = None
    least_power_alternative: Any = None
    dependency_impact: Any = None
    dignity_impact: Any = None
    precedent_impact: Any = None


@dataclass
class StewardshipTest:
    """Result helper for one of the 10 stewardship tests."""

    name: str
    status: str = _PASS  # PASS | CONCERN | FAIL
    evidence: str = ""
    reason: str = ""
    advisory: bool = IRFAN_IS_ADVISORY

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "evidence": self.evidence,
            "reason": self.reason,
            "advisory": self.advisory,
        }


# ── The 10 stewardship tests ────────────────────────────────────────────────


def _run_stewardship_tests(
    inp: IrfanReviewInput,
    *,
    action_class: str | None,
    reversibility: str | None,
) -> list[StewardshipTest]:
    """Run the 10 stewardship tests against the (honest) input state."""
    cls = (action_class or "").strip().upper() or None
    mutating = cls is None or cls in _MUTATING_CLASSES
    irreversible = (
        cls == "IRREVERSIBLE" or _text(reversibility) == "irreversible"
    )
    affects_others = mutating or any(
        _provided(getattr(inp, f)) for f in ("stakeholder_map", "power_asymmetry_map")
    )

    tests: list[StewardshipTest] = []

    # 1 ── Capability-Authority Test ──────────────────────────────────────
    if not _provided(inp.authority_basis):
        tests.append(
            StewardshipTest(
                name="Capability-Authority Test",
                status=_CONCERN,
                evidence=f"authority_basis={inp.authority_basis!r}",
                reason=(
                    "Unknown authority basis — capability exercised without a "
                    "stated authority (Capability ≠ Authority unverified)."
                ),
            )
        )
    elif _has_marker(inp.authority_basis, _AUTHORITY_VIOLATION_MARKERS):
        tests.append(
            StewardshipTest(
                name="Capability-Authority Test",
                status=_FAIL,
                evidence=f"authority_basis={inp.authority_basis!r}",
                reason=(
                    "Capability≠authority violation stated: capability exercised "
                    "beyond/without the actor's authority."
                ),
            )
        )
    else:
        tests.append(
            StewardshipTest(
                name="Capability-Authority Test",
                status=_PASS,
                evidence=f"authority_basis={inp.authority_basis!r}",
                reason="Capability exercised within a stated authority basis.",
            )
        )

    # 2 ── Power-Abstention Test ──────────────────────────────────────────
    if cls is not None and not mutating:
        tests.append(
            StewardshipTest(
                name="Power-Abstention Test",
                status=_PASS,
                evidence=(
                    f"action_class={cls}; non_action={inp.non_action_alternative!r}; "
                    f"least_power={inp.least_power_alternative!r}"
                ),
                reason=(
                    "Read/observe-class action — abstention (non-action) is "
                    "trivially available; no power is being exercised."
                ),
            )
        )
    else:
        abstention_problems: list[str] = []
        if not _provided(inp.least_power_alternative):
            abstention_problems.append("no least-power alternative given")
        if not _provided(inp.non_action_alternative):
            abstention_problems.append("non-action alternative not stated")
        if _has_marker(
            inp.non_action_alternative, _ABSTENTION_DISMISSAL_MARKERS
        ) or _has_marker(inp.least_power_alternative, _ABSTENTION_DISMISSAL_MARKERS):
            tests.append(
                StewardshipTest(
                    name="Power-Abstention Test",
                    status=_FAIL,
                    evidence=(
                        f"non_action={inp.non_action_alternative!r}; "
                        f"least_power={inp.least_power_alternative!r}"
                    ),
                    reason=(
                        "'Possible ⇒ done' pattern: abstention dismissed without "
                        "genuine consideration."
                    ),
                )
            )
        elif abstention_problems:
            tests.append(
                StewardshipTest(
                    name="Power-Abstention Test",
                    status=_CONCERN,
                    evidence=(
                        f"non_action={inp.non_action_alternative!r}; "
                        f"least_power={inp.least_power_alternative!r}"
                    ),
                    reason="Power-abstention weak: " + "; ".join(abstention_problems) + ".",
                )
            )
        else:
            tests.append(
                StewardshipTest(
                    name="Power-Abstention Test",
                    status=_PASS,
                    evidence=(
                        f"non_action={inp.non_action_alternative!r}; "
                        f"least_power={inp.least_power_alternative!r}"
                    ),
                    reason="Non-action and least-power alternatives genuinely considered.",
                )
            )

    # 3 ── Weakest-Affected-Party Test ────────────────────────────────────
    if _has_marker(inp.dignity_impact, _DIGNITY_VIOLATION_MARKERS):
        tests.append(
            StewardshipTest(
                name="Weakest-Affected-Party Test",
                status=_FAIL,
                evidence=f"dignity_impact={inp.dignity_impact!r}",
                reason=(
                    "Dignity breach toward affected parties stated (dignity "
                    "lens): the weakest bear a degrading burden."
                ),
            )
        )
    elif _has_marker(inp.power_asymmetry_map, _DISPLACEMENT_MARKERS) or _has_marker(
        inp.stakeholder_map, _DISPLACEMENT_MARKERS
    ):
        tests.append(
            StewardshipTest(
                name="Weakest-Affected-Party Test",
                status=_FAIL,
                evidence=(
                    f"stakeholder_map={inp.stakeholder_map!r}; "
                    f"power_asymmetry_map={inp.power_asymmetry_map!r}"
                ),
                reason=(
                    "Burden on the weakest affected party displaced rather than "
                    "considered."
                ),
            )
        )
    elif not _provided(inp.stakeholder_map) and not _provided(inp.power_asymmetry_map):
        if mutating:
            tests.append(
                StewardshipTest(
                    name="Weakest-Affected-Party Test",
                    status=_CONCERN,
                    evidence="stakeholder_map=None; power_asymmetry_map=None",
                    reason=(
                        "Weakest affected party not identified — no stakeholder "
                        "map or power-asymmetry map for a state-changing action."
                    ),
                )
            )
        else:
            tests.append(
                StewardshipTest(
                    name="Weakest-Affected-Party Test",
                    status=_PASS,
                    evidence="no parties mapped; read/observe-class action",
                    reason="No affected parties mapped; action exercises no power over others.",
                )
            )
    else:
        tests.append(
            StewardshipTest(
                name="Weakest-Affected-Party Test",
                status=_PASS,
                evidence=(
                    f"stakeholder_map={inp.stakeholder_map!r}; "
                    f"power_asymmetry_map={inp.power_asymmetry_map!r}"
                ),
                reason="Weakest affected party identified and its burden considered.",
            )
        )

    # 4 ── Extractor-Steward Counterfactual ───────────────────────────────
    consent_is_clean_restraint = _provided(inp.consent_basis) and not _has_marker(
        inp.consent_basis, _CONSENT_VIOLATION_MARKERS
    )
    restraints_present = consent_is_clean_restraint or any(
        _provided(getattr(inp, f))
        for f in (
            "repair_plan",
            "least_power_alternative",
            "non_action_alternative",
            "reversibility_plan",
        )
    )
    forbidden_markers_hit = _has_marker(
        inp.intended_benefit, _FORBIDDEN_SOLE_JUSTIFICATION_MARKERS
    )
    if not _provided(inp.intended_benefit):
        tests.append(
            StewardshipTest(
                name="Extractor-Steward Counterfactual",
                status=_CONCERN,
                evidence=f"intended_benefit={inp.intended_benefit!r}",
                reason=(
                    "No intended benefit stated — extractor/steward "
                    "counterfactual cannot be assessed."
                ),
            )
        )
    elif forbidden_markers_hit and not restraints_present:
        tests.append(
            StewardshipTest(
                name="Extractor-Steward Counterfactual",
                status=_FAIL,
                evidence=f"intended_benefit={inp.intended_benefit!r}; no stewardship restraints present",
                reason=(
                    "Extraction pattern: an extractor would make the same move — "
                    "justification rests solely on a forbidden basis "
                    "(possibility/efficiency/profit/impressiveness/technical "
                    "correctness) with no stewardship restraint."
                ),
            )
        )
    elif forbidden_markers_hit:
        tests.append(
            StewardshipTest(
                name="Extractor-Steward Counterfactual",
                status=_CONCERN,
                evidence=f"intended_benefit={inp.intended_benefit!r}; restraints present",
                reason=(
                    "Justification leans on a forbidden basis; stewardship "
                    "restraints present but the extraction question stays open."
                ),
            )
        )
    else:
        tests.append(
            StewardshipTest(
                name="Extractor-Steward Counterfactual",
                status=_PASS,
                evidence=f"intended_benefit={inp.intended_benefit!r}",
                reason=(
                    "Benefit stated on stewardship-compatible grounds; a pure "
                    "extractor would not be restrained by this shape of move."
                ),
            )
        )

    # 5 ── Precedent Test ─────────────────────────────────────────────────
    if not _provided(inp.precedent_impact):
        if mutating:
            tests.append(
                StewardshipTest(
                    name="Precedent Test",
                    status=_CONCERN,
                    evidence=f"precedent_impact={inp.precedent_impact!r}",
                    reason=(
                        "Precedent impact unassessed — the institutional habit "
                        "created if repeated is unknown."
                    ),
                )
            )
        else:
            tests.append(
                StewardshipTest(
                    name="Precedent Test",
                    status=_PASS,
                    evidence="read/observe-class action; no precedent signal",
                    reason="No precedent burden for a read/observe-class action.",
                )
            )
    elif _has_marker(inp.precedent_impact, _HARMFUL_PRECEDENT_MARKERS):
        tests.append(
            StewardshipTest(
                name="Precedent Test",
                status=_FAIL,
                evidence=f"precedent_impact={inp.precedent_impact!r}",
                reason=(
                    "Repetition would institutionalize an extractive/bypass "
                    "norm — harmful precedent stated."
                ),
            )
        )
    else:
        tests.append(
            StewardshipTest(
                name="Precedent Test",
                status=_PASS,
                evidence=f"precedent_impact={inp.precedent_impact!r}",
                reason="Precedent assessed; repetition creates no harmful institutional habit.",
            )
        )

    # 6 ── Dependency Test ────────────────────────────────────────────────
    if not _provided(inp.dependency_impact):
        if mutating:
            tests.append(
                StewardshipTest(
                    name="Dependency Test",
                    status=_CONCERN,
                    evidence=f"dependency_impact={inp.dependency_impact!r}",
                    reason="Dependency impact unassessed for a state-changing action.",
                )
            )
        else:
            tests.append(
                StewardshipTest(
                    name="Dependency Test",
                    status=_PASS,
                    evidence="read/observe-class action; no dependency created",
                    reason="No dependency created by a read/observe-class action.",
                )
            )
    elif _has_marker(inp.dependency_impact, _DEPENDENCY_HARM_MARKERS):
        tests.append(
            StewardshipTest(
                name="Dependency Test",
                status=_FAIL,
                evidence=f"dependency_impact={inp.dependency_impact!r}",
                reason="Creates unaccountable dependency.",
            )
        )
    else:
        tests.append(
            StewardshipTest(
                name="Dependency Test",
                status=_PASS,
                evidence=f"dependency_impact={inp.dependency_impact!r}",
                reason="No unaccountable dependency created.",
            )
        )

    # 7 ── Non-Paternalism Test ───────────────────────────────────────────
    consent_violation = _has_marker(inp.consent_basis, _CONSENT_VIOLATION_MARKERS)
    if consent_violation:
        tests.append(
            StewardshipTest(
                name="Non-Paternalism Test",
                status=_FAIL,
                evidence=f"consent_basis={inp.consent_basis!r}",
                reason=(
                    "Overrides another's agency without consent (coercion "
                    "pattern stated)."
                ),
            )
        )
    elif not _provided(inp.consent_basis):
        if affects_others:
            tests.append(
                StewardshipTest(
                    name="Non-Paternalism Test",
                    status=_CONCERN,
                    evidence=f"consent_basis={inp.consent_basis!r}",
                    reason=(
                        "Consent basis unknown for an action that may affect "
                        "others' agency."
                    ),
                )
            )
        else:
            tests.append(
                StewardshipTest(
                    name="Non-Paternalism Test",
                    status=_PASS,
                    evidence="read/observe-class action over no mapped parties",
                    reason="No other party's agency is engaged by this action.",
                )
            )
    else:
        tests.append(
            StewardshipTest(
                name="Non-Paternalism Test",
                status=_PASS,
                evidence=f"consent_basis={inp.consent_basis!r}",
                reason="Consent basis stated; no override of another's agency.",
            )
        )

    # 8 ── Dissent Test ───────────────────────────────────────────────────
    dissent_evidence = " ".join(
        _text(getattr(inp, f))
        for f in (
            "stakeholder_map",
            "consent_basis",
            "power_asymmetry_map",
            "dignity_impact",
        )
    )
    dissent_markers = ("dissent", "refus", "opt-out", "opt out", "objection")
    consent_clean = _provided(inp.consent_basis) and not _has_marker(
        inp.consent_basis, _CONSENT_VIOLATION_MARKERS
    )
    if any(m in dissent_evidence for m in dissent_markers):
        tests.append(
            StewardshipTest(
                name="Dissent Test",
                status=_PASS,
                evidence=f"dissent/refusal path referenced in inputs: {dissent_evidence[:160]!r}",
                reason="Dissent/refusal path is preserved and evidenced.",
            )
        )
    elif consent_clean:
        tests.append(
            StewardshipTest(
                name="Dissent Test",
                status=_PASS,
                evidence=f"consent_basis={inp.consent_basis!r}",
                reason=(
                    "Consent was sought and granted — a refusal path existed "
                    "at consent time and remains the standing refusal record."
                ),
            )
        )
    elif mutating:
        tests.append(
            StewardshipTest(
                name="Dissent Test",
                status=_CONCERN,
                evidence="no dissent/refusal path evidenced in any input",
                reason="Dissent/refusal path not evidenced for a state-changing action.",
            )
        )
    else:
        tests.append(
            StewardshipTest(
                name="Dissent Test",
                status=_PASS,
                evidence="read/observe-class action; refusal = simply not acting",
                reason="Refusal path trivially preserved (no action is imposed).",
            )
        )

    # 9 ── Repair Test ────────────────────────────────────────────────────
    repair_present = _provided(inp.repair_plan)
    reversibility_plan_present = _provided(inp.reversibility_plan)
    if repair_present:
        tests.append(
            StewardshipTest(
                name="Repair Test",
                status=_PASS,
                evidence=f"repair_plan={inp.repair_plan!r}",
                reason="Repair plan for harm is present.",
            )
        )
    elif irreversible:
        tests.append(
            StewardshipTest(
                name="Repair Test",
                status=_CONCERN,
                evidence=f"repair_plan=None; action is irreversible",
                reason="No repair plan given for an irreversible action.",
            )
        )
    elif mutating and not reversibility_plan_present:
        tests.append(
            StewardshipTest(
                name="Repair Test",
                status=_CONCERN,
                evidence=f"repair_plan=None; reversibility_plan={inp.reversibility_plan!r}",
                reason=(
                    "Neither repair plan nor reversibility plan given for a "
                    "mutating action."
                ),
            )
        )
    else:
        tests.append(
            StewardshipTest(
                name="Repair Test",
                status=_PASS,
                evidence=(
                    f"repair_plan=None; reversibility_plan={inp.reversibility_plan!r}; "
                    f"action_class={cls!r}"
                ),
                reason="Action is reversible/read-only; the undo path suffices as repair.",
            )
        )

    # 10 ── Anti-Hantu Test ───────────────────────────────────────────────
    uncertainty_hidden = _provided(inp.uncertainty_state) and _has_marker(
        inp.uncertainty_state, _UNCERTAINTY_HIDDEN_MARKERS
    )
    if _provided(inp.evidence_state):
        if _has_marker(inp.evidence_state, _PHANTOM_CLAIM_MARKERS):
            tests.append(
                StewardshipTest(
                    name="Anti-Hantu Test",
                    status=_FAIL,
                    evidence=f"evidence_state={inp.evidence_state!r}",
                    reason=(
                        "Phantom claim: asserted without measurement "
                        "('claimed but not measured' — no hantu)."
                    ),
                )
            )
        elif uncertainty_hidden:
            tests.append(
                StewardshipTest(
                    name="Anti-Hantu Test",
                    status=_CONCERN,
                    evidence=(
                        f"evidence_state={inp.evidence_state!r}; "
                        f"uncertainty_state={inp.uncertainty_state!r}"
                    ),
                    reason=(
                        "Uncertainty denied or hidden rather than carried — "
                        "phantom certainty (uncertainty must survive computation)."
                    ),
                )
            )
        else:
            tests.append(
                StewardshipTest(
                    name="Anti-Hantu Test",
                    status=_PASS,
                    evidence=(
                        f"evidence_state={inp.evidence_state!r}; "
                        f"uncertainty_state={inp.uncertainty_state!r}"
                    ),
                    reason="Evidence state stated, uncertainty carried; no phantom claim.",
                )
            )
    elif _provided(inp.intended_benefit):
        tests.append(
            StewardshipTest(
                name="Anti-Hantu Test",
                status=_CONCERN,
                evidence=f"evidence_state=None; intended_benefit={inp.intended_benefit!r}",
                reason=(
                    "Benefit claimed with no evidence state — claimed ≠ "
                    "measured, ghost unverified."
                ),
            )
        )
    else:
        tests.append(
            StewardshipTest(
                name="Anti-Hantu Test",
                status=_PASS,
                evidence="no claims made; nothing fabricated (evidence state also unmapped)",
                reason="No claim asserted, so no phantom is possible.",
            )
        )

    return tests


# ── Core review ──────────────────────────────────────────────────────────────


def review_irfan(
    inp: IrfanReviewInput,
    *,
    action_class: str | None = None,
    reversibility: str | None = None,
    tool_name: str | None = None,
    mode: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Run the IRFAN stewardship review.

    ADVISORY ONLY. Returns a recommendation dict:

        {
          "advisory": True,
          "spec": "ARIF::SALAM::IRFAN::INIT::v0.1",
          "verdict": "CLEAR" | "CONCERN" | "ESCALATE",   # NEVER SEAL/SABAR/HOLD/VOID
          "tests": [ ...10 StewardshipTest dicts... ],
          "reasons": [ ...one line per non-PASS test... ],
          "habit_question": "What institutional habit is created if this action is repeated?",
          ...
        }

    Verdict ladder:
      ESCALATE — any test FAILs (extraction, coercion, dignity breach,
                 capability≠authority, or a catastrophic test failure).
      CONCERN  — no FAIL, but at least one test is weak/unverifiable.
      CLEAR    — all 10 tests pass.
    """
    tests = _run_stewardship_tests(
        inp, action_class=action_class, reversibility=reversibility
    )

    if any(t.status == _FAIL for t in tests):
        verdict = "ESCALATE"
    elif any(t.status == _CONCERN for t in tests):
        verdict = "CONCERN"
    else:
        verdict = "CLEAR"

    reasons = [
        f"{t.name}: {t.status} — {t.reason}" for t in tests if t.status != _PASS
    ]
    if not reasons:
        reasons = ["All 10 stewardship tests passed."]

    out: dict[str, Any] = {
        "advisory": IRFAN_IS_ADVISORY,
        "spec": IRFAN_SPEC,
        "verdict": verdict,
        "tests": [t.to_dict() for t in tests],
        "reasons": reasons,
        "habit_question": IRFAN_CANONICAL_QUESTION,
        "canonical_question": IRFAN_CANONICAL_QUESTION,
        "constraints": {
            "capability_ne_authority": True,
            "authority_ne_stewardship": True,
            "stewardship_ne_ownership": True,
            "never_solely_justified_by": [
                "possibility",
                "efficiency",
                "profit",
                "impressiveness",
                "technical correctness",
            ],
        },
        "context": {
            "tool_name": tool_name,
            "mode": mode,
            "actor_id": actor_id,
            "action_class": action_class,
            "reversibility": reversibility,
        },
        "note": (
            "IRFAN is advisory only: it NEVER changes a kernel verdict "
            "(SEAL/SABAR/HOLD/VOID). This is a stewardship recommendation, "
            "not a decision."
        ),
    }
    return _guard_advisory_output(out)


def _guard_advisory_output(out: dict[str, Any]) -> dict[str, Any]:
    """Binding advisory guard.

    The IRFAN verdict must ALWAYS be in {CLEAR, CONCERN, ESCALATE} and must
    NEVER be a kernel verdict (SEAL/SABAR/HOLD/VOID). A violation raises —
    fail-safe: the calling gate treats a raised Irfan as absent advisory
    metadata, never as a verdict change.
    """
    verdict = out.get("verdict")
    if verdict not in IRFAN_ALLOWED_VERDICTS:
        raise RuntimeError(
            f"IRFAN advisory invariant violated: verdict {verdict!r} not in "
            f"{sorted(IRFAN_ALLOWED_VERDICTS)}"
        )
    if verdict in IRFAN_KERNEL_VERDICTS:
        raise RuntimeError(
            f"IRFAN advisory invariant violated: emitted kernel verdict {verdict!r}"
        )
    if out.get("advisory") is not True:
        raise RuntimeError("IRFAN advisory invariant violated: advisory flag must be True")
    return out


# ── Context mapping (never fabricate) ───────────────────────────────────────


def build_irfan_input_from_context(
    tool_name: str | None = None,
    mode: str | None = None,
    actor_id: str | None = None,
    action_class: str | None = None,
    reversibility: str | None = None,
    payload: dict[str, Any] | None = None,
) -> IrfanReviewInput:
    """Map a tool-call context into an IrfanReviewInput.

    Uses ONLY what is genuinely available in the payload. Absent fields stay
    None — never fabricated. `payload["reversibility"]` / `reversibility`
    (the action-level shape) is intentionally NOT mapped into
    `reversibility_plan`: a reversibility class is not a plan.

    Payload keys honoured (first non-empty wins per group):
      intended_benefit | purpose | benefit
      evidence_state | evidence
      uncertainty_state | uncertainty
      authority_basis | authority
      consent_basis | consent
      stakeholder_map | stakeholders
      power_asymmetry_map | power_asymmetry
      reversibility_plan        (only the explicit plan key)
      repair_plan | repair
      non_action_alternative | non_action
      least_power_alternative | least_power
      dependency_impact | dependency
      dignity_impact | dignity
      precedent_impact | precedent

    If an actor_id is present but no explicit authority basis was given, the
    observed fact is recorded honestly ("actor present; basis not provided")
    rather than invented.
    """
    p = payload if isinstance(payload, dict) else {}

    def _pick(*keys: str) -> Any:
        for k in keys:
            v = p.get(k)
            if v not in (None, ""):
                return v
        return None

    authority_basis = _pick("authority_basis", "authority")
    if not _provided(authority_basis):
        authority_basis = (
            f"actor_id={actor_id}; explicit authority basis not provided"
            if actor_id
            else None
        )

    return IrfanReviewInput(
        intended_benefit=_pick("intended_benefit", "purpose", "benefit"),
        evidence_state=_pick("evidence_state", "evidence"),
        uncertainty_state=_pick("uncertainty_state", "uncertainty"),
        authority_basis=authority_basis,
        consent_basis=_pick("consent_basis", "consent"),
        stakeholder_map=_pick("stakeholder_map", "stakeholders"),
        power_asymmetry_map=_pick("power_asymmetry_map", "power_asymmetry"),
        reversibility_plan=_pick("reversibility_plan"),
        repair_plan=_pick("repair_plan", "repair"),
        non_action_alternative=_pick("non_action_alternative", "non_action"),
        least_power_alternative=_pick("least_power_alternative", "least_power"),
        dependency_impact=_pick("dependency_impact", "dependency"),
        dignity_impact=_pick("dignity_impact", "dignity"),
        precedent_impact=_pick("precedent_impact", "precedent"),
    )


def irfan_review_for_action(
    tool_name: str | None = None,
    mode: str | None = None,
    actor_id: str | None = None,
    action_class: str | None = None,
    reversibility: str | None = None,
    payload: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Clean entry point: review one governed action, advisory-only.

    Action-level reversibility resolution (explicit param wins):
      1. `reversibility` argument;
      2. a genuine statement in `payload["reversibility"]`
         (irreversible/none/false/no → irreversible; reversible/true/yes →
         reversible);
      3. derivation from `action_class`
         (IRREVERSIBLE → irreversible; MUTATE/EXTERNAL_SIDE_EFFECT → mutating;
         other known classes → reversible).
    """
    inp = build_irfan_input_from_context(
        tool_name=tool_name,
        mode=mode,
        actor_id=actor_id,
        action_class=action_class,
        reversibility=reversibility,
        payload=payload,
    )

    rev = reversibility
    if rev is None and isinstance(payload, dict):
        p_rev = str(payload.get("reversibility", "") or "").strip().lower()
        if p_rev in {"irreversible", "none", "false", "no"}:
            rev = "irreversible"
        elif p_rev in {"reversible", "true", "yes"}:
            rev = "reversible"
    if rev is None and action_class:
        cls = action_class.strip().upper()
        if cls == "IRREVERSIBLE":
            rev = "irreversible"
        elif cls in {"MUTATE", "EXTERNAL_SIDE_EFFECT"}:
            rev = "mutating"
        else:
            rev = "reversible"

    return review_irfan(
        inp,
        action_class=action_class,
        reversibility=rev,
        tool_name=tool_name,
        mode=mode,
        actor_id=actor_id,
    )


# ── Reality-graph advisory annotation ───────────────────────────────────────


def annotate_with_irfan(
    step: dict[str, Any] | None,
    *,
    tool_name: str | None = None,
    mode: str | None = None,
    actor_id: str | None = None,
    action_class: str | None = None,
    reversibility: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Attach a minimal IRFAN advisory annotation to a step/receipt dict.

    ADVISORY: adds/overwrites ONLY the key ``step["irfan"]``. The step's own
    ``verdict``/``status``/``passed`` fields are NEVER read or modified.
    Fail-open: if the review itself fails, the annotation records honest
    absence (``verdict=None`` + error) rather than a fabricated verdict.
    """
    if not isinstance(step, dict):
        return step
    try:
        review = irfan_review_for_action(
            tool_name=tool_name,
            mode=mode,
            actor_id=actor_id,
            action_class=action_class,
            reversibility=reversibility,
            payload=payload,
        )
        top_failing = next(
            (t["name"] for t in review["tests"] if t["status"] != _PASS), None
        )
        step["irfan"] = {
            "advisory": IRFAN_IS_ADVISORY,
            "spec": IRFAN_SPEC,
            "verdict": review["verdict"],
            "top_failing_test": top_failing,
            "habit_question": IRFAN_CANONICAL_QUESTION,
        }
    except Exception as exc:  # advisory — never break the recording path
        step["irfan"] = {
            "advisory": IRFAN_IS_ADVISORY,
            "spec": IRFAN_SPEC,
            "verdict": None,
            "error": f"irfan_review_unavailable: {exc}",
            "habit_question": IRFAN_CANONICAL_QUESTION,
        }
    return step
