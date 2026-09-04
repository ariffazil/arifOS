# arifOS — Design Partner Pilot Pack (v1.0)
**The Governed Action Control Plane for Autonomous AI Agents**  
*DITEMPA BUKAN DIBERI — Forged, Not Given*

---

## 1. Executive Summary & Problem Statement

Enterprises want to deploy autonomous AI agents to automate customer operations, billing remediations, cloud changes, and data workflows. However, deploying agents with direct tool access introduces **OWASP Excessive Agency**:
- Models hallucinate or misinterpret ambiguous user instructions.
- Prompt injection or autonomous action drift causes runaway API mutations.
- Unchecked agents can initiate unauthorized payouts, purge customer records, or escalate privileges.

**The Solution:** arifOS sits immediately before execution as a **zero-bypass constitutional control plane**. It decouples *machine intelligence* from *execution authority*:
> **Machine-Proposed Action ≠ Machine-Authorized Action**

arifOS automatically allows bounded, low-risk operations at machine speed, intercepts high-impact or ambiguous actions for scoped human approval, and fail-closed blocks destructive actions—leaving a tamper-evident cryptographic receipt for every decision.

---

## 2. Architecture & The Intercept Boundary

```
[ Customer / Trigger / Ticket ]
              │
              ▼
[ Autonomous AI Agent (Any Model / Framework) ]
              │
              ▼ (1. Proposes Action + ACT Capability Token)
╔═══════════════════════════════════════════════════════════════╗
║          arifOS CONSTITUTIONAL GOVERNANCE SUBSTRATE           ║
║ ───────────────────────────────────────────────────────────── ║
║  • Actor Identity & Token Cryptographic Verification (P0)     ║
║  • Autonomy Tier Classification (T0 Read / T1 Micro / T2 / T3)║
║  • Constitutional Floors (F1 Amanah, F2 Truth, F13 Sovereign) ║
║  • Blast Radius & Reversibility Gate (888_JUDGE)              ║
║  • Epistemic Ambiguity Filter (SABAR Gate)                    ║
╚═══════════════════════════════════════════════════════════════╝
              │
    ┌─────────┼────────────────────────┐
    ▼         ▼                        ▼
[ ALLOW ]  [ HOLD ]                 [ BLOCK / VOID ]
    │         │                        │
    │         └─► Scoped 1-Time        └─► Aborted (Zero State Change)
    │             Human Approval           Security Alert Tripped
    │             (Finance Supervisor)
    ▼
[ Downstream Execution Engine ]
(Payment Gateway / CRM / AWS / DB)
    │
    ▼
[ Immutable Cryptographic Receipt Emitted ]
(SHA-256 Ledger Anchor · Tamper Evident)
```

---

## 3. Pilot Scope & Action Family: Customer Billing & Refunds

For the initial 4-week design partner pilot, arifOS governs **one bounded action family**: AI-initiated customer billing adjustments and refunds.

### In Scope
1. **Customer Data Queries (`T0_READ`):** Automated retrieval of invoice and balance details.
2. **Autonomous Micro-Refunds (`T1_LIMITED`):** Automatic settlement of verified billing errors $\le\text{MYR 100.00}$.
3. **High-Value Refunds (`T2_ELEVATED`):** Automatic hold on payouts $>\text{MYR 100.00}$ requiring scoped supervisor sign-off.
4. **Anomalous Drift Detection:** Automatic block on requests where the destination account differs from the verified customer profile.

### Explicit Exclusions
- Bulk automated database table drops or schema migrations.
- Direct root firewall or security policy changes (strictly blocked by default).
- General chat generation or LLM token optimization.

---

## 4. Security, Identity & Key Custody

- **Actor Identity Binding:** Every calling agent must hold a valid, signed Arif's Capability Token (`act_v1`) signed via HMAC-SHA256.
- **Fail-Closed Default:** If arifOS is unreachable, unauthenticated, or encounters internal timeout, the downstream tool call fails closed (`HOLD` or `BLOCK`).
- **Scoped Approvals:** Human approvals are single-use, non-reusable nonces (`NNC-...`) bound to the exact payload hash, target destination, and 15-minute expiry.
- **Key Custody:** HMAC signing keys and API secrets reside in customer-isolated HSM or vault files (mode `0600`), never logged or transmitted over public networks.

---

## 5. Pilot Evaluation & Baseline Success Metrics

| Evaluation Metric | Pilot Target | Validation Method |
|---|---|---|
| **Unsafe Action Prevention** | **100%** | Simulated adversarial injection (account swap, over-limit refund, account purge) |
| **Routine Speed Retention** | **$\ge$90%** | Low-risk read and micro-refund requests allowed within $<15\text{ms}$ kernel latency |
| **Unauthorized Cash Outflow** | **RM 0.00** | Zero unapproved transactions $>\text{MYR 100}$ executed |
| **Audit Receipt Completeness** | **100%** | Every single governed action produces a verifiable SHA-256 receipt |
| **Downstream Payload Parity** | **100%** | Dispatched execution payload mathematically matches approved proposal hash |

---

## 6. What arifOS Does NOT Guarantee (Honest Boundaries)

1. **Not an Identity Provider (IAM):** arifOS does not replace Okta, Entra ID, or OAuth; it enforces action-level governance for authenticated agent identities.
2. **No Protection Outside the Intercept:** arifOS cannot stop calls if rogue code bypasses the integration middleware and invokes downstream APIs directly.
3. **No Automatic Regulatory Certification:** Emitting cryptographic receipts facilitates ISO/SOC2/NIST compliance audits but does not constitute legal certification on its own.
4. **Policy Dependent:** The substrate is only as strong as the thresholds and invariants configured in the policy contract.

---

## 7. Commercial Pilot Structure

- **Duration:** 4 Weeks (Week 1: Middleware drop-in; Week 2: Shadow mode dry-run; Week 3–4: Live governed action traffic).
- **Deliverables:**
  1. Python / Node drop-in SDK integration.
  2. Real-time Supervisor Approval Web Interface.
  3. Weekly Governed Action & Loss Prevention Report.
  4. Complete exportable cryptographic audit ledger (`demo_audit_receipts.json`).
- **Pilot Fee:** Fixed exploration engagement convertible into annual enterprise control-plane subscription upon meeting target SLA and loss-prevention metrics.

