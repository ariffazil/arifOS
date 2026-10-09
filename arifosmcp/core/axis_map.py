"""axis_map.py — G0 dual-axis decomposition: metabolic stage ≠ governance tier.

One number namespace was encoding two orthogonal coordinates, and the
collision had a name: "888_JUDGE". The F13 D5 ratification (2026-07-31) set
JUDGE's metabolic stage to 666; the APEX cell framing calls the judge cell
888. BOTH are true — on DIFFERENT axes:

  METABOLIC AXIS  (kernel lifecycle position — where execution is)
    000 INIT → 111 OBSERVE → 333 THINK → 444 ROUTE → 555 MEMORY
    → 666 JUDGE → 777 FORGE → 999 SEAL

  GOVERNANCE AXIS (authority tier — who governs the verb's class)
    KERNEL        — verb operates inside kernel authority bands
    EXECUTOR_777  — mutation executes under a prior 888 verdict
    APEX_888      — the APEX cell adjudicates this verb's constitutional class
    SOVEREIGN_F13 — the sovereign seals this verb's irreversible class

decompose() accepts any legacy conflated string ("888_JUDGE", "666", "888",
"JUDGE_666", "APEX_888") and returns BOTH coordinates. Legacy references
migrate mechanically through this module; new capability records carry the
two fields natively (G0.6 hash includes them — axis reassignment flips the
capability boundary, by design).
"""

from __future__ import annotations

METABOLIC_STAGES: dict[str, str] = {
    "000": "INIT",
    "111": "OBSERVE",
    "333": "THINK",
    "444": "ROUTE",
    "555": "MEMORY",
    "666": "JUDGE",
    "777": "FORGE",
    "999": "SEAL",
}

GOVERNANCE_TIERS: dict[str, str] = {
    "KERNEL": "verb operates inside kernel authority bands",
    "EXECUTOR_777": "mutation executes under a prior APEX verdict",
    "APEX_888": "the APEX cell adjudicates this verb's constitutional class",
    "SOVEREIGN_F13": "the sovereign seals this verb's irreversible class",
}

# Per-verb native coordinates. metabolic_stage = the verb's lifecycle
# position; governance_tier = the highest tier governing its class.
VERB_AXES: dict[str, dict[str, str]] = {
    "arif_init":    {"metabolic_stage": "INIT_000",   "governance_tier": "KERNEL"},
    "arif_observe": {"metabolic_stage": "OBSERVE_111","governance_tier": "KERNEL"},
    "arif_think":   {"metabolic_stage": "THINK_333",  "governance_tier": "KERNEL"},
    "arif_route":   {"metabolic_stage": "ROUTE_444",  "governance_tier": "KERNEL"},
    "arif_memory":  {"metabolic_stage": "MEMORY_555", "governance_tier": "KERNEL"},
    "arif_judge":   {"metabolic_stage": "JUDGE_666",  "governance_tier": "APEX_888"},
    "arif_forge":   {"metabolic_stage": "FORGE_777",  "governance_tier": "EXECUTOR_777"},
    "arif_seal":    {"metabolic_stage": "SEAL_999",   "governance_tier": "SOVEREIGN_F13"},
}


def decompose(token: str) -> dict[str, str]:
    """Decompose any legacy or canonical token into both axis coordinates.

    Accepts conflated strings ("888_JUDGE"), bare stage numbers ("666"),
    canonical compounds ("JUDGE_666", "APEX_888"), and verb names
    ("arif_judge"). Returns {"metabolic_stage": ..., "governance_tier": ...}
    — fields absent from the token's meaning are omitted, never guessed.
    """
    t = (token or "").strip().upper().replace("-", "_")
    out: dict[str, str] = {}

    # canonical compound forms
    for verb, axes in VERB_AXES.items():
        if t in (verb.upper(), axes["metabolic_stage"], axes["governance_tier"]):
            out.update(axes)
            return out

    # the conflated legacy string: judge meant both axes at once
    if t in ("888_JUDGE", "JUDGE_888"):
        return {"metabolic_stage": "JUDGE_666", "governance_tier": "APEX_888"}

    # bare numbers: metabolic axis only (never assume governance from a number)
    for num, name in METABOLIC_STAGES.items():
        if t == num or t == f"{name}_{num}" or t == name:
            out["metabolic_stage"] = f"{name}_{num}"
            return out

    # bare tier names: governance axis only
    for tier in GOVERNANCE_TIERS:
        if t == tier or t == f"APEX_{tier.split('_')[0]}" and tier.startswith("APEX"):
            out["governance_tier"] = tier
            return out

    return out


def axes_for_verb(verb: str) -> dict[str, str]:
    """Native dual-axis coordinates for a canonical verb (KeyError if unknown)."""
    return dict(VERB_AXES[verb])
