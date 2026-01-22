# 🔄 Quantum Migration Patterns

**Guide for migrating from Pipeline Legacy to Quantum Executor**

---

## 📋 Pattern 1: Simple Pipeline Execution

### **Before (Pipeline Legacy):**
```python
from arifos_core.system.pipeline import Pipeline, PipelineState

# Create pipeline
pipeline = Pipeline()

# Run pipeline
state = pipeline.run(query="What is photosynthesis?")

# Access results
verdict = state.verdict  # ConstitutionalVerdict
response = state.draft_response  # str
```

### **After (Quantum Executor):**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_sync, QuantumState

# Run quantum governance (sync version)
state = govern_query_sync(query="What is photosynthesis?")

# Access results
verdict = state.final_verdict  # "SEAL" | "VOID" | "PARTIAL"
response = state.apex_particle.response if state.apex_particle else ""
```

**Key Differences:**
- No Pipeline() instantiation needed
- Single function call instead of create→run
- Verdict is a string, not ConstitutionalVerdict object
- Response is in `apex_particle.response`

---

## 📋 Pattern 2: Async Pipeline Execution (API Routes)

### **Before (Pipeline Legacy):**
```python
from arifos_core.system.pipeline import Pipeline

pipeline = Pipeline()
state = pipeline.run(query)  # Synchronous blocking call

verdict = str(state.verdict) if state.verdict else "UNKNOWN"
response = state.draft_response or ""
```

### **After (Quantum Executor):**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_async

# Use async/await for better performance
state = await govern_query_async(query)

verdict = state.final_verdict  # Already a string
response = state.apex_particle.response if state.apex_particle else ""
```

**Key Differences:**
- Use `govern_query_async` for async contexts (FastAPI routes)
- No Pipeline() object, direct function call
- Better performance through parallel execution

---

## 📋 Pattern 3A: AAA-Level Helper (RECOMMENDED) ⚡

### **The Quantum Way - Use the Helper:**
```python
from arifos_core.mcp.helpers import generate_and_validate_async

# One call - LLM generation ⊥ Quantum validation
draft, state = await generate_and_validate_async(
    query="What is photosynthesis?",
    llm_model="gpt-4"  # or "aisingapore/sea-lion-v3-70b"
)

# Check verdict
if state.final_verdict == "SEAL":
    return draft  # Constitutionally approved
else:
    return f"Blocked: {state.apex_particle.reason}"
```

**Why This is AAA-Level:**
- ✅ **Orthogonality:** LLM ⊥ Quantum (dot_product = 0)
- ✅ **Simple API:** One function call
- ✅ **Constitutional:** Quantum validates EXTERNAL text
- ✅ **Flexible:** Can swap LLM models easily

### **For Advanced Users - Manual Control:**
```python
from arifos_core.mcp.orthogonal_executor import govern_query_async
import litellm

# 1. Generate (your responsibility)
response = await litellm.acompletion(
    model="gpt-4",
    messages=[{"role": "user", "content": query}]
)
draft = response.choices[0].message.content

# 2. Validate (quantum responsibility)
state = await govern_query_async(
    query=query,
    context={"draft_response": draft}
)

# 3. Use if approved
if state.final_verdict == "SEAL":
    return draft
```

---

## 📋 Pattern 3B: Pipeline with Custom LLM Backend (Legacy)

### **Before (Pipeline Legacy):**
```python
from arifos_core.system.pipeline import Pipeline

def my_llm(prompt: str) -> str:
    # Custom LLM logic
    return litellm.completion(model="gpt-4", messages=[{"role": "user", "content": prompt}])

pipeline = Pipeline(llm_generate=my_llm)
state = pipeline.run(query)
```

### **After (AAA Helper):**
```python
from arifos_core.mcp.helpers import generate_and_validate_async

# Replace custom LLM + pipeline with helper
draft, state = await generate_and_validate_async(
    query=query,
    llm_model="gpt-4",
    llm_messages=[{"role": "user", "content": query}]
)

if state.final_verdict == "SEAL":
    return draft
```

**Key Differences:**
- Quantum executor focuses on **validation**, not generation
- Separate LLM generation from constitutional governance
- Helper function makes migration easy (AAA-level simplicity)

---

## 📋 Pattern 4: Accessing Metrics

### **Before (Pipeline Legacy):**
```python
state = pipeline.run(query)

if state.final_verdict and state.final_verdict.floors:
    truth = state.final_verdict.floors.truth
    peace = state.final_verdict.floors.peace_squared
    empathy = state.final_verdict.floors.kappa_r
```

### **After (Quantum Executor):**
```python
state = govern_query_sync(query)

# Access metrics from specific particles
agi_truth = state.agi_particle.truth_score if state.agi_particle else None
asi_peace = state.asi_particle.peace_score if state.asi_particle else None
asi_empathy = state.asi_particle.kappa_r if state.asi_particle else None

# Or calculate forces
from arifos_core.mcp.orthogonal_executor import ConstitutionalForces
forces = ConstitutionalForces.calculate_pressure(state)
print(forces["truth_pressure"])  # AGI truth force
print(forces["peace_field"])  # ASI peace force
```

**Key Differences:**
- Metrics separated by particle (AGI, ASI, APEX)
- Use `ConstitutionalForces.calculate_pressure()` for force model
- No single "floors" object, distributed across particles

---

## 📋 Pattern 5: Error Handling

### **Before (Pipeline Legacy):**
```python
try:
    pipeline = Pipeline()
    state = pipeline.run(query)
    if state.verdict == Verdict.VOID:
        print("Floor violation!")
except Exception as e:
    print(f"Pipeline error: {e}")
```

### **After (Quantum Executor):**
```python
try:
    state = govern_query_sync(query)
    if state.final_verdict == "VOID":
        # Access specific violations
        agi_reason = state.agi_particle.reason if state.agi_particle else None
        asi_reason = state.asi_particle.reason if state.asi_particle else None
        apex_reason = state.apex_particle.reason if state.apex_particle else None
        print(f"Violations: {agi_reason}, {asi_reason}, {apex_reason}")
except Exception as e:
    print(f"Quantum executor error: {e}")
```

**Key Differences:**
- Verdict is string ("VOID"), not enum (Verdict.VOID)
- Failure reasons distributed across particles
- Simpler error surface (fewer exception types)

---

## 📋 Pattern 6: Compatibility Stub (For Gradual Migration)

If you can't migrate all code at once, create a compatibility wrapper:

```python
# arifos_core/system/pipeline.py
import warnings
from arifos_core.mcp.orthogonal_executor import govern_query_sync, QuantumState

warnings.warn(
    "arifos_core.system.pipeline is deprecated. "
    "Use arifos_core.mcp.orthogonal_executor instead.",
    DeprecationWarning,
    stacklevel=2
)

class Pipeline:
    """Compatibility wrapper - DEPRECATED v47+"""

    def __init__(self, llm_generate=None, ledger_sink=None):
        warnings.warn(
            "Pipeline class is deprecated. Use govern_query_sync/async instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.llm_generate = llm_generate
        self.ledger_sink = ledger_sink

    def run(self, query: str, **kwargs) -> QuantumState:
        """Run quantum executor with pipeline compatibility"""
        # Note: This loses some pipeline-specific features
        # Full migration to quantum API is recommended
        return govern_query_sync(query)

# Re-export for compatibility
PipelineState = QuantumState
```

---

## 🎯 Migration Checklist

For each file being migrated:

- [ ] Replace `from arifos_core.system.pipeline import Pipeline`
  - **With:** `from arifos_core.mcp.orthogonal_executor import govern_query_sync` (or `govern_query_async`)

- [ ] Replace `pipeline = Pipeline(...)`
  - **With:** Direct function call `govern_query_sync(query)`

- [ ] Replace `state.verdict` access
  - **With:** `state.final_verdict` (now a string)

- [ ] Replace `state.draft_response` access
  - **With:** `state.apex_particle.response` (if needed)

- [ ] Update metrics access from `state.final_verdict.floors.X`
  - **With:** Particle-specific access or `ConstitutionalForces.calculate_pressure(state)`

- [ ] For async contexts (FastAPI, etc.)
  - **Use:** `await govern_query_async(query)` instead of sync

- [ ] Remove LLM backend from pipeline initialization
  - **Separate:** LLM generation from constitutional validation

- [ ] Test migrated code with quantum executor

---

## 📚 Quick Reference

| Pipeline Legacy | Quantum Executor |
|----------------|------------------|
| `Pipeline()` | `govern_query_sync(query)` |
| `Pipeline(llm_generate=fn)` | Separate generation + validation |
| `state.verdict` | `state.final_verdict` (string) |
| `state.draft_response` | `state.apex_particle.response` |
| `state.final_verdict.floors.truth` | `state.agi_particle.truth_score` |
| `Verdict.SEAL` (enum) | `"SEAL"` (string) |
| Synchronous blocking | Async parallel execution |
| 2500 lines | 318 lines |
| Complex API | Simple function calls |

---

**DITEMPA BUKAN DIBERI**
*Migration patterns forged from real code analysis, not assumptions.*

🌋⚛️🚀
