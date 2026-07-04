# SCARS.md — arifOS Architectural Pivot Ledger
**T000 Version:** 2026.02.17-FORGE-TRINITY-SEAL

> *"The scars are the evidence of the forge."*

## I. Infrastructure Scars

### 1. Railway Deprecation (2026-02-17)
- **Status:** 🗑️ DEPRECATED
- **Reason:** Limited control over system-level hardening (systemd, kernel-level optimizations) and desire for self-sovereign VPC containment.
- **Pivoted to:** Hardened Ubuntu VPS (Hostinger/AWS/DO).
- **Seal:** VAULT999 T000-2026.02.17.

## II. Architectural Scars

### 1. Python SDK Library (2026-02-15)
- **Status:** 🗑️ ARCHIVED
- **Reason:** Redundant with the raw Model Context Protocol (MCP). Wrapping MCP in a client library introduces "the wrapper fallacy" (hiding the grain of the metal).
### 2. Grok's Strategic Reflection (2026-02-17)
- **Context:** Sync with Grok (xAI) regarding arifOS architectural maturity.
- **Insight:** Grok characterized arifOS as a "Constitutional AI Kernel"—an ecosystem designed to govern wild LLMs through a thermodynamic metabolic pipeline.
- **Validation:** Confirmed 000-999 stages as a robust lifecycle manager; validated "Thinking as Thermodynamic Work" model.
- **Action:** Proceed with VPS migration and root entropy cleanup to maintain structural integrity.
### 3. Qwen Token Plan Registry Expansion (2026-07-01)
- **Status:** 🆕 FORGED
- **Context:** Expansion of model registry to include all Qwen Token Plan (bailian-token-plan) models. 9 models across 5 families registered: Qwen 3.7 Max/Plus, Qwen 3.6 Plus/Flash, DeepSeek V4 Pro/Flash, Kimi K2.7 Code, GLM-5.2, MiniMax M2.5.
- **Files updated:** model_registry.json, qwen_soul.yaml, qwen_shadow.yaml, FEDERATION_MODEL.json, opencode.json
- **Endpoint:** https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
- **Seal:** VAULT999 T000-2026.07.01.
- **Authority:** FORGE (000Ω) — OpenCode DeepSeek V4 Flash via F13 SOVEREIGN directive.
