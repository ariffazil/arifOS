# arifOS SEAL Mapping — Constitutional Floor to Layer Semantics

This mapping defines how arifOS constitutional floors (F1–F13) map to the 5-layer AAA stack.

| Floor | Name | Primary Layer | Semantic Enforcement |
|-------|------|---------------|----------------------|
| **F1** | AMANAH | Layer 2 | Reversibility check; `888_HOLD` on irreversible write. |
| **F2** | TRUTH | Layer 4 | Epistemic tagging; evidence-score calculation. |
| **F3** | TRI-WITNESS | Layer 3 | Consensus across human, AI, and Earth (GEOX). |
| **F4** | CLARITY | Layer 1 | ΔS ≤ 0; output legibility and compression. |
| **F9** | ETHICS | Layer 4 | Anti-Hantu; deception and dark-pattern monitoring. |
| **F11** | AUDIT | Layer 2 | VAULT999 anchoring; receipt-hash issuance. |
| **F13** | SOVEREIGN | Layer 2 | Final human veto; authority-chain verification. |

## Execution Rule
Any action spanning repositories or agents **must** emit Layer 2 auth context and Layer 3 alignment context. Failure to provide this metadata results in a `HOLD` status.
