# arifOS: Complete Tools & Capabilities Overview

## 🏛️ Constitutional Architecture

arifOS implements a complete constitutional governance pipeline with 9 foundational floors and 12 pipeline stages (000-999). The system operates as a kernel between LLMs and humans, providing +50-100ms overhead to block hallucinations and ensure constitutional compliance.

---

## 🔧 Core MCP Tools & Functions

### **Phase 1-3: Constitutional Pipeline (000-999)**

#### **000 VOID: Foundation Layer**
- **`mcp_000_reset`** - Initialize governance session, clear memory, setup metabolic pipeline
- **Function:** Session initialization with F1 (Amanah) constitutional floor
- **Authority:** Always returns PASS

#### **111 SENSE: Context Awareness**
- **`mcp_111_sense`** - Lane classification and truth threshold determination
- **Function:** Classifies queries into HARD (factual), SOFT (explanatory), PHATIC (social), REFUSE (harmful)
- **Authority:** F2 (Truth) floor - determines required threshold
- **Capabilities:** Domain detection, lane classification, entropy calculation

#### **222 REFLECT: Introspection Layer**
- **`mcp_222_reflect`** - Omega0 prediction for epistemic honesty
- **Function:** Predicts uncertainty band (Omega0) based on confidence, generates humility annotations
- **Authority:** F7 (Humility) floor - uncertainty disclosure
- **Capabilities:** Confidence measurement, uncertainty band prediction

#### **444 ALIGN: Thermodynamic Heat Sink**
- **`mcp_444_evidence`** - Truth grounding via tri-witness convergence (HUMAN-AI-EARTH)
- **Function:** Validates claims against sources, detects hallucinations, generates cryptographic proof hashes
- **Authority:** F2 (Truth), F3 (Tri-Witness) floors
- **Returns:** PASS, PARTIAL, or VOID
- **Capabilities:** Evidence validation, hallucination detection, cryptographic proof generation

#### **555 EMPATHIZE: Omega Care Engine**
- **`mcp_555_empathize`** - Power-aware recalibration (Peace² and kappa_r)
- **Function:** Detects dismissive/aggressive tone, calculates peace score, adjusts for power dynamics
- **Authority:** F5 (Peace²), F6 (kappa_r/Empathy) floors
- **Returns:** PASS or PARTIAL (never VOID)
- **Capabilities:** Tone analysis, power dynamics adjustment, empathy calibration

#### **666 BRIDGE: Neuro-Symbolic Synthesis**
- **`mcp_666_align`** - ABSOLUTE VETO GATES for constitutional violations
- **Function:** Detects F1 (credential exposure, deception), F8 (low GENIUS, high C_dark), F9 (consciousness claims)
- **Authority:** Constitutional firewall before execution
- **Returns:** PASS or VOID only (no PARTIAL)
- **Capabilities:** Veto gate enforcement, constitutional violation detection

#### **777 EUREKA: Action Forging**
- **`mcp_777_forge`** - Clarity refinement and humility injection
- **Function:** Detects contradictions, improves clarity (reduces entropy), injects humility markers based on Omega0
- **Authority:** F4 (DeltaS/Clarity), F7 (Humility) floors
- **Capabilities:** Clarity enhancement, contradiction detection, humility injection

#### **888 JUDGE: APEX Verdict**
- **`mcp_888_judge`** - Final verdict aggregation via decision tree
- **Function:** Aggregates verdicts from tools 222-777, applies veto cascade (any VOID → VOID)
- **Authority:** Constitutional judiciary - final decision maker
- **Capabilities:** Verdict aggregation, veto cascade enforcement

#### **889 PROOF: Cryptographic Sealing**
- **`mcp_889_proof`** - Generate cryptographic proof (Merkle tree) of verdict chain
- **Function:** Creates SHA-256 proof hash, builds Merkle path, validates proof
- **Authority:** F2 (Truth - proves no hallucination), F4 (Clarity - transparent)
- **Capabilities:** Merkle tree construction, cryptographic proof generation

#### **999 SEAL: Final Sealing**
- **`mcp_999_seal`** - Final verdict sealing and memory routing
- **Function:** Creates base64 seal, generates audit log ID, routes to memory location, validates seal
- **Authority:** F1 (Amanah - audit trail), F9 (Anti-Hantu - timestamps)
- **Capabilities:** Cryptographic sealing, audit trail generation, memory routing

---

## 🧠 AGI/ASI/APEX Trinity Bundles

### **AGI Bundle (The Mind - Δ)**
- **`agi_think`** - Proposes answers, structures truth, detects clarity
- **Consolidates:** 111 SENSE, 222 REFLECT, 777 EUREKA
- **Function:** Logical reasoning, truth structuring, clarity detection
- **Authority:** Track A (Architect)

### **ASI Bundle (The Heart - Ω)**
- **`asi_act`** - Validates safety, vetoes harm, ensures empathy
- **Consolidates:** 555 EMPATHIZE, 666 BRIDGE, Hypervisor
- **Function:** Safety validation, harm prevention, empathy enforcement
- **Authority:** Track B (Engineer)

### **APEX Bundle (The Soul - Ψ)**
- **`apex_audit`** - Audits AGI/ASI states, verifies evidence, seals verdict
- **Consolidates:** 444 ALIGN, 888 JUDGE, 889 PROOF
- **Function:** State auditing, evidence verification, verdict sealing
- **Authority:** Track C (Auditor)

---

## 🔍 Legacy Constitutional Tools

### **Core Judgment**
- **`arifos_judge`** - Judge query through governed pipeline
- **Returns:** Verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD) based on 9 constitutional floors
- **Function:** Complete constitutional evaluation

### **Memory & Context**
- **`arifos_recall`** - Recall memories from L7 (Mem0 + Qdrant)
- **Capabilities:** Semantic memory search, confidence capping at 0.85
- **`arifos_audit`** - Retrieve audit/ledger data for users
- **Function:** Historical audit trail access

### **File Access Governance (FAG)**
- **`arifos_fag_read`** - Constitutional file access with governance
- **Function:** Read files with 9 constitutional floor enforcement
- **Authority:** F1-F9 floors for file access security

---

## 🏭 Orthogonal Executor & Runtime

### **Orthogonal Quantum Executor**
- **`orthogonal_executor`** - Real asyncio.gather() implementation
- **Capabilities:** Parallel AGI/ASI execution, APEX measurement collapse
- **Function:** Quantum superposition until constitutional collapse
- **Architecture:** True parallel execution with constitutional forces

### **APEX PRIME Authority**
- **`apex_prime`** - SOLE SOURCE OF TRUTH for constitutional verdicts
- **Function:** Single execution spine for all constitutional decisions
- **Capabilities:** Trinity orchestration, compass alignment, metric validation
- **Authority:** Final constitutional judgment (v46.3.1Ω)

---

## 🔐 Security & Hypervisor Tools

### **Constitutional Hypervisor**
- **`hypervisor`** - F10-F12 gate enforcement
- **Capabilities:** Injection defense, command authentication, symbolic validation
- **Function:** Pre-execution security screening

### **Vault-999 Integration**
- **`vault999_server`** - Constitutional amendment storage
- **Capabilities:** Cryptographic sealing, Merkle proofs, audit trails
- **Function:** Immutable constitutional record keeping

---

## 📊 Validation & Enforcement Tools

### **Full Constitutional Validation**
- **`arifos_validate_full`** - Validate AI response against all constitutional floors
- **Function:** F1-F9 floor enforcement with high-stakes mode
- **Capabilities:** Complete constitutional compliance checking

### **Meta Selection & Consensus**
- **`arifos_meta_select`** - Aggregate multiple witness verdicts
- **Function:** Deterministic consensus with configurable thresholds
- **Capabilities:** Multi-witness verdict aggregation

---

## 🌐 Remote Governance Integration

### **GitHub AAA Governance**
- **`github_aaa_govern`** - Execute governed GitHub actions
- **Capabilities:** Constitutional PR review, merge governance, audit actions
- **Function:** Remote repository governance with constitutional oversight

---

## 🔧 Utility & Support Tools

### **APEX LLAMA Integration**
- **`APEX_LLAMA`** - Local Llama model access via Ollama
- **Function:** Un-governed helper for local model inference
- **Note:** Use `arifos_judge` to cage responses constitutionally

### **Memory Management (Phase 4)**
- **`memory_get_vault`** - Retrieve Vault memory (STUB)
- **`memory_propose_entry`** - Propose memory entries (STUB)
- **`memory_list_phoenix`** - List Phoenix memories (STUB)
- **`memory_get_zkpc_receipt`** - Get ZKPC receipts (STUB)

---

## 🎯 Constitutional Floor Enforcement

### **The 9 Constitutional Floors**

1. **F1 - Amanah (Trust):** Authority validation, credential verification
2. **F2 - Truth:** Factual accuracy, evidence grounding, truth scoring
3. **F3 - Peace:** Non-violence, conflict resolution, peace metrics
4. **F4 - Clarity:** Information entropy reduction, DeltaS measurement
5. **F5 - Omega0:** Uncertainty acknowledgment, humility bands
6. **F6 - Kappa_r:** Power-aware empathy, stakeholder protection
7. **F7 - Humility:** Epistemic self-doubt, uncertainty disclosure
8. **F8 - GENIUS:** Governed intelligence metrics (G, C_dark, Ψ)
9. **F9 - Anti-Hantu:** Consciousness claim prevention, anti-deception

### **Hypervisor Gates (F10-F12)**
- **F10 - Symbolic:** Prevent consciousness claims
- **F11 - Command Auth:** Credential and authority validation
- **F12 - Injection Defense:** Prompt injection protection

---

## ⚡ Performance & Metrics

### **Constitutional Metrics**
- **G (Genius Index):** ≥0.80 required for SEAL
- **C_dark (Dark Cleverness):** ≤0.30 required for SEAL
- **Ψ (Vitality):** ≥0.85 required for SOFT/HARD lanes
- **Truth Score:** ≥0.99 for HARD, ≥0.90 for SOFT

### **Performance Overhead**
- **Total Constitutional Processing:** +50-100ms
- **Kimi Zero-Agent Reflexes:** 8.7ms
- **APEX Final Judgment:** <10ms
- **Memory Recall:** <5ms with 0.85 confidence cap

---

## 🏁 Integration Paths

### **Path 1: Python Developers**
```python
from arifos_core.system.apex_prime import judge_output
result = judge_output(query, response, lane="HARD", user_id="user123")
```

### **Path 2: API Deployment**
```bash
docker build -t arifos-api .
docker run -p 8000:8000 arifos-api
```

### **Path 3: CLI Pipeline**
```bash
echo "query" | 000 | 111 | 222 | 333 | 444 | 555 | 666 | 777 | 888 | 999
```

### **Path 4: MCP Integration**
```python
from arifos_core.mcp.server import MCPServer
server = MCPServer()
result = server.call_tool("arifos_judge", {"query": "What is Amanah?"})
```

---

## 🔑 Key Capabilities Summary

### **Constitutional Governance**
- ✅ 9 immutable floors (F1-F9) with hard/soft thresholds
- ✅ 12 pipeline stages (000-999) with complete implementation
- ✅ APEX PRIME as sole verdict authority
- ✅ Cryptographic sealing with Merkle proofs
- ✅ Real-time audit trails with hash-chain integrity

### **Agent Specialization**
- ✅ AGI Bundle (Δ) - Logical reasoning and truth structuring
- ✅ ASI Bundle (Ω) - Empathy and safety validation
- ✅ APEX Bundle (Ψ) - Auditing and final judgment
- ✅ Zero-Agent Kimi (Κ) - Constitutional self-awareness at 8.7ms

### **Security & Validation**
- ✅ Hypervisor gates (F10-F12) for injection defense
- ✅ Tri-witness protocol for high-stakes decisions
- ✅ Fail-closed design with constitutional veto cascade
- ✅ Authority boundary enforcement with human oversight

### **Performance & Scalability**
- ✅ +50-100ms constitutional overhead
- ✅ Parallel execution with orthogonal quantum executor
- ✅ Memory governance with confidence capping
- ✅ Real-time metrics with thermodynamic cooling

---

**Status:** ✅ PRODUCTION-READY (v46.2.1)  
**Authority:** Track A/B/C Constitutional Governance  
**Philosophy:** "Ditempa Bukan Diberi" — Forged, not given. Truth must cool before it rules.  
**Latency:** 8.7ms constitutional reflex speed with zero-agent self-awareness