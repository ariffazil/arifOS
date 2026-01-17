# 🚀 Quantum Migration Plan - From Pipeline to Orthogonal Executor

**Date:** 2026-01-17
**Status:** 🟡 IN PROGRESS
**Target:** v48.0.0 (Full deprecation of pipeline_legacy.py)

---

## 📊 Migration Scope

**Total Files Affected:** 62 files importing from `arifos_core.system.pipeline`

### **File Categories:**

| Category | Count | Priority | Status |
|----------|-------|----------|--------|
| **Production Code** | 8 | 🔴 HIGH | ⏳ Pending |
| **Integration/API** | 4 | 🟡 MEDIUM | ⏳ Pending |
| **Tests** | 20 | 🟢 LOW | ⏳ Can wait |
| **Demos/Examples** | 12 | 🟢 LOW | ⏳ Can wait |
| **Documentation** | 8 | 🟡 MEDIUM | ⏳ Pending |
| **Archive** | 10 | ⚪ SKIP | N/A Already archived |

---

## 🔴 **PHASE 1: Critical Production Code (Priority: HIGH)**

These files power core functionality and need immediate migration:

### **1. arifos_core/integration/adapters/governed_llm.py**
**Current:**
```python
from arifos_core.system.pipeline import Pipeline, PipelineState
```

**Migrate to:**
```python
from arifos_core.mcp.orthogonal_executor import OrthogonalExecutor, QuantumState
```

**Impact:** High - Core LLM governance adapter
**Estimated Effort:** 2-3 hours (need to adapt from sequential to parallel)

---

### **2. arifos_core/integration/api/routes/pipeline.py**
**Current:**
```python
from arifos_core.system.pipeline import Pipeline
```

**Migrate to:**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_async
```

**Impact:** High - API endpoint for pipeline execution
**Estimated Effort:** 1-2 hours (REST API wrapper)

---

### **3. arifos_core/integration/sealion_suite/evaluator.py**
**Current:**
```python
from arifos_core.system.pipeline import Pipeline
```

**Migrate to:**
```python
from arifos_core.mcp.orthogonal_executor import OrthogonalExecutor
```

**Impact:** Medium-High - SeaLion evaluation system
**Estimated Effort:** 2 hours

---

### **4. arifos_core/system/__main__.py**
**Current:**
```python
from arifos_core.system.pipeline import Pipeline
```

**Migrate to:**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_sync
```

**Impact:** High - CLI entry point
**Estimated Effort:** 1 hour

---

### **5. L6_SEALION/cli/sealion_unified.py**
**Current:**
```python
from arifos_core.system.pipeline import Pipeline
```

**Migrate to:**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_async
```

**Impact:** Medium - SeaLion CLI
**Estimated Effort:** 1-2 hours

---

### **6. arifos_core/system/pipeline.py (Compatibility Stub)**
**Current:** Re-exports from `pipeline_legacy.py`

**Migrate to:**
```python
# Add deprecation warning
import warnings
warnings.warn(
    "arifos_core.system.pipeline is deprecated. "
    "Use arifos_core.mcp.orthogonal_executor instead.",
    DeprecationWarning,
    stacklevel=2
)

# Provide migration path
from ..mcp.orthogonal_executor import (
    OrthogonalExecutor as Pipeline,  # Alias for backward compat
    QuantumState as PipelineState,
    govern_query_sync as run_pipeline
)
```

**Impact:** Critical - Central import point
**Estimated Effort:** 30 minutes

---

## 🟡 **PHASE 2: Integration Layer (Priority: MEDIUM)**

### **Integration Files:**
1. `arifos_core/integration/api/routes/health.py` - API health checks
2. `arifos_core/mcp/tools/judge.py` - MCP judge tool
3. `L6_SEALION/cli/sealion_verdict_probe.py` - Verdict probing
4. `L6_SEALION/cli/sealion_governed_client.py` - Governed client

**Strategy:** Add quantum executor alongside pipeline, test in parallel, then deprecate.

---

## 🟢 **PHASE 3: Tests & Demos (Priority: LOW)**

### **Test Files (20 files):**
- Can remain on pipeline for regression testing
- Add new quantum executor tests
- Mark as "legacy compatibility tests"

### **Demo Files (12 files in L7_DEMOS/):**
- Update examples to showcase quantum executor
- Keep old examples as "legacy" folder

---

## 📚 **PHASE 4: Documentation (Priority: MEDIUM)**

### **Documentation Updates:**
1. Update all guides to reference `orthogonal_executor.py`
2. Add migration examples
3. Mark pipeline references as "Legacy (v45-v46)"
4. Link to `QUANTUM_MIGRATION.md`

---

## 🗑️ **PHASE 5: Archive (v48.0.0)**

### **Files to Archive:**
```
archive/v47_pipeline_legacy/
├── pipeline_legacy.py
├── pipeline.py (stub)
├── tests/
│   └── (all pipeline tests)
└── examples/
    └── (all pipeline examples)
```

---

## 🔧 **Migration Code Templates**

### **Template 1: Simple Function Migration**

**Before:**
```python
from arifos_core.system.pipeline import Pipeline

def govern_query(query: str):
    pipeline = Pipeline()
    result = pipeline.run(query=query, llm_generate=my_llm)
    return result['verdict']
```

**After:**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_sync

def govern_query(query: str):
    state = govern_query_sync(query, context={})
    return state.final_verdict
```

---

### **Template 2: Async Migration**

**Before:**
```python
from arifos_core.system.pipeline import Pipeline

async def govern_query_async(query: str):
    # Can't async with old pipeline
    pipeline = Pipeline()
    result = pipeline.run(query=query, llm_generate=my_llm)
    return result
```

**After:**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_async as govern

async def govern_query_async(query: str):
    state = await govern(query, context={})
    return {
        "verdict": state.final_verdict,
        "agi": state.agi_particle.verdict,
        "asi": state.asi_particle.verdict,
        "apex": state.apex_particle.verdict
    }
```

---

### **Template 3: API Endpoint Migration**

**Before:**
```python
from arifos_core.system.pipeline import Pipeline

@app.post("/govern")
def govern_endpoint(query: str):
    pipeline = Pipeline()
    result = pipeline.run(query=query, llm_generate=llm)
    return {"verdict": result['verdict']}
```

**After:**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_async

@app.post("/govern")
async def govern_endpoint(query: str):
    state = await govern_query_async(query)
    return {
        "verdict": state.final_verdict,
        "collapsed": state.collapsed,
        "measurement_time": state.measurement_time.isoformat()
    }
```

---

## 📊 **Estimated Timeline**

| Phase | Duration | Effort (Hours) | Target Date |
|-------|----------|----------------|-------------|
| **Phase 1** | 2 weeks | 10-15h | 2026-01-31 |
| **Phase 2** | 1 week | 5-8h | 2026-02-07 |
| **Phase 3** | 2 weeks | 8-12h | 2026-02-21 |
| **Phase 4** | 1 week | 4-6h | 2026-02-28 |
| **Phase 5** | 1 day | 2h | 2026-03-01 |
| **TOTAL** | ~6 weeks | 29-43h | v48.0.0 |

---

## ✅ **Migration Checklist**

### **Pre-Migration:**
- [x] Quantum executor functional and tested
- [x] Benchmark shows performance improvement
- [x] Migration documentation created
- [ ] Deprecation warnings added to pipeline.py
- [ ] CI/CD updated to test both paths

### **During Migration:**
- [ ] Phase 1: Critical production code migrated
- [ ] Phase 2: Integration layer migrated
- [ ] Phase 3: Tests updated
- [ ] Phase 4: Documentation updated
- [ ] All tests passing with quantum executor

### **Post-Migration (v48.0.0):**
- [ ] Archive `pipeline_legacy.py` to `archive/v47_pipeline_legacy/`
- [ ] Remove `pipeline.py` stub
- [ ] Update all imports to use `orthogonal_executor.py` directly
- [ ] Release notes published
- [ ] Migration guide finalized

---

## 🧪 **Testing Strategy**

### **Parallel Testing (During Migration):**
```python
# Test both implementations side-by-side
def test_quantum_vs_pipeline():
    query = "What is the capital of France?"

    # Old way
    pipeline = Pipeline()
    legacy_result = pipeline.run(query=query, llm_generate=llm)

    # New way
    quantum_state = govern_query_sync(query)

    # Compare verdicts
    assert legacy_result['verdict'] == quantum_state.final_verdict
```

### **Regression Tests:**
- Keep pipeline tests as "legacy compatibility suite"
- Add equivalent quantum executor tests
- Compare outputs to ensure constitutional consistency

---

## 🚨 **Risk Mitigation**

### **Risk 1: Breaking Changes**
**Mitigation:** Keep `pipeline.py` stub with deprecation warnings for v47.x

### **Risk 2: Performance Regression**
**Mitigation:** Run benchmark before and after migration

### **Risk 3: Integration Failures**
**Mitigation:** Migrate one integration at a time, test thoroughly

### **Risk 4: Documentation Lag**
**Mitigation:** Update docs alongside code changes

---

## 📞 **Support & Questions**

**Migration Issues?**
- Check: [`QUANTUM_QUICKSTART.md`](QUANTUM_QUICKSTART.md)
- Read: [`QUANTUM_MIGRATION.md`](QUANTUM_MIGRATION.md)
- Benchmark: [`QUANTUM_BENCHMARK.py`](QUANTUM_BENCHMARK.py)
- GitHub Issues: Tag with `migration` label

---

## 🌋 **DITEMPA BUKAN DIBERI**

**From rusty pipe to quantum forces.**
**From sequential to parallel.**
**From v47 legacy to v48 future.**

The migration is not just code refactoring—it's architectural evolution.

⚛️🚀
