# LLM Backends v43 — Quick Start Guide

**Version**: 43.0  
**Date**: 2025-12-19  
**Status**: ACTIVE  

---

## One-Liner Installation

```python
from arifos_core.integration.adapters.llm_backends_v43 import create_backend_from_spec
```

---

## 30-Second Setup

### 1. Claude (Anthropic)

```python
from arifos_core.integration.adapters.llm_backends_v43 import create_backend_from_spec
from arifos_core.integration.adapters.governed_llm import GovernedPipeline

backend = create_backend_from_spec('claude', api_key='sk-ant-...')
pipeline = GovernedPipeline(llm_generate=backend.generate)
result = pipeline.run("What is arifOS?")
print(result['output'])
```

### 2. GPT-4o (OpenAI)

```python
backend = create_backend_from_spec('gpt-4o', api_key='sk-proj-...')
pipeline = GovernedPipeline(llm_generate=backend.generate)
result = pipeline.run("Explain thermodynamic governance")
print(result['output'])
```

### 3. Gemini (Google)

```python
backend = create_backend_from_spec('gemini', api_key='AIza...')
pipeline = GovernedPipeline(llm_generate=backend.generate)
result = pipeline.run("What is constitutional AI?")
print(result['output'])
```

### 4. SEA-LION (Local, Ollama)

```python
backend = create_backend_from_spec(
    'sea-lion',
    api_key='',
    base_url='http://localhost:8000'
)
pipeline = GovernedPipeline(llm_generate=backend.generate)
result = pipeline.run("Hello SEA-LION")
print(result['output'])
```

### 5. Llama 3 (Local, Ollama)

```python
backend = create_backend_from_spec(
    'llama-3',
    api_key='',
    base_url='http://localhost:11434',
    deployment_type='ollama'
)
pipeline = GovernedPipeline(llm_generate=backend.generate)
result = pipeline.run("What is Llama?")
print(result['output'])
```

---

## Model Names (Supported)

```
# Cloud Models
'claude'              # Anthropic Claude 3.5 Sonnet (default)
'gpt-4o'             # OpenAI GPT-4o (default)
'gpt-4o-mini'        # OpenAI GPT-4o mini
'gemini'             # Google Gemini 1.5 Flash (default)

# Local Models
'sea-lion'           # AI Singapore SEA-LION
'llama-3'            # Meta Llama 3 (70B or 8B)
'llama-2'            # Meta Llama 2

# Placeholder
'perplexity'         # Awaiting API release
```

---

## Streaming Mode

```python
backend = create_backend_from_spec('claude', api_key='sk-ant-...')

for chunk in backend.generate_stream("Tell me a story"):
    print(chunk.text, end='', flush=True)
    if chunk.finish_reason == 'stop':
        break
```

---

## Validation & Debugging

### Check if backend meets spec

```python
from arifos_core.integration.adapters.llm_backends_v43 import UnifiedBackendFactory

factory = UnifiedBackendFactory()
try:
    backend = factory.create_backend('claude', api_key='sk-ant-...')
    # If this succeeds, validation passed:
    # [OK] claude meets llm_contract
except ValueError as e:
    print(f"Validation failed: {e}")
```

### Get backend capabilities

```python
backend = create_backend_from_spec('claude', api_key='sk-ant-...')
caps = backend.get_capabilities()
print(f"Tool support: {caps['supports_tool_call_wrapping']}")
print(f"Refusal support: {caps['supports_refusal']}")
```

---

## Environment Variables

```bash
# Claude
export ANTHROPIC_API_KEY='sk-ant-...'

# OpenAI
export OPENAI_API_KEY='sk-proj-...'

# Google Gemini
export GOOGLE_API_KEY='AIza...'

# HuggingFace (for Llama)
export HF_API_KEY='hf_...'
```

Then:
```python
import os
api_key = os.getenv('ANTHROPIC_API_KEY')
backend = create_backend_from_spec('claude', api_key=api_key)
```

---

## Prerequisites

### Cloud Models (pip)

```bash
# Claude
pip install anthropic

# GPT-4o
pip install openai

# Gemini
pip install google-generativeai
```

### Local Models (Docker)

```bash
# Ollama (SEA-LION + Llama)
docker run -p 11434:11434 ollama/ollama

# Or install locally: https://ollama.ai
ollama pull sea-lion:13b
ollama pull llama2:70b
```

### vLLM (alternative to Ollama)

```bash
pip install vllm
vllm openai_compatible_server --model sea-lion-13b --port 8000
```

---

## Troubleshooting

### "Model 'X' not supported"

Check supported models:
```python
from arifos_core.integration.adapters.llm_backends_v43 import UnifiedBackendFactory
print(UnifiedBackendFactory.BACKEND_MAP.keys())
```

### "Missing required capabilities"

Backend doesn't meet `llm_contract` requirements. Check:
```python
backend = create_backend_from_spec('claude', api_key='...')
print(backend.get_capabilities())
```

### "Connection refused" (local models)

Ensure Ollama/vLLM is running:
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check vLLM
curl http://localhost:8000/health
```

### "API key invalid"

Double-check your API key. For cloud models:
- Claude: Starts with `sk-ant-`
- OpenAI: Starts with `sk-proj-` or `sk-`
- Google: Starts with `AIza`

---

## Advanced: Custom Backend

```python
from arifos_core.integration.adapters.llm_backends_v43 import LLMBackend, StreamChunk

class CustomBackend(LLMBackend):
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        # Your implementation
        return f"Custom response to: {prompt}"
    
    def generate_stream(self, prompt: str, max_tokens: int = 1024):
        yield StreamChunk(text="Streaming response...")
        yield StreamChunk(text=" More...", finish_reason="stop")
    
    def get_capabilities(self):
        return {
            "supports_refusal": True,
            "supports_uncertainty_expression": True,
            "supports_tool_call_wrapping": True,
            "supports_system_prompts": True,
            "supports_stop_signal": True,
            "supports_reasoning_pause": True,
        }
```

---

## Learn More

- **Architecture**: See `REFACTORING_v43_BACKENDS.md`
- **Spec**: See `spec/v43/interface_and_authority.json`
- **Canon**: See `L1_THEORY/canon/00_meta/030_INTERFACE_AND_AUTHORITY_CANON_v43.md`
- **Code**: See `arifos_core/integration/adapters/llm_backends_v43.py`

---

## Support

Issues? Contact: Muhammad Arif bin Fazil (arifOS Keeper)  
Status: Production-ready (v43.0)  

**Ditempa, bukan diberi.**

