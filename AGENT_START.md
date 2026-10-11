# AGENT_START.md
## Federation canonical agent-start manifest (per directive §12)
## Single canonical entry point per repository
## Replaces hidden context injection with explicit manifest

> A new coding agent enters this repository with no conversation history and
> receives ONLY this manifest + the standard repo files. The agent must be
> able to determine: role, authority, current state, canonical SOT, safe
> autonomous actions, prohibited consequences, current gaps, and next safe action.

## SECTION 1 — IDENTITY (1 line)

This repository is part of the arifOS Federation.
See `CURRENT_VERIFIED_STATE.md` for the federation-wide role.

## SECTION 2 — CURRENT HUMAN AUTHORITY

ARIF (Muhammad Arif bin Fazil, F13 SOVEREIGN).
Mission envelope: per ARIF's instruction; mission IDs from carry-forward.

## SECTION 3 — CURRENT VERIFIED STATE (snapshot timestamp: see CURRENT_VERIFIED_STATE.md)

Two properties hold end-to-end. Four do not. UNMEASURED ≠ PASS.
Floor state: 2 pass · 4 fail (F2/F11/F12/F13) · 10 unmeasured.

## SECTION 4 — CANONICAL PATHS

| Purpose | Path |
|---------|------|
| Current state | `CURRENT_VERIFIED_STATE.md` |
| Claim registry | `CLAIM_REGISTRY.yaml` |
| Floor doctrine | `/root/AAA/instructions/arif-doctrine-v1.md` |
| Agent instructions | `AGENTS.md` |

## SECTION 5 — PROHIBITED ACTIONS

(Per directive §2 — non-negotiable safety boundary.)

- Production deployment (requires F13 stamp as separate activation step)
- Service restart affecting production
- DNS or TLS mutation
- Destructive deletion without proven rollback
- Spending money
- Creating paid accounts
- Accepting legal terms
- Sending external communications
- CVE publication
- Public vulnerability disclosure
- Company registration
- Teammate designation
- Privilege escalation
- Secret rotation
- Authentication weakening
- Production database mutation
- Irreversible ledger rewriting
- Publication of private data
- Action outside the declared repository or mission scope
- Genuine ambiguity about which human consequence is intended

## SECTION 6 — SAFE AUTONOMOUS ACTIONS

(Within mission envelope — no interruption needed.)

- inspect, search, read instruction files
- edit current documentation
- update canonical claim registries
- repair generators
- regenerate mirrors
- shorten and reconcile agent instructions
- exclude archives from indexing
- create tests, run tests
- create local previews
- create backups, hashes, reversible commits
- repair failures, continue across all safe phases

## SECTION 7 — REAL STOP CONDITIONS (HOLD only when ALL true)

1. A specific next action is identified.
2. The action is outside existing authority.
3. The consequence cannot be safely reversed or isolated.
4. No safe independent work remains.
5. The exact human decision is stated.
6. The agent has exhausted bounded local resolution.
7. Additional investigation cannot resolve the ambiguity.

HOLD scope (smallest first): FILE-LEVEL > TASK-LEVEL > MISSION-LEVEL.

## SECTION 8 — CURRENT GAPS

(Per CURRENT_VERIFIED_STATE.md, Section 3.)

1. Verified actor (signing path exists, observed unsigned)
2. Invocation receipt fidelity (HOLD persisted as ok:true)
3. Sink agreement (one event omitted from organ counters)
4. Independent reconstruction (no external verifier bound)

## SECTION 9 — HISTORICAL REFERENCES (queryable, not injected)

History must remain queryable, not continuously injected.
- git log (every commit preserved)
- AGENTS.md.bak-membrane-*.md (membrane repair snapshots)
- archive/, _archive/, _quarantine-*.Z/ (DO NOT auto-index; query on demand)
- arifFlow-rg2-verify/, work/, etc. (worktrees)

## SECTION 10 — NEXT SAFE ACTION

The next safe action is to read `CURRENT_VERIFIED_STATE.md` and `CLAIM_REGISTRY.yaml`,
then proceed within the authorized mission envelope. If no mission is active,
the agent should respond with SEAL_LOCAL_READY (nothing to do) and await ARIF.
