<!-- SOT-MANIFEST
federation_release: v2026.08.25
last_verified: 2026-08-25T04:30:00Z
live_commit: 6de71a0d7 (docs(readme): ZEN first-fold)
source_commit: 2258694 (aligned: source = built = deployed)
tools_exposed_via_mcp: 8 (canonical public verbs — live-witnessed 2026-08-25 via :8088/health)
total_declared_tools: 48 (8 public + 13 internal + 27 diagnostic)
registry_size: 62 (includes aliases)
floors_active: 13 (F1–L13, all passing)
federation_schema: 2.0.0
organs: 7 (arifOS:8088, A-FORGE:7071/7072, AAA:3001, GEOX:8081, WEALTH:18082, WELL:18083, arifFlow:7073)
infra: FED:7074 ADVISORY, FLAME:18901 ADVISORY, FRAME:frame-organ OBSERVE
truth_rule: live :8088/health + tools/list beat any static count in prose
vault999: healthy (outcomes.jsonl 67K+ records, append-only, 0 broken lines)
readme_note: ZEN first-fold — full reference at docs/README-FULL.md; federation card at docs/FEDERATION_CARD.md
-->

# arifOS — Law

## Judge before acting. Never act.

The constitutional kernel of the arifOS Federation.

arifOS is law, not an agent.
It judges.
It seals.
It never executes.

**DITEMPA BUKAN DIBERI** — Forged, Not Given.

---

## Every action, three questions

Every consequential action must answer:

1. Who **performs** it?
2. Who **approved** it?
3. Who **witnessed** it?

arifOS answers the second — and only the second.

Execution belongs to A-FORGE.
Routing belongs to AAA.
Authority belongs to the sovereign.

> **The agent that acts is not allowed to certify its own action.**

## Verdicts

Four. No fifth.

- **SEAL** — authorized under stated conditions
- **HOLD** — insufficient evidence, or human approval required
- **SABAR** — proceed cautiously, partial authorization
- **VOID** — blocked by a constitutional floor

## Verbs (MCP)

Eight canonical verbs, live-witnessed 2026-08-25 via `:8088/health`:

`arif_init` · `arif_observe` · `arif_think` · `arif_route` · `arif_memory` · `arif_judge` · `arif_forge` · `arif_seal`

Door: `/mcp`. Public console is not exposed — the kernel serves `/webmcp` on :8088 locally only.

## 30-second proof

```text
Request: "delete production database"
  No session ACT, no evidence chain → HOLD
  Evidence + floors pass → SEAL with conditions
    → execution by A-FORGE → receipt → VAULT999
```

VAULT999 (live 2026-08-25): healthy, append-only, outcomes.jsonl 67K+ records, 0 broken lines.

## Architecture in one sentence

**The judge never executes; the executor never certifies.**

```mermaid
flowchart LR
    Intent[Intent] --> Judge[arifOS]
    Judge -->|SEAL| Forge[A-FORGE]
    Forge --> Receipt[Receipt]
    Receipt --> Vault[VAULT999]
    Judge -->|HOLD| Human[Human Review]
```

## Federation card

ARIF = Sovereign · arifOS = Law · AAA = Institution · A-FORGE = Hands

**ARIF vetoes. arifOS judges. AAA routes. A-FORGE executes.**

Full card: [docs/FEDERATION_CARD.md](./docs/FEDERATION_CARD.md) ·
Full reference README: [docs/README-FULL.md](./docs/README-FULL.md) ·
Constitution: [GENESIS/000_KERNEL_CANON.md](./GENESIS/000_KERNEL_CANON.md) ·
ZEN doctrine: [docs/ZEN.md](./docs/ZEN.md)
