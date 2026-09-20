"""G-10 regression — the 888 judge must not be budgeted as a rule engine.

DEFECT (measured on the live kernel, 2026-09-21, session SEAL-11ecd272a1a44684):

    init   -> SHORT:  arif_init returned substrate DEGRADED + mutation_allowed=false
    observe-> SEAL
    judge  -> SABAR, reason "LATENCY_TIMEOUT: judge exceeded 200ms budget for
                        C2_STANDARD. Degraded to SABAR (preventive timeout —
                        deliberation did not complete)."
              meta.latency_ms = 200, within_budget = false
    judge(2)-> SAME candidate with action_tier=elevated (C3_DEEP, 1000ms):
              meta.latency_ms = 207.35, within_budget = TRUE, and the full floor
              ladder completed (L01..L10, violated_laws=[L02, L03]).

So the deliberation takes 207.35 ms and the default tier allowed 200 ms. The
timeout is PREVENTIVE (asyncio.wait_for in arif_judge), so the coroutine was
killed at the deadline and the kernel published `SABAR` — a timeout wearing a
verdict's clothes. Any caller that omitted action_tier got that false verdict,
and two prior sessions read it as a constitutional judgment.

Two independent contradictions this file pins:

  1. `arifosmcp.core.latency_budget.judge_with_budget` declares the conservative
     default explicitly:
         budget = LATENCY_BUDGETS.get(..., LATENCY_BUDGETS[DecisionClass.C3_DEEP])
                                                     # default: conservative
     `arifosmcp.tools.judge.arif_judge` contradicted it: unknown/default tier ->
     C2_STANDARD, the least conservative mapping in the table. The tool was
     strictly less conservative than the library it imports.

  2. The binding lived as an inline local dict inside a 3,949-line function, so
     it could not be imported, asserted against, or diffed. An untestable
     constant is how the default drifted below the measured floor unnoticed.

These assertions FAIL on the pre-fix source and PASS after. They import only
symbols that are expected to exist; the newly-required constants are fetched
with getattr so the pre-fix run reports a real failure instead of a collection
error (an absence must be counted, not skipped — see G-09).

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import inspect

import arifosmcp.tools.judge as judge_mod
from arifosmcp.core.latency_budget import LATENCY_BUDGETS, DecisionClass as LC

# ── Measured on the live kernel 2026-09-21 (see module docstring) ─────────────
# Provenance: arif_judge(action_tier="elevated") on session
# SEAL-11ecd272a1a44684, meta.latency_ms = 207.35, within_budget = true,
# budget_class = C3_DEEP, llm_consulted = true.
MEASURED_DELIBERATION_MS = 207.35

# Classes the judge may legitimately be budgeted as. C0/C1 are rule-engine and
# cache tiers (10ms / 50ms); C2_STANDARD carries a 200ms ceiling. The judge
# consults an LLM and walks the full floor ladder, so it belongs to none of
# them. C4_SOVEREIGN is the unbounded human loop.
RULE_ENGINE_CLASSES = (LC.C0_AUTO, LC.C1_FAST, LC.C2_STANDARD)


def _tier_map() -> dict:
    m = getattr(judge_mod, "JUDGE_TIER_TO_LATENCY_CLASS", None)
    assert m is not None, (
        "JUDGE_TIER_TO_LATENCY_CLASS is absent from arifosmcp.tools.judge — the "
        "tier->budget binding is still an inline local dict and cannot be "
        "asserted against. Re-extract it to module level (G-10)."
    )
    assert isinstance(m, dict) and m, "JUDGE_TIER_TO_LATENCY_CLASS must be a non-empty dict"
    return m


def _default_class() -> LC:
    c = getattr(judge_mod, "JUDGE_DEFAULT_LATENCY_CLASS", None)
    assert c is not None, (
        "JUDGE_DEFAULT_LATENCY_CLASS is absent from arifosmcp.tools.judge — the "
        "unknown/default tier is still hardcoded to C2_STANDARD (G-10)."
    )
    return c


def test_default_class_is_the_library_conservative_default():
    """The tool must not be less conservative than the library it imports."""
    default = _default_class()
    assert default is LC.C3_DEEP, (
        f"unknown/default action_tier resolves to {default.value}; "
        "latency_budget.judge_with_budget declares C3_DEEP the conservative "
        "default for exactly this case."
    )


def test_no_tier_is_budgeted_as_a_rule_engine():
    """No tier may resolve to a rule-engine/cache class — the judge consults an LLM."""
    for tier, cls in _tier_map().items():
        assert cls not in RULE_ENGINE_CLASSES, (
            f"tier {tier!r} -> {cls.value} ({LATENCY_BUDGETS[cls].max_latency_ms}ms). "
            "The judge path consults an LLM and evaluates L01-L10; budgeting it as "
            "a rule engine guarantees the preventive timeout fires before "
            "deliberation completes."
        )


def test_every_budget_can_contain_the_measured_deliberation():
    """Reachability: the measured deliberation must fit inside every non-sovereign budget."""
    budgets = {cls: LATENCY_BUDGETS[cls] for cls in set(_tier_map().values())}
    budgets[_default_class()] = LATENCY_BUDGETS[_default_class()]
    for cls, budget in budgets.items():
        if cls is LC.C4_SOVEREIGN:
            continue  # unbounded by design — human loop has no SLA
        assert budget.max_latency_ms > MEASURED_DELIBERATION_MS, (
            f"{cls.value} ceiling is {budget.max_latency_ms}ms but a completed "
            f"deliberation measured {MEASURED_DELIBERATION_MS}ms — this tier can "
            "only ever return a timeout."
        )


def test_tool_signature_default_resolves_to_a_reachable_budget():
    """The default an omitting caller actually gets must be able to complete."""
    sig = inspect.signature(judge_mod.arif_judge)
    declared = sig.parameters["action_tier"].default
    cls = _tier_map().get(str(declared).strip().lower(), _default_class())
    budget = LATENCY_BUDGETS[cls]
    assert budget.max_latency_ms > MEASURED_DELIBERATION_MS, (
        f"arif_judge's own default action_tier={declared!r} resolves to {cls.value} "
        f"({budget.max_latency_ms}ms) — below the measured {MEASURED_DELIBERATION_MS}ms "
        "deliberation. Every caller omitting action_tier receives a timeout "
        "published as a verdict."
    )


def test_sovereign_tier_stays_unbounded():
    """Negative control: the human loop must not have been collapsed into a SLA."""
    cls = _tier_map().get("sovereign")
    assert cls is LC.C4_SOVEREIGN, "sovereign tier must resolve to C4_SOVEREIGN"
    assert LATENCY_BUDGETS[cls].max_latency_ms == 0, (
        "C4_SOVEREIGN must stay unbounded (max_latency_ms == 0) — time is a "
        "safeguard on the human loop."
    )


def test_degradation_verdict_matches_the_default_class():
    """A reachable class degrades fail-closed, not to a proceed-ish verdict."""
    from arifosmcp.core.decision_contract import VerdictClass

    budget = LATENCY_BUDGETS[_default_class()]
    assert budget.degradation_verdict in (
        VerdictClass.HOLD.value,
        "888_HOLD",
    ), (
        f"default class {budget.decision_class.value} degrades to "
        f"{budget.degradation_verdict!r}; a judge that cannot finish must HOLD, "
        "not invite a cautious proceed."
    )
