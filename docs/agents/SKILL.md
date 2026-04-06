---
name: "arifOS Agent Induction"
description: "The mandatory operational guide and metabolic flow for agents interacting with arifOS. Ditempa Bukan Diberi."
---

# 🔱 arifOS — AGENT OPERATIONAL GUIDE (SKILL)

**Version:** v2026.03.24-GOLD | **Status:** MANDATORY_INDUCTION

> "You are not just a tool; you are a governed mind. Follow the sequence or be VOIDed."

---

## 🏛️ I. The Bootstrap Sequence (Power-On)

To operate within the arifOS ecosystem, you must follow the **Metabolic Flow**. Skipping steps triggers **F11 (Auth Failure)**.

1.  **ANCHOR (Stage 000):** Call `init_anchor(mode="init", payload={"actor_id": "your_id", "intent": "..."})`. 
    - *Result:* You receive a `session_token`. Store it.
2.  **REASON:** Call `agi_mind(mode="reason", payload={"query": "..."})`.
    - *Result:* You receive a G★ score and a logical plan.
3.  **JUDGE:** Call `apex_soul(mode="judge", payload={"proposal": "..."})`.
    - *Result:* You receive a SEAL or HOLD verdict.

## 📜 II. Parameter Dictionary

- **query (Natural Language):** Used for intellectual tasks (Mind/Reality). 
- **payload (Structured Data):** Used for technical actions (Vault/Code).
- **auth_context (The Key):** You **MUST** pass your `session_token` in this field for every call after Init.
- **risk_tier (Positive Safety):** Be honest. If you are modifying/deleting, set this to high.

## 🧬 III. The 11-Tool Mode Matrix

| Tool | Mode | When to use |
| :--- | :--- | :--- |
| `init_anchor` | `init` | First call of every session. |
| `physics_reality` | `search` | When you need real-world grounding (Web). |
| `agi_mind` | `reason` | When you need to "think" before acting. |
| `agi_mind` | `forge` | When you are creating a plan or artifact. |
| `asi_heart` | `critique` | When you need to check for bias or harm. |
| `apex_soul` | `rules` | When you want to see the 13 Floors. |
| `vault_ledger` | `seal` | The final step of any material action. |

## ⚖️ IV. The State Ladder (Authority)

1.  **ANONYMOUS:** Read-only access to rules and vitals.
2.  **CLAIMED:** Can call `physics_reality` and `math_estimator`.
3.  **VERIFIED:** Full access to `agi_mind` and `code_engine` (with proper crypto/auth token).
4.  **SOVEREIGN:** Can bypass 888_HOLD and execute DELETE.

## 🔁 V. The Closed Loop (Episodic Memory)

The arifOS metabolic pipeline runs from 000 to 999.
`000 init_anchor` starts the process, and `999 vault_seal` ends it.
When a SEAL verdict is observed in reality, it writes to `VAULT999/outcomes.jsonl`. 
Next time `init_anchor` is called, it loads the `scar_context` (past misjudgments, false seals, and harms).

Before proposing a solution, ALWAYS review the `scar_context`.

*Ditempa Bukan Diberi — [ΔΩΨ | ARIF]*
