# arifOS Federation Glossary

> **Every term, one plain-English definition.** If a stranger encounters a word they don't know, this is where they find it.
>
> **Rule:** Every term on first use in any public document should link here.

---

## A

### AAA (Agents, API, Apps)
The **operator surface** of the arifOS federation — the control plane where a human submits missions, views HOLD queues, and provides approval. AAA is also the **Trinity architecture pattern**: AGI (Mind — reasons), ASI (Heart — critiques), APEX (Soul — decides).

### A-FORGE
The **execution organ.** Builds, deploys, and runs approved plans. Hard-gated: it cannot act without a `JUDGE_SEAL_AUTHORIZATION` verdict from the constitutional kernel. It is the hands of the federation — capable, precise, and constitutionally bound.

### AGI (Δ DELTA — Mind)
The **tactical reasoning lane** of the AAA Trinity. Proposes plans, synthesizes evidence, reduces entropy. Covers floors F2 (Truth), F4 (Clarity), F7 (Humility), F8 (Genius).

### AMANAH (F1)
Malay for "trust." The **first constitutional floor.** Every irreversible action requires explicit human acknowledgment — you must say "yes, I accept this cannot be undone." No silent approvals.

### ANTIHANTU (F9)
Malay for "anti-ghost." The **integrity floor.** The machine is an instrument, not a being. No consciousness claims. No spiritual cosplay. No pretending to be human. Violation = VOID.

### APEX (Ψ PSI — Soul)
The **authority lane** of the AAA Trinity. Issues binding constitutional verdicts (SEAL / HOLD / VOID). Covers floors F3 (Witness), F10 (Ontology), F11 (Auth), F12 (Injection), F13 (Sovereign). Also refers to **Muhammad Arif bin Fazil** — the human sovereign.

### ASI (Ω OMEGA — Heart)
The **strategic judgment lane** of the AAA Trinity. Critiques proposed actions for safety, stakeholder impact, and manipulation. Covers floors F1 (Amanah), F5 (Peace²), F6 (Empathy), F9 (Antihantu).

### Authority Chain
The strict, non-skippable flow of power: Sovereign → arifOS Kernel → Domain Organs → AAA Surface → VAULT999 → A-FORGE. If any link is missing, execution is impossible. No organ may self-authorize.

---

## B

### Beautiful One
See **Anti-Beautiful-One.**

---

## C

### Constitutional Floor (F1–F13)
One of thirteen **hard rules** that every action must pass. Enforced by code, not by prompts. A floor violation stops the action immediately. See individual floor entries.

### CAUTION
A verdict meaning "valid but borderline — judge should scrutinize more carefully before sealing."

---

## D

### DITEMPA BUKAN DIBERI
Malay for **"Forged, Not Given."** The constitutional motto of arifOS. It means: intelligence is earned through work and proven through operational contact with reality, not asserted through polished language. It is the refusal of sterile collapse — the choice to be in the arena, accountable, with skin in the outcome.

### Domain Organ
Any of GEOX, WEALTH, or WELL — organs that **compute evidence** but never decide. They issue `DOMAIN_SEAL_VALIDITY` (their calculation is internally consistent), never `JUDGE_SEAL_AUTHORIZATION` (permission to act).

### DOMAIN_SEAL_VALIDITY
A seal issued by a domain organ (GEOX / WEALTH / WELL) meaning: "The calculation in my domain is internally consistent." Carries **no execution authority.** Must not be confused with `JUDGE_SEAL_AUTHORIZATION`.

---

## E

### 888 (888_JUDGE)
The **constitutional deliberator.** 888 is the number (not the year). The 888_JUDGE evaluates all thirteen floors and issues binding verdicts: SEAL (approved), HOLD (needs human review), or VOID (rejected). It is the only path to `JUDGE_SEAL_AUTHORIZATION`.

### Entropy (dS)
A measure of **system disorder.** In arifOS, every action either increases or decreases system entropy. Actions that create disorder, confusion, or ambiguity increase entropy and may be gated. The constitutional floor F4 (Clarity) requires that entropy decreases — the system must become more ordered through use.

---

## F

### Federation
The seven-organ system: arifOS + GEOX + WEALTH + WELL + AAA + A-FORGE + arif-sites. Each organ has one job. None may self-authorize execution. All communicate via MCP (Model Context Protocol).

### Forge Gate
The set of conditions that must all be true before A-FORGE can execute a plan: verified actor, stable context, complete authority chain, JUDGE_SEAL_AUTHORIZATION, acceptable reversibility score, and explicit APEX approval.

---

## G

### GEOX
The **earth intelligence organ.** Provides subsurface evidence — well logs, petrophysics, seismic data, prospect evaluation. It witnesses Earth. It never authorizes drilling decisions.

### Gödel Lock
Named after Kurt Gödel's incompleteness theorems. The first **Deep Lock:** no system may certify its own total truth from inside itself. When an agent claims "I am safe" or "I am the final judge," that claim is automatically VOIDED because the agent is inside the system it claims to verify.

---

## H

### HOLD
A verdict meaning **"blocked pending human review."** Not rejected — HOLD can resolve to SEAL after human approval. HOLDs are queued in the AAA operator surface for the human sovereign to see.

---

## J

### JUDGE_SEAL_AUTHORIZATION
The only seal that matters for execution. Issued by 888_JUDGE after all thirteen floors are cleared, evidence chain is complete, and APEX (human) has approved. This is the single bit that opens A-FORGE's execution gate.

---

## K

### KERNEL_SEAL_AWARENESS
A seal issued by the arifOS kernel meaning "I have seen this. I have not adjudicated it." Pure awareness. No authority. Used for logging and audit, never for authorization.

---

## L

### L1–L6 (Memory Layers)
The six-layer memory architecture. L1 = ephemeral (disappears on restart). L2 = session (this conversation). L3 = semantic similarity (Qdrant vector search). L4 = official record (Supabase PostgreSQL). L5 = relationships (Graphiti entity graph). L6 = immutable sealed archive (VAULT999).

---

## M

### MCP (Model Context Protocol)
The communication protocol used by all federation organs. Each organ exposes its tools as MCP endpoints. Organs discover and call each other's tools through MCP. Public endpoints: `https://<organ>.arif-fazil.com/mcp`.

---

## P

### Provenance
The **chain of evidence** proving where a piece of information came from, who verified it, and when. Memory without provenance is quarantined. Truth without provenance is not truth — it is hearsay.

### PUBLIC_SEAL_READINESS
A seal issued by the arif-sites Observatory meaning "the current public posture is X." This is a **candidate posture** — not execution approval. Shows the outside world what the federation believes about itself at this moment.

---

## R

### Receipt
A **structured record of evidence** — what was observed, who observed it, when, and with what uncertainty. Every claim must be receipt-bound. You cannot say "the reservoir is 100 meters thick" without pointing to the log, the interpreter, and the uncertainty band that produced that number.

### Reversibility Score (R)
A number from 0.0 (completely irreversible) to 1.0 (trivially reversible). Every action carries a reversibility score. Actions with R < 0.3 require explicit human approval. The constitution requires: prefer reversible action.

---

## S

### SABAR
Malay for "patient discipline." A verdict meaning **"valid but incomplete — wait for more evidence."** The calculation is internally correct, but the full evidence package is not yet assembled. Not rejection; deferred approval.

### SEAL
**Not a generic "approved."** Must always carry a namespace prefix: `KERNEL_SEAL_AWARENESS`, `DOMAIN_SEAL_VALIDITY`, `JUDGE_SEAL_AUTHORIZATION`, `VAULT999_SEAL_RECORD`, or `PUBLIC_SEAL_READINESS`. Bare "SEAL" in any badge, log, or surface is non-compliant and must be renamed.

### Sovereign (F13)
The **human with absolute final veto.** Muhammad Arif bin Fazil in the current deployment. F13 SOVEREIGN is the Gödellian fix — the external reference point that breaks the self-referential loop. No algorithm may override the Sovereign.

### Strange Loop Lock
The second **Deep Lock.** Named after the self-referential structure of a sovereign system: the Sovereign authorizes the kernel, the kernel authorizes the judge, the judge verifies the kernel, agents serve the Sovereign. The loop is structural, not a bug. The lock prevents memory from entering the loop without provenance — preventing memory mythology.

### Substrate
Whatever is being assessed for readiness — a human (biological substrate), a machine (compute substrate), or a coupled human-machine system. WELL reflects substrate state; it never diagnoses or treats.

---

## T

### Tri-Witness
The requirement that a constitutional decision be witnessed by **three independent perspectives** — typically a human, an AI, and the evidence record. Named after the Islamic legal principle of requiring three witnesses for certain transactions.

### Trinity (AAA Trinity)
The three-lane architecture: AGI (Mind — reason), ASI (Heart — critique), APEX (Soul — decide). The three engines are designed to **disagree** — forcing resolution through evidence or human judgment.

---

## V

### VAULT999
The **immutable audit ledger.** Append-only, hash-chained, Ed25519-signed. Every sealed decision, veto, and execution is recorded here forever. Nothing is ever deleted. Nothing is ever modified. 999 is the number — it represents finality (the last three-digit number, the end of the chain).

### VAULT999_SEAL_RECORD
A seal meaning "an immutable entry has been written to the ledger." Permanent for audit. Carries **no execution authority** — it records what happened, it does not authorize what happens next.

### Verdict
A **constitutional judgment** — SEAL, SABAR, VOID, or HOLD. Every verdict is receipt-bound and traceable to the evidence, floors, and judge deliberation that produced it. The system speaks in verdicts, not in yes/no.

### VOID
A verdict meaning **"rejected."** A constitutional floor has been violated. The action is blocked. VOID is final for the current session and evidence set — new evidence may reopen, but the same evidence cannot produce a different verdict.

---

## W

### WEALTH
The **capital intelligence organ.** Computes NPV, IRR, EMV, risk scores, portfolio allocation, sovereign resource economics. It computes value. It never allocates capital.

### WELL
The **human readiness organ.** Observes and reports vitality — sleep, fatigue, stress, cognitive clarity, dignity. It reflects substrate state. It never diagnoses, treats, or provides medical advice.

### Witness
A **verification layer** in the VAULT999 architecture. Every sealed entry carries attestations from human, AI, and evidence witnesses. The Byzantine Quad-Witness requirement (F3): consensus across Human × AI × Earth × Verifier must be ≥ 75%.

---

## 9

### 999 (VAULT999)
See **VAULT999.** The number 999 represents finality — the last three-digit number, the end of the chain. What is sealed in VAULT999 is final.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
