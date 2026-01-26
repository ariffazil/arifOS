---
sidebar_position: 100
title: FAQ
description: Frequently asked questions about arifOS
---

# Frequently Asked Questions

## General

### What is arifOS?

arifOS is a **governance filter** for AI systems. It checks AI outputs against 5 principles (TEACH) before they reach users, blocking or adjusting responses that could be harmful, dishonest, or overconfident.

### Does arifOS contain an AI?

**No.** arifOS is a filter, not a model. It validates outputs from other AI systems (ChatGPT, Claude, Gemini, etc.) but doesn't generate content itself.

### Is arifOS actually running somewhere?

**Yes.** [arifos.arif-fazil.com](https://arifos.arif-fazil.com) is live 24/7 on Railway. You can verify by visiting [/health](https://arifos.arif-fazil.com/health).

### What does "Ditempa Bukan Diberi" mean?

It's Malay for **"Forged, Not Given."** Good AI governance is earned through constraint, not granted freely. Like forging metal—heat, pressure, then cooling.

---

## Technical

### What is MCP?

MCP (Model Context Protocol) is a standard for AI tools to connect to external services. Think of it like USB for AI—a universal plug. It allows Claude Desktop, Cursor, and other tools to connect to arifOS as an external service.

### Can I run arifOS locally?

Yes:
```bash
pip install arifos
python -m arifos.mcp
```

### What's the difference between SSE and stdio?

- **stdio** — For local clients (Claude Desktop, Cursor) connecting to a local arifOS
- **SSE** — For remote clients connecting over the internet

### How does ATLAS-333 detect intent?

ATLAS-333 uses keyword patterns and signal extraction to classify queries into lanes:
- Crisis keywords → CRISIS lane
- Technical patterns → FACTUAL lane
- Emotional indicators → CARE lane
- Social patterns → SOCIAL lane

### How much latency does arifOS add?

The governance check adds ~50ms latency. For most use cases, this is imperceptible.

---

## Usage

### What if I disagree with a VOID?

You can override. arifOS warns but doesn't imprison. **You're the human. You decide.**

However, if you override repeatedly, consider why. The system might be catching something important.

### Can I customize the thresholds?

In the self-hosted version, yes. The floor thresholds are defined in `spec/constitutional_floors.json`. The cloud version uses standard thresholds.

### Does arifOS work with ChatGPT?

Yes, but not via MCP. Instead:
1. Copy the [system prompt](/ai/system-prompt)
2. Paste into ChatGPT's Custom Instructions
3. The AI will self-govern using TEACH

### Can AI systems read these docs and self-govern?

**Yes!** The [For AI Systems](/ai/self-governance) section is specifically written for AI readers. An AI can read this documentation and implement self-governance without MCP.

---

## Philosophical

### Why 5 principles? Why TEACH?

Five is memorable. TEACH spells out the core values:
- **T**ruth — Don't lie
- **E**mpathy — Don't harm
- **A**manah — Be trustworthy
- **C**larity — Don't confuse
- **H**umility — Don't be arrogant

### Why is Amanah a Malay word?

The author (Muhammad Arif) is Malaysian. "Amanah" captures trust + responsibility better than any single English word. It's also a reminder that good values come from many cultures.

### Isn't this just Constitutional AI?

arifOS is inspired by Constitutional AI (Anthropic), but extends it with:
- Real-time enforcement via MCP
- Thermodynamic governance (entropy, cooling)
- Tri-witness consensus (Mind, Heart, Soul)
- Immutable audit trail (VAULT999)

---

## Troubleshooting

### Tools not showing in Claude Desktop

1. Check config file location is correct
2. Ensure JSON syntax is valid
3. **Restart Claude Desktop** (required after config changes)

### Connection refused to localhost

1. Is the server running? `python -m arifos.mcp sse`
2. Check port: default is 8000
3. Check firewall settings

### Getting VOID when I expect SEAL

Check which floor failed:
```json
{
  "verdict": "VOID",
  "floor_summary": {
    "failed": ["F2"]  // ← This tells you which floor
  }
}
```

Common causes:
- F2: Unverified fact stated as certain
- F7: Missing uncertainty language
- F4: Response more confusing than question
