---
type: Concept
tags: [architecture, governance, constitution, intelligence]
sources: [README.md, GEMINI.md]
last_sync: 2026-04-08
confidence: 1.0
---

# What is arifOS?

**arifOS** is a production-grade **Constitutional AI Governance System**. It is an open-source, MCP-native operating system designed to ensure that AI agents operate within human-defined ethical, physical, and logical bounds through a multi-layered enforcement architecture.

## The Core Philosophy: "Ditempa Bukan Diberi"

The motto, *Ditempa Bukan Diberi* (Forged, Not Given), reflects the belief that intelligence and governance must be rigorously developed and enforced, not merely assumed or granted.

### The "Air Gap" Principle

arifOS operationalizes this philosophy through a strict physical and logical separation:

- **Application Layer (AAA)**: A fluid, mutable interface for user interaction and service delivery.
- **Constitutional Kernel (CCC)**: An immutable, rigid core that enforces the 13 Floors.
- **Protocol Bridge (BBB)**: The secure, audited data transport between AAA and CCC.

## The Trinity Architecture (ΔΩΨ)

arifOS is organized around three interdependent rings (The Trinity/ΔΩΨ Architecture), ensuring a strict separation of powers across both **Layer** (AAA vertical) and **Engine** (horizontal governance):

### Layer Mapping (AAA Vertical Stack)

Per `TRINITY_ARCHITECTURE.md` (000_IGNITION canon):

- **Δ HUMAN (The Body / Epistemic)**: Identity, biography, scars. Who is building this? Why does it matter?

- **Ω APPS (The Mind / Implementation)**: Tools, code, execution. How do we implement the law?

- **Ψ THEORY (The Soul / Authority)**: Constitutional law, 13 Floors. What law governs all action?

### Engine Mapping (Governance Pipeline)

- **AGI Mind (The Architect)**: Analytical reasoning, logic, factuality. Stages 111 (SENSE) to 333 (ATLAS). Proposals only; zero execution authority.

- **ASI Heart (The Guardian)**: Safety, empathy, impact simulation. Stages 444 (ALIGN) to 666 (BRIDGE). Holds veto and SABAR power.

- **APEX Soul (The Judge)**: Judiciary layer. Stages 777 (EUREKA) to 999 (VAULT). Issues final verdicts (SEAL, VOID, SABAR, HOLD_888).

> [!NOTE]
> **Layer vs Engine distinction**: ΔΩΨ maps to AAA layers vertically; AGI/ASI/APEX are horizontal governance engines that execute *across* all layers. The Ω (APPS) layer hosts the AGI Mind implementation, but ASI Heart (safety) guards all layers.

## The 13 Constitutional Floors (F1-F13)

Every action processed by arifOS must pass through 13 safety floors. Key floors include:

- **F1 Amanah**: Reversibility and sacred trust.

- **F2 Truth**: Reality grounding and citation.

- **F3 Tri-Witness**: Triple-verifiable execution.

- **F4 Clarity**: Entropy reduction (ΔS ≤ 0).

- **F9 Ethics**: Measuring harm potential (C_dark < 0.30).

- **F11 Audit**: Immutable logging in VAULT999.

## The Metabolic Pipeline (000-999)

Requests flow through a 9-stage metabolic loop:

- **000_INIT**: Session anchoring.

- **111_SENSE**: Reality grounding.

- **333_MIND**: Constitutional evaluation.

- **444_ROUT**: Execution planning.

- **555_MEM**: Context retrieval (Vector memory).

- **666_HEART**: Safety critique.

- **777_OPS**: Resource/Thermodynamic estimation.

- **888_JUDGE**: Final verdict (SEAL, HOLD, VOID).

- **999_SEAL**: Immutable audit trail.

## Technology Stack

- **Primary Language:** Python 3.12+

- **Infrastructure:** FastAPI, FastMCP, Redis, PostgreSQL (Vault999), Qdrant/Chroma.

- **Inference:** Ollama (local LLM orchestration).

## Role-Based Permissions

- **A-ARCHITECT:** Read, Plan, Design only.

- **A-ENGINEER:** Read, Write, Edit (requires approval).

- **A-AUDITOR:** Read, Review, issue VOID verdicts.

- **A-VALIDATOR:** Authorized to Deploy and issue final SEALs.

Citations:

- [README.md](README.md) (Root documentation)

- [GEMINI.md](GEMINI.md) (Agent instructions)

- [Floors](Floors) (Detailed floor specs)
