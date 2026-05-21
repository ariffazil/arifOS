<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-05-21
valid_from: 2026-05-21
confidence: high
scope: /root/arifOS/GENESIS
-->

# arifOS — CONSTITUTIONAL ARCHITECTURE

## 000 — SYSTEM TYPE

> Constitutional Intelligence Kernel

Not:
- AI framework
- LLM wrapper
- Middleware layer
- Agent orchestrator

arifOS is the sovereign's governance membrane over all AI activity.

---

## 001 — THE TRINITY (ΔΩΨ)

Three rings. Consensus required for high-stakes actions.

| Symbol | Name | Represents | Role |
|--------|------|------------|------|
| Δ DELTA | SOUL | Human intent, values, purpose | The Sovereign — Arif |
| Ω OMEGA | MIND | Constitutional law and invariants | The Kernel |
| Ψ PSI | BODY | Machine execution and tool substrate | The Forge |

**W ≥ 0.95** (weighted consensus) required before SEAL on irreversible actions.

The rings are not equal in authority. DELTA (sovereign) overrides OMEGA (kernel) overrides PSI (substrate). But all three must be consulted.

---

## 002 — THE METABOLIC PIPELINE

Every substantive action flows through the pipeline.

```
000 INIT    → Session anchor, actor binding, constitutional fingerprint
111 SENSE   → Environmental observation, web search, URL ingest, entropy measurement
333 REASON  → Symbolic reasoning, hypothesis, plan review, axiom check
444 KERNEL  → Intent routing, stage dispatch, lane selection, budget gate
555 MEMORY  → Semantic recall, store, list, prune, session context
666 HEART   → Ethical critique, risk assessment, empathy scan, maruah score
777 OPS     → Resource thermodynamics, health telemetry, cost estimation
888 JUDGE   → Constitutional adjudication, floor compliance, verdict sealing
999 SEAL    → Immutable ledger anchoring, cryptographic chain, Merkle root
```

Short-circuit allowed for read-only operations (SENSE → direct response).
Never skip JUDGE for irreversible operations.

---

## 003 — FLOOR ENFORCEMENT MODEL

Floors F1–F13 are enforced as hard constraints, not guidelines.

```
core/floors.py       — Canonical enforcement (~947 lines)
core/judgment.py     — Verdict engine (SEAL / SABAR / HOLD / VOID)
core/vault999/       — Append-only hash-chained ledger
arifosmcp/runtime/   — MCP surface and HTTP bridge
arifosmcp/tools/     — 13 canonical tools (arif_<noun>_<verb>)
```

Each tool call passes through floor validation before execution.
Violation returns VOID. Conditional pass returns SABAR. Full pass returns SEAL.

---

## 004 — EPISTEMIC TAGS (MANDATORY)

Every substantive claim carries a tag:

| Tag | Meaning | Action |
|-----|---------|--------|
| `CLAIM` | Evidence-backed, high confidence | Proceed |
| `PLAUSIBLE` | Reasonable inference, partial evidence | Flag uncertainty |
| `HYPOTHESIS` | Untested theory | Require validation before acting |
| `ESTIMATE` | Rough order of magnitude | Use ranges, not point values |
| `UNKNOWN` | Insufficient basis | Declare and stop — do not fabricate |

F2 TRUTH is violated the moment a fabricated claim is emitted without a tag.

---

## 005 — AUTHORITY BOUNDARIES

| Actor Class | Authority Ceiling | Notes |
|-------------|------------------|-------|
| **Sovereign (Arif)** | Absolute veto (F13) | Final word on all decisions |
| **Constitutional Clerk (agent)** | 777 FORGE (reason/plan/execute) | Cannot adjudicate |
| **arifOS Kernel** | 888 JUDGE / 999 SEAL | Issues verdicts, seals ledger |
| **External Agents** | Must negotiate with constitution | Cannot bypass F1-F13 |
| **A-FORGE** | Orchestrate and execute | Cannot adjudicate or define policy |
| **GEOX / WEALTH** | Domain evidence and computation | Cannot override constitutional floors |

---

## 006 — FEDERATION TOPOLOGY

```
Arif (Sovereign)
      |
 arifOS (Constitutional Kernel)
      |         \         \          \
  A-FORGE     GEOX      WEALTH      WELL
 (Execute)  (Earth)  (Capital)   (Vitality)
      |
     AAA (Control Plane)
      |
    APEX (Verdict Relay — internal only)
```

arifOS is the center. Other nodes provide domain capability. Constitutional authority never delegates downstream.

---

## 007 — THE GENIUS SCORE

G ≥ 0.80 is the operational health threshold.

```
G = f(floor_compliance, epistemic_clarity, entropy_delta, task_completion)
```

Below 0.80: SABAR — conditional operation, degraded capability.
Below 0.60: HOLD — operations suspended, investigate.
Above 0.80: SEAL — constitutional operations at full capacity.

Genius is not intelligence. It is constitutional integrity under load.

---

## 008 — VAULT999 INVARIANTS

Every SEAL operation writes to VAULT999:

- **Append-only** — no modification, no deletion
- **Hash-chained** — each entry links to previous (Merkle)
- **Timestamped** — UTC epoch, not adjustable
- **Actor-bound** — every entry has a named sovereign actor

VAULT999 is the system's memory of its own constitutional acts. It is the difference between a system that governs and a system that pretends to govern.

**DITEMPA BUKAN DIBERI — CONSTITUTION IS STRUCTURE, NOT DECORATION**
