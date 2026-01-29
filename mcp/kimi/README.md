# 🌙 Kimi (月之暗面) MCP Integration

**Moonshot AI (Kimi) specific implementation for arifOS Constitutional AI**

---

## Overview

This directory contains Kimi-specific adaptations for the arifOS MCP server, including:
- Bilingual (Chinese/English) system prompts
- Kimi-optimized adapter with streaming support
- Configuration for Kimi's 200k token context window
- Integration guide for Chinese users

---

## Files

| File | Purpose |
|------|---------|
| `kimi_config.yaml` | Kimi-specific MCP configuration |
| `kimi_adapter.py` | Python adapter for Kimi integration |
| `KIMI_PROMPT_ZH.txt` | Chinese constitutional system prompt |
| `KIMI_INTEGRATION_GUIDE.md` | Complete integration guide |
| `README.md` | This file |

---

## Quick Start

### 1. Configure Kimi

```yaml
# kimi_config.yaml
mcp_servers:
  arifos:
    command: python
    args: ["../server.py"]
    env:
      ARIFOS_MODE: "kimi"
```

### 2. Use Chinese Prompt

```python
# Load Chinese constitutional prompt
with open("KIMI_PROMPT_ZH.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Use with Kimi
response = kimi.chat.completions.create(
    model="kimi-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "什么是宪法人工智能？"}
    ]
)
```

### 3. Run Adapter

```bash
python kimi_adapter.py
```

---

## Kimi-Specific Features

### Bilingual Support

| Language | Prompt File | Use Case |
|----------|-------------|----------|
| Chinese | `KIMI_PROMPT_ZH.txt` | Chinese users, native context |
| English | `../system_prompts/AI_CONSTITUTIONAL_PROMPT.txt` | International users |

### Long Context Optimization

Kimi's 200k token window allows:
- Full conversation history
- Complete constitutional metadata
- 9-paradox equilibrium calculations
- Audit trail in context

### Streaming Verdicts

```python
async for chunk in adapter.process_message(query):
    # Shows in real-time:
    # - [constitutional_checking]
    # - Individual paradox scores
    # - Final verdict
    # - Response
    print(chunk, end="")
```

---

## Architecture

```
User (Chinese/English)
    │
    ▼
Kimi (Moonshot AI)
    │
    ├── System Prompt (KIMI_PROMPT_ZH.txt)
    │
    ▼
KimiAdapter
    │
    ├── _init_ → Session
    ├── _trinity_ → Full evaluation
    └── _vault_ → Seal
    │
    ▼
arifOS Engine
    │
    ├── AGI (Mind)
    ├── ASI (Heart)
    └── APEX (Soul)
    │
    ▼
Constitutional Verdict
    │
    ▼
Kimi Response (with metadata)
```

---

## Tool Permissions

| Tool | Kimi Behavior |
|------|---------------|
| `_init_` | Auto-invoke at session start |
| `_trinity_` | Main evaluation tool |
| `_asi_` | Ask before safety check |
| `_apex_` | Ask before judgment |
| `_vault_` | Auto-seal approved decisions |
| `_reality_` | Optional fact-checking |

---

## Example Output

```
用户: 什么是人工智能伦理？

Kimi:
[ constitutional_checking ]
[ verdict: SEAL | score: 0.92 ]

**宪法评估** | Constitutional Assessment
---
裁决: SEAL | Verdict: SEAL
三位一体得分: 0.92 | Trinity Score: 0.92

**悖论分析** | Paradox Analysis:
✓ 真理·关怀 (Truth·Care): 0.95
✓ 清晰·和平 (Clarity·Peace): 0.93
✓ 谦逊·正义 (Humility·Justice): 0.90
✓ 精度·可逆 (Precision·Reversibility): 0.91
✓ 层次·同意 (Hierarchy·Consent): 0.89
~ 代理·保护 (Agency·Protection): 0.84
✓ 紧急·可持续 (Urgency·Sustainability): 0.93
✓ 确定·怀疑 (Certainty·Doubt): 0.88
✓ 统一·多样 (Unity·Diversity): 0.91

---

人工智能伦理是...

---
*此回复已通过 arifOS 宪法框架验证*
*This response validated by arifOS constitutional framework*
```

---

## Configuration

### Environment Variables

```bash
export KIMI_API_KEY="your-moonshot-api-key"
export ARIFOS_MODE="kimi"
export ARIFOS_LANGUAGE="zh"  # or "en"
export ARIFOS_VERBOSITY="detailed"
```

### Model Settings

```yaml
model_settings:
  model: kimi-latest
  temperature: 0.7
  max_tokens: 4096
  top_p: 0.95
```

---

## Integration with Kimi Platform

### Option 1: Direct API

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_KIMI_API_KEY",
    base_url="https://api.moonshot.cn/v1"
)

# Load arifOS prompt
with open("KIMI_PROMPT_ZH.txt") as f:
    system_prompt = f.read()

response = client.chat.completions.create(
    model="kimi-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "你的问题"}
    ],
    tools=[...],  # MCP tools
    tool_choice="auto"
)
```

### Option 2: Kimi CLI (if available)

```bash
kimi chat --system-prompt KIMI_PROMPT_ZH.txt --mcp-server ../server.py
```

---

## Testing

```bash
# Test Chinese prompt
cd arifOS/mcp/kimi
python -c "
with open('KIMI_PROMPT_ZH.txt', 'r', encoding='utf-8') as f:
    content = f.read()
print('Prompt loaded successfully')
print(f'Length: {len(content)} characters')
"

# Test adapter
python kimi_adapter.py
```

---

## Troubleshooting

### Issue: Chinese characters garbled

**Fix:**
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### Issue: Kimi not using tools

**Fix:** Ensure system prompt includes explicit tool instructions (see line 85-95 of KIMI_PROMPT_ZH.txt)

### Issue: Slow constitutional checks

**Fix:** Enable streaming to show progress

---

## Resources

- **Kimi Platform:** https://platform.moonshot.cn
- **arifOS Docs:** `arifOS/codebase/`
- **MCP Spec:** https://modelcontextprotocol.io
- **English Prompt:** `../system_prompts/AI_CONSTITUTIONAL_PROMPT.txt`

---

## Version

- **Kimi Adapter:** v54.0
- **Constitutional Version:** v54.0
- **Protocol:** MCP 2025-06-18

---

**DITEMPA BUKAN DIBERI**  
*为Kimi锻造，为中文用户优化。*  
*Forged for Kimi, optimized for Chinese users.*
