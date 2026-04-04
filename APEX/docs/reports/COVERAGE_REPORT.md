# arifosmcp Code Coverage Report
**Date:** 2026-03-14  
**Total Tests Run:** 409 passed, 2 failed  
**Overall Coverage:** 49% (7,383 / 15,221 lines)

---

## Executive Summary

| Category | Coverage | Lines | Status |
|----------|----------|-------|--------|
| **Constitutional Kernel** | 85% | 2,847 / 3,351 | ✅ GOOD |
| **Runtime Tools** | 62% | 2,852 / 4,619 | ⚠️ MEDIUM |
| **Intelligence Tools** | 25% | 1,176 / 4,704 | 🔴 LOW |
| **WebMCP Layer** | 0% | 0 / 714 | 🔴 CRITICAL |
| **Security Modules** | 46% | 63 / 137 | ⚠️ MEDIUM |

---

## Key Components Coverage

### 1. CONSTITUTIONAL KERNEL (core/) 🏛️

**Overall: 85%** - This is the heart of arifOS

| Module | Coverage | Lines | Critical? |
|--------|----------|-------|-----------|
| `governance_kernel.py` | **85%** | 377/442 | ✅ YES |
| `governance_engine.py` | **81%** | 287/353 | ✅ YES |
| `kernel/engine_adapters.py` | **88%** | 171/194 | ✅ YES |
| `kernel/stage_orchestrator.py` | **92%** | 167/182 | ✅ YES |
| `kernel/heuristics.py` | **98%** | 44/45 | ✅ YES |
| `kernel/init_000_anchor.py` | **97%** | 68/70 | ✅ YES |
| `enforcement/genius.py` | **87%** | 125/144 | ✅ YES |
| `enforcement/aki_contract.py` | **92%** | 65/71 | ⚠️ |
| `kernel/constants.py` | **100%** | 29/29 | ✅ |
| `judgment.py` | **77%** | 94/122 | ✅ |

**Critical Gaps:**
- `governance_engine.py:576-587` - Error handling paths
- `governance_kernel.py:260-302` - Pipeline routing edge cases
- `judgment.py:335-404` - Verdict rendering branches

---

### 2. RUNTIME LAYER (arifosmcp/runtime/) ⚙️

**Overall: 62%** - The MCP server runtime

| Module | Coverage | Lines | Status |
|--------|----------|-------|--------|
| `tools.py` | **62%** | 261/420 | ⚠️ MEDIUM |
| `orchestrator.py` | **78%** | 137/176 | ✅ GOOD |
| `models.py` | **95%** | 265/278 | ✅ EXCELLENT |
| `public_registry.py` | **70%** | 76/108 | ⚠️ |
| `reality_handlers.py` | **57%** | 98/171 | ⚠️ |
| `reality_models.py` | **100%** | 93/93 | ✅ |
| `contracts.py` | **52%** | 16/31 | ⚠️ |
| `bridge.py` | **38%** | 107/280 | 🔴 |

**Critical Gaps:**
- `tools.py:389-422` - Forge handler (critical tool)
- `tools.py:604-631` - Memory operations
- `bridge.py:627-760` - Transport bridge (lots of dead code?)
- `reality_handlers.py:303-320` - Brave search error handling

---

### 3. INTELLIGENCE TOOLS (arifosmcp/intelligence/tools/) 🧠

**Overall: 25%** - Very low coverage - needs attention

| Module | Coverage | Lines | Status |
|--------|----------|-------|--------|
| `chroma_query.py` | **12%** | 8/64 | 🔴 CRITICAL |
| `reality_grounding.py` | **25%** | 103/404 | 🔴 |
| `vector_bridge.py` | **46%** | 70/152 | ⚠️ |
| `system_monitor.py` | **10%** | 14/145 | 🔴 |
| `log_reader.py` | **15%** | 8/52 | 🔴 |
| `safety_guard.py` | **10%** | 6/63 | 🔴 |
| `aclip_base.py` | **30%** | 11/37 | ⚠️ |
| `envelope.py` | **38%** | 35/92 | ⚠️ |
| `wisdom_quotes.py` | **78%** | 54/69 | ✅ |
| `embeddings/__init__.py` | **86%** | 18/21 | ✅ |

**Critical Gaps:**
- All tools need integration tests
- `chroma_query.py` - Only 8/64 lines covered (the fix I made isn't tested)
- `reality_grounding.py` - Only 25% covered (400+ lines untested)
- `system_monitor.py` - Only 10% covered (container detection not tested)

---

### 4. ORGANS (core/organs/) 🫀

**Overall: 76%** - The Trinity implementation

| Module | Coverage | Lines | Status |
|--------|----------|-------|--------|
| `_0_init.py` | **63%** | 120/191 | ⚠️ |
| `_1_agi.py` | **95%** | 40/42 | ✅ |
| `_2_asi.py` | **54%** | 37/68 | ⚠️ |
| `_3_apex.py` | **66%** | 51/77 | ⚠️ |
| `_4_vault.py` | **78%** | 96/123 | ✅ |
| `unified_memory.py` | **80%** | 79/99 | ✅ |

---

### 5. PHYSICS ENGINE (core/physics/) ⚛️

**Overall: 67%** - Thermodynamic calculations

| Module | Coverage | Lines | Status |
|--------|----------|-------|--------|
| `thermodynamics_hardened.py` | **67%** | 157/235 | ⚠️ |
| `thermo_budget.py` | **86%** | 126/146 | ✅ |
| `thermodynamic_enforcement.py` | **92%** | 34/37 | ✅ |
| `thermodynamics.py` | **30%** | 33/111 | 🔴 |

---

### 6. SECURITY (core/security/ & guards/) 🛡️

**Overall: 46%** - Security is under-tested

| Module | Coverage | Lines | Status |
|--------|----------|-------|--------|
| `scanner.py` | **0%** | 0/53 | 🔴 CRITICAL |
| `tokens.py` | **0%** | 0/84 | 🔴 CRITICAL |
| `guards/injection_guard.py` | **93%** | 66/71 | ✅ |
| `guards/ontology_guard.py` | **97%** | 34/35 | ✅ |
| `risk_engine.py` | **100%** | 29/29 | ✅ |

**CRITICAL:** Security scanner and token modules have ZERO coverage!

---

### 7. WEBMCP LAYER (arifosmcp/runtime/webmcp/) 🌐

**Overall: 0%** - Completely untested

| Module | Coverage | Lines | Status |
|--------|----------|-------|--------|
| `server.py` | **0%** | 0/164 | 🔴 CRITICAL |
| `governance.py` | **0%** | 0/172 | 🔴 CRITICAL |
| `live_metrics.py` | **0%** | 0/202 | 🔴 CRITICAL |
| `security.py` | **0%** | 0/76 | 🔴 CRITICAL |
| `session.py` | **0%** | 0/71 | 🔴 CRITICAL |
| `config.py` | **0%** | 0/24 | 🔴 |

**714 lines of WebMCP code completely untested!**

---

### 8. SHARED UTILITIES (core/shared/) 🧰

**Overall: 63%** - Mixed coverage

| Module | Coverage | Lines | Status |
|--------|----------|-------|--------|
| `floors.py` | **63%** | 261/412 | ⚠️ |
| `atlas.py` | **85%** | 171/201 | ✅ |
| `types.py` | **98%** | 290/297 | ✅ |
| `physics.py` | **40%** | 143/360 | 🔴 |
| `guards/injection_guard.py` | **93%** | 66/71 | ✅ |
| `guards/ontology_guard.py` | **97%** | 34/35 | ✅ |
| `manifest_loader.py` | **78%** | 40/51 | ✅ |

---

## Coverage by Architectural Layer

```
┌─────────────────────────────────────────────┐
│  APEX LAYER (888_JUDGE)                     │
│  Coverage: 77% (judgment.py)               │
│  Status: ✅ GOOD                           │
├─────────────────────────────────────────────┤
│  ASI LAYER (Heart - 666)                    │
│  Coverage: 54% (_2_asi.py)                 │
│  Status: ⚠️ NEEDS WORK                     │
├─────────────────────────────────────────────┤
│  AGI LAYER (Mind - 333)                     │
│  Coverage: 95% (_1_agi.py)                 │
│  Status: ✅ EXCELLENT                      │
├─────────────────────────────────────────────┤
│  VAULT LAYER (999)                          │
│  Coverage: 78% (_4_vault.py)               │
│  Status: ✅ GOOD                           │
├─────────────────────────────────────────────┤
│  RUNTIME LAYER                              │
│  Coverage: 62%                              │
│  Status: ⚠️ MEDIUM                          │
├─────────────────────────────────────────────┤
│  INTELLIGENCE LAYER                         │
│  Coverage: 25%                              │
│  Status: 🔴 CRITICAL                        │
├─────────────────────────────────────────────┤
│  WEBMCP LAYER                               │
│  Coverage: 0%                               │
│  Status: 🔴 CRITICAL                        │
└─────────────────────────────────────────────┘
```

---

## Critical Gaps Requiring Immediate Attention

### 🔴 CRITICAL (0-30% coverage)

1. **`core/security/scanner.py`** - 0% (53 lines)
   - Security scanner completely untested
   - Risk: Vulnerabilities undetected

2. **`core/security/tokens.py`** - 0% (84 lines)
   - Token handling untested
   - Risk: Auth bypass vulnerabilities

3. **`arifosmcp/runtime/webmcp/`** - 0% (714 lines total)
   - Entire WebMCP layer untested
   - Risk: Web interface bugs

4. **`arifosmcp/intelligence/tools/chroma_query.py`** - 12% (8/64 lines)
   - The fix I just made isn't tested!
   - Risk: Qdrant API compatibility regressions

5. **`arifosmcp/intelligence/tools/system_monitor.py`** - 10% (14/145 lines)
   - Container detection not tested
   - Risk: Container environments fail silently

### 🟡 HIGH PRIORITY (30-60% coverage)

6. **`arifosmcp/runtime/bridge.py`** - 38% (107/280 lines)
7. **`arifosmcp/intelligence/tools/reality_grounding.py`** - 25% (103/404 lines)
8. **`core/shared/physics.py`** - 40% (143/360 lines)
9. **`core/organs/_2_asi.py`** - 54% (37/68 lines)

---

## Recommendations

### Immediate (This Sprint)

1. **Add WebMCP Tests** (714 lines)
   - Priority: CRITICAL
   - Estimated effort: 3-4 days
   - Write integration tests for web server

2. **Security Module Tests** (137 lines)
   - Priority: CRITICAL
   - Estimated effort: 1-2 days
   - Test scanner and token modules

3. **Intelligence Tools Tests**
   - Priority: HIGH
   - Estimated effort: 5-7 days
   - Test all tools with mocked external services

### Short Term (Next 2 Weeks)

4. **Bridge Module Tests** (280 lines)
5. **ASI Organ Tests** (_2_asi.py)
6. **Physics Engine Tests** (360 lines)

### Medium Term (Next Month)

7. **Runtime Tools Edge Cases** (tools.py gaps)
8. **Reality Handlers** (error paths)
9. **Thermodynamics** (edge cases)

---

## Test Files Analysis

**Total Test Files Found:** 50+  
**Tests Passing:** 409  
**Tests Failing:** 2 (both due to missing Qdrant connection)

**Strongest Test Coverage:**
- `tests/03_constitutional/` - F2, F7, F8 floors (29 tests)
- `tests/core/enforcement/` - Governance engine (30+ tests)
- `tests/core/kernel/` - Kernel internals (70+ tests)
- `tests/adversarial/` - Injection attacks (50+ tests)

**Missing Test Coverage:**
- No WebMCP tests
- No security scanner tests
- Minimal intelligence tools tests
- No container-specific tests

---

## Action Items

1. **Create `tests/05_webmcp/`** - Test entire WebMCP layer
2. **Create `tests/security/`** - Test scanner and tokens
3. **Expand `tests/intelligence/`** - Test all tools with mocks
4. **Fix failing tests** - 2 tests failing due to Qdrant connection
5. **Add container tests** - Test system_monitor in Docker

---

*Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]*

**Overall Assessment:** Constitutional kernel is solid (85%), but peripheral components need significant testing work. Priority: WebMCP + Security modules.
