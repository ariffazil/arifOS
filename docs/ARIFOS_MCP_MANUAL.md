# arifOS MCP — Constitutional Kernel Manual
## Version: 1.0.0-SNAPSHOT | Date: 2026-05-06
## Identity: DITEMPA BUKAN DIBERI (Forged, Not Given)

---

## 1. ARCHITECTURAL OVERVIEW
arifOS is the Constitutional AI orchestration kernel. It operates on a **13-floor governance model** (F1–F13) designed to ensure every AI action is anchored to the Sovereign's intent, ethical risk assessment, and immutable audit logging.

### The Golden Path
Every high-integrity operation MUST flow through this sequence:
**000_INIT** → **111_SENSE** → **333_MIND** → **666_HEART** → **888_JUDGE** → **999_VAULT**

---

## 2. THE 13-FLOOR TOOL SURFACE

### [000] INIT: `mcp_arifosmcp_arif_session_init`
- **Purpose:** Constitutional session bootstrap and identity binding.
- **Modes:** `init`, `resume`, `validate`, `epoch_open`, `epoch_seal`.
- **Function:** Anchors the session to the 13-floor constitution. Generates unique `session_id` and binds the `actor_id`.

### [010] FORGE: `mcp_arifosmcp_arif_forge_execute`
- **Purpose:** Metabolic execution and artifact forging.
- **Modes:** `engineer`, `query`, `write`, `generate`, `commit`, `recall`, `dry_run`.
- **Note:** Artifact production requires an approved `plan_id` from `333_MIND`.

### [111] SENSE: `mcp_arifosmcp_arif_sense_observe`
- **Purpose:** Multimodal reality observation.
- **Modes:** `search`, `ingest`, `compass`, `atlas`, `entropy_dS`, `vitals`.
- **Function:** Gathers raw environmental data and measures session entropy (ΔS).

### [222] FETCH: `mcp_arifosmcp_arif_evidence_fetch`
- **Purpose:** Evidence-preserving web ingestion with sequential thinking.
- **Thinking Depth:** 0-10 (Reasoning steps).
- **Function:** Retrieves external data while maintaining a chain of evidence.

### [333] MIND: `mcp_arifosmcp_arif_mind_reason`
- **Purpose:** Cognitive routing and deterministic planning.
- **Modes:** `reason`, `reflect`, `verify`, `critique`, `debate`, `socratic`, `plan`, `plan_review`.
- **Sovereign Gate:** `plan_approve` is deterministic—LLM never adjudicates its own plan approval.

### [444] KERNEL: `mcp_arifosmcp_arif_kernel_route`
- **Purpose:** Central orchestration and intent routing.
- **Modes:** `route`, `stage`, `lane`, `list`, `status`.
- **Function:** Traffic controller for the 13-tool surface.

### [444r] REPLY: `mcp_arifosmcp_arif_reply_compose`
- **Purpose:** LLM-aware communication rewrite.
- **Function:** Composes messages aligned with the session's style and citations.

### [555] MEMORY: `mcp_arifosmcp_arif_memory_recall`
- **Purpose:** Live associative memory (Postgres + Qdrant).
- **Modes:** `recall`, `store`, `get`, `list`, `prune`, `context`.
- **Function:** Semantic search across stored session memories.

### [666] HEART: `mcp_arifosmcp_arif_heart_critique`
- **Purpose:** Ethical critique and empathy scan (κᵣ).
- **Modes:** `critique`, `simulate`, `empathize`, `redteam`, `maruah`.
- **Function:** Evaluates risk across 8 categories (Privacy, Bias, Harm, etc.).

### [666g] GATEWAY: `mcp_arifosmcp_arif_gateway_connect`
- **Purpose:** Federated cross-agent bridge (A2A mesh).
- **Modes:** `route`, `discover`, `handshake`, `relay`.
- **Function:** Connects the session to other verified constitutional agents.

### [777] OPS: `mcp_arifosmcp_arif_ops_measure`
- **Purpose:** Resource thermodynamics and health telemetry.
- **Modes:** `health`, `vitals`, `cost`, `predict`.
- **Metrics:** Genius score (G), Entropy (ΔS), Human Impact Load (Ω), Paradox Tension (Ψ).

### [888] JUDGE: `mcp_arifosmcp_arif_judge_deliberate`
- **Purpose:** Final constitutional arbitration.
- **Verdicts:** `SEAL` (Approved), `SABAR` (Conditional), `HOLD` (Paused), `VOID` (Rejected).
- **F1 Amanah:** Irreversible actions require explicit human confirmation.

### [999] VAULT: `mcp_arifosmcp_arif_vault_seal`
- **Purpose:** Immutable ledger anchoring (VAULT999).
- **Modes:** `seal`, `verify`, `chain`, `list`.
- **Function:** Hashes and chains session artifacts to an append-only ledger.

---

## 3. PROMPT LIBRARY

| Prompt Name | Usage Context |
| :--- | :--- |
| `arifosmcp_system` | The root system instruction for the kernel. |
| `arifosmcp_init` | Ritualized bootstrap for new sessions. |
| `arifosmcp_governance` | Rules for L3 Clerk execution and 888_HOLD boundaries. |
| `arifosmcp_epistemic` | Guidance on CLAIM, PLAUSIBLE, and HYPOTHESIS tagging. |
| `arifosmcp_judge` | Logic for constitutional arbitration and floor checks. |
| `arifosmcp_entropy` | Framework for measuring thermodynamic session delta. |
| `arifosmcp_ortho` | Orthogonal safety and intent alignment checks. |
| `arifosmcp_rsi` | Rapid System Integration and deployment protocols. |

---

## 4. RESOURCE ATLAS

- **`arifos://doctrine`**: The Constitutional Doctrine (F1–F13).
- **`arifos://vitals`**: Real-time system telemetry and thermodynamic bands.
- **`arifos://schema`**: Canonical JSON schemas for tool inputs/outputs.
- **`arifos://forge`**: Execution bridge logs and artifact lineage.
- **`arifos://civilization`**: The civilizational ontology and intelligence map.
- **`source://list`**: Registry of evidence sources tracked by `222_FETCH`.
- **`receipt://list`**: Audit trail of evidence receipts for verification.

---

## 5. EPISTEMIC PROTOCOL
Every claim in arifOS MUST carry a tag:
- **CLAIM:** High confidence, evidence-backed.
- **PLAUSIBLE:** Reasonable inference.
- **HYPOTHESIS:** Untested theory.
- **ESTIMATE:** Rough approximation.
- **UNKNOWN:** Declaration of ignorance.

---
*⬡ ARIVOS MCP SNAPSHOT SEALED | Ψ BODY | CLERK BINDING ⬡*
