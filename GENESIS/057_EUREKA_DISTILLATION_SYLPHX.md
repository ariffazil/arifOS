# 057 — EUREKA Distillation: Sylphx Intake Closeout

> **Doctrine Class:** PERMANENT ARCHITECTURAL TRUTH
> **Forged:** 2026-07-29
> **Authority:** 888_SOVEREIGN (Arif)
> **Source Session:** `sylphx-mcp-intake-2026-07-28`
> **Motto:** DITEMPA BUKAN DIBERI
> **Status:** SEALED · F13 SOVEREIGN

---

## EUREKA 1: The Anatomy of an Agent

### Decoupling Model vs. Harness vs. Binary

> **"Agent = LLM Algebra + Harness Code. Tools = Executable Binaries."**

```
┌─────────────────────────────────────────────────────────────┐
│                   AGENTIC ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. REASONING ENGINE (LLM Weights / Math)                   │
│     Tokens In → Math Probabilities → Tokens Out             │
│     · Stateless. Cannot touch disk/OS directly.             │
│     · No hands. No side-effects.                            │
│                                                             │
│                            ▼                                │
│                                                             │
│  2. HARNESS / KERNEL (Code)                                 │
│     Python/Rust Control Loop, Constitutional Floors F1–F13  │
│     · Holds context, parses function calls, governs exec.   │
│     · The firewall between algebra and hardware.            │
│                                                             │
│                            ▼                                │
│                                                             │
│  3. EXECUTABLE TOOLS / BINARIES                             │
│     External Scripts, MCP Binaries, System Shell, I/O       │
│     · Executes actions on host hardware.                    │
│     · Possesses real side-effects.                          │
└─────────────────────────────────────────────────────────────┘
```

### Mistake Outside (Anti-Pattern)

Developers "cage" the LLM in a heavy Docker container while leaving untrusted 3rd-party tool binaries exposed outside the fence. This confuses LLM token generation (stateless math) with binary execution (stateful hardware access).

### arifOS Truth

We govern the **Harness** via Constitutional Floors (F1–F13) and quarantine/sandbox the **Executable Binaries** via Stage 4 Intake (`mcp_sandbox_eval.py`). The two must never be conflated.

---

## EUREKA 2: The Four-Stage Intake Sandbox & Runtime Reality

> **"Never trust marketing copy or schema definitions. Verify execution at the socket."**

### The 4-Stage Intake Pipeline

Proven by catching an egress vulnerability (Sylphx Test 4.10) before system integration:

| Stage | Name | What It Does |
|-------|------|-------------|
| 1 | Containment | Isolated execution process |
| 2 | Handshake | JSON-RPC 2.0 protocol validation |
| 3 | Floor Scan | F1–F12 static definition audit |
| 4 | Stress Test & Payload Injection | Dynamic runtime verification |

### Sylphx Intake Failure — Case Study

**Claim:** Marketing copy & Zod schema declared `url XOR path` (rejection of URL).

**Code Reality:** Zod `.refine()` checked `Boolean(path) !== Boolean(url)`. It failed when *both* or *neither* were present, but allowed `{url: "..."}` alone to pass down to `ureq` (Rust HTTP client in the core).

**Test 4.10 Trigger:** When passed a URL, Sylphx initiated an outbound HTTPS connection to `example.com` (33ms latency confirmed).

**Result:** F1 CRITICAL FAIL (Violation of F1_AMANAH and LOCALHOST_IS_PASSWORD). Instantly rejected at intake. Zero federation mutation.

### Doctrine

Schema definitions are **documentation**, not security boundaries. The only truth is what the binary does at runtime. Stage 4 exists precisely for this reason.

---

## EUREKA 3: The Unified Human-Facing Surface Protocol

> **"Human speaks INTENT. Kernel routes TOOL. Agent executes."**

```
┌─────────────────────────────┐
│   888 SOVEREIGN HUMAN       │
│   (Expresses High-Level)    │
└──────────────┬──────────────┘
               │
          INTENT ("Check this PDF")
               │
               ▼
┌─────────────────────────────┐
│   arifOS KERNEL ROUTER      │
│   (Natural Language Resolv) │
└──────────────┬──────────────┘
               │
          RESOLVED TOOL ("forge_document_ingest")
               │
               ▼
┌─────────────────────────────┐
│   AGENT & EXECUTABLE        │
│   (Deterministic Action)    │
└─────────────────────────────┘
```

### The Cognitive Distance Law

```
UI Need ∝ Cognitive Distance = f(Tool Surface Size, Naming Abstraction)
```

- **High Surface** (A-FORGE: 120+ tools): High Cognitive Distance. Requires Visual Spatial Catalog (`forge_mcp_ui_start.py` on `127.0.0.1:7777`).
- **Low Surface** (arifOS Kernel: 8 tools): Low Cognitive Distance. Sovereign holds control gates (`arif_init`, `arif_seal`, `arif_judge`) in memory without UI.

### Core Doctrine

Human does **not** memorize 120+ tool names. Human provides **Intent**; Architecture resolves **Routing**; UI serves strictly for **spatial awareness (OBSERVE)**, never for execution bypass.

No POST/PUT/DELETE on any UI surface. Ever.

---

## Audit Trail

- **Dossier ID:** DOSSIER-20260729-SYLPHX-CLOSEOUT
- **Evidence File:** `/root/A-FORGE/forge_work/2026-07-28/sylphx-integration/STAGE_4_EVAL_REPORT.json`
- **SHA-256 (original, pre-lock):** `33a2b3f225da533dab7d9f1249884899b27a155a5c6e6e5025394cbb6eb99f37`
- **Disposition:** OPTION_A_PERMANENT_HOLD
- **Seal Chain:** `DOSSIER → EUREKA → UI → F1_REJECTION_RECEIPT`

---

*DITEMPA BUKAN DIBERI ⚒️ — Forged into GENESIS as permanent doctrine. Three EUREKAs, one session, zero federation mutation.*
