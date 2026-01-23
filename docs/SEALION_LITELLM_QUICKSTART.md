# SEA-LION LiteLLM Integration - Quick Start Guide

This guide walks you through configuring arifOS to use SEA-LION as the default LLM provider via LiteLLM.

## Prerequisites

- Python 3.8+
- arifOS v38.2+
- SEA-LION API key (get at https://playground.sea-lion.ai)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Install arifOS with LiteLLM support
pip install -e ".[litellm,api]"

# Or install dependencies separately
pip install litellm fastapi uvicorn python-multipart
```

### 2. Configure Environment

```bash
# Copy the template
cp .env.example .env

# Edit .env and set your API key
# Required variables:
#   ARIF_LLM_API_KEY=your-sealion-api-key-here
```

**Minimal .env configuration:**
```bash
ARIF_LLM_PROVIDER=openai
ARIF_LLM_API_BASE=https://api.sea-lion.ai/v1
ARIF_LLM_API_KEY=your-key-here
ARIF_LLM_MODEL=aisingapore/Llama-SEA-LION-v3-70B-IT
```

### 3. Test the Connection

```bash
# Run the test script
python scripts/test_sealion_litellm.py
```

Expected output:
```
==================================================
arifOS v38.2 - SEA-LION LiteLLM Test Suite
==================================================

Supported Providers:
  • openai: OpenAI GPT models (also SEA-LION compatible)
  • anthropic: Anthropic Claude models
  • gemini: Google Gemini models
  • sealion: SEA-LION models via OpenAI-compatible API

[CONFIG] Provider: openai
[CONFIG] API Base: https://api.sea-lion.ai/v1
[CONFIG] Model: aisingapore/Llama-SEA-LION-v3-70B-IT

[✓] LiteLLM gateway initialized successfully

...tests run...

[SUCCESS] All tests passed!
```

### 4. Start the API Server

**Windows (PowerShell):**
```powershell
.\scripts\start_sealion_server.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/start_sealion_server.sh
./scripts/start_sealion_server.sh
```

**Manual start:**
```bash
uvicorn arifos_core.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test the API

```bash
# Send a test query
curl -X POST http://localhost:8000/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI governance?"}'
```

Expected response:
```json
{
  "verdict": "SEAL",
  "response": "AI governance is...",
  "floor_scores": {
    "F1_Amanah": 1.0,
    "F2_Truth": 0.99,
    ...
  },
  "memory_band": "LEDGER",
  "timestamp": "2025-12-14T..."
}
```

## Architecture

```
User Query → LiteLLM Gateway → SEA-LION API
                ↓
          Pipeline (000→999)
                ↓
       9 Constitutional Floors
                ↓
      Memory Write Policy (v38)
                ↓
          Governed Response
```

## Switching Providers

To switch from SEA-LION to another provider, just change `.env`:

**OpenAI GPT-4:**
```bash
ARIF_LLM_PROVIDER=openai
ARIF_LLM_API_BASE=https://api.openai.com/v1
ARIF_LLM_API_KEY=sk-...
ARIF_LLM_MODEL=gpt-4o
```

**Anthropic Claude:**
```bash
ARIF_LLM_PROVIDER=anthropic
# No API base needed
ARIF_LLM_API_KEY=sk-ant-...
ARIF_LLM_MODEL=claude-3-sonnet-20240229
```

**Google Gemini:**
```bash
ARIF_LLM_PROVIDER=gemini
# No API base needed
ARIF_LLM_API_KEY=...
ARIF_LLM_MODEL=gemini-1.5-flash
```

No code changes required - just restart the server.

## Programmatic Usage

```python
from arifos_core.connectors.litellm_gateway import make_llm_generate

# Uses environment variables (.env)
generate = make_llm_generate()
response = generate("Explain constitutional AI")

# Or explicit configuration
from arifos_core.connectors.litellm_gateway import LiteLLMConfig

config = LiteLLMConfig(
    provider="openai",
    api_base="https://api.sea-lion.ai/v1",
    api_key="your-key",
    model="aisingapore/Llama-SEA-LION-v3-70B-IT",
)
generate = make_llm_generate(config)
```

## Troubleshooting

### Error: "API key required"
```
ValueError: API key required. Set ARIF_LLM_API_KEY environment variable
```
**Fix:** Set `ARIF_LLM_API_KEY` in `.env` file.

### Error: "litellm required"
```
ImportError: litellm required. Install with: pip install litellm
```
**Fix:** `pip install litellm` or `pip install -e ".[litellm]"`

### Error: "Connection refused"
Check:
1. API base URL is correct (`https://api.sea-lion.ai/v1`)
2. API key is valid
3. Network connectivity

### Verbose logging
```bash
# Enable LiteLLM debug logging
export LITELLM_LOG=DEBUG
python scripts/test_sealion_litellm.py
```

## Next Steps

- **Governed Pipeline:** All responses go through 9 constitutional floors
- **Memory Routing:** Verdicts route to appropriate memory bands (LEDGER/PHOENIX/VOID)
- **Audit Trail:** All decisions logged to `cooling_ledger/L1_cooling_ledger.jsonl`
- **W@W Organs:** @PROMPT, @WELL, @WEALTH governance active

See [AGENTS.md](../AGENTS.md) for full governance documentation.

## Related Files

- [`arifos_core/connectors/litellm_gateway.py`](../arifos_core/connectors/litellm_gateway.py) - LiteLLM adapter
- [`.env.example`](../.env.example) - Configuration template
- [`scripts/test_sealion_litellm.py`](test_sealion_litellm.py) - Test harness
- [`scripts/start_sealion_server.ps1`](start_sealion_server.ps1) - Startup script

---

**Status:** PRODUCTION  
**Version:** v38.2  
**Last Updated:** 2025-12-14
