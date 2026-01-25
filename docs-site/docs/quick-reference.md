---
sidebar_position: 101
title: Quick Reference
description: One-page cheat sheet for arifOS
---

# Quick Reference Card

```
+-----------------------------------------------------------------------------+
|                    arifOS v52.5.1-SEAL QUICK REFERENCE                      |
+-----------------------------------------------------------------------------+
|                                                                             |
|  WHAT: A filter that stops AI from lying, harming, or being overconfident   |
|  HOW:  5 rules (TEACH) checked before every response                        |
|                                                                             |
|  -------------------------------------------------------------------------  |
|                                                                             |
|  THE 5 RULES (TEACH):                                                       |
|    T - Truth      ≥99% confident OR say "I don't know"                      |
|    E - Empathy    Protect the weakest person affected                       |
|    A - Amanah     Warn before irreversible actions                          |
|    C - Clarity    Answer clearer than the question                          |
|    H - Humility   Leave 3-5% room for "I might be wrong"                    |
|                                                                             |
|  -------------------------------------------------------------------------  |
|                                                                             |
|  THE 4 VERDICTS:                                                            |
|    SEAL     = All good -> Response delivered                                |
|    SABAR    = Minor issue -> Adjusted + warning                             |
|    VOID     = Serious problem -> Blocked + explanation                      |
|    888_HOLD = High stakes -> Pause + ask human to confirm                   |
|                                                                             |
|  -------------------------------------------------------------------------  |
|                                                                             |
|  THE 4 LANES (ATLAS-333):                                                   |
|    CRISIS  -> Maximum caution, human required (suicide, self-harm)          |
|    FACTUAL -> Full fact-checking (code, research, technical)                |
|    CARE    -> Empathy focus (emotional support)                             |
|    SOCIAL  -> Light touch (greetings, casual)                               |
|                                                                             |
|  -------------------------------------------------------------------------  |
|                                                                             |
|  THE 5 MCP TOOLS:                                                           |
|    init_000   -> Gate (7-step ignition)                                     |
|    agi_genius -> Mind (truth, clarity, humility)                            |
|    asi_act    -> Heart (empathy, safety, reversibility)                     |
|    apex_judge -> Soul (verdict, consensus)                                  |
|    vault_999  -> Seal (immutable ledger)                                    |
|                                                                             |
|  -------------------------------------------------------------------------  |
|                                                                             |
|  CONNECT:                                                                   |
|    Health:  https://arifos.arif-fazil.com/health                            |
|    Docs:    https://docs.arif-fazil.com                                     |
|    MCP:     https://arifos.arif-fazil.com/sse                               |
|                                                                             |
|  INSTALL:                                                                   |
|    pip install arifos                                                       |
|    python -m arifos.mcp                                                     |
|                                                                             |
|  -------------------------------------------------------------------------  |
|                                                                             |
|  MOTTO: "Ditempa Bukan Diberi" — Forged, Not Given                          |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## Floor Thresholds

| Floor | Name | Threshold | Type |
|-------|------|-----------|------|
| F1 | Amanah | LOCK | Hard |
| F2 | Truth | ≥0.99 | Hard |
| F3 | Tri-Witness | ≥0.95 | Hard |
| F4 | Clarity | ΔS≥0 | Hard |
| F5 | Peace² | ≥1.0 | Soft |
| F6 | Empathy | κᵣ≥0.95 | Soft |
| F7 | Humility | [0.03,0.05] | Hard |

## MCP Quick Config

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

## Links

| Resource | URL |
|----------|-----|
| Live Server | https://arifos.arif-fazil.com |
| Documentation | https://docs.arif-fazil.com |
| GitHub | https://github.com/ariffazil/arifOS |
| PyPI | https://pypi.org/project/arifos/ |
