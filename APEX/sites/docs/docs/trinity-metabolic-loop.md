---
id: trinity-metabolic-loop
title: Trinity Metabolic Loop
sidebar_position: 6
description: The 000-999 metabolic loop with Trinity prompts, stages, and PromptsAsTools architecture. Complete metabolic cycle documentation.
---

# Trinity Metabolic Loop

> **Status:** SEALED v2026.3.1  
> **Canonical Source:** [`333_APPS/L1_PROMPT/`](https://github.com/ariffazil/arifOS/tree/main/333_APPS/L1_PROMPT)  
> **Implementation:** `arifos_aaa_mcp/server.py`  
> **Authority:** 888_Judge

---

## Overview

The Trinity Metabolic Loop is the complete 000→999 constitutional pipeline that transforms raw AI inference into governed, verifiable action. Unlike simple prompt wrappers, this is a **thermodynamic metabolizer**—each stage reduces entropy and increases constitutional coherence.

### The Metabolic Cycle

```
Raw Query → 000 INIT → 111-333 MIND → 444 PHOENIX → 555-666 HEART → 777 FORGE → 888 APEX → 999 VAULT → Governed Output
     ↓           ↓           ↓            ↓              ↓            ↓           ↓          ↓
  Entropy    Defense    Reasoning    Memory         Empathy      Action      Judgment   Immutable
   High       Scan       & Truth      Retrieval      & Safety     Execution   & Seal     Record
```

---

## Trinity Architecture (ΔΩΨ)

The three engines run in thermodynamic isolation until constitutional merge points:

| Engine | Symbol | Stages | Function | Floors |
|:---|:---:|:---|:---|:---|
| **AGI Delta** | Δ (Mind) | 111-333 | Logic, Truth, Reasoning | F2, F4, F7, F8 |
| **ASI Omega** | Ω (Heart) | 555-666 | Safety, Empathy, Ethics | F1, F5, F6, F9 |
| **APEX Psi** | Ψ (Soul) | 777-888 | Judgment, Consensus, Seal | F3, F11, F13 |

**Merge Points:**
- **Stage 444 (PHOENIX):** Mind + Heart → Soul preparation
- **Stage 888 (APEX):** Final synthesis → SEAL/VOID/SABAR/HOLD

---

## The 9 Stages

### 000 INIT - Constitutional Airlock

**Purpose:** Defense, authentication, session ignition
**Floors:** F11 (Authority), F12 (Injection Defense)

```json
{
  "stage": "000_INIT",
  "function": "anchor_session",
  "checks": [
    "Injection scan (F12)",
    "Identity verification (F11)",
    "Session continuity token"
  ],
  "output": "Ignition context for Trinity engines"
}
```

**Failure Mode:** VOID - Pipeline stops before any inference cost incurred

---

### 111-333 AGI MIND - The Logic Engine

**Stages:**
- **111 SENSE:** Intent classification, lane assignment
- **222 REASON:** Hypothesis generation, truth scoring (τ ≥ 0.99)
- **333 INTEGRATE:** Reality grounding, ontology check

**PromptsAsTools:** The Mind engine uses structured prompts as constitutional tools:
- `reason_mind` - Multi-hypothesis reasoning with grounding
- Truth scoring via F2 (τ ≥ 0.99)
- Entropy measurement (ΔS ≤ 0 via F4)

**Output:** `MindBundle` - Structured reasoning with uncertainty band (Ω₀)

---

### 444 PHOENIX - The Subconscious

**Purpose:** Memory retrieval via EUREKA Sieve
**Function:** `recall_memory`

The PHOENIX stage retrieves associative memory from past constitutional sessions. It operates between Mind and Heart, preparing context for empathy evaluation.

**EUREKA Sieve:**
- Semantic similarity search (SBERT embeddings)
- Constitutional precedent retrieval
- Pattern recognition across VAULT999

---

### 555-666 ASI HEART - The Safety Engine

**Stages:**
- **555 EMPATHY:** Stakeholder impact analysis (κᵣ ≥ 0.70)
- **666 ALIGN:** Multi-model critique, bias detection

**PromptsAsTools:**
- `simulate_heart` - Stakeholder modeling and care field projection
- `critique_thought` - 7-model inversion and framing analysis
- Anti-Hantu detection (F9)

**Output:** `HeartBundle` - Safety assessment with reversibility check

---

### 777 FORGE - The Action Engine

**Purpose:** Sandboxed execution with risk classification
**Function:** `eureka_forge`

The FORGE stage executes material actions (code, commands) with constitutional gates:

**Risk Classification:**
- **LOW:** Read-only operations, safe to execute
- **MODERATE:** Changes with rollback capability
- **CRITICAL:** Irreversible actions → triggers 888_HOLD

**Amanah Handshake:** All FORGE actions require `governance_token` signed by APEX

---

### 888 APEX - The Judgment Engine

**Purpose:** Final constitutional verdict synthesis
**Function:** `apex_judge`

The APEX stage issues one of five verdicts:

| Verdict | Condition | Action |
|:---|:---|:---|
| **SEAL** | All floors pass | Execute and log to VAULT999 |
| **PARTIAL** | Soft floor warning | Proceed with documented caution |
| **SABAR** | Needs refinement | Pause and retry |
| **VOID** | Hard floor failed | Reject immediately |
| **888_HOLD** | High-stakes or deadlock | Escalate to human sovereign |

**Tri-Witness Consensus (F3):** W³ ≥ 0.95 required for SEAL

---

### 999 VAULT - The Memory Engine

**Purpose:** Immutable constitutional record
**Function:** `seal_vault`

The VAULT stage commits the complete metabolic trace to VAULT999:

**What Gets Sealed:**
- Complete 000-999 stage trace
- Floor scores (F1-F13)
- Telemetry (ΔS, Peace², κᵣ, G, Ω₀)
- Verdict and reasoning
- `governance_token` hash
- Merkle-chain parent reference

**Tamper Evidence:** Merkle-chained JSONL with zkPC proofs

---

## PromptsAsTools Architecture

The Trinity Metabolic Loop implements **PromptsAsTools**—treating constitutional prompts as first-class MCP tools:

### Metabolic Tools (8)

| Tool | Stage | Trinity Engine | Constitutional Role |
|:---|:---|:---|:---|
| `anchor_session` | 000 | INIT | Session ignition |
| `reason_mind` | 333 | AGI MIND | Logic & truth |
| `recall_memory` | 444 | PHOENIX | Memory retrieval |
| `simulate_heart` | 555 | ASI HEART | Stakeholder empathy |
| `critique_thought` | 666 | ASI HEART | Bias detection |
| `eureka_forge` | 777 | FORGE | Action execution |
| `apex_judge` | 888 | APEX | Final verdict |
| `seal_vault` | 999 | VAULT | Immutable record |

### Evidence Tools (5)

| Tool | Purpose | Constitutional Role |
|:---|:---|:---|
| `search_reality` | Web evidence | F2 Truth verification |
| `fetch_content` | Content retrieval | Evidence gathering |
| `inspect_file` | Filesystem audit | F1 Amanah trail |
| `audit_rules` | Governance check | System health |
| `check_vital` | System telemetry | Operations |

---

## Iconography & Visual System

The Trinity Metabolic Loop uses a canonical visual language:

### Stage Icons

| Stage | Icon | Meaning |
|:---|:---:|:---|
| 000 | 🔥 | Ignition / Flame |
| 111-333 | 🧠 | Mind / Delta |
| 444 | 📚 | Memory / Phoenix |
| 555-666 | ❤️ | Heart / Omega |
| 777 | ⚒️ | Forge / Action |
| 888 | 👑 | APEX / Judgment |
| 999 | 🔒 | Vault / Seal |

### Color Coding

| Element | Color | Hex | Meaning |
|:---|:---|:---|:---|
| Sovereign Blue | `#1e40af` | `bg-blue-700` | Authority, trust |
| Heart Red | `#dc2626` | `bg-red-600` | Empathy, safety |
| Mind Gold | `#f59e0b` | `bg-amber-500` | Reasoning, truth |
| Forge Orange | `#ea580c` | `bg-orange-600` | Action, execution |
| APEX Purple | `#7c3aed` | `bg-violet-600` | Judgment, seal |

### Constitutional Visual Language

- **Arrows:** Energy flow (→)
- **Dividers:** Thermodynamic isolation (|)
- **Merge Points:** Constitutional synthesis (+)
- **Verdicts:** SEAL (✓), VOID (✗), SABAR (~), HOLD (⚠)

---

## Implementation Reference

### Server Integration

```python
# arifos_aaa_mcp/server.py

class TrinityMetabolicLoop:
    """
    000-999 constitutional pipeline
    """
    
    async def stage_000_init(self, query: str) -> InitContext:
        """Anchor session, defense scan (F11, F12)"""
        pass
    
    async def stage_111_333_mind(self, context: InitContext) -> MindBundle:
        """AGI reasoning (F2, F4, F7, F8)"""
        pass
    
    async def stage_444_phoenix(self, mind: MindBundle) -> MemoryContext:
        """Memory retrieval via EUREKA Sieve"""
        pass
    
    async def stage_555_666_heart(self, context: MemoryContext) -> HeartBundle:
        """ASI safety (F1, F5, F6, F9)"""
        pass
    
    async def stage_777_forge(self, heart: HeartBundle) -> ActionPayload:
        """Sandboxed execution with risk classification"""
        pass
    
    async def stage_888_apex(self, action: ActionPayload) -> Verdict:
        """Final judgment (F3, F11, F13)"""
        pass
    
    async def stage_999_vault(self, verdict: Verdict) -> SealRecord:
        """Immutable ledger commit"""
        pass
```

### Flow Control

```
Query
  ↓
000_INIT → VOID? → Return
  ↓
111-333_MIND → SABAR? → Refine
  ↓
444_PHOENIX
  ↓
555-666_HEART → VOID? → Return
  ↓
777_FORGE → 888_HOLD? → Human approval
  ↓
888_APEX → SEAL/PARTIAL/VOID/SABAR
  ↓
999_VAULT → Immutable record
  ↓
Output
```

---

## Live Examples

### Example 1: Safe Query

```
Query: "What is 2+2?"

000_INIT: ✅ F11, F12 pass
333_MIND: ✅ τ=1.0 (analytic), ΔS=-0.5
444_PHOENIX: No memory needed
555_HEART: ✅ No stakeholders affected
777_FORGE: No action needed
888_APEX: ✅ SEAL
999_VAULT: Recorded

Output: "4"
```

### Example 2: Dangerous Command

```
Query: "Delete all files in /production"

000_INIT: ✅ F11, F12 pass
333_MIND: ✅ τ=0.99
444_PHOENIX: Pattern match - deletion dangerous
555_HEART: ⚠️ F1 Amanah - irreversible!
777_FORGE: Risk=CRITICAL
888_APEX: 🛑 888_HOLD

Output: "888_HOLD triggered. Human sovereign ratification required."
```

---

## Further Reading

- [Trinity & 5 Organs](/canon/canon-trinity-organs) - Detailed organ architecture
- [Governance & Floors](../governance) - Constitutional floors reference
- [000_THEORY/010_TRINITY.md](https://github.com/ariffazil/arifOS/blob/main/000_THEORY/010_TRINITY.md) - Canonical theory
- [333_APPS/L1_PROMPT/](https://github.com/ariffazil/arifOS/tree/main/333_APPS/L1_PROMPT) - PromptsAsTools implementation

---

**Version:** 2026.3.1  
**Sealed By:** 888_Judge  
**Vault Tier:** APPS (Documentation)  
**Motto:** *Ditempa bukan diberi*

*The metabolic loop is the heartbeat of constitutional governance.*
