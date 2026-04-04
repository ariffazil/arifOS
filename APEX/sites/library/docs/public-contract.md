---
id: public-contract
title: Public Contract
slug: /public-contract
description: Auto-generated arifOS public MCP contract for model-agnostic clients.
---

<!-- AUTO-GENERATED: edit arifosmcp/runtime/public_registry.py and rerun scripts/generate_public_contract_docs.py -->

# Public Contract

Runtime version: `2026.03.12-FORGED`

This page is generated from `arifosmcp.runtime.public_registry`. It is the only supported public/main MCP contract for model-agnostic clients.

## Public MCP Contract

- Public tools: `9`
- Protocol: `2025-11-25`
- Transports: `http`, `stdio`
- Public profile: `chatgpt` / `agnostic_public`

### Public Tools

| Tool | Stage | Role | Read-only | Description |
|------|-------|------|-----------|-------------|
| `arifOS_kernel` | `444_ROUTER` | Main orchestrator | no | The arifOS Intelligence Kernel. Runs the full metabolic reasoning pipeline (000-999) and governs high-stakes execution tasks. |
| `search_reality` | `111_SENSE` | Grounding | yes | Find real-world sources and factual grounding before reasoning. |
| `ingest_evidence` | `222_REALITY` | Ingestion | yes | Fetch or extract evidence from a URL, document, or file path. |
| `session_memory` | `555_MEMORY` | Continuity | no | Store, retrieve, or forget session context and reasoning artifacts. |
| `audit_rules` | `333_MIND` | Governance | yes | Inspect the 13 constitutional floors and verify governance logic. |
| `check_vital` | `000_INIT` | Telemetry | yes | Read system vitality, including thermodynamic budget and redacted capability map. |
| `open_apex_dashboard` | `888_JUDGE` | Visualizer | yes | Open the APEX constitutional dashboard for live metrics and trace visibility. |
| `bootstrap_identity` | `000_INIT` | Onboarding | no | Declare user identity and initiate session grounding (Onboarding). |
| `verify_vault_ledger` | `999_VAULT` | Auditor | yes | Verify the SHA-256 Merkle chain integrity of the VAULT999 immutable ledger. |

### Internal / Dev-only Stage Tools

These tools are available only in internal/dev-style profiles. They are not part of the public model-facing contract and should not be treated as stable external API.

| Tool | Status |
|------|--------|
| `init_anchor_state` | internal/dev-only |
| `integrate_analyze_reflect` | internal/dev-only |
| `reason_mind_synthesis` | internal/dev-only |
| `assess_heart_impact` | internal/dev-only |
| `critique_thought_audit` | internal/dev-only |
| `quantum_eureka_forge` | internal/dev-only |
| `apex_judge_verdict` | internal/dev-only |
| `seal_vault_commit` | internal/dev-only |

### Compatibility Mapping

| Legacy name | New public route | Status | Notes |
|-------------|------------------|--------|-------|
| `anchor_session` | `bootstrap_identity` | `removed` | Explicit onboarding moved to bootstrap_identity; one-call governed work moved to arifOS_kernel. |
| `reason_mind` | `arifOS_kernel` | `removed` | Reasoning is now internal to the kernel pipeline rather than a separate public step. |
| `recall_memory` | `session_memory` | `removed` | Public memory access is exposed only through session_memory operations. |
| `vector_memory` | `session_memory` | `removed` | Public memory operations were consolidated under session_memory. |
| `simulate_heart` | `arifOS_kernel` | `internal` | Heart analysis is still executed, but only as an internal kernel stage. |
| `critique_thought` | `arifOS_kernel` | `internal` | Critique remains available only inside the governed pipeline. |
| `eureka_forge` | `arifOS_kernel` | `internal` | Forge behavior is policy-gated inside the kernel; no standalone public tool. |
| `apex_judge` | `arifOS_kernel` | `internal` | Judgment is emitted by the kernel envelope rather than a public standalone step. |
| `seal_vault` | `arifOS_kernel` | `internal` | Vault sealing remains internal/dev-only and is not part of the public model-facing contract. |
| `fetch_content` | `ingest_evidence` | `removed` | Evidence intake is consolidated under ingest_evidence. |
| `inspect_file` | `ingest_evidence` | `removed` | Public file/document intake is consolidated under ingest_evidence. |
| `metabolic_loop` | `arifOS_kernel` | `deprecated` | Use arifOS_kernel as the only supported public kernel name. |
| `metabolic_loop_router` | `arifOS_kernel` | `deprecated` | Legacy internal alias retained only for compatibility profiles. |
| `init_anchor_state` | `bootstrap_identity` | `internal` | Stage tool remains available only in internal/dev profiles. |
| `integrate_analyze_reflect` | `arifOS_kernel` | `internal` | Stage tool remains available only in internal/dev profiles. |
| `reason_mind_synthesis` | `arifOS_kernel` | `internal` | Stage tool remains available only in internal/dev profiles. |
| `assess_heart_impact` | `arifOS_kernel` | `internal` | Stage tool remains available only in internal/dev profiles. |
| `critique_thought_audit` | `arifOS_kernel` | `internal` | Stage tool remains available only in internal/dev profiles. |
| `quantum_eureka_forge` | `arifOS_kernel` | `internal` | Stage tool remains available only in internal/dev profiles. |
| `apex_judge_verdict` | `arifOS_kernel` | `internal` | Stage tool remains available only in internal/dev profiles. |
| `seal_vault_commit` | `arifOS_kernel` | `internal` | Stage tool remains available only in internal/dev profiles. |

### Prompts

| Prompt | Target tool |
|--------|-------------|
| `arifos_kernel_prompt` | `arifOS_kernel` |
| `search_reality_prompt` | `search_reality` |
| `ingest_evidence_prompt` | `ingest_evidence` |
| `session_memory_prompt` | `session_memory` |
| `audit_rules_prompt` | `audit_rules` |
| `check_vital_prompt` | `check_vital` |
| `open_apex_dashboard` | `open_apex_dashboard` |
| `bootstrap_identity_prompt` | `bootstrap_identity` |

### Resources

| Resource | Description |
|----------|-------------|
| `canon://index` | High-level arifOS canon map. |
| `canon://tools` | Canonical public tool surface. |
| `canon://floors` | arifOS 13 constitutional floors. |
| `canon://metabolic-loop` | Public kernel flow and stages. |
| `governance://law` | Verdict hierarchy and floor invariants. |
| `eval://metabolic-workflows` | Standard 000-999 workflow recipes. |
| `eval://floors-thresholds` | Numeric thresholds for floors. |
| `schema://tools/input` | Canonical JSON Schema input specs for public tools. |
| `schema://tools/output` | RuntimeEnvelope output schema. |
| `schema://opex` | Epistemic intake schema. |
| `schema://apex` | Governance output schema. |
| `vault://latest` | Latest sealed VAULT entries. |
| `telemetry://summary` | Governance telemetry summary. |
| `runtime://capability-map` | Redacted capability and credential-class state. |
| `ui://apex/dashboard-v2.html` | Packaged APEX dashboard asset. |
