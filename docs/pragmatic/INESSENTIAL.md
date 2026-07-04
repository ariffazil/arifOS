# What Is NOT Critical — Deletion Safety Guide

> **Blindspot #6 response.** "When everything is critical, nothing is."
> Updated: 2026-06-30 by FORGE (000Ω).

## The Three Actual Criticals

Only **THREE** components cannot be deleted without losing arifOS's value:

### 1. `session.py` — Actor Binding
**Why critical:** Without it, you don't know who did what. F11 audit breaks.

### 2. `vault.py` — Immutable Audit Log
**Why critical:** Without it, the guarantee "everything is inspectable" is a lie.

### 3. `gate.py` — Irreversibility + Hallucination Detection
**Why critical:** Without it, agents can destroy things with no gate. F1 + F9 break.

**These three + `server.py` (MCP entry) = the minimum viable arifOS.**
**Total: ~2,500 LOC.**

## Everything Else Is Optional

If you delete any of these, arifOS still works — just with less capability:

| Component | What Breaks If Deleted | Acceptable? |
|---|---|---|
| `arif_think` | No reasoning tool provided | Yes — user can use their own |
| `arif_route` | No routing | Yes — users call tools directly |
| `arif_observe` | No data fetching | Yes — users fetch externally |
| Trinity witness math | No cross-verification score | Yes — still have basic F2 |
| Multi-organ bridge | No cross-organ calls | Yes — each organ runs alone |
| `organ_intent_map.yaml` | No intent routing | Yes — use direct tool calls |
| A2A bridge | No agent-to-agent | Yes — single-agent deployments work |
| 48-tool surface | Tools gone | Yes — keep only canonical 7 |
| Philosophy docs | No conceptual docs | Yes — code speaks for itself |
| Constitution canon | Philosophy lost | Yes — code enforces rules, not docs |

## The Smoke Test for Criticality

Before declaring any component "critical", verify:

1. **Delete it from the codebase.** `git rm <path>`
2. **Run all tests.** Do the core 3 invariants still hold?
3. **Run the smoke test:**
   - Can I start a session? (`arif_init`)
   - Can I do a reversible action? (`arif_act` with `ack_irreversible=false`)
   - Can I log it? (`arif_seal`)
   - Is the destructive action blocked? (`arif_act` on destructive without ack → should HOLD)
4. **If all 4 pass: NOT critical.** Keep it optional.

## "Philosophical Grounding" Is Optional

This is controversial but true: arifOS works as a pragmatic MCP server even if you strip out:
- Trinity math
- F3, F5, F6 formal proofs
- All philosophy docs
- All Islamic legal references (HARAM, Mubah, Fard)
- All AGI/ASI/apex language

The **pragmatic arifOS** = session binding + audit + irreversibility gate.
The **philosophical arifOS** = the pragmatic one + conceptual framing.

Both are valid. Choose based on audience.

## The 30% Critical / 70% Optional Ratio

Target ratio: **30% of the codebase does 90% of the value.**

Currently: we're roughly at 10% critical / 90% optional.
Goal: make this ratio explicit and documented (see CODE_DEBT.md).

## What Happens When You Delete Optional Code

| Scenario | Effect |
|---|---|
| Delete `arif_think` | Users use their own reasoning. Fine. |
| Delete `trinity.py` | W3 formula gone. F3 becomes a plain-language guideline. |
| Delete A2A bridge | Single-agent deployments unaffected. Multi-agent needs rewrite. |
| Delete 40 extra tools | Keep 7 canonical. Users don't notice. |
| Delete all philosophy docs | QUICKSTART.md is enough for developers. |

## When to Re-Add Optional Code

Re-add only when:
- A real user reports a real problem only this solves (not a theoretical one)
- Tests fail without it
- Latency/observability measurably improves

**Never re-add because:**
- "It's philosophically important"
- "The architecture feels incomplete without it"
- "Other agents added it"

---

**DITEMPA BUKAN DIBERI** — less is more honest.
