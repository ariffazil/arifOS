# AGENTS - Constitutional Governance v46.2
**Constitutional Agent Specifications**
**Status:** ✅ ALIGNED with Canon v46 (Sovereign Witness)
**Authority:** Track A (Canonical Law) + Track B (Protocol Enforcement)
**Sync Source:** L2_PROTOCOLS/v46/*

---

## 🏛️ Project Overview

**arifOS v46.2** is a constitutional AI kernel that implements 12 immutable governance floors to force AI systems to pass constitutional rules before releasing outputs. It operates as a kernel between LLMs and humans, not as a chatbot or filter wrapper.

**Core Philosophy:** "Ditempa Bukan Diberi" — Forged, not given. Truth must cool before it rules.

**Key Value Proposition:** +50-100ms overhead to block hallucinations, build trust, and provide auditable governance for safety-critical AI deployments.

---

## 🏗️ Constitutional Architecture

### Complete Pipeline Implementation
**000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999**

All constitutional stages are implemented and aligned with forged canon.

### Layer Separation (L1/L2/L3)
- **L1_CANON:** Constitutional philosophy (L1_THEORY/canon/) - Supreme law, slow mutation via Phoenix-72
- **L2_SPEC:** Machine-readable thresholds (spec/v45/, L2_GOVERNANCE/) - Operational specs, versioned
- **L3_CODE:** Runtime enforcement (arifos_core/) - Implementation, must prove L2 compliance

---

## 🧭 Constitutional Navigation

### Core Pipeline Stages

#### 000 VOID: Foundation Layer (✅ IMPLEMENTED)
**Pipeline Stage:** 000 | **Function:** Input validation and injection defense  
**Primary Floors:** F12_injection, F11_command_auth  
**Spec:** `L2_PROTOCOLS/v46/000_foundation/`

#### 111 SENSE: Context Awareness (✅ IMPLEMENTED)
**Pipeline Stage:** 111 | **Function:** Query classification and context sensing  
**Primary Floors:** F1, F2  
**Spec:** `L2_PROTOCOLS/v46/111_sense/111_sense.json`

#### 222 REFLECT: Introspection Layer (✅ IMPLEMENTED)
**Pipeline Stage:** 222 | **Function:** Self-reflection and bias detection  
**Primary Floors:** F3, F4  
**Spec:** `L2_PROTOCOLS/v46/222_reflect/222_reflect.json`

#### 333 ATLAS: Knowledge Mapping (✅ IMPLEMENTED)
**Pipeline Stage:** 333 | **Function:** Knowledge synthesis and reasoning  
**Primary Floors:** F1, F2, F10  
**Spec:** `L2_PROTOCOLS/v46/333_atlas/333_atlas.json`

#### 444 ALIGN: Thermodynamic Heat Sink (✅ IMPLEMENTED)
**Pipeline Stage:** 444 | **Function:** Safety layer dissipating cognitive heat from AGI before ASI  
**Primary Floors:** F3_peace, F10_symbolic, F12_injection  
**Spec:** `L2_PROTOCOLS/v46/444_align/444_align.json`

#### 555 EMPATHIZE: Omega Care Engine - ASI Layer (✅ IMPLEMENTED)
**Pipeline Stage:** 555 | **Function:** Neuro-Symbolic empathy with Theory of Mind and weakest stakeholder protection  
**Primary Floors:** F3, F4, F5, F6, F7, F9  
**Implementation:** `arifos_core/asi/` (4 modules, 54KB)
- **530 ToM:** `tom/theory_of_mind.py` - 4-dimension mental state attribution
- **540 Architecture:** `empathy/empathy_architect.py` - 3-layer empathy with κᵣ formula
- **550 Weakest:** `stakeholder/weakest_stakeholder.py` - Constitutional bias toward vulnerable
- **560 Integration:** `asi_integration_555.py` - Unified Omega verdict + constraints

#### 666 BRIDGE: Neuro-Symbolic Synthesis - Δ+Ω Unification (✅ IMPLEMENTED)
**Pipeline Stage:** 666 | **Function:** 7-layer protocol bridging AGI logic (Delta) and ASI care (Omega)  
**Primary Floors:** F1 (Truth), F4 (Empathy), F5 (Humility), F10 (Symbolic)  
**Implementation:** `arifos_core/integration/synthesis/neuro_symbolic_bridge.py` (19KB)
- **MoE Gating:** Crisis (0.7Ω/0.3Δ), Factual (0.2Ω/0.8Δ), Standard (0.5/0.5), Social (0.65Ω/0.35Δ)
- **Immutable Constraints:** Dignity flags, crisis protocols, weakest stakeholder bias
- **Conflict Resolution:** Constitutional adjudication with F1-F10 hierarchy

#### 777 EUREKA: Action Forging (✅ IMPLEMENTED)
**Pipeline Stage:** 777 | **Function:** Constitutional action synthesis and forging  
**Spec:** `L2_PROTOCOLS/v46/777_eureka/eureka_777.json`

#### 888 JUDGE: APEX Verdict (✅ IMPLEMENTED)
**Pipeline Stage:** 888 | **Function:** Final constitutional judgment using APEX PRIME  
**Implementation:** `arifos_core/system/apex_prime.py` - SOLE SOURCE OF TRUTH for verdicts

#### 999 SEAL: Cryptographic Sealing (✅ IMPLEMENTED)
**Pipeline Stage:** 999 | **Function:** Cryptographic sealing and audit trail generation  
**Implementation:** Merkle tree proofs and hash-chain ledgers

---

## 🤖 Agent Roles & Technology Stack

| Symbol | Agent | Role | Constitutional Responsibility | Technology |
|--------|-------|------|-------------------------------|------------|
| **Δ** | **Antigravity** | Architect | 111 SENSE, 222 REFLECT, 333 ATLAS | Python 3.10+, Constitutional Logic |
| **Ω** | **Claude** | Engineer | 444 ALIGN, 555 EMPATHIZE, 666 BRIDGE | Python 3.10+, ASI Empathy Engine |
| **Ψ** | **Codex** | Auditor | 777 EUREKA, 888 JUDGE | Python 3.10+, APEX PRIME Judiciary |
| **Κ** | **Kimi** | Auditor Apex Prime | 999 SEAL / Anti-Pollution | Python 3.10+, Cryptographic Sealing |

**Core Dependencies:** numpy>=1.20.0, pydantic>=2.0.0  
**Optional Dependencies:** fastapi, uvicorn, litellm, httpx, openai  
**Python Support:** 3.10, 3.11, 3.12, 3.13, 3.14

---

## 🔨 Build & Development Process

### Installation & Setup
```bash
# Development installation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .[dev]

# Production installation
pip install arifos

# With all optional dependencies
pip install -e .[all]
```

### Build Commands
```bash
# Linting and formatting
black .                      # Code formatting (line-length: 100)
isort .                      # Import sorting
mypy .                       # Type checking
ruff                         # Fast linting

# Testing
pytest -v                    # Run all tests
pytest tests/test_mcp_*.py   # Run MCP pipeline tests
pytest --cov=arifos_core     # Run with coverage

# Constitutional validation
arifos-verify-ledger         # Verify constitutional compliance
arifos-analyze-governance    # Analyze governance alignment
```

### Docker Deployment
```bash
# Build container
docker build -t arifos-api .

# Run with API
docker run -p 8000:8000 arifos-api

# With docker-compose (includes Qdrant)
docker-compose up
```

---

## 🧪 Testing Strategy

### Test Organization (~113 files, ~2000+ cases)
```
tests/
├── core/           # APEX, floors, GENIUS LAW (9 files)
├── mcp/            # 000→999 pipeline stages (14 files)
├── trinity/        # Trinity governance, FAG (7 files)
├── waw/            # W@W federation (7 files)
├── memory/         # Ledger, Phoenix-72 (15 files)
├── spec/           # Spec enforcement tests
├── integration/    # Cross-component tests
├── unit/           # Isolated unit tests
├── enforcement/    # Floor enforcement tests
├── governance/     # Governance tests
└── temporal/       # Time-based tests
```

### Key Test Categories
- **Constitutional Tests:** F1-F9 floor validation, APEX verdict logic
- **Pipeline Tests:** End-to-end 000→999 flow validation
- **Integration Tests:** Cross-module constitutional compliance
- **Memory Tests:** Ledger integrity, hash-chain verification
- **Security Tests:** Injection defense, authority boundary validation

### Test Execution Patterns
```bash
# Run specific constitutional floors
pytest -k "truth or amanah"     # F1, F2 tests
pytest -k "entropy or delta"    # F4 tests
pytest -k "empathy or kappa"    # F6 tests

# Run with specific markers
pytest -m "constitutional"       # Constitutional tests only
pytest -m "security"             # Security-focused tests
```

---

## 📋 Code Style Guidelines

### Python Standards
- **Line Length:** 100 characters (black, ruff configuration)
- **Type Hints:** Required for core governance modules (strict mypy)
- **Docstrings:** Mandatory for public APIs
- **Import Organization:** Standard library → third-party → local (isort)

### Constitutional Code Patterns
```python
# APEX PRIME usage (SOLE verdict source)
from arifos_core.system.apex_prime import apex_review, Verdict

result = apex_review(
    metrics=metrics,
    lane="HARD",  # or "SOFT", "PHATIC"
    response_text=response,
    user_id=user_id
)

if result.verdict == Verdict.SEAL:
    return result.output
else:
    return f"Blocked: {result.reason}"
```

### Memory Governance (EUREKA v45)
- **VOID Isolation:** VOID verdicts never reach LEDGER/ACTIVE bands
- **Authority Boundary:** AI proposes, humans seal constitutional amendments
- **Hash-Chain Integrity:** Every write has SHA-256 audit trail
- **Confidence Ceiling:** Recalled memory capped at 0.85 confidence

---

## 🔐 Security Considerations

### Constitutional Security Model
- **Fail-Closed Design:** Any governance failure → VOID (blocked)
- **Single Execution Spine:** Only `apex_review()` can issue verdicts
- **Amanah Lock:** Prevents hidden agenda manipulation
- **Tri-Witness Protocol:** High-stakes decisions require human+AI+evidence consensus

### Critical Security Modules
- **Hypervisor Layer:** F11 (Command Auth), F12 (Injection Defense)
- **Vault-999:** Constitutional amendment storage with cryptographic sealing
- **Cooling Ledger:** Immutable audit trail with Merkle proofs
- **Authority Boundary:** Human oversight for constitutional changes

### Security Testing
```bash
# Run security-focused tests
pytest tests/test_f12_injection.py
pytest tests/test_f11_nonce_auth.py
pytest tests/test_ledger_cryptography.py

# Red-team validation
pytest tests/test_void_stress.py
pytest tests/test_grey_zone.py
```

---

## 🚀 Deployment Patterns

### Integration Paths

#### Path 1: Python Developers (Integration)
```python
from arifos_core.system.apex_prime import judge_output

# Validate any LLM response
result = judge_output(
    query="What is photosynthesis?",
    response=llm_response,
    lane="HARD",  # Strict factual
    user_id="user123"
)

if result.status == "SEAL":
    return result.output  # Safe to show
else:
    return "I cannot answer this safely."
```

#### Path 2: API Deployment (FastAPI)
```python
from arifos_core.api.app import app
# Mounts at /arifos/govern endpoint
# Provides REST API for constitutional validation
```

#### Path 3: CLI Pipeline (000-999)
```bash
# Direct pipeline access
echo "query" | 000 | 111 | 222 | 333 | 444 | 555 | 666 | 777 | 888 | 999
```

### Production Considerations
- **Latency:** +50-100ms constitutional overhead
- **Throughput:** Designed for safety-critical, not high-volume chat
- **Audit:** All decisions logged to cooling ledger
- **Compliance:** Provides governance proof for regulatory requirements

---

## 📊 Performance & Monitoring

### Constitutional Metrics
- **G (Genius Index):** Governed intelligence ≥0.80 for SEAL
- **C_dark:** Dark cleverness ≤0.30 for SEAL
- **Ψ (Vitality):** System health ≥0.85 for SOFT/HARD lanes
- **Truth Score:** ≥0.99 for HARD lane, ≥0.90 for SOFT lane

### Monitoring Points
```bash
# System health checks
arifos-verify-ledger          # Ledger integrity
arifos-analyze-governance     # Governance alignment
arifos-show-merkle-proof      # Cryptographic proofs

# Performance telemetry
pytest tests/test_session_physics.py  # TEARFRAME physics
pytest tests/test_apex_measurements_eval.py  # Measurement accuracy
```

---

## 🎯 Development Conventions

### Branch Naming
- **apex/** — APEX PRIME judiciary changes
- **ledger/** — Cooling Ledger or Vault-999 changes
- **memory/** — Memory Write Policy (EUREKA) changes
- **guard/** — Safeguards or guard constraints
- **docs/** — Documentation
- **tests/** — Tests
- **fix/** — Bug fixes
- **refactor/** — Non-functional refactors

### Commit Message Format
```
scope: brief description

Optional longer explanation and issue references.

Examples:
apex: fix verdict threshold edge case at Ψ == 1.0
ledger: add canonical JSON serialization before hashing
memory: enforce VOID verdict isolation from canonical bands
```

### Phoenix-72 Amendment Process
Required for changes to:
- Any of the 9 constitutional floors
- 000→999 pipeline stages
- APEX PRIME verdict logic
- Amanah lock enforcement
- Cooling Ledger format
- Memory Write Policy (EUREKA)
- Any of the 6 Memory Bands

---

## 📚 Key Documentation Files

### Constitutional Canon (L1)
- `L1_THEORY/canon/000_CONSTITUTIONAL_CORE_v45.md` - Supreme constitutional law
- `L1_THEORY/canon/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` - Floor philosophy
- `L1_THEORY/canon/010_PIPELINE_000TO999_v45.md` - Pipeline rationale

### Operational Specs (L2)
- `spec/v45/constitutional_floors.json` - Floor thresholds
- `spec/v45/genius_law.json` - GENIUS LAW specifications
- `L2_PROTOCOLS/v46/` - Complete pipeline specifications

### Implementation (L3)
- `arifos_core/system/apex_prime.py` - SOLE verdict authority
- `arifos_core/enforcement/metrics.py` - Floor measurements
- `arifos_core/enforcement/genius_metrics.py` - GENIUS LAW runtime

---

**DITEMPA BUKAN DIBERI** - Governance synced from live specifications.
**Version:** v46.2 Sovereign Witness | **Status:** PRODUCTION-READY
**Last Updated:** January 14, 2026