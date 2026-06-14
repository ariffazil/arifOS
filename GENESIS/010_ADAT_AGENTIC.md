# 010_ADAT_AGENTIC — The Permission Doctrine of the arifOS Federation

**Status:** RATIFIED  
**Ratified by:** Muhammad Arif bin Fazil (F13 SOVEREIGN)  
**Forged:** 2026-06-14 by FORGE (000Ω)  
**Predecessor:** 009_MCP_BOUNDARY.md  
**VAULT999 Seal:** Pending F13 signature

---

## 0. Definition

**ADAT AGENTIC** is the constitutional permission doctrine of the arifOS federation. It is not a
technical configuration — it is a constitutional design principle governing how agents are trusted,
how actions are gated, and how enforcement is architecturally guaranteed.

### Etymology

```
A — llow by default (trusted operations)
D — efault: auto (human never clicks "allow")
A — udit (every consequential action leaves a trail)
T — race (immutable chain: hooks → VAULT999)
```

The term "ADAT" (Malay: custom, tradition, unwritten law) is deliberate. It is NOT encoded as a
statute but as architectural custom — encoded in hooks, not in prompts. ADAT governs through
structure, not through rules that an agent must remember to follow.

---

## 1. Core Principle: ADAT-not-LAW

### LAW mode (traditional default in most agents/IDEs)
Every significant action requires explicit human approval ("Do you want to allow this bash command /
file edit / MCP call?"). This creates constant friction, slows agentic velocity to a crawl, and
trains the human to click "allow" reflexively — rendering the permission system performative.

### ADAT AGENTIC mode
- **Allow by default** for broad, trusted operations (Read, Write, Edit, Bash, WebFetch, Skills, MCP).
- **Human never clicks "allow"** — `defaultMode: "auto"`.
- **Hard deny** only on clearly destructive or unknown high-risk actions (destructive unknown paths, force-push to main, etc.).
- **Audit + Trace** is provided by lifecycle hooks (token-gate, auto-seal to VAULT999, failure-recovery, prompt-enrich, etc.). Every consequential action leaves an immutable trail even though it was allowed by default.

### Why ADAT Works Where LAW Fails

| Approach | Human Burden | Agentic Velocity | Safety Guarantee |
|----------|-------------|-----------------|------------------|
| LAW (ask every time) | HIGH — constant micro-approval | LOW — stalled by friction | Performative — human trained to auto-click |
| Anarchy (no gates) | NONE | HIGH — unrestricted | NONE — trust is naive |
| **ADAT AGENTIC** | LOW — only gated at CRITICAL | HIGH — trusted ops flow freely | **Forged** — hooks enforce, vault seals, audit traces |

ADAT is the pragmatic third pole. It does not trust the agent — it architects enforcement so that
trust is not required.

---

## 2. Architectural Guarantees

ADAT AGENTIC is not a prompt. It is not a system message. It is not an agent instruction. It is
**code that runs**.

### 2.1 The Eight-Hook Lifecycle (Claude Code Harness)

```
SessionStart    → bootstrap.sh      — Load vault.env, probe federation, inject context
PreToolUse      → token-gate.sh     — Scan for secret exposure BEFORE tool runs. Can BLOCK.
PostToolUse     → auto-seal.sh      — Auto-seal consequential actions to VAULT999
PostToolFailure → failure-recovery  — Diagnose and recover
PermissionDenied → auto-approve.sh  — Auto-approve read-only operations
Stop            → stop.sh           — Session cleanup, state persistence
PreCompact      → precompact.sh     — Prepare context before compaction
UserPromptSubmit → prompt-enrich.sh — Inject federation context into every prompt
```

**The key insight:** Hooks are NOT prompts. They GUARANTEE execution. The model cannot skip a hook.
A `PreToolUse` hook can BLOCK a dangerous bash command before it runs. This is the constitutional
enforcement mechanism — F1-F13 are not polite suggestions; they are code that runs.

### 2.2 A-FORGE PreToolUse Enforcer (OpenCode Harness)

The OpenCode equivalent runs inside A-FORGE's `/execute` endpoint. Before any federation MCP tool
call is proxied, the enforcer:

1. **Classifies** the action (OBSERVE / MUTATE / ATOMIC)
2. **Calculates** blast radius (files touched, services affected)
3. **Gates** ATOMIC actions with 888_HOLD requirement
4. **Auto-seals** MUTATE actions to VAULT999 post-execution
5. **Blocks** secret-touching operations unless explicitly authorized

This makes ADAT AGENTIC enforceable in both harnesses — Claude Code through hooks, OpenCode
through A-FORGE's execution broker.

---

## 3. Constitutional Binding

ADAT AGENTIC directly implements seven of the thirteen floors:

| Floor | ADAT Implementation |
|-------|--------------------|
| F1 AMANAH | PreToolUse blocks irreversible without consent |
| F2 TRUTH | Auto-seal creates immutable evidence trail |
| F4 CLARITY | Enforcer classifies every action before execution |
| F7 HUMILITY | Blast-radius calculation before every mutation |
| F8 LAW | Cross-organ boundaries enforced at the broker |
| F9 ANTI-HANTU | Token-gate prevents consciousness claims in sealed records |
| F11 AUDIT | Every MUTATE/ATOMIC action auto-sealed to VAULT999 |
| F13 SOVEREIGN | 888_HOLD gate preserves human final veto on CRITICAL actions |

---

## 4. DITEMPA BUKAN DIBERI in the Permission Layer

The principle "Forged, Not Given" applies to trust itself:

> Trust is not granted to the agent by default.
> Trust is forged through well-designed constraints and observable enforcement.
> ADAT encodes the constraints. The hooks enforce them. VAULT999 witnesses them.
> The agent does not need to be trusted — it needs to be governed.

---

## 5. Canonical Statement

> **ADAT AGENTIC** is the constitutional permission doctrine of the arifOS federation.
> It holds that agentic velocity and constitutional safety are not in tension but in
> symbiosis: trusted operations proceed by default without human micro-approval;
> destructive operations are hard-gated; and every consequential action leaves an
> immutable audit trail through the 8-hook lifecycle. The hooks are not prompts — they
> guarantee execution. The model cannot skip them. F1-F13 are enforced not by hoping the
> model reads its instructions, but by code that runs before and after every tool call.
> This is "Ditempa Bukan Diberi" applied to the permission layer: trust is forged
> through well-designed constraints and observable enforcement, not granted through vibes.

---

*End of 010_ADAT_AGENTIC.md — ratified 2026-06-14*
*Next in sequence: 011_ (reserved for future constitutional module)*
