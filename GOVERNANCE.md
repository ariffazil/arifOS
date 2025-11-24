# arifOS Governance (summary)

This document contains the operational governance statements for arifOS: the constitutional floors, the amendment procedure (Phoenix-72), and how governance-related rules are treated in development and deployment.

This file is NOT a software license. Legal licensing remains in LICENSE.txt (Apache-2.0). Governance rules describe runtime invariants and project governance, and are enforced by code, tests, and operational practice.

## Constitutional Floors (operational definitions)

 arifOS enforces the following runtime invariants where applicable:

- Truth ≥ 0.99 — outputs must be evidence-backed where required.
- ΔS ≥ 0 — outputs must not increase user confusion or entropy.
- Peace² ≥ 1.0 — outputs must avoid escalation, incitement, or destabilization.
- κᵣ ≥ 0.95 — weakest-listener empathy constraint; protect vulnerable recipients.
- Ω₀ ∈ [0.03, 0.05] — humility band: expressed uncertainty percentage.
- Amanah = LOCK — integrity constraint; no deception, manipulation, or hidden agendas.
- RASA = TRUE — the Receive–Appreciate–Summarize–Ask interaction pattern is enabled.
- Tri‑Witness ≥ 0.95 — high‑stakes seals require consensus across Human · AI · Reality adapters.

These invariants are implemented as runtime checks, unit & integration tests, CI gates, and operational monitoring. If you discover a code path that permits bypass of these invariants, open a high‑priority issue.

## Amendment process: Phoenix-72

To modify any constitutional floor, the 000→999 pipeline structure, or APEX behavior:

1. Create an issue titled: `[AMENDMENT] Short description`.
2. Tag it `constitutional-change`.
3. Include:
   - Root cause for the change.
   - Precise proposed specification.
   - Impact analysis across all 8 floors.
   - Migration path for existing deployments.
4. Tri‑Witness evaluation: run human review, automated AI simulation tests, and reality/evidence adapters.
5. If Tri‑Witness consensus is achieved, maintainers prepare PR(s) with migration steps.
6. Vault‑999 records/seals the amendment and the migration metadata.

Amendments are deliberate, transparent, and reproducible.

## Enforcement & code practice

- APEX PRIME, Amanah, and Cooling Ledger invariants are enforced by code-level assertions and covered by tests.
- Critical modules (APEX, ledger, guard) are protected by code-owners and require explicit approvals and reviews.
- Production deployments must use KMS/HSM-backed signing keys and enable ledger verification monitoring.

## Dispute resolution

If contributors disagree about governance changes, the Phoenix‑72 issue must document the dispute, options considered, and the chosen Tri‑Witness mediation outcome.

## Contact

For governance questions, open an issue with prefix `[GOVERNANCE]` or email: arifbfazil@gmail.com.

**Last updated:** 2025-11-24
