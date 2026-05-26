# PROMPT_INVENTORY.md — arifOS MCP Canonical Prompts
**Generated:** 2026-05-25
**Phase:** PHASE 1 — Prompt Inventory
**Target:** 9 canonical prompts (RAF + TEOF + A-PROMPT + Prompt Master + Commitment + 4 inter-agent)

---

## Prompt Definition

A canonical prompt is:
- Versioned and sealed
- Stable (not modified per-query)
- Used by agents before tool execution
- Governed by constitutional floors

---

## TARGET: 9 Canonical Prompts

### P-1: RAF (Routing Assignment Form)

**Purpose:** Determine which organ should handle a user query
**When used:** Before arif_kernel_route
**Inputs:** user query, session context
**Outputs:** target organ, confidence, reasoning
**Floors:** F01, F04
**Status:** PLANNED

### P-2: TEOF (Three-Organ Evidence Packet)

**Purpose:** Structure cross-organ evidence gathering
**When used:** Before arif_evidence_fetch + organ calls
**Inputs:** question, required organs (GEOX/WEALTH/WELL)
**Outputs:** {geox: {}, wealth: {}, well: {}, kernel: {}}
**Floors:** F02, F03, F05
**Status:** PLANNED

### P-3: A-PROMPT (Analysis Prompt)

**Purpose:** Ground analysis in constitutional principles
**When used:** Before analytical tools (reason, evidence, critique)
**Inputs:** query, session_id, available_tools
**Outputs:** grounded analysis with floor awareness
**Floors:** F01-F13 (all)
**Status:** PLANNED

### P-4: Prompt Master

**Purpose:** Meta-prompt for high-quality responses
**When used:** Before arif_reply_compose
**Inputs:** verdict, evidence, critique, tone_requirement
**Outputs:** structured response
**Floors:** F04, F06, F09
**Status:** PLANNED

### P-5: Commitment Protocol

**Purpose:** Ensure actor understands consequences before forge/judge/vault
**When used:** Before mutating tools (arif_forge_execute, arif_judge_deliberate, arif_vault_seal)
**Inputs:** action, reversibility_score, delta_S, ack_required
**Outputs:** explicit commitment acknowledgment
**Floors:** F01, F11, F13
**Status:** PLANNED

### P-6: A2A Negotiation Prompt

**Purpose:** Govern agent-to-agent delegation and handoff
**When used:** Before arif_gateway_connect (cross-agent)
**Inputs:** source_agent, target_agent, task, authority_level
**Outputs:** delegation envelope with constraints
**Floors:** F01, F03
**Status:** PLANNED

### P-7: Operator Handoff Prompt

**Purpose:** Structured handoff when human operator takes over
**When used:** During HOLD verdict or explicit operator request
**Inputs:** session state, pending actions, risk level
**Outputs:** handoff summary + operator instructions
**Floors:** F11, F12, F13
**Status:** PLANNED

### P-8: Crisis Fallback Prompt

**Purpose:** Minimal safe response when system is degraded
**When used:** During DEGRADED status or organ unreachable
**Inputs:** degraded_component, last_known_state
**Outputs:** safe-mode response, no mutation
**Floors:** F01, F04, F11
**Status:** PLANNED

### P-9: Migration/Recovery Prompt

**Purpose:** Guide system restoration after failure
**When used:** After crash, restart, or vault recovery
**Inputs:** failure_log, vault_last_seal, session_state
**Outputs:** recovery checklist + verification steps
**Floors:** F01, F08, F11
**Status:** PLANNED

---

## Old Prompt Assets (to be compressed)

| Old File | Insight | New Home |
|---|---|---|
| `prompts/deliberation.py` | Judge deliberation flow | P-4 Prompt Master |
| `prompts/init.py` | Session init sequence | P-3 A-PROMPT |
| `prompts/judge.py` | Judge verdict logic | P-5 Commitment Protocol |
| `prompts/meta_skills.py` | Meta-skill routing | P-1 RAF |
| `prompts/system.py` | System-level context | P-3 A-PROMPT |

---

## Implementation Status

| Prompt | Location | Implemented | Tested | Sealed |
|---|---|---|---|---|
| P-1 RAF | `prompts/canonical/raf.md` | NO | NO | NO |
| P-2 TEOF | `prompts/canonical/teof.md` | NO | NO | NO |
| P-3 A-PROMPT | `prompts/canonical/a-prompt.md` | NO | NO | NO |
| P-4 Prompt Master | `prompts/canonical/prompt-master.md` | NO | NO | NO |
| P-5 Commitment | `prompts/canonical/commitment.md` | NO | NO | NO |
| P-6 A2A Negotiation | `prompts/canonical/a2a-negotiation.md` | NO | NO | NO |
| P-7 Operator Handoff | `prompts/canonical/operator-handoff.md` | NO | NO | NO |
| P-8 Crisis Fallback | `prompts/canonical/crisis-fallback.md` | NO | NO | NO |
| P-9 Migration Recovery | `prompts/canonical/migration-recovery.md` | NO | NO | NO |

**Current count:** 0/9 implemented
**Target:** 9/9

---

*DITEMPA BUKAN DIBERI — 9 prompts planned, 0 written*
