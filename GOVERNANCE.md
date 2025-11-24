```markdown
# arifOS Governance (summary)

This document contains the operational governance statements for arifOS: the constitutional floors, the amendment procedure (Phoenix-72), and how governance-related rules are treated in development and deployment.

This file is NOT a software license. Legal licensing remains in LICENSE.txt (MIT). Governance rules describe runtime invariants and project governance, and are enforced by code, tests, and operational practice.

## Constitutional Floors (operational definitions)

The system enforces the following runtime invariants where applicable:
- Truth ≥ 0.99 — outputs must be evidence-backed where required.
- ΔS ≥ 0 — outputs must not increase confusion/entropy.
- Peace² ≥ 1.0 — outputs must avoid escalation or harm.
- κᵣ ≥ 0.95 — weakest-listener empathy constraints.
- Ω₀ ∈ [0.03, 0.05] — humility band for expressed uncertainty.
- Amanah = LOCK — no deceptive or manipulative behaviors permitted.
- RASA = TRUE — receive, appreciate, summarize, ask flow enabled.
- Tri-Witness ≥ 0.95 — high-stakes seals require human, model, reality consensus.

These invariants are enforced by runtime checks in code, automated tests, CI gates, and monitoring. If you believe code allows bypass, open a high-priority issue.

## Amendment process: Phoenix-72

To change any constitutional floor, the pipeline, or APEX behavior:
1. Create an `[AMENDMENT]` issue with proposed spec and migration plan.
2. Tag `constitutional-change` and notify maintainers.
3. Tri-Witness evaluation (Human review, AI simulation tests, and reality-adapter verification).
4. If Tri-Witness consensus is achieved, maintainers prepare a migration plan and PRs.
5. Vault-999 seals the amendment and records migration metadata.

Amendments are deliberate, documented, and reproducible.

## Enforcement & code practice

- APEX PRIME, Amanah, and ledger invariants are enforced by code-level asserts and test suites.
- Critical modules are covered by code owners and require explicit approvals.
- Production deployments must use KMS/HSM-backed signing keys and enable ledger verification monitoring.

## Dispute resolution

If contributors disagree about a governance change, the Phoenix-72 issue must document the dispute, options, and the Tri-Witness mediation outcome.

## Contact

For governance questions, open an issue with prefix `[GOVERNANCE]` or email arifbfazil@gmail.com.

**Last updated:** 2025-11-24
```