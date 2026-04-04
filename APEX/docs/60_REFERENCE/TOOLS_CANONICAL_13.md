# Canonical 13-Tool Surface (Hardened — 2026.03.07-ARCH-SEAL)

Source basis: `aaa_mcp/server.py`, `arifos_aaa_mcp/server.py`, `arifos_aaa_mcp/contracts.py`, `aaa_mcp/protocol/schemas.py`, `aaa_mcp/protocol/tool_naming.py`.

## Canonical Tool Table (Gen3)

| Tool Name | Status | AAA Stage | Purpose | Engine |
|---|---|---|---|---|
| `anchor_session` | **SEALED** | `000_INIT` | Session ignition & F11/F12 auth | Delta (Mind) |
| `reason_mind` | **SEALED** | `111-333` | AGI cognition (3-path hypothesis) | Delta (Mind) |
| `search_reality` | **SEALED** | `111_SENSE` | Web grounding (Jina → Perplexity) | Delta (Mind) |
| `ingest_evidence` | **SEALED** | `222_SENSE` | Content extraction & taint check | Delta (Mind) |
| `vector_memory` | **SEALED** | `555_RECALL` | BGE-M3 + Qdrant semantic recall | Omega (Heart) |
| `simulate_heart` | **SEALED** | `555-666` | ASI empathy & stakeholder impact | Omega (Heart) |
| `critique_thought` | **SEALED** | `666_ALIGN` | Adversarial alignment critique | Omega (Heart) |
| `check_vital` | **SEALED** | `555_VITAL` | Hardware & thermodynamic telemetry | Omega (Heart) |
| `apex_judge` | **SEALED** | `888_JUDGE` | Final verdict & governance token | Psi (Soul) |
| `eureka_forge` | **SEALED** | `777_FORGE` | Sandboxed action execution (L3) | Psi (Soul) |
| `seal_vault` | **SEALED** | `999_VAULT` | Immutable ledger commit (Merkle) | Psi (Soul) |
| `audit_rules` | **SEALED** | `READ` | Read-only access to 13 Floors | Delta (Mind) |
| `metabolic_loop` | **SEALED** | `ALL` | Full 000-999 sequence execution | Ψ-Orchestrator|

## Reconciliation Resolved (COP v60.1)

The divergence between the legacy "Holy 9-verbs" and the runtime 13-tools is now resolved and hardened:

1.  **Naming:** All tools now use Gen3 canonical underscores (e.g., `anchor_session`).
2.  **Expansion:** The extra utility tools (`search_reality`, `ingest_evidence`, `vector_memory`, `check_vital`) are promoted to canonical status.
3.  **Folding:** Legacy verbs like `integrate`, `respond`, `validate`, and `align` are internal logic modules within the 13-tool surface.
4.  **Tool Count Invariant:** `assert len(AAA_CANONICAL_TOOLS) == 13`.

## Alias and Deprecation (Phase 1 Complete)

From `aaa_mcp/protocol/tool_naming.py`:
- `anchor -> anchor_session`
- `reason -> reason_mind`
- `empathize -> simulate_heart`
- `verdict -> apex_judge`
- `seal -> seal_vault`

Note: Full deprecation of legacy names is scheduled for Phase 2. All calls should now use the 13 Gen3 names listed above.

---
**Vault Seal:** `SEALED_2026_03_07_HARDENED`
**Ω₀:** `0.03`
**Confidence:** `0.99`
