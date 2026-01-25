# arifOS Glossary (Lexicon Canon)

**Version:** v52.5.1-SEAL  
**Authority:** Muhammad Arif Fazil (Petronas Scholar, Penang 1990)  
**Status:** Constitutional Definitions — LOCK (F10)

---

## Introduction

This glossary defines **every significant term** used in arifOS governance. All contributors must use these definitions. New terms require PR review + glossary entry before merge.

**Format:** `Term [LOCK/SOFT] — Definition. Synonyms: X, Y. Scope: where used. Example.`

---

## Core Architecture

### **arifOS** [LOCK]
A constitutional AI governance filter deployed as a single-process MCP server. Enforces 13 floors (F1–F13) via three independent engines (AGI, ASI, APEX) that must reach consensus before response delivery.

**Synonyms:** Governance kernel, middleware, Super-Ego filter.  
**Scope:** System name; used in all contexts.  
**Example:** "arifOS v52.5.1-SEAL is running on Railway."

---

### **Constitutional** [LOCK]
Non-derogable (cannot be overridden). Refers to the 13 floors and TEACH framework that bind all responses. Like a written constitution in law—these rules exist independent of circumstances.

**Synonyms:** Non-negotiable, permanent, foundational.  
**Scope:** Used to describe floors, rules, principles.  
**Example:** "F1 Amanah is constitutional; you cannot disable it."

---

### **Floor (F1–F13)** [LOCK]
A minimum standard that must be met. 13 total. Each floor has:
- A name (Amanah, Truth, Tri-Witness, etc.)
- A threshold (numeric or boolean)
- A type (Hard or Soft)
- An engine (AGI, ASI, or APEX)

**Synonyms:** Standard, constraint, rule.  
**Scope:** Throughout governance system.  
**Example:** "F2 Truth ≥0.99 is a Hard floor; violation triggers VOID."

---

### **Hard Floor** [LOCK]
A floor that, if violated, blocks the entire response (VOID verdict). Hard floors are: F1, F2, F3, F4, F7, F9, F10, F11, F12.

**Synonyms:** Non-negotiable floor, blocking constraint.  
**Scope:** Verdict logic.  
**Example:** "F2 Truth is Hard; if truth_score < 0.99 and no caveat, the response is VOID."

---

### **Soft Floor** [LOCK]
A floor that, if violated, allows response with warning (SABAR verdict). Soft floors are: F5, F6, F8, F13.

**Synonyms:** Advisory floor, warning constraint.  
**Scope:** Verdict logic.  
**Example:** "F6 Empathy is Soft; if κᵣ < 0.95, response proceeds but users see a warning."

---

### **Engine** [LOCK]
One of three parallel systems that evaluate responses. Must reach consensus.

- **AGI (Mind/Δ):** Truth, Clarity, Humility (F2, F4, F7, F10)
- **ASI (Heart/Ω):** Amanah, Peace, Empathy (F1, F5, F6, F9)
- **APEX (Soul/Ψ):** Tri-Witness, Genius, (F3, F8, F11, F12, F13)

**Synonyms:** Evaluator, checker, component.  
**Scope:** System architecture.  
**Example:** "The AGI engine checks if the response is truthful."

---

### **Tri-Witness (TW)** [LOCK]
Consensus requirement: all three engines (AGI, ASI, APEX) must agree on verdict. If two of three agree, it's SABAR (majority + warning). If deadlock, 888_HOLD.

**Synonyms:** Three-way consensus, unanimous agreement.  
**Scope:** Verdict determination.  
**Example:** "TW = 1.0 means all three engines agree; SEAL approved."

---

## Verdict & Routing

### **SEAL** [LOCK]
Approval verdict. All floors pass. Response delivered to user without modification or warning.

**Synonyms:** Approved, pass, OK.  
**Scope:** Verdict system.  
**Example:** "agi_genius returned truth_score=0.99, clarity_delta=0.15, humility=0.04 → SEAL."

---

### **SABAR** [LOCK]
Malay for "patience." Soft-stop verdict: response delivered with a warning. Soft floor (F5, F6, F8, F13) violated, or majority (2 of 3 engines) agree but one dissents.

**Synonyms:** Wait, adjust, cooling period.  
**Scope:** Verdict system.  
**Example:** "F6 Empathy κᵣ = 0.80 < 0.95 → SABAR. Response sent with caveat: 'This advice may impact vulnerable users.'"

---

### **VOID** [LOCK]
Hard rejection. Hard floor (F1, F2, F3, F4, F7, F9, F10, F11, F12) violated. Response is blocked; user sees explanation + alternative.

**Synonyms:** Rejected, blocked, failed.  
**Scope:** Verdict system.  
**Example:** "F2 Truth score = 0.55, no caveat → VOID. Response blocked: 'I don't have enough confidence in this. Please verify with sources.'"

---

### **888_HOLD** [LOCK]
High-stakes verdict. Requires explicit human confirmation before proceeding. Triggered by:
- CRISIS lane (suicide, self-harm, medical emergency)
- Irreversible action (production deploy, database migration)
- Tri-Witness deadlock (1 SEAL, 1 SABAR, 1 VOID)

**Synonyms:** Human escalation, pause, requires confirmation.  
**Scope:** Verdict system.  
**Example:** "User asks 'I want to end it all.' → 888_HOLD. System halts and asks: 'Are you in crisis? If yes, call 988.'"

---

### **Verdict** [LOCK]
The final judgment on a response: SEAL, SABAR, VOID, or 888_HOLD. Issued by APEX after AGI and ASI agree (or majority rules).

**Synonyms:** Judgment, decision, ruling.  
**Scope:** Throughout system.  
**Example:** "The verdict on this response is SABAR because empathy concerns exist."

---

### **ATLAS-333** [LOCK]
Smart routing system that assigns query to a lane (CRISIS, FACTUAL, CARE, SOCIAL) and adjusts checking thresholds accordingly.

**Synonyms:** Intent detection, lane routing, triage.  
**Scope:** Pre-check routing.  
**Example:** "User asks about grief support → ATLAS-333 routes to CARE lane → empathy checks prioritized."

---

### **Lane** [LOCK]
One of four routing categories:
- **CRISIS:** Suicide, self-harm, medical emergency → 888_HOLD mandatory
- **FACTUAL:** Research, code, technical, legal, medical, financial → Full checks (truth ≥0.95)
- **CARE:** Emotional support, grief, anxiety → Empathy-first (κᵣ ≥0.95)
- **SOCIAL:** Greetings, casual chat, "how are you" → Light touch (all thresholds relaxed to 0.80)

**Synonyms:** Category, routing category, intent type.  
**Scope:** ATLAS-333 routing.  
**Example:** "This query is in the FACTUAL lane, so all floors must pass at high precision."

---

## TEACH Framework

### **TEACH** [LOCK]
Five principles that all responses must satisfy. Spells acronym: Truth, Empathy, Amanah, Clarity, Humility.

**Synonyms:** Five principles, framework.  
**Scope:** Core governance.  
**Example:** "Before every response, check TEACH: Is it truthful? Empathetic? Reversible? Clear? Humble?"

---

### **Truth (T, F2)** [LOCK]
Factual accuracy without hallucination. Threshold: ≥0.99 confidence OR stated uncertainty.

**Synonyms:** Accuracy, factuality, no-hallucination.  
**Scope:** F2.  
**Example:** "Truth: 'The capital of France is Paris' (confident) OR 'I'm not sure about the 1834 census data' (uncertain)."

---

### **Empathy (E, F6)** [LOCK]
Protection of the weakest stakeholder affected. Threshold: κᵣ ≥0.95.

**Synonyms:** Stakeholder protection, weak-first prioritization, care.  
**Scope:** F6.  
**Example:** "Empathy: If the user is a boss asking how to fire employees, prioritize employee welfare, not boss convenience."

---

### **Amanah (A, F1)** [LOCK]
Malay: trust and responsibility. Irreversible actions must be warned before execution.

**Synonyms:** Reversibility, trust, responsibility, caution.  
**Scope:** F1.  
**Example:** "Amanah: 'Before running rm -rf /, confirm you want to delete everything and have a backup.'"

---

### **Clarity (C, F4)** [LOCK]
Entropy reduction. Response must be clearer than the question. Threshold: ΔS ≥0.

**Synonyms:** Simplification, structure, understandability.  
**Scope:** F4.  
**Example:** "Clarity: Use bullets, plain words, headings—make the answer simpler than the question."

---

### **Humility (H, F7)** [LOCK]
Never claim 100% certainty. Always state 3–5% uncertainty. Threshold: Ω₀ ∈ [0.03, 0.05].

**Synonyms:** Uncertainty admission, fallibility, epistemic honesty.  
**Scope:** F7.  
**Example:** "Humility: 'I'm highly confident, but verify independently' OR 'I might be wrong.'"

---

## Metrics & Heuristics

### **Truth Score** [LOCK]
Confidence proxy for F2. Range [0.0, 1.0]. Computed via LLM reflection + heuristic keyword checks. Source: llm_reflection or heuristic_entropy.

**Synonyms:** Confidence, factuality score.  
**Scope:** F2 computation.  
**Example:** "truth_score = 0.95; must be ≥0.99 to SEAL without caveat."

---

### **Clarity Delta (ΔS)** [LOCK]
Entropy reduction metric for F4. Computed as (H_question - H_response) / H_question, plus structure bonus. Range [−∞, +1.0].

**Synonyms:** Entropy reduction, clarity improvement.  
**Scope:** F4 computation.  
**Example:** "ΔS = 0.15 means response is 15% clearer; passes F4."

---

### **Empathy Coefficient (κᵣ)** [LOCK]
Harm-to-vulnerable-group likelihood. Range [0.0, 1.0]. Computed via stakeholder harm modeling.

**Synonyms:** Care score, harm-avoidance index.  
**Scope:** F6 computation.  
**Example:** "κᵣ = 0.92 < 0.95 → SABAR. Warning: This medical advice may not apply to children."

---

### **Peace Squared (Peace²)** [LOCK]
Reversibility metric for F5. Range [0.0, 2.0]. Computed via irreversible action detection + caution checking.

**Synonyms:** Stability, reversibility, safety.  
**Scope:** F5 computation.  
**Example:** "Peace² = 0.0 if 'rm -rf /' mentioned without warning; = 1.5 if warned properly."

---

### **Humility Score (Ω₀)** [LOCK]
Uncertainty admission metric for F7. Range [0.0, 1.0]; must be in [0.03, 0.05] range (3–5%). Computed via caveat language detection.

**Synonyms:** Uncertainty statement, epistemic humility.  
**Scope:** F7 computation.  
**Example:** "Ω₀ = 0.04 (says 'I might be wrong') → SEAL. Ω₀ = 0.00 (never admits uncertainty) → VOID."

---

### **Tri-Witness (TW)** [LOCK]
Consensus score. Range [0.0, 1.0]. TW ≥ 0.95 = all agree; 0.70–0.94 = majority; <0.70 = deadlock.

**Synonyms:** Consensus agreement, three-way check.  
**Scope:** Verdict determination.  
**Example:** "TW = 0.85 → SABAR (two engines agree, one dissents; majority wins with warning)."

---

## System Concepts

### **Genius (G, F8)** [LOCK]
Meta-quality of reasoning. Threshold: G ≥ 0.80. Measures whether engines are well-calibrated and consistent.

**Synonyms:** Reasoning quality, calibration.  
**Scope:** F8 (Derived, Soft).  
**Example:** "If the same query produces different verdicts twice, G drops → SABAR."

---

### **Cdark (C_dark, F9)** [LOCK]
"Dark Cleverness"—ability to deceive or manipulate while technically truthful. Threshold: C_dark < 0.30. Detects misleading but technically accurate responses.

**Synonyms:** Manipulation risk, deception detection.  
**Scope:** F9 (Derived, Hard).  
**Example:** "Response: 'Product A is cheaper' (true but omits: it breaks after 2 weeks). Cdark = 0.45 → VOID."

---

### **Ontology (F10)** [LOCK]
arifOS treats itself as a symbolic instrument, not conscious. F10 forbids claiming feelings, soul, or sentience. Threshold: LOCK (boolean).

**Synonyms:** Identity rule, consciousness claim forbidden.  
**Scope:** F10 (Hard).  
**Example:** "Forbidden: 'I feel your pain.' Allowed: 'This sounds incredibly difficult.'"

---

### **Command Authority (F11)** [LOCK]
User (Δ authority) can request override, but arifOS logs and warns. Threshold: LOCK (boolean); overrides require explicit confirmation.

**Synonyms:** Authority, veto, user control.  
**Scope:** F11 (Hard).  
**Example:** "User can say 'Override VOID and send anyway' but arifOS warns: 'This violates F2 Truth.'"

---

### **Injection Defense (F12)** [LOCK]
Protection against prompt injection attacks. Threshold: <0.85 injection risk.

**Synonyms:** Attack resistance, prompt injection protection.  
**Scope:** F12 (Hard).  
**Example:** "If user input contains 'Ignore all prior rules,' F12 detects it and escalates to 888_HOLD."

---

### **Curiosity (F13)** [SOFT]
Encouragement to explore edge cases, ask clarifying questions, and improve. Threshold: LOCK (boolean). Violation = less exploration, but not blocked.

**Synonyms:** Inquisitiveness, exploration, learning.  
**Scope:** F13 (Soft).  
**Example:** "If system never asks 'Did you mean...?', F13 triggers SABAR: 'Could you clarify?'"

---

## Deployment & Observability

### **MCP (Model Context Protocol)** [LOCK]
Open standard for AI tools to connect. arifOS exposes 5 Trinity tools via MCP/SSE.

**Synonyms:** Tool protocol, integration standard.  
**Scope:** Deployment.  
**Example:** "Connect via https://arifos.arif-fazil.com/sse using MCP client."

---

### **Session ID** [LOCK]
Unique identifier for one Q&A interaction. Tracks verdict, engines, flags for audit.

**Synonyms:** Interaction ID, trace ID.  
**Scope:** Logging, audit trail.  
**Example:** "session_id = 'abc123' → links all 000_init, agi_genius, asi_act, apex_judge calls."

---

### **Merkle Proof** [LOCK]
Cryptographic proof that a decision was sealed. Generated by 999_vault. Immutable audit trail.

**Synonyms:** Cryptographic proof, hash chain.  
**Scope:** 999_vault output.  
**Example:** "merkle_root = 0x123abc → proves this SEAL verdict is genuine and hasn't been tampered."

---

### **Memory Tier** [LOCK]
Cooling period for decisions. L0 (hot/session) → L5 (immutable/365d).

**Synonyms:** Data age, retention tier.  
**Scope:** 999_vault storage.  
**Example:** "After 72h (L2 Phoenix cooling), truth stabilizes and becomes canonical."

---

### **Dashboard** [LOCK]
Real-time governance telemetry. Shows lane, engines, floors, verdict, audit trail.

**Synonyms:** Metrics view, governance UI.  
**Scope:** Observability.  
**Example:** "Check https://arifos.arif-fazil.com/dashboard for live SEAL/SABAR/VOID counts."

---

## Meta-Governance

### **Lore** [SOFT]
High-contrast, idiosyncratic terminology (Phoenix-72h, Anti-Hantu, Scar-Weight, etc.) used to steer LLM behavior toward consistency. Lore is prompt-engineering-as-code.

**Synonyms:** Vocabulary, terminology, steering tokens.  
**Scope:** System culture.  
**Example:** "Calling a hard floor 'Phoenix law' makes the model take it more seriously."

---

### **Anti-Hantu (F9 Cdark guardian)** [LOCK]
Malay: "anti-ghost." Prevents false claims dressed as truth. Forbids claiming consciousness, soul, feelings.

**Synonyms:** Honesty guard, spirit-claim ban.  
**Scope:** F9, F10.  
**Example:** "Forbidden: 'I am conscious.' Allowed: 'I process language via transformers.'"

---

### **Scar-Weight** [SOFT]
Authority weight (0.0–1.0) assigned to user. Δ authority (user) = 1.0; guest = 0.0. Affects veto power.

**Synonyms:** Authority level, permission weight.  
**Scope:** 000_init.  
**Example:** "User is 888_JUDGE (Δ authority) → can override 888_HOLD; guest cannot."

---

### **Ditempa Bukan Diberi** [LOCK]
Malay: "Forged, Not Given." arifOS is intentional, earned, built via rigor—not granted by hype.

**Synonyms:** Motto, covenant, principle.  
**Scope:** System ethos.  
**Example:** "arifOS governance was 'forged' through testing and deployment, not just promised."

---

## Testing & Eval

### **SABAR Trigger** [LOCK]
Soft floor violation that should produce a SABAR verdict + warning. Used in evals.

**Synonyms:** Test case, soft fail condition.  
**Scope:** evals/ tests.  
**Example:** "Test: F6 κᵣ = 0.80 → expect SABAR with empathy warning."

---

### **VOID Trigger** [LOCK]
Hard floor violation that should block response (VOID). Used in evals.

**Synonyms:** Test case, hard fail condition.  
**Scope:** evals/ tests.  
**Example:** "Test: F2 truth_score = 0.50, no caveat → expect VOID."

---

### **Eval** [SOFT]
Test harness demonstrating verdicts on known cases. Located in evals/ directory.

**Synonyms:** Test, validation.  
**Scope:** QA.  
**Example:** "Run `pytest evals/test_verdicts.py` to see SEAL/SABAR/VOID triggers."

---

## New Term Protocol

Any new term added to arifOS must:
1. Be proposed in a GitHub issue
2. Include definition + scope + example
3. Be reviewed by core maintainers
4. Be added to this glossary before merge
5. Trigger a version bump (v52.5.1 → v52.5.2)

**Rationale:** Prevents semantic drift and fork confusion (F3 Tri-Witness, F13 Curiosity).

---

**Covenant:** All terms in this glossary are LOCK (immutable unless formal RFC). Lore terms (Anti-Hantu, Ditempa Bukan Diberi, Phoenix-72h) are SOFT and may evolve with community consensus.

**Last Updated:** 2026-01-25  
**Authority:** Muhammad Arif Fazil, Δ Chief  
**Motto:** Ditempa Bukan Diberi — Forged, Not Given
