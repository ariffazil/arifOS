# Threat Model — arifOS Federation (Summary)

> **Binding document:** `AAA/docs/ADVERSARIAL_SPEC_EXTERNAL.md`
> **Findings:** `AAA/docs/PRE_AUDIT_RESULTS.md` (4 unfixed P0/P1 crypto gaps)
> This file is a summary pointer, not the specification. The spec governs.

## Scope
What an adversary gains by breaking arifOS: governance bypass (F1-F13 floors),
receipt forgery (VAULT999), observability poisoning, and supply-chain compromise
of the `arifosmcp` package.

## Adversary Classes
| Class | Capability | Primary Exposure |
|---|---|---|
| External network | Unauthenticated HTTP to federation surfaces | Kernel :8088, arifFlow :7073, FRAME :18085 |
| Co-tenant / local | Localhost access to unauth services | Postgres, Redis, NATS (`LOCALHOST_IS_PASSWORD` doctrine) |
| Malicious consumer | Crafted MCP requests to trigger floor breaches | Tool handlers, verdict paths |
| Supply chain | PyPI package tampering, unsigned releases | 07-publish-pypi.yml — see `release-integrity.md` |
| Insider / compromised agent | Mutates production state, forges receipts | A-FORGE write path, seal discipline |

## Current Open Weaknesses (2026-09-16)
- 4 unfixed P0/P1 crypto gaps from pre-audit — raw findings in PRE_AUDIT_RESULTS.md
- No independent external audit executed yet (spec is `ready_for_execution`)
- Observability coverage 21.9%; trace_id correlation 0% (P0-B) — see `observability-contract.md`

## Disposition
Claims tied to this model are tracked in `claims.yaml` (CLAIM-005: constitutional
governance = verified **with** the two limitations above recorded). A claim is
not closed while its limitation is open.
