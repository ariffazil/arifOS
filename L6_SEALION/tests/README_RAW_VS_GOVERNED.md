# RAW vs GOVERNED Demo - Usage Guide

**Location:** `L6_SEALION/tests/demo_sealion_raw_vs_governed.py`

## What This Demo Does

Compares two execution modes side-by-side:

1. **RAW Mode (A):** Direct LLM call with NO arifOS governance
2. **GOVERNED Mode (B):** Full arifOS v45Ω constitutional enforcement

You'll see:
- RAW: Unfiltered model response (fast, no safety checks)
- GOVERNED: Constitutional verdict (SEAL/PARTIAL/VOID/HOLD), metrics, lane classification

## Prerequisites

1. **Python 3.10+** installed
2. **Virtual environment activated** (`.venv`)
3. **API key** set in Windows environment variables

### Setting API Key (Windows PowerShell)

**Option 1: Session-scoped (current PowerShell session only)**
```powershell
$env:ARIF_LLM_API_KEY = "your-api-key-here"
```

**Option 2: User-scoped (persistent across sessions)**
```powershell
[System.Environment]::SetEnvironmentVariable('ARIF_LLM_API_KEY', 'your-api-key-here', 'User')
```

**Option 3: .env file (recommended for development)**
Create `.env` in project root:
```
ARIF_LLM_API_KEY=your-api-key-here
```

**Verify API key is set:**
```powershell
echo $env:ARIF_LLM_API_KEY
```

## Running the Demo

### Basic Usage (Default Prompt)

```powershell
# From repo root
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run demo
python L6_SEALION/tests/demo_sealion_raw_vs_governed.py
```

### Custom Prompt

```powershell
python L6_SEALION/tests/demo_sealion_raw_vs_governed.py --prompt "Explain quantum mechanics in simple terms"
```

### Custom Model Parameters

```powershell
python L6_SEALION/tests/demo_sealion_raw_vs_governed.py `
    --prompt "What is AI governance?" `
    --model "Qwen-SEA-LION-v4-32B-IT" `
    --max_tokens 512 `
    --temperature 0.2
```

### All CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--prompt` | "Explain in 5 bullets how arifOS governs an LLM." | Prompt to send |
| `--model` | "Qwen-SEA-LION-v4-32B-IT" | Model name |
| `--max_tokens` | 512 | Max tokens to generate |
| `--temperature` | 0.2 | Generation temperature (0.0-1.0) |

## Output

The demo will:

1. **Show banner** with model info and arifOS version
2. **Run RAW mode:**
   - Direct LLM call
   - Show response
   - Show timing
3. **Run GOVERNED mode:**
   - Δ Router lane classification (PHATIC/SOFT/HARD/REFUSE)
   - Ω Aggregator metrics (Truth, ΔS, Peace², κᵣ, Ω₀, Ψ)
   - 888 JUDGE verdict (SEAL/PARTIAL/VOID/SABAR/HOLD)
   - Show response (if approved) or refusal message
   - Show timing
4. **Save JSONL log** to `L6_SEALION/tests/_runs/raw_vs_governed_<timestamp>.jsonl`
5. **Show comparison summary**

## Example Output

```
🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁
  🚀 RAW vs GOVERNED - arifOS v45Ω Comparison Demo 🚀
🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁🦁

╔═══════════════════════════════════════════════════════════════════╗
║  MODEL: Qwen-SEA-LION-v4-32B-IT                                   ║
║  VERSION: v42_OMEGA_PLUS                                          ║
║  MODE A: RAW (ungoverned)                                         ║
║  MODE B: GOVERNED (full arifOS v45Ω enforcement)                  ║
╚═══════════════════════════════════════════════════════════════════╝

📝 PROMPT:
Explain in 5 bullets how arifOS governs an LLM.

══════════════════════════════════════════════════════════════════════
🔴 MODE A: RAW (Ungoverned)
══════════════════════════════════════════════════════════════════════
Calling Qwen-SEA-LION-v4-32B-IT directly (no governance)...

✅ Response received in 2.35s
📊 Estimated tokens: 128

📤 RAW OUTPUT:

──────────────────────────────────────────────────────────────────────
[RAW model response here - no governance, no safety checks]
──────────────────────────────────────────────────────────────────────

══════════════════════════════════════════════════════════════════════
🟢 MODE B: GOVERNED (arifOS v45Ω)
══════════════════════════════════════════════════════════════════════
🔀 Δ Router Lane: SOFT
   Type: Educational/explanatory (truth ≥ 0.80)

⏳ Calling Qwen-SEA-LION-v4-32B-IT (governed)...
✅ Response received (450 chars)

⚙️  Ω Aggregator - Metrics:
   Truth (ξ):      0.870
   ΔS (Clarity):   +0.150
   Peace²:         1.020
   κᵣ (Empathy):   0.960
   Ω₀ (Humility):  0.040
   Ψ (Vitality):   1.120

⚖️  888 JUDGE - Rendering constitutional verdict...

✅ SEAL
Meaning: Full approval - output released
Reason: All floors passed. Educational lane, truth 0.87 > 0.80 threshold.

📤 GOVERNED OUTPUT:

──────────────────────────────────────────────────────────────────────
[Governed response here - passed all constitutional floors]
──────────────────────────────────────────────────────────────────────

⏱️ Total governance time: 3.12s

💾 Log saved: L6_SEALION/tests/_runs/raw_vs_governed_20251227_143022.jsonl

══════════════════════════════════════════════════════════════════════
📊 COMPARISON SUMMARY
══════════════════════════════════════════════════════════════════════
RAW:      ✅ Success
GOVERNED: ✅ Success

Governance Verdict: SEAL
Lane: SOFT
Truth Score: 0.87
══════════════════════════════════════════════════════════════════════
```

## Running Tests

### Smoke Tests (No API Key Required)

```powershell
# Run all smoke tests
pytest L6_SEALION/tests/test_raw_vs_governed_smoke.py -v

# Run specific test
pytest L6_SEALION/tests/test_raw_vs_governed_smoke.py::TestCLIParsing::test_default_arguments -v
```

### Tests That ARE Included (No External Calls)

✅ CLI argument parsing
✅ Log directory creation
✅ API key validation and priority
✅ Configuration validation
✅ Log file format verification

### Tests That ARE SKIPPED (Require API Key)

⏭️ Actual RAW mode LLM calls
⏭️ Actual GOVERNED mode LLM calls

(These are marked with `@pytest.mark.skip`)

## Troubleshooting

### Error: "API Key not found!"

**Solution:** Set environment variable (see "Setting API Key" above)

### Error: "LiteLLM completion failed"

**Possible causes:**
1. Invalid API key
2. Network issue
3. Model name incorrect
4. API endpoint unreachable

**Solution:** Check API key, network connection, model name

### Error: ImportError for litellm

**Solution:**
```powershell
pip install litellm
# Or install with all dependencies:
pip install -e ".[litellm]"
```

### Log files not appearing

**Solution:** Check that `L6_SEALION/tests/_runs/` directory exists and is writable

## Expected Differences (RAW vs GOVERNED)

| Aspect | RAW Mode | GOVERNED Mode |
|--------|----------|---------------|
| **Speed** | Faster (direct call) | Slower (metrics + verdict) |
| **Safety** | ❌ None (raw output) | ✅ 9 constitutional floors |
| **Refusal** | ❌ Cannot refuse | ✅ VOID/HOLD verdicts |
| **Truth** | ❌ No verification | ✅ Lane-aware thresholds |
| **Auditability** | ❌ No trace | ✅ Full floor trace + ledger |
| **Memory** | ❌ Not governed | ✅ Verdict-gated (EUREKA) |

## What Each Verdict Means

| Verdict | Meaning | Output Behavior |
|---------|---------|-----------------|
| **SEAL** | ✅ All floors passed | Full response released |
| **PARTIAL** | ⚠️ Soft floors failed | Response with caveats |
| **VOID** | 🚫 Hard floor failed | Response blocked |
| **SABAR** | ⏸️ Constitutional pause | Must cool, re-evaluate |
| **HOLD_888** | 🔒 Human escalation | Requires human review |

## Lane Classification (Δ Router)

| Lane | Use Case | Truth Threshold |
|------|----------|-----------------|
| **PHATIC** | Greetings ("hi") | Exempt (bypassed) |
| **SOFT** | Explanations | ≥ 0.80 (buffer: 0.80-0.89 → PARTIAL) |
| **HARD** | Factual assertions | ≥ 0.90 (strict, no tolerance) |
| **REFUSE** | Constitutional violations | Auto-block |

## Related Files

- **Demo script:** `L6_SEALION/tests/demo_sealion_raw_vs_governed.py`
- **Smoke tests:** `L6_SEALION/tests/test_raw_vs_governed_smoke.py`
- **Full v45 demo:** `L6_SEALION/tests/demo_sealion_v45_full.py`
- **LiteLLM gateway:** `arifos_core/connectors/litellm_gateway.py`
- **APEX PRIME (judge):** `arifos_core/system/apex_prime.py`
- **Δ Router:** `arifos_core/routing/prompt_router.py`

## DITEMPA BUKAN DIBERI

Forged, not given. Truth must cool before it rules.

---

*Version: v45Ω Patch B | Last Updated: 2025-12-27*
