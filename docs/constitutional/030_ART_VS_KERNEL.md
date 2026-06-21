# 030 — ART vs Kernel: Three Distinctions

> **Status:** SEALED — 2026-06-21 | **Supersedes:** All prior ART architecture claims
> **Scope:** Binding doctrine. Every agent that reads this knows where ART ends and Kernel begins.

---

## The Three Distinctions (one sentence each)

```
ART (horizontal)  → tool history + lifecycle + fast-screen · fails OPEN · advisory · ≤500 lines
Gate (bridge)     → 15 gates + Gate 2.5 reflex · single chokepoint · binds ALL canonical tool calls
Kernel (vertical) → Floors F1-F13 · Judge · Vault · the ONLY path that HOLDS
```

**ART ≠ Gate. Gate ≠ Kernel. Kernel ≠ ART.**
ART decides what tool move makes sense *pre-call*.
Kernel decides whether that move is *lawful*.
The Gate is where they meet.

---

## Layer Contract

| Layer | Decides | Must Not | Fails |
|--------|---------|----------|-------|
| **ART** (horizontal micro-service) | Tool lifecycle state, past-verdict memory, blast-radius fast-screen | Floor logic, side-effects, transport coupling, kernel overrule | OPEN (no ART → gate continues) |
| **Gate** (bridge, 15 gates) | Envelope → verdict pipeline. Gate 2.5 calls ART. | Skip, shortcut, or route around | CLOSED (cannot decide → HOLD) |
| **Kernel** (sovereign vertical) | Floors F1-F13, irreversibility, human sovereignty | Delegate constitutional judgment to ART or any non-sovereign organ | CLOSED (unknown → HOLD) |

---

## What ART Actually Adds (the honest answer)

ART is *not* a second kernel. It is a narrow horizontal micro-service with three functions:

1. **Tool lifecycle** — UNTRUSTED→OBSERVED→TRUSTED→FALLBACK→ABANDONED. After repeated failures or schema drift, the same tool call is downgraded or blocked even if still "legal" under Floors.

2. **Past-verdict memory (fast lane)** — ART can react differently on call N+1 than on call 1 because of its own Library, without parsing the whole VAULT.

3. **Blast-radius-aware fast screen** — ART can cheaply reject/downgrade obviously bad calls (wrong action_class + blast_radius combination) before the full 15-gate run.

Everything else (MIND, PUSAKA, COMPAT) is advisory, cold-path, or legacy compatibility. The reflex at Gate 2.5 is the only thing that has runtime effect.

---

## Human Cognitive Mapping (the three Malay-uncle reflexes)

ART in human terms: **the part of your mind that remembers how each tool behaved last time, simulates failure before acting, and quietly says "eh… jangan ulang bodoh yang sama" before you commit.**

Three human analogues map cleanly to the ART code:

| Human Cognition | ART Code | What Happens |
|---|---|---|
| "Eh, contractor tu pernah spoil" | `art_library.py` — call history + 90-day RAG | Remembers which tools failed, how often, why |
| "Kalau salah, berapa besar meletup?" | `art.py` POWER check — blast radius simulation | Premortem: "assume this tool fails — what's the damage?" |
| "Downgrade: observe dulu, jangan full commit" | DEFAULT_OBSERVE / HOLD verdict | Refuses to act when unclear; forces smaller, safer step |

**In Penang BM (elevator version):**
> "ART ni macam otak kecil yang ingat, 'Last time guna cara ni, meletup. So sebelum tekan button, kita check dulu — boleh ka? perlu ka? ada jalan lebih selamat ka?'"

> "Kernel = undang-undang. ART = kawan yang tarik tangan hang sebelum hang tekan butang nuklear sebab dia ingat hang pernah buat silap sama dulu."

**In research terms:** ART is *metacognitive strategy selection* — the discipline of choosing which tool to reach for based on remembered outcomes, not just what's available. It's "wisdom" or "experience" given a sharp name and encoded in code.

Not IQ. Not creativity. Not "soul." Just disciplined meta-tool-sense.

**The CLAIM (canonical human-readable anchor):**
> ART = **memory + premortem + downgrade reflex** for your tools.

---

## Fiqh Classification

### WAJIB (non-negotiable — ART ceases to be ART without these)

- **4-state tool lifecycle** (UNTRUSTED→OBSERVED→TRUSTED→FALLBACK→ABANDONED) feeding into ArtVerdict
- **ArtLibrary with 90-day history** — fast lookup of recent failures/drifts, used in reflex decisions
- **Gate 2.5 integration** — `_art_reflex_check()` called on every canonical tool call via `pre_execution_gate()`
- **Fail-open discipline** — if ART module fails to load, kernel still enforces Floors; no "no ART → no law"
- **≤500 line ceiling on art.py** — enforced at import via `_assert_reflex_weight_ceiling()`

### HARAM (must never exist in ART)

- **Constitutional/Floor logic** — no F1-F13 enforcement inside ART; stays in kernel/gate/Judge
- **Side-effects** — ART must never execute tools or external actions itself; pure verdict + logging
- **Protocol-specific logic** — no MCP/REST/gRPC specifics; ART knows actions, not transports
- **Anthropomorphic/ToM speculation** — no reasoning about feelings/consciousness; that's F9/F10 territory
- **Kernel overrule of Floor verdicts** — ART is advisory only; the gate has final say

### SUNAT (strongly recommended — losing these weakens ART)

- **BlastRadius-aware downgrade rules** — DEFAULT_OBSERVE/SABAR semantics for safe downgrades
- **Confidence/trust-level bands** — using `trust_level="evidence"/"unknown"` and `actor_verified` to bias decisions
- **Config write-lock awareness** — treating config-write ops as IRREVERSIBLE by default in reflex
- **Reflexion-style self-reflection text** — storing short textual reasons for failures in Library

### HARUS (permissible — implementation details, can evolve)

- Exact lifecycle state names (can rename/sub-state as long as semantics hold)
- Data store / RAG backend (Postgres, Redis, in-memory — engineering trade-off)
- Scoring function internals (how failure count + drift frequency + blast_radius combine into verdict)
- How SABAR is surfaced to agents (can choose protocol-specific surface)

### MAKRUH (allowed but undesirable — fix when possible)

| Item | Status | Action |
|------|--------|--------|
| ToolState hardcoded TRUSTED in gate bridge | MAKRUH-NOW | W2 `art_registry.py` fixes |
| 3 bypass paths (kernel_router, rest_routes, shell_forge) | MAKRUH-NOW | HOLD-1 migration fixes |
| MIND not wired into execution path | BY-DESIGN | W3 — feeds JUDGE 888, advisory only |
| Library write atomicity unverified | MAKRUH-CHECK | audit `art_library.py` record() path |
| Silent downgrades without Library explanations | MAKRUH-AVOID | always write ArtReason to Library on non-PROCEED |

---

## Boundaries (what touches what)

```
                        ┌─────────────────────┐
                        │   ART (horizontal)  │
                        │   art.py ≤500 lines │
                        │   art_library.py    │
                        │   art_mind/ (W3)    │
                        └────────┬────────────┘
                                 │ advisory only (Gate 2.5)
                                 ▼
┌─────────────────────────────────────────────────────┐
│                 pre_execution_gate                   │
│  Gate 1→2→2.5(ART)→3→3.5→4→5→...→15               │
│  Fails CLOSED. Only path to tool execution.         │
└────────────────────────┬────────────────────────────┘
                         │ binding verdict
                         ▼
┌─────────────────────────────────────────────────────┐
│              Kernel (F1-F13 sovereign)              │
│  Floor enforcement · Judge (888) · Vault (999)     │
│  Human veto (F13) is FINAL.                        │
└─────────────────────────────────────────────────────┘
```

**Canonical path:** Agent → Sense(111) → Mind(333) → Judge(888) → Forge(666) → Vault(999)
**ART sits at Gate 2.5** — between manifest check and Floor escalation. Advisory. Lightweight. Stateless.

---

## Anti-Patterns (what this doctrine prevents)

1. **"ART as second kernel"** — HARAM. ART has no Floor enforcement, no irreversibility gating, no sovereign authority. ART is tool-history + lifecycle + fast-screen only.

2. **"Skip ART, Floors are enough"** — misses the point. Floors tell you what's *legal*. ART tells you what's *wise* given the tool's history. Both matter.

3. **"ART should enforce Floors too"** — HARAM. Floor enforcement in ART creates conflicting authority. Exactly one path HOLDS: the kernel.

4. **"ART is the safety layer"** — wrong framing. ART is the *tool-discipline* layer. Safety is the kernel's job. ART reduces dumb tool loops; it does not replace constitutional judgment.

---

## Companion Documents

- `/root/forge_work/ART-BLUEPRINT-2026-06-21.md` — canonical reference (supersedes all prior ART docs)
- `/root/forge_work/ART-INIT-PROMPT-2026-06-21.md` — system prompt for ART-capable agents
- `/root/arifOS/arifosmcp/runtime/art.py` — the reflex (≤500 lines, HOT path)
- `/root/arifOS/arifosmcp/runtime/pre_execution_gate.py` — the bridge (Gate 2.5)
- `/root/arifOS/arifosmcp/runtime/agent_loop.py` — the canonical loop
- `/root/arifOS/CLAUDE.md` — kernel loading sequence + conventions

---

*DITEMPA BUKAN DIBERI — The doctrine is forged, not given. 999 SEAL ALIVE.*
