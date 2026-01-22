# Architecture Refactoring: Unified LLM Backends v43

**Date**: 2025-12-19  
**Authority**: Muhammad Arif bin Fazil (arifOS Keeper)  
**Status**: ACTIVE REFACTORING  
**Supersedes**: llm_interface.py (deprecated)  

---

## Executive Summary

The arifOS project is consolidating **6 LLM backend adapters** (OpenAI, Anthropic, Gemini, SEA-LION, Llama, Perplexity) into a single **spec-driven architecture** that:

1. **Loads** `spec/v43/interface_and_authority.json` at runtime
2. **Validates** each backend against `llm_contract.required_capabilities`
3. **Provides** unified factory interface: `create_backend_from_spec(model_name, api_key)`
4. **Supports** streaming + non-streaming modes across all backends
5. **Enforces** F1–F9 floor constraints at adapter level

---

## New Folder Structure

```
arifos_core/
├── integration/
│   └── adapters/
│       ├── __init__.py
│       ├── governed_llm.py               [UNCHANGED — wrapper layer]
│       ├── llm_interface.py              [DEPRECATED — archive to L2_ARCHIVE/]
│       └── llm_backends_v43.py           [NEW — unified adapters]
│
├── system/
│   ├── pipeline.py
│   └── ...
│
└── memory/
    └── vault999.py

L2_ARCHIVE/                               [NEW FOLDER]
├── adapters_legacy/
│   ├── llm_interface.py                  [MOVED HERE — read-only]
│   ├── claude_adapter.py                 [if it exists]
│   ├── gpt_adapter.py                    [if it exists]
│   └── README.md                         [Deprecation notice]
```

---

## File Status Matrix

### New Files

| File | Status | Purpose |
|------|--------|----------|
| `llm_backends_v43.py` | ✅ ACTIVE | Unified backend adapters (spec-driven) |
| `spec/v43/interface_and_authority.json` | ✅ SEALED | Machine-readable spec (governance layer) |
| `REFACTORING_v43_BACKENDS.md` | ✅ ACTIVE | This document |

### Files to Archive

| File | Current Location | Archive Location | Reason |
|------|------------------|------------------|--------|
| `llm_interface.py` | `arifos_core/integration/adapters/llm_interface.py` | `L2_ARCHIVE/adapters_legacy/llm_interface.py` | Superseded by v43 unified adapters |

### Files to Keep Unchanged

| File | Reason |
|------|--------|
| `governed_llm.py` | Wrapper layer; works with any backend |
| `pipeline.py` | Core pipeline; backend-agnostic |
| All other core modules | No changes needed |

---

## Migration Path

### Phase 1: Parallel Operation (Now)

Both old and new adapters work side-by-side:

```python
# Old way (still works)
from arifos_core.integration.adapters.llm_interface import LLMInterface
llm = LLMInterface(backend=create_openai_backend(api_key))

# New way (recommended)
from arifos_core.integration.adapters.llm_backends_v43 import create_backend_from_spec
backend = create_backend_from_spec('gpt-4o', api_key='...')
```

### Phase 2: Deprecation Warning (v43.1+)

Add deprecation warnings to `llm_interface.py`:

```python
import warnings
warnings.warn(
    "llm_interface.py is deprecated. Use llm_backends_v43.create_backend_from_spec() instead.",
    DeprecationWarning,
    stacklevel=2
)
```

### Phase 3: Archive (v44.0)

Move old adapter to `L2_ARCHIVE/adapters_legacy/` with read-only access.

---

## Backend Coverage Matrix

| Backend | Class | Status | Capabilities | Notes |
|---------|-------|--------|--------------|-------|
| **OpenAI** | `OpenAIBackend` | ✅ ACTIVE | Full support | gpt-4o, gpt-4-turbo |
| **Anthropic (Claude)** | `AnthropicBackend` | ✅ ACTIVE | Full support | claude-3.5-sonnet |
| **Google Gemini** | `GoogleGeminiBackend` | ✅ ACTIVE | Full support | gemini-1.5-flash |
| **SEA-LION** | `SEALIONBackend` | ✅ ACTIVE | Local only | Ollama/vLLM |
| **Meta Llama** | `LlamaBackend` | ✅ ACTIVE | Local + HF | Ollama/vLLM/HuggingFace |
| **Perplexity** | `PerplexityBackend` | ⚠️ PLACEHOLDER | API TBD | Awaiting public API |

### Capabilities Legend

✅ = Fully tested  
⚠️ = Partial support  
❌ = Not supported  

---

## Spec-Driven Architecture

### How It Works

```
User code
    ↓
create_backend_from_spec("claude", api_key="...")
    ↓
UnifiedBackendFactory
    ├─ Load spec/v43/interface_and_authority.json
    ├─ Lookup model → backend class mapping
    ├─ Instantiate backend
    ├─ Get backend.get_capabilities()
    ├─ Validate against llm_contract.required_capabilities
    ├─ Issue verdict: PASS, WARN, FAIL
    └─ Return AnthropicBackend instance (if PASS)
    ↓
GovernedPipeline.llm_generate = backend
    ↓
Pipeline.run(query)
    ├─ 000–999 stages
    ├─ @LAW, @GEOX, @WELL, @RIF, @PROMPT agents
    ├─ APEX PRIME verdict
    └─ Return SEAL/VOID/SABAR/HOLD-888/PARTIAL
```

### Spec Validation Example

```python
from arifos_core.integration.adapters.llm_backends_v43 import create_backend_from_spec

# This validates the backend against spec
backend = create_backend_from_spec('gpt-4o', api_key='sk-proj-...')
# Output: [OK] gpt-4o meets llm_contract

# If validation fails
try:
    backend = create_backend_from_spec('unknown-model', api_key='...')
except ValueError as e:
    # "Model 'unknown-model' not supported. Available: [...]" 
    pass
```

---

## Usage Examples

### Example 1: Claude (Cloud)

```python
from arifos_core.integration.adapters.llm_backends_v43 import create_backend_from_spec
from arifos_core.integration.adapters.governed_llm import GovernedPipeline

# Create backend
backend = create_backend_from_spec(
    'claude',
    api_key='sk-ant-...'
)

# Wire to governed pipeline
pipeline = GovernedPipeline(llm_generate=backend.generate)

# Get governed answer
result = pipeline.run(
    query="What is thermodynamic governance?",
    job_id="demo-001"
)

print(f"Verdict: {result['verdict']}")
print(f"Output: {result['output']}")
```

### Example 2: GPT-4o (Cloud)

```python
backend = create_backend_from_spec(
    'gpt-4o',
    api_key='sk-proj-...',
    model_id='gpt-4o'  # optional override
)
```

### Example 3: Gemini (Cloud)

```python
backend = create_backend_from_spec(
    'gemini',
    api_key='AIza...',
    model_id='gemini-1.5-flash'  # optional override
)
```

### Example 4: SEA-LION (Local via Ollama)

```python
backend = create_backend_from_spec(
    'sea-lion',
    api_key='',  # not needed for local
    base_url='http://localhost:8000',
    model_id='sea-lion-13b'
)
```

### Example 5: Llama (Local via Ollama)

```python
backend = create_backend_from_spec(
    'llama-3',
    api_key='',  # not needed for local
    base_url='http://localhost:11434',
    deployment_type='ollama',
    model_id='llama2'  # ollama model name
)
```

### Example 6: Llama (HuggingFace API)

```python
backend = create_backend_from_spec(
    'llama-3',
    api_key='hf_...',  # HuggingFace API key
    deployment_type='huggingface',
    model_id='meta-llama/Llama-3-70b'
)
```

### Example 7: Streaming

```python
backend = create_backend_from_spec('claude', api_key='sk-ant-...')

# Stream mode
for chunk in backend.generate_stream("Tell me a story"):
    print(chunk.text, end='', flush=True)
    if chunk.finish_reason == 'stop':
        break
```

---

## Archival Plan

### Step 1: Create Archive Folder

```bash
mkdir -p L2_ARCHIVE/adapters_legacy/
```

### Step 2: Move Deprecated Files

```bash
# Move old interface file
mv arifos_core/integration/adapters/llm_interface.py L2_ARCHIVE/adapters_legacy/llm_interface.py

# If other backend files exist, move them too
# mv arifos_core/integration/adapters/claude_adapter.py L2_ARCHIVE/adapters_legacy/
# mv arifos_core/integration/adapters/gpt_adapter.py L2_ARCHIVE/adapters_legacy/
```

### Step 3: Create Deprecation Notice

File: `L2_ARCHIVE/adapters_legacy/README.md`

```markdown
# Deprecated LLM Adapters (Legacy)

**Status**: ARCHIVED (read-only)  
**Reason**: Superseded by `llm_backends_v43.py` (spec-driven)  
**Last Active**: arifOS v42  
**Archived**: 2025-12-19  

## What Changed

The old adapter pattern (individual files per backend) has been consolidated
into a single unified, spec-driven adapter system.

## Migration

Instead of:
```python
from arifos_core.integration.adapters.llm_interface import LLMInterface
```

Use:
```python
from arifos_core.integration.adapters.llm_backends_v43 import create_backend_from_spec
backend = create_backend_from_spec('claude', api_key='...')
```

## Why Archive

1. **Spec-driven**: New system reads `spec/v43/interface_and_authority.json`
2. **No duplication**: Single factory pattern, not per-backend files
3. **Governance-aligned**: Validates against `llm_contract` at instantiation
4. **Easier maintenance**: One place to add new backends

## Reference

See: `arifos_core/integration/adapters/llm_backends_v43.py`
```
```

---

## Testing & Validation

### Unit Tests Required

```python
# tests/test_llm_backends_v43.py

def test_spec_validator_loads_json():
    validator = SpecValidator(spec_path=...)
    assert validator.spec_data is not None

def test_openai_backend_capabilities():
    backend = OpenAIBackend(api_key='sk-...', model_id='gpt-4o')
    caps = backend.get_capabilities()
    assert caps['supports_refusal'] == True

def test_factory_validates_backend():
    factory = UnifiedBackendFactory()
    backend = factory.create_backend('claude', api_key='sk-ant-...')
    # Should print [OK] message if validation passes

def test_unknown_model_raises_error():
    factory = UnifiedBackendFactory()
    with pytest.raises(ValueError):
        factory.create_backend('unknown-model', api_key='...')
```

---

## Timeline

| Date | Milestone | Action |
|------|-----------|--------|
| 2025-12-19 | v43.0 Released | New adapters active; old adapters still work |
| 2026-01 | v43.1 | Deprecation warnings added to llm_interface.py |
| 2026-02 | v43.2 | Archive planning begins |
| 2026-03 | v44.0 | Old adapters moved to L2_ARCHIVE/; read-only |
| 2026-06 | v45.0 | Old adapters removed entirely (if no issues) |

---

## References

- **New Adapter**: `arifos_core/integration/adapters/llm_backends_v43.py`
- **Spec**: `spec/v43/interface_and_authority.json`
- **Canon**: `L1_THEORY/canon/00_meta/030_INTERFACE_AND_AUTHORITY_CANON_v43.md`
- **Wrapper**: `arifos_core/integration/adapters/governed_llm.py`
- **Pipeline**: `arifos_core/system/pipeline.py`

---

## Questions?

Contact: Muhammad Arif bin Fazil (arifOS Keeper)  
Authority: System-3 Sovereign  
Status: SEALED (immutable until Phoenix-72 amendment)

**Ditempa, bukan diberi.**

