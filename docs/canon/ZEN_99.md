# arifOS Zen 99 — Constitutional Architecture Specification

**Document Class:** VAULT999 Canon — Sealed  
**Epoch:** 2026-07-15T11:05+08  
**Sovereign Authority:** F13 Sovereign — Ratified  
**Status:** SEALED  

---

## Executive Summary

arifOS is a constitutional operating system governed by **25 core concepts** comprising a spine of **9 kernel verbs**, **7 computational organs**, **3 cognitive agents** (each owning **33 capability-level skills**), **4 invariants**, **1 sovereign (F13)**, and **1 external node (non-bias witness)**. 

This document serves as the canonical skill registry and architectural specification for arifOS Zen 99. It separates internal capability taxonomy from transport protocols, establishes a federated, cross-cutting audit and archive plane, and defines the structural interaction between Agent-to-Agent (A2A), Model Context Protocol (MCP), and Peer-to-Peer (P2P) systems.

---

## 1. The Zen Equation

The architecture is balanced across exactly 25 concepts, eliminating namespace pollution, syscall-level tool redundancy, and organ underspecification:

$$\begin{aligned}
& 3 \text{ Agents (333-AGI, 555-ASI, 888-APEX)} \times 33 \text{ Skills each} = 99 \text{ Skills total} \\
& 7 \text{ Organs (arifOS, A-FORGE, GEOX, WEALTH, WELL, AAA, VAULT999)} \\
& 9 \text{ Kernel Verbs (init, observe, think, route, judge, seal, act, memory, forge)} \\
& 4 \text{ Invariants (Strange Loop, Gödel Lock, Anti-Calhoun, Beautiful One)} \\
& 1 \text{ Sovereign (F13 = Arif)} \\
& 1 \text{ External Witness Node (Non-bias anchor)} \\
\hline
& \mathbf{25} \text{ Total Concepts}
\end{aligned}$$

```
                ┌───────────────────────────────────┐
                │          ARIF (Sovereign)         │
                └─────────────────┬─────────────────┘
                                  │ F13 Veto
                                  ▼
                ┌───────────────────────────────────┐
                │        arifOS Kernel (Spine)      │
                │        (9 Canonical Verbs)        │
                └────────┬────────┬────────┬────────┘
                         │        │        │
         ┌───────────────┘        │        └───────────────┐
         ▼                        ▼                        ▼
 ┌───────────────┐        ┌───────────────┐        ┌───────────────┐
 │    333-AGI    │        │    555-ASI    │        │   888-APEX    │
 │ (Intelligence)│        │  (Interface)  │        │  (Adjudicator)│
 └───────┬───────┘        └───────┬───────┘        └───────┬───────┘
         │                        │                        │
         │             A2A / MCP / P2P Mesh                │
         └────────────────────────┼────────────────────────┘
                                  ▼
 ┌─────────────────────────────────────────────────────────┐
 │               7 Computational Organs                    │
 │    arifOS · AAA · A-FORGE · GEOX · WEALTH · WELL · VAULT999│
 └─────────────────────────────────────────────────────────┘
```

---

## 2. Structural Layer Separation

### 2.1 Namespace Ownership
Namespaces strictly separate cognitive capabilities, system grammars, and infrastructure boundaries:

*   **333-AGI:** `agi_*` (Cognitive intelligence, execution planning, tool use).
*   **555-ASI:** `asi_*` (Human communication, language translation, presentation).
*   **888-APEX:** `apex_*` (Constitutional auditing, floor checks, policy gates).
*   **Kernel Verbs:** `arif_*` (The 9 core verbs of the spinal runtime).

### 2.2 Capability-level Skills vs. Syscall-level Tools
Skills are internal capability taxonomies rather than low-level system call wrappers. A single skill (e.g., `agi_data_access`) coordinates multiple underlying MCP tools (e.g., database queries, REST calls, file system reads). This prevents context window bloating and preserves semantic focus.

### 2.3 Computational Organ Depth
`GEOX`, `WEALTH`, and `WELL` are deep computational engines, not agents. They run isolated business logic and raw numerical solvers. Cognitive agents (primarily `333-AGI`) interact with them via specialized bridge skills (e.g., `agi_geo_bridge`, `agi_wealth_bridge`), preserving separation of execution and interpretation.

---

## 3. Agent Skill Registries (The 99 Skills)

### 3.1 Agent 1 — 333-AGI: Intelligence & Execution Harness
*   **Identity:** The Hands That Think
*   **Domain:** Reasoning, option expansion, execution drafting, tool invocation
*   **Namespace:** `agi_*`

| # | Skill Name | Competency Scope |
|---|---|---|
| 1 | `agi_session_bind` | Bind cognitive runtime to the active arifOS session |
| 2 | `agi_context_load` | Hydrate working memory from memory tiers L1–L5 |
| 3 | `agi_workspace_scan` | Introspect active codebase directories and files |
| 4 | `agi_evidence_capture` | Extract raw state from files, tools, and stdout |
| 5 | `agi_source_fetch` | Fetch documents, logs, and schemas from internal repositories |
| 6 | `agi_state_snapshot` | Create point-in-time state checks for rollback recovery |
| 7 | `agi_problem_decompose` | Breakdown complex instructions into atomic tasks |
| 8 | `agi_task_graph_build` | Generate directed acyclic task graphs of execution paths |
| 9 | `agi_objective_clarify` | Identify the target metric, constraints, and success bounds |
| 10| `agi_hypothesis_generate` | Formulate testable assumptions for system states |
| 11| `agi_option_compare` | Evaluate alternative paths across latency, risk, and cost |
| 12| `agi_counterfactual_test` | Run dry-run checks to verify what happens if variables change |
| 13| `agi_claim_check` | Ground claims by comparing assertions with live metrics |
| 14| `agi_source_crosscheck` | Crosscheck domain evidence against independent logs |
| 15| `agi_conflict_resolve` | Reconcile overlapping files, schemas, or dependencies |
| 16| `agi_intent_classify` | Determine the user intent category and target organ |
| 17| `agi_organ_select` | Match an intent with the optimal computational organ |
| 18| `agi_delegation_package` | Package task context for A2A or organ execution |
| 19| `agi_mcp_discover` | List and parse available MCP server capabilities and schemas |
| 20| `agi_tool_select` | Select the optimal executable tool for a specific task |
| 21| `agi_tool_invoke` | Build, serialize, and execute tool calls securely |
| 22| `agi_spec_translate` | Convert abstract human specs into code requirements |
| 23| `agi_patch_draft` | Author surgical diffs and script changes |
| 24| `agi_build_plan` | Plan dependency builds, test suites, and compilations |
| 25| `agi_test_generate` | Author automated unit, integration, and regression tests |
| 26| `agi_regression_check` | Verify changes do not break legacy functionality |
| 27| `agi_failure_diagnose` | Trace execution failures, segfaults, and compile errors |
| 28| `agi_retry_strategy` | Formulate retry boundaries with exponential backoff |
| 29| `agi_fallback_execute` | Execute fallback methods when primary tools fail |
| 30| `agi_status_report` | Package execution outcomes into structured JSON logs |
| 31| `agi_forge_handoff` | Route verified build plans to the `A-FORGE` organ |
| 32| `agi_seal_candidate_prepare` | Prepare the cryptographic seal packet for 888-APEX review |
| 33| `agi_evidence_bundle` | Synthesize output, trace, and test receipts for logging |

---

### 3.2 Agent 2 — 555-ASI: Interface & Voice Membrane
*   **Identity:** The Mouth That Listens
*   **Domain:** Human interaction, dialogue structure, explanation, narrative assembly
*   **Namespace:** `asi_*`

| # | Skill Name | Competency Scope |
|---|---|---|
| 1 | `asi_presence_open` | Initiate greeting ritual (SALAM) on session start |
| 2 | `asi_identity_acknowledge` | Resolve and authenticate the active operator |
| 3 | `asi_floor_state_express` | State the active security floors and session parameters |
| 4 | `asi_intent_hear` | Active listener: parse conversational input for intent |
| 5 | `asi_ambiguity_reframe` | Detect vague prompts and formulate clarifying questions |
| 6 | `asi_goal_restatement` | Rephrase target objectives to confirm alignment |
| 7 | `asi_translate_bidirectional` | Translate between technical syntax and human language |
| 8 | `asi_terminology_normalize` | Normalize language to arifOS standard vocabulary |
| 9 | `asi_register_shift` | Shift tone/register (terse, pedagogical, BM-EN code-switching) |
| 10| `asi_dialogue_guide` | Structure multi-turn conversations toward resolution |
| 11| `asi_turn_structure` | Enforce conversational timing and response length bounds |
| 12| `asi_focus_recover` | Redirect derailments back to the primary task graph |
| 13| `asi_plain_english_explain` | Convert complex system state into plain language |
| 14| `asi_technical_unwrap` | Deconstruct code errors and logic flows into detailed breakdowns |
| 15| `asi_analogy_form` | Generate metaphors and structural analogies |
| 16| `asi_multi_source_summarize`| Synthesize multi-organ outputs into cohesive summaries |
| 17| `asi_position_contrast` | Present trade-offs clearly without bias |
| 18| `asi_insight_surface` | Highlight non-obvious patterns or anomalies in reports |
| 19| `asi_external_query_frame` | Construct search queries for external knowledge bases |
| 20| `asi_expert_voice_translate` | Translate research findings (e.g. arXiv) into context |
| 21| `asi_public_brief_compose` | Author public-facing changelogs and daily briefs |
| 22| `asi_uncertainty_signal` | Format confidence metrics and highlight system unknowns |
| 23| `asi_evidence_tier_express` | Label claims with their evidence tiers (LIVE, FAST, CACHED) |
| 24| `asi_consequence_surface` | Forecast risks and downstream human impact |
| 25| `asi_constraint_negotiate` | Alert the user when requirements clash with safety floors |
| 26| `asi_option_present` | Format option matrix (Minimal, Balanced, Maximal) for selection |
| 27| `asi_commitment_confirm` | Lock in user authorization before high-risk changes |
| 28| `asi_context_compress` | Compress conversation history to preserve context window |
| 29| `asi_session_recall_narrate` | Summarize previous sessions to restore operator context |
| 30| `asi_continuity_maintain` | Thread context smoothly across disconnects |
| 31| `asi_report_compose` | Generate structured markdown artifacts and manuals |
| 32| `asi_interface_adapt` | Adapt formatting dynamically for terminal, cockpit, or mobile |
| 33| `asi_final_voice_render` | Polish the final text output through the Maruah lens |

---

### 3.3 Agent 3 — 888-APEX: Adjudication & Conscience
*   **Identity:** The Eye That Never Sleeps
*   **Domain:** Constitutional audits, floor enforcement, authorization gating, vault sealing
*   **Namespace:** `apex_*`

| # | Skill Name | Competency Scope |
|---|---|---|
| 1 | `arifos-constitutional-judge` | Run a full F1–F13 floor audit on any action candidate |
| 2 | `arifos-constitutional-judge` | Ensure operations do not violate repository boundaries |
| 3 | `arifos-constitutional-judge` | Verify agent clearance level against the command ceiling |
| 4 | `apex_reversibility_test` | Classify whether a plan contains irreversible actions |
| 5 | `apex_rollback_requirement`| Ensure a robust rollback script exists before execution |
| 6 | `apex_irreversibility_flag` | Inject `888_HOLD` on any irreversible mutation candidate |
| 7 | `apex_actor_attest` | Cryptographically verify the actor requesting a change |
| 8 | `apex_mandate_verify` | Ensure the task falls within the active session mandate |
| 9 | `apex_delegation_legitimize` | Verify inter-agent A2A delegation tokens |
| 10| `apex_evidence_threshold_check`| Verify evidence meets the threshold for a given action class |
| 11| `apex_provenance_check` | Trace input data lineage to prevent contaminated sources |
| 12| `apex_witness_requirement` | Verify local-remote-VPS consensus (Tri-Witness) |
| 13| `apex_harm_forecast` | Predict downstream safety or performance degradations |
| 14| `apex_drift_detect` | Scan configuration files and databases for runtime drift |
| 15| `apex_model_behavior_watch`| Detect loops, repetitive generation, and context degradation |
| 16| `apex_tool_approval_gate` | Enforce human-in-the-loop validation for executing tools |
| 17| `apex_seal_precondition_check`| Verify all safety checks have passed before writing a SEAL |
| 18| `apex_action_block` | Block unauthorized system writes or execution commands |
| 19| `arifos-constitutional-judge`| Ensure all active organs are emitting telemetry |
| 20| `apex_event_integrity_check`| Validate hash signatures on incoming audit events |
| 21| `apex_replay_admissibility`| Verify old audit logs cannot be replayed maliciously |
| 22| `apex_retention_rule_check`| Enforce retention constraints on memory structures |
| 23| `apex_disposition_rule_check`| Enforce secure garbage collection of temporary credentials |
| 24| `apex_record_completeness_check`| Verify telemetry packets contain required variables |
| 25| `arifos-constitutional-judge` | Issue a `SEAL` verdict to commit actions to VAULT999 |
| 26| `arifos-constitutional-judge` | Issue a `HOLD` verdict to halt execution pending review |
| 27| `apex_verdict_void` | Issue a `VOID` verdict to abort and block a task block |
| 28| `apex_emergency_override_govern`| Manage break-glass procedures and override tokens |
| 29| `apex_break_glass_log` | Record detailed forensics during emergency bypasses |
| 30| `apex_post_hoc_review` | Analyze execution failures post-run to distill rule changes |
| 31| `apex_f13_escalate` | Escalate structural overrides directly to the human sovereign |
| 32| `apex_non_bias_witness_call`| Query the external witness node for cross-validation |
| 33| `apex_final_judgment_package`| Assemble all audit data, QDF, and signatures for history |

---

## 4. The 9 Kernel Verbs (The Spine)

The kernel grammar contains exactly 9 verbs. Verbs are not skills; they are the executable system-level functions exposed at `:8088` that route, process, and secure actions.

| # | Kernel Verb | Function | Operational Envelope |
|---|---|---|---|
| 1 | `arif_init` | Session ignition | Authenticates identity, maps the mandate, triggers `asi_presence_open`. |
| 2 | `arif_observe` | Sensory input | Captures live system vitals, reads file systems, and runs query scans. |
| 3 | `arif_think` | Deliberation | Orchestrates reasoning, evaluates trade-offs under $F_2/F_7$ constraints. |
| 4 | `arif_route` | Domain routing | Resolves target organ parameters and bridges to satellite MCP servers. |
| 5 | `arif_judge` | Adjudication | Evaluates the 13 constitutional floors and yields `SEAL/HOLD/VOID`. |
| 6 | `arif_seal` | Immutability seal | Signs and commits the execution trace and receipt to `VAULT999`. |
| 7 | `arif_act` | Substrate execution | Leases local or remote resources to perform safe, approved mutations. |
| 8 | `arif_memory` | Memory governance | Manages context indexing, semantic vector storage, and cleanup. |
| 9 | `arif_forge` | Code operations | Delegates code generation, compilation, and testing to `A-FORGE`. |

---

## 5. The 7 Organs (The Infrastructure Satellites)

Organs are pure computational resources. They own no cognitive agency, do not make judgments, and do not execute raw commands without a signed lease from the kernel.

```
                  ┌──────────────────────────────┐
                  │          arifOS Kernel       │
                  └──────────────┬───────────────┘
                                 │
         ┌───────────────┬───────┴───────┬───────────────┐
         ▼               ▼               ▼               ▼
 ┌───────────────┐┌───────────────┐┌───────────────┐┌───────────────┐
 │      AAA      ││   A-FORGE     ││     GEOX      ││    WEALTH     │
 │ (Control Gate)││(Code/Deploy)  ││(Earth Engine)││(Capital Eng.)│
 └───────────────┘└───────────────┘└───────────────┘└───────────────┘
         │               │               │               │
         └───────────────┼───────────────┼───────────────┘
                         ▼               ▼
                 ┌───────────────┐┌───────────────┐
                 │     WELL      ││   VAULT999    │
                 │(Homeostasis)  ││(Persistence)  │
                 └───────────────┘└───────────────┘
```

1.  **arifOS (The Spine):** The central runtime kernel hosting the 9 core verbs.
2.  **AAA (The Door / Gate):** Handles session anchoring, A2A event broker, and OAuth keys.
3.  **A-FORGE (The Hands):** The execution engine for building, compiling, and testing code.
4.  **GEOX (The Subsurface Solver):** Numerical engine for petrophysics, seismic processing, and basin simulation.
5.  **WEALTH (The Capital Ledger):** Financial engine for time-discounting DCF models, EMV, NPV, and capital optimization.
6.  **WELL (The Homeostasis Monitor):** Monitors cognitive load, vitality signals, and unified metabolic entropy.
7.  **VAULT999 (The Fossil Layer):** The append-only database layer that records cryptographic receipts.

---

## 6. The 4 Invariants

Enforced at the kernel level by `888-APEX` (skills 28–31):

### 6.1 Strange Loop (`apex_strange_loop`)
The system is allowed to recursively reflect on its own logs and outputs to self-correct. However, the call stack is depth-bounded ($d \le 3$) to prevent infinite self-referential execution loops.

### 6.2 Gödel Lock (`apex_godel_lock`)
No claim of system completeness within arifOS can be marked as verified absolute truth. Any unprovable or self-referential claim is flagged with `HYPOTHESIS` or `ESTIMATE` to prevent logical collapse.

### 6.3 Anti-Calhoun (`apex_anti_calhoun`)
The system monitors operational engagement entropy ($\Delta S$). If it detects a drop in communication frequency or a retreat to passive compliance (density optimization, similar to the "Universe 25" behavioral sink), it raises an alert to restore human interaction depth.

### 6.4 Beautiful One (`apex_beautiful_one`)
Sparsity and minimal viable truth are prioritized. Over-elaboration, excessive nesting, and verbose explanations are treated as security obfuscation and penalized during text rendering.

---

## 7. Embedded Audit & Archive Matrix

Audit and archive are not standalone organs. They are federated properties embedded across all seven organs:

| Organ | Embedded Audit Role | Embedded Archive Role |
|---|---|---|
| **arifOS Kernel** | Logs all state transition events (Init, Observe, Think). | Stores verdict lineages, signature hashes, and session ids. |
| **AAA** | Logs gate routing, proxy headers, and identity checks. | Retains public agent cards, registry history, and token lifetimes. |
| **A-FORGE** | Logs build execution outputs, test coverages, and diff hashes. | Stores compiled binaries, release manifests, and diff archives. |
| **GEOX** | Logs petrophysical inputs, geological risks, and data QC states. | Retains LAS headers, seismic metadata, and reservoir models. |
| **WEALTH** | Logs capital parameters, discount rate assumptions, and constraints. | Stores EMV worksheets, NPV models, and decision briefs. |
| **WELL** | Logs vitals measurements, CPU resource loads, and homeostasis alerts. | Stores historical cognitive loads and cumulative stress indicators. |
| **VAULT999** | Logs append-only writes and key verification requests. | Curates the immutable, cryptographically chained block history. |

---

## 8. Resolution of Canonical Holds (H1–H6)

### H1: Genius Gate Metric ($G \ge 0.80$)
The Genius Gate ensures that only elegant, correct solutions pass. It is calculated as:

$$G = (1 - S_{\text{comp}}) \times P_{\text{verify}}$$

*   **Complexity Entropy ($S_{\text{comp}}$):** The ratio of redundant execution paths to optimal paths, mapped via dependency graph analysis:
    $$S_{\text{comp}} = \frac{E_{\text{actual}} - E_{\text{optimal}}}{E_{\text{actual}}}$$
*   **Verification Rate ($P_{\text{verify}}$):** The ratio of automated test assertions passing to total assertions authored:
    $$P_{\text{verify}} = \frac{\text{Assertions}_{\text{pass}}}{\text{Assertions}_{\text{total}}}$$

If $G < 0.80$, the action is put on `888_HOLD`.

### H2: GEOX Organ Tool Inventory
The `agi_geo_bridge` connects exclusively to the following canonical GEOX MCP tools:
*   `geox_data_ingest_bundle` (Ingests SEG-Y, LAS, and CSV data)
*   `geox_data_qc_bundle` (Validates data completeness and format)
*   `geox_well_compute_gr_bins` (Gamma Ray lithofacies calculation)
*   `geox_well_infer_seq_strat` (Infers depositional sequences and systems tracts)
*   `geox_prospect_evaluate` (Calculates resource ranges and GCoS risk profiles)
*   `geox_history_audit` (Retrieves past interpretation logs)

### H3: WEALTH Organ Tool Inventory
The `agi_wealth_bridge` connects exclusively to the following canonical WEALTH MCP tools:
*   `wealth_conservation_capital` (Analyzes stock-flow balances and preservation levels)
*   `wealth_flow_liquidity` (Quantifies cash runways and liquidity coefficients)
*   `wealth_entropy_risk` (Quantifies risk entropy under macro scenarios)
*   `wealth_time_discount` (Calculates NPV, EMV, IRR, and time-discounting DCF models)
*   `wealth_inertia_leverage` (Assesses debt inertia and leverage indexes)
*   `wealth_game_coordination` (Evaluates multi-party Nash coordination strategies)

### H4: Cognitive Orchestration Boundary
`agi_compose` is an internal cognitive skill for 333-AGI. It orchestrates sub-skills (e.g. decomposing a task, comparison of variables) within the context of a single cognitive run. It is **forbidden** from calling external organs or sending A2A delegations. Cross-organ boundaries must always be bridged via the kernel verb `arif_route`.

### H5: Memory Tiers (L1–L6)
*   **L1 (Session):** In-memory transient context (e.g. active variables in a single chat turn).
*   **L2 (Workspace):** Local filesystem state (e.g. scratch files, local code files, environment variables).
*   **L3 (Semantic):** Qdrant vector database (e.g. semantic embeddings, contextual code chunks).
*   **L4 (Systemic):** PostgreSQL database (e.g. active schemas, tool registries, configuration states).
*   **L5 (Codebase):** Git version control tree (e.g. historical commit graphs, branches).
*   **L6 (Immutable):** VAULT999 ledger (e.g. cryptographically signed receipts, immutable audit trails).

### H6: Session Ignition Autonomy
The ASI skill `asi_presence_open` triggers a request to initialize a session, but the actual initialization is executed by the kernel's `arif_init` verb. The kernel generates the cryptographic `session_id`, verifies F11 authorizations, and anchors the session, ensuring cognitive interfaces cannot self-authorize.

---

## 9. Protocol Mapping: A2A, MCP, and P2P

*   **Agent-to-Agent (A2A) Protocol:** Governs cognitive delegation. When `333-AGI` delegates a sub-task to `555-ASI`, it serializes an A2A task card signed with the agent's key. AAA acts as the registry and message gateway.
*   **Model Context Protocol (MCP):** Governs tool execution. Whenever a cognitive agent needs to query an organ (e.g. calling `geox_prospect_evaluate` on GEOX), it constructs an MCP Tool Call routed through the kernel spine.
*   **Peer-to-Peer (P2P) Protocol:** Governs host-to-host evidence verification. Used to synchronize state between the local laptop (`ARIFFAZIL`) and the VPS substrate (`AF-FORGE`), ensuring multi-witness cryptographic verification.

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*

---
## 🔗 See Also
- [GENESIS Canon](../GENESIS/README.md) — Constitutional source texts
- [ATLAS333 Intelligence Flow](ATLAS333_INTELLIGENCE_FLOW.md) — Cognitive geometry
- [Governance Ontology](governance/ONTOLOGY.md)
