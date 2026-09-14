# FEDERATION.md — arifOS Federation Architecture

> **CANONICAL SOURCE** — This is the single source of truth for federation architecture, constitutional planes, organ taxonomy, and boundary classification. All other FEDERATION*.md files across repos are projections or historical records. When in doubt, this file wins.
>
> **Last updated:** 2026-09-14 (federation alignment review)
>
> **DITEMPA BUKAN DIBERI** — Forged, Not Given.

---

## Constitutional Planes

The federation separates concern into four non-overlapping planes. Each plane owns a distinct scarcity. No plane may claim another plane's authority.

| Plane | Organ | Scarcity | Question | Does NOT |
|-------|-------|----------|----------|----------|
| **Authority** | arifOS | Authority | What is permissible? | Execute, route, observe vitality |
| **Attention** | AAA | Attention | What matters? | Judge, execute, mutate |
| **Execution** | A-FORGE | Execution | How do we change reality? | Judge, witness, self-authorize |
| **Witness** | arifFlow + VAULT999 | Reality | What actually happened? | Judge, execute, approve actions |

```
              ARIF (F13 Sovereign)
                     │
                     ▼
         ┌───────────────────────┐
         │   Authority Plane     │
         │   arifOS (:8088)      │
         │   Constitutional      │
         │   judgment, F1–F13    │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   Attention Plane     │
         │   AAA (:3001)         │
         │   Reality compression │
         │   + routing           │
         └───────────┬───────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
Execution        Witness        Domain Organs
Plane            Plane          (capability
A-FORGE          arifFlow        providers)
(:7071/:7072)    (:7073)
                     │
                     ▼
                 VAULT999
              (append-only ledger)
```

### Invariant

> **The judge never executes. The executor never certifies. The witness never decides. The interface never inherits authority.**

---

## Core Organs (10)

| # | Organ | Port | Plane / Role | Authority Ceiling |
|---|-------|------|--------------|-------------------|
| 1 | arifOS | :8088 | Authority Plane — constitutional judgment | JUDGE_ONLY |
| 2 | AAA | :3001 | Attention Plane — reality compression + routing | DISPLAY_ONLY |
| 3 | A-FORGE | :7071/:7072 | Execution Plane — governed mutation | EXECUTE_AFTER_SEAL |
| 4 | arifFlow | :7073 | Witness Plane — metabolism, FQ, receipt ingestion | METABOLIZE_ONLY |
| 5 | GEOX | :8081 | Earth Intelligence — geological evidence | COMPUTE_ONLY |
| 6 | WEALTH | :18082 | Capital Intelligence — financial evidence | COMPUTE_ONLY |
| 7 | WELL | :18083 | Readiness Intelligence — vitality observation | REFLECT_ONLY |
| 8 | FED | :7074 | Model Federation — multi-provider inference routing | ROUTING_ONLY |
| 9 | FRAME | :18085 | Independent Observer — drift detection, evidence | OBSERVE_ONLY |
| 10 | i-ARIF | :18095 | Synthesis — Seal B engine | COMPUTE_ONLY |

### Domain Organs

| Organ | Scarcity | Question |
|-------|----------|----------|
| GEOX | Earth evidence | What does reality say? |
| WEALTH | Capital evidence | What is economically sound? |
| WELL | Readiness evidence | Is the substrate healthy? |

---

## Boundary Interfaces (Tier 3)

Boundary interfaces are **not organs**. They are replaceable entry surfaces that route signals across the world/federation boundary. They never adjudicate.

| Interface | Location | Function | Telegram Bot |
|-----------|----------|----------|--------------|
| HERMES | KVM8 | Telegram poller, inbound signal routing | `@ASI_arifos_bot` |
| OpenClaw | KVM4 | Telegram poller, edge gateway | `@AGI_ASI_bot` |
| arif-fazil.com | KVM8 | Public web surface | — |

### Invariant

> **Organs own durable constitutional capabilities. Interfaces provide replaceable entry surfaces.**

HERMES and OpenClaw are live, deployable infrastructure. They are Tier 3 because their capability (boundary routing) survives replacement — another Telegram bot, web channel, or voice interface could serve the same function. The constitutional planes cannot be replaced.

---

## Machine Topology

### KVM8 (100.64.0.2 = `forge`) — Seat/Court

All core organs + HERMES Telegram poller.

### KVM4 (100.64.0.5 = `kvm4-forge`) — Workshop/Edge

OpenClaw (`@AGI_ASI_bot`, :18789) + FED LiteLLM (:4000, tailnet-bound).

### KVM2 (100.64.0.4 = `azwaos`) — Azwa's Civilization

Separate sovereign node. Tailscale active. Not inspected or modified without separate authority.

---

## Constitutional Chain

```
Agent proposes action
       │
       ▼
arifOS judges (F1–F13 floors)
       │
  ┌────┴────┐
  │         │
 SEAL     HOLD / SABAR / VOID
  │         │
  ▼         ▼
A-FORGE   Human
executes  decides
  │
  ▼
Receipt in VAULT999
(append-only, hash-chained)
```

### Four Verdicts

| Verdict | Meaning | What happens |
|---------|---------|-------------|
| **SEAL** | Authorized | Proceed to execution |
| **HOLD** | Needs human review | Pause; await human decision |
| **SABAR** | Not yet decidable | Wait; more evidence needed |
| **VOID** | Blocked by floor | Stop; constraint must be resolved |

---

## Operating Chain

```
arif_init → arif_observe → arif_think → arif_route → arif_memory
          → arif_judge → arif_forge → arif_seal
```

Only `arif_seal` writes to VAULT999. Only A-FORGE mutates production state.

---

## Capability Hierarchy

```
Capability → Organ → Tool → Skill
```

Capabilities are the most durable. Organs implement capabilities. Tools serve organs. Skills compose tools. The hierarchy flows downward in durability — a capability survives even if its organ is reorganized.

---

## Related Documents

| Document | Location | Purpose |
|----------|----------|---------|
| arifOS README | [arifOS/README.md](../README.md) | Authority Plane specification |
| AAA README | [AAA/README.md](../../AAA/README.md) | Attention Plane specification |
| FEDERATION_CONTRACT.md | [arifOS/FEDERATION_CONTRACT.md](../FEDERATION_CONTRACT.md) | Agent contracts |
| F1–F13 Constitution | [arifOS/CONSTITUTION.md](../CONSTITUTION.md) | Constitutional floors |
| Machine Map | [AAA/docs/MACHINE_MAP.md](../../AAA/docs/MACHINE_MAP.md) | 3-node mesh SOT |
| Canonical Glossary | [AAA/canon/CANONICAL_GLOSSARY.md](../../AAA/canon/CANONICAL_GLOSSARY.md) | Term definitions |

---

## Source-of-Truth Rule

This file (`arifOS/docs/FEDERATION.md`) is the **canonical** federation architecture document.

Other `FEDERATION*.md` files across the federation are:
- **Projections** — scoped local views that may be out of date
- **Historical** — preserved for audit, explicitly labelled
- **Specialized** — cover specific subsystems (memory, transport, envelope)

When a projection contradicts this file, **this file wins**.

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.

Built by Muhammad Arif bin Fazil (F13 Sovereign).
