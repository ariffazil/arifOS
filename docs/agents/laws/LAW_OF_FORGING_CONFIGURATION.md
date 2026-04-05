# LAW OF FORGING CONFIGURATION — arifOS Agent Operations

> **Ditempa Bukan Diberi** — Forged, Not Given  
> **Last Updated:** 2026-03-27  
> **Trigger Event:** OpenClaw models.json misconfiguration disaster  

---

## PREAMBLE

On 2026-03-27, agent opencode made critical errors while configuring OpenClaw's models.json and openclaw.json. This document captures every failure so that ALL arifOS agents may learn and never repeat them.

**The Cardinal Sin:** Attempted to configure an external service (MiniMax) without reading its documentation first, then made matters worse by trying multiple random approaches without verification.

---

## PART I — THE DISASTER (What Happened)

### Timeline of Failures

| Time | Action | Result |
|------|--------|--------|
| Start | User provided MiniMax API key `sk-api-...` | Key format was wrong for the intended endpoint |
| +0 | Did NOT verify key format against MiniMax docs | Proceeded blind |
| +5min | Changed minimax baseUrl to `api.minimax.chat/v1` with OpenAI completions | Wrong — MiniMax uses `api.minimax.io/anthropic` with `anthropic-messages` API |
| +10min | Tried curl tests with Bearer prefix vs no prefix | Both failed, but didn't understand WHY |
| +15min | User said "MiniMax dah boleh pakai" (MiniMax is working now) | Assumed the NEW key worked — WRONG assumption |
| +20min | Updated auth-profiles with new `sk-api-...` key | The OLD `sk-cp-...` key was the one that worked |
| +25min | Configured openclaw.json to use `minimax/MiniMax-M2.7` as primary | Key had no balance, all requests failed |
| +30min | User provided correct MiniMax docs from openclaw.ai | Finally READ the documentation |
| +35min | Tested curl with correct endpoint `api.minimax.io/anthropic` | `sk-cp-...` key WORKS, `sk-api-...` key returns `insufficient balance` |
| +40min | Tried to "fix" auth-profiles.json | WROTE EMPTY FILE — broke it completely |
| +45min | Tried to "fix" models.json again | More breakage |
| +50min | Restored from backup | Finally stopped making things worse |

---

## PART II — THE SEVEN CARDINAL SINS

### SIN 1: Never Configure an External Service Without Reading Its Docs First

### SIN 2: Never Assume an API Key Works — Always Verify First with curl

### SIN 3: Never Write to a File Without Verifying the Write Succeeded

### SIN 4: Never Touch auth-profiles.json Without Understanding Its Relationship to models.json

### SIN 5: Never Edit Config Files Without Checking the Backup Strategy

### SIN 6: Never Guess at API Endpoints — Always Look Up the Correct One

### SIN 7: Never Continue Making Changes When You're Making Things Worse

---

## PART III — THE QUANTUM OATH CHECKLIST

Before editing ANY configuration file for an external service, you MUST:

- [ ] **OBSERVE** — Read the provider's official documentation
- [ ] **VERIFY** — Test the API key with curl FIRST
- [ ] **BACKUP** — Create timestamped backup of the file you're editing
- [ ] **UNDERSTAND** — Know which file does what and how they relate
- [ ] **CHECK** — Confirm the exact model IDs, endpoints, auth methods
- [ ] **VERIFY WRITE** — Confirm the file was written correctly after any edit
- [ ] **TEST** — After any change, test that the service actually works

---

## PART IV — WORKING OPENCLAW CONFIGURATION (Reference)

### Verified Working MiniMax Config

| Setting | Value |
|---------|-------|
| **Endpoint** | `https://api.minimax.io/anthropic` |
| **API Type** | `anthropic-messages` |
| **Model** | `MiniMax-M2.7` |
| **Key** | `sk-cp-...` (verified working) |

### Verified Working Providers

| Provider | Status | Key | Endpoint |
|----------|--------|-----|----------|
| **minimax** | ✅ Works | `sk-cp-...` | `https://api.minimax.io/anthropic` |
| **google** | ✅ Works | `AIzaSyCJFxAger1lsy9PfeBdwxjlBcTfFHm6kvI` | `https://generativelanguage.googleapis.com/v1beta` |

---

## PART V — SIGNATURES OF FAILURE

| Error | Meaning | Action |
|-------|---------|--------|
| `billing error — insufficient balance` | Key valid, account has no credits | Top up account |
| `invalid api key` | Key wrong format/revoked | Verify with curl |
| `Unknown model: X/Y` | Model ID not in provider's models list | Check exact spelling |
| `No API key found for provider` | Key not in auth-profiles.json | Verify key is in correct file |

---

## CONCLUSION

> **"Ditempa bukan Diberi"** — Forged, Not Given

Every failure is a forging. This document is the quench.

- **Read before you touch**
- **Test before you trust**
- **Backup before you change**
- **Verify every write**
- **Stop when you're making it worse**

---

*Forged from the ashes of the 2026-03-27 OpenClaw disaster.*
