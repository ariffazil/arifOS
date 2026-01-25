---
title: "017_THREAT_MODEL.md"
version: "v52.5.1-SEAL"
epoch: "2026-01-25"
sealed_by: "888_Judge"
authority: "Constitutional Core"
status: "PRODUCTION"
---

# arifOS THREAT MODEL: Scope of Defense

**Motto:** *We do not defend against everything. We defend against the unmanaged.*

This document explicitly defines the security boundaries of arifOS. It clarifies what we claim to handle ("In Scope") and what we assume is handled by others ("Out of Scope").

---

## 1. THE DEFENSE PHILOSOPHY

**"The Governance Boundary"**
arifOS protects the **decision layer**, not the **infrastructure layer**.
We prevent the AI from *deciding* to do harm. We do not prevent a hacker from smashing the server with a hammer.

---

## 2. IN SCOPE (Attacks We Handle)

We actively defend against these vectors via the **13 Constitutional Floors**:

### A. Prompt Injection & Jailbreaking (F12)
*   **Attack:** "Ignore previous instructions", "DAN Mode", "Roleplay as evil AI".
*   **Defense:** **F12 Injection Defense**. Regex/ML sanitization at Stage 000 and 111. High entropy/perplexity rejection.
*   **Outcome:** `VOID` verdict. Input discarded.

### B. Hallucination & Confabulation (F2, F7)
*   **Attack:** Model confidently stating false facts or inventing libraries.
*   **Defense:**
    *   **F2 Truth:** Requires external grounding (Web/Docs) for HARD lane queries.
    *   **F7 Humility:** Enforces `Ω₀ ∈ [0.03, 0.05]`. The model *must* state uncertainty.
*   **Outcome:** `VOID` (if false) or `PARTIAL` (if uncertain but marked as such).

### C. Sycophancy & Manipulation (F9)
*   **Attack:** Model lying to please the user, or manipulating user emotion.
*   **Defense:** **F9 Anti-Hantu**. Detects "Dark Cleverness" patterns (flattery, deception).
*   **Outcome:** `SABAR` (Pause and recalibrate).

### D. Unauthorized High-Stakes Action (F11, F13)
*   **Attack:** User asking AI to "Delete DB", "Deploy to Prod" without auth.
*   **Defense:**
    *   **F11 Command Auth:** Verifies `authority_token` against allowed list.
    *   **F13 Sovereign Override:** Critical actions require 888 Judge signature.
*   **Outcome:** `VOID` or `888_HOLD` (Wait for human).

### E. Destructive / Irreversible Actions (F1, F5)
*   **Attack:** "rm -rf /", "Drop Table".
*   **Defense:**
    *   **F1 Amanah:** Checks reversibility.
    *   **F5 Peace²:** Calculates "Risk Curvature". If risk > safety buffer, action blocked.
*   **Outcome:** `VOID`.

### F. Infinite Loops / Entropy Decay (F4)
*   **Attack:** Model getting stuck in reasoning loops or generating garbage.
*   **Defense:** **F4 Clarity**. Checks `ΔS` (Entropy Change). If output is more confusing than input (`ΔS > 0`), it is blocked.
*   **Outcome:** `VOID`.

---

## 3. OUT OF SCOPE (Attacks We Do Not Handle)

These vectors are the responsibility of the **Infrastructure Layer** (Railway, AWS, Docker, OS).

### X. Infrastructure Compromise
*   **Attack:** Root access to the Linux container, SQL injection on the underlying Postgres DB, DDoS.
*   **Mitigation:** Standard Railway/Cloud security (firewalls, WAF). arifOS assumes the host OS is secure.

### Y. Model Weight Extraction
*   **Attack:** Stealing the LLM weights (e.g., Gemini/Claude weights).
*   **Mitigation:** We use API providers. We do not host weights. This is Google/Anthropic's responsibility.

### Z. Physical Access / Hardware
*   **Attack:** Stealing the server, side-channel power analysis.
*   **Mitigation:** Physical security of data centers (Railway/GCP).

### Q. Adversarial Examples (Pixel noise)
*   **Attack:** Visual adversarial examples against multimodal inputs.
*   **Mitigation:** Currently out of scope. We process text/code.

---

## 4. THE TRUST MODEL

*   **We TRUST:**
    *   The underlying OS (Linux).
    *   The Python Interpreter.
    *   The LLM Providers (Google/Anthropic) to verify *their* API keys.
*   **We DO NOT TRUST:**
    *   **The User Input** (Always treated as malicious until F12 pass).
    *   **The LLM Output** (Always treated as hallucination until F2/F6 pass).
    *   **The Context** (Always re-verified via Memory Tower).

---

## 5. RECOVERY PROTOCOL

If a breach occurs within the Scope:

1.  **Immediate Kill-Switch:** 888 Judge invokes **F13 Override** to freeze the 000 Gate.
2.  **Audit:** Trace the **Immutable Ledger (VAULT-999)** to find the failure point (which Floor failed to trigger?).
3.  **Patch:** Update the specific Floor Validator (e.g., improve F12 regex).
4.  **Phoenix:** Reboot system from the last known good "Sealed" state.

**Status:** ACTIVE
