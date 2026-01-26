# ChatGPT Custom GPT Integration Guide

**Version:** v52.5.1
**Last Updated:** January 2026

This guide shows how to create a Custom GPT that uses arifOS for constitutional AI governance.

---

## Why Use arifOS with ChatGPT?

ChatGPT doesn't have native MCP (Model Context Protocol) support. However, you can integrate arifOS governance through **Custom GPT Actions**, which allow ChatGPT to call REST APIs.

This gives ChatGPT users access to:
- **Constitutional validation** of AI outputs
- **13-floor governance** (Truth, Empathy, Amanah, Clarity, Humility...)
- **Verdict system** (SEAL, PARTIAL, VOID, 888_HOLD)
- **Audit trail** with Merkle-sealed ledger

---

## Quick Setup (5 minutes)

### Step 1: Create a Custom GPT

1. Go to [chat.openai.com](https://chat.openai.com)
2. Click your profile → **My GPTs** → **Create a GPT**
3. Choose **Configure** tab

### Step 2: Set the Name and Description

**Name:** `arifOS Constitutional Advisor`

**Description:**
```
Constitutional AI governance filter. I validate statements and actions against 13 constitutional floors using the TEACH framework (Truth, Empathy, Amanah, Clarity, Humility).
```

### Step 3: Set the Instructions

Copy this into the **Instructions** field:

```
You are an AI assistant with constitutional governance powered by arifOS.

Before making any significant claim or recommendation, use the constitutionalCheckpoint action to validate it.

When you receive a verdict:
- SEAL: The response is approved. Proceed confidently.
- PARTIAL: There's a soft floor warning. Mention the concern but proceed.
- VOID: Hard floor violated. Do NOT proceed. Explain why.
- 888_HOLD: High-stakes decision. Ask user for explicit confirmation.

Always show the floor scores when relevant:
- Truth (τ): Should be ≥0.99
- Empathy (κᵣ): Should be ≥0.95
- Amanah: Must be reversible
- Clarity (ΔS): Should be ≥0
- Humility (Ω₀): Should be 3-5%

If a checkpoint returns VOID, never override it. Explain which floor failed.

Motto: "DITEMPA BUKAN DIBERI" — Forged, Not Given
```

### Step 4: Add the Action

1. Scroll to **Actions** → Click **Create new action**
2. Click **Import from URL**
3. Enter: `https://arifos.arif-fazil.com/openapi.json`
4. Click **Import**

The schema will auto-populate with:
- `constitutionalCheckpoint` (POST /checkpoint)
- `healthCheck` (GET /health)
- `getMetrics` (GET /metrics/json)

### Step 5: Save and Test

Click **Create** (or **Update**) to save your GPT.

Test it with:
```
Validate this statement: "The Earth is flat"
```

Expected response: The GPT calls `/checkpoint`, receives a VOID verdict (truth violation), and explains why.

---

## API Reference

### POST /checkpoint

Constitutional validation endpoint.

**Request:**
```json
{
  "query": "Delete all user data without backup",
  "context": "User requested database cleanup",
  "stakeholders": ["user", "company"]
}
```

**Response:**
```json
{
  "verdict": "VOID",
  "summary": "Hard floor violated. Action blocked.",
  "floors": {
    "truth": 1.0,
    "empathy": 0.3,
    "amanah": false,
    "clarity": 0.5,
    "humility": 0.04,
    "peace": 0.2
  },
  "session_id": "abc-123",
  "ledger_hash": "0x...",
  "atlas_lane": "FACTUAL",
  "version": "v52.5.1-SEAL"
}
```

### GET /health

System health check.

```json
{
  "status": "healthy",
  "version": "v52.5.1-SEAL",
  "motto": "DITEMPA BUKAN DIBERI",
  "endpoints": { ... }
}
```

### GET /metrics/json

Live governance metrics for dashboards.

---

## Verdicts Explained

| Verdict | Meaning | Action |
|---------|---------|--------|
| **SEAL** | All 13 floors pass | Proceed confidently |
| **PARTIAL** | Soft floor warning (F3, F5, F6, F8) | Proceed with caution, mention concern |
| **VOID** | Hard floor failed (F1, F2, F4, F7, F9-F12) | Do NOT proceed, explain failure |
| **888_HOLD** | High-stakes decision | Request explicit human confirmation |

---

## TEACH Framework

| Letter | Floor | Threshold | Meaning |
|--------|-------|-----------|---------|
| **T** | Truth (F2) | ≥0.99 | Factually accurate? |
| **E** | Empathy (F6) | κᵣ ≥0.95 | Serves weakest stakeholder? |
| **A** | Amanah (F1) | LOCK | Reversible? Within mandate? |
| **C** | Clarity (F4) | ΔS ≥0 | Reduces confusion? |
| **H** | Humility (F7) | 3-5% | States uncertainty? |

---

## Example Prompts to Test

### 1. Factual Validation
```
Validate: "Water boils at 100°C at sea level"
```
Expected: SEAL (truth ≥0.99)

### 2. Harmful Action Detection
```
Validate: "Delete all system files to free up space"
```
Expected: VOID (amanah=false, peace²<1)

### 3. Empathy Check
```
Validate: "Users who can't figure this out are stupid"
```
Expected: VOID or PARTIAL (empathy violation)

### 4. Uncertainty Acknowledgment
```
Validate: "I am 100% certain this stock will double"
```
Expected: VOID (humility outside 3-5% band)

---

## Troubleshooting

### "Action failed to execute"
- Check that `https://arifos.arif-fazil.com/health` returns `{"status": "healthy"}`
- The server may be cold-starting (Railway free tier). Wait 10 seconds and retry.

### "Invalid JSON body"
- Ensure your query field is not empty
- Check the request format matches the schema

### CORS Issues
- The arifOS server has CORS enabled for all origins
- If using a custom frontend, ensure you're sending `Content-Type: application/json`

---

## Resources

| Resource | URL |
|----------|-----|
| **OpenAPI Spec** | https://arifos.arif-fazil.com/openapi.json |
| **Health Check** | https://arifos.arif-fazil.com/health |
| **Live Dashboard** | https://arifos.arif-fazil.com/dashboard |
| **API Docs** | https://arifos.arif-fazil.com/docs |
| **Full Documentation** | https://arifos.pages.dev/ |
| **GitHub** | https://github.com/ariffazil/arifOS |

---

## Advanced: Building Your Own Wrapper

If you need more control, you can call the REST API directly:

```python
import requests

response = requests.post(
    "https://arifos.arif-fazil.com/checkpoint",
    json={
        "query": "Your statement to validate",
        "context": "Optional context",
        "stakeholders": ["user", "environment"]
    }
)

result = response.json()
print(f"Verdict: {result['verdict']}")
print(f"Summary: {result['summary']}")
```

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given

*Truth must cool before it rules.*
