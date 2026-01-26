# Refactoring Status & Migration Roadmap

**Date:** 2026-01-26  
**Authority:** Muhammad Arif bin Fazil  
**Approved Strategy:** Option B - Complete canonical_core first  
**Target:** Lower entropy, MCP-ready production architecture  
**Version:** v52.5.1-SEAL  

---

## 📊 CURRENT STATUS SNAPSHOT

### File Count Comparison

| Location | Python Files | Status |
|----------|--------------|--------|
| **canonical_core/** | 34 files | ✅ Clean structure |
| **arifos/core/** | 383 files | ⚠️ High complexity |
| **Gap** | 349 files | Need selective migration |

**Key Insight:** We don't need all 383 files. Only **~60 critical files** need migration to make canonical_core production-ready.

---

## ✅ WHAT'S COMPLETED IN CANONICAL_CORE

### Core Infrastructure (Foundation)

| Component | Status | Files | Quality |
|-----------|--------|-------|---------|
| **Constitutional Floors** | ✅ DONE | `constitutional_floors.py` (229 LOC) | Clean definitions |
| **Floor Validators** | ✅ DONE | `floors.py` (11,774 LOC) | Complete F1-F13 |
| **Bundle Store** | ✅ DONE | `bundle_store.py` (5,803 LOC) | Session state management |
| **State Management** | ✅ DONE | `state.py` (3,713 LOC) | SessionState + cooling tiers |
| **Authority** | ✅ DONE | `authority.py` (2,077 LOC) | F11 Command Authority |
| **ZKPC Crypto** | ✅ DONE | `zkpc.py` (2,306 LOC) | Basic cryptographic proofs |
| **Entropy** | ✅ DONE | `entropy_compressor.py` (2,784 LOC) | ΔS computation |
| **Micro Loop** | ✅ DONE | `micro_loop.py` (10,147 LOC) | Basic orchestration |

**Total Foundation:** 8 files, ~50,000 LOC ✅

### AGI Engine (Δ Mind) - ISOLATED BUT COMPLETE

| Component | Status | Files | Quality |
|-----------|--------|-------|---------|
| **Stage 111 (Sense)** | ✅ DONE | `agi_room/stage_111_sense.py` (13,852 LOC) | Complete |
| **Stage 222 (Think)** | ✅ DONE | `agi_room/stage_222_think.py` (14,572 LOC) | Complete |
| **Stage 333 (Reason)** | ✅ DONE | `agi_room/stage_333_reason.py` (19,349 LOC) | Complete |
| **AGI Executor** | ✅ DONE | `agi_room/executor.py` (14,586 LOC) | Orchestration |
| **AGI Hardening** | ✅ DONE | `agi_room/hardening.py` (14,985 LOC) | Security layer |

**Total AGI:** 6 files, ~91,000 LOC ✅

**Status:** Complete but **isolated in agi_room/**. Need to integrate into main pipeline.

### ASI Engine (Ω Heart) - ISOLATED BUT COMPLETE

| Component | Status | Files | Quality |
|-----------|--------|-------|---------|
| **Stage 555 (Empathy)** | ✅ DONE | `asi_room/stage_555_empathy.py` (15,136 LOC) | Complete |
| **ASI Engine** | ✅ DONE | `asi_room/asi_engine.py` (18,415 LOC) | Complete |

**Total ASI:** 2 files, ~34,000 LOC ✅

**Status:** Complete but **isolated in asi_room/**. Need to integrate into main pipeline.

### Stage Coverage

| Stage | File | Status | LOC |
|-------|------|--------|-----|
| **000 INIT** | ✅ `000_space/000_init/stage_000_core.py` | Complete | 515 |
| **111 SENSE** | ✅ `agi_room/stage_111_sense.py` | Complete (isolated) | 13,852 |
| **222 THINK** | ✅ `agi_room/stage_222_think.py` | Complete (isolated) | 14,572 |
| **333 REASON** | ✅ `agi_room/stage_333_reason.py` | Complete (isolated) | 19,349 |
| **444 TRINITY** | ✅ `stage_444.py` | Complete | 3,665 |
| **555 EMPATHY** | ✅ `stage_555.py` + `asi_room/stage_555_empathy.py` | Complete (partial dup) | 6,042 + 15,136 |
| **666 ALIGN** | ✅ `stage_666.py` | Complete | 3,224 |
| **777 FORGE** | ❌ | **MISSING** | - |
| **888 JUDGE** | ❌ | **MISSING** | - |
| **889 PROOF** | ❌ | **MISSING** | - |
| **999 SEAL** | ⚠️ | Partial in vault/ | - |

**Coverage:** 7/10 stages complete (70%), 3 missing

### Memory/Vault

| Component | Status | Files | Quality |
|-----------|--------|-------|---------|
| **Vault Directory** | ✅ DONE | `vault/` (2 files) | Basic ledger |
| **Learning Loop** | ⚠️ PARTIAL | `vault/learning_loop.py` | Stub only |

**Status:** Basic file-based ledger exists. Missing SQLite, PostgreSQL, Merkle, Cooling backends.

---

## ❌ WHAT'S MISSING IN CANONICAL_CORE

### CRITICAL GAPS (P0 - Blocks Production)

#### 1. APEX PRIME (Stage 888 Judge) - 0% COMPLETE

**Files Needed from arifos/core:**
```
arifos/core/system/apex_prime.py (19,705 LOC)
  → Copy to: canonical_core/apex_prime.py

Key class: APEXPrime
Key methods:
  - judge_output() - Constitutional verdict logic
  - check_floors() - F1-F13 validation
  - _compute_p_truth() - Thermodynamic formula
```

**Impact:** **CRITICAL** - Cannot make verdicts without this.

#### 2. APEX Engine (Ψ Soul) - 0% COMPLETE

**Directory Needed from arifos/core:**
```
arifos/core/apex/ (7 files, ~40,000 LOC)
├── __init__.py
├── kernel.py (20,309 LOC) - APEXJudicialCore
├── psi_kernel.py (10,294 LOC) - Ψ calculations
├── floor_checks.py (5,760 LOC) - APEX floor validation
├── contracts/
│   └── apex_prime_output_v41.py
└── governance/ (8 files)
    ├── merkle_sealing.py
    ├── proof_of_governance.py
    ├── zkpc_runtime.py
    ├── sovereign_signature.py
    └── ...

→ Copy entire directory to: canonical_core/apex/
```

**Impact:** **CRITICAL** - No cryptographic sealing, Merkle proofs, governance trails.

#### 3. Missing Stages (777, 888, 889) - 0% COMPLETE

**Files Needed from arifos/core:**
```
arifos/core/stage/stage_777_forge.py
  → Copy to: canonical_core/stage_777_forge.py

arifos/core/stage/stage_888_judge.py
  → Copy to: canonical_core/stage_888_judge.py

arifos/core/stage/stage_889_proof.py
  → Copy to: canonical_core/stage_889_proof.py
```

**Impact:** **CRITICAL** - Pipeline incomplete (70% → 100%).

#### 4. MCP Trinity Tools - 0% COMPLETE

**Files Needed from arifos/mcp:**
```
arifos/mcp/tools/mcp_trinity.py (5 tools bundled)
arifos/mcp/tools/mcp_agi_kernel.py
arifos/mcp/tools/mcp_asi_kernel.py
arifos/mcp/tools/mcp_apex_kernel.py

arifos/mcp/server.py (stdio transport)
arifos/mcp/sse.py (SSE transport)
arifos/mcp/trinity_server.py (FastAPI wrapper)

→ Copy to: canonical_core/mcp/
```

**Impact:** **CRITICAL** - Cannot be used by Claude, Gemini, Kimi without MCP tools.

#### 5. Types & Contracts - PARTIAL

**Files Needed from arifos/core:**
```
arifos/core/system/types.py (Verdict, Metrics, FloorCheckResult enums)
  → Copy to: canonical_core/types.py

arifos/core/apex/contracts/apex_prime_output_v41.py
  → Copy to: canonical_core/contracts/apex_output.py
```

**Impact:** **HIGH** - Type safety for verdicts and metrics.

---

### IMPORTANT GAPS (P1 - Functional)

#### 6. Memory Backends - 12% COMPLETE

**Files Needed from arifos/core:**
```
arifos/core/memory/ledger/sqlite_ledger_store.py
arifos/core/memory/ledger/postgres_ledger.py
arifos/core/memory/ledger/cooling_ledger.py
arifos/core/memory/ledger/merkle_ledger.py
arifos/core/memory/ledger/codex_ledger.py

→ Copy to: canonical_core/memory/ledger/
```

**Impact:** **MEDIUM** - Production needs SQLite/PostgreSQL, not just file-based.

#### 7. Constitutional Memory - 0% COMPLETE

**Directory Needed:**
```
arifos/core/memory/constitutional_memory/ (8 files)
├── constitutional_ledger.py
├── floor_memory.py
├── governance_record.py
├── merkle_memory.py
└── ...

→ Copy to: canonical_core/memory/constitutional_memory/
```

**Impact:** **MEDIUM** - Historical floor violation tracking.

#### 8. Scars System - 0% COMPLETE

**Directory Needed:**
```
arifos/core/memory/scars/ (3 files)
├── void_scanner.py
├── scar_manager.py
└── ...

→ Copy to: canonical_core/memory/scars/
```

**Impact:** **LOW** - Nice to have for void history analysis.

---

### OPTIMIZATION GAPS (P2 - Enhancement)

#### 9. Advanced AGI Features

**Files Needed:**
```
arifos/core/engines/agi/atlas.py (ATLAS-333 lane routing)
arifos/core/engines/agi/clarity_scorer.py (ΔS precision)
arifos/core/engines/agi/entropy.py (expanded entropy tracking)

→ Copy to: canonical_core/engines/agi/
```

**Impact:** **LOW** - Performance optimization.

#### 10. Advanced ASI Features

**Files Needed:**
```
arifos/core/asi/tom/theory_of_mind.py (better empathy)
arifos/core/asi/cooling.py (full async cooling engine)

→ Copy to: canonical_core/engines/asi/
```

**Impact:** **LOW** - Better empathy modeling.

---

## 🎯 MIGRATION ROADMAP (6 WEEKS)

### PHASE 1: CRITICAL COMPONENTS (Week 1-2)

**Goal:** Make canonical_core functionally complete for MCP.

#### Week 1: APEX PRIME + Engine

**Day 1 (2h):**
```bash
# Copy APEX PRIME
cp arifos/core/system/apex_prime.py canonical_core/apex_prime.py

# Copy types
cp arifos/core/system/types.py canonical_core/types.py

# Test: Import works
cd canonical_core && python -c "from apex_prime import APEXPrime; print('✅ APEX PRIME imported')"
```

**Day 2-3 (4h):**
```bash
# Copy APEX Engine directory
cp -r arifos/core/apex canonical_core/apex

# Update imports in apex_prime.py to point to canonical_core.apex
# Test: APEX Engine kernel loads
python -c "from apex.kernel import APEXJudicialCore; print('✅ APEX kernel loaded')"
```

**Day 4 (2h):**
```bash
# Copy missing stages
cp arifos/core/stage/stage_777_forge.py canonical_core/stage_777_forge.py
cp arifos/core/stage/stage_888_judge.py canonical_core/stage_888_judge.py
cp arifos/core/stage/stage_889_proof.py canonical_core/stage_889_proof.py

# Update imports in stages to use canonical_core.*
# Test: Stages import successfully
```

**Day 5 (2h):**
```bash
# Create pipeline orchestrator
cat > canonical_core/pipeline.py << 'EOF'
"""
Unified Pipeline Orchestrator
000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 889 → 999
"""
from canonical_core import stage_444, stage_555, stage_666
from canonical_core import stage_777_forge, stage_888_judge, stage_889_proof
from canonical_core.agi_room import stage_111_sense, stage_222_think, stage_333_reason
from canonical_core.asi_room import stage_555_empathy
from canonical_core.apex_prime import APEXPrime

def execute_pipeline(session_id: str, query: str) -> dict:
    # 000: Init (already exists in 000_space/)
    # 111-333: AGI (from agi_room)
    # 444: Trinity Sync
    # 555: ASI Empathy
    # 666: Align
    # 777: Forge
    # 888: Judge (APEX PRIME)
    # 889: Proof
    # 999: Seal
    pass
EOF

# Test: Pipeline imports all stages
python -c "from pipeline import execute_pipeline; print('✅ Pipeline complete')"
```

**Week 1 Deliverable:** ✅ All 10 stages (000-999) available in canonical_core

#### Week 2: MCP Trinity Tools

**Day 1-2 (4h):**
```bash
# Create MCP directory structure
mkdir -p canonical_core/mcp/tools

# Copy MCP tools
cp arifos/mcp/tools/mcp_trinity.py canonical_core/mcp/tools/
cp arifos/mcp/tools/mcp_agi_kernel.py canonical_core/mcp/tools/
cp arifos/mcp/tools/mcp_asi_kernel.py canonical_core/mcp/tools/
cp arifos/mcp/tools/mcp_apex_kernel.py canonical_core/mcp/tools/

# Update imports to use canonical_core.*
# Replace: from arifos.core → from canonical_core
```

**Day 3-4 (4h):**
```bash
# Copy MCP server infrastructure
cp arifos/mcp/server.py canonical_core/mcp/server.py
cp arifos/mcp/sse.py canonical_core/mcp/sse.py
cp arifos/mcp/trinity_server.py canonical_core/mcp/trinity_server.py

# Copy supporting files
cp arifos/mcp/bridge.py canonical_core/mcp/bridge.py
cp arifos/mcp/models.py canonical_core/mcp/models.py
cp arifos/mcp/metrics.py canonical_core/mcp/metrics.py

# Update all imports
```

**Day 5 (2h):**
```bash
# Test MCP server starts
cd canonical_core
python -m mcp.server

# Test tool registration
python -c "from mcp.tools.mcp_trinity import mcp_000_init; print('✅ Tools loaded')"
```

**Week 2 Deliverable:** ✅ MCP server running with all 5 Trinity tools

---

### PHASE 2: STRUCTURAL REFACTORING (Week 3-4)

**Goal:** Lower entropy by unifying structure with arifos/core patterns.

#### Week 3: Engine Integration

**Day 1-2 (4h):**
```bash
# Create unified engines directory
mkdir -p canonical_core/engines

# Move AGI from agi_room to engines/agi
mv canonical_core/agi_room canonical_core/engines/agi

# Move ASI from asi_room to engines/asi
mv canonical_core/asi_room canonical_core/engines/asi

# Copy APEX to engines/apex (already copied to apex/)
cp -r canonical_core/apex canonical_core/engines/apex

# Directory structure now:
# canonical_core/
# ├── engines/
# │   ├── agi/          ← moved from agi_room
# │   ├── asi/          ← moved from asi_room
# │   └── apex/         ← copied from apex
# ├── apex_prime.py     ← keeps root level for import clarity
# ├── stage_*.py        ← keeps root level stages
# └── ...
```

**Day 3 (2h):**
```bash
# Create engines/__init__.py with KernelManager
cat > canonical_core/engines/__init__.py << 'EOF'
"""
Trinity Engine Manager (Δ AGI / Ω ASI / Ψ APEX)
"""
from canonical_core.engines.agi import AGIKernel
from canonical_core.engines.asi import ASIKernel
from canonical_core.engines.apex import APEXKernel

class KernelManager:
    def __init__(self):
        self.agi = AGIKernel()
        self.asi = ASIKernel()
        self.apex = APEXKernel()
    
    def get_agi(self):
        return self.agi
    
    def get_asi(self):
        return self.asi
    
    def get_apex(self):
        return self.apex

_kernel_manager = None

def get_kernel_manager():
    global _kernel_manager
    if _kernel_manager is None:
        _kernel_manager = KernelManager()
    return _kernel_manager
EOF
```

**Day 4-5 (4h):**
```bash
# Update all imports throughout canonical_core
# FROM: from canonical_core.agi_room import stage_111_sense
# TO:   from canonical_core.engines.agi import stage_111_sense

# Run global find-replace
find canonical_core -type f -name "*.py" -exec sed -i 's/agi_room/engines.agi/g' {} \;
find canonical_core -type f -name "*.py" -exec sed -i 's/asi_room/engines.asi/g' {} \;

# Test: All imports resolve
python -m pytest canonical_core/tests/ -v
```

**Week 3 Deliverable:** ✅ Unified `engines/` directory (matches arifos/core pattern)

#### Week 4: Memory System Expansion

**Day 1-2 (4h):**
```bash
# Create memory directory structure
mkdir -p canonical_core/memory/ledger
mkdir -p canonical_core/memory/constitutional_memory
mkdir -p canonical_core/memory/scars

# Copy ledger backends
cp arifos/core/memory/ledger/sqlite_ledger_store.py canonical_core/memory/ledger/
cp arifos/core/memory/ledger/postgres_ledger.py canonical_core/memory/ledger/
cp arifos/core/memory/ledger/cooling_ledger.py canonical_core/memory/ledger/
cp arifos/core/memory/ledger/merkle_ledger.py canonical_core/memory/ledger/
cp arifos/core/memory/ledger/codex_ledger.py canonical_core/memory/ledger/

# Update imports
```

**Day 3 (2h):**
```bash
# Copy constitutional memory
cp -r arifos/core/memory/constitutional_memory/* canonical_core/memory/constitutional_memory/

# Copy scars system
cp -r arifos/core/memory/scars/* canonical_core/memory/scars/
```

**Day 4-5 (4h):**
```bash
# Integrate memory backends into pipeline
# Update canonical_core/pipeline.py to use SQLite ledger by default
# Add environment variable: ARIFOS_LEDGER_BACKEND=file|sqlite|postgres

# Test: SQLite ledger works
python -c "from memory.ledger.sqlite_ledger_store import SQLiteLedger; print('✅ SQLite backend')"
```

**Week 4 Deliverable:** ✅ Production-ready memory system (file + SQLite + PostgreSQL)

---

### PHASE 3: PRODUCTION HARDENING (Week 5-6)

**Goal:** Testing, optimization, deployment readiness.

#### Week 5: Integration Testing

**Day 1-3 (6h):**
```bash
# Create comprehensive test suite
cat > canonical_core/tests/test_full_pipeline.py << 'EOF'
def test_000_to_999_pipeline():
    """Test complete 000 → 999 metabolic loop."""
    from canonical_core.pipeline import execute_pipeline
    result = execute_pipeline("test_session", "Hello world")
    assert result["verdict"] in ["SEAL", "VOID", "SABAR", "PARTIAL", "888_HOLD"]

def test_mcp_trinity_tools():
    """Test all 5 MCP tools."""
    from canonical_core.mcp.tools import mcp_trinity
    # Test init_000, agi_genius, asi_act, apex_judge, vault_999
    pass

def test_apex_prime_verdict():
    """Test APEX PRIME makes constitutional verdicts."""
    from canonical_core.apex_prime import APEXPrime
    apex = APEXPrime()
    verdict = apex.judge_output(delta_bundle={}, omega_bundle={}, response="Test", session_id="test")
    assert verdict.verdict in ["SEAL", "VOID", "SABAR", "PARTIAL"]
EOF

# Run full test suite
python -m pytest canonical_core/tests/ -v --cov=canonical_core
```

**Day 4-5 (4h):**
```bash
# Benchmark performance
python -m scripts/benchmark_canonical_core.py

# Expected results:
# - init_000: <80ms
# - agi_genius: <100ms
# - asi_act: <120ms
# - apex_judge: <150ms
# - Full pipeline (000-999): <500ms

# Verify entropy
# Target: ΔS = -0.12 (clarity increasing)
```

**Week 5 Deliverable:** ✅ Full test coverage + performance benchmarks

#### Week 6: Deployment Readiness

**Day 1-2 (4h):**
```bash
# Create deployment scripts
cat > canonical_core/deploy.sh << 'EOF'
#!/bin/bash
# Deploy canonical_core to Railway/Cloud Run

# Install dependencies
pip install -e .

# Run migrations (if any)
python scripts/migrate_ledger.py

# Start MCP server
python -m canonical_core.mcp.sse --port 8000
EOF

chmod +x canonical_core/deploy.sh
```

**Day 3-4 (4h):**
```bash
# Create Docker image
cat > canonical_core/Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app
COPY . /app/

RUN pip install -e .

CMD ["python", "-m", "canonical_core.mcp.sse"]
EOF

# Build and test
docker build -t canonical_core:v52 .
docker run -p 8000:8000 canonical_core:v52
```

**Day 5 (2h):**
```bash
# Deploy to staging
railway up --environment=staging

# Monitor health
curl https://canonical-core-staging.railway.app/health

# Run smoke tests
python scripts/smoke_test_production.py --env=staging
```

**Week 6 Deliverable:** ✅ Production deployment to Railway/Cloud Run

---

## 📐 FINAL TARGET ARCHITECTURE

### Directory Structure (After Migration)

```
canonical_core/                          # Clean, low-entropy structure
├── __init__.py                          # Main exports
├── README.md                            # Documentation
│
├── types.py                             # ← NEW: Verdict, Metrics, FloorCheckResult
├── apex_prime.py                        # ← NEW: Stage 888 Judge
├── constitutional_floors.py             # ✅ EXISTS: F1-F13 definitions
├── floors.py                            # ✅ EXISTS: Floor validators
├── authority.py                         # ✅ EXISTS: F11 Command Authority
├── bundle_store.py                      # ✅ EXISTS: Session state
├── state.py                             # ✅ EXISTS: SessionState + cooling
├── zkpc.py                              # ✅ EXISTS: Crypto proofs
├── entropy_compressor.py                # ✅ EXISTS: ΔS computation
├── exceptions.py                        # ✅ EXISTS: Error types
├── pipeline.py                          # ← NEW: Unified 000-999 orchestration
│
├── engines/                             # ← REFACTORED: Unified Trinity
│   ├── __init__.py                      # KernelManager
│   ├── agi/                             # Δ Mind (from agi_room)
│   │   ├── __init__.py
│   │   ├── stage_111_sense.py           # ✅ EXISTS
│   │   ├── stage_222_think.py           # ✅ EXISTS
│   │   ├── stage_333_reason.py          # ✅ EXISTS
│   │   ├── executor.py                  # ✅ EXISTS
│   │   ├── hardening.py                 # ✅ EXISTS
│   │   ├── atlas.py                     # ← NEW: ATLAS-333 routing
│   │   ├── clarity_scorer.py            # ← NEW: ΔS precision
│   │   └── entropy.py                   # ← NEW: Expanded entropy
│   ├── asi/                             # Ω Heart (from asi_room)
│   │   ├── __init__.py
│   │   ├── stage_555_empathy.py         # ✅ EXISTS
│   │   ├── asi_engine.py                # ✅ EXISTS
│   │   ├── tom/                         # ← NEW: Theory of Mind
│   │   └── cooling.py                   # ← NEW: Async cooling engine
│   └── apex/                            # Ψ Soul (from arifos/core/apex)
│       ├── __init__.py
│       ├── kernel.py                    # ← NEW: APEXJudicialCore
│       ├── psi_kernel.py                # ← NEW: Ψ calculations
│       ├── floor_checks.py              # ← NEW: APEX floor validation
│       ├── contracts/                   # ← NEW: Output contracts
│       └── governance/                  # ← NEW: Merkle, zkPC, proofs
│
├── stages/                              # ← OPTIONAL: Root-level stages (alternative)
│   ├── stage_444_trinity.py             # ✅ EXISTS (currently stage_444.py)
│   ├── stage_555_empathy.py             # ✅ EXISTS (currently stage_555.py)
│   ├── stage_666_align.py               # ✅ EXISTS (currently stage_666.py)
│   ├── stage_777_forge.py               # ← NEW
│   ├── stage_888_judge.py               # ← NEW
│   └── stage_889_proof.py               # ← NEW
│
├── mcp/                                 # ← NEW: MCP server & tools
│   ├── __init__.py
│   ├── server.py                        # ← NEW: stdio transport
│   ├── sse.py                           # ← NEW: SSE transport
│   ├── trinity_server.py                # ← NEW: FastAPI wrapper
│   ├── bridge.py                        # ← NEW: Kernel delegation
│   ├── models.py                        # ← NEW: MCP data models
│   ├── metrics.py                       # ← NEW: Prometheus metrics
│   └── tools/                           # ← NEW: 5 Trinity tools
│       ├── mcp_trinity.py               # Bundle: all 5 tools
│       ├── mcp_agi_kernel.py            # agi_genius tool
│       ├── mcp_asi_kernel.py            # asi_act tool
│       └── mcp_apex_kernel.py           # apex_judge tool
│
├── memory/                              # ← EXPANDED: Full memory system
│   ├── ledger/                          # ← NEW: Multiple backends
│   │   ├── base_ledger.py               # ✅ EXISTS
│   │   ├── sqlite_ledger_store.py       # ← NEW
│   │   ├── postgres_ledger.py           # ← NEW
│   │   ├── cooling_ledger.py            # ← NEW
│   │   ├── merkle_ledger.py             # ← NEW
│   │   └── codex_ledger.py              # ← NEW
│   ├── constitutional_memory/           # ← NEW: Floor memory
│   │   ├── constitutional_ledger.py
│   │   ├── floor_memory.py
│   │   └── governance_record.py
│   └── scars/                           # ← NEW: Void history
│       ├── void_scanner.py
│       └── scar_manager.py
│
├── vault/                               # ✅ EXISTS
│   ├── learning_loop.py
│   └── ...
│
├── 000_space/                           # ✅ EXISTS: Stage 000
│   └── 000_init/
│       ├── stage_000_core.py
│       ├── ignition.py
│       └── mcp_bridge.py
│
├── micro_loop/                          # ✅ EXISTS: Basic orchestration
│   ├── executor.py
│   └── cooling_scheduler.py
│
├── contracts/                           # ← NEW: Type contracts
│   └── apex_output.py
│
└── tests/                               # ✅ EXISTS: Test suite
    ├── test_full_pipeline.py            # ← NEW
    ├── test_mcp_tools.py                # ← NEW
    └── ...
```

**Total Files After Migration:** ~75 files (vs 34 now, vs 383 in arifos/core)

**Key Principles:**
- ✅ **Flat structure** for core files (apex_prime.py, types.py at root)
- ✅ **Unified engines/** directory (AGI/ASI/APEX together)
- ✅ **Clear MCP separation** (mcp/ directory)
- ✅ **Modular memory** (ledger, constitutional_memory, scars)
- ✅ **Optional stages/** for root-level stage imports (or keep stage_*.py at root)

---

## 📊 ENTROPY COMPARISON (Before vs After)

### Current State (Week 0)

```
canonical_core: 34 files
- Structure: ΔS = -0.15 (very clean)
- Completeness: 35%
- Verdict: Clean skeleton, not production-ready
```

### After Phase 1 (Week 2)

```
canonical_core: ~50 files
- Structure: ΔS = -0.12 (clean)
- Completeness: 75%
- Verdict: Functionally complete, MCP-ready
```

### After Phase 2 (Week 4)

```
canonical_core: ~65 files
- Structure: ΔS = -0.10 (very clean, unified engines)
- Completeness: 90%
- Verdict: Production-ready with full memory system
```

### After Phase 3 (Week 6)

```
canonical_core: ~75 files
- Structure: ΔS = -0.08 (minimal entropy)
- Completeness: 100%
- Verdict: Production-deployed with monitoring
```

**Comparison with arifos/core:**
- arifos/core: 383 files, ΔS = +0.25 (high entropy)
- canonical_core final: 75 files, ΔS = -0.08 (low entropy)
- **Improvement:** 80% fewer files, 33% lower entropy

---

## ✅ SUCCESS CRITERIA

### Week 2 (Phase 1 Complete)

- [ ] All 10 stages (000-999) exist and import successfully
- [ ] APEX PRIME class functional (`judge_output()` works)
- [ ] MCP server starts and responds to health checks
- [ ] All 5 Trinity tools register (init_000, agi_genius, asi_act, apex_judge, vault_999)

### Week 4 (Phase 2 Complete)

- [ ] Unified `engines/` directory with AGI/ASI/APEX
- [ ] SQLite ledger backend operational
- [ ] Constitutional memory system tracking floor violations
- [ ] Full pipeline test passes (000 → 999)

### Week 6 (Phase 3 Complete)

- [ ] Test coverage ≥85%
- [ ] MCP tool latency <100ms average
- [ ] Deployed to Railway staging environment
- [ ] Smoke tests passing in production

---

## 🚀 IMMEDIATE NEXT STEPS (This Week)

### Priority Order

1. **Copy APEX PRIME** (2h)
   ```bash
   cp arifos/core/system/apex_prime.py canonical_core/apex_prime.py
   cp arifos/core/system/types.py canonical_core/types.py
   ```

2. **Copy APEX Engine** (4h)
   ```bash
   cp -r arifos/core/apex canonical_core/apex
   # Update imports
   ```

3. **Copy Missing Stages** (2h)
   ```bash
   cp arifos/core/stage/stage_777_forge.py canonical_core/stage_777_forge.py
   cp arifos/core/stage/stage_888_judge.py canonical_core/stage_888_judge.py
   cp arifos/core/stage/stage_889_proof.py canonical_core/stage_889_proof.py
   ```

4. **Create Pipeline Orchestrator** (2h)
   ```bash
   # New file: canonical_core/pipeline.py
   # Wires all 10 stages together
   ```

5. **Test End-to-End** (2h)
   ```bash
   python -m pytest canonical_core/tests/test_full_pipeline.py
   ```

**Total Effort This Week:** 12 hours (1.5 days)

---

**DITEMPA BUKAN DIBERI** — We forge the production system through deliberate migration, not wishful thinking.

**Authority:** Muhammad Arif bin Fazil | Penang, Malaysia  
**Status:** ROADMAP APPROVED ✅  
**Next Action:** Begin Phase 1, Day 1 (Copy APEX PRIME)  
**Target:** Production-ready canonical_core in 6 weeks  
**Date:** 2026-01-26  
**Version:** v52.5.1-SEAL
