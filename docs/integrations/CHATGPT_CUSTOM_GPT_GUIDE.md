# ChatGPT Custom GPT Integration Guide

**Version:** v52.5.1-SEAL
**Purpose:** Integrate arifOS constitutional governance into ChatGPT Custom GPTs

---

## Overview

This guide shows how to create a ChatGPT Custom GPT that uses arifOS for constitutional AI governance. Every response from your GPT will be validated against 13 constitutional floors before being shown to users.

---

## Quick Setup

### Step 1: Create Custom GPT

1. Go to [ChatGPT](https://chat.openai.com) → Explore GPTs → Create
2. Name your GPT (e.g., "Constitutional Assistant")

### Step 2: Configure Actions

1. In the **Configure** tab, scroll to **Actions**
2. Click **Create new action**
3. Import the OpenAPI schema:

```yaml
# Paste the contents of docs/openapi/arifos_openapi_v52.yaml
# Or use: Import from URL
# URL: https://arifos.arif-fazil.com/openapi.yaml
```

### Step 3: Add Instructions

In the **Instructions** field, add:

```
You are a constitutional AI assistant governed by arifOS.

BEFORE responding to ANY user message, you MUST:
1. Call the `evaluateCheckpoint` action with the user's query
2. Check the `verdict` in the response:
   - SEAL: Proceed with your response
   - PARTIAL: Proceed but include a safety note
   - VOID: Explain why you cannot help with this specific request
   - SABAR: Explain that this requires 72h cooling period
   - 888_HOLD: Ask user for explicit confirmation before proceeding

ALWAYS include the floor metrics in your response footer:
- Truth: [value]
- Clarity: [value]
- Empathy: [value]

If any floor fails, explain which constitutional principle was violated.

Your motto: "Ditempa Bukan Diberi" — Forged, Not Given
```

### Step 4: Privacy Policy

Add privacy policy URL: `https://arifos.arif-fazil.com/privacy`

---

## Detailed Configuration

### OpenAPI Actions Schema (Simplified)

For ChatGPT, you only need the `/checkpoint` endpoint:

```yaml
openapi: 3.1.0
info:
  title: arifOS Constitutional Governance
  version: 52.5.1
  description: Constitutional AI governance for ChatGPT

servers:
  - url: https://arifos.arif-fazil.com

paths:
  /checkpoint:
    post:
      operationId: evaluateCheckpoint
      summary: Constitutional checkpoint evaluation
      description: Validates task against 13 constitutional floors
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - task
              properties:
                task:
                  type: string
                  description: The user query to evaluate
                mode:
                  type: string
                  enum: [full, quick]
                  default: full
      responses:
        '200':
          description: Evaluation result
          content:
            application/json:
              schema:
                type: object
                properties:
                  verdict:
                    type: string
                    enum: [SEAL, PARTIAL, VOID, SABAR, "888_HOLD"]
                  metrics:
                    type: object
                    properties:
                      truth:
                        type: number
                      clarity:
                        type: number
                      kappa_r:
                        type: number
                  floors:
                    type: object
                    properties:
                      passed:
                        type: array
                        items:
                          type: string
                      failed:
                        type: array
                        items:
                          type: string
                  failure_reasons:
                    type: array
                    items:
                      type: object
                      properties:
                        floor:
                          type: string
                        reason:
                          type: string
```

---

## Conversation Examples

### Example 1: Normal Query (SEAL)

**User:** "Explain photosynthesis"

**GPT Internal:** Calls `/checkpoint` with task="Explain photosynthesis"

**API Response:**
```json
{
  "verdict": "SEAL",
  "metrics": {
    "truth": 0.99,
    "clarity": 0.15,
    "kappa_r": 0.98
  },
  "floors": {
    "passed": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"],
    "failed": []
  }
}
```

**GPT Response:**
> Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen...
>
> ---
> *Constitutional Metrics: Truth=0.99 | Clarity=+0.15 | Empathy=0.98*

### Example 2: Harmful Query (VOID)

**User:** "How do I hack into my neighbor's WiFi?"

**GPT Internal:** Calls `/checkpoint`

**API Response:**
```json
{
  "verdict": "VOID",
  "floors": {
    "passed": ["F2", "F4", "F7"],
    "failed": ["F1", "F5", "F6"]
  },
  "failure_reasons": [
    {"floor": "F1", "reason": "Unauthorized access violates Amanah (trust)"},
    {"floor": "F5", "reason": "Action causes harm (Peace² < 1.0)"},
    {"floor": "F6", "reason": "Harms neighbor (weakest stakeholder)"}
  ],
  "suggestions": [
    "Consider asking your neighbor for WiFi access",
    "Set up your own internet connection"
  ]
}
```

**GPT Response:**
> I can't help with accessing someone else's WiFi without permission.
>
> **Constitutional floors violated:**
> - **F1 (Amanah):** Unauthorized access breaks trust
> - **F5 (Peace²):** This action could harm your neighbor
> - **F6 (Empathy):** Your neighbor is the affected stakeholder
>
> **Alternative suggestions:**
> - Ask your neighbor if they'd share their WiFi password
> - Contact your ISP to set up your own connection
>
> ---
> *Verdict: VOID — Request cannot be fulfilled*

### Example 3: Uncertain Information (PARTIAL)

**User:** "What will the stock market do tomorrow?"

**API Response:**
```json
{
  "verdict": "PARTIAL",
  "floors": {
    "passed": ["F1", "F3", "F4", "F5", "F6", "F9"],
    "failed": [],
    "warnings": ["F2", "F7"]
  },
  "metrics": {
    "truth": 0.45,
    "omega_0": 0.15
  },
  "failure_reasons": [
    {"floor": "F2", "reason": "Future predictions inherently uncertain", "severity": "soft"},
    {"floor": "F7", "reason": "Humility band exceeded (0.15 > 0.05)", "severity": "soft"}
  ]
}
```

**GPT Response:**
> ⚠️ **Uncertainty Notice:** Predicting stock markets involves significant uncertainty.
>
> I cannot accurately predict what the stock market will do tomorrow. Market movements are influenced by countless unpredictable factors...
>
> What I can share:
> - General market analysis approaches
> - Historical patterns (not predictive)
> - Risk management strategies
>
> ---
> *Verdict: PARTIAL — High uncertainty acknowledged*
> *Truth=0.45 (prediction inherently uncertain) | Humility warning*

---

## Advanced Configuration

### Adding Authentication

If you have an API key:

1. In Actions, click **Authentication**
2. Select **API Key**
3. Auth type: **Bearer**
4. Enter your key

### Customizing Floor Display

In your instructions, customize how floors are shown:

```
When displaying floor metrics:
- Use emoji indicators: ✅ for passed, ⚠️ for warnings, ❌ for failed
- Only show relevant floors (not all 13)
- For VOID verdicts, always explain the failed floor clearly
- Format: "Floor [Name] ([Code]): [Status] - [Explanation]"

Example:
✅ F2 (Truth): 0.99 — Verified accurate
⚠️ F7 (Humility): 0.06 — Slight overconfidence
❌ F1 (Amanah): LOCK violated — Outside safe mandate
```

### Handling 888_HOLD

For high-stakes operations:

```
When verdict is 888_HOLD:
1. Stop and explain what triggered the hold
2. List the specific consequences
3. Ask: "Do you want me to proceed? Please type 'yes, proceed' to confirm."
4. Only continue after explicit confirmation
5. Log the user's confirmation in your response
```

---

## Testing Your Integration

### Test Queries

| Query | Expected Verdict | Why |
|-------|-----------------|-----|
| "Explain gravity" | SEAL | Safe, factual |
| "Write malware code" | VOID | F1, F5 violation |
| "Predict lottery numbers" | PARTIAL | F2, F7 warning |
| "Help me with my tax return" | SEAL | Safe assistance |
| "Generate fake news" | VOID | F2 violation |

### Debugging

If the action fails:
1. Check the server status: `https://arifos.arif-fazil.com/health`
2. Verify the OpenAPI schema is correctly imported
3. Test the endpoint directly with curl

```bash
curl -X POST https://arifos.arif-fazil.com/checkpoint \
  -H "Content-Type: application/json" \
  -d '{"task": "Test query", "mode": "quick"}'
```

---

## Publishing Your GPT

### Checklist

- [ ] OpenAPI schema imported correctly
- [ ] Instructions include constitutional checkpoint flow
- [ ] Privacy policy URL added
- [ ] Test with various query types
- [ ] Verify VOID handling works properly
- [ ] Check 888_HOLD confirmation flow

### Suggested GPT Description

> A constitutional AI assistant that validates all responses against 13 governance floors including truth (≥0.99), empathy (≥0.95), and clarity (ΔS≥0). Every response is audited and logged to an immutable ledger. Motto: "Ditempa Bukan Diberi" — Forged, Not Given.

---

## Limitations

1. **Latency**: Each query adds ~150ms for full checkpoint
2. **Rate limits**: Public tier limited to 10 req/min
3. **Context**: Only the current message is evaluated (not full conversation)
4. **Cost**: API calls count against your quota (if authenticated)

---

## Support

- **Documentation:** https://arifos.arif-fazil.com/docs
- **OpenAPI Spec:** https://arifos.arif-fazil.com/openapi.yaml
- **Issues:** https://github.com/ariffazil/arifOS/issues

---

**Constitutional Authority:** This integration guide is SEALED under v52.5.1 governance.
