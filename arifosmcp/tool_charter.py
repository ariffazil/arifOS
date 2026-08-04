"""
arifOS Tool Operational Charter
═══════════════════════════════════

Rich metadata layer for all 13 canonical MCP tools.
Tells LLM clients WHEN, WHY, HOW, and WHEN NOT to use each tool.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL SEQUENCE — The Constitutional Golden Path
# ═══════════════════════════════════════════════════════════════════════════════

# Live public kernel surface (8 verbs). Legacy absorbed names remain in
# TOOL_CHARTER for internal/diagnostic consumers but are NOT in this order.
CANONICAL_ORDER: list[str] = [
    "arif_init",  # 000
    "arif_observe",  # 111
    "arif_think",  # 333
    "arif_route",  # 444
    "arif_memory",  # memory governor
    "arif_judge",  # 888
    "arif_forge",  # 777
    "arif_seal",  # 999
]

# Shared agent contract: how to act on verdict fields carried by every response.
# Put on init (first verb agents read) and referenced by all others.
VERDICT_RESPONSE_CONTRACT: dict[str, str] = {
    "SEAL": "Proceed to next canonical stage. Authority granted for this branch only.",
    "HOLD": "Stop autonomous progression. Escalate to human (F13). Do not forge/seal.",
    "SABAR": "Wait / backoff / retry after degraded clears. Do not invent success.",
    "VOID": "Abandon this branch. Do not retry the same candidate without new evidence.",
    "PARTIAL_PROCEED": "Continue OBSERVE/THINK only. mutation_allowed and seal_allowed false.",
}

# Kernel-wide degraded / transport failure contract (agents need this in manifest).
FAILURE_MODES_KERNEL: dict[str, Any] = {
    "http_5xx": {
        "agent_action": "Backoff ≥60s then retry once. If persists: declare SABAR, do not forge.",
        "retry_budget": 1,
        "fallback": "arif_observe(mode=vitals) then re-init validate",
    },
    "deployment_drift": {
        "agent_action": "Treat as HOLD on mutation. Observe/think only until source=built=deployed.",
        "next_action": "RECONCILE_SOURCE_BUILT_DEPLOYED",
    },
    "empty_manifest": {
        "agent_action": "Use live input_schema mode enum only; do not invent modes from prose.",
    },
}

# Risk scale Rosetta: display tier ↔ passport T-tier (keep risk_passport authoritative).
RISK_SCALE_MAP: dict[str, str] = {
    "low": "T1",
    "medium": "T2",
    "high": "T3",
    "critical": "T4/T5",
}


# ═══════════════════════════════════════════════════════════════════════════════
# OPERATIONAL METADATA — Per-tool structured guidance
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_CHARTER: dict[str, dict[str, Any]] = {
    # ── 000_INIT ─────────────────────────────────────────────────────────────
    "arif_init": {
        "eureka_insight": "Identity is the root of accountability. An unbound session is mathematically equivalent to chaos.",
        "stage_code": "000",
        "stage_name": "INIT",
        "purpose": [
            "Bootstrap a governed constitutional session.",
            "Bind actor identity to the 13-floor constitution.",
            "Establish entropy baseline and session manifest.",
        ],
        "use_when": [
            "User asks to initialize a governed arifOS session.",
            "A new constitutional workflow begins.",
            "Actor identity must be bound before later stages.",
            "No active session_id exists for the current context.",
        ],
        "do_not_use_when": [
            "User only asks a general factual question.",
            "No governed session is needed.",
            "Request is casual and does not require constitutional state.",
            "A valid session already exists and only needs resumption.",
        ],
        "modes": {
            "init": {
                "purpose": "Start a new governed session with full constitutional binding.",
                "required_parameters": ["actor_id"],
                "optional_parameters": ["ack_irreversible", "epoch_id", "intent", "verbosity"],
                "returns": [
                    "session_id",
                    "session_token",
                    "constitution_hash",
                    "allowed_next_tools",
                    "degraded",
                ],
            },
            "light": {
                "purpose": "Lightweight bind — same as init with compact payload (agent-friendly).",
                "required_parameters": ["actor_id"],
                "returns": ["session_id", "session_token", "authority_band"],
            },
            "resume": {
                "purpose": "Reattach to an existing session by session_id.",
                "required_parameters": ["session_id"],
                "optional_parameters": ["session_token"],
                "returns": ["session_id", "status", "allowed_next_tools"],
            },
            "validate": {
                "purpose": "Check session health and constitutional alignment.",
                "required_parameters": ["session_id"],
                "returns": ["session_id", "status", "floors_ok", "floors_fail"],
            },
            "canary": {
                "purpose": "Probe kernel liveness without full session bind.",
                "returns": ["ok", "release_id", "tool_count"],
            },
            "preflight": {
                "purpose": "Pre-flight checks before mutation (drift, floors, substrate).",
                "optional_parameters": ["session_id"],
                "returns": ["preflight_ok", "degraded", "blockers"],
            },
            "triage": {
                "purpose": "Session triage mode of arif_init (NOT a separate tool). Classify readiness.",
                "optional_parameters": ["session_id", "intent"],
                "returns": ["triage_class", "next_safe_action", "degraded"],
            },
            "epoch_open": {
                "purpose": "Open a new epoch, binding epoch_id to session_id (H3).",
                "required_parameters": ["session_id"],
                "optional_parameters": ["epoch_id"],
                "returns": ["epoch_id", "session_id", "status"],
            },
            "epoch_seal": {
                "purpose": "Seal the current epoch, writing Epoch Seal JSON to vault (H3).",
                "required_parameters": ["session_id"],
                "optional_parameters": ["epoch_id", "ack_irreversible"],
                "returns": ["epoch_id", "session_id", "vault_entry_id", "status"],
            },
            "opt_out": {
                "purpose": "Opt out of optional profiling / telemetry for this session.",
                "required_parameters": ["session_id"],
                "returns": ["status"],
            },
            "opt_out_profiling": {
                "purpose": "Opt out of profiling only (narrower than opt_out).",
                "required_parameters": ["session_id"],
                "returns": ["status"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "meaning": "Operation mode for the session lifecycle.",
                "allowed_values": [
                    "init",
                    "light",
                    "resume",
                    "validate",
                    "canary",
                    "preflight",
                    "triage",
                    "epoch_open",
                    "epoch_seal",
                    "opt_out",
                    "opt_out_profiling",
                ],
                "default": "init",
                "required": True,
            },
            "actor_id": {
                "type": "string",
                "meaning": "Sovereign actor identifier (L11 AUTH). Required for init.",
                "required_when": [{"mode": "init"}],
            },
            "ack_irreversible": {
                "type": "boolean",
                "meaning": "Explicit human acknowledgment for irreversible operations (F1 Amanah).",
                "default": False,
            },
            "session_id": {
                "type": "string",
                "meaning": "Existing session UUID. Required for resume/validate/epoch_*.",
                "required_when": [
                    {"mode": "resume"},
                    {"mode": "validate"},
                    {"mode": "epoch_open"},
                    {"mode": "epoch_seal"},
                ],
            },
            "epoch_id": {
                "type": "string",
                "meaning": "Epoch identifier. Optional for init; required for epoch_seal if not bound.",
            },
        },
        "outputs": {
            "session_id": {
                "meaning": "Unique identifier for the governed session.",
                "use_in_next_tools": True,
            },
            "session_token": {
                "meaning": "SCT (sct_v1.*) — Session Capability Token. Pass to every downstream arif_* and federation organ call.",
                "use_in_next_tools": True,
                "trust_role": "capability_bearer",
            },
            "constitution_hash": {
                "meaning": "SHA-256 fingerprint of the active constitutional rulebase.",
                "trust_role": "integrity_anchor",
            },
            "allowed_next_tools": {
                "meaning": "Suggested safe continuation path from this session.",
            },
            "degraded": {
                "meaning": "List of degraded conditions (e.g. kernel_drift). Non-empty → mutation_allowed=false.",
            },
        },
        "risk": {
            "tier": "low",
            "irreversible": False,
            "requires_human_ack": False,
            "requires_judge_state_hash": False,
            "requires_vault_entry_id": False,
            "risk_passport_authoritative": True,
            "display_tier_note": "risk.tier is display only; use risk_passport for machine gates.",
        },
        "state": {
            "requires_session_id": False,
            "accepts_anonymous": False,
            "carries_forward": [
                "session_id",
                "session_token",
                "constitution_hash",
            ],
        },
        "canonical_order": CANONICAL_ORDER,
        "verdict_response_contract": VERDICT_RESPONSE_CONTRACT,
        "failure_modes": FAILURE_MODES_KERNEL,
        "next_recommended_tools": [
            "arif_observe",
            "arif_think",
            "arif_route",
        ],
        "authority_boundary": {
            "may": ["bind", "validate", "resume", "triage", "preflight", "light", "canary"],
            "may_not": [
                "self-approve irreversible actions",
                "override human judge",
                "claim sovereign authority",
            ],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Start a governed reasoning session",
                    "call": {
                        "tool": "arif_init",
                        "args": {"mode": "init", "actor_id": "arif"},
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Tell me a joke",
                    "reason_not_to_call": "No constitutional session needed.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": False,
        },
    },
    # ── 111_SENSE ────────────────────────────────────────────────────────────
    "arif_observe": {
        "eureka_insight": "Observation alters the observer. All ingested reality must be tagged with an epistemic confidence band.",
        "stage_code": "111",
        "stage_name": "SENSE",
        "purpose": [
            "Gather raw observational data across multiple sensory layers.",
            "Search, ingest, compass, atlas, entropy, and vitals.",
        ],
        "use_when": [
            "User asks for information retrieval or environmental scan.",
            "A query needs grounding before reasoning.",
            "System health or entropy state must be checked.",
        ],
        "do_not_use_when": [
            "User asks for final judgment or arbitration.",
            "The task requires constitutional reasoning, not raw observation.",
            "The task requires system modification or execution.",
        ],
        "modes": {
            "search": {
                "purpose": "Free-text query against configured search backends.",
                "required_parameters": ["query"],
                "returns": ["query", "results", "source", "omega_0"],
            },
            "fetch": {
                "purpose": "Fetch a URL as evidence (live mode; not a separate arif_fetch tool).",
                "required_parameters": ["url"],
                "returns": ["url", "content", "source"],
            },
            "hybrid_discovery": {
                "purpose": "Hybrid search + discovery across configured backends.",
                "required_parameters": ["query"],
                "returns": ["results", "sources"],
            },
            "ingest": {
                "purpose": "Fetch and parse a specific URL into structured evidence.",
                "required_parameters": ["url"],
                "returns": ["url", "ingested", "note"],
            },
            "compass": {
                "purpose": "Directional / geospatial heading query.",
                "returns": ["heading", "confidence"],
            },
            "atlas": {
                "purpose": "Structured map/layer retrieval.",
                "required_parameters": ["layers"],
                "returns": ["map", "layers"],
            },
            "entropy_dS": {
                "purpose": "Measure thermodynamic entropy delta of the session.",
                "returns": ["delta_S", "trend"],
            },
            "vitals": {
                "purpose": "CPU, memory, and I/O telemetry.",
                "returns": ["cpu", "mem", "io"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": [
                    "search",
                    "fetch",
                    "hybrid_discovery",
                    "ingest",
                    "compass",
                    "atlas",
                    "entropy_dS",
                    "vitals",
                ],
                "default": "search",
            },
            "query": {
                "type": "string",
                "meaning": "Free-text search query or observation target.",
                "required_when": [
                    {"mode": "search"},
                    {"mode": "hybrid_discovery"},
                ],
            },
            "url": {
                "type": "string",
                "meaning": "Target URL for fetch/ingest mode.",
                "required_when": [{"mode": "fetch"}, {"mode": "ingest"}],
            },
            "layers": {
                "type": "list[string]",
                "meaning": "Layer identifiers for atlas mode.",
                "required_when": [{"mode": "atlas"}],
            },
            "session_id": {
                "type": "string",
                "meaning": "Governing session (recommended).",
            },
            "session_token": {
                "type": "string",
                "meaning": "SCT from arif_init — carry forward for federation continuity.",
            },
        },
        "outputs": {
            "results": {"meaning": "Observational data matching the query."},
            "omega_0": {"meaning": "Uncertainty band (0.03–0.05 = humble)."},
            "delta_S": {"meaning": "Entropy change from this observation."},
        },
        "risk": {"tier": "low", "irreversible": False, "requires_human_ack": False},
        "state": {
            "requires_session_id": False,
            "recommended_session_id": True,
            "carries_forward": ["session_id", "session_token"],
        },
        "canonical_order": CANONICAL_ORDER,
        "next_recommended_tools": ["arif_think", "arif_route"],
        "authority_boundary": {
            "may": ["observe", "search", "measure"],
            "may_not": ["modify", "judge", "seal"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Search for recent news on AI governance",
                    "call": {
                        "tool": "arif_observe",
                        "args": {"mode": "search", "query": "AI governance 2026"},
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Deploy the new build",
                    "reason_not_to_call": "Sense does not execute or deploy. Use arif_forge after judge seal.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": False,
            "redaction_required": False,
        },
    },
    # ── 222_FETCH ────────────────────────────────────────────────────────────
    "arif_fetch": {
        "eureka_insight": "Evidence is not truth; it is a cryptographic receipt of a claim at a specific timestamp.",
        "stage_code": "222",
        "stage_name": "FETCH",
        "purpose": [
            "Evidence-preserving web ingestion with sequential thinking.",
            "Retrieves verifiable external evidence for constitutional reasoning.",
        ],
        "use_when": [
            "User asks for verified facts from external sources.",
            "A constitutional reasoning step needs grounded evidence.",
            "Claims require reproducible citations (F3 Witness).",
        ],
        "do_not_use_when": [
            "User wants opinion, synthesis, or reasoning without evidence.",
            "The task is creative or speculative.",
            "No URL or query can be formulated.",
        ],
        "modes": {
            "fetch": {
                "purpose": "Retrieve content from a specific URL with optional sequential thinking.",
                "required_parameters": ["url"],
                "optional_parameters": [
                    "thinking_depth",
                    "thinking_budget",
                    "sequential_mode",
                ],
                "returns": ["status", "content", "confidence", "thinking_sequence"],
            },
            "search": {
                "purpose": "Search the web for evidence matching a query.",
                "required_parameters": ["query"],
                "returns": ["status", "results", "confidence"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["fetch", "search"],
                "default": "fetch",
            },
            "url": {
                "type": "string",
                "meaning": "Target URL for evidence retrieval.",
                "required_when": [{"mode": "fetch"}],
            },
            "query": {
                "type": "string",
                "meaning": "Search query for evidence discovery.",
                "required_when": [{"mode": "search"}],
            },
            "thinking_depth": {
                "type": "integer",
                "meaning": "Max reasoning steps (0–10). 0 = disabled.",
                "default": 0,
            },
            "thinking_budget": {
                "type": "number",
                "meaning": "Token/time budget for thinking (0.0–10.0).",
                "default": 1.0,
            },
            "sequential_mode": {
                "type": "string",
                "allowed_values": ["fast", "deliberate", "exhaustive"],
                "default": "deliberate",
            },
            "allow_early_termination": {
                "type": "boolean",
                "meaning": "Stop if confidence exceeds threshold.",
                "default": True,
            },
            "confidence_threshold": {
                "type": "number",
                "meaning": "Early-stop confidence threshold (0.0–1.0).",
                "default": 0.90,
            },
        },
        "outputs": {
            "content": {"meaning": "Retrieved evidence text or structured data."},
            "confidence": {"meaning": "Evidence reliability score (0.0–1.0)."},
            "thinking_sequence": {"meaning": "Sequential reasoning trace if thinking_depth > 0."},
        },
        "risk": {"tier": "medium", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": False, "recommended_session_id": True},
        "next_recommended_tools": ["arif_think", "arif_critique"],
        "authority_boundary": {
            "may": ["retrieve", "search", "ingest"],
            "may_not": ["modify source", "judge", "seal"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Get evidence for climate policy claims",
                    "call": {
                        "tool": "arif_fetch",
                        "args": {
                            "mode": "fetch",
                            "url": "https://ipcc.gov/report",
                            "thinking_depth": 3,
                        },
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Write a poem about the ocean",
                    "reason_not_to_call": "Fetch is for evidence, not creative writing.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": True,
        },
    },
    # ── 333_MIND ─────────────────────────────────────────────────────────────
    "arif_think": {
        "eureka_insight": "Cleverness without correctness is dangerous (G-Score). The agent must think within the constitutional box.",
        "stage_code": "333",
        "stage_name": "MIND",
        "purpose": [
            "Symbolic constitutional reasoning kernel.",
            "Evaluates claims using explicit F1–L13 axioms.",
            "Produces structured reasoning traces with confidence bands.",
        ],
        "use_when": [
            "User asks for governed reasoning or constitutional analysis.",
            "A claim, plan, or decision needs axiom-based evaluation.",
            "Inductive, deductive, abductive, or critical reasoning is required.",
        ],
        "do_not_use_when": [
            "User only needs raw evidence fetching.",
            "The task requires final arbitration (use 888_JUDGE).",
            "The task requires execution or system modification (use arif_forge after 888 SEAL).",
            "The query is purely factual and needs no constitutional framing.",
        ],
        "modes": {
            "reason": {
                "purpose": "General constitutional reasoning with explicit axiom trace.",
                "required_parameters": ["query"],
                "returns": [
                    "conclusion",
                    "confidence",
                    "axioms_used",
                    "reasoning_trace",
                ],
            },
            "reflect": {
                "purpose": "Introspective replay of prior reasoning steps.",
                "returns": ["reflection", "improvements"],
            },
            "verify": {
                "purpose": "Truth-check a specific claim against the constitution.",
                "required_parameters": ["query"],
                "returns": ["verdict", "evidence", "confidence"],
            },
            "axioms": {
                "purpose": "List available constitutional axioms and their confidence.",
                "returns": ["axioms"],
            },
            "plan": {
                "purpose": "Generate a governed execution plan (PlanReceipt) with task_graph and reversibility_map (H2).",
                "required_parameters": ["query"],
                "returns": ["plan_receipt", "plan_id", "vault_entry_id"],
            },
            "plan_review": {
                "purpose": "Retrieve an existing plan by plan_id.",
                "required_parameters": ["plan_id"],
                "returns": ["plan_receipt"],
            },
            "plan_approve": {
                "purpose": "Approve a pending plan so it can be used by arif_forge (H2).",
                "required_parameters": ["plan_id"],
                "returns": ["plan_id", "status"],
            },
            "refactor_plan": {
                "purpose": "Refactor an existing plan_id into a tighter task_graph.",
                "required_parameters": ["plan_id"],
                "returns": ["plan_receipt", "plan_id"],
            },
            "metabolize": {
                "purpose": "Metabolize evidence/receipts into a structured mind state.",
                "required_parameters": ["query"],
                "returns": ["metabolized", "delta_S"],
            },
            "simulate": {
                "purpose": "Simulate outcomes of a candidate without mutation.",
                "required_parameters": ["query"],
                "returns": ["simulation", "risks"],
            },
            "wonder": {
                "purpose": "Open-ended generative exploration under F7 humility bounds.",
                "required_parameters": ["query"],
                "returns": ["wonderings", "omega_0"],
            },
            "atlas": {
                "purpose": "Cognitive atlas / map of reasoning zones for the query.",
                "required_parameters": ["query"],
                "returns": ["atlas", "zones"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": [
                    "reason",
                    "reflect",
                    "verify",
                    "axioms",
                    "plan",
                    "plan_review",
                    "plan_approve",
                    "refactor_plan",
                    "metabolize",
                    "simulate",
                    "wonder",
                    "atlas",
                ],
                "default": "reason",
            },
            "query": {
                "type": "string",
                "meaning": "The claim, question, or plan to reason over.",
                "required_when": [
                    {"mode": "reason"},
                    {"mode": "verify"},
                    {"mode": "plan"},
                    {"mode": "metabolize"},
                    {"mode": "simulate"},
                    {"mode": "wonder"},
                    {"mode": "atlas"},
                ],
            },
            "plan_id": {
                "type": "string",
                "meaning": "Plan identifier (for plan_review / plan_approve / refactor_plan).",
                "required_when": [
                    {"mode": "plan_review"},
                    {"mode": "plan_approve"},
                    {"mode": "refactor_plan"},
                ],
            },
            "session_id": {
                "type": "string",
                "meaning": "Governing session (recommended).",
            },
            "session_token": {
                "type": "string",
                "meaning": "SCT from arif_init.",
            },
        },
        "outputs": {
            "conclusion": {"meaning": "Reasoning classification or structured conclusion."},
            "confidence": {"meaning": "Calibrated confidence (0.0–1.0), not certainty."},
            "axioms_used": {"meaning": "List of constitutional axioms invoked in the reasoning."},
            "reasoning_trace": {
                "meaning": "Step-by-step derivation with premise and conclusion per step."
            },
        },
        "risk": {"tier": "medium", "irreversible": False, "requires_human_ack": False},
        "state": {
            "requires_session_id": False,
            "recommended_session_id": True,
            "emits_chain_data": True,
            "carries_forward": ["session_id", "session_token", "plan_id"],
        },
        "canonical_order": CANONICAL_ORDER,
        "next_recommended_tools": ["arif_route", "arif_judge", "arif_memory"],
        "authority_boundary": {
            "may": ["reason", "classify", "suggest"],
            "may_not": ["approve irreversible action", "replace human judgment"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Assess whether this claim is constitutionally stable",
                    "call": {
                        "tool": "arif_think",
                        "args": {
                            "mode": "verify",
                            "query": "Deploying without review is safe",
                        },
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Deploy the build now",
                    "reason_not_to_call": "Mind reasons; it does not execute. Use forge after judge seal.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": False,
            "redaction_required": False,
        },
    },
    # ── 444_ROUTE (live public name: arif_route) ─────────────────────────────
    "arif_route": {
        "eureka_insight": "Orchestration is the physics of routing. Intent→organ is a decision, not an execution. Bridge is opt-in.",
        "stage_code": "444",
        "stage_name": "ROUTE",
        "purpose": [
            "Dispatch natural-language intent to GEOX / WEALTH / WELL / A-FORGE.",
            "Optionally bridge-call an organ tool after routing decision.",
            "Bind six-mission cockpit plans when mission_id is known.",
        ],
        "use_when": [
            "You know what the user wants but not which organ owns it.",
            "Domain evidence is needed from GEOX, WEALTH, or WELL.",
            "You want a routing decision only (mode=route) before any organ call.",
            "You have organ_tool + arguments and want governed bridge dispatch (mode=bridge).",
        ],
        "do_not_use_when": [
            "Kernel-only work (init/observe/think/judge/forge/seal) — call those verbs directly.",
            "You need a binding verdict — use arif_judge.",
            "You need irreversible mutation — use arif_forge after SEAL.",
            "Casual chat with no organ evidence required.",
        ],
        "modes": {
            "route": {
                "purpose": "Return routing decision only (organ, confidence, mission). No organ call.",
                "required_parameters": ["intent"],
                "optional_parameters": ["organ", "mission_id", "session_id", "session_token"],
                "returns": ["organ", "confidence", "mission_id", "rationale", "allowed_tools"],
            },
            "bridge": {
                "purpose": "Route then invoke organ_tool with arguments on the target organ.",
                "required_parameters": ["intent", "organ_tool"],
                "optional_parameters": [
                    "organ",
                    "arguments",
                    "mission_id",
                    "session_id",
                    "session_token",
                ],
                "returns": ["organ", "organ_tool", "result", "bridge_receipt"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["route", "bridge"],
                "default": "route",
                "meaning": "route = decision only; bridge = decision + organ tool call.",
            },
            "intent": {
                "type": "string",
                "meaning": "Natural-language description of what the user wants.",
                "required_when": [{"mode": "route"}, {"mode": "bridge"}],
            },
            "task": {
                "type": "string",
                "meaning": "Alias for intent (backward compat).",
            },
            "organ": {
                "type": "string",
                "meaning": "Optional explicit organ override (GEOX|WEALTH|WELL|A-FORGE). Skips intent matching.",
            },
            "organ_tool": {
                "type": "string",
                "meaning": "Tool name on the target organ. Required for mode=bridge; absent → route-only.",
                "required_when": [{"mode": "bridge"}],
            },
            "arguments": {
                "type": "object|string",
                "meaning": "Arguments to pass to organ_tool when bridging.",
            },
            "mission_id": {
                "type": "string",
                "meaning": "Human-cockpit mission: investigate|interpret|decide|build|monitor|remember.",
            },
            "actor_id": {"type": "string", "meaning": "Calling actor."},
            "session_id": {"type": "string", "meaning": "Governing session."},
            "session_token": {
                "type": "string",
                "meaning": "SCT from arif_init — required for federation organ continuity.",
            },
        },
        "outputs": {
            "organ": {"meaning": "Selected organ (GEOX|WEALTH|WELL|A-FORGE|kernel)."},
            "confidence": {"meaning": "Routing confidence 0.0–1.0."},
            "mission_id": {"meaning": "Bound mission if classified or provided."},
            "result": {"meaning": "Organ tool result when mode=bridge."},
            "bridge_receipt": {"meaning": "Audit receipt for the bridge call."},
        },
        "risk": {"tier": "low", "irreversible": False, "requires_human_ack": False},
        "state": {
            "requires_session_id": False,
            "recommended_session_id": True,
            "carries_forward": ["session_id", "session_token", "mission_id"],
        },
        "canonical_order": CANONICAL_ORDER,
        "next_recommended_tools": [
            "arif_think",
            "arif_memory",
            "arif_judge",
        ],
        "authority_boundary": {
            "may": ["route", "bridge_read", "suggest_organ"],
            "may_not": ["self-seal organ results", "bypass judge", "mutate production"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Which organ handles seismic interpretation?",
                    "call": {
                        "tool": "arif_route",
                        "args": {
                            "mode": "route",
                            "intent": "interpret this seismic section",
                        },
                    },
                },
                {
                    "user_intent": "Get WELL readiness for decision fitness",
                    "call": {
                        "tool": "arif_route",
                        "args": {
                            "mode": "bridge",
                            "intent": "operator readiness",
                            "organ": "WELL",
                            "organ_tool": "well_reflect",
                        },
                    },
                },
            ],
            "bad": [
                {
                    "user_intent": "Deploy the build",
                    "reason_not_to_call": "Route does not execute. Use arif_judge then arif_forge after SEAL.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": False,
        },
        "failure_modes": FAILURE_MODES_KERNEL,
    },
    # ── 444_REPLY ────────────────────────────────────────────────────────────
    "arif_compose": {
        "eureka_insight": "Communication is action. Strip all ghost-sentience (Anti-Hantu) and manipulative intent before delivery.",
        "stage_code": "444r",
        "stage_name": "REPLY",
        "purpose": [
            "Governed response composition with constitutional tone control.",
            "Ensures replies are truthful (F2), clear (F4), empathetic (F6), humble (F7).",
        ],
        "use_when": [
            "User needs a human-facing reply drafted or refined.",
            "A message needs constitutional tone control.",
            "Citations must be injected into a response.",
        ],
        "do_not_use_when": [
            "The task requires reasoning, evidence, or judgment rather than composition.",
            "The user wants raw data without formatting.",
        ],
        "modes": {
            "compose": {
                "purpose": "Draft a constitutional reply from a raw message.",
                "required_parameters": ["message"],
                "returns": [
                    "composed",
                    "tone",
                    "delta_S",
                    "f02_score",
                    "f04_score",
                    "f07_score",
                ],
            },
            "style": {
                "purpose": "Transform the message to a target constitutional tone.",
                "required_parameters": ["message", "style"],
                "returns": ["composed", "tone"],
            },
            "cite": {
                "purpose": "Inject L02-verified citations into an existing message.",
                "required_parameters": ["message", "citations"],
                "returns": ["composed", "citations_injected"],
            },
            "summary": {
                "purpose": "Condense a long message while preserving constitutional intent (L07).",
                "required_parameters": ["message"],
                "returns": ["composed", "tone", "key_points"],
            },
            "format": {
                "purpose": "Apply structural formatting — headings, bullets, concise paragraphs.",
                "required_parameters": ["message"],
                "returns": ["composed", "delta_S"],
            },
            "nudge": {
                "purpose": "Append L05 (Peace) / L06 (Empathy) guidance nudge without commanding.",
                "required_parameters": ["message"],
                "returns": ["composed", "tone", "delta_S"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["compose", "style", "cite", "summary"],
                "default": "compose",
            },
            "message": {
                "type": "string",
                "meaning": "Raw message text to compose or transform.",
                "required_when": [
                    {"mode": "compose"},
                    {"mode": "style"},
                    {"mode": "cite"},
                    {"mode": "summary"},
                ],
            },
            "style": {
                "type": "string",
                "meaning": "Tone/style directive (neutral, empathetic, terse, formal, technical).",
                "required_when": [{"mode": "style"}],
            },
            "citations": {
                "type": "list[string]",
                "meaning": "List of verified source identifiers to cite.",
                "required_when": [{"mode": "cite"}],
            },
        },
        "outputs": {
            "composed": {"meaning": "Constitutionally composed output text."},
            "tone": {
                "meaning": "Applied tone tag (neutral, empathetic, terse, formal, technical)."
            },
            "delta_S": {"meaning": "Entropy change from composition (negative = clarity added)."},
            "f02_score": {"meaning": "L02 Truth score (0.0–1.0)."},
            "f04_score": {"meaning": "L04 Clarity score (0.0–1.0)."},
            "f07_score": {"meaning": "L07 Humility score (0.0–1.0)."},
            "citations_injected": {"meaning": "Citation sources added to the message."},
        },
        "risk": {"tier": "low", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": False, "recommended_session_id": True},
        "next_recommended_tools": ["arif_memory_recall", "arif_gateway_connect"],
        "authority_boundary": {
            "may": ["compose", "format", "cite"],
            "may_not": ["judge", "seal", "execute"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Draft a formal response to the audit report",
                    "call": {
                        "tool": "arif_compose",
                        "args": {
                            "mode": "style",
                            "message": "We acknowledge the findings...",
                            "style": "formal",
                        },
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Judge whether the report is acceptable",
                    "reason_not_to_call": "Reply composes text; it does not judge. Use arif_judge.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": False,
        },
    },
    # ── MEMORY GOVERNOR (live public name: arif_memory) ──────────────────────
    "arif_memory": {
        "eureka_insight": "Memory is not truth until provenance-bound. Truth is not final until sealed (L6 VAULT999).",
        "stage_code": "555",
        "stage_name": "MEMORY",
        "purpose": [
            "Governed L1–L6 semantic recall, storage, promotion, revision, and forget.",
            "Preserve epistemic labels across memory lifecycle.",
            "Enforce F1 reversibility (supersede/tombstone) and F13 on forget.",
        ],
        "use_when": [
            "Need prior session/decision context before reasoning or judging.",
            "Store a provisional memory with truth_class and provenance.",
            "Promote / revise / forget memory under floor gates.",
            "Audit memory lineage or attest integrity.",
        ],
        "do_not_use_when": [
            "Need immutable civilizational seal — use arif_seal (L6 write path).",
            "Need live web evidence — use arif_observe.",
            "Need organ compute (earth/capital/vitality) — use arif_route.",
            "Casual note with no provenance — do not pollute memory tiers.",
        ],
        "modes": {
            "recall": {
                "purpose": "Semantic / hybrid recall across memory tiers.",
                "required_parameters": ["query"],
                "optional_parameters": ["tier", "top_k", "hybrid", "graph_first"],
                "returns": ["memories", "confidence", "tier_hits"],
            },
            "inspect": {
                "purpose": "Inspect a single memory_id or aspect without mutation.",
                "required_parameters": ["memory_id"],
                "returns": ["memory", "provenance", "truth_class"],
            },
            "attest": {
                "purpose": "Attest integrity of a memory or seal lineage.",
                "optional_parameters": ["memory_id", "seal_id", "include_proof"],
                "returns": ["attested", "proof"],
            },
            "remember": {
                "purpose": "Write a new provisional memory with provenance.",
                "required_parameters": ["content"],
                "optional_parameters": [
                    "truth_class",
                    "provenance",
                    "tier_hint",
                    "memory_class",
                ],
                "returns": ["memory_id", "tier", "status"],
            },
            "promote": {
                "purpose": "Promote memory across tiers (requires floors + often human_approval).",
                "required_parameters": ["memory_id", "to_tier"],
                "optional_parameters": [
                    "from_tier",
                    "promotion_reason",
                    "required_floors_satisfied",
                    "human_approval",
                ],
                "returns": ["memory_id", "from_tier", "to_tier", "status"],
            },
            "revise": {
                "purpose": "Supersede content (reversible correction event).",
                "required_parameters": ["memory_id", "new_content"],
                "optional_parameters": ["correction_event", "new_truth_class"],
                "returns": ["memory_id", "supersedes_memory_id", "status"],
            },
            "forget": {
                "purpose": "Tombstone a memory. F13 — human ack required for hard forget.",
                "required_parameters": ["memory_id"],
                "optional_parameters": [
                    "human_approval",
                    "require_human_ack",
                    "tombstone_text",
                    "cascade",
                ],
                "returns": ["memory_id", "tombstoned", "status"],
            },
            "audit": {
                "purpose": "Audit memory scope / policy / lineage for a query or memory_id.",
                "optional_parameters": ["query", "memory_id", "scope"],
                "returns": ["audit_report", "violations"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": [
                    "recall",
                    "inspect",
                    "attest",
                    "remember",
                    "promote",
                    "revise",
                    "forget",
                    "audit",
                ],
                "default": "recall",
            },
            "query": {
                "type": "string",
                "meaning": "Semantic search query (recall/audit).",
                "required_when": [{"mode": "recall"}],
            },
            "content": {
                "type": "string",
                "meaning": "Text body for remember mode.",
                "required_when": [{"mode": "remember"}],
            },
            "memory_id": {
                "type": "string",
                "meaning": "Target memory UUID.",
                "required_when": [
                    {"mode": "inspect"},
                    {"mode": "promote"},
                    {"mode": "revise"},
                    {"mode": "forget"},
                ],
            },
            "new_content": {
                "type": "string",
                "meaning": "Replacement content for revise.",
                "required_when": [{"mode": "revise"}],
            },
            "to_tier": {
                "type": "string",
                "meaning": "Destination tier for promote (L1–L6).",
                "required_when": [{"mode": "promote"}],
            },
            "human_approval": {
                "type": "boolean",
                "meaning": "Explicit human approval for promote/forget gates.",
                "default": False,
            },
            "session_id": {"type": "string", "meaning": "Governing session."},
            "session_token": {"type": "string", "meaning": "SCT from arif_init."},
            "actor_id": {"type": "string", "meaning": "Calling actor (F11 attribution)."},
        },
        "outputs": {
            "memories": {"meaning": "Retrieved entries with truth_class + provenance."},
            "memory_id": {"meaning": "UUID of written or targeted memory."},
            "tier": {"meaning": "Memory tier L1–L6."},
            "status": {"meaning": "Operation status."},
            "confidence": {"meaning": "Recall confidence (inherits source epistemic band)."},
        },
        "risk": {
            "tier": "medium",
            "irreversible": False,
            "requires_human_ack": False,
            "note": "forget with hard tombstone can be irreversible → human_approval required.",
        },
        "state": {
            "requires_session_id": True,
            "accepts_anonymous": False,
            "carries_forward": ["session_id", "session_token", "memory_id"],
        },
        "canonical_order": CANONICAL_ORDER,
        "next_recommended_tools": ["arif_think", "arif_judge"],
        "authority_boundary": {
            "may": ["recall", "inspect", "attest", "remember", "revise"],
            "may_not": [
                "unauthorized forget without human_approval",
                "claim sealed truth without vault lineage",
                "bypass F2 truth_class gates",
            ],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "What did we decide about the deployment strategy?",
                    "call": {
                        "tool": "arif_memory",
                        "args": {"mode": "recall", "query": "deployment strategy"},
                    },
                },
                {
                    "user_intent": "Store this session finding as provisional memory",
                    "call": {
                        "tool": "arif_memory",
                        "args": {
                            "mode": "remember",
                            "content": "Manifest drift: route/memory empty keys",
                            "truth_class": "observed",
                        },
                    },
                },
            ],
            "bad": [
                {
                    "user_intent": "Delete all past memories",
                    "reason_not_to_call": "forget is tombstone-scoped, F13-gated. Never mass-delete.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": True,
            "writes_memory": True,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": True,
        },
        "failure_modes": FAILURE_MODES_KERNEL,
    },
    # ── 666_HEART ────────────────────────────────────────────────────────────
    "arif_critique": {
        "eureka_insight": "Logic optimizes; empathy restrains. Human impact (κᵣ) is a measurable thermodynamic load.",
        "stage_code": "666",
        "stage_name": "HEART",
        "purpose": [
            "Ethical critique, risk assessment, and empathy scan.",
            "Evaluates proposed actions against 8 risk categories.",
            "Forces human_decision_required for high/critical/irreversible tiers.",
        ],
        "use_when": [
            "User proposes an action that may have ethical or safety implications.",
            "A plan needs risk analysis before proceeding.",
            "Downstream harm must be modeled (F6 Empathy).",
        ],
        "do_not_use_when": [
            "The task is purely informational with no action proposed.",
            "The task requires final arbitration (use 888_JUDGE).",
            "The task requires execution (use arif_forge after 888 SEAL after judge seal).",
        ],
        "modes": {
            "critique": {
                "purpose": "Full risk analysis of a target action or content.",
                "required_parameters": ["target"],
                "returns": [
                    "risks_found",
                    "risk_tier",
                    "human_decision_required",
                    "empathy_score",
                ],
            },
            "simulate": {
                "purpose": "Run a what-if scenario and project risk outcomes.",
                "required_parameters": ["target"],
                "returns": ["projected_risks", "mitigations"],
            },
            "empathize": {
                "purpose": "Assess human impact load (Ω) on weakest stakeholders.",
                "required_parameters": ["target"],
                "returns": ["impact_score", "affected_stakeholders"],
            },
            "summary": {
                "purpose": "Return a condensed risk scorecard.",
                "returns": ["scorecard"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["critique", "simulate", "empathize", "summary"],
                "default": "critique",
            },
            "target": {
                "type": "string",
                "meaning": "Action, content, or scenario to critique.",
                "required_when": [
                    {"mode": "critique"},
                    {"mode": "simulate"},
                    {"mode": "empathize"},
                ],
            },
        },
        "outputs": {
            "risks_found": {"meaning": "Count of risk categories flagged."},
            "risk_tier": {"meaning": "low | medium | high | critical | irreversible"},
            "human_decision_required": {
                "meaning": "True if risk_tier is high/critical/irreversible."
            },
            "empathy_score": {"meaning": "Human impact load κᵣ (0.0–1.0, ≥0.70 preferred)."},
        },
        "risk": {"tier": "high", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": True, "recommended_session_id": True},
        "next_recommended_tools": ["arif_judge", "arif_measure"],
        "authority_boundary": {
            "may": ["analyze", "assess", "warn"],
            "may_not": ["approve", "execute", "override judge"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Assess the risks of deploying without a review",
                    "call": {
                        "tool": "arif_critique",
                        "args": {"mode": "critique", "target": "deploy without review"},
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Approve the deployment",
                    "reason_not_to_call": "Heart critiques; it does not approve. Use judge_deliberate for approval.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": True,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": True,
        },
    },
    # ── 666_GATEWAY ──────────────────────────────────────────────────────────
    "arif_gateway_connect": {
        "eureka_insight": "Federation requires mutual constitutional verification. Don’t trust external agents without a protocol handshake.",
        "stage_code": "666g",
        "stage_name": "GATEWAY",
        "purpose": [
            "Federated cross-agent bridge and A2A mesh protocol.",
            "Connects sovereign sessions to other constitutional agents.",
        ],
        "use_when": [
            "User wants to interact with another agent in the federation.",
            "A task requires multi-agent collaboration.",
            "Cross-domain reasoning requires another constitutional perspective.",
        ],
        "do_not_use_when": [
            "The task can be completed within the current session alone.",
            "No verified external agents are available.",
            "The task involves sensitive data that should not leave the session.",
        ],
        "modes": {
            "route": {
                "purpose": "Forward intent to a specific target agent.",
                "required_parameters": ["target_agent"],
                "returns": ["target", "protocol", "status"],
            },
            "discover": {
                "purpose": "List available agents in the federation mesh.",
                "returns": ["agents", "protocol"],
            },
            "handshake": {
                "purpose": "Initiate a verified constitutional handshake.",
                "required_parameters": ["target_agent"],
                "returns": ["verified", "constitution_hash_match"],
            },
            "relay": {
                "purpose": "Pass a sealed message through the gateway without mutation.",
                "required_parameters": ["target_agent"],
                "returns": ["delivered", "receipt"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["route", "discover", "handshake", "relay"],
                "default": "route",
            },
            "target_agent": {
                "type": "string",
                "meaning": "Canonical agent name (e.g., kimi, claude, gemini).",
                "required_when": [
                    {"mode": "route"},
                    {"mode": "handshake"},
                    {"mode": "relay"},
                ],
            },
        },
        "outputs": {
            "protocol": {"meaning": "A2A protocol version and capability map."},
            "status": {"meaning": "Routing or handshake result."},
        },
        "risk": {"tier": "high", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": True, "recommended_session_id": True},
        "next_recommended_tools": ["arif_think", "arif_judge"],
        "authority_boundary": {
            "may": ["route", "discover", "handshake"],
            "may_not": ["execute on behalf of", "override target agent constitution"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Ask the Kimi agent to review this plan",
                    "call": {
                        "tool": "arif_gateway_connect",
                        "args": {"mode": "route", "target_agent": "kimi"},
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Force the other agent to execute my command",
                    "reason_not_to_call": "Gateway routes and handshakes; it does not override sovereign agents.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": True,
        },
    },
    # ── 777_OPS ──────────────────────────────────────────────────────────────
    "arif_measure": {
        "eureka_insight": "Metabolism dictates survival. Compute cycles and token costs are physical limits on cognitive depth.",
        "stage_code": "777",
        "stage_name": "OPS",
        "purpose": [
            "Resource thermodynamics, health telemetry, and metabolic monitoring.",
            "Measures operational health using entropy, genius score, and load.",
        ],
        "use_when": [
            "User asks about system health, load, or resource status.",
            "Before or after a heavy operation to assess impact.",
            "Thermodynamic state needs to be checked (ΔS, G, Ω, Ψ).",
        ],
        "do_not_use_when": [
            "The task requires reasoning, evidence, or judgment.",
            "The task requires execution or system modification.",
        ],
        "modes": {
            "health": {
                "purpose": "Lightweight liveness check (CPU, mem, disk).",
                "returns": ["status", "cpu", "mem", "disk"],
            },
            "vitals": {
                "purpose": "Full thermodynamic state (G, ΔS, Ω, Ψ).",
                "returns": ["g_score", "delta_S", "omega", "psi_le"],
            },
            "cost": {
                "purpose": "Estimate computational and token cost of a planned action.",
                "required_parameters": ["estimate"],
                "returns": ["cost_estimate", "currency"],
            },
            "predict": {
                "purpose": "Project resource trajectory based on current load.",
                "required_parameters": ["estimate"],
                "returns": ["projected_load", "recommendation"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["health", "vitals", "cost", "predict"],
                "default": "health",
            },
            "estimate": {
                "type": "number",
                "meaning": "Cost estimate input for cost/predict modes.",
                "required_when": [{"mode": "cost"}, {"mode": "predict"}],
            },
        },
        "outputs": {
            "g_score": {"meaning": "Genius score (elegance metric, ≥0.80 target)."},
            "delta_S": {"meaning": "Entropy change (lower is better)."},
            "omega": {"meaning": "Human impact load (care needed)."},
            "psi_le": {"meaning": "Landauer efficiency ratio."},
        },
        "risk": {"tier": "low", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": False, "recommended_session_id": True},
        "next_recommended_tools": ["arif_observe", "arif_kernel_route"],
        "authority_boundary": {
            "may": ["measure", "estimate", "predict"],
            "may_not": ["modify", "execute", "judge"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Check if the system can handle a large reasoning job",
                    "call": {"tool": "arif_measure", "args": {"mode": "vitals"}},
                }
            ],
            "bad": [
                {
                    "user_intent": "Run the large job",
                    "reason_not_to_call": "Ops measures; it does not execute. Use forge after judge seal.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": False,
            "redaction_required": False,
        },
    },
    # ── STAGE / COMMIT — Staging Protocol (888-APEX Option A, 2026-08-03) ─────
    "arif_stage": {
        "eureka_insight": "The Agent proposes; the Sovereign disposes. Separating proposal from authorization prevents self-certifying authority (F1 AMANAH). Hash-locked staging makes the boundary cryptographic, not rhetorical.",
        "stage_code": "S1",
        "stage_name": "STAGE",
        "purpose": [
            "Stage a proposal for sovereign review. Agent PROPOSES; cannot COMMIT.",
            "Hash-locks the payload — any modification changes the hash.",
            "Auto-expires after TTL (default 24h) — F1 reversible by design.",
        ],
        "use_when": [
            "Agent has prepared a VAULT999 seal payload.",
            "The action requires F13 sovereign authorization.",
            "A seal attempt via arif_seal returns HOLD due to SCT authority gap.",
        ],
        "do_not_use_when": [
            "The agent has SOVEREIGN authority (use arif_seal directly).",
            "The payload is empty or unverified.",
        ],
        "modes": {
            "stage": {
                "purpose": "Stage a proposal. Returns stg_hash.",
                "returns": ["stg_hash", "expires_at"],
            },
            "verify": {
                "purpose": "Check staging status for a session.",
                "returns": ["staged_entries"],
            },
            "list": {
                "purpose": "List all active staged proposals.",
                "returns": ["active_proposals"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["stage", "verify", "list"],
                "default": "stage",
            },
            "payload": {"type": "string", "meaning": "Seal payload content."},
            "session_token": {
                "type": "string",
                "meaning": "Agent's SCT (verified for staging, NOT for commit).",
            },
        },
        "outputs": {
            "stg_hash": {
                "meaning": "Cryptographic hash of the staged proposal. Share with sovereign for arif_commit."
            },
            "expires_at": {"meaning": "Unix timestamp when the staging auto-expires."},
        },
        "risk": {"tier": "low", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": True, "recommended_session_id": True},
        "next_recommended_tools": ["arif_commit"],
        "authority_boundary": {
            "may": ["stage", "verify", "list"],
            "may_not": ["commit", "seal", "modify_vault"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Prepare a research synthesis for sovereign seal",
                    "call": {"tool": "arif_stage", "args": {"mode": "stage", "payload": "..."}},
                }
            ],
            "bad": [
                {
                    "user_intent": "Seal directly without sovereign review",
                    "reason_not_to_call": "arif_stage prepares; arif_commit (sovereign-only) executes the seal.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": True,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": False,
        },
    },
    "arif_commit": {
        "eureka_insight": "Only the Sovereign may seal. The kernel verifies the caller, not the agent's SCT. Authority is proven by execution context, not claimed by parameter.",
        "stage_code": "S2",
        "stage_name": "COMMIT",
        "purpose": [
            "Sovereign-only authorization gate. Commits a staged proposal to VAULT999.",
            "Verifies sovereign identity via execution context (TTY, SSH, cockpit, signed nonce).",
            "Invariant: commit caller MUST NOT be the staging agent (F1 enforcement).",
        ],
        "use_when": [
            "A staged proposal awaits sovereign authorization (has valid stg_hash).",
            "The caller has SOVEREIGN authority (proven, not claimed).",
        ],
        "do_not_use_when": [
            "The caller is the same agent that staged the proposal (F1 VIOLATION).",
            "The stg_hash is not found or has expired.",
            "ack_irreversible is not explicitly set to True.",
        ],
        "modes": {
            "commit": {
                "purpose": "Execute the sovereign seal. IRREVERSIBLE.",
                "returns": ["vault_entry_id", "chain_hash"],
            },
            "verify": {
                "purpose": "Check staging status before committing.",
                "returns": ["status", "expired"],
            },
        },
        "inputs": {
            "mode": {"type": "string", "allowed_values": ["commit", "verify"], "default": "commit"},
            "stg_hash": {"type": "string", "meaning": "Hash returned by arif_stage."},
            "ack_irreversible": {
                "type": "boolean",
                "meaning": "Explicit acknowledgment of irreversible VAULT999 append.",
            },
            "auth_type": {
                "type": "string",
                "allowed_values": ["terminal", "ssh_key", "cockpit", "signed_token"],
                "meaning": "How sovereign identity is proven.",
            },
        },
        "outputs": {
            "vault_entry_id": {"meaning": "ID of the newly created VAULT999 entry."},
            "stg_hash": {"meaning": "The committed staging hash."},
        },
        "risk": {"tier": "critical", "irreversible": True, "requires_human_ack": True},
        "state": {"requires_session_id": True, "recommended_session_id": True},
        "next_recommended_tools": ["arif_seal"],
        "authority_boundary": {
            "may": ["commit", "verify"],
            "may_not": ["stage", "unseal", "modify_staged"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Authorize a staged research synthesis for immutable seal",
                    "call": {
                        "tool": "arif_commit",
                        "args": {"mode": "commit", "stg_hash": "...", "ack_irreversible": True},
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Commit from the same agent session that staged",
                    "reason_not_to_call": "F1 AMANAH VIOLATION. Agent cannot commit its own staging.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": True,
            "writes_memory": True,
            "writes_immutable_record": True,
            "contains_sensitive_data_possible": True,
            "redaction_required": False,
        },
    },
    # ── 888_JUDGE ────────────────────────────────────────────────────────────
    "arif_judge": {
        "eureka_insight": "The Gödel Lock. The mind cannot judge the mind. Arbitration relies on deterministic constitutional physics.",
        "stage_code": "888",
        "stage_name": "JUDGE",
        "purpose": [
            "Final constitutional arbitration and verdict sealing.",
            "The apex adjudication organ evaluating against all 13 floors.",
        ],
        "use_when": [
            "User asks for a binding constitutional verdict.",
            "A proposed action needs final approval or rejection.",
            "Two candidate actions need side-by-side comparison.",
        ],
        "do_not_use_when": [
            "The task is purely informational or observational.",
            "The task requires raw evidence fetching (use arif_observe).",
            "The task requires execution (use arif_forge after judge SEAL).",
            "No candidate action or proposal has been formulated.",
        ],
        "modes": {
            "judge": {
                "purpose": "Full constitutional review of a candidate.",
                "required_parameters": ["candidate"],
                "returns": ["verdict", "floor_compliance", "epistemic_snapshot"],
            },
            "intercept": {
                "purpose": "Early gate: intercept a proposed action before full deliberation.",
                "required_parameters": ["candidate"],
                "returns": ["verdict", "intercept_reason"],
            },
            "validate": {
                "purpose": "Validate an existing verdict/receipt against floors without new arbitration.",
                "required_parameters": ["candidate"],
                "returns": ["valid", "floor_compliance"],
            },
            "hold": {
                "purpose": "Explicit HOLD emission — pause progression pending human/sovereign input.",
                "required_parameters": ["candidate"],
                "returns": ["verdict", "hold_reason"],
            },
            "escalate": {
                "purpose": "Escalate to higher authority band / F13 surface.",
                "required_parameters": ["candidate"],
                "returns": ["escalation", "required_actor"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["intercept", "judge", "validate", "hold", "escalate"],
                "default": "judge",
            },
            "candidate": {
                "type": "string",
                "meaning": "Action or proposal to adjudicate.",
                "required_when": [
                    {"mode": "judge"},
                    {"mode": "intercept"},
                    {"mode": "validate"},
                    {"mode": "hold"},
                    {"mode": "escalate"},
                ],
            },
            "constitutional_chain_id": {
                "type": "string",
                "meaning": "Immutable chain hash for audit continuity.",
            },
        },
        "outputs": {
            "verdict": {"meaning": "Binding verdict: SEAL, SABAR, VOID, or HOLD."},
            "floor_compliance": {"meaning": "Per-floor pass/fail proof."},
            "epistemic_snapshot": {"meaning": "Truth state at the moment of judgment."},
        },
        "risk": {"tier": "critical", "irreversible": False, "requires_human_ack": True},
        "state": {"requires_session_id": True, "accepts_anonymous": False},
        "next_recommended_tools": ["arif_seal", "arif_forge"],
        "authority_boundary": {
            "may": ["evaluate", "intercept", "validate", "hold", "escalate", "emit_verdict_structure"],
            "may_not": [
                "self-approve irreversible actions",
                "override human judge",
                "claim sovereign authority",
            ],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Should we approve the deployment plan?",
                    "call": {
                        "tool": "arif_judge",
                        "args": {"mode": "judge", "candidate": "deploy plan v3"},
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Deploy the plan immediately",
                    "reason_not_to_call": "Judge evaluates; it does not execute. Execution requires forge after a SEAL verdict.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": True,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": True,
        },
    },
    # ── 999_VAULT ────────────────────────────────────────────────────────────
    "arif_seal": {
        "eureka_insight": "History is immutable. A ledger without cryptographic permanence is just a suggestion.",
        "stage_code": "999",
        "stage_name": "VAULT",
        "purpose": [
            "Immutable ledger anchoring and cryptographic seal.",
            "Writes terminal verdicts and audit events to VAULT999.",
        ],
        "use_when": [
            "A terminal verdict needs to be made immutable.",
            "An audit event must be cryptographically witnessed.",
            "Session artifacts need permanent archival.",
        ],
        "do_not_use_when": [
            "The action is tentative or reversible.",
            "No prior 888_JUDGE SEAL verdict exists for irreversible writes.",
            "The user has not provided explicit human ack (F1 Amanah).",
            "Dry-run mode is sufficient.",
        ],
        "modes": {
            "seal": {
                "purpose": "Anchor a payload to the immutable ledger.",
                "required_parameters": ["payload"],
                "optional_parameters": ["ack_irreversible"],
                "returns": ["entry_id", "chain_hash", "timestamp"],
            },
            "verify": {
                "purpose": "Cryptographically verify a prior vault entry.",
                "required_parameters": ["payload"],
                "returns": ["verified", "chain_tip"],
            },
            "ledger": {
                "purpose": "Read VAULT999 ledger tip / scoped entries (replaces phantom chain/list).",
                "returns": ["entries", "chain_tip"],
            },
            "changelog": {
                "purpose": "Enumerate recent sealed changes for audit continuity.",
                "returns": ["changelog"],
            },
            "audit": {
                "purpose": "Session-scoped audit package over sealed outcomes.",
                "returns": ["audit_package"],
            },
            "session_close": {
                "purpose": "Close session continuity and emit terminal continuity receipt.",
                "required_parameters": ["session_id"],
                "returns": ["status", "session_id"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": [
                    "seal",
                    "verify",
                    "ledger",
                    "changelog",
                    "audit",
                    "session_close",
                ],
                "default": "seal",
            },
            "payload": {
                "type": "string",
                "meaning": "JSON string to anchor (seal mode).",
                "required_when": [{"mode": "seal"}],
            },
            "ack_irreversible": {
                "type": "boolean",
                "meaning": "Explicit human ack for permanent writes (F1 Amanah).",
                "default": False,
            },
            "constitutional_chain_id": {
                "type": "string",
                "meaning": "Chain hash for lineage verification.",
            },
            "judge_state_hash": {
                "type": "string",
                "meaning": "Judge verdict hash that authorized this seal.",
            },
        },
        "outputs": {
            "entry_id": {"meaning": "Unique identifier for the sealed ledger entry."},
            "chain_hash": {"meaning": "Merkle root of the chain after this entry."},
            "timestamp": {"meaning": "ISO-8601 UTC timestamp of sealing."},
        },
        "risk": {
            "tier": "critical",
            "irreversible": True,
            "requires_human_ack": True,
            "requires_judge_state_hash": True,
        },
        "state": {"requires_session_id": True, "accepts_anonymous": False},
        "next_recommended_tools": [],
        "authority_boundary": {
            "may": ["anchor", "verify", "list"],
            "may_not": ["unseal", "modify", "delete"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Permanently record the approved deployment verdict",
                    "call": {
                        "tool": "arif_seal",
                        "args": {
                            "mode": "seal",
                            "payload": '{"verdict":"SEAL","plan":"v3"}',
                            "ack_irreversible": True,
                        },
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Test what a seal would look like",
                    "reason_not_to_call": "Use dry-run mode or local testing. Vault seal is permanent and irreversible.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": True,
            "contains_sensitive_data_possible": True,
            "redaction_required": True,
        },
    },
    # ── 777_FORGE (public stage_code; metabolic alias 010 retired) ───────────
    "arif_forge": {
        "eureka_insight": "Execution is irreversible. If undo(a) does not exist, explicit human acknowledgment (ack_irreversible) is mandatory.",
        "stage_code": "777",
        "stage_name": "FORGE",
        "purpose": [
            "Metabolic execution, build orchestration, and artifact forging.",
            "Executes system modifications under constitutional supervision.",
        ],
        "use_when": [
            "User asks to build, deploy, or modify the system.",
            "A prior 888_JUDGE SEAL verdict authorizes the action.",
            "Explicit human ack has been provided for irreversible changes.",
        ],
        "do_not_use_when": [
            "No 888_JUDGE SEAL verdict exists.",
            "The user has not provided explicit human ack.",
            "The action is speculative or exploratory.",
            "Dry-run mode is sufficient.",
        ],
        "modes": {
            "engineer": {
                "purpose": "Execute a charter (build, deploy, or system change).",
                "required_parameters": ["manifest"],
                "optional_parameters": ["ack_irreversible"],
                "returns": ["status", "execution_trace", "artifact_id"],
            },
            "query": {
                "purpose": "Inspect current system state without mutation.",
                "required_parameters": ["query"],
                "returns": ["state", "metrics"],
            },
            "write": {
                "purpose": "Write or modify files under constitutional supervision.",
                "required_parameters": ["manifest"],
                "optional_parameters": ["ack_irreversible", "plan_id"],
                "returns": ["status", "execution_trace", "artifact_id"],
            },
            "generate": {
                "purpose": "Generate code or artifacts under constitutional supervision.",
                "required_parameters": ["manifest"],
                "optional_parameters": ["ack_irreversible", "plan_id"],
                "returns": ["status", "execution_trace", "artifact_id"],
            },
            "commit": {
                "purpose": "Seal a forge operation to the vault.",
                "required_parameters": ["artifact_id"],
                "returns": ["status", "vault_entry_id"],
            },
            "recall": {
                "purpose": "Recall a prior forge artifact or execution trace.",
                "required_parameters": ["artifact_id"],
                "returns": ["artifact", "trace"],
            },
            "dry_run": {
                "purpose": "Simulate a forge operation without mutation.",
                "returns": ["simulation", "would_execute_steps"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": [
                    "engineer",
                    "query",
                    "write",
                    "generate",
                    "commit",
                    "recall",
                    "dry_run",
                ],
                "default": "engineer",
            },
            "manifest": {
                "type": "string",
                "meaning": "JSON manifest describing the operation.",
                "required_when": [{"mode": "engineer"}],
            },
            "query": {
                "type": "string",
                "meaning": "State inspection query (query mode).",
                "required_when": [{"mode": "query"}],
            },
            "artifact_id": {
                "type": "string",
                "meaning": "Target artifact for commit/recall (no standalone rollback mode on public surface).",
                "required_when": [{"mode": "commit"}, {"mode": "recall"}],
            },
            "ack_irreversible": {
                "type": "boolean",
                "meaning": "Explicit human ack for permanent changes (F1 Amanah).",
                "default": False,
            },
            "constitutional_chain_id": {
                "type": "string",
                "meaning": "Chain hash for audit continuity.",
            },
            "judge_state_hash": {
                "type": "string",
                "meaning": "Authorizing 888_JUDGE verdict hash.",
            },
            "plan_id": {
                "type": "string",
                "meaning": "Approved plan_id from arif_think(mode='plan'). Required for engineer/write/generate (H2).",
                "required_when": [
                    {"mode": "engineer"},
                    {"mode": "write"},
                    {"mode": "generate"},
                ],
            },
        },
        "outputs": {
            "status": {"meaning": "Execution status: SUCCESS, FAILURE, DRY_RUN, or DEGRADED."},
            "execution_trace": {"meaning": "Step-by-step log of the operation."},
            "artifact_id": {"meaning": "Identifier for the generated or modified artifact."},
            "irreversibility_level": {"meaning": "low | medium | high | irreversible"},
        },
        "risk": {
            "tier": "critical",
            "irreversible": True,
            "requires_human_ack": True,
            "requires_judge_state_hash": True,
            "requires_vault_entry_id": False,
        },
        "state": {
            "requires_session_id": True,
            "accepts_anonymous": False,
            "carries_forward": [
                "session_id",
                "session_token",
                "artifact_id",
                "plan_id",
            ],
        },
        "next_recommended_tools": ["arif_seal"],
        "authority_boundary": {
            "may": ["execute_authorized", "query", "dry_run", "recall"],
            "may_not": ["self-approve", "bypass judge", "execute without seal"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "Deploy the approved build v3 after judge seal",
                    "call": {
                        "tool": "arif_forge",
                        "args": {
                            "mode": "engineer",
                            "manifest": '{"image":"arifos:v3","rollout":"canary"}',
                            "ack_irreversible": True,
                        },
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Deploy without review",
                    "reason_not_to_call": "Forge requires a prior 888_JUDGE SEAL verdict and explicit human ack.",
                }
            ],
        },
        "privacy_scope": {
            "reads_memory": False,
            "writes_memory": False,
            "writes_immutable_record": False,
            "contains_sensitive_data_possible": True,
            "redaction_required": True,
        },
    },
}


# Live public surface aliases — registration looks up TOOL_CHARTER[name].
# Pre-audit empty manifests on arif_route/arif_memory were caused by looking up
# absorbed legacy names that were the only charter keys.
TOOL_CHARTER["arif_kernel_route"] = TOOL_CHARTER["arif_route"]
TOOL_CHARTER["arif_memory_recall"] = TOOL_CHARTER["arif_memory"]

# Stamp shared agent contracts on every charter entry (ΔS: one source of truth).
for _name, _entry in TOOL_CHARTER.items():
    if not isinstance(_entry, dict):
        continue
    _entry.setdefault("canonical_order", list(CANONICAL_ORDER))
    _entry.setdefault("verdict_response_contract", VERDICT_RESPONSE_CONTRACT)
    _entry.setdefault("failure_modes", FAILURE_MODES_KERNEL)
    _entry.setdefault("risk_scale_map", RISK_SCALE_MAP)
    st = _entry.setdefault("state", {})
    if isinstance(st, dict):
        cf = st.setdefault("carries_forward", [])
        if isinstance(cf, list) and "session_token" not in cf:
            cf.append("session_token")
    # Repair dead next_recommended_tools pointers to live public verbs.
    nxt = _entry.get("next_recommended_tools")
    if isinstance(nxt, list):
        _remap = {
            "arif_fetch": "arif_observe",  # fetch is observe mode
            "arif_critique": "arif_judge",
            "arif_memory_recall": "arif_memory",
            "arif_kernel_route": "arif_route",
            "arif_gateway_connect": "arif_route",
            "arif_measure": "arif_observe",
            "arif_triage": "arif_init",  # triage is init mode
            "arif_compose": "arif_think",
            "arif_stage": "arif_judge",
            "arif_commit": "arif_seal",
        }
        _entry["next_recommended_tools"] = [
            _remap.get(t, t) for t in nxt if _remap.get(t, t) in set(CANONICAL_ORDER) | set(TOOL_CHARTER)
        ]


__all__ = [
    "TOOL_CHARTER",
    "CANONICAL_ORDER",
    "VERDICT_RESPONSE_CONTRACT",
    "FAILURE_MODES_KERNEL",
    "RISK_SCALE_MAP",
]
