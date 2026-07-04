"""
generate.py — MCP-SYMBOLIC-HARDEN-v1 §3 — Generate 17 component schemas
════════════════════════════════════════════════════════════════════════

Run from repo root. Output:
  /root/arifOS/arifosmcp/schemas/symbolic/<component>.schema.json

This is a one-shot generator. It writes ADDITIVE schemas — no existing
schema file is modified. Each output references the shared symbolic_assessment
schema via $ref.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import os
from typing import Any

OUT_DIR = "/root/arifOS/arifosmcp/schemas/symbolic"
SYMBOLIC_ASSESSMENT_REF = "symbolic_assessment.schema.json"


def _shared_block(component: str, organ: str) -> dict[str, Any]:
    """Common fields appended to every component schema (output side)."""
    return {
        "$ref": f"../{SYMBOLIC_ASSESSMENT_REF}",
        "description": (
            f"MCP-SYMBOLIC-HARDEN-v1 §8 — Every {component} output should carry "
            f"this symbolic_assessment block so callers can distinguish literal "
            f"from symbolic, identify authority, and preserve reversibility. "
            f"See /root/arifOS/forge_work/MCP-SYMBOLIC-HARDEN-v1.md §8."
        ),
    }


def _make_schema(
    component: str,
    organ: str,
    harden_block: dict[str, Any],
    harden_required: list[str] | None = None,
    note: str = "",
) -> dict[str, Any]:
    """Build a JSON-schema dict for one component."""
    required = ["component", "organ"]
    if harden_required:
        required.extend(harden_required)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://arifosmcp.local/schemas/symbolic/{component}.schema.json",
        "title": f"{component} (symbolic hardening)",
        "description": (
            f"MCP-SYMBOLIC-HARDEN-v1 §3 — additive symbolic hardening for `{component}`. "
            f"This schema is APPENDED to the existing {organ} schema for `{component}` "
            f"and does not rewrite any pre-existing field. "
            f"Spec: /root/arifOS/forge_work/MCP-SYMBOLIC-HARDEN-v1.md §3."
            + (f" Note: {note}" if note else "")
        ),
        "type": "object",
        "required": required,
        "properties": {
            "component": {"const": component},
            "organ": {"const": organ},
            **harden_block,
            "symbolic_assessment": _shared_block(component, organ),
        },
        "additionalProperties": True,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 17 components — additive harden blocks
# ═══════════════════════════════════════════════════════════════════════════════


COMPONENTS: list[tuple[str, str, dict[str, Any], list[str] | None, str]] = [
    # ─── CRITICAL ──────────────────────────────────────────────────────────
    (
        "arif_triage", "arifos",
        {
            "symbolic_triage": {
                "type": "object",
                "description": "§3.B — Classify action before lane.",
                "properties": {
                    "action_symbol": {
                        "type": "string",
                        "enum": ["draft", "send", "seal", "judge", "delete", "publish", "approve", "advise"],
                    },
                    "authority_type": {
                        "type": "string",
                        "enum": ["none", "personal", "institutional", "financial", "legal", "sovereign", "sacred"],
                    },
                    "symbolic_harm_risk": {"type": "string", "enum": ["low", "medium", "high"]},
                    "ambiguity": {"type": "string", "enum": ["monosemic", "polysemic"]},
                    "cultural_sensitivity": {
                        "type": "string",
                        "enum": ["none", "maruah", "adab", "grief", "family", "nation", "religion", "institutional_rank"],
                    },
                },
            }
        },
        ["symbolic_triage"],
        "Best place for symbolic intelligence injection. Must classify *before* lane routing.",
    ),
    (
        "arif_think", "arifos",
        {
            "symbolic_reasoning_pass": {
                "type": "object",
                "description": "§3.D — Mandatory 6-axis symbolic_reasoning_pass for every non-trivial task.",
                "properties": {
                    "literal_meaning": {"type": "string"},
                    "social_meaning": {"type": "string"},
                    "authority_implication": {"type": "string"},
                    "emotional_charge": {"type": "string"},
                    "institutional_consequence": {"type": "string"},
                    "protocol_translation": {"type": "string"},
                    "uncertainty": {"type": "string"},
                },
            }
        },
        ["symbolic_reasoning_pass"],
        "Mandatory for non-trivial tasks. arif_think cannot be trusted without this pass.",
    ),
    (
        "arif_judge", "arifos",
        {
            "evidence_receipt": {
                "type": "object",
                "description": "§3.E — Hardening block on evidence input.",
                "properties": {
                    "symbolic_context": {
                        "type": "object",
                        "properties": {
                            "symbol_invoked": {
                                "type": "string",
                                "enum": ["SEAL", "HOLD", "VOID", "approve", "publish", "delete", "send"],
                            },
                            "symbol_owner": {
                                "type": "string",
                                "enum": ["Arif", "arifOS", "VAULT999", "institution", "unknown"],
                            },
                            "authority_verified": {"type": "boolean"},
                            "performative_effect": {"type": "boolean"},
                            "irreversible_social_effect": {"type": "boolean"},
                        },
                    },
                },
            }
        },
        ["evidence_receipt"],
        "Hard rule: No judgment if symbol_owner == unknown.",
    ),
    (
        "arif_forge", "arifos",
        {
            "forge_precheck": {
                "type": "object",
                "description": "§3.F — Required pre-mutation gate (full schema in forge_precheck.schema.json).",
                "properties": {
                    "judge_verdict_present": {"type": "boolean"},
                    "symbolic_authority_verified": {"type": "boolean"},
                    "irreversible_effect_declared": {"type": "boolean"},
                    "social_blast_radius": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["private", "team", "public", "institutional", "legal", "financial"],
                        },
                    },
                    "false_symbol_risk": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            }
        },
        ["forge_precheck"],
        "Hard rule: If symbolic authority uncertain, FORGE must dry_run only.",
    ),
    (
        "arif_seal", "arifos",
        {
            "seal_disambiguation": {
                "type": "object",
                "description": "§3.I — ties to Rule Zero. Even though arif_seal is the constitutional SEAL tool, the input it receives must disambiguate which kind of seal is being asked for.",
                "properties": {
                    "geological_seal": {"type": "boolean"},
                    "constitutional_SEAL": {"type": "boolean"},
                    "vault_seal": {"type": "boolean"},
                    "trap_seal_lithology": {"type": "boolean"},
                },
            }
        },
        ["seal_disambiguation"],
        "arif_seal MUST verify domain even when the tool itself is constitutional — protects against cross-surface contamination.",
    ),
    (
        "well_guard_dignity", "well",
        {
            "dignity_symbol_check": {
                "type": "object",
                "description": "§3.M — Natural home of social-symbology intelligence.",
                "properties": {
                    "reduction_to_metric": {"type": "boolean"},
                    "identity_symbol_violation": {"type": "boolean"},
                    "grief_or_family_charge": {"type": "boolean"},
                    "sacred_or_taboo_domain": {"type": "boolean"},
                    "coercive_symbol_detected": {"type": "boolean"},
                },
            }
        },
        ["dignity_symbol_check"],
        "Calling someone 'irrational' may be technically descriptive but symbolically humiliating — WELL must catch it.",
    ),
    (
        "well_detect_boundary", "well",
        {
            "boundary_type": {
                "type": "array",
                "description": "§3.N — Symbolic boundary type. Same sentence safe in one boundary, harmful in another.",
                "items": {
                    "type": "string",
                    "enum": [
                        "personal", "family", "professional", "institutional",
                        "sacred", "legal", "sexual", "grief", "national", "sovereign",
                    ],
                },
            }
        },
        ["boundary_type"],
        "Boundary context is required for downstream dignity / sovereignty decisions.",
    ),
    (
        "well_trace_lineage", "well",
        {
            "memory_symbol_status": {
                "type": "object",
                "description": "§3.Q — Every memory must know its own symbolic status to prevent memory poisoning.",
                "properties": {
                    "observed_fact": {"type": "boolean"},
                    "interpretation": {"type": "boolean"},
                    "emotional_state": {"type": "boolean"},
                    "ritual_phrase": {"type": "boolean"},
                    "governance_receipt": {"type": "boolean"},
                    "revoked_or_superseded": {"type": "boolean"},
                },
            }
        },
        ["memory_symbol_status"],
        "Memory poisoning prevention. Supersession chain must be preserved.",
    ),

    # ─── HIGH ─────────────────────────────────────────────────────────────
    (
        "arif_init", "arifos",
        {
            "symbolic_context": {
                "type": "object",
                "description": "§3.A — Session must know the symbolic world it operates inside.",
                "properties": {
                    "actor_identity": {"type": "string"},
                    "role_claims": {"type": "array", "items": {"type": "string"}},
                    "cultural_frame": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["maruah", "amanah", "adab", "budi", "daulat"]},
                    },
                    "session_mode": {"type": "string"},
                    "symbolic_risk_profile": {
                        "type": "object",
                        "properties": {
                            "false_seal": {"type": "string", "enum": ["low", "medium", "high"]},
                            "authority_confusion": {"type": "string", "enum": ["low", "medium", "high"]},
                            "ritual_language": {"type": "string", "enum": ["low", "medium", "high"]},
                        },
                    },
                },
            }
        },
        ["symbolic_context"],
        "init must know who is speaking AND what symbolic world the session operates inside.",
    ),
    (
        "arif_observe", "arifos",
        {
            "source_symbol_class": {
                "type": "array",
                "description": "§3.C — Observation result must be classified by source symbol.",
                "items": {
                    "type": "string",
                    "enum": [
                        "legal_document", "corporate_statement", "ritual_text", "personal_memory",
                        "financial_signal", "geological_interpretation", "governance_receipt",
                        "propaganda", "mythic_frame", "social_media_symbol",
                    ],
                },
            },
            "interpretation_warning": {
                "type": "object",
                "properties": {
                    "observed_text_is_not_authority": {"type": "boolean"},
                    "symbol_requires_context": {"type": "boolean"},
                    "possible_performative_effect": {"type": "boolean"},
                },
            },
        },
        None,
        "A PETRONAS annual report is not just information — it is institutional self-symbolisation.",
    ),
    (
        "arif_explore", "arifos",
        {
            "source_symbol_class": {
                "type": "array",
                "description": "§3.C — Same as observe. Exploratory results need the same classification.",
                "items": {
                    "type": "string",
                    "enum": [
                        "legal_document", "corporate_statement", "ritual_text", "personal_memory",
                        "financial_signal", "geological_interpretation", "governance_receipt",
                        "propaganda", "mythic_frame", "social_media_symbol",
                    ],
                },
            },
            "interpretation_warning": {
                "type": "object",
                "properties": {
                    "observed_text_is_not_authority": {"type": "boolean"},
                    "symbol_requires_context": {"type": "boolean"},
                    "possible_performative_effect": {"type": "boolean"},
                },
            },
        },
        None,
        "explore shares observe's classification needs but with broader search.",
    ),
    (
        "geox_claim_create", "geox",
        {
            "symbolic_consequence": {
                "type": "object",
                "description": "§3.G — A geological claim becomes capital-symbolic quickly.",
                "properties": {
                    "map_symbol": {"type": "boolean"},
                    "reserve_booking_risk": {"type": "boolean"},
                    "investment_signal": {"type": "boolean"},
                    "institutional_liability": {"type": "boolean"},
                    "confidence_symbol": {
                        "type": "object",
                        "properties": {"p10_p50_p90_present": {"type": "boolean"}},
                    },
                },
            }
        },
        ["symbolic_consequence"],
        "'This structure is drill-ready' is not just geology — it can become a budget, partner signal, or career liability.",
    ),
    (
        "geox_claim_challenge", "geox",
        {
            "challenge_symbolic_target": {
                "type": "object",
                "description": "§3.H — Social systems collapse when one symbol becomes unquestioned truth.",
                "properties": {
                    "dominant_story": {"type": "string"},
                    "institutional_inertia": {"type": "string", "enum": ["low", "medium", "high"]},
                    "prestige_bias": {"type": "string", "enum": ["low", "medium", "high"]},
                    "seniority_bias": {"type": "string", "enum": ["low", "medium", "high"]},
                    "map_authority_bias": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            }
        },
        ["challenge_symbolic_target"],
        "Challenge the symbol without attacking the person's maruah — critical for PETRONAS-style subsurface work.",
    ),
    (
        "geox_claim_seal", "geox",
        {
            "seal_disambiguation": {
                "type": "object",
                "description": "§3.I — MANDATORY seal disambiguation. Ties to Rule Zero.",
                "properties": {
                    "geological_seal": {"type": "boolean"},
                    "constitutional_SEAL": {"type": "boolean"},
                    "vault_seal": {"type": "boolean"},
                    "trap_seal_lithology": {"type": "boolean"},
                },
            }
        },
        ["seal_disambiguation"],
        "Geological sealing, trap seal, and constitutional SEAL must not be confused.",
    ),
    (
        "geox_prospect_evaluate", "geox",
        {
            "seal_disambiguation": {
                "type": "object",
                "description": "§3.I — Same as geox_claim_seal. Prospect evaluation triggers high-stakes symbol cascades.",
                "properties": {
                    "geological_seal": {"type": "boolean"},
                    "constitutional_SEAL": {"type": "boolean"},
                    "vault_seal": {"type": "boolean"},
                    "trap_seal_lithology": {"type": "boolean"},
                },
            },
            "prospect_symbolic_load": {
                "type": "object",
                "description": "Captures the social weight a prospect evaluation carries.",
                "properties": {
                    "career_signal": {"type": "boolean"},
                    "partner_signal": {"type": "boolean"},
                    "budget_lock_in_risk": {"type": "boolean"},
                },
            },
        },
        ["seal_disambiguation"],
        "A prospect verdict is one of the heaviest symbols in subsurface work.",
    ),
    (
        "wealth_stock_analysis", "wealth",
        {
            "market_symbolic_layer": {
                "type": "object",
                "description": "§3.J — Markets are symbolic machines.",
                "properties": {
                    "signal_type": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["price", "narrative", "status", "fear", "greed", "authority_claim", "herd_symbol"],
                        },
                    },
                    "manipulation_risk": {"type": "string", "enum": ["low", "medium", "high"]},
                    "social_proof_detected": {"type": "boolean"},
                    "tamak_trigger": {"type": "boolean"},
                    "capital_irreversibility": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            }
        },
        ["market_symbolic_layer"],
        "Price, rating, dividend, PE, 'buy call' are not neutral facts — they move behavior.",
    ),
    (
        "wealth_governance_verdict", "wealth",
        {
            "symbolic_capital_assessment": {
                "type": "object",
                "description": "§3.K — Explicit symbolic inputs.",
                "properties": {
                    "legitimacy_signal": {"type": "string"},
                    "trust_symbol": {"type": "string"},
                    "reputational_blast_radius": {"type": "string"},
                    "institutional_maruah_risk": {"type": "string"},
                    "public_private_boundary": {"type": "string"},
                },
            }
        },
        ["symbolic_capital_assessment"],
        "Already has maruah_score / trust_index / peace2 — this makes symbolic inputs explicit.",
    ),
    (
        "well_assess_livelihood", "well",
        {
            "role_symbolics": {
                "type": "object",
                "description": "§3.O — Livelihood is not just income.",
                "properties": {
                    "title_pressure": {"type": "string"},
                    "eldest_child_burden": {"type": "string"},
                    "corporate_rank_signal": {"type": "string"},
                    "public_identity_risk": {"type": "string"},
                    "purpose_symbol_alignment": {"type": "string"},
                },
            }
        },
        ["role_symbolics"],
        "Livelihood is role, maruah, social position, meaning — not just income.",
    ),
    (
        "well_assess_sovereign_entropy", "well",
        {
            "sovereignty_guard": {
                "type": "object",
                "description": "§3.P — Hard guard against symbolic overreach on the operator.",
                "properties": {
                    "no_personality_capture": {"type": "boolean"},
                    "no_behavioral_extraction": {"type": "boolean"},
                    "no_identity_freezing": {"type": "boolean"},
                    "preserve_operator_contradiction": {"type": "boolean"},
                    "do_not_reduce_arif_to_profile": {"type": "boolean"},
                },
            }
        },
        ["sovereignty_guard"],
        "Agent must not convert Arif into a fixed symbol. That would violate sovereignty.",
    ),

    # ─── MEDIUM ────────────────────────────────────────────────────────────
    (
        "wealth_survival_engine", "wealth",
        {
            "symbolic_finance_pressure": {
                "type": "object",
                "description": "§3.L — Survival is not only arithmetic.",
                "properties": {
                    "family_obligation": {"type": "string", "enum": ["low", "medium", "high"]},
                    "status_consumption": {"type": "string", "enum": ["low", "medium", "high"]},
                    "institutional_dependency": {"type": "string", "enum": ["low", "medium", "high"]},
                    "shame_risk": {"type": "string", "enum": ["low", "medium", "high"]},
                    "hidden_commitment": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            }
        },
        ["symbolic_finance_pressure"],
        "Prevents agent from treating money as only spreadsheet flow.",
    ),
    (
        "well_assess_homeostasis", "well",
        {
            "homeostasis_symbolic_layer": {
                "type": "object",
                "description": "§14 MEDIUM — Homeostasis can be misread as cold optimisation. Add the symbolic layer.",
                "properties": {
                    "vitality_social_meaning": {"type": "string"},
                    "sleep_charge_grief_overlay": {"type": "boolean"},
                    "energy_symbol_for_others": {"type": "string"},
                },
            }
        },
        None,
        "Homeostasis numbers are read as social signals, not just internal telemetry.",
    ),
    (
        "well_validate_vitality", "well",
        {
            "vitality_symbolic_load": {
                "type": "object",
                "description": "§14 MEDIUM — Vitality validation has social weight.",
                "properties": {
                    "capability_claim": {"type": "boolean"},
                    "identity_reduction_risk": {"type": "boolean"},
                    "operator_pacing_meaning": {"type": "string"},
                },
            }
        },
        None,
        "Validate that vitality signals do not become identity freezing.",
    ),
]


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    written: list[str] = []
    for component, organ, block, required, note in COMPONENTS:
        schema = _make_schema(component, organ, block, required, note)
        path = os.path.join(OUT_DIR, f"{component}.schema.json")
        with open(path, "w", encoding="utf-8") as f:
            import json
            json.dump(schema, f, indent=2, ensure_ascii=False)
            f.write("\n")
        written.append(path)
    print(f"Wrote {len(written)} component schemas to {OUT_DIR}")
    for p in written:
        print(f"  - {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())