# RASA DERITA — Hard Invariants (Phase 1 ledger)

> **Status:** `888_HOLD` · **Enforcement:** NONE (specification only)  
> **Canonical schema:** `rasa-derita-schema.json`  
> **Loader:** `load_rasa_derita_schema()` — hash + structure, no gate

## Shortest kernel form

```text
No mutation without:
1. authority
2. scoped consent
3. evidence receipt
4. causal cascade
5. reversibility estimate
6. weakest-stakeholder check
7. judge verdict
8. receipt path
```

Any missing → `888_HOLD`.

## Six semantic gates (implementation roadmap)

| Gate | Target | Phase 1 |
|------|--------|---------|
| G1 F2 claim envelope | Output epistemic labels | schema + failing evaluator tests |
| G2 Scar fail-closed | Mutation + store down → HOLD | schema tests; scar still fail-open in runtime |
| G3 Federated evidence | No silent average; WELL REFLECT_ONLY | Python schema landed |
| G4 Real F4 entropy | ΔS before/after | schema landed; laws.py length-proxy untouched |
| G5 F5/F6 human impact | Stakeholders not word lists | schema landed; laws.py untouched |
| G6 Registry truth | Live tools/list = declared surface | failing drift tests |

## Phase 1 rule

No production behaviour change. Tests define the contract before code satisfies it.

## Completion test

Not green unit tests alone. Kernel loads schema, refuses against it, deploys, VAULT-attests `INSTALLED_ENFORCED`.

DITEMPA BUKAN DIBERI
