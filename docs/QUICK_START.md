# arifOS MCP — 5-Minute Quick Start

> **What is this?** Constitutional AI governance middleware. Your AI makes requests → arifOS checks safety, truth, and ethics (13 floors) → executes or blocks.

---

## ⚡ Step 1: Connect

### Option A: Claude Desktop / OpenClaw / Any MCP Client

Add to your MCP client config:

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifosmcp.arif-fazil.com/mcp"
    }
  }
}
```

### Option B: Direct HTTP (any language)

```bash
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-03-26",
      " capabilities": {}
    }
  }'
```

---

## ⚡ Step 2: Ask Something

```bash
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "agi_reason",
      "arguments": {
        "query": "What is constitutional AI?"
      }
    }
  }'
```

---

## ⚡ Step 3: Read the Verdict

Every response has a `verdict`:

| Verdict | Meaning | Action |
|---------|---------|--------|
| `SEAL` | ✅ Approved | Safe to proceed |
| `VOID` | ❌ Rejected | Blocked — violated a constitutional floor |
| `888_HOLD` | ⏸️ Paused | Needs human approval |
| `SABAR` | ⏳ Wait | System processing, try again |

### Example Response (truncated):

```json
{
  "structuredContent": {
    "verdict": "SEAL",
    "tool": "agi_reason",
    "payload": {
      "confidence": 0.47,
      "entropy": {"delta_s": -0.47}
    },
    "floors": ["F2", "F4", "F7", "F8"]
  }
}
```

The `floors` array shows which constitutional rules were checked.

---

## 🔧 Tools by What You Want to Do

### I want to... | Use this tool

| Need | Tool | Example |
|------|------|---------|
| Start a governed session | `init_anchor` | Establish identity before doing anything |
| Search the web (grounded) | `physics_reality` | Get facts, not hallucinations |
| Execute code safely | `code_engine` | Write + run code in a sandbox |
| Check if something is safe | `apex_soul` | "Should I do X?" — final verdict |
| Remember across sessions | `engineering_memory` | Store findings for later |
| Log a decision permanently | `vault_ledger` | Record to immutable audit trail |
| Verify past records | `verify_vault_ledger` | Check if a record was tampered |
| Do deep reasoning | `agi_mind` | Multi-step reasoning with entropy tracking |
| Check system health | `agi_reflect` | Is the system healthy? |

### All Available Tools

**Governance** (constitutional enforcement):
- `init_anchor` — Start a session
- `vault_ledger` — Record to audit trail
- `vault_seal` — Commit decision permanently
- `verify_vault_ledger` — Verify record integrity
- `apex_soul` — Final safety verdict

**Intelligence** (reasoning & critique):
- `agi_mind` — Deep reasoning
- `agi_reason` — Logical reasoning
- `agi_reflect` — Self-examination
- `asi_heart` — Safety critique
- `asi_critique` — Adversarial review
- `asi_simulate` — "What if I do X?"

**Reality** (grounding in truth):
- `physics_reality` — Web search + grounding
- `reality_compass` — Epistemic intake
- `reality_atlas` — Philosophical mapping
- `math_estimator` — Computational cost estimate

**Memory**:
- `engineering_memory` — Session-scoped memory (Redis)

**Execution**:
- `code_engine` — Safe code execution
- `agentzero_engineer` — Generate new tools

---

## 📖 Plain English: What Are the 13 Floors?

| Floor | Plain English |
|-------|--------------|
| F1 AMANAH | "Can this be reversed?" — Reversibility check |
| F2 SIDDIQ | "Is this true?" — Fact-checking |
| F3 TRI_WITNESS | "Do 3 people agree?" — Human + AI + System consensus |
| F4 CLARITY | "Is the reasoning clear?" — Entropy must decrease |
| F5 PEACE² | "Will this cause harm?" — Non-destruction |
| F6 EMPATHY | "Did we listen?" — RASA listening protocol |
| F7 HUMILITY | "Are we overconfident?" — Ω must stay in GOLDILOCKS [0.03, 0.05] |
| F8 GENIUS | "Is this a good idea?" — System health check |
| F9 TAQWA | "Is this ethical?" — Ethics guard |
| F10 CONSCIENCE | "Any false claims?" — Truthfulness check |
| F11 AUDITABILITY | "Can we explain this?" — Transparent logging |
| F12 RESILIENCE | "Will this break things?" — Graceful failure |
| F13 ADAPTABILITY | "Is this safe to evolve?" — Safe self-modification |

---

## 💡 Hello World Code

```python
import aiohttp
import asyncio
import json

arifosmcp = "https://arifosmcp.arif-fazil.com/mcp"

async def ask(query: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "agi_reason",
            "arguments": {"query": query}
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(arifosmcp, json=payload, headers=headers) as resp:
            # SSE response — read data: lines
            async for line in resp.content:
                line = line.decode().strip()
                if line.startswith("data:"):
                    data = json.loads(line[5:])
                    result = data.get("result", {}).get("structuredContent", {})
                    print(f"Verdict: {result.get('verdict')}")
                    print(f"Tool: {result.get('tool')}")
                    return result

# Run
asyncio.run(ask("What is the speed of light?"))
```

**Output:**
```
Verdict: SEAL
Tool: agi_reason
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| `406 Not Acceptable` | Add header `Accept: application/json, text/event-stream` |
| `429 Rate Limited` | Wait 60s, you're sending too fast |
| `VOID` verdict | Check `floors` array in response — which floor failed? |
| No response | Try `/health` endpoint: `curl https://arifosmcp.arif-fazil.com/health` |

---

**Ditempa Bukan Diberi** — Intelligence is forged, not given.

For full documentation: [https://arifos.arif-fazil.com](https://arifos.arif-fazil.com)
