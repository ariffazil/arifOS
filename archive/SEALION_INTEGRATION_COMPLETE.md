# SEA-LION Integration Complete ✅

## Summary

Successfully configured arifOS v38.2 to use SEA-LION as the default LLM provider via LiteLLM. The integration is **environment-driven** - no code changes needed to switch providers.

---

## What Was Created

### 1. **LiteLLM Gateway Module** 
   - **File:** [`arifos_core/connectors/litellm_gateway.py`](arifos_core/connectors/litellm_gateway.py)
   - Generic adapter that reads from environment variables
   - Supports SEA-LION, OpenAI, Anthropic, Gemini, and any OpenAI-compatible endpoint
   - Clean API: `make_llm_generate()` returns a governed generate function

### 2. **Environment Configuration**
   - **File:** [`.env.example`](.env.example)
   - Template with SEA-LION as default provider
   - Includes all necessary configuration variables
   - **Required:** `ARIF_LLM_API_KEY` (get at https://playground.sea-lion.ai)

### 3. **Updated Dependencies**
   - **File:** [`pyproject.toml`](pyproject.toml)
   - Added `litellm>=1.0.0` to optional dependencies
   - Added `python-multipart>=0.0.6` for FastAPI
   - New install target: `pip install -e ".[litellm,api]"`

### 4. **Updated API Routes**
   - **File:** [`arifos_core/api/routes/pipeline.py`](arifos_core/api/routes/pipeline.py)
   - Auto-detects LiteLLM configuration from environment
   - Falls back to stub mode if API key not set
   - Status endpoint shows active LLM backend

### 5. **Test Script**
   - **File:** [`scripts/test_sealion_litellm.py`](scripts/test_sealion_litellm.py)
   - Validates connection to SEA-LION API
   - Tests English, Malay, and technical queries
   - Provides clear error messages for troubleshooting

### 6. **Startup Script (Windows)**
   - **File:** [`scripts/start_sealion_server.ps1`](scripts/start_sealion_server.ps1)
   - PowerShell script for Windows users
   - Loads `.env` file automatically
   - Validates configuration before starting

### 7. **Quick Start Guide**
   - **File:** [`docs/SEALION_LITELLM_QUICKSTART.md`](docs/SEALION_LITELLM_QUICKSTART.md)
   - Complete step-by-step instructions
   - Troubleshooting guide
   - Architecture diagram
   - Provider switching examples

---

## How to Use (Step-by-Step)

### Step 1: Install Dependencies

```powershell
# Activate your virtual environment
.\.venv\Scripts\Activate.ps1

# Install with LiteLLM support
pip install -e ".[litellm,api]"
```

### Step 2: Configure Environment

```powershell
# Copy the template
Copy-Item .env.example .env

# Edit .env and add your SEA-LION API key
# Get your key at: https://playground.sea-lion.ai
```

**Minimal required configuration in `.env`:**
```bash
ARIF_LLM_PROVIDER=openai
ARIF_LLM_API_BASE=https://api.sea-lion.ai/v1
ARIF_LLM_API_KEY=your-actual-key-here
ARIF_LLM_MODEL=aisingapore/Llama-SEA-LION-v3-70B-IT
```

### Step 3: Test the Connection

```powershell
# Run the test script
python scripts/test_sealion_litellm.py
```

**Expected output:**
```
==================================================
arifOS v38.2 - SEA-LION LiteLLM Test Suite
==================================================

[CONFIG] Provider: openai
[CONFIG] API Base: https://api.sea-lion.ai/v1
[CONFIG] Model: aisingapore/Llama-SEA-LION-v3-70B-IT

[✓] LiteLLM gateway initialized successfully

...tests run...

[SUCCESS] All tests passed! SEA-LION integration working correctly.
```

### Step 4: Start the API Server

**Option A: Using PowerShell script**
```powershell
.\scripts\start_sealion_server.ps1
```

**Option B: Manual start**
```powershell
uvicorn arifos_core.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Test the API

```powershell
# In another terminal
curl -X POST http://localhost:8000/pipeline/run `
  -H "Content-Type: application/json" `
  -d '{"query": "What is AI governance?"}'
```

**Expected response:**
```json
{
  "verdict": "SEAL",
  "response": "AI governance is a framework...",
  "job_id": "api-abc123",
  "floor_scores": {
    "F1_Amanah": 1.0,
    "F2_Truth": 0.99,
    "F4_DeltaS": 0.85,
    ...
  },
  "memory_band": "LEDGER"
}
```

### Step 6: Check Status

```powershell
curl http://localhost:8000/pipeline/status
```

**Response shows active configuration:**
```json
{
  "status": "available",
  "epoch": "v38",
  "llm_backend": "litellm",
  "llm_config": {
    "provider": "openai",
    "api_base": "https://api.sea-lion.ai/v1",
    "model": "aisingapore/Llama-SEA-LION-v3-70B-IT"
  }
}
```

---

## Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ FastAPI Endpoint        │
│ /pipeline/run           │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ LiteLLM Gateway         │
│ (Environment-driven)    │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ SEA-LION API            │
│ https://api.sea-lion.ai │
└──────┬──────────────────┘
       │
       ▼ (response)
┌─────────────────────────┐
│ arifOS Pipeline         │
│ 000 → 111 → ... → 999   │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ 9 Constitutional Floors │
│ F1-F9 Enforcement       │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Memory Write Policy     │
│ SEAL → LEDGER           │
│ VOID → VOID (no canon)  │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Governed Response       │
│ + Verdict + Telemetry   │
└─────────────────────────┘
```

---

## Switching Providers

The integration is **provider-agnostic**. Switch by changing `.env` only:

### Switch to OpenAI GPT-4o
```bash
ARIF_LLM_PROVIDER=openai
ARIF_LLM_API_BASE=https://api.openai.com/v1
ARIF_LLM_API_KEY=sk-...
ARIF_LLM_MODEL=gpt-4o
```

### Switch to Anthropic Claude
```bash
ARIF_LLM_PROVIDER=anthropic
# No API base needed for Claude
ARIF_LLM_API_KEY=sk-ant-...
ARIF_LLM_MODEL=claude-3-sonnet-20240229
```

### Switch to Google Gemini
```bash
ARIF_LLM_PROVIDER=gemini
# No API base needed for Gemini
ARIF_LLM_API_KEY=...
ARIF_LLM_MODEL=gemini-1.5-flash
```

**No code changes required - just restart the server.**

---

## Programmatic Usage

```python
from arifos_core.connectors.litellm_gateway import make_llm_generate

# Option 1: Use environment variables (.env file)
generate = make_llm_generate()
response = generate("Explain AI governance")
print(response)

# Option 2: Explicit configuration (override .env)
from arifos_core.connectors.litellm_gateway import LiteLLMConfig

config = LiteLLMConfig(
    provider="openai",
    api_base="https://api.sea-lion.ai/v1",
    api_key="your-key",
    model="aisingapore/Llama-SEA-LION-v3-70B-IT",
    temperature=0.7,
    max_tokens=2048,
)
generate = make_llm_generate(config)
response = generate("What is constitutional AI?")
```

---

## Governance Integration

All SEA-LION responses go through the **v38.2 governance stack**:

1. **9 Constitutional Floors** (F1-F9)
   - F1 Amanah (reversibility)
   - F2 Truth (factual accuracy)
   - F4 DeltaS (clarity)
   - F5 Peace² (non-destructive)
   - F6 Kr (empathy)
   - F7 Omega0 (humility)
   - F8 G (genius index)
   - F9 C_dark (anti-manipulation)

2. **Memory Write Policy Engine (EUREKA)**
   - SEAL → LEDGER + ACTIVE (canonical memory)
   - PARTIAL → PHOENIX (pending review)
   - VOID → VOID (diagnostic only, never canonical)
   - SABAR → LEDGER (with failure reason)

3. **Cooling Ledger**
   - All verdicts logged to `cooling_ledger/L1_cooling_ledger.jsonl`
   - Append-only, hash-chained audit trail
   - Phoenix-72 amendment proposals tracked

4. **W@W Federation Organs**
   - @PROMPT: Language & prompt governance
   - @WELL: Safety & harm prevention
   - @WEALTH: Ethics & integrity (ABSOLUTE VETO)
   - @GEOX: Reality grounding
   - @RIF: Logic & clarity

---

## Files Reference

| File | Purpose |
|------|---------|
| [`arifos_core/connectors/litellm_gateway.py`](arifos_core/connectors/litellm_gateway.py) | LiteLLM adapter (main integration) |
| [`.env.example`](.env.example) | Environment configuration template |
| [`pyproject.toml`](pyproject.toml) | Updated dependencies |
| [`arifos_core/api/routes/pipeline.py`](arifos_core/api/routes/pipeline.py) | API route with auto-detection |
| [`scripts/test_sealion_litellm.py`](scripts/test_sealion_litellm.py) | Connection test script |
| [`scripts/start_sealion_server.ps1`](scripts/start_sealion_server.ps1) | Windows startup script |
| [`docs/SEALION_LITELLM_QUICKSTART.md`](docs/SEALION_LITELLM_QUICKSTART.md) | Complete guide |

---

## Troubleshooting

### ❌ "API key required"
```
ValueError: API key required. Set ARIF_LLM_API_KEY environment variable
```
**Fix:** Add your SEA-LION API key to `.env` file.

### ❌ "litellm required"
```
ImportError: litellm required. Install with: pip install litellm
```
**Fix:** `pip install litellm` or `pip install -e ".[litellm]"`

### ❌ Connection errors
Check:
1. `.env` file exists and is loaded
2. `ARIF_LLM_API_BASE=https://api.sea-lion.ai/v1` is correct
3. API key is valid (test at https://playground.sea-lion.ai)
4. Network connectivity

### ❌ Stub mode instead of SEA-LION
If status shows `"llm_backend": "stub"`, check:
1. `.env` file is in project root
2. `ARIF_LLM_API_KEY` is set (not blank)
3. `litellm` package is installed
4. Server was restarted after `.env` changes

---

## Next Steps

✅ **Integration Complete**  
✅ **Governed by v38.2 Constitutional Stack**  
✅ **Memory Write Policy Enforced**  
✅ **Audit Trail Active**

Ready to:
- Scale to production with Docker deployment
- Add MCP tools for IDE integration (v40)
- Enable L7 memory with Mem0 + Qdrant
- Deploy behind reverse proxy (Nginx/Traefik)

---

**Status:** PRODUCTION READY  
**Version:** v38.2  
**Date:** 2025-12-14  
**Sealed:** APEX PRIME

**DITEMPA BUKAN DIBERI** - Forged, not given.
