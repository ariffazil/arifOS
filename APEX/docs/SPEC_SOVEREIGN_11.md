# arifOS Sovereign-11 Specification (ABI v1.0)
**Version:** 2026.03.20-SOVEREIGN11  
**Status:** SEALED / VALIDATED  
**Architecture:** MGI Double Helix (Machine-Governance-Intelligence)

This document defines the canonical 11 Mega-Tool surface for the arifOS Model Context Protocol (MCP) kernel. Any client or agent interacting with this node must adhere to this mode-dispatch contract.

---

## 🏛️ The MGI Trinity Framework

All tools are grouped into three privilege rings:
1.  ⚖️ **Governance (G)**: Soul & Will. Enforces the 13 Floors (F1-F13).
2.  🧠 **Intelligence (I)**: Mind & Logic. Performs metabolic transformations.
3.  ⚙️ **Machine (M)**: Body & Senses. Provides material grounding and execution.

---

## ⚖️ GOVERNANCE LAYER (The Spine)

### 1. `init_anchor`
**Stage:** 000_INIT | **Trinity:** PSI Ψ  
**Description:** Establish or revoke a governed session identity. Required before all other actions.
- **Modes:**
    - `init`: Mint a new session token (`auth_context`). Requires `actor_id` and `intent`.
    - `revoke`: Kill a session. Requires `session_id` and `reason`.
    - `refresh`: Mid-session token rotation and continuity check.

### 2. `arifOS_kernel`
**Stage:** 444_ROUTER | **Trinity:** DELTA/PSI  
**Description:** Primary metabolic conductor. The "syscall" entry point for complex reasoning.
- **Modes:**
    - `kernel`: Execute the full 000-999 metabolic pipe. Requires `query`.
    - `status`: Diagnostic onboarding compass. Explains authority ladder and available tools.

### 3. `apex_soul`
**Stage:** 888_JUDGE | **Trinity:** PSI Ψ  
**Description:** Final authority for verdicts, defense, and escalation.
- **Modes:**
    - `judge`: Render SEAL/VOID decisions on candidate output.
    - `rules`: Inspect live thresholds of the 13 Floors.
    - `validate`: Technical/logical audit of engineering artifacts.
    - `hold`: Status check for pending human (F13) ratification.
    - `armor`: F12 injection and adversarial logic scanning.
    - `notify`: Push-channel for high-stakes 888_HOLD escalations.

### 4. `vault_ledger`
**Stage:** 999_VAULT | **Trinity:** PSI Ψ  
**Description:** Permanent decision recording and Merkle-chain integrity.
- **Modes:**
    - `seal`: Immutable commit of verdict + evidence to VAULT999.
    - `verify`: Full scan of the Merkle chain to detect tamper/drift.

---

## 🧠 INTELLIGENCE LAYER (The Mind)

### 5. `agi_mind`
**Stage:** 333_MIND | **Trinity:** DELTA Δ  
**Description:** Core reasoning and assembly engine.
- **Modes:**
    - `reason`: First-principles structured logic and hypothesis generation.
    - `reflect`: Metacognitive integration of session memory.
    - `forge`: One-shot assembly of implementation specifications.

### 6. `asi_heart`
**Stage:** 666_HEART | **Trinity:** OMEGA Ω  
**Description:** Ethical simulation and impact modeling.
- **Modes:**
    - `critique`: Adversarial audit for bias and "Hantu" logic.
    - `simulate`: Consequence modeling for world-model stability (Peace²).

### 7. `engineering_memory`
**Stage:** 555_MEMORY | **Trinity:** OMEGA Ω  
**Description:** Technical execution and semantic learning.
- **Modes:**
    - `engineer`: Material system actions (code/shell/file) via AgentZero.
    - `recall`: Semantic context retrieval from session history.
    - `write`: Commitment of learned facts back to the operational store.
    - `generate`: Local LLM code generation (e.g. via Ollama).

---

## ⚙️ MACHINE LAYER (The Body)

### 8. `physics_reality`
**Stage:** 111_SENSE | **Trinity:** DELTA Δ  
**Description:** Fact acquisition from the external "Earth-Witness".
- **Modes:**
    - `search`: Web-based evidence acquisition.
    - `ingest`: Normalization of unstructured files/URLs into structured evidence.
    - `compass`: Quick grounding check for factual claims.
    - `atlas`: Synthesis of multiple EvidenceBundles into a grounding map.

### 9. `math_estimator`
**Stage:** 444_ROUTER | **Trinity:** DELTA Δ  
**Description:** Quantitative vitals and thermodynamic budgeting.
- **Modes:**
    - `cost`: Token and compute cost estimation for proposed paths.
    - `health`: Raw OS telemetry (CPU/RAM/Disk).
    - `vitals`: Constitutional telemetry (ΔS, Peace², G★).

### 10. `code_engine`
**Stage:** M-3_EXEC | **Trinity:** ALL  
**Description:** OS-level hygiene and observation. Defaults to `dry_run=True`.
- **Modes:**
    - `fs`: Filesystem inspection and structure mapping.
    - `process`: Active process listing and resource monitoring.
    - `net`: Network interface and connectivity integrity checks.
    - `tail`: Real-time log filtering and audit.
    - `replay`: Forensic replay of session traces from history.

### 11. `architect_registry`
**Stage:** M-4_ARCH | **Trinity:** DELTA Δ  
**Description:** Tool surface discovery and resource intake.
- **Modes:**
    - `register`: Query the currently exposed public MCP surface.
    - `list`: Enumerate available arifOS documentation and data resources.
    - `read`: Retrieve the content of a specific resource URI.

---

## ⚖️ Safety & Compliance

1.  **Fail-Closed**: All tools default to `dry_run=True`. Irreversible actions require `allow_execution=True` AND a passing F13 Sovereign gate.
2.  **Universal Envelope**: All calls must use the standard request envelope:
    `{ tool, mode, payload, auth_context, risk_tier, dry_run }`.
3.  **Identity Continuity**: Mid-chain tool calls must propagate the `auth_context` to maintain the F11 authority ladder.

*DITEMPA BUKAN DIBERI — SEALED 2026.03.20*
