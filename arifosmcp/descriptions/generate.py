"""
generate.py — MCP-SYMBOLIC-HARDEN-v1 §7 — Generate hardened tool descriptions
═══════════════════════════════════════════════════════════════════════════

Run from repo root. Output:
  /root/arifOS/arifosmcp/descriptions/<component>.md

Each description contains:
  - purpose
  - do_not_use_when (per spec §7)
  - universal pre-action block (per spec §4)

This is a one-shot generator. Additive — does not modify any existing
description files. If a tool description already exists at the canonical
location, an integrator should APPEND the do_not_use_when block.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import os

OUT_DIR = "/root/arifOS/arifosmcp/descriptions"


# (component, organ, purpose, do_not_use_when_list)
DESCRIPTIONS: list[tuple[str, str, str, list[str]]] = [
    # ─── CRITICAL ──────────────────────────────────────────────────────────
    (
        "arif_triage", "arifos",
        "Classify an inbound action into a triage lane (constitutional, domain, observational, ritual, exploratory) before any tool is called.",
        [
            "symbolic context is unclear — must HOLD until the 9-axis pre-action pass is complete",
            "user says 'seal' or 'approve' without domain qualifier",
            "authority chain (arif_judge verdict → arif_seal → arif_forge) is broken",
            "social_blast_radius implies irreversibility but symbol_owner is unknown",
        ],
    ),
    (
        "arif_think", "arifos",
        "Multi-step reasoning, planning, and reflection with explicit confidence labeling. Now requires the 6-axis symbolic_reasoning_pass for any non-trivial task.",
        [
            "task is trivial and the 6-axis pass would be theatre",
            "no symbolic_reasoning_pass was completed (degraded reasoning mode)",
            "structural reasoning is collapsing — fall back to arif_observe for grounding",
        ],
    ),
    (
        "arif_judge", "arifos",
        "Render final constitutional verdict on a proposed action. Now requires `symbol_owner` to be verified — unknown → refused.",
        [
            "symbol_owner == unknown (spec §3.E hard rule: refuse judgment)",
            "no prior arif_triage lane assignment",
            "verdict is requested but evidence_receipt.symbolic_context is incomplete",
            "the action is irreversible and authority_verified is False",
        ],
    ),
    (
        "arif_forge", "arifos",
        "Execute approved builds, deployments, or system changes only after a verified arif_judge SEAL. Now requires the `forge_precheck` gate — if symbolic authority is uncertain, FORGE must dry_run only.",
        [
            "symbolic approval is present but constitutional approval is absent",
            "user says 'seal' ambiguously (must run seal_token_guard first)",
            "authority chain is missing (no prior arif_judge verdict)",
            "action is irreversible and ack_irreversible is false",
            "false_symbol_risk=high and dry_run_only is not set",
            "forge_precheck.judge_verdict_present is false",
            "forge_precheck.symbolic_authority_verified is false",
        ],
    ),
    (
        "arif_seal", "arifos",
        "Seal a verdict or outcome to the immutable audit ledger. The input MUST carry `seal_disambiguation` distinguishing geological_seal / constitutional_SEAL / vault_seal / trap_seal_lithology.",
        [
            "input contains a bare 'seal' token without domain qualifier (Rule Zero)",
            "symbol_owner is not verified",
            "no prior arif_judge verdict exists for this outcome",
            "the outcome is reversible — seal only when irreversibility has been declared",
        ],
    ),
    (
        "well_guard_dignity", "well",
        "Detect language or behavior patterns that reduce a human to a metric, attack identity symbols, or breach sacred/grief/family charge.",
        [
            "the language is technical and carries no symbolic charge",
            "operator has not consented to dignity audit",
            "maruah_adab_risk = none and symbolic_harm_risk = low",
        ],
    ),
    (
        "well_detect_boundary", "well",
        "Classify an inbound topic by boundary type — personal / family / professional / institutional / sacred / legal / sexual / grief / national / sovereign.",
        [
            "topic is purely technical with no human dimension",
            "boundary is already classified within the active session",
            "operator has explicitly opted out of boundary detection",
        ],
    ),
    (
        "well_trace_lineage", "well",
        "Trace the symbolic status of a memory entry: observed_fact / interpretation / emotional_state / ritual_phrase / governance_receipt / revoked_or_superseded.",
        [
            "memory has not yet been written",
            "memory symbol status is already authoritative and stamped by arif_seal",
            "the lineage request is rhetorical, not investigative",
        ],
    ),

    # ─── HIGH ─────────────────────────────────────────────────────────────
    (
        "arif_init", "arifos",
        "Start or resume a governed constitutional session. Now requires `symbolic_context` (actor_identity, role_claims, cultural_frame, session_mode, symbolic_risk_profile).",
        [
            "actor identity is not verifiable",
            "session is in opt_out mode and symbolic_context cannot be collected",
            "previous session hash is broken or unrecorded",
        ],
    ),
    (
        "arif_observe", "arifos",
        "Search the web, ingest URLs, check system vitals. Now classifies source_symbol_class (legal_document, corporate_statement, ritual_text, etc.) and emits interpretation_warning.",
        [
            "source is already classified and observation is redundant",
            "interpretation_warning has not been emitted (always emit for non-trivial sources)",
            "request is performative rather than informational",
        ],
    ),
    (
        "arif_explore", "arifos",
        "Map a repository, atlas of files, or open-ended discovery. Same source_symbol_class + interpretation_warning discipline as arif_observe.",
        [
            "scope is bounded and observation (not exploration) is the correct lane",
            "exploration would violate scope constraints",
        ],
    ),
    (
        "geox_claim_create", "geox",
        "Create a new geological claim. Now requires `symbolic_consequence` (map_symbol, reserve_booking_risk, investment_signal, institutional_liability, confidence_symbol.p10_p50_p90_present).",
        [
            "reserve_booking_risk=true and confidence_symbol.p10_p50_p90_present is false",
            "institutional_liability=true and no maruah check has been performed",
            "the claim is purely speculative without L1 evidence_layer",
        ],
    ),
    (
        "geox_claim_challenge", "geox",
        "Challenge an existing claim with contradictory evidence. Now requires `challenge_symbolic_target` (dominant_story, institutional_inertia, prestige_bias, seniority_bias, map_authority_bias).",
        [
            "challenge would attack the geoscientist's maruah rather than the symbol",
            "no contradictory evidence is present",
            "claim is already SUPERSEDED in the lineage",
        ],
    ),
    (
        "geox_claim_seal", "geox",
        "Seal a geological claim with proper domain disambiguation. **MANDATORY** seal_disambiguation block — ties to Rule Zero.",
        [
            "seal_disambiguation is missing (Rule Zero violation)",
            "claim is still under challenge (cannot seal a contested claim)",
            "claim is a trap_seal_lithology but constitutional_SEAL is being requested",
        ],
    ),
    (
        "geox_prospect_evaluate", "geox",
        "Evaluate a prospect — volumetric, POS, EVOI, risk. Now requires `seal_disambiguation` and `prospect_symbolic_load` (career_signal, partner_signal, budget_lock_in_risk).",
        [
            "seal_disambiguation is missing",
            "prospect is symbolic-only (no geological substance)",
            "budget_lock_in_risk=true without partner review",
        ],
    ),
    (
        "wealth_stock_analysis", "wealth",
        "Analyze a stock. Now requires `market_symbolic_layer` (signal_type, manipulation_risk, social_proof_detected, tamak_trigger, capital_irreversibility).",
        [
            "tamak_trigger=true — escalate to wealth_governance_verdict instead",
            "social_proof_detected=true and herd_signal dominates — HOLD for review",
            "capital_irreversibility=high without wealth_survival_engine assessment",
        ],
    ),
    (
        "wealth_governance_verdict", "wealth",
        "Render a wealth-related governance verdict. Now requires explicit `symbolic_capital_assessment` (legitimacy_signal, trust_symbol, reputational_blast_radius, institutional_maruah_risk, public_private_boundary).",
        [
            "the verdict implies irreversibility without ack_irreversible",
            "tamak pressure is unrecognised",
            "maruah risk is high and verdict is irreversible",
        ],
    ),
    (
        "well_assess_livelihood", "well",
        "Assess a livelihood — income + role + maruah + social position. Now requires `role_symbolics` (title_pressure, eldest_child_burden, corporate_rank_signal, public_identity_risk, purpose_symbol_alignment).",
        [
            "the request is purely financial — wealth_survival_engine is the correct lane",
            "operator has not consented to livelihood assessment",
            "assessment would freeze identity into a profile (sovereignty violation)",
        ],
    ),
    (
        "well_assess_sovereign_entropy", "well",
        "Assess sovereign entropy — how scattered / focused the operator's identity is. Now requires `sovereignty_guard` (no_personality_capture, no_behavioral_extraction, no_identity_freezing, preserve_operator_contradiction, do_not_reduce_arif_to_profile).",
        [
            "operator has not consented",
            "assessment would collapse operator contradiction",
            "result would be used to justify identity freeze or behavioural extraction",
        ],
    ),

    # ─── MEDIUM ────────────────────────────────────────────────────────────
    (
        "wealth_survival_engine", "wealth",
        "Survival arithmetic + symbolic pressure. Now requires `symbolic_finance_pressure` (family_obligation, status_consumption, institutional_dependency, shame_risk, hidden_commitment).",
        [
            "the request is purely speculative (no real numbers)",
            "shame_risk=high and operator has not consented to assessment",
            "the assessment would become a coercion tool against the operator",
        ],
    ),
    (
        "well_assess_homeostasis", "well",
        "Assess biological and psychological homeostasis. Now emits `homeostasis_symbolic_layer` so vitality numbers don't become identity symbols.",
        [
            "telemetry is stale or degraded (status != available)",
            "vitality read would become a public identity claim without consent",
        ],
    ),
    (
        "well_validate_vitality", "well",
        "Validate a vitality signal against substrate evidence. Now emits `vitality_symbolic_load` so a single reading does not become an identity verdict.",
        [
            "the signal is identity-staking (operator = their latest reading)",
            "validation would lock identity into a number",
            "coupled_verdict is HOLD or worse",
        ],
    ),
]


def render(component: str, organ: str, purpose: str, do_not: list[str]) -> str:
    bullets = "\n".join(f"- {x}" for x in do_not)
    return f"""# {component} — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/{component}.md
# Organ: {organ}
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
{purpose}

## do_not_use_when
{bullets}

## universal_pre_action_block
Before invoking this tool, complete the 9-axis symbolic pass:
1. literal_request
2. symbolic_meaning
3. authority_implied
4. authority_verified
5. symbol_owner
6. reversibility
7. social / cultural consequence
8. correct existing tool route
9. whether HOLD is required

If any of the above cannot be completed, do **not** invoke the tool.
Apply Rule Zero: a bare `seal` token without domain qualifier triggers
seal_token_guard quarantine.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    written: list[str] = []
    for component, organ, purpose, do_not in DESCRIPTIONS:
        path = os.path.join(OUT_DIR, f"{component}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(component, organ, purpose, do_not))
        written.append(path)
    print(f"Wrote {len(written)} descriptions to {OUT_DIR}")
    for p in written:
        print(f"  - {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())