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

CANONICAL_ORDER: list[str] = [
    "arif_init",
    "arif_observe",
    "arif_fetch",
    "arif_think",
    "arif_kernel_route",
    "arif_compose",
    "arif_memory_recall",
    "arif_critique",
    "arif_gateway_connect",
    "arif_measure",
    "arif_judge",
    "arif_seal",
    "arif_forge",
]


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
                "optional_parameters": ["ack_irreversible", "epoch_id"],
                "returns": [
                    "session_id",
                    "constitution_hash",
                    "invariants_hash",
                    "allowed_next_tools",
                ],
            },
            "resume": {
                "purpose": "Reattach to an existing session by session_id.",
                "required_parameters": ["session_id"],
                "optional_parameters": [],
                "returns": ["session_id", "status", "allowed_next_tools"],
            },
            "validate": {
                "purpose": "Check session health and constitutional alignment.",
                "required_parameters": ["session_id"],
                "optional_parameters": [],
                "returns": ["session_id", "status", "floors_ok", "floors_fail"],
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
        },
        "inputs": {
            "mode": {
                "type": "string",
                "meaning": "Operation mode for the session lifecycle.",
                "allowed_values": [
                    "init",
                    "resume",
                    "validate",
                    "epoch_open",
                    "epoch_seal",
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
            "constitution_hash": {
                "meaning": "SHA-256 fingerprint of the active constitutional rulebase.",
                "trust_role": "integrity_anchor",
            },
            "allowed_next_tools": {
                "meaning": "Suggested safe continuation path from this session.",
            },
        },
        "risk": {
            "tier": "critical",
            "irreversible": False,
            "requires_human_ack": False,
            "requires_judge_state_hash": False,
            "requires_vault_entry_id": False,
        },
        "state": {
            "requires_session_id": False,
            "accepts_anonymous": False,
            "carries_forward": ["session_id", "constitution_hash"],
        },
        "next_recommended_tools": [
            "arif_observe",
            "arif_fetch",
            "arif_think",
        ],
        "authority_boundary": {
            "may": ["bind", "validate", "resume"],
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
                        "args": {"mode": "init", "actor_id": "ChatGPT"},
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
            "ingest": {
                "purpose": "Fetch and parse a specific URL.",
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
                "required_when": [{"mode": "search"}],
            },
            "url": {
                "type": "string",
                "meaning": "Target URL for ingest mode.",
                "required_when": [{"mode": "ingest"}],
            },
            "layers": {
                "type": "list[string]",
                "meaning": "Layer identifiers for atlas mode.",
                "required_when": [{"mode": "atlas"}],
            },
        },
        "outputs": {
            "results": {"meaning": "Observational data matching the query."},
            "omega_0": {"meaning": "Uncertainty band (0.03–0.05 = humble)."},
            "delta_S": {"meaning": "Entropy change from this observation."},
        },
        "risk": {"tier": "low", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": False, "recommended_session_id": True},
        "next_recommended_tools": ["arif_fetch", "arif_think"],
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
            "The task requires execution or system modification (use 010_FORGE).",
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
            "critique": {
                "purpose": "Adversarial stress-test of a reasoning chain.",
                "required_parameters": ["query"],
                "returns": ["gaps", "biases", "counterarguments"],
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
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": [
                    "reason",
                    "reflect",
                    "verify",
                    "critique",
                    "axioms",
                    "plan",
                    "plan_review",
                    "plan_approve",
                ],
                "default": "reason",
            },
            "query": {
                "type": "string",
                "meaning": "The claim, question, or plan to reason over.",
                "required_when": [
                    {"mode": "reason"},
                    {"mode": "verify"},
                    {"mode": "critique"},
                    {"mode": "plan"},
                ],
            },
            "plan_id": {
                "type": "string",
                "meaning": "Plan identifier (for plan_review / plan_approve).",
                "required_when": [{"mode": "plan_review"}, {"mode": "plan_approve"}],
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
        },
        "next_recommended_tools": ["arif_critique", "arif_judge"],
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
    # ── 444_KERNEL ───────────────────────────────────────────────────────────
    "arif_kernel_route": {
        "eureka_insight": "Orchestration is the physics of routing. No AGI lane task may unilaterally cross into the APEX lane.",
        "stage_code": "444",
        "stage_name": "KERNEL",
        "purpose": [
            "Central orchestration, intent routing, and stage dispatch.",
            "Traffic controller for the 13-tool constitutional surface.",
        ],
        "use_when": [
            "User intent is ambiguous and needs routing to the correct tool.",
            "A session stage needs to be queried or advanced.",
            "The cognitive lane (AGI/ASI/APEX) needs to be switched.",
        ],
        "do_not_use_when": [
            "The target tool is already known and can be called directly.",
            "The task requires reasoning, evidence, or judgment rather than routing.",
        ],
        "modes": {
            "route": {
                "purpose": "Resolve intent to a canonical tool + stage path.",
                "required_parameters": ["target"],
                "returns": ["target", "path", "hops"],
            },
            "status": {
                "purpose": "Return kernel health and routing table state.",
                "returns": ["status", "routing_table"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["route", "status"],
                "default": "route",
            },
            "target": {
                "type": "string",
                "meaning": "Target tool, endpoint, or lane name.",
                "required_when": [{"mode": "route"}],
            },
            "task": {
                "type": "string",
                "meaning": "Task description for routing resolution.",
            },
            "stage": {
                "type": "string",
                "meaning": "Explicit stage override (000–999).",
            },
        },
        "outputs": {
            "path": {"meaning": "Suggested tool sequence from current state to target."},
            "hops": {"meaning": "Number of stage transitions required."},
            "allowed_tools": {"meaning": "Tools permitted in the current session state."},
        },
        "risk": {"tier": "low", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": True, "recommended_session_id": True},
        "next_recommended_tools": [
            "arif_observe",
            "arif_think",
            "arif_measure",
        ],
        "authority_boundary": {
            "may": ["route", "query"],
            "may_not": ["execute", "judge", "seal"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "What tool should I use next?",
                    "call": {
                        "tool": "arif_kernel_route",
                        "args": {"mode": "route", "target": "arif_judge"},
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Execute the deployment",
                    "reason_not_to_call": "Kernel routes; it does not execute.",
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
    # ── 555_MEMORY ───────────────────────────────────────────────────────────
    "arif_memory_recall": {
        "eureka_insight": "Memory is an associative projection. Recalled facts must inherit their original epistemic uncertainty.",
        "stage_code": "555",
        "stage_name": "MEMORY",
        "purpose": [
            "Associative retrieval from VAULT999 and vector memory.",
            "Recalls prior session artifacts, reasoning traces, and sealed events.",
        ],
        "use_when": [
            "User asks about prior session history or decisions.",
            "A reasoning step needs context from past interactions.",
            "Sealed events or audit records must be retrieved.",
        ],
        "do_not_use_when": [
            "The user asks about topics never discussed in prior sessions.",
            "The task requires creating new memory without retrieval.",
        ],
        "modes": {
            "recall": {
                "purpose": "Semantic search across all stored memories.",
                "required_parameters": ["query"],
                "returns": ["memories", "confidence"],
            },
            "store": {
                "purpose": "Ingest a new memory entry (requires ack_irreversible).",
                "required_parameters": ["query"],
                "returns": ["memory_id", "status"],
            },
            "get": {
                "purpose": "Exact retrieval by memory_id.",
                "required_parameters": ["memory_id"],
                "returns": ["memory"],
            },
            "list": {
                "purpose": "List memories scoped to the current session.",
                "returns": ["memories"],
            },
            "prune": {
                "purpose": "Remove expired memories (F1 Amanah — reversible only).",
                "returns": ["pruned"],
            },
            "searah": {
                "purpose": "SEARAH Investigation Level 2 Agentic RAG — multi-hop retrieval, constitutional validation.",
                "required_parameters": ["query"],
                "returns": ["answer", "confidence", "sub_question_count"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": [
                    "recall",
                    "store",
                    "get",
                    "list",
                    "prune",
                    "search",
                    "context",
                    "dry_run",
                    "searah",
                ],
                "default": "recall",
            },
            "query": {
                "type": "string",
                "meaning": "Semantic search query (recall/search modes) OR text content (store mode).",
                "required_when": [{"mode": "recall"}, {"mode": "search"}],
            },
            "content": {
                "type": "string",
                "meaning": "Convenience alias for store mode — maps to metadata['text']. Use this OR query.",
                "required_when": [{"mode": "store", "missing": "query"}],
            },
            "project_id": {
                "type": "string",
                "meaning": "Project namespace for memory isolation.",
                "default": "default",
            },
            "area": {
                "type": "string",
                "meaning": "Memory area: 'main', 'working', 'sacred', 'canon'.",
                "default": "working",
            },
            "memory_id": {
                "type": "string",
                "meaning": "Exact UUID for get/delete.",
                "required_when": [{"mode": "get"}, {"mode": "prune"}],
            },
            "session_id": {
                "type": "string",
                "meaning": "Session scope for list operations.",
            },
        },
        "outputs": {
            "memories": {"meaning": "Retrieved memory entries with source tags."},
            "confidence": {"meaning": "Retrieval confidence score."},
            "memory_id": {"meaning": "UUID of stored memory (store mode)."},
            "stored": {"meaning": "Boolean success flag (store mode)."},
        },
        "risk": {"tier": "medium", "irreversible": False, "requires_human_ack": False},
        "state": {"requires_session_id": True, "accepts_anonymous": False},
        "next_recommended_tools": ["arif_think", "arif_critique"],
        "authority_boundary": {
            "may": ["recall", "list"],
            "may_not": ["unauthorized deletion", "seal"],
        },
        "examples": {
            "good": [
                {
                    "user_intent": "What did we decide about the deployment strategy?",
                    "call": {
                        "tool": "arif_memory_recall",
                        "args": {"mode": "recall", "query": "deployment strategy"},
                    },
                }
            ],
            "bad": [
                {
                    "user_intent": "Delete all past memories",
                    "reason_not_to_call": "Pruning requires explicit ack and session scope. Use prune mode with care.",
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
            "The task requires execution (use 010_FORGE after judge seal).",
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
            "The task requires raw evidence fetching (use 222_FETCH).",
            "The task requires execution (use 010_FORGE after judge seal).",
            "No candidate action or proposal has been formulated.",
        ],
        "modes": {
            "judge": {
                "purpose": "Full constitutional review of a candidate.",
                "required_parameters": ["candidate"],
                "returns": ["verdict", "floor_compliance", "epistemic_snapshot"],
            },
            "compare": {
                "purpose": "Side-by-side comparison of two candidate actions.",
                "required_parameters": ["candidate"],
                "returns": ["comparison", "recommendation"],
            },
            "history": {
                "purpose": "Retrieve prior verdicts from the constitutional chain.",
                "returns": ["verdicts"],
            },
            "explain": {
                "purpose": "Generate a human-readable rationale for a verdict.",
                "required_parameters": ["candidate"],
                "returns": ["rationale"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["judge", "compare", "history", "explain"],
                "default": "judge",
            },
            "candidate": {
                "type": "string",
                "meaning": "Action or proposal to adjudicate.",
                "required_when": [
                    {"mode": "judge"},
                    {"mode": "compare"},
                    {"mode": "explain"},
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
            "may": ["evaluate", "compare", "explain", "emit_verdict_structure"],
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
                "required_parameters": ["vault_entry_id"],
                "returns": ["verified", "chain_tip"],
            },
            "chain": {
                "purpose": "Retrieve the Merkle chain tip and lineage.",
                "returns": ["chain_tip", "lineage"],
            },
            "list": {
                "purpose": "Enumerate entries scoped to the current session.",
                "returns": ["entries"],
            },
        },
        "inputs": {
            "mode": {
                "type": "string",
                "allowed_values": ["seal", "verify", "chain", "list"],
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
    # ── 010_FORGE ────────────────────────────────────────────────────────────
    "arif_forge": {
        "eureka_insight": "Execution is irreversible. If undo(a) does not exist, explicit human acknowledgment (ack_irreversible) is mandatory.",
        "stage_code": "010",
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
                "meaning": "Target artifact for rollback/status.",
                "required_when": [{"mode": "rollback"}],
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
        "state": {"requires_session_id": True, "accepts_anonymous": False},
        "next_recommended_tools": ["arif_seal"],
        "authority_boundary": {
            "may": ["execute_authorized", "query", "rollback"],
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


__all__ = ["TOOL_CHARTER", "CANONICAL_ORDER"]
